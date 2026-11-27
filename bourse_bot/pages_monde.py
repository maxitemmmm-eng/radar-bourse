"""Version 103 : trois pages demandées, construites uniquement avec les vrais chiffres du radar (rien d'inventé).

- top-10-actions.html : le top 10 des actions que l'IA voit le plus à la hausse (avis net seulement), les plus fortes
  hausses et baisses du mois (« les mouvements qui intéressent les gens ») et les avis « très sûrs » du moment ;
- grandes-bourses.html : les 10 grandes Bourses du monde, analysées une par une (tendance, élan, avis de l'IA,
  agitation prévue, risque de chute) ;
- prevision-or.html : l'or, en priorité (cours, avis de l'IA, fourchette, agitation, or « papier » ou or en crypto).
"""
from __future__ import annotations

import os

from . import seo

NOM = seo.NOM
_e = seo._e

# Les 10 plus grandes places boursières du monde (capitalisation), et le titre qui les suit sur le radar
BOURSES = [
    ("États-Unis : New York (NYSE)", "SPY", "Le S&P 500 : les 500 plus grandes entreprises américaines. La première Bourse du monde, de loin."),
    ("États-Unis : Nasdaq", "QQQ", "Le Nasdaq 100 : la tech américaine (Apple, Microsoft, Nvidia…). Plus agité que le S&P 500."),
    ("Chine : Shanghai et Shenzhen", "ASHR", "Les 300 plus grandes actions chinoises cotées en Chine continentale (indice CSI 300)."),
    ("Japon : Tokyo", "EWJ", "Les grandes entreprises japonaises (Toyota, Sony…), suivies en dollars."),
    ("Inde : Bombay (NSE)", "INDA", "Les grandes entreprises indiennes : un marché en forte croissance, souvent agité."),
    ("Hong Kong", "EWH", "La place de Hong Kong, porte d'entrée vers la Chine pour les investisseurs étrangers."),
    ("Europe : Paris (Euronext)", "^FCHI", "Le CAC 40 : les 40 grandes valeurs françaises, en points (indice)."),
    ("Royaume-Uni : Londres", "EWU", "Les grandes entreprises britanniques (banques, énergie, mines), suivies en dollars."),
    ("Canada : Toronto", "EWC", "Les grandes entreprises canadiennes (banques, énergie, matières premières), suivies en dollars."),
    ("Allemagne : Francfort", "EWG", "Les grandes entreprises allemandes (SAP, Siemens…), suivies en dollars."),
    ("Taïwan", "EWT", "Les grandes entreprises taïwanaises, dominées par TSMC (puces électroniques)."),
    ("Corée du Sud : Séoul", "EWY", "Les grandes entreprises coréennes, dominées par Samsung."),
]

CSS = """<style>
.pm-grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px;margin:14px 0}
.pm-carte{border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:var(--surface)}
.pm-carte h3{margin:0 0 4px;font-size:17px}.pm-carte p{margin:6px 0}
.pm-chiffres{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:10px 0}
.pm-chiffres div{background:var(--surface-2);border-radius:9px;padding:6px 8px}
.pm-chiffres b{display:block;font-family:var(--m);font-size:15px}.pm-chiffres span{font-size:12px;color:var(--muted)}
.pm-verdict{font-weight:600}.pm-verdict.up{color:var(--up)}.pm-verdict.down{color:var(--down)}
.pm-table{width:100%;border-collapse:collapse}.pm-table td,.pm-table th{padding:8px 6px;border-bottom:1px solid var(--line);text-align:left}
.pm-table td.m{font-family:var(--m);white-space:nowrap}.pm-rang{font-family:var(--m);color:var(--muted);width:2em}
.pm-onglets{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.pm-onglets a{border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none;font-size:14px}
</style>"""


def _avis(t):
    try:
        from .hebdo import avis_ia
        p, sens, conf = avis_ia(t)
    except Exception:
        return None, 0, "faible"
    return p, sens, conf


def _phrase_avis(t):
    p, sens, conf = _avis(t)
    if p is None:
        return "<span class='muted'>pas d'avis</span>", 0
    ch = round((p if sens > 0 else 1 - p) * 100)
    cls = "up" if sens > 0 else "down"
    return (f"<span class='pm-verdict {cls}'>{'hausse' if sens > 0 else 'baisse'} · {ch} chances sur 100</span>"
            f" <span class='muted'>(confiance {conf})</span>"), sens


