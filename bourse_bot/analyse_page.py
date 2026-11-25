"""Version 106 : la page « Analyse approfondie » (lancer, suivre, lire le rapport). Le calcul se fait sur GitHub Actions
(bourse_bot/analyse_profonde.py), à la demande, via le serveur Radar Bourse+ : 1 analyse gratuite, illimité pour les abonnés."""
from __future__ import annotations

import json

from . import abonnement, seo

NOM = seo.NOM
_e = seo._e

CSS = """<style>
.ap-form{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end}.ap-form label{flex:1 1 220px}
.ap-form input{width:100%;box-sizing:border-box;padding:11px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit;font-size:16px}
.ap-etapes{list-style:none;padding:0;margin:12px 0}.ap-etapes li{padding:6px 0 6px 28px;position:relative;color:var(--muted)}
.ap-etapes li::before{content:"";position:absolute;left:4px;top:11px;width:12px;height:12px;border-radius:50%;border:2px solid var(--line)}
.ap-etapes li.fait{color:var(--ink)}.ap-etapes li.fait::before{background:var(--up);border-color:var(--up)}
.ap-etapes li.encours{color:var(--ink)}.ap-etapes li.encours::before{border-color:var(--accent);border-top-color:transparent;animation:ap-tourne 1s linear infinite}
@keyframes ap-tourne{to{transform:rotate(360deg)}}@media (prefers-reduced-motion:reduce){.ap-etapes li.encours::before{animation:none}}
.ap-grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px;margin:12px 0}
.ap-carte{border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:var(--surface)}.ap-carte h3{margin:0 0 8px;font-size:17px}
.ap-k{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.ap-k div{background:var(--surface-2);border-radius:9px;padding:7px 8px}
.ap-k b{display:block;font-family:var(--m)}.ap-k span{font-size:12px;color:var(--muted)}
.ap-t{width:100%;border-collapse:collapse;font-size:14.5px}.ap-t th{position:static!important;top:auto!important;bottom:auto!important}.ap-t td,.ap-t th{padding:6px 4px;border-bottom:1px solid var(--line);text-align:left}.ap-t .m{font-family:var(--m);white-space:nowrap}
.ap-svg{width:100%;height:auto;display:block}.ap-svg text{font-size:11px;fill:var(--muted);font-family:var(--m)}
.ap-barres div{display:grid;grid-template-columns:110px 1fr 46px;gap:8px;align-items:center;margin:5px 0;font-size:14px}
.ap-barres i{display:block;height:12px;border-radius:6px;background:var(--accent)}.ap-barres .m{font-family:var(--m);text-align:right}
.ap-synth li{margin:7px 0}
</style>"""

