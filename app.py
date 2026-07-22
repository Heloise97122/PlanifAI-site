from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from decimal import Decimal
from datetime import date, timedelta
from typing import List
import tempfile
import logging
import os
import re
import json

import billing
import planning
import documents
import db
import models
import auth

logger = logging.getLogger("planifai")

app = FastAPI()

# Création des tables + diagnostic de base de données au démarrage.
# Affiche dans les logs quel moteur est réellement utilisé (postgresql / sqlite),
# sans jamais exposer le mot de passe.
try:
    db.init_db()
    with db.engine.connect() as _conn:
        _conn.exec_driver_sql("SELECT 1")
    print(
        f"[PlanifAI] Base de donnees OK — moteur={db.engine.url.get_backend_name()} "
        f"hote={db.engine.url.host or 'local (sqlite ephemere)'}",
        flush=True,
    )
except Exception as _e:
    print(
        f"[PlanifAI] ERREUR base de donnees — moteur={db.engine.url.get_backend_name()} "
        f": {type(_e).__name__}: {_e}",
        flush=True,
    )

# Dossiers
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# --- Sécurité : le site est privé, tout passe derrière la connexion ---
PUBLIC_PATHS = {"/connexion", "/inscription", "/health", "/favicon.ico"}


@app.middleware("http")
async def garde_connexion(request: Request, call_next):
    path = request.url.path
    if path.startswith("/static") or path in PUBLIC_PATHS:
        return await call_next(request)
    if not request.session.get("user_id"):
        return RedirectResponse("/connexion", status_code=303)
    return await call_next(request)


# SessionMiddleware ajouté APRÈS la garde -> il l'enveloppe, la session est
# donc disponible quand la garde s'exécute.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "dev-secret-a-changer-en-production"),
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=False,
)


def utilisateur_courant(request: Request):
    """Retourne l'utilisateur connecté (ou None)."""
    uid = request.session.get("user_id")
    if not uid:
        return None
    session = db.SessionLocal()
    try:
        return session.get(models.User, uid)
    finally:
        session.close()


# === AUTHENTIFICATION ===

@app.get("/connexion", response_class=HTMLResponse)
async def page_connexion(request: Request):
    return templates.TemplateResponse(request, "connexion.html")


@app.post("/connexion")
async def faire_connexion(request: Request, email: str = Form(...), mot_de_passe: str = Form(...)):
    session = db.SessionLocal()
    try:
        user = session.query(models.User).filter(
            models.User.email == email.strip().lower()
        ).first()
        if not user or not auth.verify_password(mot_de_passe, user.password_hash):
            return templates.TemplateResponse(
                request, "connexion.html",
                {"erreur": "Email ou mot de passe incorrect."}, status_code=400,
            )
        request.session["user_id"] = user.id
        return RedirectResponse("/", status_code=303)
    finally:
        session.close()


@app.get("/inscription", response_class=HTMLResponse)
async def page_inscription(request: Request):
    return templates.TemplateResponse(request, "inscription.html")


@app.post("/inscription")
async def faire_inscription(
    request: Request,
    email: str = Form(...),
    mot_de_passe: str = Form(...),
    entreprise: str = Form(""),
    adresse: str = Form(""),
):
    email = email.strip().lower()
    if len(mot_de_passe) < 6:
        return templates.TemplateResponse(
            request, "inscription.html",
            {"erreur": "Le mot de passe doit faire au moins 6 caractères."}, status_code=400,
        )
    session = db.SessionLocal()
    try:
        if session.query(models.User).filter(models.User.email == email).first():
            return templates.TemplateResponse(
                request, "inscription.html",
                {"erreur": "Un compte existe déjà avec cet email."}, status_code=400,
            )
        user = models.User(
            email=email,
            password_hash=auth.hash_password(mot_de_passe),
            entreprise=entreprise.strip(),
            adresse=adresse.strip(),
        )
        session.add(user)
        session.commit()
        request.session["user_id"] = user.id
        return RedirectResponse("/", status_code=303)
    finally:
        session.close()


@app.get("/deconnexion")
async def deconnexion(request: Request):
    request.session.clear()
    return RedirectResponse("/connexion", status_code=303)


def format_eur(value) -> str:
    """Formate un montant à la française : « 1 200,50 € »."""
    montant = Decimal(str(value)).quantize(Decimal("0.01"))
    texte = f"{montant:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} €"


