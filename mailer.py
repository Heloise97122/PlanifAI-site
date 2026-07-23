"""Envoi d'e-mails transactionnels via Brevo (ex-Sendinblue).

Utilise l'API HTTP de Brevo avec la librairie standard (urllib) pour ne pas
ajouter de dépendance. La configuration se fait par variables d'environnement :

  BREVO_API_KEY   : clé API Brevo (obligatoire pour envoyer).
  MAIL_FROM       : adresse expéditeur validée dans Brevo (ex. ton Gmail).
  MAIL_FROM_NAME  : nom affiché de l'expéditeur (défaut : "PlanifAI").

Si BREVO_API_KEY n'est pas défini, l'envoi est simplement ignoré (retourne False)
et le message est journalisé — pratique en local sans casser l'application.
"""

import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("planifai.mailer")

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def email_configure() -> bool:
    """Vrai si l'envoi d'e-mails est configuré (clé API présente)."""
    return bool(os.environ.get("BREVO_API_KEY"))


def envoyer_email(destinataire: str, sujet: str, html: str,
                  nom_expediteur: str = None, repondre_a: str = None) -> bool:
    """Envoie un e-mail HTML. Retourne True si Brevo a accepté l'envoi.

    `nom_expediteur` : nom affiché de l'expéditeur (par défaut MAIL_FROM_NAME).
        Permet d'envoyer « au nom de » un artisan sans changer l'adresse validée.
    `repondre_a` : adresse de réponse (Reply-To), pour que les réponses aillent
        à l'artisan et non à l'adresse technique de la plateforme.
    """
    api_key = os.environ.get("BREVO_API_KEY")
    if not api_key:
        logger.warning("BREVO_API_KEY absent — e-mail non envoyé à %s (sujet: %s)", destinataire, sujet)
        return False

    expediteur = os.environ.get("MAIL_FROM", "")
    nom = nom_expediteur or os.environ.get("MAIL_FROM_NAME", "PlanifAI")
    if not expediteur:
        logger.error("MAIL_FROM absent — impossible d'envoyer l'e-mail.")
        return False

    payload = {
        "sender": {"name": nom, "email": expediteur},
        "to": [{"email": destinataire}],
        "subject": sujet,
        "htmlContent": html,
    }
    if repondre_a:
        payload["replyTo"] = {"email": repondre_a}
    corps = json.dumps(payload).encode("utf-8")

    requete = urllib.request.Request(
        BREVO_URL,
        data=corps,
        headers={
            "api-key": api_key,
            "content-type": "application/json",
            "accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=15) as reponse:
            return 200 <= reponse.status < 300
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        logger.error("Brevo a refusé l'envoi (%s) : %s", e.code, detail)
        return False
    except Exception as e:  # réseau, timeout…
        logger.error("Échec de l'envoi de l'e-mail : %s: %s", type(e).__name__, e)
        return False
