from jinja2 import Environment, FileSystemLoader
import json
import os

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')

with open('data/agents.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

output = template.render(agents=agents)

with open('site/index.html', 'w', encoding='utf-8') as f:
    f.write(output)

print("Site généré avec succès dans le dossier 'site'")