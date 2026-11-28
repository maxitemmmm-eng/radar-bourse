// Radar Bourse — serveur « communauté » (version 119) : comptes, commentaires modérés, sauvegarde de « Mon espace ».
// Cloudflare Worker gratuit, mémoire KV « COMMU ». Installé par installer_communaute.py (aucune clé ne passe par le site).
//
// Comptes : pseudo + mot de passe (jamais stocké : empreinte PBKDF2-SHA256, 100 000 tours, sel propre à chaque compte),
// + un code de secours donné une seule fois à l'inscription (pour changer de mot de passe sans e-mail).
// Aucune adresse e-mail, aucune donnée personnelle demandée. Adresse IP : seulement une empreinte salée, gardée 24 h (anti-abus).
// Commentaires : publiés tout de suite s'ils passent les filtres (pas de lien, pas d'insulte, 2 à 1 000 caractères, rythme limité),
// cachés automatiquement après 3 signalements, supprimables par l'auteur et par la modération (clé ADMIN_KEY).

const enc = new TextEncoder();
const b64 = u8 => btoa(String.fromCharCode(...u8)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const hex = u8 => [...u8].map(b => b.toString(16).padStart(2, "0")).join("");
const alea = n => crypto.getRandomValues(new Uint8Array(n));
const PSEUDO = /^[A-Za-z0-9_-]{3,20}$/;
const PAGE = /^[a-z0-9][a-z0-9/._-]{0,119}$/;
const LIEN = /(https?:\/\/|www\.|\b[a-z0-9-]{2,}\.(com|fr|net|org|io|xyz|co|me|ly|gg|link|app|site|online|info|biz|ru|top|shop|club)\b|t\.me\/|@[a-z0-9_]{3,}\b)/i;
const GROS_MOTS = ["connard", "connards", "connasse", "salope", "salopes", "encule", "enculer", "encules", "pute", "putes", "batard", "batards",
  "nique ta", "ntm", "fdp", "pd", "tapette", "negro", "bougnoul", "youpin", "sale arabe", "sale noir", "sale juif", "kys", "suicide toi"];
// mot entier seulement (« réputé » ou « computer » ne sont pas bloqués)
const RX_GROS = new RegExp("(^|[^a-z0-9])(" + GROS_MOTS.map(m => m.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(?=$|[^a-z0-9])");
const RESERVES = ["admin", "moderateur", "moderation", "radarbourse", "radar-bourse", "radar_bourse", "support", "officiel"];

function reponse(env, req, corps, statut = 200) {
  const o = req.headers.get("Origin") || "";
  const ok = !env.SITE || o === env.SITE || o === env.SITE.replace("https://", "https://www.") || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o);
  return new Response(JSON.stringify(corps), {status: statut, headers: {
    "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": ok ? o : (env.SITE || "*"), "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS", "Vary": "Origin"}});
}
const erreur = (env, req, msg, statut = 400) => reponse(env, req, {ok: false, erreur: msg}, statut);

async function empreinte(mdp, sel) {
  const cle = await crypto.subtle.importKey("raw", enc.encode(mdp), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({name: "PBKDF2", hash: "SHA-256", salt: sel, iterations: 100000}, cle, 256);
  return hex(new Uint8Array(bits));
}
const egal = (a, b) => { if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; };
async function sha(t) { return hex(new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(t)))); }
const ipEmpreinte = async (req, env) => (await sha((req.headers.get("CF-Connecting-IP") || "?") + "|" + (env.SEL || "sel") + "|" + new Date().toISOString().slice(0, 10))).slice(0, 24);

async function lireJ(env, k, def = null) { const v = await env.COMMU.get(k); if (v == null) return def; try { return JSON.parse(v); } catch (e) { return def; } }
const ecrireJ = (env, k, v, opts) => env.COMMU.put(k, JSON.stringify(v), opts);

// compteur simple par jour (anti-abus) ; renvoie true si la limite est dépassée
async function limite(env, cle, max, ttl = 86400) {
  const k = "lim:" + cle; const n = +(await env.COMMU.get(k) || 0);
  if (n >= max) return true;
  await env.COMMU.put(k, String(n + 1), {expirationTtl: ttl});
  return false;
}

async function session(req, env) {
  const h = req.headers.get("Authorization") || ""; const t = h.startsWith("Bearer ") ? h.slice(7) : "";
  if (!/^[A-Za-z0-9_-]{30,60}$/.test(t)) return null;
  const s = await lireJ(env, "s:" + t); if (!s) return null;
  const u = await lireJ(env, "u:" + s.p.toLowerCase()); if (!u || u.banni) return null;
  return {jeton: t, pseudo: u.pseudo, u};
}
async function nouvelleSession(env, pseudo) {
  const t = b64(alea(32));
  await ecrireJ(env, "s:" + t, {p: pseudo, d: Date.now()}, {expirationTtl: 60 * 86400});
  return t;
}
const estAdmin = (req, env) => { const h = req.headers.get("Authorization") || ""; return !!env.ADMIN_KEY && env.ADMIN_KEY.length >= 24 && egal(h, "Bearer " + env.ADMIN_KEY); };

function filtrer(texte) {
  const t = String(texte || "").replace(/\r/g, "").replace(/\n{3,}/g, "\n\n").trim();
  if (t.length < 2) return [null, "Message trop court."];
  if (t.length > 1000) return [null, "Message trop long (1 000 caractères au plus)."];
  if (LIEN.test(t)) return [null, "Les liens et les adresses sont interdits dans les commentaires."];
  const bas = t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[-_]/g, " ");
  if (RX_GROS.test(bas)) return [null, "Ce message contient des mots interdits par les règles de la communauté."];
  if (/(.)\1{9,}/.test(t)) return [null, "Message refusé (caractères répétés)."];
  return [t, null];
}

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return reponse(env, req, {});
    const url = new URL(req.url); const ch = url.pathname;
    let corps = {};
    if (req.method === "POST" || req.method === "DELETE") { try { corps = await req.json(); } catch (e) { corps = {}; } }
    try {
      // ---------------------------------------------------------------- comptes
      if (ch === "/inscription" && req.method === "POST") {
        const pseudo = String(corps.pseudo || "").trim(), mdp = String(corps.mdp || "");
        if (!PSEUDO.test(pseudo)) return erreur(env, req, "Pseudo : 3 à 20 caractères, lettres, chiffres, - et _ seulement.");
        if (RESERVES.some(r => pseudo.toLowerCase().includes(r))) return erreur(env, req, "Ce pseudo est réservé.");
        if (mdp.length < 8 || mdp.length > 200) return erreur(env, req, "Mot de passe : 8 caractères au moins.");
        if (corps.regles !== true) return erreur(env, req, "Il faut accepter les règles de la communauté.");
        if (await limite(env, "insc:" + await ipEmpreinte(req, env), 5)) return erreur(env, req, "Trop de comptes créés aujourd'hui depuis cette connexion. Réessaie demain.", 429);
        const k = "u:" + pseudo.toLowerCase();
        if (await env.COMMU.get(k)) return erreur(env, req, "Ce pseudo est déjà pris.");
        const sel = alea(16), secours = hex(alea(10)).toUpperCase().match(/.{4}/g).join("-"), sel2 = alea(16);
        await ecrireJ(env, k, {pseudo, sel: b64(sel), h: await empreinte(mdp, sel), s2: b64(sel2), hs: await empreinte(secours, sel2), cree: Date.now()});
        return reponse(env, req, {ok: true, pseudo, jeton: await nouvelleSession(env, pseudo), secours});
      }
      if (ch === "/connexion" && req.method === "POST") {
        const pseudo = String(corps.pseudo || "").trim(), mdp = String(corps.mdp || "");
        const ip = await ipEmpreinte(req, env);
        if (await limite(env, "cx:" + ip, 30, 3600)) return erreur(env, req, "Trop d'essais : attends une heure.", 429);
        const u = PSEUDO.test(pseudo) ? await lireJ(env, "u:" + pseudo.toLowerCase()) : null;
        const sel = u ? Uint8Array.from(atob(u.sel.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0)) : alea(16);
        const h = await empreinte(mdp, sel);   // calcul fait même si le compte n'existe pas (même durée de réponse)
        if (!u || !egal(h, u.h)) return erreur(env, req, "Pseudo ou mot de passe incorrect.", 401);
        if (u.banni) return erreur(env, req, "Ce compte a été suspendu pour non-respect des règles.", 403);
        return reponse(env, req, {ok: true, pseudo: u.pseudo, jeton: await nouvelleSession(env, u.pseudo)});
      }
      if (ch === "/secours" && req.method === "POST") {   // nouveau mot de passe avec le code de secours
        const pseudo = String(corps.pseudo || "").trim(), code = String(corps.code || "").trim().toUpperCase(), mdp = String(corps.mdp || "");
        if (await limite(env, "sec:" + await ipEmpreinte(req, env), 10, 3600)) return erreur(env, req, "Trop d'essais : attends une heure.", 429);
        if (mdp.length < 8) return erreur(env, req, "Nouveau mot de passe : 8 caractères au moins.");
        const u = PSEUDO.test(pseudo) ? await lireJ(env, "u:" + pseudo.toLowerCase()) : null;
        const s2 = u ? Uint8Array.from(atob(u.s2.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0)) : alea(16);
        const h = await empreinte(code, s2);
        if (!u || !egal(h, u.hs)) return erreur(env, req, "Pseudo ou code de secours incorrect.", 401);
        const sel = alea(16), secours = hex(alea(10)).toUpperCase().match(/.{4}/g).join("-"), sel2 = alea(16);
        Object.assign(u, {sel: b64(sel), h: await empreinte(mdp, sel), s2: b64(sel2), hs: await empreinte(secours, sel2)});
        await ecrireJ(env, "u:" + pseudo.toLowerCase(), u);
        return reponse(env, req, {ok: true, pseudo: u.pseudo, jeton: await nouvelleSession(env, u.pseudo), secours});
      }
      if (ch === "/moi" && req.method === "GET") {
        const s = await session(req, env); if (!s) return erreur(env, req, "Non connecté.", 401);
        return reponse(env, req, {ok: true, pseudo: s.pseudo, cree: s.u.cree});
      }
      if (ch === "/deconnexion" && req.method === "POST") {
        const s = await session(req, env); if (s) await env.COMMU.delete("s:" + s.jeton);
        return reponse(env, req, {ok: true});
      }
      if (ch === "/compte" && req.method === "DELETE") {   // RGPD : suppression du compte, de ses données et de ses commentaires
        const s = await session(req, env); if (!s) return erreur(env, req, "Non connecté.", 401);
        const mes = await lireJ(env, "mes:" + s.pseudo.toLowerCase(), []);
        for (const [page, id] of mes) { const L = await lireJ(env, "c:" + page, []); await ecrireJ(env, "c:" + page, L.filter(c => c.id !== id)); }
        await Promise.all(["u:", "d:", "mes:"].map(p => env.COMMU.delete(p + s.pseudo.toLowerCase())));
        await env.COMMU.delete("s:" + s.jeton);
        return reponse(env, req, {ok: true});
      }
      // ---------------------------------------------------------------- sauvegarde de « Mon espace » (favoris, progression…)
      if (ch === "/donnees") {
        const s = await session(req, env); if (!s) return erreur(env, req, "Non connecté.", 401);
        const k = "d:" + s.pseudo.toLowerCase();
        if (req.method === "GET") return reponse(env, req, {ok: true, donnees: await lireJ(env, k, {}), });
        if (req.method === "POST") {
          const txt = JSON.stringify(corps.donnees || {});
          if (txt.length > 200000) return erreur(env, req, "Données trop volumineuses.");
          if (await limite(env, "sync:" + s.pseudo.toLowerCase(), 40)) return erreur(env, req, "Trop de sauvegardes aujourd'hui.", 429);
          await env.COMMU.put(k, txt);
          return reponse(env, req, {ok: true, le: Date.now()});
        }
      }
      // ---------------------------------------------------------------- commentaires
      if (ch === "/commentaires" && req.method === "GET") {
        const page = String(url.searchParams.get("page") || "");
        if (!PAGE.test(page)) return erreur(env, req, "Page inconnue.");
        const L = await lireJ(env, "c:" + page, []);
        return reponse(env, req, {ok: true, commentaires: L.filter(c => !c.cache).map(({id, p, t, d, r}) => ({id, p, t, d, r: r ? r.length : 0}))});
      }
      if (ch === "/commentaires" && req.method === "POST") {
        const s = await session(req, env); if (!s) return erreur(env, req, "Connecte-toi pour commenter.", 401);
        const page = String(corps.page || "");
        if (!PAGE.test(page)) return erreur(env, req, "Page inconnue.");
        const [t, pb] = filtrer(corps.texte); if (pb) return erreur(env, req, pb);
        const pk = s.pseudo.toLowerCase();
        if (await env.COMMU.get("rythme:" + pk)) return erreur(env, req, "Attends 30 secondes entre deux commentaires.", 429);
        if (await limite(env, "com:" + pk, 20)) return erreur(env, req, "20 commentaires par jour au plus.", 429);
        await env.COMMU.put("rythme:" + pk, "1", {expirationTtl: 60});
        const L = await lireJ(env, "c:" + page, []);
        const c = {id: b64(alea(9)), p: s.pseudo, t, d: Date.now(), r: []};
        L.push(c); while (L.length > 300) L.shift();
        await ecrireJ(env, "c:" + page, L);
        const mes = await lireJ(env, "mes:" + pk, []); mes.push([page, c.id]); await ecrireJ(env, "mes:" + pk, mes.slice(-500));
        const R = await lireJ(env, "recents", []); R.unshift([page, c.id, s.pseudo, t.slice(0, 200), c.d]); await ecrireJ(env, "recents", R.slice(0, 200));
        return reponse(env, req, {ok: true, commentaire: {id: c.id, p: c.p, t: c.t, d: c.d, r: 0}});
      }
      if (ch === "/commentaires" && req.method === "DELETE") {   // l'auteur ou la modération
        const page = String(corps.page || ""), id = String(corps.id || "");
        if (!PAGE.test(page)) return erreur(env, req, "Page inconnue.");
        const admin = estAdmin(req, env), s = admin ? null : await session(req, env);
        if (!admin && !s) return erreur(env, req, "Non autorisé.", 401);
        const L = await lireJ(env, "c:" + page, []);
        const c = L.find(x => x.id === id); if (!c) return erreur(env, req, "Commentaire introuvable.", 404);
        if (!admin && c.p.toLowerCase() !== s.pseudo.toLowerCase()) return erreur(env, req, "Tu ne peux supprimer que tes propres commentaires.", 403);
        await ecrireJ(env, "c:" + page, L.filter(x => x.id !== id));
        return reponse(env, req, {ok: true});
      }
      if (ch === "/signaler" && req.method === "POST") {
        const s = await session(req, env); if (!s) return erreur(env, req, "Connecte-toi pour signaler un commentaire.", 401);
        const page = String(corps.page || ""), id = String(corps.id || "");
        if (!PAGE.test(page)) return erreur(env, req, "Page inconnue.");
        if (await limite(env, "sig:" + s.pseudo.toLowerCase(), 30)) return erreur(env, req, "Trop de signalements aujourd'hui.", 429);
        const L = await lireJ(env, "c:" + page, []); const c = L.find(x => x.id === id);
        if (!c) return erreur(env, req, "Commentaire introuvable.", 404);
        c.r = c.r || []; if (!c.r.includes(s.pseudo.toLowerCase())) c.r.push(s.pseudo.toLowerCase());
        if (c.r.length >= 3) c.cache = true;   // caché en attendant la modération
        await ecrireJ(env, "c:" + page, L);
        const S = await lireJ(env, "signales", []); if (!S.some(x => x[1] === id)) S.unshift([page, id, c.p, c.t.slice(0, 200), Date.now()]);
        await ecrireJ(env, "signales", S.slice(0, 200));
        return reponse(env, req, {ok: true, cache: !!c.cache});
      }
      // ---------------------------------------------------------------- modération (toi seule, avec la clé ADMIN_KEY)
      if (ch.startsWith("/admin/")) {
        if (!estAdmin(req, env)) return erreur(env, req, "Clé de modération incorrecte.", 401);
        if (ch === "/admin/apercu" && req.method === "GET")
          return reponse(env, req, {ok: true, recents: await lireJ(env, "recents", []), signales: await lireJ(env, "signales", [])});
        if (ch === "/admin/retablir" && req.method === "POST") {
          const page = String(corps.page || ""), id = String(corps.id || "");
          const L = await lireJ(env, "c:" + page, []); const c = L.find(x => x.id === id); if (!c) return erreur(env, req, "Introuvable.", 404);
          c.cache = false; c.r = []; await ecrireJ(env, "c:" + page, L);
          await ecrireJ(env, "signales", (await lireJ(env, "signales", [])).filter(x => x[1] !== id));
          return reponse(env, req, {ok: true});
        }
        if (ch === "/admin/classer" && req.method === "POST") {   // retire de la liste des signalés après traitement
          await ecrireJ(env, "signales", (await lireJ(env, "signales", [])).filter(x => x[1] !== String(corps.id || "")));
          return reponse(env, req, {ok: true});
        }
        if (ch === "/admin/bannir" && req.method === "POST") {
          const pk = String(corps.pseudo || "").toLowerCase(); const u = await lireJ(env, "u:" + pk);
          if (!u) return erreur(env, req, "Compte introuvable.", 404);
          u.banni = corps.banni !== false; await ecrireJ(env, "u:" + pk, u);
          return reponse(env, req, {ok: true, banni: u.banni});
        }
      }
      if (ch === "/" ) return reponse(env, req, {ok: true, service: "Radar Bourse — communauté"});
      return erreur(env, req, "Adresse inconnue.", 404);
    } catch (e) {
      return erreur(env, req, "Erreur du serveur, réessaie dans un instant.", 500);
    }
  }
};
