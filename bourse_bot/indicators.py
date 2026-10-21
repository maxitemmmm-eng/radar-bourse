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


def stochastique(d: pd.DataFrame, n: int = 14, lissage: int = 3) -> pd.Series:
    """%K lissé : position du cours entre le plus bas et le plus haut des n séances (0-100)."""
    bas, haut = d["Low"].rolling(n).min(), d["High"].rolling(n).max()
    k = 100 * (d["Close"] - bas) / (haut - bas).replace(0, np.nan)
    return k.rolling(lissage).mean()


def mfi(d: pd.DataFrame, n: int = 14) -> pd.Series:
    """Money Flow Index : un RSI qui tient compte des volumes (>80 surachat, <20 survente)."""
    tp = (d["High"] + d["Low"] + d["Close"]) / 3
    flux = tp * d["Volume"]
    pos = flux.where(tp > tp.shift(), 0.0).rolling(n).sum()
    neg = flux.where(tp < tp.shift(), 0.0).rolling(n).sum()
    return 100 - 100 / (1 + pos / neg.replace(0, np.nan))


def cmf(d: pd.DataFrame, n: int = 20) -> pd.Series:
    """Chaikin Money Flow : pression acheteuse (>0) ou vendeuse (<0) sur n séances."""
    etendue = (d["High"] - d["Low"]).replace(0, np.nan)
    mfm = ((d["Close"] - d["Low"]) - (d["High"] - d["Close"])) / etendue
    return (mfm * d["Volume"]).rolling(n).sum() / d["Volume"].rolling(n).sum().replace(0, np.nan)


def aroon_osc(d: pd.DataFrame, n: int = 25) -> pd.Series:
    """Aroon : depuis combien de temps le dernier plus haut / plus bas ? (-100 à +100)."""
    haut = d["High"].rolling(n + 1).apply(lambda x: x.argmax(), raw=True)
    bas = d["Low"].rolling(n + 1).apply(lambda x: x.argmin(), raw=True)
    return 100 * (haut - bas) / n


def supertrend_dir(d: pd.DataFrame, n: int = 10, mult: float = 3.0) -> pd.Series:
    """Supertrend : +1 tendance haussière, -1 baissière (bandes ATR qui suivent le cours)."""
    a = atr(d, n).to_numpy()
    hl2 = ((d["High"] + d["Low"]) / 2).to_numpy()
    c = d["Close"].to_numpy()
    haut_b, bas_b = hl2 + mult * a, hl2 - mult * a
    sens = np.ones(len(c))
    hf, bf = haut_b.copy(), bas_b.copy()
    for i in range(1, len(c)):
        hf[i] = haut_b[i] if (haut_b[i] < hf[i - 1] or c[i - 1] > hf[i - 1]) else hf[i - 1]
        bf[i] = bas_b[i] if (bas_b[i] > bf[i - 1] or c[i - 1] < bf[i - 1]) else bf[i - 1]
        if c[i] > hf[i - 1]:
            sens[i] = 1
        elif c[i] < bf[i - 1]:
            sens[i] = -1
        else:
            sens[i] = sens[i - 1]
    return pd.Series(sens, index=d.index)


def ichimoku_position(d: pd.DataFrame) -> pd.Series:
    """Position du cours par rapport au nuage Ichimoku : +1 au-dessus, -1 en dessous, 0 dedans.
    Le nuage du jour est calculé avec des données d'il y a 26 séances (aucune info du futur)."""
    mid = lambda n: (d["High"].rolling(n).max() + d["Low"].rolling(n).min()) / 2
    tenkan, kijun = mid(9), mid(26)
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = mid(52).shift(26)
    haut, bas = np.maximum(span_a, span_b), np.minimum(span_a, span_b)
    pos = np.where(d["Close"] > haut, 1.0, np.where(d["Close"] < bas, -1.0, 0.0))
    return pd.Series(pos, index=d.index).where(span_b.notna())


def divergences_rsi(d: pd.DataFrame, n: int = 20) -> pd.Series:
    """-1 : divergence baissière (nouveau plus haut du prix mais RSI plus faible),
    +1 : divergence haussière (nouveau plus bas du prix mais RSI plus fort), 0 sinon."""
    c, r = d["Close"], d["rsi"]
    haut_prix = c >= c.rolling(n).max() * 0.995
    bas_prix = c <= c.rolling(n).min() * 1.005
    baissiere = haut_prix & (r < r.rolling(n).max() - 5)
    haussiere = bas_prix & (r > r.rolling(n).min() + 5)
    return pd.Series(np.where(baissiere, -1.0, np.where(haussiere, 1.0, 0.0)), index=d.index)


NOMS_CHANDELIERS = {
    "doji": ("Doji", "hésitation : acheteurs et vendeurs s'équilibrent"),
    "marteau": ("Marteau", "après une baisse, les acheteurs ont repoussé les vendeurs : rebond possible"),
    "etoile_filante": ("Étoile filante", "après une hausse, les vendeurs ont repris la main : repli possible"),
    "englobante_haussiere": ("Englobante haussière", "une grosse bougie verte avale la rouge d'avant : signal de retournement à la hausse"),
    "englobante_baissiere": ("Englobante baissière", "une grosse bougie rouge avale la verte d'avant : signal de retournement à la baisse"),
    "etoile_matin": ("Étoile du matin", "figure en trois bougies qui annonce souvent la fin d'une baisse"),
    "etoile_soir": ("Étoile du soir", "figure en trois bougies qui annonce souvent la fin d'une hausse"),
}


