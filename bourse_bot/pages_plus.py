"""Version 53 : pages « Fonctionnalités », « Simulateur boursier », « À propos » et « Contact ».
Des pages claires que Google comprend facilement (une page = un sujet), avec leurs données structurées."""
from __future__ import annotations

import os

from . import config, seo

NOM = seo.NOM
_e = seo._e


def _vignette(src, alt, prefixe=""):
    return (f"<img src='{prefixe}{src}' alt='{_e(alt)}' width='1200' height='630' loading='lazy' decoding='async' "
            "style='width:100%;height:auto;border-radius:8px;display:block;margin-bottom:10px'>")


def _faq(faq):
    return "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq)


def _jl_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}


def fonctionnalites(payload):
    n = len(payload.get("titres", []))
    return [
        ("Prévisions à un mois pour plus de 200 titres", f"{n} actions, ETF et cryptos analysés chaque heure : de combien le prix peut bouger, "
         "le risque d'une forte chute, et les chances de faire mieux que son marché.", "index.html#previsions", "fonction:previsions"),
        ("Simulateur boursier et portefeuille virtuel", "10 000 € fictifs pour acheter et vendre sans risque, suivre tes gains et comparer avec l'IA.",
         "simulateur-boursier.html", "simulateur-boursier.html"),
        ("« À combien dans un mois ? »", "Pour chaque titre, une fourchette de prix probable dans un mois, avec la preuve de sa fiabilité passée.",
         "index.html#simulation", "fonction:fourchette"),
        ("L'Arène : joue contre l'IA", "Remonte le temps sur un vrai graphique et devine la suite : toi contre le radar.", "index.html#remonte", "fonction:arene"),
        ("Outils gratuits", "« Si j'avais investi… », convertisseur crypto, intérêts composés, plus-value et flat tax.", "outils.html", "outils.html"),
        ("Comparer deux titres", "Agitation, risque de chute, chances et performances côte à côte.", "comparer.html", "comparer.html"),
        ("Classements du jour", "Les titres les plus agités, les plus calmes, les plus à risque, par marché.", "classements.html", "classements.html"),
        ("Résultats réels publiés", "Chaque prévision est vérifiée après coup et publiée, ratés compris.", "resultats.html", "resultats.html"),
        ("Suivi du risque de chute", "Chaque mois, les titres jugés à risque : ont-ils vraiment chuté ?", "suivi-chute.html", "suivi-chute.html"),
        ("Guides et mini-cours", "Plus de 90 guides honnêtes et 8 mini-cours pour débuter en Bourse et en crypto.", "guides.html", "guides.html"),
        ("En 14 langues", "Les prévisions en anglais, espagnol, allemand, arabe, chinois, japonais…", "en/index.html", "fonction:langues"),
    ]


def _page_fonctionnalites(base, payload, csp):
    chemin = "fonctionnalites.html"
    F = fonctionnalites(payload)
    cartes = "".join(
        f"<a class='carte' style='text-decoration:none;color:inherit;margin:0' href='{lien}'>"
        + (_vignette(seo.IMAGES_PAGES[img], titre) if img in seo.IMAGES_PAGES else "")
        + f"<b style='font-size:18px'>{_e(titre)}</b><p class='muted' style='margin:6px 0 0'>{_e(desc)}</p></a>"
        for titre, desc, lien, img in F)
    corps = ("<h1>Toutes les fonctionnalités de Radar Bourse</h1>"
             "<p>Un site gratuit, sans compte et sans publicité, pour comprendre la Bourse et la crypto avec des chiffres vérifiés. "
             "Voici tout ce que tu peux y faire.</p>"
             f"<div class='grille' style='grid-template-columns:repeat(auto-fit,minmax(250px,1fr))'>{cartes}</div>"
             "<h2>Ce que l'IA prévoit bien, et ce qu'elle ne sait pas faire</h2>"
             "<p>L'IA est bonne pour prévoir <b>de combien un prix risque de bouger</b> et <b>quels titres risquent une forte chute</b>. "
             "Deviner si un prix va monter ou baisser reste très difficile : elle se trompe souvent, et le site le montre. "
             "Le détail est dans la <a href='fiche-technique-ia.html'>fiche technique de l'IA</a>.</p>"
             "<p><a class='btn' href='index.html'>Ouvrir l'appli</a></p>")
    jl = seo._jsonld_liste(base, "Les fonctionnalités de Radar Bourse", chemin, [(t, l) for t, _, l, _ in F])
    return chemin, seo._page(base, f"Fonctionnalités : prévisions IA, simulateur boursier, outils | {NOM}",
                             "Tout ce que fait Radar Bourse : prévisions IA pour 200+ actions et cryptos, simulateur boursier avec "
                             "portefeuille virtuel, outils gratuits, comparateur, guides. Gratuit et sans compte.", chemin, corps, jl, csp=csp)


