"""Seuils du régime micro-entreprise et alertes de chiffre d'affaires.

⚠️ Les montants ci-dessous sont des seuils de RÉFÉRENCE. Ils évoluent (la
franchise de TVA en particulier a fait l'objet de réformes récentes). Ils sont
regroupés ici pour être mis à jour facilement en un seul endroit.

Sources de référence : plafonds du régime micro (période 2023-2025) et seuils
de franchise en base de TVA. À vérifier chaque année sur service-public.fr /
impots.gouv.fr.
"""

ANNEE_REFERENCE = 2025

ACTIVITES = {
    "services": {
        "label": "Prestations de services / artisanat",
        "tva_franchise": 37500,    # seuil de franchise en base de TVA
        "tva_majore": 41250,       # seuil majoré (tolérance)
        "micro_plafond": 77700,    # plafond du régime micro
    },
    "vente": {
        "label": "Vente de marchandises",
        "tva_franchise": 85000,
        "tva_majore": 93500,
        "micro_plafond": 188700,
    },
}

DEFAUT = "services"


def config_activite(activite: str) -> dict:
    return ACTIVITES.get(activite, ACTIVITES[DEFAUT])


def _niveau(ca: float, seuil: int):
    """Retourne (niveau, pourcentage) : ok < 80 %, proche 80-100 %, depasse >= 100 %."""
    if seuil <= 0:
        return "ok", 0.0
    pct = ca / seuil * 100.0
    if pct >= 100:
        return "depasse", pct
    if pct >= 80:
        return "proche", pct
    return "ok", pct


def evaluer(activite: str, ca: float) -> dict:
    """Évalue le CA encaissé face aux deux seuils clés (franchise TVA, plafond micro).

    Retourne un dict prêt à afficher, avec pour chaque jauge : libellé, seuil,
    pourcentage (borné à 100 pour la barre), niveau, et un message.
    """
    conf = config_activite(activite)
    jauges = []

    n_tva, pct_tva = _niveau(ca, conf["tva_franchise"])
    jauges.append({
        "cle": "tva", "label": "Franchise de TVA", "seuil": conf["tva_franchise"],
        "seuil_majore": conf["tva_majore"], "pct": pct_tva, "pct_barre": min(pct_tva, 100),
        "niveau": n_tva,
        "message": {
            "ok": "Vous restez en franchise de TVA (pas de TVA à facturer).",
            "proche": "Vous approchez du seuil : au-delà, vous devrez facturer la TVA.",
            "depasse": "Seuil dépassé : vous devez normalement facturer la TVA. Vérifiez votre situation.",
        }[n_tva],
    })

    n_micro, pct_micro = _niveau(ca, conf["micro_plafond"])
    jauges.append({
        "cle": "micro", "label": "Plafond du régime micro", "seuil": conf["micro_plafond"],
        "seuil_majore": None, "pct": pct_micro, "pct_barre": min(pct_micro, 100),
        "niveau": n_micro,
        "message": {
            "ok": "Vous êtes dans les limites du régime micro-entreprise.",
            "proche": "Vous approchez du plafond du régime micro.",
            "depasse": "Plafond dépassé : au-delà 2 ans de suite, vous sortez du régime micro.",
        }[n_micro],
    })

    niveau_global = "ok"
    if any(j["niveau"] == "depasse" for j in jauges):
        niveau_global = "depasse"
    elif any(j["niveau"] == "proche" for j in jauges):
        niveau_global = "proche"

    return {
        "activite_label": conf["label"], "annee_reference": ANNEE_REFERENCE,
        "ca": ca, "jauges": jauges, "niveau_global": niveau_global,
    }
