"""Génère le site « Radar Bourse » : une page autonome (site/index.html) avec toutes les données."""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from importlib import resources

import numpy as np
import pandas as pd

from . import backtest, config, fondamentaux, seo
from .indicators import NOMS_CHANDELIERS
from .scoring import propre

INDICES = [("^FCHI", "CAC 40"), ("SPY", "S&P 500"), ("QQQ", "Nasdaq 100"), ("BTC-USD", "Bitcoin")]
JOURS_GRAPHIQUE = 400   # ~1 an et demi de bougies dans chaque graphique
Z_80 = 1.2816           # fourchette « 8 chances sur 10 » (quantiles 10 % et 90 %)

# Politique de sécurité du contenu : la page ne peut charger que ce dont elle a besoin
CSP = ("default-src 'self'; "
       "script-src 'self' 'unsafe-inline'; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; "
       "img-src 'self' data:; "
       "connect-src 'self' https://api.binance.com wss://stream.binance.com:9443 wss://ws.finnhub.io; "
       "object-src 'none'; base-uri 'none'; form-action 'none'")


def _arrondi(v):
    if v is None or not np.isfinite(v):
        return None
    return float(f"{v:.6g}")


def _serie(d: pd.DataFrame, jours: int = JOURS_GRAPHIQUE) -> dict:
    d = d.iloc[-jours:]
    return {"t": [f"{x:%Y-%m-%d}" for x in d.index],
            **{k: [_arrondi(v) for v in d[col]] for k, col in
               (("o", "Open"), ("h", "High"), ("l", "Low"), ("c", "Close"), ("v", "Volume"),
                ("sma50", "sma50"), ("sma200", "sma200"), ("bbh", "bb_haut"), ("bbb", "bb_bas"),
                ("rsi", "rsi"))}}


def _cone(a, d: pd.DataFrame, rendement: float, horizon: int) -> dict | None:
    """Prévision : trajectoire médiane (rendement historique observé pour cette probabilité)
    entourée d'une fourchette à 80 % tirée de la volatilité réelle du titre."""
    vol_an = a.perf.get("volatilité annuelle")
    if vol_an is None or not np.isfinite(vol_an) or not np.isfinite(rendement):
        return None
    crypto = a.ticker.endswith("-USD")
    vol_j = vol_an / np.sqrt(365 if crypto else 252)
    dates = pd.date_range(d.index[-1], periods=horizon + 1, freq="D" if crypto else "B")
    k = np.arange(horizon + 1)
    mediane = a.prix * (1 + rendement) ** (k / horizon)
    ecart = np.exp(Z_80 * vol_j * np.sqrt(k))
    a.fourchette = (float(mediane[-1] / ecart[-1]), float(mediane[-1] * ecart[-1]))
    return {"t": [f"{x:%Y-%m-%d}" for x in dates],
            "mediane": [_arrondi(v) for v in mediane],
            "haut": [_arrondi(v) for v in mediane * ecart],
            "bas": [_arrondi(v) for v in mediane / ecart]}


def _niveaux(d: pd.DataFrame) -> dict:
    x = d.iloc[-1]
    return {"support": _arrondi(d["Low"].iloc[-20:].min()),        # plus bas des 20 dernières séances
            "resistance": _arrondi(d["Close"].iloc[-252:].max()),  # plus haut sur un an
            "sma50": _arrondi(x["sma50"]), "sma200": _arrondi(x["sma200"]),
            "rsi": _arrondi(x["rsi"]), "adx": _arrondi(x["adx"])}


def _backtest(ticker: str, d: pd.DataFrame) -> dict | None:
    jours_an = 365 if ticker.endswith("-USD") else 252
    dispo = len(d.dropna(subset=["sma200"])) / jours_an
    if dispo < 1:
        return None
    annees = min(3, int(dispo))
    try:
        r = backtest.lancer(ticker, d, 1000, annees)
    except Exception:
        return None
    return {"annees": annees, "bot": r.stats_strategie["rendement total"],
            "garder": r.stats_buy_hold["rendement total"],
            "trades": r.stats_strategie["nombre de trades"],
            "drawdown_bot": r.stats_strategie["pire baisse (drawdown)"]}


