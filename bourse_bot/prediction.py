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
                              alternates={"fr": chemin, "en": "en/crypto-prediction.html", "x-default": chemin},
                              mots=f"prédiction crypto, prédiction bitcoin, prévision bitcoin, bitcoin va-t-il monter, prédiction ethereum, "
                                   f"crypto qui va monter, prédiction crypto {m.year}, prévision crypto {mois_an}, prédiction bitcoin IA, crypto qui va exploser avis honnête, "
                                   f"faut-il acheter du bitcoin maintenant, volatilité crypto prévision, site prédiction crypto sans inscription"))
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
                              alternates={"fr": chemin, "en": "en/stock-market-prediction.html", "x-default": chemin},
                              mots=f"prédiction bourse, prévision bourse, actions qui vont monter, prédiction action, prédiction CAC 40, "
                                   f"bourse va-t-elle monter, prévision bourse {mois_an}, prédiction bourse {m.year}, prévision action IA gratuite, IA bourse fiable, "
                                   f"prédiction cours action demain, action qui va monter cette semaine, quelle action acheter en ce moment avis, "
                                   f"prévision CAC 40 semaine prochaine, est-ce que la bourse va baisser, site prédiction bourse sans inscription"))
        faits.append(chemin)
    return faits


# ---------------------------------------------------------------------------------------------------------------
# Version 68.1 : les mêmes pages en anglais (« bitcoin price prediction », « stock market prediction »)
# ---------------------------------------------------------------------------------------------------------------
LIB_CONF_EN = {"faible": "low", "moyenne": "medium", "forte": "high"}


def _ligne_en(seo, t):
    e, slug, aff = seo._e, seo.slug, seo.aff_tk
    p, sens, conf = avis_ia(t)
    if p is None:
        return ""
    ch = round((p if sens > 0 else 1 - p) * 100)
    rp = t.get("risque_prevu") or {}
    return (f"<tr><td><a href='stocks/{slug(t['ticker'])}.html'>{e(t['nom'])}</a> <span class='muted'>{e(aff(t['ticker']))}</span></td>"
            f"<td class='m'>{seo._px(t['prix'], t['devise'])}</td>"
            f"<td class='m {'up' if sens > 0 else 'down'}'><b>{'↑ up' if sens > 0 else '↓ down'}</b></td>"
            f"<td class='m'>{ch}/100</td><td>{LIB_CONF_EN[conf]}</td>"
            f"<td class='m'>{('±' + str(round(rp['mouvement'] * 100)) + '%') if rp.get('mouvement') else '—'}</td></tr>")


def _tableau_en(seo, items, legende):
    return ("<div class='carte' style='overflow-x:auto' tabindex='0' role='region' aria-label='" + seo._e(legende) + "'><table>"
            "<tr><th>Asset</th><th>Price</th><th>AI view</th><th>Chances</th><th>Confidence</th><th>Expected swing</th></tr>"
            + "".join(_ligne_en(seo, t) for t in items) + "</table></div>")


def _phrase_en(seo, t):
    p, sens, conf = avis_ia(t)
    if p is None:
        return ""
    ch = round((p if sens > 0 else 1 - p) * 100)
    return (f"the AI sees <b>{seo._e(t['nom'])}</b> <b class='{'up' if sens > 0 else 'down'}'>{'going up ↑' if sens > 0 else 'going down ↓'}</b> "
            f"over one month ({ch} chances out of 100, {LIB_CONF_EN[conf]} confidence)")


