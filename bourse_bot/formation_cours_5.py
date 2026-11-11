"""Version 76 : les études de cas de l'Académie, une par module, à débloquer en terminant le module.

Faits vérifiés le 11/11/2026 :
- CAC 40 : record de septembre 2000 dépassé en clôture le 2 novembre 2021 (6 927 points), soit plus de 21 ans après (Bloomberg, Option Finance).
- GameStop : jusqu'à 483 $ en séance le 28 janvier 2021, après moins de 20 $ début janvier ; Robinhood limite les achats le même jour (AP).
- FTX : faillite en novembre 2022 ; Sam Bankman-Fried condamné à 25 ans de prison en mars 2024 (AP, Reuters).
Les autres cas (Léa, l'entreprise « Atelier Lumen », la publicité) sont des personnages et des chiffres fictifs, présentés comme tels.
"""
from .formation_exos import Q, V, N

_AMF = ("AMF : l'espace épargnants", "https://www.amf-france.org/fr/espace-epargnants")
_IEFP = ("La finance pour tous", "https://www.lafinancepourtous.com/")


def _cas(id_, niveau, titre, desc, mots, sections, retenir, quiz, exercice, sources, minutes=6):
    return dict(id=id_, niveau=niveau, minutes=minutes, titre=titre, desc=desc, mots=mots, sections=sections, retenir=retenir,
                quiz=quiz, exercice=exercice, sources=sources, cas=True)


