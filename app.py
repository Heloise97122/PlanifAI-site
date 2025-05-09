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

# === ROUTES GET ===

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/rh-home", response_class=HTMLResponse)
async def rh_home(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})


# === ROUTES POST : Génération de PDF ===

def render_pdf(template_name, context, filename="document.pdf"):
    html_content = env.get_template(template_name).render(context)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=filename)

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
    context = {
        "nom": nom, "poste": poste, "type_contrat": type_contrat,
        "date_debut": date_debut, "duree": duree, "salaire": salaire,
        "adresse": adresse, "periode_essai": periode_essai,
        "renouvelable": renouvelable, "logo_url": logo_url
    }
    return render_pdf("contrat_template.html", context, f"contrat_{nom}.pdf")


@app.post("/generate_cdi")
async def generate_cdi(
    nom: str = Form(...), poste: str = Form(...), salaire: str = Form(...),
    date_debut: str = Form(...), adresse: str = Form(...), logo_url: str = Form(None)
):
    context = {
        "nom": nom, "poste": poste, "salaire": salaire,
        "date_debut": date_debut, "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("contrat_cdi.html", context, f"cdi_{nom}.pdf")


@app.post("/generate_cdd")
async def generate_cdd(
    nom: str = Form(...), poste: str = Form(...), salaire: str = Form(...),
    date_debut: str = Form(...), date_fin: str = Form(...), adresse: str = Form(...),
    logo_url: str = Form(None)
):
    context = {
        "nom": nom, "poste": poste, "salaire": salaire,
        "date_debut": date_debut, "date_fin": date_fin,
        "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("contrat_cdd.html", context, f"cdd_{nom}.pdf")


@app.post("/generate_freelance")
async def generate_freelance(
    nom: str = Form(...), mission: str = Form(...), duree: str = Form(...),
    remuneration: str = Form(...), adresse: str = Form(...), logo_url: str = Form(None)
):
    context = {
        "nom": nom, "mission": mission, "duree": duree,
        "remuneration": remuneration, "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("contrat_freelance.html", context, f"freelance_{nom}.pdf")


@app.post("/generate_alternance")
async def generate_alternance(
    nom: str = Form(...), poste: str = Form(...), duree: str = Form(...),
    centre: str = Form(...), rythme: str = Form(...), date_debut: str = Form(...),
    adresse: str = Form(...), logo_url: str = Form(None)
):
    context = {
        "nom": nom, "poste": poste, "duree": duree,
        "centre": centre, "rythme": rythme, "date_debut": date_debut,
        "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("contrat_alternance.html", context, f"alternance_{nom}.pdf")


@app.post("/generate_stage")
async def generate_stage(
    nom: str = Form(...), poste: str = Form(...), duree: str = Form(...),
    gratification: str = Form(...), tuteur: str = Form(...), date_debut: str = Form(...),
    adresse: str = Form(...), logo_url: str = Form(None)
):
    context = {
        "nom": nom, "poste": poste, "duree": duree, "gratification": gratification,
        "tuteur": tuteur, "date_debut": date_debut, "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("contrat_stage.html", context, f"stage_{nom}.pdf")


@app.post("/generate_attestation")
async def generate_attestation(
    nom: str = Form(...), poste: str = Form(...), date_sortie: str = Form(...),
    adresse: str = Form(...), logo_url: str = Form(None)
):
    context = {
        "nom": nom, "poste": poste, "date_sortie": date_sortie,
        "adresse": adresse, "logo_url": logo_url
    }
    return render_pdf("attestation_template.html", context, f"attestation_{nom}.pdf")