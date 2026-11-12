"""Version 77 : contrôle automatique de l'Académie, lancé à chaque génération du site.

But : ne jamais publier un cours cassé ou un chiffre faux. Si un contrôle échoue, la génération s'arrête
(l'ancienne version du site reste en ligne) et le message dit exactement quoi corriger.

Ce qui est vérifié :
  1. la structure de chaque chapitre (un exercice par mini-leçon, bonnes réponses dans la liste, pas de choix en double…) ;
  2. les encadrés et les simulateurs (ils pointent vers une mini-leçon qui existe) ;
  3. les calculs cités dans les leçons, rejoués ici en Python ;
  4. après génération : les liens internes des pages de l'Académie.

À la main : python -m bourse_bot.verif_academie
"""
from __future__ import annotations

import math
import os
import re


def _calculs():
    """(ce que dit le cours, valeur recalculée, valeur écrite dans le cours, tolérance)."""
    from .academie_labo import PFU, PS
    def composes(c, t, n): return c * (1 + t / 100) ** n
    def mensuel(m, t, n):
        tm = t / 100 / 12
        return m * ((1 + tm) ** (n * 12) - 1) / tm
    def obligation(r, n): return sum(30 / (1 + r / 100) ** k for k in range(1, n + 1)) + 1000 / (1 + r / 100) ** n
    faces = sum(math.comb(10, k) * 0.42 ** k * 0.58 ** (10 - k) for k in range(6, 11))
    return [
        ("PFU 2026 = 12,8 % + prélèvements sociaux", 12.8 + PS, PFU, 0.001),
        ("1 000 € à 5 % pendant 10 ans", composes(1000, 5, 10), 1629, 1),
        ("1 000 € à 5 % pendant 40 ans", composes(1000, 5, 40), 7040, 1),
        ("10 000 € à 7 % pendant 30 ans (environ 76 000 €)", composes(10000, 7, 30), 76000, 300),
        ("10 000 € à 5 % pendant 30 ans (environ 43 000 €)", composes(10000, 5, 30), 43000, 300),
        ("frais : 10 000 € à 5,8 % pendant 30 ans (environ 54 000 €)", composes(10000, 5.8, 30), 54000, 400),
        ("frais : 10 000 € à 4,8 % pendant 30 ans (environ 41 000 €)", composes(10000, 4.8, 30), 41000, 400),
        ("50 € par mois pendant 40 ans à 5 % (environ 76 000 €)", mensuel(50, 5, 40), 76000, 500),
        ("règle de 72 : inflation de 3 % → 24 ans", 72 / 3, 24, 0),
        ("gain de 1 000 € en compte-titres : impôt", 1000 * PFU / 100, 314, 0.001),
        ("gain de 1 000 € en PEA de plus de 5 ans : impôt", 1000 * PS / 100, 186, 0.001),
        ("500 € de dividendes : impôt", 500 * PFU / 100, 157, 0.001),
        ("600 € de plus-value nette : impôt", 600 * PFU / 100, 188.40, 0.001),
        ("50 € de plus-value crypto : impôt", 50 * PFU / 100, 15.70, 0.001),
        ("ordre au marché : prix moyen de 30 actions à 50,00 € et 70 à 50,40 €", (30 * 50 + 70 * 50.40) / 100, 50.28, 0.001),
        ("perte de 34 % : hausse nécessaire (environ 52 %)", 34 / 66 * 100, 52, 0.6),
        ("perte de 50 % : hausse nécessaire", 50 / 50 * 100, 100, 0),
        ("portefeuille 80 % actions, actions à −40 %", 0.8 * 40, 32, 0),
        ("rééquilibrage : 70 % de 12 100 €", 0.7 * 12100, 8470, 0),
        ("rééquilibrage : part des actions après +30 %", 9100 / 12100 * 100, 75, 0.5),
        ("1 % par jour pendant un an (environ ×38)", 1.01 ** 365, 38, 0.5),
        ("1 % par jour pendant deux ans : plus d'un million pour 1 000 €", 1 if 1000 * 1.01 ** 730 > 1e6 else 0, 1, 0),
        ("pièce à 58 % : au moins 6 faces sur 10 lancers arrive plus d'une fois sur dix", 1 if faces > 0.1 else 0, 1, 0),
        ("valeur aujourd'hui d'1 € dans 10 ans à 2 %", 1 / 1.02 ** 10, 0.82, 0.005),
        ("valeur aujourd'hui d'1 € dans 10 ans à 5 %", 1 / 1.05 ** 10, 0.61, 0.005),
        ("1 000 $ à 1,10 $ pour 1 €", 1000 / 1.10, 909, 0.5),
        ("1 000 $ à 1,20 $ pour 1 €", 1000 / 1.20, 833, 0.5),
        ("perte de change de 1,10 à 1,20 (environ 8 %)", (1 - 1.10 / 1.20) * 100, 8, 0.5),
        ("action +10 %, dollar −10 %", (1.10 * 0.90 - 1) * 100, -1, 0.001),
        ("dilution : 100 actions sur 1 250", 100 / 1250 * 100, 8, 0),
        ("option : gain de 8 € pour 2 € misés", 60 - 50 - 2, 8, 0),
        ("300 € par jour sur 250 jours", 300 * 250, 75000, 0),
        ("or : de 1 900 $ à 1 045 $", (1900 - 1045) / 1900 * 100, 45, 0.1),
        ("SCPI : 10 % de frais sur 8 000 €", 8000 * 0.10, 800, 0),
        ("SCPI : 5 % par an sur 8 000 € pendant 3 ans", 8000 * 0.05 * 3, 1200, 0),
        ("or à 50 % du portefeuille, −45 % (plus de 22 %)", 0.5 * 45, 22.5, 0),
        ("obligation à 3 % quand le marché est à 3 % : prix", obligation(3, 10), 1000, 0.01),
        ("Lumen : PER", 45 / 3, 15, 0), ("Lumen : rendement (environ 2,7 %)", 1.20 / 45 * 100, 2.7, 0.05),
        ("Lumen : capitalisation en M€", 10 * 45, 450, 0),
        ("Léa : 70 % de 300 €", 0.7 * 300, 210, 0), ("Léa : 20 % de 300 €", 0.2 * 300, 60, 0),
        ("halving : 50 divisé 4 fois par deux", 50 / 2 ** 4, 3.125, 0),
    ]


