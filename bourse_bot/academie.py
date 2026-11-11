"""Version 74 : l'Académie, application d'apprentissage sérieuse, séparée du reste du site.

Principe pédagogique : chaque chapitre = des mini-leçons, chacune suivie d'un mini-exercice corrigé tout de suite,
puis un récap, un cas concret et un bilan. Les erreurs reviennent en fin de chapitre. Série de jours (flamme) et points.
Présentation sobre : programme structuré en modules, plan du chapitre, retours clairs, aucun effet « jeu ».
"""
import html
import json

OBJECTIF_XP = 30

_CLAIR = ("--a-bg:#f5f6f8;--a-card:#ffffff;--a-card2:#eff1f4;--a-ink:#111827;--a-muted:#566070;--a-line:#e1e4e9;"
          "--a-prim:#0b6b63;--a-prim-d:#08524c;--a-soft:#e2f0ee;--a-ok:#15803d;--a-ok-soft:#e6f5eb;--a-ko:#b42318;--a-ko-soft:#fdeceb;"
          "--a-or:#c2610c;--a-or-soft:#fdf0e1;--a-on:#ffffff;--a-gris:#d4d8de;--a-side:#0f1d24;--a-side-ink:#dbe5e8;--a-side-muted:#8fa3aa;--a-side-line:#22343b;--a-side-act:#173038")
_SOMBRE = ("--a-bg:#0d1215;--a-card:#141b1f;--a-card2:#1a2328;--a-ink:#e6edf0;--a-muted:#95a3a9;--a-line:#253136;"
           "--a-prim:#3fbfb1;--a-prim-d:#2b958a;--a-soft:#13302d;--a-ok:#4ade80;--a-ok-soft:#11301e;--a-ko:#f87171;--a-ko-soft:#381718;"
           "--a-or:#f59e0b;--a-or-soft:#35270f;--a-on:#071a18;--a-gris:#2b363b;--a-side:#0a0f12;--a-side-ink:#dbe5e8;--a-side-muted:#869aa1;--a-side-line:#1c282d;--a-side-act:#15282e")

