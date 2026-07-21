"""Construction d'un planning hebdomadaire à partir d'une liste de créneaux.

Logique isolée (dates + regroupement) pour être testable sans le serveur web.
"""

from datetime import date, timedelta

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def semaine_jours(date_str):
    """Retourne les 7 jours de la semaine (lundi -> dimanche) contenant `date_str`.

    `date_str` au format 'YYYY-MM-DD' ; toute date de la semaine convient, la
    semaine est calée sur le lundi. Retourne une liste de dicts :
    [{'index': 0, 'nom': 'Lundi', 'date': '21/07'}, ...].
    """
    try:
        d = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        d = date.today()
    lundi = d - timedelta(days=d.weekday())
    return [
        {
            "index": i,
            "nom": JOURS[i],
            "date": (lundi + timedelta(days=i)).strftime("%d/%m"),
        }
        for i in range(7)
    ]


def construire_planning(creneaux):
    """Regroupe des créneaux en une grille intervenant x jour.

    `creneaux` : itérable de dicts contenant `intervenant`, `jour` (index 0-6,
    lundi = 0), `heure_debut`, `heure_fin`, `activite`.
    Les créneaux sans intervenant ni activité, ou au jour invalide, sont ignorés.

    Retourne :
        {
          "intervenants": [noms dans l'ordre d'apparition],
          "grille": { intervenant: { index_jour: ["08:00-12:00 Chantier A", ...] } },
        }
    """
    intervenants = []
    grille = {}

    for creneau in creneaux:
        nom = str(creneau.get("intervenant", "")).strip()
        activite = str(creneau.get("activite", "")).strip()
        heure_debut = str(creneau.get("heure_debut", "")).strip()
        heure_fin = str(creneau.get("heure_fin", "")).strip()

        try:
            jour = int(creneau.get("jour"))
        except (ValueError, TypeError):
            continue

        if not nom and not activite:
            continue
        if not 0 <= jour <= 6:
            continue

        if nom not in grille:
            grille[nom] = {}
            intervenants.append(nom)

        if heure_debut and heure_fin:
            heures = f"{heure_debut}-{heure_fin} "
        elif heure_debut:
            heures = f"{heure_debut} "
        else:
            heures = ""
        libelle = (heures + activite).strip()

        grille[nom].setdefault(jour, []).append(libelle)

    return {"intervenants": intervenants, "grille": grille}
