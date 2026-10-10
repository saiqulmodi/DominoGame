"""Builds the Picture Data Hub: hub_data.json (dotted outlines) + pics/.

Reads every item from domino_data.CATALOG and makes, for each one:
  - "loops": the real outline (list of point loops) in a 0..1000 space
  - "pic":   the real picture, lined up exactly with the outline
  - "thumb": a small picture for the item buttons (flag for countries, ...)
  - "context": faint neighbour borders (maps and rivers)

Sources: OpenMoji pictures (CC BY-SA 4.0, openmoji.org) and Natural Earth
maps (public domain, India's official view). Downloads are cached in
tools/_downloads so later builds work offline.

Run from anywhere:  python tools/build_hub.py
"""

import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import domino_data as hub  # noqa: E402
from translations import TRANSLATIONS  # noqa: E402

# Kept outside the game folder so the raw map files never ship in the app.
DL = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                  "DominoWonderDash", "downloads")
EMOJI_DL = os.path.join(DL, "openmoji")
PICS = os.path.join(ROOT, "pics")
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
OPENMOJI = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/618x618/"
FONT = r"C:\Windows\Fonts\comicbd.ttf"
SIGN_FONT = r"C:\Windows\Fonts\arialbd.ttf"  # maths signs and the rupee symbol
SIGNS = "+−×÷=₹"
# Hindi is drawn with pygame because it joins letters (क्ष, त्र) correctly
BENG_FONT_URL = ("https://github.com/notofonts/notofonts.github.io/raw/main/"
                 "fonts/NotoSansBengali/hinted/ttf/NotoSansBengali-Bold.ttf")
DEVA_FONT_URL = ("https://github.com/notofonts/notofonts.github.io/raw/main/"
                 "fonts/NotoSansDevanagari/hinted/ttf/NotoSansDevanagari-Bold.ttf")

NORM = 1000.0
CANVAS = 600  # raster size for picture/glyph/shape silhouettes
PIC_MAX = 384
THUMB = 128


# ----------------------------------------------------------------- downloads
def download(url, path):
  if not os.path.exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(3):
      try:
        urllib.request.urlretrieve(url, path + ".part")
        os.replace(path + ".part", path)
        time.sleep(0.15)
        break
      except Exception:
        if attempt == 2:
          raise
        time.sleep(2)
  return path


def emoji_png(code):
  for name in (f"{code}.png", f"{code}-FE0F.png"):
    try:
      return download(OPENMOJI + name, os.path.join(EMOJI_DL, name))
    except Exception:
      continue
  raise FileNotFoundError(f"OpenMoji {code} not found")


def load_geojson(name):
  with open(download(NE + name, os.path.join(DL, name)), encoding="utf-8") as fh:
    return json.load(fh)["features"]


# ----------------------------------------------------------------- geometry
def polygons_of(geom):
  if geom is None:
    return []
  if geom["type"] == "Polygon":
    return [geom["coordinates"]]
  if geom["type"] == "MultiPolygon":
    return geom["coordinates"]
  return []


def lines_of(geom):
  if geom["type"] == "LineString":
    return [geom["coordinates"]]
  if geom["type"] == "MultiLineString":
    return geom["coordinates"]
  return []


def area(pts):
  return 0.5 * abs(sum(x0 * y1 - x1 * y0
                       for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])))


class Projection:
  """Simple equirectangular projection, y pointing down like the screen."""

  def __init__(self, lat0):
    self.k = math.cos(math.radians(lat0))

  def __call__(self, ring):
    return [(lon * self.k, -lat) for lon, lat in ring]


class Frame:
  """Maps a view box onto 0..1000 (longest side)."""

  def __init__(self, x0, y0, x1, y1):
    self.x0, self.y0 = x0, y0
    self.s = NORM / max(x1 - x0, y1 - y0)
    self.w = (x1 - x0) * self.s
    self.h = (y1 - y0) * self.s

  def __call__(self, pts):
    return [((x - self.x0) * self.s, (y - self.y0) * self.s) for x, y in pts]


def bbox(loops):
  xs = [p[0] for lp in loops for p in lp]
  ys = [p[1] for lp in loops for p in lp]
  return min(xs), min(ys), max(xs), max(ys)