CSS = """
html[data-aca="clair"]{""" + _CLAIR + """}
html[data-aca="sombre"]{""" + _SOMBRE + """}
body.aca-app{--bg:var(--a-bg);--surface:var(--a-card);--surface-2:var(--a-card2);--ink:var(--a-ink);--muted:var(--a-muted);--line:var(--a-line);
  --accent:var(--a-prim);--accent-soft:var(--a-soft);--up:var(--a-ok);--up-soft:var(--a-ok-soft);--down:var(--a-ko);--down-soft:var(--a-ko-soft);
  margin:0;background:var(--a-bg);color:var(--a-ink);font-size:16px;line-height:1.6;color-scheme:light}
html[data-aca="sombre"] body.aca-app{color-scheme:dark}
body.aca-app a{color:var(--a-prim)}
body.aca-app :focus-visible{outline:2px solid var(--a-prim);outline-offset:2px}
.a-skip{position:absolute;left:-999px}.a-skip:focus{left:12px;top:12px;z-index:99;background:var(--a-card);padding:8px 12px}
.a-btn,body.aca-app .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:1px solid var(--a-prim);border-radius:8px;padding:10px 18px;
  font:inherit;font-weight:600;font-size:15px;text-decoration:none;cursor:pointer;background:var(--a-prim);color:var(--a-on);transition:background .15s,border-color .15s}
.a-btn:hover,body.aca-app .btn:hover{background:var(--a-prim-d);border-color:var(--a-prim-d)}
.a-btn.ghost,body.aca-app .btn.ghost{background:var(--a-card);color:var(--a-ink);border-color:var(--a-line)}
.a-btn.ghost:hover,body.aca-app .btn.ghost:hover{border-color:var(--a-muted);background:var(--a-card)}
body.aca-app a.a-btn{color:var(--a-on)}body.aca-app a.a-btn.ghost{color:var(--a-ink)}.a-btn[hidden]{display:none!important}
.a-btn[disabled]{background:var(--a-gris);border-color:var(--a-gris);color:var(--a-muted);cursor:not-allowed}
/* ----- coque : barre latérale sombre, contenu clair ----- */
.a-app{display:grid;grid-template-columns:264px minmax(0,1fr);min-height:100vh}
.a-side{position:sticky;top:0;height:100vh;box-sizing:border-box;padding:18px 14px;background:var(--a-side);color:var(--a-side-ink);display:flex;flex-direction:column;gap:6px;overflow:auto}
.a-logo,body.aca-app .a-logo{display:flex;align-items:center;gap:10px;padding:2px 8px 14px;text-decoration:none;color:inherit}
.a-logo svg{width:30px;height:30px;flex:none}.a-side .a-logo svg{view-transition-name:logo}.a-logo b{font-family:var(--d);font-size:19px;font-weight:700;line-height:1.1}
.a-logo small{display:block;font-size:12px;color:var(--a-side-muted);font-weight:500}
.a-parties{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid var(--a-side-line);margin-bottom:10px}
.a-parties a,body.aca-app .a-parties a{display:flex;flex-direction:column;align-items:center;gap:3px;padding:7px 2px;border-radius:7px;text-decoration:none;color:var(--a-side-muted);font-size:12px;font-weight:600}
.a-parties a:hover{color:var(--a-side-ink);background:rgba(255,255,255,.05)}
.a-parties a[aria-current],body.aca-app .a-parties a[aria-current]{background:var(--a-side-ink);color:var(--a-side)}
.a-parties svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.a-groupe{font-size:11.5px;font-weight:600;color:var(--a-side-muted);padding:12px 10px 4px;letter-spacing:.02em}
.a-nav a,body.aca-app .a-nav a{display:flex;align-items:center;gap:11px;padding:8px 10px;border-radius:8px;text-decoration:none;color:var(--a-side-ink);font-size:14.5px;font-weight:500}
.a-nav a:hover,body.aca-app .a-nav a:hover{background:rgba(255,255,255,.06)}
.a-nav a[aria-current],body.aca-app .a-nav a[aria-current]{background:var(--a-side-act);box-shadow:inset 3px 0 0 var(--a-prim);font-weight:600}
html[data-aca="clair"] .a-nav a[aria-current]{box-shadow:inset 3px 0 0 #3fbfb1}
.a-nav svg{width:19px;height:19px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;opacity:.85}
.a-suivi{margin-top:auto;border:1px solid var(--a-side-line);border-radius:12px;padding:12px;font-size:13.5px}
.a-suivi .l1{display:flex;align-items:center;justify-content:space-between;gap:8px}
.a-flamme{display:inline-flex;align-items:center;gap:5px;font-weight:700;color:#f5a524}
.a-flamme svg{width:18px;height:18px}
.a-flamme.eteinte{color:var(--a-side-muted)}
.a-suivi .pts{color:var(--a-side-muted)}
.a-jauge{height:6px;border-radius:99px;background:var(--a-side-line);overflow:hidden;margin:10px 0 6px}
.a-jauge i{display:block;height:100%;width:0;background:#f5a524;border-radius:99px;transition:width .8s cubic-bezier(.2,.8,.2,1)}
.a-suivi small{color:var(--a-side-muted)}
.a-theme{display:flex;gap:8px;align-items:center;padding:8px 10px;margin-top:8px;border:0;background:none;color:var(--a-side-muted);font:inherit;font-size:13.5px;cursor:pointer;border-radius:8px}
.a-theme:hover{color:var(--a-side-ink);background:rgba(255,255,255,.05)}
.a-main{padding:30px 40px 60px;min-width:0}
.a-col{max-width:820px;margin:0 auto}
.a-top{display:none}.a-tabs{display:none}
@media (max-width:860px){
  .a-app{grid-template-columns:1fr}.a-side{display:none}
  .a-top{display:flex;position:sticky;top:0;z-index:20;align-items:center;justify-content:space-between;gap:10px;padding:10px 16px;background:var(--a-side);color:var(--a-side-ink)}
  .a-top .a-logo{padding:0}.a-top .a-logo b{font-size:16px}.a-top .a-logo svg{width:26px;height:26px}
  .a-top .droite{display:flex;align-items:center;gap:12px;font-size:14px}
  .a-top .droite a{color:var(--a-side-ink)!important;font-weight:600;text-decoration:none;border:1px solid var(--a-side-line);border-radius:8px;padding:5px 9px;font-size:13px}
  .a-main{padding:20px 16px 96px}
  .a-tabs{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:30;background:var(--a-card);border-top:1px solid var(--a-line);padding:6px 4px calc(6px + env(safe-area-inset-bottom,0px));justify-content:space-around}
  .a-tabs a,body.aca-app .a-tabs a{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;font-size:11.5px;font-weight:600;color:var(--a-muted);text-decoration:none;padding:4px 2px;border-radius:8px}
  .a-tabs a[aria-current],body.aca-app .a-tabs a[aria-current]{color:var(--a-prim)}
  .a-tabs svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
.a-pied{font-size:13px;color:var(--a-muted);max-width:820px;margin:48px auto 0;padding-top:16px;border-top:1px solid var(--a-line)}
.a-pied a{color:var(--a-muted)}
.a-carte{background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;padding:18px 20px}
/* ----- programme ----- */
.c-tete h1{font-size:clamp(28px,4vw,36px);margin:0 0 6px}.c-tete p{margin:0;color:var(--a-muted);max-width:640px}
.c-reprendre{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:center;margin:24px 0 14px;border-left:4px solid var(--a-prim)}
.c-reprendre .sur{font-size:13px;color:var(--a-muted);font-weight:600}.c-reprendre h2{margin:2px 0 4px;font-size:21px}.c-reprendre p{margin:0;color:var(--a-muted);font-size:14.5px}
.c-chiffres{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 34px}
.c-chiffres div{background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;padding:14px 16px}
.c-chiffres b{display:block;font-size:24px;font-weight:600;font-family:var(--m);font-variant-numeric:tabular-nums;line-height:1.2}
.c-chiffres div>span{font-size:13px;color:var(--a-muted)}
.c-chiffres .fl b{color:var(--a-or);display:flex;align-items:center;gap:6px}.c-chiffres .fl svg{width:20px;height:20px}
.c-modules{list-style:none;margin:0;padding:0;display:grid;gap:16px}
.c-module{background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;overflow:hidden}
.c-mtete{display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:18px 20px;border-bottom:1px solid var(--a-line)}
.c-num{width:44px;height:44px;border-radius:10px;display:grid;place-items:center;font-weight:700;font-size:18px;color:#fff;background:color-mix(in srgb,var(--c) 80%,#000)}
.c-mtete h2{margin:0;font-size:19px}.c-mtete p{margin:2px 0 0;font-size:14px;color:var(--a-muted)}
.c-mprog{text-align:right;font-size:13px;color:var(--a-muted);min-width:110px}
.c-mprog .barre{height:6px;border-radius:99px;background:var(--a-card2);overflow:hidden;margin-top:6px}
.c-mprog .barre i{display:block;height:100%;width:0;background:var(--a-prim);border-radius:99px;transition:width .8s cubic-bezier(.2,.8,.2,1)}
.c-chaps{list-style:none;margin:0;padding:0}
.c-chaps li+li{border-top:1px solid var(--a-line)}
.c-chaps a,body.aca-app .c-chaps a{display:grid;grid-template-columns:40px 1fr auto;gap:12px;align-items:center;padding:12px 20px;text-decoration:none;color:var(--a-ink)}
.c-chaps a:hover{background:var(--a-card2)}
.c-idx{font-family:var(--m);font-size:13.5px;color:var(--a-muted)}
.c-chaps b{font-weight:600;display:block;line-height:1.35}.c-chaps small{color:var(--a-muted);font-size:13px}
.c-etat{font-size:12.5px;font-weight:600;padding:3px 9px;border-radius:99px;white-space:nowrap;border:1px solid var(--a-line);color:var(--a-muted)}
.c-etat.fait{background:var(--a-ok-soft);border-color:transparent;color:var(--a-ok)}
.c-etat.encours{background:var(--a-soft);border-color:transparent;color:var(--a-prim)}
.c-badge-m{display:flex;gap:10px;align-items:center;padding:10px 20px;font-size:13.5px;color:var(--a-muted);background:var(--a-card2)}
.c-badge-m svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8}
.c-badge-m.ok{color:var(--a-ok)}
.c-exam{margin-top:16px;display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center}
.c-exam .ic{width:44px;height:44px;border-radius:10px;display:grid;place-items:center;background:var(--a-or-soft);color:var(--a-or)}
.c-exam .ic svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.c-exam h2{margin:0;font-size:19px}.c-exam p{margin:2px 0 0;color:var(--a-muted);font-size:14px}
.c-methode{margin-top:40px}.c-methode h2{font-size:22px}
.c-methode ol{padding-left:22px}.c-methode li{margin:6px 0}
.a-auteur{display:flex;gap:12px;align-items:center;font-size:14px;color:var(--a-muted)}
.a-auteur .av{flex:none;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--a-soft);color:var(--a-prim);font-weight:700}
.a-auteur b{color:var(--a-ink)}
@media (max-width:640px){.c-chiffres{grid-template-columns:1fr 1fr}.c-reprendre{grid-template-columns:1fr}.c-mtete{grid-template-columns:auto 1fr}.c-mprog{grid-column:1/-1;text-align:left}
  .c-chaps a{grid-template-columns:34px 1fr;padding:12px 16px}.c-chaps .c-etat{grid-column:2;justify-self:start}.c-exam{grid-template-columns:auto 1fr}.c-exam .a-btn{grid-column:1/-1}}
/* ----- leçon ----- */
.l-top{position:sticky;top:0;z-index:20;background:var(--a-card);border-bottom:1px solid var(--a-line)}
.l-top .in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:16px;padding:12px 20px}
.l-quitter,body.aca-app .l-quitter{display:inline-flex;align-items:center;gap:6px;color:var(--a-muted);text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap}
.l-quitter:hover{color:var(--a-ink)}.l-quitter svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.l-titre{flex:1;min-width:0}.l-titre b{display:block;font-size:14.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.l-titre span{font-size:12.5px;color:var(--a-muted)}
.l-pts{font-size:13.5px;color:var(--a-muted);white-space:nowrap;font-family:var(--m)}
.l-prog{height:3px;background:var(--a-card2)}
.l-prog i{display:block;height:100%;width:0;background:var(--a-prim);transition:width .5s cubic-bezier(.2,.8,.2,1)}
.l-corps{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:250px minmax(0,1fr);gap:40px;padding:28px 20px 190px}
.l-plan{position:sticky;top:90px;align-self:start;font-size:14px}
.l-plan h2{font-size:13px;font-family:inherit;font-weight:600;color:var(--a-muted);margin:0 0 8px}
.l-plan ol{list-style:none;margin:0;padding:0;border-left:2px solid var(--a-line)}
.l-plan li{position:relative;padding:6px 0 6px 18px;color:var(--a-muted);line-height:1.35}
.l-plan li::before{content:"";position:absolute;left:-7px;top:11px;width:12px;height:12px;border-radius:50%;background:var(--a-bg);border:2px solid var(--a-line)}
.l-plan li.ici{color:var(--a-ink);font-weight:600}.l-plan li.ici::before{border-color:var(--a-prim);background:var(--a-prim)}
.l-plan li.fait::before{border-color:var(--a-ok);background:var(--a-ok)}
.l-plan .note{font-size:12.5px;margin-top:14px;color:var(--a-muted)}
.l-main{max-width:680px;min-width:0}
.l-carte{margin:0 0 28px}
.l-type{font-size:13px;font-weight:600;color:var(--a-prim);margin:0 0 6px}
.l-carte h1,.l-carte h2{font-size:28px;line-height:1.2;margin:0 0 14px}
.l-texte{font-size:17px;line-height:1.75}.l-texte p{margin:0 0 14px}
.l-texte table{border-collapse:collapse}.l-texte th,.l-texte td{padding:6px 10px;border-bottom:1px solid var(--a-line);text-align:left;font-size:15px}
.l-exo{background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;padding:22px 24px}
.l-q{font-size:19px;font-weight:600;line-height:1.45;margin:0 0 16px}
.l-choix{display:grid;gap:10px}
.l-choix.vf,.l-choix.lettres{grid-template-columns:repeat(auto-fit,minmax(120px,1fr))}
.l-choix button{all:unset;box-sizing:border-box;display:flex;gap:12px;align-items:center;width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--a-line);
  background:var(--a-card);color:var(--a-ink);cursor:pointer;font-size:16px;line-height:1.4;transition:border-color .12s,background .12s}
.l-choix button:hover{border-color:var(--a-muted)}
.l-choix button:focus-visible{outline:2px solid var(--a-prim);outline-offset:2px}
.l-choix button kbd{flex:none;width:24px;height:24px;border-radius:6px;border:1px solid var(--a-line);display:grid;place-items:center;font:inherit;font-size:12.5px;font-weight:600;color:var(--a-muted);background:var(--a-card2)}
.l-choix button.choisi{border-color:var(--a-prim);background:var(--a-soft);box-shadow:0 0 0 1px var(--a-prim)}
.l-choix button.juste{border-color:var(--a-ok);background:var(--a-ok-soft);box-shadow:0 0 0 1px var(--a-ok)}
.l-choix button.faux{border-color:var(--a-ko);background:var(--a-ko-soft);box-shadow:0 0 0 1px var(--a-ko)}
.l-nombre input{box-sizing:border-box;width:100%;max-width:240px;padding:11px 14px;border-radius:10px;border:1px solid var(--a-line);background:var(--a-card);color:var(--a-ink);font:inherit;font-size:18px;font-family:var(--m)}
.l-nombre input:focus{border-color:var(--a-prim);outline:0;box-shadow:0 0 0 1px var(--a-prim)}
.l-nombre span{color:var(--a-muted);margin-left:10px}
.l-sol summary{cursor:pointer;color:var(--a-prim);font-weight:600;margin-top:12px}
.l-js .l-sol{display:none}
.l-js .l-carte{display:none}.l-js .l-carte.active{display:block}
.l-js .a-auteur{display:none}.l-js:has(.l-carte[data-type=intro].active) .a-auteur,.l-js:has(.l-fin.active) .a-auteur{display:flex}
.l-graph{border:1px solid var(--a-line);border-radius:10px;padding:12px 10px 6px;margin:0 0 16px;background:var(--a-bg)}
svg.g{width:100%;height:auto;display:block;overflow:visible}
svg.g path,svg.g line{fill:none;stroke-linecap:round;stroke-linejoin:round}
.g-axe{stroke:var(--a-line);stroke-width:1.5}.g-prix{stroke:var(--a-prim);stroke-width:2.2}.g-up{stroke:var(--a-ok);stroke-width:2.2}.g-down{stroke:var(--a-ko);stroke-width:2.2}
.g-up-f{fill:var(--a-ok)}.g-ma{stroke:var(--a-or);stroke-width:2.2;stroke-dasharray:6 5}.g-niveau{stroke:var(--a-muted);stroke-width:1.2;stroke-dasharray:4 4}
.g-zone{fill:color-mix(in srgb,var(--a-prim) 14%,transparent)}.g-zone-f{fill:color-mix(in srgb,var(--a-prim) 30%,transparent)}.g-zone2{fill:var(--a-card2)}
.g-cadre{fill:var(--a-card2);stroke:none}.g-pt{fill:var(--a-prim)}.g-pt-bas{fill:var(--a-ko)}
.g-txt{fill:var(--a-muted);font-size:11px;font-family:var(--f)}.g-ma-t{fill:var(--a-or)}
.g-lettre{fill:var(--a-prim);font-size:14px;font-weight:700;font-family:var(--f)}.g-down-t{fill:var(--a-ko)}.g-up-t{fill:var(--a-ok)}
.g-barre{fill:color-mix(in srgb,var(--a-prim) 65%,transparent)}
.l-bas{display:none}
.l-bas.on{display:block;position:fixed;left:0;right:0;bottom:0;z-index:25;border-top:1px solid var(--a-line);background:var(--a-card)}
.l-bas .in{max-width:1180px;margin:0 auto;padding:16px 20px calc(16px + env(safe-area-inset-bottom,0px));display:flex;gap:18px;align-items:center;justify-content:space-between}
.l-retour{flex:1;min-width:0;padding-left:290px}.l-retour b{display:block;font-size:16.5px}.l-retour p{margin:3px 0 0;font-size:14.5px;line-height:1.5;color:var(--a-ink)}
.l-bas .a-btn{min-width:160px}
.l-bas.ok{border-top:3px solid var(--a-ok);background:var(--a-ok-soft)}.l-bas.ok .l-retour b{color:var(--a-ok)}
.l-bas.ko{border-top:3px solid var(--a-ko);background:var(--a-ko-soft)}.l-bas.ko .l-retour b{color:var(--a-ko)}
.l-bas.ok .a-btn{background:var(--a-ok);border-color:var(--a-ok);color:var(--a-on)}.l-bas.ko .a-btn{background:var(--a-ko);border-color:var(--a-ko);color:var(--a-on)}
@media (max-width:980px){.l-corps{grid-template-columns:1fr;gap:0;padding-top:18px}.l-plan{display:none}.l-retour{padding-left:0}}
@media (max-width:600px){.l-bas .in{flex-direction:column;align-items:stretch;gap:12px}.l-bas .a-btn{width:100%}.l-carte h1,.l-carte h2{font-size:23px}.l-exo{padding:18px 16px}.l-pts{display:none}}
.l-fin .bilan{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--a-line);border-radius:12px;overflow:hidden;margin:20px 0}
.l-fin .bilan div{padding:14px 16px;background:var(--a-card)}.l-fin .bilan div+div{border-left:1px solid var(--a-line)}
.l-fin .bilan b{display:block;font-size:22px;font-family:var(--m);font-weight:600}.l-fin .bilan span{font-size:13px;color:var(--a-muted)}
.l-fin .statut{display:flex;align-items:center;gap:12px}
.l-fin .statut .rond{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:var(--a-ok-soft);color:var(--a-ok)}
.l-fin .statut .rond svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.l-fin.rate .statut .rond{background:var(--a-or-soft);color:var(--a-or)}
@media (max-width:600px){.l-fin .bilan{grid-template-columns:1fr 1fr}.l-fin .bilan div:nth-child(3){border-left:0}.l-fin .bilan div:nth-child(n+3){border-top:1px solid var(--a-line)}}
@media (prefers-reduced-motion:no-preference){
  .l-js .l-carte.active{animation:l-entre .3s ease-out}@keyframes l-entre{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
  .l-bas.ok .l-retour,.l-bas.ko .l-retour{animation:l-entre .25s ease-out}
  .a-flamme.vive svg{animation:fl 1.8s ease-in-out infinite;transform-origin:50% 90%}@keyframes fl{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}}
.def-lex{border-bottom-color:var(--a-prim)!important}
"""

