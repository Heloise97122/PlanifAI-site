from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os
from datetime import datetime

app = FastAPI()

# Configuration Jinja2
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/rh-ai", response_class=HTMLResponse)
async def formulaire():
    return """
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
        <title>RH-AI | Documents RH</title>
    </head>
    <body>
        <h2>Générateur de documents RH</h2>
        <form method='post' action='/generate'>
            <input name='nom' placeholder="Nom" required />
            <input name='poste' placeholder="Poste" required />
            <input name='type_contrat' placeholder="Type de contrat" required />
            <input name='date_debut' type='date' placeholder="Date de début" required />
            <input name='duree' placeholder="Durée du contrat" required />
            <input name='salaire' placeholder="Salaire mensuel brut" required />
            <input name='adresse' placeholder="Adresse de l'entreprise" required />
            <input name='periode_essai' placeholder="Période d'essai (ex: 2 mois)" required />
            <label>Renouvelable ?</label>
            <input type='radio' name='renouvelable' value='Oui' checked> Oui
            <input type='radio' name='renouvelable' value='Non'> Non
            <input name='logo_url' placeholder="URL du logo (optionnel)" />

            <br><br>
            <button type='submit' name='type_doc' value='contrat'>Générer le contrat</button>
            <button type='submit' name='type_doc' value='attestation'>Générer une attestation</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_document(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    periode_essai: str = Form(...),
    renouvelable: str = Form(...),
    logo_url: str = Form(None),
    type_doc: str = Form(...)
):
    # Sélection du bon template
    if type_doc == "attestation":
        template = env.get_template("attestation_template.html")
        rendered = template.render(
            nom=nom,
            poste=poste,
            type_contrat=type_contrat,
            date_debut=date_debut,
            salaire=salaire,
            adresse=adresse,
            date_du_jour=datetime.now().strftime("%d/%m/%Y")
        )
        filename = f"attestation_{nom}.pdf"
    else:
        template = env.get_template("contrat_template.html")
        rendered = template.render(
            nom=nom,
            poste=poste,
            type_contrat=type_contrat,
            date_debut=date_debut,
            duree=duree,
            salaire=salaire,
            adresse=adresse,
            periode_essai=periode_essai,
            renouvelable=renouvelable,
            logo_url=logo_url
        )
        filename = f"contrat_{nom}.pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=rendered).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=filename)