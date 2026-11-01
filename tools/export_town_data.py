"""Data for the 3D Wonder Town (town_web/): every house's categories, each with a small picture, so the town can
show them as 3D picture blocks (no words) and open the game straight on the chosen one.

Writes town_web/data.json  {house key: [{"pic": "thumbs/<n>.webp" | null, "glyph": key | null}, ...]}
in the same order as the game's own category list for that house (world.WorldScene.enter: Maths Play first
at the Number House, Cross the Road last at the Safety Park), so ?open=<key>&cat=<index> matches.
Thumbnails: the category's first picture, fitted into 160 px, WebP (town_web/thumbs/).
Run:  python tools/export_town_data.py   (tools/build_web.py runs it too)
"""

import json
import os
import shutil
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

import domino_data as hub  # noqa: E402
import town3d  # noqa: E402

ROAD_GAME = "Cross the Road"   # same names as world.py
MATHS_GAME = "Maths Play"
OUT = os.path.join(ROOT, "town_web")
THUMBS = os.path.join(OUT, "thumbs")
SIZE = 160


def first_picture(cat):
  for item in hub.CATEGORIES_HUB.get(cat, {}).values():
    pic = item.get("pic")
    if pic and os.path.exists(os.path.join(ROOT, pic)):
      return os.path.join(ROOT, pic)
  return None


def thumb(src, n):
  im = Image.open(src).convert("RGBA")
  bbox = im.getbbox()
  if bbox:
    im = im.crop(bbox)
  im.thumbnail((SIZE, SIZE), Image.LANCZOS)
  canvas = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
  canvas.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
  name = f"{n}.webp"
  canvas.save(os.path.join(THUMBS, name), "WEBP", quality=82, method=6)
  return "thumbs/" + name


def main():
  subjects = hub.subjects()
  shutil.rmtree(THUMBS, ignore_errors=True)
  os.makedirs(THUMBS)
  data, n = {}, 0
  for b in town3d.build_world():
    if b.kind != "subject":
      continue
    cats = list(subjects.get(b.payload, []))
    if b.key == "safety":
      cats.append(ROAD_GAME)
    if b.key == "maths":
      cats.insert(0, MATHS_GAME)
    entries = []
    for cat in cats:
      if cat == MATHS_GAME:
        entries.append({"pic": None, "glyph": "mathsplay"})
      elif cat == ROAD_GAME:
        entries.append({"pic": None, "glyph": "roadgame"})
      else:
        src = first_picture(cat)
        entries.append({"pic": thumb(src, n) if src else None, "glyph": None if src else "star"})
        n += 1
    data[b.key] = entries
  with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, separators=(",", ":"))
  size = sum(os.path.getsize(os.path.join(THUMBS, f)) for f in os.listdir(THUMBS))
  print(f"{len(data)} houses, {sum(len(v) for v in data.values())} categories, {n} thumbnails, {size / 1e3:.0f} KB")


if __name__ == "__main__":
  main()
