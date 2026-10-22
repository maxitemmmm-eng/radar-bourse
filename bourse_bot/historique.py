"""Suivi en conditions réelles : chaque prédiction est enregistrée, puis vérifiée une fois
l'horizon écoulé. C'est la seule preuve qui compte vraiment (aucun recalcul possible après coup).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import config
from .model import wilson

FICHIER = os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv")
COLS = ["date", "ticker", "prix", "proba", "score", "signal", "fort", "bas", "haut", "proba_marche", "indice", "accord",
        "proba_brute", "confiance", "mouvement"]
TRANCHES = [(0.0, 0.45, "< 45 %"), (0.45, 0.50, "45–50 %"), (0.50, 0.55, "50–55 %"), (0.55, 0.60, "55–60 %"),
            (0.60, 1.01, "> 60 %")]


def _num(v):
    try:
        v = float(v)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def enregistrer(analyses) -> None:
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    lignes = []
    for a in analyses:
        q = tuple(a.quantiles or ())
        lignes.append({
            "date": a.date_cours, "ticker": a.ticker, "prix": a.prix, "proba": a.proba_hausse,
            "score": a.score, "signal": a.signal, "fort": int(bool(a.signal_fort)),
            # fourchette « 8 chances sur 10 » à l'horizon, telle qu'affichée sur le site
            "bas": a.prix * np.exp(q[0]) if len(q) == 3 else np.nan,
            "haut": a.prix * np.exp(q[2]) if len(q) == 3 else np.nan,
            "proba_marche": getattr(a, "proba_marche", np.nan), "indice": getattr(a, "indice_ref", "") or "",
            "accord": {True: 1, False: 0}.get(getattr(a, "accord_ia", None), np.nan),
            "proba_brute": getattr(a, "proba_brute", np.nan),
            "confiance": getattr(a, "confiance", "") or "",
            "mouvement": (getattr(a, "risque_prevu", None) or {}).get("mouvement", np.nan)})
    nouvelles = pd.DataFrame(lignes, columns=COLS)
    if os.path.exists(FICHIER):
        anciennes = pd.read_csv(FICHIER)
        tout = pd.concat([anciennes, nouvelles], ignore_index=True)
    else:
        tout = nouvelles
    for c in COLS:   # anciens fichiers : colonnes ajoutées depuis
        if c not in tout.columns:
            tout[c] = np.nan
    # une seule prédiction par titre et par jour de cotation (on garde la plus récente)
    tout = tout.drop_duplicates(subset=["date", "ticker"], keep="last")
    tout[COLS].to_csv(FICHIER, index=False)


def _type(ticker: str) -> str:
    if ticker.endswith("-USD"):
        return "Cryptos"
    if ticker.endswith(".PA"):
        return "Actions françaises"
    if ticker.endswith((".DE", ".AS", ".MC", ".MI")):
        return "Actions européennes"
    if ticker.startswith("^"):
        return "Indices"
    return "Actions et ETF américains"


def _prix_apres(d: pd.DataFrame, date, horizon: int):
    apres = d.index[d.index > pd.Timestamp(date)]
    if len(apres) < horizon:
        return None, None
    jour = apres[horizon - 1]
    return float(d.loc[jour, "Close"]), jour


def bilan(donnees: dict[str, pd.DataFrame], horizon: int = config.HORIZON_PREDICTION) -> dict:
    """Compare les anciennes prédictions à ce qui s'est réellement passé."""
    vide = {"nb_verifiees": 0, "nb_en_attente": 0, "precision": None, "precision_signaux_achat": None,
            "dernieres": [], "detail": None}
    if not os.path.exists(FICHIER):
        return vide
    hist = pd.read_csv(FICHIER)
    if hist.empty:
        return vide
    for c in COLS:
        if c not in hist.columns:
            hist[c] = np.nan

    verifiees, attente = [], 0
    for r in hist.itertuples(index=False):
        d = donnees.get(r.ticker)
        if d is None or len(d) == 0:
            continue
        prix_fin, jour_fin = _prix_apres(d, r.date, horizon)
        if prix_fin is None:
            attente += 1
            continue
        prix, proba = _num(r.prix), _num(r.proba)
        if not prix or np.isnan(prix):
            continue
        reel = prix_fin / prix - 1
        prevu_hausse = (proba > 0.5) if not np.isnan(proba) else _num(r.score) >= 60
        ligne = {"date": r.date, "ticker": r.ticker, "type": _type(r.ticker), "proba": None if np.isnan(proba) else proba,
                 "signal": r.signal, "fort": bool(_num(r.fort) == 1), "rendement_reel": reel,
                 "juste": bool(prevu_hausse == (reel > 0)), "dans_fourchette": None, "juste_marche": None,
                 "accord": None if np.isnan(_num(r.accord)) else bool(_num(r.accord) == 1)}
        bas, haut = _num(r.bas), _num(r.haut)
        if not np.isnan(bas) and not np.isnan(haut):
            ligne["dans_fourchette"] = bool(bas <= prix_fin <= haut)
        pm, ind = _num(r.proba_marche), str(r.indice) if isinstance(r.indice, str) else ""
        di = donnees.get(ind) if ind else None
        if not np.isnan(pm) and di is not None and len(di):
            try:
                p0 = float(di["Close"][di.index <= pd.Timestamp(r.date)].iloc[-1])
                p1 = float(di["Close"][di.index <= jour_fin].iloc[-1])
                ligne["juste_marche"] = bool((pm > 0.5) == (reel > p1 / p0 - 1))
            except (IndexError, KeyError, ZeroDivisionError):
                pass
        verifiees.append(ligne)
    if not verifiees:
        return {**vide, "nb_en_attente": attente}
    v = pd.DataFrame(verifiees)
    achats = v[v["signal"].astype(str).str.startswith("ACHAT")]
    taux = lambda s: float(s.mean()) if len(s) else None

    def groupe(col):
        return [{"nom": str(k), "nb": int(len(g)), "precision": float(g["juste"].mean()),
                 "rendement_median": float(g["rendement_reel"].median())} for k, g in v.groupby(col)]
    v["mois"] = v["date"].astype(str).str[:7]
    calib = []
    avec_p = v.dropna(subset=["proba"])
    for a, b, nom in TRANCHES:
        sel = avec_p[(avec_p["proba"] >= a) & (avec_p["proba"] < b)]
        calib.append({"tranche": nom, "nb": int(len(sel)),
                      "taux_hausse": float((sel["rendement_reel"] > 0).mean()) if len(sel) else None})
    fourch = v.dropna(subset=["dans_fourchette"])
    rel = v.dropna(subset=["juste_marche"])
    forts = v[v["fort"]]
    acc = v.dropna(subset=["accord"])
    ic = lambda s: list(wilson(int(s.sum()), len(s))) if len(s) else None
    detail = {
        "base_hausse": float((v["rendement_reel"] > 0).mean()),   # « dire toujours hausse » aurait eu raison X %
        "par_mois": sorted(groupe("mois"), key=lambda x: x["nom"]),
        "par_type": sorted(groupe("type"), key=lambda x: -x["nb"]),
        "calibration": calib,
        "fourchette": {"nb": int(len(fourch)), "taux": taux(fourch["dans_fourchette"].astype(float))},
        "marche": {"nb": int(len(rel)), "precision": taux(rel["juste_marche"].astype(float))},
        "forts": {"nb": int(len(forts)), "precision": taux((forts["rendement_reel"] > 0).astype(float)),
                  "ic": ic((forts["rendement_reel"] > 0)),
                  "rendement_median": float(forts["rendement_reel"].median()) if len(forts) else None},
        "accord": {"nb": int(acc["accord"].astype(bool).sum()), "precision": taux(acc.loc[acc["accord"].astype(bool), "juste"].astype(float)),
                   "nb_desaccord": int((~acc["accord"].astype(bool)).sum()),
                   "precision_desaccord": taux(acc.loc[~acc["accord"].astype(bool), "juste"].astype(float))},
        "ic_precision": ic(v["juste"]), "nb_jours": int(v["date"].nunique()),
        "premiere": str(v["date"].min()), "derniere": str(v["date"].max()),
        # palmarès par titre : [prévisions vérifiées, justes]
        "par_titre": {str(t): [int(len(g)), int(g["juste"].sum())] for t, g in v.groupby("ticker")},
    }
    colonnes = ["date", "ticker", "proba", "signal", "fort", "rendement_reel", "juste", "dans_fourchette"]
    return {
        "nb_verifiees": len(v), "nb_en_attente": attente,
        "precision": float(v["juste"].mean()),
        "precision_signaux_achat": float((achats["rendement_reel"] > 0).mean()) if len(achats) else None,
        "dernieres": v.sort_values("date", ascending=False).head(15)[colonnes[:2] + ["proba", "signal", "rendement_reel", "juste"]].to_dict("records"),
        "toutes": v.sort_values("date", ascending=False).head(300)[colonnes].to_dict("records"),
        "detail": detail,
    }


