"""Version 78 : « Vos questions sur la Bourse » — les questions que les gens tapent vraiment dans Google, avec des réponses honnêtes.

Chaque réponse renvoie vers la page du site qui va plus loin (prévisions, Académie, outils). Données structurées FAQPage.
Aucun conseil personnalisé, aucune promesse : quand personne ne peut savoir, on le dit.
"""
import html


def _e(s):
    return html.escape(str(s), quote=True)


def _cent_euros(mensuel=100, taux=5, ans=20):
    t = taux / 100 / 12
    return mensuel * ((1 + t) ** (ans * 12) - 1) / t, mensuel * 12 * ans


MOTS = ("est-ce que la bourse va baisser, faut-il acheter du bitcoin maintenant, combien rapporte 100 euros par mois en bourse, la bourse c'est risqué, "
        "comment reconnaître une arnaque trading, quelle action acheter en ce moment avis, action qui va monter cette semaine, prédiction cours action demain, "
        "IA bourse fiable, prévision action IA gratuite, prévision CAC 40 semaine prochaine, crypto qui va exploser avis honnête, risque de krach boursier aujourd'hui, "
        "site prédiction bourse sans inscription, investir 50 euros par mois, DCA ou investir d'un coup, calcul flat tax 2026, flat tax 31,4 %, "
        "cours de bourse en ligne gratuit avec certificat, simulateur de trading sans argent réel, "
        "l'action va-t-elle remonter, faut-il acheter une action qui a baissé, krach IA, bulle IA bourse, bourse aujourd'hui, prévision crypto 2030, "
        "prévision XRP 2030, que veut dire EPA bourse, code bourse NYSE HKG, prévisions boursières fiables")


CSS_ACCORDEON = ("<style>.q-sommaire{columns:2 280px;gap:24px;padding-left:18px;margin:18px 0 26px}.q-sommaire li{margin:4px 0;break-inside:avoid}"
             ".q-bloc{border:1px solid var(--line);border-radius:12px;margin:10px 0;background:var(--surface);scroll-margin-top:110px;transition:border-color .2s}"
             ".q-bloc[open]{border-color:var(--accent)}.q-bloc summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 18px}"
             ".q-bloc summary::-webkit-details-marker{display:none}.q-bloc summary:hover h2{color:var(--accent)}.q-bloc h2{font-size:19px;margin:0;transition:color .15s}"
             ".q-plus{flex:none;width:22px;height:22px;position:relative}.q-plus::before,.q-plus::after{content:'';position:absolute;left:4px;right:4px;top:10px;height:2px;border-radius:2px;background:currentColor;transition:transform .3s cubic-bezier(.2,.8,.2,1)}"
             ".q-plus::after{transform:rotate(90deg)}.q-bloc[open] .q-plus::after{transform:rotate(0)}"
             ".q-rep{padding:0 18px 6px}.q-rep p{max-width:72ch;margin-top:0}.q-bloc[open] .q-rep{animation:qOuvre .35s cubic-bezier(.2,.8,.2,1)}"
             "@keyframes qOuvre{from{opacity:0;transform:translateY(-6px)}}@media (prefers-reduced-motion:reduce){.q-bloc[open] .q-rep{animation:none}.q-plus::before,.q-plus::after{transition:none}}"
             ".q-outils{display:flex;gap:10px;margin:0 0 6px}</style>")
JS_ACCORDEON = ("<script>(function(){const ds=[...document.querySelectorAll('.q-bloc')];const ouvrir=()=>{const h=decodeURIComponent(location.hash.slice(1));const d=h&&document.getElementById(h);"
             "if(d&&d.tagName==='DETAILS'){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});}};addEventListener('hashchange',ouvrir);ouvrir();"
             "const b=document.getElementById('q-tout');b.onclick=()=>{const o=!ds.every(d=>d.open);ds.forEach(d=>d.open=o);b.textContent=o?b.dataset.fermer:b.dataset.ouvrir;};})();</script>")


