/* ==========================================================================
   Yogurt Factory — comportements du site (toutes les pages)

   Ce fichier est chargé en dernier, après « data.js » que build.py génère à
   partir du dossier contenu/ :
     window.YF_SETTINGS   réglages (contenu/reglages.json)
     window.YF_COUNTRIES  pays, dans l'ordre d'affichage (contenu/pays.json)
     window.YF_STORES     boutiques (contenu/boutiques/*.json)
   On ne modifie donc jamais les boutiques ou les adresses e-mail ici.

   Organisation : une fonction auto-exécutée par fonctionnalité, qui s'arrête
   d'elle-même si la page ne contient pas les éléments dont elle a besoin.
   Pour retirer une fonctionnalité, il suffit de supprimer son bloc.

   Textes affichés par le script : objet I18N (français / anglais) plus bas.
   Sécurité : toute donnée insérée en HTML passe par esc().
   ========================================================================== */

const YF_SETTINGS = window.YF_SETTINGS || {};
const YF_CONFIG = {
  forms: YF_SETTINGS.forms || {},
  protectContent: YF_SETTINGS.protectContent !== false,
  storesPerPage: YF_SETTINGS.storesPerPage || 12,
  defaultStorePhoto: "images/boutique-thumb.webp"
};

document.documentElement.classList.remove("no-js");
// Préfixe des chemins quand le site est publié dans un sous-dossier (GitHub Pages) ; vide en production.
const BASE = document.documentElement.dataset.base || "";
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
/* ---- Textes (français / anglais) ------------------------------------------
   La langue est lue sur <html lang>. Pour ajouter un texte : même clé dans
   « fr » et « en », puis t("cle") ou t("cle", argument) dans le code. */
const LANG = (document.documentElement.lang || "fr").slice(0, 2) === "en" ? "en" : "fr";
const I18N = {
  fr: {
    pages: { stores: "boutiques.html", franchise: "franchise.html", thanks: "merci.html", careers: "recrutement.html" },
    menuOpen: "Ouvrir le menu", menuClose: "Fermer le menu",
    hoursVar: "Horaires variables", soon: "Ferme bientôt · ", openUntil: "Ouvert · ferme à ", closedOpensAt: "Fermé · ouvre à ",
    closedOpens: (day, h) => "Fermé · ouvre " + day + " à " + h, closed: "Fermé", tomorrow: "demain",
    days: ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"], midnight: "minuit",
    hm: (h, m) => h + "h" + (m ? String(m).padStart(2, "0") : ""),
    ratingAria: (r, n) => `Note Google ${r} sur 5${n ? ", " + n + " avis" : ""}`, reviews: (n) => `(${n} avis)`, seeReviews: "★ Voir les avis Google",
    myFacto: "⭐ Ma Facto", myFactoPrefix: "⭐ Ma Facto · ", route: "Itinéraire →", routeBtn: "🧭 Itinéraire", call: "📞 Appeler", onMap: "🗺️ Sur la carte",
    storeAlt: (n) => "Boutique Yogurt Factory " + n, favRemove: "Retirer de mes favoris", favSet: "Définir comme ma Facto",
    allRegions: "Toutes les régions", count: (n, near) => `${n} boutique${n > 1 ? "s" : ""}${near ? " · de la plus proche à la plus éloignée" : ""}`,
    empty: `<b>Pas encore de Facto ici…</b>Essayez une autre ville ou un code postal. Et si c'était vous qui l'ouvriez&nbsp;? <a href="franchise.html">Devenir franchisé →</a>`,
    more: (n) => `Afficher plus (${n} boutique${n > 1 ? "s" : ""})`, sheet: "Voir la fiche", here: "Vous êtes ici",
    geo: "📍 Autour de moi", geoOn: "✕ Autour de moi", geoWait: "Localisation…", geoNone: "Géolocalisation indisponible",
    geoErr: "Impossible de vous localiser : vérifiez l'autorisation de localisation de votre navigateur.",
    results: (n) => `${n} résultat${n > 1 ? "s" : ""}`, pts: "pts", unlocked: "Débloqué ✓", still: (n) => `Encore ${n} pts`,
    next: (n, name) => `Plus que ${n} pts pour : ${name}`, allDone: "Toutes les récompenses sont débloquées, régalez-vous !",
    eggAgain: (n) => `🍦 Encore toi ! ${n}e pluie de toppings. Tu es officiellement accro à la Facto.`,
    eggFirst: "🎉 Bravo, tu as trouvé le bar à toppings secret ! Chut… ça reste entre nous.",
    consoleHint: "Tu lis le code ? On aime les curieux. Indice : ↑ ↑ ↓ ↓ ← → ← → B A 😉\nEt la Facto recrute : ",
    typeMenu: ["Rechercher : ", ["mangue", "Kinder Bueno", "bubble tea", "pistache", "halal", "matcha"]],
    typeStore: ["Ville, code postal… ex. ", ["Paris", "Lyon", "Lille", "Nice", "75015", "Beaugrenelle"]],
    typeHome: ["Trouver une Facto… ex. ", ["Paris", "Marseille", "Lyon", "Toulouse", "Nantes"]],
    formFail: (m) => "Oups, l'envoi a échoué. Réessayez ou écrivez-nous à " + m + ".",
    formMail: (m) => "Votre messagerie va s'ouvrir avec votre message pré-rempli : il ne reste qu'à cliquer sur « Envoyer ». Rien ne s'ouvre ? Écrivez-nous directement à " + m + ".",
    delivery: "🛵 Livraison",
    country: (c) => c, hours: (h) => h
  },
  en: {
    pages: { stores: "stores.html", franchise: "franchise.html", thanks: "thank-you.html", careers: "careers.html" },
    menuOpen: "Open menu", menuClose: "Close menu",
    hoursVar: "Hours vary", soon: "Closing soon · ", openUntil: "Open · closes at ", closedOpensAt: "Closed · opens at ",
    closedOpens: (day, h) => "Closed · opens " + day + " at " + h, closed: "Closed", tomorrow: "tomorrow",
    days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], midnight: "midnight",
    hm: (h, m) => h + ":" + String(m || 0).padStart(2, "0"),
    ratingAria: (r, n) => `Google rating ${r} out of 5${n ? ", " + n + " reviews" : ""}`, reviews: (n) => `(${n} reviews)`, seeReviews: "★ See Google reviews",
    myFacto: "⭐ My Facto", myFactoPrefix: "⭐ My Facto · ", route: "Directions →", routeBtn: "🧭 Directions", call: "📞 Call", onMap: "🗺️ On the map",
    storeAlt: (n) => "Yogurt Factory store " + n, favRemove: "Remove from favourites", favSet: "Make it my Facto",
    allRegions: "All regions", count: (n, near) => `${n} store${n > 1 ? "s" : ""}${near ? " · nearest first" : ""}`,
    empty: `<b>No Facto here yet…</b>Try another city or postcode. And what if you opened one? <a href="franchise.html">Become a franchisee →</a>`,
    more: (n) => `Show more (${n} store${n > 1 ? "s" : ""})`, sheet: "See details", here: "You are here",
    geo: "📍 Near me", geoOn: "✕ Near me", geoWait: "Locating…", geoNone: "Geolocation unavailable",
    geoErr: "We couldn't find your location: please check your browser's location permission.",
    results: (n) => `${n} result${n > 1 ? "s" : ""}`, pts: "pts", unlocked: "Unlocked ✓", still: (n) => `${n} pts to go`,
    next: (n, name) => `Only ${n} pts to go for: ${name}`, allDone: "Every reward is unlocked. Enjoy!",
    eggAgain: (n) => `🍦 You again! Topping shower #${n}. You're officially hooked on the Facto.`,
    eggFirst: "🎉 Well done, you found the secret topping bar! Shh… it stays between us.",
    consoleHint: "Reading the code? We love curious people. Hint: ↑ ↑ ↓ ↓ ← → ← → B A 😉\nAnd the Facto is hiring: ",
    typeMenu: ["Search: ", ["mango", "Kinder Bueno", "bubble tea", "pistachio", "halal", "matcha"]],
    typeStore: ["City, postcode… e.g. ", ["Paris", "Lyon", "Lille", "Nice", "Luxembourg", "Kuala Lumpur"]],
    typeHome: ["Find a Facto… e.g. ", ["Paris", "Lyon", "Brussels", "Luxembourg", "Nice"]],
    formFail: (m) => "Oops, sending failed. Please try again or email us at " + m + ".",
    formMail: (m) => "Your email app will open with your message ready: just click “Send”. Nothing opens? Email us directly at " + m + ".",
    delivery: "🛵 Delivery",
    country: (c) => c === "Tous" ? "All" : ((window.YF_COUNTRIES || []).find((x) => x.name === c) || {}).en || c,
    hours: (h) => String(h)
      .replace(/Tous les jours/gi, "Daily").replace(/Horaires du centre/gi, "Mall opening hours").replace(/Horaires saisonniers/gi, "Seasonal hours")
      .replace(/\b(lun|mar|mer|jeu|ven|sam|dim)\b/gi, (d) => ({ lun: "Mon", mar: "Tue", mer: "Wed", jeu: "Thu", ven: "Fri", sam: "Sat", dim: "Sun" }[d.toLowerCase()]))
      .replace(/(\d{1,2})h(\d{2})?/g, (_, a, b) => a + ":" + (b || "00")).replace(/minuit/gi, "midnight")
  }
};
const t = (key, ...args) => { const v = I18N[LANG][key]; return typeof v === "function" ? v(...args) : v; };

