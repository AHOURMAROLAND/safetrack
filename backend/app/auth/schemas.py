from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class InscriptionSchema(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    phone: Optional[str] = None
    password: str

class ConnexionSchema(BaseModel):
    email: EmailStr
    password: str

class RefreshSchema(BaseModel):
    refresh_token: str

class UserReponse(BaseModel):
    id: str
    nom: str
    prenom: str
    email: str
    phone: Optional[str] = None
    photo_profil: Optional[str] = None
    statut_partage: str
    phone_verifie: bool
    date_inscription: datetime

    class Config:
        from_attributes = True