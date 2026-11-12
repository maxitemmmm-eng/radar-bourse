"""Version 83 : des schémas et graphiques DANS les mini-leçons de l'Académie (pas seulement dans les exercices).

Chaque figure est un SVG dessiné ici, coloré par le thème (mêmes classes g-* que les exercices sur graphiques), avec une
légende « Comment le lire ». Les chiffres sont des illustrations calculées (formules exactes), jamais des données inventées
présentées comme réelles. FIGURES[id_chapitre] = [(index_mini_leçon, html)].
"""
import math
import random

W, H = 360, 190


def _e(s):
    import html
    return html.escape(str(s), quote=True)


def _fig(svg, titre, lire, h=H):
    return (f"<figure class='l-fig'><svg class='g' viewBox='0 0 {W} {h}' role='img' aria-label='{_e(titre)}'>{svg}</svg>"
            f"<figcaption><b>{_e(titre)}</b> {lire}</figcaption></figure>")


def _axes(h=H, x0=34, y0=12):
    return f"<line class='g-axe' x1='{x0}' y1='{h - 22}' x2='{W - 8}' y2='{h - 22}'/><line class='g-axe' x1='{x0}' y1='{y0}' x2='{x0}' y2='{h - 22}'/>"


def _path(vals, x0=38, x1=W - 14, y0=16, y1=H - 28, vmin=None, vmax=None):
    lo = min(vals) if vmin is None else vmin
    hi = max(vals) if vmax is None else vmax
    n = len(vals)
    pts = [(x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * (v - lo) / ((hi - lo) or 1)) for i, v in enumerate(vals)]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), pts


def _y(v, lo, hi, y0=16, y1=H - 28):
    return y1 - (y1 - y0) * (v - lo) / ((hi - lo) or 1)


def _t(x, y, txt, cls="g-txt", ancre="start", taille=None):
    taille = taille or (12 if cls == "g-lettre" else 10)
    return f"<text class='{cls}' x='{x:.0f}' y='{y:.0f}' text-anchor='{ancre}' style='font-size:{taille}px'>{_e(txt)}</text>"


def _marche(n, v0, derive, agit, graine):
    r = random.Random(graine)
    v, out = v0, []
    for _ in range(n):
        out.append(v)
        v *= 1 + derive + r.gauss(0, agit)
    return out


def _sma(a, k):
    return [sum(a[i - k + 1:i + 1]) / k if i >= k - 1 else None for i in range(len(a))]


# ------------------------------------------------------------------------------------------------------------------
def offre_demande():
    prix = [19.8, 19.9, 20.0, 20.1, 20.2]
    ach = [900, 700, 520, 300, 120]
    ven = [100, 260, 520, 720, 880]
    g = ""
    for k, p in enumerate(prix):
        y = 30 + k * 30
        g += _t(176, y + 4, f"{p:.2f} €".replace(".", ","), "g-txt", "middle")
        g += f"<rect class='g-up-f' x='{150 - ach[k] / 7:.0f}' y='{y - 9}' width='{ach[k] / 7:.0f}' height='18' rx='3' opacity='.85'/>"
        g += f"<rect fill='var(--a-ko)' x='202' y='{y - 9}' width='{ven[k] / 7:.0f}' height='18' rx='3' opacity='.85'/>"
    g += _t(80, 186, "acheteurs prêts à payer ce prix", "g-up-t", "middle") + _t(270, 186, "vendeurs prêts à vendre", "g-down-t", "middle")
    g += "<rect x='136' y='81' width='88' height='18' rx='4' fill='none' stroke='var(--a-prim)' stroke-width='2'/>"
    return _fig(g, "Où se fixe le prix", "À 20,00 €, il y a autant d'actions demandées que proposées : c'est là que les échanges se font. "
                "Si de nouveaux acheteurs arrivent, les barres vertes grandissent et le point d'équilibre monte.", 196)


def risque_rendement():
    pts = [("Livret", .02, .005), ("Obligations d'État", .1, .03), ("ETF actions monde", .45, .07), ("Une seule action", .7, .08), ("Crypto", .95, .12)]
    g = _axes()
    for nom, r, ren in pts:
        x, y = 40 + r * 290, H - 26 - ren / .13 * 140
        bas = nom.startswith("ETF")
        g += f"<circle class='g-pt' cx='{x:.0f}' cy='{y:.0f}' r='6'/>" + _t(x + (-8 if r > .8 else 9), y + (16 if bas else -9), nom, "g-txt", "end" if r > .8 or bas else "start")
    g += _t(W - 10, H - 8, "risque (agitation, pertes possibles) →", "g-txt", "end") + f"<text class='g-txt' transform='translate(14 {H - 30}) rotate(-90)'>rendement espéré →</text>"
    return _fig(g, "Plus de rendement espéré = plus de risque", "Positions indicatives, pas des promesses : un rendement espéré plus élevé "
                "s'accompagne toujours de baisses possibles plus fortes. Il n'existe pas de point en haut à gauche.")