const store = {
  get(key, fallback) { try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* navigation privée : on ignore */ } }
};
// Toutes les clés « yf-… » enregistrées ici sont listées sur la page Cookies : en ajouter une = mettre la page à jour.

/* ---- Protection du contenu (sélection / copie) --------------------------- */
(() => {
  if (!YF_CONFIG.protectContent) return;
  document.documentElement.classList.add("protect");
  const editable = (el) => el && el.closest && el.closest("input, textarea, select, [contenteditable]");
  ["copy", "cut"].forEach((type) => document.addEventListener(type, (e) => {
    if (!editable(document.activeElement)) e.preventDefault();
  }));
  document.addEventListener("selectstart", (e) => { if (!editable(e.target)) e.preventDefault(); });
  document.addEventListener("dragstart", (e) => { if (e.target.tagName === "IMG") e.preventDefault(); });
})();

/* ---- Header, menu mobile, retour en haut -------------------------------- */
(() => {
  const header = $(".site-header");
  const burger = $(".burger");
  const nav = $("#nav");
  const toTop = $(".to-top");

  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY;
    header && header.classList.toggle("is-scrolled", y > 8);
    toTop && toTop.classList.toggle("is-visible", y > 900);
    ticking = false;
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  toTop && toTop.addEventListener("click", () => window.scrollTo({ top: 0 }));

  if (burger && nav) {
    const setOpen = (open) => {
      nav.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? t("menuClose") : t("menuOpen"));
      document.body.classList.toggle("nav-open", open);
    };
    burger.addEventListener("click", () => setOpen(!nav.classList.contains("is-open")));
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    document.addEventListener("click", (e) => { if (nav.classList.contains("is-open") && !e.target.closest(".site-header")) setOpen(false); });
    window.matchMedia("(min-width: 1181px)").addEventListener("change", () => setOpen(false));
    window.matchMedia("(orientation: portrait)").addEventListener("change", () => setOpen(false));   // téléphone tourné
  }

  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();

/* ---- Barre de raccourcis mobile (« Trouver une Facto » / « La carte ») ------
   Visible après le haut de page ; s'efface quand on fait défiler vers le bas
   (lecture), revient dès qu'on remonte ou qu'on s'arrête, et disparaît
   entièrement au niveau du pied de page. Le lien de la page en cours est retiré. */
(() => {
  const dock = $(".mobile-dock");
  if (!dock) return;
  const here = location.pathname.replace(/\/$/, "/index.html");
  $$("a", dock).forEach((a) => { if (a.pathname === here) a.remove(); });
  if (!$("a", dock)) { dock.remove(); return; }
  dock.classList.toggle("is-single", $$("a", dock).length === 1);
  const foot = $(".site-footer");
  let lastY = window.scrollY, idle;
  const atFooter = () => !!foot && foot.getBoundingClientRect().top < window.innerHeight - 24;
  const set = (show) => dock.classList.toggle("is-visible", show && !atFooter());
  window.addEventListener("scroll", () => {
    const y = window.scrollY;
    if (y < 360) set(false);
    else if (y > lastY + 6) set(false);
    else if (y < lastY - 6) set(true);
    lastY = y;
    clearTimeout(idle);
    idle = setTimeout(() => set(window.scrollY >= 360), 650);
  }, { passive: true });
})();

/* ---- Bandeau d'annonce refermable ------------------------------------------ */
(() => {
  const close = $(".tb-close");
  close && close.addEventListener("click", () => { document.documentElement.classList.add("tb-hidden"); store.set("yf-tb", 1); });
  const bar = $("#topbar"), link = bar && $("a", bar);
  bar && link && bar.addEventListener("click", (e) => { if (!e.target.closest("a, button")) location.href = link.href; });
})();

/* ---- Suggestion de langue (visiteurs dont le navigateur n'est pas en français) */
(() => {
  const sw = $(".lang-switch");
  if (!sw || store.get("yf-lang-hint", 0)) return;
  const langs = (navigator.languages || [navigator.language || ""]).map((l) => l.slice(0, 2).toLowerCase());
  const wantsEn = LANG === "fr" && !langs.includes("fr");
  const wantsFr = LANG === "en" && langs[0] === "fr";
  if (!wantsEn && !wantsFr) return;
  const box = document.createElement("div");
  box.className = "lang-hint";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-label", wantsEn ? "Language" : "Langue");
  box.innerHTML = wantsEn
    ? `<span>🌐 This site is also available in English.</span><a href="${sw.getAttribute("href")}" hreflang="en">View in English</a><button type="button" aria-label="Close">×</button>`
    : `<span>🌐 Ce site existe aussi en français.</span><a href="${sw.getAttribute("href")}" hreflang="fr">Voir en français</a><button type="button" aria-label="Fermer">×</button>`;
  const close = () => { store.set("yf-lang-hint", 1); box.classList.remove("is-in"); setTimeout(() => box.remove(), 300); };
  box.querySelector("button").addEventListener("click", close);
  box.querySelector("a").addEventListener("click", () => store.set("yf-lang-hint", 1));
  document.body.appendChild(box);
  setTimeout(() => box.classList.add("is-in"), 1200);
  setTimeout(() => { if (box.isConnected) { box.classList.remove("is-in"); setTimeout(() => box.remove(), 400); } }, 13000);
})();

/* ---- Accessibilité -------------------------------------------------------- */
(() => {
  const btn = $(".a11y-btn");
  const panel = $("#a11y-panel");
  if (!btn || !panel) return;
  let prefs = store.get("yf-a11y", {});
  const apply = () => $$("input[data-a11y]", panel).forEach((i) => {
    i.checked = !!prefs[i.dataset.a11y];
    document.documentElement.classList.toggle("a11y-" + i.dataset.a11y, i.checked);
  });
  const toggle = (open) => {
    panel.hidden = !open;
    btn.setAttribute("aria-expanded", String(open));
    if (open) $("input", panel).focus();
  };
  btn.addEventListener("click", () => toggle(panel.hidden));
  $(".a11y-close", panel).addEventListener("click", () => { toggle(false); btn.focus(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !panel.hidden) { toggle(false); btn.focus(); } });
  document.addEventListener("click", (e) => { if (!panel.hidden && !e.target.closest("#a11y-panel, .a11y-btn")) toggle(false); });
  panel.addEventListener("change", (e) => {
    const i = e.target.closest("input[data-a11y]");
    if (!i) return;
    prefs[i.dataset.a11y] = i.checked;
    store.set("yf-a11y", prefs); apply();
  });
  $(".a11y-reset", panel).addEventListener("click", () => { prefs = {}; store.set("yf-a11y", prefs); apply(); });
  apply();
})();

/* ---- Apparition douce des sections -------------------------------------- */
(() => {
  const items = $$(".reveal");
  if (!("IntersectionObserver" in window)) { items.forEach((el) => el.classList.add("is-in")); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add("is-in"); io.unobserve(entry.target); }
    });
  }, { rootMargin: "0px 0px -6% 0px", threshold: 0.01 });
  items.forEach((el) => io.observe(el));
})();

