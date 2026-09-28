"""
Générateur du site Yogurt Factory : transforme les sources en site statique dans dist/.

    python build.py              construit le site dans dist/ (c'est ce dossier qu'on met en ligne)
    python build.py --indexnow   construit puis signale les pages à Bing, Yandex, Seznam, Naver…
    BASE_PATH=/mon-dossier python build.py   site publié dans un sous-dossier (préversion, non indexée)

Pré-requis : Python 3.10+ et Pillow (pip install pillow). Node.js est facultatif : s'il est
installé, esbuild minifie le CSS/JS et le rend compatible avec les anciens navigateurs.

Où modifier quoi :
    contenu/boutiques/*.json    une boutique par fichier (modèle : contenu/boutiques/_modele.json)
    contenu/carte/*.json        rubriques de la carte, toppings, coulis, sirops, perles…
    contenu/fidelite.json       récompenses du programme de fidélité
    contenu/pays.json           pays (ordre des pastilles, nom anglais, fuseau horaire)
    contenu/reglages.json       adresses des formulaires, protection du texte…
    _src/pages/*.html           texte des pages en français (_src/pages-en/ : anglais, même nom de fichier)
    _src/partials/              en-tête, pied de page, données structurées communes
    _src/static/                fichiers copiés tels quels à la racine (.htaccess, _headers, security.txt…)
    assets/css, assets/js       styles et scripts ; images/ : photos (originaux lourds dans images/src/, non publiés)

Chaque page commence par un bloc de réglages lu ici puis retiré :
    <!--
    title: Titre de l'onglet et de Google
    description: Résumé pour Google et les réseaux sociaux (≈155 caractères)
    nav: carte                    lien du menu à mettre en surbrillance
    og_title / og_sub:            texte de l'image de partage générée automatiquement
    jsonld: partials/x.html       données structurées supplémentaires (facultatif)
    kind: error                   page utilitaire (404, merci…) : non indexée
    -->

Balises remplacées dans les pages : {{count:stores}}, {{count:cities}}, {{count:toppings}},
{{count:coulis}}, {{carte:onglets}}, {{carte:rubriques}}, {{fidelite:recompenses}},
{{fidelite:max}}, {{icon:halal}}, {{pot:TEXTE}}, {{nav:x}}, {{alt_href}}.
Une balise oubliée ou mal écrite arrête le build avec un message.
"""
import hashlib
import os
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
DIST = ROOT / "dist"

# ---- Réglages ---------------------------------------------------------------
SITE_URL = "https://yogurtfactory.fr"
SITE_NAME = "Yogurt Factory"
# Sous-dossier de publication, lu dans la variable d'environnement BASE_PATH (GitHub Pages : /nom-du-depot).
# Vide = site à la racine du domaine. Un site en sous-dossier est traité comme une préversion : noindex.
BASE = os.environ.get("BASE_PATH", "").strip().rstrip("/")
if BASE and not BASE.startswith("/"):
    BASE = "/" + BASE
# Codes fournis par les outils pour webmasters (balise meta de validation) ; vide = non utilisé
GOOGLE_SITE_VERIFICATION = ""   # Google Search Console
BING_SITE_VERIFICATION = ""     # Bing Webmaster Tools (alimente aussi DuckDuckGo, Qwant, Ecosia, Yahoo)
YANDEX_VERIFICATION = ""
# Clé IndexNow : publiée à la racine sous <clé>.txt pour prouver que le site nous appartient
INDEXNOW_KEY = "7f3c9a2e5b8d4f16a0c3e9b72d5f8a14"
# Navigateurs ciblés par esbuild (~98 % du parc, iPhone depuis iOS 13)
BROWSER_TARGETS = "chrome80,edge80,firefox78,safari13,ios13,opera67"
ESBUILD = "esbuild@0.25.0"

# Langues : français à la racine, anglais dans /en/. Une page anglaise porte le même nom de fichier source
# que sa version française ; SLUGS_EN donne son adresse publique en anglais.
LANGS = {
    "fr": {"dir": "", "pages": "pages", "header": "header.html", "footer": "footer.html", "locale": "fr_FR", "html": "fr-FR"},
    "en": {"dir": "en/", "pages": "pages-en", "header": "header-en.html", "footer": "footer-en.html", "locale": "en_GB", "html": "en"},
}
SLUGS_EN = {
    "carte.html": "menu.html", "fidelite.html": "loyalty.html", "boutiques.html": "stores.html", "recrutement.html": "careers.html",
    "mentions-legales.html": "legal-notice.html", "confidentialite.html": "privacy.html", "cgu.html": "terms.html",
    "accessibilite.html": "accessibility.html", "plan-du-site.html": "sitemap.html", "hors-ligne.html": "offline.html",
    "merci.html": "thank-you.html",
}


def slug(lang, fr_name):
    return SLUGS_EN.get(fr_name, fr_name) if lang == "en" else fr_name


def page_url(lang, fr_name):
    name = slug(lang, fr_name)
    return SITE_URL + "/" + LANGS[lang]["dir"] + ("" if name == "index.html" else name)


# Politique de sécurité du contenu (CSP) : seules les ressources listées ici peuvent être chargées.
# Les adresses d'envoi des formulaires (contenu/reglages.json) sont ajoutées automatiquement à connect-src.
# Ajouter un service externe (vidéo, carte, statistiques…) = ajouter son domaine ici.
CSP = {
    "default-src": "'self'",
    "script-src": "'self'",
    "style-src": "'self' 'unsafe-inline'",
    "img-src": "'self' data: https://*.tile.openstreetmap.org",
    "font-src": "'self'",
    "connect-src": "'self'",
    "manifest-src": "'self'",
    "worker-src": "'self'",
    "frame-src": "'none'",
    "media-src": "'self'",
    "object-src": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
    "frame-ancestors": "'none'",
    "upgrade-insecure-requests": "",
}
META_CSP_IGNORED = ("frame-ancestors", "upgrade-insecure-requests")   # sans effet ou gênant en balise meta (aperçu local en http)


def csp_string(settings, meta=False):
    policy = dict(CSP)
    origins = sorted({re.match(r"https://[^/]+", f["endpoint"]).group(0) for f in settings["forms"].values() if f["endpoint"]})
    if origins:
        policy["connect-src"] += " " + " ".join(origins)
    return "; ".join((k + " " + v).strip() for k, v in policy.items() if not (meta and k in META_CSP_IGNORED))


NAV_KEYS = ["concept", "carte", "fidelite", "boutiques", "franchise", "recrutement", "contact"]
ICONS = {
    "halal": '<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">'
             '<path d="M13.5 3.2A9 9 0 1 0 20.8 16 7.2 7.2 0 1 1 13.5 3.2z"/>'
             '<path d="M17.6 6.3l.9 2.1 2.2.2-1.7 1.5.5 2.2-1.9-1.2-1.9 1.2.5-2.2-1.7-1.5 2.2-.2z"/></svg>',
}

