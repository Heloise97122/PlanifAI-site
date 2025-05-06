import os
import shutil
import json
from jinja2 import Environment, FileSystemLoader, TemplateError

# Dossiers
output_dir = 'docs'
template_dir = 'templates'
data_file = 'data/agents.json'

try:
    # Nettoyage du dossier docs/
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(os.path.join(output_dir, 'agents'), exist_ok=True)

    # Environnement Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    index_template = env.get_template('index.html')
    agent_template = env.get_template('agent.html')

    # Chargement des données
    with open(data_file, 'r', encoding='utf-8') as f:
        agents = json.load(f)

    # Page d'accueil
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template.render(agents=agents))

    # Pages agents
    for agent in agents:
        agent_id = agent.get("id", "undefined")
        output_path = os.path.join(output_dir, 'agents', f"{agent_id}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(agent_template.render(agent=agent))

    print("✅ Site généré avec succès.")
except FileNotFoundError as e:
    print(f"❌ Fichier introuvable : {e.filename}")
except json.JSONDecodeError as e:
    print(f"❌ Erreur JSON : {e}")
except TemplateError as e:
    print(f"❌ Erreur dans les templates : {e}")
except Exception as e:
    print(f"❌ Erreur inattendue : {str(e)}")
# rebuild
