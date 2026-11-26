"""Version 104 : Radar Bourse+ — abonnement à 2 € par mois, premier mois gratuit (Stripe + un petit serveur Cloudflare).

Principes de sécurité :
- le paiement se fait UNIQUEMENT sur la page de Stripe : le site ne voit jamais de numéro de carte ;
- l'argent va de Stripe vers le compte bancaire de la vendeuse (réglé par elle dans Stripe, jamais dans ce code) ;
- la clé secrète Stripe vit seulement dans le serveur Cloudflare (« secret »), jamais dans le site ni dans GitHub ;
- l'accès est un code « RBP-… » signé (HMAC) par le serveur : impossible à fabriquer sans le secret ; à chaque usage le
  serveur revérifie chez Stripe que l'abonnement est actif ou en période d'essai ;
- le contenu réservé n'est jamais écrit dans les pages du site : il est servi par le serveur après vérification ;
- tant que l'identité de la vendeuse (mentions légales obligatoires) et l'adresse du serveur ne sont pas réglées, le bouton
  « S'abonner » ne s'affiche pas (rien ne peut être vendu par erreur).
"""
from __future__ import annotations

import json
import os

from . import config, seo
from .abonnement_contenu import LECONS_PLUS

NOM = seo.NOM
_e = seo._e
PRIX = "2 €"
ESSAI_JOURS = 30
LIMITE_GRATUITE = 3   # grandes leçons de l'Académie par jour sans abonnement


def reglages() -> dict:
    g = lambda k: os.environ.get(k, "").strip()
    return {"api": g("RADAR_PLUS_API").rstrip("/"), "nom": g("VENDEUR_NOM"), "siret": g("VENDEUR_SIRET"),
            "adresse": g("VENDEUR_ADRESSE"), "email": g("VENDEUR_EMAIL")}


VENTE = os.environ.get("RADAR_VENTE", "0") == "1"   # version 107 : la vente est mise de côté (pas de SIRET) ; tout est gratuit


def analyse_ouverte() -> bool:
    # version 110 : toujours ouverte — sans serveur, elle tourne dans le navigateur du visiteur (titres suivis)
    return True


def actif() -> bool:
    """Vrai seulement si la vente est rallumée (RADAR_VENTE=1) ET que TOUT est réglé : serveur + identité légale."""
    r = reglages()
    return VENTE and all(r[k] for k in ("api", "nom", "siret", "adresse", "email"))


