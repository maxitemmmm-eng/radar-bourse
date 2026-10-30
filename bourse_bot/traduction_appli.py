"""Version 54 : l'appli interactive en anglais (app-en.html), produite à partir du même gabarit que l'appli française.

Principe : le gabarit est découpé avec précision (texte HTML visible, attributs lisibles, chaînes JavaScript, parties
fixes des gabarits `...${...}...`). Seuls ces morceaux de TEXTE sont remplacés, et seulement s'ils figurent mot pour mot
dans le dictionnaire (traductions_en.py) : le code n'est jamais touché, donc l'appli ne peut pas être cassée par la
traduction ; un texte absent du dictionnaire reste simplement en français."""
from __future__ import annotations

import re

TAG = re.compile(r"(<[^<>]*>)")
ATTRS = re.compile(r'\b(aria-label|title|placeholder|alt|data-aide-titre)="([^"]*)"')


def _blocs_js(js: str):
    """Repère dans du JavaScript les étendues de texte : [(début, fin, genre)], genre = "chaine" ou "gabarit"."""
    out, i, n = [], 0, len(js)
    pile = []            # pour chaque ${ ouvert : profondeur d'accolades au moment de l'ouverture
    prof = 0
    prec = ""            # dernier caractère significatif (pour distinguer division et expression régulière)

    def lire_chaine(i, q):
        j = i + 1
        while j < n and js[j] != q:
            if js[j] == "\\":
                j += 1
            elif js[j] == "\n":
                break
            j += 1
        return j

    def lire_regex(i):
        j, classe = i + 1, False
        while j < n:
            c = js[j]
            if c == "\\":
                j += 2; continue
            if c == "[":
                classe = True
            elif c == "]":
                classe = False
            elif c == "/" and not classe:
                break
            elif c == "\n":
                break
            j += 1
        j += 1
        while j < n and js[j].isalpha():
            j += 1
        return j

    def lire_gabarit(i):
        """i : position juste après le ` ouvrant. Renvoie la position juste après le ` fermant."""
        nonlocal prof
        debut = i
        while i < n:
            c = js[i]
            if c == "\\":
                i += 2; continue
            if c == "`":
                out.append((debut, i, "gabarit"))
                return i + 1
            if c == "$" and i + 1 < n and js[i + 1] == "{":
                out.append((debut, i, "gabarit"))
                i = lire_code(i + 2, fin_accolade=True)
                debut = i
                continue
            i += 1
        return i

    def lire_code(i, fin_accolade=False):
        nonlocal prec
        d = 0
        while i < n:
            c = js[i]
            if c in " \t\r\n":
                i += 1; continue
            if c == "/" and i + 1 < n and js[i + 1] == "/":
                while i < n and js[i] != "\n":
                    i += 1
                continue
            if c == "/" and i + 1 < n and js[i + 1] == "*":
                k = js.find("*/", i + 2); i = n if k < 0 else k + 2; continue
            if c in "\"'":
                j = lire_chaine(i, c)
                out.append((i + 1, j, "chaine")); i = j + 1; prec = "a"; continue
            if c == "`":
                i = lire_gabarit(i + 1); prec = "a"; continue
            if c == "/":
                if prec in ("", "(", ",", "=", ":", "[", "!", "&", "|", "?", "{", "}", ";", "+", "-", "*", "%", "<", ">", "~", "^", "r"):
                    i = lire_regex(i); prec = "a"; continue
            if c == "{":
                d += 1
            elif c == "}":
                if fin_accolade and d == 0:
                    return i + 1
                d -= 1
            if c.isalnum() or c in "_$":
                j = i
                while j < n and (js[j].isalnum() or js[j] in "_$"):
                    j += 1
                mot = js[i:j]
                prec = "r" if mot in ("return", "typeof", "case", "in", "of", "else", "do") else "a"
                i = j; continue
            prec = c if c not in ")]" else "a"
            i += 1
        return i

    lire_code(0)
    return out


