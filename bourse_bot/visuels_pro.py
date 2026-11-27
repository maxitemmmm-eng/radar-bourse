"""Version 94 : les visuels que les grands sites ont et que Radar Bourse n'avait pas (inspirés, jamais copiés).

- Bulles du marché (idée popularisée par les « crypto bubbles ») : chaque crypto ou action est une bulle dont la taille
  suit l'ampleur du mouvement et la couleur le sens ; on peut les attraper, elles s'écartent ; un clic ouvre la fiche.
- Thermomètre du marché (comme les indices « peur et avidité ») : calcul maison, à partir des seuls titres suivis,
  avec le détail de ses 5 ingrédients. Ce n'est pas une prévision.
- Saison des altcoins (comme l'indice de CoinMarketCap) : la part des cryptos suivies qui ont fait mieux que le bitcoin
  sur 3 mois.
- Profil du titre (comme le « flocon » de Simply Wall St, autre forme et autres critères) : 5 critères notés de 0 à 100
  en comparant le titre aux autres titres suivis de même nature (actions ou cryptos).
- Jauge technique (comme les « notes techniques » de TradingView) : l'aiguille suit le score technique du radar.
- Saisonnalité (comme les cartes de rendements mensuels) : la hausse ou la baisse de chaque mois, sur 10 ans au plus.
Toutes les données viennent des cours déjà suivis par le site : rien d'inventé, rien d'acheté.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


# ----------------------------------------------------------------------------------------------------------------
# Données (Python)
# ----------------------------------------------------------------------------------------------------------------
def saison(close: pd.Series, ans: int = 10) -> dict | None:
    """Rendements mensuels (fin de mois à fin de mois) sur `ans` années au plus. Le mois en cours est inclus jusqu'au jour."""
    c = close.dropna()
    if len(c) < 120:
        return None
    try:
        c.index = pd.DatetimeIndex(c.index).tz_localize(None) if getattr(c.index, "tz", None) else pd.DatetimeIndex(c.index)
    except Exception:
        return None
    fm = c.resample("ME").last()
    r = fm.pct_change().dropna()
    if len(r) < 6:
        return None
    r = r[r.index.year >= r.index.year.max() - ans + 1]
    annees = sorted(set(r.index.year))
    m = [[None] * 12 for _ in annees]
    for d, v in r.items():
        if np.isfinite(v):
            m[annees.index(d.year)][d.month - 1] = round(float(v), 4)
    return {"annees": annees, "m": m}


def _rangs(vals: list) -> dict:
    v = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    v.sort()
    return v


def _pct(ref, x):
    if x is None or not np.isfinite(x) or not len(ref):
        return None
    return float(np.searchsorted(ref, x, "right") / len(ref) * 100)


def profils(titres: list) -> dict:
    """Profil de chaque titre : 5 critères de 0 à 100, comparé aux titres suivis de même nature."""
    groupes = {"crypto": [t for t in titres if t.get("marche") == "crypto"],
               "actions": [t for t in titres if t.get("marche") not in ("crypto", "tendances")]}
    out = {}
    for g, L in groupes.items():
        if len(L) < 10:
            continue
        get = {
            "calme": lambda t: -((t.get("risque_prevu") or {}).get("mouvement") or np.nan),
            "solidite": lambda t: -((t.get("risque_prevu") or {}).get("chute") or np.nan),
            "tendance": lambda t: (t.get("perf") or {}).get("6 mois"),
            "elan": lambda t: (t.get("perf") or {}).get("1 mois"),
            "ia": lambda t: t.get("proba_hausse"),
        }
        if g == "actions":
            get["dividende"] = lambda t: t.get("div")
        refs = {k: _rangs([f(t) for t in L]) for k, f in get.items()}
        for t in L:
            p = {}
            for k, f in get.items():
                try:
                    x = f(t)
                    x = float(x) if x is not None else None
                except (TypeError, ValueError):
                    x = None
                p[k] = None if x is None or not math.isfinite(x) else round(_pct(refs[k], x))
            if g == "actions" and p.get("dividende") is None:
                p.pop("dividende", None)
            out[t["ticker"]] = {"groupe": g, "notes": p}
    return out


NOMS_AXES = {"calme": "Calme", "solidite": "Solidité", "tendance": "Tendance 6 mois", "elan": "Élan 1 mois",
             "ia": "Avis de l'IA", "dividende": "Dividende"}
AIDE_AXES = {"calme": "agitation prévue faible", "solidite": "risque de forte chute faible", "tendance": "hausse sur 6 mois",
             "elan": "hausse sur 1 mois", "ia": "chances de hausse selon l'IA", "dividende": "rendement du dividende"}


# ----------------------------------------------------------------------------------------------------------------
# Dessins (SVG, pages fixes)
# ----------------------------------------------------------------------------------------------------------------
def _e(s):
    import html
    return html.escape(str(s), quote=True)


def svg_profil(pr: dict | None, nom: str = "") -> str:
    if not pr:
        return ""
    notes = {k: v for k, v in pr["notes"].items() if v is not None}
    if len(notes) < 4:
        return ""
    axes = list(notes)
    n, R, cx, cy = len(axes), 84, 210, 124
    pt = lambda i, r: (cx + r * math.sin(2 * math.pi * i / n), cy - r * math.cos(2 * math.pi * i / n))
    grille = "".join(f"<polygon points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in (pt(i, R * k / 4) for i in range(n)))}' class='vp-g'/>" for k in (1, 2, 3, 4))
    rayons = "".join(f"<line x1='{cx}' y1='{cy}' x2='{pt(i, R)[0]:.1f}' y2='{pt(i, R)[1]:.1f}' class='vp-g'/>" for i in range(n))
    forme = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, R * max(4, notes[a]) / 100) for i, a in enumerate(axes)))
    etiq = ""
    for i, a in enumerate(axes):
        x, y = pt(i, R + 18)
        anc = "middle" if abs(x - cx) < 8 else ("start" if x > cx else "end")
        etiq += f"<text x='{x:.1f}' y='{y + 4:.1f}' text-anchor='{anc}' class='vp-t'>{_e(NOMS_AXES[a])} <tspan class='vp-n'>{notes[a]}</tspan></text>"
    moy = round(sum(notes.values()) / len(notes))
    grp = "cryptos" if pr["groupe"] == "crypto" else "actions"
    lib = "; ".join(f"{NOMS_AXES[a]} {notes[a]} sur 100" for a in axes)
    return (f"<figure class='vp-fig'><svg viewBox='0 0 420 252' class='vp-radar' role='img' aria-label='Profil de {_e(nom)} : {_e(lib)}'>{grille}{rayons}"
            f"<polygon points='{forme}' class='vp-forme'/>{etiq}</svg>"
            f"<figcaption><b>Profil : {moy} / 100 en moyenne.</b> Chaque critère compare {_e(nom)} aux autres {grp} suivies "
            f"(100 = le mieux placé). Une photo du jour, pas une recommandation.</figcaption></figure>")


