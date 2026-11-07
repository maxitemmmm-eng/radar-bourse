"""Version 66 : droits d'auteur et crédits (credits.html et en/credits.html).

Ce qui appartient au site, ce que chacun peut en faire, et tout ce qui vient d'ailleurs
(sources de données, bibliothèques, polices, marques), avec leur licence.
"""
from __future__ import annotations

import os
from datetime import datetime

ANNEE_DEBUT = 2026


def annees() -> str:
    a = datetime.now().year
    return str(ANNEE_DEBUT) if a <= ANNEE_DEBUT else f"{ANNEE_DEBUT}-{a}"


SOURCES = [   # (nom, lien, rôle FR, rôle EN)
    ("Yahoo Finance", "https://finance.yahoo.com", "cours historiques quotidiens, données des entreprises (résultats, dividendes, dates)",
     "daily price history, company data (earnings, dividends, dates)"),
    ("Binance", "https://www.binance.com", "cours des cryptos (historique de secours et cours en direct)", "crypto prices (backup history and live prices)"),
    ("Stooq", "https://stooq.com", "cours historiques de secours", "backup price history"),
    ("CryptoCompare", "https://www.cryptocompare.com", "cours en direct des cryptos absentes de Binance", "live prices for cryptos not on Binance"),
    ("CoinGecko", "https://www.coingecko.com", "informations sur les cryptos", "crypto information"),
    ("Finnhub", "https://finnhub.io", "cours en direct des actions américaines et actualités d'entreprises", "live US stock prices and company news"),
    ("alternative.me", "https://alternative.me/crypto/fear-and-greed-index/", "indice « peur et avidité » des cryptos", "crypto Fear & Greed index"),
    ("FRED (Banque fédérale de réserve de Saint-Louis)", "https://fred.stlouisfed.org", "indicateurs économiques (taux, inflation…)",
     "economic indicators (rates, inflation…)"),
]

LOGICIELS = [   # (nom, lien, licence, rôle FR, rôle EN)
    ("TradingView Lightweight Charts™", "https://www.tradingview.com/lightweight-charts/", "Apache 2.0",
     "graphiques interactifs de l'appli (© TradingView, Inc.)", "interactive charts in the app (© TradingView, Inc.)"),
    ("IBM Plex Sans et IBM Plex Mono", "https://github.com/IBM/plex", "SIL Open Font License 1.1", "polices du texte et des chiffres", "text and number fonts"),
    ("Newsreader", "https://github.com/productiontype/Newsreader", "SIL Open Font License 1.1", "police des titres", "heading font"),
    ("Python, pandas, NumPy, scikit-learn, yfinance, Pillow, Plotly, VADER", "https://www.python.org",
     "licences libres de chaque projet (PSF, BSD, MIT, Apache 2.0, HPND)", "outils de calcul et d'apprentissage utilisés pour fabriquer le site",
     "computing and machine-learning tools used to build the site"),
    ("GitHub Pages et GitHub Actions", "https://pages.github.com", "service de GitHub, Inc.", "hébergement du site et mises à jour automatiques",
     "site hosting and automatic updates"),
]


def _li_sources(fr=True):
    return "".join(f"<li><a href='{u}' rel='noopener noreferrer'>{n}</a> : {f if fr else e}</li>" for n, u, f, e in SOURCES)


def _li_logiciels(fr=True):
    return "".join(f"<li><a href='{u}' rel='noopener noreferrer'>{n}</a> ({lic}) : {f if fr else e}</li>" for n, u, lic, f, e in LOGICIELS)


