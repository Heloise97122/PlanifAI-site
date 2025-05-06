import os
import json
from jinja2 import Environment, FileSystemLoader, TemplateError

# Chemins
output_dir = 'docs'
agents_dir = os.path.join(output_dir, 'agents')
template_dir = 'templates'
data_file = 'data/agents.json'

try:
    # Création des dossiers s'ils n'existent pas
    os.makedirs(agents_dir, exist_ok=True)

    # Environnement Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    index_template = env.get_template('index.html')
    agent_template = env.get_template('agent.html')

    # Chargement des données agents
    with open(data_file, 'r', encoding='utf-8') as f:
        agents = json.load(f)

    # Génération de index.html
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_template.render(agents=agents))
    print(f"✅ Fichier généré : {index_path}")

    # Génération des pages agents
    for agent in agents:
        agent_id = agent.get("id", "undefined")
        output_path = os.path.join(agents_dir, f"{agent_id}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(agent_template.render(agent=agent))
        print(f"✅ Agent généré : {output_path}")

except FileNotFoundError as e:
    print(f"❌ Fichier introuvable : {e.filename}")
except json.JSONDecodeError as e:
    print(f"❌ Erreur JSON : {e}")
except TemplateError as e:
    print(f"❌ Erreur dans les templates : {e}")
except Exception as e:
    print(f"❌ Erreur inattendue : {str(e)}")
    # reg