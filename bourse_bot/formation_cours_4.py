"""Version 75 : l'Académie — module 7, « Aller plus loin » (notions stables, vérifiées le 11/11/2026 : AMF, ESMA, règlement PRIIPs).

Chaque chapitre : mini-leçons + un exercice par mini-leçon (EXOS_7), récap, cas concret, bilan.
"""
from .formation_exos import Q, V, N

_AMF = ("AMF : l'espace épargnants", "https://www.amf-france.org/fr/espace-epargnants")
_IEFP = ("La finance pour tous (Institut pour l'éducation financière du public)", "https://www.lafinancepourtous.com/")

COURS_7 = [
    dict(
        id="obligations-en-detail", niveau=7, minutes=7,
        titre="Les obligations en détail : coupon, taux et risque",
        desc="Comment une obligation rapporte, pourquoi son prix bouge avec les taux, et comment lire une notation.",
        mots="obligation explication, coupon obligation, prix obligation taux, notation obligation, obligation haut rendement, sensibilité obligation",
        sections=[
            ("Le coupon et l'échéance",
             "<p>Une obligation, c'est un prêt découpé en morceaux. Celui qui l'émet (un État, une entreprise) verse chaque année un intérêt fixe, le <b>coupon</b>, "
             "calculé sur la valeur de départ (le <b>nominal</b>). À l'<b>échéance</b>, il rembourse le nominal. Une obligation de 1 000 € à 3 % verse 30 € par an, "
             "puis rend les 1 000 € à la fin.</p>"),
            ("Pourquoi le prix bouge",
             "<p>Entre l'émission et l'échéance, l'obligation s'échange sur le marché. Si les taux montent à 5 %, plus personne ne veut payer 1 000 € pour toucher 30 € par an : "
             "son prix baisse jusqu'à ce que son rendement redevienne comparable. <b>Quand les taux montent, le prix des obligations existantes baisse</b>, et inversement.</p>"),
            ("La durée change tout",
             "<p>Plus l'échéance est lointaine, plus le prix réagit fortement aux taux : on parle de <b>sensibilité</b> (ou duration). "
             "Une obligation à 20 ans peut perdre bien plus qu'une obligation à 2 ans pour la même hausse de taux. C'est ce qui s'est passé en 2022 : "
             "les obligations longues ont subi des baisses rares.</p>"),
            ("Le risque de ne pas être remboursé",
             "<p>Des agences (S&P, Moody's, Fitch) donnent une <b>notation</b> à chaque émetteur, de AAA (le plus sûr) à D (défaut). De AAA à BBB, on parle de catégorie "
             "« investissement » ; en dessous (BB, B…), de <b>haut rendement</b> : l'intérêt est plus élevé parce que le risque de défaut l'est aussi.</p>"),
        ],
        retenir=["Le coupon est l'intérêt fixe versé chaque année sur le nominal.", "Quand les taux montent, le prix des obligations existantes baisse.",
                 "Plus l'échéance est longue, plus le prix réagit aux taux.", "Une notation sous BBB signale un haut rendement… et un risque plus élevé."],
        quiz=[("Une obligation de 1 000 € à 4 % verse chaque année…", ["4 €", "40 €", "400 €", "Rien avant l'échéance"], 1, "4 % de 1 000 € = 40 € par an."),
              ("Les taux d'intérêt du marché baissent. Le prix d'une obligation déjà émise…", ["Baisse", "Monte", "Ne bouge pas", "Tombe à zéro"], 1,
               "Son coupon devient plus intéressant que celui des nouvelles obligations : son prix monte."),
              ("Une obligation notée BB est…", ["De catégorie investissement", "À haut rendement, plus risquée", "Garantie par l'État", "Sans intérêt"], 1,
               "Sous BBB, on passe en haut rendement : plus d'intérêt, plus de risque de défaut.")],
        exercice=("<p>Tu hésites entre une obligation d'État à 2 ans et une à 25 ans, au même taux. Tu crains que les taux montent l'an prochain. Laquelle choisis-tu, et pourquoi ?</p>",
                  "<p>L'obligation à <b>2 ans</b> : sa sensibilité aux taux est bien plus faible. Si les taux montent, son prix baisse peu, et tu récupères vite ton capital "
                  "pour le replacer au nouveau taux. L'obligation à 25 ans pourrait perdre une part importante de sa valeur.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="devises-risque-de-change", niveau=7, minutes=6,
        titre="Les devises et le risque de change",
        desc="Pourquoi un placement en dollars peut perdre de l'argent même quand il monte, et comment s'en protéger.",
        mots="risque de change, investir en dollars, etf couvert devise, euro dollar bourse, etf hedgé",
        sections=[
            ("Deux mouvements en même temps",
             "<p>Quand tu achètes une action américaine avec des euros, tu fais deux paris : sur l'action, et sur le dollar face à l'euro. "
             "Si l'action monte de 10 % mais que le dollar perd 10 % face à l'euro, ton gain en euros est à peu près nul.</p>"),
            ("Le calcul exact",
             "<p>Les deux effets se multiplient : résultat = (1 + variation de l'action) × (1 + variation de la devise) − 1. "
             "Avec +10 % et −10 % : 1,10 × 0,90 − 1 = <b>−1 %</b>. Pour de petites variations, on peut simplement les additionner.</p>"),
            ("Les ETF « couverts »",
             "<p>Certains ETF sont dits <b>couverts</b> (ou « hedgés », souvent notés « EUR Hedged ») : ils neutralisent l'essentiel du mouvement de la devise. "
             "Tu gardes la performance de l'indice, sans le pari sur le dollar. Cette protection a un coût, souvent un peu plus de frais.</p>"),
            ("Faut-il se couvrir ?",
             "<p>Sur le long terme, beaucoup d'investisseurs acceptent le risque de change : il fait partie de la diversification, et les mouvements de devises "
             "ont tendance à moins peser sur des décennies que sur une année. Sur un objectif court ou une grosse part en dollars, la couverture se discute.</p>"),
        ],
        retenir=["Investir à l'étranger, c'est aussi parier sur la devise.", "Les effets de l'action et de la devise se multiplient.",
                 "Un ETF couvert neutralise l'essentiel du risque de change, contre un petit coût.", "Le risque de change pèse surtout à court terme."],
        quiz=[("Une action américaine fait +8 %, le dollar fait −8 % face à l'euro. Pour un investisseur en euros, le résultat est proche de…", ["+16 %", "0 %", "−16 %", "+8 %"], 1,
               "1,08 × 0,92 − 1 ≈ −0,6 % : à peu près nul."),
              ("Un ETF « EUR Hedged » sert à…", ["Doubler la performance", "Neutraliser l'effet du dollar", "Supprimer les frais", "Verser un dividende fixe"], 1,
               "Il couvre l'essentiel du mouvement de la devise."),
              ("Le risque de change pèse surtout…", ["À court terme", "Uniquement sur les obligations", "Jamais", "Seulement en crypto"], 0,
               "Sur une année, une devise peut bouger beaucoup ; sur des décennies, l'effet tend à s'atténuer.")],
        exercice=("<p>Tu as 1 000 € investis dans un ETF S&P 500 non couvert. En un an, l'indice fait +12 % en dollars et le dollar baisse de 5 % face à l'euro. Combien vaut ton placement en euros ?</p>",
                  "<p>1 000 × 1,12 × 0,95 = <b>1 064 €</b>. Tu gagnes 6,4 % au lieu de 12 % : le recul du dollar a mangé près de la moitié du gain.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="secteurs-cycliques-defensifs", niveau=7, minutes=6,
        titre="Secteurs : cycliques, défensifs, croissance et valeur",
        desc="Pourquoi les secteurs ne réagissent pas pareil à l'économie, et ce que ça change pour un portefeuille.",
        mots="valeurs cycliques, valeurs défensives, secteurs bourse, actions de croissance, value investing débutant, etf sectoriel",
        sections=[
            ("Les valeurs cycliques",
             "<p>Certaines entreprises suivent de près la santé de l'économie : automobile, industrie, matériaux, luxe, voyages. Quand l'économie accélère, "
             "leurs ventes bondissent ; en récession, elles chutent. Ce sont les <b>cycliques</b>.</p>"),
            ("Les valeurs défensives",
             "<p>D'autres vendent des choses dont on a besoin quoi qu'il arrive : santé, alimentation, produits d'hygiène, électricité, eau. "
             "Leurs bénéfices bougent moins avec l'économie : ce sont les <b>défensives</b>. Elles baissent souvent moins dans les crises… et montent souvent moins dans les reprises.</p>"),
            ("Croissance et valeur",
             "<p>On distingue aussi les actions de <b>croissance</b> (bénéfices qui progressent vite, souvent chères, comme beaucoup de valeurs technologiques) "
             "et les actions <b>value</b> (« valeur » : entreprises plus mûres, ratios plus bas, souvent des dividendes). Selon les périodes, l'un ou l'autre style domine, "
             "parfois pendant des années.</p>"),
            ("Le piège du secteur à la mode",
             "<p>Un ETF sectoriel (uniquement la tech, uniquement l'énergie…) concentre le risque : tout le portefeuille dépend d'un seul moteur. "
             "Il peut servir de petit satellite, rarement de cœur de portefeuille. Les pages <a href='../themes.html'>par thème</a> de Radar Bourse montrent l'agitation de chaque secteur.</p>"),
        ],
        retenir=["Les cycliques suivent l'économie de près.", "Les défensives (santé, alimentation, énergie de réseau) résistent mieux en crise.",
                 "Croissance et value dominent tour à tour, parfois pendant des années.", "Un ETF sectoriel concentre le risque : à garder en petite part."],
        quiz=[("Lequel de ces secteurs est plutôt défensif ?", ["Automobile", "Santé", "Matériaux de construction", "Voyages"], 1,
               "On a besoin de se soigner quelle que soit la conjoncture."),
              ("En récession, les valeurs cycliques…", ["Résistent mieux que les autres", "Souffrent en général davantage", "Versent plus de dividendes", "Ne bougent pas"], 1,
               "Leurs ventes dépendent directement de l'activité économique."),
              ("Mettre tout son argent dans un ETF « tech » revient à…", ["Bien diversifier", "Concentrer le risque sur un seul secteur", "Supprimer le risque", "Acheter des obligations"], 1,
               "Tout dépend d'un seul moteur : c'est l'inverse de la diversification.")],
        exercice=("<p>Classe ces entreprises en cyclique ou défensive : un constructeur automobile, un fabricant de médicaments, une compagnie aérienne, un distributeur d'eau.</p>",
                  "<p>Cycliques : le <b>constructeur automobile</b> et la <b>compagnie aérienne</b>. Défensives : le <b>fabricant de médicaments</b> et le <b>distributeur d'eau</b>.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="ipo-rachats-divisions", niveau=7, minutes=6,
        titre="Introductions en Bourse, rachats et divisions d'actions",
        desc="Ce qui se passe vraiment lors d'une IPO, d'un rachat d'actions, d'une division ou d'une augmentation de capital.",
        mots="introduction en bourse ipo, rachat d'actions explication, division d'action split, augmentation de capital dilution, bénéfice par action",
        sections=[
            ("L'introduction en Bourse",
             "<p>Lors d'une <b>introduction en Bourse</b> (IPO), une entreprise vend pour la première fois des actions au public. Le prix est fixé avec des banques. "
             "Les premiers jours sont souvent très agités, et beaucoup d'IPO très médiatisées ont ensuite déçu : l'enthousiasme du lancement ne dit rien de la suite.</p>"),
            ("Le rachat d'actions",
             "<p>Une entreprise qui a de la trésorerie peut <b>racheter ses propres actions</b> puis les annuler. Il y a alors moins d'actions pour le même bénéfice : "
             "le <b>bénéfice par action</b> augmente. C'est une autre façon de rendre de l'argent aux actionnaires que le dividende.</p>"),
            ("La division d'action",
             "<p>Une <b>division</b> (« split ») découpe chaque action en plusieurs : une action à 300 € devient 3 actions à 100 €. Ta part de l'entreprise "
             "ne change pas, ta valeur non plus. Le but est surtout de rendre l'action plus accessible. Ce n'est ni une bonne ni une mauvaise nouvelle en soi.</p>"),
            ("L'augmentation de capital",
             "<p>À l'inverse, une entreprise peut créer de nouvelles actions pour lever de l'argent : c'est une <b>augmentation de capital</b>. "
             "Si tu ne suis pas, ta part de l'entreprise diminue : on parle de <b>dilution</b>. Elle peut financer un beau projet… ou boucher un trou.</p>"),
        ],
        retenir=["Une IPO médiatisée n'est pas une garantie de bonne affaire.", "Un rachat d'actions augmente le bénéfice par action.",
                 "Une division ne change pas la valeur de ce que tu possèdes.", "Une augmentation de capital dilue les actionnaires qui ne suivent pas."],
        quiz=[("Une action à 400 € est divisée par 4. Tu avais 1 action. Après la division, tu as…", ["1 action à 100 €", "4 actions à 100 €", "4 actions à 400 €", "1 action à 400 €"], 1,
               "4 × 100 € = 400 € : la valeur ne change pas."),
              ("Un rachat d'actions suivi d'une annulation…", ["Fait baisser le bénéfice par action", "Fait monter le bénéfice par action", "Ne change rien", "Est interdit en France"], 1,
               "Le même bénéfice est partagé entre moins d'actions."),
              ("La dilution, c'est…", ["Une baisse de ta part de l'entreprise quand de nouvelles actions sont créées", "Un dividende exceptionnel", "Une division d'action", "Une taxe"], 0,
               "De nouvelles actions sont créées : chaque ancienne action représente une part plus petite.")],
        exercice=("<p>Une entreprise gagne 200 M€ et compte 100 millions d'actions. Elle en rachète et annule 20 millions. Quel était son bénéfice par action avant, et quel est-il après (à bénéfice égal) ?</p>",
                  "<p>Avant : 200 ÷ 100 = <b>2 €</b> par action. Après : 200 ÷ 80 = <b>2,50 €</b> par action, soit +25 %, sans que l'entreprise gagne un euro de plus.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="levier-options-cfd", niveau=7, minutes=7,
        titre="Effet de levier, options et CFD : comprendre avant de fuir",
        desc="Comment le levier multiplie gains et pertes, ce que sont les options, et pourquoi les CFD font perdre la majorité des particuliers.",
        mots="effet de levier explication, cfd risque, options call put débutant, trading à effet de levier, produits dérivés débutant",
        sections=[
            ("Le levier multiplie tout",
             "<p>Avec un <b>effet de levier</b> de 5, tu prends une position 5 fois plus grosse que ton argent. Si le marché monte de 4 %, tu gagnes 20 %. "
             "S'il baisse de 20 %, tu perds <b>100 %</b> de ta mise. Le levier ne change pas tes chances d'avoir raison : il change seulement la taille des dégâts.</p>"),
            ("Les options",
             "<p>Une <b>option d'achat</b> (call) donne le droit, pas l'obligation, d'acheter un actif à un prix fixé, jusqu'à une date donnée. Une <b>option de vente</b> (put) donne le droit de vendre. "
             "L'acheteur paie une prime ; si le marché ne va pas dans son sens, l'option peut finir sans valeur et la prime est perdue. Les professionnels s'en servent souvent pour se protéger.</p>"),
            ("Les CFD",
             "<p>Un <b>CFD</b> (contrat sur la différence) permet de parier sur la hausse ou la baisse d'un prix, avec du levier, sans posséder l'actif. "
             "En Europe, les courtiers doivent afficher la part de comptes particuliers qui perdent de l'argent : c'est une <b>large majorité</b>. "
             "Le levier proposé aux particuliers est plafonné (par exemple 5 fois sur une action, 2 fois sur une crypto).</p>"),
            ("La règle simple",
             "<p>Tant que tu n'as pas un portefeuille solide, des années d'expérience et une stratégie écrite, ces produits n'ont rien à faire dans ton épargne. "
             "Les comprendre sert surtout à reconnaître les publicités et les « coachs » qui les présentent comme un raccourci vers la richesse.</p>"),
        ],
        retenir=["Le levier multiplie les gains et les pertes dans la même proportion.", "Une option donne un droit, mais sa prime peut être entièrement perdue.",
                 "Une large majorité des particuliers perdent de l'argent sur les CFD.", "Pour débuter, ces produits sont à comprendre, pas à utiliser."],
        quiz=[("Avec un levier de 10, une baisse de 10 % du marché fait perdre…", ["10 %", "50 %", "100 % de la mise", "Rien"], 2, "10 × 10 % = 100 % : la mise est entièrement perdue."),
              ("Un call, c'est…", ["Le droit d'acheter à un prix fixé", "L'obligation de vendre", "Un dividende", "Un ETF"], 0, "L'acheteur d'un call a le droit, pas l'obligation, d'acheter."),
              ("Que doivent afficher les courtiers européens de CFD ?", ["Leur chiffre d'affaires", "La part de comptes particuliers qui perdent de l'argent", "Leur meilleur client", "Rien"], 1,
               "C'est une obligation européenne : et cette part est une large majorité.")],
        exercice=("<p>Tu places 500 € sur un CFD avec un levier de 5, à la hausse sur une action. L'action baisse de 8 %. Combien perds-tu, et que reste-t-il ?</p>",
                  "<p>Ta position vaut 5 × 500 = 2 500 €. Une baisse de 8 % fait perdre 200 €, soit <b>40 % de ta mise</b> : il te reste 300 €, pour une baisse de l'action de seulement 8 %. "
                  "Sans levier, tu aurais perdu 40 €.</p>"),
        sources=[_AMF, ("ESMA : mesures sur les CFD pour les particuliers", "https://www.esma.europa.eu/")],
    ),
    dict(
        id="lire-un-dic", niveau=7, minutes=6,
        titre="Lire un DIC : le document qui dit tout d'un fonds",
        desc="L'indicateur de risque de 1 à 7, les scénarios, les frais et la durée conseillée : savoir lire la fiche obligatoire avant d'acheter.",
        mots="document d'informations clés, dic fonds, indicateur de risque 1 à 7, frais etf lecture, kid priips explication",
        sections=[
            ("Un document obligatoire",
             "<p>Avant d'acheter un fonds, un ETF ou un produit structuré, tu dois pouvoir lire son <b>DIC</b> (document d'informations clés, ou KID en anglais). "
             "Il fait quelques pages, a la même structure pour tous les produits, et doit être fourni gratuitement par le courtier ou l'émetteur.</p>"),
            ("L'indicateur de risque",
             "<p>Le DIC affiche un <b>indicateur synthétique de risque</b> de <b>1</b> (risque le plus faible) à <b>7</b> (le plus élevé). Un fonds monétaire est souvent en 1, "
             "un ETF actions monde plutôt en 4 ou 5, des produits très spéculatifs en 6 ou 7. C'est le premier chiffre à regarder.</p>"),
            ("Les scénarios et la durée conseillée",
             "<p>Le DIC présente des <b>scénarios de performance</b> (défavorable, intermédiaire, favorable, et de tension). Ce sont des simulations, <b>pas des promesses</b>. "
             "Il indique aussi une <b>durée de détention recommandée</b> : un fonds actions conseillé sur 5 ans n'est pas fait pour un projet dans 1 an.</p>"),
            ("Les coûts",
             "<p>Une section détaille les <b>coûts</b> : frais d'entrée ou de sortie, et frais courants prélevés chaque année. Avec 10 000 € et 0,20 % de frais courants, "
             "tu paies environ 20 € par an ; à 2 %, environ 200 €. Sur 20 ans, l'écart devient énorme.</p>"),
        ],
        retenir=["Le DIC est gratuit et obligatoire : lis-le avant d'acheter.", "L'indicateur de risque va de 1 (faible) à 7 (élevé).",
                 "Les scénarios sont des simulations, jamais des promesses.", "Les frais courants se paient chaque année, sur tout ton capital."],
        quiz=[("Sur l'échelle de risque du DIC, 7 signifie…", ["Le risque le plus faible", "Le risque le plus élevé", "7 % de rendement", "7 ans de détention"], 1,
               "L'échelle va de 1 (faible) à 7 (élevé)."),
              ("Le scénario « favorable » d'un DIC est…", ["Une garantie", "Une simulation possible parmi d'autres", "Le rendement minimum", "Obligatoirement atteint"], 1,
               "Les scénarios sont des simulations, pas des engagements."),
              ("Un fonds conseille une détention de 5 ans. Ton projet est dans 1 an. Il est…", ["Adapté", "Peu adapté", "Obligatoire", "Sans risque"], 1,
               "La durée conseillée doit correspondre à ton horizon.")],
        exercice=("<p>Deux ETF suivent le même indice. Le DIC du premier indique 0,07 % de frais courants, celui du second 0,60 %. Sur 20 000 €, combien coûte chacun par an, "
                  "et quelle différence sur 10 ans (sans compter la croissance) ?</p>",
                  "<p>Premier : 20 000 × 0,07 % = <b>14 €</b> par an. Second : 20 000 × 0,60 % = <b>120 €</b> par an. Sur 10 ans : 140 € contre 1 200 €, soit "
                  "<b>1 060 €</b> d'écart, pour exactement le même indice. Avec la croissance du capital, l'écart serait encore plus grand.</p>"),
        sources=[_AMF, _IEFP],
    ),
]

EXOS_7 = {
    "obligations-en-detail": [
        N("Une obligation de 1 000 € a un coupon de 3 %. Combien rapporte-t-elle chaque année, en € ?", 30, 0, "€", "3 % de 1 000 € = 30 € par an, jusqu'à l'échéance."),
        Q("Les taux du marché passent de 3 % à 5 %. Que devient le prix d'une obligation à 3 % déjà émise ?", ["Il monte", "Il baisse", "Il reste à 1 000 €"], 1,
          "Personne ne veut payer le prix plein pour 3 % quand on peut avoir 5 % : son prix baisse."),
        V("Pour une même hausse de taux, une obligation à 20 ans baisse en général plus qu'une obligation à 2 ans.", True,
          "Plus l'échéance est longue, plus la sensibilité aux taux est forte."),
        Q("Laquelle de ces notations correspond au haut rendement (plus risqué) ?", ["AAA", "A", "B"], 2, "Sous BBB, on est en haut rendement. B est bien en dessous."),
    ],
    "devises-risque-de-change": [
        V("En achetant une action américaine avec des euros, tu es aussi exposé au cours du dollar.", True, "Ton résultat dépend de l'action ET du dollar face à l'euro."),
        N("L'action fait +10 % en dollars, le dollar fait −10 % face à l'euro. Quel est ton résultat en euros, en % ?", -1, 0.1, "%",
          "1,10 × 0,90 − 1 = −0,01, soit −1 %. Les deux effets se multiplient."),
        Q("Quel ETF neutralise l'essentiel du risque lié au dollar ?", ["Un ETF « EUR Hedged »", "Un ETF distribuant", "Un ETF sectoriel"], 0,
          "« Hedged » signifie couvert : l'effet de la devise est neutralisé, contre un petit coût."),
        V("Le risque de change pèse en général plus sur une année que sur plusieurs décennies.", True, "Les mouvements de devises tendent à s'atténuer sur le très long terme."),
    ],
    "secteurs-cycliques-defensifs": [
        Q("Lequel de ces secteurs est cyclique ?", ["L'automobile", "La santé", "L'alimentation"], 0, "Les ventes de voitures suivent de près l'activité économique."),
        Q("Pendant une récession, quel secteur résiste en général le mieux ?", ["Les voyages", "La consommation de base (alimentation, hygiène)", "Le luxe"], 1,
          "On continue d'acheter à manger et des produits d'hygiène, même en crise."),
        V("Les actions de croissance font toujours mieux que les actions value.", False, "Les deux styles dominent tour à tour, parfois pendant des années."),
        Q("Quelle place donner à un ETF sectoriel dans un portefeuille de débutant ?", ["Tout le portefeuille", "Une petite part (satellite)", "Aucune règle"], 1,
          "Il concentre le risque : il peut compléter un cœur diversifié, pas le remplacer."),
    ],
    "ipo-rachats-divisions": [
        V("Une introduction en Bourse très médiatisée garantit une bonne performance ensuite.", False, "Beaucoup d'IPO médiatisées ont déçu : l'enthousiasme du lancement ne prédit rien."),
        N("Bénéfice de 100 M€, 50 millions d'actions. Après le rachat et l'annulation de 10 millions d'actions, quel est le bénéfice par action, en € ?", 2.5, 0.01, "€",
          "100 ÷ 40 = 2,50 € par action (contre 2 € avant)."),
        N("Une action à 240 € est divisée par 3. Quel est le nouveau prix d'une action, en € ?", 80, 0, "€", "240 ÷ 3 = 80 €. Tu as 3 fois plus d'actions : ta valeur ne change pas."),
        Q("Une entreprise crée beaucoup de nouvelles actions et tu n'en achètes pas. Que devient ta part de l'entreprise ?", ["Elle augmente", "Elle diminue (dilution)", "Elle ne change pas"], 1,
          "Le gâteau est partagé en plus de parts : la tienne devient plus petite."),
    ],
    "levier-options-cfd": [
        N("Avec un levier de 5, de combien (en %) le marché doit-il baisser pour que tu perdes toute ta mise ?", 20, 0, "%", "5 × 20 % = 100 % : il suffit d'une baisse de 20 %."),
        Q("Que perd au maximum l'acheteur d'une option d'achat (call) ?", ["La prime payée", "Dix fois la prime", "Rien"], 0,
          "Si l'option finit sans valeur, l'acheteur perd la prime, pas davantage."),
        V("La plupart des comptes de particuliers gagnent de l'argent sur les CFD.", False, "C'est l'inverse : les avertissements obligatoires montrent qu'une large majorité perd."),
        Q("Un « coach » promet de devenir riche vite grâce au trading à effet de levier. Quel est le bon réflexe ?", ["Suivre sa formation payante", "Se méfier et vérifier les listes noires de l'AMF", "Emprunter pour commencer"], 1,
          "Promesse de gains rapides + levier : deux signaux d'alerte réunis."),
    ],
    "lire-un-dic": [
        V("Le courtier doit te donner gratuitement le DIC d'un fonds avant que tu l'achètes.", True, "C'est une obligation réglementaire en Europe."),
        Q("Un fonds affiche un indicateur de risque de 6 sur 7. C'est…", ["Un placement prudent", "Un placement très risqué", "Un placement garanti"], 1,
          "6 et 7 sont en haut de l'échelle : risque élevé."),
        V("Le scénario favorable d'un DIC est un rendement garanti.", False, "Ce n'est qu'une simulation : rien n'est garanti."),
        N("10 000 € dans un fonds à 0,20 % de frais courants : combien de frais par an, en € ?", 20, 0, "€", "10 000 × 0,20 % = 20 € par an, prélevés à l'intérieur du fonds."),
    ],
}
