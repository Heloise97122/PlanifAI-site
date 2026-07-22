"""Configuration de la base de données (SQLAlchemy).

En local, on utilise SQLite (un simple fichier, aucun serveur à installer).
En production, il suffit de définir la variable d'environnement DATABASE_URL
(ex. une base PostgreSQL hébergée) : le reste du code ne change pas.
"""

import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./planifai.db")

# Certains hébergeurs fournissent une URL "postgres://" ; SQLAlchemy attend "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _ajouter_colonne_si_absente(table: str, colonne: str, type_sql: str):
    """Mini-migration : ajoute une colonne à une table existante si elle manque.

    Évite d'avoir besoin d'Alembic pour de simples ajouts de colonnes.
    Fonctionne sur SQLite comme sur PostgreSQL.
    """
    try:
        colonnes = [c["name"] for c in inspect(engine).get_columns(table)]
        if colonne not in colonnes:
            with engine.begin() as conn:
                conn.exec_driver_sql(f'ALTER TABLE {table} ADD COLUMN {colonne} {type_sql}')
    except Exception:
        # Table pas encore créée, ou permission : create_all s'en occupe.
        pass


def init_db():
    """Crée les tables si elles n'existent pas, et applique les mini-migrations."""
    import models  # noqa: F401  (nécessaire pour enregistrer les modèles)
    Base.metadata.create_all(bind=engine)
    _ajouter_colonne_si_absente("users", "logo", "TEXT")
    _ajouter_colonne_si_absente("users", "mentions_legales", "TEXT")
    _ajouter_colonne_si_absente("users", "reset_token_hash", "VARCHAR(64)")
    _ajouter_colonne_si_absente("users", "reset_token_expires", "TIMESTAMP")
