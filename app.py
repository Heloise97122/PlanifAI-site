from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import re

app = FastAPI()

# Dossiers
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))


def _slug(value: str) -> str:
    """Nettoie une valeur pour un nom de fichier."""
    value = (value or "document").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "document"


def render_pdf(template_name: str, filename_prefix: str, **context) -> FileResponse:
    """Rend un template en HTML puis le convertit en PDF téléchargeable."""
    template = env.get_template(template_name)
    html_content = template.render(**context)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html_content).write_pdf(tmp.name)
    filename = f"{filename_prefix}_{_slug(context.get('nom'))}.pdf"
    return FileResponse(tmp.name, filename=filename, media_type="application/pdf")


# === PAGES HTML (formulaires) ===

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/rh-ai", response_class=HTMLResponse)
async def rh_ai_home(request: Request):
    return templates.TemplateResponse(request, "rh_ai_home.html")

@app.get("/cdi", response_class=HTMLResponse)
async def form_cdi(request: Request):
    return templates.TemplateResponse(request, "form_cdi.html")

@app.get("/cdd", response_class=HTMLResponse)
async def form_cdd(request: Request):
    return templates.TemplateResponse(request, "form_cdd.html")

@app.get("/alternance", response_class=HTMLResponse)
async def form_alternance(request: Request):
    return templates.TemplateResponse(request, "form_alternance.html")

@app.get("/stage", response_class=HTMLResponse)
async def form_stage(request: Request):
    return templates.TemplateResponse(request, "form_stage.html")

@app.get("/freelance", response_class=HTMLResponse)
async def form_freelance(request: Request):
    return templates.TemplateResponse(request, "form_freelance.html")

@app.get("/attestation", response_class=HTMLResponse)
async def form_attestation(request: Request):
    return templates.TemplateResponse(request, "form_attestation.html")

# Route héritée : renvoie vers le formulaire CDI
@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse(request, "form_cdi.html")


# === GÉNÉRATION PDF ===

@app.post("/generate/cdi", response_class=FileResponse)
async def generate_cdi(
    nom: str = Form(...),
    poste: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    date_debut: str = Form(...),
    salaire: str = Form(...),
    periode_essai: str = Form(""),
    renouvelable: str = Form("Non"),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_cdi.html", "contrat_cdi",
        nom=nom, poste=poste, entreprise=entreprise, adresse=adresse,
        date_debut=date_debut, salaire=salaire, periode_essai=periode_essai,
        renouvelable=renouvelable, logo_url=logo_url,
    )


@app.post("/generate/cdd", response_class=FileResponse)
async def generate_cdd(
    nom: str = Form(...),
    poste: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    motif: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    duree: str = Form(...),
    salaire: str = Form(...),
    periode_essai: str = Form(""),
    renouvelable: str = Form("Non"),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_cdd.html", "contrat_cdd",
        nom=nom, poste=poste, entreprise=entreprise, adresse=adresse,
        motif=motif, date_debut=date_debut, date_fin=date_fin, duree=duree,
        salaire=salaire, periode_essai=periode_essai, renouvelable=renouvelable,
        logo_url=logo_url,
    )


@app.post("/generate/alternance", response_class=FileResponse)
async def generate_alternance(
    nom: str = Form(...),
    poste: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    diplome: str = Form(...),
    cfa: str = Form(...),
    maitre_apprentissage: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    duree: str = Form(...),
    salaire: str = Form(...),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_alternance.html", "contrat_alternance",
        nom=nom, poste=poste, entreprise=entreprise, adresse=adresse,
        diplome=diplome, cfa=cfa, maitre_apprentissage=maitre_apprentissage,
        date_debut=date_debut, date_fin=date_fin, duree=duree, salaire=salaire,
        logo_url=logo_url,
    )


@app.post("/generate/stage", response_class=FileResponse)
async def generate_stage(
    nom: str = Form(...),
    ecole: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    missions: str = Form(...),
    tuteur: str = Form(...),
    gratification: str = Form(""),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    duree: str = Form(...),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_stage.html", "convention_stage",
        nom=nom, ecole=ecole, entreprise=entreprise, adresse=adresse,
        missions=missions, tuteur=tuteur, gratification=gratification,
        date_debut=date_debut, date_fin=date_fin, duree=duree, logo_url=logo_url,
    )


@app.post("/generate/freelance", response_class=FileResponse)
async def generate_freelance(
    nom: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    mission: str = Form(...),
    tjm: str = Form(...),
    unite_tarif: str = Form("par jour"),
    modalites_paiement: str = Form(""),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    duree: str = Form(""),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_freelance.html", "contrat_freelance",
        nom=nom, entreprise=entreprise, adresse=adresse, mission=mission,
        tjm=tjm, unite_tarif=unite_tarif, modalites_paiement=modalites_paiement,
        date_debut=date_debut, date_fin=date_fin, duree=duree, logo_url=logo_url,
    )


@app.post("/generate/attestation", response_class=FileResponse)
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_attestation.html", "attestation",
        nom=nom, poste=poste, type_contrat=type_contrat, entreprise=entreprise,
        adresse=adresse, date_debut=date_debut, date_fin=date_fin, logo_url=logo_url,
    )


# Route héritée : génère un CDI (compatibilité avec l'ancien formulaire)
@app.post("/generate_rh", response_class=FileResponse)
async def generate_rh_contract(
    nom: str = Form(...),
    poste: str = Form(...),
    entreprise: str = Form("Entreprise"),
    date_debut: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    periode_essai: str = Form(""),
    renouvelable: str = Form("Non"),
    logo_url: str = Form(None),
):
    return render_pdf(
        "pdf_cdi.html", "contrat_cdi",
        nom=nom, poste=poste, entreprise=entreprise, adresse=adresse,
        date_debut=date_debut, salaire=salaire, periode_essai=periode_essai,
        renouvelable=renouvelable, logo_url=logo_url,
    )
