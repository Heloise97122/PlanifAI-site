import os
import shutil
import json
from jinja2 import Environment, FileSystemLoader

# Nettoyer le dossier docs/
output_dir = 'docs'
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)
os.makedirs(os.path.join(output_dir, 'agents'), exist_ok=True)

# Chargement des templates
env = Environment(loader=FileSystemLoader('templates'))
index_template = env.get_template('index.html')
agent_template = env.get_template('agent.html')

# Chargement des données
with open('data/agents.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Générer la page d'accueil
with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_template.render(agents=agents))

# Générer chaque page agent
for agent in agents:
    agent_file = os.path.join(output_dir, 'agents', f"{agent['id']}.html")
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(agent_template.render(agent=agent))

print("✅ Site regénéré : base.html, index.html, pages agents.")