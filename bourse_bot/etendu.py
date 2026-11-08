"""Version 67 : plus de 2 000 actions supplémentaires parmi les plus connues du monde (fiches simples).

Ces titres ne passent PAS par l'IA principale : ses performances ne bougent donc pas (elle reste mesurée sur les
titres qu'elle connaît). Leurs fiches donnent des faits vérifiables : cours, graphique, performances, tendance de fond,
agitation habituelle et la fourchette réellement observée sur deux ans. Elles le disent clairement.

Les cours sont téléchargés une fois par jour (le soir) et gardés dans .cache_etendu ; les mises à jour horaires
réécrivent les pages à partir de ce cache, sans rien retélécharger.
"""
from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime

from . import config, data

DOSSIER = ".cache_etendu"
FICHIER = os.path.join(DOSSIER, "etendu.json")
FICHIER_OHLC = os.path.join(DOSSIER, "cours.pkl")
FICHIER_PRED = os.path.join(DOSSIER, "avis_ia.json")
_OHLC: dict = {}
LISTE = os.path.join(os.path.dirname(__file__), "etendu_liste.json")

PAYS = {  # suffixe Yahoo -> (pays FR, pays EN, devise)
    "": ("États-Unis", "United States", "$"), "T": ("Japon", "Japan", "¥"), "L": ("Royaume-Uni", "United Kingdom", "£"),
    "HK": ("Hong Kong", "Hong Kong", "HK$"), "DE": ("Allemagne", "Germany", "€"), "NS": ("Inde", "India", "₹"),
    "SW": ("Suisse", "Switzerland", "CHF"), "ST": ("Suède", "Sweden", "SEK"), "TO": ("Canada", "Canada", "C$"),
    "KS": ("Corée du Sud", "South Korea", "₩"), "TW": ("Taïwan", "Taiwan", "NT$"), "OL": ("Norvège", "Norway", "NOK"),
    "MI": ("Italie", "Italy", "€"), "PA": ("France", "France", "€"), "MC": ("Espagne", "Spain", "€"),
    "AX": ("Australie", "Australia", "A$"), "CO": ("Danemark", "Denmark", "DKK"), "AS": ("Pays-Bas", "Netherlands", "€"),
    "HE": ("Finlande", "Finland", "€"), "BR": ("Belgique", "Belgium", "€"), "VI": ("Autriche", "Austria", "€"),
    "SI": ("Singapour", "Singapore", "S$"), "LS": ("Portugal", "Portugal", "€"), "IR": ("Irlande", "Ireland", "€"),
}
SECTEURS = {"Information Technology": ("technologie", "technology"), "Financials": ("finance", "financials"),
            "Health Care": ("santé", "health care"), "Consumer Discretionary": ("consommation (hors besoins de base)", "consumer discretionary"),
            "Consumer Staples": ("consommation de base", "consumer staples"), "Industrials": ("industrie", "industrials"),
            "Energy": ("énergie", "energy"), "Utilities": ("services publics", "utilities"), "Materials": ("matériaux", "materials"),
            "Real Estate": ("immobilier", "real estate"), "Communication Services": ("communication", "communication services")}


def suffixe(tk: str) -> str:
    return tk.rsplit(".", 1)[1] if "." in tk else ""


def pays(tk: str, fr: bool = True) -> str:
    p = PAYS.get(suffixe(tk), PAYS[""])
    return p[0] if fr else p[1]


