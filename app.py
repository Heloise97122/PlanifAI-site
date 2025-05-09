from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()
env = Environment(loader=FileSystemLoader("templates"))

# Assure-toi que ce dossier existe !
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def accueil():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(template.render())

@app.get("/rh", response_class=HTMLResponse)
async def formulaire_rh():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(template.render())

def render_pdf_from_template(template_name, context, filename_prefix):
    template = env.get_template(template_name)
    html_content = template.render(**context)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"{filename_prefix}_{context['nom']}.pdf")

@app.post("/generate/attestation")
async def generate_attestation(nom: str = Form(...), poste: str = Form(...), date_sortie: str = Form(...), adresse: str = Form(...)):
    context = {"nom": nom, "poste": poste, "date_sortie": date_sortie, "adresse": adresse}
    return render_pdf_from_template("attestation_template.html", context, "attestation")

@app.post("/generate/cdi")
async def generate_cdi(nom: str = Form(...), poste: str = Form(...), date_debut: str = Form(...), salaire: str = Form(...), adresse: str = Form(...)):
    context = {"nom": nom, "poste": poste, "date_debut": date_debut, "salaire": salaire, "adresse": adresse}
    return render_pdf_from_template("contrat_cdi.html", context, "contrat_cdi")

@app.post("/generate/cdd")
async def generate_cdd(nom: str = Form(...), poste: str = Form(...), date_debut: str = Form(...), duree: str = Form(...), salaire: str = Form(...), adresse: str = Form(...), periode_essai: str = Form(...)):
    context = {"nom": nom, "poste": poste, "date_debut": date_debut, "duree": duree, "salaire": salaire, "adresse": adresse, "periode_essai": periode_essai}
    return render_pdf_from_template("contrat_cdd.html", context, "contrat_cdd")

@app.post("/generate/stage")
async def generate_stage(nom: str = Form(...), poste: str = Form(...), date_debut: str = Form(...), date_fin: str = Form(...), gratification: str = Form(...), adresse: str = Form(...), tuteur: str = Form(...)):
    context = {"nom": nom, "poste": poste, "date_debut": date_debut, "date_fin": date_fin, "gratification": gratification, "adresse": adresse, "tuteur": tuteur}
    return render_pdf_from_template("contrat_stage.html", context, "contrat_stage")

@app.post("/generate/alternance")
async def generate_alternance(nom: str = Form(...), poste: str = Form(...), type_alternance: str = Form(...), date_debut: str = Form(...), duree: str = Form(...), ecole: str = Form(...), rythme: str = Form(...), salaire: str = Form(...), adresse: str = Form(...)):
    context = {"nom": nom, "poste": poste, "type_alternance": type_alternance, "date_debut": date_debut, "duree": duree, "ecole": ecole, "rythme": rythme, "salaire": salaire, "adresse": adresse}
    return render_pdf_from_template("contrat_alternance.html", context, "contrat_alternance")

@app.post("/generate/freelance")
async def generate_freelance(nom: str = Form(...), prestation: str = Form(...), date_debut: str = Form(...), date_fin: str = Form(...), montant: str = Form(...), adresse: str = Form(...)):
    context = {"nom": nom, "prestation": prestation, "date_debut": date_debut, "date_fin": date_fin, "montant": montant, "adresse": adresse}
    return render_pdf_from_template("contrat_freelance.html", context, "contrat_freelance")