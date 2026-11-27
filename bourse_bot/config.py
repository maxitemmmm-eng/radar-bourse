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
    # ajoutées en version 71 : 45 cryptos de plus, cours pris chez Binance (puis CryptoCompare) pour éviter les homonymes de Yahoo.
    # Une crypto sans au moins un an d'historique fiable est écartée automatiquement par le contrôle qualité.
    "AR-USD": "Arweave", "SNX-USD": "Synthetix", "CAKE-USD": "PancakeSwap", "1INCH-USD": "1inch", "ENS-USD": "Ethereum Name Service", "CHZ-USD": "Chiliz", "EGLD-USD": "MultiversX", "FLOW-USD": "Flow", "KAVA-USD": "Kava", "MINA-USD": "Mina", "NEO-USD": "NEO", "IOTA-USD": "IOTA", "ZIL-USD": "Zilliqa", "QTUM-USD": "Qtum", "BAT-USD": "Basic Attention Token", "ENJ-USD": "Enjin Coin", "ZRX-USD": "0x", "ANKR-USD": "Ankr", "ROSE-USD": "Oasis", "CFX-USD": "Conflux", "CELO-USD": "Celo", "KSM-USD": "Kusama", "RVN-USD": "Ravencoin", "ICX-USD": "ICON", "LRC-USD": "Loopring", "YFI-USD": "yearn.finance", "SUSHI-USD": "SushiSwap", "JASMY-USD": "JasmyCoin", "PENDLE-USD": "Pendle", "ORDI-USD": "ORDI", "CKB-USD": "Nervos Network", "ASTR-USD": "Astar", "LPT-USD": "Livepeer", "PAXG-USD": "PAX Gold", "TWT-USD": "Trust Wallet Token", "IOTX-USD": "IoTeX", "ZEN-USD": "Horizen", "TRB-USD": "Tellor", "BLUR-USD": "Blur", "CVX-USD": "Convex Finance", "SKL-USD": "SKALE", "DYDX-USD": "dYdX", "GMX-USD": "GMX", "APE-USD": "ApeCoin", "JTO-USD": "Jito",
    # version 93 : 119 cryptos de plus, toutes vérifiées le 18/11/2026 : cotées en direct chez Binance (paire USDT active) avec plus d'un an d'historique.
    # Cours pris chez Binance puis CryptoCompare (jamais chez Yahoo : symboles ambigus). Le contrôle qualité écarte toute série douteuse.
    "ZRO-USD": "LayerZero", "W-USD": "Wormhole", "ZK-USD": "ZKsync", "ETHFI-USD": "ether.fi", "TRUMP-USD": "Official Trump", "PUMP-USD": "Pump.fun", "ASTER-USD": "Aster", "WLFI-USD": "World Liberty Financial", "XPL-USD": "Plasma", "HUMA-USD": "Huma Finance", "SOPH-USD": "Sophon", "SHELL-USD": "MyShell", "USUAL-USD": "Usual", "LUNC-USD": "Terra Classic", "LUNA-USD": "Terra", "TLM-USD": "Alien Worlds", "JST-USD": "JUST", "INIT-USD": "Initia", "ONE-USD": "Harmony", "RARE-USD": "SuperRare", "PLUME-USD": "Plume", "RAY-USD": "Raydium", "STEEM-USD": "Steem", "VIRTUAL-USD": "Virtuals Protocol", "PHA-USD": "Phala Network", "S-USD": "Sonic (ex-Fantom)", "RLC-USD": "iExec RLC", "PROM-USD": "Prom", "DODO-USD": "DODO", "KMNO-USD": "Kamino", "ALT-USD": "AltLayer", "IO-USD": "io.net", "WCT-USD": "WalletConnect", "VANA-USD": "Vana", "BEAMX-USD": "Beam", "MORPHO-USD": "Morpho", "CYBER-USD": "Cyber", "LINEA-USD": "Linea", "BOME-USD": "Book of Meme", "NEIRO-USD": "Neiro", "SAGA-USD": "Saga", "SKY-USD": "Sky (ex-Maker)", "0G-USD": "0G", "GTC-USD": "Gitcoin", "EIGEN-USD": "EigenLayer", "SUPER-USD": "SuperVerse", "KAITO-USD": "Kaito", "DEXE-USD": "DeXe", "NEXO-USD": "Nexo", "ME-USD": "Magic Eden", "KAIA-USD": "Kaia", "COOKIE-USD": "Cookie DAO", "HYPER-USD": "Hyperlane", "GLMR-USD": "Moonbeam", "LSK-USD": "Lisk", "COMP-USD": "Compound", "AUDIO-USD": "Audius", "HOT-USD": "Holo", "ONT-USD": "Ontology", "MASK-USD": "Mask Network", "API3-USD": "API3", "ARKM-USD": "Arkham", "ID-USD": "Space ID", "MAGIC-USD": "Treasure (MAGIC)", "GMT-USD": "STEPN", "KNC-USD": "Kyber Network", "CELR-USD": "Celer Network", "COTI-USD": "COTI", "RSR-USD": "Reserve Rights", "ACH-USD": "Alchemy Pay", "XEC-USD": "eCash", "DGB-USD": "DigiByte", "SC-USD": "Siacoin", "UMA-USD": "UMA", "NMR-USD": "Numeraire", "METIS-USD": "Metis", "PEOPLE-USD": "ConstitutionDAO", "MEME-USD": "Memecoin", "NOT-USD": "Notcoin", "DOGS-USD": "Dogs", "TURBO-USD": "Turbo", "PNUT-USD": "Peanut the Squirrel", "ACT-USD": "Act I : The AI Prophecy", "MOVE-USD": "Movement", "BIO-USD": "Bio Protocol", "LAYER-USD": "Solayer", "BERA-USD": "Berachain", "SSV-USD": "ssv.network", "AEVO-USD": "Aevo", "MANTA-USD": "Manta Network", "DYM-USD": "Dymension", "XAI-USD": "Xai", "PIXEL-USD": "Pixels", "PORTAL-USD": "Portal", "TNSR-USD": "Tensor", "REZ-USD": "Renzo", "JOE-USD": "JOE (Trader Joe)", "C98-USD": "Coin98", "ALICE-USD": "My Neighbor Alice", "GLM-USD": "Golem", "CTSI-USD": "Cartesi", "OGN-USD": "Origin Protocol", "ILV-USD": "Illuvium", "YGG-USD": "Yield Guild Games", "RONIN-USD": "Ronin", "BICO-USD": "Biconomy", "LQTY-USD": "Liquity", "EDU-USD": "Open Campus", "CHR-USD": "Chromia", "POLYX-USD": "Polymesh", "MOVR-USD": "Moonriver", "XVG-USD": "Verge", "IOST-USD": "IOST", "STRAX-USD": "Stratis", "ORCA-USD": "Orca", "HMSTR-USD": "Hamster Kombat", "SCR-USD": "Scroll", "BANANA-USD": "Banana Gun", "LISTA-USD": "Lista DAO",
    # version 116 : des cryptos célèbres absentes de Binance (ou trop récentes chez Binance) : cours pris chez CryptoCompare
    "HYPE-USD": "Hyperliquid", "LEO-USD": "UNUS SED LEO (Bitfinex)", "OKB-USD": "OKB", "CRO-USD": "Cronos", "MNT-USD": "Mantle", "BGB-USD": "Bitget Token", "KCS-USD": "KuCoin Token", "GT-USD": "GateToken", "XDC-USD": "XDC Network", "FLR-USD": "Flare", "PI-USD": "Pi Network", "AERO-USD": "Aerodrome Finance", "FARTCOIN-USD": "Fartcoin", "BRETT-USD": "Brett", "POPCAT-USD": "Popcat", "HNT-USD": "Helium", "BSV-USD": "Bitcoin SV", "AKT-USD": "Akash Network", "MEW-USD": "cat in a dogs world", "SPX-USD": "SPX6900",
    # version 114 : 125 cryptos de plus, vérifiées le 27/11/2026 sur Binance (paire USDT active, plus d'un an d'historique,
    # au moins 50 000 $ échangés par jour). Cours pris chez Binance puis CryptoCompare. Le contrôle qualité écarte toute série douteuse.
    "HAEDAL-USD": "Haedal Protocol", "BIGTIME-USD": "Big Time", "YB-USD": "YieldBasis", "2Z-USD": "DoubleZero", "SPK-USD": "Spark", "RIF-USD": "Rootstock (RIF)", "SYRUP-USD": "Maple Finance (Syrup)", "TFUEL-USD": "Theta Fuel", "MUBARAK-USD": "Mubarak", "STO-USD": "StakeStone", "ACE-USD": "Fusionist (ACE)", "CVC-USD": "Civic", "BABY-USD": "Babylon", "BMT-USD": "Bubblemaps", "ENSO-USD": "Enso", "ATM-USD": "Atlético de Madrid Fan Token", "AVA-USD": "AVA (Travala)", "SAHARA-USD": "Sahara AI", "QI-USD": "BENQI", "ANIME-USD": "Animecoin", "ERA-USD": "Caldera", "SOMI-USD": "Somnia", "FF-USD": "Falcon Finance", "NOM-USD": "Nomina", "BB-USD": "BounceBit", "GIGGLE-USD": "Giggle Fund", "NIL-USD": "Nillion", "KERNEL-USD": "KernelDAO", "SXT-USD": "Space and Time", "1000CHEEMS-USD": "Cheems", "AIXBT-USD": "aixbt", "BARD-USD": "Lombard", "TUT-USD": "Tutorial", "LA-USD": "Lagrange", "MITO-USD": "Mitosis", "AVNT-USD": "Avantis", "OPEN-USD": "OpenLedger", "AMP-USD": "Amp", "TST-USD": "Test (TST)", "SIGN-USD": "Sign", "LUMIA-USD": "Lumia", "WAXP-USD": "WAX", "SOLV-USD": "Solv Protocol", "F-USD": "SynFutures", "CETUS-USD": "Cetus Protocol", "HEMI-USD": "Hemi", "PARTI-USD": "Particle Network", "GUN-USD": "GUNZ", "NXPC-USD": "Nexpace", "WAL-USD": "Walrus", "ADX-USD": "AdEx", "HEI-USD": "Heima", "FORM-USD": "Four (FORM)", "ONG-USD": "Ontology Gas", "MBL-USD": "MovieBloc", "BROCCOLI714-USD": "Broccoli", "TOWNS-USD": "Towns", "BTTC-USD": "BitTorrent", "RPL-USD": "Rocket Pool", "ARK-USD": "Ark", "G-USD": "Gravity", "ZBT-USD": "ZEROBASE", "HOME-USD": "DeFi App (HOME)", "AWE-USD": "AWE Network", "THE-USD": "THENA", "EDEN-USD": "OpenEden", "COW-USD": "CoW Protocol", "EUL-USD": "Euler", "GAS-USD": "Gas (NEO)", "TREE-USD": "Treehouse", "REQ-USD": "Request", "MIRA-USD": "Mira Network", "C-USD": "Chainbase", "OG-USD": "OG Fan Token", "RAD-USD": "Radworks", "AXL-USD": "Axelar", "SYN-USD": "Synapse", "TKO-USD": "Tokocrypto", "BAR-USD": "FC Barcelona Fan Token", "HIVE-USD": "Hive", "GPS-USD": "GoPlus Security", "PSG-USD": "Paris Saint-Germain Fan Token", "ZKC-USD": "Boundless", "PROVE-USD": "Succinct", "WIN-USD": "WINkLink", "CITY-USD": "Manchester City Fan Token", "RED-USD": "RedStone", "JUV-USD": "Juventus Fan Token", "CATI-USD": "Catizen", "DCR-USD": "Decred", "RESOLV-USD": "Resolv", "SUN-USD": "Sun (Tron)", "PORTO-USD": "FC Porto Fan Token", "VTHO-USD": "VeThor Token", "T-USD": "Threshold", "ASR-USD": "AS Roma Fan Token", "1MBABYDOGE-USD": "Baby Doge Coin", "1000SATS-USD": "SATS (Ordinals)", "POWR-USD": "Powerledger", "CGPT-USD": "ChainGPT", "AI-USD": "Sleepless AI", "ACM-USD": "AC Milan Fan Token", "FTT-USD": "FTX Token", "BANANAS31-USD": "Banana For Scale", "OSMO-USD": "Osmosis", "1000CAT-USD": "Simon's Cat", "DUSK-USD": "Dusk", "FLUX-USD": "Flux", "TURTLE-USD": "Turtle", "NEWT-USD": "Newton Protocol", "GNS-USD": "Gains Network", "XNO-USD": "Nano", "FIDA-USD": "Bonfida", "WOO-USD": "WOO", "BAND-USD": "Band Protocol", "PUNDIX-USD": "Pundi X", "ARPA-USD": "ARPA", "SLP-USD": "Smooth Love Potion", "AUCTION-USD": "Bounce Token", "BEL-USD": "Bella Protocol", "LAZIO-USD": "Lazio Fan Token", "XVS-USD": "Venus", "HOLO-USD": "Holoworld AI", "AGLD-USD": "Adventure Gold", "MTL-USD": "Metal DAO", "QKC-USD": "QuarkChain", "ALPINE-USD": "Alpine F1 Team Fan Token",
}
CRYPTOS_V114 = {"C98-USD", "HYPE-USD", "LEO-USD", "OKB-USD", "CRO-USD", "MNT-USD", "BGB-USD", "KCS-USD", "GT-USD", "XDC-USD", "FLR-USD", "PI-USD", "AERO-USD", "FARTCOIN-USD", "BRETT-USD", "POPCAT-USD", "HNT-USD", "BSV-USD", "AKT-USD", "MEW-USD", "SPX-USD", "HAEDAL-USD", "BIGTIME-USD", "YB-USD", "2Z-USD", "SPK-USD", "RIF-USD", "SYRUP-USD", "TFUEL-USD", "MUBARAK-USD", "STO-USD", "ACE-USD", "CVC-USD", "BABY-USD", "BMT-USD", "ENSO-USD", "ATM-USD", "AVA-USD", "SAHARA-USD", "QI-USD", "ANIME-USD", "ERA-USD", "SOMI-USD", "FF-USD", "NOM-USD", "BB-USD", "GIGGLE-USD", "NIL-USD", "KERNEL-USD", "SXT-USD", "1000CHEEMS-USD", "AIXBT-USD", "BARD-USD", "TUT-USD", "LA-USD", "MITO-USD", "AVNT-USD", "OPEN-USD", "AMP-USD", "TST-USD", "SIGN-USD", "LUMIA-USD", "WAXP-USD", "SOLV-USD", "F-USD", "CETUS-USD", "HEMI-USD", "PARTI-USD", "GUN-USD", "NXPC-USD", "WAL-USD", "ADX-USD", "HEI-USD", "FORM-USD", "ONG-USD", "MBL-USD", "BROCCOLI714-USD", "TOWNS-USD", "BTTC-USD", "RPL-USD", "ARK-USD", "G-USD", "ZBT-USD", "HOME-USD", "AWE-USD", "THE-USD", "EDEN-USD", "COW-USD", "EUL-USD", "GAS-USD", "TREE-USD", "REQ-USD", "MIRA-USD", "C-USD", "OG-USD", "RAD-USD", "AXL-USD", "SYN-USD", "TKO-USD", "BAR-USD", "HIVE-USD", "GPS-USD", "PSG-USD", "ZKC-USD", "PROVE-USD", "WIN-USD", "CITY-USD", "RED-USD", "JUV-USD", "CATI-USD", "DCR-USD", "RESOLV-USD", "SUN-USD", "PORTO-USD", "VTHO-USD", "T-USD", "ASR-USD", "1MBABYDOGE-USD", "1000SATS-USD", "POWR-USD", "CGPT-USD", "AI-USD", "ACM-USD", "FTT-USD", "BANANAS31-USD", "OSMO-USD", "1000CAT-USD", "DUSK-USD", "FLUX-USD", "TURTLE-USD", "NEWT-USD", "GNS-USD", "XNO-USD", "FIDA-USD", "WOO-USD", "BAND-USD", "PUNDIX-USD", "ARPA-USD", "SLP-USD", "AUCTION-USD", "BEL-USD", "LAZIO-USD", "XVS-USD", "HOLO-USD", "AGLD-USD", "MTL-USD", "QKC-USD", "ALPINE-USD"}
CRYPTOS_SANS_YAHOO = {"TON11419-USD", "OP-USD", "POL-USD", "STX-USD", "IMX-USD", "LDO-USD", "FET-USD", "GRT-USD", "SEI-USD", "TIA-USD",
                      "JUP-USD", "WIF-USD", "BONK-USD", "FLOKI-USD", "WLD-USD", "PYTH-USD", "STRK-USD", "GALA-USD",
                      "AXS-USD", "CRV-USD", "RUNE-USD"} | {"AR-USD", "SNX-USD", "CAKE-USD", "1INCH-USD", "ENS-USD", "CHZ-USD", "EGLD-USD", "FLOW-USD", "KAVA-USD", "MINA-USD", "NEO-USD", "IOTA-USD", "ZIL-USD", "QTUM-USD", "BAT-USD", "ENJ-USD", "ZRX-USD", "ANKR-USD", "ROSE-USD", "CFX-USD", "CELO-USD", "KSM-USD", "RVN-USD", "ICX-USD", "LRC-USD", "YFI-USD", "SUSHI-USD", "JASMY-USD", "PENDLE-USD", "ORDI-USD", "CKB-USD", "ASTR-USD", "LPT-USD", "PAXG-USD", "TWT-USD", "IOTX-USD", "ZEN-USD", "TRB-USD", "BLUR-USD", "CVX-USD", "SKL-USD", "DYDX-USD", "GMX-USD", "APE-USD", "JTO-USD"} | {"ZRO-USD", "W-USD", "ZK-USD", "ETHFI-USD", "TRUMP-USD", "PUMP-USD", "ASTER-USD", "WLFI-USD", "XPL-USD", "HUMA-USD", "SOPH-USD", "SHELL-USD", "USUAL-USD", "LUNC-USD", "LUNA-USD", "TLM-USD", "JST-USD", "INIT-USD", "ONE-USD", "RARE-USD", "PLUME-USD", "RAY-USD", "STEEM-USD", "VIRTUAL-USD", "PHA-USD", "S-USD", "RLC-USD", "PROM-USD", "DODO-USD", "KMNO-USD", "ALT-USD", "IO-USD", "WCT-USD", "VANA-USD", "BEAMX-USD", "MORPHO-USD", "CYBER-USD", "LINEA-USD", "BOME-USD", "NEIRO-USD", "SAGA-USD", "SKY-USD", "0G-USD", "GTC-USD", "EIGEN-USD", "SUPER-USD", "KAITO-USD", "DEXE-USD", "NEXO-USD", "ME-USD", "KAIA-USD", "COOKIE-USD", "HYPER-USD", "GLMR-USD", "LSK-USD", "COMP-USD", "AUDIO-USD", "HOT-USD", "ONT-USD", "MASK-USD", "API3-USD", "ARKM-USD", "ID-USD", "MAGIC-USD", "GMT-USD", "KNC-USD", "CELR-USD", "COTI-USD", "RSR-USD", "ACH-USD", "XEC-USD", "DGB-USD", "SC-USD", "UMA-USD", "NMR-USD", "METIS-USD", "PEOPLE-USD", "MEME-USD", "NOT-USD", "DOGS-USD", "TURBO-USD", "PNUT-USD", "ACT-USD", "MOVE-USD", "BIO-USD", "LAYER-USD", "BERA-USD", "SSV-USD", "AEVO-USD", "MANTA-USD", "DYM-USD", "XAI-USD", "PIXEL-USD", "PORTAL-USD", "TNSR-USD", "REZ-USD", "JOE-USD", "C98-USD", "ALICE-USD", "GLM-USD", "CTSI-USD", "OGN-USD", "ILV-USD", "YGG-USD", "RONIN-USD", "BICO-USD", "LQTY-USD", "EDU-USD", "CHR-USD", "POLYX-USD", "MOVR-USD", "XVG-USD", "IOST-USD", "STRAX-USD", "ORCA-USD", "HMSTR-USD", "SCR-USD", "BANANA-USD", "LISTA-USD"} | CRYPTOS_V114


