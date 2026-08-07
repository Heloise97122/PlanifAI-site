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
            {"h2": "Les seuils à surveiller en 2026",
             "html": "<p>En 2026, les seuils de franchise <strong>ne changent pas</strong> :</p>"
                     "<ul>"
                     "<li><strong>Prestations de services</strong> (la plupart des artisans) : "
                     "<strong>37 500 €</strong> de chiffre d'affaires (seuil majoré 41 250 €).</li>"
                     "<li><strong>Vente de marchandises</strong> : <strong>85 000 €</strong> "
                     "(seuil majoré 93 500 €).</li>"
                     "</ul>"
                     "<p>Bon à savoir : le projet de <strong>seuil unique à 25 000 €</strong>, "
                     "beaucoup commenté en 2025, a été <strong>abandonné</strong> — les seuils "
                     "ci-dessus restent la règle. Au-delà, vous devez facturer la TVA (les "
                     "modalités de bascule ont évolué récemment, vérifiez sur service-public.fr). "
                     "Un bon outil vous prévient quand vous approchez du seuil, pour ne pas être "
                     "pris au dépourvu.</p>"},
        ],
    },
    {
        "slug": "facturation-electronique-2026",
        "titre": "Facturation électronique obligatoire : ce qui change pour les artisans (2026-2027)",
        "meta": "La facturation électronique devient obligatoire en France : réception dès "
                "septembre 2026, émission en septembre 2027 pour les artisans et micro-"
                "entrepreneurs. Ce qu'il faut savoir et comment s'y préparer.",
        "date": "2026-08-07",
        "intro": "La France généralise la facturation électronique entre professionnels. Beaucoup "
                 "d'artisans pensent ne pas être concernés parce qu'ils ne facturent pas de TVA : "
                 "c'est faux. Voici le calendrier et ce qu'il faut anticiper, sans jargon.",
        "sections": [
            {"h2": "Êtes-vous concerné ? Oui, très probablement",
             "html": "<p>La réforme s'applique aux factures entre entreprises établies en France. "
                     "Elle concerne <strong>aussi les micro-entrepreneurs et les artisans en "
                     "franchise de TVA</strong> : même sans facturer de TVA, vous êtes un "
                     "assujetti, donc vous entrez dans le cadre. Personne n'y échappe.</p>"},
            {"h2": "Le calendrier à retenir",
             "html": "<ul>"
                     "<li><strong>1<sup>er</sup> septembre 2026</strong> : toutes les entreprises "
                     "doivent être capables de <strong>recevoir</strong> une facture électronique. "
                     "Les grandes entreprises et ETI doivent en plus commencer à en <strong>émettre</strong>.</li>"
                     "<li><strong>1<sup>er</sup> septembre 2027</strong> : c'est au tour des TPE, "
                     "PME et <strong>micro-entreprises</strong> de devoir <strong>émettre</strong> "
                     "leurs factures au format électronique.</li>"
                     "</ul>"
                     "<p>Autrement dit : dès septembre 2026, vous devez pouvoir <em>recevoir</em> "
                     "les factures électroniques de vos fournisseurs ; l'obligation d'en "
                     "<em>émettre</em> vous-même arrive un an plus tard.</p>"},
            {"h2": "Concrètement, comment ça marchera",
             "html": "<p>Une facture électronique n'est pas un simple PDF envoyé par e-mail. Elle "
                     "transite par une <strong>plateforme agréée</strong>, dans un format "
                     "structuré que l'administration peut lire. Le PDF classique par mail ne "
                     "suffira plus entre professionnels.</p>"},
            {"h2": "Comment vous y préparer dès maintenant",
             "html": "<p>Le plus simple : prenez dès aujourd'hui l'habitude de faire vos factures "
                     "dans un <strong>outil en ligne</strong> plutôt que sur Word ou Excel. Le "
                     "jour où l'obligation arrive, la bascule se fera sans douleur — vos documents "
                     "seront déjà numériques et bien structurés.</p>"
                     "<p><em>Les dates de cette réforme ont déjà été reportées par le passé : "
                     "vérifiez le calendrier en vigueur sur impots.gouv.fr.</em></p>"},
        ],
    },
    {
        "slug": "relancer-facture-impayee",
        "titre": "Facture impayée : comment relancer un client (méthode et modèle)",
        "meta": "Comment relancer efficacement une facture impayée : le bon timing, un modèle de "
                "relance prêt à envoyer, les pénalités de retard et l'indemnité forfaitaire de "
                "40 € prévue par la loi.",
        "date": "2026-08-07",
        "intro": "Faire le travail, c'est la moitié du chemin. Se faire payer, c'est l'autre "
                 "moitié. Une facture impayée n'est pas une fatalité : avec la bonne méthode, la "
                 "plupart se règlent d'une simple relance.",
        "sections": [
            {"h2": "Le bon timing",
             "html": "<p>Ne laissez pas traîner. Dès que l'échéance est dépassée de quelques "
                     "jours, envoyez une <strong>première relance courtoise</strong> : souvent, "
                     "c'est un simple oubli. Restez poli et factuel — le client d'aujourd'hui est "
                     "le chantier de demain.</p>"},
            {"h2": "Un modèle de relance",
             "html": "<p>« Bonjour, sauf erreur de notre part, la facture n° … d'un montant de … €, "
                     "échue le …, n'a pas encore été réglée. Nous vous remercions de bien vouloir "
                     "procéder au règlement. Si le paiement a déjà été effectué, merci de ne pas "
                     "tenir compte de ce message. »</p>"
                     "<p>Joignez toujours la facture en pièce jointe : le client a tout sous les "
                     "yeux, il n'a plus d'excuse.</p>"},
            {"h2": "Vos droits : pénalités et indemnité de 40 €",
             "html": "<p>Entre professionnels, tout retard de paiement ouvre droit à des "
                     "<strong>pénalités de retard</strong> et à une <strong>indemnité forfaitaire "
                     "de 40 €</strong> pour frais de recouvrement (article L441-10 du Code de "
                     "commerce). Mentionnez-les sur vos factures : c'est obligatoire, et c'est un "
                     "argument de poids dans une relance.</p>"},
            {"h2": "Quand ça bloque vraiment",
             "html": "<p>Si les relances amiables restent sans réponse, l'étape suivante est la "
                     "<strong>mise en demeure</strong> par lettre recommandée. Elle marque le "
                     "sérieux de votre démarche et constitue une preuve si vous devez aller plus "
                     "loin.</p>"},
        ],
    },
]

GUIDES_PAR_SLUG = {g["slug"]: g for g in GUIDES}
