from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List
import tempfile
import logging
import os
import re
import base64
import json
import secrets
import hashlib

import billing
import planning
import documents
import db
import models
import auth
import mailer
import rdv

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
PUBLIC_PATHS = {
    "/connexion", "/inscription", "/health", "/favicon.ico",
    "/mot-de-passe-oublie",
}
PUBLIC_PREFIXES = ("/static", "/reinitialiser", "/rdv")


@app.middleware("http")
async def garde_connexion(request: Request, call_next):
    path = request.url.path
    if path.startswith(PUBLIC_PREFIXES) or path in PUBLIC_PATHS:
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


def prochain_numero(request: Request, type_: str) -> str:
    """Calcule le prochain numéro de facture/devis pour le compte connecté.

    Format : FACT-2026-0001 (factures) / DEVIS-2026-0001 (devis), séquence par
    an et par compte. Le numéro reste modifiable côté formulaire.
    """
    prefixe = "FACT" if type_ == "facture" else "DEVIS"
    annee = date.today().year
    uid = request.session.get("user_id")
    maxn = 0
    if uid:
        motif = re.compile(rf"^{prefixe}-{annee}-(\d+)$")
        session = db.SessionLocal()
        try:
            numeros = session.query(models.Document.numero).filter(
                models.Document.user_id == uid,
                models.Document.type == type_,
            ).all()
        finally:
            session.close()
        for (num,) in numeros:
            m = motif.match(num or "")
            if m:
                maxn = max(maxn, int(m.group(1)))
    return f"{prefixe}-{annee}-{maxn + 1:04d}"


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


# === MOT DE PASSE OUBLIÉ ===

RESET_TTL_HEURES = 1


def _base_url(request: Request) -> str:
    """URL de base du site pour construire les liens des e-mails.

    Priorité à APP_URL (défini sur Render) pour éviter les soucis http/https
    derrière le proxy ; sinon on déduit depuis la requête.
    """
    base = os.environ.get("APP_URL", "").strip().rstrip("/")
    return base or str(request.base_url).rstrip("/")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@app.get("/mot-de-passe-oublie", response_class=HTMLResponse)
async def page_mot_de_passe_oublie(request: Request):
    return templates.TemplateResponse(request, "mot_de_passe_oublie.html")


@app.post("/mot-de-passe-oublie")
async def demander_reinitialisation(request: Request, email: str = Form(...)):
    email = email.strip().lower()
    session = db.SessionLocal()
    try:
        user = session.query(models.User).filter(models.User.email == email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token_hash = _hash_token(token)
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=RESET_TTL_HEURES)
            session.commit()
            lien = f"{_base_url(request)}/reinitialiser/{token}"
            html = (
                "<p>Bonjour,</p>"
                "<p>Vous avez demandé à réinitialiser votre mot de passe PlanifAI. "
                "Cliquez sur le lien ci-dessous (valable 1 heure) :</p>"
                f'<p><a href="{lien}">Choisir un nouveau mot de passe</a></p>'
                "<p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail : "
                "votre mot de passe reste inchangé.</p>"
                "<p>— PlanifAI</p>"
            )
            mailer.envoyer_email(email, "Réinitialisation de votre mot de passe PlanifAI", html)
    finally:
        session.close()
    # Message identique que le compte existe ou non (on ne révèle pas les e-mails inscrits).
    return templates.TemplateResponse(request, "mot_de_passe_oublie.html", {"envoye": True})


@app.get("/reinitialiser/{token}", response_class=HTMLResponse)
async def page_reinitialiser(request: Request, token: str):
    session = db.SessionLocal()
    try:
        user = session.query(models.User).filter(
            models.User.reset_token_hash == _hash_token(token),
            models.User.reset_token_expires > datetime.utcnow(),
        ).first()
    finally:
        session.close()
    if not user:
        return templates.TemplateResponse(request, "reinitialiser.html", {"invalide": True})
    return templates.TemplateResponse(request, "reinitialiser.html", {"token": token})


