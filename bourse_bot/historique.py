"""Suivi en conditions réelles : chaque prédiction est enregistrée, puis vérifiée une fois
l'horizon écoulé. C'est la seule preuve qui compte vraiment (aucun recalcul possible après coup).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import config

FICHIER = os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv")
COLS = ["date", "ticker", "prix", "proba", "score", "signal"]


def enregistrer(analyses) -> None:
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    nouvelles = pd.DataFrame([{
        "date": a.date_cours, "ticker": a.ticker, "prix": a.prix,
        "proba": a.proba_hausse, "score": a.score, "signal": a.signal} for a in analyses])
    if os.path.exists(FICHIER):
        anciennes = pd.read_csv(FICHIER)
        tout = pd.concat([anciennes, nouvelles])
    else:
        tout = nouvelles
    # une seule prédiction par titre et par jour de cotation (on garde la plus récente)
    tout = tout.drop_duplicates(subset=["date", "ticker"], keep="last")
    tout[COLS].to_csv(FICHIER, index=False)


def bilan(donnees: dict[str, pd.DataFrame], horizon: int = config.HORIZON_PREDICTION) -> dict:
    """Compare les anciennes prédictions à ce qui s'est réellement passé."""
    vide = {"nb_verifiees": 0, "nb_en_attente": 0, "precision": None,
            "precision_signaux_achat": None, "dernieres": []}
    if not os.path.exists(FICHIER):
        return vide
    hist = pd.read_csv(FICHIER)
    if hist.empty:
        return vide

    verifiees, attente = [], 0
    for _, r in hist.iterrows():
        d = donnees.get(r["ticker"])
        if d is None:
            continue
        apres = d.index[d.index > pd.Timestamp(r["date"])]
        if len(apres) < horizon:
            attente += 1
            continue
        prix_fin = float(d.loc[apres[horizon - 1], "Close"])
        reel = prix_fin / r["prix"] - 1
        prevu_hausse = (r["proba"] > 0.5) if not np.isnan(r["proba"]) else r["score"] >= 60
        verifiees.append({"date": r["date"], "ticker": r["ticker"], "proba": r["proba"],
                          "signal": r["signal"], "rendement_reel": reel,
                          "juste": bool(prevu_hausse == (reel > 0))})
    if not verifiees:
        return {**vide, "nb_en_attente": attente}
    v = pd.DataFrame(verifiees)
    achats = v[v["signal"].str.startswith("ACHAT")]
    return {
        "nb_verifiees": len(v), "nb_en_attente": attente,
        "precision": float(v["juste"].mean()),
        "precision_signaux_achat": float((achats["rendement_reel"] > 0).mean()) if len(achats) else None,
        "dernieres": v.sort_values("date", ascending=False).head(15).to_dict("records"),
    }
