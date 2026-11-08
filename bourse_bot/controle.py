"""Version 67 : contrôle automatique de TOUTES les prévisions avant publication.

Chaque titre est vérifié (cours, fourchette, éventail, chances de hausse, agitation, risque de chute). Une prévision
incohérente n'est jamais publiée : elle est retirée de la fiche (le titre reste affiché, avec ses cours) et
l'anomalie est notée dans le rapport. Mieux vaut « pas de prévision aujourd'hui » qu'un chiffre faux.
"""
from __future__ import annotations

import math


def _ok(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v)


def verifier_titre(t: dict) -> list:
    pb = []
    prix = t.get("prix")
    if not _ok(prix) or prix <= 0:
        return ["cours manquant ou nul"]
    p = t.get("proba_hausse")
    if p is not None and (not _ok(p) or not 0 <= p <= 1):
        pb.append(f"chances de hausse impossibles ({p})")
    f = t.get("fourchette") or []
    if f:
        if len(f) != 2 or not all(_ok(x) and x > 0 for x in f) or f[0] >= f[1]:
            pb.append("fourchette illisible")
        elif not (f[0] * 0.98 <= prix * 1.0 <= f[1] * 1.02) and not (f[0] < prix * 1.6 and f[1] > prix * 0.6):
            pb.append("fourchette très loin du cours")
        elif f[1] / f[0] > 20:
            pb.append("fourchette démesurée")
    k = t.get("cone") or {}
    if k:
        h, m, b = k.get("haut") or [], k.get("mediane") or [], k.get("bas") or []
        if not (len(h) == len(m) == len(b) > 1) or not all(_ok(x) and x > 0 for x in h + m + b):
            pb.append("éventail illisible")
        else:
            if any(not (bb <= mm * 1.0001 and mm <= hh * 1.0001) for hh, mm, bb in zip(h, m, b)):
                pb.append("éventail inversé (bas au-dessus du haut)")
            if abs(m[0] / prix - 1) > 0.25:
                pb.append("éventail qui ne part pas du cours")
    r = t.get("risque_prevu") or {}
    if r:
        mv, ch = r.get("mouvement"), r.get("chute")
        if mv is not None and (not _ok(mv) or not 0 < mv < 3):
            pb.append(f"agitation prévue impossible ({mv})")
        if ch is not None and (not _ok(ch) or not 0 <= ch <= 1):
            pb.append(f"risque de chute impossible ({ch})")
    s = t.get("serie") or {}
    c = [x for x in (s.get("c") or []) if x is not None]
    if c and _ok(c[-1]) and c[-1] > 0 and abs(prix / c[-1] - 1) > 0.5 and not t.get("live"):
        pb.append("cours affiché très différent du dernier cours de l'historique")
    return pb


def appliquer(payload: dict) -> dict:
    """Vérifie chaque titre ; retire la prévision des titres incohérents. Renvoie le rapport."""
    rapport = {"verifies": 0, "retires": {}}
    for t in payload.get("titres", []):
        rapport["verifies"] += 1
        pb = verifier_titre(t)
        if not pb:
            continue
        rapport["retires"][t.get("ticker", "?")] = pb
        # on garde le titre et ses cours, mais aucune prévision douteuse n'est publiée
        for cle in ("proba_hausse", "proba_ia", "proba_marche", "fourchette", "cone", "proba_ia1", "proba_ia2"):
            if cle in t:
                t[cle] = None
        t["avis_net"] = False
        t["signal_fort"] = False
        r = t.get("risque_prevu") or {}
        if any("agitation" in x or "chute" in x for x in pb):
            t["risque_prevu"] = None
        elif r:
            t["risque_prevu"] = r
        t["controle"] = pb
    payload["controle"] = rapport
    return rapport