@app.post("/reinitialiser/{token}")
async def faire_reinitialiser(
    request: Request, token: str,
    nouveau: str = Form(...), confirmation: str = Form(...),
):
    session = db.SessionLocal()
    try:
        user = session.query(models.User).filter(
            models.User.reset_token_hash == _hash_token(token),
            models.User.reset_token_expires > datetime.utcnow(),
        ).first()
        if not user:
            return templates.TemplateResponse(request, "reinitialiser.html", {"invalide": True})
        if len(nouveau) < 6:
            return templates.TemplateResponse(request, "reinitialiser.html", {
                "token": token, "erreur": "Le mot de passe doit faire au moins 6 caractères.",
            }, status_code=400)
        if nouveau != confirmation:
            return templates.TemplateResponse(request, "reinitialiser.html", {
                "token": token, "erreur": "La confirmation ne correspond pas.",
            }, status_code=400)
        user.password_hash = auth.hash_password(nouveau)
        user.reset_token_hash = None
        user.reset_token_expires = None
        session.commit()
    finally:
        session.close()
    return templates.TemplateResponse(request, "reinitialiser.html", {"succes": True})


# === MON ENTREPRISE (profil + logo) ===

MAX_LOGO = 2_000_000  # 2 Mo


@app.get("/mon-entreprise", response_class=HTMLResponse)
async def page_entreprise(request: Request):
    user = utilisateur_courant(request)
    return templates.TemplateResponse(request, "mon_entreprise.html", {
        "entreprise": user.entreprise if user else "",
        "adresse": user.adresse if user else "",
        "logo": user.logo if user else None,
        "mentions_legales": (user.mentions_legales if user else "") or "",
        "enregistre": request.query_params.get("ok") == "1",
    })


@app.post("/mon-entreprise")
async def sauver_entreprise(
    request: Request,
    entreprise: str = Form(""),
    adresse: str = Form(""),
    mentions_legales: str = Form(""),
    logo: UploadFile = File(None),
    supprimer_logo: str = Form(""),
):
    uid = request.session.get("user_id")
    erreur = None
    changer_logo = False
    nouveau_logo = None

    if supprimer_logo == "1":
        changer_logo, nouveau_logo = True, None
    elif logo is not None and logo.filename:
        data = await logo.read()
        ctype = logo.content_type or ""
        if not ctype.startswith("image/"):
            erreur = "Le fichier doit être une image (PNG, JPG…)."
        elif len(data) > MAX_LOGO:
            erreur = "Le logo est trop lourd (2 Mo maximum)."
        else:
            nouveau_logo = f"data:{ctype};base64," + base64.b64encode(data).decode()
            changer_logo = True

    session = db.SessionLocal()
    try:
        user = session.get(models.User, uid)
        if erreur:
            return templates.TemplateResponse(request, "mon_entreprise.html", {
                "entreprise": entreprise, "adresse": adresse,
                "mentions_legales": mentions_legales, "logo": user.logo, "erreur": erreur,
            }, status_code=400)
        user.entreprise = entreprise.strip()
        user.adresse = adresse.strip()
        user.mentions_legales = mentions_legales.strip()
        if changer_logo:
            user.logo = nouveau_logo
        session.commit()
    finally:
        session.close()
    return RedirectResponse("/mon-entreprise?ok=1", status_code=303)


@app.post("/mon-mot-de-passe")
async def changer_mot_de_passe(
    request: Request,
    actuel: str = Form(...),
    nouveau: str = Form(...),
    confirmation: str = Form(...),
):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        user = session.get(models.User, uid)

        def _reponse(mdp_erreur=None, mdp_ok=False, code=200):
            return templates.TemplateResponse(request, "mon_entreprise.html", {
                "entreprise": user.entreprise or "", "adresse": user.adresse or "",
                "logo": user.logo, "mentions_legales": user.mentions_legales or "",
                "mdp_erreur": mdp_erreur, "mdp_ok": mdp_ok,
            }, status_code=code)

        if not auth.verify_password(actuel, user.password_hash):
            return _reponse(mdp_erreur="Mot de passe actuel incorrect.", code=400)
        if len(nouveau) < 6:
            return _reponse(mdp_erreur="Le nouveau mot de passe doit faire au moins 6 caractères.", code=400)
        if nouveau != confirmation:
            return _reponse(mdp_erreur="La confirmation ne correspond pas au nouveau mot de passe.", code=400)

        user.password_hash = auth.hash_password(nouveau)
        session.commit()
        return _reponse(mdp_ok=True)
    finally:
        session.close()


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