def chandeliers(d: pd.DataFrame) -> pd.Series:
    """Repère les figures de chandeliers japonais classiques (nom de la figure ou chaîne vide)."""
    o, h, l, c = d["Open"], d["High"], d["Low"], d["Close"]
    corps = (c - o).abs()
    etendue = (h - l).replace(0, np.nan)
    haute = h - np.maximum(o, c)
    basse = np.minimum(o, c) - l
    vert, rouge = c > o, c < o
    baisse_avant = c.shift(1) < c.shift(5)
    hausse_avant = c.shift(1) > c.shift(5)
    corps_moy = corps.rolling(20).mean()
    f = pd.Series("", index=d.index, dtype=object)
    regles = [   # du moins prioritaire au plus prioritaire (le dernier vrai l'emporte)
        ("doji", corps <= 0.08 * etendue),
        ("marteau", baisse_avant & (basse >= 2 * corps) & (haute <= corps) & (corps > 0)),
        ("etoile_filante", hausse_avant & (haute >= 2 * corps) & (basse <= corps) & (corps > 0)),
        ("englobante_haussiere", baisse_avant & rouge.shift(1) & vert & (o <= c.shift(1)) & (c >= o.shift(1)) & (corps > corps.shift(1))),
        ("englobante_baissiere", hausse_avant & vert.shift(1) & rouge & (o >= c.shift(1)) & (c <= o.shift(1)) & (corps > corps.shift(1))),
        ("etoile_matin", rouge.shift(2) & (corps.shift(2) > corps_moy) & (corps.shift(1) < 0.4 * corps.shift(2))
         & vert & (c > (o.shift(2) + c.shift(2)) / 2)),
        ("etoile_soir", vert.shift(2) & (corps.shift(2) > corps_moy) & (corps.shift(1) < 0.4 * corps.shift(2))
         & rouge & (c < (o.shift(2) + c.shift(2)) / 2)),
    ]
    for nom, cond in regles:
        f[cond.fillna(False).astype(bool)] = nom
    return f


def calculer(df: pd.DataFrame, benchmark: pd.DataFrame | None = None,
             macro: dict | None = None) -> pd.DataFrame:
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

    # Indicateurs complémentaires (moyennes exponentielles, Ichimoku, flux d'argent…)
    for n in (9, 20, 50, 200):
        d[f"ema{n}"] = ema(c, n)
    d["dist_ema50_200"] = d["ema50"] / d["ema200"] - 1
    d["stoch_k"] = stochastique(d)
    d["mfi"] = mfi(d)
    d["cmf"] = cmf(d)
    vwap20 = (c * d["Volume"]).rolling(20).sum() / d["Volume"].rolling(20).sum().replace(0, np.nan)
    d["dist_vwap20"] = c / vwap20 - 1
    d["aroon"] = aroon_osc(d)
    don_h, don_b = d["High"].rolling(20).max(), d["Low"].rolling(20).min()
    d["donchian_pos"] = (c - don_b) / (don_h - don_b).replace(0, np.nan)
    d["supertrend"] = supertrend_dir(d)
    d["ichimoku"] = ichimoku_position(d)
    d["roc_10"] = c.pct_change(10)
    d["div_rsi"] = divergences_rsi(d)
    d["chandelier"] = chandeliers(d)

    # Contexte économique : peur des marchés (VIX), taux, dollar, sentiment crypto
    macro = macro or {}
    def aligne(nom):
        m = macro.get(nom)
        return None if m is None or len(m) == 0 else m.reindex(d.index, method="ffill")
    vix, taux, dollar, fng = aligne("vix"), aligne("taux"), aligne("dollar"), aligne("fng")
    d["vix"] = vix if vix is not None else np.nan
    d["vix_chg"] = vix.pct_change(20) if vix is not None else np.nan
    d["taux_chg"] = taux.diff(20) if taux is not None else np.nan
    d["dollar_chg"] = dollar.pct_change(20) if dollar is not None else np.nan
    d["fng"] = fng if fng is not None else np.nan

    return d.replace([np.inf, -np.inf], np.nan)


# Colonnes utilisées comme variables explicatives par le modèle de machine learning
FEATURES = [
    "dist_sma50", "dist_sma200", "pente_sma50", "adx", "rsi", "macd_hist_norm",
    "ret_5j", "ret_21j", "ret_63j", "ret_126j", "vol_20j", "atr_pct", "bb_position",
    "bb_largeur", "drawdown", "dist_plus_haut", "volume_ratio", "obv_pente",
    "force_relative_63j", "marche_tendance", "marche_vol",
    # ajoutés en version 2 (voir README : chaque ajout est mesuré par la validation walk-forward)
    "dist_ema50_200", "stoch_k", "mfi", "cmf", "dist_vwap20", "aroon", "donchian_pos",
    "supertrend", "ichimoku", "roc_10", "div_rsi",
    "vix", "vix_chg", "taux_chg", "dollar_chg", "fng",
]
