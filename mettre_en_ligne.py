"""Met Radar Bourse en ligne sur GitHub Pages, automatiquement.

Lance-le avec un double-clic sur mettre_en_ligne.bat (ou : python mettre_en_ligne.py).
Il te faut seulement un compte GitHub (gratuit). Le script s'occupe du reste :
installation des outils, connexion, création du dépôt, envoi des fichiers,
activation de l'hébergement et première mise à jour du site.

Option : --simulation affiche les commandes sans rien exécuter.
"""
from __future__ import annotations

import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time

for flux in (sys.stdout, sys.stderr):
    try:
        flux.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
SIMULATION = "--simulation" in sys.argv
WINDOWS = os.name == "nt"


def titre(t):
    print(f"\n━━━ {t} ━━━")


def stop(msg):
    print(f"\n❌ {msg}")
    if WINDOWS:
        input("\nAppuie sur Entrée pour fermer…")
    sys.exit(1)


def lancer(cmd, ok_codes=(0,), capture=True, entree=None):
    """Exécute une commande et renvoie (code, sortie)."""
    print("  $ " + " ".join(c if " " not in c else f'"{c}"' for c in cmd))
    if SIMULATION:
        return 0, ""
    r = subprocess.run(cmd, cwd=ICI, text=True, input=entree, encoding="utf-8", errors="replace",
                       capture_output=capture)
    sortie = ((r.stdout or "") + (r.stderr or "")).strip() if capture else ""
    if r.returncode not in ok_codes:
        stop(f"La commande a échoué :\n{sortie}")
    return r.returncode, sortie


def demander(question, defaut=""):
    if SIMULATION:
        print(f"{question} → {defaut or '(vide)'}")
        return defaut
    rep = input(f"{question}{f' [{defaut}]' if defaut else ''} : ").strip()
    return rep or defaut


# ----------------------------------------------------------------------------
def verifier_outils():
    titre("1/7 · Vérification des outils")
    manquants = [nom for nom, exe in (("Git", "git"), ("GitHub CLI", "gh")) if not shutil.which(exe)]
    if not manquants or SIMULATION:
        print("  ✅ Git et GitHub CLI sont installés.")
        return
    print(f"  Il manque : {', '.join(manquants)}.")
    if WINDOWS and shutil.which("winget"):
        if demander("  Je les installe maintenant ? (o/n)", "o").lower().startswith("o"):
            ids = {"Git": "Git.Git", "GitHub CLI": "GitHub.cli"}
            for nom in manquants:
                lancer(["winget", "install", "--id", ids[nom], "-e", "--silent",
                        "--accept-package-agreements", "--accept-source-agreements"],
                       ok_codes=(0, -1978335189), capture=False)  # ce code = déjà installé
            stop("Installation terminée. FERME cette fenêtre et relance mettre_en_ligne.bat "
                 "(Windows doit recharger les nouveaux programmes).")
    stop("Installe Git (https://git-scm.com) et GitHub CLI (https://cli.github.com), puis relance.")


def connexion():
    titre("2/7 · Connexion à GitHub")
    if not SIMULATION:
        st = subprocess.run(["gh", "auth", "status", "-h", "github.com"], capture_output=True, text=True)
        if st.returncode == 0:
            # le droit « workflow » est nécessaire pour envoyer le fichier de mise à jour automatique
            if "workflow" not in (st.stdout + st.stderr):
                print("  Ton navigateur va s'ouvrir pour accorder un droit en plus à l'outil GitHub.")
                lancer(["gh", "auth", "refresh", "-h", "github.com", "-s", "workflow"], capture=False)
            _, login = lancer(["gh", "api", "user", "--jq", ".login"])
            print(f"  ✅ Connectée en tant que {login}")
            return login
    print("  Ton navigateur va s'ouvrir : connecte-toi à GitHub et colle le code affiché ici.")
    lancer(["gh", "auth", "login", "-h", "github.com", "-p", "https", "-w", "-s", "workflow"], capture=False)
    _, login = lancer(["gh", "api", "user", "--jq", ".login"])
    return login or "ton-pseudo"


def infos_legales():
    titre("3/7 · Mentions légales")
    chemin = os.path.join(ICI, "bourse_bot", "config.py")
    texte = open(chemin, encoding="utf-8").read()
    if "[ton prénom ou pseudo]" not in texte and "[ton adresse e-mail de contact]" not in texte:
        print("  ✅ Déjà remplies.")
        return
    print("  La loi impose de pouvoir contacter l'éditeur d'un site. Un pseudo et un e-mail suffisent.")
    nom = demander("  Ton prénom ou pseudo", "")
    mail = demander("  Ton e-mail de contact", "")
    while not SIMULATION and (not nom or "@" not in mail):
        print("  Il faut un pseudo et une adresse e-mail valide.")
        nom = demander("  Ton prénom ou pseudo", nom)
        mail = demander("  Ton e-mail de contact", mail)
    if not SIMULATION:
        texte = texte.replace("[ton prénom ou pseudo]", nom.replace('"', "'"))
        texte = texte.replace("[ton adresse e-mail de contact]", mail.replace('"', "'"))
        open(chemin, "w", encoding="utf-8").write(texte)
    print("  ✅ Enregistré dans bourse_bot/config.py")


