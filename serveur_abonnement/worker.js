// Radar Bourse+ : serveur d'abonnement (Cloudflare Worker). Généré par bourse_bot/abonnement.py — ne pas modifier à la main.
// Réglages dans Cloudflare (Settings > Variables and Secrets) :
//   STRIPE_SECRET (Secret) : clé secrète Stripe (sk_test_… pour tester, sk_live_… ensuite)
//   CODE_SECRET   (Secret) : une longue phrase au hasard (sert à signer les codes d'accès)
//   STRIPE_PRICE  (Text)   : identifiant du prix à 2 €/mois (price_…)
//   SITE          (Text)   : https://radarbourse.fr
//   Analyse approfondie (facultatif) : QUOTAS (liaison KV), GITHUB_REPO (Text, ex. pseudo/radar-bourse),
//   GITHUB_TOKEN (Secret : jeton GitHub limité à ce dépôt, droit « Actions : lecture et écriture »), DEPOT_SECRET (Secret)
const LECONS = {"lire-un-bilan": "<h2>Les deux colonnes du bilan</h2>\n<p>Le bilan est une photo de l'entreprise à une date précise (souvent le 31 décembre). À gauche, l'<b>actif</b> : tout ce qu'elle possède ou contrôle (usines, brevets, stocks, créances sur ses clients, trésorerie). À droite, le <b>passif</b> : d'où vient l'argent qui a financé cet actif, soit des <b>fonds propres</b> (l'argent des actionnaires, apporté ou accumulé), soit des <b>dettes</b>. Les deux colonnes sont toujours égales : chaque euro possédé a été financé par quelqu'un.</p>\n<p>Pour lire vite, regroupe en quatre blocs : actif immobilisé (ce qui sert longtemps), actif circulant (stocks, créances, trésorerie), fonds propres, dettes (financières d'un côté, fournisseurs et fiscales de l'autre).</p>\n<h2>Les fonds propres et ce qu'ils racontent</h2>\n<p>Les fonds propres = actif total − toutes les dettes. Ils augmentent quand l'entreprise fait des bénéfices qu'elle garde, et baissent quand elle perd de l'argent, verse des dividendes ou rachète ses actions. Une entreprise dont les fonds propres montent régulièrement sur 5 ans crée de la valeur comptable ; s'ils baissent alors qu'elle ne verse rien, elle perd de l'argent.</p>\n<p>Attention à la <b>survaleur</b> (goodwill) : quand une entreprise en rachète une autre plus cher que sa valeur comptable, la différence est inscrite à l'actif. Si le goodwill représente une grosse part des fonds propres, une seule dépréciation peut les faire fondre.</p>\n<h2>La dette nette, le vrai chiffre de l'endettement</h2>\n<p><b>Dette nette = dettes financières − trésorerie.</b> Une entreprise avec 10 Md€ de dettes et 9 Md€ de trésorerie est bien moins fragile qu'une autre avec 3 Md€ de dettes et rien en caisse. On la compare ensuite à ce que l'entreprise gagne : <b>dette nette / EBITDA</b> (l'EBITDA est le résultat avant intérêts, impôts et amortissements, une mesure de la trésorerie produite par l'activité). En dessous de 2, c'est confortable ; au-dessus de 4, la moindre baisse d'activité devient dangereuse (les banques et les agences de notation regardent ce ratio en premier).</p>\n<h2>Le besoin en fonds de roulement (BFR)</h2>\n<p>BFR = stocks + créances clients − dettes fournisseurs. C'est l'argent immobilisé par le cycle d'exploitation. Un supermarché a souvent un BFR <b>négatif</b> : il vend comptant et paie ses fournisseurs à 60 jours, ce qui lui donne de la trésorerie gratuite. Un fabricant d'avions a un BFR énorme : il construit pendant des mois avant d'être payé. Un BFR qui grossit plus vite que le chiffre d'affaires est un signal à surveiller (stocks qui s'accumulent, clients qui paient de plus en plus tard).</p>\n<h2>Les cinq signaux d'alerte</h2>\n<ol><li>Fonds propres qui baissent plusieurs années de suite sans dividende ni rachat d'actions.</li>\n<li>Dette nette / EBITDA au-dessus de 4, ou qui monte vite.</li>\n<li>Goodwill supérieur aux fonds propres.</li>\n<li>Créances clients qui augmentent beaucoup plus vite que les ventes.</li>\n<li>Trésorerie qui baisse alors que l'entreprise annonce des bénéfices : les bénéfices comptables ne se transforment pas en argent.</li></ol>\n<h2>Exercice corrigé : deux entreprises face à face</h2>\n<p><b>A</b> : actif 500, dettes financières 150, trésorerie 120, autres dettes 100, EBITDA 60. <b>B</b> : actif 500, dettes financières 300, trésorerie 20, autres dettes 120, EBITDA 55.</p>\n<p><b>Corrigé.</b> Fonds propres A = 500 − 150 − 100 = 250 ; B = 500 − 300 − 120 = 80. Dette nette A = 150 − 120 = 30, soit 0,5 fois l'EBITDA : très solide. Dette nette B = 300 − 20 = 280, soit 5,1 fois l'EBITDA : fragile, une année difficile peut la mettre en danger. À chiffre d'affaires égal, A a beaucoup plus de marge de manœuvre.</p>\n<p class=\"muted\">Cours éducatif : il ne constitue pas un conseil en investissement.</p>", "valoriser-dcf": "<h2>L'idée : un euro demain vaut moins qu'un euro aujourd'hui</h2>\n<p>Le DCF (discounted cash flows, « flux de trésorerie actualisés ») estime ce que vaut une entreprise en additionnant tout l'argent qu'elle produira dans le futur, ramené à sa valeur d'aujourd'hui. Pourquoi « ramené » ? Parce qu'un euro reçu dans 5 ans vaut moins qu'un euro aujourd'hui : on aurait pu le placer entre-temps, et il y a un risque de ne jamais le recevoir.</p>\n<p>Avec un taux de 8 %, 100 € reçus dans un an valent aujourd'hui 100 ÷ 1,08 = 92,6 €. Dans deux ans : 100 ÷ 1,08² = 85,7 €. C'est l'<b>actualisation</b>.</p>\n<h2>Les flux de trésorerie disponibles (free cash-flow)</h2>\n<p>Free cash-flow = trésorerie produite par l'activité − investissements nécessaires (usines, machines, logiciels). C'est l'argent qui reste vraiment, et qui pourrait être rendu aux actionnaires et aux prêteurs. On le projette en général sur 5 à 10 ans, en partant de l'historique et d'hypothèses de croissance prudentes.</p>\n<h2>Le taux d'actualisation</h2>\n<p>On utilise souvent le <b>coût moyen pondéré du capital</b> (CMPC, ou WACC en anglais) : le rendement qu'exigent ensemble les actionnaires et les prêteurs. Pour une grande entreprise stable, il tourne souvent autour de 7 à 9 % ; pour une jeune entreprise risquée, bien plus. Plus le taux est élevé, plus les flux lointains « pèsent » peu.</p>\n<h2>La valeur terminale</h2>\n<p>On ne peut pas projeter année par année jusqu'à l'infini. Après la dernière année projetée, on suppose une croissance constante g, faible (souvent 1,5 à 2,5 %, pas plus que la croissance de l'économie). Valeur terminale = flux de l'année suivante ÷ (taux − g). Elle représente souvent <b>plus de la moitié</b> de la valeur totale : c'est la partie la plus fragile du calcul.</p>\n<h2>De la valeur de l'entreprise au prix par action</h2>\n<p>La somme des flux actualisés + la valeur terminale actualisée donne la <b>valeur d'entreprise</b>. On retire la dette nette pour obtenir la valeur des fonds propres, puis on divise par le nombre d'actions. On compare ensuite au cours de Bourse.</p>\n<h2>La sensibilité : le piège du DCF</h2>\n<p>Changer le taux de 8 % à 9 %, ou la croissance terminale de 2 % à 1,5 %, peut faire varier la valeur de 20 à 30 %. Un DCF n'est donc pas un « vrai prix » : c'est un outil pour comprendre <b>quelles hypothèses</b> le marché fait déjà. Les analystes présentent toujours un tableau de sensibilité (plusieurs taux × plusieurs croissances) plutôt qu'un chiffre unique.</p>\n<h2>Exercice corrigé</h2>\n<p>Une entreprise produit 100 M€ de free cash-flow par an, sans croissance pendant 3 ans, puis +2 % par an pour toujours. Taux : 8 %. Dette nette : 200 M€. 50 millions d'actions.</p>\n<p><b>Corrigé.</b> Flux actualisés des années 1 à 3 : 100/1,08 + 100/1,08² + 100/1,08³ = 92,6 + 85,7 + 79,4 = 257,7 M€. Valeur terminale fin d'année 3 : 102 ÷ (0,08 − 0,02) = 1 700 M€, actualisée : 1 700 ÷ 1,08³ = 1 349,5 M€. Valeur d'entreprise ≈ 1 607 M€ ; moins la dette nette : 1 407 M€ ; par action : environ 28 €. Avec un taux de 9 % au lieu de 8 %, on tombe vers 24 € (−16 %) : voilà la sensibilité.</p>\n<p class=\"muted\">Cours éducatif : il ne constitue pas un conseil en investissement.</p>", "pieges-statistiques": "<h2>Le surapprentissage</h2>\n<p>Un modèle qui apprend « par cœur » le passé, y compris son bruit, paraît excellent sur les données d'entraînement et décevant sur des données nouvelles. Plus un modèle a de réglages par rapport à la quantité de données, plus le risque est grand. La seule protection fiable : juger le modèle sur des <b>années qu'il n'a jamais vues</b> (c'est ce que fait Radar Bourse, année après année).</p>\n<h2>Le biais du survivant</h2>\n<p>Si on teste une stratégie uniquement sur les entreprises qui existent encore aujourd'hui, on oublie celles qui ont fait faillite ou ont été retirées de la cote. Le passé paraît alors plus rose qu'il ne l'était. Ce biais gonfle surtout les résultats sur les petites entreprises et les cryptos (beaucoup ont disparu). Limite honnête de notre propre test : notre univers de titres est celui d'aujourd'hui, donc nos résultats historiques en sont un peu affectés ; c'est une des raisons pour lesquelles nous publions les résultats en conditions réelles.</p>\n<h2>La fuite de données</h2>\n<p>C'est utiliser, sans s'en rendre compte, une information qui n'était pas encore connue à la date de la prévision : une moyenne calculée en incluant les jours suivants, des résultats financiers publiés des semaines après la date de clôture, des chiffres économiques révisés après coup. Le modèle semble alors « deviner » le futur. Règle : chaque donnée doit être datée du jour où elle était réellement disponible.</p>\n<h2>Les tests multiples : le gagnant par hasard</h2>\n<p>Teste 100 stratégies sans aucune valeur : par pur hasard, quelques-unes auront l'air brillantes. Choisir la meilleure après coup, c'est choisir un coup de chance. Remèdes : fixer l'hypothèse avant le test, compter combien d'essais ont été faits, et confirmer sur une période jamais utilisée pour choisir. C'est pour cela que Radar Bourse n'adopte un changement que s'il ne dégrade aucune année de test.</p>\n<h2>Les prévisions qui se chevauchent</h2>\n<p>Une prévision à un mois faite chaque jour : celle du lundi et celle du mardi partagent 19 jours sur 20. Elles ne sont pas indépendantes. 1 000 prévisions qui se chevauchent valent beaucoup moins que 1 000 expériences séparées : les marges d'erreur calculées naïvement sont trop étroites. Même chose quand 100 actions montent ensemble parce que tout le marché monte.</p>\n<h2>Backtest contre conditions réelles</h2>\n<p>Un backtest (test sur le passé), même propre, reste une simulation. Les conditions réelles ajoutent les frais, les cours qui sautent à l'ouverture, les marchés qui changent de comportement. C'est pourquoi un site sérieux montre les deux et explique l'écart : sur Radar Bourse, la fourchette « 8 fois sur 10 » tenait environ 81 fois sur 100 en test, et nettement moins en conditions réelles ; les fiches affichent les deux chiffres.</p>\n<h2>Exercice : repérer le piège</h2>\n<p>« Notre stratégie a gagné 40 % par an de 2015 à 2025, testée sur les 30 actions les plus grosses du Nasdaq aujourd'hui, après avoir essayé 200 combinaisons d'indicateurs. » Combien de pièges ?</p>\n<p><b>Corrigé.</b> Au moins deux : le <b>biais du survivant</b> (les plus grosses d'aujourd'hui sont, par définition, celles qui ont le mieux réussi) et les <b>tests multiples</b> (200 combinaisons, on garde la meilleure). Probablement aussi aucun test sur une période jamais vue. Ce chiffre ne dit presque rien de l'avenir.</p>\n<p class=\"muted\">Cours éducatif : il ne constitue pas un conseil en investissement.</p>"};
const ESSAI = 30;
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
