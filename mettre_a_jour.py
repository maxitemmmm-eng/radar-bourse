"""Mise à jour en un clic.

1. Télécharge le nouveau radar_bourse.zip (il arrive en général dans « Téléchargements »).
2. Double-clique sur mettre_a_jour.bat, dans ton dossier Radar Bourse habituel.

Le script trouve le zip le plus récent, remplace le code de ton dossier par la nouvelle version
(sans toucher à l'historique, aux connaissances de l'IA ni à tes réglages), puis met le site en ligne.
Plus besoin de dézipper ni de chercher le bon dossier.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import zipfile
from datetime import datetime

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)

# Ce qui n'est JAMAIS remplacé : ce que le site et l'IA ont appris, tes réglages et tes rapports
PROTEGES = ("historique/", ".git/", "rapports/", ".cache_cours/", ".cache_entrainement/", "site/")
PROTEGES_FICHIERS = (".radar_deploy.json", "mettre_a_jour.bat")   # le .bat en cours d'exécution ne doit pas changer


def dire(msg=""):
    print(msg, flush=True)


def trouver_zip():
    lieux = [ICI, os.path.join(os.path.expanduser("~"), "Downloads"), os.path.join(os.path.expanduser("~"), "Téléchargements"),
             os.path.join(os.path.expanduser("~"), "Desktop"), os.path.join(os.path.expanduser("~"), "Bureau"),
             os.path.dirname(ICI)]
    zips = []
    for lieu in lieux:
        zips += glob.glob(os.path.join(lieu, "radar_bourse*.zip"))
    zips = [z for z in set(zips) if os.path.isfile(z) and "_installe_" not in os.path.basename(z)]
    return max(zips, key=os.path.getmtime) if zips else None


def racine_du_zip(noms):
    """Le zip peut contenir les fichiers directement, ou dans un dossier « radar_bourse/ »."""
    for n in noms:
        if n.endswith("bourse_bot/__init__.py"):
            return n[: -len("bourse_bot/__init__.py")]
    return None


def extraire(chemin_zip) -> int:
    with zipfile.ZipFile(chemin_zip) as z:
        noms = z.namelist()
        racine = racine_du_zip(noms)
        if racine is None:
            dire("❌ Ce zip ne contient pas Radar Bourse (dossier bourse_bot introuvable). Rien n'a été changé.")
            return -1
        n = 0
        for info in z.infolist():
            if not info.filename.startswith(racine) or info.is_dir():
                continue
            rel = info.filename[len(racine):].replace("\\", "/")
            if not rel or rel.startswith(PROTEGES) or rel in PROTEGES_FICHIERS:
                continue
            cible = os.path.normpath(os.path.join(ICI, rel))
            if not cible.startswith(os.path.normpath(ICI) + os.sep):   # sécurité : rien en dehors du dossier
                continue
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            with z.open(info) as src, open(cible, "wb") as dst:
                dst.write(src.read())
            n += 1
    return n


def main():
    dire("━━ Mise à jour de Radar Bourse")
    if not os.path.isdir(os.path.join(ICI, "bourse_bot")):
        dire("❌ Lance ce fichier depuis ton dossier Radar Bourse habituel.")
        return 1
    z = trouver_zip()
    if not z:
        dire("Aucun fichier radar_bourse.zip trouvé dans Téléchargements, sur le Bureau ou dans ce dossier.")
        dire("Télécharge d'abord la nouvelle version, puis relance ce fichier.")
        return 1
    quand = datetime.fromtimestamp(os.path.getmtime(z)).strftime("%d/%m/%Y à %H:%M")
    dire(f"Nouvelle version trouvée : {z}  (du {quand})")
    if "--oui" not in sys.argv:
        r = input("Installer cette version et mettre le site à jour ? [Entrée = oui, n = non] ").strip().lower()
        if r in ("n", "non", "no"):
            dire("Rien n'a été changé.")
            return 0
    n = extraire(z)
    if n < 0:
        return 1
    dire(f"✅ {n} fichiers mis à jour. Historique, connaissances de l'IA et réglages : gardés tels quels.")
    try:   # on range le zip pour ne pas le réinstaller par erreur la prochaine fois
        os.replace(z, z[:-4] + f"_installe_{datetime.now():%Y%m%d_%H%M}.zip")
    except OSError:
        pass
    if "--sans-envoi" in sys.argv:
        return 0
    dire("\nMise en ligne (tes réponses précédentes sont réutilisées, il ne devrait rien te demander)…\n")
    return subprocess.call([sys.executable, os.path.join(ICI, "mettre_en_ligne.py")], cwd=ICI)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nArrêté.")
        sys.exit(1)
