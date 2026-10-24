"""Paints the app icons and the start-up splash into icons/.

Used by the phone app (buildozer.spec), the installable web app
(manifest.json) and the browser tab. Run:  python tools/make_icons.py
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
FONT = os.path.join(ROOT, "fonts", "Sniglet-ExtraBold.ttf")
SKY_TOP, SKY_LOW = (120, 205, 255), (60, 140, 235)
GRASS = (90, 200, 110)
COLOURS = [(233, 69, 96), (255, 140, 40), (255, 204, 0), (80, 200, 90),
           (60, 160, 255), (170, 110, 255)]


def tile(w, h, colour):
  """One domino: coloured tile, dark rim, shine, middle line and two pips."""
  s = pygame.Surface((w, h), pygame.SRCALPHA)
  r = max(2, w // 5)
  dark = tuple(int(c * 0.55) for c in colour)
  pygame.draw.rect(s, dark, (0, 0, w, h), border_radius=r)
  pygame.draw.rect(s, colour, (w // 14 + 1, w // 14 + 1, w - 2 * (w // 14 + 1),
                               h - 2 * (w // 14 + 1)), border_radius=r)
  pygame.draw.line(s, (255, 255, 255), (w // 8, h // 2), (w - w // 8, h // 2), max(1, w // 12))
  for y in (h // 4, 3 * h // 4):
    pygame.draw.circle(s, (255, 255, 255), (w // 2, y), max(2, w // 6))
  return s


def star(surf, c, r, colour=(255, 215, 0)):
  pts = []
  for i in range(10):
    rad = r if i % 2 == 0 else r * 0.45
    a = -math.pi / 2 + i * math.pi / 5
    pts.append((c[0] + rad * math.cos(a), c[1] + rad * math.sin(a)))
  pygame.draw.polygon(surf, colour, pts)
  pygame.draw.polygon(surf, (180, 120, 0), pts, max(1, int(r / 9)))


def icon(size, safe=1.0):
  """Square icon. safe < 1 keeps the picture inside Android's round mask."""
  s = pygame.Surface((size, size))
  for y in range(size):
    k = y / size
    pygame.draw.line(s, tuple(int(a + (b - a) * k) for a, b in zip(SKY_TOP, SKY_LOW)),
                     (0, y), (size, y))
  u = size * safe / 100.0                    # picture units: 0..100 in the safe area
  ox = oy = size * (1 - safe) / 2
  pygame.draw.ellipse(s, GRASS, (ox - 20 * u, oy + 74 * u, 140 * u, 60 * u))
  # a line of dominoes toppling from left to right
  for i, col in enumerate(COLOURS):
    w, h = int(11 * u), int(26 * u)
    t = tile(w, h, col)
    angle = -min(80, max(0, (3 - i) * 26))   # the first ones have fallen
    t = pygame.transform.rotozoom(t, angle, 1)
    x = ox + (14 + i * 14.5) * u
    y = oy + 78 * u
    s.blit(t, t.get_rect(midbottom=(x, y)))
  star(s, (ox + 72 * u, oy + 26 * u), 17 * u)
  try:
    f = pygame.font.Font(FONT, int(24 * u))
    a = f.render("ABC", True, (255, 255, 255))
    sh = f.render("ABC", True, (30, 70, 150))
    s.blit(sh, sh.get_rect(center=(ox + 33 * u + 2 * u / 3, oy + 28 * u + 2 * u / 3)))
    s.blit(a, a.get_rect(center=(ox + 33 * u, oy + 28 * u)))
  except Exception:
    pass
  return s


def splash(w, h):
  s = pygame.Surface((w, h))
  for y in range(h):
    k = y / h
    pygame.draw.line(s, tuple(int(a + (b - a) * k) for a, b in zip(SKY_TOP, SKY_LOW)),
                     (0, y), (w, y))
  n = int(w * 0.6)
  card = pygame.Surface((n, n), pygame.SRCALPHA)        # icon with round corners
  pygame.draw.rect(card, (255, 255, 255), (0, 0, n, n), border_radius=n // 6)
  card.blit(icon(n), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
  rect = card.get_rect(center=(w // 2, int(h * 0.4)))
  pygame.draw.rect(s, (255, 255, 255), rect.inflate(12, 12), border_radius=n // 6 + 6)
  s.blit(card, rect)
  f = pygame.font.Font(FONT, int(w * 0.09))
  for n, line in enumerate(("Domino", "Game")):
    t = f.render(line, True, (255, 255, 255))
    s.blit(t, t.get_rect(center=(w // 2, int(h * 0.68) + n * int(w * 0.11))))
  f2 = pygame.font.Font(FONT, int(w * 0.05))
  t = f2.render("Learn while you play", True, (255, 240, 160))
  s.blit(t, t.get_rect(center=(w // 2, int(h * 0.86))))
  return s


def main():
  pygame.init()
  os.makedirs(OUT, exist_ok=True)
  for n in (48, 180, 192, 512):
    pygame.image.save(icon(n), os.path.join(OUT, f"icon-{n}.png"))
  pygame.image.save(icon(512, safe=0.72), os.path.join(OUT, "icon-maskable-512.png"))
  pygame.image.save(splash(720, 1280), os.path.join(OUT, "presplash.png"))
  print("icons written to", OUT)


if __name__ == "__main__":
  main()
