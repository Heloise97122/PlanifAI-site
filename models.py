"""Modèles de données PlanifAI."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from db import Base


class User(Base):
    """Un compte client (une entreprise qui utilise PlanifAI)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    # Profil de l'entreprise, réutilisé pour pré-remplir les documents.
    entreprise = Column(String(255), default="")
    adresse = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
