"""Configuration : univers de titres suivis et paramètres globaux."""

# --- Actions françaises (principales valeurs du CAC 40, suffixe .PA = Euronext Paris)
ACTIONS_FR = {
    "MC.PA": "LVMH", "OR.PA": "L'Oréal", "TTE.PA": "TotalEnergies", "SAN.PA": "Sanofi",
    "AIR.PA": "Airbus", "SU.PA": "Schneider Electric", "AI.PA": "Air Liquide",
    "BNP.PA": "BNP Paribas", "RMS.PA": "Hermès", "EL.PA": "EssilorLuxottica",
    "SAF.PA": "Safran", "CS.PA": "AXA", "DG.PA": "Vinci", "KER.PA": "Kering",
    "STLAP.PA": "Stellantis", "GLE.PA": "Société Générale", "CAP.PA": "Capgemini",
    "DSY.PA": "Dassault Systèmes", "ORA.PA": "Orange", "RI.PA": "Pernod Ricard",
}

# --- Actions américaines (grandes capitalisations)
ACTIONS_US = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "JPM": "JPMorgan", "V": "Visa", "NFLX": "Netflix", "AMD": "AMD",
    "PLTR": "Palantir", "COST": "Costco", "LLY": "Eli Lilly", "XOM": "ExxonMobil",
    "UNH": "UnitedHealth", "CRM": "Salesforce", "INTC": "Intel", "DIS": "Disney",
}

# --- Cryptomonnaies principales (cotées en dollars)
CRYPTOS = {
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana",
    "BNB-USD": "BNB", "XRP-USD": "XRP", "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin", "AVAX-USD": "Avalanche", "LINK-USD": "Chainlink",
    "DOT-USD": "Polkadot", "LTC-USD": "Litecoin", "BCH-USD": "Bitcoin Cash",
    "TRX-USD": "Tron", "XLM-USD": "Stellar", "NEAR-USD": "Near", "ATOM-USD": "Cosmos",
}

# --- Grandes actions européennes (hors France), cotées en euros
ACTIONS_EU = {
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Deutsche Telekom",
    "ADS.DE": "Adidas", "BMW.DE": "BMW", "MBG.DE": "Mercedes-Benz", "ASML.AS": "ASML",
    "INGA.AS": "ING", "ADYEN.AS": "Adyen", "PRX.AS": "Prosus", "IBE.MC": "Iberdrola",
    "ITX.MC": "Inditex", "SAN.MC": "Banco Santander", "ENEL.MI": "Enel", "RACE.MI": "Ferrari",
}

# --- ETF de référence (indices) : servent aussi de "marché" pour comparer
ETFS = {
    "SPY": "S&P 500 (ETF)", "QQQ": "Nasdaq 100 (ETF)", "CW8.PA": "MSCI World (ETF Amundi)",
    "^FCHI": "CAC 40 (indice)", "^STOXX50E": "Euro Stoxx 50 (indice)",
    "GLD": "Or (ETF SPDR Gold)", "SMH": "Semi-conducteurs (ETF VanEck)",
    "ICLN": "Énergie propre (ETF iShares)", "BOTZ": "Robotique et IA (ETF Global X)",
    "XLE": "Pétrole et gaz (ETF Energy Select)",
}

UNIVERS = {"fr": ACTIONS_FR, "eu": ACTIONS_EU, "us": ACTIONS_US, "crypto": CRYPTOS, "etf": ETFS}

# Titres utilisés UNIQUEMENT pour l'apprentissage de l'IA (pas affichés sur le site) :
# plus l'IA voit de situations différentes, moins elle se fait piéger par le hasard.
ENTRAINEMENT_SUPPLEMENTAIRE = {
    "us": ["ADBE", "ORCL", "CSCO", "PEP", "KO", "PG", "JNJ", "MRK", "PFE", "ABBV", "WMT", "HD", "MCD",
           "NKE", "BA", "CAT", "GE", "IBM", "QCOM", "TXN", "BAC", "WFC", "GS", "MS", "T", "VZ", "CVX",
           "COP", "SBUX", "UPS", "LMT", "HON", "AMAT", "MU", "PYPL", "UBER"],
    "fr": ["ENGI.PA", "VIE.PA", "SGO.PA", "LR.PA", "ML.PA", "PUB.PA", "ACA.PA", "BN.PA"],
    "eu": ["BAS.DE", "BAYN.DE", "MUV2.DE", "PHIA.AS", "AD.AS", "BBVA.MC", "UCG.MI", "ISP.MI"],
    "crypto": ["ETC-USD", "ALGO-USD", "FIL-USD", "HBAR-USD"],
}

MAX_APPRENTISSAGE_EN_LIGNE = 80   # titres d'apprentissage en plus, au maximum, lors des mises à jour en ligne


