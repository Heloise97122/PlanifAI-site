from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Jinja2 template configuration
env = Environment(loader=FileSystemLoader("templates"))

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# === PAGE D’ACCUEIL RH ===
@app.get("/rh-home", response_class=HTMLResponse)
async def rh_home():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(template.render())

# === FORMULAIRE CONTRAT RH GÉNÉRAL ===
@app.get("/formulaire-rh", response_class=HTMLResponse)
async def formulaire_rh():
    template = env.get_template("formulaire_rh.html")
    return HTMLResponse(template.render())

# === FORMULAIRE CONTRAT FREELANCE ===
@app.get("/contrat-freelance", response_class=HTMLResponse)
async def contrat_freelance_form():
    template = env.get_template("contrat_freelance.html")
    return HTMLResponse(template.render())

# === FORMULAIRE ATTESTATION EMPLOYEUR ===
@app.get("/attestation", response_class=HTMLResponse)
async def attestation_form():
    template = env.get_template("attestation_template.html")
    return HTMLResponse(template.render())

# === FORMULAIRE ALTERNANCE ===
@app.get("/contrat-alternance", response_class=HTMLResponse)
async def contrat_alternance_form():
    template = env.get_template("contrat_alternance.html")
    return HTMLResponse(template.render())

# === FORMULAIRE STAGE ===
@app.get("/contrat-stage", response_class=HTMLResponse)
async def contrat_stage_form():
    template = env.get_template("contrat_stage.html")
    return HTMLResponse(template.render())