"""Version 68 : pages « prédiction » pour Google (prédiction crypto, prédiction bitcoin, prédiction bourse…).

Les gens tapent « prédiction bitcoin », « bitcoin va-t-il monter », « prédiction bourse » : ces pages répondent
directement, avec l'avis de l'IA pour chaque titre (toujours un sens : hausse ou baisse, avec sa confiance),
et renvoient vers la fiche complète. Tout est recalculé à chaque mise à jour, sans rien promettre.
"""
from __future__ import annotations

import os
from datetime import datetime

from .hebdo import avis_ia, barres

CRYPTOS_VEDETTES = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD", "DOGE-USD", "ADA-USD"]


def _ligne(seo, t, prefixe=""):
    e, slug, aff = seo._e, seo.slug, seo.aff_tk
    p, sens, conf = avis_ia(t)
    if p is None:
        return ""
    ch = round((p if sens > 0 else 1 - p) * 100)
    fl = "↑ hausse" if sens > 0 else "↓ baisse"
    rp = t.get("risque_prevu") or {}
    return (f"<tr><td><a href='{prefixe}titres/{slug(t['ticker'])}.html'>{e(t['nom'])}</a> "
            f"<span class='muted'>{e(aff(t['ticker']))}</span></td>"
            f"<td class='m'>{seo._px(t['prix'], t['devise'])}</td>"
            f"<td class='m {'up' if sens > 0 else 'down'}'><b>{fl}</b></td>"
            f"<td class='m'>{ch}/100</td><td>{e(conf)}</td>"
            f"<td class='m'>{('±' + str(round(rp['mouvement'] * 100)) + ' %') if rp.get('mouvement') else '—'}</td></tr>")


def _tableau(seo, items, legende, prefixe=""):
    return ("<div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='" + seo._e(legende) + "'><table>"
            "<tr><th>Titre</th><th>Cours</th><th>Avis de l'IA</th><th>Chances</th><th>Confiance</th>"
            "<th title='De combien le cours peut bouger le mois prochain'>Agitation prévue</th></tr>"
            + "".join(_ligne(seo, t, prefixe) for t in items) + "</table></div>")


def _graph(seo, items, titre, note):
    lignes = []
    for t in items:
        p, sens, _ = avis_ia(t)
        if p is not None:
            lignes.append((seo._e(t["nom"]), p - .5))
    return barres(lignes, fmt=lambda v: f"{round((.5 + v) * 100)} % ↑" if v >= 0 else f"{round((.5 - v) * 100)} % ↓",
                  titre=titre, note=note)


def _faq_html(faq):
    return ("<h2>Questions fréquentes</h2>" + "".join(f"<h3>{q}</h3><p>{r}</p>" for q, r in faq))


def _faq_jsonld(faq):
    import re
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for q, r in faq]}


def _phrase(seo, t):
    p, sens, conf = avis_ia(t)
    if p is None:
        return ""
    ch = round((p if sens > 0 else 1 - p) * 100)
    return (f"l'IA voit <b>{seo._e(t['nom'])}</b> <b class='{'up' if sens > 0 else 'down'}'>{'à la hausse ↑' if sens > 0 else 'à la baisse ↓'}</b> "
            f"sur un mois ({ch} chances sur 100, {conf.replace('confiance ', '')} confiance)".replace("faible confiance", "confiance faible")
            .replace("moyenne confiance", "confiance moyenne").replace("forte confiance", "confiance forte"))


AVERTISSEMENT = ("<p class='muted'>L'avis de l'IA donne toujours un sens (hausse ou baisse) avec sa confiance. Sur le sens du prix, "
                 "elle se trompe souvent : ce qu'elle prévoit le mieux, c'est l'agitation (<a href='{p}resultats.html'>résultats réels</a>, "
                 "<a href='{p}avis-surs-verifies.html'>avis vérifiés en public</a>). Projet éducatif, pas un conseil en investissement.</p>")


