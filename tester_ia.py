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

import numpy as np
import pandas as pd

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
    cols = [c for c in MACRO + TITRE if c in jeu.columns]
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
    test = masque.copy()

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
    gbm = lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=500, random_state=0)
    macro = [c for c in MACRO if c in O.columns and O[c].nunique(dropna=True) > 1]
    titre = [c for c in TITRE if c in O.columns and O[c].nunique(dropna=True) > 1]
    reste = O.loc[~test]
    calib = model.CalibrationPlatt().fit(reste["proba"], reste["cible"])
    methodes = {"IA actuelle": calib.predict(O["proba"].to_numpy())}
    tend = O["marche_tendance"].to_numpy() if "marche_tendance" in O else np.full(len(O), np.nan)
    methodes["IA + règle de tendance (marché sous sa moyenne 200 jours = « baisse »)"] = np.where(
        np.nan_to_num(tend, nan=0) < 0, 0.0, methodes["IA actuelle"])
    methodes["Modèle du climat du marché seul (économie, VIX, tendance)"] = walk_forward(macro, gbm)
    methodes["Combinaison apprise : IA + « mieux que son marché » + climat"] = walk_forward(["l_ia", "l_rel"] + macro, lin)
    methodes["Combinaison apprise par arbres : IA + marché + climat + titre"] = walk_forward(["l_ia", "l_rel"] + macro + titre, gbm)

    ok = test & np.isfinite(methodes["Combinaison apprise : IA + « mieux que son marché » + climat"])
    n = int(ok.sum())
    if n < 500:
        return ["", "4. Recherche de meilleures méthodes : pas assez d'années pour tester sans tricher."]
    yy = y[ok]
    hausse = float(yy.mean())
    ref = max(hausse, 1 - hausse)
    annee = O.loc[ok, "_d"].dt.year.to_numpy()
    baisse_ok = np.isin(annee, ANNEES_BAISSE)
    out = ["", f"4. OBJECTIF 3000 SUR 5000 : AUTRES FAÇONS DE DÉCIDER (sur les mêmes {n} cas, ramenés sur 5000)",
           f"   Référence « toujours {'hausse' if hausse >= .5 else 'baisse'} » : {round(ref * 5000)} sur 5000"]
    res = []
    for nom, p in methodes.items():
        pp = p[ok]
        juste = (pp >= 0.5) == (yy == 1)
        k = int(juste.sum())
        lo, hi = model.wilson(k, n)
        part_baisse = float((pp < 0.5).mean())
        jb = float(juste[baisse_ok].mean()) if baisse_ok.any() else None
        res.append((k / n, nom))
        out.append(f"   {round(k / n * 5000):>4} sur 5000 · {nom}")
        out.append(f"        dit « baisse » {pct(part_baisse)} du temps · marge {round(lo * 5000)} à {round(hi * 5000)}"
                   + (f" · années de baisse (2008, 2011, 2015, 2018, 2020, 2022) : {pct(jb)} justes" if jb is not None else ""))
    meilleur = max(res)
    act = res[0][0]
    out.append("")
    if meilleur[1] != "IA actuelle" and meilleur[0] > act + 0.01:
        out.append(f"   ➜ Piste à creuser : « {meilleur[1]} » fait {round((meilleur[0] - act) * 5000)} bonnes réponses de plus que l'IA actuelle. "
                   "Envoie ce résultat : si l'écart tient, on l'intègre au site.")
    else:
        out.append("   ➜ Aucune méthode ne fait nettement mieux que l'IA actuelle sur ces cas : le sens du prix à un mois reste très dur à prévoir.")
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
    lignes += ["", "Par marché :"]
    for m, g in test.groupby("marche"):
        if len(g) >= 30:
            hm = float(g["cible"].mean())
            lignes.append(f"  {NOMS.get(m, m):<22} {len(g):>5} cas · justes {pct(float(g['juste'].mean()))} · référence {pct(max(hm, 1 - hm))}")
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
    except Exception:
        ag = None
    if ag is not None:
        ag = ag[np.isfinite(ag[["y", "p", "naif"]]).all(axis=1)]
        k = min(nb_cas, len(ag))
        ag = ag.iloc[rng.choice(len(ag), size=k, replace=False)]
        e_ia = (np.exp(ag["p"] - ag["y"]) - 1).abs()
        e_nf = (np.exp(ag["naif"] - ag["y"]) - 1).abs()
        mieux = int((e_ia < e_nf).sum())
        lo3, hi3 = model.wilson(mieux, k)
        lignes += ["", "3. L'AGITATION (de combien le prix va bouger le mois suivant, dans un sens ou dans l'autre)",
                   f"➜ Erreur moyenne de l'IA : {pct(float(e_ia.mean()))} · méthode simple (« comme le mois dernier ») : {pct(float(e_nf.mean()))}",
                   f"  L'IA a été plus proche de la réalité que la méthode simple {mieux} fois sur {k} ({pct(mieux / k)}, marge {pct(lo3)} à {pct(hi3)})",
                   "  " + ("Verdict : l'IA fait mieux que la méthode simple, de façon sûre." if lo3 > .5 and e_ia.mean() < e_nf.mean() else
                           "Verdict : pas de différence sûre avec la méthode simple.")]
    # ---------------- 4. Objectif 3000 sur 5000 : d'autres façons de décider « hausse » ou « baisse » ----------------
    print("   + recherche de meilleures méthodes pour le sens du prix…", flush=True)
    try:
        lignes += explorer(jeu, oof, rel, masque, horizon)
    except Exception as e:
        lignes += ["", f"4. Recherche de meilleures méthodes : impossible cette fois ({e})"]
    ex = test.sample(min(8, len(test)), random_state=1)
    lignes += ["", "Quelques cas au hasard :"]
    for d, r in ex.iterrows():
        p_txt = f"{r['p'] * 100:.1f}".replace(".", ",")
        reel = f"{r['rendement_futur'] * 100:+.1f}".replace(".", ",")
        tk = str(r.get("ticker", ""))
        lignes.append(f"  {d:%d/%m/%Y} {tk:<12} IA : {p_txt} % de hausse, donc « {'hausse' if r['p'] >= .5 else 'baisse'} » · "
                      f"réel : {reel} % · {'juste' if r['juste'] else 'faux'}")
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
