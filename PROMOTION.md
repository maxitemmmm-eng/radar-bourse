# 📣 Faire connaître Radar Bourse

Ce qui marche pour un site gratuit et éducatif, du plus efficace au moins efficace.
Présente toujours le site comme **un outil pour apprendre**, jamais comme « le site qui te fait gagner » :
c'est plus honnête, mieux accepté sur les forums, et ça évite les ennuis.
Poste sous le pseudo **maxitemmmm**, sans nom ni photo. Pour le contact, renvoie vers les « Issues » GitHub.

Adresse à coller partout : https://maxitemmmm-eng.github.io/radar-bourse/
Appli en anglais : https://maxitemmmm-eng.github.io/radar-bourse/app-en.html

## 1. Google (gratuit, effet durable)
- Fais l'étape **Google Search Console** du README (10 minutes). C'est ce qui compte le plus.
- Le site publie chaque soir un **« point du jour »**. Google aime le contenu frais et régulier.
- Patience : il faut en général 2 à 8 semaines pour apparaître sur des recherches comme
  « prévision action LVMH », « simulateur boursier » ou « convertisseur bitcoin euro ».

## 2. Reddit en français (r/vosfinances, r/BourseFrance, r/CryptoFr)
Lis les règles de chaque forum avant de poster : certains interdisent l'autopromotion.
Texte prêt à adapter :

> **J'ai codé un site gratuit qui montre honnêtement ce qu'une IA sait (et ne sait pas) prévoir en Bourse**
> Salut ! En apprenant Python, j'ai construit un site qui analyse chaque heure plus de 200 actions, ETF et cryptos.
> Ce que j'ai appris en le testant sur 20 ans d'historique : la **direction** d'un prix à un mois, c'est presque
> pile ou face, et le site le dit. En revanche, **de combien un prix peut bouger**, ça se prévoit nettement mieux
> (plus proche de la réalité que « comme le mois dernier » 6 fois sur 10, toutes les années testées).
> Il y a aussi un simulateur, un portefeuille virtuel en argent fictif, un jeu « remonte le temps » contre l'IA,
> des outils gratuits (« si j'avais investi », intérêts composés, plus-values) et des mini-cours.
> Chaque prévision publiée est vérifiée un mois plus tard, même les ratées. Gratuit, sans pub, sans inscription.
> Je cherche surtout des retours pour l'améliorer !
> [lien]

## 3. Reddit en anglais (r/SideProject, r/webdev, r/learnpython)
r/SideProject accepte l'autopromotion. Sur r/learnpython, insiste sur ce que tu as appris.

> **I built a free stock & crypto forecast site that is honest about what AI can't predict**
> I've been learning Python and built Radar Bourse: every hour it analyses 200+ stocks, ETFs and cryptos and
> publishes one-month forecasts. The twist: it measures and shows its own reliability.
> What 20 years of walk-forward testing taught me: predicting the *direction* of a price is close to a coin toss
> (and the site says so, market by market). Predicting *how much* a price will move works much better: closer to
> reality than "same as last month" about 6 times out of 10, every year tested.
> Also: a "go back in time" game against the AI, a virtual portfolio, free calculators (if I had invested,
> compound interest, crypto converter). Static site on GitHub Pages, no ads, no sign-up.
> Feedback welcome, especially on the methodology!
> https://maxitemmmm-eng.github.io/radar-bourse/app-en.html

## 4. Hacker News (« Show HN »)
Va sur https://news.ycombinator.com/submit. Titre court et factuel, sans superlatif :

- **Titre :** `Show HN: An AI stock forecaster that publishes how often it's wrong`
- **URL :** l'adresse de l'appli anglaise
- **Premier commentaire** (à poster toi-même juste après) :

> Hi HN. This is a hobby project: a Python pipeline (gradient boosting, walk-forward validation, conformal
> prediction intervals) that rebuilds a static site every hour on GitHub Actions.
> The main lesson: one-month price direction is barely better than chance (AUC ~0.53), so the site falls back to
> each market's base rate wherever the model isn't proven better. Volatility is far more predictable, so the
> site leans on that instead: ranges, drop risk, "how much can it move".
> Every published forecast is checked a month later on a public results page.
> Happy to answer questions about the validation setup.

Conseils : poste un mardi ou un mercredi vers 15 h (heure française), et réponds aux commentaires dans l'heure.

## 5. Product Hunt
Il faut un compte : crée-le toi-même avec ton pseudo. Fiche prête :

- **Nom :** Radar Bourse
- **Accroche (60 caractères max) :** `Free AI stock & crypto forecasts that show their own errors`
- **Description :**
  > One-month forecasts for 200+ stocks, ETFs and cryptos, updated every hour. Each forecast shows how reliable
  > the AI really was on years it had never seen, and every published forecast is checked a month later.
  > Includes a "beat the AI" history game, a virtual portfolio, and free calculators. No ads, no sign-up.
- **Images :** les vignettes de `partage/pages/` (1200 × 630) : fonctionnalités, arène, simulateur, outils.
- **Catégories :** Fintech, Artificial Intelligence, Education.

## 6. dev.to (article technique, très bien référencé)
Titre proposé : **« What 20 years of backtesting taught me about predicting stock prices with ML »**

Plan de l'article (environ 1 000 mots) :
1. Le projet en deux phrases, et le lien.
2. Le piège : un modèle qui dit « hausse » tout le temps a l'air bon, parce que les marchés montent plus souvent
   qu'ils ne baissent. D'où la comparaison systématique avec « toujours la même réponse ».
3. La validation « walk-forward » : on n'entraîne que sur le passé, on teste sur des années jamais vues.
4. Le résultat honnête : la direction est proche du hasard, l'agitation (volatilité) se prévoit bien.
5. Ce qui n'a PAS marché : modèles séparés crypto/actions, pondération des années récentes, ensemble de
   3 modèles, recalibrage par marché. Tous testés, aucun n'a battu le modèle en place.
6. Les fourchettes conformes (CQR) : promettre « 8 fois sur 10 » et le vérifier.
7. Le site statique : GitHub Actions + GitHub Pages, zéro serveur, zéro coût.

Tags : `#python #machinelearning #finance #showdev`

## 7. L'image du jour et la page « Résultats réels »
- Chaque jour, le site fabrique **`image-du-jour.png`** (1080 × 1350). Tu peux la partager où tu veux.
- La page **« Résultats réels »** est ton meilleur argument : peu de sites osent publier leurs vrais résultats.
  Partage-la une fois par mois (« voilà ce que mon radar a eu juste et faux ce mois-ci »).

## 8. Annuaires et listes gratuites
Voir `LISTES_A_PROPOSER.md` (awesome-quant : il te reste à cliquer « Create pull request »).

## À éviter
- Promettre des gains, citer des « taux de réussite » sortis de leur contexte.
- Poster le même message sur plusieurs forums le même jour.
- Acheter des abonnés ou des faux avis.

## Suivre les résultats
Ton tableau de bord GoatCounter (privé) montre le nombre de visites, les pages les plus vues
et d'où viennent les visiteurs (Google, Reddit, Hacker News…).
