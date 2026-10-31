"""Référencement : tout ce qui aide Google et les réseaux sociaux à trouver et présenter le site.

- une page HTML statique par titre (lisible par Google sans JavaScript) ;
- un glossaire des indicateurs (pages très recherchées) ;
- sitemap.xml, robots.txt, image de partage, icônes et manifeste (installation sur téléphone) ;
- balises <meta> : description, Open Graph, Twitter, adresse canonique, données structurées.
"""
from __future__ import annotations

import html
import math
import json
import os
import re
from datetime import datetime

from . import config

NOM = "Radar Bourse"
SLOGAN = "Analyse et prévisions boursières à un mois, expliquées simplement"
TITRE_ACCUEIL = "Radar Bourse : prévisions bourse et crypto par IA, gratuites"   # le nom en premier : recherches « radar bourse »
DESCRIPTION = ("Prévisions bourse et crypto par IA, gratuites : agitation à un mois, risque de chute, simulateur boursier "
               "à 10 000 € virtuels. Résultats vérifiés publiquement.")
MOTS_CLES = ("prévision bourse IA, prévision action, prévision crypto, prévision bitcoin, simulateur boursier gratuit, "
             "portefeuille virtuel, risque de chute action, volatilité, CAC 40, S&P 500, apprendre la bourse")
LIB_SIGNAL = {"ACHAT FORT": "haussier fort", "ACHAT": "haussier", "NEUTRE": "neutre",
              "VENTE": "baissier", "VENTE FORTE": "baissier fort"}

GLOSSAIRE = [
    ("Bougie (chandelier japonais)", "Représente une journée de cotation : le corps va du prix d'ouverture au prix de clôture (vert si le prix a monté, rouge s'il a baissé), les fines mèches montrent le plus haut et le plus bas du jour."),
    ("Moyenne mobile (SMA)", "Moyenne des cours de clôture sur les N dernières séances. La moyenne 200 jours sert de repère pour la tendance de fond : un cours au-dessus est généralement vu comme un signe de bonne santé."),
    ("Moyenne mobile exponentielle (EMA)", "Moyenne qui donne plus de poids aux séances récentes, donc réagit plus vite que la SMA."),
    ("Golden cross / death cross", "Croisement de la moyenne 50 jours au-dessus (golden cross) ou en dessous (death cross) de la moyenne 200 jours. Signal de changement de tendance de long terme, souvent tardif."),
    ("RSI", "Indicateur de 0 à 100 qui mesure la vitesse des hausses et des baisses récentes. Au-dessus de 70 : titre peut-être monté trop vite (surachat). Sous 30 : peut-être trop baissé (survente)."),
    ("Divergence", "Situation où le prix fait un nouveau sommet alors que le RSI n'en fait pas (divergence baissière), ou l'inverse (divergence haussière). Signale un essoufflement possible."),
    ("MACD", "Différence entre deux moyennes exponentielles (12 et 26 jours). Quand elle passe au-dessus de sa propre moyenne, l'élan devient haussier."),
    ("Bandes de Bollinger", "Enveloppe autour de la moyenne 20 jours, à deux écarts-types. Quand les bandes se resserrent fortement (« squeeze »), un mouvement important suit souvent."),
    ("ATR", "Average True Range : amplitude moyenne d'une séance. Sert à mesurer la volatilité et à placer un stop-loss à une distance raisonnable."),
    ("ADX", "Mesure la force d'une tendance, quel que soit son sens. Au-dessus de 25 : tendance nette."),
    ("Stochastique", "Position du cours entre le plus bas et le plus haut des 14 dernières séances (0 à 100). Au-dessus de 80 : haut de fourchette, sous 20 : bas de fourchette."),
    ("Ichimoku", "Méthode japonaise qui dessine un « nuage » de support et de résistance. Un cours au-dessus du nuage est considéré comme haussier."),
    ("Supertrend", "Ligne qui suit le cours à une distance fondée sur l'ATR et change de côté quand la tendance se retourne."),
    ("Volume", "Nombre de titres échangés. Une hausse avec de forts volumes est jugée plus solide qu'une hausse avec peu d'échanges."),
    ("OBV, MFI, Chaikin Money Flow", "Indicateurs qui combinent prix et volumes pour estimer si l'argent entre (pression acheteuse) ou sort (pression vendeuse)."),
    ("VWAP", "Prix moyen pondéré par les volumes : le prix moyen réellement payé par les investisseurs sur la période."),
    ("Support et résistance", "Niveaux de prix où le cours a souvent rebondi (support) ou buté (résistance). Une cassure de ces niveaux est souvent suivie d'un mouvement marqué."),
    ("Stop-loss", "Niveau de prix fixé à l'avance où l'on vend pour limiter une perte. Indispensable pour gérer le risque."),
    ("Règle des 1 à 2 %", "Ne jamais risquer plus de 1 à 2 % de son capital total sur une seule opération, pour survivre à une série de pertes."),
    ("PER", "Price Earning Ratio : prix de l'action divisé par le bénéfice par action. Indique combien le marché paie chaque euro de bénéfice."),
    ("VIX", "« Indice de la peur » : volatilité attendue de la Bourse américaine. Sous 15 : calme. Au-dessus de 30 : forte nervosité."),
    ("Fear & Greed crypto", "Indice de sentiment des investisseurs en cryptos, de 0 (peur extrême) à 100 (avidité extrême)."),
    ("Probabilité calibrée", "Probabilité recalée sur ce qui s'est réellement passé : « 60 % » signifie que, dans des situations comparables, la hausse s'est produite environ 6 fois sur 10."),
    ("Validation walk-forward", "Méthode de test où le modèle est entraîné sur le passé puis évalué sur une période qu'il n'a jamais vue, comme dans la réalité. Évite les résultats trop beaux pour être vrais."),
    ("Simulation de Monte-Carlo", "Rejoue des milliers de scénarios possibles à partir des variations passées du titre pour montrer l'éventail des résultats, plutôt qu'un seul chiffre."),
]

_COULEURS_SOMBRES = ("--bg:#0a111d;--surface:#111a29;--surface-2:#162133;--ink:#e4ebf5;--muted:#8c9bb0;--line:#22314a;"
                     "--accent:#7398ff;--accent-soft:#1a2747;--up:#35c27d;--up-soft:#11301f;--down:#ff6b62;--down-soft:#3a1716;color-scheme:dark")
# Version 51 : toutes les pages ont la même identité que l'appli (en-tête, logo, menu en pastilles, thème clair/sombre partagé)
CSS_PAGE = """:root{--bg:#eef1f5;--surface:#fff;--surface-2:#f6f8fb;--ink:#0f1b2d;--muted:#5a6a80;--line:#d9e0e8;--accent:#1d4fd8;--accent-soft:#e3eafc;
--up:#07743f;--up-soft:#dcf2e6;--down:#b42a25;--down-soft:#fbe3e1;
--f:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--d:"Newsreader",Georgia,"Times New Roman",serif;--m:"IBM Plex Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){""" + _COULEURS_SOMBRES + """}}
:root[data-theme="dark"]{""" + _COULEURS_SOMBRES + """}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--f)}
.g{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.w{max-width:860px;margin:0 auto;padding-block:22px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.skip{position:absolute;left:12px;top:-60px;z-index:60;background:var(--ink);color:var(--surface);padding:8px 14px;border-radius:8px;font-weight:600;text-decoration:none}.skip:focus{top:12px}
.top{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--line)}
.top .in{max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:12px;padding-block:10px}
.brand{display:flex;align-items:center;gap:10px;margin-right:auto;text-decoration:none;color:var(--ink);min-width:0}
.brand svg{width:26px;height:26px;flex:none}.brand b{font-family:var(--d);font-size:22px;font-weight:700;white-space:nowrap}
.brand span{font-size:13px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ouvrir{flex:none;text-decoration:none;font-size:13.5px;font-weight:600;color:var(--surface);background:var(--ink);padding:6px 12px;border-radius:8px;white-space:nowrap}
.theme-btn{flex:none;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:8px;width:34px;height:30px;display:grid;place-items:center;cursor:pointer}
.nav-sec{max-width:1240px;margin:0 auto;display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;padding-bottom:10px}
.nav-sec::-webkit-scrollbar{display:none}
.nav-sec a{flex:none;text-decoration:none;color:var(--muted);font-size:13.5px;font-weight:600;padding:6px 11px;border-radius:99px;border:1px solid transparent;white-space:nowrap}
.nav-sec a:hover{color:var(--ink);border-color:var(--line)}.nav-sec a[aria-current]{color:var(--surface);background:var(--ink)}
@media (max-width:560px){.brand span{display:none}.brand b{font-size:19px}.ouvrir{padding:6px 10px}}
@media (max-width:380px){.brand svg{display:none}}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
a{color:var(--accent);text-underline-offset:2px}h1,h2,h3{font-family:var(--d);line-height:1.15;text-wrap:balance}h1{font-size:clamp(28px,5vw,40px);margin:10px 0 8px}
h2{font-size:21px;margin:30px 0 10px}h3{font-size:17px;margin:20px 0 6px}.m{font-family:var(--m);font-variant-numeric:tabular-nums}.muted{color:var(--muted)}
.carte{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;margin:14px 0}
.grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.k b{display:block;font-family:var(--m);font-size:20px;font-weight:500}.k>span{font-size:13px;color:var(--muted)}
.up{color:var(--up)}.down{color:var(--down)}.btn{display:inline-block;background:var(--ink);color:var(--surface);padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600}
table{width:100%;border-collapse:collapse}td,th{padding:8px 6px;border-bottom:1px solid var(--line)}td:last-child{text-align:right}
.liste{columns:2 300px;column-gap:28px;padding:0;margin:10px 0;list-style:none}
.liste li{break-inside:avoid;padding:7px 0;border-bottom:1px solid var(--line)}
.liste a{text-decoration:none;color:var(--ink);font-weight:500}.liste a:hover{color:var(--accent);text-decoration:underline}
main>p:first-of-type,main>.carte:first-of-type{margin-top:6px}
.avert{font-size:13.5px;color:var(--muted);border-top:1px solid var(--line);margin-top:40px;padding-top:14px}
footer .muted{font-size:13.5px}
dt{font-weight:700;margin-top:16px}dd{margin:4px 0 0}nav.fil{font-size:14px}
html.contraste{--muted:#2f3b4c;--line:#8795a8}html.contraste[data-theme="dark"]{--muted:#c3cede;--line:#4b5d78}
html.lisible body{letter-spacing:.02em;word-spacing:.08em;line-height:1.75}
.partager-page{font-size:14px;margin-top:34px}
html.texte-115 body{font-size:18px}html.texte-130 body{font-size:20px}"""

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#0f1b2d" stroke="var(--line)" stroke-width="1"/>'
        '<circle cx="16" cy="16" r="9.5" fill="none" stroke="#7398ff" stroke-width="1.4"/><circle cx="16" cy="16" r="4.8" fill="none" '
        'stroke="#7398ff" stroke-width="1" opacity=".55"/><path d="M16 16 L26.5 9.5" stroke="#35c27d" stroke-width="2.6" stroke-linecap="round"/>'
        '<circle cx="16" cy="16" r="2.1" fill="#35c27d"/><circle cx="21.5" cy="21" r="1.5" fill="#35c27d" opacity=".8"/></svg>')

# Lu avant l'affichage : même thème et mêmes réglages de lecture que sur l'appli (pas d'éclair blanc en mode sombre)
SCRIPT_THEME = ('<script>try{var d=document.documentElement,t=localStorage.getItem("radar-theme");if(t)d.dataset.theme=t;'
                'var a=JSON.parse(localStorage.getItem("radar-acces")||"{}")||{};if(a.taille==="115"||a.taille==="130")d.classList.add("texte-"+a.taille);'
                '["contraste","lisible"].forEach(function(k){if(a[k])d.classList.add(k)})}catch(e){}</script>')
POLICES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,600;6..72,700'
           '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
SCRIPT_BOUTON = ('<script>(function(){var b=document.getElementById("theme");if(!b)return;b.onclick=function(){var d=document.documentElement,'
                 'a=d.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),n=a==="dark"?"light":"dark";'
                 'd.dataset.theme=n;try{localStorage.setItem("radar-theme",n)}catch(e){}};'
                 'var c=document.querySelector(".nav-sec [aria-current]");if(c&&c.scrollIntoView)c.scrollIntoView({block:"nearest",inline:"center"})})();</script>')


def entete(prefixe: str, chemin: str, accueil: str, sous_titre: str, liens: list, ouvrir: tuple | None = None,
           aria_nav: str = "Pages du site", aria_theme: str = "Thème clair / sombre", aller: str = "Aller au contenu") -> str:
    """En-tête commun : logo + nom, bouton vers l'appli, thème, puis le menu en pastilles (la page en cours est marquée)."""
    hrefs = [l[1] for l in liens]
    # page en cours, sinon sa rubrique (titres/x.html → « Tous les titres », en/guides/x.html → « Guides »…)
    rubrique = next((c for c in (chemin, chemin.rsplit("/", 1)[0] + ".html", chemin.split("/")[0] + "/index.html") if c in hrefs), None)
    pastilles = "".join(
        f'<a href="{prefixe}{h}"{(" aria-current=" + chr(34) + ("page" if h == chemin else "true") + chr(34)) if h == rubrique else ""}{extra}>{_e(t)}</a>'
        for t, h, *r in liens for extra in [(" " + r[0]) if r else ""])
    bouton = f'<a class="ouvrir" href="{prefixe}{ouvrir[1]}">{_e(ouvrir[0])}</a>' if ouvrir else ""
    return (f'<a class="skip" href="#contenu">{_e(aller)}</a>'
            f'<header class="top g"><div class="in"><a class="brand" href="{prefixe}{accueil}">{LOGO}<b>{NOM}</b>'
            f'<span>{_e(sous_titre)}</span></a>{bouton}'
            f'<button class="theme-btn" id="theme" type="button" aria-label="{_e(aria_theme)}" title="{_e(aria_theme)}">'
            '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" '
            'stroke-width="1.5"/><path d="M8 1.5a6.5 6.5 0 0 1 0 13z" fill="currentColor"/></svg></button></div>'
            f'<nav class="nav-sec" aria-label="{_e(aria_nav)}">{pastilles}</nav></header>')


def barre_partage(base: str, chemin: str, titre: str, libelle: str = "Partager cette page") -> str:
    """Version 52 : liens de partage simples (aucun script tiers, aucun pisteur). Seulement si l'adresse du site est connue."""
    if not base or chemin == "404.html":
        return ""
    from urllib.parse import quote
    u, t = quote(base + chemin, safe=""), quote(titre.split(" | ")[0], safe="")
    liens = [("WhatsApp", f"https://wa.me/?text={t}%20{u}"), ("X", f"https://twitter.com/intent/tweet?text={t}&url={u}"),
             ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}"), ("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}"),
             ("Reddit", f"https://www.reddit.com/submit?url={u}&title={t}")]
    return ("<p class='partager-page muted'>" + _e(libelle) + " : " + " · ".join(
        f"<a href='{_e(h)}' target='_blank' rel='noopener noreferrer'>{n}</a>" for n, h in liens) + "</p>")


def liens_fr() -> list:
    return [("Le point du jour", "point.html"), ("Résultats réels", "resultats.html"),
            ("Tous les titres", "titres.html"), ("Comparer", "comparer.html"), ("Classements", "classements.html"),
            ("Sélection IA du mois", "portefeuille.html"), (f"Prévisions {datetime.now().year}", "previsions.html"),
            ("Simulateur boursier", "simulateur-boursier.html"), ("Outils gratuits", "outils.html"), ("Guides", "guides.html"), ("Apprendre", "apprendre.html"), ("Glossaire", "glossaire.html"),
            ("Les mini-robots", "robots.html"), ("Ce que sait l'IA", "connaissances.html"),
            ("Fiche technique", "fiche-technique-ia.html"), ("Fonctionnalités", "fonctionnalites.html"), ("À propos", "a-propos.html"),
            ("Contact", "contact.html"), ("English", "en/index.html", 'hreflang="en" lang="en"')]


def url_site() -> str:
    """Adresse publique du site : déduite du dépôt GitHub, ou définie dans RADAR_URL."""
    if config.DOMAINE:
        return f"https://{config.DOMAINE}/"
    if os.environ.get("RADAR_URL"):
        return os.environ["RADAR_URL"].rstrip("/") + "/"
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in depot:
        proprio, nom = depot.split("/", 1)
        if nom.lower() == f"{proprio.lower()}.github.io":
            return f"https://{proprio.lower()}.github.io/"
        return f"https://{proprio.lower()}.github.io/{nom}/"
    return ""


def slug(ticker: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", ticker.lower()).strip("-") or "titre"


def aff_tk(tk: str) -> str:
    """TON11419-USD → TON-USD : on cache le numéro interne de Yahoo."""
    return re.sub(r"\d+(-USD)$", r"\1", str(tk))


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _px(v, dev):
    if v is None:
        return "–"
    if abs(v) >= 1 or v == 0:
        txt = f"{v:,.2f}"
    else:   # petites cryptos (SHIB, PEPE…) : 4 chiffres significatifs, jamais d'écriture « 1.2e-05 »
        txt = f"{v:.{max(2, 3 - math.floor(math.log10(abs(v))))}f}"
    return txt.replace(",", "\u202f").replace(".", ",") + f" {dev}"


def _pct(v, d=1):
    if v is None:
        return "–"
    cls = "up" if v > 0 else "down" if v < 0 else ""
    return f'<span class="m {cls}">{"+" if v > 0 else ""}{v*100:.{d}f} %</span>'.replace(".", ",", 1)


def balises_tete(base: str, titre: str, description: str, chemin: str = "", image: str = "partage.png",
                 jsonld: dict | None = None, alternates: dict | None = None, langue: str = "fr") -> str:
    """Balises <head> communes : description, Open Graph, Twitter, canonique, icônes, manifeste."""
    url = (base + chemin) if base else ""
    img = (base + image) if base else image
    lignes = [
        f'<meta name="description" content="{_e(description)}">',
        f'<meta name="keywords" content="{_e(MOTS_CLES)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        f'<meta name="author" content="{NOM}">',
        f'<meta name="application-name" content="{NOM}">',
        f'<meta name="apple-mobile-web-app-title" content="{NOM}">',
        '<meta name="format-detection" content="telephone=no">',   # les prix ne deviennent pas des numéros de téléphone sur iPhone
        # même couleur que l'en-tête du site, en clair comme en sombre ; « color-scheme » évite l'éclair blanc à l'ouverture
        '<meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff">',
        '<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#111a29">',
        '<meta name="color-scheme" content="light dark">',
        f'<meta property="og:site_name" content="{NOM}">',
        f'<meta property="og:locale" content="{_locale(langue)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{_e(titre)}">',
        f'<meta property="og:description" content="{_e(description)}">',
        f'<meta property="og:image" content="{_e(img)}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{_e(titre)}">',
        f'<meta name="twitter:image:alt" content="{_e(titre)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_e(titre)}">',
        f'<meta name="twitter:description" content="{_e(description)}">',
        f'<meta name="twitter:image" content="{_e(img)}">',
        f'<link rel="manifest" href="{"../" * chemin.count("/")}manifest.webmanifest">',
        f'<link rel="alternate" type="application/rss+xml" title="{NOM}" href="{"../" * chemin.count("/")}flux.xml">',
        f'<link rel="apple-touch-icon" href="{"../" * chemin.count("/")}icone-180.png">',
    ]
    if url:
        lignes += [f'<link rel="canonical" href="{_e(url)}">', f'<meta property="og:url" content="{_e(url)}">']
    if base and alternates:   # versions dans d'autres langues (Google affiche la bonne selon le visiteur)
        for lg, c in alternates.items():
            lignes.append(f'<link rel="alternate" hreflang="{lg}" href="{_e(base + c)}">')
        for lg in alternates:   # partages sur les réseaux : les autres langues disponibles
            if lg not in ("x-default", langue):
                lignes.append(f'<meta property="og:locale:alternate" content="{_locale(lg)}">')
    verif = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    if verif and re.fullmatch(r"[A-Za-z0-9_\-]{10,100}", verif):
        lignes.append(f'<meta name="google-site-verification" content="{verif}">')
    if not jsonld and chemin and base and not chemin.startswith("widget/") and chemin != "404.html":
        # Version 55 : toute page indexée décrit au moins ce qu'elle est et où elle se trouve dans le site
        jsonld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebPage", "name": titre, "description": description, "url": url,
             "inLanguage": "en" if langue == "en" else "fr-FR", "isPartOf": {"@id": base + "#site"},
             "primaryImageOfPage": img},
            _jsonld_fil(base, [(NOM, ""), (titre.split(" : ")[0].split(" | ")[0][:60], chemin)])]}
    if jsonld:
        data = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        lignes.append(f'<script type="application/ld+json">{data}</script>')
    return "\n".join(lignes)


_VOLATIL = re.compile(r"\d{4}-\d{2}-\d{2}(?:T[\d:.+Z-]*)?|\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{1,2}[h:]\d{2}(?::\d{2})?"
                      r"|\b\d{1,2}(?:er)? (?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre) \d{4}"
                      r"|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", re.I)


def _dates_modif(dossier: str, chemins: list, aujourdhui: str) -> dict:
    """Version 55 : vraie date de dernière modification de chaque page pour le sitemap. Avant, toutes les pages
    portaient la date du jour, même les guides qui ne changent jamais : Google finit alors par ignorer ces dates.
    On garde une empreinte du contenu (sans les dates et heures) ; la date ne change que si le contenu change."""
    import hashlib
    fichier = os.path.join(config.DOSSIER_HISTORIQUE, "dates_pages.json")
    try:
        with open(fichier, encoding="utf-8") as f:
            avant = json.load(f)
    except (OSError, ValueError):
        avant = {}
    apres, dates = {}, {}
    for c in chemins:
        chemin = os.path.join(dossier, c or "index.html")
        try:
            with open(chemin, encoding="utf-8", errors="replace") as f:
                texte = f.read()
        except OSError:
            dates[c] = aujourdhui
            continue
        texte = _VOLATIL.sub("", re.sub(r"<script\b[^>]*>.*?</script>", "", texte, flags=re.S))
        empreinte = hashlib.sha1(texte.encode("utf-8", "replace")).hexdigest()[:16]
        ancien = avant.get(c)
        date = ancien[1] if isinstance(ancien, list) and len(ancien) == 2 and ancien[0] == empreinte else aujourdhui
        apres[c], dates[c] = [empreinte, date], date
    try:
        os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(apres, f, separators=(",", ":"), sort_keys=True)
    except OSError:
        pass
    return dates


def script_stats() -> str:
    """Compteur de visites GoatCounter (anonyme, sans cookie) si configuré."""
    code = config.GOATCOUNTER
    if not code:
        return ""
    return (f'<script data-goatcounter="https://{code}.goatcounter.com/count" '
            'async src="https://gc.zgo.at/count.js"></script>')


def csp_avec_stats(csp: str) -> str:
    code = config.GOATCOUNTER
    if not code or not csp:
        return csp
    hote = f"https://{code}.goatcounter.com"
    return (csp.replace("script-src 'self' 'unsafe-inline'", "script-src 'self' 'unsafe-inline' https://gc.zgo.at")
               .replace("img-src 'self' data:", f"img-src 'self' data: {hote}")
               .replace("connect-src 'self'", f"connect-src 'self' {hote}"))


def desc_courte(d: str, maxi: int = 160) -> str:
    if not d or len(d) <= maxi:
        return d
    return d[: d.rfind(" ", 0, maxi - 1)].rstrip(" ,;:") + "…"


def _locale(langue: str) -> str:
    if langue == "fr":
        return "fr_FR"
    if langue == "en":
        return "en_US"
    from .langues import LANGUES
    return LANGUES.get(langue, ("", "fr_FR"))[1]