def expand(b, f):
  x0, y0, x1, y1 = b
  dx, dy = (x1 - x0) * f, (y1 - y0) * f
  return x0 - dx, y0 - dy, x1 + dx, y1 + dy


def simplify(pts, eps, closed):
  arr = np.array(pts, dtype=np.float32).reshape(-1, 1, 2)
  out = cv2.approxPolyDP(arr, eps, closed).reshape(-1, 2)
  return [(round(float(x), 1), round(float(y), 1)) for x, y in out]


def clip_runs(pts, box):
  """Pieces of a polyline that fall inside box (for faint context lines)."""
  x0, y0, x1, y1 = box
  runs, cur = [], []
  for x, y in pts:
    if x0 <= x <= x1 and y0 <= y <= y1:
      cur.append((x, y))
    else:
      if cur:
        cur.append((x, y))
        runs.append(cur)
      cur = []
  if cur:
    runs.append(cur)
  return [r for r in runs if len(r) >= 2]


# ----------------------------------------------------------- raster outlines
def mask_contours(mask, min_frac):
  """Outer outlines (and big holes) of a white-on-black mask."""
  mask = cv2.GaussianBlur(mask, (5, 5), 0)
  _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
  contours, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
  if not contours:
    return []
  areas = [cv2.contourArea(c) for c in contours]
  biggest = max(areas)
  keep = [(a, c) for a, c in zip(areas, contours) if a >= biggest * min_frac]
  keep.sort(key=lambda t: -t[0])
  return [[(float(x), float(y)) for x, y in c.reshape(-1, 2)] for _, c in keep]


def outline_from_mask(mask, min_frac=0.04):
  loops = mask_contours(mask, min_frac)
  frame = Frame(*bbox(loops))
  out = [simplify(frame(lp), 2.2, True) for lp in loops]
  out = [lp for lp in out if len(lp) >= 3]
  pic_frame = frame([(0, 0), (mask.shape[1], mask.shape[0])])
  return out, frame, [round(v, 1) for v in (*pic_frame[0], *pic_frame[1])]


def save_pic(img, slug, kind="pic", size=PIC_MAX):
  img = img.copy()
  img.thumbnail((size, size), Image.LANCZOS)
  rel = f"pics/{slug}{'' if kind == 'pic' else '_t'}.png"
  compact(img).save(os.path.join(ROOT, rel), optimize=True)
  return rel


def compact(img):
  """Palette PNG (like pngquant): same size picture, a fraction of the bytes,
  so the web/phone package stays small."""
  return img.convert("RGBA").quantize(colors=128, method=Image.Quantize.FASTOCTREE,
                                      dither=Image.Dither.NONE)


def colour_silhouette(mask, fill, edge=(40, 40, 60)):
  """Turn a mask into a friendly coloured picture with a dark outline."""
  h, w = mask.shape
  rgba = np.zeros((h, w, 4), np.uint8)
  rgba[mask > 127] = (*fill, 255)
  contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
  edge_img = np.zeros((h, w), np.uint8)
  cv2.drawContours(edge_img, contours, -1, 255, 8)
  rgba[edge_img > 0] = (*edge, 255)
  return Image.fromarray(rgba, "RGBA")


def hsv(i, n, s=0.65, v=0.95):
  import colorsys
  r, g, b = colorsys.hsv_to_rgb((i / max(1, n)) % 1.0, s, v)
  return int(r * 255), int(g * 255), int(b * 255)


def glyph_mask(ch):
  img = Image.new("L", (CANVAS, CANVAS), 0)
  font = ImageFont.truetype(SIGN_FONT if ch in SIGNS else FONT, 430)
  ImageDraw.Draw(img).text((CANVAS / 2, CANVAS / 2), ch, fill=255, font=font,
                           anchor="mm")
  return np.array(img)


_DEVA_FONTS = {}


def deva_font(size):
  import pygame  # only needed for Hindi
  if size not in _DEVA_FONTS:
    pygame.font.init()
    path = download(DEVA_FONT_URL, os.path.join(DL, "fonts", "NotoSansDevanagari-Bold.ttf"))
    f = pygame.font.Font(path, size)
    f.set_script("Deva")
    _DEVA_FONTS[size] = f
  return _DEVA_FONTS[size]