def generer_en(seo, anglais, base, payload, dossier, csp, date) -> list:
    titres = [t for t in payload.get("titres", []) if t.get("prix") and avis_ia(t)[0] is not None]
    if not titres:
        return []
    os.makedirs(os.path.join(dossier, "en"), exist_ok=True)
    m = datetime.now()
    mois_an = m.strftime("%B %Y")
    est_crypto = lambda t: t.get("marche") == "crypto" or t["ticker"].endswith("-USD")
    note = ("<p class='muted'>The AI always gives a direction (up or down) with its confidence. On price direction it is often wrong: "
            "what it forecasts best is volatility (<a href='verified-calls.html'>calls verified in public</a>). "
            "Educational project, not investment advice.</p>")
    graphe = lambda items, titre: barres([(seo._e(t["nom"]), avis_ia(t)[0] - .5) for t in items], titre=titre,
                                         fmt=lambda v: f"{round((.5 + v) * 100)}% ↑" if v >= 0 else f"{round((.5 - v) * 100)}% ↓",
                                         note="Green: the AI leans up. Red: down.")
    faits = []
    cryptos = [t for t in titres if est_crypto(t)]
    if len(cryptos) >= 3:
        par_tk = {t["ticker"]: t for t in cryptos}
        vedettes = [par_tk[k] for k in CRYPTOS_VEDETTES if k in par_tk]
        autres = sorted([t for t in cryptos if t["ticker"] not in CRYPTOS_VEDETTES], key=lambda t: -avis_ia(t)[0])
        hausse = sum(1 for t in cryptos if avis_ia(t)[1] > 0)
        btc = par_tk.get("BTC-USD")
        faq = []
        if btc:
            faq.append((f"Will Bitcoin go up in {mois_an}?", f"Today, {_phrase_en(seo, btc)}. Nobody can know for sure: it is a probability, "
                        "measured on years the AI had never seen."))
        faq.append(("Which crypto will go up this month according to the AI?",
                    "Highest chances of a rise today: " + ", ".join(f"{seo._e(t['nom'])} ({round(avis_ia(t)[0] * 100)}/100)"
                                                                    for t in sorted(cryptos, key=lambda t: -avis_ia(t)[0])[:3])
                    + ". Not buying advice: crypto is very risky."))
        corps = (f"<h1>Crypto price prediction {seo._e(mois_an)}: Bitcoin, Ethereum… up or down?</h1>"
                 f"<p class='muted'>AI view updated automatically · prices as of {seo._e(date)}</p>"
                 f"<p>For the coming month, the AI sees <b>{hausse} of {len(cryptos)} cryptos</b> going up and <b>{len(cryptos) - hausse}</b> going down."
                 + (f" In short, {_phrase_en(seo, btc)}." if btc else "") + "</p>"
                 + graphe(vedettes or cryptos[:8], "Major cryptos: chances according to the AI")
                 + "<h2>Major cryptos</h2>" + _tableau_en(seo, vedettes, "Major crypto predictions")
                 + ("<h2>All other cryptos tracked</h2>" + _tableau_en(seo, autres, "Other crypto predictions") if autres else "")
                 + _faq_html(faq).replace("Questions fréquentes", "FAQ") + note
                 + "<p><a class='btn' href='stock-market-prediction.html'>Stock market prediction</a></p>")
        chemin = "en/crypto-prediction.html"
        alt = {"fr": "prediction-crypto.html", "en": chemin, "x-default": "prediction-crypto.html"}
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(anglais._page(base, f"Crypto price prediction {mois_an}: Bitcoin, Ethereum, up or down? | {seo.NOM}",
                                  f"Bitcoin, Ethereum, Solana price prediction for {mois_an}: the AI's view (up or down, chances out of 100) "
                                  "and expected volatility, updated automatically. Free, results verified in public.",
                                  chemin, corps, csp, alt,
                                  mots="bitcoin price prediction, crypto price prediction, will bitcoin go up, ethereum price prediction, "
                                       f"bitcoin forecast {m.year}, crypto forecast {mois_an}"))
        faits.append(chemin)
    actions = [t for t in titres if not est_crypto(t) and t.get("marche") not in ("etf", "tendances")]
    if len(actions) >= 10:
        tri = sorted(actions, key=lambda t: -avis_ia(t)[0])
        haut, bas = tri[:15], list(reversed(tri[-15:]))
        hausse = sum(1 for t in actions if avis_ia(t)[1] > 0)
        faq = [("Which stocks will go up this month according to the AI?",
                "Highest chances of a rise today: " + ", ".join(f"{seo._e(t['nom'])} ({round(avis_ia(t)[0] * 100)}/100)" for t in haut[:5])
                + ". These are probabilities, not certainties or buying advice."),
               ("Will the stock market go up or down?", f"Out of {len(actions)} stocks tracked, the AI sees <b>{hausse}</b> going up and "
                f"<b>{len(actions) - hausse}</b> going down over the coming month.")]
        corps = (f"<h1>Stock market prediction {seo._e(mois_an)}: stocks the AI sees going up or down</h1>"
                 f"<p class='muted'>AI view updated automatically · prices as of {seo._e(date)}</p>"
                 f"<p>Out of <b>{len(actions)}</b> stocks tracked (France, Europe, US, Asia), the AI sees <b>{hausse}</b> going up and "
                 f"<b>{len(actions) - hausse}</b> going down over the coming month.</p>"
                 + graphe(haut[:8] + bas[:8][::-1], "The AI's strongest views")
                 + "<h2>The 15 stocks the AI sees most likely to rise</h2>" + _tableau_en(seo, haut, "Stocks seen going up")
                 + "<h2>The 15 stocks the AI sees most likely to fall</h2>" + _tableau_en(seo, bas, "Stocks seen going down")
                 + "<p><a class='btn' href='all-stocks.html'>All stocks (2,000+)</a> <a class='btn' href='crypto-prediction.html'>Crypto prediction</a></p>"
                 + _faq_html(faq).replace("Questions fréquentes", "FAQ") + note)
        chemin = "en/stock-market-prediction.html"
        alt = {"fr": "prediction-bourse.html", "en": chemin, "x-default": "prediction-bourse.html"}
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(anglais._page(base, f"Stock market prediction {mois_an}: stocks up or down | {seo.NOM}",
                                  f"Stock market prediction for {mois_an}: the stocks the AI sees going up or down next month, with their "
                                  "chances out of 100. Free, updated automatically.", chemin, corps, csp, alt,
                                  mots="stock market prediction, stock prediction, stocks to go up, stock forecast next month, AI stock prediction"))
        faits.append(chemin)
    return faits