def liste() -> dict:
    try:
        with open(LISTE, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return {}
    principaux = {t for u in config.UNIVERS.values() for t in u}
    return {k: v for k, v in d.items() if k not in principaux}


# ----------------------------------------------------------------------------
# Calcul (faits seulement, sur deux ans de cours quotidiens)
# ----------------------------------------------------------------------------
def _stats(close, dates) -> dict | None:
    c = [float(x) for x in close if x is not None and x == x and x > 0]
    if len(c) < 260 or len(c) != len(close):
        return None
    r = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]

    def ecart(seg):
        m = sum(seg) / len(seg)
        return math.sqrt(sum((x - m) ** 2 for x in seg) / (len(seg) - 1)) * math.sqrt(252)

    vols = [ecart(r[i - 20:i]) for i in range(20, len(r) + 1)]
    vols_an = sorted(vols[-252:])
    perf = lambda n: (c[-1] / c[-1 - n] - 1) if len(c) > n else None
    mois = sorted(c[i + 20] / c[i] - 1 for i in range(len(c) - 20))
    q = lambda p: mois[min(len(mois) - 1, max(0, int(p * (len(mois) - 1))))]
    an = c[-252:]
    pic, dd = an[0], 0.0
    for v in an:
        pic = max(pic, v)
        dd = min(dd, v / pic - 1)
    sma = lambda n: sum(c[-n:]) / n
    debut_an = next((i for i, d in enumerate(dates) if d[:4] == dates[-1][:4]), None)
    return {
        "prix": c[-1], "date": dates[-1],
        "perf": {"1j": perf(1), "1s": perf(5), "1m": perf(21), "3m": perf(63), "1a": perf(252),
                 "ytd": (c[-1] / c[debut_an - 1] - 1) if debut_an and debut_an > 0 else None},
        "vol": vols[-1], "vol_normale": vols_an[len(vols_an) // 2],
        "haut": max(an), "bas": min(an), "dd": dd,
        "sma50": sma(50), "sma200": sma(200),
        "f10": q(0.10), "f90": q(0.90), "pire": mois[0], "meilleur": mois[-1],
        "serie": {"t": dates[-130:], "c": [round(v, 6) for v in c[-130:]]},
    }


def _telecharger(tickers: list) -> dict:
    """{ticker: (closes, dates)} sur deux ans, par paquets (Yahoo), sans planter si un titre manque."""
    out = {}
    global _OHLC
    _OHLC = {}
    if data.DEMO:
        for t in tickers:
            df = data.cours_synthetiques(t, 520)
            out[t] = (list(df["Close"]), [d.strftime("%Y-%m-%d") for d in df.index])
            _OHLC[t] = df
        return out
    import contextlib
    import io
    import yfinance as yf
    debut = time.time()
    for i in range(0, len(tickers), 150):
        if time.time() - debut > 15 * 60:   # garde-fou : jamais plus de 15 minutes (la suite attendra le lendemain)
            print(f"Fiches simples : téléchargement arrêté après 15 min ({len(out)} titres reçus).")
            break
        paquet = tickers[i:i + 150]
        for essai in range(2):
            try:
                data._silencieux()   # coupe les messages de yfinance (ce n'est pas un « with » : correction v67.3)
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    brut = yf.download(paquet, period="2y", interval="1d", auto_adjust=True, group_by="ticker",
                                       threads=True, progress=False, timeout=30)
                break
            except Exception:
                brut = None
                time.sleep(5)
        if brut is None or brut.empty:
            continue
        for t in paquet:
            try:
                df = (brut[t] if len(paquet) > 1 else brut)[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])
            except Exception:
                continue
            if len(df) >= 260:
                if suffixe(t) == "L":   # Londres : cours en pence -> livres
                    df = df.copy()
                    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]] / 100.0
                s = df["Close"]
                out[t] = (list(s.to_numpy()), [d.strftime("%Y-%m-%d") for d in s.index])
                _OHLC[t] = df.astype("float32")
    return out


_MEMO: dict | None = None


def charger(forcer: bool = False) -> dict:
    """Les fiches simples : relues du cache (moins de 20 h), sinon recalculées (une seule fois par lancement)."""
    global _MEMO
    if _MEMO is not None and not forcer:
        return _MEMO
    _MEMO = _charger(forcer)
    return _MEMO