def svg_saison(s: dict | None, nom: str = "") -> str:
    if not s or not s.get("annees"):
        return ""
    A, M = s["annees"], s["m"]
    vals = [abs(v) for ligne in M for v in ligne if v is not None]
    if len(vals) < 6:
        return ""
    lim = max(0.02, float(np.quantile(vals, 0.9)))
    cw, ch, gx, gy = 40, 22, 48, 22
    W, H = gx + 12 * cw + 4, gy + len(A) * ch + 26
    cases = ""
    for j, an in enumerate(A):
        cases += f"<text x='{gx - 6}' y='{gy + j * ch + 15}' text-anchor='end' class='vp-t'>{an}</text>"
        for i in range(12):
            v = M[j][i]
            x, y = gx + i * cw, gy + j * ch
            if v is None:
                cases += f"<rect x='{x + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' rx='3' class='vp-vide'/>"
                continue
            a = min(1.0, abs(v) / lim)
            coul = "68,224,156" if v >= 0 else "255,95,95"
            txt = f"{v * 100:+.0f}".replace("-", "−")
            cases += (f"<rect x='{x + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' rx='3' fill='rgba({coul},{0.12 + 0.78 * a:.2f})'>"
                      f"<title>{MOIS_COURTS[i]} {an} : {v * 100:+.1f} %</title></rect>"
                      f"<text x='{x + cw / 2}' y='{y + 15}' text-anchor='middle' class='vp-c'>{txt}</text>")
    tete = "".join(f"<text x='{gx + i * cw + cw / 2}' y='14' text-anchor='middle' class='vp-t'>{MOIS_COURTS[i][:4]}</text>" for i in range(12))
    # moyenne et part des hausses de chaque mois
    pied = ""
    for i in range(12):
        col = [M[j][i] for j in range(len(A)) if M[j][i] is not None]
        if len(col) >= 3:
            h = sum(1 for v in col if v > 0)
            pied += f"<text x='{gx + i * cw + cw / 2}' y='{gy + len(A) * ch + 16}' text-anchor='middle' class='vp-t'>{h}/{len(col)}</text>"
    return (f"<figure class='vp-fig vp-large'><div class='vp-defile'><svg viewBox='0 0 {W} {H}' class='vp-saison' role='img' "
            f"aria-label='Saisonnalité de {_e(nom)} : hausse ou baisse de chaque mois depuis {A[0]}'>{tete}{cases}{pied}</svg></div>"
            f"<figcaption><b>Saisonnalité.</b> Hausse (vert) ou baisse (rouge) de {_e(nom)} chaque mois, en %. En bas : nombre d'années où ce mois a monté. "
            "Le passé ne se répète pas forcément : un mois souvent vert peut très bien être rouge cette année.</figcaption></figure>")


CSS_FIXE = """<style>
.vp-duo{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;align-items:start;margin:14px 0}
.vp-fig{margin:0;border:1px solid rgba(127,127,127,.28);border-radius:12px;padding:12px 14px}
.vp-fig figcaption{font-size:13.5px;color:var(--muted,#9aa6bd);margin-top:6px;line-height:1.45}
.vp-radar{width:100%;max-width:440px;display:block;margin:0 auto}
.vp-g{fill:none;stroke:rgba(127,127,127,.28);stroke-width:1}
.vp-forme{fill:rgba(90,169,255,.28);stroke:#5aa9ff;stroke-width:2;stroke-linejoin:round}
.vp-t{font:12px system-ui,sans-serif;fill:currentColor;opacity:.8}.vp-n{font-weight:700;opacity:1}
.vp-c{font:600 11px system-ui,sans-serif;fill:currentColor}
.vp-vide{fill:rgba(127,127,127,.07)}
.vp-defile{overflow-x:auto}.vp-saison{display:block;width:100%;min-width:520px;height:auto}.vp-large{grid-column:1/-1}
@media (prefers-reduced-motion:no-preference){.vp-forme{transform-origin:210px 124px;animation:vp-pousse .8s cubic-bezier(.2,.8,.2,1) both}
@keyframes vp-pousse{from{transform:scale(.2);opacity:0}to{transform:none;opacity:1}}}
</style>"""


def bloc_fiche(pr, s, nom) -> str:
    a, b = svg_profil(pr, nom), svg_saison(s, nom)
    if not a and not b:
        return ""
    return CSS_FIXE + "<h2>En images</h2><div class='vp-duo'>" + a + b + "</div>"


# ----------------------------------------------------------------------------------------------------------------
# Appli (HTML, CSS, JS)
# ----------------------------------------------------------------------------------------------------------------
HTML = """
  <section aria-labelledby="h-vp" id="bulles">
    <div class="sec-head"><h2 id="h-vp">Le marché en bulles</h2>
      <div class="per" role="group" aria-label="Quels titres"><button data-vpq="crypto" aria-pressed="true">Cryptos</button><button data-vpq="actions" aria-pressed="false">Actions</button><button data-vpq="tout" aria-pressed="false">Tout</button></div>
      <div class="per" role="group" aria-label="Période des bulles"><button data-vpp="1 jour" aria-pressed="true">Jour</button><button data-vpp="1 semaine" aria-pressed="false">Semaine</button><button data-vpp="1 mois" aria-pressed="false">Mois</button></div></div>
    <div class="vp-zone" id="vp-zone"><canvas id="vp-canvas" aria-hidden="true"></canvas>
      <div class="vp-info" id="vp-info" hidden></div></div>
    <p class="muted vp-leg" id="vp-leg">Chaque bulle est un titre : plus elle est grosse, plus son prix a bougé ; verte s'il a monté, rouge s'il a baissé. Attrape-les, elles s'écartent. Clique sur une bulle pour ouvrir sa fiche.</p>
    <ul class="sr" id="vp-liste" aria-label="Plus fortes variations"></ul>
  </section>
  <section aria-labelledby="h-jauges" id="jauges">
    <div class="sec-head"><h2 id="h-jauges">Le marché en jauges</h2><p>Calculées chaque heure à partir des titres suivis. Ce sont des photos du marché, pas des prévisions.</p></div>
    <div class="vp-jauges" id="vp-jauges"></div>
  </section>
"""

