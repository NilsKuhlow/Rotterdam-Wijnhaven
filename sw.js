/* ═══════════════════════════════════════════════════════════
   Wijnhaven Feldjournal — Service Worker
   Strategy:
     • install  → precache every local asset
     • activate → delete stale caches, claim all tabs
     • fetch    → network-first for HTML (always fresh),
                  cache-first for images/assets (instant)
   ⚠ Bump CACHE version on every deploy that changes files.
═══════════════════════════════════════════════════════════ */

const CACHE = 'wijnhaven-v12';

/* All local assets that must work fully offline.
   Map figure-ground is inlined in index.html; eigene Fotos kommen
   nach der Reise dazu und werden hier ergänzt (+ CACHE-Version bumpen). */
const PRECACHE = [
  '/',
  '/index.html',
  '/sw.js',
  '/manifest.json',
  '/icon.svg',
  '/models/kubuswoningen.glb',
  '/models/markthal.glb',
];

/* ── Update trigger from page script ── */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

/* ── Install: fetch + cache everything, activate immediately ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(PRECACHE))
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
  const url = new URL(req.url);

  /* Only handle GET */
  if (req.method !== 'GET') return;

  const isSameOrigin  = url.origin === self.location.origin;
  const isGoogleFonts = url.hostname === 'fonts.googleapis.com'
                     || url.hostname === 'fonts.gstatic.com';

  /* Skip unknown cross-origin requests */
  if (!isSameOrigin && !isGoogleFonts) return;

  /* HTML navigation: network-first — always delivers latest version.
     Falls back to cached page only when truly offline. */
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          caches.open(CACHE).then(c => c.put(req, res.clone()));
          return res;
        })
        .catch(() => caches.match(req).then(r => r || caches.match('/index.html')))
    );
    return;
  }

  /* Images, SVG, fonts, SW itself:
     cache-first — instant response, refreshed in background (stale-while-revalidate) */
  event.respondWith(
    caches.match(req).then(cached => {
      const networkFetch = fetch(req).then(res => {
        if (res && res.status === 200 && isSameOrigin) {
          caches.open(CACHE).then(c => c.put(req, res.clone()));
        }
        return res;
      });
      /* Return cached immediately; update cache silently in background */
      return cached || networkFetch.catch(() =>
        new Response('Offline – Ressource nicht verfügbar', {
          status: 503,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        })
      );
    })
  );
});
