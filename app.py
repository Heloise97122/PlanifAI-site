from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Configuration des chemins
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# PAGE D'ACCUEIL RH-AI
@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# TABLEAU DE BORD
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# FORMULAIRES
@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

@app.get("/freelance", response_class=HTMLResponse)
async def formulaire_freelance(request: Request):
    return templates.TemplateResponse("formulaire_freelance.html", {"request": request})

@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation(request: Request):
    return templates.TemplateResponse("formulaire_attestation.html", {"request": request})

@app.get("/alternance", response_class=HTMLResponse)
async def formulaire_alternance(request: Request):
    return templates.TemplateResponse("formulaire_alternance.html", {"request": request})

@app.get("/stage", response_class=HTMLResponse)
async def formulaire_stage(request: Request):
    return templates.TemplateResponse("formulaire_stage.html", {"request": request})

# Tu peux ajouter ici toutes les routes POST pour générer les PDF pour chaque type de contrat si ce n'est pas déjà fait.