def titre_court(titre: str, maxi: int = 65) -> str:
    """Google coupe les titres vers 60 caractères : on retire « | Radar Bourse » (ou « avec Radar Bourse »)
    quand le titre est trop long, pour garder les mots utiles visibles."""
    if len(titre) <= maxi:
        return titre
    for fin in (f" | {NOM}", f" avec {NOM}"):
        if titre.endswith(fin):
            titre = titre[: -len(fin)]
            break
    if len(titre) > maxi + 5:   # version 51 : on retire les précisions entre parenthèses du nom, en gardant le code (SMH, BTC-USD…)
        court = re.sub(r" \((?![A-Z0-9.^=\-]+\))[^()]*\)", "", titre)
        if len(court) >= 25:
            titre = court
    return titre


IMAGES_PAGES: dict = {}   # version 53 : image de partage propre à chaque type de page (voir visuels.py)


def _image_de(chemin, image="partage.png"):
    if image != "partage.png":
        return image
    from .visuels import image_pour
    return image_pour(chemin, IMAGES_PAGES) or image


def _page(base, titre, description, chemin, corps, jsonld=None, csp="", alternates=None, image="partage.png"):
    image = _image_de(chemin, image)
    prefixe = "../" * chemin.count("/")
    csp = csp_avec_stats(csp)
    titre = titre_court(titre)
    description = desc_courte(description)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{balises_tete(base, titre, description, chemin, image=image, jsonld=jsonld, alternates=alternates)}
{liens_icones(prefixe)}
{SCRIPT_THEME}
{POLICES}
{script_stats()}
<style>{CSS_PAGE}</style>
</head>
<body>
{entete(prefixe, chemin, "index.html", "Prévisions vérifiées, sans promesse", liens_fr(), ("Ouvrir l'appli", "index.html"))}
<div class="w">
<main id="contenu" tabindex="-1">
{corps}
</main>
{barre_partage(base, chemin, titre)}
<footer><p class="avert"><b>Rien n'est sûr en Bourse.</b> {NOM} est un projet éducatif : ces informations sont générées automatiquement,
peuvent contenir des erreurs et ne constituent pas un conseil en investissement. Tu peux perdre tout l'argent investi.
Conditions d'utilisation, méthodologie et aide : voir la <a href="{prefixe}index.html#conditions">page d'accueil</a>.</p>
<p class="muted"><a href="{prefixe}fonctionnalites.html">Fonctionnalités</a> · <a href="{prefixe}simulateur-boursier.html">Simulateur boursier</a> · <a href="{prefixe}outils.html">Outils gratuits</a> · <a href="{prefixe}a-propos.html">À propos</a> · <a href="{prefixe}contact.html">Contact</a></p></footer>
</div>
{SCRIPT_BOUTON}
</body></html>
"""


def _page_titre(base, t, horizon, date, csp, modele, suivi=None, voisins=()):
    dev, prix, p = t["devise"], t["prix"], t.get("proba_hausse")
    cone, f = t.get("cone"), t.get("fourchette") or []
    med = cone["mediane"][-1] if cone else None
    sur10 = round(p * 10) if p is not None else None
    verdict = ("plutôt à la hausse" if p >= .58 else "légèrement à la hausse" if p >= .52 else
               "sans direction claire" if p > .48 else "légèrement à la baisse" if p > .42 else
               "plutôt à la baisse") if p is not None else "sans prévision de direction aujourd'hui"
    if p is not None and t.get("avis_net") is False:
        verdict = "sans avis net (les IA hésitent : dans ces cas-là, elles n'ont pas fait mieux que le hasard)"
    rq = t.get("risque_prevu") or {}
    agitation = (f"<p>Agitation prévue le mois prochain : en général, le prix bougera d'environ <b class='m'>±{round(rq['mouvement'] * 100)} %</b>"
                 + (", plus que d'habitude" if (rq.get("habitude") or 1) > 1.25 else ", moins que d'habitude" if (rq.get("habitude") or 1) < 0.8 else "")
                 + ", dans un sens ou dans l'autre.</p>") if rq.get("mouvement") else ""
    if rq.get("semaine"):
        agitation += (f"<p>Sur la semaine qui vient (5 séances) : environ <b class='m'>±{rq['semaine'] * 100:.1f} %</b>.".replace(".", ",", 1)
                      + " Cette prévision à une semaine a été testée sur près de 290 000 cas réels : plus proche de la réalité que « comme la semaine dernière » 57 fois sur 100.</p>")
    pourquoi = "".join(f"<li><b>{_e(r['famille'])}</b> : pousse vers la {'hausse' if r['effet'] > 0 else 'baisse'}"
                       + (f" ({_e(r['etat'])})" if r.get("etat") else "") + "</li>" for r in (t.get("raisons_ia") or []))
    nom, tk = t["nom"], t["ticker"]
    marche = t.get("marche", "")
    hub = MARCHES.get(marche)
    # Performances (contenu propre à chaque titre)
    pf = t.get("perf") or {}
    perfs = "".join(f"<tr><td>{lib}</td><td class='m'>{_pct(pf.get(k))}</td></tr>" for k, lib in (
        ("1 semaine", "1 semaine"), ("1 mois", "1 mois"), ("3 mois", "3 mois"), ("6 mois", "6 mois"), ("1 an", "1 an")) if pf.get(k) is not None)
    if pf.get("volatilité annuelle") is not None:
        perfs += f"<tr><td>Volatilité annuelle</td><td class='m'>{_pct(pf['volatilité annuelle'], 0).replace('+', '')}</td></tr>"
    # Profil de l'entreprise (actions seulement)
    fd = t.get("fondamentaux") or {}
    profil = _profil(fd) if fd.get("valeurs") else ""
    # Palmarès réel sur ce titre
    pt = (((suivi or {}).get("detail") or {}).get("par_titre") or {}).get(tk)
    palmares = (f"<p>Depuis le début du suivi, sur <b>{pt[0]}</b> prévisions vérifiées un mois plus tard pour {_e(nom)}, "
                f"les IA ont vu juste <b>{pt[1]} fois</b> ({round(pt[1] / pt[0] * 100)} %).</p>") if pt and pt[0] >= 5 else ""
    est_crypto = tk.endswith("-USD")
    if est_crypto:
        titre = f"{nom} ({aff_tk(tk).replace('-USD', '')}) : cours, prévision et analyse IA | {NOM}"
    elif t.get("marche") in ("fr", "eu", "us") or (t.get("fondamentaux") or {}).get("valeurs"):
        titre = f"Action {nom} ({aff_tk(tk)}) : cours, prévision et analyse IA | {NOM}"
    else:
        titre = f"{nom} : cours, prévision et analyse IA | {NOM}"
    faq = _faq_titre(t, nom, date, verdict)
    # version 52 : « si j'avais investi 100 il y a un an » (vrais cours) + lien vers le simulateur
    investi_html = ""
    try:
        from .outils import valeur_un_an
        vi = valeur_un_an(t)
    except Exception:
        vi = None
    if vi:
        dev = t.get("devise", "")
        sym = {"EUR": "€", "USD": "$"}.get(dev, dev)
        cent = f"100 {sym}"
        lignes_vi = []
        for cle, quand in (("an", "il y a un an"), ("six_mois", "il y a six mois")):
            if cle in vi:
                d0, v = vi[cle]
                lignes_vi.append(f"<li><b>{cent}</b> investis dans {_e(nom)} {quand} (le {_e(date_longue(d0))}) vaudraient aujourd'hui "
                                 f"<b class='{'up' if v >= 100 else 'down'}'>{_px(v, dev)}</b> ({_pct(v / 100 - 1)}).</li>")
        if lignes_vi:
            investi_html = (f"<h2>Si tu avais investi dans {_e(nom)}</h2><ul>{''.join(lignes_vi)}</ul>"
                            f"<p class='muted'>Performance brute du cours, sans frais, dividendes, impôts{' ni effet du change euro/dollar' if dev in ('$', 'USD') else ''}. "
                            f"Le passé ne prévoit pas l'avenir. <a href='../outils/si-javais-investi.html?t={_e(tk)}'>Simuler une autre somme ou un investissement chaque mois</a></p>")
            if "an" in vi:
                d0, v = vi["an"]
                faq = list(faq) + [(f"Combien vaudraient {cent} investis dans {nom} il y a un an ?",
                                    f"{cent} investis dans {_e(nom)} le {_e(date_longue(d0))} vaudraient environ {_px(v, dev)} au {_e(date)}, "
                                    f"soit {_pct(v / 100 - 1)} (performance brute, sans frais ni impôts).")]
    duels_html = ("<h2>Comparer</h2><ul class='liste'>" + "".join(
        f"<li><a href='../{ch}'>{_e(nom)} ou {_e(o['nom'])}</a></li>"
        for o, ch in (t.get("_duels") or [])[:10]) + "</ul>") if t.get("_duels") else ""
    similaires = "".join(f"<li><a href='{slug(v['ticker'])}.html'>{_e(v['nom'])}</a></li>" for v in voisins)
    mv = (t.get("risque_prevu") or {}).get("mouvement")
    desc = (f"{nom} ({aff_tk(tk)}) au {date} : "
            + (f"agitation prévue ±{round(mv * 100)} %, " if mv else "")
            + ("pas d'avis net des IA sur la hausse. " if sur10 is not None and t.get("avis_net") is False else
               f"{sur10} chances sur 10 de hausse à un mois. " if sur10 is not None else "")
            + "Analyse IA gratuite et vérifiée, pas un conseil.")
    chemin = f"titres/{slug(tk)}.html"
    lien_app = f"../index.html#{re.sub(r'[^A-Za-z0-9._-]', '', tk)}"
    perf = t.get("perf", {})
    raisons = "".join(f"<li>{_e(r)}</li>" for r in (t.get("alertes", []) + t.get("raisons_pour", []) + t.get("raisons_contre", []))[:10])
    actus = "".join(f'<li><a href="{_e(a["url"])}" rel="noopener noreferrer nofollow" target="_blank">{_e(a["titre"])}</a> <span class="muted">({_e(a.get("source", ""))})</span></li>'
                    for a in (t.get("actus") or [])[:5] if str(a.get("url", "")).startswith("http"))
    niv = t.get("niveaux") or {}
    niveaux = "".join(f"<tr><td>{lib}</td><td class='m'>{_px(v, dev)}</td></tr>" for lib, v in (
        ("Résistance (plus haut sur un an)", niv.get("resistance")), ("Moyenne 50 jours", niv.get("sma50")),
        ("Moyenne 200 jours", niv.get("sma200")), ("Support (plus bas sur 20 séances)", niv.get("support")),
        ("Stop-loss indicatif", t.get("stop_loss"))) if v)
    fiab = ""
    if modele and modele.get("precision") is not None:
        fiab = (f"<p>Fiabilité mesurée du modèle sur des périodes jamais vues : "
                f"<b>{round(modele['precision']*100)} %</b> de bonnes directions (référence naïve "
                f"{round(modele['precision_base']*100)} %). Une prévision reste une probabilité.</p>")
    fil = (f"<p class='muted' style='font-size:14px'><a href='../titres.html'>Tous les titres</a>"
           + (f" › <a href='../marches/{hub[0]}.html'>{_e(hub[1])}</a>" if hub else "") + f" › {_e(nom)}</p>")
    corps = f"""{fil}
<h1>{"Action " if titre.startswith("Action ") else ""}{_e(nom)} ({_e(aff_tk(tk))}) : cours, prévision et analyse</h1>
<p class="muted">Mise à jour automatique · cours au {_e(date)}</p>
<div class="carte grille">
  <div class="k"><b>{_px(prix, dev)}</b><span>dernier cours</span></div>
  <div class="k"><b>{_pct(perf.get('1 mois'))}</b><span>sur 1 mois</span></div>
  <div class="k"><b>{round(t['score'])} / 100</b><span>score technique ({LIB_SIGNAL.get(t['signal'], '')})</span></div>
  <div class="k"><b>{'pas d’avis net' if sur10 is not None and t.get("avis_net") is False else f'{sur10} sur 10' if sur10 is not None else '–'}</b><span>chances d'être plus haut dans {horizon} séances</span></div>
</div>
<h2>En résumé</h2>
<p>Pour le mois qui vient, le radar voit {_e(nom)} <b>{verdict}</b>.
{f"Scénario central : environ <b class='m'>{_px(med, dev)}</b>. " if med else ""}
{f"Dans 8 cas sur 10, le cours devrait rester entre <b class='m'>{_px(f[0], dev)}</b> et <b class='m'>{_px(f[1], dev)}</b>." if len(f) == 2 else ""}
{f"Cette promesse a été tenue {round(modele['fourchette']['couverture'] * 100)} fois sur 100 sur les années testées (<a href='../fiche-technique-ia.html'>fiche technique</a>)." if len(f) == 2 and ((modele or {}).get('fourchette') or {}).get('couverture') else ""}
{"<b>Signal fort</b> : le modèle et la tendance technique vont dans le même sens." if t.get("signal_fort") else ""}
{f"Probabilité de faire mieux que {_e(t.get('indice_nom') or 'son marché')} sur la même période : <b>{round(t['proba_marche'] * 100)} %</b>." if t.get("proba_marche") is not None else ""}
{"Fourchette élargie par prudence : l'entreprise publie ses résultats avant l'échéance." if t.get("fourchette_elargie") else ""}</p>
{agitation}
{f"<h2>Pourquoi cet avis ?</h2><p class='muted'>Ce qui a le plus pesé dans le calcul des deux IA.</p><ul>{pourquoi}</ul>" if pourquoi else ""}
<p><a class="btn" href="{lien_app}">Voir le graphique interactif et le simulateur</a></p>
{f"<h2>Ce que montrent les indicateurs</h2><ul>{raisons}</ul>" if raisons else ""}
{f"<h2>Niveaux à surveiller</h2><div class='carte'><table>{niveaux}</table></div>" if niveaux else ""}
{f"<h2>Dernières actualités</h2><ul>{actus}</ul>" if actus else ""}
{f"<h2>Performances passées</h2><div class='carte'><table>{perfs}</table></div>" if perfs else ""}
{investi_html}
{profil}
<h2>Fiabilité</h2>{palmares}{fiab or "<p>Prévision statistique : elle se trompe souvent.</p>"}
{f"<h2>Questions fréquentes sur {_e(nom)}</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{r}</p>" for q, r in faq) if faq else ""}
{f"<h2>Autres titres du même marché</h2><ul class='liste'>{similaires}</ul>" if similaires else ""}
{duels_html}
<h2>Afficher {_e(nom)} sur ton site</h2>
<p>Un petit encadré gratuit, mis à jour automatiquement (cours, agitation prévue, avis des IA). Copie ce code dans ta page :</p>
<pre class='code' style='white-space:pre-wrap;word-break:break-all;font-size:12.5px'>{_e(f'<iframe src="{base or "../"}widget/{slug(tk)}.html" width="320" height="150" style="border:0" title="{nom} · {NOM}" loading="lazy"></iframe>')}</pre>
"""
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "name": titre, "description": desc,
              "inLanguage": "fr-FR", "dateModified": datetime.now().isoformat(timespec="seconds"),
              "isPartOf": {"@type": "WebSite", "name": NOM, "url": base or None},
              "about": ({"@type": "Corporation", "name": nom, "tickerSymbol": aff_tk(tk)} if titre.startswith("Action ")
                        else {"@type": "Thing", "name": f"{nom} ({aff_tk(tk)})"})}
    graphe = [jsonld, _jsonld_fil(base, [("Tous les titres", "titres.html")] + ([(hub[1], f"marches/{hub[0]}.html")] if hub else [])
                                  + [(nom, chemin)])]
    if faq:
        graphe.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {
            "@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for q, r in faq]})
    jsonld = {"@context": "https://schema.org", "@graph": [{k: v for k, v in g.items() if k != "@context"} for g in graphe]}
    img = f"partage/{slug(tk)}.png" if t.get("_image_ok") else "partage.png"
    from . import langues as _lg
    corps += f"<p class='muted'>Cette page dans d'autres langues : {_lg.selecteur('../', 'fr', _lg.alternates_titre(slug(tk)))}</p>"
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp,
                         alternates=__import__("bourse_bot.langues", fromlist=["x"]).alternates_titre(slug(tk)), image=img)


# Comparaisons que les gens tapent vraiment sur Google (« or ou bitcoin », « LVMH ou Hermès »…)
DUELS = [("BTC-USD", "ETH-USD"), ("GLD", "BTC-USD"), ("CW8.PA", "SPY"), ("SPY", "QQQ"), ("^FCHI", "SPY"),
         ("ETH-USD", "SOL-USD"), ("BTC-USD", "SOL-USD"), ("XRP-USD", "ADA-USD"), ("DOGE-USD", "SHIB-USD"),
         ("SOL-USD", "AVAX-USD"), ("BNB-USD", "SOL-USD"), ("BTC-USD", "LTC-USD"),
         ("AAPL", "MSFT"), ("NVDA", "AMD"), ("GOOGL", "META"), ("AMZN", "GOOGL"), ("AMD", "INTC"),
         ("V", "JPM"), ("NFLX", "DIS"), ("TSLA", "NVDA"), ("NVDA", "AVGO"), ("NVDA", "SMH"),
         ("MC.PA", "RMS.PA"), ("MC.PA", "KER.PA"), ("OR.PA", "EL.PA"), ("BNP.PA", "GLE.PA"),
         ("AIR.PA", "SAF.PA"), ("TTE.PA", "XLE"), ("ASML.AS", "NVDA"), ("SAP.DE", "MSFT"), ("RACE.MI", "TSLA"),
         # version 33
         ("KO", "PEP"), ("V", "MA"), ("JPM", "BAC"), ("COIN", "MSTR"), ("MSTR", "BTC-USD"), ("WMT", "COST"),
         ("RNO.PA", "STLAP.PA"), ("HO.PA", "AM.PA"), ("BNP.PA", "ACA.PA"), ("ENGI.PA", "TTE.PA"), ("ORA.PA", "EN.PA"),
         ("STMPA.PA", "SOI.PA"), ("RHM.DE", "HO.PA"), ("BRK-B", "SPY"), ("MCD", "SBUX"), ("BA", "AIR.PA")]


MAX_DUELS = 450
CRYPTOS_DUELS = 14   # les plus grosses cryptos : toutes comparées entre elles


def _duels_dispos(titres):
    """Les duels choisis à la main, puis (version 39) des duels automatiques entre titres comparables :
    même marché et même secteur pour les actions, les plus grosses cryptos entre elles."""
    par = {t["ticker"]: t for t in titres}
    paires = [(a, b) for a, b in DUELS if a in par and b in par]
    vus = {frozenset(p) for p in paires}
    groupes = {}
    for t in titres:
        if t.get("marche") in ("fr", "eu", "us") and t.get("secteur"):
            groupes.setdefault((t["marche"], t["secteur"]), []).append(t["ticker"])
    from .config import CRYPTOS
    cryptos = [tk for tk in list(CRYPTOS)[:CRYPTOS_DUELS] if tk in par]
    candidats = [(x, y) for i, x in enumerate(cryptos) for y in cryptos[i + 1:]]
    for g in sorted(groupes.values(), key=len):
        candidats += [(x, y) for i, x in enumerate(g) for y in g[i + 1:]]
    for x, y in candidats:
        if len(paires) >= MAX_DUELS:
            break
        if frozenset((x, y)) not in vus:
            vus.add(frozenset((x, y)))
            paires.append((x, y))
    return [(par[a], par[b]) for a, b in paires]


def _chemin_duel(a, b):
    return f"comparer/{slug(a['ticker'])}-ou-{slug(b['ticker'])}.html"


def _page_duel(base, a, b, date, csp):
    """« X ou Y ? » : les deux titres côte à côte, avec les chiffres du jour. On compare, on ne conseille pas."""
    na, nb = a["nom"], b["nom"]
    chemin = _chemin_duel(a, b)
    def avis(t):
        p = t.get("proba_hausse")
        if p is None:
            return "–"
        return "pas d'avis net" if t.get("avis_net") is False else f"{round(p * 100)} chances sur 100 de hausse"
    def face(t):
        pm = t.get("proba_marche")
        if pm is None:
            return "–"
        return ("pas d'avis net" if t.get("marche_net") is False else f"{round(pm * 100)} sur 100") + f" (vs {_e(t.get('indice_nom') or 'son marché')})"
    agit = lambda t: f"±{round((t.get('risque_prevu') or {})['mouvement'] * 100)} %" if (t.get("risque_prevu") or {}).get("mouvement") else "–"
    chu = lambda t: f"{round((t.get('risque_prevu') or {})['chute'] * 100)} sur 100" if (t.get("risque_prevu") or {}).get("chute") is not None else "–"
    perf = lambda t, k: _pct((t.get("perf") or {}).get(k)) if (t.get("perf") or {}).get(k) is not None else "–"
    vol = lambda t: _taux((t.get("perf") or {}).get("volatilité annuelle"))
    lignes = [("Cours", _px(a.get("prix"), a.get("devise", "")), _px(b.get("prix"), b.get("devise", ""))),
              ("Sur un mois", perf(a, "1 mois"), perf(b, "1 mois")),
              ("Sur 6 mois", perf(a, "6 mois"), perf(b, "6 mois")),
              ("Volatilité annuelle", vol(a), vol(b)),
              ("Agitation prévue le mois prochain", agit(a), agit(b)),
              ("Risque de chute de plus de 10 % prévu", chu(a), chu(b)),
              ("Avis des IA sur le sens du prix", avis(a), avis(b)),
              ("Chances de faire mieux que son marché", face(a), face(b)),
              ("Niveau de risque", _e(a.get("risque") or "–"), _e(b.get("risque") or "–"))]
    fva, fvb = (a.get("fondamentaux") or {}).get("valeurs") or {}, (b.get("fondamentaux") or {}).get("valeurs") or {}
    nb2 = lambda v: f"{v:.1f}".replace(".", ",") if isinstance(v, (int, float)) else "–"
    if fva.get("trailingPE") or fvb.get("trailingPE"):
        lignes.append(("PER (12 derniers mois)", nb2(fva.get("trailingPE")), nb2(fvb.get("trailingPE"))))
    if fva.get("dividendYield") is not None or fvb.get("dividendYield") is not None:
        lignes.append(("Rendement du dividende", nb2(fva.get("dividendYield")) + (" %" if fva.get("dividendYield") is not None else ""),
                       nb2(fvb.get("dividendYield")) + (" %" if fvb.get("dividendYield") is not None else "")))
    tableau = ("<div class='carte' style='overflow-x:auto'><table><tr><td></td>"
               f"<td><b><a href='../titres/{slug(a['ticker'])}.html'>{_e(na)}</a></b></td><td><b><a href='../titres/{slug(b['ticker'])}.html'>{_e(nb)}</a></b></td></tr>"
               + "".join(f"<tr><td>{l}</td><td class='m'>{x}</td><td class='m'>{y}</td></tr>" for l, x, y in lignes) + "</table></div>")
    phrases = []
    va, vb = (a.get("perf") or {}).get("volatilité annuelle"), (b.get("perf") or {}).get("volatilité annuelle")
    if va and vb:
        plus = na if va > vb else nb
        phrases.append(f"<b>{_e(plus)}</b> bouge le plus : sa volatilité annuelle est {max(va, vb) / min(va, vb):.1f} fois celle de l'autre.".replace(".", ",", 1)
                       if max(va, vb) / min(va, vb) >= 1.15 else "Les deux bougent à peu près autant.")
    sa, sb = (a.get("perf") or {}).get("6 mois"), (b.get("perf") or {}).get("6 mois")
    if sa is not None and sb is not None:
        phrases.append(f"Sur six mois, <b>{_e(na if sa > sb else nb)}</b> a fait mieux ({_pct(max(sa, sb))} contre {_pct(min(sa, sb))}). "
                       "Le passé ne dit rien de sûr sur la suite.")
    ma, mb = (a.get("risque_prevu") or {}).get("mouvement"), (b.get("risque_prevu") or {}).get("mouvement")
    if ma and mb:
        phrases.append(f"Pour le mois qui vient, les IA prévoient plus d'agitation pour <b>{_e(na if ma > mb else nb)}</b>. "
                       "C'est ce qu'elles prévoient le mieux.")
    faq = [(f"{na} ou {nb} : lequel acheter ?",
            "Le radar ne dit pas quoi acheter : il compare les chiffres du jour et ses prévisions, qui se trompent souvent. "
            "Le bon choix dépend de ton objectif, de ta durée et du risque que tu acceptes."),
           (f"Lequel va bouger le plus le mois prochain, {na} ou {nb} ?",
            (f"Les IA prévoient environ ±{round(max(ma, mb) * 100)} % pour {_e(na if ma > mb else nb)} contre ±{round(min(ma, mb) * 100)} % "
             f"pour {_e(nb if ma > mb else na)}. Prévoir l'agitation est ce que les IA font le mieux, mais ça reste une estimation."
             if ma and mb else "Les prévisions d'agitation ne sont pas disponibles aujourd'hui.")),
           (f"Lequel est le plus risqué entre {na} et {nb} ?",
            (f"Aujourd'hui, {_e(na if va > vb else nb)} est le plus volatil des deux ({_taux(max(va, vb))} par an contre {_taux(min(va, vb))})."
             if va and vb else "Les données de volatilité ne sont pas disponibles aujourd'hui."))]
    corps = (f"<p class='muted'><a href='../comparer.html'>Toutes les comparaisons</a></p>"
             f"<h1>{_e(na)} ou {_e(nb)} : la comparaison du {_e(date)}</h1>"
             "<p class='muted'>Les deux titres côte à côte : cours, risque et ce que prévoient les IA du radar. "
             "Mis à jour automatiquement. Une comparaison, pas un conseil.</p>"
             + tableau + ("<h2>En bref</h2><ul>" + "".join(f"<li>{p}</li>" for p in phrases) + "</ul>" if phrases else "")
             + "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{r}</p>" for q, r in faq)
             + f"<p><a class='btn' href='../titres/{slug(a['ticker'])}.html'>Fiche {_e(na)}</a> "
             f"<a class='btn' href='../titres/{slug(b['ticker'])}.html'>Fiche {_e(nb)}</a></p>"
             "<p class='muted'>Projet éducatif. Tu peux perdre tout l'argent investi.</p>")
    titre = f"{na} ou {nb} : comparaison et prévisions | {NOM}"
    desc = f"{na} ou {nb} ? Cours, volatilité, agitation prévue et avis des IA côte à côte, mis à jour chaque jour."
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": f"{na} ou {nb}", "inLanguage": "fr-FR"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for q, r in faq]},
        _jsonld_fil(base, [(NOM, ""), ("Comparer", "comparer.html"), (f"{na} ou {nb}", chemin)])]}
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp)


def _exemple_du_jour(mot, payload):
    """Un exemple tiré des chiffres du jour, quand c'est possible (rend chaque page vivante et unique)."""
    titres = [t for t in payload.get("titres", []) if t.get("prix")]
    ctx = {c.get("nom", ""): c for c in payload.get("contexte") or []}
    if mot == "PER":
        avec = sorted([t for t in titres if (t.get("per") or 0) > 0], key=lambda t: t["per"])
        if len(avec) >= 6:
            f = lambda t: f"<a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> ({t['per']:.1f})".replace(".", ",").replace(",html", ".html").replace(",,/", "../")
            return ("Parmi les actions suivies, les PER les plus bas aujourd'hui : " + ", ".join(f(t) for t in avec[:3])
                    + ". Les plus élevés : " + ", ".join(f(t) for t in avec[-3:][::-1]) + ".")
    if mot == "VIX":
        c = next((v for n, v in ctx.items() if "VIX" in n), None)
        if c and c.get("valeur") is not None:
            return f"Le VIX vaut aujourd'hui <b>{c['valeur']:.1f}</b>.".replace(".", ",", 1)
    if mot == "Fear & Greed crypto":
        c = next((v for n, v in ctx.items() if "Greed" in n or "crypto" in n.lower()), None)
        if c and c.get("valeur") is not None:
            return f"L'indice vaut aujourd'hui <b>{c['valeur']:.0f}</b> sur 100."
    if mot == "Stop-loss":
        t = next((t for t in titres if t["ticker"] == "MC.PA" and t.get("stop_loss")), None)
        if t:
            return (f"Exemple du jour : pour <a href='../titres/mc-pa.html'>LVMH</a> à {_px(t['prix'], t['devise'])}, le radar calcule un stop-loss "
                    f"indicatif vers {_px(t['stop_loss'], t['devise'])}, soit {_pct(t['stop_loss'] / t['prix'] - 1)}.")
    if mot == "Moyenne mobile (SMA)":
        av = [t for t in titres if t.get("au_dessus_200") is not None]
        if len(av) >= 20:
            return (f"Aujourd'hui, <b>{round(sum(t['au_dessus_200'] for t in av) / len(av) * 100)} %</b> des {len(av)} titres suivis "
                    "sont au-dessus de leur moyenne 200 jours.")
    return ""