# version 93 : autres noms sous lesquels les gens cherchent une crypto (anciens noms, surnoms) : ajoutés aux mots-clés de sa fiche
ALIAS_CRYPTO = {
    "S-USD": ["Fantom", "FTM", "Sonic crypto"], "SKY-USD": ["Maker", "MKR", "MakerDAO"], "POL-USD": ["Matic", "Polygon Matic"],
    "LUNC-USD": ["Terra Luna Classic", "LUNC"], "LUNA-USD": ["Terra 2.0", "Terra Luna"], "FET-USD": ["ASI Alliance", "Artificial Superintelligence Alliance"],
    "RENDER-USD": ["RNDR"], "TON11419-USD": ["TON", "Telegram crypto"], "BEAMX-USD": ["Beam crypto"], "PNUT-USD": ["PNUT"],
    "TRUMP-USD": ["Trump coin", "memecoin Trump", "$TRUMP"], "WLFI-USD": ["WLFI", "crypto Trump World Liberty"], "PUMP-USD": ["pump fun", "PUMP"],
    "ZK-USD": ["zkSync Era"], "EIGEN-USD": ["Eigen", "restaking"], "ETHFI-USD": ["etherfi"], "HMSTR-USD": ["Hamster", "HMSTR"],
    "NOT-USD": ["Notcoin Telegram"], "DOGS-USD": ["Dogs Telegram"], "VIRTUAL-USD": ["Virtuals", "agents IA crypto"], "KAITO-USD": ["Kaito AI"],
    "IO-USD": ["io net"], "0G-USD": ["Zero Gravity"],
    # version 114 : surnoms et anciens noms des nouvelles cryptos
    "PSG-USD": ["jeton PSG", "crypto PSG", "PSG fan token", "Socios PSG"], "BAR-USD": ["jeton Barça", "crypto FC Barcelone"],
    "CITY-USD": ["jeton Manchester City"], "JUV-USD": ["jeton Juventus"], "ACM-USD": ["jeton AC Milan"], "ASR-USD": ["jeton AS Roma"],
    "ATM-USD": ["jeton Atlético Madrid"], "PORTO-USD": ["jeton FC Porto"], "LAZIO-USD": ["jeton Lazio"], "ALPINE-USD": ["jeton Alpine F1"],
    "OG-USD": ["OG esports"], "WAXP-USD": ["WAX", "WAXP"], "BTTC-USD": ["BitTorrent", "BTT"], "XNO-USD": ["Nano", "XNO"],
    "FTT-USD": ["FTX", "FTT"], "GAS-USD": ["NeoGas"], "SUN-USD": ["SUN crypto"], "1MBABYDOGE-USD": ["Baby Doge", "BabyDoge"],
    "1000SATS-USD": ["SATS", "Ordinals SATS"], "1000CAT-USD": ["Simons Cat"], "1000CHEEMS-USD": ["Cheems"], "BROCCOLI714-USD": ["Broccoli CZ"],
    "SYRUP-USD": ["Maple", "Syrup"], "RIF-USD": ["Rootstock", "RSK"], "THE-USD": ["Thena"], "G-USD": ["Gravity crypto", "Galxe"],
    "T-USD": ["Threshold Network"], "C-USD": ["Chainbase crypto"], "AI-USD": ["Sleepless AI"], "F-USD": ["SynFutures"],
    "HAEDAL-USD": ["Haedal"], "LEO-USD": ["Bitfinex LEO", "LEO token"], "CRO-USD": ["Crypto.com", "Crypto.com coin", "CRO"],
    "OKB-USD": ["OKX token", "OKB OKX"], "BGB-USD": ["Bitget", "BGB"], "KCS-USD": ["KuCoin", "KCS"], "GT-USD": ["Gate.io", "Gate token"],
    "HYPE-USD": ["Hyperliquid HYPE", "HYPE crypto"], "PI-USD": ["Pi Network crypto", "Pi coin", "Pi"], "MNT-USD": ["Mantle crypto"],
    "SPX-USD": ["SPX6900 memecoin"], "BSV-USD": ["BSV", "Bitcoin Satoshi Vision"], "HNT-USD": ["Helium crypto"], "BABY-USD": ["Babylon Bitcoin staking"], "WAL-USD": ["Walrus Sui"], "XVS-USD": ["Venus Protocol"], "PEPE24478-USD": ["PEPE"], "SHIB-USD": ["SHIB"], "DOGE-USD": ["DOGE"],
}


