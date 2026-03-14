from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.auth.schemas import InscriptionSchema, ConnexionSchema, RefreshSchema, UserReponse
from app.auth.service import inscrire, connecter, rafraichir, envoyer_otp, verifier_otp

router = APIRouter()

@router.post("/inscription")
async def inscription(data: InscriptionSchema, db: AsyncSession = Depends(get_db)):
    result = await inscrire(data, db)
    return {
        "message": "Compte créé",
        "user": UserReponse.model_validate(result["user"]),
        "tokens": result["tokens"]
    }

@router.post("/connexion")
async def connexion(data: ConnexionSchema, db: AsyncSession = Depends(get_db)):
    result = await connecter(data, db)
    return {
        "message": "Connexion réussie",
        "user": UserReponse.model_validate(result["user"]),
        "tokens": result["tokens"]
    }

@router.post("/refresh")
async def refresh(data: RefreshSchema):
    return await rafraichir(data.refresh_token)

@router.post("/otp/envoyer")
async def otp_envoyer(phone: str):
    code = await envoyer_otp(phone)
    return {"message": f"OTP envoyé au {phone}", "dev_code": code}

@router.post("/otp/verifier")
async def otp_verifier(phone: str, code: str, db: AsyncSession = Depends(get_db)):
    return await verifier_otp(phone, code, db)

@router.get("/moi")
async def moi(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "email": user.email,
        "phone": user.phone,
        "statut_partage": user.statut_partage,
        "phone_verifie": user.phone_verifie,
    }