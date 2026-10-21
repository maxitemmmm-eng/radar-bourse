"""Rapports HTML interactifs (graphiques Plotly) + export JSON pour le futur site web."""
from __future__ import annotations

import html
import json
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import config

CSS = """
:root{--bg:#0f1117;--carte:#181b24;--bord:#2a2f3d;--texte:#e6e8ef;--doux:#9aa3b5;
--vert:#22c55e;--rouge:#ef4444;--jaune:#eab308;--bleu:#60a5fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--texte);
font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1200px;margin:0 auto;padding:24px 16px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 12px}
.sous{color:var(--doux);font-size:13px}
.carte{background:var(--carte);border:1px solid var(--bord);border-radius:12px;padding:16px;margin:12px 0}
.avert{border-left:4px solid var(--jaune)}
.grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.kpi b{display:block;font-size:22px}.kpi span{color:var(--doux);font-size:12px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 6px;border-bottom:1px solid var(--bord);text-align:left;white-space:nowrap}
th{color:var(--doux);cursor:pointer;user-select:none}tr:hover td{background:#1f2330}
.tag{padding:2px 8px;border-radius:99px;font-size:12px;font-weight:600}
.ACHATFORT{background:#14532d;color:#86efac}.ACHAT{background:#1e3a2a;color:#86efac}
.NEUTRE{background:#2a2f3d;color:#cbd5e1}.VENTE{background:#3b1d1d;color:#fca5a5}
.VENTEFORTE{background:#7f1d1d;color:#fecaca}
.pos{color:var(--vert)}.neg{color:var(--rouge)}
ul{margin:6px 0 0;padding-left:20px}li{margin:2px 0}
.tablewrap{overflow-x:auto}
"""

JS_TRI = """
document.querySelectorAll('th').forEach((th,i)=>th.onclick=()=>{
 const t=th.closest('table'),b=t.tBodies[0],rows=[...b.rows],asc=th.dataset.asc!=='1';
 rows.sort((a,c)=>{const x=a.cells[i].dataset.v??a.cells[i].innerText,y=c.cells[i].dataset.v??c.cells[i].innerText;
  const nx=parseFloat(x),ny=parseFloat(y);return (isNaN(nx)||isNaN(ny)?x.localeCompare(y):nx-ny)*(asc?1:-1)});
 rows.forEach(r=>b.appendChild(r));th.dataset.asc=asc?'1':'0'});
"""

AVERTISSEMENT = ("⚠️ Outil d'analyse éducatif, pas un conseil en investissement. Les signaux "
                 "techniques et le modèle se trompent souvent ; les performances passées ne "
                 "garantissent rien. N'investis que ce que tu peux te permettre de perdre.")


def _pct(v, signe=True):
    if v is None or pd.isna(v):
        return "–"
    cls = "pos" if v > 0 else "neg" if v < 0 else ""
    return f'<span class="{cls}">{v*100:+.1f} %</span>' if signe else f"{v*100:.1f} %"


def _page(titre: str, corps: str) -> str:
    return (f"<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(titre)}</title><style>{CSS}</style>"
            f"<script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script></head>"
            f"<body><div class='wrap'>{corps}</div><script>{JS_TRI}</script></body></html>")


def graphique_cours(ticker: str, nom: str, d: pd.DataFrame, jours: int = 250) -> str:
    d = d.iloc[-jours:]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2],
                        vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close,
                                 name="Cours"), 1, 1)
    for col, coul in (("sma50", "#60a5fa"), ("sma200", "#f59e0b")):
        fig.add_trace(go.Scatter(x=d.index, y=d[col], name=col.upper(), line=dict(color=coul, width=1.4)), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d.bb_haut, name="Bollinger", line=dict(color="#555", width=1, dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d.bb_bas, showlegend=False, line=dict(color="#555", width=1, dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d.rsi, name="RSI", line=dict(color="#a78bfa")), 2, 1)
    for niv in (30, 70):
        fig.add_hline(y=niv, line=dict(color="#555", dash="dash", width=1), row=2, col=1)
    couleurs = ["#22c55e" if v >= 0 else "#ef4444" for v in d.macd_hist]
    fig.add_trace(go.Bar(x=d.index, y=d.macd_hist, name="MACD", marker_color=couleurs), 3, 1)
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=30, b=10),
                      title=f"{nom} ({ticker})", xaxis_rangeslider_visible=False,
                      paper_bgcolor="#181b24", plot_bgcolor="#181b24",
                      legend=dict(orientation="h", y=1.02, x=0))
    return fig.to_html(include_plotlyjs=False, full_html=False)


