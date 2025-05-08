from fastapi import FastAPI, Form
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
async def home():
    return """
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
        <title>RH-AI | Générateur de contrat</title>
    </head>
    <body>
        <h2>Générateur de contrat RH</h2>
        <form method='post' action='/generate'>
            <label>Nom :</label>
            <input name='nom' required />
            <label>Poste :</label>
            <input name='poste' required />
            <label>Type de contrat :</label>
            <select name='type_contrat'>
                <option>CDI</option>
                <option>CDD</option>
                <option>Stage</option>
                <option>Alternance</option>
            </select>
            <label>Date de début :</label>
            <input name='date_debut' type='date' required />
            <label>Durée :</label>
            <input name='duree' required />
            <label>Salaire mensuel brut :</label>
            <input name='salaire' required />
            <label>Adresse de l'entreprise :</label>
            <input name='adresse' required />
            <label>Durée période d'essai :</label>
            <input name='periode_essai' required />
            <label>Renouvelable :</label>
            <select name='renouvelable'>
                <option>Oui</option>
                <option>Non</option>
            </select>
            <label>URL du logo (optionnel) :</label>
            <input name='logo_url' />
            <label>Type spécial :</label>
            <select name='contrat_special'>
                <option>Aucun</option>
                <option>Stage</option>
                <option>Alternance</option>
            </select>
            <label>Établissement de formation :</label>
            <input name='ecole' />
            <label>Rythme :</label>
            <input name='rythme' />
            <label>Gratification (stage) :</label>
            <input name='gratification' />
            <label>Tuteur :</label>
            <input name='tuteur' />
            <button type='submit'>Générer le contrat</button>
        </form>
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
    periode_essai: str = Form(...),
    renouvelable: str = Form(...),
    logo_url: str = Form(None),
    contrat_special: str = Form(None),
    ecole: str = Form(None),
    rythme: str = Form(None),
    gratification: str = Form(None),
    tuteur: str = Form(None)
):
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
        logo_url=logo_url,
        contrat_special=contrat_special,
        ecole=ecole,
        rythme=rythme,
        gratification=gratification,
        tuteur=tuteur
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf")