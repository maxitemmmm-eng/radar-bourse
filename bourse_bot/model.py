"""Les deux IA du radar : probabilité que le cours soit plus haut dans N séances.

Principes (tous vérifiés à chaque calcul du soir, sur des périodes que les IA n'ont jamais vues) :
- IA n°1 : gradient boosting + régression logistique (repère les combinaisons d'indicateurs) ;
- IA n°2 : forêt d'arbres aléatoires (méthode différente, qui se trompe sur d'autres cas) ;
- la probabilité publiée combine les deux ; on affiche aussi si elles sont d'accord. Un signal
  fort exige leur accord : quand elles divergent, le radar le dit au lieu de trancher ;
- « champion / challenger » : la façon de prévoir n'est remplacée que si la nouvelle fait mieux
  de façon statistiquement prouvée (bootstrap par mois, 95 %), jamais sur un coup de chance ;
- statistiques honnêtes : intervalles de confiance calculés en tirant des mois entiers au hasard
  (les jours d'un même mois se ressemblent, compter chaque ligne comme indépendante exagérerait la
  précision), score de Brier, calibration de Platt ;
- contrôles de cohérence avant chaque publication : si un contrôle critique échoue, rien n'est publié
  et l'ancienne version reste en ligne ;
- fourchettes de prix apprises (quantiles 5, 10, 50, 90 et 95 %) puis corrigées pour tenir leurs
  promesses (correction conformale), et un modèle « mieux que son marché ».
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import config
from .indicators import FEATURES

COLS_RANG = ["ret_21j", "ret_63j", "ret_126j", "vol_20j", "force_relative_63j", "dist_plus_haut"]
VARIABLES = FEATURES + ["est_crypto"] + [f"rang_{c}" for c in COLS_RANG]
TRANCHES = [0.0, 0.40, 0.45, 0.50, 0.55, 0.60, 1.0]
NOMS_TRANCHES = ["< 40 %", "40–45 %", "45–50 %", "50–55 %", "55–60 %", "> 60 %"]
SEUIL_FORT = 0.55  # probabilité calibrée minimale pour un « signal fort »
N_BOOT = 200       # tirages du bootstrap


class ErreurControle(RuntimeError):
    """Un contrôle de cohérence critique a échoué : on ne publie pas."""


def technique_haussiere(df: pd.DataFrame) -> pd.Series:
    """Tendance technique haussière nette : au-dessus de la moyenne 200 j, moyenne 50 j > 200 j,
    MACD positif et RSI pas en surchauffe. Fonctionne sur les colonnes d'indicateurs."""
    sma50_sur_200 = (1 + df["dist_sma200"]) / (1 + df["dist_sma50"])
    return ((df["dist_sma200"] > 0) & (sma50_sur_200 > 1) & (df["macd_hist_norm"] > 0)
            & (df["rsi"] < 75)).fillna(False)


class CalibrationPlatt:
    """Régression logistique sur le logit de la probabilité brute (courbe lisse et croissante)."""

    def __init__(self):
        self.lr = LogisticRegression(C=1.0)

    @staticmethod
    def _logit(p):
        p = np.clip(np.asarray(p, dtype=float), 1e-4, 1 - 1e-4)
        return np.log(p / (1 - p)).reshape(-1, 1)

    def fit(self, p, y):
        self.lr.fit(self._logit(p), np.asarray(y))
        return self

    def predict(self, p):
        return np.clip(self.lr.predict_proba(self._logit(p))[:, 1], 0.03, 0.97)

    def vers_dict(self):
        return {"coef": float(self.lr.coef_[0][0]), "intercept": float(self.lr.intercept_[0])}

    @classmethod
    def depuis_dict(cls, d):
        if not d:
            return None
        c = cls()
        c.lr.classes_ = np.array([0.0, 1.0])
        c.lr.coef_ = np.array([[d["coef"]]])
        c.lr.intercept_ = np.array([d["intercept"]])
        c.lr.n_features_in_ = 1
        return c


PARAMS_DEFAUT = {"profondeur": 3, "apprentissage": 0.04, "iterations": 250, "feuille": 300}


class Ensemble:
    """IA n°1 : moyenne de deux modèles qui se trompent de façons différentes."""

    def __init__(self, params=None):
        P = {**PARAMS_DEFAUT, **(params or {})}
        self.gbm = HistGradientBoostingClassifier(max_depth=int(P["profondeur"]), learning_rate=float(P["apprentissage"]),
                                                  max_iter=int(P["iterations"]), min_samples_leaf=int(P["feuille"]),
                                                  l2_regularization=2.0, random_state=0)
        self.lin = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                 LogisticRegression(C=0.05, max_iter=500))

    def fit(self, X, y):
        self.gbm.fit(X, y)
        self.lin.fit(X, y)
        return self

    def predict_proba(self, X):
        return 0.5 * self.gbm.predict_proba(X)[:, 1] + 0.5 * self.lin.predict_proba(X)[:, 1]


