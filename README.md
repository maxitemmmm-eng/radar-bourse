# 📈 Radar Bourse

Un site qui analyse les actions françaises, les actions américaines, les principales cryptos,
des ETF et les titres en tendance. Pour chaque titre : cours actuel, score technique sur 100,
signal, **probabilité de hausse à 20 séances (~1 mois)**, fourchette de prix probable,
graphique avec la prévision, raisons du signal, et résultat d'un backtest.

> ⚠️ **Outil éducatif, pas un conseil en investissement.** Aucun programme ne prédit la Bourse de façon
> fiable. Le site affiche lui-même sa précision pour que tu saches quand ne pas le croire.

## En bref : ce que tu as à faire

**Presque rien.** Une fois en ligne, tout tourne tout seul :
- **chaque heure**, le site se met à jour avec les derniers cours ;
- **chaque soir**, les IA sont réévaluées et l'historique des prévisions est sauvegardé ;
- **chaque nuit**, l'IA s'entraîne sur GitHub et retient tout ce qu'elle apprend ;
- **toutes les 6 heures**, une surveillance relance ce qui serait en panne, et t'envoie un e-mail si ça dure.

Pour tout le reste, il n'y a qu'**un seul fichier** : double-clique sur **`Radar Bourse.bat`**, puis tape un numéro dans le menu.

| N° | Choix du menu | Quand l'utiliser |
|---|---|---|
| 1 | Installer une nouvelle version reçue en zip | Quand tu reçois `radar_bourse_mise_a_jour.zip` (laisse-le dans Téléchargements) |
| 2 | Remettre le site en ligne | Après une modification faite à la main |
| 3 | Entraîner l'IA sur ce PC | Facultatif : en plus de l'entraînement automatique de chaque nuit |
| 4 | Mon bilan privé | Pour savoir combien de fois les IA ont vraiment eu raison |
| 5 | Voir le site sur ce PC | Pour regarder sans passer par Internet |
| 6 à 9 | Google, statistiques, nom de domaine, Telegram | Réglages facultatifs, à faire une fois |

Les anciens fichiers `.bat` marchent toujours ; le menu les regroupe.

## Installation (une seule fois)

1. Installe Python 3.10 ou plus récent depuis python.org (sur Windows, coche **« Add Python to PATH »**).
2. Double-clique sur **`lancer.bat`**. La première fois, il installe ce qu'il faut (1 à 2 minutes).

Le site s'ouvre tout seul dans ton navigateur (`site/index.html`). Il faut Internet pour les vrais cours.

## Commandes (dans un terminal ouvert dans ce dossier)

| Commande | Ce que ça fait |
|---|---|
| `python -m bourse_bot` | Génère le site complet (tous les marchés) et l'ouvre |
| `python -m bourse_bot site --marches crypto us` | Seulement certains marchés (`fr`, `us`, `crypto`, `etf`, `tendances`) |
| `python -m bourse_bot analyse NVDA` | Fiche d'un titre dans le terminal (`MC.PA`, `BTC-USD`…) |
| `python -m bourse_bot backtest BTC-USD --capital 500 --annees 3` | « Si j'avais suivi le radar, combien j'aurais ? » |
| `python -m bourse_bot --demo` | Données fictives, pour tester sans Internet |
| `python -m bourse_bot --sans-ml` | Plus rapide, sans le modèle de prédiction |

## Mettre à jour le site en ligne

- **Les données** (cours, prévisions, actus) se mettent à jour toutes seules, chaque heure en semaine.
- **Une nouvelle version du code** : extrais le nouveau zip **dans le même dossier** que l'ancien
  (accepte de remplacer les fichiers), puis double-clique sur `mettre_en_ligne.bat`. Il ne repose pas
  les questions et envoie la nouvelle version ; le site est à jour 3 à 6 minutes après.

## Ce qu'affiche le site

- **Signaux forts** : les titres où le modèle est confiant ET la tendance technique haussière,
  avec leur taux de réussite réellement mesuré sur l'historique.
- **Actualités** : derniers titres de presse par action et pour le marché, avec leur tonalité
  (positive, neutre, négative). La tonalité est informative : elle n'entre pas dans la probabilité.
- **Simulateur** dans chaque fiche : choisis un montant et une durée, le site rejoue 4 000 scénarios
  tirés du vrai historique du titre et montre l'éventail des résultats et le risque de perte.
- **Météo du marché** : part des titres en tendance haussière, probabilité moyenne, signaux d'achat
  et de vente, nombre de configurations de décollage.

- **Bandeau des marchés** : CAC 40, Euro Stoxx 50, S&P 500, Nasdaq, Bitcoin, avec la variation du jour.
- **Ce que le radar prévoit** : les plus fortes probabilités de hausse et les « configurations de décollage »
  (cours proche du plus haut annuel, volatilité comprimée, volumes en hausse, tendance haussière…).
- **Peut-on lui faire confiance ?** : précision du modèle testé sur des périodes qu'il n'a jamais vues,
  comparée à une réponse naïve, table de calibration (quand il dit 60 %, ça monte vraiment combien de fois ?)
  et **suivi réel** : chaque prédiction est enregistrée dans `historique/predictions.csv` puis vérifiée
  20 séances plus tard. Plus tu relances le bot, plus ce suivi devient parlant.
- **Tous les titres** : tableau filtrable et triable. Clique sur un titre pour ouvrir sa fiche :
  graphique en chandeliers, moyennes 50 et 200 jours, **cône de prévision** (médiane + fourchette
  2 chances sur 3), raisons du signal, stop-loss et objectif indicatifs, backtest sur 3 ans.

## Comment le modèle fonctionne

1. **Données** : 5 ans de cours quotidiens (Yahoo Finance, gratuit), téléchargés en un seul lot avec
   3 tentatives. Si Internet coupe, le dernier cache est réutilisé.
