"""Radar Bourse — point d'entrée en ligne de commande.

    python -m bourse_bot site                        # génère le site complet et l'ouvre
    python -m bourse_bot site --marches crypto us    # seulement certains marchés
    python -m bourse_bot analyse NVDA                # fiche détaillée d'un titre dans le terminal
    python -m bourse_bot backtest BTC-USD --capital 500 --annees 3
    python -m bourse_bot --demo site                 # données fictives (test sans Internet)
"""
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

# Console Windows : forcer l'UTF-8 pour éviter les plantages sur les accents et emojis
for flux in (sys.stdout, sys.stderr):
    try:
        flux.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table

from . import backtest, config, data, historique, indicators, model, report, scoring, site

console = Console()
COULEUR = {"ACHAT FORT": "bold green", "ACHAT": "green", "NEUTRE": "white",
           "VENTE": "red", "VENTE FORTE": "bold red"}
TOUS_MARCHES = ["fr", "us", "crypto", "etf", "tendances"]


def _marche_de(ticker: str) -> str:
    for marche, univers in config.UNIVERS.items():
        if ticker in univers:
            return marche
    if ticker.endswith("-USD"):
        return "crypto"
    return "fr" if ticker.endswith(".PA") else "us"


def _univers(marches: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    noms, marche_de = {}, {}
    for m in marches:
        if m == "tendances":
            continue
        for t, n in config.UNIVERS[m].items():
            noms[t], marche_de[t] = n, m
    if "tendances" in marches:
        with console.status("Recherche des titres en tendance…"):
            tend = data.tendances_actions() | data.tendances_crypto()
        for t, n in tend.items():
            if t not in noms:
                noms[t], marche_de[t] = n, "tendances"
    return noms, marche_de


def _preparer(noms: dict[str, str], marche_de: dict[str, str]):
    """Télécharge tout en un lot puis calcule les indicateurs. Renvoie (données, bruts)."""
    extra = set(config.BENCHMARK.values()) | {t for t, _ in site.INDICES}
    with console.status(f"Téléchargement des cours ({len(noms)} titres)…"):
        bruts = data.telecharger_plusieurs(list(noms) + sorted(extra))
    donnees, ignores = {}, []
    for t in noms:
        brut = bruts.get(t)
        if brut is None or len(brut) < 260:
            ignores.append(t)
            continue
        type_marche = "crypto" if t.endswith("-USD") else marche_de[t]
        bench = bruts.get(config.BENCHMARK.get(type_marche, "SPY"))
        donnees[t] = indicators.calculer(brut, bench)
    if ignores:
        console.print(f"[dim]{len(ignores)} titre(s) ignoré(s) (introuvable ou moins d'un an "
                      f"d'historique) : {', '.join(ignores[:12])}{'…' if len(ignores) > 12 else ''}[/dim]")
    return donnees, bruts


def _analyser(donnees, noms, marche_de, args):
    analyses = []
    for t, d in donnees.items():
        try:
            analyses.append(scoring.analyser(t, noms[t], marche_de[t], d))
        except Exception as e:  # un titre aux données bizarres ne doit pas bloquer tout le reste
            console.print(f"[dim]{t} : analyse impossible ({e})[/dim]")
    evaluation = None
    if not args.sans_ml and len(donnees) >= 5:
        with console.status("Entraînement et validation du modèle (peut prendre 1 à 2 minutes)…"):
            try:
                probas, evaluation = model.entrainer_et_predire(
                    {a.ticker: donnees[a.ticker] for a in analyses},
                    {a.ticker: ("crypto" if a.ticker.endswith("-USD") else a.marche) for a in analyses})
                for a in analyses:
                    a.proba_hausse = probas.get(a.ticker, float("nan"))
                    a.fiabilite_modele = evaluation.precision
            except Exception as e:
                console.print(f"[yellow]Modèle désactivé pour cette fois : {e}[/yellow]")
    return analyses, evaluation


def _afficher_eval(ev):
    if ev is None or ev.precision != ev.precision:
        return
    console.rule("[bold]Fiabilité du modèle (périodes jamais vues)")
    console.print(f"Bonnes directions à {config.HORIZON_PREDICTION} séances : [bold]{ev.precision*100:.1f} %[/bold]"
                  f"  (référence naïve {ev.precision_base*100:.1f} %)  ·  AUC {ev.auc:.3f}")
    console.print(f"[yellow]{ev.verdict()}[/yellow]")


def _ouvrir(chemin, args):
    console.print(f"\n🌐 [bold]{chemin}[/bold]")
    if not args.pas_de_navigateur:
        webbrowser.open(Path(chemin).resolve().as_uri())


# ----------------------------------------------------------------------------
def cmd_site(args):
    noms, marche_de = _univers(args.marches)
    donnees, bruts = _preparer(noms, marche_de)
    if not donnees:
        console.print("[red]Aucune donnée récupérée. Vérifie ta connexion Internet puis relance.[/red]")
        return 1
    # Garde-fou : si Yahoo n'a renvoyé qu'une partie des titres principaux, on ne publie pas
    # un site à moitié vide (en ligne, l'ancienne version reste affichée).
    principaux = [t for t in noms if marche_de[t] != "tendances"]
    couverture = sum(t in donnees for t in principaux) / max(len(principaux), 1)
    if couverture < 0.6:
        console.print(f"[red]Seulement {couverture:.0%} des titres ont pu être téléchargés : "
                      f"Yahoo bloque sans doute temporairement. Site non mis à jour, réessaie plus tard.[/red]")
        return 2
    analyses, evaluation = _analyser(donnees, noms, marche_de, args)
    if not args.demo:
        historique.enregistrer(analyses)
    suivi = historique.bilan(bruts if not args.demo else {})

    _afficher_eval(evaluation)
    tab = Table(title="Top 10 du radar", header_style="bold cyan")
    for c in ("Titre", "Nom", "Score", "Signal", f"Proba ↑ {config.HORIZON_PREDICTION}s", "🚀"):
        tab.add_column(c)
    for a in sorted(analyses, key=lambda a: a.score, reverse=True)[:10]:
        p = "–" if a.proba_hausse != a.proba_hausse else f"{a.proba_hausse*100:.0f} %"
        tab.add_row(a.ticker, a.nom[:24], f"{a.score:.0f}", f"[{COULEUR[a.signal]}]{a.signal}[/]", p,
                    "🚀" if a.potentiel_hausse else "")
    console.print(tab)

    payload = site.construire(analyses, donnees, evaluation, suivi, bruts, demo=args.demo)
    chemin = site.ecrire(payload)
    console.print(f"✅ Site généré : {len(analyses)} titres analysés.")
    _ouvrir(chemin, args)
    return 0


def cmd_analyse(args):
    t = args.ticker.upper()
    marche = _marche_de(t)
    noms, marche_de = dict(config.UNIVERS[marche]), {k: marche for k in config.UNIVERS[marche]}
    noms.setdefault(t, t); marche_de.setdefault(t, marche)
    donnees, _ = _preparer(noms, marche_de)
    if t not in donnees:
        console.print(f"[red]{t} introuvable ou historique trop court (il faut au moins un an).[/red]")
        return 1
    analyses, evaluation = _analyser(donnees, noms, marche_de, args)
    a = next(x for x in analyses if x.ticker == t)
    console.rule(f"[bold]{a.nom} ({t})")
    console.print(f"Cours : [bold]{a.prix:,.2f} {a.devise}[/bold]  ·  Score [bold]{a.score:.0f}/100[/bold]  ·  "
                  f"[{COULEUR[a.signal]}]{a.signal}[/]  ·  Risque {a.risque}")
    if a.proba_hausse == a.proba_hausse:
        console.print(f"Probabilité de hausse à {config.HORIZON_PREDICTION} séances : [bold]{a.proba_hausse*100:.0f} %[/bold]")
    for r in a.alertes: console.print(f"🔔 {r}")
    for r in a.raisons_pour: console.print(f"[green]✓ {r}[/green]")
    for r in a.raisons_contre: console.print(f"[red]✕ {r}[/red]")
    _afficher_eval(evaluation)
    return 0


def _brut(k, v):
    if v != v:
        return "–"
    if k == "nombre de trades":
        return str(int(v))
    return f"{v:.2f}" if k == "ratio de Sharpe" else f"{v*100:+.1f} %"


def cmd_backtest(args):
    t = args.ticker.upper()
    marche = _marche_de(t)
    bruts = data.telecharger_plusieurs([t, config.BENCHMARK[marche]])
    if len(bruts.get(t, [])) < 300:
        console.print(f"[red]{t} : historique insuffisant.[/red]")
        return 1
    d = indicators.calculer(bruts[t], bruts.get(config.BENCHMARK[marche]))
    res = backtest.lancer(t, d, args.capital, args.annees)
    nom = config.UNIVERS.get(marche, {}).get(t, t)
    tab = Table(title=f"Backtest {nom} — {args.capital:,.0f} € sur {args.annees:g} ans", header_style="bold cyan")
    tab.add_column("Mesure"); tab.add_column("Radar"); tab.add_column("Acheter et garder")
    for k in res.stats_buy_hold:
        tab.add_row(k, _brut(k, res.stats_strategie[k]), _brut(k, res.stats_buy_hold[k]))
    tab.add_row("nombre de trades", _brut("nombre de trades", res.stats_strategie["nombre de trades"]), "–")
    console.print(tab)
    console.print(f"Capital final — radar : [bold]{res.courbe_strategie.iloc[-1]:,.2f} €[/bold]   "
                  f"acheter et garder : [bold]{res.courbe_buy_hold.iloc[-1]:,.2f} €[/bold]")
    chemin = report.sauvegarder(f"backtest_{t.replace('^', '')}.html", report.rapport_backtest(res, nom))
    _ouvrir(chemin, args)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="bourse_bot", description="Radar Bourse : analyse et prévisions (éducatif).")
    p.add_argument("--demo", action="store_true", help="données fictives, sans Internet")
    p.add_argument("--sans-ml", action="store_true", help="désactive le modèle de machine learning")
    p.add_argument("--pas-de-navigateur", action="store_true", help="n'ouvre pas la page automatiquement")
    sp = p.add_subparsers(dest="cmd")

    s = sp.add_parser("site", aliases=["scan"], help="analyse les marchés et génère le site")
    s.add_argument("--marches", nargs="+", default=TOUS_MARCHES, choices=TOUS_MARCHES)
    s.set_defaults(f=cmd_site)
    a = sp.add_parser("analyse", help="fiche détaillée d'un titre (ex : AAPL, MC.PA, BTC-USD)")
    a.add_argument("ticker"); a.set_defaults(f=cmd_analyse)
    b = sp.add_parser("backtest", help="teste la stratégie du radar sur l'historique d'un titre")
    b.add_argument("ticker")
    b.add_argument("--capital", type=float, default=1000)
    b.add_argument("--annees", type=float, default=3)
    b.set_defaults(f=cmd_backtest)

    args = p.parse_args(argv)
    if args.cmd is None:  # double-clic / sans argument : on génère le site
        args = p.parse_args((sys.argv[1:] if argv is None else argv) + ["site"])
    data.DEMO = args.demo
    try:
        return args.f(args)
    except KeyboardInterrupt:
        console.print("\nArrêté.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