# === PRISE DE RENDEZ-VOUS EN LIGNE ===

RDV_HORIZON = 14  # nombre de jours réservables à l'avance


def _slug_unique(session, souhaite: str, user_id: int) -> str:
    """Retourne un slug libre, en ajoutant -2, -3… si déjà pris par un autre compte."""
    base = rdv.slugify(souhaite)
    candidat, n = base, 1
    while True:
        occupe = session.query(models.User).filter(
            models.User.rdv_slug == candidat, models.User.id != user_id
        ).first()
        if not occupe:
            return candidat
        n += 1
        candidat = f"{base}-{n}"


@app.get("/mes-disponibilites", response_class=HTMLResponse)
async def page_disponibilites(request: Request):
    user = utilisateur_courant(request)
    lien = None
    if user and user.rdv_slug:
        lien = f"{_base_url(request)}/rdv/{user.rdv_slug}"
    return templates.TemplateResponse(request, "mes_disponibilites.html", {
        "actif": bool(user and user.rdv_actif),
        "jours": rdv.parse_jours(user.rdv_jours if user else "0,1,2,3,4"),
        "heure_debut": (user.rdv_heure_debut if user else None) or "08:00",
        "heure_fin": (user.rdv_heure_fin if user else None) or "17:00",
        "duree": (user.rdv_duree if user else None) or 60,
        "slug": user.rdv_slug if user else "",
        "lien": lien,
        "enregistre": request.query_params.get("ok") == "1",
        "jours_noms": list(enumerate(rdv.JOURS_FR)),
    })


@app.post("/mes-disponibilites")
async def sauver_disponibilites(
    request: Request,
    actif: str = Form(""),
    jours: List[str] = Form([]),
    heure_debut: str = Form("08:00"),
    heure_fin: str = Form("17:00"),
    duree: int = Form(60),
    slug: str = Form(""),
):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        user = session.get(models.User, uid)
        user.rdv_actif = 1 if actif == "1" else 0
        user.rdv_jours = ",".join(j for j in jours if j.isdigit()) or "0,1,2,3,4"
        user.rdv_heure_debut = heure_debut
        user.rdv_heure_fin = heure_fin
        user.rdv_duree = duree if duree in (30, 60) else 60
        souhaite = slug.strip() or user.entreprise or user.email.split("@")[0]
        if not user.rdv_slug or slug.strip():
            user.rdv_slug = _slug_unique(session, souhaite, user.id)
        session.commit()
    finally:
        session.close()
    return RedirectResponse("/mes-disponibilites?ok=1", status_code=303)


@app.get("/mes-rendez-vous", response_class=HTMLResponse)
async def page_mes_rdv(request: Request):
    user = utilisateur_courant(request)
    lien = f"{_base_url(request)}/rdv/{user.rdv_slug}" if (user and user.rdv_slug) else None
    session = db.SessionLocal()
    try:
        rdvs = session.query(models.RendezVous).filter(
            models.RendezVous.user_id == user.id,
            models.RendezVous.statut == "confirme",
            models.RendezVous.jour >= date.today(),
        ).order_by(models.RendezVous.jour, models.RendezVous.heure).all()
        items = [{
            "id": r.id,
            "jour_label": rdv.libelle_jour(r.jour), "heure": r.heure,
            "client_nom": r.client_nom, "client_tel": r.client_tel,
            "client_email": r.client_email, "motif": r.motif,
        } for r in rdvs]
    finally:
        session.close()
    return templates.TemplateResponse(request, "mes_rendez_vous.html", {
        "rdvs": items, "actif": bool(user and user.rdv_actif), "lien": lien,
    })


def _pro_par_slug(session, slug: str):
    return session.query(models.User).filter(models.User.rdv_slug == slug).first()


