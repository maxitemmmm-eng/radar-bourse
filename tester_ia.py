"""Test de l'IA sur 5000 cas réels tirés au hasard.

Ce test télécharge les vrais cours, entraîne l'IA du site uniquement sur le PASSÉ de chaque période,
puis lui fait prévoir des mois qu'elle n'a jamais vus. On tire ensuite 5000 cas au hasard parmi ces
prévisions et on compte combien de fois elle a eu raison (le prix a-t-il fini plus haut ou plus bas un mois après ?).

Le résultat est comparé à la « référence naïve » : répondre toujours la même chose (par exemple « hausse »).
Faire mieux que ça, c'est ça qui compte.

Lancement : double-clique sur tester_ia.bat   (ou : python tester_ia.py)
Options : --cas 5000 (nombre de cas)   --demo (essai avec des données fictives)
Durée : 10 à 25 minutes selon le PC. Rien n'est envoyé sur Internet : le rapport reste dans « rapports ».
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
sys.path.insert(0, ICI)

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")   # avertissements techniques des librairies : sans importance pour le résultat

from bourse_bot import config, data, main as radar, model


NOMS = {"fr": "Actions françaises", "eu": "Actions européennes", "us": "Actions américaines",
        "crypto": "Cryptos", "etf": "ETF et indices", "tendances": "En tendance"}


def pct(x):
    return f"{x * 100:.1f} %".replace(".", ",")


MACRO = ["marche_tendance", "marche_vol", "vix", "vix_chg", "vix_structure", "courbe_taux", "taux_chg", "dollar_chg",
         "spread_credit", "spread_credit_chg", "conditions_fin", "chomage_tendance", "marche_largeur", "marche_dispersion",
         "fng", "est_crypto"]
TITRE = ["ret_21j", "ret_63j", "ret_126j", "vol_20j", "dist_sma200", "drawdown", "rsi"]
ANNEES_BAISSE = (2008, 2011, 2015, 2018, 2020, 2022)


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


NOM_SITE = "IA prudente par marché (tendance habituelle là où l'IA n'a pas fait ses preuves) ← utilisée sur le site"


def examen_final(methodes, ok, yy, dates_ok, hausse, noms):
    """Version 43 : un examen plus dur et plus fiable que le simple score sur 5000.
    Une méthode ne le réussit que si elle bat la règle « toujours hausse » :
      1. de façon sûre MÊME en tenant compte du nombre de méthodes essayées (sinon, en en essayant 15, une finit
         toujours devant par chance) ;
      2. sur la majorité des années, pas grâce à une seule année exceptionnelle ;
      3. sur les 24 derniers mois, jamais utilisés pour choisir quoi que ce soit ;
    et on montre de combien le score sur 5000 varie d'un tirage à l'autre."""
    nb_meth = sum(1 for k in methodes if not k.startswith("("))
    j_ref = (yy == 1) if hausse >= .5 else (yy == 0)
    annee = dates_ok.year.to_numpy()
    recent = dates_ok >= dates_ok.max() - pd.DateOffset(months=24)
    rng = np.random.default_rng(7)
    out = ["", "   EXAMEN FINAL (plus dur) : pour réussir, il faut battre « toujours hausse » sur les 3 épreuves",
           f"   1) de façon sûre même en comptant les {nb_meth} méthodes essayées · 2) sur la majorité des années · 3) sur les 24 derniers mois"]
    vus = set()
    for nom in noms:
        if nom in vus:
            continue
        vus.add(nom)
        pp = np.asarray(methodes[nom])[ok]
        if not np.isfinite(pp).all():
            continue
        juste = (pp >= 0.5) == (yy == 1)
        d = pd.DataFrame({"g": juste.astype(float) - j_ref.astype(float)}, index=dates_ok)
        boot = model.bootstrap_mois(d, lambda x: np.array([x["g"].mean()]), graine=43)
        lo = float(np.percentile(boot[:, 0], 100 * 0.025 / max(nb_meth, 1))) if len(boot) else -1.0
        e1 = lo > 0
        ans = sorted(set(annee))
        gagne = sum(1 for a in ans if juste[annee == a].mean() > j_ref[annee == a].mean() + 1e-9)
        e2 = gagne > len(ans) / 2
        sr, rr = float(juste[recent].mean()), float(j_ref[recent].mean())
        e3 = sr > rr
        tirages = [int(juste[rng.choice(len(juste), 5000, replace=False)].sum()) for _ in range(30)] if len(juste) > 5000 else []
        court = nom.split(" ←")[0]
        if len(court) > 70:
            court = court.split(" (")[0]
        out.append(f"   • {court} : {'RÉUSSI ✅' if e1 and e2 and e3 else 'pas réussi'}")
        out.append(f"       épreuve 1 {'✅' if e1 else '❌'} (écart sûr minimum : {lo * 5000:+.0f} sur 5000)"
                   f" · épreuve 2 {'✅' if e2 else '❌'} ({gagne} année{'s' if gagne > 1 else ''} gagnée{'s' if gagne > 1 else ''} sur {len(ans)})"
                   f" · épreuve 3 {'✅' if e3 else '❌'} (24 derniers mois : {round(sr * 5000)} contre {round(rr * 5000)})")
        if tirages:
            out.append(f"       sur 30 tirages de 5000 cas, son score va de {min(tirages)} à {max(tirages)} (moyenne {round(np.mean(tirages))}) : "
                       "un écart de quelques dizaines entre deux tests est normal")
    return out


def tester_semaine(tous):
    """Version 48 : l'agitation sur une semaine (5 séances), modèle simple contre « comme la semaine dernière »,
    chaque année n'apprenant que des années d'avant."""
    from sklearn.linear_model import LinearRegression
    from bourse_bot import comprendre as C
    L = []
    for t, df in tous.items():
        if df is None or len(df) < 400:
            continue
        c = df["Close"].dropna()
        r, v5, v20, v63 = C._vols_semaine(c)
        d = pd.DataFrame({"v5": v5, "v20": v20, "v63": v63, "cr": float(str(t).endswith("-USD")),
                          "fut": r[::-1].rolling(5).std()[::-1].shift(-1), "mvt": (c.shift(-5) / c - 1).abs()}).dropna()
        d = d[(d[["v5", "v20", "v63", "fut"]] > 1e-5).all(axis=1)].iloc[::5]
        d.index = pd.DatetimeIndex(d.index).tz_localize(None) if pd.DatetimeIndex(d.index).tz is not None else d.index
        L.append(d)
    if not L:
        return []
    O = pd.concat(L)
    an = pd.DatetimeIndex(O.index).year.to_numpy()
    X = np.c_[np.log(O[["v5", "v20", "v63"]].to_numpy()), O["cr"].to_numpy()]
    y = np.log(O["fut"].to_numpy())
    pred = np.full(len(O), np.nan)
    for a in sorted(set(an)):
        app, tst = an < a, an == a
        if app.sum() >= 5000:
            pred[tst] = LinearRegression().fit(X[app], y[app]).predict(X[tst])
    ok = np.isfinite(pred)
    if ok.sum() < 1000:
        return []
    e_ia = np.abs(np.exp(pred[ok]) * np.sqrt(5) - O["mvt"].to_numpy()[ok])
    e_nf = np.abs(O["v5"].to_numpy()[ok] * np.sqrt(5) - O["mvt"].to_numpy()[ok])
    ans = an[ok]
    gagne = sum(np.mean(e_ia[ans == a] < e_nf[ans == a]) > .5 for a in np.unique(ans))
    k = int(ok.sum()); mieux = float(np.mean(e_ia < e_nf))
    return ["", "3 bis. L'AGITATION SUR UNE SEMAINE (5 séances)",
            f"➜ Plus proche de la réalité que « comme la semaine dernière » dans {pct(mieux)} des cas ({f'{k:,}'.replace(',', ' ')} cas)"
            + f" · meilleure {gagne} années sur {len(np.unique(ans))}",
            f"  Erreur habituelle (médiane) : modèle {pct(float(np.median(e_ia)))} · méthode simple {pct(float(np.median(e_nf)))}",
            "  " + ("Verdict : fait mieux que la méthode simple, de façon régulière." if mieux > .5 and gagne > len(np.unique(ans)) * .75 else
                    "Verdict : pas assez régulier.")]


def explorer(jeu, oof, rel, masque, horizon):
    """Essaie d'autres façons de choisir « hausse » ou « baisse », toutes testées sans tricher :
    chaque méthode n'apprend que sur les années AVANT celle qu'elle prévoit, puis on compte ses bonnes réponses
    sur exactement les mêmes cas que l'IA actuelle."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer

    O = oof.copy()
    O["_i"] = np.arange(len(O))
    O["_d"] = pd.to_datetime(O.index)
    from bourse_bot import comprendre as C
    cols_chute = [c for c in C._variables_chute(jeu, model.VARIABLES_BASE) if c in jeu.columns]
    cols = list(dict.fromkeys([c for c in MACRO + TITRE if c in jeu.columns] + cols_chute))
    J = jeu[["ticker"] + cols].copy()
    J["_d"] = pd.to_datetime(J.index)
    J = J.drop_duplicates(["_d", "ticker"])
    O = O.merge(J, on=["_d", "ticker"], how="left")
    if rel is not None and "ticker" in rel:
        R = rel[["ticker", "proba"]].rename(columns={"proba": "proba_rel"}).copy()
        R["_d"] = pd.to_datetime(R.index)
        O = O.merge(R.drop_duplicates(["_d", "ticker"]), on=["_d", "ticker"], how="left")
    else:
        O["proba_rel"] = np.nan
    O = O.sort_values("_i").reset_index(drop=True)
    O["l_ia"] = _logit(O["proba"])
    O["l_rel"] = _logit(O["proba_rel"].fillna(0.5))
    y = O["cible"].to_numpy()

    def walk_forward(features, fabrique):
        """Prévisions année par année : le modèle de l'année A n'a vu que les données d'avant (avec un mois d'écart)."""
        p = np.full(len(O), np.nan)
        annees = sorted(O["_d"].dt.year.unique())
        for a in annees[1:]:
            debut = pd.Timestamp(year=a, month=1, day=1)
            app = O["_d"] < debut - pd.Timedelta(days=horizon * 1.5)
            cib = O["_d"].dt.year == a
            if app.sum() < 3000 or cib.sum() == 0 or len(np.unique(y[app])) < 2:
                continue
            m = fabrique().fit(O.loc[app, features], y[app])
            p[cib.to_numpy()] = m.predict_proba(O.loc[cib, features])[:, 1]
        return p

    lin = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=0.1, max_iter=500))
    from bourse_bot.comprendre import SansColonnesVides
    gbm = lambda: SansColonnesVides(HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=500, random_state=0))
    macro = [c for c in MACRO if c in O.columns and O[c].nunique(dropna=True) > 1]
    titre = [c for c in TITRE if c in O.columns and O[c].nunique(dropna=True) > 1]
    # IA actuelle, recalée année par année sur les seules années d'avant (comme toutes les autres méthodes : sans tricher)
    p_ia = np.full(len(O), np.nan)
    for a_ in sorted(O["_d"].dt.year.unique())[1:]:
        app = (O["_d"] < pd.Timestamp(year=a_, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)).to_numpy()
        cib = (O["_d"].dt.year == a_).to_numpy()
        if app.sum() >= 3000 and cib.any():
            p_ia[cib] = model.CalibrationPlatt().fit(O.loc[app, "proba"], y[app]).predict(O.loc[cib, "proba"].to_numpy())
    methodes = {"IA actuelle": p_ia}
    tend = O["marche_tendance"].to_numpy() if "marche_tendance" in O else np.full(len(O), np.nan)
    methodes["IA + règle de tendance (marché sous sa moyenne 200 jours = « baisse »)"] = np.where(
        np.nan_to_num(tend, nan=0) < 0, 0.0, methodes["IA actuelle"])
    erreurs = []

    def essai(nom, f):
        try:
            methodes[nom] = f()
        except Exception as ex:
            erreurs.append(f"{nom} : {ex}")
            methodes[nom] = np.full(len(O), np.nan)
    essai("Modèle du climat du marché seul (économie, VIX, tendance)", lambda: walk_forward(macro, gbm))
    essai("Combinaison apprise : IA + « mieux que son marché » + climat", lambda: walk_forward(["l_ia", "l_rel"] + macro, lin))
    essai("Combinaison apprise par arbres : IA + marché + climat + titre", lambda: walk_forward(["l_ia", "l_rel"] + macro + titre, gbm))
    # le marché en colonnes 0/1, et l'avis de l'IA croisé avec le marché : la décision peut apprendre
    # que l'IA vaut quelque chose sur un marché et rien sur un autre (ex. les cryptos)
    marches_presents = sorted(O["marche"].dropna().astype(str).unique())
    croises = []
    for m in marches_presents:
        O[f"m_{m}"] = (O["marche"].astype(str) == m).astype(float)
        O[f"ia_x_{m}"] = O["l_ia"] * O[f"m_{m}"]
        croises += [f"m_{m}", f"ia_x_{m}"]
    essai("Décision apprise par marché : IA × marché + climat", lambda: walk_forward(["l_ia", "l_rel"] + croises + macro, lin))

    def seuils_par_marche():
        """Sur les années d'avant, à partir de quelle probabilité de l'IA valait-il mieux dire « hausse » sur ce marché ?"""
        p_cal = methodes["IA actuelle"]
        p = np.array(p_cal, dtype=float)   # par défaut (marché trop récent) : l'avis normal de l'IA
        marche = O["marche"].astype(str).to_numpy()
        for a in sorted(O["_d"].dt.year.unique())[1:]:
            app = (O["_d"] < pd.Timestamp(year=a, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)).to_numpy()
            cib = (O["_d"].dt.year == a).to_numpy()
            for m in marches_presents:
                am, cm = app & (marche == m) & np.isfinite(p_cal), cib & (marche == m) & np.isfinite(p_cal)
                if am.sum() < 300 or not cm.any():
                    continue
                grille = np.unique(np.quantile(p_cal[am], np.linspace(0.02, 0.98, 49)))
                scores = [((p_cal[am] >= g) == (y[am] == 1)).mean() for g in grille]
                g = float(grille[int(np.argmax(scores))])
                p[cm] = np.where(p_cal[cm] >= g, 0.75, 0.25)
        return p
    essai("IA avec un seuil appris pour chaque marché", seuils_par_marche)

    def repere():
        """Repère honnête : sur chaque marché, répondre ce qui arrivait le plus souvent les années d'avant."""
        p = np.where(np.asarray(methodes["IA actuelle"]) >= 0.5, 0.75, 0.25)   # marché trop récent : avis normal
        marche = O["marche"].astype(str).to_numpy()
        for a in sorted(O["_d"].dt.year.unique())[1:]:
            app = (O["_d"] < pd.Timestamp(year=a, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)).to_numpy()
            cib = (O["_d"].dt.year == a).to_numpy()
            for m in marches_presents:
                am, cm = app & (marche == m), cib & (marche == m)
                if am.sum() >= 100 and cm.any():
                    p[cm] = 0.75 if y[am].mean() >= 0.5 else 0.25
        return p
    essai("(Repère) répondre ce qui arrivait le plus souvent sur chaque marché", repere)

    def prudence(p_base):
        """Par marché : là où l'IA n'a pas fait mieux que « toujours la même réponse » les années d'AVANT,
        on donne la tendance habituelle de ce marché (apprise sur ces mêmes années) au lieu de son avis."""
        p = np.array(p_base, dtype=float)
        marche = O["marche"].astype(str).to_numpy()
        for a in sorted(O["_d"].dt.year.unique())[1:]:
            app = (O["_d"] < pd.Timestamp(year=a, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)).to_numpy()
            cib = (O["_d"].dt.year == a).to_numpy()
            for m in np.unique(marche[cib]):
                sel = app & (marche == m) & np.isfinite(p_base)
                if sel.sum() < 300:
                    continue
                hausse_m = float(y[sel].mean())
                acc_m = float(((np.asarray(p_base)[sel] >= 0.5) == (y[sel] == 1)).mean())
                if acc_m <= max(hausse_m, 1 - hausse_m) + 0.005:
                    p[cib & (marche == m)] = 0.9 if hausse_m >= 0.5 else 0.1
        return p
    methodes["IA prudente par marché (tendance habituelle là où l'IA n'a pas fait ses preuves) ← utilisée sur le site"] = prudence(methodes["IA actuelle"])
    methodes["Combinaison apprise + prudence par marché"] = prudence(methodes["Combinaison apprise : IA + « mieux que son marché » + climat"])
    # vote des trois meilleures façons de décider (la majorité l'emporte)
    trio = ["IA prudente par marché (tendance habituelle là où l'IA n'a pas fait ses preuves) ← utilisée sur le site",
            "Combinaison apprise + prudence par marché", "IA avec un seuil appris pour chaque marché"]
    if all(t in methodes for t in trio):
        votes = np.column_stack([np.asarray(methodes[t]) >= 0.5 for t in trio]).sum(axis=1)
        manque = ~np.all(np.column_stack([np.isfinite(methodes[t]) for t in trio]), axis=1)
        methodes["Vote des 3 meilleures méthodes"] = np.where(manque, np.nan, np.where(votes >= 2, 0.75, 0.25))

    # le risque de forte chute (la prévision la plus forte de l'IA) comme indice pour le sens du prix
    def chute_wf():
        from sklearn.ensemble import HistGradientBoostingClassifier as HGB
        yc = (O["rendement_futur"] < -0.10).astype(float).to_numpy()
        vs = [c for c in cols_chute if c in O.columns and O[c].nunique(dropna=True) > 1]
        p = np.full(len(O), np.nan)
        for a_ in sorted(O["_d"].dt.year.unique())[1:]:
            app = (O["_d"] < pd.Timestamp(year=a_, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)).to_numpy()
            cib = (O["_d"].dt.year == a_).to_numpy()
            if app.sum() < 5000 or not cib.any() or len(np.unique(yc[app])) < 2:
                continue
            m = SansColonnesVides(HGB(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=500, random_state=0))
            p[cib] = m.fit(O.loc[app, vs], yc[app]).predict_proba(O.loc[cib, vs])[:, 1]
        return p
    try:
        O["l_chute"] = _logit(np.nan_to_num(chute_wf(), nan=0.084))
        O["l_chute_x_crypto"] = O["l_chute"] * O.get("est_crypto", 0).fillna(0) if "est_crypto" in O else 0.0
        essai("IA + risque de forte chute (combinaison apprise)",
              lambda: walk_forward(["l_ia", "l_chute", "l_chute_x_crypto"] + [c for c in croises if c.startswith("m_")], lin))
        essai("IA prudente + risque de forte chute",
              lambda: walk_forward(["l_ia", "l_chute"] + croises + macro, lin))
    except Exception as ex:
        erreurs.append(f"risque de chute : {ex}")

    # choix automatique, année par année, de la méthode qui a le mieux marché les années d'AVANT (sans regarder l'avenir)
    candidats = {k: np.asarray(v, float) for k, v in methodes.items() if not k.startswith("(")}
    auto = np.full(len(O), np.nan)
    choix_annees = []
    for a_ in sorted(O["_d"].dt.year.unique())[2:]:
        avant = (O["_d"].dt.year < a_).to_numpy()
        cib = (O["_d"].dt.year == a_).to_numpy()
        scores = {}
        for k, v in candidats.items():
            okk = avant & np.isfinite(v)
            if okk.sum() > 5000:
                scores[k] = ((v[okk] >= 0.5) == (y[okk] == 1)).mean()
        if scores:
            best = max(scores, key=scores.get)
            auto[cib] = candidats[best][cib]
            choix_annees.append(f"{a_} : {best.split(' (')[0].split(' ←')[0]}")
    # premières années (rien à comparer avant) : l'avis normal de l'IA
    methodes["Choix automatique de la meilleure méthode, année par année"] = np.where(np.isfinite(auto), auto, candidats["IA actuelle"])

    # MESURE PRÉCISE : sur TOUS les cas des années jamais vues (des dizaines de milliers), pas seulement 5000 tirés au hasard.
    # Avec 5000 cas, la marge d'erreur est d'environ ±70 : deux tests peuvent donner 2793 puis 2753 pour la même méthode.
    ok = np.isfinite(methodes["Combinaison apprise : IA + « mieux que son marché » + climat"])
    for nom, p in methodes.items():
        if not nom.startswith("(") and np.isfinite(p).sum() > 0.5 * ok.sum():
            ok &= np.isfinite(p)
    n = int(ok.sum())
    if n < 500:
        return ["", "4. Recherche de meilleures méthodes : pas assez d'années pour tester sans tricher."]
    yy = y[ok]
    hausse = float(yy.mean())
    ref = max(hausse, 1 - hausse)
    dates_ok = pd.DatetimeIndex(O.loc[ok, "_d"])
    annee = dates_ok.year.to_numpy()
    baisse_ok = np.isin(annee, ANNEES_BAISSE)
    j_ia = (np.asarray(methodes["IA actuelle"])[ok] >= 0.5) == (yy == 1)
    out = ["", "4. OBJECTIF 3000 SUR 5000 : AUTRES FAÇONS DE DÉCIDER",
           f"   Mesuré sur TOUS les cas des années jamais vues : {n:,} cas (ramenés sur 5000 pour comparer). Marge d'erreur : environ ±{round(1.96 * (0.25 / n) ** 0.5 * 5000)}.".replace(",", " "),
           f"   Référence « toujours {'hausse' if hausse >= .5 else 'baisse'} » : {round(ref * 5000)} sur 5000"]
    res = []
    for nom, p in methodes.items():
        pp = np.asarray(p)[ok]
        if not np.isfinite(pp).all():
            out.append(f"   ---- sur 5000 · {nom} (n'a pas pu être testée)")
            continue
        juste = (pp >= 0.5) == (yy == 1)
        k = int(juste.sum())
        part_baisse = float((pp < 0.5).mean())
        jb = float(juste[baisse_ok].mean()) if baisse_ok.any() else None
        juste_baisse = float(juste[pp < 0.5].mean()) if (pp < 0.5).any() else None
        # l'écart avec l'IA actuelle est-il sûr ? (rééchantillonnage par mois : les cas d'un même mois se ressemblent)
        sur = ""
        if nom != "IA actuelle":
            d = pd.DataFrame({"g": juste.astype(float) - j_ia.astype(float)}, index=dates_ok)
            boot = model.bootstrap_mois(d, lambda x: np.array([x["g"].mean()]), graine=21)
            if len(boot):
                lo, hi = np.percentile(boot[:, 0], [2.5, 97.5])
                sur = (" · mieux que l'IA actuelle, de façon sûre" if lo > 0 else
                       " · moins bien que l'IA actuelle, de façon sûre" if hi < 0 else " · écart avec l'IA actuelle pas sûr")
        if not nom.startswith("("):
            res.append((k / n, nom, sur))
        out.append(f"   {round(k / n * 5000):>4} sur 5000 · {nom}"
                   + ("   ✅ objectif 2800 atteint" if k / n * 5000 >= 2799.5 and not nom.startswith("(") else ""))
        out.append(f"        dit « baisse » {pct(part_baisse)} du temps"
                   + (f" (justes quand elle dit « baisse » : {pct(juste_baisse)})" if juste_baisse is not None else "")
                   + (f" · années de baisse : {pct(jb)} justes" if jb is not None else "") + sur)
    if erreurs:
        out.append("   Méthodes en erreur : " + " / ".join(erreurs))
    if choix_annees:
        out.append("   Méthodes choisies automatiquement : " + " · ".join(choix_annees))
    meilleur = max(res)
    out += examen_final(methodes, ok, yy, dates_ok, hausse, [m for m in (meilleur[1], NOM_SITE, "IA actuelle") if m in methodes])
    out.append("")
    if meilleur[1] != "IA actuelle" and "de façon sûre" in meilleur[2] and "mieux" in meilleur[2]:
        out.append(f"   ➜ « {meilleur[1]} » fait mieux que l'IA actuelle de façon sûre ({round(meilleur[0] * 5000)} sur 5000). "
                   "Envoie ce résultat : on l'intègre au site.")
    else:
        out.append(f"   ➜ Meilleure méthode : « {meilleur[1]} » ({round(meilleur[0] * 5000)} sur 5000). "
                   "Aucune ne fait mieux que l'IA actuelle de façon sûre : le sens du prix à un mois reste très dur à prévoir.")
    return out