def _mini(t):
    """Mini-courbe (sparkline) en SVG, à partir des derniers cours."""
    sp = [v for v in (t.get("spark") or []) if isinstance(v, (int, float))]
    if len(sp) < 5:
        return ""
    lo, hi = min(sp), max(sp)
    hi = hi if hi > lo else lo + 1
    pts = " ".join(f"{i * 100 / (len(sp) - 1):.1f},{28 - (v - lo) / (hi - lo) * 26:.1f}" for i, v in enumerate(sp))
    c = "var(--up)" if sp[-1] >= sp[0] else "var(--down)"
    return (f"<svg viewBox='0 0 100 30' preserveAspectRatio='none' style='width:100%;height:34px;display:block' aria-hidden='true'>"
            f"<polyline points='{pts}' fill='none' stroke='{c}' stroke-width='1.6' vector-effect='non-scaling-stroke'/></svg>")


def _analyse(t):
    """Quelques phrases tirées uniquement des chiffres du titre (tendance, élan, agitation, risque, avis)."""
    perf, rp = t.get("perf") or {}, t.get("risque_prevu") or {}
    out = []
    m1, m3 = perf.get("1 mois"), perf.get("3 mois")
    if t.get("au_dessus_200") is True:
        out.append("Tendance de fond <b>haussière</b> (cours au-dessus de sa moyenne 200 jours).")
    elif t.get("au_dessus_200") is False:
        out.append("Tendance de fond <b>baissière</b> (cours sous sa moyenne 200 jours).")
    if isinstance(m1, (int, float)) and isinstance(m3, (int, float)):
        if m1 > 0 and m3 > 0:
            out.append(f"Élan positif : {seo._pct(m1)} sur un mois, {seo._pct(m3)} sur trois mois.")
        elif m1 < 0 and m3 < 0:
            out.append(f"Élan négatif : {seo._pct(m1)} sur un mois, {seo._pct(m3)} sur trois mois.")
        else:
            out.append(f"Élan hésitant : {seo._pct(m1)} sur un mois, {seo._pct(m3)} sur trois mois.")
    if rp.get("tres_sur") or rp.get("sur"):
        plus = (rp.get("recent") or 1) > 1
        out.append(f"Avis {'très sûr' if rp.get('tres_sur') else 'sûr'} sur l'agitation : le mois prochain devrait être "
                   f"<b>plus {'agité' if plus else 'calme'}</b> que ces dernières semaines.")
    if isinstance(rp.get("chute"), (int, float)):
        out.append(f"Risque d'une chute de plus de 10 % dans le mois : <b>{round(rp['chute'] * 100)} %</b>.")
    return " ".join(out)


def _carte_titre(t, titre=None, texte=""):
    s = seo.slug(t["ticker"])
    perf, rp = t.get("perf") or {}, t.get("risque_prevu") or {}
    verdict, _ = _phrase_avis(t)
    mv = rp.get("mouvement")
    return (f"<article class='pm-carte'><h3><a href='titres/{s}.html'>{_e(titre or t.get('nom') or t['ticker'])}</a></h3>"
            + (f"<p class='muted' style='font-size:14px'>{_e(texte)}</p>" if texte else "")
            + f"<p>Avis de l'IA à un mois : {verdict}</p>{_mini(t)}"
            "<div class='pm-chiffres'>"
            f"<div><b>{seo._px(t.get('prix'), t.get('devise', ''))}</b><span>dernier cours</span></div>"
            f"<div><b>{seo._pct(perf.get('1 mois'))}</b><span>sur 1 mois</span></div>"
            f"<div><b>{'±' + str(round(mv * 100)) + ' %' if isinstance(mv, (int, float)) else '–'}</b><span>agitation prévue</span></div></div>"
            f"<p style='font-size:14.5px'>{_analyse(t)}</p>"
            f"<p style='margin-bottom:0;display:flex;gap:8px;flex-wrap:wrap;align-items:center'><a class='btn' style='font-size:14px;padding:7px 12px' "
            f"href='analyse-approfondie.html?t={__import__('urllib.parse', fromlist=['x']).quote(t['ticker'])}'>🔬 Réanalyser</a>"
            f"<a href='titres/{s}.html'>Fiche et graphique complet</a></p></article>")


