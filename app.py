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
async def rh_home():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(content=template.render())

@app.get("/formulaire", response_class=HTMLResponse)
async def formulaire():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(content=template.render())

@app.post("/generate-contract", response_class=HTMLResponse)
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
    temps_travail: str = Form(...),
    remboursement_transport: str = Form(...),
    droits_conges: str = Form(...),
    logo_url: str = Form(None),
    gratification: str = Form(None),
    tuteur: str = Form(None),
    ecole: str = Form(None),
    rythme: str = Form(None)
):
    if type_contrat.lower() == "cdi":
        template_file = "contrat_cdi.html"
    elif type_contrat.lower() == "cdd":
        template_file = "contrat_cdd.html"
    elif type_contrat.lower() == "stage":
        template_file = "contrat_stage.html"
    elif type_contrat.lower() == "alternance":
        template_file = "contrat_alternance.html"
    elif type_contrat.lower() == "freelance":
        template_file = "contrat_freelance.html"
    else:
        template_file = "contrat_modele.html"

    template = env.get_template(template_file)
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
        temps_travail=temps_travail,
        remboursement_transport=remboursement_transport,
        droits_conges=droits_conges,
        logo_url=logo_url,
        gratification=gratification,
        tuteur=tuteur,
        ecole=ecole,
        rythme=rythme
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf")

@app.post("/generate-attestation", response_class=HTMLResponse)
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    adresse: str = Form(...)
):
    template = env.get_template("attestation_template.html")
    html_content = template.render(
        nom=nom,
        poste=poste,
        date_debut=date_debut,
        adresse=adresse
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf")