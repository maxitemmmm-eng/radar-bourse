"""Version 73 : exercices sur graphiques pour l'Académie.

Chaque graphique est un petit SVG dessiné ici (pas d'image externe), coloré par le thème de la page :
classes g-axe, g-prix, g-up, g-down, g-ma, g-zone, g-zone2, g-txt, g-pt.
Chaque exercice : {"type": "graphique", "svg", "q", "choix", "bonne", "expl"} inséré après la mini-leçon d'index donné.
"""
import math
import random

L, H = 320, 170   # taille logique de tous les graphiques


def _svg(contenu, titre, h=H):
    return (f"<svg class='g' viewBox='0 0 {L} {h}' role='img' aria-label='{titre}'>"
            f"<line class='g-axe' x1='24' y1='{h - 20}' x2='{L - 8}' y2='{h - 20}'/><line class='g-axe' x1='24' y1='10' x2='24' y2='{h - 20}'/>"
            f"{contenu}</svg>")


def _chemin(vals, x0=28, x1=L - 12, vmin=None, vmax=None, y0=14, y1=H - 26):
    vmin = min(vals) if vmin is None else vmin
    vmax = max(vals) if vmax is None else vmax
    n = len(vals)
    pts = [(x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * (v - vmin) / ((vmax - vmin) or 1)) for i, v in enumerate(vals)]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), pts


def _marche(n, depart, derive, agit, graine):
    r = random.Random(graine)
    v, out = depart, []
    for _ in range(n):
        v *= 1 + derive + r.gauss(0, agit)
        out.append(v)
    return out


def _bougie():
    # ouverture 100, clôture 108, plus haut 112, plus bas 97
    def y(v):
        return 150 - (v - 90) * 5.5
    x = 160
    c = (f"<line class='g-up' x1='{x}' y1='{y(112):.0f}' x2='{x}' y2='{y(97):.0f}' stroke-width='2'/>"
         f"<rect class='g-up-f' x='{x - 22}' y='{y(108):.0f}' width='44' height='{y(100) - y(108):.0f}' rx='3'/>"
         f"<text class='g-txt' x='{x + 34}' y='{y(112) + 4:.0f}'>plus haut 112</text>"
         f"<text class='g-txt' x='{x + 34}' y='{y(108) + 4:.0f}'>108</text>"
         f"<text class='g-txt' x='{x + 34}' y='{y(100) + 4:.0f}'>100</text>"
         f"<text class='g-txt' x='{x + 34}' y='{y(97) + 4:.0f}'>plus bas 97</text>")
    return _svg(c, "Une bougie : ouverture 100, clôture 108")


def _trois_tendances():
    panneaux = []
    series = {"A": _marche(30, 100, 0.012, 0.012, 3), "B": _marche(30, 100, -0.012, 0.012, 5),
              "C": [100 + 6 * math.sin(i / 2.2) for i in range(30)]}
    for k, (nom, vals) in enumerate(series.items()):
        x0 = 30 + k * 98
        d, _ = _chemin(vals, x0=x0, x1=x0 + 84, y0=24, y1=130)
        panneaux.append(f"<rect class='g-cadre' x='{x0 - 4}' y='14' width='92' height='126' rx='8'/><path class='g-prix' d='{d}'/>"
                        f"<text class='g-lettre' x='{x0 + 42}' y='160' text-anchor='middle'>{nom}</text>")
    return f"<svg class='g' viewBox='0 0 {L} {H}' role='img' aria-label='Trois graphiques A, B et C'>" + "".join(panneaux) + "</svg>"


def _support():
    r = random.Random(11)
    vals, v, sens = [], 56, 1
    for i in range(46):
        v += sens * (0.9 + r.random() * 0.8)
        if v <= 50:
            v, sens = 50.2, 1
        if v >= 61.5:
            sens = -1
        vals.append(v)
    d, _ = _chemin(vals, vmin=46, vmax=70)
    def y(v):
        return (H - 26) - (H - 40) * (v - 46) / 24
    lignes = "".join(f"<line class='g-niveau' x1='28' x2='{L - 12}' y1='{y(n):.1f}' y2='{y(n):.1f}'/><text class='g-lettre' x='{L - 6}' y='{y(n) + 4:.1f}' text-anchor='end'>{k}</text>"
                     for k, n in (("A", 50), ("B", 55.5), ("C", 67)))
    return _svg(lignes + f"<path class='g-prix' d='{d}'/>", "Un prix qui oscille, et trois lignes A, B et C")


