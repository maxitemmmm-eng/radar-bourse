"""Version 56 : les IA de risque (agitation à un mois, risque de forte chute) se règlent toutes seules, nuit après nuit.

Jusqu'ici, seule l'IA du « sens du prix » (proche du hasard) cherchait de meilleurs réglages chaque nuit ; les deux IA qui
marchent vraiment gardaient des réglages fixes. Désormais, chaque nuit :
  1. Quelques nouveaux réglages sont essayés : la moitié autour des meilleures idées déjà trouvées (mémoire de tous les
     essais, comme un chercheur qui reprend ses notes), l'autre moitié au hasard pour ne pas tourner en rond.
  2. Chaque essai est comparé à l'IA en place sur les MÊMES périodes jamais vues (validation walk-forward), dans la zone
     de recherche : les années récentes restent sous clé.
  3. Le meilleur essai prometteur passe l'examen final sur les années sous clé. Il n'est adopté que s'il fait mieux de façon
     prouvée (marge d'erreur à 95 % au-dessus de zéro, par mois) ET sur chacune des deux moitiés de l'examen.
     Les années sous clé resservent d'une nuit à l'autre : pour limiter la chance, le seuil exigé monte avec le nombre
     d'examens déjà passés, et un essai doit d'abord être nettement meilleur dans la zone de recherche.
  4. Tout est noté dans historique/reglages_risque.json : réglages adoptés, essais, et un journal lisible sur le site
     (page « Journal de l'IA »).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from datetime import datetime

import numpy as np
import pandas as pd

from . import config

FICHIER = os.path.join(config.DOSSIER_HISTORIQUE, "reglages_risque.json")

DEFAUTS = {
    "agitation": {"max_depth": 3, "learning_rate": 0.05, "max_iter": 300, "min_samples_leaf": 300, "l2_regularization": 1.0},
    "chute": {"max_depth": 3, "learning_rate": 0.05, "max_iter": 200, "min_samples_leaf": 500, "l2_regularization": 0.0},
}
ESPACE = {
    "max_depth": [2, 3, 4, 5, 6],
    "learning_rate": [0.02, 0.03, 0.05, 0.08, 0.12],
    "max_iter": [150, 200, 300, 450, 600],
    "min_samples_leaf": [100, 200, 300, 500, 800, 1200, 2000],
    "l2_regularization": [0.0, 0.3, 1.0, 3.0, 10.0],
}
NOMS = {"agitation": "l'IA de l'agitation à un mois", "chute": "l'IA du risque de forte chute"}


# ----------------------------------------------------------------------------------------------------------------------
# Lecture / écriture
# ----------------------------------------------------------------------------------------------------------------------
def _lire() -> dict:
    try:
        with open(FICHIER, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _ecrire(d: dict) -> None:
    os.makedirs(os.path.dirname(FICHIER), exist_ok=True)
    d["essais"] = d.get("essais", [])[-400:]       # la mémoire reste légère
    d["journal"] = d.get("journal", [])[-120:]
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def reglages(nom: str) -> dict:
    """Réglages en place pour « agitation » ou « chute » (ceux par défaut tant que rien n'a été prouvé meilleur)."""
    r = ((_lire().get("adoptes") or {}).get(nom) or {}).get("params")
    if isinstance(r, dict) and all(k in ESPACE for k in r):
        return {**DEFAUTS[nom], **r}
    return dict(DEFAUTS[nom])


def signature() -> str:
    """Change dès que des réglages sont adoptés : les IA du matin sont alors réentraînées."""
    return hashlib.sha1(json.dumps([reglages("agitation"), reglages("chute")], sort_keys=True).encode()).hexdigest()[:10]


def journal() -> dict:
    """Ce que la page « Journal de l'IA » affiche."""
    d = _lire()
    return {"journal": d.get("journal", []), "adoptes": d.get("adoptes", {}), "nb_essais": len(d.get("essais", [])),
            "nb_examens": d.get("nb_examens", {})}


# ----------------------------------------------------------------------------------------------------------------------
# Modèles et mesures
# ----------------------------------------------------------------------------------------------------------------------
def fabriquer(nom: str, params: dict | None = None):
    from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
    from .comprendre import SansColonnesVides
    p = {**DEFAUTS[nom], **(params or {})}
    cls = HistGradientBoostingRegressor if nom == "agitation" else HistGradientBoostingClassifier
    return SansColonnesVides(cls(random_state=0, **p))


def _preparer(jeu: pd.DataFrame, nom: str, variables_base):
    from . import comprendre
    if nom == "agitation":
        et = jeu.dropna(subset=["vol_futur", "vol_20j"])
        et = et[np.isfinite(et["vol_futur"])].copy()
        et["y"] = et["vol_futur"]
        vs = comprendre._variables_agitation(et, variables_base)
    else:
        et = jeu.dropna(subset=["rendement_futur"]).copy()
        et["y"] = (et["rendement_futur"] < comprendre.SEUIL_CHUTE).astype(float)
        vs = comprendre._variables_chute(et, variables_base)
    return et, vs


def _predire(m, nom, X):
    return m.predict(X) if nom == "agitation" else m.predict_proba(X)[:, 1]


def _sorties(et, vs, nom, params, tranches, horizon):
    """Prévisions hors échantillon : pour chaque tranche de test, entraînement sur tout ce qui précède (avec purge)."""
    morceaux = []
    jours = et.index
    for debut, fin in tranches:
        purge = debut - pd.Timedelta(days=int(horizon * 1.6) + 2)
        train = et[jours < purge]
        test = et[(jours >= debut) & (jours <= fin)]
        if len(train) < 3000 or test.empty or (nom == "chute" and train["y"].nunique() < 2):
            continue
        m = fabriquer(nom, params).fit(train[vs], train["y"].to_numpy())
        morceaux.append(pd.DataFrame({"y": test["y"].to_numpy(), "p": _predire(m, nom, test[vs])}, index=test.index))
    return pd.concat(morceaux) if morceaux else None


def _tranches(dates, n):
    dates = np.array(sorted(pd.unique(dates)))
    if len(dates) < n * 20:
        return []
    bornes = np.array_split(dates, n)
    return [(b[0], b[-1]) for b in bornes]


def _comparer(nom, o_ref, o_new, graine=0):
    """Gain du nouveau réglage sur l'ancien, mêmes lignes ; marge d'erreur par tirage de mois (bootstrap).
    agitation : baisse de l'erreur absolue (en log) ; chute : hausse de l'AUC."""
    from .model import _auc, _ic, bootstrap_mois
    commun = o_ref.index.intersection(o_new.index) if not o_ref.index.has_duplicates else None
    if commun is None:   # plusieurs titres par jour : on aligne par position (mêmes tranches, même ordre)
        d = pd.DataFrame({"y": o_ref["y"].to_numpy(), "a": o_ref["p"].to_numpy(), "b": o_new["p"].to_numpy()}, index=o_ref.index)
    else:
        d = pd.DataFrame({"y": o_ref.loc[commun, "y"], "a": o_ref.loc[commun, "p"], "b": o_new.loc[commun, "p"]})
    d = d[np.isfinite(d[["y", "a", "b"]]).all(axis=1)]
    if nom == "agitation":
        d["g"] = np.abs(d["a"] - d["y"]) - np.abs(d["b"] - d["y"])
        stat = lambda x: np.array([x["g"].mean()])
        gain = float(d["g"].mean())
        ref = float(np.expm1(np.abs(d["a"] - d["y"]).median()))
        new = float(np.expm1(np.abs(d["b"] - d["y"]).median()))
    else:
        stat = lambda x: np.array([_auc(x["y"].to_numpy(), x["b"].to_numpy()) - _auc(x["y"].to_numpy(), x["a"].to_numpy())])
        ref, new = _auc(d["y"].to_numpy(), d["a"].to_numpy()), _auc(d["y"].to_numpy(), d["b"].to_numpy())
        gain = float(new - ref)
    boot = bootstrap_mois(d, stat, n=300, graine=graine)
    ic = _ic(boot[:, 0]) if len(boot) else None
    # régularité : le gain est-il positif sur chacune des deux moitiés ?
    moitie = d.index.sort_values()[len(d) // 2]
    moities = []
    for part in (d[d.index < moitie], d[d.index >= moitie]):
        if part.empty:
            moities.append(False)
        elif nom == "agitation":
            moities.append(bool(part["g"].mean() > 0))
        else:
            moities.append(bool(_auc(part["y"].to_numpy(), part["b"].to_numpy()) > _auc(part["y"].to_numpy(), part["a"].to_numpy())))
    return {"gain": gain, "ic": ic, "moities": moities, "score_ref": ref, "score_new": new, "nb": int(len(d))}


# ----------------------------------------------------------------------------------------------------------------------
# Recherche guidée par la mémoire
# ----------------------------------------------------------------------------------------------------------------------
def _cle(p: dict) -> str:
    return json.dumps({k: p[k] for k in sorted(p)}, sort_keys=True)


def _proposer(nom, champion, essais, deja, rng, n):
    """La moitié des idées part des meilleurs essais passés (1 ou 2 réglages changés), l'autre moitié au hasard."""
    bons = sorted((e for e in essais if e.get("modele") == nom and (e.get("gain") or 0) > 0), key=lambda e: -e["gain"])[:5]
    graines = [champion] + [e["params"] for e in bons]
    out, essais_max = [], 200
    while len(out) < n and essais_max > 0:
        essais_max -= 1
        if len(out) % 2 == 0:
            base = dict(rng.choice(graines))
            for k in rng.sample(list(ESPACE), rng.choice([1, 2])):
                base[k] = rng.choice(ESPACE[k])
        else:
            base = {k: rng.choice(v) for k, v in ESPACE.items()}
        c = _cle(base)
        if c not in deja:
            deja.add(c)
            out.append(base)
    return out


def seance(jeu: pd.DataFrame, horizon: int, variables_base, budget_s: float = 600, log=print, arret=None,
           part_cle: float = 0.2, pas: int = 3, max_lignes: int = 300_000, graine: int | None = None) -> dict:
    """Une nuit d'auto-réglage pour les deux IA de risque. Renvoie un résumé (et l'écrit dans le journal)."""
    t0 = time.time()
    etat = _lire()
    etat.setdefault("adoptes", {})
    etat.setdefault("essais", [])
    etat.setdefault("nb_examens", {})
    etat.setdefault("journal", [])
    rng = random.Random(graine if graine is not None else int(datetime.now().strftime("%Y%m%d")))
    resume = {"date": datetime.now().isoformat(timespec="minutes"), "modeles": {}}
    noms = ["agitation", "chute"]
    for i, nom in enumerate(noms):
        budget_nom = budget_s * (i + 1) / len(noms) - (time.time() - t0)
        et, vs = _preparer(jeu, nom, variables_base)
        if len(et) < 20000:
            log(f"   {NOMS[nom]} : trop peu de données pour s'entraîner cette nuit.")
            continue
        dates = np.array(sorted(pd.unique(et.index)))
        coupure = dates[int(len(dates) * (1 - part_cle))]
        zone = et[et.index < coupure]
        jours = np.array(sorted(pd.unique(zone.index)))[::pas]
        zone = zone[zone.index.isin(jours)]
        if len(zone) > max_lignes:
            zone = zone.sample(max_lignes, random_state=0).sort_index()
        tr_zone = _tranches(zone.index[zone.index >= jours[int(len(jours) * 0.45)]], 4)
        champion = reglages(nom)
        log(f"🔧 {NOMS[nom][0].upper() + NOMS[nom][1:]} : réglages en place {_texte(champion)}")
        o_champ = _sorties(zone, vs, nom, champion, tr_zone, horizon)
        if o_champ is None:
            continue
        deja = {_cle(e["params"]) for e in etat["essais"] if e.get("modele") == nom} | {_cle(champion)}
        candidats, essayes = [], 0
        for p in _proposer(nom, champion, etat["essais"], deja, rng, 12):
            if (arret is not None and arret.is_set()) or time.time() - t0 > budget_nom * 0.75 + (budget_s * i / len(noms)):
                break
            o = _sorties(zone, vs, nom, p, tr_zone, horizon)
            essayes += 1
            if o is None or len(o) != len(o_champ):
                continue
            c = _comparer(nom, o_champ, o, graine=essayes)
            etat["essais"].append({"modele": nom, "params": p, "gain": c["gain"], "ic": c["ic"], "date": resume["date"][:10]})
            log(f"   essai {essayes} : {_texte(p)} → {_gain_texte(nom, c['gain'])}")
            if c["ic"] and c["ic"][0] > 0 and all(c["moities"]):
                candidats.append((c["gain"], p))
        res = {"essayes": essayes, "candidats": len(candidats), "adopte": False, "champion": champion}
        if candidats:
            gain, meilleur = max(candidats, key=lambda x: x[0])
            n_ex = int(etat["nb_examens"].get(nom, 0)) + 1
            etat["nb_examens"][nom] = n_ex
            # seuil qui monte avec les examens déjà passés sur les mêmes années (anti-chance)
            # gain minimum dès le 1er examen (pas de changement pour un gain infime), qui monte ensuite avec les examens
            exige = (0.0002 if nom == "agitation" else 0.0005) + (0.0005 if nom == "agitation" else 0.0015) * np.log(n_ex)
            final = et[et.index >= coupure - pd.Timedelta(days=0)]
            tr_final = _tranches(final.index, 2)
            o_a = _sorties(et, vs, nom, champion, tr_final, horizon)
            o_b = _sorties(et, vs, nom, meilleur, tr_final, horizon)
            if o_a is not None and o_b is not None and len(o_a) == len(o_b):
                c = _comparer(nom, o_a, o_b, graine=99)
                ok = bool(c["ic"] and c["ic"][0] > exige and all(c["moities"]))
                res.update({"examen": c, "exige": exige, "meilleur": meilleur, "adopte": ok})
                log(f"   🧪 Examen final ({NOMS[nom]}) : {_gain_texte(nom, c['gain'])}"
                    + (f", marge {c['ic'][0]:+.4f} à {c['ic'][1]:+.4f}" if c["ic"] else "")
                    + (" → ✅ adopté : c'est prouvé et régulier." if ok else " → ➖ pas assez prouvé : on garde l'IA en place."))
                if ok:
                    etat["adoptes"][nom] = {"params": meilleur, "date": resume["date"], "score_avant": c["score_ref"],
                                            "score_apres": c["score_new"], "ic": c["ic"]}
        else:
            log(f"   Aucun essai nettement meilleur que l'IA en place cette nuit ({essayes} essayés).")
        resume["modeles"][nom] = res
    etat["journal"].append({"date": resume["date"], "duree_s": round(time.time() - t0),
                            **{nom: {"essayes": r["essayes"], "adopte": r["adopte"],
                                     "gain": (r.get("examen") or {}).get("gain"),
                                     "score_avant": (r.get("examen") or {}).get("score_ref"),
                                     "score_apres": (r.get("examen") or {}).get("score_new")}
                               for nom, r in resume["modeles"].items()}})
    _ecrire(etat)
    resume["change"] = any(r["adopte"] for r in resume["modeles"].values())
    return resume


def _texte(p: dict) -> str:
    return (f"profondeur {p['max_depth']}, pas {p['learning_rate']}, {p['max_iter']} arbres, "
            f"feuilles ≥ {p['min_samples_leaf']}, régularisation {p['l2_regularization']}")


def _gain_texte(nom, g) -> str:
    if g is None:
        return "non mesuré"
    return (f"erreur {'en baisse' if g > 0 else 'en hausse'} de {abs(g) * 100:.2f} pt (log)" if nom == "agitation"
            else f"AUC {g:+.4f}")
