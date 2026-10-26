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
# Every .py in the game folder is a game module (tools live in tools/), so all of
# them ship. A hand-kept list missed magic.py on 17-Oct and the web game stopped at
# "No module named 'magic'" (grey screen) until 18-Oct.
GAME_FILES = sorted(f for f in os.listdir(ROOT) if f.endswith(".py")) + ["hub_data.json", "videos.json"]
GAME_DIRS = ["pics", "sounds", "fonts", "labels"]   # labels: Hindi / Bangla button words
APP = "dominowonderdash"
ICONS = ["icon-180.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png"]
THEME = "#4A90E2"

MANIFEST = {
    "name": "Domino Game",
    "short_name": "Domino Game",
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
SW = """// Domino Game - keeps the game on the device so it opens offline
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
    <meta name="apple-mobile-web-app-title" content="Domino Game">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="icon-180.png">
    <link rel="icon" type="image/png" href="icon-192.png" sizes="192x192">
    <script data-goatcounter="https://dominogame.goatcounter.com/count"
            async src="//gc.zgo.at/count.js"></script>
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
          navigator.serviceWorker.register('sw.js').catch(function (e) {
            console.warn('offline mode not available', e);
          });
        });
      }
    </script>
    <!-- Firebase Analytics - anonymous usage tracking (no personal data) -->
    <script type="module">
      import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
      import { getAnalytics, logEvent } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-analytics.js";

      const firebaseConfig = {
        apiKey:            "AIzaSyC063203QLH1oldbRfLUxivnUP9TeH6rCg",
        authDomain:        "dominogame-ee7d8.firebaseapp.com",
        projectId:         "dominogame-ee7d8",
        storageBucket:     "dominogame-ee7d8.firebasestorage.app",
        messagingSenderId: "789561435508",
        appId:             "1:789561435508:web:c79869f6d1dfc52949b821",
        measurementId:     "G-X5MCMTN4T7"
      };

      const app       = initializeApp(firebaseConfig);
      const analytics = getAnalytics(app);

      const sessionStart = Date.now();
      logEvent(analytics, "game_session_start", {
        platform: /Mobi|Android/i.test(navigator.userAgent) ? "mobile" : "desktop"
      });

      window.addEventListener("beforeunload", () => {
        const seconds = Math.round((Date.now() - sessionStart) / 1000);
        logEvent(analytics, "game_session_end", { duration_seconds: seconds });
      });

      document.addEventListener("click", function onFirstClick() {
        logEvent(analytics, "game_started");
        document.removeEventListener("click", onFirstClick);
      }, { once: true });

      // milestones from the game (counter.count_event): class travel, finished
      // pictures, celebrations - anonymous names only
      window.dominoEvent = function (name, value) {
        try { logEvent(analytics, name, { value: String(value) }); } catch (e) {}
        try {
          if (window.goatcounter && window.goatcounter.count) {
            window.goatcounter.count({ path: "/event/" + name + "/" + value, title: name, event: true });
          }
        } catch (e) {}
      };
    </script>
"""


def main():
  stage_root = tempfile.mkdtemp(prefix="dwd_web_")
  stage = os.path.join(stage_root, APP)
  os.makedirs(stage)
  for f in GAME_FILES:
    if f == "hub_data.json":             # outline points to whole pixels: smaller download
      write_compact_hub(os.path.join(stage, f))
    else:
      shutil.copy2(os.path.join(ROOT, f), stage)
  for d in GAME_DIRS:
    if d == "pics":                      # only pictures the game uses (old builds
      copy_used_pics(os.path.join(stage, d))   # leave unused ones behind)
    else:
      shutil.copytree(os.path.join(ROOT, d), os.path.join(stage, d))
  for f in GAME_FILES:
    if f.endswith(".py"):
      subprocess.run([sys.executable, "-m", "py_compile", os.path.join(stage, f)], check=True)
  # pygbag reads the game files with Windows' default code page unless told
  # otherwise; Bengali text has bytes that code page cannot decode
  env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
  subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", "Domino Game",
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


def write_compact_hub(dest):
  """hub_data.json with outline points rounded to whole pixels (the canvas
  cannot show a tenth of a pixel) and no spaces."""
  with open(os.path.join(ROOT, "hub_data.json"), encoding="utf-8") as fh:
    data = json.load(fh)

  def snap(x):
    if isinstance(x, float):
      return int(round(x))
    if isinstance(x, list):
      return [snap(v) for v in x]
    if isinstance(x, dict):
      return {k: (v if k in ("w", "h", "pic_frame") else snap(v)) for k, v in x.items()}
    return x

  with open(dest, "w", encoding="utf-8") as fh:
    json.dump({k: snap(v) for k, v in data.items()}, fh, separators=(",", ":"),
              ensure_ascii=False)


def used_pics():
  """Every picture hub_data.json points to (the Stratos copy must stay small)."""
  with open(os.path.join(ROOT, "hub_data.json"), encoding="utf-8") as fh:
    data = json.load(fh)
  used = set()

  def walk(x):
    if isinstance(x, dict):
      for v in x.values():
        walk(v)
    elif isinstance(x, list):
      for v in x:
        walk(v)
    elif isinstance(x, str) and x.startswith("pics/"):
      used.add(x[len("pics/"):])

  walk(data)
  return used


WEB_PIC_MAX = 448      # px: the game canvas is 450 wide, so bigger is never seen
WEB_THUMB_MAX = 88     # px: menu, banner and word-card thumbnails are drawn at most ~74 px


def copy_used_pics(dest):
  """Copies the used pictures; full-size pictures are scaled down to fit the
  450-wide canvas (keeps the Stratos copy under its 20 MB limit)."""
  import re
  from PIL import Image
  sys.path.insert(0, os.path.join(ROOT, "tools"))
  from build_hub import compact
  os.makedirs(dest)
  used = used_pics()
  for name in os.listdir(os.path.join(ROOT, "pics")):
    if name not in used:
      continue
    src = os.path.join(ROOT, "pics", name)
    if re.search(r"_(hi|bn|w|l\d+(_hi|_bn)?)\.png$", name):
      shutil.copy2(src, dest)            # word pictures stay as they are
      continue
    img = Image.open(src)
    limit = WEB_THUMB_MAX if name.endswith("_t.png") else WEB_PIC_MAX
    if max(img.size) <= limit:
      shutil.copy2(src, dest)
      continue
    k = limit / max(img.size)
    img = img.convert("RGBA").resize((round(img.width * k), round(img.height * k)),
                                      Image.LANCZOS)
    out = os.path.join(dest, name)
    compact(img).save(out, optimize=True)         # the hub's own picture packer
    if os.path.getsize(out) >= os.path.getsize(src):
      shutil.copy2(src, out)                      # keep whichever is smaller


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
