from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from app.groupes.models import Groupe, Membership
from app.auth.models import User
from app.schemas_shared import ok


async def creer_groupe(nom: str, max_membres: int, user: User, db: AsyncSession) -> dict:
    groupe = Groupe(nom=nom, max_membres=max_membres, createur_id=user.id)
    db.add(groupe)
    await db.flush()

    membership = Membership(
        user_id=user.id,
        groupe_id=groupe.id,
        statut="approved",
        role="admin",
        nom_affiche=f"{user.prenom} {user.nom}",
        date_approbation=datetime.utcnow(),
    )
    db.add(membership)
    await db.flush()
    await db.refresh(groupe)
    return {"groupe": groupe, "membership": membership}


async def rejoindre_groupe(code: str, nom_affiche: str, user: User, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Groupe).where(and_(Groupe.code_unique == code.upper(), Groupe.is_active == True))
    )
    groupe = result.scalar_one_or_none()
    if not groupe:
        raise HTTPException(status_code=404, detail="Code invalide")

    result = await db.execute(
        select(Membership).where(and_(Membership.user_id == user.id, Membership.groupe_id == groupe.id))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Vous etes deja dans ce groupe")

    membership = Membership(
        user_id=user.id, groupe_id=groupe.id,
        statut="pending", nom_affiche=nom_affiche,
    )
    db.add(membership)
    await db.flush()
    await db.refresh(membership)
    return {"groupe": groupe, "membership": membership}


async def mes_groupes(user: User, db: AsyncSession) -> list:
    result = await db.execute(
        select(Membership).where(and_(Membership.user_id == user.id, Membership.statut == "approved"))
    )
    memberships = result.scalars().all()
    groupes = []
    for m in memberships:
        r = await db.execute(select(Groupe).where(Groupe.id == m.groupe_id))
        g = r.scalar_one_or_none()
        if g:
            groupes.append(g)
    return groupes


async def membres_groupe(groupe_id: str, user: User, db: AsyncSession) -> list:
    # Verifier que l'utilisateur est membre
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
        select(Membership).where(and_(Membership.groupe_id == groupe_id, Membership.statut == "approved"))
    )
    memberships = result.scalars().all()

    membres = []
    for m in memberships:
        r = await db.execute(select(User).where(User.id == m.user_id))
        u = r.scalar_one_or_none()
        if u:
            membres.append({
                "user_id": u.id,
                "nom": u.nom,
                "prenom": u.prenom,
                "nom_affiche": m.nom_affiche,
                "photo_profil": u.photo_profil,
                "statut_partage": u.statut_partage,
                "role": m.role,
                "membership_id": m.id,
            })
    return membres


async def gerer_membre(membership_id: str, action: str, user: User, db: AsyncSession) -> Membership:
    if action not in ["approve", "reject", "ban"]:
        raise HTTPException(status_code=400, detail="Action invalide")

    result = await db.execute(select(Membership).where(Membership.id == membership_id))
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membre introuvable")

    # Verifier admin
    result = await db.execute(
        select(Membership).where(and_(
            Membership.user_id == user.id,
            Membership.groupe_id == membership.groupe_id,
            Membership.role == "admin",
            Membership.statut == "approved"
        ))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Admins uniquement")

    mapping = {"approve": "approved", "reject": "rejected", "ban": "banned"}
    membership.statut = mapping[action]
    if action == "approve":
        membership.date_approbation = datetime.utcnow()
    await db.flush()
    await db.refresh(membership)
    return membership