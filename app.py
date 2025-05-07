from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration de Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Serveur de fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def formulaire():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>RH-AI | Générateur de contrat</title>
    </head>
    <body>
        <div class="container">
            <h2>Générateur de contrat RH</h2>
            <form method="post" action="/generate">
                <input name="nom" placeholder="Nom" required />
                <input name="poste" placeholder="Poste" required />
                <input name="type_contrat" placeholder="Type de contrat" required />
                <input name="date_debut" type="date" required />
                <input name="duree" placeholder="Durée" required />
                <input name="salaire" placeholder="Salaire mensuel brut (€)" required />
                <input name="adresse" placeholder="Adresse de l'entreprise" required />
                <input name="logo_url" placeholder="URL du logo (optionnel)" />
                <button type="submit">Générer le contrat</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    logo_url: str = Form(None)  # facultatif
):
    template = env.get_template("contrat_template.html")
    rendered_html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        duree=duree,
        salaire=salaire,
        adresse=adresse,
        logo_url=logo_url
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=rendered_html).write_pdf(tmp_pdf.name)
        pdf_path = tmp_pdf.name

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"contrat_{nom}.pdf"
    )