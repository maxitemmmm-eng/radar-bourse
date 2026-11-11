"""Version 70 : l'Académie Radar Bourse — niveaux 3, 4 et 5 (analyser une entreprise, lire le marché, investir comme un pro)."""

COURS_3 = [
    dict(
        id="lire-les-comptes", niveau=3, minutes=8,
        titre="Lire les comptes d'une entreprise",
        desc="Chiffre d'affaires, marge, bénéfice, dette : les quatre chiffres à regarder en premier.",
        mots="lire un compte de résultat, analyse fondamentale débutant, chiffre d'affaires bénéfice différence, marge nette, analyser une action",
        sections=[
            ("Le compte de résultat en une phrase",
             "<p>Il raconte l'année : <b>ce que l'entreprise a vendu</b> (le chiffre d'affaires), moins <b>ce que ça lui a coûté</b>, égale "
             "<b>ce qu'elle a gagné</b> (le résultat net, ou bénéfice).</p>"),
            ("Les quatre chiffres clés",
             "<ul><li><b>Chiffre d'affaires</b> : le total des ventes. Est-ce qu'il grandit d'année en année ?</li>"
             "<li><b>Marge opérationnelle</b> : le résultat des activités ÷ le chiffre d'affaires. Une marge de 20 % signifie que sur 100 € vendus, il reste 20 € avant intérêts et impôts.</li>"
             "<li><b>Résultat net</b> : ce qui reste vraiment à la fin, pour les actionnaires.</li>"
             "<li><b>Dette nette</b> (dans le bilan) : dettes moins trésorerie. Une dette élevée rend l'entreprise fragile quand les taux montent ou que les ventes baissent.</li></ul>"),
            ("Où trouver ces chiffres",
             "<p>Les entreprises cotées publient leurs comptes : rapport annuel et communiqués de résultats, sur leur site (rubrique « Investisseurs » ou « Finance »). "
             "Sur Radar Bourse, la fiche de chaque grande entreprise résume quelques chiffres (bénéfice par action, dividende, PER) quand ils sont disponibles.</p>"),
            ("Un bon réflexe",
             "<p>Regarde toujours <b>plusieurs années</b> et <b>la tendance</b>, pas une seule année. Et compare avec des entreprises du même secteur : "
             "une marge de 5 % est excellente pour un supermarché, faible pour un éditeur de logiciels.</p>"),
        ],
        retenir=["Chiffre d'affaires − coûts = résultat.", "Marge = résultat ÷ chiffre d'affaires.", "La dette nette mesure la fragilité.",
                 "Compare sur plusieurs années et avec le même secteur."],
        quiz=[("Une entreprise vend pour 200 millions € et fait 30 millions € de résultat opérationnel. Sa marge opérationnelle est de…", ["6,7 %", "15 %", "30 %", "170 %"], 1,
               "30 / 200 = 0,15, soit 15 %."),
              ("Le chiffre d'affaires, c'est…", ["Le bénéfice", "Le total des ventes", "La dette", "Le cours de l'action"], 1, "C'est le total des ventes, avant de retirer les coûts."),
              ("Pourquoi comparer la marge avec le même secteur ?", ["Parce que les marges normales varient beaucoup d'un secteur à l'autre", "Ce n'est pas utile", "Pour la fiscalité", "Pour le PEA"], 0,
               "Un supermarché et un éditeur de logiciels n'ont pas du tout les mêmes marges « normales »."),
              ],
        exercice=("<p>Entreprise X : chiffre d'affaires 2024 = 500 M€, 2025 = 550 M€. Résultat net 2024 = 40 M€, 2025 = 38 M€. "
                  "Calcule la croissance des ventes et la marge nette chaque année. Qu'en conclus-tu ?</p>",
                  "<p>Croissance des ventes : (550 − 500) / 500 = <b>+10 %</b>. Marge nette 2024 : 40/500 = <b>8 %</b> ; 2025 : 38/550 = <b>6,9 %</b>. "
                  "L'entreprise vend plus mais gagne moins sur chaque euro vendu : ses coûts augmentent plus vite que ses ventes. À surveiller.</p>"),
        sources=[("AMF : l'information financière des sociétés cotées", "https://www.amf-france.org/fr/espace-epargnants"),
                 ("La finance pour tous : lire un compte de résultat", "https://www.lafinancepourtous.com/decryptages/entreprise/")],
    ),
    dict(
        id="ratios-per-rendement", niveau=3, minutes=7,
        titre="Les ratios clés : PER, rendement, dette",
        desc="Calculer et interpréter les ratios que tout le monde cite.",
        mots="per définition, calcul per action, rendement dividende calcul, ratio dette, ratios boursiers débutant",
        sections=[
            ("Le PER (price earnings ratio)",
             "<p><b>PER = cours de l'action ÷ bénéfice par action</b>. Un PER de 15 signifie que tu paies 15 fois le bénéfice annuel. "
             "Plus il est élevé, plus le marché attend une forte croissance… ou plus l'action est chère. Un PER n'a de sens que comparé "
             "(au secteur, à l'historique de l'entreprise).</p>"),
            ("Le rendement du dividende",
             "<p><b>Rendement = dividende annuel par action ÷ cours</b>. Une action à 50 € qui verse 2 € par an a un rendement de 4 %. "
             "Un rendement très élevé peut être un piège : il vient parfois d'un cours qui s'est effondré parce que le dividende risque d'être coupé.</p>"),
            ("La dette",
             "<p>Un ratio courant : <b>dette nette ÷ EBITDA</b> (en gros, les bénéfices avant intérêts, impôts et amortissements). "
             "Sous 2, c'est en général considéré comme confortable ; au-dessus de 4, la dette devient lourde pour la plupart des secteurs.</p>"),
            ("Les limites",
             "<p>Les ratios sont des photos : ils ne disent rien du futur. Une entreprise avec un PER de 8 peut être bon marché… ou en déclin. "
             "Ils servent à poser des questions, pas à donner des réponses.</p>"),
        ],
        retenir=["PER = cours ÷ bénéfice par action.", "Rendement = dividende ÷ cours.", "Dette nette ÷ EBITDA : sous 2 confortable, au-dessus de 4 lourd.",
                 "Un ratio se compare toujours."],
        quiz=[("Une action cote 60 € pour un bénéfice par action de 4 €. Son PER est…", ["4", "15", "60", "240"], 1, "60 / 4 = 15."),
              ("Une action à 40 € verse 1,60 € de dividende par an. Son rendement est…", ["1,6 %", "4 %", "25 %", "40 %"], 1, "1,60 / 40 = 0,04, soit 4 %."),
              ("Un rendement du dividende de 15 % doit surtout…", ["Rassurer", "Faire vérifier pourquoi le cours a chuté et si le dividende est tenable", "Être ignoré", "Être acheté vite"], 1,
               "Un rendement anormalement élevé signale souvent un risque de baisse du dividende."),
              ],
        exercice=("<p>Deux entreprises du même secteur : A cote 30 € avec un bénéfice par action de 1,5 € ; B cote 90 € avec un bénéfice par action de 9 €. "
                  "Calcule leurs PER. Laquelle paraît la moins chère ? Que faudrait-il vérifier ?</p>",
                  "<p>PER de A = 30 / 1,5 = <b>20</b> ; PER de B = 90 / 9 = <b>10</b>. B paraît deux fois moins chère par rapport à ses bénéfices. "
                  "À vérifier : la croissance attendue de chacune, leur dette, et si les bénéfices de B ne sont pas exceptionnels cette année.</p>"),
        sources=[("La finance pour tous : le PER", "https://www.lafinancepourtous.com/decryptages/marches-financiers/fonctionnement-de-la-bourse/le-per/")],
    ),
    dict(
        id="dividendes", niveau=3, minutes=6,
        titre="Les dividendes : comment ça marche",
        desc="Date de détachement, versement, rendement et la grande illusion du dividende « gratuit ».",
        mots="dividende action explication, date de détachement dividende, vivre des dividendes, action à dividende débutant",
        sections=[
            ("Le principe",
             "<p>Le dividende est une partie des bénéfices que l'entreprise reverse à ses actionnaires, en général une ou plusieurs fois par an. "
             "Il est décidé chaque année par l'assemblée générale : <b>il n'est jamais garanti</b>.</p>"),
            ("Le calendrier",
             "<ul><li><b>Date de détachement</b> : à partir de ce jour, acheter l'action ne donne plus droit au dividende. Le cours baisse en général du montant du dividende ce jour-là.</li>"
             "<li><b>Date de paiement</b> : l'argent arrive sur ton compte quelques jours plus tard.</li></ul>"),
            ("Le dividende n'est pas « gratuit »",
             "<p>Quand une action à 50 € verse 2 €, son cours passe à environ 48 € au détachement : tu as 48 € d'action et 2 € d'argent, soit toujours 50 €. "
             "Le dividende ne crée pas de richesse en lui-même ; il en transfère une partie de l'entreprise vers toi (et peut être taxé au passage, sauf dans un PEA tant que l'argent y reste).</p>"),
            ("Ce qui compte vraiment",
             "<p>Une entreprise qui verse un dividende stable et croissant depuis longtemps montre en général des bénéfices solides. "
             "Mais une entreprise qui ne verse rien et réinvestit tout peut aussi très bien faire. Juge l'entreprise, pas seulement son dividende.</p>"),
        ],
        retenir=["Le dividende n'est jamais garanti.", "Au détachement, le cours baisse d'environ le montant du dividende.",
                 "Un dividende ne crée pas de valeur par magie.", "Dans un PEA, les dividendes peuvent être réinvestis sans impôt tant qu'ils restent dans le plan."],
        quiz=[("Que se passe-t-il en général au détachement du dividende ?", ["Le cours monte du montant du dividende", "Le cours baisse d'environ le montant du dividende", "Rien", "L'action est suspendue"], 1,
               "La valeur versée sort de l'entreprise : le cours s'ajuste à la baisse."),
              ("Qui décide du dividende ?", ["L'AMF", "L'assemblée générale de l'entreprise", "Le courtier", "Euronext"], 1, "C'est l'assemblée générale des actionnaires qui vote le dividende."),
              ("Tu achètes l'action le jour même du détachement. Tu touches le dividende ?", ["Oui", "Non", "Seulement la moitié", "Ça dépend du courtier"], 1,
               "À partir du jour de détachement, l'acheteur n'a plus droit au dividende en cours."),
              ],
        exercice=("<p>Tu as 200 actions à 25 €. L'entreprise verse un dividende de 1 € par action. Sur un compte-titres en 2026 (31,4 % de prélèvement forfaitaire), "
                  "combien touches-tu net ? Que vaut environ ton portefeuille juste après le détachement ?</p>",
                  "<p>Dividende brut : 200 × 1 € = <b>200 €</b>. Net : 200 × (1 − 0,314) = <b>137,20 €</b>. "
                  "Les actions passent à environ 24 € : 200 × 24 = 4 800 €. Total ≈ 4 800 + 137,20 = <b>4 937,20 €</b>, contre 5 000 € avant : "
                  "l'impôt a coûté 62,80 €.</p>"),
        sources=[("AMF : les dividendes", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/actions")],
    ),
    dict(
        id="publications-et-actualite", niveau=3, minutes=6,
        titre="Résultats, annonces et actualité",
        desc="Comment lire une publication de résultats et pourquoi le cours réagit parfois « à l'envers ».",
        mots="publication résultats entreprise, réaction bourse résultats, actualité bourse débutant, calendrier résultats",
        sections=[
            ("Le rythme des publications",
             "<p>Les grandes entreprises publient leurs résultats tous les trimestres ou tous les semestres. Ces jours-là, le cours peut bouger beaucoup plus que d'habitude. "
             "Le <a href='../calendrier-resultats.html'>calendrier des résultats</a> de Radar Bourse te dit quand.</p>"),
            ("Ce que le marché regarde",
             "<ol><li>Les chiffres par rapport au <b>consensus</b> (la moyenne des prévisions des analystes).</li>"
             "<li>Les <b>prévisions</b> de l'entreprise pour la suite (la « guidance »), souvent plus importantes que le passé.</li>"
             "<li>Le ton de la direction : prudent, confiant, évasif ?</li></ol>"),
            ("Les actualités sur Radar Bourse",
             "<p>Chaque fiche affiche les derniers titres d'actualité de l'entreprise, avec la source. L'IA en tient compte de façon limitée : "
             "elle mesure le ton général des titres récents. Lis toujours l'article d'origine avant de conclure : un titre peut être trompeur.</p>"),
            ("Le piège de la réaction immédiate",
             "<p>Acheter ou vendre dans les minutes qui suivent une annonce, c'est jouer contre des professionnels et des algorithmes plus rapides que toi. "
             "Pour un investisseur à long terme, la vraie question est : <b>cette nouvelle change-t-elle les bénéfices de l'entreprise dans les années qui viennent ?</b></p>"),
        ],
        retenir=["Les résultats sont comparés aux attentes (le consensus).", "Les prévisions de l'entreprise comptent souvent plus que le passé.",
                 "Lis l'article d'origine, pas seulement le titre.", "Ne réagis pas dans la minute : demande-toi si les bénéfices futurs changent."],
        quiz=[("Le « consensus », c'est…", ["Un vote de l'AMF", "La moyenne des prévisions des analystes", "Le prix moyen de l'action", "Un type d'ordre"], 1, "C'est la moyenne des prévisions des analystes qui suivent l'entreprise."),
              ("La « guidance », c'est…", ["Les prévisions de l'entreprise pour la suite", "Un indice", "Un courtier", "Une taxe"], 0, "Ce sont les objectifs que l'entreprise annonce pour les mois ou l'année à venir."),
              ("Une bonne question face à une nouvelle importante :", ["Le cours a-t-il bougé de 1 % ?", "Est-ce que ça change les bénéfices futurs de l'entreprise ?", "Que dit un influenceur ?", "Faut-il vendre tout de suite ?"], 1,
               "À long terme, ce sont les bénéfices futurs qui comptent."),
              ],
        exercice=("<p>Une entreprise publie : ventes +8 % (consensus +5 %), bénéfice +6 % (consensus +6 %), mais elle abaisse ses prévisions pour l'an prochain. "
                  "Comment le cours risque-t-il de réagir, et pourquoi ?</p>",
                  "<p>Le cours risque de <b>baisser</b> malgré des chiffres passés corrects : le marché regarde surtout l'avenir, et une baisse des prévisions "
                  "pèse plus que des ventes un peu meilleures qu'attendu.</p>"),
        sources=[("AMF : l'information des sociétés cotées", "https://www.amf-france.org/fr/espace-epargnants")],
    ),
]

COURS_4 = [
    dict(
        id="bougies-tendances", niveau=4, minutes=7,
        titre="Lire un graphique : bougies, tendances, supports",
        desc="Les bases de l'analyse graphique, avec ses limites.",
        mots="lire un graphique bourse, bougies japonaises débutant, support résistance, tendance haussière, analyse technique débutant",
        sections=[
            ("La bougie",
             "<p>Chaque bougie résume une période (un jour, par exemple) : le prix d'<b>ouverture</b>, de <b>clôture</b>, le <b>plus haut</b> et le <b>plus bas</b>. "
             "Verte (ou blanche) : la clôture est au-dessus de l'ouverture. Rouge (ou noire) : en dessous. Les « mèches » montrent les extrêmes atteints.</p>"),
            ("La tendance",
             "<p>Une tendance <b>haussière</b> enchaîne des plus hauts et des plus bas de plus en plus élevés. Une tendance <b>baissière</b>, l'inverse. "
             "Sans direction claire, on parle de « range » (le prix oscille entre deux niveaux).</p>"),
            ("Supports et résistances",
             "<p>Un <b>support</b> est un niveau de prix où les acheteurs sont souvent revenus ; une <b>résistance</b>, un niveau où les vendeurs ont souvent pris le dessus. "
             "Quand une résistance est franchie, elle devient parfois un support.</p>"),
            ("Une limite honnête",
             "<p>L'analyse graphique décrit le passé. De nombreuses études montrent que ses signaux simples ont peu de pouvoir prédictif une fois les frais pris en compte. "
             "Elle sert surtout à <b>lire</b> un graphique et à placer des niveaux de sortie, pas à deviner l'avenir. C'est aussi ce que constate l'IA de Radar Bourse sur ses propres tests.</p>"),
        ],
        retenir=["Une bougie = ouverture, clôture, plus haut, plus bas.", "Tendance haussière = plus hauts et plus bas croissants.",
                 "Support = zone où les acheteurs reviennent ; résistance = zone où les vendeurs dominent.", "L'analyse graphique décrit, elle ne prédit pas de façon fiable."],
        quiz=[("Une bougie verte signifie que…", ["Le prix a clôturé au-dessus de son ouverture", "Le prix a baissé", "Le volume était faible", "L'action verse un dividende"], 0, "Clôture > ouverture."),
              ("Une tendance haussière, c'est…", ["Des plus hauts et des plus bas de plus en plus élevés", "Un prix qui ne bouge pas", "Une seule grosse bougie verte", "Un dividende en hausse"], 0,
               "C'est l'enchaînement de sommets et de creux toujours plus hauts."),
              ("Les signaux graphiques simples permettent-ils de prédire le marché de façon fiable ?", ["Oui, toujours", "Non, leur pouvoir prédictif est faible", "Seulement le lundi", "Seulement pour les cryptos"], 1,
               "Les études et les tests de Radar Bourse montrent un pouvoir prédictif faible : à utiliser avec prudence."),
              ],
        exercice=("<p>Ouvre le graphique d'une fiche (par exemple <a href='../titres/btc-usd.html'>Bitcoin</a>). Repère un niveau de prix que le cours a touché "
                  "au moins deux fois sans le franchir. Est-ce un support ou une résistance ?</p>",
                  "<p>Si le cours a rebondi deux fois <b>vers le haut</b> sur ce niveau, c'est un <b>support</b>. S'il a été repoussé <b>vers le bas</b>, "
                  "c'est une <b>résistance</b>. Plus un niveau a été touché souvent, plus il est surveillé par les autres investisseurs.</p>"),
        sources=[("AMF : l'analyse technique", "https://www.amf-france.org/fr/espace-epargnants")],
    ),
    dict(
        id="moyennes-rsi-macd", niveau=4, minutes=7,
        titre="Moyennes mobiles, RSI et MACD",
        desc="Les trois indicateurs les plus utilisés, comment ils se calculent et ce qu'ils ne disent pas.",
        mots="moyenne mobile 200 jours, rsi explication, macd explication, indicateurs techniques débutant, surachat survente",
        sections=[
            ("La moyenne mobile",
             "<p>La moyenne mobile à 200 jours est la moyenne des 200 derniers cours de clôture. Si le cours est au-dessus, la tendance de fond est plutôt haussière. "
             "Elle lisse le bruit quotidien, mais réagit avec retard.</p>"),
            ("Le RSI",
             "<p>Le RSI mesure, sur 14 jours en général, la force des hausses par rapport aux baisses, sur une échelle de 0 à 100. "
             "Au-dessus de 70, on parle de « surachat » ; sous 30, de « survente ». Attention : une action peut rester en surachat pendant des mois dans une forte hausse.</p>"),
            ("Le MACD",
             "<p>Le MACD compare deux moyennes mobiles (12 et 26 jours, exponentielles). Quand il passe au-dessus de sa ligne de signal (moyenne sur 9 jours), "
             "c'est souvent lu comme un regain d'élan haussier.</p>"),
            ("Ce que Radar Bourse en fait",
             "<p>L'IA du site utilise ces indicateurs parmi des dizaines d'autres, et teste leur utilité sur des années qu'elle n'a jamais vues. "
             "Résultat : pris seuls, ils prévoient mal le sens du prix, mais ils aident un peu à prévoir l'agitation. C'est pourquoi le site met l'agitation en avant.</p>"),
        ],
        retenir=["Moyenne mobile 200 jours = tendance de fond.", "RSI : >70 surachat, <30 survente, mais pas un signal de vente automatique.",
                 "MACD = élan, à partir de deux moyennes mobiles.", "Pris seuls, ces indicateurs prévoient mal le sens du prix."],
        quiz=[("Sur combien de jours calcule-t-on le plus souvent le RSI ?", ["5", "14", "50", "200"], 1, "14 jours est le réglage classique."),
              ("Un RSI à 80 signifie forcément que le cours va baisser.", ["Vrai", "Faux"], 1, "Faux : dans une forte tendance haussière, le RSI peut rester au-dessus de 70 longtemps."),
              ("Une moyenne mobile réagit…", ["En avance sur le prix", "Avec retard sur le prix", "Au hasard", "Seulement le vendredi"], 1, "Elle moyenne le passé : elle suit le prix avec retard."),
              ],
        exercice=("<p>Calcule la moyenne mobile à 5 jours de ces cours de clôture : 10, 11, 12, 11, 13. Puis le lendemain le cours clôture à 15 : quelle est la nouvelle moyenne mobile à 5 jours ?</p>",
                  "<p>(10 + 11 + 12 + 11 + 13) / 5 = <b>11,4</b>. Le lendemain, on retire le plus ancien (10) et on ajoute 15 : (11 + 12 + 11 + 13 + 15) / 5 = <b>12,4</b>. "
                  "Le cours (15) est au-dessus de sa moyenne : signe d'élan haussier à court terme.</p>"),
        sources=[("La finance pour tous : l'analyse technique", "https://www.lafinancepourtous.com/decryptages/marches-financiers/")],
    ),
    dict(
        id="volatilite-et-ia", niveau=4, minutes=6,
        titre="Volatilité : ce qui se prévoit le mieux",
        desc="Pourquoi l'agitation d'un prix est plus prévisible que son sens, et comment lire les fourchettes de Radar Bourse.",
        mots="volatilité bourse explication, prévoir la volatilité, fourchette prévision bourse, risque de chute action",
        sections=[
            ("Le sens est difficile, l'agitation moins",
             "<p>Deviner si une action montera ou baissera le mois prochain est très difficile : même les meilleurs modèles font à peine mieux que le hasard. "
             "En revanche, <b>l'agitation</b> (de combien le prix va bouger) a une mémoire : une période agitée est souvent suivie d'une période encore agitée. "
             "Les chercheurs l'ont montré depuis les années 1980 (modèles GARCH).</p>"),
            ("Lire une fourchette",
             "<p>Sur chaque fiche, Radar Bourse affiche une zone foncée (le prix y finit environ 1 fois sur 2) et une zone claire (environ 8 fois sur 10). "
             "Une fourchette large veut dire « beaucoup d'incertitude » : ce n'est pas un objectif de prix, c'est une mesure du risque.</p>"),
            ("Le risque de chute",
             "<p>Le site affiche aussi le risque de perdre plus de 10 % en un mois. Il est vérifié en public : les titres jugés les plus à risque chutent "
             "réellement plus souvent que les autres (voir <a href='../resultats.html'>résultats réels</a>).</p>"),
        ],
        retenir=["Le sens du prix est très difficile à prévoir ; l'agitation l'est beaucoup moins.", "Une fourchette mesure l'incertitude, ce n'est pas un objectif.",
                 "Le risque de chute est vérifié en public sur le site."],
        quiz=[("Qu'est-ce qui se prévoit le mieux ?", ["Le sens du prix demain", "L'agitation du prix le mois prochain", "Le prix exact dans un an", "Le gagnant du loto"], 1,
               "L'agitation a une mémoire : c'est ce que les modèles prévoient le mieux."),
              ("Dans la zone claire de la fourchette, le prix finit environ…", ["1 fois sur 10", "1 fois sur 2", "8 fois sur 10", "Toujours"], 2,
               "La zone claire couvre environ 8 cas sur 10 ; 2 fois sur 10, le prix sort de la fourchette."),
              ("Une fourchette très large signifie…", ["Que l'action va monter", "Beaucoup d'incertitude", "Que l'IA est en panne", "Un dividende élevé"], 1, "Plus la fourchette est large, plus l'incertitude est grande."),
              ],
        exercice=("<p>Une action vaut 100 €, l'agitation prévue est de ±12 % sur un mois. Entre quels prix la zone « 8 fois sur 10 » se situe-t-elle à peu près ? "
                  "Et pour une crypto à 100 € avec ±30 % ?</p>",
                  "<p>Action : en gros entre <b>88 € et 112 €</b>. Crypto : entre <b>70 € et 130 €</b>. Même prix de départ, mais un risque bien différent : "
                  "sur la crypto, une perte de 30 % en un mois est un scénario normal, pas exceptionnel. (Le site calcule des bornes un peu asymétriques, car les prix ne peuvent pas devenir négatifs.)</p>"),
        sources=[("Engle (1982), modèle ARCH, prix Nobel 2003", "https://www.nobelprize.org/prizes/economic-sciences/2003/engle/facts/"),
                 ("Radar Bourse : résultats réels", "../resultats.html")],
    ),
    dict(
        id="taux-inflation-banques-centrales", niveau=4, minutes=7,
        titre="Taux, inflation et banques centrales",
        desc="Pourquoi la BCE et la Fed font bouger toute la Bourse.",
        mots="taux d'intérêt bourse, bce fed explication, inflation et bourse, banque centrale débutant",
        sections=[
            ("Le rôle des banques centrales",
             "<p>La <b>BCE</b> (zone euro) et la <b>Fed</b> (États-Unis) fixent leurs taux directeurs pour tenir l'inflation proche de leur objectif, "
             "autour de 2 % par an. Quand l'inflation est trop forte, elles montent leurs taux ; quand l'économie ralentit trop, elles les baissent.</p>"),
            ("L'effet sur les actions",
             "<ul><li>Des taux plus hauts rendent l'épargne sans risque plus attractive et l'emprunt plus cher pour les entreprises : souvent négatif pour les actions.</li>"
             "<li>Les entreprises de croissance (dont les bénéfices sont attendus loin dans le futur) y sont les plus sensibles.</li>"
             "<li>Les banques, elles, profitent parfois de taux plus élevés.</li></ul>"),
            ("Un exemple récent",
             "<p>En 2022, face à une inflation au plus haut depuis des décennies, la Fed et la BCE ont monté leurs taux très vite. "
             "Le Nasdaq a perdu environ un tiers de sa valeur cette année-là, et les obligations ont aussi baissé : une année rare où actions et obligations ont chuté ensemble.</p>"),
            ("Sur Radar Bourse",
             "<p>La section « contexte économique » (mode expert) affiche les taux et l'inflation. Les annonces des banques centrales sont des moments où "
             "l'agitation monte souvent.</p>"),
        ],
        retenir=["Les banques centrales visent environ 2 % d'inflation.", "Taux en hausse = souvent mauvais pour les actions, surtout de croissance.",
                 "2022 : hausse rapide des taux, actions et obligations en baisse ensemble."],
        quiz=[("Quand l'inflation est trop forte, une banque centrale a tendance à…", ["Baisser ses taux", "Monter ses taux", "Fermer la Bourse", "Acheter des cryptos"], 1,
               "Monter les taux rend le crédit plus cher et freine l'inflation."),
              ("Quelles actions sont en général les plus sensibles aux hausses de taux ?", ["Les entreprises de croissance", "Les supermarchés", "Toutes pareil", "Aucune"], 0,
               "Leurs bénéfices sont attendus loin dans le futur : ils « valent » moins quand les taux montent."),
              ("Quel est l'objectif d'inflation de la BCE ?", ["0 %", "Environ 2 %", "10 %", "Pas d'objectif"], 1, "La BCE vise une inflation de 2 % à moyen terme."),
              ],
        exercice=("<p>Un livret sans risque rapporte 1 % ; il passe à 4 % après des hausses de taux. Une action a un rendement du dividende de 3 %. "
                  "Pourquoi certains investisseurs vont-ils vendre cette action ?</p>",
                  "<p>À 1 %, l'action à 3 % de dividende était attractive. À 4 % <b>sans risque</b>, il devient plus intéressant pour certains de vendre l'action "
                  "(risquée) et de placer l'argent sur le livret. Ces ventes font baisser le cours, jusqu'à ce que le rendement de l'action redevienne intéressant.</p>"),
        sources=[("BCE : la politique monétaire", "https://www.ecb.europa.eu/mopo/html/index.fr.html"),
                 ("Banque de France : l'inflation", "https://www.banque-france.fr/fr/a-votre-service/particuliers/connaitre-pratiques-bancaires-assurance/linflation")],
    ),
    dict(
        id="krachs-et-cycles", niveau=4, minutes=7,
        titre="Krachs et cycles : 2000, 2008, 2020",
        desc="Ce que les grandes chutes nous apprennent, avec les vrais chiffres.",
        mots="krach boursier histoire, krach 2008, bulle internet 2000, krach covid 2020, que faire en cas de krach",
        sections=[
            ("2000-2003 : la bulle internet",
             "<p>Les valeurs technologiques montent de façon spectaculaire à la fin des années 1990. Puis la bulle éclate : le Nasdaq perd environ 78 % entre mars 2000 et octobre 2002, "
             "le CAC 40 environ 65 % entre 2000 et 2003.</p>"),
            ("2007-2009 : la crise financière",
             "<p>Les crédits immobiliers à risque aux États-Unis provoquent la faillite de Lehman Brothers (septembre 2008). "
             "Le CAC 40 perd environ 59 % entre son sommet de 2007 et son plus bas de mars 2009.</p>"),
            ("2020 : le krach du Covid",
             "<p>En février-mars 2020, le S&amp;P 500 perd environ 34 % en cinq semaines, l'une des chutes les plus rapides de l'histoire. "
             "Il retrouve son record en août 2020, soutenu par les banques centrales et les plans de relance.</p>"),
            ("Les leçons",
             "<ul><li>Les krachs font partie de la Bourse : ils reviennent, sans prévenir.</li>"
             "<li>Le temps de récupération varie énormément : quelques mois en 2020, plus de vingt ans pour le CAC 40 hors dividendes après 2000.</li>"
             "<li>Vendre en panique au plus bas transforme une perte provisoire en perte définitive.</li>"
             "<li>La diversification (pays, secteurs, types de placements) et l'investissement régulier atténuent les dégâts.</li></ul>"
             "<p>Pour aller plus loin : la page <a href='../krach-boursier.html'>krach boursier</a> et la carte des risques de Radar Bourse.</p>"),
        ],
        retenir=["Krachs majeurs : 2000-2003 (bulle internet), 2007-2009 (crise financière), 2020 (Covid).",
                 "Les chutes peuvent dépasser 50 % et la récupération prendre des années.", "Vendre en panique au plus bas rend la perte définitive."],
        quiz=[("Environ combien le S&P 500 a-t-il perdu lors du krach de 2020 ?", ["5 %", "34 %", "80 %", "100 %"], 1, "Environ 34 % entre le 19 février et le 23 mars 2020."),
              ("Quelle faillite symbolise la crise de 2008 ?", ["Apple", "Lehman Brothers", "LVMH", "Euronext"], 1, "La banque Lehman Brothers a fait faillite le 15 septembre 2008."),
              ("Que faut-il éviter pendant un krach ?", ["Vendre tout en panique au plus bas", "Garder son calme", "Relire ses objectifs", "Vérifier sa diversification"], 0,
               "Vendre au plus bas transforme une baisse temporaire en perte réelle."),
              ],
        exercice=("<p>Un portefeuille de 10 000 € perd 34 %, puis remonte de 50 %. A-t-il retrouvé son niveau ? Et s'il avait été vendu au plus bas ?</p>",
                  "<p>10 000 × 0,66 = <b>6 600 €</b>, puis × 1,5 = <b>9 900 €</b> : presque revenu (il fallait +51,5 %). "
                  "Vendu au plus bas, il serait resté à <b>6 600 €</b> : 3 300 € de différence.</p>"),
        sources=[("Radar Bourse : krach boursier", "../krach-boursier.html"),
                 ("Federal Reserve History : la crise de 2007-2009", "https://www.federalreservehistory.org/essays/great-recession-of-200709")],
    ),
]

COURS_5 = [
    dict(
        id="diversification", niveau=5, minutes=7,
        titre="Diversifier : ne pas mettre tous ses œufs dans le même panier",
        desc="Pays, secteurs, types de placements, corrélation : la seule « astuce gratuite » de la finance.",
        mots="diversification portefeuille, diversifier ses placements, corrélation actions, allocation d'actifs débutant",
        sections=[
            ("Pourquoi ça marche",
             "<p>Si tu possèdes une seule action, une mauvaise nouvelle peut te faire perdre beaucoup. Avec 50 entreprises de secteurs et pays différents, "
             "une faillite ne pèse plus que 2 %. Le prix Nobel Harry Markowitz l'a formalisé en 1952 : combiner des placements qui ne bougent pas pareil "
             "réduit le risque sans forcément réduire le rendement.</p>"),
            ("La corrélation",
             "<p>La <b>corrélation</b> mesure à quel point deux placements bougent ensemble (de −1 à +1). Deux banques françaises sont très corrélées ; "
             "une action et une obligation d'État l'étaient souvent peu. Mais attention : <b>en pleine crise, les corrélations montent</b>, et beaucoup de placements baissent en même temps.</p>"),
            ("Les axes de diversification",
             "<ul><li><b>Géographie</b> : pas seulement la France.</li><li><b>Secteurs</b> : pas seulement la tech.</li>"
             "<li><b>Types de placements</b> : actions, obligations, fonds en euros, liquidités.</li><li><b>Temps</b> : investir régulièrement plutôt qu'en une fois.</li></ul>"),
            ("Sur Radar Bourse",
             "<p>Le <a href='../comparer.html'>comparateur</a> montre si deux titres bougent ensemble, et les pages par <a href='../themes.html'>thème</a> aident à repérer les secteurs que tu as déjà.</p>"),
        ],
        retenir=["Diversifier réduit le risque d'une seule entreprise.", "La corrélation mesure si deux placements bougent ensemble.",
                 "En crise, les corrélations montent.", "Diversifie par pays, secteurs, types de placements et dans le temps."],
        quiz=[("Une corrélation de +0,9 entre deux actions signifie qu'elles…", ["Bougent presque toujours ensemble", "Bougent en sens inverse", "N'ont aucun lien", "Versent le même dividende"], 0,
               "Proche de +1 : elles montent et baissent ensemble."),
              ("Un ETF MSCI World seul est-il parfaitement diversifié ?", ["Oui, totalement", "Non : il est surtout américain, en actions uniquement", "Il n'a aucune action", "Seulement en Europe"], 1,
               "Il est diversifié en entreprises, mais concentré sur les États-Unis et uniquement en actions."),
              ("Qui a formalisé l'intérêt de la diversification en 1952 ?", ["Warren Buffett", "Harry Markowitz", "Elon Musk", "Christine Lagarde"], 1, "Harry Markowitz, avec la théorie moderne du portefeuille (prix Nobel 1990)."),
              ],
        exercice=("<p>Ton portefeuille : 60 % TotalEnergies, 30 % une autre pétrolière, 10 % un ETF monde. Quel est le problème ? Propose une meilleure répartition pour un débutant.</p>",
                  "<p>90 % du portefeuille dépend du <b>même secteur</b> (le pétrole) : une baisse du prix du pétrole toucherait presque tout. "
                  "Une répartition plus diversifiée, par exemple : une large part en ETF monde, une petite part en actions individuelles de secteurs différents, "
                  "et une épargne de précaution à côté. (Exemple pédagogique, pas un conseil personnalisé.)</p>"),
        sources=[("Nobel 1990 : Harry Markowitz", "https://www.nobelprize.org/prizes/economic-sciences/1990/markowitz/facts/"),
                 ("AMF : diversifier ses placements", "https://www.amf-france.org/fr/espace-epargnants/bien-investir")],
    ),
    dict(
        id="construire-son-portefeuille", niveau=5, minutes=8,
        titre="Construire son portefeuille pas à pas",
        desc="Objectifs, horizon, répartition « cœur + satellites », rééquilibrage.",
        mots="construire portefeuille bourse, portefeuille débutant exemple, coeur satellite stratégie, rééquilibrer portefeuille, allocation selon âge",
        sections=[
            ("1. Fixer ses objectifs et son horizon",
             "<p>Pour quoi investis-tu ? Dans combien de temps auras-tu besoin de l'argent ? Un objectif à 2 ans (un permis, un voyage) ne se place pas en actions ; "
             "un objectif à 15 ans peut l'être en grande partie.</p>"),
            ("2. Choisir la part d'actions",
             "<p>La part d'actions dépend de ton horizon et de ta capacité à supporter une baisse. Demande-toi : « si mon portefeuille perdait 40 % pendant un an, est-ce que je tiendrais ? » "
             "Si la réponse est non, réduis la part d'actions.</p>"),
            ("3. Le modèle « cœur et satellites »",
             "<p>Le <b>cœur</b> (par exemple 70 à 90 %) : un ou deux ETF larges et peu chers, que tu gardes longtemps. "
             "Les <b>satellites</b> (le reste) : quelques actions ou thèmes que tu as étudiés. Tes erreurs sur les satellites ne mettent pas tout en danger.</p>"),
            ("4. Rééquilibrer",
             "<p>Une fois par an, regarde si la répartition a dérivé (par exemple les actions sont passées de 70 % à 80 % après une forte hausse). "
             "Rééquilibrer, c'est revenir à ta cible, en vendant un peu de ce qui a monté ou en orientant tes nouveaux versements.</p>"),
            ("5. Écrire ses règles",
             "<p>Note en quelques lignes : ton objectif, ta répartition, ce que tu feras en cas de forte baisse. Les relire pendant une crise évite beaucoup de mauvaises décisions. "
             "Teste tes idées sans risque avec le <a href='../index.html#portefeuille'>portefeuille virtuel</a>.</p>"),
        ],
        retenir=["Horizon court = pas d'actions ; horizon long = actions possibles.", "Choisis la part d'actions selon la baisse que tu peux supporter.",
                 "Cœur (ETF larges) + satellites (choix personnels).", "Rééquilibre une fois par an et écris tes règles."],
        quiz=[("Tu as besoin de ton argent dans 18 mois. Le placer entièrement en actions est…", ["Adapté", "Peu adapté : une baisse peut durer plus longtemps", "Obligatoire", "Sans risque"], 1,
               "Sur 18 mois, une baisse de 30 % est possible et peut ne pas être rattrapée à temps."),
              ("Dans le modèle cœur-satellites, le cœur est en général…", ["Quelques actions risquées", "Des ETF larges et peu chers", "Des cryptos", "Du liquide"], 1, "Le cœur est la partie stable et diversifiée."),
              ("Rééquilibrer, c'est…", ["Tout vendre chaque mois", "Revenir à la répartition cible", "Acheter ce qui monte le plus", "Changer de courtier"], 1, "On ramène le portefeuille à la répartition choisie."),
              ],
        exercice=("<p>Ta cible : 70 % ETF actions, 30 % fonds sans risque. Après un an, tu as 8 400 € en ETF et 2 600 € en fonds sans risque. "
                  "Quelle est ta répartition actuelle ? Que faut-il déplacer pour revenir à la cible ?</p>",
                  "<p>Total : 11 000 €. ETF : 8 400 / 11 000 = <b>76,4 %</b> ; fonds : <b>23,6 %</b>. Cible : 70 % de 11 000 = 7 700 € en ETF, 3 300 € en fonds. "
                  "Il faut déplacer <b>700 €</b> des ETF vers le fonds sans risque (ou orienter les prochains versements vers le fonds).</p>"),
        sources=[("AMF : définir son profil d'investisseur", "https://www.amf-france.org/fr/espace-epargnants/bien-investir")],
    ),
    dict(
        id="fiscalite-2026", niveau=5, minutes=8,
        titre="La fiscalité de la Bourse en 2026",
        desc="Flat tax à 31,4 %, PEA, assurance-vie, moins-values : les règles vérifiées pour 2026.",
        mots="fiscalité bourse 2026, flat tax 31,4 %, impôt plus-value actions, impôt dividendes 2026, fiscalité pea 2026, déclarer ses gains bourse",
        sections=[
            ("Le prélèvement forfaitaire unique (PFU)",
             "<p>Sur un compte-titres, les dividendes et les plus-values sont taxés par défaut au PFU, ou « flat tax ». Depuis le <b>1er janvier 2026</b>, "
             "les prélèvements sociaux sur ces revenus passent de 17,2 % à <b>18,6 %</b> (hausse de la CSG votée dans la loi de financement de la Sécurité sociale pour 2026). "
             "Le PFU total passe donc de 30 % à <b>31,4 %</b> (12,8 % d'impôt sur le revenu + 18,6 %).</p>"
             "<p>Tu peux opter pour le barème progressif de l'impôt si c'est plus avantageux (par exemple si ton taux d'imposition est faible) : l'option vaut alors pour tous tes revenus de capitaux de l'année.</p>"),
            ("Le PEA",
             "<p>Tant que l'argent reste dans le PEA, achats, ventes et dividendes ne sont pas taxés. Au retrait après 5 ans, seuls les prélèvements sociaux s'appliquent sur les gains : "
             "18,6 % pour les gains acquis depuis 2026, l'ancien taux pour les gains plus anciens.</p>"),
            ("L'assurance-vie",
             "<p>Elle n'est pas concernée par la hausse : les prélèvements sociaux restent à 17,2 %. Après 8 ans, un abattement annuel sur les gains retirés s'applique "
             "(4 600 € pour une personne seule, 9 200 € pour un couple) et le taux d'impôt est réduit.</p>"),
            ("Les moins-values",
             "<p>Sur un compte-titres, une perte réalisée (moins-value) peut être déduite des plus-values de la même année ou des <b>10 années suivantes</b>.</p>"),
            ("Déclarer",
             "<p>Ton courtier français t'envoie un <b>IFU</b> (imprimé fiscal unique) au printemps, avec les montants à reporter. "
             "Un compte ouvert à l'étranger doit être déclaré (formulaire 3916). En cas de doute : impots.gouv.fr ou un professionnel.</p>"),
        ],
        retenir=["Compte-titres : PFU de 31,4 % en 2026 (12,8 % + 18,6 %).", "PEA après 5 ans : seulement les prélèvements sociaux.",
                 "Assurance-vie : prélèvements sociaux maintenus à 17,2 %.", "Moins-values reportables 10 ans ; compte à l'étranger à déclarer."],
        quiz=[("Le PFU sur les dividendes d'un compte-titres en 2026 est de…", ["17,2 %", "30 %", "31,4 %", "12,8 %"], 2, "12,8 % + 18,6 % = 31,4 %."),
              ("Les prélèvements sociaux de l'assurance-vie en 2026 sont de…", ["17,2 %", "18,6 %", "31,4 %", "0 %"], 0, "L'assurance-vie est exclue de la hausse : 17,2 %."),
              ("Pendant combien d'années peut-on reporter une moins-value ?", ["1 an", "5 ans", "10 ans", "Jamais"], 2, "Les moins-values sont imputables sur les plus-values des 10 années suivantes."),
              ],
        exercice=("<p>En 2026, sur ton compte-titres : plus-value de 2 000 € sur l'action A, moins-value de 500 € sur l'action B, dividendes de 300 €. "
                  "Combien paies-tu au PFU ?</p>",
                  "<p>Plus-values nettes : 2 000 − 500 = 1 500 €. Total imposable : 1 500 + 300 = <b>1 800 €</b>. PFU : 1 800 × 31,4 % = <b>565,20 €</b>.</p>"),
        sources=[("Service-public : impôt sur les plus-values de valeurs mobilières", "https://www.service-public.fr/particuliers/vosdroits/F21618"),
                 ("Prélèvements sociaux 2026 (18,6 % / 17,2 %)", "https://www.hagnere-patrimoine.fr/guides-patrimoine/comment-payer-moins-impots/csg-crds-prelevements-sociaux-2026"),
                 ("Flat tax 2026 à 31,4 %", "https://www.nbe-avocats.fr/articles/fiscal/flat-tax-2026-taux-applicable-revenus-concernes-option-bareme/")],
    ),
    dict(
        id="psychologie-investisseur", niveau=5, minutes=7,
        titre="La psychologie de l'investisseur",
        desc="FOMO, aversion à la perte, excès de confiance : les biais qui coûtent le plus cher.",
        mots="psychologie bourse, biais cognitifs investissement, fomo bourse, aversion à la perte, erreurs débutant bourse",
        sections=[
            ("Ton pire ennemi, c'est toi",
             "<p>Les études sur les investisseurs particuliers montrent souvent le même résultat : ils gagnent moins que les fonds dans lesquels ils investissent, "
             "parce qu'ils achètent après les hausses et vendent après les baisses. L'économiste Daniel Kahneman (prix Nobel 2002) a décrit beaucoup de ces biais.</p>"),
            ("Les biais à connaître",
             "<ul><li><b>Aversion à la perte</b> : une perte fait environ deux fois plus mal qu'un gain du même montant fait plaisir. On garde alors trop longtemps ses perdants.</li>"
             "<li><b>FOMO</b> (peur de rater) : acheter parce que « tout le monde en parle », souvent près du sommet.</li>"
             "<li><b>Excès de confiance</b> : croire qu'on bat le marché après quelques gains chanceux.</li>"
             "<li><b>Biais de confirmation</b> : ne lire que ce qui confirme son avis.</li>"
             "<li><b>Ancrage</b> : rester accroché au prix d'achat, alors que le marché s'en moque.</li></ul>"),
            ("Des parades simples",
             "<ul><li>Écrire ses règles avant d'investir, et les relire.</li><li>Investir de façon programmée.</li>"
             "<li>Attendre 24 h avant tout achat « coup de cœur ».</li><li>Tenir un journal de ses décisions et de leurs raisons.</li></ul>"),
            ("Un entraînement sans risque",
             "<p>Le <a href='../index.html#prono'>pronostic du jour</a> et l'<a href='../index.html#remonte'>Arène</a> de Radar Bourse te montrent tes réussites… et surtout tes erreurs, "
             "sans perdre un euro. Compare ton taux de réussite à celui de l'IA : c'est une leçon d'humilité très utile.</p>"),
        ],
        retenir=["Les biais font acheter haut et vendre bas.", "Aversion à la perte, FOMO, excès de confiance, confirmation, ancrage.",
                 "Parades : règles écrites, investissement programmé, délai de 24 h, journal."],
        quiz=[("L'aversion à la perte, c'est…", ["Aimer perdre", "Souffrir plus d'une perte que se réjouir d'un gain équivalent", "Éviter la Bourse", "Un type d'ordre"], 1,
               "Une perte pèse psychologiquement environ deux fois plus qu'un gain du même montant."),
              ("Acheter parce que « tout le monde en parle sur les réseaux », c'est souvent…", ["De l'analyse", "Du FOMO", "De la diversification", "Obligatoire"], 1, "La peur de rater pousse à acheter tard, souvent près du sommet."),
              ("Une bonne parade contre les achats impulsifs :", ["Acheter plus vite", "Attendre 24 h avant d'acheter", "Suivre un influenceur", "Utiliser un crédit"], 1, "Le délai laisse retomber l'émotion."),
              ],
        exercice=("<p>Tu as acheté une action à 50 €. Elle vaut 35 €. Tu te dis : « je vendrai quand elle reviendra à 50 € ». Quel biais est en jeu ? Quelle question devrais-tu te poser à la place ?</p>",
                  "<p>C'est l'<b>ancrage</b> (et l'aversion à la perte) : ton prix d'achat ne compte pas pour le marché. La bonne question : "
                  "« <b>si je n'avais pas cette action aujourd'hui, l'achèterais-je à 35 € ?</b> » Si non, la garder n'est pas plus logique que l'acheter.</p>"),
        sources=[("Nobel 2002 : Daniel Kahneman", "https://www.nobelprize.org/prizes/economic-sciences/2002/kahneman/facts/"),
                 ("AMF : les biais comportementaux", "https://www.amf-france.org/fr/espace-epargnants")],
    ),
    dict(
        id="arnaques-et-pieges", niveau=5, minutes=6,
        titre="Arnaques et pièges : se protéger",
        desc="Les signaux d'alerte, les listes noires de l'AMF et les réflexes à avoir.",
        mots="arnaque bourse, arnaque crypto, liste noire amf, faux conseiller investissement, influenceur finance arnaque",
        sections=[
            ("Les signaux d'alerte",
             "<ul><li>Un rendement élevé <b>garanti</b> ou « sans risque ».</li><li>De l'urgence : « offre valable aujourd'hui seulement ».</li>"
             "<li>Un contact non sollicité (appel, message, réseaux sociaux).</li><li>Une demande de virement vers un compte à l'étranger ou en crypto.</li>"
             "<li>Une plateforme introuvable dans les registres officiels.</li><li>Des « coachs » qui montrent leur train de vie plutôt que leurs résultats vérifiables.</li></ul>"),
            ("Les bons réflexes",
             "<ol><li>Vérifier sur les <b>listes noires de l'AMF</b> et le registre REGAFI.</li><li>Ne jamais transmettre ses codes ou documents d'identité à un inconnu.</li>"
             "<li>En cas de doute, appeler <b>AMF Épargne Info Service</b> : 01 53 45 62 00.</li><li>Si tu as été victime : porter plainte et signaler sur la plateforme gouvernementale (cybermalveillance.gouv.fr ou Pharos).</li></ol>"),
            ("Les pièges légaux",
             "<p>Certains produits sont légaux mais très risqués : CFD, options binaires (interdites à la publicité en France), effet de levier. "
             "Selon les avertissements obligatoires des courtiers, une large majorité des comptes de particuliers perdent de l'argent sur les CFD.</p>"),
        ],
        retenir=["Rendement garanti + urgence + contact non sollicité = arnaque probable.", "Vérifie les listes noires de l'AMF et REGAFI.",
                 "AMF Épargne Info Service : 01 53 45 62 00.", "CFD et levier : légaux mais très risqués."],
        quiz=[("Un inconnu te contacte sur Instagram pour un placement crypto « garanti 20 % par mois ». Tu…", ["Investis un peu pour tester", "Ignores et vérifies les listes noires de l'AMF", "Envoies tes papiers", "Partages à tes amis"], 1,
               "Toutes les cases de l'arnaque sont cochées : contact non sollicité, rendement garanti irréaliste."),
              ("Quel numéro permet d'interroger l'AMF ?", ["17", "01 53 45 62 00", "3615 BOURSE", "112"], 1, "AMF Épargne Info Service répond aux épargnants."),
              ("Les CFD sont…", ["Interdits partout", "Légaux mais très risqués pour les particuliers", "Sans risque", "Garantis par l'État"], 1, "La majorité des comptes particuliers y perdent de l'argent."),
              ],
        exercice=("<p>Une publicité dit : « Rejoins mon groupe privé, 3 000 € par mois grâce à mon robot de trading, places limitées ». Liste au moins trois signaux d'alerte.</p>",
                  "<p>1) Un gain élevé et régulier présenté comme certain ; 2) l'urgence (« places limitées ») ; 3) un « robot » miracle invérifiable ; "
                  "4) un groupe privé, donc sans contrôle ; 5) aucune mention d'agrément AMF. À fuir.</p>"),
        sources=[("AMF : listes noires et mises en garde", "https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde"),
                 ("AMF Épargne Info Service", "https://www.amf-france.org/fr/formulaires-et-declarations/contact-epargnant"),
                 ("Cybermalveillance.gouv.fr", "https://www.cybermalveillance.gouv.fr")],
    ),
    dict(
        id="utiliser-ia-intelligemment", niveau=5, minutes=6,
        titre="Utiliser l'IA (et Radar Bourse) intelligemment",
        desc="Probabilités, confiance, vérification : lire un avis d'IA comme un professionnel.",
        mots="ia bourse fiable, prédiction bourse ia, utiliser ia pour investir, intelligence artificielle bourse débutant",
        sections=[
            ("Une IA donne des probabilités, pas des certitudes",
             "<p>Quand Radar Bourse affiche « hausse, 58 chances sur 100 », cela veut dire que dans des cas comparables, le prix a fini plus haut "
             "à peu près 58 fois sur 100. Donc <b>42 fois sur 100, il a fini plus bas</b>. Un avis n'est jamais une promesse.</p>"),
            ("La confiance compte autant que l'avis",
             "<p>Sur des années qu'elle n'avait jamais vues, l'IA du site a eu raison environ 51 % du temps quand sa confiance était faible, 55 % quand elle était moyenne "
             "et 58 % quand elle était forte. C'est mieux que le hasard, mais loin d'être magique. Elle est en revanche bien meilleure pour prévoir l'agitation "
             "(environ 80 % de bonnes réponses pour ses avis sûrs).</p>"),
            ("Comment l'utiliser",
             "<ul><li>Comme un <b>point de départ</b> pour poser des questions, pas comme un ordre d'achat.</li>"
             "<li>Pour mesurer le <b>risque</b> (agitation, risque de chute) avant d'investir.</li>"
             "<li>En vérifiant ses <a href='../avis-surs-verifies.html'>résultats passés</a>, publiés en public, ratés compris.</li></ul>"),
            ("Se méfier des autres « IA de trading »",
             "<p>Un service sérieux montre ses résultats passés, ses erreurs et sa méthode. Un service qui promet des gains sans montrer de résultats vérifiables "
             "ou qui cache ses ratés ne mérite pas ta confiance, qu'il utilise une IA ou non.</p>"),
        ],
        retenir=["Une probabilité de 58 % veut dire 42 % de chances de se tromper.", "La confiance compte autant que l'avis.",
                 "L'IA prévoit bien mieux l'agitation que le sens du prix.", "Un service sérieux publie ses ratés."],
        quiz=[("L'IA annonce « hausse, 60 chances sur 100 ». Dans des cas comparables, le prix a baissé environ…", ["0 fois sur 100", "40 fois sur 100", "60 fois sur 100", "100 fois sur 100"], 1, "100 − 60 = 40."),
              ("Qu'est-ce que l'IA de Radar Bourse prévoit le mieux ?", ["Le sens du prix demain", "L'agitation le mois prochain", "Le cours exact dans un an", "Les dividendes"], 1, "Ses avis sûrs sur l'agitation sont justes environ 80 % du temps."),
              ("Un signe de sérieux pour un service d'IA financière :", ["Il promet des gains", "Il publie ses résultats passés, y compris ses erreurs", "Il a beaucoup d'abonnés", "Il est payant"], 1, "La transparence sur les erreurs est le meilleur indice de sérieux."),
              ],
        exercice=("<p>Ouvre la page <a href='../avis-surs-verifies.html'>avis vérifiés</a>. Sur les avis déjà contrôlés, quel est le taux de réussite ? "
                  "Compare-le avec le taux annoncé sur les années passées.</p>",
                  "<p>Si le taux réel est proche du taux annoncé, l'IA est bien « calibrée » : ce qu'elle dit correspond à ce qui se passe. "
                  "S'il est nettement plus bas, il faut s'en méfier davantage. C'est exactement pour permettre ce contrôle que la page existe.</p>"),
        sources=[("Radar Bourse : avis vérifiés en public", "../avis-surs-verifies.html"),
                 ("Radar Bourse : idées testées et méthode", "../fiche-technique-ia.html")],
    ),
]