def generer(seo, anglais, base, dossier, csp) -> list:
    nom = seo.NOM
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    issues = f"https://github.com/{depot}/issues" if depot else None
    a = annees()
    corps = (f"<h1>Droits d'auteur et crédits</h1>"
             f"<p>© {a} {nom}. Tous droits réservés. Le site est publié sous pseudo, de façon non commerciale, à des fins éducatives.</p>"
             "<h2>Ce qui appartient à Radar Bourse</h2>"
             "<p>Les textes, les guides, les analyses rédigées automatiquement, les prévisions et les statistiques calculées par le radar, "
             "le design, le logo, les images et le code sont protégés par le droit d'auteur. "
             "Le code est visible sur GitHub pour la transparence, mais sa licence ne permet pas de le réutiliser sans autorisation.</p>"
             "<h2>Ce que tu peux faire sans demander</h2><ul>"
             "<li>Citer une phrase ou un chiffre du site, avec un lien vers la page d'origine.</li>"
             "<li>Partager un lien, l'image du jour ou une image de partage d'une fiche sur les réseaux.</li>"
             "<li>Intégrer sur ton site le petit module gratuit d'un titre (adresse <code>widget/…html</code>), tel quel, avec son lien.</li>"
             "<li>Télécharger les <a href='donnees-ouvertes.html'>données ouvertes</a> pour un usage personnel, scolaire ou de recherche, en citant "
             f"« {nom} » et l'adresse du site.</li></ul>"
             "<h2>Ce qui demande une autorisation</h2>"
             "<p>Recopier des pages ou des guides entiers, reprendre le code, aspirer le site en masse, ou utiliser son contenu à des fins "
             "commerciales.</p>"
             "<h2>D'où viennent les données</h2>"
             f"<ul>{_li_sources()}</ul>"
             "<p>Ces données appartiennent à leurs fournisseurs et restent soumises à leurs conditions. Le site les affiche à titre "
             "informatif et éducatif, avec un décalage possible. Les actualités affichées ne reprennent que le titre et un lien vers "
             "l'article de l'éditeur, qui reste propriétaire de son contenu.</p>"
             "<h2>Logiciels et polices</h2>"
             f"<ul>{_li_logiciels()}</ul>"
             "<h2>Marques</h2>"
             "<p>Les noms de sociétés, de cryptomonnaies, d'indices (CAC 40, S&amp;P 500, Euro Stoxx 50, Nasdaq 100…) et d'ETF, ainsi que leurs "
             "symboles boursiers, appartiennent à leurs propriétaires. Ils ne sont cités que pour identifier les titres analysés. "
             "Le site n'est lié à aucune de ces sociétés et n'utilise pas leurs logos.</p>"
             "<h2>Signaler un problème de droits</h2>"
             + (f"<p>Si tu penses qu'un contenu du site porte atteinte à tes droits, ouvre un signalement sur <a href='{issues}'>la page GitHub du projet</a> "
                "en précisant la page et le contenu concernés : il sera examiné et retiré si nécessaire.</p>" if issues else
                "<p>Pour signaler un problème de droits, passe par la page <a href='contact.html'>Contact</a>.</p>")
             + "<p class='muted'>Les conditions complètes d'utilisation sont sur la <a href='index.html#conditions'>page d'accueil</a>.</p>")
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Droits d'auteur et crédits",
              "copyrightHolder": {"@type": "Organization", "name": nom}, "copyrightYear": datetime.now().year}
    alt = {"fr": "credits.html", "en": "en/credits.html", "x-default": "credits.html"}
    with open(os.path.join(dossier, "credits.html"), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Droits d'auteur, licences et crédits | {nom}",
                          "Ce qui appartient à Radar Bourse, ce que tu peux en faire, et les sources de données, logiciels et polices utilisés, avec leurs licences.",
                          "credits.html", corps, jsonld, csp, alternates=alt))
    corps_en = (f"<h1>Copyright and credits</h1><p>© {a} {nom}. All rights reserved. Non-commercial educational project published under a pseudonym.</p>"
                "<h2>What belongs to Radar Bourse</h2><p>Texts, guides, automatically written analyses, forecasts and statistics computed by the radar, "
                "design, logo, images and code are protected by copyright. The code is visible on GitHub for transparency, but its licence does not "
                "allow reuse without permission.</p>"
                "<h2>What you can do without asking</h2><ul><li>Quote a sentence or a figure with a link to the original page.</li>"
                "<li>Share a link, the image of the day or a page's share image on social media.</li>"
                f"<li>Download the <a href='../donnees-ouvertes.html'>open data</a> for personal, school or research use, crediting “{nom}” and the site address.</li></ul>"
                "<h2>What needs permission</h2><p>Copying whole pages or guides, reusing the code, bulk scraping, or any commercial use.</p>"
                f"<h2>Data sources</h2><ul>{_li_sources(False)}</ul><p>This data belongs to its providers and remains subject to their terms. "
                "News items show only the headline and a link to the publisher, who owns the content.</p>"
                f"<h2>Software and fonts</h2><ul>{_li_logiciels(False)}</ul>"
                "<h2>Trademarks</h2><p>Company, crypto, index and ETF names and ticker symbols belong to their owners and are used only to identify "
                "the assets analysed. The site is not affiliated with any of them and does not use their logos.</p>"
                "<h2>Report a rights issue</h2>"
                + (f"<p>Open a report on <a href='{issues}'>the project's GitHub page</a> with the page and content concerned; it will be reviewed and removed if needed.</p>"
                   if issues else "<p>Use the contact page of the French site.</p>"))
    os.makedirs(os.path.join(dossier, "en"), exist_ok=True)
    with open(os.path.join(dossier, "en", "credits.html"), "w", encoding="utf-8") as f:
        f.write(anglais._page(base, f"Copyright, licences and credits | {nom}",
                              "What belongs to Radar Bourse, what you may do with it, and the data sources, software and fonts used, with their licences.",
                              "en/credits.html", corps_en, csp, alt))
    return ["credits.html", "en/credits.html"]
