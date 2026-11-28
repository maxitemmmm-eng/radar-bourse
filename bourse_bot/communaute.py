"""Version 119 : la communauté Radar Bourse — comptes, commentaires modérés, sauvegarde de « Mon espace » dans le compte.

Le serveur (serveur_communaute/worker.js) tourne gratuitement chez Cloudflare ; il est installé par installer_communaute.py,
qui enregistre son adresse dans la variable GitHub RADAR_COMMU_API. Tant qu'elle n'est pas réglée, rien n'apparaît sur le site.

Ce que voit le visiteur :
- « Mon compte » (compte.html) : créer un compte (pseudo + mot de passe, sans e-mail), se connecter, code de secours,
  sauvegarder / récupérer sa progression (Académie, portefeuille, favoris…) sur tous ses appareils, supprimer son compte ;
- des commentaires en bas de chaque fiche et dans la page « Discussions » (4 salons), avec signalement ;
- les règles de la communauté et ce qui est enregistré (regles-communaute.html).
Pour toi : moderation.html (non indexée), où tu colles ta clé de modération une fois (gardée seulement dans ton navigateur).
"""
from __future__ import annotations

import json
import os
import re

from . import mon_espace, seo

_e = seo._e

SALONS = [("general", "Discussion générale", "Tout ce qui concerne la Bourse, la crypto et le site."),
          ("crypto", "Crypto", "Bitcoin, Ethereum, altcoins, memecoins : vos avis et vos questions."),
          ("actions", "Actions et ETF", "Actions françaises, américaines, ETF, PEA."),
          ("debutants", "Débutants : vos questions", "Aucune question n'est bête : on apprend ensemble.")]


def api() -> str:
    u = os.environ.get("RADAR_COMMU_API", "").strip().rstrip("/")
    return u if re.fullmatch(r"https://[a-z0-9.-]{3,120}(/[a-z0-9._-]{0,40})?", u, re.I) else ""


def google_id() -> str:
    """Version 121 : identifiant client Google (public, ce n'est pas un secret) pour « Continuer avec Google »."""
    from . import config
    g = (os.environ.get("RADAR_GOOGLE_ID", "") or getattr(config, "GOOGLE_CLIENT_ID", "")).strip()
    return g if re.fullmatch(r"[0-9]{5,20}-[a-z0-9]{10,40}\.apps\.googleusercontent\.com", g) else ""


def csp_google(c: str) -> str:
    if not c or not google_id():
        return c
    c = c.replace("script-src 'self' 'unsafe-inline'", "script-src 'self' 'unsafe-inline' https://accounts.google.com/gsi/client", 1)
    c = c.replace("style-src 'self' 'unsafe-inline'", "style-src 'self' 'unsafe-inline' https://accounts.google.com/gsi/style", 1)
    c = c.replace("connect-src 'self'", "connect-src 'self' https://accounts.google.com/gsi/", 1)
    return c.rstrip("; ") + "; frame-src https://accounts.google.com/gsi/"


def actif() -> bool:
    return bool(api())


def csp(c: str) -> str:
    a = api()
    if not c or not a or a in c:
        return c
    return c.replace("connect-src 'self'", f"connect-src 'self' {a}", 1)


