from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

# Configuration Jinja2
env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route pour la page d'accueil RH-AI
@app.get("/rh-home", response_class=HTMLResponse)
async def accueil_rh_ai():
    template = env.get_template("rh_ai_home.html")
    return HTMLResponse(content=template.render())