SVG = {
    "programme": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16M4 12h16M4 19h10"/></svg>',
    "revision": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="6" width="14" height="14" rx="2"/><path d="M7 3h12a2 2 0 0 1 2 2v12"/></svg>',
    "test": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4h6M10 4v5L5 19a1.5 1.5 0 0 0 1.3 2h11.4a1.5 1.5 0 0 0 1.3-2L14 9V4"/></svg>',
    "examen": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="9" r="5.5"/><path d="M8.5 13.5 7 21l5-2.5 5 2.5-1.5-7.5"/></svg>',
    "lexique": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 7h7"/></svg>',
    "profil": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
    "pronos": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12 19 6"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/></svg>',
    "academie": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 9 12 4l10 5-10 5z"/><path d="M6 11v5c2.5 2.5 9.5 2.5 12 0v-5"/></svg>',
    "flamme": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2c1 3.5 5 5.5 5 11a5 5 0 0 1-10 0c0-2.4 1-4 2.3-5.3.2 1.6.9 2.6 1.9 3.1C11 8 11.2 5 12 2z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    "retour": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>',
    "lune": '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
}

# version 75 : un seul réglage clair / sombre pour tout le site (avant, l'Académie passait en clair et le reste en sombre : changement brutal)
JS_THEME = ('<script>try{var t=localStorage.getItem("radar-theme");document.documentElement.dataset.aca=t==="light"?"clair":"sombre";'
            'document.documentElement.dataset.theme=t==="light"?"light":"dark";}catch(e){document.documentElement.dataset.aca="sombre";}</script>')

