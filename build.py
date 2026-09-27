"""
Génère le site de production dans le dossier dist/.

    python build.py              construit le site
    python build.py --indexnow   construit puis signale les pages à Bing, Yandex, Seznam, Naver… (après mise en ligne)

Sources :
- _src/partials/header.html, footer.html : communs à toutes les pages
- _src/pages/*.html : contenu de chaque page, précédé d'un bloc d'en-tête :
      <!--
      title: Titre de la page — suite du titre
      description: Description pour Google (≈155 caractères)
      nav: carte            (lien du menu à mettre en surbrillance)
      jsonld: partials/x.html  (données structurées supplémentaires, facultatif)
      -->
- _src/static/ : fichiers copiés tels quels à la racine (.htaccess, _headers…)
- assets/, images/ : copiés dans dist/ (sauf images/src/, les originaux)

Le dossier dist/ est entièrement régénéré à chaque build : c'est lui qu'on met en ligne.
Si Node.js est installé, CSS et JS sont minifiés et rendus compatibles avec les anciens
navigateurs (esbuild) ; sinon une minification simple est appliquée.
"""
import hashlib
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
# Codes de validation des outils pour webmasters (laisser vide si non utilisé)
GOOGLE_SITE_VERIFICATION = ""   # Google Search Console
BING_SITE_VERIFICATION = ""     # Bing Webmaster Tools (alimente aussi DuckDuckGo, Qwant, Ecosia, Yahoo)
YANDEX_VERIFICATION = ""
# Clé IndexNow (fichier <clé>.txt publié à la racine)
INDEXNOW_KEY = "7f3c9a2e5b8d4f16a0c3e9b72d5f8a14"
# Navigateurs ciblés (esbuild) : couvre ~98 % du parc, iPhone depuis iOS 13
BROWSER_TARGETS = "chrome80,edge80,firefox78,safari13,ios13,opera67"
ESBUILD = "esbuild@0.25.0"

# Langues : le français à la racine, l'anglais dans /en/ (pages dans _src/pages-en/, même nom de fichier que la version FR)
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


NAV_KEYS = ["concept", "carte", "fidelite", "boutiques", "franchise", "recrutement", "contact"]
ICONS = {
    "halal": '<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">'
             '<path d="M13.5 3.2A9 9 0 1 0 20.8 16 7.2 7.2 0 1 1 13.5 3.2z"/>'
             '<path d="M17.6 6.3l.9 2.1 2.2.2-1.7 1.5.5 2.2-1.9-1.2-1.9 1.2.5-2.2-1.7-1.5 2.2-.2z"/></svg>',
}

HEAD = """<!doctype html>
<html lang="{html_lang}" class="no-js">
<head>
<meta charset="utf-8">
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

FOOT = """<script src="/assets/js/stores.js?v={v_stores}" defer></script>
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


def load_stores():
    """Lit assets/js/stores.js (objets JS) et le convertit en liste de dicts."""
    src = (ROOT / "assets/js/stores.js").read_text(encoding="utf-8")
    out = []
    for row in re.findall(r"\{ name: .*? \}", src):
        out.append(json.loads(re.sub(r'([{,]\s*)([a-zA-Z]+):', r'\1"\2":', row)))
    return out


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
        f'<h3>{e(s["name"])}</h3><address>{e(s["center"])} · {e(s["address"])}, {e(s.get("zip", ""))} {e(s["city"])}</address>'
        f'<div class="hours">{e(s["hours"])}</div></div></article>' for s in stores)


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

> Yogurt Factory (« la Facto ») est le leader français du frozen yogurt : glace au yaourt 0 % de matières grasses ou sundae vanille, servie avec le plus gros bar à toppings de France (36 toppings et 11 coulis à volonté, tant que ça rentre dans le pot). Enseigne créée en 2011 par Ouriel Hodara et Emmanuel Tedesco, réseau de franchise depuis 2016, 90 points de vente dans 10 pays.

