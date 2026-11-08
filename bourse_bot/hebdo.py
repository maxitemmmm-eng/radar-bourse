"""Version 65 : la visibilité.

- Les avis sûrs de l'IA sont archivés chaque soir puis VÉRIFIÉS en public 20 séances plus tard
  (même règle que le test sur les années passées : le mois a-t-il vraiment été plus agité, ou plus calme,
  que les 20 séances d'avant ?). Page « avis-surs-verifies.html ».
- Pages par thème (luxe, IA et puces, défense, banques…) : elles répondent à des recherches larges
  (« actions du luxe », « actions IA ») et relient les fiches entre elles.
- Graphiques en barres sans JavaScript pour les pages statiques (semaine, thèmes, vérification).
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime

from . import config

HORIZON = 20   # séances : le « mois prochain » des avis d'agitation (config.HORIZON_PREDICTION)


# ----------------------------------------------------------------------------
# Graphique en barres (HTML + CSS, lisible au téléphone et à l'impression)
# ----------------------------------------------------------------------------
def barres(lignes, fmt=None, titre="", note="", neutre=False):
    """lignes : [(libellé_html, valeur)] ; barres vertes à droite du zéro, rouges à gauche."""
    lignes = [(l, v) for l, v in lignes if isinstance(v, (int, float)) and math.isfinite(v)]
    if not lignes:
        return ""
    fmt = fmt or (lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v) * 100:.1f} %".replace(".", ","))
    m = max(abs(v) for _, v in lignes) or 1
    neg = any(v < 0 for _, v in lignes)
    pos = any(v > 0 for _, v in lignes)
    out = []
    for lib, v in lignes:
        larg = max(1.5, abs(v) / m * (50 if neg and pos else 100))
        if neg and pos:
            style = f"left:{50 if v >= 0 else 50 - larg:.1f}%;width:{larg:.1f}%"
        elif neg:
            style = f"right:0;width:{larg:.1f}%"
        else:
            style = f"left:0;width:{larg:.1f}%"
        cls = "" if neutre else "b-up" if v > 0 else "b-down" if v < 0 else ""
        out.append(f"<div class='bar-l'><span class='bar-n'>{lib}</span><span class='bar-t{' z' if neg and pos else ''}'>"
                   f"<i class='{cls}' style='{style}'></i></span><span class='bar-v m {('' if neutre else 'up' if v > 0 else 'down' if v < 0 else '')}'>{fmt(v)}</span></div>")
    return (f"<figure class='barres'>{f'<figcaption>{titre}</figcaption>' if titre else ''}" + "".join(out)
            + (f"<p class='muted' style='margin:6px 0 0;font-size:13px'>{note}</p>" if note else "") + "</figure>")


CSS = """
.barres{margin:14px 0;padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
.barres figcaption{font-weight:700;margin:0 0 10px}
.bar-l{display:grid;grid-template-columns:minmax(90px,34%) 1fr 74px;gap:10px;align-items:center;padding:4px 0;font-size:14.5px}
.bar-n{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar-t{position:relative;height:12px;border-radius:6px;background:var(--line)}
.bar-t.z::after{content:"";position:absolute;left:50%;top:-3px;bottom:-3px;width:1px;background:var(--muted)}
.bar-t i{position:absolute;top:0;bottom:0;border-radius:6px;background:var(--accent)}
.bar-t i.b-up{background:var(--up)}.bar-t i.b-down{background:var(--down)}
.bar-v{text-align:right;font-weight:600}
td.m{white-space:nowrap}
.kv th{width:46%;font-weight:500;color:var(--muted);position:static;font-size:14px}.kv td.m{white-space:normal;text-align:right}
@media (prefers-reduced-motion:no-preference){
.bar-t i{animation:barre-pousse .9s cubic-bezier(.2,.8,.2,1) both;transform-origin:left center}
.bar-t i.b-down{transform-origin:right center}
.bar-l:nth-child(2) i{animation-delay:.05s}.bar-l:nth-child(3) i{animation-delay:.1s}.bar-l:nth-child(4) i{animation-delay:.15s}
.bar-l:nth-child(5) i{animation-delay:.2s}.bar-l:nth-child(6) i{animation-delay:.25s}.bar-l:nth-child(n+7) i{animation-delay:.3s}
@keyframes barre-pousse{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.courbe .cs-ligne{stroke-dasharray:1;stroke-dashoffset:1;animation:trace 1.6s ease-out .1s forwards}
@keyframes trace{to{stroke-dashoffset:0}}
.courbe .ag-pred,.courbe .cs-med{animation:apparait .5s ease-out 1.5s both}
@keyframes apparait{from{opacity:0}to{opacity:1}}
.compteurs div{animation:monte .5s ease-out both}.compteurs div:nth-child(2){animation-delay:.08s}.compteurs div:nth-child(3){animation-delay:.16s}
@keyframes monte{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.verdict{animation:apparait .4s ease-out both}}
@media print{.bar-t i,.courbe .cs-ligne,.courbe .ag-pred,.courbe .cs-med,.compteurs div{animation:none!important;stroke-dashoffset:0!important;opacity:1!important}}
.ag-norm{stroke:var(--muted);stroke-width:1.2;stroke-dasharray:5 5}.ag-pred{fill:var(--ink);stroke:var(--surface);stroke-width:2}
.verdict{display:inline-block;min-width:1.6em;text-align:center;font-weight:700;border-radius:6px;padding:0 6px}
.verdict.ok{color:var(--up);background:var(--up-soft)}.verdict.ko{color:var(--down);background:var(--down-soft)}
.compteurs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.compteurs div{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--surface)}
.compteurs b{display:block;font-size:26px;font-variant-numeric:tabular-nums}.compteurs span{color:var(--muted);font-size:13.5px}
@media (max-width:560px){.bar-l{grid-template-columns:38% 1fr 66px;font-size:13.5px}}
"""


# ----------------------------------------------------------------------------
# Archivage des avis sûrs (chaque soir, dans historique/points/<date>.json)
# ----------------------------------------------------------------------------
def avis_du_jour(payload: dict) -> list:
    """[ticker, sens (+1 plus agité / −1 plus calme), agitation des 20 dernières séances, 1 si très sûr]."""
    out = []
    for t in payload.get("titres", []):
        r = t.get("risque_prevu") or {}
        if t.get("marche") == "tendances" or not r.get("sur") or not r.get("recent") or not r.get("vol"):
            continue
        v20 = r["vol"] / r["recent"]
        if v20 > 0 and math.isfinite(v20):
            out.append([t["ticker"], 1 if r["recent"] > 1 else -1, round(v20, 5), 1 if r.get("tres_sur") else 0])
    return out


def _points():
    src = os.path.join(config.DOSSIER_HISTORIQUE, "points")
    if not os.path.isdir(src):
        return []
    res = []
    for nom in sorted(os.listdir(src)):
        if not nom.endswith(".json"):
            continue
        try:
            with open(os.path.join(src, nom), encoding="utf-8") as f:
                r = json.load(f)
        except Exception:
            continue
        if r.get("surs") and r.get("date"):
            res.append(r)
    return res


def _vol_realisee(c, debut, n):
    """Agitation réalisée (annualisée) sur les n rendements après l'indice `debut` (même règle que le test)."""
    seg = c[debut:debut + n + 1]
    if len(seg) < n + 1 or any(v is None or v <= 0 for v in seg):
        return None
    r = [math.log(seg[i + 1] / seg[i]) for i in range(n)]
    moy = sum(r) / n
    return math.sqrt(sum((x - moy) ** 2 for x in r) / (n - 1)) * math.sqrt(252)


def verifier(titres: list) -> dict:
    """Vérifie chaque avis archivé dont les 20 séances sont passées. Les cours viennent des séries du site."""
    series = {t["ticker"]: t.get("serie") or {} for t in titres if t.get("serie")}
    noms = {t["ticker"]: t.get("nom", t["ticker"]) for t in titres}
    faits, attente, prochains, en_cours = [], 0, [], []
    for p in _points():
        for tk, sens, v20, tres in p["surs"]:
            s = series.get(tk) or {}
            dates, c = s.get("t") or [], s.get("c") or []
            if not dates:
                continue
            idx = max((i for i, d in enumerate(dates) if d <= p["date"]), default=None)
            if idx is None or dates[0] > p["date"]:
                continue
            if idx + HORIZON >= len(c):
                attente += 1
                prochains.append(p["date"])
                en_cours.append({"date": p["date"], "ticker": tk, "nom": noms.get(tk, tk), "sens": sens, "tres": bool(tres), "avant": v20})
                continue
            vr = _vol_realisee(c, idx, HORIZON)
            if vr is None:
                continue
            juste = (vr > v20) == (sens > 0)
            faits.append({"date": p["date"], "fin": dates[idx + HORIZON], "ticker": tk, "nom": noms.get(tk, tk),
                          "sens": sens, "tres": bool(tres), "avant": v20, "apres": vr, "juste": juste})
    faits.sort(key=lambda f: (f["fin"], f["date"]), reverse=True)
    return {"faits": faits, "attente": attente, "premier_attente": min(prochains) if prochains else None, "en_cours": en_cours}


def _wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    e = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - e), min(1, c + e)


def bilan(faits, tres=None):
    sel = [f for f in faits if tres is None or f["tres"] == tres]
    k = sum(f["juste"] for f in sel)
    return {"n": len(sel), "k": k, "taux": (k / len(sel)) if sel else None, "ic": _wilson(k, len(sel))}


def _pc(v):
    return "—" if v is None else f"{round(v * 100)} %"


# ----------------------------------------------------------------------------
# Page publique : les avis sûrs vérifiés
# ----------------------------------------------------------------------------
def page_verifies(seo, base, payload, dossier, csp, V=None):
    V = V or verifier(payload.get("titres", []))
    faits = V["faits"]
    av = ((payload.get("modele") or {}).get("risque") or {}).get("avis_surs") or {}
    taux_test = av.get("taux")
    taux_t = (av.get("tres") or {}).get("taux")
    b_tous, b_tres = bilan(faits), bilan(faits, True)
    e, slug, dl = seo._e, seo.slug, seo.date_longue
    h1 = "Les avis sûrs de l'IA, vérifiés en public"
    corps = (f"<p class='muted'><a href='resultats.html'>Résultats réels</a></p><h1>{h1}</h1>"
             "<p>Chaque soir, le radar note ses <b>avis sûrs</b> : les titres dont il pense, avec une bonne marge, que le mois "
             "qui vient sera <b>plus agité</b> ou <b>plus calme</b> que les dernières semaines. Ces avis sont enregistrés "
             "avant de connaître la suite, puis vérifiés ici, automatiquement, 20 séances plus tard. Rien n'est effacé.</p>")
    if taux_test:
        corps += (f"<p class='avis-sur'>Sur les années passées (jamais vues pendant l'apprentissage), les avis sûrs étaient justes "
                  f"<b>{_pc(taux_test)}</b> du temps{f', les avis très sûrs <b>{_pc(taux_t)}</b>' if taux_t else ''}. "
                  "Cette page dit si ça tient en vrai, dans le futur.</p>")
    if b_tous["n"]:
        ic = b_tous["ic"]
        corps += ("<div class='compteurs'>"
                  f"<div><b>{_pc(b_tous['taux'])}</b><span>avis sûrs justes ({b_tous['k']} sur {b_tous['n']})</span></div>"
                  + (f"<div><b>{_pc(b_tres['taux'])}</b><span>avis très sûrs justes ({b_tres['k']} sur {b_tres['n']})</span></div>" if b_tres["n"] else "")
                  + f"<div><b>{V['attente']}</b><span>avis en cours de vérification</span></div></div>"
                  + (f"<p class='muted'>Marge d'erreur liée au nombre d'avis : entre {_pc(ic[0])} et {_pc(ic[1])}. "
                     "Les avis d'un même jour se ressemblent souvent (un marché entier qui se calme) : il faut plusieurs mois "
                     "pour juger vraiment.</p>" if ic else ""))
        # par semaine de vérification
        sem = {}
        for f in faits:
            a, s, _ = datetime.strptime(f["fin"], "%Y-%m-%d").isocalendar()
            sem.setdefault(f"{a}-S{s:02d}", []).append(f["juste"])
        lignes = [(f"Semaine {int(k.split('-S')[1])}", sum(v) / len(v)) for k, v in sorted(sem.items())[-12:]]
        corps += barres(lignes, fmt=lambda v: f"{round(v * 100)} %", titre="Part d'avis justes, par semaine de vérification", neutre=True,
                        note="Une barre par semaine où des avis sont arrivés à leur terme.")
        corps += ("<h2>Les derniers avis vérifiés</h2><div class='carte' style='overflow-x:auto' tabindex='0' role='region' "
                  "aria-label='Derniers avis vérifiés'><table><tr><th>Titre</th><th>Avis du</th><th>L'IA disait</th>"
                  "<th>Agitation avant → après</th><th>Résultat</th></tr>")
        for f in faits[:60]:
            corps += (f"<tr><td><a href='titres/{slug(f['ticker'])}.html'>{e(f['nom'])}</a>{' <span class=\"muted\">(très sûr)</span>' if f['tres'] else ''}</td>"
                      f"<td class='m'>{e(f['date'][8:10] + '/' + f['date'][5:7])}</td>"
                      f"<td>{'plus agité' if f['sens'] > 0 else 'plus calme'}</td>"
                      f"<td class='m'>{round(f['avant'] * 100)} % → {round(f['apres'] * 100)} %</td>"
                      f"<td>{'<span class=\"verdict ok\" title=\"juste\">✓ juste</span>' if f['juste'] else '<span class=\"verdict ko\" title=\"faux\">✗ faux</span>'}</td></tr>")
        corps += "</table></div>"
    else:
        quand = ""
        if V["premier_attente"]:
            quand = f" Les premiers avis enregistrés datent du {e(dl(V['premier_attente']))} : leur verdict tombe environ 4 semaines plus tard."
        corps += (f"<div class='carte'><b>Premiers verdicts bientôt.</b><p style='margin:6px 0 0'>{V['attente']} avis sont "
                  f"enregistrés et attendent la fin de leurs 20 séances.{quand} Cette page se remplit toute seule, chaque soir.</p></div>")
    corps += ("<p><a class='btn' href='donnees-ouvertes.html'>Toutes les données en CSV et JSON</a></p>"
              "<h2>Comment c'est vérifié</h2><ul>"
              "<li>L'agitation, c'est l'ampleur des mouvements de prix (à la hausse comme à la baisse), ramenée à une année.</li>"
              "<li>« Avant » : l'agitation des 20 séances qui précèdent l'avis. « Après » : celle des 20 séances qui le suivent.</li>"
              "<li>L'avis est juste si « après » est plus grand que « avant » quand l'IA disait « plus agité », et plus petit quand elle disait « plus calme ».</li>"
              "<li>C'est exactement la règle utilisée pour mesurer l'IA sur les années passées (<a href='fiche-technique-ia.html'>fiche technique</a>).</li>"
              "</ul><p class='muted'>Prévoir l'agitation n'est pas prévoir le sens : un titre peut être plus calme et baisser quand même. "
              "Projet éducatif, pas un conseil en investissement.</p>")
    jsonld = {"@context": "https://schema.org", "@type": "Dataset", "name": h1, "isAccessibleForFree": True,
              "description": "Avis de l'IA sur l'agitation du mois suivant, enregistrés à l'avance et vérifiés 20 séances plus tard.",
              "creator": {"@type": "Organization", "name": seo.NOM}, "license": (base + "credits.html") if base else "credits.html",
              "copyrightHolder": {"@type": "Organization", "name": seo.NOM}}
    desc = ("Les avis sûrs de l'IA sont enregistrés avant de connaître la suite, puis vérifiés en public 20 séances plus tard : "
            + (f"{_pc(b_tous['taux'])} justes sur {b_tous['n']} à ce jour." if b_tous["n"] else "premiers verdicts en cours."))
    with open(os.path.join(dossier, "avis-surs-verifies.html"), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Avis de l'IA vérifiés en public : vrais résultats | {seo.NOM}", desc,
                          "avis-surs-verifies.html", corps, jsonld, csp,
                          alternates={"fr": "avis-surs-verifies.html", "en": "en/verified-calls.html", "x-default": "avis-surs-verifies.html"}))
    return V


# ----------------------------------------------------------------------------
# Pages par thème
# ----------------------------------------------------------------------------
THEMES = [
    ("luxe", "Actions du luxe et de la mode", "luxe",
     "LVMH, Hermès, Kering, L'Oréal, Ferrari… Les grandes marques du luxe et de la mode suivies par le radar.",
     ["MC.PA", "RMS.PA", "KER.PA", "EL.PA", "OR.PA", "RACE.MI", "ITX.MC", "ADS.DE", "NKE", "ZAL.DE", "PRX.AS"], "actions-luxe"),
    ("ia-semi-conducteurs", "Actions de l'intelligence artificielle et des puces", "IA et semi-conducteurs",
     "Les fabricants de puces (Nvidia, TSMC, ASML…) et les géants du logiciel qui misent sur l'IA.",
     ["NVDA", "AMD", "AVGO", "TSM", "ASML.AS", "MU", "ARM", "INTC", "QCOM", "TXN", "AMAT", "IFX.DE", "STMPA.PA", "SOI.PA",
      "MSFT", "GOOGL", "META", "PLTR", "ORCL", "NOW", "CRM", "SMH", "BOTZ"], "actions-ia"),
    ("gafam", "Les géants de la tech américaine (GAFAM et « 7 magnifiques »)", "géants de la tech",
     "Apple, Microsoft, Nvidia, Alphabet, Amazon, Meta et Tesla : les sept plus grosses entreprises de la Bourse américaine.",
     ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "QQQ"], None),
    ("defense-aeronautique", "Actions de la défense et de l'aéronautique", "défense et aéronautique",
     "Rheinmetall, Safran, Airbus, Thales, Dassault Aviation, Lockheed Martin… Les industriels de la défense et de l'aviation.",
     ["RHM.DE", "SAF.PA", "AIR.PA", "HO.PA", "AM.PA", "LMT", "RTX", "BA", "GE", "HON"], None),
    ("banques", "Actions des banques", "banques",
     "BNP Paribas, Société Générale, Crédit Agricole, les grandes banques européennes et américaines.",
     ["BNP.PA", "GLE.PA", "ACA.PA", "INGA.AS", "SAN.MC", "BBVA.MC", "UCG.MI", "ISP.MI", "DBK.DE", "KBC.BR", "JPM", "BAC",
      "WFC", "GS", "MS", "C", "HSBC", "MUFG", "HDB", "IBN", "TD", "RY"], "actions-bancaires"),
    ("petrole-energie", "Actions du pétrole et de l'énergie", "pétrole et énergie",
     "TotalEnergies, Shell, BP, ExxonMobil, Chevron… Les grandes compagnies pétrolières et gazières.",
     ["TTE.PA", "ENI.MI", "SHEL", "BP", "XOM", "CVX", "COP", "PBR", "ENB", "XLE"], "petrole-energie-bourse"),
    ("energies-vertes", "Actions de l'électricité et des énergies vertes", "énergies vertes",
     "Engie, Iberdrola, Enel, RWE, NextEra… Les producteurs d'électricité et les énergies renouvelables.",
     ["ENGI.PA", "IBE.MC", "ENEL.MI", "RWE.DE", "EOAN.DE", "NEE", "ICLN"], None),
    ("sante-pharma", "Actions de la santé et de la pharmacie", "santé et pharmacie",
     "Sanofi, Novo Nordisk, Eli Lilly, AstraZeneca, Johnson & Johnson… Les laboratoires et les géants de la santé.",
     ["SAN.PA", "EL.PA", "BAYN.DE", "MRK.DE", "LLY", "UNH", "JNJ", "MRK", "PFE", "ABBV", "NVO", "NVS", "AZN", "GSK",
      "AMGN", "TMO", "ABT", "ISRG"], "actions-defensives"),
    ("automobile", "Actions de l'automobile", "automobile",
     "Stellantis, Renault, BMW, Mercedes, Volkswagen, Tesla, Toyota… Les constructeurs et Michelin.",
     ["STLAP.PA", "RNO.PA", "BMW.DE", "MBG.DE", "VOW3.DE", "TSLA", "TM", "HMC", "RACE.MI", "ML.PA"], None),
    ("chine-emergents", "Actions de Chine et des pays émergents", "Chine et émergents",
     "Alibaba, JD.com, Tencent, Infosys, MercadoLibre, Vale… et les ETF des pays émergents.",
     ["BABA", "PDD", "JD", "BIDU", "TCEHY", "INFY", "HDB", "IBN", "MELI", "NU", "SE", "VALE", "PBR", "FXI", "EEM", "INDA"], None),
    ("consommation", "Actions de la consommation de tous les jours", "consommation",
     "Danone, Pernod Ricard, Coca-Cola, Procter & Gamble, McDonald's… Des titres souvent plus calmes que la moyenne.",
     ["BN.PA", "RI.PA", "CA.PA", "AD.AS", "HEIA.AS", "ABI.BR", "BEI.DE", "HEN3.DE", "UL", "DEO", "KO", "PEP", "PG",
      "WMT", "COST", "MCD", "SBUX", "PM", "BTI"], "actions-defensives"),
]


