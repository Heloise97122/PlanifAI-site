from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile

app = FastAPI()
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/rh-ai", response_class=HTMLResponse)
async def rh_ai_home():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(content=template.render())

@app.get("/formulaire", response_class=HTMLResponse)
async def formulaire():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(content=template.render())

@app.post("/generate", response_class=FileResponse)
async def generate_contract(
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
    nom_template = f"contrat_{type_contrat.lower()}.html"
    try:
        template = env.get_template(nom_template)
    except:
        template = env.get_template("contrat_modele.html")

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

@app.post("/attestation", response_class=FileResponse)
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)
):
    template = env.get_template("attestation.html")
    html_content = template.render(
        nom=nom,
        poste=poste,
        date_debut=date_debut,
        adresse=adresse,
        logo_url=logo_url
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf")