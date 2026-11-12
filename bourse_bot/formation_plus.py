"""Version 77 : l'Académie en plus complet.

Pour chaque chapitre, des encadrés ajoutés sous une mini-leçon précise :
  ("ex", ...)     un exemple concret, avec des chiffres simples
  ("piege", ...)  l'erreur que presque tout le monde fait au début
  ("geste", ...)  le bon réflexe, ce qu'on fait concrètement
  ("savais", ...) un fait utile qui aide à retenir
et des « labos » : de petits simulateurs à manipuler dans la leçon (voir academie_labo.py).

PLUS  = {id_chapitre: [(index_mini_leçon, type, html), ...]}
LABOS = {id_chapitre: [(index_mini_leçon, nom_du_labo[, réglages de départ]), ...]}

Tous les calculs de ce fichier sont revérifiés par bourse_bot/verif_academie.py (lancé à chaque génération du site).
"""

PLUS = {
    # ------------------------------------------------------------------ module 1
    "bourse-c-est-quoi": [
        (0, "ex", "<p>Quand tu lis « l'action vaut 50 € », ça veut dire une seule chose : <b>la dernière fois</b> que quelqu'un en a acheté une, "
                  "il l'a payée 50 €. Ce n'est pas un prix affiché par un magasin, c'est le prix du dernier échange. Dix secondes plus tard, il peut déjà avoir changé.</p>"),
        (2, "savais", "<p>À Paris, la journée commence et se termine par un <b>fixing</b> : à 9 h et à 17 h 35, tous les ordres en attente sont confrontés d'un coup "
                      "pour trouver un prix unique. Entre les deux, les échanges se font en continu.</p>"),
        (3, "piege", "<p>Acheter une action « parce qu'elle monte », sans savoir ce que vend l'entreprise. À ce moment-là, tu n'investis plus : tu paries. "
                     "Une bonne question avant chaque achat : <i>est-ce que je saurais expliquer en deux phrases comment cette entreprise gagne de l'argent ?</i></p>"),
    ],
    "action-obligation-etf-crypto": [
        (0, "ex", "<p>Une boulangerie est découpée en 1 000 parts et tu en achètes 10 : tu possèdes 1 % de la boulangerie. "
                  "Si elle décide de distribuer 20 000 € de bénéfices cette année, chaque part reçoit 20 €, donc toi <b>200 €</b>. "
                  "Une action, c'est exactement ça, avec une entreprise plus grande.</p>"),
        (1, "piege", "<p>Croire qu'une obligation ne peut pas baisser. En 2022, quand les taux ont monté très vite, beaucoup de fonds d'obligations ont perdu plus de 10 % dans l'année. "
                     "Moins risqué qu'une action ne veut pas dire sans risque.</p>"),
        (2, "ex", "<p>Avec une seule part d'un ETF « monde », tu détiens un tout petit morceau de plus de 1 000 entreprises. "
                  "Si l'une d'elles fait faillite, tu ne le remarques presque pas. Si tu n'avais acheté que celle-là, tu aurais tout perdu.</p>"),
    ],
    "pourquoi-un-cours-bouge": [
        (0, "ex", "<p>Une entreprise annonce un bénéfice en hausse de 10 %. Bonne nouvelle ? Pas forcément : si tout le monde attendait +15 %, "
                  "le cours peut baisser le jour même. Le marché ne note pas le résultat, il note <b>l'écart avec ce qu'il attendait</b>.</p>"),
        (1, "savais", "<p>Les professionnels ont un dicton : « acheter la rumeur, vendre la nouvelle ». Quand une bonne nouvelle est attendue depuis des semaines, "
                      "elle est souvent déjà dans le prix le jour où elle tombe.</p>"),
        (2, "geste", "<p>Devant une variation qui t'inquiète, pose-toi une seule question : <i>dans cinq ans, est-ce que ce qui s'est passé aujourd'hui comptera encore ?</i> "
                     "Neuf fois sur dix, la réponse est non.</p>"),
    ],
    "indices-cac40-sp500": [
        (0, "savais", "<p>Le CAC 40 a été lancé avec une valeur de <b>1 000 points</b> au 31 décembre 1987. Les « points » ne sont pas des euros : "
                      "ils servent seulement à comparer le niveau d'aujourd'hui à celui d'hier.</p>"),
        (1, "ex", "<p>Dans un indice, toutes les entreprises ne comptent pas pareil : plus une entreprise est grosse, plus elle pèse. "
                  "Si les trois ou quatre géants du CAC 40 baissent le même jour, l'indice recule même quand la majorité des 40 monte.</p>"),
        (3, "piege", "<p>Comparer un fonds qui inclut les dividendes avec un indice qui ne les inclut pas. Le fonds a l'air meilleur… alors qu'il a juste encaissé des dividendes. "
                     "Compare toujours « dividendes réinvestis » avec « dividendes réinvestis ».</p>"),
    ],
    "rendement-risque": [
        (0, "piege", "<p>Regarder seulement ce qu'un placement a rapporté ces dernières années. Un +80 % en trois ans dit surtout que le placement bouge beaucoup : "
                     "il peut faire le chemin inverse aussi vite.</p>"),
        (1, "ex", "<p>Tu as 10 000 € sur une action dont la volatilité est de 20 % par an. Une année ordinaire, tu peux t'attendre à finir quelque part "
                  "entre 8 000 € et 12 000 €. Et environ une année sur trois, ce sera en dehors de cette zone.</p>"),
    ],
    "interets-composes": [
        (2, "ex", "<p>La règle de 72 marche aussi dans l'autre sens. Avec une inflation de 3 % par an, les prix doublent en 72 / 3 = <b>24 ans</b> : "
                  "un billet de 100 € laissé dans un tiroir n'achètera plus que la moitié de ce qu'il achète aujourd'hui.</p>"),
        (3, "piege", "<p>Oublier les frais dans le calcul. 10 000 € placés 30 ans à 7 % par an donnent environ 76 000 €. Avec 2 % de frais annuels, il ne reste que 5 % par an : "
                     "environ 43 000 €. Les frais ont mangé plus de 40 % du résultat final.</p>"),
    ],
    "cas-cac40-21-ans": [
        (2, "savais", "<p>Un indice change avec le temps : les entreprises qui déclinent en sortent, d'autres y entrent. Plusieurs vedettes du CAC 40 de l'an 2000 "
                      "n'en font plus partie aujourd'hui. Celui qui possédait l'indice entier a été « mis à jour » automatiquement ; celui qui n'avait que deux ou trois vedettes, non.</p>"),
        (3, "piege", "<p>Se dire « ça finit toujours par remonter ». C'est vrai, jusqu'ici, pour un indice large tenu très longtemps. "
                     "Ce n'est pas vrai pour une action seule : une entreprise peut ne jamais revenir à son ancien cours, voire disparaître.</p>"),
    ],
    # ------------------------------------------------------------------ module 2
    "pea-cto-assurance-vie": [
        (1, "geste", "<p>Ce qui compte pour le délai de 5 ans, c'est la <b>date du premier versement</b>. Ouvrir un PEA avec une petite somme, même sans rien acheter tout de suite, "
                     "fait déjà tourner le compteur. Regarde simplement les frais de tenue de compte avant.</p>"),
        (2, "ex", "<p>Sur un compte-titres, tu vends avec 1 000 € de gain. Au taux de 31,4 %, l'impôt est de <b>314 €</b> : il te reste 686 €. "
                  "Le même gain retiré d'un PEA de plus de 5 ans supporte 18,6 % : 186 €, il te reste 814 €.</p>"),
        (4, "piege", "<p>Choisir le placement d'abord et l'enveloppe ensuite. C'est l'inverse : on décide d'abord dans quelle enveloppe on investit, "
                     "puis on regarde ce qu'elle permet d'acheter.</p>"),
    ],
    "choisir-son-courtier": [
        (0, "ex", "<p>Tu achètes pour 100 € d'actions et le courtier prend 1 € : 1 % de ta mise est déjà parti. Il prendra encore 1 € à la revente. "
                  "Ton action doit donc monter d'environ <b>2 %</b> juste pour que tu retrouves ton argent. Sur les petits ordres, les frais fixes pèsent lourd.</p>"),
        (2, "geste", "<p>Deux minutes avant d'ouvrir un compte : tape le nom exact du courtier dans le registre REGAFI. S'il n'y est pas, tu n'ouvres pas. "
                     "Aucune « offre de bienvenue » ne vaut de sauter cette étape.</p>"),
    ],
    "passer-un-ordre": [
        (0, "ex", "<p>Dans le carnet, le meilleur acheteur propose 49,95 € et le meilleur vendeur demande 50,00 €. Ces 5 centimes d'écart s'appellent la <b>fourchette</b>. "
                  "Sur une grande action, elle est minuscule ; sur une petite action peu échangée, elle peut dépasser 1 % du prix : acheter puis revendre tout de suite te coûterait déjà ça.</p>"),
        (1, "ex", "<p>Tu passes un ordre au marché pour 100 actions. Il n'y en a que 30 à vendre à 50,00 €, puis 70 à 50,40 €. "
                  "Ton ordre prend tout : tu paies en moyenne 50,28 €, plus cher que le prix que tu voyais à l'écran. Avec un ordre limité à 50,00 €, tu aurais eu 30 actions, et le reste aurait attendu.</p>"),
        (2, "geste", "<p>Avant de valider, relis quatre choses : le <b>sens</b> (achat ou vente), la <b>quantité</b>, le <b>prix limite</b> et la <b>validité</b> "
                     "(un ordre « jour » s'annule le soir s'il n'est pas exécuté). La plupart des erreurs coûteuses sont des fautes de frappe.</p>"),
    ],
    "etf-debutant": [
        (1, "ex", "<p>Le nom d'un ETF se lit comme une étiquette. Dans « … MSCI World UCITS ETF <b>Acc</b> » : <i>MSCI World</i> est l'indice copié, <i>UCITS</i> signifie qu'il suit les règles européennes, "
                  "<i>Acc</i> (accumulation) qu'il est capitalisant. S'il se termine par <b>Dist</b>, il verse ses dividendes.</p>"),
        (3, "piege", "<p>Empiler les ETF en croyant diversifier. Un ETF monde, un ETF S&amp;P 500 et un ETF Nasdaq contiennent en grande partie les mêmes géants américains : "
                     "tu les achètes trois fois. Un seul ETF large fait souvent mieux le travail que cinq qui se recoupent.</p>"),
    ],
    "investir-regulierement": [
        (0, "ex", "<p>Tes dépenses tournent autour de 1 200 € par mois ? Ton épargne de précaution se situe entre <b>3 600 €</b> (3 mois) et <b>7 200 €</b> (6 mois). "
                  "Plutôt 3 mois si tes revenus sont stables, plutôt 6 s'ils sont irréguliers.</p>"),
        (1, "piege", "<p>Suspendre ses versements quand le marché baisse, « en attendant que ça se calme ». C'est précisément pendant les baisses que tes 100 € achètent le plus de parts. "
                     "Arrêter à ce moment-là, c'est garder les inconvénients de la méthode et jeter son principal avantage.</p>"),
    ],
    "cas-premier-investissement": [
        (1, "piege", "<p>Penser que 50 € par mois, « ça ne sert à rien ». Versés pendant 40 ans avec un rendement régulier de 5 % par an, 50 € par mois donnent environ <b>76 000 €</b>, "
                     "pour 24 000 € réellement versés. Le montant compte moins que la durée. (Un rendement régulier n'existe pas en Bourse : c'est un ordre de grandeur.)</p>"),
        (3, "geste", "<p>La liste de Sami tient sur un ticket de caisse : 1) épargne de précaution, 2) courtier vérifié, 3) une enveloppe, 4) un ETF large, "
                     "5) un versement automatique, 6) trois règles écrites. Rien d'autre n'est nécessaire pour démarrer.</p>"),
    ],
    # ------------------------------------------------------------------ module 3
    "lire-les-comptes": [
        (0, "ex", "<p>Une boulangerie vend pour 200 000 € dans l'année. Farine, salaires, loyer, électricité et impôts lui coûtent 170 000 €. "
                  "Il lui reste <b>30 000 €</b> : c'est son résultat net, soit 15 % de ses ventes. Les comptes d'un groupe du CAC 40 racontent la même histoire, avec plus de lignes.</p>"),
        (1, "piege", "<p>Se réjouir d'un chiffre d'affaires record sans regarder plus bas. Une entreprise peut vendre de plus en plus tout en perdant de l'argent sur chaque vente. "
                     "Les ventes disent si l'entreprise grandit ; la marge dit si elle gagne sa vie.</p>"),
    ],
    "ratios-per-rendement": [
        (0, "savais", "<p>Retourne le PER et tu obtiens un rendement : un PER de 20 signifie que l'entreprise gagne chaque année 1 / 20 = <b>5 %</b> du prix que tu paies. "
                      "C'est une façon simple de le comparer à ce que rapporte un placement sans risque.</p>"),
        (1, "ex", "<p>Une action verse 2 € de dividende et cote 50 € : rendement de 4 %. Son cours s'effondre à 25 € : le rendement affiché passe à <b>8 %</b>. "
                  "Rien n'a été amélioré, au contraire : le marché pense que ces 2 € ne seront plus versés longtemps.</p>"),
    ],
    "dividendes": [
        (1, "ex", "<p>Détachement le mardi 12, paiement le jeudi 14. Si tu achètes le lundi 11, tu touches le dividende. Si tu achètes le mardi 12, tu ne le touches pas… "
                  "mais tu paies l'action moins cher, du montant du dividende à peu près. Dans les deux cas, tu n'as rien gagné ni perdu.</p>"),
        (2, "piege", "<p>Acheter la veille du détachement pour « encaisser le dividende » et revendre le lendemain. Le cours baisse du montant versé, tu paies deux fois des frais de courtage, "
                     "et sur un compte-titres le dividende est imposé. Le résultat est presque toujours négatif.</p>"),
    ],
    "publications-et-actualite": [
        (1, "ex", "<p>Une entreprise publie des ventes 2 % au-dessus du consensus : bravo. Dans le même communiqué, elle abaisse ses prévisions pour l'an prochain. "
                  "Le cours perd 8 % dans la matinée. Ce que le marché achète, c'est toujours la suite de l'histoire.</p>"),
        (3, "geste", "<p>Une règle simple : aucune décision le jour d'une publication. Lis le communiqué le soir, relis-le le lendemain, et décide ensuite. "
                     "Ceux qui réagissent dans la minute sont des machines ; tu ne gagneras pas cette course, et tu n'en as pas besoin.</p>"),
    ],
    "cas-analyser-une-entreprise": [
        (2, "savais", "<p>Avec 10 millions d'actions à 45 €, Atelier Lumen « vaut » 450 millions d'euros en Bourse : c'est sa <b>capitalisation</b>. "
                      "C'est elle qu'il faut comparer d'une entreprise à l'autre, jamais le prix d'une action seule : une action à 5 € n'est pas moins chère qu'une action à 500 €.</p>"),
        (3, "piege", "<p>Tomber amoureux d'une entreprise après l'avoir étudiée. Plus on a passé de temps sur un dossier, plus on a du mal à admettre qu'il se dégrade. "
                     "Note à l'avance ce qui te ferait changer d'avis (une marge qui chute, une dette qui double), et tiens-t'y.</p>"),
    ],
    # ------------------------------------------------------------------ module 4
    "bougies-tendances": [
        (2, "ex", "<p>Les chiffres ronds servent souvent de repères : 10 €, 50 €, 100 €. Beaucoup d'investisseurs y placent leurs ordres, "
                  "alors le prix y bute plus souvent qu'ailleurs. Rien de magique : c'est seulement l'endroit où les ordres s'accumulent.</p>"),
        (3, "piege", "<p>Voir des figures partout. Le cerveau humain adore reconnaître des formes, même dans le hasard : montre un graphique tiré au sort à dix personnes, "
                     "plusieurs y verront une « tendance claire ». L'Arène de Radar Bourse permet de tester honnêtement ton œil.</p>"),
    ],
    "moyennes-rsi-macd": [
        (0, "savais", "<p>Quand la moyenne à 50 jours passe au-dessus de celle à 200 jours, on parle de « croix dorée » ; l'inverse s'appelle la « croix de la mort ». "
                      "Les noms impressionnent plus que les résultats : ces signaux arrivent tard, souvent quand une bonne partie du mouvement est déjà faite.</p>"),
        (1, "piege", "<p>Vendre dès que le RSI dépasse 70. Dans une vraie tendance haussière, il peut rester au-dessus de 70 pendant des semaines pendant que le cours continue de grimper. "
                     "Le RSI dit « ça a monté vite », pas « ça va baisser ».</p>"),
    ],
    "volatilite-et-ia": [
        (0, "ex", "<p>C'est comme la météo en mer. Personne ne sait s'il pleuvra un mardi précis dans trois semaines. Mais tout marin sait que novembre est plus agité qu'août. "
                  "Le sens du prix, c'est le mardi précis ; l'agitation, c'est la saison.</p>"),
        (1, "ex", "<p>Une action cote 100 €. Zone foncée : 96 à 104 €. Zone claire : 90 à 110 €. Lecture : dans un mois, le prix a environ une chance sur deux de finir entre 96 et 104, "
                  "et environ deux chances sur dix de finir <b>en dehors</b> de 90 à 110. Ça arrive donc régulièrement.</p>"),
    ],
    "taux-inflation-banques-centrales": [
        (0, "savais", "<p>La BCE siège à Francfort et annonce ses décisions environ toutes les six semaines, huit fois par an. "
                      "Ces dates sont connues longtemps à l'avance : ce sont des jours où les marchés retiennent leur souffle.</p>"),
        (1, "ex", "<p>Pourquoi les taux pèsent sur les actions de croissance ? Parce qu'un euro promis dans dix ans vaut moins aujourd'hui quand les taux sont hauts. "
                  "Avec des taux à 2 %, cet euro futur vaut environ 0,82 € aujourd'hui ; à 5 %, seulement 0,61 €. Plus les bénéfices attendus sont lointains, plus l'effet est fort.</p>"),
    ],
    "krachs-et-cycles": [
        (2, "ex", "<p>Après une chute de 34 %, il faut une hausse d'environ <b>52 %</b> pour revenir au point de départ (100 → 66 → 100). "
                  "En 2020, cette remontée a pris cinq mois. Après 2000, la même arithmétique a demandé des années : la vitesse du retour, personne ne la connaît à l'avance.</p>"),
        (3, "piege", "<p>Attendre le prochain krach pour commencer à investir. Il peut arriver dans six mois ou dans huit ans, et pendant ce temps le marché peut avoir monté "
                     "bien plus que ce que le krach fera perdre. Investir un peu chaque mois évite d'avoir à deviner.</p>"),
    ],
    "cas-gamestop-2021": [
        (0, "ex", "<p>La vente à découvert en chiffres : tu empruntes une action et tu la vends 20 $. Si elle tombe à 5 $, tu la rachètes, tu la rends, et tu gagnes 15 $. "
                  "Mais si elle monte à 100 $, tu dois quand même la racheter : tu perds 80 $. Le gain est limité (l'action ne descend pas sous zéro), la perte ne l'est pas.</p>"),
        (3, "geste", "<p>Quand une action fait la une et que tes amis en parlent, pose-toi la question : <i>qui me vendrait cette action aujourd'hui, et pourquoi ?</i> "
                     "Très souvent, c'est quelqu'un qui l'a achetée bien avant et qui est ravi de trouver preneur.</p>"),
    ],
    # ------------------------------------------------------------------ module 5
    "diversification": [
        (1, "piege", "<p>La fausse diversification : vingt actions… toutes françaises, ou toutes dans la technologie. Le nombre de lignes ne compte pas, "
                     "c'est le nombre de <b>moteurs différents</b> qui compte. Vingt valeurs qui montent et baissent ensemble se comportent comme une seule.</p>"),
        (2, "ex", "<p>Un portefeuille à 100 % en actions françaises dépend d'un seul pays, qui pèse environ 3 % de la Bourse mondiale. "
                  "Le même montant dans un ETF monde est réparti sur une vingtaine de pays et tous les secteurs, sans effort supplémentaire.</p>"),
    ],
    "construire-son-portefeuille": [
        (1, "ex", "<p>Tu as 10 000 € répartis en 80 % d'actions et 20 % de placements prudents. Les actions perdent 40 % : ton portefeuille recule de 0,8 × 40 = <b>32 %</b>, "
                  "soit 3 200 €. Fais ce calcul avec <i>ta</i> répartition avant d'investir : c'est le montant que tu dois être capable de regarder sans vendre.</p>"),
        (3, "ex", "<p>Cible : 70 % d'actions. Tu pars avec 7 000 € d'actions et 3 000 € de prudent. Les actions gagnent 30 % : 9 100 € et 3 000 €, soit 75 % d'actions. "
                  "Pour revenir à 70 %, il faudrait environ 8 470 € d'actions : tu en vends 630 €, ou tu diriges tes prochains versements vers la partie prudente.</p>"),
    ],
    "fiscalite-2026": [
        (0, "ex", "<p>Tu reçois 500 € de dividendes sur un compte-titres. Le courtier prélève 31,4 %, soit <b>157 €</b>, et te verse 343 €. "
                  "Tu n'as rien à calculer toi-même : le montant est reporté sur ta déclaration de revenus, déjà rempli.</p>"),
        (3, "ex", "<p>Dans l'année, tu gagnes 1 000 € sur une vente et tu perds 400 € sur une autre. Tu es imposé sur la différence, 600 € : "
                  "600 × 31,4 % = <b>188,40 €</b>. Sans la moins-value, l'impôt aurait été de 314 €.</p>"),
        (4, "savais", "<p>Les règles fiscales se décident chaque automne, dans le budget de l'année suivante. Ce chapitre décrit ce qui s'applique en 2026 ; "
                      "le budget 2027 est encore en discussion au Parlement à la date de relecture. Avant une décision importante, vérifie toujours sur impots.gouv.fr.</p>"),
    ],
    "psychologie-investisseur": [
        (1, "ex", "<p>On te propose un pile ou face : pile, tu gagnes 110 € ; face, tu perds 100 €. Le jeu est à ton avantage, et pourtant la plupart des gens refusent. "
                  "C'est l'aversion à la perte à l'œuvre : la peur de perdre 100 € pèse plus lourd que l'envie d'en gagner 110.</p>"),
        (2, "geste", "<p>Avant chaque achat, écris une phrase : « J'achète X parce que…, et je revendrai si… ». Dans six mois, relis-la. "
                     "C'est le moyen le plus simple de savoir si tu as eu raison pour les bonnes raisons, ou seulement de la chance.</p>"),
    ],
    "arnaques-et-pieges": [
        (0, "ex", "<p>« 1 % par jour, garanti. » Fais le calcul : 1 % par jour pendant un an multiplie la mise par environ <b>38</b>. "
                  "Avec 1 000 €, tu aurais 38 000 € en un an et plus d'un million au bout de deux. Si ça existait, personne n'aurait besoin de te le vendre.</p>"),
        (1, "geste", "<p>Trois vérifications, cinq minutes : le nom sur la liste noire de l'AMF, le nom sur REGAFI, et une recherche « nom + arnaque ». "
                     "Et une règle sans exception : on ne décide jamais pendant l'appel. Un vrai professionnel te laisse le temps de réfléchir.</p>"),
    ],
    "utiliser-ia-intelligemment": [
        (0, "ex", "<p>Imagine une pièce truquée qui tombe sur pile 58 fois sur 100. Sur dix lancers, tu peux très bien voir sortir six faces : cela arrive plus d'une fois sur dix. "
                  "Une probabilité se vérifie sur des centaines de cas, jamais sur un seul avis.</p>"),
        (3, "piege", "<p>Se fier à une courbe de résultats « sur le passé ». N'importe quelle méthode peut être réglée après coup pour avoir l'air géniale sur des années déjà connues. "
                     "Seuls comptent les résultats annoncés <b>avant</b> et vérifiés <b>après</b>, comme la page des résultats réels du site.</p>"),
    ],
    "cas-portefeuille-lea": [
        (1, "ex", "<p>Chaque mois, les 300 € de Léa se répartissent ainsi : <b>210 €</b> sur l'ETF monde dans son PEA (70 %), <b>30 €</b> sur ses satellites (10 %) "
                  "et <b>60 €</b> sur le fonds en euros de son assurance-vie (20 %). Une fois les virements programmés, elle n'a plus rien à faire.</p>"),
        (3, "geste", "<p>Écris tes règles un jour où tout va bien, pas pendant une baisse. On réfléchit mal quand on a peur : les règles servent justement à décider à ta place ce jour-là.</p>"),
    ],
    # ------------------------------------------------------------------ module 6
    "blockchain-bitcoin": [
        (0, "ex", "<p>Imagine un cahier de comptes dont chaque élève de la classe possède une copie. Si quelqu'un modifie une ligne dans son cahier, "
                  "les trente autres copies le contredisent aussitôt. Une blockchain fonctionne ainsi, avec des milliers d'ordinateurs à la place des élèves.</p>"),
        (2, "savais", "<p>La récompense des mineurs était de 50 bitcoins par bloc en 2009. Elle est passée à 25 en 2012, 12,5 en 2016, 6,25 en 2020 et <b>3,125</b> en 2024. "
                      "À ce rythme, les derniers bitcoins seront créés vers 2140.</p>"),
    ],
    "altcoins-stablecoins": [
        (1, "ex", "<p>Un stablecoin sérieux garde en réserve un dollar (ou des bons du Trésor) pour chaque jeton émis. TerraUSD, lui, tenait son prix grâce à un mécanisme automatique lié à une autre crypto. "
                  "Quand la confiance a cédé, en mai 2022, il n'y avait rien derrière : des dizaines de milliards de dollars ont disparu en quelques jours.</p>"),
        (2, "piege", "<p>« Il ne coûte que 0,00001 €, il peut facilement faire ×1 000. » Le prix d'un jeton ne dit rien : il faut le multiplier par le nombre de jetons en circulation. "
                     "Une crypto à 0,00001 € peut déjà « valoir » plusieurs milliards au total, et ×1 000 la rendrait plus grosse que le bitcoin.</p>"),
    ],
    "acheter-conserver-crypto": [
        (2, "ex", "<p>L'arnaque la plus courante : un faux « support technique » te contacte après un message que tu as posté, et te demande ta phrase de récupération "
                  "« pour resynchroniser ton portefeuille ». À la seconde où tu la donnes, tes cryptos sont parties, et personne ne peut annuler.</p>"),
        (3, "geste", "<p>Avant tout gros transfert : envoie d'abord l'équivalent de quelques euros, attends qu'ils arrivent, puis envoie le reste. "
                     "Ça coûte un peu de frais en plus, et ça évite l'erreur qui ne se rattrape pas.</p>"),
    ],
    "fiscalite-crypto-2026": [
        (0, "ex", "<p>Tu échanges du bitcoin contre de l'ether : rien à payer pour l'instant. Trois mois plus tard, tu vends cet ether contre des euros : "
                  "c'est cette vente qui déclenche l'impôt, calculé sur le gain de l'ensemble de ton portefeuille crypto.</p>"),
        (2, "ex", "<p>Tu vends pour 300 € de cryptos dans l'année : rien à payer, quelle que soit ta plus-value. "
                  "Tu vends pour 400 € avec 50 € de gain : le seuil est dépassé, et l'impôt porte sur les 50 €, soit 50 × 31,4 % = <b>15,70 €</b>.</p>"),
    ],
    "cas-ftx-2022": [
        (0, "savais", "<p>Début 2022, FTX était valorisée 32 milliards de dollars, sponsorisait un stade et s'offrait des publicités pendant le Super Bowl. "
                      "La notoriété d'une plateforme ne dit rien de sa solidité.</p>"),
        (3, "geste", "<p>Pose-toi la question pour chaque plateforme : « si elle fermait demain matin, qu'est-ce que je perdrais ? » "
                     "Si la réponse te fait peur, c'est qu'il y a trop d'argent au même endroit.</p>"),
    ],
    # ------------------------------------------------------------------ module 7
    "obligations-en-detail": [
        (0, "savais", "<p>Quand l'État français emprunte, il émet des obligations appelées <b>OAT</b> (obligations assimilables du Trésor). "
                      "Le « taux à 10 ans de la France » dont parlent les journaux, c'est le rendement de l'OAT à 10 ans.</p>"),
        (3, "ex", "<p>Si un État bien noté emprunte à 3 % et qu'une entreprise fragile doit offrir 8 % pour la même durée, l'écart de 5 points s'appelle la <b>prime de risque</b> "
                  "(ou « spread »). C'est le prix que le marché demande pour accepter le risque de ne pas être remboursé.</p>"),
    ],
    "devises-risque-de-change": [
        (0, "ex", "<p>Tu achètes pour 1 000 $ d'actions quand 1 € vaut 1,10 $ : cela te coûte 909 €. L'action ne bouge pas, mais l'euro monte à 1,20 $. "
                  "Tes 1 000 $ ne valent plus que 833 € : tu as perdu environ <b>8 %</b> sans que l'entreprise y soit pour rien.</p>"),
        (3, "piege", "<p>Croire qu'un ETF coté en euros te protège du dollar. La devise de cotation n'est qu'un affichage : si l'ETF contient des actions américaines, "
                     "tu portes le risque du dollar, sauf s'il est explicitement « couvert » (hedged).</p>"),
    ],
    "secteurs-cycliques-defensifs": [
        (0, "ex", "<p>En récession, une famille repousse l'achat d'une voiture neuve : les ventes du constructeur plongent. Elle continue en revanche d'acheter du dentifrice et de payer l'électricité. "
                  "Voilà toute la différence entre une valeur cyclique et une valeur défensive.</p>"),
        (3, "piege", "<p>Acheter le secteur qui a le plus monté l'an dernier. C'est souvent celui dont tout le monde parle… et celui qui est devenu cher. "
                     "Les secteurs vedettes d'une décennie sont rarement ceux de la suivante.</p>"),
    ],
    "ipo-rachats-divisions": [
        (2, "ex", "<p>Tu possèdes 2 actions à 300 €, soit 600 €. Après une division par 3, tu as 6 actions à 100 € : toujours 600 €. "
                  "C'est une pizza coupée en six parts au lieu de deux : il n'y a pas plus de pizza.</p>"),
        (3, "ex", "<p>Tu détiens 100 actions d'une entreprise qui en compte 1 000 : 10 % du capital. Elle crée 250 actions nouvelles et tu n'en achètes pas. "
                  "Tu as toujours 100 actions, mais sur 1 250 : ta part tombe à <b>8 %</b>. C'est la dilution.</p>"),
    ],
    "levier-options-cfd": [
        (1, "ex", "<p>Tu paies 2 € une option d'achat à 50 €. Si l'action monte à 60 €, ton option vaut 10 € : tu as gagné 8 € pour 2 € misés. "
                  "Si l'action finit à 49 €, l'option ne vaut plus rien : tu as perdu <b>100 %</b> de ta mise, alors que l'action n'a presque pas bougé.</p>"),
        (3, "geste", "<p>Un test simple avant tout produit à levier : es-tu capable d'expliquer, par écrit, dans quel cas précis tu perds toute ta mise ? "
                     "Si tu ne le sais pas, tu n'es pas prêt, et ce n'est pas grave.</p>"),
    ],
    "lire-un-dic": [
        (1, "piege", "<p>Lire l'indicateur de risque comme une note sur 7. Un ETF actions classé 4 peut tout à fait perdre 30 % ou 40 % lors d'un krach. "
                     "L'échelle compare les produits entre eux ; elle ne promet pas de plafond de perte.</p>"),
        (0, "geste", "<p>Le DIC se trouve en tapant le <b>code ISIN</b> du fonds (12 caractères, par exemple FR… ou IE…) suivi de « DIC » ou « KID » dans un moteur de recherche, "
                     "ou sur la fiche du produit chez ton courtier. Trois minutes de lecture avant chaque premier achat.</p>"),
    ],
    "cas-decortiquer-une-pub": [
        (1, "ex", "<p>« 300 € par jour » sur les quelque 250 jours de Bourse d'une année, cela ferait <b>75 000 €</b> par an, sans effort, depuis un canapé. "
                  "Quelqu'un qui saurait vraiment faire ça ne chercherait pas des abonnés à 49 € par mois.</p>"),
        (3, "geste", "<p>Face à une publicité de ce genre, ne réponds pas, ne clique pas, et signale-la : à l'AMF (Épargne Info Service) et sur le réseau social concerné. "
                     "Chaque signalement protège la personne suivante.</p>"),
    ],
}

