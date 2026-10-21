"""Indicateurs techniques, calculés sans librairie externe pour qu'on puisse lire chaque formule."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """RSI de Wilder : >70 = suracheté, <30 = survendu."""
    delta = close.diff()
    hausse = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    baisse = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = hausse / baisse.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100)


def macd(close: pd.Series, rapide=12, lent=26, signal=9):
    ligne = ema(close, rapide) - ema(close, lent)
    sig = ema(ligne, signal)
    return ligne, sig, ligne - sig


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Average True Range : amplitude moyenne d'une séance (mesure de volatilité)."""
    prev = df["Close"].shift()
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - prev).abs(),
                    (df["Low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Force de la tendance (peu importe le sens) : >25 = tendance nette."""
    up = df["High"].diff()
    down = -df["Low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    a = atr(df, n)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def calculer(df: pd.DataFrame, benchmark: pd.DataFrame | None = None) -> pd.DataFrame:
    """Ajoute toutes les colonnes d'indicateurs au DataFrame de cours."""
    d = df.copy()
    c = d["Close"]

    # Tendance
    d["sma20"] = c.rolling(20).mean()
    d["sma50"] = c.rolling(50).mean()
    d["sma200"] = c.rolling(200).mean()
    d["dist_sma50"] = c / d["sma50"] - 1
    d["dist_sma200"] = c / d["sma200"] - 1
    d["pente_sma50"] = d["sma50"].pct_change(10)
    d["adx"] = adx(d)

    # Momentum
    d["rsi"] = rsi(c)
    d["macd"], d["macd_signal"], d["macd_hist"] = macd(c)
    d["macd_hist_norm"] = d["macd_hist"] / c
    for n in (1, 5, 21, 63, 126):
        d[f"ret_{n}j"] = c.pct_change(n)

    # Volatilité / risque
    rend = c.pct_change()
    d["vol_20j"] = rend.rolling(20).std() * np.sqrt(252)
    d["atr_pct"] = atr(d) / c
    bb_moy = c.rolling(20).mean()
    bb_std = c.rolling(20).std()
    d["bb_haut"], d["bb_bas"] = bb_moy + 2 * bb_std, bb_moy - 2 * bb_std
    d["bb_position"] = (c - d["bb_bas"]) / (d["bb_haut"] - d["bb_bas"])
    d["bb_largeur"] = (d["bb_haut"] - d["bb_bas"]) / bb_moy
    # "Squeeze" : bandes de Bollinger les plus serrées depuis 6 mois → mouvement fort souvent imminent
    d["squeeze"] = d["bb_largeur"] <= d["bb_largeur"].rolling(126).quantile(0.1)
    d["drawdown"] = c / c.cummax() - 1

    # Plus hauts / volume
    d["plus_haut_52s"] = c.rolling(252).max()
    d["dist_plus_haut"] = c / d["plus_haut_52s"] - 1
    # Les indices (ex : CAC 40) n'ont pas de volume : on évite les divisions par zéro
    vol_moy = d["Volume"].rolling(20).mean().replace(0, np.nan)
    d["volume_ratio"] = d["Volume"] / vol_moy
    obv = (np.sign(c.diff()).fillna(0) * d["Volume"]).cumsum()
    d["obv_pente"] = obv.diff(20) / vol_moy / 20
    d["var_jour"] = c.pct_change()

    # Force relative face au marché (le titre fait-il mieux que son indice ?)
    # + « régime » du marché : l'indice est-il en tendance haussière ? est-il agité ?
    if benchmark is not None and not benchmark.empty:
        b = benchmark["Close"].reindex(d.index).ffill()
        d["force_relative_63j"] = c.pct_change(63) - b.pct_change(63)
        d["marche_tendance"] = b / b.rolling(200, min_periods=150).mean() - 1
        d["marche_vol"] = b.pct_change().rolling(20).std() * np.sqrt(252)
    else:
        d["force_relative_63j"] = np.nan
        d["marche_tendance"] = np.nan
        d["marche_vol"] = np.nan

    return d.replace([np.inf, -np.inf], np.nan)


# Colonnes utilisées comme variables explicatives par le modèle de machine learning
FEATURES = [
    "dist_sma50", "dist_sma200", "pente_sma50", "adx", "rsi", "macd_hist_norm",
    "ret_5j", "ret_21j", "ret_63j", "ret_126j", "vol_20j", "atr_pct", "bb_position",
    "bb_largeur", "drawdown", "dist_plus_haut", "volume_ratio", "obv_pente",
    "force_relative_63j", "marche_tendance", "marche_vol",
]
