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
import re
import time
import urllib.parse
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
PERIODES_YAHOO = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
TAILLE_LOT = 40   # Yahoo bloque les gros téléchargements d'un coup : on envoie des lots


def _periode_yahoo() -> tuple[str, int | None]:
    """Yahoo n'accepte que certaines durées (1y, 2y, 5y, 10y, max…). Pour « 20y », on demande « max »
    puis on garde les 20 dernières années."""
    p = config.HISTORIQUE
    if p in PERIODES_YAHOO:
        return p, None
    m = re.fullmatch(r"(\d+)y", p)
    return "max", (int(m.group(1)) if m else None)


def _silencieux():
    """Coupe les messages « Failed to download » de yfinance : le radar fait son propre bilan."""
    import logging
    for nom in ("yfinance", "yfinance.base", "yfinance.data", "peewee"):
        logging.getLogger(nom).setLevel(logging.CRITICAL)
        logging.getLogger(nom).propagate = False


def _yahoo(tickers: list[str], progres=None, periode_forcee: str | None = None) -> dict[str, pd.DataFrame]:
    import contextlib
    import io
    import yfinance as yf
    _silencieux()
    periode, annees = (periode_forcee, None) if periode_forcee else _periode_yahoo()
    debut_min = pd.Timestamp.today() - pd.DateOffset(years=annees) if annees else None
    out: dict[str, pd.DataFrame] = {}

    def garder(t, df):
        df = _nettoyer(df.copy())
        if debut_min is not None and not df.empty:
            df = df[df.index >= debut_min]
        if not df.empty:
            out[t] = df

    lots = [tickers[k:k + TAILLE_LOT] for k in range(0, len(tickers), TAILLE_LOT)]
    for n, lot in enumerate(lots, 1):
        for tentative in range(3):
            manquants = [t for t in lot if t not in out]
            if not manquants:
                break
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    brut = yf.download(manquants, period=periode, interval="1d", auto_adjust=True,
                                       progress=False, group_by="ticker", threads=True)
                for t in manquants:
                    try:
                        df = brut[t] if isinstance(brut.columns, pd.MultiIndex) else brut
                    except KeyError:
                        continue
                    garder(t, df)
            except Exception:
                pass
            if len([t for t in lot if t not in out]) and tentative < 2:
                time.sleep(3 * (tentative + 1))   # pause plus longue si Yahoo freine
        if progres:
            progres(n / len(lots))
        if n < len(lots):
            time.sleep(1)
    # rattrapage titre par titre (certains passent mieux seuls)
    for t in [t for t in tickers if t not in out]:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                garder(t, yf.Ticker(t).history(period=periode, interval="1d", auto_adjust=True))
        except Exception:
            pass
        time.sleep(0.3)
    return out


# ----------------------------------------------------------------------------
# Sources de secours (si Yahoo ne répond pas pour un titre)
# ----------------------------------------------------------------------------
def _binance(ticker: str) -> pd.DataFrame:
    """Cryptos : bougies quotidiennes Binance (point d'accès public de données de marché)."""
    if not ticker.endswith("-USD"):
        return pd.DataFrame()
    symbole = config.symbole_binance(ticker)
    url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbole}&interval=1d&limit=1000"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "radar-bourse"})
        with urllib.request.urlopen(req, timeout=15) as r:
            lignes = json.load(r)
    except Exception:
        return pd.DataFrame()
    if not isinstance(lignes, list) or not lignes:
        return pd.DataFrame()
    df = pd.DataFrame([l[:6] for l in lignes], columns=["t", "Open", "High", "Low", "Close", "Volume"])
    df.index = pd.to_datetime(df.pop("t"), unit="ms").dt.normalize()
    return _nettoyer(df.astype(float))


def _symbole_stooq(ticker: str) -> str | None:
    speciaux = {"^FCHI": "^cac", "^VIX": None, "^TNX": None, "DX-Y.NYB": None, "GC=F": "xauusd"}
    if ticker in speciaux:
        return speciaux[ticker]
    if ticker.endswith("-USD"):
        return None
    if ticker.endswith(".PA"):
        return ticker[:-3].lower() + ".fr"
    if re.fullmatch(r"[A-Z.]{1,6}", ticker):
        return ticker.lower().replace(".", "-") + ".us"
    return None