/* ---- Compteurs de boutiques ---------------------------------------------- */
(() => {
  const stores = window.YF_STORES;
  if (!stores) return;
  $$("[data-count='stores']").forEach((el) => { el.textContent = stores.length; });
  $$("[data-count='cities']").forEach((el) => { el.textContent = new Set(stores.map((s) => s.city)).size; });
})();

/* ---- Recherche de boutique depuis les autres pages ----------------------- */
$$("form[data-store-search]").forEach((form) => {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = $("input", form).value.trim();
    window.location.href = t("pages").stores + (q ? "?q=" + encodeURIComponent(q) : "") + "#liste";
  });
});

/* ---- Horaires : « Ouvert / Fermé » --------------------------------------- */
const YF_HOURS = (() => {
  const DAYS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"];
  const toMin = (h, m) => parseInt(h, 10) * 60 + (m ? parseInt(m, 10) : 0);
  const fmt = (min) => min >= 1440 ? t("midnight") : t("hm", Math.floor(min / 60), min % 60);

  // Format accepté (vérifié par build.py) : "Tous les jours 10h–20h" ou "Lun–sam 10h–20h · dim 11h–19h".
  // Résultat : { 0: [600, 1200], … } en minutes, 0 = lundi. Tout autre texte = « Horaires variables ».
  const parse = (txt) => {
    const out = {};
    for (const seg of String(txt || "").split("·").map((s) => s.trim()).filter(Boolean)) {
      const m = seg.match(/^(tous les jours|[a-zé]{3}(?:–[a-zé]{3})?)\s+(\d{1,2})h(\d{2})?–(?:(\d{1,2})h(\d{2})?|(minuit))$/i);
      if (!m) return null;
      const open = toMin(m[2], m[3]);
      const close = m[6] ? 1440 : toMin(m[4], m[5]);
      let days = [];
      if (/tous/i.test(m[1])) days = [0, 1, 2, 3, 4, 5, 6];
      else {
        const [a, b] = m[1].toLowerCase().split("–");
        const ia = DAYS.indexOf(a), ib = DAYS.indexOf(b ?? a);
        if (ia < 0 || ib < 0) return null;
        for (let i = ia; ; i = (i + 1) % 7) { days.push(i); if (i === ib) break; }
      }
      days.forEach((d) => { out[d] = [open, close]; });
    }
    return Object.keys(out).length ? out : null;
  };

  const nowIn = (tz) => {
    const parts = new Intl.DateTimeFormat("en-GB", { timeZone: tz, weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
    const get = (t) => parts.find((p) => p.type === t).value;
    return { day: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(get("weekday")), min: (parseInt(get("hour"), 10) % 24) * 60 + parseInt(get("minute"), 10) };
  };

  const status = (s) => {
    const sched = parse(s.hours);
    if (!sched) return { state: "unknown", label: t("hoursVar") };
    const now = nowIn(s.tz || "Europe/Paris");   // fuseau calculé par build.py
    const today = sched[now.day];
    if (today && now.min >= today[0] && now.min < today[1]) {
      const left = today[1] - now.min;
      return { state: left <= 45 ? "soon" : "open", label: (left <= 45 ? t("soon") : t("openUntil")) + fmt(today[1]) };
    }
    if (today && now.min < today[0]) return { state: "closed", label: t("closedOpensAt") + fmt(today[0]) };
    for (let i = 1; i <= 7; i++) {
      const d = (now.day + i) % 7;
      if (sched[d]) return { state: "closed", label: t("closedOpens", i === 1 ? t("tomorrow") : t("days")[d], fmt(sched[d][0])) };
    }
    return { state: "closed", label: t("closed") };
  };
  return { status };
})();

/* ---- Outils boutiques (partagés accueil / page boutiques) ---------------- */
const YF_STORE_UI = (() => {
  const fullAddr = (s) => [s.center, s.address, [s.zip, s.city].filter(Boolean).join(" "), s.country === "France" ? "" : s.country].filter(Boolean).join(", ");
  const q = (s) => encodeURIComponent("Yogurt Factory " + fullAddr(s));
  const dirUrl = (s) => s.lat != null
    ? `https://www.google.com/maps/dir/?api=1&destination=${s.lat},${s.lng}`
    : `https://www.google.com/maps/dir/?api=1&destination=${q(s)}`;
  const reviewsUrl = (s) => s.googleUrl || `https://www.google.com/maps/search/?api=1&query=${q(s)}`;
  const stars = (r) => {
    const full = Math.round(r * 2) / 2;
    return [1, 2, 3, 4, 5].map((i) => `<span class="${full >= i ? "on" : full >= i - 0.5 ? "half" : ""}">★</span>`).join("");
  };
  const rating = (s) => s.rating
    ? `<a class="rating" href="${esc(reviewsUrl(s))}" target="_blank" rel="noopener" aria-label="${t("ratingAria", LANG === "fr" ? String(s.rating).replace(".", ",") : s.rating, s.reviews)}"><span class="stars" aria-hidden="true">${stars(s.rating)}</span><b>${LANG === "fr" ? String(s.rating).replace(".", ",") : s.rating}</b>${s.reviews ? `<small>${t("reviews", Number(s.reviews).toLocaleString(LANG === "fr" ? "fr-FR" : "en-GB"))}</small>` : ""}</a>`
    : `<a class="rating rating--empty" href="${esc(reviewsUrl(s))}" target="_blank" rel="noopener">${t("seeReviews")}</a>`;
  const photo = (s) => BASE + "/" + (s.photo || YF_CONFIG.defaultStorePhoto).replace(/^\//, "");
  // Liens de commande en ligne (renseignés dans contenu/boutiques/, domaines vérifiés par build.py)
  const DELIVERY = [["uberEats", "Uber Eats", "#06c167"], ["deliveroo", "Deliveroo", "#00ccbc"], ["takeaway", "Takeaway", "#ff8000"]];
  const delivers = (s) => DELIVERY.some(([k]) => s[k]);
  const delivery = (s) => delivers(s)
    ? `<div class="deliv"><span>${t("delivery")}</span>${DELIVERY.filter(([k]) => s[k]).map(([k, name, color]) =>
      `<a href="${esc(s[k])}" target="_blank" rel="noopener"><i style="background:${color}"></i>${name}</a>`).join("")}</div>`
    : "";
  const favKey = (s) => s.name;
  const getFav = () => store.get("yf-fav-store", null);
  const setFav = (name) => store.set("yf-fav-store", name);
  return { fullAddr, dirUrl, reviewsUrl, rating, photo, delivers, delivery, favKey, getFav, setFav };
})();

/* ---- Accueil : « Ma Facto » ----------------------------------------------- */
(() => {
  const box = $("#fav-store");
  if (!box || !window.YF_STORES) return;
  const fav = YF_STORE_UI.getFav();
  const s = window.YF_STORES.find((x) => x.name === fav);
  if (!s) return;
  const st = YF_HOURS.status(s);
  box.innerHTML = `<span class="fav-label">${t("myFacto")}</span><b>${esc(s.name)}</b><span class="status status--${st.state}">${esc(st.label)}</span><a href="${esc(YF_STORE_UI.dirUrl(s))}" target="_blank" rel="noopener">${t("route")}</a>`;
  box.hidden = false;
})();

/* ---- Localisateur de boutiques ------------------------------------------ */
(() => {
  const root = $("#store-locator");
  if (!root || !window.YF_STORES) return;
  const UI = YF_STORE_UI;
  const stores = window.YF_STORES.map((s, i) => ({ ...s, id: i }));
  const input = $("#store-q", root);
  const regionSel = $("#store-region", root);
  const pillsBox = $(".country-pills", root);
  const list = $(".store-list", root);
  const count = $(".store-count", root);
  const openOnly = $("#store-open", root);
  const delivOnly = $("#store-deliv", root);
  const geoBtn = $("#store-geo", root);
  const moreBtn = $("#store-more", root);
  const mapEl = $("#store-map");
  let country = "Tous";
  let userPos = null;
  let limit = YF_CONFIG.storesPerPage;
  let fav = UI.getFav();
  let map = null, markers = {}, userMarker = null, lastRes = [];

  const norm = (s) => (s || "").toString().normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const dist = (a, b) => {
    const R = 6371, rad = Math.PI / 180;
    const dLat = (b.lat - a.lat) * rad, dLng = (b.lng - a.lng) * rad;
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(x));
  };
  const km = (d) => d < 10 ? d.toFixed(1).replace(".", ",") + " km" : Math.round(d) + " km";

  // Pastilles pays, dans l'ordre de contenu/pays.json
  const order = (window.YF_COUNTRIES || []).map((c) => c.name);
  const byCountry = {};
  stores.forEach((s) => { byCountry[s.country] = (byCountry[s.country] || 0) + 1; });
  const countryList = ["Tous", ...order.filter((c) => byCountry[c]), ...Object.keys(byCountry).filter((c) => !order.includes(c))];
  pillsBox.innerHTML = countryList.map((c) =>
    `<button type="button" class="pill" data-country="${esc(c)}" aria-pressed="${c === "Tous"}">${esc(t("country", c))}<small>${c === "Tous" ? stores.length : byCountry[c]}</small></button>`
  ).join("");

  const fillRegions = () => {
    const regions = [...new Set(stores.filter((s) => country === "Tous" || s.country === country).map((s) => s.region))].sort((a, b) => a.localeCompare(b, "fr"));
    const current = regionSel.value;
    regionSel.innerHTML = `<option value="">${t("allRegions")}</option>` + regions.map((r) => `<option>${esc(r)}</option>`).join("");
    regionSel.value = regions.includes(current) ? current : "";
  };

  const filtered = () => {
    const q = norm(input.value.trim());
    const region = regionSel.value;
    let res = stores.filter((s) =>
      (country === "Tous" || s.country === country) &&
      (!region || s.region === region) &&
      (!q || norm([s.name, s.center, s.address, s.zip, s.city, s.region, s.country].join(" ")).includes(q))
    ).map((s) => ({ ...s, st: YF_HOURS.status(s), d: userPos && s.lat != null ? dist(userPos, s) : null }));
    if (openOnly.checked) res = res.filter((s) => s.st.state === "open" || s.st.state === "soon");
    if (delivOnly && delivOnly.checked) res = res.filter(UI.delivers);
    if (userPos) res.sort((a, b) => (a.d ?? 1e9) - (b.d ?? 1e9));
    const fi = res.findIndex((s) => s.name === fav);
    if (fi > 0) res.unshift(res.splice(fi, 1)[0]);
    return res;
  };

  const card = (s) => {
    const isFav = s.name === fav;
    const tel = s.phone ? `<a href="tel:${s.phone.replace(/[^\d+]/g, "")}">${t("call")}</a>` : "";
    const onMap = mapEl && s.lat != null ? `<button type="button" data-focus="${s.id}">${t("onMap")}</button>` : "";
    return `<article class="store${isFav ? " is-fav" : ""}" id="store-${s.id}">
      <div class="store-photo"><img src="${esc(UI.photo(s))}" alt="${esc(t("storeAlt", s.name))}" loading="lazy" width="480" height="270">
        <button type="button" class="fav-btn" data-fav="${esc(s.name)}" aria-pressed="${isFav}" aria-label="${isFav ? t("favRemove") : t("favSet")}">${isFav ? "★" : "☆"}</button>
        ${s.d != null ? `<span class="dist">${km(s.d)}</span>` : ""}
      </div>
      <div class="store-body">
        <span class="where">${isFav ? t("myFactoPrefix") : ""}${esc(s.region)}${s.country !== "France" ? " · " + esc(t("country", s.country)) : ""}</span>
        <h3>${esc(s.name)}</h3>
        ${UI.rating(s)}
        <address>${esc(s.center)} · ${esc(s.address)}, ${esc([s.zip, s.city].filter(Boolean).join(" "))}</address>
        <span class="status status--${s.st.state}">${esc(s.st.label)}</span>
        <div class="hours">${esc(t("hours", s.hours))}</div>
        ${UI.delivery(s)}
        <div class="actions"><a href="${esc(UI.dirUrl(s))}" target="_blank" rel="noopener">${t("routeBtn")}</a>${tel}${onMap}</div>
      </div>
    </article>`;
  };

  const render = (keepLimit) => {
    if (!keepLimit) limit = YF_CONFIG.storesPerPage;
    const res = filtered();
    lastRes = res;
    const shown = res.slice(0, limit);
    count.textContent = res.length ? t("count", res.length, !!userPos) : "";
    list.innerHTML = res.length ? shown.map(card).join("")
      : `<div class="empty" style="grid-column:1/-1">${t("empty")}</div>`;
    const left = res.length - shown.length;
    moreBtn.hidden = left <= 0;
    moreBtn.textContent = t("more", left);
    updateMap(res);
    const url = new URL(location.href);
    input.value.trim() ? url.searchParams.set("q", input.value.trim()) : url.searchParams.delete("q");
    history.replaceState(null, "", url);
  };

  // Carte interactive (Leaflet + OpenStreetMap) ---------------------------
  const pin = (color) => window.L.divIcon({
    className: "",
    html: `<span class="map-pin" style="background:${color}"></span>`,
    iconSize: [24, 24], iconAnchor: [12, 24], popupAnchor: [0, -22]
  });
  const popup = (s) => {
    const st = YF_HOURS.status(s);
    return `<div class="map-pop"><img src="${esc(UI.photo(s))}" alt="" width="240" height="135"><b>${esc(s.name)}</b>${UI.rating(s)}<span>${esc(UI.fullAddr(s))}</span><span class="status status--${st.state}">${esc(st.label)}</span><a href="${esc(UI.dirUrl(s))}" target="_blank" rel="noopener">${t("route")}</a> · <a href="#store-${s.id}" data-goto="${s.id}">${t("sheet")}</a></div>`;
  };
  const initMap = () => {
    if (!mapEl || !window.L) return;
    map = window.L.map(mapEl, { scrollWheelZoom: true, wheelPxPerZoomLevel: 90, tap: true }).setView([46.6, 2.4], 5);
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    const icon = pin("#e3232b");
    stores.forEach((s) => {
      if (s.lat == null) return;
      markers[s.id] = window.L.marker([s.lat, s.lng], { icon, title: s.name, alt: s.name }).bindPopup(() => popup(s), { maxWidth: 260 });
    });
    map.on("popupopen", (e) => {
      const a = e.popup.getElement().querySelector("[data-goto]");
      a && a.addEventListener("click", (ev) => { ev.preventDefault(); goToCard(parseInt(a.dataset.goto, 10)); });
    });
    updateMap(lastRes);
  };
  const goToCard = (id) => {
    const idx = lastRes.findIndex((s) => s.id === id);
    if (idx >= limit) { limit = idx + 1; render(true); }
    const el = document.getElementById("store-" + id);
    if (el) { el.scrollIntoView({ block: "center" }); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1600); }
  };
  const updateMap = (res) => {
    if (!map) return;
    Object.values(markers).forEach((m) => m.remove());
    const pts = [];
    res.forEach((s) => { if (markers[s.id]) { markers[s.id].addTo(map); pts.push([s.lat, s.lng]); } });
    if (userPos) { pts.push([userPos.lat, userPos.lng]); map.setView([userPos.lat, userPos.lng], 11); return; }
    if (!pts.length) return;
    const pristine = country === "Tous" && !input.value.trim() && !regionSel.value && !openOnly.checked && !(delivOnly && delivOnly.checked);
    if (pristine) map.setView([46.6, 2.4], 5);
    else if (pts.length === 1) map.setView(pts[0], 14);
    else map.fitBounds(pts, { padding: [30, 30], maxZoom: 13 });
  };
  if (mapEl) {
    const css = document.createElement("link");
    css.rel = "stylesheet"; css.href = BASE + "/assets/vendor/leaflet/leaflet.css";
    document.head.appendChild(css);
    const js = document.createElement("script");
    js.src = BASE + "/assets/vendor/leaflet/leaflet.js"; js.onload = initMap;
    document.body.appendChild(js);
  }

  list.addEventListener("click", (e) => {
    const f = e.target.closest("[data-fav]");
    if (f) {
      fav = fav === f.dataset.fav ? null : f.dataset.fav;
      UI.setFav(fav);
      render(true);
      return;
    }
    const b = e.target.closest("[data-focus]");
    if (b && map) {
      const m = markers[b.dataset.focus];
      if (m) { mapEl.scrollIntoView({ block: "center" }); map.setView(m.getLatLng(), 15); m.openPopup(); }
    }
  });
  moreBtn.addEventListener("click", () => { limit += YF_CONFIG.storesPerPage; render(true); });

  // Géolocalisation --------------------------------------------------------
  geoBtn.addEventListener("click", () => {
    if (userPos) { // 2e clic : on désactive le tri par distance
      userPos = null; userMarker && userMarker.remove(); userMarker = null;
      geoBtn.classList.remove("is-on"); geoBtn.textContent = t("geo");
      render(); return;
    }
    if (!navigator.geolocation) { geoBtn.textContent = t("geoNone"); return; }
    geoBtn.textContent = t("geoWait");
    navigator.geolocation.getCurrentPosition((pos) => {
      userPos = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      geoBtn.classList.add("is-on"); geoBtn.textContent = t("geoOn");
      country = "Tous"; input.value = ""; regionSel.value = "";
      $$(".pill", pillsBox).forEach((p) => p.setAttribute("aria-pressed", String(p.dataset.country === "Tous")));
      if (map) userMarker = window.L.marker([userPos.lat, userPos.lng], { icon: pin("#3d63d6"), title: t("here") }).addTo(map).bindPopup(t("here"));
      render();
    }, () => {
      geoBtn.textContent = t("geo");
      count.textContent = t("geoErr");
    }, { timeout: 10000, maximumAge: 300000 });
  });

  pillsBox.addEventListener("click", (e) => {
    const b = e.target.closest(".pill");
    if (!b) return;
    country = b.dataset.country;
    $$(".pill", pillsBox).forEach((p) => p.setAttribute("aria-pressed", String(p === b)));
    fillRegions();
    render();
  });
  let debounce;
  input.addEventListener("input", () => { clearTimeout(debounce); debounce = setTimeout(() => render(), 150); });
  regionSel.addEventListener("change", () => render());
  openOnly.addEventListener("change", () => render());
  delivOnly && delivOnly.addEventListener("change", () => render());
  $("form", root).addEventListener("submit", (e) => { e.preventDefault(); input.blur(); });

  const params = new URLSearchParams(location.search);
  if (params.get("q")) input.value = params.get("q");
  if (params.get("livraison") && delivOnly) delivOnly.checked = true;
  fillRegions();
  render();
})();

/* ---- Carte : rubrique active pendant le défilement ----------------------- */
(() => {
  const links = $$(".menu-nav a");
  if (!links.length || !("IntersectionObserver" in window)) return;
  const byId = Object.fromEntries(links.map((a) => [a.hash.slice(1), a]));
  const setActive = (id) => links.forEach((a) => {
    const on = a.hash === "#" + id;
    a.classList.toggle("is-active", on);
    if (on) { a.setAttribute("aria-current", "true"); const bar = a.parentElement; bar.scrollTo({ left: a.offsetLeft - bar.clientWidth / 2 + a.clientWidth / 2 }); }
    else a.removeAttribute("aria-current");
  });
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => { if (en.isIntersecting && byId[en.target.id]) setActive(en.target.id); });
  }, { rootMargin: "-35% 0px -60% 0px" });
  Object.keys(byId).forEach((id) => { const el = document.getElementById(id); el && io.observe(el); });
})();