def verifier() -> list:
    """Renvoie la liste des problèmes trouvés (vide si tout va bien)."""
    from . import formation
    from .formation_exos import EXOS
    from .formation_plus import PLUS, LABOS, TITRES
    from .academie_labo import NOMS
    from .academie_graphiques import exercices as graphes
    from .academie import cle_q
    pb = []
    ids = [c["id"] for c in formation.CHAPITRES]
    for i in set(ids):
        if ids.count(i) > 1:
            pb.append(f"identifiant de chapitre en double : {i}")
    niveaux = {n[0] for n in formation.NIVEAUX}
    cles = {}

    def question(ou, q, choix, bonne):
        if not (isinstance(bonne, int) and 0 <= bonne < len(choix)):
            pb.append(f"{ou} : la bonne réponse n'est pas dans la liste ({q[:50]})")
        if len(set(choix)) != len(choix) or any(not str(x).strip() for x in choix):
            pb.append(f"{ou} : choix vide ou en double ({q[:50]})")
        if len(choix) < 2:
            pb.append(f"{ou} : il faut au moins deux choix ({q[:50]})")
        k = cle_q(q)
        if cles.setdefault(k, q) != q:
            pb.append(f"{ou} : deux questions différentes ont la même clé {k}")

    for c in formation.CHAPITRES:
        cid = c["id"]
        if not re.fullmatch(r"[a-z0-9-]+", cid):
            pb.append(f"{cid} : identifiant invalide")
        if c["niveau"] not in niveaux:
            pb.append(f"{cid} : module {c['niveau']} inconnu")
        for champ in ("titre", "desc", "mots", "sections", "retenir", "quiz", "exercice", "sources"):
            if not c.get(champ):
                pb.append(f"{cid} : champ « {champ} » manquant ou vide")
        n = len(c.get("sections", []))
        ex = EXOS.get(cid)
        if ex is None or len(ex) != n:
            pb.append(f"{cid} : {n} mini-leçons mais {0 if ex is None else len(ex)} exercices")
        for x in ex or []:
            if x["type"] == "nombre":
                if not isinstance(x["rep"], (int, float)) or x["tol"] < 0:
                    pb.append(f"{cid} : exercice de calcul mal défini ({x['q'][:50]})")
                cles.setdefault(cle_q(x["q"]), x["q"])
            else:
                question(cid, x["q"], x["choix"], x["bonne"])
            if not x.get("expl"):
                pb.append(f"{cid} : exercice sans explication ({x['q'][:50]})")
        for q, choix, b, e in c.get("quiz", []):
            question(cid + " (bilan)", q, choix, b)
            if not e:
                pb.append(f"{cid} : question de bilan sans explication")
        if len(c.get("quiz", [])) < 3:
            pb.append(f"{cid} : il faut au moins 3 questions de bilan")
        for nom, url in c.get("sources", []):
            if not (url.startswith("https://") or url.startswith("../")):
                pb.append(f"{cid} : source sans adresse https ({nom})")
        for t, h in c.get("sections", []):
            if h.count("<p") != h.count("</p>") or h.count("<ul") != h.count("</ul>") or h.count("<table") != h.count("</table>"):
                pb.append(f"{cid} : balises mal fermées dans « {t} »")
    for cid, items in PLUS.items():
        if cid not in ids:
            pb.append(f"encadrés : chapitre inconnu {cid}")
            continue
        n = len(next(c for c in formation.CHAPITRES if c["id"] == cid)["sections"])
        for s, t, h in items:
            if not 0 <= s < n:
                pb.append(f"encadrés de {cid} : mini-leçon {s} inexistante")
            if t not in TITRES:
                pb.append(f"encadrés de {cid} : type inconnu {t}")
            if h.count("<p") != h.count("</p>") or h.count("<b>") != h.count("</b>") or h.count("<i>") != h.count("</i>"):
                pb.append(f"encadrés de {cid} : balises mal fermées")
    for cid, items in LABOS.items():
        if cid not in ids:
            pb.append(f"simulateurs : chapitre inconnu {cid}")
            continue
        n = len(next(c for c in formation.CHAPITRES if c["id"] == cid)["sections"])
        for it in items:
            if not 0 <= it[0] < n or it[1] not in NOMS:
                pb.append(f"simulateur de {cid} : mal défini {it}")
    for cid, items in graphes().items():
        if cid not in ids:
            pb.append(f"graphiques : chapitre inconnu {cid}")
            continue
        n = len(next(c for c in formation.CHAPITRES if c["id"] == cid)["sections"])
        for s, g in items:
            if not 0 <= s < n:
                pb.append(f"graphique de {cid} : mini-leçon {s} inexistante")
            question(cid + " (graphique)", g["q"] + "|" + cid + str(s), g["choix"], g["bonne"])
    from .formation_plus import PRATIQUE
    for i, (_t, lien) in PRATIQUE.items():
        if i not in ids or not lien.endswith(".html"):
            pb.append(f"mise en pratique : entrée invalide {i}")
    from .formation_plus import OBJECTIFS
    for t, _d, lst in OBJECTIFS:
        for i in lst:
            if i not in ids:
                pb.append(f"parcours « {t} » : chapitre inconnu {i}")
    for n in niveaux:
        if not any(c["niveau"] == n and not c.get("cas") for c in formation.CHAPITRES):
            pb.append(f"module {n} : aucun chapitre")
    for texte, calcul, ecrit, tol in _calculs():
        if abs(calcul - ecrit) > tol + 1e-9:
            pb.append(f"calcul faux dans le cours : {texte} → {calcul:.4g}, le cours dit {ecrit}")
    return pb


def verifier_liens(dossier: str) -> list:
    """Après génération : chaque lien interne des pages de l'Académie mène à un fichier qui existe."""
    pb = []
    pages = [os.path.join(dossier, "formation.html")]
    d = os.path.join(dossier, "formation")
    if os.path.isdir(d):
        pages += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".html")]
    for p in pages:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            h = f.read()
        for lien in set(re.findall(r"""href=['"]([^'"#?:]+\.html)(?:[#?][^'"]*)?['"]""", h)):
            if "$" in lien or "{" in lien:   # lien fabriqué par le navigateur, pas un vrai fichier
                continue
            cible = os.path.normpath(os.path.join(os.path.dirname(p), lien))
            if not os.path.exists(cible):
                pb.append(f"{os.path.relpath(p, dossier)} : lien cassé vers {lien}")
    return pb


if __name__ == "__main__":
    probs = verifier()
    print("\n".join(probs) if probs else f"Académie : tout est cohérent ({len(_calculs())} calculs revérifiés).")
    raise SystemExit(1 if probs else 0)