JS_STATS = """<script>
(function(){
  const CLE="radar-academie";
  function lire(){try{return JSON.parse(localStorage.getItem(CLE)||"{}")||{}}catch(e){return{}}}
  function jour(t){const d=t?new Date(t):new Date();return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");}
  function serie(d){const j=new Set(d.jours||[]);let n=0,t=Date.now();if(!j.has(jour(t)))t-=864e5;while(j.has(jour(t))){n++;t-=864e5;}return n;}
  function xp(d){let x=d.xp||0;if(!d.xp_migre){x+=d.points_lecons||0;Object.values(d).forEach(v=>{if(v&&typeof v==="object"&&v.score)x+=v.score*10;});}return x;}
  window.acaStats={lire,jour,serie,xp,objectif:""" + str(OBJECTIF_XP) + """};
  const d=lire(),s=serie(d),x=xp(d),xj=(d.xp_jours||{})[jour()]||0, auj=(d.jours||[]).includes(jour());
  document.querySelectorAll("[data-a=serie]").forEach(e=>e.textContent=s);
  document.querySelectorAll("[data-a=serie-j]").forEach(e=>e.textContent=s+(s>1?" jours":" jour"));
  document.querySelectorAll(".a-flamme").forEach(e=>{e.classList.toggle("eteinte",!auj);e.classList.toggle("vive",auj);});
  document.querySelectorAll("[data-a=xp]").forEach(e=>e.textContent=x.toLocaleString("fr-FR"));
  document.querySelectorAll("[data-a=xpj]").forEach(e=>e.textContent=Math.min(xj,""" + str(OBJECTIF_XP) + """)+" / """ + str(OBJECTIF_XP) + """ points aujourd'hui");
  requestAnimationFrame(()=>document.querySelectorAll("[data-a=jauge]").forEach(e=>e.style.width=Math.min(100,xj/""" + str(OBJECTIF_XP) + """*100)+"%"));
  document.querySelectorAll("[data-a=serie-txt]").forEach(e=>e.textContent=auj?"Série entretenue aujourd'hui.":(s?"Fais un exercice aujourd'hui pour garder ta série.":"Fais un exercice pour lancer ta série."));
  const b=document.getElementById("a-theme");if(b)b.onclick=()=>{const n=document.documentElement.dataset.aca==="sombre"?"clair":"sombre";document.documentElement.dataset.aca=n;document.documentElement.dataset.theme=n==="clair"?"light":"dark";try{localStorage.setItem("radar-theme",n==="clair"?"light":"dark")}catch(e){}};
})();
</script>"""

MENU = (("Apprendre", (("programme", "formation.html", "Programme"), ("lexique", "glossaire.html", "Lexique"))),
        ("S'entraîner", (("revision", "formation/revision.html", "Révisions"), ("test", "formation/test-de-niveau.html", "Test de niveau"),
                         ("examen", "formation/examen.html", "Examen final"))),
        ("Mon suivi", (("profil", "formation/profil.html", "Ma progression"),)))
TOUS = [x for _g, items in MENU for x in items]


def _e(s):
    return html.escape(str(s), quote=True)


def onglet_de(chemin):
    return next((k for k, h, _ in TOUS if h == chemin), "programme")


def parties(prefixe):
    """Le sélecteur des 3 parties du site, le même partout : Menu, Pronos, Académie."""
    return ("<nav class='a-parties' aria-label='Les trois parties du site'>"
            f"<a href='{prefixe}index.html#menu'>{SVG['menu']}<span>Menu</span></a>"
            f"<a href='{prefixe}index.html'>{SVG['pronos']}<span>Pronos</span></a>"
            f"<a href='{prefixe}formation.html' aria-current='true'>{SVG['academie']}<span>Académie</span></a></nav>")


def coque(seo, prefixe, chemin, corps):
    actif = onglet_de(chemin)
    nav = "".join(f"<p class='a-groupe'>{g}</p><nav class='a-nav' aria-label='{g}'>"
                  + "".join(f"<a href='{prefixe}{h}'{' aria-current=\"page\"' if k == actif else ''}>{SVG[k]}<span>{t}</span></a>" for k, h, t in items)
                  + "</nav>" for g, items in MENU)
    tabs = "".join(f"<a href='{prefixe}{h}'{' aria-current=\"page\"' if k == actif else ''}>{SVG[k]}<span>{t.replace('Test de niveau', 'Test').replace('Ma progression', 'Suivi')}</span></a>"
                   for k, h, t in TOUS if k in ("programme", "revision", "test", "profil"))
    logo = f"<a class='a-logo' href='{prefixe}formation.html'>{seo.LOGO}<span><b>Radar Bourse</b><small>Académie</small></span></a>"
    suivi = (f"<div class='a-suivi'><div class='l1'><span class='a-flamme' title='Série de jours'>{SVG['flamme']}<span data-a='serie-j'>0 jour</span></span>"
             f"<span class='pts'><span data-a='xp'>0</span> pts</span></div><div class='a-jauge'><i data-a='jauge'></i></div>"
             f"<small data-a='xpj'>0 / {OBJECTIF_XP} points aujourd'hui</small></div>")
    return (f"<a class='a-skip' href='#contenu'>Aller au contenu</a><div class='a-app'>"
            f"<aside class='a-side'>{logo}{parties(prefixe)}{nav}{suivi}"
            f"<button class='a-theme' id='a-theme' type='button'>{SVG['lune']}<span>Mode clair / sombre</span></button></aside>"
            f"<header class='a-top'>{logo}<div class='droite'><span class='a-flamme'>{SVG['flamme']}<span data-a='serie'>0</span></span>"
            f"<a href='{prefixe}index.html'>Pronos</a></div></header>"
            f"<main class='a-main' id='contenu' tabindex='-1'><div class='a-col'>{corps}</div>"
            f"<footer class='a-pied'><p>L'Académie est un projet éducatif et gratuit de {seo.NOM}. Rien de ce qui est écrit ici n'est un conseil en investissement : "
            f"investir comporte un risque de perte en capital. <a href='{prefixe}a-propos.html'>À propos</a> · <a href='{prefixe}contact.html'>Contact</a> · "
            f"<a href='{prefixe}index.html'>Pronos de l'IA</a> · <a href='{prefixe}credits.html'>Crédits</a></p></footer></main></div>"
            f"<nav class='a-tabs' aria-label=\"Menu de l'Académie\">{tabs}</nav>")


