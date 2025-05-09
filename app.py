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

# Accueil tableau de bord
@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Page RH-AI
@app.get("/rh-ai", response_class=HTMLResponse)
async def rh_ai_home(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# Formulaire Attestation employeur
@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

# Génération PDF Attestation
@app.post("/generate_attestation", response_class=FileResponse)
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    entreprise: str = Form(...),
    date_debut: str = Form(...),
    lieu: str = Form(...),
    date_signature: str = Form(...)
):
    template = env.get_template("attestation_template.html")
    html_content = template.render(
        nom=nom,
        poste=poste,
        entreprise=entreprise,
        date_debut=date_debut,
        lieu=lieu,
        date_signature=date_signature
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf")