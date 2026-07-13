/* ═══════════════════════════════════════════════════════════
   Wijnhaven Feldjournal — Service Worker
   Strategy:
     • install  → precache every local app-shell asset (bypass HTTP cache)
     • activate → delete stale caches, claim all tabs
     • fetch    → network-first for HTML (always fresh),
                  cache-first for everything else (instant, no refetch).
                  Versioned cache = a CACHE bump re-fetches all assets, so
                  cache-first needs no per-request revalidation.
   ⚠ Bump CACHE version on every deploy that changes files.
═══════════════════════════════════════════════════════════ */

const CACHE = 'wijnhaven-v49';

/* Cross-origin hosts we are allowed to cache (all send CORS headers, so the
   responses are readable/cacheable — needed for offline fonts + 3D on-site). */
const CACHEABLE_HOSTS = [
  'fonts.googleapis.com',   // font CSS
  'fonts.gstatic.com',      // font woff2
  'esm.sh',                 // three.js + GLTFLoader (3D map)
  'unpkg.com',              // <model-viewer> (per-stop models)
];

/* All local assets that must work fully offline.
   Map figure-ground is inlined in index.html; eigene Fotos kommen
   nach der Reise dazu und werden hier ergänzt (+ CACHE-Version bumpen). */
const PRECACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon.svg',
  '/icon-192.png',
  '/icon-512.png',
  '/icon-512-maskable.png',
  '/apple-touch-icon.png',
  '/models/kubuswoningen.glb',
  '/models/markthal.glb',
  /* Eintrags-Abbildungen (frei lizenziert, WebP) — fuer den Offline-Feldeinsatz vorgeladen */
  '/img/witte-huis-then.webp',
  '/img/witte-huis-now.webp',
  '/img/luftbild-1940.webp',
  '/img/kubuswoningen.webp',
  '/img/markthal.webp',
  '/img/markthal-innen.webp',
  '/img/red-apple.webp',
  '/img/wijnhaveneiland.webp',
  '/img/wederopbouw-1950.webp',
  '/img/ey.webp',
  '/img/casanova.webp',
];
/* Bewusst NICHT precachen (gross / Opt-in, werden bei Bedarf zur Laufzeit gecacht):
   models/map_v1.glb (~8,9 MB), downloads/wijnhaven-volldetail-demo.glb, Thesis-PDF. */

/* ── Update trigger from page script ── */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

/* ── Install: fetch + cache the shell, activate immediately.
   {cache:'reload'} bypasses the browser HTTP cache so a CACHE bump can never
   precache a stale index.html/asset. ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(
        PRECACHE.map(u => new Request(u, { cache: 'reload' }))
      ))
      .then(() => self.skipWaiting())
  );
});

/* ── Activate: delete ALL old caches, take control of all tabs ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* ── Fetch ── */
self.addEventListener('fetch', event => {
  const req = event.request;

  /* Only handle GET */
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const isSameOrigin = url.origin === self.location.origin;
  const isCacheable  = isSameOrigin || CACHEABLE_HOSTS.indexOf(url.hostname) !== -1;

  /* Leave everything else (analytics, source links, …) to the network */
  if (!isCacheable) return;

  /* HTML navigation: network-first — always delivers the latest version.
     Only a genuinely good response is cached; 404/500/redirect pages must
     never poison the offline app shell. Falls back to cache when offline. */
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          if (res && res.ok && res.type === 'basic') {
            const copy = res.clone();               // clone BEFORE returning
            caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() => caches.match(req).then(r => r || caches.match('/index.html')))
    );
    return;
  }

  /* Everything else (images, SVG, fonts, CDN modules, GLB):
     cache-first — instant, and NEVER re-downloads a cached asset (important
     for the 8.9 MB map GLB on mobile data). Fresh copies arrive via CACHE bump. */
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req)
        .then(res => {
          /* Cache only readable, successful responses (basic = same-origin,
             cors = the whitelisted CDNs). Opaque responses are skipped. */
          if (res && res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
            const copy = res.clone();               // clone BEFORE returning
            caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() =>
          new Response('Offline – Ressource nicht verfügbar', {
            status: 503,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
          })
        );
    })
  );
});
