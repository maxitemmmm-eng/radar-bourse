"""Version 88 : Prediction Engine 2.0 — ce que voit le visiteur pour chaque titre.

1. Trois horizons : 7 jours, 30 jours, 90 jours. À 30 jours, c'est l'avis de l'IA (testé sur des années jamais vues).
   À 7 et 90 jours, l'IA n'a pas encore prouvé sa fiabilité (l'entraînement de nuit l'examine) : on donne donc une
   estimation STATISTIQUE, clairement signalée, tirée du propre historique du titre (part des périodes en hausse et
   agitation habituelle), jamais présentée comme un avis de l'IA.
2. Hausse / stable / baisse : au lieu d'un seul pourcentage, trois chances qui font 100. « Stable » = le prix bouge
   de moins de ±2 % sur 30 jours (±1 % sur 7 jours, ±4 % sur 90 jours ; le double pour les cryptos). Les chances
   restent cohérentes avec l'avis de l'IA : hausse + moitié haute de « stable » = chances de hausse de l'IA.
3. Détecteur de situations où l'IA est moins fiable : marché nerveux, titre très agité pour son marché, avis
   hésitant, mouvement de plus de 25 % en un mois. Mesuré sur 2016-2026 (années jamais vues) : dans ces cas l'IA a vu
   juste 52,5 % du temps contre 57,4 % ailleurs, et c'était moins bien 9 années sur 11. L'IA donne quand même son
   avis (règle du site), mais le visiteur est prévenu.
"""
from __future__ import annotations

import math

import numpy as np

# mesuré sur les prévisions hors échantillon 2016-2026 (voir le texte ci-dessus) ; recalculé à la main à chaque version
DETECTEUR = {"signale": 0.525, "ailleurs": 0.574, "annees": "9 années sur 11", "part": 0.327}
_Z80 = 1.2816


def _phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def trois_chances(p_hausse: float, m: float, sigma: float, seuil: float) -> dict | None:
    """Hausse / stable / baisse (en %) à partir des chances de hausse et de la distribution prévue (log-rendements)."""
    if p_hausse is None or p_hausse != p_hausse or not sigma or sigma <= 0:
        return None
    hi, lo = math.log(1 + seuil), math.log(1 - seuil)
    st_haut = max(0.0, _phi((hi - m) / sigma) - _phi((0 - m) / sigma))
    st_bas = max(0.0, _phi((0 - m) / sigma) - _phi((lo - m) / sigma))
    h = max(0.0, p_hausse - st_haut)
    b = max(0.0, (1 - p_hausse) - st_bas)
    s = st_haut + st_bas
    tot = h + b + s
    if tot <= 0:
        return None
    h, s, b = h / tot, s / tot, b / tot
    vals = [round(h * 100), round(s * 100), round(b * 100)]
    vals[int(np.argmax(vals))] += 100 - sum(vals)   # la somme fait toujours 100
    return {"hausse": vals[0], "stable": vals[1], "baisse": vals[2], "seuil": seuil}