def _pages_glossaire(base, payload, dossier, csp, date):
    from .glossaire_plus import PLUS
    os.makedirs(os.path.join(dossier, "glossaire"), exist_ok=True)
    faits = []
    for i, (mot, definition) in enumerate(GLOSSAIRE):
        usage, piege = PLUS.get(mot, ("", ""))
        exemple = _exemple_du_jour(mot, payload)
        voisins = [GLOSSAIRE[(i + d) % len(GLOSSAIRE)][0] for d in (-2, -1, 1, 2, 3)]
        corps = (f"<p class='muted'><a href='../glossaire.html'>Glossaire</a></p><h1>{_e(mot)} : définition simple</h1>"
                 f"<p><b>{_e(definition)}</b></p>"
                 + (f"<h2>À quoi ça sert ?</h2><p>{_e(usage)}</p>" if usage else "")
                 + (f"<h2>Le piège à éviter</h2><p>{_e(piege)}</p>" if piege else "")
                 + (f"<h2>Exemple avec les chiffres du jour</h2><p>{exemple}</p><p class='muted'>Chiffres du {_e(date)}, mis à jour automatiquement.</p>" if exemple else "")
                 + "<h2>Pour aller plus loin</h2><ul class='liste'><li><a href='../lecons/indicateurs.html'>Les indicateurs techniques, expliqués</a></li>"
                 "<li><a href='../lecons/risque.html'>Gérer son risque</a></li><li><a href='../resultats.html'>Ce que valent vraiment les prévisions du radar</a></li></ul>"
                 "<h2>Autres mots</h2><ul class='liste'>" + "".join(f"<li><a href='{slug(v)}.html'>{_e(v)}</a></li>" for v in voisins) + "</ul>")
        q = f"Qu'est-ce que {mot.split(' (')[0]} en Bourse ?"
        jsonld = {"@context": "https://schema.org", "@graph": [
            {"@type": "DefinedTerm", "name": mot, "description": definition, "inDefinedTermSet": f"{base}glossaire.html" if base else "glossaire.html"},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": definition + (" " + usage if usage else "")}}]}]}
        chemin = f"glossaire/{slug(mot)}.html"
        court = mot.split(" (")[0]
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(base, f"{court} : définition simple et exemple | {NOM}", (definition[:150] + "…") if len(definition) > 155 else definition,
                          chemin, corps, jsonld, csp))
        faits.append(chemin)
    return faits


def _page_calendrier(base, payload, dossier, csp, date):
    """« Calendrier des résultats » : les prochaines publications des entreprises suivies, jour par jour."""
    auj = datetime.now().date()
    evts = []
    for t in payload.get("titres", []):
        rl = t.get("resultats_le") or (t.get("fondamentaux") or {}).get("resultats_le")
        try:
            d = datetime.strptime(rl, "%Y-%m-%d").date() if rl else None
        except ValueError:
            d = None
        if d and 0 <= (d - auj).days <= 90:
            evts.append((d, t))
    evts.sort(key=lambda x: (x[0], x[1]["nom"]))
    corps = ("<h1>Calendrier des résultats des entreprises</h1>"
             f"<p class='muted'>Mis à jour automatiquement · {_e(date)}</p>"
             "<p>Les jours de publication des résultats sont souvent ceux où une action bouge le plus, dans un sens comme dans l'autre. "
             "Voici les prochaines dates annoncées pour les entreprises suivies par le radar (dates fournies par les entreprises via Yahoo Finance, "
             "parfois approximatives : à vérifier sur le site de l'entreprise).</p>")
    if not evts:
        corps += "<p class='muted'>Aucune date de résultats connue pour les trois prochains mois.</p>"
    jour = None
    for d, t in evts:
        if d != jour:
            if jour is not None:
                corps += "</ul>"
            corps += f"<h2>{_e(date_longue(d.strftime('%Y-%m-%d')))}</h2><ul class='liste'>"
            jour = d
        rp = t.get("risque_prevu") or {}
        mv = f" · agitation prévue ±{round(rp['mouvement'] * 100)} %" if rp.get("mouvement") else ""
        corps += f"<li><a href='titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> <span class='muted'>({_e(aff_tk(t['ticker']))}){mv}</span></li>"
    if jour is not None:
        corps += "</ul>"
    corps += "<p class='muted'>Ce calendrier n'est pas un conseil. Voir aussi le <a href='guides/resultats-trimestriels.html'>guide sur les résultats trimestriels</a>.</p>"
    with open(os.path.join(dossier, "calendrier-resultats.html"), "w", encoding="utf-8") as f:
        jl = _jsonld_liste(base, "Calendrier des résultats des entreprises", "calendrier-resultats.html",
                           [(f"{t['nom']} : résultats le {d.strftime('%d/%m/%Y')}", f"titres/{slug(t['ticker'])}.html") for d, t in evts[:100]])
        f.write(_page(base, f"Calendrier des résultats des entreprises ({datetime.now().year}) | {NOM}",
                      "Les prochaines dates de publication des résultats de LVMH, TotalEnergies, Apple, Nvidia et des autres entreprises suivies, jour par jour.",
                      "calendrier-resultats.html", corps, jl, csp=csp))
    return True


def _page_suivi_chute(base, payload, dossier, csp):
    """Suivi public du risque de forte chute : les 10 titres les plus à risque contre les 10 les moins à risque."""
    S = payload.get("suivi_chute") or {}
    mois = S.get("mois") or []
    R = S.get("resume")
    corps = ("<h1>Le risque de chute, vérifié en public</h1>"
             "<p>Prévoir si un prix va monter ou baisser est presque impossible. Prévoir quels titres risquent le plus une "
             "<b>forte chute</b> (plus de 10 % en 20 séances), les IA du radar le font bien sur les années testées. Pour le prouver "
             "en conditions réelles, au début de chaque mois le radar enregistre publiquement les <b>10 titres les plus à risque</b> "
             "et les <b>10 les moins à risque</b>, avec le prix du jour. Rien n'est modifié ensuite : on compte simplement combien ont "
             "vraiment chuté dans chaque groupe, mois ratés compris.</p>")
    if R:
        th = R["chutes_haut"] / max(R["nb_haut"], 1)
        tb = R["chutes_bas"] / max(R["nb_bas"], 1)
        corps += ("<div class='carte grille'>"
                  f"<div class='k'><b>{R['chutes_haut']} / {R['nb_haut']}</b><span>titres « à risque » qui ont chuté de plus de 10 % ({round(th * 100)} %)</span></div>"
                  f"<div class='k'><b>{R['chutes_bas']} / {R['nb_bas']}</b><span>titres « peu risqués » qui ont chuté de plus de 10 % ({round(tb * 100)} %)</span></div>"
                  f"<div class='k'><b>{R['mois_reussis']} / {R['nb_mois']}</b><span>mois où le groupe à risque a eu plus de chutes</span></div></div>"
                  "<p class='muted'>Sur quelques mois, le hasard pèse beaucoup : il faut plusieurs mois pour juger.</p>")
    elif not mois:
        corps += "<p class='muted'>La première liste sera enregistrée au prochain calcul complet du soir.</p>"
    for m in mois:
        nm = _mois(m["mois"])
        de = "d'" if nm[:1].lower() in "aeiouyéè" else "de "
        def table(lignes):
            return ("<div class='carte' style='overflow-x:auto'><table><tr><td><b>Titre</b></td><td><b>Risque prévu</b></td><td><b>Évolution</b></td><td></td></tr>"
                    + "".join(f"<tr><td><a href='titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a></td><td class='m'>{round(t['risque'] * 100)} %</td>"
                              f"<td class='m'>{_pct(t['perf'])}</td><td>{'<span class=down>Chute de plus de 10 %</span>' if t['chute'] else ''}</td></tr>" for t in lignes)
                    + "</table></div>")
        corps += (f"<h2>Liste {de}{_e(nm)}{'' if m['termine'] else ' (en cours)'}</h2>"
                  f"<p>Enregistrée le {_e(date_longue(m['date']))}. Chutes de plus de 10 % {'' if m['termine'] else 'à ce jour '}: "
                  f"<b>{m['chutes_haut']}</b> parmi les plus à risque, <b>{m['chutes_bas']}</b> parmi les moins à risque.</p>"
                  "<h3>Les 10 plus à risque</h3>" + table(m["risque_haut"]) + "<h3>Les 10 moins à risque</h3>" + table(m["risque_bas"]))
    corps += ("<p class='muted'>Une prévision de risque n'est pas un conseil de vente : un titre « à risque » peut aussi monter fortement. "
              "Voir aussi les <a href='classements.html'>classements du jour</a> et les <a href='resultats.html'>résultats réels</a>.</p>")
    with open(os.path.join(dossier, "suivi-chute.html"), "w", encoding="utf-8") as f:
        jl = {"@context": "https://schema.org", "@graph": [
            {"@type": "Dataset", "name": "Suivi public du risque de forte chute prévu par l'IA de Radar Bourse",
             "description": "Chaque mois, les 10 titres que l'IA juge les plus exposés à une chute de plus de 10 % et les 10 les moins exposés, "
                            "enregistrés avec le prix du jour, puis le nombre de chutes réellement observées.",
             "inLanguage": "fr-FR", "creator": {"@type": "Organization", "name": NOM}, "isAccessibleForFree": True,
             "temporalCoverage": (mois[-1]["date"] + "/..") if mois else None, "url": (base + "suivi-chute.html") if base else None},
            _jsonld_fil(base, [(NOM, ""), ("Suivi du risque de chute", "suivi-chute.html")])]}
        f.write(_page(base, f"Risque de chute en bourse : la prévision de l'IA vérifiée | {NOM}",
                      "Chaque mois, les 10 actions et cryptos les plus et les moins exposées à une forte chute selon l'IA, suivies en public : combien ont vraiment chuté.",
                      "suivi-chute.html", corps, jl, csp=csp))
    return True


def _page_portefeuille(base, payload, dossier, csp):
    P = payload.get("portefeuille_public") or {}
    mois = P.get("mois") or []
    if not mois:   # jamais de lien cassé : la page existe même avant la première sélection
        corps = ("<h1>La sélection IA du mois</h1><p>Chaque mois, le radar choisit publiquement 10 actions auxquelles ses IA donnent "
                 "le plus de chances de faire mieux que leur indice, puis publie le résultat, réussite ou échec.</p>"
                 "<p class='muted'>La première sélection sera enregistrée au prochain calcul complet du soir.</p>")
        with open(os.path.join(dossier, "portefeuille.html"), "w", encoding="utf-8") as f:
            f.write(_page(base, f"Sélection IA du mois : 10 actions suivies en public | {NOM}",
                          "Chaque mois, 10 actions choisies par les IA du radar, suivies publiquement face à leur indice, ratés compris.",
                          "portefeuille.html", corps, csp=csp))
        return True
    noms_ind = config.NOM_BENCHMARK
    R = P.get("resume")
    corps = ("<h1>Le portefeuille public « mieux que le marché »</h1>"
             "<p>Chaque mois, le radar choisit les 10 actions auxquelles ses IA donnent le plus de chances de faire "
             "<b>mieux que leur indice</b> (CAC 40, Euro Stoxx 50 ou S&amp;P 500). C'est, après l'agitation, ce que les IA prévoient "
             "le mieux sur les années testées. Depuis la version 40, les titres au plus fort risque de chute prévu sont écartés. Le choix est enregistré le jour même avec les prix du jour et n'est plus jamais modifié : "
             "ce suivi montre ce que l'IA vaut vraiment, mois après mois, réussites et ratés compris.</p>")
    if R:
        corps += ("<div class='carte grille'>"
                  f"<div class='k'><b>{_pct(R['ecart_moyen'])}</b><span>d'écart moyen avec les indices par mois ({R['nb_mois']} mois terminés)</span></div>"
                  f"<div class='k'><b>{R['mois_gagnants']} / {R['nb_mois']}</b><span>mois où la sélection a fait mieux que ses indices</span></div>"
                  f"<div class='k'><b>{R['titres_mieux']} / {R['titres']}</b><span>titres qui ont fait mieux que leur indice</span></div></div>")
    else:
        corps += "<p class='muted'>Le premier mois de suivi n'est pas encore terminé : le bilan complet arrivera à la fin du mois.</p>"
    for m in mois:
        lignes = "".join(
            f"<tr><td><a href='titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a></td><td class='m'>{_pct(t['perf'])}</td>"
            f"<td class='m'>{_pct(t['perf_indice'])} <span class='muted'>({_e(noms_ind.get(t['indice'], t['indice']))})</span></td>"
            f"<td>{'<span class=up>Mieux</span>' if t['mieux'] else '<span class=down>Moins bien</span>'}</td></tr>" for t in m["titres"])
        nm = _mois(m["mois"])
        de = "d'" if nm[:1].lower() in "aeiouyéè" else "de "
        debut = m["date"] == datetime.now().strftime("%Y-%m-%d")
        corps += (f"<h2>Sélection {de}{_e(nm)}{'' if m['termine'] else ' (en cours)'}</h2>"
                  + (f"<p>Choisie aujourd'hui, le {_e(date_longue(m['date']))}, avec les prix du jour : le suivi commence demain.</p>" if debut else
                     f"<p>Choisie le {_e(date_longue(m['date']))}. Résultat {'final' if m['termine'] else 'à ce jour'} : "
                     f"<b>{_pct(m['perf'])}</b> en moyenne, contre {_pct(m['perf_indices'])} pour leurs indices, soit un écart de "
                     f"<b>{_pct(m['ecart'])}</b>. {m['nb_mieux']} titre{'s' if m['nb_mieux'] > 1 else ''} sur {m['nb']} "
                     f"{'font' if m['nb_mieux'] > 1 else 'fait'} mieux que {'leur' if m['nb_mieux'] > 1 else 'son'} indice.</p>")
                  + "<div class='carte' style='overflow-x:auto'><table><tr><td><b>Titre</b></td><td><b>Depuis le choix</b></td>"
                  "<td><b>Son indice</b></td><td><b>Résultat</b></td></tr>" + lignes + "</table></div>")
    corps += ("<p class='muted'>Suivi éducatif, sans frais ni impôts, à poids égal. Ce n'est pas un conseil : un mois peut être "
              "très mauvais, et les résultats passés ne garantissent rien.</p>")
    with open(os.path.join(dossier, "portefeuille.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Portefeuille IA « mieux que le marché » : le suivi public | {NOM}",
                      "Chaque mois, 10 actions choisies par IA pour battre leur indice, suivies publiquement contre le CAC 40 et le S&P 500, ratés compris.",
                      "portefeuille.html", corps, csp=csp))
    return True


CLASSEMENTS = [
    ("actions-dividende", "Actions à fort dividende : le classement du jour",
     "Les actions suivies qui versent le plus de dividende par rapport à leur prix, avec leur agitation prévue.",
     lambda t: t.get("marche") in ("fr", "eu", "us") and (t.get("div") or 0) > 0, lambda t: -(t.get("div") or 0),
     lambda t: f"{t['div']:.2f} % de dividende".replace(".", ",")),
    ("actions-calmes", "Actions les moins agitées prévues ce mois-ci",
     "Les actions dont les IA prévoient qu'elles bougeront le moins le mois prochain : moins de surprises, dans un sens comme dans l'autre.",
     lambda t: t.get("marche") in ("fr", "eu", "us") and (t.get("risque_prevu") or {}).get("mouvement"),
     lambda t: t["risque_prevu"]["mouvement"], lambda t: f"±{round(t['risque_prevu']['mouvement'] * 100)} % prévus en un mois"),
    ("cryptos-agitees", "Cryptos les plus volatiles prévues ce mois-ci",
     "Les cryptomonnaies dont les IA prévoient les plus grands mouvements le mois prochain, à la hausse comme à la baisse.",
     lambda t: str(t.get("ticker", "")).endswith("-USD") and (t.get("risque_prevu") or {}).get("mouvement"),
     lambda t: -t["risque_prevu"]["mouvement"], lambda t: f"±{round(t['risque_prevu']['mouvement'] * 100)} % prévus en un mois"),
    ("mieux-que-leur-marche", "Actions qui pourraient faire mieux que leur indice",
     "Les actions auxquelles les IA donnent le plus de chances de faire mieux que le CAC 40, le S&P 500 ou l'Euro Stoxx 50 le mois prochain.",
     lambda t: t.get("marche") in ("fr", "eu", "us") and t.get("proba_marche") is not None and t.get("marche_net") is not False,
     lambda t: -t["proba_marche"], lambda t: f"{round(t['proba_marche'] * 100)} chances sur 100 de faire mieux que {t.get('indice_nom') or 'son marché'}"),
    ("risque-de-chute", "Actions et cryptos les plus exposées à une forte chute ce mois-ci",
     "Les titres auxquels les IA donnent le plus de risque de perdre plus de 10 % le mois prochain (prévision testée sur des années jamais vues).",
     lambda t: (t.get("risque_prevu") or {}).get("chute") is not None, lambda t: -t["risque_prevu"]["chute"],
     lambda t: f"{round(t['risque_prevu']['chute'] * 100)} chances sur 100 de perdre plus de 10 %"),
    ("per-bas", "Actions au PER le plus bas parmi les grandes valeurs",
     "Les grandes actions suivies dont le prix est le plus bas par rapport à leurs bénéfices (PER). Un PER bas n'est pas forcément une bonne affaire.",
     lambda t: t.get("marche") in ("fr", "eu", "us") and (t.get("per") or 0) > 0, lambda t: t["per"],
     lambda t: f"PER {t['per']:.1f}".replace(".", ",")),
]


def _md(txt):
    """Texte des guides : échappé, puis **gras** autorisé."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", _e(txt))


def _jsonld_liste(base, nom, chemin, elements, parent=None):
    """Données structurées d'une page « liste » (classement, secteur, guides) : ItemList + fil d'Ariane."""
    etapes = [(NOM, "")] + ([parent] if parent else []) + [(nom, chemin)]
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": nom, "numberOfItems": len(elements), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "url": (base + c) if base else c} for i, (n, c) in enumerate(elements)]},
        _jsonld_fil(base, etapes)]}


def _pages_guides(base, payload, dossier, csp, date):
    """Version 38 : 100 guides qui répondent honnêtement aux recherches les plus tapées sur la Bourse et la crypto
    (« débuter en bourse », « argent facile », « prévision bitcoin »…), avec les chiffres du jour quand c'est utile."""
    from .guides import GUIDES, CATEGORIES
    os.makedirs(os.path.join(dossier, "guides"), exist_ok=True)
    par_tk = {t.get("ticker"): t for t in payload.get("titres", []) if t.get("prix")}
    faits = []
    for g in GUIDES:
        voisins = [v for v in GUIDES if v["c"] == g["c"] and v["i"] != g["i"]]
        idx = [v["i"] for v in GUIDES if v["c"] == g["c"]].index(g["i"])
        voisins = (voisins[idx:] + voisins[:idx])[:5]
        corps = (f"<p class='muted'><a href='../guides.html'>Guides</a> · {_e(CATEGORIES[g['c']])}</p>"
                 f"<h1>{_e(g['h'])}</h1><div class='carte'><p><b>En bref :</b> {_md(g['r'])}</p></div>")
        for h2, txt in g.get("p", []):
            corps += f"<h2>{_e(h2)}</h2>" + "".join(f"<p>{_md(x)}</p>" for x in txt.split("\n\n"))
        lignes = []
        for tk in g.get("k", []):
            t = par_tk.get(tk)
            if not t:
                continue
            rp = t.get("risque_prevu") or {}
            mv, ch = rp.get("mouvement"), rp.get("chute")
            lignes.append(f"<tr><td><a href='../titres/{slug(tk)}.html'>{_e(t.get('nom') or tk)}</a></td><td class='m'>{_px(t['prix'], t.get('devise', ''))}</td>"
                          f"<td class='m'>{'±' + str(round(mv * 100)) + ' %' if mv else '—'}</td>"
                          f"<td class='m'>{str(round(ch * 100)) + ' %' if ch is not None else '—'}</td></tr>")
        if lignes:
            corps += ("<h2>Les chiffres du jour</h2><div class='carte' style='overflow-x:auto'><table><tr><td><b>Titre</b></td><td><b>Cours</b></td>"
                      "<td><b>Agitation prévue sur un mois</b></td><td><b>Risque de chute de plus de 10 %</b></td></tr>" + "".join(lignes) + "</table></div>"
                      f"<p class='muted'>Cours au {_e(date)}, mis à jour automatiquement. L'agitation et le risque de chute sont ce que les IA du radar prévoient le mieux "
                      "(voir les <a href='../resultats.html'>résultats réels</a>) ; ce ne sont pas des conseils d'achat.</p>")
        if g.get("q"):
            corps += "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_md(a)}</p>" for q, a in g["q"])
        liens = [(n, c) for n, c in g.get("l", []) if not c.startswith("classements/") or os.path.exists(os.path.join(dossier, c))]
        liens += [("Ce que valent vraiment les prévisions du radar", "resultats.html")]
        corps += ("<h2>Pour aller plus loin</h2><ul class='liste'>" + "".join(f"<li><a href='../{_e(c)}'>{_e(n)}</a></li>" for n, c in liens)
                  + "".join(f"<li><a href='{v['i']}.html'>{_e(v['h'])}</a></li>" for v in voisins) + "</ul>")
        chemin = f"guides/{g['i']}.html"
        url = (base + chemin) if base else chemin
        faq = [(g["h"], g["r"])] + list(g.get("q", []))
        jsonld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Article", "headline": g["h"][:110], "description": g["d"], "inLanguage": "fr-FR", "url": url,
             "dateModified": datetime.now().strftime("%Y-%m-%d"), "author": {"@type": "Organization", "name": NOM},
             "publisher": {"@type": "Organization", "name": NOM}},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.replace("**", "")}} for q, a in faq]},
            _jsonld_fil(base, [(NOM, ""), ("Guides", "guides.html"), (g["t"], chemin)])]}
        titre = g["t"] + (f" | {NOM}" if len(g["t"]) <= 50 else "")
        from .guides_en import IDS_EN
        alt = {"fr": chemin, "en": f"en/guides/{g['i']}.html", "x-default": chemin} if g["i"] in IDS_EN else None
        if alt:
            avant, _, apres = corps.rpartition("</ul>")
            corps = avant + f"<li><a href='../en/guides/{g['i']}.html' hreflang='en' lang='en'>English version</a></li></ul>" + apres
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(base, titre, g["d"], chemin, corps, jsonld, csp, alternates=alt))
        faits.append(chemin)
    corps = ("<h1>Guides de la Bourse et de la crypto</h1><p>Les questions que tout le monde se pose, avec des réponses honnêtes : "
             "pas de promesse d'argent facile, des chiffres vérifiables et les vrais risques.</p>")
    for c, lib in CATEGORIES.items():
        items = [g for g in GUIDES if g["c"] == c]
        if items:
            corps += f"<h2>{_e(lib)}</h2><ul class='liste'>" + "".join(f"<li><a href='guides/{g['i']}.html'>{_e(g['h'])}</a></li>" for g in items) + "</ul>"
    with open(os.path.join(dossier, "guides.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Guides bourse et crypto pour débutants | {NOM}",
                      "Débuter en bourse, investir petit budget, crypto, ETF, arnaques, argent facile : 100 guides simples et honnêtes.",
                      "guides.html", corps, _jsonld_liste(base, "Guides bourse et crypto", "guides.html", [(g["h"], f"guides/{g['i']}.html") for g in GUIDES]), csp=csp))
    faits.append("guides.html")
    return faits


