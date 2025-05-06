from jinja2 import Environment, FileSystemLoader
import json
import os

# Initialisation de Jinja2
env = Environment(loader=FileSystemLoader('templates'))
index_template = env.get_template('index.html')
agent_template = env.get_template('agent.html')

# Charger les données des agents
with open('data/agents.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Générer la page d'accueil
os.makedirs('docs', exist_ok=True)
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(index_template.render(agents=agents))

# Générer une page pour chaque agent
agents_dir = 'docs/agents'
os.makedirs(agents_dir, exist_ok=True)

for agent in agents:
    agent_filename = f"{agent['id']}.html"
    with open(os.path.join(agents_dir, agent_filename), 'w', encoding='utf-8') as f:
        f.write(agent_template.render(agent=agent))

print("✅ Pages générées avec succès : index + agents individuels.")
