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
    "DOT-USD": "Polkadot",
}

# --- ETF de référence (indices) : servent aussi de "marché" pour comparer
ETFS = {
    "SPY": "S&P 500 (ETF)", "QQQ": "Nasdaq 100 (ETF)", "CW8.PA": "MSCI World (ETF Amundi)",
    "^FCHI": "CAC 40 (indice)",
}

UNIVERS = {"fr": ACTIONS_FR, "us": ACTIONS_US, "crypto": CRYPTOS, "etf": ETFS}

# Indice de référence par marché (pour la force relative)
BENCHMARK = {"fr": "^FCHI", "us": "SPY", "crypto": "BTC-USD", "etf": "SPY"}

HISTORIQUE = "5y"           # profondeur d'historique téléchargée
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
EDITEUR = _os.environ.get("RADAR_EDITEUR", "maxitemmmm")
CONTACT = _os.environ.get("RADAR_CONTACT", "https://github.com/maxitemmmm-eng/radar-bourse/issues")
