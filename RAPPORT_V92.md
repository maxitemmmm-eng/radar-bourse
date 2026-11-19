# Rapport version 92 : audit, source unique des chiffres, registre public, scanner

Date : 18 novembre 2026. Ce rapport suit l'ordre de la mission : audit, comparaison, plan, développement, tests, limites.

## 1. Audit du site en ligne (radarbourse.fr, 18/11/2026)

J'ai relu 16 pages clés du site en ligne et cherché dans le code d'où vient chaque chiffre.

### Chiffres incohérents trouvés

| Page | Ce qui était écrit | D'où ça venait | Problème |
|---|---|---|---|
| Accueil (appli) | « Les avis de l'IA sur plus de 2 500 actions » | écrit à la main dans le gabarit | l'IA analyse ~340 titres chaque heure ; les ~2 150 fiches simples n'ont un avis qu'une fois par jour, et seulement quand le calcul a réussi. Le nombre n'était jamais vérifié |
| Accueil (appli) | « Plus de 2 500 titres ont leur fiche » | écrit à la main | juste aujourd'hui, mais ne suivait pas la réalité |
| À propos | « l'avis de l'IA sur 2 517 actions » | 362 titres (avec les 3 pages « tendances ») + 2 155 fiches | mélange deux choses différentes, et compte les « tendances » qui ne sont pas des titres |
| Fonctionnalités | « 362 titres » | tous les éléments de la liste, « tendances » comprises | 22 de trop par rapport à la fiche technique (340) |
| Fiche technique | « 340 titres suivis » | sans les « tendances » | le bon compte |
| Images de partage, appli anglaise | « près de 300 actions » / « nearly 300 » | écrit à la main il y a des mois | faux depuis longtemps |
| Google (description de l'accueil) | « Avis de l'IA sur 2 500 actions (81 % de réussite sur ses avis sûrs) » | 2 500 écrit à la main | laissait croire à 81 % de réussite sur le sens du prix, alors que ce chiffre porte sur l'agitation |
| Vos questions (FR et EN) | « 51 fois sur 100 … 58 fois sur 100 » | écrit à la main | ne suivait pas l'examen du soir |

### Autres problèmes trouvés

- **Accueil anglais** : « Model unavailable today » alors que le modèle tournait. Cause : ce jour-là, aucun titre n'avait un avis « net » ; la liste était vide et le message affiché était faux.
- **Page Résultats réels** : un grand « 81 % de bonnes directions » sur 455 prédictions, mais faites sur environ 8 jours de marché et à 75 % sur des cryptos qui ont chuté ensemble. Le verdict honnête était bien affiché, mais rien ne disait que 455 cas aussi liés valent beaucoup moins que 455 cas indépendants. La fourchette réelle n'a tenu que 52 % du temps, contre 80 % promis : c'était affiché, mais sans explication.
- **Prédiction crypto** : phrase mal construite (« l'IA voit 2 cryptos sur 112 à la hausse et 110 à la baisse »).
- **Avertissement démo** : le bandeau « Données fictives de démonstration » existe dans la page mais reste caché sur le vrai site (il n'apparaît qu'en mode démo). C'est correct.
- **Délais de mise à jour** : chaque page datée affiche la date des cours (« cours au 18/11/2026 »), et la fiche technique la date du dernier examen. C'est correct.
- **Cohérence des performances** : la fiche technique (55,6 %), l'accueil anglais (56 %), les fiches (« 56 fois sur 100 ») et la fourchette (79 à 81 %) lisent toutes le même examen du soir. C'est cohérent. Seules les réponses de « Vos questions » étaient écrites à la main.

## 2. Comparaison avec les grands sites (pour s'inspirer, sans rien copier)

| Site | Son point fort | Ce que Radar Bourse en retient | Ce que Radar Bourse fait déjà mieux |
|---|---|---|---|
| TradingView | graphiques et scanner très complets, filtres enregistrés | scanner à critères combinables, enregistrés et partageables par lien (fait en v92) | explications en mots simples ; aucun compte demandé |
| CoinMarketCap | classements crypto, listes de suivi | page « Data du jour » à prévoir (plus grosses hausses et baisses, volumes) | avis à un mois avec niveau de confiance |
| Simply Wall St | fondamentaux résumés en un visuel | fiche titre : un résumé visuel des fondamentaux (à faire) | transparence totale sur les erreurs |
| Koyfin | tableaux de bord personnalisables | tableau de bord personnel stocké sur l'appareil, avec export et import (à faire) | gratuit, sans inscription |
| Glassnode | données on-chain des cryptos | données on-chain gratuites et sous licence claire (à étudier, beaucoup sont payantes) | – |
| Token Metrics | notes IA des cryptos | – | nos résultats sont publiés et vérifiables, ratés compris, et le registre scellé rend toute retouche détectable |

Le point fort de Radar Bourse, que les autres n'ont pas : la preuve. Le registre scellé (v92) va dans ce sens.

## 3. Plan par priorité

1. **Fait en v92** : une seule source de vérité pour les chiffres ; un registre public scellé ; un scanner sérieux ; les corrections trouvées pendant l'audit.
2. **Prochaine étape** : un tableau de bord personnel (favoris, scanners, simulateur, sur l'appareil, avec export et import) et une page « Data du jour » (hausses, baisses, agitation et risque de chute du jour, tout calculé à partir des cours suivis).
3. **Ensuite** : un simulateur à plusieurs portefeuilles (historique, comparaison au CAC 40 ou au MSCI World, pire baisse) et une fiche titre en 6 parties (résumé, avis IA, graphique, fondamentaux, risques, historique des avis).
4. **Plus tard** : un assistant qui répond seulement avec les données du site, en citant la source et la date. Il en existe déjà une version simple, par règles, dans l'appli. Une vraie IA conversationnelle demanderait une API payante.

## 4. Ce qui a été développé

### Une source unique de vérité pour les chiffres (`bourse_bot/chiffres.py`, nouveau)
- Tous les chiffres publics sont calculés à un seul endroit, à chaque génération du site, à partir des données du jour :
  - titres analysés par l'IA ;
  - fiches simples, et fiches simples qui ont reçu un avis de l'IA ;
  - réussite hors échantillon (globale, en confiance faible, en confiance forte) ;
  - avis sûrs d'agitation ;
  - fourchette tenue ;
  - résultats réels.
- Un chiffre manquant reste vide. Il n'est jamais inventé.
- Les textes fixes (appli, traductions, images) utilisent des jetons (`__NB_IA__`, `__NB_FICHES__`, `__NB_AVIS_IA__`), remplacés à la fin, au format de la langue de la page. Les nombres sont arrondis vers le bas (« plus de 2 500 ») pour ne jamais exagérer.
- Le nombre de fiches simples qui ont reçu un avis de l'IA est maintenant compté (`main.py`), et non plus supposé.
- **Nouvelle page `chiffres-du-site.html`** : chaque chiffre, sa valeur du jour, ce qu'il mesure et sa source. **Nouveau fichier `chiffres.json`**, public.
- **Contrôle automatique** à chaque génération : si une ancienne formulation écrite à la main revient (« près de 300 »…), ou si un jeton n'a pas été remplacé, le journal l'affiche.

### Le registre public des prévisions (`bourse_bot/registre.py`, nouveau)
- **Scellement** : chaque soir, les prévisions publiées sont copiées dans `historique/registre/AAAA-MM-JJ.csv`, au format fixe. Ce fichier n'est jamais réécrit.
- **Chaîne d'empreintes** : chaque fichier est scellé dans `chaine.csv` avec son empreinte SHA-256 et celle du bloc précédent. Modifier un seul chiffre casse la chaîne.
- **Bloc 0** : l'historique d'avant le registre, scellé tel quel le premier soir. Il est présenté comme tel, avec une garantie plus faible.
- **Corrections** : on ne modifie jamais un fichier. Une erreur s'ajoute dans `corrections.csv` (date, motif) et apparaît publiquement. La prévision concernée sort des calculs de performance, jamais du fichier.
- **Nouvelle page `registre-previsions.html`** :
  - l'état de la chaîne ;
  - un bouton « Vérifier moi-même » qui recalcule toutes les empreintes dans le navigateur du visiteur ;
  - le tableau de performance par modèle, uniquement sur les prévisions scellées et échues ;
  - les derniers blocs, téléchargeables ;
  - les corrections ;
  - les commandes pour vérifier sans passer par le site (`shasum`, `certutil`).
- Le registre est enregistré chaque soir dans l'historique git, ce qui date chaque version.

### Le scanner (appli, section « Tous les titres »)
- Les 5 filtres existants sont gardés.
- 6 nouveaux filtres : tendance de fond (moyenne 200 jours), risque de forte chute, fiabilité de l'IA ici (détecteur de situations), dernier mois, résultats d'entreprise dans les 14 jours, taille.
- 4 exemples à un clic, présentés comme des exemples et non des recommandations.
- Enregistrement de scanners nommés, sur l'appareil (sans compte), et lien partageable qui rouvre l'appli avec les mêmes critères.
- Export CSV de la liste filtrée, avec la source et la date.
- Un titre qui n'a pas la donnée est écarté, jamais deviné. La taille n'est comparée que pour les titres en € ou en $, puisqu'elle est exprimée dans la devise du titre.
- Traduit dans l'appli anglaise.

### Corrections issues de l'audit
- Accueil, à propos, fonctionnalités, Google, images de partage, appli anglaise : les mêmes comptes partout, venant de la source unique.
- Description Google : le chiffre de réussite précise qu'il porte sur l'agitation.
- « Vos questions » (FR et EN) : les chiffres de confiance faible et forte viennent de l'examen du soir.
- Accueil anglais : plus de faux « Model unavailable ». Si aucun avis n'est net, la liste s'affiche avec une phrase qui le dit.
- Résultats réels : un encadré « À lire avant de juger » apparaît quand l'échantillon est court ou concentré sur un seul type de titre. Il explique aussi la fourchette ratée.
- Prédiction crypto : la phrase a été réécrite.

## 5. Tests faits
- **Registre (test unitaire, dossier temporaire)** :
  - scellement de l'historique (bloc 0) puis d'un soir (bloc 1) : OK ;
  - un deuxième scellement le même jour est refusé : OK ;
  - un chiffre modifié dans un fichier est détecté (« le fichier 2026-11-18.csv a été modifié »), puis la chaîne redevient intacte une fois le fichier remis : OK ;
  - nombres minuscules (PEPE à 0,0000089) et valeurs manquantes : OK ;
  - performance par modèle sur des cours fictifs : OK.
- **Vérification dans le navigateur** (Chromium) : le bouton « Vérifier moi-même » recalcule toutes les empreintes et affiche « chaîne intacte ».
- **Scanner** (Chromium, ordinateur et iPhone 13) :
  - les exemples, les filtres combinés (344 → 50 → 28 titres), l'enregistrement, la réapplication et la suppression d'un scanner, le lien partagé (#scan=…) qui rouvre les critères et l'export CSV fonctionnent ;
  - aucune erreur JavaScript, et aucun défilement horizontal sur mobile (grille passée à 2 colonnes) ;
  - le scanner est traduit dans l'appli anglaise.
- **Source unique** :
  - les jetons sont remplacés en français et en anglais ;
  - le contrôle automatique a trouvé un dernier « nearly 300 » oublié (description de l'appli anglaise), corrigé ;
  - les textes générés ont été vérifiés : à propos, fonctionnalités, accueil anglais, Vos questions FR et EN, prédiction crypto, description Google.
- **Résultats réels** : l'encadré « À lire avant de juger » a été testé avec les chiffres réels d'octobre (455 prédictions, 8 jours, fourchette 52 %).
- **Génération complète du site en démo** (`--demo`) : OK, 344 titres, aucun chiffre incohérent signalé, aucune page en erreur.

## 6. Limites honnêtes
- Le registre ne prouve la date des prévisions qu'à partir de sa création. Pour le bloc 0, la seule garantie est l'historique git.
- Les marges d'erreur affichées sont trop étroites : les prévisions d'un même soir ne sont pas indépendantes. C'est écrit sur les pages.
- Le scanner ne filtre que sur les ~340 titres analysés chaque heure. Les fiches simples n'y figurent pas (leurs données ne sont pas chargées dans l'appli, pour qu'elle reste légère).
- Pas de test d'amélioration de l'IA dans cette version : le temps est allé à la fiabilité des chiffres et à la preuve. Les avis sûrs à 82 % (v89) restent la dernière amélioration adoptée.

## 7. Ce qui demanderait une API ou une infrastructure en plus
- Un assistant conversationnel (vraie IA) : une API payante (Claude ou autre) et un petit serveur pour cacher la clé. Une clé dans le code public est interdite.
- L'horodatage indépendant du registre (OpenTimestamps sur Bitcoin, gratuit) : un outil en ligne de commande dans le robot GitHub. Faisable plus tard.
- Les actualités en temps réel et les données on-chain : la plupart des sources sérieuses sont payantes ou ont une licence restrictive. À vérifier avant tout usage.
- Des alertes poussées (prix, avis) : il existe déjà des alertes Telegram ; des notifications web demanderaient un serveur.

## 8. Nouvelles idées, rangées par utilité

| Idée | Utilité | Difficulté | Coût |
|---|---|---|---|
| Tableau de bord personnel (sur l'appareil, export/import) | forte | moyenne | gratuit |
| Page « Data du jour » | forte | faible | gratuit |
| Fiche titre en 6 parties | forte | moyenne | gratuit |
| Simulateur à plusieurs portefeuilles avec indice de comparaison | moyenne | moyenne | gratuit |
| Horodatage OpenTimestamps du registre | moyenne (crédibilité) | faible | gratuit |
| Comparaison des modèles sur le registre, mois par mois | moyenne | faible | gratuit |
| Assistant IA citant ses sources | moyenne | forte | payant (API) |
| Données on-chain | faible à moyenne | moyenne | souvent payant |
