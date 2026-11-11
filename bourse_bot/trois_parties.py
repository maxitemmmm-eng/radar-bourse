"""Version 71 : le site en 3 parties (Menu, Pronos, Apprendre), partagé par toutes les pages."""

SVG = {"menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/></svg>', "pronos": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12 L19 6"/></svg>', "apprendre": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 9 L12 4 L22 9 L12 14 Z"/><path d="M6 11 V16 C8.5 18.5 15.5 18.5 18 16 V11"/></svg>'}
CSS = '\n/* version 71 : le site en 3 parties — Menu, Pronos, Apprendre (sélecteur en haut sur ordinateur, onglets en bas sur téléphone) */\n.trois{display:flex;gap:4px;padding:4px;border-radius:12px;background:var(--surface-2);border:1px solid var(--line)}\n.trois a{display:flex;align-items:center;gap:7px;padding:6px 13px;border-radius:9px;text-decoration:none;color:var(--muted);font-weight:700;font-size:14px;white-space:nowrap}\n.trois a svg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}\n.trois a:hover{color:var(--ink)}\n.trois a[aria-current]{background:var(--ink);color:var(--surface)}\n.trois a::after{content:none!important}\n@media (max-width:980px){\n  .trois{position:fixed;left:0;right:0;bottom:0;z-index:30;border-radius:0;border:0;border-top:1px solid var(--line);background:var(--surface);\n    padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));justify-content:space-around;box-shadow:0 -6px 20px rgba(5,10,20,.18)}\n  .trois a{flex:1;flex-direction:column;gap:3px;font-size:12px;padding:6px 4px;justify-content:center}\n  .trois a svg{width:22px;height:22px}\n  .trois a[aria-current]{background:color-mix(in srgb,var(--accent) 16%,transparent);color:var(--ink)}\n  body{padding-bottom:72px}\n}\n@media print{.trois{display:none!important}}\n'


def partie_de(chemin: str) -> str:
    return "apprendre" if (chemin.startswith("formation") or chemin in ("apprendre.html", "glossaire.html", "guides.html")
                           or chemin.startswith(("guides/", "lecons/", "glossaire/"))) else "pronos"


def barre(prefixe: str, actif: str, libelles=("Menu", "Pronos", "Apprendre")) -> str:
    liens = (("menu", prefixe + "index.html#menu", libelles[0]), ("pronos", prefixe + "index.html", libelles[1]),
             ("apprendre", prefixe + "formation.html", libelles[2]))
    return ('<nav class="trois" aria-label="Les trois parties du site">'
            + "".join(f'<a href="{h}" data-partie="{k}"{" aria-current=\"page\"" if k == actif else ""}>{SVG[k]}<span>{t}</span></a>' for k, h, t in liens)
            + "</nav>")


# Version 72 : chaque partie a son propre thème, pour savoir d'un coup d'œil où l'on est.
#   Pronos    : bleu nuit et vert (le thème historique du radar)
#   Apprendre : prune et ambre, plus chaleureux, comme un carnet de cours
#   Menu      : l'écran d'accueil façon jeu (noir profond et grille verte), dans l'appli
_APP_CLAIR = ("--bg:#f5f3fa;--surface:#ffffff;--surface-2:#efebf7;--ink:#1d1631;--muted:#5d5576;--line:#ddd5ec;"
              "--accent:#6a3fcf;--accent-soft:#ece4fb;--marque:#b7791f")
_APP_SOMBRE = ("--bg:#130f1f;--surface:#1c1730;--surface-2:#251f3d;--ink:#eee9f8;--muted:#a79fc0;--line:#362d55;"
               "--accent:#f2b54a;--accent-soft:#3a2d16;--marque:#f2b54a")
CSS_THEMES = (
    "\n/* version 72 : un thème par partie */\n"
    "body.partie-apprendre{" + _APP_CLAIR + "}\n"
    "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]) body.partie-apprendre{" + _APP_SOMBRE + "}}\n"
    ":root[data-theme=\"dark\"] body.partie-apprendre{" + _APP_SOMBRE + "}\n"
    "body.partie-apprendre header.top{border-bottom:2px solid var(--marque)}\n"
    "body.partie-apprendre .trois a[aria-current]{background:var(--marque);color:#1a1206}\n"
    "body.partie-apprendre .btn:not(.ghost){background:var(--accent);border-color:var(--accent);color:var(--surface)}\n"
    "body.partie-apprendre .brand small.partie{color:var(--marque)}\n"
    "body.partie-pronos .trois a[aria-current]{background:var(--accent);color:#fff}\n"
    "body.partie-pronos header.top{border-bottom:2px solid color-mix(in srgb,var(--accent) 55%,transparent)}\n"
    ".brand small.partie{display:block;font-size:11.5px;font-weight:700;letter-spacing:.02em;color:var(--accent);margin-top:-2px}\n"
    "@media (max-width:980px){body.partie-apprendre .trois a[aria-current]{background:color-mix(in srgb,var(--marque) 22%,transparent);color:var(--ink)}"
    "body.partie-pronos .trois a[aria-current]{background:color-mix(in srgb,var(--accent) 18%,transparent);color:var(--ink)}}\n"
)
CSS = CSS + CSS_THEMES
