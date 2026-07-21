"""Tests du calcul des factures / devis (billing.compute_invoice)."""

from decimal import Decimal

from billing import compute_invoice


def test_taux_unique():
    res = compute_invoice([
        {"description": "Prestation", "quantite": "2", "prix_unitaire": "100", "taux_tva": "20"},
    ])
    assert res["total_ht"] == Decimal("200.00")
    assert res["total_tva"] == Decimal("40.00")
    assert res["total_ttc"] == Decimal("240.00")


def test_multi_taux():
    res = compute_invoice([
        {"description": "Main d'oeuvre", "quantite": "1", "prix_unitaire": "200", "taux_tva": "20"},
        {"description": "Repas", "quantite": "1", "prix_unitaire": "50", "taux_tva": "10"},
    ])
    assert res["total_ht"] == Decimal("250.00")
    # 200*20% = 40 ; 50*10% = 5
    assert res["total_tva"] == Decimal("45.00")
    assert res["total_ttc"] == Decimal("295.00")
    # deux lignes de TVA, triées par taux croissant
    taux = [t["taux"] for t in res["tva_par_taux"]]
    assert taux == [Decimal("10"), Decimal("20")]


def test_format_francais_et_arrondi():
    # Saisie « 1 200,50 » avec quantité 3 -> 3601,50 HT
    res = compute_invoice([
        {"description": "Lot", "quantite": "3", "prix_unitaire": "1 200,50", "taux_tva": "20"},
    ])
    assert res["total_ht"] == Decimal("3601.50")
    assert res["total_tva"] == Decimal("720.30")
    assert res["total_ttc"] == Decimal("4321.80")


def test_ligne_vide_ignoree():
    res = compute_invoice([
        {"description": "Prestation", "quantite": "1", "prix_unitaire": "100", "taux_tva": "20"},
        {"description": "", "quantite": "", "prix_unitaire": "", "taux_tva": "20"},
    ])
    assert len(res["lignes"]) == 1
    assert res["total_ht"] == Decimal("100.00")


def test_taux_zero():
    res = compute_invoice([
        {"description": "Exonéré", "quantite": "1", "prix_unitaire": "100", "taux_tva": "0"},
    ])
    assert res["total_tva"] == Decimal("0.00")
    assert res["total_ttc"] == Decimal("100.00")


if __name__ == "__main__":
    # Permet de lancer les tests sans pytest : `python tests/test_billing.py`
    import sys
    import traceback

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"✅ {fn.__name__}")
        except AssertionError:
            failures += 1
            print(f"❌ {fn.__name__}")
            traceback.print_exc()
    sys.exit(1 if failures else 0)