@app.get("/rdv/{slug}", response_class=HTMLResponse)
async def page_rdv_public(request: Request, slug: str):
    session = db.SessionLocal()
    try:
        pro = _pro_par_slug(session, slug)
        if not pro or not pro.rdv_actif:
            return templates.TemplateResponse(request, "rdv_public.html", {"indisponible": True})

        jours = rdv.jours_reservables(pro.rdv_jours, RDV_HORIZON)
        jour_choisi = request.query_params.get("jour")
        jour_sel = None
        for j in jours:
            if j.isoformat() == jour_choisi:
                jour_sel = j
                break
        if jour_sel is None and jours:
            jour_sel = jours[0]

        creneaux = []
        if jour_sel:
            prises = [h for (h,) in session.query(models.RendezVous.heure).filter(
                models.RendezVous.user_id == pro.id,
                models.RendezVous.jour == jour_sel,
                models.RendezVous.statut == "confirme",
            ).all()]
            creneaux = rdv.creneaux_libres(
                jour_sel, pro.rdv_heure_debut or "08:00", pro.rdv_heure_fin or "17:00",
                pro.rdv_duree or 60, prises)

        jours_aff = [{"iso": j.isoformat(), "label": rdv.libelle_jour(j),
                      "sel": (j == jour_sel)} for j in jours]
    finally:
        session.close()
    return templates.TemplateResponse(request, "rdv_public.html", {
        "entreprise": pro.entreprise or "Prise de rendez-vous",
        "slug": slug, "jours": jours_aff, "creneaux": creneaux,
        "jour_sel": jour_sel.isoformat() if jour_sel else "",
        "jour_sel_label": rdv.libelle_jour(jour_sel) if jour_sel else "",
    })


@app.post("/rdv/{slug}", response_class=HTMLResponse)
async def reserver_rdv(
    request: Request, slug: str,
    jour: str = Form(...), heure: str = Form(...),
    client_nom: str = Form(...), client_tel: str = Form(""),
    client_email: str = Form(""), motif: str = Form(""),
):
    session = db.SessionLocal()
    try:
        pro = _pro_par_slug(session, slug)
        if not pro or not pro.rdv_actif:
            return templates.TemplateResponse(request, "rdv_public.html", {"indisponible": True})
        try:
            jour_date = date.fromisoformat(jour)
        except ValueError:
            return RedirectResponse(f"/rdv/{slug}", status_code=303)

        # Le créneau est-il toujours libre ? (évite la double réservation)
        deja = session.query(models.RendezVous).filter(
            models.RendezVous.user_id == pro.id,
            models.RendezVous.jour == jour_date,
            models.RendezVous.heure == heure,
            models.RendezVous.statut == "confirme",
        ).first()
        if deja:
            return templates.TemplateResponse(request, "rdv_public.html", {
                "entreprise": pro.entreprise or "Prise de rendez-vous", "slug": slug,
                "erreur": "Ce créneau vient d'être réservé. Merci d'en choisir un autre.",
                "recommencer": True,
            }, status_code=409)

        token = secrets.token_urlsafe(24)
        rendezvous = models.RendezVous(
            user_id=pro.id, jour=jour_date, heure=heure,
            client_nom=client_nom.strip(), client_tel=client_tel.strip(),
            client_email=client_email.strip(), motif=motif.strip(),
            gestion_token_hash=_hash_token(token),
        )
        session.add(rendezvous)
        session.commit()

        jour_label = rdv.libelle_jour(jour_date)
        pro_email = pro.email
        pro_nom = pro.entreprise or "votre prestataire"
    finally:
        session.close()

    lien_gestion = f"{_base_url(request)}/rdv/gerer/{token}"

    # E-mails (best-effort : un échec d'envoi ne bloque pas la réservation).
    if client_email.strip():
        mailer.envoyer_email(
            client_email.strip(),
            f"Confirmation de votre rendez-vous — {pro_nom}",
            f"<p>Bonjour {client_nom.strip()},</p>"
            f"<p>Votre rendez-vous avec <strong>{pro_nom}</strong> est confirmé :</p>"
            f"<p><strong>{jour_label} à {heure}</strong></p>"
            + (f"<p>Motif : {motif.strip()}</p>" if motif.strip() else "")
            + f'<p>Besoin d\'annuler ou de déplacer ce rendez-vous ? '
              f'<a href="{lien_gestion}">Gérer mon rendez-vous</a></p>'
            + "<p>À bientôt !</p><p>— PlanifAI</p>",
        )
    if pro_email:
        mailer.envoyer_email(
            pro_email,
            f"Nouveau rendez-vous : {client_nom.strip()} — {jour_label} à {heure}",
            f"<p>Nouveau rendez-vous réservé en ligne :</p>"
            f"<p><strong>{jour_label} à {heure}</strong></p>"
            f"<p>Client : {client_nom.strip()}<br>"
            f"Téléphone : {client_tel.strip() or '—'}<br>"
            f"E-mail : {client_email.strip() or '—'}</p>"
            + (f"<p>Motif : {motif.strip()}</p>" if motif.strip() else "")
            + "<p>— PlanifAI</p>",
        )

    return templates.TemplateResponse(request, "rdv_public.html", {
        "entreprise": pro_nom, "confirme": True,
        "jour_sel_label": jour_label, "heure": heure,
    })


