"""Version 95 : la visite guidée pour les nouveaux venus (inspirée des « tours » des grandes applis, jamais imposée).

- Dans l'appli : 7 étapes qui éclairent chaque partie (recherche, avis du jour, bulles, jauges, scanner, entraînement, preuves),
  avec Précédent / Suivant / Terminer, au clavier (flèches, Échap) comme à la souris. Elle se lance seulement si on la
  demande : bouton de la carte d'accueil, bouton « Découvrir le site » (toujours disponible), ou lien index.html#visite.
- Sur les pages fixes : un bloc « Et maintenant ? » de 3 cartes en bas des fiches et des outils, pour donner envie
  d'aller voir une deuxième page (la plupart des visiteurs arrivent de Google sur une fiche ou un outil).
"""

ETAPES = [
    ("#rech", "Cherche n'importe quel titre", "Tape le nom d'une action ou d'une crypto (Apple, Bitcoin, LVMH…) : sa fiche s'ouvre avec l'avis de l'IA, sa fourchette de prix et ses graphiques."),
    ("#previsions", "Les avis du jour", "Les titres que l'IA voit monter ou baisser le mois prochain, avec ses chances sur 100 et sa confiance. « Confiance faible » veut dire qu'elle hésite : on te le dit."),
    ("#bulles", "Le marché en un coup d'œil", "Chaque bulle est un titre : grosse si son prix a beaucoup bougé, verte s'il monte. Attrape-les, clique pour ouvrir une fiche."),
    ("#jauges", "Le moral du marché", "Le thermomètre (de la peur à l'euphorie), la saison des altcoins et l'agitation prévue. Des photos du marché, pas des prévisions."),
    ("#tous", "Trouve tes titres", "Le tableau complet et son scanner : combine des critères (calme, dividende, tendance…) et garde tes recherches préférées."),
    ("#portefeuille", "Entraîne-toi sans risque", "10 000 € fictifs pour acheter et vendre, et « Mon espace » pour retrouver tout ce que tu fais, même sur un autre appareil."),
    ("#confiance", "Vérifie l'IA toi-même", "Ses résultats sur des années jamais vues, et ses prévisions passées vérifiées en public, ratés compris. Pour apprendre de zéro : l'Académie, gratuite."),
]

CSS = r"""
html[lang="en"] #visite-go{display:none}
.vg-voile{position:fixed;inset:0;z-index:80;pointer-events:none}
.vg-trou{position:fixed;z-index:81;border-radius:14px;box-shadow:0 0 0 4px var(--accent),0 0 0 9999px rgba(5,10,20,.62);pointer-events:none;
  transition:top .45s cubic-bezier(.2,.8,.2,1),left .45s cubic-bezier(.2,.8,.2,1),width .45s cubic-bezier(.2,.8,.2,1),height .45s cubic-bezier(.2,.8,.2,1)}
.vg-bulle{position:fixed;z-index:82;width:min(360px,calc(100vw - 24px));background:var(--surface);color:var(--ink);border:1px solid var(--line);
  border-radius:14px;padding:16px 18px 14px;box-shadow:0 18px 50px rgba(5,10,20,.45)}
.vg-bulle h3{margin:0 0 6px;font-size:18px}.vg-bulle p{margin:0 0 12px;font-size:14.5px;line-height:1.5}
.vg-pied{display:flex;align-items:center;gap:8px}.vg-pied .vg-n{margin-right:auto;font-size:12.5px;color:var(--muted)}
.vg-points{display:flex;gap:5px;margin:0 0 12px}.vg-points i{width:22px;height:4px;border-radius:2px;background:var(--line)}.vg-points i.on{background:var(--accent)}
.vg-bouton{position:fixed;right:76px;bottom:16px;z-index:30;display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);background:var(--surface);
  color:var(--ink);border-radius:999px;padding:9px 14px 9px 10px;font:600 13.5px var(--font,system-ui);cursor:pointer;box-shadow:0 6px 20px rgba(5,10,20,.3)}
.vg-bouton b{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--accent);color:var(--surface);font-size:14px}
.vg-bouton:hover{border-color:var(--accent)}.vg-bouton:focus-visible,.vg-bulle button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:640px){.vg-bouton{bottom:calc(90px + env(safe-area-inset-bottom));right:70px;padding:8px}.vg-bouton span{display:none}}
@media (prefers-reduced-motion:reduce){.vg-trou{transition:none}}
"""

