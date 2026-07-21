"""Calcul des totaux d'une facture ou d'un devis (HT, TVA, TTC).

La logique est isolée ici pour être testable indépendamment du serveur web.
Les montants sont manipulés en Decimal et arrondis au centime (ROUND_HALF_UP).
"""

from decimal import Decimal, ROUND_HALF_UP


def _dec(value) -> Decimal:
    """Convertit une saisie utilisateur en Decimal.

    Tolère les formats français (« 1 200,50 ») et les champs vides.
    """
    s = str(value).strip().replace(" ", "").replace(" ", "").replace(",", ".")
    if s == "":
        s = "0"
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def _money(value: Decimal) -> Decimal:
    """Arrondit au centime."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_invoice(lignes):
    """Calcule les totaux d'une facture / d'un devis.

    `lignes` : itérable de dicts contenant au moins les clés
    `description`, `quantite`, `prix_unitaire`, `taux_tva`.
    Les lignes sans description ni montant sont ignorées.

    Retourne un dict :
        {
          "lignes": [{description, quantite, prix_unitaire, taux_tva, montant_ht}, ...],
          "total_ht": Decimal,
          "tva_par_taux": [{taux, base_ht, montant_tva}, ...],  # trié par taux
          "total_tva": Decimal,
          "total_ttc": Decimal,
        }
    """
    computed = []
    total_ht = Decimal("0")
    base_par_taux = {}

    for ligne in lignes:
        description = str(ligne.get("description", "")).strip()
        quantite = _dec(ligne.get("quantite"))
        prix_unitaire = _dec(ligne.get("prix_unitaire"))
        taux = _dec(ligne.get("taux_tva"))

        # Ignore les lignes totalement vides
        if not description and quantite == 0 and prix_unitaire == 0:
            continue

        montant_ht = _money(quantite * prix_unitaire)
        total_ht += montant_ht
        base_par_taux[taux] = base_par_taux.get(taux, Decimal("0")) + montant_ht

        computed.append({
            "description": description,
            "quantite": quantite,
            "prix_unitaire": _money(prix_unitaire),
            "taux_tva": taux,
            "montant_ht": montant_ht,
        })

    tva_par_taux = []
    total_tva = Decimal("0")
    for taux in sorted(base_par_taux):
        base = base_par_taux[taux]
        montant_tva = _money(base * taux / Decimal("100"))
        total_tva += montant_tva
        tva_par_taux.append({
            "taux": taux,
            "base_ht": _money(base),
            "montant_tva": montant_tva,
        })

    total_ht = _money(total_ht)
    total_tva = _money(total_tva)
    total_ttc = _money(total_ht + total_tva)

    return {
        "lignes": computed,
        "total_ht": total_ht,
        "tva_par_taux": tva_par_taux,
        "total_tva": total_tva,
        "total_ttc": total_ttc,
    }
