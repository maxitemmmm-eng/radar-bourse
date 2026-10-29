"""Version 52 : outils gratuits (calculateurs) — ce que les gens cherchent le plus sur Google :
« si j'avais investi 100 € dans le bitcoin », « convertisseur bitcoin euro », « calculateur intérêts composés »,
« calcul plus-value flat tax ». Chaque outil marche sur les VRAIS cours suivis par le radar, sans compte ni cookie.
Les données sont intégrées à la page (pas de chargement à part) : l'outil marche même hors connexion."""
from __future__ import annotations

import json
import os
from datetime import datetime

from . import seo

NOM = seo.NOM
_e = seo._e

# Taux en France en 2026 (12,8 % d'impôt + 18,6 % de prélèvements sociaux) — modifiable dans l'outil
TAUX_FLAT_TAX = 31.4


def _cours(payload: dict) -> dict:
    """Clôtures hebdomadaires (environ 80 semaines) de chaque titre + prix actuel : assez pour « si j'avais investi »."""
    titres = []
    for t in payload.get("titres", []):
        s = t.get("serie") or {}
        dates, cl = s.get("t") or [], s.get("c") or []
        pts = [(d, c) for d, c in zip(dates, cl) if c is not None and c > 0]
        if len(pts) < 30 or not t.get("prix"):
            continue
        hebdo, der = [], None              # une clôture par semaine (7 jours de calendrier), en partant de la plus récente
        for d, c in reversed(pts):
            jour = datetime.strptime(d, "%Y-%m-%d")
            if der is None or (der - jour).days >= 7:
                hebdo.append((d, c)); der = jour
        hebdo.reverse()
        titres.append({"tk": t["ticker"], "a": seo.aff_tk(t["ticker"]), "n": t.get("nom") or t["ticker"],
                       "d": {"€": "EUR", "$": "USD"}.get(t.get("devise", ""), t.get("devise", "")), "m": t.get("marche", ""), "p": t["prix"], "s": seo.slug(t["ticker"]),
                       "t": [d for d, _ in hebdo], "c": [float(f"{c:.6g}") for _, c in hebdo]})
    titres.sort(key=lambda x: (x["m"] != "crypto", x["n"].lower()))
    return {"maj": payload.get("date_donnees", ""), "usd_eur": payload.get("usd_eur") or 0.92, "titres": titres}


def _date_fr(iso) -> str:
    try:
        return seo.date_longue(str(iso)[:10])
    except (ValueError, TypeError):
        return str(iso or "")


def _json(d) -> str:
    return json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _jsonld(base, chemin, nom, desc, faq):
    url = (base + chemin) if base else None
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": nom, "description": desc, "url": url, "applicationCategory": "FinanceApplication",
         "operatingSystem": "Tous (navigateur web)", "inLanguage": "fr", "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
         "publisher": {"@type": "Organization", "name": NOM}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]},
        seo._jsonld_fil(base, [(NOM, ""), ("Outils gratuits", "outils.html"), (nom, chemin)])]}


def _faq_html(faq):
    return "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq)


# Style commun aux outils (formulaire, résultat, graphique), avec les couleurs du site
CSS_OUTIL = """<style>
.outil{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));align-items:end}
.outil label{display:grid;gap:4px;font-size:14px;font-weight:600}
.outil [hidden]{display:none}
.outil input,.outil select{font:inherit;font-weight:400;height:42px;padding:0 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);width:100%}
.res{font-size:17px}.res .gros{display:block;font-family:var(--d);font-size:clamp(28px,6vw,40px);font-weight:700;line-height:1.15;margin:4px 0}
.graphe{width:100%;height:auto;display:block;margin-top:10px}
.graphe text{font:12px var(--f);fill:var(--muted)}
.partage{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.partage button,.partage a{font:inherit;font-size:14px;font-weight:600;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;text-decoration:none}
.choix-mode{display:flex;gap:6px;flex-wrap:wrap}.choix-mode button{font:inherit;font-size:14px;padding:7px 12px;border-radius:99px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.choix-mode button[aria-pressed="true"]{background:var(--ink);color:var(--surface);border-color:var(--ink)}
table.annees td{font-family:var(--m);font-variant-numeric:tabular-nums}table.annees td:first-child{font-family:var(--f)}
</style>"""

# Petites fonctions JavaScript partagées : formats français, graphique en SVG, partage du lien
JS_COMMUN = r"""<script>
const fmt=(v,d)=>new Intl.NumberFormat('fr-FR',{maximumFractionDigits:d==null?2:d,minimumFractionDigits:d==null?0:Math.min(d,2)}).format(v);
const fmtM=(v,dev)=>fmt(v,Math.abs(v)<1?4:2)+' '+(dev==='EUR'?'€':dev==='USD'?'$':dev||'');
function courbe(el,xs,series,etiq){ // series: [{v:[...],c:'var(--accent)'}]
  const W=640,H=220,P=34,tous=series.flatMap(s=>s.v).filter(Number.isFinite);if(!tous.length){el.innerHTML='';return}
  let lo=Math.min(...tous),hi=Math.max(...tous);if(hi===lo){hi+=1;lo-=1}const m=(hi-lo)*.08;lo-=m;hi+=m;
  const X=i=>P+(W-P-8)*i/Math.max(1,xs.length-1),Y=v=>8+(H-P-8)*(1-(v-lo)/(hi-lo));
  let s=`<svg class="graphe" viewBox="0 0 ${W} ${H}" role="img" aria-label="${etiq}">`;
  [lo+(hi-lo)*.1,(lo+hi)/2,hi-(hi-lo)*.1].forEach(v=>{s+=`<line x1="${P}" x2="${W-8}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)"/><text x="2" y="${Y(v)+4}">${fmt(v,v<10?2:0)}</text>`});
  s+=`<text x="${P}" y="${H-8}">${xs[0]||''}</text><text x="${W-8}" y="${H-8}" text-anchor="end">${xs[xs.length-1]||''}</text>`;
  series.forEach(se=>{s+=`<polyline fill="none" stroke="${se.c}" stroke-width="2.4" ${se.tiret?'stroke-dasharray="6 5"':''} points="${se.v.map((v,i)=>X(i).toFixed(1)+','+Y(v).toFixed(1)).join(' ')}"/>`});
  el.innerHTML=s+'</svg>';
}
function partager(titre){
  const u=location.href;
  if(navigator.share){navigator.share({title:titre,url:u}).catch(()=>{});return}
  (navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>{const b=document.getElementById('btn-partage');if(b){b.textContent='Lien copié ✓';setTimeout(()=>b.textContent='Partager ce résultat',2500)}}).catch(()=>prompt('Copie ce lien :',u));
}
</script>"""


