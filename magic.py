"""Domino magic: every cascade is a little show, and never the same twice.

Each time the dominoes are pushed, a Show is made with
  - its own music: an instrument (bells, xylophone, marimba, piano, harp, flute,
    steel drum, kalimba, sitar, water drops), a scale (Indian ragas Bhupali, Yaman,
    Kafi, or major, pentatonic, whole-tone ...), a melody shape (rising, falling,
    waves, zigzag, mountain, ocean) and a rhythm (waltz, march, swing, gallop ...),
    one note every few dominoes, never the same as the show before;
  - its own timing: a slow start, waves of speed, one or two "twists" where
    the line almost stops ("will it fall?") and then bursts forward, tiny
    stops of a fraction of a second, and a
    slow-motion ending, about 4-8 seconds in all whatever the picture;
  - its own magic along the line: butterflies, fireflies, a rainbow trail,
    stars or bubbles rising from the falling dominoes;
  - a butterfly-effect finale: butterflies burst out of the finished picture.
"""

import math
import random

import pygame

SCALES = [
    ("Bhupali", [0, 2, 4, 7, 9]),
    ("Yaman", [0, 2, 4, 6, 7, 9, 11]),
    ("Kafi", [0, 2, 3, 5, 7, 9, 10]),
    ("Major", [0, 2, 4, 5, 7, 9, 11]),
    ("Pentatonic", [0, 3, 5, 7, 10]),
    ("Whole tone", [0, 2, 4, 6, 8, 10]),
    ("Bilawal", [0, 2, 4, 5, 7, 9, 11, 12]),
]
CONTOURS = ["up", "down", "wave", "zigzag", "mountain", "valley", "ocean"]
STYLES = ["butterflies", "fireflies", "rainbow", "stars", "bubbles"]
INSTRUMENTS = ["bell", "xylophone", "marimba", "piano", "harp", "flute", "steel drum",
               "kalimba", "sitar", "water drop"]
# Rhythms: how long each note waits, cycling (1 = an even step); the first is the strong beat
RHYTHMS = {
    "flowing waves": [1.0],
    "waltz": [1.5, 0.75, 0.75],
    "march": [1.2, 0.8],
    "swing": [1.35, 0.65],
    "gallop": [0.6, 0.6, 1.8],
    "skip": [0.7, 1.3, 1.0, 1.0],
}
NOTES_PER_SECOND = 7
_LAST = {}                 # the previous show's music: the next one never repeats it


def pick(rng, key, options):
  """A random choice that is never the previous show's choice."""
  fresh = [o for o in options if o != _LAST.get(key)] or list(options)
  _LAST[key] = choice = rng.choice(fresh)
  return choice


def plan_music(seed=None):
  """The next cascade's music, chosen when a picture opens (so its instrument's
  notes can be made while the child traces). Never the same as the last one."""
  rng = random.Random(seed)
  return {"inst": pick(rng, "inst", INSTRUMENTS),
          "scale": pick(rng, "scale", [s[0] for s in SCALES]),
          "contour": pick(rng, "contour", CONTOURS),
          "rhythm": pick(rng, "rhythm", list(RHYTHMS)),
          "style": pick(rng, "style", STYLES)}
WING = [(255, 120, 180), (255, 200, 60), (120, 200, 255), (170, 120, 255), (120, 230, 140),
        (255, 150, 80)]


def hue(h, s=85, v=100):
  c = pygame.Color(0)
  c.hsva = (int(h) % 360, s, v, 100)
  return c