def _bloc_modele(evaluation, importances) -> str:
    if evaluation is None or pd.isna(evaluation.precision):
        return ""
    imp = ""
    if importances is not None:
        imp = "<p class='sous'>Variables les plus utilisées : " + ", ".join(
            f"{k}" for k in importances.index) + "</p>"
    return f"""<div class='carte'><h2 style='margin-top:0'>🧠 Fiabilité du modèle (testé sur des périodes jamais vues)</h2>
<div class='grille'>
<div class='kpi'><b>{evaluation.precision*100:.1f} %</b><span>bonnes prédictions de direction à {config.HORIZON_PREDICTION} séances</span></div>
<div class='kpi'><b>{evaluation.precision_base*100:.1f} %</b><span>en disant toujours « ça monte » (référence)</span></div>
<div class='kpi'><b>{evaluation.auc:.3f}</b><span>AUC (0,5 = pile ou face)</span></div>
<div class='kpi'><b>{_pct(evaluation.precision_signaux_forts, False)}</b><span>réussite quand proba &gt; 55 % ({evaluation.nb_signaux_forts} cas)</span></div>
</div><p><b>Verdict :</b> {html.escape(evaluation.verdict())}</p>{imp}</div>"""


def rapport_scan(analyses, donnees, evaluation=None, importances=None, titre="Scan du marché") -> str:
    analyses = sorted(analyses, key=lambda a: a.score, reverse=True)
    lignes = []
    for a in analyses:
        proba = "–" if pd.isna(a.proba_hausse) else f"{a.proba_hausse*100:.0f} %"
        lignes.append(
            f"<tr><td><b>{html.escape(a.ticker)}</b><br><span class='sous'>{html.escape(a.nom)}</span></td>"
            f"<td>{a.marche.upper()}</td><td data-v='{a.prix}'>{a.prix:,.2f}</td>"
            f"<td data-v='{a.score}'><b>{a.score:.0f}</b></td>"
            f"<td><span class='tag {a.signal.replace(' ', '')}'>{a.signal}</span></td>"
            f"<td data-v='{a.proba_hausse if not pd.isna(a.proba_hausse) else -1}'>{proba}</td>"
            f"<td data-v='{a.perf['1 mois']}'>{_pct(a.perf['1 mois'])}</td>"
            f"<td data-v='{a.perf['3 mois']}'>{_pct(a.perf['3 mois'])}</td>"
            f"<td>{a.risque}</td><td>{'🚀' if a.potentiel_hausse else ''}</td></tr>")
    tableau = ("<div class='tablewrap'><table><thead><tr><th>Titre</th><th>Marché</th><th>Prix</th>"
               "<th>Score</th><th>Signal</th><th>Proba hausse</th><th>1 mois</th><th>3 mois</th>"
               "<th>Risque</th><th>Décollage</th></tr></thead><tbody>" + "".join(lignes) +
               "</tbody></table></div>")

    def carte(a):
        pour = "".join(f"<li>✅ {html.escape(r)}</li>" for r in a.raisons_pour)
        contre = "".join(f"<li>❌ {html.escape(r)}</li>" for r in a.raisons_contre)
        alertes = "".join(f"<li>🔔 {html.escape(r)}</li>" for r in a.alertes)
        return (f"<div class='carte'><b>{html.escape(a.nom)} ({a.ticker})</b> — score {a.score:.0f}, "
                f"<span class='tag {a.signal.replace(' ', '')}'>{a.signal}</span>"
                f"<p class='sous'>Stop-loss indicatif : {a.stop_loss:,.2f} · objectif indicatif : {a.objectif:,.2f}</p>"
                f"<ul>{alertes}{pour}{contre}</ul>{graphique_cours(a.ticker, a.nom, donnees[a.ticker])}</div>")

    decollage = [a for a in analyses if a.potentiel_hausse]
    top = [a for a in analyses if not a.potentiel_hausse][:5]
    corps = (f"<h1>📈 {html.escape(titre)}</h1><p class='sous'>Généré le "
             f"{datetime.now():%d/%m/%Y à %H:%M} · {len(analyses)} titres analysés</p>"
             f"<div class='carte avert'>{AVERTISSEMENT}</div>"
             + _bloc_modele(evaluation, importances)
             + "<h2>Classement (clique sur une colonne pour trier)</h2>" + tableau
             + (f"<h2>🚀 Titres avec une configuration de hausse potentielle ({len(decollage)})</h2>"
                + "".join(carte(a) for a in decollage) if decollage else
                "<h2>🚀 Aucune configuration de décollage détectée aujourd'hui</h2>")
             + "<h2>🏆 Meilleurs scores</h2>" + "".join(carte(a) for a in top))
    return _page(titre, corps)


