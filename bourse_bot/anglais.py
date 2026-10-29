"""English version (static pages) : a landing page and one page per stock or crypto.

The interactive app stays in French, but these pages let English-speaking visitors find the site on
Google and read the key figures. Every page links to its French twin (hreflang tags).
"""
from __future__ import annotations

import html
import math
import os
from datetime import datetime

from . import langues, seo

NOM = seo.NOM
SIGNAL_EN = {"ACHAT FORT": "strongly bullish", "ACHAT": "bullish", "NEUTRE": "neutral",
             "VENTE": "bearish", "VENTE FORTE": "strongly bearish"}
MARCHE_EN = {"fr": "French stocks", "eu": "European stocks", "us": "US stocks", "crypto": "Cryptocurrencies",
             "etf": "ETFs and indices", "tendances": "Trending"}


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _px(v, dev):
    if v is None:
        return "–"
    if abs(v) >= 1 or v == 0:
        txt = f"{v:,.2f}"
    else:   # petites cryptos (SHIB, PEPE…) : 4 chiffres significatifs, jamais d'écriture « 1.2e-05 »
        txt = f"{v:.{max(2, 3 - math.floor(math.log10(abs(v))))}f}"
    return f"{'€' if dev == '€' else '$'}{txt}"


def _pct(v, d=1):
    if v is None:
        return "–"
    cls = "up" if v > 0 else "down" if v < 0 else ""
    return f'<span class="m {cls}">{"+" if v > 0 else ""}{v * 100:.{d}f}%</span>'


def _page(base, titre, description, chemin, corps, csp, alternates):
    prefixe = "../" * chemin.count("/")
    titre, description = seo.titre_court(titre), seo.desc_courte(description)
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "name": titre, "description": description,
              "inLanguage": "en", "dateModified": datetime.now().isoformat(timespec="seconds"),
              "isPartOf": {"@type": "WebSite", "name": NOM, "url": base or None}}
    tete = seo.balises_tete(base, titre, description, chemin, jsonld=jsonld, alternates=alternates, langue="en")
    tete = tete.replace(f'<meta name="keywords" content="{_e(seo.MOTS_CLES)}">',
                        '<meta name="keywords" content="stock forecast, crypto forecast, technical analysis, RSI, MACD, '
                        'S&amp;P 500, CAC 40, Bitcoin, stock prediction, market outlook">')
    csp = seo.csp_avec_stats(csp)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{tete}
<link rel="icon" href="{prefixe}icone-192.png">
{seo.SCRIPT_THEME}
{seo.POLICES}
{seo.script_stats()}
<style>{seo.CSS_PAGE}</style>
</head>
<body>
{seo.entete(prefixe, chemin, "en/index.html", "Checked forecasts, no promises",
            [("All stocks and cryptos", "en/index.html"), ("If I had invested…", "en/tools/if-i-had-invested.html"),
             ("Crypto converter", "en/tools/crypto-converter.html"), ("Guides", "en/guides.html"), ("Version française", "index.html", 'hreflang="fr" lang="fr"')],
            ("Open the app (FR)", "index.html"), aria_nav="Site pages", aria_theme="Light / dark theme", aller="Skip to content")}