env.filters["eur"] = format_eur
templates.env.filters["eur"] = format_eur


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
    rappels = []
    uid = request.session.get("user_id")
    if uid:
        session = db.SessionLocal()
        try:
            aujourdhui = date.today()
            limite = aujourdhui + timedelta(days=30)
            docs = session.query(models.Document).filter(
                models.Document.user_id == uid,
                models.Document.date_echeance.isnot(None),
                models.Document.date_echeance <= limite,
                models.Document.date_echeance >= aujourdhui - timedelta(days=60),
            ).order_by(models.Document.date_echeance).all()
            for d in docs:
                jours = (d.date_echeance - aujourdhui).days
                rappels.append({
                    "label": d.echeance_label or "Échéance",
                    "tiers": d.tiers or d.titre,
                    "date": d.date_echeance.strftime("%d/%m/%Y"),
                    "jours": jours,
                    "urgent": 0 <= jours <= 7,
                    "retard": jours < 0,
                })
        finally:
            session.close()
    return templates.TemplateResponse(request, "dashboard.html", {"rappels": rappels})


@app.get("/mes-documents", response_class=HTMLResponse)
async def mes_documents(request: Request):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        docs = session.query(models.Document).filter(
            models.Document.user_id == uid
        ).order_by(models.Document.date_creation.desc()).all()
        items = [{
            "id": d.id, "type": d.type, "titre": d.titre, "tiers": d.tiers,
            "montant": d.montant, "numero": d.numero,
            "date": d.date_creation.strftime("%d/%m/%Y") if d.date_creation else "",
        } for d in docs]
    finally:
        session.close()
    return templates.TemplateResponse(request, "mes_documents.html", {"documents": items})


@app.get("/document/{doc_id}", response_class=FileResponse)
async def telecharger_document(request: Request, doc_id: int):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        doc = session.get(models.Document, doc_id)
        if not doc or doc.user_id != uid:
            return RedirectResponse("/mes-documents", status_code=303)
        type_ = doc.type
        fields = json.loads(doc.donnees or "{}")
    finally:
        session.close()
    template, prefix, context = documents.build_context(type_, fields)
    return render_pdf(template, prefix, **context)

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

@app.get("/facturation", response_class=HTMLResponse)
async def facturation_home(request: Request):
    return templates.TemplateResponse(request, "facturation_home.html")

@app.get("/facture", response_class=HTMLResponse)
async def form_facture(request: Request):
    return templates.TemplateResponse(request, "form_facture.html")

@app.get("/devis", response_class=HTMLResponse)
async def form_devis(request: Request):
    return templates.TemplateResponse(request, "form_devis.html")

@app.get("/planning", response_class=HTMLResponse)
async def form_planning(request: Request):
    return templates.TemplateResponse(request, "form_planning.html")


# === GÉNÉRATION PDF ===

def _persist_document(request: Request, type_: str, fields: dict):
    """Sauvegarde le document pour le client connecté (silencieux sinon)."""
    uid = request.session.get("user_id")
    if not uid:
        return
    try:
        titre, tiers, numero, montant, statut, ech_iso, ech_label = documents.summarize(type_, fields)
        ech_date = None
        if ech_iso:
            try:
                ech_date = date.fromisoformat(ech_iso)
            except ValueError:
                ech_date = None
        session = db.SessionLocal()
        try:
            session.add(models.Document(
                user_id=uid, type=type_, titre=titre, tiers=tiers, numero=numero,
                montant=montant, statut=statut, date_echeance=ech_date,
                echeance_label=ech_label, donnees=json.dumps(fields, ensure_ascii=False),
            ))
            session.commit()
        finally:
            session.close()
    except Exception:
        logger.exception("Échec de sauvegarde du document (%s)", type_)


def _save_and_render(request: Request, type_: str, fields: dict):
    """Sauvegarde (si connecté) puis renvoie le PDF."""
    _persist_document(request, type_, fields)
    template, prefix, context = documents.build_context(type_, fields)
    return render_pdf(template, prefix, **context)