/* ---- Carte : recherche globale -------------------------------------------- */
(() => {
  const input = $("#menu-q");
  if (!input) return;
  const page = $(".menu-page");
  const count = $("#menu-count");
  const empty = $("#menu-empty");
  const sections = $$(".menu-sec", page).filter((s) => s.id !== "infos");
  const units = $$(".pot-card, .item, .tlist li", page);
  const norm = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const plain = new Map(units.map((u) => [u, u.innerHTML]));
  const index = new Map(units.map((u) => [u, norm(u.textContent + " " + (u.closest(".menu-sec").querySelector("h2")?.textContent || "") + " " + (u.closest(".topping-col")?.querySelector("h3")?.textContent || ""))]));
  const highlight = (el, q) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((n) => {
      const i = norm(n.data).indexOf(q);
      if (i < 0) return;
      const mark = document.createElement("mark");
      const after = n.splitText(i);
      after.splitText(q.length);
      mark.textContent = after.data;
      after.replaceWith(mark);
    });
  };

  let debounce;
  const run = () => {
    const q = norm(input.value.trim());
    units.forEach((u) => { u.innerHTML = plain.get(u); u.hidden = !!q && !index.get(u).includes(q); if (q && !u.hidden) highlight(u, q); });
    $$(".topping-col", page).forEach((c) => { c.hidden = !!q && !$$(".tlist li", c).some((li) => !li.hidden); });
    $$(".pots-grid", page).forEach((g) => { const none = !!q && !$$(".pot-card", g).some((p) => !p.hidden); g.hidden = none; const title = g.previousElementSibling; if (title && title.classList.contains("group-title")) title.hidden = none; });
    let total = 0;
    sections.forEach((s) => {
      const n = $$(".pot-card, .item, .tlist li", s).filter((u) => !u.hidden).length;
      s.hidden = !!q && n === 0;
      const link = $(`.menu-nav a[href="#${s.id}"]`); if (link) link.hidden = s.hidden;
      total += n;
    });
    count.textContent = q ? (total ? t("results", total) : "") : "";
    empty.hidden = !q || total > 0;
  };
  input.addEventListener("input", () => { clearTimeout(debounce); debounce = setTimeout(run, 120); });
  $("#menu-search").addEventListener("submit", (e) => {
    e.preventDefault(); input.blur();
    const first = $(".menu-sec:not([hidden])", page);
    first && first.scrollIntoView({ block: "start" });
  });
})();

