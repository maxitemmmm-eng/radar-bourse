"""Version 81 : le graphique interactif des fiches (actions, ETF, cryptos).

- Périodes (1 mois → tout), courbe ou bougies, volumes, moyennes 50 / 200 jours.
- Réticule : date, prix, variation, au doigt ou à la souris (et au clavier : flèches gauche / droite).
- L'éventail de la prévision du mois prochain (8 fois sur 10 / 1 fois sur 2 / le plus probable).
- Les prévisions passées de l'IA posées sur la courbe : la fourchette annoncée et le prix réel un mois plus tard,
  en vert si le prix est tombé dedans, en rouge sinon. C'est ce qui permet de juger l'IA sur pièces.
Sans JavaScript, le graphique fixe (courbe_svg) reste affiché : rien ne se perd pour Google.
"""
from __future__ import annotations

import json
import os

FICHIER_JS = "graphique-pro.js"

CSS = """
.gp{margin:18px 0 8px;border:1px solid var(--line);border-radius:14px;background:var(--surface);overflow:hidden}
.gp-tete{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:flex-end;justify-content:space-between;padding:14px 16px 6px}
.gp-prix{font-family:var(--m);font-variant-numeric:tabular-nums}
.gp-prix b{font-size:24px;font-weight:600;display:block;line-height:1.1}.gp-prix span{font-size:13.5px;color:var(--muted)}
.gp-prix .up{color:var(--up)}.gp-prix .down{color:var(--down)}
.gp-barre{display:flex;flex-wrap:wrap;gap:6px}
.gp-groupe{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.gp-groupe button{font:inherit;font-size:13px;font-weight:600;padding:5px 10px;border:0;background:transparent;color:var(--muted);cursor:pointer}
.gp-groupe button+button{border-left:1px solid var(--line)}
.gp-groupe button[aria-pressed=true]{background:var(--ink);color:var(--surface)}
.gp-groupe button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.gp-zone{position:relative;touch-action:pan-y}
.gp-zone svg{display:block;width:100%;height:auto;user-select:none}
.gp-zone:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.gp-bulle{position:absolute;top:8px;pointer-events:none;background:var(--ink);color:var(--surface);border-radius:9px;padding:7px 10px;font-size:12.5px;line-height:1.45;
  white-space:nowrap;box-shadow:0 8px 22px rgba(0,0,0,.25);opacity:0;transition:opacity .12s}
.gp-bulle b{font-family:var(--m);font-weight:600}
.gp-legende{display:flex;flex-wrap:wrap;gap:6px 16px;padding:8px 16px 12px;font-size:12.5px;color:var(--muted)}
.gp-legende i{display:inline-block;width:14px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.gp-fiab{padding:10px 16px 14px;border-top:1px solid var(--line);font-size:14px}
.gp-fiab b{font-family:var(--m)}
.gp svg .ax{fill:var(--muted);font-size:11px;font-family:var(--m)}
.gp svg .gr{stroke:var(--line);stroke-width:1}
.gp svg .ln{fill:none;stroke:var(--accent);stroke-width:2;stroke-linejoin:round}
.gp svg .ar{opacity:.18}
.gp svg .m50{fill:none;stroke:#e0a43a;stroke-width:1.4;opacity:.9}.gp svg .m200{fill:none;stroke:#b07cff;stroke-width:1.4;opacity:.9}
.gp svg .vol{opacity:.35}
.gp svg .futur{fill:var(--surface-2);opacity:.6}
.gp svg .f80{opacity:.16}.gp svg .f50{opacity:.3}.gp svg .fmed{fill:none;stroke-width:2;stroke-dasharray:5 5}
.gp svg .auj{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 4}
.gp svg .ret{stroke:var(--muted);stroke-width:1}
.gp svg .lab{font-size:11.5px;font-family:var(--m);font-weight:600}
.gp svg .pas-ok{stroke:var(--up)}.gp svg .pas-ko{stroke:var(--down)}
@media (prefers-reduced-motion:no-preference){.gp svg .anim{stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:gp-trace 1s ease-out forwards}
  @keyframes gp-trace{to{stroke-dashoffset:0}}.gp svg .fondu{animation:gp-fondu .6s ease-out .5s both}@keyframes gp-fondu{from{opacity:0}}}
@media (max-width:600px){.gp-prix b{font-size:20px}.gp-groupe button{padding:5px 8px}}
"""

