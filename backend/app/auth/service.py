from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.auth.models import User
from app.security import hasher_password, verifier_password, creer_access_token, creer_refresh_token, decoder_token
from app.auth.schemas import InscriptionSchema, ConnexionSchema

async def inscrire(data: InscriptionSchema, db: AsyncSession) -> dict:
    # Vérifier email existant
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")

    # Vérifier phone existant
    if data.phone:
        result = await db.execute(select(User).where(User.phone == data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Téléphone déjà utilisé")

    user = User(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        phone=data.phone,
        hashed_password=hasher_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return {
        "user": user,
        "tokens": {
            "access_token": creer_access_token(user.id),
            "refresh_token": creer_refresh_token(user.id),
            "token_type": "bearer"
        }
    }

async def connecter(data: ConnexionSchema, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verifier_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")

    return {
        "user": user,
        "tokens": {
            "access_token": creer_access_token(user.id),
            "refresh_token": creer_refresh_token(user.id),
            "token_type": "bearer"
        }
    }

async def rafraichir(refresh_token: str) -> dict:
    payload = decoder_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    user_id = payload.get("sub")
    return {
        "access_token": creer_access_token(user_id),
        "refresh_token": creer_refresh_token(user_id),
        "token_type": "bearer"
    }

async def envoyer_otp(phone: str) -> str:
    import random
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # Stockage Redis à implémenter — pour l'instant on affiche dans les logs
    print(f"OTP pour {phone} : {code}")
    return code

async def verifier_otp(phone: str, code: str, db: AsyncSession) -> dict:
    # TODO: vérifier via Redis
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if user:
        user.phone_verifie = True
        await db.flush()
    return {"message": "Téléphone vérifié"}