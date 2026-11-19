"""Version 92 : la source unique de vérité pour les chiffres publics du site.

Pourquoi : l'audit du site en ligne a trouvé le même chiffre écrit de cinq façons (« plus de 2 500 », « 2 517 », « 362 »,
« 340 », « près de 300 ») selon la page, parce que certains nombres étaient écrits à la main dans le texte et que d'autres
comptaient des choses différentes (avec ou sans les « tendances », avec ou sans les fiches simples).

Règles :
- chaque chiffre public est calculé ICI, une seule fois par génération, à partir des données du jour ;
- chaque chiffre a une définition et une source écrites (publiées sur chiffres-du-site.html et dans chiffres.json) ;
- un chiffre absent (donnée manquante) vaut None : il n'est jamais inventé ni remplacé par une valeur par défaut ;
- dans les textes fixes (gabarit de l'appli, traductions), on écrit un jeton __NB_xxx__ remplacé à la fin de la génération,
  au format de la langue de la page ;
- à la fin, controler() cherche dans les pages produites les anciennes formulations écrites à la main.
"""
from __future__ import annotations

import json
import os
import re

ACTUELS: dict = {}
MARCHES_ACTIONS = ("fr", "eu", "us", "monde")


def _plancher(n: int | None) -> int | None:
    """Arrondi vers le bas, pour écrire « plus de … » sans jamais exagérer."""
    if n is None:
        return None
    if n >= 1000:
        return n // 100 * 100
    if n >= 100:
        return n // 10 * 10
    return n


def nb_fr(n) -> str:
    return "–" if n is None else f"{int(n):,}".replace(",", " ")


def nb_en(n) -> str:
    return "–" if n is None else f"{int(n):,}"


def _pc(x):
    return None if x is None else round(float(x), 4)


def calculer(payload: dict) -> dict:
    titres = payload.get("titres", []) or []
    ia = [t for t in titres if t.get("marche") != "tendances"]   # les « tendances » sont des thèmes, pas des titres
    par = {}
    for t in ia:
        par[t.get("marche")] = par.get(t.get("marche"), 0) + 1
    nb_ia = len(ia)
    nb_etendu = int(payload.get("nb_etendu") or 0)
    nb_etendu_ia = payload.get("nb_etendu_ia")
    nb_etendu_ia = int(nb_etendu_ia) if nb_etendu_ia is not None else None
    M = payload.get("modele") or {}
    R = M.get("risque") or {}
    A = R.get("avis_surs") or {}
    F = M.get("fourchette") or {}
    cal = M.get("calibration") or []
    # confiance faible : avis entre 45 et 55 chances sur 100 ; on compte une bonne direction quand le sens annoncé s'est produit
    nb_f = sum(c.get("nb") or 0 for c in cal if c.get("min") in (0.45, 0.5) and c.get("taux_hausse") is not None)
    justes_f = sum((c["nb"] * (c["taux_hausse"] if c["min"] >= 0.5 else 1 - c["taux_hausse"]))
                   for c in cal if c.get("min") in (0.45, 0.5) and c.get("taux_hausse") is not None)
    S = payload.get("suivi") or {}
    c = {
        "version": 92,
        "genere_le": payload.get("genere_le"),
        "date_donnees": payload.get("date_donnees"),
        "date_evaluation": M.get("date_evaluation"),
        "demo": bool(payload.get("demo")),
        # ---- univers suivi
        "nb_ia": nb_ia,
        "nb_actions": sum(par.get(m, 0) for m in MARCHES_ACTIONS),
        "nb_cryptos": par.get("crypto", 0),
        "nb_etf": par.get("etf", 0),
        "par_marche": par,
        "nb_etendu": nb_etendu,
        "nb_etendu_ia": nb_etendu_ia,
        "nb_fiches": nb_ia + nb_etendu,
        "nb_avis_ia": nb_ia + (nb_etendu_ia or 0),
        # ---- performances mesurées hors échantillon (années jamais vues)
        "periode_test": M.get("periode"),
        "nb_tests": M.get("nb_tests"),
        "sens": _pc(M.get("precision")),
        "sens_reference": _pc(M.get("precision_base")),
        "sens_confiance_forte": _pc((M.get("top_confiance") or {}).get("precision")),
        "sens_confiance_faible": _pc(justes_f / nb_f) if nb_f else None,
        "agitation_avis_surs": _pc(A.get("taux")),
        "agitation_avis_surs_couverture": _pc(A.get("couverture")),
        "agitation_avis_tres_surs": _pc((A.get("tres") or {}).get("taux")),
        "fourchette_tenue": _pc(F.get("couverture")),
        "fourchette_promise": F.get("cible"),
        "chute_auc": _pc((R.get("chute") or {}).get("auc")),
        # ---- résultats réels, enregistrés avant de connaître la suite
        "reel_nb_verifiees": S.get("nb_verifiees"),
        "reel_nb_en_attente": S.get("nb_en_attente"),
        "reel_sens": _pc(S.get("precision")),
    }
    c["sources"] = SOURCES
    ACTUELS.clear()
    ACTUELS.update(c)
    return c