def _moyenne():
    vals = _marche(120, 100, 0.0022, 0.012, 21)
    ma = [sum(vals[max(0, i - 39):i + 1]) / len(vals[max(0, i - 39):i + 1]) for i in range(len(vals))]
    lo, hi = min(vals + ma), max(vals + ma)
    d, _ = _chemin(vals, vmin=lo, vmax=hi)
    d2, _ = _chemin(ma, vmin=lo, vmax=hi)
    leg = "<text class='g-txt' x='34' y='22'>prix</text><text class='g-txt g-ma-t' x='70' y='22'>moyenne mobile</text>"
    return _svg(f"<path class='g-ma' d='{d2}'/><path class='g-prix' d='{d}'/>" + leg, "Un prix et sa moyenne mobile")


def _rsi():
    r = random.Random(4)
    vals, v = [], 50
    for i in range(60):
        v += r.gauss(0, 4) + (0.9 if i > 40 else 0)
        v = max(18, min(82, v))
        vals.append(v)
    vals[-1] = 78
    def y(v):
        return (H - 26) - (H - 40) * v / 100
    bandes = (f"<rect class='g-zone2' x='28' y='{y(100):.0f}' width='{L - 40}' height='{y(70) - y(100):.0f}'/>"
              f"<rect class='g-zone2' x='28' y='{y(30):.0f}' width='{L - 40}' height='{y(0) - y(30):.0f}'/>"
              + "".join(f"<text class='g-txt' x='20' y='{y(n) + 4:.0f}' text-anchor='end'>{n}</text>" for n in (30, 70)))
    d, pts = _chemin(vals, vmin=0, vmax=100)
    x, yy = pts[-1]
    return _svg(bandes + f"<path class='g-prix' d='{d}'/><circle class='g-pt' cx='{x:.0f}' cy='{yy:.0f}' r='5'/>", "Le RSI d'une action, qui finit à 78")


def _deux_agitations():
    a = _marche(60, 100, 0.001, 0.006, 8)
    b = _marche(60, 100, 0.001, 0.035, 9)
    lo, hi = min(a + b), max(a + b)
    da, pa = _chemin(a, vmin=lo, vmax=hi)
    db, pb = _chemin(b, vmin=lo, vmax=hi)
    return _svg(f"<path class='g-prix' d='{da}'/><path class='g-down' d='{db}'/>"
                f"<text class='g-lettre' x='{pa[-1][0] - 4:.0f}' y='{pa[-1][1] - 8:.0f}' text-anchor='end'>A</text>"
                f"<text class='g-lettre g-down-t' x='{pb[-1][0] - 4:.0f}' y='{pb[-1][1] - 8:.0f}' text-anchor='end'>B</text>",
                "Deux actions A et B")


def _drawdown():
    vals = [120, 140, 165, 185, 200, 190, 172, 160, 150, 158, 166, 171]
    d, pts = _chemin(vals, vmin=100, vmax=210)
    (xh, yh), (xb, yb) = pts[4], pts[8]
    return _svg(f"<path class='g-prix' d='{d}'/><line class='g-niveau' x1='{xh:.0f}' x2='{L - 12}' y1='{yh:.0f}' y2='{yh:.0f}'/>"
                f"<circle class='g-pt' cx='{xh:.0f}' cy='{yh:.0f}' r='5'/><circle class='g-pt-bas' cx='{xb:.0f}' cy='{yb:.0f}' r='5'/>"
                f"<text class='g-txt' x='{xh:.0f}' y='{yh - 10:.0f}' text-anchor='middle'>plus haut : 200 €</text>"
                f"<text class='g-txt' x='{xb:.0f}' y='{yb + 20:.0f}' text-anchor='middle'>plus bas : 150 €</text>",
                "Un cours qui monte à 200 € puis tombe à 150 €")