# --------------------------------------------------------------------------------------------------------------------
# Le serveur (Cloudflare Worker) : fichier à copier-coller une fois dans Cloudflare (voir TUTO_ABONNEMENT.md)
# --------------------------------------------------------------------------------------------------------------------
WORKER = r"""// Radar Bourse+ : serveur d'abonnement (Cloudflare Worker). Généré par bourse_bot/abonnement.py — ne pas modifier à la main.
// Réglages dans Cloudflare (Settings > Variables and Secrets) :
//   STRIPE_SECRET (Secret) : clé secrète Stripe (sk_test_… pour tester, sk_live_… ensuite)
//   CODE_SECRET   (Secret) : une longue phrase au hasard (sert à signer les codes d'accès)
//   STRIPE_PRICE  (Text)   : identifiant du prix à 2 €/mois (price_…)
//   SITE          (Text)   : https://radarbourse.fr
//   Analyse approfondie (facultatif) : QUOTAS (liaison KV), GITHUB_REPO (Text, ex. pseudo/radar-bourse),
//   GITHUB_TOKEN (Secret : jeton GitHub limité à ce dépôt, droit « Actions : lecture et écriture »), DEPOT_SECRET (Secret)
const LECONS = __LECONS__;
const ESSAI = __ESSAI__;
const OK_STATUTS = ["trialing", "active", "past_due"];

function cors(env){ return {"Access-Control-Allow-Origin": env.SITE, "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin", "Cache-Control": "no-store"}; }
function rep(env, obj, statut = 200){ return new Response(JSON.stringify(obj), {status: statut, headers: {"Content-Type": "application/json; charset=utf-8", ...cors(env)}}); }

async function stripe(env, chemin, params = null, methode = "GET"){
  let url = "https://api.stripe.com/v1/" + chemin, corps = null;
  if(params){ const p = new URLSearchParams(params); if(methode === "GET") url += (url.includes("?") ? "&" : "?") + p; else corps = p; }
  const r = await fetch(url, {method: methode, body: corps, headers: {"Authorization": "Bearer " + env.STRIPE_SECRET, "Content-Type": "application/x-www-form-urlencoded"}});
  const j = await r.json(); if(!r.ok) throw new Error((j.error && j.error.message) || "Stripe"); return j;
}
async function signer(env, texte){
  const cle = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.CODE_SECRET), {name: "HMAC", hash: "SHA-256"}, false, ["sign"]);
  const s = new Uint8Array(await crypto.subtle.sign("HMAC", cle, new TextEncoder().encode(texte)));
  return [...s.slice(0, 9)].map(b => b.toString(16).padStart(2, "0")).join("");
}
function egal(a, b){ if(a.length !== b.length) return false; let d = 0; for(let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; }
async function codePour(env, sub){ return "RBP-" + sub + "-" + await signer(env, sub); }
async function lireCode(env, code){
  const m = /^RBP-(sub_[A-Za-z0-9]{8,64})-([0-9a-f]{18})$/.exec(String(code || "").trim());
  if(!m) return null;
  return egal(await signer(env, m[1]), m[2]) ? m[1] : null;
}
async function etat(env, sub){
  const cache = caches.default, cleCache = new Request("https://cache.radar-plus/" + sub);
  const c = await cache.match(cleCache); if(c) return c.json();
  const s = await stripe(env, "subscriptions/" + sub);
  const item = s.items && s.items.data && s.items.data[0];
  const e = {ok: OK_STATUTS.includes(s.status), statut: s.status, client: s.customer, fin_essai: s.trial_end || null,
             fin_periode: s.current_period_end || (item && item.current_period_end) || null, annule: !!s.cancel_at_period_end};
  await cache.put(cleCache, new Response(JSON.stringify(e), {headers: {"Cache-Control": "max-age=600"}}));
  return e;
}
async function verifie(env, code){ const sub = await lireCode(env, code); if(!sub) return null; const e = await etat(env, sub); return e.ok ? {sub, ...e} : null; }

// ---------- Analyse approfondie à la demande : 1 fois pour un visiteur gratuit, sans limite (10 par jour) pour un abonné ----------
const MAX_VIP_JOUR = 10;
async function hache(txt){
  const h = new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(txt)));
  return [...h.slice(0, 12)].map(b => b.toString(16).padStart(2, "0")).join("");   // on ne garde jamais l'adresse IP en clair
}
// une analyse gratuite par appareil, et au plus 3 par connexion internet et par an (wifi d'école ou de famille partagé)
async function clesGratuit(req, appareil){
  return {app: "gapp:" + await hache("a|" + String(appareil || "?").slice(0, 64)), ip: "gip:" + await hache("i|" + (req.headers.get("CF-Connecting-IP") || "?"))};
}
async function gratuitUtilise(env, k){ return !!(await env.QUOTAS.get(k.app)) || +(await env.QUOTAS.get(k.ip) || 0) >= 3; }
// version 107 : MODE_GRATUIT=1 (pas de vente) : tout le monde a droit à quelques analyses par jour, sans compte
const GRATUIT_JOUR_APPAREIL = 3, GRATUIT_JOUR_IP = 10;
async function quotaGratuit(env, req, corps, compter){
  const jour = new Date().toISOString().slice(0, 10), k = await clesGratuit(req, corps.appareil);
  const ka = "j:" + jour + ":" + k.app, ki = "j:" + jour + ":" + k.ip;
  const na = +(await env.QUOTAS.get(ka) || 0), ni = +(await env.QUOTAS.get(ki) || 0);
  const restant = Math.max(0, Math.min(GRATUIT_JOUR_APPAREIL - na, GRATUIT_JOUR_IP - ni));
  if(!compter) return {ok: true, mode_gratuit: true, restant, active: !!env.GITHUB_TOKEN};
  if(restant <= 0) return {ok: false, erreur: "Tu as utilisé tes " + GRATUIT_JOUR_APPAREIL + " analyses du jour. Reviens demain !"};
  return {ok: true, vip: false, noter: async () => { await env.QUOTAS.put(ka, String(na + 1), {expirationTtl: 172800}); await env.QUOTAS.put(ki, String(ni + 1), {expirationTtl: 172800}); }};
}
async function quota(env, req, corps){
  if(!env.QUOTAS) return {ok: false, erreur: "analyse non activée"};
  if(env.MODE_GRATUIT === "1") return quotaGratuit(env, req, corps, true);
  const v = corps.code ? await verifie(env, corps.code) : null;
  const jour = new Date().toISOString().slice(0, 10);
  if(v){
    const cle = "vip:" + v.sub + ":" + jour, n = +(await env.QUOTAS.get(cle) || 0);
    if(n >= MAX_VIP_JOUR) return {ok: false, erreur: "Limite de " + MAX_VIP_JOUR + " analyses par jour atteinte, reviens demain."};
    return {ok: true, vip: true, noter: () => env.QUOTAS.put(cle, String(n + 1), {expirationTtl: 172800})};
  }
  const k = await clesGratuit(req, corps.appareil);
  if(await gratuitUtilise(env, k)) return {ok: false, gratuit_utilise: true, erreur: "Ton analyse gratuite a déjà été utilisée. Avec Radar Bourse+ (1 mois offert), elles sont illimitées."};
  return {ok: true, vip: false, noter: async () => { await env.QUOTAS.put(k.app, "1", {expirationTtl: 31536000});
    await env.QUOTAS.put(k.ip, String(+(await env.QUOTAS.get(k.ip) || 0) + 1), {expirationTtl: 31536000}); }};
}
async function lancer(env, ticker, id){
  const r = await fetch("https://api.github.com/repos/" + env.GITHUB_REPO + "/actions/workflows/analyse.yml/dispatches", {method: "POST",
    headers: {"Authorization": "Bearer " + env.GITHUB_TOKEN, "Accept": "application/vnd.github+json", "User-Agent": "radar-plus", "Content-Type": "application/json"},
    body: JSON.stringify({ref: "main", inputs: {ticker, id}})});
  if(r.status !== 204) throw new Error("dispatch " + r.status);
}

export default {
  async fetch(req, env){
    if(req.method === "OPTIONS") return new Response(null, {headers: cors(env)});
    const url = new URL(req.url), p = url.pathname;
    try{
      if(p === "/checkout" && req.method === "POST"){
        const s = await stripe(env, "checkout/sessions", {"mode": "subscription", "line_items[0][price]": env.STRIPE_PRICE, "line_items[0][quantity]": "1",
          "subscription_data[trial_period_days]": String(ESSAI), "locale": "fr", "billing_address_collection": "auto",
          "success_url": env.SITE + "/merci-plus.html?session_id={CHECKOUT_SESSION_ID}", "cancel_url": env.SITE + "/radar-bourse-plus.html"}, "POST");
        return rep(env, {url: s.url});
      }
      if(p === "/retour"){
        const id = url.searchParams.get("session_id") || "";
        if(!/^cs_[A-Za-z0-9_]{10,200}$/.test(id)) return rep(env, {ok: false, erreur: "lien invalide"}, 400);
        const s = await stripe(env, "checkout/sessions/" + id);
        if(s.status !== "complete" || !s.subscription) return rep(env, {ok: false, erreur: "paiement non terminé"}, 402);
        const sub = typeof s.subscription === "string" ? s.subscription : s.subscription.id;
        const e = await etat(env, sub);
        return rep(env, {ok: e.ok, code: e.ok ? await codePour(env, sub) : null, statut: e.statut, fin_essai: e.fin_essai});
      }
      if(p === "/depot" && req.method === "POST"){
        if(!env.DEPOT_SECRET || !egal(req.headers.get("Authorization") || "", "Bearer " + env.DEPOT_SECRET)) return rep(env, {ok: false}, 403);
        const d = await req.json(); if(!/^[a-z0-9]{12,40}$/.test(d.id || "")) return rep(env, {ok: false}, 400);
        const ancien = JSON.parse(await env.QUOTAS.get("job:" + d.id) || "null"); if(!ancien) return rep(env, {ok: false}, 404);
        await env.QUOTAS.put("job:" + d.id, JSON.stringify({...ancien, etat: "fini", resultat: d.resultat}), {expirationTtl: 2592000});
        return rep(env, {ok: true});
      }
      if(p === "/resultat"){
        const id = url.searchParams.get("id") || ""; if(!/^[a-z0-9]{12,40}$/.test(id)) return rep(env, {ok: false}, 400);
        const j = env.QUOTAS ? JSON.parse(await env.QUOTAS.get("job:" + id) || "null") : null;
        if(!j) return rep(env, {ok: false, erreur: "analyse inconnue ou expirée"}, 404);
        if(j.etat !== "fini" && Date.now() - j.debut > 20 * 60000) return rep(env, {ok: true, etat: "echec", erreur: "L'analyse n'a pas abouti. Réessaie un peu plus tard."});
        return rep(env, {ok: true, etat: j.etat, ticker: j.ticker, debut: j.debut, resultat: j.resultat || null});
      }
      const corps = req.method === "POST" ? await req.json().catch(() => ({})) : {};
      if(p === "/analyse" && req.method === "POST"){
        const ticker = String(corps.ticker || "").trim().toUpperCase();
        if(!/^[A-Z0-9.^=-]{1,20}$/.test(ticker)) return rep(env, {ok: false, erreur: "Symbole invalide."}, 400);
        if(!env.GITHUB_TOKEN || !env.GITHUB_REPO) return rep(env, {ok: false, erreur: "L'analyse approfondie n'est pas encore activée."}, 503);
        const q = await quota(env, req, corps); if(!q.ok) return rep(env, q, 429);
        const id = [...crypto.getRandomValues(new Uint8Array(12))].map(b => b.toString(16).padStart(2, "0")).join("");
        await env.QUOTAS.put("job:" + id, JSON.stringify({etat: "en_cours", ticker, debut: Date.now()}), {expirationTtl: 2592000});
        await lancer(env, ticker, id); await q.noter();
        return rep(env, {ok: true, id, vip: q.vip});
      }
      if(p === "/quota" && env.MODE_GRATUIT === "1" && env.QUOTAS) return rep(env, await quotaGratuit(env, req, corps, false));
      if(p === "/quota"){
        const v = corps.code ? await verifie(env, corps.code) : null;
        if(v) return rep(env, {ok: true, vip: true});
        const u = env.QUOTAS ? await gratuitUtilise(env, await clesGratuit(req, corps.appareil)) : true;
        return rep(env, {ok: true, vip: false, gratuit_restant: u ? 0 : 1, active: !!(env.QUOTAS && env.GITHUB_TOKEN)});
      }
      if(p === "/verifier"){
        const v = await verifie(env, corps.code);
        return rep(env, v ? {ok: true, statut: v.statut, fin_essai: v.fin_essai, fin_periode: v.fin_periode, annule: v.annule} : {ok: false});
      }
      if(p === "/lecon"){
        const v = await verifie(env, corps.code); if(!v) return rep(env, {ok: false}, 403);
        const l = LECONS[corps.id]; if(!l) return rep(env, {ok: false, erreur: "leçon inconnue"}, 404);
        return rep(env, {ok: true, html: l});
      }
      if(p === "/portail"){
        const sub = await lireCode(env, corps.code); if(!sub) return rep(env, {ok: false}, 403);
        const e = await etat(env, sub);
        const prm = {"customer": e.client, "return_url": env.SITE + "/radar-bourse-plus.html"}; if(env.PORTAIL_CONFIG) prm.configuration = env.PORTAIL_CONFIG;
        const s = await stripe(env, "billing_portal/sessions", prm, "POST");
        return rep(env, {ok: true, url: s.url});
      }
      return rep(env, {ok: false, erreur: "inconnu"}, 404);
    }catch(err){ return rep(env, {ok: false, erreur: "serveur"}, 500); }
  }
};
"""


