"""Version 53 : une image de partage (1200×630) pour chaque type de page, au lieu d'une seule pour tout le site.
C'est l'image qui s'affiche quand un lien est partagé (WhatsApp, X, Discord, LinkedIn…) : elle donne envie de cliquer.
Dessinée par le programme (aucune photo achetée, aucun droit d'auteur tiers), dans les couleurs du site."""
from __future__ import annotations

import os

FOND, FOND2, BLEU, VERT, ROUGE, TEXTE, GRIS = "#0f1b2d", "#16264a", "#7398ff", "#35c27d", "#ff6b62", "#ffffff", "#a9b8d0"

# chemin de la page → (titre, sous-titre, motif). Les pages d'un dossier (guides/…) prennent l'image du dossier.
PAGES = {
    "outils.html": ("Outils gratuits", "Simulateur, convertisseur crypto, intérêts composés, plus-value", "outils"),
    "outils/si-javais-investi.html": ("Si j'avais investi 100 €…", "Combien j'aurais aujourd'hui ? Sur les vrais cours", "courbe"),
    "outils/convertisseur.html": ("Convertisseur crypto", "Bitcoin, ether, actions ↔ euros et dollars", "pieces"),
    "outils/interets-composes.html": ("Intérêts composés", "Ce que deviendra ton épargne, mois après mois", "barres"),
    "outils/plus-value.html": ("Plus-value et flat tax 2026", "Ton gain après frais et l'impôt à prévoir", "pourcent"),
    "en/tools/if-i-had-invested.html": ("If I had invested $100…", "How much would I have today? Real prices", "courbe"),
    "en/tools/crypto-converter.html": ("Crypto converter", "Bitcoin, Ether, stocks ↔ USD and EUR", "pieces"),
    "en/tools/compound-interest.html": ("Compound interest", "What your savings become, month after month", "barres"),
    "en/tools/capital-gains.html": ("Capital gains calculator", "Your gain after fees and the tax at your rate", "pourcent"),
    "guides.html": ("Guides Bourse et crypto", "Les questions de tout le monde, des réponses honnêtes", "livre"),
    "guides/": ("Guide Bourse et crypto", "Une réponse simple et honnête, sans promesse", "livre"),
    "en/guides.html": ("Stock & crypto guides", "Honest answers for beginners", "livre"),
    "en/guides/": ("Stock & crypto guide", "A simple, honest answer, no hype", "livre"),
    "apprendre.html": ("Apprendre la Bourse", "8 mini-cours gratuits, du tout début", "livre"),
    "lecons/": ("Apprendre la Bourse", "Un mini-cours gratuit et simple", "livre"),
    "glossaire.html": ("Le glossaire de la Bourse", "RSI, MACD, PER, volatilité… expliqués simplement", "livre"),
    "glossaire/": ("Le glossaire de la Bourse", "Un mot de la Bourse, expliqué simplement", "livre"),
    "fonctionnalites.html": ("Tout ce que fait Radar Bourse", "Prévisions IA, simulateur boursier, outils, guides", "cible"),
    "simulateur-boursier.html": ("Simulateur boursier gratuit", "10 000 € virtuels pour t'entraîner sans risque", "courbe"),
    "a-propos.html": ("À propos de Radar Bourse", "Un projet éducatif, gratuit et transparent", "radar"),
    "contact.html": ("Contacter Radar Bourse", "Un bug, une idée ? Écris-nous", "bulle"),
    "classements.html": ("Les classements du jour", "Les titres les plus agités, les plus calmes, les plus à risque", "barres"),
    "classements/": ("Classement du jour", "Mis à jour automatiquement chaque jour", "barres"),
    "comparer.html": ("Comparer deux titres", "Agitation, risque de chute, chances : côte à côte", "duel"),
    "comparer/": ("Lequel choisir ?", "Deux titres comparés par l'IA, chiffres vérifiés", "duel"),
    "resultats.html": ("Les résultats réels de l'IA", "Chaque prévision vérifiée, ratés compris", "cible"),
    "fiche-technique-ia.html": ("La fiche technique de l'IA", "Ce qu'elle prévoit bien, et ce qu'elle ne sait pas", "radar"),
    "suivi-chute.html": ("Le risque de chute, vérifié", "Les titres jugés à risque ont-ils vraiment chuté ?", "courbe_bas"),
    "previsions.html": ("Prévisions bourse et crypto", "Ce que l'IA prévoit pour le mois qui vient", "courbe"),
    "portefeuille.html": ("La sélection IA du mois", "10 actions suivies en public, ratés compris", "barres"),
    "titres.html": ("Tous les titres suivis", "Plus de 200 actions, ETF et cryptos", "radar"),
    "fonction:previsions": ("Prévisions à un mois", "Plus de 200 actions, ETF et cryptos, chaque heure", "radar"),
    "fonction:fourchette": ("À combien dans un mois ?", "Une fourchette de prix probable, vérifiée", "cone"),
    "fonction:arene": ("L'Arène : toi contre l'IA", "Remonte le temps et devine la suite", "manette"),
    "fonction:langues": ("En 14 langues", "Français, anglais, espagnol, arabe, chinois…", "globe"),
}