def cartes_cryptos(payload, n=10):
    """Version 114 : les 10 grandes cryptos en cartes (mini-graphique 6 mois, avis, agitation, bouton Réanalyser)."""
    from . import config
    par_tk = {t["ticker"]: t for t in payload.get("titres", [])}
    ordre = ["BTC-USD", "ETH-USD", "XRP-USD", "BNB-USD", "SOL-USD", "DOGE-USD", "TRX-USD", "ADA-USD", "LINK-USD", "AVAX-USD",
             "XLM-USD", "SUI20947-USD", "BCH-USD", "HBAR-USD", "LTC-USD"]
    tks = [tk for tk in ordre if tk in par_tk][:n]
    if not tks:
        return ""
    return (CSS + "<h2>Les 10 grandes cryptos en graphiques</h2><div class='pm-grille'>"
            + "".join(_carte_titre(par_tk[tk], config.CRYPTOS.get(tk)) for tk in tks) + "</div>")


def _actions(payload):
    return [t for t in payload.get("titres", []) if t.get("marche") in ("fr", "eu", "us", "monde") and t.get("qualite_ok", True) is not False]


def _page_top(base, payload, csp):
    chemin = "top-10-actions.html"
    acts = _actions(payload)
    notes = []
    for t in acts:
        p, sens, conf = _avis(t)
        if p is not None and sens > 0 and conf != "faible":
            notes.append((p, t))
    notes.sort(key=lambda x: -x[0])
    top = [t for _, t in notes[:10]]
    perf1 = [t for t in acts if isinstance((t.get("perf") or {}).get("1 mois"), (int, float))]
    hausses = sorted(perf1, key=lambda t: -t["perf"]["1 mois"])[:10]
    baisses = sorted(perf1, key=lambda t: t["perf"]["1 mois"])[:10]
    tres = [t for t in payload.get("titres", []) if t.get("marche") != "tendances" and (t.get("risque_prevu") or {}).get("tres_sur")][:12]
    date = seo.date_longue(str(payload.get("date_donnees", ""))[:10]) if payload.get("date_donnees") else ""

    def ligne(i, t, col):
        s = seo.slug(t["ticker"])
        verdict, _ = _phrase_avis(t)
        return (f"<tr><td class='pm-rang'>{i}</td><td><a href='titres/{s}.html'><b>{_e(t.get('nom') or t['ticker'])}</b></a> "
                f"<span class='muted'>({_e(seo.aff_tk(t['ticker']))})</span><br><span style='font-size:14px'>{verdict}</span></td>"
                f"<td class='m'>{col(t)}</td></tr>")
    tab = lambda lst, col, tete: (f"<div class='carte' style='overflow-x:auto'><table class='pm-table'><thead><tr><th>#</th><th>Action</th><th>{tete}</th></tr></thead><tbody>"
                                  + "".join(ligne(i + 1, t, col) for i, t in enumerate(lst)) + "</tbody></table></div>")
    corps = (CSS + f"<h1>Top 10 des actions : ce que l'IA voit monter, et les mouvements du mois</h1>"
             f"<p class='muted'>Mis à jour automatiquement{(' · données au ' + _e(date)) if date else ''}. Classements calculés sur les {len(acts)} actions suivies.</p>"
             "<nav class='pm-onglets' aria-label='Sur cette page'><a href='#top-ia'>Top 10 de l'IA</a><a href='#hausses'>Plus fortes hausses</a>"
             "<a href='#baisses'>Plus fortes baisses</a><a href='#tres-surs'>Avis très sûrs</a></nav>"
             "<div class='carte'><b>À lire avant :</b> deviner si une action monte le mois prochain reste difficile, même pour l'IA "
             "(un peu mieux que le hasard). Ce classement est une information, <b>pas un conseil d'achat</b>. "
             "<a href='resultats.html'>Les vrais résultats de l'IA</a>.</div>"
             "<h2 id='top-ia'>Le top 10 des actions que l'IA voit le plus à la hausse</h2>"
             "<p>Seulement les avis nets (confiance moyenne ou forte), classés par chances de hausse à un mois.</p>"
             + (tab(top, lambda t: seo._pct((t.get('perf') or {}).get('1 mois')), "Sur 1 mois") if top else "<p class='muted'>Aucun avis assez net aujourd'hui : l'IA préfère ne rien classer.</p>")
             + "<h2 id='hausses'>Les 10 plus fortes hausses du mois</h2>"
             + tab(hausses, lambda t: f"<span class='up'>{seo._pct(t['perf']['1 mois'])}</span>", "Sur 1 mois")
             + "<h2 id='baisses'>Les 10 plus fortes baisses du mois</h2>"
             + tab(baisses, lambda t: f"<span class='down'>{seo._pct(t['perf']['1 mois'])}</span>", "Sur 1 mois")
             + "<h2 id='tres-surs'>Les avis « très sûrs » du moment</h2>"
             "<p>Là où l'IA est la plus fiable : prévoir si le mois prochain sera <b>plus calme ou plus agité</b> que ces dernières semaines. "
             + (f"Sur des années jamais vues, ces avis très sûrs ont eu raison <b>{round(_tx * 100)} %</b> du temps ; " if (_tx := ((payload.get("chiffres") or {}).get("agitation_avis_tres_surs"))) else "")
             + "Ce sont les avis les plus fiables du site ; "
             "<a href='avis-surs-verifies.html'>leur vérification en conditions réelles est publique</a>.</p>"
             + ("<div class='pm-grille'>" + "".join(
                 f"<article class='pm-carte'><h3><a href='titres/{seo.slug(t['ticker'])}.html'>{_e(t.get('nom') or t['ticker'])}</a></h3>"
                 f"<p>Mois prochain : <b>plus {'agité' if ((t.get('risque_prevu') or {}).get('recent') or 1) > 1 else 'calme'}</b> que ces dernières semaines"
                 f" (environ ±{round(((t.get('risque_prevu') or {}).get('mouvement') or 0) * 100)} %).</p></article>" for t in tres) + "</div>"
                if tres else "<p class='muted'>Pas d'avis très sûr aujourd'hui.</p>")
             + "<p>Voir aussi : <a href='grandes-bourses.html'>les 10 grandes Bourses du monde</a> · <a href='prevision-or.html'>l'or</a> · "
             "<a href='prediction-bourse.html'>prédiction bourse du mois</a> · <a href='outils/simulateur-stop-loss.html'>simulateur de stop-loss</a></p>")
    jl = seo._jsonld_liste(base, "Top 10 des actions vues à la hausse par l'IA", chemin,
                           [(t.get("nom") or t["ticker"], f"titres/{seo.slug(t['ticker'])}.html") for t in top]) if top else None
    page = seo._page(base, f"Top 10 des actions : hausses, baisses et avis de l'IA | {NOM}",
                     "Les 10 actions que l'IA voit le plus à la hausse ce mois-ci, les plus fortes hausses et baisses du mois et les avis très sûrs. "
                     "Mis à jour chaque heure, résultats vérifiés.", chemin, corps, jl, csp=csp)
    return chemin, page