def ecrire_worker(chemin: str) -> None:
    lecons = {l["id"]: l["contenu"].strip() for l in LECONS_PLUS}
    code = (WORKER.replace("__LECONS__", json.dumps(lecons, ensure_ascii=False))
                  .replace("__ESSAI__", str(ESSAI_JOURS)))
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(code)


# --------------------------------------------------------------------------------------------------------------------
# Côté site
# --------------------------------------------------------------------------------------------------------------------
CSS = """<style>
.rbp-offre{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px;margin:14px 0}
.rbp-carte{border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:var(--surface)}
.rbp-carte.plus{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset}
.rbp-prix{font-size:30px;font-weight:700;font-family:var(--m);margin:4px 0 8px}.rbp-prix small{font-size:15px;color:var(--muted);font-weight:500}
.rbp-liste{padding-left:1.1em}.rbp-liste li{margin:6px 0}
.rbp-verrou{border:1px dashed var(--line);border-radius:14px;padding:18px;text-align:center;background:var(--surface-2)}
.rbp-code{font-family:var(--m);font-size:16px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);width:100%;box-sizing:border-box}
.rbp-etat{font-size:14.5px}
</style>"""

JS = """<script>
const RBP={api:__API__,cle:'rb-plus-code',
 code(){try{return localStorage.getItem(this.cle)||''}catch(e){return ''}},
 garder(c){try{localStorage.setItem(this.cle,c)}catch(e){}},
 oublier(){try{localStorage.removeItem(this.cle)}catch(e){}},
 async appel(ch,donnees){if(!this.api)throw new Error('off');const r=await fetch(this.api+ch,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(donnees||{})});return r.json()},
 async verifier(){const c=this.code();if(!c)return {ok:false};try{const v=await this.appel('/verifier',{code:c});try{sessionStorage.setItem('rb-plus-ok',v.ok?'1':'0')}catch(e){}return v}catch(e){return {ok:false,hors_ligne:true}}}
};
</script>"""


