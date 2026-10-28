"""Les connaissances de l'IA ne doivent jamais se perdre.

Trois fichiers gardent ce que l'IA a appris pendant les entraînements faits sur ton PC :
- historique/modele.json       → la recette retenue et le journal des entraînements
- historique/essais_ia.json    → la mémoire de tous les réglages déjà testés (sert à guider les suivants)
- historique/apprentissage.json → les titres d'apprentissage en plus, quand ils ont prouvé leur utilité

Le site en ligne réécrit aussi modele.json chaque soir (nouvelle évaluation). Quand on remet le site en
ligne, ou quand on envoie un entraînement, on FUSIONNE donc les deux versions au lieu d'en écraser une :
on garde l'évaluation la plus récente du site ET les connaissances les plus récentes de l'IA.
"""
from __future__ import annotations

import json
import os

DOSSIER = "historique"
MODELE, ESSAIS, APPRENTISSAGE = "modele.json", "essais_ia.json", "apprentissage.json"
FICHIERS = (MODELE, ESSAIS, APPRENTISSAGE)


def lire(dossier: str = DOSSIER) -> dict:
    out = {}
    for nom in FICHIERS:
        try:
            with open(os.path.join(dossier, nom), encoding="utf-8") as f:
                out[nom] = json.load(f)
        except (OSError, ValueError):
            out[nom] = None
    return out


def _date_recette(m):
    return str(((m or {}).get("recette") or {}).get("date") or "")


def _signature(e):
    return json.dumps([sorted(e.get("variables") or []), bool(e.get("par_marche")),
                       sorted((e.get("params") or {}).items(), key=lambda kv: kv[0]), e.get("date")], default=str)


def fusionner(local: dict, distant: dict) -> dict:
    """Renvoie les contenus fusionnés (sans rien écrire)."""
    out = {}
    # 1. modele.json : base = version la plus complète du site, + la recette et le journal les plus récents
    ml, md = local.get(MODELE), distant.get(MODELE)
    if md is None or ml is None:
        out[MODELE] = md if ml is None else ml
    else:
        m = dict(md)
        if _date_recette(ml) > _date_recette(md):
            m["recette"] = ml["recette"]
            if ml.get("configuration"):
                m["configuration"] = ml["configuration"]
            m["date"] = "2000-01-01T00:00:00"   # le site refera un test complet avec la recette
        vus, journal = set(), []
        for e in (md.get("entrainements") or []) + (ml.get("entrainements") or []):
            cle = str(e.get("date"))
            if cle not in vus:
                vus.add(cle)
                journal.append(e)
        m["entrainements"] = sorted(journal, key=lambda e: str(e.get("date")))[-20:]
        out[MODELE] = m
    # 2. essais_ia.json : union des deux mémoires
    el, ed = (local.get(ESSAIS) or {}).get("essais", []), (distant.get(ESSAIS) or {}).get("essais", [])
    if el or ed:
        vus, tout = set(), []
        for e in ed + el:
            s = _signature(e)
            if s not in vus:
                vus.add(s)
                tout.append(e)
        out[ESSAIS] = {"essais": sorted(tout, key=lambda e: str(e.get("date") or ""))[-600:]}
    else:
        out[ESSAIS] = local.get(ESSAIS) or distant.get(ESSAIS)
    # 3. apprentissage.json : le plus récent
    al, ad = local.get(APPRENTISSAGE), distant.get(APPRENTISSAGE)
    out[APPRENTISSAGE] = al if (al and (not ad or str(al.get("date")) >= str(ad.get("date")))) else ad
    return out


def ecrire(contenus: dict, dossier: str = DOSSIER):
    os.makedirs(dossier, exist_ok=True)
    for nom, v in contenus.items():
        if v is None:
            continue
        with open(os.path.join(dossier, nom), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, indent=1 if nom != ESSAIS else None, default=lambda x: None)
