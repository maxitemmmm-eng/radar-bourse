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
    faits, attente, prochains = [], 0, []
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
                continue
            vr = _vol_realisee(c, idx, HORIZON)
            if vr is None:
                continue
            juste = (vr > v20) == (sens > 0)
            faits.append({"date": p["date"], "fin": dates[idx + HORIZON], "ticker": tk, "nom": noms.get(tk, tk),
                          "sens": sens, "tres": bool(tres), "avant": v20, "apres": vr, "juste": juste})
    faits.sort(key=lambda f: (f["fin"], f["date"]), reverse=True)
    return {"faits": faits, "attente": attente, "premier_attente": min(prochains) if prochains else None}


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
def page_verifies(seo, base, payload, dossier, csp):
    V = verifier(payload.get("titres", []))
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
    corps += ("<h2>Comment c'est vérifié</h2><ul>"
              "<li>L'agitation, c'est l'ampleur des mouvements de prix (à la hausse comme à la baisse), ramenée à une année.</li>"
              "<li>« Avant » : l'agitation des 20 séances qui précèdent l'avis. « Après » : celle des 20 séances qui le suivent.</li>"
              "<li>L'avis est juste si « après » est plus grand que « avant » quand l'IA disait « plus agité », et plus petit quand elle disait « plus calme ».</li>"
              "<li>C'est exactement la règle utilisée pour mesurer l'IA sur les années passées (<a href='fiche-technique-ia.html'>fiche technique</a>).</li>"
              "</ul><p class='muted'>Prévoir l'agitation n'est pas prévoir le sens : un titre peut être plus calme et baisser quand même. "
              "Projet éducatif, pas un conseil en investissement.</p>")
    jsonld = {"@context": "https://schema.org", "@type": "Dataset", "name": h1, "isAccessibleForFree": True,
              "description": "Avis de l'IA sur l'agitation du mois suivant, enregistrés à l'avance et vérifiés 20 séances plus tard.",
              "creator": {"@type": "Organization", "name": seo.NOM}, "license": "https://opensource.org/licenses/MIT"}
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