def _js():
    # le serveur sert aussi à l'analyse approfondie (1 gratuite) : il est utilisable dès qu'il est réglé,
    # même si la vente n'est pas encore ouverte (le bouton « S'abonner » reste, lui, caché sans identité du vendeur)
    return JS.replace("__API__", json.dumps(reglages()["api"]))


def _page_offre(base, csp):
    chemin = "radar-bourse-plus.html"
    on = actif()
    lecons = "".join(f"<li><a href='plus/{l['id']}.html'>{_e(l['titre'])}</a></li>" for l in LECONS_PLUS)
    faq = [("Comment marche le mois gratuit ?",
            f"Tu t'abonnes, tu ne paies rien pendant {ESSAI_JOURS} jours. Si tu résilies avant la fin de l'essai, tu ne paies jamais rien. "
            f"Sinon, l'abonnement passe à {PRIX} par mois. Un rappel n'est pas garanti : note la date."),
           ("Comment résilier ?", "En un clic, avec le bouton « Gérer ou résilier mon abonnement » de cette page : tu arrives sur l'espace "
            "sécurisé de Stripe. L'accès reste ouvert jusqu'à la fin de la période déjà payée."),
           ("Mes données bancaires sont-elles en sécurité ?", "Le paiement se fait uniquement sur la page sécurisée de Stripe, un prestataire "
            "de paiement agréé. Radar Bourse ne voit et ne garde jamais ton numéro de carte."),
           ("Le gratuit va-t-il disparaître ?", "Non. Le radar, les fiches, les prévisions, les résultats, les outils et l'Académie restent gratuits "
            f"(avec {LIMITE_GRATUITE} grandes leçons par jour). Radar Bourse+ ajoute des cours avancés et lève la limite."),
           ("Est-ce un service de conseil en investissement ?", "Non. Radar Bourse+ vend de la formation : des cours, des exercices et des outils. "
            "Aucun abonnement ne donne de recommandation personnalisée d'achat ou de vente.")]
    bouton = ("<p><button type='button' class='btn' id='rbp-go' style='font-size:17px;padding:12px 20px'>Essayer gratuitement pendant 1 mois</button></p>"
              f"<p class='muted' style='font-size:14px'>Puis {PRIX} par mois, sans engagement. Paiement sécurisé par Stripe. "
              "En continuant, tu acceptes les <a href='cgv.html'>conditions générales de vente</a>.</p>") if on else \
             "<div class='carte'><b>Bientôt disponible.</b> L'abonnement n'est pas encore ouvert : tout le contenu ci-dessous sera accessible au lancement.</div>"
    corps = (CSS + "<h1>Radar Bourse+ : apprendre plus loin, sans limite</h1>"
             f"<p>Le site reste gratuit. Radar Bourse+ ajoute des <b>cours avancés</b> (le parcours « Analyste ») et lève la limite de "
             f"{LIMITE_GRATUITE} grandes leçons par jour de l'Académie, et les <a href='analyse-approfondie.html'>analyses approfondies</a> deviennent illimitées. <b>Le premier mois est gratuit</b>, ensuite {PRIX} par mois, résiliable en un clic.</p>"
             + bouton +
             "<div class='rbp-offre'><div class='rbp-carte'><h2 style='margin-top:0'>Gratuit</h2><p class='rbp-prix'>0 €</p><ul class='rbp-liste'>"
             "<li>Le radar, les fiches, les prévisions et leurs vrais résultats</li><li>Les outils et simulateurs</li>"
             f"<li>L'Académie : {LIMITE_GRATUITE} grandes leçons par jour</li><li>1 analyse approfondie offerte</li><li>Sans compte, sans publicité</li></ul></div>"
             f"<div class='rbp-carte plus'><h2 style='margin-top:0'>Radar Bourse+</h2><p class='rbp-prix'>{PRIX} <small>/ mois après 1 mois offert</small></p><ul class='rbp-liste'>"
             "<li>Tout le gratuit</li><li><b>Analyses approfondies illimitées</b> de n'importe quel titre (gratuit : 1)</li><li>L'Académie <b>sans limite</b></li><li>Le parcours avancé « Analyste » (bilans, valorisation, pièges statistiques), enrichi chaque mois</li>"
             "<li>Toujours sans publicité, résiliable en un clic</li></ul></div></div>"
             f"<h2>Le parcours « Analyste »</h2><ul class='rbp-liste'>{lecons}</ul>"
             "<h2>Déjà abonné ?</h2><div class='rbp-carte'><label for='rbp-in'><b>Ton code d'accès</b> (il commence par RBP-)</label>"
             "<input id='rbp-in' class='rbp-code' autocomplete='off' spellcheck='false' placeholder='RBP-…' style='margin:8px 0'>"
             "<p style='display:flex;gap:8px;flex-wrap:wrap'><button type='button' class='btn' id='rbp-ok'>Activer sur cet appareil</button>"
             "<button type='button' class='btn ghost' id='rbp-portail'>Gérer ou résilier mon abonnement</button></p>"
             "<p class='rbp-etat' id='rbp-etat' aria-live='polite'></p></div>"
             "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{_e(r)}</p>" for q, r in faq)
             + "<p class='muted'><a href='cgv.html'>Conditions générales de vente et mentions légales</a></p>"
             + _js() + """<script>
(function(){const etat=document.getElementById('rbp-etat'),inp=document.getElementById('rbp-in');inp.value=RBP.code();
const d=t=>t?new Date(t*1000).toLocaleDateString('fr-FR',{day:'numeric',month:'long',year:'numeric'}):'';
async function montrer(){if(!RBP.code()){etat.textContent='';return}etat.textContent='Vérification…';const v=await RBP.verifier();
 etat.innerHTML=v.ok?('✅ Abonnement actif'+(v.statut==='trialing'&&v.fin_essai?' : essai gratuit jusqu\\u2019au '+d(v.fin_essai):'')+(v.annule?' (résilié, accès jusqu\\u2019au '+d(v.fin_periode)+')':'')+'.')
 :v.hors_ligne?'Serveur injoignable pour le moment, réessaie plus tard.':'Ce code n\\u2019est pas (ou plus) actif.'}
const go=document.getElementById('rbp-go');if(go)go.onclick=async()=>{go.disabled=true;go.textContent='Ouverture du paiement sécurisé…';
 try{const r=await RBP.appel('/checkout');if(r.url&&/^https:\\/\\/checkout\\.stripe\\.com\\//.test(r.url))location.href=r.url;else throw 0}catch(e){go.disabled=false;go.textContent='Réessayer';etat.textContent='Le paiement n\\u2019a pas pu s\\u2019ouvrir. Réessaie dans un instant.'}};
document.getElementById('rbp-ok').onclick=()=>{const c=inp.value.trim();if(!c)return;RBP.garder(c);montrer()};
document.getElementById('rbp-portail').onclick=async()=>{const c=inp.value.trim()||RBP.code();if(!c){etat.textContent='Entre d\\u2019abord ton code d\\u2019accès.';return}
 try{const r=await RBP.appel('/portail',{code:c});if(r.url&&/^https:\\/\\/billing\\.stripe\\.com\\//.test(r.url))location.href=r.url;else etat.textContent='Code non reconnu.'}catch(e){etat.textContent='Serveur injoignable.'}};
montrer();})();
</script>""")
    jl = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    return chemin, seo._page(base, f"Radar Bourse+ : cours avancés de Bourse, 1 mois gratuit | {NOM}",
                             f"Le site reste gratuit. Radar Bourse+ ajoute le parcours avancé « Analyste » et l'Académie sans limite : 1 mois gratuit, puis {PRIX} par mois.",
                             chemin, corps, jl, csp=_csp(csp))


