"""Reconstruction des documents (contexte PDF + résumé pour historique/rappels).

Sert à la fois à la génération initiale et à la régénération d'un PDF déjà
sauvegardé (à partir des champs bruts stockés en base).
"""

import billing

CONTRAT_TYPES = {"cdi", "cdd", "alternance", "stage", "freelance", "attestation"}

PREFIX = {
    "cdi": "contrat_cdi", "cdd": "contrat_cdd", "alternance": "contrat_alternance",
    "stage": "convention_stage", "freelance": "contrat_freelance", "attestation": "attestation",
    "facture": "facture", "devis": "devis",
}

TITRES = {
    "cdi": "Contrat CDI", "cdd": "Contrat CDD", "alternance": "Contrat alternance",
    "stage": "Convention de stage", "freelance": "Contrat freelance",
    "attestation": "Attestation employeur", "facture": "Facture", "devis": "Devis",
}

FIN_LABELS = {
    "cdd": "Fin de CDD", "alternance": "Fin d'alternance",
    "stage": "Fin de stage", "freelance": "Fin de mission",
}


def _lignes(f):
    d = f.get("description", []) or []
    q = f.get("quantite", []) or []
    p = f.get("prix_unitaire", []) or []
    t = f.get("taux_tva", []) or []
    n = max(len(d), len(q), len(p), len(t))
    return [{
        "description": d[i] if i < len(d) else "",
        "quantite": q[i] if i < len(q) else "0",
        "prix_unitaire": p[i] if i < len(p) else "0",
        "taux_tva": t[i] if i < len(t) else "0",
    } for i in range(n)]


def build_context(type_, f):
    """Retourne (template, prefixe_fichier, contexte) pour render_pdf."""
    if type_ in CONTRAT_TYPES:
        return f"pdf_{type_}.html", PREFIX[type_], dict(f)

    if type_ in ("facture", "devis"):
        calc = billing.compute_invoice(_lignes(f))
        is_facture = type_ == "facture"
        context = {
            "nom": f.get("numero", ""),  # sert au nom de fichier
            "type_document": "Facture" if is_facture else "Devis",
            "numero": f.get("numero", ""), "date": f.get("date", ""),
            "date_limite": (f.get("echeance") if is_facture else f.get("validite")) or "",
            "date_limite_label": "Échéance" if is_facture else "Validité",
            "entreprise": f.get("entreprise", ""), "adresse": f.get("adresse", ""),
            "siret": f.get("siret", ""), "email": f.get("email", ""),
            "client_nom": f.get("client_nom", ""), "client_adresse": f.get("client_adresse", ""),
            "calc": calc, "logo_url": f.get("logo_url") or None,
        }
        return "pdf_facturation.html", PREFIX[type_], context

    raise ValueError(f"type de document inconnu : {type_}")


def summarize(type_, f):
    """Résumé pour la fiche Document : (titre, tiers, numero, montant, statut,
    echeance_iso, echeance_label)."""
    if type_ in ("facture", "devis"):
        calc = billing.compute_invoice(_lignes(f))
        montant = float(calc["total_ttc"])
        numero = f.get("numero", "")
        titre = f"{TITRES[type_]} {numero}".strip()
        tiers = f.get("client_nom", "")
        if type_ == "facture" and f.get("echeance"):
            return titre, tiers, numero, montant, "attente", f["echeance"], "Facture à encaisser"
        if type_ == "devis" and f.get("validite"):
            return titre, tiers, numero, montant, "devis", f["validite"], "Devis à relancer"
        return titre, tiers, numero, montant, ("attente" if type_ == "facture" else "devis"), None, None

    # Contrats
    nom = f.get("nom", "")
    titre = f"{TITRES.get(type_, type_)} — {nom}".strip(" —")
    ech, label = None, None
    if type_ in FIN_LABELS and f.get("date_fin"):
        ech, label = f["date_fin"], FIN_LABELS[type_]
    return titre, nom, None, None, "", ech, label