class Foret:
    """IA n°2 : forêt d'arbres très aléatoires. Elle découpe les données autrement que l'IA n°1,
    donc ses erreurs sont en partie différentes : leur accord a plus de valeur que chacune seule."""

    def __init__(self, params=None):
        P = params or {}
        self.m = make_pipeline(SimpleImputer(strategy="median"),
                               ExtraTreesClassifier(n_estimators=120, min_samples_leaf=int(P.get("feuille_foret", 400)), max_features=0.4,
                                                    n_jobs=-1, random_state=1))

    def fit(self, X, y):
        self.m.fit(X, y)
        return self

    def predict_proba(self, X):
        return self.m.predict_proba(X)[:, 1]


ALGOS = {"ia1": Ensemble, "ia2": Foret}


# ----------------------------------------------------------------------------
# Statistiques robustes
# ----------------------------------------------------------------------------
def wilson(k: float, n: float, z: float = 1.96):
    """Intervalle de confiance à 95 % d'une proportion (méthode de Wilson)."""
    if n <= 0:
        return None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    marge = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(max(0.0, centre - marge)), float(min(1.0, centre + marge))


def _groupes_mois(index) -> list:
    mois = pd.Index(pd.to_datetime(index)).to_period("M")
    codes, _ = pd.factorize(mois)
    return [np.flatnonzero(codes == c) for c in range(codes.max() + 1)]


def bootstrap_mois(df: pd.DataFrame, stat, n: int = N_BOOT, graine: int = 0) -> np.ndarray:
    """Recalcule `stat` sur des échantillons formés en tirant des MOIS entiers avec remise.
    Les journées d'un même mois étant liées, c'est la seule façon honnête d'obtenir une marge
    d'erreur réaliste (sinon on se croit bien plus précis qu'on ne l'est)."""
    groupes = _groupes_mois(df.index)
    if len(groupes) < 6:
        return np.array([])
    rng = np.random.default_rng(graine)
    out = []
    for _ in range(n):
        choix = rng.integers(0, len(groupes), len(groupes))
        idx = np.concatenate([groupes[i] for i in choix])
        try:
            v = stat(df.iloc[idx])
        except ValueError:
            continue
        if v is not None and np.all(np.isfinite(v)):
            out.append(v)
    return np.array(out)


def _ic(valeurs):
    if valeurs is None or len(valeurs) < 20:
        return None
    return [float(np.percentile(valeurs, 2.5)), float(np.percentile(valeurs, 97.5))]


def _precision(y, p):
    return float(((p > 0.5) == (y == 1)).mean())


def _auc(y, p):
    return float(roc_auc_score(y, p)) if len(set(np.asarray(y).tolist())) > 1 else float("nan")


# ----------------------------------------------------------------------------
@dataclass
class Evaluation:
    precision: float
    precision_base: float
    auc: float
    nb_tests: int
    calibration: list = field(default_factory=list)
    signaux_forts: dict = field(default_factory=dict)
    top_confiance: dict = field(default_factory=dict)
    fourchette: dict = field(default_factory=dict)
    quantiles: dict = field(default_factory=dict)      # {ticker: (bas 10 %, central, haut 90 %)} log-rendements
    configuration: str = ""
    comparaison: list = field(default_factory=list)
    par_marche: dict = field(default_factory=dict)
    periode: str = ""
    relatif: dict = field(default_factory=dict)
    proba_marche: dict = field(default_factory=dict)
    ic: dict = field(default_factory=dict)             # intervalles de confiance à 95 %
    brier: dict = field(default_factory=dict)
    ia: dict = field(default_factory=dict)             # fiabilité de chaque IA et de leur combinaison
    accord: dict = field(default_factory=dict)         # que valent les cas où les deux IA sont d'accord ?
    champion: dict = field(default_factory=dict)       # décision champion / challenger
    controles: list = field(default_factory=list)      # contrôles de cohérence de ce calcul
    date_evaluation: str = ""
    # par titre (non publiés tels quels dans l'évaluation)
    proba_ia1: dict = field(default_factory=dict)
    proba_ia2: dict = field(default_factory=dict)
    accord_titres: dict = field(default_factory=dict)
    extremes: dict = field(default_factory=dict)       # {ticker: (bas 5 %, haut 95 %)} log-rendements

    @property
    def avantage(self) -> float:
        return self.precision - self.precision_base

    def niveau_preuve(self) -> str:
        """« prouve » : avantage confirmé à 95 % ; « possible » : chiffre positif mais pas prouvé ; « aucun »."""
        ic_av, ic_auc = (self.ic or {}).get("avantage"), (self.ic or {}).get("auc")
        if ic_auc and ic_auc[0] > 0.5 and ic_av and ic_av[0] > 0:
            return "prouve"
        if not np.isnan(self.auc) and self.auc > 0.51 and self.avantage > 0:
            return "possible"
        return "aucun"

    def verdict(self) -> str:
        n = self.niveau_preuve()
        if n == "prouve":
            return ("Avantage sur le hasard confirmé statistiquement (à 95 %) sur l'historique, mais faible : "
                    "le radar trie un peu mieux que le hasard, il ne devine pas l'avenir.")
        if n == "possible":
            return ("Léger avantage possible, mais pas prouvé : la marge d'erreur inclut le hasard. "
                    "Les probabilités sont indicatives.")
        return "Pas d'avantage mesurable sur le hasard : les probabilités sont indicatives seulement."

    def rendement_attendu(self, proba: float) -> float:
        for t in self.calibration:
            if t["min"] <= proba < t["max"] and t["nb"] >= 30:
                return t["rendement_moyen"]
        return 0.0

    def to_dict(self) -> dict:
        return {"precision": self.precision, "precision_base": self.precision_base, "auc": self.auc,
                "nb_tests": self.nb_tests, "calibration": self.calibration,
                "par_marche": self.par_marche, "periode": self.periode, "verdict": self.verdict(),
                "niveau_preuve": self.niveau_preuve(),
                "signaux_forts": self.signaux_forts, "top_confiance": self.top_confiance,
                "seuil_fort": SEUIL_FORT, "configuration": self.configuration,
                "comparaison": self.comparaison, "fourchette": self.fourchette,
                "relatif": self.relatif, "ic": self.ic, "brier": self.brier, "ia": self.ia,
                "accord": self.accord, "champion": self.champion, "controles": self.controles,
                "date_evaluation": self.date_evaluation, "horizon": config.HORIZON_PREDICTION}