/* ---- Fidélité : simulateur de points -------------------------------------- */
(() => {
  const range = $("#pts-range");
  if (!range) return;
  const outPts = $("#pts-out");
  const next = $("#pts-next");
  const bar = $("#pts-bar");
  const items = $$(".reward");
  const max = Math.max(...items.map((li) => parseInt(li.dataset.points, 10)));
  const update = () => {
    const pts = parseInt(range.value, 10);
    outPts.textContent = pts + " " + t("pts");
    let nextItem = null;
    items.forEach((li) => {
      const need = parseInt(li.dataset.points, 10);
      const ok = pts >= need;
      li.classList.toggle("is-unlocked", ok);
      li.classList.toggle("is-locked", !ok);
      li.querySelector(".state").textContent = ok ? t("unlocked") : t("still", need - pts);
      if (!ok && !nextItem) nextItem = { need, name: li.querySelector("b").textContent };
    });
    next.textContent = nextItem ? t("next", nextItem.need - pts, nextItem.name) : t("allDone");
    bar.style.width = Math.min(100, (pts / max) * 100) + "%";
  };
  range.addEventListener("input", update);
  items.forEach((li) => li.addEventListener("click", () => { range.value = li.dataset.points; update(); }));
  update();
})();

/* ---- 🥚 Easter egg : la pluie de toppings ----------------------------------
   Déclencheurs : code Konami (↑ ↑ ↓ ↓ ← → ← → B A) sur ordinateur,
   ou 5 tapotements rapides sur le logo du pied de page (mobile). */