2. **19 indicateurs** par titre (tendance, RSI, MACD, ADX, Bollinger, volumes, force relative face à l'indice…)
   + des **classements entre titres** (ex : fait partie des 20 % qui ont le plus monté sur 3 mois).
3. **Deux modèles combinés** : gradient boosting + régression logistique, moyennés pour plus de stabilité,
   avec des variables de « régime » (l'indice du marché est-il haussier, agité ?).
4. **Probabilités calibrées** : elles sont recalées sur les fréquences réellement observées hors
   échantillon. « 60 % » veut dire « dans des cas semblables, ça a monté environ 6 fois sur 10 ».
5. **Validation walk-forward avec purge** : le modèle est entraîné sur le passé et testé sur la période
   suivante, sans jamais voir le futur. C'est ce chiffre que le site affiche.
6. **Cône de prévision** : le centre vient du rendement réellement observé dans l'historique quand le
   modèle donnait cette probabilité ; la largeur vient de la volatilité du titre.

### Comment lire la précision

Sur les vrais marchés, attends-toi à **50 à 55 % de bonnes directions**. C'est le niveau normal, même
pour des professionnels. Si l'AUC est proche de 0,50, les probabilités ne valent pas mieux qu'une pièce,
et le site le dit. S'il annonçait un jour 80 %, ce serait un bug, pas un trésor.

## Mettre le site en ligne, toujours actif

Suis le guide **`METTRE_EN_LIGNE.md`** : le site est hébergé gratuitement sur GitHub Pages et se
met à jour tout seul (cryptos en direct, prévisions chaque heure), même PC éteint.

## Cours en direct

Quand la page est ouverte, elle reçoit les prix en direct : cryptos via Binance (sans inscription),
actions US via Finnhub si une clé est configurée (`FINNHUB_KEY`). Les actions françaises n'ont pas de
source gratuite en temps réel : elles sont rafraîchies à chaque mise à jour du site.

## Espace simulation (à combien dans un mois ?)

Pour chaque action et crypto : un **scénario bas, central et haut** à 1 semaine, 2 semaines et
1 mois, sur une barre visuelle. Les fourchettes sont **apprises par l'IA** (modèles de quantiles),
puis **corrigées automatiquement** (méthode conformale) pour contenir le vrai prix 8 fois sur 10.
Le taux réellement obtenu sur des cas jamais vus est affiché en gros, avec un avertissement très
visible : environ 2 fois sur 10, le prix sort de la fourchette.
Le **défi pronostic** permet de parier (sans argent) contre le radar et de comparer les scores.

## Pour les visiteurs

- **Carte du marché** colorée (jour, mois, 3 mois), graphiques avec filigrane, curseur aimanté,
  zones en dégradé et **mode ligne** pour les débutants.
- **Dates de résultats** : un avertissement apparaît quand une entreprise publie ses résultats
  dans les 30 jours (forte volatilité possible).
- **Mise à jour automatique** : la page se recharge seule quand de nouvelles prévisions arrivent,
  si le visiteur n'est pas en train de lire une fiche.
- **Portefeuille virtuel** : 10 000 € fictifs pour s'entraîner sans risque (gardé dans le navigateur).
- **Favoris**, bouton **Partager**, installation sur téléphone.
- **Apprendre la Bourse** : 8 mini-cours illustrés avec un quiz (actions, cryptos, bougies, tendances,
  RSI/MACD, gestion du risque, pièges, long terme) + un glossaire.
- **Alertes Telegram** (facultatif) : chaque soir, le robot publie les signaux forts sur ta chaîne.
  Pour l'activer plus tard : double-clique sur `alertes_telegram.bat`.

# Historique des versions

## Version 33 : 169 titres, filtre de recherche, prévisions honnêtes à un an

- **169 titres au lieu de 99** :
  - toutes les grandes valeurs de Paris (Engie, Michelin, Thales, Renault, Danone…) ;
  - 40 grandes actions américaines de plus (Coca-Cola, McDonald's, Boeing, Mastercard, Coinbase…) ;
  - 12 européennes de plus (BASF, Rheinmetall, Volkswagen…).
  La plupart servaient déjà à l'apprentissage de l'IA : le calcul ne s'alourdit presque pas.
- **Filtre « selon mes critères »** dans « Tous les titres » : agitation prévue, avis des IA, face à son marché, dividende, PER.
- **Chiffres d'entreprise mis en cache 24 h** et **actus mises en cache 2 h** : avec plus de titres, on reste poli avec Yahoo et Finnhub, et la mise à jour reste rapide.
- **Questions Google sur chaque fiche** :
  - « Quel est le dividende de X ? » et « Quel est le PER de X ? » ;
  - « Quelle est la prévision pour X en 2026 ? ». La réponse est honnête : personne ne sait à un an. On donne la prévision à un mois et l'écart habituel du prix sur un an, tiré de sa volatilité.
- **Nouvelle page « Prévisions 2026 »** : tous les titres avec leur agitation prévue, leurs chances à un mois et leur écart habituel sur un an.
- **16 comparaisons de plus** : Coca-Cola ou Pepsi, Visa ou Mastercard, Renault ou Stellantis, Boeing ou Airbus… Le dividende et le PER s'ajoutent dans les tableaux.
- **Savoir dire « baisse » (couche « climat du marché »)** : le calcul du soir teste une couche qui apprend quand dire « baisse » à partir de l'avis de l'IA et de l'état du marché (tendance de l'indice, VIX, taux, crédit, part des titres en hausse).
  - Elle est testée année par année, en n'apprenant que sur les années d'avant.
  - Elle n'est utilisée que si elle donne plus de bonnes directions de façon prouvée.
  - Le résultat s'affiche sur le site dans « Savoir dire « baisse » », adoptée ou non.
- **Campagne Google** (`campagne_google.bat`, ou le menu), à lancer une fois par semaine :
  - il vérifie les pages en ligne comme Google (titre, description, titre principal, page bloquée) ;
  - il rappelle les tâches de la semaine du plan ;
  - il ouvre Search Console, copie une par une les adresses des 10 pages du jour (il suffit de les coller dans la barre d'inspection) et se souvient de celles déjà envoyées.
  Son premier passage a trouvé des descriptions trop longues et un titre de 106 caractères : c'est corrigé.
- **Objectif 3000 sur 5000** : le test essaie aussi 4 autres façons de décider « hausse » ou « baisse » sur les mêmes cas, chacune apprise seulement sur les années d'avant. Il dit combien de fois chacune répond « baisse », et comment elle s'en sort les années de baisse (2008, 2011, 2015, 2018, 2020, 2022). Les 4 façons :
  - une règle de tendance du marché ;
  - un modèle du climat économique ;
  - deux combinaisons apprises.
  Une méthode n'ira sur le site que si elle fait nettement mieux sur les vrais cours.
- **Prudence par marché, sur le site** : ton test sur les vrais cours a donné 2793 sur 5000 avec cette méthode, contre 2733 pour l'IA seule et 2763 pour « toujours hausse ».
  - Sur un marché où l'avis des IA n'a pas fait mieux que la tendance habituelle de ce marché (sur des années jamais vues), le site publie cette tendance (« il a fini plus haut N mois sur 100 »). Il l'affiche clairement comme telle, avec l'avis brut des IA pour info.
  - Le choix des marchés est refait chaque soir.
  - Le test d'agitation est corrigé : les cours figés faussaient la moyenne (« 261612 % »). Il affiche maintenant l'erreur habituelle (médiane) et la part des cas où l'IA est plus proche que la méthode simple (62,5 % sur tes vrais cours).
  - Les avertissements techniques qui encombraient la fenêtre sont masqués.
- **Objectif 2800 sur 5000, et une IA qui ose dire « baisse »** (d'après ton test sur les vrais cours : 2766 sur 5000, mais seulement 49 % de justes sur les cryptos et environ 10 points perdus en 2018, 2022 et 2026) :
  - **Bug corrigé** : sur les versions récentes de scikit-learn, un indicateur vide sur une période (par exemple le « fear & greed », qui n'existe que depuis 2018) faisait planter les tests d'agitation et de méthodes. Il pouvait aussi faire retomber l'agitation du site sur la méthode simple sans prévenir. Ces colonnes vides sont maintenant écartées avant l'apprentissage.
  - **Le test compare maintenant 9 façons de décider**, dont :
    - une décision apprise par marché (l'avis de l'IA croisé avec le type de marché) ;
    - un seuil appris pour chaque marché, qui laisse l'IA dire « baisse » bien plus souvent ;
    - une « prudence » sur les marchés où l'IA n'a pas fait ses preuves ;
    - un repère honnête, qui répond ce qui arrivait le plus souvent.
    Chacune n'apprend que sur les années d'avant. Le test indique celles qui atteignent 2800.
  - **Sur le site**, la couche « climat du marché » testée chaque soir peut apprendre que l'IA vaut moins sur les cryptos. Elle n'est utilisée que si elle donne plus de bonnes directions de façon prouvée.
- **Plus de visibilité** :
  - **Classements du jour** (`classements/…`), pour les recherches très tapées : actions à fort dividende, actions les moins agitées prévues, cryptos les plus volatiles, actions qui pourraient battre leur indice, PER les plus bas. Une page « Classements » est ajoutée au menu.
  - **Flux RSS** (`flux.xml`) : le point du jour et les bilans du mois, repris par les lecteurs de flux et les agrégateurs.
  - **Encadré à intégrer** : chaque fiche donne un code à copier pour afficher le titre (cours, agitation, avis des IA) sur un autre site, avec un lien vers la fiche. Chaque site qui l'utilise crée un lien vers Radar Bourse, ce qui compte beaucoup pour Google. Les encadrés ne sont pas indexés, pour ne pas faire de doublons. Les conditions d'utilisation autorisent cet encadré.
- **Toncoin et cryptos à trous** : si Yahoo renvoie une série trop courte ou figée pour une crypto, le site prend maintenant l'historique de Binance, au lieu d'ignorer le titre. C'était pour ça que Toncoin manquait dans ton test.
- **Balises essentielles ajoutées** sur toutes les pages :
  - `author`, `application-name`, `apple-mobile-web-app-title` ;
  - `format-detection` : sur iPhone, les prix ne se transforment plus en numéros de téléphone ;
  - `og:image:alt` et `twitter:image:alt`, la description de l'image de partage ;
  - `robots` complété (`max-snippet:-1`, `max-video-preview:-1`).
  Les pages anglaises ont maintenant des données structurées (WebPage). Sur les fiches d'actions, l'entreprise est décrite comme une `Corporation` avec son symbole boursier. Vérifié : aucune balise en double, et les données structurées sont valides.
- **Titres Google retravaillés** pour coller à ce que les gens tapent : « Action LVMH (MC.PA) : cours, prévision et analyse IA », « Bitcoin (BTC) : cours, prévision et analyse IA ». L'accueil devient « Prévisions bourse et crypto par IA, gratuites et vérifiées ».
- **Test sur 5000 cas** (`tester_ia.bat`, ou choix 5 du menu) : l'IA s'entraîne sur le passé, prévoit des mois qu'elle n'a jamais vus, puis on tire 5000 cas au hasard et on compte ses bonnes réponses. Il mesure trois choses : le sens du prix, « mieux que son marché » et l'agitation, chaque fois comparées à une référence simple, avec la marge d'erreur, et détaillé par marché et par année. Il est calculé avec les vrais cours, sur ton PC, et le rapport reste dans « rapports ».
- **Correction du suivi** : un titre retiré de la cote (cours figé) avait été enregistré à la date de son dernier cours (février 2025). La page « Résultats réels » annonçait donc « premiers résultats vers mars 2025 ». Ces lignes fantômes sont maintenant ignorées, et une prévision n'est plus jamais enregistrée sur un cours de plus de 10 jours.
- **Corrections** :
  - les numéros internes de Yahoo n'apparaissent plus dans le tableau des titres, ni dans les dernières prévisions vérifiées ;
  - les pages Google (françaises et anglaises) ont maintenant une zone principale et un pied de page bien marqués, pour les lecteurs d'écran (vérifié avec axe : aucune erreur) ;
  - le filtre d'agitation s'adapte aux titres du jour (un tiers des titres dans chaque groupe), au lieu de seuils fixes qui pouvaient ne rien donner.

## Version 32 : deux nouvelles façons d'apprendre, et plus de contradictions

- **« Comparer les titres entre eux »** : l'IA peut voir chaque indicateur comme une place parmi les titres du jour (« RSI parmi les plus hauts ») au lieu d'un chiffre brut. Ça marche pareil en marché calme ou agité. Cette façon de prévoir est testée chaque soir, et l'entraînement de la nuit l'explore aussi.
- **« Ignorer les petits mouvements »** : à l'entraînement, l'IA peut laisser de côté les cas où le titre a fini presque pareil que les autres (du pur pile ou face). Seul l'entraînement de la nuit l'essaie, avec 20 %, 35 % ou 50 % des cas retirés.
- Comme toujours, ces options ne sont adoptées que si elles font mieux sur les vraies données.
- **Bilan du mois** : une page par mois (`bilan/2026-10.html`…) avec le score honnête, la comparaison avec la référence naïve, l'agitation prévue contre la réalité, les plus beaux coups ET les pires ratés. Les pages sont reliées depuis « Résultats réels ».
- **Pages « X ou Y ? »** : 31 comparaisons très recherchées sur Google (or ou bitcoin, MSCI World ou S&P 500, LVMH ou Hermès, Nvidia ou AMD…), mises à jour automatiquement. Elles sont reliées depuis les fiches, avec une page « Comparer » dans le menu.
- **Image de partage par titre** : partager la page d'un titre affiche maintenant sa propre carte (prix, variation, mini-courbe, agitation prévue, avis des IA).
- **Accueil** : « Ce que le radar prévoit » remonte juste après la météo du marché. Le texte d'accueil dit ce que les IA prévoient le mieux (l'agitation, et la comparaison avec son marché). Dans « Chances de hausse », les titres avec un avis net passent en premier.
- **Corrections** :
  - « le 1 septembre » devient « le 1er septembre » ;
  - quand les IA n'ont pas d'avis net, la fiche, le résumé en 3 points et les pages Google (français et anglais) n'affichent plus en même temps « 58 chances sur 100 de monter ». Le chiffre brut est présenté comme tel ;
  - dans les alertes Telegram, les cryptos n'affichent plus le numéro interne de Yahoo (TON-USD au lieu de TON11419-USD).

## Version 31 : de nouvelles façons de prévoir, testées chaque soir

- **IA « classement »** : au lieu de deviner « monte / baisse », elle apprend à classer les titres du plus prometteur au moins prometteur. C'est souvent plus stable en bourse.
- **IA « par ambiance »** : une IA pour les marchés calmes, une autre pour les marchés nerveux (selon le VIX).
- **Nouveaux indicateurs** :
  - l'élan ajusté au risque (hausse divisée par l'agitation) ;
  - le rang de chaque titre dans sa famille (actions ou cryptos).
- **IA n°2 plus sobre** : une version avec moins d'indicateurs est essayée, et gardée seulement si elle fait mieux.
- **Prévision « mieux que son marché »** : la version classement est essayée et gardée seulement si elle fait mieux.
- **Journal du ton des actus** : chaque jour, il est enregistré pour qu'on puisse vérifier plus tard s'il aide vraiment.
- **Entraînement de la nuit** : il explore aussi ces nouvelles options. Le dimanche, il teste en plus un univers d'apprentissage élargi (environ 80 titres de plus).
- **Site** : une carte « Les façons de prévoir testées » montre honnêtement le score de chaque recette.
- **Règle d'or inchangée** : une nouveauté n'est adoptée que si elle prouve qu'elle fait mieux sur les vraies données. Sinon, l'ancienne recette reste.

## Version 30 : finitions graphiques

- **Logo radar dans l'en-tête**, le même dessin que l'icône de l'onglet. Il est masqué sur les très petits écrans.
- **Mini-courbes plus lisibles** : une aire légère sous la courbe et un point final bien détaché.
- **Carte des chances et des risques** : les quatre coins sont expliqués en mots (« Plus de chances, et calme »…), une vraie légende dessinée montre point plein / rond vide, et le point survolé est mis en évidence.
- **Arène** : une ligne pointillée marque le prix du jour mystère, et une étiquette affiche le résultat final (« +9,0 % ») au bout de la courbe.
- **Fiche** : la ligne de confiance ne commence plus par un « · » orphelin.
- **Signal technique** : une bulle d'aide explique qu'il est indépendant de l'avis des IA.
- **Corrections** :
  - en mode simple, les prévisions prennent toute la largeur ;
  - dans l'agenda, les dates ne se coupent plus en deux ;
  - sur mobile, le nom du site ne passe plus à la ligne.

## Version 29 : l'IA apprend toute seule, chaque nuit

- **Entraînement automatique** (nouvelle tâche GitHub « Entraînement automatique de l'IA ») : chaque nuit à 2 h 40 UTC, un entraînement « rapide » tourne sur GitHub avec les vrais cours ; le dimanche, c'est un entraînement « normal », avec l'examen des crises et des horizons.
  - La recherche est guidée par la mémoire de tous les essais passés, et la mémoire grandit chaque nuit.
  - Une nouvelle recette n'est adoptée que si elle fait mieux de façon prouvée. Dans ce cas, le site est mis à jour tout de suite.
  - Tu n'as rien à faire. Tu peux toujours lancer `entrainement_ia.bat` sur ton PC en plus ; les deux mémoires sont fusionnées.
- **Plus aucune connaissance perdue.** La mise à jour du soir fusionne maintenant ce qu'elle enregistre avec ce que les entraînements ont appris entre-temps, au lieu de l'écraser.
- **Surveillance qui répare toute seule** (toutes les 6 h) :
  - si le site n'a pas été mis à jour depuis 6 h, la mise à jour est relancée ;
  - après 26 h, GitHub t'envoie aussi un e-mail ;
  - si l'IA n'a pas été entraînée depuis 3 jours, l'entraînement est relancé.
- **Robustesse.** Une mise à jour interrompue au milieu d'un envoi ne bloque plus les suivantes.

## Version 28 : revue complète du site

**Corrections**
- **Accueil.** Sous le graphique du jour, il n'y a plus qu'un résumé en 3 points et un lien vers la fiche, au lieu de tout répéter (3 500 px de moins sur mobile).
- **Fiche.** L'agitation prévue n'apparaît plus deux fois. Sa fiabilité est donnée dans le résumé en 3 points.
- **Mini-robots.** Les cartes sont plus compactes : un verdict clair, les signaux du jour, et « Comment il raisonne » qui se déplie. Une phrase trop affirmative sur les fonds professionnels a été corrigée.
- **Arène.** Une invitation remplace le grand cadre vide avant la première partie.
- **Pourcentages.** Ils ne passent plus à la ligne dans les listes sur mobile.

**Ajouts**
- **Page publique « Les mini-robots »** (robots.html). On y trouve leurs règles, leur vrai palmarès et leurs signaux du jour, avec des liens vers chaque titre. Elle est mise à jour chaque jour, ajoutée au plan du site et reliée depuis toutes les pages.
- **Bouton « haut de page »** quand on descend loin dans la page, surtout utile sur mobile.
- **Touche « / »** sur ordinateur, pour aller directement à la recherche.

## Version 27 : l'IA dit ce qu'elle sait vraiment faire

Cette version part des **vrais résultats** du site en ligne, qui montrent trois choses :
- Pour deviner si un prix va monter, les IA sont à peine meilleures que le hasard.
- Pour dire si un titre fera mieux que son marché, elles sont un peu meilleures.
- Pour prévoir l'agitation (de combien un prix va bouger), elles sont nettement meilleures.

Le site s'organise maintenant autour de ça :
- **Résumé en 3 points sur chaque fiche** : agitation prévue, face à son marché, sens du prix. Chaque point affiche sa fiabilité réelle (« juste X fois sur 100, hasard : Y »).
- **« Pas d'avis » par marché.** Si, sur un marché (par exemple les cryptos), même les avis tranchés n'ont pas fait mieux que « toujours la même réponse », le site ne donne plus d'avis de direction sur ce marché, et il explique pourquoi.
- **« Pas d'avis net » aussi pour la comparaison avec le marché**, calculé de la même façon.
- **Classement par défaut** : le site ouvre sur la compétence la plus fiable des IA.
- **Deux nouvelles recettes testées chaque soir** : indicateurs de base + avis des robots, et indicateurs de base + économie. Elles ne sont adoptées que si elles font mieux de façon prouvée.
- **Entraînement.** Le résultat est maintenant **toujours enregistré sur ton PC**, même si tu fermes la fenêtre ou choisis « Ne rien envoyer ». La prochaine mise en ligne l'envoie automatiquement. Avant, tes entraînements n'arrivaient jamais sur le site.
- **Corrections.**
  - Les numéros internes de Yahoo n'apparaissent plus (« TON-USD » au lieu de « TON11419-USD »).
  - La confiance affichée est toujours « faible » quand il n'y a pas d'avis net.
  - Les pages Google ont une question « va-t-il faire mieux que son marché ? ».

## Version 26 : l'Arène, les mini-robots, plus de cryptos

- **Avertissement d'entrée.** Une fenêtre claire au premier passage résume ce qu'il faut savoir : rien n'est sûr, ce ne sont pas des conseils, on peut perdre de l'argent.
- **L'Arène** (anciennement « Remonte le temps ») :
  - deux modes, partie libre et défi du jour (5 manches, le même pour tout le monde, score à copier et partager) ;
  - des points (+10 si tu as raison, +5 de bonus si tu bats l'IA, −3 si tu demandes son avis avant de répondre) ;
  - des séries, 6 badges et un tableau de bord.

  Il n'y a jamais d'argent en jeu. Le mode expert n'a volontairement pas été transformé en casino : mélanger Bourse et jeux d'argent pousse à parier.
- **Les mini-robots.** 9 stratégies classiques avec des règles fixes : suiveur de tendance, chasseur de rebonds (RSI), momentum 6 mois, cassure des « Turtle traders », MACD, Bollinger, le prudent, et pour les cryptos l'horloge du halving et le contrarien de la peur. Pour chacun, le site montre :
  - ses signaux du jour ;
  - son vrai palmarès sur tout l'historique, comparé à « toujours acheter ».

  Chaque fiche affiche aussi leurs votes. L'IA reçoit leur avis moyen comme indicateur, et ne s'en sert que s'il l'aide de façon prouvée.
- **31 cryptos au lieu de 16**, avec le prix en direct via Binance (Toncoin, Shiba Inu, Uniswap, Sui, Aptos, Pepe…).
- **Carte des chances et des risques.** C'est un nouveau graphique interactif : chaque titre placé selon ses chances de hausse et son agitation prévue, avec un filtre par marché, une info-bulle et un clic pour ouvrir la fiche. Il est utilisable au clavier.
- **État des marchés en direct** (Paris, Francfort, New York ouverts ou fermés, cryptos 24 h/24) et **agenda des résultats d'entreprises** des 30 prochains jours.
- **Corrections.**
  - Les titres aux cours figés (crypto abandonnée, homonyme sur Yahoo) ne reçoivent plus de prévision.
  - Les très petits prix (SHIB, PEPE) ne s'affichent plus en « 1.2e-05 » sur les pages Google.
  - Une phrase trop flatteuse de la FAQ a été corrigée.

## Version 25 : des pages plus riches pour Google

- **Pages de chaque titre plus complètes, avec un contenu propre à chacune** (environ 650 à 800 mots au lieu de 450). Elles contiennent maintenant :
  - les performances passées ;
  - l'entreprise en chiffres (capitalisation, PER, marges, dette, dividende) ;
  - le palmarès réel des IA sur ce titre ;
  - des questions fréquentes, celles que les gens tapent vraiment (« LVMH va-t-il monter ? », « Faut-il acheter… ? », « Quand LVMH publie-t-il ses résultats ? »), avec des réponses honnêtes tirées des chiffres du jour ;
  - des liens vers les titres du même marché.
- **5 pages par marché**, qui visent des recherches plus larges : actions françaises (CAC 40), actions européennes, actions américaines, cryptomonnaies, ETF et indices. Chacune a son tableau du jour (cours, chances de hausse, agitation prévue).
- **Fil d'Ariane et données structurées** (BreadcrumbList, FAQPage) : Google comprend mieux l'organisation du site.
- Les nouvelles pages sont ajoutées automatiquement au plan du site (sitemap) et reliées depuis l'accueil.

## Être trouvé sur Google : `google.bat`

Double-clique sur `google.bat` : il te guide pas à pas pour inscrire le site sur Google Search Console. Il ouvre la page, tu colles le code, il l'ajoute au site et republie, puis il te dit quoi valider. Compte 5 minutes.

## Mettre à jour en un clic (version 24)

1. Télécharge le nouveau `radar_bourse_mise_a_jour.zip`. Laisse-le dans Téléchargements, inutile de le dézipper.
2. Double-clique sur `mettre_a_jour.bat`, dans ton dossier Radar Bourse habituel.

Le script trouve le zip, remplace le code par la nouvelle version, puis met le site en ligne avec tes réponses habituelles. Il ne touche jamais :
- à l'historique ;
- aux connaissances de l'IA ;
- à tes réglages.

Il renomme ensuite le zip en « …_installe_… », pour ne pas le réinstaller par erreur.

## Version 24 : l'IA garde tout ce qu'elle apprend, crises et jeu

- **Les connaissances de l'IA ne se perdent plus.** Avant, `mettre_en_ligne` remplaçait le dossier `historique/` de ton PC par la version en ligne. La mémoire des essais d'entraînement (et une recette non envoyée) pouvaient être écrasées. Maintenant les deux versions sont **fusionnées** : on garde l'évaluation la plus récente du site ET les connaissances les plus récentes de l'IA. Pareil quand l'entraînement envoie son résultat : plus de conflit possible avec la mise à jour du soir.
- **Examen des crises** (entraînement Normal et Expert). L'IA rejoue le krach de 2008, la crise de l'euro, la Chine 2015, le krach crypto 2018, le Covid et la hausse des taux 2022. Elle rejoue aussi des périodes **tirées au hasard**, différentes à chaque fois. Pour chacune, elle n'apprend que sur ce qui précède. Le site montre la comparaison « en crise / en temps ordinaire ». Quand la peur des marchés est forte (VIX ≥ 30), le résumé du jour prévient.
- **Jeu « Remonte le temps ».** Un moment du passé est tiré au hasard. Le graphique s'arrête ce jour-là, tu devines la suite face à l'IA, puis on révèle le titre, la date et le résultat. L'IA n'avait jamais vu ces périodes. Le score se garde dans ton navigateur.
- **Plus de pourcentages par IA sur le site.** Seule la décision commune des deux IA est affichée.
- **Pages Google** : les titres contiennent maintenant « cours, analyse et prévision », comme les recherches des gens.

## Version 23 : confiance claire, nouveaux classements, corrections

- **Une seule échelle de confiance** (faible / moyenne / forte), avec pour chaque niveau ce qu'il a vraiment donné sur des années jamais vues. Elle apparaît dans le tableau (petites barres) et sur chaque fiche.
- **Palmarès sur chaque fiche.** « Sur ce titre, les IA ont vu juste X fois sur Y », dès que 5 prévisions ont été vérifiées.
- **Trois classements** dans « Ce que le radar prévoit » : chances de hausse, mieux que leur marché, les plus calmes.
- **Agitation prévue dans le tableau**, colonne Risque (triable).
- **Résumé du jour plus honnête.** Il parle aussi des titres sans avis net et des titres plus agités que d'habitude.
- **Pages Google et version anglaise** : elles affichent aussi « pas d'avis net », l'agitation et les raisons de l'avis. Les titres hésitants ne sont plus mis en avant dans les tops ni dans les alertes Telegram.
- **Entraînement.** Il est impossible de lancer deux entraînements en même temps (message clair). Le nouvel « examen des horizons » (modes Normal et Expert) dit à quelle échéance l'IA est la plus fiable : 1 semaine, 1 mois ou 3 mois.
- **Bilan privé** (`mon_bilan_ia.bat`). Il donne le taux de réussite par niveau de confiance, et vérifie si l'agitation prévue a été tenue.
- **Corrections.**
  - Un « signal fort » ne peut plus apparaître sur un avis jugé non fiable.
  - En mode simple, la liste des prévisions n'est plus coincée dans une demi-largeur.
  - Le nom et le code des titres ne sont plus collés dans la liste.
  - Une variable inutilisée a été retirée du script de mise en ligne.

## Version 22 : une IA plus juste et plus lisible

- **Agitation prévue.** Une IA prévoit de combien chaque titre risque de bouger le mois prochain (par exemple « ±9 %, comme d'habitude »). C'est beaucoup plus prévisible que la direction. Elle n'est utilisée que si elle bat la méthode naïve de façon prouvée ; sinon le site prend la méthode naïve et le dit.
- **Pourquoi cet avis ?** Chaque fiche montre les 3 éléments qui ont le plus pesé dans l'avis des deux IA (tendance de fond, nervosité du marché, règle du manuel…), dans quel sens et de combien. Ce sont les raisons du calcul, mesurées, pas inventées.
- **Savoir dire « je ne sais pas ».** Chaque soir, on mesure à partir de quel écart à 50 % les avis ont vraiment été plus justes que le hasard. En dessous, le site affiche « pas d'avis net » au lieu de faire semblant.
- Deux nouvelles cartes dans « Fiabilité » montrent ces mesures, avec leurs marges d'erreur.

## Entraînement intelligent (version 21)

- **Recherche guidée.** L'entraînement dessine une « carte » à partir de tous ses essais, passés et présents, pour prévoir quels réglages ont le plus de chances de faire mieux. Il teste ceux-là en priorité. Un essai sur quatre reste une idée neuve tirée au hasard, pour ne pas tourner en rond.
- **Pas de questions en double.** Les réglages identiques ou trop proches d'un essai déjà fait sont écartés.
- **Notes remises à jour.** Les meilleurs essais des séances passées sont rejoués sur les données du jour. Une vieille note n'est jamais comparée telle quelle à une note d'aujourd'hui.
- **Bilan de chaque séance.** Même quand l'IA du site ne change pas, l'entraînement dit ce qu'il a appris : réglages mémorisés, anciens réglages revérifiés, familles de réglages qui marchent le mieux. Le rapport contient une section « Recherche intelligente ».

## Ton bilan privé : combien de fois les IA ont eu raison

Double-clique sur `mon_bilan_ia.bat`. Le script récupère les prévisions que le site enregistre chaque soir sur GitHub.
Il télécharge ensuite les cours pour vérifier chacune d'elles un mois plus tard, puis ouvre une page dans ton navigateur :
- Le nombre de fois où les IA ont eu raison (« X fois sur Y »), avec sa marge d'erreur et un verdict honnête.
- La comparaison avec la stratégie paresseuse, qui parie toujours sur le sens le plus fréquent.
- L'évolution : 7 derniers jours, 30 derniers jours, mois par mois.
- Les cas où on peut lui faire confiance : IA sûre d'elle ou hésitante, deux IA d'accord ou non, signaux forts, achats et ventes.
- Les résultats par marché, les titres où elle réussit et ceux où elle rate, ses plus beaux coups et ses pires erreurs.
- L'évolution de tes bilans successifs.

Ce rapport est **privé**. Il est créé dans le dossier `rapports/` de ton PC, qui n'est jamais envoyé sur GitHub ni sur le site.
Les premiers résultats arrivent environ un mois après la mise en ligne, le temps que les premières prévisions puissent être vérifiées.

## Nouveautés de la version 20 : un site plus soigné

- Nouvelle typographie : titres en Newsreader (police éditoriale), textes en IBM Plex. Fini les petites étiquettes en MAJUSCULES.
- En haut de la page, « Aujourd'hui en bref » : un court texte écrit automatiquement à partir des chiffres du jour (humeur des indices, avis des deux IA, rappel de leur taux de réussite réel).
- Nouvelle section « Nos engagements » : on montre nos erreurs, rien à vendre, on explique tout, contact par la page GitHub du projet (aucune identité publiée).
- Pied de page rangé en colonnes : pages du site, informations légales, avertissement.

## Nouveautés de la version 19 : les techniques des professionnels

Personne n'est « imbattable » en Bourse (les meilleurs fonds ont raison autour de 52 à 55 % du temps), mais
voici ce que les gérants quantitatifs utilisent vraiment pour être plus précis, et que les IA ont appris :
- **Classements entre titres** : chaque règle du manuel est aussi utilisée en rang du jour (« ce titre fait
  partie des 10 % au meilleur momentum »), comparable d'une époque à l'autre.
- **Santé du marché entier** : part des titres en tendance haussière (« largeur ») et écart entre gagnants
  et perdants (« dispersion »), recalculés chaque jour.
- **Structure de la peur** : VIX comparé au VIX à 3 mois (panique immédiate ou pas).
- **Mémoire qui s'estompe** : l'entraînement teste si les années récentes doivent compter davantage.
- **Comité des meilleures recettes** : à l'examen final, la moyenne des 3 meilleures recettes est jugée
  aussi ; si elle gagne de façon prouvée, le site l'utilise.

## Nouveautés de la version 18 : deux IA expertes qui décident ensemble

- **Les deux IA connaissent toutes les techniques** : l'IA n°1 est une spécialiste (les indicateurs qui ont
  fait leurs preuves), l'IA n°2 utilise TOUT : indicateurs techniques, économie et les 23 règles du manuel.
- **Décision commune apprise** : chaque soir, le radar teste si une décision « apprise » (combien faire
  confiance à chacune, comment réagir quand elles se contredisent) fait mieux qu'une simple moyenne, sur des
  années jamais vues. Elle n'est utilisée que si c'est le cas. La fiche de chaque titre montre l'avis de
  chaque IA et la décision commune.
- **Tous les cours depuis le début** : jusqu'à 25 ans d'historique, relus à chaque mise à jour (toutes les
  heures). Grâce à la **mise à jour express**, seul le dernier mois est téléchargé puis collé à l'historique
  en mémoire (tout est retéléchargé si un dividende ou une division d'actions a modifié les anciens prix).
- **Apprendre de ses erreurs** : quand au moins 300 prévisions publiées ont été vérifiées, les vraies erreurs
  recalent la confiance des IA (seulement pour les rendre plus prudentes, jamais plus sûres d'elles).
  L'entraînement sur PC analyse aussi où l'IA se trompe le plus (par marché, par niveau de confiance).
- **Plus rapide** : tests sur un jour sur deux, forêt d'arbres 2 à 3 fois plus rapide, entraînement sur PC
  avec choix de durée et mémoire de ses essais.

## Le manuel de Bourse de l'IA (bourse_bot/connaissances.py)

L'IA a reçu 23 règles de Bourse étudiées par des chercheurs en finance, chacune avec sa source :
momentum (3, 6, 12 mois), retournement à court et à long terme, proximité du plus haut sur un an, cassure
du plus haut, croisements de moyennes mobiles, faible volatilité, volatilité propre au titre, pari contre le
bêta, bêta de baisse, effet « ticket de loterie », asymétrie des rendements, prime d'illiquidité, régularité
de la hausse (« frog in the pan »), momentum des nuits, suivi de tendance, prime des volumes, « Sell in May »,
effet janvier, retour vers la moyenne, momentum face au marché, momentum des cryptos, et le cycle du halving
Bitcoin (croyance populaire, testée elle aussi). Chaque règle a
une ou plusieurs versions (ex : momentum sur 3, 6 ou 12 mois) et sa source.

L'IA ne les croit pas sur parole : à chaque entraînement, elle vérifie chaque règle sur deux périodes
jamais vues, garde la meilleure version de celles qui aident vraiment, et construit une IA « indicateurs
de base + connaissances prouvées » qui doit ensuite gagner l'examen final. Le verdict est publié sur la
page **« Ce que sait l'IA »** du site (`connaissances.html`).

**Ajouter une connaissance** : ouvre `bourse_bot/connaissances.py`, copie un bloc de la liste `REGLES`,
change la clé, le nom, l'idée, la source et le calcul. Au prochain entraînement, l'IA la testera seule.

## Entraînement approfondi de l'IA (sur ton PC)

Double-clique sur **`entrainement_ia.bat`** : une fenêtre te demande la durée, **Rapide** (≈ 20 min),
**Normal** (≈ 50 min) ou **Expert** (≈ 2 h 30). `entrainement_ia_complet.bat` lance directement le mode
Expert. Pendant la recherche, l'IA garde 1 jour sur 2 ou 3 (deux jours voisins ont presque le même
résultat à un mois) : chaque essai va deux à trois fois plus vite, et l'examen final utilise tous les jours.
Elle **se souvient de ses essais** d'un entraînement à l'autre (`historique/essais_ia.json`) : la moitié
de ses essais améliore ses meilleures idées passées, l'autre moitié explore des idées nouvelles.
La fenêtre affiche ensuite :
- la **progression** en % et le temps restant ;
- une **jauge « ce que l'IA a appris »**, de « hasard » à « exceptionnel », avec l'IA du site et le
  résultat de l'examen final ;
- le **journal** de tout ce que fait l'IA ;
- un bouton **Arrêter** (ou la croix de la fenêtre) : l'IA passe alors l'examen final avec ce
  qu'elle a déjà appris, puis te propose de **mettre à jour le site**, suit la publication sur GitHub
  et **analyse le site en ligne** pour vérifier qu'il fonctionne.

Ce qu'elle étudie : jusqu'à 20 ans d'historique sur près de 300 actions, ETF et cryptos, plus des
données économiques (VIX, taux, courbe des taux, dollar, or, pétrole, cuivre, prime de risque du crédit,
tension financière, chômage), chaque chiffre décalé de son délai de publication.

**Protections contre la chance** (pour qu'elle apprenne des choses vraies, pas des coïncidences) :
1. les années les plus récentes sont **mises sous clé** : toute la recherche se fait sans elles, elles ne
   servent qu'une fois, pour l'examen final ;
2. chaque réglage est testé sur des années **jamais vues**, avec un mois de pause entre apprentissage et
   test pour que rien du futur ne fuite ;
3. un indicateur n'est gardé que s'il aide sur **deux périodes différentes** ;
4. l'IA du site n'est remplacée que si la nouvelle fait mieux **de façon prouvée (95 %)** ET **sur chaque
   moitié** de l'examen final ;
5. le rapport affiche l'« écart d'optimisme » entre la recherche et l'examen final.

Si l'entraînement n'apporte pas de progrès prouvé, l'IA du site est simplement confirmée : c'est le
résultat le plus fréquent, et c'est normal.

## Nouveautés de la version 14 (fiabilité et clarté)

- **Deux IA qui se vérifient** : IA n°1 (gradient boosting + régression) et IA n°2 (forêt d'arbres),
  construites différemment. Le site affiche si elles sont d'accord ; un signal fort exige leur accord.
  Sur l'historique, leurs désaccords ne font pas mieux que le hasard : le radar le dit au lieu de trancher.
- **Champion / challenger** : chaque soir, plusieurs méthodes sont comparées, mais la méthode en place
  n'est remplacée que si une autre fait mieux de façon prouvée (bootstrap par mois, 95 %).
- **Contrôles avant chaque publication** (probabilités valides et variées, fourchettes cohérentes, pas de
  saut brutal) : si un contrôle important échoue, rien n'est publié et l'ancienne version reste en ligne.
- **Statistiques honnêtes** : marges d'erreur calculées en tirant des mois entiers (sinon on se croit plus
  précis qu'on ne l'est), score de Brier, verdict « prouvé / possible / aucun ».
- **Actualités en garde-fou** : un signal fort est suspendu si les actus récentes sont nettement négatives,
  et une contradiction entre l'IA et l'actu est signalée (elles n'entrent pas dans la probabilité, faute
  d'historique pour mesurer leur effet).
- **Pour les débutants** : « Par où commencer », boutons « ? » qui expliquent chaque mot, grille de
  100 points (« sur 100 situations comme celle-ci, 56 ont monté »), langage simple partout.
- **Accessibilité** : taille du texte, contraste renforcé, texte aéré, sans animation (bouton « AA »).
- **Mode scénarios extrêmes** : montre les cas à 1 chance sur 20 dans les deux sens, après une
  confirmation explicite (3 cases) à chaque activation.
- **Mises à jour toutes les heures, 7 jours sur 7**, et les fourchettes suivent le prix en direct.

## Nouveautés de la version 13

- **Menu fixe** en haut (Prévisions, Simulation, Portefeuille, Fiabilité…) et **recherche** : tape
  « Apple » ou « BTC » et la fiche s'ouvre. Sur téléphone, l'en-tête se replie quand on descend.
- **Mode Simple / Expert** : le mode simple (par défaut) cache les indicateurs techniques et montre une
  courbe au lieu des bougies ; le mode expert affiche tout.
- **« Mieux que son marché ? »** : un second modèle estime la probabilité qu'un titre fasse mieux que
  son indice (CAC 40, Euro Stoxx 50, S&P 500 ou Bitcoin). Sa fiabilité est mesurée et affichée à part.
- **Fourchettes élargies de 30 %** (règle de prudence) quand une entreprise publie ses résultats avant
  l'échéance.
- **Plus de titres** : 16 grandes actions européennes (SAP, ASML, Ferrari…), 6 cryptos de plus,
  des ETF thématiques (or, semi-conducteurs, énergie propre, robotique et IA, pétrole) et l'Euro Stoxx 50.
- **Page « Résultats réels »** (`resultats.html`) : chaque prévision vérifiée après coup, mois par mois,
  par type de titre, fourchettes, signaux forts, avec un verdict honnête.
- **Image du jour** (`image-du-jour.png`, format portrait) prête à poster sur Instagram, TikTok, X.
- **Version anglaise** (`en/`) : une page par titre pour le référencement international.
- **Comparer deux titres** : courbes base 100 et tableau côte à côte.
- **Sauvegarde dans un fichier** du portefeuille virtuel, des favoris et des paris (pour changer d'appareil).
- **Alertes favoris** : en revenant, le visiteur voit ce qui a changé sur ses favoris.
- **Accessibilité** : contrastes conformes WCAG AA (thème clair et sombre), navigation au clavier,
  lien « Aller au contenu », fenêtres qui gardent le focus.
- **Nom de domaine** (facultatif) : double-clique sur `nom_de_domaine.bat`.

## Statistiques de visites (visibles par toi seule)

Le site peut compter ses visiteurs avec **GoatCounter** : gratuit pour un usage non commercial,
sans cookie, sans pistage. Le script `mettre_en_ligne.bat` (étape 9) ou `statistiques.bat` te guide.
Ton tableau de bord privé montre : visiteurs par jour, pages et fiches les plus vues, provenance
(Google, Reddit…), pays et type d'appareil. Le site n'a pas de comptes utilisateurs : on compte des
**visites**, pas des personnes « connectées ».

## Visibilité

- **Le point du jour** : chaque soir, une page « Bourse du 21 octobre : ce qu'il faut retenir » est
  rédigée automatiquement et archivée (`point.html`). Du contenu frais tous les jours, idéal pour Google.
- **FAQ** sur la page d'accueil, avec les données structurées que Google affiche dans ses résultats.
- **IndexNow** : chaque soir, les nouvelles pages sont signalées à Bing et Yandex.
- Voir **`PROMOTION.md`** pour les textes prêts à publier (Reddit, TikTok, Discord).

## Fiabilité et surveillance

- L'IA apprend sur **10 ans d'historique** et sur **~110 titres** (dont une cinquantaine utilisés
  uniquement pour l'apprentissage) : plus de situations vues, moins de pièges du hasard.
- **Contrôle qualité** de chaque titre à chaque mise à jour (fraîcheur, trous, sauts anormaux,
  comparaison Yahoo / Binance pour les cryptos). Un titre douteux est exclu des signaux forts.
- Le soir, le radar **teste 3 façons de prévoir** (modèle unique avec tous les
  indicateurs, modèle unique avec les indicateurs de base, un modèle par marché) sur des périodes
  jamais vues, et garde la meilleure. Le résultat est affiché dans « Peut-on lui faire confiance ? ».
- **Sources de secours** si Yahoo ne répond pas : Binance pour les cryptos, Stooq pour le reste.
- **Surveillance** : chaque matin, une tâche vérifie que le site a été mis à jour ; sinon GitHub
  t'envoie un e-mail.
- Les titres « en tendance » sont filtrés (pas de petites valeurs ni de micro-cryptos, souvent manipulées).

## Indicateurs utilisés (et ceux volontairement écartés)

**Utilisés par le modèle** (leur effet est mesuré par la validation walk-forward) : moyennes mobiles
simples et exponentielles (EMA 9/20/50/200), RSI et ses divergences, MACD, ADX, Bollinger (et squeeze),
ATR, stochastique, Ichimoku, Supertrend, Aroon, canal de Donchian, MFI, Chaikin Money Flow, OBV,
VWAP 20 séances, force relative, supports et résistances, figures de chandeliers japonais (affichées),
et le contexte : VIX, taux 10 ans US, dollar, or, Fear & Greed crypto.

**Affichés mais hors du modèle** (pas d'historique gratuit pour mesurer leur effet) : actualités et
leur tonalité, données fondamentales (PER, PEG, marges, ROE, dette, dividende, free cash-flow).

**Écartés** : données on-chain avancées (MVRV, SOPR…), options (gamma, max pain), futures
(funding, liquidations), carnet d'ordres et flux institutionnels (payants ou réservés aux pros) ;
Smart Money Concepts et Wyckoff (interprétations subjectives, impossibles à tester proprement) ;
les « 100 indicateurs » : la plupart se recoupent, et en empiler davantage rend un modèle moins
fiable, pas plus (il apprend le bruit du passé).

## Être trouvé sur Google et partagé

Le site génère automatiquement tout ce qu'il faut pour le référencement :
- **une page par titre** (`titres/lvmh…`), lisible par Google sans JavaScript, avec un titre et une
  description qui changent chaque jour (« LVMH (MC.PA) : analyse et prévision à un mois ») ;
- **un glossaire** des indicateurs (RSI, MACD, PER…), des pages très recherchées ;
- `sitemap.xml`, `robots.txt`, balises Open Graph / Twitter, données structurées, adresse canonique ;
- **une image de partage** : quand quelqu'un colle le lien dans WhatsApp, Discord, X ou Snapchat,
  une jolie carte s'affiche ;
- un **manifeste** : sur téléphone, « Ajouter à l'écran d'accueil » installe le site comme une appli.

**Pour accélérer l'arrivée sur Google (10 minutes, une seule fois) :**
1. Va sur https://search.google.com/search-console et ajoute ta propriété « Préfixe de l'URL » avec
   l'adresse de ton site.
2. Choisis la méthode « Balise HTML » et copie uniquement le code entre `content="` et `"`.
3. Sur GitHub : Settings → Secrets and variables → Actions → onglet **Variables** → New variable,
   nom `GOOGLE_SITE_VERIFICATION`, valeur : ce code. Relance la mise à jour (onglet Actions).
4. Dans Search Console, clique « Valider », puis menu « Sitemaps » : ajoute `sitemap.xml`.

## Sécurité

- **Politique de sécurité du contenu (CSP)** : la page ne peut charger des scripts que depuis le site
  lui-même et ne peut se connecter qu'aux services de cours (Binance, Finnhub). Un script injecté
  depuis ailleurs serait bloqué par le navigateur.
- **Bibliothèque graphique hébergée sur le site** (plus de dépendance à un CDN externe).
- **Toutes les données affichées sont échappées** (titres d'actus, noms…) et seuls les liens
  `http(s)` sont acceptés, ouverts sans transmettre d'informations au site visé.
- **Anti-cadre** : le site refuse de s'afficher à l'intérieur d'un autre site.
- **Robot GitHub à droits minimaux** : aucun droit par défaut, chaque tâche reçoit uniquement ce
  dont elle a besoin. **Dependabot** propose chaque mois les mises à jour de sécurité des outils.
- **Clé Finnhub** : elle reste visible dans la page (inévitable pour du direct sans serveur). Elle ne
  donne accès qu'à des données publiques gratuites ; utilise un compte Finnhub dédié au projet et
  régénère la clé sur finnhub.io si tu vois un usage anormal.

## Mentions légales

Avant toute mise en ligne, renseigne ton nom ou pseudo et un e-mail de contact à la fin de
`bourse_bot/config.py`. Le site affiche un avertissement au premier passage, et propose les pages
Avertissement sur les risques, Conditions d'utilisation, Mentions légales et Confidentialité.

## Personnaliser

Tout se règle dans `bourse_bot/config.py` : listes de titres, horizon de prédiction, frais.

## Un problème ?

- **« python n'est pas reconnu »** : réinstalle Python en cochant « Add Python to PATH ».
- **Beaucoup de titres ignorés** : Yahoo bloque parfois temporairement. Attends quelques minutes et relance.
- **Autre erreur** : copie le message rouge complet, il indique le fichier et la ligne en cause.