def _bloc_partage(titre_js: str) -> str:
    return (f"<div class='partage'><button type='button' id='btn-partage' onclick=\"partager({_e(json.dumps(titre_js))})\">Partager ce résultat</button>"
            "<a id='p-wa' href='#' target='_blank' rel='noopener'>WhatsApp</a><a id='p-x' href='#' target='_blank' rel='noopener'>X (Twitter)</a></div>")


JS_LIENS_PARTAGE = r"""<script>
function majLiensPartage(texte){const u=encodeURIComponent(location.href),t=encodeURIComponent(texte);
  const wa=document.getElementById('p-wa'),x=document.getElementById('p-x');
  if(wa)wa.href='https://wa.me/?text='+t+'%20'+u; if(x)x.href='https://twitter.com/intent/tweet?text='+t+'&url='+u;}
</script>"""


# ---------------------------------------------------------------------------------------------------------------
# 1. « Si j'avais investi… » (une fois ou chaque mois), sur les vrais cours
# ---------------------------------------------------------------------------------------------------------------
def _page_investi(base, D, csp):
    chemin = "outils/si-javais-investi.html"
    nom = "Si j'avais investi… : simulateur sur les vrais cours"
    faq = [("Combien aurais-je aujourd'hui si j'avais investi 100 € dans le bitcoin il y a un an ?",
            "Choisis Bitcoin, 100 et « il y a 1 an » dans le simulateur : le calcul se fait sur les vrais cours de clôture suivis par Radar Bourse, mis à jour chaque jour."),
           ("Investir un peu chaque mois, c'est mieux qu'en une fois ?",
            "Pas forcément : si le prix monte régulièrement, investir tout au début rapporte plus. Investir chaque mois (DCA) lisse surtout le prix d'achat et réduit le risque de tout acheter au plus haut. Le simulateur compare les deux."),
           ("Le résultat tient-il compte des frais et des impôts ?",
            "Non. C'est la performance brute du cours, sans frais de courtage, sans dividendes et sans impôts. Pour les titres cotés en dollars, le résultat est en dollars (sans l'effet du change euro/dollar)."),
           ("Le passé permet-il de prévoir l'avenir ?",
            "Non. Un titre qui a beaucoup monté peut chuter ensuite. Ce simulateur montre ce qui s'est passé, pas ce qui va se passer.")]
    corps = (f"<h1>Si j'avais investi… combien j'aurais aujourd'hui ?</h1>"
             "<p>Choisis une action, un ETF ou une crypto, une somme et une date : le calcul se fait sur les <b>vrais cours</b>, "
             f"mis à jour chaque jour (données au {_e(_date_fr(D['maj']))}). Compare aussi avec un investissement <b>un peu chaque mois</b>.</p>"
             "<div class='carte'><form class='outil' id='f' onsubmit='return false'>"
             "<label>Titre<select id='tk'></select></label>"
             "<label>Somme<input id='m' type='number' min='1' step='1' value='100' inputmode='decimal'></label>"
             "<label>Il y a<select id='per'><option value='4'>1 mois</option><option value='13'>3 mois</option><option value='26'>6 mois</option>"
             "<option value='52' selected>1 an</option><option value='999'>le plus loin possible</option></select></label></form>"
             "<p class='choix-mode' role='group' aria-label='Façon d’investir'><button type='button' data-mode='une' aria-pressed='true'>En une fois</button>"
             "<button type='button' data-mode='mois' aria-pressed='false'>Chaque mois (DCA)</button></p></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div><div id='g'></div>" + _bloc_partage("Si j'avais investi…") + "</div>"
             "<p class='muted'>Performance brute du cours : sans frais, sans dividendes, sans impôts ni effet du change. "
             "Ce n'est pas un conseil d'investissement : le passé ne dit rien de l'avenir.</p>"
             "<p>Voir aussi : <a href='interets-composes.html'>calculateur d'intérêts composés</a> · <a href='plus-value.html'>calcul de plus-value et flat tax</a> · "
             "<a href='../guides.html'>guides pour débuter</a></p>" + _faq_html(faq))
    js = r"""<script>
const D=__D__;const sel=document.getElementById('tk');let mode='une';
const grp={};D.titres.forEach((t,i)=>{const g=t.m==='crypto'?'Cryptos':t.m==='etf'?'ETF et indices':'Actions';(grp[g]=grp[g]||[]).push([i,t])});
Object.entries(grp).forEach(([g,l])=>{const og=document.createElement('optgroup');og.label=g;l.forEach(([i,t])=>{const o=document.createElement('option');o.value=t.tk;o.textContent=t.n+' ('+t.a+')';og.appendChild(o)});sel.appendChild(og)});
const q=new URLSearchParams(location.search);
if(q.get('t')&&D.titres.some(t=>t.tk===q.get('t')))sel.value=q.get('t');else{const b=D.titres.find(t=>t.tk==='BTC-USD');if(b)sel.value=b.tk}
if(q.get('m'))document.getElementById('m').value=q.get('m');if(q.get('p'))document.getElementById('per').value=q.get('p');if(q.get('mode')==='mois')mode='mois';
document.querySelectorAll('[data-mode]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.mode===mode);b.onclick=()=>{mode=b.dataset.mode;document.querySelectorAll('[data-mode]').forEach(x=>x.setAttribute('aria-pressed',x===b));calc()}});
function calc(){
  const t=D.titres.find(x=>x.tk===sel.value);if(!t)return;const S=Math.max(0,+document.getElementById('m').value||0);
  const per=+document.getElementById('per').value,n=t.c.length,deb=Math.max(0,n-1-per),c=t.c.slice(deb),x=t.t.slice(deb);
  const fin=t.p,dev=t.d;let valeur,mise,parts=0,courbeV=[],courbeM=[];
  if(mode==='une'){parts=S/c[0];mise=S;c.forEach(p=>{courbeV.push(parts*p);courbeM.push(S)});valeur=parts*fin}
  else{const nbM=Math.max(1,Math.round((c.length-1)/4.33));const par=S;mise=0;
    c.forEach((p,i)=>{if(i%4===0&&mise<par*(nbM+1)-1e-9){parts+=par/p;mise+=par}courbeV.push(parts*p);courbeM.push(mise)});valeur=parts*fin}
  const g=valeur-mise,pc=mise?g/mise*100:0,haut=g>=0;
  const quand=per>=999?'depuis le '+new Date(x[0]).toLocaleDateString('fr-FR'):'il y a '+document.getElementById('per').selectedOptions[0].text;
  const phrase=mode==='une'?`${fmtM(S,dev)} investis dans ${t.n} ${quand}`:`${fmtM(S,dev)} investis chaque mois dans ${t.n} ${quand} (${fmtM(mise,dev)} au total)`;
  document.getElementById('res').innerHTML=`<p>${phrase} vaudraient aujourd'hui</p><span class="gros">${fmtM(valeur,dev)}</span>`+
    `<p class="${haut?'up':'down'}"><b>${haut?'+':''}${fmtM(g,dev)} (${haut?'+':''}${fmt(pc,1)} %)</b></p>`+
    `<p class="muted">Prix d'achat ${mode==='une'?'':'moyen '}: ${fmtM(mise/parts,dev)} · prix actuel : ${fmtM(fin,dev)}. <a href="../titres/${t.s}.html">Prévision et analyse de ${t.n}</a></p>`;
  courbe(document.getElementById('g'),x,[{v:courbeM,c:'var(--muted)',tiret:1},{v:courbeV,c:haut?'var(--up)':'var(--down)'}],'Valeur de l’investissement au fil du temps');
  const u=new URL(location.href);u.searchParams.set('t',t.tk);u.searchParams.set('m',S);u.searchParams.set('p',per);u.searchParams.set('mode',mode);history.replaceState(null,'',u);
  majLiensPartage(`${phrase} vaudraient aujourd'hui ${fmtM(valeur,dev)} (${haut?'+':''}${fmt(pc,1)} %) 👀`);
}
['tk','m','per'].forEach(id=>document.getElementById(id).addEventListener('input',calc));calc();
</script>""".replace("__D__", _json(D))
    page = seo._page(base, f"Si j'avais investi 100 € dans le bitcoin, une action… : simulateur gratuit | {NOM}",
                     "Combien vaudrait aujourd'hui 100 € investis il y a 1 an dans le bitcoin, Apple, LVMH ou un ETF ? Simulateur gratuit "
                     "sur les vrais cours, en une fois ou chaque mois (DCA).", chemin, CSS_OUTIL + corps + JS_COMMUN + JS_LIENS_PARTAGE + js,
                     _jsonld(base, chemin, nom, "Simulateur gratuit sur les vrais cours : combien vaudrait aujourd'hui un investissement passé.", faq), csp=csp,
                     alternates={"fr": chemin, "en": "en/tools/if-i-had-invested.html", "x-default": chemin})
    return chemin, page