<div class="w">
<main id="contenu" tabindex="-1">
{corps}
</main>
{seo.barre_partage(base, chemin, titre, "Share this page")}
<footer><p class="avert"><b>Nothing is certain in the markets.</b> {NOM} is a free educational project. These figures are generated
automatically, may contain errors and are not investment advice or a recommendation to buy or sell. You can lose all the
money you invest. Full terms of use (in French): <a href="{prefixe}index.html#conditions">conditions d'utilisation</a>.</p>
{f'<p class="muted">Languages: {langues.selecteur(prefixe, "en", alternates)}</p>' if alternates and "es" in alternates else ""}</footer>
</div>
{seo.SCRIPT_BOUTON}
</body></html>
"""


def _page_titre(base, t, horizon, date, csp, modele):
    dev, p = t["devise"], t.get("proba_hausse")
    cone, f = t.get("cone"), t.get("fourchette") or []
    med = cone["mediane"][-1] if cone else None
    sur10 = round(p * 10) if p is not None else None
    verdict = ("leaning higher" if p >= .58 else "slightly higher" if p >= .52 else "no clear direction" if p > .48
               else "slightly lower" if p > .42 else "leaning lower") if p is not None else "not available"
    if p is not None and t.get("avis_net") is False:
        verdict = "without a clear call (the AIs hesitate: in such cases they did no better than chance)"
    nom, tk = t["nom"], t["ticker"]
    s = seo.slug(tk)
    chemin = f"en/stocks/{s}.html"
    titre = f"{nom} ({seo.aff_tk(tk)}) forecast: one-month outlook and analysis | {NOM}"
    desc = (f"{nom} ({seo.aff_tk(tk)}) on {date}: {SIGNAL_EN.get(t['signal'], 'neutral')} technical trend"
            + (", no clear call from the AIs for the coming month" if sur10 is not None and t.get("avis_net") is False else
               f", {sur10} in 10 chance of trading higher in a month according to the model" if sur10 is not None else "")
            + (f", central scenario {_px(med, dev)}" if med else "") + ". Free educational project, not advice.")
    perf, niv = t.get("perf", {}), t.get("niveaux") or {}
    pm = t.get("proba_marche")
    ind = {"le CAC 40": "the CAC 40", "l'Euro Stoxx 50": "the Euro Stoxx 50", "le S&P 500": "the S&P 500",
           "le Bitcoin": "Bitcoin"}.get(t.get("indice_nom") or "", "its market")
    niveaux = "".join(f"<tr><td>{lib}</td><td class='m'>{_px(v, dev)}</td></tr>" for lib, v in (
        ("Resistance (1-year high)", niv.get("resistance")), ("50-day moving average", niv.get("sma50")),
        ("200-day moving average", niv.get("sma200")), ("Support (20-day low)", niv.get("support")),
        ("Indicative stop-loss", t.get("stop_loss"))) if v)
    fiab = ""
    if modele and modele.get("precision") is not None:
        fiab = (f"<p>Measured accuracy of the model on periods it never saw: <b>{round(modele['precision'] * 100)}%</b> "
                f"correct directions (naive baseline {round(modele['precision_base'] * 100)}%). A forecast is a probability, never a promise.</p>")
    corps = f"""
<h1>{_e(nom)} ({_e(seo.aff_tk(tk))}): forecast and analysis</h1>
<p class="muted">Updated automatically · prices as of {_e(date)}</p>
<div class="carte grille">
  <div class="k"><b>{_px(t['prix'], dev)}</b><span>last price</span></div>
  <div class="k"><b>{_pct(perf.get('1 mois'))}</b><span>over 1 month</span></div>
  <div class="k"><b>{round(t['score'])} / 100</b><span>technical score ({SIGNAL_EN.get(t['signal'], '')})</span></div>
  <div class="k"><b>{'no clear call' if sur10 is not None and t.get("avis_net") is False else f'{sur10} in 10' if sur10 is not None else '–'}</b><span>chance of being higher in {horizon} sessions</span></div>