JS = r"""<script>
(function(){
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct=(v,d=1)=>v==null?'–':(v>0?'+':'')+(v*100).toLocaleString('fr-FR',{maximumFractionDigits:d})+' %';
const px=(v,dev)=>v==null?'–':v.toLocaleString('fr-FR',{maximumFractionDigits:Math.abs(v)>=1?2:6})+' '+(dev||'');
let app='';try{app=localStorage.getItem('rb-appareil');if(!app){app=[...crypto.getRandomValues(new Uint8Array(12))].map(b=>b.toString(16).padStart(2,'0')).join('');localStorage.setItem('rb-appareil',app)}}catch(e){}
const ETAPES=["Demande envoyée au serveur","Démarrage de la machine de calcul (1 à 2 min)","Téléchargement de tout l'historique du titre","Fourchettes testées sur le passé du titre",
 "3 000 simulations de l'avenir (Monte-Carlo)","Modèle de direction testé année par année","Pires chutes, lien avec le marché, saisonnalité","Rédaction du rapport"];
function suivre(debut){const ul=$('#ap-etapes');ul.hidden=false;const t=Math.floor((Date.now()-debut)/1000);
 const k=Math.min(ETAPES.length-1,t<5?0:t<100?1:2+Math.floor((t-100)/25));ul.innerHTML=ETAPES.map((e,i)=>`<li class="${i<k?'fait':i===k?'encours':''}">${e}</li>`).join('')}
function mes(){try{return JSON.parse(localStorage.getItem('rb-analyses')||'[]')}catch(e){return[]}}
function garder(a){const l=mes().filter(x=>x.id!==a.id);l.unshift(a);try{localStorage.setItem('rb-analyses',JSON.stringify(l.slice(0,20)))}catch(e){}liste()}
function liste(){const l=mes();$('#ap-mes').innerHTML=l.length?'<h2>Mes analyses</h2><ul>'+l.map(a=>`<li><a href="#${esc(a.id)}">${esc(a.ticker)}</a> <span class="muted">· ${new Date(a.debut).toLocaleDateString('fr-FR')}</span></li>`).join('')+'</ul>':''}
async function etat(){const z=$('#ap-quota');if(!RBP.api){z.innerHTML='<b>Bientôt disponible.</b> L’analyse approfondie ouvrira avec Radar Bourse+.';$('#ap-go').disabled=true;return}
 try{const q=await RBP.appel('/quota',{code:RBP.code(),appareil:app});
  if(q.active===false){z.innerHTML='<b>Bientôt disponible.</b>';$('#ap-go').disabled=true;return}
  if(q.mode_gratuit){z.innerHTML=q.restant>0?'Gratuit et sans compte : il te reste <b>'+q.restant+' analyse'+(q.restant>1?'s':'')+'</b> aujourd\u2019hui.':'Tu as utilisé tes analyses du jour : reviens demain !';$('#ap-go').disabled=!(q.restant>0);return}
  z.innerHTML=q.vip?'✅ Abonné Radar Bourse+ : analyses illimitées (10 par jour).':q.gratuit_restant?'Tu as <b>1 analyse gratuite</b>. Ensuite, elles sont illimitées avec <a href="radar-bourse-plus.html">Radar Bourse+</a> (1 mois offert).':'Ton analyse gratuite est utilisée. <a href="radar-bourse-plus.html">Radar Bourse+</a> : illimité, 1 mois offert.'}catch(e){z.textContent='Serveur injoignable pour le moment.'}}
async function attendre(id){const box=$('#ap-res');box.innerHTML='';let n=0;
 while(n++<200){let r;try{r=await fetch(RBP.api+'/resultat?id='+id).then(x=>x.json())}catch(e){r={}}
  if(r.etat==='fini'){$('#ap-etapes').hidden=true;rapport(r.resultat);return}
  if(r.etat==='echec'||r.ok===false&&n>3){$('#ap-etapes').hidden=true;box.innerHTML='<p>'+esc(r.erreur||'Analyse introuvable.')+'</p>';return}
  if(r.debut)suivre(r.debut);await new Promise(o=>setTimeout(o,8000))}}
async function lancer(){const tk=$('#ap-tk').value.trim().toUpperCase().split(' ')[0];if(!tk)return;const b=$('#ap-go');b.disabled=true;$('#ap-msg').textContent='';
 try{const r=await RBP.appel('/analyse',{ticker:tk,code:RBP.code(),appareil:app});
  if(!r.ok){$('#ap-msg').innerHTML=esc(r.erreur||'Impossible de lancer l’analyse.');b.disabled=false;return}
  garder({id:r.id,ticker:tk,debut:Date.now()});location.hash=r.id;suivre(Date.now());attendre(r.id);etat()}catch(e){$('#ap-msg').textContent='Serveur injoignable.';b.disabled=false}}
function ligne(xs,ys,W,H,c,lo,hi){const X=i=>8+(W-60)*i/Math.max(1,xs-1),Y=v=>8+(H-24)*(1-(v-lo)/(hi-lo));return ys.map((v,i)=>v==null?'':(i?'L':'M')+X(i).toFixed(1)+','+Y(v).toFixed(1)).join('')}
function eventail(R){const s=R.serie,ev=R.monte_carlo&&R.monte_carlo.eventail;if(!s||!ev)return'';const W=640,H=240,hist=s.c.slice(-126),pts=Object.keys(ev).map(Number).sort((a,b)=>a-b),fin=pts.at(-1);
 const tot=hist.length+fin,all=hist.concat(...pts.map(p=>[ev[p][5],ev[p][95]])).filter(v=>v!=null),lo=Math.min(...all)*.98,hi=Math.max(...all)*1.02;
 const X=i=>8+(W-70)*i/(tot-1),Y=v=>8+(H-28)*(1-(v-lo)/(hi-lo)),x0=hist.length-1;
 const bande=(a,b)=>'M'+X(x0)+','+Y(hist.at(-1))+pts.map(p=>' L'+X(x0+p).toFixed(1)+','+Y(ev[p][a]).toFixed(1)).join('')+pts.slice().reverse().map(p=>' L'+X(x0+p).toFixed(1)+','+Y(ev[p][b]).toFixed(1)).join('')+' Z';
 let g=`<svg class="ap-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Cours des 6 derniers mois et éventail des simulations à 3 mois">`;
 [lo,(lo+hi)/2,hi].forEach(v=>g+=`<text x="${W-60}" y="${Y(v)+4}">${px(v,'')}</text>`);
 g+=`<path d="${bande(5,95)}" fill="var(--accent)" opacity=".15"/><path d="${bande(25,75)}" fill="var(--accent)" opacity=".3"/>`;
 g+=`<path d="${hist.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+','+Y(v).toFixed(1)).join('')}" fill="none" stroke="var(--ink)" stroke-width="2"/>`;
 g+=`<path d="M${X(x0)},${Y(hist.at(-1))}${pts.map(p=>' L'+X(x0+p).toFixed(1)+','+Y(ev[p][50]).toFixed(1)).join('')}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-dasharray="5 4"/>`;
 g+=`<line x1="${X(x0)}" x2="${X(x0)}" y1="8" y2="${H-20}" stroke="var(--muted)" stroke-dasharray="3 4"/><text x="${X(x0)+4}" y="${H-6}">aujourd'hui</text><text x="${X(tot-1)-40}" y="${H-6}">+3 mois</text></svg>`;
 return g+'<p class="muted" style="font-size:13px">Clair : 90 % des simulations. Foncé : la moitié du milieu. Pointillés : la simulation du milieu. Ce n’est pas une prévision : c’est l’éventail de ce qui arrive si le titre se comporte comme dans son passé.</p>'}
function barres(l,max){return '<div class="ap-barres">'+l.map(x=>`<div><span>${esc(x[0])}</span><i style="width:${Math.max(2,x[1]/max*100)}%;background:${x[2]||'var(--accent)'}"></i><span class="m">${x[3]}</span></div>`).join('')+'</div>'}
function rapport(R){const box=$('#ap-res');if(!R||!R.ok){box.innerHTML='<p>'+esc((R&&R.erreur)||'Analyse impossible.')+'</p>';return}
 const S=R.situation||{},dev=R.devise,F=R.fourchettes||{},MC=R.monte_carlo||{},D=R.direction||{},RI=R.risques||{},M=R.marche||{},Z=R.saisonnalite||{};
 let h=`<h2>${esc(R.nom)} (${esc(R.ticker)}) : le rapport complet</h2><p class="muted">Calculé le ${new Date(R.genere_le).toLocaleString('fr-FR')} sur ${R.seances} séances depuis le ${esc(R.debut)} · source : ${esc(R.source)} · ${esc(R.avertissement)}</p>`;
 h+=`<div class="ap-carte"><h3>En résumé</h3><ul class="ap-synth">${(R.synthese||[]).map(x=>'<li>'+esc(x)+'</li>').join('')}</ul></div>`;
 h+=`<div class="ap-grille"><div class="ap-carte"><h3>La situation</h3><div class="ap-k"><div><b>${px(S.prix,dev)}</b><span>cours au ${esc(S.date)}</span></div><div><b>${pct((S.perf||{})['1 mois'])}</b><span>sur 1 mois</span></div><div><b>${pct((S.perf||{})['1 an'])}</b><span>sur 1 an</span></div>`
  +`<div><b>${S.au_dessus_200==null?'–':S.au_dessus_200?'Haussière':'Baissière'}</b><span>tendance de fond</span></div><div><b>${Math.round((S.vol_actuelle||0)*100)} %</b><span>agitation / an</span></div><div><b>${pct(S.recul_plus_haut_1an)}</b><span>depuis le plus haut 1 an</span></div></div></div>`;
 h+=`<div class="ap-carte"><h3>Les fourchettes probables</h3><table class="ap-t"><thead><tr><th>Horizon</th><th>8 fois sur 10 (en principe)</th><th>Réussite passée sur ce titre</th></tr></thead><tbody>${Object.entries(F).map(([k,v])=>`<tr><td>1 ${esc(k)}</td><td class="m">${px(v.bas80,'')} – ${px(v.haut80,dev)}</td><td class="m">${v.reussite_passee==null?'–':Math.round(v.reussite_passee*100)+' %'}</td></tr>`).join('')}</tbody></table></div></div>`;
 h+=`<div class="ap-carte"><h3>3 000 simulations des 3 prochains mois</h3>${eventail(R)}</div>`;
 const sc=(MC.scenarios||{})['21'];if(sc){const cs=['var(--down)','var(--down)','var(--muted)','var(--up)','var(--up)'];h+=`<div class="ap-grille"><div class="ap-carte"><h3>Scénarios à 1 mois</h3>${barres(sc.map((x,i)=>[x.nom,x.proba,cs[i],Math.round(x.proba*100)+' %']),Math.max(...sc.map(x=>x.proba)))}<p class="muted" style="font-size:13px">Forte baisse : plus de 10 % ; stable : entre −3 et +3 %.</p></div>`}
 else h+='<div class="ap-grille">';
 h+=`<div class="ap-carte"><h3>Le sens à un mois : le test honnête</h3>`+(D.ok?barres(D.annees.map(a=>[a.annee+(a.ia>a.naif?' ✓':''),a.ia,a.ia>a.naif?'var(--up)':'var(--muted)',Math.round(a.ia*100)+' %']),1)+`<p>${esc(D.verdict)}</p>`+(D.fiable?`<p><b>Aujourd'hui : ${Math.round(D.proba_hausse*100)} chances sur 100 de hausse à 1 mois.</b></p>`:''):`<p>${esc(D.raison||'')}</p>`)+`<p class="muted" style="font-size:13px">Barres : bonnes réponses du modèle chaque année jamais vue. ✓ = mieux que la réponse naïve.</p></div></div>`;
 h+=`<div class="ap-grille"><div class="ap-carte"><h3>Les pires chutes de son histoire</h3><table class="ap-t"><tbody>${(RI.pires_chutes||[]).map(c=>`<tr><td class="m down">${pct(c.chute,0)}</td><td>${esc(c.debut)} → ${esc(c.creux)}</td><td>${c.jours_recuperation!=null?'rattrapée en '+c.jours_recuperation+' j':'pas encore rattrapée'}</td></tr>`).join('')}</tbody></table>`
  +(RI.chute10_mois_historique!=null?`<p>Dans son passé, ce titre a perdu plus de 10 % en moins d’un mois <b>${Math.round(RI.chute10_mois_historique*100)} fois sur 100</b>`+(MC.chute10_mois!=null?` ; les simulations donnent <b>${Math.round(MC.chute10_mois*100)} %</b> pour le mois qui vient.`:'.')+'</p>':'')+'</div>';
 h+=`<div class="ap-carte"><h3>Lien avec le marché</h3>`+(M.beta!=null?`<p>Par rapport à ${esc(M.reference)} : <b>bêta ${String(M.beta).replace('.',',')}</b>, corrélation ${String(M.correlation).replace('.',',')}.</p><p class="muted">Bêta au-dessus de 1 : bouge plus fort que le marché. Sous 1 : plus calme.</p>`:'<p class="muted">Non disponible.</p>')+'</div></div>';
 if(Z.par_mois){const mo=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];h+=`<div class="ap-carte"><h3>Saisonnalité : part des années où chaque mois a monté</h3>${barres(Object.entries(Z.par_mois).map(([k,v])=>[mo[k-1]+(+k===Z.mois_prochain?' ←':''),v.hausse,v.hausse>=.5?'var(--up)':'var(--down)',Math.round(v.hausse*100)+' %']),1)}<p class="muted" style="font-size:13px">← le mois prochain. Le passé ne se répète pas forcément.</p></div>`}
 const fv=(R.fondamentaux||{}).valeurs;if(fv){const L={marketCap:'Capitalisation',trailingPE:'PER',returnOnEquity:'ROE',debtToEquity:'Dette / fonds propres',profitMargins:'Marge nette',fondsPropres:'Fonds propres',priceToBook:'Cours / fonds propres'};
  h+=`<div class="ap-carte"><h3>L’entreprise en chiffres</h3><table class="ap-t">${Object.entries(L).filter(([k])=>fv[k]!=null).map(([k,l])=>`<tr><td>${l}</td><td class="m">${['returnOnEquity','profitMargins'].includes(k)?pct(fv[k]):k==='debtToEquity'?Math.round(fv[k])+' %':Math.abs(fv[k])>=1e6?(fv[k]/1e9).toLocaleString('fr-FR',{maximumFractionDigits:1})+' Md':fv[k].toLocaleString('fr-FR',{maximumFractionDigits:2})}</td></tr>`).join('')}</table></div>`}
 h+=`<p><a href="titres/${esc(String(R.ticker).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''))}.html">Fiche du titre</a> · <a href="outils/simulateur-stop-loss.html">Tester un stop-loss</a> · <a href="lecons/stop-loss.html">Comprendre les risques</a></p>`;
 box.innerHTML=h;box.scrollIntoView({behavior:'smooth'})}
$('#ap-go').onclick=lancer;$('#ap-tk').addEventListener('keydown',e=>{if(e.key==='Enter')lancer()});
const q=new URLSearchParams(location.search).get('t');if(q)$('#ap-tk').value=q;
liste();etat();const h=location.hash.slice(1);if(/^[a-z0-9]{12,40}$/.test(h)&&RBP.api){$('#ap-etapes').hidden=false;attendre(h)}
window.addEventListener('hashchange',()=>{const i=location.hash.slice(1);if(/^[a-z0-9]{12,40}$/.test(i))attendre(i)});
window.APRapport=rapport;
})();
</script>"""


