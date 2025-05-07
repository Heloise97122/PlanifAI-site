from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

# Configuration Jinja2
env = Environment(loader=FileSystemLoader("templates"))

@app.get("/", response_class=HTMLResponse)
async def formulaire():
    return """
    <form method="post" action="/generate">
        Nom: <input name="nom" /><br>
        Poste: <input name="poste" /><br>
        Type de contrat: <input name="type_contrat" /><br>
        Date de début: <input name="date_debut" type="date"/><br>
        Durée: <input name="duree" /><br>
        Salaire: <input name="salaire" /><br>
        Adresse: <input name="adresse" /><br><br>
        <button type="submit">Générer</button>
    </form>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    duree: str = Form(...),
    salaire: str = Form(...),
    adresse: str = Form(...)
):
    template = env.get_template("contrat_template.html")
    html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        duree=duree,
        salaire=salaire,
        adresse=adresse
    )
    return html