HEAD = """<!doctype html>
<html lang="{html_lang}" class="no-js"{data_base}>
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{base}<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
{alternates}
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Yogurt Factory">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/{og_image}">
<meta property="og:image:secure_url" content="{site}/{og_image}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{og_alt}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:locale:alternate" content="{og_locale_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{site}/{og_image}">
<meta name="twitter:image:alt" content="{og_alt}">
{twitter_labels}
<meta name="theme-color" content="#e3232b">
<meta name="color-scheme" content="light">
<meta name="application-name" content="Yogurt Factory">
<meta name="apple-mobile-web-app-title" content="Yogurt Factory">
{verification}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/images/icons/icon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/images/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/poppins-400-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/montserrat-100-900-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/lobster-400-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/fonts.css?v={v_fonts}">
<link rel="stylesheet" href="/assets/css/style.css?v={v_css}">
<script src="/assets/js/prefs.js?v={v_prefs}"></script>
{extra_head}</head>
<body>
"""

FOOT = """<script src="/assets/js/data.js?v={v_data}" defer></script>
<script src="/assets/js/main.js?v={v_main}" defer></script>
</body>
</html>
"""


# ---- Outils -----------------------------------------------------------------
def fhash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def minify_css_simple(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)   # jamais autour de ":" (sélecteurs « a :focus »)
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip() + "\n"


def esbuild(path, loader):
    """Minifie + transpile un fichier avec esbuild. Retourne False si indisponible."""
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        return False
    try:
        subprocess.run([npx, "--yes", ESBUILD, str(path), f"--loader:.{loader}={loader}", "--minify",
                        f"--target={BROWSER_TARGETS}", f"--outfile={path}", "--allow-overwrite", "--log-level=error",
                        "--legal-comments=none", "--charset=utf8"],
                       check=True, capture_output=True, timeout=180)
        return True
    except Exception as exc:  # noqa: BLE001
        print("  ! esbuild indisponible, minification simple :", exc)
        return False


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"


def store_jsonld(stores):
    items = []
    for i, s in enumerate(stores, 1):
        biz = {
            "@type": "IceCreamShop",
            "name": "Yogurt Factory " + s["name"],
            "brand": {"@id": SITE_URL + "/#organization"},
            "address": {"@type": "PostalAddress", "streetAddress": s["address"], "postalCode": s.get("zip", ""),
                        "addressLocality": s["city"], "addressRegion": s["region"], "addressCountry": s["country"]},
            "servesCuisine": ["Frozen yogurt", "Glaces", "Bubble tea", "Gaufres"],
            "image": SITE_URL + "/" + s.get("photo", "images/boutique-thumb.webp"),
            "url": SITE_URL + "/boutiques.html?q=" + s["city"].replace(" ", "+"),
        }
        if s.get("phone"):
            biz["telephone"] = s["phone"]
        if s.get("lat") is not None:
            biz["geo"] = {"@type": "GeoCoordinates", "latitude": s["lat"], "longitude": s["lng"]}
        if s.get("rating") and s.get("reviews"):
            biz["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": s["rating"], "reviewCount": s["reviews"]}
        items.append({"@type": "ListItem", "position": i, "item": biz})
    return ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Boutiques Yogurt Factory",
               "numberOfItems": len(items), "itemListElement": items})


def breadcrumb_jsonld(name, url, home="Accueil", home_url=SITE_URL + "/"):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": home, "item": home_url},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]})


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def faq_jsonld(raw):
    qa = re.findall(r"<details><summary>(.*?)</summary><div>(.*?)</div></details>", raw, re.S)
    if not qa:
        return ""
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
        for q, a in qa]})


def store_cards(stores):
    """Liste statique des boutiques (lisible sans JavaScript et par les moteurs de recherche)."""
    e = html.escape
    return "".join(
        f'<article class="store"><div class="store-body"><span class="where">{e(s["region"])}</span>'
        f'<h3>{e(s["name"])}</h3><address>{e(" · ".join(filter(None, (s["center"], s["address"]))))}, {e(s["zip"])} {e(s["city"])}</address>'
        f'<div class="hours">{e(s["hours"])}</div></div></article>' for s in stores)


# ---- Contenu éditable (dossier contenu/) -------------------------------------
# Tout ce qui change souvent vit dans contenu/ au format JSON : boutiques, carte,
# récompenses fidélité, pays, réglages. Ce module lit ces fichiers, les vérifie
# (message clair + arrêt du build en cas d'erreur) et produit le HTML / JS / JSON-LD.
# Un texte traduisible s'écrit soit "texte" (identique en FR et EN), soit
# { "fr": "…", "en": "…" }.
CONTENT = ROOT / "contenu"
STORE_FIELDS = {   # clé du fichier JSON -> clé utilisée par le JavaScript du site
    "nom": "name", "centre": "center", "adresse": "address", "code_postal": "zip", "ville": "city",
    "region": "region", "pays": "country", "horaires": "hours", "telephone": "phone", "lat": "lat", "lng": "lng",
    "note_google": "rating", "nombre_avis": "reviews", "lien_google": "googleUrl", "photo": "photo",
    "fuseau_horaire": "tz",
}
STORE_REQUIRED = ("nom", "adresse", "ville", "region", "pays", "horaires")
HOURS_FREE_TEXT = ("Horaires du centre", "Horaires saisonniers")   # affichés tels quels, sans « Ouvert / Fermé »
HOURS_RE = re.compile(r"^(tous les jours|(lun|mar|mer|jeu|ven|sam|dim)(–(lun|mar|mer|jeu|ven|sam|dim))?)\s+"
                      r"\d{1,2}h(\d{2})?–(\d{1,2}h(\d{2})?|minuit)$", re.I)
PHOTO_EXT = (".webp", ".jpg", ".jpeg", ".png")


def fail(msg):
    raise SystemExit("\n✗ " + msg + "\n  Le site n'a pas été généré : corrigez le fichier puis relancez python build.py.\n")


