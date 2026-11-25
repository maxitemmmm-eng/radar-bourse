"""Installe Radar Bourse+ (abonnement 2 €/mois, 1 mois offert) et l'analyse approfondie à la demande, en une fois.

Ce que fait ce script, sur TON ordinateur, avec les clés que TU tapes (elles ne sont jamais enregistrées sur le disque) :
  1. Stripe     : crée (ou retrouve) le produit « Radar Bourse+ » à 2 €/mois et active la résiliation en ligne.
  2. Cloudflare : crée la mémoire des quotas, installe le serveur radar-plus et y range les clés secrètes.
  3. GitHub     : règle les variables du site (adresse du serveur, identité du vendeur) et le secret de l'analyse.

Avant de le lancer, il te faut (voir TUTO_ABONNEMENT.md pour les détails) :
  - un compte Stripe (commence en mode test : clé sk_test_…), avec ton IBAN tapé dans Stripe ;
  - un compte Cloudflare + un « API token » (modèle « Edit Cloudflare Workers ») ; ouvre une fois Workers & Pages pour choisir ton sous-domaine ;
  - deux jetons GitHub « fine-grained » limités au dépôt du site :
      A. « installation » : droits Variables + Secrets (lecture et écriture) — tu pourras le supprimer après ;
      B. « serveur »      : droit Actions (lecture et écriture) seulement — il reste dans Cloudflare pour lancer les analyses.
Tu peux relancer le script autant de fois que tu veux (par exemple pour passer de sk_test_ à sk_live_) : il ne crée pas de doublon.
"""
from __future__ import annotations

import base64
import getpass
import json
import os
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

ICI = os.path.dirname(os.path.abspath(__file__))
NOM_WORKER = "radar-plus"
LOOKUP = "radar_bourse_plus_mensuel"
SITE_DEFAUT = "https://radarbourse.fr"
RESUME = os.path.join(ICI, "abonnement_installe.json")   # rien de secret dedans


def dire(t=""):
    print(t, flush=True)


def demander(q, defaut="", secret=False, obligatoire=True):
    while True:
        s = (getpass.getpass(f"{q} : ") if secret else input(f"{q}{f' [{defaut}]' if defaut else ''} : ")).strip() or defaut
        if s or not obligatoire:
            return s
        dire("  (obligatoire)")


# ------------------------------------------------------------------------------------------------ HTTP (remplaçable pour les tests)
def http(methode, url, entetes=None, corps=None):
    req = urllib.request.Request(url, data=corps, method=methode, headers=entetes or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode() or "{}"
            return r.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else {})
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"message": txt[:300]}


class Erreur(Exception):
    pass


def verifier(statut, rep, quoi):
    if statut >= 300:
        msg = (rep.get("error") or {}).get("message") if isinstance(rep.get("error"), dict) else None
        msg = msg or (rep.get("errors") or [{}])[0].get("message") if isinstance(rep.get("errors"), list) and rep.get("errors") else msg
        raise Erreur(f"{quoi} : refusé ({statut}) {msg or rep.get('message') or ''}".strip())
    return rep


# ------------------------------------------------------------------------------------------------ Stripe
def stripe(cle, methode, chemin, params=None):
    corps = urllib.parse.urlencode(params or {}, doseq=True).encode() if methode != "GET" else None
    url = "https://api.stripe.com/v1/" + chemin + (("?" + urllib.parse.urlencode(params, doseq=True)) if methode == "GET" and params else "")
    return http(methode, url, {"Authorization": "Bearer " + cle, "Content-Type": "application/x-www-form-urlencoded"}, corps)


