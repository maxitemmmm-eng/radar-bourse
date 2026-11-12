"""Version 83 : l'examen final expert et le questionnaire de positionnement de l'Académie.

Examen final : 30 questions en 4 épreuves (lecture de graphiques, méthodes de calcul, cas d'application, règles et pièges).
Les graphiques et les chiffres sont tirés au hasard à chaque passage : impossible d'apprendre les réponses par cœur.
Réponses chiffrées à saisir (pas de choix à cocher) pour la plupart des calculs. Certificat si 24 / 30 au moins
ET au moins la moitié des points dans chaque épreuve.

Positionnement : 3 questions de profil (objectif, expérience, temps par jour), puis un diagnostic d'une question à la fois
(2 par module, de la plus simple à la plus difficile), puis un plan personnel : module de départ, maîtrise par module,
chapitres conseillés dans l'ordre de l'objectif, date de fin estimée. Tout reste dans le navigateur.
Les chiffres réglementaires reprennent ceux des chapitres (relus le 11/11/2026).
"""
import json


def _e(s):
    import html
    return html.escape(str(s), quote=True)


CSS = """<style>
.x-tete{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;flex-wrap:wrap;margin-bottom:6px}
.x-regles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:16px 0}
.x-regles div{background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;padding:12px 14px}
.x-regles b{display:block;font-size:22px;color:var(--a-prim)}.x-regles span{font-size:13.5px;color:var(--a-muted)}
.x-barre{position:sticky;top:0;z-index:5;background:var(--a-bg);padding:10px 0;display:flex;gap:14px;align-items:center;border-bottom:1px solid var(--a-line);margin-bottom:14px}
.x-barre .p{flex:1;height:8px;border-radius:4px;background:var(--a-line);overflow:hidden}.x-barre .p i{display:block;height:100%;width:0;background:var(--a-prim);transition:width .3s}
.x-barre span{font-size:13.5px;color:var(--a-muted);white-space:nowrap;font-variant-numeric:tabular-nums}
.x-partie{margin:26px 0 8px;display:flex;gap:10px;align-items:baseline}.x-partie h2{margin:0;font-size:20px}.x-partie span{color:var(--a-muted);font-size:14px}
.x-q{background:var(--a-card);border:1px solid var(--a-line);border-radius:14px;padding:16px 18px;margin:12px 0;transition:border-color .2s}
.x-q.rep{border-color:var(--a-prim)}.x-q.ok{border-color:var(--a-ok);background:var(--a-ok-soft)}.x-q.ko{border-color:var(--a-ko);background:var(--a-ko-soft)}
.x-q .n{font-size:12.5px;color:var(--a-muted);margin:0 0 4px}.x-q .e{font-weight:600;margin:0 0 10px;line-height:1.45}
.x-q svg{width:100%;height:auto;max-width:640px;display:block;margin:6px 0 10px;background:var(--a-card2);border-radius:10px}
.x-q svg text{font-size:11px;fill:var(--a-muted);font-family:inherit}.x-q svg .fort{fill:var(--a-ink);font-weight:600}
.x-choix{display:grid;gap:8px}.x-choix label{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border:1.5px solid var(--a-line);border-radius:10px;cursor:pointer;background:var(--a-card)}
.x-choix label:has(input:checked){border-color:var(--a-prim);background:var(--a-soft)}
.x-choix label.juste{border-color:var(--a-ok)}.x-choix label.faux{border-color:var(--a-ko)}
.x-num{display:flex;gap:8px;align-items:center}.x-num input{font:inherit;font-size:17px;width:160px;padding:9px 12px;border-radius:10px;border:1.5px solid var(--a-line);background:var(--a-card);color:var(--a-ink)}
.x-num input:focus{outline:2px solid var(--a-prim);outline-offset:1px}
.x-cor{margin-top:10px;padding:10px 12px;border-radius:10px;background:var(--a-card);border:1px solid var(--a-line);font-size:14.5px}
.x-cor b.m{display:block;font-size:12.5px;color:var(--a-prim);margin-bottom:3px}
.x-res{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:14px 0}
.x-res div{border:1px solid var(--a-line);border-radius:12px;padding:12px;background:var(--a-card)}.x-res b{display:block;font-size:24px}
.x-res .ok b{color:var(--a-ok)}.x-res .ko b{color:var(--a-ko)}
.x-certif{border:2px solid var(--a-prim);border-radius:16px;padding:28px;text-align:center;background:var(--a-card);margin:20px 0}
.x-certif h2{margin:.2em 0;font-size:26px}.x-certif input{font:inherit;font-size:22px;text-align:center;border:0;border-bottom:2px solid var(--a-line);background:transparent;color:var(--a-ink);padding:4px;width:100%;max-width:320px}
.p-etape{animation:pIn .35s ease}@keyframes pIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.p-choix{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:12px 0}
.p-choix button{font:inherit;text-align:left;padding:14px 16px;border-radius:12px;border:1.5px solid var(--a-line);background:var(--a-card);color:var(--a-ink);cursor:pointer;transition:border-color .15s,transform .15s}
.p-choix button:hover{border-color:var(--a-prim)}.p-choix button[aria-pressed=true]{border-color:var(--a-prim);background:var(--a-soft)}
.p-choix button b{display:block}.p-choix button small{color:var(--a-muted)}
.p-q .x-choix label{cursor:pointer}
.p-niv{display:grid;gap:8px;margin:12px 0}.p-niv div{display:grid;grid-template-columns:minmax(150px,240px) 1fr 54px;gap:10px;align-items:center;font-size:14px}
.p-niv .b{height:10px;border-radius:5px;background:var(--a-line);overflow:hidden}.p-niv .b i{display:block;height:100%;background:var(--a-prim);width:0;transition:width .6s ease}
.p-plan ol{padding-left:20px}.p-plan li{margin:6px 0}
@media (prefers-reduced-motion:reduce){.p-etape{animation:none}.p-niv .b i{transition:none}}
</style>"""