# --- Gestion d'un RDV par le client (annuler / reporter) via lien e-mail ---

def _rdv_par_token(session, token: str):
    return session.query(models.RendezVous).filter(
        models.RendezVous.gestion_token_hash == _hash_token(token)
    ).first()


def _notifier(destinataire: str, sujet: str, html: str):
    if destinataire:
        mailer.envoyer_email(destinataire, sujet, html + "<p>— PlanifAI</p>")


@app.get("/rdv/gerer/{token}", response_class=HTMLResponse)
async def page_gerer_rdv(request: Request, token: str):
    session = db.SessionLocal()
    try:
        r = _rdv_par_token(session, token)
        if not r:
            return templates.TemplateResponse(request, "rdv_gerer.html", {"introuvable": True})
        pro = session.get(models.User, r.user_id)
        ctx = {
            "token": token,
            "entreprise": (pro.entreprise if pro else "") or "votre prestataire",
            "jour_label": rdv.libelle_jour(r.jour), "heure": r.heure,
            "motif": r.motif,
            "annule": r.statut == "annule",
            "passe": r.jour < date.today(),
        }
    finally:
        session.close()
    return templates.TemplateResponse(request, "rdv_gerer.html", ctx)


@app.post("/rdv/gerer/{token}/annuler", response_class=HTMLResponse)
async def annuler_rdv_client(request: Request, token: str):
    session = db.SessionLocal()
    try:
        r = _rdv_par_token(session, token)
        if not r:
            return templates.TemplateResponse(request, "rdv_gerer.html", {"introuvable": True})
        pro = session.get(models.User, r.user_id)
        entreprise = (pro.entreprise if pro else "") or "votre prestataire"
        if r.statut != "annule":
            r.statut = "annule"
            session.commit()
            jour_label = rdv.libelle_jour(r.jour)
            _notifier(pro.email if pro else "",
                      f"Rendez-vous annulé : {r.client_nom} — {jour_label} à {r.heure}",
                      f"<p>Le client <strong>{r.client_nom}</strong> a annulé son rendez-vous "
                      f"du <strong>{jour_label} à {r.heure}</strong>. Le créneau est de nouveau libre.</p>")
    finally:
        session.close()
    return templates.TemplateResponse(request, "rdv_gerer.html", {
        "entreprise": entreprise, "annule_ok": True,
    })


@app.get("/rdv/gerer/{token}/reporter", response_class=HTMLResponse)
async def page_reporter_rdv(request: Request, token: str):
    session = db.SessionLocal()
    try:
        r = _rdv_par_token(session, token)
        if not r:
            return templates.TemplateResponse(request, "rdv_gerer.html", {"introuvable": True})
        pro = session.get(models.User, r.user_id)
        jours = rdv.jours_reservables(pro.rdv_jours, RDV_HORIZON) if pro else []
        jour_choisi = request.query_params.get("jour")
        jour_sel = next((j for j in jours if j.isoformat() == jour_choisi), None) or (jours[0] if jours else None)
        creneaux = []
        if jour_sel:
            prises = [h for (h,) in session.query(models.RendezVous.heure).filter(
                models.RendezVous.user_id == pro.id, models.RendezVous.jour == jour_sel,
                models.RendezVous.statut == "confirme", models.RendezVous.id != r.id,
            ).all()]
            creneaux = rdv.creneaux_libres(jour_sel, pro.rdv_heure_debut or "08:00",
                                           pro.rdv_heure_fin or "17:00", pro.rdv_duree or 60, prises)
        jours_aff = [{"iso": j.isoformat(), "label": rdv.libelle_jour(j), "sel": (j == jour_sel)} for j in jours]
        ctx = {
            "token": token, "reporter": True,
            "entreprise": (pro.entreprise if pro else "") or "votre prestataire",
            "jour_label": rdv.libelle_jour(r.jour), "heure": r.heure,
            "jours": jours_aff, "creneaux": creneaux,
            "jour_sel": jour_sel.isoformat() if jour_sel else "",
            "jour_sel_label": rdv.libelle_jour(jour_sel) if jour_sel else "",
        }
    finally:
        session.close()
    return templates.TemplateResponse(request, "rdv_gerer.html", ctx)


