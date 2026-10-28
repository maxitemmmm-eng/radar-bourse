"""Données fondamentales des entreprises (Yahoo Finance) : PER, marges, dette, rentabilité…

Affichées dans l'onglet « Entreprise » de chaque action. Elles n'entrent PAS dans le modèle :
Yahoo ne donne que les valeurs actuelles, sans historique, donc impossible de mesurer leur effet.
"""
from __future__ import annotations

import time
import zlib
from datetime import datetime, timedelta, timezone

from . import data

CHAMPS = {
    # clé Yahoo : (libellé, format, explication simple)
    "marketCap": ("Capitalisation", "montant", "Valeur totale de l'entreprise en Bourse."),
    "trailingPE": ("PER (12 derniers mois)", "x", "Prix de l'action divisé par le bénéfice par action. Plus il est élevé, plus le marché paie cher chaque euro de bénéfice."),
    "forwardPE": ("PER attendu", "x", "Même calcul avec les bénéfices prévus par les analystes pour l'année qui vient."),
    "pegRatio": ("PEG", "x", "PER divisé par la croissance attendue. Autour de 1 : prix cohérent avec la croissance."),
    "revenueGrowth": ("Croissance du chiffre d'affaires", "pct", "Évolution des ventes sur un an."),
    "profitMargins": ("Marge nette", "pct", "Part du chiffre d'affaires qui reste en bénéfice."),
    "returnOnEquity": ("Rentabilité des capitaux (ROE)", "pct", "Bénéfice rapporté à l'argent des actionnaires. Au-dessus de 15 % : très rentable."),
    "debtToEquity": ("Dette / capitaux propres", "ratio", "Poids de la dette. Au-dessus de 200 % : entreprise très endettée."),
    "dividendYield": ("Rendement du dividende", "pct_brut", "Dividende annuel rapporté au prix de l'action."),
    "freeCashflow": ("Trésorerie disponible (free cash-flow)", "montant", "Argent réellement généré après les investissements."),
}


def _demo(ticker: str) -> dict:
    r = zlib.crc32(ticker.encode())
    jours = r % 60
    f = lambda a, b, k: a + (r >> k) % 1000 / 1000 * (b - a)
    return {"secteur": "Démo (données fictives)", "devise": data.devise(ticker), "valeurs": {
        "marketCap": f(5e9, 3e12, 1), "trailingPE": f(8, 45, 3), "forwardPE": f(8, 35, 5),
        "pegRatio": f(0.5, 3, 7), "revenueGrowth": f(-0.05, 0.3, 9), "profitMargins": f(0.02, 0.35, 11),
        "returnOnEquity": f(0.03, 0.45, 13), "debtToEquity": f(10, 250, 15), "dividendYield": f(0, 4, 17),
        "freeCashflow": f(1e8, 9e10, 19)},
        "resultats_le": (datetime.now() + timedelta(days=jours)).strftime("%Y-%m-%d")}


def recuperer(ticker: str, marche: str) -> dict | None:
    if ticker.endswith("-USD") or ticker.startswith("^") or marche == "etf":
        return None  # pas de fondamentaux pour les cryptos, indices et ETF
    if data.DEMO:
        return _demo(ticker)
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info or {}
    except Exception:
        return None
    if info.get("quoteType") not in (None, "EQUITY"):
        return None
    valeurs = {}
    for k in CHAMPS:
        v = info.get(k)
        if isinstance(v, (int, float)) and v == v:
            valeurs[k] = float(v)
    # Yahoo a changé le format du rendement du dividende (parfois 0,03, parfois 3) : on unifie en %
    if "dividendYield" in valeurs and valeurs["dividendYield"] < 0.5:
        valeurs["dividendYield"] *= 100
    resultats = None
    for cle in ("earningsTimestamp", "earningsTimestampStart"):
        ts = info.get(cle)
        if isinstance(ts, (int, float)) and ts > 0:
            resultats = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
            break
    if not valeurs and not resultats:
        return None
    return {"secteur": info.get("sector") or "", "devise": "€" if info.get("currency") == "EUR" else "$",
            "valeurs": valeurs, "resultats_le": resultats}


ELARGISSEMENT_RESULTATS = 1.3   # règle de prudence fixe (non mesurée) : +30 % d'amplitude


def elargir_fourchette(a) -> None:
    """Une publication de résultats avant l'échéance peut faire bouger le cours bien plus que
    d'habitude : on élargit les scénarios bas et haut autour du scénario central."""
    if len(a.quantiles or ()) != 3 or a.fourchette_elargie:
        return
    b, m, h = a.quantiles
    k = ELARGISSEMENT_RESULTATS
    a.quantiles = (m - (m - b) * k, m, m + (h - m) * k)
    if len(a.extremes or ()) == 2:
        eb, eh = a.extremes
        a.extremes = (m - (m - eb) * k, m + (eh - m) * k)
    a.fourchette_elargie = True


def enrichir(analyses) -> None:
    aujourd_hui = datetime.now().date()
    for a in analyses:
        appel = []
        if data.DEMO:
            a.fondamentaux = recuperer(a.ticker, a.marche)
        else:   # les fondamentaux changent peu : une fois par jour suffit (cache de 20 h)
            a.fondamentaux = data.cache_json("fondamentaux", a.ticker, 20,
                                             lambda: appel.append(1) or recuperer(a.ticker, a.marche))
        date = (a.fondamentaux or {}).get("resultats_le")
        if date:
            ecart = (datetime.strptime(date, "%Y-%m-%d").date() - aujourd_hui).days
            if 0 <= ecart <= 30:
                a.resultats_le = date
                quand = "aujourd'hui" if ecart == 0 else "demain" if ecart == 1 else f"dans {ecart} jours"
                a.alertes.insert(0, f"📅 Résultats trimestriels {quand} ({datetime.strptime(date, '%Y-%m-%d'):%d/%m}) : "
                                    "le cours peut bouger fortement, même au-delà de la fourchette prévue")
                if ecart <= 28:   # publication avant l'échéance de la prévision (~20 séances)
                    elargir_fourchette(a)
        if appel and a.fondamentaux is not None:
            time.sleep(0.2)


def libelles() -> dict:
    return {k: {"libelle": l, "format": f, "aide": aide} for k, (l, f, aide) in CHAMPS.items()}
