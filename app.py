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
async def formulaire():
    return """
    <html>
    <head>
        <link rel='stylesheet' href='/static/style.css'>
        <title>RH-AI | Générateur de contrat</title>
    </head>
    <body>
        <h2>Générateur de contrat RH</h2>
        <form method='post' action='/generate'>
            <input name='nom' placeholder="Nom du salarié" required />
            <input name='poste' placeholder="Poste" required />
            <input name='type_contrat' placeholder="Type de contrat (CDI, CDD...)" required />
            <input name='date_debut' type='date' placeholder="Date de début" required />
            <input name='duree' placeholder="Durée (en mois)" required />
            <input name='salaire' placeholder="Salaire mensuel brut (€)" required />
            <input name='adresse' placeholder="Adresse de l'entreprise" required />
            <input name='periode_essai' placeholder="Durée période d'essai (ex: 1 mois)" required />
            <label>Renouvelable ?</label>
            <input type='radio' name='renouvelable' value='Oui' checked> Oui
            <input type='radio' name='renouvelable' value='Non'> Non
            <input name='temps_travail' placeholder="Temps de travail (ex: 35h/semaine)" required />
            <input name='remboursement_transport' placeholder="Remboursement transport (ex: 50%)" required />
            <input name='conges' placeholder="Droits aux congés (ex: 2,5 jours/mois)" required />
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
    temps_travail: str = Form(...),
    remboursement_transport: str = Form(...),
    conges: str = Form(...)
):
    template = env.get_template("contrat_template.html")
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
        conges=conges
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{nom}.pdf")