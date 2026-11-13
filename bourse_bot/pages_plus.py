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
    try:   # version 77 : plus aucun nombre écrit en dur (ils finissaient par se contredire d'une page à l'autre)
        from .langues import NOMS_LANGUES
        n_langues = len(NOMS_LANGUES)
    except Exception:
        n_langues = 28
    try:
        from .formation import CHAPITRES
        from .formation_plus import LABOS
        n_chap, n_labos = sum(1 for c in CHAPITRES if not c.get("cas")), sum(len(v) for v in LABOS.values())
    except Exception:
        n_chap, n_labos = 40, 13
    return [
        (f"Prévisions à un mois pour {n} titres", f"{n} actions, ETF et cryptos analysés chaque heure : de combien le prix peut bouger, "
         "le risque d'une forte chute, et les chances de faire mieux que son marché.", "index.html#previsions", "fonction:previsions"),
        ("Simulateur boursier et portefeuille virtuel", "10 000 € fictifs pour acheter et vendre sans risque, suivre tes gains et comparer avec l'IA.",
         "simulateur-boursier.html", "simulateur-boursier.html"),
        ("« À combien dans un mois ? »", "Pour chaque titre, une fourchette de prix probable dans un mois, avec la preuve de sa fiabilité passée.",
         "index.html#simulation", "fonction:fourchette"),
        ("Ton pronostic du jour", "Trois marchés, plus haut ou plus bas demain ? Reviens le lendemain voir ton résultat, et garde ta série de jours.",
         "index.html#prono", "fonction:prono"),
        ("L'Arène : joue contre l'IA", "Remonte le temps sur un vrai graphique et devine la suite : toi contre le radar.", "index.html#remonte", "fonction:arene"),
        ("Une IA qui s'améliore chaque nuit", "Chaque nuit, elle essaie de nouveaux réglages et n'adopte que ceux qui font mieux de façon prouvée. "
         "Tout est noté dans son journal.", "journal-ia.html", "journal-ia.html"),
        ("Outils gratuits", "« Si j'avais investi… », convertisseur crypto, intérêts composés, plus-value et flat tax.", "outils.html", "outils.html"),
        ("Comparer deux titres", "Agitation, risque de chute, chances et performances côte à côte.", "comparer.html", "comparer.html"),
        ("Classements du jour", "Les titres les plus agités, les plus calmes, les plus à risque, par marché.", "classements.html", "classements.html"),
        ("Résultats réels publiés", "Chaque prévision est vérifiée après coup et publiée, ratés compris.", "resultats.html", "resultats.html"),
        ("Suivi du risque de chute", "Chaque mois, les titres jugés à risque : ont-ils vraiment chuté ?", "suivi-chute.html", "suivi-chute.html"),
        ("L'Académie : apprendre de zéro", f"{n_chap} chapitres courts avec exercices corrigés, {n_labos} simulateurs à manipuler, "
         "un entraînement de 3 minutes par jour, des fiches de révision et un examen final avec certificat.", "formation.html", "formation.html"),
        ("Guides et mini-cours", "Plus de 90 guides honnêtes et 8 mini-cours pour débuter en Bourse et en crypto.", "guides.html", "guides.html"),
        (f"En {n_langues} langues", "Les prévisions en anglais, espagnol, allemand, arabe, chinois, japonais…", "en/index.html", "fonction:langues"),
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
                             f"Tout ce que fait Radar Bourse : prévisions IA pour {len(payload.get('titres', []))} actions et cryptos, Académie gratuite, simulateur boursier avec "
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
    ne = payload.get("nb_etendu") or 0
    total = f"{n + ne:,}".replace(",", "\u202f") if ne else str(n)
    # version 70 : page réécrite, plus humaine — qui, pourquoi, comment, et ce qu'on ne fera jamais
    corps = ("<h1>À propos de Radar Bourse</h1>"
             "<p class='muted'>Un projet indépendant, gratuit et sans publicité, mené sous le pseudonyme <b>maxitemmmm</b>.</p>"
             "<h2>Comment tout a commencé</h2>"
             "<p>Radar Bourse est né d'une question toute simple : <i>est-ce qu'une IA peut vraiment prévoir la Bourse ?</i> "
             "En cherchant la réponse, on tombe surtout sur des sites qui promettent des gains, vendent des « signaux » et ne montrent jamais leurs erreurs. "
             "Alors plutôt que de croire sur parole, j'ai construit l'outil moi-même, en solo, sur mon temps libre, et décidé de tout publier : "
             "les avis de l'IA, la méthode, et surtout les résultats, ratés compris.</p>"
             "<p>La réponse, aujourd'hui, est nuancée. Deviner si un prix va monter le mois prochain reste très difficile (l'IA fait un peu mieux que le hasard, pas beaucoup plus). "
             "En revanche, prévoir de combien un prix va bouger, ou le risque d'une forte chute, ça marche nettement mieux. Le site est construit autour de cette honnêteté.</p>"
             "<h2>Ce que tu trouves ici</h2><ul>"
             f"<li><b>Le Radar</b> : l'avis de l'IA sur {total} actions, ETF et cryptos, mis à jour chaque heure, toujours avec son niveau de confiance.</li>"
             "<li><b>L'Académie</b> : un parcours gratuit pour apprendre la Bourse de zéro, avec quiz, exercices et certificat. <a href='formation.html'>Commencer</a>.</li>"
             "<li><b>Les preuves</b> : chaque avis important est contrôlé un mois plus tard, en public. <a href='avis-surs-verifies.html'>Voir les avis vérifiés</a>.</li></ul>"
             "<h2>Comment ça marche, concrètement</h2><ul>"
             "<li><b>Les données</b> : cours publics (Yahoo Finance, Binance, CryptoCompare, Stooq) et indicateurs économiques (FRED), contrôlés automatiquement avant chaque publication. "
             "Une prévision incohérente est retirée plutôt que publiée.</li>"
             "<li><b>L'IA</b> : des modèles d'apprentissage automatique (forêts d'arbres de décision et boosting) entraînés sur plus de dix ans de cours.</li>"
             "<li><b>Les tests</b> : chaque idée est jugée sur des années que l'IA n'avait jamais vues, comme dans la vraie vie. Si elle ne fait pas mieux, elle n'est pas gardée, "
             "et c'est écrit sur la page des <a href='fiche-technique-ia.html'>idées testées</a>.</li>"
             "<li><b>Le suivi</b> : les avis sont archivés le jour même et vérifiés vingt séances plus tard. Rien n'est effacé.</li></ul>"
             "<h2>Ce que Radar Bourse ne fera jamais</h2><ul>"
             "<li>Te dire quoi acheter ou te promettre un gain.</li><li>Cacher une erreur ou embellir un résultat.</li>"
             "<li>Vendre tes données, te pister avec des cookies publicitaires ou t'obliger à créer un compte.</li>"
             "<li>Te faire payer quoi que ce soit, ou t'envoyer vers une plateforme en échange d'une commission.</li></ul>"
             "<h2>Une question, une erreur repérée ?</h2><p>Les remarques sont les bienvenues, surtout les critiques sur la méthode : "
             "<a href='contact.html'>contact</a>. Chaque remarque est lue, et les erreurs sont corrigées dès la mise à jour suivante.</p>"
             "<h2>En savoir plus</h2><ul><li><a href='fonctionnalites.html'>Toutes les fonctionnalités</a></li>"
             "<li><a href='fiche-technique-ia.html'>La fiche technique de l'IA</a></li><li><a href='resultats.html'>Les résultats réels</a></li>"
             "<li><a href='credits.html'>Sources des données et crédits</a></li><li><a href='index.html#conditions'>Conditions d'utilisation et mentions légales</a></li></ul>")
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


IDEES_TESTEES = [   # (version, idée, verdict, détail) — tout est testé sur des années que l'IA n'avait jamais vues
    ("85", "Effet calendrier : quand l'IA hésite, suivre la tendance habituelle du mois de l'année (certains mois montent plus souvent que d'autres)", False,
     "Testé de 2018 à 2026 avec les seules années passées : −0,4 point en moyenne, recul 5 années sur 9 (jusqu'à −3,4 points en 2025). Les « bons mois » du passé ne se répètent pas. Non adopté"),
    ("84", "Mettre en avant seulement les 10 % d'avis les plus tranchés (« avis très net »)", False,
     "Testé de 2018 à 2026, seuil fixé avec les seules années passées : 60,4 % de bons sens en moyenne contre 54,3 % pour tous les avis, et mieux 8 années sur 9. "
     "Mais en 2021 ces avis tranchés ont fait moins bien que les autres (54,6 % contre 55,7 %) : pas de badge qui promettrait plus que la réalité. Non adopté"),
    ("84", "Une IA spécialisée par marché (un modèle pour les actions américaines, un pour l'Europe, un pour les cryptos…)", False,
     "Moins d'exemples par modèle : −1,7 point en moyenne, recul 6 années sur 9 (jusqu'à −5,2 points). Non adopté"),
    ("84", "Donner à l'IA la santé du marché entier (part des titres au-dessus de leur moyenne 200 jours, hausse moyenne, dispersion)", False,
     "−1,5 point en moyenne, recul 6 années sur 9 (jusqu'à −8,4 points) : ces informations font surtout apprendre le passé par cœur. Non adopté"),
    ("84", "Recalibrer les pourcentages pour que « 60 % » arrive vraiment 60 fois sur 100 (régression isotonique)", False,
     "Le score de Brier (précision des pourcentages) se dégrade 7 années sur 9 : les pourcentages actuels sont déjà mieux réglés. Non adopté"),
    ("83", "Nouveau test de l'idée « rebond quand la peur est forte » : avis de hausse quand l'indice de la peur (VIX) dépasse un seuil, seuil choisi chaque année avec les seules années précédentes", False,
     "Testé de 2016 à 2026 : +0,49 point en moyenne, gain net en 2020 (+4,8 points), mais 2022 recule encore légèrement (−0,06 point). Avec un seuil fixé après coup (35), aucune année ne recule, "
     "mais ce serait choisir le réglage en connaissant les résultats : ce n'est pas un test honnête. Non adopté, à retester quand de nouvelles périodes de forte peur auront été vécues"),
    ("82", "Déplacer le seuil hausse/baisse (au lieu de 50 sur 100) : par marché selon la part de hausses passée, un seuil unique, ou le seuil qui marchait le mieux sur chaque marché", False,
     "Testé année par année (2018 à 2026) en n'apprenant que sur les années précédentes : seuil par marché −1,6 point en moyenne (jusqu'à −5,9), seuil unique −1,0 point, "
     "meilleur seuil passé +0,1 point en moyenne mais −1,6 point en 2022 et 5 années sur 9 en recul. Non adopté : le seuil de 50 reste le plus fiable"),
    ("81", "Un « correcteur » appris par-dessus l'IA : un second modèle (régression logistique, puis arbres) qui corrige l'avis selon la peur du marché, la tendance, l'agitation et le type de titre", False,
     "Testé année par année en n'apprenant que sur les années précédentes (2018 à 2026) : la version logistique gagne 0,5 point en moyenne mais perd jusqu'à 2,5 points en 2022 "
     "et recule 5 années sur 9 ; la version à arbres perd 1 point en moyenne. Non adopté"),
    ("81", "Quand l'IA hésite (chances entre 48 et 52 sur 100), suivre la tendance : celle du titre sur 1 ou 6 mois, celle du marché ou la moyenne 200 jours", False,
     "228 443 avis jugés de 2016 à 2026 : au mieux +0,1 point au total (tendance d'un mois), mais 4 années sur 11 reculent. Non adopté"),
    ("76", "Quand la peur est très forte sur les marchés (indice VIX au-dessus de 30), donner un avis de rebond (hausse)", False,
     "228 443 avis jugés de 2016 à 2026 : 56,36 % de bonnes réponses au lieu de 55,78 % au total, mais une année recule légèrement (−0,06 point), "
     "et l'idée repose sur peu d'épisodes (5,7 % des avis, surtout 2020 et 2022). Règle du site : jamais moins bien sur aucune année. Non adopté, à retester avec plus de recul"),
    ("75", "Juger chaque titre par rapport aux autres du même marché le même jour (la moitié la mieux classée en hausse, l'autre en baisse)", False,
     "228 443 avis jugés de 2016 à 2026 : 51,8 % de bonnes réponses au lieu de 55,78 %, jusqu'à 12 points de moins certaines années (quand presque tout monte ou tout baisse ensemble). "
     "Non adopté"),
    ("74", "Inverser l'avis de l'IA sur les titres où elle s'est souvent trompée récemment (moins de 40 % de réussite sur ses 20 ou 40 derniers avis connus)", False,
     "228 443 avis jugés de 2016 à 2026 : 53,0 % à 54,0 % de bonnes réponses au lieu de 55,78 %, et jusqu'à 7,8 points de moins certaines années. "
     "Une série d'erreurs sur un titre ne dit rien des suivantes. Non adopté"),
    ("73", "Quand l'IA hésite (chances entre 47 et 53 sur 100), garder plutôt son avis de la veille", False,
     "228 443 avis jugés de 2016 à 2026 : 55,73 % à 55,77 % de bonnes réponses contre 55,78 % sans ce changement, et 5 ou 6 années sur 11 reculent. "
     "Non adopté : l'IA ferait moins bien"),
    ("72", "Mélanger à nouveau l'avis de la première IA avec l'avis final, pour corriger les hésitations", False,
     "228 443 avis jugés de 2016 à 2026 : exactement le même nombre de bonnes réponses (55,78 %) avec 25 % ou 50 % de mélange, sur chacune des 11 années. "
     "L'avis final contient déjà tout ce que sait la première IA. Non adopté : aucun gain"),
    ("71", "Lisser l'avis de l'IA : faire la moyenne de ses chances des derniers jours, titre par titre, pour un avis plus stable", False,
     "228 443 avis jugés de 2016 à 2026 : 55,78 % de bonnes réponses sans lissage, 55,79 % à 55,82 % avec (moyennes de 2 à 5 jours ou lissage exponentiel). "
     "Le gain global est du bruit, et 5 ou 6 années sur 11 reculent (jusqu'à −0,8 point). Non adopté : l'IA ne doit jamais faire moins bien"),
    ("70", "Fourchettes « conformes » : recalculer chaque année la marge des fourchettes à partir des erreurs passées, globalement ou marché par marché", False,
     "515 008 cas, jugés sur 2018-2026 : la version globale revient au réglage déjà utilisé par le site (tenue proche de 79 % pour 80 % promis) ; "
     "la version par marché déséquilibre les cryptos (85 % au lieu de 80 %) et n'améliore pas la pire année. Non adopté"),
    ("70", "Ajouter le ton des actualités au calcul de l'IA", False,
     "Impossible à tester honnêtement aujourd'hui : il n'existe pas d'historique fiable du ton des actus pour les années passées. "
     "Le ton des actus de chaque titre est désormais archivé chaque soir ; il sera testé sur des jours que l'IA n'a pas vus dès qu'il y aura assez de recul. "
     "En attendant, il sert seulement de garde-fou (signal fort suspendu si les actus sont nettement négatives)"),
    ("69", "Quand l'IA hésite (chances entre 47 et 53 sur 100), suivre plutôt le sens habituel du marché", False,
     "Vrais cours 2018-2026 : +0,1 à +0,2 point au total, mais l'IA perd jusqu'à 1,4 point en 2022 et un peu en 2018, 2019 et 2024. "
     "Règle du site : jamais de baisse. Non adopté : l'avis reste celui de l'IA, marqué « confiance faible »"),
    ("68.1", "Pousser un peu l'avis hausse/baisse vers le sens habituel du marché (10 % de « le marché monte d'habitude »)", False,
     "Vrais cours 2018-2026 : +0,4 point en moyenne (54,8 % contre 54,5 %), mais ça vient des années de hausse ; en 2022 l'IA perd 2 points "
     "(45,3 % contre 47,3 %), en 2024 et 2018 aussi, et les chances sont moins bien calibrées. Règle du site : l'IA ne doit jamais baisser. Non adopté"),
    ("68", "Recalibrer les « chances sur 100 » de l'avis hausse/baisse (régression isotonique apprise sur les années d'avant, globale ou par marché)", False,
     "Vrais cours 2018-2026, 195 124 avis : justesse 53,8 % (globale) et 54,8 % (par marché) contre 54,5 % aujourd'hui, et chances moins bien "
     "calibrées (Brier 0,2519 et 0,2509 contre 0,2480). Non adopté"),
    ("68", "Rapprocher les « chances sur 100 » de 50 (facteur appris chaque année sur les années d'avant), le sens restant le même", False,
     "Même justesse (54,5 %) mais chances un peu moins bien calibrées (Brier 0,2486 contre 0,2480). Non adopté. Constat honnête : quand l'IA "
     "affiche environ 62 chances sur 100, elle a raison environ 58 fois sur 100 ; les niveaux de confiance restent bien rangés "
     "(faible 50,7 %, moyenne 55,3 %, forte 58,2 %)"),
    ("67", "« Avis sûrs » aussi pour le sens du prix (monte / baisse), comme pour l'agitation : seuil appris sur les années d'avant", False,
     "Vrais cours 2018-2026 : visé 58 %, obtenu 54,3 % alors que « toujours la hausse » faisait 54,8 % dans les mêmes cas ; visé 60 %, obtenu 52,0 %. "
     "Les avis les plus tranchés ne tiennent pas sur les années suivantes. Non adopté : l'avis reste toujours donné (hausse ou baisse), avec sa confiance"),
    ("67", "Moyenne de deux IA d'agitation (avec et sans « l'écart à sa normale ») au lieu d'une seule", False,
     "Avis sûrs 80,6 % contre 80,8 %, tous les cas 70,5 % contre 70,5 %, erreur médiane un peu moins bonne : pas de gain. Non adopté"),
    ("66.1", "La même règle d'accord avec « retour vers sa normale », appliquée aussi au niveau « avis sûr »", False,
     "80,8 % de justes pour 51,7 % des cas, contre 80,8 % pour 52,3 % sans la règle : un peu moins d'avis, pas plus justes. Non adopté"),
    ("66", "« Avis très sûr » seulement quand l'IA et la règle simple « retour vers sa normale de l'année » sont d'accord (seuil réappris dans ces cas-là)", True,
     "Vrais cours 2017-2026 : 44 390 avis très sûrs au lieu de 40 473 (+9,7 %) pour la même justesse (89,0 % contre 89,0 % ; écart −0,7 à +0,9 point), "
     "plus d'avis 9 années sur 10. Pire année 83,0 % contre 83,6 %. Adopté : plus d'avis très sûrs sans perdre en justesse"),
    ("65", "Un seuil d'« avis sûr » propre à chaque marché (ou à chaque sens : plus agité / plus calme), pour donner plus d'avis sûrs", False,
     "Par marché : 80,9 % juste pour 50,4 % des cas, contre 80,8 % pour 52,3 % avec un seuil commun (moins d'avis, pas plus justes). "
     "Par sens : 80,3 % pour 52,4 %. En avis très sûrs, la pire année tombe de 83,6 % à 80,0 %. Aucun gain, non adopté"),
    ("65", "Les avis sûrs enregistrés chaque soir et vérifiés en public 20 séances plus tard", True,
     "Même règle que le test sur les années passées ; rien n'est effacé (page « Avis de l'IA vérifiés »)"),
    ("64", "« L'écart à sa normale » ajouté aussi au modèle du risque de forte chute", False,
     "Note de tri 0,7451 → 0,7444, score de Brier inchangé (marge −0,0002 à +0,0002), mieux 7 années sur 13 seulement : aucun gain, non adopté"),
    ("63.4", "Un 2e niveau d'avis : « avis très sûr », quand l'écart avec les dernières semaines est encore plus net", True,
     "89,0 % de bonnes réponses (marge 87,4 % à 90,5 %) sur environ 1 cas sur 5 ; pire année 83,6 %. Affiché sur les fiches concernées"),
    ("63", "« Avis sûrs » : l'IA ne répond à « plus ou moins agité le mois prochain ? » que quand sa prévision s'écarte nettement des dernières semaines "
     "(seuil appris chaque année sur les seules années d'avant)", True,
     "80,8 % de bonnes réponses sur 119 493 avis (marge 79,3 % à 82,4 %), au moins 77 % dix années sur onze, pour environ la moitié des cas. "
     "Repère honnête : dans les mêmes cas, la règle simple « l'agitation revient vers sa normale » fait environ 78 %"),
    ("63", "« L'écart à sa normale » : comparer l'agitation récente d'un titre à sa médiane de l'année et de ses 3 derniers mois", True,
     "« Plus ou moins agité ? » 70,25 % → 70,52 % sur 257 322 cas (marge du gain +0,07 à +0,44 point), erreur plus faible 11 années sur 13 : adopté"),
    ("63", "Un 2e modèle spécialisé (classifieur) pour « plus ou moins agité ? » à la place du modèle d'agitation", False,
     "69,7 % contre 70,3 % pour le modèle d'agitation actuel, sur les mêmes 257 322 cas : moins bien, non adopté"),
    ("59", "Nouvelle question posée à l'IA : « le mois prochain, plus ou moins agité que ces dernières semaines ? »", True,
     "70,9 % de bonnes réponses sur 514 838 cas (marge 69,9 % à 72,0 %), contre 51 % pour la réponse la plus fréquente ; "
     "au-dessus de 60 % les 13 années sur 13. Affichée sur chaque fiche"),
    ("59", "« IA juge » : une 2e IA apprend quand la 1re a raison sur le sens du prix, et ne la laisse parler que dans ces cas-là",
     False, "56,14 % de bonnes réponses contre 56,01 % pour la tendance habituelle, sur 228 443 avis : gain non prouvé (marge −0,3 à +0,5 point), "
     "5 années gagnées sur 11. Piste à retester quand il y aura plus de données"),
    ("58", "« Mémoire du titre » pour le risque de chute : sa fréquence passée de fortes chutes et son agitation passée",
     True, "note 0,7518 → 0,7554 (marge +0,0016 à +0,0052) sur 514 838 cas, mieux sur les deux moitiés de la période, Brier meilleur dans les 5 marchés"),
    ("58", "« Mémoire du titre » pour l'agitation", False, "erreur un peu plus grande, de façon sûre"),
    ("58", "Risque de chute « en deux étages » (l'agitation prévue donnée comme indice)", False, "gain non prouvé (marge −0,0005 à +0,0026)"),
    ("54", "Moyenne de 3 IA entraînées différemment", False, "risque de chute 0,752 contre 0,754, gain négligeable pour l'agitation"),
    ("54", "Plus de poids aux années récentes", False, "moins bien partout (risque de chute 0,730 à 0,748 contre 0,754)"),
    ("53", "Recalage du risque de chute par marché", False, "actions sous-estimées : écart moyen par marché 1,35 pt contre 1,12 pt"),
    ("52", "Fourchettes calées sur l'agitation prévue", False, "plus larges et moins régulières"),
    ("51", "Risque propre à chaque titre (volatilité hors marché, bêta, à-coups, liquidité)", True,
     "risque de chute 0,747 → 0,754, agitation 24,2 % → 23,9 % d'erreur, mieux sur les 5 marchés"),
    ("51", "IA séparées pour les cryptos et les actions", False, "moins bonnes"),
]


def _idees_testees():
    lignes = "".join(f"<tr><td>v{v}</td><td>{_e(idee)}<br><span class='muted'>{_e(det)}</span></td>"
                     f"<td>{'✅ adoptée' if ok else '➖ rejetée'}</td></tr>" for v, idee, ok, det in IDEES_TESTEES)
    return ("<p>Chaque idée est jugée sur des années que l'IA n'avait jamais vues ; elle n'est gardée que si le gain est prouvé "
            "et régulier. La plupart sont rejetées : c'est ce qui garde l'IA honnête.</p>"
            f"<table><thead><tr><th>Version</th><th>Idée</th><th>Verdict</th></tr></thead><tbody>{lignes}</tbody></table>")


def _memoire_actus():
    """Version 57 : l'IA garde chaque jour la tonalité des actualités et le nombre d'articles qui parlent de krach.
    Elle ne s'en servira pour prévoir que si un test sur assez de jours montre que ça aide vraiment."""
    try:
        from . import pages_marche
        n = len(pages_marche.lire_memoire())
    except Exception:
        n = 0
    return ("<p>Chaque jour, l'IA note la tonalité des actualités qu'elle lit, le nombre d'articles qui parlent de krach ou de bulle, "
            "la peur des marchés et son risque de chute moyen. Aujourd'hui, les actualités ne servent que de <b>garde-fou</b> "
            "(elles peuvent rendre un avis plus prudent, jamais plus confiant), car on n'a pas encore d'historique pour prouver "
            f"qu'elles améliorent les prévisions.</p><p><b>{n} jour{'s' if n > 1 else ''} en mémoire</b> sur les 250 nécessaires "
            "(environ un an de marché) pour un premier test honnête. Si ce test montre un gain prouvé, les actualités entreront "
            "dans les prévisions ; sinon, elles resteront un simple éclairage.</p>")


def _page_journal_ia(base, csp):
    """Version 56 : ce que l'IA a essayé chaque nuit, ce qu'elle a adopté (seulement si c'est prouvé), et ses scores."""
    from . import autoreglage, model
    chemin = "journal-ia.html"
    j = autoreglage.journal()
    noms = {"agitation": ("L'IA de l'agitation à un mois", "erreur médiane", True),
            "chute": ("L'IA du risque de forte chute", "note (AUC)", False)}

    def score(nom, v):
        if v is None:
            return "–"
        return f"{v * 100:.1f} %" if noms[nom][2] else f"{v:.3f}"
    cartes = ""
    for nom, (titre, lib, _) in noms.items():
        a = (j["adoptes"] or {}).get(nom)
        p = autoreglage.reglages(nom)
        etat = (f"Réglages adoptés le {seo.date_longue(a['date'][:10])} : {lib} {score(nom, a.get('score_avant'))} → "
                f"<b>{score(nom, a.get('score_apres'))}</b> sur les années sous clé." if a else
                "Réglages d'origine : aucun essai n'a encore fait mieux de façon prouvée.")
        cartes += (f"<div class='carte'><h3 style='margin-top:0'>{_e(titre)}</h3><p>{etat}</p>"
                   f"<p class='muted' style='margin:0'>{_e(autoreglage._texte(p))} · "
                   f"{sum(1 for e in j['journal'] if (e.get(nom) or {}).get('essayes'))} nuits d'essais</p></div>")
    lignes = ""
    for e in reversed(j["journal"][-30:]):
        cell = lambda nom: ("–" if not e.get(nom) else
                            f"{e[nom].get('essayes', 0)} essai{'s' if e[nom].get('essayes', 0) > 1 else ''}"
                            + (" · <b>✅ adopté</b>" if e[nom].get("adopte") else ""))
        lignes += (f"<tr><td>{_e(seo.date_longue(e['date'][:10]))}</td><td>{cell('agitation')}</td><td>{cell('chute')}</td></tr>")
    tableau = (f"<table class='tab'><thead><tr><th>Nuit</th><th>Agitation</th><th>Forte chute</th></tr></thead><tbody>{lignes}</tbody></table>"
               if lignes else "<p class='muted'>Le premier auto-réglage aura lieu lors du prochain entraînement de nuit.</p>")
    sens = (model._lire_fichier_modele() or {}).get("entrainements") or []
    der = sens[-1] if sens else None
    texte_sens = (f"<p>L'IA du sens du prix (proche du hasard, voir la <a href='fiche-technique-ia.html'>fiche technique</a>) s'entraîne aussi : "
                  f"{len(sens)} entraînement{'s' if len(sens) > 1 else ''} gardé{'s' if len(sens) > 1 else ''} en mémoire"
                  + (f", le dernier le {seo.date_longue(str(der.get('date', ''))[:10])}" if der and der.get("date") else "") + ".</p>") if sens else ""
    corps = ("<h1>Journal de l'IA : ce qu'elle essaie chaque nuit</h1>"
             "<p>Chaque nuit, pendant que les marchés dorment, l'IA essaie de nouveaux réglages pour ses deux prévisions les plus fiables : "
             "<b>l'agitation des prix à un mois</b> et <b>le risque de forte chute</b>. Elle garde la mémoire de tous ses essais : "
             "la moitié des nouvelles idées part de ses meilleures pistes, l'autre moitié est tirée au hasard.</p>"
             "<p><b>Règle anti-chance :</b> un réglage n'est adopté que s'il fait mieux que l'IA en place <b>de façon prouvée</b> "
             "(marge d'erreur à 95 %) sur des années qu'elle n'a jamais vues, <b>et</b> sur chacune des deux moitiés de cet examen. "
             "La plupart des nuits, rien ne change : c'est normal, et c'est voulu.</p>"
             f"<h2>Où en est l'IA</h2>{cartes}"
             f"<p class='muted'>{j['nb_essais']} réglages essayés au total, tous gardés en mémoire pour guider les nuits suivantes.</p>"
             f"<h2>Les 30 dernières nuits</h2>{tableau}{texte_sens}"
             f"<h2>La mémoire des actualités</h2>{_memoire_actus()}"
             f"<h2>Les idées testées, adoptées ou rejetées</h2>{_idees_testees()}"
             "<p>Voir aussi : <a href='resultats.html'>les résultats réels, mois par mois</a> · "
             "<a href='connaissances.html'>ce que sait l'IA</a> · <a href='a-propos.html'>à propos</a></p>")
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": "Journal de l'IA de Radar Bourse", "url": url, "inLanguage": "fr",
         "description": "Ce que l'IA de Radar Bourse a essayé chaque nuit pour s'améliorer, et ce qu'elle a adopté."},
        seo._jsonld_fil(base, [(NOM, ""), ("Journal de l'IA", chemin)])]}
    return chemin, seo._page(base, f"Journal de l'IA : comment elle s'améliore chaque nuit | {NOM}",
                             "Chaque nuit, l'IA de Radar Bourse essaie de nouveaux réglages et n'adopte que ceux qui font mieux de façon prouvée "
                             "sur des années jamais vues. Le journal complet, essais ratés compris.", chemin, corps, jl, csp=csp)


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    urls = []
    for chemin, page in (_page_fonctionnalites(base, payload, csp), _page_simulateur(base, csp),
                         _page_a_propos(base, payload, csp), _page_contact(base, csp), _page_journal_ia(base, csp)):
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily" if chemin == "journal-ia.html" else "weekly",
                     "0.9" if chemin in ("simulateur-boursier.html", "fonctionnalites.html") else "0.6" if chemin == "journal-ia.html" else "0.5"))
    return urls