JS = r"""
(function(){
"use strict";
var NS="http://www.w3.org/2000/svg";
function el(n,a,p){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function fmtPrix(v,dev){if(v==null||!isFinite(v))return"–";var d=Math.abs(v)>=1000?0:Math.abs(v)>=1?2:Math.abs(v)>=0.01?4:6;
  var s=v.toLocaleString("fr-FR",{minimumFractionDigits:d,maximumFractionDigits:d});return s+(dev==="EUR"?" €":dev==="USD"?" $":" "+dev);}
function fmtPct(v){return(v>=0?"+":"")+(v*100).toLocaleString("fr-FR",{maximumFractionDigits:2,minimumFractionDigits:2})+" %";}
var MOIS=["janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."];
function fmtDate(s,court){var p=s.split("-");return court?(+p[2])+" "+MOIS[+p[1]-1]:(+p[2])+" "+MOIS[+p[1]-1]+" "+p[0];}
function init(fig){
  var D;try{D=JSON.parse(fig.querySelector(".gp-data").textContent);}catch(e){return;}
  var S=D.serie,n=S.c.length;if(n<20)return;
  var zone=fig.querySelector(".gp-zone"),bulle=fig.querySelector(".gp-bulle"),prixEl=fig.querySelector(".gp-prix");
  var etat={periode:D.periode||126,type:"ligne",moy:false,prev:true,passes:true,curseur:null};
  var aOHLC=S.o&&S.h&&S.l&&S.o.length===n;
  if(!aOHLC){var bt=fig.querySelector("[data-type=bougies]");if(bt)bt.remove();}
  if(!(S.sma50&&S.sma50.some(function(v){return v!=null;}))){var bm=fig.querySelector("[data-opt=moy]");if(bm)bm.remove();}
  if(!(D.passes&&D.passes.length)){var bp=fig.querySelector("[data-opt=passes]");if(bp)bp.remove();}
  var premier=true,geo=null;
  function entete(i){var c=S.c,j=i==null?n-1:i,v=c[j],ref=j>0?c[j-1]:null;
    var hors=i==null;var debut=c[Math.max(0,n-etat.periode)];
    var varTxt=hors?(debut?fmtPct(v/debut-1)+" sur la période":""):(ref?fmtPct(v/ref-1)+" sur la séance":"");
    var cls=hors?(v>=debut?"up":"down"):(v>=ref?"up":"down");
    prixEl.innerHTML="<b>"+fmtPrix(v,D.devise)+"</b><span><span class='"+cls+"'>"+varTxt+"</span> · "+fmtDate(S.t[j])+"</span>";}
  function dessiner(){
    var W=Math.max(320,zone.clientWidth||700),H=W<560?300:380,pl=8,pr=W<560?62:78,pt=16,pb=26;
    var hv=etat.type==="bougies"||S.v?Math.round(H*0.16):0;
    var i0=Math.max(0,n-etat.periode),idx=[];for(var i=i0;i<n;i++)idx.push(i);
    var cone=etat.prev&&D.cone&&D.cone.mediane?D.cone:null,nf=cone?cone.mediane.length-1:0;
    var total=idx.length-1+nf,X=function(k){return pl+(W-pl-pr)*k/Math.max(1,total);};
    var vals=[];idx.forEach(function(i){vals.push(S.c[i]);if(etat.type==="bougies"&&aOHLC){vals.push(S.h[i],S.l[i]);}
      if(etat.moy){if(S.sma50&&S.sma50[i]!=null)vals.push(S.sma50[i]);if(S.sma200&&S.sma200[i]!=null)vals.push(S.sma200[i]);}});
    if(cone){vals=vals.concat(cone.haut,cone.bas);}
    var pas=etat.passes&&D.passes?D.passes.filter(function(p){return p.i1>=i0;}):[];
    pas.forEach(function(p){vals.push(p.bas,p.haut);});
    vals=vals.filter(function(v){return v!=null&&isFinite(v);});
    var lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals),m=(hi-lo)*0.06||hi*0.02;lo-=m;hi+=m;
    var yb=H-pb-hv,Y=function(v){return pt+(yb-pt)*(1-(v-lo)/(hi-lo));};
    zone.innerHTML="";var svg=el("svg",{viewBox:"0 0 "+W+" "+H,role:"img","aria-label":D.titre});zone.appendChild(svg);zone.appendChild(bulle);
    var defs=el("defs",{},svg),g1=el("linearGradient",{id:"gpg"+D.id,x1:0,y1:0,x2:0,y2:1},defs);
    el("stop",{offset:"0","stop-color":"var(--accent)","stop-opacity":"1"},g1);el("stop",{offset:"1","stop-color":"var(--accent)","stop-opacity":"0"},g1);
    for(var q=0;q<=4;q++){var v=lo+(hi-lo)*q/4,y=Y(v);el("line",{x1:pl,x2:W-pr,y1:y,y2:y,"class":"gr"},svg);
      var tx=el("text",{x:W-pr+6,y:y+4,"class":"ax"},svg);tx.textContent=fmtPrix(v,D.devise);}
    var nbD=W<560?3:5;for(var q2=0;q2<nbD;q2++){var k=Math.round((idx.length-1)*q2/(nbD-1)),t=el("text",{x:X(k),y:H-8,"class":"ax","text-anchor":q2===0?"start":q2===nbD-1?"end":"middle"},svg);t.textContent=fmtDate(S.t[idx[k]],true);}
    var xAuj=X(idx.length-1);
    if(cone){el("rect",{x:xAuj,y:pt,width:W-pr-xAuj,height:yb-pt,"class":"futur"},svg);}
    if(hv&&S.v){var vmax=Math.max.apply(null,idx.map(function(i){return S.v[i]||0;}))||1,bw=Math.max(1,(W-pl-pr)/Math.max(1,total)*0.7);
      idx.forEach(function(i,k){var vv=S.v[i]||0,h=(hv-6)*vv/vmax,up=k===0||S.c[i]>=S.c[idx[k-1]];
        el("rect",{x:X(k)-bw/2,y:H-pb-h,width:bw,height:h,"class":"vol",fill:up?"var(--up)":"var(--down)"},svg);});}
    if(etat.moy){[["sma50","m50"],["sma200","m200"]].forEach(function(p){var a=S[p[0]];if(!a)return;var d="";idx.forEach(function(i,k){if(a[i]!=null)d+=(d?" L":"M")+X(k).toFixed(1)+","+Y(a[i]).toFixed(1);});
      if(d)el("path",{d:d,"class":p[1]},svg);});}
    var coul=D.sens>0?"var(--up)":D.sens<0?"var(--down)":"var(--muted)";
    if(etat.type==="bougies"&&aOHLC){var cw=Math.max(1.5,(W-pl-pr)/Math.max(1,total)*0.62);
      idx.forEach(function(i,k){var up=S.c[i]>=S.o[i],c=up?"var(--up)":"var(--down)",x=X(k);
        el("line",{x1:x,x2:x,y1:Y(S.h[i]),y2:Y(S.l[i]),stroke:c,"stroke-width":1},svg);
        var y1=Y(Math.max(S.o[i],S.c[i])),y2=Y(Math.min(S.o[i],S.c[i]));el("rect",{x:x-cw/2,y:y1,width:cw,height:Math.max(1,y2-y1),fill:c},svg);});}
    else{var d="";idx.forEach(function(i,k){d+=(k?" L":"M")+X(k).toFixed(1)+","+Y(S.c[i]).toFixed(1);});
      el("path",{d:d+" L"+xAuj.toFixed(1)+","+yb+" L"+X(0).toFixed(1)+","+yb+" Z",fill:"url(#gpg"+D.id+")","class":"ar"},svg);
      var ln=el("path",{d:d,"class":"ln"+(premier?" anim":"")},svg);if(premier){try{ln.style.setProperty("--l",Math.ceil(ln.getTotalLength()));}catch(e){}}}
    if(cone){var fx=function(j){return X(idx.length-1+j);},r50=0.6745/1.2816;
      var h50=cone.haut.map(function(v,j){var m=cone.mediane[j];return m*Math.pow(v/m,r50);}),b50=cone.bas.map(function(v,j){var m=cone.mediane[j];return m*Math.pow(v/m,r50);});
      function poly(a,b){var s="M";a.forEach(function(v,j){s+=(j?" L":"")+fx(j).toFixed(1)+","+Y(v).toFixed(1);});for(var j=b.length-1;j>=0;j--)s+=" L"+fx(j).toFixed(1)+","+Y(b[j]).toFixed(1);return s+" Z";}
      var gF=el("g",{"class":premier?"fondu":""},svg);
      el("path",{d:poly(cone.haut,cone.bas),fill:coul,"class":"f80"},gF);el("path",{d:poly(h50,b50),fill:coul,"class":"f50"},gF);
      var dm="";cone.mediane.forEach(function(v,j){dm+=(j?" L":"M")+fx(j).toFixed(1)+","+Y(v).toFixed(1);});el("path",{d:dm,stroke:coul,"class":"fmed"},gF);
      var L=cone.mediane.length-1,etq=[[Y(cone.haut[L]),cone.haut[L]],[Y(cone.mediane[L]),cone.mediane[L]],[Y(cone.bas[L]),cone.bas[L]]];
      if(etq[1][0]-etq[0][0]<15)etq[0][0]=etq[1][0]-15;if(etq[2][0]-etq[1][0]<15)etq[2][0]=etq[1][0]+15;
      etq.forEach(function(e,k){var tt=el("text",{x:fx(L)-4,y:e[0]+(k===0?-4:k===2?12:-7),"class":"lab","text-anchor":"end",fill:k===1?coul:"var(--muted)"},gF);tt.textContent=fmtPrix(e[1],D.devise);});}
    el("line",{x1:xAuj,x2:xAuj,y1:pt,y2:yb,"class":"auj"},svg);
    el("circle",{cx:xAuj,cy:Y(S.c[n-1]),r:4.5,fill:"var(--accent)",stroke:"var(--surface)","stroke-width":2},svg);
    var gP=el("g",{"class":premier?"fondu":""},svg);
    pas.forEach(function(p){var k=p.i1-i0,x=X(k),cls=p.dans?"pas-ok":"pas-ko";
      el("line",{x1:x,x2:x,y1:Y(p.haut),y2:Y(p.bas),"class":cls,"stroke-width":3,"stroke-linecap":"round",opacity:.75},gP);
      el("line",{x1:x-5,x2:x+5,y1:Y(p.haut),y2:Y(p.haut),"class":cls,"stroke-width":2},gP);el("line",{x1:x-5,x2:x+5,y1:Y(p.bas),y2:Y(p.bas),"class":cls,"stroke-width":2},gP);
      el("circle",{cx:x,cy:Y(p.pf),r:3.5,fill:p.dans?"var(--up)":"var(--down)",stroke:"var(--surface)","stroke-width":1.5},gP);});
    var ret=el("line",{x1:0,x2:0,y1:pt,y2:H-pb,"class":"ret",opacity:0},svg),pt0=el("circle",{r:4,fill:"var(--ink)",opacity:0},svg);
    geo={X:X,Y:Y,idx:idx,i0:i0,total:total,W:W,H:H,pl:pl,pr:pr,ret:ret,pt0:pt0,cone:cone,pas:pas,svg:svg};
    premier=false;entete(null);
  }
  function montrer(k){if(!geo)return;var g=geo,ki=Math.max(0,Math.min(g.total,k)),x=g.X(ki),hist=ki<=g.idx.length-1,txt;
    if(hist){var i=g.idx[ki],v=S.c[i];g.pt0.setAttribute("cx",x);g.pt0.setAttribute("cy",g.Y(v));g.pt0.setAttribute("opacity",1);entete(i);
      txt="<b>"+fmtPrix(v,D.devise)+"</b><br>"+fmtDate(S.t[i]);
      if(etat.type==="bougies"&&aOHLC)txt+="<br>Ouv. "+fmtPrix(S.o[i],D.devise)+" · Haut "+fmtPrix(S.h[i],D.devise)+" · Bas "+fmtPrix(S.l[i],D.devise);
      var pp=g.pas.filter(function(p){return Math.abs(p.i1-i)<=1;})[0];
      if(pp)txt+="<br><span style='opacity:.85'>Prévu le "+fmtDate(pp.d0,true)+" : entre "+fmtPrix(pp.bas,D.devise)+" et "+fmtPrix(pp.haut,D.devise)+"</span><br>"+(pp.dans?"✓ prix tombé dans la fourchette":"✗ prix sorti de la fourchette");}
    else{var j=ki-(g.idx.length-1),c=g.cone;g.pt0.setAttribute("opacity",0);entete(null);
      txt="<b>Dans "+j+" séance"+(j>1?"s":"")+"</b> ("+fmtDate(c.t[j],true)+")<br>8 fois sur 10 entre "+fmtPrix(c.bas[j],D.devise)+" et "+fmtPrix(c.haut[j],D.devise)+"<br>Le plus probable : "+fmtPrix(c.mediane[j],D.devise);}
    g.ret.setAttribute("x1",x);g.ret.setAttribute("x2",x);g.ret.setAttribute("opacity",1);
    bulle.innerHTML=txt;bulle.style.opacity=1;var bw=bulle.offsetWidth,zw=zone.clientWidth,px=x*zw/g.W;
    bulle.style.left=Math.max(4,Math.min(zw-bw-4,px+(px>zw/2?-bw-12:12)))+"px";etat.curseur=ki;}
  function cacher(){if(!geo)return;geo.ret.setAttribute("opacity",0);geo.pt0.setAttribute("opacity",0);bulle.style.opacity=0;etat.curseur=null;entete(null);}
  function kDepuis(ev){var r=zone.getBoundingClientRect(),cx=(ev.touches?ev.touches[0].clientX:ev.clientX)-r.left,x=cx*geo.W/r.width;
    return Math.round((x-geo.pl)/(geo.W-geo.pl-geo.pr)*geo.total);}
  zone.addEventListener("pointermove",function(e){if(geo)montrer(kDepuis(e));});
  zone.addEventListener("pointerleave",cacher);
  zone.addEventListener("touchmove",function(e){if(geo)montrer(kDepuis(e));},{passive:true});
  zone.addEventListener("keydown",function(e){if(!geo)return;var k=etat.curseur==null?geo.idx.length-1:etat.curseur;
    if(e.key==="ArrowLeft"){montrer(k-1);e.preventDefault();}else if(e.key==="ArrowRight"){montrer(k+1);e.preventDefault();}else if(e.key==="Escape")cacher();});
  zone.addEventListener("blur",cacher);
  fig.querySelectorAll("[data-periode]").forEach(function(b){b.addEventListener("click",function(){etat.periode=+b.dataset.periode;
    fig.querySelectorAll("[data-periode]").forEach(function(x){x.setAttribute("aria-pressed",x===b?"true":"false");});dessiner();});});
  fig.querySelectorAll("[data-type]").forEach(function(b){b.addEventListener("click",function(){etat.type=b.dataset.type;
    fig.querySelectorAll("[data-type]").forEach(function(x){x.setAttribute("aria-pressed",x===b?"true":"false");});dessiner();});});
  fig.querySelectorAll("[data-opt]").forEach(function(b){b.addEventListener("click",function(){var o=b.dataset.opt;etat[o]=!etat[o];b.setAttribute("aria-pressed",etat[o]?"true":"false");
    var lg=fig.querySelector("[data-leg="+o+"]");if(lg)lg.hidden=!etat[o];dessiner();});});
  var rt;window.addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(dessiner,150);});
  fig.querySelector(".gp-barre").hidden=false;dessiner();
}
function go(){document.querySelectorAll("figure.gp").forEach(init);}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
})();
"""


