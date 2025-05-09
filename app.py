from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile

app = FastAPI()

env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/alternance", response_class=HTMLResponse)
async def formulaire_alternance():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>RH-AI | Contrat d'alternance</title>
    </head>
    <body>
        <h2>Contrat d'alternance</h2>
        <form method="post" action="/generate-alternance">
            <input name="nom" placeholder="Nom de l'alternant" required />
            <input name="poste" placeholder="Poste" required />
            <input name="type_alternance" placeholder="Type (apprentissage / pro)" required />
            <input name="date_debut" type="date" placeholder="Date de début" required />
            <input name="duree" placeholder="Durée (ex: 12 mois)" required />
            <input name="salaire" placeholder="Salaire" required />
            <input name="adresse" placeholder="Adresse de l'entreprise" required />
            <input name="entreprise" placeholder="Nom de l'entreprise" required />
            <input name="ecole" placeholder="Nom de l'école ou centre de formation" required />
            <input name="rythme" placeholder="Rythme (ex: 3j