@app.post("/rdv/gerer/{token}/reporter", response_class=HTMLResponse)
async def reporter_rdv(request: Request, token: str,
                       jour: str = Form(...), heure: str = Form(...)):
    session = db.SessionLocal()
    try:
        r = _rdv_par_token(session, token)
        if not r:
            return templates.TemplateResponse(request, "rdv_gerer.html", {"introuvable": True})
        pro = session.get(models.User, r.user_id)
        entreprise = (pro.entreprise if pro else "") or "votre prestataire"
        try:
            jour_date = date.fromisoformat(jour)
        except ValueError:
            return RedirectResponse(f"/rdv/gerer/{token}/reporter", status_code=303)

        # Le nouveau créneau est-il libre ? (hors ce RDV lui-même)
        deja = session.query(models.RendezVous).filter(
            models.RendezVous.user_id == pro.id, models.RendezVous.jour == jour_date,
            models.RendezVous.heure == heure, models.RendezVous.statut == "confirme",
            models.RendezVous.id != r.id,
        ).first()
        if deja:
            return RedirectResponse(f"/rdv/gerer/{token}/reporter", status_code=303)

        ancien = f"{rdv.libelle_jour(r.jour)} à {r.heure}"
        r.jour, r.heure, r.statut = jour_date, heure, "confirme"
        session.commit()
        nouveau = f"{rdv.libelle_jour(jour_date)} à {heure}"
        client_email, client_nom = r.client_email, r.client_nom
        pro_email = pro.email if pro else ""
    finally:
        session.close()

    _notifier(client_email,
              f"Rendez-vous déplacé — {entreprise}",
              f"<p>Bonjour {client_nom},</p><p>Votre rendez-vous avec <strong>{entreprise}</strong> "
              f"est désormais fixé au <strong>{nouveau}</strong> (au lieu du {ancien}).</p>"
              f'<p><a href="{_base_url(request)}/rdv/gerer/{token}">Gérer mon rendez-vous</a></p>')
    _notifier(pro_email,
              f"Rendez-vous déplacé : {client_nom} — {nouveau}",
              f"<p>Le client <strong>{client_nom}</strong> a déplacé son rendez-vous : "
              f"<strong>{nouveau}</strong> (au lieu du {ancien}).</p>")

    return templates.TemplateResponse(request, "rdv_gerer.html", {
        "entreprise": entreprise, "reporte_ok": True, "jour_sel_label": nouveau,
    })


@app.post("/mes-rendez-vous/{rdv_id}/annuler")
async def annuler_rdv_pro(request: Request, rdv_id: int):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        r = session.get(models.RendezVous, rdv_id)
        if r and r.user_id == uid and r.statut != "annule":
            r.statut = "annule"
            session.commit()
            jour_label = rdv.libelle_jour(r.jour)
            _notifier(r.client_email,
                      "Votre rendez-vous a été annulé",
                      f"<p>Bonjour {r.client_nom},</p><p>Votre rendez-vous du "
                      f"<strong>{jour_label} à {r.heure}</strong> a été annulé par le prestataire. "
                      f"N'hésitez pas à réserver un autre créneau.</p>")
    finally:
        session.close()
    return RedirectResponse("/mes-rendez-vous", status_code=303)


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
                models.Document.statut != "paye",  # une facture payée ne se rappelle plus
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
            # Rendez-vous à venir (7 prochains jours) dans les rappels.
            prochains = session.query(models.RendezVous).filter(
                models.RendezVous.user_id == uid,
                models.RendezVous.statut == "confirme",
                models.RendezVous.jour >= aujourdhui,
                models.RendezVous.jour <= aujourdhui + timedelta(days=7),
            ).order_by(models.RendezVous.jour, models.RendezVous.heure).all()
            for r in prochains:
                jours = (r.jour - aujourdhui).days
                rappels.append({
                    "label": f"RDV {r.heure}",
                    "tiers": r.client_nom or "Client",
                    "date": r.jour.strftime("%d/%m/%Y"),
                    "jours": jours,
                    "urgent": 0 <= jours <= 2,
                    "retard": False,
                })
            rappels.sort(key=lambda x: x["jours"])
        finally:
            session.close()
    return templates.TemplateResponse(request, "dashboard.html", {"rappels": rappels})


