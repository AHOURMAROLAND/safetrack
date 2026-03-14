import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class LocationUpdate(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    groupe_id: Mapped[str] = mapped_column(String(36), ForeignKey("groupes.id"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    vitesse: Mapped[float] = mapped_column(Float, default=0)
    is_moving: Mapped[bool] = mapped_column(Boolean, default=False)
    battery_level: Mapped[int] = mapped_column(Integer, default=100)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    nom_lieu: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    heure_depart: Mapped[datetime] = mapped_column(DateTime)
    heure_arrivee_prevue: Mapped[datetime] = mapped_column(DateTime)
    heure_arrivee_reelle: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    statut: Mapped[str] = mapped_column(String(20), default="en_route")
    valide_par_user: Mapped[bool] = mapped_column(Boolean, default=False)
    delai_grace_minutes: Mapped[int] = mapped_column(Integer, default=10)
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)