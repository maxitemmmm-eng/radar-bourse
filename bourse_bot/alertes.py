"""Alertes Telegram : chaque soir, le robot publie un résumé sur une chaîne Telegram.

Configuration (faite par mettre_en_ligne.py) :
- secret GitHub TELEGRAM_TOKEN : le jeton du bot créé avec @BotFather ;
- secret GitHub TELEGRAM_CHAT  : la chaîne où publier, par ex. @radar_bourse_alertes ;
- variable GitHub TELEGRAM_CHAINE : le nom public de la chaîne (affiché sur le site).
"""
from __future__ import annotations

import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime

from . import seo

LIB = {"ACHAT FORT": "haussier fort", "ACHAT": "haussier", "NEUTRE": "neutre",
       "VENTE": "baissier", "VENTE FORTE": "baissier fort"}


def envoyer(texte: str, token: str | None = None, chat: str | None = None) -> bool:
    token = token or os.environ.get("TELEGRAM_TOKEN", "")
    chat = chat or os.environ.get("TELEGRAM_CHAT", "")
    if not token or not chat:
        return False
    donnees = urllib.parse.urlencode({"chat_id": chat, "text": texte, "parse_mode": "HTML",
                                      "disable_web_page_preview": "true"}).encode()
    try:
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=donnees)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r).get("ok", False)
    except Exception:
        return False


def _pct(v):
    return "–" if v is None else f"{'+' if v > 0 else ''}{v * 100:.1f} %".replace(".", ",")


def resume(payload: dict) -> str:
    """Message du soir : signaux forts, meilleures probabilités, météo, lien vers le site."""
    e = html.escape
    base = seo.url_site()
    titres = payload.get("titres", [])
    date = datetime.now().strftime("%d/%m/%Y")
    forts = sorted([t for t in titres if t.get("signal_fort")], key=lambda t: -(t.get("proba_hausse") or 0))
    meilleurs = sorted([t for t in titres if t.get("proba_hausse") is not None and not t.get("signal_fort")],
                       key=lambda t: -t["proba_hausse"])[:3]

    def ligne(t):
        p = t.get("proba_hausse")
        med = t["cone"]["mediane"][-1] if t.get("cone") else None
        lien = f'{base}titres/{seo.slug(t["ticker"])}.html' if base else ""
        nom = f'<a href="{e(lien)}">{e(t["nom"])}</a>' if lien else e(t["nom"])
        return (f"• {nom} ({e(t['ticker'])}) : {round(p * 10)} chances sur 10 de hausse à 1 mois"
                + (f", scénario central {_pct(med / t['prix'] - 1)}" if med else ""))

    morceaux = [f"📡 <b>Radar Bourse · {date}</b>"]
    if forts:
        morceaux.append("\n<b>Signaux forts</b> (modèle confiant + tendance technique haussière) :")
        morceaux += [ligne(t) for t in forts[:8]]
    else:
        morceaux.append("\nAucun signal fort ce soir : les conditions ne sont pas réunies.")
    if meilleurs:
        morceaux.append("\n<b>Autres probabilités les plus élevées</b> :")
        morceaux += [ligne(t) for t in meilleurs]
    m = payload.get("modele") or {}
    sf = m.get("signaux_forts") or {}
    if sf.get("precision") is not None:
        morceaux.append(f"\nRéussite mesurée des signaux forts sur l'historique : {round(sf['precision'] * 100)} % "
                        f"(contre {round(sf['base'] * 100)} % en moyenne).")
    if base:
        morceaux.append(f'\n👉 <a href="{e(base)}">Graphiques, simulateur et explications</a>')
    morceaux.append("\n⚠️ Calculs automatiques, rien n'est sûr. Pas un conseil en investissement : "
                    "tu peux perdre l'argent investi.")
    return "\n".join(morceaux)[:4000]


def publier_si_active(payload: dict) -> str:
    if os.environ.get("RADAR_ALERTES") != "1":
        return "désactivées pour cette exécution"
    if not os.environ.get("TELEGRAM_TOKEN") or not os.environ.get("TELEGRAM_CHAT"):
        return "non configurées"
    return "envoyées" if envoyer(resume(payload)) else "échec de l'envoi"
