from jinja2 import Environment, FileSystemLoader
import json
import os

# Préparation
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

# Charger les données des agents
with open('data/agents.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Rendu du HTML
output = template.render(agents=agents)

# Créer le dossier de sortie s’il n’existe pas
os.makedirs('docs', exist_ok=True)

# Sauvegarder le rendu dans docs/index.html
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(output)

print("✅ Site généré avec succès dans docs/index.html")
