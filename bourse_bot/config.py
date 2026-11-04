"""Configuration : univers de titres suivis et paramètres globaux."""

# --- Actions françaises (principales valeurs du CAC 40, suffixe .PA = Euronext Paris)
ACTIONS_FR = {
    "MC.PA": "LVMH", "OR.PA": "L'Oréal", "TTE.PA": "TotalEnergies", "SAN.PA": "Sanofi",
    "AIR.PA": "Airbus", "SU.PA": "Schneider Electric", "AI.PA": "Air Liquide",
    "BNP.PA": "BNP Paribas", "RMS.PA": "Hermès", "EL.PA": "EssilorLuxottica",
    "SAF.PA": "Safran", "CS.PA": "AXA", "DG.PA": "Vinci", "KER.PA": "Kering",
    "STLAP.PA": "Stellantis", "GLE.PA": "Société Générale", "CAP.PA": "Capgemini",
    "DSY.PA": "Dassault Systèmes", "ORA.PA": "Orange", "RI.PA": "Pernod Ricard",
    # ajoutées en version 33 : les autres grandes valeurs de la Bourse de Paris
    "ENGI.PA": "Engie", "VIE.PA": "Veolia", "SGO.PA": "Saint-Gobain", "LR.PA": "Legrand",
    "ML.PA": "Michelin", "PUB.PA": "Publicis", "ACA.PA": "Crédit Agricole", "BN.PA": "Danone",
    "HO.PA": "Thales", "EN.PA": "Bouygues", "STMPA.PA": "STMicroelectronics", "RNO.PA": "Renault",
    "AC.PA": "Accor", "ERF.PA": "Eurofins Scientific", "TEP.PA": "Teleperformance", "URW.PA": "Unibail-Rodamco-Westfield",
    "BVI.PA": "Bureau Veritas", "AM.PA": "Dassault Aviation", "SOI.PA": "Soitec", "UBI.PA": "Ubisoft",
    # ajoutées en version 63 (SBF 120)
    "ALO.PA": "Alstom", "CA.PA": "Carrefour", "FR.PA": "Valeo", "SW.PA": "Sodexo", "EDEN.PA": "Edenred",
    "AF.PA": "Air France-KLM", "VK.PA": "Vallourec", "FGR.PA": "Eiffage", "RXL.PA": "Rexel", "BIM.PA": "bioMérieux",
    "GET.PA": "Getlink", "AMUN.PA": "Amundi",
}

# --- Actions américaines (grandes capitalisations)
ACTIONS_US = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "JPM": "JPMorgan", "V": "Visa", "NFLX": "Netflix", "AMD": "AMD",
    "PLTR": "Palantir", "COST": "Costco", "LLY": "Eli Lilly", "XOM": "ExxonMobil",
    "UNH": "UnitedHealth", "CRM": "Salesforce", "INTC": "Intel", "DIS": "Disney",
    # ajoutées en version 33 (elles servaient déjà à l'apprentissage de l'IA)
    "ADBE": "Adobe", "ORCL": "Oracle", "CSCO": "Cisco", "PEP": "PepsiCo", "KO": "Coca-Cola",
    "PG": "Procter & Gamble", "JNJ": "Johnson & Johnson", "MRK": "Merck", "PFE": "Pfizer", "ABBV": "AbbVie",
    "WMT": "Walmart", "HD": "Home Depot", "MCD": "McDonald's", "NKE": "Nike", "BA": "Boeing",
    "CAT": "Caterpillar", "GE": "GE Aerospace", "IBM": "IBM", "QCOM": "Qualcomm", "TXN": "Texas Instruments",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs", "MS": "Morgan Stanley",
    "T": "AT&T", "VZ": "Verizon", "CVX": "Chevron", "COP": "ConocoPhillips", "SBUX": "Starbucks",
    "UPS": "UPS", "LMT": "Lockheed Martin", "HON": "Honeywell", "AMAT": "Applied Materials", "MU": "Micron",
    "PYPL": "PayPal", "UBER": "Uber", "MA": "Mastercard", "BRK-B": "Berkshire Hathaway", "COIN": "Coinbase",
    "MSTR": "Strategy (MicroStrategy)",
    # ajoutées en version 63
    "ABT": "Abbott", "TMO": "Thermo Fisher", "LIN": "Linde", "ACN": "Accenture", "NOW": "ServiceNow",
    "INTU": "Intuit", "AMGN": "Amgen", "ISRG": "Intuitive Surgical", "BKNG": "Booking Holdings", "SPGI": "S&P Global",
    "BLK": "BlackRock", "C": "Citigroup", "AXP": "American Express", "PM": "Philip Morris", "NEE": "NextEra Energy",
    "LOW": "Lowe's", "RTX": "RTX (Raytheon)", "DE": "Deere & Company", "PANW": "Palo Alto Networks", "ABNB": "Airbnb",
}