(() => {
  const TOPPINGS = ["🍓", "🍫", "🍬", "🍪", "🥝", "🍌", "🫐", "🥥", "🍦", "🧇", "🍒", "🍭", "🥭"];
  let running = false;

  const toast = (text) => {
    const t = document.createElement("div");
    t.className = "egg-toast";
    t.setAttribute("role", "status");
    t.textContent = text;
    document.body.appendChild(t);
    requestAnimationFrame(() => t.classList.add("is-in"));
    setTimeout(() => { t.classList.remove("is-in"); setTimeout(() => t.remove(), 400); }, 4200);
  };

  const rain = () => {
    if (running) return;
    running = true;
    const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.classList.contains("a11y-motion");
    const found = store.get("yf-egg", 0) + 1;
    store.set("yf-egg", found);
    toast(found > 1
      ? t("eggAgain", found)
      : t("eggFirst"));
    if (calm) { running = false; return; }
    const box = document.createElement("div");
    box.className = "egg-rain";
    box.setAttribute("aria-hidden", "true");
    const n = window.innerWidth < 600 ? 40 : 70;
    for (let i = 0; i < n; i++) {
      const s = document.createElement("span");
      s.textContent = TOPPINGS[Math.floor(Math.random() * TOPPINGS.length)];
      s.style.left = Math.random() * 100 + "vw";
      s.style.fontSize = 20 + Math.random() * 26 + "px";
      s.style.animationDuration = 2.2 + Math.random() * 2.2 + "s";
      s.style.animationDelay = Math.random() * 1.6 + "s";
      s.style.setProperty("--spin", (Math.random() * 720 - 360).toFixed(0) + "deg");
      box.appendChild(s);
    }
    document.body.appendChild(box);
    const logo = $(".brand img");
    logo && logo.classList.add("egg-spin");
    setTimeout(() => { box.remove(); logo && logo.classList.remove("egg-spin"); running = false; }, 6200);
  };

  const KONAMI = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
  let pos = 0;
  document.addEventListener("keydown", (e) => {
    if (e.target.closest && e.target.closest("input, textarea, select")) return;
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    pos = k === KONAMI[pos] ? pos + 1 : (k === KONAMI[0] ? 1 : 0);
    if (pos === KONAMI.length) { pos = 0; rain(); }
  });

  const footLogo = $(".footer-brand img");
  if (footLogo) {
    let taps = 0, timer;
    footLogo.addEventListener("click", () => {
      taps++; clearTimeout(timer);
      timer = setTimeout(() => { taps = 0; }, 1500);
      if (taps >= 5) { taps = 0; rain(); }
    });
  }

  // Petit mot pour les curieux qui ouvrent la console
  try {
    console.log("%c🍦 Yogurt Factory", "font:800 28px Montserrat,sans-serif;color:#e3232b");
    console.log("%c" + t("consoleHint") + location.origin + BASE + "/" + (LANG === "en" ? "en/" : "") + t("pages").careers, "font:14px Poppins,sans-serif;color:#2a1a1a");
  } catch { /* console indisponible */ }
})();

