# Donner une vraie adresse au site (ex : radarbourse.fr)

Ton site est déjà en ligne, gratuitement, à l'adresse `https://maxitemmmm-eng.github.io/radar-bourse/`.
Avec ton propre nom de domaine, il aura une adresse courte et pro. L'hébergement reste gratuit chez GitHub ; seul le nom coûte environ **7 à 12 € par an**.

## Le plus simple : double-clic sur `nom_de_domaine.bat`

Le script te guide en 5 étapes et vérifie tout lui-même.

1. **Le nom** : tu tapes le nom voulu (ex : `radarbourse.fr`).
2. **L'achat** : la page d'OVHcloud s'ouvre. Tu achètes le nom pour 1 an. Le paiement, c'est toi qui le fais.
   - Refuse les options payantes (hébergement, e-mail…) : elles ne servent à rien ici.
   - **Anonymat** : active la « protection WHOIS » / « masquer mes informations ». C'est gratuit pour les .fr des particuliers. Sans ça, ton vrai nom serait visible dans l'annuaire public des domaines.
3. **La zone DNS** : chez OVH, va dans Noms de domaine → ton nom → onglet « Zone DNS ».
   - Supprime les lignes A et AAAA déjà présentes pour le nom principal.
   - Ajoute ces 4 lignes de type **A** (sous-domaine vide) :
     `185.199.108.153` · `185.199.109.153` · `185.199.110.153` · `185.199.111.153`
   - Ajoute 1 ligne **CNAME** : sous-domaine `www`, cible `maxitemmmm-eng.github.io.`
4. **La vérification** : le script attend que le nom pointe bien vers GitHub. Ça peut prendre quelques minutes, parfois quelques heures. S'il s'arrête avant, ce n'est pas grave : relance-le plus tard.
5. **GitHub** : le script règle tout seul l'adresse, le cadenas https et la nouvelle publication du site.

## Après

- L'ancienne adresse github.io renvoie automatiquement vers la nouvelle, et Google suit tout seul.
- Dans la Search Console, il faut ajouter la nouvelle adresse et y renvoyer `sitemap.xml`. Je peux le faire avec toi dans le navigateur de l'appli.
- Pour revenir en arrière : relance `nom_de_domaine.bat` et tape `aucun`.

## Ce qu'il ne faut pas faire

- Pas de nom avec une marque connue (« boursorama-ia.fr »…) : c'est risqué juridiquement.
- Ne laisse pas le nom expirer : active le **renouvellement automatique** chez le vendeur, sinon le site redevient inaccessible à cette adresse.
