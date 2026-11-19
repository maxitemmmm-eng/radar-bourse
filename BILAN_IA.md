# Grand bilan de l'IA de Radar Bourse (18 novembre 2026)

Chiffres relevés sur le site en ligne le 18/11/2026 (fiche technique, journal de l'IA, résultats réels, suivi du risque de chute).
« Hors échantillon » : testé sur des années que l'IA n'avait jamais vues (avril 2014 – octobre 2026, 581 357 prévisions).

## Ce qu'elle fait bien (prouvé)

| Ce que l'IA prévoit | Résultat | À comparer à |
|---|---|---|
| Risque de chute de plus de 10 % en un mois | note de tri 0,775 ; titres jugés les plus à risque : 38 % de chutes | 13 % d'habitude |
| Agitation à un mois (de combien le prix va bouger) | erreur 24,1 % | méthode simple : 31,5 % |
| Plus ou moins agité le mois prochain, tous les cas | 70,2 % de bonnes réponses | 50,9 % |
| … avis sûrs (environ la moitié des cas) | 80,9 % (82,3 % avec le réglage v89, en place dès le prochain examen du soir) | au moins 77 % 11 années sur 12 |
| … avis très sûrs (un quart des cas) | 86,7 % | pire année 83 % |
| Fourchette « 8 fois sur 10 » | tenue 79,4 % | promis 80 % |
| Agitation sur une semaine | meilleure 24 années sur 24 | « comme la semaine dernière » |

## Ce qu'elle fait à peine mieux que le hasard

| Ce que l'IA prévoit | Résultat | À comparer à |
|---|---|---|
| Sens du prix à un mois (hausse ou baisse) | 55,6 % | 54,1 % en répondant toujours pareil |
| … quand elle est la plus confiante (10 % des avis) | environ 58 % | – |
| … quand elle hésite | environ 51 à 53 % | – |
| Faire mieux que son marché | 54,0 % | 51,8 % |

Cela fait à peu près une bonne réponse de plus tous les 65 avis. Personne ne prévoit bien le sens du prix à un mois. Le site le dit partout et n'en fait jamais une promesse.

## En conditions réelles (prévisions publiées, vérifiées après coup)

- **Risque de chute, suivi public** : en octobre comme en novembre, les 10 titres jugés les plus à risque ont tous chuté de plus de 10 % ; aucun des 10 moins à risque n'a chuté. Excellent, mais à relativiser : les « plus à risque » étaient surtout de petites cryptos, pendant une baisse générale des cryptos. L'IA a surtout repéré ce qui est le plus fragile, ce qui est déjà utile.
- **Sens du prix** : 81 % de bonnes directions, mais en disant « baisse » sur des cryptos qui ont toutes baissé ensemble. Répondre toujours la même chose aurait fait 88 %. Verdict honnête : pas mieux que la référence sur cette période.
- **Fourchette** : 52 % tenues au lieu de 80 %. C'est le vrai point faible du mois : une baisse générale des cryptos casse toutes les fourchettes en même temps. Sur 12 ans de tests, elle tenait 79 %. Il faut plusieurs mois de suivi pour savoir si c'est un mauvais mois ou un défaut.
- **Avis sûrs vérifiés en public** : 937 avis enregistrés depuis le 6 novembre, premiers verdicts vers début décembre.
- **Registre scellé (v92)** : à partir de maintenant, chaque prévision est scellée le soir même. Les résultats réels ne pourront plus être contestés.

## Ce qui a été essayé

- **50 idées testées honnêtement** depuis la version 51 : 9 adoptées, 41 rejetées. Toutes sont listées dans le journal de l'IA.
- **Ce qui a été adopté** : tout concerne l'agitation et le risque de chute. Par exemple, le risque propre à chaque titre, la mémoire du titre pour le risque de chute, la question « plus ou moins agité ? », l'écart à sa normale, les avis sûrs, les avis très sûrs et le réglage plus exigeant de la v89.
- **Ce qui a été rejeté** : presque toutes les idées pour mieux deviner le sens du prix. Par exemple, la cible « classement », une IA par ambiance de marché, le comité de 5 experts de la v88, les fourchettes par marché ou un seuil par marché. Elles restent en compétition chaque soir, mais ne battent pas la recette la plus simple (« un seul modèle, indicateurs de base »).
- **Entraînement de nuit** : 384 réglages essayés en 16 nuits, aucun n'a battu les réglages d'origine de façon prouvée. C'est voulu : la règle anti-chance empêche d'adopter un réglage qui gagnerait par hasard.
- **Le « manuel de Bourse »** : 3 règles de finance sur 23 sont prouvées utiles sur les années récentes. Le momentum, par exemple, ne marche plus ces dernières années.

## Ce que j'en conclus

1. L'IA est vraiment bonne pour mesurer le risque : de combien ça va bouger, et quels titres peuvent chuter. C'est sa vraie force, et c'est ce que le site doit mettre en avant.
2. Pour le sens du prix, elle est proche du hasard, comme toutes les IA sérieuses. Continuer à régler le même modèle ne mènera nulle part : 41 essais l'ont montré. Un vrai gain ne viendra que d'informations nouvelles.
3. Les résultats réels ne portent encore que sur environ 8 jours de marché. Il faut 6 à 12 mois avant de conclure, d'où le registre scellé.

## Les prochaines pistes, par ordre de chances de succès

1. **Dates de résultats d'entreprise** : prévenir et élargir la fourchette avant une publication. Ces dates sont déjà connues du site. Gain probable sur la fourchette.
2. **Fourchettes plus larges quand tout le marché crypto est nerveux** : une correction pour les baisses générales comme celle d'octobre. À tester sur les crises passées, et seulement si aucune année ne recule.
3. **Les actualités** : 17 jours de mémoire sur 250. Premier test honnête possible vers l'automne 2027.
4. **Les experts « entreprise » et « actualités »** (journal depuis la v88) : à tester quand il y aura assez de recul.
