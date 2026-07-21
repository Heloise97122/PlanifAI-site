from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from decimal import Decimal
from typing import List
import tempfile
import logging
import re

import billing

logger = logging.getLogger("planifai")

app = FastAPI()

# Dossiers
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))


def format_eur(value) -> str:
    """Formate un montant à la française : « 1 200,50 € »."""
    montant = Decimal(str(value)).quantize(Decimal("0.01"))
    texte = f"{montant:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} €"


env.filters["eur"] = format_eur


def _slug(value: str) -> str:
    """Nettoie une valeur pour un nom de fichier."""
    value = (value or "document").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "document"


def _error_page() -> HTMLResponse:
    """Page d'erreur claire pour l'utilisateur (sans détail technique)."""
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<title>PlanifAI | Erreur</title><link rel="stylesheet" href="/static/style.css"></head>
<body>
    <h1>Le PDF n'a pas pu être généré</h1>
    <p>Un problème technique est survenu. Vous pouvez :</p>
    <ul>
        <li>vérifier que tous les champs obligatoires sont remplis ;</li>
        <li>réessayer sans renseigner l'URL du logo (une adresse invalide peut bloquer la génération) ;</li>
        <li>revenir en arrière et soumettre à nouveau le formulaire.</li>
    </ul>
    <p><a href="/">&larr; Retour au tableau de bord</a></p>
</body></html>""",
        status_code=500,
    )


def render_pdf(template_name: str, filename_prefix: str, **context):
    """Rend un template en HTML puis le convertit en PDF téléchargeable.

    En cas d'échec (template, WeasyPrint, logo inaccessible...), l'erreur est
    journalisée côté serveur et une page claire est renvoyée à l'utilisateur.
    """
    try:
        template = env.get_template(template_name)
        html_content = template.render(**context)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        HTML(string=html_content).write_pdf(tmp.name)
        filename = f"{filename_prefix}_{_slug(context.get('nom'))}.pdf"
        return FileResponse(tmp.name, filename=filename, media_type="application/pdf")
    except Exception:
        logger.exception("Échec de génération du PDF (%s)", template_name)
        return _error_page()


# === SANTÉ / MONITORING ===

@app.get("/health")
async def health():
    return {"status": "ok", "service": "PlanifAI"}


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

@app.get("/facture", response_class=HTMLResponse)
async def form_facture(request: Request):
    return templates.TemplateResponse(request, "form_facture.html")

@app.get("/devis", response_class=HTMLResponse)
async def form_devis(request: Request):
    return templates.TemplateResponse(request, "form_devis.html")


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


def _construire_lignes(descriptions, quantites, prix, taux):
    """Reconstruit une liste de lignes à partir des champs répétés du formulaire."""
    lignes = []
    for i in range(max(len(descriptions), len(quantites), len(prix), len(taux))):
        lignes.append({
            "description": descriptions[i] if i < len(descriptions) else "",
            "quantite": quantites[i] if i < len(quantites) else "0",
            "prix_unitaire": prix[i] if i < len(prix) else "0",
            "taux_tva": taux[i] if i < len(taux) else "0",
        })
    return lignes


@app.post("/generate/facture", response_class=FileResponse)
async def generate_facture(
    entreprise: str = Form(...),
    adresse: str = Form(...),
    siret: str = Form(""),
    email: str = Form(""),
    client_nom: str = Form(...),
    client_adresse: str = Form(...),
    numero: str = Form(...),
    date: str = Form(...),
    echeance: str = Form(""),
    description: List[str] = Form([]),
    quantite: List[str] = Form([]),
    prix_unitaire: List[str] = Form([]),
    taux_tva: List[str] = Form([]),
    logo_url: str = Form(None),
):
    calc = billing.compute_invoice(
        _construire_lignes(description, quantite, prix_unitaire, taux_tva)
    )
    return render_pdf(
        "pdf_facturation.html", "facture",
        nom=numero, type_document="Facture",
        entreprise=entreprise, adresse=adresse, siret=siret, email=email,
        client_nom=client_nom, client_adresse=client_adresse,
        numero=numero, date=date,
        date_limite=echeance, date_limite_label="Échéance",
        calc=calc, logo_url=logo_url,
    )


@app.post("/generate/devis", response_class=FileResponse)
async def generate_devis(
    entreprise: str = Form(...),
    adresse: str = Form(...),
    siret: str = Form(""),
    email: str = Form(""),
    client_nom: str = Form(...),
    client_adresse: str = Form(...),
    numero: str = Form(...),
    date: str = Form(...),
    validite: str = Form(""),
    description: List[str] = Form([]),
    quantite: List[str] = Form([]),
    prix_unitaire: List[str] = Form([]),
    taux_tva: List[str] = Form([]),
    logo_url: str = Form(None),
):
    calc = billing.compute_invoice(
        _construire_lignes(description, quantite, prix_unitaire, taux_tva)
    )
    return render_pdf(
        "pdf_facturation.html", "devis",
        nom=numero, type_document="Devis",
        entreprise=entreprise, adresse=adresse, siret=siret, email=email,
        client_nom=client_nom, client_adresse=client_adresse,
        numero=numero, date=date,
        date_limite=validite, date_limite_label="Validité",
        calc=calc, logo_url=logo_url,
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
