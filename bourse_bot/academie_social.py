"""Version 120 : l'Académie qui fait revenir — rappel de série, classement de la semaine, parcours par objectif, cas réels.

- Rappel de série : « Ta série de 5 jours s'arrête ce soir » (Académie et accueil), tant que rien n'a été fait aujourd'hui.
- Classement de la semaine (avec un compte de la communauté) : les points gagnés depuis lundi, remis à zéro chaque semaine.
- Parcours par objectif (formation/objectifs.html) : 3 chemins de 15 à 40 minutes vers un vrai but, avec cases à cocher.
- Cas pratiques réels (formation/cas-reel-*.html) : lire une vraie fiche avec les chiffres du jour, questions corrigées.
"""
from __future__ import annotations

import json
import os

from . import seo as _seo

_e = _seo._e

# ---------------------------------------------------------------------------------------------- JS commun (toutes les pages)
JS_SERIE = r"""<script>
/* version 120 : rappel de série (sans serveur : lit la progression gardée dans ce navigateur) */
(function(){
  const P=document.documentElement.dataset.acaPrefixe||'';
  let d={};try{d=JSON.parse(localStorage.getItem('radar-academie')||'{}')||{}}catch(e){return}
  const jour=t=>{const x=t?new Date(t):new Date();return x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0')};
  const J=new Set(d.jours||[]);if(J.has(jour()))return;let n=0,t=Date.now()-864e5;while(J.has(jour(t))){n++;t-=864e5}
  if(n<1)return;try{if(sessionStorage.getItem('rb-serie-vu')===jour())return}catch(e){}
  const b=document.createElement('div');b.className='rb-serie';b.setAttribute('role','status');
  b.innerHTML=`<span aria-hidden="true">🔥</span><span>Ta série de <b>${n} jour${n>1?'s':''}</b> s’arrête ce soir à minuit : 2 minutes suffisent pour la garder.</span>`+
    `<a class="rb-serie-go" href="${P}formation/entrainement.html">Entraînement du jour</a><button type="button" aria-label="Fermer">✕</button>`;
  b.querySelector('button').onclick=()=>{b.remove();try{sessionStorage.setItem('rb-serie-vu',jour())}catch(e){}};
  const ac=document.querySelector('.a-col');if(ac)ac.prepend(b);else{b.classList.add('rb-serie-flottant');document.body.appendChild(b)}   // flottant : la page ne bouge pas
})();
</script><style>
.rb-serie{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0 14px;padding:10px 14px;border-radius:12px;
 border:1px solid color-mix(in srgb,#f5a524 55%,transparent);background:color-mix(in srgb,#f5a524 12%,transparent);font-size:15px}
.rb-serie>span:nth-child(2){flex:1 1 220px}.rb-serie-go{font-weight:700;white-space:nowrap}
.rb-serie button{background:none;border:0;color:inherit;opacity:.7;cursor:pointer;font-size:16px}
.rb-serie-flottant{position:fixed;left:12px;right:12px;bottom:16px;max-width:560px;margin:0 auto;z-index:80;background:var(--surface,#16213a);box-shadow:0 10px 30px rgba(0,0,0,.35)}
@media (max-width:760px){.rb-serie-flottant{bottom:78px}}
</style>"""

