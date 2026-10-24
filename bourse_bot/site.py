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

INDICES = [("^FCHI", "CAC 40"), ("^STOXX50E", "Euro Stoxx 50"), ("SPY", "S&P 500"), ("QQQ", "Nasdaq 100"), ("BTC-USD", "Bitcoin")]
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


def _trajectoire(prix, q, k, horizon):
    """Prix bas / central / haut après k séances, à partir des scénarios de l'IA à l'horizon."""
    b, m, h = q
    f = k / horizon
    centre = m * f
    return (prix * np.exp(centre - (m - b) * np.sqrt(f)), prix * np.exp(centre),
            prix * np.exp(centre + (h - m) * np.sqrt(f)))


def _cone(a, d: pd.DataFrame, rendement: float, horizon: int) -> dict | None:
    """Fourchette de prix pour les prochaines séances. Priorité aux scénarios appris par l'IA
    (quantiles corrigés pour tenir 8 fois sur 10) ; sinon, estimation par la volatilité."""
    crypto = a.ticker.endswith("-USD")
    dates = pd.date_range(d.index[-1], periods=horizon + 1, freq="D" if crypto else "B")
    if len(a.quantiles) == 3:
        pts = [_trajectoire(a.prix, a.quantiles, k, horizon) for k in range(horizon + 1)]
        a.fourchette = (float(pts[-1][0]), float(pts[-1][2]))
        return {"t": [f"{x:%Y-%m-%d}" for x in dates], "source": "ia",
                "bas": [_arrondi(p[0]) for p in pts], "mediane": [_arrondi(p[1]) for p in pts],
                "haut": [_arrondi(p[2]) for p in pts]}
    return _cone_volatilite(a, d, rendement, horizon)


def _previsions(a, horizon: int) -> dict | None:
    """Estimations à 1 semaine, 2 semaines et 1 mois (pour l'espace simulation).
    Actions : 5, 10 et 20 séances. Cryptos (cotées 7 j/7) : 7, 14 et 30 jours."""
    if len(a.quantiles) != 3:
        return None
    pas = (7, 14, 30) if a.ticker.endswith("-USD") else (5, 10, horizon)
    out = {}
    for nom, k in zip(("1s", "2s", "1m"), pas):
        b, m, h = _trajectoire(a.prix, a.quantiles, k, horizon)
        out[nom] = {"bas": _arrondi(b), "centre": _arrondi(m), "haut": _arrondi(h)}
        if len(a.extremes) == 2:   # scénarios extrêmes (1 chance sur 20 de chaque côté), mode risque
            eb, _, eh = _trajectoire(a.prix, (a.extremes[0], a.quantiles[1], a.extremes[1]), k, horizon)
            out[nom]["ext_bas"], out[nom]["ext_haut"] = _arrondi(eb), _arrondi(eh)
    return out


def _cone_volatilite(a, d: pd.DataFrame, rendement: float, horizon: int) -> dict | None:
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


def _dernier_entrainement():
    """Dernier entraînement approfondi lancé sur le PC (entrainement_ia.py), pour l'afficher sur le site."""
    try:
        from .model import _lire_fichier_modele
        liste = [e for e in ((_lire_fichier_modele() or {}).get("entrainements") or []) if not e.get("demo")]
        if not liste:
            return None
        e = liste[-1]
        out = {k: e.get(k) for k in ("date", "mode", "nb_titres", "nb_lignes", "retenu", "en_place", "change_methode",
                                     "raison", "series_economiques", "examen_donnees", "precision", "ic_precision", "connaissances")}
        # l'examen des crises n'est fait qu'en mode Normal ou Expert : on garde le plus récent disponible
        avec = [x for x in liste if x.get("crises")]
        if avec:
            out["crises"] = avec[-1]["crises"]
            out["crises_date"] = avec[-1].get("date")
        return out
    except Exception:
        return None


