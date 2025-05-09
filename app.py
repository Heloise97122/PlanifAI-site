from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Config
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# PAGE ACCUEIL RH
@app.get("/rh-ai-home", response_class=HTMLResponse)
async def rh_ai_home(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# DASHBOARD
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# FORMULAIRES

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

# ROUTES DE GENERATION DE PDF

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
        return FileResponse(tmp.name, filename=f"Contrat_{nom}.pdf")

# Tu peux dupliquer cette logique pour les autres types de PDF :
# - generate_freelance
# - generate_attestation
# - generate_alternance
# - generate_stage