CAS = [
    _cas("cas-cac40-21-ans", 1, "Étude de cas : 21 ans pour retrouver un record",
         "Le CAC 40 a mis plus de 21 ans à dépasser son sommet de 2000. Ce que cette histoire vraie enseigne sur le temps, les dividendes et la patience.",
         "cac 40 record 2000 2021, cac 40 historique, bourse long terme exemple, dividendes réinvestis cac 40 gr",
         [("Le sommet de septembre 2000",
           "<p>En septembre 2000, en pleine bulle internet, le CAC 40 atteint un sommet proche de <b>6 920 points</b>. Trois ans plus tard, il est tombé vers 2 400 points : "
           "environ <b>−65 %</b>. Celui qui avait tout investi au sommet voyait son argent divisé par près de trois.</p>"),
          ("La longue attente",
           "<p>Il faut attendre le <b>2 novembre 2021</b> pour que le CAC 40 termine une séance au-dessus de ce record (6 927 points). "
           "Plus de <b>21 ans</b> d'attente, avec entre-temps la crise de 2008 et le krach du Covid.</p>"),
          ("Le rôle caché des dividendes",
           "<p>Ce chiffre est pourtant trompeur : le CAC 40 « classique » ne compte pas les dividendes. Avec les dividendes réinvestis (le CAC 40 GR), "
           "l'investisseur du sommet de 2000 a retrouvé sa mise bien plus tôt. Sur longue période, les dividendes pèsent lourd dans la performance totale.</p>"),
          ("Ce qu'il faut en retenir",
           "<p>Tout investir d'un coup au pire moment peut coûter des années. Investir régulièrement (chaque mois), réinvestir les dividendes et diversifier "
           "hors d'un seul pays auraient fortement réduit la douleur. Le temps aide, mais il ne fait pas de miracle si l'on entre au sommet d'une bulle.</p>")],
         ["Le CAC 40 a mis plus de 21 ans (2000 → 2021) à retrouver son record.", "Sans les dividendes, les indices « classiques » sous-estiment la performance.",
          "Tout investir au sommet d'une bulle peut coûter des années.", "Investir régulièrement et diversifier réduisent ce risque."],
         [("Quand le CAC 40 a-t-il dépassé en clôture son record de 2000 ?", ["En 2007", "En 2015", "En novembre 2021", "Jamais"], 2, "Le 2 novembre 2021, à 6 927 points."),
          ("Pourquoi le CAC 40 « classique » sous-estime-t-il la performance réelle ?", ["Il oublie les dividendes", "Il compte les frais deux fois", "Il est en dollars", "Il ne compte que 10 entreprises"], 0,
           "Les dividendes versés ne sont pas réinvestis dans l'indice classique."),
          ("Quelle méthode aurait réduit le risque d'entrer au sommet ?", ["Tout investir d'un coup", "Investir chaque mois", "Emprunter pour investir", "Attendre une rumeur"], 1,
           "Investir régulièrement évite de tout miser sur un seul moment.")],
         ("<p>Un indice tombe de 6 900 à 2 400 points. De combien de pourcents a-t-il baissé, et de combien doit-il monter pour revenir à 6 900 ?</p>",
          "<p>Baisse : (6 900 − 2 400) ÷ 6 900 ≈ <b>65 %</b>. Remontée nécessaire : 6 900 ÷ 2 400 − 1 ≈ <b>+188 %</b>. Une perte de 65 % demande presque de tripler pour s'effacer.</p>"),
         [("Bloomberg : le CAC 40 au plus haut depuis la bulle internet (2021)", "https://www.bloombergquint.com/markets/france-s-cac-40-set-for-first-record-high-since-internet-bubble"), _AMF]),

    _cas("cas-premier-investissement", 2, "Étude de cas : le premier investissement de Sami",
         "Sami, 19 ans, a 1 500 € de côté. On suit pas à pas ses décisions : épargne de précaution, enveloppe, courtier, premier ordre. Personnage fictif.",
         "premier investissement bourse exemple, comment commencer à investir, ouvrir un pea jeune, premier ordre de bourse",
         [("La situation",
           "<p>Sami (personnage fictif) a 19 ans, un job étudiant, 1 500 € sur un livret et 50 € qu'il peut mettre de côté chaque mois. "
           "Il veut « commencer la Bourse ». Première question : de quoi aura-t-il besoin dans les deux ans ?</p>"),
          ("D'abord la sécurité",
           "<p>Ses dépenses sont d'environ 400 € par mois. Il garde <b>1 200 €</b> sur son livret (3 mois de dépenses) : c'est son épargne de précaution. "
           "Il ne lui reste donc que 300 € à investir pour l'instant, plus 50 € par mois. Ce n'est pas grave : le plus important est de commencer tôt.</p>"),
          ("Le choix de l'enveloppe et du placement",
           "<p>Pour un objectif lointain, Sami ouvre un <b>PEA</b> chez un courtier agréé (vérifié sur REGAFI), avec des frais de courtage faibles sur les petits ordres. "
           "Il choisit un seul <b>ETF monde éligible au PEA</b>, capitalisant, avec des frais courants bas. Pas de crypto, pas d'action « à la mode » pour démarrer.</p>"),
          ("Le premier ordre",
           "<p>Il passe un <b>ordre à cours limité</b>, en milieu de séance, au prix affiché. Puis il programme 50 € par mois. Il écrit ses règles : "
           "« je ne vends pas si ça baisse, je regarde une fois par mois, je rééquilibre une fois par an ».</p>")],
         ["L'épargne de précaution passe avant la Bourse.", "Commencer petit mais tôt compte plus que commencer gros.",
          "Un ETF monde peu cher est un premier placement simple.", "Écrire ses règles avant d'investir protège des émotions."],
         [("Pourquoi Sami garde-t-il 1 200 € sur son livret ?", ["Pour toucher plus d'intérêts", "C'est son épargne de précaution", "C'est obligatoire", "Pour payer le courtier"], 1,
           "Il ne veut pas devoir vendre ses placements au premier imprévu."),
          ("Quel ordre choisit-il pour son premier achat ?", ["Au marché à 9 h pile", "À cours limité", "Un ordre stop", "Un CFD"], 1, "L'ordre à cours limité lui garantit son prix maximum."),
          ("Quel placement choisit-il pour démarrer ?", ["Un memecoin", "Un ETF monde éligible au PEA", "Une seule action tech", "Un CFD à levier"], 1,
           "Un seul ETF large et peu cher : simple et diversifié.")],
         ("<p>Sami investit 300 € puis 50 € par mois pendant 5 ans. Combien aura-t-il versé au total ?</p>",
          "<p>300 + 50 × 60 = <b>3 300 €</b> versés. Ce que ce montant deviendra dépendra des marchés : ce n'est jamais garanti.</p>"),
         [_AMF, _IEFP]),

    _cas("cas-analyser-une-entreprise", 3, "Étude de cas : analyser l'entreprise Atelier Lumen",
         "Une entreprise fictive, des chiffres fictifs, une vraie méthode : chiffre d'affaires, marge, dette, PER et dividende, dans l'ordre.",
         "analyser une entreprise exemple, analyse fondamentale débutant, calculer marge per exemple, lire un bilan exemple",
         [("Les chiffres de départ",
           "<p>Atelier Lumen (entreprise fictive) fabrique des luminaires. Chiffre d'affaires : 400 M€ (il y a 3 ans : 300 M€). Résultat opérationnel : 48 M€. "
           "Résultat net : 30 M€. Dette nette : 60 M€. 10 millions d'actions, cours de 45 €, dividende de 1,20 € par action.</p>"),
          ("La croissance et la marge",
           "<p>Les ventes sont passées de 300 à 400 M€ en 3 ans : <b>+33 %</b>, environ 10 % par an. La marge opérationnelle vaut 48 ÷ 400 = <b>12 %</b> : "
           "sur 100 € vendus, il reste 12 € avant intérêts et impôts. À comparer aux concurrents du secteur.</p>"),
          ("La dette et la valorisation",
           "<p>Bénéfice par action : 30 M€ ÷ 10 millions = <b>3 €</b>. PER : 45 ÷ 3 = <b>15</b>. La dette nette (60 M€) est modeste face au résultat opérationnel : "
           "l'entreprise pourrait la rembourser en un peu plus d'un an de résultats.</p>"),
          ("Le dividende et la conclusion",
           "<p>Rendement : 1,20 ÷ 45 ≈ <b>2,7 %</b>. L'entreprise distribue 1,20 € sur 3 € de bénéfice par action, soit 40 % : elle garde de quoi investir. "
           "Conclusion : une entreprise en croissance, peu endettée, à un prix raisonnable. Mais ces chiffres décrivent le passé : rien ne dit qu'elle continuera.</p>")],
         ["Analyser dans l'ordre : croissance, marge, dette, valorisation, dividende.", "Toujours comparer aux concurrents du même secteur.",
          "Un dividende raisonnable laisse de quoi investir.", "Les chiffres décrivent le passé, pas l'avenir."],
         [("Ventes de 400 M€, résultat opérationnel de 48 M€ : la marge opérationnelle est de…", ["4,8 %", "12 %", "48 %", "8,3 %"], 1, "48 ÷ 400 = 0,12, soit 12 %."),
          ("Cours de 45 €, bénéfice par action de 3 €. Le PER vaut…", ["3", "15", "45", "135"], 1, "45 ÷ 3 = 15."),
          ("Pourquoi verser 40 % de son bénéfice en dividende est plutôt sain ?", ["Ça garde de quoi investir et encaisser un coup dur", "C'est obligatoire", "Ça double le cours", "Ça supprime la dette"], 0,
           "L'entreprise rémunère ses actionnaires sans se priver de marge de manœuvre.")],
         ("<p>L'an prochain, Atelier Lumen gagne 36 M€ (toujours 10 millions d'actions) et le cours passe à 54 €. Que deviennent le bénéfice par action et le PER ?</p>",
          "<p>Bénéfice par action : 36 ÷ 10 = <b>3,60 €</b>. PER : 54 ÷ 3,60 = <b>15</b>. Le cours a monté de 20 %, exactement comme le bénéfice : l'action n'est pas devenue plus chère.</p>"),
         [_AMF, _IEFP]),

    _cas("cas-gamestop-2021", 4, "Étude de cas : GameStop, janvier 2021",
         "Quand des milliers de particuliers coordonnés sur un forum ont fait flamber une action : ce qui s'est passé, et ce que ça enseigne.",
         "gamestop 2021 explication, short squeeze explication, wallstreetbets gamestop, bulle spéculative exemple, action mème",
         [("Le contexte",
           "<p>GameStop, une chaîne américaine de magasins de jeux vidéo, est en difficulté fin 2020. Des fonds spéculatifs parient sur la baisse de son action "
           "en la <b>vendant à découvert</b> (ils vendent des actions empruntées, en espérant les racheter moins cher). Sur le forum Reddit WallStreetBets, "
           "des particuliers décident d'acheter en masse pour les contrer.</p>"),
          ("L'emballement",
           "<p>L'action, qui valait moins de 20 $ début janvier 2021, atteint jusqu'à <b>483 $</b> en séance le 28 janvier. Les vendeurs à découvert doivent racheter "
           "à n'importe quel prix pour limiter leurs pertes, ce qui fait encore monter le cours : c'est un <b>« short squeeze »</b>.</p>"),
          ("Le coup d'arrêt",
           "<p>Le 28 janvier, plusieurs courtiers, dont Robinhood, limitent les achats de l'action. Le cours s'effondre dans les jours suivants. "
           "Ceux qui ont acheté au plus haut perdent une grande partie de leur mise, tandis que les premiers arrivés et certains professionnels ont gagné gros.</p>"),
          ("Les leçons",
           "<p>Le prix peut se déconnecter complètement de la valeur de l'entreprise, dans les deux sens, plus longtemps qu'on ne l'imagine. "
           "Dans une frénésie, ce sont presque toujours les derniers arrivés qui paient. Acheter parce que « tout le monde en parle », c'est le FOMO en action.</p>")],
         ["Une vente à découvert parie sur la baisse avec des actions empruntées.", "Un short squeeze force les vendeurs à découvert à racheter, ce qui fait flamber le cours.",
          "GameStop est passé de moins de 20 $ à 483 $ en séance en janvier 2021.", "Dans une frénésie, les derniers arrivés paient presque toujours."],
         [("Vendre à découvert, c'est…", ["Parier sur la hausse", "Vendre des actions empruntées en pariant sur la baisse", "Vendre ses propres actions à perte", "Une taxe"], 1,
           "On vend des titres empruntés en espérant les racheter moins cher."),
          ("Qu'est-ce qu'un short squeeze ?", ["Une baisse lente", "Des vendeurs à découvert forcés de racheter, ce qui fait flamber le cours", "Un dividende", "Une division d'action"], 1,
           "Les rachats en urgence alimentent la hausse."),
          ("Qui a le plus souvent perdu dans l'affaire GameStop ?", ["Les premiers acheteurs", "Ceux qui ont acheté au plus haut", "Personne", "Les magasins"], 1,
           "Le cours s'est effondré après le sommet : les derniers arrivés ont subi les plus grosses pertes.")],
         ("<p>Tu achètes une action « mème » à 300 $ au plus fort de l'emballement. Quelques semaines plus tard, elle vaut 60 $. Combien as-tu perdu, en pourcentage ?</p>",
          "<p>(300 − 60) ÷ 300 = <b>80 %</b> de perte. Il faudrait que l'action soit multipliée par 5 pour revenir à ton prix d'achat.</p>"),
         [("AP : des courtiers limitent les échanges sur GameStop (28 janvier 2021)", "https://komonews.com/news/nation-world/trading-sites-restrict-stock-trading-in-gamestop-other-cos"), _AMF]),

    _cas("cas-portefeuille-lea", 5, "Étude de cas : le portefeuille de Léa, 25 ans",
         "Léa (personnage fictif) construit un portefeuille complet : objectif, répartition, cœur et satellites, rééquilibrage et règles écrites.",
         "exemple de portefeuille débutant, construire un portefeuille etf exemple, coeur satellite exemple, rééquilibrage exemple",
         [("Le profil",
           "<p>Léa (personnage fictif), 25 ans, salariée, a une épargne de précaution de 4 mois de dépenses. Elle peut investir 300 € par mois pour un objectif lointain "
           "(dans plus de 15 ans). Elle sait qu'elle supporterait mal une baisse de plus de 30 % sur l'ensemble de son épargne investie.</p>"),
          ("La répartition",
           "<p>Elle choisit <b>80 % d'actions</b> et <b>20 % de placements prudents</b> (fonds en euros d'assurance-vie). Côté actions : un <b>cœur</b> de 70 % "
           "en ETF monde dans un PEA, et 10 % de <b>satellites</b> (deux ou trois entreprises qu'elle a étudiées). Pas de crypto pour l'instant, par choix.</p>"),
          ("Le rééquilibrage",
           "<p>Après une très bonne année, ses actions pèsent 88 % au lieu de 80 %. Plutôt que de vendre, elle oriente ses versements suivants vers la partie prudente "
           "jusqu'à revenir près de sa cible. Elle vérifie sa répartition <b>une fois par an</b>, pas chaque jour.</p>"),
          ("Ses règles écrites",
           "<p>« Je ne vends pas dans la panique. Je ne mets jamais plus de 10 % sur les satellites. Je relis ces règles avant toute décision importante. "
           "Je refais le point si ma situation change (achat d'un logement, enfants…). » Ces quelques lignes valent plus qu'une prévision de marché.</p>")],
         ["Le profil (horizon, tolérance aux baisses) décide de la répartition.", "Un cœur large et peu cher, des satellites limités.",
          "Rééquilibrer en orientant les nouveaux versements évite de vendre.", "Des règles écrites protègent des décisions émotionnelles."],
         [("Pourquoi Léa garde-t-elle 20 % en placements prudents ?", ["Pour limiter la baisse possible de l'ensemble", "C'est obligatoire", "Pour payer moins de frais", "Pour la crypto"], 0,
           "Elle sait qu'elle supporterait mal une très forte baisse."),
          ("Ses actions passent de 80 % à 88 %. Que fait-elle ?", ["Elle vend tout", "Elle oriente ses nouveaux versements vers la partie prudente", "Elle achète plus d'actions", "Rien, jamais"], 1,
           "C'est une façon douce de rééquilibrer sans vendre."),
          ("À quelle fréquence vérifie-t-elle sa répartition ?", ["Chaque heure", "Chaque jour", "Une fois par an", "Jamais"], 2, "Une fois par an suffit pour un objectif long.")],
         ("<p>Le portefeuille de Léa vaut 20 000 €, dont 17 600 € en actions. Sa cible est de 80 % d'actions. Combien d'euros d'actions a-t-elle « en trop » ?</p>",
          "<p>Cible : 80 % de 20 000 = 16 000 €. Elle a <b>1 600 €</b> d'actions en trop. Avec 300 € par mois versés sur la partie prudente, il lui faudrait environ 8 mois "
          "pour revenir près de sa cible (le portefeuille grossissant en même temps), ou elle peut vendre 1 600 € d'actions en une fois.</p>"),
         [_AMF, _IEFP]),

    _cas("cas-ftx-2022", 6, "Étude de cas : la chute de FTX en 2022",
         "Une des plus grandes plateformes crypto du monde fait faillite en quelques jours : ce qui s'est passé, et pourquoi on dit « pas tes clés, pas tes cryptos ».",
         "ftx faillite explication, sam bankman-fried, plateforme crypto faillite, pas tes clés pas tes cryptos, sécurité crypto",
         [("Une plateforme géante",
           "<p>Début 2022, FTX est l'une des plus grandes plateformes d'échange de cryptomonnaies au monde, très présente dans la publicité et le sport. "
           "Des millions de clients y laissent leurs cryptos, comme sur un compte en banque.</p>"),
          ("L'effondrement en quelques jours",
           "<p>En novembre 2022, des révélations sur ses liens avec une société sœur de trading font paniquer les clients, qui veulent tous retirer leurs fonds. "
           "FTX ne peut pas tout rembourser : les retraits sont bloqués, et la société se déclare en <b>faillite</b> le même mois.</p>"),
          ("La fraude",
           "<p>L'enquête montre que l'argent des clients avait été utilisé pour d'autres activités. Son fondateur, Sam Bankman-Fried, est reconnu coupable de fraude "
           "et condamné en mars 2024 à <b>25 ans de prison</b>. Pendant ce temps, les clients ont attendu longtemps pour récupérer tout ou partie de leurs avoirs.</p>"),
          ("Les leçons",
           "<p>Laisser ses cryptos sur une plateforme, c'est lui faire confiance comme à une banque, sans les mêmes protections. D'où la formule « <b>pas tes clés, pas tes cryptos</b> ». "
           "Choisir un prestataire agréé, ne pas tout laisser au même endroit et, pour de grosses sommes, garder ses clés soi-même réduisent ce risque.</p>")],
         ["FTX a fait faillite en novembre 2022 en quelques jours.", "L'argent des clients avait été détourné : son fondateur a été condamné à 25 ans de prison.",
          "Sur une plateforme, tu dépends de sa solidité et de son honnêteté.", "« Pas tes clés, pas tes cryptos » : pour de grosses sommes, garde tes clés."],
         [("Que s'est-il passé pour les clients de FTX en novembre 2022 ?", ["Leurs retraits ont été bloqués", "Ils ont reçu un bonus", "Rien", "Leurs cryptos ont doublé"], 0,
           "La plateforme ne pouvait plus rembourser tout le monde."),
          ("« Pas tes clés, pas tes cryptos » signifie…", ["Les cryptos sont gratuites", "Si une plateforme garde tes clés, tu dépends d'elle", "Il faut deux clés", "Les cryptos sont illégales"], 1,
           "Sans tes clés privées, tu ne contrôles pas vraiment tes cryptos."),
          ("Quelle précaution réduit ce risque ?", ["Tout laisser sur une seule plateforme inconnue", "Choisir un prestataire agréé et ne pas tout mettre au même endroit", "Partager sa phrase de récupération", "Utiliser un levier"], 1,
           "Agrément, répartition et, pour de grosses sommes, portefeuille personnel.")],
         ("<p>Tu as 3 000 € de cryptos sur une seule plateforme. Propose deux mesures concrètes pour réduire le risque d'une faillite comme celle de FTX.</p>",
          "<p>Par exemple : <b>vérifier que la plateforme est agréée</b> (liste blanche de l'AMF depuis MiCA) ; <b>répartir</b> entre deux prestataires sérieux ; "
          "pour la part que tu gardes longtemps, la transférer sur un <b>portefeuille personnel</b> (idéalement matériel) dont tu notes la phrase de récupération hors ligne.</p>"),
         [("Reuters / Investment Executive : Sam Bankman-Fried condamné à 25 ans de prison", "https://www.investmentexecutive.com/news/from-the-regulators/sam-bankman-fried-sentenced-to-25-years-in-prison/"), _AMF]),

    _cas("cas-decortiquer-une-pub", 7, "Étude de cas : décortiquer une publicité de trading",
         "Une publicité fictive mais typique, analysée phrase par phrase avec tout ce que tu as appris : levier, garanties, urgence, témoignages.",
         "arnaque trading publicité, reconnaître une arnaque financière, formation trading arnaque, signaux d'alerte placement",
         [("La publicité",
           "<p>« <i>Gagnez 300 € par jour depuis votre canapé ! Notre algorithme IA a 94 % de réussite. Levier ×100 offert. Places limitées : inscrivez-vous avant minuit. "
           "Déjà 12 000 membres satisfaits.</i> » (Publicité fictive, construite à partir de pratiques réelles signalées par l'AMF.)</p>"),
          ("Les promesses impossibles",
           "<p>« 300 € par jour » et « 94 % de réussite » : aucun investisseur sérieux ne promet un gain régulier. Même l'IA de Radar Bourse, qui publie tous ses résultats, "
           "a raison environ 55 à 58 fois sur 100 sur le sens du prix. Un chiffre spectaculaire sans résultats vérifiables est un signal d'alerte.</p>"),
          ("Le piège du levier",
           "<p>« Levier ×100 offert » : avec un levier de 100, une variation de <b>1 %</b> contre toi suffit à perdre toute ta mise. En Europe, le levier offert aux particuliers "
           "sur les CFD est d'ailleurs plafonné bien en dessous : une offre à ×100 vient souvent d'un acteur non autorisé.</p>"),
          ("L'urgence et la preuve sociale",
           "<p>« Avant minuit » crée une urgence artificielle pour t'empêcher de réfléchir. « 12 000 membres satisfaits » ne prouve rien. Bon réflexe : chercher le nom "
           "sur les <b>listes noires de l'AMF</b> et le registre REGAFI, et ne jamais transmettre ses papiers ou faire un virement sur la base d'une publicité.</p>")],
         ["Un gain régulier promis est un signal d'alerte.", "Avec un levier de 100, 1 % contre toi efface toute la mise.",
          "L'urgence et les témoignages servent à t'empêcher de réfléchir.", "Vérifie toujours les listes noires de l'AMF avant d'agir."],
         [("Avec un levier de 100, quelle baisse suffit à perdre toute la mise ?", ["1 %", "10 %", "50 %", "100 %"], 0, "100 × 1 % = 100 %."),
          ("« 94 % de réussite » sans résultats publiés, c'est…", ["Une preuve", "Un signal d'alerte", "Une obligation légale", "Normal"], 1,
           "Un service sérieux publie ses résultats, ratés compris."),
          ("« Inscrivez-vous avant minuit » sert surtout à…", ["T'informer", "T'empêcher de prendre le temps de vérifier", "Respecter la loi", "Réduire les frais"], 1,
           "L'urgence artificielle est une technique classique de manipulation.")],
         ("<p>Relève dans la publicité au moins quatre signaux d'alerte et, pour chacun, le chapitre de l'Académie qui l'explique.</p>",
          "<p>Gain régulier promis (<b>Rendement et risque</b>) ; taux de réussite invérifiable (<b>Utiliser l'IA intelligemment</b>) ; levier ×100 (<b>Effet de levier, options et CFD</b>) ; "
          "urgence et témoignages (<b>Arnaques et pièges</b>, <b>Psychologie de l'investisseur</b>).</p>"),
         [_AMF, ("AMF : listes noires et mises en garde", "https://www.amf-france.org/fr/espace-epargnants")]),
]