def page(seo, base, titre, description, chemin, corps, jsonld=None, csp="", mots=None, lecon=False, image="partage.png"):
    """Équivalent de seo._page pour l'Académie (même référencement, autre coque, autre thème)."""
    image = seo._image_de(chemin, image)
    prefixe = "../" * chemin.count("/")
    csp = seo.csp_avec_stats(csp)
    titre = seo.titre_court(titre)
    description = seo.desc_courte(description)
    corps = seo.typo_fr(corps)
    contenu = corps if lecon else coque(seo, prefixe, chemin, corps)
    return f"""<!doctype html>
<html lang="fr" data-aca="sombre" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{seo.balises_tete(base, titre, description, chemin, image=image, jsonld=jsonld, mots=mots)}
{'<meta name="robots" content="noindex, follow">' if chemin == "formation/profil.html" else ''}
{seo.liens_icones(prefixe)}
{JS_THEME}
{seo.POLICES}
{seo.script_stats()}
{seo.lien_css(prefixe)}
<style>{CSS}</style>
</head>
<body class="aca-app{' aca-lecon' if lecon else ''}">
{contenu}
{JS_STATS}
</body></html>
"""


class SeoAcademie:
    """Fait passer les pages existantes (test, révisions, examen) dans la coque de l'Académie sans toucher à leur code."""
    def __init__(self, seo):
        self._seo = seo

    def __getattr__(self, nom):
        return getattr(self._seo, nom)

    def _page(self, base, titre, description, chemin, corps, jsonld=None, csp="", alternates=None, image="partage.png", mots=None):
        return page(self._seo, base, titre, description, chemin, corps, jsonld, csp=csp, mots=mots, image=image)


# ------------------------------------------------------------------ le programme ------------------------------------------------------------------
def parcours(chapitres, niveaux, verifie_le, nom):
    total_l = sum(len(c["sections"]) for c in chapitres)
    modules = ""
    for n, titre_n, desc, coul in niveaux:
        chs = [(i, c) for i, c in enumerate(chapitres) if c["niveau"] == n]
        lignes = "".join(
            f"<li><a href='formation/{c['id']}.html' data-chap='{c['id']}'><span class='c-idx'>{n}.{k + 1}</span>"
            f"<span><b>{_e(c['titre'])}</b><small>{len(c['sections'])} mini-leçons et exercices · environ {c['minutes'] + 3} min</small></span>"
            f"<span class='c-etat'>À faire</span></a></li>" for k, (i, c) in enumerate(chs))
        modules += (f"<li class='c-module' style='--c:{coul}' id='niv{n}' data-niv='{n}'><div class='c-mtete'><span class='c-num' aria-hidden='true'>{n}</span>"
                    f"<div><h2>Module {n} : {_e(titre_n)}</h2><p>{_e(desc)}</p></div>"
                    f"<div class='c-mprog'><span class='txt'>0 / {len(chs)} chapitres</span><div class='barre'><i></i></div></div></div>"
                    f"<ol class='c-chaps'>{lignes}</ol>"
                    f"<div class='c-badge-m'>{SVG['examen']}<span>Attestation du module {n} : valide les {len(chs)} chapitres pour l'obtenir.</span></div></li>")
    corps = (f"<header class='c-tete'><h1>Apprendre la Bourse, de zéro à l'autonomie</h1>"
             f"<p>{len(chapitres)} chapitres en {len(niveaux)} modules, {total_l} mini-leçons, chacune suivie d'un exercice corrigé. "
             "Gratuit, sans compte : ta progression reste dans ce navigateur.</p></header>"
             "<section class='a-carte c-reprendre' aria-labelledby='rep-t'><div><p class='sur' id='rep-sur'>Pour commencer</p>"
             f"<h2 id='rep-t'>{_e(chapitres[0]['titre'])}</h2><p id='rep-p'>Module 1 · {len(chapitres[0]['sections'])} mini-leçons · environ {chapitres[0]['minutes'] + 3} min</p></div>"
             f"<a class='a-btn' id='rep-a' href='formation/{chapitres[0]['id']}.html'>Commencer</a></section>"
             f"<div class='c-chiffres'><div class='fl'><b>{SVG['flamme']}<span data-a='serie'>0</span></b><span>jours de suite</span></div>"
             f"<div><b><span id='c-n'>0</span> / {len(chapitres)}</b><span>chapitres validés</span></div>"
             "<div><b data-a='xp'>0</b><span>points</span></div>"
             f"<div><b id='c-mod'>0 / {len(niveaux)}</b><span>modules terminés</span></div></div>"
             f"<ol class='c-modules'>{modules}</ol>"
             f"<section class='a-carte c-exam' aria-labelledby='ex-t'><span class='ic'>{SVG['examen']}</span><div><h2 id='ex-t'>Examen final et certificat</h2>"
             "<p>20 questions tirées de tout le programme. 15 bonnes réponses donnent le certificat de l'Académie.</p></div>"
             "<a class='a-btn ghost' href='formation/examen.html'>Passer l'examen</a></section>"
             "<section class='c-methode' aria-labelledby='m-t'><h2 id='m-t'>Comment fonctionne un chapitre</h2><ol>"
             "<li><b>Une mini-leçon</b> de quelques paragraphes, avec les mots techniques expliqués au survol.</li>"
             "<li><b>Un exercice tout de suite après</b> : choix, vrai ou faux, calcul ou lecture de graphique, corrigé et expliqué.</li>"
             "<li><b>Tes erreurs reviennent</b> à la fin du chapitre, puis dans les révisions, pour qu'elles ne se répètent pas.</li>"
             "<li><b>Un récap, un cas concret et un bilan</b> de 3 questions : 2 bonnes réponses valident le chapitre.</li></ol>"
             "<p>Chaque jour où tu fais au moins un exercice entretient ta <b>série</b> (la flamme). L'objectif conseillé : "
             f"{OBJECTIF_XP} points par jour, soit un chapitre environ tous les deux jours.</p>"
             f"<div class='a-auteur'><span class='av' aria-hidden='true'>M</span><p style='margin:0'>Écrit et tenu à jour par <b>maxitemmmm</b>, créateur de {nom}. "
             f"Chaque chiffre est relu à partir des sources officielles (AMF, impots.gouv.fr, service-public.fr, Banque de France), dernière relecture le {verifie_le}. "
             "Une erreur ou une idée de chapitre ? <a href='contact.html'>Écris-moi</a>.</p></div></section>")
    js = ("<script>document.addEventListener('DOMContentLoaded',function(){const S=window.acaStats;const d=S?S.lire():{};"
          "const liens=[...document.querySelectorAll('[data-chap]')];let n=0;"
          "liens.forEach(a=>{const x=d[a.dataset.chap],e=a.querySelector('.c-etat');if(x&&x.fait){e.textContent='Validé';e.classList.add('fait');n++;}"
          "else if(x&&x.etape){e.textContent='Commencé';e.classList.add('encours');}});"
          "document.getElementById('c-n').textContent=n;let m=0;"
          "document.querySelectorAll('.c-module').forEach(mo=>{const ls=[...mo.querySelectorAll('[data-chap]')],f=ls.filter(a=>d[a.dataset.chap]&&d[a.dataset.chap].fait).length;"
          "mo.querySelector('.c-mprog .txt').textContent=f+' / '+ls.length+' chapitres';requestAnimationFrame(()=>mo.querySelector('.c-mprog i').style.width=(100*f/ls.length)+'%');"
          "if(f===ls.length){m++;const b=mo.querySelector('.c-badge-m');b.classList.add('ok');b.querySelector('span').textContent='Attestation du module obtenue.';}});"
          f"document.getElementById('c-mod').textContent=m+' / {len(niveaux)}';"
          "const suite=liens.find(a=>!(d[a.dataset.chap]&&d[a.dataset.chap].fait));"
          "if(n>0&&suite){document.getElementById('rep-sur').textContent='Reprendre où tu en étais';document.getElementById('rep-t').textContent=suite.querySelector('b').textContent;"
          "document.getElementById('rep-p').textContent='Chapitre '+suite.querySelector('.c-idx').textContent+' · '+suite.querySelector('small').textContent;"
          "const a=document.getElementById('rep-a');a.href=suite.getAttribute('href');a.textContent='Continuer';}"
          "else if(!suite){document.getElementById('rep-sur').textContent='Programme terminé';document.getElementById('rep-t').textContent='Passe l\\u2019examen final';"
          "document.getElementById('rep-p').textContent='Tous les chapitres sont validés.';const a=document.getElementById('rep-a');a.href='formation/examen.html';a.textContent='Passer l\\u2019examen';}"
          "const t=d.niveau_test;if(n===0&&t&&t.depart>1&&t.depart<=" + str(len(niveaux)) + "){const p=document.querySelector('.c-module[data-niv=\"'+t.depart+'\"] [data-chap]');"
          "if(p){document.getElementById('rep-sur').textContent='Conseillé par ton test de niveau';document.getElementById('rep-t').textContent=p.querySelector('b').textContent;"
          "const a=document.getElementById('rep-a');a.href=p.getAttribute('href');}}"
          "});</script>")
    return corps + js


