from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Dossiers
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/rh-ai", response_class=HTMLResponse)
async def show_form():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(template.render())

@app.post("/generate", response_class=FileResponse)
async def generate_contract(
    type_contrat: str = Form(...),
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    periode_essai: str = Form(None),
    renouvelable: str = Form(None),
    gratification: str = Form(None),
    tuteur: str = Form(None),
    convention: str = Form(None),
    alternance_type: str = Form(None),
    alternance_duree: str = Form(None),
    centre_formation: str = Form(None),
    rythme: str = Form(None),
    logo_url: str = Form(None)
):
    # Choix du template selon le contrat
    template_map = {
        "CDI": "contrat_cdi.html",
        "CDD": "contrat_cdd.html",
        "Freelance": "contrat_freelance.html",
        "Stage": "contrat_stage.html",
        "Alternance": "contrat_alternance.html"
    }

    template_name = template_map.get(type_contrat, "contrat_cdi.html")
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
        gratification=gratification,
        tuteur=tuteur,
        convention=convention,
        alternance_type=alternance_type,
        alternance_duree=alternance_duree,
        centre_formation=centre_formation,
        rythme=rythme,
        logo_url=logo_url
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf")