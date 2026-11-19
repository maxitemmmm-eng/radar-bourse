"""Version 92 : le registre public des prévisions, impossible à modifier en douce.

Chaque soir, les prévisions publiées sont copiées dans un fichier du jour (historique/registre/AAAA-MM-JJ.csv) qui n'est
JAMAIS réécrit. Chaque fichier est « scellé » dans une chaîne (historique/registre/chaine.csv) : son empreinte SHA-256,
et l'empreinte du bloc précédent. Modifier un ancien fichier, même d'un chiffre, change son empreinte et casse toute la
chaîne qui suit : n'importe qui peut le vérifier, dans son navigateur (page registre-previsions.html) ou avec la commande
`sha256sum`. L'historique git du dépôt horodate en plus chaque soir.

Corrections : on ne réécrit jamais un fichier scellé. Une erreur découverte (cours faux, titre retiré de la cote…) est
ajoutée dans historique/registre/corrections.csv, avec la date et le motif, et affichée publiquement.

Bloc 0 : l'historique enregistré AVANT la création du registre, scellé tel quel le jour de la création. Pour ce bloc, la
date de chaque prévision n'est garantie que par l'historique git (le fichier predictions.csv a été enregistré chaque soir).
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import shutil
from datetime import date

from . import config

DOSSIER = os.path.join(config.DOSSIER_HISTORIQUE, "registre")
CHAINE = os.path.join(DOSSIER, "chaine.csv")
CORRECTIONS = os.path.join(DOSSIER, "corrections.csv")
COLS = ["date", "ticker", "prix", "proba", "bas", "haut", "confiance"]
COLS_CHAINE = ["bloc", "scelle_le", "fichier", "nb", "empreinte_fichier", "precedent", "modele", "note", "empreinte_bloc"]
ZERO = "0" * 64


def _f(v, d=6):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return ""
    if x != x or x in (float("inf"), float("-inf")):
        return ""
    return f"{x:.{d}g}"


def _contenu(lignes: list[dict]) -> bytes:
    """Format canonique : en-tête fixe, lignes triées, nombres écrits toujours pareil, fin de ligne \\n."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLS)
    propres = []
    for r in lignes:
        if not r.get("ticker") or not r.get("date"):
            continue
        propres.append([str(r["date"])[:10], str(r["ticker"]), _f(r.get("prix")), _f(r.get("proba"), 4),
                        _f(r.get("bas")), _f(r.get("haut")), str(r.get("confiance") or "")])
    for p in sorted(propres, key=lambda x: (x[1], x[0])):
        w.writerow(p)
    return buf.getvalue().encode("utf-8")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def empreinte_bloc(b: dict) -> str:
    champs = "|".join(str(b.get(k, "")) for k in COLS_CHAINE[:-1])
    return _sha(champs.encode("utf-8"))