JS = r"""/* Radar Bourse — communauté (version 119). Aucune donnée n'est envoyée tant qu'on n'utilise pas le compte ou les commentaires. */
(function(){
const API=document.documentElement.dataset.commu||(window.RBC_API||'');if(!API)return;
const K='rb-session',P='rb-pseudo';
const get=k=>{try{return localStorage.getItem(k)}catch(e){return null}},set=(k,v)=>{try{v==null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}};
async function appel(m,ch,corps,admin){const h={'Content-Type':'application/json'};const t=admin||get(K);if(t)h.Authorization='Bearer '+t;
  let r;try{r=await fetch(API+ch,{method:m,headers:h,body:corps?JSON.stringify(corps):undefined})}catch(e){return {ok:false,erreur:'Serveur injoignable : vérifie ta connexion et réessaie.'}}
  let j={};try{j=await r.json()}catch(e){}if(r.status===401&&!admin&&t&&ch!=='/connexion')set(K,null);return j.ok===undefined?{ok:false,erreur:'Erreur du serveur.'}:j}
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const quand=d=>{const s=(Date.now()-d)/1e3;return s<60?'à l’instant':s<3600?'il y a '+Math.floor(s/60)+' min':s<86400?'il y a '+Math.floor(s/3600)+' h':s<86400*30?'il y a '+Math.floor(s/86400)+' j':new Date(d).toLocaleDateString('fr-FR')};
const base=(document.querySelector('link[rel=canonical]')||{}).href?'':'';
const racine=document.documentElement.dataset.racine||'';
window.RBC={api:API,appel,connecte:()=>!!get(K),pseudo:()=>get(P),
  entrer:(j)=>{set(K,j.jeton);set(P,j.pseudo);document.dispatchEvent(new Event('rbc-change'))},
  sortir:()=>{appel('POST','/deconnexion');set(K,null);set(P,null);document.dispatchEvent(new Event('rbc-change'))}};
// ---------- commentaires : <section class="rbc-com" data-page="titres/aapl" data-titre="Apple">
function brancher(sec){const page=sec.dataset.page;if(!page)return;
  sec.innerHTML=`<h2>${esc(sec.dataset.titre||'Commentaires')}</h2><div class="rbc-form"></div><ol class="rbc-liste" aria-live="polite"><li class="muted">Chargement des commentaires…</li></ol>
   <p class="muted rbc-pied">Respect, pas de lien, pas de conseil d'achat présenté comme sûr : <a href="${racine}regles-communaute.html">règles de la communauté</a>. Les avis des membres ne sont pas ceux de Radar Bourse.</p>`;
  const form=sec.querySelector('.rbc-form'),liste=sec.querySelector('.rbc-liste');
  const formulaire=()=>{if(!RBC.connecte()){form.innerHTML=`<p class="rbc-invite"><a class="btn" href="${racine}compte.html?retour=${encodeURIComponent(location.pathname)}">Créer un compte ou se connecter pour commenter</a> <span class="muted">gratuit, sans e-mail</span></p>`;return}
    form.innerHTML=`<label class="sr" for="rbc-t-${page.replace(/\W/g,'')}">Ton commentaire</label><textarea id="rbc-t-${page.replace(/\W/g,'')}" maxlength="1000" rows="3" placeholder="Ton avis, ta question… (connecté en tant que ${esc(RBC.pseudo())})"></textarea>
     <div class="rbc-act"><button type="button" class="btn">Publier</button><span class="rbc-msg" role="status"></span></div>`;
    const ta=form.querySelector('textarea'),bt=form.querySelector('button'),msg=form.querySelector('.rbc-msg');
    bt.onclick=async()=>{const t=ta.value.trim();if(t.length<2){msg.textContent='Écris au moins quelques mots.';return}bt.disabled=true;msg.textContent='Publication…';
      const r=await appel('POST','/commentaires',{page,texte:t});bt.disabled=false;
      if(!r.ok){msg.textContent=r.erreur||'Impossible de publier.';formulaire.r&&0;return}
      ta.value='';msg.textContent='Publié ✓';try{goatcounter.count({path:'commentaire/publie',title:page,event:true})}catch(e){}charger()}};
  const rendu=L=>{if(!L.length){liste.innerHTML='<li class="muted rbc-vide">Pas encore de commentaire : lance la discussion !</li>';return}
    const moi=(RBC.pseudo()||'').toLowerCase();
    liste.innerHTML=L.slice().reverse().map(c=>`<li class="rbc-c" data-id="${esc(c.id)}"><div class="rbc-tete"><b>${esc(c.p)}</b> <span class="muted">${quand(c.d)}</span></div><p>${esc(c.t).replace(/\n/g,'<br>')}</p>
      <div class="rbc-outils">${c.p.toLowerCase()===moi?'<button type="button" data-a="suppr">Supprimer</button>':RBC.connecte()?'<button type="button" data-a="sig">Signaler</button>':''}</div></li>`).join('');
    liste.querySelectorAll('button[data-a]').forEach(b=>b.onclick=async()=>{const li=b.closest('li'),id=li.dataset.id;
      if(b.dataset.a==='suppr'){if(!confirmer(b))return;const r=await appel('DELETE','/commentaires',{page,id});if(r.ok)li.remove();else b.textContent=r.erreur||'Erreur'}
      else{const r=await appel('POST','/signaler',{page,id});b.textContent=r.ok?'Signalé, merci':(r.erreur||'Erreur');b.disabled=true;if(r.cache)li.remove()}})};
  const confirmer=b=>{if(b.dataset.ok)return true;b.dataset.ok=1;b.textContent='Confirmer la suppression ?';return false};
  async function charger(){const r=await appel('GET','/commentaires?page='+encodeURIComponent(page));if(!r.ok){liste.innerHTML='<li class="muted">Commentaires indisponibles pour le moment.</li>';return}
    rendu(r.commentaires||[]);const n=sec.dataset.compteur?document.getElementById(sec.dataset.compteur):null;if(n)n.textContent=(r.commentaires||[]).length}
  formulaire();charger();document.addEventListener('rbc-change',()=>{formulaire();charger()})}
const go=()=>{document.querySelectorAll('section.rbc-com').forEach(s=>{if('IntersectionObserver' in window){const io=new IntersectionObserver(e=>{if(e.some(x=>x.isIntersecting)){io.disconnect();brancher(s)}},{rootMargin:'600px'});io.observe(s)}else brancher(s)});
  document.querySelectorAll('[data-rbc-etat]').forEach(a=>{const m=()=>{a.textContent=RBC.connecte()?'👤 '+RBC.pseudo():'Se connecter'};m();document.addEventListener('rbc-change',m)})};
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',go):go();
})();
"""

