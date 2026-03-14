import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class AlerteDanger(Base):
    __tablename__ = "alertes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    declencheur_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    groupe_id: Mapped[str] = mapped_column(String(36), ForeignKey("groupes.id"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    type_declenchement: Mapped[str] = mapped_column(String(30), default="manuel")
    message_court: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    est_fausse_alerte: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class AudioUrgence(Base):
    __tablename__ = "audio_urgences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alerte_id: Mapped[str] = mapped_column(String(36), ForeignKey("alertes.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    numero_segment: Mapped[int] = mapped_column(Integer, default=1)
    duree_secondes: Mapped[int] = mapped_column(Integer, default=0)
    url_fichier: Mapped[str | None] = mapped_column(String(500), nullable=True)
    taille_octets: Mapped[int] = mapped_column(Integer, default=0)
    is_uploade: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp_debut: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
