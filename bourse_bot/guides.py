"""Les guides du site (version 38) : réponses honnêtes aux recherches les plus tapées sur la Bourse et la crypto."""

CATEGORIES = {
    "debuter": "Débuter en Bourse",
    "argent": "Argent facile, trading et arnaques : la vérité",
    "crypto": "Cryptomonnaies",
    "marches": "Actions, ETF et marchés",
}

GUIDES = []
for _nom in ("guides_1", "guides_2", "guides_3", "guides_4"):
    try:
        _m = __import__(f"{__package__}.{_nom}", fromlist=["x"])
    except ImportError:
        continue
    for _k in dir(_m):
        if _k.startswith("GUIDES_"):
            GUIDES.extend(getattr(_m, _k))
