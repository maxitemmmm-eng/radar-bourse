# Activer les fils de discussion (Giscus) : 5 minutes, gratuit

Les discussions sont stockées dans l'onglet « Discussions » de ton dépôt GitHub. Tout le monde peut les lire ;
pour écrire, il faut un compte GitHub gratuit. Toi, tu modères (supprimer un message, bloquer quelqu'un, verrouiller un fil).

1. Sur GitHub, ouvre ton dépôt du site → **Settings** → coche **Discussions** (rubrique « Features »).
2. Dans l'onglet **Discussions**, crée une catégorie (crayon à côté de « Categories ») nommée **Fils du site**,
   de type **Announcement** (seuls toi et Giscus créent les fils ; les visiteurs répondent dedans).
3. Va sur https://github.com/apps/giscus → **Install** → choisis seulement ton dépôt du site.
4. Va sur https://giscus.app/fr, tape `ton-pseudo/ton-depot`, choisis la catégorie « Fils du site ».
   Plus bas, la page affiche un code avec `data-repo`, `data-repo-id` et `data-category-id`.
5. Sur GitHub : **Settings → Secrets and variables → Actions → onglet Variables → New repository variable**, crée :
   - `GISCUS_REPO` = la valeur de `data-repo` (ex. `maxitemmmm-eng/radar-bourse`)
   - `GISCUS_REPO_ID` = la valeur de `data-repo-id`
   - `GISCUS_CATEGORY_ID` = la valeur de `data-category-id`

À la mise à jour suivante du site, un fil apparaît en bas de chaque fiche (un fil par titre) et sur la page « Discussions ».

## Modération (les liens interdits)

GitHub ne peut pas bloquer automatiquement les liens. Les règles (pas de liens, pas de pub, pas de signaux d'achat) sont
affichées au-dessus de chaque fil ; quand quelqu'un les enfreint :
- message : « … » → **Delete** ; récidive : **Block user** (depuis son profil, ou Settings → Moderation → Blocked users) ;
- en cas d'attaque : Settings → **Moderation options → Interaction limits** (limite l'écriture aux comptes connus pendant 24 h à 6 mois).
Active les notifications de l'onglet Discussions (bouton **Watch → All activity**) pour voir chaque nouveau message.