def _page_bourses(base, payload, csp):
    chemin = "grandes-bourses.html"
    par_tk = {t["ticker"]: t for t in payload.get("titres", [])}
    cartes = [_carte_titre(par_tk[tk], nom, txt) for nom, tk, txt in BOURSES if tk in par_tk]
    lignes = []
    for nom, tk, _ in BOURSES:
        t = par_tk.get(tk)
        if not t:
            continue
        verdict, _s = _phrase_avis(t)
        perf = t.get("perf") or {}
        lignes.append(f"<tr><td><a href='titres/{seo.slug(tk)}.html'>{_e(nom)}</a></td><td class='m'>{seo._pct(perf.get('1 mois'))}</td>"
                      f"<td class='m'>{seo._pct(perf.get('6 mois'))}</td><td style='font-size:14px'>{verdict}</td></tr>")
    corps = (CSS + "<h1>Les 10 grandes Bourses du monde, analysées par l'IA</h1>"
             "<p>New York, Shanghai, Tokyo, Paris, Londres… Pour chaque grande place, le radar suit un indice ou un ETF qui la représente, "
             "et l'IA en fait la même analyse que pour une action : tendance de fond, élan, agitation prévue, risque de chute et avis à un mois. "
             "Mis à jour chaque heure.</p>"
             "<div class='carte' style='overflow-x:auto'><table class='pm-table'><thead><tr><th>Bourse</th><th>1 mois</th><th>6 mois</th><th>Avis de l'IA</th></tr></thead>"
             f"<tbody>{''.join(lignes)}</tbody></table></div>"
             f"<div class='pm-grille'>{''.join(cartes)}</div>"
             "<p class='muted'>Les ETF étrangers sont cotés en dollars : leur performance inclut l'effet du change. Information, pas conseil "
             "en investissement.</p><p>Voir aussi : <a href='top-10-actions.html'>top 10 des actions</a> · <a href='prevision-or.html'>l'or</a> · "
             "<a href='krach-boursier.html'>le radar du risque de krach</a></p>")
    page = seo._page(base, f"Les 10 grandes Bourses du monde : tendance et avis de l'IA | {NOM}",
                     "New York, Nasdaq, Shanghai, Tokyo, Inde, Hong Kong, Paris, Londres, Toronto, Francfort : la tendance, l'agitation prévue et "
                     "l'avis de l'IA pour chaque grande Bourse, chaque heure.", chemin, corps, csp=csp,
                     mots="grandes bourses du monde, bourses mondiales, plus grandes places boursières, bourse de New York, Nasdaq, bourse de Shanghai, "
                          "bourse de Tokyo, Nikkei, bourse indienne, Hong Kong Hang Seng, CAC 40, bourse de Londres, FTSE, bourse de Toronto, DAX, "
                          "bourse Taïwan, bourse Corée, prévision bourses mondiales, tendance marchés mondiaux, avis IA indices boursiers")
    return chemin, page


