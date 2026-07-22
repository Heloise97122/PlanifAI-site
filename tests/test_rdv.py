"""Tests de la logique de prise de rendez-vous (rdv.py)."""

from datetime import date, datetime

import rdv


def test_slugify():
    assert rdv.slugify("Menuiserie Lefèvre") == "menuiserie-lefevre"
    assert rdv.slugify("  Élec & Cie !! ") == "elec-cie"
    assert rdv.slugify("") == "atelier"


def test_generer_creneaux_1h():
    assert rdv.generer_creneaux("08:00", "12:00", 60) == ["08:00", "09:00", "10:00", "11:00"]


def test_generer_creneaux_30min():
    assert rdv.generer_creneaux("09:00", "10:30", 30) == ["09:00", "09:30", "10:00"]


def test_generer_creneaux_incomplet_exclu():
    # 16:00->17:00 avec 1h : dernier créneau à 16:00 (finit à 17:00), pas au-delà
    assert rdv.generer_creneaux("16:00", "17:00", 60) == ["16:00"]
    assert rdv.generer_creneaux("16:00", "16:45", 60) == []


def test_parse_jours():
    assert rdv.parse_jours("0,1,2,3,4") == {0, 1, 2, 3, 4}
    assert rdv.parse_jours("5, 6") == {5, 6}
    assert rdv.parse_jours("") == set()
    assert rdv.parse_jours("9,abc,3") == {3}


def test_jours_reservables_filtre_jours_ouvres():
    # 2026-07-22 est un mercredi (weekday 2)
    maintenant = datetime(2026, 7, 22, 10, 0)
    jours = rdv.jours_reservables("0,1,2,3,4", horizon_jours=7, maintenant=maintenant)
    # sur 7 jours à partir du mercredi : mer, jeu, ven, (sam/dim exclus), lun, mar
    assert date(2026, 7, 22) in jours   # mercredi
    assert date(2026, 7, 25) not in jours  # samedi exclu
    assert date(2026, 7, 26) not in jours  # dimanche exclu
    assert date(2026, 7, 27) in jours   # lundi
    assert all(j.weekday() in {0, 1, 2, 3, 4} for j in jours)


def test_creneaux_libres_exclut_pris():
    jour = date(2026, 7, 30)  # jeudi, loin dans le futur relatif à maintenant
    maintenant = datetime(2026, 7, 22, 10, 0)
    libres = rdv.creneaux_libres(jour, "08:00", "11:00", 60, ["09:00"], maintenant=maintenant)
    assert libres == ["08:00", "10:00"]


def test_creneaux_libres_exclut_passe_aujourdhui():
    jour = date(2026, 7, 22)
    maintenant = datetime(2026, 7, 22, 9, 30)  # 9h30
    libres = rdv.creneaux_libres(jour, "08:00", "12:00", 60, [], maintenant=maintenant)
    # 08:00 et 09:00 sont passés (début <= maintenant), reste 10:00, 11:00
    assert libres == ["10:00", "11:00"]
