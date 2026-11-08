# Visibilité : les textes prêts (version 65, corrigés en version 66)

Le meilleur argument du site, c'est désormais **la page des avis vérifiés en public**. Peu de sites osent montrer leurs ratés. C'est ce qui donne envie de partager et de faire un lien.
Les pages à montrer :

- Les avis vérifiés en public : `https://radarbourse.fr/avis-surs-verifies.html`
- La Bourse cette semaine : `https://radarbourse.fr/bourse-cette-semaine.html`
- Les actions par thème : `https://radarbourse.fr/themes.html`
- Prédiction crypto (Bitcoin, Ethereum…) : `https://radarbourse.fr/prediction-crypto.html`
- Prédiction bourse : `https://radarbourse.fr/prediction-bourse.html`

Règles : publier sous pseudo seulement, une fois par endroit, sans spam. Toujours répondre aux commentaires, même aux critiques.

---

## 1. awesome-quant (en attente : question de licence)

Cette liste recense surtout des projets **open source**, c'est-à-dire que tout le monde a le droit de réutiliser le code. Ton dépôt est sous licence **« Tous droits réservés »** : le code se lit, mais personne n'a le droit de le réutiliser. Avec cette licence, la demande risque d'être refusée. Deux choix :

- **Garder « Tous droits réservés »** (ton travail reste protégé) : on oublie awesome-quant et on vise les annuaires d'outils (Product Hunt, AlternativeTo), qui acceptent les projets non libres.
- **Passer le code en licence libre** (MIT ou AGPL, par exemple) : awesome-quant devient possible, mais n'importe qui pourra réutiliser ton code. C'est à toi de décider ; je ne change rien sans ton accord.

---

## 2. Reddit en français : r/vosfinances (lis les règles avant, l'autopromo y est encadrée), r/BourseFrance, r/CryptoFr

**Titre** : `J'ai fait un site d'IA bourse qui publie ses propres ratés (gratuit, sans pub)`

```
Salut ! Projet perso d'étudiante : un radar gratuit qui suit ~300 actions, ETF et cryptos suivis de près (et 2 000+ fiches simples).

Pour chaque titre, l'IA donne son avis (hausse ou baisse) avec ses chances et son niveau de confiance, sans cacher qu'elle se trompe souvent sur le sens du prix. Ce qu'elle prévoit le mieux : si le mois prochain sera plus agité ou plus calme, et le risque d'une chute de plus de 10 %.

Ce qui change :
- les avis sont enregistrés à l'avance, puis vérifiés en public 20 séances plus tard. Rien n'est effacé, les ratés restent affichés ;
- sur les années passées, que l'IA n'avait jamais vues, ses « avis sûrs » étaient justes environ 80 % du temps. On verra si ça tient en vrai ;
- c'est gratuit, sans inscription, sans pub, et le code est public (on peut le lire sur GitHub).

La page des avis vérifiés : https://radarbourse.fr/avis-surs-verifies.html

Je prends toutes les critiques, surtout sur la méthode. (Ce n'est pas un conseil en investissement.)
```

---

## 3. Reddit en anglais : r/SideProject, r/algotrading (le jour « Show and Tell » seulement), r/learnmachinelearning

**Titre** : `I built a free stock/crypto volatility forecaster that checks its own calls in public`

```
Side project: ~300 stocks, ETFs and cryptos, updated hourly on GitHub Pages (Python + GitHub Actions, no server).

Instead of predicting direction (close to a coin flip), it forecasts next-month volatility and drawdown risk. Every "confident call" is logged before the outcome and verified 20 sessions later, on a public page with misses included. Out of sample (walk-forward, 2016-2026), the confident calls were right ~80% of the time vs ~78% for a simple mean-reversion rule, so the edge is real but small.

Verified calls: https://radarbourse.fr/en/verified-calls.html
Source code (public, all rights reserved): https://github.com/maxitemmmm-eng/radar-bourse

Feedback on the methodology very welcome.
```

---

## 4. Hacker News (« Show HN », un mardi ou un mercredi vers 15 h, heure de Paris)

**Titre** : `Show HN: A stock volatility forecaster that publishes every call and checks it later`
Lien : la page anglaise des avis vérifiés. En premier commentaire, mets le paragraphe de la partie 3.

---

## 5. Product Hunt et AlternativeTo

- **Phrase courte** : `Free AI stock & crypto forecasts that check their own calls in public, misses included.`
- **Description** : `~300 stocks, ETFs and cryptos. Forecasts what can actually be forecast (next-month volatility, risk of a >10% fall), records every confident call in advance and verifies it 20 sessions later. Free, no sign-up, no ads, public source code.`
- **Alternative à** : Danelfin, Zonebourse, TradingView, Investing.com
- **Images** : `partage.png` et une capture de la page des avis vérifiés.

---

## 6. Forums (Boursorama, Investing.com, forum-crypto.fr)

Ne poste pas d'annonce. Réponds à une vraie question, puis ajoute le lien s'il aide vraiment. Exemple, sous « L'IA peut-elle prédire la Bourse ? » :

```
Pour le sens du prix, honnêtement non : les meilleurs modèles font à peine mieux que le hasard. Par contre l'agitation (de combien ça va bouger) se prévoit assez bien. J'ai un petit projet qui vérifie ça en public, avis par avis : https://radarbourse.fr/avis-surs-verifies.html
```

---

## 7. Les petits gestes qui comptent

- **Dépôt GitHub** : roue dentée « About », ajouter les topics `volatility-forecasting` `walk-forward` `stock-market` `crypto` `python` `github-pages`.
- **Bing Webmaster** : connecte-toi une fois dans le navigateur de l'appli et je fais le reste.
- **Chaque lundi** : partager `bourse-cette-semaine.html` (WhatsApp, Discord, groupe de fac). L'adresse ne change jamais.
