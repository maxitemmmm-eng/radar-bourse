"""Version 77 : l'Académie — module 8, « Élargir son horizon » (or et matières premières, immobilier coté et SCPI,
investissement responsable) puis un chapitre de synthèse : le plan d'action en 7 étapes.

Notions stables, relues le 12/11/2026 (AMF, label ISR, ministère de l'Économie). Les points qui bougent (classification européenne
des fonds durables) sont signalés comme tels dans le texte.
"""
from .formation_exos import Q, V, N

_AMF = ("AMF : l'espace épargnants", "https://www.amf-france.org/fr/espace-epargnants")
_IEFP = ("La finance pour tous (Institut pour l'éducation financière du public)", "https://www.lafinancepourtous.com/")
_ISR = ("Le label ISR (site officiel)", "https://www.lelabelisr.fr/")

COURS_8 = [
    dict(
        id="or-matieres-premieres", niveau=8, minutes=7,
        titre="L'or et les matières premières",
        desc="Ce que l'or apporte vraiment à un portefeuille, comment on en achète, et pourquoi un fonds « pétrole » ne suit pas le prix du baril.",
        mots="investir dans l'or, or valeur refuge, ETC or, matières premières bourse, contango, acheter de l'or débutant",
        sections=[
            ("L'or : un actif qui ne rapporte rien",
             "<p>Un lingot ne verse ni dividende ni intérêt. Ce que tu gagnes avec l'or dépend d'une seule chose : le prix auquel quelqu'un te le rachètera plus tard. "
             "On l'appelle <b>valeur refuge</b> parce qu'il a souvent bien résisté pendant les grandes crises, quand les actions chutaient.</p>"
             "<p>Refuge ne veut pas dire tranquille. Entre son sommet de 2011 (autour de 1 900 dollars l'once) et la fin 2015 (autour de 1 050 dollars), "
             "l'or a perdu environ <b>45 %</b>. Il a ensuite battu de nouveaux records, mais il a fallu près de neuf ans pour revoir le niveau de 2011.</p>"),
            ("Trois façons d'en avoir",
             "<ul><li><b>L'or physique</b> (pièces, lingots) : tu le tiens dans la main, mais tu paies une prime à l'achat, et il faut le stocker et l'assurer.</li>"
             "<li><b>L'or « papier »</b> : un produit coté adossé à de l'or stocké dans un coffre. En Europe, ce n'est pas un ETF mais un <b>ETC</b> : "
             "juridiquement une dette de l'émetteur, garantie par le métal. Il s'achète sur un compte-titres, pas dans un PEA.</li>"
             "<li><b>Les actions de mines d'or</b> : ce sont des entreprises, avec leurs coûts, leurs dettes et leurs accidents. Elles bougent bien plus que l'or lui-même.</li></ul>"),
            ("Pétrole, blé, cuivre : des marchés de contrats",
             "<p>Personne ne stocke des barils dans son salon. Les fonds sur matières premières achètent des <b>contrats à terme</b> (une promesse de livraison à une date donnée) "
             "et doivent les remplacer avant chaque échéance. Quand le contrat suivant coûte plus cher que celui qu'on vend, le fonds perd un peu à chaque remplacement.</p>"
             "<p>Résultat : un fonds « pétrole » peut baisser alors que le prix du baril affiché à la télévision monte. Le 20 avril 2020, un contrat sur le pétrole américain "
             "a même fini à un prix <b>négatif</b> (−37 dollars) : les vendeurs payaient pour ne pas avoir à stocker.</p>"),
            ("Quelle place dans un portefeuille ?",
             "<p>L'intérêt de l'or est de ne pas bouger comme les actions : une petite part peut amortir certains chocs. Beaucoup d'investisseurs qui en détiennent "
             "se limitent à quelques pourcents du total, et beaucoup d'autres s'en passent très bien.</p>"
             "<p>Les matières premières prises une à une (pétrole, blé, gaz) relèvent plus du pari que de l'épargne : leurs prix dépendent de la météo, des guerres et des stocks, "
             "et les fonds qui les suivent subissent le coût des contrats. Pour un portefeuille de long terme, elles ne sont pas indispensables.</p>"),
        ],
        retenir=["L'or ne verse aucun revenu : seul son prix de revente compte.",
                 "Valeur refuge ne veut pas dire sans baisse : −45 % entre 2011 et 2015.",
                 "En Europe, l'or coté s'achète via un ETC, sur un compte-titres.",
                 "Un fonds sur matières premières suit des contrats à terme, pas le prix affiché du jour."],
        quiz=[("Que rapporte un lingot d'or tant qu'on le garde ?", ["Un intérêt annuel", "Un dividende", "Rien : seul le prix de revente compte", "Un loyer"], 2,
               "L'or ne produit aucun revenu. Le gain éventuel vient uniquement de la différence entre le prix d'achat et le prix de revente."),
              ("Pourquoi un fonds « pétrole » peut-il baisser alors que le baril monte ?",
               ["Parce qu'il est mal géré", "Parce qu'il doit remplacer régulièrement ses contrats à terme, parfois à perte", "Parce que le pétrole est coté en dollars", "Ce n'est pas possible"], 1,
               "Le fonds détient des contrats à terme qu'il doit renouveler avant l'échéance. Si le contrat suivant est plus cher, chaque renouvellement coûte un peu."),
              ("En Europe, comment s'appelle le produit coté qui suit le prix de l'or ?", ["Un ETF", "Un ETC", "Un PEA", "Une SCPI"], 1,
               "Un ETF européen ne peut pas détenir une seule matière première. Les produits adossés à l'or sont des ETC (exchange traded commodities).")],
        exercice=("<p>Karim veut « se protéger d'un krach » et hésite entre mettre 5 % ou 50 % de son épargne investie en or. "
                  "Avec ce que tu sais (pas de revenu, baisse de 45 % entre 2011 et 2015), que lui dirais-tu ?</p>",
                  "<p>À 5 %, une chute de 45 % de l'or coûterait à Karim environ 2 % de son portefeuille : supportable, et l'or peut amortir d'autres chocs. "
                  "À 50 %, la même chute lui coûterait plus de 22 %, et la moitié de son épargne ne produirait aucun revenu pendant des années. "
                  "L'or peut jouer un rôle d'appoint, pas remplacer la diversification.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="immobilier-cote-scpi", niveau=8, minutes=7,
        titre="L'immobilier sans acheter d'appartement : foncières et SCPI",
        desc="Foncières cotées (SIIC, REIT) et SCPI : comment elles marchent, ce qu'elles coûtent, et pourquoi on n'en sort pas toujours quand on veut.",
        mots="SCPI explication, SIIC foncière cotée, REIT, pierre papier, frais SCPI, liquidité SCPI, investir immobilier bourse",
        sections=[
            ("Les foncières cotées",
             "<p>Une <b>foncière cotée</b> est une entreprise dont le métier est de posséder des immeubles (bureaux, centres commerciaux, entrepôts, logements) et d'encaisser les loyers. "
             "En France, elles ont un statut particulier, les <b>SIIC</b> ; aux États-Unis, on parle de <b>REIT</b>.</p>"
             "<p>Le principe du statut : la foncière ne paie pas d'impôt sur ses bénéfices locatifs, à condition d'en reverser l'essentiel à ses actionnaires "
             "(95 % des loyers nets pour une SIIC). D'où des dividendes souvent élevés. Mais c'est une action : elle s'achète et se revend en une seconde, "
             "et son cours peut chuter fortement, surtout quand les taux d'intérêt montent.</p>"),
            ("Les SCPI",
             "<p>Une <b>SCPI</b> (société civile de placement immobilier) rassemble l'argent de milliers d'épargnants pour acheter des immeubles, puis leur reverse les loyers. "
             "Elle n'est <b>pas cotée en Bourse</b> : les parts s'achètent auprès de la société de gestion, à un prix qu'elle fixe.</p>"
             "<ul><li><b>Frais d'entrée</b> souvent compris entre 8 % et 12 %, inclus dans le prix de la part : il faut plusieurs années de loyers pour les amortir.</li>"
             "<li><b>Délai de jouissance</b> : les premiers revenus n'arrivent que quelques mois après l'achat.</li>"
             "<li>Durée de placement conseillée : en général <b>8 à 10 ans</b> au minimum.</li></ul>"),
            ("Le vrai risque : ne pas pouvoir sortir",
             "<p>Pour revendre des parts de SCPI, il faut qu'un autre épargnant les achète. Quand tout va bien, c'est rapide. "
             "Quand beaucoup de monde veut sortir en même temps, les demandes s'empilent et l'attente peut durer des mois, voire plus.</p>"
             "<p>C'est ce qui s'est produit à partir de 2023 : avec la hausse des taux, plusieurs SCPI connues ont <b>baissé le prix de leurs parts</b>, "
             "et des épargnants ont attendu longtemps pour vendre. L'AMF le rappelle régulièrement : ni le capital, ni les revenus, ni la revente ne sont garantis.</p>"),
            ("Comparer les trois façons",
             "<table><tr><th></th><th>Foncière cotée</th><th>SCPI</th><th>Achat en direct</th></tr>"
             "<tr><td>Mise de départ</td><td>Le prix d'une action</td><td>Quelques centaines d'euros</td><td>Élevée</td></tr>"
             "<tr><td>Revente</td><td>Immédiate</td><td>Dépend des acheteurs</td><td>Plusieurs mois</td></tr>"
             "<tr><td>Frais d'entrée</td><td>Courtage</td><td>8 à 12 %</td><td>Notaire, travaux</td></tr>"
             "<tr><td>Prix</td><td>Très agité</td><td>Lissé, mais peut baisser</td><td>Estimé rarement</td></tr></table>"
             "<p>Un prix « lissé » n'est pas un prix plus sûr : il bouge simplement moins souvent. Et dans les trois cas, tu restes exposé au même marché immobilier.</p>"),
        ],
        retenir=["Une foncière cotée (SIIC, REIT) est une action : liquide, mais agitée et sensible aux taux.",
                 "Une SCPI n'est pas cotée : 8 à 12 % de frais d'entrée, placement de 8 à 10 ans.",
                 "Revendre des parts de SCPI suppose de trouver un acheteur : l'attente peut être longue.",
                 "Un prix lissé n'est pas un prix garanti."],
        quiz=[("Qu'est-ce qui distingue une SCPI d'une foncière cotée ?",
               ["La SCPI n'est pas cotée en Bourse", "La SCPI ne possède pas d'immeubles", "La foncière ne verse jamais de dividende", "Il n'y a aucune différence"], 0,
               "Les deux possèdent des immeubles. La foncière cotée s'échange en Bourse à tout moment ; les parts de SCPI s'achètent et se revendent auprès de la société de gestion."),
              ("Une SCPI affiche 10 % de frais d'entrée. Tu investis 5 000 €. Combien sert réellement à acheter de l'immobilier ?", ["5 000 €", "4 500 €", "4 000 €", "5 500 €"], 1,
               "10 % de 5 000 €, soit 500 €, partent en frais : 4 500 € sont investis. Il faut plusieurs années de loyers pour rattraper cet écart."),
              ("Pourquoi peut-il être long de revendre des parts de SCPI ?",
               ["Parce que la loi impose un délai de 5 ans", "Parce qu'il faut qu'un autre épargnant veuille les acheter", "Parce que les notaires sont débordés", "Parce que la Bourse est fermée le week-end"], 1,
               "Il n'y a pas de marché coté : une vente n'a lieu que s'il y a un acheteur en face. Quand beaucoup de porteurs veulent sortir, la file s'allonge.")],
        exercice=("<p>Inès a 8 000 € et aura besoin de cet argent dans <b>3 ans</b> pour un apport. Un conseiller lui propose une SCPI « qui rapporte 5 % par an » avec 10 % de frais d'entrée. "
                  "Est-ce adapté ? Fais le calcul sur 3 ans, en supposant que le prix de la part ne bouge pas.</p>",
                  "<p>Sur 8 000 €, 800 € partent en frais : 7 200 € travaillent vraiment. À 5 % par an (sur le montant versé), elle touche environ 400 € par an, soit 1 200 € en 3 ans, "
                  "moins le délai de jouissance des premiers mois. Elle a donc à peine rattrapé les frais… et rien ne garantit qu'elle pourra revendre vite ni au même prix. "
                  "Pour un besoin dans 3 ans, ce placement n'est pas adapté : sa durée conseillée est de 8 à 10 ans.</p>"),
        sources=[_AMF, _IEFP],
    ),
    dict(
        id="investissement-responsable-esg", niveau=8, minutes=7,
        titre="ISR, ESG : investir responsable sans se faire avoir",
        desc="Ce que veulent dire ESG et ISR, comment les fonds « responsables » choisissent leurs entreprises, et comment repérer le greenwashing.",
        mots="ISR définition, ESG explication, label ISR, greenwashing fonds, investissement responsable débutant, label Greenfin, SFDR article 8 9",
        sections=[
            ("Trois lettres : E, S, G",
             "<p>Les critères <b>ESG</b> jugent une entreprise autrement que par ses comptes : l'<b>environnement</b> (émissions de CO₂, déchets, eau), "
             "le <b>social</b> (conditions de travail, sécurité, sous-traitants) et la <b>gouvernance</b> (qui dirige, qui contrôle, comment sont payés les dirigeants).</p>"
             "<p>L'<b>ISR</b> (investissement socialement responsable) consiste à tenir compte de ces critères pour choisir ses placements, en plus des critères financiers.</p>"),
            ("Quatre façons de faire, très différentes",
             "<ul><li><b>L'exclusion</b> : on écarte certains secteurs (charbon, tabac, armes controversées…).</li>"
             "<li><b>Le « meilleur de la classe »</b> (best-in-class) : on garde les entreprises les mieux notées <i>de chaque secteur</i>. "
             "Un fonds de ce type peut donc contenir une compagnie pétrolière, si elle est mieux notée que ses concurrentes.</li>"
             "<li><b>Le thématique</b> : on vise un thème précis (eau, énergies renouvelables, santé).</li>"
             "<li><b>L'engagement</b> : on reste actionnaire et on vote en assemblée générale pour faire changer l'entreprise.</li></ul>"
             "<p>Deux fonds « responsables » peuvent donc n'avoir presque rien en commun.</p>"),
            ("Les labels à connaître",
             "<ul><li><b>Label ISR</b> : créé par l'État français en 2016. Depuis sa réforme de 2024, il exclut notamment les entreprises qui lancent de nouveaux projets "
             "d'exploitation de charbon, de pétrole ou de gaz.</li>"
             "<li><b>Greenfin</b> : label public centré sur la transition écologique ; il exclut les entreprises du secteur des énergies fossiles.</li>"
             "<li><b>Finansol</b> : pour l'épargne solidaire (financement d'associations, de logement social, d'insertion).</li></ul>"
             "<p>Tu verras aussi les mentions européennes « article 8 » ou « article 9 ». Ce ne sont <b>pas des labels</b> : c'est le fonds lui-même qui se classe, "
             "et ce classement européen est en cours de refonte. Ne t'y fie pas seul.</p>"),
            ("Repérer le greenwashing",
             "<p>Le <b>greenwashing</b>, c'est se donner une image verte sans que le contenu suive. Trois vérifications simples :</p>"
             "<ul><li>Regarde les <b>10 premières lignes</b> du fonds (elles sont publiées). Si tu y retrouves exactement les mêmes géants que dans un fonds ordinaire, pose-toi des questions.</li>"
             "<li>Compare les <b>frais</b> : un fonds « vert » plus cher doit le justifier.</li>"
             "<li>Lis la méthode : exclusion, meilleur de la classe, thématique ?</li></ul>"
             "<p>Côté performance, rien n'est acquis : selon les périodes, les fonds ISR font un peu mieux ou un peu moins bien que les autres. "
             "On choisit l'ISR pour ses convictions, pas pour gagner plus.</p>"),
        ],
        retenir=["ESG : environnement, social, gouvernance. L'ISR en tient compte pour choisir ses placements.",
                 "Exclusion, meilleur de la classe, thématique, engagement : quatre méthodes très différentes.",
                 "Label ISR, Greenfin, Finansol sont de vrais labels ; « article 8 » ou « article 9 » n'en sont pas.",
                 "Vérifie toujours les 10 premières lignes et les frais d'un fonds « vert »."],
        quiz=[("Que signifie le G de ESG ?", ["Gains", "Gouvernance", "Garantie", "Global"], 1,
               "ESG = environnement, social, gouvernance. La gouvernance porte sur la façon dont l'entreprise est dirigée et contrôlée."),
              ("Un fonds « meilleur de la classe » (best-in-class) peut-il contenir une compagnie pétrolière ?",
               ["Non, jamais", "Oui, si elle est mieux notée que les autres entreprises de son secteur", "Oui, mais seulement 1 %", "Seulement s'il n'a pas de label"], 1,
               "Cette méthode garde les mieux notées de chaque secteur, sans exclure de secteur. C'est pour cela qu'il faut lire la méthode du fonds."),
              ("Lequel de ces éléments n'est PAS un label ?", ["Label ISR", "Greenfin", "« Article 9 »", "Finansol"], 2,
               "« Article 8 » et « article 9 » viennent d'un règlement européen de transparence : le fonds se classe lui-même. Ce n'est pas une certification.")],
        exercice=("<p>Un fonds s'appelle « Planète Avenir Durable ». Ses frais sont de 1,8 % par an. Ses cinq premières lignes sont les cinq plus grandes entreprises technologiques américaines, "
                  "exactement comme dans un ETF monde à 0,2 % de frais. Que t'inspire ce fonds ?</p>",
                  "<p>Le nom est très vert, le contenu ne l'est pas particulièrement : ses premières lignes sont celles de n'importe quel fonds mondial. "
                  "Tu paierais 1,6 point de frais de plus chaque année pour un portefeuille presque identique. Avant d'aller plus loin : chercher s'il a un vrai label, "
                  "lire sa méthode de sélection, et comparer avec un ETF labellisé à frais bas. C'est un cas typique où le marketing est plus vert que le portefeuille.</p>"),
        sources=[_ISR, _AMF, ("Ministère de l'Écologie : le label Greenfin", "https://www.ecologie.gouv.fr/politiques-publiques/label-greenfin")],
    ),
    dict(
        id="plan-d-action", niveau=8, minutes=8,
        titre="Ton plan d'action en 7 étapes",
        desc="La synthèse de toute l'Académie : dans quel ordre faire les choses, de l'épargne de précaution au suivi annuel.",
        mots="comment commencer à investir, plan investissement débutant, étapes pour investir en bourse, par où commencer bourse, checklist investisseur débutant",
        sections=[
            ("Étapes 1 et 2 : la base",
             "<p><b>1. Sécuriser.</b> Une épargne de précaution de 3 à 6 mois de dépenses, sur un livret, disponible tout de suite. Et aucun crédit à la consommation coûteux en cours : "
             "rembourser un crédit à 15 % rapporte plus, et plus sûrement, que n'importe quel placement.</p>"
             "<p><b>2. Savoir pour quoi et pour quand.</b> Chaque somme a une date. Ce dont tu auras besoin dans moins de 3 ans ne va pas en actions. "
             "Ce qui peut attendre 10 ans ou plus peut y aller en grande partie.</p>"),
            ("Étapes 3 et 4 : les outils",
             "<p><b>3. Choisir l'enveloppe et le courtier.</b> L'enveloppe d'abord (PEA, assurance-vie, compte-titres), selon ton objectif. "
             "Puis un courtier agréé, vérifié sur REGAFI, avec des frais faibles sur les montants que <i>tu</i> investis vraiment.</p>"
             "<p><b>4. Choisir le cœur du portefeuille.</b> Pour la plupart des débutants : un ETF large, peu cher, capitalisant. "
             "Vérifie quatre choses dans son DIC : l'indice suivi, les frais courants, l'indicateur de risque et la durée conseillée.</p>"),
            ("Étapes 5 et 6 : la discipline",
             "<p><b>5. Automatiser.</b> Un virement programmé le lendemain de la paie, puis un achat régulier. Ce qui est automatique se fait ; ce qui demande une décision chaque mois finit par être repoussé.</p>"
             "<p><b>6. Écrire ses règles.</b> Trois lignes suffisent : ta répartition cible, ce que tu feras si le marché perd 30 % (rien, ou continuer les versements), "
             "et le plafond que tu t'autorises sur les paris plus risqués (par exemple 10 %).</p>"),
            ("Étape 7 : le suivi, sans y passer sa vie",
             "<p><b>7. Faire le point une fois par an.</b> Ta répartition a-t-elle dérivé ? Ta situation a-t-elle changé (emploi, logement, famille) ? Tes frais sont-ils toujours corrects ? "
             "Une demi-heure par an suffit.</p>"
             "<p>Ce que tu n'as <b>pas</b> besoin de faire : regarder les cours chaque jour, suivre l'actualité heure par heure, deviner le prochain krach. "
             "Les études le montrent depuis longtemps : les investisseurs qui touchent le moins à leur portefeuille sont souvent ceux qui s'en sortent le mieux.</p>"),
        ],
        retenir=["L'ordre compte : précaution, objectif, enveloppe, cœur du portefeuille, automatisation, règles, suivi.",
                 "Rembourser un crédit coûteux passe avant tout placement.",
                 "Ce qui est automatique se fait : programme tes versements.",
                 "Un point par an suffit ; regarder les cours tous les jours n'aide pas."],
        quiz=[("Tu as un crédit à la consommation à 15 % et 2 000 € d'économies. Quelle est la priorité ?",
               ["Acheter des actions", "Rembourser le crédit", "Acheter des cryptos", "Ouvrir une SCPI"], 1,
               "Rembourser un crédit à 15 %, c'est gagner 15 % par an à coup sûr. Aucun placement ne promet cela."),
              ("Dans quel ordre fait-on les choses ?",
               ["Choisir une action, puis ouvrir un compte, puis épargner", "Épargne de précaution, objectif, enveloppe, puis placements", "Placements, puis objectif, puis précaution", "Peu importe l'ordre"], 1,
               "On sécurise d'abord, on fixe l'objectif et l'horizon, on choisit l'enveloppe, et seulement ensuite ce qu'on met dedans."),
              ("À quelle fréquence un investisseur de long terme a-t-il besoin de faire le point ?", ["Chaque heure", "Chaque jour", "Environ une fois par an", "Jamais"], 2,
               "Un point annuel suffit pour vérifier la répartition, les frais et sa situation. Regarder trop souvent pousse surtout à trop intervenir.")],
        exercice=("<p>À toi. Sur une feuille (ou dans le cadre ci-dessous), écris ton propre plan en sept lignes : ton épargne de précaution cible en euros, ton objectif et sa date, "
                  "l'enveloppe envisagée, le type de placement de cœur, le montant mensuel, tes trois règles, et la date de ton prochain point annuel.</p>",
                  "<p>Il n'y a pas de bonne réponse unique, mais ton plan doit passer quatre tests. 1) L'argent dont tu as besoin dans moins de 3 ans n'est pas en actions. "
                  "2) Tu saurais expliquer chaque placement en deux phrases. 3) Tu as écrit ce que tu feras si le marché perd 30 %. "
                  "4) Les versements sont automatiques. Si un test échoue, reprends l'étape concernée : les chapitres 2.1, 2.5, 5.2 et 7.6 t'y aideront.</p>"),
        sources=[_AMF, _IEFP, ("Banque de France : Mes questions d'argent", "https://www.mesquestionsdargent.fr/")],
    ),
]

EXOS_8 = {
    "or-matieres-premieres": [
        N("L'or passe de 1 900 $ à 1 045 $ l'once. De combien de pour cent a-t-il baissé ?", 45, 1, "%",
          "(1 900 − 1 045) ÷ 1 900 = 0,45, soit 45 %. Une valeur refuge peut baisser fortement."),
        Q("Tu veux de l'or dans un PEA. Est-ce possible avec un ETC adossé à de l'or ?",
          ["Oui, sans limite", "Non : un ETC s'achète sur un compte-titres", "Oui, mais seulement 10 %"], 1,
          "Les ETC ne sont pas éligibles au PEA. Ils se logent dans un compte-titres ordinaire."),
        V("Un fonds qui suit le pétrole reproduit exactement le prix du baril annoncé dans les médias.", False,
          "Il détient des contrats à terme qu'il doit renouveler : sa performance peut s'écarter nettement du prix du jour."),
        Q("Quel est le principal intérêt de l'or dans un portefeuille ?",
          ["Il verse des revenus réguliers", "Il ne bouge pas comme les actions", "Il monte toujours", "Il est garanti par l'État"], 1,
          "L'or sert surtout à diversifier : il réagit souvent différemment des actions. Il ne verse aucun revenu et peut baisser."),
    ],
    "immobilier-cote-scpi": [
        Q("Une foncière cotée (SIIC), c'est :",
          ["Une action d'une entreprise qui possède des immeubles", "Un livret garanti", "Un crédit immobilier"], 0,
          "C'est une entreprise cotée dont le métier est de louer des immeubles. Son cours varie comme celui de n'importe quelle action."),
        N("Tu investis 10 000 € dans une SCPI avec 10 % de frais d'entrée. Quel montant est réellement investi ?", 9000, 1, "€",
          "10 % de 10 000 € = 1 000 € de frais. Il reste 9 000 € investis dans l'immobilier."),
        V("On peut toujours revendre ses parts de SCPI en quelques jours, au prix d'achat.", False,
          "Il faut un acheteur en face, et le prix de la part peut avoir baissé. Ni le délai ni le prix ne sont garantis."),
        Q("Le prix d'une part de SCPI bouge moins souvent que le cours d'une foncière cotée. Qu'en conclure ?",
          ["Que la SCPI est sans risque", "Que le prix est lissé, pas garanti", "Que la foncière est une arnaque"], 1,
          "La SCPI est estimée moins souvent, donc son prix paraît stable. Le risque immobilier, lui, est le même."),
    ],
    "investissement-responsable-esg": [
        Q("Lequel de ces critères relève du « S » de ESG ?",
          ["Les émissions de CO₂", "Les conditions de travail", "La rémunération des dirigeants"], 1,
          "Le S, pour social, couvre les conditions de travail, la sécurité, les relations avec les sous-traitants."),
        Q("Un fonds écarte totalement le tabac et le charbon. Quelle méthode utilise-t-il ?",
          ["L'exclusion", "Le meilleur de la classe", "L'engagement"], 0,
          "Écarter des secteurs entiers, c'est l'exclusion. Le meilleur de la classe, lui, garde tous les secteurs."),
        V("La mention « article 9 » est un label décerné par un organisme indépendant.", False,
          "C'est une catégorie d'un règlement européen de transparence : le fonds se classe lui-même. Les vrais labels sont, par exemple, le label ISR ou Greenfin."),
        Q("Quelle vérification est la plus parlante pour repérer le greenwashing ?",
          ["La couleur du logo", "Les 10 premières lignes du fonds", "Le nombre d'abonnés du gérant"], 1,
          "Les principales positions montrent ce que le fonds détient vraiment. C'est public et cela prend deux minutes."),
    ],
    "plan-d-action": [
        N("Tes dépenses sont de 1 500 € par mois. Quelle est l'épargne de précaution minimale conseillée (3 mois) ?", 4500, 1, "€",
          "3 × 1 500 € = 4 500 €. C'est le bas de la fourchette habituelle de 3 à 6 mois."),
        Q("Tu vises un ETF monde. Dans quel document vérifies-tu ses frais et sa durée conseillée ?",
          ["Le DIC", "L'IFU", "Le formulaire 2086"], 0,
          "Le DIC (document d'informations clés) donne l'indicateur de risque, les frais et la durée de détention recommandée."),
        V("Programmer un versement automatique chaque mois est moins efficace que décider soi-même, chaque mois, du bon moment.", False,
          "Chercher le bon moment échoue presque toujours, et un versement qui demande une décision finit par être repoussé."),
        Q("Que n'as-tu PAS besoin de faire en tant qu'investisseur de long terme ?",
          ["Faire un point annuel", "Regarder les cours tous les jours", "Vérifier tes frais"], 1,
          "Suivre les cours au quotidien n'améliore pas les résultats et pousse aux décisions impulsives."),
    ],
}