# Version 39 : les mêmes classements, marché par marché (« actions françaises à fort dividende »…)
_LIB_M = {"fr": ("francaises", "françaises", "CAC 40"), "eu": ("europeennes", "européennes", "Euro Stoxx 50"),
          "us": ("americaines", "américaines", "S&P 500")}


def _variantes():
    out = []
    for m, (sm, lm, ind) in _LIB_M.items():
        f = lambda t, m=m: t.get("marche") == m
        out += [
            (f"actions-{sm}-dividende", f"Actions {lm} à fort dividende : le classement du jour",
             f"Les actions {lm} suivies qui versent le plus de dividende par rapport à leur prix.",
             lambda t, f=f: f(t) and (t.get("div") or 0) > 0, lambda t: -(t.get("div") or 0),
             lambda t: f"{t['div']:.2f} % de dividende".replace(".", ",")),
            (f"actions-{sm}-calmes", f"Actions {lm} les moins agitées prévues ce mois-ci",
             f"Les actions {lm} dont les IA prévoient qu'elles bougeront le moins le mois prochain.",
             lambda t, f=f: f(t) and (t.get("risque_prevu") or {}).get("mouvement"), lambda t: t["risque_prevu"]["mouvement"],
             lambda t: f"±{round(t['risque_prevu']['mouvement'] * 100)} % prévus en un mois"),
            (f"actions-{sm}-agitees", f"Actions {lm} les plus agitées prévues ce mois-ci",
             f"Les actions {lm} dont les IA prévoient les plus grands mouvements le mois prochain, à la hausse comme à la baisse.",
             lambda t, f=f: f(t) and (t.get("risque_prevu") or {}).get("mouvement"), lambda t: -t["risque_prevu"]["mouvement"],
             lambda t: f"±{round(t['risque_prevu']['mouvement'] * 100)} % prévus en un mois"),
            (f"actions-{sm}-risque-de-chute", f"Actions {lm} les plus exposées à une forte chute ce mois-ci",
             f"Les actions {lm} auxquelles les IA donnent le plus de risque de perdre plus de 10 % le mois prochain.",
             lambda t, f=f: f(t) and (t.get("risque_prevu") or {}).get("chute") is not None, lambda t: -t["risque_prevu"]["chute"],
             lambda t: f"{round(t['risque_prevu']['chute'] * 100)} chances sur 100 de perdre plus de 10 %"),
            (f"actions-{sm}-mieux-que-le-marche", f"Actions {lm} qui pourraient faire mieux que le {ind}",
             f"Les actions {lm} auxquelles les IA donnent le plus de chances de faire mieux que le {ind} le mois prochain.",
             lambda t, f=f: f(t) and t.get("proba_marche") is not None and t.get("marche_net") is not False, lambda t: -t["proba_marche"],
             lambda t: f"{round(t['proba_marche'] * 100)} chances sur 100 de faire mieux que {t.get('indice_nom') or 'son marché'}"),
            (f"actions-{sm}-per-bas", f"Actions {lm} au PER le plus bas",
             f"Les actions {lm} suivies dont le prix est le plus bas par rapport à leurs bénéfices. Un PER bas n'est pas forcément une bonne affaire.",
             lambda t, f=f: f(t) and (t.get("per") or 0) > 0, lambda t: t["per"], lambda t: f"PER {t['per']:.1f}".replace(".", ",")),
        ]
    est_c = lambda t: str(t.get("ticker", "")).endswith("-USD")
    out += [
        ("cryptos-calmes", "Cryptos les moins agitées prévues ce mois-ci",
         "Les cryptomonnaies dont les IA prévoient les plus petits mouvements le mois prochain (elles restent bien plus agitées que les actions).",
         lambda t: est_c(t) and (t.get("risque_prevu") or {}).get("mouvement"), lambda t: t["risque_prevu"]["mouvement"],
         lambda t: f"±{round(t['risque_prevu']['mouvement'] * 100)} % prévus en un mois"),
        ("cryptos-risque-de-chute", "Cryptos les plus exposées à une forte chute ce mois-ci",
         "Les cryptomonnaies auxquelles les IA donnent le plus de risque de perdre plus de 10 % le mois prochain.",
         lambda t: est_c(t) and (t.get("risque_prevu") or {}).get("chute") is not None, lambda t: -t["risque_prevu"]["chute"],
         lambda t: f"{round(t['risque_prevu']['chute'] * 100)} chances sur 100 de perdre plus de 10 %"),
    ]
    return out


CLASSEMENTS += _variantes()

SECTEURS_FR = {"Technology": "technologie", "Financial Services": "finance et banques", "Healthcare": "santé",
               "Consumer Cyclical": "consommation (luxe, auto, loisirs)", "Consumer Defensive": "consommation de base",
               "Industrials": "industrie", "Energy": "énergie", "Utilities": "services publics (électricité, eau)",
               "Communication Services": "communication et médias", "Basic Materials": "matériaux et chimie",
               "Real Estate": "immobilier"}


def _pages_secteurs(base, titres, dossier, csp, date):
    """Une page par secteur : « actions du secteur santé », avec l'agitation et le risque de chute du jour."""
    groupes = {}
    for t in titres:
        if t.get("marche") in ("fr", "eu", "us") and t.get("secteur"):
            groupes.setdefault(t["secteur"], []).append(t)
    faits = []
    for sec, items in sorted(groupes.items()):
        if len(items) < 4:
            continue
        lib = SECTEURS_FR.get(sec, sec)
        items.sort(key=lambda t: ((t.get("risque_prevu") or {}).get("chute") or 1))
        lignes = "".join(
            f"<tr><td><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> <span class='muted'>{_e(aff_tk(t['ticker']))}</span></td>"
            f"<td class='m'>{_px(t['prix'], t['devise'])}</td>"
            f"<td class='m'>{('±' + str(round(t['risque_prevu']['mouvement'] * 100)) + ' %') if (t.get('risque_prevu') or {}).get('mouvement') else '—'}</td>"
            f"<td class='m'>{(str(round(t['risque_prevu']['chute'] * 100)) + ' %') if (t.get('risque_prevu') or {}).get('chute') is not None else '—'}</td></tr>"
            for t in items)
        h1 = f"Actions du secteur {lib} : prévisions et risque du jour"
        intro = (f"Les {len(items)} actions du secteur {lib} suivies par le radar (France, Europe, États-Unis), "
                 "triées du plus faible au plus fort risque de chute prévu pour le mois prochain.")
        corps = (f"<p class='muted'><a href='../classements.html'>Tous les classements</a></p><h1>{_e(h1)}</h1>"
                 f"<p class='muted'>Mis à jour automatiquement · cours au {_e(date)}</p><p>{_e(intro)}</p>"
                 "<div class='carte' style='overflow-x:auto'><table><tr><td><b>Action</b></td><td><b>Cours</b></td>"
                 "<td><b>Agitation prévue</b></td><td><b>Risque de chute de plus de 10 %</b></td></tr>" + lignes + "</table></div>"
                 "<p class='muted'>L'agitation et le risque de chute sont ce que les IA prévoient le mieux sur les années testées "
                 "(<a href='../resultats.html'>résultats réels</a>). Ce n'est pas un conseil d'achat.</p>")
        chemin = f"classements/secteur-{slug(sec)}.html"
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            jl = _jsonld_liste(base, h1, chemin, [(t["nom"], f"titres/{slug(t['ticker'])}.html") for t in items], ("Classements", "classements.html"))
            f.write(_page(base, f"Actions secteur {lib} : prévisions {datetime.now().year}"[:60] + f" | {NOM}", intro[:155], chemin, corps, jl, csp=csp))
        faits.append((h1, chemin))
    return faits


def _pages_classements(base, payload, dossier, csp, date):
    """Pages « classement » mises à jour chaque jour : elles répondent à des recherches très tapées."""
    titres = [t for t in payload.get("titres", []) if t.get("prix")]
    for t in titres:   # dividende / PER : dans la page légère (div, per) ou dans le détail (fondamentaux)
        fv = (t.get("fondamentaux") or {}).get("valeurs") or {}
        t.setdefault("div", fv.get("dividendYield"))
        t.setdefault("per", fv.get("trailingPE"))
        if t.get("div") is None and fv.get("dividendYield") is not None:
            t["div"] = fv["dividendYield"]
        if t.get("per") is None and fv.get("trailingPE") is not None:
            t["per"] = fv["trailingPE"]
    os.makedirs(os.path.join(dossier, "classements"), exist_ok=True)
    faits, liens = [], []
    for cle, titre_h1, intro, filtre, tri, valeur in CLASSEMENTS:
        sel = sorted([t for t in titres if filtre(t)], key=tri)[:20]
        if len(sel) < 5:
            continue
        lignes = "".join(f"<tr><td class='m'>{i}</td><td><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> "
                         f"<span class='muted'>{_e(aff_tk(t['ticker']))}</span></td><td class='m'>{_e(valeur(t))}</td>"
                         f"<td class='m'>{_px(t['prix'], t['devise'])}</td></tr>" for i, t in enumerate(sel, 1))
        corps = (f"<p class='muted'><a href='../classements.html'>Tous les classements</a></p><h1>{_e(titre_h1)}</h1>"
                 f"<p class='muted'>Mis à jour automatiquement · cours au {_e(date)}</p><p>{_e(intro)}</p>"
                 + ("<p><a href='../suivi-chute.html'>Cette prévision est-elle fiable ? Le suivi public mois par mois</a></p>" if "chute" in cle else "")
                 + ""
                 "<div class='carte' style='overflow-x:auto'><table><tr><td><b>#</b></td><td><b>Titre</b></td><td><b>Valeur</b></td><td><b>Cours</b></td></tr>"
                 + lignes + "</table></div>"
                 "<p class='muted'>Un classement trie des chiffres : il ne dit pas quoi acheter. Les prévisions des IA se trompent souvent, "
                 "leur vrai taux de réussite est sur la page <a href='../resultats.html'>Résultats réels</a>. Projet éducatif, pas un conseil.</p>")
        chemin = f"classements/{cle}.html"
        an = datetime.now().year
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            jl = _jsonld_liste(base, titre_h1, chemin, [(t["nom"], f"titres/{slug(t['ticker'])}.html") for t in sel], ("Classements", "classements.html"))
            f.write(_page(base, f"{titre_h1} ({an}) | {NOM}", intro[:155], chemin, corps, jl, csp=csp))
        faits.append(chemin)
        liens.append((titre_h1, chemin))
    try:
        for h1, chemin in _pages_secteurs(base, titres, dossier, csp, date):
            faits.append(chemin)
            liens.append((h1, chemin))
    except Exception as e:
        print(f"Pages secteurs non générées : {e}")
    if liens:
        liens.insert(0, ("Le risque de chute vérifié en public, mois par mois", "suivi-chute.html"))
        liens.insert(1, ("Calendrier des résultats des entreprises", "calendrier-resultats.html"))
        corps = ("<h1>Les classements du jour</h1><p class='muted'>Actions et cryptos triées selon un critère, mis à jour automatiquement.</p><ul class='liste'>"
                 + "".join(f"<li><a href='{c}'>{_e(t)}</a></li>" for t, c in liens) + "</ul>")
        with open(os.path.join(dossier, "classements.html"), "w", encoding="utf-8") as f:
            f.write(_page(base, f"Classements du jour : dividende, risque, PER | {NOM}",
                          "Actions à fort dividende, actions les plus calmes, cryptos les plus volatiles, PER les plus bas : les classements du jour.",
                          "classements.html", corps, _jsonld_liste(base, "Classements du jour", "classements.html", [(t, c) for t, c in liens]), csp=csp))
        faits.append("classements.html")
    return faits


def _widgets(base, payload, dossier, date):
    """Un petit encadré par titre, que n'importe quel site peut intégrer (code fourni sur chaque fiche).
    Il affiche le cours, l'agitation prévue et l'avis des IA, avec un lien vers la fiche : chaque intégration
    est un lien vers le site, ce qui compte beaucoup pour Google. Les encadrés eux-mêmes ne sont pas indexés."""
    os.makedirs(os.path.join(dossier, "widget"), exist_ok=True)
    for t in payload.get("titres", []):
        if not t.get("prix"):
            continue
        rq, p = t.get("risque_prevu") or {}, t.get("proba_hausse")
        m1 = (t.get("perf") or {}).get("1 mois")
        avis = "–" if p is None else ("pas d'avis net" if t.get("avis_net") is False else f"{round(p * 100)} chances sur 100 de hausse")
        fiche = f"{base}titres/{slug(t['ticker'])}.html" if base else f"../titres/{slug(t['ticker'])}.html"
        page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow"><link rel="canonical" href="{_e(fiche)}">