def correction_erreurs(donnees: dict, horizon: int = config.HORIZON_PREDICTION) -> dict | None:
    """Apprendre de ses erreurs réelles : on compare les probabilités publiées à ce qui s'est vraiment passé.
    Si les IA ont été trop sûres d'elles, leurs prochaines probabilités sont rendues moins tranchées.
    Par prudence, la correction ne peut que RAPPROCHER les probabilités de 50 %, jamais les exagérer."""
    if not os.path.exists(FICHIER):
        return None
    try:
        h = pd.read_csv(FICHIER)
    except (OSError, ValueError):
        return None
    if "proba_brute" not in h.columns:
        h["proba_brute"] = np.nan
    h["p"] = pd.to_numeric(h["proba_brute"], errors="coerce").fillna(pd.to_numeric(h["proba"], errors="coerce"))
    h = h.dropna(subset=["p"])
    p_l, y_l, dates = [], [], set()
    for r in h.itertuples(index=False):
        d = donnees.get(r.ticker)
        if d is None or len(d) == 0:
            continue
        fin, _ = _prix_apres(d, r.date, horizon)
        prix = _num(r.prix)
        if fin is None or not prix or np.isnan(prix):
            continue
        p_l.append(float(r.p))
        y_l.append(1.0 if fin > prix else 0.0)
        dates.add(r.date)
    n = len(p_l)
    if n < 300 or len(dates) < 15:
        return {"n": n, "jours": len(dates), "active": False,
                "raison": "pas encore assez de prévisions vérifiées (il en faut au moins 300 sur 15 jours)"}
    p, y = np.clip(np.array(p_l), 0.02, 0.98), np.array(y_l)
    z = np.log(p / (1 - p))
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(C=1.0).fit(z.reshape(-1, 1), y)
    a = float(np.clip(lr.coef_[0][0], 0.3, 1.0))
    b = float(np.clip(lr.intercept_[0], -0.25, 0.25))
    pc = 1 / (1 + np.exp(-(a * z + b)))
    perte = lambda q: float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))
    avant, apres = perte(p), perte(pc)
    active = apres < avant - 1e-4
    return {"n": n, "jours": len(dates), "a": a, "b": b, "active": bool(active),
            "perte_avant": avant, "perte_apres": apres,
            "raison": ("les vraies erreurs montrent que les IA étaient trop sûres d'elles : leurs probabilités sont adoucies"
                       if active and a < 0.98 else "corrigé d'un léger biais constaté sur les vrais résultats" if active
                       else "les vrais résultats ne demandent aucune correction")}


def appliquer_correction(p: float, corr: dict | None) -> float:
    if not corr or not corr.get("active") or p is None or p != p:
        return p
    q = min(max(p, 0.02), 0.98)
    z = np.log(q / (1 - q))
    return float(1 / (1 + np.exp(-(corr["a"] * z + corr["b"]))))