def base100():
    a = _marche(60, 100, .003, .015, 2)
    b = _marche(60, 100, -.001, .02, 4)
    c = _marche(60, 100, .001, .01, 6)
    a, b, c = [x * 100 / a[0] for x in a], [x * 100 / b[0] for x in b], [x * 100 / c[0] for x in c]
    idx = [(x + y + z) / 3 for x, y, z in zip(a, b, c)]
    lo, hi = min(a + b + c) - 2, max(a + b + c) + 2
    g = _axes()
    for s, cls in ((a, "g-up"), (b, "g-down"), (c, "g-niveau")):
        g += f"<path class='{cls}' d='{_path(s, vmin=lo, vmax=hi)[0]}' fill='none' opacity='.6'/>"
    d, p = _path(idx, vmin=lo, vmax=hi)
    g += f"<path class='g-prix' d='{d}' fill='none' stroke-width='3.2'/>" + _t(p[-1][0], p[-1][1] - 10, "l'indice (la moyenne)", "g-lettre", "end")
    y100 = _y(100, lo, hi)
    g += f"<line class='g-niveau' x1='34' x2='{W - 8}' y1='{y100:.0f}' y2='{y100:.0f}'/>" + _t(38, y100 - 4, "100 = point de départ")
    return _fig(g, "Un indice, c'est la moyenne d'un panier", "Trois actions (lignes fines) partent toutes de 100. L'indice (trait épais) suit leur moyenne : "
                "il monte moins que la meilleure et baisse moins que la pire.")


def pertes_hausse():
    cas = [(10, 11.1), (25, 33.3), (50, 100), (75, 300)]
    g = ""
    for k, (p, h) in enumerate(cas):
        x = 40 + k * 80
        hp, hh = p * 1.3, min(150, h * .5)
        g += f"<rect fill='var(--a-ko)' x='{x}' y='{H - 26 - hp:.0f}' width='26' height='{hp:.0f}' rx='3'/>"
        g += f"<rect class='g-up-f' x='{x + 30}' y='{H - 26 - hh:.0f}' width='26' height='{hh:.0f}' rx='3'/>"
        g += (f"<text class='g-down-t' x='{x + 13}' y='{H - 30 - hp:.0f}' text-anchor='middle' style='font-size:9px'>−{p} %</text>"
              f"<text class='g-up-t' x='{x + 43}' y='{H - 30 - hh - (10 if abs(hh - hp) < 12 else 0):.0f}' text-anchor='middle' style='font-size:9px'>{('+' + format(h, 'g') + ' %').replace('.', ',')}</text>")
    g += f"<line class='g-axe' x1='30' x2='{W - 8}' y1='{H - 26}' y2='{H - 26}'/>" + _t(W / 2, H - 8, "rouge : la perte · vert : la hausse nécessaire pour revenir au départ", "g-txt", "middle")
    return _fig(g, "Une perte demande une hausse plus grande pour être effacée", "Après −50 %, il faut +100 % pour revenir au point de départ ; après −75 %, +300 %. "
                "Formule : hausse nécessaire = 1 ÷ (1 − perte) − 1. C'est pour cela qu'éviter les grosses pertes compte autant.")


def drawdown():
    v = [100 + i * 1.1 + 2 * math.sin(i) for i in range(25)] + [127 - (i * 1.6) + 2 * math.sin(i * 1.3) for i in range(25)] + [87 + i * 1.2 + 2 * math.sin(i) for i in range(20)]
    pic, dd = v[0], []
    for x in v:
        pic = max(pic, x)
        dd.append(x / pic - 1)
    d, p = _path(v, y1=96)
    g = _axes() + f"<path class='g-prix' d='{d}' fill='none'/>"
    lo = min(dd)
    pts = [(38 + (W - 52) * i / 69, 112 + (-x / -lo) * 50 if lo else 112) for i, x in enumerate(dd)]
    zone = "M38,112 L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" L{W - 14},112 Z"
    g += f"<path style='fill:var(--a-ko);opacity:.3' d='{zone}'/><line class='g-niveau' x1='38' x2='{W - 14}' y1='112' y2='112'/>"
    g += _t(40, 108, "0 % : au plus haut") + _t(40, 176, f"pire baisse : {lo * 100:.0f} %".replace(".", ","), "g-down-t")
    return _fig(g, "Le drawdown : la distance au plus haut", "En haut, le prix. En bas, en rouge, l'écart avec le plus haut déjà atteint. "
                "Le point le plus bas de la zone rouge, c'est la pire baisse vécue par quelqu'un qui aurait acheté au sommet.")