@app.get("/mes-documents", response_class=HTMLResponse)
async def mes_documents(request: Request):
    uid = request.session.get("user_id")
    aujourdhui = date.today()
    annee = aujourdhui.year
    session = db.SessionLocal()
    try:
        docs = session.query(models.Document).filter(
            models.Document.user_id == uid
        ).order_by(models.Document.date_creation.desc()).all()
        items, encaisse_annee, encaisse_mois, attente = [], 0.0, 0.0, 0.0
        for d in docs:
            is_facture = d.type == "facture"
            paye = d.statut == "paye"
            en_retard = (is_facture and not paye and d.date_echeance is not None
                         and d.date_echeance < aujourdhui)
            if is_facture and (d.montant is not None):
                if paye:
                    dp = d.date_paiement or (d.date_creation.date() if d.date_creation else aujourdhui)
                    if dp.year == annee:
                        encaisse_annee += d.montant
                        if dp.month == aujourdhui.month:
                            encaisse_mois += d.montant
                else:
                    attente += d.montant
            items.append({
                "id": d.id, "type": d.type, "titre": d.titre, "tiers": d.tiers,
                "montant": d.montant, "numero": d.numero, "is_facture": is_facture,
                "paye": paye, "en_retard": en_retard,
                "relance": d.date_relance.strftime("%d/%m/%Y") if d.date_relance else None,
                "date": d.date_creation.strftime("%d/%m/%Y") if d.date_creation else "",
            })
        resume = {"encaisse_annee": encaisse_annee, "encaisse_mois": encaisse_mois,
                  "attente": attente, "annee": annee}
        a_des_factures = any(i["is_facture"] for i in items)
    finally:
        session.close()
    return templates.TemplateResponse(request, "mes_documents.html", {
        "documents": items, "resume": resume, "a_des_factures": a_des_factures,
    })


@app.post("/document/{doc_id}/paiement")
async def marquer_paiement(request: Request, doc_id: int, paye: str = Form("")):
    uid = request.session.get("user_id")
    session = db.SessionLocal()
    try:
        doc = session.get(models.Document, doc_id)
        if doc and doc.user_id == uid and doc.type == "facture":
            if paye == "1":
                doc.statut = "paye"
                doc.date_paiement = date.today()
            else:
                doc.statut = "attente"
                doc.date_paiement = None
            session.commit()
    finally:
        session.close()
    return RedirectResponse("/mes-documents", status_code=303)


def _message_relance_defaut(user, doc, fields):
    """Texte de relance pré-rempli (modifiable par l'artisan avant envoi)."""
    client = fields.get("client_nom", "") or "Madame, Monsieur"
    entreprise = (user.entreprise if user else "") or "Votre prestataire"
    montant = format_eur(doc.montant) if doc.montant is not None else ""
    ech = ""
    if doc.date_echeance:
        ech = f" (échéance du {doc.date_echeance.strftime('%d/%m/%Y')})"
    return (
        f"Bonjour {client},\n\n"
        f"Sauf erreur de notre part, la facture n° {doc.numero or ''} "
        f"d'un montant de {montant}{ech} demeure impayée à ce jour.\n\n"
        f"Nous vous remercions de bien vouloir procéder à son règlement dès que possible. "
        f"Si le paiement a déjà été effectué, merci de ne pas tenir compte de ce message.\n\n"
        f"Cordialement,\n{entreprise}"
    )


