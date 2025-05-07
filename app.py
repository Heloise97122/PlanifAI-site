from datetime import date

@app.get("/attestation", response_class=HTMLResponse)
async def formulaire_attestation():
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
        <title>Attestation RH</title>
    </head>
    <body>
        <form method="post" action="/attestation">
            <h2>Générateur d'attestation employeur</h2>
            <input name="nom" placeholder="Nom de l'employé" />
            <input name="poste" placeholder="Poste occupé" />
            <input name="type_contrat" placeholder="Type de contrat (CDI, CDD...)" />
            <input name="date_debut" type="date" placeholder="Date de début" />
            <input name="entreprise" placeholder="Nom de l'entreprise" />
            <input name="adresse" placeholder="Adresse de l'entreprise" />
            <button type="submit">Générer l’attestation</button>
        </form>
    </body>
    </html>
    """

@app.post("/attestation")
async def generate_attestation(
    nom: str = Form(...),
    poste: str = Form(...),
    type_contrat: str = Form(...),
    date_debut: str = Form(...),
    entreprise: str = Form(...),
    adresse: str = Form(...)
):
    template = env.get_template("attestation_template.html")
    rendered_html = template.render(
        nom=nom,
        poste=poste,
        type_contrat=type_contrat,
        date_debut=date_debut,
        entreprise=entreprise,
        adresse=adresse,
        date_du_jour=date.today().strftime("%Y-%m-%d")
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        HTML(string=rendered_html).write_pdf(tmp_pdf.name)
        return FileResponse(tmp_pdf.name, filename=f"attestation_{nom}.pdf", media_type='application/pdf')