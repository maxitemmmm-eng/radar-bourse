"""Version 104 : le contenu réservé à Radar Bourse+ (parcours « Analyste »).

Chaque leçon a une partie publique (titre, résumé, plan : visibles par tous et par Google) et une partie réservée,
servie uniquement par le petit serveur d'abonnement (worker) après vérification de l'abonnement.
Le contenu réservé n'est JAMAIS écrit dans les pages du site.
"""

LECONS_PLUS = [
    {
        "id": "lire-un-bilan",
        "titre": "Lire un bilan comme un analyste",
        "resume": "Actif, passif, fonds propres, dette nette, besoin en fonds de roulement : lire le bilan d'une vraie entreprise et repérer ses forces et ses fragilités.",
        "minutes": 25,
        "plan": ["Les deux colonnes du bilan", "Les fonds propres et ce qu'ils racontent", "La dette nette, le vrai chiffre de l'endettement",
                 "Le besoin en fonds de roulement", "Les cinq signaux d'alerte", "Exercice corrigé : deux entreprises face à face"],
        "contenu": """
<h2>Les deux colonnes du bilan</h2>
<p>Le bilan est une photo de l'entreprise à une date précise (souvent le 31 décembre). À gauche, l'<b>actif</b> : tout ce qu'elle possède ou contrôle (usines, brevets, stocks, créances sur ses clients, trésorerie). À droite, le <b>passif</b> : d'où vient l'argent qui a financé cet actif, soit des <b>fonds propres</b> (l'argent des actionnaires, apporté ou accumulé), soit des <b>dettes</b>. Les deux colonnes sont toujours égales : chaque euro possédé a été financé par quelqu'un.</p>
<p>Pour lire vite, regroupe en quatre blocs : actif immobilisé (ce qui sert longtemps), actif circulant (stocks, créances, trésorerie), fonds propres, dettes (financières d'un côté, fournisseurs et fiscales de l'autre).</p>
<h2>Les fonds propres et ce qu'ils racontent</h2>
<p>Les fonds propres = actif total − toutes les dettes. Ils augmentent quand l'entreprise fait des bénéfices qu'elle garde, et baissent quand elle perd de l'argent, verse des dividendes ou rachète ses actions. Une entreprise dont les fonds propres montent régulièrement sur 5 ans crée de la valeur comptable ; s'ils baissent alors qu'elle ne verse rien, elle perd de l'argent.</p>
<p>Attention à la <b>survaleur</b> (goodwill) : quand une entreprise en rachète une autre plus cher que sa valeur comptable, la différence est inscrite à l'actif. Si le goodwill représente une grosse part des fonds propres, une seule dépréciation peut les faire fondre.</p>
<h2>La dette nette, le vrai chiffre de l'endettement</h2>
<p><b>Dette nette = dettes financières − trésorerie.</b> Une entreprise avec 10 Md€ de dettes et 9 Md€ de trésorerie est bien moins fragile qu'une autre avec 3 Md€ de dettes et rien en caisse. On la compare ensuite à ce que l'entreprise gagne : <b>dette nette / EBITDA</b> (l'EBITDA est le résultat avant intérêts, impôts et amortissements, une mesure de la trésorerie produite par l'activité). En dessous de 2, c'est confortable ; au-dessus de 4, la moindre baisse d'activité devient dangereuse (les banques et les agences de notation regardent ce ratio en premier).</p>
<h2>Le besoin en fonds de roulement (BFR)</h2>
<p>BFR = stocks + créances clients − dettes fournisseurs. C'est l'argent immobilisé par le cycle d'exploitation. Un supermarché a souvent un BFR <b>négatif</b> : il vend comptant et paie ses fournisseurs à 60 jours, ce qui lui donne de la trésorerie gratuite. Un fabricant d'avions a un BFR énorme : il construit pendant des mois avant d'être payé. Un BFR qui grossit plus vite que le chiffre d'affaires est un signal à surveiller (stocks qui s'accumulent, clients qui paient de plus en plus tard).</p>
<h2>Les cinq signaux d'alerte</h2>
<ol><li>Fonds propres qui baissent plusieurs années de suite sans dividende ni rachat d'actions.</li>
<li>Dette nette / EBITDA au-dessus de 4, ou qui monte vite.</li>
<li>Goodwill supérieur aux fonds propres.</li>
<li>Créances clients qui augmentent beaucoup plus vite que les ventes.</li>
<li>Trésorerie qui baisse alors que l'entreprise annonce des bénéfices : les bénéfices comptables ne se transforment pas en argent.</li></ol>
<h2>Exercice corrigé : deux entreprises face à face</h2>
<p><b>A</b> : actif 500, dettes financières 150, trésorerie 120, autres dettes 100, EBITDA 60. <b>B</b> : actif 500, dettes financières 300, trésorerie 20, autres dettes 120, EBITDA 55.</p>
<p><b>Corrigé.</b> Fonds propres A = 500 − 150 − 100 = 250 ; B = 500 − 300 − 120 = 80. Dette nette A = 150 − 120 = 30, soit 0,5 fois l'EBITDA : très solide. Dette nette B = 300 − 20 = 280, soit 5,1 fois l'EBITDA : fragile, une année difficile peut la mettre en danger. À chiffre d'affaires égal, A a beaucoup plus de marge de manœuvre.</p>
<p class="muted">Cours éducatif : il ne constitue pas un conseil en investissement.</p>
""",
    },
    {
        "id": "valoriser-dcf",
        "titre": "Valoriser une entreprise : le DCF pas à pas",
        "resume": "Ce que vaut une entreprise d'après l'argent qu'elle produira : flux de trésorerie, taux d'actualisation, valeur terminale, et pourquoi le résultat est si sensible aux hypothèses.",
        "minutes": 30,
        "plan": ["L'idée : un euro demain vaut moins qu'un euro aujourd'hui", "Les flux de trésorerie disponibles", "Le taux d'actualisation",
                 "La valeur terminale", "De la valeur de l'entreprise au prix par action", "La sensibilité : le piège du DCF", "Exercice corrigé"],
        "contenu": """
<h2>L'idée : un euro demain vaut moins qu'un euro aujourd'hui</h2>
<p>Le DCF (discounted cash flows, « flux de trésorerie actualisés ») estime ce que vaut une entreprise en additionnant tout l'argent qu'elle produira dans le futur, ramené à sa valeur d'aujourd'hui. Pourquoi « ramené » ? Parce qu'un euro reçu dans 5 ans vaut moins qu'un euro aujourd'hui : on aurait pu le placer entre-temps, et il y a un risque de ne jamais le recevoir.</p>
<p>Avec un taux de 8 %, 100 € reçus dans un an valent aujourd'hui 100 ÷ 1,08 = 92,6 €. Dans deux ans : 100 ÷ 1,08² = 85,7 €. C'est l'<b>actualisation</b>.</p>
<h2>Les flux de trésorerie disponibles (free cash-flow)</h2>
<p>Free cash-flow = trésorerie produite par l'activité − investissements nécessaires (usines, machines, logiciels). C'est l'argent qui reste vraiment, et qui pourrait être rendu aux actionnaires et aux prêteurs. On le projette en général sur 5 à 10 ans, en partant de l'historique et d'hypothèses de croissance prudentes.</p>
<h2>Le taux d'actualisation</h2>
<p>On utilise souvent le <b>coût moyen pondéré du capital</b> (CMPC, ou WACC en anglais) : le rendement qu'exigent ensemble les actionnaires et les prêteurs. Pour une grande entreprise stable, il tourne souvent autour de 7 à 9 % ; pour une jeune entreprise risquée, bien plus. Plus le taux est élevé, plus les flux lointains « pèsent » peu.</p>
<h2>La valeur terminale</h2>
<p>On ne peut pas projeter année par année jusqu'à l'infini. Après la dernière année projetée, on suppose une croissance constante g, faible (souvent 1,5 à 2,5 %, pas plus que la croissance de l'économie). Valeur terminale = flux de l'année suivante ÷ (taux − g). Elle représente souvent <b>plus de la moitié</b> de la valeur totale : c'est la partie la plus fragile du calcul.</p>
<h2>De la valeur de l'entreprise au prix par action</h2>
<p>La somme des flux actualisés + la valeur terminale actualisée donne la <b>valeur d'entreprise</b>. On retire la dette nette pour obtenir la valeur des fonds propres, puis on divise par le nombre d'actions. On compare ensuite au cours de Bourse.</p>
<h2>La sensibilité : le piège du DCF</h2>
<p>Changer le taux de 8 % à 9 %, ou la croissance terminale de 2 % à 1,5 %, peut faire varier la valeur de 20 à 30 %. Un DCF n'est donc pas un « vrai prix » : c'est un outil pour comprendre <b>quelles hypothèses</b> le marché fait déjà. Les analystes présentent toujours un tableau de sensibilité (plusieurs taux × plusieurs croissances) plutôt qu'un chiffre unique.</p>
<h2>Exercice corrigé</h2>
<p>Une entreprise produit 100 M€ de free cash-flow par an, sans croissance pendant 3 ans, puis +2 % par an pour toujours. Taux : 8 %. Dette nette : 200 M€. 50 millions d'actions.</p>
<p><b>Corrigé.</b> Flux actualisés des années 1 à 3 : 100/1,08 + 100/1,08² + 100/1,08³ = 92,6 + 85,7 + 79,4 = 257,7 M€. Valeur terminale fin d'année 3 : 102 ÷ (0,08 − 0,02) = 1 700 M€, actualisée : 1 700 ÷ 1,08³ = 1 349,5 M€. Valeur d'entreprise ≈ 1 607 M€ ; moins la dette nette : 1 407 M€ ; par action : environ 28 €. Avec un taux de 9 % au lieu de 8 %, on tombe vers 24 € (−16 %) : voilà la sensibilité.</p>
<p class="muted">Cours éducatif : il ne constitue pas un conseil en investissement.</p>
""",
    },
    {
        "id": "pieges-statistiques",
        "titre": "Les pièges statistiques des prévisions (et de notre propre IA)",
        "resume": "Surapprentissage, biais du survivant, fuite de données, tests multiples, prévisions qui se chevauchent : pourquoi tant de « stratégies gagnantes » s'effondrent en vrai, et comment Radar Bourse s'en protège.",
        "minutes": 25,
        "plan": ["Le surapprentissage", "Le biais du survivant", "La fuite de données (regarder le futur sans le savoir)",
                 "Les tests multiples : le gagnant par hasard", "Les prévisions qui se chevauchent", "Backtest contre conditions réelles", "Exercice : repérer le piège"],
        "contenu": """
<h2>Le surapprentissage</h2>
<p>Un modèle qui apprend « par cœur » le passé, y compris son bruit, paraît excellent sur les données d'entraînement et décevant sur des données nouvelles. Plus un modèle a de réglages par rapport à la quantité de données, plus le risque est grand. La seule protection fiable : juger le modèle sur des <b>années qu'il n'a jamais vues</b> (c'est ce que fait Radar Bourse, année après année).</p>
<h2>Le biais du survivant</h2>
<p>Si on teste une stratégie uniquement sur les entreprises qui existent encore aujourd'hui, on oublie celles qui ont fait faillite ou ont été retirées de la cote. Le passé paraît alors plus rose qu'il ne l'était. Ce biais gonfle surtout les résultats sur les petites entreprises et les cryptos (beaucoup ont disparu). Limite honnête de notre propre test : notre univers de titres est celui d'aujourd'hui, donc nos résultats historiques en sont un peu affectés ; c'est une des raisons pour lesquelles nous publions les résultats en conditions réelles.</p>
<h2>La fuite de données</h2>
<p>C'est utiliser, sans s'en rendre compte, une information qui n'était pas encore connue à la date de la prévision : une moyenne calculée en incluant les jours suivants, des résultats financiers publiés des semaines après la date de clôture, des chiffres économiques révisés après coup. Le modèle semble alors « deviner » le futur. Règle : chaque donnée doit être datée du jour où elle était réellement disponible.</p>
<h2>Les tests multiples : le gagnant par hasard</h2>
<p>Teste 100 stratégies sans aucune valeur : par pur hasard, quelques-unes auront l'air brillantes. Choisir la meilleure après coup, c'est choisir un coup de chance. Remèdes : fixer l'hypothèse avant le test, compter combien d'essais ont été faits, et confirmer sur une période jamais utilisée pour choisir. C'est pour cela que Radar Bourse n'adopte un changement que s'il ne dégrade aucune année de test.</p>
<h2>Les prévisions qui se chevauchent</h2>
<p>Une prévision à un mois faite chaque jour : celle du lundi et celle du mardi partagent 19 jours sur 20. Elles ne sont pas indépendantes. 1 000 prévisions qui se chevauchent valent beaucoup moins que 1 000 expériences séparées : les marges d'erreur calculées naïvement sont trop étroites. Même chose quand 100 actions montent ensemble parce que tout le marché monte.</p>
<h2>Backtest contre conditions réelles</h2>
<p>Un backtest (test sur le passé), même propre, reste une simulation. Les conditions réelles ajoutent les frais, les cours qui sautent à l'ouverture, les marchés qui changent de comportement. C'est pourquoi un site sérieux montre les deux et explique l'écart : sur Radar Bourse, la fourchette « 8 fois sur 10 » tenait environ 81 fois sur 100 en test, et nettement moins en conditions réelles ; les fiches affichent les deux chiffres.</p>
<h2>Exercice : repérer le piège</h2>
<p>« Notre stratégie a gagné 40 % par an de 2015 à 2025, testée sur les 30 actions les plus grosses du Nasdaq aujourd'hui, après avoir essayé 200 combinaisons d'indicateurs. » Combien de pièges ?</p>
<p><b>Corrigé.</b> Au moins deux : le <b>biais du survivant</b> (les plus grosses d'aujourd'hui sont, par définition, celles qui ont le mieux réussi) et les <b>tests multiples</b> (200 combinaisons, on garde la meilleure). Probablement aussi aucun test sur une période jamais vue. Ce chiffre ne dit presque rien de l'avenir.</p>
<p class="muted">Cours éducatif : il ne constitue pas un conseil en investissement.</p>
""",
    },
]
