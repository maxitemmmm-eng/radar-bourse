"""Suivi public du risque de forte chute (version 47).

C'est ce que les IA du radar prévoient le mieux sur des années jamais vues. Pour le prouver en conditions réelles,
au premier calcul complet de chaque mois, le radar enregistre publiquement :
  - les 10 titres auxquels il donne le PLUS de risque de perdre plus de 10 % ;
  - les 10 titres auxquels il en donne le MOINS.
Chaque choix est daté, enregistré avec le prix du jour, et n'est plus jamais modifié. Au bout de 20 séances
(la durée de la prévision), le site compte combien ont vraiment chuté de plus de 10 % dans chaque groupe.
Si l'IA a raison, le premier groupe doit chuter nettement plus souvent que le second. Les mois ratés restent affichés.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from . import config

FICHIER = "suivi_chute.json"
TAILLE = 10
SEUIL = -0.10


def _chemin():
    return os.path.join(config.DOSSIER_HISTORIQUE, FICHIER)


def lire() -> dict:
    try:
        with open(_chemin(), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"mois": {}}


def _ecrire(d: dict):
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    with open(_chemin(), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def _cours(df):
    if df is None or len(df) == 0:
        return None
    c = df["Close"].dropna()
    idx = pd.DatetimeIndex(c.index)
    c.index = (idx.tz_localize(None) if idx.tz is not None else idx).normalize()
    return c


def choisir(analyses, enregistrer: bool = True) -> dict | None:
    """Au premier calcul complet du mois : les 10 titres au plus fort et les 10 au plus faible risque de chute."""
    d = lire()
    mois = datetime.now().strftime("%Y-%m")
    if mois in d.get("mois", {}):
        return None
    cand = [a for a in analyses if a.marche != "tendances" and a.prix
            and isinstance(a.risque_prevu, dict) and a.risque_prevu.get("chute") is not None]
    if len(cand) < 3 * TAILLE:
        return None
    cand.sort(key=lambda a: -a.risque_prevu["chute"])
    fiche = lambda a: {"ticker": a.ticker, "nom": a.nom, "prix": float(a.prix), "risque": round(float(a.risque_prevu["chute"]), 4)}
    d.setdefault("mois", {})[mois] = {"date": datetime.now().strftime("%Y-%m-%d"),
                                      "risque_haut": [fiche(a) for a in cand[:TAILLE]],
                                      "risque_bas": [fiche(a) for a in cand[-TAILLE:]]}
    if enregistrer:
        _ecrire(d)
    return d["mois"][mois]


def _suivre(t, bruts, debut, horizon):
    c = _cours(bruts.get(t["ticker"]))
    if c is None:
        return None
    apres = c[c.index > debut]
    termine = len(apres) >= horizon
    if len(apres) == 0:
        return {**t, "perf": 0.0, "chute": False, "termine": False}
    p1 = float(apres.iloc[horizon - 1] if termine else apres.iloc[-1])
    r = p1 / t["prix"] - 1
    return {**t, "perf": r, "chute": bool(r < SEUIL), "termine": termine}


def bilan(bruts, horizon: int = config.HORIZON_PREDICTION) -> dict:
    d = lire()
    out = []
    for mois, s in sorted(d.get("mois", {}).items()):
        debut = pd.Timestamp(s["date"])
        groupes = {}
        for g in ("risque_haut", "risque_bas"):
            lignes = [x for t in s.get(g, []) if (x := _suivre(t, bruts, debut, horizon))]
            groupes[g] = lignes
        if not groupes["risque_haut"] or not groupes["risque_bas"]:
            continue
        tous = groupes["risque_haut"] + groupes["risque_bas"]
        out.append({"mois": mois, "date": s["date"], "termine": all(x["termine"] for x in tous),
                    **groupes,
                    "chutes_haut": int(sum(x["chute"] for x in groupes["risque_haut"])),
                    "chutes_bas": int(sum(x["chute"] for x in groupes["risque_bas"])),
                    "perf_haut": float(np.mean([x["perf"] for x in groupes["risque_haut"]])),
                    "perf_bas": float(np.mean([x["perf"] for x in groupes["risque_bas"]]))})
    finis = [m for m in out if m["termine"]]
    resume = None
    if finis:
        nh = sum(len(m["risque_haut"]) for m in finis)
        nb = sum(len(m["risque_bas"]) for m in finis)
        resume = {"nb_mois": len(finis), "chutes_haut": sum(m["chutes_haut"] for m in finis), "nb_haut": nh,
                  "chutes_bas": sum(m["chutes_bas"] for m in finis), "nb_bas": nb,
                  "mois_reussis": int(sum(m["chutes_haut"] > m["chutes_bas"] for m in finis)),
                  "mois_egaux": int(sum(m["chutes_haut"] == m["chutes_bas"] for m in finis))}
    return {"mois": out[::-1], "resume": resume}
