"""Builds the browser version into docs/ (GitHub Pages) with pygbag.

pygbag packs every file in the folder it is given, so the game files are
copied into a clean staging folder first (no docs/, tools/, build/, venv/ ...).

The page is then made an installable app (PWA): manifest.json, the app icons
(icons/, from tools/make_icons.py) and sw.js, a service worker that keeps the
game and the Python engine on the phone so it opens again without internet.

Run:  python tools/build_web.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_FILES = ["main.py", "audio.py", "domino_data.py", "fun.py", "calls.py", "modes.py",
              "screens.py", "scenery.py", "howto.py", "stories.py", "town3d.py", "translations.py",
              "video.py", "rhymes_hub.py", "roadsafety.py", "singalong.py", "catalog_more.py", "bangla.py",
              "world.py", "hub_data.json", "videos.json"]
GAME_DIRS = ["pics", "sounds", "fonts"]
APP = "dominowonderdash"
ICONS = ["icon-180.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]
THEME = "#4A90E2"

MANIFEST = {
    "name": "Domino Wonder Dash",
    "short_name": "Wonder Dash",
    "description": "Children learn by tracing, toppling and listening (Class 1-7).",
    "start_url": "./",
    "scope": "./",
    "display": "fullscreen",
    "orientation": "portrait",
    "background_color": "#87CEEB",
    "theme_color": THEME,
    "categories": ["education", "games", "kids"],
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "maskable"},
    ],
}

# Service worker. The game page and its archive: network first (a new version
# shows at once), the saved copy when offline. The pygbag engine on
# pygame-web.github.io is versioned, so it is kept and reused. Videos are
# never stored (too big; they stream).
SW = """// Domino Wonder Dash - keeps the game on the device so it opens offline
const CACHE = 'dwd-%(stamp)s';
const START = ['./', 'index.html', 'manifest.json', 'favicon.png', %(icons)s];

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
  if (/\\.(mp4|webm|ogv|mov)$/i.test(url.pathname) || url.pathname.includes('/videos/')) return;
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
"""

HEAD = """    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="%(theme)s">
    <meta name="apple-mobile-web-app-title" content="Wonder Dash">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="icon-180.png">
    <link rel="icon" type="image/png" href="icon-192.png" sizes="192x192">
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
          navigator.serviceWorker.register('sw.js').catch(function (e) {
            console.warn('offline mode not available', e);
          });
        });
      }
    </script>
"""


def main():
  stage_root = tempfile.mkdtemp(prefix="dwd_web_")
  stage = os.path.join(stage_root, APP)
  os.makedirs(stage)
  for f in GAME_FILES:
    shutil.copy2(os.path.join(ROOT, f), stage)
  for d in GAME_DIRS:
    shutil.copytree(os.path.join(ROOT, d), os.path.join(stage, d))
  for f in GAME_FILES:
    if f.endswith(".py"):
      subprocess.run([sys.executable, "-m", "py_compile", os.path.join(stage, f)], check=True)
  # pygbag reads the game files with Windows' default code page unless told
  # otherwise; Bengali text has bytes that code page cannot decode
  env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
  subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", "Domino Wonder Dash",
                  stage], check=True, env=env)
  docs = os.path.join(ROOT, "docs")
  os.makedirs(docs, exist_ok=True)
  for name in os.listdir(os.path.join(stage, "build", "web")):
    shutil.copy2(os.path.join(stage, "build", "web", name), docs)
  open(os.path.join(docs, ".nojekyll"), "w").close()
  make_pwa(docs)
  shutil.rmtree(stage_root, ignore_errors=True)
  for name in sorted(os.listdir(docs)):
    print(f"{name:28s} {os.path.getsize(os.path.join(docs, name)) / 1e6:6.2f} MB")


def make_pwa(docs):
  """Manifest, icons, service worker and the <head> lines that use them."""
  icons_dir = os.path.join(ROOT, "icons")
  if not all(os.path.exists(os.path.join(icons_dir, n)) for n in ICONS):
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_icons.py")], check=True)
  for name in ICONS:
    shutil.copy2(os.path.join(icons_dir, name), docs)
  shutil.copy2(os.path.join(icons_dir, "icon-48.png"), os.path.join(docs, "favicon.png"))
  with open(os.path.join(docs, "manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(MANIFEST, fh, indent=2)
  with open(os.path.join(docs, "sw.js"), "w", encoding="utf-8") as fh:
    fh.write(SW % {"stamp": time.strftime("%Y%m%d%H%M%S"),
                   "icons": ", ".join(f"'{n}'" for n in ICONS)})
  # the phone app's video player page (video.player_url opens it in Chrome)
  sys.path.insert(0, ROOT)
  import video
  with open(os.path.join(docs, "play.html"), "w", encoding="utf-8") as fh:
    fh.write(video.player_page())
  page = os.path.join(docs, "index.html")
  html = open(page, encoding="utf-8").read()
  if 'rel="manifest"' not in html:
    assert html.count("</head>") == 1, "pygbag page changed: no single </head>"
    html = html.replace("</head>", HEAD % {"theme": THEME} + "</head>")
    with open(page, "w", encoding="utf-8") as fh:
      fh.write(html)


if __name__ == "__main__":
  main()