# ----------------------------------------------------------------------------------------------------------------------------
# L'examen : générateurs de questions (JavaScript). Chaque générateur renvoie {p, e, svg?, t:'n'|'c', rep, tol, u, c, b, x, ch}
# p : épreuve (0 à 3), e : énoncé, x : correction avec la méthode, ch : chapitre à revoir.
# ----------------------------------------------------------------------------------------------------------------------------
JS_EXAMEN = r"""
(function(){
const Z=document.getElementById("x-zone"); if(!Z) return;
let graine=Date.now()%2147483647||7; const R=()=>{graine=graine*48271%2147483647; return graine/2147483647;};
const U=(a,b)=>a+R()*(b-a), I=(a,b)=>Math.floor(U(a,b+1)), P=a=>a[Math.floor(R()*a.length)];
const mel=a=>a.map(x=>[R(),x]).sort((p,q)=>p[0]-q[0]).map(x=>x[1]);
const nf=(v,d=2)=>v.toLocaleString("fr-FR",{minimumFractionDigits:0,maximumFractionDigits:d});
const eur=v=>nf(v,2)+" €", pc=v=>nf(v,1)+" %";
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const EPR=["Lecture de graphiques","Méthodes de calcul","Cas d'application","Règles et pièges"];

/* ---------- petit moteur de graphiques ---------- */
function marche(n,v0,derive,agit){const v=[v0];for(let i=1;i<n;i++)v.push(Math.max(1,v[i-1]*(1+derive+agit*(R()+R()+R()-1.5)/1.5)));return v;}
function lisse(a,k){return a.map((_,i)=>{const s=a.slice(Math.max(0,i-k),i+k+1);return s.reduce((x,y)=>x+y,0)/s.length;});}
function graphe(series,o={}){
  const W=640,H=o.h||250,pl=10,pr=56,pt=14,pb=24,n=Math.max(...series.map(s=>s.v.length));
  let vals=series.flatMap(s=>s.v).concat((o.lignes||[]).map(l=>l.v)); let lo=o.min??Math.min(...vals),hi=o.max??Math.max(...vals); const m=(hi-lo)*.08; if(o.min==null)lo-=m; if(o.max==null)hi+=m;
  const x=i=>pl+i/(n-1)*(W-pl-pr), y=v=>pt+(hi-v)/(hi-lo)*(H-pt-pb);
  const pas=o.pas||(()=>{const r=(hi-lo)/5,p=Math.pow(10,Math.floor(Math.log10(r)));return [1,2,2.5,5,10].map(k=>k*p).find(k=>k>=r)||r;})();
  let g=""; for(let v=Math.ceil(lo/pas)*pas;v<=hi;v+=pas){g+=`<line x1="${pl}" x2="${W-pr}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" stroke="var(--a-line)"/><text x="${W-pr+6}" y="${(y(v)+4).toFixed(1)}">${nf(v,1)}</text>`;}
  const ex=o.ex||Math.ceil(n/6); for(let i=0;i<n;i+=ex) g+=`<text x="${x(i).toFixed(1)}" y="${H-6}" text-anchor="middle">${o.xlab?o.xlab(i):"J"+i}</text>`;
  (o.lignes||[]).forEach(l=>g+=`<line x1="${pl}" x2="${W-pr}" y1="${y(l.v)}" y2="${y(l.v)}" stroke="${l.c||"var(--a-muted)"}" stroke-dasharray="5 4"/>`+(l.t?`<text x="${pl+4}" y="${y(l.v)-5}" class="fort">${l.t}</text>`:""));
  if(o.zone) g+=`<path d="${o.zone(x,y)}" fill="var(--a-prim)" opacity=".16"/>`;
  series.forEach(s=>{ if(s.barres){const bw=(W-pl-pr)/n*.7; s.v.forEach((v,i)=>g+=`<rect x="${(x(i)-bw/2).toFixed(1)}" y="${y(v).toFixed(1)}" width="${bw.toFixed(1)}" height="${(y(lo)-y(v)).toFixed(1)}" fill="${s.c}" opacity=".55"/>`);return;}
    g+=`<path d="${s.v.map((v,i)=>(i?"L":"M")+x(i).toFixed(1)+" "+y(v).toFixed(1)).join("")}" fill="none" stroke="${s.c||"var(--a-ink)"}" stroke-width="${s.w||2}" ${s.tir?'stroke-dasharray="6 4"':""}/>`;
    if(s.nom) g+=`<text x="${(x(s.v.length-1)+4).toFixed(1)}" y="${(y(s.v.at(-1))-8).toFixed(1)}" class="fort" text-anchor="end">${s.nom}</text>`;});
  (o.points||[]).forEach(p=>g+=`<circle cx="${x(p.i)}" cy="${y(p.v)}" r="4.5" fill="${p.c||"var(--a-prim)"}"/><text x="${x(p.i)}" y="${y(p.v)+(p.bas?18:-10)}" text-anchor="middle" class="fort">${p.t}</text>`);
  if(o.bougies) o.bougies.forEach((b,i)=>{const c=b.c>=b.o?"var(--a-ok)":"var(--a-ko)",bw=46,cx=x(i+1);g+=`<line x1="${cx}" x2="${cx}" y1="${y(b.h)}" y2="${y(b.l)}" stroke="${c}" stroke-width="2"/><rect x="${cx-bw/2}" y="${y(Math.max(b.o,b.c))}" width="${bw}" height="${Math.max(2,Math.abs(y(b.o)-y(b.c)))}" fill="${c}"/><text x="${cx}" y="${H-6}" text-anchor="middle">bougie ${i+1}</text>`;});
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.titre||"Graphique")}">${g}</svg>`;
}
function rsi(a,n=14){const o=a.map(()=>null);let g=0,p=0;for(let i=1;i<a.length;i++){const d=a[i]-a[i-1],u=Math.max(d,0),w=Math.max(-d,0);if(i<=n){g+=u/n;p+=w/n;if(i===n)o[i]=p?100-100/(1+g/p):100;}else{g=(g*(n-1)+u)/n;p=(p*(n-1)+w)/n;o[i]=p?100-100/(1+g/p):100;}}return o;}
function qcm(choix,bonne){const m=mel(choix.map((c,i)=>({c,ok:i===bonne})));return {c:m.map(x=>x.c),b:m.findIndex(x=>x.ok)};}

/* ---------- épreuve 1 : lecture de graphiques ---------- */
function A_drawdown(){
  const v0=100,pic=U(135,175),creux=pic*(1-U(.24,.42)),fin=creux*U(1.05,1.2);
  const a=lisse(marche(50,v0,(Math.log(pic/v0))/49,.006),2).map((v,i,s)=>v*(pic/s.at(-1))**(i/49));
  const b=Array.from({length:36},(_,i)=>pic*(creux/pic)**(i/35)*(1+.012*Math.sin(i*1.3)));b[0]=pic;b[35]=creux;
  const c=Array.from({length:30},(_,i)=>creux*(fin/creux)**(i/29)*(1+.01*Math.sin(i*1.7)));
  const v=a.concat(b.slice(1),c.slice(1)).map(z=>Math.round(z*10)/10); const ip=v.indexOf(Math.max(...v.slice(0,60))), ic=v.indexOf(Math.min(...v.slice(ip)));
  const P=v[ip],C=v[ic],dd=(C/P-1)*100,rem=(P/C-1)*100;
  const svg=graphe([{v}],{titre:"Cours avec sommet et creux",points:[{i:ip,v:P,t:"sommet "+nf(P,1)},{i:ic,v:C,t:"creux "+nf(C,1),bas:1}]});
  return [
    {p:0,svg,e:"Sur ce graphique, quelle a été la pire baisse depuis le sommet (le drawdown maximal), en % ? Réponds avec un nombre (le signe moins est facultatif).",t:"n",rep:dd,tol:.5,u:"%",abs:1,
     x:`Drawdown = creux ÷ sommet − 1 = ${nf(C,1)} ÷ ${nf(P,1)} − 1 = <b>${pc(dd)}</b>. On part toujours du plus haut atteint AVANT le creux.`,ch:"rendement-risque"},
    {p:0,svg,e:"Depuis ce creux, de combien le prix doit-il monter (en %) pour revenir exactement au sommet ?",t:"n",rep:rem,tol:.5,u:"%",
     x:`Hausse nécessaire = sommet ÷ creux − 1 = ${nf(P,1)} ÷ ${nf(C,1)} − 1 = <b>${pc(rem)}</b>, bien plus que les ${pc(-dd)} perdus : une perte de x % demande une hausse de x ÷ (1 − x).`,ch:"rendement-risque"}];
}
function A_support(){
  const S=I(40,80), pts=[[0,1.3],[24,1],[41,U(1.15,1.25)],[58,1],[75,U(1.12,1.2)],[92,1],[109,U(1.2,1.3)]], v=[];
  for(let k=0;k<pts.length-1;k++){const [i0,a]=pts[k],[i1,b]=pts[k+1];for(let i=i0;i<i1;i++){const t=(i-i0)/(i1-i0);v.push(S*(a+(b-a)*t)*(1+(i===i0?0:.008*(R()-.5))));}}
  v.push(S*pts.at(-1)[1]); for(let i=0;i<v.length;i++) v[i]=Math.max(S*1.001,v[i]);
  const opts=[S,Math.round(S*1.18),Math.round(S*.85),Math.round(Math.max(...v))]; const q=qcm(opts.map(z=>nf(z,0)),0);
  return [{p:0,svg:graphe([{v}],{titre:"Cours qui rebondit plusieurs fois"}),e:"Quel niveau de prix a servi de support (le prix a rebondi dessus trois fois) ?",t:"c",c:q.c,b:q.b,
    x:`Le prix est venu trois fois toucher environ <b>${nf(S,0)}</b> sans passer dessous, puis est reparti : c'est un support, une zone où les acheteurs reviennent. Ce n'est pas une garantie : un support finit souvent par céder.`,ch:"bougies-tendances"}];
}
function A_bougies(){
  const bs=[]; let o=I(20,30)*2;
  for(let i=0;i<4;i++){ const c=o+2*I(-4,4)||o+4; const h=Math.max(o,c)+2*I(1,3), l=Math.min(o,c)-2*I(1,3); bs.push({o,c,h,l}); o=c; }
  const k=2, b=bs[k], rouge=b.c<b.o;
  return [{p:0,svg:graphe([{v:[0,0,0,0,0,0],c:"none",w:0}],{titre:"Quatre bougies",bougies:bs,min:Math.min(...bs.map(z=>z.l))-4,max:Math.max(...bs.map(z=>z.h))+4,pas:2,h:240,xlab:()=>"",ex:99}),
    e:`Lis la bougie 3 (${rouge?"rouge":"verte"}). Quel est son cours de clôture ?`,t:"n",rep:b.c,tol:.6,u:"",
    x:`Bougie ${rouge?"rouge : le prix a baissé, la clôture est en BAS du corps":"verte : le prix a monté, la clôture est en HAUT du corps"}. Ouverture ${b.o}, clôture <b>${b.c}</b>, plus haut ${b.h}, plus bas ${b.l} (les mèches).`,ch:"bougies-tendances"}];
}
function A_rsi(){
  let v,r,k=0,essai=0; do{ v=marche(120,100,0,.03); r=rsi(v); k=0; for(let i=15;i<r.length;i++) if(r[i-1]>=30&&r[i]<30) k++; essai++; }while((k<1||k>3)&&essai<200);
  const rr=r.map(z=>z??50); const q=qcm(["0","1","2","3","4"].slice(0,5),k);
  return [{p:0,svg:graphe([{v:rr,c:"var(--a-prim)"}],{titre:"RSI sur 14 jours",min:0,max:100,pas:10,h:220,lignes:[{v:70,t:"70 : surachat",c:"var(--a-ko)"},{v:30,t:"30 : survente",c:"var(--a-ok)"}]}),
    e:"Combien de fois le RSI est-il passé SOUS le seuil de 30 (franchissement de haut en bas) ?",t:"c",c:q.c,b:q.b,
    x:`On compte les passages de la ligne au-dessus de 30 vers en dessous : <b>${k}</b>. Un RSI sous 30 signale une baisse rapide (« survente »), pas un rebond garanti : il peut rester bas longtemps dans une forte tendance baissière.`,ch:"moyennes-rsi-macd"}];
}
function A_base100(){
  const a=lisse(marche(90,100,U(.001,.004),.018),2), b=lisse(marche(90,100,U(-.001,.002),.012),2);
  a[0]=b[0]=100; const fa=Math.round(a.at(-1)*10)/10, fb=Math.round(b.at(-1)*10)/10; a[89]=fa; b[89]=fb;
  const d=fa-fb;
  return [{p:0,svg:graphe([{v:a,c:"var(--a-prim)",nom:"A : "+nf(fa,1)},{v:b,c:"var(--a-or)",nom:"B : "+nf(fb,1)}],{titre:"Deux placements en base 100",lignes:[{v:100}]}),
    e:"Ces deux placements sont en « base 100 » au départ. De combien de points de % A a-t-il fait mieux (ou moins bien, avec un signe moins) que B sur la période ?",t:"n",rep:d,tol:.15,u:"points",
    x:`En base 100, la valeur finale moins 100 donne directement la performance : A ${pc(fa-100)}, B ${pc(fb-100)}. Écart = <b>${nf(d,1)} points</b>. La base 100 sert justement à comparer des prix très différents.`,ch:"indices-cac40-sp500"}];
}
function A_fan(){
  const p0=I(40,160), h=p0*U(1.12,1.25), b=p0*U(.78,.9), n=22, med=p0*U(.99,1.02);
  const haut=Array.from({length:n},(_,i)=>p0+(h-p0)*Math.sqrt(i/(n-1))), bas=Array.from({length:n},(_,i)=>p0+(b-p0)*Math.sqrt(i/(n-1))), m=Array.from({length:n},(_,i)=>p0+(med-p0)*i/(n-1));
  const q=qcm(["Environ 10 %","Environ 20 %","Environ 50 %","Environ 80 %"],0);
  return [{p:0,svg:graphe([{v:haut,c:"var(--a-ok)",nom:"haut (8 fois sur 10 dessous)"},{v:m,c:"var(--a-ink)",tir:1},{v:bas,c:"var(--a-ko)",nom:"bas"}],{titre:"Fourchette de prévision à 80 %",ex:7,xlab:i=>"J+"+i}),
    e:"Cette fourchette contient le prix final 8 fois sur 10 et elle est symétrique en probabilité. Quelle est la probabilité que le prix finisse AU-DESSUS de la borne haute ?",t:"c",c:q.c,b:q.b,
    x:"8 fois sur 10 dedans, donc 2 fois sur 10 dehors, réparties des deux côtés : <b>environ 10 %</b> au-dessus et 10 % en dessous. C'est pour cela qu'une fourchette « ratée » 2 fois sur 10 est normale.",ch:"volatilite-et-ia"}];
}
function A_volume(){
  const v=lisse(marche(60,100,.004,.008),2).map((z,i)=>z+i*.15), vol=v.map((_,i)=>Math.max(5,100-i*1.3+U(-8,8)));
  const lo=Math.min(...v), hi=Math.max(...v), vs=vol.map(z=>lo+(z/110)*(hi-lo)*.45);
  const q=qcm(["La hausse est soutenue par de plus en plus d'acheteurs","La hausse s'essouffle : de moins en moins d'échanges la portent","Le volume n'apporte aucune information","C'est un signal certain de krach"],1);
  return [{p:0,svg:graphe([{v:vs,c:"var(--a-muted)",barres:1},{v,c:"var(--a-ink)"}],{titre:"Cours et volumes échangés"}),
    e:"Le cours monte (ligne) pendant que les volumes échangés (barres) diminuent nettement. Quelle lecture est la plus juste ?",t:"c",c:q.c,b:q.b,
    x:"Une hausse sur des volumes en baisse montre que de moins en moins de monde achète à ces prix : la tendance <b>s'essouffle</b>. C'est un signal de prudence, jamais une certitude.",ch:"bougies-tendances"}];
}

/* ---------- épreuve 2 : méthodes de calcul ---------- */
const CALC=[
 ()=>{const a=I(5000,20000),n=I(5,15),r=U(.03,.11),b=a*(1+r)**n,cagr=((b/a)**(1/n)-1)*100;return {e:`Un placement passe de ${eur(a)} à ${eur(Math.round(b))} en ${n} ans. Quel est son rendement annuel moyen (taux de croissance annuel composé), en % ?`,t:"n",rep:cagr,tol:.1,u:"%",
   x:`Taux annuel = (valeur finale ÷ valeur initiale)^(1/n) − 1 = (${nf(Math.round(b)/a,4)})^(1/${n}) − 1 = <b>${pc(cagr)}</b>. Diviser le gain total par le nombre d'années surestime le rendement.`,ch:"interets-composes"};},
 ()=>{const m=P([50,100,150,200]),n=P([10,15,20,25]),r=P([4,5,6,7]),t=r/100/12,fv=m*((1+t)**(n*12)-1)/t;return {e:`Tu verses ${m} € par mois pendant ${n} ans, à ${r} % par an (intérêts composés chaque mois). Quel capital final, en € ? (tolérance 1 %)`,t:"n",rep:fv,tol:fv*.01,u:"€",
   x:`Valeur future de versements réguliers = m × ((1 + t)^N − 1) ÷ t, avec t = ${r} % ÷ 12 et N = ${n*12} mois : <b>${eur(Math.round(fv))}</b>, pour ${eur(m*12*n)} versés.`,ch:"interets-composes"};},
 ()=>{const ach=I(2000,9000),gain=I(400,3000),fr=I(5,30),pv=gain-2*fr,imp=pv*.314,net=gain-2*fr-imp;return {e:`Sur un compte-titres, tu achètes pour ${eur(ach)} et revends pour ${eur(ach+gain)}. Frais de courtage : ${fr} € à l'achat et ${fr} € à la vente. Flat tax 2026 : 31,4 %. Quel gain net, après frais et impôt, en € ?`,t:"n",rep:net,tol:1,u:"€",
   x:`Plus-value imposable = ${gain} − ${2*fr} (frais déductibles) = ${eur(pv)}. Impôt = 31,4 % × ${eur(pv)} = ${eur(imp)}. Gain net = <b>${eur(net)}</b>.`,ch:"fiscalite-2026"};},
 ()=>{const bpa=U(2,9),per=I(10,25),cible=I(12,30),px=bpa*per,pc2=bpa*cible;return {e:`Une action vaut ${eur(Math.round(px*100)/100)} et son bénéfice par action est de ${nf(bpa,2)} €. Si le marché la valorisait à un PER de ${cible}, à bénéfice égal, quel serait son prix, en € ?`,t:"n",rep:pc2,tol:.05,u:"€",
   x:`PER = prix ÷ bénéfice par action, donc prix = PER × BPA = ${cible} × ${nf(bpa,2)} = <b>${eur(pc2)}</b> (PER actuel : ${nf(px/bpa,1)}).`,ch:"ratios-per-rendement"};},
 ()=>{const px=I(20,120),div=U(.6,5),n=I(50,400),brut=div*n,net=brut*(1-.314),rd=div/px*100;return {e:`Tu détiens ${n} actions à ${px} €. Le dividende est de ${nf(div,2)} € par action, sur un compte-titres (flat tax 31,4 %). Quel montant net touches-tu, en € ?`,t:"n",rep:net,tol:.5,u:"€",
   x:`Brut = ${n} × ${nf(div,2)} = ${eur(brut)} ; net = brut × (1 − 0,314) = <b>${eur(net)}</b>. Rendement brut du dividende : ${pc(rd)}. Le cours baisse d'environ le montant du dividende le jour du détachement.`,ch:"dividendes"};},
 ()=>{const d=U(.8,3.2),a=d*Math.sqrt(252);return {e:`Une action varie en moyenne de ${nf(d,2)} % par jour (écart-type des variations quotidiennes). Quelle est sa volatilité annuelle, en % ? (252 séances par an)`,t:"n",rep:a,tol:.3,u:"%",
   x:`Volatilité annuelle = quotidienne × √252 ≈ ${nf(d,2)} × 15,87 = <b>${pc(a)}</b>. On multiplie par la racine du nombre de jours, pas par le nombre de jours.`,ch:"rendement-risque"};},
 ()=>{const cap=P([5000,10000,20000,30000]),r=P([1,1.5,2]),e=I(30,120),s=Math.round(e*U(.88,.95)*100)/100,risque=cap*r/100,nb=Math.floor(risque/(e-s));return {e:`Capital : ${eur(cap)}. Tu acceptes de risquer ${nf(r,1)} % du capital sur une opération. Achat à ${eur(e)}, stop-loss à ${eur(s)}. Combien d'actions au maximum (nombre entier) ?`,t:"n",rep:nb,tol:0,u:"actions",
   x:`Risque accepté = ${nf(r,1)} % × ${eur(cap)} = ${eur(risque)}. Perte par action si le stop est touché = ${eur(e-s)}. Nombre = ${eur(risque)} ÷ ${eur(e-s)} = ${nf(risque/(e-s),2)}, arrondi en dessous : <b>${nb}</b>.`,ch:"construire-son-portefeuille"};},
 ()=>{const lev=P([3,5,10]),b=I(4,15),perte=Math.min(100,lev*b);return {e:`Tu prends une position avec un effet de levier de ${lev} sur une action qui baisse ensuite de ${b} %. Quelle perte, en % de ta mise ? (100 si tout est perdu)`,t:"n",rep:perte,tol:.1,u:"%",
   x:`Le levier multiplie le mouvement : ${lev} × ${b} % = ${lev*b} %${lev*b>=100?" : au-delà de 100 %, la position est liquidée et la mise est <b>entièrement perdue</b>":" : <b>"+perte+" %</b> de la mise"}. Le levier ne change pas les chances d'avoir raison.`,ch:"levier-options-cfd"};},
 ()=>{const D=I(4,12),dy=P([.5,1,1.5,2]),ch=-D*dy;return {e:`Une obligation a une duration de ${D} ans. Les taux du marché montent de ${nf(dy,1)} point. De combien son prix varie-t-il environ, en % ?`,t:"n",rep:ch,tol:.2,u:"%",
   x:`Variation du prix ≈ − duration × variation des taux = − ${D} × ${nf(dy,1)} = <b>${pc(ch)}</b>. Quand les taux montent, le prix des obligations existantes baisse, d'autant plus que la duration est longue.`,ch:"obligations-en-detail"};},
 ()=>{const a=I(-10,25),f=I(-12,10),eu=((1+a/100)*(1+f/100)-1)*100;return {e:`Une action américaine fait ${a>=0?"+":""}${a} % en dollars sur l'année. Sur la même période, le dollar ${f>=0?"gagne":"perd"} ${Math.abs(f)} % face à l'euro. Quelle performance pour un investisseur en euros, en % ?`,t:"n",rep:eu,tol:.1,u:"%",
   x:`Les deux effets se multiplient : (1 ${a>=0?"+":"−"} ${Math.abs(a)/100}) × (1 ${f>=0?"+":"−"} ${Math.abs(f)/100}) − 1 = <b>${pc(eu)}</b>. Les additionner donne un résultat approché, pas exact.`,ch:"devises-risque-de-change"};},
 ()=>{const c=10000,n=P([15,20,25]),r=.06,f1=P([1.5,1.8,2]),f2=P([.2,.3]),v1=c*(1+r-f1/100)**n,v2=c*(1+r-f2/100)**n;return {e:`10 000 € placés ${n} ans à 6 % par an avant frais. Fonds A : ${nf(f1,1)} % de frais par an. Fonds B (ETF) : ${nf(f2,1)} %. Quel écart de capital final entre B et A, en € ? (tolérance 1 %)`,t:"n",rep:v2-v1,tol:(v2-v1)*.01,u:"€",
   x:`A : 10 000 × (1 + 0,06 − ${nf(f1/100,3)})^${n} = ${eur(Math.round(v1))}. B : 10 000 × (1 + 0,06 − ${nf(f2/100,3)})^${n} = ${eur(Math.round(v2))}. Écart : <b>${eur(Math.round(v2-v1))}</b>. Des frais de 1,5 % par an paraissent petits, mais ils se composent.`,ch:"lire-un-dic"};},
 ()=>{const w=[I(40,70)],ra=I(-15,30),rb=I(-5,10);w.push(100-w[0]);const g=(w[0]*ra+w[1]*rb)/100;return {e:`Ton portefeuille contient ${w[0]} % d'actions (qui font ${ra} % sur l'année) et ${w[1]} % d'obligations (qui font ${rb} %). Quelle performance globale, en % ?`,t:"n",rep:g,tol:.05,u:"%",
   x:`Moyenne pondérée : ${w[0]} % × ${ra} + ${w[1]} % × ${rb} = <b>${pc(g)}</b>.`,ch:"construire-son-portefeuille"};},
];

/* ---------- épreuve 3 : cas d'application ---------- */
const CAS=[
 ()=>{const tot=P([10000,20000,50000]),wa=P([60,70,50]),ra=I(15,40),rb=I(-8,3),A=tot*wa/100*(1+ra/100),B=tot*(100-wa)/100*(1+rb/100),T=A+B,vend=A-T*wa/100;
   return {e:`Léa a ${eur(tot)} répartis ${wa} % actions / ${100-wa} % obligations. En un an, les actions font ${ra>=0?"+":""}${ra} % et les obligations ${rb>=0?"+":""}${rb} %. Pour revenir à ${wa} / ${100-wa}, combien d'euros d'actions doit-elle vendre (pour acheter des obligations) ?`,t:"n",rep:vend,tol:2,u:"€",
   x:`Actions : ${eur(Math.round(A))}, obligations : ${eur(Math.round(B))}, total ${eur(Math.round(T))}. Cible actions = ${wa} % × ${eur(Math.round(T))} = ${eur(Math.round(T*wa/100))}. À vendre : <b>${eur(Math.round(vend))}</b>. Rééquilibrer revient à vendre ce qui a monté.`,ch:"construire-son-portefeuille"};},
 ()=>{const m=P([100,200,300]),px=[I(40,60)];for(let i=0;i<3;i++)px.push(Math.max(10,px.at(-1)+I(-12,12)));const parts=px.reduce((s,p)=>s+m/p,0),pm=4*m/parts,moy=px.reduce((s,p)=>s+p,0)/4;
   return {e:`Tu investis ${m} € chaque mois pendant 4 mois, aux prix successifs de ${px.join(" €, ")} €. Quel est ton prix de revient moyen par part, en € ?`,t:"n",rep:pm,tol:.05,u:"€",
   x:`Parts achetées = ${px.map(p=>m+"÷"+p).join(" + ")} = ${nf(parts,3)}. Prix moyen = ${4*m} ÷ ${nf(parts,3)} = <b>${eur(pm)}</b>, un peu sous la moyenne des prix (${eur(moy)}) : on achète plus de parts quand c'est bas.`,ch:"investir-regulierement"};},
 ()=>{const g=I(3000,15000),cto=g*.314,pea=g*.186;return {e:`Un gain de ${eur(g)} (réalisé en 2026) : combien d'impôts et prélèvements économise-t-on en le retirant d'un PEA de plus de 5 ans plutôt que d'un compte-titres, en € ?`,t:"n",rep:cto-pea,tol:1,u:"€",
   x:`Compte-titres : 31,4 % = ${eur(cto)}. PEA de plus de 5 ans : prélèvements sociaux seulement, 18,6 % = ${eur(pea)}. Économie : <b>${eur(cto-pea)}</b> (12,8 % du gain).`,ch:"fiscalite-2026"};},
 ()=>{const sous=R()<.5,ces=sous?I(120,300):I(600,4000),pv=Math.round(ces*U(.2,.6)),imp=sous?0:pv*.314;return {e:`En 2026, tu vends des cryptos contre des euros pour un total de ${eur(ces)} sur l'année, avec une plus-value totale de ${eur(pv)}. Combien d'impôt dois-tu, en € ? (0 si rien)`,t:"n",rep:imp,tol:.5,u:"€",
   x:sous?`Le total des cessions (${eur(ces)}) ne dépasse pas 305 € : <b>aucun impôt</b>. C'est le montant des ventes qui compte, pas celui du gain.`:`Le total des cessions dépasse 305 € : toute la plus-value est imposable à 31,4 % = <b>${eur(imp)}</b> (ce n'est pas un abattement).`,ch:"fiscalite-crypto-2026"};},
 ()=>{const s=I(80,95),o=s-I(5,12),q=qcm([`Vers ${o} €, au prix d'ouverture`,`Exactement à ${s} €`,`L'ordre est annulé`,`Le courtier rembourse la différence`],0);return {e:`Tu as placé un stop-loss à ${s} €. Après une mauvaise nouvelle publiée la nuit, l'action ouvre directement à ${o} €. À quel prix ta vente est-elle probablement exécutée ?`,t:"c",c:q.c,b:q.b,
   x:`Un stop devient un ordre au marché quand le seuil est franchi. Le prix a « sauté » ${s} € (un gap) : la vente se fait au premier prix disponible, <b>vers ${o} €</b>. Le stop limite les pertes, il ne les garantit pas.`,ch:"passer-un-ordre"};},
 ()=>{const sig=P([15,20,25]),rho=P([-.5,0,.5]),sp=sig*Math.sqrt(.5+.5*rho);return {e:`Deux actifs ont chacun une volatilité de ${sig} % par an et une corrélation de ${nf(rho,1)}. Portefeuille 50 / 50 : quelle volatilité, en % ?`,t:"n",rep:sp,tol:.15,u:"%",
   x:`σ² = 0,5² × σ² + 0,5² × σ² + 2 × 0,5 × 0,5 × ρ × σ² = σ² × (0,5 + 0,5ρ). σ = ${sig} × √${nf(.5+.5*rho,2)} = <b>${pc(sp)}</b>. Moins les actifs bougent ensemble, plus la diversification réduit le risque.`,ch:"diversification"};},
 ()=>{const k=P([5,9,12]),q=qcm([k>=9?"Bien calibrée sur ces cas":"Trop sûre d'elle sur ces cas","Parfaitement fiable","Impossible à juger avec des pourcentages","Calibrée seulement si elle a eu raison 10 fois"],0);return {e:`Une IA a annoncé « 70 % de chances de hausse » sur 12 titres différents. ${k} ont réellement monté. Que peut-on dire, sur ces 12 cas ?`,t:"c",c:q.c,b:q.b,
   x:`70 % de 12 ≈ 8,4 hausses attendues. ${k} observées : ${k>=9?"c'est cohérent, elle est <b>bien calibrée</b> sur ces cas":"c'est bien moins, elle est <b>trop sûre d'elle</b>"}. Une probabilité se juge sur beaucoup de cas, jamais sur un seul. 12 cas restent peu : la conclusion est fragile.`,ch:"utiliser-ia-intelligemment"};},
 ()=>{const S=[["Tu gardes une action qui a perdu 40 % « pour ne pas réaliser la perte », alors que tu ne l'achèterais plus aujourd'hui.","L'aversion à la perte"],
   ["Tu refuses de vendre au-dessous de ton prix d'achat, comme si ce prix comptait pour le marché.","L'ancrage"],["Tu achètes une crypto parce que tout le monde en parle et qu'elle a doublé en une semaine.","La peur de rater le coche (FOMO)"],
   ["Tu ne lis que les articles qui confirment que ton action va monter.","Le biais de confirmation"]],s=P(S),noms=S.map(x=>x[1]),q=qcm(noms,noms.indexOf(s[1]));
   return {e:`Quel biais décrit le mieux ce comportement ? « ${s[0]} »`,t:"c",c:q.c,b:q.b,x:`C'est <b>${s[1].toLowerCase()}</b>. La parade : des règles écrites à l'avance, décidées à froid.`,ch:"psychologie-investisseur"};},
];

/* ---------- épreuve 4 : règles et pièges ---------- */
const REGLES=[
 ["Quel est le plafond de versements d'un PEA classique ?",["150 000 €","22 950 €","100 000 €","Il n'y a pas de plafond"],0,"150 000 € de versements (225 000 € au total avec un PEA-PME). Les gains ne comptent pas dans le plafond.","pea-cto-assurance-vie"],
 ["Que se passe-t-il, en principe, si tu retires de l'argent d'un PEA avant 5 ans ?",["Le plan est clôturé et les gains sont taxés comme sur un compte-titres","Rien de particulier","Une amende de 750 €","Seuls les prélèvements sociaux s'appliquent"],0,"Avant 5 ans, un retrait clôture en principe le plan ; les gains sont taxés au PFU.","pea-cto-assurance-vie"],
 ["Sur un compte-titres, une moins-value réalisée en 2026 peut être imputée sur les plus-values…",["de la même année et des 10 années suivantes","de la même année seulement","des 3 années précédentes","jamais"],0,"Report possible sur les plus-values de la même année et des 10 années suivantes.","fiscalite-2026"],
 ["Après 8 ans, l'abattement annuel sur les gains retirés d'une assurance-vie, pour une personne seule, est de…",["4 600 €","9 200 €","1 525 €","305 €"],0,"4 600 € pour une personne seule, 9 200 € pour un couple.","fiscalite-2026"],
 ["Échanger du bitcoin contre un stablecoin (sans revenir en euros) est-il imposable au moment de l'échange en France ?",["Non, l'impôt est reporté jusqu'à la sortie en euros","Oui, à 31,4 %","Oui, au-delà de 305 €","Seulement pour les stablecoins en dollars"],0,"Les échanges crypto contre crypto sont neutres fiscalement ; l'impôt est dû lors de la cession contre euros, d'un bien ou d'un service.","fiscalite-crypto-2026"],
 ["Oublier de déclarer un compte crypto ouvert à l'étranger (formulaire 3916-bis) coûte, par compte et par an…",["750 € (1 500 € au-delà de 50 000 €)","Rien si le compte est petit","10 % du solde","150 €"],0,"750 € par compte non déclaré, 1 500 € si la valeur dépasse 50 000 €.","fiscalite-crypto-2026"],
 ["Sur le DIC d'un produit, l'indicateur synthétique de risque va de…",["1 à 7","0 à 10","A à E","1 à 5"],0,"De 1 (le plus faible) à 7 (le plus élevé). C'est le premier chiffre à regarder.","lire-un-dic"],
 ["Une publicité promet « 2 % par jour garantis grâce à notre IA de trading ». Quelle est la bonne réaction ?",["Vérifier la liste noire de l'AMF et ne rien verser : un gain garanti élevé est un signal d'arnaque","Tester avec une petite somme","Demander une preuve par capture d'écran","Accepter si le site est en français"],0,"2 % par jour, c'est plus de 1 300 fois la mise en un an : impossible. Gain garanti + urgence = arnaque. On vérifie les listes de l'AMF.","arnaques-et-pieges"],
 ["Dans quel cas un ordre « à cours limité » d'achat à 50 € est-il exécuté ?",["Seulement si un vendeur accepte 50 € ou moins","Toujours, au prix du marché","Seulement à 50 € exactement, jamais en dessous","Seulement le lendemain"],0,"Un ordre limité fixe un prix maximum à l'achat : il est exécuté à 50 € ou moins, ou pas du tout.","passer-un-ordre"],
];

function tirer(){
  const qs=[]; const ajoute=(arr,p)=>arr.forEach(q=>qs.push(Object.assign({p},q)));
  ajoute(A_drawdown(),0); [A_support,A_bougies,A_rsi,A_base100,A_fan,A_volume].forEach(f=>ajoute(f(),0));
  mel(CALC).slice(0,10).forEach(f=>qs.push(Object.assign({p:1},f())));
  CAS.forEach(f=>qs.push(Object.assign({p:2},f())));
  mel(REGLES).slice(0,4).forEach(([e,c,b,x,ch])=>{const q=qcm(c,b);qs.push({p:3,e,t:"c",c:q.c,b:q.b,x,ch});});
  return qs;
}

const Q=tirer(), N=Q.length, debut=Date.now();
const LIBCH=window.ACA_CHAPITRES||{};
let html="",pAvant=-1;
Q.forEach((q,i)=>{
  if(q.p!==pAvant){pAvant=q.p; const k=Q.filter(z=>z.p===q.p).length; html+=`<div class="x-partie"><h2>Épreuve ${q.p+1} : ${EPR[q.p]}</h2><span>${k} questions</span></div>`;}
  const zone=q.t==="n"?`<div class="x-num"><label class="sr" for="xq${i}">Ta réponse</label><input id="xq${i}" inputmode="decimal" autocomplete="off" placeholder="Ta réponse"><span>${esc(q.u||"")}</span></div>`
    :`<div class="x-choix" role="radiogroup">${q.c.map((c,j)=>`<label><input type="radio" name="xq${i}" value="${j}"> <span>${esc(c)}</span></label>`).join("")}</div>`;
  html+=`<section class="x-q" data-i="${i}"><p class="n">Question ${i+1} sur ${N}</p>${q.svg||""}<p class="e">${q.e}</p>${zone}<div class="x-cor" hidden></div></section>`;
});
Z.innerHTML=html+`<p><button class="a-btn" type="button" id="x-fin">Rendre ma copie</button></p>`;
const barre=document.querySelector(".x-barre .p i"), cpt=document.getElementById("x-cpt"), chrono=document.getElementById("x-chrono");
const lire=(i)=>{const s=Z.querySelector(`.x-q[data-i="${i}"]`),q=Q[i];if(q.t==="n"){const v=s.querySelector("input").value.trim();return v===""?null:parseFloat(v.replace(/\s|€|%/g,"").replace(",","."));}const c=s.querySelector("input:checked");return c?+c.value:null;};
const maj=()=>{let k=0;Q.forEach((q,i)=>{const r=lire(i);const s=Z.querySelector(`.x-q[data-i="${i}"]`);s.classList.toggle("rep",r!=null&&!isNaN(r));if(r!=null&&!isNaN(r))k++;});barre.style.width=(100*k/N)+"%";cpt.textContent=k+" / "+N+" réponses";};
Z.addEventListener("input",maj); Z.addEventListener("change",maj); maj();
const tic=setInterval(()=>{const s=Math.floor((Date.now()-debut)/1000);chrono.textContent=Math.floor(s/60)+" min "+String(s%60).padStart(2,"0")+" s";},1000);
document.getElementById("x-fin").onclick=()=>{
  const manque=Q.map((q,i)=>i).filter(i=>{const r=lire(i);return r==null||isNaN(r);});
  if(manque.length){const m=document.getElementById("x-msg");m.textContent=`Il reste ${manque.length} question${manque.length>1?"s":""} sans réponse. Une réponse vide compte faux. Clique à nouveau sur « Rendre ma copie » pour corriger quand même.`;
    if(!Z.dataset.averti){Z.dataset.averti="1";Z.querySelector(`.x-q[data-i="${manque[0]}"]`).scrollIntoView({behavior:"smooth",block:"center"});return;}}
  clearInterval(tic);
  const par=[0,0,0,0],tot=[0,0,0,0],revoir=new Map();let ok=0;
  Q.forEach((q,i)=>{const s=Z.querySelector(`.x-q[data-i="${i}"]`),r=lire(i);let juste=false;tot[q.p]++;
    if(q.t==="n"){juste=r!=null&&!isNaN(r)&&Math.abs((q.abs?Math.abs(r):r)-(q.abs?Math.abs(q.rep):q.rep))<=q.tol+1e-9;}
    else {juste=r===q.b;s.querySelectorAll("label").forEach((l,j)=>{l.classList.toggle("juste",j===q.b);l.classList.toggle("faux",r===j&&j!==q.b);});}
    s.querySelectorAll("input").forEach(x=>x.disabled=true);
    if(juste){ok++;par[q.p]++;}else revoir.set(q.ch,(LIBCH[q.ch]||q.ch));
    s.classList.add(juste?"ok":"ko");
    const c=s.querySelector(".x-cor");c.hidden=false;c.innerHTML=`<b class="m">${juste?"Juste":"Faux"}${q.t==="n"?" · réponse attendue : "+nf(q.rep,2)+" "+esc(q.u||""):""}</b>${q.x} <a href="${q.ch}.html">Revoir le chapitre</a>`;});
  const seuil=Math.ceil(N*.8), parOK=par.every((v,k)=>v>=Math.ceil(tot[k]/2)), reussi=ok>=seuil&&parOK;
  const duree=Math.round((Date.now()-debut)/60000);
  const d=acaLire(); d.examen={meilleur:Math.max(ok,(d.examen||{}).v===2?(d.examen.meilleur||0):0),sur:N,v:2,reussi:reussi||(((d.examen||{}).v===2)&&d.examen.reussi)||false,date:Date.now(),essais:((d.examen||{}).essais||0)+1}; acaEcrire(d);
  document.getElementById("x-fin").hidden=true;
  const res=document.getElementById("x-resultat");
  res.innerHTML=`<h2>${reussi?"Examen réussi":"Examen pas encore réussi"} : ${ok} / ${N}</h2>
   <p>${reussi?"Bravo : tu maîtrises la lecture des graphiques, les calculs et les règles. C'est un vrai niveau.":`Il faut ${seuil} / ${N}${parOK?"":" et au moins la moitié des points dans chaque épreuve"}. Les corrections sont sous chaque question : relis la méthode, puis retente, les chiffres changeront.`} Temps : ${duree} min.</p>
   <div class="x-res">${EPR.map((n,k)=>`<div class="${par[k]>=Math.ceil(tot[k]/2)?"ok":"ko"}"><span>${n}</span><b>${par[k]} / ${tot[k]}</b></div>`).join("")}</div>
   ${revoir.size?`<p><b>Chapitres à revoir :</b> ${[...revoir].map(([id,t])=>`<a href="${id}.html">${esc(t)}</a>`).join(" · ")}</p>`:""}
   <p><button class="a-btn ghost" type="button" onclick="location.reload()">Repasser l'examen (nouveaux chiffres)</button></p>`
   +(reussi?`<div class="x-certif"><p class="muted">Certificat</p><h2>Académie Radar Bourse · niveau expert</h2><p>Ce certificat atteste que</p><p><input aria-label="Ton prénom" placeholder="Ton prénom"></p>
     <p>a réussi l'examen final (lecture de graphiques, méthodes de calcul, cas d'application, règles et pièges) avec <b>${ok} / ${N}</b>, le ${new Date().toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"})}.</p>
     <p class="muted" style="font-size:13px">Formation éducative gratuite. Ce certificat n'est pas un diplôme officiel.</p><button class="a-btn" type="button" onclick="print()">Imprimer ou enregistrer en PDF</button></div>`:"");
  res.hidden=false; res.scrollIntoView({behavior:"smooth",block:"start"});
};
})();
"""