def pages_themes(seo, base, payload, dossier, csp, date):
    """Une page par thème, triée par avis de l'IA, avec un graphique de la performance sur un mois."""
    par_tk = {t["ticker"]: t for t in payload.get("titres", []) if t.get("prix")}
    os.makedirs(os.path.join(dossier, "themes"), exist_ok=True)
    e, slug, aff, px, pct = seo._e, seo.slug, seo.aff_tk, seo._px, seo._pct
    maintenant = datetime.now()
    mois_an = f"{seo.MOIS[maintenant.month - 1]} {maintenant.year}"
    faits, liens = [], []
    for cle, h1, court, intro, tks, guide in THEMES:
        items = [par_tk[t] for t in tks if t in par_tk]
        if len(items) < 4:
            continue
        rp = lambda t: t.get("risque_prevu") or {}
        perf_m = lambda t: (t.get("perf") or {}).get("1 mois")
        nb_sur = sum(1 for t in items if seo.marque_sur(t))
        lignes = "".join(
            f"<tr><td><a href='../titres/{slug(t['ticker'])}.html'>{e(t['nom'])}</a>{seo.marque_sur(t)} "
            f"<span class='muted'>{e(aff(t['ticker']))}</span></td><td class='m'>{px(t['prix'], t['devise'])}</td>"
            f"<td class='m'>{pct(perf_m(t))}</td>"
            f"<td class='m'>{('±' + str(round(rp(t)['mouvement'] * 100)) + ' %') if rp(t).get('mouvement') else '—'}</td>"
            f"<td class='m'>{(str(round(rp(t)['chute'] * 100)) + ' %') if rp(t).get('chute') is not None else '—'}</td></tr>"
            for t in sorted(items, key=lambda t: -(perf_m(t) or -9)))
        graph = barres([(e(t["nom"]), perf_m(t)) for t in sorted(items, key=lambda t: -(perf_m(t) or -9))],
                       titre=f"{court[:1].upper() + court[1:]} : variation sur un mois", note=f"Cours au {e(date)}.")
        calmes = sorted([t for t in items if rp(t).get("mouvement")], key=lambda t: rp(t)["mouvement"])
        resume = ""
        if len(calmes) >= 3:
            resume = (f"<p>Pour le mois qui vient, l'IA prévoit le plus de mouvement pour <b>{e(calmes[-1]['nom'])}</b> "
                      f"(environ ±{round(rp(calmes[-1])['mouvement'] * 100)} %) et le moins pour <b>{e(calmes[0]['nom'])}</b> "
                      f"(environ ±{round(rp(calmes[0])['mouvement'] * 100)} %)."
                      + (f" {nb_sur} titre{'s' if nb_sur > 1 else ''} de ce thème {'ont' if nb_sur > 1 else 'a'} un avis sûr de l'IA "
                         "(petit logo vert)." if nb_sur else "") + "</p>")
        corps = (f"<p class='muted'><a href='../themes.html'>Tous les thèmes</a></p><h1>{e(h1)} : cours et prévisions</h1>"
                 f"<p class='muted'>Mis à jour automatiquement · cours au {e(date)}</p><p>{e(intro)}</p>{resume}{graph}"
                 "<div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='Tableau du thème'><table>"
                 "<tr><th>Titre</th><th>Cours</th><th>Sur 1 mois</th><th>Agitation prévue</th><th title='Risque de chute de plus de 10 % le mois prochain'>Risque de chute*</th></tr>"
                 + lignes + "</table></div>"
                 "<p class='muted'>* Risque de chute de plus de 10 % sur le mois prochain. L'agitation et le risque de chute sont ce que l'IA prévoit le mieux "
                 "(<a href='../resultats.html'>résultats réels</a>, <a href='../avis-surs-verifies.html'>avis vérifiés en public</a>). "
                 "Le sens du prix, lui, reste très incertain. Ce n'est pas un conseil d'achat.</p>"
                 + (f"<p><a class='btn' href='../guides/{guide}.html'>Lire le guide</a></p>" if guide else "")
                 + "<h2>Les autres thèmes</h2><ul class='liste'>"
                 + "".join(f"<li><a href='{c}.html'>{e(h)}</a></li>" for c, h, *_ in THEMES if c != cle) + "</ul>")
        chemin = f"themes/{cle}.html"
        titre = f"{h1} : prévisions {mois_an}"
        titre = (titre if len(titre) <= 62 else f"{h1}") + f" | {seo.NOM}"
        jl = seo._jsonld_liste(base, h1, chemin, [(t["nom"], f"titres/{slug(t['ticker'])}.html") for t in items], ("Thèmes", "themes.html"))
        desc = f"{intro} Cours au {date}, variation sur un mois, agitation et risque de chute prévus par l'IA."
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(seo._page(base, titre, seo.desc_courte(desc), chemin, corps, jl, csp=csp,
                              alternates={"fr": chemin, "en": "en/" + chemin, "x-default": chemin}))
        faits.append(chemin)
        liens.append((h1, chemin, intro))
        for t in items:
            t.setdefault("_themes", []).append((court, chemin))
    if liens:
        corps = ("<h1>Les thèmes de la Bourse</h1><p class='muted'>Les titres suivis par le radar, rangés par grand thème : "
                 "luxe, intelligence artificielle, défense, banques, énergie…</p><div class='liste-themes'>"
                 + "".join(f"<a class='carte' style='display:block;margin:10px 0;text-decoration:none' href='{c}'><b>{e(h)}</b>"
                           f"<span class='muted' style='display:block;margin-top:4px'>{e(i)}</span></a>" for h, c, i in liens) + "</div>")
        with open(os.path.join(dossier, "themes.html"), "w", encoding="utf-8") as f:
            f.write(seo._page(base, f"Actions par thème : luxe, IA, défense, banques | {seo.NOM}",
                              "Les actions suivies par le radar rangées par thème, avec les prévisions de l'IA mises à jour chaque jour.",
                              "themes.html", corps, seo._jsonld_liste(base, "Thèmes", "themes.html", [(h, c) for h, c, _ in liens]), csp=csp,
                              alternates={"fr": "themes.html", "en": "en/themes.html", "x-default": "themes.html"}))
        faits.append("themes.html")
    return faits