def _page_or(base, payload, csp):
    chemin = "prevision-or.html"
    par_tk = {t["ticker"]: t for t in payload.get("titres", [])}
    t = par_tk.get("GC=F") or par_tk.get("GLD")
    if not t:
        return None
    s = seo.slug(t["ticker"])
    verdict, _sens = _phrase_avis(t)
    fr_ = t.get("fourchette") or []
    rp, perf = t.get("risque_prevu") or {}, t.get("perf") or {}
    autres = [x for x in (par_tk.get("GLD"), par_tk.get("PAXG-USD"), par_tk.get("SLV")) if x]
    faq = [("Pourquoi le cours de l'or monte ou baisse ?",
            "L'or ne verse ni intérêt ni dividende. Il a tendance à monter quand les taux d'intérêt réels baissent, quand le dollar faiblit "
            "ou quand les investisseurs cherchent une valeur refuge (crises, inflation). Les achats des banques centrales comptent aussi."),
           ("Comment investir dans l'or ?",
            "En or physique (pièces, lingots), avec un ETF ou un ETC adossé à de l'or (comme GLD), ou avec un jeton crypto adossé à l'or (comme PAX Gold). "
            "Chaque solution a ses frais, sa fiscalité et ses risques (garde, émetteur, change euro/dollar)."),
           ("L'IA sait-elle prévoir l'or ?",
            "Comme pour les actions, deviner le sens à un mois est difficile. Elle prévoit mieux l'ampleur des mouvements (l'agitation). "
            "Les résultats réels sont publiés, ratés compris.")]
    corps = (CSS + "<h1>Cours de l'or et prévision de l'IA</h1>"
             f"<p class='muted'>Cours de l'once d'or en dollars (contrat à terme le plus proche), mis à jour chaque heure.</p>"
             f"<div class='pm-carte' style='margin:12px 0'><p style='font-size:18px;margin-top:0'>Avis de l'IA pour le mois qui vient : {verdict}</p>{_mini(t)}"
             "<div class='pm-chiffres'>"
             f"<div><b>{seo._px(t.get('prix'), t.get('devise', ''))}</b><span>l'once</span></div>"
             f"<div><b>{seo._pct(perf.get('1 mois'))}</b><span>sur 1 mois</span></div>"
             f"<div><b>{seo._pct(perf.get('6 mois'))}</b><span>sur 6 mois</span></div></div>"
             + (f"<p>Fourchette probable dans un mois : <b>{seo._px(fr_[0], t.get('devise', ''))}</b> à <b>{seo._px(fr_[1], t.get('devise', ''))}</b>.</p>" if len(fr_) == 2 else "")
             + f"<p>{_analyse(t)}</p><p style='margin-bottom:0'><a class='btn' href='titres/{s}.html'>Graphique et analyse complète</a></p></div>"
             + ("<h2>L'or sous d'autres formes</h2><div class='pm-grille'>" + "".join(_carte_titre(x) for x in autres) + "</div>" if autres else "")
             + "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq)
             + "<p class='muted'>Information, pas conseil en investissement. Le cours affiché est en dollars : pour un épargnant en euros, "
             "le change euro/dollar s'ajoute.</p><p>Voir aussi : <a href='grandes-bourses.html'>les grandes Bourses du monde</a> · "
             "<a href='top-10-actions.html'>top 10 des actions</a> · <a href='outils/simulateur-stop-loss.html?t=gc-f'>tester un stop-loss sur l'or</a></p>")
    jl = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    page = seo._page(base, f"Cours de l'or et prévision : l'avis de l'IA pour le mois | {NOM}",
                     "Le cours de l'or en direct, la fourchette probable à un mois, l'agitation prévue et l'avis de l'IA, avec ses vrais résultats. "
                     "Gratuit, mis à jour chaque heure.", chemin, corps, jl, csp=csp)
    return chemin, page


