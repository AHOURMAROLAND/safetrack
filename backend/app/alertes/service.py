from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, UploadFile
from app.alertes.models import AlerteDanger, AudioUrgence
from app.groupes.models import Membership
from app.auth.models import User
from app.ws_manager import manager
import os


async def declencher_sos(data, user: User, db: AsyncSession) -> AlerteDanger:
    # Verifier membre
    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.groupe_id == data.groupe_id,
            Membership.statut == "approved"
        ))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Acces refuse")

    alerte = AlerteDanger(
        declencheur_id=user.id,
        groupe_id=data.groupe_id,
        latitude=data.latitude,
        longitude=data.longitude,
        type_declenchement=data.type_declenchement or "manuel",
        message_court=data.message_court,
        is_active=True,
    )
    db.add(alerte)
    await db.flush()
    await db.refresh(alerte)

    # Diffuser SOS via WebSocket
    await manager.diffuser(data.groupe_id, {
        "t": "sos",
        "alerte_id": alerte.id,
        "user_id": user.id,
        "nom": f"{user.prenom} {user.nom}",
        "la": data.latitude,
        "lo": data.longitude,
        "type": data.type_declenchement,
        "message": data.message_court,
        "ts": datetime.utcnow().isoformat(),
    })

    # SMS fallback via notifications
    from app.notifications.service import sms_sos
    result = await db.execute(
        select(Membership).where(and_(
            Membership.groupe_id == data.groupe_id,
            Membership.statut == "approved"
        ))
    )
    membres = result.scalars().all()
    for m in membres:
        if m.user_id == user.id:
            continue
        r = await db.execute(select(User).where(User.id == m.user_id))
        u = r.scalar_one_or_none()
        if u and u.phone:
            await sms_sos(u.phone, f"{user.prenom} {user.nom}", data.latitude, data.longitude)

    return alerte


async def annuler_sos(alerte_id: str, user: User, db: AsyncSession) -> AlerteDanger:
    result = await db.execute(
        select(AlerteDanger).where(and_(
            AlerteDanger.id == alerte_id,
            AlerteDanger.declencheur_id == user.id,
            AlerteDanger.is_active == True,
        ))
    )
    alerte = result.scalar_one_or_none()
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte introuvable")

    delta = (datetime.utcnow() - alerte.timestamp).total_seconds()
    if delta > 60:
        raise HTTPException(status_code=400, detail="Delai d'annulation depasse (60 sec max)")

    alerte.is_active = False
    alerte.est_fausse_alerte = True
    await db.flush()

    await manager.diffuser(alerte.groupe_id, {
        "t": "sos_annule",
        "alerte_id": alerte.id,
        "user_id": user.id,
        "nom": f"{user.prenom} {user.nom}",
    })
    return alerte


async def alertes_actives(user: User, db: AsyncSession) -> list:
    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.statut == "approved"
        ))
    )
    groupe_ids = [m.groupe_id for m in result.scalars().all()]
    alertes = []
    for gid in groupe_ids:
        r = await db.execute(
            select(AlerteDanger).where(and_(
                AlerteDanger.groupe_id == gid,
                AlerteDanger.is_active == True,
            ))
        )
        alertes.extend(r.scalars().all())
    return alertes


async def upload_audio(alerte_id: str, numero_segment: int, user_id: str, fichier: UploadFile, db: AsyncSession) -> AudioUrgence:
    result = await db.execute(
        select(AlerteDanger).where(and_(
            AlerteDanger.id == alerte_id,
            AlerteDanger.declencheur_id == user_id,
        ))
    )
    alerte = result.scalar_one_or_none()
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte introuvable")

    contenu = await fichier.read()
    dossier = f"audio_urgences/{alerte_id}"
    os.makedirs(dossier, exist_ok=True)
    chemin = f"{dossier}/segment_{numero_segment}.aac"
    with open(chemin, "wb") as f:
        f.write(contenu)

    audio = AudioUrgence(
        alerte_id=alerte_id,
        user_id=user_id,
        numero_segment=numero_segment,
        taille_octets=len(contenu),
        url_fichier=chemin,
        is_uploade=True,
    )
    db.add(audio)
    await db.flush()
    await db.refresh(audio)

    await manager.diffuser(alerte.groupe_id, {
        "t": "audio_disponible",
        "alerte_id": alerte_id,
        "segment": numero_segment,
        "audio_id": audio.id,
    })
    return audio


async def segments_audio(alerte_id: str, db: AsyncSession) -> list:
    result = await db.execute(
        select(AudioUrgence).where(AudioUrgence.alerte_id == alerte_id)
    )
    return result.scalars().all()