def themes_de(ticker: str) -> list:
    """[(chemin court, nom du thème)] pour les liens des fiches."""
    return [(cle, court[:1].upper() + court[1:]) for cle, _h, court, _i, tks, _g in THEMES if ticker in tks]


# ----------------------------------------------------------------------------
# Versions anglaises (en/themes/*.html, en/verified-calls.html)
# ----------------------------------------------------------------------------
THEMES_EN = {
    "luxe": ("Luxury and fashion stocks", "luxury", "LVMH, Hermès, Kering, L'Oréal, Ferrari… the big luxury and fashion brands tracked by the radar."),
    "ia-semi-conducteurs": ("AI and semiconductor stocks", "AI and chips", "Chipmakers (Nvidia, TSMC, ASML…) and the software giants betting on AI."),
    "gafam": ("Big Tech stocks (the Magnificent 7)", "Big Tech", "Apple, Microsoft, Nvidia, Alphabet, Amazon, Meta and Tesla: the seven largest US companies."),
    "defense-aeronautique": ("Defense and aerospace stocks", "defense and aerospace", "Rheinmetall, Safran, Airbus, Thales, Dassault Aviation, Lockheed Martin…"),
    "banques": ("Bank stocks", "banks", "BNP Paribas, Société Générale, the big European and US banks."),
    "petrole-energie": ("Oil and energy stocks", "oil and energy", "TotalEnergies, Shell, BP, ExxonMobil, Chevron… the oil and gas majors."),
    "energies-vertes": ("Utilities and clean energy stocks", "clean energy", "Engie, Iberdrola, Enel, RWE, NextEra… power producers and renewables."),
    "sante-pharma": ("Healthcare and pharma stocks", "healthcare", "Sanofi, Novo Nordisk, Eli Lilly, AstraZeneca, Johnson & Johnson…"),
    "automobile": ("Car maker stocks", "automotive", "Stellantis, Renault, BMW, Mercedes, Volkswagen, Tesla, Toyota… and Michelin."),
    "chine-emergents": ("China and emerging market stocks", "China and emerging markets", "Alibaba, JD.com, Tencent, Infosys, MercadoLibre, Vale… and emerging-market ETFs."),
    "consommation": ("Consumer staples stocks", "consumer staples", "Danone, Pernod Ricard, Coca-Cola, Procter & Gamble, McDonald's… often calmer than average."),
}


