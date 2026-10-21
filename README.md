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

## Ce qu'affiche le site

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