CHAMPS_CACHE = ("precision", "precision_base", "auc", "nb_tests", "calibration", "signaux_forts", "top_confiance",
                "fourchette", "configuration", "comparaison", "par_marche", "periode", "relatif", "ic", "brier",
                "ia", "accord", "champion", "date_evaluation")


def _ajouter_rangs(jeu: pd.DataFrame) -> pd.DataFrame:
    for c in COLS_RANG:
        jeu[f"rang_{c}"] = jeu.groupby(level=0)[c].rank(pct=True)
    return jeu


def construire_jeu(donnees: dict[str, pd.DataFrame], marches: dict[str, str], horizon: int) -> pd.DataFrame:
    morceaux = []
    futurs = {t: d["Close"].shift(-horizon) / d["Close"] - 1 for t, d in donnees.items()}
    for ticker, d in donnees.items():
        m = d[FEATURES].copy()
        m["est_crypto"] = float(marches.get(ticker) == "crypto")
        futur = futurs[ticker]
        m["rendement_futur"] = futur
        m["cible"] = np.where(futur.isna(), np.nan, (futur > 0).astype(float))
        ref = config.benchmark_de(ticker, marches.get(ticker, ""))
        if ref != ticker and ref in futurs:
            ecart = futur - futurs[ref].reindex(futur.index)
            m["cible_rel"] = np.where(ecart.isna(), np.nan, (ecart > 0).astype(float))
        else:
            m["cible_rel"] = np.nan
        m["ticker"] = ticker
        m["marche"] = marches.get(ticker, "?")
        morceaux.append(m.iloc[252:])
    jeu = pd.concat(morceaux).sort_index()
    return _ajouter_rangs(jeu)


VARIABLES_BASE = FEATURES[:21] + ["est_crypto"] + [f"rang_{c}" for c in COLS_RANG]
CONFIGS = [   # (nom, variables, un modèle par marché ?, réglages)
    ("Un seul modèle, tous les indicateurs", VARIABLES, False, {}),
    ("Un seul modèle, indicateurs de base", VARIABLES_BASE, False, {}),
    ("Un modèle par marché (actions / cryptos)", VARIABLES, True, {}),
]
NOM_RECETTE = "Recette de l'entraînement approfondi"


def recette_vers_config(r: dict):
    """Recette trouvée par entrainement_ia.py (enregistrée dans historique/modele.json)."""
    variables = [v for v in r.get("variables", []) if v in VARIABLES] or VARIABLES
    return (NOM_RECETTE, variables, bool(r.get("par_marche")), dict(r.get("params") or {}))


def configs_disponibles() -> list:
    """Les façons de prévoir testées chaque soir, plus la recette de l'entraînement approfondi s'il y en a une."""
    out = list(CONFIGS)
    m = _lire_fichier_modele() or {}
    if m.get("recette"):
        try:
            out.append(recette_vers_config(m["recette"]))
        except Exception:
            pass
    return out


class Predicteur:
    """Une IA entraînée soit sur tout le marché, soit séparément pour les actions et les cryptos."""

    def __init__(self, variables, par_marche=False, algo="ia1", params=None):
        self.variables, self.par_marche, self.algo, self.params = variables, par_marche, algo, params or {}
        self.commun, self.groupes = None, {}

    @staticmethod
    def _utiles(df, variables):
        """Retire les colonnes vides ou constantes (ex : sentiment crypto pour les actions)."""
        return [v for v in variables if df[v].nunique(dropna=True) > 1]

    def fit(self, df):
        self.vars_commun = self._utiles(df, self.variables)
        self.commun = ALGOS[self.algo](self.params).fit(df[self.vars_commun], df["cible"])
        if self.par_marche:
            for g, sous in df.groupby("est_crypto"):
                if len(sous) >= 3000 and sous["cible"].nunique() == 2:
                    vs = self._utiles(sous, self.variables)
                    self.groupes[g] = (vs, ALGOS[self.algo](self.params).fit(sous[vs], sous["cible"]))
        return self

    def predict_proba(self, df):
        p = self.commun.predict_proba(df[self.vars_commun])
        if self.groupes:
            g = df["est_crypto"].to_numpy()
            for cle, (vs, mod) in self.groupes.items():
                masque = g == cle
                if masque.any():
                    p[masque] = mod.predict_proba(df[vs][masque])
        return p