def questions():
    total, verse = _cent_euros()
    gain = total - verse
    nb = lambda x: f"{x:,.0f}".replace(",", " ")
    return [
        ("baisse", "Est-ce que la Bourse va baisser ?",
         "Personne ne peut le savoir avec certitude, ni un humain ni une IA. Ce qu'on peut mesurer, c'est le <b>risque</b> : l'agitation prévue et la part de titres "
         "qui risquent une forte chute. C'est ce que montre en direct la page <a href='krach-boursier.html'>risque de krach aujourd'hui</a>, et l'avis de l'IA "
         "sur un mois est sur <a href='prediction-bourse.html'>prédiction bourse</a>. Sur longue période, les grands indices ont jusqu'ici fini par remonter, "
         "mais cela a parfois pris très longtemps : plus de 21 ans pour le CAC 40 (2000-2021), plus de 34 ans pour l'indice japonais Nikkei (1989-2024)."),
        ("bitcoin", "Faut-il acheter du bitcoin maintenant ?",
         "Ce site ne donne pas de conseil personnalisé : la réponse dépend de ta situation. Ce qu'il faut savoir : le bitcoin a déjà perdu plus de 70 % plusieurs fois, "
         "n'investis que ce que tu peux perdre, et préfère un prestataire agréé (liste blanche de l'AMF). L'avis de l'IA, avec son niveau de confiance, est sur "
         "<a href='prediction-crypto.html'>prédiction bitcoin et crypto</a> ; pour comprendre avant d'acheter, l'Académie a un "
         "<a href='formation/blockchain-bitcoin.html'>module entier sur la crypto</a>."),
        ("cent-euros", "Combien rapportent 100 € par mois en Bourse ?",
         f"Rien n'est garanti, mais voici un ordre de grandeur. Avec 100 € par mois pendant 20 ans et un rendement moyen de 5 % par an (une hypothèse, pas une promesse), "
         f"tu aurais versé {nb(verse)} € et tu aurais environ <b>{nb(total)} €</b>, soit environ {nb(gain)} € de gains, avant impôts et frais. Une mauvaise période "
         "peut faire beaucoup moins. Fais tes propres calculs avec le <a href='outils/interets-composes.html'>simulateur d'intérêts composés</a> et lis le chapitre "
         "<a href='formation/investir-regulierement.html'>investir un peu chaque mois</a>."),
        ("risque", "La Bourse, c'est risqué ?",
         "Oui : la valeur d'un placement peut baisser, parfois beaucoup, et rien n'est garanti. Le risque se réduit en <b>diversifiant</b> (un ETF monde plutôt qu'une seule action), "
         "en investissant sur <b>longtemps</b>, régulièrement, et en gardant une épargne de précaution à côté. Le chapitre "
         "<a href='formation/rendement-risque.html'>rendement et risque</a> l'explique en quelques minutes, avec exercices."),
        ("arnaque", "Comment reconnaître une arnaque au trading ?",
         "Les signaux d'alerte : un gain élevé <b>garanti</b>, une offre « valable aujourd'hui seulement », un contact par message ou réseau social, un effet de levier énorme, "
         "une demande de virement à l'étranger ou en crypto. Vérifie toujours le nom sur les listes noires de l'AMF avant d'agir. Exemples concrets dans "
         "<a href='formation/arnaques-et-pieges.html'>arnaques et pièges</a> et dans l'étude de cas <a href='formation/cas-decortiquer-une-pub.html'>une publicité de trading décortiquée</a>."),
        ("monter", "Quelle action va monter cette semaine ?",
         "Personne ne le sait de façon fiable : sur une semaine, les mouvements sont en grande partie du hasard. L'IA de Radar Bourse donne un avis à <b>un mois</b>, avec "
         "ses chances et sa confiance ; les titres qu'elle voit monter sont dans les <a href='classements.html'>classements</a>, et ses erreurs sont publiées sur "
         "<a href='resultats.html'>résultats réels</a>."),
        ("fiable", "Une IA de Bourse est-elle fiable ?",
         "Une IA peut aider, mais aucune ne lit l'avenir. Sur des années qu'elle n'avait jamais vues, celle de Radar Bourse a eu raison sur le sens du prix environ "
         "51 fois sur 100 quand sa confiance était faible et 58 fois sur 100 quand elle était forte. Elle est bien meilleure pour prévoir l'<b>agitation</b>. "
         "Tout est vérifiable sur <a href='resultats.html'>résultats réels</a> et <a href='journal-ia.html'>le journal de l'IA</a>. Méfie-toi de tout service qui promet plus "
         "sans publier ses ratés."),
        ("demain", "Peut-on prédire le cours d'une action demain ?",
         "Pas de façon fiable : à un jour, le bruit domine. Radar Bourse ne fait donc pas de prévision au jour le jour, mais un avis à un mois et une "
         "<b>fourchette</b> de prix probable, sans inscription. Exemples : <a href='titres/mc-pa.html'>avis IA sur LVMH</a>, <a href='titres/nvda.html'>Nvidia</a>, "
         "<a href='titres/tsla.html'>Tesla</a>, <a href='titres/tte-pa.html'>TotalEnergies</a>, <a href='titres/air-pa.html'>Airbus</a>."),
        ("cac40", "Que prévoit l'IA pour le CAC 40 ?",
         "L'avis du mois sur les grandes valeurs françaises est sur <a href='prediction-bourse.html'>prédiction bourse</a>, et le résumé de la semaine sur "
         "<a href='bourse-cette-semaine.html'>la semaine en Bourse</a>. Ce sont des probabilités, jamais des certitudes."),
        ("exploser", "Quelle crypto va exploser ?",
         "Réponse honnête : personne ne le sait. Les cryptos qui ont « explosé » à la hausse ont souvent explosé à la baisse ensuite, et beaucoup de petites cryptos ont "
         "disparu. Compare plutôt l'agitation prévue des cryptos sur <a href='prediction-crypto.html'>prédiction crypto</a> et lis "
         "<a href='formation/altcoins-stablecoins.html'>altcoins, stablecoins et memecoins</a>."),
        ("flat-tax", "Combien coûte la flat tax en 2026 ?",
         "Sur un compte-titres et pour la crypto, le prélèvement forfaitaire unique est de <b>31,4 %</b> en 2026 (12,8 % d'impôt sur le revenu + 18,6 % de prélèvements sociaux). "
         "Calcule ton cas avec le <a href='outils/plus-value.html'>calculateur de plus-value et flat tax</a>, et vois les autres enveloppes dans "
         "<a href='formation/pea-cto-assurance-vie.html'>PEA, compte-titres ou assurance-vie</a>."),
        ("dca", "Faut-il investir d'un coup ou un peu chaque mois ?",
         "Sur un marché qui monte, investir d'un coup rapporte en moyenne un peu plus ; investir chaque mois (le DCA) évite de tout miser au mauvais moment et se tient "
         "mieux psychologiquement. Avec 50 € par mois, le DCA est souvent la seule option réaliste, et c'est très bien. Détails dans "
         "<a href='formation/investir-regulierement.html'>investir un peu chaque mois</a>."),
        ("apprendre", "Où apprendre la Bourse gratuitement, avec un certificat ?",
         "L'<a href='formation.html'>Académie Radar Bourse</a> est gratuite et sans compte : des leçons courtes avec exercices corrigés, des études de cas, un "
         "<a href='formation/entrainement.html'>entraînement du jour</a> et un <a href='formation/examen.html'>examen final</a> qui donne un certificat."),
        # version 85 : six questions de plus, tirées des recherches qui arrivent vraiment sur le site (Search Console)
        ("remonter", "Une action qui a beaucoup baissé va-t-elle remonter ?",
         "Pas forcément. Une forte baisse ne rend pas une action « pas chère » : elle peut refléter de vrais problèmes (ventes en recul, dette, procès), et certaines "
         "ne remontent jamais. Une perte de 50 % demande une hausse de 100 % pour revenir au point de départ. Avant de « renforcer », demande-toi si tu l'achèterais aujourd'hui "
         "à ce prix sans l'avoir déjà. Sur chaque fiche, l'IA donne son avis à un mois (par exemple <a href='titres/rno-pa.html'>Renault</a> ou <a href='titres/af-pa.html'>Air France-KLM</a>), "
         "et le chapitre <a href='formation/psychologie-investisseur.html'>psychologie de l'investisseur</a> explique pourquoi on s'accroche à une perte."),
        ("krach-ia", "Y a-t-il une bulle et un risque de krach de l'IA ?",
         "Personne ne peut dater un krach. Ce qu'on sait : les valeurs liées à l'IA ont beaucoup monté et pèsent lourd dans les grands indices américains, donc une déception "
         "toucherait beaucoup de portefeuilles. Les bulles passées (internet en 2000) ont fait perdre plus de 70 % à certains indices technologiques. Le niveau de risque du jour "
         "est sur <a href='krach-boursier.html'>risque de krach aujourd'hui</a> ; l'histoire des krachs est dans <a href='formation/krachs-et-cycles.html'>krachs et cycles</a>."),
        ("aujourdhui", "Que fait la Bourse aujourd'hui ?",
         "Les grands indices, les plus fortes hausses et baisses du jour et l'avis de l'IA sont résumés dans <a href='point.html'>le point du jour</a>, mis à jour automatiquement, "
         "et sur <a href='index.html'>l'accueil</a> avec les cours. Pour la vue d'ensemble de la semaine : <a href='bourse-cette-semaine.html'>la semaine en Bourse</a>."),
        ("prevision-longue", "Peut-on prévoir le prix d'une crypto en 2030 ou 2050 ?",
         "Non. Les sites qui affichent un prix précis pour le XRP, le Polkadot ou le Bitcoin en 2030 prolongent une tendance ou un calcul arbitraire, sans aucune preuve que ça marche. "
         "Sur des années, une crypto peut être multipliée par dix ou disparaître. Radar Bourse ne prévoit qu'à un mois et publie ses ratés : voir "
         "<a href='prediction-crypto.html'>prédiction crypto</a> et <a href='resultats.html'>résultats réels</a>."),
        ("codes", "Que veulent dire « EPA: », « NYSE: » ou « HKG: » devant le nom d'une action ?",
         "C'est le code de la Bourse où l'action est cotée, suivi de son symbole : EPA pour Euronext Paris (EPA: MC = LVMH), NYSE et NASDAQ pour New York, HKG pour Hong Kong, "
         "TPE pour Taïwan, TYO pour Tokyo. Une même entreprise peut être cotée sur plusieurs places, dans des devises différentes. Toutes les actions suivies sont sur "
         "<a href='toutes-les-actions.html'>toutes les actions</a>."),
        ("previsions-fiables", "Les prévisions boursières sont-elles fiables ?",
         "Sur le sens du prix à court terme, aucune prévision n'est très fiable : même les meilleurs modèles ont raison un peu plus d'une fois sur deux. On prévoit beaucoup mieux "
         "l'agitation (de combien un prix risque de bouger) que la direction. Une prévision sérieuse donne une probabilité, une fourchette et ses résultats passés, ratés compris. "
         "C'est ce que fait le <a href='resultats.html'>tableau des résultats</a> de Radar Bourse ; le chapitre <a href='formation/utiliser-ia-intelligemment.html'>utiliser une IA intelligemment</a> "
         "explique comment les lire."),
        ("sans-argent", "Où s'entraîner sans argent réel ?",
         "Avec le <a href='simulateur-boursier.html'>simulateur boursier</a> (10 000 € fictifs), le <a href='index.html#portefeuille'>portefeuille virtuel</a> et le "
         "<a href='index.html#prono'>pronostic du jour</a>, où tu affrontes l'IA. Tout est gratuit, sans inscription."),
    ]


