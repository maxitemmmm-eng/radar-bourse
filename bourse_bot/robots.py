"""Les mini-robots : des stratégies classiques de Bourse et de crypto, chacune avec une règle simple et fixe.

Chaque robot dit chaque jour, pour chaque titre : « acheter » (+1), « vendre » (-1) ou rien (0).
- Le site montre leurs signaux du jour ET leur vrai palmarès sur tout l'historique : quand un robot a dit
  « acheter », le prix était-il plus haut un mois après ? (comparé à « toujours acheter », pour être honnête).
- L'IA reçoit leur avis moyen (le « consensus des robots ») comme un indicateur de plus. Elle ne s'en sert que
  si les tests sur des années jamais vues prouvent qu'il l'aide.

Les règles sont fixes (on ne les ajuste pas sur le passé) : c'est ce qui rend leur palmarès honnête.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .connaissances import HALVINGS_BITCOIN


def _croise(s: pd.Series, jours: int = 3) -> pd.Series:
    """Vrai si la série est passée au-dessus de 0 dans les `jours` derniers jours."""
    dessus = s > 0
    passage = dessus & ~dessus.shift(1, fill_value=False)
    return passage.rolling(jours, min_periods=1).max().astype(bool)


def _tendance(d):
    c = d["Close"]
    haut = (c > d["sma200"]) & (d["sma50"] > d["sma200"])
    bas = (c < d["sma200"]) & (d["sma50"] < d["sma200"])
    return haut.astype(int) - bas.astype(int)


def _rebond(d):
    return (d["rsi"] < 30).astype(int) - (d["rsi"] > 70).astype(int)


def _momentum(d):
    return (d["ret_126j"] > 0.15).astype(int) - (d["ret_126j"] < -0.15).astype(int)


def _cassure(d):
    c = d["Close"]
    haut, bas = c.rolling(55).max().shift(1), c.rolling(55).min().shift(1)
    return (c > haut).astype(int) - (c < bas).astype(int)


def _macd(d):
    h = d["macd_hist"]
    return _croise(h).astype(int) - _croise(-h).astype(int)


def _bollinger(d):
    return (d["bb_position"] < 0).astype(int) - (d["bb_position"] > 1).astype(int)


def _calme(d):
    v = d["vol_20j"]
    calme = (v < v.rolling(252, min_periods=120).median()) & (d["Close"] > d["sma200"])
    return calme.astype(int)


def _halving(d):
    idx = pd.DatetimeIndex(d.index).tz_localize(None) if getattr(d.index, "tz", None) else pd.DatetimeIndex(d.index)
    pos = np.searchsorted(HALVINGS_BITCOIN.values, idx.values, side="right") - 1
    dernier = HALVINGS_BITCOIN.values[np.clip(pos, 0, None)]
    jours = (idx.values - dernier) / np.timedelta64(1, "D")
    jours = np.where(pos < 0, np.nan, jours)
    return pd.Series(np.where((jours >= 120) & (jours <= 540), 1, np.where((jours > 540) & (jours <= 900), -1, 0)),
                     index=d.index)


def _peur(d):
    f = d["fng"]
    return (f < 25).astype(int) - (f > 75).astype(int)


# (clé, nom, pour qui, idée en mots simples, règle)
ROBOTS = [
    ("tendance", "Le suiveur de tendance", "tous",
     "Il achète quand le prix est au-dessus de sa moyenne des 200 derniers jours et que la tendance récente va dans le même sens. "
     "Il vend dans le cas inverse. Beaucoup de fonds professionnels utilisent ce type de règle.", _tendance),
    ("rebond", "Le chasseur de rebonds", "tous",
     "Il achète quand le titre a beaucoup baissé en peu de temps (RSI sous 30) et vend quand il a trop monté (RSI au-dessus de 70). "
     "Il parie que les excès se corrigent.", _rebond),
    ("momentum", "Le coureur de fond", "tous",
     "Il achète les titres qui ont pris plus de 15 % en 6 mois et vend ceux qui en ont perdu plus de 15 %. "
     "L'effet « momentum » est l'un des plus étudiés en finance.", _momentum),
    ("cassure", "Le casseur de records", "tous",
     "Il achète quand le prix dépasse son plus haut des 55 derniers jours, et vend quand il passe sous son plus bas. "
     "C'est la règle des célèbres « Turtle traders » des années 1980.", _cassure),
    ("macd", "Le guetteur de MACD", "tous",
     "Il achète quand l'élan du prix (MACD) repasse au-dessus de zéro, et vend quand il repasse en dessous.", _macd),
    ("bollinger", "L'élastique de Bollinger", "tous",
     "Il achète quand le prix sort par le bas des bandes de Bollinger et vend quand il sort par le haut, "
     "comme un élastique trop tendu qui revient.", _bollinger),
    ("calme", "Le prudent", "tous",
     "Il n'achète que les titres en tendance haussière ET plus calmes que d'habitude. Il ne vend jamais : il reste simplement à l'écart.", _calme),
    ("halving", "L'horloge du halving", "crypto",
     "Il suit le cycle de 4 ans du Bitcoin : il achète de 4 à 18 mois après un « halving », puis devient vendeur. "
     "Attention : ce cycle ne s'est produit que 4 fois, c'est très peu pour être sûr.", _halving),
    ("peur", "Le contrarien de la peur", "crypto",
     "Il achète quand l'indice de peur des cryptos est très bas (panique) et vend quand il est très haut (euphorie). "
     "« Sois avide quand les autres ont peur », disait Warren Buffett.", _peur),
]
COLONNES = [f"robot_{r[0]}" for r in ROBOTS]


def signaux(d: pd.DataFrame, crypto: bool) -> pd.DataFrame:
    out = {}
    for cle, _, pour, _, regle in ROBOTS:
        if pour == "crypto" and not crypto:
            out[f"robot_{cle}"] = pd.Series(0, index=d.index)
            continue
        try:
            out[f"robot_{cle}"] = regle(d).reindex(d.index).fillna(0).astype(int)
        except Exception:
            out[f"robot_{cle}"] = pd.Series(0, index=d.index)
    return pd.DataFrame(out, index=d.index)


def ajouter(d: pd.DataFrame, crypto: bool) -> pd.DataFrame:
    """Ajoute le consensus des robots (moyenne de leurs votes, de -1 à +1) aux indicateurs."""
    s = signaux(d, crypto)
    actifs = [c for c, r in zip(COLONNES, ROBOTS) if r[2] == "tous" or crypto]
    d["robots_consensus"] = s[actifs].mean(axis=1)
    return d


def bilan(donnees: dict, marches: dict, horizon: int) -> dict:
    """Palmarès de chaque robot sur tout l'historique + ses signaux du jour."""
    stats = {r[0]: {"achat": [0, 0], "vente": [0, 0], "base": [0, 0]} for r in ROBOTS}
    du_jour = {r[0]: {"achat": [], "vente": []} for r in ROBOTS}
    votes = {}
    for t, d in donnees.items():
        crypto = marches.get(t) == "crypto" or t.endswith("-USD")
        if "Close" not in d or len(d) < 300:
            continue
        s = signaux(d, crypto)
        futur = d["Close"].shift(-horizon) / d["Close"] - 1
        ok = futur.notna()
        votes[t] = {}
        for cle, _, pour, _, _ in ROBOTS:
            if pour == "crypto" and not crypto:
                continue
            sig = s[f"robot_{cle}"]
            st = stats[cle]
            a, v = (sig == 1) & ok, (sig == -1) & ok
            st["achat"][0] += int((futur[a] > 0).sum()); st["achat"][1] += int(a.sum())
            st["vente"][0] += int((futur[v] < 0).sum()); st["vente"][1] += int(v.sum())
            st["base"][0] += int((futur[ok] > 0).sum()); st["base"][1] += int(ok.sum())
            aujourdhui = int(sig.iloc[-1])
            votes[t][cle] = aujourdhui
            if aujourdhui == 1:
                du_jour[cle]["achat"].append(t)
            elif aujourdhui == -1:
                du_jour[cle]["vente"].append(t)
    out = []
    for cle, nom, pour, idee, _ in ROBOTS:
        st = stats[cle]
        taux = lambda x: (x[0] / x[1]) if x[1] else None
        out.append({"cle": cle, "nom": nom, "pour": pour, "idee": idee,
                    "achat": {"justes": st["achat"][0], "nb": st["achat"][1], "taux": taux(st["achat"])},
                    "vente": {"justes": st["vente"][0], "nb": st["vente"][1], "taux": taux(st["vente"])},
                    "base_hausse": taux(st["base"]),
                    "du_jour": du_jour[cle]})
    return {"robots": out, "votes": votes, "horizon": horizon}