JS = r"""
/* ---------- Version 95 : visite guidée ---------- */
(function(){
  const ETAPES = __ETAPES__;
  let i = 0, trou = null, bulle = null, avant = null;
  const vis = s => { const e = document.querySelector(s); return e && e.offsetParent !== null ? e : null; };
  function placer(){
    const [sel, titre, texte] = ETAPES[i], e = vis(sel); if(!e){ return suivant(1); }
    const r = e.getBoundingClientRect(), m = 8, h = Math.min(r.height + 2 * m, innerHeight * .6);
    Object.assign(trou.style, {top: (r.top - m) + "px", left: Math.max(4, r.left - m) + "px", width: Math.min(innerWidth - 8, r.width + 2 * m) + "px", height: h + "px"});
    bulle.innerHTML = `<div class="vg-points" aria-hidden="true">${ETAPES.map((_, k) => `<i class="${k <= i ? "on" : ""}"></i>`).join("")}</div>
      <h3 id="vg-t">${titre}</h3><p>${texte}</p><div class="vg-pied"><span class="vg-n">${i + 1} / ${ETAPES.length}</span>
      ${i ? `<button class="btn ghost" type="button" data-vg="-1">Précédent</button>` : `<button class="btn ghost" type="button" data-vg="fin">Passer</button>`}
      <button class="btn" type="button" data-vg="${i === ETAPES.length - 1 ? "fin" : "1"}">${i === ETAPES.length - 1 ? "Terminer" : "Suivant"}</button></div>`;
    const bw = bulle.offsetWidth, bh = bulle.offsetHeight, bas = r.top - m + h + 12;
    let top = bas + bh < innerHeight - 8 ? bas : Math.max(8, r.top - m - bh - 12);
    if(top + bh > innerHeight - 8) top = innerHeight - bh - 8;
    bulle.style.top = top + "px"; bulle.style.left = Math.max(12, Math.min(innerWidth - bw - 12, r.left)) + "px";
    bulle.querySelectorAll("[data-vg]").forEach(b => b.onclick = () => b.dataset.vg === "fin" ? fermer() : suivant(+b.dataset.vg));
    const prim = bulle.querySelector(".btn:not(.ghost)"); if(prim) prim.focus({preventScroll: true});
  }
  function aller(){
    const e = vis(ETAPES[i][0]); if(!e) return suivant(1);
    const r = e.getBoundingClientRect();
    if(r.top < 70 || r.top > innerHeight * .45){
      e.scrollIntoView({block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"});
      // on attend la fin du défilement (position stable) avant d'éclairer la zone
      let dernier = null, stable = 0, tours = 0;
      const attendre = () => { const t = e.getBoundingClientRect().top; stable = (dernier !== null && Math.abs(t - dernier) < 1) ? stable + 1 : 0; dernier = t;
        if(stable >= 3 || ++tours > 90) placer(); else requestAnimationFrame(attendre); };
      requestAnimationFrame(attendre);
    } else placer();
  }
  function suivant(d){ const j = i + d; if(j < 0) return; if(j >= ETAPES.length) return fermer(); i = j; aller(); }
  function touche(e){ if(e.key === "Escape") fermer(); else if(e.key === "ArrowRight") suivant(1); else if(e.key === "ArrowLeft") suivant(-1); }
  function fermer(){ if(trou) trou.remove(); if(bulle) bulle.remove(); trou = bulle = null; removeEventListener("keydown", touche); removeEventListener("resize", placer);
    try{ localStorage.setItem("radar-visite-faite", "1"); }catch(e){} if(avant && avant.focus) avant.focus(); }
  window.visiteGuidee = function(){
    if(trou) return; avant = document.activeElement; i = 0;
    const cs = document.getElementById("consent"); if(cs) cs.hidden = true;
    trou = document.createElement("div"); trou.className = "vg-trou"; document.body.appendChild(trou);
    bulle = document.createElement("div"); bulle.className = "vg-bulle"; bulle.setAttribute("role", "dialog"); bulle.setAttribute("aria-labelledby", "vg-t");
    document.body.appendChild(bulle); addEventListener("keydown", touche); addEventListener("resize", placer); aller();
  };
  // bouton toujours disponible (texte masqué sur téléphone), et lancement par le lien index.html#visite
  if(document.documentElement.lang !== "en"){
    const b = document.createElement("button"); b.className = "vg-bouton"; b.type = "button"; b.setAttribute("aria-label", "Découvrir le site en 1 minute");
    b.innerHTML = `<b aria-hidden="true">?</b><span>Découvrir le site</span>`; b.onclick = () => visiteGuidee(); document.body.appendChild(b);
  }
  if(location.hash === "#visite") setTimeout(() => visiteGuidee(), 900);
})();
"""


