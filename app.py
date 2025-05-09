from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import os

app = FastAPI()

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env = Environment(loader=FileSystemLoader("templates"))

# ROUTE: Accueil RH-AI
@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# ROUTE: Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ROUTE: Formulaire contrat RH
@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

# ROUTE: Freelance
@app.get("/freelance", response_class=HTMLResponse)
async def freelance(request: Request):
    return templates.TemplateResponse("formulaire_freelance.html", {"request": request})

# ROUTE: Alternance
@app.get("/alternance", response_class=HTMLResponse)
async def alternance(request: Request):
    return templates.TemplateResponse("formulaire_alternance.html", {"request": request})

# ROUTE: Stage
@app.get("/stage", response_class=HTMLResponse)
async def stage(request: Request):
    return templates.TemplateResponse("formulaire_stage.html", {"request": request})

# ROUTE: Attestation
@app.get("/attestation", response_class=HTMLResponse)
async def attestation(request: Request):
    return templates.TemplateResponse("formulaire_attestation.html", {"request": request})

# EXEMPLE PDF (serve le fichier depuis /static)
@app.get("/exemple-pdf", response_class=FileResponse)
async def exemple_pdf():
    return FileResponse("static/exemple_rh.pdf", media_type="application/pdf", filename="exemple_rh.pdf")