</div>
<h2>Summary</h2>
<p>For the coming month, the radar sees {_e(nom)} <b>{verdict}</b>.
{f"Central scenario: about <b class='m'>{_px(med, dev)}</b>. " if med else ""}
{f"In 8 cases out of 10, the price should stay between <b class='m'>{_px(f[0], dev)}</b> and <b class='m'>{_px(f[1], dev)}</b>." if len(f) == 2 else ""}
{"<b>Strong signal</b>: the model and the technical trend agree." if t.get("signal_fort") else ""}
{f"Probability of beating {ind} over the same period: <b>{round(pm * 100)}%</b>." if pm is not None else ""}</p>
<p><a class="btn" href="../../index.html#{_e(__import__('re').sub(r'[^A-Za-z0-9._-]', '', tk))}">Open the interactive chart and simulator (French)</a></p>
<h2>Key indicators</h2>
<div class="carte"><table>
<tr><td>RSI (14)</td><td class="m">{'–' if niv.get('rsi') is None else round(niv['rsi'])}</td></tr>
<tr><td>ADX (trend strength)</td><td class="m">{'–' if niv.get('adx') is None else round(niv['adx'])}</td></tr>
{f"<tr><td>Expected move over the next 5 sessions</td><td class='m'>±{(t.get('risque_prevu') or {})['semaine'] * 100:.1f}%</td></tr>" if (t.get('risque_prevu') or {}).get('semaine') else ""}
<tr><td>3-month performance</td><td>{_pct(perf.get('3 mois'))}</td></tr>
<tr><td>Annualised volatility</td><td>{_pct(perf.get('volatilité annuelle'), 0)}</td></tr>
<tr><td>Risk level</td><td>{_e({'Faible': 'Low', 'Moyen': 'Medium', 'Élevé': 'High', 'Très élevé': 'Very high'}.get(t.get('risque'), t.get('risque')))}</td></tr>
</table></div>
{f"<h2>Levels to watch</h2><div class='carte'><table>{niveaux}</table></div>" if niveaux else ""}
<h2>Reliability</h2>{fiab or "<p>Statistical forecast: it is often wrong.</p>"}
"""
    return chemin, _page(base, titre, desc, chemin, corps, csp,
                         langues.alternates_titre(s))


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    """Writes en/index.html and en/stocks/*.html. Returns the sitemap entries."""
    date = payload.get("date_donnees", "")
    horizon = payload.get("horizon", 20)
    modele = payload.get("modele")
    titres = payload.get("titres", [])
    os.makedirs(os.path.join(dossier, "en", "stocks"), exist_ok=True)
    urls = [("en/index.html", "daily", "0.8")]
    for t in titres:
        chemin, page = _page_titre(base, t, horizon, date, csp, modele)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily", "0.5"))

    avec_p = sorted([t for t in titres if t.get("proba_hausse") is not None and t.get("avis_net") is not False], key=lambda t: -t["proba_hausse"])
    lien = lambda t: f"<a href='stocks/{seo.slug(t['ticker'])}.html'>{_e(t['nom'])}</a>"
    top = "".join(f"<tr><td>{lien(t)} <span class='muted'>({_e(t['ticker'])})</span></td><td class='m'>{round(t['proba_hausse'] * 100)}%</td></tr>"
                  for t in avec_p[:10])
    forts = [t for t in titres if t.get("signal_fort")]
    groupes = ""
    for cle, lib in MARCHE_EN.items():
        items = [t for t in titres if t.get("marche") == cle]
        if items:
            groupes += f"<h3>{lib}</h3><ul class='liste'>" + "".join(f"<li>{lien(t)}</li>" for t in items) + "</ul>"
    fiab = ""
    if modele and modele.get("precision") is not None:
        fiab = (f"<p>Tested only on periods it never saw, the model found the right direction <b>{round(modele['precision'] * 100)}%</b> "
                f"of the time over {modele.get('nb_tests', 0):,} forecasts (naive baseline {round(modele['precision_base'] * 100)}%). "
                "That is close to chance, which is normal: nobody predicts markets reliably.</p>")
    corps = f"""
<h1>{NOM}: one-month stock and crypto forecasts, explained simply</h1>
<p class="muted">French, European and US stocks, ETFs and major cryptocurrencies, analysed automatically every hour. Free, no sign-up, educational.</p>
<p><a class="btn" href="../index.html">Open the interactive app (French)</a> <a class="btn ghost" href="guides.html">Beginner guides</a></p>
<h2>Highest probability of rising over the next month</h2>
<div class="carte"><table>{top or "<tr><td>Model unavailable today.</td></tr>"}</table></div>
<h2>Strong signals today</h2>
<p>{", ".join(lien(t) for t in forts[:12]) if forts else "None today: the radar does not invent signals when conditions are not met."}</p>
<h2>How reliable is it?</h2>{fiab or "<p>Statistical forecasts are often wrong.</p>"}
<p>Every published forecast is recorded and checked {horizon} sessions later: see the <a href="../resultats.html">real results page</a> (French).</p>
<h2 id="all">All stocks and cryptos</h2>{groupes}
"""
    titre = f"{NOM}: free one-month stock and crypto forecasts"
    desc = ("Free one-month forecasts for French, European and US stocks and major cryptocurrencies: probability of rising, "
            "price range, technical analysis and measured reliability. Educational project, not advice.")
    with open(os.path.join(dossier, "en", "index.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, titre, desc, "en/index.html", corps, csp, langues.alternates_accueil()))
    return urls
