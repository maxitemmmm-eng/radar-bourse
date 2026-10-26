"""Rendre l'IA plus juste et plus lisible (version 22).

1. RISQUE PRÉVU : en plus de la direction, une IA prévoit de combien le titre risque de bouger le mois
   prochain. C'est beaucoup plus prévisible que la direction (les périodes agitées durent) : on le mesure
   honnêtement sur des années jamais vues, face à la méthode naïve « ça bougera comme ces derniers jours ».
2. LES RAISONS DE CHAQUE AVIS : pour chaque titre, on retire tour à tour chaque famille d'indicateurs
   (on la remplace par sa valeur habituelle) et on regarde de combien l'avis des IA change. Les 3 familles
   qui pèsent le plus sont expliquées en mots simples. Ce sont les raisons du calcul, pas des certitudes.
3. SAVOIR DIRE « JE NE SAIS PAS » : on cherche à partir de quel écart à 50 % les avis des IA ont VRAIMENT été
   plus justes que le hasard sur des années jamais vues. En dessous, le site affiche « pas d'avis net ».
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

ANNEE = 252   # même convention que vol_20j (indicators.py)


# ----------------------------------------------------------------------------
# 1. Risque prévu
# ----------------------------------------------------------------------------
def vol_futur(close: pd.Series, horizon: int) -> pd.Series:
    """Volatilité réalisée (annualisée) sur les `horizon` prochaines séances, en logarithme."""
    r = np.log(close).diff()
    v = r.rolling(horizon).std().shift(-horizon) * np.sqrt(ANNEE)
    return np.log(v.where(v > 0))


def _variables_risque(jeu, variables_base):
    extra = ["vol_20j", "atr_pct", "bb_largeur", "marche_vol", "vix", "vix_structure", "drawdown",
             "marche_dispersion", "spread_credit", "conditions_fin", "est_crypto"]
    vs = [v for v in dict.fromkeys(list(variables_base) + extra) if v in jeu.columns]
    return [v for v in vs if jeu[v].nunique(dropna=True) > 1]


def _naif(df):
    return np.log(df["vol_20j"].clip(lower=1e-4))


class SansColonnesVides:
    """Enveloppe un modèle : écarte à l'apprentissage les colonnes vides ou constantes sur la période apprise
    (ex. un indicateur économique qui n'existait pas encore en 2014). Les versions récentes de scikit-learn
    plantent sinon (« window shape cannot be larger than input array shape »)."""

    def __init__(self, modele):
        self.modele, self.cols = modele, None

    def fit(self, X, y, **kw):
        self.cols = [c for c in X.columns if X[c].nunique(dropna=True) > 1]
        self.modele.fit(X[self.cols] if self.cols else X.iloc[:, :0].assign(_z=0.0), y, **kw)
        return self

    def predict(self, X):
        return self.modele.predict(X[self.cols] if self.cols else X.iloc[:, :0].assign(_z=0.0))

    def predict_proba(self, X):
        return self.modele.predict_proba(X[self.cols] if self.cols else X.iloc[:, :0].assign(_z=0.0))


def _modele():
    from sklearn.ensemble import HistGradientBoostingRegressor
    return SansColonnesVides(HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=300, min_samples_leaf=300,
                                                           l2_regularization=1.0, random_state=0))


def _concordance(df, col_p, col_y, pas=5):
    """Sur deux titres pris au hasard le même jour, combien de fois désigne-t-on le plus agité des deux ?"""
    from scipy.stats import kendalltau
    taus = []
    for k, (_, g) in enumerate(df.groupby(level=0)):
        if k % pas or len(g) < 8:
            continue
        t = kendalltau(g[col_p], g[col_y]).statistic
        if t == t:
            taus.append(t)
    return float((np.mean(taus) + 1) / 2) if taus else None


def evaluer_risque(jeu, horizon, variables_base, n_plis=5):
    """Prévisions du risque sur des périodes jamais vues, comparées à la méthode naïve."""
    from .model import _plis
    et = jeu.dropna(subset=["vol_futur", "vol_20j"])
    et = et[np.isfinite(et["vol_futur"])]
    vs = _variables_risque(et, variables_base)
    morceaux = []
    for train, test in _plis(et.assign(cible=0.0), horizon, n_plis):
        if len(train) < 3000 or test.empty:
            continue
        mod = _modele().fit(train[vs], train["vol_futur"])
        t = pd.DataFrame({"y": test["vol_futur"].to_numpy(), "p": mod.predict(test[vs]),
                          "naif": _naif(test).to_numpy()}, index=test.index)
        morceaux.append(t)
    if not morceaux:
        return {}
    o = pd.concat(morceaux)
    o = o[np.isfinite(o[["y", "p", "naif"]]).all(axis=1)]
    err_ia, err_naif = np.abs(o["p"] - o["y"]), np.abs(o["naif"] - o["y"])
    ss = float(((o["y"] - o["y"].mean()) ** 2).sum())
    r2 = lambda c: float(1 - ((o[c] - o["y"]) ** 2).sum() / ss) if ss else None
    # bootstrap par mois sur le gain d'erreur (l'IA doit battre la méthode naïve de façon prouvée)
    from .model import _ic, bootstrap_mois
    d = pd.DataFrame({"gain": (err_naif - err_ia).to_numpy()}, index=o.index)
    boot = bootstrap_mois(d, lambda x: np.array([x["gain"].mean()]), graine=11)
    ic = _ic(boot[:, 0]) if len(boot) else None
    return {"nb": int(len(o)), "periode": f"{o.index.min():%m/%Y} – {o.index.max():%m/%Y}",
            "erreur_ia": float(np.expm1(err_ia.median())), "erreur_naif": float(np.expm1(err_naif.median())),
            "r2_ia": r2("p"), "r2_naif": r2("naif"),
            "concordance_ia": _concordance(o, "p", "y"), "concordance_naif": _concordance(o, "naif", "y"),
            "ic_gain": ic, "prouve": bool(ic and ic[0] > 0), "variables": vs}


SEUIL_CHUTE = -0.10   # « forte chute » : perdre plus de 10 % en un mois


def _modele_chute():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return SansColonnesVides(HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=500,
                                                            random_state=0))


def evaluer_chute(jeu, horizon, variables_base, n_plis=5):
    """Version 33 : le risque de forte chute (plus de 10 % en un mois), testé sur des périodes jamais vues.
    Plus prévisible que le sens du prix, car lié à l'agitation (le point fort des IA). Utilisé seulement si prouvé."""
    from .model import _auc, _ic, _plis, bootstrap_mois
    et = jeu.dropna(subset=["rendement_futur"]).copy()
    et["cible"] = (et["rendement_futur"] < SEUIL_CHUTE).astype(float)
    vs = _variables_risque(et, variables_base)
    morceaux = []
    for train, test in _plis(et, horizon, n_plis):
        if len(train) < 5000 or test.empty or train["cible"].nunique() < 2:
            continue
        m = _modele_chute().fit(train[vs], train["cible"].to_numpy())
        morceaux.append(pd.DataFrame({"y": test["cible"].to_numpy(), "p": m.predict_proba(test[vs])[:, 1],
                                      "crypto": test["est_crypto"].to_numpy() if "est_crypto" in test else 0.0}, index=test.index))
    if not morceaux:
        return {}
    o = pd.concat(morceaux)
    boot = bootstrap_mois(o, lambda d: np.array([_auc(d["y"].to_numpy(), d["p"].to_numpy())]), graine=17)
    ic = _ic(boot[:, 0]) if len(boot) else None
    haut = o["p"] >= o["p"].quantile(0.9)
    return {"nb": int(len(o)), "auc": _auc(o["y"].to_numpy(), o["p"].to_numpy()), "ic_auc": ic,
            "base": float(o["y"].mean()), "base_actions": float(o.loc[o["crypto"] < 0.5, "y"].mean()) if (o["crypto"] < 0.5).any() else None,
            "base_cryptos": float(o.loc[o["crypto"] >= 0.5, "y"].mean()) if (o["crypto"] >= 0.5).any() else None,
            "taux_risque_haut": float(o.loc[haut, "y"].mean()), "seuil": SEUIL_CHUTE,
            "prouve": bool(ic and ic[0] > 0.55)}


def predire_chute(jeu, actuel, variables_base, mod=None):
    """{ticker: probabilité de perdre plus de 10 % dans le mois}, et le modèle (gardé pour les mises à jour horaires)."""
    if mod is None:
        et = jeu.dropna(subset=["rendement_futur"]).copy()
        et["cible"] = (et["rendement_futur"] < SEUIL_CHUTE).astype(float)
        vs = _variables_risque(et, variables_base)
        mod = (_modele_chute().fit(et[vs], et["cible"].to_numpy()), vs)
    m, vs = mod
    p = m.predict_proba(actuel[vs])[:, 1]
    return {t: float(v) for t, v in zip(actuel["ticker"], p) if np.isfinite(v)}, mod


def predire_risque(jeu, actuel, tous, horizon, variables_base, utiliser_ia=True, mod=None):
    """{ticker: {"vol": vol annualisée prévue, "mouvement": mouvement typique sur l'horizon,
    "habitude": rapport à son agitation habituelle, "source": "ia" ou "naif"}}"""
    if mod is not None and utiliser_ia:   # modèle du matin réutilisé (mises à jour horaires)
        modele, vs = mod
        lp, source = modele.predict(actuel[vs]), "ia"
    elif utiliser_ia and len(jeu) > 3000:
        et = jeu.dropna(subset=["vol_futur", "vol_20j"])
        et = et[np.isfinite(et["vol_futur"])]
        vs = _variables_risque(et, variables_base)
        modele = _modele().fit(et[vs], et["vol_futur"])
        mod = (modele, vs)
        lp, source = modele.predict(actuel[vs]), "ia"
    else:
        lp, source, mod = _naif(actuel).to_numpy(), "naif", None
    out = {}
    for t, l in zip(actuel["ticker"], lp):
        if not np.isfinite(l) or t not in tous:
            continue
        c = tous[t]["Close"]
        hist = (c.pct_change().rolling(horizon).std() * np.sqrt(ANNEE)).iloc[-504:].dropna()
        vol = float(np.exp(l))
        out[t] = {"vol": vol, "mouvement": float(vol / np.sqrt(ANNEE) * np.sqrt(horizon)),
                  "habitude": float(vol / hist.median()) if len(hist) > 60 and hist.median() > 0 else None,
                  "source": source}
    return out, mod


# ----------------------------------------------------------------------------
# 2. Les raisons de chaque avis
# ----------------------------------------------------------------------------
# (clé, nom, indicateurs, indicateur principal, sens « haut », sens « bas »)
FAMILLES = [
    ("court", "Les derniers jours", ["ret_5j", "roc_10", "rsi", "stoch_k", "mfi", "bb_position", "div_rsi"], "ret_5j",
     "le titre a bien monté ces derniers jours", "le titre a baissé ces derniers jours"),
    ("mois", "Le dernier mois", ["ret_21j", "macd_hist_norm", "dist_vwap20"], "ret_21j",
     "le dernier mois a été meilleur que d'habitude", "le dernier mois a été moins bon que d'habitude"),
    ("fond", "La tendance de fond", ["ret_63j", "ret_126j", "dist_sma50", "dist_sma200", "pente_sma50", "dist_ema50_200",
                                     "adx", "aroon", "donchian_pos", "supertrend", "ichimoku", "force_relative_63j"], "ret_126j",
     "la tendance des derniers mois est plus forte que d'habitude", "la tendance des derniers mois est plus faible que d'habitude"),
    ("agitation", "L'agitation du titre", ["vol_20j", "atr_pct", "bb_largeur"], "vol_20j",
     "le titre bouge plus que d'habitude", "le titre est plus calme que d'habitude"),
    ("sommet", "La distance au plus haut", ["drawdown", "dist_plus_haut"], "dist_plus_haut",
     "le titre est proche de son plus haut", "le titre est loin de son plus haut"),
    ("volumes", "Les volumes échangés", ["volume_ratio", "obv_pente", "cmf"], "volume_ratio",
     "il s'échange plus de titres que d'habitude", "il s'échange moins de titres que d'habitude"),
    ("marche", "L'état du marché", ["marche_tendance", "marche_vol", "marche_largeur", "marche_dispersion"], "marche_tendance",
     "le marché dans son ensemble va bien", "le marché dans son ensemble va mal"),
    ("peur", "La nervosité des investisseurs", ["vix", "vix_chg", "vix_structure", "fng"], "vix",
     "les investisseurs sont plus nerveux que d'habitude", "les investisseurs sont plus calmes que d'habitude"),
    ("economie", "Le contexte économique", ["taux_chg", "dollar_chg", "courbe_taux", "petrole_chg", "cuivre_chg",
                                            "spread_credit", "spread_credit_chg", "conditions_fin", "chomage_tendance"], None,
     "les taux, le dollar, le crédit, le pétrole…", "les taux, le dollar, le crédit, le pétrole…"),
]


def _groupes(colonnes):
    """Familles d'indicateurs présentes (les classements rang_X suivent leur indicateur X ;
    chaque règle du manuel de Bourse forme sa propre famille)."""
    from .connaissances import REGLES
    groupes = []
    for cle, nom, cols, principal, haut, bas in FAMILLES:
        g = [c for c in colonnes if c in cols or (c.startswith("rang_") and c[5:] in cols)]
        if g:
            groupes.append({"cle": cle, "nom": nom, "colonnes": g, "principal": principal, "haut": haut, "bas": bas})
    for r in REGLES:
        g = [c for c in colonnes if re.fullmatch(rf"(rang_)?cx_{re.escape(r['cle'])}_.+", c)]
        if g:
            groupes.append({"cle": "cx_" + r["cle"], "nom": r["nom"], "colonnes": g, "principal": None,
                            "haut": "", "bas": "", "idee": r.get("idee", "")})
    return groupes


def expliquer(predire, actuel, reference, garde, n=3, seuil=0.003):
    """predire(df) → probabilités finales. reference : valeurs habituelles (médiane historique) par colonne,
    séparément pour les actions (0) et les cryptos (1). Renvoie {ticker: [raisons]}."""
    base = predire(actuel)
    colonnes = [c for c in actuel.columns if c not in ("ticker", "est_crypto")]
    effets = {}
    crypto = actuel["est_crypto"].to_numpy() == 1 if "est_crypto" in actuel else np.zeros(len(actuel), bool)
    groupes = _groupes(colonnes)
    for g in groupes:
        x = actuel.copy()
        for c in g["colonnes"]:
            ref = np.where(crypto, reference[1].get(c, np.nan), reference[0].get(c, np.nan))
            x[c] = np.where(np.isnan(ref), x[c], ref) if not c.startswith("rang_") else 0.5
        effets[g["cle"]] = base - predire(x)
    out = {}
    tks = actuel["ticker"].to_numpy()
    for i, t in enumerate(tks):
        if not garde[i]:
            continue
        lst = sorted(((g, float(effets[g["cle"]][i])) for g in groupes), key=lambda z: -abs(z[1]))
        raisons = []
        for g, e in lst[:n]:
            if abs(e) < seuil:
                break
            etat = ""
            p = g["principal"]
            if p and p in actuel:
                v, r = actuel[p].iloc[i], (reference[1] if crypto[i] else reference[0]).get(p, np.nan)
                if v == v and r == r:
                    etat = g["haut"] if v > r else g["bas"]
            elif g["cle"] == "economie":
                etat = g["haut"]
            raisons.append({"famille": g["nom"], "etat": etat, "effet": round(e, 4),
                            "manuel": g["cle"].startswith("cx_"), "idee": g.get("idee", "")})
        out[t] = raisons
    return out


def references(etiquete, colonnes, annees=5):
    """Valeurs « habituelles » de chaque indicateur (médiane des dernières années), actions et cryptos à part."""
    recent = etiquete[etiquete.index >= etiquete.index.max() - pd.Timedelta(days=365 * annees)]
    cols = [c for c in colonnes if c in recent.columns]
    out = {}
    for g in (0, 1):
        sous = recent[recent["est_crypto"] == g] if "est_crypto" in recent else recent
        if len(sous) < 500:
            sous = recent
        out[g] = sous[cols].median(numeric_only=True).to_dict()
    return out


# ----------------------------------------------------------------------------
# 3. Savoir dire « je ne sais pas »
# ----------------------------------------------------------------------------
MARGES = (0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12)


def seuil_avis_net(oof):
    """oof : prévisions calibrées hors échantillon (colonnes cible, proba). On garde la plus petite marge
    autour de 50 % au-delà de laquelle les avis ont été plus justes que « toujours la même réponse »,
    de façon prouvée (marge d'erreur par mois), sur au moins 10 % des cas."""
    from .model import _ic, bootstrap_mois
    y, p = oof["cible"].to_numpy(), oof["proba"].to_numpy()
    ecart = np.abs(p - 0.5)
    for m in MARGES:
        sel = ecart >= m
        part = float(sel.mean())
        if part < 0.10 or sel.sum() < 500:
            break
        d = pd.DataFrame({"juste": ((p > 0.5) == (y == 1)).astype(float), "y": y}, index=oof.index)[sel]

        def gain(x):
            b = max(x["y"].mean(), 1 - x["y"].mean())
            return np.array([x["juste"].mean() - b])
        boot = bootstrap_mois(d, gain, graine=13)
        ic = _ic(boot[:, 0]) if len(boot) else None
        if ic and ic[0] > 0:
            reste = ~sel
            return {"marge": m, "part": part, "precision": float(d["juste"].mean()),
                    "base": float(max(d["y"].mean(), 1 - d["y"].mean())), "ic_gain": ic,
                    "precision_reste": float(((p[reste] > 0.5) == (y[reste] == 1)).mean()) if reste.any() else None}
    return {"marge": None}


# ----------------------------------------------------------------------------
# 4. Une seule échelle de confiance : faible / moyenne / forte, avec ce que chaque niveau a vraiment donné
# ----------------------------------------------------------------------------
def marge_forte(marge):
    return None if marge is None else max(2 * marge, marge + 0.03)


def niveau(p, accord, marge) -> str:
    if p is None or p != p or marge is None or abs(p - 0.5) < marge or accord is False:
        return "faible"
    return "forte" if abs(p - 0.5) >= marge_forte(marge) else "moyenne"


def niveaux_confiance(oof, marge):
    """Taux de bonnes directions mesuré pour chaque niveau, sur des années jamais vues."""
    y, p = oof["cible"].to_numpy(), oof["proba"].to_numpy()
    acc = oof["accord"].to_numpy() if "accord" in oof else np.ones(len(p), bool)
    niv = np.array([niveau(a, b, marge) for a, b in zip(p, acc)])
    juste = (p > 0.5) == (y == 1)
    from .model import wilson
    out = {}
    for n in ("faible", "moyenne", "forte"):
        m = niv == n
        if m.sum() >= 100:
            lo, hi = wilson(int(juste[m].sum()), int(m.sum()))
            out[n] = {"part": float(m.mean()), "precision": float(juste[m].mean()), "nb": int(m.sum()), "ic": [lo, hi]}
    return out


# ----------------------------------------------------------------------------
# 5. Jeu « Remonte le temps » : des moments du passé que l'IA n'avait jamais vus
# ----------------------------------------------------------------------------
def echantillon_jeu(oof, proba, donnees, horizon, n=300, avant=120):
    """Tire au hasard n moments passés (titre + date) parmi les prévisions faites sur des périodes
    JAMAIS vues par l'IA. Pour chacun : 120 séances avant, la suite à l'horizon, l'avis de l'IA et la vérité.
    Les prix sont ramenés à 100 à la date du jeu (on ne voit ni le nom ni le vrai prix avant la réponse)."""
    if "ticker" not in oof:
        return []
    d = pd.DataFrame({"ticker": oof["ticker"].to_numpy(), "p": np.asarray(proba), "y": oof["cible"].to_numpy(),
                      "r": oof["rendement_futur"].to_numpy()}, index=oof.index)
    d = d[d["ticker"].isin(list(donnees))]
    if d.empty:
        return []
    rng = np.random.default_rng()
    out, vus = [], set()
    for k in rng.permutation(len(d))[: n * 4]:
        ligne = d.iloc[int(k)]
        t, date = ligne["ticker"], d.index[int(k)]
        if (t, date.year, date.month) in vus:
            continue
        c = donnees[t]["Close"]
        try:
            pos = c.index.get_loc(date)
        except KeyError:
            continue
        if not isinstance(pos, (int, np.integer)) or pos < avant or pos + horizon >= len(c):
            continue
        serie = c.iloc[pos - avant: pos + horizon + 1].to_numpy() / float(c.iloc[pos]) * 100
        if not np.isfinite(serie).all():
            continue
        vus.add((t, date.year, date.month))
        out.append({"t": t, "d": f"{date:%Y-%m-%d}", "p": round(float(ligne["p"]), 3), "y": int(ligne["y"]),
                    "r": round(float(ligne["r"]), 4), "s": [round(float(v), 2) for v in serie], "a": avant})
        if len(out) >= n:
            break
    return out


# ----------------------------------------------------------------------------
# 6. « Je ne sais pas » par marché : si, sur un marché, même les avis nets n'ont pas fait mieux que
#    « toujours la même réponse », on ne donne pas d'avis de direction sur ce marché.
# ----------------------------------------------------------------------------
def prudence_par_marche(oof, gain_min=0.005, nb_min=300):
    """Version 33 (ton test sur 5000 cas : +60 bonnes réponses) : sur un marché où l'IA n'a PAS fait mieux que la
    tendance habituelle de ce marché (sur des années jamais vues), on publie cette tendance habituelle
    (la part des mois où ce marché a fini plus haut) au lieu de l'avis de l'IA. C'est affiché comme tel sur le site."""
    if "marche" not in oof:
        return {}
    y, p, m = oof["cible"].to_numpy(), oof["proba"].to_numpy(), oof["marche"].astype(str).to_numpy()
    out = {}
    for nom in sorted(set(m)):
        sel = m == nom
        if sel.sum() < nb_min:
            continue
        juste = float(((p[sel] >= 0.5) == (y[sel] == 1)).mean())
        taux = float(y[sel].mean())
        if juste <= max(taux, 1 - taux) + gain_min:
            out[nom] = {"precision_ia": juste, "taux_hausse": taux, "base": max(taux, 1 - taux), "nb": int(sel.sum())}
    return out


def marches_sans_avis(oof, marge, gain_min=0.005):
    if marge is None or "marche" not in oof:
        return {}
    y, p, m = oof["cible"].to_numpy(), oof["proba"].to_numpy(), oof["marche"].to_numpy()
    out = {}
    for nom in sorted(set(m)):
        sel = (m == nom) & (np.abs(p - 0.5) >= marge)
        if sel.sum() < 300:
            continue
        juste = float(((p[sel] > 0.5) == (y[sel] == 1)).mean())
        base = float(max(y[sel].mean(), 1 - y[sel].mean()))
        if juste - base < gain_min:
            out[str(nom)] = {"precision": juste, "base": base, "nb": int(sel.sum())}
    return out