# ---------------------------------------------------------------------------------------------------------------
# 2. Convertisseur crypto / action ↔ euro / dollar
# ---------------------------------------------------------------------------------------------------------------
def _page_convertisseur(base, D, csp):
    chemin = "outils/convertisseur.html"
    nom = "Convertisseur crypto et actions en euros"
    faq = [("Combien vaut 1 bitcoin en euros ?", "Le convertisseur affiche le dernier cours connu, converti en euros. Pour les cryptos, il essaie aussi de récupérer le prix en direct."),
           ("Combien de bitcoin pour 100 € ?", "Mets 100 dans la case « en euros » : le convertisseur calcule la quantité correspondante, au dernier cours."),
           ("Le taux de change est-il exact ?", "Il s'agit du dernier cours euro/dollar suivi par le site. Ta banque ou ta plateforme peut appliquer un taux et des frais différents.")]
    corps = ("<h1>Convertisseur crypto et actions ↔ euros et dollars</h1>"
             f"<p>Combien vaut 1 bitcoin, 0,5 ether ou 10 actions Apple en euros ? Et combien en obtenir pour 100 € ? Cours au {_e(_date_fr(D['maj']))}"
             "<span id='direct'></span>.</p>"
             "<div class='carte'><form class='outil' onsubmit='return false'>"
             "<label>Titre<select id='tk'></select></label><label>Quantité<input id='q' type='number' min='0' step='any' value='1' inputmode='decimal'></label>"
             "<label>En euros<input id='eur' type='number' min='0' step='any' inputmode='decimal'></label>"
             "<label>En dollars<input id='usd' type='number' min='0' step='any' inputmode='decimal'></label></form></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div>" + _bloc_partage("Convertisseur crypto et actions") + "</div>"
             "<p class='muted'>Prix indicatif, sans frais. Ce n'est pas un conseil d'investissement.</p>"
             "<p>Voir aussi : <a href='si-javais-investi.html'>si j'avais investi…</a> · <a href='../titres.html'>prévisions de tous les titres</a></p>" + _faq_html(faq))
    js = r"""<script>
const D=__D__;const sel=document.getElementById('tk'),Q=document.getElementById('q'),E=document.getElementById('eur'),U=document.getElementById('usd');
const ue=D.usd_eur;const grp={};D.titres.forEach(t=>{const g=t.m==='crypto'?'Cryptos':t.m==='etf'?'ETF et indices':'Actions';(grp[g]=grp[g]||[]).push(t)});
Object.entries(grp).forEach(([g,l])=>{const og=document.createElement('optgroup');og.label=g;l.forEach(t=>{const o=document.createElement('option');o.value=t.tk;o.textContent=t.n+' ('+t.a+')';og.appendChild(o)});sel.appendChild(og)});
const qs=new URLSearchParams(location.search);sel.value=(qs.get('t')&&D.titres.some(t=>t.tk===qs.get('t')))?qs.get('t'):'BTC-USD';if(qs.get('q'))Q.value=qs.get('q');
const vivant={};
function prixEnUsd(t){const p=vivant[t.tk]||t.p;return t.d==='USD'?p:t.d==='EUR'?p/ue:null}
function maj(src){const t=D.titres.find(x=>x.tk===sel.value);if(!t)return;const pu=prixEnUsd(t);if(pu==null){document.getElementById('res').innerHTML='<p>Devise non prise en charge pour ce titre.</p>';return}
  const pe=pu*ue;if(src==='eur')Q.value=+(E.value/pe).toPrecision(8);if(src==='usd')Q.value=+(U.value/pu).toPrecision(8);
  const q=+Q.value||0;if(src!=='eur')E.value=+(q*pe).toFixed(2);if(src!=='usd')U.value=+(q*pu).toFixed(2);
  document.getElementById('res').innerHTML=`<p>${fmt(q,8)} ${t.a.replace('-USD','')} =</p><span class="gros">${fmtM(q*pe,'EUR')}</span><p>soit ${fmtM(q*pu,'USD')} · 1 ${t.a.replace('-USD','')} = ${fmtM(pe,'EUR')}</p><p class="muted"><a href="../titres/${t.s}.html">Prévision à un mois pour ${t.n}</a></p>`;
  const u=new URL(location.href);u.searchParams.set('t',t.tk);u.searchParams.set('q',q);history.replaceState(null,'',u);
  majLiensPartage(`${fmt(q,8)} ${t.n} = ${fmtM(q*pe,'EUR')}`);}
Q.oninput=()=>maj('q');E.oninput=()=>maj('eur');U.oninput=()=>maj('usd');
sel.onchange=()=>{maj('q');enDirect()};
function enDirect(){const t=D.titres.find(x=>x.tk===sel.value);if(!t||t.m!=='crypto')return;const s=t.a.replace('-USD','');
  fetch('https://min-api.cryptocompare.com/data/price?fsym='+encodeURIComponent(s)+'&tsyms=USD').then(r=>r.json()).then(j=>{if(j&&j.USD>0){vivant[t.tk]=j.USD;document.getElementById('direct').textContent=' · prix de '+t.n+' en direct';maj('q')}}).catch(()=>{});}
maj('q');enDirect();
</script>""".replace("__D__", _json({**D, "titres": [{k: v for k, v in t.items() if k not in ("t", "c")} for t in D["titres"]]}))
    page = seo._page(base, f"Convertisseur bitcoin euro, crypto et actions en euros | {NOM}",
                     "Convertis bitcoin, ether, solana ou une action en euros et en dollars, dans les deux sens. Gratuit, cours du jour, prix crypto en direct.",
                     chemin, CSS_OUTIL + corps + JS_COMMUN + JS_LIENS_PARTAGE + js,
                     _jsonld(base, chemin, nom, "Convertisseur gratuit crypto et actions vers euros et dollars.", faq), csp=csp,
                     alternates={"fr": chemin, "en": "en/tools/crypto-converter.html", "x-default": chemin})
    return chemin, page


