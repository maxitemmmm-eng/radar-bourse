"""Version 57 : trois pages qui répondent à des recherches fréquentes, avec du vrai contenu mis à jour chaque heure :
- krach-boursier.html : « le radar du risque de krach » (peur des marchés, tendance de fond, risque de chute moyen
  calculé par l'IA, actualités qui parlent de krach ou de bulle) — sans jamais prétendre prédire un krach ;
- actu-bourse.html et actu-bitcoin.html : les derniers titres d'actualité, leur tonalité, et ce que dit le radar.

Et la mémoire quotidienne du marché (historique/marche_jour.csv) : chaque jour, la tonalité des actualités, le nombre
d'articles qui parlent de krach, la peur des marchés et le risque de chute moyen. Quand il y aura assez de jours, on
pourra tester honnêtement si les actualités aident vraiment l'IA (aujourd'hui, elles ne servent que de garde-fou)."""
from __future__ import annotations

import csv
import os
import re
from datetime import datetime

from . import config, seo

NOM = seo.NOM
_e = seo._e
MOTS_KRACH = re.compile(r"\b(krach|crash|bulle|bubble|correction|r[ée]cession|sell-?off|panic|panique|plunge|plonge|"
                        r"tumble|turmoil|meltdown|d[ée]gringol|effondr|collapse|bear market|march[ée] baissier)\w*", re.I)
FICHIER_JOUR = os.path.join(config.DOSSIER_HISTORIQUE, "marche_jour.csv")
CHAMPS = ["date", "articles", "tonalite", "mentions_krach", "vix", "peur_crypto", "au_dessus_200", "chute_moyenne", "chute_base"]


# ----------------------------------------------------------------------------------------------------------------------
# Les chiffres du jour
# ----------------------------------------------------------------------------------------------------------------------
def _toutes_actus(payload):
    vus, out = set(), []
    for a in (payload.get("actus_marche") or []) + [x for t in payload.get("titres", []) for x in (t.get("actus") or [])]:
        cle = str(a.get("titre", "")).lower()[:80]
        if cle and cle not in vus and str(a.get("url", "")).startswith("http"):
            vus.add(cle)
            out.append(a)
    out.sort(key=lambda a: str(a.get("date", "")), reverse=True)
    return out


def _contexte(payload, cle):
    for c in payload.get("contexte") or []:
        if c.get("cle") == cle:
            return c.get("valeur")
    return None


def chiffres(payload) -> dict:
    titres = [t for t in payload.get("titres", []) if t.get("marche") != "tendances"]
    actions = [t for t in titres if t.get("marche") not in ("crypto", "etf")]
    chutes = [(t.get("risque_prevu") or {}).get("chute") for t in actions]
    chutes = [c for c in chutes if isinstance(c, (int, float))]
    base = (((payload.get("modele") or {}).get("risque") or {}).get("chute") or {}).get("base_actions")
    au200 = [t.get("au_dessus_200") for t in titres if t.get("au_dessus_200") is not None]
    actus = _toutes_actus(payload)
    krach = [a for a in actus if MOTS_KRACH.search(str(a.get("titre", "")))]
    tons = [a.get("tonalite") for a in actus if isinstance(a.get("tonalite"), (int, float))]
    a_risque = sorted(((t, (t.get("risque_prevu") or {}).get("chute")) for t in actions
                       if isinstance((t.get("risque_prevu") or {}).get("chute"), (int, float))), key=lambda x: -x[1])
    return {
        "vix": _contexte(payload, "vix"), "peur_crypto": _contexte(payload, "fng"),
        "au_dessus_200": (sum(1 for x in au200 if x) / len(au200)) if au200 else None,
        "chute_moyenne": (sum(chutes) / len(chutes)) if chutes else None, "chute_base": base,
        "nb_actions": len(actions), "a_risque": a_risque[:8],
        "actus": actus, "krach": krach, "tonalite": (sum(tons) / len(tons)) if tons else None,
    }


