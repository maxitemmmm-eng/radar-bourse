"""Score technique transparent (0-100) + détection des titres susceptibles de monter.

Chaque point attribué est accompagné d'une raison lisible : pas de boîte noire.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Analyse:
    ticker: str
    nom: str
    marche: str
    prix: float
    score: float                 # 0-100, 50 = neutre
    signal: str                  # ACHAT FORT / ACHAT / NEUTRE / VENTE / VENTE FORTE
    risque: str                  # Faible / Moyen / Élevé / Très élevé
    potentiel_hausse: bool       # configuration de "décollage" détectée
    raisons_pour: list[str] = field(default_factory=list)
    raisons_contre: list[str] = field(default_factory=list)
    alertes: list[str] = field(default_factory=list)
    stop_loss: float = float("nan")
    objectif: float = float("nan")
    proba_hausse: float = float("nan")      # rempli par le modèle ML
    fiabilite_modele: float = float("nan")  # précision mesurée hors échantillon
    perf: dict = field(default_factory=dict)
    date_cours: str = ""
    devise: str = "$"
    rendement_attendu: float = float("nan")   # médiane historique pour cette probabilité
    fourchette: tuple = ()                    # (bas, haut) probables à l'horizon
    signal_fort: bool = False                 # modèle confiant ET tendance technique haussière
    actus: list = field(default_factory=list) # derniers titres d'actualité
    tonalite: float = float("nan")            # tonalité moyenne des actus (-1 à +1)
    fondamentaux: dict | None = None          # PER, marges, dette… (actions seulement)
    quantiles: tuple = ()                     # (bas, central, haut) du log-rendement à l'horizon, par l'IA
    resultats_le: str = ""                     # date de la prochaine publication de résultats
    proba_marche: float = float("nan")         # probabilité de faire mieux que son indice de référence
    indice_ref: str = ""                       # indice de comparaison (CAC 40, S&P 500, Bitcoin…)
    fourchette_elargie: bool = False           # fourchette élargie avant une publication de résultats
    extremes: tuple = ()                       # (bas 5 %, haut 95 %) : scénarios extrêmes (mode risque)
    proba_ia1: float = float("nan")            # avis de l'IA n°1
    proba_ia2: float = float("nan")            # avis de l'IA n°2
    accord_ia: bool | None = None              # les deux IA vont-elles dans le même sens ?
    actu_contredit: bool = False               # les actus récentes contredisent l'avis de l'IA
    proba_brute: float = float("nan")          # probabilité avant la correction apprise des vraies erreurs
    risque_prevu: dict | None = None           # agitation prévue le mois prochain (vol, mouvement typique, vs habitude)
    raisons_ia: list = field(default_factory=list)  # ce qui a le plus pesé dans l'avis des IA
    confiance: str = ""                         # faible / moyenne / forte (échelle unique, mesurée)
    avis_net: bool | None = None               # l'avis est-il assez tranché pour avoir été fiable ? (None = inconnu)

    def to_dict(self) -> dict:
        return propre(self.__dict__.copy())


def propre(v):
    """Rend un objet sérialisable en JSON valide (NaN/inf → null, numpy → Python)."""
    if isinstance(v, dict):
        return {str(k): propre(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [propre(x) for x in v]
    if isinstance(v, (np.floating, float)):
        return None if not np.isfinite(v) else float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def _sous_score(points: float, maxi: float) -> float:
    return float(np.clip(points / maxi, -1, 1))


def analyser(ticker: str, nom: str, marche: str, d: pd.DataFrame) -> Analyse:
    x = d.iloc[-1]
    pour, contre, alertes = [], [], []

    # ---------------- 1. Tendance (poids 35 %) ----------------
    t = 0.0
    if x.Close > x.sma200:
        t += 2; pour.append("Cours au-dessus de la moyenne 200 jours (tendance de fond haussière)")
    else:
        t -= 2; contre.append("Cours sous la moyenne 200 jours (tendance de fond baissière)")
    if x.sma50 > x.sma200:
        t += 1; pour.append("Moyenne 50j > moyenne 200j (configuration haussière)")
    else:
        t -= 1; contre.append("Moyenne 50j < moyenne 200j")
    if x.pente_sma50 > 0.01:
        t += 1
    elif x.pente_sma50 < -0.01:
        t -= 1
    croisement = (d["sma50"] > d["sma200"]).astype(int).diff().iloc[-10:]
    if (croisement == 1).any():
        t += 1; alertes.append("Golden cross récent (la moyenne 50j vient de passer au-dessus de la 200j)")
    if (croisement == -1).any():
        t -= 1; alertes.append("Death cross récent (la moyenne 50j vient de passer sous la 200j)")
    if x.adx > 25:
        t *= 1.2  # une tendance nette renforce le signal, dans un sens comme dans l'autre
    s_tendance = _sous_score(t, 5)

    # ---------------- 2. Momentum (poids 30 %) ----------------
    m = 0.0
    if 50 <= x.rsi <= 70:
        m += 1; pour.append(f"RSI à {x.rsi:.0f} : élan acheteur sans excès")
    elif x.rsi > 75:
        m -= 1; contre.append(f"RSI à {x.rsi:.0f} : suracheté, risque de repli")
    elif x.rsi < 30:
        m += 0.5; alertes.append(f"RSI à {x.rsi:.0f} : survendu, rebond technique possible")
    elif x.rsi < 45:
        m -= 1; contre.append(f"RSI à {x.rsi:.0f} : élan vendeur")
    if x.macd_hist > 0:
        m += 1
    else:
        m -= 1
    if d["macd_hist"].iloc[-2] <= 0 < x.macd_hist:
        alertes.append("Le MACD vient de passer haussier")
    if x.ret_63j > 0.10:
        m += 1; pour.append(f"+{x.ret_63j*100:.0f} % sur 3 mois")
    elif x.ret_63j < -0.10:
        m -= 1; contre.append(f"{x.ret_63j*100:.0f} % sur 3 mois")
    if x.force_relative_63j > 0.05:
        m += 1; pour.append("Fait mieux que son marché sur 3 mois (force relative)")
    elif x.force_relative_63j < -0.05:
        m -= 1; contre.append("Fait moins bien que son marché sur 3 mois")
    # Confirmations par d'autres indicateurs (poids volontairement modéré)
    g = lambda nom: x.get(nom, np.nan)
    if g("ichimoku") == 1:
        m += 0.5; pour.append("Cours au-dessus du nuage Ichimoku")
    elif g("ichimoku") == -1:
        m -= 0.5; contre.append("Cours sous le nuage Ichimoku")
    if g("supertrend") == 1:
        m += 0.5; pour.append("Supertrend orienté à la hausse")
    elif g("supertrend") == -1:
        m -= 0.5; contre.append("Supertrend orienté à la baisse")
    if g("stoch_k") > 80 and x.rsi > 70:
        m -= 0.5; contre.append("Surchauffe confirmée par le stochastique")
    elif g("stoch_k") < 20 and x.rsi < 35:
        alertes.append("Stochastique en zone de survente : rebond possible")
    if g("div_rsi") == -1:
        m -= 0.5; alertes.append("Divergence baissière : le prix monte mais le RSI s'essouffle")
    elif g("div_rsi") == 1:
        m += 0.5; alertes.append("Divergence haussière : le prix baisse mais le RSI se redresse")
    s_momentum = _sous_score(m, 6)

    # ---------------- 3. Volume / flux (poids 15 %) ----------------
    v = 0.0
    if x.obv_pente > 0.1:
        v += 1; pour.append("Volumes plutôt acheteurs (OBV en hausse)")
    elif x.obv_pente < -0.1:
        v -= 1; contre.append("Volumes plutôt vendeurs (OBV en baisse)")
    if x.volume_ratio > 1.8:
        alertes.append(f"Volume inhabituel : x{x.volume_ratio:.1f} la moyenne")
        v += 1 if x.ret_5j > 0 else -1
    if g("cmf") > 0.1:
        v += 0.5; pour.append("Pression acheteuse sur 20 séances (Chaikin Money Flow)")
    elif g("cmf") < -0.1:
        v -= 0.5; contre.append("Pression vendeuse sur 20 séances (Chaikin Money Flow)")
    if g("mfi") > 80:
        contre.append(f"Money Flow Index à {g('mfi'):.0f} : beaucoup d'argent est déjà entré")
    if x.ret_5j > 0.02 and x.volume_ratio < 0.8:
        v -= 0.5; contre.append("Hausse récente avec des volumes faibles : mouvement fragile")
    elif x.ret_5j > 0.02 and x.volume_ratio > 1.3:
        v += 0.5; pour.append("Hausse récente confirmée par des volumes élevés")
    s_volume = _sous_score(v, 3)

    # Figures de chandeliers japonais des 3 dernières séances
    from .indicators import NOMS_CHANDELIERS
    for date, fig in d["chandelier"].iloc[-3:].items():
        if fig and fig in NOMS_CHANDELIERS:
            nom_f, sens = NOMS_CHANDELIERS[fig]
            alertes.append(f"Chandelier « {nom_f} » le {date:%d/%m} : {sens}")
    # Proximité d'une résistance (plus haut annuel)
    if -0.02 < x.dist_plus_haut < 0:
        alertes.append("Tout proche de son plus haut sur un an : cassure (hausse) ou rejet (repli) à surveiller")
    # Contexte économique
    if g("vix") > 30:
        alertes.append(f"Marchés très nerveux (VIX à {g('vix'):.0f}) : les mouvements peuvent être violents")
    if g("fng") < 20:
        alertes.append(f"Crypto : « peur extrême » (Fear & Greed à {g('fng'):.0f})")
    elif g("fng") > 80:
        alertes.append(f"Crypto : « avidité extrême » (Fear & Greed à {g('fng'):.0f}), prudence")

    # ---------------- 4. Risque (poids 20 %, pénalité) ----------------
    r = 0.0
    if x.vol_20j > 0.80:
        r -= 2; niveau = "Très élevé"
    elif x.vol_20j > 0.45:
        r -= 1; niveau = "Élevé"
    elif x.vol_20j > 0.25:
        niveau = "Moyen"
    else:
        r += 1; niveau = "Faible"
    if x.drawdown < -0.35:
        r -= 1; contre.append(f"À {x.drawdown*100:.0f} % de son plus haut historique récent")
    s_risque = _sous_score(r, 2)

    brut = 0.35 * s_tendance + 0.30 * s_momentum + 0.15 * s_volume + 0.20 * s_risque
    score = round(50 + 50 * brut, 1)

    if score >= 75: signal = "ACHAT FORT"
    elif score >= 60: signal = "ACHAT"
    elif score > 40: signal = "NEUTRE"
    elif score > 25: signal = "VENTE"
    else: signal = "VENTE FORTE"

    # ---------------- Détection "susceptible de monter" ----------------
    criteres = {
        "proche du plus haut 52 semaines (cassure possible)": x.dist_plus_haut > -0.05,
        "volatilité comprimée (squeeze de Bollinger)": bool(d["squeeze"].iloc[-10:].any()),
        "volume en hausse": x.volume_ratio > 1.3,
        "tendance de fond haussière": x.Close > x.sma200,
        "élan sain (RSI 50-70)": 50 <= x.rsi <= 70,
        "MACD haussier": x.macd_hist > 0,
    }
    remplis = [k for k, ok in criteres.items() if ok]
    potentiel = len(remplis) >= 4 and criteres["tendance de fond haussière"]
    if potentiel:
        alertes.insert(0, "🚀 Configuration de hausse potentielle : " + ", ".join(remplis))

    # Stop-loss (2 ATR sous le cours) et objectif (rapport gain/risque 2:1)
    a = x.atr_pct * x.Close
    stop, objectif = x.Close - 2 * a, x.Close + 4 * a

    perf = {k: float(x[f"ret_{n}j"]) for k, n in
            (("1 jour", 1), ("1 semaine", 5), ("1 mois", 21), ("3 mois", 63), ("6 mois", 126))}
    perf["volatilité annuelle"] = float(x.vol_20j)

    from .data import devise
    return Analyse(ticker, nom, marche, float(x.Close), score, signal, niveau, bool(potentiel),
                   pour, contre, alertes, float(stop), float(objectif), perf=perf,
                   date_cours=f"{d.index[-1]:%Y-%m-%d}", devise=devise(ticker))
