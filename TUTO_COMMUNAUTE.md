# Installer la communauté (comptes, commentaires, discussions) — gratuit, 10 minutes

Une seule fois. Ensuite tout tourne tout seul, même PC éteint.

## 1. Cloudflare (gratuit)
1. Crée un compte sur **dash.cloudflare.com** (gratuit, pas de carte bancaire).
2. Dans le menu de gauche, ouvre **Workers & Pages** une fois et choisis ton sous-domaine (ex. `radarbourse`).
3. En haut à droite : **Mon profil → Jetons d'API → Créer un jeton → modèle « Modifier Cloudflare Workers »** → Continuer → Créer.
   Copie le jeton (il ne s'affiche qu'une fois).

## 2. GitHub
1. GitHub → photo de profil → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. *Repository access* : **Only select repositories** → ton dépôt du site.
3. *Permissions* → *Repository permissions* → **Variables : Read and write**. Rien d'autre.
4. Generate token, copie-le. Tu pourras le supprimer après l'installation.

## 3. Lancer
Double-clique sur **installer_communaute.bat**, réponds aux questions, colle les deux jetons (rien ne s'affiche quand tu colles : c'est normal).

À la fin, le script affiche **ta clé de modération** (et l'enregistre dans ton dossier personnel, hors du site).
**Ne la donne à personne, Claude compris.**

## 4. Après
- Le site affiche « Mon compte », « Discussions » et les commentaires à sa prochaine mise à jour (dans l'heure).
- Pour modérer : va sur **radarbourse.fr/moderation.html**, colle ta clé une fois. Tu vois les commentaires signalés et récents :
  supprimer, rétablir, suspendre un compte.
- Les commentaires avec un lien ou une insulte sont refusés automatiquement ; 3 signalements cachent un commentaire en attendant ta décision.

## Limites (version gratuite de Cloudflare)
1 000 écritures par jour (inscriptions, commentaires, sauvegardes) et 100 000 lectures : largement assez au début.
Si un jour ça ne suffit plus, l'offre payante de Cloudflare coûte environ 5 $ par mois.