def _page_merci(base, csp):
    chemin = "merci-plus.html"
    corps = (CSS + "<h1>Bienvenue dans Radar Bourse+</h1><div class='rbp-carte' id='m'><p>Vérification du paiement…</p></div>"
             "<p class='muted'>Si cette page reste bloquée, reviens dans quelques minutes : le paiement peut mettre un instant à être confirmé.</p>"
             + _js() + """<script>
(async function(){const m=document.getElementById('m'),id=new URLSearchParams(location.search).get('session_id');
if(!id||!RBP.api){m.innerHTML='<p>Lien incomplet.</p>';return}
try{const r=await fetch(RBP.api+'/retour?session_id='+encodeURIComponent(id)).then(x=>x.json());
 if(!r.ok||!r.code){m.innerHTML='<p>Le paiement n\\u2019est pas encore confirmé. Recharge la page dans une minute.</p>';return}
 RBP.garder(r.code);const fin=r.fin_essai?new Date(r.fin_essai*1000).toLocaleDateString('fr-FR',{day:'numeric',month:'long'}):'';
 m.innerHTML='<p>✅ C\\u2019est activé sur cet appareil'+(fin?' : ton essai gratuit dure jusqu\\u2019au <b>'+fin+'</b>':'')+'.</p>'+
  '<p><b>Garde ce code d\\u2019accès</b> (pour tes autres appareils). Ne le partage pas : il donne accès à ton abonnement.</p><p><input class="rbp-code" readonly value="'+r.code.replace(/[^A-Za-z0-9_-]/g,'')+'"></p>'+
  '<p><a class="btn" href="academie-plus.html">Commencer le parcours Analyste</a></p>';
 history.replaceState(null,'',location.pathname)}catch(e){m.innerHTML='<p>Serveur injoignable, recharge la page dans un instant.</p>'}})();
</script>""")
    page = seo._page(base, f"Merci : Radar Bourse+ est activé | {NOM}", "Activation de Radar Bourse+.", chemin, corps, csp=_csp(csp))
    return chemin, page.replace('content="index, follow', 'content="noindex, nofollow', 1)