def deux_agitations():
    calme = [100 * (1.4 ** (i / 59)) * (1 + .012 * math.sin(i)) for i in range(60)]
    agite = [100 * (1.4 ** (i / 59)) * (1 + .12 * math.sin(i / 2.6) + .04 * math.sin(i * 1.7)) for i in range(60)]
    lo, hi = min(calme + agite), max(calme + agite)
    g = _axes() + f"<path class='g-up' d='{_path(calme, vmin=lo, vmax=hi)[0]}' fill='none'/><path class='g-down' d='{_path(agite, vmin=lo, vmax=hi)[0]}' fill='none'/>"
    g += _t(44, 30, "même point d'arrivée,", "g-txt") + _t(44, 44, "chemins très différents", "g-txt")
    return _fig(g, "La volatilité, c'est le chemin, pas l'arrivée", "Les deux placements finissent au même niveau. Le rouge a beaucoup plus secoué : "
                "sa volatilité est plus forte, et quelqu'un qui aurait dû vendre au mauvais moment aurait perdu.")


def composes():
    ans = list(range(31))
    simple = [10000 * (1 + .07 * a) for a in ans]
    comp = [10000 * 1.07 ** a for a in ans]
    hi = comp[-1]
    g = _axes() + f"<path class='g-niveau' d='{_path(simple, vmin=0, vmax=hi)[0]}' fill='none' style='stroke-dasharray:none;stroke-width:2'/>"
    d, p = _path(comp, vmin=0, vmax=hi)
    g += f"<path class='g-prix' d='{d}' fill='none' stroke-width='3'/>"
    g += _t(p[-1][0], p[-1][1] + 14, "composés : 76 123 €", "g-lettre", "end") + _t(W - 14, _path(simple, vmin=0, vmax=hi)[1][-1][1] - 6, "simples : 31 000 €", "g-txt", "end")
    g += _t(40, H - 8, "0 an") + _t(W - 14, H - 8, "30 ans", "g-txt", "end")
    return _fig(g, "10 000 € à 7 % par an pendant 30 ans", "Intérêts simples : on gagne toujours 700 € par an. Intérêts composés : les gains rapportent "
                "à leur tour. L'écart est faible au début et énorme à la fin : c'est le temps qui fait le travail.")


def fiscalite_barres():
    cas = [("Compte-titres", 3140, "31,4 %"), ("PEA de plus de 5 ans", 1860, "18,6 %"), ("Assurance-vie de plus de 8 ans, sous l'abattement", 1720, "17,2 % (sociaux seuls)")]
    g = ""
    for k, (nom, v, tx) in enumerate(cas):
        y = 24 + k * 54
        g += _t(14, y, nom, "g-txt") + f"<rect class='g-barre' x='14' y='{y + 6}' width='{v / 3140 * 250:.0f}' height='22' rx='4'/>" + _t(v / 3140 * 250 + 22, y + 22, f"{v // 1000} {v % 1000:03d} € ({tx})", "g-lettre", taille=11)
    return _fig(g, "Impôts sur un gain de 10 000 € en 2026", "Même gain, enveloppes différentes. Pour l'assurance-vie, cas d'un retrait dont le gain reste sous "
                "l'abattement annuel de 4 600 € (personne seule) : seul le taux des prélèvements sociaux s'applique. Ordres de grandeur, pas un conseil fiscal.", 176)


def carnet():
    vente = [(20.12, 300), (20.08, 520), (20.05, 180)]
    achat = [(20.02, 400), (19.98, 650), (19.95, 230)]
    g = _t(W / 2, 16, "carnet d'ordres", "g-lettre", "middle")
    for k, (p, q) in enumerate(vente):
        y = 28 + k * 22
        g += f"<rect fill='var(--a-ko)' opacity='.75' x='190' y='{y}' width='{q / 5:.0f}' height='17' rx='3'/>" + _t(178, y + 13, f"{p:.2f}".replace(".", ","), "g-down-t", "end") + _t(196 + q / 5, y + 13, f"{q} titres")
    g += f"<line class='g-niveau' x1='40' x2='{W - 20}' y1='{28 + 3 * 22 + 4}' y2='{28 + 3 * 22 + 4}'/>" + _t(40, 28 + 3 * 22 + 18, "écart (spread) : 0,03 €")
    for k, (p, q) in enumerate(achat):
        y = 104 + k * 22
        g += f"<rect class='g-up-f' opacity='.85' x='190' y='{y}' width='{q / 5:.0f}' height='17' rx='3'/>" + _t(178, y + 13, f"{p:.2f}".replace(".", ","), "g-up-t", "end") + _t(196 + q / 5, y + 13, f"{q} titres")
    g += _t(110, 52, "vendeurs", "g-down-t", "end") + _t(110, 128, "acheteurs", "g-up-t", "end")
    return _fig(g, "Le carnet d'ordres", "En rouge, les vendeurs et leur prix minimum ; en vert, les acheteurs et leur prix maximum. Un ordre « au marché » d'achat "
                "prend d'abord les 180 titres à 20,05 €, puis monte au prix suivant s'il en faut plus.", 180)