# --- Cryptomonnaies principales (cotées en dollars)
CRYPTOS = {
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana",
    "BNB-USD": "BNB", "XRP-USD": "XRP", "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin", "AVAX-USD": "Avalanche", "LINK-USD": "Chainlink",
    "DOT-USD": "Polkadot", "LTC-USD": "Litecoin", "BCH-USD": "Bitcoin Cash",
    "TRX-USD": "Tron", "XLM-USD": "Stellar", "NEAR-USD": "Near", "ATOM-USD": "Cosmos",
    # ajoutées en version 26 (cryptos établies, présentes sur Yahoo Finance et Binance).
    # Les numéros après certains symboles sont ceux de Yahoo, qui distingue ainsi des jetons homonymes.
    "TON11419-USD": "Toncoin", "SHIB-USD": "Shiba Inu", "UNI7083-USD": "Uniswap", "ICP-USD": "Internet Computer",
    "ETC-USD": "Ethereum Classic", "HBAR-USD": "Hedera", "APT21794-USD": "Aptos", "SUI20947-USD": "Sui",
    "ARB11841-USD": "Arbitrum", "FIL-USD": "Filecoin", "AAVE-USD": "Aave", "ALGO-USD": "Algorand",
    "PEPE24478-USD": "Pepe", "INJ-USD": "Injective", "VET-USD": "VeChain",
    # ajoutées en version 47 (au moins un an d'historique chez Yahoo ; secours Binance puis CryptoCompare)
    "XMR-USD": "Monero", "KAS-USD": "Kaspa", "RENDER-USD": "Render", "TAO-USD": "Bittensor", "QNT-USD": "Quant",
    "XTZ-USD": "Tezos", "EOS-USD": "EOS", "ZEC-USD": "Zcash", "DASH-USD": "Dash", "ONDO-USD": "Ondo",
    "ENA-USD": "Ethena", "SAND-USD": "The Sandbox", "MANA-USD": "Decentraland", "THETA-USD": "Theta Network",
    "PENGU-USD": "Pudgy Penguins",
    # ajoutées en version 48 : cours pris directement chez Binance (puis CryptoCompare), pas chez Yahoo,
    # pour éviter les jetons homonymes (même symbole, autre crypto)
    "OP-USD": "Optimism", "POL-USD": "Polygon", "STX-USD": "Stacks", "IMX-USD": "Immutable", "LDO-USD": "Lido DAO",
    "FET-USD": "Fetch.ai (ASI)", "GRT-USD": "The Graph", "SEI-USD": "Sei", "TIA-USD": "Celestia", "JUP-USD": "Jupiter",
    "WIF-USD": "dogwifhat", "BONK-USD": "Bonk", "FLOKI-USD": "Floki", "WLD-USD": "Worldcoin", "PYTH-USD": "Pyth Network",
    "STRK-USD": "Starknet", "GALA-USD": "Gala", "AXS-USD": "Axie Infinity", "CRV-USD": "Curve DAO", "RUNE-USD": "THORChain",
}
CRYPTOS_SANS_YAHOO = {"TON11419-USD", "OP-USD", "POL-USD", "STX-USD", "IMX-USD", "LDO-USD", "FET-USD", "GRT-USD", "SEI-USD", "TIA-USD",
                      "JUP-USD", "WIF-USD", "BONK-USD", "FLOKI-USD", "WLD-USD", "PYTH-USD", "STRK-USD", "GALA-USD",
                      "AXS-USD", "CRV-USD", "RUNE-USD"}