def construire(analyses, donnees, evaluation, suivi, indices_bruts, demo=False, actus_marche=None) -> dict:
    horizon = config.HORIZON_PREDICTION
    titres = []
    for a in sorted(analyses, key=lambda a: a.score, reverse=True):
        d = donnees[a.ticker]
        if evaluation is not None and a.proba_hausse == a.proba_hausse:
            a.rendement_attendu = evaluation.rendement_attendu(a.proba_hausse)
        rend = a.rendement_attendu if a.rendement_attendu == a.rendement_attendu else 0.0
        item = a.to_dict()
        item["cone"] = _cone(a, d, rend, horizon)
        item["fourchette"] = list(a.fourchette)
        item["serie"] = _serie(d)
        item["niveaux"] = _niveaux(d)
        fig = d["chandelier"].iloc[-120:]
        item["chandeliers"] = [{"t": f"{dt:%Y-%m-%d}", "code": c, "nom": NOMS_CHANDELIERS[c][0],
                                "sens": NOMS_CHANDELIERS[c][1]}
                               for dt, c in fig.items() if c and c != "doji" and c in NOMS_CHANDELIERS]
        item["backtest"] = _backtest(a.ticker, d)
        item["prev_close"] = float(d["Close"].iloc[-2]) if len(d) > 1 else None
        item["spark"] = [_arrondi(v) for v in d["Close"].iloc[-63:]]
        # rendements quotidiens réels (3 dernières années) pour le simulateur Monte-Carlo du site
        lr = np.log(d["Close"]).diff().dropna().iloc[-750:]
        item["rendements"] = [round(float(v), 5) for v in lr if np.isfinite(v)]
        item["jours_an"] = 365 if a.ticker.endswith("-USD") else 252
        x = d.iloc[-1]
        item["au_dessus_200"] = bool(x["Close"] > x["sma200"]) if x["sma200"] == x["sma200"] else None
        titres.append(item)

    indices = []
    for t, nom in INDICES:
        d = indices_bruts.get(t)
        if d is None or len(d) < 2:
            continue
        c = d["Close"]
        indices.append({"ticker": t, "nom": nom, "prix": float(c.iloc[-1]),
                        "var_jour": float(c.iloc[-1] / c.iloc[-2] - 1),
                        "devise": "€" if t == "^FCHI" else "$",
                        "prev_close": float(c.iloc[-2]),
                        "spark": [_arrondi(v) for v in c.iloc[-60:]]})

    # Contexte économique : dernière valeur et évolution sur un mois
    contexte = []
    infos = {"vix": ("Peur des marchés (VIX)", "pts", "Sous 15 : marché calme. Au-dessus de 30 : forte nervosité."),
             "taux": ("Taux à 10 ans américain", "%", "Des taux qui montent pèsent souvent sur les actions de croissance."),
             "dollar": ("Dollar (indice DXY)", "pts", "Un dollar fort pèse souvent sur les cryptos et les matières premières."),
             "or": ("Or (once)", "$", "Valeur refuge : il monte souvent quand les investisseurs ont peur."),
             "fng": ("Sentiment crypto (Fear & Greed)", "/100", "0 = peur extrême, 100 = avidité extrême.")}
    for cle, serie in (indices_bruts.get("__macro__") or {}).items():
        serie = serie.dropna()
        if cle not in infos or len(serie) < 25:
            continue
        nom, unite, aide = infos[cle]
        v, avant = float(serie.iloc[-1]), float(serie.iloc[-22])
        contexte.append({"cle": cle, "nom": nom, "valeur": v, "unite": unite, "aide": aide,
                         "variation": (v - avant) if cle in ("taux", "fng") else (v / avant - 1),
                         "variation_type": "points" if cle in ("taux", "fng") else "pct",
                         "spark": [_arrondi(x) for x in serie.iloc[-60:]]})

    # Taux de change pour le portefeuille virtuel (les cours en $ sont convertis en €)
    usd_eur = 0.92
    fx = indices_bruts.get("EURUSD=X")
    if fx is not None and len(fx) and not demo:
        dernier = float(fx["Close"].iloc[-1])
        if 0.5 < dernier < 2:
            usd_eur = 1 / dernier

    date_max = max(a.date_cours for a in analyses)
    return propre({
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "date_donnees": date_max, "demo": demo, "horizon": horizon,
        "modele": None if evaluation is None else evaluation.to_dict(),
        "suivi": suivi, "indices": indices, "titres": titres,
        "live": {"finnhub": config.FINNHUB_CLE},
        "actus_marche": actus_marche or [],
        "legal": {"editeur": config.EDITEUR, "contact": config.CONTACT, "conflits": config.CONFLITS},
        "contexte": contexte,
        "usd_eur": usd_eur,
        "telegram": config.TELEGRAM_CHAINE.lstrip("@") if config.TELEGRAM_CHAINE else "",
        "fondamentaux_libelles": fondamentaux.libelles(),
    })