CSS = """<style>
.rbc-com{margin:28px 0 8px;border-top:1px solid var(--line);padding-top:8px}
.rbc-com textarea{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);resize:vertical}
.rbc-act{display:flex;gap:10px;align-items:center;margin:8px 0}.rbc-msg{font-size:14px;color:var(--muted)}
.rbc-liste{list-style:none;padding:0;margin:12px 0}.rbc-c{border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:8px 0;background:var(--surface)}
.rbc-c p{margin:6px 0;white-space:normal;overflow-wrap:anywhere}.rbc-tete{font-size:14.5px}.rbc-outils button{background:none;border:0;color:var(--muted);font:inherit;font-size:13px;cursor:pointer;padding:2px 0}
.rbc-outils button:hover{color:var(--ink);text-decoration:underline}.rbc-pied{font-size:13px}.rbc-vide{padding:8px 0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.cpt-form{display:grid;gap:10px;max-width:420px}.cpt-form label{display:flex;flex-direction:column;gap:5px;font-size:14px}
.cpt-form input{font:inherit;font-size:16px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}
.cpt-onglets{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}.cpt-onglets button{border:1px solid var(--line);background:none;color:inherit;font:inherit;padding:8px 14px;border-radius:999px;cursor:pointer}
.cpt-onglets button[aria-selected=true]{background:var(--accent);border-color:var(--accent);color:#fff}
.cpt-code{font-family:var(--m,monospace);font-size:20px;letter-spacing:1px;padding:12px;border:2px dashed var(--accent);border-radius:10px;text-align:center;user-select:all}
.cpt-msg{min-height:1.3em}.cpt-ok{color:var(--up)}.cpt-ko{color:var(--down)}
</style>"""


def section(page: str, titre: str = "Commentaires", prefixe: str = "") -> str:
    """Bloc de commentaires (vide si la communauté n'est pas installée)."""
    if not actif():
        return ""
    return (f"<section class='rbc-com' data-page='{_e(page)}' data-titre='{_e(titre)}'><h2>{_e(titre)}</h2>"
            "<noscript><p>Les commentaires ont besoin de JavaScript.</p></noscript></section>")


def balises(prefixe: str = "") -> str:
    """À mettre dans les pages qui utilisent le compte : adresse du serveur + script (chargé en différé)."""
    if not actif():
        return ""
    return (CSS + f"<script>window.RBC_API={json.dumps(api())};document.documentElement.dataset.racine={json.dumps(prefixe)};</script>"
            f"<script src='{prefixe}communaute.js' defer></script>")