def dca():
    px = [50, 44, 38, 41, 47, 53, 49, 56]
    parts = sum(100 / p for p in px)
    pm = 100 * len(px) / parts
    d, p = _path(px, vmin=30, vmax=60)
    g = _axes() + f"<path class='g-prix' d='{d}' fill='none'/>" + "".join(f"<circle class='g-pt' cx='{x:.0f}' cy='{y:.0f}' r='5'/>" for x, y in p)
    yp = _y(pm, 30, 60)
    g += f"<line class='g-ma' x1='38' x2='{W - 14}' y1='{yp:.0f}' y2='{yp:.0f}'/>" + _t(W - 14, H - 30, f"ton prix moyen : {pm:.2f} €".replace(".", ","), "g-ma-t", "end", 11)
    f2 = lambda x: f"{x:.2f}".replace(".", ",")
    return _fig(g, "Investir 100 € chaque mois", f"Chaque point est un achat de 100 €. Quand le prix baisse, 100 € achètent plus de parts. Prix moyen payé : {f2(pm)} € "
                f"(la moyenne simple des prix est {f2(sum(px) / len(px))} €). Le DCA lisse le prix d'entrée, il ne garantit pas un gain.")


def resultat_cascade():
    etapes = [("Chiffre d'affaires", 100, 0), ("− coûts de production et salaires", -72, 100), ("= résultat d'exploitation", 28, 0),
              ("− intérêts de la dette", -4, 28), ("− impôts", -6, 24), ("= résultat net", 18, 0)]
    g = ""
    for k, (nom, v, base) in enumerate(etapes):
        x = 18 + k * 56
        haut, bas = (base + v, base) if v < 0 else (v, 0)
        y1, y2 = 150 - max(haut, bas) * 1.3, 150 - min(haut, bas) * 1.3
        cls = "fill='var(--a-ko)' opacity='.75'" if v < 0 else "class='g-barre'"
        g += f"<rect {cls} x='{x}' y='{y1:.0f}' width='40' height='{y2 - y1:.0f}' rx='3'/>" + _t(x + 20, y1 - 4, f"{v:+d}" if k not in (0,) else "100", "g-txt", "middle")
        g += f"<text class='g-txt' transform='translate({x + 14} 160) rotate(30)' style='font-size:8.5px'>{_e(nom)}</text>"
    return _fig(g, "Du chiffre d'affaires au bénéfice", "Exemple pour 100 € de ventes : il reste 28 € après les coûts, puis 18 € de bénéfice net "
                "après les intérêts et les impôts. La marge nette est donc de 18 %.", 220)


def per():
    g = ""
    for k, (nom, bpa, per_) in enumerate((("Entreprise A", 5, 12), ("Entreprise B", 5, 30))):
        x = 50 + k * 160
        h1, h2 = bpa * 4, bpa * per_ * .9
        g += f"<rect class='g-barre' x='{x}' y='{160 - h2:.0f}' width='60' height='{h2:.0f}' rx='4' opacity='.45'/><rect class='g-up-f' x='{x}' y='{160 - h1:.0f}' width='60' height='{h1:.0f}' rx='3'/>"
        g += _t(x + 30, 176, nom, "g-lettre", "middle") + _t(x + 30, 154 - h2, f"prix {bpa * per_} € · PER {per_}", "g-txt", "middle") + _t(x + 66, 160 - h1 / 2 + 4, f"bénéfice {bpa} €")
    return _fig(g, "Même bénéfice, prix très différents", "A et B gagnent 5 € par action. Le marché paie 12 années de bénéfices pour A, 30 pour B. "
                "Un PER élevé n'est pas « cher » par définition : le marché attend une forte croissance, et sera déçu si elle ne vient pas.")


def detachement():
    v = [50 + .08 * i + .3 * math.sin(i) for i in range(20)] + [48.3 + .08 * i + .3 * math.sin(i + 20) for i in range(20)]
    d, p = _path(v)
    g = _axes() + f"<path class='g-prix' d='{d}' fill='none'/>"
    xd = p[20][0]
    g += f"<line class='g-niveau' x1='{xd:.0f}' x2='{xd:.0f}' y1='14' y2='{H - 22}'/>" + _t(xd + 5, 26, "détachement du dividende : −2 €", "g-down-t")
    return _fig(g, "Le jour où le dividende est détaché", "Un dividende de 2 € quitte la caisse de l'entreprise : le cours baisse mécaniquement d'environ 2 € ce jour-là. "
                "L'actionnaire n'est pas plus riche avant impôts, il a juste reçu une partie en argent.")