JS_CLASSEMENT = r"""<script>
/* version 120 : classement de la semaine (compte de la communauté). Les points sont ceux de cet appareil, envoyés au plus toutes les 5 min. */
(function(){
  const sem=()=>{const d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()+3-(d.getDay()+6)%7);const s1=new Date(d.getFullYear(),0,4);
    return d.getFullYear()+'-S'+String(1+Math.round(((d-s1)/864e5-3+(s1.getDay()+6)%7)/7)).padStart(2,'0')};
  const lundi=()=>{const d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()-(d.getDay()+6)%7);return d};
  const jour=x=>x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0');
  function xpSemaine(){let d={};try{d=JSON.parse(localStorage.getItem('radar-academie')||'{}')||{}}catch(e){}const X=d.xp_jours||{};let s=0;const l=lundi();
    for(let k=0;k<7;k++){const x=new Date(l);x.setDate(l.getDate()+k);s+=+X[jour(x)]||0}return Math.min(5000,Math.round(s))}
  async function envoyer(){if(!window.RBC||!RBC.connecte())return;const x=xpSemaine(),S=sem();let m={};try{m=JSON.parse(localStorage.getItem('rb-xp-envoi')||'{}')}catch(e){}
    if(m.s===S&&m.x===x)return;if(m.t&&Date.now()-m.t<300000&&m.s===S)return;const r=await RBC.appel('POST','/xp',{semaine:S,xp:x});
    if(r.ok&&!r.attente)try{localStorage.setItem('rb-xp-envoi',JSON.stringify({s:S,x,t:Date.now()}))}catch(e){}}
  async function afficher(){const z=document.getElementById('aca-classement');if(!z||!window.RBC)return;const P=document.documentElement.dataset.acaPrefixe||'';
    const r=await RBC.appel('GET','/classement?semaine='+sem()+'&moi='+encodeURIComponent(RBC.pseudo()||''));if(!r.ok){z.hidden=true;return}
    const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const top=(r.top||[]).slice(0,10);
    z.hidden=false;z.innerHTML=`<h2>🏆 Classement de la semaine</h2><p class="muted" style="margin-top:-4px">Les points gagnés depuis lundi dans l’Académie. Remis à zéro chaque lundi.</p>`+
      (top.length?`<ol class="rb-cl">${top.map((x,i)=>`<li${(RBC.pseudo()||'').toLowerCase()===x.p.toLowerCase()?' class="moi"':''}><span class="r">${i<3?['🥇','🥈','🥉'][i]:i+1}</span><b>${esc(x.p)}</b><span class="x">${x.x} pts</span></li>`).join('')}</ol>`:'<p>Personne encore cette semaine : sois le premier !</p>')+
      (RBC.connecte()?(r.rang?`<p>Toi : <b>${r.rang}<sup>e</sup></b> sur ${r.total} avec ${r.moi_xp} points.</p>`:`<p>Gagne des points cette semaine (leçons, entraînement du jour) pour entrer dans le classement.</p>`)
        :`<p><a class="a-btn" href="${P}compte.html?retour=${encodeURIComponent(location.pathname)}">Crée ton compte (sans e-mail) pour entrer dans le classement</a></p>`)}
  const go=async()=>{try{await envoyer()}catch(e){}afficher();document.addEventListener('rbc-change',()=>{envoyer().then(afficher)})};
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',()=>setTimeout(go,0)):setTimeout(go,0);
  window.addEventListener('pagehide',()=>{try{envoyer()}catch(e){}});
})();
</script><style>
.rb-cl{list-style:none;padding:0;margin:8px 0}.rb-cl li{display:flex;gap:10px;align-items:center;padding:7px 10px;border-radius:10px}
.rb-cl li:nth-child(odd){background:rgba(127,127,127,.08)}.rb-cl li.moi{outline:2px solid var(--a-prim,#7398ff)}
.rb-cl .r{width:2em;text-align:center;font-variant-numeric:tabular-nums}.rb-cl b{flex:1}.rb-cl .x{font-variant-numeric:tabular-nums;opacity:.85}
</style>"""


def scripts(prefixe: str) -> str:
    """À la fin de chaque page de l'Académie : rappel de série (+ classement et compte si la communauté est installée)."""
    from . import communaute
    s = f"<script>document.documentElement.dataset.acaPrefixe={json.dumps(prefixe)};</script>" + JS_SERIE
    if communaute.actif():
        s += communaute.balises(prefixe) + JS_CLASSEMENT
    return s


def bloc_classement() -> str:
    from . import communaute
    if not communaute.actif():
        return ""
    return "<section class='a-carte' id='aca-classement' hidden style='margin:18px 0'></section>"


