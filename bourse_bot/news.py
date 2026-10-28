"""Actualités par titre et tonalité (positive / négative).

Sources : Finnhub (actions US, si une clé est configurée) puis Yahoo Finance pour le reste.
Seuls les titres d'articles et leurs liens sont conservés.

La tonalité est affichée à titre d'information : elle n'entre PAS dans la probabilité du modèle,
car on n'a pas d'historique d'actus pour mesurer si elle améliore vraiment les prévisions.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from . import config, data

JOURS = 7          # on garde les actus des 7 derniers jours
MAX_PAR_TITRE = 6

# Vocabulaire financier ajouté à VADER (anglais) et petit lexique français
FINANCE_EN = {
    "beat": 1.6, "beats": 1.6, "surge": 2.0, "surges": 2.0, "soar": 2.2, "soars": 2.2, "rally": 1.6,
    "rallies": 1.6, "upgrade": 1.8, "upgraded": 1.8, "outperform": 1.5, "record": 1.0, "jumps": 1.6,
    "jump": 1.4, "gains": 1.2, "bullish": 1.8, "raises": 1.0, "buyback": 1.0, "growth": 1.0,
    "miss": -1.6, "misses": -1.6, "plunge": -2.3, "plunges": -2.3, "tumble": -2.0, "tumbles": -2.0,
    "downgrade": -1.8, "downgraded": -1.8, "lawsuit": -1.6, "probe": -1.4, "fraud": -2.5,
    "bearish": -1.8, "slump": -1.8, "slumps": -1.8, "layoffs": -1.5, "recall": -1.3, "cuts": -1.0,
    "warning": -1.4, "sinks": -1.8, "falls": -1.2, "drops": -1.2, "loss": -1.3, "losses": -1.3,
    "bankruptcy": -2.8, "investigation": -1.4, "fine": -0.8, "fined": -1.6, "selloff": -1.8,
}
FINANCE_FR = {
    "hausse": 1, "bondit": 2, "bond": 1.5, "flambe": 2, "record": 1, "benefice": 1, "benefices": 1,
    "croissance": 1, "releve": 1, "relevement": 1, "depasse": 1.5, "progresse": 1, "grimpe": 1.5,
    "optimiste": 1, "rachat": 0.8, "succes": 1.5, "acquisition": 0.5, "rebond": 1, "rebondit": 1,
    "baisse": -1, "chute": -2, "chutent": -2, "recul": -1, "recule": -1, "perte": -1.5,
    "pertes": -1.5, "avertissement": -1.5, "plonge": -2, "degringole": -2, "abaisse": -1.2,
    "enquete": -1.2, "amende": -1.5, "licenciements": -1.5, "faillite": -2.5, "deception": -1.5,
    "decoit": -1.5, "inquietude": -1, "sanction": -1.2, "greve": -1, "rappel": -0.8, "proces": -1.2,
}
MOTS_FR = {"le", "la", "les", "des", "du", "une", "et", "pour", "sur", "avec", "dans", "est", "au", "aux"}

_vader = None


def _analyseur():
    global _vader
    if _vader is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _vader = SentimentIntensityAnalyzer()
            _vader.lexicon.update(FINANCE_EN)
        except Exception:
            _vader = False
    return _vader


def _sans_accents(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def tonalite(titre: str) -> float:
    """Score de -1 (très négatif) à +1 (très positif)."""
    mots = re.findall(r"[a-zà-ÿ]+", titre.lower())
    if sum(m in MOTS_FR for m in mots) >= 2 or re.search(r"[éèàùç]", titre.lower()):
        brut = sum(FINANCE_FR.get(_sans_accents(m), 0) for m in mots)
        return max(-1.0, min(1.0, brut / 4))
    v = _analyseur()
    if v:
        return float(v.polarity_scores(titre)["compound"])
    brut = sum(FINANCE_EN.get(m, 0) for m in mots)
    return max(-1.0, min(1.0, brut / 3))


def _get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "radar-bourse"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def _finnhub(ticker: str) -> list[dict]:
    cle = config.FINNHUB_CLE
    if not cle or not re.fullmatch(r"[A-Z]{1,5}", ticker):
        return []
    fin = datetime.now(timezone.utc).date()
    debut = fin - timedelta(days=JOURS)
    q = urllib.parse.urlencode({"symbol": ticker, "from": debut, "to": fin, "token": cle})
    try:
        items = _get_json(f"https://finnhub.io/api/v1/company-news?{q}")
    except Exception:
        return []
    return [{"titre": it.get("headline", ""), "source": it.get("source", ""),
             "date": datetime.fromtimestamp(it.get("datetime", 0), timezone.utc).isoformat(timespec="minutes"),
             "url": it.get("url", "")} for it in items if it.get("headline")]


def _yahoo(ticker: str) -> list[dict]:
    try:
        import yfinance as yf
        brut = yf.Ticker(ticker).news or []
    except Exception:
        return []
    out = []
    for it in brut:
        c = it.get("content", it)  # le format de Yahoo a changé en 2025 : on gère les deux
        titre = c.get("title", "")
        date = c.get("pubDate") or c.get("displayTime")
        if not date and it.get("providerPublishTime"):
            date = datetime.fromtimestamp(it["providerPublishTime"], timezone.utc).isoformat()
        source = (c.get("provider") or {}).get("displayName") if isinstance(c.get("provider"), dict) else it.get("publisher", "")
        url = ((c.get("canonicalUrl") or c.get("clickThroughUrl") or {}).get("url")
               if isinstance(c.get("canonicalUrl") or c.get("clickThroughUrl"), dict) else it.get("link", ""))
        if titre:
            out.append({"titre": titre, "source": source or "", "date": date or "", "url": url or ""})
    return out


def actus(ticker: str) -> list[dict]:
    if data.DEMO:
        return _demo(ticker)
    items = _finnhub(ticker) or _yahoo(ticker)
    limite = datetime.now(timezone.utc) - timedelta(days=JOURS)
    propres, vus = [], set()
    for it in items:
        try:
            d = datetime.fromisoformat(it["date"].replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        cle = it["titre"].lower()[:80]
        if d < limite or cle in vus or not it["url"].startswith("http"):
            continue
        vus.add(cle)
        it["date"] = d.isoformat(timespec="minutes")
        it["tonalite"] = round(tonalite(it["titre"]), 3)
        propres.append(it)
    propres.sort(key=lambda x: x["date"], reverse=True)
    return propres[:MAX_PAR_TITRE]


def tonalite_moyenne(items: list[dict]) -> float:
    """Moyenne pondérée : les actus récentes comptent davantage."""
    if not items:
        return float("nan")
    maintenant = datetime.now(timezone.utc)
    tot = poids = 0.0
    for it in items:
        age_j = (maintenant - datetime.fromisoformat(it["date"])).total_seconds() / 86400
        w = 0.5 ** (age_j / 2)  # demi-vie de 2 jours
        tot += w * it["tonalite"]
        poids += w
    return tot / poids if poids else float("nan")


def enrichir(analyses, progres=None) -> list[dict]:
    """Ajoute actus + tonalité à chaque analyse. Renvoie les actus générales du marché."""
    for a in analyses:
        a.actus = actus(a.ticker)
        a.tonalite = tonalite_moyenne(a.actus)
        if progres:
            progres()
        if not data.DEMO:
            time.sleep(0.25)  # politesse envers les API gratuites
    marche = []
    for t in ("SPY", "^FCHI", "BTC-USD"):
        marche += actus(t)[:4]
    marche.sort(key=lambda x: x["date"], reverse=True)
    return marche[:8]


def _demo(ticker: str) -> list[dict]:
    import zlib
    r = zlib.crc32(ticker.encode()) % 3
    base = datetime.now(timezone.utc)
    exemples = [
        ("Exemple : résultats trimestriels supérieurs aux attentes", 0.6),
        ("Exemple : un analyste abaisse son objectif de cours", -0.5),
        ("Exemple : la société annonce un nouveau produit", 0.3),
    ]
    return [{"titre": f"[Démo] {t}", "source": "Données fictives", "url": "https://example.com",
             "date": (base - timedelta(hours=10 * i + r)).isoformat(timespec="minutes"),
             "tonalite": s} for i, (t, s) in enumerate(exemples[r:] + exemples[:r])]


def garde_fou(analyses) -> None:
    """L'actu n'entre pas dans la probabilité (pas d'historique pour mesurer son effet), mais elle
    sert de garde-fou : quand les articles récents contredisent nettement l'avis de l'IA, on le
    signale, et un signal fort est suspendu par prudence. Cela ne peut que rendre le radar plus prudent."""
    for a in analyses:
        ton, n = a.tonalite, len(a.actus or [])
        if ton != ton or n < 3 or a.proba_hausse != a.proba_hausse:
            continue
        a.actu_contredit = bool((a.proba_hausse >= 0.55 and ton <= -0.25) or (a.proba_hausse <= 0.45 and ton >= 0.25))
        if a.actu_contredit:
            a.alertes.insert(0, "📰 Les actualités récentes vont dans le sens contraire de l'IA : prudence")
        if a.signal_fort and ton <= -0.25:
            a.signal_fort = False
            a.alertes.insert(0, "Signal fort suspendu : actualités récentes nettement négatives")