def ecrire_js(dossier: str) -> None:
    with open(os.path.join(dossier, FICHIER_JS), "w", encoding="utf-8") as f:
        f.write(JS)


_HIST = {}


def _historique():
    """Les prévisions enregistrées (historique/predictions.csv), lues une seule fois."""
    if "df" not in _HIST:
        try:
            import pandas as pd
            from . import config
            _HIST["df"] = pd.read_csv(os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv"))
        except Exception:
            _HIST["df"] = None
    return _HIST["df"]


def passes(t: dict, horizon: int) -> list:
    """Prévisions passées de ce titre dont le résultat est connu dans la série affichée (une toutes les ~2 semaines)."""
    df = _historique()
    s = t.get("serie") or {}
    dates, c = s.get("t") or [], s.get("c") or []
    if df is None or not dates:
        return []
    pos = {d: i for i, d in enumerate(dates)}
    out, dernier = [], -99
    lignes = df[df["ticker"] == t.get("ticker")].sort_values("date")
    for r in lignes.itertuples(index=False):
        d0 = str(r.date)[:10]
        i = pos.get(d0)
        if i is None or i + horizon >= len(dates) or i - dernier < 10:
            continue
        try:
            bas, haut, p0 = float(r.bas), float(r.haut), float(r.prix)
        except (TypeError, ValueError):
            continue
        pf = c[i + horizon]
        if pf is None or not (bas == bas and haut == haut) or bas <= 0:
            continue
        proba = float(r.proba) if r.proba == r.proba else None
        out.append({"d0": d0, "i1": i + horizon, "bas": round(bas, 6), "haut": round(haut, 6), "pf": pf, "dans": bool(bas <= pf <= haut),
                    "juste": (proba > 0.5) == (pf > p0) if proba is not None else None})
        dernier = i
    return out


def stats_globales(payload: dict, horizon: int) -> dict:
    """Taux de fourchettes tenues sur toutes les prévisions vérifiables (tous titres), calculé une fois."""
    if "stats" in _HIST:
        return _HIST["stats"]
    n = k = 0
    for t in payload.get("titres", []):
        for p in passes(t, horizon):
            n += 1
            k += p["dans"]
    _HIST["stats"] = {"n": n, "k": k}
    return _HIST["stats"]


def bloc(t: dict, svg_fixe: str, horizon: int, stats: dict | None = None, sens: int = 0) -> str:
    s = t.get("serie") or {}
    n = len(s.get("c") or [])
    if n < 30 or not svg_fixe:
        return svg_fixe
    ps = passes(t, horizon)
    garder = ("t", "o", "h", "l", "c", "v", "sma50", "sma200")
    data = {"id": abs(hash(t.get("ticker"))) % 100000, "titre": f"Cours de {t.get('nom')} et prévision de l'IA", "devise": t.get("devise", ""),
            "serie": {k: s[k] for k in garder if s.get(k)}, "cone": {k: (t.get("cone") or {}).get(k) for k in ("t", "bas", "mediane", "haut")} if t.get("cone") else None,
            "passes": ps, "sens": sens, "periode": min(126, n)}
    donnees = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    periodes = [(p, lib) for p, lib in ((21, "1M"), (63, "3M"), (126, "6M"), (252, "1A"), (n, "Tout")) if p <= n or lib == "Tout"]
    if n < 252:
        periodes = [x for x in periodes if x[1] != "1A"]
    btn_p = "".join(f"<button type='button' data-periode='{p}' aria-pressed='{'true' if p == min(126, n) else 'false'}'>{lib}</button>" for p, lib in periodes)
    k_ok = sum(p["dans"] for p in ps)
    fiab_titre = (f"Sur ce titre : <b>{k_ok} sur {len(ps)}</b> prévisions vérifiées sont tombées dans la fourchette annoncée (traits verts sur la courbe ; "
                  "en rouge, celles qui en sont sorties). ") if ps else "Les prévisions de l'IA sur ce titre seront posées sur la courbe dès qu'elles pourront être vérifiées (un mois après). "
    st = stats or {}
    fiab_glob = (f"Tous titres confondus : <b>{round(st['k'] / st['n'] * 100)} %</b> de fourchettes tenues sur {st['n']} vérifiées, pour un objectif de 80 %. "
                 if st.get("n", 0) >= 30 else "")
    return (f"<figure class='gp' aria-label='Graphique interactif du cours'><div class='gp-tete'><div class='gp-prix' aria-live='polite'></div>"
            f"<div class='gp-barre' hidden><span class='gp-groupe' role='group' aria-label='Période'>{btn_p}</span>"
            "<span class='gp-groupe' role='group' aria-label='Type de graphique'><button type='button' data-type='ligne' aria-pressed='true'>Courbe</button>"
            "<button type='button' data-type='bougies' aria-pressed='false'>Bougies</button></span>"
            "<span class='gp-groupe' role='group' aria-label='Affichage'><button type='button' data-opt='prev' aria-pressed='true'>Prévision</button>"
            "<button type='button' data-opt='passes' aria-pressed='true'>Vérifications</button>"
            "<button type='button' data-opt='moy' aria-pressed='false'>Moyennes</button></span></div></div>"
            f"<div class='gp-zone' tabindex='0' aria-label='Graphique : déplace-toi avec les flèches gauche et droite'>{svg_fixe}<div class='gp-bulle' aria-hidden='true'></div></div>"
            "<div class='gp-legende'><span><i style='background:var(--accent)'></i>Cours</span>"
            "<span data-leg='prev'><i style='background:currentColor;opacity:.3'></i>Prévision : 8 fois sur 10 (clair), 1 fois sur 2 (foncé), pointillés = le plus probable</span>"
            "<span data-leg='passes'><i style='background:var(--up)'></i>Prévision passée tenue <i style='background:var(--down);margin-left:8px'></i>non tenue</span>"
            "<span data-leg='moy' hidden><i style='background:#e0a43a'></i>Moyenne 50 jours <i style='background:#b07cff;margin-left:8px'></i>200 jours</span></div>"
            f"<p class='gp-fiab'>{fiab_titre}{fiab_glob}<a href='../resultats.html'>Toutes les vérifications</a></p>"
            f"<script type='application/json' class='gp-data'>{donnees}</script></figure>")
