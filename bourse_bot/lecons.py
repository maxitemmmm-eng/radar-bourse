"""Mini-cours « Apprendre la Bourse » : pages statiques, simples et illustrées.

Chaque leçon : (identifiant, titre, description, durée, contenu HTML, à retenir, question, réponse).
"""
from __future__ import annotations

SVG_BOUGIE = """<svg viewBox="0 0 320 170" width="320" role="img" aria-label="Schéma de deux bougies : verte en hausse, rouge en baisse" style="max-width:100%;height:auto">
<line x1="80" y1="15" x2="80" y2="155" stroke="#0b8a4f" stroke-width="3"/><rect x="60" y="45" width="40" height="80" rx="4" fill="#0b8a4f"/>
<text x="110" y="20" font-size="12" fill="currentColor">plus haut</text><text x="110" y="50" font-size="12" fill="currentColor">clôture</text>
<text x="110" y="125" font-size="12" fill="currentColor">ouverture</text><text x="110" y="158" font-size="12" fill="currentColor">plus bas</text>
<line x1="250" y1="15" x2="250" y2="155" stroke="#c9352f" stroke-width="3"/><rect x="230" y="45" width="40" height="80" rx="4" fill="#c9352f"/>
<text x="196" y="50" font-size="12" fill="currentColor" text-anchor="end">ouverture</text><text x="196" y="125" font-size="12" fill="currentColor" text-anchor="end">clôture</text></svg>"""

SVG_TENDANCE = """<svg viewBox="0 0 320 150" width="320" role="img" aria-label="Schéma d'une tendance haussière avec support et résistance" style="max-width:100%;height:auto">
<line x1="10" y1="40" x2="310" y2="40" stroke="#c9352f" stroke-dasharray="6 4" stroke-width="2"/><text x="12" y="34" font-size="12" fill="#c9352f">résistance</text>
<line x1="10" y1="120" x2="310" y2="120" stroke="#0b8a4f" stroke-dasharray="6 4" stroke-width="2"/><text x="12" y="138" font-size="12" fill="#0b8a4f">support</text>
<polyline points="10,110 50,70 80,95 120,50 150,80 190,45 220,70 260,42 300,20" fill="none" stroke="#1d4fd8" stroke-width="3"/>
<text x="232" y="16" font-size="12" fill="currentColor">cassure ↑</text></svg>"""

SVG_RISQUE = """<svg viewBox="0 0 320 140" width="320" role="img" aria-label="Comparaison : perdre 50 % demande de gagner 100 % pour revenir" style="max-width:100%;height:auto">
<rect x="20" y="20" width="120" height="100" rx="6" fill="#1d4fd8" opacity=".25"/><text x="80" y="75" font-size="14" text-anchor="middle" fill="currentColor">1 000 €</text>
<rect x="180" y="70" width="120" height="50" rx="6" fill="#c9352f" opacity=".35"/><text x="240" y="100" font-size="14" text-anchor="middle" fill="currentColor">500 €</text>
<text x="160" y="60" font-size="13" text-anchor="middle" fill="#c9352f">−50 %</text>
<text x="160" y="134" font-size="12" text-anchor="middle" fill="currentColor">pour revenir à 1 000 € : il faut +100 %</text></svg>"""

