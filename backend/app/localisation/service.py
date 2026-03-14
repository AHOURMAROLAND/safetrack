from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from app.localisation.models import LocationUpdate, Destination
from app.groupes.models import Membership
from app.auth.models import User
from app.ws_manager import manager


async def sauvegarder_position(user_id: str, groupe_id: str, data: dict, db: AsyncSession):
    loc = LocationUpdate(
        user_id=user_id,
        groupe_id=groupe_id,
        latitude=data.get("la", 0),
        longitude=data.get("lo", 0),
        vitesse=data.get("v", 0),
        is_moving=bool(data.get("m", 0)),
        battery_level=data.get("b", 100),
    )
    db.add(loc)
    await db.commit()


async def historique_48h(user_id: str, groupe_id: str, db: AsyncSession) -> list:
    limite = datetime.utcnow() - timedelta(hours=48)
    result = await db.execute(
        select(LocationUpdate).where(and_(
            LocationUpdate.user_id == user_id,
            LocationUpdate.groupe_id == groupe_id,
            LocationUpdate.timestamp >= limite,
        )).order_by(LocationUpdate.timestamp.asc())
    )
    return result.scalars().all()


async def dernieres_positions(groupe_id: str, user: User, db: AsyncSession) -> list:
    # Verifier membre
    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.groupe_id == groupe_id,
            Membership.statut == "approved"
        ))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Acces refuse")

    result = await db.execute(
        select(Membership).where(and_(
            Membership.groupe_id == groupe_id,
            Membership.statut == "approved"
        ))
    )
    memberships = result.scalars().all()

    positions = []
    for m in memberships:
        r_user = await db.execute(select(User).where(User.id == m.user_id))
        u = r_user.scalar_one_or_none()
        r_loc = await db.execute(
            select(LocationUpdate).where(and_(
                LocationUpdate.user_id == m.user_id,
                LocationUpdate.groupe_id == groupe_id,
            )).order_by(LocationUpdate.timestamp.desc()).limit(1)
        )
        loc = r_loc.scalar_one_or_none()
        if u:
            positions.append({
                "user_id": u.id,
                "nom": f"{u.prenom} {u.nom}",
                "statut_partage": u.statut_partage,
                "latitude": loc.latitude if loc else None,
                "longitude": loc.longitude if loc else None,
                "vitesse": loc.vitesse if loc else 0,
                "is_moving": loc.is_moving if loc else False,
                "battery_level": loc.battery_level if loc else None,
                "timestamp": loc.timestamp.isoformat() if loc else None,
            })
    return positions


async def demarrer_partage(data, user: User, db: AsyncSession) -> Destination:
    # Annuler destinations actives
    result = await db.execute(
        select(Destination).where(and_(
            Destination.user_id == user.id,
            Destination.statut == "en_route"
        ))
    )
    for d in result.scalars().all():
        d.statut = "annule"

    dest = Destination(
        user_id=user.id,
        nom_lieu=data.nom_lieu,
        latitude=data.latitude,
        longitude=data.longitude,
        heure_depart=datetime.utcnow(),
        heure_arrivee_prevue=data.heure_arrivee_prevue,
        delai_grace_minutes=data.delai_grace_minutes,
        statut="en_route",
    )
    db.add(dest)
    user.statut_partage = "actif"
    await db.flush()
    await db.refresh(dest)

    # Notifier les groupes via WebSocket
    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.statut == "approved"
        ))
    )
    for m in result.scalars().all():
        await manager.diffuser(m.groupe_id, {
            "t": "destination",
            "user_id": user.id,
            "nom": f"{user.prenom} {user.nom}",
            "lieu": data.nom_lieu,
            "arrivee_prevue": data.heure_arrivee_prevue.isoformat(),
        })
    return dest


async def valider_arrivee(destination_id: str, user: User, db: AsyncSession) -> Destination:
    result = await db.execute(
        select(Destination).where(and_(
            Destination.id == destination_id,
            Destination.user_id == user.id,
        ))
    )
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination introuvable")

    dest.statut = "arrive"
    dest.valide_par_user = True
    dest.heure_arrivee_reelle = datetime.utcnow()
    user.statut_partage = "arrete"
    await db.flush()

    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.statut == "approved"
        ))
    )
    for m in result.scalars().all():
        await manager.diffuser(m.groupe_id, {
            "t": "arrive",
            "user_id": user.id,
            "nom": f"{user.prenom} {user.nom}",
            "lieu": dest.nom_lieu,
        })
    return dest


async def arreter_partage(user: User, db: AsyncSession):
    result = await db.execute(
        select(Destination).where(and_(
            Destination.user_id == user.id,
            Destination.statut == "en_route"
        ))
    )
    for d in result.scalars().all():
        d.statut = "annule"
    user.statut_partage = "arrete"
    await db.flush()

    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.statut == "approved"
        ))
    )
    for m in result.scalars().all():
        await manager.diffuser(m.groupe_id, {
            "t": "partage_arrete",
            "user_id": user.id,
            "nom": f"{user.prenom} {user.nom}",
        })
    return {"message": "Partage arrete"}