def _charger(forcer: bool = False) -> dict:
    if os.environ.get("RADAR_ETENDU", "1") == "0":
        return {}
    L = liste()
    if not L:
        return {}
    try:
        if not forcer and not data.DEMO and time.time() - os.path.getmtime(FICHIER) < 20 * 3600:
            with open(FICHIER, encoding="utf-8") as f:
                d = json.load(f)
            return {k: v for k, v in d.items() if k in L}
    except Exception:
        pass
    bruts = _telecharger(sorted(L))
    res = {}
    for t, (c, dts) in bruts.items():
        st = _stats(c, dts)
        if st:
            nom, sec = L[t]
            st.update({"ticker": t, "nom": nom, "secteur": sec})
            res[t] = st
    if res and not data.DEMO:
        try:   # téléchargement partiel : on complète avec le calcul précédent plutôt que de perdre des fiches
            with open(FICHIER, encoding="utf-8") as f:
                ancien = json.load(f)
            for k, v in ancien.items():
                if k in L and k not in res:
                    res[k] = v
        except Exception:
            pass
        os.makedirs(DOSSIER, exist_ok=True)
        with open(FICHIER, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, separators=(",", ":"))
        try:   # les cours complets (pour l'avis de l'IA), gardés jusqu'au prochain téléchargement
            import pickle
            with open(FICHIER_OHLC, "wb") as f:
                pickle.dump(_OHLC, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass
    elif not res and os.path.exists(FICHIER):   # Yahoo muet : on garde l'ancien calcul plutôt que rien
        try:
            with open(FICHIER, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return res


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
_MODELE: dict = {}


def _rc_ia(t, fr, px):
    """L'avis de l'IA du site (calculé une fois par jour) en haut de la fiche simple."""
    ia = t.get("ia")
    if not ia or ia.get("p") is None:
        return ""
    from .hebdo import reponse_courte_html
    mv = ia["v"] / math.sqrt(252) * math.sqrt(20) if ia.get("v") else t["vol"] / math.sqrt(252) * math.sqrt(20)
    t2 = {"proba_hausse": ia["p"], "avis_net": False if ia.get("c") == "faible" else True, "confiance": "moyenne",
          "risque_prevu": {"mouvement": mv}, "devise": _devise(t)}
    note = ("<p class='muted' style='font-size:14px;margin-top:-4px'>Avis calculé une fois par jour par l'IA du radar, "
            "à partir des mêmes indicateurs que pour les titres qu'elle suit en continu.</p>" if fr else
            "<p class='muted' style='font-size:14px;margin-top:-4px'>Call computed once a day by the radar's AI, from the same "
            "indicators as for the assets it follows continuously.</p>")
    return reponse_courte_html(t2, _MODELE, fr, px) + note


def _devise(t):
    return PAYS.get(suffixe(t["ticker"]), PAYS[""])[2]


def _fleche(t):
    p = (t.get("ia") or {}).get("p")
    if p is None:
        return ""
    return (f" <span class='{'up' if p >= .5 else 'down'}' title='{round(p * 100)} / 100' aria-label='{round(p * 100)} / 100'>"
            f"{'↑' if p >= .5 else '↓'}</span>")


def _sym(tk):
    return tk.split(".")[0]


def _rangs(t, groupe):
    """Version 67 : place du titre parmi les actions du même pays (une information propre à chaque fiche)."""
    perfs = [x["perf"].get("1a") for x in groupe if x["perf"].get("1a") is not None]
    vols = [x["vol"] for x in groupe if x.get("vol")]
    p, v = t["perf"].get("1a"), t.get("vol")
    rp = sum(1 for x in perfs if x < p) / len(perfs) if p is not None and len(perfs) >= 8 else None
    rv = sum(1 for x in vols if x < v) / len(vols) if v and len(vols) >= 8 else None
    return rp, rv, len(groupe)


def _page_fr(seo, base, t, csp, voisins, date, rangs=(None, None, 0)):
    e, px, pct = seo._e, seo._px, seo._pct
    from .hebdo import barres
    nom, tk, dev = t["nom"], t["ticker"], _devise(t)
    sym = _sym(tk)
    P = t["perf"]
    au200 = t["prix"] > t["sma200"]
    au50 = t["prix"] > t["sma50"]
    tend = ("en hausse" if au200 and au50 else "en baisse" if not au200 and not au50 else "hésitante")
    tend_txt = (f"Le cours est {'au-dessus' if au200 else 'en dessous'} de sa moyenne des 200 dernières séances "
                f"et {'au-dessus' if au50 else 'en dessous'} de celle des 50 dernières : sa tendance de fond est <b>{tend}</b>.")
    mvt = t["vol"] / math.sqrt(252) * math.sqrt(20)
    agite = t["vol"] / t["vol_normale"] if t["vol_normale"] else 1
    agi_txt = ("plus agité que d'habitude" if agite > 1.25 else "plus calme que d'habitude" if agite < 0.8 else "agité comme d'habitude")
    pays_fr = pays(tk)
    sec = (SECTEURS.get(t.get("secteur") or "") or (None, None))[0]
    cls = "rc-up" if tend == "en hausse" else "rc-down" if tend == "en baisse" else "rc-nul"
    ic = "↑" if tend == "en hausse" else "↓" if tend == "en baisse" else "↔"
    rc = (f"<div class='carte rc {cls}'><div class='rc-l'>La réponse courte</div>"
          f"<div class='rc-q rc-q1'><span class='rc-ic' aria-hidden='true'>{ic}</span><div><span class='rc-k'>Tendance actuelle (un fait, pas une prévision)</span>"
          f"<b>{tend[:1].upper() + tend[1:]}</b></div></div>"
          f"<p class='rc-t'>{tend_txt} Sur 3 mois : {pct(P.get('3m'))}. "
          f"<span class='muted'>L'IA du radar ne donne pas encore d'avis sur ce titre : personne ne peut dire de façon fiable "
          f"s'il montera le mois prochain. Les titres que l'IA analyse ont une <a href='../titres.html'>fiche complète</a>.</span></p>"
          f"<div class='rc-q rc-q2'><span class='rc-ic' aria-hidden='true'>↕</span><div><span class='rc-k'>De combien ça bouge d'habitude ?</span>"
          f"<b>±{round(mvt * 100)} % en un mois</b><span class='rc-s'>Sur deux ans, 8 mois sur 10, entre {pct(t['f10'], 0)} et {pct(t['f90'], 0)}</span></div></div></div>")
    courbe = seo.courbe_svg({"serie": t["serie"]}, {"prevision": "", "cours": "cours des 6 derniers mois", "bien": "", "probable": "",
                                                     "mal": "", "moitie": "", "aria": f"Graphique : cours de {nom} sur six mois"})
    graph = barres([("Depuis 1 semaine", P.get("1s")), ("Depuis 1 mois", P.get("1m")), ("Depuis 3 mois", P.get("3m")),
                    ("Depuis le 1er janvier", P.get("ytd")), ("Depuis 1 an", P.get("1a"))], titre=f"{e(nom)} : évolution du cours")
    lignes = [("Dernier cours", f"{px(t['prix'], dev)} <span class='muted'>({e(seo.date_longue(t['date']))})</span>"),
              ("Variation du jour", pct(P.get("1j"), 2)),
              ("Plus haut sur un an", px(t["haut"], dev)), ("Plus bas sur un an", px(t["bas"], dev)),
              ("Pire baisse depuis un sommet (1 an)", pct(t["dd"])),
              ("Agitation (20 dernières séances)", f"{round(t['vol'] * 100)} % par an, {agi_txt}"),
              ("Meilleur mois / pire mois (2 ans)", f"{pct(t['meilleur'])} / {pct(t['pire'])}"),
              ("Pays", e(pays_fr))] + ([("Secteur", e(sec))] if sec else [])
    table = "".join(f"<tr><th scope='row'>{a}</th><td class='m'>{b}</td></tr>" for a, b in lignes)
    faq = [(f"Quel est le cours de l'action {nom} ?",
            f"Le dernier cours de {nom} ({sym}) est de {px(t['prix'], dev)} ({seo.date_longue(t['date'])}), "
            f"soit {('+' if (P.get('1a') or 0) >= 0 else '')}{round((P.get('1a') or 0) * 100)} % sur un an."),
           (f"L'action {nom} va-t-elle monter ?",
            ((f"Selon l'IA du radar, {nom} est {'plutôt' if t['ia'].get('c') != 'faible' else 'légèrement'} "
              f"{'à la hausse' if t['ia']['p'] >= .5 else 'à la baisse'} pour le mois qui vient : {round(t['ia']['p'] * 100)} chances sur 100 "
              f"de finir plus haut (confiance {t['ia'].get('c', 'faible')}). ") if (t.get("ia") or {}).get("p") is not None else "")
            + f"Sa tendance de fond est {tend}, et sur deux ans elle a bougé "
            f"8 mois sur 10 entre {round(t['f10'] * 100)} % et +{round(t['f90'] * 100)} % en un mois. Rien n'est sûr : ce n'est pas un conseil d'achat."),
           (f"L'action {nom} est-elle risquée ?",
            f"Son agitation récente est de {round(t['vol'] * 100)} % par an ({agi_txt}), et sa pire baisse depuis un sommet sur un an "
            f"est de {round(t['dd'] * 100)} %. Toute action peut perdre beaucoup de valeur.")]
    rp, rv, ng = rangs
    compare = ""
    if rp is not None and rv is not None:
        compare = (f"<h2>Face aux autres actions ({e(pays_fr)})</h2><p>Sur un an, {e(nom)} a fait mieux que <b>{round(rp * 100)} %</b> "
                   f"des {ng} actions de ce pays suivies par le radar, et son agitation récente est plus forte que celle de "
                   f"<b>{round(rv * 100)} %</b> d'entre elles : c'est une action {'plutôt agitée' if rv > .66 else 'plutôt calme' if rv < .33 else 'moyennement agitée'} "
                   f"pour son marché.</p>")
    faq_html = compare + "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq)
    voisins_html = ("<h2>Autres actions du même pays</h2><ul class='liste'>"
                    + "".join(f"<li><a href='{seo.slug(v['ticker'])}.html'>{e(v['nom'])}</a></li>" for v in voisins) + "</ul>") if voisins else ""
    corps = (f"<p class='muted'><a href='../toutes-les-actions.html'>Toutes les actions</a> · {e(pays_fr)}</p>"
             f"<h1>{e(nom)} ({e(sym)}) : cours de l'action et analyse</h1>"
             f"<p class='muted'>Cours au {e(seo.date_longue(t['date']))}, mis à jour chaque jour · fiche simple</p>"
             f"{_rc_ia(t, True, px) or rc}{courbe}{graph}<h2>Les chiffres clés</h2><div class='carte' style='overflow-x:auto' tabindex='0' role='region' "
             f"aria-label='Chiffres clés'><table class='kv'>{table}</table></div>{faq_html}{voisins_html}"
             "<p class='muted'>Fiche simple calculée automatiquement à partir des cours publics (Yahoo Finance). "
             "Les chiffres clés sont des faits passés ; l'avis de l'IA est une prévision, pas une certitude. Projet éducatif, pas un conseil en investissement. "
             "<a href='../credits.html'>Sources et crédits</a>.</p>")
    mois = seo.MOIS[datetime.now().month - 1]
    titre = f"Action {nom} ({sym}) : cours et analyse {mois} {datetime.now().year}"
    if len(titre) > 62:
        titre = next((x for x in (f"{nom} ({sym}) : cours et analyse", f"Action {nom} : cours", f"{nom} : cours") if len(x) <= 62),
                     f"{nom[:50]} : cours")
    desc = (f"Cours de l'action {nom} ({sym}) : {px(t['prix'], dev)} le {seo.date_longue(t['date'])}. "
            f"Sur un an {round((P.get('1a') or 0) * 100):+d} %, tendance {tend}, agitation habituelle ±{round(mvt * 100)} % par mois.")
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Toutes les actions", "item": (base + "toutes-les-actions.html") if base else None},
            {"@type": "ListItem", "position": 2, "name": nom}]}]}
    chemin = f"titres/{seo.slug(tk)}.html"
    t2 = dict(t, marche="etendu")
    return chemin, seo._page(base, titre, desc, chemin, corps, jsonld, csp,
                             alternates={"fr": chemin, "en": f"en/stocks/{seo.slug(tk)}.html", "x-default": chemin},
                             mots=seo.mots_titre(t2))


