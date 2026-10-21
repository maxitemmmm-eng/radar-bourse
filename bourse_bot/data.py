"""Récupération des données de marché (Yahoo Finance + CoinGecko), avec cache local.

Fiabilité :
- téléchargement groupé (plus rapide, moins de blocages par Yahoo) puis rattrapage titre par titre ;
- 3 tentatives avec pause en cas d'échec réseau ;
- si Internet ou Yahoo tombe, on réutilise le dernier cache disponible (même ancien) ;
- mode démo : cours synthétiques réalistes pour tester sans Internet.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import zlib

import numpy as np
import pandas as pd

from . import config

DEMO = False  # activé par l'option --demo
COLONNES = ["Open", "High", "Low", "Close", "Volume"]


# ----------------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------------
def _chemin_cache(ticker: str) -> str:
    os.makedirs(config.DOSSIER_CACHE, exist_ok=True)
    nom = "".join(c if c.isalnum() or c in "-._" else "_" for c in ticker)
    return os.path.join(config.DOSSIER_CACHE, f"{nom}.csv")


def _lire_cache(ticker: str, max_age_h: float | None) -> pd.DataFrame:
    chemin = _chemin_cache(ticker)
    if not os.path.exists(chemin):
        return pd.DataFrame()
    if max_age_h is not None and time.time() - os.path.getmtime(chemin) > max_age_h * 3600:
        return pd.DataFrame()
    try:
        return pd.read_csv(chemin, index_col=0, parse_dates=True)
    except Exception:
        return pd.DataFrame()


def _nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if not set(COLONNES) <= set(df.columns):
        return pd.DataFrame()
    df = df[COLONNES].apply(pd.to_numeric, errors="coerce").dropna(subset=["Close"])
    df = df[df["Close"] > 0]
    df["Volume"] = df["Volume"].fillna(0)
    for c in ("Open", "High", "Low"):  # certaines cotations n'ont que le cours de clôture
        df[c] = df[c].fillna(df["Close"])
    idx = pd.to_datetime(df.index)
    df.index = idx.tz_localize(None) if idx.tz is not None else idx
    return df[~df.index.duplicated(keep="last")].sort_index()


# ----------------------------------------------------------------------------
# Téléchargement
# ----------------------------------------------------------------------------
def _yahoo(tickers: list[str]) -> dict[str, pd.DataFrame]:
    import yfinance as yf
    out: dict[str, pd.DataFrame] = {}
    for tentative in range(3):
        manquants = [t for t in tickers if t not in out]
        if not manquants:
            break
        try:
            brut = yf.download(manquants, period=config.HISTORIQUE, interval="1d",
                               auto_adjust=True, progress=False, group_by="ticker", threads=True)
            for t in manquants:
                try:
                    df = brut[t] if isinstance(brut.columns, pd.MultiIndex) else brut
                except KeyError:
                    continue
                df = _nettoyer(df.copy())
                if not df.empty:
                    out[t] = df
        except Exception:
            pass
        if tentative < 2 and len(out) < len(tickers):
            time.sleep(2 * (tentative + 1))
    return out


def telecharger_plusieurs(tickers: list[str], max_age_h: float | None = None) -> dict[str, pd.DataFrame]:
    """Renvoie {ticker: cours} pour tous les titres trouvés (les introuvables sont ignorés)."""
    tickers = list(dict.fromkeys(tickers))
    if max_age_h is None:
        max_age_h = config.CACHE_MAX_H
    if DEMO:
        return {t: cours_synthetiques(t) for t in tickers}

    resultats = {t: df for t in tickers if not (df := _lire_cache(t, max_age_h)).empty}
    a_telecharger = [t for t in tickers if t not in resultats]
    if a_telecharger:
        frais = _yahoo(a_telecharger)
        for t, df in frais.items():
            df.to_csv(_chemin_cache(t))
            resultats[t] = df
        for t in a_telecharger:  # secours : vieux cache si le réseau a échoué
            if t not in resultats and not (vieux := _lire_cache(t, None)).empty:
                resultats[t] = vieux
    return resultats


def telecharger(ticker: str) -> pd.DataFrame:
    return telecharger_plusieurs([ticker]).get(ticker, pd.DataFrame())


# ----------------------------------------------------------------------------
# Titres "en tendance"
# ----------------------------------------------------------------------------
def tendances_actions(n: int = 15) -> dict[str, str]:
    """Plus fortes hausses et titres les plus échangés du jour (marché US, via Yahoo)."""
    if DEMO:
        return {"DEMO1": "Démo Tendance 1", "DEMO2": "Démo Tendance 2"}
    out: dict[str, str] = {}
    try:
        import yfinance as yf
        for ecran in ("day_gainers", "most_actives"):
            for q in yf.screen(ecran, count=n).get("quotes", []):
                if q.get("quoteType", "EQUITY") == "EQUITY":
                    out[q["symbol"]] = q.get("shortName") or q["symbol"]
    except Exception:
        pass  # le screener Yahoo change parfois de format : on continue sans
    return out


def tendances_crypto() -> dict[str, str]:
    """Cryptos les plus recherchées sur CoinGecko (API gratuite, sans clé)."""
    if DEMO:
        return {"DEMOC-USD": "Démo Crypto Tendance"}
    out: dict[str, str] = {}
    try:
        req = urllib.request.Request("https://api.coingecko.com/api/v3/search/trending",
                                     headers={"User-Agent": "radar-bourse"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        for item in data.get("coins", [])[:10]:
            c = item["item"]
            out[f"{c['symbol'].upper()}-USD"] = c["name"]
    except Exception:
        pass
    return out


def devise(ticker: str) -> str:
    if ticker.endswith((".PA", ".AS", ".DE", ".MI", ".MC")) or ticker == "^FCHI":
        return "€"
    return "$"


# ----------------------------------------------------------------------------
# Données synthétiques (mode démo / tests)
# ----------------------------------------------------------------------------
def cours_synthetiques(ticker: str, n: int = 1260) -> pd.DataFrame:
    """Marche aléatoire avec régimes de tendance et de volatilité (déterministe par ticker)."""
    rng = np.random.default_rng(zlib.crc32(ticker.encode()))
    crypto = ticker.endswith("-USD")
    vol_base = 0.035 if crypto else 0.017
    rendements = np.empty(n)
    derive, vol = 0.0004, vol_base
    for i in range(n):
        if i % 60 == 0:
            derive = rng.normal(0.0004, 0.0015)
            vol = vol_base * rng.uniform(0.6, 1.6)
        rendements[i] = rng.normal(derive, vol)
    close = rng.uniform(20, 400) * np.exp(np.cumsum(rendements))
    ecart = np.abs(rng.normal(0, vol_base * 0.6, n))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, vol_base * 0.2, n))
    high = np.maximum(close, open_) * (1 + ecart)
    low = np.minimum(close, open_) * (1 - ecart)
    volume = rng.lognormal(15, 0.4, n) * (1 + 8 * np.abs(rendements))
    freq = "D" if crypto else "B"
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq=freq)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close,
                         "Volume": volume}, index=dates)
