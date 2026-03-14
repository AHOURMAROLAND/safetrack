from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreerGroupeSchema(BaseModel):
    nom: str
    max_membres: Optional[int] = 100

class RejoindreGroupeSchema(BaseModel):
    code_unique: str
    nom_affiche: str

class GererMembreSchema(BaseModel):
    action: str  # approve, reject, ban

class GroupeReponse(BaseModel):
    id: str
    nom: str
    code_unique: str
    createur_id: str
    max_membres: int
    is_active: bool
    date_creation: datetime
    class Config:
        from_attributes = True

class MembershipReponse(BaseModel):
    id: str
    user_id: str
    groupe_id: str
    statut: str
    role: str
    nom_affiche: str
    date_demande: datetime
    date_approbation: Optional[datetime] = None
    class Config:
        from_attributes = True