"""Génère le site « Radar Bourse » : une page autonome (site/index.html) avec toutes les données."""
from __future__ import annotations

import json
import os
from datetime import datetime
from importlib import resources

import numpy as np
import pandas as pd

from . import backtest, config
from .scoring import propre

INDICES = [("^FCHI", "CAC 40"), ("SPY", "S&P 500"), ("QQQ", "Nasdaq 100"), ("BTC-USD", "Bitcoin")]


def _arrondi(v):
    if v is None or not np.isfinite(v):
        return None
    return float(f"{v:.6g}")


def _serie(d: pd.DataFrame, jours: int = 260) -> dict:
    d = d.iloc[-jours:]
    return {"t": [f"{x:%Y-%m-%d}" for x in d.index],
            **{k: [_arrondi(v) for v in d[col]] for k, col in
               (("o", "Open"), ("h", "High"), ("l", "Low"), ("c", "Close"),
                ("sma50", "sma50"), ("sma200", "sma200"))}}


def _cone(a, d: pd.DataFrame, rendement: float, horizon: int) -> dict | None:
    """Prévision : médiane (rendement historique pour cette proba) ± 1 écart-type de volatilité."""
    vol_an = a.perf.get("volatilité annuelle")
    if vol_an is None or not np.isfinite(vol_an) or not np.isfinite(rendement):
        return None
    crypto = a.marche == "crypto" or a.ticker.endswith("-USD")
    vol_j = vol_an / np.sqrt(365 if crypto else 252)
    dates = pd.date_range(d.index[-1], periods=horizon + 1, freq="D" if crypto else "B")
    k = np.arange(horizon + 1)
    mediane = a.prix * (1 + rendement) ** (k / horizon)
    ecart = np.exp(vol_j * np.sqrt(k))
    a.fourchette = (float(mediane[-1] / ecart[-1]), float(mediane[-1] * ecart[-1]))
    return {"t": [f"{x:%Y-%m-%d}" for x in dates],
            "mediane": [_arrondi(v) for v in mediane],
            "haut": [_arrondi(v) for v in mediane * ecart],
            "bas": [_arrondi(v) for v in mediane / ecart]}


def _backtest(ticker: str, d: pd.DataFrame) -> dict | None:
    jours_an = 365 if ticker.endswith("-USD") else 252
    dispo = len(d.dropna(subset=["sma200"])) / jours_an
    if dispo < 1:
        return None
    annees = min(3, int(dispo))
    try:
        r = backtest.lancer(ticker, d, 1000, annees)
    except Exception:
        return None
    return {"annees": annees, "bot": r.stats_strategie["rendement total"],
            "garder": r.stats_buy_hold["rendement total"],
            "trades": r.stats_strategie["nombre de trades"],
            "drawdown_bot": r.stats_strategie["pire baisse (drawdown)"]}


def construire(analyses, donnees, evaluation, suivi, indices_bruts, demo=False, actus_marche=None) -> dict:
    horizon = config.HORIZON_PREDICTION
    titres = []
    for a in sorted(analyses, key=lambda a: a.score, reverse=True):
        d = donnees[a.ticker]
        if evaluation is not None and a.proba_hausse == a.proba_hausse:
            a.rendement_attendu = evaluation.rendement_attendu(a.proba_hausse)
        rend = a.rendement_attendu if a.rendement_attendu == a.rendement_attendu else 0.0
        item = a.to_dict()
        item["cone"] = _cone(a, d, rend, horizon)
        item["fourchette"] = list(a.fourchette)
        item["serie"] = _serie(d)
        item["backtest"] = _backtest(a.ticker, d)
        item["prev_close"] = float(d["Close"].iloc[-2]) if len(d) > 1 else None
        item["spark"] = [_arrondi(v) for v in d["Close"].iloc[-63:]]
        # rendements quotidiens réels (3 dernières années) pour le simulateur Monte-Carlo du site
        lr = np.log(d["Close"]).diff().dropna().iloc[-750:]
        item["rendements"] = [round(float(v), 5) for v in lr if np.isfinite(v)]
        item["jours_an"] = 365 if a.ticker.endswith("-USD") else 252
        x = d.iloc[-1]
        item["au_dessus_200"] = bool(x["Close"] > x["sma200"]) if x["sma200"] == x["sma200"] else None
        titres.append(item)

    indices = []
    for t, nom in INDICES:
        d = indices_bruts.get(t)
        if d is None or len(d) < 2:
            continue
        c = d["Close"]
        indices.append({"ticker": t, "nom": nom, "prix": float(c.iloc[-1]),
                        "var_jour": float(c.iloc[-1] / c.iloc[-2] - 1),
                        "devise": "€" if t == "^FCHI" else "$",
                        "prev_close": float(c.iloc[-2]),
                        "spark": [_arrondi(v) for v in c.iloc[-60:]]})

    date_max = max(a.date_cours for a in analyses)
    return propre({
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "date_donnees": date_max, "demo": demo, "horizon": horizon,
        "modele": None if evaluation is None else evaluation.to_dict(),
        "suivi": suivi, "indices": indices, "titres": titres,
        "live": {"finnhub": config.FINNHUB_CLE},
        "actus_marche": actus_marche or [],
        "legal": {"editeur": config.EDITEUR, "contact": config.CONTACT},
    })


def ecrire(payload: dict, dossier: str = config.DOSSIER_SITE, pour_artifact: bool = False) -> str:
    gabarit = resources.files(__package__).joinpath("site_template.html").read_text(encoding="utf-8")
    donnees = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    donnees = donnees.replace("</", "<\\/")  # sécurité : pas de fermeture de balise dans le JSON
    page = gabarit.replace("/*__DATA__*/null", donnees)
    if not pour_artifact:
        page = ("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">"
                "</head><body>\n" + page + "\n</body></html>")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "index.html")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(dossier, "donnees.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    return chemin