def page(base, payload, csp):
    chemin = "analyse-approfondie.html"
    opts = "".join(f"<option value='{_e(t['ticker'])}'>{_e(t.get('nom') or t['ticker'])}</option>"
                   for t in payload.get("titres", []) if t.get("marche") != "tendances")
    corps = (CSS + "<h1>Analyse approfondie d'une action, d'une crypto ou de l'or</h1>"
             "<p>Choisis un titre : l'IA reprend <b>tout son historique</b> et l'analyse à fond pendant quelques minutes, sur un serveur (pas besoin de "
             "laisser ton ordinateur allumé). Fourchettes testées sur son propre passé, 3 000 simulations, modèle de direction jugé année par année, "
             "pires chutes, lien avec le marché, saisonnalité et chiffres de l'entreprise. Chaque résultat dit à quel point il est fiable.</p>"
             "<div class='ap-carte'><div class='ap-form'><label for='ap-tk'><b>Titre</b> (nom ou symbole : MC.PA, AAPL, BTC-USD, GC=F…)"
             "<input id='ap-tk' list='ap-liste' autocomplete='off' placeholder='LVMH, Apple, Bitcoin, l’or…'></label>"
             "<button type='button' class='btn' id='ap-go' style='padding:11px 18px'>Lancer l'analyse approfondie</button></div>"
             f"<datalist id='ap-liste'>{opts}</datalist><p id='ap-quota' class='muted' style='margin:10px 0 0'></p><p id='ap-msg' role='alert'></p>"
             "<ul class='ap-etapes' id='ap-etapes' hidden aria-live='polite'></ul></div>"
             "<div id='ap-res' aria-live='polite'></div><div id='ap-mes'></div>"
             "<p class='muted'>Analyse statistique automatique et éducative : ce n'est pas un conseil en investissement. Tu peux fermer la page : "
             "le rapport reste disponible 30 jours dans « Mes analyses » sur cet appareil.</p>"
             + abonnement._js() + JS)
    return chemin, seo._page(base, f"Analyse approfondie d'une action par l'IA, à la demande | {NOM}",
                             "Choisis une action, une crypto ou l'or : l'IA analyse tout son historique (fourchettes testées, 3 000 simulations, "
                             "modèle jugé année par année, risques). Gratuit, sans compte.",
                             chemin, corps, csp=abonnement._csp(csp))