def page_examen(seo, base, csp, chapitres, niveaux, js_progres):
    libs = {c["id"]: c["titre"] for c in chapitres}
    corps = (CSS + js_progres +
             "<div class='x-tete'><div><p class='aca-fil'><a href='../formation.html'>Académie</a> › Examen final</p>"
             "<h1>Examen final : niveau expert</h1></div></div>"
             "<p>Le dernier palier de l'Académie. Pas de questions de cours à cocher au hasard : tu lis de vrais graphiques, tu fais les calculs "
             "et tu tranches des cas concrets. Les graphiques et les chiffres changent à chaque passage.</p>"
             "<div class='x-regles'><div><b>30</b><span>questions en 4 épreuves</span></div><div><b>24 / 30</b><span>pour le certificat, et la moitié des points dans chaque épreuve</span></div>"
             "<div><b>≈ 60 min</b><span>conseillées. Calculatrice et brouillon autorisés.</span></div><div><b>Corrigé</b><span>avec la méthode pour chaque question</span></div></div>"
             "<p class='muted' style='font-size:14px'>Conseillé quand les 8 modules sont validés. Les réponses chiffrées s'écrivent avec une virgule ou un point (12,5 ou 12.5), sans le symbole.</p>"
             "<div class='x-barre'><div class='p'><i></i></div><span id='x-cpt'></span><span id='x-chrono'>0 min 00 s</span></div>"
             "<p id='x-msg' role='status' class='muted'></p><div id='x-zone'><p>Préparation de ton sujet…</p></div><div id='x-resultat' hidden></div>"
             f"<script>window.ACA_CHAPITRES={json.dumps(libs, ensure_ascii=False)};</script><script>{JS_EXAMEN}</script>")
    chemin = "formation/examen.html"
    return chemin, seo._page(base, f"Examen final Bourse niveau expert : graphiques, calculs, cas | {seo.NOM}",
                             "Examen gratuit de niveau expert : lecture de graphiques, calculs (rendement, fiscalité 2026, volatilité, levier, obligations), "
                             "cas pratiques et règles. 30 questions corrigées avec la méthode, certificat à 24 / 30.",
                             chemin, corps, None, csp=csp,
                             mots="examen bourse, test bourse difficile, quiz bourse expert, exercices calcul bourse, lecture graphique bourse exercice, certificat bourse gratuit")