# ---------------------------------------------------------------------------------------------- parcours par objectif
OBJECTIFS = [
    ("pea", "Ouvrir mon premier PEA", "40 min", "Comprendre le PEA, choisir où l'ouvrir, savoir ce qu'on paiera en frais et en impôts, puis faire un premier achat sans stress.",
     [("ch", "pea-cto-assurance-vie", "PEA, compte-titres, assurance-vie : où investir ?"),
      ("guide", "guides/pea-ou-compte-titres.html", "Guide : PEA ou compte-titres ?"),
      ("ch", "choisir-son-courtier", "Choisir son courtier et comprendre les frais"),
      ("guide", "guides/ouvrir-compte-bourse.html", "Guide : ouvrir son compte, étape par étape"),
      ("ch", "passer-un-ordre", "Passer un ordre : au marché, à cours limité, stop"),
      ("ch", "fiscalite-2026", "La fiscalité de la Bourse en 2026"),
      ("outil", "simulateur-boursier.html", "S'entraîner avec 10 000 € virtuels avant le vrai premier achat")]),
    ("etf", "Acheter mon premier ETF", "35 min", "La façon la plus simple d'investir sur le long terme : comprendre un ETF, choisir un indice, investir chaque mois.",
     [("ch", "action-obligation-etf-crypto", "Action, obligation, ETF, crypto : les différences"),
      ("ch", "indices-cac40-sp500", "Les indices : CAC 40, S&P 500, MSCI World"),
      ("ch", "etf-debutant", "Les ETF : la façon la plus simple d'investir"),
      ("guide", "guides/etf-msci-world.html", "Guide : l'ETF MSCI World"),
      ("ch", "investir-regulierement", "Investir régulièrement et garder une épargne de précaution"),
      ("ch", "interets-composes", "Les intérêts composés : le temps travaille pour toi"),
      ("outil", "outils/interets-composes.html", "Calculer ce que donnent 100 € par mois")]),
    ("crypto", "Acheter du bitcoin sans me faire arnaquer", "45 min", "Comprendre ce qu'on achète, où l'acheter, comment le garder en sécurité, déjouer les arnaques et bien le déclarer.",
     [("ch", "blockchain-bitcoin", "Blockchain et bitcoin : comment ça marche"),
      ("ch", "acheter-conserver-crypto", "Acheter et conserver des cryptos en sécurité"),
      ("guide", "guides/wallet-crypto.html", "Guide : choisir un portefeuille (wallet)"),
      ("ch", "arnaques-et-pieges", "Arnaques et pièges : se protéger"),
      ("guide", "guides/arnaques-crypto.html", "Guide : les arnaques crypto les plus courantes"),
      ("ch", "cas-ftx-2022", "Étude de cas : la chute de FTX en 2022"),
      ("ch", "fiscalite-crypto-2026", "Crypto : fiscalité et déclaration en 2026")]),
]

JS_OBJECTIFS = r"""<script>
(function(){
  let a={};try{a=JSON.parse(localStorage.getItem('radar-academie')||'{}')||{}}catch(e){}
  let o={};try{o=JSON.parse(localStorage.getItem('rb-objectifs')||'{}')||{}}catch(e){}
  const sauver=()=>{try{localStorage.setItem('rb-objectifs',JSON.stringify(o))}catch(e){}};
  const maj=()=>document.querySelectorAll('.ob-parcours').forEach(p=>{const c=[...p.querySelectorAll('input[type=checkbox]')];const f=c.filter(x=>x.checked).length;
    p.querySelector('.ob-barre i').style.width=(f/c.length*100)+'%';p.querySelector('.ob-n').textContent=f+' / '+c.length+(f===c.length?' · objectif atteint 🎉':'')});
  document.querySelectorAll('.ob-parcours input[type=checkbox]').forEach(c=>{const k=c.dataset.k,ch=c.dataset.ch;
    c.checked=!!o[k]||!!(ch&&a[ch]&&(a[ch].fait||a[ch].valide));if(ch&&a[ch]&&(a[ch].fait||a[ch].valide))c.title='Chapitre validé dans l’Académie';
    c.addEventListener('change',()=>{o[k]=c.checked;sauver();maj();try{if(c.checked)goatcounter.count({path:'objectif/'+k,event:true})}catch(e){}})});
  maj();
})();
</script>"""

CSS_OBJ = """<style>
.ob-parcours{border:1px solid var(--a-ligne,rgba(127,127,127,.3));border-radius:16px;padding:16px 18px;margin:14px 0}
.ob-parcours h2{margin:0 0 4px}.ob-meta{display:flex;gap:12px;flex-wrap:wrap;align-items:center;color:var(--a-muted,#9aa6bd);font-size:14px}
.ob-barre{height:8px;border-radius:99px;background:rgba(127,127,127,.2);overflow:hidden;margin:10px 0}.ob-barre i{display:block;height:100%;width:0;background:linear-gradient(90deg,#7398ff,#35c27d);transition:width .4s}
.ob-etapes{list-style:none;padding:0;margin:8px 0;counter-reset:e}.ob-etapes li{display:flex;gap:10px;align-items:center;padding:8px 0;border-top:1px solid rgba(127,127,127,.15)}
.ob-etapes input{width:20px;height:20px;flex:none}.ob-etapes .t{font-size:12px;border-radius:99px;padding:2px 8px;background:rgba(127,127,127,.15);white-space:nowrap}
</style>"""


