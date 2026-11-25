"""Version 106 : l'analyse approfondie à la demande (« re-scanner » un titre au maximum).

Lancée par GitHub Actions quand un visiteur la demande sur le site (rien ne tourne sur le PC de l'éditrice).
Tout est calculé sur les vrais cours du titre, et chaque chiffre « prédictif » est accompagné de son test honnête
sur le passé du même titre (walk-forward : on n'utilise jamais une donnée postérieure à la date de prévision).

Ce que l'analyse contient :
1. Situation : tendance de fond, élan, agitation actuelle par rapport à son habitude, recul depuis le plus haut.
2. Fourchettes à 1 semaine, 1 mois, 3 mois, calibrées sur le passé du titre, avec leur taux de réussite réel sur ce titre.
3. Scénarios à 1 et 3 mois par simulation (Monte-Carlo par blocs de vrais rendements) : forte baisse … forte hausse.
4. Direction à 1 mois : un modèle testé année par année contre la réponse naïve ; s'il ne la bat pas assez souvent, on le dit
   et on n'affiche pas de « sens ».
5. Risques : pires chutes de l'histoire du titre et temps de récupération, risque de chute de plus de 10 % en un mois.
6. Lien avec le marché (bêta, corrélation), saisonnalité, et chiffres de l'entreprise quand ils existent.

Usage : python -m bourse_bot.analyse_profonde --ticker MC.PA --id abc123 [--demo] [--sortie fichier.json] [--envoyer]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config, data

HORIZONS = {"semaine": 5, "mois": 21, "trimestre": 63}
SCENARIOS = [("Forte baisse", -1, -0.10), ("Baisse", -0.10, -0.03), ("Stable", -0.03, 0.03), ("Hausse", 0.03, 0.10), ("Forte hausse", 0.10, 9)]


def _r(x, n=4):
    return None if x is None or not np.isfinite(x) else round(float(x), n)


# --------------------------------------------------------------------------------------------------------------------
def situation(c: pd.Series) -> dict:
    r = np.log(c).diff().dropna()
    sma50, sma200 = c.rolling(50).mean(), c.rolling(200).mean()
    vol20 = r.tail(20).std() * math.sqrt(252)
    vol_hab = r.tail(756).std() * math.sqrt(252)
    vols = r.rolling(20).std().dropna() * math.sqrt(252)
    pct_vol = float((vols.tail(1260) < vol20).mean()) if len(vols) > 50 else None
    haut1a = c.tail(252).max()
    return {"prix": _r(c.iloc[-1], 6), "date": str(c.index[-1].date()),
            "au_dessus_200": bool(c.iloc[-1] > sma200.iloc[-1]) if len(c) > 200 else None,
            "sma50_sur_200": bool(sma50.iloc[-1] > sma200.iloc[-1]) if len(c) > 200 else None,
            "perf": {k: _r(c.iloc[-1] / c.iloc[-1 - n] - 1) if len(c) > n else None for k, n in (("1 semaine", 5), ("1 mois", 21), ("3 mois", 63), ("1 an", 252), ("5 ans", 1260))},
            "vol_actuelle": _r(vol20), "vol_habituelle": _r(vol_hab), "percentile_vol": _r(pct_vol, 3),
            "recul_plus_haut_1an": _r(c.iloc[-1] / haut1a - 1)}


def _ewma_vol(r: pd.Series, lam=0.94) -> pd.Series:
    return np.sqrt((r ** 2).ewm(alpha=1 - lam, adjust=False).mean())


def fourchettes(c: pd.Series) -> dict:
    """Fourchette 80 % (et 50 %) par horizon : rendements passés « normalisés » par l'agitation du moment (EWMA), quantiles
    appris sur le passé seulement ; puis taux de réussite réel de cette méthode sur ce titre (walk-forward)."""
    lr = np.log(c).diff().dropna()
    sig = _ewma_vol(lr).shift(1).dropna()
    out = {}
    for nom, h in HORIZONS.items():
        fut = np.log(c).shift(-h) - np.log(c)
        z = (fut / (sig * math.sqrt(h))).dropna()
        z = z[np.isfinite(z)]
        if len(z) < 300:
            continue
        # réussite walk-forward : toutes les 5 séances, quantiles appris sur ce qui précède (avec h séances d'écart)
        dedans, n = 0, 0
        idx = z.index
        for k in range(250, len(idx) - 1, 5):
            passe = z.iloc[: max(0, k - h)]
            if len(passe) < 250:
                continue
            q10, q90 = passe.quantile(0.10), passe.quantile(0.90)
            n += 1
            dedans += int(q10 <= z.iloc[k] <= q90)
        s_now = float(_ewma_vol(lr).iloc[-1]) * math.sqrt(h)
        qs = {p: float(z.quantile(p)) for p in (0.10, 0.25, 0.5, 0.75, 0.90)}
        p0 = float(c.iloc[-1])
        out[nom] = {"seances": h, "bas80": _r(p0 * math.exp(qs[0.10] * s_now), 6), "haut80": _r(p0 * math.exp(qs[0.90] * s_now), 6),
                    "bas50": _r(p0 * math.exp(qs[0.25] * s_now), 6), "haut50": _r(p0 * math.exp(qs[0.75] * s_now), 6),
                    "median": _r(p0 * math.exp(qs[0.5] * s_now), 6), "reussite_passee": _r(dedans / n, 3) if n else None, "tests": n}
    return out


def monte_carlo(c: pd.Series, n_chemins=3000, jours=63, bloc=10, graine=7) -> dict:
    """Simulation par blocs de 10 vrais jours consécutifs tirés des 5 dernières années, remis à l'échelle de l'agitation
    actuelle. Ce n'est pas une prévision : c'est l'éventail de ce qui arrive si le titre se comporte comme dans son passé."""
    lr = np.log(c).diff().dropna().tail(1260).values
    if len(lr) < 200:
        return {}
    ratio = float(_ewma_vol(pd.Series(lr)).iloc[-1] / (lr.std() or 1))
    ratio = min(max(ratio, 0.5), 2.5)
    lr = (lr - lr.mean()) * ratio + lr.mean()
    rng = np.random.default_rng(graine)
    nb = math.ceil(jours / bloc)
    debuts = rng.integers(0, len(lr) - bloc, size=(n_chemins, nb))
    chem = np.concatenate([np.stack([lr[s:s + bloc] for s in debuts[:, j]]) for j in range(nb)], axis=1)[:, :jours]
    cum = np.exp(np.cumsum(chem, axis=1))
    p0 = float(c.iloc[-1])
    pts = [5, 10, 21, 42, 63]
    eventail = {str(p): {q: _r(p0 * float(np.percentile(cum[:, p - 1], q)), 6) for q in (5, 25, 50, 75, 95)} for p in pts if p <= jours}
    scen = {}
    for h in (21, 63):
        if h > jours:
            continue
        rr = cum[:, h - 1] - 1
        scen[str(h)] = [{"nom": nom, "proba": _r(float(((rr > a) & (rr <= b)).mean()), 3)} for nom, a, b in SCENARIOS]
    return {"chemins": n_chemins, "eventail": eventail, "scenarios": scen, "chute10_mois": _r(float((cum[:, :21].min(axis=1) < 0.9).mean()), 3)}