def niveau_tension(c) -> tuple[str, str]:
    """Une lecture simple et prudente, à partir de deux mesures solides : la peur des marchés (VIX) et le risque de chute
    moyen calculé par l'IA, comparé à son niveau habituel. Ce n'est PAS une prévision de krach."""
    points = 0
    v = c.get("vix")
    if v is not None:
        points += 0 if v < 15 else 1 if v < 22 else 2 if v < 30 else 3
    if c.get("chute_moyenne") is not None and c.get("chute_base"):
        r = c["chute_moyenne"] / c["chute_base"]
        points += 0 if r < 0.9 else 1 if r < 1.2 else 2 if r < 1.6 else 3
    if c.get("au_dessus_200") is not None:
        points += 1 if c["au_dessus_200"] < 0.4 else 0
    if points <= 1:
        return "calme", "Les marchés sont plutôt calmes : la peur est basse et le risque de forte chute est à son niveau habituel, voire en dessous."
    if points <= 3:
        return "normale", "Tension normale : rien d'inhabituel dans les mesures du radar."
    if points <= 5:
        return "élevée", "Tension élevée : la peur des marchés et le risque de forte chute sont au-dessus de la normale."
    return "très élevée", "Tension très élevée : peur forte et risque de chute nettement plus haut que d'habitude. Ce n'est pas une annonce de krach, mais une période où les grosses baisses sont plus fréquentes."


def memoriser(payload) -> None:
    """Une ligne par jour (la dernière mise à jour du jour remplace la précédente)."""
    c = chiffres(payload)
    jour = str(payload.get("date_donnees") or datetime.now().strftime("%Y-%m-%d"))[:10]
    ligne = {"date": jour, "articles": len(c["actus"]), "tonalite": _r(c["tonalite"]), "mentions_krach": len(c["krach"]),
             "vix": _r(c["vix"]), "peur_crypto": _r(c["peur_crypto"]), "au_dessus_200": _r(c["au_dessus_200"]),
             "chute_moyenne": _r(c["chute_moyenne"]), "chute_base": _r(c["chute_base"])}
    lignes = lire_memoire()
    lignes = [l for l in lignes if l.get("date") != jour] + [ligne]
    lignes.sort(key=lambda l: l.get("date", ""))
    os.makedirs(os.path.dirname(FICHIER_JOUR), exist_ok=True)
    with open(FICHIER_JOUR, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS)
        w.writeheader()
        w.writerows(lignes[-2000:])


