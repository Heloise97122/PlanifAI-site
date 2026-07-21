FROM python:3.11-slim

# Dépendances système nécessaires à WeasyPrint (génération des PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY . .

# Render/Railway fournissent le port via la variable $PORT (défaut : 8000)
ENV PORT=8000
EXPOSE 8000

# Lancement du serveur (forme shell pour que $PORT soit bien substitué)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}