# ---------------------------------------------------------------------------------------------------------------
# 3. Intérêts composés (et « combien épargner par mois pour atteindre X »)
# ---------------------------------------------------------------------------------------------------------------
def _page_interets(base, csp):
    chemin = "outils/interets-composes.html"
    nom = "Calculateur d'intérêts composés"
    faq = [("C'est quoi les intérêts composés ?", "Les gains d'une année rapportent à leur tour l'année suivante : l'argent fait « boule de neige ». Plus la durée est longue, plus l'effet est fort."),
           ("Quel rendement mettre ?", "Il n'existe aucun rendement garanti en Bourse. Sur très longue période, les grands indices mondiaux ont fait en moyenne quelques % par an après inflation, avec des années très négatives. Essaie plusieurs hypothèses, prudentes comprises."),
           ("Combien épargner par mois pour atteindre un objectif ?", "Utilise le mode « Atteindre un objectif » : indique la somme visée, la durée et le rendement supposé, l'outil calcule le versement mensuel nécessaire.")]
    corps = ("<h1>Calculateur d'intérêts composés</h1><p>Combien vaudra ton épargne dans 10, 20 ou 30 ans, avec un versement chaque mois ? "
             "Ou combien mettre de côté pour atteindre un objectif ?</p>"
             "<p class='choix-mode' role='group' aria-label='Mode de calcul'><button type='button' data-mode='futur' aria-pressed='true'>Ce que j'aurai</button>"
             "<button type='button' data-mode='objectif' aria-pressed='false'>Atteindre un objectif</button></p>"
             "<div class='carte'><form class='outil' onsubmit='return false'>"
             "<label>Capital de départ (€)<input id='c0' type='number' min='0' step='any' value='1000' inputmode='decimal'></label>"
             "<label id='l-v'>Versement par mois (€)<input id='v' type='number' min='0' step='any' value='100' inputmode='decimal'></label>"
             "<label id='l-o' hidden>Objectif (€)<input id='o' type='number' min='0' step='any' value='50000' inputmode='decimal'></label>"
             "<label>Rendement par an (%)<input id='r' type='number' step='any' value='5' inputmode='decimal'></label>"
             "<label>Durée (années)<input id='n' type='number' min='1' max='60' step='1' value='20' inputmode='numeric'></label></form></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div><div id='g'></div>" + _bloc_partage("Calculateur d'intérêts composés") + "</div>"
             "<details class='carte'><summary>Le détail année par année</summary><div style='overflow-x:auto'><table class='annees' id='tab'></table></div></details>"
             "<p class='muted'>Hypothèse de rendement constant, sans frais ni impôts ni inflation : la réalité varie beaucoup d'une année à l'autre. "
             "Ce n'est pas un conseil d'investissement.</p>"
             "<p>Voir aussi : <a href='si-javais-investi.html'>si j'avais investi… (vrais cours)</a> · <a href='../guides/interets-composes.html'>le guide des intérêts composés</a></p>" + _faq_html(faq))
    js = r"""<script>
let mode='futur';const $=id=>document.getElementById(id);
const qs=new URLSearchParams(location.search);['c0','v','o','r','n'].forEach(k=>{if(qs.get(k))$(k).value=qs.get(k)});if(qs.get('mode')==='objectif')mode='objectif';
function bascule(){document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.mode===mode));$('l-v').hidden=mode!=='futur';$('l-o').hidden=mode!=='objectif';calc()}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;bascule()});
function serie(c0,v,r,n){const im=Math.pow(1+r/100,1/12)-1;let cap=c0,ver=c0;const ans=[{a:0,cap,ver}];for(let a=1;a<=n;a++){for(let m=0;m<12;m++){cap=cap*(1+im)+v;ver+=v}ans.push({a,cap,ver})}return ans}
function calc(){const c0=+$('c0').value||0,r=+$('r').value||0,n=Math.min(60,Math.max(1,Math.round(+$('n').value||1)));let v=+$('v').value||0;
  if(mode==='objectif'){const o=+$('o').value||0,im=Math.pow(1+r/100,1/12)-1,N=12*n,fv0=c0*Math.pow(1+im,N),k=im?((Math.pow(1+im,N)-1)/im):N;v=Math.max(0,(o-fv0)/k)}
  const s=serie(c0,v,r,n),f=s[s.length-1],gain=f.cap-f.ver;
  $('res').innerHTML=mode==='futur'?`<p>Dans ${n} ans, tu aurais environ</p><span class="gros">${fmtM(f.cap,'EUR')}</span><p>dont <b>${fmtM(f.ver,'EUR')}</b> versés par toi et <b class="up">${fmtM(gain,'EUR')}</b> d'intérêts composés.</p>`
    :`<p>Pour atteindre ${fmtM(+$('o').value||0,'EUR')} en ${n} ans, il faudrait verser environ</p><span class="gros">${fmtM(v,'EUR')} par mois</span><p>Total versé : ${fmtM(f.ver,'EUR')} · intérêts : ${fmtM(gain,'EUR')}.</p>`;
  courbe($('g'),s.map(x=>'an '+x.a),[{v:s.map(x=>x.ver),c:'var(--muted)',tiret:1},{v:s.map(x=>x.cap),c:'var(--accent)'}],'Capital et sommes versées au fil des années');
  $('tab').innerHTML='<tr><td><b>Année</b></td><td><b>Versé</b></td><td><b>Intérêts</b></td><td><b>Capital</b></td></tr>'+s.slice(1).map(x=>`<tr><td>${x.a}</td><td>${fmtM(x.ver,'EUR')}</td><td>${fmtM(x.cap-x.ver,'EUR')}</td><td>${fmtM(x.cap,'EUR')}</td></tr>`).join('');
  const u=new URL(location.href);['c0','v','o','r','n'].forEach(k=>u.searchParams.set(k,$(k).value));u.searchParams.set('mode',mode);history.replaceState(null,'',u);
  majLiensPartage(mode==='futur'?`${fmtM(+$('v').value||0,'EUR')} par mois pendant ${n} ans à ${fmt(r,1)} % = ${fmtM(f.cap,'EUR')} 🤯`:`Objectif ${fmtM(+$('o').value||0,'EUR')} en ${n} ans : ${fmtM(v,'EUR')} par mois`);}
['c0','v','o','r','n'].forEach(k=>$(k).addEventListener('input',calc));bascule();
</script>"""
    page = seo._page(base, f"Calculateur d'intérêts composés gratuit (avec versements mensuels) | {NOM}",
                     "Calcule ce que deviendra ton épargne avec des versements chaque mois, ou combien épargner pour atteindre un objectif. "
                     "Gratuit, détail année par année.", chemin, CSS_OUTIL + corps + JS_COMMUN + JS_LIENS_PARTAGE + js,
                     _jsonld(base, chemin, nom, "Calculateur gratuit d'intérêts composés avec versements mensuels et mode objectif.", faq), csp=csp)
    return chemin, page


