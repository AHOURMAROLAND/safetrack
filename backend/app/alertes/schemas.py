from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeclencherSOSSchema(BaseModel):
    latitude: float
    longitude: float
    groupe_id: str
    type_declenchement: Optional[str] = "manuel"
    message_court: Optional[str] = None

class AnnulerSOSSchema(BaseModel):
    alerte_id: str

class AlerteReponse(BaseModel):
    id: str
    declencheur_id: str
    groupe_id: str
    latitude: float
    longitude: float
    type_declenchement: str
    message_court: Optional[str] = None
    is_active: bool
    est_fausse_alerte: bool
    timestamp: datetime
    class Config:
        from_attributes = True

class AudioReponse(BaseModel):
    id: str
    alerte_id: str
    user_id: str
    numero_segment: int
    duree_secondes: int
    url_fichier: Optional[str] = None
    is_uploade: bool
    timestamp_debut: datetime
    class Config:
        from_attributes = True