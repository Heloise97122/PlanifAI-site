mfrom fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def formulaire():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>RH-AI | Générateur CDI</title>
    </head>
    <body>
        <h2>Contrat CDI</h2>
        <form method="post" action="/generate">
            <input name="entreprise" placeholder="Nom de l'entreprise" required />
            <input name="adresse" placeholder="Adresse" required />
            <input name="nom" placeholder="Nom du salarié" required />
            <input name="poste" placeholder="Poste" required />
            <input name="date_debut" type="date" required />
            <input name="salaire" placeholder="Salaire brut mensuel" required />
            <input name="periode_essai" placeholder="Durée période d’essai (ex: 2 mois)" required />
            <label>Renouvelable ?</label>
            <input type="radio" name="renouvelable" value="Oui" checked> Oui
            <input type="radio" name="renouvelable" value="Non"> Non
            <input name="lieu" placeholder="Lieu de signature" required />
            <input name="date_signature" type="date" required />
            <button type="submit">Générer le PDF</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    entreprise: str = Form(...),
    adresse: str = Form(...),
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    salaire: str = Form(...),
    periode_essai: str = Form(...),
    renouvelable: str = Form(...),
    lieu: str = Form(...),
    date_signature: str = Form(...)
):
    template = env.get_template("contrat_cdi.html")
    html_content = template.render(
        entreprise=entreprise,
        adresse=adresse,
        nom=nom,
        poste=poste,
        date_debut=date_debut,
        salaire=salaire,
        periode_essai=periode_essai,
        renouvelable=renouvelable,
        lieu=lieu,
        date_signature=date_signature
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"Contrat_CDI_{nom}.pdf")