"""Version 70 : l'Académie Radar Bourse — niveaux 1 et 2 (les bases, passer à l'action).

Chaque chapitre : dict(id, niveau, titre, desc, minutes, mots, sections=[(titre, html)], retenir=[...],
quiz=[(question, [choix], index_bonne, explication)], exercice=(énoncé_html, correction_html), sources=[(nom, url)]).
Les chiffres réglementaires ont été vérifiés le 11/11/2026 (AMF, service-public, textes de loi repris par la presse spécialisée).
"""

COURS_1 = [
    dict(
        id="bourse-c-est-quoi", niveau=1, minutes=6,
        titre="La Bourse, c'est quoi ?",
        desc="Ce qui se passe vraiment quand on « achète en Bourse », expliqué depuis zéro.",
        mots="bourse pour débutant, c'est quoi la bourse, comment fonctionne la bourse, apprendre la bourse, bourse expliquée simplement",
        sections=[
            ("Un marché comme un autre… ou presque",
             "<p>La Bourse est un <b>marché</b> où des acheteurs et des vendeurs s'échangent des titres financiers : des morceaux d'entreprises "
             "(les <b>actions</b>), des prêts faits à des entreprises ou à des États (les <b>obligations</b>), ou des paniers de titres (les <b>ETF</b>).</p>"
             "<p>Comme sur un marché de fruits et légumes, le prix monte quand il y a plus d'acheteurs que de vendeurs, et baisse dans le cas inverse. "
             "La différence : tout se passe sur ordinateur, en quelques millièmes de seconde, et des millions de personnes y participent en même temps.</p>"),
            ("Qui fait quoi ?",
             "<ul><li><b>Les entreprises</b> entrent en Bourse pour lever de l'argent : elles vendent une partie de leur capital au public.</li>"
             "<li><b>Les investisseurs</b> (toi, des banques, des fonds de retraite…) achètent et revendent ces titres.</li>"
             "<li><b>Les courtiers</b> (banques, applis de Bourse) transmettent tes ordres au marché. Tu ne peux pas acheter directement : tu passes toujours par eux.</li>"
             "<li><b>L'entreprise de marché</b> organise les échanges. À Paris, c'est <b>Euronext</b>.</li>"
             "<li><b>Le gendarme</b> surveille que tout le monde respecte les règles. En France, c'est l'<b>AMF</b> (Autorité des marchés financiers).</li></ul>"),
            ("Quand est-ce ouvert ?",
             "<p>Euronext Paris fonctionne en continu du lundi au vendredi, de <b>9 h à 17 h 30</b> (heure de Paris), hors jours fériés de Bourse. "
             "Wall Street (New York) ouvre de 9 h 30 à 16 h heure locale, soit en général de <b>15 h 30 à 22 h</b> à Paris. "
             "Les cryptomonnaies, elles, s'échangent 24 h sur 24, 7 jours sur 7.</p>"),
            ("Ce que la Bourse n'est pas",
             "<p>Ce n'est pas un casino : quand tu achètes une action, tu deviens copropriétaire d'une vraie entreprise qui fait (ou non) des bénéfices. "
             "Mais ce n'est pas non plus un livret d'épargne : <b>la valeur peut baisser</b>, parfois beaucoup, et rien n'est garanti.</p>"),
        ],
        retenir=["La Bourse est un marché où s'échangent actions, obligations et ETF.",
                 "Le prix bouge selon l'équilibre entre acheteurs et vendeurs.",
                 "On passe toujours par un courtier ; à Paris, le marché s'appelle Euronext et le gendarme l'AMF.",
                 "Euronext Paris est ouvert de 9 h à 17 h 30 en semaine."],
        quiz=[("Que se passe-t-il quand il y a plus d'acheteurs que de vendeurs sur une action ?",
               ["Le prix baisse", "Le prix monte", "Le prix ne change pas", "La cotation s'arrête"], 1,
               "Les acheteurs doivent proposer un prix plus élevé pour convaincre les vendeurs : le cours monte."),
              ("Qui surveille les marchés financiers en France ?",
               ["La Banque de France", "Euronext", "L'AMF", "Le ministère du Travail"], 2,
               "L'Autorité des marchés financiers (AMF) est le gendarme de la Bourse : elle protège les épargnants et sanctionne les fraudes."),
              ("À quelle heure ferme la Bourse de Paris en semaine ?",
               ["12 h", "17 h 30", "20 h", "Elle ne ferme jamais"], 1,
               "La cotation en continu d'Euronext Paris se termine à 17 h 30 (avec un fixing de clôture juste avant)."),
              ],
        exercice=("<p>Une action vaut 20 €. Le matin, 1 000 personnes veulent l'acheter à 20 €, mais seulement 200 veulent la vendre à ce prix. "
                  "Que va-t-il probablement se passer sur le prix pendant la journée ? Explique avec tes mots.</p>",
                  "<p>Il y a 5 fois plus d'acheteurs que de vendeurs au prix de 20 €. Pour obtenir l'action, certains acheteurs vont accepter "
                  "de payer 20,10 €, puis 20,20 €… Le prix <b>monte</b> jusqu'à ce que suffisamment de vendeurs soient d'accord pour vendre, "
                  "et qu'acheteurs et vendeurs s'équilibrent.</p>"),
        sources=[("AMF : comprendre les marchés", "https://www.amf-france.org/fr/espace-epargnants"),
                 ("Euronext : horaires de négociation", "https://www.euronext.com/fr/trading-calendars-hours")],
    ),
    dict(
        id="action-obligation-etf-crypto", niveau=1, minutes=7,
        titre="Action, obligation, ETF, crypto : les différences",
        desc="Les quatre grandes familles de placements, ce qu'elles rapportent et ce qu'elles risquent.",
        mots="différence action obligation, c'est quoi un etf, action ou etf débutant, crypto vs action, placements bourse débutant",
        sections=[
            ("L'action : un morceau d'entreprise",
             "<p>Acheter une action, c'est acheter une petite part d'une entreprise. Si elle grandit et gagne de l'argent, ta part vaut plus cher "
             "et elle peut te verser une partie de ses bénéfices : le <b>dividende</b>. Si elle va mal, l'action peut perdre beaucoup, "
             "et en cas de faillite, elle peut tomber à zéro.</p>"),
            ("L'obligation : un prêt",
             "<p>Une obligation, c'est un prêt que tu fais à une entreprise ou à un État. En échange, il te verse des intérêts (le <b>coupon</b>) "
             "et te rembourse à une date fixée (l'<b>échéance</b>). C'est en général moins risqué qu'une action… à condition que l'emprunteur "
             "puisse rembourser. Le prix d'une obligation baisse quand les taux d'intérêt montent.</p>"),
            ("L'ETF : un panier tout fait",
             "<p>Un ETF (ou « tracker ») est un fonds coté en Bourse qui copie un indice : par exemple les 40 entreprises du CAC 40, "
             "ou des milliers d'entreprises dans le monde. En une seule opération, tu achètes un petit bout de toutes. "
             "C'est la manière la plus simple de <b>diversifier</b>, avec des frais en général faibles.</p>"),
            ("La crypto : un actif numérique",
             "<p>Le bitcoin ou l'ether ne sont pas des entreprises : ils ne font pas de bénéfices et ne versent pas de dividendes. "
             "Leur prix dépend uniquement de ce que d'autres sont prêts à payer. Ils sont <b>beaucoup plus agités</b> que les actions : "
             "des chutes de plus de 50 % ont eu lieu plusieurs fois. Sur Radar Bourse, tu peux le vérifier : l'agitation prévue d'une crypto "
             "est souvent deux à trois fois celle d'une grande action.</p>"),
            ("En résumé",
             "<div class='tableau-simple'><table><tr><th>Placement</th><th>Ce que tu possèdes</th><th>Ce qui peut rapporter</th><th>Risque</th></tr>"
             "<tr><td>Action</td><td>Une part d'entreprise</td><td>Hausse du cours, dividendes</td><td>Élevé</td></tr>"
             "<tr><td>Obligation</td><td>Une créance (un prêt)</td><td>Intérêts</td><td>Faible à moyen</td></tr>"
             "<tr><td>ETF</td><td>Un panier de titres</td><td>Comme son indice</td><td>Selon l'indice</td></tr>"
             "<tr><td>Crypto</td><td>Un actif numérique</td><td>Hausse du prix uniquement</td><td>Très élevé</td></tr></table></div>"),
        ],
        retenir=["Action = part d'entreprise ; obligation = prêt ; ETF = panier qui copie un indice ; crypto = actif numérique sans bénéfices.",
                 "L'ETF est le moyen le plus simple de diversifier.",
                 "Plus un placement peut rapporter, plus il peut aussi faire perdre."],
        quiz=[("Que reçoit en général le détenteur d'une obligation ?",
               ["Un dividende", "Des intérêts (coupon)", "Des droits de vote", "Une part du capital"], 1,
               "L'obligation est un prêt : le prêteur reçoit des intérêts, appelés coupon, puis il est remboursé à l'échéance."),
              ("Un ETF « MSCI World » permet surtout…",
               ["De parier sur une seule entreprise", "D'investir dans beaucoup d'entreprises en une fois", "D'avoir un rendement garanti", "D'éviter tout risque"], 1,
               "Un ETF copie un indice : un ETF MSCI World contient plus de 1 000 grandes entreprises de pays développés. Il n'y a aucune garantie de rendement."),
              ("Pourquoi le bitcoin ne verse-t-il pas de dividende ?",
               ["Parce que c'est interdit", "Parce que ce n'est pas une entreprise qui fait des bénéfices", "Parce qu'il est trop cher", "Il en verse chaque année"], 1,
               "Une crypto n'a pas d'activité qui produit des bénéfices : seul le prix peut rapporter (ou faire perdre)."),
              ],
        exercice=("<p>Classe ces quatre placements du <b>moins agité</b> au <b>plus agité</b> en général : une action d'une grande entreprise, "
                  "un ETF sur le monde entier, une obligation d'État française, le bitcoin.</p>",
                  "<p>En général : <b>obligation d'État française</b> (la moins agitée) → <b>ETF monde</b> (diversifié) → <b>action d'une grande "
                  "entreprise</b> (dépend d'une seule société) → <b>bitcoin</b> (le plus agité). Ce n'est pas une règle absolue : une obligation "
                  "longue peut beaucoup bouger quand les taux changent, et un ETF sur un seul secteur peut être très agité.</p>"),
        sources=[("AMF : les différents produits financiers", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers"),
                 ("La finance pour tous : les obligations", "https://www.lafinancepourtous.com/decryptages/marches-financiers/produits-financiers/obligations/")],
    ),
    dict(
        id="pourquoi-un-cours-bouge", niveau=1, minutes=6,
        titre="Pourquoi un cours monte ou baisse",
        desc="Résultats, taux d'intérêt, actualités, émotions : les vraies raisons des mouvements.",
        mots="pourquoi une action monte, pourquoi la bourse baisse, cours de bourse explication, facteurs cours action",
        sections=[
            ("Le prix reflète des attentes",
             "<p>Le cours d'une action ne dit pas ce que vaut l'entreprise aujourd'hui, mais ce que les investisseurs <b>pensent qu'elle va gagner demain</b>. "
             "C'est pour ça qu'une entreprise peut publier de bons résultats… et voir son cours baisser : ils étaient moins bons que ce que le marché espérait.</p>"),
            ("Les quatre grandes causes",
             "<ol><li><b>Les résultats de l'entreprise</b> : ventes, bénéfices, prévisions pour l'année.</li>"
             "<li><b>Les taux d'intérêt</b> : quand ils montent, placer son argent sans risque rapporte plus, donc les actions attirent moins.</li>"
             "<li><b>L'actualité</b> : guerre, élection, nouvelle loi, nouveau produit, scandale.</li>"
             "<li><b>Les émotions</b> : la peur fait vendre trop vite, l'euphorie fait acheter trop cher. À court terme, elles pèsent souvent plus que les chiffres.</li></ol>"),
            ("Court terme et long terme",
             "<p>Sur une journée ou une semaine, les mouvements sont en grande partie du <b>bruit</b> : impossible à prévoir de façon fiable. "
             "Sur des années, le cours finit en général par suivre les bénéfices de l'entreprise. C'est pour ça que l'IA de Radar Bourse affiche "
             "« confiance faible » si souvent sur le sens du prix à un mois : c'est honnête, ce n'est pas un défaut.</p>"),
        ],
        retenir=["Un cours reflète les bénéfices attendus, pas ceux d'aujourd'hui.",
                 "Résultats, taux d'intérêt, actualité et émotions font bouger les prix.",
                 "À court terme, une grande partie des mouvements est imprévisible."],
        quiz=[("Une entreprise annonce un bénéfice en hausse de 10 %, mais le marché attendait +20 %. Que peut faire le cours ?",
               ["Forcément monter", "Baisser, car c'est moins bien qu'attendu", "Rester bloqué", "Doubler"], 1,
               "Le cours intègre déjà les attentes. Un résultat inférieur aux attentes déçoit, même s'il est en hausse."),
              ("Quand les taux d'intérêt montent fortement, les actions ont tendance à…",
               ["Devenir plus attractives", "Devenir moins attractives", "Ne pas réagir", "Être interdites"], 1,
               "Des placements sans risque mieux rémunérés font concurrence aux actions, et l'argent emprunté coûte plus cher aux entreprises."),
              ("Sur une seule journée, les mouvements d'un cours sont…",
               ["Toujours prévisibles", "En grande partie du bruit difficile à prévoir", "Toujours liés aux résultats", "Décidés par l'AMF"], 1,
               "À très court terme, les prix bougent beaucoup pour des raisons difficiles à anticiper."),
              ],
        exercice=("<p>Trouve, dans l'actualité de cette semaine sur <a href='../actu-bourse.html'>Actu bourse</a>, un titre qui a fortement bougé. "
                  "D'après toi, laquelle des quatre causes (résultats, taux, actualité, émotions) explique ce mouvement ?</p>",
                  "<p>Il n'y a pas une seule bonne réponse : l'important est de chercher la cause <b>avant</b> de conclure. Souvent, plusieurs causes se mélangent "
                  "(par exemple des résultats décevants qui déclenchent une vague de peur). Garde l'habitude de te demander : « qu'est-ce que le marché attendait ? »</p>"),
        sources=[("AMF : comprendre les variations de cours", "https://www.amf-france.org/fr/espace-epargnants")],
    ),
    dict(
        id="indices-cac40-sp500", niveau=1, minutes=5,
        titre="Les indices : CAC 40, S&P 500, MSCI World",
        desc="Ce que mesurent les indices boursiers et pourquoi tout le monde en parle.",
        mots="c'est quoi le cac 40, indice boursier débutant, s&p 500 explication, msci world c'est quoi, nasdaq débutant",
        sections=[
            ("Un thermomètre du marché",
             "<p>Un indice suit la valeur d'un groupe d'entreprises. Quand on entend « la Bourse de Paris a pris 1 % », on parle en général du "
             "<b>CAC 40</b> : les 40 plus grandes entreprises cotées à Paris (LVMH, TotalEnergies, Airbus…).</p>"),
            ("Les indices à connaître",
             "<ul><li><b>CAC 40</b> : 40 grandes entreprises françaises.</li>"
             "<li><b>S&amp;P 500</b> : environ 500 grandes entreprises américaines.</li>"
             "<li><b>Nasdaq 100</b> : 100 grandes entreprises non financières du Nasdaq, très orientées technologie.</li>"
             "<li><b>Euro Stoxx 50</b> : 50 grandes entreprises de la zone euro.</li>"
             "<li><b>MSCI World</b> : plus de 1 000 grandes entreprises des pays développés, dont environ 70 % américaines.</li></ul>"),
            ("Pourquoi c'est utile",
             "<p>Les indices servent de <b>repère</b> : un fonds qui gagne 5 % pendant que son indice gagne 10 % a en réalité fait moins bien. "
             "Et grâce aux ETF, on peut acheter un indice entier en une seule fois.</p>"),
            ("Attention aux dividendes",
             "<p>Le CAC 40 classique ne compte pas les dividendes versés. Sa version « dividendes réinvestis » (le CAC 40 GR) monte nettement plus sur longue période. "
             "Quand tu compares des performances, vérifie toujours si les dividendes sont inclus.</p>"),
        ],
        retenir=["Un indice suit un groupe d'entreprises et sert de repère.",
                 "CAC 40 = 40 grandes françaises ; S&P 500 = ~500 grandes américaines ; MSCI World = plus de 1 000 grandes entreprises mondiales.",
                 "On peut acheter un indice entier grâce à un ETF."],
        quiz=[("Combien d'entreprises composent le CAC 40 ?", ["10", "40", "100", "500"], 1,
               "Le CAC 40 regroupe 40 grandes entreprises cotées à Paris."),
              ("Le MSCI World contient surtout des entreprises…", ["Françaises", "Chinoises", "Américaines", "Africaines"], 2,
               "Environ 70 % du MSCI World est composé d'entreprises américaines : ce n'est pas aussi « mondial » que son nom le laisse croire."),
              ("Un fonds gagne 6 % sur un an, son indice de référence 9 %. Le fonds a fait…", ["Mieux que l'indice", "Moins bien que l'indice", "Pareil", "On ne peut pas savoir"], 1,
               "6 % est inférieur aux 9 % de l'indice : le fonds a sous-performé de 3 points."),
              ],
        exercice=("<p>Ouvre la fiche <a href='../titres/fchi.html'>CAC 40</a> sur Radar Bourse. Note sa variation sur un mois et l'agitation prévue par l'IA. "
                  "Fais pareil pour le <a href='../titres/btc-usd.html'>Bitcoin</a>. Lequel bouge le plus ?</p>",
                  "<p>Dans presque tous les cas, le Bitcoin a une agitation prévue bien plus élevée que le CAC 40 (souvent deux à quatre fois plus). "
                  "Un indice de 40 entreprises est diversifié ; une crypto seule ne l'est pas du tout.</p>"),
        sources=[("Euronext : CAC 40", "https://live.euronext.com/fr/product/indices/FR0003500008-XPAR"),
                 ("MSCI : MSCI World Index", "https://www.msci.com/indexes/index/990100")],
    ),
    dict(
        id="rendement-risque", niveau=1, minutes=7,
        titre="Rendement et risque : toujours ensemble",
        desc="Pourquoi il n'existe pas de gros gain sans risque, et comment mesurer ce risque.",
        mots="rendement risque bourse, volatilité explication, perte en capital, risque bourse débutant",
        sections=[
            ("La règle d'or",
             "<p>Plus un placement peut rapporter, plus il peut faire perdre. Un placement qui promet un rendement élevé <b>sans risque</b> "
             "est presque toujours une arnaque. Retiens-le avant tout le reste.</p>"),
            ("La volatilité : mesurer l'agitation",
             "<p>La <b>volatilité</b> mesure de combien un prix bouge habituellement. Une action avec une volatilité de 20 % par an fait, "
             "en gros, des écarts de ±20 % sur une année assez souvent (environ 2 années sur 3). C'est exactement ce que Radar Bourse appelle "
             "« agitation prévue » sur un mois.</p>"),
            ("Le piège des pertes",
             "<p>Les pertes et les gains ne se compensent pas de façon symétrique. Si tu perds 50 %, il faut ensuite <b>gagner 100 %</b> pour revenir au point de départ : "
             "1 000 € → 500 € → il faut doubler pour retrouver 1 000 €.</p>"
             "<div class='tableau-simple'><table><tr><th>Perte</th><th>Gain nécessaire pour revenir</th></tr>"
             "<tr><td>−10 %</td><td>+11,1 %</td></tr><tr><td>−25 %</td><td>+33,3 %</td></tr><tr><td>−50 %</td><td>+100 %</td></tr>"
             "<tr><td>−75 %</td><td>+300 %</td></tr></table></div>"),
            ("Le drawdown",
             "<p>Le <b>drawdown</b> (ou « baisse depuis le plus haut ») mesure la pire chute subie. Le CAC 40 est passé d'environ 6 900 points en "
             "septembre 2000 à environ 2 400 en mars 2003 : une chute d'environ 65 %. Il a fallu plus de vingt ans pour dépasser ce record. "
             "Se demander « est-ce que je supporterais de voir mon argent divisé par deux ? » est une excellente question de départ.</p>"),
        ],
        retenir=["Pas de gros rendement sans gros risque.", "La volatilité mesure l'agitation habituelle d'un prix.",
                 "Après −50 %, il faut +100 % pour revenir.", "Le drawdown mesure la pire chute ; avant d'investir, demande-toi si tu la supporterais."],
        quiz=[("Ton placement perd 20 %. De combien doit-il remonter pour revenir à son niveau de départ ?",
               ["20 %", "25 %", "40 %", "10 %"], 1,
               "100 → 80 : il faut gagner 20 sur 80, soit 20 / 80 = 25 %."),
              ("Un site promet « 15 % par mois garantis ». C'est…", ["Une bonne affaire", "Très probablement une arnaque", "Normal en Bourse", "Réservé aux experts"], 1,
               "Aucun placement légal ne garantit un tel rendement. C'est un signe classique d'escroquerie : vérifie toujours les listes noires de l'AMF."),
              ("Une volatilité plus élevée signifie…", ["Un prix plus stable", "Un prix plus agité", "Un rendement garanti", "Moins de frais"], 1,
               "La volatilité mesure l'ampleur habituelle des mouvements : plus elle est haute, plus le prix est agité."),
              ],
        exercice=("<p>Tu investis 2 000 €. Ton placement baisse de 40 %, puis remonte de 40 %. Combien as-tu à la fin ? As-tu retrouvé tes 2 000 € ?</p>",
                  "<p>2 000 × (1 − 0,40) = <b>1 200 €</b>, puis 1 200 × (1 + 0,40) = <b>1 680 €</b>. Tu as encore perdu 320 €, soit −16 %. "
                  "Pour revenir à 2 000 € depuis 1 200 €, il fallait +66,7 % (800 / 1 200).</p>"),
        sources=[("AMF : le couple rendement / risque", "https://www.amf-france.org/fr/espace-epargnants/bien-investir/rendement-risque")],
    ),
    dict(
        id="interets-composes", niveau=1, minutes=6,
        titre="Les intérêts composés : le temps travaille pour toi",
        desc="Pourquoi commencer tôt compte plus que commencer gros, calculs à l'appui.",
        mots="intérêts composés explication, effet boule de neige épargne, investir jeune bourse, calcul intérêts composés",
        sections=[
            ("L'effet boule de neige",
             "<p>Les intérêts composés, c'est gagner des intérêts <b>sur tes intérêts</b>. Avec 1 000 € placés à 5 % par an : "
             "après un an tu as 1 050 €, après deux ans 1 102,50 € (5 % de 1 050 €), et ainsi de suite.</p>"
             "<p>La formule : <b>capital final = capital × (1 + taux)<sup>années</sup></b>.</p>"),
            ("Le temps compte plus que tout",
             "<div class='tableau-simple'><table><tr><th>1 000 € placés à 5 % par an pendant</th><th>Résultat</th></tr>"
             "<tr><td>10 ans</td><td>1 629 €</td></tr><tr><td>20 ans</td><td>2 653 €</td></tr><tr><td>30 ans</td><td>4 322 €</td></tr>"
             "<tr><td>40 ans</td><td>7 040 €</td></tr></table></div>"
             "<p>Entre 30 et 40 ans de placement, le gain (2 718 €) est plus grand que celui des 20 premières années (1 653 €). C'est pour ça que commencer jeune, même avec de petites sommes, est un énorme avantage.</p>"),
            ("La règle de 72",
             "<p>Pour savoir en combien d'années ton argent double : divise 72 par le taux annuel. À 6 % par an : 72 / 6 = <b>12 ans</b>. "
             "C'est une approximation, mais elle est très proche de la réalité pour des taux entre 2 et 15 %.</p>"),
            ("Attention",
             "<p>En Bourse, il n'y a pas de taux fixe : une année peut faire +20 % et la suivante −15 %. Les exemples ci-dessus utilisent un taux "
             "régulier pour comprendre le mécanisme, pas pour prédire l'avenir. Les frais et l'inflation réduisent aussi le résultat réel. "
             "Teste toi-même avec le <a href='../outils/interets-composes.html'>calculateur d'intérêts composés</a>.</p>"),
        ],
        retenir=["Les intérêts composés font gagner des intérêts sur les intérêts.", "Capital final = capital × (1 + taux)^années.",
                 "Règle de 72 : 72 / taux = nombre d'années pour doubler.", "En Bourse, le rendement n'est jamais fixe ni garanti."],
        quiz=[("Avec la règle de 72, combien d'années faut-il pour doubler à 8 % par an ?", ["6 ans", "9 ans", "12 ans", "72 ans"], 1, "72 / 8 = 9 ans."),
              ("1 000 € à 10 % par an pendant 2 ans donnent…", ["1 200 €", "1 210 €", "1 100 €", "2 000 €"], 1,
               "1 000 × 1,10 = 1 100, puis 1 100 × 1,10 = 1 210 € : les 10 € en plus sont les intérêts sur les intérêts."),
              ("Qu'est-ce qui compte le plus pour profiter des intérêts composés ?", ["Le nom du courtier", "La durée", "La couleur du graphique", "L'heure d'achat"], 1,
               "Plus la durée est longue, plus l'effet boule de neige est puissant."),
              ],
        exercice=("<p>Léa place 100 € par mois à partir de 20 ans, Tom 200 € par mois à partir de 35 ans. Les deux s'arrêtent à 60 ans et obtiennent 5 % par an. "
                  "Qui a versé le plus ? Utilise le <a href='../outils/interets-composes.html'>calculateur</a> pour estimer qui a le plus à 60 ans.</p>",
                  "<p>Léa verse 100 € × 12 × 40 = <b>48 000 €</b>, Tom 200 € × 12 × 25 = <b>60 000 €</b>. Pourtant, à 5 % par an, Léa finit autour de "
                  "<b>152 000 €</b> et Tom autour de <b>119 000 €</b> : 15 années de plus valent plus que deux fois plus d'argent chaque mois. "
                  "(Calcul : versements mensuels capitalisés à 5 %/12 par mois.)</p>"),
        sources=[("AMF : les intérêts composés", "https://www.amf-france.org/fr/espace-epargnants/bien-investir")],
    ),
]

COURS_2 = [
    dict(
        id="pea-cto-assurance-vie", niveau=2, minutes=8,
        titre="PEA, compte-titres, assurance-vie : où investir ?",
        desc="Les trois enveloppes pour investir en Bourse en France, avec les règles 2026 vérifiées.",
        mots="pea débutant, pea ou compte titre, ouvrir un pea, plafond pea 2026, assurance vie bourse, enveloppe fiscale débutant",
        sections=[
            ("Une enveloppe, c'est quoi ?",
             "<p>Pour acheter des actions ou des ETF, il faut d'abord ouvrir un compte chez un courtier. Ce compte est une <b>enveloppe</b> : "
             "elle ne change pas ce que tu achètes, mais elle change <b>les impôts</b> et <b>les règles</b>. En France, il y en a trois principales.</p>"),
            ("Le PEA (plan d'épargne en actions)",
             "<ul><li>Pour les actions européennes et les ETF éligibles (beaucoup d'ETF « monde » le sont grâce à une technique de réplication).</li>"
             "<li>Plafond de versements : <b>150 000 €</b> (225 000 € au total avec un PEA-PME). Les gains ne comptent pas dans le plafond.</li>"
             "<li>Après <b>5 ans</b> : plus d'impôt sur le revenu sur les gains, seulement les prélèvements sociaux (18,6 % pour les gains réalisés depuis 2026).</li>"
             "<li>Avant 5 ans : un retrait clôture en principe le plan, et les gains sont taxés comme sur un compte-titres.</li>"
             "<li>Un seul PEA par personne. Les frais sont plafonnés par la loi.</li></ul>"),
            ("Le compte-titres ordinaire (CTO)",
             "<ul><li>Tout est possible : actions du monde entier, obligations, ETF de tous types.</li>"
             "<li>Pas de plafond, pas de durée minimale.</li>"
             "<li>Gains et dividendes taxés au prélèvement forfaitaire unique : <b>31,4 %</b> en 2026 (12,8 % d'impôt + 18,6 % de prélèvements sociaux).</li></ul>"),
            ("L'assurance-vie",
             "<ul><li>Contrat d'assurance qui peut contenir un fonds en euros (capital garanti par l'assureur) et des unités de compte (ETF, fonds…).</li>"
             "<li>Fiscalité plus douce après <b>8 ans</b>, et avantages pour la transmission.</li>"
             "<li>Les prélèvements sociaux y restent à 17,2 % en 2026.</li>"
             "<li>Choix de supports plus limité, et frais de gestion annuels à surveiller.</li></ul>"),
            ("Pour débuter",
             "<p>Pour un débutant qui vise le long terme, le <b>PEA</b> est souvent l'enveloppe la plus intéressante fiscalement, et ouvrir tôt fait courir le délai des 5 ans. "
             "Ce n'est pas un conseil personnalisé : ta situation (âge, projets, impôts) compte. En cas de doute, le site de l'AMF et service-public.fr sont les références.</p>"),
        ],
        retenir=["L'enveloppe change les impôts, pas ce que tu achètes.", "PEA : 150 000 € de versements, avantage fiscal après 5 ans.",
                 "Compte-titres : tout est possible, gains taxés à 31,4 % en 2026.", "Assurance-vie : avantages après 8 ans et pour la transmission."],
        quiz=[("Quel est le plafond de versements d'un PEA classique ?", ["22 950 €", "100 000 €", "150 000 €", "Aucun"], 2,
               "Le PEA classique est plafonné à 150 000 € de versements (les gains ne comptent pas)."),
              ("Au bout de combien d'années le PEA devient-il fiscalement avantageux ?", ["1 an", "5 ans", "8 ans", "10 ans"], 1,
               "Après 5 ans, les gains sont exonérés d'impôt sur le revenu (les prélèvements sociaux restent dus)."),
              ("Sur un compte-titres en 2026, le prélèvement forfaitaire unique est de…", ["17,2 %", "30 %", "31,4 %", "45 %"], 2,
               "12,8 % d'impôt sur le revenu + 18,6 % de prélèvements sociaux = 31,4 % (dividendes et plus-values perçus depuis le 1er janvier 2026)."),
              ],
        exercice=("<p>Tu réalises 1 000 € de plus-value. Combien d'impôts et prélèvements paies-tu (au prélèvement forfaitaire, sans option pour le barème) : "
                  "a) sur un compte-titres en 2026 ; b) sur un PEA de plus de 5 ans (gain réalisé en 2026) ?</p>",
                  "<p>a) Compte-titres : 1 000 × 31,4 % = <b>314 €</b>. b) PEA de plus de 5 ans : seulement les prélèvements sociaux, 1 000 × 18,6 % = <b>186 €</b>. "
                  "L'écart (128 €) correspond aux 12,8 % d'impôt sur le revenu évités grâce au PEA.</p>"),
        sources=[("Service-public : le PEA", "https://www.service-public.fr/particuliers/vosdroits/F2385"),
                 ("AMF : PEA, compte-titres, assurance-vie", "https://www.amf-france.org/fr/espace-epargnants/bien-investir/choisir-ses-placements"),
                 ("Prélèvements sociaux 2026 (18,6 % / 17,2 %)", "https://www.hagnere-patrimoine.fr/guides-patrimoine/comment-payer-moins-impots/csg-crds-prelevements-sociaux-2026")],
    ),
    dict(
        id="choisir-son-courtier", niveau=2, minutes=6,
        titre="Choisir son courtier et comprendre les frais",
        desc="Frais de courtage, de garde, de change : ce qui grignote ton rendement, et comment vérifier un courtier.",
        mots="choisir courtier bourse débutant, frais de courtage, meilleur courtier débutant, courtier agréé amf, frais bourse",
        sections=[
            ("Les frais qui comptent",
             "<ul><li><b>Frais de courtage</b> : payés à chaque achat ou vente (un montant fixe, un pourcentage, ou les deux).</li>"
             "<li><b>Frais de garde / tenue de compte</b> : prélevés chaque année par certains courtiers.</li>"
             "<li><b>Frais de change</b> : quand tu achètes une action en dollars depuis un compte en euros.</li>"
             "<li><b>Frais des ETF</b> (TER) : prélevés directement dans le fonds, chaque année.</li></ul>"),
            ("Pourquoi c'est important",
             "<p>1 % de frais par an, ça paraît peu. Sur 30 ans, avec 10 000 € qui rapportent 6 % par an, la différence entre 0,2 % et 1,2 % de frais annuels "
             "représente environ <b>13 000 €</b> à l'arrivée (environ 54 000 € contre 41 000 €). Les frais sont le seul élément que tu contrôles à coup sûr.</p>"),
            ("Vérifier qu'un courtier est autorisé",
             "<p>Avant d'ouvrir un compte, vérifie que le courtier est agréé : sur le registre <b>REGAFI</b> (Banque de France) ou la liste des prestataires de l'AMF. "
             "Méfie-toi des plateformes inconnues contactées via les réseaux sociaux.</p>"),
            ("Et si mon courtier fait faillite ?",
             "<p>Tes actions restent à toi : elles ne font pas partie des biens du courtier. En cas de problème, le Fonds de garantie des dépôts et de résolution (FGDR) "
             "indemnise jusqu'à <b>70 000 €</b> par personne pour les titres, et jusqu'à 100 000 € pour l'argent liquide si le courtier est une banque.</p>"),
        ],
        retenir=["Courtage, garde, change, frais des ETF : additionne tout.", "Quelques dixièmes de % par an font des milliers d'euros sur 30 ans.",
                 "Vérifie toujours l'agrément (REGAFI, AMF).", "Tes titres restent à toi en cas de faillite ; garantie FGDR jusqu'à 70 000 € pour les titres."],
        quiz=[("Quel frais est prélevé directement à l'intérieur d'un ETF ?", ["Le courtage", "Le TER (frais de gestion)", "Les frais de change", "Les frais de virement"], 1,
               "Le TER est prélevé chaque année dans le fonds : tu ne le vois pas passer, mais il réduit la performance."),
              ("Où vérifier qu'un courtier est autorisé en France ?", ["Sur Instagram", "Sur le registre REGAFI ou les listes de l'AMF", "Dans un forum", "Nulle part"], 1,
               "REGAFI et l'AMF permettent de vérifier les agréments ; l'AMF publie aussi des listes noires de sites non autorisés."),
              ("Jusqu'à combien le FGDR garantit-il les titres en cas de faillite d'un intermédiaire ?", ["10 000 €", "70 000 €", "1 million €", "Rien"], 1,
               "La garantie des titres couvre jusqu'à 70 000 € par personne et par établissement."),
              ],
        exercice=("<p>Courtier A : 2 € par ordre. Courtier B : 0,5 % par ordre (minimum 1 €). Tu investis 150 € par mois, en un ordre. Quel courtier coûte le moins cher par an ?</p>",
                  "<p>A : 2 € × 12 = <b>24 €</b>. B : 0,5 % de 150 € = 0,75 €, donc le minimum de 1 € s'applique : 1 € × 12 = <b>12 €</b>. "
                  "Le courtier B est moins cher pour ce petit montant. Avec 1 000 € par ordre, A coûterait 24 € et B 60 € : ça s'inverse !</p>"),
        sources=[("REGAFI (Banque de France)", "https://www.regafi.fr"),
                 ("AMF : mes titres sont-ils protégés en cas de faillite ?", "https://www.amf-france.org/fr/mes-titres-sont-ils-proteges-en-cas-de-faillite-de-mon-intermediaire-financier-0"),
                 ("AMF : listes noires", "https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde")],
    ),
    dict(
        id="passer-un-ordre", niveau=2, minutes=7,
        titre="Passer un ordre : au marché, à cours limité, stop",
        desc="Les types d'ordres et le carnet d'ordres, pour ne pas acheter n'importe quel prix.",
        mots="passer un ordre en bourse, ordre à cours limité, ordre au marché, ordre stop, carnet d'ordres débutant",
        sections=[
            ("Le carnet d'ordres",
             "<p>Pour chaque action, le marché affiche un <b>carnet d'ordres</b> : à gauche les acheteurs et le prix maximum qu'ils proposent, "
             "à droite les vendeurs et le prix minimum qu'ils demandent. Un échange a lieu quand un acheteur et un vendeur sont d'accord sur le prix.</p>"),
            ("Les trois ordres à connaître",
             "<ul><li><b>Ordre au marché</b> : tu achètes tout de suite, au meilleur prix disponible. Rapide, mais tu ne maîtrises pas le prix exact "
             "(risqué sur une petite action peu échangée).</li>"
             "<li><b>Ordre à cours limité</b> : tu fixes un prix maximum à l'achat (ou minimum à la vente). Ton ordre ne s'exécute que si ce prix est atteint. "
             "C'est l'ordre le plus recommandé aux débutants.</li>"
             "<li><b>Ordre stop</b> (à seuil de déclenchement) : il se déclenche quand le cours franchit un seuil. Souvent utilisé pour limiter une perte "
             "(« vends si le cours tombe sous 40 € »). Attention : en cas de forte chute à l'ouverture, il peut s'exécuter bien plus bas que le seuil.</li></ul>"),
            ("Les erreurs classiques",
             "<ul><li>Passer un ordre au marché à 9 h pile, quand les prix sont encore instables.</li>"
             "<li>Oublier qu'un ordre limité peut ne jamais s'exécuter.</li>"
             "<li>Se tromper d'action (deux noms proches) : vérifie toujours le <b>code ISIN</b> ou le symbole.</li></ul>"),
        ],
        retenir=["Le carnet d'ordres montre acheteurs et vendeurs.", "Ordre limité = tu fixes ton prix : le plus sûr pour débuter.",
                 "Ordre stop = se déclenche à un seuil, utile pour limiter une perte, mais sans garantie de prix.", "Vérifie toujours le code ISIN."],
        quiz=[("Quel ordre te garantit de ne pas payer plus qu'un prix choisi ?", ["Au marché", "À cours limité", "Stop", "Aucun"], 1,
               "L'ordre à cours limité fixe un prix maximum à l'achat."),
              ("Un ordre « au marché »…", ["S'exécute au meilleur prix disponible, tout de suite", "Attend un prix précis", "Ne s'exécute qu'à la clôture", "Est interdit aux particuliers"], 0,
               "Il est prioritaire et s'exécute immédiatement, au prix disponible."),
              ("Tu poses un stop de vente à 40 €. Le cours ouvre directement à 35 € après une mauvaise nouvelle. Tu vends probablement…", ["À 40 €", "Autour de 35 €", "À 45 €", "Tu ne vends pas"], 1,
               "Le stop se déclenche, mais au prix disponible : autour de 35 €. Un stop limite les pertes, il ne garantit pas le prix."),
              ],
        exercice=("<p>Une action cote 50 €. Tu veux l'acheter seulement si elle baisse à 48 €, et la revendre automatiquement si ensuite elle tombe sous 44 €. "
                  "Quels ordres passes-tu ?</p>",
                  "<p>1) Un <b>ordre d'achat à cours limité à 48 €</b>. 2) Une fois acheté, un <b>ordre de vente stop à 44 €</b>. "
                  "Ta perte maximale « prévue » est d'environ 4 € par action (8,3 %), mais elle peut être plus forte si le cours chute brutalement sous 44 €.</p>"),
        sources=[("AMF : les ordres de Bourse", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/actions/passer-un-ordre-de-bourse")],
    ),
    dict(
        id="etf-debutant", niveau=2, minutes=7,
        titre="Les ETF : la façon la plus simple d'investir",
        desc="Choisir un ETF : indice, frais, réplication, capitalisant ou distribuant.",
        mots="etf débutant, investir en etf, etf msci world pea, etf capitalisant ou distribuant, frais etf ter, meilleur etf débutant",
        sections=[
            ("Pourquoi les ETF plaisent tant",
             "<p>Un ETF te donne en une fois des dizaines ou des milliers d'entreprises, avec des frais souvent compris entre 0,05 % et 0,5 % par an. "
             "La plupart des fonds gérés activement font moins bien que leur indice sur longue période, une fois les frais déduits : c'est ce que montrent "
             "régulièrement les études SPIVA de S&amp;P. Copier l'indice à petit prix est donc une stratégie solide.</p>"),
            ("Les quatre questions à se poser",
             "<ol><li><b>Quel indice ?</b> Monde (MSCI World, MSCI ACWI), un pays (S&amp;P 500, CAC 40), un secteur… Plus c'est large, plus c'est diversifié.</li>"
             "<li><b>Quels frais ?</b> Regarde le TER (frais courants annuels).</li>"
             "<li><b>Capitalisant ou distribuant ?</b> Capitalisant : les dividendes sont réinvestis automatiquement (pratique pour le long terme). "
             "Distribuant : ils te sont versés.</li>"
             "<li><b>Éligible au PEA ?</b> C'est indiqué dans la fiche du fonds.</li></ol>"),
            ("Réplication physique ou synthétique",
             "<p>Un ETF « physique » achète vraiment les actions de l'indice. Un ETF « synthétique » obtient la performance via un contrat (un swap) "
             "avec une banque : c'est ce qui permet à certains ETF monde d'être éligibles au PEA. Les deux sont encadrés en Europe (règles UCITS).</p>"),
            ("Ce qu'un ETF ne fait pas",
             "<p>Un ETF ne protège pas d'une baisse du marché : si le monde entier baisse de 30 %, ton ETF monde aussi. Il supprime le risque d'une seule "
             "entreprise, pas le risque du marché.</p>"),
        ],
        retenir=["Un ETF copie un indice, avec des frais faibles.", "Regarde l'indice, le TER, capitalisant/distribuant et l'éligibilité PEA.",
                 "Physique ou synthétique : les deux sont encadrés (UCITS).", "Un ETF diversifie, mais ne protège pas d'une baisse générale."],
        quiz=[("Un ETF capitalisant…", ["Te verse les dividendes", "Réinvestit automatiquement les dividendes", "N'a pas de frais", "Est garanti"], 1,
               "Les dividendes restent dans le fonds et font grossir sa valeur."),
              ("Le TER d'un ETF, c'est…", ["Son rendement", "Ses frais courants annuels", "Son nombre d'actions", "Son prix"], 1, "Total Expense Ratio : les frais annuels prélevés dans le fonds."),
              ("Si tout le marché mondial baisse de 30 %, un ETF MSCI World…", ["Monte", "Baisse aussi, à peu près autant", "Reste stable", "Est remboursé"], 1,
               "L'ETF suit son indice, à la hausse comme à la baisse."),
              ],
        exercice=("<p>ETF A : MSCI World, TER 0,20 %, capitalisant, éligible PEA. ETF B : même indice, TER 0,50 %, distribuant, non éligible PEA. "
                  "Pour un investissement sur 20 ans dans un PEA, lequel choisirais-tu et pourquoi ?</p>",
                  "<p><b>L'ETF A</b> : il est éligible au PEA (donc utilisable dans cette enveloppe), moins cher (0,30 point de frais en moins chaque année) "
                  "et capitalisant (pas de dividendes à réinvestir à la main). Sur 20 ans, l'écart de frais seul représente environ 6 % de capital en moins pour l'ETF B.</p>"),
        sources=[("AMF : les ETF", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/placements-collectifs/trackers-etf"),
                 ("S&P SPIVA (études sur la gestion active)", "https://www.spglobal.com/spdji/en/research-insights/spiva/")],
    ),
    dict(
        id="investir-regulierement", niveau=2, minutes=6,
        titre="Investir régulièrement et garder une épargne de précaution",
        desc="L'investissement programmé (DCA) et pourquoi on n'investit jamais l'argent dont on aura besoin.",
        mots="investissement programmé dca, investir chaque mois bourse, épargne de précaution, combien investir en bourse débutant",
        sections=[
            ("D'abord : l'épargne de précaution",
             "<p>Avant d'investir en Bourse, garde de côté une <b>épargne de précaution</b> disponible tout de suite (sur un livret), souvent "
             "l'équivalent de <b>3 à 6 mois de dépenses</b>. Sinon, au premier imprévu, tu risques de devoir vendre tes actions au pire moment.</p>"),
            ("L'investissement programmé (DCA)",
             "<p>Le DCA (<i>dollar cost averaging</i>) consiste à investir la même somme à intervalle régulier, par exemple 100 € chaque mois, "
             "quoi qu'il arrive. Quand les prix sont bas, tu achètes plus de parts ; quand ils sont hauts, moins. Tu évites de tout investir juste avant une chute "
             "et, surtout, tu évites de chercher « le bon moment », ce que presque personne ne réussit.</p>"),
            ("Un exemple chiffré",
             "<div class='tableau-simple'><table><tr><th>Mois</th><th>Prix de la part</th><th>Investi</th><th>Parts achetées</th></tr>"
             "<tr><td>1</td><td>10 €</td><td>100 €</td><td>10</td></tr><tr><td>2</td><td>8 €</td><td>100 €</td><td>12,5</td></tr>"
             "<tr><td>3</td><td>12,50 €</td><td>100 €</td><td>8</td></tr></table></div>"
             "<p>Total : 300 € pour 30,5 parts, soit un prix moyen de <b>9,84 €</b>, plus bas que la moyenne des prix (10,17 €).</p>"),
            ("Une limite honnête",
             "<p>Sur un marché qui monte régulièrement, investir tout d'un coup rapporte en moyenne un peu plus que le DCA. Mais le DCA est plus simple "
             "psychologiquement et correspond à la vie réelle : on investit au fil de son salaire.</p>"),
        ],
        retenir=["Épargne de précaution d'abord (souvent 3 à 6 mois de dépenses).", "Le DCA = même somme, à intervalle régulier.",
                 "Il évite de chercher le « bon moment ».", "N'investis jamais en Bourse l'argent dont tu as besoin à court terme."],
        quiz=[("À quoi sert l'épargne de précaution ?", ["À spéculer", "À faire face aux imprévus sans vendre ses placements", "À payer ses impôts", "À rien"], 1,
               "Elle évite de devoir vendre des actions au mauvais moment."),
              ("Avec le DCA, quand le prix baisse, tu achètes…", ["Moins de parts", "Plus de parts", "Le même nombre de parts", "Rien"], 1,
               "Somme fixe ÷ prix plus bas = plus de parts."),
              ("Quel argent ne faut-il pas placer en actions ?", ["L'argent dont tu auras besoin dans quelques mois", "L'argent pour le long terme", "Le surplus d'épargne", "Les primes"], 0,
               "Les actions peuvent baisser fortement sur quelques mois : l'argent nécessaire à court terme doit rester disponible et sans risque."),
              ],
        exercice=("<p>Tu investis 50 € par mois. Les prix de la part sur 4 mois sont : 5 €, 4 €, 5 €, 6,25 €. Calcule le nombre total de parts et ton prix moyen.</p>",
                  "<p>Parts : 50/5 = 10 ; 50/4 = 12,5 ; 50/5 = 10 ; 50/6,25 = 8 → <b>40,5 parts</b> pour 200 €. Prix moyen : 200 / 40,5 = <b>4,94 €</b>, "
                  "inférieur à la moyenne des prix (5,06 €).</p>"),
        sources=[("AMF : bien investir", "https://www.amf-france.org/fr/espace-epargnants/bien-investir"),
                 ("La finance pour tous : l'épargne de précaution", "https://www.lafinancepourtous.com/pratique/epargne/")],
    ),
]
