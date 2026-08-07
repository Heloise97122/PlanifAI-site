"""Contenu éditorial (rubrique Guides) — inbound / SEO.

Chaque guide vise une requête que tape la cible artisan sur Google. Les pages
sont rendues par un template unique et renvoient vers l'inscription.
"""

GUIDES = [
    {
        "slug": "facture-artisan",
        "titre": "Comment faire une facture d'artisan : mentions obligatoires et modèle",
        "meta": "Toutes les mentions obligatoires d'une facture d'artisan (auto-entrepreneur "
                "ou société), les erreurs à éviter, et comment créer une facture conforme en "
                "2 minutes.",
        "date": "2026-08-07",
        "intro": "Une facture d'artisan n'est pas un simple bout de papier : c'est un document "
                 "légal. S'il manque une mention obligatoire, votre facture peut être refusée "
                 "par le client, ou vous exposer à une amende. Voici, simplement, tout ce "
                 "qu'elle doit contenir.",
        "sections": [
            {"h2": "Les mentions obligatoires sur toute facture",
             "html": "<ul>"
                     "<li><strong>Votre identité</strong> : nom ou raison sociale, adresse, SIRET.</li>"
                     "<li><strong>Un numéro de facture unique</strong>, suivant une séquence continue (ex. FACT-2026-0001).</li>"
                     "<li><strong>La date</strong> d'émission de la facture.</li>"
                     "<li><strong>L'identité du client</strong> : nom et adresse.</li>"
                     "<li><strong>Le détail des prestations</strong> : désignation, quantité, prix unitaire.</li>"
                     "<li><strong>Les montants</strong> : total HT, taux et montant de TVA, total TTC.</li>"
                     "<li><strong>La date d'échéance</strong> du règlement et les pénalités de retard applicables.</li>"
                     "</ul>"},
            {"h2": "Le cas de l'auto-entrepreneur (franchise de TVA)",
             "html": "<p>La plupart des artisans auto-entrepreneurs sont en <strong>franchise en "
                     "base de TVA</strong> : ils ne facturent pas de TVA. Dans ce cas, la facture "
                     "doit porter la mention obligatoire <em>« TVA non applicable, art. 293 B du "
                     "CGI »</em>, et les montants sont indiqués en HT (= TTC, puisqu'il n'y a pas "
                     "de TVA). Oublier cette mention est l'erreur la plus fréquente.</p>"},
            {"h2": "Les erreurs qui coûtent cher",
             "html": "<ul>"
                     "<li>Numéros de facture qui se répètent ou sautent (la séquence doit être continue).</li>"
                     "<li>Oubli de la mention de franchise de TVA quand on est auto-entrepreneur.</li>"
                     "<li>Pas de date d'échéance ni de pénalités de retard (elles sont obligatoires entre professionnels).</li>"
                     "<li>Calcul de TVA à la main : source d'erreurs, surtout avec plusieurs taux.</li>"
                     "</ul>"},
        ],
    },
    {
        "slug": "devis-artisan",
        "titre": "Le devis d'artisan : ce qu'il doit contenir (et pourquoi il vous protège)",
        "meta": "Ce qu'un devis d'artisan doit obligatoirement mentionner, sa valeur juridique, "
                "sa durée de validité, et comment le transformer en facture sans tout resaisir.",
        "date": "2026-08-07",
        "intro": "Le devis, c'est votre meilleure protection : une fois signé par le client, il "
                 "vaut contrat. Il fixe le prix, le périmètre et les délais — et évite les "
                 "mauvaises surprises en fin de chantier. Encore faut-il qu'il soit complet.",
        "sections": [
            {"h2": "Ce qu'un devis doit contenir",
             "html": "<ul>"
                     "<li>Vos coordonnées et votre SIRET, celles du client.</li>"
                     "<li>La mention « Devis » et un numéro.</li>"
                     "<li>La date d'émission et la <strong>durée de validité</strong> (souvent 30 à 90 jours).</li>"
                     "<li>Le détail des prestations et des matériaux, avec quantités et prix unitaires.</li>"
                     "<li>Le total HT, la TVA (ou la mention de franchise), le total TTC.</li>"
                     "<li>Les conditions de paiement et, le cas échéant, l'acompte demandé.</li>"
                     "</ul>"},
            {"h2": "Pourquoi il vous protège",
             "html": "<p>Un devis signé « bon pour accord » engage le client sur le prix et le "
                     "périmètre. En cas de litige, c'est votre preuve. Sans devis, tout repose sur "
                     "la parole — et c'est vous qui perdez.</p>"},
            {"h2": "Du devis à la facture, sans tout resaisir",
             "html": "<p>Quand le client accepte, vous n'avez pas à tout retaper : un bon outil "
                     "transforme le devis en facture en un clic, en reprenant le client, les lignes "
                     "et les montants, avec un nouveau numéro et une échéance.</p>"},
        ],
    },
    {
        "slug": "franchise-tva-auto-entrepreneur",
        "titre": "Auto-entrepreneur : la franchise en base de TVA expliquée simplement",
        "meta": "Ce qu'est la franchise en base de TVA pour un auto-entrepreneur, la mention "
                "obligatoire à mettre sur vos factures, les seuils, et ce qui change quand vous "
                "les dépassez.",
        "date": "2026-08-07",
        "intro": "« Franchise en base de TVA » : derrière ce terme un peu barbare se cache une "
                 "bonne nouvelle pour la plupart des artisans qui débutent. On vous explique en "
                 "clair.",
        "sections": [
            {"h2": "C'est quoi, concrètement ?",
             "html": "<p>Être en franchise de TVA, c'est <strong>ne pas facturer de TVA</strong> à "
                     "vos clients (et ne pas la reverser à l'État). Vos prix sont nets. C'est le "
                     "régime par défaut de l'auto-entrepreneur tant que votre chiffre d'affaires "
                     "reste sous certains seuils.</p>"},
            {"h2": "La mention obligatoire sur vos factures",
             "html": "<p>Si vous êtes en franchise, vos factures et devis doivent porter la mention "
                     "<em>« TVA non applicable, art. 293 B du CGI »</em>. Sans elle, le document "
                     "n'est pas en règle. C'est un oubli très courant.</p>"},
            {"h2": "Les seuils à surveiller",
             "html": "<p>La franchise s'applique tant que votre chiffre d'affaires ne dépasse pas "
                     "les seuils en vigueur (ils évoluent régulièrement — vérifiez sur "
                     "service-public.fr). Au-delà, vous devez facturer la TVA. Un bon outil vous "
                     "prévient quand vous approchez du seuil, pour ne pas être pris au dépourvu.</p>"},
        ],
    },
]

GUIDES_PAR_SLUG = {g["slug"]: g for g in GUIDES}
