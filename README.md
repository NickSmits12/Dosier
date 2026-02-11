# SamenGezond voedingslogboek (starter)

Eenvoudige website voor een beginnend diëtist:
- Team/"wie zijn wij" hoofdpagina
- Voedingsformulier met verplichte naam + leeftijd
- Optioneel gewicht
- Dropdown 1 t/m 10 maaltijden
- Dynamische velden per maaltijd
- Lokale opslag in SQLite
- Overzicht voor cliënt en adminpagina voor database-weergave

## Benodigdheden
- Python 3.10+
- `pip`

## Installatie
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Starten
```bash
python app.py
```
Open daarna: `http://127.0.0.1:5000`.

## Pagina's
- `/` — hoofdpagina
- `/formulier` — invulformulier
- `/mijn-gegevens` — opgeslagen inzendingen bekijken
- `/admin/database?token=admin-demo-token` — admin-overzicht

> Belangrijk: zet in productie een sterk geheim token/secret en gebruik HTTPS.
