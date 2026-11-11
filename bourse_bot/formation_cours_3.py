"""Version 71 : l'Académie — niveau 6, « Comprendre la crypto » (vérifié le 11/11/2026 : AMF, textes fiscaux 2026)."""

COURS_6 = [
    dict(
        id="blockchain-bitcoin", niveau=6, minutes=7,
        titre="Blockchain et bitcoin : comment ça marche",
        desc="Le registre partagé, le minage, la rareté du bitcoin et le halving, sans jargon.",
        mots="blockchain expliquée simplement, comment fonctionne le bitcoin, halving bitcoin, minage bitcoin débutant, crypto pour débutant",
        sections=[
            ("Un grand registre partagé",
             "<p>Une <b>blockchain</b> est un registre de transactions copié sur des milliers d'ordinateurs dans le monde. Chaque nouveau « bloc » de transactions "
             "est relié au précédent, ce qui rend la falsification du passé extrêmement difficile : il faudrait réécrire la majorité des copies en même temps.</p>"),
            ("Le bitcoin",
             "<p>Lancé en 2009 par une personne (ou un groupe) sous le pseudonyme Satoshi Nakamoto, le bitcoin est la première cryptomonnaie. "
             "Son nombre total est plafonné à <b>21 millions</b>. Les nouveaux bitcoins sont créés par le <b>minage</b> : des ordinateurs valident les transactions "
             "et reçoivent une récompense.</p>"),
            ("Le halving",
             "<p>Environ tous les quatre ans (tous les 210 000 blocs), la récompense des mineurs est divisée par deux : c'est le <b>halving</b>. Le dernier a eu lieu en avril 2024. "
             "Il ralentit la création de nouveaux bitcoins. Beaucoup y voient un moteur de hausse, mais rien ne garantit que le passé se répète.</p>"),
            ("Ce que ça ne dit pas",
             "<p>La technologie peut être solide sans que le prix le soit. Le bitcoin a déjà perdu plus de 70 % plusieurs fois (2014, 2018, 2022). "
             "Comprendre la blockchain n'aide pas à prévoir le cours : sur Radar Bourse, l'IA affiche d'ailleurs toujours une confiance faible sur le sens du prix des cryptos.</p>"),
        ],
        retenir=["Une blockchain est un registre partagé et très difficile à falsifier.", "Le bitcoin est plafonné à 21 millions d'unités.",
                 "Le halving divise la récompense des mineurs par deux tous les ~4 ans (dernier : avril 2024).", "Technologie solide ne veut pas dire prix stable."],
        quiz=[("Combien de bitcoins existeront au maximum ?", ["1 million", "21 millions", "100 millions", "Aucune limite"], 1, "Le protocole plafonne l'offre à 21 millions de bitcoins."),
              ("Le halving, c'est…", ["Le prix divisé par deux", "La récompense des mineurs divisée par deux", "Une taxe", "Une panne"], 1, "Environ tous les 4 ans, la récompense par bloc est divisée par deux."),
              ("Le bitcoin a-t-il déjà perdu plus de 70 % de sa valeur ?", ["Jamais", "Oui, plusieurs fois", "Une seule fois", "Seulement en 2009"], 1, "Par exemple en 2018 et en 2022, après des sommets."),
              ],
        exercice=("<p>La récompense par bloc était de 50 bitcoins en 2009. Après 4 halvings (2012, 2016, 2020, 2024), combien vaut-elle ?</p>",
                  "<p>50 → 25 → 12,5 → 6,25 → <b>3,125 bitcoins</b> par bloc depuis avril 2024.</p>"),
        sources=[("Livre blanc du bitcoin (Satoshi Nakamoto, 2008)", "https://bitcoin.org/bitcoin.pdf"),
                 ("AMF : les crypto-actifs", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/crypto-actifs")],
    ),
    dict(
        id="altcoins-stablecoins", niveau=6, minutes=6,
        titre="Ethereum, altcoins, stablecoins, memecoins",
        desc="Les grandes familles de cryptos et ce qui les distingue vraiment.",
        mots="c'est quoi ethereum, altcoin définition, stablecoin explication, memecoin risque, différentes cryptomonnaies",
        sections=[
            ("Ethereum et les plateformes",
             "<p>Ethereum n'est pas seulement une monnaie : c'est une plateforme où l'on peut programmer des « contrats intelligents » (applications qui s'exécutent toutes seules). "
             "Solana, Avalanche ou Cardano jouent sur le même terrain. Leur valeur dépend en partie de l'usage réel de leur réseau.</p>"),
            ("Les stablecoins",
             "<p>Un stablecoin vise un prix fixe, en général 1 dollar ou 1 euro (USDT, USDC…). Il sert à passer d'une crypto à l'autre sans repasser par la banque. "
             "Il n'est pas sans risque : sa stabilité dépend des réserves de l'émetteur. En 2022, le stablecoin TerraUSD (UST) a perdu son ancrage et s'est effondré presque à zéro.</p>"),
            ("Les memecoins",
             "<p>Dogecoin, Shiba Inu, Pepe… Ces cryptos sont nées comme des blagues. Elles n'ont souvent aucun usage particulier, et leur prix dépend surtout de la mode "
             "et des réseaux sociaux. Elles peuvent faire ×10… ou −90 %. C'est le terrain le plus risqué de la crypto.</p>"),
            ("Sur Radar Bourse",
             "<p>Le radar suit plus de 100 cryptos : compare l'agitation prévue d'un memecoin à celle du bitcoin, et regarde la page <a href='../prediction-crypto.html'>prédiction crypto</a>.</p>"),
        ],
        retenir=["Ethereum et ses concurrents sont des plateformes programmables.", "Un stablecoin vise un prix fixe mais dépend de ses réserves.",
                 "Les memecoins sont les cryptos les plus spéculatives.", "Plus une crypto est petite et à la mode, plus elle est agitée."],
        quiz=[("Un stablecoin cherche à…", ["Doubler chaque année", "Garder un prix fixe, souvent 1 dollar", "Remplacer les actions", "Payer des dividendes"], 1, "Il vise un prix stable, adossé à des réserves."),
              ("Qu'est-il arrivé au stablecoin TerraUSD en 2022 ?", ["Il a doublé", "Il a perdu son ancrage et s'est effondré", "Il est devenu une action", "Rien"], 1, "UST a perdu son ancrage au dollar et s'est effondré, entraînant de lourdes pertes."),
              ("Les memecoins sont en général…", ["Les cryptos les plus sûres", "Très spéculatifs", "Garantis par l'État", "Des obligations"], 1, "Leur prix dépend surtout de la mode : risque extrême."),
              ],
        exercice=("<p>Ouvre la fiche du <a href='../titres/btc-usd.html'>Bitcoin</a> puis celle du <a href='../titres/doge-usd.html'>Dogecoin</a>. Compare leur agitation prévue sur un mois. "
                  "Laquelle est la plus risquée ?</p>",
                  "<p>En général, le Dogecoin a une agitation prévue nettement plus élevée que le Bitcoin : un memecoin réagit plus violemment aux modes. "
                  "Plus l'agitation est forte, plus la perte possible en un mois est grande.</p>"),
        sources=[("AMF : les crypto-actifs", "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/crypto-actifs"),
                 ("Banque de France : les stablecoins", "https://www.banque-france.fr/fr")],
    ),
    dict(
        id="acheter-conserver-crypto", niveau=6, minutes=7,
        titre="Acheter et conserver des cryptos en sécurité",
        desc="Plateformes agréées (MiCA), portefeuilles, clés privées : les règles depuis le 1er juillet 2026.",
        mots="acheter crypto en france, plateforme crypto agréée amf, mica psca, portefeuille crypto ledger, clé privée crypto, sécuriser ses cryptos",
        sections=[
            ("Choisir une plateforme autorisée",
             "<p>Depuis le <b>1er juillet 2026</b>, avec la fin de la période de transition du règlement européen <b>MiCA</b>, seuls les prestataires agréés "
             "(PSCA, ou CASP en anglais) peuvent proposer des services sur crypto-actifs en France. Vérifie toujours la <b>liste blanche de l'AMF</b> avant d'ouvrir un compte.</p>"),
            ("Les portefeuilles",
             "<ul><li><b>Sur la plateforme</b> : simple, mais la plateforme garde tes cryptos. Si elle fait faillite ou est piratée, tu peux tout perdre (FTX, 2022).</li>"
             "<li><b>Portefeuille logiciel</b> (une appli) : tu gardes toi-même tes clés, sur ton téléphone ou ton ordinateur.</li>"
             "<li><b>Portefeuille matériel</b> (une clé physique) : les clés restent hors ligne, c'est le plus sûr pour de grosses sommes.</li></ul>"),
            ("La clé privée et la phrase de récupération",
             "<p>Posséder une crypto, c'est posséder la <b>clé privée</b> qui permet de la dépenser. La phrase de récupération (12 ou 24 mots) permet de la retrouver. "
             "<b>Ne la donne jamais à personne</b>, ne la prends pas en photo, ne la tape sur aucun site : aucun service sérieux ne te la demandera jamais.</p>"),
            ("Les erreurs irréversibles",
             "<p>Une transaction crypto envoyée à la mauvaise adresse ne peut pas être annulée. Envoie d'abord un petit montant test, vérifie le réseau utilisé, "
             "et méfie-toi des faux sites et des faux supports techniques.</p>"),
        ],
        retenir=["Depuis le 1er juillet 2026, seules les plateformes agréées MiCA peuvent opérer en France : vérifie la liste blanche de l'AMF.",
                 "Laisser ses cryptos sur une plateforme, c'est lui faire confiance.", "Ta phrase de récupération ne se donne jamais.",
                 "Une transaction crypto est irréversible."],
        quiz=[("Depuis quand seules les plateformes agréées MiCA peuvent-elles opérer en France ?", ["2019", "1er juillet 2026", "2030", "Il n'y a pas de règle"], 1,
               "La période transitoire des anciens PSAN s'est terminée le 1er juillet 2026."),
              ("Quelqu'un te demande ta phrase de récupération pour « débloquer ton compte ». Tu…", ["La donnes", "Refuses : c'est une arnaque", "La donnes à moitié", "L'envoies par mail"], 1,
               "Aucun service légitime ne demande jamais ta phrase de récupération."),
              ("Le portefeuille le plus sûr pour une grosse somme est souvent…", ["Le compte sur un site inconnu", "Un portefeuille matériel hors ligne", "Une capture d'écran", "Un mail"], 1,
               "Les clés restent hors ligne, à l'abri des piratages en ligne."),
              ],
        exercice=("<p>Avant d'envoyer 500 € de crypto vers une nouvelle adresse, quelles sont les trois vérifications à faire ?</p>",
                  "<p>1) Vérifier l'adresse caractère par caractère (ou via un QR code de confiance) ; 2) vérifier que le <b>réseau</b> choisi est le même des deux côtés ; "
                  "3) envoyer d'abord un <b>petit montant test</b>, attendre qu'il arrive, puis envoyer le reste.</p>"),
        sources=[("AMF : fin de la période transitoire des PSAN (1er juillet 2026)", "https://www.amf-france.org/fr/actualites-publications/actualites/lamf-rappelle-que-la-periode-transitoire-pour-les-psan-pour-continuer-de-fournir-des-services-sur"),
                 ("AMF : listes blanches et listes noires", "https://www.amf-france.org/fr/espace-epargnants/proteger-son-epargne/listes-noires-et-mises-en-garde")],
    ),
    dict(
        id="fiscalite-crypto-2026", niveau=6, minutes=7,
        titre="Crypto : fiscalité et déclaration en 2026",
        desc="Flat tax à 31,4 %, seuil de 305 €, échanges crypto-crypto, formulaires 2086 et 3916-bis.",
        mots="fiscalité crypto 2026, impôt crypto france, déclarer ses cryptos, formulaire 2086, 3916 bis crypto, flat tax crypto 31,4",
        sections=[
            ("Quand paie-t-on des impôts ?",
             "<p>En France, tu es imposé quand tu <b>vends des cryptos contre des euros</b> (ou que tu paies un bien ou un service avec). "
             "Échanger une crypto contre une autre crypto (y compris un stablecoin) n'est <b>pas</b> imposé au moment de l'échange : l'impôt est reporté jusqu'à la sortie en euros.</p>"),
            ("Le taux",
             "<p>Les plus-values de cession de crypto-actifs des particuliers sont taxées au prélèvement forfaitaire unique : <b>31,4 % en 2026</b> "
             "(12,8 % d'impôt sur le revenu + 18,6 % de prélèvements sociaux, après la hausse de la CSG votée pour 2026). L'option pour le barème progressif reste possible.</p>"),
            ("Le seuil de 305 €",
             "<p>Si le total de tes <b>cessions</b> (ventes contre euros) de l'année ne dépasse pas <b>305 €</b>, tu n'as pas d'impôt. Attention : c'est le montant des ventes qui compte, "
             "pas celui de la plus-value, et ce n'est pas un abattement : au-delà, toute la plus-value est imposable.</p>"),
            ("Les formulaires",
             "<ul><li><b>2086</b> : le détail de chaque cession imposable (avec une formule de prix moyen d'acquisition sur l'ensemble du portefeuille).</li>"
             "<li><b>2042 C</b> : le report du gain (case 3AN) ou de la perte (case 3BN).</li>"
             "<li><b>3916-bis</b> : chaque compte ouvert sur une plateforme étrangère, chaque année, même sans opération. L'oubli coûte 750 € par compte (1 500 € au-delà de 50 000 €).</li></ul>"),
        ],
        retenir=["Imposition à la vente contre euros, pas lors des échanges crypto-crypto.", "Flat tax de 31,4 % en 2026.",
                 "Cessions annuelles ≤ 305 € : pas d'impôt.", "Formulaires 2086 et 3916-bis ; oubli d'un compte étranger : 750 € d'amende."],
        quiz=[("Échanger du bitcoin contre de l'ether est-il imposé au moment de l'échange ?", ["Oui", "Non, l'impôt est reporté à la vente en euros", "Seulement le dimanche", "Toujours à 50 %"], 1,
               "Les échanges entre crypto-actifs ne déclenchent pas l'impôt ; c'est la sortie en euros qui compte."),
              ("Le taux du prélèvement forfaitaire sur les plus-values crypto en 2026 est de…", ["17,2 %", "30 %", "31,4 %", "45 %"], 2, "12,8 % + 18,6 % = 31,4 %."),
              ("Quel formulaire sert à déclarer un compte sur une plateforme crypto étrangère ?", ["2086", "3916-bis", "2042", "Aucun"], 1, "Le 3916-bis, chaque année, même sans opération."),
              ],
        exercice=("<p>En 2026, tu as vendu pour 2 000 € de bitcoin. Selon la formule officielle, ta plus-value imposable est de 600 €. Combien paies-tu au prélèvement forfaitaire ? "
                  "Et si tu n'avais vendu que pour 300 € ?</p>",
                  "<p>2 000 € de cessions dépassent 305 € : 600 × 31,4 % = <b>188,40 €</b>. Avec 300 € de cessions seulement (sous le seuil de 305 €), <b>0 €</b> d'impôt.</p>"),
        sources=[("Fiscalité des cryptomonnaies en 2026 (taux, seuil, formulaires)", "https://www.hagnere-patrimoine.fr/guides-patrimoine/comment-payer-moins-impots/fiscalite-cryptomonnaies-2026"),
                 ("impots.gouv.fr", "https://www.impots.gouv.fr")],
    ),
]