def rel(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{rel(path)} est introuvable.")
    except json.JSONDecodeError as e:
        fail(f"{rel(path)}, ligne {e.lineno} : JSON invalide ({e.msg}). "
             "Vérifiez les guillemets droits \" \", les virgules entre les lignes et l'absence de virgule après le dernier élément.")


def tr(value, lang):
    if isinstance(value, dict):
        return value.get(lang) or value.get("fr", "")
    return "" if value is None else str(value)


def load_countries():
    data = read_json(CONTENT / "pays.json")
    return [{"name": k, "en": v.get("en", k), "tz": v.get("fuseau_horaire", "")} for k, v in data.items()]


def load_settings():
    data = read_json(CONTENT / "reglages.json")
    forms = {}
    for key, f in data.get("formulaires", {}).items():
        email, endpoint = f.get("email", "").strip(), f.get("endpoint", "").strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email, re.I):
            fail(f"contenu/reglages.json : adresse e-mail invalide pour le formulaire « {key} ».")
        if endpoint and not re.fullmatch(r"https://[\w.-]+(:\d+)?(/[\w\-./%?=&]*)?", endpoint):
            fail(f"contenu/reglages.json : l'endpoint du formulaire « {key} » doit être une adresse https://…")
        forms[key] = {"email": email, "endpoint": endpoint}
    per_page = data.get("boutiques_par_page", 12)
    if not isinstance(per_page, int) or not 4 <= per_page <= 100:
        fail("contenu/reglages.json : boutiques_par_page doit être un nombre entre 4 et 100.")
    return {"forms": forms, "protectContent": bool(data.get("proteger_le_texte", True)), "storesPerPage": per_page}


def store_photo(slug, data, path):
    if data.get("photo"):
        p = ROOT / data["photo"]
        if not p.is_file():
            fail(f"{rel(path)} : la photo « {data['photo']} » n'existe pas.")
        return data["photo"]
    for ext in PHOTO_EXT:
        if (ROOT / "images" / "boutiques" / (slug + ext)).is_file():
            return f"images/boutiques/{slug}.webp"   # les JPG/PNG sont convertis en WebP au build
    return None


def load_stores(countries):
    """Lit contenu/boutiques/*.json (les fichiers commençant par « _ » sont ignorés : modèles, brouillons)."""
    tz_of = {c["name"]: c["tz"] for c in countries}
    order = {c["name"]: i for i, c in enumerate(countries)}
    stores, names = [], {}
    for path in sorted((CONTENT / "boutiques").glob("*.json")):
        if path.name.startswith("_"):
            continue
        data = read_json(path)
        where = rel(path)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", path.stem):
            fail(f"{where} : le nom du fichier doit être en minuscules, sans accent ni espace (ex. lyon-part-dieu.json).")
        unknown = set(data) - set(STORE_FIELDS)
        if unknown:
            fail(f"{where} : champ inconnu {sorted(unknown)}. Champs possibles : {', '.join(STORE_FIELDS)}.")
        for k in STORE_REQUIRED:
            if not str(data.get(k, "")).strip():
                fail(f"{where} : le champ « {k} » est obligatoire.")
        if data["pays"] not in tz_of:
            fail(f"{where} : pays « {data['pays']} » inconnu. Ajoutez-le d'abord dans contenu/pays.json.")
        if data["nom"] in names:
            fail(f"{where} : le nom « {data['nom']} » est déjà utilisé par {names[data['nom']]}.")
        names[data["nom"]] = where
        s = {STORE_FIELDS[k]: v for k, v in data.items() if v not in ("", None)}
        s.setdefault("center", "")
        s.setdefault("zip", "")
        has_lat, has_lng = "lat" in data, "lng" in data
        if has_lat != has_lng:
            fail(f"{where} : indiquez lat et lng ensemble (ou aucun des deux).")
        if has_lat and not (isinstance(data["lat"], (int, float)) and isinstance(data["lng"], (int, float))
                            and -90 <= data["lat"] <= 90 and -180 <= data["lng"] <= 180):
            fail(f"{where} : lat / lng doivent être des nombres (ex. 48.8566 et 2.3522), sans guillemets.")
        if "note_google" in data and not (isinstance(data["note_google"], (int, float)) and 0 <= data["note_google"] <= 5):
            fail(f"{where} : note_google doit être un nombre entre 0 et 5 (ex. 4.6).")
        if "nombre_avis" in data and not (isinstance(data["nombre_avis"], int) and data["nombre_avis"] >= 0):
            fail(f"{where} : nombre_avis doit être un nombre entier (ex. 1234).")
        if data.get("lien_google") and not re.match(r"https://(www\.google\.[a-z.]+/maps|maps\.google\.[a-z.]+|maps\.app\.goo\.gl|goo\.gl/maps)/", data["lien_google"]):
            fail(f"{where} : lien_google doit être un lien Google Maps en https://.")
        hours = data["horaires"].strip()
        if hours not in HOURS_FREE_TEXT and not all(HOURS_RE.match(seg.strip()) for seg in hours.split("·")):
            print(f"  ! {where} : horaires « {hours} » non reconnus, la boutique s'affichera sans « Ouvert / Fermé ».")
        s["tz"] = data.get("fuseau_horaire") or tz_of[data["pays"]]
        if not s["tz"]:
            fail(f"{where} : fuseau_horaire obligatoire pour le pays « {data['pays']} » (ex. \"America/Cayenne\").")
        photo = store_photo(path.stem, data, path)
        if photo:
            s["photo"] = photo
        else:
            s.pop("photo", None)
        s["_order"] = (order[data["pays"]], data["region"] != "Île-de-France", data["region"], data["nom"])   # ordre d'affichage par défaut
        stores.append(s)
    if not stores:
        fail("aucune boutique trouvée dans contenu/boutiques/.")
    stores.sort(key=lambda s: s.pop("_order"))
    return stores


# ---- Carte -------------------------------------------------------------------
def load_menu():
    """Rubriques de la carte : contenu/carte/<numéro>-<ancre>.json, dans l'ordre des numéros."""
    lists = read_json(CONTENT / "carte" / "listes.json")
    sections = []
    for path in sorted((CONTENT / "carte").glob("*.json"), key=lambda p: (len(p.stem.split("-")[0]), p.stem)):
        m = re.fullmatch(r"(\d+)-([a-z0-9-]+)", path.stem)
        if not m:
            continue
        sec = read_json(path)
        sec["id"], sec["_file"] = m.group(2), rel(path)
        for b in sec.get("blocs", []):
            if b.get("type") not in ("bases", "pots", "listes", "produits"):
                fail(f"{rel(path)} : type de bloc « {b.get('type')} » inconnu (bases, pots, listes ou produits).")
        sections.append(sec)
    counts = {"toppings": 0, "coulis": 0}
    for sec in sections:
        for b in sec.get("blocs", []):
            for lst in b.get("listes", []):
                if lst.get("compte") in counts:
                    counts[lst["compte"]] += len(lst.get("elements", []))
    return {"sections": sections, "lists": lists, "counts": counts}