def _json_sur(payload: dict) -> str:
    """JSON insérable sans risque dans une balise <script>."""
    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return (s.replace("</", "<\\/").replace("<!--", "<\\!--")
             .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


CHAMPS_DETAIL = ("serie", "rendements", "cone", "chandeliers", "backtest", "niveaux", "actus",
                 "fondamentaux", "raisons_pour", "raisons_contre")
TOUJOURS_COMPLETS = {"^FCHI", "SPY", "QQQ", "BTC-USD"}  # utilisés par le graphique de l'accueil


def _decouper(payload: dict, dossier: str) -> dict:
    """Sort les données lourdes de chaque titre dans donnees/<titre>.json (chargées à l'ouverture
    de la fiche). La page d'accueil devient plusieurs fois plus légère."""
    os.makedirs(os.path.join(dossier, "donnees"), exist_ok=True)
    leger = dict(payload)
    leger["titres"] = []
    for t in payload["titres"]:
        if t["ticker"] in TOUJOURS_COMPLETS:
            leger["titres"].append(t)
            continue
        nom = f"donnees/{seo.slug(t['ticker'])}.json"
        with open(os.path.join(dossier, nom), "w", encoding="utf-8") as f:
            json.dump({k: t.get(k) for k in CHAMPS_DETAIL}, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        court = {k: v for k, v in t.items() if k not in CHAMPS_DETAIL}
        court["detail"] = nom
        leger["titres"].append(court)
    return leger


def ecrire(payload: dict, dossier: str = config.DOSSIER_SITE, pour_artifact: bool = False) -> str:
    gabarit = resources.files(__package__).joinpath("site_template.html").read_text(encoding="utf-8")
    # En ligne (robot GitHub), on découpe ; en local (ouverture du fichier sur le PC), tout reste
    # dans la page car les navigateurs bloquent la lecture de fichiers voisins en « file:// ».
    decouper = not pour_artifact and (os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("RADAR_DECOUPER") == "1")
    if os.path.isdir(os.path.join(dossier, "donnees")):
        shutil.rmtree(os.path.join(dossier, "donnees"))
    page = gabarit.replace("/*__DATA__*/null", _json_sur(_decouper(payload, dossier) if decouper else payload))
    tete, corps = page.split("<!--__CORPS__-->", 1)
    if pour_artifact:  # aperçu Claude : bibliothèque depuis un CDN autorisé, pas de CSP propre
        lib = '<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>'
        html = tete.replace("<!--__LIB__-->", lib) + corps
    else:              # vrai site : tout est servi par le site lui-même
        lib = '<script src="lightweight-charts.js"></script>'
        # balises de référencement complètes à la place des balises minimales de l'aperçu
        debut, fin = tete.index("<!--META-->"), tete.index("<!--/META-->") + len("<!--/META-->")
        tete = (tete[:debut] + seo.balises_tete(seo.url_site(), f"{seo.NOM} : prévisions boursières à un mois, actions et cryptos",
                                                 seo.DESCRIPTION, "", jsonld=seo.jsonld_accueil()) + tete[fin:])
        tete = tete.replace("<title>Radar Bourse</title>",
                            f"<title>{seo.NOM} : prévisions boursières à un mois, actions et cryptos</title>", 1)
        corps = corps.replace("<!--__LIENS_SEO__-->", seo.liens_accueil(payload), 1)
        securite = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
                    '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
        html = ("<!doctype html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
                + securite + tete.replace("<!--__LIB__-->", lib) + "\n</head>\n<body>\n" + corps
                + "\n</body>\n</html>\n")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "index.html")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(html)
    if not pour_artifact:
        vendeur = resources.files(__package__).joinpath("vendor")
        for nom in ("lightweight-charts.js", "LICENSE-lightweight-charts.txt"):
            with resources.as_file(vendeur.joinpath(nom)) as src:
                shutil.copyfile(src, os.path.join(dossier, nom))
        # petit fichier public servant seulement à détecter une nouvelle version des prévisions
        with open(os.path.join(dossier, "version.json"), "w", encoding="utf-8") as f:
            json.dump({"genere_le": payload["genere_le"]}, f)
        seo.generer(payload, dossier, CSP)
        ancien = os.path.join(dossier, "donnees.json")
        if os.path.exists(ancien):
            os.remove(ancien)
    return chemin