# ---------------------------------------------------------------------------------------------------------------
# 4. Plus-value / moins-value et flat tax
# ---------------------------------------------------------------------------------------------------------------
def _page_plus_value(base, csp):
    chemin = "outils/plus-value.html"
    nom = "Calcul de plus-value et de flat tax"
    faq = [("Quel est le taux de la flat tax en 2026 ?",
            f"En 2026 en France, la flat tax (prélèvement forfaitaire unique) est de {str(TAUX_FLAT_TAX).replace('.', ',')} % sur les plus-values d'actions d'un compte-titres et sur les plus-values de cryptos : 12,8 % d'impôt et 18,6 % de prélèvements sociaux. Vérifie toujours sur impots.gouv.fr."),
           ("Les frais sont-ils déduits de la plus-value ?", "Oui : les frais d'achat s'ajoutent au prix de revient et les frais de vente se déduisent du prix de vente. Le calculateur en tient compte."),
           ("Et pour les cryptos ?", "Les plus-values sur cryptos sont imposables lors d'une vente contre des euros (pas lors d'un échange crypto contre crypto). Si le total des cessions de l'année ne dépasse pas 305 €, il n'y a pas d'impôt. Le calcul officiel tient compte de tout ton portefeuille crypto : ce calculateur donne une approximation."),
           ("Et dans un PEA ?", "Dans un PEA, les règles sont différentes : après 5 ans, pas d'impôt sur le revenu (seulement les prélèvements sociaux). Choisis « Autre taux » pour simuler.")]
    taux = str(TAUX_FLAT_TAX)
    corps = ("<h1>Calcul de plus-value et de flat tax</h1><p>Combien j'ai gagné (ou perdu) en vendant, frais compris, et combien d'impôt prévoir ?</p>"
             "<div class='carte'><form class='outil' onsubmit='return false'>"
             "<label>Prix d'achat (par unité)<input id='pa' type='number' min='0' step='any' value='100' inputmode='decimal'></label>"
             "<label>Prix de vente (par unité)<input id='pv' type='number' min='0' step='any' value='130' inputmode='decimal'></label>"
             "<label>Quantité<input id='q' type='number' min='0' step='any' value='10' inputmode='decimal'></label>"
             "<label>Frais (achat + vente, €)<input id='fr' type='number' min='0' step='any' value='4' inputmode='decimal'></label>"
             f"<label>Fiscalité<select id='fi'><option value='{taux}'>Compte-titres ou crypto ({taux.replace('.', ',')} %)</option>"
             "<option value='0'>Pas d'impôt (simulation)</option><option value='autre'>Autre taux…</option></select></label>"
             "<label id='l-t' hidden>Taux (%)<input id='t' type='number' min='0' max='100' step='any' value='18.6' inputmode='decimal'></label></form></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div>" + _bloc_partage("Calcul de plus-value") + "</div>"
             "<p class='muted'>Estimation simplifiée pour la France, pas un conseil fiscal. Les moins-values peuvent s'imputer sur les plus-values "
             "de la même année et des 10 années suivantes (actions). Vérifie ta situation sur impots.gouv.fr.</p>"
             "<p>Voir aussi : <a href='../guides/fiscalite-bourse.html'>comment sont imposés les gains en Bourse</a> · <a href='si-javais-investi.html'>si j'avais investi…</a></p>" + _faq_html(faq))
    js = r"""<script>
const $=id=>document.getElementById(id);
function calc(){const pa=+$('pa').value||0,pv=+$('pv').value||0,q=+$('q').value||0,fr=+$('fr').value||0;$('l-t').hidden=$('fi').value!=='autre';
  const taux=$('fi').value==='autre'?(+$('t').value||0):+$('fi').value;const brut=(pv-pa)*q,net=brut-fr,imp=net>0?net*taux/100:0,apres=net-imp,pc=pa*q?net/(pa*q+fr)*100:0;
  $('res').innerHTML=`<p>${net>=0?'Plus-value':'Moins-value'} après frais</p><span class="gros ${net>=0?'up':'down'}">${net>=0?'+':''}${fmtM(net,'EUR')}</span>`+
   `<p>${net>=0?'+':''}${fmt(pc,1)} % sur ${fmtM(pa*q+fr,'EUR')} investis · impôt estimé : <b>${fmtM(imp,'EUR')}</b> (${fmt(taux,1)} %) · <b>gain net : ${fmtM(apres,'EUR')}</b></p>`+
   (net<0?'<p class="muted">Une moins-value ne donne pas d’impôt et peut réduire l’impôt sur d’autres plus-values.</p>':'');
  majLiensPartage(`Ma plus-value : ${fmtM(net,'EUR')}, impôt estimé ${fmtM(imp,'EUR')}`);}
['pa','pv','q','fr','fi','t'].forEach(k=>$(k).addEventListener('input',calc));calc();
</script>"""
    page = seo._page(base, f"Calcul plus-value actions et crypto, flat tax 2026 ({taux.replace('.', ',')} %) | {NOM}",
                     f"Calcule ta plus-value ou moins-value après frais et l'impôt à prévoir (flat tax {taux.replace('.', ',')} % en 2026) : actions, ETF, cryptos. Gratuit.",
                     chemin, CSS_OUTIL + corps + JS_COMMUN + JS_LIENS_PARTAGE + js,
                     _jsonld(base, chemin, nom, "Calculateur gratuit de plus-value et de flat tax pour actions et cryptos.", faq), csp=csp)
    return chemin, page