def _page_compte(base, csp_):
    cles = json.dumps(mon_espace.CLES)
    corps = (CSS + "<h1>Mon compte Radar Bourse</h1>"
             "<p>Un compte gratuit, <b>sans adresse e-mail</b> : un pseudo et un mot de passe suffisent. Il sert à commenter, à discuter "
             "avec les autres membres et à <b>retrouver ta progression sur tous tes appareils</b> (Académie, portefeuille virtuel, favoris, défis…).</p>"
             "<div id='cpt-dehors'>"
             + (f"<div class='carte' id='cpt-google' style='max-width:420px'><p style='margin:0 0 10px'><b>Le plus simple :</b></p><div id='g-bouton'></div>"
                "<div id='g-pseudo' hidden style='margin-top:12px'><label class='cpt-form' style='display:grid;gap:8px'><span>Choisis ton pseudo (il sera visible par les autres membres)</span>"
                "<input id='g-p' maxlength='20' autocomplete='nickname'></label><label style='display:flex;gap:8px;align-items:flex-start;margin:8px 0'><input type='checkbox' id='g-regles' style='margin-top:3px'> "
                "<span>J'accepte les <a href='regles-communaute.html' target='_blank'>règles de la communauté</a>.</span></label>"
                "<button class='btn' type='button' id='g-ok'>Terminer l'inscription</button></div><p class='cpt-msg' id='g-msg' role='status'></p>"
                "<p class='muted' style='font-size:13px;margin:8px 0 0'>Google confirme seulement que c'est toi : le site ne garde ni ton e-mail ni ton nom.</p></div>"
                "<p class='muted' style='margin:14px 0 4px'>Ou avec un pseudo et un mot de passe :</p>"
                f"<script src='https://accounts.google.com/gsi/client' async defer></script>" if google_id() else "")
             + "<div class='cpt-onglets' role='tablist'>"
             "<button type='button' role='tab' data-o='creer' aria-selected='true'>Créer un compte</button>"
             "<button type='button' role='tab' data-o='entrer' aria-selected='false'>Se connecter</button>"
             "<button type='button' role='tab' data-o='secours' aria-selected='false'>Mot de passe oublié</button></div>"
             "<form class='cpt-form carte' id='cpt-f' autocomplete='on'>"
             "<label>Pseudo <input name='pseudo' id='cpt-pseudo' autocomplete='username' required minlength='3' maxlength='20' pattern='[A-Za-z0-9_\\-]{3,20}'></label>"
             "<label id='cpt-l-code' hidden>Code de secours <input name='code' id='cpt-code' autocomplete='off' placeholder='XXXX-XXXX-XXXX-XXXX-XXXX'></label>"
             "<label id='cpt-l-mdp'><span id='cpt-mdp-lib'>Mot de passe (8 caractères au moins)</span> <input type='password' name='mdp' id='cpt-mdp' autocomplete='new-password' required minlength='8'></label>"
             "<label id='cpt-l-regles' style='flex-direction:row;align-items:flex-start;gap:8px'><input type='checkbox' id='cpt-regles' style='width:auto;margin-top:3px'> "
             "<span>J'accepte les <a href='regles-communaute.html' target='_blank'>règles de la communauté</a> (respect, pas de lien, pas d'arnaque).</span></label>"
             "<button type='submit' class='btn' id='cpt-go'>Créer mon compte</button><p class='cpt-msg' id='cpt-msg' role='status'></p></form>"
             "<p class='muted' style='font-size:14px'>Ton mot de passe n'est jamais enregistré tel quel (seulement une empreinte impossible à inverser). "
             "Choisis-en un que tu n'utilises nulle part ailleurs.</p></div>"
             "<div id='cpt-secours-box' hidden class='carte'><h2>⚠️ Garde ce code de secours</h2><p>C'est le seul moyen de changer ton mot de passe si tu "
             "l'oublies (le site ne connaît pas ton e-mail). Note-le ou fais une capture d'écran. Il ne sera plus jamais affiché.</p>"
             "<p class='cpt-code' id='cpt-secours'></p><button type='button' class='btn' id='cpt-secours-ok'>Je l'ai noté</button></div>"
             "<div id='cpt-dedans' hidden><div class='carte'><h2>Bonjour <span id='cpt-nom'></span> 👋</h2>"
             "<p>Tu peux commenter sur les fiches et dans les <a href='discussions.html'>discussions</a>.</p></div>"
             "<div class='carte'><h2>Ma progression sur tous mes appareils</h2><p>Sauvegarde ce que tu as fait sur cet appareil (Académie, portefeuille, "
             "favoris, défis, réglages), puis récupère-le sur ton téléphone ou ton ordinateur en te connectant.</p>"
             "<p style='display:flex;gap:8px;flex-wrap:wrap'><button type='button' class='btn' id='cpt-sauver'>Sauvegarder dans mon compte</button>"
             "<button type='button' class='btn ghost' id='cpt-recup'>Récupérer sur cet appareil</button></p><p class='cpt-msg' id='cpt-msg2' role='status'></p></div>"
             "<div class='carte'><h2>Mon compte</h2><p style='display:flex;gap:8px;flex-wrap:wrap'><button type='button' class='btn ghost' id='cpt-sortir'>Se déconnecter</button>"
             "<button type='button' class='btn ghost' id='cpt-suppr' style='border-color:var(--down)'>Supprimer mon compte</button></p>"
             "<p class='muted' style='font-size:14px'>La suppression efface ton compte, ta sauvegarde et tous tes commentaires, définitivement.</p></div></div>"
             "<script>(function(){const go=()=>{if(!window.RBC){document.getElementById('cpt-msg').textContent='Le compte est indisponible pour le moment.';return}"
             "const $=i=>document.getElementById(i),CLES=" + cles + ";let o='creer';"
             "const retour=new URLSearchParams(location.search).get('retour');"
             "const etat=()=>{const c=RBC.connecte();$('cpt-dehors').hidden=c;$('cpt-dedans').hidden=!c;if(c)$('cpt-nom').textContent=RBC.pseudo()};"
             "document.querySelectorAll('[data-o]').forEach(b=>b.onclick=()=>{o=b.dataset.o;document.querySelectorAll('[data-o]').forEach(x=>x.setAttribute('aria-selected',x===b));"
             "$('cpt-l-code').hidden=o!=='secours';$('cpt-l-regles').hidden=o!=='creer';$('cpt-mdp-lib').textContent=o==='entrer'?'Mot de passe':o==='secours'?'Nouveau mot de passe (8 caractères au moins)':'Mot de passe (8 caractères au moins)';"
             "$('cpt-mdp').autocomplete=o==='entrer'?'current-password':'new-password';$('cpt-go').textContent=o==='entrer'?'Se connecter':o==='secours'?'Changer mon mot de passe':'Créer mon compte';$('cpt-msg').textContent=''});"
             "$('cpt-f').onsubmit=async e=>{e.preventDefault();const m=$('cpt-msg');const pseudo=$('cpt-pseudo').value.trim(),mdp=$('cpt-mdp').value;m.className='cpt-msg';m.textContent='…';"
             "let r;if(o==='creer'){if(!$('cpt-regles').checked){m.textContent='Coche la case des règles de la communauté.';return}r=await RBC.appel('POST','/inscription',{pseudo,mdp,regles:true})}"
             "else if(o==='entrer')r=await RBC.appel('POST','/connexion',{pseudo,mdp});else r=await RBC.appel('POST','/secours',{pseudo,code:$('cpt-code').value,mdp});"
             "if(!r.ok){m.className='cpt-msg cpt-ko';m.textContent=r.erreur||'Erreur';return}RBC.entrer(r);try{goatcounter.count({path:'compte/'+o,event:true})}catch(e){}"
             "if(r.secours){$('cpt-secours').textContent=r.secours;$('cpt-secours-box').hidden=false;$('cpt-dehors').hidden=true}else{etat();if(retour&&retour.startsWith('/'))location.href=retour}};"
             "$('cpt-secours-ok').onclick=()=>{$('cpt-secours-box').hidden=true;etat();if(retour&&retour.startsWith('/'))location.href=retour};"
             "$('cpt-sortir').onclick=()=>{RBC.sortir();etat()};"
             "$('cpt-suppr').onclick=async e=>{const b=e.target;if(!b.dataset.ok){b.dataset.ok=1;b.textContent='Confirmer : tout supprimer définitivement';return}"
             "const r=await RBC.appel('DELETE','/compte',{});if(r.ok){RBC.sortir();etat();$('cpt-msg').textContent='Compte supprimé.'}else b.textContent=r.erreur||'Erreur'};"
             "$('cpt-sauver').onclick=async()=>{const d={};CLES.forEach(k=>{try{const v=localStorage.getItem(k);if(v!=null)d[k]=v}catch(e){}});"
             "const r=await RBC.appel('POST','/donnees',{donnees:d});$('cpt-msg2').textContent=r.ok?'Sauvegardé ✓ ('+Object.keys(d).length+' éléments)':(r.erreur||'Erreur')};"
             "$('cpt-recup').onclick=async()=>{const r=await RBC.appel('GET','/donnees');if(!r.ok){$('cpt-msg2').textContent=r.erreur||'Erreur';return}"
             "const d=r.donnees||{};let n=0;Object.entries(d).forEach(([k,v])=>{if(CLES.includes(k)&&typeof v==='string'){try{localStorage.setItem(k,v);n++}catch(e){}}});"
             "$('cpt-msg2').textContent=n?n+' éléments récupérés ✓ : recharge les pages pour les voir.':'Rien à récupérer : sauvegarde d’abord depuis ton autre appareil.'};"
             "document.addEventListener('rbc-change',etat);etat();"
             "const GID=" + json.dumps(google_id()) + ";let cred='';"
             "const gEnvoyer=async(extra)=>{const r=await RBC.appel('POST','/google',Object.assign({credential:cred},extra||{}));"
             "if(r.nouveau){$('g-pseudo').hidden=false;$('g-msg').textContent=r.erreur;$('g-p').focus();return}"
             "if(!r.ok){$('g-msg').className='cpt-msg cpt-ko';$('g-msg').textContent=r.erreur||'Erreur';return}"
             "RBC.entrer(r);try{goatcounter.count({path:'compte/google',event:true})}catch(e){}etat();if(retour&&retour.startsWith('/'))location.href=retour};"
             "if(GID&&$('g-bouton')){const init=()=>{if(!window.google||!google.accounts){return setTimeout(init,300)}"
             "google.accounts.id.initialize({client_id:GID,callback:x=>{cred=x.credential;gEnvoyer()},ux_mode:'popup',use_fedcm_for_prompt:true});"
             "google.accounts.id.renderButton($('g-bouton'),{theme:'outline',size:'large',text:'continue_with',locale:'fr',shape:'pill'})};init();"
             "$('g-ok').onclick=()=>{if(!$('g-regles').checked){$('g-msg').textContent='Coche la case des règles.';return}gEnvoyer({pseudo:$('g-p').value.trim(),regles:true})}}"
             "};"
             "document.readyState==='loading'?document.addEventListener('DOMContentLoaded',()=>setTimeout(go,0)):setTimeout(go,0)})();</script>")
    return "compte.html", seo._page(base, f"Mon compte : commenter et garder sa progression | {seo.NOM}",
                                    "Crée ton compte Radar Bourse gratuit, sans e-mail : commente, discute avec les autres membres et retrouve ta "
                                    "progression sur tous tes appareils.", "compte.html", balises("") + corps, csp=csp_google(csp(csp_)))