Informations clés :
- Produits : glace au yaourt 0 % MG, sundae vanille, pots Le Mignon (110 g), Le Beau (160 g), Le Magnifique (220 g), Le Superbe (350 g, à partager), Le Parfait (180 g), Le Trognon (90 g, moins de 10 ans) ; bubble waffles, gaufres liégeoises, crêpes, donuts ; bubble tea, smoothies, milkshakes, thés glacés, citronnade, granités ; cafés frappés, boissons chaudes, matcha, ube.
- Halal : les glaces (yaourt et sundae vanille) et les bubble waffles sont halal ; lait pasteurisé et stérilisé. Les bonbons Tagada, Schtroumpfs et Marshmallow contiennent de la gélatine de porc.
- Prix : fixés et affichés par chaque boutique (ils peuvent varier d'une boutique franchisée à l'autre) ; le site ne publie pas de prix.
- Fidélité : 1 € dépensé = 1 point, avec le numéro de téléphone en caisse ou sur borne ; récompenses de 30 points (petit thé glacé) à 120 points (Le Superbe).
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
    }).catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match(url.pathname.startsWith("/en/") ? "/en/offline.html" : "/hors-ligne.html"))));
    return;
  }
  if (/^\\/(assets|images)\\//.test(url.pathname) || url.pathname === "/favicon.ico") {
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    })));
  }
});
"""


# ---- Build ------------------------------------------------------------------
def build():
    # On vide dist/ sans supprimer le dossier lui-même (il peut être ouvert par un serveur local)
    DIST.mkdir(exist_ok=True)
    for child in DIST.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()

    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copytree(ROOT / "images", DIST / "images", ignore=shutil.ignore_patterns("src"))
    for f in (SRC / "static").iterdir():
        (shutil.copytree if f.is_dir() else shutil.copy2)(f, DIST / f.name)
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")

    # Minification + compatibilité navigateurs
    modern = True
    for rel, loader in [("assets/css/style.css", "css"), ("assets/css/fonts.css", "css"),
                        ("assets/js/main.js", "js"), ("assets/js/stores.js", "js"), ("assets/js/prefs.js", "js")]:
        p = DIST / rel
        if not (modern and esbuild(p, loader)):
            modern = False
            if loader == "css":
                p.write_text(minify_css_simple(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("✓ CSS/JS", "minifiés et transpilés (esbuild)" if modern else "minifiés (mode simple)")

    build_images()
    (DIST / "site.webmanifest").write_text(json.dumps({
        "name": SITE_NAME, "short_name": SITE_NAME, "description": "Glace au yaourt 0 % et le plus gros bar à toppings de France",
        "lang": "fr", "start_url": "/", "scope": "/", "display": "standalone",
        "background_color": "#fff7ee", "theme_color": "#e3232b",
        "icons": [{"src": "images/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "images/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    versions = {k: fhash(DIST / p) for k, p in [
        ("v_css", "assets/css/style.css"), ("v_fonts", "assets/css/fonts.css"), ("v_prefs", "assets/js/prefs.js"),
        ("v_main", "assets/js/main.js"), ("v_stores", "assets/js/stores.js")]}
    verification = "".join(f'<meta name="{n}" content="{v}">\n' for n, v in [
        ("google-site-verification", GOOGLE_SITE_VERIFICATION), ("msvalidate.01", BING_SITE_VERIFICATION),
        ("yandex-verification", YANDEX_VERIFICATION)] if v)

    stores = load_stores()
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
            raw = raw.replace("{{count:stores}}", str(len(stores))).replace("{{count:cities}}", str(len({s["city"] for s in stores})))
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
                twitter_labels=(
                    '<meta name="twitter:label1" content="Stores">\n<meta name="twitter:data1" content="90 locations in 10 countries">\n'
                    '<meta name="twitter:label2" content="Loyalty">\n<meta name="twitter:data2" content="€1 spent = 1 point">') if lang == "en" else (
                    '<meta name="twitter:label1" content="Boutiques">\n<meta name="twitter:data1" content="90 points de vente dans 10 pays">\n'
                    '<meta name="twitter:label2" content="Fidélité">\n<meta name="twitter:data2" content="1 € dépensé = 1 point">'),
                base=f'<base href="/{L["dir"]}">\n' if is404 else "",
                robots="noindex, follow" if is404 else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
                **versions,
            ) + nav + '<main id="main">\n' + raw.strip() + "\n</main>\n" + foot + FOOT.format(**versions)
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
                f"/assets/js/main.js?v={versions['v_main']}", f"/assets/js/stores.js?v={versions['v_stores']}",
                f"/assets/js/prefs.js?v={versions['v_prefs']}", "/images/logo.png",
                "/assets/fonts/poppins-400-normal-latin.woff2", "/assets/fonts/montserrat-100-900-normal-latin.woff2",
                "/assets/fonts/lobster-400-normal-latin.woff2"]
    sw_version = hashlib.md5("".join(precache).encode()).hexdigest()[:8]
    (DIST / "sw.js").write_text(SW_TEMPLATE % {"version": sw_version, "precache": json.dumps(precache)}, encoding="utf-8")

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
    (DIST / "llms.txt").write_text(LLMS_INTRO.format(site=SITE_URL, pages=llm_list), encoding="utf-8")
    store_lines = "\n".join(
        f"- {s['name']} ({s['country']}) : {s['center']}, {s['address']}, {s.get('zip', '')} {s['city']} — {s['hours']}"
        + (f" — tél. {s['phone']}" if s.get("phone") else "") for s in stores)
    (DIST / "llms-full.txt").write_text(
        LLMS_INTRO.format(site=SITE_URL, pages=llm_list) + "".join(full_text)
        + f"\n\n---\n\n# Liste des boutiques ({len(stores)})\n\n" + store_lines + "\n", encoding="utf-8")
    print("✓ sitemap.xml, robots.txt, llms.txt, llms-full.txt, icônes, image de partage")

    size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"→ dist/ prêt : {size / 1024 / 1024:.1f} Mo")
    return [page_url(lg, n) for lg, n, _ in pages]


if __name__ == "__main__":
    built = build()
    if "--indexnow" in sys.argv:
        indexnow(built + [SITE_URL + "/llms.txt"])
