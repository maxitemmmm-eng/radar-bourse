"""Référencement : tout ce qui aide Google et les réseaux sociaux à trouver et présenter le site.

- une page HTML statique par titre (lisible par Google sans JavaScript) ;
- un glossaire des indicateurs (pages très recherchées) ;
- sitemap.xml, robots.txt, image de partage, icônes et manifeste (installation sur téléphone) ;
- balises <meta> : description, Open Graph, Twitter, adresse canonique, données structurées.
"""
from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime

from . import config

NOM = "Radar Bourse"
SLOGAN = "Analyse et prévisions boursières à un mois, expliquées simplement"
DESCRIPTION = ("Radar Bourse analyse chaque jour les actions françaises, américaines et les cryptos : "
               "prévision à un mois, signaux forts mesurés, graphiques expliqués, simulateur et actualités. "
               "Gratuit, sans inscription, projet éducatif.")
MOTS_CLES = ("prévision bourse, analyse technique, prévision action, prévision crypto, CAC 40, S&P 500, "
             "Bitcoin, RSI, MACD, moyenne mobile, simulateur bourse, signaux bourse, apprendre la bourse")
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

CSS_PAGE = """:root{--bg:#eef1f5;--surface:#fff;--ink:#0f1b2d;--muted:#5a6a80;--line:#d9e0e8;--accent:#1d4fd8;--up:#0b8a4f;--down:#c9352f;
--f:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--d:"Schibsted Grotesk","Helvetica Neue",Arial,sans-serif;--m:"IBM Plex Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#0a111d;--surface:#111a29;--ink:#e4ebf5;--muted:#8c9bb0;--line:#22314a;--accent:#7398ff;--up:#35c27d;--down:#ff6b62;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--f)}
.w{max-width:860px;margin:0 auto;padding-block:28px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
a{color:var(--accent)}h1,h2{font-family:var(--d);line-height:1.15;text-wrap:balance}h1{font-size:clamp(28px,5vw,40px);margin:8px 0}
h2{font-size:21px;margin:28px 0 8px}.m{font-family:var(--m);font-variant-numeric:tabular-nums}.muted{color:var(--muted)}
.carte{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px;margin:14px 0}
.grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.k b{display:block;font-family:var(--m);font-size:20px;font-weight:500}.k>span{font-size:13px;color:var(--muted)}
.up{color:var(--up)}.down{color:var(--down)}.btn{display:inline-block;background:var(--ink);color:var(--surface);padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600}
table{width:100%;border-collapse:collapse}td{padding:8px 6px;border-bottom:1px solid var(--line)}td:last-child{text-align:right}
.liste{columns:3 220px;padding-left:18px}.avert{font-size:13.5px;color:var(--muted);border-top:1px solid var(--line);margin-top:36px;padding-top:14px}
dt{font-weight:700;margin-top:16px}dd{margin:4px 0 0}nav.fil{font-size:14px}"""


def url_site() -> str:
    """Adresse publique du site : déduite du dépôt GitHub, ou définie dans RADAR_URL."""
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


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _px(v, dev):
    if v is None:
        return "–"
    txt = f"{v:,.2f}" if abs(v) >= 1 else f"{v:.4g}"
    return txt.replace(",", "\u202f").replace(".", ",") + f" {dev}"


def _pct(v, d=1):
    if v is None:
        return "–"
    cls = "up" if v > 0 else "down" if v < 0 else ""
    return f'<span class="m {cls}">{"+" if v > 0 else ""}{v*100:.{d}f} %</span>'.replace(".", ",", 1)


def balises_tete(base: str, titre: str, description: str, chemin: str = "", image: str = "partage.png",
                 jsonld: dict | None = None) -> str:
    """Balises <head> communes : description, Open Graph, Twitter, canonique, icônes, manifeste."""
    url = (base + chemin) if base else ""
    img = (base + image) if base else image
    lignes = [
        f'<meta name="description" content="{_e(description)}">',
        f'<meta name="keywords" content="{_e(MOTS_CLES)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#0f1b2d">',
        f'<meta property="og:site_name" content="{NOM}">',
        '<meta property="og:locale" content="fr_FR">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{_e(titre)}">',
        f'<meta property="og:description" content="{_e(description)}">',
        f'<meta property="og:image" content="{_e(img)}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_e(titre)}">',
        f'<meta name="twitter:description" content="{_e(description)}">',
        f'<meta name="twitter:image" content="{_e(img)}">',
        f'<link rel="manifest" href="{"../" if chemin.count("/") else ""}manifest.webmanifest">',
        f'<link rel="apple-touch-icon" href="{"../" if chemin.count("/") else ""}icone-192.png">',
    ]
    if url:
        lignes += [f'<link rel="canonical" href="{_e(url)}">', f'<meta property="og:url" content="{_e(url)}">']
    verif = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    if verif and re.fullmatch(r"[A-Za-z0-9_\-]{10,100}", verif):
        lignes.append(f'<meta name="google-site-verification" content="{verif}">')
    if jsonld:
        data = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        lignes.append(f'<script type="application/ld+json">{data}</script>')
    return "\n".join(lignes)