def chaine() -> list[dict]:
    if not os.path.exists(CHAINE):
        return []
    with open(CHAINE, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _ajouter_bloc(fichier: str, contenu: bytes, modele: str, note: str, jour: str) -> dict:
    os.makedirs(DOSSIER, exist_ok=True)
    ch = chaine()
    chemin = os.path.join(DOSSIER, fichier)
    if os.path.exists(chemin):
        raise FileExistsError(fichier)   # un fichier scellé n'est jamais réécrit
    with open(chemin, "wb") as f:
        f.write(contenu)
    b = {"bloc": str(len(ch)), "scelle_le": jour, "fichier": fichier, "nb": str(contenu.count(b"\n") - 1),
         "empreinte_fichier": _sha(contenu), "precedent": ch[-1]["empreinte_bloc"] if ch else ZERO,
         "modele": (modele or "").replace("|", "/").replace("\n", " "), "note": (note or "").replace("|", "/").replace("\n", " ")}
    b["empreinte_bloc"] = empreinte_bloc(b)
    nouveau = not os.path.exists(CHAINE)
    with open(CHAINE, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS_CHAINE, lineterminator="\n")
        if nouveau:
            w.writeheader()
        w.writerow(b)
    return b


def sceller(lignes: list[dict], modele: str = "", jour: str | None = None) -> dict | None:
    """Scelle les prévisions du soir. Une seule fois par jour ; jamais en mode démo (l'appelant le vérifie)."""
    jour = jour or date.today().isoformat()
    os.makedirs(DOSSIER, exist_ok=True)
    if not chaine():
        _genese(jour)
    fichier = f"{jour}.csv"
    if os.path.exists(os.path.join(DOSSIER, fichier)) or not lignes:
        return None
    return _ajouter_bloc(fichier, _contenu(lignes), modele, "prévisions publiées ce soir-là", jour)


def _genese(jour: str) -> dict | None:
    """Bloc 0 : tout l'historique d'avant le registre, scellé tel qu'il est le jour de la création."""
    src = os.path.join(config.DOSSIER_HISTORIQUE, "predictions.csv")
    if not os.path.exists(src):
        return None
    with open(src, encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        return None
    return _ajouter_bloc("bloc0-avant-le-registre.csv", _contenu(lignes), "modèle non noté (avant le registre)",
                         "historique enregistré avant la création du registre, scellé tel quel ; dates garanties par l'historique git", jour)


def verifier(dossier: str = DOSSIER) -> dict:
    """Recalcule toutes les empreintes. Renvoie {"ok": bool, "nb_blocs", "probleme"}."""
    ch = []
    p = os.path.join(dossier, "chaine.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8", newline="") as f:
            ch = list(csv.DictReader(f))
    prec = ZERO
    for b in ch:
        if b["precedent"] != prec:
            return {"ok": False, "nb_blocs": len(ch), "probleme": f"bloc {b['bloc']} : lien vers le bloc précédent cassé"}
        if empreinte_bloc(b) != b["empreinte_bloc"]:
            return {"ok": False, "nb_blocs": len(ch), "probleme": f"bloc {b['bloc']} : empreinte du bloc fausse"}
        try:
            with open(os.path.join(dossier, b["fichier"]), "rb") as f:
                if _sha(f.read()) != b["empreinte_fichier"]:
                    return {"ok": False, "nb_blocs": len(ch), "probleme": f"bloc {b['bloc']} : le fichier {b['fichier']} a été modifié"}
        except OSError:
            return {"ok": False, "nb_blocs": len(ch), "probleme": f"bloc {b['bloc']} : fichier {b['fichier']} manquant"}
        prec = b["empreinte_bloc"]
    return {"ok": True, "nb_blocs": len(ch), "probleme": None}


def corrections() -> list[dict]:
    if not os.path.exists(CORRECTIONS):
        return []
    with open(CORRECTIONS, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _lire(fichier: str) -> list[dict]:
    with open(os.path.join(DOSSIER, fichier), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def performance(donnees: dict, horizon: int = config.HORIZON_PREDICTION) -> dict:
    """Performance par modèle, uniquement sur les prévisions scellées dont l'échéance est passée."""
    import numpy as np
    import pandas as pd
    from .model import wilson
    idx, jours = {}, {}
    exclus = {(c.get("date"), c.get("ticker")) for c in corrections() if c.get("action", "exclure") == "exclure"}
    par = {}
    for b in chaine():
        try:
            lignes = _lire(b["fichier"])
        except OSError:
            continue
        m = par.setdefault(b["modele"] or "modèle non noté", {"nb": 0, "justes": 0, "four_nb": 0, "four_ok": 0, "attente": 0, "blocs": set()})
        m["blocs"].add(int(b["bloc"]))
        for r in lignes:
            if (r["date"], r["ticker"]) in exclus:
                continue
            d = donnees.get(r["ticker"])
            try:
                p, prix = float(r["proba"]), float(r["prix"])
            except (TypeError, ValueError):
                continue
            if d is None or "Close" not in getattr(d, "columns", []):
                m["attente"] += 1
                continue
            if r["ticker"] not in idx:
                idx[r["ticker"]] = (d.index.values, d["Close"].to_numpy(dtype=float))
            ix, cl = idx[r["ticker"]]
            if r["date"] not in jours:
                jours[r["date"]] = np.datetime64(pd.Timestamp(r["date"]).to_datetime64())
            k = int(np.searchsorted(ix, jours[r["date"]], side="right")) + horizon - 1
            if k >= len(cl):
                m["attente"] += 1
                continue
            fin = float(cl[k])
            if fin != fin:
                continue
            if p == 0.5 or fin == prix:
                continue
            m["nb"] += 1
            m["justes"] += int((p > 0.5) == (fin > prix))
            try:
                bas, haut = float(r["bas"]), float(r["haut"])
                m["four_nb"] += 1
                m["four_ok"] += int(bas <= fin <= haut)
            except (TypeError, ValueError):
                pass
    out = []
    for nom, m in par.items():
        out.append({"modele": nom, "blocs": f"{min(m['blocs'])}–{max(m['blocs'])}" if len(m["blocs"]) > 1 else str(min(m["blocs"])),
                    "nb": m["nb"], "attente": m["attente"],
                    "sens": m["justes"] / m["nb"] if m["nb"] else None, "ic": list(wilson(m["justes"], m["nb"])) if m["nb"] else None,
                    "fourchette": m["four_ok"] / m["four_nb"] if m["four_nb"] else None, "four_nb": m["four_nb"]})
    return {"modeles": out, "verification": verifier(), "nb_corrections": len(corrections()), "blocs": chaine()[-60:]}


def publier(dossier_site: str) -> int:
    """Copie le registre (fichiers scellés, chaîne, corrections) dans le site, à l'identique, octet pour octet."""
    if not os.path.isdir(DOSSIER):
        return 0
    cible = os.path.join(dossier_site, "registre")
    os.makedirs(cible, exist_ok=True)
    n = 0
    for nom in os.listdir(DOSSIER):
        if nom.endswith(".csv"):
            shutil.copyfile(os.path.join(DOSSIER, nom), os.path.join(cible, nom))
            n += 1
    return n


JS_VERIF = r"""<script>(function(){
const b=document.getElementById('rg-verif'),o=document.getElementById('rg-sortie');if(!b||!crypto.subtle)return;
const COLS=["bloc","scelle_le","fichier","nb","empreinte_fichier","precedent","modele","note"];
const hex=buf=>[...new Uint8Array(buf)].map(x=>x.toString(16).padStart(2,'0')).join('');
const sha=async d=>hex(await crypto.subtle.digest('SHA-256',d));
function lire(t){const L=[];let r=[],c='',q=false;for(let i=0;i<t.length;i++){const ch=t[i];
 if(q){if(ch=='"'){if(t[i+1]=='"'){c+='"';i++}else q=false}else c+=ch}
 else if(ch=='"')q=true;else if(ch==','){r.push(c);c=''}else if(ch=='\n'){r.push(c);L.push(r);r=[];c=''}else if(ch!='\r')c+=ch}
 if(c||r.length){r.push(c);L.push(r)}return L}
b.onclick=async()=>{b.disabled=true;o.className='rg-sortie';o.textContent='Lecture de la chaîne…';
 try{const t=await (await fetch('registre/chaine.csv',{cache:'no-store'})).text();const L=lire(t),E=L.shift();
  const blocs=L.filter(r=>r.length===E.length).map(r=>Object.fromEntries(E.map((k,i)=>[k,r[i]])));let prec='0'.repeat(64);
  for(const x of blocs){o.textContent=`Bloc ${x.bloc} sur ${blocs.length-1} : ${x.fichier}…`;
   if(x.precedent!==prec)throw `bloc ${x.bloc} : le lien vers le bloc précédent est cassé`;
   const eb=await sha(new TextEncoder().encode(COLS.map(k=>x[k]).join('|')));if(eb!==x.empreinte_bloc)throw `bloc ${x.bloc} : son empreinte ne correspond pas`;
   const f=await fetch('registre/'+encodeURIComponent(x.fichier),{cache:'no-store'});if(!f.ok)throw `bloc ${x.bloc} : fichier ${x.fichier} introuvable`;
   if(await sha(await f.arrayBuffer())!==x.empreinte_fichier)throw `bloc ${x.bloc} : le fichier ${x.fichier} a été modifié`;prec=x.empreinte_bloc}
  o.className='rg-sortie rg-ok';o.textContent=`Vérifié dans ton navigateur : ${blocs.length} bloc${blocs.length>1?'s':''}, aucun fichier modifié, chaîne intacte. Dernière empreinte : ${prec.slice(0,16)}…`}
 catch(e){o.className='rg-sortie rg-ko';o.textContent='Problème détecté : '+e}
 b.disabled=false}})();</script>"""

CSS = """<style>.rg-etat{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.rg-etat b{font-size:20px}
.rg-sortie{margin:12px 0 0;padding:10px 12px;border-radius:8px;background:rgba(127,127,127,.1);min-height:1.4em;font-variant-numeric:tabular-nums}
.rg-sortie:empty{display:none}.rg-ok{background:rgba(68,224,156,.14)}.rg-ko{background:rgba(255,95,95,.16)}
.rg-h{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;word-break:break-all}
.rg-t td,.rg-t th{padding:6px 8px;text-align:left;vertical-align:top}.rg-t th{font-weight:600}.rg-t .m{text-align:right;white-space:nowrap}
@media (prefers-reduced-motion:no-preference){.rg-sortie{transition:background .3s}}</style>"""


def page(seo, base, payload, dossier, csp) -> list:
    R = payload.get("registre") or {}
    V = R.get("verification") or {}
    blocs = R.get("blocs") or []
    from .chiffres import nb_fr as nb
    e, pc = seo._e, (lambda x: "–" if x is None else f"{x * 100:.1f} %".replace(".", ","))
    n_pub = publier(dossier)
    corps = (CSS + "<p class='muted'><a href='resultats.html'>Résultats réels</a></p><h1>Le registre des prévisions</h1>"
             "<p>Chaque soir, les prévisions publiées sont copiées dans un fichier qui n'est <b>plus jamais réécrit</b>, puis scellées : "
             "on calcule leur empreinte numérique (SHA-256) et on l'enchaîne à celle de la veille. Changer un seul chiffre d'un ancien fichier "
             "changerait son empreinte et casserait toute la chaîne. Tu n'as pas besoin de nous croire : tu peux le vérifier toi-même, ici.</p>")
    if not blocs or not n_pub:
        corps += ("<div class='carte'><p style='margin:0'><b>Le registre démarre au prochain calcul du soir.</b> Le premier bloc contiendra "
                  "tout l'historique déjà enregistré, scellé tel quel ; ensuite, un bloc par soir.</p></div>")
    else:
        dernier = blocs[-1]
        corps += ("<div class='carte'><div class='rg-etat'>"
                  + (f"<div><b>{'Chaîne intacte' if V.get('ok') else 'Problème détecté'}</b><br><span class='muted'>contrôlée à la génération de cette page"
                     f" · {V.get('nb_blocs', 0)} blocs · dernier scellé le {e(seo.date_longue(dernier['scelle_le']))}</span></div>")
                  + "<button class='btn' type='button' id='rg-verif'>Vérifier moi-même</button></div>"
                  + (f"<p class='muted' style='margin:8px 0 0'>{e(V.get('probleme') or '')}</p>" if not V.get("ok") else "")
                  + "<p id='rg-sortie' class='rg-sortie' role='status' aria-live='polite'></p></div>")
        M = [m for m in R.get("modeles") or []]
        corps += ("<h2>Performance par modèle</h2><p class='muted'>Seulement les prévisions scellées dont les 20 séances sont passées. "
                  "Une bonne direction : le prix a fini du côté annoncé (hausse si les chances dépassaient 50 sur 100).</p>"
                  "<div class='carte' style='overflow-x:auto'><table class='rg-t'><tr><th>Modèle</th><th>Blocs</th><th class='m'>Vérifiées</th>"
                  "<th class='m'>Bonnes directions</th><th class='m'>Fourchette tenue</th><th class='m'>En attente</th></tr>"
                  + "".join(f"<tr><td>{e(m['modele'])}</td><td>{e(m['blocs'])}</td><td class='m'>{nb(m['nb'])}</td>"
                            f"<td class='m'>{pc(m['sens']) if m['nb'] >= 30 else 'trop peu de cas'}"
                            + (f"<br><span class='muted'>marge {pc(m['ic'][0])} à {pc(m['ic'][1])}</span>" if m.get('ic') and m['nb'] >= 30 and m['ic'][0] is not None else "")
                            + f"</td><td class='m'>{pc(m['fourchette']) if m['four_nb'] >= 30 else '–'}</td><td class='m'>{nb(m['attente'])}</td></tr>"
                            for m in M)
                  + "</table></div><p class='muted'>Les marges sont trop étroites : les prévisions d'un même soir se ressemblent et ne sont pas des cas indépendants.</p>")
        corps += ("<h2>Les derniers blocs</h2><div class='carte' style='overflow-x:auto'><table class='rg-t'><tr><th>Bloc</th><th>Scellé le</th>"
                  "<th class='m'>Prévisions</th><th>Fichier</th><th>Empreinte du bloc</th></tr>"
                  + "".join(f"<tr><td>{e(b['bloc'])}</td><td>{e(b['scelle_le'])}</td><td class='m'>{e(b['nb'])}</td>"
                            f"<td><a href='registre/{e(b['fichier'])}' download>{e(b['fichier'])}</a></td>"
                            f"<td class='rg-h' title='{e(b['empreinte_bloc'])}'>{e(b['empreinte_bloc'][:20])}…</td></tr>" for b in reversed(blocs[-30:]))
                  + "</table></div><p><a href='registre/chaine.csv' download>Toute la chaîne (chaine.csv)</a></p>")
    C = corrections()
    corps += ("<h2>Corrections</h2>" + (
        "<p>Aucune correction à ce jour.</p>" if not C else
        "<div class='carte' style='overflow-x:auto'><table class='rg-t'><tr><th>Corrigé le</th><th>Prévision</th><th>Motif</th></tr>"
        + "".join(f"<tr><td>{e(c.get('corrige_le', ''))}</td><td>{e(c.get('ticker', ''))} du {e(c.get('date', ''))}</td><td>{e(c.get('motif', ''))}</td></tr>" for c in C)
        + "</table></div>")
        + "<p class='muted'>Un fichier scellé n'est jamais modifié. Une erreur découverte après coup (cours faux, titre retiré de la cote) est ajoutée ici, "
          "avec sa date et son motif, et la prévision concernée est retirée des calculs de performance, jamais du fichier.</p>")
    corps += ("<h2>Vérifier sans passer par ce site</h2><p>Télécharge un fichier du jour et calcule son empreinte : sur Mac ou Linux, "
              "<code>shasum -a 256 2026-11-18.csv</code> ; sous Windows, <code>certutil -hashfile 2026-11-18.csv SHA256</code>. "
              "Elle doit être identique à la colonne <i>empreinte_fichier</i> de chaine.csv. L'empreinte d'un bloc est celle du texte "
              "<code>bloc|scelle_le|fichier|nb|empreinte_fichier|precedent|modele|note</code>. Chaque soir, le registre est aussi enregistré "
              "dans l'historique public du dépôt, qui date chaque version.</p>"
              "<p class='muted'>Le bloc 0 contient l'historique d'avant la création du registre, scellé tel quel le jour de sa création : "
              "pour lui, les dates ne sont garanties que par l'historique du dépôt. Projet éducatif, pas un conseil en investissement.</p>" + JS_VERIF)
    chemin = "registre-previsions.html"
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(seo._page(base, f"Registre public des prévisions, vérifiable | {seo.NOM}",
                          "Chaque prévision de l'IA est scellée le soir même par une empreinte SHA-256 enchaînée : impossible à modifier sans que ça se voie. Vérifie-le toi-même.",
                          chemin, corps, csp=csp))
    return [(chemin, "daily", "0.7")]