def bougies():
    def y(v):
        return 176 - (v - 95) * 9.5
    g = ""
    for k, (x, (o, c, h, l)) in enumerate(((90, (100, 108, 112, 97)), (250, (108, 101, 110, 98)))):
        cls, f = ("g-up", "class='g-up-f'") if c > o else ("g-down", "style='fill:var(--a-ko)'")
        g += f"<line class='{cls}' x1='{x}' x2='{x}' y1='{y(h):.0f}' y2='{y(l):.0f}'/><rect {f} x='{x - 18}' y='{y(max(o, c)):.0f}' width='36' height='{abs(y(o) - y(c)):.0f}' rx='3'/>"
        g += _t(x + 26, y(h) + 4, f"plus haut {h}") + _t(x + 26, y(l) + 4, f"plus bas {l}") + _t(x + 26, y(c) + 4, f"clôture {c}", "g-lettre")
        g += _t(x - 26, y(o) + 4, f"ouverture {o}", "g-txt", "end") if k == 0 else _t(x + 26, y(o) + 4, f"ouverture {o}")
    return _fig(g, "Bougie verte, bougie rouge", "Le corps va de l'ouverture à la clôture : vert si la clôture est plus haute, rouge si elle est plus basse. "
                "Les mèches montent au plus haut et descendent au plus bas de la séance.", 196)


def tendance():
    v = [100, 108, 103, 114, 109, 121, 115, 128]
    d, p = _path(v)
    g = _axes() + f"<path class='g-prix' d='{d}' fill='none'/>"
    for k, (x, y) in enumerate(p):
        haut = k % 2 == 1
        g += f"<circle class='{'g-pt' if haut else 'g-pt-bas'}' cx='{x:.0f}' cy='{y:.0f}' r='4.5'/>"
        if k in (1, 3, 5):
            g += _t(x, y - 9, "sommet plus haut", "g-txt", "middle")
        if k in (2, 4, 6):
            g += _t(x, y + 16, "creux plus haut", "g-txt", "middle")
    return _fig(g, "Une tendance haussière, définie précisément", "Chaque sommet dépasse le précédent ET chaque creux reste au-dessus du précédent. "
                "Dès qu'un creux passe sous le précédent, la tendance est en question.")


def support_res():
    v = [60 + 9 * abs(math.sin(i / 3.2)) + (i % 3) * .4 for i in range(46)]
    d, p = _path(v, vmin=58, vmax=72)
    ys, yr = _y(60.2, 58, 72), _y(68.8, 58, 72)
    g = _axes() + f"<rect class='g-zone' x='38' y='{ys - 5:.0f}' width='{W - 52}' height='10'/><rect fill='var(--a-ko)' opacity='.15' x='38' y='{yr - 5:.0f}' width='{W - 52}' height='10'/>"
    g += f"<path class='g-prix' d='{d}' fill='none'/>" + _t(W - 14, ys + 18, "support : les acheteurs reviennent", "g-txt", "end") + _t(W - 14, yr - 9, "résistance : les vendeurs reviennent", "g-down-t", "end")
    return _fig(g, "Support et résistance", "Ce sont des zones, pas des lignes exactes. Plus un niveau a été touché souvent, plus il est surveillé ; "
                "quand il finit par céder, le mouvement est souvent rapide.")


def moyennes():
    v = _marche(120, 100, .0, .014, 11)
    v = [x * (1 + .25 * math.sin(i / 30)) for i, x in enumerate(v)]
    m20, m50 = _sma(v, 20), _sma(v, 50)
    lo, hi = min(v), max(v)
    g = _axes() + f"<path class='g-prix' d='{_path(v, vmin=lo, vmax=hi)[0]}' fill='none' opacity='.55'/>"
    for m, cls in ((m20, "g-up"), (m50, "g-ma")):
        k0 = next(i for i, x in enumerate(m) if x is not None)
        pts = _path(v, vmin=lo, vmax=hi)[1]
        dd = "M" + " L".join(f"{pts[i][0]:.1f},{(H - 28) - (H - 44) * (m[i] - lo) / (hi - lo):.1f}" for i in range(k0, len(m)))
        g += f"<path class='{cls}' d='{dd}' fill='none'/>"
    g += _t(42, 14, "vert : moyenne 20 jours (rapide)", "g-up-t") + _t(42, 27, "orange : moyenne 50 jours (lente)", "g-ma-t")
    return _fig(g, "Moyennes mobiles", "Chaque point d'une moyenne 20 jours est la moyenne des 20 derniers cours : la courbe est lissée et en retard. "
                "Quand la rapide passe au-dessus de la lente, la tendance récente devient haussière, avec retard, et beaucoup de faux signaux.")


def rsi():
    v = _marche(120, 100, 0, .02, 19)
    out, g_, p_ = [None] * len(v), 0, 0
    for i in range(1, len(v)):
        d = v[i] - v[i - 1]
        u, w = max(d, 0), max(-d, 0)
        if i <= 14:
            g_ += u / 14
            p_ += w / 14
            if i == 14:
                out[i] = 100 - 100 / (1 + g_ / p_) if p_ else 100
        else:
            g_ = (g_ * 13 + u) / 14
            p_ = (p_ * 13 + w) / 14
            out[i] = 100 - 100 / (1 + g_ / p_) if p_ else 100
    r = [x if x is not None else 50 for x in out][14:]
    g = _axes()
    y = lambda val: (H - 28) - (H - 44) * val / 100
    g += f"<rect fill='var(--a-ko)' opacity='.12' x='38' y='{y(100):.0f}' width='{W - 52}' height='{y(70) - y(100):.0f}'/><rect class='g-zone' x='38' y='{y(30):.0f}' width='{W - 52}' height='{y(0) - y(30):.0f}'/>"
    g += f"<path class='g-prix' d='{_path(r, vmin=0, vmax=100)[0]}' fill='none'/>" + _t(W - 14, y(70) - 4, "70 : a beaucoup monté, vite", "g-down-t", "end") + _t(W - 14, y(30) + 14, "30 : a beaucoup baissé, vite", "g-up-t", "end")
    return _fig(g, "Le RSI sur 14 jours", "Il compare la force des hausses et des baisses récentes, sur une échelle de 0 à 100. Au-dessus de 70 ou sous 30, "
                "le mouvement a été rapide ; ça ne dit pas quand il s'arrêtera.")


