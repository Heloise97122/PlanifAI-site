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
    # Réinitialisation de mot de passe : on stocke un HASH du jeton (jamais le jeton
    # brut) + sa date d'expiration. Le lien envoyé par e-mail contient le jeton brut.
    reset_token_hash = Column(String(64), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    # Prise de rendez-vous en ligne (page publique /rdv/<slug>).
    rdv_actif = Column(Integer, default=0)                 # 0/1 : la prise de RDV est-elle ouverte
    rdv_slug = Column(String(120), unique=True, index=True, nullable=True)
    rdv_jours = Column(String(30), default="0,1,2,3,4")    # jours ouvrés (0 = lundi)
    rdv_heure_debut = Column(String(5), default="08:00")
    rdv_heure_fin = Column(String(5), default="17:00")
    rdv_duree = Column(Integer, default=60)                # durée d'un créneau en minutes
    created_at = Column(DateTime, default=datetime.utcnow)


class RendezVous(Base):
    """Un rendez-vous réservé par un client sur la page publique d'un pro."""

    __tablename__ = "rendez_vous"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # le pro
    jour = Column(Date, nullable=False, index=True)
    heure = Column(String(5), nullable=False)              # « HH:MM »
    client_nom = Column(String(255), default="")
    client_email = Column(String(255), default="")
    client_tel = Column(String(40), default="")
    motif = Column(Text, default="")
    statut = Column(String(20), default="confirme")        # confirme / annule
    date_creation = Column(DateTime, default=datetime.utcnow)


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
