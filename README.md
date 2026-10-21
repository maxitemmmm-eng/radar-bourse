# 📈 Radar Bourse

Un site qui analyse les actions françaises, les actions américaines, les principales cryptos,
des ETF et les titres en tendance. Pour chaque titre : cours actuel, score technique sur 100,
signal, **probabilité de hausse à 20 séances (~1 mois)**, fourchette de prix probable,
graphique avec la prévision, raisons du signal, et résultat d'un backtest.

> ⚠️ **Outil éducatif, pas un conseil en investissement.** Aucun programme ne prédit la Bourse de façon
> fiable. Le site affiche lui-même sa précision pour que tu saches quand ne pas le croire.

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

## Entraînement approfondi de l'IA (sur ton PC)

Double-clique sur **`entrainement_ia.bat`** (20 à 60 min) ou **`entrainement_ia_complet.bat`** (1 à 3 h,
plus de réglages testés). L'IA :

1. étudie **jusqu'à 20 ans** d'historique sur **près de 300 actions, ETF et cryptos** (France, Europe,
   États-Unis, cryptos) et des **indicateurs économiques** : peur des marchés (VIX), taux longs et
   courts, courbe des taux, dollar, or, pétrole, cuivre, prime de risque du crédit, tension
   financière, inscriptions au chômage (Réserve fédérale de Saint-Louis). Chaque chiffre économique
   est décalé de son délai de publication : l'IA ne « voit » jamais une donnée avant sa sortie ;
2. passe deux examens sur des années qu'elle n'a jamais vues : plus de titres d'apprentissage
   aident-ils vraiment ? quelle façon de prévoir est la meilleure ?
3. ne remplace l'IA du site **que si le progrès est prouvé** (marge d'erreur à 95 %) ;
4. écrit un rapport clair (dossier `rapports`) et, si elle a progressé, **envoie la nouvelle recette
   sur GitHub** : le site se met à jour tout seul en 15 à 30 minutes.

Le résultat du dernier entraînement est affiché sur le site, rubrique « Peut-on lui faire confiance ? ».
Ces données économiques sont aussi utilisées par les mises à jour automatiques en ligne.

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