# ----------------------------------------------------------------------------------------------------------------------------
# Positionnement
# ----------------------------------------------------------------------------------------------------------------------------
JS_POSITION = r"""
(function(){
const Z=document.getElementById("p-zone"); if(!Z) return;
const D=window.POS, esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const prof={}; let k=0; const rep=[];
const PROFIL=[
 ["objectif","Qu'est-ce qui t'amène ?",[["bases","Comprendre comment ça marche","Les bases, sans jargon"],["investir","Investir mon épargne sur le long terme","PEA, ETF, versements réguliers"],["analyser","Analyser des entreprises et des graphiques","Comptes, ratios, analyse technique"],["crypto","Comprendre la crypto","Bitcoin, plateformes, fiscalité"],["examen","Viser le certificat expert","Tout le programme"]]],
 ["exp","Ton expérience aujourd'hui ?",[["0","Je n'ai jamais investi",""],["1","J'ai un livret, pas encore de Bourse",""],["2","J'ai déjà acheté des actions ou des ETF",""],["3","J'investis régulièrement",""]]],
 ["temps","Combien de temps par jour pour apprendre ?",[["5","5 minutes","1 mini-leçon"],["10","10 minutes","Environ un demi-chapitre"],["20","20 minutes","Environ un chapitre"],["30","30 minutes ou plus","Plus d'un chapitre"]]],
];
function profil(i){
  if(i>=PROFIL.length){ diag(0); return; }
  const [cle,t,opts]=PROFIL[i];
  Z.innerHTML=`<div class="p-etape"><p class="muted">Étape 1 sur 3 · ton profil (${i+1}/${PROFIL.length})</p><h2>${t}</h2><div class="p-choix">${opts.map(([v,a,b])=>`<button type="button" data-v="${v}" aria-pressed="false"><b>${a}</b>${b?`<small>${b}</small>`:""}</button>`).join("")}</div></div>`;
  Z.querySelectorAll("button").forEach(b=>b.onclick=()=>{b.setAttribute("aria-pressed","true");prof[cle]=b.dataset.v;setTimeout(()=>profil(i+1),180);});
  Z.querySelector("button").focus();
}
function diag(i){
  if(i>=D.qs.length){ plan(); return; }
  const q=D.qs[i];
  Z.innerHTML=`<div class="p-etape p-q"><p class="muted">Étape 2 sur 3 · diagnostic, question ${i+1} sur ${D.qs.length} · module ${q.n} : ${esc(q.niv)}</p>
    <div class="x-q"><p class="e">${esc(q.q)}</p><div class="x-choix">${q.c.map((c,j)=>`<label><input type="radio" name="pq" value="${j}"> <span>${esc(c)}</span></label>`).join("")}<label><input type="radio" name="pq" value="-1"> <span>Je ne sais pas</span></label></div></div>
    <p><button class="a-btn" type="button" id="p-ok" disabled>Valider</button></p><div id="p-cor"></div></div>`;
  const ok=Z.querySelector("#p-ok"); Z.querySelectorAll("input").forEach(x=>x.onchange=()=>ok.disabled=false);
  ok.onclick=()=>{ const v=+Z.querySelector("input:checked").value, bon=v===q.b; rep.push({n:q.n,ok:bon});
    Z.querySelectorAll(".x-choix label").forEach((l,j)=>{l.classList.toggle("juste",j===q.b);l.classList.toggle("faux",j===v&&!bon);}); Z.querySelectorAll("input").forEach(x=>x.disabled=true);
    Z.querySelector("#p-cor").innerHTML=`<div class="x-cor"><b class="m">${bon?"Juste":v<0?"Pas de souci, c'est fait pour ça":"Pas tout à fait"}</b>${esc(q.e)}</div><p><button class="a-btn" type="button" id="p-suite">${i+1<D.qs.length?"Question suivante":"Voir mon plan"}</button></p>`;
    ok.hidden=true; const s=Z.querySelector("#p-suite"); s.focus(); s.onclick=()=>diag(i+1); };
}
function plan(){
  const par={}; rep.forEach(r=>{(par[r.n]||=[0,0])[1]++; if(r.ok) par[r.n][0]++;});
  let depart=D.niv.length+1; for(const [n] of D.niv){ if(!par[n]||par[n][0]<par[n][1]){ depart=n; break; } }
  if(+prof.exp===0) depart=1;   // jamais investi : on commence au début, même avec de la chance au diagnostic
  const total=rep.filter(r=>r.ok).length;
  const ordre=(D.objectifs[prof.objectif]||[]).filter(id=>!D.module_de[id]||D.module_de[id]>=depart);
  const restants=D.chapitres.filter(c=>c.n>=depart);
  const minutes=restants.reduce((s,c)=>s+c.m,0), parJour=+prof.temps||10, jours=Math.ceil(minutes/parJour);
  const fin=new Date(Date.now()+jours*864e5).toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"});
  const premier=ordre.length?D.chapitres.find(c=>c.id===ordre[0]):restants[0];
  const d=acaLire(); d.niveau_test={depart,total,date:Date.now()}; d.profil=Object.assign({},prof,{date:Date.now()}); d.plan={ordre,minutes,parJour,fin,premier:premier&&premier.id}; acaEcrire(d);
  const libO={bases:"comprendre les bases",investir:"investir sur le long terme",analyser:"analyser entreprises et graphiques",crypto:"comprendre la crypto",examen:"viser le certificat expert"}[prof.objectif]||"";
  Z.innerHTML=`<div class="p-etape p-plan"><p class="muted">Étape 3 sur 3 · ton plan</p>
    <h2>${depart>D.niv.length?"Tu maîtrises déjà l'essentiel du programme":`Ton point de départ : module ${depart}, ${esc((D.niv.find(x=>x[0]===depart)||[0,""])[1])}`}</h2>
    <p>${total} bonnes réponses sur ${rep.length}. ${depart>1&&depart<=D.niv.length?`Les modules 1 à ${depart-1} sont débloqués : tu peux les survoler ou faire seulement leurs bilans.`:""}</p>
    <div class="p-niv">${D.niv.map(([n,nom])=>{const p=par[n]||[0,2];return `<div><span>Module ${n} · ${esc(nom)}</span><span class="b"><i data-w="${Math.round(100*p[0]/p[1])}"></i></span><b>${p[0]} / ${p[1]}</b></div>`;}).join("")}</div>
    <div class="a-carte" style="display:block;margin:16px 0"><h3 style="margin-top:0">Ton rythme : ${parJour} min par jour</h3>
      <p>Il te reste environ <b>${Math.round(minutes/60)} h</b> de leçons. À ce rythme, tu auras fini le programme vers le <b>${fin}</b>, puis l'examen expert.</p>
      ${ordre.length?`<p>Pour ton objectif (<b>${libO}</b>), commence par ces chapitres, dans cet ordre :</p><ol>${ordre.slice(0,8).map(id=>{const c=D.chapitres.find(x=>x.id===id);return c?`<li><a href="${id}.html">${esc(c.t)}</a> <span class="muted">· ${c.m} min</span></li>`:"";}).join("")}</ol>`:""}</div>
    <p>${premier?`<a class="a-btn" href="${premier.id}.html">Commencer : ${esc(premier.t)}</a> `:`<a class="a-btn" href="examen.html">Passer l'examen expert</a> `}<a class="a-btn ghost" href="../formation.html">Voir tout le programme</a></p>
    <p class="muted" style="font-size:13.5px">Ton plan est gardé dans ce navigateur. Tu peux refaire ce questionnaire quand tu veux.</p></div>`;
  requestAnimationFrame(()=>Z.querySelectorAll(".p-niv i").forEach(i=>i.style.width=i.dataset.w+"%"));
  Z.querySelector(".a-btn").focus();
}
document.getElementById("p-go").onclick=()=>{document.getElementById("p-intro").hidden=true;profil(0);};
if(/[?&]go=1/.test(location.search)){document.getElementById("p-intro").hidden=true;profil(0);}
})();
"""