CSS = r"""
.vp-zone{position:relative;height:min(560px,72vh);border:1px solid var(--line);border-radius:14px;overflow:hidden;
  background:radial-gradient(120% 90% at 50% 40%,rgba(90,169,255,.08),transparent 70%),var(--surface);touch-action:none}
.vp-zone canvas{position:absolute;inset:0;width:100%;height:100%;cursor:grab}.vp-zone canvas:active{cursor:grabbing}
.vp-info{position:absolute;pointer-events:none;background:var(--ink);color:var(--surface);padding:7px 10px;border-radius:9px;font-size:13px;line-height:1.35;
  box-shadow:0 6px 18px rgba(0,0,0,.25);white-space:nowrap;z-index:2}
.vp-leg{font-size:12.5px;margin:8px 0 0}
.vp-jauges{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.vp-j{border:1px solid var(--line);border-radius:14px;padding:14px 16px 12px;background:var(--surface)}
.vp-j h3{margin:0 0 2px;font-size:15px}.vp-j .vp-s{font-size:12.5px;color:var(--muted);margin:0}
.vp-j svg{display:block;width:100%;max-width:260px;margin:6px auto 0}
.vp-arc{fill:none;stroke-width:16;stroke-linecap:round}
.vp-aig{transform-origin:130px 112px;transition:transform 1.1s cubic-bezier(.2,.8,.2,1)}
.vp-val{font:700 30px var(--font,system-ui);fill:var(--ink)}.vp-lib{font:600 13px system-ui;fill:var(--muted)}
.vp-j details{margin-top:6px;font-size:13px}.vp-j summary{cursor:pointer;color:var(--muted)}
.vp-j ul{margin:6px 0 0;padding-left:18px}.vp-j li{margin:2px 0}
.vp-carte{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:0 0 12px}
.vp-carte .panel{margin:0}
.vp-radar{width:100%;max-width:380px;display:block;margin:0 auto}
.vp-g{fill:none;stroke:var(--line);stroke-width:1}
.vp-forme{fill:color-mix(in srgb,var(--accent) 28%,transparent);stroke:var(--accent);stroke-width:2;stroke-linejoin:round}
.vp-t{font:12px system-ui,sans-serif;fill:var(--muted)}.vp-n{font-weight:700;fill:var(--ink)}
.vp-c{font:600 11px system-ui,sans-serif;fill:var(--ink)}.vp-vide{fill:color-mix(in srgb,var(--line) 40%,transparent)}
.vp-defile{overflow-x:auto}.vp-saison{display:block;width:100%;max-width:720px;min-width:520px;height:auto}
.vp-carte svg{max-width:300px;margin:0 auto;display:block}.vp-carte .vp-radar{max-width:420px}
.vp-note{font-size:12.5px;color:var(--muted);margin:6px 0 0;line-height:1.45}
@media (prefers-reduced-motion:no-preference){.vp-forme{transform-box:fill-box;transform-origin:center;animation:vp-pousse .8s cubic-bezier(.2,.8,.2,1) both}
 @keyframes vp-pousse{from{transform:scale(.2);opacity:0}to{transform:none;opacity:1}}}
@media (max-width:640px){.vp-zone{height:62vh}}

.radar-une{position:relative;margin:4px 0 6px}
.radar-une svg{display:block;width:100%;max-width:440px;margin:0 auto;overflow:visible}
.ru-anneau{fill:none;stroke:var(--line);stroke-width:1}.ru-axe{stroke:var(--line);stroke-width:1;stroke-dasharray:2 4}
.ru-zone{font:600 10.5px var(--f-body,system-ui);fill:var(--muted);letter-spacing:.02em}
.ru-balai{transform-origin:200px 200px}
.ru-blip{cursor:pointer}.ru-blip:hover circle.c,.ru-blip:focus circle.c{stroke:var(--ink);stroke-width:2}.ru-blip:focus{outline:none}
.ru-blip:focus-visible circle.c{stroke:var(--ink);stroke-width:2.5}
.ru-lab{font:700 11px var(--f-body,system-ui);fill:var(--ink);pointer-events:none;paint-order:stroke;stroke:var(--surface);stroke-width:3px}
.ru-halo{opacity:0}
.ru-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:6px}
.ru-stats a,.ru-stats div{border:1px solid var(--line);border-radius:12px;padding:9px 10px;text-decoration:none;color:var(--ink);background:var(--bg)}
.ru-stats small{display:block;font-size:11.5px;color:var(--muted)}.ru-stats b{font-size:18px;font-variant-numeric:tabular-nums}
.bref .ru-leg{font:12.5px/1.45 var(--f-body,system-ui);color:var(--muted);margin:6px 0 0;text-align:center}
.ru-info{position:absolute;pointer-events:none;background:var(--ink);color:var(--surface);font-size:12.5px;padding:6px 9px;border-radius:8px;white-space:nowrap;z-index:3}
@media (prefers-reduced-motion:no-preference){
 .ru-balai{animation:ru-tour 7s linear infinite}@keyframes ru-tour{to{transform:rotate(360deg)}}
 .ru-halo{animation:ru-halo 7s linear infinite;animation-delay:var(--d);transform-box:fill-box;transform-origin:center}
 @keyframes ru-halo{0%{opacity:.55;transform:scale(1)}10%{opacity:0;transform:scale(2.2)}100%{opacity:0}}}
@media (max-width:640px){.ru-stats b{font-size:16px}}
"""