def symbole_binance(ticker: str) -> str:
    """BTC-USD → BTCUSDT ; UNI7083-USD → UNIUSDT (on retire le numéro propre à Yahoo)."""
    import re as _re
    # version 114 : seuls les numéros de Yahoo (4 chiffres ou plus : UNI7083, TON11419…) sont retirés. Avant, API3 devenait
    # « API » et C98 devenait « C » (une autre crypto, Chainbase) : leurs cours étaient faux ou absents.
    return _re.sub(r"\d{4,}$", "", ticker[:-4]) + "USDT"

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
    # version 103 : l'or en direct (cours de l'once en dollars, contrat à terme le plus proche) et les grandes Bourses du
    # monde qui manquaient, suivies par un ETF coté en dollars (achetable, compatible portefeuille virtuel).
    "GC=F": "Or (once, cours en dollars)",
    "ASHR": "Chine continentale, Shanghai et Shenzhen (ETF Xtrackers CSI 300)", "EWH": "Hong Kong (ETF iShares)",
    "EWU": "Royaume-Uni, Bourse de Londres (ETF iShares)", "EWC": "Canada, Bourse de Toronto (ETF iShares)",
    "EWG": "Allemagne, Bourse de Francfort (ETF iShares)", "EWT": "Taïwan (ETF iShares)", "EWY": "Corée du Sud (ETF iShares)",
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