def _page_lecon(base, l, csp):
    chemin = f"plus/{l['id']}.html"
    if not actif():   # version 107 : tout est gratuit, la leçon est publiée en entier (et lisible par Google)
        idx = [x["id"] for x in LECONS_PLUS].index(l["id"])
        suiv = LECONS_PLUS[idx + 1] if idx + 1 < len(LECONS_PLUS) else None
        corps = (CSS + f"<p class='muted'><a href='../academie-plus.html'>Parcours Analyste</a> · cours avancé gratuit · {l['minutes']} min</p>"
                 f"<h1>{_e(l['titre'])}</h1><p>{_e(l['resume'])}</p><nav class='carte'><b>Au programme</b><ol>" + "".join(f"<li>{_e(x)}</li>" for x in l["plan"]) + "</ol></nav>"
                 f"<article class='aca-cours'>{l['contenu']}</article>"
                 + (f"<p><a class='btn' href='{suiv['id']}.html'>Leçon suivante : {_e(suiv['titre'])}</a></p>" if suiv else
                    "<p><a class='btn' href='../formation.html'>Retour à l'Académie</a>" + (" <a class='btn ghost' href='../analyse-approfondie.html'>Essayer une analyse approfondie</a>" if analyse_ouverte() else "") + "</p>"))
        jl = {"@context": "https://schema.org", "@type": "LearningResource", "name": l["titre"], "description": l["resume"], "inLanguage": "fr",
              "learningResourceType": "Cours", "educationalLevel": "avancé", "timeRequired": f"PT{l['minutes']}M", "isAccessibleForFree": True,
              "author": {"@type": "Person", "name": "maxitemmmm"}}
        return chemin, seo._page(base, f"{l['titre']} | Cours de Bourse avancé gratuit", l["resume"], chemin, corps, jl, csp=csp)
    corps = (CSS + f"<p class='muted'><a href='../academie-plus.html'>Parcours Analyste</a> · Radar Bourse+ · {l['minutes']} min</p>"
             f"<h1>{_e(l['titre'])}</h1><p>{_e(l['resume'])}</p><h2>Au programme</h2><ol>" + "".join(f"<li>{_e(x)}</li>" for x in l["plan"]) + "</ol>"
             "<div id='rbp-zone'><div class='rbp-verrou'><p><b>Cette leçon fait partie de Radar Bourse+.</b></p>"
             "<p>1 mois gratuit, puis 2 € par mois, résiliable en un clic.</p><p><a class='btn' href='../radar-bourse-plus.html'>Découvrir Radar Bourse+</a></p></div></div>"
             + _js() + f"""<script>
(async function(){{if(!RBP.code()||!RBP.api)return;const z=document.getElementById('rbp-zone');
try{{const r=await RBP.appel('/lecon',{{code:RBP.code(),id:{json.dumps(l['id'])}}});if(r.ok&&r.html){{z.innerHTML='<article class="aca-cours">'+r.html+'</article>';}}}}catch(e){{}}}})();
</script>""")
    jl = {"@context": "https://schema.org", "@type": "LearningResource", "name": l["titre"], "description": l["resume"], "inLanguage": "fr",
          "isAccessibleForFree": False, "hasPart": {"@type": "WebPageElement", "isAccessibleForFree": False, "cssSelector": "#rbp-zone"}}
    return chemin, seo._page(base, f"{l['titre']} | Radar Bourse+", l["resume"], chemin, corps, jl, csp=_csp(csp))