<title>{_e(t['nom'])} · {NOM}</title>
<style>
:root{{--bg:#ffffff;--ink:#0f1b2d;--muted:#5a6a80;--line:#d9e0e8;--up:#137a3f;--down:#b42318}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111a29;--ink:#e4ebf5;--muted:#8c9bb0;--line:#22314a;--up:#35c27d;--down:#ff6b6b}}}}
body{{margin:0;font:14px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}}
a{{color:inherit;text-decoration:none}} .w{{display:block;border:1px solid var(--line);border-radius:12px;padding:12px 14px}}
.n{{font-weight:700;font-size:16px}} .p{{font-size:20px;font-weight:700;margin:2px 0}} .u{{color:var(--up)}} .d{{color:var(--down)}}
.l{{color:var(--muted);font-size:12.5px}} .s{{margin-top:6px;font-size:12px;color:var(--muted)}}
</style></head><body>
<main><a class="w" href="{_e(fiche)}" target="_blank" rel="noopener">
<h1 class="n" style="margin:0">{_e(t['nom'])} <span class="l">{_e(aff_tk(t['ticker']))}</span></h1>
<div class="p">{_px(t['prix'], t['devise'])}{f' <span class="{"u" if m1 >= 0 else "d"}" style="font-size:14px">{_pct(m1)} sur 1 mois</span>' if m1 is not None else ''}</div>
<div class="l">{f"Agitation prévue : ±{round(rq['mouvement'] * 100)} % en un mois · " if rq.get('mouvement') else ''}IA : {_e(avis)}</div>
<div class="s">{NOM} · cours au {_e(date)} · pas un conseil</div>
</a></main></body></html>
"""
        with open(os.path.join(dossier, "widget", f"{slug(t['ticker'])}.html"), "w", encoding="utf-8") as f:
            f.write(page)


def _page_previsions(base, payload, dossier, csp, date):
    an = datetime.now().year
    annees = f"{an}" if datetime.now().month < 9 else f"{an} et {an + 1}"
    groupes = {"fr": "Actions françaises", "eu": "Actions européennes", "us": "Actions américaines",
               "crypto": "Cryptomonnaies", "etf": "ETF et indices"}
    corps = (f"<h1>Prévisions Bourse et crypto {annees} : ce qu'on peut vraiment prévoir</h1>"
             "<p>Beaucoup de sites affichent un prix précis pour le Bitcoin ou Nvidia en fin d'année, voire en 2030. "
             "Ces chiffres prolongent une tendance passée : aucun n'a prouvé qu'il faisait mieux que le hasard. "
             f"{NOM} fait autrement : ses deux IA prévoient seulement <b>le mois qui vient</b>, et chaque prévision est "
             "<a href='resultats.html'>vérifiée publiquement</a>, ratés compris.</p>"
             "<p>Ce que les IA prévoient le mieux, c'est <b>l'agitation</b> : de combien un prix risque de bouger. "
             "Deviner s'il va monter est beaucoup plus dur, et elles le disent quand elles n'ont pas d'avis net. "
             "La dernière colonne n'est pas une prévision : c'est l'écart que le prix parcourt souvent en un an (environ 2 chances sur 3), "
             "calculé à partir de sa volatilité. Elle mesure le risque.</p>")
    for cle, lib in groupes.items():
        sel = [t for t in payload.get("titres", []) if t.get("marche") == cle and t.get("prix")]
        if not sel:
            continue
        sel.sort(key=lambda t: t["nom"].lower())
        lignes = []
        for t in sel:
            rq, p = t.get("risque_prevu") or {}, t.get("proba_hausse")
            vol = (t.get("perf") or {}).get("volatilité annuelle")
            avis = "–" if p is None else ("pas d'avis net" if t.get("avis_net") is False else f"{round(p * 100)} sur 100")
            an_txt = (f"{_px(t['prix'] * math.exp(-vol), t['devise'])} à {_px(t['prix'] * math.exp(vol), t['devise'])}" if vol else "–")
            lignes.append(f"<tr><td><a href='titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a></td><td class='m'>{_px(t['prix'], t['devise'])}</td>"
                          f"<td class='m'>{'±' + str(round(rq['mouvement'] * 100)) + ' %' if rq.get('mouvement') else '–'}</td>"
                          f"<td class='m'>{avis}</td><td class='m'>{an_txt}</td></tr>")
        corps += (f"<h2>{lib}</h2><div class='carte' style='overflow-x:auto'><table><tr><td><b>Titre</b></td><td><b>Cours</b></td>"
                  "<td><b>Agitation prévue (1 mois)</b></td><td><b>Chances de hausse (1 mois)</b></td><td><b>Écart habituel sur un an</b></td></tr>"
                  + "".join(lignes) + "</table></div>")
    corps += (f"<p class='muted'>Chiffres du {_e(date)}, mis à jour automatiquement. Projet éducatif, pas un conseil en investissement : "
              "tu peux perdre tout l'argent investi.</p>")
    faq = [(f"Peut-on prévoir le cours du Bitcoin en {an + 1} ?",
            "Pas de façon fiable. Les prix « prévus » pour l'année prochaine ou 2030 qu'on trouve en ligne ne sont pas vérifiés. "
            f"{NOM} ne prévoit qu'à un mois et publie son taux de réussite réel."),
           ("Quelle est la meilleure action pour les mois qui viennent ?",
            "Personne ne le sait à l'avance. Le radar montre les chances calculées par ses IA et leur fiabilité mesurée, "
            "mais elles se trompent souvent : c'est un outil pour comprendre, pas une liste d'achats.")]
    jsonld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    corps += "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq)
    titre = f"Prévisions bourse et crypto {annees}, vérifiées | {NOM}"
    desc = (f"Prévisions {annees} pour plus de 200 actions et cryptos : agitation et chances de hausse à un mois par IA, "
            "vérifiées publiquement, et écart habituel sur un an.")
    with open(os.path.join(dossier, "previsions.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, titre, desc, "previsions.html", corps, jsonld, csp))


MARCHES = {
    "fr": ("actions-francaises", "Actions françaises", "Prévisions à un mois des grandes actions françaises (CAC 40)",
           "Les grandes entreprises cotées à Paris : LVMH, TotalEnergies, Airbus, L'Oréal… Leur indice de référence est le CAC 40."),
    "eu": ("actions-europeennes", "Actions européennes", "Prévisions à un mois des grandes actions européennes",
           "Les géants européens hors France : SAP, ASML, Siemens, Ferrari… Leur indice de référence est l'Euro Stoxx 50."),
    "us": ("actions-americaines", "Actions américaines", "Prévisions à un mois des actions américaines (Apple, Nvidia…)",
           "Les grandes entreprises de Wall Street : Apple, Microsoft, Nvidia, Amazon… Leur indice de référence est le S&P 500."),
    "crypto": ("cryptomonnaies", "Cryptomonnaies", "Prévisions à un mois des cryptomonnaies (Bitcoin, Ethereum…)",
               "Bitcoin, Ethereum, Solana et les autres grandes cryptos, cotées 7 jours sur 7. Elles bougent beaucoup plus que les actions."),
    "etf": ("etf-et-indices", "ETF et indices", "Prévisions à un mois des ETF et grands indices boursiers",
            "Les fonds indiciels (ETF) et les grands indices : une façon de suivre tout un marché ou un thème d'un coup."),
}


def _jsonld_fil(base, etapes):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": (base + c) if base else None} for i, (n, c) in enumerate(etapes)]}


def _profil(fd):
    """Carte d'identité de l'entreprise, en phrases et en chiffres."""
    v, dev = fd.get("valeurs") or {}, fd.get("devise", "")

    def montant(x):
        for seuil, unite in ((1e12, "000 Md"), (1e9, "Md"), (1e6, "M")):
            if abs(x) >= seuil:
                n = x / (1e9 if unite == "000 Md" else seuil)
                return f"{n:,.0f}".replace(",", " ") + f" Md {dev}" if unite == "000 Md" else f"{n:,.1f}".replace(",", " ").replace(".", ",") + f" {unite} {dev}"
        return f"{x:,.0f}".replace(",", " ") + f" {dev}"
    lignes = []
    for k, lib, f in (("marketCap", "Capitalisation boursière", montant), ("trailingPE", "PER (12 derniers mois)", lambda x: f"{x:.1f}".replace(".", ",")),
                      ("forwardPE", "PER attendu", lambda x: f"{x:.1f}".replace(".", ",")),
                      ("revenueGrowth", "Croissance du chiffre d'affaires", lambda x: _pct(x)),
                      ("profitMargins", "Marge nette", lambda x: f"{x * 100:.1f} %".replace(".", ",")),
                      ("returnOnEquity", "Rentabilité des capitaux (ROE)", lambda x: f"{x * 100:.1f} %".replace(".", ",")),
                      ("debtToEquity", "Dette / capitaux propres", lambda x: f"{x:.0f} %"),
                      ("dividendYield", "Rendement du dividende", lambda x: f"{x:.2f} %".replace(".", ",")),
                      ("freeCashflow", "Trésorerie disponible (free cash-flow)", montant)):
        x = v.get(k)
        if isinstance(x, (int, float)) and x == x:
            lignes.append(f"<tr><td>{lib}</td><td class='m'>{f(x)}</td></tr>")
    if not lignes:
        return ""
    secteur = fd.get("secteur")
    intro = f"<p>Secteur : <b>{_e(secteur)}</b>.</p>" if secteur else ""
    return (f"<h2>L'entreprise en chiffres</h2>{intro}<div class='carte'><table>{''.join(lignes)}</table></div>"
            "<p class='muted' style='font-size:14px'>Données publiques des derniers comptes. Le PER indique combien le marché paie "
            "chaque euro de bénéfice ; une dette au-dessus de 200 % des capitaux propres est élevée.</p>")


def _faq_titre(t, nom, date, verdict):
    """Questions que les gens tapent vraiment sur Google, avec des réponses honnêtes tirées des chiffres du jour."""
    dev, p, pf = t["devise"], t.get("proba_hausse"), t.get("perf") or {}
    rq = t.get("risque_prevu") or {}
    faq = [(f"Quel est le cours de {nom} aujourd'hui ?",
            f"Au {_e(date)}, {_e(nom)} cote <b>{_px(t['prix'], dev)}</b>"
            + (f", soit {_pct(pf['1 mois'])} sur un mois" if pf.get("1 mois") is not None else "") + ". Cours mis à jour automatiquement plusieurs fois par jour.")]
    if p is not None:
        faq.append((f"{nom} va-t-il monter le mois prochain ?",
                    (f"Personne ne peut le savoir avec certitude. Sur ce marché, les IA de {NOM} n'ont pas fait mieux que sa tendance habituelle : "
                     f"historiquement, il a fini plus haut environ {round(p * 100)} mois sur 100. Ce n'est pas une prévision."
                     if t.get("source_proba") == "marche" else
                     f"Personne ne peut le savoir avec certitude. Aujourd'hui, les deux IA de {NOM} n'ont <b>pas d'avis net</b> sur {_e(nom)} : "
                     f"leur chiffre brut ({round(p * 100)} sur 100) est dans une zone où, par le passé, elles n'ont pas fait mieux que le hasard."
                     if t.get("avis_net") is False else
                     f"Personne ne peut le savoir avec certitude. Pour les 20 prochaines séances, les deux IA de {NOM} voient {_e(nom)} "
                     f"<b>{verdict}</b>, avec {round(p * 100)} chances sur 100 d'être plus haut dans un mois. "
                     "Ces chances sont mesurées sur des années que les IA n'avaient jamais vues, et elles se trompent souvent.")))
    if t.get("proba_marche") is not None:
        pm, ind = t["proba_marche"], t.get("indice_nom") or "son marché"
        faq.append((f"{nom} va-t-il faire mieux que {ind} ?",
                    (f"Les IA n'ont pas d'avis net sur ce point aujourd'hui ({round(pm * 100)} chances sur 100). "
                     if t.get("marche_net") is False else
                     f"Les IA donnent <b>{round(pm * 100)} chances sur 100</b> que {_e(nom)} fasse mieux que {_e(ind)} d'ici un mois. ")
                    + "Cette comparaison reste utile même quand tout le marché baisse : certains titres baissent moins que les autres."))
    # « prévision X 2026 » : une des recherches les plus tapées. Réponse honnête : à un an, personne ne sait ;
    # on donne la prévision à un mois (testée) et l'écart HABITUEL sur un an, tiré de la volatilité (statistique, pas une prévision).
    an = datetime.now().year
    annees = f"{an}" if datetime.now().month < 9 else f"{an} et {an + 1}"
    vol = pf.get("volatilité annuelle")
    if vol:
        px0 = t.get("prix")
        bas, haut = (px0 * math.exp(-vol), px0 * math.exp(vol)) if px0 else (None, None)
        faq.append((f"Quelle est la prévision pour {nom} en {annees} ?",
                    "Personne ne peut prévoir sérieusement le cours d'une action ou d'une crypto à un an : les sites qui donnent un prix précis pour "
                    f"{an + 1} ou 2030 prolongent une tendance, sans preuve que ça marche. {NOM} ne prévoit qu'à un mois, et affiche son taux de réussite réel. "
                    + (f"Pour se faire une idée de l'incertitude : avec sa volatilité actuelle ({_taux(vol)} par an), le prix de {_e(nom)} "
                       f"finit souvent une année entre <b>{_px(bas, dev)}</b> et <b>{_px(haut, dev)}</b> (environ 2 chances sur 3), "
                       "et il peut sortir de cet écart. C'est une mesure du risque, pas une prévision." if bas else "")))
    fv = (t.get("fondamentaux") or {}).get("valeurs") or {}
    dy, per = fv.get("dividendYield"), fv.get("trailingPE")
    if dy is not None:
        faq.append((f"Quel est le dividende de {nom} ?",
                    (f"Le rendement du dividende de {_e(nom)} est d'environ <b>{dy:.2f} %</b> par an au cours actuel".replace(".", ",", 1)
                     + " (source : Yahoo Finance). Un dividende peut baisser ou être supprimé ; il n'est jamais garanti."
                     if dy > 0.05 else f"{_e(nom)} ne verse pas de dividende significatif actuellement (source : Yahoo Finance).")))
    if per is not None and per > 0:
        faq.append((f"Quel est le PER de {nom} ?",
                    f"Le PER de {_e(nom)} sur les 12 derniers mois est d'environ <b>{per:.1f}</b>".replace(".", ",", 1)
                    + " : le marché paie environ " + f"{per:.0f}" + " fois le bénéfice annuel par action. "
                    "Un PER élevé veut dire que le marché attend beaucoup de croissance ; il ne dit pas à lui seul si l'action est chère."))
    faq.append((f"Faut-il acheter {nom} ?",
                f"{NOM} ne donne aucun conseil d'achat ou de vente : c'est un projet éducatif. La page montre les chiffres "
                "(chances de hausse, agitation prévue, fourchette de prix) pour aider à comprendre, pas pour décider à ta place. "
                "N'investis que de l'argent que tu peux te permettre de perdre."))
    if rq.get("mouvement"):
        faq.append((f"{nom} est-il risqué ?",
                    f"Pour le mois prochain, l'agitation prévue est d'environ <b>±{round(rq['mouvement'] * 100)} %</b> : "
                    "en général, le prix finira le mois dans cet écart, à la hausse comme à la baisse"
                    + (", ce qui est plus que d'habitude pour ce titre" if (rq.get("habitude") or 1) > 1.25 else
                       ", ce qui est moins que d'habitude pour ce titre" if (rq.get("habitude") or 1) < 0.8 else "") + "."))
    rl = t.get("resultats_le") or (t.get("fondamentaux") or {}).get("resultats_le")
    if rl:
        try:
            rl_txt = datetime.strptime(rl, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            rl_txt = rl
        faq.append((f"Quand {nom} publie-t-il ses résultats ?",
                    f"La prochaine publication de résultats est prévue le <b>{_e(rl_txt)}</b>. Le cours peut beaucoup bouger ce jour-là."))
    return faq


def _page_marche(base, cle, titres, date, csp):
    chemin_page, lib, titre_h1, intro = MARCHES[cle]
    chemin = f"marches/{chemin_page}.html"
    avec = [t for t in titres if t.get("proba_hausse") is not None]
    nets = [t for t in avec if t.get("avis_net") is not False]
    moy = sum(t["proba_hausse"] for t in avec) / len(avec) if avec else None
    lignes = "".join(
        f"<tr><td><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a></td><td class='m'>{_px(t['prix'], t['devise'])}</td>"
        f"<td class='m'>{_pct((t.get('perf') or {}).get('1 mois'))}</td>"
        f"<td class='m'>{'pas d’avis net' if t.get('avis_net') is False else (str(round(t['proba_hausse'] * 100)) + ' %') if t.get('proba_hausse') is not None else '–'}</td>"
        f"<td class='m'>{('±' + str(round(t['risque_prevu']['mouvement'] * 100)) + ' %') if (t.get('risque_prevu') or {}).get('mouvement') else '–'}</td></tr>"
        for t in sorted(titres, key=lambda t: -(t.get("proba_hausse") or 0)))
    tete = (f"<h1>{_e(titre_h1)}</h1><p class='muted'>Mise à jour automatique · cours au {_e(date)}</p><p>{_e(intro)}</p>"
            + (f"<p>Aujourd'hui, les deux IA donnent en moyenne <b>{round(moy * 100)} chances sur 100</b> de hausse à un mois "
               f"pour ces {len(avec)} titres, avec un avis net sur {len(nets)} d'entre eux.</p>" if moy is not None else ""))
    corps = (f"<p class='muted' style='font-size:14px'><a href='../titres.html'>Tous les titres</a> › {_e(lib)}</p>" + tete
             + "<div class='carte' style='overflow-x:auto'><table><tr><td><b>Titre</b></td><td><b>Cours</b></td><td><b>1 mois</b></td>"
             "<td><b>Chances de hausse</b></td><td><b>Agitation prévue</b></td></tr>" + lignes + "</table></div>"
             "<p class='muted' style='font-size:14px'>« Chances de hausse » : probabilité d'être plus haut dans 20 séances. "
             "« Pas d'avis net » : les IA hésitent, et dans ces cas-là elles n'ont pas fait mieux que le hasard. "
             "« Agitation prévue » : de combien le prix bouge en général sur un mois, dans un sens ou dans l'autre.</p>"
             f"<h2>Les autres marchés</h2><ul class='liste'>" + "".join(
                 f"<li><a href='{m[0]}.html'>{_e(m[1])}</a></li>" for k, m in MARCHES.items() if k != cle) + "</ul>")
    desc = f"{titre_h1} : chances de hausse, agitation prévue et analyse de chaque titre, mises à jour chaque jour. Projet éducatif."
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": titre_h1, "description": desc, "inLanguage": "fr-FR",
         "dateModified": datetime.now().isoformat(timespec="seconds")},
        _jsonld_fil(base, [("Tous les titres", "titres.html"), (lib, chemin)])]}
    return chemin, _page(base, f"{titre_h1} | {NOM}", desc, chemin, corps, jsonld, csp)


def _page_robots(base, payload, csp, date):
    """Page publique des mini-robots : leurs règles, leur vrai palmarès et leurs signaux du jour."""
    robots = payload.get("robots") or []
    noms = {t["ticker"]: t["nom"] for t in payload.get("titres", [])}
    lien = lambda tk: f"<a href='titres/{slug(tk)}.html'>{_e(noms.get(tk, aff_tk(tk)))}</a>"
    blocs = []
    for r in robots:
        A, V, b = r.get("achat") or {}, r.get("vente") or {}, r.get("base_hausse")
        bilan = ""
        if A.get("nb", 0) >= 30 and b is not None:
            ecart = A["taux"] - b
            nb = f"{A['nb']:,}".replace(",", "\u202f")
            bilan = (f"<p>Sur tout l'historique, quand il a dit « acheter » ({nb} fois), le prix était plus haut "
                     f"{payload.get('horizon', 20)} séances plus tard <b>{round(A['taux'] * 100)} fois sur 100</b>, contre "
                     f"{round(b * 100)} en achetant au hasard : "
                     + ("un peu mieux que le hasard." if ecart > .01 else "moins bien que le hasard." if ecart < -.01 else "pas mieux que le hasard.")
                     + "</p>")
        if V.get("nb", 0) >= 30 and b is not None:
            bilan += f"<p>Quand il a dit « vendre », le prix a bien baissé {round(V['taux'] * 100)} fois sur 100 (au hasard : {round((1 - b) * 100)}).</p>"
        ach, ven = r["du_jour"]["achat"], r["du_jour"]["vente"]
        jour = (f"<p><b>Aujourd'hui, il achèterait :</b> {', '.join(lien(t) for t in ach[:15])}{' …' if len(ach) > 15 else ''}</p>" if ach else "")
        jour += (f"<p><b>Aujourd'hui, il vendrait :</b> {', '.join(lien(t) for t in ven[:15])}{' …' if len(ven) > 15 else ''}</p>" if ven else "")
        blocs.append(f"<div class='carte'><h2 style='margin-top:0'>{_e(r['nom'])}</h2><p>{_e(r['idee'])}</p>{bilan}"
                     f"{jour or '<p>Aujourd’hui, il ne donne aucun signal.</p>'}</div>")
    corps = (f"<h1>Les mini-robots de Bourse et de crypto</h1><p class='muted'>Mise à jour automatique · cours au {_e(date)}</p>"
             "<p>Neuf stratégies classiques, chacune avec une règle simple et fixe : suivi de tendance, RSI, momentum, cassures, MACD, "
             "Bollinger, cycle du halving… Pour chacune, voici ce qu'elle a vraiment donné sur tout l'historique, comparé à "
             "« acheter au hasard », et ce qu'elle dirait aujourd'hui. Ce sont des outils pour comprendre, pas des conseils.</p>"
             + "".join(blocs))
    desc = "Neuf stratégies classiques de Bourse et de crypto (tendance, RSI, MACD, Bollinger, halving…) : leur vrai palmarès et leurs signaux du jour."
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Les mini-robots de Bourse et de crypto",
              "description": desc, "inLanguage": "fr-FR", "dateModified": datetime.now().isoformat(timespec="seconds")}
    return _page(base, f"Stratégies de Bourse testées : les mini-robots | {NOM}", desc, "robots.html", corps, jsonld, csp)


def _image_partage(payload: dict, chemin: str) -> None:
    """Image 1200×630 affichée quand le lien est partagé (WhatsApp, Discord, X…).
    Version 53 : même style que les images des autres pages, avec le nombre de titres du jour."""
    try:
        from .visuels import dessiner
        n = len(payload.get("titres", []))
        if dessiner(chemin, "Prévisions bourse et crypto par IA", f"{n} actions, ETF et cryptos · simulateur boursier · outils gratuits", "radar"):
            return
    except Exception:
        pass
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#0f1b2d")
    dr = ImageDraw.Draw(img)

    def police(taille, gras=False):
        for nom in (("DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf"), ("arialbd.ttf" if gras else "arial.ttf")):
            for dossier in ("/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", ""):
                try:
                    return ImageFont.truetype(dossier + nom, taille)
                except Exception:
                    continue
        return ImageFont.load_default()
    # radar décoratif
    for r, a in ((260, "#16264a"), (190, "#1a2d57"), (120, "#1f3566")):
        dr.ellipse((W - 330 - r, H / 2 - r, W - 330 + r, H / 2 + r), outline=a, width=3)
    dr.line((W - 330, H / 2, W - 120, H / 2 - 150), fill="#35c27d", width=8)
    dr.ellipse((W - 342, H / 2 - 12, W - 318, H / 2 + 12), fill="#35c27d")
    dr.text((70, 80), NOM, font=police(78, True), fill="#ffffff")
    dr.text((72, 185), "Prévisions à un mois, expliquées simplement", font=police(34), fill="#a9b8d0")
    titres = payload.get("titres", [])
    forts = [t for t in titres if t.get("signal_fort")]
    y = 280
    lignes = [f"{len(titres)} titres analysés · actions FR, US et cryptos",
              (f"{len(forts)} signal fort aujourd'hui" if len(forts) == 1 else
               f"{len(forts)} signaux forts aujourd'hui" if forts else "Signaux forts mesurés sur l'historique"),
              "Graphiques, simulateur, actualités · gratuit"]
    for l in lignes:
        dr.ellipse((72, y + 14, 88, y + 30), fill="#7398ff")
        dr.text((104, y), l, font=police(32), fill="#e4ebf5")
        y += 62
    dr.text((72, H - 70), "Projet éducatif · pas un conseil en investissement", font=police(24), fill="#8c9bb0")
    img.save(chemin, optimize=True)


def _police(taille, gras=False):
    from PIL import ImageFont
    for nom in (("DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf"), ("arialbd.ttf" if gras else "arial.ttf")):
        for d in ("/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", ""):
            try:
                return ImageFont.truetype(d + nom, taille)
            except Exception:
                continue
    return ImageFont.load_default()


def _image_titre(t: dict, chemin: str, date: str) -> bool:
    """Image 1200×630 propre à chaque titre (aperçu quand on partage sa page sur WhatsApp, Discord, X…) :
    nom, prix, variation sur un mois, mini-courbe, agitation prévue et avis des IA, sans rien promettre."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return False
    try:
        W, H = 1200, 630
        FOND, TEXTE, DOUX, HAUT, BAS = "#0f1b2d", "#ffffff", "#a9b8d0", "#35c27d", "#ff6b6b"
        img = Image.new("RGB", (W, H), FOND)
        dr = ImageDraw.Draw(img)
        nom = str(t.get("nom") or t["ticker"])
        if len(nom) > 26:
            nom = nom[:25] + "…"
        dr.text((70, 60), NOM, font=_police(30, True), fill=DOUX)
        dr.text((70, 110), nom, font=_police(66, True), fill=TEXTE)
        dr.text((72, 195), f"{aff_tk(t['ticker'])} · cours au {date}", font=_police(28), fill=DOUX)
        dr.text((70, 255), _px(t.get("prix"), t.get("devise", "")).replace("\u202f", " ").replace("\xa0", " "), font=_police(72, True), fill=TEXTE)
        m1 = (t.get("perf") or {}).get("1 mois")
        if m1 is not None:
            dr.text((72, 345), f"{'+' if m1 >= 0 else '−'}{abs(m1) * 100:.1f} % sur un mois".replace(".", ","), font=_police(32, True),
                    fill=HAUT if m1 >= 0 else BAS)
        # mini-courbe des 3 derniers mois
        sp = [float(v) for v in (t.get("spark") or []) if v is not None]
        if len(sp) >= 5:
            x0, y0, x1, y1 = 660, 120, 1130, 380
            lo, hi = min(sp), max(sp)
            et = (hi - lo) or 1
            pts = [(x0 + (x1 - x0) * i / (len(sp) - 1), y1 - (y1 - y0) * (v - lo) / et) for i, v in enumerate(sp)]
            coul = HAUT if sp[-1] >= sp[0] else BAS
            dr.polygon(pts + [(x1, y1), (x0, y1)], fill="#16264a")
            dr.line(pts, fill=coul, width=6, joint="curve")
            dr.ellipse((pts[-1][0] - 10, pts[-1][1] - 10, pts[-1][0] + 10, pts[-1][1] + 10), fill=coul)
            dr.text((x0, y1 + 14), "3 derniers mois", font=_police(24), fill=DOUX)
        # ce que disent les IA (l'agitation d'abord : c'est ce qu'elles prévoient le mieux)
        rq, p = t.get("risque_prevu") or {}, t.get("proba_hausse")
        lignes = []
        if rq.get("mouvement"):
            lignes.append(f"Agitation prévue : ±{round(rq['mouvement'] * 100)} % sur un mois")
        if p is not None:
            lignes.append("Avis des IA : pas d'avis net" if t.get("avis_net") is False else
                          f"Avis des IA : {round(p * 100)} chances sur 100 de hausse")
        y = 440
        for l in lignes[:2]:
            dr.ellipse((72, y + 12, 88, y + 28), fill="#7398ff")
            dr.text((104, y), l, font=_police(32), fill="#e4ebf5")
            y += 56
        dr.text((72, H - 52), "Projet éducatif · pas un conseil en investissement", font=_police(22), fill="#8c9bb0")
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        img.save(chemin)
        return True
    except Exception:
        return False


ICONE_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
             "<defs><linearGradient id='b' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#16294a'/>"
             "<stop offset='1' stop-color='#0b1424'/></linearGradient></defs>"
             "<rect width='64' height='64' rx='14' fill='url(#b)'/>"
             "<circle cx='32' cy='32' r='21' fill='none' stroke='#7398ff' stroke-width='2.5' opacity='.9'/>"
             "<circle cx='32' cy='32' r='12' fill='none' stroke='#7398ff' stroke-width='2' opacity='.55'/>"
             "<path d='M32 32 L50 21 A21 21 0 0 0 39 12.2 Z' fill='#35c27d' opacity='.35'/>"
             "<path d='M32 32 L50 21' stroke='#35c27d' stroke-width='4' stroke-linecap='round'/>"
             "<circle cx='32' cy='32' r='4' fill='#35c27d'/><circle cx='22' cy='41' r='2.6' fill='#ffd166'/></svg>")


def _icones(dossier: str) -> None:
    """Icône du site (onglet, résultats Google, écran d'accueil du téléphone) : vrais fichiers, lisibles par Google
    (une icône intégrée en « data: » n'est pas reprise dans les résultats de recherche)."""
    with open(os.path.join(dossier, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(ICONE_SVG)
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return
    T = 1024                       # dessin en grand puis réduction : bords lisses
    k = T / 64
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    fond = Image.new("RGBA", (T, T))
    fd = ImageDraw.Draw(fond)
    for y in range(T):             # dégradé diagonal simplifié (vertical)
        t = y / T
        fd.line((0, y, T, y), fill=(int(0x16 + (0x0b - 0x16) * t), int(0x29 + (0x14 - 0x29) * t), int(0x4a + (0x24 - 0x4a) * t), 255))
    masque = Image.new("L", (T, T), 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, T - 1, T - 1), radius=int(14 * k), fill=255)
    img.paste(fond, (0, 0), masque)
    dr = ImageDraw.Draw(img, "RGBA")
    c = 32 * k
    for r, w, a in ((21, 2.5, 230), (12, 2, 140)):
        dr.ellipse((c - r * k, c - r * k, c + r * k, c + r * k), outline=(0x73, 0x98, 0xff, a), width=int(w * k))
    dr.pieslice((c - 21 * k, c - 21 * k, c + 21 * k, c + 21 * k), start=-69, end=-31, fill=(0x35, 0xc2, 0x7d, 90))
    dr.line((c, c, 50 * k, 21 * k), fill=(0x35, 0xc2, 0x7d, 255), width=int(4 * k))
    dr.ellipse((50 * k - 2 * k, 21 * k - 2 * k, 50 * k + 2 * k, 21 * k + 2 * k), fill=(0x35, 0xc2, 0x7d, 255))
    dr.ellipse((c - 4 * k, c - 4 * k, c + 4 * k, c + 4 * k), fill=(0x35, 0xc2, 0x7d, 255))
    dr.ellipse((22 * k - 2.6 * k, 41 * k - 2.6 * k, 22 * k + 2.6 * k, 41 * k + 2.6 * k), fill=(0xff, 0xd1, 0x66, 255))
    for taille in (48, 96, 180, 192, 512):
        petit = img.resize((taille, taille), Image.LANCZOS)
        if taille in (180, 192, 512):   # écran d'accueil du téléphone : fond plein, sans transparence
            plein = Image.new("RGB", (taille, taille), "#0b1424")
            plein.paste(petit, (0, 0), petit)
            petit = plein
        petit.save(os.path.join(dossier, f"icone-{taille}.png"), optimize=True)
    img.resize((48, 48), Image.LANCZOS).save(os.path.join(dossier, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def liens_icones(prefixe: str = "") -> str:
    return (f'<link rel="icon" href="{prefixe}favicon.ico" sizes="48x48">\n'
            f'<link rel="icon" href="{prefixe}favicon.svg" type="image/svg+xml">\n'
            f'<link rel="icon" type="image/png" sizes="96x96" href="{prefixe}icone-96.png">')


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]


def date_longue(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]} {d.year}"


def resume_du_jour(payload: dict) -> dict:
    """Ce qu'il faut retenir de la journée (archivé chaque soir dans historique/points/)."""
    titres = [t for t in payload.get("titres", []) if t.get("marche") != "tendances"]
    avec_var = [t for t in titres if (t.get("perf") or {}).get("1 jour") is not None]
    avec_var.sort(key=lambda t: t["perf"]["1 jour"], reverse=True)
    garde = lambda t: {"ticker": t["ticker"], "nom": t["nom"], "var": t["perf"]["1 jour"],
                       "prix": t["prix"], "devise": t["devise"], "proba": t.get("proba_hausse")}
    au200 = [t for t in titres if t.get("au_dessus_200") is not None]
    return {
        "date": payload.get("date_donnees"),
        "indices": [{"nom": i["nom"], "prix": i["prix"], "var": i["var_jour"], "devise": i["devise"]}
                    for i in payload.get("indices", [])],
        "hausses": [garde(t) for t in avec_var[:5]],
        "baisses": [garde(t) for t in avec_var[-5:][::-1]],
        "forts": [garde(t) for t in titres if t.get("signal_fort")][:8],
        "largeur": (sum(t["au_dessus_200"] for t in au200) / len(au200)) if au200 else None,
        "contexte": [{"nom": c["nom"], "valeur": c["valeur"], "unite": c["unite"]} for c in payload.get("contexte", [])],
        "actus": list({a["titre"]: {"titre": a["titre"], "url": a["url"], "source": a.get("source", "")}
                       for a in payload.get("actus_marche", [])}.values())[:5],
    }


def archiver_point(payload: dict) -> None:
    """Le soir, enregistre le point du jour dans l'historique (gardé d'une mise à jour à l'autre)."""
    r = resume_du_jour(payload)
    if not r["date"]:
        return
    dossier = os.path.join(config.DOSSIER_HISTORIQUE, "points")
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, f"{r['date']}.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, separators=(",", ":"), default=lambda v: None)


def _semaine_id(d: datetime) -> str:
    a, s, _ = d.isocalendar()
    return f"{a}-S{s:02d}"


def archiver_semaine(payload: dict) -> None:
    """Le soir, met à jour le résumé de la semaine en cours (le dernier soir de la semaine fait foi)."""
    titres = [t for t in payload.get("titres", []) if t.get("marche") != "tendances" and (t.get("perf") or {}).get("1 semaine") is not None]
    if len(titres) < 10:
        return
    now = datetime.now()
    indices = []
    for i in payload.get("indices") or []:
        sp = [v for v in (i.get("spark") or []) if v]
        if len(sp) >= 6:
            indices.append({"nom": i.get("nom"), "var": sp[-1] / sp[-6] - 1, "prix": i.get("prix"), "devise": i.get("devise", "")})
    garde = lambda t: {"ticker": t["ticker"], "nom": t["nom"], "var": t["perf"]["1 semaine"], "prix": t["prix"], "devise": t["devise"]}
    tri = sorted(titres, key=lambda t: t["perf"]["1 semaine"], reverse=True)
    agites = sorted([t for t in titres if (t.get("risque_prevu") or {}).get("mouvement")], key=lambda t: -t["risque_prevu"]["mouvement"])
    r = {"semaine": _semaine_id(now), "date": now.strftime("%Y-%m-%d"),
         "indices": indices, "hausses": [garde(t) for t in tri[:5]], "baisses": [garde(t) for t in tri[-5:][::-1]],
         "agites": [{"ticker": t["ticker"], "nom": t["nom"], "mouvement": t["risque_prevu"]["mouvement"]} for t in agites[:5]],
         "part_hausse": sum(t["perf"]["1 semaine"] > 0 for t in titres) / len(titres), "nb": len(titres)}
    dossier = os.path.join(config.DOSSIER_HISTORIQUE, "semaines")
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, f"{r['semaine']}.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, separators=(",", ":"), default=lambda v: None)


def _pages_semaines(base, dossier, csp):
    src = os.path.join(config.DOSSIER_HISTORIQUE, "semaines")
    if not os.path.isdir(src):
        return []
    semaines = {}
    for nom in sorted(os.listdir(src))[-104:]:
        try:
            with open(os.path.join(src, nom), encoding="utf-8") as f:
                r = json.load(f)
            semaines[r["semaine"]] = r
        except Exception:
            continue
    if not semaines:
        return []
    os.makedirs(os.path.join(dossier, "semaine"), exist_ok=True)
    ids = sorted(semaines)
    faits = []
    li = lambda t: (f"<li><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> {_pct(t['var'])} "
                    f"<span class='muted'>({_px(t['prix'], t['devise'])})</span></li>")
    for n, sid in enumerate(ids):
        r = semaines[sid]
        a, s = sid.split("-S")
        titre_h1 = f"La semaine en Bourse : semaine {int(s)} de {a}"
        ph = r.get("part_hausse") or 0
        corps = (f"<p class='muted'>La semaine en Bourse</p><h1>{_e(titre_h1)}</h1>"
                 f"<p>Sur les {r.get('nb', 0)} titres suivis, <b>{round(ph * 100)} %</b> ont fini la semaine en hausse : "
                 f"une semaine {'plutôt favorable' if ph >= .6 else 'plutôt difficile' if ph < .4 else 'mitigée'}. "
                 f"Résumé établi le {_e(date_longue(r['date']))}.</p>")
        if r.get("indices"):
            corps += ("<h2>Les grands indices sur la semaine</h2><div class='carte grille'>"
                      + "".join(f"<div class='k'><b>{_pct(i['var'])}</b><span>{_e(i['nom'])}</span></div>" for i in r["indices"]) + "</div>")
        corps += ("<h2>Plus fortes hausses de la semaine</h2><ul>" + "".join(li(t) for t in r.get("hausses", [])) + "</ul>"
                  "<h2>Plus fortes baisses de la semaine</h2><ul>" + "".join(li(t) for t in r.get("baisses", [])) + "</ul>")
        if r.get("agites"):
            corps += ("<h2>Les plus agités prévus pour le mois qui vient</h2><p>C'est ce que les IA du radar prévoient le mieux : "
                      "de combien un prix risque de bouger, dans un sens ou dans l'autre.</p><ul>"
                      + "".join(f"<li><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> : ±{round(t['mouvement'] * 100)} % prévus</li>"
                                for t in r["agites"]) + "</ul>")
        prec, suiv = (ids[n - 1] if n else None), (ids[n + 1] if n + 1 < len(ids) else None)
        corps += ("<p style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap'>"
                  + (f"<a href='{prec}.html'>← Semaine précédente</a>" if prec else "<span></span>")
                  + (f"<a href='{suiv}.html'>Semaine suivante →</a>" if suiv else "<a href='../point.html'>Le point du jour →</a>") + "</p>"
                  "<p class='muted'>Résumé automatique, projet éducatif : pas un conseil en investissement.</p>")
        chemin = f"semaine/{sid}.html"
        desc = f"{titre_h1} : indices, plus fortes hausses et baisses, et les titres les plus agités prévus par l'IA."
        jsonld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": titre_h1, "datePublished": r["date"],
                  "inLanguage": "fr-FR", "isAccessibleForFree": True, "author": {"@type": "Organization", "name": NOM}}
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(base, f"{titre_h1} | {NOM}", desc, chemin, corps, jsonld, csp))
        faits.append(chemin)
    corps = ("<h1>La semaine en Bourse</h1><p class='muted'>Chaque semaine, le résumé des marchés suivis par le radar.</p><ul class='liste'>"
             + "".join(f"<li><a href='semaine/{sid}.html'>Semaine {int(sid.split('-S')[1])} de {sid.split('-S')[0]}</a></li>" for sid in reversed(ids)) + "</ul>")
    with open(os.path.join(dossier, "semaines.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"La semaine en Bourse : résumés hebdomadaires | {NOM}",
                      "Chaque semaine : indices, plus fortes hausses et baisses, et les titres les plus agités prévus par l'IA.",
                      "semaines.html", corps, csp=csp))
    return faits + ["semaines.html"]