/* ---- Petits plus & animations ---------------------------------------------
   Tout est désactivé si le visiteur préfère réduire les animations. */
const YF_CALM = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.classList.contains("a11y-motion");

// Barre de progression de lecture
(() => {
  const bar = document.createElement("div");
  bar.className = "read-progress";
  bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  let ticking = false;
  const update = () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.transform = `scaleX(${h > 0 ? Math.min(1, window.scrollY / h) : 0})`;
    ticking = false;
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();

// Compteurs qui défilent (chiffres clés)
(() => {
  const els = $$(".stat b, .kpi b, .phone-card .val");
  if (!els.length || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (!en.isIntersecting) return;
    io.unobserve(en.target);
    const node = [...en.target.childNodes].find((n) => n.nodeType === 3 && /\d/.test(n.textContent));
    if (!node || YF_CALM()) return;
    const m = node.textContent.match(/^(\D*)(\d(?:[\d  ]*\d)?)(.*)$/s);
    if (!m) return;
    const target = parseInt(m[2].replace(/\D/g, ""), 10);
    if (!target || (target >= 1900 && target <= 2100)) return; // on ne fait pas défiler les années
    const fmt = (n) => (m[2].match(/[  ]/) ? n.toLocaleString("fr-FR") : String(n));
    const t0 = performance.now(), dur = 1100;
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      node.textContent = m[1] + fmt(Math.round(target * e)) + m[3];
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }), { threshold: 0.6 });
  els.forEach((el) => io.observe(el));
})();