def _police(taille, gras=False):
    from PIL import ImageFont
    for nom in (("DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf"), ("arialbd.ttf" if gras else "arial.ttf")):
        for d in ("/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", ""):
            try:
                return ImageFont.truetype(d + nom, taille)
            except Exception:
                continue
    return ImageFont.load_default()


def _lignes(dr, texte, police, largeur):
    mots, lignes, cur = texte.split(), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if dr.textlength(essai, font=police) <= largeur:
            cur = essai
        else:
            lignes.append(cur); cur = m
    return lignes + ([cur] if cur else [])


def _symbole(dr, s, cx, cy, taille):
    """Écrit un symbole centré ; le ₿ (absent de beaucoup de polices) est dessiné : un B barré de deux traits."""
    f = _police(taille, True)
    lettre = "B" if s == "₿" else s
    w = dr.textlength(lettre, font=f)
    x, y = cx - w / 2, cy - taille * 0.58
    dr.text((x, y), lettre, font=f, fill=FOND)
    if s == "₿":
        for dx in (0.36, 0.6):
            dr.line((x + w * dx, y + taille * 0.02, x + w * dx, y + taille * 1.12), fill=FOND, width=max(3, taille // 14))


def _motif(dr, motif, cx, cy):
    """Petit dessin à droite de l'image, selon le sujet de la page."""
    if motif == "radar":
        for r, c in ((200, "#1a2d57"), (140, "#1f3566"), (80, "#24407a")):
            dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=4)
        dr.line((cx, cy, cx + 150, cy - 120), fill=VERT, width=9)
        dr.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=VERT)
        dr.ellipse((cx + 60, cy + 50, cx + 80, cy + 70), fill=VERT)
    elif motif in ("courbe", "courbe_bas"):
        import math
        pts = []
        for i in range(13):
            x = cx - 200 + i * 33
            base = (i * 14) if motif == "courbe" else (-i * 11)
            y = cy + 90 - base - 28 * math.sin(i * 1.3)
            pts.append((x, y))
        dr.line([(cx - 210, cy + 150), (cx + 210, cy + 150)], fill="#24407a", width=3)
        dr.line(pts, fill=VERT if motif == "courbe" else ROUGE, width=10, joint="curve")
        x, y = pts[-1]
        dr.ellipse((x - 14, y - 14, x + 14, y + 14), fill=VERT if motif == "courbe" else ROUGE)
    elif motif == "pieces":
        for (dx, dy, r, s, c) in ((-90, -40, 95, "₿", "#f7931a"), (70, 40, 80, "€", BLEU), (-30, 120, 60, "$", VERT)):
            dr.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=c)
            _symbole(dr, s, cx + dx, cy + dy, int(r * 1.1))
    elif motif == "barres":
        for i, h in enumerate((60, 90, 130, 185, 250, 330)):
            x = cx - 190 + i * 66
            dr.rounded_rectangle((x, cy + 160 - h, x + 46, cy + 160), radius=8, fill=BLEU if i < 5 else VERT)
    elif motif == "pourcent":
        dr.rounded_rectangle((cx - 150, cy - 170, cx + 150, cy + 170), radius=22, fill=FOND2, outline="#24407a", width=4)
        f = _police(170, True)
        w = dr.textlength("%", font=f)
        dr.text((cx - w / 2, cy - 120), "%", font=f, fill=VERT)
        for i in range(3):
            dr.rounded_rectangle((cx - 110, cy + 80 + i * 26, cx + 110 - i * 50, cy + 92 + i * 26), radius=6, fill="#24407a")
    elif motif == "livre":
        for i, c in enumerate((BLEU, VERT, "#f2c14e")):
            y = cy + 110 - i * 78
            dr.rounded_rectangle((cx - 170 + i * 14, y - 60, cx + 170 - i * 14, y), radius=10, fill=c)
            dr.rectangle((cx - 140 + i * 14, y - 42, cx + 60, y - 36), fill=FOND)
    elif motif == "cible":
        for r, c in ((190, BLEU), (130, FOND), (80, VERT), (35, FOND)):
            dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
        dr.line((cx + 170, cy - 170, cx + 6, cy - 6), fill=TEXTE, width=10)
    elif motif == "bulle":
        dr.rounded_rectangle((cx - 200, cy - 140, cx + 180, cy + 90), radius=40, fill=BLEU)
        dr.polygon([(cx - 120, cy + 80), (cx - 160, cy + 170), (cx - 40, cy + 85)], fill=BLEU)
        for i in range(3):
            dr.ellipse((cx - 100 + i * 80, cy - 45, cx - 60 + i * 80, cy - 5), fill=FOND)
    elif motif == "duel":
        dr.rounded_rectangle((cx - 210, cy - 130, cx - 20, cy + 150), radius=18, fill=BLEU)
        dr.rounded_rectangle((cx + 20, cy - 80, cx + 210, cy + 150), radius=18, fill=VERT)
        f = _police(90, True)
        dr.text((cx - 32, cy - 220), "VS", font=f, fill=TEXTE)
    elif motif == "cone":
        dr.polygon([(cx - 200, cy + 10), (cx + 200, cy - 170), (cx + 200, cy + 190)], fill="#1f3566")
        dr.polygon([(cx - 200, cy + 10), (cx + 200, cy - 90), (cx + 200, cy + 110)], fill="#2b4a8f")
        dr.line([(cx - 200, cy + 10), (cx + 200, cy + 10)], fill=VERT, width=8)
        dr.ellipse((cx - 214, cy - 4, cx - 186, cy + 24), fill=VERT)
    elif motif == "manette":
        dr.rounded_rectangle((cx - 200, cy - 90, cx + 200, cy + 110), radius=90, fill=BLEU)
        dr.rectangle((cx - 135, cy - 5, cx - 65, cy + 25), fill=FOND); dr.rectangle((cx - 115, cy - 25, cx - 85, cy + 45), fill=FOND)
        for dx, dy, c in ((85, -10, VERT), (130, 30, "#f2c14e")):
            dr.ellipse((cx + dx - 20, cy + dy - 20, cx + dx + 20, cy + dy + 20), fill=c)
    elif motif == "globe":
        dr.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), outline=BLEU, width=8)
        dr.ellipse((cx - 80, cy - 190, cx + 80, cy + 190), outline=BLEU, width=6)
        dr.line((cx, cy - 190, cx, cy + 190), fill=BLEU, width=6)
        for dy in (-95, 0, 95):
            w = int((190 ** 2 - dy ** 2) ** .5)
            dr.line((cx - w, cy + dy, cx + w, cy + dy), fill=VERT if dy == 0 else BLEU, width=6)
    elif motif == "outils":
        for i, (s, c) in enumerate((("₿", "#f7931a"), ("%", VERT), ("€", BLEU), ("↗", "#f2c14e"))):
            x, y = cx - 190 + (i % 2) * 200, cy - 170 + (i // 2) * 190
            dr.rounded_rectangle((x, y, x + 170, y + 160), radius=24, fill=c)
            _symbole(dr, s, x + 85, y + 80, 96)


def dessiner(chemin_png: str, titre: str, sous_titre: str, motif: str, nom: str = "Radar Bourse") -> bool:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), FOND)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, 0, W, 10), fill=VERT)
    _motif(dr, motif, 930, 330)
    # nom du site + petit logo
    dr.ellipse((70, 58, 112, 100), outline=BLEU, width=4); dr.line((91, 79, 108, 66), fill=VERT, width=5)
    dr.text((128, 58), nom, font=_police(36, True), fill=TEXTE)
    # titre sur 3 lignes maximum, sous-titre sur 2 ; on réduit le titre si l'ensemble touche le badge du bas
    fs = _police(32)
    ls = _lignes(dr, sous_titre, fs, 580)[:2]
    for taille in (68, 60, 52, 46):
        f = _police(taille, True)
        lt = _lignes(dr, titre, f, 580)[:3]
        if 175 + len(lt) * int(taille * 1.18) + 18 + len(ls) * 44 <= H - 125:
            break
    y = 175
    for l in lt:
        dr.text((70, y), l, font=f, fill=TEXTE); y += int(f.size * 1.18)
    for l in ls:
        dr.text((72, y + 18), l, font=fs, fill=GRIS); y += 44
    dr.rounded_rectangle((70, H - 112, 70 + dr.textlength("Gratuit · sans compte · résultats vérifiés", font=_police(26)) + 40, H - 62),
                         radius=25, fill=FOND2)
    dr.text((90, H - 102), "Gratuit · sans compte · résultats vérifiés", font=_police(26), fill=TEXTE)
    os.makedirs(os.path.dirname(chemin_png), exist_ok=True)
    img.save(chemin_png, optimize=True)
    return True


def generer(dossier: str) -> dict:
    """Dessine toutes les images ; renvoie {chemin de page ou dossier: image}."""
    out = {}
    for page, (titre, sous, motif) in PAGES.items():
        nom = "partage/pages/" + (page.rstrip("/").replace("/", "_") + "_dossier" if page.endswith("/") else
                                  page.replace("/", "_").replace(".html", "").replace(":", "_")) + ".png"
        if dessiner(os.path.join(dossier, nom), titre, sous, motif):
            out[page] = nom
    return out


def image_pour(chemin: str, images: dict) -> str | None:
    if chemin in images:
        return images[chemin]
    dossier = chemin.rsplit("/", 1)[0] + "/" if "/" in chemin else ""
    return images.get(dossier)