def _plis(etiquete, horizon, n_plis):
    dates = np.array(sorted(etiquete.index.unique()))
    bornes = np.linspace(len(dates) * 0.4, len(dates), n_plis + 1).astype(int)
    for i in range(n_plis):
        debut, fin = dates[bornes[i]], dates[bornes[i + 1] - 1]
        fin_train = dates[max(bornes[i] - horizon - 2, 0)]  # purge anti-fuite du futur
        yield etiquete[etiquete.index <= fin_train], etiquete[(etiquete.index >= debut) & (etiquete.index <= fin)]


def predictions_hors_echantillon(jeu, horizon, variables, par_marche, n_plis=6, algos=("ia1",), params=None,
                                 garder_ticker=False):
    """Prévisions « walk-forward » : chaque période n'est prédite que par des IA entraînées avant elle."""
    etiquete = jeu.dropna(subset=["cible"])
    morceaux = []
    for train, test in _plis(etiquete, horizon, n_plis):
        if len(train) < 2000 or test.empty or train["cible"].nunique() < 2:
            continue
        t = test[["cible", "rendement_futur", "marche"] + (["ticker"] if garder_ticker else [])].copy()
        t["technique"] = technique_haussiere(test).to_numpy()
        for algo in algos:
            t[f"proba_{algo}"] = Predicteur(variables, par_marche, algo, params).fit(train).predict_proba(test)
        t["proba"] = t[f"proba_{algos[0]}"]
        morceaux.append(t)
    return pd.concat(morceaux) if morceaux else None


def _evaluation(oof):
    """Calibre les prévisions hors échantillon et calcule toutes les mesures de fiabilité,
    avec leurs marges d'erreur."""
    oof = oof.copy()
    calibreur = None
    if len(oof) >= 2000:
        calibreur = CalibrationPlatt().fit(oof["proba"], oof["cible"])
        oof["proba"] = calibreur.predict(oof["proba"])
    y, p = oof["cible"].to_numpy(), oof["proba"].to_numpy()

    calibration = []
    for (a, b), nom in zip(zip(TRANCHES[:-1], TRANCHES[1:]), NOMS_TRANCHES):
        sel = oof[(oof["proba"] >= a) & (oof["proba"] < b)]
        lo, hi = wilson(sel["cible"].sum(), len(sel)) if len(sel) else (None, None)
        calibration.append({"tranche": nom, "min": a, "max": b, "nb": int(len(sel)),
                            "taux_hausse": float(sel["cible"].mean()) if len(sel) else None,
                            "ic": [lo, hi] if lo is not None else None,
                            "rendement_moyen": float(sel["rendement_futur"].median()) if len(sel) else 0.0})
    par_marche = {}
    for m, g in oof.groupby("marche"):
        par_marche[m] = {"precision": _precision(g["cible"].to_numpy(), g["proba"].to_numpy()),
                         "base": float(max(g["cible"].mean(), 1 - g["cible"].mean())), "nb": int(len(g))}
    periode = f"{oof.index.min():%m/%Y} – {oof.index.max():%m/%Y}"

    # marges d'erreur : bootstrap par mois
    def stats(d):
        yy, pp = d["cible"].to_numpy(), d["proba"].to_numpy()
        base = max(yy.mean(), 1 - yy.mean())
        return np.array([_precision(yy, pp), _auc(yy, pp), _precision(yy, pp) - base])
    boot = bootstrap_mois(oof, stats)
    ic = {}
    if len(boot):
        ic = {"precision": _ic(boot[:, 0]), "auc": _ic(boot[:, 1]), "avantage": _ic(boot[:, 2]),
              "p_hasard": float((boot[:, 1] <= 0.5).mean()), "nb_mois": len(_groupes_mois(oof.index))}

    base_h = float(y.mean())
    brier = float(np.mean((p - y) ** 2))
    ref = base_h * (1 - base_h)
    brier_d = {"brier": brier, "reference": ref, "progres": float(1 - brier / ref) if ref else None}

    def resume(sel):
        if len(sel) < 30:
            return {"nb": int(len(sel)), "precision": None, "rendement_median": None}
        b = bootstrap_mois(sel, lambda d: np.array([d["cible"].mean()]), graine=1)
        return {"nb": int(len(sel)), "precision": float(sel["cible"].mean()),
                "ic": _ic(b[:, 0]) if len(b) else None,
                "rendement_median": float(sel["rendement_futur"].median()), "part": float(len(sel) / len(oof))}
    masque_fort = (oof["proba"] >= SEUIL_FORT) & oof["technique"]
    if "accord" in oof:
        masque_fort &= oof["accord"]
    forts = resume(oof[masque_fort])
    forts["base"] = base_h
    top = resume(oof[oof["proba"] >= oof["proba"].quantile(0.9)])
    ev = Evaluation(precision=_precision(y, p), precision_base=float(max(base_h, 1 - base_h)), auc=_auc(y, p),
                    nb_tests=len(y), calibration=calibration, par_marche=par_marche, periode=periode,
                    signaux_forts=forts, top_confiance=top, ic=ic, brier=brier_d)
    return ev, calibreur


