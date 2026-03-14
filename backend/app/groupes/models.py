import uuid
import random
import string
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

def generer_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Groupe(Base):
    __tablename__ = "groupes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom: Mapped[str] = mapped_column(String(100))
    code_unique: Mapped[str] = mapped_column(String(6), unique=True, default=generer_code)
    createur_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    max_membres: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    groupe_id: Mapped[str] = mapped_column(String(36), ForeignKey("groupes.id"), index=True)
    statut: Mapped[str] = mapped_column(String(20), default="pending")
    role: Mapped[str] = mapped_column(String(20), default="membre")
    nom_affiche: Mapped[str] = mapped_column(String(100))
    date_demande: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    date_approbation: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)