def _interets():
    simple = [1000 + 50 * t for t in range(41)]
    compose = [1000 * 1.05 ** t for t in range(41)]
    lo, hi = 1000, max(compose)
    d1, p1 = _chemin(simple, vmin=lo, vmax=hi)
    d2, p2 = _chemin(compose, vmin=lo, vmax=hi)
    return _svg(f"<path class='g-ma' d='{d1}'/><path class='g-up' d='{d2}'/>"
                f"<text class='g-lettre' x='{p1[-1][0] - 4:.0f}' y='{p1[-1][1] - 8:.0f}' text-anchor='end'>A</text>"
                f"<text class='g-lettre g-up-t' x='{p2[-1][0] - 4:.0f}' y='{p2[-1][1] + 18:.0f}' text-anchor='end'>B</text>"
                "<text class='g-txt' x='30' y='164'>0 an</text><text class='g-txt' x='300' y='164' text-anchor='end'>40 ans</text>",
                "Deux courbes de 1 000 € placés pendant 40 ans")


def _fourchette():
    hist = _marche(40, 100, 0.001, 0.012, 2)
    x0, xm, x1 = 28, 190, L - 12
    lo, hi = 70, 135
    d, pts = _chemin(hist, x0=x0, x1=xm, vmin=lo, vmax=hi)
    def y(v):
        return (H - 26) - (H - 40) * (v - lo) / (hi - lo)
    v0 = hist[-1]
    clair = f"M{xm},{y(v0):.0f} L{x1},{y(v0 * 1.16):.0f} L{x1},{y(v0 * 0.86):.0f} Z"
    fonce = f"M{xm},{y(v0):.0f} L{x1},{y(v0 * 1.06):.0f} L{x1},{y(v0 * 0.95):.0f} Z"
    return _svg(f"<path class='g-zone' d='{clair}'/><path class='g-zone-f' d='{fonce}'/><path class='g-prix' d='{d}'/>"
                f"<text class='g-txt' x='{x1 - 2}' y='{y(v0 * 1.16) - 6:.0f}' text-anchor='end'>zone claire</text>"
                f"<text class='g-txt' x='{x1 - 2}' y='{y(v0 * 1.06) + 14:.0f}' text-anchor='end'>zone foncée</text>",
                "Une fourchette de prix pour le mois prochain")


def _krach_rapide():
    vals = [100, 101, 102, 103, 102, 96, 86, 75, 68, 66, 70, 76, 81, 86, 91, 95, 99, 102, 104]
    d, pts = _chemin(vals, vmin=60, vmax=108)
    return _svg(f"<path class='g-prix' d='{d}'/>"
                "<text class='g-txt' x='30' y='164'>février</text><text class='g-txt' x='300' y='164' text-anchor='end'>août</text>",
                "Une chute de 34 % en cinq semaines puis une remontée")


def _dca():
    prix = [10, 9, 8, 6, 9, 11]
    mois = ["janv.", "févr.", "mars", "avril", "mai", "juin"]
    bw = 34
    barres = ""
    for i, (p, m) in enumerate(zip(prix, mois)):
        x = 40 + i * 46
        h = p * 10.5
        barres += (f"<rect class='g-barre' x='{x}' y='{150 - h:.0f}' width='{bw}' height='{h:.0f}' rx='4'/>"
                   f"<text class='g-txt' x='{x + bw / 2}' y='{150 - h - 6:.0f}' text-anchor='middle'>{p} €</text>"
                   f"<text class='g-txt' x='{x + bw / 2}' y='164' text-anchor='middle'>{m}</text>")
    return _svg(barres, "Le prix d'une part d'ETF chaque mois")


