"""Version 83 : « Le Défi du jour » devient un vrai dossier d'analyse.

Chaque jour, le même dossier pour tout le monde : une vraie période de marché (actif masqué, révélé à la fin), un graphique
complet (cours, moyennes 20 et 50 jours, RSI), quatre questions de méthode (tendance, pire baisse, écart à la moyenne,
volatilité sur un mois), puis un pronostic chiffré avec niveau de confiance et une fourchette de prix.
Le pronostic est noté comme chez les prévisionnistes professionnels (score de Brier) et comparé à l'IA du site.
Tout est calculé dans le navigateur à partir de jeu_temps.json ; rien n'est envoyé nulle part.
"""

HTML = """
  <section aria-labelledby="h-defi" id="defi" class="dossier">
    <div class="sec-head"><h2 id="h-defi">Le Défi du jour : le dossier d'analyse</h2>
      <p>Une vraie période de marché, le même dossier pour tout le monde. Analyse le graphique en quatre questions de méthode,
      puis donne ton pronostic à un mois avec ton niveau de confiance et ta fourchette. Ton score est comparé à celui de l'IA.</p></div>
    <div class="ds-carte" id="ds">
      <div class="ds-tete"><div><span class="ds-num" id="ds-num">Dossier du jour</span><b id="ds-titre">Actif masqué · révélé à la fin</b></div>
        <div class="ds-etapes" id="ds-etapes" role="img" aria-label="Avancement du dossier, 6 étapes"></div></div>
      <div class="ds-corps"><div class="ds-gauche">
      <p class="ds-lire"><b>Comment lire ce graphique.</b> C'est le vrai cours d'une action ou d'une crypto pendant environ 4 mois, jusqu'au « jour du dossier » (trait pointillé).
      Le cours est ramené à 100 ce jour-là : 110 veut dire 10 % plus haut, 80 veut dire 20 % plus bas. La zone bleutée à droite cache le mois qui a suivi : c'est ce que tu dois prévoir.
      En bas, le RSI mesure si les dernières hausses ou baisses ont été rapides. Passe la souris ou le doigt sur le graphique pour lire chaque jour.</p>
      <div class="ds-graph" id="ds-graph"><p class="muted">Chargement du dossier…</p></div>
      <div class="ds-leg" id="ds-leg" aria-hidden="true"><span class="l-px">Cours (base 100 = jour du dossier)</span><span class="l-20">Moyenne 20 jours</span><span class="l-50">Moyenne 50 jours</span><span class="l-rsi">RSI 14 jours (en bas)</span></div>
      </div><div class="ds-q" id="ds-q" aria-live="polite"></div></div>
    </div>
  </section>
"""

