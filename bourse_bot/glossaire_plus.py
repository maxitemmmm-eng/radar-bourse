"""Explications détaillées de chaque mot du glossaire (version 33) : une page par mot.
Pour chaque mot : à quoi ça sert concrètement, et le piège à éviter. Le texte de base reste dans seo.GLOSSAIRE."""

PLUS = {
    "Bougie (chandelier japonais)": (
        "Une bougie résume une journée en un coup d'œil : qui a gagné entre acheteurs et vendeurs, et avec quelle force. "
        "Une longue mèche basse veut dire que le prix est descendu puis a été racheté ; un grand corps vert, que les acheteurs ont dominé toute la journée.",
        "Une bougie seule dit très peu de choses. Les « figures » célèbres (marteau, étoile du soir…) se trompent souvent : "
        "sur le radar, elles ne servent que d'indice parmi d'autres."),
    "Moyenne mobile (SMA)": (
        "Elle lisse les hauts et les bas pour montrer la direction de fond. Beaucoup d'investisseurs regardent si le prix est "
        "au-dessus ou en dessous de sa moyenne 50 jours (tendance moyenne) et 200 jours (tendance longue).",
        "Une moyenne regarde le passé : elle réagit toujours en retard. Dans un marché sans direction, le prix la traverse sans cesse "
        "et donne de faux signaux."),
    "Moyenne mobile exponentielle (EMA)": (
        "Comme la moyenne simple, mais plus réactive : les derniers jours comptent davantage. Elle sert de base au MACD.",
        "Plus réactive veut aussi dire plus de faux signaux. Une EMA courte suit le bruit autant que la tendance."),
    "Golden cross / death cross": (
        "Ces croisements résument un changement de tendance longue en un seul événement facile à repérer, d'où leur succès dans les médias.",
        "Ils arrivent souvent tard, quand une bonne partie du mouvement est déjà faite. Testés sur le passé, ils ne sont pas une recette miracle."),
    "RSI": (
        "Le RSI aide à repérer un emballement : un titre qui a monté très vite (RSI au-dessus de 70) ou chuté très vite (en dessous de 30). "
        "Il se calcule en général sur 14 séances.",
        "« Surachat » ne veut pas dire « va baisser » : dans une forte tendance, le RSI peut rester au-dessus de 70 pendant des semaines "
        "pendant que le prix continue de monter."),
    "Divergence": (
        "Elle signale un essoufflement : le prix fait un nouveau sommet mais l'indicateur (RSI, MACD) n'en fait pas, comme si la force s'épuisait.",
        "Une divergence peut durer longtemps avant que le prix ne se retourne, et souvent il ne se retourne pas du tout."),
    "MACD": (
        "Le MACD compare une moyenne rapide et une moyenne lente pour mesurer l'élan d'un titre. Le passage de son histogramme au-dessus de zéro "
        "est souvent lu comme un regain de force.",
        "Il est construit avec des moyennes, donc en retard. Seul, il ne fait pas mieux que le hasard sur beaucoup de marchés."),
    "Bandes de Bollinger": (
        "Elles dessinent un couloir autour de la moyenne, plus large quand le marché est agité. Un couloir qui se resserre annonce souvent "
        "un mouvement plus fort à venir, sans dire dans quel sens.",
        "Toucher la bande haute n'est pas un signal de vente : dans une tendance, le prix peut « marcher » le long de la bande."),
    "ATR": (
        "L'ATR mesure de combien un prix bouge en moyenne chaque jour. Il sert à placer un stop-loss à une distance raisonnable et "
        "à comparer l'agitation de deux titres.",
        "L'ATR ne dit rien de la direction : un ATR élevé veut dire « ça bouge beaucoup », à la hausse comme à la baisse."),
    "ADX": (
        "L'ADX mesure la force d'une tendance, de 0 à 100. Au-dessus de 25, la tendance est nette ; en dessous de 20, le marché tourne en rond.",
        "Il ne dit pas si la tendance est haussière ou baissière, seulement si elle est forte."),
    "Stochastique": (
        "Il situe le prix du jour par rapport aux plus hauts et plus bas récents. Proche de 100 : le prix est en haut de sa fourchette récente.",
        "Très nerveux, il change souvent de zone. Comme le RSI, « suracheté » ne veut pas dire « va baisser »."),
    "Ichimoku": (
        "Système japonais complet : le « nuage » montre en un coup d'œil la tendance, des zones de support et de résistance, et l'élan.",
        "Beaucoup de lignes, donc facile de s'y perdre et de voir ce qu'on veut y voir. Il fonctionne surtout dans les marchés qui ont une vraie tendance."),
    "Supertrend": (
        "Une ligne qui suit le prix en tenant compte de son agitation : sous le prix en tendance haussière, au-dessus en tendance baissière. "
        "Elle sert souvent de stop-loss qui suit le mouvement.",
        "Dans un marché sans tendance, elle change de côté souvent et fait perdre de petites sommes à répétition."),
    "Volume": (
        "Le volume compte combien de titres ont été échangés. Une hausse avec beaucoup de volume est jugée plus solide qu'une hausse dans le calme.",
        "Les volumes des cryptos varient beaucoup d'une plateforme à l'autre : ils sont moins fiables que ceux des actions."),
    "OBV, MFI, Chaikin Money Flow": (
        "Ces indicateurs essaient de voir si l'argent entre ou sort d'un titre, en combinant prix et volume.",
        "Ce sont des estimations indirectes : personne ne voit vraiment qui achète et qui vend."),
    "VWAP": (
        "Le prix moyen payé pendant une période, pondéré par les volumes. Les professionnels s'en servent pour juger s'ils ont acheté cher ou bon marché.",
        "Utile surtout à court terme ; sur un mois, il apporte peu."),
    "Support et résistance": (
        "Un support est un niveau où le prix a souvent arrêté de baisser ; une résistance, un niveau où il a souvent arrêté de monter. "
        "Beaucoup d'acheteurs et de vendeurs les surveillent.",
        "Ces niveaux finissent toujours par céder un jour. Ce sont des zones floues, pas des lignes exactes."),
    "Stop-loss": (
        "Un ordre qui vend automatiquement si le prix descend sous un niveau choisi à l'avance, pour limiter une perte. "
        "Le radar propose sur chaque fiche un niveau calculé avec l'agitation du titre.",
        "Trop serré, il se déclenche sur un simple mouvement normal. Et lors d'une chute brutale (à l'ouverture, par exemple), "
        "la vente peut se faire bien plus bas que prévu."),
    "Règle des 1 à 2 %": (
        "Ne jamais risquer plus de 1 à 2 % de son capital sur une seule idée. Avec 5 000 €, ça veut dire accepter de perdre au maximum 50 à 100 € par position.",
        "Elle limite les dégâts, elle ne rend pas une mauvaise idée bonne. Elle suppose aussi de respecter son stop-loss."),
    "PER": (
        "Le PER compare le prix d'une action aux bénéfices de l'entreprise. Un PER de 20 veut dire que l'on paie 20 années de bénéfices actuels. "
        "Il sert à comparer des entreprises d'un même secteur.",
        "Un PER bas peut cacher une entreprise en difficulté, un PER élevé une entreprise qui grandit vite. "
        "Comparer le PER d'une banque à celui d'une entreprise technologique n'a pas de sens."),
    "VIX": (
        "Surnommé « indice de la peur », il mesure l'agitation que les investisseurs attendent sur le S&P 500 dans les 30 prochains jours. "
        "Au-dessus de 30, les marchés sont nerveux.",
        "Un VIX bas ne garantit pas le calme : les plus grosses chutes partent souvent de périodes très tranquilles."),
    "Fear & Greed crypto": (
        "Un indice de 0 (peur extrême) à 100 (euphorie) qui résume l'humeur du marché crypto à partir des prix, des volumes et des réseaux sociaux.",
        "Acheter dans la peur et vendre dans l'euphorie est une idée populaire, mais l'humeur peut rester extrême longtemps."),
    "Probabilité calibrée": (
        "Une probabilité est « calibrée » quand elle tient parole : sur 100 prévisions à 60 %, environ 60 se sont réalisées. "
        "Le radar recale chaque soir ses chiffres sur ce qui s'est vraiment passé.",
        "60 % veut aussi dire que 40 fois sur 100, c'est l'inverse qui arrive. Une probabilité n'est jamais une certitude."),
    "Validation walk-forward": (
        "La façon honnête de tester une IA de prévision : elle apprend sur le passé, puis on la juge sur les mois suivants qu'elle n'a jamais vus, "
        "en avançant dans le temps. C'est comme ça que le radar mesure sa fiabilité.",
        "Un test où l'IA a déjà « vu » les réponses donne des résultats trop beaux. Méfie-toi des taux de réussite annoncés sans cette précaution."),
    "Simulation de Monte-Carlo": (
        "On rejoue des milliers de futurs possibles en tirant au hasard des journées passées, pour voir l'éventail des prix plausibles dans un mois.",
        "La simulation suppose que l'avenir ressemble au passé. Une crise jamais vue peut sortir de tous les scénarios."),
}