def construire(analyses, donnees, evaluation, suivi, indices_bruts, demo=False, actus_marche=None,
               qualite=None) -> dict:
    horizon = config.HORIZON_PREDICTION
    titres = []
    for a in sorted(analyses, key=lambda a: a.score, reverse=True):
        d = donnees[a.ticker]
        if evaluation is not None and a.proba_hausse == a.proba_hausse:
            a.rendement_attendu = evaluation.rendement_attendu(a.proba_hausse)
        rend = a.rendement_attendu if a.rendement_attendu == a.rendement_attendu else 0.0
        if len(a.quantiles) == 3:   # rendement central appris par l'IA
            a.rendement_attendu = float(np.expm1(a.quantiles[1]))
            rend = a.rendement_attendu
        item = a.to_dict()
        item["cone"] = _cone(a, d, rend, horizon)
        item["previsions"] = _previsions(a, horizon)
        item["fourchette"] = list(a.fourchette)
        item["serie"] = _serie(d)
        item["niveaux"] = _niveaux(d)
        fig = d["chandelier"].iloc[-30:]   # seulement les figures récentes, pour garder un graphique lisible
        item["chandeliers"] = [{"t": f"{dt:%Y-%m-%d}", "code": c, "nom": NOMS_CHANDELIERS[c][0],
                                "sens": NOMS_CHANDELIERS[c][1]}
                               for dt, c in fig.items() if c and c != "doji" and c in NOMS_CHANDELIERS]
        item["backtest"] = _backtest(a.ticker, d)
        item["prev_close"] = float(d["Close"].iloc[-2]) if len(d) > 1 else None
        q = (qualite or {}).get("details", {}).get(a.ticker)
        item["qualite_ok"] = True if q is None else q["ok"]
        item["spark"] = [float(f"{v:.4g}") for v in d["Close"].iloc[-63:] if np.isfinite(v)]
        # rendements quotidiens réels (3 dernières années) pour le simulateur Monte-Carlo du site
        lr = np.log(d["Close"]).diff().dropna().iloc[-750:]
        item["rendements"] = [round(float(v), 5) for v in lr if np.isfinite(v)]
        item["jours_an"] = 365 if a.ticker.endswith("-USD") else 252
        x = d.iloc[-1]
        item["au_dessus_200"] = bool(x["Close"] > x["sma200"]) if x["sma200"] == x["sma200"] else None
        item["indice_nom"] = config.NOM_BENCHMARK.get(a.indice_ref, a.indice_ref)
        # quelques chiffres d'entreprise gardés dans la page légère (filtre de recherche) ; le détail reste dans la fiche
        fv = ((a.fondamentaux or {}).get("valeurs") or {}) if getattr(a, "fondamentaux", None) else {}
        item["div"] = _arrondi(fv.get("dividendYield")) if fv.get("dividendYield") is not None else None
        item["per"] = _arrondi(fv.get("trailingPE")) if fv.get("trailingPE") is not None else None
        item["secteur"] = (a.fondamentaux or {}).get("secteur") or None if getattr(a, "fondamentaux", None) else None
        item["perf_an"] = _arrondi(float(d["Close"].iloc[-1] / d["Close"].iloc[-min(len(d), 253)] - 1)) if len(d) > 200 else None
        titres.append(item)

    indices = []
    for t, nom in INDICES:
        d = indices_bruts.get(t)
        if d is None or len(d) < 2:
            continue
        c = d["Close"]
        indices.append({"ticker": t, "nom": nom, "prix": float(c.iloc[-1]),
                        "var_jour": float(c.iloc[-1] / c.iloc[-2] - 1),
                        "devise": "€" if t in ("^FCHI", "^STOXX50E") else "$",
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
    suivi = dict(suivi or {})
    resultats = suivi.pop("toutes", [])
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
        "stats": bool(config.GOATCOUNTER) and not demo,
        "qualite": None if not qualite else {
            "resume": qualite["resume"],
            "a_verifier": [{"ticker": t, "problemes": v["problemes"]} for t, v in qualite["details"].items() if not v["ok"]],
            "demo": demo},
        "telegram": config.TELEGRAM_CHAINE.lstrip("@") if config.TELEGRAM_CHAINE else "",
        "fondamentaux_libelles": fondamentaux.libelles(),
        "resultats": resultats,   # liste complète des prédictions vérifiées (page « résultats » seulement)
        "elargissement_resultats": fondamentaux.ELARGISSEMENT_RESULTATS,
        "entrainement": _dernier_entrainement(),
    })