def generer(seo, base, dossier, csp):
    import os
    qs = questions()
    # version 85 : chaque question s'ouvre et se ferme avec une petite animation (le texte reste dans la page pour Google)
    blocs = "".join(f"<details class='q-bloc' id='{a}'><summary><h2>{_e(q)}</h2><span class='q-plus' aria-hidden='true'></span></summary>"
                    f"<div class='q-rep'><p>{r}</p></div></details>" for a, q, r in qs)
    sommaire = "".join(f"<li><a href='#{a}'>{_e(q)}</a></li>" for a, q, _ in qs)
    corps = (CSS_ACCORDEON +
             "<h1>Vos questions sur la Bourse, la crypto et l'IA</h1>"
             "<p class='muted'>Les questions que l'on nous pose le plus, avec des réponses honnêtes : quand personne ne peut savoir, on le dit. "
             "Ce ne sont pas des conseils personnalisés. <a href='en/questions.html' hreflang='en' lang='en'>English version</a></p>"
             f"<ol class='q-sommaire'>{sommaire}</ol><p class='q-outils'><button class='btn ghost' type='button' id='q-tout' data-ouvrir='Tout ouvrir' data-fermer='Tout fermer'>Tout ouvrir</button></p>{blocs}"
             + JS_ACCORDEON)
    import re
    jl = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for _a, q, r in qs]}
    chemin = "questions-bourse.html"
    page = seo._page(base, f"Vos questions sur la Bourse et l'IA : réponses honnêtes | {seo.NOM}",
                     "La Bourse va-t-elle baisser ? Faut-il acheter du bitcoin ? Combien rapportent 100 € par mois ? Une IA de bourse est-elle fiable ? "
                     "Des réponses honnêtes, chiffrées et sans promesse.", chemin, corps, jl, csp=csp, mots=MOTS,
                     alternates={"fr": chemin, "en": "en/questions.html", "x-default": chemin})
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(page)
    from . import questions_en   # version 86 : la même page en anglais
    return [chemin] + questions_en.generer(base, dossier, csp)
