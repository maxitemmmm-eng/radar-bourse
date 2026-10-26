"""Le portefeuille public « mieux que le marché » (version 33).

C'est ce que l'IA prévoit le mieux après l'agitation : quels titres feront mieux que leur indice.
Au début de chaque mois, le radar choisit les 10 actions auxquelles l'IA donne le plus de chances de battre
leur indice (CAC 40, Euro Stoxx 50 ou S&P 500). Le choix est enregistré avec le prix du jour et n'est plus
jamais modifié. Ensuite, le site affiche tout seul comment chaque sélection s'en sort face à son indice.
C'est un suivi public et honnête, pas un conseil : les mois ratés restent affichés.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from . import config

FICHIER = "portefeuille_public.json"
TAILLE = 10
DUREE_JOURS = 31   # chaque sélection est suivie un mois


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


def _dernier_prix(df, jusqua=None):
    if df is None or len(df) == 0:
        return None
    c = df["Close"]
    if jusqua is not None:
        idx = pd.DatetimeIndex(c.index)
        idx = idx.tz_localize(None) if idx.tz is not None else idx
        c = c[idx <= pd.Timestamp(jusqua)]
    c = c.dropna()
    return float(c.iloc[-1]) if len(c) else None


def choisir(analyses, bruts, enregistrer: bool = True) -> dict | None:
    """Au premier calcul complet du mois : enregistre les 10 actions les mieux placées face à leur indice."""
    d = lire()
    mois = datetime.now().strftime("%Y-%m")
    if mois in d.get("mois", {}):
        return None
    candidats = [a for a in analyses
                 if a.marche in ("fr", "eu", "us") and a.proba_marche == a.proba_marche and a.proba_marche is not None
                 and getattr(a, "qualite_ok", True) is not False and a.indice_ref]
    candidats.sort(key=lambda a: -a.proba_marche)
    sel = []
    for a in candidats[:TAILLE]:
        pi = _dernier_prix(bruts.get(a.indice_ref))
        if not a.prix or not pi:
            continue
        sel.append({"ticker": a.ticker, "nom": a.nom, "prix": float(a.prix), "indice": a.indice_ref,
                    "prix_indice": pi, "proba_marche": round(float(a.proba_marche), 4)})
    if len(sel) < 5:
        return None
    d.setdefault("mois", {})[mois] = {"date": datetime.now().strftime("%Y-%m-%d"), "titres": sel}
    if enregistrer:
        _ecrire(d)
    return d["mois"][mois]


def bilan(bruts) -> dict:
    """Comment chaque sélection s'en sort face à son indice (jusqu'à aujourd'hui, ou au bout d'un mois)."""
    d = lire()
    out = []
    for mois, s in sorted(d.get("mois", {}).items()):
        debut = pd.Timestamp(s["date"])
        fin = debut + pd.Timedelta(days=DUREE_JOURS)
        termine = pd.Timestamp.now() >= fin
        lignes = []
        for t in s["titres"]:
            p1 = _dernier_prix(bruts.get(t["ticker"]), fin if termine else None)
            i1 = _dernier_prix(bruts.get(t["indice"]), fin if termine else None)
            if not p1 or not i1:
                continue
            r, ri = p1 / t["prix"] - 1, i1 / t["prix_indice"] - 1
            lignes.append({**t, "perf": r, "perf_indice": ri, "ecart": r - ri, "mieux": bool(r > ri)})
        if not lignes:
            continue
        out.append({"mois": mois, "date": s["date"], "termine": bool(termine), "titres": lignes,
                    "perf": float(np.mean([l["perf"] for l in lignes])),
                    "perf_indices": float(np.mean([l["perf_indice"] for l in lignes])),
                    "ecart": float(np.mean([l["ecart"] for l in lignes])),
                    "nb_mieux": int(sum(l["mieux"] for l in lignes)), "nb": len(lignes)})
    finis = [m for m in out if m["termine"]]
    resume = None
    if finis:
        resume = {"nb_mois": len(finis), "ecart_moyen": float(np.mean([m["ecart"] for m in finis])),
                  "mois_gagnants": int(sum(m["ecart"] > 0 for m in finis)),
                  "titres_mieux": int(sum(m["nb_mieux"] for m in finis)), "titres": int(sum(m["nb"] for m in finis))}
    return {"mois": out[::-1], "resume": resume}
