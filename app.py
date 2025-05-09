from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# ROUTES GET : affichage des pages
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

@app.get("/freelance", response_class=HTMLResponse)
async def freelance(request: Request):
    return templates.TemplateResponse("formulaire_freelance.html", {"request": request})

@app.get("/attestation", response_class=HTMLResponse)
async def attestation(request: Request):
    return templates.TemplateResponse("formulaire_attestation.html", {"request": request})

@app.get("/alternance", response_class=HTMLResponse)
async def alternance(request: Request):
    return templates.TemplateResponse("formulaire_alternance.html", {"request": request})

@app.get("/stage", response_class=HTMLResponse)
async def stage(request: Request):
    return templates.TemplateResponse("formulaire_stage.html", {"request": request})

# ROUTES POST : génération de PDF

@app.post("/generate_rh")
async def generate_rh(
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
    html_content = env.get_template("contrat_rh_template.html").render(
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return FileResponse(tmp.name, filename=f"Contrat_RH_{nom}.pdf")

@app.post("/generate_freelance")
async def generate_freelance(
    nom: str = Form(...),
    mission: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    tarif: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    html_content = env.get_template("contrat_freelance_template.html").render(
        nom=nom,
        mission=mission,
        date_debut=date_debut,
        date_fin=date_fin,
        tarif=tarif,
        adresse=adresse,
        logo_url=logo_url
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return FileResponse(tmp.name, filename=f"Freelance_{nom}.pdf")

@app.post("/generate_attestation")
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    date_entree: str = Form(...),
    date_sortie: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    html_content = env.get_template("attestation_template.html").render(
        nom=nom,
        poste=poste,
        date_entree=date_entree,
        date_sortie=date_sortie,
        adresse=adresse,
        logo_url=logo_url
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return FileResponse(tmp.name, filename=f"Attestation_{nom}.pdf")

@app.post("/generate_alternance")
async def generate_alternance(
    nom: str = Form(...),
    poste: str = Form(...),
    type_alternance: str = Form(...),
    duree: str = Form(...),
    centre_formation: str = Form(...),
    rythme: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    html_content = env.get_template("contrat_alternance_template.html").render(
        nom=nom,
        poste=poste,
        type_alternance=type_alternance,
        duree=duree,
        centre_formation=centre_formation,
        rythme=rythme,
        salaire=salaire,
        adresse=adresse,
        logo_url=logo_url
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return FileResponse(tmp.name, filename=f"Alternance_{nom}.pdf")

@app.post("/generate_stage")
async def generate_stage(
    nom: str = Form(...),
    poste: str = Form(...),
    duree: str = Form(...),
    gratification: str = Form(...),
    tuteur: str = Form(...),
    centre_formation: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    html_content = env.get_template("contrat_stage_template.html").render(
        nom=nom,
        poste=poste,
        duree=duree,
        gratification=gratification,
        tuteur=tuteur,
        centre_formation=centre_formation,
        adresse=adresse,
        logo_url=logo_url
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_content).write_pdf(tmp.name)
        return FileResponse(tmp.name, filename=f"Stage_{nom}.pdf")