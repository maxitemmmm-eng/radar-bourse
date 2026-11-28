"""Version 93 : « Mon espace », l'équivalent d'un compte, sans inscription ni mot de passe.

Pourquoi pas un vrai compte en ligne : il faudrait un serveur qui garde des données personnelles (adresse e-mail, mot de
passe, portefeuille), avec les obligations qui vont avec (RGPD, sécurité, fuites possibles). Le site a fait le choix de
ne rien collecter. « Mon espace » donne presque tout ce qu'apporte un compte :
- un profil (pseudo, couleur, objectif), gardé dans ce navigateur ;
- un tableau de bord de tout ce que la personne a fait : portefeuille virtuel, favoris, scanners, pronostics, Académie,
  défis ;
- l'emporter sur un autre appareil : un fichier, ou un code de transfert à copier-coller (compressé), sans serveur ;
- tout effacer en un clic.
Rien n'est jamais envoyé sur Internet : tout se passe dans le navigateur.
"""
import os

CLES = ["radar-profil", "radar-bourse-portefeuille-v1", "radar-bourse-favoris", "radar-bourse-favoris-etat-v1", "radar-bourse-defis-v1",
        "radar-prono-v1", "radar-academie", "radar-scanner", "radar-bourse-arene-v1", "radar-theme", "radar-mode", "radar-acces",
        "radar-dossier", "radar-sections", "radar-bourse-avertissement-v2", "radar-depart-vu", "radar-dernier-espace",
        "rb-plus-code", "rb-analyses"]   # version 106 : le code Radar Bourse+ et les analyses suivent le transfert d'appareil

CSS = """<style>
.me-tete{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:8px 0 4px}
.me-av{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;font-size:26px;font-weight:700;color:#fff;flex:0 0 auto;
 background:var(--me-c,#3b6fd8);box-shadow:inset 0 0 0 3px rgba(255,255,255,.14)}
.me-tete>div:last-child{flex:1 1 280px;min-width:0}.me-tete h1{margin:0}.me-tete p{margin:2px 0 0}
.me-profil{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px 16px;align-items:end}
.me-profil label{display:flex;flex-direction:column;gap:5px;font-size:13.5px;color:var(--muted,#9aa6bd)}
.me-profil input,.me-profil select,.me-code{font:inherit;font-size:15px;color:inherit;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.35);border-radius:8px;padding:8px 10px;min-width:0}
.me-couleurs{display:flex;gap:8px;flex-wrap:wrap}.me-couleurs button{width:30px;height:30px;border-radius:50%;border:2px solid transparent;cursor:pointer;background:var(--c)}
.me-couleurs button[aria-pressed=true]{border-color:currentColor;outline:2px solid var(--c);outline-offset:2px}
.me-grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:12px 0}
.me-t{border:1px solid rgba(127,127,127,.28);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:4px;text-decoration:none;color:inherit}
.me-t small{color:var(--muted,#9aa6bd);font-size:13px}.me-t b{font-size:24px;font-variant-numeric:tabular-nums;line-height:1.2}.me-t span{font-size:14px}
a.me-t:hover{border-color:rgba(127,127,127,.6)}a.me-t:focus-visible,.me-couleurs button:focus-visible{outline:2px solid #86a8ff;outline-offset:2px}
.me-t ul{margin:6px 0 0;padding-left:18px;font-size:14px}.me-vide{color:var(--muted,#9aa6bd)}
.me-actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}.me-actions .btn{font-size:14px;font-weight:600;line-height:1.3;cursor:pointer}
.me-code{width:100%;min-height:84px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;word-break:break-all;resize:vertical;box-sizing:border-box}
#me-msg{min-height:1.3em;margin:6px 0 0}.me-ok{color:#44e09c}.me-ko{color:#ff7a7a}
.me-danger{border-color:rgba(255,95,95,.55)!important}
.up{color:#44e09c}.down{color:#ff7a7a}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
</style>"""