# Version 103 : fils de discussion (Giscus, gratuit, open source : les messages sont stockés dans les « Discussions » du dépôt
# GitHub, modérables par toi). Vides = pas de discussions affichées. Voir TUTO_DISCUSSIONS.md.
GISCUS = {"repo": _os.environ.get("GISCUS_REPO", "").strip(), "repo_id": _os.environ.get("GISCUS_REPO_ID", "").strip(),
          "categorie_id": _os.environ.get("GISCUS_CATEGORY_ID", "").strip()}

# Version 108 : lien discret « Soutenir le projet » (dons libres, sans contrepartie, sans entreprise). Vide = rien d'affiché.
# Seules des plateformes de dons connues sont acceptées (sécurité : jamais un lien arbitraire).
def _soutien():
    import re as _r
    u = _os.environ.get("RADAR_SOUTIEN", "").strip() or "https://ko-fi.com/supporteradarbourse"   # page Ko-fi de l'éditrice
    ok = _r.fullmatch(r"https://(www\.)?(ko-fi\.com|tipeee\.com|fr\.tipeee\.com|en\.tipeee\.com|buymeacoffee\.com|liberapay\.com|paypal\.me)/[A-Za-z0-9_.\-/]{1,80}", u)
    return u if ok else ""


SOUTIEN = _soutien()
