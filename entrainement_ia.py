"""Entraînement approfondi de l'IA de Radar Bourse (à lancer sur ton PC : double-clic sur entrainement_ia.bat).

Une fenêtre s'ouvre avec la progression, une jauge « ce que l'IA a appris » et le journal.
  1. Collecte : jusqu'à 20 ans d'historique sur près de 300 actions, ETF et cryptos, plus des données
     économiques (taux, courbe des taux, dollar, or, pétrole, cuivre, crédit, tension financière, chômage).
     Chaque chiffre économique est décalé de son délai de publication : l'IA ne voit jamais l'avenir.
  2. Règle anti-chance : les années les plus récentes sont mises sous clé. Toute la recherche se fait
     sans elles ; elles ne servent qu'une fois, à la fin, pour l'examen final.
  3. Recherche : des dizaines de réglages tirés au hasard, chacun testé sur des années jamais vues
     (validation « walk-forward » avec purge). Les réglages prometteurs sont testés plus en profondeur.
  4. Tri des indicateurs : un indicateur n'est gardé que s'il aide sur DEUX périodes différentes.
  5. Examen final : les 3 meilleurs contre l'IA du site, sur les années sous clé. L'IA du site n'est
     remplacée que si la nouvelle fait mieux de façon prouvée (marge d'erreur à 95 %) ET sur chacune
     des deux moitiés de l'examen (pas seulement en moyenne).
  6. Quand tu fermes la fenêtre ou cliques « Arrêter », l'IA passe l'examen final avec ce qu'elle a
     appris, puis te propose de mettre à jour le site, suit sa publication et vérifie qu'il fonctionne.

Au démarrage, la fenêtre te demande la durée : Rapide (≈ 20 min), Normal (≈ 50 min) ou Expert (≈ 2 h 30).
L'IA garde en mémoire ses essais (historique/essais_ia.json) : d'un entraînement à l'autre, elle explore
autour de ses meilleures idées au lieu de repartir de zéro.

Options : --duree rapide|normal|expert, --minutes N, --console (sans fenêtre), --demo (données fictives).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser
from datetime import datetime, timezone

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
sys.path.insert(0, ICI)

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
               "THETA-USD", "NEO-USD", "ZEC-USD", "DASH-USD", "KSM-USD"],
}
MACRO = {"vix", "vix_chg", "taux_chg", "dollar_chg", "fng", "courbe_taux", "petrole_chg", "cuivre_chg",
         "spread_credit", "spread_credit_chg", "conditions_fin", "chomage_tendance", "vix_structure",
         "marche_largeur", "marche_dispersion"}
SEUIL_INDICATEUR = 0.0003   # gain d'AUC minimal, sur chacune des deux périodes, pour garder un indicateur
SEUIL_REGLE = 0.001         # plus exigeant pour les règles du manuel (beaucoup de versions testées)
# Durées proposées : temps de recherche, nombre maximal d'essais, 1 jour sur N gardé pendant la recherche.
# Garder 1 jour sur 2 ou 3 ne fait presque rien perdre : deux jours voisins ont des résultats à un mois
# presque identiques (ils se chevauchent sur 19 jours sur 20). L'examen final, lui, utilise TOUS les jours.
DUREES = {
    "rapide": {"nom": "Rapide", "minutes": 12, "essais": 14, "pas": 3, "resume": "≈ 20 min · pour vérifier que tout va bien"},
    "normal": {"nom": "Normal", "minutes": 35, "essais": 35, "pas": 2, "resume": "≈ 50 min · le bon choix la plupart du temps"},
    "expert": {"nom": "Expert", "minutes": 140, "essais": 120, "pas": 1, "resume": "≈ 2 h 30 · recherche très large, précision maximale"},
}
FICHIER_ESSAIS = os.path.join("historique", "essais_ia.json")   # mémoire des essais d'un entraînement à l'autre
AUC_HASARD, AUC_EXCELLENT = 0.50, 0.58   # bornes de la jauge (0,58 serait exceptionnel en Bourse)


# ----------------------------------------------------------------------------
# Outils
# ----------------------------------------------------------------------------
def duree(secondes):
    m = int(secondes // 60)
    return f"{m} min {int(secondes % 60):02d} s" if m else f"{int(secondes)} s"


def verifier_dependances():
    try:
        import numpy, pandas, sklearn, yfinance  # noqa: F401
    except ImportError:
        print("Installation des outils nécessaires (une seule fois)…")
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


def commande(prog, *args, timeout=300):
    exe = trouver(prog)
    if not exe:
        return 1, f"{prog} introuvable"
    try:
        r = subprocess.run([exe, *args], cwd=ICI, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)


def adresse_site() -> str:
    try:
        with open(os.path.join(ICI, ".radar_deploy.json"), encoding="utf-8") as f:
            dom = json.load(f).get("domaine")
        if dom:
            return f"https://{dom}/"
    except Exception:
        pass
    code, url = commande("git", "remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url or "")
    if code != 0 or not m:
        return ""
    proprio, depot = m.group(1).lower(), m.group(2)
    return f"https://{proprio}.github.io/" if depot.lower() == f"{proprio}.github.io" else f"https://{proprio}.github.io/{depot}/"


# ----------------------------------------------------------------------------
# Le moteur d'entraînement (tourne en arrière-plan, envoie des événements à la fenêtre)
# ----------------------------------------------------------------------------

class CarteRecherche:
    """Recherche guidée : l'IA apprend, à partir de TOUS ses essais (passés et présents), quels réglages
    marchent, puis choisit le prochain essai là où elle s'attend au meilleur gain.

    - Chaque essai est décrit par quelques chiffres (profondeur, vitesse d'apprentissage, nombre et type d'indicateurs…).
    - Les notes de jours différents ne sont pas comparables (les données changent) : chaque note est donc
      exprimée par rapport à la moyenne de SA séance. Seul l'écart compte, pas la note brute.
    - Une forêt d'arbres prévoit l'écart attendu ET son incertitude. On teste en priorité ce qui est
      prometteur ou encore inconnu (« optimisme face à l'inconnu »), de moins en moins au fil de la séance.
    - Un candidat trop proche d'un essai déjà fait est écarté : il n'apprendrait rien de nouveau.
    """
    PARAMS = (("profondeur", 3, False), ("apprentissage", 0.04, True), ("iterations", 250, True),
              ("feuille", 300, True), ("l2", 2.0, True), ("c_lin", 0.05, True), ("demi_vie", 0, False))
    MINIMUM = 12

    def __init__(self, np, macro):
        self.np, self.macro = np, macro
        self.foret, self.X, self.y = None, None, None

    def decrire(self, variables, par_marche, params):
        np, prm = self.np, params or {}
        x = []
        for k, d, log in self.PARAMS:
            v = float(prm.get(k, d) or 0)
            x.append(np.log(max(v, 1e-4)) if log else v)
        v = set(variables)
        x += [float(bool(par_marche)), len(v), sum(c.startswith("cx_") for c in v), len(v & self.macro),
              sum(c.startswith("rang_") for c in v)]
        return np.array(x, dtype=float)

    def apprendre(self, anciens, actuels):
        """anciens : essais des séances passées (avec leur date) ; actuels : essais de cette séance."""
        np = self.np
        lignes = [(e, e.get("date") or "ancien") for e in anciens if "membres" not in (e.get("params") or {})]
        lignes += [(e, "maintenant") for e in actuels if "membres" not in (e.get("params") or {})]
        if len(lignes) < self.MINIMUM:
            self.foret = None
            return False
        par_seance = {}
        for e, s in lignes:
            par_seance.setdefault(s, []).append(e["auc_recherche"])
        moy = {s: float(np.mean(v)) for s, v in par_seance.items()}
        X = np.array([self.decrire(e["variables"], e["par_marche"], e.get("params")) for e, _ in lignes])
        y = np.array([e["auc_recherche"] - moy[s] for e, s in lignes])
        # une séance avec un seul essai n'apprend rien sur les écarts : poids nul
        w = np.array([0.0 if len(par_seance[s]) < 2 else (0.6 if not e.get("teste_completement", True) else 1.0)
                      for e, s in lignes])
        if (w > 0).sum() < self.MINIMUM:
            self.foret = None
            return False
        from sklearn.ensemble import RandomForestRegressor
        self.foret = RandomForestRegressor(n_estimators=150, min_samples_leaf=2, max_features=0.6,
                                           random_state=0, n_jobs=-1).fit(X, y, sample_weight=w)
        self.X, self.y = X, y
        return True

    def prevoir(self, candidats):
        np = self.np
        X = np.array([self.decrire(c[1], c[2], c[3]) for c in candidats])
        arbres = np.array([a.predict(X) for a in self.foret.estimators_])
        return arbres.mean(axis=0), arbres.std(axis=0), X

    def choisir(self, candidats, avancement):
        """avancement de 0 à 1 : au début on explore l'inconnu, à la fin on vise ce qui est sûr."""
        np = self.np
        moy, inc, X = self.prevoir(candidats)
        kappa = 1.5 * (1 - avancement) + 0.3
        score = moy + kappa * inc
        if self.X is not None and len(self.X):
            echelle = self.X.std(axis=0) + 1e-6
            dist = np.min(np.abs((X[:, None, :] - self.X[None, :, :]) / echelle).sum(axis=2), axis=1)
            score = np.where(dist < 0.35, -np.inf, score)   # quasi-doublon d'un essai déjà fait
        k = int(np.argmax(score))
        if not np.isfinite(score[k]):
            return None, None, None
        return candidats[k], float(moy[k]), float(inc[k])

    def lecons(self, anciens, actuels):
        """Ce que la carte a appris, en phrases simples (moyennes des écarts par famille de réglages)."""
        np = self.np
        lignes = [(e, e.get("date") or "ancien") for e in anciens + [dict(a, date="maintenant") for a in actuels]
                  if "membres" not in (e.get("params") or {})]
        if len(lignes) < 20:
            return []
        par_seance = {}
        for e, s in lignes:
            par_seance.setdefault(s, []).append(e["auc_recherche"])
        moy = {s: float(np.mean(v)) for s, v in par_seance.items()}
        ecarts = [(e, e["auc_recherche"] - moy[s]) for e, s in lignes if len(par_seance[s]) >= 2]
        familles = {
            "arbres peu profonds (2–3)": lambda e: (e.get("params") or {}).get("profondeur", 3) <= 3,
            "arbres profonds (4 et plus)": lambda e: (e.get("params") or {}).get("profondeur", 3) >= 4,
            "un modèle séparé par marché": lambda e: bool(e["par_marche"]),
            "un seul modèle pour tous les marchés": lambda e: not e["par_marche"],
            "donner plus de poids aux années récentes": lambda e: bool((e.get("params") or {}).get("demi_vie")),
            "toutes les années comptent pareil": lambda e: not (e.get("params") or {}).get("demi_vie"),
            "apprentissage lent (≤ 0,03)": lambda e: (e.get("params") or {}).get("apprentissage", 0.04) <= 0.03,
            "apprentissage rapide (≥ 0,05)": lambda e: (e.get("params") or {}).get("apprentissage", 0.04) >= 0.05,
            "avec les règles du manuel de Bourse": lambda e: any(v.startswith("cx_") for v in e["variables"]),
            "sans les règles du manuel": lambda e: not any(v.startswith("cx_") for v in e["variables"]),
            "avec les données économiques": lambda e: bool(set(e["variables"]) & self.macro),
            "peu d'indicateurs (moins de 30)": lambda e: len(e["variables"]) < 30,
        }
        res = []
        for nom, f in familles.items():
            v = [d for e, d in ecarts if f(e)]
            if len(v) >= 6:
                res.append((nom, float(np.mean(v)), len(v)))
        res.sort(key=lambda r: -r[1])
        return res

class Moteur:
    PHASES = [("collecte", 0.16), ("examen1", 0.10), ("manuel", 0.09), ("recherche", 0.42), ("tri", 0.08), ("final", 0.15)]

    def __init__(self, args, emettre):
        self.args, self.emettre = args, emettre
        self.arret = threading.Event()
        self.resultat = None
        self.depot_git = False
        self.cols_utiles = []

    def log(self, texte):
        self.emettre("log", texte=texte)

    def etape(self, n, texte):
        self.emettre("etape", n=n, texte=texte)
        self.log(f"\n━━ {n}/7 · {texte}")

    def progres(self, phase, frac):
        total = 0.0
        for nom, poids in self.PHASES:
            if nom == phase:
                total += poids * max(0.0, min(1.0, frac))
                break
            total += poids
        self.emettre("progres", pct=total)

    def lancer(self):
        try:
            self._lancer()
        except Exception:
            self.emettre("erreur", texte=traceback.format_exc())

    def _lancer(self):
        args = self.args
        from bourse_bot import config, data, model
        import numpy as np
        import pandas as pd
        self.np, self.pd, self.model = np, pd, model
        data.DEMO = args.demo
        config.HISTORIQUE = "20y"
        config.DOSSIER_CACHE = ".cache_entrainement"
        config.CACHE_MAX_H = 24
        self.horizon = horizon = config.HORIZON_PREDICTION
        reglage = DUREES[args.duree]
        budget = (args.minutes or reglage["minutes"]) * 60
        max_essais = reglage["essais"]
        self.log(f"Durée choisie : {reglage['nom']} ({reglage['resume']}).")

        self.etape(1, "Récupération de la dernière version du site")
        self.depot_git = bool(os.path.isdir(os.path.join(ICI, ".git")) and trouver("git"))
        if self.depot_git and not args.demo:
            code, sortie = commande("git", "pull", "--rebase", "--autostash")
            self.log("✅ À jour avec GitHub." if code == 0 else f"⚠️ Mise à jour depuis GitHub impossible ({sortie[-160:]}). On continue.")
        else:
            self.log("Dossier non relié à GitHub : l'entraînement se fera, mais rien ne pourra être envoyé sur le site.")

        self.etape(2, "Collecte des données : Bourse et économie")
        affiches, supp_base, supp_etendu, marches, contexte, etendu = self._donnees(config, data)
        if len(affiches) < 20:
            raise RuntimeError("Trop peu de données reçues (Yahoo bloque peut-être). Réessaie dans une heure.")

        ancien = model._lire_fichier_modele() or {}
        configs = {c[0]: c for c in model.configs_disponibles()}
        champion = ancien.get("configuration") if ancien.get("configuration") in configs else "Un seul modèle, tous les indicateurs"
        _, v_ch, pm_ch, p_ch = configs[champion]

        jeu_base = model.construire_jeu({**supp_base, **affiches}, marches, horizon)
        dates = np.array(sorted(jeu_base.dropna(subset=["cible"]).index.unique()))
        coupure = dates[int(len(dates) * 0.8)]
        self.log(f"🔒 Règle anti-chance : les années après le {pd.Timestamp(coupure):%d/%m/%Y} sont mises sous clé. "
                 "La recherche se fait sans elles ; elles servent une seule fois, pour l'examen final.")

        self.etape(3, "Examen n°1 : étudier plus de titres aide-t-il vraiment ?")
        garder_etendu, examen_donnees = False, {}
        jeu = jeu_base
        if supp_etendu:
            jeu_etendu = model.construire_jeu({**supp_base, **supp_etendu, **affiches}, marches, horizon)
            self.progres("examen1", 0.1)
            # examen fait AVANT les années sous clé (sur la fin de la zone de recherche), pour ne pas les user
            zb, ze = self._zone_recherche(jeu_base, coupure), self._zone_recherche(jeu_etendu, coupure)
            d_sel = np.array(sorted(zb.dropna(subset=["cible"]).index.unique()))
            coupure_1 = d_sel[int(len(d_sel) * 0.75)]
            o_b = self._final(zb, coupure_1, v_ch, pm_ch, p_ch)
            self.progres("examen1", 0.55)
            o_e = self._final(ze, coupure_1, v_ch, pm_ch, p_ch)
            if o_b is not None and o_e is not None:
                sel = lambda o: o[o["ticker"].isin(list(affiches))].set_index("ticker", append=True)
                o_b, o_e = sel(o_b), sel(o_e)
                commun = o_b.index.intersection(o_e.index)
                if len(commun) > 2000:
                    duo = pd.DataFrame({"cible": o_b.loc[commun, "cible"].to_numpy(), "pa": o_e.loc[commun, "proba"].to_numpy(),
                                        "pb": o_b.loc[commun, "proba"].to_numpy()}, index=commun.get_level_values(0))
                    ic, a_avec, a_sans, moities = self._comparer(duo)
                    garder_etendu = bool(ic and ic[0] > 0 and moities)
                    examen_donnees = {"auc_sans": a_sans, "auc_avec": a_avec, "ic_gain": ic,
                                      "nb_titres_en_plus": len(supp_etendu), "decision": garder_etendu}
                    self.log(f"Sans les {len(supp_etendu)} titres en plus : AUC {a_sans:.4f} · avec : {a_avec:.4f}"
                             + (f" · marge du gain {ic[0]:+.4f} à {ic[1]:+.4f}" if ic else ""))
                    self.log("✅ Gain prouvé et régulier : ils seront utilisés." if garder_etendu
                             else "➖ Gain non prouvé : on garde la liste actuelle.")
            if garder_etendu:
                jeu = jeu_etendu
        self.donnees_jeu = {**supp_base, **(supp_etendu if garder_etendu else {}), **affiches}
        self.marches_jeu = marches
        self.progres("examen1", 1)
        jeu_sel = self._zone_recherche(jeu, coupure)
        if reglage["pas"] > 1:   # recherche plus rapide : 1 jour sur N (l'examen final garde tous les jours)
            jours = np.array(sorted(jeu_sel.index.unique()))[::reglage["pas"]]
            jeu_sel = jeu_sel[jeu_sel.index.isin(jours)]
            self.log(f"⚡ Recherche accélérée : 1 jour sur {reglage['pas']} (les jours voisins se ressemblent presque "
                     "tous à un mois d'horizon). L'examen final utilisera tous les jours.")

        self.etape(4, "Examen du manuel de Bourse : les règles connues marchent-elles vraiment ?")
        verdicts, cols_utiles = self._examen_manuel(jeu_sel)

        self.etape(5, "Recherche : des dizaines de façons de prévoir, testées sur des années jamais vues")
        self.log("Tu peux arrêter quand tu veux (bouton « Arrêter » ou croix de la fenêtre) : "
                 "l'IA passera alors l'examen final avec ce qu'elle a déjà appris.")
        rng = np.random.default_rng(int(time.time()) % 100000)
        essais, t0 = [], time.time()
        memoire = self._lire_memoire()
        deja = {self._signature(e) for e in memoire}
        carte = CarteRecherche(np, MACRO)
        if memoire:
            self.log(f"🧠 Mémoire : {len(memoire)} essais des entraînements précédents, sur {len({e.get('date') for e in memoire})} séance(s). "
                     "Ils servent à guider la recherche, et les meilleurs sont revérifiés sur les données d'aujourd'hui.")
        meilleur_rapide = [0.0]

        def tester(nom, v, pm, prm, force=False):
            if self.arret.is_set() and not force:
                return
            ti = time.time()
            # 1er tour rapide (3 périodes) ; seuls les réglages prometteurs passent le test complet (5 périodes)
            o3 = model.predictions_hors_echantillon(jeu_sel, horizon, v, pm, n_plis=3, params=prm)
            if o3 is None or o3["cible"].nunique() < 2:
                return
            a3 = model._auc(o3["cible"].to_numpy(), o3["proba"].to_numpy())
            complet = force or a3 >= meilleur_rapide[0] - 0.004
            meilleur_rapide[0] = max(meilleur_rapide[0], a3)
            auc = a3
            if complet:
                o5 = model.predictions_hors_echantillon(jeu_sel, horizon, v, pm, n_plis=5, params=prm)
                if o5 is not None and o5["cible"].nunique() == 2:
                    auc = model._auc(o5["cible"].to_numpy(), o5["proba"].to_numpy())
            essais.append({"nom": nom, "variables": list(v), "par_marche": bool(pm), "params": dict(prm),
                           "auc_recherche": auc, "teste_completement": bool(complet)})
            deja.add(self._signature(essais[-1]))
            best = max((e["auc_recherche"] for e in essais if e["teste_completement"]), default=auc)
            self.emettre("niveau", meilleur=best, essais=len(essais))
            self.log(f"[{len(essais):>2}] AUC {auc:.4f}{' ★' if complet and auc >= best else ''}{'' if complet else ' (1er tour seulement)'} · "
                     f"{nom}{'  ← IA du site' if nom == champion else ''} · {duree(time.time() - ti)}")
            self.progres("recherche", min(1.0, (time.time() - t0) / budget))

        for nom, v, pm, prm in model.configs_disponibles():
            tester(nom, v, pm, prm, force=(nom == champion))
        # Revérification : les meilleurs essais des séances passées sont rejoués sur les données d'aujourd'hui.
        # Une vieille note n'est jamais comparée telle quelle à une note d'aujourd'hui (les données ont changé).
        a_reverifier = self._meilleurs_passes(memoire, {self._signature(e) for e in essais}, n=4 if max_essais < 30 else 6)
        if a_reverifier:
            self.log(f"🔁 Revérification de {len(a_reverifier)} des meilleurs essais passés sur les données d'aujourd'hui…")
        for e in a_reverifier:
            if self.arret.is_set() or time.time() - t0 > budget * 0.45:
                break
            avant = e["auc_recherche"]
            tester("Revérifié : " + re.sub(r"^(Revérifié : |🧭 )+", "", e["nom"])[:90], e["variables"], e["par_marche"],
                   dict(e.get("params") or {}), force=True)
            if essais and essais[-1]["nom"].startswith("Revérifié"):
                essais[-1]["auc_avant"] = avant
        i, guides, aleatoires = 1, 0, 0
        while not self.arret.is_set() and len(essais) < max_essais and time.time() - t0 < budget:
            # les meilleurs essais de CETTE séance (tous notés sur les mêmes données)
            meilleurs = sorted([e for e in essais if e.get("teste_completement", True)
                                and "membres" not in (e.get("params") or {})],
                               key=lambda e: -e["auc_recherche"])[:5]
            cand, attendu = None, None
            # 3 essais sur 4 sont choisis par la carte ; 1 sur 4 reste une idée neuve tirée au hasard
            if i % 4 and carte.apprendre(memoire, essais):
                pool = []
                for k in range(300):
                    c = self._muter(rng, meilleurs, i) if (k % 2 == 0 and meilleurs) else self._tirer(rng, i)
                    if self._signature({"variables": c[1], "par_marche": c[2], "params": c[3]}) not in deja:
                        pool.append(c)
                if pool:
                    cand, attendu, incertitude = carte.choisir(pool, min(1.0, (time.time() - t0) / budget))
                if cand is not None:
                    guides += 1
                    cand = ("🧭 " + cand[0], *cand[1:])
                    if guides <= 3 or guides % 5 == 0:
                        self.log(f"   🧭 Choix guidé par la carte : gain attendu {attendu:+.4f} (± {incertitude:.4f}) par rapport à la moyenne")
            if cand is None:
                for _ in range(20):
                    cand = self._muter(rng, meilleurs, i) if (i % 2 == 0 and meilleurs) else self._tirer(rng, i)
                    if self._signature({"variables": cand[1], "par_marche": cand[2], "params": cand[3]}) not in deja:
                        break
                aleatoires += 1
            tester(*cand)
            i += 1
        self.guidage = {"guides": guides, "aleatoires": aleatoires,
                        "reverifies": [{"nom": e["nom"], "avant": e.get("auc_avant"), "apres": e["auc_recherche"]}
                                       for e in essais if e["nom"].startswith("Revérifié")]}
        for r in self.guidage["reverifies"]:
            if r["avant"] is not None:
                self.log(f"   🔁 {r['nom'][:70]} : {r['avant']:.4f} autrefois → {r['apres']:.4f} aujourd'hui")
        self.lecons = carte.lecons(memoire, [e for e in essais if "membres" not in (e.get("params") or {})])
        if self.lecons:
            self.log("📚 Ce que la carte a appris de tous les essais (écart moyen par rapport aux autres) :")
            for nom, d, n in self.lecons[:3]:
                self.log(f"   ↑ {nom} : {d:+.4f} ({n} essais)")
            for nom, d, n in self.lecons[-2:]:
                self.log(f"   ↓ {nom} : {d:+.4f} ({n} essais)")
        self.progres("recherche", 1)
        if not any(e["nom"] == champion for e in essais):
            tester(champion, v_ch, pm_ch, p_ch, force=True)
        complets = sorted([e for e in essais if e["teste_completement"]], key=lambda e: -e["auc_recherche"])

        self._ecrire_memoire(memoire, essais)
        if cols_utiles:   # l'IA améliore son manuel : seulement les règles prouvées, dans leur meilleure version
            tester(f"Indicateurs de base + {len(cols_utiles)} connaissances prouvées", model.VARIABLES_BASE + cols_utiles, False, {}, force=True)
            complets = sorted([e for e in essais if e["teste_completement"]], key=lambda e: -e["auc_recherche"])

        self.etape(6, "Tri des indicateurs : lesquels aident vraiment ?")
        imp = {}
        if complets:
            m0 = complets[0]
            imp = self._importance(jeu_sel, m0)
            if imp:
                utiles = [k for k, (a, b) in sorted(imp.items(), key=lambda kv: -min(kv[1])) if a > SEUIL_INDICATEUR and b > SEUIL_INDICATEUR]
                self.log(f"{len(utiles)} indicateurs aident sur les deux périodes testées ; "
                         f"{len(imp) - len(utiles)} n'apportent rien de sûr.")
                if utiles:
                    self.log("Les plus utiles : " + ", ".join(utiles[:8]))
                if 8 <= len(utiles) < len(m0["variables"]):
                    tester(f"Sélection automatique : {len(utiles)} indicateurs utiles", utiles, m0["par_marche"], m0["params"], force=True)
                    complets = sorted([e for e in essais if e["teste_completement"]], key=lambda e: -e["auc_recherche"])
        self.progres("tri", 1)

        self.etape(7, "Examen final sur les années mises sous clé")
        finalistes = complets[:3] + [e for e in essais if e["nom"] == champion and e not in complets[:3]]
        resultats = []
        for k, e in enumerate(finalistes, 1):
            o = self._final(jeu, coupure, e["variables"], e["par_marche"], e["params"])
            self.progres("final", k / len(finalistes))
            if o is None:
                continue
            e["auc_final"] = model._auc(o["cible"].to_numpy(), o["proba"].to_numpy())
            resultats.append((e, o))
            self.log(f"AUC à l'examen final {e['auc_final']:.4f} · {e['nom']}{'  ← IA du site' if e['nom'] == champion else ''}")
        if not resultats:
            raise RuntimeError("Examen final impossible : pas assez d'années de données.")
        # Comité des meilleures recettes : la moyenne de plusieurs bonnes IA différentes est souvent plus juste
        # et plus stable que chacune seule (technique très utilisée par les professionnels). Jugé lui aussi à l'examen.
        membres = [(e, o) for e, o in resultats if e["nom"] != champion][:3]
        if len(membres) >= 2 and all(len(o) == len(membres[0][1]) for _, o in membres):
            o_c = membres[0][1].copy()
            o_c["proba"] = np.mean([o["proba"].to_numpy() for _, o in membres], axis=0)
            ec = {"nom": f"Comité des {len(membres)} meilleures recettes", "variables": sorted({v for e, _ in membres for v in e["variables"]}),
                  "par_marche": False, "params": {"membres": [{"variables": e["variables"], "par_marche": e["par_marche"],
                                                               "params": e["params"]} for e, _ in membres]},
                  "auc_recherche": float(np.mean([e["auc_recherche"] for e, _ in membres])), "teste_completement": True}
            ec["auc_final"] = model._auc(o_c["cible"].to_numpy(), o_c["proba"].to_numpy())
            essais.append(ec)
            resultats.append((ec, o_c))
            self.log(f"AUC à l'examen final {ec['auc_final']:.4f} · {ec['nom']} (moyenne de leurs avis)")
        resultats.sort(key=lambda r: -r[0]["auc_final"])
        gagnant, o_g = resultats[0]
        ref = next(((e, o) for e, o in resultats if e["nom"] == champion), None)
        decision = {"change": False, "raison": "L'IA du site reste la meilleure à l'examen final."}
        if ref and gagnant["nom"] != champion:
            o_c = ref[1]
            if len(o_g) == len(o_c) and (o_g.index.values == o_c.index.values).all():
                duo = pd.DataFrame({"cible": o_g["cible"].to_numpy(), "pa": o_g["proba"].to_numpy(),
                                    "pb": o_c["proba"].to_numpy()}, index=o_g.index)
                ic, _, _, moities = self._comparer(duo)
                if ic and ic[0] > 0 and moities:
                    decision = {"change": True, "ic_gain_auc": ic,
                                "raison": "La nouvelle IA fait mieux de façon prouvée (95 %) ET sur chaque moitié de l'examen final."}
                elif ic and ic[0] > 0:
                    decision = {"change": False, "ic_gain_auc": ic,
                                "raison": "Meilleure en moyenne, mais pas sur chaque moitié de l'examen : pas assez régulière, on ne change pas."}
                else:
                    decision = {"change": False, "ic_gain_auc": ic,
                                "raison": "Un meilleur score, mais l'écart peut venir du hasard : on garde l'IA du site."}
        elif not ref:
            decision = {"change": False, "raison": "L'IA du site n'a pas pu être évaluée : par prudence, rien ne change."}
        retenu, o_r = (gagnant, o_g) if decision["change"] else (ref or (gagnant, o_g))
        ev, _ = model._evaluation(o_r)
        self.progres("final", 1)
        self.log(decision["raison"])
        erreurs = self._analyse_erreurs(o_r)
        horizons = None
        if args.duree != "rapide" and not self.arret.is_set():
            try:
                horizons = self._examen_horizons(coupure, retenu, reglage["pas"])
            except Exception as ex:
                self.log(f"(Examen des horizons impossible cette fois : {ex})")

        entree = {"date": datetime.now().isoformat(timespec="minutes"), "mode": args.duree,
                  "demo": args.demo, "arret_manuel": self.arret.is_set(),
                  "nb_titres": len(affiches) + len(supp_base) + (len(supp_etendu) if garder_etendu else 0),
                  "nb_lignes": int(len(jeu)), "series_economiques": sorted(contexte), "nb_essais": len(essais),
                  "coupure": f"{pd.Timestamp(coupure):%Y-%m-%d}",
                  "candidats": [{"nom": e["nom"], "auc_recherche": e["auc_recherche"], "auc_final": e.get("auc_final"),
                                 "complet": e["teste_completement"]} for e in sorted(essais, key=lambda e: -e["auc_recherche"])],
                  "importance": {k: min(v) for k, v in sorted(imp.items(), key=lambda kv: -min(kv[1]))[:15]} if imp else {},
                  "en_place": champion, "retenu": retenu["nom"], "change_methode": decision["change"],
                  "raison": decision["raison"], "ic_gain_auc": decision.get("ic_gain_auc"), "examen_donnees": examen_donnees,
                  "precision": ev.precision, "ic_precision": ev.ic.get("precision"), "auc": ev.auc,
                  "auc_recherche_retenu": retenu["auc_recherche"], "precision_base": ev.precision_base,
                  "niveau_preuve": ev.niveau_preuve(), "connaissances": verdicts, "erreurs": erreurs,
                  "guidage": getattr(self, "guidage", None), "lecons": getattr(self, "lecons", None),
                  "horizons": horizons}
        recette = {"nom": retenu["nom"], "variables": retenu["variables"], "par_marche": retenu["par_marche"],
                   **({"membres": retenu["params"]["membres"]} if "membres" in retenu["params"] else {}),
                   "params": retenu["params"], "date": entree["date"], "auc": retenu.get("auc_final")}
        apprentissage = {mk: [t for t in lst if t in supp_etendu] for mk, lst in etendu.items()} if garder_etendu else None
        chemin = ecrire_rapport(entree, ev)
        self.resultat = {"entree": entree, "decision": decision, "recette": recette, "ancien": ancien,
                         "apprentissage": apprentissage, "rapport": chemin, "ev": ev, "garder_etendu": garder_etendu,
                         "change": decision["change"] or garder_etendu}
        self.emettre("final", auc=retenu.get("auc_final"), champion_auc=(ref[0]["auc_final"] if ref else None))
        self.emettre("progres", pct=1.0)
        self.emettre("resultat", resultat=self.resultat)

    def _donnees(self, config, data):
        from bourse_bot import indicators
        noms, marche_de = {}, {}
        for m, univers in config.UNIVERS.items():
            for t in univers:
                noms[t], marche_de[t] = univers[t], m
        base = config.entrainement_supplementaire()
        etendu = {m: [t for t in v if t not in noms] for m, v in UNIVERS_ETENDU.items()}
        tout_base = {t: m for m, v in base.items() for t in v if t not in noms}
        tout_etendu = {t: m for m, v in etendu.items() for t in v if t not in noms and t not in tout_base}
        a_telecharger = list(dict.fromkeys(list(noms) + list(tout_base) + list(tout_etendu) + list(config.BENCHMARK.values())))
        self.log(f"{len(a_telecharger)} titres à télécharger (jusqu'à 20 ans d'historique), par lots pour ne pas être bloqué par Yahoo…")
        t0 = time.time()
        bruts = data.telecharger_plusieurs(a_telecharger, progres=lambda f: self.progres("collecte", 0.7 * f))
        manquants = [t for t in a_telecharger if t not in bruts]
        self.log(f"✅ {len(bruts)} titres reçus sur {len(a_telecharger)} ({duree(time.time() - t0)})."
                 + (f" Introuvables, ignorés sans conséquence : {', '.join(manquants[:12])}{'…' if len(manquants) > 12 else ''}" if manquants else ""))
        self.log("Données économiques (VIX, taux, courbe des taux, dollar, or, pétrole, cuivre, crédit, chômage)…")
        try:
            contexte = data.macro()
        except Exception:
            contexte = {}
        self.log(f"✅ {len(contexte)} séries économiques : {', '.join(sorted(contexte)) or 'aucune'}.")
        self.progres("collecte", 0.8)

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
        self.log("Calcul de plus de 50 indicateurs par titre…")
        affiches = {t: d for t in noms if (d := calc(t, marche_de[t], 260)) is not None}
        supp_base = {t: d for t, m in tout_base.items() if (d := calc(t, m, 400)) is not None}
        supp_etendu = {t: d for t, m in tout_etendu.items() if (d := calc(t, m, 400)) is not None}
        marches = {t: ("crypto" if t.endswith("-USD") else m) for t, m in {**marche_de, **tout_base, **tout_etendu}.items()}
        lignes = sum(len(d) for d in (*affiches.values(), *supp_base.values(), *supp_etendu.values()))
        annees = max((len(d) for d in affiches.values()), default=0) / 252
        self.log(f"✅ {len(affiches)} titres du site + {len(supp_base) + len(supp_etendu)} titres d'apprentissage · "
                 + f"{lignes:,}".replace(",", " ") + f" journées de cotation · jusqu'à {annees:.0f} ans.")
        self.progres("collecte", 1)
        return affiches, supp_base, supp_etendu, marches, contexte, etendu

    def _zone_recherche(self, jeu, coupure):
        np = self.np
        dates = np.array(sorted(jeu.index.unique()))
        i = int(np.searchsorted(dates, coupure))
        return jeu[jeu.index <= dates[max(i - self.horizon - 2, 0)]]

    def _final(self, jeu, coupure, v, pm, prm):
        """Examen final : années sous clé, en deux moitiés, chacune prédite par une IA entraînée avant elle."""
        np, pd, model = self.np, self.pd, self.model
        et = jeu.dropna(subset=["cible"])
        dates = np.array(sorted(et.index.unique()))
        zone = dates[dates > coupure]
        if len(zone) < 60:
            return None
        morceaux = []
        for part in (zone[: len(zone) // 2], zone[len(zone) // 2:]):
            i = int(np.searchsorted(dates, part[0]))
            train = et[et.index <= dates[max(i - self.horizon - 2, 0)]]
            test = et[(et.index >= part[0]) & (et.index <= part[-1])]
            if len(train) < 2000 or test.empty:
                continue
            t = test[["cible", "rendement_futur", "marche", "ticker"]].copy()
            t["technique"] = model.technique_haussiere(test).to_numpy()
            t["proba"] = model.Predicteur(v, pm, "ia1", prm).fit(train).predict_proba(test)
            morceaux.append(t)
        return pd.concat(morceaux) if morceaux else None

    def _comparer(self, duo):
        """Gain d'AUC de pa sur pb : marge d'erreur (bootstrap par mois) et régularité (meilleur sur
        chaque moitié de la période)."""
        np, model = self.np, self.model
        y = duo["cible"].to_numpy()
        a, b = model._auc(y, duo["pa"].to_numpy()), model._auc(y, duo["pb"].to_numpy())
        boot = model.bootstrap_mois(duo, lambda d: np.array([model._auc(d["cible"].to_numpy(), d["pa"].to_numpy())
                                                             - model._auc(d["cible"].to_numpy(), d["pb"].to_numpy())]), graine=7)
        ic = model._ic(boot[:, 0]) if len(boot) else None
        dates = np.array(sorted(duo.index.unique()))
        moities = True
        for part in (dates[: len(dates) // 2], dates[len(dates) // 2:]):
            d = duo[duo.index.isin(part)]
            if len(d) and model._auc(d["cible"].to_numpy(), d["pa"].to_numpy()) <= model._auc(d["cible"].to_numpy(), d["pb"].to_numpy()):
                moities = False
        return ic, a, b, moities

    def _tirer(self, rng, i):
        model = self.model
        technique = [v for v in model.VARIABLES if v not in MACRO]
        cx = [v for v in model.VARIABLES if v.startswith("cx_")]
        groupes = {"tous les indicateurs + économie + manuel": list(model.VARIABLES),
                   "indicateurs de base + économie": model.VARIABLES_BASE + sorted(MACRO & set(model.VARIABLES)),
                   "indicateurs de base + manuel de Bourse": model.VARIABLES_BASE + cx,
                   "indicateurs de base + manuel prouvé": model.VARIABLES_BASE + (self.cols_utiles or cx),
                   "indicateurs techniques seulement": [v for v in technique if not v.startswith("cx_")],
                   "indicateurs de base": list(model.VARIABLES_BASE)}
        g = list(groupes)[rng.integers(len(groupes))]
        prm = {"profondeur": int(rng.choice([2, 3, 4, 5])), "apprentissage": float(rng.choice([0.02, 0.03, 0.05, 0.08])),
               "iterations": int(rng.choice([150, 250, 400, 600])), "feuille": int(rng.choice([150, 300, 600, 1000])),
               "l2": float(rng.choice([0.5, 2.0, 5.0])), "c_lin": float(rng.choice([0.01, 0.05, 0.2]))}
        dv = rng.choice([0, 0, 3, 6, 10])   # mémoire qui s'estompe (0 = toutes les années comptent pareil)
        if dv:
            prm["demi_vie"] = int(dv)
        pm = bool(rng.random() < 0.35)
        return (f"Essai {i} : {g}, profondeur {prm['profondeur']}, {prm['iterations']} étapes"
                + (", un modèle par marché" if pm else "")), groupes[g], pm, prm

    def _analyse_erreurs(self, o):
        """Apprendre de ses erreurs : où l'IA se trompe-t-elle le plus à l'examen final ?"""
        np = self.np
        y, p = o["cible"].to_numpy(), o["proba"].to_numpy()
        juste = (p > 0.5) == (y == 1)
        noms = {"fr": "actions françaises", "eu": "actions européennes", "us": "actions américaines",
                "crypto": "cryptos", "etf": "ETF et indices", "tendances": "titres en tendance"}
        par_marche = [{"nom": noms.get(m, m), "nb": int(g.sum()), "precision": float(juste[g].mean())}
                      for m in sorted(set(o["marche"])) if (g := (o["marche"] == m).to_numpy()).sum() >= 200]
        conf = np.abs(p - 0.5)
        par_conf = []
        for nom, a, b in (("avis prudents (45–55 %)", 0, 0.05), ("avis nets (55–60 % ou 40–45 %)", 0.05, 0.10),
                          ("avis très nets (plus de 60 % ou moins de 40 %)", 0.10, 1)):
            g = (conf >= a) & (conf < b)
            if g.sum() >= 100:
                par_conf.append({"nom": nom, "nb": int(g.sum()), "precision": float(juste[g].mean())})
        if par_marche:
            pire = min(par_marche, key=lambda x: x["precision"])
            meilleur = max(par_marche, key=lambda x: x["precision"])
            self.log(f"🔍 Erreurs : l'IA se trompe le plus sur les {pire['nom']} ({pire['precision'] * 100:.0f} % justes) "
                     f"et le moins sur les {meilleur['nom']} ({meilleur['precision'] * 100:.0f} %).")
        if len(par_conf) >= 2 and par_conf[-1]["precision"] <= par_conf[0]["precision"]:
            self.log("🔍 Ses avis les plus tranchés ne sont pas plus justes que les prudents : le site les adoucira "
                     "(la correction par les vraies erreurs s'en charge en ligne).")
        return {"par_marche": par_marche, "par_confiance": par_conf}

    @staticmethod
    def _signature(e):
        return json.dumps([sorted(e["variables"]), bool(e["par_marche"]), sorted((e.get("params") or {}).items())])

    def _examen_horizons(self, coupure, e, pas):
        """À quel horizon l'IA est-elle la plus fiable ? Même recette, testée à 1 semaine, 1 mois et 3 mois,
        sur la zone de recherche (les années sous clé ne sont pas utilisées)."""
        np, model = self.np, self.model
        if "membres" in (e.get("params") or {}):
            e = {"variables": model.VARIABLES_BASE, "par_marche": False, "params": {}}
        self.log("🔭 Examen des horizons : à quelle échéance l'IA est-elle la plus fiable ?")
        out = []
        for h, nom in ((5, "1 semaine"), (20, "1 mois"), (60, "3 mois")):
            if self.arret.is_set():
                break
            jeu_h = model.construire_jeu(self.donnees_jeu, self.marches_jeu, h)
            z = self._zone_recherche(jeu_h, coupure)
            jours = np.array(sorted(z.index.unique()))[::max(pas, 3)]
            z = z[z.index.isin(jours)]
            o = model.predictions_hors_echantillon(z, h, e["variables"], e["par_marche"], n_plis=3, params=e.get("params"))
            if o is None or o["cible"].nunique() < 2:
                continue
            y, p = o["cible"].to_numpy(), o["proba"].to_numpy()
            auc = model._auc(y, p)
            base = float(max(y.mean(), 1 - y.mean()))
            prec = model._precision(y, p)
            out.append({"horizon": h, "nom": nom, "auc": auc, "precision": prec, "base": base, "nb": int(len(o))})
            self.log(f"   {nom} : AUC {auc:.4f} · bonne direction {prec * 100:.1f} % (toujours la même réponse : {base * 100:.1f} %)")
        if out:
            m = max(out, key=lambda x: x["auc"])
            self.log(f"   → L'IA est la plus fiable à {m['nom']}. (Le site garde un mois ; c'est une information pour la suite.)")
        return out

    def _fichier_essais(self):
        # en démo (données fictives), la mémoire est rangée à part pour ne jamais se mélanger aux vrais essais
        return os.path.join(".cache_entrainement", "essais_demo.json") if self.args.demo else FICHIER_ESSAIS

    def _meilleurs_passes(self, memoire, exclus, n=6):
        """Les meilleurs essais passés, classés par écart à la moyenne de leur propre séance."""
        np = self.np
        par_seance = {}
        for e in memoire:
            par_seance.setdefault(e.get("date") or "ancien", []).append(e["auc_recherche"])
        moy = {k: float(np.mean(v)) for k, v in par_seance.items()}
        vus, res = set(exclus), []
        for e in sorted(memoire, key=lambda e: -(e["auc_recherche"] - moy[e.get("date") or "ancien"])):
            sig = self._signature(e)
            if sig in vus or "membres" in (e.get("params") or {}):
                continue
            vus.add(sig)
            res.append(e)
            if len(res) >= n:
                break
        return res

    def _lire_memoire(self):
        try:
            with open(self._fichier_essais(), encoding="utf-8") as f:
                m = json.load(f)
            vars_ok = set(self.model.VARIABLES)
            return [e for e in m.get("essais", []) if set(e["variables"]) <= vars_ok][-600:]
        except (OSError, ValueError, KeyError):
            return []

    def _ecrire_memoire(self, memoire, essais):
        try:
            os.makedirs(os.path.dirname(self._fichier_essais()), exist_ok=True)
            jour = datetime.now().strftime("%Y-%m-%d")
            nouveaux = [{k: v for k, v in e.items() if k not in ("auc_avant", "auc_final")} | {"date": jour}
                        for e in essais if e.get("teste_completement") and "membres" not in (e.get("params") or {})]
            # une seule note par réglage et par jour (la plus récente)
            tout, vus = [], set()
            for e in reversed(memoire + nouveaux):
                cle = (self._signature(e), e.get("date"))
                if cle not in vus:
                    vus.add(cle)
                    tout.append(e)
            with open(self._fichier_essais(), "w", encoding="utf-8") as f:
                json.dump({"essais": list(reversed(tout))[-600:]}, f, ensure_ascii=False)
        except OSError:
            pass

    def _muter(self, rng, meilleurs, i):
        """Amélioration : reprend un des meilleurs essais et change un ou deux réglages."""
        base = meilleurs[int(rng.integers(len(meilleurs)))]
        prm = dict(base.get("params") or {})
        defaut = {"profondeur": 3, "apprentissage": 0.04, "iterations": 250, "feuille": 300, "l2": 2.0, "c_lin": 0.05,
                  "demi_vie": 6}
        for _ in range(int(rng.integers(1, 3))):
            k = list(defaut)[int(rng.integers(len(defaut)))]
            v = prm.get(k, defaut[k])
            if k == "profondeur":
                prm[k] = int(min(6, max(2, v + rng.choice([-1, 1]))))
            elif k == "iterations":
                prm[k] = int(min(900, max(100, v * rng.choice([0.7, 1.4]))))
            elif k == "demi_vie":
                prm[k] = int(rng.choice([3, 4, 6, 8, 10, 15]))
            elif k == "feuille":
                prm[k] = int(min(2000, max(100, v * rng.choice([0.5, 2.0]))))
            else:
                prm[k] = float(round(v * rng.choice([0.6, 1.6]), 4))
        pm = base["par_marche"] if rng.random() > 0.15 else not base["par_marche"]
        nom = f"Amélioration {i} (variante d'un des meilleurs : " + ", ".join(f"{k} {prm[k]}" for k in sorted(prm)) + ")"
        return nom, list(base["variables"]), bool(pm), prm

    def _importance(self, jeu_sel, e, colonnes=None, phase="tri"):
        """Un indicateur n'est gardé que s'il aide sur DEUX périodes différentes (pas un hasard)."""
        np, model = self.np, self.model
        et = jeu_sel.dropna(subset=["cible"])
        dates = np.array(sorted(et.index.unique()))
        res = {}
        for k, frac in enumerate((0.6, 0.8)):
            cut = int(len(dates) * frac)
            fin = min(int(len(dates) * (frac + 0.2)), len(dates)) - 1
            train = et[et.index <= dates[max(cut - self.horizon - 2, 0)]]
            valid = et[(et.index > dates[cut]) & (et.index <= dates[fin])]
            if len(train) < 5000 or len(valid) < 2000:
                return {}
            mod = model.Predicteur(e["variables"], e["par_marche"], "ia1", e["params"]).fit(train)
            y = valid["cible"].to_numpy()
            base = model._auc(y, mod.predict_proba(valid))
            rng = np.random.default_rng(11 + k)
            for var in [v for v in mod.vars_commun if colonnes is None or v in colonnes]:
                X = valid.copy()
                X[var] = rng.permutation(X[var].to_numpy())
                res.setdefault(var, [0.0, 0.0])[k] = base - model._auc(y, mod.predict_proba(X))
            self.progres(phase, 0.5 * (k + 1))
        return {k: tuple(v) for k, v in res.items()}

    def _examen_manuel(self, jeu_sel):
        """Chaque règle du manuel est vérifiée : aide-t-elle l'IA sur DEUX périodes jamais vues ?
        Va-t-elle dans le sens annoncé par les chercheurs ? Quelle variante marche le mieux ?"""
        from bourse_bot import connaissances
        model, pd = self.model, self.pd
        cx = [v for v in model.VARIABLES if v.startswith("cx_")]
        self.cols_utiles = []
        if not cx:
            return {}, []
        imp = self._importance(jeu_sel, {"variables": list(model.VARIABLES), "par_marche": False, "params": {}},
                               colonnes=set(cx), phase="manuel")
        et = jeu_sel.dropna(subset=["cible"])
        echant = et.sample(min(len(et), 200000), random_state=3) if len(et) else et
        verdicts, utiles = {}, []
        for r in connaissances.REGLES:
            meilleure, score, sens = None, None, None
            for v in r["variantes"]:
                col = connaissances.nom_colonne(r["cle"], v)
                if col not in imp:
                    continue
                s = min(imp[col])
                if score is None or s > score:
                    meilleure, score = v, s
                    x = echant[col]
                    ok = x.notna()
                    sens = (float(pd.Series(x[ok].rank()).corr(pd.Series(echant.loc[ok, "rendement_futur"].rank())))
                            if ok.sum() > 1000 else None)
            if meilleure is None:
                verdicts[r["cle"]] = {"nom": r["nom"], "statut": "non testable", "variante": None}
                self.log(f"   ⚪ {r['nom']} : pas assez de données pour la tester.")
                continue
            # seuil exigeant : 17 versions de règles sont testées, une seule pourrait passer par pur hasard
            prouvee = all(i > SEUIL_REGLE for i in imp[connaissances.nom_colonne(r["cle"], meilleure)])
            dans_le_sens = sens is not None and sens * r["sens"] > 0
            statut = "utile" if prouvee else "pas d'effet prouvé"
            verdicts[r["cle"]] = {"nom": r["nom"], "statut": statut, "variante": meilleure, "importance": score,
                                  "sens_observe": sens, "dans_le_sens_annonce": dans_le_sens if sens is not None else None}
            if prouvee:
                utiles.append(connaissances.nom_colonne(r["cle"], meilleure))
            self.log(f"   {'🟢' if prouvee else '⚪'} {r['nom']} · meilleure version : {meilleure} · "
                     + ("aide l'IA sur les deux périodes" if prouvee else "aucun effet prouvé")
                     + ("" if sens is None else (" · va dans le sens annoncé" if dans_le_sens else " · va plutôt dans le sens inverse aujourd'hui")))
        self.cols_utiles = utiles
        self.log(f"→ {len(utiles)} règle(s) sur {len(connaissances.REGLES)} prouvée(s) utile(s). Les autres restent "
                 "disponibles, mais l'IA ne leur fait pas confiance pour l'instant.")
        self.progres("manuel", 1)
        return verdicts, utiles


# ----------------------------------------------------------------------------
# Enregistrement, publication et vérification du site
# ----------------------------------------------------------------------------
def enregistrer(res, demo):
    from bourse_bot import config, model
    entree, m = res["entree"], dict(res["ancien"])
    m["entrainements"] = (m.get("entrainements") or [])[-19:] + [entree]
    if res["decision"]["change"]:
        m["recette"] = res["recette"]
        m["configuration"] = model.NOM_RECETTE
        m["date"] = "2000-01-01T00:00:00"   # le site refera un test complet avec la nouvelle recette
        m.setdefault("version", 2)
    if demo:
        return
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    with open(model.FICHIER_MODELE, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, default=lambda v: None)
    if res["apprentissage"]:
        with open(os.path.join(config.DOSSIER_HISTORIQUE, "apprentissage.json"), "w", encoding="utf-8") as f:
            json.dump({"date": entree["date"], "tickers": res["apprentissage"]}, f, ensure_ascii=False, indent=1)


def publier(res, log) -> bool:
    """Envoie le résultat sur GitHub et lance la mise à jour du site."""
    commande("git", "add", "historique/modele.json", "historique/apprentissage.json", FICHIER_ESSAIS.replace(os.sep, "/"))
    msg = f"Entraînement du {datetime.now():%d/%m/%Y} : " + (res["recette"]["nom"] if res["decision"]["change"] else "IA confirmée")
    commande("git", "commit", "-m", msg)
    sortie = ""
    for _ in range(3):
        commande("git", "pull", "--rebase", "--autostash")
        code, sortie = commande("git", "push")
        if code == 0:
            log("✅ Résultat envoyé sur GitHub.")
            break
        time.sleep(5)
    else:
        log(f"❌ Envoi impossible : {sortie[-300:]}")
        return False
    code, _ = commande("gh", "workflow", "run", "radar.yml")
    if code != 0:
        log("⚠️ La mise à jour du site n'a pas pu être lancée tout de suite : elle se fera à la prochaine heure.")
        return False
    log("🚀 Mise à jour du site lancée sur GitHub (15 à 30 minutes).")
    return True


def surveiller_site(depuis_iso, log, etat):
    """Suit la mise à jour sur GitHub, puis analyse le site en ligne."""
    run_id = None
    for _ in range(20):
        code, sortie = commande("gh", "run", "list", "-w", "radar.yml", "-L", "5", "--json", "databaseId,createdAt")
        try:
            runs = [r for r in json.loads(sortie) if r["createdAt"] >= depuis_iso]
        except Exception:
            runs = []
        if runs:
            run_id = runs[0]["databaseId"]
            break
        time.sleep(6)
    if not run_id:
        log("⚠️ Impossible de suivre la mise à jour. Regarde l'onglet Actions de ton dépôt GitHub.")
        return
    debut, conclusion = time.time(), None
    while time.time() - debut < 100 * 60:
        code, sortie = commande("gh", "run", "view", str(run_id), "--json", "status,conclusion")
        try:
            r = json.loads(sortie)
        except Exception:
            r = {}
        etat(f"Mise à jour du site en cours sur GitHub… {duree(time.time() - debut)}")
        if r.get("status") == "completed":
            conclusion = r.get("conclusion")
            break
        time.sleep(20)
    if conclusion != "success":
        log(f"❌ La mise à jour en ligne s'est terminée avec le résultat : {conclusion or 'trop longue'}. "
            "L'ancienne version du site reste en ligne. Ouvre l'onglet Actions de GitHub pour le détail.")
        etat("Mise à jour en ligne échouée")
        return
    log(f"✅ Mise à jour terminée sur GitHub ({duree(time.time() - debut)}). Analyse du site en ligne…")
    analyser_site(log, etat)


def analyser_site(log, etat):
    url = adresse_site()
    if not url:
        log("⚠️ Adresse du site inconnue : analyse impossible.")
        return
    for _ in range(12):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{url}version.json?t={time.time():.0f}",
                                                               headers={"Cache-Control": "no-cache"}), timeout=15) as r:
                v = json.load(r)
            age = (datetime.now() - datetime.fromisoformat(v["genere_le"])).total_seconds() / 60
            with urllib.request.urlopen(url, timeout=20) as r:
                page = r.read().decode("utf-8", "replace")
            n = len(re.findall(r'"ticker":"', page))
            verifs = [("Le site répond", True), ("Prévisions de moins de 3 heures", -120 < age < 180),
                      ("Page complète", len(page) > 50000 and "Radar Bourse" in page), ("Titres présents", n >= 20),
                      ("Pas de données de démonstration", '"demo":true' not in page)]
            ok = all(b for _, b in verifs)
            for nom, b in verifs:
                log(f"   {'✅' if b else '❌'} {nom}")
            log(f"{'✅' if ok else '⚠️'} Site analysé : {url} · prévisions générées il y a {max(0, age):.0f} min · {n} titres.")
            etat("Site en ligne vérifié ✅" if ok else "Site en ligne : à vérifier ⚠️")
            return
        except Exception:
            etat("Le site se met en ligne… (GitHub peut prendre 1 à 2 minutes)")
            time.sleep(10)
    log(f"⚠️ Le site {url} ne répond pas encore. Réessaie « Analyser le site » dans quelques minutes.")
    etat("Site pas encore joignable")


# ----------------------------------------------------------------------------
# Rapport
# ----------------------------------------------------------------------------
def appris_cette_fois(e):
    """Même quand l'IA du site ne change pas, la séance n'est pas perdue : on dit ce qui a été appris."""
    g, lecons = e.get("guidage") or {}, e.get("lecons") or []
    morceaux = [f"{e.get('nb_essais', 0)} nouveaux réglages testés et mémorisés pour guider les prochaines séances"]
    if g.get("reverifies"):
        morceaux.append(f"{len(g['reverifies'])} anciens réglages revérifiés sur les données d'aujourd'hui")
    if lecons:
        morceaux.append(f"ce qui marche le mieux jusqu'ici : {lecons[0][0]}")
    return "\nCe que cette séance a appris : " + " ; ".join(morceaux) + "."


def section_guidage(e, x):
    g, lecons = e.get("guidage") or {}, e.get("lecons") or []
    if not g and not lecons:
        return ""
    fmt = lambda a: "–" if a is None else f"{a:.4f}"
    rev = "".join(f"<tr><td>{x(r['nom'])}</td><td>{fmt(r['avant'])}</td><td>{fmt(r['apres'])}</td></tr>"
                  for r in g.get("reverifies", []))
    lec = "".join(f"<tr><td>{'↑' if d > 0 else '↓'} {x(n)}</td><td>{d:+.4f}</td><td>{k}</td></tr>" for n, d, k in lecons)
    return ("<div class='c'><h2>Recherche intelligente</h2>"
            f"<p>{g.get('guides', 0)} essais choisis par la carte (là où un gain était le plus probable), "
            f"{g.get('aleatoires', 0)} idées neuves tirées au hasard pour ne pas tourner en rond. "
            "Les réglages trop proches d'un essai déjà fait sont écartés : chaque essai apprend quelque chose de nouveau.</p>"
            + (f"<h3>Meilleurs essais passés, revérifiés sur les données d'aujourd'hui</h3><table><tr><th>Réglage</th><th>Note autrefois</th><th>Note aujourd'hui</th></tr>{rev}</table>" if rev else "")
            + (f"<h3>Ce que la carte a appris (tous les essais, toutes les séances)</h3><p class='m'>Écart moyen d'AUC par rapport aux autres essais de la même séance. Positif = cette famille de réglages marche mieux.</p><table><tr><th>Famille de réglages</th><th>Écart moyen</th><th>Essais</th></tr>{lec}</table>" if lec else "")
            + "</div>")


def ecrire_rapport(e, ev):
    from bourse_bot import config
    os.makedirs(config.DOSSIER_RAPPORTS, exist_ok=True)
    chemin = os.path.join(config.DOSSIER_RAPPORTS, f"entrainement_{datetime.now():%Y%m%d_%H%M}.html")
    x = lambda s: html.escape(str(s))
    fmt = lambda a: "–" if a is None else f"{a:.4f}"
    barre = lambda a: f"<div class='b'><i style='width:{max(0, min(100, (a - AUC_HASARD) / (AUC_EXCELLENT - AUC_HASARD) * 100)):.0f}%'></i></div>" if a else ""
    lignes = "".join(
        f"<tr><td>{x(c['nom'])}{' <b>(IA du site)</b>' if c['nom'] == e['en_place'] else ''}{' <b>✓ retenue</b>' if c['nom'] == e['retenu'] else ''}"
        f"{'' if c['complet'] else ' <span class=m>(1er tour)</span>'}</td>"
        f"<td>{fmt(c['auc_recherche'])}</td><td>{fmt(c.get('auc_final'))}</td><td>{barre(c.get('auc_final') or c['auc_recherche'])}</td></tr>"
        for c in e["candidats"][:30])
    D, icp, imp = e.get("examen_donnees") or {}, e.get("ic_precision"), e.get("importance") or {}
    verdict = ("✅ L'IA a progressé de façon prouvée et régulière à l'examen final." if e["change_methode"]
               else "➖ Pas de progrès prouvé à l'examen final : l'IA du site est confirmée. C'est normal et sain : on ne change pas sur un coup de chance.")
    optimisme = (e.get("auc_recherche_retenu") or 0) - (e.get("auc") or 0)
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Entraînement de l'IA du {datetime.now():%d/%m/%Y}</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:900px;margin:0 auto;padding:24px 16px;color:#0f1b2d;background:#eef1f5}}
.c{{background:#fff;border:1px solid #d9e0e8;border-radius:10px;padding:16px;margin:14px 0;overflow-x:auto}}h1{{font-size:28px}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:8px;border-bottom:1px solid #d9e0e8;text-align:left;font-size:14.5px}}
.b{{height:10px;background:#eef1f5;border-radius:5px;min-width:100px}}.b i{{display:block;height:100%;background:#1d4fd8;border-radius:5px}}
.v{{font-size:18px;font-weight:700}}.m{{color:#5a6a80;font-size:14px}}</style></head><body>
<h1>🧠 Rapport d'entraînement de l'IA</h1><p class="m">{x(e['date'])} · {e['nb_essais']} façons de prévoir testées{' · arrêté à la main' if e.get('arret_manuel') else ''}{' · DÉMO (données fictives)' if e['demo'] else ''}</p>
<div class="c"><p class="v">{x(verdict)}</p><p>{x(e.get('raison') or '')}</p></div>
<div class="c"><h2>Ce que l'IA a étudié</h2><ul>
<li><b>{e['nb_titres']}</b> actions, ETF et cryptos, <b>{e['nb_lignes']:,}</b> situations de marché.</li>
<li>Données économiques : {x(', '.join(e['series_economiques']) or 'aucune')}.</li></ul></div>
<div class="c"><h2>Les protections contre la chance</h2><ul>
<li><b>Années sous clé</b> : après le {x(e['coupure'])}, les données n'ont servi qu'à l'examen final, jamais à la recherche.</li>
<li><b>Tests sur des années jamais vues</b>, avec une pause d'un mois entre apprentissage et test pour que rien du futur ne fuite.</li>
<li><b>Marge d'erreur à 95 %</b> calculée en tirant des mois entiers au hasard.</li>
<li><b>Régularité</b> : une nouvelle IA doit faire mieux sur chaque moitié de l'examen final, pas seulement en moyenne.</li>
<li><b>Indicateurs</b> gardés seulement s'ils aident sur deux périodes différentes.</li>
<li>Écart d'optimisme de l'IA retenue (recherche → examen final) : {optimisme:+.4f} d'AUC. Un grand écart positif signifie qu'elle avait eu de la chance pendant la recherche.</li></ul></div>
<div class="c"><h2>Examen n°1 : étudier plus de titres ?</h2>{
    f"<p>Sans les {D['nb_titres_en_plus']} titres en plus : AUC {D['auc_sans']:.4f}. Avec : {D['auc_avec']:.4f}. "
    + (f"Marge du gain : {D['ic_gain'][0]:+.4f} à {D['ic_gain'][1]:+.4f}. " if D.get('ic_gain') else "")
    + ("<b>Gain prouvé : utilisés désormais.</b>" if D.get('decision') else "<b>Gain non prouvé : liste actuelle conservée.</b>") + "</p>"
    if D else "<p>Pas assez de données pour cet examen.</p>"}</div>
<div class="c"><h2>Recherche et examen final</h2>
<p class="m">AUC : 0,5 = hasard, 1 = parfait. En Bourse, 0,52 à 0,56 est déjà un bon score. Seule la colonne « examen final » compte vraiment.</p>
<table><tr><th>Façon de prévoir</th><th>Recherche</th><th>Examen final</th><th></th></tr>{lignes}</table></div>
{section_guidage(e, x)}
{"<div class='c'><h2>À quelle échéance l'IA est-elle la plus fiable ?</h2><p class='m'>Même recette, testée sur la zone de recherche à trois horizons. Plus l'AUC est au-dessus de 0,5, mieux c'est. Comparer aussi la bonne direction à « toujours la même réponse ».</p><table><tr><th>Horizon</th><th>AUC</th><th>Bonne direction</th><th>Toujours la même réponse</th></tr>" + "".join(f"<tr><td>{x(h['nom'])}</td><td>{h['auc']:.4f}</td><td>{h['precision'] * 100:.1f} %</td><td>{h['base'] * 100:.1f} %</td></tr>" for h in e['horizons']) + "</table></div>" if e.get('horizons') else ""}
{"<div class='c'><h2>Le manuel de Bourse : verdict de l'IA</h2><p class='m'>Chaque règle connue a été vérifiée sur deux périodes jamais vues. 🟢 = aide vraiment l'IA. ⚪ = pas d'effet prouvé (la règle n'est pas forcément fausse, mais l'IA ne lui fait pas confiance).</p><table><tr><th>Règle</th><th>Verdict</th><th>Meilleure version</th><th>Sens</th></tr>" + "".join(f"<tr><td>{x(v['nom'])}</td><td>{'🟢 utile' if v['statut'] == 'utile' else '⚪ ' + x(v['statut'])}</td><td>{x(v.get('variante') or '–')}</td><td>{'comme annoncé' if v.get('dans_le_sens_annonce') else 'inverse' if v.get('dans_le_sens_annonce') is False else '–'}</td></tr>" for v in (e.get('connaissances') or {}).values()) + "</table></div>" if e.get('connaissances') else ""}
{"<div class='c'><h2>Apprendre de ses erreurs : où l'IA se trompe-t-elle ?</h2><table>" + "".join(f"<tr><td>{x(g['nom'])}</td><td>{g['nb']:,} cas</td><td>{g['precision'] * 100:.0f} % justes</td></tr>" for g in ((e.get('erreurs') or {}).get('par_marche', []) + (e.get('erreurs') or {}).get('par_confiance', []))) + "</table><p class='m'>Les marchés où elle se trompe le plus sont ceux où ses prochaines recherches (un modèle par marché, d'autres indicateurs) ont le plus à gagner.</p></div>" if e.get('erreurs') else ""}
{"<div class='c'><h2>Les indicateurs les plus utiles</h2><p class='m'>Perte d'AUC quand on mélange l'indicateur au hasard (la plus faible des deux périodes).</p><table>" + "".join(f"<tr><td>{x(k)}</td><td>{v:+.4f}</td></tr>" for k, v in imp.items()) + "</table></div>" if imp else ""}
<div class="c"><h2>L'IA retenue en chiffres simples</h2>
<p>À l'examen final, sur 100 prévisions, elle a trouvé la bonne direction <b>{ev.precision * 100:.0f} fois</b>{f" (marge d'erreur : {icp[0] * 100:.0f} à {icp[1] * 100:.0f})" if icp else ""}.
En répondant toujours la même chose, on aurait eu raison {ev.precision_base * 100:.0f} fois.</p><p><b>{x(ev.verdict())}</b></p></div>
<p class="m">Rien n'est sûr en Bourse : ce rapport mesure le passé, il ne garantit rien pour l'avenir.</p></body></html>"""
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)
    return chemin


# ----------------------------------------------------------------------------
# Fenêtre
# ----------------------------------------------------------------------------
def fenetre(args):
    import tkinter as tk
    from tkinter import messagebox, ttk

    q = queue.Queue()
    moteur = Moteur(args, lambda type_, **kw: q.put((type_, kw)))
    racine = tk.Tk()
    racine.title("Radar Bourse · Entraînement de l'IA" + (" (démo)" if args.demo else ""))
    racine.geometry("920x760")
    racine.minsize(700, 560)
    BG, INK, MUTED, ACC, UP, WARN = "#0f1b2d", "#e4ebf5", "#8c9bb0", "#7398ff", "#35c27d", "#e5b453"
    racine.configure(bg=BG)
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Barre.Horizontal.TProgressbar", troughcolor="#22314a", background=ACC, thickness=22, bordercolor=BG)
    police = ("Segoe UI", 11)
    etat_fen = {"erreur": False, "en_attente": False}

    tk.Label(racine, text="🧠 Entraînement de l'IA", font=("Segoe UI", 20, "bold"), fg=INK, bg=BG).pack(anchor="w", padx=18, pady=(14, 0))
    lib_etape = tk.Label(racine, text="Démarrage…", font=("Segoe UI", 12), fg=MUTED, bg=BG)
    lib_etape.pack(anchor="w", padx=18)

    cadre = tk.Frame(racine, bg=BG)
    cadre.pack(fill="x", padx=18, pady=(10, 4))
    pct_var = tk.StringVar(value="0 %")
    tk.Label(cadre, text="Progression de l'entraînement", font=police, fg=INK, bg=BG).grid(row=0, column=0, sticky="w")
    tk.Label(cadre, textvariable=pct_var, font=("Segoe UI", 11, "bold"), fg=INK, bg=BG).grid(row=0, column=1, sticky="e")
    barre = ttk.Progressbar(cadre, style="Barre.Horizontal.TProgressbar", maximum=1000)
    barre.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)
    cadre.columnconfigure(0, weight=1)

    tk.Label(racine, text="Ce que l'IA a appris (testé sur des années qu'elle n'a jamais vues)",
             font=police, fg=INK, bg=BG).pack(anchor="w", padx=18, pady=(10, 0))
    jauge = tk.Canvas(racine, height=96, bg=BG, highlightthickness=0)
    jauge.pack(fill="x", padx=18)
    lib_niveau = tk.Label(racine, text="La jauge se remplit pendant la recherche.", font=police, fg=MUTED, bg=BG,
                          justify="left", wraplength=860)
    lib_niveau.pack(anchor="w", padx=18)
    etat_j = {"meilleur": None, "champion": None, "final": None}

    def dessiner_jauge():
        jauge.delete("all")
        w = max(300, jauge.winfo_width())
        x0, x1, y = 12, w - 12, 44
        xa = lambda a: x0 + (x1 - x0) * max(0, min(1, (a - AUC_HASARD) / (AUC_EXCELLENT - AUC_HASARD)))
        for a, b, c in ((0.50, 0.51, "#3a1716"), (0.51, 0.53, "#33270d"), (0.53, 0.56, "#11301f"), (0.56, 0.58, "#145c39")):
            jauge.create_rectangle(xa(a), y - 12, xa(b), y + 12, fill=c, outline="")
        if etat_j["meilleur"] is not None:
            jauge.create_rectangle(xa(0.50), y - 5, xa(etat_j["meilleur"]), y + 5, fill=ACC, outline="")
        for a, t in ((0.50, "hasard"), (0.52, "léger"), (0.54, "bon"), (0.56, "très bon"), (0.58, "exceptionnel")):
            jauge.create_text(xa(a), y + 28, text=t, fill=MUTED, font=("Segoe UI", 9),
                              anchor="nw" if a == 0.50 else "ne" if a == 0.58 else "n")
        if etat_j["champion"] is not None:
            xc = xa(etat_j["champion"])
            jauge.create_line(xc, y - 18, xc, y + 18, fill=WARN, width=3)
            jauge.create_text(xc - 6, y - 20, text="IA du site", fill=WARN, font=("Segoe UI", 9, "bold"), anchor="se")
        if etat_j["final"] is not None:
            xf = xa(etat_j["final"])
            jauge.create_oval(xf - 8, y - 8, xf + 8, y + 8, fill=UP, outline=INK, width=2)
            jauge.create_text(xf + 6, y - 20, text="examen final", fill=UP, font=("Segoe UI", 9, "bold"), anchor="sw")
    jauge.bind("<Configure>", lambda e: dessiner_jauge())

    journal = tk.Text(racine, height=12, bg="#111a29", fg=INK, insertbackground=INK, font=("Consolas", 10), relief="flat", wrap="word")
    journal.pack(fill="both", expand=True, padx=18, pady=(10, 6))
    journal.configure(state="disabled")

    bas = tk.Frame(racine, bg=BG)
    bas.pack(fill="x", padx=18, pady=(0, 14))
    lib_etat = tk.Label(bas, text="", font=police, fg=MUTED, bg=BG)
    lib_etat.pack(side="left")
    btn_arret = tk.Button(bas, text="⏹ Arrêter et passer à l'examen final", font=police, bg="#22314a", fg=INK,
                          activebackground="#2b3d5c", relief="flat", padx=12, pady=6)
    btn_arret.pack(side="right")
    actions = tk.Frame(racine, bg=BG)
    debut = time.time()

    def ecrire(t):
        journal.configure(state="normal")
        journal.insert("end", t + "\n")
        journal.see("end")
        journal.configure(state="disabled")

    def demander_arret():
        if moteur.resultat is not None or moteur.arret.is_set():
            return
        if messagebox.askyesno("Arrêter l'entraînement ?",
                               "L'IA va arrêter de chercher et passer l'examen final avec ce qu'elle a déjà appris "
                               "(quelques minutes), puis te proposer de mettre à jour le site.\n\nArrêter maintenant ?"):
            moteur.arret.set()
            btn_arret.configure(state="disabled", text="Arrêt demandé : examen final en cours…")
            ecrire("⏹ Arrêt demandé : l'IA termine l'essai en cours puis passe l'examen final.")

    def fermer():
        if moteur.resultat is None and not etat_fen["erreur"]:
            demander_arret()
            return
        if etat_fen["en_attente"] and not messagebox.askyesno(
                "Quitter ?", "Le résultat n'a pas été envoyé sur le site. Quitter quand même ?"):
            return
        racine.destroy()

    btn_arret.configure(command=demander_arret)
    racine.protocol("WM_DELETE_WINDOW", fermer)
    journal_q = lambda t: q.put(("log", {"texte": t}))
    etat_q = lambda t: q.put(("etat", {"texte": t}))

    def proposer(res):
        etat_fen["en_attente"] = True
        btn_arret.pack_forget()
        actions.pack(fill="x", padx=18, pady=(0, 14), before=bas)
        d, ev = res["decision"], res["ev"]
        txt = (("✅ L'IA a progressé de façon prouvée et régulière." if d["change"] else
                "✅ Les titres en plus améliorent l'IA de façon prouvée." if res["change"] else
                "➖ Pas de progrès prouvé : l'IA du site est confirmée (c'est normal et sain).")
               + f"\n{d['raison']}\nÀ l'examen final : bonne direction {ev.precision * 100:.0f} fois sur 100"
               + (f" (marge {ev.ic['precision'][0] * 100:.0f} à {ev.ic['precision'][1] * 100:.0f})" if ev.ic.get("precision") else "")
               + f", contre {ev.precision_base * 100:.0f} en répondant toujours la même chose."
               + appris_cette_fois(res["entree"]))
        tk.Label(actions, text=txt, font=("Segoe UI", 11, "bold"), fg=UP if res["change"] else WARN, bg=BG,
                 justify="left", wraplength=860).pack(anchor="w", pady=(0, 8))
        rangee = tk.Frame(actions, bg=BG)
        rangee.pack(fill="x")
        peut = moteur.depot_git and not args.demo

        def envoyer():
            etat_fen["en_attente"] = False
            b_env.configure(state="disabled")
            b_rien.configure(state="disabled")
            depuis = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            def tache():
                enregistrer(res, args.demo)
                if publier(res, journal_q):
                    surveiller_site(depuis, journal_q, etat_q)
                else:
                    analyser_site(journal_q, etat_q)
            threading.Thread(target=tache, daemon=True).start()

        def garder_local():
            etat_fen["en_attente"] = False
            enregistrer(res, args.demo)
            ecrire("Résultat gardé sur ton PC, rien n'a été envoyé sur le site.")

        lib = "🚀 Mettre à jour le site avec la nouvelle IA" if res["change"] else "📤 Envoyer le résultat et vérifier le site"
        b_env = tk.Button(rangee, text=lib, font=("Segoe UI", 11, "bold"), bg=ACC, fg="#0a111d", relief="flat", padx=12, pady=6,
                          state="normal" if peut else "disabled", command=envoyer)
        b_env.pack(side="left")
        tk.Button(rangee, text="🔎 Analyser le site en ligne", font=police, bg="#22314a", fg=INK, relief="flat", padx=12, pady=6,
                  command=lambda: threading.Thread(target=analyser_site, args=(journal_q, etat_q), daemon=True).start()
                  ).pack(side="left", padx=8)
        tk.Button(rangee, text="📄 Voir le rapport", font=police, bg="#22314a", fg=INK, relief="flat", padx=12, pady=6,
                  command=lambda: webbrowser.open("file://" + os.path.abspath(res["rapport"]))).pack(side="left")
        b_rien = tk.Button(rangee, text="Ne rien envoyer", font=police, bg=BG, fg=MUTED, relief="flat", padx=12, pady=6,
                           command=garder_local)
        b_rien.pack(side="right")
        if not peut:
            ecrire("ℹ️ Envoi impossible : " + ("mode démo." if args.demo else
                                               "ce dossier n'est pas relié à GitHub (lance d'abord mettre_en_ligne.bat depuis ce dossier)."))

    def relever():
        try:
            while True:
                type_, kw = q.get_nowait()
                if type_ == "log":
                    ecrire(kw["texte"])
                elif type_ == "etape":
                    lib_etape.configure(text=f"Étape {kw['n']}/7 · {kw['texte']}")
                elif type_ == "progres":
                    barre["value"] = kw["pct"] * 1000
                    ecoule = time.time() - debut
                    reste = ecoule / kw["pct"] - ecoule if kw["pct"] > 0.05 else None
                    pct_var.set(f"{kw['pct'] * 100:.0f} %" + (f" · encore ~{duree(reste)}" if reste and kw["pct"] < 1 else ""))
                elif type_ == "niveau":
                    etat_j["meilleur"] = m = kw["meilleur"]
                    lib_niveau.configure(text=f"Meilleure trouvée : AUC {m:.4f}, soit {(m - 0.5) * 100:+.1f} points au-dessus du hasard · "
                                              f"{kw['essais']} façons de prévoir testées. Ce score est un peu optimiste : "
                                              "seul l'examen final dira la vérité.")
                    dessiner_jauge()
                elif type_ == "final":
                    etat_j["final"], etat_j["champion"] = kw["auc"], kw["champion_auc"]
                    lib_niveau.configure(text=f"Examen final (années sous clé) : AUC {kw['auc']:.4f} (rond vert)"
                                              + (f" · IA du site : {kw['champion_auc']:.4f} (trait jaune)" if kw["champion_auc"] else ""))
                    dessiner_jauge()
                elif type_ == "resultat":
                    lib_etape.configure(text="Entraînement terminé")
                    lib_etat.configure(text=f"Durée : {duree(time.time() - debut)}")
                    proposer(kw["resultat"])
                elif type_ == "etat":
                    lib_etat.configure(text=kw["texte"])
                elif type_ == "erreur":
                    etat_fen["erreur"] = True
                    ecrire("❌ Problème : " + kw["texte"][-1500:])
                    lib_etape.configure(text="Entraînement interrompu par une erreur (rien n'a été envoyé)")
                    btn_arret.configure(state="disabled")
        except queue.Empty:
            pass
        racine.after(120, relever)

    def demarrer():
        nonlocal debut
        debut = time.time()
        threading.Thread(target=moteur.lancer, daemon=True).start()

    if args.duree:
        demarrer()
    else:   # écran de choix de la durée, posé par-dessus la fenêtre
        choix = tk.Frame(racine, bg=BG)
        choix.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(choix, text="🧠 Combien de temps veux-tu entraîner l'IA ?", font=("Segoe UI", 18, "bold"), fg=INK, bg=BG
                 ).pack(anchor="w", padx=24, pady=(28, 4))
        tk.Label(choix, text="Plus l'entraînement est long, plus l'IA essaie d'idées. Tu pourras l'arrêter à tout moment : "
                             "elle passera alors l'examen final avec ce qu'elle a déjà appris.",
                 font=police, fg=MUTED, bg=BG, wraplength=840, justify="left").pack(anchor="w", padx=24, pady=(0, 18))

        def choisir(cle):
            args.duree = cle
            choix.destroy()
            demarrer()
        for cle, r in DUREES.items():
            b = tk.Button(choix, text=f"{r['nom']}\n{r['resume']}", font=("Segoe UI", 13, "bold"), justify="left", anchor="w",
                          bg=ACC if cle == "normal" else "#22314a", fg="#0a111d" if cle == "normal" else INK,
                          activebackground="#2b3d5c", relief="flat", padx=18, pady=12, command=lambda c=cle: choisir(c))
            b.pack(fill="x", padx=24, pady=6)
        tk.Label(choix, text="Conseil : « Normal » une fois par semaine suffit. « Expert » de temps en temps, par exemple la nuit.",
                 font=police, fg=MUTED, bg=BG, wraplength=840, justify="left").pack(anchor="w", padx=24, pady=(14, 0))
    racine.after(120, relever)
    racine.mainloop()


def console(args):
    """Version sans fenêtre (Ctrl+C = arrêter la recherche et passer à l'examen final)."""
    dernier = [0.0]

    def emettre(type_, **kw):
        if type_ == "log":
            print("   " + kw["texte"], flush=True)
        elif type_ == "progres" and kw["pct"] - dernier[0] >= 0.05:
            dernier[0] = kw["pct"]
            print(f"   ── progression : {kw['pct'] * 100:.0f} %", flush=True)
        elif type_ == "erreur":
            print("❌ " + kw["texte"], flush=True)
    if not args.duree:
        print("Durée : 1 = Rapide (≈ 20 min) · 2 = Normal (≈ 50 min) · 3 = Expert (≈ 2 h 30)")
        r = input("Ton choix [2] : ").strip()
        args.duree = {"1": "rapide", "3": "expert"}.get(r, "normal")
    moteur = Moteur(args, emettre)
    t = threading.Thread(target=moteur.lancer, daemon=True)
    t.start()
    try:
        while t.is_alive():
            t.join(0.5)
    except KeyboardInterrupt:
        print("\n⏹ Arrêt demandé : examen final avec ce qui a été appris…", flush=True)
        moteur.arret.set()
        t.join()
    res = moteur.resultat
    if not res:
        return 2
    print(f"\n{res['decision']['raison']}{appris_cette_fois(res['entree'])}\n📄 Rapport : {res['rapport']}")
    if moteur.depot_git and not args.demo and input("Mettre à jour le site maintenant ? (o/n) ").strip().lower().startswith("o"):
        enregistrer(res, args.demo)
        depuis = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if publier(res, print):
            surveiller_site(depuis, print, lambda t: print("   " + t, flush=True))
    else:
        enregistrer(res, args.demo)
    return 0


_VERROU = None


def prendre_verrou() -> bool:
    """Empêche deux entraînements en même temps (ils écriraient dans les mêmes fichiers).
    Le verrou est tenu par le système : il disparaît tout seul si la fenêtre est fermée ou plante."""
    global _VERROU
    os.makedirs(".cache_entrainement", exist_ok=True)
    try:
        f = open(os.path.join(".cache_entrainement", "en_cours.lock"), "a+")
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    _VERROU = f
    return True


def main():
    if not prendre_verrou():
        msg = ("Un entraînement est déjà en cours sur ce PC.\n"
               "Attends qu'il se termine (ou ferme sa fenêtre) avant d'en lancer un autre : "
               "deux entraînements en même temps se gêneraient et n'iraient pas plus vite.")
        print(msg)
        try:
            import tkinter
            from tkinter import messagebox
            r = tkinter.Tk()
            r.withdraw()
            messagebox.showinfo("Radar Bourse", msg)
            r.destroy()
        except Exception:
            pass
        return 4
    p = argparse.ArgumentParser(description="Entraînement approfondi de l'IA de Radar Bourse")
    p.add_argument("--duree", choices=list(DUREES), default=None, help="rapide, normal ou expert (sinon la fenêtre demande)")
    p.add_argument("--complet", action="store_true", help="(ancien nom de --duree expert)")
    p.add_argument("--minutes", type=int, default=None, help="durée maximale de la recherche")
    p.add_argument("--console", action="store_true", help="sans fenêtre")
    p.add_argument("--demo", action="store_true", help="données fictives (pour tester)")
    args = p.parse_args()
    if args.complet and not args.duree:
        args.duree = "expert"
    verifier_dependances()
    if not args.console:
        try:
            import tkinter
            tkinter.Tk().destroy()   # vérifie qu'une fenêtre peut s'ouvrir
        except Exception:
            print("(Fenêtre indisponible : passage en mode texte.)")
            return console(args)
        fenetre(args)
        return 0
    return console(args)


if __name__ == "__main__":
    sys.exit(main())
