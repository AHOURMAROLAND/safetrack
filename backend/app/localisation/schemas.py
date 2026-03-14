from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DemarrerPartageSchema(BaseModel):
    nom_lieu: str
    latitude: float
    longitude: float
    heure_arrivee_prevue: datetime
    delai_grace_minutes: Optional[int] = 10

class ValiderArriveeSchema(BaseModel):
    destination_id: str

class DestinationReponse(BaseModel):
    id: str
    user_id: str
    nom_lieu: str
    latitude: float
    longitude: float
    heure_depart: datetime
    heure_arrivee_prevue: datetime
    heure_arrivee_reelle: Optional[datetime] = None
    statut: str
    valide_par_user: bool
    delai_grace_minutes: int
    class Config:
        from_attributes = True

class PositionReponse(BaseModel):
    user_id: str
    nom: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    vitesse: float = 0
    is_moving: bool = False
    battery_level: Optional[int] = None
    timestamp: Optional[str] = None
    statut_partage: str