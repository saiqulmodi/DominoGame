// Domino Game - keeps the game on the device so it opens offline
const CACHE = 'dwd-20261028202954';
const START = ['./', 'index.html', 'manifest.json', 'favicon.png', 'icon-180.png', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(START)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function keep(req, res) {
  if (res && (res.ok || res.type === 'opaque')) {
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(req, copy));
  }
  return res;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const url = new URL(req.url);
  if (/\.(mp4|webm|ogv|mov)$/i.test(url.pathname) || url.pathname.includes('/videos/')) return;
  const engine = url.hostname === 'pygame-web.github.io';
  if (url.origin !== self.location.origin && !engine) return;
  if (engine) {                              // versioned engine files: saved copy first
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => keep(req, res))));
    return;
  }
  e.respondWith(fetch(req).then((res) => keep(req, res))
    .catch(() => caches.match(req, {ignoreSearch: true})
      .then((hit) => hit || caches.match('index.html'))));
});