def page_objectifs(seo, base, csp):
    from . import academie
    blocs = []
    for k, titre, duree, desc, etapes in OBJECTIFS:
        lis = []
        for i, (typ, cible, lib) in enumerate(etapes):
            lien = f"{cible}.html" if typ == "ch" else f"../{cible}"
            tag = {"ch": "Chapitre", "guide": "Guide", "outil": "Outil"}[typ]
            lis.append(f"<li><input type='checkbox' data-k='{k}-{i}'{f' data-ch={_e(cible)}' if typ == 'ch' else ''} aria-label='Fait : {_e(lib)}'>"
                       f"<span class='t'>{tag}</span><a href='{_e(lien)}'>{_e(lib)}</a></li>")
        blocs.append(f"<section class='ob-parcours' id='{k}'><h2>{_e(titre)}</h2><div class='ob-meta'><span>⏱ {duree}</span><span class='ob-n'></span></div>"
                     f"<p>{_e(desc)}</p><div class='ob-barre'><i></i></div><ol class='ob-etapes'>{''.join(lis)}</ol></section>")
    corps = (CSS_OBJ + "<h1>Les parcours par objectif</h1><p>Tu sais ce que tu veux faire ? Suis le chemin le plus court pour y arriver, étape par étape. "
             "Les chapitres déjà validés dans l'Académie sont cochés tout seuls ; coche les autres au fur et à mesure.</p>"
             + "".join(blocs) + "<p class='muted' style='font-size:14px'>Parcours éducatifs : ils expliquent comment ça marche, ils ne disent pas quoi acheter.</p>" + JS_OBJECTIFS)
    chemin = "formation/objectifs.html"
    return chemin, academie.page(seo, base, f"Ouvrir un PEA, acheter un ETF ou du bitcoin : parcours pas à pas | {seo.NOM}",
                                 "Trois parcours gratuits pour débutants : ouvrir son premier PEA, acheter son premier ETF, acheter du bitcoin sans se faire "
                                 "arnaquer. Chapitres, guides et outils dans l'ordre, avec ta progression.", chemin, corps, None, csp=csp,
                                 mots="ouvrir un PEA débutant, acheter son premier ETF, acheter du bitcoin en sécurité, comment commencer en bourse, "
                                      "premier investissement étape par étape")


# ---------------------------------------------------------------------------------------------- cas pratiques réels
CAS = [("MC.PA", "LVMH", "une grande action française"), ("BTC-USD", "Bitcoin", "la première crypto"),
       ("CW8.PA", "l'ETF MSCI World", "un ETF qui suit 1 500 entreprises du monde entier")]


def _q(i, question, choix, bonne, expl):
    opts = "".join(f"<label class='cq-c'><input type='radio' name='cq{i}' value='{k}'> {_e(c)}</label>" for k, c in enumerate(choix))
    return (f"<div class='cq' data-b='{bonne}'><p><b>Question {i + 1}.</b> {_e(question)}</p>{opts}"
            f"<p class='cq-r' hidden></p><p class='cq-e' hidden>{_e(expl)}</p></div>")


JS_CAS = r"""<script>
document.querySelectorAll('.cq').forEach(q=>q.querySelectorAll('input').forEach(i=>i.addEventListener('change',()=>{const ok=i.value===q.dataset.b;
  const r=q.querySelector('.cq-r');r.hidden=false;r.textContent=ok?'✓ Bonne réponse':'✗ Pas tout à fait';r.className='cq-r '+(ok?'ok':'ko');q.querySelector('.cq-e').hidden=false;
  q.querySelectorAll('input').forEach(x=>x.disabled=true);try{goatcounter.count({path:'cas-reel/reponse',title:ok?'ok':'ko',event:true})}catch(e){}})));
</script><style>.cq{border:1px solid rgba(127,127,127,.3);border-radius:12px;padding:12px 14px;margin:10px 0}.cq-c{display:block;padding:6px 0;cursor:pointer}
.cq-r.ok{color:#35c27d;font-weight:700}.cq-r.ko{color:#ff7a7a;font-weight:700}.cq-e{opacity:.9}
.cas-k{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:10px 0}.cas-k div{border:1px solid rgba(127,127,127,.3);border-radius:10px;padding:8px 10px}
.cas-k b{display:block;font-size:18px}.cas-k span{font-size:13px;opacity:.8}</style>"""