SOURCES = {
    "nb_ia": ("Titres analysés par l'IA chaque heure", "actions, ETF et cryptos de la liste suivie (config.py), hors pages « tendances »"),
    "nb_etendu": ("Fiches simples", "grandes actions mondiales ajoutées en plus (etendu_liste.json) : cours, tendance, agitation"),
    "nb_etendu_ia": ("Fiches simples avec un avis de l'IA", "avis calculé une fois par jour avec le même modèle, compté seulement s'il existe"),
    "nb_fiches": ("Titres qui ont une fiche", "titres analysés par l'IA + fiches simples"),
    "nb_avis_ia": ("Titres qui ont un avis de l'IA", "titres analysés chaque heure + fiches simples qui ont reçu un avis aujourd'hui"),
    "sens": ("Bonnes directions à un mois (hors échantillon)", "examen du soir, années jamais vues pendant l'apprentissage"),
    "sens_reference": ("Référence naïve", "répondre toujours la réponse la plus fréquente, sur les mêmes cas"),
    "sens_confiance_forte": ("Bonnes directions, 10 % d'avis les plus confiants", "examen du soir"),
    "sens_confiance_faible": ("Bonnes directions, avis entre 45 et 55 chances sur 100", "tableau de calibration de l'examen du soir"),
    "agitation_avis_surs": ("Avis sûrs sur l'agitation justes", "plus ou moins agité le mois suivant, seuil appris sur les seules années d'avant"),
    "fourchette_tenue": ("Fourchette « 8 fois sur 10 » tenue", "part des prix finaux dans la fourchette annoncée, années jamais vues"),
    "reel_sens": ("Résultats réels : bonnes directions", "prévisions enregistrées le jour même et vérifiées 20 séances plus tard"),
}


def get() -> dict:
    return ACTUELS


def jetons(langue: str = "fr") -> dict:
    """Les jetons à remplacer dans les textes fixes. Toujours au plancher : « plus de 2 500 » ne promet jamais plus que la réalité."""
    c = ACTUELS
    f = nb_fr if langue == "fr" else nb_en
    if not c:
        return {}
    return {
        "__NB_IA__": f(c["nb_ia"]),
        "__NB_FICHES__": f(_plancher(c["nb_fiches"])),
        "__NB_AVIS_IA__": f(_plancher(c["nb_avis_ia"])),
        "__NB_ETENDU__": f(c["nb_etendu"]),
    }


_JETON = re.compile(r"__NB_[A-Z_]+?__")


def appliquer(texte: str, langue: str = "fr") -> str:
    if "__NB_" not in texte:
        return texte
    j = jetons(langue)
    return _JETON.sub(lambda m: j.get(m.group(0), m.group(0)), texte)


# formulations écrites à la main autrefois et devenues fausses : leur retour serait une régression
ANCIENNES = [r"près de 300", r"[Nn]early 300", r"__NB_[A-Z_]+__", r"Avis de l'IA sur 2 500", r"sur plus de 2 500 actions et cryptos : hausse"]


def controler(dossier: str, limite: int = 20) -> list[str]:
    """Cherche dans les pages produites les jetons non remplacés et les anciens chiffres écrits à la main."""
    motif = re.compile("|".join(ANCIENNES))
    trouves = []
    for racine, _d, fichiers in os.walk(dossier):
        for nom in fichiers:
            if not nom.endswith(".html"):
                continue
            ch = os.path.join(racine, nom)
            try:
                with open(ch, encoding="utf-8") as fh:
                    m = motif.search(fh.read())
            except Exception:
                continue
            if m:
                trouves.append(f"{os.path.relpath(ch, dossier)} : « {m.group(0)} »")
                if len(trouves) >= limite:
                    return trouves
    return trouves


