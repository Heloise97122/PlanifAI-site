"""Configuration de la base de données (SQLAlchemy).

En local, on utilise SQLite (un simple fichier, aucun serveur à installer).
En production, il suffit de définir la variable d'environnement DATABASE_URL
(ex. une base PostgreSQL hébergée) : le reste du code ne change pas.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./planifai.db")

# Certains hébergeurs fournissent une URL "postgres://" ; SQLAlchemy attend "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Crée les tables si elles n'existent pas encore."""
    import models  # noqa: F401  (nécessaire pour enregistrer les modèles)
    Base.metadata.create_all(bind=engine)
