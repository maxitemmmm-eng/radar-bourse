"""Le « manuel de Bourse » de l'IA : des règles connues, étudiées par des chercheurs en finance.

Chaque règle devient une information que l'IA peut utiliser. Mais l'IA ne les croit pas sur parole :
l'entraînement (entrainement_ia.py) vérifie chacune sur des années qu'elle n'a jamais vues, et ne garde
que celles qui aident vraiment. Beaucoup d'effets célèbres se sont affaiblis depuis leur découverte
(McLean et Pontiff, 2016 : environ un tiers de moins après publication) : c'est justement pour ça
qu'on les teste au lieu de les appliquer aveuglément.

AJOUTER UNE CONNAISSANCE : copie un bloc de la liste REGLES, change la clé, le nom, l'idée, la source et
le calcul (une fonction qui reçoit les cours `d` et l'indice du marché `b`). Au prochain entraînement,
l'IA la testera toute seule et dira sur la page « Ce que sait l'IA » si elle est utile.

Chaque règle peut avoir des variantes (ex : momentum sur 6 ou 12 mois) : l'entraînement teste toutes les
versions et indique la meilleure. C'est ainsi que l'IA améliore les connaissances qu'on lui donne.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HALVINGS_BITCOIN = pd.to_datetime(["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20", "2028-04-15"])


def _ret(c, n, saut=0):
    return c.shift(saut) / c.shift(n) - 1


def _vol(c, n):
    return c.pct_change().rolling(n, min_periods=int(n * 0.8)).std() * np.sqrt(252)


def _beta(c, b, n=252):
    r, rb = c.pct_change(), b.pct_change()
    cov = r.rolling(n, min_periods=int(n * 0.7)).cov(rb)
    return cov / rb.rolling(n, min_periods=int(n * 0.7)).var()


def _vol_idio(c, b, n=60):
    """Volatilité propre au titre, une fois retiré ce qui vient du marché."""
    if b is None:
        return pd.Series(np.nan, index=c.index)
    r, rb = c.pct_change(), b.pct_change()
    beta = r.rolling(n, min_periods=int(n * 0.8)).cov(rb) / rb.rolling(n, min_periods=int(n * 0.8)).var()
    return (r - beta * rb).rolling(n, min_periods=int(n * 0.8)).std() * np.sqrt(252)


def _amihud(d, n=60):
    """Illiquidité : de combien le prix bouge pour chaque euro échangé (plus c'est grand, moins c'est liquide)."""
    montant = (d["Close"] * d["Volume"]).replace(0, np.nan)
    return np.log1p((d["Close"].pct_change().abs() / montant).rolling(n, min_periods=int(n * 0.6)).mean() * 1e9)


def _regularite(c, n=252):
    """« Frog in the pan » : une hausse faite de nombreux petits pas réguliers plutôt que de quelques bonds."""
    r = c.pct_change()
    part = (r > 0).astype(float).rolling(n, min_periods=int(n * 0.8)).mean() - (r < 0).astype(float).rolling(n, min_periods=int(n * 0.8)).mean()
    return np.sign(_ret(c, n, 21)) * part


def _nuit(d, n=252):
    """Rendement accumulé pendant les nuits (de la clôture à l'ouverture du lendemain)."""
    nuit = np.log(d["Open"] / d["Close"].shift(1)).replace([np.inf, -np.inf], np.nan)
    return nuit.rolling(n, min_periods=int(n * 0.8)).sum()


def _beta_baisse(c, b, n=252):
    """Sensibilité du titre au marché, mesurée seulement les jours où le marché baisse."""
    if b is None:
        return pd.Series(np.nan, index=c.index)
    r, rb = c.pct_change(), b.pct_change()
    rb_b = rb.where(rb < 0)
    r_b = r.where(rb < 0)
    return r_b.rolling(n, min_periods=60).cov(rb_b) / rb_b.rolling(n, min_periods=60).var()


def _jours_depuis_halving(index):
    idx = pd.DatetimeIndex(index)
    pos = np.searchsorted(HALVINGS_BITCOIN.values, idx.values, side="right") - 1
    dernier = HALVINGS_BITCOIN.values[np.clip(pos, 0, None)]
    jours = (idx.values - dernier).astype("timedelta64[D]").astype(float)
    jours[pos < 0] = np.nan
    return pd.Series(jours / 1460, index=index)   # 0 = juste après un halving, 1 = 4 ans après


# Sens attendu : +1 = la règle dit « plutôt hausse » quand la valeur est grande, -1 = l'inverse.
REGLES = [
    {"cle": "momentum", "nom": "Le momentum (ce qui monte a tendance à continuer)",
     "idee": "Les titres qui ont le plus monté sur les 6 à 12 derniers mois (sans compter le dernier mois) ont "
             "souvent continué à faire mieux les mois suivants.",
     "source": "Jegadeesh et Titman (1993) ; Carhart (1997) ; Asness, Moskowitz et Pedersen (2013)", "sens": 1,
     "variantes": {"12m": lambda d, b: _ret(d["Close"], 252, 21), "6m": lambda d, b: _ret(d["Close"], 126, 21),
                   "3m": lambda d, b: _ret(d["Close"], 63, 5)}},
    {"cle": "retournement", "nom": "Le retournement à court terme",
     "idee": "Sur un mois, les titres qui ont le plus baissé rebondissent souvent un peu, et ceux qui ont le plus "
             "monté reculent un peu (excès de réaction des investisseurs).",
     "source": "Jegadeesh (1990) ; Lehmann (1990)", "sens": -1,
     "variantes": {"1m": lambda d, b: _ret(d["Close"], 21), "1s": lambda d, b: _ret(d["Close"], 5)}},
    {"cle": "plus_haut_52s", "nom": "La proximité du plus haut sur un an",
     "idee": "Un titre proche de son plus haut sur 52 semaines a tendance à continuer de monter : les investisseurs "
             "hésitent à acheter au-dessus de ce repère, puis rattrapent leur retard.",
     "source": "George et Hwang (2004)", "sens": 1,
     "variantes": {"52s": lambda d, b: d["Close"] / d["Close"].rolling(252, min_periods=200).max()}},
    {"cle": "faible_volatilite", "nom": "L'anomalie de la faible volatilité",
     "idee": "Les titres calmes ont historiquement rapporté autant, voire plus, que les titres très agités, pour "
             "beaucoup moins de risque.",
     "source": "Ang, Hodrick, Xing et Zhang (2006) ; Baker, Bradley et Wurgler (2011)", "sens": -1,
     "variantes": {"60j": lambda d, b: _vol(d["Close"], 60), "120j": lambda d, b: _vol(d["Close"], 120)}},
    {"cle": "beta_faible", "nom": "Parier contre le bêta",
     "idee": "Les titres qui amplifient les mouvements du marché (bêta élevé) ont souvent moins rapporté que prévu, "
             "et les titres peu sensibles au marché plus que prévu.",
     "source": "Frazzini et Pedersen (2014) ; Black, Jensen et Scholes (1972)", "sens": -1,
     "variantes": {"1an": lambda d, b: _beta(d["Close"], b) if b is not None else pd.Series(np.nan, index=d.index)}},
    {"cle": "loterie", "nom": "L'effet « ticket de loterie »",
     "idee": "Les titres qui ont fait un bond spectaculaire en une journée récemment attirent les joueurs, sont "
             "souvent trop chers ensuite, et font moins bien.",
     "source": "Bali, Cakici et Whitelaw (2011)", "sens": -1,
     "variantes": {"1m": lambda d, b: d["Close"].pct_change().rolling(21).max()}},
    {"cle": "tendance_temporelle", "nom": "Le suivi de tendance",
     "idee": "Un actif en hausse sur un an, rapporté à son agitation, a eu tendance à continuer dans le même sens "
             "(utilisé par de nombreux fonds de suivi de tendance).",
     "source": "Moskowitz, Ooi et Pedersen (2012) ; Hurst, Ooi et Pedersen (2017)", "sens": 1,
     "variantes": {"12m": lambda d, b: _ret(d["Close"], 252) / _vol(d["Close"], 60).replace(0, np.nan)}},
    {"cle": "choc_volume", "nom": "La prime des volumes élevés",
     "idee": "Un titre qui attire soudain beaucoup plus d'échanges que d'habitude gagne en visibilité, et a souvent "
             "fait un peu mieux le mois suivant.",
     "source": "Gervais, Kaniel et Mingelgrin (2001)", "sens": 1,
     "variantes": {"5j": lambda d, b: d["Volume"].rolling(5).mean() / d["Volume"].rolling(60).mean().replace(0, np.nan)}},
    {"cle": "saison", "nom": "« Sell in May » : les saisons de la Bourse",
     "idee": "Historiquement, les marchés ont souvent mieux rapporté de novembre à avril que de mai à octobre.",
     "source": "Bouman et Jacobsen (2002) ; Jacobsen et Zhang (2014)", "sens": 1,
     "variantes": {"hiver": lambda d, b: pd.Series(pd.DatetimeIndex(d.index).month.isin([11, 12, 1, 2, 3, 4]).astype(float), index=d.index)}},
    {"cle": "ecart_moyenne", "nom": "Le retour vers la moyenne",
     "idee": "Quand un prix s'écarte très fortement de sa moyenne récente (en nombre d'écarts habituels), il a "
             "parfois tendance à y revenir.",
     "source": "De Bondt et Thaler (1985) ; Poterba et Summers (1988)", "sens": -1,
     "variantes": {"20j": lambda d, b: (d["Close"] - d["Close"].rolling(20).mean()) / d["Close"].rolling(20).std().replace(0, np.nan),
                   "60j": lambda d, b: (d["Close"] - d["Close"].rolling(60).mean()) / d["Close"].rolling(60).std().replace(0, np.nan)}},
    {"cle": "momentum_relatif", "nom": "Le momentum face à son marché",
     "idee": "Un titre qui fait mieux que son propre marché depuis 6 mois a souvent continué à le battre.",
     "source": "Moskowitz et Grinblatt (1999) ; Blitz, Huij et Martens (2011)", "sens": 1,
     "variantes": {"6m": lambda d, b: (_ret(d["Close"], 126, 21) - _ret(b, 126, 21)) if b is not None else pd.Series(np.nan, index=d.index)}},
    {"cle": "cycle_halving", "nom": "Le cycle du « halving » Bitcoin (idée populaire, peu prouvée)",
     "idee": "Tous les 4 ans environ, la création de nouveaux bitcoins est divisée par deux. Beaucoup pensent que "
             "le marché crypto suit ce cycle. C'est une croyance répandue, avec très peu d'années pour la vérifier : "
             "l'IA la teste comme les autres.",
     "source": "Croyance de marché (pas d'étude solide)", "sens": 1, "crypto_seulement": True,
     "variantes": {"cycle": lambda d, b: _jours_depuis_halving(d.index)}},
    # --- Ajouts de la version 18 : encore plus d'études de base
    {"cle": "volatilite_propre", "nom": "La volatilité propre au titre",
     "idee": "Les titres qui bougent beaucoup pour des raisons qui leur sont propres (et pas à cause du marché) "
             "ont souvent moins rapporté ensuite : ils attirent des investisseurs trop optimistes.",
     "source": "Ang, Hodrick, Xing et Zhang (2006, 2009)", "sens": -1,
     "variantes": {"60j": lambda d, b: _vol_idio(d["Close"], b, 60)}},
    {"cle": "asymetrie", "nom": "L'asymétrie des rendements",
     "idee": "Les titres qui font parfois des bonds énormes (comme des billets de loterie) sont souvent payés trop "
             "cher, et rapportent moins ensuite.",
     "source": "Harvey et Siddique (2000) ; Amaya, Christoffersen, Jacobs et Vasquez (2015)", "sens": -1,
     "variantes": {"60j": lambda d, b: d["Close"].pct_change().rolling(60, min_periods=48).skew()}},
    {"cle": "illiquidite", "nom": "La prime d'illiquidité",
     "idee": "Les titres peu échangés sont plus difficiles à revendre : les investisseurs exigent en moyenne un peu "
             "plus de rendement pour les détenir.",
     "source": "Amihud (2002) ; Pastor et Stambaugh (2003)", "sens": 1,
     "variantes": {"60j": lambda d, b: _amihud(d, 60)}},
    {"cle": "momentum_regulier", "nom": "La régularité de la hausse (« frog in the pan »)",
     "idee": "Une hausse faite de nombreux petits pas réguliers passe inaperçue et continue plus longtemps qu'une "
             "hausse faite de quelques bonds spectaculaires.",
     "source": "Da, Gurun et Warachka (2014)", "sens": 1,
     "variantes": {"12m": lambda d, b: _regularite(d["Close"], 252)}},
    {"cle": "croisement_moyennes", "nom": "Les croisements de moyennes mobiles",
     "idee": "Un cours au-dessus de sa moyenne longue (et une moyenne courte au-dessus de la longue) a été suivi de "
             "meilleurs rendements dans les grandes études historiques sur l'analyse technique.",
     "source": "Brock, Lakonishok et LeBaron (1992) ; Faber (2007)", "sens": 1,
     "variantes": {"50_200": lambda d, b: d["Close"].rolling(50).mean() / d["Close"].rolling(200).mean() - 1,
                   "10mois": lambda d, b: d["Close"] / d["Close"].rolling(210).mean() - 1}},
    {"cle": "cassure", "nom": "La cassure du plus haut",
     "idee": "Quand le prix dépasse son plus haut des derniers mois, le mouvement a souvent continué un peu "
             "(règle de « trading range breakout »).",
     "source": "Brock, Lakonishok et LeBaron (1992)", "sens": 1,
     "variantes": {"6m": lambda d, b: (d["Close"] >= d["Close"].rolling(126).max().shift(1)).astype(float)
                   .where(d["Close"].rolling(126).max().notna())}},
    {"cle": "nuit", "nom": "Le momentum des nuits",
     "idee": "Une partie de la hausse se fait la nuit, entre la clôture et l'ouverture. Les titres qui montent "
             "régulièrement la nuit ont souvent continué à le faire.",
     "source": "Lou, Polk et Skouras (2019)", "sens": 1,
     "variantes": {"12m": lambda d, b: _nuit(d, 252)}},
    {"cle": "retournement_long", "nom": "Le retournement à long terme",
     "idee": "Sur 3 à 5 ans, les grands perdants ont souvent fini par faire mieux que les grands gagnants : "
             "les investisseurs exagèrent les bonnes et les mauvaises nouvelles.",
     "source": "De Bondt et Thaler (1985)", "sens": -1,
     "variantes": {"3ans": lambda d, b: _ret(d["Close"], 756, 252)}},
    {"cle": "effet_janvier", "nom": "L'effet janvier",
     "idee": "Historiquement, janvier a souvent été un bon mois, surtout pour les titres qui avaient baissé l'année "
             "précédente (ventes de fin d'année pour raisons fiscales).",
     "source": "Rozeff et Kinney (1976) ; Keim (1983)", "sens": 1,
     "variantes": {"dec_jan": lambda d, b: pd.Series(pd.DatetimeIndex(d.index).month.isin([12, 1]).astype(float), index=d.index)}},
    {"cle": "momentum_crypto", "nom": "Le momentum des cryptos (court terme)",
     "idee": "Chez les cryptos, les hausses des dernières semaines ont souvent continué la semaine suivante, plus "
             "nettement qu'en Bourse classique.",
     "source": "Liu et Tsyvinski (2021) ; Liu, Tsyvinski et Wu (2022)", "sens": 1, "crypto_seulement": True,
     "variantes": {"1s": lambda d, b: _ret(d["Close"], 7), "4s": lambda d, b: _ret(d["Close"], 28)}},
    {"cle": "pression_marche", "nom": "Le titre face aux journées de panique",
     "idee": "Les titres qui chutent fort quand tout le marché panique (risque de krach) ont dû offrir plus de "
             "rendement ensuite, en compensation.",
     "source": "Ang, Chen et Xing (2006) : le « bêta de baisse »", "sens": 1,
     "variantes": {"1an": lambda d, b: _beta_baisse(d["Close"], b)}},
]


def nom_colonne(cle: str, variante: str) -> str:
    return f"cx_{cle}_{variante}"


COLONNES = [nom_colonne(r["cle"], v) for r in REGLES for v in r["variantes"]]


def ajouter(d: pd.DataFrame, benchmark: pd.DataFrame | None = None, crypto: bool = False) -> None:
    """Ajoute au tableau une colonne par règle et par variante (calculée uniquement avec le passé)."""
    b = None
    if benchmark is not None and not benchmark.empty:
        b = benchmark["Close"].reindex(d.index).ffill()
    for r in REGLES:
        for v, f in r["variantes"].items():
            col = nom_colonne(r["cle"], v)
            if r.get("crypto_seulement") and not crypto:
                d[col] = np.nan
                continue
            try:
                s = f(d, b)
                d[col] = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan) if s is not None else np.nan
            except Exception:
                d[col] = np.nan


def description(col: str):
    """(règle, variante) correspondant à une colonne cx_…, ou (None, None)."""
    for r in REGLES:
        for v in r["variantes"]:
            if nom_colonne(r["cle"], v) == col:
                return r, v
    return None, None
