"""Modèle de machine learning : probabilité que le cours soit plus haut dans N séances.

Ce qui le rend plus fiable que la version 1 :
- horizon de 20 séances (~1 mois) : à 5 jours, les mouvements sont presque du pur bruit ;
- variables de classement entre titres (ex : « fait partie des 20 % qui montent le plus ») ;
- ensemble de deux modèles différents (gradient boosting + régression logistique) ;
- validation walk-forward avec purge : testé uniquement sur des périodes jamais vues ;
- variables de « régime » : le marché global est-il haussier, agité ?
- calibration isotonique : les probabilités affichées sont recalées sur les fréquences réellement
  observées hors échantillon (« 60 % » veut dire « ça a monté 6 fois sur 10 dans ce cas-là »).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import config
from .indicators import FEATURES

COLS_RANG = ["ret_21j", "ret_63j", "ret_126j", "vol_20j", "force_relative_63j", "dist_plus_haut"]
VARIABLES = FEATURES + ["est_crypto"] + [f"rang_{c}" for c in COLS_RANG]
TRANCHES = [0.0, 0.40, 0.45, 0.50, 0.55, 0.60, 1.0]
SEUIL_FORT = 0.55  # probabilité calibrée minimale pour un « signal fort »


def technique_haussiere(df: pd.DataFrame) -> pd.Series:
    """Tendance technique haussière nette : au-dessus de la moyenne 200 j, moyenne 50 j > 200 j,
    MACD positif et RSI pas en surchauffe. Fonctionne sur les colonnes d'indicateurs."""
    sma50_sur_200 = (1 + df["dist_sma200"]) / (1 + df["dist_sma50"])
    return ((df["dist_sma200"] > 0) & (sma50_sur_200 > 1) & (df["macd_hist_norm"] > 0)
            & (df["rsi"] < 75)).fillna(False)
NOMS_TRANCHES = ["< 40 %", "40–45 %", "45–50 %", "50–55 %", "55–60 %", "> 60 %"]


class CalibrationPlatt:
    """Régression logistique sur le logit de la probabilité brute."""

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


class Ensemble:
    """Moyenne de deux modèles qui se trompent de façons différentes → plus stable."""

    def __init__(self):
        self.gbm = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.04, max_iter=250,
                                                  min_samples_leaf=300, l2_regularization=2.0,
                                                  random_state=0)
        self.lin = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                 LogisticRegression(C=0.05, max_iter=500))

    def fit(self, X, y):
        self.gbm.fit(X, y)
        self.lin.fit(X, y)
        return self

    def predict_proba(self, X):
        return 0.5 * self.gbm.predict_proba(X)[:, 1] + 0.5 * self.lin.predict_proba(X)[:, 1]


@dataclass
class Evaluation:
    precision: float
    precision_base: float
    auc: float
    nb_tests: int
    calibration: list = field(default_factory=list)   # par tranche de probabilité
    signaux_forts: dict = field(default_factory=dict)  # modèle confiant ET technique haussière
    top_confiance: dict = field(default_factory=dict)  # 10 % des prévisions les plus confiantes
    configuration: str = ""                            # façon de prévoir retenue
    comparaison: list = field(default_factory=list)    # AUC de chaque façon testée
    par_marche: dict = field(default_factory=dict)
    periode: str = ""

    @property
    def avantage(self) -> float:
        return self.precision - self.precision_base

    def verdict(self) -> str:
        if np.isnan(self.auc) or self.auc < 0.52 or self.avantage < 0.005:
            return "Pas d'avantage mesurable sur le hasard : les probabilités sont indicatives seulement."
        if self.auc < 0.56:
            return "Léger avantage statistique : utile pour trier, insuffisant pour trader seul dessus."
        return "Avantage statistique net sur l'historique, à confirmer avec le suivi en conditions réelles."

    def rendement_attendu(self, proba: float) -> float:
        """Rendement moyen observé historiquement quand le modèle donnait cette probabilité."""
        for t in self.calibration:
            if t["min"] <= proba < t["max"] and t["nb"] >= 30:
                return t["rendement_moyen"]
        return 0.0

    def to_dict(self) -> dict:
        return {"precision": self.precision, "precision_base": self.precision_base, "auc": self.auc,
                "nb_tests": self.nb_tests, "calibration": self.calibration,
                "par_marche": self.par_marche, "periode": self.periode, "verdict": self.verdict(),
                "signaux_forts": self.signaux_forts, "top_confiance": self.top_confiance,
                "seuil_fort": SEUIL_FORT, "configuration": self.configuration,
                "comparaison": self.comparaison,
                "horizon": config.HORIZON_PREDICTION}


