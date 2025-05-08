from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration Jinja2
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# Page RH-AI : formulaire contrat
@app.get("/rh-ai", response_class=HTMLResponse)
async def formulaire():
    return """
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
        <title>RH-AI | Générateur de contrat</title>
    </head>
    <body>
        <h2>Générateur de contrat RH</h2>
        <form method='post' action='/generate'>
            <input name='nom' placeholder="Nom" required />
            <input name='poste' placeholder="Poste" required />
            <input name='type_contrat' placeholder="Type de contrat" required />
            <input name='date_debut' type='date' placeholder="Date de début" required />
            <input name='duree' placeholder="Durée" required />
            <input name='salaire' placeholder="Salaire mensuel" required />
            <input name='adresse' placeholder="Adresse de l'entreprise" required />
            <input name='periode_essai' placeholder="Durée de la période d'essai (ex: 2 mois)" required />
            <label>Renouvelable ?</label>
            <input type='radio' name='renouvelable' value='Oui' checked> Oui
            <input type='radio' name='renouvelable' value='Non'> Non
            <input name='logo_url' placeholder="URL du logo (optionnel)" />
            <button type='submit'>Générer le contrat</button>
        </form>
        <p><a href="/attestation">Générer une attestation employeur</a></p>
    </body>
    </html>
    """

# Traitement PDF Contrat
@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    periode_essai: str = Form(...),
    renouvelable: str = Form(...),
    logo_url: str = Form(None)
):
    template = env.get_template("contrat_template.html")
    html_content = template.render(
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

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf")

# Page RH-AI : formulaire attestation
@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation():
    return """
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
        <title>RH-AI | Attestation Employeur</title>
    </head>
    <body>
        <h2>Générateur d’attestation employeur</h2>
        <form method='post' action='/generate-attestation'>
            <input name='employeur' placeholder="Nom de l'employeur" required />
            <input name='entreprise' placeholder="Nom de l’entreprise" required />
            <input name='adresse' placeholder="Adresse de l’entreprise" required />
            <input name='nom_employe' placeholder="Nom de l’employé(e)" required />
            <input name='poste' placeholder="Poste de l’employé(e)" required />
            <input name='date_embauche' type='date' placeholder="Date d'embauche" required />
            <input name='type_contrat' placeholder="Type de contrat (CDI, CDD…)" required />
            <input name='salaire' placeholder="Salaire mensuel brut" required />
            <input name='date_du_jour' type='date' placeholder="Date de rédaction" required />
            <button type='submit'>Générer l’attestation</button>
        </form>
        <p><a href="/rh-ai">Retour au générateur de contrat</a></p>
    </body>
    </html>
    """

# Traitement PDF Attestation
@app.post("/generate-attestation", response_class=HTMLResponse)
async def generate_attestation(
    employeur: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    nom_employe: str = Form(...),
    poste: str = Form(...),
    date_embauche: str = Form(...),
    type_contrat: str = Form(...),
    salaire: str = Form(...),
    date_du_jour: str = Form(...)
):
    template = env.get_template("attestation.html")
    html_content = template.render(
        employeur=employeur,
        entreprise=entreprise,
        adresse=adresse,
        nom_employe=nom_employe,
        poste=poste,
        date_embauche=date_embauche,
        type_contrat=type_contrat,
        salaire=salaire,
        date_du_jour=date_du_jour
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom_employe}.pdf")