CHUTE = -0.10   # « forte chute » : perdre plus de 10 % en un mois


def tester_baisses(jeu, oof, variables, horizon):
    """Deux façons honnêtes d'aider à voir venir les baisses, testées année par année sur les seules années d'avant :
    A. un avis « baisse » donné seulement là où, par le passé, il a eu raison au moins 55 fois sur 100 ;
    B. un détecteur du risque de forte chute (plus de 10 % en un mois), plus prévisible que le sens du prix."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from bourse_bot import comprendre as C
    out = ["", "5. PRÉVOIR LES BAISSES"]
    d = pd.to_datetime(oof.index)
    y = oof["cible"].to_numpy()
    annees = sorted(d.year.unique())
    # A. avis « baisse » prouvé : seuil appris sur les années d'avant (précision ≥ 55 %, au moins 200 cas)
    pc = np.full(len(oof), np.nan)
    dit_baisse = np.zeros(len(oof), dtype=bool)
    for a_ in annees[1:]:
        app = d < pd.Timestamp(year=a_, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)
        cib = d.year == a_
        if app.sum() < 3000:
            continue
        cal = model.CalibrationPlatt().fit(oof.loc[app, "proba"], y[app])
        p_app = cal.predict(oof.loc[app, "proba"].to_numpy())
        pc[cib] = cal.predict(oof.loc[cib, "proba"].to_numpy())
        seuil = None
        for s_ in np.quantile(p_app, np.linspace(0.005, 0.30, 60)):
            sel = p_app <= s_
            if sel.sum() >= 200 and (y[app][sel] == 0).mean() >= 0.55:
                seuil = s_   # le plus haut seuil (donc le plus de cas) qui garde 55 % de réussite
        if seuil is not None:
            dit_baisse[cib] = pc[cib] <= seuil
    ok = np.isfinite(pc)
    nb = int(dit_baisse[ok].sum())
    if nb:
        juste = float((y[ok][dit_baisse[ok]] == 0).mean())
        lo, hi = model.wilson(int((y[ok][dit_baisse[ok]] == 0).sum()), nb)
        nb_txt = f"{nb:,}".replace(",", " ")
        out += [f"A. Avis « baisse » prouvé : l'IA dit « baisse » dans {pct(nb / ok.sum())} des cas ({nb_txt} fois),",
                f"   et elle a raison {pct(juste)} de ces fois-là (marge {pct(lo)} à {pct(hi)}). Habituellement, ça baisse {pct(1 - y[ok].mean())} du temps.",
                "   " + ("Verdict : ses « baisse » valent mieux que le hasard, de façon sûre." if lo > 0.5 else
                         "Verdict : pas assez sûr pour l'utiliser.")]
        # C. et si les avis très pessimistes annonçaient plutôt des REBONDS ? On vérifie année par année avant d'y croire.
        sel = ok & dit_baisse
        if sel.sum() >= 300:
            dd = pd.DataFrame({"monte": (y[sel] == 1).astype(float)}, index=d[sel])
            boot = model.bootstrap_mois(dd, lambda x: np.array([x["monte"].mean()]), graine=23)
            lo_r, hi_r = (np.percentile(boot[:, 0], [2.5, 97.5]) if len(boot) else (np.nan, np.nan))
            base_h = float(y[ok].mean())
            par_an = dd.groupby(dd.index.year)["monte"].agg(["count", "mean"])
            an_txt = " · ".join(f"{a_} : {int(r_['count'])} cas, {round(r_['mean'] * 100)} % de hausse" for a_, r_ in par_an.iterrows())
            nb_ans_bons = int(((par_an["mean"] > base_h) & (par_an["count"] >= 30)).sum())
            nb_ans = int((par_an["count"] >= 30).sum())
            out += ["", "C. Et si ces avis très pessimistes annonçaient plutôt un REBOND ?",
                    f"   Après ces avis, le prix a monté {pct(float(dd['monte'].mean()))} du temps (d'habitude {pct(base_h)}),",
                    f"   marge en tenant compte des mois qui se ressemblent : {pct(lo_r)} à {pct(hi_r)}.",
                    f"   Année par année : {an_txt}",
                    "   " + ("Verdict : pas d'effet rebond, le prix a même plutôt moins monté que d'habitude."
                             if float(dd["monte"].mean()) <= base_h else
                             "Verdict : effet rebond régulier sur plusieurs années, piste sérieuse à tester sur le site."
                             if lo_r > base_h and nb_ans >= 4 and nb_ans_bons >= 0.75 * nb_ans else
                             "Verdict : l'effet vient surtout de quelques mois exceptionnels (comme un krach suivi d'un rebond) : "
                             "pas assez régulier pour s'en servir.")]
    else:
        out += ["A. Avis « baisse » prouvé : sur les années passées, aucun seuil n'a donné 55 % de « baisse » justes. L'IA ne doit pas dire « baisse »."]
    # B. risque de forte chute (> 10 % en un mois)
    et = jeu.dropna(subset=["rendement_futur"]).copy()
    et["chute"] = (et["rendement_futur"] < CHUTE).astype(float)
    vs = C._variables_chute(et, variables)
    de = pd.to_datetime(et.index)
    p = np.full(len(et), np.nan)
    for a_ in sorted(de.year.unique())[1:]:
        app = (de < pd.Timestamp(year=a_, month=1, day=1) - pd.Timedelta(days=horizon * 1.5))
        cib = de.year == a_
        if app.sum() < 5000 or et.loc[app, "chute"].nunique() < 2:
            continue
        m = C.SansColonnesVides(HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                               min_samples_leaf=500, random_state=0))
        m.fit(et.loc[app, vs], et.loc[app, "chute"].to_numpy())
        p[cib] = m.predict_proba(et.loc[cib, vs])[:, 1]
    okb = np.isfinite(p)
    if okb.sum() > 2000:
        yc, pp = et["chute"].to_numpy()[okb], p[okb]
        base = float(yc.mean())
        haut = pp >= np.quantile(pp, 0.9)
        bas = pp <= np.quantile(pp, 0.5)
        auc = model._auc(yc, pp)
        n_txt = f"{int(okb.sum()):,}".replace(",", " ")
        out += ["", f"B. Risque de forte chute (plus de 10 % en un mois), sur {n_txt} cas :",
                f"   Habituellement, une forte chute arrive {pct(base)} du temps.",
                f"   Quand l'IA annonce les risques les plus élevés (10 % des cas) : elle arrive {pct(float(yc[haut].mean()))} du temps.",
                f"   Quand l'IA annonce un risque faible (la moitié des cas) : {pct(float(yc[bas].mean()))} du temps.",
                f"   Note de tri (0,5 = hasard, 1 = parfait) : {auc:.3f}".replace(".", ","),
                "   " + ("Verdict : l'IA repère bien les titres les plus exposés à une forte chute." if auc > 0.6 else
                         "Verdict : utile mais limité." if auc > 0.55 else "Verdict : pas mieux que le hasard.")]
    return out


SCORES = {}
SEUILS_ALERTE = {"direction": 80, "mieux_que_marche": 80, "agitation_mois": 80, "agitation_semaine_pct": 1.0,
                 "chute_note": 0.02, "brier_gain_pct": 0.5}


def suivi_scores(texte: str) -> list:
    """Version 49 : garde les notes de chaque test dans rapports/historique_tests.csv et prévient si une note baisse
    nettement par rapport au test précédent (au-delà du bruit habituel d'un tirage à l'autre)."""
    import re as _re
    def nb(m, i=1):
        return float(m.group(i).replace(",", ".").replace(" ", "")) if m else None
    s = dict(SCORES)
    s["direction"] = nb(_re.search(r"1\. LE SENS DU PRIX.*?raison (\d+) fois sur", texte, _re.S))
    s["mieux_que_marche"] = nb(_re.search(r"2\. FAIRE MIEUX.*?raison (\d+) fois sur", texte, _re.S))
    s["agitation_mois"] = nb(_re.search(r"3\. L'AGITATION.*?simple[^\d]*(\d+) fois sur", texte, _re.S))
    s["agitation_semaine_pct"] = nb(_re.search(r"3 bis\..*?dans ([\d,]+) % des cas", texte, _re.S))
    s["chute_note"] = nb(_re.search(r"Note de tri[^:]*: ([\d,]+)", texte))
    s["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    chemin = os.path.join("rapports", "historique_tests.csv")
    avant = None
    try:
        h = pd.read_csv(chemin)
        avant = h.iloc[-1].to_dict() if len(h) else None
    except Exception:
        h = pd.DataFrame()
    pd.concat([h, pd.DataFrame([s])], ignore_index=True).to_csv(chemin, index=False)
    if not avant:
        return ["", "Suivi dans le temps : premier test enregistré (rapports/historique_tests.csv). Le prochain sera comparé à celui-ci."]
    noms = {"direction": "sens du prix (sur 5000)", "mieux_que_marche": "mieux que son marché (sur 5000)",
            "agitation_mois": "agitation à un mois (sur 5000)", "agitation_semaine_pct": "agitation sur une semaine (%)",
            "chute_note": "risque de chute (note de tri)", "brier_gain_pct": "gain du score de Brier (%)"}
    out = ["", f"Suivi dans le temps (comparé au test du {avant.get('date', '?')}) :"]
    alerte = False
    for k, lib in noms.items():
        a, b = avant.get(k), s.get(k)
        if a is None or b is None or a != a or b != b:
            continue
        baisse = (a - b) > SEUILS_ALERTE[k]
        alerte |= baisse
        out.append(f"  {lib:<34} {a:g} → {b:g}" + ("   ⚠ BAISSE NETTE" if baisse else ""))
    out.append("  ⚠ Au moins une note a nettement baissé : envoie ce rapport pour qu'on regarde." if alerte
               else "  Aucune baisse au-delà du bruit habituel.")
    return out


def lancer(nb_cas: int, demo: bool) -> int:
    data.DEMO = demo
    horizon = config.HORIZON_PREDICTION
    print("1/4 Téléchargement des cours (actions, ETF, cryptos)…")
    noms, marche_de = radar._univers(radar.TOUS_MARCHES)
    donnees, bruts = radar._preparer(noms, marche_de)
    supp = bruts.pop("__apprentissage__", {})
    tous = {**supp, **donnees}
    if len(tous) < 20:
        print("Trop peu de données reçues (Yahoo bloque peut-être). Réessaie dans une heure.")
        return 1
    marches = {t: ("crypto" if t.endswith("-USD") else marche_de.get(t, "us")) for t in tous}

    print("2/4 Préparation des situations passées…")
    jeu = model.construire_jeu(tous, marches, horizon)

    # la recette actuellement utilisée par le site
    configs = {c[0]: c for c in model.configs_disponibles()}
    fichier = model._lire_fichier_modele() or {}
    nom = fichier.get("configuration") if fichier.get("configuration") in configs else "Un seul modèle, indicateurs de base"
    nom, variables, par_marche, params = configs.get(nom) or configs["Un seul modèle, indicateurs de base"]
    marge = (((fichier.get("evaluation") or {}).get("avis_net")) or {}).get("marge")
    print(f"3/4 L'IA s'entraîne sur le passé puis prévoit des mois jamais vus (recette : {nom})…")
    oof = model.predictions_hors_echantillon(jeu, horizon, variables, par_marche, params=params, garder_ticker=True)
    if oof is None or len(oof) < 1000:
        print("Pas assez de prévisions pour faire le test.")
        return 1

    print(f"4/4 Tirage de {nb_cas} cas au hasard et vérification…\n")
    rng = np.random.default_rng(int(datetime.now().strftime("%Y%m%d")))
    n = min(nb_cas, len(oof))
    idx = rng.choice(len(oof), size=n, replace=False)
    masque = np.zeros(len(oof), dtype=bool)
    masque[idx] = True
    test, reste = oof[masque].copy(), oof[~masque]
    # calibration apprise sur les AUTRES cas seulement (comme sur le site, sans tricher)
    calib = model.CalibrationPlatt().fit(reste["proba"], reste["cible"])
    test["p"] = calib.predict(test["proba"].to_numpy())
    test["juste"] = (test["p"] >= 0.5) == (test["cible"] == 1)
    hausse = float(test["cible"].mean())
    ref = max(hausse, 1 - hausse)
    justes = int(test["juste"].sum())

    lignes = [f"TEST DE L'IA SUR {n} CAS TIRÉS AU HASARD ({'données FICTIVES de démo : résultats sans valeur' if demo else 'vrais cours'})",
              f"Fait le {datetime.now():%d/%m/%Y à %H:%M} · recette : {nom}",
              f"Période des cas : {test.index.min():%m/%Y} à {test.index.max():%m/%Y} (des mois que l'IA n'avait jamais vus)",
              "",
              "1. LE SENS DU PRIX (plus haut ou plus bas dans un mois ?)",
              f"➜ L'IA a eu raison {justes} fois sur {n} : {pct(justes / n)}",
              f"  Référence naïve (répondre toujours « {'hausse' if hausse >= .5 else 'baisse'} ») : {pct(ref)}",
              f"  Écart : {'+' if justes / n >= ref else ''}{(justes / n - ref) * 100:.1f}".replace(".", ",") + " point(s)",
              ""]
    # marge d'erreur approximative (95 %)
    lo, hi = model.wilson(justes, n)
    lignes.append(f"  Marge d'erreur : le vrai taux est probablement entre {pct(lo)} et {pct(hi)}.")
    lignes.append("  " + ("Verdict : mieux que la référence, même en comptant la marge d'erreur." if lo > ref else
                          "Verdict : pas de différence sûre avec la référence naïve. Deviner la direction est très dur." if hi >= ref else
                          "Verdict : moins bien que la référence naïve sur ces cas."))
    if marge is not None:
        nets = test[(test["p"] - 0.5).abs() >= marge]
        if len(nets) >= 50:
            h2 = float(nets["cible"].mean())
            lignes += ["", f"Quand l'IA avait un avis net (au moins {round((0.5 + marge) * 100)} % ou au plus {round((0.5 - marge) * 100)} %) : "
                       f"{len(nets)} cas, {pct(float(nets['juste'].mean()))} de bonnes réponses "
                       f"(référence sur ces cas : {pct(max(h2, 1 - h2))})."]
    # ---- Notes de pro (version 49) : la qualité des probabilités, pas seulement le % de bonnes réponses
    try:
        p_, y_ = test["p"].to_numpy(), test["cible"].to_numpy()
        base = float(reste["cible"].mean())
        brier, brier_ref = float(np.mean((p_ - y_) ** 2)), float(np.mean((base - y_) ** 2))
        bins = pd.qcut(p_, 10, labels=False, duplicates="drop")
        dd = pd.DataFrame({"p": p_, "y": y_, "k": bins}).groupby("k").agg(p=("p", "mean"), y=("y", "mean"), n=("y", "size"))
        ece = float(np.average(np.abs(dd["p"] - dd["y"]), weights=dd["n"]))
        # version 53 : écart attendu par le seul hasard si l'IA était parfaitement calibrée (groupes de taille finie)
        bruit = float(np.average(np.sqrt(2 / np.pi) * np.sqrt(dd["p"] * (1 - dd["p"]) / dd["n"]), weights=dd["n"]))
        lignes += ["", "Notes de pro (qualité des probabilités annoncées) :",
                   f"  Score de Brier : IA {brier:.4f} · référence « taux habituel » {brier_ref:.4f} · "
                   f"gain {(1 - brier / brier_ref) * 100:+.2f} % (au-dessus de 0 = mieux que la référence)".replace(".", ","),
                   f"  Écart moyen entre probabilité annoncée et fréquence réelle : {ece * 100:.1f} point(s), "
                   f"dont environ {bruit * 100:.1f} dû au seul hasard des 5000 cas".replace(".", ",")
                   + (" (bien calibrée)" if ece < bruit + .01 else " (à surveiller)")]
        SCORES["brier_gain_pct"] = round((1 - brier / brier_ref) * 100, 3)
        SCORES["ecart_calibration_pt"] = round(ece * 100, 2)
    except Exception:
        pass
    # version 53 : on signale les marchés où le SITE n'affiche pas l'avis brut de l'IA (prudence par marché)
    try:
        from bourse_bot import comprendre as _C
        _col = "p" if "p" in reste else "proba"
        _prud = _C.prudence_par_marche(reste[["cible", "marche"]].assign(proba=reste[_col].to_numpy()))
    except Exception:
        _prud = {}
    lignes += ["", "Par marché (avis BRUT de l'IA, avant le garde-fou du site) :"]
    for m, g in test.groupby("marche"):
        if len(g) >= 30:
            hm = float(g["cible"].mean())
            lignes.append(f"  {NOMS.get(m, m):<22} {len(g):>5} cas · justes {pct(float(g['juste'].mean()))} · référence {pct(max(hm, 1 - hm))}"
                          + ("  → sur le site : tendance habituelle affichée à la place" if m in _prud else ""))
    if _prud:
        lignes.append("  (Là où l'IA n'a pas fait mieux que la tendance habituelle, le site affiche cette tendance : c'est la méthode "
                      "« IA prudente par marché » mesurée plus bas.)")
    lignes += ["", "Par année :"]
    for an, g in test.groupby(test.index.year):
        if len(g) >= 30:
            ha = float(g["cible"].mean())
            lignes.append(f"  {an}  {len(g):>5} cas · justes {pct(float(g['juste'].mean()))} · référence {pct(max(ha, 1 - ha))}")
    # ---------------- 2. « Mieux que son marché » : la même question, mais contre son indice ----------------
    print("   + test « mieux que son marché »…", flush=True)
    try:
        rel = model.predictions_hors_echantillon(model._jeu_relatif(jeu), horizon, variables, par_marche, garder_ticker=True)
    except Exception:
        rel = None
    if rel is not None and len(rel) > 1000:
        k = min(nb_cas, len(rel))
        m2 = np.zeros(len(rel), dtype=bool)
        m2[rng.choice(len(rel), size=k, replace=False)] = True
        tr, rr = rel[m2].copy(), rel[~m2]
        tr["p"] = model.CalibrationPlatt().fit(rr["proba"], rr["cible"]).predict(tr["proba"].to_numpy())
        tr["juste"] = (tr["p"] >= 0.5) == (tr["cible"] == 1)
        hr = float(tr["cible"].mean())
        jr = int(tr["juste"].sum())
        lo2, hi2 = model.wilson(jr, k)
        lignes += ["", "2. FAIRE MIEUX QUE SON MARCHÉ (CAC 40, S&P 500, Bitcoin…)",
                   f"➜ L'IA a eu raison {jr} fois sur {k} : {pct(jr / k)}  (référence naïve : {pct(max(hr, 1 - hr))}, "
                   f"marge {pct(lo2)} à {pct(hi2)})",
                   "  " + ("Verdict : mieux que la référence, même en comptant la marge d'erreur." if lo2 > max(hr, 1 - hr) else
                           "Verdict : pas de différence sûre avec la référence.")]
        # version 33 : la même question avec les indicateurs « comparés entre titres du jour », sur TOUS les cas
        try:
            print("   + test « mieux que son marché », version comparée…", flush=True)
            relc = model.predictions_hors_echantillon(model._jeu_relatif(jeu), horizon, variables, par_marche,
                                                      params={"rangs_jour": True}, garder_ticker=True)
            if relc is not None and len(relc) == len(rel):
                def taux_wf(o):
                    """bonnes réponses sur tous les cas, recalage appris année par année sur les seules années d'avant"""
                    d = pd.to_datetime(o.index)
                    yv, p = o["cible"].to_numpy(), np.full(len(o), np.nan)
                    for a_ in sorted(d.year.unique())[1:]:
                        app = d < pd.Timestamp(year=a_, month=1, day=1) - pd.Timedelta(days=horizon * 1.5)
                        cib = d.year == a_
                        if app.sum() >= 3000:
                            p[cib] = model.CalibrationPlatt().fit(o.loc[app, "proba"], yv[app]).predict(o.loc[cib, "proba"].to_numpy())
                    okk = np.isfinite(p)
                    return float(((p[okk] >= 0.5) == (yv[okk] == 1)).mean()), int(okk.sum())
                t1, n1 = taux_wf(rel)
                t2, _ = taux_wf(relc)
                lignes += [f"  Sur TOUS les cas ({n1:,}) : version actuelle {round(t1 * 5000)} sur 5000 · version « comparée entre titres » "
                           f"{round(t2 * 5000)} sur 5000".replace(",", " ")
                           + (" ← la version comparée fait mieux" if t2 > t1 + 0.002 else "")]
        except Exception as e:
            lignes += [f"  (version comparée non testée : {e})"]
    # ---------------- 3. L'agitation : de combien le prix va bouger ----------------
    print("   + test de l'agitation prévue…", flush=True)
    try:
        from bourse_bot import comprendre as C
        et = jeu.dropna(subset=["vol_futur", "vol_20j"])
        et = et[np.isfinite(et["vol_futur"])]
        vs = C._variables_risque(et, variables)
        morceaux = []
        for train, tst in model._plis(et.assign(cible=0.0), horizon, 5):
            if len(train) < 3000 or tst.empty:
                continue
            mod = C._modele().fit(train[vs], train["vol_futur"])
            morceaux.append(pd.DataFrame({"y": tst["vol_futur"].to_numpy(), "p": mod.predict(tst[vs]),
                                          "naif": C._naif(tst).to_numpy()}, index=tst.index))
        ag = pd.concat(morceaux) if morceaux else None
    except Exception as ex:
        ag = None
        lignes += ["", f"3. L'AGITATION : test impossible cette fois ({ex})"]
    if ag is not None:
        ag = ag[np.isfinite(ag[["y", "p", "naif"]]).all(axis=1)]
        ag = ag[ag["y"] > np.log(0.02)]   # cours figés (titre retiré de la cote) : agitation nulle, comparaison absurde
        k = min(nb_cas, len(ag))
        ag = ag.iloc[rng.choice(len(ag), size=k, replace=False)]
        e_ia = (np.exp(ag["p"] - ag["y"]) - 1).abs()
        e_nf = (np.exp(ag["naif"] - ag["y"]) - 1).abs()
        mieux = int((e_ia < e_nf).sum())
        lo3, hi3 = model.wilson(mieux, k)
        lignes += ["", "3. L'AGITATION (de combien le prix va bouger le mois suivant, dans un sens ou dans l'autre)",
                   f"➜ L'IA a été plus proche de la réalité que la méthode simple (« comme le mois dernier ») {mieux} fois sur {k} "
                   f"({pct(mieux / k)}, marge {pct(lo3)} à {pct(hi3)})",
                   f"  Erreur habituelle (médiane) : IA {pct(float(e_ia.median()))} · méthode simple {pct(float(e_nf.median()))}",
                   "  " + ("Verdict : l'IA fait mieux que la méthode simple, de façon sûre." if lo3 > .5 and e_ia.median() < e_nf.median() else
                           "Verdict : pas de différence sûre avec la méthode simple.")]
    print("   + test de l'agitation sur une semaine…", flush=True)
    try:
        lignes += tester_semaine(tous)
    except Exception as e:
        lignes += ["", f"3 bis. Agitation sur une semaine : impossible cette fois ({e})"]
    # ---------------- 4. Objectif 3000 sur 5000 : d'autres façons de décider « hausse » ou « baisse » ----------------
    print("   + recherche de meilleures méthodes pour le sens du prix…", flush=True)
    try:
        lignes += explorer(jeu, oof, rel, masque, horizon)
    except Exception as e:
        lignes += ["", f"4. Recherche de meilleures méthodes : impossible cette fois ({e})"]
    # ---------------- 5. Prévoir les baisses ----------------
    print("   + test des baisses (avis « baisse » prouvé, risque de forte chute)…", flush=True)
    try:
        lignes += tester_baisses(jeu, oof, variables, horizon)
    except Exception as e:
        lignes += ["", f"5. Prévoir les baisses : impossible cette fois ({e})"]
    ex = test.sample(min(8, len(test)), random_state=1)
    lignes += ["", "Quelques cas au hasard :"]
    for d, r in ex.iterrows():
        p_txt = f"{r['p'] * 100:.1f}".replace(".", ",")
        reel = f"{r['rendement_futur'] * 100:+.1f}".replace(".", ",")
        tk = str(r.get("ticker", ""))
        lignes.append(f"  {d:%d/%m/%Y} {tk:<12} IA : {p_txt} % de hausse, donc « {'hausse' if r['p'] >= .5 else 'baisse'} » · "
                      f"réel : {reel} % · {'juste' if r['juste'] else 'faux'}")
    try:
        if not demo:
            lignes += suivi_scores("\n".join(lignes))
    except Exception as e:
        lignes += ["", f"Suivi dans le temps : impossible cette fois ({e})"]
    lignes += ["", "Rappel : une prévision à 60 % se trompe 4 fois sur 10 par définition. Ce test ne garantit rien pour l'avenir."]
    texte = "\n".join(lignes)
    print(texte)
    os.makedirs("rapports", exist_ok=True)
    chemin = os.path.join("rapports", f"test_ia_{n}_cas_{datetime.now():%Y%m%d_%H%M}.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte + "\n")
    print(f"\n📄 Résultat enregistré dans {chemin} (sur ce PC uniquement).")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Teste l'IA du radar sur des cas réels jamais vus.")
    p.add_argument("--cas", type=int, default=5000)
    p.add_argument("--demo", action="store_true")
    a = p.parse_args()
    try:
        sys.exit(lancer(a.cas, a.demo))
    except KeyboardInterrupt:
        sys.exit(1)
