// Offline cache for the diet plan app. Bump VERSION when files change.
const VERSION = 'pdp-v2';
const CORE = ['./', './index.html', './manifest.json', './print.html', '../app.css', '../data/diet.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => Promise.all(CORE.map(u => fetch(u, { cache: 'no-cache' }).then(r => c.put(u, r)).catch(() => {})))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  e.respondWith(fetch(e.request.url, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request)));
});
