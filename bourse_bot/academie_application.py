"""Version 83 : un « exercice d'application » en fin de chapitre, plus exigeant que les exercices des mini-leçons.

Plusieurs étapes de calcul, une réponse chiffrée à saisir, une correction qui détaille la méthode.
Les réponses sont CALCULÉES ici (pas recopiées à la main) pour éviter toute erreur.
"""


def _f(x, d=2):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s.rstrip("0").rstrip(",") if "," in s else s


def _ex(q, rep, tol, unite, expl):
    return {"type": "nombre", "q": q, "rep": round(rep, 4), "tol": tol, "unite": unite, "expl": expl}


def _tous():
    A = {}
    # rendement et risque : perte puis hausse
    v = 10000 * (1 - .35) * (1 + .35)
    A["rendement-risque"] = _ex("Tu places 10 000 €. La première année : −35 %. La deuxième : +35 %. Combien as-tu à la fin, en € ?", v, 1, "€",
                                f"10 000 × 0,65 = 6 500 €, puis 6 500 × 1,35 = {_f(v)} €. Une baisse puis une hausse du même pourcentage ne ramènent pas au départ : "
                                "il manque 1 225 €.")
    # intérêts composés : règle de 72 vs calcul exact
    import math
    n = math.log(2) / math.log(1.06)
    A["interets-composes"] = _ex("À 6 % par an, combien d'années faut-il exactement pour doubler un capital (à 0,1 an près) ? Compare avec la règle de 72.", n, .1, "ans",
                                 f"On cherche n tel que 1,06ⁿ = 2, soit n = ln 2 ÷ ln 1,06 = {_f(n, 1)} ans. La règle de 72 donne 72 ÷ 6 = 12 ans : une très bonne approximation.")
    # indices : dividendes
    p = (1.04 * 1.03 - 1) * 100
    A["indices-cac40-sp500"] = _ex("Un indice de prix monte de 4 % sur l'année et ses entreprises versent 3 % de dividendes, réinvestis. Quelle est la performance "
                                   "de l'indice « dividendes réinvestis », en % ?", p, .05, "%",
                                   f"(1 + 0,04) × (1 + 0,03) − 1 = {_f(p)} %. L'indice de prix (le CAC 40 affiché partout) oublie environ 3 points par an.")
    # PEA / CTO
    g = 8000
    A["pea-cto-assurance-vie"] = _ex("Tu retires un gain de 8 000 €, réalisé en 2026, d'un PEA ouvert il y a 6 ans. Combien de prélèvements paies-tu, en € ?", g * .186, 1, "€",
                                     f"Après 5 ans, pas d'impôt sur le revenu : seulement les prélèvements sociaux, 18,6 % × 8 000 = {_f(g * .186)} €. "
                                     f"Sur un compte-titres, ce serait 31,4 % = {_f(g * .314)} €.")
    # courtier : frais annuels
    f1, f2 = 12 * 2.0, 12 * 200 * .005
    A["choisir-son-courtier"] = _ex("Tu achètes 200 € d'ETF chaque mois. Courtier A : 2 € par ordre. Courtier B : 0,5 % du montant. Combien d'euros économises-tu par an "
                                    "avec le moins cher ?", abs(f1 - f2), .5, "€",
                                    f"A : 12 × 2 = {_f(f1)} € (soit 1 % de chaque achat). B : 12 × 200 × 0,5 % = {_f(f2)} €. Écart : {_f(abs(f1 - f2))} €. "
                                    "Sur de petits montants, un frais fixe pèse lourd.")
    # passer un ordre : carnet
    cout = 180 * 20.05 + 120 * 20.08
    A["passer-un-ordre"] = _ex("Dans le carnet, les vendeurs proposent 180 titres à 20,05 €, puis 520 à 20,08 €. Tu passes un ordre au marché pour 300 titres. "
                               "Quel prix moyen paies-tu par titre, en € (au centime) ?", cout / 300, .005, "€",
                               f"180 × 20,05 + 120 × 20,08 = {_f(cout)} €, divisé par 300 = {_f(cout / 300, 3)} €. Un ordre au marché « remonte » le carnet : "
                               "avec un ordre à cours limité, tu aurais fixé ton prix maximum.")
    # ETF : frais sur 20 ans
    a, b = 10000 * 1.06 ** 20, 10000 * (1.06 - .018) ** 20
    A["etf-debutant"] = _ex("10 000 € placés 20 ans à 6 % par an. Un ETF à 0,2 % de frais contre un fonds à 2 % : quel écart final, en € ? (tolérance 1 %)",
                            10000 * (1.058) ** 20 - 10000 * (1.04) ** 20, (10000 * (1.058) ** 20 - 10000 * (1.04) ** 20) * .01, "€",
                            f"ETF : 10 000 × 1,058²⁰ = {_f(10000 * 1.058 ** 20, 0)} €. Fonds : 10 000 × 1,04²⁰ = {_f(10000 * 1.04 ** 20, 0)} €. "
                            f"Écart : {_f(10000 * 1.058 ** 20 - 10000 * 1.04 ** 20, 0)} €, pour la même performance des marchés.")
    # investir régulièrement
    px = [40, 32, 50]
    parts = sum(150 / x for x in px)
    A["investir-regulierement"] = _ex("Tu investis 150 € par mois pendant 3 mois, aux prix de 40 €, 32 € puis 50 €. Quel est ton prix de revient moyen par part, en € ?",
                                      450 / parts, .01, "€",
                                      f"Parts : 150/40 + 150/32 + 150/50 = {_f(parts, 4)}. Prix moyen = 450 ÷ {_f(parts, 4)} = {_f(450 / parts)} €, "
                                      f"sous la moyenne des prix ({_f(sum(px) / 3)} €).")
    # lire les comptes : marge nette
    A["lire-les-comptes"] = _ex("Une entreprise fait 2 400 M€ de chiffre d'affaires, 336 M€ de résultat d'exploitation et 204 M€ de bénéfice net. Quelle est sa marge nette, en % ?",
                                204 / 2400 * 100, .05, "%", f"Marge nette = bénéfice net ÷ chiffre d'affaires = 204 ÷ 2 400 = {_f(204 / 2400 * 100)} %. "
                                f"Marge d'exploitation : 336 ÷ 2 400 = {_f(336 / 2400 * 100)} %.")
    # PER
    A["ratios-per-rendement"] = _ex("Une action vaut 84 €, son bénéfice par action est de 6 € et son dividende de 2,52 €. Quel est son PER ?", 14, .05, "",
                                    "PER = 84 ÷ 6 = 14 : le marché paie 14 années de bénéfices actuels. Rendement du dividende : 2,52 ÷ 84 = 3 %. "
                                    "Taux de distribution : 2,52 ÷ 6 = 42 % du bénéfice.")
    # dividendes
    n_ = 120 * 1.85 * (1 - .314)
    A["dividendes"] = _ex("Tu détiens 120 actions sur un compte-titres. Dividende : 1,85 € par action, flat tax 31,4 %. Combien touches-tu net, en € ?", n_, .05, "€",
                          f"Brut : 120 × 1,85 = 222 €. Net : 222 × (1 − 0,314) = {_f(n_)} €. Le jour du détachement, le cours baisse d'environ 1,85 €.")
    # volatilité
    m = 25 / 12 ** .5
    A["volatilite-et-ia"] = _ex("Une action a une volatilité de 25 % par an. Quelle agitation « habituelle » sur un mois, en % (12 mois par an) ?", m, .1, "%",
                                f"Volatilité sur un mois = annuelle ÷ √12 = 25 ÷ 3,46 = {_f(m, 1)} %. Environ 2 mois sur 3, la variation reste dans ±{_f(m, 1)} %.")
    # krachs
    A["krachs-et-cycles"] = _ex("Un indice perd 49 % entre son sommet et son creux. De combien doit-il remonter pour retrouver son sommet, en % ?", (1 / .51 - 1) * 100, .2, "%",
                                f"Hausse nécessaire = 1 ÷ (1 − 0,49) − 1 = {_f((1 / .51 - 1) * 100, 1)} %. C'est pour cela que les reprises après un krach paraissent si longues.")
    # diversification
    s = (0.5 ** 2 * 20 ** 2 + 0.5 ** 2 * 20 ** 2) ** .5
    A["diversification"] = _ex("Deux actions ont chacune une volatilité de 20 % et sont sans lien (corrélation 0). Moitié-moitié : quelle volatilité pour le portefeuille, en % ?",
                               s, .1, "%", f"σ = √(0,5² × 20² + 0,5² × 20²) = √200 = {_f(s, 1)} %. La diversification a retiré près de 6 points de risque sans changer le rendement moyen.")
    # construire son portefeuille : rééquilibrage
    act, obl = 12000 * 1.25, 8000 * .98
    vend = act - (act + obl) * .6
    A["construire-son-portefeuille"] = _ex("20 000 € répartis 60 % actions / 40 % obligations. Un an après : actions +25 %, obligations −2 %. Combien d'euros d'actions "
                                           "vendre pour revenir à 60 / 40 ?", vend, 1, "€",
                                           f"Actions : 12 000 × 1,25 = {_f(act)} €. Obligations : 8 000 × 0,98 = {_f(obl)} €. Total {_f(act + obl)} €, cible actions 60 % = "
                                           f"{_f((act + obl) * .6)} €. À vendre : {_f(vend)} €.")
    # fiscalité
    pv = 6000 - 1500
    A["fiscalite-2026"] = _ex("En 2026, sur ton compte-titres : +6 000 € de plus-values et −1 500 € de moins-values. Combien de flat tax paies-tu, en € ?", pv * .314, 1, "€",
                              f"Les moins-values s'imputent sur les plus-values de la même année : 6 000 − 1 500 = {_f(pv)} €. Impôt : 31,4 % × {_f(pv)} = {_f(pv * .314)} €.")
    # psychologie : perte cachée
    A["psychologie-investisseur"] = _ex("Tu as acheté à 80 €, l'action vaut 52 €. Combien faut-il qu'elle monte (en %) juste pour revenir à ton prix d'achat ?",
                                        (80 / 52 - 1) * 100, .2, "%", f"80 ÷ 52 − 1 = {_f((80 / 52 - 1) * 100, 1)} %. Ton prix d'achat n'intéresse pas le marché : "
                                        "la bonne question est « l'achèterais-je aujourd'hui à 52 € ? ».")
    # crypto fiscalité
    A["fiscalite-crypto-2026"] = _ex("En 2026, tu vends des cryptos pour 1 200 € au total. Ton portefeuille valait 4 000 € au moment de la vente et tu avais investi 2 500 € "
                                     "au total. Quelle plus-value imposable, en € ? (formule : prix de cession − prix d'acquisition × cession ÷ valeur du portefeuille)",
                                     1200 - 2500 * 1200 / 4000, 1, "€", f"1 200 − 2 500 × 1 200 ÷ 4 000 = 1 200 − 750 = {_f(1200 - 750)} €, taxés à 31,4 % : {_f(450 * .314)} €.")
    # obligations
    prix = sum(4 / 1.05 ** k for k in range(1, 6)) + 100 / 1.05 ** 5
    A["obligations-en-detail"] = _ex("Une obligation paie 4 € par an pendant 5 ans puis rembourse 100 €. Si le marché exige 5 % par an, quel est son prix, en € ?", prix, .05, "€",
                                     f"On actualise chaque flux : 4/1,05 + 4/1,05² + … + 104/1,05⁵ = {_f(prix)} €. Le taux exigé (5 %) dépasse le coupon (4 %) : le prix passe sous 100.")
    # devises
    r = (1.12 * .93 - 1) * 100
    A["devises-risque-de-change"] = _ex("Un ETF américain fait +12 % en dollars ; sur la même période, le dollar perd 7 % face à l'euro. Ta performance en euros, en % ?", r, .05, "%",
                                        f"1,12 × 0,93 − 1 = {_f(r)} %. Additionner (12 − 7 = 5 %) donne un résultat approché.")
    # levier
    A["levier-options-cfd"] = _ex("Avec 1 000 € et un levier de 5, tu prends une position. L'actif monte de 3 %, puis baisse de 8 %. Combien reste-t-il de tes 1 000 €, en € ?",
                                  1000 + 5000 * (1.03 * .92 - 1), 1, "€",
                                  f"Position : 5 000 €. Après +3 % puis −8 % : 5 000 × 1,03 × 0,92 = {_f(5000 * 1.03 * .92)} €, soit {_f(5000 * (1.03 * .92 - 1))} €. "
                                  f"Il te reste {_f(1000 + 5000 * (1.03 * .92 - 1))} € : une baisse de 5,2 % de l'actif t'a coûté 26 % de ta mise.")
    # DIC
    A["lire-un-dic"] = _ex("Un fonds a 1,8 % de frais courants par an. Sur 10 000 € qui restent stables, combien paies-tu de frais au total en 10 ans, environ, en € ? "
                           "(frais prélevés chaque année sur le capital restant)", 10000 * (1 - (1 - .018) ** 10), 10, "€",
                           f"10 000 × (1 − 0,982¹⁰) = {_f(10000 * (1 - .982 ** 10), 0)} €. Près de 17 % du capital, sans qu'aucune ligne « frais » n'apparaisse sur ton relevé.")
    return A


APPLICATION = _tous()