def lire_memoire() -> list[dict]:
    try:
        with open(FICHIER_JOUR, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _r(x, n=4):
    return "" if x is None else round(float(x), n)


# ----------------------------------------------------------------------------------------------------------------------
# Mise en page
# ----------------------------------------------------------------------------------------------------------------------
def _pct(x, d=0):
    return "–" if x is None else f"{x * 100:.{d}f} %".replace(".", ",")


def _date_actu(a):
    try:
        d = datetime.fromisoformat(str(a.get("date")).replace("Z", "+00:00"))
        return f"{d.day} {seo.MOIS[d.month - 1][:4].rstrip('.')}. {d:%H:%M}"
    except Exception:
        return ""


def _ton(x):
    if not isinstance(x, (int, float)):
        return ""
    return "🟢 plutôt positif" if x > 0.15 else "🔴 plutôt négatif" if x < -0.15 else "⚪ neutre"


def _liste_actus(actus, n=12):
    if not actus:
        return "<p class='muted'>Pas d'actualité récupérée lors de la dernière mise à jour.</p>"
    return "<ul>" + "".join(
        f"<li><a href='{_e(a['url'])}' target='_blank' rel='noopener nofollow'>{_e(a.get('titre', ''))}</a>"
        f" <span class='muted'>· {_e(a.get('source', ''))} · {_date_actu(a)}{' · ' + _ton(a.get('tonalite')) if _ton(a.get('tonalite')) else ''}</span></li>"
        for a in actus[:n]) + "</ul>"


def _faq_html(faq):
    return "<h2>Questions fréquentes</h2>" + "".join(f"<h3>{_e(q)}</h3><p>{r}</p>" for q, r in faq)


def _faq_jl(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                                                "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for q, r in faq]}


def _maj(payload):
    return seo.date_longue(str(payload.get("date_donnees") or datetime.now().strftime("%Y-%m-%d"))[:10])


def _page_krach(base, payload, csp):
    chemin = "krach-boursier.html"
    c = chiffres(payload)
    niv, phrase = niveau_tension(c)
    v, f = c["vix"], c["peur_crypto"]
    lignes_mesures = [
        ("Peur des marchés (VIX)", "–" if v is None else f"{v:.1f}".replace(".", ","),
         "Sous 15 : calme. Au-dessus de 30 : forte nervosité. Il monte quand les investisseurs achètent des protections contre la baisse."),
        ("Risque de forte chute moyen (actions)", _pct(c["chute_moyenne"], 1),
         f"Probabilité moyenne, calculée par l'IA, qu'une action perde plus de 10 % dans le mois. D'habitude : {_pct(c['chute_base'], 1)}."),
        ("Titres au-dessus de leur moyenne 200 jours", _pct(c["au_dessus_200"]),
         "La part des titres suivis en tendance de fond haussière. Sous 40 %, le marché est globalement fragile."),
        ("Sentiment crypto (Fear & Greed)", "–" if f is None else f"{f:.0f} / 100", "0 = peur extrême, 100 = avidité extrême."),
        ("Articles qui parlent de krach, de bulle ou de chute", f"{len(c['krach'])} sur {len(c['actus'])}",
         "Parmi les titres d'actualité lus par le radar ces derniers jours."),
    ]
    mesures = "<table><tbody>" + "".join(f"<tr><td><b>{_e(a)}</b><br><span class='muted'>{_e(x)}</span></td><td>{_e(b)}</td></tr>"
                                         for a, b, x in lignes_mesures) + "</tbody></table>"
    risque = ("<ol>" + "".join(f"<li><a href='titres/{seo.slug(t['ticker'])}.html'>{_e(t['nom'])}</a> : {_pct(p)} de risque de perdre plus de 10 % en un mois</li>"
                               for t, p in c["a_risque"]) + "</ol>") if c["a_risque"] else ""
    memoire = lire_memoire()[-14:]
    histo = ("<table><thead><tr><th>Jour</th><th>VIX</th><th>Risque de chute moyen</th><th>Articles « krach »</th></tr></thead><tbody>"
             + "".join(f"<tr><td>{_e(l['date'])}</td><td>{_e(str(l.get('vix') or '–'))}</td>"
                       f"<td>{_pct(float(l['chute_moyenne']), 1) if l.get('chute_moyenne') else '–'}</td><td>{_e(str(l.get('mentions_krach') or 0))}</td></tr>"
                       for l in reversed(memoire)) + "</tbody></table>") if len(memoire) >= 2 else ""
    faq = [
        ("Un krach boursier est-il prévu ?", "Personne ne peut annoncer un krach à l'avance de façon fiable : ni les experts, ni les IA. "
         "Les krachs arrivent souvent par surprise. Ce que l'on peut mesurer, c'est la <b>tension</b> du marché (peur, risque de forte chute), "
         "qui rend les grosses baisses plus ou moins fréquentes. C'est ce que montre cette page, mise à jour chaque heure."),
        ("L'IA de Radar Bourse peut-elle prédire un krach ?", "Non. Elle prévoit bien l'agitation des prix et le risque qu'un titre perde plus de 10 % "
         "en un mois (testé sur des années qu'elle n'avait jamais vues), mais un krach de tout le marché est un événement rare : il n'y en a pas "
         "assez dans l'histoire pour apprendre à les prévoir de façon prouvée. Voir la <a href='fiche-technique-ia.html'>fiche technique de l'IA</a>."),
        ("Y a-t-il une bulle de l'IA en Bourse ?", "Beaucoup d'articles en parlent. Une bulle ne se reconnaît vraiment qu'après coup. Le radar ne donne pas "
         "d'avis sur la question ; il montre si la tension du marché et le risque de forte chute sont au-dessus de leur niveau habituel, "
         "et quels titres sont les plus exposés."),
        ("Que faire si un krach arrive ?", "Ce site ne donne pas de conseil personnel. Les principes connus des débutants : ne jamais investir l'argent "
         "dont on aura besoin bientôt, répartir son argent sur plusieurs placements, et éviter de vendre dans la panique. "
         "Voir les <a href='guides.html'>guides pour débuter</a>."),
    ]
    corps = (f"<h1>Krach boursier : le radar du risque, aujourd'hui</h1>"
             f"<p class='muted'>Mis à jour chaque heure · dernières données du {_maj(payload)}</p>"
             f"<div class='carte'><p style='margin:0'><b>Tension du marché : {_e(niv)}.</b> {_e(phrase)}</p></div>"
             "<p><b>Honnêtement :</b> personne ne sait prédire un krach. Cette page ne l'annonce pas ; elle rassemble les mesures qui montrent "
             "si le marché est calme ou tendu, et les actualités qui en parlent.</p>"
             f"<h2>Les mesures du jour</h2>{mesures}"
             + (f"<h2>Les actions les plus exposées à une forte chute</h2><p>Selon l'IA, sur le mois qui vient :</p>{risque}"
                "<p><a href='suivi-chute.html'>Ces alertes ont-elles été justes par le passé ?</a></p>" if risque else "")
             + f"<h2>Ce que disent les actualités</h2>{_liste_actus(c['krach'] or c['actus'], 10)}"
             + (f"<h2>Les 14 derniers jours</h2>{histo}" if histo else "")
             + _faq_html(faq)
             + "<p>Pour comprendre : <a href='guides/krach-boursier.html'>qu'est-ce qu'un krach boursier ?</a> · "
               "<a href='guides/que-faire-krach.html'>que faire en cas de krach ?</a></p>"
             + "<p>Voir aussi : <a href='actu-bourse.html'>actu bourse</a> · <a href='actu-bitcoin.html'>actu bitcoin</a> · "
               "<a href='classements/risque-de-chute.html'>classement du risque de chute</a> · <a href='index.html'>l'appli Radar Bourse</a></p>")
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": "Krach boursier : le radar du risque", "url": url, "inLanguage": "fr-FR",
         "dateModified": datetime.now().isoformat(timespec="minutes")},
        _faq_jl(faq), seo._jsonld_fil(base, [(NOM, ""), ("Krach boursier", chemin)])]}
    return chemin, seo._page(base, f"Krach boursier : risque de krach aujourd'hui, le radar en direct | {NOM}",
                             "Krach boursier : la tension du marché mesurée chaque heure (peur des marchés, risque de forte chute calculé par l'IA, "
                             "actualités sur le krach et la bulle). Sans fausse promesse.", chemin, corps, jl, csp=csp)