def page_positionnement(seo, base, csp, chapitres, niveaux, objectifs, js_progres):
    qs = []
    for n, nom, *_ in niveaux:
        chs = [c for c in chapitres if c["niveau"] == n and not c.get("cas")]
        for c in chs[:2]:
            q, choix, b, e = c["quiz"][0]
            qs.append(dict(n=n, niv=nom, q=q, c=choix, b=b, e=e))
    regs = [c for c in chapitres if not c.get("cas")]
    from .academie import _min
    cle_obj = {"bases": 0, "investir": 1, "analyser": 2, "crypto": 3}
    obj = {k: objectifs[i][2] for k, i in cle_obj.items() if i < len(objectifs)}
    # objectifs du questionnaire : on retrouve la liste la plus proche dans les raccourcis du programme, par mots-clés
    for k, mots in (("analyser", ("analys", "entreprise", "graph")), ("crypto", ("crypto", "bitcoin")), ("investir", ("pea", "etf", "long")), ("bases", ("zéro", "zero", "début"))):
        for t, d, ids in objectifs:
            if any(m in (t + d).lower() for m in mots):
                obj[k] = ids
                break
    obj["examen"] = [c["id"] for c in regs]
    donnees = {"qs": qs, "niv": [[n, nom] for n, nom, *_ in niveaux], "objectifs": obj,
               "module_de": {c["id"]: c["niveau"] for c in chapitres},
               "chapitres": [{"id": c["id"], "t": c["titre"], "n": c["niveau"], "m": _min(c)} for c in regs]}
    corps = (CSS + js_progres +
             "<p class='aca-fil'><a href='../formation.html'>Académie</a> › Questionnaire de départ</p>"
             "<h1>Par où commencer ? Ton plan en 5 minutes</h1>"
             "<div id='p-intro'><p>Trois questions sur toi, puis un diagnostic d'une question à la fois, des bases jusqu'aux notions avancées. "
             f"À la fin, tu obtiens ton point de départ, ton niveau dans chacun des {len(niveaux)} modules, les chapitres à faire en premier pour ton objectif "
             "et la date à laquelle tu auras fini à ton rythme.</p>"
             "<div class='x-regles'><div><b>3</b><span>questions de profil</span></div>"
             f"<div><b>{len(qs)}</b><span>questions de diagnostic, avec « je ne sais pas »</span></div><div><b>1</b><span>plan personnel, gardé dans ton navigateur</span></div></div>"
             "<p><button class='a-btn' type='button' id='p-go'>Commencer le questionnaire</button></p></div>"
             f"<div id='p-zone' aria-live='polite'></div><script>window.POS={json.dumps(donnees, ensure_ascii=False)};</script><script>{JS_POSITION}</script>")
    chemin = "formation/test-de-niveau.html"
    return chemin, seo._page(base, f"Test de niveau en Bourse : par où commencer ? | {seo.NOM}",
                             f"Questionnaire gratuit : ton profil, {len(qs)} questions de diagnostic et un plan personnel pour apprendre la Bourse à ton rythme.",
                             chemin, corps, None, csp=csp, mots="test niveau bourse, test connaissances bourse, quiz bourse débutant, par où commencer la bourse")