def js() -> str:
    import json
    return JS.replace("__ETAPES__", json.dumps(ETAPES, ensure_ascii=False))


# ----------------------------------------------------------------------------------------------------------------
# « Et maintenant ? » (pages fixes)
# ----------------------------------------------------------------------------------------------------------------
CSS_SUITE = """<style>
.suite{margin:36px 0 8px}.suite h2{margin:0 0 12px}
.suite-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.suite-g a{display:flex;flex-direction:column;gap:6px;border:1px solid var(--line);border-radius:14px;padding:16px;text-decoration:none;color:inherit;
  background:var(--surface,transparent);transition:border-color .2s,transform .2s}
.suite-g a:hover{border-color:var(--accent,#5aa9ff);transform:translateY(-2px)}.suite-g a:focus-visible{outline:2px solid var(--accent,#5aa9ff);outline-offset:2px}
.suite svg{width:34px;height:34px;color:var(--accent,#5aa9ff)}.suite b{font-size:16px}.suite span{font-size:13.5px;color:var(--muted)}
.suite-visite{margin:12px 0 0;font-size:14px}
@media (prefers-reduced-motion:reduce){.suite a{transition:none}.suite-g a:hover{transform:none}}
</style>"""

_IC = {
    "comparer": "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' aria-hidden='true'><path d='M7 4v16M17 4v16M3 9h8M13 15h8'/></svg>",
    "preuve": "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'><path d='M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z'/><path d='M9 12l2 2 4-4'/></svg>",
    "apprendre": "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'><path d='M2 9l10-5 10 5-10 5z'/><path d='M6 11v5c3 2 9 2 12 0v-5'/></svg>",
    "jouer": "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'><path d='M3 17l6-6 4 4 8-8'/><path d='M15 7h6v6'/></svg>",
    "bulles": "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' aria-hidden='true'><circle cx='8' cy='9' r='5'/><circle cx='17' cy='15' r='4'/><circle cx='16' cy='5' r='2'/></svg>",
}


def bloc_suite(cartes: list, prefixe: str = "") -> str:
    """cartes : [(icône, titre, texte, lien)] ; 3 cartes en général."""
    html = "".join(f"<a href='{prefixe}{l}'>{_IC.get(ic, '')}<b>{t}</b><span>{x}</span></a>" for ic, t, x, l in cartes)
    return (CSS_SUITE + "<section class='suite' aria-labelledby='suite-t'><h2 id='suite-t'>Et maintenant ?</h2>"
            f"<div class='suite-g'>{html}</div><p class='suite-visite muted'>Nouveau sur Radar Bourse ? <a href='{prefixe}index.html#visite'>Découvre le site en 1 minute</a>.</p></section>")


def suite_fiche(t: dict, voisin: dict | None, prefixe: str = "../") -> str:
    import re
    nom = t.get("nom", "")
    crypto = t.get("ticker", "").endswith("-USD")
    cartes = []
    tok = re.sub(r"[^A-Za-z0-9._-]", "", t.get("ticker", ""))
    cartes.append(("bulles", f"{nom} dans l'appli interactive", "Graphique en bougies, profil, saisonnalité, simulateur et comparaison avec un autre titre.", f"index.html#{tok}"))
    cartes.append(("preuve", "L'IA a-t-elle eu raison ?", "Ses prévisions passées vérifiées en public, ratés compris.", "avis-surs-verifies.html"))
    cartes.append(("apprendre", "Comprendre en 3 minutes" if not crypto else "La crypto, simplement",
                   "Lire un graphique, l'agitation, le risque : l'Académie gratuite." if not crypto else "Ce qu'est une crypto et ses risques, à l'Académie gratuite.",
                   "formation.html"))
    cartes.append(("jouer", f"Et si tu avais investi dans {nom} ?", "Le calcul sur les vrais cours, en une fois ou chaque mois.", "outils/si-javais-investi.html"))
    return bloc_suite(cartes[:4], prefixe)


SUITE_OUTIL = [("bulles", "Le marché en bulles", "Toutes les cryptos et actions d'un coup d'œil : qui monte, qui baisse.", "index.html#bulles"),
               ("jouer", "Simulateur boursier", "10 000 € fictifs pour t'entraîner sans risque.", "simulateur-boursier.html"),
               ("preuve", "L'avis de l'IA sur le mois qui vient", "Hausse ou baisse, avec ses chances et ses ratés publiés.", "prediction-crypto.html"),
               ("apprendre", "Apprendre la Bourse de zéro", "Des leçons courtes avec exercices corrigés.", "formation.html")]