JS = r"""<script>(function(){
const CLES = __CLES__;
const $ = s => document.querySelector(s), esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const lire = (k, d) => { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch(e){ return d; } };
let dispo = true; try { localStorage.setItem("radar-test", "1"); localStorage.removeItem("radar-test"); } catch(e){ dispo = false; }
const msg = (t, ok) => { const m = $("#me-msg"); m.textContent = t; m.className = ok === false ? "me-ko" : ok ? "me-ok" : ""; };
if(!dispo){ $("#me-bloque").hidden = false; }
const COULEURS = ["#3b6fd8", "#1f9d6b", "#c2543a", "#8a4fd1", "#c28a12", "#2a8ea8"];
let P = Object.assign({pseudo: "", couleur: COULEURS[0], objectif: "", cree: new Date().toISOString()}, lire("radar-profil", {}) || {});
const sauverP = () => { try { localStorage.setItem("radar-profil", JSON.stringify(P)); return true; } catch(e){ return false; } };
function tete(){
  const n = (P.pseudo || "").trim();
  $("#me-av").textContent = n ? n[0].toUpperCase() : "?";
  $("#me-av").style.setProperty("--me-c", COULEURS.includes(P.couleur) ? P.couleur : COULEURS[0]);
  $("#me-nom").textContent = n ? `L'espace de ${n}` : "Mon espace";
}
$("#me-pseudo").value = P.pseudo || ""; $("#me-objectif").value = P.objectif || "";
$("#me-couleurs").innerHTML = COULEURS.map(c => `<button type="button" style="--c:${c}" data-c="${c}" aria-pressed="${c === P.couleur}" aria-label="Couleur ${COULEURS.indexOf(c) + 1}"></button>`).join("");
$("#me-couleurs").querySelectorAll("button").forEach(b => b.onclick = () => { P.couleur = b.dataset.c;
  $("#me-couleurs").querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b)); tete(); sauverP(); });
$("#me-form").addEventListener("submit", e => { e.preventDefault();
  P.pseudo = $("#me-pseudo").value.trim().slice(0, 24); P.objectif = $("#me-objectif").value; tete();
  msg(sauverP() ? "Profil enregistré sur cet appareil." : "Ton navigateur bloque l'enregistrement.", sauverP()); bilan(); });
tete();

const eur = v => v.toLocaleString("fr-FR", {maximumFractionDigits: 0}) + " €";
const jour = t => { const d = new Date(t); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
const slug = tk => tk.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
function bilan(){
  const T = [];
  const pf = lire("radar-bourse-portefeuille-v1", null);
  if(pf && typeof pf.cash === "number"){
    let v = pf.cash; const pos = Object.entries(pf.positions || {});
    pos.forEach(([, p]) => { v += (+p.qte || 0) * (+p.dernier || +p.prixMoyen || 0) * (+p.taux || 1); });
    const g = v / 10000 - 1;
    T.push(`<a class="me-t" href="index.html#portefeuille"><small>Portefeuille virtuel</small><b>${eur(v)}</b><span class="${g >= 0 ? "up" : "down"}">${g >= 0 ? "+" : ""}${(g * 100).toFixed(1).replace(".", ",")} % depuis le départ</span><span class="me-vide">${pos.length} position${pos.length > 1 ? "s" : ""} · valeur au dernier passage dans l'appli</span></a>`);
  } else T.push(`<a class="me-t" href="index.html#portefeuille"><small>Portefeuille virtuel</small><b>10 000 €</b><span class="me-vide">Pas encore commencé : achète et vends avec de l'argent fictif, sans risque.</span></a>`);
  const fav = lire("radar-bourse-favoris", []);
  const F = Array.isArray(fav) ? fav.filter(x => typeof x === "string").slice(0, 8) : [];
  T.push(`<div class="me-t"><small>Mes favoris</small><b>${Array.isArray(fav) ? fav.length : 0}</b>` + (F.length ? `<ul>${F.map(tk => `<li><a href="titres/${slug(tk)}.html">${esc(tk)}</a></li>`).join("")}</ul>` : `<span class="me-vide">Ouvre un titre et clique « ☆ Suivre » pour le retrouver ici.</span>`) + `</div>`);
  const sc = lire("radar-scanner", []);
  const S = Array.isArray(sc) ? sc.filter(x => x && x.nom && typeof x.c === "string").slice(0, 6) : [];
  T.push(`<div class="me-t"><small>Mes scanners</small><b>${S.length}</b>` + (S.length ? `<ul>${S.map(x => `<li><a href="index.html#scan=${encodeURIComponent(x.c)}">${esc(x.nom)}</a></li>`).join("")}</ul>` : `<span class="me-vide">Dans l'appli, « Tous les titres » → Scanner : garde tes critères préférés.</span>`) + `</div>`);
  const pr = lire("radar-prono-v1", {}) || {};
  T.push(`<a class="me-t" href="index.html#prono"><small>Pronostic du jour</small><b>${+pr.serie || 0} jour${(+pr.serie || 0) > 1 ? "s" : ""}</b><span>de série · meilleure : ${+pr.meilleure || 0}</span><span class="me-vide">${+pr.total ? `${+pr.justes || 0} justes sur ${+pr.total}` : "Pas encore joué"}</span></a>`);
  const a = lire("radar-academie", {}) || {};
  const faits = Object.values(a).filter(x => x && typeof x === "object" && x.fait).length;
  const jours = new Set(Array.isArray(a.jours) ? a.jours : []); let s = 0, t = Date.now(); if(!jours.has(jour(t))) t -= 864e5; while(jours.has(jour(t))){ s++; t -= 864e5; }
  const ex = a.examen || {};
  T.push(`<a class="me-t" href="formation.html"><small>Académie</small><b>${faits} chapitre${faits > 1 ? "s" : ""}</b><span>validé${faits > 1 ? "s" : ""} · série de ${s} jour${s > 1 ? "s" : ""}</span><span class="me-vide">${ex.reussi ? "Certificat obtenu ✓" : ex.meilleur ? `Examen : meilleur score ${+ex.meilleur} / 20` : "Examen final pas encore tenté"}</span></a>`);
  const df = lire("radar-bourse-defis-v1", []);
  const D = Array.isArray(df) ? df : [], fini = D.filter(x => x && x.fin).length;
  T.push(`<a class="me-t" href="index.html#simulation"><small>Mes paris contre l'IA</small><b>${D.length}</b><span>${fini} terminé${fini > 1 ? "s" : ""}, ${D.length - fini} en cours</span></a>`);
  $("#me-bilan").innerHTML = T.join("");
  const n = CLES.filter(k => { try { return localStorage.getItem(k) != null; } catch(e){ return false; } }).length;
  $("#me-n").textContent = n ? `${n} élément${n > 1 ? "s" : ""} enregistré${n > 1 ? "s" : ""} sur cet appareil.` : "Rien d'enregistré sur cet appareil pour l'instant.";
}
bilan();

function tout(){ const d = {}; CLES.forEach(k => { try { const v = localStorage.getItem(k); if(v != null) d[k] = v; } catch(e){} }); return {format: "radar-bourse-espace", version: 2, cree: new Date().toISOString(), donnees: d}; }
function valide(k, v){
  if(!CLES.includes(k) || typeof v !== "string" || v.length > 1e6) return false;
  if(["radar-theme", "radar-mode", "radar-acces", "radar-dernier-espace", "radar-bourse-avertissement-v2", "radar-depart-vu"].includes(k)) return v.length < 40;
  try { const x = JSON.parse(v);
    if(k === "radar-bourse-portefeuille-v1") return x && typeof x.cash === "number" && isFinite(x.cash) && x.cash >= 0 && typeof (x.positions || {}) === "object";
    if(["radar-bourse-favoris", "radar-scanner", "radar-bourse-defis-v1"].includes(k)) return Array.isArray(x);
    return x !== null && typeof x === "object";
  } catch(e){ return false; }
}
function restaurer(o){
  let d = null;
  if(o && o.format === "radar-bourse-espace" && o.donnees && typeof o.donnees === "object") d = o.donnees;
  else if(o && o.format === "radar-bourse-sauvegarde"){   // ancien fichier « Sauvegarder dans un fichier » de l'appli
    d = {}; if(o.portefeuille) d["radar-bourse-portefeuille-v1"] = JSON.stringify(o.portefeuille);
    if(Array.isArray(o.favoris)) d["radar-bourse-favoris"] = JSON.stringify(o.favoris);
    if(Array.isArray(o.defis)) d["radar-bourse-defis-v1"] = JSON.stringify(o.defis);
  }
  if(!d) throw new Error("format");
  const ok = Object.entries(d).filter(([k, v]) => valide(k, v));
  if(!ok.length) throw new Error("vide");
  ok.forEach(([k, v]) => localStorage.setItem(k, v));
  return ok.length;
}
$("#me-fichier").onclick = () => {
  const blob = new Blob([JSON.stringify(tout(), null, 1)], {type: "application/json"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `radar-bourse-mon-espace-${jour(Date.now())}.json`;
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  msg("Fichier créé. Ouvre « Mon espace » sur l'autre appareil et choisis « Restaurer un fichier ».", true); };
$("#me-import").onchange = e => { const f = e.target.files && e.target.files[0]; e.target.value = ""; if(!f) return;
  if(f.size > 3e6){ msg("Fichier trop gros : ce n'est pas une sauvegarde Radar Bourse.", false); return; }
  const r = new FileReader(); r.onload = () => { try { const n = restaurer(JSON.parse(r.result)); bilan(); P = Object.assign(P, lire("radar-profil", {}) || {}); tete();
      $("#me-pseudo").value = P.pseudo || ""; msg(`Restauré : ${n} élément${n > 1 ? "s" : ""}.`, true); } catch(err){ msg("Ce fichier n'est pas une sauvegarde Radar Bourse valide.", false); } };
  r.readAsText(f); };
const b64 = u => { let s = ""; u.forEach(x => s += String.fromCharCode(x)); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); };
const deb64 = s => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0));
async function flux(octets, sens){ const f = new Blob([octets]).stream().pipeThrough(sens === "c" ? new CompressionStream("deflate-raw") : new DecompressionStream("deflate-raw"));
  return new Uint8Array(await new Response(f).arrayBuffer()); }
$("#me-code-faire").onclick = async () => {
  const brut = new TextEncoder().encode(JSON.stringify(tout()));
  let code; try { code = "RB1-" + b64(await flux(brut, "c")); } catch(e){ code = "RB0-" + b64(brut); }
  $("#me-code").value = code; $("#me-code").select();
  try { await navigator.clipboard.writeText(code); msg(`Code copié (${code.length.toLocaleString("fr-FR")} caractères). Envoie-le-toi, puis colle-le ici sur l'autre appareil.`, true); }
  catch(e){ msg("Code prêt : sélectionne-le et copie-le.", true); } };
$("#me-code-lire").onclick = async () => {
  const c = $("#me-code").value.trim().replace(/\s+/g, "");
  try { let o;
    if(c.startsWith("RB1-")) o = JSON.parse(new TextDecoder().decode(await flux(deb64(c.slice(4)), "d")));
    else if(c.startsWith("RB0-")) o = JSON.parse(new TextDecoder().decode(deb64(c.slice(4))));
    else throw new Error("code");
    const n = restaurer(o); bilan(); P = Object.assign(P, lire("radar-profil", {}) || {}); tete(); $("#me-pseudo").value = P.pseudo || "";
    msg(`Code accepté : ${n} élément${n > 1 ? "s" : ""} restauré${n > 1 ? "s" : ""}.`, true);
  } catch(e){ msg("Ce code n'est pas valide (il doit commencer par RB1- et être complet).", false); } };
$("#me-effacer").onclick = () => {
  const z = $("#me-eff-zone");
  z.innerHTML = `Effacer profil, portefeuille, favoris, scanners, pronostics et progression de l'Académie sur cet appareil ? <button class="btn ghost me-danger" type="button" id="me-oui">Oui, tout effacer</button> <button class="btn ghost" type="button" id="me-non">Non</button>`;
  $("#me-non").onclick = () => location.reload();
  $("#me-oui").onclick = () => { CLES.forEach(k => { try { localStorage.removeItem(k); } catch(e){} }); location.reload(); }; };
})();</script>"""


