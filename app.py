from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration Jinja2 pour accéder aux fichiers templates
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# Page d'accueil RH
@app.get("/rh-ai", response_class=HTMLResponse)
async def rh_home():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(content=template.render())

# Formulaire RH global
@app.get("/formulaire", response_class=HTMLResponse)
async def formulaire():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(content=template.render())

# Génération des contrats dynamiques
@app.post("/generate-contract", response_class=HTMLResponse)
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
    temps_travail: str = Form(...),
    remboursement_transport: str = Form(...),
    droits_conges: str = Form(...),
    logo_url: str = Form(None),
    gratification: str = Form(None),
    tuteur: str = Form(None),
    ecole: str = Form(None),
    rythme: str = Form(None)
):
    # Sélection dynamique du bon template
    if type_contrat.lower() == "cdi":
        template_file = "contrat_cdi.html"
    elif type_contrat.lower() == "cdd":
        template_file = "contrat_cdd.html"
    elif type_contrat.lower() == "stage":
        template_file = "contrat_stage.html"
    elif type_contrat.lower() == "alternance":
        template_file = "contrat_alternance.html"
    elif type_contrat.lower() == "freelance":
        template_file = "contrat_freelance.html"