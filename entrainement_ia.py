"""Entraînement approfondi de l'IA de Radar Bourse (à lancer sur ton PC).

Double-clique sur entrainement_ia.bat. Le script :
  1. télécharge beaucoup plus de données que les mises à jour en ligne : jusqu'à 20 ans d'historique,
     plusieurs centaines d'actions, d'ETF et de cryptos, et des indicateurs économiques (taux, courbe
     des taux, pétrole, cuivre, prime de risque du crédit, tension financière, chômage) ;
  2. fait passer un examen aux IA : chaque façon de prévoir est testée uniquement sur des années
     qu'elle n'a jamais vues (validation « walk-forward ») ;
  3. compare la meilleure à celle qui tourne aujourd'hui sur ton site. Elle ne la remplace QUE si elle
     fait mieux de façon prouvée (marge d'erreur à 95 %, en tirant des mois entiers au hasard) ;
  4. écrit un rapport clair (dossier « rapports ») et, si l'IA a vraiment progressé, envoie la nouvelle
     recette sur GitHub : le site se met à jour tout seul avec elle.

Options : --complet (plus de réglages testés, plus long), --sans-publier (rapport seulement),
--demo (données fictives, pour tester le script).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from datetime import datetime

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
sys.path.insert(0, ICI)

# Titres supplémentaires pour l'entraînement (beaucoup de situations différentes = IA plus robuste)
UNIVERS_ETENDU = {
    "us": ["MA", "ACN", "TMO", "ABT", "DHR", "LIN", "NEE", "PM", "MO", "RTX", "DE", "MMM", "LOW", "TGT", "BKNG",
           "ADP", "INTU", "NOW", "ISRG", "AMGN", "GILD", "MDT", "BMY", "CVS", "CI", "ELV", "SCHW", "BLK", "AXP",
           "C", "USB", "PNC", "SPGI", "CME", "ICE", "MCO", "DUK", "SO", "D", "AEP", "EXC", "SLB", "EOG", "OXY",
           "PSX", "MPC", "F", "GM", "CMCSA", "TMUS", "EA", "ADI", "LRCX", "KLAC", "SNPS", "CDNS", "MRVL",
           "PANW", "ZTS", "SYK", "BDX", "REGN", "VRTX", "FDX", "CSX", "UNP", "NSC", "WM", "ECL", "APD", "SHW",
           "KMB", "CL", "GIS", "MDLZ", "HSY", "STZ",
           "EEM", "EFA", "TLT", "IWM", "XLF", "XLK", "XLV", "XLY", "XLP", "XLI", "XLU", "VNQ", "GDX"],
    "eu": ["DBK.DE", "IFX.DE", "VOW3.DE", "DHL.DE", "RWE.DE", "EOAN.DE", "HEN3.DE", "BEI.DE", "DB1.DE",
           "HNR1.DE", "MRK.DE", "HEIA.AS", "KPN.AS", "WKL.AS", "NN.AS", "ABI.BR", "KBC.BR", "UCB.BR",
           "NOKIA.HE", "NESTE.HE", "TEF.MC", "REP.MC", "AMS.MC", "CABK.MC", "ENI.MI", "G.MI", "PRY.MI",
           "NOVO-B.CO", "NESN.SW", "ROG.SW", "NOVN.SW", "UBSG.SW"],
    "fr": ["RNO.PA", "ALO.PA", "BVI.PA", "ERF.PA", "URW.PA", "AC.PA", "TEP.PA", "SW.PA", "FGR.PA", "HO.PA",
           "AMUN.PA", "GET.PA"],
    "crypto": ["AAVE-USD", "XMR-USD", "VET-USD", "ICP-USD", "EOS-USD", "XTZ-USD", "MANA-USD", "SAND-USD",
               "THETA-USD", "CRO-USD", "NEO-USD", "ZEC-USD", "DASH-USD", "KSM-USD"],
}


def titre(texte):
    print("\n" + "━" * 64 + f"\n {texte}\n" + "━" * 64, flush=True)


def info(texte):
    print("   " + texte, flush=True)


def duree(secondes):
    m = int(secondes // 60)
    return f"{m} min {int(secondes % 60)} s" if m else f"{int(secondes)} s"


def verifier_dependances():
    try:
        import numpy, pandas, sklearn, yfinance  # noqa: F401
    except ImportError:
        info("Installation des outils nécessaires (une seule fois)…")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", os.path.join(ICI, "requirements.txt")], check=False)


def trouver(nom):
    chemin = shutil.which(nom)
    if chemin:
        return chemin
    for c in (rf"C:\Program Files\Git\cmd\{nom}.exe", rf"C:\Program Files\GitHub CLI\{nom}.exe",
              os.path.expandvars(rf"%LOCALAPPDATA%\Programs\Git\cmd\{nom}.exe")):
        if os.path.exists(c):
            return c
    return None


def git(*args, ok=(0,)):
    g = trouver("git")
    if not g:
        return 1, "git introuvable"
    r = subprocess.run([g, *args], cwd=ICI, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


# ----------------------------------------------------------------------------
def preparer_donnees(args):
    from bourse_bot import config, data, indicators
    noms = {}
    marche_de = {}
    for m, univers in config.UNIVERS.items():
        for t in univers:
            noms[t], marche_de[t] = univers[t], m
    base = config.entrainement_supplementaire()
    etendu = {m: [t for t in v if t not in noms] for m, v in UNIVERS_ETENDU.items()}
    tout_base = {t: m for m, v in base.items() for t in v if t not in noms}
    tout_etendu = {t: m for m, v in etendu.items() for t in v if t not in noms and t not in tout_base}
    a_telecharger = list(noms) + list(tout_base) + list(tout_etendu) + list(set(config.BENCHMARK.values()))
    info(f"{len(a_telecharger)} titres à télécharger, jusqu'à {config.HISTORIQUE.replace('y', ' ans')} d'historique (Yahoo Finance, avec secours)…")
    t0 = time.time()
    bruts = data.telecharger_plusieurs(a_telecharger)
    info(f"→ {len(bruts)} titres reçus en {duree(time.time() - t0)}.")
    info("Indicateurs économiques : VIX, taux, courbe des taux, dollar, or, pétrole, cuivre, crédit, chômage…")
    try:
        contexte = data.macro()
    except Exception:
        contexte = {}
    info(f"→ {len(contexte)} séries économiques reçues : {', '.join(sorted(contexte)) or 'aucune'}.")

    def calc(t, m, minimum):
        brut = bruts.get(t)
        if brut is None or len(brut) < minimum:
            return None
        type_m = "crypto" if t.endswith("-USD") else m
        bench = bruts.get(config.BENCHMARK.get(type_m, "SPY"))
        ctx = contexte if type_m == "crypto" else {k: v for k, v in contexte.items() if k != "fng"}
        try:
            return indicators.calculer(brut, bench, ctx)
        except Exception:
            return None
    info("Calcul de plus de 40 indicateurs par titre…")
    affiches = {t: d for t in noms if (d := calc(t, marche_de[t], 260)) is not None}
    supp_base = {t: d for t, m in tout_base.items() if (d := calc(t, m, 400)) is not None}
    supp_etendu = {t: d for t, m in tout_etendu.items() if (d := calc(t, m, 400)) is not None}
    marches = {t: ("crypto" if t.endswith("-USD") else m) for t, m in {**marche_de, **tout_base, **tout_etendu}.items()}
    lignes = sum(len(d) for d in (*affiches.values(), *supp_base.values(), *supp_etendu.values()))
    annees = max((len(d) for d in affiches.values()), default=0) / 252
    info(f"→ {len(affiches)} titres du site + {len(supp_base) + len(supp_etendu)} titres d'apprentissage, "
         f"{lignes:,} journées de cotation".replace(",", " ") + f", jusqu'à {annees:.0f} ans d'historique.")
    return affiches, supp_base, supp_etendu, marches, contexte, etendu, lignes


def candidats(model, complet):
    """Façons de prévoir testées : celles du site, la recette actuelle, et des réglages nouveaux."""
    macro = {"vix", "vix_chg", "taux_chg", "dollar_chg", "fng", "courbe_taux", "petrole_chg", "cuivre_chg",
             "spread_credit", "spread_credit_chg", "conditions_fin", "chomage_tendance"}
    technique = [v for v in model.VARIABLES if v not in macro]
    out = [(n, v, pm, p) for n, v, pm, p in model.configs_disponibles()]
    noms = {c[0] for c in out}
    nouveaux = [
        ("Tous les indicateurs + économie, arbres plus profonds", model.VARIABLES, False,
         {"profondeur": 4, "apprentissage": 0.03, "iterations": 350, "feuille": 400}),
        ("Un modèle par marché, plus prudent", model.VARIABLES, True, {"profondeur": 3, "feuille": 600}),
        ("Indicateurs techniques seulement (sans économie)", technique, False, {}),
    ]
    if complet:
        nouveaux += [
            ("Tous les indicateurs, apprentissage lent", model.VARIABLES, False,
             {"profondeur": 3, "apprentissage": 0.02, "iterations": 500, "feuille": 300}),
            ("Tous les indicateurs, très prudent", model.VARIABLES, False, {"profondeur": 2, "feuille": 800}),
            ("Un modèle par marché, arbres plus profonds", model.VARIABLES, True,
             {"profondeur": 4, "apprentissage": 0.03, "iterations": 350, "feuille": 400}),
            ("Indicateurs de base + économie", model.VARIABLES_BASE + sorted(macro & set(model.VARIABLES)), False, {}),
        ]
    out += [c for c in nouveaux if c[0] not in noms]
    return out


def main():
    p = argparse.ArgumentParser(description="Entraînement approfondi de l'IA de Radar Bourse")
    p.add_argument("--complet", action="store_true", help="tester plus de réglages (plus long)")
    p.add_argument("--sans-publier", action="store_true", help="faire le rapport sans rien envoyer sur le site")
    p.add_argument("--demo", action="store_true", help="données fictives (pour tester le script)")
    p.add_argument("--pas-de-navigateur", action="store_true")
    args = p.parse_args()
    debut = time.time()
    print("🧠 Entraînement approfondi de l'IA de Radar Bourse" + ("  (DÉMO, données fictives)" if args.demo else ""))
    print("   Durée : environ " + ("1 à 3 heures" if args.complet else "20 à 60 minutes") + " selon ton ordinateur.")
    print("   Tu peux utiliser ton PC pendant ce temps. Ne ferme pas cette fenêtre.")
    verifier_dependances()

    titre("1/6 · Récupération de la dernière version du site")
    depot_git = os.path.isdir(os.path.join(ICI, ".git")) and trouver("git")
    if depot_git and not args.demo:
        code, sortie = git("pull", "--rebase", "--autostash")
        info("✅ À jour avec GitHub." if code == 0 else f"⚠️ Impossible de récupérer la dernière version ({sortie[-200:]}). On continue.")
    else:
        info("Dossier non relié à GitHub : le rapport sera fait, mais rien ne sera envoyé sur le site.")

    from bourse_bot import config, data, model
    data.DEMO = args.demo
    config.HISTORIQUE = "20y"
    config.DOSSIER_CACHE = ".cache_entrainement"
    config.CACHE_MAX_H = 24
    horizon = config.HORIZON_PREDICTION

    titre("2/6 · Collecte des données : Bourse et économie")
    affiches, supp_base, supp_etendu, marches, contexte, etendu, nb_lignes = preparer_donnees(args)
    if len(affiches) < 20:
        print("\n❌ Trop peu de données reçues (Yahoo bloque peut-être). Réessaie dans une heure.")
        return 2

    ancien = model._lire_fichier_modele() or {}
    configs = {c[0]: c for c in model.configs_disponibles()}
    champion_nom = ancien.get("configuration") if ancien.get("configuration") in configs else "Un seul modèle, tous les indicateurs"
    _, v_ch, pm_ch, p_ch = configs[champion_nom]

    titre("3/6 · Examen n°1 : plus de titres d'apprentissage aide-t-il vraiment ?")
    info("Les IA sont testées sur les mêmes titres du site et les mêmes années, avec ou sans les titres en plus.")
    import numpy as np
    import pandas as pd
    jeu_base = model.construire_jeu({**supp_base, **affiches}, marches, horizon)
    jeu_etendu = model.construire_jeu({**supp_base, **supp_etendu, **affiches}, marches, horizon) if supp_etendu else None
    garder_etendu, examen_donnees = False, {}

    def oof_sur_site(jeu, v, pm, prm):
        o = model.predictions_hors_echantillon(jeu, horizon, v, pm, params=prm, garder_ticker=True)
        if o is None:
            return None
        o = o[o["ticker"].isin(list(affiches))]
        return o.set_index(["ticker"], append=True).sort_index()
    t0 = time.time()
    o_base = oof_sur_site(jeu_base, v_ch, pm_ch, p_ch)
    if jeu_etendu is not None and o_base is not None:
        o_et = oof_sur_site(jeu_etendu, v_ch, pm_ch, p_ch)
        commun = o_base.index.intersection(o_et.index) if o_et is not None else []
        if len(commun) > 5000:
            duo = pd.DataFrame({"cible": o_base.loc[commun, "cible"].to_numpy(), "pa": o_et.loc[commun, "proba"].to_numpy(),
                                "pb": o_base.loc[commun, "proba"].to_numpy()}, index=commun.get_level_values(0))
            auc_a, auc_b = model._auc(duo["cible"].to_numpy(), duo["pa"].to_numpy()), model._auc(duo["cible"].to_numpy(), duo["pb"].to_numpy())
            boot = model.bootstrap_mois(duo, lambda d: np.array([model._auc(d["cible"].to_numpy(), d["pa"].to_numpy())
                                                                 - model._auc(d["cible"].to_numpy(), d["pb"].to_numpy())]), graine=7)
            ic = model._ic(boot[:, 0]) if len(boot) else None
            garder_etendu = bool(ic and ic[0] > 0)
            examen_donnees = {"auc_sans": auc_b, "auc_avec": auc_a, "ic_gain": ic, "nb_titres_en_plus": len(supp_etendu),
                              "decision": garder_etendu}
            info(f"Sans les titres en plus : AUC {auc_b:.4f} · avec : AUC {auc_a:.4f} · gain {auc_a - auc_b:+.4f}"
                 + (f" (marge {ic[0]:+.4f} à {ic[1]:+.4f})" if ic else ""))
            info("✅ Gain prouvé : les titres en plus seront utilisés." if garder_etendu
                 else "➖ Gain non prouvé : on garde la liste actuelle (plus rapide en ligne).")
    info(f"({duree(time.time() - t0)})")

    jeu = jeu_etendu if garder_etendu else jeu_base

    titre("4/6 · Examen n°2 : quelle façon de prévoir est la meilleure ?")
    liste = candidats(model, args.complet)
    info(f"{len(liste)} façons de prévoir testées, chacune sur des années qu'elle n'a jamais vues.")
    resultats = []
    for i, (nom, v, pm, prm) in enumerate(liste, 1):
        t0 = time.time()
        oof = model.predictions_hors_echantillon(jeu, horizon, v, pm, params=prm)
        if oof is None or oof["cible"].nunique() < 2:
            info(f"[{i}/{len(liste)}] {nom} : impossible à tester.")
            continue
        auc = model._auc(oof["cible"].to_numpy(), oof["proba"].to_numpy())
        resultats.append((auc, nom, v, pm, oof, prm))
        info(f"[{i}/{len(liste)}] {nom} : AUC {auc:.4f}{'  (en place sur le site)' if nom == champion_nom else ''}  · {duree(time.time() - t0)}")
    if not resultats:
        print("\n❌ Aucun modèle n'a pu être testé.")
        return 3
    resultats.sort(key=lambda r: r[0], reverse=True)

    titre("5/6 · Décision : le site doit-il changer d'IA ?")
    choix, decision = model._decision_champion(resultats, champion_nom)
    auc_choix, nom_choix, v_c, pm_c, oof_c, prm_c = choix
    ev, _ = model._evaluation(oof_c)
    info(decision.get("raison", ""))
    if decision.get("ic_gain_auc"):
        a, b = decision["ic_gain_auc"]
        info(f"Gain de la meilleure sur l'IA en place : entre {a:+.4f} et {b:+.4f} d'AUC (95 %).")
    info(f"IA retenue : {nom_choix} · bonnes directions {ev.precision * 100:.1f} % "
         + (f"(marge {ev.ic['precision'][0] * 100:.1f} à {ev.ic['precision'][1] * 100:.1f}) " if ev.ic.get("precision") else "")
         + f"· {ev.verdict()}")
    change = bool(decision.get("change")) or garder_etendu

    entree = {"date": datetime.now().isoformat(timespec="minutes"), "mode": "complet" if args.complet else "rapide",
              "demo": args.demo, "nb_titres": len(affiches) + len(supp_base) + (len(supp_etendu) if garder_etendu else 0),
              "nb_lignes": int(len(jeu)), "series_economiques": sorted(contexte),
              "candidats": [{"nom": n, "auc": a} for a, n, *_ in resultats], "en_place": champion_nom,
              "retenu": nom_choix, "change_methode": bool(decision.get("change")), "raison": decision.get("raison"),
              "ic_gain_auc": decision.get("ic_gain_auc"), "examen_donnees": examen_donnees,
              "precision": ev.precision, "ic_precision": ev.ic.get("precision"), "auc": ev.auc,
              "niveau_preuve": ev.niveau_preuve()}

    titre("6/6 · Rapport et mise à jour du site")
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    m = dict(ancien)
    m["entrainements"] = (m.get("entrainements") or [])[-19:] + [entree]
    if decision.get("change"):
        m["recette"] = {"nom": nom_choix, "variables": list(v_c), "par_marche": bool(pm_c), "params": prm_c,
                        "date": entree["date"], "auc": auc_choix}
        m["configuration"] = model.NOM_RECETTE
        m["date"] = "2000-01-01T00:00:00"   # oblige le site à refaire un test complet avec la nouvelle recette
        m.setdefault("version", 2)
    if not args.demo:
        with open(model.FICHIER_MODELE, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=1, default=lambda v: None)
        if garder_etendu:
            utiles = {mk: [t for t in liste_t if t in supp_etendu] for mk, liste_t in etendu.items()}
            with open(os.path.join(config.DOSSIER_HISTORIQUE, "apprentissage.json"), "w", encoding="utf-8") as f:
                json.dump({"date": entree["date"], "tickers": utiles}, f, ensure_ascii=False, indent=1)
    chemin = ecrire_rapport(entree, resultats, champion_nom, ev, change)
    info(f"📄 Rapport : {chemin}")

    publie = False
    if change and not args.sans_publier and not args.demo and depot_git:
        git("add", "historique/modele.json", "historique/apprentissage.json")
        git("commit", "-m", f"Entraînement approfondi du {datetime.now():%d/%m/%Y} : {nom_choix}")
        for _ in range(3):
            git("pull", "--rebase", "--autostash")
            code, sortie = git("push")
            if code == 0:
                publie = True
                break
            time.sleep(5)
        if publie:
            gh = trouver("gh")
            if gh:
                subprocess.run([gh, "workflow", "run", "radar.yml"], cwd=ICI, capture_output=True)
            info("✅ Nouvelle IA envoyée : le site va se mettre à jour tout seul (15 à 30 minutes).")
        else:
            info("⚠️ L'envoi sur GitHub a échoué. Relance mettre_en_ligne.bat, il enverra la nouvelle IA.")
    elif not change:
        if not args.demo and depot_git and not args.sans_publier:
            git("add", "historique/modele.json")
            git("commit", "-m", f"Entraînement approfondi du {datetime.now():%d/%m/%Y} : IA confirmée")
            git("pull", "--rebase", "--autostash")
            git("push")
        info("✅ L'IA en place reste la meilleure (ou l'écart n'est pas prouvé) : le site ne change pas de méthode.")

    print("\n" + "━" * 64)
    print(f"🏁 Terminé en {duree(time.time() - debut)}.")
    print("   Rappel : même la meilleure IA se trompe souvent. Rien n'est sûr en Bourse.")
    if not args.pas_de_navigateur:
        try:
            webbrowser.open("file://" + os.path.abspath(chemin))
        except Exception:
            pass
    return 0


def ecrire_rapport(e, resultats, champion_nom, ev, change):
    from bourse_bot import config
    os.makedirs(config.DOSSIER_RAPPORTS, exist_ok=True)
    chemin = os.path.join(config.DOSSIER_RAPPORTS, f"entrainement_{datetime.now():%Y%m%d_%H%M}.html")
    x = lambda s: html.escape(str(s))
    lignes = "".join(
        f"<tr><td>{x(n)}{' <b>(en place)</b>' if n == champion_nom else ''}{' <b>✓ retenue</b>' if n == e['retenu'] else ''}</td>"
        f"<td>{a:.4f}</td><td><div class='b'><i style='width:{max(0, min(100, (a - 0.45) / 0.15 * 100)):.0f}%'></i></div></td></tr>"
        for a, n, *_ in resultats)
    D = e.get("examen_donnees") or {}
    icp = e.get("ic_precision")
    verdict = ("✅ L'IA a progressé de façon prouvée : la nouvelle version est envoyée sur le site." if change and not e["demo"]
               else "✅ (Démo) L'IA aurait été mise à jour." if change else
               "➖ Pas de progrès prouvé : le site garde son IA actuelle. C'est normal et sain : on ne change pas sur un coup de chance.")
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Entraînement de l'IA du {datetime.now():%d/%m/%Y}</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:24px 16px;color:#0f1b2d;background:#eef1f5}}
.c{{background:#fff;border:1px solid #d9e0e8;border-radius:10px;padding:16px;margin:14px 0}}h1{{font-size:28px}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:8px;border-bottom:1px solid #d9e0e8;text-align:left}}
.b{{height:10px;background:#eef1f5;border-radius:5px;min-width:120px}}.b i{{display:block;height:100%;background:#1d4fd8;border-radius:5px}}
.v{{font-size:18px;font-weight:700}}.m{{color:#5a6a80;font-size:14px}}</style></head><body>
<h1>🧠 Rapport d'entraînement de l'IA</h1><p class="m">{x(e['date'])} · mode {x(e['mode'])}{' · DÉMO (données fictives)' if e['demo'] else ''}</p>
<div class="c"><p class="v">{x(verdict)}</p><p>{x(e.get('raison') or '')}</p></div>
<div class="c"><h2>Ce que l'IA a étudié</h2><ul>
<li><b>{e['nb_titres']}</b> actions, ETF et cryptos, <b>{e['nb_lignes']:,}</b> situations de marché analysées.</li>
<li>Données économiques : {x(', '.join(e['series_economiques']) or 'aucune')}.</li>
<li>Chaque façon de prévoir a été testée uniquement sur des années qu'elle n'avait jamais vues.</li></ul></div>
<div class="c"><h2>Examen n°1 : plus de titres d'apprentissage ?</h2>{
    f"<p>Sans les {D['nb_titres_en_plus']} titres en plus : AUC {D['auc_sans']:.4f}. Avec : AUC {D['auc_avec']:.4f}. "
    + (f"Marge du gain : {D['ic_gain'][0]:+.4f} à {D['ic_gain'][1]:+.4f}. " if D.get('ic_gain') else "")
    + ("<b>Gain prouvé : utilisés désormais.</b>" if D.get('decision') else "<b>Gain non prouvé : liste actuelle conservée.</b>") + "</p>"
    if D else "<p>Pas assez de données pour cet examen.</p>"}</div>
<div class="c"><h2>Examen n°2 : la meilleure façon de prévoir</h2>
<p class="m">AUC : 0,5 = hasard, 1 = parfait. En Bourse, 0,52 à 0,56 est déjà un bon score : personne ne prévoit les marchés de façon fiable.</p>
<table><tr><th>Façon de prévoir</th><th>AUC</th><th></th></tr>{lignes}</table></div>
<div class="c"><h2>L'IA retenue en chiffres simples</h2>
<p>Sur 100 prévisions testées, elle a trouvé la bonne direction <b>{ev.precision * 100:.0f} fois</b>{f" (marge d'erreur : {icp[0] * 100:.0f} à {icp[1] * 100:.0f})" if icp else ""}.
En répondant toujours la même chose, on aurait eu raison {ev.precision_base * 100:.0f} fois.</p><p><b>{x(ev.verdict())}</b></p></div>
<p class="m">Rien n'est sûr en Bourse : ce rapport mesure le passé, il ne garantit rien pour l'avenir.</p></body></html>"""
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)
    return chemin


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nArrêté. Rien n'a été envoyé sur le site.")
        sys.exit(1)
