"""Transitions entre les pages, partagées par le site, l'appli et l'Académie.

Version 75 : fondu doux. Version 83 : de vraies mini-animations.
- Changement de page : l'ancienne page recule légèrement et s'efface, la nouvelle glisse en place.
- Changement de PARTIE (Pronos ↔ Académie ↔ Menu) : la nouvelle partie s'ouvre en cercle depuis l'endroit du clic.
- Une fine barre de chargement en haut dès le clic, pour que rien ne paraisse figé.
- Dans l'appli, un lien vers une section (#defi, #prono…) fait défiler en douceur puis fait « entrer » la section.
Tout est désactivé si l'utilisateur a demandé moins d'animations (réglage du système ou bouton « Sans animation »).
"""
CSS = """
@view-transition{navigation:auto}
::view-transition-old(root){animation:vt-sort .26s cubic-bezier(.4,0,1,1) both}
::view-transition-new(root){animation:vt-entre .42s cubic-bezier(.2,.8,.2,1) both}
@keyframes vt-sort{to{opacity:0;transform:scale(.985)}}
@keyframes vt-entre{from{opacity:0;transform:translateY(12px) scale(.996)}}
html:active-view-transition-type(partie)::view-transition-old(root){animation:vt-recule .5s cubic-bezier(.4,0,.2,1) both}
html:active-view-transition-type(partie)::view-transition-new(root){animation:vt-cercle .55s cubic-bezier(.6,0,.2,1) both}
@keyframes vt-recule{to{opacity:.35;transform:scale(.96)}}
@keyframes vt-cercle{from{clip-path:circle(0 at var(--vt-x,50%) var(--vt-y,50%))}to{clip-path:circle(150vmax at var(--vt-x,50%) var(--vt-y,50%))}}
@supports not (view-transition-name:none){@media (prefers-reduced-motion:no-preference){body{animation:vt-entre .35s ease-out both}}}
.vt-barre{position:fixed;left:0;top:0;height:3px;width:0;z-index:2147483000;pointer-events:none;background:linear-gradient(90deg,#3fbfb1,#7398ff);box-shadow:0 0 8px rgba(115,152,255,.6);transition:width 2.5s cubic-bezier(.1,.7,.2,1),opacity .2s}
.vt-barre.on{width:82%}
.vt-section{animation:vt-section .55s cubic-bezier(.2,.8,.2,1) both}
@keyframes vt-section{from{opacity:.25;transform:translateY(18px)}}
@media (prefers-reduced-motion:reduce){@view-transition{navigation:none}.vt-barre{display:none}.vt-section{animation:none}}
html[data-calme] .vt-section,.calme .vt-section{animation:none}
"""

CODE = r"""
(function(){
  if(window.__vt) return; window.__vt=1;
  const calme=()=>matchMedia("(prefers-reduced-motion: reduce)").matches||document.documentElement.classList.contains("calme")||document.body.classList.contains("calme");
  const partie=p=>/formation|glossaire|lexique/.test(p)?"academie":"pronos";
  let barre=null;
  function charge(){ if(calme()) return; barre=barre||Object.assign(document.createElement("div"),{className:"vt-barre"}); if(!barre.isConnected) document.body.appendChild(barre);
    barre.style.opacity="1"; barre.classList.remove("on"); void barre.offsetWidth; barre.classList.add("on"); }
  document.addEventListener("click",e=>{
    const a=e.target.closest&&e.target.closest("a[href]"); if(!a||e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||a.target==="_blank"||a.hasAttribute("download")) return;
    let u; try{u=new URL(a.href,location.href);}catch(x){return;}
    if(u.origin!==location.origin) return;
    if(u.pathname===location.pathname&&u.hash){   // une section de la même page
      const cible=u.hash.length>1&&document.getElementById(decodeURIComponent(u.hash.slice(1)));
      if(cible&&!calme()&&cible.tagName==="SECTION"){ setTimeout(()=>{cible.classList.remove("vt-section");void cible.offsetWidth;cible.classList.add("vt-section");},220); }
      return;
    }
    try{ sessionStorage.setItem("vt-clic",JSON.stringify({x:e.clientX,y:e.clientY,de:partie(location.pathname),vers:partie(u.pathname),t:Date.now()})); }catch(x){}
    charge();
  },true);
  addEventListener("pageshow",()=>{ if(barre){barre.style.opacity="0";barre.classList.remove("on");} });
  addEventListener("pagereveal",e=>{
    if(!e.viewTransition) return;
    try{ const c=JSON.parse(sessionStorage.getItem("vt-clic")||"null"); sessionStorage.removeItem("vt-clic");
      if(c&&Date.now()-c.t<4000&&c.de!==c.vers){ const r=document.documentElement.style; r.setProperty("--vt-x",c.x+"px"); r.setProperty("--vt-y",c.y+"px"); e.viewTransition.types.add("partie"); }
    }catch(x){}
  });
})();
"""
JS = "<script>" + CODE + "</script>"
