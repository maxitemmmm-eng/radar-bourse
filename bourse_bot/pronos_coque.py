"""Version 83 : la partie Pronos prend la même architecture que l'Académie.

Sur grand écran : une barre latérale sombre (logo, sélecteur des 3 parties, rubriques groupées avec icônes, carte du Défi du
jour en bas, bouton clair / sombre), le contenu à droite. Chaque partie garde sa couleur (bleu pour les Pronos, vert d'eau
pour l'Académie) mais la même structure : on sait toujours où l'on est. Sur téléphone, rien ne change (barre du haut).
"""
from .academie import SVG

_I = {
    "accueil": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M3 11 12 4l9 7'/><path d='M5 10v10h14V10'/></svg>",
    "crypto": "<svg viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='9'/><path d='M9.5 7.5h4a2.2 2.2 0 0 1 0 4.5h-4zm0 4.5h4.5a2.2 2.2 0 0 1 0 4.5H9.5zM11 6v2m0 8.5v2'/></svg>",
    "bourse": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M3 17l5-5 4 3 8-8'/><path d='M15 7h5v5'/></svg>",
    "liste": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01'/></svg>",
    "themes": "<svg viewBox='0 0 24 24' aria-hidden='true'><rect x='3' y='3' width='7' height='7' rx='1.5'/><rect x='14' y='3' width='7' height='7' rx='1.5'/><rect x='3' y='14' width='7' height='7' rx='1.5'/><circle cx='17.5' cy='17.5' r='3.5'/></svg>",
    "defi": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M7 4h10v5a5 5 0 0 1-10 0z'/><path d='M7 6H4a3 3 0 0 0 3.5 4M17 6h3a3 3 0 0 1-3.5 4M12 14v4M8 21h8'/></svg>",
    "prono": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 4v16M5 11l7-7 7 7'/></svg>",
    "arene": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M5 19 19 5M14 5h5v5M5 5l5 5M14 14l5 5'/></svg>",
    "portefeuille": "<svg viewBox='0 0 24 24' aria-hidden='true'><rect x='3' y='7' width='18' height='13' rx='2'/><path d='M16 13h2M7 7V5h10v2'/></svg>",
    "simulation": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M4 20V10M10 20V4M16 20v-7M22 20H2'/></svg>",
    "resultats": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M9 12l2 2 4-4'/><path d='M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z'/></svg>",
    "journal": "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z'/><path d='M9 9h6M9 13h6'/></svg>",
    "questions": "<svg viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='9'/><path d='M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5V14M12 17h.01'/></svg>",
}

MENU = [
    ("Prédictions de l'IA", [("accueil", "#contenu", "Accueil des pronos"), ("crypto", "prediction-crypto.html", "Prédiction crypto"),
                             ("bourse", "prediction-bourse.html", "Prédiction bourse"), ("liste", "toutes-les-actions.html", "Toutes les actions"),
                             ("themes", "themes.html", "Actions par thème")]),
    ("Jouer et s'entraîner", [("defi", "#defi", "Défi du jour"), ("prono", "#prono", "Pronostic du jour"), ("arene", "#remonte", "L'Arène contre l'IA"),
                              ("portefeuille", "#portefeuille", "Portefeuille virtuel"), ("simulation", "#simulation", "Simulation")]),
    ("L'IA est-elle fiable ?", [("resultats", "avis-surs-verifies.html", "Résultats vérifiés"), ("journal", "journal-ia.html", "Journal de l'IA"),
                                ("questions", "questions-bourse.html", "Vos questions")]),
]


def html(logo_svg: str) -> str:
    nav = "".join(f"<p class='p-groupe'>{g}</p><nav class='p-nav' aria-label=\"{g}\">"
                  + "".join(f"<a href='{h}'{' aria-current=\"page\"' if k == 'accueil' else ''} data-pk='{k}'>{_I[k]}<span>{t}</span></a>" for k, h, t in items)
                  + "</nav>" for g, items in MENU)
    parties = ("<nav class='trois p-parties' aria-label='Les trois parties du site'>"
               f"<a href='#menu' data-partie='menu'>{SVG['menu']}<span>Menu</span></a>"
               f"<a href='#contenu' data-partie='pronos' aria-current='page'>{SVG['pronos']}<span>Pronos</span></a>"
               f"<a href='formation.html' data-partie='apprendre'>{SVG['academie']}<span>Académie</span></a></nav>")
    return (f"<aside class='p-side' aria-label='Navigation des pronos'>"
            f"<a class='p-logo' href='#contenu'>{logo_svg}<span><b>Radar Bourse</b><small>Pronos de l'IA</small></span></a>{parties}{nav}"
            "<a class='p-defi' href='#defi'><span class='l1'><b>Défi du jour</b><span id='p-defi-etat'>à faire</span></span>"
            "<span class='p-jauge'><i id='p-defi-jauge'></i></span><small id='p-defi-txt'>Un dossier d'analyse, noté face à l'IA</small></a>"
            f"<button class='p-theme' type='button' id='p-theme'>{SVG['lune']}<span>Mode clair / sombre</span></button></aside>")