def entrainement_supplementaire() -> dict:
    """Titres d'apprentissage : la liste de base, plus ceux que l'entraînement approfondi
    (entrainement_ia.py) a prouvé utiles (historique/apprentissage.json)."""
    import json as _json
    out = {k: list(v) for k, v in ENTRAINEMENT_SUPPLEMENTAIRE.items()}
    try:
        with open(_os.path.join(DOSSIER_HISTORIQUE, "apprentissage.json"), encoding="utf-8") as f:
            extra = _json.load(f).get("tickers", {})
        deja = {t for v in out.values() for t in v}
        n = 0
        for marche, liste in extra.items():
            for t in liste:
                if isinstance(t, str) and len(t) <= 20 and t not in deja and n < MAX_APPRENTISSAGE_EN_LIGNE:
                    out.setdefault(marche, []).append(t); deja.add(t); n += 1
    except (OSError, ValueError, AttributeError):
        pass
    return out


# Indice de référence par marché (pour la force relative)
BENCHMARK = {"fr": "^FCHI", "eu": "^STOXX50E", "us": "SPY", "crypto": "BTC-USD", "etf": "SPY"}
NOM_BENCHMARK = {"^FCHI": "le CAC 40", "^STOXX50E": "l'Euro Stoxx 50", "SPY": "le S&P 500", "BTC-USD": "le Bitcoin"}


def benchmark_de(ticker: str, marche: str = "") -> str:
    """Indice de comparaison d'un titre (pour « fera-t-il mieux que son marché ? »)."""
    if ticker.endswith("-USD"):
        return "BTC-USD"
    if ticker.endswith(".PA") or ticker == "^FCHI":
        return "^FCHI"
    if ticker.endswith((".DE", ".AS", ".MC", ".MI")) or ticker == "^STOXX50E":
        return "^STOXX50E"
    return BENCHMARK.get(marche, "SPY")

HISTORIQUE = "25y"          # tout l'historique disponible (jusqu'à 25 ans) : plus de situations vécues = IA plus robuste
HORIZON_PREDICTION = 20     # le modèle prédit la direction sur N séances (~1 mois)
FRAIS_PAR_ORDRE = 0.001     # 0,1 % de frais par achat/vente dans les backtests
DOSSIER_CACHE = ".cache_cours"
DOSSIER_RAPPORTS = "rapports"
DOSSIER_SITE = "site"
DOSSIER_HISTORIQUE = "historique"

# --- Site en ligne -----------------------------------------------------------
import os as _os

# Durée de validité du cache des cours (heures). En ligne, le robot GitHub la met à 0,5 h.
CACHE_MAX_H = float(_os.environ.get("RADAR_CACHE_MAX_H", "12"))

# Clé gratuite Finnhub (finnhub.io) pour les cours US en direct. Laisse vide pour s'en passer.
# Sur GitHub, mets-la dans Settings → Secrets → Actions sous le nom FINNHUB_KEY.
FINNHUB_CLE = _os.environ.get("FINNHUB_KEY", "")

# Mentions légales : à compléter avant la mise en ligne (un pseudo suffit pour un particulier).
# Nom de domaine personnalisé (facultatif), ex : radarbourse.fr
DOMAINE = _os.environ.get("RADAR_DOMAINE", "").strip().lower().removeprefix("https://").removeprefix("http://").strip("/")
if DOMAINE and not __import__("re").fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+", DOMAINE):
    DOMAINE = ""

EDITEUR = _os.environ.get("RADAR_EDITEUR", "maxitemmmm")
CONTACT = _os.environ.get("RADAR_CONTACT", "https://github.com/maxitemmmm-eng/radar-bourse/issues")

# Conflits d'intérêts (obligation de transparence pour qui publie des avis sur des cours).
# Décris honnêtement ta situation, par exemple : « L'éditeur détient des actions Apple. »
CONFLITS = _os.environ.get("RADAR_CONFLITS",
    "L'éditeur ne perçoit aucune rémunération liée aux titres présentés. Les signaux sont "
    "générés automatiquement, sans intervention manuelle sur un titre en particulier. "
    "L'éditeur peut détenir à titre personnel certains des instruments mentionnés.")

# Chaîne Telegram publique des alertes (ex : @radar_bourse_alertes), affichée sur le site.
TELEGRAM_CHAINE = _os.environ.get("TELEGRAM_CHAINE", "")

# Statistiques de visites privées (GoatCounter, sans cookies). Code du compte, ex : « radarbourse »
# pour un tableau de bord à l'adresse https://radarbourse.goatcounter.com (visible par toi seule).
GOATCOUNTER = _os.environ.get("GOATCOUNTER_CODE", "").strip().lower()
if GOATCOUNTER and not __import__("re").fullmatch(r"[a-z0-9][a-z0-9-]{1,48}", GOATCOUNTER):
    GOATCOUNTER = ""