def _features(c: pd.Series) -> pd.DataFrame:
    lr = np.log(c).diff()
    f = pd.DataFrame(index=c.index)
    for n in (5, 20, 60, 120):
        f[f"r{n}"] = np.log(c / c.shift(n))
    f["vol20"] = lr.rolling(20).std()
    f["vol_ratio"] = f["vol20"] / lr.rolling(120).std()
    f["d50"] = c / c.rolling(50).mean() - 1
    f["d200"] = c / c.rolling(200).mean() - 1
    gain, perte = lr.clip(lower=0).rolling(14).mean(), (-lr.clip(upper=0)).rolling(14).mean()
    f["rsi"] = 100 - 100 / (1 + gain / perte.replace(0, np.nan))
    f["dd"] = c / c.rolling(252, min_periods=60).max() - 1
    return f


def direction(c: pd.Series, h=21) -> dict:
    """Modèle simple et robuste (régression logistique) testé année par année sur des années jamais vues,
    avec 21 séances d'écart entre apprentissage et test, contre la réponse naïve (« comme d'habitude »)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    f = _features(c)
    y = (np.log(c.shift(-h) / c) > 0).astype(float).where(c.shift(-h).notna())
    d = f.join(y.rename("y")).replace([np.inf, -np.inf], np.nan).dropna()
    if len(d) < 800:
        return {"ok": False, "raison": "historique trop court pour un test honnête"}
    annees = sorted(set(d.index.year))[3:]
    res, toutes_p, toutes_y = [], [], []
    for a in annees:
        app = d[d.index < pd.Timestamp(f"{a}-01-01") - pd.Timedelta(days=35)]
        test = d[d.index.year == a]
        if len(app) < 500 or len(test) < 60:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=500))
        m.fit(app.drop(columns="y"), app["y"])
        p = m.predict_proba(test.drop(columns="y"))[:, 1]
        base = float(app["y"].mean())
        juste = float(((p >= 0.5) == (test["y"] == 1)).mean())
        naif = float(((base >= 0.5) == (test["y"] == 1)).mean())
        res.append({"annee": int(a), "ia": _r(juste, 3), "naif": _r(naif, 3), "n": int(len(test))})
        toutes_p += list(p); toutes_y += list(test["y"])
    if not res:
        return {"ok": False, "raison": "pas assez d'années testables"}
    gagnees = sum(1 for x in res if x["ia"] > x["naif"])
    tp, ty = np.array(toutes_p), np.array(toutes_y)
    brier = float(((tp - ty) ** 2).mean())
    brier_naif = float(((ty.mean() - ty) ** 2).mean())
    m = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=500))
    m.fit(d.drop(columns="y"), d["y"])
    p_now = float(m.predict_proba(f.replace([np.inf, -np.inf], np.nan).dropna().tail(1))[:, 1][0])
    fiable = gagnees >= math.ceil(0.7 * len(res)) and brier < brier_naif
    return {"ok": True, "annees": res, "gagnees": gagnees, "testees": len(res), "brier": _r(brier), "brier_naif": _r(brier_naif),
            "proba_hausse": _r(p_now, 3), "fiable": bool(fiable),
            "verdict": ("Sur ce titre, le modèle a fait mieux que la réponse naïve " f"{gagnees} années sur {len(res)} : son avis peut compter un peu."
                        if fiable else f"Sur ce titre, le modèle n'a battu la réponse naïve que {gagnees} années sur {len(res)} : son avis sur le sens "
                        "n'est pas fiable, on ne l'affiche pas comme un signal.")}


def risques(c: pd.Series) -> dict:
    """Les 3 pires chutes (du plus haut au plus bas) et le temps pour revenir au plus haut."""
    pic, out, i = c.cummax(), [], 0
    dd = c / pic - 1
    vus = set()
    for _ in range(3):
        dd2 = dd[[d not in vus for d in dd.index]]
        if dd2.empty or dd2.min() > -0.05:
            break
        bas = dd2.idxmin()
        haut = c[:bas].idxmax()
        apres = c[bas:]
        rec = apres[apres >= c[haut]]
        fin = rec.index[0] if len(rec) else None
        out.append({"debut": str(haut.date()), "creux": str(bas.date()), "chute": _r(float(dd[bas])),
                    "recupere": str(fin.date()) if fin is not None else None,
                    "jours_recuperation": int((fin - bas).days) if fin is not None else None})
        for d in c[haut:(fin or c.index[-1])].index:
            vus.add(d)
    m21 = (c.rolling(21).min().shift(-20) / c - 1).dropna()
    return {"pires_chutes": out, "chute10_mois_historique": _r(float((m21 < -0.10).mean()), 3)}


def marche(c: pd.Series, ref: pd.Series, nom_ref: str) -> dict:
    j = pd.concat([np.log(c).diff(), np.log(ref).diff()], axis=1, join="inner").dropna().tail(756)
    if len(j) < 120:
        return {}
    cov = np.cov(j.iloc[:, 0], j.iloc[:, 1])
    return {"reference": nom_ref, "beta": _r(cov[0, 1] / cov[1, 1], 2), "correlation": _r(float(j.corr().iloc[0, 1]), 2)}


def saisonnalite(c: pd.Series) -> dict:
    m = c.resample("ME").last().pct_change().dropna()
    if len(m) < 36:
        return {}
    g = m.groupby(m.index.month)
    mois_suivant = (datetime.now().month % 12) + 1
    return {"par_mois": {int(k): {"moyenne": _r(float(v.mean())), "hausse": _r(float((v > 0).mean()), 2), "annees": int(len(v))} for k, v in g},
            "mois_prochain": mois_suivant}


def _px(v):
    if v is None:
        return "–"
    txt = f"{v:,.2f}" if abs(v) >= 1 else f"{v:.6g}"
    return txt.replace(",", "\u202f").replace(".", ",")


def synthese(t, S, F, MC, D, R, M) -> list:
    """Le résumé en phrases, uniquement à partir des chiffres calculés."""
    out = []
    tend = "haussière" if S.get("au_dessus_200") else "baissière" if S.get("au_dessus_200") is False else "indéterminée"
    out.append(f"Tendance de fond {tend}. Agitation actuelle {('élevée' if (S.get('percentile_vol') or 0) > .7 else 'faible' if (S.get('percentile_vol') or 1) < .3 else 'normale')} "
               f"pour ce titre ({round((S.get('vol_actuelle') or 0) * 100)} % par an, habituellement {round((S.get('vol_habituelle') or 0) * 100)} %).")
    fm = F.get("mois")
    if fm:
        out.append(f"Dans un mois, fourchette probable : {_px(fm['bas80'])} à {_px(fm['haut80'])}"
                   + (f" ; sur ce titre, cette méthode a vu juste {round(fm['reussite_passee'] * 100)} fois sur 100 dans le passé." if fm.get("reussite_passee") else "."))
    sc = (MC.get("scenarios") or {}).get("21")
    if sc:
        top = max(sc, key=lambda x: x["proba"] or 0)
        out.append(f"Scénario le plus fréquent dans les simulations à un mois : « {top['nom']} » ({round(top['proba'] * 100)} %).")
    if D.get("ok"):
        out.append(D["verdict"] + (f" Il donne aujourd'hui {round(D['proba_hausse'] * 100)} chances sur 100 de hausse à un mois." if D.get("fiable") else ""))
    if R.get("pires_chutes"):
        p = R["pires_chutes"][0]
        out.append(f"Pire chute de l'historique : {round(p['chute'] * 100)} % (du {p['debut']} au {p['creux']})"
                   + (f", rattrapée en {p['jours_recuperation']} jours." if p.get("jours_recuperation") else ", pas encore rattrapée."))
    if M.get("beta") is not None:
        out.append(f"Lien avec {M['reference']} : bêta {str(M['beta']).replace('.', ',')} (quand le marché bouge de 1 %, ce titre bouge en moyenne de {str(M['beta']).replace('.', ',')} %).")
    return out


def analyser(ticker: str) -> dict:
    t0 = time.time()
    df = data.telecharger(ticker)
    if df is None or df.empty or len(df) < 260:
        return {"ok": False, "ticker": ticker, "erreur": "Cours introuvables ou historique trop court pour ce symbole."}
    c = df["Close"].astype(float).dropna()
    c = c[c > 0]
    ref_tk = config.benchmark_de(ticker)
    ref = data.telecharger(ref_tk) if ref_tk and ref_tk != ticker else pd.DataFrame()
    S, F, MC = situation(c), fourchettes(c), monte_carlo(c)
    D, R = direction(c), risques(c)
    M = marche(c, ref["Close"].astype(float), config.NOM_BENCHMARK.get(ref_tk, ref_tk)) if not ref.empty else {}
    Z = saisonnalite(c)
    fond = None
    try:
        from . import fondamentaux
        fond = fondamentaux.recuperer(ticker, "")
    except Exception:
        fond = None
    nom = next((u[ticker] for u in config.UNIVERS.values() if ticker in u), None)
    return {"ok": True, "ticker": ticker, "nom": nom or ticker, "devise": data.devise(ticker), "genere_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": data.SOURCES_UTILISEES.get(ticker, "Yahoo Finance"), "seances": int(len(c)), "debut": str(c.index[0].date()),
            "situation": S, "fourchettes": F, "monte_carlo": MC, "direction": D, "risques": R, "marche": M, "saisonnalite": Z,
            "fondamentaux": fond, "synthese": synthese(ticker, S, F, MC, D, R, M), "duree_s": round(time.time() - t0, 1),
            "serie": {"t": [str(d.date()) for d in c.index[-504:]], "c": [_r(v, 6) for v in c.values[-504:]]},
            "avertissement": "Analyse statistique automatique et éducative, pas un conseil en investissement."}


def envoyer(resultat: dict, ident: str) -> None:
    api, secret = os.environ.get("RADAR_PLUS_API", "").rstrip("/"), os.environ.get("DEPOT_SECRET", "")
    if not api or not secret:
        print("RADAR_PLUS_API ou DEPOT_SECRET manquant : résultat non envoyé")
        return
    corps = json.dumps({"id": ident, "resultat": resultat}, allow_nan=False).encode()
    req = urllib.request.Request(api + "/depot", data=corps, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + secret})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("Résultat envoyé :", r.status)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--id", default="local")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--sortie")
    ap.add_argument("--envoyer", action="store_true")
    a = ap.parse_args(argv)
    tk = a.ticker.strip().upper()
    if not all(ch.isalnum() or ch in ".-^=" for ch in tk) or not 1 <= len(tk) <= 20:
        print("Symbole refusé"); sys.exit(2)
    data.DEMO = a.demo
    try:
        res = analyser(tk)
    except Exception as e:   # le visiteur reçoit un message clair plutôt qu'une attente sans fin
        res = {"ok": False, "ticker": tk, "erreur": f"L'analyse a échoué ({type(e).__name__})."}
    if a.sortie:
        with open(a.sortie, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, allow_nan=False)
    if a.envoyer:
        envoyer(res, a.id)
    print(json.dumps({k: res.get(k) for k in ("ok", "ticker", "duree_s", "erreur")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