def eventail():
    n, sig = 22, .11
    past = _marche(40, 100, .001, .012, 23)
    p0 = past[-1]
    bande = lambda z, sgn: [p0 * math.exp(sgn * z * sig * math.sqrt(k / (n - 1))) for k in range(n)]
    h80, b80, h50, b50 = bande(1.2816, 1), bande(1.2816, -1), bande(.6745, 1), bande(.6745, -1)
    lo, hi = min(past + b80) - 2, max(past + h80) + 2
    x0, x1 = 38, W - 14
    tx = lambda i: x0 + (x1 - x0) * i / (39 + n - 1)
    ty = lambda v: (H - 28) - (H - 44) * (v - lo) / (hi - lo)
    poly = lambda h, b: "M" + " L".join(f"{tx(39 + k):.1f},{ty(v):.1f}" for k, v in enumerate(h)) + " L" + " L".join(f"{tx(39 + k):.1f},{ty(v):.1f}" for k, v in reversed(list(enumerate(b)))) + " Z"
    g = _axes()
    g += (f"<path style='fill:color-mix(in srgb,var(--a-prim) 16%,transparent);stroke:none' d='{poly(h80, b80)}'/>"
          f"<path style='fill:color-mix(in srgb,var(--a-prim) 38%,transparent);stroke:none' d='{poly(h50, b50)}'/>")
    g += "<path class='g-prix' fill='none' d='M" + " L".join(f"{tx(i):.1f},{ty(v):.1f}" for i, v in enumerate(past)) + "'/>"
    g += f"<line class='g-niveau' x1='{tx(39):.0f}' x2='{tx(39):.0f}' y1='14' y2='{H - 22}'/>" + _t(tx(39) - 4, 22, "aujourd'hui", "g-txt", "end")
    g += _t(x1, ty(h80[-1]) - 5, "8 fois sur 10 dans la zone claire", "g-txt", "end") + _t(x1, ty(b50[-1]) + 14, "1 fois sur 2 dans la foncée", "g-txt", "end")
    return _fig(g, "Lire une fourchette de prévision", "La zone s'élargit avec le temps : plus on regarde loin, plus l'incertitude grandit (comme la racine du temps). "
                "Une fourchette à 80 % doit être « ratée » environ 2 fois sur 10 : sinon, elle est trop large.")


def taux_prix():
    taux = [1, 2, 3, 4, 5, 6]
    prix = [100 * sum(.03 / (1 + t / 100) ** k for k in range(1, 11)) + 100 / (1 + t / 100) ** 10 for t in taux]
    d, p = _path(prix)
    g = _axes() + f"<path class='g-down' d='{d}' fill='none'/>" + "".join(f"<circle class='g-pt' cx='{x:.0f}' cy='{y:.0f}' r='4'/>" for x, y in p)
    for (x, y), t, pr in zip(p, taux, prix):
        g += _t(x, H - 8, f"{t} %", "g-txt", "middle") + _t(x + 6, y - 7, f"{pr:.0f}")
    return _fig(g, "Quand les taux montent, le prix des obligations baisse", "Obligation à 10 ans, coupon de 3 %, remboursée 100. Si le marché exige 5 % au lieu "
                "de 3 %, personne ne la paie 100 : son prix tombe vers 85. En bas : le taux du marché ; sur les points : le prix.")


def correlation():
    r = random.Random(3)
    g = ""
    for k, (nom, rho) in enumerate((("corrélation +1", 1), ("corrélation 0", 0), ("corrélation −1", -1))):
        x0 = 14 + k * 116
        g += f"<rect class='g-cadre' x='{x0}' y='14' width='104' height='140' rx='8'/>"
        for _ in range(26):
            a = r.gauss(0, 1)
            b = rho * a + math.sqrt(max(0, 1 - rho * rho)) * r.gauss(0, 1)
            a, b = max(-2.6, min(2.6, a)), max(-3.3, min(3.3, b))
            g += f"<circle class='g-pt' cx='{x0 + 52 + a * 16:.0f}' cy='{84 - b * 16:.0f}' r='3' opacity='.8'/>"
        g += _t(x0 + 52, 172, nom, "g-lettre", "middle")
    return _fig(g, "La corrélation entre deux placements", "Chaque point = un mois : à l'horizontale le rendement de A, à la verticale celui de B. "
                "À +1, ils bougent ensemble (aucune protection) ; à 0, sans lien ; à −1, l'un compense l'autre. La diversification marche mieux quand la corrélation est basse.", 180)