def rapport_backtest(res, nom: str) -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=res.courbe_strategie.index, y=res.courbe_strategie, name="Stratégie du bot"))
    fig.add_trace(go.Scatter(x=res.courbe_buy_hold.index, y=res.courbe_buy_hold, name="Acheter et garder"))
    fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="#181b24",
                      plot_bgcolor="#181b24", margin=dict(l=10, r=10, t=40, b=10),
                      title=f"Évolution de {res.capital_depart:,.0f} € investis")
    lignes = ""
    for k in res.stats_buy_hold:
        lignes += (f"<tr><td>{k}</td><td>{_fmt(k, res.stats_strategie[k])}</td>"
                   f"<td>{_fmt(k, res.stats_buy_hold[k])}</td></tr>")
    for k in ("nombre de trades", "trades gagnants", "temps investi"):
        lignes += f"<tr><td>{k}</td><td>{_fmt(k, res.stats_strategie[k])}</td><td>–</td></tr>"
    gagne = res.stats_strategie["rendement total"] > res.stats_buy_hold["rendement total"]
    conclusion = ("La stratégie a battu le simple achat-conservation sur cette période."
                  if gagne else "La stratégie a fait MOINS bien que d'acheter et garder : "
                  "les signaux n'ont pas apporté de valeur ici.")
    corps = (f"<h1>🔁 Backtest — {html.escape(nom)} ({res.ticker})</h1>"
             f"<div class='carte avert'>{AVERTISSEMENT}</div>"
             f"<div class='carte'>{fig.to_html(include_plotlyjs=False, full_html=False)}</div>"
             f"<div class='carte'><table><thead><tr><th>Mesure</th><th>Bot</th><th>Acheter et garder</th>"
             f"</tr></thead><tbody>{lignes}</tbody></table><p><b>{conclusion}</b></p></div>")
    return _page(f"Backtest {res.ticker}", corps)


def _fmt(k, v):
    if v is None or pd.isna(v):
        return "–"
    if k == "nombre de trades":
        return str(int(v))
    if k == "ratio de Sharpe":
        return f"{v:.2f}"
    return _pct(v)


def sauvegarder(nom_fichier: str, contenu: str) -> str:
    os.makedirs(config.DOSSIER_RAPPORTS, exist_ok=True)
    chemin = os.path.join(config.DOSSIER_RAPPORTS, nom_fichier)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return chemin


def exporter_json(analyses, evaluation, nom_fichier="signaux.json") -> str:
    """Format prévu pour alimenter le futur site web."""
    data = {
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "modele": None if evaluation is None else {
            "precision": evaluation.precision, "precision_base": evaluation.precision_base,
            "auc": evaluation.auc, "verdict": evaluation.verdict()},
        "titres": [a.to_dict() for a in sorted(analyses, key=lambda a: a.score, reverse=True)],
    }
    return sauvegarder(nom_fichier, json.dumps(data, ensure_ascii=False, indent=2, default=float))