def _page_en(seo, anglais, base, t, csp, voisins):
    e, px, pct = seo._e, anglais._px, anglais._pct
    from .hebdo import barres
    nom, tk, dev = t["nom"], t["ticker"], _devise(t)
    sym = _sym(tk)
    P = t["perf"]
    au200, au50 = t["prix"] > t["sma200"], t["prix"] > t["sma50"]
    tend = "up" if au200 and au50 else "down" if not au200 and not au50 else "mixed"
    mvt = t["vol"] / math.sqrt(252) * math.sqrt(20)
    cls = {"up": "rc-up", "down": "rc-down"}.get(tend, "rc-nul")
    ic = {"up": "↑", "down": "↓"}.get(tend, "↔")
    rc = (f"<div class='carte rc {cls}'><div class='rc-l'>The short answer</div>"
          f"<div class='rc-q rc-q1'><span class='rc-ic' aria-hidden='true'>{ic}</span><div><span class='rc-k'>Current trend (a fact, not a forecast)</span>"
          f"<b>{'Trending up' if tend == 'up' else 'Trending down' if tend == 'down' else 'Mixed'}</b></div></div>"
          f"<p class='rc-t'>The price is {'above' if au200 else 'below'} its 200-session average and {'above' if au50 else 'below'} its 50-session "
          f"average. Over 3 months: {pct(P.get('3m'))}. <span class='muted'>The radar's AI does not give a call on this stock yet: nobody can reliably "
          f"say whether it will rise next month.</span></p>"
          f"<div class='rc-q rc-q2'><span class='rc-ic' aria-hidden='true'>↕</span><div><span class='rc-k'>How much does it usually move?</span>"
          f"<b>±{round(mvt * 100)}% in a month</b><span class='rc-s'>Over two years, 8 months in 10 between {pct(t['f10'], 0)} and {pct(t['f90'], 0)}</span></div></div></div>")
    courbe = seo.courbe_svg({"serie": t["serie"]}, {"prevision": "", "cours": "price over the last 6 months", "bien": "", "probable": "",
                                                     "mal": "", "moitie": "", "aria": f"Chart: {nom} price over six months"})
    fmt = lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v) * 100:.1f}%"
    graph = barres([("1 week", P.get("1s")), ("1 month", P.get("1m")), ("3 months", P.get("3m")), ("Year to date", P.get("ytd")),
                    ("1 year", P.get("1a"))], fmt=fmt, titre=f"{e(nom)}: price change")
    lignes = [("Last price", f"{px(t['prix'], dev)} <span class='muted'>({e(t['date'])})</span>"), ("Day change", pct(P.get("1j"), 2)),
              ("1-year high", px(t["haut"], dev)), ("1-year low", px(t["bas"], dev)), ("Max drawdown (1 year)", pct(t["dd"])),
              ("Volatility (last 20 sessions)", f"{round(t['vol'] * 100)}% a year"),
              ("Best / worst month (2 years)", f"{pct(t['meilleur'])} / {pct(t['pire'])}"), ("Country", e(pays(tk, False)))]
    sec = (SECTEURS.get(t.get("secteur") or "") or (None, None))[1]
    if sec:
        lignes.append(("Sector", e(sec)))
    table = "".join(f"<tr><th scope='row'>{a}</th><td class='m'>{b}</td></tr>" for a, b in lignes)
    voisins_html = ("<h2>Other stocks from the same country</h2><ul class='liste'>"
                    + "".join(f"<li><a href='{seo.slug(v['ticker'])}.html'>{e(v['nom'])}</a></li>" for v in voisins) + "</ul>") if voisins else ""
    corps = (f"<p class='muted'><a href='../all-stocks.html'>All stocks</a> · {e(pays(tk, False))}</p>"
             f"<h1>{e(nom)} ({e(sym)}): stock price and analysis</h1><p class='muted'>Price as of {e(t['date'])}, updated daily · simple page</p>"
             f"{_rc_ia(t, False, px) or rc}{courbe}{graph}<h2>Key figures</h2><div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='Key figures'>"
             f"<table class='kv'>{table}</table></div>{voisins_html}<p class='muted'>Simple page computed from public prices (Yahoo Finance). "
             "Key figures are past facts; the AI's call is a forecast, not a certainty. Educational project, not investment advice.</p>")
    chemin = f"en/stocks/{seo.slug(tk)}.html"
    desc = (f"{nom} ({sym}) stock price: {px(t['prix'], dev)} on {t['date']}. 1 year {round((P.get('1a') or 0) * 100):+d}%, "
            f"trend {tend}, usual move ±{round(mvt * 100)}% a month.")
    titre = next((x for x in (f"{nom} ({sym}) stock: price and analysis | {seo.NOM}", f"{nom} ({sym}) stock: price and analysis",
                              f"{nom} ({sym}) stock price", f"{nom} stock price") if len(x) <= 62), f"{nom[:50]} stock price")
    return chemin, anglais._page(base, titre, desc, chemin, corps, csp,
                                 {"fr": f"titres/{seo.slug(tk)}.html", "en": chemin, "x-default": f"titres/{seo.slug(tk)}.html"},
                                 mots=seo.mots_titre(dict(t, marche="etendu"), "en"))