JS = r"""
/* ---------- Version 94 : bulles, jauges, profil, jauge technique, saisonnalité ---------- */
(function(){
  if(typeof DATA === "undefined" || !DATA || !DATA.titres) return;
  const TT = DATA.titres.filter(t => t.marche !== "tendances" && t.perf);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const pc = (v, d = 1) => v == null ? "–" : (v >= 0 ? "+" : "−") + Math.abs(v * 100).toFixed(d).replace(".", ",") + " %";
  const rgba = (c, a, def) => { const m = /^#([0-9a-f]{6})$/i.exec(c || ""); const h = m ? m[1] : def;
    return `rgba(${parseInt(h.slice(0, 2), 16)},${parseInt(h.slice(2, 4), 16)},${parseInt(h.slice(4, 6), 16)},${a})`; };
  const court = tk => tk.endsWith("-USD") ? tk.replace(/(\d{4,})?-USD$/, "") : (window.affTk ? affTk(tk) : tk);
  /* ===== Bulles ===== */
  const zone = document.getElementById("vp-zone"), cv = document.getElementById("vp-canvas");
  if(zone && cv){
    const ctx = cv.getContext("2d"), info = document.getElementById("vp-info");
    let Q = "crypto", P = "1 jour", B = [], W = 0, H = 0, dpr = 1, drag = null, survol = null, actif = false, raf = 0, img = {};
    const reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const choisir = () => TT.filter(t => Q === "tout" ? true : Q === "crypto" ? t.marche === "crypto" : t.marche !== "crypto")
                            .filter(t => t.perf[P] != null && isFinite(t.perf[P]));
    function taille(){ const r = zone.getBoundingClientRect(); dpr = Math.min(2, devicePixelRatio || 1); W = r.width; H = r.height;
      cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    function construire(){
      const L = choisir(); if(!L.length){ B = []; return; }
      const a = L.map(t => Math.abs(t.perf[P])), mx = Math.max(...a, 1e-4);
      const surface = W * H * 0.5, somme = a.reduce((s, v) => s + (0.15 + v / mx), 0);
      const k = Math.sqrt(surface / Math.PI / somme);
      const anc = Object.fromEntries(B.map(b => [b.t.ticker, b]));
      B = L.map((t, i) => { const v = t.perf[P], r = Math.max(10, Math.min(Math.min(W, H) / 4.2, k * Math.sqrt(0.15 + Math.abs(v) / mx)));
        const o = anc[t.ticker]; return {t, v, r, x: o ? o.x : W / 2 + (Math.random() - .5) * W * .8, y: o ? o.y : H / 2 + (Math.random() - .5) * H * .8, vx: 0, vy: 0}; });
      liste(L);
    }
    function liste(L){ const z = document.getElementById("vp-liste"); if(!z) return;
      z.innerHTML = [...L].sort((a, b) => Math.abs(b.perf[P]) - Math.abs(a.perf[P])).slice(0, 15).map(t => `<li>${esc(t.nom)} : ${pc(t.perf[P])}</li>`).join(""); }
    function pas(){
      for(const b of B){ b.vx += (W / 2 - b.x) * 0.0009; b.vy += (H / 2 - b.y) * 0.0012; }
      for(let i = 0; i < B.length; i++) for(let j = i + 1; j < B.length; j++){
        const a = B[i], b = B[j], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy) || .01, m = a.r + b.r + 1.5;
        if(d < m){ const f = (m - d) / d * 0.5, fx = dx * f, fy = dy * f, wa = b.r / (a.r + b.r), wb = 1 - wa;
          a.x -= fx * wa; a.y -= fy * wa; b.x += fx * wb; b.y += fy * wb; a.vx -= fx * .05; b.vx += fx * .05; a.vy -= fy * .05; b.vy += fy * .05; } }
      for(const b of B){ if(b === drag) continue; b.vx *= .86; b.vy *= .86; b.x += b.vx; b.y += b.vy;
        b.x = Math.max(b.r, Math.min(W - b.r, b.x)); b.y = Math.max(b.r, Math.min(H - b.r, b.y)); }
    }
    function dessiner(){
      ctx.clearRect(0, 0, W, H);
      const up = css("--up"), dn = css("--down"), ink = css("--ink") || "#fff";
      const mx = Math.max(...B.map(b => Math.abs(b.v)), 1e-4);
      for(const b of B){
        const f = Math.min(1, Math.abs(b.v) / mx), c = b.v >= 0 ? up : dn, def = b.v >= 0 ? "44e09c" : "ff6b6b";
        const g = ctx.createRadialGradient(b.x - b.r * .3, b.y - b.r * .35, b.r * .1, b.x, b.y, b.r);
        g.addColorStop(0, rgba(c, (.12 + .25 * f).toFixed(2), def));
        g.addColorStop(1, rgba(c, (.35 + .5 * f).toFixed(2), def));
        ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = b === survol ? 3 : 1.5; ctx.strokeStyle = rgba(c, .95, def); ctx.stroke();
        if(b.r >= 16){ ctx.fillStyle = ink; ctx.textAlign = "center"; ctx.textBaseline = "middle";
          const fs = Math.max(10, Math.min(22, b.r / 2.6));
          ctx.font = `700 ${fs}px system-ui,sans-serif`; ctx.fillText(court(b.t.ticker).slice(0, 7), b.x, b.y - (b.r > 26 ? fs * .45 : 0));
          if(b.r > 26){ ctx.font = `600 ${Math.max(9, fs * .72)}px system-ui,sans-serif`; ctx.fillText(pc(b.v), b.x, b.y + fs * .7); } }
      }
    }
    let tours = 0;
    function boucle(){ pas(); dessiner(); tours++; if(actif && (tours < 400 || drag)) raf = requestAnimationFrame(boucle); else raf = 0; }
    function lancer(){ tours = 0; if(!raf) raf = requestAnimationFrame(boucle); }
    function tout(){ taille(); construire(); if(reduit){ for(let i = 0; i < 300; i++) pas(); dessiner(); } else lancer(); }
    const pos = e => { const r = cv.getBoundingClientRect(); return {x: e.clientX - r.left, y: e.clientY - r.top}; };
    const sous = p => { for(let i = B.length - 1; i >= 0; i--){ const b = B[i]; if(Math.hypot(p.x - b.x, p.y - b.y) <= b.r) return b; } return null; };
    let depart = null;
    cv.addEventListener("pointerdown", e => { const p = pos(e), b = sous(p); depart = {p, t: Date.now(), b}; if(b){ drag = b; cv.setPointerCapture(e.pointerId); lancer(); } });
    cv.addEventListener("pointermove", e => { const p = pos(e);
      if(drag){ drag.vx = p.x - drag.x; drag.vy = p.y - drag.y; drag.x = p.x; drag.y = p.y; }
      const b = sous(p); if(b !== survol){ survol = b; if(!raf) dessiner(); }
      if(b){ const t = b.t; info.hidden = false;
        info.innerHTML = `<b>${esc(t.nom)}</b> · ${pc(b.v)} (${P})<br>Avis de l'IA sur un mois : ${t.proba_hausse == null ? "–" : (t.proba_hausse >= .5 ? "↑ hausse " : "↓ baisse ") + Math.round(Math.max(t.proba_hausse, 1 - t.proba_hausse) * 100) + " chances sur 100"}`;
        const r = zone.getBoundingClientRect(), w = info.offsetWidth; info.style.left = Math.max(6, Math.min(r.width - w - 6, p.x - w / 2)) + "px"; info.style.top = Math.max(6, p.y - b.r - 58) + "px";
      } else info.hidden = true; });
    cv.addEventListener("pointerup", e => { const p = pos(e);
      if(depart && depart.b && Date.now() - depart.t < 350 && Math.hypot(p.x - depart.p.x, p.y - depart.p.y) < 6 && window.ouvrir) ouvrir(depart.b.t.ticker);
      drag = null; depart = null; lancer(); });
    cv.addEventListener("pointerleave", () => { survol = null; info.hidden = true; if(!raf) dessiner(); });
    document.querySelectorAll("[data-vpq]").forEach(b => b.onclick = () => { Q = b.dataset.vpq;
      document.querySelectorAll("[data-vpq]").forEach(x => x.setAttribute("aria-pressed", x === b)); construire(); lancer(); });
    document.querySelectorAll("[data-vpp]").forEach(b => b.onclick = () => { P = b.dataset.vpp;
      document.querySelectorAll("[data-vpp]").forEach(x => x.setAttribute("aria-pressed", x === b)); construire(); lancer(); });
    new IntersectionObserver(es => { actif = es[0].isIntersecting; if(actif){ if(!B.length) tout(); else lancer(); } }, {threshold: .05}).observe(zone);
    let to; addEventListener("resize", () => { clearTimeout(to); to = setTimeout(() => { if(B.length){ taille(); construire(); lancer(); } }, 200); });
  }
  /* ===== Jauges ===== */
  const ARC = (v, coul, val, lib) => {   // demi-cercle de 0 à 100 ; la valeur s'écrit sous l'aiguille
    return `<svg viewBox="0 0 260 182" role="img" aria-label="${esc(lib)} : ${val}">
      <defs><linearGradient id="vpg${coul}" x1="0" x2="1"><stop offset="0" stop-color="var(--down)"/><stop offset=".5" stop-color="var(--warn)"/><stop offset="1" stop-color="var(--up)"/></linearGradient></defs>
      <path d="M35 112 A95 95 0 0 1 225 112" class="vp-arc" stroke="var(--line)"/>
      <path d="M35 112 A95 95 0 0 1 225 112" class="vp-arc" stroke="url(#vpg${coul})" opacity=".85"/>
      <g class="vp-aig" style="transform:rotate(${-90 + 1.8 * v}deg)"><line x1="130" y1="112" x2="130" y2="36" stroke="var(--ink)" stroke-width="4" stroke-linecap="round"/><circle cx="130" cy="112" r="8" fill="var(--ink)"/></g>
      <text x="130" y="152" text-anchor="middle" class="vp-val">${val}</text><text x="130" y="174" text-anchor="middle" class="vp-lib">${esc(lib)}</text></svg>`;
  };
  const jz = document.getElementById("vp-jauges");
  if(jz){
    const cartes = [];
    const part = (L, f) => L.length ? Math.round(L.filter(f).length / L.length * 100) : null;
    // 1. Thermomètre du marché (calcul maison)
    const A = TT.filter(t => t.marche !== "crypto");
    const ing = [];
    const p1 = part(TT.filter(t => t.perf["1 mois"] != null), t => t.perf["1 mois"] > 0); if(p1 != null) ing.push(["Élan", p1, `${p1} % des titres ont monté sur un mois`]);
    const p2 = part(TT.filter(t => t.au_dessus_200 != null), t => t.au_dessus_200); if(p2 != null) ing.push(["Largeur", p2, `${p2} % sont au-dessus de leur moyenne 200 jours`]);
    const p3 = part(TT.filter(t => t.proba_hausse != null), t => t.proba_hausse >= .5); if(p3 != null) ing.push(["Avis de l'IA", p3, `l'IA voit ${p3} % des titres en hausse sur un mois`]);
    const ctxv = (DATA.contexte || []).find(c => c.cle === "vix");
    if(ctxv && ctxv.valeur){ const s = Math.round(Math.max(0, Math.min(100, (35 - ctxv.valeur) / (35 - 12) * 100))); ing.push(["Calme (VIX)", s, `peur des marchés américains : ${ctxv.valeur.toFixed(1).replace(".", ",")} points`]); }
    const fg = (DATA.contexte || []).find(c => c.cle === "fng");
    if(fg && fg.valeur != null){ const s = Math.round(fg.valeur); ing.push(["Sentiment crypto", s, `indice Fear & Greed crypto (alternative.me) : ${s}`]); }
    if(ing.length >= 3){
      const v = Math.round(ing.reduce((s, x) => s + x[1], 0) / ing.length);
      const lib = v < 25 ? "Peur forte" : v < 45 ? "Peur" : v <= 55 ? "Neutre" : v <= 75 ? "Confiance" : "Euphorie";
      cartes.push(`<div class="vp-j"><h3>Thermomètre du marché</h3><p class="vp-s">De la peur à l'euphorie, calcul maison</p>${ARC(v, "t", v, lib)}
        <details><summary>Ses ${ing.length} ingrédients</summary><ul>${ing.map(x => `<li><b>${esc(x[0])} : ${x[1]}</b> — ${esc(x[2])}</li>`).join("")}</ul>
        <p class="vp-note">Moyenne des ingrédients, chacun de 0 (peur) à 100 (euphorie). Une euphorie générale n'annonce pas une hausse : elle précède parfois une baisse.</p></details></div>`);
    }
    // 2. Saison des altcoins
    const btc = TT.find(t => t.ticker === "BTC-USD");
    const alts = TT.filter(t => t.marche === "crypto" && t.ticker !== "BTC-USD" && !/^(PAXG|XAUT|USDT|USDC)/.test(t.ticker) && t.perf["3 mois"] != null);
    if(btc && btc.perf["3 mois"] != null && alts.length >= 20){
      const v = part(alts, t => t.perf["3 mois"] > btc.perf["3 mois"]);
      const lib = v >= 75 ? "Saison des altcoins" : v <= 25 ? "Saison du bitcoin" : "Entre les deux";
      cartes.push(`<div class="vp-j"><h3>Saison des altcoins</h3><p class="vp-s">Les autres cryptos font-elles mieux que le bitcoin ?</p>${ARC(v, "a", v, lib)}
        <details><summary>Comment c'est calculé</summary><p class="vp-note">${v} % des ${alts.length} cryptos suivies (hors bitcoin et or numérique) ont fait mieux que le bitcoin sur 3 mois (bitcoin : ${pc(btc.perf["3 mois"], 0)}). Au-dessus de 75 : « saison des altcoins » ; sous 25 : « saison du bitcoin ».</p></details></div>`);
    }
    // 3. Agitation prévue (médiane)
    const mv = TT.map(t => t.risque_prevu && t.risque_prevu.mouvement).filter(v => v > 0).sort((a, b) => a - b);
    const hab = TT.map(t => t.risque_prevu && t.risque_prevu.habitude).filter(v => v > 0).sort((a, b) => a - b);
    if(mv.length >= 20 && hab.length >= 20){
      const h = hab[hab.length >> 1];
      const v = Math.round(Math.max(0, Math.min(100, 50 + (1 - h) * 150)));   // à droite (vert) : plus calme que d'habitude
      cartes.push(`<div class="vp-j"><h3>Agitation prévue</h3><p class="vp-s">Le mois prochain, plus calme ou plus agité que d'habitude ?</p>${ARC(v, "g", "±" + Math.round(mv[mv.length >> 1] * 100) + " %", h > 1.08 ? "Plus agité que d'habitude" : h < .92 ? "Plus calme que d'habitude" : "Comme d'habitude")}
        <details><summary>Comment c'est calculé</summary><p class="vp-note">Pour un titre typique, l'IA prévoit un mouvement de ±${Math.round(mv[mv.length >> 1] * 100)} % sur un mois, soit ${Math.round(h * 100)} % de son agitation habituelle. C'est la prévision la plus fiable du radar.</p></details></div>`);
    }
    jz.innerHTML = cartes.join("") || `<p class="muted">Pas assez de données aujourd'hui.</p>`;
  }

  /* ===== Version 96 : le radar du jour (haut de l'accueil) ===== */
  const ru = document.getElementById("radar-une"), EN = document.documentElement.lang === "en";
  if(ru){
    const ZONES = [["fr", "France"], ["eu", "Europe"], ["us", "États-Unis"], ["monde", "Monde"], ["etf", "ETF"], ["crypto", "Crypto"]];
    const zi = Object.fromEntries(ZONES.map((z, k) => [z[0], k]));
    const L = TT.filter(t => t.proba_hausse != null && zi[t.marche] != null);
    // les avis les plus nets de chaque marché (5 au plus par marché), pour couvrir tout le radar
    const fort = ZONES.flatMap(([z]) => L.filter(t => t.marche === z).sort((a, b) => Math.abs(b.proba_hausse - .5) - Math.abs(a.proba_hausse - .5)).slice(0, 5));
    if(fort.length >= 6){
      const C = 200, R = 168, mx = Math.max(...fort.map(t => Math.abs(t.proba_hausse - .5)), .01);
      const parZone = {}; fort.forEach(t => (parZone[t.marche] ||= []).push(t));
      let blips = "", labels = "";
      fort.forEach((t, k) => {
        const z = zi[t.marche], grp = parZone[t.marche], j = grp.indexOf(t), n = grp.length;
        const a0 = (z / ZONES.length) * 2 * Math.PI - Math.PI / 2, pas = 2 * Math.PI / ZONES.length;
        const ordre = [2, 0, 4, 1, 3, 5, 6], pos = n <= 5 ? ordre.filter(x => x < n).indexOf(j) : j;   // évite l'effet « spirale »
        const a = a0 + pas * (0.12 + 0.76 * (pos + .5) / n);
        const f = 1 - j / Math.max(1, n - 1);   // dans chaque marché, l'avis le plus net est le plus près du centre
        const r = R * (0.86 - 0.6 * f);
        const x = C + r * Math.cos(a), y = C + r * Math.sin(a), up = t.proba_hausse >= .5, col = up ? "var(--up)" : "var(--down)";
        const ang = ((a + Math.PI / 2) / (2 * Math.PI) + 1) % 1, d = (ang * 7).toFixed(2) + "s";
        const rr = 4.5 + 4 * f, ch = Math.round(Math.max(t.proba_hausse, 1 - t.proba_hausse) * 100);
        blips += `<g class="ru-blip" tabindex="0" role="button" data-t="${esc(t.ticker)}" style="--d:${d};transform-origin:${x.toFixed(1)}px ${y.toFixed(1)}px" aria-label="${esc(t.nom)} : ${up ? "hausse" : "baisse"}, ${ch} chances sur 100">
          <circle class="ru-halo" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rr.toFixed(1)}" fill="${col}"/><circle class="c" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rr.toFixed(1)}" fill="${col}" fill-opacity=".9"/></g>`;
        if(j === 0) labels += `<text class="ru-lab" x="${(x + rr + 4).toFixed(1)}" y="${(y + 4).toFixed(1)}">${esc(court(t.ticker))}</text>`;
      });
      let fond = [1, .66, .33].map(k => `<circle class="ru-anneau" cx="${C}" cy="${C}" r="${(R * k).toFixed(1)}"/>`).join("");
      fond += ZONES.map((z, k) => { const a = (k / ZONES.length) * 2 * Math.PI - Math.PI / 2, a2 = a + Math.PI / ZONES.length;
        const lx = C + (R + 16) * Math.cos(a2), ly = C + (R + 16) * Math.sin(a2), anc = Math.abs(Math.cos(a2)) < .2 ? "middle" : Math.cos(a2) > 0 ? "start" : "end";
        return `<line class="ru-axe" x1="${C}" y1="${C}" x2="${(C + R * Math.cos(a)).toFixed(1)}" y2="${(C + R * Math.sin(a)).toFixed(1)}"/>`
          + `<text class="ru-zone" x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="${anc}">${z[1]}</text>`; }).join("");
      const balai = `<defs><linearGradient id="ru-g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--accent)" stop-opacity="0"/><stop offset="1" stop-color="var(--accent)" stop-opacity=".38"/></linearGradient></defs>
        <g class="ru-balai"><path d="M${C} ${C} L${C + R} ${C} A${R} ${R} 0 0 0 ${(C + R * Math.cos(-0.7)).toFixed(1)} ${(C + R * Math.sin(-0.7)).toFixed(1)} Z" fill="url(#ru-g)"/>
        <line x1="${C}" y1="${C}" x2="${C + R}" y2="${C}" stroke="var(--accent)" stroke-width="1.5" stroke-opacity=".8"/></g>`;
      const nbH = L.filter(t => t.proba_hausse >= .5).length, pcH = L.length ? Math.round(nbH / L.length * 100) : null;
      const btc = TT.find(t => t.ticker === "BTC-USD"), cac = (DATA.indices || []).find(i => i.ticker === "^FCHI") || TT.find(t => t.ticker === "^FCHI");
      const v1 = cac && (cac.var_jour ?? (cac.perf && cac.perf["1 jour"]));
      ru.innerHTML = `<svg viewBox="-60 -10 520 420" role="group" aria-label="Le radar du jour : les avis les plus nets de l'IA, rangés par marché">${fond}${balai}
        <circle cx="${C}" cy="${C}" r="3.5" fill="var(--accent)"/>${blips}${labels}</svg>
        <p class="ru-leg">${EN ? `The AI's clearest views in each market: <b class="up">●</b> up, <b class="down">●</b> down. In each market, the clearest is closest to the centre. Click to open.`
          : `Les avis les plus nets de l'IA dans chaque marché : <b class="up">●</b> hausse, <b class="down">●</b> baisse. Dans chaque marché, le plus net est le plus près du centre. Clique pour ouvrir.`}</p>
        <div class="ru-stats">${pcH != null ? `<a href="prediction-bourse.html"><small>Vus en hausse</small><b>${pcH} %</b></a>` : ""}
          ${btc ? `<a href="titres/btc-usd.html"><small>Bitcoin, 24 h</small><b class="${(btc.perf["1 jour"] || 0) >= 0 ? "up" : "down"}">${pc(btc.perf["1 jour"])}</b></a>` : ""}
          ${v1 != null ? `<a href="titres/fchi.html"><small>CAC 40, jour</small><b class="${v1 >= 0 ? "up" : "down"}">${pc(v1)}</b></a>` : `<a href="#jauges"><small>Thermomètre</small><b>voir</b></a>`}</div>
        <div class="ru-info" id="ru-info" hidden></div>`;
      const info = document.getElementById("ru-info");
      ru.querySelectorAll(".ru-blip").forEach(g => {
        const t = TT.find(x => x.ticker === g.dataset.t);
        const montrer = () => { const b = g.getBoundingClientRect(), z = ru.getBoundingClientRect();
          info.hidden = false; info.innerHTML = `<b>${esc(t.nom)}</b> · ${t.proba_hausse >= .5 ? "↑ hausse" : "↓ baisse"} ${Math.round(Math.max(t.proba_hausse, 1 - t.proba_hausse) * 100)} chances sur 100`;
          info.style.left = Math.max(0, Math.min(z.width - info.offsetWidth, b.left - z.left + b.width / 2 - info.offsetWidth / 2)) + "px"; info.style.top = (b.top - z.top - 34) + "px"; };
        g.addEventListener("mouseenter", montrer); g.addEventListener("focus", montrer);
        g.addEventListener("mouseleave", () => info.hidden = true); g.addEventListener("blur", () => info.hidden = true);
        const go = () => { if(window.ouvrir) ouvrir(t.ticker); };
        g.addEventListener("click", go); g.addEventListener("keydown", e => { if(e.key === "Enter" || e.key === " "){ e.preventDefault(); go(); } });
      });
    }
  }
  /* ===== Fiche : profil, jauge technique, saisonnalité ===== */
  const groupe = t => t.marche === "crypto" ? TT.filter(x => x.marche === "crypto") : TT.filter(x => x.marche !== "crypto");
  const rang = (L, f, x) => { const v = L.map(f).filter(y => y != null && isFinite(y)).sort((a, b) => a - b); if(x == null || !isFinite(x) || v.length < 10) return null;
    let k = 0; while(k < v.length && v[k] <= x) k++; return Math.round(k / v.length * 100); };
  const AXES = [["calme", "Calme", t => -((t.risque_prevu || {}).mouvement ?? NaN)], ["solidite", "Solidité", t => -((t.risque_prevu || {}).chute ?? NaN)],
                ["tendance", "Tendance 6 mois", t => t.perf["6 mois"]], ["elan", "Élan 1 mois", t => t.perf["1 mois"]], ["ia", "Avis de l'IA", t => t.proba_hausse],
                ["dividende", "Dividende", t => t.marche === "crypto" ? null : t.div]];
  window.vpProfil = function(t){
    if(!t || !t.perf) return "";
    const L = groupe(t), notes = AXES.map(([k, n, f]) => [n, rang(L, f, f(t))]).filter(x => x[1] != null);
    if(notes.length < 4) return "";
    const n = notes.length, R = 84, cx = 210, cy = 124, pt = (i, r) => [cx + r * Math.sin(2 * Math.PI * i / n), cy - r * Math.cos(2 * Math.PI * i / n)];
    const poly = (r) => Array.from({length: n}, (_, i) => pt(i, r).map(v => v.toFixed(1)).join(",")).join(" ");
    const forme = notes.map((x, i) => pt(i, R * Math.max(4, x[1]) / 100).map(v => v.toFixed(1)).join(",")).join(" ");
    const etq = notes.map((x, i) => { const [X, Y] = pt(i, R + 18), a = Math.abs(X - cx) < 8 ? "middle" : X > cx ? "start" : "end";
      return `<text x="${X.toFixed(1)}" y="${(Y + 4).toFixed(1)}" text-anchor="${a}" class="vp-t">${esc(x[0])} <tspan class="vp-n">${x[1]}</tspan></text>`; }).join("");
    const moy = Math.round(notes.reduce((s, x) => s + x[1], 0) / n);
    return `<div class="panel"><div class="label">Profil du titre</div><svg viewBox="0 0 420 252" class="vp-radar" role="img" aria-label="Profil : ${notes.map(x => x[0] + " " + x[1] + " sur 100").join(", ")}">
      ${[1, 2, 3, 4].map(k => `<polygon points="${poly(R * k / 4)}" class="vp-g"/>`).join("")}${notes.map((x, i) => { const [X, Y] = pt(i, R); return `<line x1="${cx}" y1="${cy}" x2="${X.toFixed(1)}" y2="${Y.toFixed(1)}" class="vp-g"/>`; }).join("")}
      <polygon points="${forme}" class="vp-forme"/>${etq}</svg>
      <p class="vp-note"><b>${moy} / 100 en moyenne.</b> Chaque critère compare ce titre aux autres ${t.marche === "crypto" ? "cryptos" : "actions"} suivies (100 = le mieux placé aujourd'hui). Une photo, pas une recommandation.</p></div>`;
  };
  window.vpJaugeTech = function(t){
    if(!t || t.score == null) return "";
    const v = Math.max(0, Math.min(100, t.score)), lib = v >= 65 ? "Plutôt haussier" : v >= 55 ? "Légèrement haussier" : v > 45 ? "Neutre" : v > 35 ? "Légèrement baissier" : "Plutôt baissier";
    const pour = (t.raisons_pour || []).length, contre = (t.raisons_contre || []).length;
    return `<div class="panel"><div class="label">Résumé technique</div>${ARC(v, "s" + Math.round(v), Math.round(v), lib)}
      <p class="vp-note">L'aiguille suit le score technique du radar (moyennes mobiles, RSI, MACD, volumes…) : ${pour} signe${pour > 1 ? "s" : ""} favorable${pour > 1 ? "s" : ""}, ${contre} défavorable${contre > 1 ? "s" : ""}. C'est l'état des graphiques aujourd'hui, pas l'avis de l'IA sur le mois qui vient.</p></div>`;
  };
  const MC = ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"];
  window.vpSaison = function(t){
    const s = t && t.saison; if(!s || !s.annees || !s.annees.length) return "";
    const A = s.annees, M = s.m, vals = M.flat().filter(v => v != null).map(Math.abs).sort((a, b) => a - b);
    if(vals.length < 6) return "";
    const lim = Math.max(.02, vals[Math.floor(vals.length * .9)]), cw = 40, ch = 22, gx = 48, gy = 22, W = gx + 12 * cw + 4, H = gy + A.length * ch + 26;
    let c = MC.map((m, i) => `<text x="${gx + i * cw + cw / 2}" y="14" text-anchor="middle" class="vp-t">${m}</text>`).join("");
    A.forEach((an, j) => { c += `<text x="${gx - 6}" y="${gy + j * ch + 15}" text-anchor="end" class="vp-t">${an}</text>`;
      for(let i = 0; i < 12; i++){ const v = M[j][i], x = gx + i * cw, y = gy + j * ch;
        if(v == null){ c += `<rect x="${x + 1}" y="${y + 1}" width="${cw - 2}" height="${ch - 2}" rx="3" class="vp-vide"/>`; continue; }
        const a = Math.min(1, Math.abs(v) / lim);
        c += `<rect x="${x + 1}" y="${y + 1}" width="${cw - 2}" height="${ch - 2}" rx="3" fill="color-mix(in srgb, var(${v >= 0 ? "--up" : "--down"}) ${Math.round(14 + 70 * a)}%, transparent)"><title>${MC[i]} ${an} : ${pc(v)}</title></rect>`
          + `<text x="${x + cw / 2}" y="${y + 15}" text-anchor="middle" class="vp-c">${(v >= 0 ? "+" : "−") + Math.abs(Math.round(v * 100))}</text>`; } });
    for(let i = 0; i < 12; i++){ const col = M.map(l => l[i]).filter(v => v != null); if(col.length >= 3) c += `<text x="${gx + i * cw + cw / 2}" y="${gy + A.length * ch + 16}" text-anchor="middle" class="vp-t">${col.filter(v => v > 0).length}/${col.length}</text>`; }
    return `<div class="panel"><div class="label">Saisonnalité : chaque mois depuis ${A[0]}</div><div class="vp-defile"><svg viewBox="0 0 ${W} ${H}" class="vp-saison" role="img" aria-label="Hausse ou baisse de chaque mois depuis ${A[0]}">${c}</svg></div>
      <p class="vp-note">En %, vert si le mois a monté, rouge s'il a baissé. En bas : nombre d'années où ce mois a monté. Le passé ne se répète pas forcément.</p></div>`;
  };
})();
"""


