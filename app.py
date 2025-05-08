from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile

app = FastAPI()

# Configuration Jinja2
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
            <select name='type_contrat' required>
                <option value='cdi'>CDI / CDD</option>
                <option value='stage'>Stage</option>
                <option value='alternance'>Alternance</option>
                <option value='freelance'>Freelance</option>
            </select>
            <input name='nom' placeholder='Nom' required />
            <input name='poste' placeholder='Poste / Mission' required />
            <input name='date_debut' type='date' required />
            <input name='duree' placeholder='Durée (ex : 6 mois)' required />
            <input name='salaire' placeholder='Salaire ou gratification' required />
            <input name='adresse' placeholder='Adresse de l\'entreprise' required />
            <input name='centre' placeholder='Centre de formation / École (si besoin)' />
            <input name='tuteur' placeholder='Tuteur / Référent (si besoin)' />
            <input name='rythme' placeholder='Rythme (ex: 3j entreprise / 2j école)' />
            <button type='submit'>Générer le contrat</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    type_contrat: str = Form(...),
    nom: str = Form(...),
    poste: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...),
    centre: str = Form(""),
    tuteur: str = Form(""),
    rythme: str = Form("")
):
    template_file = {
        "cdi": "contrat_template.html",
        "stage": "contrat_stage.html",
        "alternance": "contrat_alternance.html",
        "freelance": "contrat_freelance.html"
    }.get(type_contrat, "contrat_template.html")

    template = env.get_template(template_file)
    html_content = template.render(
        nom=nom, poste=poste, type_contrat=type_contrat,
        date_debut=date_debut, duree=duree, salaire=salaire,
        adresse=adresse, centre=centre, tuteur=tuteur, rythme=rythme
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=html_content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"contrat_{type_contrat}_{nom}.pdf")