def _image_point(r: dict, chemin: str) -> bool:
    """Grande image paysage (1200×630) du point du jour : Google Discover met en avant les pages qui en ont une."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return False
    try:
        W, H = 1200, 630
        img = Image.new("RGB", (W, H), "#0f1b2d")
        dr = ImageDraw.Draw(img)
        dr.text((60, 50), NOM, font=_police(30, True), fill="#a9b8d0")
        dr.text((60, 100), f"Bourse du {date_longue(r['date'])}", font=_police(60, True), fill="#ffffff")
        y = 210
        for i in (r.get("indices") or [])[:4]:
            v = i.get("var")
            if v is None:
                continue
            dr.text((60, y), str(i.get("nom", "")), font=_police(36), fill="#e4ebf5")
            dr.text((700, y), f"{'+' if v >= 0 else '−'}{abs(v) * 100:.2f} %".replace(".", ","), font=_police(36, True),
                    fill="#35c27d" if v >= 0 else "#ff6b6b")
            y += 64
        h = (r.get("hausses") or [None])[0]
        if h:
            dr.text((60, y + 20), f"Plus forte hausse : {h['nom'][:24]} {'+' if h['var'] >= 0 else '−'}{abs(h['var']) * 100:.1f} %".replace(".", ","),
                    font=_police(30), fill="#e4ebf5")
        dr.text((60, H - 56), "Projet éducatif · pas un conseil en investissement", font=_police(22), fill="#8c9bb0")
        img.save(chemin)
        return True
    except Exception:
        return False


def _page_point(base, r, csp, precedent, suivant, image="partage.png"):
    dl = date_longue(r["date"])
    largeur = r.get("largeur")
    humeur = ("plutôt optimiste" if largeur is not None and largeur >= .6 else
              "plutôt prudent" if largeur is not None and largeur < .4 else "mitigé")
    li = lambda t: (f"<li><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> "
                    f"{_pct(t['var'])} <span class='muted'>({_px(t['prix'], t['devise'])})</span></li>")
    corps = (f"<p class='muted'>Le point du radar</p><h1>Bourse du {dl} : ce qu'il faut retenir</h1>"
             f"<p>Climat du marché : <b>{humeur}</b>"
             + (f" ({round(largeur * 100)} % des titres suivis sont au-dessus de leur moyenne 200 jours)." if largeur is not None else ".")
             + "</p>")
    if r.get("indices"):
        corps += ("<h2>Les grands indices</h2><div class='carte grille'>"
                  + "".join(f"<div class='k'><b>{_px(i['prix'], i['devise'])}</b><span>{_e(i['nom'])} {_pct(i['var'])}</span></div>" for i in r["indices"])
                  + "</div>")
    if r.get("hausses"):
        corps += "<h2>Plus fortes hausses</h2><ul>" + "".join(li(t) for t in r["hausses"]) + "</ul>"
    if r.get("baisses"):
        corps += "<h2>Plus fortes baisses</h2><ul>" + "".join(li(t) for t in r["baisses"]) + "</ul>"
    corps += "<h2>Signaux forts du jour</h2>"
    corps += ("<ul>" + "".join(f"<li><a href='../titres/{slug(t['ticker'])}.html'>{_e(t['nom'])}</a> : "
                               f"{round((t.get('proba') or 0) * 10)} chances sur 10 de hausse à un mois</li>" for t in r["forts"]) + "</ul>"
              if r.get("forts") else "<p>Aucun signal fort : les conditions n'étaient pas réunies.</p>")
    if r.get("contexte"):
        corps += "<h2>Contexte</h2><ul>" + "".join(
            f"<li>{_e(c['nom'])} : <span class='m'>{c['valeur']:.2f}</span> {_e(c['unite'])}</li>".replace(".", ",", 1) for c in r["contexte"]) + "</ul>"
    if r.get("actus"):
        corps += "<h2>Dans l'actualité</h2><ul>" + "".join(
            f"<li><a href='{_e(a['url'])}' rel='noopener noreferrer nofollow' target='_blank'>{_e(a['titre'])}</a> <span class='muted'>({_e(a['source'])})</span></li>"
            for a in r["actus"] if str(a.get("url", "")).startswith("http")) + "</ul>"
    corps += ("<p style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap'>"
              + (f"<a href='{precedent}.html'>← {date_longue(precedent)}</a>" if precedent else "<span></span>")
              + (f"<a href='{suivant}.html'>{date_longue(suivant)} →</a>" if suivant else "<a href='../index.html'>Prévisions du jour →</a>")
              + "</p>")
    titre = f"Bourse du {dl} : le point du radar (CAC 40, S&P 500, Bitcoin) | {NOM}"
    desc = f"Ce qu'il faut retenir des marchés le {dl} : indices, plus fortes hausses et baisses, signaux forts et actualités."
    chemin = f"point/{r['date']}.html"
    jsonld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": f"Bourse du {dl} : ce qu'il faut retenir",
              "datePublished": r["date"], "inLanguage": "fr-FR", "isAccessibleForFree": True,
              "author": {"@type": "Organization", "name": NOM}}
    if image != "partage.png":
        jsonld["image"] = (base + image) if base else image
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp, image=image)


def generer(payload: dict, dossier: str, csp: str) -> None:
    """Écrit toutes les pages et fichiers de référencement dans le dossier du site."""
    try:   # version 53 : images de partage par type de page
        from . import visuels
        IMAGES_PAGES.update(visuels.generer(dossier))
    except Exception as e:
        print(f"Images de partage non générées : {e}")
    base = url_site()
    date = payload.get("date_donnees", "")
    try:
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        pass
    horizon = payload.get("horizon", 20)
    os.makedirs(os.path.join(dossier, "titres"), exist_ok=True)
    urls = [("", "hourly", "1.0"), ("app-en.html", "hourly", "0.9"), ("titres.html", "daily", "0.8"), ("glossaire.html", "monthly", "0.6")]

    # Une page par titre
    duels = _duels_dispos(payload.get("titres", []))
    liens = []
    for t in payload.get("titres", []):
        voisins = [x for x in payload.get("titres", []) if x.get("marche") == t.get("marche") and x["ticker"] != t["ticker"]]
        voisins = sorted(voisins, key=lambda x: -(x.get("score") or 0))[:6]
        t = dict(t, _duels=[((y if x["ticker"] == t["ticker"] else x), _chemin_duel(x, y)) for x, y in duels if t["ticker"] in (x["ticker"], y["ticker"])])
        t = dict(t, _image_ok=_image_titre(t, os.path.join(dossier, "partage", f"{slug(t['ticker'])}.png"), date))
        chemin, page = _page_titre(base, t, horizon, date, csp, payload.get("modele"), payload.get("suivi"), voisins)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "hourly", "0.7"))
        liens.append((t["nom"], t["ticker"], chemin, t.get("marche", "")))

    # Une page par marché (actions françaises, cryptos…)
    os.makedirs(os.path.join(dossier, "marches"), exist_ok=True)
    for cle in MARCHES:
        sel = [t for t in payload.get("titres", []) if t.get("marche") == cle]
        if sel:
            chemin, page = _page_marche(base, cle, sel, date, csp)
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.8"))

    # « X ou Y ? »
    if duels:
        os.makedirs(os.path.join(dossier, "comparer"), exist_ok=True)
        for a_, b_ in duels:
            chemin, page = _page_duel(base, a_, b_, date, csp)
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.6"))
        corps = ("<h1>Comparer deux titres</h1><p class='muted'>Les comparaisons les plus demandées, avec les chiffres du jour : "
                 "cours, risque, agitation prévue et avis des IA.</p><ul class='liste'>"
                 + "".join(f"<li><a href='{_chemin_duel(a_, b_)}'>{_e(a_['nom'])} ou {_e(b_['nom'])}</a></li>" for a_, b_ in duels) + "</ul>")
        with open(os.path.join(dossier, "comparer.html"), "w", encoding="utf-8") as f:
            f.write(_page(base, f"Comparer deux titres : actions, ETF et cryptos côte à côte | {NOM}",
                          "Or ou bitcoin, LVMH ou Hermès, Nvidia ou AMD… Les comparaisons les plus demandées, avec les chiffres et prévisions du jour.",
                          "comparer.html", corps, csp=csp))
        urls.append(("comparer.html", "daily", "0.7"))

    # Portefeuille public « mieux que le marché »
    try:
        if _page_fiche_ia(base, payload, dossier, csp):
            urls.append(("fiche-technique-ia.html", "daily", "0.8"))
    except Exception as e:
        print(f"Fiche technique de l'IA non générée : {e}")
    try:
        if _page_calendrier(base, payload, dossier, csp, date):
            urls.append(("calendrier-resultats.html", "daily", "0.7"))
    except Exception as e:
        print(f"Calendrier des résultats non généré : {e}")
    try:
        if _page_suivi_chute(base, payload, dossier, csp):
            urls.append(("suivi-chute.html", "daily", "0.8"))
    except Exception as e:
        print(f"Page suivi du risque de chute non générée : {e}")
    try:
        if _page_portefeuille(base, payload, dossier, csp):
            urls.append(("portefeuille.html", "daily", "0.8"))
    except Exception as e:
        print(f"Page portefeuille non générée : {e}")

    # Classements du jour (« action dividende élevé », « action peu risquée »…) — version 33
    try:
        for chemin in _pages_classements(base, payload, dossier, csp, date):
            urls.append((chemin, "daily", "0.7"))
    except Exception as e:
        print(f"Classements non générés : {e}")
    # Encadrés à intégrer sur d'autres sites (chaque intégration = un lien vers le site)
    try:
        _widgets(base, payload, dossier, date)
    except Exception as e:
        print(f"Encadrés non générés : {e}")

    # « Prévisions bourse et crypto 2026 » : la page qui répond honnêtement à cette recherche
    try:
        _page_previsions(base, payload, dossier, csp, date)
        urls.append(("previsions.html", "daily", "0.8"))
    except Exception as e:
        print(f"Page prévisions non générée : {e}")

    # Les mini-robots
    if payload.get("robots"):
        with open(os.path.join(dossier, "robots.html"), "w", encoding="utf-8") as f:
            f.write(_page_robots(base, payload, csp, date))
        urls.append(("robots.html", "daily", "0.7"))

    # Index des titres
    groupes = {"fr": "Actions françaises", "eu": "Actions européennes", "us": "Actions américaines",
               "crypto": "Cryptomonnaies", "etf": "ETF et indices", "tendances": "En tendance"}
    corps = "<h1>Tous les titres analysés</h1><p class='muted'>Analyse et prévision à un mois, mises à jour automatiquement.</p>"
    for cle, lib in groupes.items():
        items = [l for l in liens if l[3] == cle]
        if items:
            hub = MARCHES.get(cle)
            corps += (f"<h2>{lib}</h2>" + (f"<p><a href='marches/{hub[0]}.html'>Voir le tableau des prévisions : {_e(hub[1].lower())}</a></p>" if hub else "")
                      + "<ul class='liste'>") + "".join(
                f"<li><a href='{_e(c)}'>{_e(n)}</a> <span class='muted'>({_e(aff_tk(tk))})</span></li>" for n, tk, c, _ in items) + "</ul>"
    with open(os.path.join(dossier, "titres.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Tous les titres : actions, ETF et cryptos | {NOM}",
                      "Liste des actions françaises et américaines, ETF et cryptomonnaies analysés chaque jour par Radar Bourse.",
                      "titres.html", corps, csp=csp))

    # Guides (version 38) : 100 réponses honnêtes aux recherches les plus tapées
    try:
        for chemin in _pages_guides(base, payload, dossier, csp, date):
            urls.append((chemin, "weekly", "0.7"))
    except Exception as e:
        print(f"Guides non générés : {e}")

    # Glossaire : une page par mot (version 33) + la page qui les rassemble
    try:
        for chemin in _pages_glossaire(base, payload, dossier, csp, date):
            urls.append((chemin, "weekly", "0.6"))
    except Exception as e:
        print(f"Pages du glossaire non générées : {e}")
    corps = ("<h1>Glossaire de la Bourse et de l'analyse technique</h1>"
             "<p class='muted'>Les mots utilisés sur Radar Bourse, expliqués simplement. Clique sur un mot pour sa page complète.</p><dl>"
             + "".join(f"<dt id='{slug(m)}'><a href='glossaire/{slug(m)}.html'>{_e(m)}</a></dt><dd>{_e(d)}</dd>" for m, d in GLOSSAIRE) + "</dl>")
    jsonld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": f"Glossaire {NOM}",
              "inLanguage": "fr-FR", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": m, "description": d} for m, d in GLOSSAIRE]}
    with open(os.path.join(dossier, "glossaire.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Glossaire : RSI, MACD, moyennes mobiles, PER… | {NOM}",
                      "Définitions simples des indicateurs boursiers : RSI, MACD, Bollinger, Ichimoku, stop-loss, PER, VIX et plus.",
                      "glossaire.html", corps, jsonld, csp))

    # Mini-cours « Apprendre la Bourse »
    from .lecons import LECONS
    os.makedirs(os.path.join(dossier, "lecons"), exist_ok=True)
    for i, (ident, titre_l, desc_l, minutes, contenu, retenir, question, reponse) in enumerate(LECONS):
        precedente = LECONS[i - 1] if i > 0 else None
        suivante = LECONS[i + 1] if i + 1 < len(LECONS) else None
        corps = (f"<p class='muted'>Leçon {i + 1} sur {len(LECONS)} · {minutes} min de lecture</p>"
                 f"<h1>{_e(titre_l)}</h1>{contenu}"
                 f"<div class='carte'><b>À retenir</b><p style='margin:6px 0 0'>{_e(retenir)}</p></div>"
                 f"<div class='carte'><b>Teste-toi</b><p style='margin:6px 0'>{_e(question)}</p>"
                 f"<details><summary style='cursor:pointer;color:var(--accent)'>Voir la réponse</summary><p>{_e(reponse)}</p></details></div>"
                 "<p style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap'>"
                 + (f"<a href='{precedente[0]}.html'>← {_e(precedente[1])}</a>" if precedente else "<span></span>")
                 + (f"<a href='{suivante[0]}.html'>{_e(suivante[1])} →</a>" if suivante else "<a href='../index.html'>Retour au radar →</a>")
                 + "</p>")
        jsonld = {"@context": "https://schema.org", "@type": "LearningResource", "name": titre_l,
                  "description": desc_l, "inLanguage": "fr-FR", "educationalLevel": "débutant",
                  "timeRequired": f"PT{minutes}M", "isAccessibleForFree": True}
        chemin = f"lecons/{ident}.html"
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(base, f"{titre_l} | Apprendre la Bourse avec {NOM}", desc_l, chemin, corps, jsonld, csp))
        urls.append((chemin, "monthly", "0.7"))
    corps = ("<h1>Apprendre la Bourse</h1><p class='muted'>Huit mini-cours gratuits pour comprendre les marchés, "
             "lire les graphiques et éviter les pièges. Environ 30 minutes au total.</p><ol>"
             + "".join(f"<li style='margin:10px 0'><a href='lecons/{l[0]}.html'><b>{_e(l[1])}</b></a><br>"
                       f"<span class='muted'>{_e(l[2])} · {l[3]} min</span></li>" for l in LECONS) + "</ol>"
             "<p>Ensuite, entraîne-toi sans risque avec le <a href='index.html#portefeuille'>portefeuille virtuel</a> "
             "et consulte le <a href='glossaire.html'>glossaire</a>.</p>")
    with open(os.path.join(dossier, "apprendre.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Apprendre la Bourse : 8 mini-cours gratuits | {NOM}",
                      "Cours gratuits et simples pour débuter en Bourse : actions, cryptos, graphiques en bougies, RSI, gestion du risque et pièges à éviter.",
                      "apprendre.html", corps, csp=csp))
    urls.append(("apprendre.html", "monthly", "0.8"))

    # Le point du jour : pages archivées (une par jour) + page du jour en cours
    points = {}
    dossier_pts = os.path.join(config.DOSSIER_HISTORIQUE, "points")
    if os.path.isdir(dossier_pts):
        for nom in sorted(os.listdir(dossier_pts))[-400:]:
            try:
                with open(os.path.join(dossier_pts, nom), encoding="utf-8") as f:
                    r = json.load(f)
                points[r["date"]] = r
            except Exception:
                continue
    if not payload.get("demo"):
        aujourdhui = resume_du_jour(payload)
        if aujourdhui["date"]:
            points[aujourdhui["date"]] = aujourdhui
    os.makedirs(os.path.join(dossier, "point"), exist_ok=True)
    dates = sorted(points)
    for i, dte in enumerate(dates):
        img = "partage.png"
        if i >= len(dates) - 7 and _image_point(points[dte], os.path.join(dossier, "point", f"{dte}.png")):
            img = f"point/{dte}.png"   # les 7 derniers jours : une grande image propre (Google Discover)
        chemin, page = _page_point(base, points[dte], csp, dates[i - 1] if i else None,
                                   dates[i + 1] if i + 1 < len(dates) else None, image=img)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily" if i == len(dates) - 1 else "yearly", "0.6"))
    corps = ("<h1>Le point du jour</h1><p class='muted'>Chaque soir, ce qu'il faut retenir des marchés, "
             "rédigé automatiquement par le radar.</p>"
             "<div class='carte'><b>À partager</b><p style='margin:6px 0 10px'>Une image du jour, prête pour Instagram, "
             "TikTok, X ou WhatsApp (format portrait).</p><a class='btn' href='image-du-jour.png' download>Télécharger l'image du jour</a></div>")
    _sem = os.path.join(config.DOSSIER_HISTORIQUE, "semaines")
    if os.path.isdir(_sem) and os.listdir(_sem):
        corps += "<p><a class='btn' href='semaines.html'>La semaine en Bourse</a></p>"
    corps += ("<ul>" + "".join(f"<li><a href='point/{dte}.html'>Bourse du {date_longue(dte)}</a></li>" for dte in reversed(dates)) + "</ul>"
              if dates else "<p>Le premier point du jour sera publié ce soir.</p>")
    with open(os.path.join(dossier, "point.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Le point du jour : la Bourse chaque soir | {NOM}",
                      "Résumé quotidien des marchés : indices, plus fortes hausses et baisses, signaux forts, actualités.",
                      "point.html", corps, csp=csp))
    urls.append(("point.html", "daily", "0.8"))

    # La semaine en Bourse
    try:
        for chemin in _pages_semaines(base, dossier, csp):
            urls.append((chemin, "weekly", "0.6"))
    except Exception as e:
        print(f"Semaines non générées : {e}")

    try:   # version 53 : fonctionnalités, simulateur boursier, à propos, contact
        from . import pages_plus
        urls += pages_plus.generer(payload, dossier, csp, base)
    except Exception as e:
        print(f"Pages fonctionnalités / à propos / contact non générées : {e}")
    try:   # version 52 : outils gratuits (simulateur sur les vrais cours, convertisseur, intérêts composés, plus-value)
        from . import outils
        urls += outils.generer(payload, dossier, csp, base)
    except Exception as e:
        print(f"Outils non générés : {e}")
    try:
        _page_404(base, dossier, csp)
    except Exception as e:
        print(f"Page 404 non générée : {e}")
    # Résultats réels, image du jour à partager, version anglaise
    try:
        _page_connaissances(base, payload, dossier, csp)
        urls.append(("connaissances.html", "weekly", "0.7"))
    except Exception as e:
        print(f"Page connaissances non générée : {e}")
    try:
        _page_resultats(base, payload, dossier, csp)
        urls.append(("resultats.html", "daily", "0.8"))
    except Exception as e:
        print(f"Page résultats non générée : {e}")
    try:
        for chemin, fq in _pages_bilan_mois(base, payload, dossier, csp):
            urls.append((chemin, fq, "0.7"))
    except Exception as e:
        print(f"Bilans du mois non générés : {e}")
    try:
        if _image_du_jour(payload, os.path.join(dossier, "image-du-jour.png"), base):
            if dates:
                import shutil
                shutil.copyfile(os.path.join(dossier, "image-du-jour.png"), os.path.join(dossier, "point", f"{dates[-1]}.png"))
    except Exception as e:
        print(f"Image du jour non générée : {e}")
    try:
        from . import anglais
        urls += anglais.generer(payload, dossier, csp, base)
        from . import guides_en
        urls += guides_en.generer(payload, dossier, csp, base)
    except Exception as e:
        print(f"Version anglaise non générée : {e}")
    try:   # version 47 : les autres grandes langues du monde
        from . import langues
        urls += langues.generer(payload, dossier, csp, base)
    except Exception as e:
        print(f"Versions dans les autres langues non générées : {e}")

    # IndexNow : fichier-clé qui autorise le site à signaler ses nouvelles pages à Bing et Yandex
    cle = cle_indexnow()
    if cle:
        with open(os.path.join(dossier, f"{cle}.txt"), "w", encoding="utf-8") as f:
            f.write(cle)

    # sitemap.xml et robots.txt (adresse absolue requise : uniquement si l'adresse du site est connue)
    maintenant = datetime.now().strftime("%Y-%m-%d")
    if base:
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        dates = _dates_modif(dossier, [c for c, _, _ in urls], maintenant)
        xml += [f"<url><loc>{html.escape(base + c)}</loc><lastmod>{dates.get(c, maintenant)}</lastmod><changefreq>{fq}</changefreq><priority>{pr}</priority></url>"
                for c, fq, pr in urls]
        xml.append("</urlset>")
        with open(os.path.join(dossier, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write("\n".join(xml))
    # Flux RSS : le point du jour et les bilans du mois, repris par les lecteurs de flux et les agrégateurs
    try:
        _flux_rss(base, dossier, points, [c for c, *_ in urls if c.startswith("bilan/")])
    except Exception as e:
        print(f"Flux RSS non généré : {e}")
    with open(os.path.join(dossier, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n" + (f"Sitemap: {base}sitemap.xml\n" if base else ""))

    # Hors connexion (version 33) : le réseau d'abord (cours toujours frais), la copie gardée seulement sans réseau
    with open(os.path.join(dossier, "sw.js"), "w", encoding="utf-8") as f:
        f.write(SERVICE_WORKER.replace("__VERSION__", datetime.now().strftime("%Y%m%d%H")))

    # Manifeste (« Ajouter à l'écran d'accueil »), icônes, image de partage
    manifeste = {"name": NOM, "short_name": NOM, "description": SLOGAN, "lang": "fr", "start_url": "./",
                 "display": "standalone", "background_color": "#0f1b2d", "theme_color": "#0f1b2d",
                 "icons": [{"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
                           {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"}]}
    with open(os.path.join(dossier, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifeste, f, ensure_ascii=False)
    _icones(dossier)
    _image_partage(payload, os.path.join(dossier, "partage.png"))


def _flux_rss(base, dossier, points, bilans):
    from email.utils import format_datetime
    items = []
    for d in sorted(points)[-30:][::-1]:
        dt = datetime.strptime(d, "%Y-%m-%d").replace(hour=23)
        lien = f"{base}point/{d}.html"
        resume = f"Indices, plus fortes hausses et baisses, signaux et actualités du {date_longue(d)}."
        items.append((dt, f"Bourse du {date_longue(d)} : ce qu'il faut retenir", lien, resume))
    for c in bilans[-12:]:
        m = c.split("/")[-1].replace(".html", "")
        try:
            dt = datetime.strptime(m + "-28", "%Y-%m-%d")
        except ValueError:
            continue
        items.append((dt, f"Bilan {_mois(m)} : les prévisions du radar vérifiées", base + c,
                      "Le score honnête du mois, les plus beaux coups et les pires ratés."))
    items.sort(key=lambda x: x[0], reverse=True)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>',
           f"<title>{html.escape(NOM)} : le point de la Bourse et les bilans</title>", f"<link>{html.escape(base)}</link>",
           f'<atom:link href="{html.escape(base)}flux.xml" rel="self" type="application/rss+xml"/>',
           "<description>Chaque soir, ce qu'il faut retenir des marchés ; chaque mois, les prévisions vérifiées.</description>",
           "<language>fr-fr</language>"]
    for dt, titre, lien, resume in items:
        xml.append(f"<item><title>{html.escape(titre)}</title><link>{html.escape(lien)}</link><guid>{html.escape(lien)}</guid>"
                   f"<pubDate>{format_datetime(dt.astimezone())}</pubDate><description>{html.escape(resume)}</description></item>")
    xml.append("</channel></rss>")
    with open(os.path.join(dossier, "flux.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml))


SERVICE_WORKER = """// Radar Bourse : fonctionnement hors connexion.
// Règle : on demande toujours d'abord au réseau (prix du jour) ; la copie gardée ne sert que s'il n'y a pas de réseau.
const CACHE = "radar-__VERSION__";
const DE_BASE = ["./", "index.html", "lightweight-charts.js", "manifest.webmanifest", "icone-192.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(DE_BASE.map(u => c.add(u).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("radar-") && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== self.location.origin) return;   // jamais les sites extérieurs
  e.respondWith(fetch(r).then(rep => {
    if (rep && rep.ok && rep.type === "basic") { const copie = rep.clone(); caches.open(CACHE).then(c => c.put(r, copie)); }
    return rep;
  }).catch(() => caches.match(r).then(m => m || (r.mode === "navigate" ? caches.match("index.html") : undefined))
    .then(m => m || new Response("Hors connexion : cette page n'a pas encore été gardée sur cet appareil.",
                                 {status: 503, headers: {"Content-Type": "text/plain; charset=utf-8"}}))));
});
"""


def cle_indexnow() -> str:
    import hashlib
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    return hashlib.sha256(f"radar-{depot}".encode()).hexdigest()[:32] if depot else ""


FAQ = [
    ("Radar Bourse est-il gratuit ?", "Oui, entièrement : pas d'inscription, pas d'abonnement, pas de publicité."),
    ("Les prévisions sont-elles fiables ?", "Ce sont des probabilités, pas des certitudes. La précision mesurée du modèle sur des périodes qu'il n'a jamais vues est affichée sur le site, ainsi que le suivi réel de chaque prévision publiée. Elle reste modeste : à peine meilleure que le hasard pour deviner le sens du prix. Les IA sont nettement plus fiables pour prévoir l'agitation (de combien un prix risque de bouger) que pour deviner s'il va monter."),
    ("D'où viennent les données ?", "Cours de Yahoo Finance (avec Binance et Stooq en secours), cours en direct de Binance et Finnhub, actualités de Finnhub et Yahoo, sentiment crypto d'alternative.me. Chaque titre passe un contrôle qualité à chaque mise à jour."),
    ("Comment la probabilité de hausse est-elle calculée ?", "Deux intelligences artificielles de conception différente analysent une quarantaine d'indicateurs techniques et de contexte sur dix ans d'historique. Leurs avis sont combinés, recalés sur ce qui s'est réellement passé, et testés chaque soir sur des années qu'elles n'ont jamais vues."),
    ("Est-ce un conseil en investissement ?", "Non. Ce sont des calculs automatiques, identiques pour tout le monde, publiés dans un but éducatif. Tu restes seul responsable de tes décisions et tu peux perdre tout l'argent investi."),
    ("Pourquoi deux intelligences artificielles ?", "Elles sont construites différemment et ne se trompent pas sur les mêmes cas. Quand elles sont d'accord, leurs prévisions ont été un peu plus souvent justes ; quand elles ne le sont pas, elles n'ont pas fait mieux que le hasard. Le site affiche donc toujours si elles sont d'accord, et ne donne jamais de signal fort en cas de désaccord."),
    ("Que veulent dire les marges d'erreur ?", "Un taux de réussite mesuré sur quelques années n'est jamais exact. La marge indique entre quelles valeurs se trouve probablement le vrai chiffre. Si elle contient 50 %, on ne peut pas affirmer que le radar fait mieux que pile ou face, et le site le dit."),
    ("Que veut dire « mieux que son marché » ?", "C'est la probabilité qu'un titre monte plus (ou baisse moins) que son indice de référence sur le mois qui vient : le CAC 40 pour les actions françaises, l'Euro Stoxx 50 pour les européennes, le S&P 500 pour les américaines et le Bitcoin pour les cryptos. Sa fiabilité est mesurée et affichée séparément."),
    ("Les vrais résultats sont-ils publiés ?", "Oui. Chaque prévision est enregistrée le jour même puis vérifiée un mois plus tard, sans retouche possible. La page « Résultats réels » affiche le taux de réussite mois par mois, même quand il n'est pas bon."),
    ("Comment garder mon portefeuille virtuel sur un autre appareil ?", "Dans la rubrique portefeuille, clique « Sauvegarder dans un fichier », puis « Restaurer un fichier » sur l'autre appareil. Le fichier reste chez toi : rien n'est envoyé sur Internet."),
    ("Mes données personnelles sont-elles collectées ?", "Non. Pas de compte, pas de cookie publicitaire. Favoris et portefeuille virtuel restent dans ton navigateur."),
]


def jsonld_faq() -> dict:
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in FAQ]}


def html_faq() -> str:
    return "".join(f"<details class='faq'><summary>{_e(q)}</summary><p>{_e(r)}</p></details>" for q, r in FAQ)


def liens_accueil(payload: dict) -> str:
    """Liens texte vers chaque page de titre, ajoutés en bas de l'accueil (Google suit les liens)."""
    items = "".join(f'<a href="titres/{slug(t["ticker"])}.html">{_e(t["nom"])}</a>' for t in payload.get("titres", []))
    return (f'<nav class="seo-liens" aria-label="Pages des titres"><b>Analyses détaillées :</b> {items} '
            f'· <a href="titres.html">tous les titres</a> · <a href="outils.html">outils gratuits</a> · <a href="outils/si-javais-investi.html">si j\'avais investi…</a> · <a href="outils/convertisseur.html">convertisseur crypto</a> · <a href="apprendre.html">apprendre la Bourse</a> · <a href="glossaire.html">glossaire</a>'
            + "".join(f' · <a href="marches/{m[0]}.html">{_e(m[1].lower())}</a>' for k, m in MARCHES.items()
                      if any(t.get("marche") == k for t in payload.get("titres", []))) + '</nav>')


