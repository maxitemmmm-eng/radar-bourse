"""Backtest : « si j'avais suivi les signaux du bot ces dernières années, combien aurais-je ? »

Règles anti-triche :
- le signal calculé à la clôture du jour J n'est exécuté qu'au jour J+1 ;
- des frais sont payés à chaque achat et à chaque vente ;
- on compare toujours à la stratégie la plus simple : acheter et garder (buy & hold).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config


@dataclass
class ResultatBacktest:
    ticker: str
    capital_depart: float
    courbe_strategie: pd.Series
    courbe_buy_hold: pd.Series
    stats_strategie: dict
    stats_buy_hold: dict
    trades: pd.DataFrame


def signal_historique(d: pd.DataFrame) -> pd.Series:
    """Version vectorisée des règles principales du score : 1 = investi, 0 = en liquide."""
    entree = (d["Close"] > d["sma200"]) & (d["sma50"] > d["sma200"]) & \
             (d["macd_hist"] > 0) & (d["rsi"] < 75)
    sortie = (d["Close"] < d["sma50"]) | ((d["macd_hist"] < 0) & (d["rsi"] < 50))

    position = np.zeros(len(d))
    en_position = False
    stop = -np.inf
    atr_abs = (d["atr_pct"] * d["Close"]).to_numpy()
    close = d["Close"].to_numpy()
    for i in range(len(d)):
        if np.isnan(d["sma200"].iat[i]):
            continue
        if not en_position and entree.iat[i]:
            en_position, stop = True, close[i] - 2 * atr_abs[i]
        elif en_position:
            stop = max(stop, close[i] - 3 * atr_abs[i])  # stop suiveur
            if sortie.iat[i] or close[i] < stop:
                en_position = False
        position[i] = 1.0 if en_position else 0.0
    return pd.Series(position, index=d.index)


def _stats(courbe: pd.Series, jours_par_an: int) -> dict:
    rend = courbe.pct_change().dropna()
    annees = len(rend) / jours_par_an
    total = courbe.iloc[-1] / courbe.iloc[0] - 1
    cagr = (1 + total) ** (1 / annees) - 1 if annees > 0 else np.nan
    vol = rend.std() * np.sqrt(jours_par_an)
    sharpe = (rend.mean() * jours_par_an) / vol if vol > 0 else np.nan
    dd = (courbe / courbe.cummax() - 1).min()
    return {"rendement total": total, "rendement annuel": cagr, "volatilité": vol,
            "ratio de Sharpe": sharpe, "pire baisse (drawdown)": dd}


def lancer(ticker: str, d: pd.DataFrame, capital: float = 1000.0,
           annees: float = 3.0) -> ResultatBacktest:
    jours_par_an = 365 if ticker.endswith("-USD") else 252
    d = d.dropna(subset=["sma200"]).iloc[-int(annees * jours_par_an):]

    position = signal_historique(d).shift(1).fillna(0)  # exécution le lendemain
    rend_marche = d["Close"].pct_change().fillna(0)
    changements = position.diff().abs().fillna(position.iloc[0])
    rend_strat = position * rend_marche - changements * config.FRAIS_PAR_ORDRE

    courbe_s = capital * (1 + rend_strat).cumprod()
    courbe_bh = capital * (1 + rend_marche).cumprod() * (1 - config.FRAIS_PAR_ORDRE)

    # Liste des trades
    trades, debut = [], None
    for date, pos, prev in zip(position.index, position, position.shift(1).fillna(0)):
        if pos == 1 and prev == 0:
            debut = date
        elif pos == 0 and prev == 1 and debut is not None:
            trades.append((debut, date, d["Close"].shift(1)[date] / d["Close"].shift(1)[debut] - 1))
            debut = None
    if debut is not None:
        trades.append((debut, d.index[-1], d["Close"].iloc[-1] / d["Close"].shift(1)[debut] - 1))
    trades = pd.DataFrame(trades, columns=["entrée", "sortie", "résultat"])

    stats_s = _stats(courbe_s, jours_par_an)
    stats_s["nombre de trades"] = len(trades)
    stats_s["trades gagnants"] = float((trades["résultat"] > 0).mean()) if len(trades) else np.nan
    stats_s["temps investi"] = float(position.mean())
    return ResultatBacktest(ticker, capital, courbe_s, courbe_bh, stats_s,
                            _stats(courbe_bh, jours_par_an), trades)
