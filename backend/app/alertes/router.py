from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.alertes.schemas import DeclencherSOSSchema, AnnulerSOSSchema, AlerteReponse, AudioReponse
from app.alertes import service

router = APIRouter()


@router.post("/sos")
async def sos(data: DeclencherSOSSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alerte = await service.declencher_sos(data, user, db)
    return {"message": "SOS declenche", "alerte": AlerteReponse.model_validate(alerte)}


@router.post("/sos/annuler")
async def annuler(data: AnnulerSOSSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alerte = await service.annuler_sos(data.alerte_id, user, db)
    return {"message": "Alerte annulee", "alerte": AlerteReponse.model_validate(alerte)}


@router.get("/actives")
async def actives(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alertes = await service.alertes_actives(user, db)
    return [AlerteReponse.model_validate(a) for a in alertes]


@router.post("/audio/upload")
async def upload(
    alerte_id: str = Form(...),
    numero_segment: int = Form(...),
    fichier: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    audio = await service.upload_audio(alerte_id, numero_segment, user.id, fichier, db)
    return {"message": f"Segment {numero_segment} uploade", "audio": AudioReponse.model_validate(audio)}


@router.get("/audio/{alerte_id}")
async def segments(alerte_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    segs = await service.segments_audio(alerte_id, db)
    return [AudioReponse.model_validate(s) for s in segs]