def pages_en(seo, anglais, langues, base, payload, dossier, csp, date, V=None):
    par_tk = {t["ticker"]: t for t in payload.get("titres", []) if t.get("prix")}
    e, slug = seo._e, seo.slug
    os.makedirs(os.path.join(dossier, "en", "themes"), exist_ok=True)
    faits, liens = [], []
    pct = lambda v: anglais._pct(v)
    for cle, _h, _c, _i, tks, _g in THEMES:
        if cle not in THEMES_EN:
            continue
        h1, court, intro = THEMES_EN[cle]
        items = [par_tk[t] for t in tks if t in par_tk]
        if len(items) < 4:
            continue
        rp = lambda t: t.get("risque_prevu") or {}
        pm = lambda t: (t.get("perf") or {}).get("1 mois")
        items.sort(key=lambda t: -(pm(t) or -9))
        nom = lambda t: e(langues.nom_intl(t["nom"]))
        lignes = "".join(
            f"<tr><td><a href='../stocks/{slug(t['ticker'])}.html'>{nom(t)}</a> <span class='muted'>{e(seo.aff_tk(t['ticker']))}</span></td>"
            f"<td class='m'>{anglais._px(t['prix'], t['devise'])}</td><td class='m'>{pct(pm(t))}</td>"
            f"<td class='m'>{('±' + str(round(rp(t)['mouvement'] * 100)) + '%') if rp(t).get('mouvement') else '—'}</td>"
            f"<td class='m'>{(str(round(rp(t)['chute'] * 100)) + '%') if rp(t).get('chute') is not None else '—'}</td></tr>"
            for t in items)
        fmt = lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v) * 100:.1f}%"
        corps = (f"<p class='muted'><a href='../themes.html'>All themes</a></p><h1>{e(h1)}: prices and forecasts</h1>"
                 f"<p class='muted'>Updated automatically · prices as of {e(date)}</p><p>{e(intro)}</p>"
                 + barres([(nom(t), pm(t)) for t in items], fmt=fmt, titre=f"{court[:1].upper() + court[1:]}: one-month change")
                 + "<div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='Theme table'><table>"
                 "<tr><th>Stock</th><th>Price</th><th>1 month</th><th>Expected swing</th><th title='Risk of a fall of more than 10% next month'>Fall risk*</th></tr>"
                 + lignes + "</table></div><p class='muted'>* Risk of a fall of more than 10% over the next month. Swings and fall risk are "
                 "what the AI forecasts best (<a href='../verified-calls.html'>calls checked in public</a>). The direction of prices stays very "
                 "uncertain. Not investment advice.</p><h2>Other themes</h2><ul class='liste'>"
                 + "".join(f"<li><a href='{c}.html'>{e(THEMES_EN[c][0])}</a></li>" for c in THEMES_EN if c != cle) + "</ul>")
        chemin = f"en/themes/{cle}.html"
        alt = {"fr": f"themes/{cle}.html", "en": chemin, "x-default": f"themes/{cle}.html"}
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(anglais._page(base, f"{h1}: forecasts and risk | {seo.NOM}", f"{intro} Prices, one-month change and AI forecasts of swings and fall risk.",
                                  chemin, corps, csp, alt))
        faits.append(chemin)
        liens.append((h1, f"themes/{cle}.html", intro))
    if liens:
        corps = ("<h1>Stocks by theme</h1><p class='muted'>Stocks tracked by the radar, grouped by theme, with daily AI forecasts.</p>"
                 + "".join(f"<a class='carte' style='display:block;margin:10px 0;text-decoration:none' href='{c}'><b>{e(h)}</b>"
                           f"<span class='muted' style='display:block;margin-top:4px'>{e(i)}</span></a>" for h, c, i in liens))
        with open(os.path.join(dossier, "en", "themes.html"), "w", encoding="utf-8") as f:
            f.write(anglais._page(base, f"Stocks by theme: luxury, AI, defense, banks | {seo.NOM}",
                                  "Stocks grouped by theme with daily AI forecasts: luxury, AI and chips, Big Tech, defense, banks, energy.",
                                  "en/themes.html", corps, csp, {"fr": "themes.html", "en": "en/themes.html", "x-default": "themes.html"}))
        faits.append("en/themes.html")
    # verified calls
    V = V or verifier(payload.get("titres", []))
    b = bilan(V["faits"])
    bt = bilan(V["faits"], True)
    pc = lambda v: "—" if v is None else f"{round(v * 100)}%"
    corps = ("<h1>The AI's confident calls, checked in public</h1><p>Every evening the radar records its <b>confident calls</b>: "
             "stocks for which it expects, with a clear margin, the coming month to be <b>more volatile</b> or <b>calmer</b> than recent "
             "weeks. Calls are saved before the outcome is known and checked here automatically 20 sessions later. Nothing is deleted.</p>")
    if b["n"]:
        corps += ("<div class='compteurs'>"
                  f"<div><b>{pc(b['taux'])}</b><span>confident calls right ({b['k']} of {b['n']})</span></div>"
                  + (f"<div><b>{pc(bt['taux'])}</b><span>very confident calls right ({bt['k']} of {bt['n']})</span></div>" if bt["n"] else "")
                  + f"<div><b>{V['attente']}</b><span>calls still running</span></div></div>")
        corps += ("<div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='Latest checked calls'><table>"
                  "<tr><th>Stock</th><th>Call date</th><th>AI said</th><th>Volatility before → after</th><th>Result</th></tr>"
                  + "".join(f"<tr><td><a href='stocks/{slug(f['ticker'])}.html'>{e(langues.nom_intl(f['nom']))}</a></td><td class='m'>{e(f['date'])}</td>"
                            f"<td>{'more volatile' if f['sens'] > 0 else 'calmer'}</td><td class='m'>{round(f['avant'] * 100)}% → {round(f['apres'] * 100)}%</td>"
                            f"<td>{'<span class=\"verdict ok\">✓ right</span>' if f['juste'] else '<span class=\"verdict ko\">✗ wrong</span>'}</td></tr>"
                            for f in V["faits"][:40]) + "</table></div>")
    else:
        corps += (f"<div class='carte'><b>First verdicts soon.</b><p style='margin:6px 0 0'>{V['attente']} calls are recorded and "
                  "waiting for their 20 sessions to end. This page fills itself every evening.</p></div>")
    corps += ("<h2>How it is checked</h2><p>Volatility before = the 20 sessions before the call; after = the 20 sessions after it. "
              "A call is right if volatility went the way the AI said. It is the exact rule used to test the AI on past years. "
              "Forecasting volatility is not forecasting direction. Educational project, not investment advice.</p>")
    with open(os.path.join(dossier, "en", "verified-calls.html"), "w", encoding="utf-8") as f:
        f.write(anglais._page(base, f"AI stock calls checked in public: real results | {seo.NOM}",
                              "The AI's confident calls are recorded in advance and checked in public 20 sessions later: "
                              + (f"{pc(b['taux'])} right out of {b['n']} so far." if b["n"] else "first verdicts coming."),
                              "en/verified-calls.html", corps, csp,
                              {"fr": "avis-surs-verifies.html", "en": "en/verified-calls.html", "x-default": "avis-surs-verifies.html"}))
    faits.append("en/verified-calls.html")
    return faits


