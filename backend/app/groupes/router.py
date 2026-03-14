from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.groupes.schemas import CreerGroupeSchema, RejoindreGroupeSchema, GroupeReponse, MembershipReponse, GererMembreSchema
from app.groupes import service

router = APIRouter()


@router.post("/creer")
async def creer(data: CreerGroupeSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await service.creer_groupe(data.nom, data.max_membres, user, db)
    return {
        "message": "Groupe cree",
        "groupe": GroupeReponse.model_validate(result["groupe"]),
        "code": result["groupe"].code_unique,
    }


@router.post("/rejoindre")
async def rejoindre(data: RejoindreGroupeSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await service.rejoindre_groupe(data.code_unique, data.nom_affiche, user, db)
    return {
        "message": "Demande envoyee",
        "membership": MembershipReponse.model_validate(result["membership"]),
    }


@router.get("/mes-groupes")
async def get_mes_groupes(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    groupes = await service.mes_groupes(user, db)
    return [GroupeReponse.model_validate(g) for g in groupes]


@router.get("/{groupe_id}/membres")
async def get_membres(groupe_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.membres_groupe(groupe_id, user, db)


@router.post("/membres/{membership_id}/gerer")
async def gerer(membership_id: str, data: GererMembreSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    m = await service.gerer_membre(membership_id, data.action, user, db)
    return {"message": f"Membre {data.action}", "membership": MembershipReponse.model_validate(m)}