# Les simulateurs intégrés aux leçons : (index de la mini-leçon, nom du labo dans academie_labo.LABOS)
LABOS = {
    "bourse-c-est-quoi": [(0, "offre")],
    "rendement-risque": [(2, "pertes")],
    "interets-composes": [(1, "composes")],
    "choisir-son-courtier": [(1, "frais")],
    "investir-regulierement": [(2, "dca")],
    "ratios-per-rendement": [(0, "per")],
    "diversification": [(0, "diversif")],
    "fiscalite-2026": [(1, "fiscal")],
    "obligations-en-detail": [(1, "obligation")],
    "devises-risque-de-change": [(1, "change")],
    "levier-options-cfd": [(0, "levier")],
    "lire-un-dic": [(3, "frais")],
    "cas-decortiquer-une-pub": [(2, "levier", {"l": 100, "v": -1})],
}

TITRES = {"ex": "Exemple concret", "piege": "L'erreur classique", "geste": "Le bon réflexe", "savais": "Bon à savoir"}

# Parcours par objectif (version 77) : des raccourcis dans le programme pour qui sait déjà ce qu'il cherche.
OBJECTIFS = [
    ("Je pars de zéro", "L'essentiel pour comprendre, puis faire un premier pas sans se tromper.",
     ["bourse-c-est-quoi", "action-obligation-etf-crypto", "rendement-risque", "interets-composes", "pea-cto-assurance-vie", "etf-debutant", "investir-regulierement", "plan-d-action"]),
    ("Je veux ouvrir un PEA et acheter mon premier ETF", "L'enveloppe, le courtier, l'ordre, le choix du fonds et les impôts.",
     ["pea-cto-assurance-vie", "choisir-son-courtier", "passer-un-ordre", "etf-debutant", "lire-un-dic", "fiscalite-2026"]),
    ("Je veux apprendre à analyser une action", "Lire les comptes, les ratios, l'actualité et le graphique.",
     ["lire-les-comptes", "ratios-per-rendement", "dividendes", "publications-et-actualite", "bougies-tendances", "secteurs-cycliques-defensifs"]),
    ("Je m'intéresse à la crypto", "Comment ça marche, comment en acheter sans se faire piéger, et comment la déclarer.",
     ["action-obligation-etf-crypto", "blockchain-bitcoin", "altcoins-stablecoins", "acheter-conserver-crypto", "fiscalite-crypto-2026", "arnaques-et-pieges"]),
    ("Je veux éviter les pièges", "Le risque, les biais, les arnaques, le levier et les promesses des « IA de trading ».",
     ["rendement-risque", "psychologie-investisseur", "arnaques-et-pieges", "levier-options-cfd", "utiliser-ia-intelligemment", "lire-un-dic"]),
]