@app.get("/document/{doc_id}/relance", response_class=HTMLResponse)
async def page_relance(request: Request, doc_id: int):
    uid = request.session.get("user_id")
    user = utilisateur_courant(request)
    session = db.SessionLocal()
    try:
        doc = session.get(models.Document, doc_id)
        if not doc or doc.user_id != uid or doc.type != "facture":
            return RedirectResponse("/mes-documents", status_code=303)
        fields = json.loads(doc.donnees or "{}")
        ctx = {
            "doc_id": doc.id, "numero": doc.numero or "",
            "montant": format_eur(doc.montant) if doc.montant is not None else "",
            "client_email": fields.get("client_email", ""),
            "sujet": f"Relance — facture {doc.numero or ''}".strip(" —"),
            "message": _message_relance_defaut(user, doc, fields),
            "sans_email": not mailer.email_configure(),
        }
    finally:
        session.close()
    return templates.TemplateResponse(request, "relance.html", ctx)


@app.post("/document/{doc_id}/relance", response_class=HTMLResponse)
async def envoyer_relance(request: Request, doc_id: int,
                          destinataire: str = Form(...), sujet: str = Form(...),
                          message: str = Form(...)):
    uid = request.session.get("user_id")
    user = utilisateur_courant(request)
    session = db.SessionLocal()
    try:
        doc = session.get(models.Document, doc_id)
        if not doc or doc.user_id != uid or doc.type != "facture":
            return RedirectResponse("/mes-documents", status_code=303)
        numero = doc.numero or ""
    finally:
        session.close()

    corps_html = "<p>" + message.strip().replace("\n", "<br>\n") + "</p>"
    nom_expediteur = (user.entreprise if user else "") or None
    envoye = mailer.envoyer_email(
        destinataire.strip(), sujet.strip(), corps_html,
        nom_expediteur=nom_expediteur,
        repondre_a=(user.email if user else None),
    )

    if envoye:
        # Mémoriser la date de relance + l'e-mail client saisi (pour la prochaine fois).
        session = db.SessionLocal()
        try:
            doc = session.get(models.Document, doc_id)
            if doc:
                doc.date_relance = date.today()
                fields = json.loads(doc.donnees or "{}")
                fields["client_email"] = destinataire.strip()
                doc.donnees = json.dumps(fields, ensure_ascii=False)
                session.commit()
        finally:
            session.close()

    return templates.TemplateResponse(request, "relance.html", {
        "envoye": envoye, "echec": not envoye, "numero": numero,
        "destinataire": destinataire.strip(),
    })


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
    return _render_with_logo(request, type_, fields)

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
    return templates.TemplateResponse(
        request, "form_facture.html", {"numero_suggere": prochain_numero(request, "facture")}
    )

@app.get("/devis", response_class=HTMLResponse)
async def form_devis(request: Request):
    return templates.TemplateResponse(
        request, "form_devis.html", {"numero_suggere": prochain_numero(request, "devis")}
    )

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


def _render_with_logo(request: Request, type_: str, fields: dict):
    """Injecte le logo et les mentions légales du compte, puis renvoie le PDF."""
    f = dict(fields)
    user = utilisateur_courant(request)
    f["logo_url"] = user.logo if (user and user.logo) else None
    f["mentions_legales"] = (user.mentions_legales if user else "") or ""
    template, prefix, context = documents.build_context(type_, f)
    return render_pdf(template, prefix, **context)


def _save_and_render(request: Request, type_: str, fields: dict):
    """Sauvegarde les champs bruts (sans le logo) puis renvoie le PDF avec le logo du compte."""
    _persist_document(request, type_, fields)
    return _render_with_logo(request, type_, fields)


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
    client_email: str = Form(""),
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
        "client_nom": client_nom, "client_adresse": client_adresse, "client_email": client_email,
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
    request: Request,
    semaine_debut: str = Form(...),
    titre: str = Form(""),
    entreprise: str = Form(""),
    intervenant: List[str] = Form([]),
    jour: List[str] = Form([]),
    heure_debut: List[str] = Form([]),
    heure_fin: List[str] = Form([]),
    activite: List[str] = Form([]),
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
    user = utilisateur_courant(request)
    logo = user.logo if (user and user.logo) else None
    return render_pdf(
        "pdf_planning.html", "planning",
        nom=f"semaine_{semaine_debut}", titre=titre, entreprise=entreprise,
        jours=jours, intervenants=grille["intervenants"], grille=grille["grille"],
        logo_url=logo,
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
