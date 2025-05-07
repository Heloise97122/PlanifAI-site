from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration des templates Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Fichiers statiques (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Page d’accueil avec formulaire RH
@app.get("/", response_class=HTMLResponse)
async def formulaire():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>RH-AI | Générateur de contrat</title>
    </head>
    <body>
        <form method="post" action="/generate">
            <h2>Générateur de contrat RH</h2>
            <input name="nom" placeholder="Nom" />
            <input name="poste" placeholder="Poste" />
            <input name="type_contrat" placeholder="Type de contrat" />
            <input name="date_debut" type="date" placeholder="Date de début" />
            <input name="duree" placeholder="Durée" />
            <input name="salaire" placeholder="Salaire mensuel" />
            <input name="adresse" placeholder="Adresse de l'entreprise" />
            <button type="submit">Générer le contrat</button>
        </form>
    </body>
    </html>
    """

# Route de génération PDF
@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...)
):
    template = env.get_template("contrat_template.html")
    html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        duree=duree,
        salaire=salaire,
        adresse=adresse
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html).write_pdf(tmp_pdf.name)
        pdf_path = tmp_pdf.name

    return FileResponse(pdf_path, media_type="application/pdf", filename="contrat_rh.pdf")
