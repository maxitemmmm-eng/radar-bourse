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

CSS_PAGE = """:root{--bg:#eef1f5;--surface:#fff;--ink:#0f1b2d;--muted:#5a6a80;--line:#d9e0e8;--accent:#1d4fd8;--up:#07743f;--down:#b42a25;
--f:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--d:"Newsreader",Georgia,"Times New Roman",serif;--m:"IBM Plex Mono",ui-monospace,Consolas,monospace}
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
                 jsonld: dict | None = None, alternates: dict | None = None, langue: str = "fr") -> str:
    """Balises <head> communes : description, Open Graph, Twitter, canonique, icônes, manifeste."""
    url = (base + chemin) if base else ""
    img = (base + image) if base else image
    lignes = [
        f'<meta name="description" content="{_e(description)}">',
        f'<meta name="keywords" content="{_e(MOTS_CLES)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#0f1b2d">',
        f'<meta property="og:site_name" content="{NOM}">',
        f'<meta property="og:locale" content="{"en_US" if langue == "en" else "fr_FR"}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{_e(titre)}">',
        f'<meta property="og:description" content="{_e(description)}">',
        f'<meta property="og:image" content="{_e(img)}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_e(titre)}">',
        f'<meta name="twitter:description" content="{_e(description)}">',
        f'<meta name="twitter:image" content="{_e(img)}">',
        f'<link rel="manifest" href="{"../" * chemin.count("/")}manifest.webmanifest">',
        f'<link rel="apple-touch-icon" href="{"../" * chemin.count("/")}icone-192.png">',
    ]
    if url:
        lignes += [f'<link rel="canonical" href="{_e(url)}">', f'<meta property="og:url" content="{_e(url)}">']
    if base and alternates:   # versions dans d'autres langues (Google affiche la bonne selon le visiteur)
        for lg, c in alternates.items():
            lignes.append(f'<link rel="alternate" hreflang="{lg}" href="{_e(base + c)}">')
    verif = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    if verif and re.fullmatch(r"[A-Za-z0-9_\-]{10,100}", verif):
        lignes.append(f'<meta name="google-site-verification" content="{verif}">')
    if jsonld:
        data = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        lignes.append(f'<script type="application/ld+json">{data}</script>')
    return "\n".join(lignes)


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


def _page(base, titre, description, chemin, corps, jsonld=None, csp="", alternates=None):
    prefixe = "../" * chemin.count("/")
    csp = csp_avec_stats(csp)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{balises_tete(base, titre, description, chemin, jsonld=jsonld, alternates=alternates)}
<link rel="icon" href="{prefixe}icone-192.png">
{script_stats()}
<style>{CSS_PAGE}</style>
</head>
<body><div class="w">
<nav class="fil"><a href="{prefixe}index.html">{NOM}</a> · <a href="{prefixe}point.html">Le point du jour</a> · <a href="{prefixe}resultats.html">Résultats réels</a> · <a href="{prefixe}connaissances.html">Ce que sait l'IA</a> · <a href="{prefixe}apprendre.html">Apprendre</a> · <a href="{prefixe}titres.html">Tous les titres</a> · <a href="{prefixe}glossaire.html">Glossaire</a> · <a href="{prefixe}en/index.html" hreflang="en">English</a></nav>
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
    if p is not None and t.get("avis_net") is False:
        verdict = "sans avis net (les IA hésitent : dans ces cas-là, elles n'ont pas fait mieux que le hasard)"
    rq = t.get("risque_prevu") or {}
    agitation = (f"<p>Agitation prévue le mois prochain : en général, le prix bougera d'environ <b class='m'>±{round(rq['mouvement'] * 100)} %</b>"
                 + (", plus que d'habitude" if (rq.get("habitude") or 1) > 1.25 else ", moins que d'habitude" if (rq.get("habitude") or 1) < 0.8 else "")
                 + ", dans un sens ou dans l'autre.</p>") if rq.get("mouvement") else ""
    pourquoi = "".join(f"<li><b>{_e(r['famille'])}</b> : pousse vers la {'hausse' if r['effet'] > 0 else 'baisse'}"
                       + (f" ({_e(r['etat'])})" if r.get("etat") else "") + "</li>" for r in (t.get("raisons_ia") or []))
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
{"<b>Signal fort</b> : le modèle et la tendance technique vont dans le même sens." if t.get("signal_fort") else ""}
{f"Probabilité de faire mieux que {_e(t.get('indice_nom') or 'son marché')} sur la même période : <b>{round(t['proba_marche'] * 100)} %</b>." if t.get("proba_marche") is not None else ""}
{"Fourchette élargie par prudence : l'entreprise publie ses résultats avant l'échéance." if t.get("fourchette_elargie") else ""}</p>
{agitation}
{f"<h2>Pourquoi cet avis ?</h2><p class='muted'>Ce qui a le plus pesé dans le calcul des deux IA.</p><ul>{pourquoi}</ul>" if pourquoi else ""}
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
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp,
                         alternates={"fr": chemin, "en": f"en/stocks/{slug(tk)}.html", "x-default": chemin})


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


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]


def date_longue(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


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


def _page_point(base, r, csp, precedent, suivant):
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
    return chemin, _page(base, titre, desc, chemin, corps, jsonld, csp)


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
    groupes = {"fr": "Actions françaises", "eu": "Actions européennes", "us": "Actions américaines",
               "crypto": "Cryptomonnaies", "etf": "ETF et indices", "tendances": "En tendance"}
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
        chemin, page = _page_point(base, points[dte], csp, dates[i - 1] if i else None,
                                   dates[i + 1] if i + 1 < len(dates) else None)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily" if i == len(dates) - 1 else "yearly", "0.6"))
    corps = ("<h1>Le point du jour</h1><p class='muted'>Chaque soir, ce qu'il faut retenir des marchés, "
             "rédigé automatiquement par le radar.</p>"
             "<div class='carte'><b>À partager</b><p style='margin:6px 0 10px'>Une image du jour, prête pour Instagram, "
             "TikTok, X ou WhatsApp (format portrait).</p><a class='btn' href='image-du-jour.png' download>Télécharger l'image du jour</a></div>")
    corps += ("<ul>" + "".join(f"<li><a href='point/{dte}.html'>Bourse du {date_longue(dte)}</a></li>" for dte in reversed(dates)) + "</ul>"
              if dates else "<p>Le premier point du jour sera publié ce soir.</p>")
    with open(os.path.join(dossier, "point.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Le point du jour : la Bourse chaque soir | {NOM}",
                      "Résumé quotidien des marchés : indices, plus fortes hausses et baisses, signaux forts, actualités.",
                      "point.html", corps, csp=csp))
    urls.append(("point.html", "daily", "0.8"))

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
        if _image_du_jour(payload, os.path.join(dossier, "image-du-jour.png"), base):
            if dates:
                import shutil
                shutil.copyfile(os.path.join(dossier, "image-du-jour.png"), os.path.join(dossier, "point", f"{dates[-1]}.png"))
    except Exception as e:
        print(f"Image du jour non générée : {e}")
    try:
        from . import anglais
        urls += anglais.generer(payload, dossier, csp, base)
    except Exception as e:
        print(f"Version anglaise non générée : {e}")

    # IndexNow : fichier-clé qui autorise le site à signaler ses nouvelles pages à Bing et Yandex
    cle = cle_indexnow()
    if cle:
        with open(os.path.join(dossier, f"{cle}.txt"), "w", encoding="utf-8") as f:
            f.write(cle)

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


def cle_indexnow() -> str:
    import hashlib
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    return hashlib.sha256(f"radar-{depot}".encode()).hexdigest()[:32] if depot else ""


FAQ = [
    ("Radar Bourse est-il gratuit ?", "Oui, entièrement : pas d'inscription, pas d'abonnement, pas de publicité."),
    ("Les prévisions sont-elles fiables ?", "Ce sont des probabilités, pas des certitudes. La précision mesurée du modèle sur des périodes qu'il n'a jamais vues est affichée sur le site, ainsi que le suivi réel de chaque prévision publiée. Elle reste proche de ce que font les professionnels : bien au-dessous de 100 %."),
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
            f'· <a href="titres.html">tous les titres</a> · <a href="apprendre.html">apprendre la Bourse</a> · <a href="glossaire.html">glossaire</a></nav>')


def jsonld_accueil() -> dict:
    base = url_site()
    return {"@context": "https://schema.org", "@type": "WebSite", "name": NOM, "url": base or None,
            "description": DESCRIPTION, "inLanguage": "fr-FR"}


# ----------------------------------------------------------------------------
# Page « Résultats réels » : chaque prédiction publiée, vérifiée après coup
# ----------------------------------------------------------------------------
def _info_historique() -> tuple[int, str | None]:
    """Nombre de prédictions enregistrées et date de la première (pour annoncer les premiers résultats)."""
    try:
        import pandas as pd
        h = pd.read_csv(os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv"), usecols=["date"])
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
                      + "".join(f"<tr><td>{_e(_mois(m['nom']))}</td><td class='m'>{m['nb']}</td><td class='m'>{_taux(m['precision'])}</td></tr>" for m in D["par_mois"][-12:])
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
                      + "".join(f"<tr><td class='m'>{_e(r['date'])}</td><td><a href='titres/{slug(r['ticker'])}.html'>{_e(r['ticker'])}</a>"
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