# ----------------------------------------------------------------------------------------------------------------
# Version 95 : couverture illustrée de chaque leçon (idée vue sur les académies des courtiers, dessin original)
# ----------------------------------------------------------------------------------------------------------------
_TEINTES = [("#1d3b8a", "#3f7cf0"), ("#0f5a4a", "#28b487"), ("#5a2a83", "#9a5cf0"), ("#7a3b12", "#e08a3c"), ("#103f63", "#2aa6d9"), ("#5c1d3a", "#e0527f"), ("#2f3d12", "#8fbf3c")]


def couverture_lecon(cid: str, module: int, pastilles: list) -> str:
    """Une bannière dessinée : dégradé du module, une courbe ou des bougies tirées du nom du chapitre (toujours la même pour une leçon)."""
    import hashlib
    h = int(hashlib.sha1(cid.encode()).hexdigest(), 16)
    a, b = _TEINTES[(module - 1) % len(_TEINTES)]
    rnd = lambda k: ((h >> (k * 7)) % 1000) / 1000
    motif = h % 3
    W, H = 720, 170
    if motif == 0:   # une courbe
        pts, y = [], 110
        for i in range(25):
            y = max(30, min(140, y + (rnd(i) - .47) * 34))
            pts.append(f"{i * 30:.0f},{y:.0f}")
        dessin = (f"<polyline points='{' '.join(pts)}' fill='none' stroke='rgba(255,255,255,.85)' stroke-width='3' stroke-linejoin='round'/>"
                  f"<polygon points='0,{H} {' '.join(pts)} 720,{H}' fill='rgba(255,255,255,.10)'/>")
    elif motif == 1:   # des bougies
        dessin, y = "", 95
        for i in range(22):
            o = y; c = max(30, min(140, y + (rnd(i) - .47) * 30)); y = c
            haut, bas = min(o, c) - 6 - rnd(i + 3) * 10, max(o, c) + 6 + rnd(i + 5) * 10
            coul = "rgba(255,255,255,.9)" if c < o else "rgba(255,255,255,.45)"
            x = 18 + i * 32
            dessin += (f"<line x1='{x}' y1='{haut:.0f}' x2='{x}' y2='{bas:.0f}' stroke='{coul}' stroke-width='2'/>"
                       f"<rect x='{x - 7}' y='{min(o, c):.0f}' width='14' height='{max(3, abs(c - o)):.0f}' rx='2' fill='{coul}'/>")
    else:   # des barres
        dessin = "".join(f"<rect x='{20 + i * 34}' y='{H - 20 - (30 + rnd(i) * 100):.0f}' width='22' height='{30 + rnd(i) * 100:.0f}' rx='4' fill='rgba(255,255,255,{.25 + .5 * rnd(i + 9):.2f})'/>" for i in range(21))
    cercles = "".join(f"<circle cx='{rnd(i + 20) * W:.0f}' cy='{rnd(i + 30) * H:.0f}' r='{20 + rnd(i + 40) * 60:.0f}' fill='rgba(255,255,255,.05)'/>" for i in range(4))
    pills = "".join(f"<span>{_e(p)}</span>" for p in pastilles)
    return (f"<div class='l-couv'><svg viewBox='0 0 {W} {H}' preserveAspectRatio='xMidYMid slice' aria-hidden='true'>"
            f"<defs><linearGradient id='lc{h % 10000}' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{a}'/><stop offset='1' stop-color='{b}'/></linearGradient></defs>"
            f"<rect width='{W}' height='{H}' fill='url(#lc{h % 10000})'/>{cercles}{dessin}</svg><div class='l-pills'>{pills}</div></div>")


CSS_COUV = (".l-couv{position:relative;margin:-4px -4px 16px;border-radius:14px;overflow:hidden;aspect-ratio:720/170;min-height:110px}"
            ".l-couv svg{position:absolute;inset:0;width:100%;height:100%}"
            ".l-pills{position:absolute;left:12px;bottom:10px;display:flex;flex-wrap:wrap;gap:6px}"
            ".l-pills span{background:rgba(10,15,30,.55);color:#fff;font-size:12.5px;font-weight:600;padding:4px 10px;border-radius:999px;backdrop-filter:blur(4px)}"
            "@media (prefers-reduced-motion:no-preference){.l-couv svg polyline,.l-couv svg rect,.l-couv svg line{animation:lc-entre .9s cubic-bezier(.2,.8,.2,1) both}"
            "@keyframes lc-entre{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}}")