# À la fin d'un chapitre : où mettre en pratique sur le site, tout de suite (texte, page du site).
PRATIQUE = {
    "bourse-c-est-quoi": ("Regarde un vrai marché en direct : la carte du marché sur la page des pronos.", "index.html"),
    "action-obligation-etf-crypto": ("Compare une action et une crypto côte à côte : agitation, risque de chute, performances.", "comparer.html"),
    "pourquoi-un-cours-bouge": ("Repère les prochaines publications de résultats, ces jours où les cours bougent le plus.", "calendrier-resultats.html"),
    "indices-cac40-sp500": ("Vois comment se portent les grands indices cette semaine.", "bourse-cette-semaine.html"),
    "rendement-risque": ("Regarde quels titres l'IA juge les plus risqués en ce moment, et si elle a eu raison le mois dernier.", "suivi-chute.html"),
    "interets-composes": ("Refais le calcul avec tes propres chiffres dans le calculateur d'intérêts composés.", "outils.html"),
    "cas-cac40-21-ans": ("Teste « Si j'avais investi… » sur le CAC 40 ou sur une action, avec les vrais cours.", "outils.html"),
    "choisir-son-courtier": ("Dans le calculateur d'intérêts composés, baisse le taux d'un point pour voir ce que 1 % de frais retire sur 20 ou 30 ans.", "outils.html"),
    "passer-un-ordre": ("Passe tes premiers ordres avec 10 000 € fictifs, sans rien risquer.", "simulateur-boursier.html"),
    "investir-regulierement": ("Compare « tout d'un coup » et « chaque mois » sur les vrais cours d'un titre.", "outils.html"),
    "cas-premier-investissement": ("Entraîne-toi avec le portefeuille virtuel avant de passer au réel.", "simulateur-boursier.html"),
    "ratios-per-rendement": ("Trie les titres par PER ou par dividende dans le tableau des pronos.", "index.html"),
    "publications-et-actualite": ("Le calendrier des résultats te dit quelles entreprises publient bientôt.", "calendrier-resultats.html"),
    "bougies-tendances": ("Teste ton œil dans l'Arène : un vrai graphique, tu devines la suite, contre l'IA.", "index.html"),
    "volatilite-et-ia": ("Vérifie par toi-même : les avis sûrs de l'IA, contrôlés en public un mois plus tard.", "avis-surs-verifies.html"),
    "krachs-et-cycles": ("Regarde où en est le risque de krach aujourd'hui, mesuré par le radar.", "krach-boursier.html"),
    "diversification": ("Vérifie si deux de tes titres bougent ensemble avec le comparateur.", "comparer.html"),
    "construire-son-portefeuille": ("Construis ta répartition dans le portefeuille virtuel et suis-la sur quelques semaines.", "simulateur-boursier.html"),
    "fiscalite-2026": ("Calcule l'impôt sur une plus-value avec le calculateur de flat tax.", "outils.html"),
    "psychologie-investisseur": ("Fais ton pronostic du jour, puis compare ton taux de réussite à celui de l'IA.", "index.html"),
    "utiliser-ia-intelligemment": ("Lis la fiche technique de l'IA : ce qu'elle sait faire, ce qu'elle rate, chiffres à l'appui.", "fiche-technique-ia.html"),
    "secteurs-cycliques-defensifs": ("Parcours les actions par thème et compare l'agitation des secteurs.", "themes.html"),
    "plan-d-action": ("Dernière étape avant le réel : un mois de portefeuille virtuel avec ton plan.", "simulateur-boursier.html"),
}
