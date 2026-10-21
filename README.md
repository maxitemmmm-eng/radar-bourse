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

- **Bandeau des marchés** : CAC 40, S&P 500, Nasdaq, Bitcoin, avec la variation du jour.
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

## Pour les visiteurs

- **Portefeuille virtuel** : 10 000 € fictifs pour s'entraîner sans risque (gardé dans le navigateur).
- **Favoris**, bouton **Partager**, installation sur téléphone.
- **Apprendre la Bourse** : 8 mini-cours illustrés avec un quiz (actions, cryptos, bougies, tendances,
  RSI/MACD, gestion du risque, pièges, long terme) + un glossaire.
- **Alertes Telegram** (facultatif) : chaque soir, le robot publie les signaux forts sur ta chaîne.
  Pour l'activer plus tard : double-clique sur `alertes_telegram.bat`.

## Fiabilité et surveillance

- À chaque mise à jour, le radar **teste 3 façons de prévoir** (modèle unique avec tous les
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