def _page_cas(seo, base, csp, t, nom, quoi, date):
    from . import academie
    from .hebdo import avis_ia
    px, pct = seo._px, seo._pct
    dev, prix = t.get("devise", ""), t.get("prix")
    perf = t.get("perf") or {}
    m1, m6 = perf.get("1 mois"), perf.get("6 mois")
    au200 = t.get("au_dessus_200")
    mv = (t.get("risque_prevu") or {}).get("mouvement")
    f = t.get("fourchette") or []
    p, sens, conf = avis_ia(t)
    slug = seo.slug(t["ticker"])
    k = [(px(prix, dev), "dernier cours"), (pct(m1), "sur 1 mois"), (pct(m6), "sur 6 mois"),
         ("au-dessus" if au200 else "en dessous" if au200 is not None else "–", "de la moyenne 200 jours"),
         (f"±{round(mv * 100)} %" if isinstance(mv, (int, float)) else "–", "agitation prévue en un mois")]
    if len(f) == 2:
        k.append((f"{px(f[0], dev)} – {px(f[1], dev)}", "fourchette probable à un mois"))
    if p is not None:
        k.append((f"{'↑' if sens > 0 else '↓'} {round((p if sens > 0 else 1 - p) * 100)}/100", f"avis de l'IA (confiance {conf})"))
    qs = []
    if au200 is not None:
        qs.append(("Sa tendance de fond est-elle plutôt haussière ou baissière aujourd'hui ?", ["Haussière", "Baissière"], 0 if au200 else 1,
                   f"Le cours est {'au-dessus' if au200 else 'en dessous'} de sa moyenne des 200 dernières séances : c'est le repère le plus simple de la tendance de fond."))
    if isinstance(mv, (int, float)) and prix:
        bas = prix * (1 - mv)
        qs.append((f"Avec une agitation prévue de ±{round(mv * 100)} % en un mois, jusqu'où le cours peut-il baisser « normalement » ?",
                   [f"Vers {px(bas, dev)}", f"Vers {px(prix * (1 - mv * 3), dev)}", "Il ne peut pas baisser"], 0,
                   f"±{round(mv * 100)} % autour de {px(prix, dev)}, c'est environ {px(bas, dev)} en bas. Une baisse bien plus forte reste possible, mais rare."))
    if len(f) == 2:
        qs.append(("La fourchette « 8 fois sur 10 » veut dire…", ["Que le cours finira dedans 8 fois sur 10 environ, pas toujours",
                                                                   "Que le cours ne peut pas en sortir", "Que l'IA est sûre à 80 % de la hausse"], 0,
                   f"Entre {px(f[0], dev)} et {px(f[1], dev)} : c'est un ordre de grandeur. 2 fois sur 10, le cours finit en dehors, parfois loin."))
    if p is not None:
        qs.append((f"L'IA donne {round((p if sens > 0 else 1 - p) * 100)} chances sur 100 de {'hausse' if sens > 0 else 'baisse'}. Qu'en conclure ?",
                   ["C'est une légère inclinaison, pas une certitude", "Il faut acheter (ou vendre) tout de suite", "L'IA a toujours raison"], 0,
                   "Sur le sens du prix à un mois, l'IA fait à peine mieux qu'une réponse naïve : le site le montre dans ses résultats vérifiés. "
                   "Le plus utile, ce sont la fourchette et le risque, pas le sens."))
    if m1 is not None and m6 is not None:
        qs.append(("Sur 1 mois et sur 6 mois, le mouvement va-t-il dans le même sens ?", ["Oui", "Non"], 0 if (m1 >= 0) == (m6 >= 0) else 1,
                   f"{pct(m1)} sur 1 mois et {pct(m6)} sur 6 mois. Quand les deux divergent, le court terme contredit la tendance plus longue : prudence avant de conclure."))
    corps = (f"<p class='aca-fil'><a href='../formation.html'>Académie</a> › Cas pratiques réels</p>"
             f"<h1>Cas pratique réel : lire {_e(nom)} comme un pro</h1>"
             f"<p>{_e(nom[:1].upper() + nom[1:])}, c'est {_e(quoi)}. Voici ses <b>vrais chiffres du jour</b> (cours au {_e(date)}), tels qu'ils "
             "apparaissent sur sa fiche. Lis-les, puis réponds aux questions : la correction s'affiche tout de suite. Les chiffres changent chaque jour : "
             "reviens demain, le cas sera différent.</p>"
             "<div class='cas-k'>" + "".join(f"<div><b>{v}</b><span>{_e(l)}</span></div>" for v, l in k) + "</div>"
             + "".join(_q(i, *q) for i, q in enumerate(qs))
             + f"<h2>À toi de jouer</h2><p>Ouvre la <a href='../titres/{slug}.html'>fiche complète</a> ou lance une "
               f"<a href='../analyse-approfondie.html?t={_e(t['ticker'])}'>analyse approfondie</a> et retrouve ces chiffres toi-même. "
               "Puis fais la même lecture sur une autre action de ton choix.</p>"
               "<p class='muted' style='font-size:14px'>Cas éducatif : ce n'est pas un conseil d'achat ou de vente.</p>" + JS_CAS)
    chemin = f"formation/cas-reel-{slug}.html"
    return chemin, academie.page(seo, base, f"Cas pratique réel : analyser {nom} avec les chiffres du jour | {seo.NOM}",
                                 f"Exercice gratuit : lis les vrais chiffres du jour de {nom} (tendance, agitation, fourchette, avis de l'IA) et réponds "
                                 "aux questions corrigées. Change chaque jour.", chemin, corps, None, csp=csp,
                                 mots=f"exercice bourse corrigé, analyser {nom}, cas pratique bourse, apprendre à lire un graphique, exercice analyse action")


