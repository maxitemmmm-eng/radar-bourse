"""Test de l'IA sur 5000 cas réels tirés au hasard.

Ce test télécharge les vrais cours, entraîne l'IA du site uniquement sur le PASSÉ de chaque période,
puis lui fait prévoir des mois qu'elle n'a jamais vus. On tire ensuite 5000 cas au hasard parmi ces
prévisions et on compte combien de fois elle a eu raison (le prix a-t-il fini plus haut ou plus bas un mois après ?).

Le résultat est comparé à la « référence naïve » : répondre toujours la même chose (par exemple « hausse »).
Faire mieux que ça, c'est ça qui compte.

Lancement : double-clique sur tester_ia.bat   (ou : python tester_ia.py)
Options : --cas 5000 (nombre de cas)   --demo (essai avec des données fictives)
Durée : 5 à 15 minutes selon le PC. Rien n'est envoyé sur Internet : le rapport reste dans « rapports ».
"""
from __future__ import annotations

import argparse
import json
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
