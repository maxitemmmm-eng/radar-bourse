"""Met Radar Bourse en ligne sur GitHub Pages (et le met à jour quand tu le relances).

Double-clique sur mettre_en_ligne.bat. Il te faut seulement un compte GitHub.
Le script :
  1. vérifie Python, installe Git et l'outil GitHub s'ils manquent (sans redémarrage) ;
  2. te connecte à GitHub ;
  3. teste le site sur ton PC avant d'envoyer quoi que ce soit ;
  4. crée le dépôt (ou met à jour celui qui existe déjà), active l'hébergement ;
  5. suit la mise en ligne, vérifie que le site répond et l'ouvre.

Tes réponses sont mémorisées dans .radar_deploy.json : la prochaine fois, il ne repose pas les questions.
Option : --simulation affiche ce qui serait fait sans rien exécuter.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

for flux in (sys.stdout, sys.stderr):
    try:
        flux.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
SIMULATION = "--simulation" in sys.argv
WINDOWS = os.name == "nt"
MEMOIRE = os.path.join(ICI, ".radar_deploy.json")
JOURNAL = os.path.join(ICI, "erreur_mise_en_ligne.txt")
GIT, GH = "git", "gh"
ETAPES = 10


# ----------------------------------------------------------------------------
# Affichage et utilitaires
# ----------------------------------------------------------------------------
MEMOIRE_DOMAINE = [""]


def etape(n, texte):
    print(f"\n[{n}/{ETAPES}] {texte}")


def ok(texte):
    print(f"   ✅ {texte}")


def info(texte):
    print(f"   {texte}")


def fermer(code=0):
    if WINDOWS and not SIMULATION:
        input("\nAppuie sur Entrée pour fermer cette fenêtre…")
    sys.exit(code)


def stop(msg, details=""):
    print(f"\n❌ {msg}")
    if details:
        with open(JOURNAL, "w", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M}\n{msg}\n\n{details}\n")
        print(f"   Les détails sont dans « {os.path.basename(JOURNAL)} » : envoie ce fichier ou une capture si tu as besoin d'aide.")
    fermer(1)


def run(cmd, ok_codes=(0,), capture=True, entree=None, montrer=True):
    """Exécute une commande. Renvoie (code, sortie)."""
    if montrer:
        print("   › " + " ".join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd)))
    if SIMULATION:
        return 0, ""
    try:
        r = subprocess.run(cmd, cwd=ICI, text=True, input=entree, encoding="utf-8", errors="replace",
                           capture_output=capture)
    except FileNotFoundError:
        stop(f"Programme introuvable : {cmd[0]}")
    sortie = ((r.stdout or "") + (r.stderr or "")).strip() if capture else ""
    if r.returncode not in ok_codes:
        stop("Une commande a échoué.", f"Commande : {' '.join(cmd)}\nCode : {r.returncode}\n\n{sortie}")
    return r.returncode, sortie


def silencieux(cmd):
    if SIMULATION:
        return 1, ""
    r = subprocess.run(cmd, cwd=ICI, text=True, capture_output=True, encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def question(texte, defaut=""):
    if SIMULATION:
        print(f"   {texte} → {defaut or '(vide)'}")
        return defaut
    rep = input(f"   {texte}{f' [{defaut}]' if defaut else ''} : ").strip()
    return rep or defaut


def oui(texte, defaut=True):
    rep = question(f"{texte} (o/n)", "o" if defaut else "n").lower()
    return rep.startswith(("o", "y"))


def charger_memoire() -> dict:
    try:
        return json.load(open(MEMOIRE, encoding="utf-8"))
    except Exception:
        return {}


def sauver_memoire(m: dict):
    if not SIMULATION:
        json.dump(m, open(MEMOIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------------
# 1. Outils
# ----------------------------------------------------------------------------
EMPLACEMENTS = {
    "git": [r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files (x86)\Git\cmd\git.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe")],
    "gh": [r"C:\Program Files\GitHub CLI\gh.exe", r"C:\Program Files (x86)\GitHub CLI\gh.exe",
           os.path.expandvars(r"%LOCALAPPDATA%\Programs\GitHub CLI\gh.exe")],
}


def trouver(nom):
    chemin = shutil.which(nom)
    if chemin:
        return chemin
    for c in EMPLACEMENTS.get(nom, []) if WINDOWS else []:
        if os.path.exists(c):
            return c
    return None


def outils():
    global GIT, GH
    etape(1, "Vérification des outils")
    if sys.version_info < (3, 10):
        stop(f"Python {sys.version.split()[0]} est trop ancien. Installe Python 3.10 ou plus récent depuis python.org.")
    if SIMULATION:
        ok("Python, Git et l'outil GitHub sont prêts.")
        return
    manquants = [n for n in ("git", "gh") if not trouver(n)]
    if manquants:
        noms = {"git": "Git", "gh": "l'outil GitHub (GitHub CLI)"}
        info("Il manque : " + " et ".join(noms[n] for n in manquants) + ".")
        if not (WINDOWS and shutil.which("winget")):
            stop("Installe Git (https://git-scm.com) et GitHub CLI (https://cli.github.com), puis relance ce script.")
        if not oui("Je les installe maintenant ?"):
            fermer(1)
        ids = {"git": "Git.Git", "gh": "GitHub.cli"}
        for n in manquants:
            info(f"Installation de {noms[n]} (1 à 3 minutes, une fenêtre de Windows peut demander ton accord)…")
            run(["winget", "install", "--id", ids[n], "-e", "--silent",
                 "--accept-package-agreements", "--accept-source-agreements"],
                ok_codes=(0, -1978335189, 2316632107), capture=False)
        manquants = [n for n in ("git", "gh") if not trouver(n)]
        if manquants:
            stop("L'installation semble terminée, mais Windows ne trouve pas encore les outils. "
                 "Redémarre ton PC puis relance mettre_en_ligne.bat.")
    GIT, GH = trouver("git"), trouver("gh")
    ok("Python, Git et l'outil GitHub sont prêts.")


# ----------------------------------------------------------------------------
# 2. Connexion GitHub
# ----------------------------------------------------------------------------
def connexion(m) -> str:
    etape(2, "Connexion à GitHub")
    if SIMULATION:
        ok("Connectée en tant que ton-pseudo")
        return m.get("login", "ton-pseudo")
    code, sortie = silencieux([GH, "auth", "status", "-h", "github.com"])
    if code != 0:
        info("Comment ça se passe :")
        info("  1. Appuie sur Entrée quand on te le demande : ton navigateur s'ouvre.")
        info("  2. Le code est déjà copié : dans la page GitHub, fais Ctrl+V (ou recopie-le).")
        info("  3. Clique « Continue » puis « Authorize », et reviens ici.")
        info("⚠️  N'appuie jamais sur Ctrl+C dans cette fenêtre : ça arrête le script.")
        run([GH, "auth", "login", "-h", "github.com", "-p", "https", "-w", "-s", "workflow"], capture=False)
    elif "workflow" not in sortie:
        info("Il faut accorder un droit en plus à l'outil GitHub (pour la mise à jour automatique).")
        info("Ton navigateur va s'ouvrir : colle le code avec Ctrl+V et valide.")
        run([GH, "auth", "refresh", "-h", "github.com", "-s", "workflow"], capture=False)
    run([GH, "auth", "setup-git"], montrer=False)
    _, login = run([GH, "api", "user", "--jq", ".login"], montrer=False)
    if not login:
        stop("Impossible de lire ton nom d'utilisateur GitHub.")
    ok(f"Connectée en tant que {login}")
    return login


# ----------------------------------------------------------------------------
# 3. Mentions légales
# ----------------------------------------------------------------------------
def mentions(m, login):
    etape(3, "Mentions légales (affichées sur le site)")
    chemin = os.path.join(ICI, "bourse_bot", "config.py")
    texte = open(chemin, encoding="utf-8").read()
    actuel_nom = re.search(r'RADAR_EDITEUR", "([^"]*)"', texte).group(1)

    nom = m.get("editeur") or (actuel_nom if not actuel_nom.startswith("[") and "@" not in actuel_nom else login)
    mail = m.get("contact") or ""
    lien_github = f"https://github.com/{login}/{m.get('depot', 'radar-bourse')}/issues"
    if not (m.get("editeur") and m.get("contact")):
        info("Le site doit indiquer qui l'édite et comment le contacter. Un pseudo suffit.")
        while True:
            nom = question("Pseudo affiché (pas ton e-mail)", nom)
            if nom and "@" not in nom:
                break
            info("Mets un pseudo, sans @ (par exemple ton nom GitHub).")
        info("Contact : tu peux donner un e-mail, OU appuyer juste sur Entrée pour que les visiteurs")
        info("te contactent via la page GitHub du projet (aucun e-mail ni téléphone affiché).")
        while True:
            mail = question("E-mail de contact (ou Entrée = contact via GitHub)", "")
            if not mail:
                mail = lien_github
                break
            if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
                break
            info("Adresse e-mail invalide. Réessaie, ou appuie juste sur Entrée pour passer par GitHub.")
        m["editeur"], m["contact"] = nom, mail
        sauver_memoire(m)
    propre = lambda v: v.replace("\\", "").replace('"', "'")
    texte = re.sub(r'(RADAR_EDITEUR", ")[^"]*(")', lambda x: x.group(1) + propre(nom) + x.group(2), texte)
    texte = re.sub(r'(RADAR_CONTACT", ")[^"]*(")', lambda x: x.group(1) + propre(mail) + x.group(2), texte)
    if not SIMULATION:
        open(chemin, "w", encoding="utf-8").write(texte)
    ok(f"Éditeur : {nom} · contact : {mail}")


# ----------------------------------------------------------------------------
# 4. Test local
# ----------------------------------------------------------------------------
def test_local():
    etape(4, "Test du site sur ton PC (données de démo, 20 secondes)")
    if not SIMULATION:
        silencieux([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check",
                    "-r", "requirements.txt"])
    code, sortie = run([sys.executable, "-m", "bourse_bot", "--demo", "--sans-ml", "--pas-de-navigateur",
                        "site", "--marches", "crypto", "etf"], ok_codes=(0, 1, 2), montrer=False)
    if code != 0:
        stop("Le site ne se génère pas correctement sur ton PC : je n'envoie rien.", sortie)
    ok("Le site se génère sans erreur.")


# ----------------------------------------------------------------------------
# 5-6. Dépôt et envoi
# ----------------------------------------------------------------------------
def depot(m, login) -> str:
    etape(5, "Dépôt GitHub et hébergement")
    nom = m.get("depot") or question("Nom du dépôt (Entrée pour garder)", "radar-bourse")
    nom = re.sub(r"[^A-Za-z0-9._-]", "-", nom).strip("-") or "radar-bourse"
    m["depot"], m["login"] = nom, login
    sauver_memoire(m)
    complet = f"{login}/{nom}"
    existe, _ = silencieux([GH, "repo", "view", complet])
    if existe == 0 and not SIMULATION:
        ok(f"Le dépôt {complet} existe déjà : je le mets à jour.")
    else:
        run([GH, "repo", "create", complet, "--public",
             "--description", "Radar Bourse : analyse et prévisions boursières éducatives"])
        ok(f"Dépôt créé : https://github.com/{complet}")
    # GitHub Pages en mode « GitHub Actions » (avant l'envoi, pour que la 1re publication passe)
    for essai in range(4):
        c, _ = silencieux([GH, "api", "-X", "POST", f"repos/{complet}/pages", "-f", "build_type=workflow"])
        if c != 0:
            c, _ = silencieux([GH, "api", "-X", "PUT", f"repos/{complet}/pages", "-f", "build_type=workflow"])
        if c == 0 or SIMULATION:
            break
        time.sleep(3)
    else:
        info("⚠️ Je n'ai pas pu activer l'hébergement automatiquement. Fais-le à la main : "
             "Settings → Pages → Source : GitHub Actions.")
    ok("Hébergement GitHub Pages activé.")
    return complet


def envoyer(complet):
    etape(6, "Envoi des fichiers")
    distant = f"https://github.com/{complet}.git"
    if not os.path.isdir(os.path.join(ICI, ".git")):
        run([GIT, "init", "-q"], montrer=False)
    run([GIT, "symbolic-ref", "HEAD", "refs/heads/main"], montrer=False, ok_codes=(0, 1, 128))
    if not SIMULATION:
        _, uid = run([GH, "api", "user", "--jq", ".id"], montrer=False)
        _, login = run([GH, "api", "user", "--jq", ".login"], montrer=False)
        run([GIT, "config", "user.name", login], montrer=False)
        run([GIT, "config", "user.email", f"{uid}+{login}@users.noreply.github.com"], montrer=False)
        run([GIT, "config", "core.autocrlf", "false"], montrer=False)
    code, _ = silencieux([GIT, "remote", "get-url", "origin"])
    run([GIT, "remote", "set-url" if code == 0 else "add", "origin", distant], montrer=False)

    # Récupère ce qui est déjà en ligne (dont l'historique des prédictions écrit par le robot)
    silencieux([GIT, "fetch", "-q", "origin"])
    distant_existe = silencieux([GIT, "rev-parse", "--verify", "-q", "origin/main"])[0] == 0
    local_existe = silencieux([GIT, "rev-parse", "--verify", "-q", "HEAD"])[0] == 0
    if distant_existe and not local_existe:
        run([GIT, "reset", "-q", "--mixed", "origin/main"], montrer=False)
    if distant_existe:
        # On récupère l'historique écrit par le robot en ligne, SANS perdre ce que l'IA a appris sur ce PC :
        # les connaissances locales (recette, mémoire des essais) sont fusionnées avec la version en ligne.
        from bourse_bot import savoir
        local = savoir.lire(os.path.join(ICI, "historique"))
        silencieux([GIT, "checkout", "origin/main", "--", "historique"])
        distant = savoir.lire(os.path.join(ICI, "historique"))
        savoir.ecrire(savoir.fusionner(local, distant), os.path.join(ICI, "historique"))
        if any(local.values()):
            ok("Connaissances de l'IA gardées (recette, mémoire des essais) et fusionnées avec la version en ligne.")

    run([GIT, "add", "-A"], montrer=False)
    code, _ = run([GIT, "commit", "-q", "-m", f"Mise à jour du site ({datetime.now():%d/%m/%Y %H:%M})"],
                  ok_codes=(0, 1), montrer=False)
    nouveau = code == 0
    if os.path.isdir(os.path.join(ICI, ".git", "rebase-merge")) or os.path.isdir(os.path.join(ICI, ".git", "rebase-apply")):
        silencieux([GIT, "rebase", "--abort"])   # une ancienne mise à jour interrompue ne doit pas tout bloquer
    if distant_existe and local_existe:
        c, _ = run([GIT, "pull", "-q", "--rebase", "-X", "theirs", "origin", "main"], ok_codes=(0, 1, 128), montrer=False)
        if c != 0:
            silencieux([GIT, "rebase", "--abort"])
            run([GIT, "pull", "-q", "--no-rebase", "-X", "ours", "origin", "main"], ok_codes=(0, 1), montrer=False)
    info("Envoi en cours…")
    run([GIT, "push", "-q", "-u", "origin", "main"], montrer=False)
    ok("Fichiers envoyés." if nouveau else "Rien de nouveau à envoyer : je relance juste une mise à jour.")
    return nouveau


# ----------------------------------------------------------------------------
# 7. Clé Finnhub (optionnelle)
# ----------------------------------------------------------------------------
def finnhub(m, complet):
    etape(7, "Actions US en direct (optionnel)")
    if m.get("finnhub_demande"):
        ok("Déjà réglé lors d'un passage précédent.")
        return
    info("Avec une clé gratuite Finnhub, les actions américaines bougent en direct sur ton site.")
    if oui("Tu veux l'ajouter maintenant ?", defaut=False):
        info("1. Crée un compte sur https://finnhub.io  2. Copie ta « API key »")
        info("3. Colle-la ici avec un clic droit (ou Ctrl+V), puis Entrée.")
        cle = question("Clé Finnhub").strip()
        if cle:
            run([GH, "secret", "set", "FINNHUB_KEY", "-R", complet], entree=cle, montrer=False)
            ok("Clé enregistrée. Elle sera active à la prochaine mise à jour.")
    else:
        info("Passé. Relance ce script plus tard pour l'ajouter.")
    m["finnhub_demande"] = True
    sauver_memoire(m)


# ----------------------------------------------------------------------------
# 8. Alertes Telegram (optionnel)
# ----------------------------------------------------------------------------
def telegram(m, complet):
    etape(8, "Alertes Telegram (optionnel)")
    if m.get("telegram_demande") and "--telegram" not in sys.argv:
        ok("Déjà réglé lors d'un passage précédent.")
        return
    info("Chaque soir, le robot peut publier les signaux forts sur une chaîne Telegram que les")
    info("visiteurs suivent. Ton identité n'apparaît pas : seul le nom de la chaîne est public.")
    if not oui("Tu veux le configurer maintenant ?", defaut=False):
        info("Passé. Pour l'ajouter plus tard : double-clique sur alertes_telegram.bat.")
        m["telegram_demande"] = True
        sauver_memoire(m)
        return
    info("1. Dans Telegram, ouvre @BotFather, envoie /newbot et suis les questions.")
    info("   Il te donne un « token » qui ressemble à 123456789:ABCdef… : copie-le.")
    jeton = question("Colle le token du bot (clic droit pour coller)").strip()
    info("2. Crée une chaîne PUBLIQUE (Nouvelle chaîne), choisis un lien du type t.me/radar_bourse_xxx.")
    info("3. Dans les réglages de la chaîne : Administrateurs → Ajouter → cherche ton bot → valide.")
    chaine = question("Nom de la chaîne (ce qui suit t.me/, par exemple radar_bourse_xxx)").strip().lstrip("@")
    chaine = chaine.replace("https://t.me/", "").replace("t.me/", "").strip("/")
    if not re.fullmatch(r"\d{5,}:[A-Za-z0-9_-]{20,}", jeton) or not re.fullmatch(r"[A-Za-z0-9_]{4,40}", chaine):
        info("⚠️ Le token ou le nom de la chaîne ne semble pas valide. Passé : relance le script pour réessayer.")
        return
    if not SIMULATION:
        import urllib.parse
        try:
            donnees = urllib.parse.urlencode({"chat_id": "@" + chaine, "text":
                "📡 Radar Bourse est connecté ! Les signaux du soir arriveront ici. "
                "Rappel : calculs automatiques, rien n'est sûr, pas un conseil en investissement."}).encode()
            with urllib.request.urlopen(urllib.request.Request(
                    f"https://api.telegram.org/bot{jeton}/sendMessage", data=donnees), timeout=15) as r:
                bon = json.load(r).get("ok", False)
        except Exception:
            bon = False
        if not bon:
            info("⚠️ Le message de test n'est pas passé. Vérifie que le bot est bien administrateur de la")
            info("   chaîne et que la chaîne est publique, puis relance le script.")
            return
        run([GH, "secret", "set", "TELEGRAM_TOKEN", "-R", complet], entree=jeton, montrer=False)
        run([GH, "secret", "set", "TELEGRAM_CHAT", "-R", complet], entree="@" + chaine, montrer=False)
        run([GH, "variable", "set", "TELEGRAM_CHAINE", "-R", complet, "--body", chaine], montrer=False)
    ok(f"Alertes activées : un message de test vient d'arriver sur t.me/{chaine}")
    m["telegram_demande"] = True
    sauver_memoire(m)


# ----------------------------------------------------------------------------
# 9. Statistiques de visites privées (optionnel)
# ----------------------------------------------------------------------------
def statistiques(m, complet):
    etape(9, "Statistiques de visites, visibles par toi seule (optionnel)")
    if m.get("stats_demande") and "--stats" not in sys.argv:
        if m.get("stats_code"):
            ok(f"Déjà configurées : https://{m['stats_code']}.goatcounter.com")
        else:
            ok("Déjà réglé lors d'un passage précédent.")
        return
    info("GoatCounter compte les visiteurs sans cookie et sans les pister. Ton tableau de bord")
    info("est privé : toi seule le vois. Ton nom n'apparaît nulle part sur le site.")
    if not oui("Tu veux l'activer maintenant ?", defaut=True):
        info("Passé. Pour l'activer plus tard : double-clique sur statistiques.bat.")
        m["stats_demande"] = True
        sauver_memoire(m)
        return
    info("1. Va sur https://www.goatcounter.com/signup (gratuit, sans carte bancaire).")
    info("2. Choisis un « Code » (par exemple radarbourse123) : ton tableau de bord sera")
    info("   https://CODE.goatcounter.com. Mets ton e-mail et un mot de passe, valide.")
    if not SIMULATION and WINDOWS:
        try:
            os.startfile("https://www.goatcounter.com/signup")
        except Exception:
            pass
    code = question("Le code que tu as choisi").strip().lower()
    code = code.replace("https://", "").replace(".goatcounter.com", "").strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,48}", code):
        info("⚠️ Ce code ne semble pas valide. Passé : double-clique sur statistiques.bat pour réessayer.")
        return
    run([GH, "variable", "set", "GOATCOUNTER_CODE", "-R", complet, "--body", code], montrer=False)
    if not SIMULATION:
        with open(os.path.join(ICI, "Mes statistiques de visites.url"), "w", encoding="utf-8") as f:
            f.write(f"[InternetShortcut]\nURL=https://{code}.goatcounter.com\n")
    ok(f"Statistiques activées. Tableau de bord privé : https://{code}.goatcounter.com")
    ok("Raccourci créé dans ce dossier : « Mes statistiques de visites ».")
    m["stats_demande"], m["stats_code"] = True, code
    sauver_memoire(m)


# ----------------------------------------------------------------------------
# Google Search Console (seulement avec google.bat)
# ----------------------------------------------------------------------------
def google(m, complet, login):
    if "--google" not in sys.argv:
        if m.get("google"):
            ok("Google Search Console : site vérifié.")
        return
    adresse = f"https://{m['domaine']}/" if m.get("domaine") else f"https://{login.lower()}.github.io/{complet.split('/')[1]}/"
    print("\n🔎 Inscrire le site sur Google (gratuit, 5 minutes)")
    info("1. Va sur https://search.google.com/search-console (connecte-toi avec un compte Google).")
    info("2. Clique « Ajouter une propriété », choisis « Préfixe de l'URL » et colle :")
    info(f"      {adresse}")
    info("3. Méthode de validation : « Balise HTML ». Google affiche une ligne comme :")
    info('      <meta name="google-site-verification" content="AbC123...xyz" />')
    info("   Copie seulement ce qu'il y a entre les guillemets après content= (ou toute la ligne, ça marche aussi).")
    info("   Ne clique PAS encore sur « Valider ».")
    if not SIMULATION and WINDOWS:
        try:
            os.startfile("https://search.google.com/search-console")
        except Exception:
            pass
    code = question("Colle le code ici").strip()
    trouve = re.search(r'content="([^"]+)"', code)
    code = (trouve.group(1) if trouve else code).strip().strip('"')
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,100}", code):
        info("⚠️ Ce code ne semble pas valide. Relance google.bat pour réessayer.")
        return
    run([GH, "variable", "set", "GOOGLE_SITE_VERIFICATION", "-R", complet, "--body", code], montrer=False)
    m["google"] = code
    sauver_memoire(m)
    ok("Code enregistré. Le site va être republié avec ce code (3 à 6 minutes).")
    info("4. Quand la publication est finie, retourne sur Search Console et clique « Valider ».")
    info("5. Puis menu de gauche « Sitemaps » : tape  sitemap.xml  et clique « Envoyer ».")
    info(f"   (adresse complète : {adresse}sitemap.xml)")


# ----------------------------------------------------------------------------
# Nom de domaine personnalisé (seulement avec nom_de_domaine.bat)
# ----------------------------------------------------------------------------
def domaine(m, complet):
    if "--domaine" not in sys.argv:
        if m.get("domaine"):
            ok(f"Nom de domaine : {m['domaine']}")
        return
    print("\n🌍 Nom de domaine personnalisé (facultatif, environ 7 à 12 € par an)")
    info("1. Achète un nom (ex : radarbourse.fr) chez OVH, Gandi, Namecheap ou Cloudflare.")
    info("   Conseil anti-dox : active la « protection WHOIS » (souvent gratuite) pour que ton")
    info("   nom n'apparaisse pas dans l'annuaire public des domaines.")
    info("2. Dans la zone DNS de ton domaine, ajoute ces 4 enregistrements de type A :")
    for ip in ("185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"):
        info(f"      A   @   {ip}")
    info(f"   et un enregistrement CNAME :  www   {complet.split('/')[0].lower()}.github.io")
    nom = question("3. Ton nom de domaine (vide pour annuler, « aucun » pour le retirer)").strip().lower()
    nom = nom.replace("https://", "").replace("http://", "").strip("/")
    if not nom:
        info("Annulé.")
        return
    if nom == "aucun":
        silencieux([GH, "api", "-X", "PUT", f"repos/{complet}/pages", "-F", "cname="])
        silencieux([GH, "variable", "delete", "RADAR_DOMAINE", "-R", complet])
        m.pop("domaine", None)
        sauver_memoire(m)
        ok("Nom de domaine retiré : le site reprend son adresse github.io.")
        return
    if not re.fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+", nom):
        info("⚠️ Ce nom ne semble pas valide (exemple attendu : radarbourse.fr). Relance nom_de_domaine.bat.")
        return
    run([GH, "variable", "set", "RADAR_DOMAINE", "-R", complet, "--body", nom], montrer=False)
    code, sortie = silencieux([GH, "api", "-X", "PUT", f"repos/{complet}/pages", "-f", f"cname={nom}"])
    if code != 0:
        info("⚠️ GitHub n'a pas accepté le domaine tout de suite (souvent parce que le DNS n'est pas encore")
        info(f"   propagé). Tu peux aussi le saisir dans https://github.com/{complet}/settings/pages")
    else:
        ok(f"Domaine {nom} enregistré. Le DNS peut mettre jusqu'à 24 h à fonctionner.")
        info(f"Ensuite, coche « Enforce HTTPS » dans https://github.com/{complet}/settings/pages")
    m["domaine"] = nom
    sauver_memoire(m)


# ----------------------------------------------------------------------------
# 10. Publication et vérification
# ----------------------------------------------------------------------------
def dernier_run(complet, depuis):
    code, sortie = silencieux([GH, "run", "list", "-R", complet, "-w", "radar.yml", "-L", "5",
                               "--json", "databaseId,createdAt,status,conclusion"])
    if code != 0 or not sortie:
        return None
    try:
        runs = json.loads(sortie)
    except ValueError:
        return None
    recents = [r for r in runs if r["createdAt"] >= depuis]
    return recents[0] if recents else None


def publier(complet, login):
    etape(10, "Publication (3 à 6 minutes)")
    depuis = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if SIMULATION:
        run([GH, "workflow", "run", "radar.yml", "-R", complet])
        return f"https://{login.lower()}.github.io/{complet.split('/')[1]}/"
    time.sleep(5)
    r = None
    for _ in range(8):  # l'envoi déclenche normalement la mise à jour tout seul
        r = dernier_run(complet, depuis)
        if r:
            break
        time.sleep(5)
    if not r:
        for _ in range(6):
            if silencieux([GH, "workflow", "run", "radar.yml", "-R", complet])[0] == 0:
                break
            time.sleep(5)
        for _ in range(12):
            r = dernier_run(complet, depuis)
            if r:
                break
            time.sleep(5)
    if not r:
        stop("La mise à jour automatique ne démarre pas. Ouvre https://github.com/"
             f"{complet}/actions, active les workflows si GitHub le demande, puis relance ce script.")

    info("Le robot GitHub télécharge les cours, entraîne le modèle et construit le site.")
    info("Tu peux suivre ici (ne ferme pas la fenêtre) :")
    rid = str(r["databaseId"])
    code = subprocess.run([GH, "run", "watch", rid, "-R", complet, "--exit-status", "-i", "15"],
                          cwd=ICI).returncode
    if code != 0:
        _, logs = silencieux([GH, "run", "view", rid, "-R", complet, "--log-failed"])
        stop("La mise à jour en ligne a échoué.", logs[-15000:])
    ok("Mise à jour terminée.")

    url = f"https://{login.lower()}.github.io/{complet.split('/')[1]}/"
    if MEMOIRE_DOMAINE[0]:
        url = f"https://{MEMOIRE_DOMAINE[0]}/"
    info("Vérification que le site répond…")
    for _ in range(24):  # jusqu'à 2 minutes : GitHub met parfois un peu de temps à servir la page
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control": "no-cache"}),
                                        timeout=10) as rep:
                if rep.status == 200:
                    ok("Le site répond.")
                    break
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(5)
    else:
        info("⚠️ Le site ne répond pas encore. Attends 2-3 minutes puis ouvre le lien.")
    return url


def main():
    print("🚀 Mise en ligne de Radar Bourse" + ("  (SIMULATION)" if SIMULATION else ""))
    print("   ⚠️ Pendant tout le script : n'appuie jamais sur Ctrl+C (ça l'arrête). Réponds puis Entrée.")
    if not os.path.isdir(os.path.join(ICI, "bourse_bot")):
        stop("Lance ce script depuis le dossier Radar Bourse dézippé.")
    m = charger_memoire()
    outils()
    login = connexion(m)
    mentions(m, login)
    test_local()
    complet = depot(m, login)
    envoyer(complet)
    finnhub(m, complet)
    telegram(m, complet)
    statistiques(m, complet)
    domaine(m, complet)
    google(m, complet, login)
    MEMOIRE_DOMAINE[0] = m.get("domaine", "")
    url = publier(complet, login)

    if not SIMULATION:
        with open(os.path.join(ICI, "Mon site Radar Bourse.url"), "w", encoding="utf-8") as f:
            f.write(f"[InternetShortcut]\nURL={url}\n")
        if os.path.exists(JOURNAL):
            os.remove(JOURNAL)
    print("\n" + "━" * 60)
    print(f"🎉 Ton site est en ligne : {url}")
    print("   • Il se met à jour tout seul chaque heure en semaine.")
    print("   • Les cryptos bougent en direct quand la page est ouverte.")
    print("   • Raccourci créé dans ce dossier : « Mon site Radar Bourse ».")
    print("   • Nouvelle version reçue en zip : double-clique sur mettre_a_jour.bat (sans dézipper).")
    print("━" * 60)
    if WINDOWS and not SIMULATION:
        try:
            os.startfile(url)
        except Exception:
            pass
    fermer(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nArrêté (Ctrl+C). Relance mettre_en_ligne.bat pour reprendre : tes réponses sont gardées.")
        fermer(1)