MOIS_NOMS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_SLUGS = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
EFFETS = {11: "l'« effet Père Noël » (le rallye de fin d'année)", 0: "l'« effet janvier »", 4: "le dicton « Sell in May and go away »",
          8: "la réputation de septembre, souvent présenté comme le pire mois"}


def _page_mois(base, payload, k, csp):
    """Version 111 : « La Bourse en <mois> » — ce que disent les dernières années, calculé sur tous les titres suivis (vrais chiffres)."""
    from datetime import datetime as _dt
    nom, sl = MOIS_NOMS[k], MOIS_SLUGS[k]
    chemin = f"bourse-en-{sl}.html"
    lignes, tous = [], []
    for t in payload.get("titres", []):
        sa = t.get("saison") or {}
        vals = [(a, m[k]) for a, m in zip(sa.get("annees") or [], sa.get("m") or []) if len(m) > k and isinstance(m[k], (int, float))]
        if len(vals) < 3 or t.get("marche") == "tendances":
            continue
        tous += [v for _, v in vals]
        lignes.append((t, vals))
    if len(lignes) < 20:
        return None
    hausse = sum(1 for v in tous if v > 0) / len(tous)
    moy = sum(tous) / len(tous)
    cles = [("^FCHI", "CAC 40"), ("SPY", "S&P 500"), ("QQQ", "Nasdaq 100"), ("BTC-USD", "Bitcoin"), ("GC=F", "Or"), ("ETH-USD", "Ether")]
    par_tk = {t["ticker"]: vals for t, vals in lignes}
    annees = sorted({a for _, vals in lignes for a, _ in vals})
    tab = ("<div class='carte' style='overflow-x:auto'><table class='pm-table'><thead><tr><th></th>" + "".join(f"<th>{a}</th>" for a in annees) + "</tr></thead><tbody>"
           + "".join(f"<tr><td><a href='titres/{seo.slug(tk)}.html'>{_e(lib)}</a></td>" + "".join(
               (lambda v: f"<td class='m {'up' if v > 0 else 'down'}'>{seo._pct(v)}</td>" if v is not None else "<td class='m muted'>–</td>")(dict(par_tk[tk]).get(a))
               for a in annees) + "</tr>" for tk, lib in cles if tk in par_tk) + "</tbody></table></div>")
    reg = sorted([(t, vals) for t, vals in lignes if len(vals) >= 4 and t.get("marche") in ("fr", "eu", "us", "monde", "etf", "crypto")],
                 key=lambda x: (-sum(1 for _, v in x[1] if v > 0) / len(x[1]), -sum(v for _, v in x[1]) / len(x[1])))[:10]
    top = "".join(f"<tr><td><a href='titres/{seo.slug(t['ticker'])}.html'>{_e(t.get('nom') or t['ticker'])}</a></td><td class='m'>{sum(1 for _, v in vals if v > 0)} / {len(vals)}</td>"
                  f"<td class='m'>{seo._pct(sum(v for _, v in vals) / len(vals))}</td></tr>" for t, vals in reg)
    effet = EFFETS.get(k)
    corps = (CSS + f"<h1>La Bourse en {nom} : ce que disent les dernières années</h1>"
             f"<p>Chaque année, on entend parler de {effet + ' ' if effet else 'tendances saisonnières '}: les marchés ont-ils vraiment tendance à monter ou à baisser en {nom} ? "
             f"Plutôt que de croire un dicton, voici les vrais chiffres de {len(lignes)} actions, ETF et cryptos suivis par Radar Bourse, sur {len(annees)} années.</p>"
             "<div class='pm-grille'>"
             f"<div class='pm-carte'><p class='muted' style='margin:0'>Part des {nom}s en hausse</p><p style='font-size:32px;font-weight:700;margin:4px 0' class='{'up' if hausse >= .5 else 'down'}'>{round(hausse * 100)} %</p>"
             f"<p class='muted' style='margin:0'>sur {len(tous)} cas (titre × année)</p></div>"
             f"<div class='pm-carte'><p class='muted' style='margin:0'>Variation moyenne en {nom}</p><p style='font-size:32px;font-weight:700;margin:4px 0' class='{'up' if moy >= 0 else 'down'}'>{seo._pct(moy)}</p>"
             "<p class='muted' style='margin:0'>tous titres confondus</p></div></div>"
             f"<h2>Les grands marchés, {nom} par {nom}</h2>" + tab
             + f"<h2>Les titres qui ont le plus souvent monté en {nom}</h2><div class='carte' style='overflow-x:auto'><table class='pm-table'><thead><tr><th>Titre</th>"
             f"<th>Années en hausse</th><th>Variation moyenne</th></tr></thead><tbody>{top}</tbody></table></div>"
             f"<div class='carte'><b>À garder en tête :</b> {len(annees)} années, c'est très peu pour parler de règle. Un mois souvent vert peut très bien être rouge cette année, "
             "et classer des titres sur 4 ou 5 années, c'est presque du hasard. Ces chiffres servent à remettre les dictons à leur place, pas à décider un achat. "
             "<a href='plus/pieges-statistiques.html'>Pourquoi se méfier des petits échantillons</a>.</div>"
             f"<p>Pour aller plus loin : <a href='analyse-approfondie.html'>l'analyse approfondie d'un titre</a> (avec sa saisonnalité) · <a href='top-10-actions.html'>top 10 des actions</a> · "
             "<a href='prevision-or.html'>l'or</a> · <a href='grandes-bourses.html'>les grandes Bourses du monde</a></p>")
    titre = f"La Bourse en {nom} : hausse ou baisse ? Les vrais chiffres | {NOM}"
    desc = (f"La Bourse monte-t-elle en {nom} ? Part des hausses et variation moyenne en {nom} pour {len(lignes)} actions, ETF et cryptos, "
            f"CAC 40, S&P 500, bitcoin et or, année par année.")
    return chemin, seo._page(base, titre, desc, chemin, corps, csp=csp)


