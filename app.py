from fastapi import FastAPI, Request, Form
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

# DASHBOARD
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# PAGE D'ACCUEIL RH-AI
@app.get("/rh-ai-home", response_class=HTMLResponse)
async def rh_ai_home(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# CONTRAT RH
@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

# CONTRAT FREELANCE
@app.get("/freelance", response_class=HTMLResponse)
async def freelance(request: Request):
    return templates.TemplateResponse("formulaire_freelance.html", {"request": request})

# ATTESTATION EMPLOYEUR
@app.get("/attestation", response_class=HTMLResponse)
async def attestation(request: Request):
    return templates.TemplateResponse("formulaire_attestation.html", {"request": request})

# ALTERNANCE
@app.get("/alternance", response_class=HTMLResponse)
async def alternance(request: Request):
    return templates.TemplateResponse("formulaire_alternance.html", {"request": request})

# STAGE
@app.get("/stage", response_class=HTMLResponse)
async def stage(request: Request):
    return templates.TemplateResponse("formulaire_stage.html", {"request": request})