CSS = """
.p-side{display:none}
@media (min-width:1180px){
  body.partie-pronos:has(.p-side:not([hidden])){padding-left:264px}
  body.partie-pronos:has(.p-side:not([hidden])) header.top .brand,body.partie-pronos:has(.p-side:not([hidden])) header.top .trois,body.partie-pronos:has(.p-side:not([hidden])) .nav-ligne .nav-sec{display:none}
  .p-side{display:flex;flex-direction:column;gap:6px;position:fixed;left:0;top:0;bottom:0;width:264px;box-sizing:border-box;padding:18px 14px;overflow:auto;z-index:15;
    background:#0e1628;color:#dbe3f5;--ps-muted:#8c9bbd;--ps-line:#1f2b45;--ps-act:#17233d;border-right:1px solid #1a2540}
  .p-logo{display:flex;align-items:center;gap:10px;padding:2px 8px 14px;text-decoration:none;color:inherit}
  .p-logo svg{width:30px;height:30px;flex:none;view-transition-name:logo}.p-logo b{font-family:var(--f-display,Georgia,serif);font-size:19px;line-height:1.1;display:block}
  .p-logo small{display:block;font-size:12px;color:var(--ps-muted)}
  .p-parties{display:grid!important;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid var(--ps-line);margin:0 0 10px}
  .p-parties a{display:flex;flex-direction:column;align-items:center;gap:3px;padding:7px 2px;border-radius:7px;text-decoration:none;color:var(--ps-muted);font-size:12px;font-weight:600}
  .p-parties a:hover{color:#dbe3f5;background:rgba(255,255,255,.05)}.p-parties a[aria-current]{background:#dbe3f5;color:#0e1628}
  .p-parties svg,.p-nav svg,.p-theme svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;flex:none}
  .p-groupe{font-size:11.5px;font-weight:600;color:var(--ps-muted);padding:12px 10px 4px;margin:0}
  .p-nav{display:flex;flex-direction:column}
  .p-nav a{display:flex;align-items:center;gap:11px;padding:8px 10px;border-radius:8px;text-decoration:none;color:#dbe3f5;font-size:14.5px;font-weight:500;transition:background .15s}
  .p-nav a:hover{background:rgba(255,255,255,.06)}.p-nav a[aria-current]{background:var(--ps-act);box-shadow:inset 3px 0 0 #7398ff;font-weight:600}
  .p-defi{margin-top:auto;display:block;border:1px solid var(--ps-line);border-radius:12px;padding:12px;font-size:13.5px;text-decoration:none;color:#dbe3f5}
  .p-defi:hover{border-color:#7398ff}.p-defi .l1{display:flex;justify-content:space-between;gap:8px}.p-defi .l1 span{color:var(--ps-muted)}
  .p-defi .l1 span.fait{color:#35c27d;font-weight:700}
  .p-jauge{display:block;height:6px;border-radius:99px;background:var(--ps-line);overflow:hidden;margin:10px 0 6px}
  .p-jauge i{display:block;height:100%;width:0;background:linear-gradient(90deg,#7398ff,#35c27d);border-radius:99px;transition:width .8s cubic-bezier(.2,.8,.2,1)}
  .p-defi small{color:var(--ps-muted)}
  .p-theme{display:flex;gap:8px;align-items:center;padding:8px 10px;margin-top:8px;border:0;background:none;color:var(--ps-muted);font:inherit;font-size:13.5px;cursor:pointer;border-radius:8px}
  .p-theme:hover{color:#dbe3f5;background:rgba(255,255,255,.05)}
  body.partie-pronos .titre-ecran{z-index:60}
}
"""

JS = r"""
(function(){
  const side=document.querySelector(".p-side"); if(!side) return;
  const th=document.getElementById("p-theme"), t0=document.getElementById("theme"); if(th&&t0) th.onclick=()=>t0.click();
  // la rubrique active suit le défilement, comme dans l'Académie
  const liens=[...side.querySelectorAll(".p-nav a[href^='#']")];
  const cibles=liens.map(a=>[a,document.getElementById(a.getAttribute("href").slice(1))]).filter(([,s])=>s);
  const actif=a=>side.querySelectorAll(".p-nav a").forEach(x=>x===a?x.setAttribute("aria-current","page"):x.removeAttribute("aria-current"));
  if(window.IntersectionObserver){ const vus=new Map(); const io=new IntersectionObserver(es=>{es.forEach(e=>vus.set(e.target,e.isIntersecting?e.intersectionRatio:0));
      let best=null,v=0; cibles.forEach(([a,s])=>{const r=vus.get(s)||0; if(r>v){v=r;best=a;}}); actif(best||liens[0]); },{threshold:[0,.15,.4]});
    cibles.forEach(([,s])=>io.observe(s)); }
  // la carte du Défi du jour : fait ou à faire, et le score
  try{ const S=JSON.parse(localStorage.getItem("radar-dossier")||"{}"), j=(S.jours||{})[new Date().toISOString().slice(0,10)];
    const e=document.getElementById("p-defi-etat"), g=document.getElementById("p-defi-jauge"), t=document.getElementById("p-defi-txt");
    if(j&&j.fini){ e.textContent=j.score+" / 100"; e.classList.add("fait"); g.style.width=j.score+"%"; t.textContent="Fait aujourd'hui. Nouveau dossier demain."; }
    else if(j){ g.style.width=Math.round(100*(j.k||0)/6)+"%"; e.textContent="étape "+((j.k||0)+1)+" / 6"; }
  }catch(x){}
})();
"""