def _ajouter_rangs(jeu: pd.DataFrame) -> pd.DataFrame:
    for c in COLS_RANG:
        jeu[f"rang_{c}"] = jeu.groupby(level=0)[c].rank(pct=True)
    return jeu


def construire_jeu(donnees: dict[str, pd.DataFrame], marches: dict[str, str],
                   horizon: int) -> pd.DataFrame:
    morceaux = []
    for ticker, d in donnees.items():
        m = d[FEATURES].copy()
        m["est_crypto"] = float(marches.get(ticker) == "crypto")
        futur = d["Close"].shift(-horizon) / d["Close"] - 1
        m["rendement_futur"] = futur
        m["cible"] = np.where(futur.isna(), np.nan, (futur > 0).astype(float))
        m["ticker"] = ticker
        m["marche"] = marches.get(ticker, "?")
        morceaux.append(m.iloc[252:])
    jeu = pd.concat(morceaux).sort_index()
    return _ajouter_rangs(jeu)


VARIABLES_BASE = FEATURES[:21] + ["est_crypto"] + [f"rang_{c}" for c in COLS_RANG]
CONFIGS = [
    ("Un seul modèle, tous les indicateurs", VARIABLES, False),
    ("Un seul modèle, indicateurs de base", VARIABLES_BASE, False),
    ("Un modèle par marché (actions / cryptos)", VARIABLES, True),
]


class Predicteur:
    """Ensemble entraîné soit sur tout le marché, soit séparément pour les actions et les cryptos
    (qui ne réagissent pas pareil). Un groupe trop petit retombe sur le modèle commun."""

    def __init__(self, variables, par_marche=False):
        self.variables, self.par_marche = variables, par_marche
        self.commun, self.groupes = None, {}

    @staticmethod
    def _utiles(df, variables):
        """Retire les colonnes vides ou constantes (ex : sentiment crypto pour les actions)."""
        return [v for v in variables if df[v].nunique(dropna=True) > 1]

    def fit(self, df):
        self.vars_commun = self._utiles(df, self.variables)
        self.commun = Ensemble().fit(df[self.vars_commun], df["cible"])
        if self.par_marche:
            for g, sous in df.groupby("est_crypto"):
                if len(sous) >= 3000 and sous["cible"].nunique() == 2:
                    vs = self._utiles(sous, self.variables)
                    self.groupes[g] = (vs, Ensemble().fit(sous[vs], sous["cible"]))
        return self

    def predict_proba(self, df):
        p = self.commun.predict_proba(df[self.vars_commun])
        if self.groupes:
            g = df["est_crypto"].to_numpy()
            for cle, (vs, mod) in self.groupes.items():
                masque = g == cle
                if masque.any():
                    p[masque] = mod.predict_proba(df.loc[masque, vs] if df.index.is_unique else df[vs][masque])
        return p


def predictions_hors_echantillon(jeu, horizon, variables, par_marche, n_plis=6):
    """Prévisions « walk-forward » : chaque période n'est prédite que par un modèle entraîné avant elle."""
    etiquete = jeu.dropna(subset=["cible"])
    dates = np.array(sorted(etiquete.index.unique()))
    bornes = np.linspace(len(dates) * 0.4, len(dates), n_plis + 1).astype(int)
    morceaux = []
    for i in range(n_plis):
        debut, fin = dates[bornes[i]], dates[bornes[i + 1] - 1]
        fin_train = dates[max(bornes[i] - horizon - 2, 0)]  # purge anti-fuite du futur
        train = etiquete[etiquete.index <= fin_train]
        test = etiquete[(etiquete.index >= debut) & (etiquete.index <= fin)]
        if len(train) < 2000 or test.empty or train["cible"].nunique() < 2:
            continue
        mod = Predicteur(variables, par_marche).fit(train)
        t = test[["cible", "rendement_futur", "marche"]].copy()
        t["technique"] = technique_haussiere(test).to_numpy()
        t["proba"] = mod.predict_proba(test)
        morceaux.append(t)
    return pd.concat(morceaux) if morceaux else None