def _pages_mois(base, payload, csp):
    from datetime import datetime as _dt
    m = _dt.now().month - 1
    return [x for x in (_page_mois(base, payload, m, csp), _page_mois(base, payload, (m + 1) % 12, csp)) if x]


def _page_discussions(base, payload, csp):
    """Le forum du site (Giscus) : un fil général et un fil par sujet. Créée seulement si les discussions sont activées."""
    if not seo.giscus_actif():
        return None
    chemin = "discussions.html"
    sujets = [("general", "Le fil général", "Questions sur le site, idées d'amélioration, discussion libre sur la Bourse."),
              ("debutants", "Débuter en Bourse", "Les questions de débutants : aucune question n'est bête ici."),
              ("crypto", "Cryptos", "Bitcoin, ether et les autres : questions et analyses."),
              ("ia", "L'IA du radar", "Ses résultats, ses ratés, ce que tu aimerais qu'elle sache faire.")]
    corps = ("<h1>Discussions</h1><p>Les fils de discussion de Radar Bourse : pose tes questions, partage tes analyses, aide les débutants. "
             "Chaque action a aussi son propre fil, en bas de sa fiche.</p>"
             "<nav class='pm-onglets' aria-label='Les fils'>" + "".join(f"<a href='#fil-{k}'>{_e(t)}</a>" for k, t, _ in sujets) + "</nav>"
             + "".join(f"<div id='fil-{k}'>" + seo.bloc_discussion(f"fil-{k}", t, _e(d)) + "</div>" for k, t, d in sujets))
    return chemin, seo._page(base, f"Discussions : le forum de {NOM}", "Les fils de discussion modérés de Radar Bourse : questions, analyses, "
                             "entraide entre débutants. Lecture libre.", chemin, CSS + corps, csp=csp)


