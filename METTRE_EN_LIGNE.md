# 🌐 Mettre Radar Bourse en ligne (gratuit, toujours actif)

Une fois ces étapes faites, le site est en ligne 24 h/24 à une adresse du type
`https://ton-pseudo.github.io/radar-bourse/`, même quand ton PC est éteint.

**Ce qui se met à jour tout seul :**
- les **cours des cryptos** : en direct, chaque seconde, directement dans la page ;
- les **cours des actions US** : en direct si tu ajoutes une clé Finnhub (étape 6) ;
- les **prévisions et les actions françaises** : toutes les heures en semaine, toutes les 3 h le week-end ;
- le **suivi des prédictions** : enregistré chaque soir.

## ⚡ Méthode rapide : le script automatique

1. Aie un compte GitHub (gratuit, sur https://github.com).
2. Double-clique sur **`mettre_en_ligne.bat`**.
3. Réponds aux questions (souvent juste Entrée). **N'appuie jamais sur Ctrl+C** : ça arrête le script.

Le script installe les outils manquants sans redémarrage, te connecte à GitHub (le code de connexion
est copié tout seul : fais Ctrl+V dans la page GitHub), teste le site sur ton PC, crée ou met à jour
le dépôt, active l'hébergement, suit la publication et vérifie que le site répond.
Il crée à la fin un raccourci « Mon site Radar Bourse » dans le dossier.

Tes réponses sont mémorisées : pour envoyer une nouvelle version plus tard, relance-le, il ne
repose pas les questions. En cas d'erreur, il écrit les détails dans `erreur_mise_en_ligne.txt`.

---

## Méthode manuelle (si le script ne marche pas)

## 1. Créer un compte GitHub

Va sur https://github.com et crée un compte gratuit. Ton pseudo apparaîtra dans l'adresse du site.

## 2. Créer le dépôt

En haut à droite : **+ → New repository**.
- Nom : `radar-bourse`
- Visibilité : **Public** (GitHub Pages est gratuit seulement pour les dépôts publics)
- Clique **Create repository**.

## 3. Envoyer les fichiers

Sur la page du dépôt vide, clique **uploading an existing file**.
Ouvre le dossier dézippé, sélectionne **tout son contenu** (y compris le dossier `.github`) et glisse-le
dans la page. Puis clique **Commit changes**.

> Si le dossier `.github` n'apparaît pas dans la liste envoyée : **Add file → Create new file**,
> tape `.github/workflows/radar.yml` comme nom, colle le contenu du fichier `radar.yml`, puis **Commit**.

## 4. Remplir les mentions légales

Dans le dépôt, ouvre `bourse_bot/config.py`, clique sur le crayon ✏️ et remplace à la fin du fichier :
- `[ton prénom ou pseudo]` par ton prénom ou un pseudo ;
- `[ton adresse e-mail de contact]` par une adresse e-mail (tu peux en créer une dédiée au projet).

Clique **Commit changes**.

## 5. Activer GitHub Pages

**Settings → Pages → Build and deployment → Source : GitHub Actions.**

## 6. (Optionnel) Actions US en direct

1. Crée un compte gratuit sur https://finnhub.io et copie ta **API key**.
2. Dans le dépôt : **Settings → Secrets and variables → Actions → New repository secret**.
3. Nom : `FINNHUB_KEY`, valeur : ta clé. **Add secret.**

La clé sera visible dans le code de la page (c'est inévitable sans serveur). Utilise un compte Finnhub
dédié au projet, gratuit, sans moyen de paiement.

## 7. Premier lancement

Onglet **Actions** → si GitHub le demande, clique **I understand my workflows, go ahead and enable them**
→ **Mise à jour du Radar** → **Run workflow**.

Après 3 à 6 minutes, la coche devient verte. L'adresse du site s'affiche dans
**Settings → Pages** (et dans le résultat de l'étape « publier »).

## En cas de souci

- **Croix rouge dans Actions** : clique dessus, puis sur l'étape en rouge, et copie le message d'erreur.
- **Yahoo bloque parfois les serveurs de GitHub** : le site garde alors la dernière version publiée,
  et l'exécution suivante (une heure plus tard) réessaie.
- GitHub peut retarder les exécutions programmées de quelques minutes, c'est normal.

## Nom de domaine personnalisé (facultatif)

Une adresse comme `radarbourse.fr` (7 à 12 € par an) inspire plus confiance qu'une adresse en
`github.io`. Achète le nom (OVH, Gandi, Namecheap, Cloudflare), **active la protection WHOIS** pour
que ton nom n'apparaisse pas publiquement, puis double-clique sur **`nom_de_domaine.bat`** : il
t'indique les réglages DNS à faire et branche le domaine sur ton site. Pour revenir à l'adresse
github.io, relance-le et réponds « aucun ».

## À savoir

- Garde le site **gratuit et sans publicité** : les données de Yahoo Finance sont réservées à un usage
  non commercial, et faire payer des signaux boursiers relève d'une activité réglementée par l'AMF.
- Les textes légaux fournis sont une base sérieuse, mais ce n'est pas un avis juridique. Relis-les avant de publier.
