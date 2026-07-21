"""Tests du module planning (calcul des jours et construction de la grille)."""

from planning import semaine_jours, construire_planning


def test_semaine_calee_sur_lundi():
    # 2026-07-22 est un mercredi -> le lundi de la semaine est le 2026-07-20
    jours = semaine_jours("2026-07-22")
    assert len(jours) == 7
    assert jours[0]["nom"] == "Lundi"
    assert jours[0]["date"] == "20/07"
    assert jours[6]["nom"] == "Dimanche"
    assert jours[6]["date"] == "26/07"


def test_date_invalide_ne_plante_pas():
    jours = semaine_jours("pas-une-date")
    assert len(jours) == 7
    assert jours[0]["nom"] == "Lundi"


def test_construire_grille():
    res = construire_planning([
        {"intervenant": "Alice", "jour": "0", "heure_debut": "08:00", "heure_fin": "12:00", "activite": "Chantier A"},
        {"intervenant": "Alice", "jour": "0", "heure_debut": "14:00", "heure_fin": "17:00", "activite": "Chantier B"},
        {"intervenant": "Bob", "jour": "2", "heure_debut": "09:00", "heure_fin": "", "activite": "Livraison"},
    ])
    assert res["intervenants"] == ["Alice", "Bob"]
    # Deux créneaux le même jour pour Alice
    assert res["grille"]["Alice"][0] == ["08:00-12:00 Chantier A", "14:00-17:00 Chantier B"]
    # Bob : heure de fin manquante -> seul le début affiché
    assert res["grille"]["Bob"][2] == ["09:00 Livraison"]


def test_creneaux_vides_et_jours_invalides_ignores():
    res = construire_planning([
        {"intervenant": "", "jour": "1", "heure_debut": "", "heure_fin": "", "activite": ""},
        {"intervenant": "Carla", "jour": "9", "heure_debut": "", "heure_fin": "", "activite": "Hors semaine"},
        {"intervenant": "Carla", "jour": "4", "heure_debut": "", "heure_fin": "", "activite": "RDV"},
    ])
    assert res["intervenants"] == ["Carla"]
    assert 9 not in res["grille"]["Carla"]
    assert res["grille"]["Carla"][4] == ["RDV"]


if __name__ == "__main__":
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