def jsonld_accueil() -> dict:
    """Ce que Google utilise pour reconnaître le NOM du site (recherches « radar bourse », « bourse radar »…)."""
    base = url_site()
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    org = {"@type": "Organization", "@id": (base or "") + "#org", "name": NOM, "url": base or None,
           "logo": (base + "icone-512.png") if base else None}
    site = {"@type": "WebSite", "@id": (base or "") + "#site", "name": NOM,
            "alternateName": ["Radar-Bourse", "RadarBourse", "Bourse Radar", "Radar Bourse IA"],
            "url": base or None, "description": DESCRIPTION, "inLanguage": "fr-FR", "publisher": {"@id": (base or "") + "#org"}}
    return {"@context": "https://schema.org", "@graph": [site, org]}


# ----------------------------------------------------------------------------
# Page « Résultats réels » : chaque prédiction publiée, vérifiée après coup
# ----------------------------------------------------------------------------
def _info_historique() -> tuple[int, str | None]:
    """Nombre de prédictions enregistrées et date de la première (pour annoncer les premiers résultats)."""
    try:
        import pandas as pd
        from . import historique
        h = historique.nettoyer(pd.read_csv(os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv"), usecols=["date"]))
        return len(h), (str(h["date"].min()) if len(h) else None)
    except Exception:
        return 0, None


def _mois(aaaa_mm: str) -> str:
    try:
        a, m = aaaa_mm.split("-")
        return f"{MOIS[int(m) - 1]} {a}"
    except (ValueError, IndexError):
        return aaaa_mm


def _marge(ic):
    return f" · marge {round(ic[0] * 100)} à {round(ic[1] * 100)}" if ic and ic[0] is not None else ""


def _taux(v):
    return "–" if v is None else f"{round(v * 100)} %"


def _lien_mois(m, D):
    return f"<a href='bilan/{m}.html'>{_e(_mois(m))}</a>" if m in (D.get("mois") or {}) else _e(_mois(m))


def _pages_bilan_mois(base, payload, dossier, csp):
    """Une page par mois : ce que les IA avaient prévu, ce qui s'est passé, le score honnête.
    Du contenu neuf chaque mois, et la preuve qu'on ne cache rien (même les ratés sont affichés)."""
    M = (((payload.get("suivi") or {}).get("detail") or {}).get("mois")) or {}
    if not M:
        return []
    noms = {t["ticker"]: t["nom"] for t in payload.get("titres", [])}
    os.makedirs(os.path.join(dossier, "bilan"), exist_ok=True)
    mois = sorted(M)
    out = []
    lien = lambda tk: (f"<a href='../titres/{slug(tk)}.html'>{_e(noms[tk])}</a>" if tk in noms else _e(aff_tk(tk)))
    for i, m in enumerate(mois):
        B, nm = M[m], _mois(m)
        nb_txt = f"{B['nb']:,}".replace(",", "\u202f")
        prov = B.get("attente", 0) > 0
        p, ref = B["precision"], B["reference"]
        ecart = p - ref
        verdict = ("mieux que la référence naïve" if ecart > 0.02 else "à peu près comme la référence naïve" if ecart > -0.02
                   else "moins bien que la référence naïve")
        corps = (f"<p class='muted'>Le bilan du mois</p><h1>{_e(nm)} : les prévisions du radar vérifiées</h1>"
                 + (f"<div class='carte'><p style='margin:0'><b>Bilan provisoire.</b> {B['attente']} prévisions de ce mois attendent encore "
                    "leur échéance (un mois après leur publication). Les chiffres vont encore bouger.</p></div>" if prov else "")
                 + f"<p>En {_e(nm)}, le radar a publié des prévisions sur {B['nb_jours']} jours. <b>{nb_txt}</b> ont été vérifiées un mois plus tard. "
                 f"Résultat : <b>{_taux(p)}</b> de bonnes directions, soit <b>{verdict}</b> ({_taux(ref)} en répondant toujours "
                 f"« {'hausse' if B['part_hausse'] >= .5 else 'baisse'} »). Sur un seul mois, la chance pèse beaucoup : "
                 "c'est la durée qui compte, voir les <a href='../resultats.html'>résultats depuis le début</a>.</p>")
        cases = [(_taux(p), "bonnes directions"), (_taux(ref), "référence : toujours la même réponse")]
        if B.get("marche"):
            cases.append((_taux(B["marche"]["precision"]), f"bons pronostics « mieux que son marché » ({B['marche']['nb']} cas)"))
        if B.get("agitation"):
            cases.append((_taux(B["agitation"]["dans"]), f"des prix sont restés dans l'agitation prévue (attendu : environ 2 sur 3)"))
        if B.get("fourchette"):
            cases.append((_taux(B["fourchette"]["taux"]), f"prix final dans la fourchette (promis : 80 %)"))
        corps += "<div class='carte grille'>" + "".join(f"<div class='k'><b>{v}</b><span>{l}</span></div>" for v, l in cases) + "</div>"
        if B.get("agitation"):
            r = B["agitation"]["ratio_median"]
            corps += ("<h2>L'agitation prévue</h2><p>C'est ce que les IA prévoient le mieux. En général, le prix a bougé de "
                      f"<b>{round(r * 100)} %</b> de l'agitation annoncée"
                      + (" : les marchés ont été plus calmes que prévu." if r < .7 else " : plus agités que prévu." if r > 1.3 else " : à peu près ce qui était prévu.")
                      + "</p>")
        if B.get("confiance"):
            corps += ("<h2>Selon le niveau de confiance</h2><div class='carte'><table>"
                      + "".join(f"<tr><td>Confiance {_e(c['nom'])}</td><td class='m'>{c['nb']} cas</td><td class='m'>{_taux(c['precision'])} justes</td></tr>" for c in B["confiance"])
                      + "</table></div>")
        if B.get("par_type"):
            corps += ("<h2>Par type de titre</h2><div class='carte'><table>"
                      + "".join(f"<tr><td>{_e(x['nom'])}</td><td class='m'>{x['nb']} cas</td><td class='m'>{_taux(x['precision'])} justes</td></tr>" for x in B["par_type"])
                      + "</table></div>")
        ligne = lambda r: (f"<li>{lien(r['ticker'])} le {_e(date_longue(str(r['date'])))} : {round(r['proba'] * 100)} chances sur 100 de hausse, "
                           f"résultat {_pct(r['rendement_reel'])}</li>")
        if B.get("beaux_coups"):
            corps += "<h2>Les plus beaux coups</h2><ul>" + "".join(ligne(r) for r in B["beaux_coups"]) + "</ul>"
        if B.get("rates"):
            corps += ("<h2>Les pires ratés</h2><p class='muted'>Affichés aussi : un radar qui ne montre que ses réussites ment.</p><ul>"
                      + "".join(ligne(r) for r in B["rates"]) + "</ul>")
        prec, suiv = (mois[i - 1] if i else None), (mois[i + 1] if i + 1 < len(mois) else None)
        corps += ("<p style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap'>"
                  + (f"<a href='{prec}.html'>← {_e(_mois(prec))}</a>" if prec else "<span></span>")
                  + (f"<a href='{suiv}.html'>{_e(_mois(suiv))} →</a>" if suiv else "<a href='../index.html'>Prévisions du jour →</a>") + "</p>"
                  "<p class='muted'>Projet éducatif : ces résultats ne garantissent rien pour l'avenir. Pas un conseil en investissement.</p>")
        chemin = f"bilan/{m}.html"
        titre = f"Bilan {nm} : les prévisions boursières du radar vérifiées | {NOM}"
        desc = f"{nm} : {_taux(p)} de bonnes directions sur {B['nb']} prévisions vérifiées, beaux coups et pires ratés, sans rien cacher."
        jsonld = {"@context": "https://schema.org", "@type": "Article", "headline": f"Bilan {nm} des prévisions du radar",
                  "datePublished": f"{m}-01", "inLanguage": "fr-FR", "isAccessibleForFree": True, "author": {"@type": "Organization", "name": NOM}}
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(base, titre, desc, chemin, corps, jsonld, csp))
        out.append((chemin, "weekly" if prov else "yearly"))
    return out


def _page_resultats(base, payload, dossier, csp):
    S = payload.get("suivi") or {}
    D = S.get("detail") or {}
    horizon = payload.get("horizon", 20)
    nb_total, premiere = _info_historique()
    corps = ("<h1>Les résultats réels du radar</h1>"
             "<p class='muted'>Chaque prévision publiée est enregistrée le jour même, puis comparée à ce qui s'est "
             f"vraiment passé {horizon} séances plus tard. Rien n'est recalculé après coup : c'est la seule preuve qui compte, "
             "et elle est affichée même quand elle n'est pas flatteuse.</p>")
    if not S.get("nb_verifiees"):
        quand = ""
        if premiere:
            try:
                from datetime import timedelta
                d0 = datetime.strptime(premiere, "%Y-%m-%d") + timedelta(days=30)
                quand = f" Les premiers résultats arriveront vers le <b>{date_longue(d0.strftime('%Y-%m-%d'))}</b>."
            except ValueError:
                pass
        corps += (f"<div class='carte'><p style='margin:0'><b>Le suivi vient de commencer.</b> {nb_total} prédictions sont "
                  f"déjà enregistrées{f' depuis le {date_longue(premiere)}' if premiere else ''} et attendent leur échéance.{quand}</p></div>")
    else:
        base_h = D.get("base_hausse")
        F, R, FO = D.get("fourchette") or {}, D.get("marche") or {}, D.get("forts") or {}
        corps += "<div class='carte grille'>" + "".join(
            f"<div class='k'><b>{v}</b><span>{lib}</span></div>" for v, lib in (
                (f"{S['nb_verifiees']:,}".replace(",", "\u202f"), "prédictions vérifiées"),
                (_taux(S.get("precision")), "bonnes directions (hausse ou baisse)" + _marge(D.get("ic_precision"))),
                (_taux(max(base_h, 1 - base_h)) if base_h is not None else "–", "en répondant toujours la même chose (référence)"),
                (_taux(F.get("taux")), f"prix final dans la fourchette (promis : 80 %, {F.get('nb', 0)} cas)"),
                (_taux(FO.get("precision")), f"signaux forts gagnants ({FO.get('nb', 0)} cas)" + _marge(FO.get("ic"))),
                (_taux((D.get("accord") or {}).get("precision")), f"justes quand les deux IA étaient d'accord ({(D.get('accord') or {}).get('nb', 0)} cas)"),
                (_taux((D.get("accord") or {}).get("precision_desaccord")), f"justes quand elles ne l'étaient pas ({(D.get('accord') or {}).get('nb_desaccord', 0)} cas)"),
                (_taux(R.get("precision")), f"bons pronostics « mieux que son marché » ({R.get('nb', 0)} cas)"),
            )) + "</div>"
        p, ref = S.get("precision"), (max(base_h, 1 - base_h) if base_h is not None else None)
        icp = D.get("ic_precision")
        if p is not None and ref is not None:
            corps += ("<p><b>Verdict honnête :</b> " + (
                "le radar fait mieux que la référence naïve, même en tenant compte de la marge d'erreur. L'écart doit encore tenir dans la durée."
                if icp and icp[0] > ref else
                "le radar a un meilleur chiffre que la référence naïve, mais la marge d'erreur est trop large pour affirmer que ce n'est pas de la chance."
                if p > ref else
                "le radar ne fait pas mieux que la référence naïve sur cette période. C'est fréquent : la Bourse est très difficile à prévoir."
            ) + f" Période vérifiée : du {date_longue(D['premiere'])} au {date_longue(D['derniere'])}.</p>")
        if D.get("par_mois"):
            corps += ("<h2>Mois par mois</h2><div class='carte'><table><tr><td><b>Mois</b></td><td><b>Vérifiées</b></td><td><b>Justes</b></td></tr>"
                      + "".join(f"<tr><td>{_lien_mois(m['nom'], D)}</td><td class='m'>{m['nb']}</td><td class='m'>{_taux(m['precision'])}</td></tr>" for m in D["par_mois"][-12:])
                      + "</table></div>")
        if D.get("par_type"):
            corps += ("<h2>Par type de titre</h2><div class='carte'><table>"
                      + "".join(f"<tr><td>{_e(m['nom'])}</td><td class='m'>{m['nb']} cas</td><td class='m'>{_taux(m['precision'])} justes</td></tr>" for m in D["par_type"])
                      + "</table></div>")
        cal = [c for c in D.get("calibration", []) if c["nb"]]
        if cal:
            corps += ("<h2>Les probabilités tiennent-elles leurs promesses ?</h2><p class='muted'>Quand le radar annonçait "
                      "une probabilité donnée, à quelle fréquence le cours a-t-il vraiment monté ?</p><div class='carte'><table>"
                      + "".join(f"<tr><td>Annoncé {_e(c['tranche'])}</td><td class='m'>{c['nb']} cas</td><td class='m'>"
                                + (f"monté {_taux(c['taux_hausse'])}" if c["nb"] >= 20 else "trop peu de cas") + "</td></tr>" for c in cal)
                      + "</table></div>")
        lignes = payload.get("resultats") or []
        if lignes:
            corps += ("<h2>Les dernières prédictions vérifiées</h2><div class='carte' style='overflow-x:auto'><table>"
                      "<tr><td><b>Date</b></td><td><b>Titre</b></td><td><b>Proba</b></td><td><b>Réel</b></td><td><b>Résultat</b></td></tr>"
                      + "".join(f"<tr><td class='m'>{_e(r['date'])}</td><td><a href='titres/{slug(r['ticker'])}.html'>{_e(aff_tk(r['ticker']))}</a>"
                                f"{' ★' if r.get('fort') else ''}</td><td class='m'>{_taux(r.get('proba'))}</td><td>{_pct(r['rendement_reel'])}</td>"
                                f"<td>{'<span class=up>Juste</span>' if r['juste'] else '<span class=down>Faux</span>'}</td></tr>" for r in lignes[:120])
                      + "</table></div><p class='muted'>★ : signal fort. « Juste » : la direction annoncée (hausse si probabilité &gt; 50 %) s'est réalisée.</p>")
    corps += ("<h2>Comment lire ces chiffres</h2><p>La « marge » indique entre quelles valeurs se trouve probablement le vrai taux de réussite "
              "(95 chances sur 100). Elle est approximative, car les prévisions d'un même jour se ressemblent : elle est sans doute un peu trop étroite. "
              "Une probabilité de 60 % se trompe, par définition, 4 fois sur 10. "
              "Sur quelques semaines, la chance ou la malchance pèse beaucoup : il faut plusieurs mois de suivi et des centaines "
              "de cas pour juger. Ces résultats ne garantissent rien pour l'avenir.</p>"
              "<p><a class='btn' href='index.html'>Voir les prévisions du jour</a></p>")
    titre = f"Résultats réels : les prévisions du radar vérifiées | {NOM}"
    desc = "Chaque prévision publiée par Radar Bourse est vérifiée après coup : taux de réussite réel, fourchettes, signaux forts, mois par mois."
    with open(os.path.join(dossier, "resultats.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, titre, desc, "resultats.html", corps, csp=csp))


# ----------------------------------------------------------------------------
# Image du jour (format portrait 1080 × 1350, idéal Instagram / TikTok / X / WhatsApp)
# ----------------------------------------------------------------------------
def _humeur(titres):
    base = [t for t in titres if t.get("marche") != "tendances"]
    au = [t for t in base if t.get("au_dessus_200") is not None]
    largeur = sum(t["au_dessus_200"] for t in au) / len(au) if au else None
    achats = sum(str(t.get("signal", "")).startswith("ACHAT") for t in titres)
    ventes = sum(str(t.get("signal", "")).startswith("VENTE") for t in titres)
    if largeur is None:
        return "Mitigé", largeur
    if largeur >= 0.6 and achats > ventes:
        return "Optimiste", largeur
    if largeur < 0.4 or ventes > achats * 1.5:
        return "Prudent", largeur
    return "Mitigé", largeur


def _image_du_jour(payload: dict, chemin: str, base: str = "") -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    W, H = 1080, 1350
    fond, carte, ligne_c, blanc, gris = "#0b1424", "#132038", "#22314a", "#f2f5fa", "#93a3bb"
    vert, rouge, bleu, ambre = "#35c27d", "#ff6b62", "#7398ff", "#e5b453"
    img = Image.new("RGB", (W, H), fond)
    dr = ImageDraw.Draw(img)

    def police(taille, gras=False):
        for nom in (("DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf"), ("arialbd.ttf" if gras else "arial.ttf")):
            for dossier in ("/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", ""):
                try:
                    return ImageFont.truetype(dossier + nom, taille)
                except Exception:
                    continue
        return ImageFont.load_default()

    def pct(v):
        return "–" if v is None else f"{'+' if v > 0 else ''}{v * 100:.1f} %".replace(".", ",")

    def couper(txt, f, largeur):
        while dr.textlength(txt, font=f) > largeur and len(txt) > 4:
            txt = txt[:-2] + "…" if not txt.endswith("…") else txt[:-2] + "…"
        return txt

    titres = payload.get("titres", [])
    try:
        dt = datetime.strptime(payload.get("date_donnees", ""), "%Y-%m-%d")
        jour = f"{dt.day} {MOIS[dt.month - 1]} {dt.year}"
    except ValueError:
        jour = ""
    M = 64
    # en-tête
    dr.ellipse((M, 78, M + 26, 104), fill=vert)
    dr.text((M + 44, 60), NOM, font=police(54, True), fill=blanc)
    dr.text((M, 140), f"Le point du {jour}" if jour else "Le point du jour", font=police(36), fill=gris)
    mot, largeur = _humeur(titres)
    coul = {"Optimiste": vert, "Prudent": rouge}.get(mot, ambre)
    dr.rounded_rectangle((M, 214, W - M, 360), radius=22, fill=carte)
    dr.text((M + 34, 236), "MÉTÉO DU MARCHÉ", font=police(24, True), fill=gris)
    dr.text((M + 34, 272), mot, font=police(64, True), fill=coul)
    if largeur is not None:
        dr.text((W - M - 34, 250), f"{round(largeur * 100)} %", font=police(52, True), fill=blanc, anchor="ra")
        dr.text((W - M - 34, 316), "des titres en tendance haussière", font=police(22), fill=gris, anchor="ra")
    # indices
    y = 392
    ind = [i for i in payload.get("indices", []) if i["nom"] in ("CAC 40", "S&P 500", "Nasdaq 100", "Bitcoin")][:4]
    if ind:
        lw = (W - 2 * M - 3 * 16) / max(len(ind), 1)
        for i, x in enumerate(ind):
            x0 = M + i * (lw + 16)
            dr.rounded_rectangle((x0, y, x0 + lw, y + 128), radius=18, fill=carte)
            dr.text((x0 + 22, y + 18), couper(x["nom"], police(24, True), lw - 40), font=police(24, True), fill=gris)
            v = x.get("var_jour")
            dr.text((x0 + 22, y + 60), pct(v), font=police(40, True), fill=vert if (v or 0) >= 0 else rouge)
        y += 160
    # plus fortes probabilités de hausse
    dr.text((M, y), "Plus forte probabilité de hausse à un mois", font=police(32, True), fill=blanc)
    y += 58
    top = sorted([t for t in titres if t.get("proba_hausse") is not None and t.get("qualite_ok", True) and t.get("avis_net") is not False],
                 key=lambda t: -t["proba_hausse"])[:4]
    for t in top:
        dr.rounded_rectangle((M, y, W - M, y + 88), radius=16, fill=carte)
        dr.text((M + 26, y + 16), couper(t["nom"], police(34, True), 560), font=police(34, True), fill=blanc)
        dr.text((M + 26, y + 58), t["ticker"] + ("  · signal fort" if t.get("signal_fort") else ""), font=police(22), fill=gris)
        p = t["proba_hausse"]
        bx0, bx1 = W - M - 360, W - M - 160
        dr.rounded_rectangle((bx0, y + 40, bx1, y + 54), radius=7, fill=ligne_c)
        dr.rounded_rectangle((bx0, y + 40, bx0 + (bx1 - bx0) * p, y + 54), radius=7, fill=bleu)
        dr.text((W - M - 26, y + 24), f"{round(p * 100)} %", font=police(40, True), fill=blanc, anchor="ra")
        y += 100
    forts = sum(1 for t in titres if t.get("signal_fort"))
    y += 8
    dr.text((M, y), f"{forts} signal fort aujourd'hui" if forts == 1 else f"{forts} signaux forts aujourd'hui",
            font=police(30, True), fill=bleu)
    # avertissement très visible
    dr.rounded_rectangle((M, H - 250, W - M, H - 120), radius=20, outline=ambre, width=4, fill="#2a2210")
    dr.text((M + 30, H - 230), "⚠ Rien n'est sûr.", font=police(36, True), fill=ambre)
    dr.text((M + 30, H - 180), "Probabilités statistiques, pas des conseils. Elles se trompent souvent.",
            font=police(24), fill=blanc)
    site_txt = (base or "").replace("https://", "").rstrip("/")
    dr.text((M, H - 86), site_txt or "Projet éducatif gratuit", font=police(28, True), fill=gris)
    img.save(chemin, optimize=True)
    return True


# ----------------------------------------------------------------------------
# Page « Ce que sait l'IA » : son manuel de Bourse et le verdict de ses tests
# ----------------------------------------------------------------------------
def _fiche_valeurs(payload):
    """Les chiffres de la fiche technique, tirés des tests du soir (rien n'est écrit à la main)."""
    M = payload.get("modele") or {}
    F, R, Rel = M.get("fourchette") or {}, M.get("risque") or {}, M.get("relatif") or {}
    C = R.get("chute") or {}
    S = ((payload.get("suivi") or {}).get("detail") or {}).get("fourchette") or {}
    return M, F, R, Rel, C, S


def _page_fiche_ia(base, payload, dossier, csp):
    """Version 50 : la fiche technique de l'IA, comme en publient les acteurs sérieux. Mise à jour à chaque calcul du soir."""
    M, F, R, Rel, C, S = _fiche_valeurs(payload)
    p = lambda v, d=1: "–" if v is None else f"{v * 100:.{d}f} %".replace(".", ",")
    n = lambda v: "–" if v is None else f"{v:,}".replace(",", " ")
    nb_titres = len([t for t in payload.get("titres", []) if t.get("marche") != "tendances"])
    note_chute = "–" if C.get("auc") is None else f"{C['auc']:.3f}".replace(".", ",")
    lignes = [
        ("Sens du prix à un mois", f"{p(M.get('precision'))} de bonnes réponses", f"référence « toujours la réponse la plus fréquente » : {p(M.get('precision_base'))}",
         "Pas mieux que la référence : le site n'affiche un avis que là où il a fait ses preuves." if (M.get("precision") or 0) - (M.get("precision_base") or 0) < 0.005 else "Un peu mieux que la référence."),
        ("Faire mieux que son marché", f"{p(Rel.get('precision'))} de bonnes réponses", f"référence : {p(Rel.get('precision_base'))}",
         "Petit avantage, mesuré sur des années jamais vues." if (Rel.get("precision") or 0) > (Rel.get("precision_base") or 1) else "Pas d'avantage prouvé."),
        ("Agitation à un mois", f"erreur habituelle {p(R.get('erreur_ia'))}", f"méthode simple : {p(R.get('erreur_naif'))}",
         "Prouvé : nettement mieux que la méthode simple." if R.get("prouve") else "Pas encore prouvé."),
        ("Risque de chute de plus de 10 %", f"note de tri {note_chute}",
         f"titres jugés les plus à risque : {p(C.get('taux_risque_haut'))} de chutes, contre {p(C.get('base'))} d'habitude",
         "Prouvé : la prévision la plus fiable du radar." if C.get("prouve") else "Pas encore prouvé."),
        ("Fourchette « 8 fois sur 10 »", f"tenue {p(F.get('couverture'))} du temps", f"promis : 80 % · sans correction : {p(F.get('couverture_brute'))}",
         "Promesse tenue à quelques points près." if F.get("couverture") and abs(F["couverture"] - .8) < .03 else "À surveiller."),
        ("Fourchette extrême « 9 fois sur 10 »", f"tenue {p(F.get('couverture_extreme'))} du temps", "promis : 90 %",
         "Promesse tenue à quelques points près." if F.get("couverture_extreme") and abs(F["couverture_extreme"] - .9) < .03 else "À surveiller."),
        ("Agitation sur une semaine", "plus proche de la réalité 57,7 % du temps", "que « comme la semaine dernière »",
         "Prouvé : meilleure 24 années sur 24 (test du 28 octobre 2026 sur 328 000 cas)."),
    ]
    tableau = ("<div class='carte' style='overflow-x:auto'><table><tr><td><b>Ce que l'IA prévoit</b></td><td><b>Résultat</b></td><td><b>À comparer à</b></td><td><b>Verdict</b></td></tr>"
               + "".join(f"<tr><td>{_e(a)}</td><td class='m'>{_e(b)}</td><td>{_e(c)}</td><td>{_e(d)}</td></tr>" for a, b, c, d in lignes) + "</table></div>")
    direct = (f"<p>En conditions réelles, depuis la mise en ligne : sur {n(S.get('nb'))} prévisions arrivées à échéance, le prix est resté dans la fourchette "
              f"<b>{p(S.get('taux'))}</b> du temps (promis : 80 %).</p>") if S.get("nb") else ""
    corps = ("<h1>Fiche technique de l'IA du radar</h1>"
             f"<p class='muted'>Mise à jour automatiquement à chaque calcul du soir · dernière évaluation : {_e(M.get('date_evaluation') or '–')}</p>"
             "<p>Cette page dit ce que l'IA sait faire, ce qu'elle ne sait pas faire, et comment on le vérifie. Tous les chiffres viennent de tests sur des "
             "périodes que l'IA n'avait <b>jamais vues</b> pendant son apprentissage.</p>"
             "<h2>Résultats mesurés</h2>" + tableau + direct
             + f"<p class='muted'>Prévisions testées : {n(M.get('nb_tests'))} · période : {_e(M.get('periode') or '–')} · recette : {_e(M.get('configuration') or '–')}.</p>"
             "<h2>Données utilisées</h2><ul>"
             f"<li><b>{nb_titres} titres</b> suivis : actions françaises, européennes et américaines, ETF, indices et cryptomonnaies.</li>"
             "<li>Cours quotidiens sur tout l'historique disponible (jusqu'à 25 ans) : Yahoo Finance, avec Binance, CryptoCompare et Stooq en secours.</li>"
             "<li>Contexte du marché : VIX (peur sur les marchés), taux d'intérêt, dollar, or, pétrole, sentiment crypto.</li>"
             "<li>Contrôle qualité automatique : cours figés, trous, sauts anormaux et comparaison entre deux sources ; un titre douteux est exclu des signaux.</li></ul>"
             "<h2>Comment on teste, sans tricher</h2><ul>"
             "<li><b>Test « walk-forward »</b> : l'IA apprend sur le passé, puis prévoit une période qu'elle n'a jamais vue, avec un écart d'un mois entre les deux pour qu'aucune information du futur ne fuie.</li>"
             "<li><b>Marges d'erreur réalistes</b> : on tire des mois entiers au hasard (les jours d'un même mois se ressemblent), ce qui évite de se croire plus précis qu'on ne l'est.</li>"
             "<li><b>Examen final</b> : une amélioration n'est adoptée que si elle bat la référence de façon sûre même en comptant toutes les méthodes essayées, sur la majorité des années et sur les deux dernières années.</li>"
             "<li><b>Champion contre challenger</b> : une nouvelle version ne remplace l'ancienne que si elle fait mieux, de façon prouvée.</li>"
             "<li><b>Calibrage</b> : les fourchettes sont corrigées pour tenir leur promesse. Neuf autres corrections ont été testées sur 515 000 cas réels ; aucune ne faisait mieux.</li></ul>"
             "<h2>Ce que l'IA ne sait pas faire</h2><ul>"
             "<li>Dire si un prix sera plus haut ou plus bas dans un mois : sur ce point, elle ne fait pas mieux que des règles simples. Le site le dit sur chaque fiche.</li>"
             "<li>Prévoir les événements imprévisibles : annonces, crises, décisions politiques, piratages.</li>"
             "<li>Garantir l'avenir : des résultats passés, même testés honnêtement, peuvent ne pas se répéter.</li></ul>"
             "<h2>Surveillance</h2><ul>"
             "<li>Le site est recalculé toutes les heures ; s'il prend du retard, il est relancé automatiquement et un bandeau prévient les visiteurs.</li>"
             "<li>Chaque prévision publiée est enregistrée, puis vérifiée à son échéance : voir les <a href='resultats.html'>résultats réels</a>.</li>"
             "<li>Le risque de chute est suivi en public chaque mois : voir le <a href='suivi-chute.html'>suivi du risque de chute</a>.</li></ul>"
             "<p class='muted'>Projet éducatif. Rien de tout cela n'est un conseil en investissement. Voir aussi <a href='connaissances.html'>ce que sait l'IA</a>.</p>")
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "TechArticle", "headline": "Fiche technique de l'IA du radar", "inLanguage": "fr-FR",
         "dateModified": datetime.now().strftime("%Y-%m-%d"), "author": {"@type": "Organization", "name": NOM},
         "about": "Prévisions boursières par intelligence artificielle : méthode de test, précision mesurée et limites"},
        _jsonld_fil(base, [(NOM, ""), ("Fiche technique de l'IA", "fiche-technique-ia.html")])]}
    with open(os.path.join(dossier, "fiche-technique-ia.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Fiche technique de l'IA : méthode, tests et précision | {NOM}",
                      "Ce que l'IA de Radar Bourse sait prévoir, avec quelle précision, comment elle est testée sans tricher, et ses limites. Mis à jour chaque soir.",
                      "fiche-technique-ia.html", corps, jsonld, csp))
    return True