def _page_parcours(base, csp):
    chemin = "academie-plus.html"
    corps = (CSS + ("<h1>Le parcours « Analyste » (Radar Bourse+)</h1><p>Pour aller au-delà des bases : lire les comptes d'une entreprise, "
             "la valoriser, et éviter les pièges statistiques qui font croire à de fausses certitudes. Le plan de chaque leçon est visible par tous.</p>"
             if actif() else "<h1>Le parcours « Analyste » : cours de Bourse avancés, gratuits</h1><p>Tu as fini les bases de l'Académie ? Va plus loin : "
             "lire les comptes d'une entreprise comme un analyste, la valoriser par la méthode des flux actualisés (DCF), et repérer les pièges statistiques "
             "qui font croire à de fausses certitudes. Chaque leçon a un exercice corrigé.</p>")
             + "<div class='rbp-offre'>" + "".join(
                 f"<a class='rbp-carte' style='text-decoration:none;color:inherit' href='plus/{l['id']}.html'><b style='font-size:17px'>{_e(l['titre'])}</b>"
                 f"<p class='muted' style='margin:6px 0 0'>{_e(l['resume'])}</p><p class='muted' style='font-size:13px'>{l['minutes']} min</p></a>" for l in LECONS_PLUS)
             + ("</div><p><a href='radar-bourse-plus.html'>Comment accéder au parcours (1 mois gratuit)</a> · <a href='formation.html'>L'Académie gratuite</a></p>"
                if actif() else "</div><p><a href='formation.html'>Revoir les bases à l'Académie</a>" + (" · <a href='analyse-approfondie.html'>Lancer une analyse approfondie</a>" if analyse_ouverte() else "") + "</p>"))
    return chemin, seo._page(base, f"Parcours Analyste : cours de Bourse avancés gratuits | {NOM}",
                             "Lire un bilan, valoriser une entreprise par DCF, éviter les pièges statistiques : cours de Bourse avancés, gratuits, avec exercices corrigés.",
                             chemin, corps, csp=csp)


