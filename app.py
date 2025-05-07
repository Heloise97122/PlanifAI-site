from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os
from datetime import date

app = FastAPI()

# Config Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Dossier statique
app.mount("/static", StaticFiles(directory="static"), name="static")

# PAGE RH-AI (accueil)
@app.get("/rh-ai", response_class=HTMLResponse)
async def page_rh_ai():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(content=template.render())

# FORMULAIRE CONTRAT
@app.get("/", response_class=HTMLResponse)
async def formulaire_contrat():
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

        <p style="text-align: center; margin-top: 20px;">
            <a href="/rh-ai" style="text-decoration: none; color: #1e90ff;">← Retour à l’accueil RH-AI</a>
        </p>
    </body>
    </html>
    """

# TRAITEMENT CONTRAT
@app.post("/generate")
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
    rendered_html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        duree=duree,
        salaire=salaire,
        adresse=adresse
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=rendered_html).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf", media_type='application/pdf')

# FORMULAIRE ATTESTATION
@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>Attestation RH</title>
    </head>
    <body>
        <form method="post" action="/attestation">
            <h2>Générateur d'attestation employeur</h2>
            <input name="nom" placeholder="Nom de l'employé" />
            <input name="poste" placeholder="Poste occupé" />
            <input name="type_contrat" placeholder="Type de contrat (CDI, CDD...)" />
            <input name="date_debut" type="date" placeholder="Date de début" />
            <input name="entreprise" placeholder="Nom de l'entreprise" />
            <input name="adresse" placeholder="Adresse de l'entreprise" />
            <button type="submit">Générer l’attestation</button>
        </form>

        <p style="text-align: center; margin-top: 20px;">
            <a href="/rh-ai" style="text-decoration: none; color: #1e90ff;">← Retour à l’accueil RH-AI</a>
        </p>
    </body>
    </html>
    """

# TRAITEMENT ATTESTATION
@app.post("/attestation")
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...)
):
    template = env.get_template("attestation_template.html")
    rendered_html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        entreprise=entreprise,
        adresse=adresse,
        date_du_jour=date.today().strftime("%Y-%m-%d")
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=rendered_html).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf", media_type='application/pdf')