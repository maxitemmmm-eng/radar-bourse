# Ouvrir l'analyse approfondie (gratuit, sans SIRET) — et plus tard, si tu veux, la vente

> ⚠️ **Ne donne jamais tes mots de passe, tes clés ou tes jetons à personne, Claude compris.**
> Ils se tapent uniquement dans la fenêtre du script, sur ton PC.

## Aujourd'hui : mode GRATUIT (pas besoin de SIRET)

Tout le site est gratuit et sans limite (l'Académie, le parcours Analyste…). Seule l'**analyse approfondie à la demande**
a besoin d'un petit serveur gratuit pour fonctionner : chacun pourra en lancer **3 par jour**, sans compte.

Ce qu'il te faut :
1. **Cloudflare** (cloudflare.com, gratuit) : crée le compte, ouvre une fois **Workers & Pages** et choisis ton sous-domaine.
   Puis Mon profil → **API Tokens → Create Token → modèle « Edit Cloudflare Workers »** → copie le jeton.
2. **GitHub** (quand ton accès est revenu) : Settings → Developer settings → **Fine-grained tokens**, deux jetons limités au dépôt du site :
   - **A « installation »** : Variables + Secrets (Read and write) — tu pourras le supprimer après ;
   - **B « serveur »** : Actions (Read and write) seulement.
3. Double-clique sur **installer_abonnement.bat**, choisis **1 = GRATUIT**, colle tes jetons. C'est tout.

À la mise à jour suivante du site, la page « Analyse approfondie » est ouverte à tous.

## Plus tard (si un jour tu as un SIRET) : rallumer la vente

Tout le code de Radar Bourse+ (2 €/mois, 1 mois offert) est gardé de côté, rien n'est supprimé. Pour le rallumer :
1. micro-entreprise → SIRET ; compte **Stripe** avec ton IBAN tapé dans Stripe (commence en mode test) ;
2. relance **installer_abonnement.bat**, choisis **2 = VENTE**, donne ton identité de vendeur et ta clé `sk_test_…` ;
3. teste avec la carte `4242 4242 4242 4242`, puis relance le script avec ta clé `sk_live_…`.

## Ce qui est protégé

- Les analyses ne peuvent être lancées que par ton serveur (jamais par un inconnu sur GitHub), sur un symbole vérifié.
- Les adresses IP ne sont jamais gardées en clair (seulement une empreinte, pour compter les 3 analyses par jour).
- Aucune clé n'est enregistrée sur ton ordinateur ; elles sont rangées dans Cloudflare et GitHub (chiffrées).