def _deux_portefeuilles():
    a = [100, 104, 108, 112, 95, 70, 52, 45, 48, 44, 42, 40]
    b = [100, 102, 104, 106, 101, 95, 91, 90, 93, 96, 98, 101]
    d1, p1 = _chemin(a, vmin=35, vmax=115)
    d2, p2 = _chemin(b, vmin=35, vmax=115)
    return _svg(f"<path class='g-down' d='{d1}'/><path class='g-prix' d='{d2}'/>"
                f"<text class='g-lettre g-down-t' x='{p1[-1][0] - 4:.0f}' y='{p1[-1][1] - 8:.0f}' text-anchor='end'>A</text>"
                f"<text class='g-lettre' x='{p2[-1][0] - 4:.0f}' y='{p2[-1][1] - 8:.0f}' text-anchor='end'>B</text>",
                "Deux portefeuilles A et B pendant une crise")


def _taux_prix():
    taux = [2.0, 2.1, 2.0, 2.3, 2.6, 3.0, 3.4, 3.7, 3.9, 4.0, 4.1, 4.0]
    prix = [100 - (t - 2.0) * 8.5 for t in taux]
    d1, p1 = _chemin(taux, y0=18, y1=70)
    d2, p2 = _chemin(prix, y0=84, y1=H - 26)
    return _svg(f"<path class='g-ma' d='{d1}'/><path class='g-prix' d='{d2}'/>"
                f"<text class='g-txt g-ma-t' x='30' y='14'>taux d'intérêt</text><text class='g-txt' x='30' y='{p2[0][1] - 8:.0f}'>prix de l'obligation</text>",
                "Les taux d'intérêt montent, le prix d'une obligation baisse")


def _levier():
    # position fixe 5 fois la mise : valeur = mise + 5 × variation du marché ; une fois à zéro, la position est fermée
    marche = [100, 103, 101, 97, 94, 90, 86, 82, 79, 83, 88, 92, 95]
    x5, perdu = [], False
    for m in marche:
        v = 100 + 5 * (m - 100)
        perdu = perdu or v <= 0
        x5.append(0 if perdu else v)
    d1, p1 = _chemin(marche, vmin=0, vmax=120)
    d2, p2 = _chemin(x5, vmin=0, vmax=120)
    return _svg(f"<path class='g-prix' d='{d1}'/><path class='g-down' d='{d2}'/>"
                f"<text class='g-lettre' x='{p1[-1][0] - 4:.0f}' y='{p1[-1][1] - 8:.0f}' text-anchor='end'>A</text>"
                f"<text class='g-lettre g-down-t' x='{p2[-1][0] - 4:.0f}' y='{p2[-1][1] - 8:.0f}' text-anchor='end'>B</text>",
                "Le même marché, sans levier (A) et avec un levier de 5 (B)")


def _G(svg, q, choix, bonne, expl):
    return {"type": "graphique", "svg": svg, "q": q, "choix": choix, "bonne": bonne, "expl": expl}