def _resume_titre(t):
    if not t:
        return ""
    r = t.get("risque_prevu") or {}
    var = (t.get("perf") or {}).get("1 jour")
    morceaux = [f"<b>{_e(t['nom'])}</b> : {_e(seo._px(t['prix'], t.get('devise', '')))}"]
    if isinstance(var, (int, float)):
        morceaux.append(f"{var * 100:+.2f} % sur la journée".replace(".", ","))
    if isinstance(r.get("mouvement"), (int, float)):
        morceaux.append(f"mouvement typique prévu sur un mois : ±{r['mouvement'] * 100:.0f} %")
    if isinstance(r.get("chute"), (int, float)):
        morceaux.append(f"risque de perdre plus de 10 % en un mois : {_pct(r['chute'])}")
    return "<p>" + " · ".join(morceaux) + f" — <a href='titres/{seo.slug(t['ticker'])}.html'>analyse complète</a></p>"


def _page_actu(base, payload, csp, crypto: bool):
    chemin = "actu-bitcoin.html" if crypto else "actu-bourse.html"
    titres = {t["ticker"]: t for t in payload.get("titres", [])}
    toutes = _toutes_actus(payload)
    if crypto:
        cryptos = {t for t, x in titres.items() if x.get("marche") == "crypto"}
        actus = [a for t in ("BTC-USD", "ETH-USD", "SOL-USD") if t in titres for a in (titres[t].get("actus") or [])]
        actus += [a for t in cryptos for a in (titres[t].get("actus") or [])]
        vus, propres = set(), []
        for a in sorted(actus, key=lambda a: str(a.get("date", "")), reverse=True):
            k = str(a.get("titre", "")).lower()[:80]
            if k not in vus and str(a.get("url", "")).startswith("http"):
                vus.add(k)
                propres.append(a)
        actus = propres
        tete = _resume_titre(titres.get("BTC-USD")) + _resume_titre(titres.get("ETH-USD"))
        h1, titre_page = "Actu bitcoin et crypto : les dernières nouvelles, lues par le radar", f"Actu bitcoin : dernières nouvelles crypto et prévisions | {NOM}"
        desc = "Actu bitcoin et crypto mise à jour chaque heure : derniers titres d'actualité, leur tonalité, et ce que prévoit le radar IA pour le bitcoin."
    else:
        actus = toutes
        indices = payload.get("indices") or []
        tete = ("<ul>" + "".join(f"<li><b>{_e(i['nom'])}</b> : {(i.get('var_jour') or 0) * 100:+.2f} % aujourd'hui</li>".replace(".", ",")
                                 for i in indices if isinstance(i.get("var_jour"), (int, float))) + "</ul>") if indices else ""
        h1, titre_page = "Actu bourse : les dernières nouvelles des marchés, lues par le radar", f"Actu bourse : dernières nouvelles des marchés aujourd'hui | {NOM}"
        desc = "Actu bourse mise à jour chaque heure : derniers titres d'actualité sur les actions, le CAC 40 et Wall Street, leur tonalité, et la tension du marché."
    tons = [a.get("tonalite") for a in actus if isinstance(a.get("tonalite"), (int, float))]
    ton = (f"<p>Tonalité moyenne des titres récents : <b>{_ton(sum(tons) / len(tons))}</b> "
           f"({len(tons)} articles). Estimée automatiquement à partir des titres ; elle n'entre pas dans les prévisions de l'IA.</p>") if tons else ""
    c = chiffres(payload)
    niv, _ = niveau_tension(c)
    corps = (f"<h1>{_e(h1)}</h1><p class='muted'>Mis à jour chaque heure · dernières données du {_maj(payload)}</p>"
             f"<h2>{'Le bitcoin aujourd' + chr(39) + 'hui' if crypto else 'Les marchés aujourd' + chr(39) + 'hui'}</h2>{tete}"
             f"<p>Tension du marché selon le radar : <b>{_e(niv)}</b> (<a href='krach-boursier.html'>voir le radar du risque de krach</a>).</p>"
             f"<h2>Les dernières actualités</h2>{ton}{_liste_actus(actus, 20)}"
             "<p class='muted'>Les titres viennent de sources publiques (souvent en anglais) ; Radar Bourse n'en est pas l'auteur. "
             "Une actualité n'est pas un conseil d'achat ou de vente.</p>"
             + ("<p>Voir aussi : <a href='titres/btc-usd.html'>prévision bitcoin</a> · <a href='outils/convertisseur.html'>convertisseur bitcoin euro</a> · "
                "<a href='actu-bourse.html'>actu bourse</a> · <a href='krach-boursier.html'>krach boursier</a></p>" if crypto else
                "<p>Voir aussi : <a href='titres.html'>prévisions par titre</a> · <a href='point.html'>le point du jour</a> · "
                "<a href='actu-bitcoin.html'>actu bitcoin</a> · <a href='krach-boursier.html'>krach boursier</a></p>"))
    url = (base + chemin) if base else None
    jl = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": h1, "url": url, "inLanguage": "fr-FR", "dateModified": datetime.now().isoformat(timespec="minutes")},
        seo._jsonld_fil(base, [(NOM, ""), ("Actu bitcoin" if crypto else "Actu bourse", chemin)])]}
    return chemin, seo._page(base, titre_page, desc, chemin, corps, jl, csp=csp)


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    try:
        memoriser(payload)
    except Exception as e:
        print(f"Mémoire du marché non enregistrée : {e}")
    urls = []
    for chemin, page in (_page_krach(base, payload, csp), _page_actu(base, payload, csp, False), _page_actu(base, payload, csp, True)):
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((chemin, "hourly", "0.8"))
    return urls