CSS = """
.dossier .ds-carte{border:1px solid var(--line);border-radius:14px;background:var(--surface);padding:18px;box-shadow:0 1px 0 var(--line)}
.ds-tete{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:10px}
.ds-tete b{display:block;font-size:17px}.ds-num{font-size:12.5px;color:var(--muted)}
.ds-etapes{display:flex;gap:5px}.ds-etapes i{width:26px;height:6px;border-radius:3px;background:var(--line);transition:background .3s}
.ds-etapes i.ok{background:var(--up)}.ds-etapes i.ko{background:var(--down)}.ds-etapes i.on{background:var(--accent)}
.ds-graph{position:relative}.ds-graph svg{width:100%;height:auto;display:block;touch-action:pan-y}
.ds-graph text{font-size:11px;fill:var(--muted);font-family:var(--f-mono)}
.ds-bulle{position:absolute;pointer-events:none;background:var(--ink);color:var(--surface);font-size:12px;padding:4px 8px;border-radius:6px;white-space:nowrap;transform:translate(-50%,-120%)}
.ds-leg{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--muted);margin:6px 0 12px}
.ds-leg span::before{content:"";display:inline-block;width:16px;height:3px;border-radius:2px;margin-right:6px;vertical-align:middle;background:var(--ink)}
.ds-leg .l-20::before{background:var(--accent)}.ds-leg .l-50::before{background:var(--warn)}.ds-leg .l-rsi::before{background:var(--muted)}
.ds-q{border-top:1px solid var(--line);padding-top:14px;scroll-margin-top:120px}
@media (min-width:1100px){.ds-corps{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(300px,1fr);gap:22px;align-items:start}
  .ds-gauche{position:sticky;top:96px}.ds-q{border-top:0;border-left:1px solid var(--line);padding:0 0 0 20px;min-height:380px}
  .ds-opts{grid-template-columns:1fr}}
.ds-opts button[aria-pressed=true]{border-color:var(--accent);background:var(--accent-soft)}
.ds-valider{margin-top:10px}
.ds-lire{font-size:13.5px;color:var(--muted);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:4px 0 10px;max-width:none}
.ds-lire b{color:var(--ink)}.ds-suite{scroll-margin-bottom:110px}.dossier .ds-carte{padding-bottom:22px}
.ds-q h3{font-size:17px;margin:0 0 4px}.ds-q .ds-cons{color:var(--muted);font-size:13.5px;margin:0 0 12px}
.ds-opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.ds-opts button{font:inherit;text-align:left;padding:11px 13px;border:1.5px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);cursor:pointer;transition:border-color .15s,transform .15s}
.ds-opts button:hover{border-color:var(--accent)}.ds-opts button:active{transform:scale(.98)}
.ds-opts button.bon{border-color:var(--up);background:var(--up-soft)}.ds-opts button.faux{border-color:var(--down);background:var(--down-soft)}
.ds-opts button:disabled{cursor:default}
#ds-ok:disabled{opacity:.55;cursor:not-allowed}.ds-sens button{transition:border-color .15s,background .15s}.ds-sens button:hover{border-color:var(--accent)}
.ds-expl{margin-top:12px;padding:12px 14px;border-radius:10px;background:var(--accent-soft);font-size:14px;animation:dsIn .35s ease}
.ds-expl b.m{display:block;font-size:12.5px;margin-bottom:2px}
.ds-reg{display:grid;gap:14px;margin:6px 0 12px}.ds-reg label{font-size:14px;display:flex;justify-content:space-between;gap:10px}
.ds-reg input[type=range]{width:100%;accent-color:var(--accent)}
.ds-sens{display:flex;gap:8px}.ds-sens button{flex:1;font:inherit;font-weight:600;padding:11px;border-radius:10px;border:1.5px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer}
.ds-sens button[aria-pressed=true].h{border-color:var(--up);background:var(--up-soft)}.ds-sens button[aria-pressed=true].b{border-color:var(--down);background:var(--down-soft)}
.ds-bilan{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.ds-bilan div{border:1px solid var(--line);border-radius:10px;padding:10px 12px}.ds-bilan b{display:block;font-size:22px;font-family:var(--f-mono)}
.ds-bilan span{font-size:12.5px;color:var(--muted)}
.ds-score{font-size:34px;font-weight:700;font-family:var(--f-mono)}
.ds-futur{stroke-dasharray:1;stroke-dashoffset:1;animation:dsTrace 1.4s ease forwards}
@keyframes dsTrace{to{stroke-dashoffset:0}}@keyframes dsIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.ds-futur{animation:none;stroke-dashoffset:0}.ds-expl{animation:none}}
"""