# ------------------------------------------------------------------ la leçon ------------------------------------------------------------------
def _nombre_fr(x):
    return f"{x:,.2f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",")


def _carte_exo(ex, k, groupe, bilan=False, type_txt=None):
    t = ex["type"]
    if t == "nombre":
        sol = f"{_nombre_fr(ex['rep'])} {ex['unite']}".strip()
        zone = (f"<div class='l-nombre'><label class='sr' for='n{k}'>Ta réponse</label><input id='n{k}' inputmode='decimal' autocomplete='off' placeholder='Ta réponse'>"
                f"<span>{_e(ex['unite'])}</span></div>")
        attrs = f"data-rep='{ex['rep']}' data-tol='{ex['tol']}' data-sol=\"{_e(sol)}\""
    else:
        sol = ex["choix"][ex["bonne"]]
        lettres = all(len(c) <= 6 for c in ex["choix"])
        cls = " vf" if t == "vf" else (" lettres" if lettres else "")
        zone = (f"<div class='l-choix{cls}' role='group' aria-label='Choisis une réponse'>"
                + "".join(f"<button type='button' data-j='{j}' aria-pressed='false'><kbd aria-hidden='true'>{j + 1}</kbd><span>{_e(c)}</span></button>" for j, c in enumerate(ex["choix"]))
                + "</div>")
        attrs = f"data-bonne='{ex['bonne']}' data-sol=\"{_e(sol)}\" data-melange='{0 if t == 'vf' or lettres else 1}'"
    graph = f"<div class='l-graph'>{ex['svg']}</div>" if t == "graphique" else ""
    titre = type_txt or {"qcm": "Exercice", "vf": "Exercice : vrai ou faux", "nombre": "Exercice : calcul", "graphique": "Exercice : lecture de graphique"}[t]
    return (f"<section class='l-carte' data-type='exo' data-g='{groupe}' {attrs}{' data-bilan=\"1\"' if bilan else ''} data-expl=\"{_e(ex['expl'])}\">"
            f"<p class='l-type'>{titre}</p><div class='l-exo'>{graph}<p class='l-q'>{_e(ex['q'])}</p>{zone}"
            f"<details class='l-sol'><summary>Voir la réponse</summary><p><b>{_e(sol)}</b>. {_e(ex['expl'])}</p></details></div></section>")


JS_LECON = """<script>
(function(){
  const main=document.getElementById("contenu"); if(!main) return; main.classList.add("l-js");
  const bas=document.getElementById("l-bas"); bas.classList.add("on");
  const action=document.getElementById("l-action"), retour=document.getElementById("l-retour"), prog=document.querySelector(".l-prog i"), pts=document.getElementById("l-pts"), etp=document.getElementById("l-etape");
  const cartes=[...main.querySelectorAll(".l-carte:not(.l-fin)")]; const id=document.body.dataset.chap; const plan=[...document.querySelectorAll(".l-plan li")];
  let file=cartes.map((c,i)=>i), pos=0, etat="lire", choix=null, xp=0, justes=0, essais=0, bilanOK=0, bilanN=0, faites=new Set(), revues=new Set();
  cartes.forEach(c=>{const ch=c.querySelector(".l-choix"); if(ch&&c.dataset.melange==="1"){const bs=[...ch.children]; bs.sort(()=>Math.random()-.5).forEach((b,i)=>{b.querySelector("kbd").textContent=i+1; ch.appendChild(b);});}
    if(ch) ch.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{ if(etat!=="repondre") return; ch.querySelectorAll("button").forEach(x=>{x.classList.remove("choisi");x.setAttribute("aria-pressed","false");});
      b.classList.add("choisi"); b.setAttribute("aria-pressed","true"); choix=b.dataset.j; action.disabled=false; }));
    const inp=c.querySelector(".l-nombre input"); if(inp) inp.addEventListener("input",()=>{ if(etat==="repondre") action.disabled=!inp.value.trim(); });
  });
  const total=cartes.length;
  function majProg(){prog.style.width=Math.round(100*faites.size/total)+"%"; const g=cartes[file[Math.min(pos,file.length-1)]].dataset.g;
    plan.forEach(l=>{const k=l.dataset.g, cs=cartes.map((c,i)=>[c,i]).filter(([c])=>c.dataset.g===k); l.classList.toggle("fait",cs.every(([c,i])=>faites.has(i))); l.classList.toggle("ici",k===g&&!l.classList.contains("fait"));});
    etp.textContent="Étape "+Math.min(pos+1,file.length)+" sur "+file.length; pts.textContent=xp?"+"+xp+" points":"";}
  function bandeau(cls,html){bas.className="l-bas on "+cls; retour.innerHTML=html;}
  function montre(){
    const c=cartes[file[pos]]; cartes.forEach(x=>x.classList.remove("active")); c.classList.add("active"); scrollTo({top:0});
    const h=c.querySelector("h1,h2,.l-q"); if(h){h.tabIndex=-1; h.focus({preventScroll:true});}
    choix=null; bandeau("",""); const t=c.dataset.type;
    if(t==="exo"){ etat="repondre"; action.textContent="Vérifier"; action.disabled=true;
      c.querySelectorAll(".l-choix button").forEach(b=>{b.classList.remove("choisi","juste","faux");b.disabled=false;b.setAttribute("aria-pressed","false");});
      const inp=c.querySelector(".l-nombre input"); if(inp){inp.value="";inp.disabled=false;setTimeout(()=>inp.focus(),60);}
      if(revues.has(file[pos])) bandeau("","<p style='margin:0'><b style='display:inline;font-size:15px'>Deuxième essai.</b> Cette question t'avait posé problème : reprends-la.</p>");
    } else if(t==="pratique"){ etat="pratique"; action.textContent="Voir la correction"; action.disabled=false; c.querySelector(".l-cor").hidden=true; }
    else { etat="lire"; action.textContent=t==="intro"?"Commencer le chapitre":"Continuer"; action.disabled=false; }
    majProg();
  }
  function verifier(){
    const i=file[pos], c=cartes[i]; let ok;
    const inp=c.querySelector(".l-nombre input");
    if(inp){ const v=parseFloat(inp.value.replace(/\\s|€|%/g,"").replace(",",".")); if(isNaN(v)){bandeau("ko","<b>Entre un nombre</b><p>Par exemple 12 ou 12,5.</p>");return;}
      ok=Math.abs(v-(+c.dataset.rep))<=(+c.dataset.tol)+1e-9; inp.disabled=true; }
    else { ok=choix===c.dataset.bonne; c.querySelectorAll(".l-choix button").forEach(b=>{b.disabled=true; b.classList.remove("choisi"); if(b.dataset.j===c.dataset.bonne)b.classList.add("juste"); else if(b.dataset.j===choix)b.classList.add("faux");}); }
    const premier=!revues.has(i);
    if(c.dataset.bilan){bilanN+=premier?1:0; if(ok&&premier)bilanOK++;}
    if(premier) essais++;
    if(ok){ if(premier)justes++; xp+=premier?10:5; faites.add(i); bandeau("ok","<b>Bonne réponse</b><p>"+c.dataset.expl+"</p>"); }
    else { bandeau("ko","<b>Réponse attendue : "+c.dataset.sol+"</b><p>"+c.dataset.expl+"</p>"); if(!revues.has(i)){revues.add(i); file.push(i);} else faites.add(i); }
    etat="suite"; action.textContent="Continuer"; action.disabled=false; majProg(); setTimeout(()=>action.focus(),40);
  }
  function suivant(){ const i=file[pos]; if(cartes[i].dataset.type!=="exo") faites.add(i); pos++; if(pos>=file.length) fin(); else montre(); }
  function fin(){
    const d=acaStats.lire(), j=acaStats.jour(), x=d[id]||{}; const deja=!!x.fait; const besoin=Math.ceil(bilanN*2/3); const valide=bilanOK>=besoin;
    const gain=deja?Math.round(xp/4):xp+(valide?20:0);
    if(!d.xp_migre){d.xp=acaStats.xp(d); d.xp_migre=1;}
    d.xp=(d.xp||0)+gain; d.xp_jours=d.xp_jours||{}; d.xp_jours[j]=(d.xp_jours[j]||0)+gain; d.jours=[...new Set([...(d.jours||[]),j])].slice(-400);
    d[id]=Object.assign(x,{score:Math.max(x.score||0,bilanOK),total:bilanN,fait:deja||valide,etape:99,date:Date.now()}); d.serie_max=Math.max(d.serie_max||0,acaStats.serie(d));
    try{localStorage.setItem("radar-academie",JSON.stringify(d))}catch(e){}
    const prec=essais?Math.round(100*justes/essais):100;
    cartes.forEach(c=>c.classList.remove("active")); prog.style.width="100%"; plan.forEach(l=>{l.classList.remove("ici");l.classList.add("fait");}); etp.textContent="Chapitre terminé";
    const f=document.getElementById("l-fin"); f.hidden=false; f.classList.add("active"); f.classList.toggle("rate",!valide);
    f.querySelector("[data-f=titre]").textContent=valide?(deja?"Chapitre révisé":"Chapitre validé"):"Chapitre pas encore validé";
    f.querySelector("[data-f=texte]").textContent=valide?(deja?"Bonne révision. Les notions de ce chapitre sont fraîches.":"Le chapitre compte maintenant pour l'attestation du module.")
      :"Il faut "+besoin+" bonnes réponses sur "+bilanN+" au bilan pour valider (tu en as "+bilanOK+"). Relis le récap puis recommence : les points gagnés restent acquis.";
    f.querySelector("[data-f=bilan]").textContent=bilanOK+" / "+bilanN; f.querySelector("[data-f=prec]").textContent=prec+" %";
    f.querySelector("[data-f=xp]").textContent="+"+gain; const s=acaStats.serie(d); f.querySelector("[data-f=serie]").textContent=s+(s>1?" jours":" jour");
    if(!valide){const r=f.querySelector("[data-f=refaire]"); r.hidden=false; r.onclick=()=>location.reload();}
    bandeau("",""); action.textContent=valide?(document.body.dataset.suite.endsWith("formation.html")?"Retour au programme":"Chapitre suivant"):"Retour au programme";
    action.dataset.va=valide?"":"../formation.html"; etat="fin"; action.disabled=false; scrollTo({top:0});
  }
  action.addEventListener("click",()=>{ if(action.disabled) return;
    if(etat==="repondre") verifier(); else if(etat==="pratique"){ cartes[file[pos]].querySelector(".l-cor").hidden=false; etat="lire"; action.textContent="Continuer"; }
    else if(etat==="fin") location.href=action.dataset.va||document.body.dataset.suite; else suivant(); });
  document.addEventListener("keydown",e=>{ if(e.target.tagName==="TEXTAREA") return;
    if(e.key==="Enter"&&!(e.target.tagName==="BUTTON"&&e.target!==action)&&!(e.target.tagName==="A")){ e.preventDefault(); action.click(); }
    if(etat==="repondre"&&/^[1-6]$/.test(e.key)&&e.target.tagName!=="INPUT"){ const c=cartes[file[pos]]; const b=[...c.querySelectorAll(".l-choix button")][+e.key-1]; if(b) b.click(); } });
  montre();
})();
</script>"""