class Show:

  def __init__(self, n, seed=None, music=None):
    rng = random.Random(seed)
    self.rng = rng
    self.n = n
    music = music or plan_music(rng.random())
    self.inst = music["inst"]
    self.scale_name = music["scale"]
    self.scale = dict(SCALES)[self.scale_name]
    self.root = rng.choice([60, 62, 63, 65, 67])
    self.contour = music["contour"]
    self.rhythm_name = music["rhythm"]
    self.rhythm = RHYTHMS[self.rhythm_name]
    self.style = music["style"]
    self.hue0 = rng.uniform(0, 360)
    self.ph = rng.uniform(0, 2 * math.pi)
    self.duration = min(8.0, max(4.0, 3.0 + 0.03 * n))
    phase = rng.uniform(0, 2 * math.pi)
    waves = rng.choice([2, 3, 4])
    depth = rng.uniform(0.45, 0.65)        # waves of speed: slow ... quick ... slow
    self.twists = sorted((rng.uniform(0.3, 0.75), rng.uniform(0.03, 0.06))
                         for _ in range(rng.choice([1, 2])))
    self.step = max(1, round(n / (self.duration * NOTES_PER_SECOND)))
    weights = []
    for i in range(n):
      p = i / max(1, n - 1)
      ramp = 0.35 + 0.65 * min(1.0, p / 0.25)                 # slow start
      speed = ramp * (1.0 + depth * math.sin(p * math.pi * 2 * waves + phase))
      for c, w in self.twists:
        if abs(p - c) < w:
          speed *= 0.22                                       # suspense ...
        elif c + w <= p < c + w + 0.05:
          speed *= 1.8                                        # ... then a burst
      if p > 0.92:
        speed *= 0.55                                         # slow-motion end
      beat = self.rhythm[(i // self.step) % len(self.rhythm)]  # the rhythm's long and short notes
      weights.append(max(0.05, speed / beat))
    raw = [1.0 / s for s in weights]
    k = self.duration / sum(raw)
    self.gaps = [r * k for r in raw]                          # s until the next push
    # a few tiny stops, a fraction of a second, as if the chain holds its breath
    for _ in range(rng.choice([1, 2, 3])):
      j = int(rng.uniform(0.15, 0.85) * n) // self.step * self.step
      if 0 < j < n - 1:
        self.gaps[j] += rng.uniform(0.15, 0.4)
    self.fx = []                                              # magic particles
    self.teased = set()

  # ------------------------------------------------------------ music
  def note(self, i):
    """The bell note for domino i, or None (one note every few dominoes)."""
    if i % self.step:
      return None
    j, m = i // self.step, max(1, (self.n - 1) // self.step)
    span = len(self.scale) * 2
    f = j / m
    shape = {
        "up": f, "down": 1 - f,
        "wave": 0.5 + 0.5 * math.sin(j * 0.6),
        "zigzag": (j % 4) / 3,
        "mountain": 1 - abs(2 * f - 1),
        "valley": abs(2 * f - 1),
        "ocean": 0.5 + 0.35 * math.sin(j * 0.5 + self.ph) + 0.15 * math.sin(j * 1.7),
    }[self.contour]
    d = int(round(max(0.0, min(1.0, shape)) * (span - 1)))
    return self.root + self.scale[d % len(self.scale)] + 12 * (d // len(self.scale))

  def accent(self, i):
    """Volume of domino i's note: the rhythm's strong beat is louder."""
    return 1.0 if (i // self.step) % len(self.rhythm) == 0 else 0.68

  def tip_speed(self, i, push=0.3):
    """rad/s: domino i tilts far enough to push the next one exactly on time."""
    return max(1.2, push / self.gaps[i])

  def is_twist(self, i):
    p = i / max(1, self.n - 1)
    return any(abs(p - c) < w for c, w in self.twists)

  # ------------------------------------------------------------ magic along the line
  def pushed(self, i, x, y):
    """Domino i starts to fall at (x, y): magic for this show's style."""
    r = self.rng
    h = self.hue0 + 300 * i / max(1, self.n)
    # a ring of light at every push: a glowing wave runs along the picture
    self.fx.append({"k": "ring", "x": x, "y": y, "vx": 0, "vy": 0, "t": 0.0, "life": 0.7,
                    "c": hue(h)})
    if self.style == "butterflies" and i % max(2, self.step * 2) == 0:
      self.fx.append({"k": "fly", "x": x, "y": y, "vx": r.uniform(-30, 30), "vy": r.uniform(-70, -40),
                      "t": 0.0, "life": r.uniform(2.0, 3.0), "c": r.choice(WING), "s": 1.4})
    elif self.style == "fireflies" and i % max(1, self.step) == 0:
      self.fx.append({"k": "glow", "x": x, "y": y, "vx": r.uniform(-25, 25), "vy": r.uniform(-30, -10),
                      "t": 0.0, "life": r.uniform(1.5, 2.5), "c": (255, 240, 120), "ph": r.uniform(0, 6)})
    elif self.style == "rainbow":
      self.fx.append({"k": "spark", "x": x, "y": y, "vx": r.uniform(-15, 15), "vy": r.uniform(-40, -15),
                      "t": 0.0, "life": 1.0, "c": hue(h)})
    elif self.style == "stars" and i % max(1, self.step) == 0:
      self.fx.append({"k": "star", "x": x, "y": y, "vx": 0, "vy": -35, "t": 0.0, "life": 1.4,
                      "c": hue(45 + 20 * r.random(), 70), "rot": r.uniform(0, 6)})
    elif self.style == "bubbles" and i % max(1, self.step) == 0:
      self.fx.append({"k": "bubble", "x": x, "y": y, "vx": r.uniform(-10, 10), "vy": r.uniform(-50, -30),
                      "t": 0.0, "life": r.uniform(1.6, 2.4), "c": hue(h, 40), "r": r.uniform(6, 12)})

  def finale(self, rect):
    """The butterfly effect: butterflies burst out of the finished picture."""
    r = self.rng
    cx, cy = rect.center
    for k in range(18):
      a = k / 18 * 2 * math.pi + r.uniform(-0.2, 0.2)
      sp = r.uniform(70, 140)
      self.fx.append({"k": "fly", "x": cx + r.uniform(-40, 40), "y": cy + r.uniform(-40, 40),
                      "vx": math.cos(a) * sp, "vy": math.sin(a) * sp - 40, "t": 0.0,
                      "life": r.uniform(2.5, 3.8), "c": r.choice(WING), "s": r.uniform(1.6, 2.4)})

  def update(self, dt):
    keep = []
    for f in self.fx:
      f["t"] += dt
      if f["t"] >= f["life"]:
        continue
      if f["k"] == "fly":                      # flutter: weave side to side
        f["vx"] += math.sin(f["t"] * 3 + f["x"] * 0.01) * 40 * dt
        f["vy"] -= 8 * dt
      elif f["k"] == "glow":
        f["vx"] += math.sin(f["t"] * 2 + f["ph"]) * 30 * dt
      f["x"] += f["vx"] * dt
      f["y"] += f["vy"] * dt
      keep.append(f)
    self.fx = keep[-160:]

  def draw(self, screen, now):
    for f in self.fx:
      fade = 1.0 - f["t"] / f["life"]
      x, y = int(f["x"]), int(f["y"])
      k = f["k"]
      if k == "fly":
        butterfly(screen, x, y, f["c"], now * 14 + x, f["s"], fade)
      elif k == "glow":
        a = int(255 * fade * (0.6 + 0.4 * math.sin(now * 8 + f["ph"])))
        g = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 240, 120, a // 4), (20, 20), 19)
        pygame.draw.circle(g, (255, 245, 150, a // 2), (20, 20), 10)
        pygame.draw.circle(g, (255, 255, 220, a), (20, 20), 5)
        screen.blit(g, (x - 20, y - 20))
      elif k == "spark":
        rad = max(1, int(7 * fade))
        pygame.draw.circle(screen, f["c"], (x, y), rad)
      elif k == "ring":
        grow = f["t"] / f["life"]
        rad = int(8 + 30 * grow)
        ring = pygame.Surface((rad * 2 + 6, rad * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*f["c"][:3], int(240 * fade)), (rad + 3, rad + 3), rad, 5)
        screen.blit(ring, (x - rad - 3, y - rad - 3))
      elif k == "star":
        star(screen, (x, y), 10 + 5 * fade, f["c"], f["rot"] + f["t"] * 3)
      elif k == "bubble":
        rad = int(f["r"])
        b = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(b, (*f["c"][:3], int(90 * fade)), (rad + 2, rad + 2), rad)
        pygame.draw.circle(b, (255, 255, 255, int(220 * fade)), (rad + 2, rad + 2), rad, 2)
        pygame.draw.circle(b, (255, 255, 255, int(230 * fade)), (rad - 1, rad - 1), max(1, rad // 4))
        screen.blit(b, (x - rad - 2, y - rad - 2))

  @property
  def busy(self):
    return bool(self.fx)


def jingle(inst, seed=None):
  """A short tune for the ♪ button: [(seconds from now, MIDI note, volume)].
  Its scale, shape and rhythm are never the same as the last jingle's."""
  rng = random.Random(seed)
  scale = dict(SCALES)[pick(rng, "j_scale", [s[0] for s in SCALES])]
  shape = pick(rng, "j_shape", ["up", "down", "wave", "mountain", "valley", "bounce"])
  beats = RHYTHMS[pick(rng, "j_rhythm", list(RHYTHMS))]
  root = rng.choice([60, 62, 64, 65, 67])
  n = rng.choice([6, 7, 8, 9])
  out, t = [], 0.0
  for j in range(n):
    f = j / (n - 1)
    v = {"up": f, "down": 1 - f, "wave": 0.5 + 0.5 * math.sin(j * 1.1),
         "mountain": 1 - abs(2 * f - 1), "valley": abs(2 * f - 1),
         "bounce": (j % 2) * 0.6 + f * 0.4}[shape]
    d = int(round(v * (len(scale) + 2)))
    midi = root + scale[d % len(scale)] + 12 * (d // len(scale))
    if j == n - 1:
      midi = root + 12                     # always lands home
    out.append((t, midi, 1.0 if j % len(beats) == 0 else 0.7))
    t += 0.17 * beats[j % len(beats)]
  return out


def butterfly(screen, x, y, colour, flap, size=1.0, fade=1.0):
  """Two pairs of wings that open and close, and a little body."""
  open_ = abs(math.sin(flap))
  w = max(2, int(9 * size * (0.35 + 0.65 * open_)))
  h = int(8 * size)
  s = pygame.Surface((4 * w + 6, 3 * h + 6), pygame.SRCALPHA)
  cx, cy = s.get_width() // 2, s.get_height() // 2
  col = (*colour[:3], int(235 * fade))
  dark = (*[int(c * 0.6) for c in colour[:3]], int(235 * fade))
  for side in (-1, 1):
    pygame.draw.ellipse(s, col, (cx + (0 if side > 0 else -2 * w), cy - h - 2, 2 * w, h + 2))
    pygame.draw.ellipse(s, dark, (cx + (0 if side > 0 else -int(1.5 * w)), cy, int(1.5 * w), h))
  pygame.draw.line(s, (60, 40, 30, int(255 * fade)), (cx, cy - h), (cx, cy + h), 2)
  screen.blit(s, (x - cx, y - cy))


def star(screen, c, r, colour, rot=0.0):
  pts = []
  for k in range(10):
    rad = r if k % 2 == 0 else r * 0.45
    a = rot + k * math.pi / 5
    pts.append((c[0] + rad * math.cos(a), c[1] + rad * math.sin(a)))
  pygame.draw.polygon(screen, colour, pts)