LECONS = [
    ("action", "C'est quoi une action ?", "Comprendre ce que l'on achète vraiment quand on achète une action.", 4,
     """<p>Une <b>action</b> est un petit morceau d'une entreprise. Si une société est découpée en 1 million d'actions et que tu en possèdes une, tu détiens un millionième de cette entreprise.</p>
<h2>Pourquoi le prix bouge</h2>
<p>Le prix d'une action se fixe comme sur un marché : par la rencontre entre acheteurs et vendeurs. Si beaucoup de gens veulent acheter (bons résultats, nouveau produit, optimisme général), le prix monte. S'ils veulent vendre (mauvaises nouvelles, peur), il baisse.</p>
<h2>Comment on gagne (ou perd) de l'argent</h2>
<ul><li><b>La plus-value</b> : revendre plus cher qu'on a acheté.</li>
<li><b>Le dividende</b> : une partie des bénéfices que certaines entreprises reversent chaque année à leurs actionnaires.</li>
<li><b>La moins-value</b> : revendre moins cher. Si l'entreprise fait faillite, l'action peut ne plus rien valoir.</li></ul>
<h2>Indices et ETF</h2>
<p>Un <b>indice</b> (CAC 40, S&amp;P 500) mesure l'évolution d'un groupe d'actions. Un <b>ETF</b> est un produit qui copie un indice : en l'achetant, on achète d'un coup un petit morceau de toutes les entreprises de l'indice, ce qui répartit le risque.</p>""",
     "Une action = une part d'entreprise. Son prix dépend de l'offre et de la demande, et peut baisser jusqu'à zéro.",
     "Si tu achètes une action à 50 € et que l'entreprise verse 2 € de dividende, puis que tu revends à 45 €, as-tu gagné ou perdu ?",
     "Perdu : −5 € sur le prix + 2 € de dividende = −3 € au total."),
    ("crypto", "C'est quoi une cryptomonnaie ?", "Bitcoin, Ethereum : comment ça marche et pourquoi c'est si risqué.", 4,
     """<p>Une <b>cryptomonnaie</b> est une monnaie numérique qui fonctionne sans banque centrale. Les échanges sont enregistrés dans un grand registre public partagé entre des milliers d'ordinateurs : la <b>blockchain</b>.</p>
<h2>Ce qui la différencie d'une action</h2>
<p>Derrière une action, il y a une entreprise qui vend des produits et fait (ou non) des bénéfices. Derrière la plupart des cryptos, il n'y a ni bénéfice ni dividende : le prix dépend presque uniquement de ce que les gens sont prêts à payer. C'est pour ça qu'il peut varier de 10 % en une journée.</p>
<h2>Les risques propres aux cryptos</h2>
<ul><li><b>Volatilité extrême</b> : des baisses de 70 à 90 % sont déjà arrivées, même pour le Bitcoin.</li>
<li><b>Plateformes</b> : des plateformes d'échange ont fait faillite ou ont été piratées, et leurs clients ont tout perdu.</li>
<li><b>Arnaques</b> : jetons créés pour être gonflés puis vendus (« pump and dump »), faux projets, faux conseillers.</li></ul>
<p>En France, l'AMF publie la liste des prestataires enregistrés. Vérifie toujours une plateforme avant d'y mettre de l'argent.</p>""",
     "Une crypto n'a pas d'entreprise ni de bénéfices derrière elle : son prix peut s'effondrer très vite.",
     "Pourquoi un jeton inconnu qui a pris +500 % en une semaine est-il dangereux ?",
     "Parce que ces hausses viennent souvent d'une manipulation : les créateurs revendent au sommet et le prix s'effondre ensuite."),
    ("bougies", "Lire un graphique en bougies", "Les bougies japonaises expliquées en 3 minutes.", 3,
     f"""<p>Sur les graphiques de Radar Bourse, chaque <b>bougie</b> résume une journée de cotation.</p>{SVG_BOUGIE}
<ul><li><b>Bougie verte</b> : le prix a fini la journée plus haut qu'il ne l'a commencée.</li>
<li><b>Bougie rouge</b> : le prix a fini plus bas.</li>
<li>Le <b>corps</b> (rectangle) va du prix d'ouverture au prix de clôture.</li>
<li>Les <b>mèches</b> (traits fins) montrent jusqu'où le prix est monté et descendu pendant la journée.</li></ul>
<h2>Quelques figures connues</h2>
<p>Un <b>doji</b> (corps minuscule) traduit l'hésitation. Un <b>marteau</b> (longue mèche basse après une baisse) montre que les acheteurs ont repoussé les vendeurs. Ces figures sont des indices, jamais des certitudes : elles ratent souvent.</p>""",
     "Vert = hausse sur la journée, rouge = baisse. Les mèches montrent les extrêmes du jour.",
     "Une bougie a un corps très petit et de longues mèches en haut et en bas. Que traduit-elle ?",
     "L'hésitation : les acheteurs et les vendeurs se sont équilibrés (c'est un doji)."),
    ("tendance", "Tendances, supports et résistances", "Repérer la direction d'un marché et ses niveaux clés.", 4,
     f"""<p>Une <b>tendance haussière</b> est une suite de sommets et de creux de plus en plus hauts. Une tendance baissière, l'inverse. Entre les deux, le marché fait du « range » : il oscille sans direction.</p>{SVG_TENDANCE}
<h2>Les moyennes mobiles</h2>
<p>La <b>moyenne 200 jours</b> (ligne orange sur le site) lisse les mouvements pour montrer la tendance de fond. Un cours au-dessus est généralement vu comme un bon signe, en dessous comme un signal de prudence. La moyenne 50 jours (ligne bleue) suit la tendance récente.</p>
<h2>Supports et résistances</h2>
<p>Un <b>support</b> est un niveau où le prix a souvent rebondi, une <b>résistance</b> un niveau où il a souvent buté. Quand le prix casse une résistance avec de forts volumes, la hausse continue souvent ; quand il casse un support, la baisse peut s'accélérer.</p>""",
     "La tendance de fond se lit avec la moyenne 200 jours ; supports et résistances sont des zones à surveiller.",
     "Le cours passe au-dessus de sa résistance mais avec des volumes très faibles. Faut-il s'en méfier ?",
     "Oui : une cassure sans volume est fragile, le prix retombe souvent sous la résistance."),
    ("indicateurs", "RSI et MACD : mesurer l'élan", "Les deux indicateurs les plus utilisés, sans jargon.", 4,
     """<p>Les indicateurs d'<b>élan</b> (momentum) mesurent la force et la vitesse d'un mouvement.</p>
<h2>Le RSI</h2>
<p>Le RSI va de 0 à 100. Au-dessus de <b>70</b>, le titre a beaucoup monté en peu de temps : il est dit « suracheté » et peut faire une pause. Sous <b>30</b>, il a beaucoup baissé : il est « survendu » et peut rebondir. Attention, dans une tendance très forte, le RSI peut rester au-dessus de 70 pendant des semaines.</p>
<h2>Le MACD</h2>
<p>Le MACD compare deux moyennes, une rapide et une lente. Quand l'histogramme passe du négatif au positif, l'élan devient haussier. C'est un signal tardif mais utile pour confirmer une tendance.</p>
<h2>Les divergences</h2>
<p>Si le prix fait un nouveau sommet mais que le RSI n'en fait pas, l'élan s'essouffle : c'est une <b>divergence baissière</b>. Le site les signale automatiquement dans la fiche de chaque titre.</p>""",
     "RSI > 70 : peut-être monté trop vite. RSI < 30 : peut-être trop baissé. Aucun indicateur n'est fiable seul.",
     "Le RSI d'une action est à 82. Est-ce une raison suffisante pour être sûr qu'elle va baisser ?",
     "Non : cela indique une surchauffe possible, mais dans une forte tendance la hausse peut continuer longtemps."),
    ("risque", "Gérer son risque", "La compétence la plus importante, avant toute analyse.", 5,
     f"""<p>Même avec la meilleure analyse du monde, on se trompe souvent. Ce qui fait la différence sur la durée, c'est la façon de <b>limiter les pertes</b>.</p>{SVG_RISQUE}
<p>Perdre 50 % oblige à gagner 100 % pour revenir au point de départ. C'est pour ça que les grosses pertes sont si difficiles à rattraper.</p>
<h2>Les règles de base</h2>
<ul><li><b>Le stop-loss</b> : décider à l'avance du prix auquel on vend si on s'est trompé, et s'y tenir.</li>
<li><b>La règle des 1 à 2 %</b> : ne jamais risquer plus de 1 à 2 % de son capital sur une opération. Le calculateur de chaque fiche (onglet Simulateur) fait le calcul pour toi.</li>
<li><b>La diversification</b> : ne pas tout mettre sur un seul titre ou un seul secteur.</li>
<li><b>Pas d'argent emprunté, pas d'effet de levier</b> : ils transforment une petite erreur en catastrophe.</li></ul>""",
     "Limiter ses pertes compte plus que chercher le gain maximal : stop-loss, 1 à 2 % de risque, diversification.",
     "Tu as 2 000 € et tu acceptes de risquer 1 % par opération. Quelle perte maximale acceptes-tu sur une opération ?",
     "20 € (1 % de 2 000 €). Le reste se règle avec la taille de la position et le stop-loss."),
    ("pieges", "Les pièges à éviter", "Arnaques, biais et erreurs classiques des débutants.", 4,
     """<h2>Les arnaques</h2>
<p>Rendement « garanti », gains rapides, conseiller rencontré sur Instagram ou Telegram, pression pour se décider vite, demande de virement vers une plateforme inconnue : ce sont les signes classiques d'une escroquerie. Vérifie toujours sur la liste noire de l'AMF (amf-france.org).</p>
<h2>Les pièges dans notre tête</h2>
<ul><li><b>La peur de rater le train</b> (FOMO) : acheter parce que « tout le monde en parle », souvent au plus haut.</li>
<li><b>Vouloir se refaire</b> : augmenter ses mises après une perte. C'est le chemin le plus court vers la ruine.</li>
<li><b>Le biais de confirmation</b> : ne lire que ce qui confirme ce qu'on pense déjà.</li>
<li><b>L'excès de confiance</b> après quelques gains : souvent, c'était de la chance.</li></ul>
<h2>Quand demander de l'aide</h2>
<p>Si tu regardes les cours sans arrêt, caches tes pertes ou empruntes pour continuer, le trading devient un problème. Joueurs Info Service (09 74 75 13 13) écoute anonymement, 7 jours sur 7.</p>""",
     "Méfie-toi des promesses de gains rapides et de tes propres réflexes : FOMO, envie de se refaire, excès de confiance.",
     "Un inconnu sur un réseau social te promet 20 % par mois « sans risque ». Que fais-tu ?",
     "Rien : aucun placement légal ne garantit ce rendement. C'est presque toujours une arnaque."),
    ("long-terme", "Investir sur le long terme", "Pourquoi le temps est souvent le meilleur allié.", 4,
     """<p>À court terme, la Bourse ressemble à un pile ou face. Sur de longues périodes, les grands indices mondiaux ont historiquement progressé, avec des baisses parfois très fortes en chemin. Rien ne garantit que ce sera le cas à l'avenir.</p>
<h2>Les intérêts composés</h2>
<p>Quand les gains produisent eux-mêmes des gains, l'argent grossit de plus en plus vite. C'est pour ça que commencer tôt, même avec de petites sommes régulières, compte plus que de chercher le « bon coup ».</p>
<h2>Quelques notions utiles</h2>
<ul><li><b>Les ETF larges</b> (sur un indice mondial) permettent de diversifier très simplement.</li>
<li><b>Investir régulièrement</b> (la même somme chaque mois) évite d'avoir à deviner le bon moment.</li>
<li><b>L'épargne de précaution d'abord</b> : garder de côté de quoi faire face aux imprévus avant d'investir.</li></ul>
<p>Ces informations sont générales. Pour ta situation personnelle, renseigne-toi auprès de sources officielles (AMF, Banque de France) ou d'un professionnel agréé.</p>""",
     "Le temps, la régularité et la diversification comptent plus que la recherche du coup parfait.",
     "Vaut-il mieux attendre le « meilleur moment » pour investir une grosse somme, ou investir un peu chaque mois ?",
     "Personne ne sait prédire le meilleur moment ; investir régulièrement lisse le prix d'achat et évite de dépendre de la chance."),
]