def symbole_binance(ticker: str) -> str:
    """BTC-USD → BTCUSDT ; UNI7083-USD → UNIUSDT (on retire le numéro propre à Yahoo)."""
    import re as _re
    return _re.sub(r"\d+$", "", ticker[:-4]) + "USDT"

# --- Grandes actions européennes (hors France), cotées en euros
ACTIONS_EU = {
    "SAP.DE": "SAP", "SIE.DE": "Siemens", "ALV.DE": "Allianz", "DTE.DE": "Deutsche Telekom",
    "ADS.DE": "Adidas", "BMW.DE": "BMW", "MBG.DE": "Mercedes-Benz", "ASML.AS": "ASML",
    "INGA.AS": "ING", "ADYEN.AS": "Adyen", "PRX.AS": "Prosus", "IBE.MC": "Iberdrola",
    "ITX.MC": "Inditex", "SAN.MC": "Banco Santander", "ENEL.MI": "Enel", "RACE.MI": "Ferrari",
    # ajoutées en version 33
    "BAS.DE": "BASF", "BAYN.DE": "Bayer", "MUV2.DE": "Munich Re", "PHIA.AS": "Philips", "AD.AS": "Ahold Delhaize",
    "BBVA.MC": "BBVA", "UCG.MI": "UniCredit", "ISP.MI": "Intesa Sanpaolo", "RHM.DE": "Rheinmetall",
    "VOW3.DE": "Volkswagen", "IFX.DE": "Infineon",
    # ajoutées en version 63
    "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse", "DHL.DE": "DHL Group", "EOAN.DE": "E.ON", "RWE.DE": "RWE",
    "HEN3.DE": "Henkel", "BEI.DE": "Beiersdorf", "MRK.DE": "Merck KGaA", "ZAL.DE": "Zalando", "ENI.MI": "Eni",
    "NOKIA.HE": "Nokia", "ABI.BR": "AB InBev", "TEF.MC": "Telefónica", "HEIA.AS": "Heineken", "KBC.BR": "KBC",
}

# --- Version 63 : grandes entreprises du monde entier (hors Europe de l'euro), cotées à New York en dollars
# (actions ou certificats ADR) : même devise et mêmes horaires pour toutes, cours fiables sur des années.
# Pays d'origine : PAYS_MONDE (affiché sur la page du marché).
ACTIONS_MONDE = {
    "TSM": "TSMC", "TM": "Toyota", "SONY": "Sony", "NVO": "Novo Nordisk",
    "NVS": "Novartis", "AZN": "AstraZeneca", "SHEL": "Shell", "BP": "BP",
    "HSBC": "HSBC", "UL": "Unilever", "RIO": "Rio Tinto", "BHP": "BHP",
    "TD": "Toronto-Dominion Bank", "RY": "Royal Bank of Canada", "SHOP": "Shopify", "ENB": "Enbridge",
    "BABA": "Alibaba", "PDD": "PDD Holdings (Temu)", "JD": "JD.com", "BIDU": "Baidu",
    "TCEHY": "Tencent", "INFY": "Infosys", "HDB": "HDFC Bank", "IBN": "ICICI Bank",
    "MUFG": "Mitsubishi UFJ", "HMC": "Honda", "DEO": "Diageo", "GSK": "GSK",
    "BTI": "British American Tobacco", "ARM": "Arm Holdings", "SPOT": "Spotify",
    "MELI": "MercadoLibre", "NU": "Nubank", "VALE": "Vale", "PBR": "Petrobras",
    "SE": "Sea Limited",
}
PAYS_MONDE = {"TSM": "Taïwan", "TM": "Japon", "SONY": "Japon", "NVO": "Danemark", "NVS": "Suisse", "AZN": "Royaume-Uni", "SHEL": "Royaume-Uni",
              "BP": "Royaume-Uni", "HSBC": "Royaume-Uni", "UL": "Royaume-Uni", "RIO": "Royaume-Uni", "BHP": "Australie", "TD": "Canada",
              "RY": "Canada", "SHOP": "Canada", "ENB": "Canada", "BABA": "Chine", "PDD": "Chine", "JD": "Chine", "BIDU": "Chine",
              "TCEHY": "Chine", "INFY": "Inde", "HDB": "Inde", "IBN": "Inde", "MUFG": "Japon", "HMC": "Japon", "DEO": "Royaume-Uni",
              "GSK": "Royaume-Uni", "BTI": "Royaume-Uni", "ARM": "Royaume-Uni", "SPOT": "Suède", "MELI": "Amérique latine", "NU": "Brésil",
              "VALE": "Brésil", "PBR": "Brésil", "SE": "Singapour"}

