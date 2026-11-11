"""Version 70 : l'Académie Radar Bourse, centre de formation gratuit pour débutants.

5 niveaux, 27 chapitres, des bases jusqu'à l'investissement maîtrisé. Chaque chapitre : cours, « à retenir », quiz corrigé,
exercice avec correction, sources vérifiées. Progression gardée dans le navigateur (aucun compte), examen final et certificat.
Pages : formation.html (la carte des niveaux), formation/<chapitre>.html, formation/examen.html.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from .formation_cours_1 import COURS_1, COURS_2
from .formation_cours_2 import COURS_3, COURS_4, COURS_5
from .formation_cours_3 import COURS_6
from .formation_cours_4 import COURS_7, EXOS_7
from . import formation_exos as _fx
_fx.EXOS.update(EXOS_7)

CHAPITRES = COURS_1 + COURS_2 + COURS_3 + COURS_4 + COURS_5 + COURS_6 + COURS_7

NIVEAUX = [
    (1, "Les bases", "Comprendre ce qu'est la Bourse, sans aucun prérequis.", "#3f7be0"),
    (2, "Passer à l'action", "Ouvrir un compte, passer un ordre, choisir un ETF.", "#1f9d6b"),
    (3, "Analyser une entreprise", "Lire les comptes, les ratios, les dividendes et l'actualité.", "#b7791f"),
    (4, "Lire le marché", "Graphiques, volatilité, taux d'intérêt et krachs.", "#8b5cf6"),
    (5, "Investir comme un pro", "Diversifier, construire un portefeuille, fiscalité, psychologie.", "#d4495a"),
    (6, "Comprendre la crypto", "Blockchain, stablecoins, sécurité, fiscalité crypto 2026.", "#0ea5a4"),
    (7, "Aller plus loin", "Obligations, devises, secteurs, opérations sur actions, levier, documents réglementaires.", "#7c3aed"),
]
VERIFIE_LE = "11 novembre 2026"
MOTS_ACADEMIE = ("apprendre la bourse, bourse pour débutant, formation bourse gratuite, cours de bourse débutant, comment investir en bourse, "
                 "investir en bourse débutant, débuter en bourse, quiz bourse, exercices bourse, formation investissement gratuite, "
                 "comprendre la bourse, bourse expliquée simplement, apprendre à investir, éducation financière, "
                 "apprendre la crypto, formation crypto gratuite, crypto pour débutant, comprendre le bitcoin, cours d'analyse technique, "
                 "lire un graphique boursier, cours finance gratuit, formation trading débutant")

CSS = """
.aca-hero{padding:8px 0 4px}.aca-hero h1{margin-bottom:6px}
.aca-methode{list-style:none;counter-reset:m;padding:0;margin:16px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.aca-methode li{counter-increment:m;padding:12px 14px 12px 48px;border-radius:12px;background:var(--surface-2);position:relative}
.aca-methode li::before{content:counter(m);position:absolute;left:14px;top:12px;width:24px;height:24px;border-radius:50%;background:var(--accent);color:var(--surface);display:grid;place-items:center;font-weight:800;font-size:13px}
.aca-methode b{display:block}.aca-methode span{font-size:14px;color:var(--muted)}
.aca-barre{display:flex;flex-wrap:wrap;gap:12px 22px;align-items:center;margin:16px 0 4px;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.aca-barre b{font-size:22px}.aca-barre .lbl{font-size:13px;color:var(--muted);display:block}
.aca-prog{flex:1 1 220px;height:10px;border-radius:99px;background:var(--surface-2);overflow:hidden;min-width:160px}
.aca-prog i{display:block;height:100%;width:0;background:linear-gradient(90deg,#3f7be0,#1f9d6b);border-radius:99px;transition:width .8s cubic-bezier(.2,.8,.2,1)}
.aca-niveaux{display:grid;gap:18px;margin:22px 0}
.aca-niv{border:1px solid var(--line);border-radius:16px;background:var(--surface);padding:18px 18px 14px;position:relative;overflow:hidden}
.aca-niv::before{content:"";position:absolute;inset:0 auto 0 0;width:5px;background:var(--c)}
.aca-niv header{display:flex;gap:14px;align-items:center;margin-bottom:10px}
.aca-num{flex:none;width:46px;height:46px;border-radius:12px;display:grid;place-items:center;font-weight:800;font-size:20px;color:#fff;background:var(--c)}
.aca-niv h2{margin:0;font-size:21px}.aca-niv header p{margin:2px 0 0;color:var(--muted);font-size:14px}
.aca-chaps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px}
.aca-chaps a{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:10px;border:1px solid var(--line);text-decoration:none;color:var(--ink);background:var(--bg)}
.aca-chaps a:hover{border-color:var(--c)}
.aca-etat{flex:none;width:24px;height:24px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;font-size:13px;font-weight:800}
.aca-chaps a.fait .aca-etat{background:var(--c);border-color:var(--c);color:#fff}
.aca-chaps small{display:block;color:var(--muted);font-size:12.5px}.aca-chaps a.encours .aca-etat{border-color:var(--c)}.aca-chaps a.encours small{color:var(--ink)}
.aca-badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.aca-badge{padding:6px 10px;border-radius:99px;border:1px dashed var(--line);font-size:13px;color:var(--muted)}
.aca-badge.ok{border-style:solid;border-color:#1f9d6b;color:var(--ink);background:color-mix(in srgb,#1f9d6b 14%,transparent)}
.aca-fil{font-size:13.5px;color:var(--muted);margin:4px 0 0}
.aca-cours h2{margin-top:28px}
.aca-retenir{border:1px solid var(--line);border-left:5px solid #1f9d6b;border-radius:12px;padding:14px 18px;background:var(--surface);margin:24px 0}
.aca-retenir h2{margin:0 0 6px;font-size:18px}.aca-retenir ul{margin:0;padding-left:20px}
.aca-quiz{border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:var(--surface);margin:24px 0}
.aca-q{margin:0 0 16px}.aca-q p{font-weight:600;margin:0 0 8px}
.aca-q label{display:flex;gap:10px;align-items:flex-start;padding:9px 11px;border:1px solid var(--line);border-radius:10px;margin:6px 0;cursor:pointer;background:var(--bg)}
.aca-q label.juste{border-color:#1f9d6b;background:color-mix(in srgb,#1f9d6b 14%,transparent)}
.aca-q label.faux{border-color:#d4495a;background:color-mix(in srgb,#d4495a 12%,transparent)}
.aca-q .expl{font-size:14px;color:var(--muted);margin:6px 2px 0}
.aca-res{font-weight:700;margin-top:6px}
.aca-ex{border:1px solid var(--line);border-radius:14px;padding:14px 18px;background:var(--surface);margin:24px 0}
.aca-ex details{margin-top:10px}.aca-ex summary{cursor:pointer;font-weight:600;color:var(--accent)}
.aca-nav{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:28px 0}
.aca-sources{font-size:13.5px;color:var(--muted)}.aca-sources ul{padding-left:20px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.tableau-simple{overflow-x:auto}.tableau-simple table{border-collapse:collapse;min-width:280px}
.tableau-simple th,.tableau-simple td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;font-size:14.5px}
.aca-certif{border:2px solid #b7791f;border-radius:16px;padding:28px;text-align:center;background:var(--surface);margin:20px 0}
.aca-certif h2{font-size:28px;margin:4px 0}
@media (prefers-reduced-motion:no-preference){.aca-niv{animation:aca-monte .5s cubic-bezier(.2,.8,.2,1) both}
 .aca-niv:nth-child(2){animation-delay:.06s}.aca-niv:nth-child(3){animation-delay:.12s}.aca-niv:nth-child(4){animation-delay:.18s}.aca-niv:nth-child(5){animation-delay:.24s}
 @keyframes aca-monte{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}}
@media print{.aca-nav,.aca-quiz,header.top,.nav-ligne,footer{display:none!important}.aca-certif{border-color:#000}}
"""

JS_PROGRES = """<script>
const ACA_CLE="radar-academie";
function acaLire(){try{return JSON.parse(localStorage.getItem(ACA_CLE)||"{}")||{}}catch(e){return{}}}
function acaEcrire(d){try{localStorage.setItem(ACA_CLE,JSON.stringify(d))}catch(e){}}
</script>"""


def _e(s):
    import html
    return html.escape(str(s), quote=True)


def _quiz_html(ch):
    qs = []
    for i, (q, choix, bonne, expl) in enumerate(ch["quiz"]):
        opts = "".join(f"<label><input type='radio' name='q{i}' value='{j}'> <span>{_e(c)}</span></label>" for j, c in enumerate(choix))
        qs.append(f"<fieldset class='aca-q' data-bonne='{bonne}' style='border:0;padding:0'><legend class='sr'>Question {i + 1}</legend>"
                  f"<p>{i + 1}. {_e(q)}</p>{opts}<p class='expl' hidden>{_e(expl)}</p></fieldset>")
    return ("<section class='aca-quiz' aria-labelledby='q-t'><h2 id='q-t' style='margin-top:0'>Quiz : vérifie que tu as compris</h2>"
            + "".join(qs) + "<button class='btn' type='button' id='aca-valider'>Valider mes réponses</button><p class='aca-res' id='aca-res' role='status'></p></section>")


JS_QUIZ = """<script>
(function(){
  const id=document.body.dataset.chap, b=document.getElementById("aca-valider"); if(!b) return;
  const qs=[...document.querySelectorAll(".aca-q")];
  b.onclick=()=>{
    let ok=0, repondu=0;
    qs.forEach(f=>{const c=f.querySelector("input:checked"), bonne=+f.dataset.bonne;
      f.querySelectorAll("label").forEach((l,j)=>{l.classList.toggle("juste",j===bonne);l.classList.toggle("faux",!!c&&+c.value===j&&j!==bonne);});
      f.querySelector(".expl").hidden=false; if(c){repondu++; if(+c.value===bonne) ok++;}});
    const r=document.getElementById("aca-res");
    if(repondu<qs.length){r.textContent="Réponds à toutes les questions pour valider le chapitre ("+repondu+"/"+qs.length+").";return;}
    const d=acaLire(); const avant=(d[id]||{}).score||0; d[id]=Object.assign(d[id]||{},{score:Math.max(avant,ok),total:qs.length,fait:((d[id]||{}).fait)||ok>=Math.ceil(qs.length*2/3),date:Date.now()}); acaEcrire(d);
    r.textContent=ok+" bonne"+(ok>1?"s":"")+" réponse"+(ok>1?"s":"")+" sur "+qs.length+". "+(d[id].fait?"Chapitre validé, bravo (+"+(ok*10)+" points).":"Relis le chapitre et réessaie : il faut "+Math.ceil(qs.length*2/3)+" bonnes réponses.");
  };
})();
</script>"""


CSS_PAS = """
/* version 72 : chaque chapitre = une suite de mini-leçons, chacune suivie d'un mini-exercice (comme un cours de programmation) */
.pp-tete{margin:6px 0 18px}.pp-meta{display:flex;flex-wrap:wrap;gap:6px 16px;color:var(--muted);font-size:14px;margin:6px 0 0}
.pp-meta b{color:var(--ink);font-weight:600}
.pp{display:grid;grid-template-columns:230px minmax(0,1fr);gap:28px;align-items:start}
.pp-plan{position:sticky;top:86px;border:1px solid var(--line);border-radius:14px;background:var(--surface);padding:14px 12px}
.pp-plan h2{font-size:15px;margin:0 0 8px;font-family:inherit;font-weight:700}
.pp-plan ol{list-style:none;margin:0;padding:0;counter-reset:pp}
.pp-plan li a{display:flex;gap:9px;align-items:flex-start;padding:7px 8px;border-radius:9px;color:var(--muted);text-decoration:none;font-size:14px;line-height:1.35}
.pp-plan li a:hover{background:var(--surface-2);color:var(--ink)}
.pp-plan .pt{flex:none;width:20px;height:20px;border-radius:50%;border:2px solid var(--line);margin-top:1px;display:grid;place-items:center;font-size:11px;font-weight:800;transition:background .3s,border-color .3s}
.pp-plan li.fait .pt{background:var(--up);border-color:var(--up);color:#fff}
.pp-plan li{counter-increment:pp}.pp-plan li .pt::before{content:counter(pp)}.pp-plan li.fait .pt::before{content:"✓"}
.pp-plan li.ici a{background:var(--accent-soft);color:var(--ink);font-weight:600}.pp-plan li.ici .pt{border-color:var(--accent)}
.pp-plan li.ferme a{opacity:.55;pointer-events:none}
.pp-barre{height:6px;border-radius:99px;background:var(--surface-2);overflow:hidden;margin:0 0 10px}
.pp-barre i{display:block;height:100%;width:0;background:var(--accent);border-radius:99px;transition:width .6s cubic-bezier(.2,.8,.2,1)}
.pp-compte{font-size:13px;color:var(--muted);margin:0 0 6px}
.pp-etape{border:1px solid var(--line);border-radius:16px;background:var(--surface);padding:22px 24px;margin:0 0 18px;scroll-margin-top:96px}
.pp-etape>header{margin-bottom:6px}.pp-etape>header span{font-size:13.5px;color:var(--muted)}
.pp-etape>header h2{margin:4px 0 0;font-size:24px}
.pp-lecon{font-size:16.5px;line-height:1.65}.pp-lecon p{margin:12px 0}
.pp-atoi{margin-top:20px;border-radius:14px;padding:16px 18px;background:var(--surface-2);border:1px solid var(--line)}
.pp-atoi h3{margin:0 0 4px;font-family:inherit;font-size:15px;color:var(--accent)}
.pp-atoi .pp-q{font-weight:600;margin:0 0 10px;font-size:16px}
.pp-choix{display:grid;gap:8px}
.pp-choix button{all:unset;box-sizing:border-box;display:block;width:100%;padding:11px 14px;border-radius:11px;border:1.5px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font-size:15.5px;line-height:1.4}
.pp-choix button:hover{border-color:var(--accent)}.pp-choix button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.pp-choix.vf{grid-template-columns:1fr 1fr}
.pp-choix button.juste{border-color:var(--up);background:var(--up-soft)}
.pp-choix button.faux{border-color:var(--down);background:var(--down-soft)}
.pp-choix button[disabled]{cursor:default}
.pp-nombre{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.pp-nombre input{width:150px;max-width:100%;padding:10px 12px;border-radius:10px;border:1.5px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;font-size:16px}
.pp-nombre input:focus{outline:3px solid var(--accent);outline-offset:1px}
.pp-retour{margin:12px 0 0;font-size:15px;line-height:1.5}.pp-retour b{display:block;margin-bottom:2px}
.pp-retour.ok b{color:var(--up)}.pp-retour.ko b{color:var(--down)}
.pp-suite{display:flex;justify-content:flex-end;align-items:center;gap:10px;margin-top:16px;flex-wrap:wrap}
.pp-continuer:disabled{opacity:.4;cursor:not-allowed;filter:saturate(.4)}
.pp-aide{font-size:13.5px;color:var(--muted);margin-right:auto}
.pp-sol summary{cursor:pointer;color:var(--accent);font-weight:600;margin-top:10px}
.pp-js .pp-sol{display:none}
.pp-js .pp-etape[hidden]{display:none}
.pp-tout{font-size:14px;margin:0 0 14px}
@media (prefers-reduced-motion:no-preference){
 .pp-js .pp-etape.entre{animation:pp-entre .45s cubic-bezier(.2,.8,.2,1)}
 @keyframes pp-entre{from{opacity:0;transform:translateX(18px)}to{opacity:1;transform:none}}
 .pp-choix button.faux,.pp-nombre input.faux{animation:pp-non .35s}
 @keyframes pp-non{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
 .pp-retour.ok{animation:pp-oui .4s cubic-bezier(.2,.8,.2,1.4)}
 @keyframes pp-oui{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}}
@media (max-width:860px){.pp{grid-template-columns:1fr}.pp-plan{position:static}.pp-plan ol{display:flex;gap:4px;overflow-x:auto;padding-bottom:2px}
 .pp-plan li a span.t{display:none}.pp-plan li a{padding:6px}.pp-etape{padding:18px 16px}}
.pp-auteur{display:flex;gap:12px;align-items:center;border-top:1px solid var(--line);padding-top:16px;margin-top:26px;font-size:14.5px;color:var(--muted)}
.pp-auteur .av{flex:none;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);font-weight:800}
.pp-auteur b{color:var(--ink)}
"""

JS_PAS = """<script>
(function(){
  const pp=document.getElementById("pp"); if(!pp) return; pp.classList.add("pp-js");
  const id=document.body.dataset.chap, et=[...pp.querySelectorAll(".pp-etape")], plan=[...pp.querySelectorAll(".pp-plan li")];
  const d=acaLire(); const moi=d[id]||{}; let max=Math.min(moi.etape||0, et.length-1), cur=max, tout=false;
  const barre=pp.querySelector(".pp-barre i"), compte=pp.querySelector(".pp-compte");
  function sauve(){const x=acaLire(); x[id]=Object.assign(x[id]||{}, {etape:Math.max((x[id]||{}).etape||0,max), etapes:et.length}); acaEcrire(x);}
  function maj(){
    et.forEach((e,i)=>{e.hidden=!tout && i!==cur;});
    plan.forEach((l,i)=>{l.classList.toggle("fait",i<max||(i===max&&et[i].dataset.reussi==="1"));l.classList.toggle("ici",i===cur);l.classList.toggle("ferme",i>max);});
    barre.style.width=Math.round(100*Math.min(max,et.length)/et.length)+"%"; compte.textContent="Étape "+(cur+1)+" sur "+et.length;
  }
  function aller(i,anim){cur=Math.max(0,Math.min(i,et.length-1)); if(cur>max){max=cur; sauve();} maj();
    if(anim&&!tout){et[cur].classList.remove("entre"); void et[cur].offsetWidth; et[cur].classList.add("entre"); et[cur].scrollIntoView({behavior:"smooth",block:"start"});
      const h=et[cur].querySelector("h2"); if(h){h.tabIndex=-1; h.focus({preventScroll:true});}}}
  plan.forEach((l,i)=>l.querySelector("a").addEventListener("click",ev=>{ev.preventDefault(); if(i<=max) aller(i,true);}));
  pp.querySelectorAll(".pp-continuer").forEach(b=>b.addEventListener("click",()=>{const i=et.indexOf(b.closest(".pp-etape")); et[i].dataset.reussi="1"; aller(i+1,true);}));
  pp.querySelectorAll(".pp-retourner").forEach(b=>b.addEventListener("click",()=>aller(et.indexOf(b.closest(".pp-etape"))-1,true)));
  const bt=document.getElementById("pp-tout"); if(bt) bt.addEventListener("click",ev=>{ev.preventDefault(); tout=!tout; bt.textContent=tout?"Revenir au mode pas à pas":"Tout afficher sur une seule page"; maj();});
  const BRAVO=["Bien vu !","Exactement.","C'est ça !","Parfait.","Bonne réponse."];
  pp.querySelectorAll(".pp-atoi").forEach(a=>{
    const etape=a.closest(".pp-etape"), suite=etape.querySelector(".pp-continuer"), ret=a.querySelector(".pp-retour"), expl=a.dataset.expl;
    suite.disabled=true; let essais=0; const aide=document.createElement("span"); aide.className="pp-aide"; aide.textContent="Réponds à l\u2019exercice pour continuer."; suite.parentNode.insertBefore(aide,suite.parentNode.firstChild);
    function fini(ok){suite.disabled=false; aide.remove(); ret.className="pp-retour "+(ok?"ok":"ko");
      ret.innerHTML="<b>"+(ok?BRAVO[Math.floor(Math.random()*BRAVO.length)]:"Voici la bonne réponse.")+"</b>"; ret.append(document.createTextNode(expl));
      if(ok){const x=acaLire(); x.points_lecons=(x.points_lecons||0)+(essais===0?5:2); acaEcrire(x);} setTimeout(()=>suite.focus(),50);}
    function rate(){essais++; ret.className="pp-retour ko"; ret.innerHTML="<b>Pas tout à fait.</b>"+(essais<2?"Relis la leçon juste au-dessus et réessaie.":"");
      if(essais>=2) fini(false);}
    const ch=a.querySelector(".pp-choix");
    if(ch){ const bs=[...ch.querySelectorAll("button")];
      if(!ch.classList.contains("vf")) bs.slice().sort(()=>Math.random()-.5).forEach(b=>ch.appendChild(b));
      bs.forEach(b=>b.addEventListener("click",()=>{ if(!suite.disabled) return; const bon=b.dataset.j===a.dataset.bonne;
        if(bon){b.classList.add("juste"); bs.forEach(x=>x.disabled=true); fini(true);}
        else{b.classList.remove("faux"); void b.offsetWidth; b.classList.add("faux"); b.disabled=true; rate();
          if(essais>=2){bs.forEach(x=>{x.disabled=true; if(x.dataset.j===a.dataset.bonne) x.classList.add("juste");});}}}));
    } else {
      const inp=a.querySelector("input"), ok=a.querySelector(".pp-verifier"), rep=+a.dataset.rep, tol=+a.dataset.tol;
      const test=()=>{ if(!suite.disabled) return; const v=parseFloat(inp.value.replace(/\\s|€|%/g,"").replace(",",".")); if(isNaN(v)){ret.className="pp-retour ko";ret.innerHTML="<b>Écris un nombre.</b>Par exemple 12 ou 12,5.";return;}
        if(Math.abs(v-rep)<=tol+1e-9){inp.classList.remove("faux"); inp.disabled=true; ok.disabled=true; fini(true);}
        else{inp.classList.remove("faux"); void inp.offsetWidth; inp.classList.add("faux"); rate(); if(essais>=2){inp.disabled=true; ok.disabled=true;}}};
      ok.addEventListener("click",test); inp.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();test();}});
    }
  });
  maj();
})();
</script>"""


def _nombre_fr(x):
    t = f"{x:,.2f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",")
    return t


def _atoi_html(ex):
    if ex["type"] == "nombre":
        sol = f"{_nombre_fr(ex['rep'])} {ex['unite']}".strip()
        zone = (f"<div class='pp-nombre'><label class='sr' for='{{fid}}'>Ta réponse</label><input id='{{fid}}' inputmode='decimal' autocomplete='off' placeholder='Ta réponse'>"
                f"<span class='muted'>{_e(ex['unite'])}</span><button class='btn' type='button' class='pp-verifier'>Vérifier</button></div>").replace("class='btn' type='button' class='pp-verifier'", "class='btn pp-verifier' type='button'")
        attrs = f"data-rep='{ex['rep']}' data-tol='{ex['tol']}'"
    else:
        sol = ex["choix"][ex["bonne"]]
        zone = (f"<div class='pp-choix{' vf' if ex['type'] == 'vf' else ''}' role='group' aria-label='Choisis une réponse'>"
                + "".join(f"<button type='button' data-j='{j}'>{_e(c)}</button>" for j, c in enumerate(ex["choix"])) + "</div>")
        attrs = f"data-bonne='{ex['bonne']}'"
    titre = {"qcm": "À toi : choisis la bonne réponse", "vf": "À toi : vrai ou faux ?", "nombre": "À toi : fais le calcul"}[ex["type"]]
    return (f"<div class='pp-atoi' {attrs} data-expl=\"{_e(ex['expl'])}\"><h3>{titre}</h3><p class='pp-q'>{_e(ex['q'])}</p>{zone}"
            f"<p class='pp-retour' role='status' aria-live='polite'></p>"
            f"<details class='pp-sol'><summary>Voir la réponse</summary><p><b>{_e(sol)}</b>. {_e(ex['expl'])}</p></details></div>")


def _page_chapitre(seo, base, csp, ch, i):
    from .formation_exos import EXOS
    niv = next(n for n in NIVEAUX if n[0] == ch["niveau"])
    prec = CHAPITRES[i - 1] if i > 0 else None
    suiv = CHAPITRES[i + 1] if i + 1 < len(CHAPITRES) else None
    exos = EXOS[ch["id"]]
    n_lecons = len(ch["sections"])
    etapes, plan = [], []
    # le lexique au survol est calculé sur tout le chapitre pour qu'un mot ne soit expliqué qu'une fois
    lecons = avec_lexique("".join(f"<!--L{k}-->{h}" for k, (t, h) in enumerate(ch["sections"]))).split("<!--L")[1:]
    lecons = [x.split("-->", 1)[1] for x in lecons]
    total = n_lecons + 3
    for k, ((t, _h), h, ex) in enumerate(zip(ch["sections"], lecons, exos)):
        t_aff = t.split(". ", 1)[1] if t[:1].isdigit() and ". " in t[:4] else t
        a = _atoi_html(ex).replace("{fid}", f"n{k}")
        etapes.append(f"<section class='pp-etape' id='lecon-{k + 1}'><header><span>Mini-leçon {k + 1} sur {n_lecons}</span><h2>{_e(t_aff)}</h2></header>"
                      f"<div class='pp-lecon'>{h}</div>{a}<div class='pp-suite'>"
                      + ("<button class='btn ghost pp-retourner' type='button'>Retour</button>" if k else "")
                      + f"<button class='btn pp-continuer' type='button'>{'Mini-leçon suivante' if k + 1 < n_lecons else 'Voir le récap'}</button></div></section>")
        plan.append((f"lecon-{k + 1}", t_aff))
    enonce, correction = ch["exercice"]
    etapes.append("<section class='pp-etape' id='recap'><header><span>Récap</span><h2>Ce qu'il faut retenir</h2></header><div class='pp-lecon'><ul>"
                  + "".join(f"<li>{_e(x)}</li>" for x in ch["retenir"])
                  + "</ul><p class='muted'>Ces points reviendront dans les <a href='revision.html'>révisions express</a>, au bon moment pour ne pas les oublier.</p></div>"
                    "<div class='pp-suite'><button class='btn ghost pp-retourner' type='button'>Retour</button><button class='btn pp-continuer' type='button'>Passer à la pratique</button></div></section>")
    plan.append(("recap", "Récap"))
    etapes.append(f"<section class='pp-etape' id='pratique'><header><span>Mise en pratique</span><h2>Un cas concret</h2></header><div class='pp-lecon'>{enonce}"
                  f"<details class='pp-sol' style='display:block'><summary>Voir la correction (essaie d'abord !)</summary>{correction}</details></div>"
                  "<div class='pp-suite'><button class='btn ghost pp-retourner' type='button'>Retour</button><button class='btn pp-continuer' type='button'>Faire le bilan</button></div></section>")
    plan.append(("pratique", "Mise en pratique"))
    etapes.append(f"<section class='pp-etape' id='bilan'><header><span>Bilan du chapitre</span><h2>Valide le chapitre</h2></header>"
                  f"<p class='muted'>{len(ch['quiz'])} questions sur tout le chapitre. Avec {-(-len(ch['quiz']) * 2 // 3)} bonnes réponses, il est validé et compte pour ton badge de niveau.</p>"
                  f"{_quiz_html(ch).replace('<h2 id=' + chr(39) + 'q-t' + chr(39) + ' style=' + chr(39) + 'margin-top:0' + chr(39) + '>Quiz : vérifie que tu as compris</h2>', '<h3 id=' + chr(39) + 'q-t' + chr(39) + ' class=' + chr(39) + 'sr' + chr(39) + '>Quiz du chapitre</h3>')}"
                  "<div class='pp-suite'><button class='btn ghost pp-retourner' type='button'>Retour</button>"
                  + (f"<a class='btn' href='{suiv['id']}.html'>Chapitre suivant : {_e(suiv['titre'])}</a>" if suiv else "<a class='btn' href='examen.html'>Passer l'examen final</a>")
                  + "</div></section>")
    plan.append(("bilan", "Bilan"))
    plan_html = ("<aside class='pp-plan' aria-label='Plan du chapitre'><p class='pp-compte'>Étape 1 sur " + str(total) + "</p><div class='pp-barre'><i></i></div><h2>Au programme</h2><ol>"
                 + "".join(f"<li><a href='#{a}' aria-label='{_e(t)}'><span class='pt' aria-hidden='true'></span><span class='t'>{_e(t)}</span></a></li>" for a, t in plan) + "</ol></aside>")
    sources = ("<section class='aca-sources'><h2 style='font-size:17px'>Sources</h2><ul>"
               + "".join(f"<li><a href='{_e(u)}'" + ("" if u.startswith("..") else " rel='noopener noreferrer'") + f">{_e(n)}</a></li>" for n, u in ch["sources"])
               + f"</ul><p>Les règles fiscales et les plafonds peuvent changer : en cas de doute, consulte service-public.fr ou l'AMF. "
               "Ce cours est éducatif et ne constitue pas un conseil en investissement.</p></section>")
    auteur = (f"<div class='pp-auteur'><span class='av' aria-hidden='true'>M</span><p style='margin:0'>Écrit et vérifié par <b>maxitemmmm</b>, créateur de {seo.NOM}. "
              f"Chiffres relus le {VERIFIE_LE} à partir des sources officielles ci-dessus. Tu as repéré une erreur ? <a href='../contact.html'>Dis-le moi</a>, je corrige.</p></div>")
    nav = ("<nav class='aca-nav' aria-label='Chapitres'>"
           + (f"<a class='btn ghost' href='{prec['id']}.html'>Précédent : {_e(prec['titre'])}</a>" if prec else "<span></span>")
           + "<a class='btn ghost' href='../formation.html'>Tous les chapitres</a>"
           + (f"<a class='btn' href='{suiv['id']}.html'>Suivant : {_e(suiv['titre'])}</a>" if suiv else "<a class='btn' href='examen.html'>Passer l'examen final</a>")
           + "</nav>")
    corps = (f"<style>{CSS}{CSS_LEX}{CSS_PAS}</style>{JS_PROGRES}"
             f"<p class='aca-fil'><a href='../formation.html'>Académie</a> › Niveau {niv[0]} : {_e(niv[1])} › Chapitre {i + 1} sur {len(CHAPITRES)}</p>"
             f"<article class='aca-cours'><header class='pp-tete'><h1>{_e(ch['titre'])}</h1><p class='muted' style='margin:0'>{_e(ch['desc'])}</p>"
             f"<p class='pp-meta'><span><b>{n_lecons}</b> mini-leçons</span><span><b>{n_lecons}</b> exercices</span><span>environ <b>{ch['minutes'] + 3}</b> min</span></p></header>"
             f"<p class='pp-tout'><a href='#' id='pp-tout'>Tout afficher sur une seule page</a></p>"
             f"<div class='pp' id='pp'>{plan_html}<div class='pp-etapes'>{''.join(etapes)}</div></div>"
             f"{sources}{auteur}</article>{nav}"
             f"<script>document.body.dataset.chap={json.dumps(ch['id'])};</script>{JS_QUIZ}{JS_PAS}")
    chemin = f"formation/{ch['id']}.html"
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "LearningResource", "name": ch["titre"], "description": ch["desc"], "inLanguage": "fr",
         "learningResourceType": "Cours", "educationalLevel": f"Niveau {niv[0]} : {niv[1]}", "timeRequired": f"PT{ch['minutes'] + 3}M",
         "isAccessibleForFree": True, "url": (base + chemin) if base else None,
         "author": {"@type": "Person", "name": "maxitemmmm"},
         "hasPart": [{"@type": "LearningResource", "name": t, "learningResourceType": "Mini-leçon"} for _a, t in plan[:n_lecons]],
         "isPartOf": {"@type": "Course", "name": "Académie Radar Bourse : apprendre la Bourse de zéro", "url": (base + "formation.html") if base else None}},
        {"@type": "Quiz", "name": f"Quiz : {ch['titre']}", "about": ch["titre"], "inLanguage": "fr", "hasPart": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": choix[b] + ". " + e},
             "suggestedAnswer": [{"@type": "Answer", "text": c} for k, c in enumerate(choix) if k != b]} for q, choix, b, e in ch["quiz"]]},
        seo._jsonld_fil(base, [(seo.NOM, ""), ("Académie", "formation.html"), (ch["titre"], chemin)])]}
    titre = f"{ch['titre']} | Cours de Bourse débutant gratuit"
    titre = titre if len(titre) <= 66 else f"{ch['titre']} | Académie {seo.NOM}"
    return chemin, seo._page(base, titre, ch["desc"] + f" {n_lecons} mini-leçons avec exercices, puis un quiz corrigé.", chemin, corps, jl, csp=csp,
                             mots=ch["mots"] + ", " + MOTS_ACADEMIE)


class _Capture:
    """Récupère les données structurées d'une page sans la fabriquer."""
    def __init__(self, seo):
        self._seo = seo

    def __getattr__(self, nom):
        return getattr(self._seo, nom)

    def _page(self, base, titre, description, chemin, corps, jsonld=None, *a, **k):
        return jsonld


def _page_chapitre_app(seo, base, csp, ch, i):
    """Version 73 : la leçon plein écran façon appli de cours (le contenu et le référencement restent ceux du chapitre)."""
    from . import academie
    from .formation_exos import EXOS
    from .academie_graphiques import exercices as _graphes
    lecons = avec_lexique("".join(f"<!--L{k}-->{h}" for k, (t, h) in enumerate(ch["sections"]))).split("<!--L")[1:]
    lecons = [x.split("-->", 1)[1] for x in lecons]
    corps = academie.lecon(seo, ch, i, CHAPITRES, NIVEAUX, EXOS[ch["id"]], _graphes().get(ch["id"], []), lecons, VERIFIE_LE)
    chemin, jl = _page_chapitre(_Capture(seo), base, csp, ch, i)   # mêmes données structurées que la page de cours
    n_lecons = len(ch["sections"])
    titre = f"{ch['titre']} | Cours de Bourse débutant gratuit"
    titre = titre if len(titre) <= 66 else f"{ch['titre']} | Académie {seo.NOM}"
    return chemin, academie.page(seo, base, titre, ch["desc"] + f" {n_lecons} mini-leçons avec exercices, puis un quiz corrigé.", chemin, corps, jl,
                                 csp=csp, mots=ch["mots"] + ", " + MOTS_ACADEMIE, lecon=True)


def _page_hub_app(seo, base, csp):
    from . import academie
    corps = f"<style>{CSS_LEX}</style>" + academie.parcours(CHAPITRES, NIVEAUX, VERIFIE_LE, seo.NOM)
    jl = _page_hub(_Capture(seo), base, csp)
    return academie.page(seo, base, f"Apprendre la Bourse de zéro : formation gratuite pour débutants | {seo.NOM}",
                         f"Formation Bourse gratuite façon appli : {len(CHAPITRES)} chapitres, {sum(len(c['sections']) for c in CHAPITRES)} mini-leçons avec exercices, "
                         "série de jours, examen final et certificat. Des bases à la crypto.", "formation.html", corps, jl, csp=csp, mots=MOTS_ACADEMIE)


def _page_profil(seo, base, csp):
    from . import academie
    chemin = "formation/profil.html"
    return chemin, academie.page(seo, base, f"Mon profil | Académie {seo.NOM}", "Ta progression dans l'Académie Radar Bourse : série, XP, badges et chapitres validés.",
                                 chemin, academie.profil(NIVEAUX, CHAPITRES), None, csp=csp)


def _page_hub(seo, base, csp):
    blocs = []
    for n, nom, desc, coul in NIVEAUX:
        chs = [(i, c) for i, c in enumerate(CHAPITRES) if c["niveau"] == n]
        lis = "".join(f"<li><a href='formation/{c['id']}.html' data-chap='{c['id']}'><span class='aca-etat' aria-hidden='true'>{i + 1}</span>"
                      f"<span>{_e(c['titre'])}<small class='aca-sous' data-n='{len(c['sections'])}'>{len(c['sections'])} mini-leçons, environ {c['minutes'] + 3} min</small></span></a></li>" for i, c in chs)
        blocs.append(f"<section class='aca-niv' style='--c:{coul}' aria-labelledby='niv{n}'><header><span class='aca-num' aria-hidden='true'>{n}</span>"
                     f"<div><h2 id='niv{n}' style='scroll-margin-top:120px'>Niveau {n} : {_e(nom)}</h2><p>{_e(desc)}</p></div></header><ul class='aca-chaps'>{lis}</ul></section>")
    total_min = sum(c["minutes"] for c in CHAPITRES)
    badges = "".join(f"<span class='aca-badge' data-niv='{n}'>Niveau {n} : {_e(nom)}</span>" for n, nom, *_ in NIVEAUX)
    corps = (f"<style>{CSS}{CSS_LEX}{CSS_PAS}</style>{JS_PROGRES}"
             "<div class='aca-hero'><h1>L'Académie : apprendre la Bourse de zéro</h1>"
             f"<p>J'ai construit ce parcours comme un cours de programmation : une petite leçon de quelques lignes, un exercice tout de suite après pour vérifier, "
             f"et on passe à la suite. {len(CHAPITRES)} chapitres en {len(NIVEAUX)} niveaux, {sum(len(c['sections']) for c in CHAPITRES)} mini-leçons, "
             "des bases jusqu'à la construction d'un vrai portefeuille, avec un niveau entier consacré à la crypto.</p>"
             "<ol class='aca-methode'><li><b>Une mini-leçon</b><span>2 minutes de lecture, avec les mots techniques expliqués au survol.</span></li>"
             "<li><b>Un exercice</b><span>Choix, vrai ou faux, ou petit calcul. Corrigé tout de suite.</span></li>"
             "<li><b>Le bilan</b><span>Un récap, un cas concret, puis un quiz pour valider le chapitre.</span></li></ol>"
             f"<p class='muted' style='font-size:14px'>Pas de compte à créer : ta progression reste dans ton navigateur. Chiffres et règles vérifiés le {VERIFIE_LE}, "
             "sources officielles citées dans chaque chapitre. Gratuit, sans publicité, sans rien à vendre.</p></div>"
             "<div class='aca-barre'><div><span class='lbl'>Chapitres validés</span><b id='aca-n'>0</b> / " + str(len(CHAPITRES)) + "</div>"
             "<div><span class='lbl'>Points</span><b id='aca-pts'>0</b></div><div class='aca-prog' role='progressbar' aria-label='Progression' "
             f"aria-valuemin='0' aria-valuemax='{len(CHAPITRES)}' aria-valuenow='0'><i id='aca-barre'></i></div>"
             "<a class='btn' id='aca-reprendre' href='formation/" + CHAPITRES[0]["id"] + ".html'>Commencer</a></div>"
             f"<div class='aca-badges' aria-label='Badges de niveau'>{badges}<span class='aca-badge' data-niv='examen'>Certificat de l'Académie</span></div>"
             "<div class='aca-outils'><a href='formation/test-de-niveau.html'><b>Test de niveau</b><span>14 questions pour savoir par où commencer.</span></a>"
             "<a href='formation/revision.html'><b>Révisions express</b><span>Des fiches qui reviennent au bon moment pour tout retenir.</span></a>"
             "<a href='formation/examen.html'><b>Examen final</b><span>20 questions, et un certificat si tu réussis.</span></a>"
             "<a href='glossaire.html'><b>Glossaire</b><span>Tous les mots de la Bourse, expliqués simplement.</span></a></div>"
             f"<div class='aca-niveaux'>{''.join(blocs)}</div>"
             "<section class='aca-ex'><h2 style='margin-top:0'>L'examen final</h2><p>20 questions tirées de tout le parcours. Avec au moins 15 bonnes réponses, "
             "tu obtiens le certificat de l'Académie Radar Bourse, à imprimer ou à enregistrer en PDF.</p>"
             "<p><a class='btn' href='formation/examen.html'>Passer l'examen</a></p></section>"
             "<section class='aca-ex'><h2 style='margin-top:0'>Et ensuite ?</h2><p>Mets en pratique sans risque : le <a href='index.html#portefeuille'>portefeuille virtuel</a> "
             "(10 000 € fictifs), le <a href='index.html#prono'>pronostic du jour</a> et l'<a href='index.html#remonte'>Arène</a> contre l'IA. "
             "Pour aller plus loin : les <a href='guides.html'>guides</a> et le <a href='glossaire.html'>glossaire</a>.</p></section>"
             f"<div class='pp-auteur'><span class='av' aria-hidden='true'>M</span><p style='margin:0'>L'Académie est écrite et tenue à jour par <b>maxitemmmm</b>, créateur de {seo.NOM}. "
             "Je relis chaque chiffre à partir des sources officielles (AMF, impots.gouv.fr, service-public.fr, Banque de France). "
             "Une question, une erreur, une idée de chapitre ? <a href='contact.html'>Écris-moi</a>.</p></div>"
             "<script>(function(){const d=acaLire(),ids=" + json.dumps([c["id"] for c in CHAPITRES]) + ",niv=" + json.dumps({c["id"]: c["niveau"] for c in CHAPITRES}) + ";"
             "let n=0,pts=0;const parNiv={};ids.forEach(id=>{const x=d[id];if(x&&x.fait){n++;}if(x)pts+=(x.score||0)*10;"
             "parNiv[niv[id]]=parNiv[niv[id]]||[0,0];parNiv[niv[id]][1]++;if(x&&x.fait)parNiv[niv[id]][0]++;});"
             "document.querySelectorAll('[data-chap]').forEach(a=>{const x=d[a.dataset.chap];if(x&&x.fait){a.classList.add('fait');a.querySelector('.aca-etat').textContent='✓';}else if(x&&x.etape){const sm=a.querySelector('.aca-sous'),nl=+sm.dataset.n;sm.textContent='En cours : étape '+Math.min(x.etape+1,nl+3)+' sur '+(nl+3);a.classList.add('encours');}});"
             "document.getElementById('aca-n').textContent=n;document.getElementById('aca-pts').textContent=pts+(d.points_lecons||0);"
             "const b=document.getElementById('aca-barre');requestAnimationFrame(()=>{b.style.width=(n/ids.length*100)+'%';});b.parentElement.setAttribute('aria-valuenow',n);"
             "document.querySelectorAll('.aca-badge[data-niv]').forEach(x=>{const k=x.dataset.niv;if(k==='examen'?(d.examen&&d.examen.reussi):(parNiv[k]&&parNiv[k][0]===parNiv[k][1]))x.classList.add('ok');});"
             "const suite=ids.find(id=>!(d[id]&&d[id].fait));const r=document.getElementById('aca-reprendre');"
             "if(n>0&&suite){r.href='formation/'+suite+'.html';r.textContent='Reprendre';}else if(!suite){r.href='formation/examen.html';r.textContent=\"Passer l'examen\";}})();</script>")
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "Course", "name": "Académie Radar Bourse : apprendre la Bourse de zéro", "inLanguage": "fr",
         "description": f"Formation gratuite pour débutants en {len(NIVEAUX)} niveaux et {len(CHAPITRES)} chapitres, avec quiz, exercices corrigés et examen final.",
         "provider": {"@type": "Organization", "name": seo.NOM, "url": base or None}, "isAccessibleForFree": True,
         "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online", "courseWorkload": f"PT{total_min}M"},
         "offers": {"@type": "Offer", "price": 0, "priceCurrency": "EUR", "category": "Free"},
         "syllabusSections": [{"@type": "Syllabus", "name": f"Niveau {n} : {nom}", "description": desc} for n, nom, desc, _ in NIVEAUX]},
        seo._jsonld_liste(base, "Chapitres de l'Académie", "formation.html", [(c["titre"], f"formation/{c['id']}.html") for c in CHAPITRES])["@graph"][0],
        seo._jsonld_fil(base, [(seo.NOM, ""), ("Académie", "formation.html")])]}
    return seo._page(base, f"Apprendre la Bourse de zéro : formation gratuite pour débutants | {seo.NOM}",
                     f"Formation Bourse gratuite pour débutants : {len(CHAPITRES)} chapitres en {len(NIVEAUX)} niveaux, des bases au portefeuille, avec quiz, exercices corrigés et certificat.",
                     "formation.html", corps, jl, csp=csp, mots=MOTS_ACADEMIE)


def _page_examen(seo, base, csp):
    banque = [dict(q=q, c=c, b=b, e=e, ch=ch["titre"]) for ch in CHAPITRES for q, c, b, e in ch["quiz"]]
    corps = (f"<style>{CSS}</style>{JS_PROGRES}"
             "<p class='aca-fil'><a href='../formation.html'>Académie</a> › Examen final</p>"
             "<h1>Examen final de l'Académie</h1><p>20 questions tirées au hasard dans tout le parcours. Il faut <b>15 bonnes réponses</b> pour obtenir le certificat. "
             "Tu peux le repasser autant de fois que tu veux : les questions changent.</p>"
             "<div class='aca-quiz' id='examen'></div><p class='aca-res' id='ex-res' role='status'></p><div id='certif'></div>"
             "<script>(function(){const B=" + json.dumps(banque, ensure_ascii=False) + ";"
             "const z=document.getElementById('examen');const tirage=B.map(x=>[Math.random(),x]).sort((a,b)=>a[0]-b[0]).slice(0,20).map(x=>x[1]);"
             "const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));"
             "z.innerHTML=tirage.map((x,i)=>`<fieldset class='aca-q' data-bonne='${x.b}' style='border:0;padding:0'><legend class='sr'>Question ${i+1}</legend>"
             "<p>${i+1}. ${esc(x.q)}</p>${x.c.map((c,j)=>`<label><input type='radio' name='e${i}' value='${j}'> <span>${esc(c)}</span></label>`).join('')}"
             "<p class='expl' hidden>${esc(x.e)} <i>(chapitre : ${esc(x.ch)})</i></p></fieldset>`).join('')+\"<button class='btn' type='button' id='ex-ok'>Corriger l'examen</button>\";"
             "document.getElementById('ex-ok').onclick=()=>{let ok=0,rep=0;z.querySelectorAll('.aca-q').forEach(f=>{const c=f.querySelector('input:checked'),b=+f.dataset.bonne;"
             "f.querySelectorAll('label').forEach((l,j)=>{l.classList.toggle('juste',j===b);l.classList.toggle('faux',!!c&&+c.value===j&&j!==b);});f.querySelector('.expl').hidden=false;if(c){rep++;if(+c.value===b)ok++;}});"
             "const r=document.getElementById('ex-res');if(rep<20){r.textContent='Réponds aux 20 questions ('+rep+'/20).';return;}"
             "const reussi=ok>=15;const d=acaLire();d.examen={meilleur:Math.max(ok,(d.examen||{}).meilleur||0),reussi:reussi||((d.examen||{}).reussi||false),date:Date.now()};acaEcrire(d);"
             "r.textContent=ok+' / 20. '+(reussi?'Bravo, examen réussi !':'Il faut 15 bonnes réponses : relis les chapitres indiqués et réessaie.');"
             "if(reussi){const date=new Date().toLocaleDateString('fr-FR',{day:'numeric',month:'long',year:'numeric'});"
             "document.getElementById('certif').innerHTML=`<div class='aca-certif'><p class='muted'>Certificat</p><h2>Académie Radar Bourse</h2>"
             "<p>Ce certificat atteste que</p><p><input id='nom-certif' placeholder='Ton prénom' aria-label='Ton prénom' style='font:inherit;font-size:22px;text-align:center;border:0;border-bottom:2px solid var(--line);background:transparent;color:var(--ink);padding:4px;width:100%;max-width:300px;box-sizing:border-box'></p>"
             "<p>a terminé le parcours « Apprendre la Bourse de zéro » et réussi l'examen final avec <b>${ok}/20</b>, le ${date}.</p>"
             "<p class='muted' style='font-size:13px'>Formation éducative gratuite. Ce certificat n'est pas un diplôme officiel.</p>"
             "<button class='btn' type='button' onclick='print()'>Imprimer ou enregistrer en PDF</button></div>`;}"
             "r.scrollIntoView({behavior:'smooth',block:'center'});};})();</script>"
             "<nav class='aca-nav'><a class='btn ghost' href='../formation.html'>Retour à l'Académie</a></nav>")
    chemin = "formation/examen.html"
    return chemin, seo._page(base, f"Quiz Bourse : examen final pour débutants | {seo.NOM}",
                             "Teste tes connaissances en Bourse : 20 questions corrigées tirées des 27 chapitres de l'Académie, et un certificat si tu réussis.",
                             chemin, corps, None, csp=csp, mots="quiz bourse, test connaissances bourse, qcm bourse débutant, " + MOTS_ACADEMIE)


def generer(seo, base, dossier, csp) -> list:
    os.makedirs(os.path.join(dossier, "formation"), exist_ok=True)
    faits = []
    from .academie import SeoAcademie
    with open(os.path.join(dossier, "formation.html"), "w", encoding="utf-8") as f:
        f.write(_page_hub_app(seo, base, csp))
    faits.append("formation.html")
    chemin, html_ = _page_profil(seo, base, csp)
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(html_)
    faits.append(chemin)
    seo = SeoAcademie(seo)   # test de niveau, révisions et examen passent dans la coque de l'Académie
    for i, ch in enumerate(CHAPITRES):
        chemin, html_ = _page_chapitre_app(seo._seo, base, csp, ch, i)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(html_)
        faits.append(chemin)
    for fab in (_page_test_niveau, _page_revision):
        chemin, html_ = fab(seo, base, csp)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(html_)
        faits.append(chemin)
    chemin, html_ = _page_examen(seo, base, csp)
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(html_)
    faits.append(chemin)
    return faits


# ---------------------------------------------------------------------------------------------------------------
# Version 71 : définitions au survol, test de niveau, révisions express (répétition espacée)
# ---------------------------------------------------------------------------------------------------------------
LEXIQUE = {
    "action": "Une part du capital d'une entreprise.",
    "obligation": "Un prêt fait à une entreprise ou à un État, rémunéré par des intérêts.",
    "ETF": "Un fonds coté qui copie un indice (par exemple le CAC 40 ou le MSCI World).",
    "indice": "Un panier d'entreprises qui sert de thermomètre du marché.",
    "dividende": "La part des bénéfices reversée aux actionnaires. Jamais garantie.",
    "volatilité": "La mesure de l'agitation habituelle d'un prix.",
    "courtier": "L'intermédiaire qui transmet tes ordres au marché.",
    "PEA": "Plan d'épargne en actions : enveloppe fiscale française, plafonnée à 150 000 € de versements.",
    "compte-titres": "Compte pour détenir des titres du monde entier, sans plafond ni avantage fiscal.",
    "ordre à cours limité": "Un ordre qui fixe le prix maximum à l'achat (ou minimum à la vente).",
    "carnet d'ordres": "La liste des prix proposés par les acheteurs et les vendeurs.",
    "diversification": "Répartir son argent sur des placements qui ne bougent pas tous pareil.",
    "corrélation": "La mesure de la tendance de deux placements à bouger ensemble (de −1 à +1).",
    "drawdown": "La baisse depuis le plus haut : la pire chute subie.",
    "intérêts composés": "Des intérêts qui rapportent eux-mêmes des intérêts.",
    "capitalisant": "Un fonds qui réinvestit automatiquement ses dividendes.",
    "TER": "Les frais courants annuels d'un fonds, prélevés à l'intérieur.",
    "consensus": "La moyenne des prévisions des analystes.",
    "chiffre d'affaires": "Le total des ventes d'une entreprise.",
    "marge": "La part des ventes qui reste en bénéfice.",
    "RSI": "Un indicateur de 0 à 100 qui compare la force des hausses et des baisses récentes.",
    "moyenne mobile": "La moyenne des derniers cours, recalculée chaque jour.",
    "support": "Un niveau de prix où les acheteurs sont souvent revenus.",
    "résistance": "Un niveau de prix où les vendeurs ont souvent pris le dessus.",
    "inflation": "La hausse générale des prix, qui réduit le pouvoir d'achat.",
    "taux directeur": "Le taux fixé par une banque centrale pour piloter l'économie.",
    "krach": "Une chute brutale et forte des marchés.",
    "blockchain": "Un registre de transactions partagé et très difficile à falsifier.",
    "stablecoin": "Une crypto qui vise un prix fixe, souvent 1 dollar.",
    "halving": "La division par deux de la récompense des mineurs de bitcoin, environ tous les 4 ans.",
    "phrase de récupération": "Les 12 ou 24 mots qui donnent accès à tes cryptos. À ne jamais partager.",
    "plus-value": "Le gain réalisé en vendant plus cher qu'à l'achat.",
    "moins-value": "La perte réalisée en vendant moins cher qu'à l'achat.",
    "flat tax": "Le prélèvement forfaitaire unique : 31,4 % en 2026 sur les gains d'un compte-titres.",
    "rééquilibrer": "Ramener un portefeuille à la répartition choisie au départ.",
}


def avec_lexique(html_):
    """Entoure la première apparition de chaque terme du lexique (hors balises et liens) d'une définition au survol."""
    import re
    vus = set()
    morceaux = re.split(r"(<[^>]+>)", html_)
    dans_lien = 0
    for i, m in enumerate(morceaux):
        if m.startswith("<"):
            if re.match(r"<(a|h\d|dfn|code)[\s>]", m):
                dans_lien += 1
            elif re.match(r"</(a|h\d|dfn|code)>", m):
                dans_lien = max(0, dans_lien - 1)
            continue
        if dans_lien or not m.strip():
            continue
        poses = []
        for terme, defi in LEXIQUE.items():
            if terme in vus:
                continue
            motif = re.compile(r"(?<![\w-])(" + re.escape(terme) + r")(?![\w-])", 0 if terme.isupper() else re.I)
            x = motif.search(m)
            if x:
                poses.append(f"<dfn class='def-lex' tabindex='0' data-def=\"{_e(defi)}\">{x.group(1)}</dfn>")
                m = m[:x.start()] + f"\x00{len(poses) - 1}\x00" + m[x.end():]
                vus.add(terme)
        morceaux[i] = re.sub(r"\x00(\d+)\x00", lambda y: poses[int(y.group(1))], m)
    return "".join(morceaux)


CSS_LEX = """
.def-lex{font-style:normal;border-bottom:1.5px dotted var(--accent);cursor:help;position:relative}
.def-lex:hover::after,.def-lex:focus::after{content:attr(data-def);position:absolute;left:0;top:calc(100% + 6px);z-index:20;width:min(280px,80vw);
  padding:9px 11px;border-radius:10px;background:var(--ink);color:var(--surface);font-size:13.5px;line-height:1.45;font-weight:400;box-shadow:0 10px 26px rgba(0,0,0,.3)}
.aca-outils{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px;margin:18px 0}
.aca-outils a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:var(--surface);text-decoration:none;color:var(--ink)}
.aca-outils a:hover{border-color:var(--accent)}.aca-outils b{display:block;font-size:16px;margin-bottom:4px}.aca-outils span{color:var(--muted);font-size:14px}
.carte-rev{min-height:180px;display:grid;place-items:center;text-align:center;padding:24px;border:1px solid var(--line);border-radius:16px;background:var(--surface);
  font-size:19px;line-height:1.5;margin:14px 0;cursor:pointer;perspective:800px}
.carte-rev small{display:block;color:var(--muted);font-size:13px;margin-bottom:8px}
.rev-btns{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
@media (prefers-reduced-motion:no-preference){.carte-rev.tourne{animation:rev-tourne .35s ease}@keyframes rev-tourne{from{transform:rotateX(70deg);opacity:.3}to{transform:none;opacity:1}}}
"""


def _page_test_niveau(seo, base, csp):
    # 2 questions par niveau, de la plus simple à la plus difficile : le premier niveau raté donne le point de départ conseillé
    qs = []
    for n, nom, *_ in NIVEAUX:
        chs = [c for c in CHAPITRES if c["niveau"] == n]
        for c in chs[:2]:
            q, choix, b, e = c["quiz"][0]
            qs.append(dict(n=n, niv=nom, q=q, c=choix, b=b, e=e, id=c["id"]))
    corps = (f"<style>{CSS}{CSS_LEX}</style>{JS_PROGRES}"
             "<p class='aca-fil'><a href='../formation.html'>Académie</a> › Test de niveau</p>"
             "<h1>Test de niveau : par où commencer ?</h1>"
             f"<p>{len(qs)} questions, des bases jusqu'aux notions avancées. Réponds sans chercher : le test te dit à quel niveau commencer et quels chapitres tu peux survoler. "
             "Il prend environ 4 minutes.</p><div class='aca-quiz' id='tn'></div><p class='aca-res' id='tn-res' role='status'></p><div id='tn-conseil'></div>"
             "<script>(function(){const Q=" + json.dumps(qs, ensure_ascii=False) + ",NIV=" + json.dumps([[n, nom] for n, nom, *_ in NIVEAUX], ensure_ascii=False) + ";"
             "const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));"
             "const z=document.getElementById('tn');z.innerHTML=Q.map((x,i)=>`<fieldset class='aca-q' data-bonne='${x.b}' data-n='${x.n}' style='border:0;padding:0'><legend class='sr'>Question ${i+1}</legend>"
             "<p>${i+1}. ${esc(x.q)} <span class='muted' style='font-weight:400;font-size:13px'>(niveau ${x.n})</span></p>${x.c.map((c,j)=>`<label><input type='radio' name='t${i}' value='${j}'> <span>${esc(c)}</span></label>`).join('')}"
             "<label><input type='radio' name='t${i}' value='-1'> <span>Je ne sais pas</span></label><p class='expl' hidden>${esc(x.e)}</p></fieldset>`).join('')+\"<button class='btn' type='button' id='tn-ok'>Voir mon niveau</button>\";"
             "document.getElementById('tn-ok').onclick=()=>{const par={};let rep=0;z.querySelectorAll('.aca-q').forEach(f=>{const c=f.querySelector('input:checked'),b=+f.dataset.bonne,n=+f.dataset.n;"
             "par[n]=par[n]||[0,0];par[n][1]++;f.querySelectorAll('label').forEach((l,j)=>{l.classList.toggle('juste',j===b);l.classList.toggle('faux',!!c&&+c.value===j&&j!==b);});"
             "f.querySelector('.expl').hidden=false;if(c){rep++;if(+c.value===b)par[n][0]++;}});"
             "if(rep<Q.length){document.getElementById('tn-res').textContent='Réponds à toutes les questions (« je ne sais pas » compte) : '+rep+'/'+Q.length+'.';return;}"
             "let depart=NIV[NIV.length-1][0]+1;for(const [n] of NIV){if(!par[n]||par[n][0]<par[n][1]){depart=n;break;}}"
             "const total=Object.values(par).reduce((a,v)=>a+v[0],0);const d=acaLire();d.niveau_test={depart,total,date:Date.now()};acaEcrire(d);"
             "document.getElementById('tn-res').textContent=total+' bonnes réponses sur '+Q.length+'.';"
             "const nom=(NIV.find(x=>x[0]===depart)||[0,''])[1];"
             "document.getElementById('tn-conseil').innerHTML=depart>NIV.length?\"<div class='aca-ex'><h2 style='margin-top:0'>Bravo, tu maîtrises les bases de tous les niveaux</h2><p>Passe directement à l'<a href='examen.html'>examen final</a>, ou révise avec les <a href='revision.html'>révisions express</a>.</p></div>\""
             ":`<div class='aca-ex'><h2 style='margin-top:0'>Commence au niveau ${depart} : ${esc(nom)}</h2><p>Les niveaux précédents semblent acquis : tu peux les survoler et faire seulement leurs quiz. "
             "</p><p><a class='btn' href='../formation.html#niv${depart}'>Aller au niveau ${depart}</a></p></div>`;"
             "document.getElementById('tn-conseil').scrollIntoView({behavior:'smooth',block:'center'});};})();</script>"
             "<nav class='aca-nav'><a class='btn ghost' href='../formation.html'>Retour à l'Académie</a></nav>")
    chemin = "formation/test-de-niveau.html"
    return chemin, seo._page(base, f"Test de niveau en Bourse : par où commencer ? | {seo.NOM}",
                             "Test gratuit de connaissances en Bourse : 14 questions des bases aux notions avancées, pour savoir à quel niveau commencer l'Académie Radar Bourse.",
                             chemin, corps, None, csp=csp, mots="test niveau bourse, test connaissances bourse, quiz bourse débutant, " + MOTS_ACADEMIE)


def _page_revision(seo, base, csp):
    cartes = []
    for c in CHAPITRES:
        for r in c["retenir"]:
            cartes.append(dict(r="À retenir", q=f"{c['titre']} : que faut-il retenir ?", a=r, ch=c["id"], t=c["titre"]))
        for q, choix, b, e in c["quiz"]:
            cartes.append(dict(r="Question", q=q, a=f"{choix[b]}. {e}", ch=c["id"], t=c["titre"]))
    for terme, defi in LEXIQUE.items():
        cartes.append(dict(r="Définition", q=f"Que veut dire « {terme} » ?", a=defi, ch="", t="Lexique"))
    corps = (f"<style>{CSS}{CSS_LEX}</style>{JS_PROGRES}"
             "<p class='aca-fil'><a href='../formation.html'>Académie</a> › Révisions express</p>"
             "<h1>Révisions express</h1>"
             f"<p>{len(cartes)} cartes tirées de l'Académie. Lis la question, essaie de répondre dans ta tête, puis retourne la carte. "
             "Les cartes que tu connais reviennent moins souvent, celles que tu rates reviennent vite : c'est la <b>répétition espacée</b>, "
             "la méthode la plus efficace connue pour mémoriser durablement.</p>"
             "<p class='muted' id='rev-stat'></p><div class='carte-rev' id='rev' tabindex='0' role='button' aria-live='polite'></div>"
             "<div class='rev-btns'><button class='btn ghost' type='button' id='rev-non'>Je ne savais pas</button><button class='btn' type='button' id='rev-oui'>Je savais</button></div>"
             "<script>(function(){const C=" + json.dumps(cartes, ensure_ascii=False) + ";"
             "const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));"
             "const d=acaLire();const R=d.revision||{};const maint=Date.now();"
             "const due=k=>((R[k]||{}).quand||0)<=maint;let file=C.map((c,i)=>i).filter(i=>due(i)).sort(()=>Math.random()-.5);if(!file.length)file=C.map((c,i)=>i).sort(()=>Math.random()-.5);"
             "let cur=null,face=false;const el=document.getElementById('rev');"
             "const stat=()=>{const sues=Object.values(R).filter(x=>(x.boite||0)>=3).length;document.getElementById('rev-stat').textContent=sues+' carte(s) bien mémorisée(s) sur '+C.length+' · '+file.length+' à revoir aujourd\\'hui';};"
             "const montre=()=>{cur=file[0];face=false;const c=C[cur];el.classList.remove('tourne');void el.offsetWidth;el.classList.add('tourne');"
             "el.innerHTML=`<div><small>${esc(c.r)} · ${esc(c.t)}</small>${esc(c.q)}<small style='margin-top:12px'>Touche ou clique pour voir la réponse</small></div>`;stat();};"
             "const retourne=()=>{if(cur===null)return;face=!face;const c=C[cur];el.classList.remove('tourne');void el.offsetWidth;el.classList.add('tourne');"
             "el.innerHTML=face?`<div><small>Réponse</small>${esc(c.a)}${c.ch?`<small style='margin-top:12px'><a href='${c.ch}.html'>Revoir le chapitre</a></small>`:''}</div>`:`<div><small>${esc(c.r)} · ${esc(c.t)}</small>${esc(c.q)}</div>`;};"
             "el.onclick=e=>{if(e.target.closest('a'))return;retourne();};el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();retourne();}};"
             "const note=ok=>{if(cur===null)return;const x=R[cur]||{boite:0};x.boite=ok?Math.min((x.boite||0)+1,5):0;"
             "const jours=[0,1,3,7,16,35][x.boite];x.quand=Date.now()+jours*864e5;R[cur]=x;d.revision=R;acaEcrire(d);"
             "file.shift();if(!ok)file.splice(Math.min(3,file.length),0,cur);if(!file.length){el.innerHTML=\"<div>Bravo, plus rien à revoir aujourd'hui.<small style='margin-top:12px'>Reviens demain : les cartes reviendront au bon moment.</small></div>\";cur=null;stat();return;}montre();};"
             "document.getElementById('rev-oui').onclick=()=>note(true);document.getElementById('rev-non').onclick=()=>note(false);montre();})();</script>"
             "<nav class='aca-nav'><a class='btn ghost' href='../formation.html'>Retour à l'Académie</a></nav>")
    chemin = "formation/revision.html"
    return chemin, seo._page(base, f"Fiches de révision Bourse : flashcards gratuites | {seo.NOM}",
                             "Fiches de révision Bourse gratuites : questions, définitions et points clés de l'Académie, avec répétition espacée pour mémoriser durablement.",
                             chemin, corps, None, csp=csp, mots="fiches de révision bourse, flashcards bourse, réviser la bourse, lexique bourse, " + MOTS_ACADEMIE)