// Accueil : toppings qui flottent + parallaxe au mouvement de la souris
(() => {
  const hero = $(".hero");
  const visual = $(".hero-visual");
  if (!hero || !visual) return;
  const bits = document.createElement("div");
  bits.className = "hero-bits";
  bits.setAttribute("aria-hidden", "true");
  [["🍓", 8, 12], ["🍫", 86, 8], ["🫐", 3, 40], ["🍪", 92, 62], ["🥝", 18, 92], ["🍬", 74, 88]].forEach(([e, x, y], i) => {
    const s = document.createElement("span");
    s.textContent = e;
    s.style.left = x + "%"; s.style.top = y + "%"; s.style.animationDelay = (-i * 1.3) + "s";
    s.dataset.depth = String(0.6 + (i % 3) * 0.35);
    bits.appendChild(s);
  });
  visual.appendChild(bits);
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  const layers = [[$(".sundae", visual), 12], [$(".donut", visual), -20], [$(".sticker", visual), 16], ...$$("span", bits).map((s) => [s, 30 * parseFloat(s.dataset.depth)])];
  let raf = 0;
  hero.addEventListener("pointermove", (e) => {
    if (YF_CALM() || raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      const r = hero.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      layers.forEach(([el, k]) => { if (el) el.style.translate = `${(x * k).toFixed(1)}px ${(y * k).toFixed(1)}px`; });
    });
  });
  hero.addEventListener("pointerleave", () => layers.forEach(([el]) => { if (el) el.style.translate = ""; }));
})();

// Cartes qui s'inclinent légèrement sous la souris
(() => {
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  $$(".card, .pot-card, .loyalty-steps > div, .step").forEach((el) => {
    el.classList.add("tilt");
    el.addEventListener("pointermove", (e) => {
      if (YF_CALM()) return;
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transform = `perspective(700px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg) translateY(-3px)`;
    });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  });
})();

// Suggestions qui s'écrivent toutes seules dans les champs de recherche
(() => {
  const fields = [
    ["#menu-q", t("typeMenu")[1], t("typeMenu")[0]],
    ["#store-q", t("typeStore")[1], t("typeStore")[0]],
    ["#home-q", t("typeHome")[1], t("typeHome")[0]]
  ];
  fields.forEach(([sel, words, prefix]) => {
    const input = $(sel);
    if (!input || YF_CALM()) return;
    const base = input.placeholder;
    let w = 0, c = 0, del = false, timer;
    const tick = () => {
      if (document.activeElement === input || input.value) { input.placeholder = base; timer = setTimeout(tick, 1500); return; }
      const word = words[w];
      c += del ? -1 : 1;
      input.placeholder = prefix + word.slice(0, c) + (del ? "" : "|");
      if (!del && c === word.length) { del = true; timer = setTimeout(tick, 1400); return; }
      if (del && c === 0) { del = false; w = (w + 1) % words.length; }
      timer = setTimeout(tick, del ? 45 : 95);
    };
    timer = setTimeout(tick, 1200);
  });
})();

// Fidélité : petit « pop » quand une récompense se débloque
(() => {
  const list = $(".rewards");
  if (!list) return;
  new MutationObserver((muts) => muts.forEach((m) => {
    const li = m.target;
    if (m.attributeName === "class" && li.classList.contains("is-unlocked") && !(m.oldValue || "").includes("is-unlocked") && !YF_CALM()) {
      li.classList.remove("pop"); void li.offsetWidth; li.classList.add("pop");
    }
  })).observe(list, { subtree: true, attributes: true, attributeFilter: ["class"], attributeOldValue: true });
})();

/* ---- Pages utilitaires ------------------------------------------------------ */
$$("[data-reload]").forEach((b) => b.addEventListener("click", () => location.reload()));
if ($(".err") && /hors-ligne/.test(location.pathname)) window.addEventListener("online", () => location.reload());
(() => {
  const blocks = $$("[data-merci]");
  if (!blocks.length) return;
  const f = new URLSearchParams(location.search).get("f");
  if (!blocks.some((b) => b.dataset.merci === f)) return;
  blocks.forEach((b) => { b.hidden = b.dataset.merci !== f; });
})();

/* ---- Service worker : consultation hors connexion ------------------------- */
if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
  window.addEventListener("load", () => navigator.serviceWorker.register(BASE + "/sw.js", { scope: BASE + "/" }).catch(() => {}));
}

/* ---- Formulaires ---------------------------------------------------------- */
$$("form[data-form]").forEach((form) => {
  const cfg = YF_CONFIG.forms[form.dataset.form];
  const msg = $(".form-msg", form);
  const btn = $("button[type=submit]", form);
  const draftKey = "yf-draft-" + form.dataset.form;
  const openedAt = Date.now();

  // Brouillon : on restaure ce que le visiteur avait commencé à taper
  const draft = store.get(draftKey, null);
  if (draft) Object.entries(draft).forEach(([k, v]) => { const f = form.elements[k]; if (f && f.type !== "checkbox" && !f.value) f.value = v; });
  form.addEventListener("input", () => {
    const d = {};
    for (const [k, v] of new FormData(form).entries()) if (k !== "consent" && k !== "website" && typeof v === "string") d[k] = v;
    store.set(draftKey, d);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    // Anti-spam : champ invisible rempli ou envoi en moins de 3 s = robot, on ignore sans rien dire.
    if (data.get("website") || Date.now() - openedAt < 3000) return;
    data.delete("website");

    if (!cfg) return;
    if (cfg.endpoint) {
      btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = "Envoi…";
      try {
        const r = await fetch(cfg.endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
        if (!r.ok) throw new Error(r.status);
        form.reset(); store.set(draftKey, null);
        location.href = t("pages").thanks + "?f=" + encodeURIComponent(form.dataset.form);
        return;
      } catch {
        msg.textContent = t("formFail", cfg.email);
      }
      btn.disabled = false; btn.textContent = btn.dataset.label;
      msg.classList.add("is-visible");
      return;
    }

    const subject = form.dataset.subject || "Contact site web";
    const lines = [];
    for (const [key, value] of data.entries()) {
      if (key === "consent" || !value) continue;
      const label = form.querySelector(`[name="${key}"]`)?.closest(".field")?.querySelector("label")?.textContent.replace(/\s*\*$/, "") || key;
      lines.push(`${label} : ${value}`);
    }
    window.location.href = `mailto:${cfg.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
    msg.textContent = t("formMail", cfg.email);
    msg.classList.add("is-visible");
  });
});
