from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.localisation.schemas import DemarrerPartageSchema, ValiderArriveeSchema, DestinationReponse
from app.localisation import service

router = APIRouter()


@router.get("/groupe/{groupe_id}/positions")
async def positions_groupe(groupe_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.dernieres_positions(groupe_id, user, db)


@router.get("/membre/{user_id}/historique/{groupe_id}")
async def historique(user_id: str, groupe_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    positions = await service.historique_48h(user_id, groupe_id, db)
    return [{"latitude": p.latitude, "longitude": p.longitude, "vitesse": p.vitesse, "timestamp": p.timestamp.isoformat()} for p in positions]


@router.post("/demarrer")
async def demarrer(data: DemarrerPartageSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    dest = await service.demarrer_partage(data, user, db)
    return {"message": "Partage demarre", "destination": DestinationReponse.model_validate(dest)}


@router.post("/valider-arrivee")
async def valider(data: ValiderArriveeSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    dest = await service.valider_arrivee(data.destination_id, user, db)
    return {"message": "Arrivee validee", "destination": DestinationReponse.model_validate(dest)}


@router.post("/arreter")
async def arreter(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.arreter_partage(user, db)