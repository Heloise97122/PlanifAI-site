"""Tests des seuils micro-entreprise (seuils.py)."""

import seuils


def _jauge(res, cle):
    return next(j for j in res["jauges"] if j["cle"] == cle)


def test_niveaux_services_ok():
    res = seuils.evaluer("services", 10000)
    assert res["niveau_global"] == "ok"
    assert _jauge(res, "tva")["niveau"] == "ok"
    assert _jauge(res, "micro")["niveau"] == "ok"


def test_tva_proche():
    # 37 500 * 0.85 = 31 875 -> proche (80-100 %) pour la TVA, ok pour le micro
    res = seuils.evaluer("services", 32000)
    assert _jauge(res, "tva")["niveau"] == "proche"
    assert _jauge(res, "micro")["niveau"] == "ok"
    assert res["niveau_global"] == "proche"


def test_tva_depassee():
    res = seuils.evaluer("services", 40000)
    assert _jauge(res, "tva")["niveau"] == "depasse"
    assert res["niveau_global"] == "depasse"


def test_micro_depasse():
    res = seuils.evaluer("services", 80000)
    assert _jauge(res, "micro")["niveau"] == "depasse"
    assert _jauge(res, "tva")["niveau"] == "depasse"


def test_barre_bornee_a_100():
    res = seuils.evaluer("services", 200000)
    for j in res["jauges"]:
        assert j["pct_barre"] <= 100
        assert j["pct"] > 100


def test_vente_seuils_plus_hauts():
    # 40 000 dépasse la TVA en services mais pas en vente (85 000)
    res = seuils.evaluer("vente", 40000)
    assert _jauge(res, "tva")["niveau"] == "ok"
    assert res["activite_label"] == "Vente de marchandises"


def test_activite_inconnue_defaut_services():
    res = seuils.evaluer("n_importe_quoi", 40000)
    assert _jauge(res, "tva")["seuil"] == seuils.ACTIVITES["services"]["tva_franchise"]