def cas_disponibles(payload) -> list:
    par = {t["ticker"]: t for t in payload.get("titres", []) if t.get("prix")}
    out = []
    for tk, nom, quoi in CAS:
        if tk in par:
            out.append((par[tk], nom, quoi))
    return out


def generer(seo, base, payload, dossier, csp) -> list:
    os.makedirs(os.path.join(dossier, "formation"), exist_ok=True)
    urls = []
    chemin, page = page_objectifs(seo, base, csp)
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(page)
    urls.append((chemin, "weekly", "0.7"))
    date = payload.get("date_donnees", "")[:10]
    try:
        from datetime import date as _d
        date = _seo.date_longue(date) if date else ""
    except Exception:
        pass
    for t, nom, quoi in cas_disponibles(payload):
        try:
            chemin, page = _page_cas(seo, base, csp, t, nom, quoi, date)
        except Exception as e:
            print(f"Cas réel {t.get('ticker')} non généré : {e}")
            continue
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "daily", "0.6"))
    return urls


def bloc_hub(payload=None) -> str:
    """Cartes « par objectif », « cas réels » et classement, sur l'accueil de l'Académie."""
    cas = "".join(f"<li><a href='formation/cas-reel-{_seo.slug(tk)}.html'>{_e(nom)}</a></li>" for tk, nom, _ in CAS
                  if not payload or any(t.get("ticker") == tk for t in payload.get("titres", [])))
    return ("<section style='max-width:900px;margin:24px auto;padding:0 16px'>" + bloc_classement() +
            "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px'>"
            "<div class='carte' style='border:1px solid var(--line);border-radius:14px;padding:16px 18px'><h2 style='margin-top:0'>🎯 Par objectif</h2>"
            "<p>Le chemin le plus court vers un vrai but : <a href='formation/objectifs.html#pea'>ouvrir mon premier PEA</a>, "
            "<a href='formation/objectifs.html#etf'>acheter mon premier ETF</a>, <a href='formation/objectifs.html#crypto'>acheter du bitcoin sans me faire arnaquer</a>.</p></div>"
            "<div class='carte' style='border:1px solid var(--line);border-radius:14px;padding:16px 18px'><h2 style='margin-top:0'>📊 Cas pratiques réels</h2>"
            f"<p>Lire une vraie fiche avec les chiffres du jour, questions corrigées (ça change chaque jour) :</p><ul style='margin:0'>{cas}</ul></div></div></section>")