def installer_stripe(cle, site):
    s, r = stripe(cle, "GET", "prices", {"lookup_keys[]": LOOKUP, "active": "true"})
    verifier(s, r, "Stripe (lecture des prix)")
    if r.get("data"):
        prix = r["data"][0]["id"]
        dire(f"  ✓ Produit déjà présent (prix {prix})")
    else:
        s, p = stripe(cle, "POST", "products", {"name": "Radar Bourse+", "description": "Cours avancés, Académie sans limite et analyses approfondies illimitées."})
        verifier(s, p, "Stripe (création du produit)")
        s, pr = stripe(cle, "POST", "prices", {"product": p["id"], "unit_amount": "200", "currency": "eur", "recurring[interval]": "month",
                                                "lookup_key": LOOKUP, "nickname": "2 € par mois"})
        prix = verifier(s, pr, "Stripe (création du prix)")["id"]
        dire(f"  ✓ Produit « Radar Bourse+ » créé à 2 €/mois (prix {prix})")
    params = {"business_profile[headline]": "Radar Bourse+ : gère ou résilie ton abonnement",
              "business_profile[terms_of_service_url]": site + "/cgv.html", "business_profile[privacy_policy_url]": site + "/cgv.html",
              "features[subscription_cancel][enabled]": "true", "features[subscription_cancel][mode]": "at_period_end",
              "features[payment_method_update][enabled]": "true", "features[invoice_history][enabled]": "true",
              "metadata[radar]": "plus"}
    s, r = stripe(cle, "GET", "billing_portal/configurations", {"limit": "100"})
    verifier(s, r, "Stripe (portail client)")
    exist = [c for c in r.get("data", []) if (c.get("metadata") or {}).get("radar") == "plus"]
    if exist:
        s, c = stripe(cle, "POST", "billing_portal/configurations/" + exist[0]["id"], params)
    else:
        s, c = stripe(cle, "POST", "billing_portal/configurations", params)
    portail = verifier(s, c, "Stripe (portail client)")["id"]
    dire("  ✓ Résiliation en un clic activée (portail client Stripe)")
    return prix, portail


# ------------------------------------------------------------------------------------------------ Cloudflare
def cf(jeton, methode, chemin, corps=None, entetes=None):
    h = {"Authorization": "Bearer " + jeton}
    if entetes:
        h.update(entetes)
    elif corps is not None:
        h["Content-Type"] = "application/json"
        corps = json.dumps(corps).encode()
    return http(methode, "https://api.cloudflare.com/client/v4/" + chemin, h, corps)