def reequilibrage():
    g = ""
    for k, (nom, a, o) in enumerate((("Départ", 60, 40), ("Un an plus tard", 70, 30), ("Après rééquilibrage", 60, 40))):
        x = 40 + k * 108
        ha, ho = a * 1.4, o * 1.4
        g += f"<rect class='g-barre' x='{x}' y='{160 - ha:.0f}' width='60' height='{ha:.0f}'/>"
        g += f"<rect fill='var(--a-or)' opacity='.7' x='{x}' y='{160 - ha - ho:.0f}' width='60' height='{ho:.0f}'/>"
        g += _t(x + 30, 176, nom, "g-txt", "middle") + f"<text x='{x + 30}' y='{164 - ha / 2:.0f}' text-anchor='middle' style='fill:#fff;font-weight:700;font-size:13px'>{a} %</text><text x='{x + 30}' y='{164 - ha - ho / 2:.0f}' text-anchor='middle' style='fill:#fff;font-weight:700;font-size:13px'>{o} %</text>"
    g += _t(14, 14, "bleu-vert : actions · orange : obligations", "g-txt")
    return _fig(g, "Rééquilibrer : revenir à sa répartition", "Les actions ont monté et pèsent 70 % au lieu de 60 %. Rééquilibrer, c'est vendre "
                "une partie de ce qui a monté pour racheter ce qui a pris du retard : on revient au risque choisi au départ.", 186)


def levier():
    v = [100 * (1 - .004 * i + .01 * math.sin(i / 1.6)) for i in range(40)]
    lv = [100 + 5 * (x - 100) for x in v]
    k = next((i for i, x in enumerate(lv) if x <= 0), len(lv))
    lv = [max(0, x) for x in lv[:k + 1]]
    g = _axes() + f"<path class='g-prix' d='{_path(v, vmin=0, vmax=110)[0]}' fill='none'/>"
    pts = _path(v, vmin=0, vmax=110)[1]
    g += "<path class='g-down' fill='none' d='M" + " L".join(f"{pts[i][0]:.1f},{(H - 28) - (H - 44) * x / 110:.1f}" for i, x in enumerate(lv)) + "'/>"
    xk = pts[min(k, len(pts) - 1)][0]
    g += f"<circle cx='{xk:.0f}' cy='{H - 28}' r='5' fill='var(--a-ko)'/>" + _t(xk - 4, H - 36, "levier 5 : tout est perdu", "g-down-t", "end") + _t(W - 14, pts[-1][1] - 8, "sans levier : −16 %", "g-txt", "end")
    return _fig(g, "Le levier multiplie aussi les baisses", "Le même marché baisse d'environ 16 %. Sans levier, tu perds 16 %. Avec un levier de 5, "
                "ta mise disparaît dès que la baisse atteint 20 %, et la position est fermée : tu ne profites même pas d'un rebond.")


def change():
    g = ""
    for k, (nom, v, cls) in enumerate((("action en $", 10, "g-up-f"), ("dollar face à l'euro", -8, "red"), ("résultat en €", 1.2, "g-up-f"))):
        x = 50 + k * 100
        h = abs(v) * 6
        y = 100 - h if v > 0 else 100
        f = "fill='var(--a-ko)' opacity='.8'" if cls == "red" else f"class='{cls}'"
        g += f"<rect {f} x='{x}' y='{y:.0f}' width='56' height='{h:.0f}' rx='3'/>" + _t(x + 28, (y - 6) if v > 0 else (y + h + 14), f"{v:+g} %".replace(".", ","), "g-lettre", "middle") + _t(x + 28, 178, nom, "g-txt", "middle")
    g += f"<line class='g-axe' x1='30' x2='{W - 10}' y1='100' y2='100'/>"
    return _fig(g, "Deux mouvements qui se multiplient", "+10 % en dollars et −8 % pour le dollar : 1,10 × 0,92 − 1 = +1,2 % en euros. "
                "Une action américaine qui monte peut faire perdre de l'argent à un investisseur européen si le dollar chute.", 186)


def sri():
    g = ""
    for k in range(7):
        x = 24 + k * 46
        g += f"<rect x='{x}' y='60' width='40' height='40' rx='6' fill='var(--a-prim)' opacity='{.15 + k * .12:.2f}'/>" + _t(x + 20, 86, str(k + 1), "g-lettre", "middle")
    g += _t(24, 124, "fonds monétaire", "g-txt") + _t(24 + 3 * 46 + 20, 124, "ETF actions monde", "g-txt", "middle") + _t(W - 14, 124, "très spéculatif", "g-txt", "end")
    g += _t(24, 48, "risque plus faible, rendement potentiel plus faible", "g-txt") + _t(W - 14, 148, "risque plus élevé", "g-down-t", "end")
    return _fig(g, "L'indicateur de risque du DIC (de 1 à 7)", "Le premier chiffre à regarder avant d'acheter un fonds : il combine la volatilité et le risque de crédit. "
                "Un produit en 6 ou 7 peut perdre une grande partie de sa valeur.", 160)


