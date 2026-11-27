"""Contrôle qualité des données : on ne publie pas de prévision sur des données douteuses.

Pour chaque titre :
- fraîcheur : la dernière cotation est-elle récente ?
- trous : manque-t-il beaucoup de séances ?
- sauts anormaux : variation quotidienne invraisemblable (souvent une erreur de données) ;
- vérification croisée (cryptos) : le dernier cours Yahoo est comparé à celui de Binance.

Un titre « à vérifier » reste affiché, mais il est exclu des signaux forts et des configurations
de décollage, et sa fiche le signale clairement.
"""
from __future__ import annotations

import json
import urllib.request

import numpy as np
import pandas as pd

from . import config, data

SAUT_MAX = {"crypto": 0.60, "autre": 0.35}   # variation quotidienne au-delà de laquelle on se méfie
ECART_CROISE_MAX = 0.05                      # 5 % d'écart entre deux sources = suspect


def _prix_binance() -> dict[str, float]:
    if data.DEMO:
        return {}
    try:
        req = urllib.request.Request("https://data-api.binance.vision/api/v3/ticker/price",
                                     headers={"User-Agent": "radar-bourse"})
        with urllib.request.urlopen(req, timeout=15) as r:
            prix = {x["symbol"]: float(x["price"]) for x in json.load(r)}
        # version 114 : seulement les paires qui s'échangent vraiment. Une paire suspendue (XMR, EOS…) garde un vieux prix figé,
        # ce qui donnait de fausses alertes (« écart de 1103 % entre Yahoo et Binance »).
        try:
            req = urllib.request.Request("https://data-api.binance.vision/api/v3/exchangeInfo?permissions=SPOT",
                                         headers={"User-Agent": "radar-bourse"})
            with urllib.request.urlopen(req, timeout=20) as r:
                actives = {x["symbol"] for x in json.load(r).get("symbols", []) if x.get("status") == "TRADING"}
            if actives:
                prix = {k: v for k, v in prix.items() if k in actives}
        except Exception:
            pass
        return prix
    except Exception:
        return {}


def controler(donnees: dict[str, pd.DataFrame]) -> dict:
    """Renvoie {ticker: {"ok": bool, "problemes": [...], "source": str}} et un résumé."""
    binance = _prix_binance()
    aujourd_hui = pd.Timestamp.today().normalize()
    details, resume = {}, {"ok": 0, "a_verifier": 0, "croisees": 0, "croisees_ok": 0}
    for t, d in donnees.items():
        crypto = t.endswith("-USD")
        problemes = []
        derniere = d.index[-1]
        retard = (aujourd_hui - derniere).days if crypto else np.busday_count(derniere.date(), aujourd_hui.date())
        if retard > (3 if crypto else 4):
            problemes.append(f"dernière cotation il y a {retard} jours")
        an = d.iloc[-260:]
        if not crypto:
            attendu = np.busday_count(an.index[0].date(), an.index[-1].date())
            if attendu and len(an) < 0.85 * attendu:
                problemes.append(f"{attendu - len(an)} séances manquantes sur un an")
        # version 114 : une vraie envolée (petite crypto, rachat d'entreprise…) n'est pas une erreur. La signature d'une erreur de
        # données, c'est l'aller-retour : un saut énorme effacé dès le lendemain. On ne signale que ça (ou des sauts en rafale).
        r = an["Close"].pct_change()
        seuil = SAUT_MAX["crypto" if crypto else "autre"]
        gros = r.abs() > seuil
        retour = (gros & ((1 + r) * (1 + r.shift(-1)) - 1).abs().lt(seuil / 3)).sum()
        n_retours, n_gros = int(retour), int(gros.sum())
        if n_retours:
            problemes.append(f"{n_retours} aller(s)-retour(s) anormal(aux) du cours sur un an (probable erreur de données)")
        elif n_gros >= 4:
            problemes.append(f"{n_gros} variations quotidiennes anormales sur un an")
        if an["Close"].iloc[-5:].nunique() == 1 and float(an["Close"].iloc[-1]) > 1e-5:   # les cours minuscules (BTTC) bougent par paliers
            problemes.append("cours figé depuis 5 séances")
        if crypto and binance:
            sym = config.symbole_binance(t)
            if sym in binance:
                resume["croisees"] += 1
                ecart = abs(binance[sym] / float(d["Close"].iloc[-1]) - 1)
                if ecart > ECART_CROISE_MAX:
                    problemes.append(f"écart de {ecart * 100:.0f} % entre Yahoo et Binance")
                else:
                    resume["croisees_ok"] += 1
        ok = not problemes
        resume["ok" if ok else "a_verifier"] += 1
        details[t] = {"ok": ok, "problemes": problemes, "source": data.SOURCES_UTILISEES.get(t, "cache")}
    sources = {}
    for v in details.values():
        sources[v["source"]] = sources.get(v["source"], 0) + 1
    resume["sources"] = sources
    return {"details": details, "resume": resume}


def appliquer(analyses, controle: dict) -> None:
    """Exclut des signaux les titres aux données douteuses et le signale dans la fiche."""
    for a in analyses:
        q = controle["details"].get(a.ticker)
        if not q or q["ok"]:
            continue
        a.signal_fort = False
        a.potentiel_hausse = False
        a.alertes.insert(0, "⚠️ Données à vérifier (" + ", ".join(q["problemes"]) +
                         ") : ce titre est exclu des signaux forts et des configurations de décollage.")