def generer(seo, base, payload, dossier, csp, date) -> list:
    titres = [t for t in payload.get("titres", []) if t.get("prix") and avis_ia(t)[0] is not None]
    if not titres:
        return []
    e = seo._e
    m = datetime.now()
    mois_an = f"{seo.MOIS[m.month - 1]} {m.year}"
    faits = []
    est_crypto = lambda t: t.get("marche") == "crypto" or t["ticker"].endswith("-USD")

    # 1. Prédiction crypto
    cryptos = [t for t in titres if est_crypto(t)]
    if len(cryptos) >= 3:
        par_tk = {t["ticker"]: t for t in cryptos}
        vedettes = [par_tk[k] for k in CRYPTOS_VEDETTES if k in par_tk]
        autres = sorted([t for t in cryptos if t["ticker"] not in CRYPTOS_VEDETTES], key=lambda t: -avis_ia(t)[0])
        hausse = sum(1 for t in cryptos if avis_ia(t)[1] > 0)
        btc = par_tk.get("BTC-USD")
        eth = par_tk.get("ETH-USD")
        intro = (f"<p>Pour le mois qui vient, l'IA voit <b>{hausse} cryptos sur {len(cryptos)}</b> à la hausse "
                 f"et <b>{len(cryptos) - hausse}</b> à la baisse. " + (f"En résumé, {_phrase(seo, btc)}." if btc else "") + "</p>")
        faq = []
        if btc:
            p, sens, conf = avis_ia(btc)
            faq.append((f"Le Bitcoin va-t-il monter en {mois_an} ?",
                        f"Aujourd'hui, {_phrase(seo, btc)}. Personne ne peut le savoir avec certitude : c'est une probabilité, "
                        f"mesurée sur des années que l'IA n'avait jamais vues. <a href='titres/{seo.slug('BTC-USD')}.html'>Voir la prédiction Bitcoin complète</a>."))
            faq.append((f"Quelle est la prédiction Bitcoin pour {mois_an} ?",
                        f"Cours au {e(date)} : {seo._px(btc['prix'], btc['devise'])}. "
                        + (f"L'IA prévoit une agitation d'environ ±{round(btc['risque_prevu']['mouvement'] * 100)} % sur un mois. "
                           if (btc.get('risque_prevu') or {}).get('mouvement') else "")
                        + f"Pour le sens : {_phrase(seo, btc)}."))
        if eth:
            faq.append((f"Ethereum va-t-il monter en {mois_an} ?", f"Aujourd'hui, {_phrase(seo, eth)}."))
        faq.append(("Quelle crypto va monter ce mois-ci selon l'IA ?",
                    "Les cryptos avec le plus de chances de hausse selon l'IA aujourd'hui : "
                    + ", ".join(f"{e(t['nom'])} ({round(avis_ia(t)[0] * 100)}/100)" for t in sorted(cryptos, key=lambda t: -avis_ia(t)[0])[:3])
                    + ". Ce n'est pas un conseil d'achat : la crypto est très risquée."))
        corps = (f"<h1>Prédiction crypto {e(mois_an)} : Bitcoin, Ethereum… hausse ou baisse ?</h1>"
                 f"<p class='muted'>Avis de l'IA mis à jour automatiquement · cours au {e(date)}</p>{intro}"
                 + _graph(seo, vedettes or cryptos[:8], "Les grandes cryptos : chances selon l'IA",
                          "Vert : l'IA penche pour la hausse. Rouge : pour la baisse. Plus la barre est longue, plus l'avis est marqué.")
                 + "<h2>Les grandes cryptos</h2>" + _tableau(seo, vedettes, "Prédiction des grandes cryptos")
                 + ("<h2>Toutes les autres cryptos suivies</h2>" + _tableau(seo, autres, "Prédiction des autres cryptos") if autres else "")
                 + _faq_html(faq) + AVERTISSEMENT.format(p="")
                 + "<p><a class='btn' href='prediction-bourse.html'>Prédiction bourse (actions)</a> "
                   "<a class='btn' href='actu-bitcoin.html'>Actu bitcoin</a></p>")
        chemin = "prediction-crypto.html"
        jl = seo._jsonld_liste(base, f"Prédiction crypto {mois_an}", chemin,
                               [(t["nom"], f"titres/{seo.slug(t['ticker'])}.html") for t in vedettes + autres])
        jl["@graph"].append(_faq_jsonld(faq))
        titre = f"Prédiction crypto {mois_an} : Bitcoin, Ethereum, hausse ou baisse ? | {seo.NOM}"
        desc = (f"Prédiction Bitcoin, Ethereum, Solana… pour {mois_an} : l'avis de l'IA (hausse ou baisse, chances sur 100) "
                "et l'agitation prévue, mis à jour automatiquement. Gratuit, résultats vérifiés.")
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(seo._page(base, titre, seo.desc_courte(desc), chemin, corps, jl, csp=csp,
                              mots=f"prédiction crypto, prédiction bitcoin, prévision bitcoin, bitcoin va-t-il monter, prédiction ethereum, "
                                   f"crypto qui va monter, prédiction crypto {m.year}, prévision crypto {mois_an}"))
        faits.append(chemin)

    # 2. Prédiction bourse (actions)
    actions = [t for t in titres if not est_crypto(t) and t.get("marche") not in ("etf", "tendances")]
    if len(actions) >= 10:
        tri = sorted(actions, key=lambda t: -avis_ia(t)[0])
        haut, bas = tri[:15], list(reversed(tri[-15:]))
        hausse = sum(1 for t in actions if avis_ia(t)[1] > 0)
        indices = [t for t in titres if t["ticker"].startswith("^")]
        phr_ind = "".join(f"<li>{_phrase(seo, t)[0].upper() + _phrase(seo, t)[1:]}.</li>" for t in indices[:5] if _phrase(seo, t))
        faq = [("Quelles actions vont monter ce mois-ci selon l'IA ?",
                "Les actions avec le plus de chances de hausse selon l'IA aujourd'hui : "
                + ", ".join(f"{e(t['nom'])} ({round(avis_ia(t)[0] * 100)}/100)" for t in haut[:5])
                + ". Ce sont des probabilités, pas des certitudes ni des conseils d'achat."),
               ("La Bourse va-t-elle monter ou baisser ?",
                f"Sur les {len(actions)} actions suivies, l'IA en voit <b>{hausse}</b> à la hausse et <b>{len(actions) - hausse}</b> à la baisse "
                f"pour le mois qui vient (cours au {e(date)}).")]
        cac = next((t for t in indices if t["ticker"] in ("^FCHI",)), None)
        if cac:
            faq.append((f"Le CAC 40 va-t-il monter en {mois_an} ?", f"Aujourd'hui, {_phrase(seo, cac)}."))
        corps = (f"<h1>Prédiction bourse {e(mois_an)} : les actions que l'IA voit monter ou baisser</h1>"
                 f"<p class='muted'>Avis de l'IA mis à jour automatiquement · cours au {e(date)}</p>"
                 f"<p>Sur <b>{len(actions)}</b> actions suivies (France, Europe, États-Unis, Asie), l'IA en voit <b>{hausse}</b> à la hausse "
                 f"et <b>{len(actions) - hausse}</b> à la baisse pour le mois qui vient.</p>"
                 + (f"<h2>Les grands indices</h2><ul>{phr_ind}</ul>" if phr_ind else "")
                 + _graph(seo, haut[:8] + bas[:8][::-1], "Les avis les plus marqués de l'IA", "Vert : hausse. Rouge : baisse.")
                 + "<h2>Les 15 actions que l'IA voit le plus à la hausse</h2>" + _tableau(seo, haut, "Actions vues à la hausse")
                 + "<h2>Les 15 actions que l'IA voit le plus à la baisse</h2>" + _tableau(seo, bas, "Actions vues à la baisse")
                 + "<p><a class='btn' href='toutes-les-actions.html'>Toutes les actions (2 000+)</a> "
                   "<a class='btn' href='themes.html'>Par thème</a> <a class='btn' href='prediction-crypto.html'>Prédiction crypto</a></p>"
                 + _faq_html(faq) + AVERTISSEMENT.format(p=""))
        chemin = "prediction-bourse.html"
        jl = seo._jsonld_liste(base, f"Prédiction bourse {mois_an}", chemin,
                               [(t["nom"], f"titres/{seo.slug(t['ticker'])}.html") for t in haut + bas])
        jl["@graph"].append(_faq_jsonld(faq))
        titre = f"Prédiction bourse {mois_an} : actions en hausse ou en baisse | {seo.NOM}"
        desc = (f"Prédiction bourse {mois_an} : les actions que l'IA voit monter ou baisser le mois prochain, avec leurs chances sur 100, "
                "le CAC 40 et les grands indices. Gratuit, mis à jour automatiquement.")
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(seo._page(base, titre, seo.desc_courte(desc), chemin, corps, jl, csp=csp,
                              mots=f"prédiction bourse, prévision bourse, actions qui vont monter, prédiction action, prédiction CAC 40, "
                                   f"bourse va-t-elle monter, prévision bourse {mois_an}, prédiction bourse {m.year}"))
        faits.append(chemin)
    return faits