def menu_text(value, lang, menu, where):
    """Texte traduit, avec les listes partagées {{liste:nom}} (ou {{Liste:nom}} pour une majuscule)."""
    text = tr(value, lang)

    def repl(m):
        items = menu["lists"].get(m.group(2))
        if items is None:
            fail(f"{where} : la liste « {m.group(2)} » n'existe pas dans contenu/carte/listes.json.")
        words = [tr(i, lang) for i in items]
        joined = ", ".join(words[:-1]) + (" et " if lang == "fr" else " and ") + words[-1] if len(words) > 1 else "".join(words)
        return joined[:1].upper() + joined[1:] if m.group(1) == "L" else joined
    text = re.sub(r"\{\{count:(toppings|coulis)\}\}", lambda m: str(menu["counts"][m.group(1)]), text)
    return re.sub(r"\{\{([lL])iste:([\w-]+)\}\}", repl, text)


def image_tag(src, alt, where):
    path = ROOT / src
    if not path.is_file():
        fail(f"{where} : l'image « {src} » n'existe pas.")
    with Image.open(path) as im:
        w, h = im.size
    return f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" width="{w}" height="{h}">'


def badge(item, lang):
    if not item.get("badge"):
        return ""
    cls = " badge--blue" if item.get("badge_couleur") == "bleu" else ""
    return f'<span class="badge{cls}">{html.escape(tr(item["badge"], lang))}</span>'


LEGEND = {
    "fr": ("contient de la gélatine de porc", "de saison"),
    "en": ("contains pork gelatine", "seasonal"),
}


def menu_html(menu, lang):
    e = html.escape
    tabs, out = [], []
    for sec in menu["sections"]:
        where, sid = sec["_file"], sec["id"]
        T = lambda v: e(menu_text(v, lang, menu, where))   # noqa: E731
        tabs.append(f'<a href="#{sid}"><span aria-hidden="true">{sec.get("icone", "")}</span> {T(sec.get("onglet", sec["titre"]))}</a>')
        body = []
        for b in sec.get("blocs", []):
            if b["type"] == "bases":
                cells = []
                for base in b["bases"]:
                    cls = f' base--{e(base["style"])}' if base.get("style") else ""
                    ico = "{{icon:%s}} " % base["icone"] if base.get("icone") else ""
                    cells.append(f'<div class="base{cls}"><b>{ico}{T(base["nom"])}</b><span>{T(base.get("texte"))}</span></div>')
                body.append('<div class="bases">' + "".join(cells) + "</div>")
            elif b["type"] == "pots":
                if b.get("titre"):
                    body.append(f'<h3 class="group-title">{T(b["titre"])}</h3>')
                cards = [f'<article class="pot-card">{image_tag(p["image"], menu_text(p["nom"], lang, menu, where), where)}'
                         f'{badge(p, lang)}<h4>{T(p["nom"])}</h4><p>{T(p.get("detail"))}</p></article>' for p in b["pots"]]
                body.append('<div class="pots-grid">' + "".join(cards) + "</div>")
            elif b["type"] == "listes":
                cols, flagged = [], -1
                for i, lst in enumerate(b["listes"]):
                    lis = []
                    for it in lst.get("elements", []):
                        flags = [f for f in ("porc", "saison") if isinstance(it, dict) and it.get(f)]
                        cls = " ".join({"porc": "pork", "saison": "season"}[f] for f in flags)
                        note = "".join(f'<span class="sr-only"> ({LEGEND[lang][0 if f == "porc" else 1]})</span>' for f in flags)
                        lis.append(f'<li{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{T(it)}{note}</li>')
                        if flags:
                            flagged = i
                    cols.append([f'<div class="topping-col"><h3>{T(lst["titre"])}</h3><ul class="tlist">{"".join(lis)}</ul>', "</div>"])
                if flagged >= 0:
                    pork, season = LEGEND[lang]
                    cols[flagged].insert(1, f'<p class="legend" aria-hidden="true"><span class="pork-dot"></span>{pork}<br><span class="season-dot"></span>{season}</p>')
                body.append('<div class="topping-cols">' + "".join("".join(c) for c in cols) + "</div>")
            else:
                items = []
                for p in b["produits"]:
                    name = menu_text(p["nom"], lang, menu, where)
                    if p.get("image"):
                        media = image_tag(p["image"], name, where)
                    else:
                        colors = p.get("fond", ["#fff3c4", "#ffe1e6"])
                        if not all(re.fullmatch(r"#[0-9a-fA-F]{3,8}", c) for c in colors):
                            fail(f"{where} : « fond » doit contenir des couleurs au format #rrggbb.")
                        media = (f'<span class="item-emoji" style="background:linear-gradient(135deg,{colors[0]},{colors[-1]})" '
                                 f'aria-hidden="true">{p.get("emoji", "🍦")}</span>')
                    parts = [f"<h3>{e(name)} {badge(p, lang)}</h3>".replace(" </h3>", "</h3>")]
                    if p.get("description"):
                        parts.append(f'<p class="meta">{T(p["description"])}</p>')
                    for ln in p.get("lignes", []):
                        title = f'<b>{T(ln["titre"])}</b> ' if ln.get("titre") else ""
                        parts.append(f'<p class="meta">{title}{T(ln.get("texte"))}</p>')
                    if p.get("options"):
                        opts = "".join(f'<li>{"<b>" + T(o["nom"]) + "</b> " if o.get("nom") else ""}{T(o.get("texte"))}</li>'.replace(" </li>", "</li>")
                                       for o in p["options"])
                        parts.append(f'<ul class="opts">{opts}</ul>')
                    items.append(f'<article class="item">{media}<div>{"".join(parts)}</div></article>')
                body.append('<div class="items">' + "".join(items) + "</div>")
        out.append(f'<section class="menu-sec" id="{sid}" aria-labelledby="t-{sid}">\n'
                   f'    <header class="sec-head"><span class="sec-ico" aria-hidden="true">{sec.get("icone", "")}</span>'
                   f'<div><h2 id="t-{sid}">{T(sec["titre"])}</h2><p>{T(sec.get("sous_titre"))}</p></div></header>\n    '
                   + "\n    ".join(body) + "\n  </section>")
    return "\n    ".join(tabs), "\n\n  ".join(out)