OUTILS = [("outils/si-javais-investi.html", "Si j'avais investi…", "Combien vaudrait aujourd'hui 100 € placés il y a un an dans le bitcoin, une action ou un ETF ? Sur les vrais cours, en une fois ou chaque mois."),
          ("outils/convertisseur.html", "Convertisseur crypto et actions", "Bitcoin, ether, actions : la valeur en euros et en dollars, dans les deux sens."),
          ("outils/interets-composes.html", "Calculateur d'intérêts composés", "Ce que deviendra ton épargne avec un versement chaque mois, ou combien épargner pour un objectif."),
          ("outils/plus-value.html", "Calcul de plus-value et flat tax", "Ton gain après frais et l'impôt à prévoir en 2026, pour les actions et les cryptos.")]


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    os.makedirs(os.path.join(dossier, "outils"), exist_ok=True)
    D = _cours(payload)
    pages = [_page_investi(base, D, csp), _page_convertisseur(base, D, csp), _page_interets(base, csp), _page_plus_value(base, csp)]
    urls = []
    os.makedirs(os.path.join(dossier, "en", "tools"), exist_ok=True)
    try:
        pages += _pages_en(base, D, csp)
    except Exception as e:
        print(f"Outils en anglais non générés : {e}")
    for chemin, page in pages:
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily", "0.8"))
    corps = ("<h1>Outils gratuits pour la Bourse et la crypto</h1><p>Des calculateurs simples, sans compte, sans cookie publicitaire, "
             "qui marchent sur les vrais cours suivis par le radar.</p><div class='grille'>"
             + "".join(f"<a class='carte' style='text-decoration:none;color:inherit;margin:0' href='{c}'><b style='font-size:18px'>{_e(n)}</b>"
                       f"<p class='muted' style='margin:6px 0 0'>{_e(d)}</p></a>" for c, n, d in OUTILS)
             + "</div><p class='muted'>Ces outils servent à comprendre et à simuler. Ce ne sont pas des conseils d'investissement.</p>")
    jl = seo._jsonld_liste(base, "Outils gratuits pour la Bourse et la crypto", "outils.html", [(n, c) for c, n, _ in OUTILS])
    with open(os.path.join(dossier, "outils.html"), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Outils gratuits : simulateur, convertisseur crypto, intérêts composés | {NOM}",
                          "Simulateur « si j'avais investi », convertisseur bitcoin euro, calculateur d'intérêts composés et de plus-value : gratuits, sur les vrais cours.",
                          "outils.html", corps, jl, csp=csp))
    urls.append(("outils.html", "weekly", "0.8"))
    return urls


def valeur_un_an(t: dict):
    """Pour la fiche d'un titre : ce que seraient devenus 100 (dans la devise du titre) placés il y a un an et six mois
    (première clôture à partir de cette date du calendrier)."""
    s = t.get("serie") or {}
    pts = [(d, c) for d, c in zip(s.get("t") or [], s.get("c") or []) if c]
    if len(pts) < 100 or not t.get("prix"):
        return None
    from datetime import timedelta
    der = datetime.strptime(pts[-1][0], "%Y-%m-%d")
    out = {}
    for cle, jours in (("an", 365), ("six_mois", 182)):
        cible = (der - timedelta(days=jours)).strftime("%Y-%m-%d")
        if pts[0][0] <= cible:
            d0, c0 = next((d, c) for d, c in pts if d >= cible)
            out[cle] = (d0, 100 * t["prix"] / c0)
    return out or None


# ---------------------------------------------------------------------------------------------------------------
# Version anglaise des deux outils les plus recherchés dans le monde
# ---------------------------------------------------------------------------------------------------------------
import re as _re
JS_COMMUN_EN = _re.sub(r"const fmtM=[^\n]*", lambda m: "const fmtM=(v,dev)=>(v<0?'-':'')+(dev==='USD'?'$':'')+fmt(Math.abs(v),Math.abs(v)<1?4:2)+(dev==='EUR'?'\\u00a0€':dev&&dev!=='USD'?'\\u00a0'+dev:'');",
                       JS_COMMUN.replace("'fr-FR'", "'en-US'").replace("Lien copié ✓", "Link copied ✓")
                       .replace("Partager ce résultat", "Share this result").replace("Copie ce lien :", "Copy this link:"), count=1)


def _avec_jsonld(page, jl):
    return page.replace("</head>", f'<script type="application/ld+json">{_json(jl)}</script>\n</head>', 1)


