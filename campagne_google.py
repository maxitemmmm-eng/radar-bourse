"""Campagne Google gratuite : le programme qui t'accompagne chaque semaine.

À lancer une fois par semaine (double-clic sur campagne_google.bat, ou choix du menu). Il :
1. vérifie les pages du site en ligne comme le ferait Google (titre, description, titre principal, page bloquée…) ;
2. te dit où tu en es dans le plan de 8 semaines et ce qu'il reste à faire cette semaine ;
3. ouvre Search Console et copie pour toi, une par une, les adresses des pages à faire indexer aujourd'hui
   (Google en accepte une dizaine par jour) : tu colles, puis tu cliques sur « Demander l'indexation » ;
4. se souvient de ce qui a déjà été envoyé (fichier rapports/campagne.json, sur ce PC uniquement).

Rien n'est payant, rien n'est publié à ton nom.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser
from datetime import date

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
ETAT = os.path.join("rapports", "campagne.json")
PAR_JOUR = 10

# Les pages à faire connaître en premier : celles qui répondent aux recherches les plus tapées
PRIORITE = ["", "previsions.html", "comparer.html", "classements.html", "resultats.html", "point.html", "titres.html",
            "classements/actions-dividende.html", "classements/actions-calmes.html", "classements/cryptos-agitees.html",
            "titres/btc-usd.html", "titres/nvda.html", "titres/aapl.html", "titres/tsla.html", "titres/mc-pa.html",
            "titres/eth-usd.html", "titres/tte-pa.html", "titres/ai-pa.html", "titres/air-pa.html", "titres/msft.html",
            "comparer/gld-ou-btc-usd.html", "comparer/cw8-pa-ou-spy.html", "comparer/btc-usd-ou-eth-usd.html",
            "comparer/mc-pa-ou-rms-pa.html", "comparer/ko-ou-pep.html", "comparer/v-ou-ma.html", "comparer/nvda-ou-amd.html",
            "titres/sol-usd.html", "titres/xrp-usd.html", "titres/rno-pa.html", "titres/ho-pa.html", "titres/san-pa.html",
            "titres/or-pa.html", "titres/bnp-pa.html", "titres/amzn.html", "titres/googl.html", "titres/meta.html"]

PLAN = {
    1: ["Faire indexer les pages principales (ce programme les ouvre pour toi, 10 par jour)",
        "Search Console › Sitemaps : vérifier l'état « Réussite »"],
    2: ["Bing Webmaster Tools : « Importer depuis Google Search Console » (alimente aussi DuckDuckGo, Copilot, ChatGPT)",
        "Continuer l'indexation : 10 pages par jour"],
    3: ["GitHub : mettre l'adresse du site et des sujets (bourse, crypto, machine-learning) dans « About » du dépôt",
        "Si tu connais quelqu'un qui a un blog ou un site : lui proposer l'encadré gratuit (code en bas de chaque fiche)",
        "Créer une fiche gratuite sur AlternativeTo (alternative gratuite à Danelfin / Zonebourse), avec un pseudo",
        "Textes prêts à copier (GitHub, awesome-quant, AlternativeTo, Product Hunt) : fichier LISTES_A_PROPOSER.md"],
    4: ["Search Console › Performances › Requêtes : capture à envoyer à Claude pour ajuster les titres",
        "Search Console › Améliorations : vérifier qu'il n'y a pas d'erreur"],
    5: ["Demander l'indexation du bilan du mois dès qu'il apparaît (bilan/…)", "Continuer l'indexation des fiches"],
    6: ["Option : partager l'image du jour là où tu es déjà", "Continuer l'indexation des comparaisons"],
    7: ["Deuxième capture des requêtes pour Claude : nouvelles pages à créer", "Indexer les nouvelles pages"],
    8: ["Bilan des 8 semaines : clics, impressions, position moyenne (capture pour Claude)",
         "Ensuite : la routine de 10 minutes par mois (capture des requêtes, bilan du mois à indexer)"],
}


def adresse_site() -> str | None:
    """L'adresse du site, d'après les réglages de mettre_en_ligne (ou le dépôt GitHub du dossier)."""
    try:
        with open(".radar_deploy.json", encoding="utf-8") as f:
            m = json.load(f)
        if m.get("domaine"):
            return f"https://{m['domaine']}/"
        if m.get("login") and m.get("depot"):
            return f"https://{m['login'].lower()}.github.io/{m['depot']}/"
    except (OSError, ValueError):
        pass
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10).stdout.strip()
        r = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
        if r:
            return f"https://{r.group(1).lower()}.github.io/{r.group(2)}/"
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def lire(url: str, timeout=20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "radar-bourse-campagne"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def etat() -> dict:
    try:
        with open(ETAT, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def sauver(e: dict):
    os.makedirs("rapports", exist_ok=True)
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)


def copier(texte: str) -> bool:
    """Copie le texte dans le presse-papiers (Windows, Mac ou Linux). Renvoie False si impossible."""
    for cmd, enc in ((["clip"], "utf-16"), (["pbcopy"], "utf-8"), (["xclip", "-selection", "clipboard"], "utf-8")):
        try:
            subprocess.run(cmd, input=texte.encode(enc), check=True, timeout=5)
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def verifier_page(url: str) -> list[str]:
    """Ce que Google regarde en premier sur une page."""
    try:
        h = lire(url)
    except Exception as ex:
        return [f"page inaccessible ({ex})"]
    pb = []
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    titre = html.unescape(t.group(1).strip()) if t else ""
    if not titre:
        pb.append("pas de titre")
    elif len(titre) > 75:
        pb.append(f"titre un peu long ({len(titre)} caractères : Google coupera la fin)")
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    desc = html.unescape(d.group(1)) if d else ""
    if not desc:
        pb.append("pas de description")
    elif not 50 <= len(desc) <= 200:
        pb.append(f"description de {len(desc)} caractères (idéal : 120 à 160)")
    nb_h1 = len(re.findall(r"<h1[\s>]", h))
    if nb_h1 != 1 and "index.html" not in url and not url.endswith("/"):
        pb.append(f"{nb_h1} titres principaux (h1) au lieu d'un")
    if re.search(r'<meta name="robots" content="[^"]*noindex', h):
        pb.append("page interdite à Google (noindex)")
    if 'rel="canonical"' not in h:
        pb.append("pas d'adresse canonique")
    return pb


def _nombre(v: str) -> float | None:
    v = str(v).strip().replace("\u202f", "").replace("\xa0", "").replace(" ", "").replace("%", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def _lire_csv(texte: str) -> list[dict]:
    import csv
    import io
    lignes = list(csv.reader(io.StringIO(texte.lstrip("\ufeff"))))
    if len(lignes) < 2:
        return []
    tete = [h.strip().lower() for h in lignes[0]]
    out = []
    for l in lignes[1:]:
        if len(l) < len(tete):
            continue
        d = dict(zip(tete, l))
        cle = l[0].strip()
        val = {"cle": cle}
        for nom, mots in (("clics", ("clic", "click")), ("impressions", ("impression",)), ("ctr", ("ctr",)), ("position", ("position",))):
            col = next((h for h in tete if any(m in h for m in mots)), None)
            val[nom] = _nombre(d[col]) if col else None
        out.append(val)
    return out


def trouver_export() -> dict:
    """Cherche le dernier export « Performances » de Search Console (zip ou CSV) dans Téléchargements ou ce dossier."""
    import glob
    import zipfile
    lieux = [ICI, os.path.join(os.path.expanduser("~"), "Downloads"), os.path.join(os.path.expanduser("~"), "Téléchargements")]
    zips = []
    for l in lieux:
        zips += glob.glob(os.path.join(l, "*.zip"))
    for z in sorted(zips, key=os.path.getmtime, reverse=True)[:15]:
        try:
            with zipfile.ZipFile(z) as f:
                noms = f.namelist()
                req = next((n for n in noms if n.lower().startswith(("requ", "quer"))), None)
                pag = next((n for n in noms if n.lower().startswith("pages")), None)
                if req or pag:
                    lire_f = lambda n: f.read(n).decode("utf-8", "replace") if n else ""
                    return {"source": z, "requetes": _lire_csv(lire_f(req)), "pages": _lire_csv(lire_f(pag))}
        except (zipfile.BadZipFile, OSError):
            continue
    return {}


def analyser_export(base: str) -> list[str]:
    """Ce que les résultats Google disent de faire : pages vues mais peu cliquées, recherches presque en 1re page."""
    ex = trouver_export()
    if not ex:
        return ["   Aucun export trouvé. Dans Search Console › Performances, clique sur « Exporter » › « Télécharger au format CSV »,",
                "   puis relance ce programme : il trouvera le fichier tout seul dans Téléchargements."]
    req, pages = ex["requetes"], ex["pages"]
    clics = sum(r["clics"] or 0 for r in pages or req)
    impr = sum(r["impressions"] or 0 for r in pages or req)
    out = [f"   Export lu : {os.path.basename(ex['source'])}",
           f"   Total : {int(clics)} clics pour {int(impr)} apparitions dans Google ({(clics / impr * 100 if impr else 0):.1f} % de clics).".replace(".", ",", 1)]
    a_retravailler = [p for p in pages if (p["impressions"] or 0) >= 30 and (p["ctr"] or 0) < 2 and (p["position"] or 99) <= 20]
    a_retravailler.sort(key=lambda p: -(p["impressions"] or 0))
    if a_retravailler:
        out.append("   Pages souvent vues mais peu cliquées (leur titre ou leur description donne peu envie) :")
        out += [f"     • {p['cle'].replace(base, '/')} : {int(p['impressions'])} apparitions, "
                f"{str(round(p['ctr'], 1)).replace('.', ',')} % de clics, position {p['position']:.0f}" for p in a_retravailler[:10]]
    presque = [r for r in req if (r["impressions"] or 0) >= 20 and 8 <= (r["position"] or 0) <= 20]
    presque.sort(key=lambda r: -(r["impressions"] or 0))
    if presque:
        out.append("   Recherches presque en première page (position 8 à 20) : un petit coup de pouce peut les faire monter :")
        out += [f"     • « {r['cle']} » : position {r['position']:.0f}, {int(r['impressions'])} apparitions" for r in presque[:10]]
    top = sorted(req, key=lambda r: -(r["clics"] or 0))[:5]
    if top:
        out.append("   Recherches qui t'amènent le plus de visiteurs : " + ", ".join(f"« {r['cle']} »" for r in top) + ".")
    out.append("   ➜ Envoie ce rapport à Claude : il retravaille les titres et crée les pages qui manquent.")
    return out


def main() -> int:
    print("━" * 64)
    print("  📣 Campagne Google gratuite · Radar Bourse")
    print("━" * 64)
    base = adresse_site()
    if not base:
        base = input("Adresse du site (ex. https://pseudo.github.io/radar-bourse/) : ").strip()
        if not base:
            return 1
    if not base.endswith("/"):
        base += "/"
    print(f"Site : {base}\n")
    e = etat()
    e.setdefault("debut", date.today().isoformat())
    e.setdefault("envoyees", {})
    semaine = min(8, (date.today() - date.fromisoformat(e["debut"])).days // 7 + 1)

    # 1. Les pages du site, vues comme Google
    print("1. Vérification des pages en ligne…")
    try:
        plan_site = lire(base + "sitemap.xml")
        toutes = re.findall(r"<loc>([^<]+)</loc>", plan_site)
        print(f"   ✅ Plan du site lu : {len(toutes)} pages déclarées à Google.")
    except Exception as ex:
        toutes = []
        print(f"   ⚠️ Plan du site illisible ({ex}). Vérifie que le site est bien en ligne.")
    a_verifier = [base + p for p in PRIORITE[:12]]
    souci = 0
    for u in a_verifier:
        pb = verifier_page(u)
        if pb:
            souci += 1
            print(f"   ⚠️ {u.replace(base, '/') or '/'} : {', '.join(pb)}")
    if not souci:
        print(f"   ✅ Les {len(a_verifier)} pages principales ont un titre, une description et une adresse canonique corrects.")

    # 2. Où en est le plan
    print(f"\n2. Plan de campagne : semaine {semaine} sur 8 (commencé le {date.fromisoformat(e['debut']):%d/%m/%Y})")
    for tache in PLAN[semaine]:
        print(f"   ☐ {tache}")

    # 3. Les pages à faire indexer aujourd'hui
    deja = e["envoyees"]
    candidates = [base + p for p in PRIORITE] + [u for u in toutes if "/bilan/" in u] + \
                 [u for u in toutes if "/comparer/" in u or "/titres/" in u]
    vues, a_faire = set(), []
    for u in candidates:
        if u not in vues and u not in deja:
            vues.add(u)
            a_faire.append(u)
    aujourd_hui = a_faire[:PAR_JOUR]
    print(f"\n3. Indexation : {len(deja)} pages déjà envoyées à Google, {len(a_faire)} restantes.")
    if not aujourd_hui:
        print("   ✅ Toutes les pages prioritaires ont été envoyées. Bravo !")
    else:
        prop = urllib.parse.quote(base, safe="")
        print(f"   Pages du jour ({len(aujourd_hui)}) :")
        for u in aujourd_hui:
            print(f"   • {u}")
        r = input("\n   On les envoie à Google maintenant ? (o/n) ").strip().lower()
        if r in ("o", "oui", "y", ""):
            webbrowser.open_new_tab(f"https://search.google.com/search-console?resource_id={prop}")
            print("\n   Search Console s'ouvre dans ton navigateur (connecte-toi si besoin, avec le compte où tu as ajouté le site).")
            print("   Pour chaque page, le programme COPIE son adresse pour toi. Ensuite, dans Search Console :")
            print("     1. clique dans la barre tout en haut « Inspecter n'importe quelle URL »")
            print("     2. colle avec Ctrl+V, puis Entrée")
            print("     3. clique sur « Demander l'indexation » et attends le message « Indexation demandée »")
            print("   (« L'URL n'est pas sur Google » est normal pour une page neuve. « Quota dépassé » : arrête et reprends demain.)\n")
            for k, u in enumerate(aujourd_hui, 1):
                copie = copier(u)
                rep = input(f"   [{k}/{len(aujourd_hui)}] {'Copié' if copie else 'À copier'} : {u}\n"
                            "         Entrée quand c'est fait · s pour sauter · q pour arrêter : ").strip().lower()
                if rep == "q":
                    break
                if rep != "s":
                    deja[u] = date.today().isoformat()
            print(f"\n   ✅ Noté. {len(a_faire) - sum(1 for u in a_faire if u in deja)} pages restent pour les prochains jours.")
    sauver(e)
    print("\n4. Tes résultats dans Google (export de Search Console)")
    rapport = analyser_export(base)
    print("\n".join(rapport))
    try:
        os.makedirs("rapports", exist_ok=True)
        with open(os.path.join("rapports", f"analyse_google_{date.today().isoformat()}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(rapport) + "\n")
    except OSError:
        pass
    print("\n5. Rappel : Google met en général 2 à 6 mois à faire monter un site neuf. Regarde d'abord les impressions "
          "(Search Console › Performances), les clics viennent après.")
    print(f"\nSuivi enregistré dans {ETAT} (sur ce PC uniquement).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        sys.exit(1)