def _json_sur(payload: dict) -> str:
    """JSON insérable sans risque dans une balise <script>."""
    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return (s.replace("</", "<\\/").replace("<!--", "<\\!--")
             .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


CHAMPS_DETAIL = ("serie", "rendements", "cone", "chandeliers", "backtest", "niveaux", "actus",
                 "fondamentaux", "raisons_pour", "raisons_contre", "raisons_ia")
TOUJOURS_COMPLETS = {"^FCHI"}  # premier graphique de l'accueil : affiché tout de suite (les autres sont chargés au clic)


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
    pour_page = {k: v for k, v in payload.items() if k != "resultats"}
    # jeu « Remonte le temps » : fichier à part en ligne (chargé seulement si on joue), intégré sinon
    try:
        with open(os.path.join(config.DOSSIER_HISTORIQUE, "jeu_temps.json"), encoding="utf-8") as f:
            jeu_temps = json.load(f).get("items") or []
    except (OSError, ValueError, AttributeError):
        jeu_temps = []
    if jeu_temps:
        if decouper:
            os.makedirs(dossier, exist_ok=True)
            with open(os.path.join(dossier, "jeu_temps.json"), "w", encoding="utf-8") as f:
                json.dump(jeu_temps, f, ensure_ascii=False, separators=(",", ":"))
            pour_page["jeu_temps"] = "jeu_temps.json"
        else:
            pour_page["jeu_temps"] = jeu_temps[:80]
    page = gabarit.replace("/*__DATA__*/null", _json_sur(_decouper(pour_page, dossier) if decouper else pour_page))
    tete, corps = page.split("<!--__CORPS__-->", 1)
    corps = corps.replace("<!--__FAQ__-->", seo.html_faq(), 1)
    if pour_artifact:  # aperçu Claude : bibliothèque depuis un CDN autorisé, pas de CSP propre
        lib = '<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>'
        html = tete.replace("<!--__LIB__-->", lib) + corps
    else:              # vrai site : tout est servi par le site lui-même
        lib = '<script src="lightweight-charts.js"></script>'
        # balises de référencement complètes à la place des balises minimales de l'aperçu
        debut, fin = tete.index("<!--META-->"), tete.index("<!--/META-->") + len("<!--/META-->")
        tete = (tete[:debut] + seo.balises_tete(seo.url_site(), seo.TITRE_ACCUEIL,
                                                 seo.DESCRIPTION, "", jsonld=seo.jsonld_accueil(),
                                                 alternates={"fr": "", "en": "en/index.html", "x-default": ""}) + tete[fin:])
        faq = json.dumps(seo.jsonld_faq(), ensure_ascii=False).replace("</", "<\\/")
        tete = tete.replace("<!--__LIB__-->", f'<script type="application/ld+json">{faq}</script>\n<!--__LIB__-->', 1)
        tete = tete.replace("<title>Radar Bourse</title>",
                            f"<title>{seo.TITRE_ACCUEIL}</title>", 1)
        corps = corps.replace("<!--__LIENS_SEO__-->", seo.liens_accueil(payload), 1)
        securite = (f'<meta http-equiv="Content-Security-Policy" content="{seo.csp_avec_stats(CSP)}">\n'
                    '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
                    + seo.script_stats() + "\n")
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
        cname = os.path.join(dossier, "CNAME")
        if config.DOMAINE:
            with open(cname, "w", encoding="utf-8") as f:
                f.write(config.DOMAINE + "\n")
        elif os.path.exists(cname):
            os.remove(cname)
        ancien = os.path.join(dossier, "donnees.json")
        if os.path.exists(ancien):
            os.remove(ancien)
    return chemin