def _jsonld_en(base, chemin, nom, desc, faq):
    url = (base + chemin) if base else None
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": nom, "description": desc, "url": url, "applicationCategory": "FinanceApplication",
         "operatingSystem": "Any (web browser)", "inLanguage": "en", "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@type": "Organization", "name": NOM}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}]}


def _pages_en(base, D, csp):
    from . import anglais
    out = []
    # 1. If I had invested…
    chemin = "en/tools/if-i-had-invested.html"
    faq = [("How much would I have if I had invested $100 in Bitcoin one year ago?",
            "Pick Bitcoin, 100 and \"1 year ago\": the result uses the real daily closing prices tracked by Radar Bourse, updated every day."),
           ("Is investing every month better than all at once?",
            "Not always: when prices rise steadily, investing everything at the start earns more. Monthly investing (DCA) mainly smooths your buying price. The simulator compares both."),
           ("Does it include fees and taxes?", "No. It is the raw price performance: no fees, dividends, taxes or currency effects."),
           ("Does the past predict the future?", "No. An asset that rose a lot can fall afterwards. This shows what happened, not what will happen.")]
    corps = ("<h1>If I had invested… how much would I have today?</h1>"
             f"<p>Pick a stock, an ETF or a crypto, an amount and a date: the result uses <b>real prices</b>, updated daily (data as of {_e(D['maj'])}). "
             "Compare with investing <b>a little every month</b> too.</p>"
             "<div class='carte'><form class='outil' onsubmit='return false'><label>Asset<select id='tk'></select></label>"
             "<label>Amount<input id='m' type='number' min='1' step='1' value='100' inputmode='decimal'></label>"
             "<label>Invested<select id='per'><option value='4'>1 month ago</option><option value='13'>3 months ago</option><option value='26'>6 months ago</option>"
             "<option value='52' selected>1 year ago</option><option value='999'>as far back as possible</option></select></label></form>"
             "<p class='choix-mode' role='group' aria-label='How to invest'><button type='button' data-mode='une' aria-pressed='true'>All at once</button>"
             "<button type='button' data-mode='mois' aria-pressed='false'>Every month (DCA)</button></p></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div><div id='g'></div><div class='partage'><button type='button' id='btn-partage' "
             "onclick=\"partager('If I had invested…')\">Share this result</button><a id='p-wa' href='#' target='_blank' rel='noopener'>WhatsApp</a>"
             "<a id='p-x' href='#' target='_blank' rel='noopener'>X (Twitter)</a></div></div>"
             "<p class='muted'>Raw price performance: no fees, dividends, taxes or currency effects. Not investment advice: the past says nothing about the future.</p>"
             "<p>See also: <a href='crypto-converter.html'>crypto converter</a> · <a href='../guides.html'>beginner guides</a></p>"
             "<h2>FAQ</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq))
    js = r"""<script>
const D=__D__;const sel=document.getElementById('tk');let mode='une';
const grp={};D.titres.forEach(t=>{const g=t.m==='crypto'?'Crypto':t.m==='etf'?'ETFs and indices':'Stocks';(grp[g]=grp[g]||[]).push(t)});
Object.entries(grp).forEach(([g,l])=>{const og=document.createElement('optgroup');og.label=g;l.forEach(t=>{const o=document.createElement('option');o.value=t.tk;o.textContent=t.n+' ('+t.a+')';og.appendChild(o)});sel.appendChild(og)});
const q=new URLSearchParams(location.search);sel.value=(q.get('t')&&D.titres.some(t=>t.tk===q.get('t')))?q.get('t'):'BTC-USD';
if(q.get('m'))document.getElementById('m').value=q.get('m');if(q.get('p'))document.getElementById('per').value=q.get('p');if(q.get('mode')==='mois')mode='mois';
document.querySelectorAll('[data-mode]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.mode===mode);b.onclick=()=>{mode=b.dataset.mode;document.querySelectorAll('[data-mode]').forEach(x=>x.setAttribute('aria-pressed',x===b));calc()}});
function calc(){const t=D.titres.find(x=>x.tk===sel.value);if(!t)return;const S=Math.max(0,+document.getElementById('m').value||0);
  const per=+document.getElementById('per').value,n=t.c.length,deb=Math.max(0,n-1-per),c=t.c.slice(deb),x=t.t.slice(deb),fin=t.p,dev=t.d;let mise,parts=0,V=[],M=[];
  if(mode==='une'){parts=S/c[0];mise=S;c.forEach(p=>{V.push(parts*p);M.push(S)})}else{const nbM=Math.max(1,Math.round((c.length-1)/4.33));mise=0;c.forEach((p,i)=>{if(i%4===0&&mise<S*(nbM+1)-1e-9){parts+=S/p;mise+=S}V.push(parts*p);M.push(mise)})}
  const valeur=parts*fin,g=valeur-mise,pc=mise?g/mise*100:0,up=g>=0;
  const quand=per>=999?'since '+new Date(x[0]).toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric'}):document.getElementById('per').selectedOptions[0].text;
  const phrase=mode==='une'?`${fmtM(S,dev)} invested in ${t.n} ${quand}`:`${fmtM(S,dev)} invested in ${t.n} every month ${quand.replace(' ago','')} on (${fmtM(mise,dev)} in total)`;
  document.getElementById('res').innerHTML=`<p>${phrase} would be worth today</p><span class="gros">${fmtM(valeur,dev)}</span><p class="${up?'up':'down'}"><b>${up?'+':''}${fmtM(g,dev)} (${up?'+':''}${fmt(pc,1)}%)</b></p><p class="muted">Average buy price: ${fmtM(mise/parts,dev)} · price now: ${fmtM(fin,dev)}. <a href="../stocks/${t.s}.html">${t.n} one-month forecast</a></p>`;
  courbe(document.getElementById('g'),x,[{v:M,c:'var(--muted)',tiret:1},{v:V,c:up?'var(--up)':'var(--down)'}],'Investment value over time');
  const u=new URL(location.href);u.searchParams.set('t',t.tk);u.searchParams.set('m',S);u.searchParams.set('p',per);u.searchParams.set('mode',mode);history.replaceState(null,'',u);
  majLiensPartage(`${phrase} would be worth ${fmtM(valeur,dev)} today (${up?'+':''}${fmt(pc,1)}%) 👀`);}
['tk','m','per'].forEach(id=>document.getElementById(id).addEventListener('input',calc));calc();
</script>""".replace("__D__", _json(D))
    alt = {"en": chemin, "fr": "outils/si-javais-investi.html", "x-default": "outils/si-javais-investi.html"}
    page = anglais._page(base, f"If I had invested $100 in Bitcoin (or any stock): free calculator | {NOM}",
                         "How much would $100 invested in Bitcoin, Apple, Nvidia or an ETF one year ago be worth today? Free calculator on real prices, lump sum or monthly (DCA).",
                         chemin, CSS_OUTIL + corps + JS_COMMUN_EN + JS_LIENS_PARTAGE + js, csp, alt)
    out.append((chemin, _avec_jsonld(page, _jsonld_en(base, chemin, "If I had invested… calculator", "Free calculator on real prices.", faq))))
    # 2. Crypto converter
    chemin = "en/tools/crypto-converter.html"
    faq = [("How much is 1 Bitcoin in dollars or euros?", "The converter shows the latest known price, in dollars and euros. For cryptos it also tries to fetch the live price."),
           ("How much Bitcoin can I buy with $100?", "Type 100 in the \"in dollars\" box: the converter computes the matching amount at the latest price."),
           ("Is the exchange rate exact?", "It is the latest euro/dollar rate tracked by the site. Your bank or exchange may apply a different rate and fees.")]
    corps = ("<h1>Crypto and stock converter: USD and EUR</h1>"
             f"<p>How much is 1 Bitcoin, 0.5 Ether or 10 Apple shares worth? And how much can you get for $100? Prices as of {_e(D['maj'])}<span id='direct'></span>.</p>"
             "<div class='carte'><form class='outil' onsubmit='return false'><label>Asset<select id='tk'></select></label>"
             "<label>Quantity<input id='q' type='number' min='0' step='any' value='1' inputmode='decimal'></label>"
             "<label>In dollars<input id='usd' type='number' min='0' step='any' inputmode='decimal'></label>"
             "<label>In euros<input id='eur' type='number' min='0' step='any' inputmode='decimal'></label></form></div>"
             "<div class='carte res' aria-live='polite'><div id='res'></div><div class='partage'><button type='button' id='btn-partage' "
             "onclick=\"partager('Crypto converter')\">Share this result</button><a id='p-wa' href='#' target='_blank' rel='noopener'>WhatsApp</a>"
             "<a id='p-x' href='#' target='_blank' rel='noopener'>X (Twitter)</a></div></div>"
             "<p class='muted'>Indicative price, no fees. Not investment advice.</p>"
             "<p>See also: <a href='if-i-had-invested.html'>if I had invested…</a> · <a href='../index.html'>forecasts for every asset</a></p>"
             "<h2>FAQ</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq))
    js = r"""<script>
const D=__D__;const sel=document.getElementById('tk'),Q=document.getElementById('q'),E=document.getElementById('eur'),U=document.getElementById('usd'),ue=D.usd_eur,vivant={};
const grp={};D.titres.forEach(t=>{const g=t.m==='crypto'?'Crypto':t.m==='etf'?'ETFs and indices':'Stocks';(grp[g]=grp[g]||[]).push(t)});
Object.entries(grp).forEach(([g,l])=>{const og=document.createElement('optgroup');og.label=g;l.forEach(t=>{const o=document.createElement('option');o.value=t.tk;o.textContent=t.n+' ('+t.a+')';og.appendChild(o)});sel.appendChild(og)});
const qs=new URLSearchParams(location.search);sel.value=(qs.get('t')&&D.titres.some(t=>t.tk===qs.get('t')))?qs.get('t'):'BTC-USD';if(qs.get('q'))Q.value=qs.get('q');
const pUsd=t=>{const p=vivant[t.tk]||t.p;return t.d==='USD'?p:t.d==='EUR'?p/ue:null};
function maj(src){const t=D.titres.find(x=>x.tk===sel.value);if(!t)return;const pu=pUsd(t);if(pu==null)return;const pe=pu*ue;
  if(src==='eur')Q.value=+(E.value/pe).toPrecision(8);if(src==='usd')Q.value=+(U.value/pu).toPrecision(8);const q=+Q.value||0;
  if(src!=='eur')E.value=+(q*pe).toFixed(2);if(src!=='usd')U.value=+(q*pu).toFixed(2);const s=t.a.replace('-USD','');
  document.getElementById('res').innerHTML=`<p>${fmt(q,8)} ${s} =</p><span class="gros">${fmtM(q*pu,'USD')}</span><p>or ${fmtM(q*pe,'EUR')} · 1 ${s} = ${fmtM(pu,'USD')}</p><p class="muted"><a href="../stocks/${t.s}.html">${t.n} one-month forecast</a></p>`;
  const u=new URL(location.href);u.searchParams.set('t',t.tk);u.searchParams.set('q',q);history.replaceState(null,'',u);majLiensPartage(`${fmt(q,8)} ${t.n} = ${fmtM(q*pu,'USD')}`);}
Q.oninput=()=>maj('q');E.oninput=()=>maj('eur');U.oninput=()=>maj('usd');sel.onchange=()=>{maj('q');live()};
function live(){const t=D.titres.find(x=>x.tk===sel.value);if(!t||t.m!=='crypto')return;fetch('https://min-api.cryptocompare.com/data/price?fsym='+encodeURIComponent(t.a.replace('-USD',''))+'&tsyms=USD').then(r=>r.json()).then(j=>{if(j&&j.USD>0){vivant[t.tk]=j.USD;document.getElementById('direct').textContent=' · live price for '+t.n;maj('q')}}).catch(()=>{})}
maj('q');live();
</script>""".replace("__D__", _json({**D, "titres": [{k: v for k, v in t.items() if k not in ("t", "c")} for t in D["titres"]]}))
    alt = {"en": chemin, "fr": "outils/convertisseur.html", "x-default": "outils/convertisseur.html"}
    page = anglais._page(base, f"Bitcoin to USD and EUR converter, crypto and stocks | {NOM}",
                         "Convert Bitcoin, Ether, Solana or any stock to dollars and euros, both ways. Free, daily prices, live crypto prices.",
                         chemin, CSS_OUTIL + corps + JS_COMMUN_EN + JS_LIENS_PARTAGE + js, csp, alt)
    out.append((chemin, _avec_jsonld(page, _jsonld_en(base, chemin, "Crypto and stock converter", "Free converter to USD and EUR.", faq))))
    return out
