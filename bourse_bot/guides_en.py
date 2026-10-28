"""English guides (version 47): translations of the French guides, each linked to its French twin (hreflang)."""
from __future__ import annotations

import html
import os
import re
from datetime import datetime

from . import seo

CATEGORIES_EN = {"debuter": "Getting started", "argent": "Easy money, trading and scams: the truth",
                 "crypto": "Cryptocurrencies", "marches": "Stocks, ETFs and markets"}

GUIDES_EN = []
for _nom in ("guides_en_1", "guides_en_2", "guides_en_3", "guides_en_4"):
    try:
        _m = __import__(f"{__package__}.{_nom}", fromlist=["x"])
    except ImportError:
        continue
    for _k in dir(_m):
        if _k.startswith("GUIDES_EN_"):
            GUIDES_EN.extend(getattr(_m, _k))
IDS_EN = {g["i"] for g in GUIDES_EN}


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _md(txt):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", _e(txt))


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    from .anglais import _page, _px
    from .guides import GUIDES
    fr = {g["i"]: g for g in GUIDES}
    par_tk = {t.get("ticker"): t for t in payload.get("titres", []) if t.get("prix")}
    date = payload.get("date_donnees", "")
    os.makedirs(os.path.join(dossier, "en", "guides"), exist_ok=True)
    urls = []
    for g in GUIDES_EN:
        voisins = [v for v in GUIDES_EN if v["c"] == g["c"] and v["i"] != g["i"]]
        ordre = [v["i"] for v in GUIDES_EN if v["c"] == g["c"]]
        k = ordre.index(g["i"])
        voisins = (voisins[k:] + voisins[:k])[:5]
        corps = (f"<p class='muted'><a href='../guides.html'>Guides</a> · {_e(CATEGORIES_EN[g['c']])}</p>"
                 f"<h1>{_e(g['h'])}</h1><div class='carte'><p><b>In short:</b> {_md(g['r'])}</p></div>")
        for h2, txt in g.get("p", []):
            corps += f"<h2>{_e(h2)}</h2>" + "".join(f"<p>{_md(x)}</p>" for x in txt.split("\n\n"))
        lignes = []
        for tk in (g.get("k") or (fr.get(g["i"]) or {}).get("k") or []):
            t = par_tk.get(tk)
            if not t:
                continue
            rp = t.get("risque_prevu") or {}
            mv, ch = rp.get("mouvement"), rp.get("chute")
            lignes.append(f"<tr><td><a href='../stocks/{seo.slug(tk)}.html'>{_e(t.get('nom') or tk)}</a></td><td class='m'>{_px(t['prix'], t.get('devise', ''))}</td>"
                          f"<td class='m'>{'±' + str(round(mv * 100)) + '%' if mv else '–'}</td>"
                          f"<td class='m'>{str(round(ch * 100)) + '%' if ch is not None else '–'}</td></tr>")
        if lignes:
            corps += ("<h2>Today's numbers</h2><div class='carte' style='overflow-x:auto'><table><tr><td><b>Asset</b></td><td><b>Price</b></td>"
                      "<td><b>Expected move over a month</b></td><td><b>Risk of a drop of more than 10%</b></td></tr>" + "".join(lignes) + "</table></div>"
                      f"<p class='muted'>Prices as of {_e(date)}, updated automatically. Volatility and drop risk are what the radar's AIs forecast best; "
                      "they are not buy or sell recommendations.</p>")
        if g.get("q"):
            corps += "<h2>FAQ</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_md(a)}</p>" for q, a in g["q"])
        corps += ("<h2>Read next</h2><ul class='liste'>" + "".join(f"<li><a href='{v['i']}.html'>{_e(v['h'])}</a></li>" for v in voisins)
                  + f"<li><a href='../../guides/{g['i']}.html' hreflang='fr' lang='fr'>Version française</a></li></ul>")
        chemin = f"en/guides/{g['i']}.html"
        url = (base + chemin) if base else chemin
        faq = [(g["h"], g["r"])] + list(g.get("q", []))
        jsonld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Article", "headline": g["h"][:110], "description": g["d"], "inLanguage": "en", "url": url,
             "dateModified": datetime.now().strftime("%Y-%m-%d"), "author": {"@type": "Organization", "name": seo.NOM},
             "publisher": {"@type": "Organization", "name": seo.NOM}},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.replace("**", "")}} for q, a in faq]}]}
        alternates = {"en": chemin, "fr": f"guides/{g['i']}.html", "x-default": f"guides/{g['i']}.html"}
        page = _page(base, g["t"] + f" | {seo.NOM}", g["d"], chemin, corps, csp, alternates)
        # données structurées propres au guide (en plus de celles de la page)
        page = page.replace("</head>", f'<script type="application/ld+json">{_json(jsonld)}</script>\n</head>', 1)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "weekly", "0.6"))
    corps = ("<h1>Stock market and crypto guides</h1><p>The questions everyone asks, with honest answers: no promise of easy money, "
             "verifiable numbers and the real risks.</p>")
    for c, lib in CATEGORIES_EN.items():
        items = [g for g in GUIDES_EN if g["c"] == c]
        if items:
            corps += f"<h2>{_e(lib)}</h2><ul class='liste'>" + "".join(f"<li><a href='guides/{g['i']}.html'>{_e(g['h'])}</a></li>" for g in items) + "</ul>"
    with open(os.path.join(dossier, "en", "guides.html"), "w", encoding="utf-8") as f:
        f.write(_page(base, f"Stock market and crypto guides for beginners | {seo.NOM}",
                      "Investing for beginners, small budgets, crypto, ETFs, scams, easy money: honest, simple guides.",
                      "en/guides.html", corps, csp, {"en": "en/guides.html", "fr": "guides.html", "x-default": "guides.html"}))
    urls.append(("en/guides.html", "weekly", "0.7"))
    return urls


def _json(d):
    import json
    return json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