def _page_simulateur(base, csp):
    chemin = "simulateur-boursier.html"
    faq = [("Le simulateur boursier est-il vraiment gratuit ?", "Oui : pas de compte, pas d'abonnement, pas de publicité. Ton portefeuille est enregistré dans ton navigateur."),
           ("Avec quel argent je joue ?", "Avec 10 000 € fictifs. Aucun argent réel n'est engagé, rien n'est acheté pour de vrai."),
           ("Les cours sont-ils réels ?", "Oui : actions françaises, européennes et américaines, ETF et cryptos, mis à jour plusieurs fois par jour (les cryptos en direct)."),
           ("Ça sert à quoi de s'entraîner ?", "À comprendre les frais, la volatilité et ses propres réflexes (vendre en panique, acheter trop haut) avant de risquer de l'argent réel."),
           ("Mes données sont-elles envoyées quelque part ?", "Non. Le portefeuille reste dans ton navigateur ; il n'y a ni compte ni cookie publicitaire.")]
    etapes = [("Ouvre l'appli et va dans « Mon portefeuille virtuel ».", "index.html#portefeuille"),
              ("Cherche une action ou une crypto (Apple, LVMH, Bitcoin…) et ouvre sa fiche.", "index.html"),
              ("Clique sur « Investir (virtuel) » et choisis un montant.", None),
              ("Suis tes gains et tes pertes, et compare avec les prévisions de l'IA.", None)]
    img = seo.IMAGES_PAGES.get(chemin)
    corps = ("<h1>Simulateur boursier gratuit : 10 000 € virtuels pour t'entraîner</h1>"
             + (_vignette(img, "Simulateur boursier gratuit de Radar Bourse") if img else "")
             + "<p>Achète et vends des actions, des ETF et des cryptos avec de l'argent <b>fictif</b>, sur les <b>vrais cours</b>. "
             "Sans compte, sans risque, directement dans ton navigateur.</p>"
             "<p><a class='btn' href='index.html#portefeuille'>Commencer avec 10 000 € virtuels</a></p>"
             "<h2>Comment ça marche</h2><ol>" + "".join(f"<li>{f'<a href={chr(39)}{l}{chr(39)}>{_e(t)}</a>' if l else _e(t)}</li>" for t, l in etapes) + "</ol>"
             "<h2>Deux façons de jouer en plus</h2><div class='grille'>"
             "<a class='carte' style='text-decoration:none;color:inherit;margin:0' href='index.html#remonte'><b>L'Arène : remonte le temps</b>"
             "<p class='muted' style='margin:6px 0 0'>Un vrai graphique s'arrête : devine la suite, contre le radar.</p></a>"
             "<a class='carte' style='text-decoration:none;color:inherit;margin:0' href='outils/si-javais-investi.html'><b>Si j'avais investi…</b>"
             "<p class='muted' style='margin:6px 0 0'>Combien vaudraient aujourd'hui 100 € placés il y a un an ?</p></a></div>"
             "<h2>Ce que le simulateur ne fait pas</h2><p>Il ne tient pas compte des frais réels de ton courtier ni des impôts, et un gain virtuel "
             "ne garantit aucun gain réel. C'est un outil pour apprendre, pas un conseil d'investissement.</p>" + _faq(faq))
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "Simulateur boursier Radar Bourse", "url": url, "applicationCategory": "FinanceApplication",
         "operatingSystem": "Tous (navigateur web)", "inLanguage": "fr", "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
         "description": "Simulateur boursier gratuit avec 10 000 € virtuels sur les vrais cours des actions, ETF et cryptos."},
        _jl_faq(faq), seo._jsonld_fil(base, [(NOM, ""), ("Simulateur boursier", chemin)])]}
    return chemin, seo._page(base, f"Simulateur boursier gratuit : portefeuille virtuel de 10 000 € | {NOM}",
                             "Simulateur boursier gratuit et sans compte : 10 000 € virtuels pour acheter actions, ETF et cryptos sur les vrais cours, "
                             "et t'entraîner sans risque.", chemin, corps, jl, csp=csp)