def blocs():
    g = ""
    for k in range(4):
        x = 14 + k * 86
        g += f"<rect class='g-cadre' x='{x}' y='50' width='72' height='86' rx='8' style='stroke:var(--a-prim);stroke-width:1.5'/>"
        g += _t(x + 36, 70, f"bloc n°{k + 1}", "g-lettre", "middle", 11) + _t(x + 36, 88, "transactions", "g-txt", "middle", 9) + _t(x + 36, 104, f"empreinte {['a3f9', '7c21', 'e04b', '91d6'][k]}", "g-txt", "middle", 9)
        if k:
            g += _t(x + 36, 122, f"← {['a3f9', '7c21', 'e04b'][k - 1]}", "g-ma-t", "middle", 9) + f"<line class='g-axe' x1='{x - 14}' x2='{x}' y1='93' y2='93' style='stroke:var(--a-prim)'/>"
    g += _t(W / 2, 28, "chaque bloc contient l'empreinte du précédent", "g-txt", "middle")
    return _fig(g, "Une chaîne de blocs", "Modifier une transaction ancienne changerait l'empreinte de son bloc, donc de tous les suivants : il faudrait refaire "
                "tout le travail de calcul plus vite que le reste du réseau. C'est ce qui rend l'historique très difficile à falsifier.", 160)


def emotions():
    v = [100 + 40 * math.sin((i - 8) / 9) + i * .6 for i in range(60)]
    d, p = _path(v)
    g = _axes() + f"<path class='g-prix' d='{d}' fill='none'/>"
    ih = v.index(max(v))
    ib = ih + v[ih:].index(min(v[ih:]))
    for i, txt, pos in ((ih, "euphorie : « ça ne peut que monter »", "haut"), (min(ih + 7, 59), "déni", "droite"), (ib, "panique : on vend", "bas"), (min(ib + 9, 59), "espoir", "droite")):
        x, y = p[i]
        g += f"<circle class='{'g-pt-bas' if pos == 'bas' else 'g-pt'}' cx='{x:.0f}' cy='{y:.0f}' r='4.5'/>"
        g += _t(x + (8 if pos == "droite" else 0), y + (16 if pos == "bas" else 4 if pos == "droite" else -9), txt, "g-txt", "start" if pos == "droite" else "middle")
    return _fig(g, "Le cycle des émotions", "On a le plus envie d'acheter près des sommets et de vendre près des creux : exactement l'inverse de ce qui rapporte. "
                "Des règles écrites à l'avance servent à ne pas suivre ce cycle.")


FIGURES = {
    "bourse-c-est-quoi": [(0, offre_demande)],
    "action-obligation-etf-crypto": [(4, risque_rendement)],
    "indices-cac40-sp500": [(0, base100)],
    "rendement-risque": [(1, deux_agitations), (2, pertes_hausse), (3, drawdown)],
    "interets-composes": [(0, composes)],
    "pea-cto-assurance-vie": [(0, fiscalite_barres)],
    "passer-un-ordre": [(0, carnet)],
    "investir-regulierement": [(2, dca)],
    "lire-les-comptes": [(0, resultat_cascade)],
    "ratios-per-rendement": [(0, per)],
    "dividendes": [(2, detachement)],
    "bougies-tendances": [(0, bougies), (1, tendance), (2, support_res)],
    "moyennes-rsi-macd": [(0, moyennes), (1, rsi)],
    "volatilite-et-ia": [(1, eventail)],
    "obligations-en-detail": [(1, taux_prix)],
    "diversification": [(1, correlation)],
    "construire-son-portefeuille": [(3, reequilibrage)],
    "levier-options-cfd": [(0, levier)],
    "devises-risque-de-change": [(1, change)],
    "lire-un-dic": [(1, sri)],
    "blockchain-bitcoin": [(0, blocs)],
    "psychologie-investisseur": [(0, emotions)],
}

CSS = (".l-fig{margin:18px 0;border:1px solid var(--a-line);border-radius:12px;padding:14px 12px 10px;background:var(--a-bg)}"
       ".l-fig svg{max-width:560px;margin:0 auto}.l-fig figcaption{font-size:14px;color:var(--a-muted);margin-top:8px;line-height:1.5}"
       ".l-fig figcaption b{display:block;color:var(--a-ink);font-size:14.5px;margin-bottom:2px}")


def figures(ch_id):
    """[(index_mini_leçon, html)] pour ce chapitre ; une figure en erreur est simplement ignorée."""
    out = []
    for s, f in FIGURES.get(ch_id, []):
        try:
            out.append((s, f()))
        except Exception:
            pass
    return out