def generer(seo, anglais, base, dossier, csp, date) -> list:
    E = charger()
    if not E:
        return []
    pris = {seo.slug(t) for u in config.UNIVERS.values() for t in u}
    E = {k: v for k, v in E.items() if seo.slug(k) not in pris}
    os.makedirs(os.path.join(dossier, "titres"), exist_ok=True)
    os.makedirs(os.path.join(dossier, "en", "stocks"), exist_ok=True)
    par_pays = {}
    for t in E.values():
        par_pays.setdefault(suffixe(t["ticker"]), []).append(t)
    for v in par_pays.values():
        v.sort(key=lambda t: t["nom"].lower())
    urls = []
    for t in E.values():
        tk = t["ticker"]
        if seo.slug(tk) in pris:   # une fiche complète existe déjà sous ce nom : jamais d'écrasement
            continue
        groupe = par_pays.get(suffixe(tk), [])
        i = groupe.index(t)
        voisins = [groupe[(i + d) % len(groupe)] for d in (1, 2, 3, 4, 5, -1) if len(groupe) > 6]
        try:
            chemin, page = _page_fr(seo, base, t, csp, voisins, date, _rangs(t, groupe))
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.5"))
            chemin, page = _page_en(seo, anglais, base, t, csp, voisins)
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.4"))
        except Exception as ex:
            print(f"Fiche simple {tk} non générée : {ex}")
    # Index : toutes les actions, par pays
    e = seo._e
    ordre = sorted(par_pays, key=lambda s: -len(par_pays[s]))
    corps = ("<h1>Toutes les actions : cours et analyse</h1>"
             f"<p>{len(E)} actions parmi les plus connues du monde, en plus des titres analysés par l'IA "
             "(<a href='titres.html'>fiches complètes</a>). Chaque fiche simple donne le cours, le graphique, la tendance et l'agitation habituelle.</p>"
             "<p>" + " · ".join(f"<a href='#p-{s or 'us'}'>{e(PAYS[s][0])} ({len(par_pays[s])})</a>" for s in ordre) + "</p>")
    corps_en = ("<h1>All stocks: prices and analysis</h1>"
                f"<p>{len(E)} of the world's best-known stocks, on top of the assets analysed by the AI.</p>"
                "<p>" + " · ".join(f"<a href='#p-{s or 'us'}'>{e(PAYS[s][1])} ({len(par_pays[s])})</a>" for s in ordre) + "</p>")
    for s in ordre:
        corps += (f"<h2 id='p-{s or 'us'}'>{e(PAYS[s][0])}</h2><ul class='liste'>"
                  + "".join(f"<li><a href='titres/{seo.slug(t['ticker'])}.html'>{e(t['nom'])}</a>{_fleche(t)}</li>" for t in par_pays[s]) + "</ul>")
        corps_en += (f"<h2 id='p-{s or 'us'}'>{e(PAYS[s][1])}</h2><ul class='liste'>"
                     + "".join(f"<li><a href='stocks/{seo.slug(t['ticker'])}.html'>{e(t['nom'])}</a>{_fleche(t)}</li>" for t in par_pays[s]) + "</ul>")
    alt = {"fr": "toutes-les-actions.html", "en": "en/all-stocks.html", "x-default": "toutes-les-actions.html"}
    with open(os.path.join(dossier, "toutes-les-actions.html"), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Toutes les actions du monde : cours et analyse | {seo.NOM}",
                          f"{len(E)} actions parmi les plus connues (États-Unis, Europe, Japon, Chine, Inde…) : cours, graphique, tendance et agitation, mis à jour chaque jour.",
                          "toutes-les-actions.html", corps, csp=csp, alternates=alt))
    with open(os.path.join(dossier, "en", "all-stocks.html"), "w", encoding="utf-8") as f:
        f.write(anglais._page(base, f"All stocks: prices and analysis | {seo.NOM}",
                              f"{len(E)} of the best-known stocks worldwide: price, chart, trend and volatility, updated daily.",
                              "en/all-stocks.html", corps_en, csp, alt))
    urls += [("toutes-les-actions.html", "daily", "0.7"), ("en/all-stocks.html", "daily", "0.5")]
    # Recherche : la liste légère, chargée seulement quand on tape dans la barre de recherche
    with open(os.path.join(dossier, "recherche-etendue.json"), "w", encoding="utf-8") as f:
        json.dump([[t["nom"], t["ticker"], seo.slug(t["ticker"]), pays(t["ticker"]),
                    (1 if t["ia"]["p"] >= .5 else -1) if (t.get("ia") or {}).get("p") is not None else 0,
                    (t.get("ia") or {}).get("c", "")] for t in sorted(E.values(), key=lambda t: t["nom"].lower())],
                  f, ensure_ascii=False, separators=(",", ":"))
    return urls