def _page_defi(base, payload, csp):
    """Version 103 : le Défi du jour a sa propre page (lien direct depuis le menu), en plus de sa place dans l'appli."""
    import json as _json
    from . import defi_dossier
    if not os.path.exists(os.path.join(_DOSSIER.get("d", ""), "jeu_temps.json")):
        return None
    chemin = "defi-du-jour.html"
    aides = ("<script>const esc=s=>String(s??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));"
             "const fmtDate=d=>new Date(d+'T12:00:00').toLocaleDateString('fr-FR',{day:'numeric',month:'short',year:'numeric'});"
             "function flash(m){const n=document.createElement('div');n.className='note-flash';n.setAttribute('role','status');n.textContent=m;document.body.appendChild(n);setTimeout(()=>n.remove(),2400);}"
             "const DATA=" + _json.dumps({"jeu_temps": "jeu_temps.json"}) + ";</script>")
    corps = ("<style>" + defi_dossier.CSS + ".note-flash{position:fixed;left:50%;bottom:max(84px,env(safe-area-inset-bottom,0px));transform:translateX(-50%);"
             "z-index:50;background:var(--ink);color:var(--surface);padding:10px 16px;border-radius:10px;font-weight:600}</style>"
             + defi_dossier.HTML.replace("<h2 id=\"h-defi\">", "<h1 id=\"h-defi\" style='font-size:clamp(26px,5vw,36px)'>", 1).replace("</h2>", "</h1>", 1)
             + "<div class='carte'><b>Comment marche le score ?</b> Ton pronostic est noté comme celui des prévisionnistes professionnels "
             "(score de Brier) : être sûr de soi et se tromper coûte cher, dire « je ne sais pas » coûte peu. Ton score est comparé à celui de l'IA du site. "
             "Un nouveau dossier chaque jour, le même pour tout le monde ; gratuit, sans compte : ton score reste sur ton appareil.</div>"
             "<p>Pour aller plus loin : <a href='index.html#remonte'>l'Arène, joue contre l'IA</a> · <a href='formation.html'>l'Académie</a> · "
             "<a href='outils/simulateur-stop-loss.html'>simulateur de stop-loss</a></p>"
             + aides + "<script>(function(){" + defi_dossier.JS.strip() + "})();</script>")
    return chemin, seo._page(base, f"Le Défi du jour : analyse un vrai graphique et bats l'IA | {NOM}",
                             "Chaque jour, un vrai graphique de Bourse masqué : réponds à 4 questions d'analyse, donne ton pronostic à un mois "
                             "et compare ton score à celui de l'IA. Gratuit, sans compte.", chemin, corps, csp=csp)


_DOSSIER = {}


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    _DOSSIER["d"] = dossier
    urls = []
    try:
        for chemin, page in _pages_mois(base, payload, csp):
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.8"))
    except Exception as e:
        print(f"Pages « la Bourse en … » non générées : {e}")
    for fn in (_page_top, _page_bourses, _page_or, _page_discussions, _page_defi):
        try:
            r = fn(base, payload, csp)
        except Exception as e:
            print(f"Page {fn.__name__} non générée : {e}")
            continue
        if not r:
            continue
        chemin, page = r
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "hourly", "0.9"))
    return urls