# --- ETF de référence (indices) : servent aussi de "marché" pour comparer
ETFS = {
    "SPY": "S&P 500 (ETF)", "QQQ": "Nasdaq 100 (ETF)", "CW8.PA": "MSCI World (ETF Amundi)",
    "^FCHI": "CAC 40 (indice)", "^STOXX50E": "Euro Stoxx 50 (indice)",
    "GLD": "Or (ETF SPDR Gold)", "SMH": "Semi-conducteurs (ETF VanEck)",
    "ICLN": "Énergie propre (ETF iShares)", "BOTZ": "Robotique et IA (ETF Global X)",
    "XLE": "Pétrole et gaz (ETF Energy Select)",
    # ajoutés en version 63 : le reste du monde, les obligations et les matières premières
    "VEU": "Monde hors États-Unis (ETF Vanguard)", "EEM": "Pays émergents (ETF iShares)", "EWJ": "Japon (ETF iShares)",
    "FXI": "Chine grandes valeurs (ETF iShares)", "INDA": "Inde (ETF iShares)", "TLT": "Obligations US 20 ans (ETF iShares)",
    "IWM": "Petites entreprises US (ETF Russell 2000)", "DIA": "Dow Jones (ETF SPDR)", "SLV": "Argent métal (ETF iShares)",
    "VNQ": "Immobilier US (ETF Vanguard)",
}

UNIVERS = {"fr": ACTIONS_FR, "eu": ACTIONS_EU, "us": ACTIONS_US, "monde": ACTIONS_MONDE, "crypto": CRYPTOS, "etf": ETFS}

# suffixes Yahoo des places de la zone euro (cours en euros)
SUFFIXES_EURO = (".PA", ".AS", ".DE", ".MI", ".MC", ".BR", ".HE", ".LS", ".VI", ".IR")
SUFFIXES_EU = SUFFIXES_EURO[1:]

# Titres utilisés UNIQUEMENT pour l'apprentissage de l'IA (pas affichés sur le site) :
# plus l'IA voit de situations différentes, moins elle se fait piéger par le hasard.
ENTRAINEMENT_SUPPLEMENTAIRE = {
    "us": ["ADBE", "ORCL", "CSCO", "PEP", "KO", "PG", "JNJ", "MRK", "PFE", "ABBV", "WMT", "HD", "MCD",
           "NKE", "BA", "CAT", "GE", "IBM", "QCOM", "TXN", "BAC", "WFC", "GS", "MS", "T", "VZ", "CVX",
           "COP", "SBUX", "UPS", "LMT", "HON", "AMAT", "MU", "PYPL", "UBER"],
    "fr": ["ENGI.PA", "VIE.PA", "SGO.PA", "LR.PA", "ML.PA", "PUB.PA", "ACA.PA", "BN.PA"],
    "eu": ["BAS.DE", "BAYN.DE", "MUV2.DE", "PHIA.AS", "AD.AS", "BBVA.MC", "UCG.MI", "ISP.MI"],
    "crypto": [],   # XTZ, EOS, ZEC et DASH sont maintenant affichés sur le site (version 47)
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
BENCHMARK = {"fr": "^FCHI", "eu": "^STOXX50E", "us": "SPY", "monde": "VEU", "crypto": "BTC-USD", "etf": "SPY"}
NOM_BENCHMARK = {"^FCHI": "le CAC 40", "^STOXX50E": "l'Euro Stoxx 50", "SPY": "le S&P 500", "BTC-USD": "le Bitcoin", "VEU": "les actions mondiales hors USA"}


def benchmark_de(ticker: str, marche: str = "") -> str:
    """Indice de comparaison d'un titre (pour « fera-t-il mieux que son marché ? »)."""
    if ticker.endswith("-USD"):
        return "BTC-USD"
    if ticker.endswith(".PA") or ticker == "^FCHI":
        return "^FCHI"
    if ticker.endswith(SUFFIXES_EU) or ticker == "^STOXX50E":
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