def _page_regles(base, csp_):
    corps = ("<h1>Les règles de la communauté</h1>"
             "<p>Radar Bourse est un endroit pour apprendre et échanger sur la Bourse et la crypto, entre débutants comme entre passionnés. "
             "Pour que ça reste agréable et sûr pour tout le monde :</p><ol>"
             "<li><b>Respect</b> : pas d'insulte, de moquerie, de harcèlement, de propos racistes, sexistes ou haineux.</li>"
             "<li><b>Pas de lien ni d'adresse</b> (sites, Telegram, comptes, e-mails) : c'est le premier outil des arnaques. Ils sont bloqués automatiquement.</li>"
             "<li><b>Pas d'arnaque ni de promesse</b> : « gain garanti », « je double ton argent », groupes de signaux payants, demandes d'argent ou de "
             "codes : supprimés, compte suspendu.</li>"
             "<li><b>Pas de conseil présenté comme sûr</b> : partage ton avis, mais personne ne sait ce que fera la Bourse. Un avis de membre n'est pas "
             "un conseil en investissement, et n'engage pas Radar Bourse.</li>"
             "<li><b>Pas de données personnelles</b> : ne publie ni ton adresse, ni ton téléphone, ni ceux des autres.</li></ol>"
             "<h2>Modération</h2><p>Chaque membre peut <b>signaler</b> un commentaire : après 3 signalements il est caché en attendant d'être relu. "
             "Les commentaires qui ne respectent pas les règles sont supprimés, et les comptes qui insistent sont suspendus. "
             "Tu peux supprimer tes propres commentaires à tout moment.</p>"
             "<h2>Ce qui est enregistré</h2><ul><li>Ton <b>pseudo</b> et une <b>empreinte</b> de ton mot de passe et de ton code de secours (impossible à "
             "inverser : personne ne peut lire ton mot de passe, pas même nous). Si tu passes par <b>« Continuer avec Google »</b>, Google confirme "
             "seulement que c'est toi : on ne garde ni ton e-mail ni ton nom, juste une empreinte non réversible de ton identifiant Google.</li><li>Tes <b>commentaires</b> (publics) et, si tu l'utilises, la "
             "<b>sauvegarde de ta progression</b>.</li><li><b>Aucune adresse e-mail</b>, aucun nom, aucune publicité, aucun traçage. Contre les abus, "
             "une empreinte de ton adresse IP (non réversible) est gardée 24 heures au plus.</li></ul>"
             "<p>Les données sont hébergées par Cloudflare. Tu peux <b>tout supprimer</b> toi-même depuis <a href='compte.html'>Mon compte</a> "
             "(compte, sauvegarde et commentaires). Une question ou un signalement urgent : <a href='contact.html'>contact</a>.</p>")
    return "regles-communaute.html", seo._page(base, f"Règles de la communauté et données enregistrées | {seo.NOM}",
                                               "Les règles des commentaires et discussions de Radar Bourse : respect, pas de lien, pas d'arnaque. "
                                               "Ce qui est enregistré (pas d'e-mail) et comment tout supprimer.", "regles-communaute.html", corps, csp=csp_)


