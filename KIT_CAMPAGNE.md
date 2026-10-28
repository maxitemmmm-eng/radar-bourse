# Kit de campagne Radar Bourse : 14 jours, gratuit, sous pseudo

Le but : faire venir de vraies personnes **et** obtenir des liens vers le site. Ces liens sont ce qui fait le plus monter le site dans Google.
Tout est prêt à copier-coller. Ne mets jamais ton vrai nom, signe « Radar Bourse » ou avec ton pseudo.

**Règles pour ne pas te faire bannir :**
- Lis les règles de chaque groupe avant de poster.
- Dis toujours que c'est **ton** projet.
- Pas plus d'un post par groupe.
- Réponds aux commentaires, c'est ça qui fait remonter un post.
- Jamais de faux comptes ni de faux avis.

---

## Le calendrier

| Jour | Action (10–20 min) |
|---|---|
| 1 | Installer la mise à jour, `mettre_en_ligne`, Search Console : demander l'indexation de l'accueil et de `guides.html` |
| 1 | GitHub : remplir « About » + « Website » + topics (voir LISTES_A_PROPOSER.md) |
| 2 | Post Reddit **r/vosfinances** (texte A) |
| 3 | Vidéo courte n°1 (script 1) sur TikTok + Reels + Shorts |
| 4 | Fiche **AlternativeTo** (LISTES_A_PROPOSER.md) |
| 5 | Post Reddit **r/CryptoFr** (texte B) |
| 6 | Vidéo n°2 (script 2) |
| 7 | Regarder Search Console (`campagne_google.bat` → analyser l'export) |
| 8 | Proposer le site à **awesome-quant** (LISTES_A_PROPOSER.md) |
| 9 | Vidéo n°3 (script 3) |
| 10 | Post sur 1 ou 2 serveurs **Discord** bourse/crypto (texte C, dans le salon « projets » ou « partage ») |
| 11 | Post anglais **r/algotrading** ou **Hacker News « Show HN »** (texte D) |
| 12 | Vidéo n°4 (script 4) |
| 13 | **Product Hunt** (une seule fois, un mardi ou mercredi) |
| 14 | Bilan : visites (statistiques.bat), requêtes Google, liens obtenus. On garde ce qui a marché |

Tous les jours (2 min) : `campagne_google.bat`, pour les 10 demandes d'indexation.

---

## Texte A : Reddit r/vosfinances

**Titre :** J'ai testé honnêtement une IA de prévision boursière sur 5000 cas : elle ne devine pas le sens du prix, mais elle repère bien les risques de chute

**Texte :**
> Je fais un projet perso gratuit (pas de pub, pas de compte, pas d'affiliation) : un site qui analyse ~185 actions, ETF et cryptos chaque jour avec des IA.
>
> Je voulais savoir si ça marche vraiment, donc je l'ai testé sur 5000 cas tirés au hasard dans des années que l'IA n'avait jamais vues :
> - **Sens du prix à 1 mois** : ~56 %, autant que la règle bête « ça monte toujours ». Donc non, l'IA ne prédit pas la bourse.
> - **Risque de chute de plus de 10 % en un mois** : là, ça marche. Les titres jugés les plus risqués chutent 21,8 % du temps, contre 8,6 % en moyenne.
> - **Agitation** (de combien ça va bouger) : plus proche de la réalité que la méthode simple 61 % du temps.
>
> Tout est publié sur le site, ratés compris : https://maxitemmmm-eng.github.io/radar-bourse/resultats.html
>
> Je suis preneur de critiques sur la méthode de test (walk-forward, calibration par année, bootstrap par mois).

## Texte B : Reddit r/CryptoFr

**Titre :** Agitation prévue et risque de chute de plus de 60 cryptos, mis à jour chaque jour (projet gratuit, résultats publiés)

**Texte :**
> Petit projet perso gratuit et sans pub : chaque jour, des IA estiment pour plus de 60 cryptos **de combien elles vont bouger** le mois prochain et **le risque de perdre plus de 10 %**.
>
> Je ne prétends pas deviner si ça monte : je l'ai testé et sur les cryptos, l'IA fait même moins bien que « ça monte toujours ». Le site l'affiche honnêtement.
> Par contre, le risque de chute est bien repéré sur les années testées.
>
> Classement du jour : https://maxitemmmm-eng.github.io/radar-bourse/classements/cryptos-agitees.html
> Pas un conseil, juste des chiffres. Retours bienvenus.

## Texte C : Discord (court)

> Salut ! J'ai fait un site gratuit (sans pub ni compte) qui montre chaque jour l'agitation prévue et le risque de forte chute d'environ 185 actions et cryptos, avec ses vrais résultats publiés, ratés compris. Il y a aussi des duels genre « Airbus ou Safran », « BTC ou ETH ». Si ça vous intéresse : https://maxitemmmm-eng.github.io/radar-bourse/ ; dites-moi ce qui manque.

## Texte D : anglais (r/algotrading ou Show HN)

**Titre :** Show HN: I tested my stock-forecasting models on 5,000 unseen cases. Direction is a coin flip, drop risk isn't

> Free, no-ads side project analysing ~185 stocks, ETFs and cryptos daily. Walk-forward test on years the models never saw:
> - 1-month direction: ~56%, same as "always up". No edge.
> - Risk of a >10% drop next month: AUC 0.69; top decile drops 21.8% of the time vs 8.6% base.
> - Volatility forecast beats last-month baseline 61% of the time.
> Everything (including failures) is published: https://maxitemmmm-eng.github.io/radar-bourse/en/index.html
> Feedback on the methodology welcome.

---

## 4 scripts de vidéos courtes (20–30 s, filme ton écran, sans montrer ton visage)

1. **« J'ai testé une IA de bourse sur 5000 cas »**
   - Accroche : « Les IA qui prédisent la bourse, ça marche ? J'ai testé. »
   - Montre `resultats.html` : « Le sens du prix : 56 %, comme répondre "ça monte" à chaque fois. »
   - Fin : « Mais il y a un truc qu'elle fait bien… partie 2. »
2. **« Le seul truc que l'IA prévoit vraiment »** : montre le classement « risque de chute » et le chiffre 21,8 % contre 8,6 %.
3. **« L'argent facile en bourse, la vérité »** : montre le guide `guides/argent-facile-bourse.html`, en trois phrases.
4. **« Airbus ou Safran ? »** : ouvre un duel et lis les 3 chiffres clés. « Lien en bio pour comparer n'importe quelles actions. »

À chaque fois : lien du site en bio, et la phrase « pas un conseil d'investissement » à l'écran.

---

## Répondre aux commentaires (exemples)

- **« C'est une arnaque ? »** → « Aucun paiement, aucun compte, aucune pub, et les ratés sont publiés. Si tu vois quelque chose de louche, dis-le-moi. »
- **« Ton IA est nulle, 56 % »** → « Oui, sur le sens du prix, et je l'écris en gros sur le site. C'est le risque de chute qui marche. »
- **« Tu gagnes combien ? »** → « Rien, c'est un projet éducatif. »

## Ce qu'on mesure au jour 14

- Visites par jour (statistiques.bat).
- Nombre de pages indexées dans Search Console.
- Requêtes qui amènent du monde (`campagne_google.bat` → export).
- Nombre de sites qui font un lien vers le tien.
