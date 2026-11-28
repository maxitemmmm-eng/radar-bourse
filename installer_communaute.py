"""Installe la communauté Radar Bourse (comptes, commentaires modérés, discussions), en une fois. Gratuit.

Ce que fait ce script, sur TON ordinateur, avec les clés que TU tapes (elles ne sont jamais enregistrées sur le disque) :
  1. Cloudflare : crée la mémoire « radar-communaute », installe le serveur radar-communaute et y range ses clés secrètes.
  2. GitHub     : enregistre l'adresse du serveur dans la variable RADAR_COMMU_API (le site l'utilisera à sa prochaine mise à jour).
  3. Il te donne TA clé de modération (une seule fois) : elle sert sur la page moderation.html du site.

Avant de le lancer, il te faut (voir TUTO_COMMUNAUTE.md) :
  - un compte Cloudflare gratuit + un « API token » (modèle « Edit Cloudflare Workers ») ; ouvre une fois « Workers & Pages »
    dans le tableau de bord pour choisir ton sous-domaine ;
  - un jeton GitHub « fine-grained » limité au dépôt du site, avec le droit « Variables » (lecture et écriture).
Tu peux le relancer sans risque : rien n'est créé en double, les comptes et commentaires existants sont gardés.
Pour une MISE À JOUR du serveur (nouvelles fonctions), seul un jeton Cloudflare est nécessaire : le réglage GitHub est déjà fait.
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import uuid

import installer_abonnement as ia

ICI = os.path.dirname(os.path.abspath(__file__))
NOM_WORKER = "radar-communaute"
RESUME = os.path.join(ICI, "communaute_installee.json")   # rien de secret dedans


def installer_cloudflare(jeton, site, nouvelle_cle):
    s, r = ia.cf(jeton, "GET", "accounts")
    comptes = ia.verifier(s, r, "Cloudflare (compte)").get("result") or []
    if not comptes:
        raise ia.Erreur("Cloudflare : aucun compte visible avec ce jeton (vérifie ses droits).")
    acc = comptes[0]["id"]
    s, r = ia.cf(jeton, "GET", f"accounts/{acc}/storage/kv/namespaces?per_page=100")
    ns = [n for n in ia.verifier(s, r, "Cloudflare (mémoire KV)").get("result", []) if n.get("title") == "radar-communaute"]
    if ns:
        kv = ns[0]["id"]
        ia.dire("  ✓ Mémoire de la communauté retrouvée (comptes et commentaires gardés)")
    else:
        s, r = ia.cf(jeton, "POST", f"accounts/{acc}/storage/kv/namespaces", {"title": "radar-communaute"})
        kv = ia.verifier(s, r, "Cloudflare (création de la mémoire)")["result"]["id"]
        ia.dire("  ✓ Mémoire de la communauté créée")
    with open(os.path.join(ICI, "serveur_communaute", "worker.js"), "rb") as f:
        code = f.read()
    meta = {"main_module": "worker.js", "compatibility_date": "2026-01-01", "keep_bindings": ["secret_text"],
            "bindings": [{"type": "kv_namespace", "name": "COMMU", "namespace_id": kv}, {"type": "plain_text", "name": "SITE", "text": site}]}
    bord = "----radarcommu" + uuid.uuid4().hex
    corps = (f"--{bord}\r\nContent-Disposition: form-data; name=\"metadata\"\r\nContent-Type: application/json\r\n\r\n{json.dumps(meta)}\r\n"
             f"--{bord}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n").encode() \
        + code + f"\r\n--{bord}--\r\n".encode()
    s, r = ia.cf(jeton, "PUT", f"accounts/{acc}/workers/scripts/{NOM_WORKER}", corps, {"Content-Type": f"multipart/form-data; boundary={bord}"})
    ia.verifier(s, r, "Cloudflare (installation du serveur)")
    s, r = ia.cf(jeton, "GET", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/secrets")
    deja = {x.get("name") for x in (ia.verifier(s, r, "Cloudflare (liste des secrets)").get("result") or [])}
    cle = None
    a_mettre = {}
    if "SEL" not in deja:
        a_mettre["SEL"] = secrets.token_urlsafe(24)
    if "ADMIN_KEY" not in deja or nouvelle_cle:
        cle = secrets.token_urlsafe(30)
        a_mettre["ADMIN_KEY"] = cle
    for nom, val in a_mettre.items():
        s, r = ia.cf(jeton, "PUT", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/secrets", {"name": nom, "text": val, "type": "secret_text"})
        ia.verifier(s, r, f"Cloudflare (secret {nom})")
    s, r = ia.cf(jeton, "POST", f"accounts/{acc}/workers/scripts/{NOM_WORKER}/subdomain", {"enabled": True})
    ia.verifier(s, r, "Cloudflare (adresse publique du serveur)")
    s, r = ia.cf(jeton, "GET", f"accounts/{acc}/workers/subdomain")
    sous = (ia.verifier(s, r, "Cloudflare (sous-domaine)").get("result") or {}).get("subdomain")
    if not sous:
        raise ia.Erreur("Cloudflare : ouvre une fois « Workers & Pages » dans le tableau de bord pour choisir ton sous-domaine, puis relance.")
    url = f"https://{NOM_WORKER}.{sous}.workers.dev"
    ia.dire(f"  ✓ Serveur de la communauté installé : {url}")
    return url, cle


def installer_github(jeton, depot, url):
    s, r = ia.gh(jeton, "PATCH", f"repos/{depot}/actions/variables/RADAR_COMMU_API", {"name": "RADAR_COMMU_API", "value": url})
    if s == 404:
        s, r = ia.gh(jeton, "POST", f"repos/{depot}/actions/variables", {"name": "RADAR_COMMU_API", "value": url})
    ia.verifier(s, r, "GitHub (variable RADAR_COMMU_API)")
    ia.dire("  ✓ Adresse du serveur enregistrée sur GitHub (variable RADAR_COMMU_API)")


def main():
    ia.dire("=" * 72)
    ia.dire(" Installation de la communauté Radar Bourse (comptes, commentaires, discussions)")
    ia.dire("=" * 72)
    ia.dire("Tes clés ne sont jamais écrites sur le disque ni envoyées ailleurs qu'à Cloudflare et GitHub.")
    ia.dire("Ne les donne à personne (Claude compris).\n")
    ancien = json.load(open(RESUME, encoding="utf-8")) if os.path.exists(RESUME) else {}
    site = ia.demander("Adresse du site", ancien.get("site", ia.SITE_DEFAUT)).rstrip("/")
    depot = ia.demander("Dépôt GitHub du site (pseudo/nom)", ancien.get("depot") or ia.depot_git())
    nouvelle = False
    if ancien:
        nouvelle = ia.demander("Créer une NOUVELLE clé de modération (o/N) ? (si tu as perdu l'ancienne)", "n", obligatoire=False).lower().startswith("o")
    ia.dire("\nClés (rien ne s'affiche quand tu tapes, c'est normal) :")
    jeton_cf = ia.demander("  Jeton API Cloudflare", secret=True)
    deja_gh = bool(ancien.get("serveur"))
    jeton_gh = ia.demander("  Jeton GitHub (droit Variables)" + (" — déjà réglé : appuie juste sur Entrée" if deja_gh else ""),
                           secret=True, obligatoire=not deja_gh)
    ia.dire("\n1/2 Cloudflare")
    url, cle = installer_cloudflare(jeton_cf, site, nouvelle)
    ia.dire("2/2 GitHub")
    if jeton_gh:
        installer_github(jeton_gh, depot, url)
    elif ancien.get("serveur") == url:
        ia.dire("  ✓ Déjà réglé sur GitHub (rien à changer)")
    else:
        raise ia.Erreur("L'adresse du serveur a changé : relance avec un jeton GitHub (droit Variables).")
    json.dump({"site": site, "depot": depot, "serveur": url}, open(RESUME, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ia.dire("\n✅ Terminé.")
    ia.dire(f"   Serveur : {url}")
    if cle:
        fichier = os.path.join(os.path.expanduser("~"), "radar_bourse_cle_moderation.txt")   # hors du dossier du site : jamais mise en ligne
        try:
            with open(fichier, "w", encoding="utf-8") as f:
                f.write(f"Clé de modération Radar Bourse (page {site}/moderation.html) :\n{cle}\n\nNe la donne à personne.\n")
        except OSError:
            fichier = None
        ia.dire("\n   🔑 TA CLÉ DE MODÉRATION (garde-la secrète, ne la donne à personne, Claude compris) :")
        ia.dire(f"      {cle}")
        if fichier:
            ia.dire(f"      Elle est aussi enregistrée dans : {fichier}")
        ia.dire(f"      Elle sert sur {site}/moderation.html (colle-la une fois, ton navigateur s'en souvient).")
    else:
        ia.dire("   Clé de modération : inchangée (celle que tu as déjà).")
    ia.dire("   Le site affichera comptes et commentaires à sa prochaine mise à jour (dans l'heure, ou lance mettre_en_ligne.bat).")


if __name__ == "__main__":
    try:
        main()
    except ia.Erreur as e:
        ia.dire(f"\n❌ {e}\nRien de grave : corrige ce point et relance le script (il reprend sans doublon).")
        sys.exit(1)
    except KeyboardInterrupt:
        ia.dire("\nArrêté.")
        sys.exit(1)
