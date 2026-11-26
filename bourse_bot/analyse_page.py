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
.ap-verdict{border-left:5px solid var(--accent)}.ap-verdict p{margin:0;font-size:18px;line-height:1.45}
.ap-alerte{border-color:#d9a400;background:color-mix(in srgb,#d9a400 10%,var(--surface))}
.ap-plus{margin:14px 0}.ap-plus>summary{cursor:pointer;font-weight:700;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--surface-2)}
.ap-plus[open]>summary{margin-bottom:6px}
</style>"""

NAV = r"""<script>
/* Version 112 : analyse approfondie DANS LE NAVIGATEUR (sans serveur).
   - 3 ans de cours (rendements quotidiens du site) au lieu d'un an et demi ;
   - fourchettes « 8 fois sur 10 » avec un plancher d'agitation (0,8 × l'agitation habituelle) et des quantiles choisis sur la
     période la plus ancienne puis vérifiés sur la plus récente (test sur 471 titres réels, novembre 2026) ;
   - événements à venir (résultats), vraies prévisions vérifiées du titre, comparaison avec des titres proches ;
   - aussi les ~2 000 fiches simples (2 ans de cours, avis quotidien de l'IA quand il existe). */
(function(){
const L=__LISTE__,M=__MODELE__;window.APNav={liste:L};
const Q={semaine:[5,.10],mois:[21,.09],trimestre:[63,.06]},PLANCHER=.8;
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length,std=a=>{const m=mean(a);return Math.sqrt(a.reduce((x,y)=>x+(y-m)**2,0)/(a.length-1||1))};
const qs=(b,q)=>{const i=(b.length-1)*q,lo=Math.floor(i),hi=Math.ceil(i);return b[lo]+(b[hi]-b[lo])*(i-lo)};
const quant=(a,q)=>qs(a.slice().sort((x,y)=>x-y),q);
function rng(seed){let t=seed>>>0;return()=>{t+=0x6D2B79F5;let r=Math.imul(t^t>>>15,1|t);r^=r+Math.imul(r^r>>>7,61|r);return((r^r>>>14)>>>0)/4294967296}}
const hash=s=>{let h=2166136261;for(const ch of s){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0};
const iso=d=>d.toISOString().slice(0,10);
let ETENDU=null;
async function etendu(){if(ETENDU)return ETENDU;try{ETENDU=await fetch('recherche-etendue.json').then(r=>r.json())}catch(e){ETENDU=[]}return ETENDU}
window.APEtendu=etendu;
// 3 ans : les rendements quotidiens (log) du site, raccordés au premier cours exact de la série ; dates d'avant reconstituées (≈)
function longue(d,crypto){const S=d.serie||{};const t=[],c=[];(S.c||[]).forEach((v,i)=>{if(v>0){t.push(S.t[i]);c.push(v)}});
  const r=d.rendements||[];const pre=r.length+1-c.length;if(pre<=20||!c.length)return {t,c,approx:0};
  const cp=new Array(pre);let v=c[0];for(let k=pre-1;k>=0;k--){v=v*Math.exp(-r[k]);cp[k]=v}
  const tp=new Array(pre);let dt=new Date(t[0]+'T12:00:00Z');for(let k=pre-1;k>=0;k--){do{dt=new Date(dt.getTime()-864e5)}while(!crypto&&(dt.getUTCDay()===0||dt.getUTCDay()===6));tp[k]=iso(dt)}
  if(!cp.every(x=>x>0&&isFinite(x)))return {t,c,approx:0};
  return {t:tp.concat(t),c:cp.concat(c),approx:pre}}
async function charger(tk){const it=L.find(x=>x[0]===tk);
  if(it){const r=await fetch('donnees/'+it[2]+'.json');if(!r.ok)throw new Error('cours');const d=await r.json();const s=longue(d,/-USD$/.test(tk));return {it,d,...s,simple:false}}
  const E=await etendu();const e=E.find(x=>x[1]===tk);if(!e)return null;
  const r=await fetch('donnees-e/'+e[2]+'.json');if(!r.ok)throw new Error('cours');const d=await r.json();
  const t=[];let dt=new Date(d.t0+'T12:00:00Z');d.dt.forEach((g,i)=>{if(i)dt=new Date(dt.getTime()+g*864e5);t.push(iso(dt))});
  const ia=d.ia||{};const sens=ia.p==null?0:ia.p>=.5?1:-1;
  return {it:[tk,d.nom||e[0],e[2],'',sens,ia.p==null?null:Math.round((sens>0?ia.p:1-ia.p)*100),ia.c||'faible','',d.dev||'',d.sec||'',[0,0,0,0]],d:{fondamentaux:null},t,c:d.c,approx:0,simple:true,pays:e[3],ia_ok:ia.p!=null}}
window.APCharger=charger;
function ewma(lr){const out=[];let v=lr.slice(0,20).reduce((x,y)=>x+y*y,0)/Math.max(1,Math.min(20,lr.length));for(const r of lr){v=0.94*v+0.06*r*r;out.push(Math.sqrt(v))}return out}
// les fourchettes testées : renvoie aussi la réussite passée sur ce titre (walk-forward : chaque test n'utilise que le passé)
function fourchettes(c){const n=c.length,lr=c.slice(1).map((v,i)=>Math.log(v/c[i])),sig=ewma(lr);const cs=[0],c2=[0];lr.forEach(x=>{cs.push(cs.at(-1)+x);c2.push(c2.at(-1)+x*x)});
  const sd=k=>{const m=cs[k]/k;return Math.sqrt(Math.max(0,c2[k]/k-m*m))},se=i=>Math.max(sig[i-1],PLANCHER*sd(i));const F={};
  for(const [nom,[h,q]] of Object.entries(Q)){const z=[];for(let i=60;i+h<n;i++)z.push([i,Math.log(c[i+h]/c[i])/(se(i)*Math.sqrt(h))]);
    if(z.length<80)continue;let dedans=0,nb=0;for(let k=80;k<z.length;k+=3){const i=z[k][0];const past=z.filter(x=>x[0]+h<=i).map(x=>x[1]).sort((a,b)=>a-b);if(past.length<60)continue;nb++;if(z[k][1]>=qs(past,q)&&z[k][1]<=qs(past,1-q))dedans++}
    const all=z.map(x=>x[1]).sort((a,b)=>a-b),sn=se(n-1)*Math.sqrt(h),p0=c[n-1];
    F[nom]={seances:h,bas80:p0*Math.exp(qs(all,q)*sn),haut80:p0*Math.exp(qs(all,1-q)*sn),median:p0*Math.exp(qs(all,.5)*sn),reussite_passee:nb?dedans/nb:null,tests:nb}}
  return F}
window.APFourchettes=fourchettes;
function resume(c){const n=c.length,lr=c.slice(1).map((v,i)=>Math.log(v/c[i])),an=c.slice(-252);let pic=an[0],dd=0;for(const v of an){pic=Math.max(pic,v);dd=Math.min(dd,v/pic-1)}
  const s200=n>=200?mean(c.slice(-200)):null;return {perf:n>252?c[n-1]/c[n-253]-1:null,vol:std(lr.slice(-20))*Math.sqrt(252),dd,tend:s200==null?null:c[n-1]>s200}}
async function etape(n){if(window.APEtape)window.APEtape(n);await new Promise(r=>setTimeout(r,200))}
window.analyserNav=async function(tk){
  await etape(1);const X=await charger(tk);if(!X)return {ok:false,erreur:"Ce titre n'est pas encore disponible : choisis-le dans la liste."};
  const {it,d,t,c,approx,simple}=X;const n=c.length;if(n<150)return {ok:false,erreur:"Historique trop court pour une analyse sérieuse."};
  await etape(2);
  const lr=c.slice(1).map((v,i)=>Math.log(v/c[i]));const sig=ewma(lr);
  // 1. situation
  const sma=k=>n>=k?mean(c.slice(-k)):null,v20=std(lr.slice(-20))*Math.sqrt(252),vh=std(lr)*Math.sqrt(252);
  const vols=[];for(let i=20;i<=lr.length;i++)vols.push(std(lr.slice(i-20,i))*Math.sqrt(252));
  const perf=k=>n>k?c[n-1]/c[n-1-k]-1:null;
  const S={prix:c[n-1],date:t[n-1],au_dessus_200:sma(200)!=null?c[n-1]>sma(200):(sma(100)!=null?c[n-1]>sma(100):null),au_dessus_50:c[n-1]>sma(50),perf:{"1 semaine":perf(5),"1 mois":perf(21),"3 mois":perf(63),"1 an":perf(252)},
    vol_actuelle:v20,vol_habituelle:vh,percentile_vol:vols.filter(v=>v<v20).length/vols.length,recul_plus_haut_1an:c[n-1]/Math.max(...c.slice(-252))-1};
  await etape(3);
  // 2. fourchettes
  const F=fourchettes(c);
  await etape(4);
  // 3. Monte-Carlo par blocs de 10 vrais jours (3 ans de blocs)
  const m0=mean(lr),ratio=Math.min(2.5,Math.max(.5,sig[sig.length-1]/(std(lr)||1))),rr=lr.map(x=>(x-m0)*ratio+m0),R=rng(hash(tk)),J=63,B=10,N=3000;
  const pts=[5,10,21,42,63],fins={},min21=[];pts.forEach(p=>fins[p]=[]);
  for(let k=0;k<N;k++){let cum=0,mn=1,j=0;while(j<J){const s0=Math.floor(R()*(rr.length-B));for(let b=0;b<B&&j<J;b++,j++){cum+=rr[s0+b];const v=Math.exp(cum);if(j<21&&v<mn)mn=v;if(fins[j+1])fins[j+1].push(v)}}min21.push(mn)}
  const p0=c[n-1],ev={};pts.forEach(p=>{ev[p]={};[5,25,50,75,95].forEach(q=>ev[p][q]=p0*quant(fins[p],q/100))});
  const SC=[["Forte baisse",-1,-.10],["Baisse",-.10,-.03],["Stable",-.03,.03],["Hausse",.03,.10],["Forte hausse",.10,9]],sc={};
  [21,63].forEach(h=>sc[h]=SC.map(([nom,a,b])=>({nom,proba:fins[h].filter(v=>v-1>a&&v-1<=b).length/N})));
  const MC={chemins:N,eventail:ev,scenarios:sc,chute10_mois:min21.filter(v=>v<.9).length/N};
  await etape(5);
  // 4. avis de l'IA du radar
  const D=simple?(X.ia_ok?{ia_radar:true,quotidien:true,sens:it[4],chances:it[5],confiance:it[6],fiab:M.fiab,naif:M.naif}:{aucun:true}):{ia_radar:true,sens:it[4],chances:it[5],confiance:it[6],fiab:M.fiab,naif:M.naif};
  const B4=it[10]||[0,0,0,0],BILAN={direction:B4[0]>=5?{nb:B4[0],justes:B4[1]}:null,fourchette:B4[2]>=5?{nb:B4[2],tenues:B4[3]}:null};
  // 5. événements à venir
  let EV=null;const rl=(d.fondamentaux||{}).resultats_le;if(rl){const j=Math.round((new Date(rl+'T12:00:00Z')-new Date(iso(new Date())+'T12:00:00Z'))/864e5);if(j>=0&&j<=45)EV={resultats_le:rl,jours:j,avant_echeance_mois:j<=30}}
  await etape(6);
  // 6. risques : pires chutes de la période
  const pires=[],pris=new Set();for(let r=0;r<3;r++){let best=0,ib=-1,ih=-1,hm=0,ihm=-1;
    for(let i=0;i<n;i++){if(pris.has(i)){hm=0;ihm=-1;continue}if(c[i]>hm){hm=c[i];ihm=i}const dd=c[i]/hm-1;if(dd<best){best=dd;ib=i;ih=ihm}}
    if(best>-.05)break;let fin=null;for(let i=ib;i<n;i++)if(c[i]>=c[ih]){fin=i;break}
    const dte=i=>(i<approx?'≈ ':'')+t[i];
    pires.push({debut:dte(ih),creux:dte(ib),chute:best,recupere:fin!=null?t[fin]:null,jours_recuperation:fin!=null?Math.round((fin-ib)*(/-USD$/.test(tk)?1:365/252)):null});
    for(let i=ih;i<=(fin??n-1);i++)pris.add(i)}
  let c10=0,n10=0;for(let i=0;i+20<n;i++){n10++;let mn=Infinity;for(let k=i+1;k<=i+20;k++)if(c[k]<mn)mn=c[k];if(mn/c[i]-1<-.10)c10++}
  const RI={pires_chutes:pires,chute10_mois_historique:n10?c10/n10:null};
  // 7. lien avec le marché
  let MA={};if(it[3]&&it[3]!==it[2]){try{const b=await fetch('donnees/'+it[3]+'.json').then(r=>r.json());const bs=longue(b,/-usd$/.test(it[3])),pos={};bs.t.forEach((d0,i)=>{if(i>=bs.approx)pos[d0]=i});const x=[],y=[];
    for(let i=Math.max(1,approx);i<n;i++){const a=pos[t[i]],a0=pos[t[i-1]];if(a!=null&&a0!=null&&a===a0+1){x.push(Math.log(c[i]/c[i-1]));y.push(Math.log(bs.c[a]/bs.c[a0]))}}
    if(x.length>100){const xs=x.slice(-252),ys=y.slice(-252),mx=mean(xs),my=mean(ys);let cv=0,vx=0,vy=0;xs.forEach((v,i)=>{cv+=(v-mx)*(ys[i]-my);vx+=(v-mx)**2;vy+=(ys[i]-my)**2});
      MA={reference:it[7],beta:Math.round(cv/vy*100)/100,correlation:Math.round(cv/Math.sqrt(vx*vy)*100)/100}}}catch(e){}}
  // 8. titres proches (même secteur, même type) : performance, agitation, pire chute, tendance
  let PR=[];try{let cands=[];const sec=it[9];
    if(sec==='crypto')cands=['BTC-USD','ETH-USD','SOL-USD','BNB-USD'].filter(x=>x!==tk);
    else if(sec)cands=L.filter(x=>x[9]===sec&&x[0]!==tk).sort((a,b)=>(b[2].split('-').pop()===it[2].split('-').pop())-(a[2].split('-').pop()===it[2].split('-').pop())).map(x=>x[0]);
    for(const p of cands.slice(0,3)){const ip=L.find(x=>x[0]===p);if(!ip)continue;const dp=await fetch('donnees/'+ip[2]+'.json').then(r=>r.json());const sp=longue(dp,/-USD$/.test(p));if(sp.c.length<260)continue;PR.push({ticker:p,nom:ip[1],slug:ip[2],...resume(sp.c)})}
    if(PR.length)PR.unshift({ticker:tk,nom:it[1],soi:true,...resume(c)})}catch(e){PR=[]}
  // 9. saisonnalité
  let Z={};const sa=d.saison;const prochain=new Date().getMonth()%12+2>12?1:new Date().getMonth()+2;
  if(sa&&sa.m){const pm={};for(let k=0;k<12;k++){const v=sa.m.map(a=>a[k]).filter(x=>x!=null);if(v.length>=2)pm[k+1]={hausse:v.filter(x=>x>0).length/v.length,moyenne:mean(v),annees:v.length}}Z={par_mois:pm,mois_prochain:prochain}}
  else{const fm={};for(let i=approx;i<n;i++){const k=t[i].slice(0,7);if(!fm[k])fm[k]=[c[i],c[i]];fm[k][1]=c[i]}const ks=Object.keys(fm).sort(),pm={};
    for(let j=1;j<ks.length-1;j++){const m=+ks[j].slice(5,7);const v=fm[ks[j]][1]/fm[ks[j-1]][1]-1;(pm[m]=pm[m]||[]).push(v)}
    const out={};for(const m in pm)if(pm[m].length>=2)out[m]={hausse:pm[m].filter(x=>x>0).length/pm[m].length,moyenne:mean(pm[m]),annees:pm[m].length};if(Object.keys(out).length)Z={par_mois:out,mois_prochain:prochain}}
  await etape(7);
  const fx=v=>v==null?'–':v.toLocaleString('fr-FR',{maximumFractionDigits:Math.abs(v)>=1?2:6}),syn=[];
  const tend=S.au_dessus_200==null?'indéterminée':S.au_dessus_200&&S.au_dessus_50?'haussière':!S.au_dessus_200&&!S.au_dessus_50?'baissière':'hésitante';
  const agit=S.percentile_vol>.7?'plus agité que d’habitude':S.percentile_vol<.3?'plus calme que d’habitude':'agité comme d’habitude';
  const verdict=`${it[1]} : tendance ${tend}, ${agit}`+(F.mois?`, fourchette probable à un mois de ${fx(F.mois.bas80)} à ${fx(F.mois.haut80)} ${it[8]||''}`.trimEnd():'')+'.'
    +(D.ia_radar?` L’IA le voit ${D.sens>0?'plutôt à la hausse':'plutôt à la baisse'} (${D.chances} chances sur 100, confiance ${D.confiance}).`:'')
    +(EV?` Attention : résultats ${EV.jours===0?'aujourd’hui':EV.jours===1?'demain':'dans '+EV.jours+' jours'}.`:'');
  syn.push(`Tendance de fond ${tend}. Agitation actuelle ${S.percentile_vol>.7?'élevée':S.percentile_vol<.3?'faible':'normale'} pour ce titre (${Math.round(v20*100)} % par an, habituellement ${Math.round(vh*100)} %).`);
  if(F.mois)syn.push(`Dans un mois, fourchette probable : ${fx(F.mois.bas80)} à ${fx(F.mois.haut80)}`+(F.mois.reussite_passee!=null?` ; sur ce titre, cette méthode a vu juste ${Math.round(F.mois.reussite_passee*100)} fois sur 100 dans le passé.`:'.'));
  if(EV)syn.push(`Publication des résultats le ${EV.resultats_le.split('-').reverse().join('/')} : ce jour-là, le cours peut sauter plus loin que la fourchette.`);
  const top=sc[21].reduce((a,b)=>b.proba>a.proba?b:a);syn.push(`Scénario le plus fréquent dans les simulations à un mois : « ${top.nom} » (${Math.round(top.proba*100)} %).`);
  if(D.ia_radar)syn.push(`L'IA du radar le voit ${D.sens>0?'plutôt à la hausse':'plutôt à la baisse'} (${D.chances} chances sur 100, confiance ${D.confiance}).`);
  if(pires[0])syn.push(`Pire chute sur 3 ans : ${Math.round(pires[0].chute*100)} % (du ${pires[0].debut} au ${pires[0].creux})`+(pires[0].jours_recuperation!=null?`, rattrapée en ${pires[0].jours_recuperation} jours environ.`:', pas encore rattrapée.'));
  if(MA.beta!=null)syn.push(`Lien avec ${MA.reference} : bêta ${String(MA.beta).replace('.',',')}.`);
  if(PR.length>1){const me=PR[0],o=PR.slice(1);const plus=o.filter(p=>p.vol<me.vol).length;syn.push(`Face à ${o.map(p=>p.nom).join(', ')} : ${plus===o.length?'le plus agité':plus===0?'le plus calme':'agitation dans la moyenne'} du groupe.`)}
  return {ok:true,ticker:tk,slug:it[2],nom:it[1],devise:it[8],genere_le:new Date().toISOString(),source:simple?'cours publics (2 ans, mis à jour chaque jour)':'cours du radar (3 ans, mis à jour chaque heure)',seances:n,debut:(approx?'≈ ':'')+t[0],
    verdict,situation:S,fourchettes:F,monte_carlo:MC,direction:D,bilan:BILAN,evenement:EV,risques:RI,marche:MA,pairs:PR,saisonnalite:Z,fondamentaux:d.fondamentaux,synthese:syn,serie:{t,c},
    simple,periode_courte:true,avertissement:'Analyse statistique calculée dans ton navigateur, éducative, pas un conseil en investissement.'};
};
})();
</script>"""

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
const NAVE=["Préparation","Lecture de 3 ans de cours","Situation et agitation","Fourchettes testées sur le passé du titre","3 000 simulations des 3 prochains mois","Avis de l’IA, vraies prévisions vérifiées, événements à venir","Pires chutes, marché, titres proches, saisonnalité","Rédaction du rapport"];
window.APEtape=k=>{const ul=$('#ap-etapes');ul.hidden=false;ul.innerHTML=NAVE.map((e,i)=>`<li class="${i<k?'fait':i===k?'encours':''}">${e}</li>`).join('')};
async function trouver(v){const L=(window.APNav||{}).liste||[];const x=v.trim().toLowerCase();if(!x)return null;
 const f=(A,tk,nm)=>A.find(i=>tk(i).toLowerCase()===x)||A.find(i=>nm(i).toLowerCase()===x)||A.find(i=>nm(i).toLowerCase().startsWith(x))||A.find(i=>nm(i).toLowerCase().includes(x)||tk(i).toLowerCase().startsWith(x));
 const a=f(L,i=>i[0],i=>i[1]);if(a)return a[0];const E=window.APEtendu?await window.APEtendu():[];const b=f(E,i=>i[1],i=>i[0]);return b?b[1]:null}
async function lancerNav(){const tk=await trouver($('#ap-tk').value);const b=$('#ap-go');$('#ap-msg').textContent='';
 if(!tk){$('#ap-msg').textContent='Titre introuvable : tape son nom ou son symbole (LVMH, AAPL, BTC-USD…).';return}
 b.disabled=true;$('#ap-res').innerHTML='';window.APEtape(1);
 try{const R=await window.analyserNav(tk);$('#ap-etapes').hidden=true;rapport(R)}catch(e){$('#ap-etapes').hidden=true;$('#ap-res').innerHTML='<p>Les cours de ce titre n’ont pas pu être chargés. Réessaie dans un instant.</p>'}
 b.disabled=false;try{const u=new URL(location.href);u.searchParams.set('t',tk);history.replaceState(null,'',u)}catch(e){}}
async function etat(){const z=$('#ap-quota');if(!RBP.api){z.innerHTML='Gratuit, sans compte et sans limite : l’analyse est calculée en quelques secondes <b>directement dans ton navigateur</b>, sur plus de 2 000 actions, ETF, cryptos et l’or.';return}
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
 const S=R.situation||{},dev=R.devise,F=R.fourchettes||{},MC=R.monte_carlo||{},D=R.direction||{},RI=R.risques||{},M=R.marche||{},Z=R.saisonnalite||{},BL=R.bilan||{},EV=R.evenement,PR=R.pairs||[];
 let h=`<h2>${esc(R.nom)} (${esc(R.ticker)}) : le rapport complet</h2><p class="muted">Calculé le ${new Date(R.genere_le).toLocaleString('fr-FR')} sur ${R.seances} séances depuis le ${esc(R.debut)} · source : ${esc(R.source)} · ${esc(R.avertissement)}</p>`;
 if(R.verdict)h+=`<div class="ap-carte ap-verdict"><p>${esc(R.verdict)}</p></div>`;
 if(EV)h+=`<div class="ap-carte ap-alerte"><h3>📅 Résultats de l’entreprise ${EV.jours===0?'aujourd’hui':EV.jours===1?'demain':'dans '+EV.jours+' jours'} (${esc(EV.resultats_le.split('-').reverse().join('/'))})</h3><p>Le jour d’une publication, le cours peut sauter bien plus que d’habitude, dans un sens comme dans l’autre. ${EV.avant_echeance_mois?'La publication tombe avant l’échéance d’un mois : la fourchette ci-dessous est calculée sur des mois « normaux », garde de la marge.':'Elle tombe après l’échéance d’un mois.'}</p></div>`;
 h+=`<div class="ap-grille"><div class="ap-carte"><h3>La situation</h3><div class="ap-k"><div><b>${px(S.prix,dev)}</b><span>cours au ${esc(S.date)}</span></div><div><b>${pct((S.perf||{})['1 mois'])}</b><span>sur 1 mois</span></div><div><b>${pct((S.perf||{})['1 an'])}</b><span>sur 1 an</span></div>`
  +`<div><b>${S.au_dessus_200==null?'–':S.au_dessus_200?'Haussière':'Baissière'}</b><span>tendance de fond</span></div><div><b>${Math.round((S.vol_actuelle||0)*100)} %</b><span>agitation / an</span></div><div><b>${pct(S.recul_plus_haut_1an)}</b><span>depuis le plus haut 1 an</span></div></div></div>`;
 h+=`<div class="ap-carte"><h3>Les fourchettes probables</h3><table class="ap-t"><thead><tr><th>Horizon</th><th>8 fois sur 10 (en principe)</th><th>Réussite passée sur ce titre</th></tr></thead><tbody>${Object.entries(F).map(([k,v])=>`<tr><td>1 ${esc(k)}</td><td class="m">${px(v.bas80,'')} – ${px(v.haut80,dev)}</td><td class="m">${v.reussite_passee==null?'–':Math.round(v.reussite_passee*100)+' %'}</td></tr>`).join('')}</tbody></table>`
  +(BL.fourchette?`<p><b>En vrai</b>, sur ses ${BL.fourchette.nb} dernières prévisions vérifiées, le prix est resté dans la fourchette du site <b>${BL.fourchette.tenues} fois</b>${BL.fourchette.nb<30?' (encore peu de cas : à confirmer)':''}.</p>`:'')+`</div></div>`;
 h+=`<div class="ap-carte"><h3>3 000 simulations des 3 prochains mois</h3>${eventail(R)}</div>`;
 const sc=(MC.scenarios||{})['21'];
 const dirCarte=D.aucun?`<div class="ap-carte"><h3>Le sens à un mois</h3><p>L’IA du radar ne donne pas encore d’avis sur ce titre. Personne ne peut dire de façon fiable s’il montera le mois prochain : fie-toi plutôt aux fourchettes et aux risques.</p></div>`
  :`<div class="ap-carte"><h3>Le sens à un mois : l’avis de l’IA du radar</h3><p style="font-size:18px"><b class="${D.sens>0?'up':'down'}">${D.sens>0?'Plutôt à la hausse':'Plutôt à la baisse'}</b> : ${D.chances} chances sur 100, confiance ${esc(D.confiance)}.</p><p>Sur des années jamais vues, l’IA trouve le bon sens environ <b>${D.fiab}</b> fois sur 100 (réponse naïve : ${D.naif}). ${(+D.fiab>+D.naif)?'C’est un léger avantage, pas une certitude.':'Pour l’instant, ce n’est pas mieux que la réponse naïve : prends cet avis avec beaucoup de recul.'}${D.quotidien?' Avis calculé une fois par jour.':''}</p>`
   +(BL.direction?`<p>Sur ce titre, ses ${BL.direction.nb} dernières prévisions vérifiées : <b>${BL.direction.justes} bonnes directions</b>${BL.direction.nb<30?' (encore peu de cas)':''}.</p>`:'')+`<p><a href="resultats.html">Tous ses vrais résultats</a></p></div>`;
 let det='';
 if(sc){const cs=['var(--down)','var(--down)','var(--muted)','var(--up)','var(--up)'];det+=`<div class="ap-grille"><div class="ap-carte"><h3>Scénarios à 1 mois</h3>${barres(sc.map((x,i)=>[x.nom,x.proba,cs[i],Math.round(x.proba*100)+' %']),Math.max(...sc.map(x=>x.proba)))}<p class="muted" style="font-size:13px">Forte baisse : plus de 10 % ; stable : entre −3 et +3 %.</p></div>${dirCarte}</div>`}
 else det+=dirCarte;
 det+=`<div class="ap-grille"><div class="ap-carte"><h3>Les pires chutes sur la période</h3><table class="ap-t"><tbody>${(RI.pires_chutes||[]).map(c=>`<tr><td class="m down">${pct(c.chute,0)}</td><td>${esc(c.debut)} → ${esc(c.creux)}</td><td>${c.jours_recuperation!=null?'rattrapée en ~'+c.jours_recuperation+' j':'pas encore rattrapée'}</td></tr>`).join('')}</tbody></table>`
  +(RI.chute10_mois_historique!=null?`<p>Dans son passé, ce titre a perdu plus de 10 % en moins d’un mois <b>${Math.round(RI.chute10_mois_historique*100)} fois sur 100</b>`+(MC.chute10_mois!=null?` ; les simulations donnent <b>${Math.round(MC.chute10_mois*100)} %</b> pour le mois qui vient.`:'.')+'</p>':'')+'</div>';
 det+=`<div class="ap-carte"><h3>Lien avec le marché</h3>`+(M.beta!=null?`<p>Par rapport à ${esc(M.reference)} : <b>bêta ${String(M.beta).replace('.',',')}</b>, corrélation ${String(M.correlation).replace('.',',')}.</p><p class="muted">Bêta au-dessus de 1 : bouge plus fort que le marché. Sous 1 : plus calme.</p>`:'<p class="muted">Non disponible pour ce titre.</p>')+'</div></div>';
 if(PR.length>1)det+=`<div class="ap-carte"><h3>Face à des titres proches</h3><div style="overflow-x:auto"><table class="ap-t"><thead><tr><th>Titre</th><th>Sur 1 an</th><th>Agitation / an</th><th>Pire chute (1 an)</th><th>Tendance</th></tr></thead><tbody>${PR.map(p=>`<tr${p.soi?' style="font-weight:700"':''}><td>${p.soi?esc(p.nom):`<a href="analyse-approfondie.html?t=${encodeURIComponent(p.ticker)}">${esc(p.nom)}</a>`}</td><td class="m ${p.perf>0?'up':'down'}">${pct(p.perf,0)}</td><td class="m">${Math.round(p.vol*100)} %</td><td class="m down">${pct(p.dd,0)}</td><td>${p.tend==null?'–':p.tend?'↑ haussière':'↓ baissière'}</td></tr>`).join('')}</tbody></table></div><p class="muted" style="font-size:13px">Même secteur ou même famille. Clique sur un nom pour l’analyser à son tour.</p></div>`;
 if(Z.par_mois){const mo=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];det+=`<div class="ap-carte"><h3>Saisonnalité : part des années où chaque mois a monté</h3>${barres(Object.entries(Z.par_mois).map(([k,v])=>[mo[k-1]+(+k===Z.mois_prochain?' ←':''),v.hausse,v.hausse>=.5?'var(--up)':'var(--down)',Math.round(v.hausse*100)+' %']),1)}<p class="muted" style="font-size:13px">← le mois prochain. Peu d’années : le passé ne se répète pas forcément.</p></div>`}
 const fv=(R.fondamentaux||{}).valeurs;if(fv){const L={marketCap:'Capitalisation',trailingPE:'PER',returnOnEquity:'ROE',debtToEquity:'Dette / fonds propres',profitMargins:'Marge nette',fondsPropres:'Fonds propres',priceToBook:'Cours / fonds propres'};
  det+=`<div class="ap-carte"><h3>L’entreprise en chiffres</h3><table class="ap-t">${Object.entries(L).filter(([k])=>fv[k]!=null).map(([k,l])=>`<tr><td>${l}</td><td class="m">${['returnOnEquity','profitMargins'].includes(k)?pct(fv[k]):k==='debtToEquity'?Math.round(fv[k])+' %':Math.abs(fv[k])>=1e6?(fv[k]/1e9).toLocaleString('fr-FR',{maximumFractionDigits:1})+' Md':fv[k].toLocaleString('fr-FR',{maximumFractionDigits:2})}</td></tr>`).join('')}</table></div>`}
 h+=`<div class="ap-carte"><h3>En résumé</h3><ul class="ap-synth">${(R.synthese||[]).map(x=>'<li>'+esc(x)+'</li>').join('')}</ul></div>`;
 h+=`<details class="ap-plus"><summary>Voir tout le détail : avis de l’IA, scénarios, chutes, marché, titres proches, saisonnalité</summary>${det}</details>`;
 h+=`<p style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" class="btn" id="ap-partager">Partager ce rapport</button></p>`;
 h+=window.APSoutien||'';
 h+=`<p><a href="titres/${esc(R.slug||'')}.html">Fiche du titre</a> · <a href="outils/simulateur-stop-loss.html">Tester un stop-loss</a> · <a href="lecons/stop-loss.html">Comprendre les risques</a></p>`;
 box.innerHTML=h;box.scrollIntoView({behavior:'smooth'});
 const bp=document.getElementById('ap-partager');if(bp)bp.onclick=async()=>{const u=new URL(location.href);u.hash='';u.searchParams.set('t',R.ticker);u.searchParams.set('utm_campaign','partage-analyse');
  const txt='Analyse approfondie de '+R.nom+' : fourchettes, 3 000 simulations, risques (gratuit)';try{goatcounter.count({path:'partage/analyse',title:R.ticker,event:true})}catch(e){}
  if(navigator.share){try{await navigator.share({title:txt,url:u.href});return}catch(e){}}try{await navigator.clipboard.writeText(txt+' '+u.href);bp.textContent='Lien copié ✓'}catch(e){bp.textContent=u.href}}}
const go=()=>RBP.api?lancer():lancerNav();
$('#ap-go').onclick=go;$('#ap-tk').addEventListener('keydown',e=>{if(e.key==='Enter')go()});
const q=new URLSearchParams(location.search).get('t');if(q){$('#ap-tk').value=q;if(!RBP.api)setTimeout(lancerNav,300)}
liste();etat();const h=location.hash.slice(1);if(/^[a-z0-9]{12,40}$/.test(h)&&RBP.api){$('#ap-etapes').hidden=false;attendre(h)}
window.addEventListener('hashchange',()=>{const i=location.hash.slice(1);if(/^[a-z0-9]{12,40}$/.test(i))attendre(i)});
window.APRapport=rapport;
$('#ap-tk').addEventListener('focus',async()=>{if(!window.APEtendu)return;const E=await window.APEtendu();const dl=$('#ap-liste');if(!dl||!E.length)return;
 const deja=new Set([...dl.options].map(o=>o.value));const fr=document.createDocumentFragment();E.forEach(e=>{if(deja.has(e[1]))return;const o=document.createElement('option');o.value=e[1];o.textContent=e[0];fr.appendChild(o)});dl.appendChild(fr)},{once:true});
})();
</script>"""


def _liste_nav(payload):
    from . import config
    from .hebdo import avis_ia
    det = ((payload.get("suivi") or {}).get("detail") or {})
    pdir, pfo = det.get("par_titre") or {}, det.get("fourchette_par_titre") or {}
    out = []
    for t in payload.get("titres", []):
        if t.get("marche") == "tendances":
            continue
        try:
            p, sens, conf = avis_ia(t)
        except Exception:
            p, sens, conf = None, 0, "faible"
        if p is None:
            continue
        tk = t["ticker"]
        ref = config.benchmark_de(tk, t.get("marche", ""))
        sec = ((t.get("fondamentaux") or {}).get("secteur") or t.get("secteur") or "")
        if tk.endswith("-USD"):
            sec = "crypto"
        elif t.get("marche") == "etf":
            sec = "etf"
        d, f = pdir.get(tk) or [0, 0], pfo.get(tk) or [0, 0]
        out.append([tk, t.get("nom") or tk, seo.slug(tk), seo.slug(ref) if ref else "", sens,
                    round((p if sens > 0 else 1 - p) * 100), conf, config.NOM_BENCHMARK.get(ref, ref or ""),
                    {"€": "€", "$": "$"}.get(t.get("devise", ""), t.get("devise", "")),
                    sec[:40], [int(d[0]), int(d[1]), int(f[0]), int(f[1])]])
    return out


def _modele(payload):
    m = payload.get("modele") or {}
    pr, base = m.get("precision"), m.get("precision_base")
    return {"fiab": round(pr * 100) if isinstance(pr, (int, float)) else "–", "naif": round(base * 100) if isinstance(base, (int, float)) else "–"}


def page(base, payload, csp):
    chemin = "analyse-approfondie.html"
    opts = "".join(f"<option value='{_e(t['ticker'])}'>{_e(t.get('nom') or t['ticker'])}</option>"
                   for t in payload.get("titres", []) if t.get("marche") != "tendances")
    corps = (CSS + "<h1>Analyse approfondie d'une action, d'une crypto ou de l'or</h1>"
             "<p>Choisis un titre parmi plus de 2 000 : l'analyse reprend jusqu'à 3 ans de cours et les passe au crible. Fourchettes testées sur son propre passé, "
             "3 000 simulations des 3 prochains mois, avis de l'IA et ses vraies prévisions vérifiées, prochains résultats, pires chutes, "
             "comparaison avec des titres proches, saisonnalité et chiffres de l'entreprise. Chaque résultat dit à quel point il est fiable.</p>"
             "<div class='ap-carte'><div class='ap-form'><label for='ap-tk'><b>Titre</b> (nom ou symbole : MC.PA, AAPL, BTC-USD, GC=F…)"
             "<input id='ap-tk' list='ap-liste' autocomplete='off' placeholder='LVMH, Apple, Bitcoin, l’or…'></label>"
             "<button type='button' class='btn' id='ap-go' style='padding:11px 18px'>Lancer l'analyse approfondie</button></div>"
             f"<datalist id='ap-liste'>{opts}</datalist><p id='ap-quota' class='muted' style='margin:10px 0 0'></p><p id='ap-msg' role='alert'></p>"
             "<ul class='ap-etapes' id='ap-etapes' hidden aria-live='polite'></ul></div>"
             "<div id='ap-res' aria-live='polite'></div><div id='ap-mes'></div>"
             "<p class='muted'>Analyse statistique automatique et éducative : ce n'est pas un conseil en investissement. Tu peux fermer la page : "
             "le rapport reste disponible 30 jours dans « Mes analyses » sur cet appareil.</p>"
             + "<script>window.APSoutien=" + json.dumps(seo.bloc_soutien("", "Cette analyse est gratuite et illimitée. Si elle t’a été utile, tu peux soutenir le projet.").split("<script>")[0]).replace("</", "<\\/") + ";</script>"
             + abonnement._js()
             + NAV.replace("__LISTE__", json.dumps(_liste_nav(payload), ensure_ascii=False).replace("</", "<\\/"))
                  .replace("__MODELE__", json.dumps(_modele(payload)))
             + JS)
    return chemin, seo._page(base, f"Analyse approfondie d'une action par l'IA, à la demande | {NOM}",
                             "Choisis une action, une crypto ou l'or : l'IA analyse 3 ans de cours (fourchettes testées, 3 000 simulations, "
                             "risques, titres proches). Plus de 2 000 titres, gratuit, sans compte.",
                             chemin, corps, csp=abonnement._csp(csp))