def menu_jsonld(menu, lang):
    halal = "https://schema.org/HalalDiet"
    sections = []
    for sec in menu["sections"]:
        where = sec["_file"]
        T = lambda v: strip_tags(menu_text(v, lang, menu, where))   # noqa: E731
        s = {"@type": "MenuSection", "name": T(sec["titre"])}
        if sec.get("sous_titre"):
            s["description"] = T(sec["sous_titre"])
        items = []
        for b in sec.get("blocs", []):
            for p in b.get("pots", []) + b.get("produits", []):
                desc = [T(p.get("detail") or p.get("description"))]
                desc += [(T(ln.get("titre")) + " : " if ln.get("titre") else "") + T(ln.get("texte")) for ln in p.get("lignes", [])]
                desc += [" ".join(filter(None, (T(o.get("nom")), T(o.get("texte"))))) for o in p.get("options", [])]
                it = {"@type": "MenuItem", "name": T(p["nom"])}
                if any(desc):
                    it["description"] = " ; ".join(d for d in desc if d)
                if sec.get("halal") or p.get("halal"):
                    it["suitableForDiet"] = halal
                items.append(it)
            for lst in b.get("listes", []):
                s["description"] = s.get("description", "") + f" — {T(lst['titre'])} : " + ", ".join(T(i) for i in lst.get("elements", []))
        if items:
            s["hasMenuItem"] = items
        sections.append(s)
    return ld({"@context": "https://schema.org", "@type": "Menu",
               "name": "Carte Yogurt Factory" if lang == "fr" else "Yogurt Factory menu",
               "url": page_url(lang, "carte.html"), "inLanguage": lang,
               "description": "Carte indicative du réseau Yogurt Factory. Les prix sont fixés et affichés par chaque boutique." if lang == "fr"
               else "Indicative menu of the Yogurt Factory network. Prices are set and displayed by each store.",
               "hasMenuSection": sections})


# ---- Fidélité ----------------------------------------------------------------
def load_rewards():
    data = read_json(CONTENT / "fidelite.json").get("recompenses", [])
    pts = [r.get("points") for r in data]
    if not data or not all(isinstance(p, int) and p > 0 for p in pts) or pts != sorted(pts):
        fail("contenu/fidelite.json : chaque récompense doit avoir un nombre de points entier, du plus petit au plus grand.")
    return data


def rewards_html(rewards, lang):
    return "\n        ".join(
        f'<li class="reward" data-points="{r["points"]}"><span class="pts-badge">{r["points"]}<small>points</small></span>'
        f'<b>{html.escape(tr(r, lang))}</b><span class="state"></span></li>' for r in rewards)


def data_js(settings, countries, stores):
    """assets/js/data.js : seul fichier JS généré, lu par main.js."""
    dump = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")   # noqa: E731
    return ("/* Généré par build.py depuis contenu/ : ne pas modifier à la main. */\n"
            f"window.YF_SETTINGS={dump(settings)};\n"
            f"window.YF_COUNTRIES={dump([{'name': c['name'], 'en': c['en']} for c in countries])};\n"
            f"window.YF_STORES={dump(stores)};\n")