def horizons(close, item: dict, crypto: bool) -> dict:
    """Les trois horizons d'un titre. close : série des cours de clôture."""
    out = {}
    c = np.asarray(close, dtype=float)
    c = c[np.isfinite(c)]
    if len(c) < 260:
        return out
    r1 = np.diff(np.log(c))
    sd_jour = float(np.std(r1[-126:], ddof=1)) if len(r1) > 130 else float(np.std(r1, ddof=1))
    q = item.get("quantiles") or ()
    fois = 2 if crypto else 1
    prix = float(item.get("prix") or c[-1])
    # 30 jours : l'IA (quantiles appris + chances de hausse calibrées)
    k = item.get("cone") or {}
    if len(q) != 3 and k.get("mediane") and k.get("bas") and k.get("haut") and prix > 0:   # sinon : l'éventail affiché
        try:
            q = (math.log(k["bas"][-1] / prix), math.log(k["mediane"][-1] / prix), math.log(k["haut"][-1] / prix))
        except (TypeError, ValueError, ZeroDivisionError):
            q = ()
    if len(q) == 3 and item.get("proba_hausse") is not None:
        m, sig = float(q[1]), (float(q[2]) - float(q[0])) / (2 * _Z80)
        tc = trois_chances(float(item["proba_hausse"]), m, sig, 0.02 * fois)
        if tc:
            out["30"] = {**tc, "source": "ia", "bas": prix * math.exp(float(q[0])), "haut": prix * math.exp(float(q[2])),
                         "central": prix * math.exp(m)}
    # 7 et 90 jours : statistiques du titre lui-même, sur 5 ans au plus
    jours_an = 365 if crypto else 252
    for h, cle, seuil in ((7 if crypto else 5, "7", 0.01), (90 if crypto else 63, "90", 0.04)):
        n = min(len(c) - 1, 5 * jours_an)
        hist = c[-n - 1:]
        rets = np.log(hist[h:] / hist[:-h])
        if len(rets) < 100:
            continue
        p_up = float((rets > 0).mean())
        sig = sd_jour * math.sqrt(h)
        m = float(np.median(rets)) * 0.5   # tendance passée, volontairement amortie : le passé se répète mal
        tc = trois_chances(p_up, m, sig, seuil * fois)
        if tc:
            out[cle] = {**tc, "source": "stats", "bas": prix * math.exp(m - _Z80 * sig), "haut": prix * math.exp(m + _Z80 * sig),
                        "central": prix * math.exp(m), "part_hausse_passee": round(p_up * 100)}
    return out


def situation(item: dict, d, rang_agitation: float | None) -> dict:
    """Détecteur : pourquoi l'IA risque d'être moins fiable sur ce titre en ce moment."""
    raisons = []
    try:
        mv = d["marche_vol"].dropna()
        if len(mv) > 250 and float(mv.iloc[-1]) > float(mv.quantile(0.8)):
            raisons.append("le marché est nerveux en ce moment (parmi ses 20 % de périodes les plus agitées)")
    except Exception:
        pass
    if rang_agitation is not None and rang_agitation > 0.9:
        raisons.append("ce titre est parmi les 10 % les plus agités de son marché")
    p = item.get("proba_hausse")
    if p is not None and p == p and abs(p - 0.5) < 0.02:
        raisons.append("l'IA hésite : ses chances sont très proches de 50 sur 100")
    r21 = (item.get("perf") or {}).get("1 mois")
    if r21 is not None and abs(r21) > 0.25:
        raisons.append(f"le prix a bougé de plus de 25 % en un mois")
    return {"risquee": bool(raisons), "raisons": raisons}


def enregistrer_journal(payload: dict, dossier: str) -> int:
    """Experts « entreprise » et « actualités » : leurs chiffres du soir sont gardés (historique/journal_experts.csv).
    Dans quelques mois, on saura sur des données jamais modifiées s'ils aident à prévoir : ils ne voteront qu'à ce moment-là."""
    import csv
    import os
    from datetime import date
    chemin = os.path.join(dossier, "journal_experts.csv")
    jour = date.today().isoformat()
    deja = False
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            deja = any(l.startswith(jour + ",") for l in f.readlines()[-3000:])
    if deja:
        return 0
    lignes = []
    for t in payload.get("titres", []):
        fv = (t.get("fondamentaux") or {}).get("valeurs") or {}
        ex = t.get("experts") or {}
        lignes.append([jour, t["ticker"], t.get("prix"), fv.get("trailingPE"), fv.get("dividendYield"), fv.get("debtToEquity"),
                       fv.get("revenueGrowth"), t.get("tonalite"), t.get("proba_hausse"),
                       *[ex.get(k) for k in ("technique", "statistique", "sentiment", "economie", "maison")]])
    nouveau = not os.path.exists(chemin)
    os.makedirs(dossier, exist_ok=True)
    with open(chemin, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if nouveau:
            w.writerow(["date", "ticker", "prix", "per", "rendement_dividende", "dette_capitaux", "croissance_ca", "tonalite", "proba_ia",
                        "expert_technique", "expert_statistique", "expert_sentiment", "expert_economie", "expert_maison"])
        w.writerows(lignes)
    return len(lignes)