@app.post("/generate/cdi", response_class=FileResponse)
async def generate_cdi(
    request: Request,
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
    return _save_and_render(request, "cdi", {
        "nom": nom, "poste": poste, "entreprise": entreprise, "adresse": adresse,
        "date_debut": date_debut, "salaire": salaire, "periode_essai": periode_essai,
        "renouvelable": renouvelable, "logo_url": logo_url,
    })


@app.post("/generate/cdd", response_class=FileResponse)
async def generate_cdd(
    request: Request,
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
    return _save_and_render(request, "cdd", {
        "nom": nom, "poste": poste, "entreprise": entreprise, "adresse": adresse,
        "motif": motif, "date_debut": date_debut, "date_fin": date_fin, "duree": duree,
        "salaire": salaire, "periode_essai": periode_essai, "renouvelable": renouvelable,
        "logo_url": logo_url,
    })


@app.post("/generate/alternance", response_class=FileResponse)
async def generate_alternance(
    request: Request,
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
    return _save_and_render(request, "alternance", {
        "nom": nom, "poste": poste, "entreprise": entreprise, "adresse": adresse,
        "diplome": diplome, "cfa": cfa, "maitre_apprentissage": maitre_apprentissage,
        "date_debut": date_debut, "date_fin": date_fin, "duree": duree, "salaire": salaire,
        "logo_url": logo_url,
    })


@app.post("/generate/stage", response_class=FileResponse)
async def generate_stage(
    request: Request,
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
    return _save_and_render(request, "stage", {
        "nom": nom, "ecole": ecole, "entreprise": entreprise, "adresse": adresse,
        "missions": missions, "tuteur": tuteur, "gratification": gratification,
        "date_debut": date_debut, "date_fin": date_fin, "duree": duree, "logo_url": logo_url,
    })


@app.post("/generate/freelance", response_class=FileResponse)
async def generate_freelance(
    request: Request,
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
    return _save_and_render(request, "freelance", {
        "nom": nom, "entreprise": entreprise, "adresse": adresse, "mission": mission,
        "tjm": tjm, "unite_tarif": unite_tarif, "modalites_paiement": modalites_paiement,
        "date_debut": date_debut, "date_fin": date_fin, "duree": duree, "logo_url": logo_url,
    })


@app.post("/generate/attestation", response_class=FileResponse)
async def generate_attestation(
    request: Request,
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(""),
    logo_url: str = Form(None),
):
    return _save_and_render(request, "attestation", {
        "nom": nom, "poste": poste, "type_contrat": type_contrat, "entreprise": entreprise,
        "adresse": adresse, "date_debut": date_debut, "date_fin": date_fin, "logo_url": logo_url,
    })


@app.post("/generate/facture", response_class=FileResponse)
async def generate_facture(
    request: Request,
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
    return _save_and_render(request, "facture", {
        "entreprise": entreprise, "adresse": adresse, "siret": siret, "email": email,
        "client_nom": client_nom, "client_adresse": client_adresse,
        "numero": numero, "date": date, "echeance": echeance,
        "description": description, "quantite": quantite,
        "prix_unitaire": prix_unitaire, "taux_tva": taux_tva, "logo_url": logo_url,
    })


@app.post("/generate/devis", response_class=FileResponse)
async def generate_devis(
    request: Request,
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
    return _save_and_render(request, "devis", {
        "entreprise": entreprise, "adresse": adresse, "siret": siret, "email": email,
        "client_nom": client_nom, "client_adresse": client_adresse,
        "numero": numero, "date": date, "validite": validite,
        "description": description, "quantite": quantite,
        "prix_unitaire": prix_unitaire, "taux_tva": taux_tva, "logo_url": logo_url,
    })


@app.post("/generate/planning", response_class=FileResponse)
async def generate_planning(
    semaine_debut: str = Form(...),
    titre: str = Form(""),
    entreprise: str = Form(""),
    intervenant: List[str] = Form([]),
    jour: List[str] = Form([]),
    heure_debut: List[str] = Form([]),
    heure_fin: List[str] = Form([]),
    activite: List[str] = Form([]),
    logo_url: str = Form(None),
):
    creneaux = []
    for i in range(max(len(intervenant), len(jour), len(activite))):
        creneaux.append({
            "intervenant": intervenant[i] if i < len(intervenant) else "",
            "jour": jour[i] if i < len(jour) else "",
            "heure_debut": heure_debut[i] if i < len(heure_debut) else "",
            "heure_fin": heure_fin[i] if i < len(heure_fin) else "",
            "activite": activite[i] if i < len(activite) else "",
        })
    grille = planning.construire_planning(creneaux)
    jours = planning.semaine_jours(semaine_debut)
    return render_pdf(
        "pdf_planning.html", "planning",
        nom=f"semaine_{semaine_debut}", titre=titre, entreprise=entreprise,
        jours=jours, intervenants=grille["intervenants"], grille=grille["grille"],
        logo_url=logo_url,
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
