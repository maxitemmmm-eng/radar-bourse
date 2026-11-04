"""Version 62 : « le défi 5 jours de l'IA », un test public et honnête.

Chaque semaine, l'IA choisit les 3 cryptos auxquelles elle donne le plus de chances de monter (son avis brut). Cinq jours plus
tard, le site compare leur résultat à la moyenne de toutes les cryptos suivies (le « hasard » : acheter un peu de tout).
Tout est gardé dans historique/defi_5j.json et affiché sur l'accueil, ratés compris. Ce n'est pas un conseil : sur les
années passées, l'IA n'a pas fait mieux que la tendance habituelle pour le sens du prix des cryptos ; ce défi permet à
chacun de le vérifier en conditions réelles.

Le défi n'avance que lors du calcul complet du soir (ou sur le PC), pour que le fichier enregistré sur GitHub fasse foi ;
les mises à jour de chaque heure ne font que l'afficher."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from . import config

FICHIER = os.path.join(config.DOSSIER_HISTORIQUE, "defi_5j.json")
JOURS = 5
NB = 3


def _lire() -> dict:
    try:
        with open(FICHIER, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _cryptos(payload):
    return {t["ticker"]: t for t in payload.get("titres", []) if t.get("marche") == "crypto" and t.get("prix")}


def mettre_a_jour(payload: dict, ecrire: bool) -> dict:
    """Clôture le défi en cours s'il a 5 jours, en lance un nouveau sinon. Renvoie ce que la page affiche."""
    d = _lire()
    d.setdefault("resultats", [])
    cryptos = _cryptos(payload)
    maintenant = datetime.fromisoformat(str(payload.get("genere_le") or datetime.now().isoformat(timespec="seconds"))[:19])
    en_cours = d.get("en_cours")
    change = False
    if ecrire and en_cours and maintenant >= datetime.fromisoformat(en_cours["fin"]):
        rend = lambda tk, p0: (cryptos[tk]["prix"] / p0 - 1) if tk in cryptos and p0 else None
        ia = [rend(p["tk"], p["prix"]) for p in en_cours["choix"]]
        ia = [r for r in ia if r is not None]
        tous = [rend(tk, p0) for tk, p0 in en_cours.get("panier", {}).items()]
        tous = [r for r in tous if r is not None]
        if ia and tous:
            r_ia, r_tous = sum(ia) / len(ia), sum(tous) / len(tous)
            d["resultats"].append({"debut": en_cours["debut"], "fin": maintenant.isoformat(timespec="minutes"),
                                   "choix": [{"tk": p["tk"], "nom": p["nom"], "rend": round(rend(p["tk"], p["prix"]) or 0, 4)} for p in en_cours["choix"]],
                                   "ia": round(r_ia, 4), "moyenne": round(r_tous, 4), "gagne": r_ia > r_tous})
        en_cours = None
        change = True
    if ecrire and not en_cours and len(cryptos) >= 6:
        notes = sorted(((t.get("proba_ia") if t.get("proba_ia") is not None else t.get("proba_brute")), tk) for tk, t in cryptos.items()
                       if (t.get("proba_ia") if t.get("proba_ia") is not None else t.get("proba_brute")) is not None)
        if len(notes) >= NB:
            choix = [cryptos[tk] for _, tk in sorted(notes, reverse=True)[:NB]]
            en_cours = {"debut": maintenant.isoformat(timespec="minutes"), "fin": (maintenant + timedelta(days=JOURS) - timedelta(hours=3)).isoformat(timespec="minutes"),   # marge : le calcul du soir ne tombe pas toujours à la même minute
                        "choix": [{"tk": t["ticker"], "nom": t["nom"], "prix": t["prix"], "proba": round(float(t.get("proba_ia") or t.get("proba_brute")), 4)} for t in choix],
                        "panier": {tk: t["prix"] for tk, t in cryptos.items()}}
            change = True
    d["en_cours"] = en_cours
    d["resultats"] = d["resultats"][-104:]
    if change and ecrire:
        os.makedirs(os.path.dirname(FICHIER), exist_ok=True)
        with open(FICHIER, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    res = d["resultats"]
    # ce que la page affiche (sans le panier complet, inutile pour le visiteur)
    vue = None
    if en_cours:
        vue = {"debut": en_cours["debut"], "fin": en_cours["fin"],
               "choix": [{**p, "maintenant": cryptos.get(p["tk"], {}).get("prix")} for p in en_cours["choix"]]}
    return {"en_cours": vue, "resultats": res[-8:], "bilan": {"n": len(res), "gagnes": sum(1 for r in res if r.get("gagne")),
            "ia_cumul": round(sum(r["ia"] for r in res), 4) if res else None, "moyenne_cumul": round(sum(r["moyenne"] for r in res), 4) if res else None}}