def _page(base, titre, description, chemin, corps, jsonld=None, csp=""):
    prefixe = "../" if "/" in chemin else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{balises_tete(base, titre, description, chemin, jsonld=jsonld)}
<link rel="icon" href="{prefixe}icone-192.png">
<style>{CSS_PAGE}</style>
</head>
<body><div class="w">
<nav class="fil"><a href="{prefixe}index.html">{NOM}</a> · <a href="{prefixe}apprendre.html">Apprendre</a> · <a href="{prefixe}titres.html">Tous les titres</a> · <a href="{prefixe}glossaire.html">Glossaire</a></nav>
{corps}
<p class="avert"><b>Rien n'est sûr en Bourse.</b> {NOM} est un projet éducatif : ces informations sont générées automatiquement,
peuvent contenir des erreurs et ne constituent pas un conseil en investissement. Tu peux perdre tout l'argent investi.
Conditions d'utilisation, méthodologie et aide : voir la <a href="{prefixe}index.html#conditions">page d'accueil</a>.</p>
</div></body></html>
"""


def _page_titre(base, t, horizon, date, csp, modele):
    dev, prix, p = t["devise"], t["prix"], t.get("proba_hausse")
    cone, f = t.get("cone"), t.get("fourchette") or []
    med = cone["mediane"][-1] if cone else None
    sur10 = round(p * 10) if p is not None else None
    verdict = ("plutôt à la hausse" if p >= .58 else "légèrement à la hausse" if p >= .52 else
               "sans direction claire" if p > .48 else "légèrement à la baisse" if p > .42 else
               "plutôt à la baisse") if p is not None else "non disponible"
    nom, tk = t["nom"], t["ticker"]
    titre = f"{nom} ({tk}) : analyse et prévision à un mois | {NOM}"
    desc = (f"{nom} ({tk}) au {date} : tendance {LIB_SIGNAL.get(t['signal'], 'neutre')}, "
            + (f"{sur10} chances sur 10 d'être plus haut dans un mois selon le modèle, " if sur10 is not None else "")
            + (f"scénario central {_px(med, dev)}. " if med else "")
            + "Graphique, niveaux clés et actualités. Projet éducatif, pas un conseil.")
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
    corps = f"""
<h1>{_e(nom)} ({_e(tk)}) : analyse et prévision</h1>
<p class="muted">Mise à jour automatique · cours au {_e(date)}</p>
<div class="carte grille">
  <div class="k"><b>{_px(prix, dev)}</b><span>dernier cours</span></div>
  <div class="k"><b>{_pct(perf.get('1 mois'))}</b><span>sur 1 mois</span></div>
  <div class="k"><b>{round(t['score'])} / 100</b><span>score technique ({LIB_SIGNAL.get(t['signal'], '')})</span></div>
  <div class="k"><b>{f'{sur10} sur 10' if sur10 is not None else '–'}</b><span>chances d'être plus haut dans {horizon} séances</span></div>