def _page_discussions(base, csp_):
    onglets = "".join(f"<a href='#s-{k}'>{_e(t)}</a>" for k, t, _ in SALONS)
    salons = "".join(f"<div id='s-{k}'><p class='muted' style='margin:18px 0 -14px'>{_e(d)}</p>{section('salon/' + k, t)}</div>" for k, t, d in SALONS)
    corps = (CSS + "<h1>Les discussions de la communauté</h1>"
             "<p>Pose tes questions, partage tes analyses, discute des marchés avec les autres membres. Compte gratuit, sans e-mail. "
             "Chaque fiche d'action ou de crypto a aussi ses propres commentaires.</p>"
             f"<p class='pm-onglets' style='display:flex;gap:8px;flex-wrap:wrap'>{onglets}</p>{salons}")
    return "discussions.html", seo._page(base, f"Discussions bourse et crypto entre membres | {seo.NOM}",
                                         "Forum de discussion gratuit sur la Bourse et la crypto : questions de débutants, actions, ETF, bitcoin. "
                                         "Compte sans e-mail, modération et règles claires.", "discussions.html", balises("") + corps, csp=csp(csp_),
                                         mots="forum bourse, forum crypto, discussion bourse débutant, forum bitcoin français, questions bourse débutant")


def _page_moderation(base, csp_):
    corps = ("<h1>Modération</h1><p class='muted'>Page réservée à la modération (non indexée). Colle ta clé de modération : elle est gardée seulement "
             "dans ce navigateur.</p><p style='display:flex;gap:8px;flex-wrap:wrap'><input id='md-cle' type='password' autocomplete='off' placeholder='Clé de modération' "
             "style='flex:1 1 260px;padding:10px;border-radius:9px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit'>"
             "<button class='btn' id='md-ok' type='button'>Ouvrir</button><button class='btn ghost' id='md-oubli' type='button'>Oublier la clé</button></p>"
             "<p id='md-msg' role='status'></p><h2>Signalés</h2><div id='md-sig'></div><h2>Derniers commentaires</h2><div id='md-rec'></div>"
             "<script>(function(){const go=()=>{if(!window.RBC)return;const $=i=>document.getElementById(i),esc=s=>String(s??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]));"
             "let cle='';try{cle=localStorage.getItem('rb-modo')||''}catch(e){}"
             "const ligne=(x,sig)=>`<div class='carte' data-p='${esc(x[0])}' data-i='${esc(x[1])}' data-u='${esc(x[2])}'><b>${esc(x[2])}</b> · <a href='${x[0].startsWith('salon/')?'discussions.html':esc(x[0])+'.html'}'>${esc(x[0])}</a> · ${new Date(x[4]).toLocaleString('fr-FR')}<p>${esc(x[3])}</p>`"
             "+`<button class='btn ghost' data-a='suppr'>Supprimer</button> ${sig?\"<button class='btn ghost' data-a='retablir'>Rétablir (pas de problème)</button> \":''}<button class='btn ghost' data-a='bannir'>Suspendre ${esc(x[2])}</button></div>`;"
             "async function charger(){if(!cle)return;const r=await RBC.appel('GET','/admin/apercu',null,cle);if(!r.ok){$('md-msg').textContent=r.erreur||'Erreur';return}"
             "$('md-msg').textContent='Connecté à la modération ✓';$('md-sig').innerHTML=r.signales.map(x=>ligne(x,1)).join('')||'<p class=muted>Rien à traiter.</p>';"
             "$('md-rec').innerHTML=r.recents.map(x=>ligne(x,0)).join('')||'<p class=muted>Aucun commentaire.</p>';"
             "document.querySelectorAll('[data-a]').forEach(b=>b.onclick=async()=>{const d=b.closest('[data-i]'),page=d.dataset.p,id=d.dataset.i,a=b.dataset.a;let r;"
             "if(a==='suppr'){r=await RBC.appel('DELETE','/commentaires',{page,id},cle);await RBC.appel('POST','/admin/classer',{id},cle)}"
             "else if(a==='retablir')r=await RBC.appel('POST','/admin/retablir',{page,id},cle);else r=await RBC.appel('POST','/admin/bannir',{pseudo:d.dataset.u},cle);"
             "b.textContent=r.ok?'Fait ✓':(r.erreur||'Erreur');b.disabled=true})}"
             "$('md-ok').onclick=()=>{cle=$('md-cle').value.trim();try{localStorage.setItem('rb-modo',cle)}catch(e){}charger()};"
             "$('md-oubli').onclick=()=>{cle='';try{localStorage.removeItem('rb-modo')}catch(e){}$('md-msg').textContent='Clé oubliée.'};charger()};"
             "document.readyState==='loading'?document.addEventListener('DOMContentLoaded',()=>setTimeout(go,0)):setTimeout(go,0)})();</script>")
    page = seo._page(base, f"Modération | {seo.NOM}", "Page de modération.", "moderation.html", balises("") + corps, csp=csp(csp_))
    return "moderation.html", re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', page, 1)


def generer(base: str, dossier: str, csp_: str) -> list:
    if not actif():
        return []
    with open(os.path.join(dossier, "communaute.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    urls = []
    for fn, indexer in ((_page_compte, True), (_page_regles, True), (_page_discussions, True), (_page_moderation, False)):
        chemin, page = fn(base, csp_)
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        if indexer:
            urls.append((chemin, "weekly", "0.5"))
    return urls
