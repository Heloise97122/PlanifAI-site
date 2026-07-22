"""Logique de la prise de rendez-vous en ligne.

Fonctions pures (sans base de données) pour :
- fabriquer un identifiant d'URL (slug) à partir d'un nom d'entreprise ;
- calculer les créneaux horaires d'une journée ;
- lister les jours réservables sur un horizon donné ;
- déterminer les créneaux encore libres d'une journée.

Le paramètre `maintenant` est injectable pour faciliter les tests.
"""

import re
import unicodedata
from datetime import date, datetime, timedelta

JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
JOURS_FR_COURT = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


def slugify(texte: str) -> str:
    """Transforme un nom en identifiant d'URL : « Menuiserie Lefèvre » -> « menuiserie-lefevre »."""
    texte = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode("ascii")
    texte = texte.lower()
    texte = re.sub(r"[^a-z0-9]+", "-", texte).strip("-")
    return texte or "atelier"


def _hhmm_en_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _minutes_en_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def generer_creneaux(heure_debut: str, heure_fin: str, duree_min: int):
    """Liste des créneaux « HH:MM » entre début et fin, par pas de `duree_min`.

    Un créneau n'est proposé que s'il tient entièrement avant l'heure de fin.
    Ex. 08:00 -> 17:00, 60 min => 08:00, 09:00, ..., 16:00.
    """
    if duree_min <= 0:
        return []
    debut = _hhmm_en_minutes(heure_debut)
    fin = _hhmm_en_minutes(heure_fin)
    creneaux = []
    t = debut
    while t + duree_min <= fin:
        creneaux.append(_minutes_en_hhmm(t))
        t += duree_min
    return creneaux


def parse_jours(jours_str: str):
    """« 0,1,2,3,4 » -> {0,1,2,3,4} (0 = lundi, 6 = dimanche)."""
    jours = set()
    for part in (jours_str or "").split(","):
        part = part.strip()
        if part.isdigit():
            n = int(part)
            if 0 <= n <= 6:
                jours.add(n)
    return jours


def jours_reservables(jours_str: str, horizon_jours: int = 14, maintenant: datetime = None):
    """Liste des dates réservables (jours ouvrés du pro) dans l'horizon, à partir d'aujourd'hui."""
    maintenant = maintenant or datetime.now()
    ouverts = parse_jours(jours_str)
    aujourdhui = maintenant.date()
    resultat = []
    for i in range(horizon_jours):
        j = aujourdhui + timedelta(days=i)
        if j.weekday() in ouverts:
            resultat.append(j)
    return resultat


def creneaux_libres(jour: date, heure_debut: str, heure_fin: str, duree_min: int,
                    heures_prises, maintenant: datetime = None):
    """Créneaux « HH:MM » encore disponibles pour une journée.

    Exclut les créneaux déjà réservés (`heures_prises`) et, si `jour` est
    aujourd'hui, les créneaux déjà passés.
    """
    maintenant = maintenant or datetime.now()
    prises = set(heures_prises or [])
    tous = generer_creneaux(heure_debut, heure_fin, duree_min)
    libres = []
    for c in tous:
        if c in prises:
            continue
        if jour == maintenant.date():
            debut_creneau = datetime.combine(jour, datetime.min.time()) + timedelta(minutes=_hhmm_en_minutes(c))
            if debut_creneau <= maintenant:
                continue
        libres.append(c)
    return libres


def libelle_jour(jour: date) -> str:
    """« lundi 5 août »."""
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
    return f"{JOURS_FR[jour.weekday()]} {jour.day} {mois[jour.month - 1]}"