def lecon(seo, ch, i, chapitres, niveaux, exos, graphes, lexique, verifie_le):
    niv = next(n for n in niveaux if n[0] == ch["niveau"])
    suiv = chapitres[i + 1] if i + 1 < len(chapitres) else None
    n_l = len(ch["sections"])
    k_mod = [c["id"] for c in chapitres if c["niveau"] == niv[0]].index(ch["id"]) + 1
    noms = [t.split(". ", 1)[1] if t[:1].isdigit() and ". " in t[:4] else t for t, _ in ch["sections"]]
    cartes = [f"<section class='l-carte' data-type='intro' data-g='intro'><p class='l-type'>Module {niv[0]} : {_e(niv[1])} · Chapitre {niv[0]}.{k_mod}</p>"
              f"<h1>{_e(ch['titre'])}</h1><div class='l-texte'><p>{_e(ch['desc'])}</p>"
              f"<p><b>Dans ce chapitre</b> : {n_l} mini-leçons ({', '.join(_e(x) for x in noms)}), chacune suivie d'un exercice, "
              f"puis un récap, un cas concret et un bilan de {len(ch['quiz'])} questions. Environ {ch['minutes'] + 3} minutes.</p></div></section>"]
    k = 0
    for s, (t_aff, h2) in enumerate(zip(noms, lexique)):
        g = f"l{s}"
        cartes.append(f"<section class='l-carte' data-type='lecon' data-g='{g}'><p class='l-type'>Mini-leçon {s + 1} sur {n_l}</p><h2>{_e(t_aff)}</h2><div class='l-texte'>{h2}</div></section>")
        cartes.append(_carte_exo(exos[s], k, g)); k += 1
        for (si, gx) in graphes:
            if si == s:
                cartes.append(_carte_exo(gx, k, g)); k += 1
    cartes.append("<section class='l-carte' data-type='recap' data-g='recap'><p class='l-type'>Récap</p><h2>Ce qu'il faut retenir</h2><div class='l-texte'><ul>"
                  + "".join(f"<li>{_e(x)}</li>" for x in ch["retenir"]) + "</ul></div></section>")
    enonce, correction = ch["exercice"]
    cartes.append(f"<section class='l-carte' data-type='pratique' data-g='cas'><p class='l-type'>Cas concret</p><h2>À toi de raisonner</h2><div class='l-texte'>{enonce}"
                  "<label class='sr' for='l-brouillon'>Ton raisonnement</label><textarea id='l-brouillon' rows='3' placeholder='Écris ton raisonnement ici (facultatif)' "
                  "style='width:100%;box-sizing:border-box;border-radius:10px;border:1px solid var(--a-line);background:var(--a-card);color:var(--a-ink);font:inherit;padding:12px'></textarea>"
                  f"<div class='l-cor'><h3>Correction</h3>{correction}</div></div></section>")
    for q, choix, b, e in ch["quiz"]:
        cartes.append(_carte_exo({"type": "qcm", "q": q, "choix": choix, "bonne": b, "expl": e}, k, "bilan", bilan=True, type_txt="Bilan du chapitre")); k += 1
    fin = ("<section class='l-carte l-fin' id='l-fin' data-type='fin' hidden><div class='statut'><span class='rond'>" + SVG["check"] + "</span>"
           "<div><h2 data-f='titre' style='margin:0'>Chapitre validé</h2><p data-f='texte' style='margin:2px 0 0;color:var(--a-muted)'></p></div></div>"
           "<div class='bilan'><div><b data-f='bilan'>0</b><span>au bilan</span></div><div><b data-f='prec'>0</b><span>de bonnes réponses du premier coup</span></div>"
           "<div><b data-f='xp'>0</b><span>points gagnés</span></div><div><b data-f='serie' style='color:var(--a-or)'>0</b><span>de série</span></div></div>"
           "<p><button class='a-btn ghost' type='button' data-f='refaire' hidden>Recommencer le chapitre</button></p>"
           "<p class='muted' style='font-size:14.5px'>Les notions de ce chapitre reviendront dans les <a href='revision.html'>révisions</a>, au bon moment pour ne pas les oublier.</p></section>")
    plan = ("<aside class='l-plan' aria-label='Plan du chapitre'><h2>Plan du chapitre</h2><ol>"
            + "".join(f"<li data-g='l{s}'>{_e(x)}</li>" for s, x in enumerate(noms))
            + "<li data-g='recap'>Récap</li><li data-g='cas'>Cas concret</li><li data-g='bilan'>Bilan</li></ol>"
            + "<p class='note'>Raccourcis : touches 1 à 4 pour répondre, Entrée pour valider.</p></aside>")
    corps = (f"<header class='l-top'><div class='in'><a class='l-quitter' href='../formation.html'>{SVG['retour']}<span>Programme</span></a>"
             f"<div class='l-titre'><b>{niv[0]}.{k_mod} · {_e(ch['titre'])}</b><span id='l-etape'>Module {niv[0]} : {_e(niv[1])}</span></div>"
             f"<span class='l-pts' id='l-pts' aria-live='polite'></span></div><div class='l-prog' role='presentation'><i></i></div></header>"
             f"<div class='l-corps'>{plan}<main class='l-main' id='contenu'>{''.join(cartes)}{fin}"
             "<div class='a-auteur' style='margin-top:30px'><span class='av' aria-hidden='true'>M</span><p style='margin:0'>Écrit et vérifié par <b>maxitemmmm</b>. "
             f"Chiffres relus le {verifie_le}. Sources : "
             + ", ".join(f"<a href='{_e(u)}'" + ("" if u.startswith("..") else " rel='noopener noreferrer'") + f">{_e(n)}</a>" for n, u in ch["sources"])
             + ". Une erreur ? <a href='../contact.html'>Signale-la</a>.</p></div></main></div>"
             "<div class='l-bas' id='l-bas'><div class='in'><div class='l-retour' id='l-retour' role='status' aria-live='polite'></div>"
             "<button class='a-btn' id='l-action' type='button'>Continuer</button></div></div>"
             f"<script>document.body.dataset.chap={json.dumps(ch['id'])};document.body.dataset.suite={json.dumps((suiv['id'] + '.html') if suiv else '../formation.html')};</script>"
             + JS_LECON)
    return corps