# ----------------------------------------------------------------------------
# Fourchettes de prix : quantiles appris puis corrigés (méthode conformale)
# ----------------------------------------------------------------------------
NIVEAUX = (0.05, 0.1, 0.5, 0.9, 0.95)
CIBLE_COUVERTURE = 0.80
CIBLE_EXTREME = 0.90


def _modeles_quantiles(train, variables):
    vs = Predicteur._utiles(train, variables)
    y = np.log1p(train["rendement_futur"].clip(lower=-0.95))
    mods = {q: HistGradientBoostingRegressor(loss="quantile", quantile=q, max_depth=3, learning_rate=0.05,
                                             max_iter=200, min_samples_leaf=300, random_state=0).fit(train[vs], y)
            for q in NIVEAUX}
    return vs, mods


def _predire_quantiles(vs, mods, df):
    Q = np.column_stack([mods[q].predict(df[vs]) for q in NIVEAUX])
    Q.sort(axis=1)  # garantit bas ≤ central ≤ haut
    return Q        # colonnes : q05, q10, q50, q90, q95


def _ajustement_conformal(bas, haut, y, cible):
    """Élargissement minimal pour atteindre la couverture visée (méthode CQR)."""
    e = np.maximum(bas - y, y - haut)
    niveau = min(1.0, cible * (1 + 1 / len(e)))
    return float(np.quantile(e, niveau))


def fiabilite_fourchettes(jeu, horizon, variables, n_plis=6):
    """Mesure honnête : correction apprise sur la première moitié des périodes de test, couverture
    mesurée sur la seconde moitié, jamais vue par la correction."""
    etiquete = jeu.dropna(subset=["cible"])
    morceaux = []
    for train, test in _plis(etiquete, horizon, n_plis):
        if len(train) < 2000 or test.empty:
            continue
        vs, mods = _modeles_quantiles(train, variables)
        Q = _predire_quantiles(vs, mods, test)
        morceaux.append(pd.DataFrame(Q, columns=["q05", "q10", "q50", "q90", "q95"], index=test.index)
                        .assign(y=np.log1p(test["rendement_futur"].clip(lower=-0.95)).to_numpy()))
    if not morceaux:
        return {}
    oof = pd.concat(morceaux).sort_index()
    y = oof["y"].to_numpy()
    moitie = len(oof) // 2
    out = {"cible": CIBLE_COUVERTURE, "cible_extreme": CIBLE_EXTREME, "nb": int(len(oof))}
    for nom, (b, h, cible) in {"": ("q10", "q90", CIBLE_COUVERTURE), "_extreme": ("q05", "q95", CIBLE_EXTREME)}.items():
        B, Hh = oof[b].to_numpy(), oof[h].to_numpy()
        adj_1 = _ajustement_conformal(B[:moitie], Hh[:moitie], y[:moitie], cible)
        dedans = (y[moitie:] >= B[moitie:] - adj_1) & (y[moitie:] <= Hh[moitie:] + adj_1)
        partie = oof.iloc[moitie:].assign(dedans=dedans.astype(float))
        boot = bootstrap_mois(partie, lambda d: np.array([d["dedans"].mean()]), graine=2)
        out[f"couverture_brute{nom}"] = float(((y >= B) & (y <= Hh)).mean())
        out[f"couverture{nom}"] = float(dedans.mean())
        out[f"ic{nom}"] = _ic(boot[:, 0]) if len(boot) else None
        out[f"ajustement{nom}"] = _ajustement_conformal(B, Hh, y, cible)
    out["largeur_mediane"] = float(np.median(np.expm1(oof["q90"]) - np.expm1(oof["q10"])))
    return out


# ----------------------------------------------------------------------------
# Modèle « fera mieux que son marché ? »
# ----------------------------------------------------------------------------
def evaluer_relatif(jeu, horizon, variables, par_marche):
    rel = jeu.dropna(subset=["cible_rel"]).copy()
    if len(rel) < 5000:
        return {}, None
    rel["cible"] = rel["cible_rel"]
    oof = predictions_hors_echantillon(rel, horizon, variables, par_marche)
    if oof is None or oof["cible"].nunique() < 2 or len(oof) < 2000:
        return {}, None
    calib = CalibrationPlatt().fit(oof["proba"], oof["cible"])
    oof["proba"] = calib.predict(oof["proba"])
    p, y = oof["proba"].to_numpy(), oof["cible"].to_numpy()
    boot = bootstrap_mois(oof, lambda d: np.array([_auc(d["cible"].to_numpy(), d["proba"].to_numpy()),
                                                   _precision(d["cible"].to_numpy(), d["proba"].to_numpy())]), graine=3)
    confiants = p >= 0.55
    return {"auc": _auc(y, p), "precision": _precision(y, p),
            "precision_base": float(max(y.mean(), 1 - y.mean())), "nb": int(len(y)),
            "ic_auc": _ic(boot[:, 0]) if len(boot) else None, "ic_precision": _ic(boot[:, 1]) if len(boot) else None,
            "precision_confiants": float(y[confiants].mean()) if confiants.sum() >= 30 else None,
            "nb_confiants": int(confiants.sum())}, calib


