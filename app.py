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

# ===== ROUTES PAGES PRINCIPALES =====

@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/rh-ai", response_class=HTMLResponse)
async def page_rh_ai(request: Request):
    return templates.TemplateResponse("rh_ai_home.html", {"request": request})

# ===== ROUTES FORMULAIRES CONTRACTUELS =====

@app.get("/formulaire_rh", response_class=HTMLResponse)
async def formulaire_rh(request: Request):
    return templates.TemplateResponse("formulaire_rh.html", {"request": request})

@app.get("/freelance", response_class=HTMLResponse)
async def freelance(request: Request):
    return templates.TemplateResponse("contrat_freelance.html", {"request": request})

@app.get("/alternance", response_class=HTMLResponse)
async def alternance(request: Request):
    return templates.TemplateResponse("contrat_alternance.html", {"request": request})

@app.get("/stage", response_class=HTMLResponse)
async def stage(request: Request):
    return templates.TemplateResponse("contrat_stage.html", {"request": request})

@app.get("/attestation", response_class=HTMLResponse)
async def attestation(request: Request):
    return templates.TemplateResponse("attestation_template.html", {"request": request})

# ===== EXEMPLES OU MODELES DE CONTRATS =====

@app.get("/modele", response_class=HTMLResponse)
async def modele(request: Request):
    return templates.TemplateResponse("contrat_modele.html", {"request": request})

@app.get("/cdi", response_class=HTMLResponse)
async def cdi(request: Request):
    return templates.TemplateResponse("contrat_cdi.html", {"request": request})

@app.get("/cdd", response_class=HTMLResponse)
async def cdd(request: Request):
    return templates.TemplateResponse("contrat_cdd.html", {"request": request})

# ===== ROUTE PDF GÉNÉRIQUE =====

@app.post("/generate_pdf")
async def generate_pdf(content: str = Form(...), filename: str = Form("document.pdf")):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=content).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=filename)