def _page_a_propos(base, payload, csp):
    chemin = "a-propos.html"
    n = len(payload.get("titres", []))
    corps = ("<h1>À propos de Radar Bourse</h1>"
             f"<p><b>Radar Bourse</b> est un projet personnel, <b>éducatif et gratuit</b>, créé par un particulier passionné de finance et de programmation. "
             f"Il analyse chaque heure {n} actions, ETF et cryptos, et publie des prévisions à un mois expliquées simplement.</p>"
             "<h2>Pourquoi ce site</h2><p>Beaucoup de sites promettent de « prédire la Bourse ». Radar Bourse fait l'inverse : il montre ce que "
             "l'IA prévoit vraiment bien (l'agitation des prix, le risque de forte chute), ce qu'elle prévoit mal (le sens du prix à un mois), "
             "et il <b>publie tous ses résultats, ratés compris</b>.</p>"
             "<h2>Comment ça marche</h2><ul>"
             "<li><b>Les données</b> : cours publics (Yahoo Finance, Binance, CryptoCompare), vérifiés automatiquement.</li>"
             "<li><b>L'IA</b> : des modèles d'apprentissage automatique (arbres de décision) entraînés sur plus de 10 ans d'historique.</li>"
             "<li><b>Les tests</b> : chaque méthode est jugée sur des années que l'IA n'avait jamais vues, comme dans la réalité.</li>"
             "<li><b>Le suivi</b> : chaque prévision publiée est vérifiée un mois plus tard, en public.</li></ul>"
             "<h2>Nos principes</h2><ul><li>Gratuit, sans compte, sans publicité, sans cookie publicitaire.</li>"
             "<li>Aucun conseil en investissement : le site explique et mesure, il ne dit pas quoi acheter.</li>"
             "<li>Honnêteté sur les chiffres : jamais de résultat embelli.</li></ul>"
             "<h2>En savoir plus</h2><ul><li><a href='fonctionnalites.html'>Toutes les fonctionnalités</a></li>"
             "<li><a href='fiche-technique-ia.html'>La fiche technique de l'IA</a></li><li><a href='resultats.html'>Les résultats réels</a></li>"
             "<li><a href='contact.html'>Nous contacter</a></li><li><a href='index.html#conditions'>Conditions d'utilisation et mentions légales</a></li></ul>")
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "AboutPage", "name": "À propos de Radar Bourse", "url": url, "inLanguage": "fr",
         "about": {"@type": "Organization", "name": NOM, "url": base or None}},
        seo._jsonld_fil(base, [(NOM, ""), ("À propos", chemin)])]}
    return chemin, seo._page(base, f"À propos de Radar Bourse : un projet éducatif et transparent | {NOM}",
                             "Qui est derrière Radar Bourse, comment fonctionnent ses prévisions IA, d'où viennent les données et pourquoi tous les résultats "
                             "sont publiés, ratés compris.", chemin, corps, jl, csp=csp)


def _page_contact(base, csp):
    chemin = "contact.html"
    lien = config.CONTACT
    corps = ("<h1>Contacter Radar Bourse</h1><p>Un bug, une erreur dans un chiffre, une idée de fonctionnalité ? "
             "Écris-nous : chaque message est lu.</p>"
             f"<div class='carte'><p><b>Le plus simple :</b> ouvre un message (« issue ») sur la page du projet.</p>"
             f"<p><a class='btn' href='{_e(lien)}' target='_blank' rel='noopener'>Écrire un message</a></p>"
             "<p class='muted' style='margin:0'>Il faut un compte GitHub gratuit. Ton message sera public : n'y mets aucune information personnelle.</p></div>"
             "<h2>Pour un bug, indique</h2><ul><li>la page concernée (copie son adresse) ;</li><li>ce que tu as fait, ce que tu attendais, ce qui s'est passé ;</li>"
             "<li>ton appareil (téléphone ou ordinateur) et ton navigateur.</li></ul>"
             "<h2>Ce que nous ne faisons pas</h2><p>Nous ne répondons pas aux demandes de conseil personnel (« dois-je acheter… ? ») : "
             "Radar Bourse n'est pas un conseiller en investissement. Aucune demande de paiement, d'identifiant ou de mot de passe "
             "ne viendra jamais de nous.</p><p>Voir aussi : <a href='a-propos.html'>à propos</a> · <a href='index.html#h-faq'>questions fréquentes</a></p>")
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "ContactPage", "name": "Contacter Radar Bourse", "url": url, "inLanguage": "fr"},
        seo._jsonld_fil(base, [(NOM, ""), ("Contact", chemin)])]}
    return chemin, seo._page(base, f"Contact : signaler un bug ou proposer une idée | {NOM}",
                             "Comment contacter Radar Bourse pour signaler un bug, une erreur ou proposer une idée.", chemin, corps, jl, csp=csp)


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    urls = []
    for chemin, page in (_page_fonctionnalites(base, payload, csp), _page_simulateur(base, csp),
                         _page_a_propos(base, payload, csp), _page_contact(base, csp)):
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "weekly", "0.9" if chemin in ("simulateur-boursier.html", "fonctionnalites.html") else "0.5"))
    return urls