def themes_noms() -> list:
    return [(cle, "actions " + court) for cle, _h, court, *_ in THEMES]


# ----------------------------------------------------------------------------
# Version 66 : données ouvertes (CSV + JSON) — tous les avis enregistrés, vérifiés ou en cours
# ----------------------------------------------------------------------------
def donnees_ouvertes(seo, base, dossier, csp, V):
    import csv
    import io
    os.makedirs(os.path.join(dossier, "donnees-ouvertes"), exist_ok=True)
    lignes = []
    for f in V.get("faits", []):
        lignes.append({"date_avis": f["date"], "ticker": f["ticker"], "nom": f["nom"], "avis": "plus_agite" if f["sens"] > 0 else "plus_calme",
                       "niveau": "tres_sur" if f["tres"] else "sur", "agitation_avant": round(f["avant"], 5),
                       "agitation_apres": round(f["apres"], 5), "fin_verification": f["fin"], "resultat": "juste" if f["juste"] else "faux"})
    for f in V.get("en_cours", []):
        lignes.append({"date_avis": f["date"], "ticker": f["ticker"], "nom": f["nom"], "avis": "plus_agite" if f["sens"] > 0 else "plus_calme",
                       "niveau": "tres_sur" if f["tres"] else "sur", "agitation_avant": round(f["avant"], 5),
                       "agitation_apres": "", "fin_verification": "", "resultat": "en_cours"})
    lignes.sort(key=lambda r: (r["date_avis"], r["ticker"]))
    champs = ["date_avis", "ticker", "nom", "avis", "niveau", "agitation_avant", "agitation_apres", "fin_verification", "resultat"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=champs, lineterminator="\n")
    w.writeheader()
    w.writerows(lignes)
    with open(os.path.join(dossier, "donnees-ouvertes", "avis-ia.csv"), "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    meta = {"source": seo.NOM, "page": (base or "") + "avis-surs-verifies.html", "licence": (base or "") + "credits.html",
            "description": "Avis sûrs de l'IA sur l'agitation du mois suivant (20 séances), enregistrés avant de connaître la suite. "
                           "agitation = écart-type annualisé des rendements quotidiens (log), sur les 20 séances avant / après l'avis.",
            "mis_a_jour": datetime.now().strftime("%Y-%m-%d"), "avis": lignes}
    with open(os.path.join(dossier, "donnees-ouvertes", "avis-ia.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, separators=(",", ":"))
    nb_v = len(V.get("faits", []))
    nb_c = len(V.get("en_cours", []))
    e = seo._e
    corps = ("<h1>Données ouvertes</h1>"
             "<p>Tous les avis sûrs de l'IA, enregistrés chaque soir avant de connaître la suite, avec leur résultat une fois vérifiés. "
             "Les fichiers se mettent à jour automatiquement : tu peux refaire les calculs toi-même.</p>"
             "<div class='compteurs'>"
             f"<div><b>{nb_v + nb_c}</b><span>avis enregistrés</span></div>"
             f"<div><b>{nb_v}</b><span>avis vérifiés</span></div>"
             f"<div><b>{nb_c}</b><span>avis en cours</span></div></div>"
             "<p><a class='btn' href='donnees-ouvertes/avis-ia.csv' download>Télécharger le CSV</a> "
             "<a class='btn' href='donnees-ouvertes/avis-ia.json' download>Télécharger le JSON</a></p>"
             "<h2>Les colonnes</h2><ul>"
             "<li><b>date_avis</b> : le soir où l'avis a été enregistré.</li>"
             "<li><b>ticker</b>, <b>nom</b> : le titre concerné.</li>"
             "<li><b>avis</b> : <code>plus_agite</code> ou <code>plus_calme</code> que les 20 dernières séances, sur les 20 séances suivantes.</li>"
             "<li><b>niveau</b> : <code>sur</code> ou <code>tres_sur</code>.</li>"
             "<li><b>agitation_avant</b>, <b>agitation_apres</b> : écart-type annualisé des rendements quotidiens (0,25 = 25 %).</li>"
             "<li><b>resultat</b> : <code>juste</code>, <code>faux</code> ou <code>en_cours</code>.</li></ul>"
             "<h2>Conditions</h2><p>Usage personnel, scolaire ou de recherche libre, en citant « Radar Bourse » et l'adresse du site. "
             "Voir <a href='credits.html'>droits d'auteur et crédits</a>. Les cours qui servent à la vérification viennent de Yahoo Finance "
             "et Binance ; ils ne sont pas redistribués ici.</p>"
             "<p class='muted'>Projet éducatif, pas un conseil en investissement.</p>")
    jsonld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Avis de l'IA de Radar Bourse, vérifiés en public",
              "description": meta["description"], "isAccessibleForFree": True, "dateModified": meta["mis_a_jour"],
              "creator": {"@type": "Organization", "name": seo.NOM}, "license": meta["licence"],
              "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": (base or "") + "donnees-ouvertes/avis-ia.csv"},
                               {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": (base or "") + "donnees-ouvertes/avis-ia.json"}]}
    with open(os.path.join(dossier, "donnees-ouvertes.html"), "w", encoding="utf-8") as fh:
        fh.write(seo._page(base, f"Données ouvertes : les avis de l'IA en CSV et JSON | {seo.NOM}",
                           "Téléchargez tous les avis de l'IA de Radar Bourse, enregistrés à l'avance et vérifiés 20 séances plus tard : CSV et JSON mis à jour chaque jour.",
                           "donnees-ouvertes.html", corps, jsonld, csp))
    return ["donnees-ouvertes.html"]


# ----------------------------------------------------------------------------
# Version 66 : graphique « agitation sur un an + agitation prévue » des fiches
# ----------------------------------------------------------------------------
def agitation_svg(t: dict, fr: bool = True) -> str:
    s = t.get("serie") or {}
    c = [v for v in (s.get("c") or [])]
    rq = t.get("risque_prevu") or {}
    pred = rq.get("vol")
    if len(c) < 120 or not pred or any(v is None or v <= 0 for v in c[-60:]):
        return ""
    r = [math.log(c[i] / c[i - 1]) if c[i] and c[i - 1] and c[i] > 0 and c[i - 1] > 0 else None for i in range(1, len(c))]
    vols = []
    for i in range(20, len(r) + 1):
        seg = [x for x in r[i - 20:i] if x is not None]
        if len(seg) < 15:
            vols.append(None)
            continue
        m = sum(seg) / len(seg)
        vols.append(math.sqrt(sum((x - m) ** 2 for x in seg) / (len(seg) - 1)) * math.sqrt(252))
    vols = vols[-250:]
    if sum(v is not None for v in vols) < 60 or vols[-1] is None:
        return ""
    ok = sorted(v for v in vols if v is not None)
    normale = ok[len(ok) // 2]
    W, H, pl, pr, pt, pb = 800, 250, 6, 190, 16, 24
    n = len(vols) - 1 + 20
    vmax = max(max(ok), pred, normale) * 1.12
    X = lambda i: pl + i / n * (W - pl - pr)
    Y = lambda v: pt + (1 - v / vmax) * (H - pt - pb)
    pts = " ".join(f"{X(i):.0f},{Y(v):.0f}" for i, v in enumerate(vols) if v is not None)
    i0 = len(vols) - 1
    x0, y0, x1, y1 = X(i0), Y(vols[-1]), X(n), Y(pred)
    pc = lambda v: f"{round(v * 100)} %" if fr else f"{round(v * 100)}%"
    grille = "".join(f"<line class='cs-grille' x1='{pl}' x2='{W - pr}' y1='{Y(g):.0f}' y2='{Y(g):.0f}'/>"
                     for g in (vmax * .25, vmax * .5, vmax * .75))
    lib_p = "Prévu" if fr else "Forecast"
    lib_a = "Actuel" if fr else "Now"
    lib_n = "Sa normale" if fr else "Its normal"
    ya, yp = y0, y1
    if abs(ya - yp) < 30:   # étiquettes sans chevauchement
        ya, yp = (ya - 15, yp + 15) if ya <= yp else (ya + 15, yp - 15)
    titre = (f"Agitation de {t.get('nom', '')} sur un an et agitation prévue le mois prochain" if fr
             else f"{t.get('nom', '')}: volatility over one year and forecast for next month")
    svg = (f"<svg viewBox='0 0 {W} {H}' role='img' aria-label=\"{titre.replace(chr(34), '')}\">{grille}"
           f"<line class='cs-auj' x1='{x0:.0f}' x2='{x0:.0f}' y1='{pt}' y2='{H - pb}'/>"
           f"<line class='ag-norm' x1='{pl}' x2='{W - pr}' y1='{Y(normale):.0f}' y2='{Y(normale):.0f}'/>"
           f"<polyline class='cs-ligne' pathLength='1' points='{pts}'/>"
           f"<line class='cs-med' x1='{x0:.0f}' y1='{y0:.0f}' x2='{x1:.0f}' y2='{y1:.0f}'/>"
           f"<circle class='cs-point' cx='{x0:.0f}' cy='{y0:.0f}' r='5'/><circle class='ag-pred' cx='{x1:.0f}' cy='{y1:.0f}' r='6'/>"
           f"<text class='cs-t' x='{x1 + 12:.0f}' y='{yp + 5:.0f}'>{lib_p} {pc(pred)}</text>"
           f"<text class='cs-d' x='{x1 + 12:.0f}' y='{ya + 5:.0f}'>{lib_a} {pc(vols[-1])}</text>"
           f"<text class='cs-d' x='{pl + 4}' y='{Y(normale) - 6:.0f}'>{lib_n} {pc(normale)}</text></svg>")
    leg = ("<p class='cs-leg'><span>Agitation des 20 dernières séances</span><span class='l-med'>Prévision de l'IA (mois prochain)</span>"
           "<span class='l-50'>Sa normale sur un an</span></p>" if fr else
           "<p class='cs-leg'><span>Volatility over the last 20 sessions</span><span class='l-med'>AI forecast (next month)</span>"
           "<span class='l-50'>Its one-year normal</span></p>")
    return f"<figure class='courbe'><figcaption class='muted' style='font-size:14px;margin-bottom:6px'>{titre}</figcaption>{svg}{leg}</figure>"


def avis_passes_html(ticker: str, V: dict, fr: bool = True, prefixe: str = "../") -> str:
    """Version 66.1 : sur chaque fiche, les avis passés de l'IA pour ce titre (justes, faux, en cours)."""
    if not V:
        return ""
    faits = [f for f in V.get("faits", []) if f["ticker"] == ticker]
    cours = [f for f in V.get("en_cours", []) if f["ticker"] == ticker]
    if not faits and not cours:
        return ""
    vus, uniques = set(), []
    for f in faits:   # un avis par date suffit à l'affichage
        if f["date"] not in vus:
            vus.add(f["date"])
            uniques.append(f)
    k = sum(f["juste"] for f in faits)
    if fr:
        tete = ("<h2>Les avis passés de l'IA sur ce titre</h2>"
                + (f"<p><b>{k} juste{'s' if k > 1 else ''} sur {len(faits)}</b> avis vérifié{'s' if len(faits) > 1 else ''}"
                   f"{f', et {len(cours)} en cours de vérification' if cours else ''}. "
                   if faits else f"<p>{len(cours)} avis enregistré{'s' if len(cours) > 1 else ''}, en cours de vérification (20 séances). ")
                + f"<a href='{prefixe}avis-surs-verifies.html'>Tous les avis vérifiés</a></p>")
        lignes = "".join(
            f"<li>{f['date'][8:10]}/{f['date'][5:7]} : {'plus agité' if f['sens'] > 0 else 'plus calme'} "
            f"({round(f['avant'] * 100)} % → {round(f['apres'] * 100)} %) "
            f"{'<span class="verdict ok">✓ juste</span>' if f['juste'] else '<span class="verdict ko">✗ faux</span>'}</li>"
            for f in uniques[:6])
    else:
        tete = ("<h2>The AI's past calls on this asset</h2>"
                + (f"<p><b>{k} right out of {len(faits)}</b> checked call{'s' if len(faits) > 1 else ''}{f', {len(cours)} still running' if cours else ''}. "
                   if faits else f"<p>{len(cours)} call{'s' if len(cours) > 1 else ''} recorded, being checked (20 sessions). ")
                + f"<a href='{prefixe}verified-calls.html'>All checked calls</a></p>")
        lignes = "".join(
            f"<li>{f['date']}: {'more volatile' if f['sens'] > 0 else 'calmer'} "
            f"({round(f['avant'] * 100)}% → {round(f['apres'] * 100)}%) "
            f"{'<span class="verdict ok">✓ right</span>' if f['juste'] else '<span class="verdict ko">✗ wrong</span>'}</li>"
            for f in uniques[:6])
    return tete + (f"<ul>{lignes}</ul>" if lignes else "")


# ----------------------------------------------------------------------------
# Version 67 : la réponse courte des pages fixes (« ça monte ou ça baisse ? », « de combien ? »)
# ----------------------------------------------------------------------------
def avis_ia(t: dict, modele: dict | None = None):
    """Version 67.5 : l'avis de l'IA, toujours donné — (proba, sens ±1, confiance « faible » / « moyenne » / « forte »)."""
    p = t.get("proba_ia") if t.get("source_proba") == "marche" and t.get("proba_ia") is not None else t.get("proba_hausse")
    if p is None:
        return None, 0, "faible"
    marge = max(((modele or {}).get("avis_net") or {}).get("marge") or 0, .02)
    faible = t.get("avis_net") is False or t.get("source_proba") == "marche" or abs(p - .5) < marge
    conf = "faible" if faible else ("forte" if t.get("confiance") == "forte" else "moyenne")
    return p, (1 if p >= .5 else -1), conf


LIB_SENS = {(1, True): ("Légèrement à la hausse", "Slightly up"), (1, False): ("Plutôt à la hausse", "Leaning up"),
            (-1, True): ("Légèrement à la baisse", "Slightly down"), (-1, False): ("Plutôt à la baisse", "Leaning down")}
LIB_CONF = {"faible": ("confiance faible", "low confidence"), "moyenne": ("confiance moyenne", "medium confidence"),
            "forte": ("confiance forte", "high confidence")}


def reponse_courte_html(t: dict, modele: dict | None, fr: bool = True, px=None) -> str:
    p, sens, conf = avis_ia(t, modele)
    if p is None:
        return ""
    M = modele or {}
    AN = M.get("avis_net") or {}
    k = 0 if fr else 1
    titre = LIB_SENS[(sens, conf == "faible")][k]
    ch = round(p * 100) if sens > 0 else 100 - round(p * 100)
    prec = AN.get("precision") if (conf != "faible" and AN.get("precision")) else M.get("precision")
    base = AN.get("base") if (conf != "faible" and AN.get("precision")) else M.get("precision_base")
    f = t.get("fourchette") or []
    mv = (t.get("risque_prevu") or {}).get("mouvement")
    px = px or (lambda v, d: f"{v:,.2f} {d}")
    if fr:
        expl = (f"<b>{ch} chances sur 100</b> de finir plus {'haut' if sens > 0 else 'bas'} dans un mois, selon l'IA."
                + (" <span class='muted'>Confiance faible : dans ce genre de cas, l'IA se trompe souvent. Regarde surtout l'agitation prévue.</span>"
                   if conf == "faible" else ""))
        fiab = (f" <span class='muted'>Fiabilité réelle : sur des années jamais vues, l'IA a trouvé le bon sens {round(prec * 100)} fois sur 100 "
                f"(en répondant toujours pareil : {round(base * 100)}).</span>") if prec and base else ""
        k1, k2, lib = "Ça monte ou ça baisse ?", "De combien ça peut bouger ?", "L'avis de l'IA"
        mv_t = f"±{round(mv * 100)} % en un mois" if mv else ""
        fo = f"8 fois sur 10, entre {px(f[0], t.get('devise', ''))} et {px(f[1], t.get('devise', ''))}" if len(f) == 2 else ""
    else:
        expl = (f"<b>{ch} chances in 100</b> of ending {'higher' if sens > 0 else 'lower'} in a month, according to the AI."
                + (" <span class='muted'>Low confidence: in cases like this the AI is often wrong. Look mainly at the expected volatility.</span>"
                   if conf == "faible" else ""))
        fiab = (f" <span class='muted'>Real reliability: on years it never saw, the AI got the direction right {round(prec * 100)} times in 100 "
                f"(always giving the same answer: {round(base * 100)}).</span>") if prec and base else ""
        k1, k2, lib = "Up or down?", "How much can it move?", "The AI's call"
        mv_t = f"±{round(mv * 100)}% in a month" if mv else ""
        fo = f"8 times out of 10, between {px(f[0], t.get('devise', ''))} and {px(f[1], t.get('devise', ''))}" if len(f) == 2 else ""
    cls = "rc-up" if sens > 0 else "rc-down"
    ic = "↑" if sens > 0 else "↓"
    deux = (f"<div class='rc-q rc-q2'><span class='rc-ic' aria-hidden='true'>↕</span><div><span class='rc-k'>{k2}</span>"
            f"<b>{mv_t}</b>{f'<span class=rc-s>{fo}</span>' if fo else ''}</div></div>") if (mv_t or fo) else ""
    return (f"<div class='carte rc {cls}{' rc-faible' if conf == 'faible' else ''}'><div class='rc-l'>{lib} "
            f"<span class='conf conf-{conf}'>{LIB_CONF[conf][k]}</span></div>"
            f"<div class='rc-q rc-q1'><span class='rc-ic' aria-hidden='true'>{ic}</span><div><span class='rc-k'>{k1}</span><b>{titre}</b></div></div>"
            f"<div class='rc-jauge' role='img' aria-label='{round(p * 100)} / 100'><i style='--p:{round(p * 100)}%'></i><span>{'baisse' if fr else 'down'}</span>"
            f"<span>50/50</span><span>{'hausse' if fr else 'up'}</span></div>"
            f"<p class='rc-t'>{expl}{fiab}</p>{deux}</div>")


CSS_RC = """
.rc{padding:18px 20px;margin:14px 0;border-left:4px solid var(--muted)}.rc-up{border-left-color:var(--up)}.rc-down{border-left-color:var(--down)}
.rc-l{font-size:12.5px;color:var(--muted);font-weight:600;margin-bottom:8px}
.rc-q{display:flex;gap:14px;align-items:center}.rc-q b{display:block;font-size:24px;line-height:1.2}.rc-q2 b{font-size:19px}
.rc-k{display:block;font-size:13.5px;color:var(--muted)}.rc-s{display:block;font-size:14px;color:var(--muted);margin-top:2px}
.rc-ic{flex:none;display:grid;place-items:center;width:46px;height:46px;border-radius:50%;font-size:24px;font-weight:700;background:var(--bg);color:var(--muted)}
.rc-up .rc-q1 .rc-ic{background:var(--up-soft);color:var(--up)}.rc-down .rc-q1 .rc-ic{background:var(--down-soft);color:var(--down)}
.rc-up .rc-q1 b{color:var(--up)}.rc-down .rc-q1 b{color:var(--down)}
.rc-jauge{position:relative;margin:14px 0 4px;height:8px;border-radius:4px;background:linear-gradient(90deg,var(--down) 0%,var(--line) 42%,var(--line) 58%,var(--up) 100%)}
.rc-jauge i{position:absolute;top:50%;left:var(--p);width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:var(--ink);border:3px solid var(--surface);box-shadow:0 1px 4px rgba(0,0,0,.3)}
.rc-jauge span{position:absolute;top:12px;font-size:11.5px;color:var(--muted)}.rc-jauge span:nth-of-type(1){left:0}.rc-jauge span:nth-of-type(2){left:50%;transform:translateX(-50%)}.rc-jauge span:nth-of-type(3){right:0}
.rc-t{margin:26px 0 12px;font-size:15px}
.conf{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:99px;font-size:11.5px;font-weight:600;background:var(--bg);color:var(--muted)}.conf-forte{background:var(--accent-soft);color:var(--accent)}.conf-moyenne{color:var(--ink)}.rc-faible .rc-q1 b{opacity:.85}.rc-q2{padding-top:12px;border-top:1px solid var(--line)}
@media (prefers-reduced-motion:no-preference){.rc-jauge i{animation:rc-glisse .9s cubic-bezier(.2,.8,.2,1) both}@keyframes rc-glisse{from{left:50%;opacity:0}to{left:var(--p);opacity:1}}}
"""
CSS = CSS + CSS_RC


def reponse_mini(t: dict, question: str, reponse: str, mouvement: str = "", lib_mouvement: str = "") -> str:
    """Version 67 : la réponse courte sans phrase à traduire (pages des 26 autres langues) : flèche, jauge, chiffres."""
    p = t.get("proba_hausse")
    if p is None:
        return ""
    p, sens, _conf = avis_ia(t)
    cls = "rc-up" if sens > 0 else "rc-down"
    ic = "↑" if sens > 0 else "↓"
    ch = round(p * 100)
    deux = (f"<div class='rc-q rc-q2'><span class='rc-ic' aria-hidden='true'>↕</span><div><span class='rc-k'>{lib_mouvement}</span>"
            f"<b><bdi>{mouvement}</bdi></b></div></div>") if mouvement else ""
    return (f"<div class='carte rc {cls}'><div class='rc-q rc-q1'><span class='rc-ic' aria-hidden='true'>{ic}</span>"
            f"<div><span class='rc-k'>{question}</span><b>{reponse}</b></div></div>"
            f"<div class='rc-jauge' role='img' aria-label='{ch} / 100'><i style='--p:{ch}%'></i><span>0</span><span>50</span><span>100</span></div>"
            f"<p class='rc-t'></p>{deux}</div>")