def hindi_mask(text):
  import pygame
  surf = deva_font(330).render(text, True, (255, 255, 255))
  alpha = np.array(pygame.surfarray.pixels_alpha(surf)).T.copy()
  h, w = alpha.shape
  scale = min(1.0, (CANVAS * 0.84) / max(w, h))
  if scale < 1.0:
    alpha = cv2.resize(alpha, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    h, w = alpha.shape
  mask = np.zeros((CANVAS, CANVAS), np.uint8)
  y0, x0 = (CANVAS - h) // 2, (CANVAS - w) // 2
  mask[y0:y0 + h, x0:x0 + w] = alpha
  return mask


_BENG_FONTS = {}


def beng_font(size):
  import pygame
  if size not in _BENG_FONTS:
    pygame.font.init()
    path = download(BENG_FONT_URL, os.path.join(DL, "fonts", "NotoSansBengali-Bold.ttf"))
    f = pygame.font.Font(path, size)
    f.set_script("Beng")
    _BENG_FONTS[size] = f
  return _BENG_FONTS[size]


def native_word_image(text, slug, lang):
  """Hindi or Bengali word drawn as a picture (shows on every device)."""
  import pygame
  font = deva_font(72) if lang == "hi" else beng_font(72)
  surf = font.render(text, True, (255, 230, 120))
  raw = pygame.image.tobytes(surf, "RGBA")
  img = Image.frombytes("RGBA", surf.get_size(), raw)
  img = img.crop(img.getbbox())
  rel = f"pics/{slug}_{lang}.png"
  compact(img).save(os.path.join(ROOT, rel), optimize=True)
  return rel


def hindi_word_image(text, slug):
  import pygame
  surf = deva_font(96).render(text, True, (255, 204, 0))
  raw = pygame.image.tobytes(surf, "RGBA")
  img = Image.frombytes("RGBA", surf.get_size(), raw)
  img = img.crop(img.getbbox())
  rel = f"pics/{slug}_w.png"
  compact(img).save(os.path.join(ROOT, rel), optimize=True)
  return rel


def shape_mask(kind):
  img = Image.new("L", (CANVAS, CANVAS), 0)
  d = ImageDraw.Draw(img)
  c, r = CANVAS / 2, CANVAS * 0.4

  def poly(n, rot=-math.pi / 2, rad=r):
    return [(c + rad * math.cos(rot + 2 * math.pi * i / n),
             c + rad * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]

  if kind == "circle":
    d.ellipse((c - r, c - r, c + r, c + r), fill=255)
  elif kind == "square":
    d.rectangle((c - r * 0.85, c - r * 0.85, c + r * 0.85, c + r * 0.85), fill=255)
  elif kind == "rectangle":
    d.rectangle((c - r, c - r * 0.55, c + r, c + r * 0.55), fill=255)
  elif kind == "triangle":
    d.polygon(poly(3, rad=r * 1.1), fill=255)
  elif kind == "pentagon":
    d.polygon(poly(5), fill=255)
  elif kind == "hexagon":
    d.polygon(poly(6, rot=0), fill=255)
  elif kind == "diamond":
    d.polygon([(c, c - r), (c + r * 0.7, c), (c, c + r), (c - r * 0.7, c)], fill=255)
  elif kind == "oval":
    d.ellipse((c - r * 0.7, c - r, c + r * 0.7, c + r), fill=255)
  elif kind == "star":
    pts = []
    for i in range(10):
      rad = r if i % 2 == 0 else r * 0.42
      a = -math.pi / 2 + i * math.pi / 5
      pts.append((c + rad * math.cos(a), c + rad * math.sin(a)))
    d.polygon(pts, fill=255)
  elif kind == "heart":
    pts = []
    for i in range(200):
      t = 2 * math.pi * i / 200
      x = 16 * math.sin(t) ** 3
      y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
      pts.append((c + x * r / 16, c - y * r / 16 - r * 0.05))
    d.polygon(pts, fill=255)
  elif kind == "moon":
    d.ellipse((c - r, c - r, c + r, c + r), fill=255)
    d.ellipse((c - r * 0.45, c - r * 1.05, c + r * 1.35, c + r * 0.75), fill=0)
  elif kind == "igloo":
    base = c + r * 0.45
    d.pieslice((c - r, base - r, c + r, base + r), 180, 360, fill=255)
    d.pieslice((c - r * 0.28, base - r * 0.32, c + r * 0.28, base + r * 0.32),
               180, 360, fill=0)
  elif kind == "road":
    pts = [(c + r * 0.45 * math.sin(i / 40 * 2.2 * math.pi), c - r + 2 * r * i / 40)
           for i in range(41)]
    d.line(pts, fill=255, width=int(r * 0.4), joint="curve")
  elif kind == "railway":
    for i in range(7):
      y = c - r + i * (2 * r / 6)
      d.rectangle((c - r * 0.5, y - r * 0.05, c + r * 0.5, y + r * 0.05), fill=255)
    for x in (c - r * 0.3, c + r * 0.3):
      d.rectangle((x - r * 0.05, c - r * 1.02, x + r * 0.05, c + r * 1.02), fill=255)
  elif kind == "arrow":
    d.polygon([(c - r, c - r * 0.25), (c + r * 0.2, c - r * 0.25),
               (c + r * 0.2, c - r * 0.6), (c + r, c), (c + r * 0.2, c + r * 0.6),
               (c + r * 0.2, c + r * 0.25), (c - r, c + r * 0.25)], fill=255)
  else:
    raise ValueError(kind)
  return np.array(img)


def landmark_mask(spec):
  if isinstance(spec, tuple):
    half, holes = spec
  else:
    half, holes = spec, []
  full = list(half) + [(100 - x, y) for x, y in reversed(half)]
  m, s = CANVAS * 0.08, CANVAS * 0.84 / 100

  def tf(pts):
    return [(m + x * s, m + y * s) for x, y in pts]

  img = Image.new("L", (CANVAS, CANVAS), 0)
  d = ImageDraw.Draw(img)
  d.polygon(tf(full), fill=255)
  for hole in holes:
    d.polygon(tf(hole), fill=0)
  return np.array(img)


# ------------------------------------------------------------ map rendering
def render_map(frame, fills, lines=(), size=PIC_MAX * 2):
  """fills: [(rings, rgb, outline_rgb)], lines: [(pts, rgb, width)]"""
  k = size / max(frame.w, frame.h)
  w, h = max(1, int(frame.w * k)), max(1, int(frame.h * k))
  img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  d = ImageDraw.Draw(img)
  for rings, fill, edge in fills:
    for ring in rings:
      pts = [(x * k, y * k) for x, y in frame(ring)]
      if len(pts) >= 3:
        d.polygon(pts, fill=fill, outline=edge)
        d.line(pts + pts[:1], fill=edge, width=max(2, size // 200))
  for pts, col, width in lines:
    d.line([(x * k, y * k) for x, y in frame(pts)], fill=col, width=width,
           joint="curve")
  return img


def flag_thumb(iso2, slug):
  code = "-".join(f"{0x1F1E6 + ord(ch) - 65:X}" for ch in iso2.upper())
  img = Image.open(emoji_png(code)).convert("RGBA")
  return save_pic(img.crop(img.getbbox()), slug, "thumb", THUMB)


# --------------------------------------------------------------------- build
def slugify(ci, ii, name):
  return f"{ci:02d}_{ii:02d}_" + re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def main():
  os.makedirs(PICS, exist_ok=True)
  countries = load_geojson("ne_10m_admin_0_countries_ind.geojson")
  states = [f for f in load_geojson("ne_10m_admin_1_states_provinces.geojson")
            if f["properties"].get("adm0_a3") == "IND"]
  rivers = load_geojson("ne_10m_rivers_lake_centerlines.geojson")

  def country(name):
    for f in countries:
      p = f["properties"]
      if name in (p.get("NAME"), p.get("ADMIN"), p.get("NAME_LONG")):
        return f
    raise KeyError(name)

  def biggest_ring(feature, proj):
    rings = [proj(poly[0]) for poly in polygons_of(feature["geometry"])]
    rings.sort(key=area, reverse=True)
    return rings[0], rings[1:]

  def neighbours(view, proj, skip=None, extra=()):
    """Borders around the item, clipped to the view (faint context)."""
    x0, y0, x1, y1 = view
    out = []
    for f in list(countries) + list(extra):
      if f is skip:
        continue
      for poly in polygons_of(f["geometry"]):
        ring = proj(poly[0])
        bx0, by0, bx1, by1 = bbox([ring])
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
          continue
        out.append(ring)
    return out

  def lat_centre(feature_or_lines):
    lats = [pt[1] for ln in feature_or_lines for pt in ln]
    return (min(lats) + max(lats)) / 2

  india = country("India")
  result, failed = {}, []
  for ci, (cat, items) in enumerate(hub.CATALOG.items()):
    for ii, (name, _desc, (kind, arg)) in enumerate(items):
      if kind == "custom":
        key = hub.item_key(cat, name)
        if key in TRANSLATIONS:
          slug = slugify(ci, ii, name)
          hi, bn = TRANSLATIONS[key]
          result[key] = {"hi_img": native_word_image(hi, slug, "hi"),
                         "bn_img": native_word_image(bn, slug, "bn")}
        continue
      key = hub.item_key(cat, name)
      slug = slugify(ci, ii, name)
      try:
        entry = {"closed": True}
        if kind in ("emoji", "glyph", "shape", "landmark", "hindi"):
          if kind == "emoji":
            img = Image.open(emoji_png(arg)).convert("RGBA")
            mask = (np.array(img)[:, :, 3] > 100).astype(np.uint8) * 255
            mask = cv2.morphologyEx(
                mask, cv2.MORPH_CLOSE,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
            pic = img
            min_frac = 0.02
          elif kind == "glyph":
            mask = glyph_mask(arg)
            pic = colour_silhouette(mask, hsv(ii, len(items)))
            min_frac = 0.01
          elif kind == "hindi":
            mask = hindi_mask(name)
            pic = colour_silhouette(mask, hsv(ii, len(items)))
            min_frac = 0.005
            entry["word_img"] = hindi_word_image(arg[0], slug)
          elif kind == "shape":
            mask = shape_mask(arg)
            fill = {"road": (120, 120, 130), "railway": (150, 100, 60),
                    "igloo": (225, 240, 255)}.get(arg, hsv(ii, len(items)))
            pic = colour_silhouette(mask, fill)
            min_frac = 0.04
          else:
            mask = landmark_mask(arg)
            fill = (226, 120, 80) if cat == "Bridges" else (236, 196, 140)
            pic = colour_silhouette(mask, fill, (90, 60, 40))
            min_frac = 0.01
          loops, frame, pic_frame = outline_from_mask(mask, min_frac)
          entry.update(loops=loops, w=round(frame.w, 1), h=round(frame.h, 1),
                       pic=save_pic(pic, slug), pic_frame=pic_frame)
          entry["thumb"] = save_pic(pic.crop(pic.getbbox()), slug, "thumb", THUMB)

        elif kind in ("country", "state"):
          if kind == "country":
            feat = country(arg)
            others = []
          else:
            feat = next(f for f in states if f["properties"]["name"] == arg)
            others = [f for f in states if f is not feat]
          proj = Projection(lat_centre([poly[0] for poly in polygons_of(feat["geometry"])]))
          main_ring, islands = biggest_ring(feat, proj)
          frame = Frame(*bbox([main_ring]))
          eps = 2.0
          loops = [simplify(frame(main_ring), eps, True)]
          view = expand(bbox([main_ring]), 0.35)
          ctx_rings = neighbours(view, proj, skip=feat, extra=others)
          ctx_rings += [r for r in islands if area(r) > area(main_ring) * 0.002]
          ctx = []
          vbox = (-NORM * 0.4, -NORM * 0.4, frame.w + NORM * 0.4, frame.h + NORM * 0.4)
          for ring in ctx_rings:
            for run in clip_runs(frame(ring), vbox):
              s = simplify(run, 3.0, False)
              if len(s) >= 2:
                ctx.append(s)
          fills = [([main_ring] + islands, (120, 200, 120, 255), (30, 90, 40, 255))]
          if kind == "state":
            fills = [([main_ring], (250, 170, 70, 255), (150, 80, 20, 255))]
          pic = render_map(frame, fills)
          entry.update(loops=loops, w=round(frame.w, 1), h=round(frame.h, 1),
                       context=ctx, pic=save_pic(pic, slug),
                       pic_frame=[0, 0, round(frame.w, 1), round(frame.h, 1)])
          if kind == "country":
            p = feat["properties"]
            iso = p.get("ISO_A2") if p.get("ISO_A2", "-99") != "-99" else p.get("ISO_A2_EH")
            entry["thumb"] = flag_thumb(iso, slug)
          else:
            ip = Projection(22)
            iring, _ = biggest_ring(india, ip)
            ifr = Frame(*bbox([iring]))
            th = render_map(ifr, [
                ([iring], (200, 230, 200, 255), (60, 110, 60, 255)),
                ([biggest_ring(feat, ip)[0]], (250, 140, 40, 255), (150, 70, 10, 255)),
            ], size=THUMB * 2)
            entry["thumb"] = save_pic(th, slug, "thumb", THUMB)

        elif kind == "river":
          wanted = {plain(n) for n in arg}
          segs = []
          for f in rivers:
            p = f["properties"]
            names = {plain(str(p.get(k) or "")) for k in ("name", "name_en", "name_alt")}
            if names & wanted:
              segs += [list(map(tuple, ln)) for ln in lines_of(f["geometry"])]
          if not segs:
            raise KeyError(f"river {arg} not in Natural Earth")
          chain = join_segments(segs)
          proj = Projection(lat_centre([chain]))
          course = proj(chain)
          frame_box = expand(bbox([course]), 0.12)
          frame = Frame(*frame_box)
          loops = [simplify(frame(course), 1.5, False)]
          ctx_rings = neighbours(expand(frame_box, 0.3), proj)
          ctx = []
          vbox = (-NORM * 0.4, -NORM * 0.4, frame.w + NORM * 0.4, frame.h + NORM * 0.4)
          for ring in ctx_rings:
            for run in clip_runs(frame(ring), vbox):
              s = simplify(run, 3.0, False)
              if len(s) >= 2:
                ctx.append(s)
          pic = render_map(frame, [(ctx_rings, (205, 235, 200, 255), (110, 150, 110, 255))],
                           [(course, (30, 110, 230, 255), 10)])
          entry.update(closed=False, loops=loops, w=round(frame.w, 1),
                       h=round(frame.h, 1), context=ctx, pic=save_pic(pic, slug),
                       pic_frame=[0, 0, round(frame.w, 1), round(frame.h, 1)])
          entry["thumb"] = save_pic(pic, slug, "thumb", THUMB)
        else:
          raise ValueError(kind)

        if not entry["loops"]:
          raise ValueError("empty outline")
        if key in TRANSLATIONS:
          hi, bn = TRANSLATIONS[key]
          entry["hi_img"] = native_word_image(hi, slug, "hi")
          entry["bn_img"] = native_word_image(bn, slug, "bn")
        result[key] = entry
        print(f"ok   {key:32s} loops={len(entry['loops'])} "
              f"pts={sum(len(l) for l in entry['loops'])}")
      except Exception as exc:
        failed.append((key, str(exc)))
        print(f"FAIL {key}: {exc}")

  with open(hub.HUB_JSON, "w", encoding="utf-8") as fh:
    json.dump(result, fh, separators=(",", ":"))
  print(f"\n{len(result)} items written to hub_data.json, {len(failed)} failed")
  for k, e in failed:
    print("  missing:", k, e)


def plain(text):
  """Lower-case name without accents (Godāvari -> godavari)."""
  text = unicodedata.normalize("NFKD", text)
  return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def join_segments(segs, tol=0.02):
  """Joins river pieces end to end into the longest single course."""
  def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

  def length(s):
    return sum(d(a, b) for a, b in zip(s, s[1:]))

  remaining = sorted(segs, key=length, reverse=True)
  chain = list(remaining.pop(0))
  grown = True
  while grown and remaining:
    grown = False
    for i, s in enumerate(remaining):
      if d(chain[-1], s[0]) < tol:
        chain += s[1:]
      elif d(chain[-1], s[-1]) < tol:
        chain += s[::-1][1:]
      elif d(chain[0], s[-1]) < tol:
        chain = s[:-1] + chain
      elif d(chain[0], s[0]) < tol:
        chain = s[::-1][:-1] + chain
      else:
        continue
      remaining.pop(i)
      grown = True
      break
  return chain


if __name__ == "__main__":
  main()
