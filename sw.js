/* Yogurt Factory — service worker (généré par build.py)
   - pages : réseau d'abord, copie de secours en cache, page « hors connexion » sinon
   - CSS/JS/polices/images : cache d'abord (fichiers versionnés) */
const VERSION = "yf-c51d844d";
const PRECACHE = ["/yogurt-factory/hors-ligne.html", "/yogurt-factory/en/offline.html", "/yogurt-factory/assets/css/style.css?v=817cb2d8", "/yogurt-factory/assets/css/fonts.css?v=8fa55788", "/yogurt-factory/assets/js/main.js?v=6aff58a5", "/yogurt-factory/assets/js/data.js?v=9b6d0a2b", "/yogurt-factory/assets/js/prefs.js?v=c988606d", "/yogurt-factory/images/logo.png", "/yogurt-factory/assets/fonts/poppins-400-normal-latin.woff2", "/yogurt-factory/assets/fonts/montserrat-100-900-normal-latin.woff2", "/yogurt-factory/assets/fonts/lobster-400-normal-latin.woff2"];
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
    }).catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match(url.pathname.startsWith("/yogurt-factory/en/") ? "/yogurt-factory/en/offline.html" : "/yogurt-factory/hors-ligne.html"))));
    return;
  }
  const path = url.pathname.slice("/yogurt-factory".length);
  if (/^\/(assets|images)\//.test(path) || path === "/favicon.ico") {
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    })));
  }
});