def nombre() -> int:
    """Nombre de fiches simples réellement disponibles (lu dans le cache, sans rien télécharger)."""
    try:
        with open(FICHIER, encoding="utf-8") as f:
            return len(json.load(f))
    except Exception:
        return 0


# ----------------------------------------------------------------------------
# Version 67.5 : l'avis de l'IA du site pour chaque fiche simple (calculé une fois par jour)
# ----------------------------------------------------------------------------
REFERENCE = {"us": "SPY", "eu": "^STOXX50E", "monde": "VEU"}
EU_SUF = ("DE", "PA", "AS", "MC", "MI", "SW", "L", "ST", "BR", "HE", "CO", "OL", "VI", "LS", "IR")


def _marche(tk):
    sx = suffixe(tk)
    return "us" if not sx else "eu" if sx in EU_SUF else "monde"


def _ligne(t, brut, bench, ctx):
    """Indicateurs du dernier jour d'une fiche simple (fonction de haut niveau : calcul en parallèle)."""
    try:
        return _ligne_calc(t, brut, bench, ctx)
    except Exception:
        return None


def _ligne_calc(t, brut, bench, ctx):
    from . import indicators, model
    d = indicators.calculer(brut.astype("float64"), bench, ctx)
    cols = [c for c in model.FEATURES if c in d.columns]
    ligne = d[cols].iloc[[-1]].copy()
    n = d[["vol_20j"]].iloc[-260:].copy()
    model.ajouter_normale(n)
    ligne["vol_normale"] = float(n["vol_normale"].iloc[-1])
    ligne["vol_normale_60"] = float(n["vol_normale_60"].iloc[-1])
    ligne["ticker"] = t
    return ligne