# ----------------------------------------------------------------------------
# Sélection (le soir) et mémoire du modèle
# ----------------------------------------------------------------------------
FICHIER_MODELE = os.path.join(config.DOSSIER_HISTORIQUE, "modele.json")


def _lire_fichier_modele():
    try:
        with open(FICHIER_MODELE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _charger_selection():
    """Résultat de la dernière sélection (faite le soir), réutilisé pendant la journée."""
    m = _lire_fichier_modele()
    try:
        age_h = (datetime.now() - datetime.fromisoformat(m["date"])).total_seconds() / 3600
        if age_h > 48 or m.get("horizon") != config.HORIZON_PREDICTION or m.get("version", 1) < 2:
            return None
        if m["configuration"] not in {c[0] for c in configs_disponibles()}:
            return None
        return m
    except Exception:
        return None


def _sauver_selection(evaluation, calibs, mode, recette=None, entrainements=None):
    os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
    m = {"version": 2, "recette": recette, "entrainements": entrainements or [], "date": datetime.now().isoformat(timespec="seconds"), "horizon": config.HORIZON_PREDICTION,
         "configuration": evaluation.configuration, "mode": mode, "evaluation": evaluation.to_dict(),
         "platt": {k: (c.vers_dict() if c is not None else None) for k, c in calibs.items()}}
    with open(FICHIER_MODELE, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, default=lambda v: None)


def _decision_champion(resultats, champion_nom):
    """Garde le modèle en place sauf si un autre fait mieux de façon prouvée (95 %)."""
    meilleur = resultats[0]
    if not champion_nom or champion_nom not in {r[1] for r in resultats} or champion_nom == meilleur[1]:
        return meilleur, {"actuel": meilleur[1], "change": False,
                          "raison": "Premier choix ou même modèle qu'avant." if not champion_nom else "Le modèle en place reste le meilleur."}
    champ = next(r for r in resultats if r[1] == champion_nom)
    a, b = meilleur[4], champ[4]
    if len(a) != len(b) or not np.array_equal(a.index.values, b.index.values):
        return champ, {"actuel": champ[1], "change": False, "raison": "Comparaison impossible : modèle en place conservé."}
    duo = pd.DataFrame({"cible": a["cible"].to_numpy(), "pa": a["proba"].to_numpy(), "pb": b["proba"].to_numpy()}, index=a.index)
    boot = bootstrap_mois(duo, lambda d: np.array([_auc(d["cible"].to_numpy(), d["pa"].to_numpy())
                                                   - _auc(d["cible"].to_numpy(), d["pb"].to_numpy())]), graine=4)
    ic = _ic(boot[:, 0]) if len(boot) else None
    if ic and ic[0] > 0:
        return meilleur, {"actuel": meilleur[1], "ancien": champ[1], "change": True, "ic_gain_auc": ic,
                          "raison": "Le nouveau modèle fait mieux de façon prouvée (95 %) : il remplace l'ancien."}
    return champ, {"actuel": champ[1], "challenger": meilleur[1], "change": False, "ic_gain_auc": ic,
                   "raison": "Un autre modèle a eu un meilleur score, mais l'écart peut venir du hasard : le modèle en place est gardé."}


def entrainer_et_predire(donnees, marches, horizon: int = config.HORIZON_PREDICTION,
                         supplementaires: dict | None = None, selection: bool | None = None):
    """Renvoie ({ticker: probabilité de hausse}, Evaluation). Le soir : sélection complète, tests et
    mémoire ; dans la journée : réutilise la sélection du soir et refait les contrôles."""
    supplementaires = supplementaires or {}
    tous = {**supplementaires, **donnees}
    jeu = construire_jeu(tous, marches, horizon)
    if selection is None:
        selection = os.environ.get("RADAR_SELECTION") == "1"
    cache = None if selection else _charger_selection()

    if cache is not None:
        _, variables, par_marche, params = {c[0]: c for c in configs_disponibles()}[cache["configuration"]]
        ev = cache["evaluation"]
        evaluation = Evaluation(**{k: ev[k] for k in CHAMPS_CACHE if k in ev})
        calibs = {k: CalibrationPlatt.depuis_dict(v) for k, v in (cache.get("platt") or {}).items()}
        mode = cache.get("mode", "commun")
    else:
        resultats = []
        for nom, variables, par_marche, params in configs_disponibles():
            oof = predictions_hors_echantillon(jeu, horizon, variables, par_marche, params=params)
            if oof is None or oof["cible"].nunique() < 2:
                continue
            resultats.append((_auc(oof["cible"].to_numpy(), oof["proba"].to_numpy()), nom, variables, par_marche, oof, params))
        if not resultats:
            return {}, Evaluation(np.nan, np.nan, np.nan, 0)
        resultats.sort(key=lambda r: r[0], reverse=True)
        ancien = _lire_fichier_modele() or {}
        choix, champion = _decision_champion(resultats, ancien.get("configuration"))
        _, nom, variables, par_marche, oof, params = choix

        # IA n°2 sur les mêmes périodes de test, puis combinaison des deux
        oof2 = predictions_hors_echantillon(jeu, horizon, variables, par_marche, algos=("ia2",), params=params)
        calibs = {"ia1": None, "ia2": None, "final": None, "relatif": None}
        mode = "ia1"
        ia = {}
        if oof2 is not None and len(oof2) == len(oof) and np.array_equal(oof2.index.values, oof.index.values):
            oof = oof.copy()
            oof["proba_ia2"] = oof2["proba_ia2"].to_numpy()
            y = oof["cible"].to_numpy()
            calibs["ia1"] = CalibrationPlatt().fit(oof["proba_ia1"], y)
            calibs["ia2"] = CalibrationPlatt().fit(oof["proba_ia2"], y)
            c1, c2 = calibs["ia1"].predict(oof["proba_ia1"]), calibs["ia2"].predict(oof["proba_ia2"])
            comb = 0.5 * (oof["proba_ia1"] + oof["proba_ia2"])
            for cle, pp in (("ia1", c1), ("ia2", c2), ("commun", comb)):
                ia[cle] = {"auc": _auc(y, pp), "precision": _precision(y, CalibrationPlatt().fit(pp, y).predict(pp))}
            # la combinaison n'est retenue que si elle ne fait pas moins bien que l'IA n°1 seule
            if ia["commun"]["auc"] >= ia["ia1"]["auc"] - 0.002:
                mode = "commun"
                oof["proba"] = comb
            oof["accord"] = (c1 > 0.5) == (c2 > 0.5)
        evaluation, calibs["final"] = _evaluation(oof)
        evaluation.configuration = nom
        evaluation.comparaison = [{"nom": n, "auc": a} for a, n, *_ in resultats]
        evaluation.champion = champion
        evaluation.ia = {**ia, "mode": mode}
        if "accord" in oof:
            pf = calibs["final"].predict(oof["proba"]) if calibs["final"] else oof["proba"]
            y = oof["cible"].to_numpy()
            acc = oof["accord"].to_numpy()
            juste = ((pf > 0.5) == (y == 1)).astype(float)
            d = pd.DataFrame({"juste": juste, "accord": acc.astype(float)}, index=oof.index)
            boot = bootstrap_mois(d, lambda x: np.array([x.loc[x["accord"] == 1, "juste"].mean(),
                                                         x.loc[x["accord"] == 0, "juste"].mean()]), graine=5)
            evaluation.accord = {"part": float(acc.mean()), "precision_accord": float(juste[acc].mean()) if acc.any() else None,
                                 "precision_desaccord": float(juste[~acc].mean()) if (~acc).any() else None,
                                 "ic_accord": _ic(boot[:, 0]) if len(boot) else None,
                                 "ic_desaccord": _ic(boot[:, 1]) if len(boot) else None}
        try:
            evaluation.fourchette = fiabilite_fourchettes(jeu, horizon, variables)
        except Exception:
            evaluation.fourchette = {}
        try:
            evaluation.relatif, calibs["relatif"] = evaluer_relatif(jeu, horizon, variables, par_marche)
        except Exception:
            evaluation.relatif, calibs["relatif"] = {}, None
        evaluation.date_evaluation = datetime.now().isoformat(timespec="minutes")
        _sauver_selection(evaluation, calibs, mode, ancien.get("recette"), ancien.get("entrainements"))

    probas = _predire(jeu, tous, donnees, marches, variables, par_marche, calibs, mode, evaluation, params)
    evaluation.controles = controler(probas, evaluation, marches, nouvelle_methode=cache is None)
    return probas, evaluation


def _predire(jeu, tous, donnees, marches, variables, par_marche, calibs, mode, evaluation, params=None):
    etiquete = jeu.dropna(subset=["cible"])
    ia1 = Predicteur(variables, par_marche, "ia1", params).fit(etiquete)
    ia2 = Predicteur(variables, par_marche, "ia2", params).fit(etiquete) if calibs.get("ia2") is not None else None
    try:
        vs_q, mods_q = _modeles_quantiles(etiquete, variables)
    except Exception:
        vs_q, mods_q = None, None
    modele_rel = None
    if calibs.get("relatif") is not None:
        try:
            rel = jeu.dropna(subset=["cible_rel"]).copy()
            rel["cible"] = rel["cible_rel"]
            modele_rel = Predicteur(variables, par_marche).fit(rel)
        except Exception:
            modele_rel = None

    # dernière ligne de chaque titre, classements recalculés entre ces dernières lignes
    dernieres = []
    for ticker, d in tous.items():
        ligne = d[FEATURES].iloc[[-1]].copy()
        ligne["est_crypto"] = float(marches.get(ticker) == "crypto")
        ligne["ticker"] = ticker
        dernieres.append(ligne)
    actuel = pd.concat(dernieres).reset_index(drop=True)
    for c in COLS_RANG:
        actuel[f"rang_{c}"] = actuel[c].rank(pct=True)
    garde = actuel["ticker"].isin(list(donnees)).to_numpy()
    tks = actuel["ticker"].to_numpy()

    p1 = ia1.predict_proba(actuel)
    p2 = ia2.predict_proba(actuel) if ia2 is not None else None
    brut = 0.5 * (p1 + p2) if (mode == "commun" and p2 is not None) else p1
    final = calibs["final"].predict(brut) if calibs.get("final") is not None else brut
    if p2 is not None:
        c1, c2 = calibs["ia1"].predict(p1), calibs["ia2"].predict(p2)
        evaluation.proba_ia1 = {t: float(v) for t, v, g in zip(tks, c1, garde) if g}
        evaluation.proba_ia2 = {t: float(v) for t, v, g in zip(tks, c2, garde) if g}
        evaluation.accord_titres = {t: bool((a > 0.5) == (b > 0.5)) for t, a, b, g in zip(tks, c1, c2, garde) if g}
    F = evaluation.fourchette or {}
    if mods_q is not None:
        Q = _predire_quantiles(vs_q, mods_q, actuel)
        a, ax = max(0.0, float(F.get("ajustement") or 0.0)), max(0.0, float(F.get("ajustement_extreme") or 0.0))
        for t, q, g in zip(tks, Q, garde):
            if g:
                evaluation.quantiles[t] = (float(q[1] - a), float(q[2]), float(q[3] + a))
                evaluation.extremes[t] = (float(min(q[0] - ax, q[1] - a)), float(max(q[4] + ax, q[3] + a)))
    if modele_rel is not None:
        pr = calibs["relatif"].predict(modele_rel.predict_proba(actuel))
        evaluation.proba_marche = {t: float(v) for t, v, g in zip(tks, pr, garde)
                                   if g and config.benchmark_de(t, marches.get(t, "")) != t}
    return {t: float(v) for t, v, g in zip(tks, final, garde) if g}


# ----------------------------------------------------------------------------
# Contrôles de cohérence avant publication (« l'IA teste ses compétences à chaque fois »)
# ----------------------------------------------------------------------------
def _dernieres_publiees():
    try:
        h = pd.read_csv(os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv"), usecols=["date", "ticker", "proba"])
        h = h.dropna(subset=["proba"])
        h["date"] = pd.to_datetime(h["date"])
        recentes = h[h["date"] >= h["date"].max() - pd.Timedelta(days=5)]
        return recentes.sort_values("date").groupby("ticker")["proba"].last().to_dict()
    except Exception:
        return {}


def controler(probas: dict, evaluation: Evaluation, marches: dict, nouvelle_methode: bool = False) -> list:
    """Vérifie le calcul avant de publier. Un contrôle critique en échec lève ErreurControle :
    le site n'est pas republié et l'ancienne version reste en ligne."""
    res = []

    def ajoute(nom, ok, detail, critique=False):
        res.append({"nom": nom, "ok": bool(ok), "detail": detail, "critique": critique})

    p = np.array(list(probas.values()), dtype=float)
    ajoute("Probabilités valides", len(p) > 0 and np.all(np.isfinite(p)) and np.all((p >= 0) & (p <= 1)),
           f"{len(p)} probabilités calculées, toutes entre 0 et 100 %", critique=True)
    ajoute("Avis variés selon les titres", len(p) > 3 and float(np.std(p)) > 0.004,
           f"écart-type {np.std(p) * 100:.1f} points (une IA qui dit la même chose partout est en panne)" if len(p) else "aucune", critique=True)
    q = list(evaluation.quantiles.values())
    ordre = all(b <= m <= h and (h - b) < np.log(20) for b, m, h in q)
    ajoute("Fourchettes cohérentes", ordre, f"{len(q)} fourchettes : bas ≤ central ≤ haut, largeur plausible", critique=bool(q))
    precedentes = _dernieres_publiees()
    communs = [t for t in probas if t in precedentes]
    if len(communs) >= 5:
        sauts = np.abs(np.array([probas[t] - precedentes[t] for t in communs]))
        med = float(np.median(sauts))
        ajoute("Pas de changement brutal inexpliqué", med < 0.12,
               f"changement médian {med * 100:.1f} points depuis les dernières prévisions ({len(communs)} titres)"
               + (" ; normal après un nouveau test complet du soir" if nouvelle_methode and med >= 0.12 else ""),
               # bloquant seulement en journée : le soir, un nouveau test complet peut légitimement tout recaler
               critique=med >= 0.2 and not nouvelle_methode)
    else:
        ajoute("Pas de changement brutal inexpliqué", True, "pas encore assez d'historique pour comparer")
    auc = evaluation.auc
    ajoute("Meilleure que le hasard sur l'historique", auc == auc and auc > 0.5,
           f"AUC {auc:.3f} (0,5 = hasard)".replace(".", ",", 1) if auc == auc else "non évaluée")
    if evaluation.accord_titres:
        part = float(np.mean(list(evaluation.accord_titres.values())))
        ajoute("Les deux IA souvent d'accord", part >= 0.5, f"d'accord sur {part * 100:.0f} % des titres aujourd'hui")
    critiques = [r for r in res if r["critique"] and not r["ok"]]
    if critiques:
        raise ErreurControle("; ".join(f"{r['nom']} : {r['detail']}" for r in critiques))
    return res