def _traduire_html(txt: str, D: dict) -> str:
    """Remplace chaque morceau de texte visible (entre les balises) et les attributs lisibles."""
    morceaux = TAG.split(txt)
    for k, m in enumerate(morceaux):
        if k % 2 == 1:      # une balise : seulement ses attributs lisibles
            morceaux[k] = ATTRS.sub(lambda a: f'{a.group(1)}="{D.get(a.group(2).strip(), a.group(2))}"', m)
            continue
        s = m.strip()
        if s and s in D:
            g = m[: len(m) - len(m.lstrip())]
            dr = m[len(m.rstrip()):]
            morceaux[k] = g + D[s] + dr
    return "".join(morceaux)


def traduire_js(js: str, D: dict) -> str:
    blocs = _blocs_js(js)
    res, pos = [], 0
    for a, b, genre in sorted(blocs):
        if a < pos:
            continue
        res.append(js[pos:a])
        txt = js[a:b]
        if genre == "chaine" and _est_cle(js, a, b):
            res.append(txt); pos = b; continue
        if genre == "chaine" and txt.strip() in D and "<" not in txt:
            s = txt.strip()
            t = txt[: len(txt) - len(txt.lstrip())] + D[s] + txt[len(txt.rstrip()):]
            # une chaîne entre "..." ou '...' ne doit pas recevoir le guillemet qui la ferme
            t = t.replace("\\", "\\\\") if False else t
            res.append(_echapper(t, js[a - 1]))
        else:
            res.append(_traduire_html(txt, D) if genre == "gabarit" else _echapper_html_chaine(txt, D, js[a - 1]))
        pos = b
    res.append(js[pos:])
    return "".join(res)


def _est_cle(js: str, a: int, b: int) -> bool:
    """Une chaîne utilisée comme CLÉ dans le code (comparaison, clé d'objet, case, sélecteur, aide("…"), dataset…)
    ne doit jamais être traduite : sinon la logique de l'appli changerait."""
    avant = js[max(0, a - 40): a - 1].rstrip()
    apres = js[b + 1: b + 30].lstrip()
    if re.search(r"(===|!==|==|!=|\bcase|\bin|\[|\bincludes\(|\bhas\(|\bget\(|\bset\(|aide\(|\bindexOf\(|\bstartsWith\(|getItem\(|setItem\(|querySelector(All)?\(|getElementById\(|\$\(|classList\.\w+\(|dataset\.\w+\s*=)$", avant):
        return True
    if re.match(r"(===|!==|==|!=|:(?!:))", apres) and not re.search(r"\?\s*$", avant):
        return True
    return False


def _echapper(t: str, q: str) -> str:
    if q in "\"'":
        return re.sub(r"(?<!\\)" + re.escape(q), "\\" + q, t)
    return t


def _echapper_html_chaine(txt, D, q):
    t = _traduire_html(txt, D)
    return t if t == txt else _echapper(t, q)


def traduire_page(html: str, D: dict) -> str:
    """Traduit une page entière : le HTML hors <script>/<style>, et le JavaScript des <script>."""
    morceaux = re.split(r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)", html, flags=re.S)
    for k, m in enumerate(morceaux):
        if k % 2 == 0:
            morceaux[k] = _traduire_html(m, D)
        elif m.startswith("<script") and "application/ld+json" not in m[:80] and 'src="' not in m[:120]:
            o = m.index(">") + 1
            f = m.rindex("</script>")
            morceaux[k] = m[:o] + traduire_js(m[o:f], D) + m[f:]
    return "".join(morceaux)


def unites(html: str) -> list:
    """Pour préparer le dictionnaire : tous les morceaux de texte que traduire_page peut remplacer."""
    vu = []

    def ajout(s):
        s = s.strip()
        if s and re.search(r"[A-Za-zÀ-ÿ]{2}", s) and s not in vu:
            vu.append(s)

    def html_unites(t):
        for k, m in enumerate(TAG.split(t)):
            if k % 2 == 1:
                for a in ATTRS.finditer(m):
                    ajout(a.group(2))
            else:
                ajout(m)
    morceaux = re.split(r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)", html, flags=re.S)
    for k, m in enumerate(morceaux):
        if k % 2 == 0:
            html_unites(m)
        elif m.startswith("<script") and "application/ld+json" not in m[:80] and 'src="' not in m[:120]:
            js = m[m.index(">") + 1: m.rindex("</script>")]
            for a, b, genre in _blocs_js(js):
                t = js[a:b]
                if genre == "chaine" and _est_cle(js, a, b):
                    continue
                if genre == "chaine" and "<" not in t:
                    ajout(t)
                else:
                    html_unites(t)
    return vu