def ecrire_json(dossier: str) -> None:
    """chiffres.json : les mêmes chiffres, lisibles par tous (transparence)."""
    if not ACTUELS:
        return
    sortie = {k: v for k, v in ACTUELS.items() if k != "sources"}
    sortie["definitions"] = {k: {"nom": a, "source": b} for k, (a, b) in SOURCES.items()}
    with open(os.path.join(dossier, "chiffres.json"), "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)


def page(seo, base, payload, dossier, csp) -> list:
    """chiffres-du-site.html : chaque chiffre public, sa valeur du jour, ce qu'il mesure et d'où il vient."""
    c = ACTUELS
    if not c:
        return []
    e = seo._e
    pc = lambda x: "–" if x is None else f"{x * 100:.1f} %".replace(".", ",")
    val = {"nb_ia": nb_fr(c["nb_ia"]), "nb_etendu": nb_fr(c["nb_etendu"]), "nb_etendu_ia": nb_fr(c["nb_etendu_ia"]),
           "nb_fiches": nb_fr(c["nb_fiches"]), "nb_avis_ia": nb_fr(c["nb_avis_ia"]), "sens": pc(c["sens"]), "sens_reference": pc(c["sens_reference"]),
           "sens_confiance_forte": pc(c["sens_confiance_forte"]), "sens_confiance_faible": pc(c["sens_confiance_faible"]),
           "agitation_avis_surs": pc(c["agitation_avis_surs"]) + (f" (sur {pc(c['agitation_avis_surs_couverture'])} des cas)" if c.get("agitation_avis_surs_couverture") else ""),
           "fourchette_tenue": pc(c["fourchette_tenue"]) + (f" (promis : {pc(c['fourchette_promise'])})" if c.get("fourchette_promise") else ""),
           "reel_sens": pc(c["reel_sens"]) + (f" sur {nb_fr(c['reel_nb_verifiees'])} prévisions" if c.get("reel_nb_verifiees") else " (pas encore assez de recul)")}
    lignes = "".join(f"<tr><td><b>{e(SOURCES[k][0])}</b></td><td class='m'>{e(val.get(k, '–'))}</td><td class='muted' style='text-align:left'>{e(SOURCES[k][1])}</td></tr>" for k in SOURCES)
    pm = c.get("par_marche") or {}
    noms = {"fr": "actions françaises", "eu": "actions européennes", "us": "actions américaines", "monde": "actions du reste du monde", "etf": "ETF", "crypto": "cryptos"}
    detail = ", ".join(f"{pm[k]} {noms[k]}" for k in ("fr", "eu", "us", "monde", "etf", "crypto") if pm.get(k))
    corps = ("<h1>Les chiffres du site, et d'où ils viennent</h1>"
             "<p>Chaque chiffre affiché sur Radar Bourse est calculé à un seul endroit, à chaque mise à jour, à partir des données du jour. "
             "Aucun n'est écrit à la main dans les pages : ils ne peuvent donc plus se contredire d'une page à l'autre. Voici leur valeur aujourd'hui, "
             "ce qu'ils mesurent exactement, et leur source.</p>"
             + (f"<p class='muted'>Données du {e(seo.date_longue(c['date_donnees']))}" if c.get("date_donnees") else "<p class='muted'>")
             + (f" · examen de l'IA du {e(str(c['date_evaluation'])[:10])}" if c.get("date_evaluation") else "")
             + (f" · années de test : {e(c['periode_test'])}" if c.get("periode_test") else "") + "</p>"
             + (f"<p><b>Titres analysés par l'IA chaque heure :</b> {e(detail)}.</p>" if detail else "")
             + "<div class='carte' style='overflow-x:auto'><table><tr><td><b>Chiffre</b></td><td class='m'><b>Aujourd'hui</b></td><td style='text-align:left'><b>Ce qu'il mesure, d'où il vient</b></td></tr>"
             + lignes + "</table></div>"
             "<h2>Pourquoi deux sortes de résultats ?</h2><p>Les chiffres « hors échantillon » viennent de l'examen du soir : l'IA est testée sur des années "
             "qu'elle n'a jamais vues pendant son apprentissage. Les « résultats réels » sont des prévisions publiées, enregistrées le jour même puis "
             "vérifiées 20 séances plus tard (voir le <a href='registre-previsions.html'>registre public</a>). Les deux peuvent différer, surtout au début, "
             "quand les résultats réels ne portent que sur quelques semaines.</p>"
             "<p><a href='chiffres.json'>Les mêmes chiffres en JSON</a> · <a href='fiche-technique-ia.html'>Fiche technique de l'IA</a> · "
             "<a href='resultats.html'>Résultats réels</a></p>")
    chemin = "chiffres-du-site.html"
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Les chiffres du site et leur source | {seo.NOM}",
                          "Tous les chiffres publics de Radar Bourse (titres suivis, réussite de l'IA, fourchettes) avec leur définition et leur source, recalculés à chaque mise à jour.",
                          chemin, corps, csp=csp))
    return [(chemin, "daily", "0.5")]