def _evaluation(oof):
    """Calibre les prévisions hors échantillon et calcule toutes les mesures de fiabilité."""
    oof = oof.copy()
    calibreur = None
    if len(oof) >= 2000:
        # Calibration de Platt (courbe lisse et croissante) : recale les probabilités sur les
        # fréquences observées, sans paliers (évite que 20 titres affichent tous « 54 % »).
        calibreur = CalibrationPlatt().fit(oof["proba"], oof["cible"])
        oof["proba"] = calibreur.predict(oof["proba"])
    y, p = oof["cible"].to_numpy(), oof["proba"].to_numpy()

    calibration = []
    for (a, b), nom in zip(zip(TRANCHES[:-1], TRANCHES[1:]), NOMS_TRANCHES):
        sel = oof[(oof["proba"] >= a) & (oof["proba"] < b)]
        calibration.append({"tranche": nom, "min": a, "max": b, "nb": int(len(sel)),
                            "taux_hausse": float(sel["cible"].mean()) if len(sel) else None,
                            "rendement_moyen": float(sel["rendement_futur"].median()) if len(sel) else 0.0})
    par_marche = {}
    for m, g in oof.groupby("marche"):
        par_marche[m] = {"precision": float(((g["proba"] > 0.5) == (g["cible"] == 1)).mean()),
                         "base": float(max(g["cible"].mean(), 1 - g["cible"].mean())),
                         "nb": int(len(g))}
    periode = f"{oof.index.min():%m/%Y} – {oof.index.max():%m/%Y}"

    def resume(sel):
        if len(sel) < 30:
            return {"nb": int(len(sel)), "precision": None, "rendement_median": None}
        return {"nb": int(len(sel)), "precision": float(sel["cible"].mean()),
                "rendement_median": float(sel["rendement_futur"].median()),
                "part": float(len(sel) / len(oof))}
    forts = resume(oof[(oof["proba"] >= SEUIL_FORT) & oof["technique"]])
    forts["base"] = float(oof["cible"].mean())  # taux de hausse moyen, pour comparer
    top = resume(oof[oof["proba"] >= oof["proba"].quantile(0.9)])
    ev = Evaluation(
        precision=float(((p > 0.5) == (y == 1)).mean()),
        precision_base=float(max(y.mean(), 1 - y.mean())),
        auc=float(roc_auc_score(y, p)) if len(set(y)) > 1 else np.nan,
        nb_tests=len(y), calibration=calibration, par_marche=par_marche, periode=periode,
        signaux_forts=forts, top_confiance=top)
    return ev, calibreur


def evaluer_walk_forward(jeu, horizon, n_plis=6):
    """Compatibilité : évaluation du modèle par défaut."""
    oof = predictions_hors_echantillon(jeu, horizon, VARIABLES, False, n_plis)
    if oof is None:
        return Evaluation(np.nan, np.nan, np.nan, 0), None
    return _evaluation(oof)


def entrainer_et_predire(donnees, marches, horizon: int = config.HORIZON_PREDICTION):
    """Teste plusieurs façons de prévoir, garde celle qui fait le mieux sur des périodes jamais vues,
    puis prédit. Renvoie ({ticker: proba de hausse}, Evaluation)."""
    jeu = construire_jeu(donnees, marches, horizon)

    resultats = []
    for nom, variables, par_marche in CONFIGS:
        oof = predictions_hors_echantillon(jeu, horizon, variables, par_marche)
        if oof is None or oof["cible"].nunique() < 2:
            continue
        auc = float(roc_auc_score(oof["cible"], oof["proba"]))
        resultats.append((auc, nom, variables, par_marche, oof))
    if not resultats:
        return {}, Evaluation(np.nan, np.nan, np.nan, 0)
    resultats.sort(key=lambda r: r[0], reverse=True)
    auc, nom, variables, par_marche, oof = resultats[0]
    evaluation, calibreur = _evaluation(oof)
    evaluation.configuration = nom
    evaluation.comparaison = [{"nom": n, "auc": a} for a, n, *_ in resultats]

    etiquete = jeu.dropna(subset=["cible"])
    modele = Predicteur(variables, par_marche).fit(etiquete)

    # Dernière ligne de chaque titre, classements recalculés entre ces dernières lignes
    dernieres = []
    for ticker, d in donnees.items():
        ligne = d[FEATURES].iloc[[-1]].copy()
        ligne["est_crypto"] = float(marches.get(ticker) == "crypto")
        ligne["ticker"] = ticker
        dernieres.append(ligne)
    actuel = pd.concat(dernieres).reset_index(drop=True)
    for c in COLS_RANG:
        actuel[f"rang_{c}"] = actuel[c].rank(pct=True)
    probas = modele.predict_proba(actuel)
    if calibreur is not None:
        probas = calibreur.predict(probas)
    return dict(zip(actuel["ticker"], map(float, probas))), evaluation