class TextExtractor(HTMLParser):
    """Convertit le contenu principal d'une page en Markdown simple (pour llms-full.txt)."""
    SKIP = {"script", "style", "svg", "nav", "form", "button", "noscript"}
    VOID = {"img", "br", "input", "meta", "link", "hr", "source", "wbr", "path", "circle", "rect"}

    def __init__(self):
        super().__init__()
        self.out, self.stack = [], []   # pile des balises ouvertes : (tag, ignorée ?)

    @property
    def skip(self):
        return any(s for _, s in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        hide = tag in self.SKIP or a.get("aria-hidden") == "true" or "hidden" in a
        if tag not in self.VOID:
            self.stack.append((tag, hide))
        if hide or self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in ("p", "div", "section", "article", "address", "tr", "details", "summary"):
            self.out.append("\n")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag == "br":
            self.out.append("\n")
        elif tag in ("span", "b", "strong", "em", "a", "small"):
            self.out.append(" ")

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.skip:
            self.out.append(re.sub(r"\s+", " ", data))

    def text(self):
        t = "".join(self.out)
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"\n[ \t]+", "\n", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()


def page_markdown(raw):
    main = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    p = TextExtractor()
    p.feed(main)
    return p.text()


OG_FONTS = SRC / "og-fonts"
# Image produit mise en avant sur l'aperçu de chaque page (réseaux sociaux, Discord, WhatsApp…)
OG_PRODUCT = {
    "index.html": "images/sundae.webp", "carte.html": "images/menu/beau.webp", "fidelite.html": "images/menu/superbe.webp",
    "boutiques.html": "images/boutique.webp", "franchise.html": "images/video-cover.webp", "concept.html": "images/boutique.webp",
    "recrutement.html": "images/topping-smarties.webp", "contact.html": "images/pot-framboise.webp",
}


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split(" "):
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            lines.append(line); line = word
    return lines + [line] if line else lines


def make_og(filename, headline, sub, product):
    """Carte de partage 1200×630 aux couleurs de la marque."""
    from PIL import ImageDraw, ImageFont
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#e3232b")
    d = ImageDraw.Draw(img)
    for y in range(18, H, 26):                      # trame de points
        for x in range(18, W, 26):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#e8434a")
    # Photo produit dans un cercle blanc
    cx, cy, r = 960, 330, 215
    d.ellipse((cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), fill="#ea4b52")
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white")
    src = Image.open(ROOT / product).convert("RGBA")
    flat = Image.new("RGBA", src.size, "white")
    flat.alpha_composite(src)                        # fond transparent -> blanc
    src = flat.convert("RGB")
    D = 2 * r - 24
    if "/menu/" in product or product.endswith(("sundae.webp", "donut.webp")):
        # Produit détouré : on l'affiche en entier, centré dans le cercle
        src.thumbnail((int(D * .78), int(D * .78)), Image.LANCZOS)
        ph = Image.new("RGB", (D, D), "white")
        ph.paste(src, ((D - src.width) // 2, (D - src.height) // 2))
    else:
        s = min(src.size)
        ph = src.crop(((src.width - s) // 2, (src.height - s) // 2, (src.width + s) // 2, (src.height + s) // 2)).resize((D, D), Image.LANCZOS)
    mask = Image.new("L", ph.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, ph.width, ph.height), fill=255)
    img.paste(ph, (cx - r + 12, cy - r + 12), mask)
    # Logo
    logo = Image.open(ROOT / "images/logo.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
    img.paste(logo, (64, 52), logo)
    f_brand = ImageFont.truetype(str(OG_FONTS / "Lobster.ttf"), 44)
    d.text((176, 70), "Yogurt Factory", font=f_brand, fill="#ffc845")
    # Titre (taille adaptée à la longueur)
    for size in (74, 66, 58, 50):
        f_title = ImageFont.truetype(str(OG_FONTS / "Montserrat-ExtraBold.ttf"), size)
        lines = _wrap(d, headline, f_title, 620)
        if len(lines) <= 3:
            break
    y = 200
    for line in lines[:3]:
        d.text((64, y), line, font=f_title, fill="white"); y += int(size * 1.12)
    f_sub = ImageFont.truetype(str(OG_FONTS / "Poppins-Medium.ttf"), 27)
    y += 14
    for line in _wrap(d, sub, f_sub, 610)[:3]:
        d.text((64, y), line, font=f_sub, fill="#ffe3e1"); y += 40
    f_url = ImageFont.truetype(str(OG_FONTS / "Poppins-Medium.ttf"), 24)
    d.rounded_rectangle((64, 548, 64 + d.textlength("yogurtfactory.fr", font=f_url) + 40, 592), radius=22, fill="#2a1a1a")
    d.text((84, 553), "yogurtfactory.fr", font=f_url, fill="white")
    out = DIST / "images" / "og" / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=80, optimize=True, progressive=True)
    return "images/og/" + filename


def build_images():
    icons = DIST / "images" / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    logo = Image.open(ROOT / "images/logo.png").convert("RGBA")
    for size, name in [(32, "icon-32.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
        logo.resize((size, size), Image.LANCZOS).save(icons / name, optimize=True)
    bg = Image.new("RGBA", (180, 180), "#e3232b")
    bg.alpha_composite(logo.resize((164, 164), Image.LANCZOS), (8, 8))
    bg.convert("RGB").save(icons / "apple-touch-icon.png", optimize=True)
    logo.resize((48, 48), Image.LANCZOS).save(DIST / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    photo = Image.open(ROOT / "images/boutique.webp").convert("RGB")
    w, h = photo.size
    target = 1200 / 630
    if w / h > target:
        nw = int(h * target); photo = photo.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / target); photo = photo.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    og = photo.resize((1200, 630), Image.LANCZOS).convert("RGBA")
    og.alpha_composite(logo.resize((220, 220), Image.LANCZOS), (40, 370))
    og.convert("RGB").save(DIST / "images" / "og-image.jpg", quality=84, optimize=True)


def optimize_images():
    """Allège les photos publiées : 1600 px de large au plus, WebP recompressé.
    Les photos de boutiques déposées en JPG/PNG sont converties en WebP 800 px."""
    saved = 0
    for f in (DIST / "images").rglob("*"):
        if f.suffix.lower() not in PHOTO_EXT or f.parent.name == "icons" or f.name.startswith(("logo", "og-")):
            continue
        store = f.parent.name == "boutiques"
        if store and f.suffix.lower() != ".webp":
            target = f.with_suffix(".webp")
        elif f.suffix.lower() == ".webp" and (f.stat().st_size > 250_000 or store):
            target = f
        else:
            continue
        before = f.stat().st_size
        with Image.open(f) as im:
            im.load()
            max_w = 800 if store else 1600
            if im.width > max_w:
                im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            tmp = target.with_name(target.stem + ".tmp.webp")
            im.save(tmp, "WEBP", quality=80, method=6)
        if target == f and tmp.stat().st_size >= before:
            tmp.unlink()
            continue
        if target != f:
            f.unlink()
        tmp.replace(target)
        saved += before - target.stat().st_size
    if saved > 0:
        print(f"✓ images allégées : {saved / 1024:.0f} Ko gagnés")


# ---- Fichiers pour moteurs de recherche et agents IA ------------------------
ROBOTS = """# Yogurt Factory — robots.txt
# Tous les moteurs de recherche et assistants IA sont les bienvenus.
User-agent: *
Allow: /
Disallow: /404.html

# Moteurs de recherche
User-agent: Googlebot
User-agent: Bingbot
User-agent: DuckDuckBot
User-agent: YandexBot
User-agent: Qwantbot
User-agent: Applebot
User-agent: Baiduspider
User-agent: Slurp
Allow: /

# Assistants et moteurs IA (réponses, citations, résumés)
User-agent: GPTBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: ClaudeBot
User-agent: Claude-User
User-agent: Claude-SearchBot
User-agent: anthropic-ai
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: meta-externalagent
User-agent: MistralAI-User
User-agent: CCBot
User-agent: cohere-ai
User-agent: DuckAssistBot
Allow: /

Sitemap: {site}/sitemap.xml
# Résumé pour les agents IA : {site}/llms.txt
"""

LLMS_INTRO = """# Yogurt Factory

> Yogurt Factory (« la Facto ») est le leader français du frozen yogurt : glace au yaourt 0 % de matières grasses ou sundae vanille, servie avec le plus gros bar à toppings de France ({toppings} toppings et {coulis} coulis à volonté, tant que ça rentre dans le pot). Enseigne créée en 2011 par Ouriel Hodara et Emmanuel Tedesco, réseau de franchise depuis 2016, {stores} boutiques référencées sur le site.

Informations clés :
- Produits : glace au yaourt 0 % MG, sundae vanille, pots Le Mignon (110 g), Le Beau (160 g), Le Magnifique (220 g), Le Superbe (350 g, à partager), Le Parfait (180 g), Le Trognon (90 g, moins de 10 ans) ; bubble waffles, gaufres liégeoises, crêpes, donuts ; bubble tea, smoothies, milkshakes, thés glacés, citronnade, granités ; cafés frappés, boissons chaudes, matcha, ube.
- Halal : les glaces (yaourt et sundae vanille) et les bubble waffles sont halal ; lait pasteurisé et stérilisé. Les bonbons Tagada, Schtroumpfs et Marshmallow contiennent de la gélatine de porc.
- Prix : fixés et affichés par chaque boutique (ils peuvent varier d'une boutique franchisée à l'autre) ; le site ne publie pas de prix.
- Fidélité : 1 € dépensé = 1 point, avec le numéro de téléphone en caisse ou sur borne ; récompenses : {rewards}.
- Franchise : apport ≈ 30 000 €, droit d'entrée 20 000 € HT, kiosques de 15 à 25 m² ou boutiques de 30 à 60 m², contrat de 5 ans.
- Réseaux sociaux : TikTok @yogurt_factory, Instagram @yogurtfactory, Facebook YogurtFactory.fr.

## Pages principales
{pages}

## Données
- [Liste complète des boutiques avec adresses et horaires]({site}/llms-full.txt) : contenu intégral du site en texte brut
- [Plan du site]({site}/sitemap.xml)
"""


def indexnow(urls):
    body = json.dumps({"host": SITE_URL.split("//")[1], "key": INDEXNOW_KEY,
                       "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow :", r.status, "(200/202 = OK)")



SW_TEMPLATE = """/* Yogurt Factory — service worker (généré par build.py)
   - pages : réseau d'abord, copie de secours en cache, page « hors connexion » sinon
   - CSS/JS/polices/images : cache d'abord (fichiers versionnés) */
const VERSION = "yf-%(version)s";
const PRECACHE = %(precache)s;
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match(url.pathname.startsWith("__BASE__/en/") ? "__BASE__/en/offline.html" : "__BASE__/hors-ligne.html"))));
    return;
  }
  const path = url.pathname.slice("__BASE__".length);
  if (/^\\/(assets|images)\\//.test(path) || path === "/favicon.ico") {
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    })));
  }
});
"""


# ---- Build ------------------------------------------------------------------
def build():
    # Contenu éditable : lu et vérifié avant de toucher à dist/ : une erreur laisse le site précédent intact
    settings = load_settings()
    countries = load_countries()
    stores = load_stores(countries)
    menu = load_menu()
    rewards = load_rewards()

    # On vide dist/ sans supprimer le dossier lui-même (il peut être ouvert par un serveur local)
    DIST.mkdir(exist_ok=True)
    for child in DIST.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()

    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copytree(ROOT / "images", DIST / "images", ignore=shutil.ignore_patterns("src"))
    for f in (SRC / "static").iterdir():
        (shutil.copytree if f.is_dir() else shutil.copy2)(f, DIST / f.name)

    (DIST / "assets/js/data.js").write_text(data_js(settings, countries, stores), encoding="utf-8")
    for name in (".htaccess", "_headers"):
        f = DIST / name
        f.write_text(f.read_text(encoding="utf-8").replace("__CSP__", csp_string(settings)), encoding="utf-8")
    optimize_images()
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")

    # Minification + compatibilité navigateurs
    modern = True
    for rel, loader in [("assets/css/style.css", "css"), ("assets/css/fonts.css", "css"),
                        ("assets/js/main.js", "js"), ("assets/js/data.js", "js"), ("assets/js/prefs.js", "js")]:
        p = DIST / rel
        if not (modern and esbuild(p, loader)):
            modern = False
            if loader == "css":
                p.write_text(minify_css_simple(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("✓ CSS/JS", "minifiés et transpilés (esbuild)" if modern else "minifiés (mode simple)")

    build_images()
    (DIST / "site.webmanifest").write_text(json.dumps({
        "name": SITE_NAME, "short_name": SITE_NAME, "description": "Glace au yaourt 0 % et le plus gros bar à toppings de France",
        "lang": "fr", "start_url": BASE + "/", "scope": BASE + "/", "display": "standalone",
        "background_color": "#fff7ee", "theme_color": "#e3232b",
        "icons": [{"src": "images/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "images/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    versions = {k: fhash(DIST / p) for k, p in [
        ("v_css", "assets/css/style.css"), ("v_fonts", "assets/css/fonts.css"), ("v_prefs", "assets/js/prefs.js"),
        ("v_main", "assets/js/main.js"), ("v_data", "assets/js/data.js")]}
    verification = "".join(f'<meta name="{n}" content="{v}">\n' for n, v in [
        ("google-site-verification", GOOGLE_SITE_VERIFICATION), ("msvalidate.01", BING_SITE_VERIFICATION),
        ("yandex-verification", YANDEX_VERIFICATION)] if v)

    pot = (SRC / "partials" / "error-pot.svg").read_text(encoding="utf-8")
    pages, llm_pages, full_text = [], {"fr": [], "en": []}, []
    for lang, L in LANGS.items():
        src_dir = SRC / L["pages"]
        if not src_dir.exists():
            continue
        (DIST / L["dir"]).mkdir(exist_ok=True)
        other = "en" if lang == "fr" else "fr"
        header = (SRC / "partials" / L["header"]).read_text(encoding="utf-8")
        footer = (SRC / "partials" / L["footer"]).read_text(encoding="utf-8")
        for page in sorted(src_dir.glob("*.html"), key=lambda p: (p.name != "index.html", p.name)):
            raw = page.read_text(encoding="utf-8")
            if "{{carte:" in raw:
                tabs, body = menu_html(menu, lang)
                raw = raw.replace("{{carte:onglets}}", tabs).replace("{{carte:rubriques}}", body)
            raw = (raw.replace("{{fidelite:recompenses}}", rewards_html(rewards, lang))
                   .replace("{{fidelite:max}}", str(rewards[-1]["points"] + 10))
                   .replace("{{count:stores}}", str(len(stores))).replace("{{count:cities}}", str(len({s["city"] for s in stores})))
                   .replace("{{count:toppings}}", str(menu["counts"]["toppings"])).replace("{{count:coulis}}", str(menu["counts"]["coulis"])))
            m = re.match(r"\s*<!--(.*?)-->\s*", raw, re.S)
            meta = {}
            if m:
                for line in m.group(1).strip().splitlines():
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
                raw = raw[m.end():]
            title = html.unescape(meta.get("title", SITE_NAME))
            desc = html.unescape(meta.get("description", ""))
            is404 = meta.get("kind") == "error"   # pages d'erreur et utilitaires : non indexées
            url = page_url(lang, page.name)
            has_twin = (SRC / LANGS[other]["pages"] / page.name).exists()
            alt_url = (page_url(other, page.name) if has_twin else page_url(other, "index.html")).replace(SITE_URL, "")
            short = title.split(" — ")[0].split(" | ")[0]

            extra = ""
            if "jsonld" in meta:
                extra += (SRC / meta["jsonld"]).read_text(encoding="utf-8")
            if page.name == "carte.html":
                extra += menu_jsonld(menu, lang)
            if page.name == "boutiques.html":
                extra += store_jsonld(stores)
                raw = raw.replace('<div class="store-list"></div>', '<div class="store-list">' + store_cards(stores) + "</div>")
            if page.name != "index.html" and not is404:
                extra += breadcrumb_jsonld(short, url, "Home" if lang == "en" else "Accueil", page_url(lang, "index.html"))
            extra += faq_jsonld(raw)
            for key, svg in ICONS.items():
                raw = raw.replace("{{icon:%s}}" % key, svg)
            raw = re.sub(r"\{\{pot:([^}]*)\}\}", lambda mm: pot.replace("{{pot-label}}", html.escape(mm.group(1))), raw)
            raw = re.sub(r"<img (?![^>]*decoding)", '<img decoding="async" ', raw)
            raw = re.sub(r'(src|href|data-src)="(images|assets)/', r'\1="/\2/', raw)   # chemins absolus (valables dans /en/)
            nav = header.replace("{{alt_href}}", alt_url)
            for key in NAV_KEYS:
                nav = nav.replace("{{nav:%s}}" % key, ' aria-current="page"' if meta.get("nav") == key else "")
            nav = re.sub(r'(src|href)="(images|assets)/', r'\1="/\2/', nav)
            foot = re.sub(r'(src|href)="(images|assets)/', r'\1="/\2/', footer)

            og_image = "images/og-image.jpg"
            if not is404:
                og_image = make_og(("en-" if lang == "en" else "") + page.stem + ".jpg", html.unescape(meta.get("og_title", short)),
                                   html.unescape(meta.get("og_sub", desc)), OG_PRODUCT.get(page.name, "images/sundae.webp"))
            if is404:
                alternates = ""
            else:
                fr_u = page_url("fr", page.name)
                alternates = f'<link rel="alternate" hreflang="fr" href="{fr_u}">\n'
                if (SRC / LANGS["en"]["pages"] / page.name).exists():
                    alternates += f'<link rel="alternate" hreflang="en" href="{page_url("en", page.name)}">\n'
                alternates += f'<link rel="alternate" hreflang="x-default" href="{fr_u}">'
            out = HEAD.format(
                title=html.escape(title, quote=True), description=html.escape(desc, quote=True),
                og_image=og_image, og_alt=html.escape(html.unescape(meta.get("og_title", short)).replace("\u00a0", " ") + " — Yogurt Factory", quote=True),
                url=url, site=SITE_URL, extra_head=extra, verification=verification, alternates=alternates,
                html_lang=L["html"], og_locale=L["locale"], og_locale_alt=LANGS[other]["locale"],
                data_base=f' data-base="{BASE}"' if BASE else "",
                csp=csp_string(settings, meta=True),
                twitter_labels=(
                    '<meta name="twitter:label1" content="Stores">\n<meta name="twitter:data1" content="90 locations in 10 countries">\n'
                    '<meta name="twitter:label2" content="Loyalty">\n<meta name="twitter:data2" content="€1 spent = 1 point">') if lang == "en" else (
                    '<meta name="twitter:label1" content="Boutiques">\n<meta name="twitter:data1" content="90 points de vente dans 10 pays">\n'
                    '<meta name="twitter:label2" content="Fidélité">\n<meta name="twitter:data2" content="1 € dépensé = 1 point">'),
                base=f'<base href="/{L["dir"]}">\n' if is404 else "",
                robots="noindex, follow" if (is404 or BASE) else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
                **versions,
            ) + nav + '<main id="main">\n' + raw.strip() + "\n</main>\n" + foot + FOOT.format(**versions)
            out = re.sub(r"<!--(?!\[if).*?-->\s*", "", out, flags=re.S)   # aucun commentaire de travail en ligne
            if BASE:   # chemins absolus « /… » → « /sous-dossier/… »
                out = re.sub(r'(href|src|data-src)="/(?!/)', lambda mm: f'{mm.group(1)}="{BASE}/', out)
            leftovers = re.findall(r"\{\{[^}]+\}\}", out)
            assert not leftovers, f"{lang}/{page.name} : balises non remplacées {leftovers}"
            (DIST / L["dir"] / slug(lang, page.name)).write_text(out, encoding="utf-8")
            if not is404:
                imgs = sorted(set(re.findall(r'<img src="/(images/[^"]+)"', raw)))
                pages.append((lang, page.name, imgs))
                llm_pages[lang].append(f"- [{short}]({url}) : {desc}")
                full_text.append(f"\n\n---\n\n# {title}\nURL : {url}\n\n" + page_markdown(raw))
            print("✓", L["dir"] + slug(lang, page.name))

    # Service worker (hors connexion + cache)
    precache = ["/hors-ligne.html", "/en/offline.html", f"/assets/css/style.css?v={versions['v_css']}", f"/assets/css/fonts.css?v={versions['v_fonts']}",
                f"/assets/js/main.js?v={versions['v_main']}", f"/assets/js/data.js?v={versions['v_data']}",
                f"/assets/js/prefs.js?v={versions['v_prefs']}", "/images/logo.png",
                "/assets/fonts/poppins-400-normal-latin.woff2", "/assets/fonts/montserrat-100-900-normal-latin.woff2",
                "/assets/fonts/lobster-400-normal-latin.woff2"]
    precache = [BASE + p for p in precache]
    sw_version = hashlib.md5("".join(precache).encode()).hexdigest()[:8]
    (DIST / "sw.js").write_text((SW_TEMPLATE % {"version": sw_version, "precache": json.dumps(precache)}).replace("__BASE__", BASE), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")   # GitHub Pages : publier aussi .well-known, _headers…

    # Sitemap multilingue (avec images et alternatives de langue)
    today = date.today().isoformat()
    urls = ""
    has_en = {n for lg, n, _ in pages if lg == "en"}
    for lang, name, imgs in pages:
        loc = page_url(lang, name)
        prio = "1.0" if name == "index.html" else "0.9" if name in ("carte.html", "boutiques.html", "franchise.html", "fidelite.html") else "0.4" if name in (
            "mentions-legales.html", "confidentialite.html", "cookies.html", "cgu.html", "accessibilite.html", "plan-du-site.html") else "0.7"
        if lang == "en":
            prio = f"{max(0.3, float(prio) - 0.1):.1f}"
        alts = ""
        if name in has_en:
            alts = (f'<xhtml:link rel="alternate" hreflang="fr" href="{page_url("fr", name)}"/>'
                    f'<xhtml:link rel="alternate" hreflang="en" href="{page_url("en", name)}"/>'
                    f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("fr", name)}"/>')
        img_tags = "".join(f"<image:image><image:loc>{SITE_URL}/{i}</image:loc></image:image>" for i in imgs[:20])
        urls += f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{prio}</priority>{alts}{img_tags}</url>\n"
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + urls + "</urlset>\n", encoding="utf-8")

    # robots.txt, llms.txt, llms-full.txt
    (DIST / "robots.txt").write_text(ROBOTS.format(site=SITE_URL), encoding="utf-8")
    llm_list = "\n".join(llm_pages["fr"]) + ("\n\n## English version\n" + "\n".join(llm_pages["en"]) if llm_pages["en"] else "")
    facts = dict(site=SITE_URL, pages=llm_list, stores=len(stores), toppings=menu["counts"]["toppings"], coulis=menu["counts"]["coulis"],
                 rewards=", ".join(f"{r['points']} points = {r['fr']}" for r in rewards))
    (DIST / "llms.txt").write_text(LLMS_INTRO.format(**facts), encoding="utf-8")
    store_lines = "\n".join(
        f"- {s['name']} ({s['country']}) : {', '.join(filter(None, (s['center'], s['address'])))}, {s['zip']} {s['city']} — {s['hours']}"
        + (f" — tél. {s['phone']}" if s.get("phone") else "") for s in stores)
    (DIST / "llms-full.txt").write_text(
        LLMS_INTRO.format(**facts) + "".join(full_text)
        + f"\n\n---\n\n# Liste des boutiques ({len(stores)})\n\n" + store_lines + "\n", encoding="utf-8")
    print("✓ sitemap.xml, robots.txt, llms.txt, llms-full.txt, icônes, image de partage")

    size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"→ dist/ prêt : {size / 1024 / 1024:.1f} Mo")
    return [page_url(lg, n) for lg, n, _ in pages]


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")   # accents et symboles dans la console Windows
    built = build()
    if "--indexnow" in sys.argv:
        indexnow(built + [SITE_URL + "/llms.txt"])