JS = r"""
(function(){
  const box = document.getElementById("ds"); if(!box) return;
  const G = box.querySelector("#ds-graph"), Q = box.querySelector("#ds-q"), ET = box.querySelector("#ds-etapes");
  const auj = new Date().toISOString().slice(0, 10), CLE = "radar-dossier";
  let S = {}; try{ S = JSON.parse(localStorage.getItem(CLE) || "{}") || {}; }catch(e){}
  S.jours ||= {};
  const sauver = () => { try{ localStorage.setItem(CLE, JSON.stringify(S)); }catch(e){} };
  const f1 = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(1).replace(".", ",") + " %";
  const f0 = v => (v >= 0 ? "+" : "−") + Math.abs(Math.round(v)) + " %";
  let it = null, M = null, etat = null;

  function graine(txt){ let h = 2166136261; for(const c of txt){ h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return () => { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 1e6) / 1e6; }; }
  const sma = (a, n) => a.map((_, i) => i < n - 1 ? null : a.slice(i - n + 1, i + 1).reduce((x, y) => x + y, 0) / n);
  function rsi(a, n = 14){
    const out = a.map(() => null); let g = 0, p = 0;
    for(let i = 1; i < a.length; i++){
      const d = a[i] - a[i - 1], up = Math.max(d, 0), dn = Math.max(-d, 0);
      if(i <= n){ g += up / n; p += dn / n; if(i === n) out[i] = p === 0 ? 100 : 100 - 100 / (1 + g / p); }
      else { g = (g * (n - 1) + up) / n; p = (p * (n - 1) + dn) / n; out[i] = p === 0 ? 100 : 100 - 100 / (1 + g / p); }
    }
    return out;
  }
  function mesures(item){
    const a = item.a, s = item.s.map(v => v * 100 / item.s[item.a]), passe = s.slice(0, a + 1), x = passe.at(-1);
    const m20 = sma(s, 20), m50 = sma(s, 50), r = rsi(s);
    let pic = passe[0], dd = 0; for(const v of passe){ pic = Math.max(pic, v); dd = Math.min(dd, v / pic - 1); }
    const rets = []; for(let i = Math.max(1, a - 59); i <= a; i++) rets.push(Math.log(passe[i] / passe[i - 1]));
    const moy = rets.reduce((x, y) => x + y, 0) / rets.length;
    const sd = Math.sqrt(rets.reduce((x, y) => x + (y - moy) ** 2, 0) / (rets.length - 1));
    const perf = x / passe[0] - 1, ecart50 = m50[a] ? x / m50[a] - 1 : 0;
    const pente50 = m50[a] && m50[a - 20] ? m50[a] / m50[a - 20] - 1 : 0;
    const tend = pente50 > .02 && ecart50 > 0 ? "h" : pente50 < -.02 && ecart50 < 0 ? "b" : "n";
    return {s, a, x, m20, m50, r, dd, sd, sdm: sd * Math.sqrt(21), perf, ecart50, pente50, tend, rsiJ: r[a]};
  }

  function dessiner(revele){
    const s = M.s, a = M.a, n = revele ? s.length : a + 1, W = 720, H1 = 230, H2 = 64, gap = 18, pl = 8, pr = 50;
    const vis = s.slice(0, revele ? s.length : a + 1).concat(M.m50.slice(0, n).filter(v => v != null));
    let lo = Math.min(...vis), hi = Math.max(...vis); const mg = (hi - lo) * .08; lo -= mg; hi += mg;
    const total = s.length - 1, x = i => pl + i / total * (W - pl - pr), y = v => 10 + (hi - v) / (hi - lo) * (H1 - 20);
    const yr = v => H1 + gap + (100 - v) / 100 * H2;
    const chemin = (arr, i0, i1) => { let d = ""; for(let i = i0; i <= i1; i++){ if(arr[i] == null) continue; d += (d ? "L" : "M") + x(i).toFixed(1) + " " + y(arr[i]).toFixed(1); } return d; };
    const brut = (hi - lo) / 5, p10 = Math.pow(10, Math.floor(Math.log10(brut))), pas = [1, 2, 2.5, 5, 10].map(k => k * p10).find(k => k >= brut) || brut;
    const grille = []; for(let v = Math.ceil(lo / pas) * pas; v <= hi; v += pas) grille.push(v);
    let g = grille.map(v => `<line x1="${pl}" x2="${W - pr}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" stroke="var(--line)"/><text x="${W - pr + 6}" y="${(y(v) + 4).toFixed(1)}">${v.toFixed(0)}</text>`).join("");
    g += [30, 70].map(v => `<line x1="${pl}" x2="${W - pr}" y1="${yr(v)}" y2="${yr(v)}" stroke="var(--line)" stroke-dasharray="3 3"/><text x="${W - pr + 6}" y="${yr(v) + 4}">${v}</text>`).join("");
    g += `<rect x="${pl}" y="${H1 + gap}" width="${W - pl - pr}" height="${H2}" fill="none" stroke="var(--line)"/>`;
    const xa = x(a);
    g += `<line x1="${xa}" x2="${xa}" y1="4" y2="${H1 + gap + H2}" stroke="var(--accent)" stroke-dasharray="5 4"/>`;
    g += `<text x="${xa - 6}" y="16" text-anchor="end">jour du dossier</text>`;
    if(!revele) g += `<rect x="${xa + 1}" y="4" width="${W - pr - xa - 1}" height="${H1 - 4}" fill="var(--accent-soft)" opacity=".5"/><text x="${(xa + W - pr) / 2}" y="${H1 / 2}" text-anchor="middle" style="font-size:30px;fill:var(--accent)">?</text><text x="${(xa + W - pr) / 2}" y="${H1 / 2 + 20}" text-anchor="middle">mois caché</text>`;
    const aire = `M${x(0)} ${y(lo)}` + chemin(s, 0, a).replace(/^M/, "L") + `L${xa} ${y(lo)}Z`;
    g += `<path d="${aire}" fill="var(--accent-soft)" opacity=".55"/>`;
    g += `<path d="${chemin(M.m50, 0, n - 1)}" fill="none" stroke="var(--warn)" stroke-width="1.6"/>`;
    g += `<path d="${chemin(M.m20, 0, n - 1)}" fill="none" stroke="var(--accent)" stroke-width="1.4"/>`;
    g += `<path d="${chemin(s, 0, a)}" fill="none" stroke="var(--ink)" stroke-width="2.2" stroke-linejoin="round"/>`;
    g += `<text x="${pl + 4}" y="${H1 + gap + 12}">RSI 14 j</text>`;
    if(revele){
      const up = s.at(-1) >= s[a];
      if(etat && etat.bas != null) g += `<rect x="${xa}" y="${y(etat.haut).toFixed(1)}" width="${W - pr - xa}" height="${(y(etat.bas) - y(etat.haut)).toFixed(1)}" fill="var(--accent)" opacity=".12"/><text x="${W - pr - 4}" y="${(y(etat.haut) - 4).toFixed(1)}" text-anchor="end">ta fourchette</text>`;
      g += `<path class="ds-futur" pathLength="1" d="${chemin(s, a, s.length - 1)}" fill="none" stroke="${up ? "var(--up)" : "var(--down)"}" stroke-width="2.6"/>`;
      g += `<circle cx="${x(s.length - 1)}" cy="${y(s.at(-1))}" r="4" fill="${up ? "var(--up)" : "var(--down)"}"/>`;
    }
    let dr = ""; for(let i = 0; i < n; i++){ if(M.r[i] == null) continue; dr += (dr ? "L" : "M") + x(i).toFixed(1) + " " + yr(M.r[i]).toFixed(1); }
    g += `<path d="${dr}" fill="none" stroke="var(--muted)" stroke-width="1.3"/>`;
    g += `<line class="ds-cx" x1="0" x2="0" y1="4" y2="${H1 + gap + H2}" stroke="var(--muted)" opacity="0"/>`;
    G.innerHTML = `<svg viewBox="0 0 ${W} ${H1 + gap + H2 + 6}" role="img" aria-label="Graphique du dossier : cours sur ${a + 1} séances, moyennes 20 et 50 jours, RSI 14 jours${revele ? ", puis le mois suivant" : ""}">${g}</svg><div class="ds-bulle" hidden></div>`;
    const svg = G.querySelector("svg"), bulle = G.querySelector(".ds-bulle"), cx = svg.querySelector(".ds-cx");
    const bouger = e => {
      const r = svg.getBoundingClientRect(), px = (e.clientX - r.left) / r.width * W;
      const i = Math.max(0, Math.min(n - 1, Math.round((px - pl) / (W - pl - pr) * total)));
      cx.setAttribute("x1", x(i)); cx.setAttribute("x2", x(i)); cx.setAttribute("opacity", ".6");
      bulle.hidden = false; bulle.style.left = (x(i) / W * 100) + "%"; bulle.style.top = (y(s[i]) / (H1 + gap + H2 + 6) * 100) + "%";
      bulle.textContent = `${i <= a ? "J" + (i - a) : "J+" + (i - a)} · ${s[i].toFixed(1).replace(".", ",")}${M.r[i] != null ? " · RSI " + Math.round(M.r[i]) : ""}`;
    };
    svg.addEventListener("pointermove", bouger);
    svg.addEventListener("pointerleave", () => { bulle.hidden = true; cx.setAttribute("opacity", "0"); });
  }

  function options(bonne, autres, fmt){
    const vals = [bonne]; for(const v of autres){ if(vals.every(w => fmt(w) !== fmt(v))) vals.push(v); }
    const r = graine(auj + "o" + bonne); return vals.slice(0, 4).map(v => ({v, txt: fmt(v), bon: v === bonne})).sort(() => r() - .5);
  }
  function questions(){
    const T = {h:"Haussière", b:"Baissière", n:"Sans direction nette"};
    const dd = M.dd * 100, e50 = M.ecart50 * 100, sd = M.sd * 100, sdm = M.sdm * 100;
    return [
      {titre:"1. Quelle est la tendance de fond au jour du dossier ?", cons:"Regarde la ligne orange (moyenne 50 jours) sur le dernier mois : monte-t-elle ou descend-elle ? Et le cours est-il au-dessus ou en dessous ?",
       opts:["h", "b", "n"].map(k => ({v:k, txt:T[k], bon:k === M.tend})),
       expl:`Sur le dernier mois, la moyenne 50 jours a ${M.pente50 >= 0 ? "monté" : "baissé"} de <b>${f1(Math.abs(M.pente50) * 100).slice(1)}</b> et le cours finit <b>${M.ecart50 >= 0 ? "au-dessus" : "en dessous"}</b> de cette moyenne (${f1(e50)}). Règle : haussière si la moyenne 50 jours monte de plus de 2 % en un mois <i>et</i> que le cours est au-dessus ; baissière si elle baisse de plus de 2 % <i>et</i> que le cours est en dessous ; sinon, pas de direction nette.`,
       methode:"Tendance = pente de la moyenne longue + position du cours. Les deux doivent aller dans le même sens."},
      {titre:"2. Quelle a été la pire baisse depuis un sommet ?", cons:"C'est le « drawdown maximal » : la plus forte chute entre un plus haut et un plus bas qui le suit.",
       opts:options(Math.round(dd), [Math.round(dd / 2), Math.round(dd * 1.7), Math.round(Math.min(-2, M.perf * 100)), Math.round(dd) - 9], v => f0(v)),
       expl:`Le pire recul depuis un sommet a été de <b>${f1(dd)}</b>. Pour le trouver : on garde en mémoire le plus haut atteint, et chaque jour on calcule cours ÷ plus haut − 1 ; la valeur la plus basse est le drawdown maximal.`,
       methode:"Drawdown = cours ÷ plus haut précédent − 1. C'est la mesure de risque que ressent vraiment un investisseur."},
      {titre:"3. À combien de % de sa moyenne 50 jours le cours se trouve-t-il ?", cons:"Repère la ligne orange au jour du dossier et compare-la au dernier cours.",
       opts:options(Math.round(e50), [-Math.round(e50) || 4, Math.round(e50) + (e50 >= 0 ? 7 : -7), Math.round(e50 / 3) + (e50 >= 0 ? -3 : 3)], v => f0(v)),
       expl:`Dernier cours ${M.x.toFixed(1).replace(".", ",")}, moyenne 50 jours ${M.m50[M.a].toFixed(1).replace(".", ",")} : écart <b>${f1(e50)}</b>. Plus l'écart est grand, plus le mouvement récent a été rapide${Math.abs(e50) > 10 ? " : ici, il est important, un retour vers la moyenne est fréquent mais pas automatique" : ""}.`,
       methode:"Écart à la moyenne = cours ÷ moyenne − 1."},
      {titre:"4. D'après la volatilité, de combien le prix bouge-t-il « habituellement » en un mois ?", cons:`L'écart-type des variations quotidiennes sur 60 séances vaut ${sd.toFixed(2).replace(".", ",")} %. Un mois ≈ 21 séances.`,
       opts:options(Math.round(sdm), [Math.max(1, Math.round(sd)), Math.round(sd * 21), Math.round(sdm * 2.2), Math.round(sdm / 2)], v => "± " + Math.abs(v) + " %"),
       expl:`Les variations s'additionnent au hasard : l'écart se multiplie par √21 ≈ 4,6 et non par 21. ${sd.toFixed(2).replace(".", ",")} % × 4,6 ≈ <b>± ${sdm.toFixed(1).replace(".", ",")} %</b> en un mois, environ 2 fois sur 3. Pour 9 fois sur 10, on prend environ 1,6 fois plus : ± ${(sdm * 1.645).toFixed(0)} %.`,
       methode:"Volatilité sur n jours = volatilité quotidienne × √n."},
    ];
  }

  function etapes(){ ET.innerHTML = [0, 1, 2, 3, 4, 5].map(i => `<i class="${etat.rep[i] === true ? "ok" : etat.rep[i] === false ? "ko" : i === etat.k ? "on" : ""}"></i>`).join(""); }

  function voir(el, ou){ if(!el) return; requestAnimationFrame(() => { const r = el.getBoundingClientRect(), bas = innerHeight - (innerWidth < 900 ? 110 : 30);
      if(ou === "start" ? (r.top < 100 || r.top > innerHeight * .6) : r.bottom > bas) el.scrollIntoView({behavior:"smooth", block:ou === "start" ? "start" : "end"}); }); }
  function poser(){
    etapes();
    const qs = questions();
    if(etat.k < 4){
      const q = qs[etat.k];
      Q.innerHTML = `<p class="ds-num">Question ${etat.k + 1} sur 4 · méthode</p><h3>${q.titre.replace(/^\d\. /, "")}</h3><p class="ds-cons">${q.cons}</p><div class="ds-opts" role="group" aria-label="Choisis une réponse">${q.opts.map((o, i) => `<button type="button" data-i="${i}" aria-pressed="false">${o.txt}</button>`).join("")}</div>
        <p class="ds-valider"><button class="btn" type="button" id="ds-val" disabled>Choisis une réponse</button></p><div class="ds-suite"></div>`;
      let choisi = null; const val = Q.querySelector("#ds-val");
      Q.querySelectorAll(".ds-opts button").forEach(b => b.onclick = () => { if(b.disabled) return; choisi = b;
        Q.querySelectorAll(".ds-opts button").forEach(x => x.setAttribute("aria-pressed", x === b)); val.disabled = false; val.textContent = "Valider ma réponse"; });
      val.onclick = () => { if(!choisi) return; const b = choisi; val.closest("p").remove();
        const o = q.opts[+b.dataset.i]; etat.rep[etat.k] = !!o.bon;
        Q.querySelectorAll(".ds-opts button").forEach((x, i) => { x.disabled = true; if(q.opts[i].bon) x.classList.add("bon"); else if(x === b) x.classList.add("faux"); });
        Q.querySelector(".ds-suite").innerHTML = `<div class="ds-expl"><b class="m">${o.bon ? "Juste." : "Pas tout à fait."} Méthode : ${q.methode}</b>${q.expl}</div><p><button class="btn" type="button" id="ds-next">Question suivante</button></p>`;
        etapes(); sauverEtat();
        const n = Q.querySelector("#ds-next"); n.focus({preventScroll:true}); voir(Q.querySelector(".ds-suite"), "nearest"); n.onclick = () => { etat.k++; sauverEtat(); poser(); voir(Q, "start"); };
      };
      return;
    }
    if(etat.k === 4){
      Q.innerHTML = `<h3>5. Ton pronostic à un mois</h3><p class="ds-cons">Plus haut ou plus bas dans 21 séances, et avec quelle confiance ? Être sûr à 90 % et se tromper coûte cher : c'est la règle des prévisionnistes.</p>
        <div class="ds-sens"><button type="button" class="h" data-s="1" aria-pressed="false">Plus haut ↑</button><button type="button" class="b" data-s="0" aria-pressed="false">Plus bas ↓</button></div>
        <div class="ds-reg"><label for="ds-conf">Ta confiance <b id="ds-conf-v">60 %</b></label><input type="range" id="ds-conf" min="50" max="95" step="5" value="60"></div>
        <p><button class="btn" type="button" id="ds-ok" disabled>Choisis d'abord plus haut ou plus bas</button></p>`;
      let sens = null; const c = Q.querySelector("#ds-conf"), ok = Q.querySelector("#ds-ok");
      Q.querySelectorAll(".ds-sens button").forEach(b => b.onclick = () => { sens = +b.dataset.s; Q.querySelectorAll(".ds-sens button").forEach(x => x.setAttribute("aria-pressed", x === b)); ok.disabled = false; ok.textContent = "Valider mon pronostic"; });
      c.oninput = () => Q.querySelector("#ds-conf-v").textContent = c.value + " %";
      ok.onclick = () => { etat.sens = sens; etat.conf = +c.value / 100; etat.k = 5; sauverEtat(); poser(); voir(Q, "start"); };
      return;
    }
    if(etat.k === 5){
      const sdm = M.sdm * 100;
      Q.innerHTML = `<h3>6. Ta fourchette de prix dans un mois</h3><p class="ds-cons">Choisis l'écart autour du prix du jour (100) dans lequel tu penses que le prix finira. Plus elle est étroite, plus elle rapporte, mais si le prix sort, tu n'as rien. Indice : ta réponse à la question 4.</p>
        <div class="ds-reg"><label for="ds-l">Largeur : <b id="ds-l-v"></b></label><input type="range" id="ds-l" min="2" max="40" step="1" value="${Math.min(40, Math.max(2, Math.round(sdm * 1.6)))}"></div>
        <p><button class="btn" type="button" id="ds-ok">Valider et voir la suite du graphique</button></p>`;
      const l = Q.querySelector("#ds-l"), v = () => { Q.querySelector("#ds-l-v").textContent = `± ${l.value} % · entre ${(M.x * (1 - l.value / 100)).toFixed(1).replace(".", ",")} et ${(M.x * (1 + l.value / 100)).toFixed(1).replace(".", ",")}`; };
      l.oninput = v; v();
      Q.querySelector("#ds-ok").onclick = () => { etat.largeur = +l.value / 100; etat.bas = M.x * (1 - etat.largeur); etat.haut = M.x * (1 + etat.largeur); etat.k = 6; sauverEtat(); poser(); voir(G, "start"); };
      return;
    }
    bilan();
  }

  function bilan(){
    const s = M.s, fin = s.at(-1), r = fin / M.x - 1, hausse = r > 0;
    const brier = (p, y) => (p - y) ** 2;
    const pToi = etat.sens ? etat.conf : 1 - etat.conf, bToi = brier(pToi, hausse ? 1 : 0), bIA = brier(it.p, hausse ? 1 : 0);
    const ptsQ = etat.rep.slice(0, 4).filter(Boolean).length * 10;
    const ptsP = Math.round(Math.max(0, 30 * (1 - bToi / .25)) * (bToi <= .25 ? 1 : 0));
    const dedans = fin >= etat.bas && fin <= etat.haut, ref = 2 * M.sdm * 1.645;
    const ptsF = dedans ? Math.max(5, Math.round(30 * Math.min(1, 1.25 - etat.largeur * 2 / ref * .5))) : 0;
    const total = Math.min(100, ptsQ + ptsP + ptsF);
    etat.rep[4] = bToi < .25; etat.rep[5] = dedans; etat.score = total; etat.fini = true; sauverEtat(); etapes();
    dessiner(true);
    const tk = T.find(x => x.ticker === it.t), nom = tk ? tk.nom : it.t.replace(/-USD$/, "");
    const tous = Object.values(S.jours).filter(j => j.fini && j.score != null), moy = tous.length ? Math.round(tous.reduce((x, j) => x + j.score, 0) / tous.length) : total;
    document.getElementById("ds-titre").textContent = `${nom} · période réelle du ${fmtDate(it.d)}`;
    Q.innerHTML = `<h3>Résultat du dossier</h3>
      <p>C'était <b>${esc(nom)}</b>, au ${fmtDate(it.d)}. Un mois plus tard : <b class="${hausse ? "up" : "down"}">${f1(r * 100)}</b>.</p>
      <div class="ds-bilan">
        <div><span>Ton score du jour</span><b class="ds-score">${total}<small style="font-size:15px"> / 100</small></b></div>
        <div><span>Analyse (4 questions)</span><b>${ptsQ} / 40</b></div>
        <div><span>Pronostic (${etat.sens ? "hausse" : "baisse"}, ${Math.round(etat.conf * 100)} %)</span><b>${ptsP} / 30</b><span>score de Brier ${bToi.toFixed(3).replace(".", ",")} · l'IA ${bIA.toFixed(3).replace(".", ",")}</span></div>
        <div><span>Fourchette ± ${Math.round(etat.largeur * 100)} %</span><b>${ptsF} / 30</b><span>${dedans ? "le prix est resté dedans" : "le prix en est sorti"}</span></div>
      </div>
      <div class="ds-expl"><b class="m">Face à l'IA</b>L'IA donnait <b>${Math.round(it.p * 100)} chances sur 100</b> de hausse : elle ${(it.p > .5) === hausse ? "a vu juste" : "s'est trompée"}. ${bToi < bIA ? "Ton pronostic était mieux calibré que le sien aujourd'hui." : bToi === bIA ? "Même précision que l'IA." : "Son pronostic était mieux calibré que le tien aujourd'hui."}
      Le score de Brier mesure l'écart entre la confiance annoncée et ce qui s'est passé : 0 = parfait, 0,25 = pile ou face, 1 = sûr de soi et faux.</div>
      <p class="muted" style="font-size:13px">Ta moyenne sur ${tous.length} dossier${tous.length > 1 ? "s" : ""} : <b>${moy} / 100</b>. Nouveau dossier demain, le même pour tout le monde.</p>
      <p><button class="btn" type="button" id="ds-copier">Copier mon score</button> <a class="btn ghost" href="formation/bougies-tendances.html">Revoir la méthode à l'Académie</a></p>`;
    Q.querySelector("#ds-copier").onclick = async () => { const t = `Radar Bourse · Dossier du ${new Date().toLocaleDateString("fr-FR")} : ${total}/100 (Brier ${bToi.toFixed(2)} contre ${bIA.toFixed(2)} pour l'IA)`; try{ await navigator.clipboard.writeText(t); flash("Score copié."); }catch(e){ flash(t); } };
  }

  function sauverEtat(){ S.jours[auj] = etat; sauver(); }

  async function demarrer(){
    let items = DATA.jeu_temps;
    try{ if(typeof items === "string") items = await fetch(items).then(r => r.json()); items = items && items.items || items; }catch(e){ items = null; }
    items = (items || []).filter(x => x && Array.isArray(x.s) && x.a >= 60 && x.s.length > x.a + 5 && x.p != null);
    if(!items.length){ G.innerHTML = `<p class="muted">Le dossier du jour n'a pas pu être chargé. Vérifie ta connexion puis recharge la page.</p>`; return; }
    const r = graine("dossier-" + auj); it = items[Math.floor(r() * items.length)];
    M = mesures(it);
    etat = S.jours[auj] && S.jours[auj].t === it.t ? S.jours[auj] : {t:it.t, k:0, rep:[]};
    const nb = Object.keys(S.jours).length;
    document.getElementById("ds-num").textContent = `Dossier du ${new Date().toLocaleDateString("fr-FR", {day:"numeric", month:"long"})}${nb > 1 ? ` · ton ${nb}e dossier` : ""}`;
    dessiner(etat.k >= 6); poser();
  }
  const io = window.IntersectionObserver ? new IntersectionObserver(e => { if(e.some(x => x.isIntersecting)){ io.disconnect(); demarrer(); } }, {rootMargin:"300px"}) : null;
  io ? io.observe(box) : demarrer();
})();
"""