def exercices():
    """{id_chapitre: [(index_mini_leçon, exercice)]}"""
    return {
        "bougies-tendances": [
            (0, _G(_bougie(), "Que t'apprend cette bougie journalière ?",
                   ["Le prix a fini la journée plus haut qu'à l'ouverture", "Le prix a fini plus bas qu'à l'ouverture", "Le prix n'est jamais descendu sous 100"], 0,
                   "Ouverture 100, clôture 108 : c'est une bougie de hausse. La mèche du bas montre que le prix est quand même descendu à 97 dans la journée.")),
            (1, _G(_trois_tendances(), "Lequel de ces trois graphiques est en tendance baissière ?", ["A", "B", "C"], 1,
                   "B enchaîne des plus hauts et des plus bas de plus en plus bas. A monte, C oscille sans direction (un range).")),
            (2, _G(_support(), "Quelle ligne correspond à un support ?", ["A", "B", "C"], 0,
                   "Le prix rebondit plusieurs fois sur la ligne A : les acheteurs y reviennent. B coupe le prix sans rien arrêter, C n'est jamais atteinte.")),
        ],
        "moyennes-rsi-macd": [
            (0, _G(_moyenne(), "Le prix finit au-dessus de sa moyenne mobile. Comment lire la tendance de fond ?",
                   ["Plutôt haussière", "Plutôt baissière", "On ne peut rien en dire"], 0,
                   "Un prix au-dessus de sa moyenne mobile indique plutôt une tendance de fond haussière. Mais la moyenne réagit avec retard.")),
            (1, _G(_rsi(), "Le RSI finit à 78 (le point). Comment le lit-on en général ?", ["Surachat", "Survente", "Neutre"], 0,
                   "Au-dessus de 70, on parle de surachat. Attention : en forte hausse, une action peut y rester longtemps.")),
        ],
        "rendement-risque": [
            (1, _G(_deux_agitations(), "Laquelle de ces deux actions a la volatilité la plus forte ?", ["A", "B"], 1,
                   "B fait des écarts bien plus grands que A, dans les deux sens : sa volatilité est plus forte.")),
            (3, _G(_drawdown(), "Quel est le drawdown (la baisse depuis le plus haut) sur ce graphique ?", ["25 %", "33 %", "50 %"], 0,
                   "(200 − 150) ÷ 200 = 25 %. On divise toujours par le plus haut, pas par le plus bas.")),
        ],
        "interets-composes": [
            (1, _G(_interets(), "1 000 € placés 40 ans. Quelle courbe montre les intérêts composés à 5 % ?", ["A", "B"], 1,
                   "B se courbe vers le haut : les intérêts rapportent eux-mêmes des intérêts. A gagne 50 € par an, toujours pareil (intérêts simples).")),
        ],
        "volatilite-et-ia": [
            (1, _G(_fourchette(), "Selon Radar Bourse, où le prix finit-il environ 8 fois sur 10 dans un mois ?",
                   ["Dans la zone claire", "Exactement au milieu", "Au-dessus de la zone claire"], 0,
                   "La zone claire contient le prix final environ 8 fois sur 10, la zone foncée environ 1 fois sur 2. C'est une mesure du risque, pas un objectif.")),
        ],
        "krachs-et-cycles": [
            (2, _G(_krach_rapide(), "Ce graphique (−34 % puis retour au record en 6 mois) ressemble le plus à quel krach ?",
                   ["Le Covid en 2020", "La bulle internet en 2000", "La crise de 2008"], 0,
                   "En 2020, le S&P 500 a perdu environ 34 % en cinq semaines puis retrouvé son record en août. Les krachs de 2000 et 2008 ont duré des années.")),
        ],
        "investir-regulierement": [
            (1, _G(_dca(), "Tu investis 100 € chaque mois. Quel mois ton versement achète-t-il le plus de parts ?", ["Janvier", "Avril", "Juin"], 1,
                   "En avril, la part coûte 6 € : 100 € achètent environ 16,7 parts, contre 10 en janvier et 9,1 en juin. C'est le principe du DCA.")),
        ],
        "obligations-en-detail": [
            (1, _G(_taux_prix(), "D'après ce graphique, que se passe-t-il pour le prix de l'obligation quand les taux montent ?",
                   ["Il baisse", "Il monte", "Il ne bouge pas"], 0,
                   "Les deux courbes vont en sens inverse : quand les taux d'intérêt montent, le prix des obligations déjà émises baisse.")),
        ],
        "levier-options-cfd": [
            (0, _G(_levier(), "Le marché (A) baisse d'environ 21 % puis remonte en partie. Pourquoi la courbe B (levier de 5) ne remonte-t-elle pas ?",
                   ["Elle est tombée à zéro : la mise est perdue", "Elle remonte plus tard", "Le levier protège des baisses"], 0,
                   "Avec un levier de 5, une baisse de 20 % suffit à tout perdre. Une fois à zéro, la remontée du marché ne sert plus à rien.")),
        ],
        "diversification": [
            (0, _G(_deux_portefeuilles(), "Pendant cette crise, lequel des deux portefeuilles est sans doute diversifié ?", ["A", "B"], 1,
                   "B baisse d'environ 10 % puis revient. A perd plus de la moitié : il ressemble à une seule action ou un seul secteur.")),
        ],
    }
