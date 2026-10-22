"""Mon bilan privé : combien de fois les IA ont eu raison ?

Ce rapport est QUE pour toi : il est créé dans le dossier « rapports » de ton PC, qui n'est jamais
envoyé sur GitHub ni sur le site. Il compare chaque prévision enregistrée par le site à ce qui
s'est vraiment passé un mois plus tard.

Lancement : double-clique sur mon_bilan_ia.bat   (ou : python mon_bilan_ia.py)
Options : --pas-de-navigateur (n'ouvre pas la page)   --demo (essai avec des données fictives)
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import webbrowser
from datetime import datetime

ICI = os.path.dirname(os.path.abspath(__file__))
os.chdir(ICI)
sys.path.insert(0, ICI)

import numpy as np
import pandas as pd

from bourse_bot import config, data, historique
from bourse_bot.model import wilson

DOSSIER = os.path.join(ICI, "rapports")
PAGE = os.path.join(DOSSIER, "mon_bilan_ia.html")
JOURNAL = os.path.join(DOSSIER, "journal_bilan.csv")
CONFIANT = 0.60   # au-dessus de 60 % (ou en dessous de 40 %), on dit que l'IA est « sûre d'elle »


def dire(msg=""):
    print(msg, flush=True)


# ---------------------------------------------------------------- récupération des prévisions
def _trouver(nom):
    chemin = shutil.which(nom)
    if chemin:
        return chemin
    for c in (rf"C:\Program Files\Git\cmd\{nom}.exe", os.path.expandvars(rf"%LOCALAPPDATA%\Programs\Git\cmd\{nom}.exe")):
        if os.path.exists(c):
            return c
    return None


def recuperer_previsions(demo: bool) -> bool:
    """Le site enregistre ses prévisions sur GitHub chaque soir : on récupère la dernière version."""
    if demo:
        return os.path.exists(historique.FICHIER)
    git = _trouver("git")
    if git and os.path.isdir(os.path.join(ICI, ".git")):
        try:
            r = subprocess.run([git, "pull", "--rebase", "--autostash"], cwd=ICI, capture_output=True, text=True,
                               timeout=180, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if r.returncode == 0:
                dire("✅ Prévisions mises à jour depuis GitHub.")
                return os.path.exists(historique.FICHIER)
        except (OSError, subprocess.SubprocessError):
            pass
    # pas de git : on lit directement le fichier public du dépôt
    try:
        with open(os.path.join(ICI, ".radar_deploy.json"), encoding="utf-8") as f:
            m = json.load(f)
        login, depot = m.get("login"), m.get("depot")
    except (OSError, ValueError):
        login = depot = None
    if login and depot:
        for branche in ("main", "master"):
            url = f"https://raw.githubusercontent.com/{login}/{depot}/{branche}/historique/predictions.csv"
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    contenu = r.read()
                os.makedirs(config.DOSSIER_HISTORIQUE, exist_ok=True)
                with open(historique.FICHIER, "wb") as f:
                    f.write(contenu)
                dire("✅ Prévisions téléchargées depuis GitHub.")
                return True
            except Exception:
                continue
    if os.path.exists(historique.FICHIER):
        dire("⚠️ Impossible de joindre GitHub : j'utilise les prévisions déjà présentes sur ce PC.")
        return True
    return False


# ---------------------------------------------------------------- vérification
def verifier(hist: pd.DataFrame, donnees: dict, horizon: int) -> tuple[pd.DataFrame, int]:
    lignes, attente = [], 0
    for r in hist.itertuples(index=False):
        d = donnees.get(r.ticker)
        if d is None or len(d) == 0:
            continue
        fin, jour_fin = historique._prix_apres(d, r.date, horizon)
        if fin is None:
            attente += 1
            continue
        prix, proba = historique._num(r.prix), historique._num(r.proba)
        if not prix or np.isnan(prix) or np.isnan(proba):
            continue
        reel = fin / prix - 1
        bas, haut = historique._num(getattr(r, "bas", np.nan)), historique._num(getattr(r, "haut", np.nan))
        acc = historique._num(getattr(r, "accord", np.nan))
        lignes.append({
            "date": str(r.date)[:10], "ticker": r.ticker, "type": historique._type(r.ticker), "proba": proba,
            "signal": str(r.signal), "fort": historique._num(getattr(r, "fort", 0)) == 1,
            "reel": reel, "juste": (proba > 0.5) == (reel > 0),
            "dans_fourchette": None if np.isnan(bas) or np.isnan(haut) else bool(bas <= fin <= haut),
            "accord": None if np.isnan(acc) else acc == 1, "fin": str(jour_fin)[:10]})
    return pd.DataFrame(lignes), attente


def taux(s) -> dict | None:
    s = pd.Series(s).dropna().astype(bool)
    if not len(s):
        return None
    bas, haut = wilson(int(s.sum()), len(s))
    return {"ok": int(s.sum()), "n": int(len(s)), "taux": float(s.mean()), "bas": float(bas), "haut": float(haut)}


def analyser(v: pd.DataFrame, attente: int, noms: dict) -> dict:
    v = v.copy()
    v["date_dt"] = pd.to_datetime(v["date"])
    derniere = v["date_dt"].max()
    sure = (v["proba"] >= CONFIANT) | (v["proba"] <= 1 - CONFIANT)
    base_hausse = float((v["reel"] > 0).mean())
    # « toujours dire hausse » : la stratégie paresseuse à battre
    paresseux = max(base_hausse, 1 - base_hausse)
    r = {
        "global": taux(v["juste"]), "attente": attente, "base_hausse": base_hausse, "paresseux": paresseux,
        "premiere": v["date"].min(), "derniere": v["date"].max(), "nb_jours": int(v["date"].nunique()),
        "nb_titres": int(v["ticker"].nunique()),
        "periodes": [(nom, taux(v.loc[v["date_dt"] > derniere - pd.Timedelta(days=j), "juste"]))
                     for nom, j in (("7 derniers jours vérifiés", 7), ("30 derniers jours vérifiés", 30),
                                    ("Depuis le début", 100000))],
        "sure": taux(v.loc[sure, "juste"]), "hesite": taux(v.loc[~sure, "juste"]),
        "forts": taux(v.loc[v["fort"], "reel"] > 0) if v["fort"].any() else None,
        "achat": taux(v.loc[v["signal"].str.startswith("ACHAT"), "reel"] > 0),
        "vente": taux(v.loc[v["signal"].str.startswith("VENTE"), "reel"] < 0),
        "accord": taux(v.loc[v["accord"] == True, "juste"]),      # noqa: E712
        "desaccord": taux(v.loc[v["accord"] == False, "juste"]),  # noqa: E712
        "fourchette": taux(v["dans_fourchette"]),
        "par_type": sorted([(k, taux(g["juste"])) for k, g in v.groupby("type")], key=lambda x: -x[1]["n"]),
        "par_mois": [(k, taux(g["juste"])) for k, g in v.groupby(v["date"].str[:7])],
        "tranches": [],
    }
    for a, b, nom in historique.TRANCHES:
        sel = v[(v["proba"] >= a) & (v["proba"] < b)]
        r["tranches"].append((nom, len(sel), float((sel["reel"] > 0).mean()) if len(sel) else None))
    par_titre = [(t, taux(g["juste"])) for t, g in v.groupby("ticker") if len(g) >= 5]
    par_titre.sort(key=lambda x: x[1]["taux"])
    r["meilleurs_titres"] = [(noms.get(t, t), x) for t, x in par_titre[::-1][:6]]
    r["pires_titres"] = [(noms.get(t, t), x) for t, x in par_titre[:6]]
    # ses plus beaux coups et ses pires erreurs : quand elle était sûre d'elle
    v["ecart"] = (v["proba"] - 0.5).abs()
    s = v[sure].copy()
    s["force"] = s["ecart"] * s["reel"].abs()
    r["beaux"] = s[s["juste"]].nlargest(6, "force").to_dict("records")
    r["erreurs"] = s[~s["juste"]].nlargest(6, "force").to_dict("records")
    for lst in (r["beaux"], r["erreurs"]):
        for x in lst:
            x["nom"] = noms.get(x["ticker"], x["ticker"])
    # série la plus longue de journées « gagnantes » (plus de la moitié des prévisions du jour justes)
    jours = v.groupby("date")["juste"].mean().sort_index() > 0.5
    meilleure = cur = 0
    for ok in jours:
        cur = cur + 1 if ok else 0
        meilleure = max(meilleure, cur)
    r["serie"], r["jours_gagnants"] = meilleure, (int(jours.sum()), int(len(jours)))
    return r


def verdict(r) -> tuple[str, str]:
    g = r["global"]
    if g["n"] < 200 or r["nb_jours"] < 20:
        return ("encore trop tôt", f"Seulement {g['n']} prévisions vérifiées sur {r['nb_jours']} jours : "
                "le hasard peut encore tout expliquer. Il faut au moins 20 jours de prévisions vérifiées pour conclure.")
    if g["bas"] > r["paresseux"]:
        return ("meilleure que le hasard", "Même en comptant la marge d'erreur, les IA font mieux qu'une stratégie "
                "paresseuse (toujours parier sur le sens le plus fréquent).")
    if g["taux"] > r["paresseux"]:
        return ("légèrement mieux, pas prouvé", "Les IA font un peu mieux que la stratégie paresseuse, "
                "mais l'écart reste dans la marge d'erreur : pas encore prouvé.")
    return ("pas mieux que le hasard", "Pour l'instant, les IA ne font pas mieux que la stratégie paresseuse "
            "(toujours parier sur le sens le plus fréquent). Ce n'est pas grave : c'est exactement ce qu'il faut savoir.")


# ---------------------------------------------------------------- journal (évolution d'un bilan à l'autre)
def noter_journal(r) -> pd.DataFrame:
    g = r["global"]
    ligne = pd.DataFrame([{"bilan_du": datetime.now().strftime("%Y-%m-%d %H:%M"), "verifiees": g["n"],
                           "justes": g["ok"], "taux": round(g["taux"], 4)}])
    try:
        j = pd.concat([pd.read_csv(JOURNAL), ligne], ignore_index=True)
    except (OSError, ValueError):
        j = ligne
    j.to_csv(JOURNAL, index=False)
    return j


# ---------------------------------------------------------------- page
def fr(d):
    try:
        return datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(d)


def pc(x, d=0):
    return "–" if x is None else f"{x * 100:.{d}f} %".replace(".", ",")


def barre(t: dict | None, ref: float) -> str:
    if not t:
        return '<span class="vide">pas encore de données</span>'
    w = max(0, min(100, t["taux"] * 100))
    cl = "bon" if t["bas"] > ref else "moyen" if t["taux"] > ref else "faible"
    return (f'<div class="barre" role="img" aria-label="{pc(t["taux"])} de bonnes réponses">'
            f'<div class="rempli {cl}" style="width:{w:.1f}%"></div><div class="ref" style="left:{ref * 100:.1f}%"></div></div>'
            f'<span class="chiffre"><b>{t["ok"]}</b> sur {t["n"]} · <b>{pc(t["taux"])}</b>'
            f' <small>(entre {pc(t["bas"])} et {pc(t["haut"])})</small></span>')


def ligne(nom, t, ref, aide=""):
    a = f'<small class="aide">{html.escape(aide)}</small>' if aide else ""
    return f'<tr><th scope="row">{html.escape(nom)}{a}</th><td>{barre(t, ref)}</td></tr>'


def page(r, journal: pd.DataFrame, demo: bool) -> str:
    g, ref = r["global"], r["paresseux"]
    titre_v, texte_v = verdict(r)
    e = html.escape
    mois = "".join(
        f'<div class="col" title="{k} : {pc(t["taux"])} sur {t["n"]}"><div class="b {"bon" if t["taux"] > ref else "faible"}" '
        f'style="height:{max(4, t["taux"] * 100):.0f}%"></div><span>{k[5:]}/{k[2:4]}</span><b>{pc(t["taux"])}</b></div>'
        for k, t in r["par_mois"])
    coups = lambda lst: "".join(
        f'<li><b>{e(x["nom"])}</b> le {fr(x["date"])} : l\'IA donnait <b>{pc(x["proba"])}</b> de chances de hausse, '
        f'résultat <b class="{"up" if x["reel"] > 0 else "down"}">{"+" if x["reel"] > 0 else ""}{pc(x["reel"], 1)}</b> en un mois.</li>'
        for x in lst) or "<li>Aucun pour l'instant.</li>"
    titres = lambda lst: "".join(f'<li><b>{e(n)}</b> : {t["ok"]} sur {t["n"]} ({pc(t["taux"])})</li>' for n, t in lst) or "<li>–</li>"
    calib = "".join(
        f'<tr><th scope="row">{nom}</th><td>{n}</td><td>{pc(h)}</td></tr>' for nom, n, h in r["tranches"])
    jr = journal.tail(12).iloc[::-1]
    evol = "".join(f'<tr><td>{x.bilan_du}</td><td>{int(x.verifiees)}</td><td>{int(x.justes)}</td><td>{pc(x.taux, 1)}</td></tr>'
                   for x in jr.itertuples())
    jg, jt = r["jours_gagnants"]
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Mon bilan des IA</title><style>
:root{{--bg:#f3f5f8;--carte:#fff;--encre:#0f1b2d;--gris:#56657a;--ligne:#d9e0e8;--bon:#07743f;--moyen:#855c08;--faible:#b42a25;--accent:#1d4fd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0a111d;--carte:#111a29;--encre:#e4ebf5;--gris:#93a2b7;--ligne:#22314a;--bon:#35c27d;--moyen:#e5b453;--faible:#ff6b62;--accent:#7398ff}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--encre);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:980px;margin:0 auto;padding:28px 16px 60px}}h1,h2{{font-family:Georgia,"Times New Roman",serif;font-weight:600;margin:0}}
h1{{font-size:clamp(28px,5vw,42px);line-height:1.1}}h2{{font-size:22px;margin:34px 0 12px}}
.prive{{display:inline-block;background:var(--encre);color:var(--bg);border-radius:6px;padding:3px 10px;font-size:13px;margin-bottom:14px}}
.chapo{{color:var(--gris);max-width:64ch}}.grand{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:24px;margin-top:22px;
background:var(--carte);border:1px solid var(--ligne);border-radius:12px;padding:22px}}@media (max-width:720px){{.grand{{grid-template-columns:1fr}}}}
.score{{font-family:Georgia,serif;font-size:64px;line-height:1;font-weight:600}}.score small{{font-size:22px;color:var(--gris)}}
.verdict b{{font-size:18px}}.carte{{background:var(--carte);border:1px solid var(--ligne);border-radius:12px;padding:6px 18px}}
table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px 6px;border-bottom:1px solid var(--ligne);vertical-align:middle}}
tr:last-child th,tr:last-child td{{border-bottom:0}}th[scope=row]{{font-weight:500;width:34%}}.aide{{display:block;color:var(--gris);font-weight:400}}
.barre{{position:relative;height:10px;background:var(--ligne);border-radius:5px;margin-bottom:5px}}.rempli{{height:100%;border-radius:5px}}
.ref{{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--encre)}}.bon{{background:var(--bon)}}.moyen{{background:var(--moyen)}}.faible{{background:var(--faible)}}
.chiffre small{{color:var(--gris)}}.vide{{color:var(--gris)}}.up{{color:var(--bon)}}.down{{color:var(--faible)}}
.mois{{display:flex;gap:8px;align-items:flex-end;height:190px;padding:16px 4px 0;overflow-x:auto}}.col{{flex:1 0 46px;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end;font-size:12px}}
.col .b{{width:100%;border-radius:4px 4px 0 0}}.col span{{color:var(--gris)}}
.deux{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}@media (max-width:720px){{.deux{{grid-template-columns:1fr}}}}ul{{padding-left:20px}}li{{margin:6px 0}}
.note{{color:var(--gris);font-size:13.5px;max-width:75ch}}
</style></head><body><main>
<span class="prive">Rapport privé · reste sur ce PC, jamais publié{" · DONNÉES FICTIVES" if demo else ""}</span>
<h1>Combien de fois les IA ont eu raison</h1>
<p class="chapo">Chaque prévision du site est comparée à ce qui s'est vraiment passé un mois plus tard. Une prévision est « juste » si
l'IA donnait plus de 50 % de chances de hausse et que le prix a monté, ou moins de 50 % et qu'il a baissé.
Bilan fait le {datetime.now().strftime("%d/%m/%Y à %H:%M")}.</p>

<section class="grand"><div><div class="score">{g["ok"]}<small> fois sur {g["n"]}</small></div>
<p style="margin:8px 0 0;font-size:18px">soit <b>{pc(g["taux"], 1)}</b> de bonnes réponses</p>
<p class="note">Avec la marge d'erreur : entre {pc(g["bas"])} et {pc(g["haut"])}. Prévisions du {fr(r["premiere"])} au {fr(r["derniere"])},
sur {r["nb_titres"]} titres. {r["attente"]} prévisions attendent encore leur résultat.</p></div>
<div class="verdict"><b>Verdict : {e(titre_v)}</b><p>{e(texte_v)}</p>
<p class="note">Repère : pile ou face = 50 %. Toujours parier sur le sens le plus fréquent aurait eu raison <b>{pc(ref, 1)}</b>
des fois (ça a monté {pc(r["base_hausse"])} du temps). Sur les barres, ce repère est le trait noir : il faut le dépasser.</p></div></section>

<h2>Dans le temps</h2><div class="carte"><table>{"".join(ligne(n, t, ref) for n, t in r["periodes"])}</table></div>
<div class="carte" style="margin-top:12px"><div class="mois" aria-label="Taux de bonnes réponses par mois de prévision">{mois}</div>
<p class="note">Journées où plus de la moitié des prévisions étaient justes : {jg} sur {jt}. Meilleure série : {r["serie"]} jours de suite.</p></div>

<h2>Quand peut-on lui faire confiance ?</h2><div class="carte"><table>
{ligne("Quand elle est sûre d'elle", r["sure"], ref, "plus de 60 % ou moins de 40 %")}
{ligne("Quand elle hésite", r["hesite"], ref, "entre 40 et 60 %")}
{ligne("Les deux IA d'accord", r["accord"], ref)}
{ligne("Les deux IA pas d'accord", r["desaccord"], ref)}
{ligne("Signaux forts", r["forts"], ref, "le prix a bien monté")}
{ligne("Conseils « achat »", r["achat"], ref, "le prix a bien monté")}
{ligne("Conseils « vente »", r["vente"], ref, "le prix a bien baissé")}
{ligne("Prix final dans la fourchette", r["fourchette"], 0.8, "promis : 8 fois sur 10")}
</table></div>

<h2>Par marché</h2><div class="carte"><table>{"".join(ligne(n, t, ref) for n, t in r["par_type"])}</table></div>

<h2>Ses probabilités sont-elles honnêtes ?</h2><div class="carte"><table>
<thead><tr><th>Quand l'IA annonçait</th><th>Prévisions</th><th>Ça a vraiment monté</th></tr></thead><tbody>{calib}</tbody></table>
<p class="note">Si l'IA est honnête, la dernière colonne doit monter avec la première : quand elle dit 60 %, ça doit monter environ 6 fois sur 10.</p></div>

<div class="deux"><div><h2>Où elle a le plus raison</h2><div class="carte"><ul>{titres(r["meilleurs_titres"])}</ul></div></div>
<div><h2>Où elle se trompe le plus</h2><div class="carte"><ul>{titres(r["pires_titres"])}</ul></div></div></div>
<p class="note">Titres avec au moins 5 prévisions vérifiées. Sur peu de prévisions, un titre peut briller ou rater par simple chance.</p>

<div class="deux"><div><h2>Ses plus beaux coups</h2><div class="carte"><ul>{coups(r["beaux"])}</ul></div></div>
<div><h2>Ses pires erreurs</h2><div class="carte"><ul>{coups(r["erreurs"])}</ul></div></div></div>

<h2>Évolution de tes bilans</h2><div class="carte"><table><thead><tr><th>Bilan du</th><th>Vérifiées</th><th>Justes</th><th>Taux</th></tr></thead>
<tbody>{evol}</tbody></table></div>

<h2>À savoir pour bien lire</h2><p class="note">Les prévisions d'un même jour sont liées entre elles (quand tout le marché chute,
beaucoup de prévisions ratent ensemble). La vraie marge d'erreur est donc un peu plus large que celle affichée : fie-toi surtout
aux résultats sur plusieurs mois. Ce rapport est rangé dans le dossier « rapports », qui n'est jamais envoyé sur GitHub ni sur le site.</p>
</main></body></html>"""


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(description="Bilan privé : combien de fois les IA ont eu raison.")
    ap.add_argument("--pas-de-navigateur", action="store_true")
    ap.add_argument("--demo", action="store_true", help="essai avec des données fictives")
    args = ap.parse_args()
    data.DEMO = args.demo
    dire("━━ Mon bilan des IA (privé, rien n'est publié)")
    if not recuperer_previsions(args.demo):
        dire("Aucune prévision enregistrée pour l'instant. Le site les enregistre chaque soir :")
        dire("reviens dans un peu plus d'un mois pour voir les premiers résultats.")
        return 1
    hist = pd.read_csv(historique.FICHIER)
    if hist.empty:
        dire("Le fichier des prévisions est vide pour l'instant.")
        return 1
    hist["date"] = hist["date"].astype(str).str[:10]
    tickers = sorted(set(hist["ticker"].astype(str)))
    dire(f"{len(hist)} prévisions trouvées sur {len(tickers)} titres. Téléchargement des cours pour les vérifier…")
    donnees = data.telecharger_plusieurs(tickers, max_age_h=6)
    v, attente = verifier(hist, donnees, config.HORIZON_PREDICTION)
    if v.empty:
        dire(f"Aucune prévision n'a encore atteint son mois d'attente ({attente} en attente). Reviens plus tard !")
        return 0
    noms = {t: n for marche in config.UNIVERS.values() for t, n in marche.items()}
    r = analyser(v, attente, noms)
    os.makedirs(DOSSIER, exist_ok=True)
    journal = noter_journal(r)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(page(r, journal, args.demo))
    g = r["global"]
    titre_v, _ = verdict(r)
    dire()
    dire(f"   Les IA ont eu raison {g['ok']} fois sur {g['n']}  →  {pc(g['taux'], 1)}")
    dire(f"   (marge d'erreur : {pc(g['bas'])} à {pc(g['haut'])} · stratégie paresseuse : {pc(r['paresseux'], 1)})")
    for nom, t in r["periodes"][:2]:
        if t:
            dire(f"   {nom} : {t['ok']} sur {t['n']} ({pc(t['taux'])})")
    dire(f"   Verdict : {titre_v}")
    dire()
    dire(f"Rapport détaillé (privé) : {PAGE}")
    if not args.pas_de_navigateur:
        webbrowser.open("file://" + os.path.abspath(PAGE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