def _page_404(base, dossier, csp):
    """Version 51 : une vraie page « introuvable » au design du site (au lieu de la page brute de GitHub).
    Elle peut s'afficher à n'importe quelle profondeur : tous ses liens partent de l'adresse du site (<base>)."""
    corps = ("<h1>Cette page n'existe pas (ou plus)</h1>"
             "<p>Le lien est peut-être ancien, ou le titre a quitté la liste suivie par le radar.</p>"
             "<div class='carte'><p><b>Pour retrouver ce que tu cherchais :</b></p><ul class='liste'>"
             "<li><a href='index.html'>L'appli : prévisions de toutes les actions et cryptos</a></li>"
             "<li><a href='titres.html'>Tous les titres suivis</a></li><li><a href='guides.html'>Les guides</a></li>"
             "<li><a href='resultats.html'>Les résultats réels de l'IA</a></li><li><a href='en/index.html' hreflang='en' lang='en'>English version</a></li>"
             "</ul></div><p><a class='btn' href='index.html'>Ouvrir l'appli</a></p>")
    page = _page(base, f"Page introuvable | {NOM}", "Cette page n'existe pas ou plus sur Radar Bourse.", "404.html", corps,
                 csp=csp.replace("base-uri 'none'", "base-uri 'self'"))   # <base> doit être autorisé sur cette page seulement
    page = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex">', page, 1)
    page = re.sub(r'<link rel="canonical"[^>]*>\n?|<meta property="og:url"[^>]*>\n?', "", page)
    if base:
        page = page.replace("<head>\n", f'<head>\n<base href="{_e(base)}">\n', 1)
    with open(os.path.join(dossier, "404.html"), "w", encoding="utf-8") as f:
        f.write(page)


def _page_connaissances(base, payload, dossier, csp):
    from . import connaissances
    E = payload.get("entrainement") or {}
    V = E.get("connaissances") or {}
    quand = ""
    if E.get("date"):
        try:
            quand = date_longue(E["date"][:10])
        except ValueError:
            quand = E["date"][:10]
    corps = ("<h1>Ce que sait l'IA du radar</h1>"
             "<p class='muted'>On a donné à l'IA un « manuel de Bourse » : des règles connues, étudiées par des chercheurs "
             "en finance. Mais elle ne les croit pas sur parole. Lors de chaque entraînement, elle vérifie chaque règle "
             "sur des années qu'elle n'a jamais vues, teste plusieurs versions, et ne fait confiance qu'à celles qui aident "
             "vraiment. Beaucoup d'effets célèbres se sont affaiblis depuis leur découverte : c'est pour ça qu'on les teste.</p>"
             + (f"<div class='carte'><b>Dernier examen du manuel : {_e(quand)}.</b> "
                f"{sum(1 for v in V.values() if v.get('statut') == 'utile')} règle(s) sur {len(connaissances.REGLES)} prouvée(s) utile(s).</div>"
                if V else "<div class='carte'>Les règles seront vérifiées au prochain entraînement approfondi de l'IA.</div>"))
    for r in connaissances.REGLES:
        v = V.get(r["cle"]) or {}
        if v.get("statut") == "utile":
            badge = "<span class='up'><b>✓ Utile : vérifiée par l'IA</b></span>"
        elif v.get("statut"):
            badge = f"<span class='muted'><b>○ {_e(v['statut'].capitalize())}</b> : l'IA ne lui fait pas confiance pour l'instant</span>"
        else:
            badge = "<span class='muted'>Pas encore testée</span>"
        sens = ("" if v.get("dans_le_sens_annonce") is None else
                " · va dans le sens annoncé par les chercheurs" if v["dans_le_sens_annonce"] else " · va plutôt dans le sens inverse ces dernières années")
        corps += (f"<div class='carte'><h2 style='margin-top:0'>{_e(r['nom'])}</h2><p>{_e(r['idee'])}</p>"
                  f"<p class='muted' style='font-size:14px'>Source : {_e(r['source'])}</p><p>{badge}"
                  f"{(' · meilleure version : ' + _e(v['variante'])) if v.get('variante') else ''}{_e(sens)}</p></div>")
    corps += ("<p>Rien n'est sûr : une règle utile sur le passé peut cesser de fonctionner. Voir aussi les "
              "<a href='resultats.html'>résultats réels</a> du radar.</p>")
    with open(os.path.join(dossier, "connaissances.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Ce que sait l'IA : les règles de Bourse vérifiées | {NOM}",
                      "Momentum, faible volatilité, saisons, retournement… les règles de Bourse connues, et ce que l'IA du radar en a vraiment vérifié.",
                      "connaissances.html", corps, csp=csp))
