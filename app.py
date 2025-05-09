from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Jinja2 + fichiers statiques
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# PAGE ACCUEIL
@app.get("/", response_class=HTMLResponse)
async def home():
    template = env.get_template("index.html")
    return HTMLResponse(template.render())

# FORMULAIRE RH GÉNÉRAL
@app.get("/rh-ai", response_class=HTMLResponse)
async def formulaire_rh():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(template.render())

# GÉNÉRATION CONTRAT CDI / CDD
@app.post("/generate-contrat", response_class=FileResponse)
async def generate_contrat(
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
    template = env.get_template("contrat_cdi_cdd.html")
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

# FORMULAIRE FREELANCE
@app.get("/freelance", response_class=HTMLResponse)
async def formulaire_freelance():
    template = env.get_template("formulaire_freelance.html")
    return HTMLResponse(template.render())

# GÉNÉRATION CONTRAT FREELANCE
@app.post("/generate-freelance", response_class=FileResponse)
async def generate_freelance(
    nom: str = Form(...),
    mission: str = Form(...),
    duree: str = Form(...),
    remuneration: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    template = env.get_template("contrat_freelance.html")
    html_content = template.render(
        nom=nom,
        mission=mission,
        duree=duree,
        remuneration=remuneration,
        adresse=adresse,
        logo_url=logo_url
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"freelance_{nom}.pdf")

# FORMULAIRE ATTESTATION
@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation():
    template = env.get_template("formulaire_attestation.html")
    return HTMLResponse(template.render())

# GÉNÉRATION ATTESTATION
@app.post("/generate-attestation", response_class=FileResponse)
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    template = env.get_template("attestation.html")
    html_content = template.render(
        nom=nom,
        poste=poste,
        date_debut=date_debut,
        date_fin=date_fin,
        adresse=adresse,
        logo_url=logo_url
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf")