"""Modèles de données PlanifAI."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Text, ForeignKey

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
    # Logo de l'entreprise, stocké en data URI (base64) pour persister avec la base.
    logo = Column(Text, nullable=True)
    # Mentions légales libres, imprimées en bas des factures / devis.
    mentions_legales = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """Un document généré par un client (contrat, facture, devis).

    On stocke un résumé (pour l'historique et les rappels) + les champs bruts
    en JSON (colonne `donnees`) afin de pouvoir régénérer le PDF à la demande.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(String(30), nullable=False)     # cdi, cdd, ..., facture, devis
    titre = Column(String(255), default="")       # libellé lisible
    tiers = Column(String(255), default="")        # salarié / client concerné
    numero = Column(String(80), nullable=True)
    montant = Column(Float, nullable=True)         # total TTC pour factures/devis
    statut = Column(String(20), default="")
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_echeance = Column(Date, nullable=True)    # date qui déclenche un rappel
    echeance_label = Column(String(60), nullable=True)
    donnees = Column(Text, default="{}")           # champs bruts (JSON)
