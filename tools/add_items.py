"""Builds only the named categories and merges them into hub_data.json.

build_hub.py rebuilds every picture (and every map) at once; this adds a new
category of OpenMoji pictures without touching the others. Same outlines,
inside parts, pictures, thumbs and Hindi/Bengali word pictures as build_hub.

Run:  python tools/add_items.py "Road Safety"
      python tools/add_items.py "Classic Rhymes" "Desi Rhymes"
Rhymes with Hindi or Bengali words also get one picture per line of words.
A picture that cannot be built is reported and left out (the game hides it).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hub as bh  # noqa: E402  (also puts the game folder on sys.path)

hub = bh.hub


def build(cat):
  ci = list(hub.CATALOG).index(cat)
  items = hub.CATALOG[cat]
  out = {}
  for ii, (name, _desc, (kind, arg)) in enumerate(items):
    if kind != "emoji":
      raise SystemExit(f"{cat}/{name}: only emoji pictures here; use build_hub.py for {kind}")
    try:
      out.update(build_item(cat, ci, ii, name, arg))
    except Exception as exc:          # e.g. a picture OpenMoji does not have
      print(f"FAIL {cat}/{name}: {exc}")
  return out


def build_item(cat, ci, ii, name, arg):
  out = {}
  key = hub.item_key(cat, name)
  slug = bh.slugify(ci, ii, name)
  img, mask = bh.emoji_picture(key, arg)
  loops, frame, pic_frame = bh.outline_from_mask(mask, bh.EMOJI_MIN_FRAC)
  if not loops:
    raise ValueError("empty outline")
  entry = {"closed": True, "loops": loops, "w": round(frame.w, 1), "h": round(frame.h, 1),
           "pic": bh.save_pic(img, slug), "pic_frame": pic_frame}
  entry["parts"] = bh.inner_parts(img, mask, frame, loops)
  entry["thumb"] = bh.save_pic(img.crop(img.getbbox()), slug, "thumb", bh.THUMB)
  if key in bh.TRANSLATIONS:
    hi, bn = bh.TRANSLATIONS[key]
    entry["hi_img"] = bh.native_word_image(hi, slug, "hi")
    entry["bn_img"] = bh.native_word_image(bn, slug, "bn")
  rhyme = hub.rhyme_of(cat, name)
  if rhyme and rhyme.get("native"):     # the words in Hindi / Bengali script
    # the Bengali font has no comma or danda (they would show as empty boxes)
    clean = (lambda t: t.replace(",", "").replace("।", "")) if rhyme["lang"] == "bn" else str
    entry["lyric_imgs"] = [bh.native_word_image(clean(line), f"{slug}_l{n}", rhyme["lang"])
                           for n, line in enumerate(rhyme["native"])]
  out[key] = entry
  print(f"ok   {key:32s} loops={len(loops)} parts={len(entry['parts'])}")
  return out


def main(cats):
  with open(hub.HUB_JSON, encoding="utf-8") as fh:
    data = json.load(fh)
  for cat in cats:
    data.update(build(cat))
  with open(hub.HUB_JSON, "w", encoding="utf-8") as fh:
    json.dump(data, fh, separators=(",", ":"))
  print(f"{len(data)} items in hub_data.json")


if __name__ == "__main__":
  main(sys.argv[1:] or ["Road Safety"])