# Libellés qui arrivent avec les DONNÉES (calculées en Python, en français) : traduits à l'affichage seulement,
# texte par texte, sans toucher aux données elles-mêmes (le code continue de les comparer en français).
# « # » = un nombre, recopié tel quel dans la traduction.
from .traductions_en import EXACT_DONNEES as LIBELLES_EXACTS_EN, PHRASES_DONNEES as PHRASES_EN


def _regex_js(fr: str) -> str:
    e = re.sub(r"([.*+?^${}()|\[\]\\/])", r"\\\1", fr)
    return e.replace("#", r"(-?\d+(?:[.,]\d+)?)")


def _remplacement_js(en: str) -> str:
    k = [0]
    def num(_):
        k[0] += 1
        return "$" + str(k[0])
    return re.sub("#", num, en.replace("$", "$$"))


def _script_donnees(exact: dict, phrases: list) -> str:
    import json
    paires = list(phrases)
    for fr, en in phrases:   # la même phrase en début de texte, avec une majuscule
        if fr[:1].islower():
            paires.append((fr[0].upper() + fr[1:], en[0].upper() + en[1:]))
    regles = [[_regex_js(fr), _remplacement_js(en)] for fr, en in sorted(paires, key=lambda x: -len(x[0]))]
    regles.append([r"(\d[\d,.]*\s?%?) à (-?−?\d)", "$1 to $2"])
    regles.append([r"([A-Za-z0-9)%\"]) : ", "$1: "])
    regles.append([r"(\d),(\d{1,2})(?!\d)", "$1.$2"])   # virgule décimale française → point (0,8 → 0.8 ; 4,000 inchangé)        # espace français avant « : » dans les textes déjà traduits
    js = json.dumps({"E": exact, "R": regles}, ensure_ascii=False).replace("</", "<\\/")
    return ("<script>(()=>{const D=" + js + ";const R=D.R.map(([a,b])=>[new RegExp(a,'g'),b]);"
            "const tr=n=>{const t=n.nodeValue;if(!t||t.length<2)return;const s=t.trim();"
            "if(D.E[s]!==undefined){const v=t.replace(s,D.E[s]);if(v!==t)n.nodeValue=v;return;}"
            "if(!/[a-zà-ÿ]{2}|\\d,\\d/i.test(t))return;let u=t;for(const[r,b]of R)u=u.replace(r,b);if(u!==t)n.nodeValue=u;};"
            "const SAUTE={SCRIPT:1,STYLE:1,NOSCRIPT:1,TEXTAREA:1,TEMPLATE:1};"
            "const tout=r=>{const w=document.createTreeWalker(r,NodeFilter.SHOW_TEXT,{acceptNode:n=>{const p=n.parentNode;"
            "return p&&SAUTE[p.nodeName]||n.nodeValue.length>3000?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT;}});let n;while((n=w.nextNode()))tr(n);};"
            "const go=()=>{tout(document.body);new MutationObserver(l=>{for(const x of l){if(x.type==='characterData'){const p=x.target.parentNode;if(!(p&&SAUTE[p.nodeName]))tr(x.target);}"
            "else for(const n of x.addedNodes){if(n.nodeType===3){if(!SAUTE[x.target.nodeName])tr(n);}else if(n.nodeType===1&&!SAUTE[n.nodeName])tout(n);}}})"
            ".observe(document.body,{childList:true,subtree:true,characterData:true});};"
            "document.readyState==='loading'?document.addEventListener('DOMContentLoaded',go):go();})();</script>")


SCRIPT_DONNEES_EN = _script_donnees(LIBELLES_EXACTS_EN, PHRASES_EN)