EXOS_CAS = {
    "cas-cac40-21-ans": [
        N("Un sommet en 2000, dépassé en 2021 : combien d'années d'attente, environ ?", 21, 0, "ans", "De septembre 2000 à novembre 2021 : un peu plus de 21 ans."),
        V("Celui qui avait acheté le CAC 40 au sommet de 2000 a dû attendre jusqu'en 2021 pour retrouver sa mise, même avec les dividendes réinvestis.", False,
          "Avec les dividendes réinvestis, il l'a retrouvée bien plus tôt : l'indice classique les ignore."),
        Q("Dans ce cas, qu'est-ce qui aurait le plus réduit la douleur ?", ["Tout investir au sommet", "Investir chaque mois et diversifier hors de France", "Vendre au plus bas"], 1,
          "Investir régulièrement et diversifier réduisent l'impact d'un mauvais point d'entrée."),
        V("Le temps garantit toujours de retrouver sa mise en quelques années.", False, "Le cas du CAC 40 montre que l'attente peut durer plus de 20 ans."),
    ],
    "cas-premier-investissement": [
        N("Les dépenses de Sami sont de 400 € par mois. Combien garde-t-il pour 3 mois de précaution, en € ?", 1200, 0, "€", "3 × 400 € = 1 200 €."),
        V("Avec seulement 300 € à investir, ça ne vaut pas la peine de commencer.", False, "Commencer tôt, même petit, est un avantage grâce aux intérêts composés."),
        Q("Comment Sami vérifie-t-il que son courtier est autorisé ?", ["Sur le registre REGAFI", "Sur Instagram", "En appelant un ami"], 0, "REGAFI et l'AMF sont les sources officielles."),
        Q("Quelle règle écrite l'aide le plus en cas de baisse ?", ["« Je ne vends pas si ça baisse »", "« J'achète des CFD »", "« Je regarde toutes les heures »"], 0,
          "Une règle décidée au calme évite une vente en panique."),
    ],
    "cas-analyser-une-entreprise": [
        N("Les ventes passent de 300 à 400 M€. Quelle hausse, en % (arrondie) ?", 33, 1, "%", "(400 − 300) ÷ 300 ≈ 0,333, soit environ 33 %."),
        N("Résultat opérationnel 48 M€, ventes 400 M€ : marge opérationnelle en % ?", 12, 0.1, "%", "48 ÷ 400 = 12 %."),
        N("Résultat net 30 M€, 10 millions d'actions, cours de 45 € : quel est le PER ?", 15, 0.1, "", "Bénéfice par action = 3 € ; 45 ÷ 3 = 15."),
        N("Dividende de 1,20 € pour un cours de 45 € : rendement en % (une décimale) ?", 2.7, 0.05, "%", "1,20 ÷ 45 ≈ 2,7 %."),
    ],
    "cas-gamestop-2021": [
        Q("Que font les fonds qui vendent GameStop à découvert ?", ["Ils parient sur la hausse", "Ils parient sur la baisse avec des actions empruntées", "Ils achètent l'entreprise"], 1,
          "Ils vendent des actions empruntées en espérant les racheter moins cher."),
        N("De moins de 20 $ à 483 $ : par combien le cours a-t-il été multiplié au moins (arrondi) ?", 24, 0.5, "fois", "483 ÷ 20 ≈ 24 : plus de 24 fois en quelques semaines."),
        V("Le 28 janvier 2021, plusieurs courtiers, dont Robinhood, ont limité les achats de l'action.", True, "Ce coup d'arrêt a précédé l'effondrement du cours."),
        Q("Quel biais pousse à acheter une action parce que « tout le monde en parle » ?", ["Le FOMO", "L'aversion à la perte", "La règle de 72"], 0, "La peur de rater pousse à entrer près du sommet."),
    ],
    "cas-portefeuille-lea": [
        N("Léa vise 80 % d'actions. Sur 10 000 €, combien d'euros en actions ?", 8000, 0, "€", "80 % de 10 000 € = 8 000 €."),
        Q("Dans le portefeuille de Léa, quelle part va aux satellites ?", ["10 %", "50 %", "80 %"], 0, "Le cœur (ETF monde) pèse 70 %, les satellites 10 %, la partie prudente 20 %."),
        V("Pour rééquilibrer, Léa est obligée de vendre une partie de ses actions.", False, "Elle peut aussi orienter ses nouveaux versements vers la partie en retard."),
        Q("Quand Léa doit-elle revoir ses règles ?", ["Si sa situation change (logement, enfants…)", "Chaque fois que le marché baisse de 1 %", "Jamais"], 0,
          "Ses règles suivent sa vie, pas l'humeur du marché."),
    ],
    "cas-ftx-2022": [
        V("En novembre 2022, les clients de FTX ont pu retirer tout leur argent sans problème.", False, "Les retraits ont été bloqués, puis la plateforme a fait faillite."),
        Q("Pourquoi FTX n'a-t-elle pas pu rembourser ses clients ?", ["Leur argent avait été utilisé pour d'autres activités", "À cause d'un bug", "À cause des impôts"], 0,
          "L'enquête a montré un détournement des fonds des clients."),
        N("À combien d'années de prison le fondateur de FTX a-t-il été condamné ?", 25, 0, "ans", "Sam Bankman-Fried a été condamné à 25 ans de prison en mars 2024."),
        Q("Pour une grosse somme en crypto gardée longtemps, quelle solution réduit le risque de plateforme ?", ["Un portefeuille personnel matériel", "Tout laisser sur une plateforme inconnue", "Un CFD"], 0,
          "Avec un portefeuille matériel, c'est toi qui gardes les clés."),
    ],
    "cas-decortiquer-une-pub": [
        V("Un investissement sérieux peut promettre « 300 € par jour ».", False, "Aucun placement sérieux ne promet un gain régulier."),
        N("Avec un levier de 100, quelle baisse (en %) efface toute la mise ?", 1, 0, "%", "100 × 1 % = 100 % de la mise."),
        Q("Que veut provoquer « Places limitées, avant minuit » ?", ["Une décision précipitée", "Une réflexion calme", "Une baisse des frais"], 0, "L'urgence empêche de vérifier."),
        Q("Premier réflexe face à cette publicité ?", ["Vérifier les listes noires de l'AMF", "S'inscrire pour voir", "Envoyer ses papiers d'identité"], 0,
          "Toujours vérifier avant d'agir, et ne rien transmettre."),
    ],
}