def envoyer(login):
    titre("4/7 · Création du dépôt et envoi des fichiers")
    depot = demander("  Nom du dépôt", "radar-bourse")
    depot = re.sub(r"[^A-Za-z0-9._-]", "-", depot)
    complet = f"{login}/{depot}"

    if not os.path.isdir(os.path.join(ICI, ".git")):
        lancer(["git", "init", "-b", "main"])
    # identité des commits : adresse « noreply » de GitHub pour ne pas publier ton vrai e-mail
    if not SIMULATION:
        _, uid = lancer(["gh", "api", "user", "--jq", ".id"])
        lancer(["git", "config", "user.name", login])
        lancer(["git", "config", "user.email", f"{uid}+{login}@users.noreply.github.com"])
    lancer(["git", "add", "-A"])
    lancer(["git", "commit", "-m", "Mise en ligne de Radar Bourse"], ok_codes=(0, 1))

    existe = SIMULATION is False and subprocess.run(
        ["gh", "repo", "view", complet], capture_output=True).returncode == 0
    if existe:
        print(f"  Le dépôt {complet} existe déjà : je le mets à jour.")
        distant = subprocess.run(["git", "remote"], cwd=ICI, capture_output=True, text=True).stdout
        if "origin" not in distant:
            lancer(["git", "remote", "add", "origin", f"https://github.com/{complet}.git"])
        # le robot GitHub ajoute l'historique des prédictions chaque soir : on le récupère d'abord
        lancer(["git", "pull", "--rebase", "-X", "theirs", "origin", "main"], ok_codes=(0, 1))
        lancer(["git", "push", "-u", "origin", "main"], capture=False)
    else:
        lancer(["gh", "repo", "create", complet, "--public", "--source", ".", "--push",
                "--description", "Radar Bourse : analyse et prévisions éducatives"], capture=False)
    print(f"  ✅ Fichiers envoyés sur https://github.com/{complet}")
    return complet


def activer_pages(complet):
    titre("5/7 · Activation de l'hébergement (GitHub Pages)")
    if SIMULATION:
        lancer(["gh", "api", "-X", "POST", f"repos/{complet}/pages", "-f", "build_type=workflow"])
        return
    r = subprocess.run(["gh", "api", "-X", "POST", f"repos/{complet}/pages", "-f", "build_type=workflow"],
                       capture_output=True, text=True)
    if r.returncode != 0:  # déjà activé : on s'assure juste du bon mode
        lancer(["gh", "api", "-X", "PUT", f"repos/{complet}/pages", "-f", "build_type=workflow"])
    print("  ✅ GitHub Pages activé.")


def cle_finnhub(complet):
    titre("6/7 · Actions US en direct (optionnel)")
    print("  Crée un compte gratuit sur https://finnhub.io et copie ta clé API.")
    print("  Laisse vide et appuie sur Entrée pour passer (tu pourras l'ajouter plus tard).")
    cle = "" if SIMULATION else getpass.getpass("  Clé Finnhub (invisible quand tu tapes) : ").strip()
    if cle:
        lancer(["gh", "secret", "set", "FINNHUB_KEY", "-R", complet], entree=cle)
        print("  ✅ Clé enregistrée en secret sur GitHub.")
    else:
        print("  Passé.")


def premiere_mise_a_jour(complet, login):
    titre("7/7 · Première mise à jour du site")
    for essai in range(10):  # GitHub met parfois quelques secondes à repérer le fichier de workflow
        if SIMULATION:
            lancer(["gh", "workflow", "run", "radar.yml", "-R", complet])
            break
        r = subprocess.run(["gh", "workflow", "run", "radar.yml", "-R", complet],
                           capture_output=True, text=True)
        if r.returncode == 0:
            break
        time.sleep(5)
    else:
        print("  ⚠️ Je n'ai pas pu lancer la mise à jour. Va dans l'onglet Actions du dépôt et clique "
              "« Mise à jour du Radar » → « Run workflow ».")
        return
    print("  Lancée ! Ça prend 3 à 6 minutes. Je te montre l'avancement :")
    if not SIMULATION:
        time.sleep(8)
        _, rid = lancer(["gh", "run", "list", "-R", complet, "-w", "radar.yml", "-L", "1",
                         "--json", "databaseId", "--jq", ".[0].databaseId"])
        if rid:
            subprocess.run(["gh", "run", "watch", rid, "-R", complet, "--exit-status"], cwd=ICI)


def main():
    print("🚀 Mise en ligne de Radar Bourse" + (" (SIMULATION)" if SIMULATION else ""))
    if not os.path.isdir(os.path.join(ICI, "bourse_bot")):
        stop("Lance ce script depuis le dossier Radar Bourse dézippé.")
    verifier_outils()
    login = connexion()
    infos_legales()
    complet = envoyer(login)
    activer_pages(complet)
    cle_finnhub(complet)
    premiere_mise_a_jour(complet, login)
    depot = complet.split("/")[1]
    url = f"https://{login.lower()}.github.io/{depot}/"
    print(f"\n🎉 Terminé ! Ton site : {url}")
    print("   Il se met à jour tout seul chaque heure. Si la page affiche une erreur 404,"
          " attends 2 minutes et rafraîchis.")
    if WINDOWS and not SIMULATION:
        try:
            os.startfile(url)
        except Exception:
            pass
        input("\nAppuie sur Entrée pour fermer…")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêté.")
