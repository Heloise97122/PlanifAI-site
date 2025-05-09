from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration des templates et fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# ROUTE: Accueil RH-AI
@app.get("/rh-ai-home", response_class=HTMLResponse)
async def rh_ai_home(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# ROUTE: Dashboard principal
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ROUTES FORMULAIRES (Affichage)

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


# ROUTES POST PDF (génération contrats & attestations)

@app.post("/generate_pdf", response_class=FileResponse)
async def generate_pdf(
    template_name: str = Form(...),
    nom: str = Form(...),
    poste: str = Form(None),
    type_contrat: str = Form(None),
    date_debut: str = Form(None),
    duree: str = Form(None),
    salaire: str = Form(None),
    adresse: str = Form(None),
    periode_essai: str = Form(None),
    renouvelable: str = Form(None),
    entreprise: str = Form(None),
    objet: str = Form(None),
    lieu: str = Form(None),
    tuteur: str = Form(None),
    rythme: str = Form(None),
    organisme: str = Form(None),
    gratification: str = Form(None),
    logo_url: str = Form(None),
):
    template = env.get_template(template_name)
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
        entreprise=entreprise,
        objet=objet,
        lieu=lieu,
        tuteur=tuteur,
        rythme=rythme,
        organisme=organisme,
        gratification=gratification,
        logo_url=logo_url,
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"document_{nom}.pdf")