def profil(niveaux, chapitres):
    lignes = "".join(f"<li data-niv='{n}'><span class='ic'>{SVG['examen']}</span><div><b>Attestation du module {n}</b><small>{_e(t)}</small></div><span class='c-etat'>À obtenir</span></li>"
                     for n, t, _d, _c in niveaux)
    autres = (("serie7", "Régularité", "7 jours de suite"), ("serie30", "Assiduité", "30 jours de suite"),
              ("xp1000", "1 000 points", "Cumuler 1 000 points"), ("certif", "Certificat de l'Académie", "Réussir l'examen final"))
    lignes += "".join(f"<li data-b='{k}'><span class='ic'>{SVG['flamme'] if k.startswith('serie') else SVG['examen']}</span><div><b>{t}</b><small>{d}</small></div><span class='c-etat'>À obtenir</span></li>"
                      for k, t, d in autres)
    return ("<style>.pf-liste{list-style:none;padding:0;margin:0;background:var(--a-card);border:1px solid var(--a-line);border-radius:12px;overflow:hidden}"
            ".pf-liste li{display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:center;padding:12px 18px}.pf-liste li+li{border-top:1px solid var(--a-line)}"
            ".pf-liste .ic{width:36px;height:36px;border-radius:9px;display:grid;place-items:center;background:var(--a-card2);color:var(--a-muted)}"
            ".pf-liste .ic svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8}.pf-liste li[data-b^=serie] .ic svg{fill:currentColor;stroke:none}"
            ".pf-liste li.ok .ic{background:var(--a-ok-soft);color:var(--a-ok)}.pf-liste b{display:block;font-weight:600}.pf-liste small{color:var(--a-muted)}"
            ".pf-cal{display:grid;grid-template-columns:repeat(14,minmax(0,22px));gap:5px;margin:12px 0 4px}.pf-cal i{aspect-ratio:1;border-radius:4px;background:var(--a-card2)}.pf-cal i.on{background:var(--a-or)}</style>"
            "<header class='c-tete'><h1>Ma progression</h1><p>Enregistrée uniquement dans ce navigateur, sans compte.</p></header>"
            f"<div class='c-chiffres' style='margin-top:22px'><div class='fl'><b>{SVG['flamme']}<span data-a='serie'>0</span></b><span>jours de suite</span></div>"
            "<div><b id='pf-record'>0</b><span>meilleure série</span></div><div><b data-a='xp'>0</b><span>points au total</span></div>"
            f"<div><b><span id='pf-chap'>0</span> / {len(chapitres)}</b><span>chapitres validés</span></div></div>"
            "<section class='a-carte' style='margin-bottom:26px'><h2 style='font-size:18px;margin:0'>Les 4 dernières semaines</h2>"
            "<div class='pf-cal' id='pf-cal' aria-label='Jours où tu as fait au moins un exercice'></div><p class='muted' style='font-size:13.5px;margin:6px 0 0' data-a='serie-txt'></p></section>"
            f"<h2 style='font-size:20px'>Attestations et distinctions</h2><ul class='pf-liste'>{lignes}</ul>"
            "<h2 style='font-size:20px;margin-top:34px'>Réinitialiser</h2><p class='muted'>Efface toute ta progression de l'Académie sur ce navigateur.</p>"
            "<button class='a-btn ghost' type='button' id='pf-raz'>Effacer ma progression</button><p id='pf-raz-ok' class='muted' role='status'></p>"
            "<script>document.addEventListener('DOMContentLoaded',function(){const S=window.acaStats;if(!S)return;const d=S.lire(),ids=" + json.dumps([c["id"] for c in chapitres])
            + ",niv=" + json.dumps({c["id"]: c["niveau"] for c in chapitres}) + ";"
            "const n=ids.filter(i=>d[i]&&d[i].fait).length;document.getElementById('pf-chap').textContent=n;const s=S.serie(d),rec=Math.max(d.serie_max||0,s);"
            "document.getElementById('pf-record').textContent=rec;const x=S.xp(d);"
            "const j=new Set(d.jours||[]),cal=document.getElementById('pf-cal');for(let k=27;k>=0;k--){const e=document.createElement('i');const jj=S.jour(Date.now()-k*864e5);if(j.has(jj))e.className='on';e.title=jj;cal.appendChild(e);}"
            "function ok(li){li.classList.add('ok');const e=li.querySelector('.c-etat');e.textContent='Obtenu';e.classList.add('fait');}"
            "document.querySelectorAll('li[data-niv]').forEach(li=>{const k=+li.dataset.niv;if(ids.filter(i=>niv[i]===k).every(i=>d[i]&&d[i].fait))ok(li);});"
            "const c={serie7:rec>=7,serie30:rec>=30,xp1000:x>=1000,certif:!!(d.examen&&d.examen.reussi)};document.querySelectorAll('li[data-b]').forEach(li=>{if(c[li.dataset.b])ok(li);});"
            "const r=document.getElementById('pf-raz');let arme=false;r.onclick=()=>{if(!arme){arme=true;r.textContent='Confirmer l\\u2019effacement';return;}"
            "try{localStorage.removeItem('radar-academie')}catch(e){}document.getElementById('pf-raz-ok').textContent='Progression effacée.';r.textContent='Effacer ma progression';arme=false;};});</script>")
