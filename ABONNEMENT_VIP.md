# Abonnement « Radar Bourse+ » à 2 € par mois : ce qu'on peut faire, et ce qu'il ne faut pas faire

Document de travail du 25/11/2026. Ce n'est pas un avis juridique : avant d'encaisser le premier euro, fais-le relire
(un juriste, ou au minimum la page « Créer une activité » de l'URSSAF et les pages de l'AMF citées plus bas).

## 1. Ce qui est interdit ou dangereux

| Idée | Pourquoi c'est un problème | À la place |
|---|---|---|
| « Pronostics à plus de 88 % de réussite » | Aucune IA ne fait ça sur le sens d'une action à un mois (la nôtre : environ 56 % sur des années jamais vues). Annoncer 88 % serait une **publicité mensongère**. | Le 88 % existe, mais pour **l'agitation** (mois plus calme ou plus agité) : on peut le dire, avec le vrai chiffre vérifié. |
| « L'IA analyse en profondeur l'action que tu veux et te dit quoi faire » (payant) | Donner des recommandations **personnalisées** sur ce qu'il faut acheter ou vendre, c'est du **conseil en investissement** : il faut un statut agréé (CIF, inscrit à l'ORIAS, membre d'une association agréée par l'AMF). Sans statut : sanctions pénales possibles. | Vendre de l'**éducation et des outils** (cours, exercices, simulateurs, données), jamais « achète / vends ». |
| Cacher du contenu payant dans le site actuel | Le site est statique (sans serveur) : tout ce qui est dans la page peut être lu en 2 clics. Le « payant » serait contournable par n'importe qui. | Un vrai compte avec un serveur (voir § 3). |

Source : l'ESMA rappelle aux « finfluenceurs » que fournir des recommandations personnalisées est un conseil en investissement qui nécessite une autorisation (fiche France, janvier 2026).

## 2. Une offre qui serait propre

**Gratuit (comme aujourd'hui, rien n'est retiré)** : radar, fiches, graphiques, prévisions, résultats, outils, l'Académie avec **3 grandes leçons par jour**.

**Radar Bourse+ (2 €/mois, 1 mois d'essai gratuit)**, uniquement de l'éducation et du confort :
- leçons de l'Académie **illimitées**, cours longs et parcours avancé « Analyste financier » (bilans, DCF, flux de trésorerie, biais statistiques) ;
- cas pratiques sur de **vraies entreprises** (bilan, compte de résultat, fonds propres) avec correction ;
- « Dossier d'étude » d'une action au choix : tous les chiffres et graphiques réunis, **sans** recommandation d'achat ni de vente ;
- alertes personnalisées (seuils de prix, agitation), plusieurs portefeuilles virtuels, export ;
- pas de publicité (il n'y en a déjà pas : on garde ça comme promesse).

## 3. Ce qu'il faudrait mettre en place (dans l'ordre)

1. **Statut** : micro-entreprise (déclaration en ligne gratuite, URSSAF). Tu as 18 ans, c'est possible. Revenus à déclarer.
2. **Mentions légales, CGV, politique de confidentialité**, droit de rétractation de 14 jours expliqué (avec l'essai gratuit, c'est simple).
3. **Paiement** : un service qui gère la TVA européenne à ta place (« merchant of record », par exemple Lemon Squeezy ou Paddle), ou Stripe. **C'est toi qui crées le compte** : je ne crée pas de compte ni ne manipule de moyen de paiement.
4. **Comptes utilisateurs** : un petit serveur gratuit (par exemple Supabase ou Firebase) pour la connexion et pour vérifier l'abonnement. Le site garde son côté « sans compte » pour tout le gratuit.
5. **Limite des 3 leçons par jour** côté serveur (sinon contournable).

Coûts : 0 € au départ (offres gratuites), puis environ 5 % + quelques centimes par paiement selon le service.

## 4. Ma recommandation

Avant de coder le payant, attends d'avoir **au moins 300 à 500 visiteurs par jour** : à 2 €, il faut environ 1 abonné pour 100 visiteurs
réguliers. Aujourd'hui (environ 60 par jour), l'abonnement rapporterait quelques euros par mois pour beaucoup d'obligations.
D'ici là, je peux préparer le terrain : rallonger les leçons, créer le parcours avancé et les cas pratiques, en gratuit,
pour faire venir du monde. Le jour où tu lances le payant, ils basculeront dans Radar Bourse+.

Pages utiles : AMF, « Quelles sont les activités de conseil pouvant être exercées par un CIF ? » ; ESMA, fiche « Finfluencers » France.