def _page_cgv(base, csp):
    chemin = "cgv.html"
    r = reglages()
    if not actif():
        corps = ("<h1>Conditions générales de vente</h1><p>Aucun produit n'est vendu sur Radar Bourse pour le moment. "
                 "Les conditions de vente seront publiées ici avant l'ouverture de l'abonnement.</p>")
    else:
        corps = ("<h1>Conditions générales de vente et mentions légales</h1>"
                 f"<h2>Vendeur</h2><p>{_e(r['nom'])}, entrepreneur individuel (micro-entreprise), SIRET {_e(r['siret'])}, {_e(r['adresse'])}. "
                 f"Contact : {_e(r['email'])}. TVA non applicable, article 293 B du CGI.</p>"
                 "<h2>Hébergement</h2><p>Site hébergé par GitHub Pages (GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis). "
                 "Paiements traités par Stripe. Serveur d'abonnement : Cloudflare.</p>"
                 f"<h2>Objet</h2><p>Radar Bourse+ est un abonnement à des contenus de formation en ligne (cours, exercices). Ce n'est pas un service de "
                 "conseil en investissement : aucune recommandation personnalisée d'achat ou de vente n'est fournie.</p>"
                 f"<h2>Prix et essai gratuit</h2><p>{PRIX} TTC par mois, prélevés chaque mois à la date anniversaire. Les {ESSAI_JOURS} premiers jours sont gratuits ; "
                 "le premier prélèvement a lieu à la fin de l'essai, sauf résiliation avant cette date. Un seul essai gratuit par personne.</p>"
                 "<h2>Paiement</h2><p>Par carte bancaire, sur la page sécurisée de Stripe. Le vendeur n'a jamais accès aux données de carte.</p>"
                 "<h2>Résiliation</h2><p>À tout moment, en un clic, depuis la page Radar Bourse+ (bouton « Gérer ou résilier mon abonnement »). "
                 "L'accès reste ouvert jusqu'à la fin de la période payée ; aucun prélèvement n'a lieu ensuite.</p>"
                 f"<h2>Droit de rétractation</h2><p>Tu disposes de 14 jours à compter de la souscription pour te rétracter, sans justification, en écrivant à {_e(r['email'])} "
                 f"ou en résiliant. Ces 14 jours se terminent pendant l'essai gratuit de {ESSAI_JOURS} jours : aucune somme n'a donc été prélevée pendant le délai de rétractation.</p>"
                 f"<h2>Réclamations et médiation</h2><p>Écris d'abord à {_e(r['email'])}. En cas de litige non résolu, tu peux recourir gratuitement à un médiateur de la consommation "
                 "(coordonnées communiquées sur demande) ou à la plateforme européenne de règlement en ligne des litiges.</p>"
                 "<h2>Données personnelles</h2><p>Le site ne crée pas de compte. Pour l'abonnement, Stripe traite ton adresse email et tes données de paiement "
                 "pour le compte du vendeur ; aucune autre donnée n'est collectée. Tu peux demander l'accès ou la suppression de tes données par email.</p>")
    return chemin, seo._page(base, f"Conditions générales de vente | {NOM}", "Conditions générales de vente de Radar Bourse+ et mentions légales du vendeur.",
                             chemin, corps, csp=csp)


def _csp(csp):
    """Autorise le site à parler au serveur d'abonnement (et seulement à lui)."""
    api = reglages()["api"]
    if not csp or not api or api in csp:
        return csp
    return csp.replace("connect-src 'self'", f"connect-src 'self' {api}", 1)


def script_limite(chap_id: str) -> str:
    """Académie : 3 grandes leçons différentes par jour sans abonnement (actif seulement quand l'abonnement est ouvert).
    Limite douce (compteur sur l'appareil) : honnête et sans compte, mais contournable — on le sait."""
    if not actif():
        return ""
    return (_js() + "<script>(async function(){try{const id=" + json.dumps(chap_id) + ",j=new Date().toISOString().slice(0,10),k='rb-aca-jour';"
            "let s={};try{s=JSON.parse(localStorage.getItem(k)||'{}')}catch(e){}if(s.j!==j)s={j:j,l:[]};"
            "if(!s.l.includes(id)){if(s.l.length>=" + str(LIMITE_GRATUITE) + "){"
            "if(RBP.code()){const v=await RBP.verifier();if(v.ok||v.hors_ligne)return}"
            "const a=document.querySelector('.aca-cours')||document.querySelector('main#contenu');if(!a)return;a.innerHTML='<div class=\"carte\" style=\"text-align:center;padding:24px\"><h2>Tu as fait tes "
            + str(LIMITE_GRATUITE) + " grandes leçons du jour 🎉</h2><p>Reviens demain pour la suite, ou continue sans limite avec Radar Bourse+ (1 mois gratuit, puis 2 € par mois).</p>"
            "<p><a class=\"btn\" href=\"../radar-bourse-plus.html\">Essayer Radar Bourse+</a> <a class=\"btn ghost\" href=\"../formation.html\">Retour à l\\u2019Académie</a></p></div>';return}"
            "s.l.push(id);localStorage.setItem(k,JSON.stringify(s))}}catch(e){}})();</script>")


def generer(dossier: str, csp: str, base: str) -> list:
    os.makedirs(os.path.join(dossier, "plus"), exist_ok=True)
    # version 107 : sans vente, pas de page d'offre ni de remerciement (le code reste prêt, mis de côté)
    pages = ([_page_offre(base, csp), _page_merci(base, csp)] if actif() else []) + [_page_parcours(base, csp), _page_cgv(base, csp)] + \
            [_page_lecon(base, l, csp) for l in LECONS_PLUS]
    urls = []
    for chemin, page in pages:
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        if chemin != "merci-plus.html":
            urls.append((chemin, "monthly", "0.7"))
    return urls