def _stooq(ticker: str) -> pd.DataFrame:
    """Actions, ETF et indices : historique quotidien Stooq (CSV gratuit)."""
    sym = _symbole_stooq(ticker)
    if not sym:
        return pd.DataFrame()
    url = "https://stooq.com/q/d/l/?" + urllib.parse.urlencode({"s": sym, "i": "d"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 radar-bourse"})
        with urllib.request.urlopen(req, timeout=15) as r:
            texte = r.read().decode("utf-8", "replace")
        if not texte.startswith("Date"):
            return pd.DataFrame()
        import io
        df = pd.read_csv(io.StringIO(texte), index_col=0, parse_dates=True)
        if "Volume" not in df:
            df["Volume"] = 0.0
        return _nettoyer(df.iloc[-1300:])
    except Exception:
        return pd.DataFrame()


SOURCES_UTILISEES: dict[str, str] = {}


def telecharger_plusieurs(tickers: list[str], max_age_h: float | None = None, progres=None) -> dict[str, pd.DataFrame]:
    """Renvoie {ticker: cours} pour tous les titres trouvés (les introuvables sont ignorés)."""
    tickers = list(dict.fromkeys(tickers))
    if max_age_h is None:
        max_age_h = config.CACHE_MAX_H
    if DEMO:
        SOURCES_UTILISEES.update({t: "Démo" for t in tickers})
        return {t: cours_synthetiques(t) for t in tickers}

    resultats = {t: df for t in tickers if not (df := _lire_cache(t, max_age_h)).empty}
    for t in resultats:
        SOURCES_UTILISEES.setdefault(t, "Yahoo (cache récent)")
    # Mise à jour express : pour les titres déjà en mémoire (moins de 10 jours), on ne télécharge que le
    # dernier mois et on le colle à l'historique. Bien plus rapide, et Yahoo bloque moins.
    anciens = {t: df for t in tickers if t not in resultats and len(df := _lire_cache(t, 24 * 10)) > 200}
    if anciens:
        recents = _yahoo(list(anciens), periode_forcee="1mo")
        for t, neuf in recents.items():
            vieux = anciens[t]
            commun = vieux.index.intersection(neuf.index)
            # si un dividende ou une division d'actions a changé les anciens prix ajustés, on retélécharge tout
            if len(commun) >= 3:
                ecart = (neuf.loc[commun, "Close"] / vieux.loc[commun, "Close"] - 1).abs().max()
                if ecart > 0.005:
                    continue
            elif len(commun) == 0 and neuf.index.min() > vieux.index.max() + pd.Timedelta(days=5):
                continue
            df = pd.concat([vieux[~vieux.index.isin(neuf.index)], neuf]).sort_index()
            df.to_csv(_chemin_cache(t))
            resultats[t] = df
            SOURCES_UTILISEES[t] = "Yahoo (mise à jour express)"
        if progres:
            progres(0.1)
    a_telecharger = [t for t in tickers if t not in resultats]
    if a_telecharger:
        frais = _yahoo(a_telecharger, progres)
        for t in frais:
            SOURCES_UTILISEES[t] = "Yahoo"
        maintenant = pd.Timestamp.now().normalize()

        def douteux(df, t):
            """Série absente, trop courte ou figée : on essaie la source de secours (ex. Toncoin chez Yahoo)."""
            if df is None or len(df) < 260:
                return True
            dernier = pd.Timestamp(df.index[-1])
            dernier = dernier.tz_localize(None) if dernier.tzinfo else dernier
            return (maintenant - dernier.normalize()).days > (4 if t.endswith("-USD") else 8)
        for t in a_telecharger:   # secours : Binance pour les cryptos, Stooq pour le reste
            if douteux(frais.get(t), t):
                df = _binance(t) if t.endswith("-USD") else _stooq(t)
                if len(df) >= 260 and (frais.get(t) is None or not douteux(df, t)):
                    frais[t] = df
                    SOURCES_UTILISEES[t] = "Binance" if t.endswith("-USD") else "Stooq"
        for t, df in frais.items():
            df.to_csv(_chemin_cache(t))
            resultats[t] = df
        for t in a_telecharger:  # secours : vieux cache si le réseau a échoué
            if t not in resultats and not (vieux := _lire_cache(t, None)).empty:
                resultats[t] = vieux
                SOURCES_UTILISEES[t] = "ancien cache"
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
                # Filtre anti « penny stocks » : sur ces petites valeurs, les hausses spectaculaires
                # sont souvent des manipulations (pump & dump). On garde les sociétés solides.
                prix = q.get("regularMarketPrice") or 0
                capi = q.get("marketCap") or 0
                if q.get("quoteType", "EQUITY") == "EQUITY" and prix >= 5 and capi >= 2e9:
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
        for item in data.get("coins", [])[:15]:
            c = item["item"]
            rang = c.get("market_cap_rank")
            # seulement les cryptos établies (top 150) : les micro-jetons à la mode sont trop risqués
            if rang and rang <= 150 and re.fullmatch(r"[A-Z0-9]{2,10}", c["symbol"].upper()):
                out[f"{c['symbol'].upper()}-USD"] = c["name"]
    except Exception:
        pass
    return out


def devise(ticker: str) -> str:
    if ticker.endswith((".PA", ".AS", ".DE", ".MI", ".MC")) or ticker in ("^FCHI", "^STOXX50E"):
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


# ----------------------------------------------------------------------------
# Contexte économique (peur des marchés, taux, dollar, or, sentiment crypto)
# ----------------------------------------------------------------------------
MACRO_TICKERS = {"vix": "^VIX", "taux": "^TNX", "dollar": "DX-Y.NYB", "or": "GC=F",
                 # économie : pétrole, cuivre (thermomètre de l'industrie), taux court américain (3 mois)
                 "petrole": "CL=F", "cuivre": "HG=F", "taux_court": "^IRX",
                 # peur à 3 mois : comparée à la peur à 1 mois (VIX), elle dit si la panique est immédiate
                 "vix3m": "^VIX3M"}

# Indicateurs économiques de la Réserve fédérale de Saint-Louis (FRED), gratuits et sans clé.
# Le décalage (jours) reproduit le délai de publication : l'IA ne voit jamais un chiffre avant
# qu'il ait été réellement publié (sinon elle « tricherait » en regardant le futur).
FRED_SERIES = {
    "spread_credit": ("BAMLH0A0HYM2", 1),   # prime de risque des entreprises fragiles (quotidien)
    "conditions_fin": ("NFCI", 7),          # tension du système financier (hebdomadaire)
    "chomage": ("ICSA", 7),                 # inscriptions au chômage aux États-Unis (hebdomadaire)
}


def _fred(code: str, decalage_jours: int) -> pd.Series:
    try:
        req = urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}",
                                     headers={"User-Agent": "radar-bourse"})
        with urllib.request.urlopen(req, timeout=20) as r:
            df = pd.read_csv(r)
        df.columns = ["date", "valeur"]
        s = pd.Series(pd.to_numeric(df["valeur"], errors="coerce").to_numpy(), index=pd.to_datetime(df["date"])).dropna()
        s.index = s.index + pd.Timedelta(days=decalage_jours)
        return s.sort_index()
    except Exception:
        return pd.Series(dtype=float)