def page(seo, base, dossier, csp) -> list:
    corps = (CSS +
             "<div class='me-tete'><div class='me-av' id='me-av' aria-hidden='true'>?</div><div><h1 id='me-nom'>Mon espace</h1>"
             "<p class='muted'>Ton compte Radar Bourse, sans inscription ni mot de passe : tout reste dans ce navigateur, rien n'est envoyé sur Internet.</p></div></div>"
             "<p id='me-bloque' class='carte' hidden>Ton navigateur bloque l'enregistrement (navigation privée ou stockage désactivé) : rien ne pourra être gardé ici.</p>"
             + ("<section class='carte'><h2 style='margin-top:0'>🔄 Sur tous tes appareils</h2><p>Avec un compte gratuit (sans e-mail), sauvegarde tout ce "
                "qu'il y a ici et retrouve-le sur ton téléphone ou ton ordinateur, et participe aux <a href='discussions.html'>discussions</a>.</p>"
                "<p><a class='btn' href='compte.html'>Mon compte</a></p></section>" if __import__("bourse_bot.communaute", fromlist=["x"]).actif() else "")
             + "<section class='carte'><h2 style='margin-top:0'>Mon profil</h2><form id='me-form' class='me-profil'>"
             "<label>Pseudo<input id='me-pseudo' maxlength='24' autocomplete='nickname' placeholder='ex. Max'></label>"
             "<label>Mon objectif<select id='me-objectif'><option value=''>Choisir…</option><option value='apprendre'>Apprendre la Bourse de zéro</option>"
             "<option value='suivre'>Suivre des actions et des cryptos</option><option value='entrainer'>M'entraîner sans risque</option>"
             "<option value='comprendre'>Comprendre ce que vaut l'IA</option></select></label>"
             "<div><span class='muted' style='font-size:13.5px'>Ma couleur</span><div class='me-couleurs' id='me-couleurs' role='group' aria-label='Couleur du profil'></div></div>"
             "<div><button class='btn' type='submit'>Enregistrer le profil</button></div></form></section>"
             + ("" if not __import__("bourse_bot.abonnement", fromlist=["x"]).actif() else
             "<section class='carte' id='me-statut'><h2 style='margin-top:0'>Mon statut</h2><p id='me-statut-t'>Compte <b>classique</b> (gratuit).</p>"
             "<ul class='liste' id='me-statut-l'><li>Radar, fiches, prévisions, outils : <b>illimités</b></li><li>Académie : <b>3 grandes leçons par jour</b></li>"
             "<li>Analyse approfondie : <b>1 offerte</b></li><li>Parcours Analyste : <b>aperçu</b></li></ul>"
             "<p class='me-actions'><a class='btn' id='me-plus-a' href='radar-bourse-plus.html'>Passer à Radar Bourse+ (1 mois offert)</a>"
             "<a class='btn ghost' href='analyse-approfondie.html'>Mes analyses approfondies</a></p></section>") +
             "<h2>Ce que j'ai fait</h2><p class='muted' id='me-n'></p><div class='me-grille' id='me-bilan' aria-live='polite'></div>"
             "<section class='carte'><h2 style='margin-top:0'>Changer d'appareil</h2>"
             "<p>Pour retrouver ton espace sur ton téléphone ou un autre ordinateur, emporte-le avec un fichier ou un code. "
             "Ça remplace l'adresse e-mail et le mot de passe d'un compte classique.</p>"
             "<div class='me-actions'><button class='btn' type='button' id='me-fichier'>Télécharger mon espace (fichier)</button>"
             "<label class='btn ghost'>Restaurer un fichier<input type='file' id='me-import' accept='.json,application/json' class='sr'></label></div>"
             "<div class='me-actions'><button class='btn ghost' type='button' id='me-code-faire'>Créer un code de transfert</button>"
             "<button class='btn ghost' type='button' id='me-code-lire'>Utiliser le code collé</button></div>"
             "<label for='me-code' class='muted' style='font-size:13.5px'>Code de transfert</label>"
             "<textarea id='me-code' class='me-code' spellcheck='false' placeholder='Colle ici un code qui commence par RB1-'></textarea>"
             "<p id='me-msg' role='status' aria-live='polite'></p>"
             "<p class='muted' style='font-size:13.5px'>Le code contient tes données en clair (compressées) : ne le publie pas. Le fichier de l'ancienne "
             "sauvegarde du portefeuille est aussi accepté.</p></section>"
             "<section><h2>Pourquoi pas un compte avec mot de passe ?</h2><p>Un compte en ligne obligerait à garder sur un serveur ton adresse e-mail, ton mot de passe "
             "et ce que tu fais sur le site. On a choisi de ne rien collecter : pas de fichier client, pas de fuite possible, pas de publicité. "
             "En échange, c'est à toi d'emporter ton espace quand tu changes d'appareil.</p>"
             "<p id='me-eff-zone'><button class='btn ghost me-danger' type='button' id='me-effacer'>Tout effacer de cet appareil</button></p></section>"
             + JS.replace("__CLES__", str(CLES).replace("'", '"'))
             + __import__("bourse_bot.abonnement", fromlist=["x"])._js()
             + """<script>(async function(){if(!RBP.code()||!document.getElementById('me-statut'))return;const v=await RBP.verifier();if(!v.ok)return;
const d=t=>t?new Date(t*1000).toLocaleDateString('fr-FR',{day:'numeric',month:'long'}):'';
document.getElementById('me-statut-t').innerHTML='Compte <b>Radar Bourse+</b> ✨'+(v.statut==='trialing'&&v.fin_essai?' : essai gratuit jusqu\u2019au '+d(v.fin_essai):'')+(v.annule?' (résilié, actif jusqu\u2019au '+d(v.fin_periode)+')':'')+'.';
document.getElementById('me-statut-l').innerHTML='<li>Radar, fiches, prévisions, outils : <b>illimités</b></li><li>Académie : <b>sans limite</b></li><li>Analyses approfondies : <b>illimitées</b> (10 par jour)</li><li>Parcours Analyste : <b>complet</b></li>';
const a=document.getElementById('me-plus-a');a.textContent='Gérer mon abonnement';})();</script>""")
    chemin = "mon-espace.html"
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Mon espace : profil, portefeuille, favoris, Académie | {seo.NOM}",
                          "Ton espace Radar Bourse sans inscription : profil, portefeuille virtuel, favoris, scanners, progression à l'Académie, "
                          "et transfert vers un autre appareil par fichier ou code. Rien n'est envoyé sur Internet.",
                          chemin, corps, csp=csp))
    return [(chemin, "monthly", "0.4")]