</div>
<h2>En résumé</h2>
<p>Pour le mois qui vient, le radar voit {_e(nom)} <b>{verdict}</b>.
{f"Scénario central : environ <b class='m'>{_px(med, dev)}</b>. " if med else ""}
{f"Dans 8 cas sur 10, le cours devrait rester entre <b class='m'>{_px(f[0], dev)}</b> et <b class='m'>{_px(f[1], dev)}</b>." if len(f) == 2 else ""}
{"<b>Signal fort</b> : le modèle et la tendance technique vont dans le même sens." if t.get("signal_fort") else ""}</p>
<p><a class="btn" href="{lien_app}">Voir le graphique interactif et le simulateur</a></p>
{f"<h2>Ce que montrent les indicateurs</h2><ul>{raisons}</ul>" if raisons else ""}
{f"<h2>Niveaux à surveiller</h2><div class='carte'><table>{niveaux}</table></div>" if niveaux else ""}
{f"<h2>Dernières actualités</h2><ul>{actus}</ul>" if actus else ""}
<h2>Fiabilité</h2>{fiab or "<p>Prévision statistique : elle se trompe souvent.</p>"}
"""
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "name": titre, "description": desc,
              "inLanguage": "fr-FR", "dateModified": datetime.now().isoformat(timespec="seconds"),
              "isPartOf": {"@type": "WebSite", "name": NOM, "url": base or None},
              "about": {"@type": "Thing", "name": f"{nom} ({tk})"}}
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp)


def _image_partage(payload: dict, chemin: str) -> None:
    """Image 1200×630 affichée quand le lien est partagé (WhatsApp, Discord, X…)."""
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


def _icones(dossier: str) -> None:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return
    for taille in (192, 512):
        img = Image.new("RGB", (taille, taille), "#0f1b2d")
        dr = ImageDraw.Draw(img)
        c, r = taille / 2, taille * 0.32
        dr.ellipse((c - r, c - r, c + r, c + r), outline="#7398ff", width=max(3, taille // 40))
        dr.line((c, c, c + r * 0.95, c - r * 0.6), fill="#35c27d", width=max(5, taille // 22))
        dr.ellipse((c - taille * .05, c - taille * .05, c + taille * .05, c + taille * .05), fill="#35c27d")
        img.save(os.path.join(dossier, f"icone-{taille}.png"), optimize=True)


def generer(payload: dict, dossier: str, csp: str) -> None:
    """Écrit toutes les pages et fichiers de référencement dans le dossier du site."""
    base = url_site()
    date = payload.get("date_donnees", "")
    try:
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        pass
    horizon = payload.get("horizon", 20)
    os.makedirs(os.path.join(dossier, "titres"), exist_ok=True)
    urls = [("", "hourly", "1.0"), ("titres.html", "daily", "0.8"), ("glossaire.html", "monthly", "0.6")]

    # Une page par titre
    liens = []
    for t in payload.get("titres", []):
        chemin, page = _page_titre(base, t, horizon, date, csp, payload.get("modele"))
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "hourly", "0.7"))
        liens.append((t["nom"], t["ticker"], chemin, t.get("marche", "")))

    # Index des titres
    groupes = {"fr": "Actions françaises", "us": "Actions américaines", "crypto": "Cryptomonnaies",
               "etf": "ETF et indices", "tendances": "En tendance"}
    corps = "<h1>Tous les titres analysés</h1><p class='muted'>Analyse et prévision à un mois, mises à jour automatiquement.</p>"
    for cle, lib in groupes.items():
        items = [l for l in liens if l[3] == cle]
        if items:
            corps += f"<h2>{lib}</h2><ul class='liste'>" + "".join(
                f"<li><a href='{_e(c)}'>{_e(n)}</a> <span class='muted'>({_e(tk)})</span></li>" for n, tk, c, _ in items) + "</ul>"
    with open(os.path.join(dossier, "titres.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Tous les titres : actions, ETF et cryptos | {NOM}",
                      "Liste des actions françaises et américaines, ETF et cryptomonnaies analysés chaque jour par Radar Bourse.",
                      "titres.html", corps, csp=csp))

    # Glossaire
    corps = ("<h1>Glossaire de la Bourse et de l'analyse technique</h1>"
             "<p class='muted'>Les mots utilisés sur Radar Bourse, expliqués simplement.</p><dl>"
             + "".join(f"<dt id='{slug(m)}'>{_e(m)}</dt><dd>{_e(d)}</dd>" for m, d in GLOSSAIRE) + "</dl>")
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

    # sitemap.xml et robots.txt (adresse absolue requise : uniquement si l'adresse du site est connue)
    maintenant = datetime.now().strftime("%Y-%m-%d")
    if base:
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        xml += [f"<url><loc>{html.escape(base + c)}</loc><lastmod>{maintenant}</lastmod><changefreq>{fq}</changefreq><priority>{pr}</priority></url>"
                for c, fq, pr in urls]
        xml.append("</urlset>")
        with open(os.path.join(dossier, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write("\n".join(xml))
    with open(os.path.join(dossier, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n" + (f"Sitemap: {base}sitemap.xml\n" if base else ""))

    # Manifeste (« Ajouter à l'écran d'accueil »), icônes, image de partage
    manifeste = {"name": NOM, "short_name": NOM, "description": SLOGAN, "lang": "fr", "start_url": "./",
                 "display": "standalone", "background_color": "#0f1b2d", "theme_color": "#0f1b2d",
                 "icons": [{"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
                           {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"}]}
    with open(os.path.join(dossier, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifeste, f, ensure_ascii=False)
    _icones(dossier)
    _image_partage(payload, os.path.join(dossier, "partage.png"))


def liens_accueil(payload: dict) -> str:
    """Liens texte vers chaque page de titre, ajoutés en bas de l'accueil (Google suit les liens)."""
    items = "".join(f'<a href="titres/{slug(t["ticker"])}.html">{_e(t["nom"])}</a>' for t in payload.get("titres", []))
    return (f'<nav class="seo-liens" aria-label="Pages des titres"><b>Analyses détaillées :</b> {items} '
            f'· <a href="titres.html">tous les titres</a> · <a href="apprendre.html">apprendre la Bourse</a> · <a href="glossaire.html">glossaire</a></nav>')


def jsonld_accueil() -> dict:
    base = url_site()
    return {"@context": "https://schema.org", "@type": "WebSite", "name": NOM, "url": base or None,
            "description": DESCRIPTION, "inLanguage": "fr-FR"}