def _fear_greed() -> pd.Series:
    """Indice Fear & Greed crypto (alternative.me, gratuit, historique complet)."""
    try:
        req = urllib.request.Request("https://api.alternative.me/fng/?limit=0&format=json",
                                     headers={"User-Agent": "radar-bourse"})
        with urllib.request.urlopen(req, timeout=15) as r:
            brut = json.load(r).get("data", [])
        s = pd.Series({pd.Timestamp(int(x["timestamp"]), unit="s").normalize(): float(x["value"])
                       for x in brut})
        return s.sort_index()
    except Exception:
        return pd.Series(dtype=float)


def macro() -> dict[str, pd.Series]:
    """Séries de contexte (cours de clôture), indexées par date. Vide si indisponible."""
    if DEMO:
        out = {}
        for nom, t in MACRO_TICKERS.items():
            out[nom] = cours_synthetiques(t)["Close"] / (5 if nom in ("vix", "taux") else 1)
        idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=1260, freq="D")
        rng = np.random.default_rng(7)
        out["fng"] = pd.Series(np.clip(50 + np.cumsum(rng.normal(0, 4, len(idx))) % 80, 5, 95), index=idx)
        for nom in FRED_SERIES:
            out[nom] = cours_synthetiques("FRED-" + nom)["Close"] / 50
        return out
    bruts = telecharger_plusieurs(list(MACRO_TICKERS.values()))
    out = {nom: bruts[t]["Close"] for nom, t in MACRO_TICKERS.items() if t in bruts}
    fng = _fear_greed()
    if len(fng):
        out["fng"] = fng
    for nom, (code, decalage) in FRED_SERIES.items():
        serie = _fred(code, decalage)
        if len(serie):
            out[nom] = serie
    return out


# ---------------------------------------------------------------------------
# Petit cache sur disque pour les données qui changent lentement (fondamentaux, actus).
# Avec plus de titres suivis, on évite de redemander la même chose à Yahoo chaque heure.
def cache_json(nom: str, cle: str, duree_h: float, calcul):
    """Renvoie la valeur en cache si elle a moins de `duree_h` heures, sinon la recalcule et l'enregistre.
    Le cache n'est qu'un accélérateur : la moindre erreur de lecture ou d'écriture est ignorée."""
    import json as _json
    import time as _time
    chemin = os.path.join(config.DOSSIER_CACHE, f"{nom}.json")
    try:
        with open(chemin, encoding="utf-8") as f:
            tout = _json.load(f)
    except (OSError, ValueError):
        tout = {}
    e = tout.get(cle)
    if isinstance(e, dict) and _time.time() - float(e.get("t", 0)) < duree_h * 3600:
        return e.get("v")
    v = calcul()
    tout[cle] = {"t": _time.time(), "v": v}
    try:
        os.makedirs(config.DOSSIER_CACHE, exist_ok=True)
        with open(chemin + ".tmp", "w", encoding="utf-8") as f:
            _json.dump(tout, f, ensure_ascii=False)
        os.replace(chemin + ".tmp", chemin)
    except OSError:
        pass
    return v