def predire(bruts_site: dict, marge: float = 0.02, modele: dict | None = None) -> dict:
    """Ajoute à chaque fiche simple l'avis de l'IA du site (proba de hausse à un mois, agitation prévue).
    Une fois par jour : le résultat est gardé dans .cache_etendu/avis_ia.json pour les mises à jour horaires."""
    global _MODELE
    _MODELE = dict(modele or {})
    _MODELE.setdefault("avis_net", {"marge": marge})
    E = charger()
    if not E:
        return {}
    jour = datetime.now().strftime("%Y-%m-%d")
    preds = None
    if not data.DEMO:
        try:
            with open(FICHIER_PRED, encoding="utf-8") as f:
                c = json.load(f)
            if c.get("jour") == jour:
                preds = c.get("avis") or {}
        except Exception:
            preds = None
    if preds is None:
        global _OHLC
        if not _OHLC:
            try:
                import pickle
                with open(FICHIER_OHLC, "rb") as f:
                    _OHLC = pickle.load(f)
            except Exception:
                _OHLC = {}
        ctx = {k: v for k, v in (bruts_site.get("__macro__") or {}).items() if k != "fng"}
        travaux = [(t, df, bruts_site.get(REFERENCE[_marche(t)]), ctx) for t, df in _OHLC.items() if t in E]
        lignes = []
        n = min(4, os.cpu_count() or 1)
        try:
            if n > 1 and os.environ.get("RADAR_PARALLELE", "1") != "0":
                from concurrent.futures import ProcessPoolExecutor
                with ProcessPoolExecutor(n) as ex:
                    for r in ex.map(_ligne, *zip(*travaux), chunksize=16):
                        if r is not None:
                            lignes.append(r)
            else:
                raise RuntimeError
        except Exception:
            lignes = []
            for tr in travaux:
                r = _ligne(*tr)
                if r is not None:
                    lignes.append(r)
        from . import model
        brut = model.predire_autres(lignes) if lignes else {}
        preds = {}
        for t, r in brut.items():
            p = r["proba"]
            preds[t] = {"p": round(p, 4), "c": "moyenne" if abs(p - .5) >= marge else "faible"}
            if r.get("vol"):
                preds[t]["v"] = round(r["vol"], 4)
        if preds and not data.DEMO:
            try:
                os.makedirs(DOSSIER, exist_ok=True)
                with open(FICHIER_PRED, "w", encoding="utf-8") as f:
                    json.dump({"jour": jour, "avis": preds}, f, separators=(",", ":"))
            except Exception:
                pass
    for t, r in preds.items():
        if t in E:
            E[t]["ia"] = r
    return preds
