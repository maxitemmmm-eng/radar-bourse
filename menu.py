"""Le menu de Radar Bourse : tous les outils au même endroit.

Double-clique sur « Radar Bourse.bat » et tape le numéro de ce que tu veux faire.
(Les anciens fichiers .bat marchent toujours, ce menu les regroupe simplement.)
"""
from __future__ import annotations

import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
PY = sys.executable

CHOIX = [
    ("Installer une nouvelle version reçue en zip (et mettre le site en ligne)", [PY, "mettre_a_jour.py"]),
    ("Remettre le site en ligne (après une modification)", [PY, "mettre_en_ligne.py"]),
    ("Entraîner l'IA sur ce PC (en plus de l'entraînement automatique de chaque nuit)", [PY, "entrainement_ia.py"]),
    ("Mon bilan privé : combien de fois les IA ont eu raison", [PY, "mon_bilan_ia.py"]),
    ("Tester l'IA sur 5000 cas réels tirés au hasard (10 à 25 min)", [PY, "tester_ia.py"]),
    ("Voir le site sur ce PC avec les cours du jour", [PY, "-m", "bourse_bot", "site"]),
    ("Inscrire le site sur Google", [PY, "mettre_en_ligne.py", "--google"]),
    ("Campagne Google de la semaine (vérifier les pages, faire indexer les pages du jour)", [PY, "campagne_google.py"]),
    ("Statistiques de visites (privées)", [PY, "mettre_en_ligne.py", "--stats"]),
    ("Nom de domaine personnalisé", [PY, "mettre_en_ligne.py", "--domaine"]),
    ("Alertes Telegram", [PY, "mettre_en_ligne.py", "--telegram"]),
]


def main():
    while True:
        print("\n" + "━" * 62)
        print("  📡 Radar Bourse · que veux-tu faire ?")
        print("━" * 62)
        for i, (lib, _) in enumerate(CHOIX, 1):
            print(f"  {i}. {lib}")
        print("  0. Quitter")
        r = input("\nTon choix : ").strip()
        if r in ("0", "q", ""):
            return 0
        if not r.isdigit() or not 1 <= int(r) <= len(CHOIX):
            print("Tape un numéro de la liste.")
            continue
        lib, cmd = CHOIX[int(r) - 1]
        print(f"\n▶ {lib}\n")
        try:
            subprocess.call(cmd, cwd=ICI)
        except KeyboardInterrupt:
            print("\nArrêté.")
        input("\nAppuie sur Entrée pour revenir au menu…")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