def installer_cloudflare(jeton, reglages, secrets_):
    s, r = cf(jeton, "GET", "accounts")
    comptes = verifier(s, r, "Cloudflare (compte)").get("result") or []
    if not comptes:
        raise Erreur("Cloudflare : aucun compte visible avec ce jeton (vérifie ses droits).")
    acc = comptes[0]["id"]
    s, r = cf(jeton, "GET", f"accounts/{acc}/storage/kv/namespaces?per_page=100")
    ns = [n for n in verifier(s, r, "Cloudflare (mémoire KV)").get("result", []) if n.get("title") == "radar-plus-quotas"]
    if ns:
        kv = ns[0]["id"]
    else:
        s, r = cf(jeton, "POST", f"accounts/{acc}/storage/kv/namespaces", {"title": "radar-plus-quotas"})
        kv = verifier(s, r, "Cloudflare (création de la mémoire KV)")["result"]["id"]
    dire("  ✓ Mémoire des quotas prête")
    with open(os.path.join(ICI, "serveur_abonnement", "worker.js"), "rb") as f:
        code = f.read()
    liaisons = [{"type": "kv_namespace", "name": "QUOTAS", "namespace_id": kv}] + \
               [{"type": "plain_text", "name": k, "text": v} for k, v in reglages.items() if v]
    # les secrets déjà présents sont gardés tels quels (keep_bindings), puis mis à jour un par un ci-dessous
    meta = {"main_module": "worker.js", "compatibility_date": "2026-01-01", "bindings": liaisons, "keep_bindings": ["secret_text"]}
    bord = "----radarplus" + uuid.uuid4().hex
    corps = (f"--{bord}\r\nContent-Disposition: form-data; name=\"metadata\"\r\nContent-Type: application/json\r\n\r\n{json.dumps(meta)}\r\n"
             f"--{bord}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n").encode() \
        + code + f"\r\n--{bord}--\r\n".encode()
    s, r = cf(jeton, "PUT", f"accounts/{acc}/workers/scripts/{NOM_WORKER}", corps, {"Content-Type": f"multipart/form-data; boundary={bord}"})
    verifier(s, r, "Cloudflare (installation du serveur)")
    s, r = cf(jeton, "GET", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/secrets")
    deja = {x.get("name") for x in (verifier(s, r, "Cloudflare (liste des secrets)").get("result") or [])}
    if "CODE_SECRET" in deja:
        secrets_.pop("CODE_SECRET", None)   # surtout ne pas le changer : les codes des abonnés deviendraient invalides
        dire("  (secret des codes d'accès déjà présent : conservé)")
    for nom, val in secrets_.items():
        s, r = cf(jeton, "PUT", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/secrets", {"name": nom, "text": val, "type": "secret_text"})
        verifier(s, r, f"Cloudflare (secret {nom})")
    dire("  ✓ Serveur radar-plus installé, clés secrètes rangées dans Cloudflare")
    s, r = cf(jeton, "POST", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/subdomain", {"enabled": True})
    verifier(s, r, "Cloudflare (adresse publique du serveur)")
    s, r = cf(jeton, "GET", f"accounts/{acc}/workers/subdomain")
    sous = (verifier(s, r, "Cloudflare (sous-domaine)").get("result") or {}).get("subdomain")
    if not sous:
        raise Erreur("Cloudflare : ouvre une fois « Workers & Pages » dans le tableau de bord pour choisir ton sous-domaine, puis relance.")
    url = f"https://{NOM_WORKER}.{sous}.workers.dev"
    dire(f"  ✓ Adresse du serveur : {url}")
    return url


# ------------------------------------------------------------------------------------------------ GitHub
def gh(jeton, methode, chemin, corps=None):
    h = {"Authorization": "Bearer " + jeton, "Accept": "application/vnd.github+json", "User-Agent": "radar-bourse-installeur",
         "X-GitHub-Api-Version": "2022-11-28"}
    if corps is not None:
        h["Content-Type"] = "application/json"
        corps = json.dumps(corps).encode()
    return http(methode, "https://api.github.com/" + chemin, h, corps)


def chiffrer_secret(cle_publique_b64, valeur):
    try:
        from nacl import encoding, public
    except ImportError:
        dire("  (installation du module de chiffrement PyNaCl…)")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pynacl"])
        from nacl import encoding, public
    boite = public.SealedBox(public.PublicKey(cle_publique_b64.encode(), encoding.Base64Encoder()))
    return base64.b64encode(boite.encrypt(valeur.encode())).decode()


def installer_github(jeton, depot, variables, secret_depot):
    for nom, val in variables.items():
        if not val:
            continue
        s, r = gh(jeton, "PATCH", f"repos/{depot}/actions/variables/{nom}", {"name": nom, "value": val})
        if s == 404:
            s, r = gh(jeton, "POST", f"repos/{depot}/actions/variables", {"name": nom, "value": val})
        verifier(s, r, f"GitHub (variable {nom})")
    dire(f"  ✓ {sum(1 for v in variables.values() if v)} réglages du site enregistrés sur GitHub")
    s, r = gh(jeton, "GET", f"repos/{depot}/actions/secrets/public-key")
    k = verifier(s, r, "GitHub (clé de chiffrement)")
    s, r = gh(jeton, "PUT", f"repos/{depot}/actions/secrets/DEPOT_SECRET", {"encrypted_value": chiffrer_secret(k["key"], secret_depot), "key_id": k["key_id"]})
    verifier(s, r, "GitHub (secret de l'analyse)")
    dire("  ✓ Secret de l'analyse approfondie enregistré (chiffré)")


def depot_git():
    try:
        url = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=ICI, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        try:
            m = json.load(open(os.path.join(ICI, ".radar_deploy.json"), encoding="utf-8"))
            return f"{m['login']}/{m.get('depot', 'radar-bourse')}"
        except Exception:
            return ""
    url = url.removesuffix(".git")
    return "/".join(url.replace(":", "/").split("/")[-2:])


def main():
    dire("=" * 72)
    dire(" Installation de Radar Bourse+ et de l'analyse approfondie")
    dire("=" * 72)
    dire("Tes clés ne sont jamais écrites sur le disque ni envoyées ailleurs qu'à Stripe, Cloudflare et GitHub.")
    dire("Ne les donne à personne (Claude compris).\n")
    ancien = {}
    if os.path.exists(RESUME):
        ancien = json.load(open(RESUME, encoding="utf-8"))
    site = demander("Adresse du site", ancien.get("site", SITE_DEFAUT)).rstrip("/")
    depot = demander("Dépôt GitHub du site (pseudo/nom)", ancien.get("depot") or depot_git())
    dire("\nMode : 1 = GRATUIT (analyse approfondie pour tout le monde, sans vente ni SIRET)   2 = VENTE (abonnement, SIRET obligatoire)")
    vente = demander("Ton choix", "2" if ancien.get("mode_vente") else "1") == "2"
    vend, cle_stripe = {k: "" for k in ("VENDEUR_NOM", "VENDEUR_SIRET", "VENDEUR_ADRESSE", "VENDEUR_EMAIL")}, ""
    if vente:
        dire("\nIdentité du vendeur (obligatoire pour vendre) :")
        vend = {k: demander(f"  {lib}", ancien.get(k, "")) for k, lib in
                (("VENDEUR_NOM", "Nom et prénom"), ("VENDEUR_SIRET", "SIRET"), ("VENDEUR_ADRESSE", "Adresse (ou domiciliation)"), ("VENDEUR_EMAIL", "Email de contact"))}
    dire("\nClés (rien ne s'affiche quand tu tapes, c'est normal) :")
    if vente:
        cle_stripe = demander("  Clé secrète Stripe (sk_test_… ou sk_live_…)", secret=True)
        if not cle_stripe.startswith(("sk_test_", "sk_live_", "rk_test_", "rk_live_")):
            raise Erreur("Ce n'est pas une clé secrète Stripe (elle commence par sk_test_ ou sk_live_).")
    jeton_cf = demander("  Jeton API Cloudflare", secret=True)
    jeton_gh_install = demander("  Jeton GitHub A « installation » (Variables + Secrets)", secret=True)
    jeton_gh_serveur = demander("  Jeton GitHub B « serveur » (Actions seulement)", secret=True)
    prix = portail = ""
    if vente:
        dire("\n1/3 Stripe")
        prix, portail = installer_stripe(cle_stripe, site)
    else:
        dire("\n1/3 Stripe : rien à faire en mode gratuit")
    dire("2/3 Cloudflare")
    # CODE_SECRET n'est créé qu'une fois (s'il existe déjà dans Cloudflare, il est conservé)
    secrets_ = {"STRIPE_SECRET": cle_stripe, "GITHUB_TOKEN": jeton_gh_serveur, "DEPOT_SECRET": secrets.token_urlsafe(32),
                "CODE_SECRET": secrets.token_urlsafe(32)}
    if not vente:
        secrets_.pop("STRIPE_SECRET")
    url = installer_cloudflare(jeton_cf, {"STRIPE_PRICE": prix, "SITE": site, "GITHUB_REPO": depot, "PORTAIL_CONFIG": portail,
                                          "MODE_GRATUIT": "" if vente else "1"}, secrets_)
    dire("3/3 GitHub")
    installer_github(jeton_gh_install, depot, {"RADAR_PLUS_API": url, **vend, "RADAR_VENTE": "1" if vente else "0"}, secrets_["DEPOT_SECRET"])
    json.dump({"site": site, "depot": depot, "worker": url, "prix": prix, "mode_vente": vente, "mode": "test" if "_test_" in cle_stripe else "réel",
               **{k: v for k, v in vend.items()}}, open(RESUME, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    dire("\n✅ Terminé.")
    dire(f"   Serveur : {url}")
    dire("   Mode : " + (f"VENTE, Stripe {'TEST (aucun vrai paiement)' if '_test_' in cle_stripe else 'RÉEL'}" if vente else "GRATUIT (3 analyses par jour et par personne)"))
    dire("   Le site prendra ces réglages à sa prochaine mise à jour (dans l'heure, ou lance mettre_en_ligne.bat).")
    dire("   Tu peux maintenant supprimer le jeton GitHub A « installation » sur GitHub (il ne sert plus).")


if __name__ == "__main__":
    try:
        main()
    except Erreur as e:
        dire(f"\n❌ {e}\nRien de grave : corrige ce point et relance le script (il reprend sans doublon).")
        sys.exit(1)
    except KeyboardInterrupt:
        dire("\nArrêté.")
        sys.exit(1)
