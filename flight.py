"""Flights across Wonder Town: tap a house and the hero flies there - never the same way twice.

Every flight is made of
  - a cruise in the style of something that travels through the air: a thrown stone's
    arc, a penguin's hops, a butterfly's flutter, an eagle circling up a warm wind and
    gliding down, a swallow's dives, a hummingbird's darts and hovers, a paper plane's
    loop, a bee's figure-eights or a dragonfly's zigzags (never the previous style);
  - one round around the house, however near it is;
  - a helicopter landing: hover above the door, rotor spinning, and down gently.
Colourful dominoes stand along the whole path just behind the hero, and a toppling wave
chases the hero along it; the last domino falls at the hero's feet just after touch-down,
and then the house opens. Every flight has its own colours and its own music (instrument,
scale, melody), never the same as the flight before. A tap skips to the landing.
"""

import bisect
import math
import random

import pygame

import magic

SPACING = 3.0            # m between dominoes along the path
DOM_H, DOM_W = 4.0, 2.0  # a domino's height and width (real 1:2 shape)
MAX_DOMINOES = 200
FALL_SECS = 0.38         # one domino's fall
FALL_ANGLE = 1.2         # rad: how far it leans onto the next one
NOTES_PER_SECOND = 7
FADE_SECS = 1.4          # after the house opens, the trail shrinks away
LIGHT = (0.45, 0.80, -0.40)

STYLES = {               # name -> (toast text, wing flaps per second)
    "stone": ("like a thrown stone", 0.0),
    "penguin": ("hopping like a penguin", 3.0),
    "butterfly": ("like a butterfly", 5.0),
    "eagle": ("like an eagle", 1.2),
    "swallow": ("like a swallow", 3.5),
    "hummingbird": ("like a hummingbird", 14.0),
    "paper plane": ("like a paper plane", 0.0),
    "bee": ("like a bee", 12.0),
    "dragonfly": ("like a dragonfly", 9.0),
}


def _hsv(h, s=85, v=100):
  c = pygame.Color(0)
  c.hsva = (int(h) % 360, s, v, 100)
  return (c.r, c.g, c.b)


PALETTES = {             # name -> colour of the domino at share f of the path
    "rainbow": lambda f, i: _hsv(360 * f),
    "sunset": lambda f, i: _hsv(330 + 80 * f, 80 + 15 * (i % 2)),
    "ocean": lambda f, i: _hsv(165 + 75 * f + 15 * (i % 2), 75),
    "peacock": lambda f, i: [(0, 150, 160), (40, 90, 200), (120, 200, 60), (90, 50, 160)][i % 4],
    "tricolour": lambda f, i: [(255, 153, 51), (250, 250, 250), (19, 136, 8), (0, 0, 128)][i % 4],
    "candy": lambda f, i: [(255, 120, 180), (120, 230, 190), (255, 230, 90), (190, 150, 255)][i % 4],
    "fire": lambda f, i: _hsv(50 * f + 10 * (i % 3), 90),
    "forest": lambda f, i: _hsv(70 + 70 * f + 20 * (i % 2), 75, 85 + 15 * (i % 2)),
    "galaxy": lambda f, i: _hsv(220 + 110 * f, 70 + 25 * (i % 2)),
}
_LAST = {}


def _pick(rng, key, options):
  """A random choice that is never the previous flight's choice."""
  fresh = [o for o in options if o != _LAST.get(key)] or list(options)
  _LAST[key] = choice = rng.choice(fresh)
  return choice


def _ease(k):
  k = max(0.0, min(1.0, k))
  return k * k * (3 - 2 * k)


def _tri(x):
  """A zigzag wave between -1 and 1."""
  x = x % 1.0
  return 4 * x - 1 if x < 0.5 else 3 - 4 * x


def _norm(v):
  n = math.sqrt(sum(c * c for c in v)) or 1.0
  return tuple(c / n for c in v)


def _cross(a, b):
  return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Domino:
  __slots__ = ("pos", "tan", "up", "side", "col", "laid", "fall", "rang")

  def __init__(self, pos, tan, col):
    self.pos, self.col = pos, col
    self.tan = tan
    up = (0.0, 1.0, 0.0)
    d = sum(a * b for a, b in zip(up, tan))          # the part of "up" across the path
    up = tuple(u - d * t for u, t in zip(up, tan))
    if math.sqrt(sum(c * c for c in up)) < 0.2:      # the path goes straight up or down
      up = (math.sin(0.3), 0.0, math.cos(0.3))
    self.up = _norm(up)
    self.side = _norm(_cross(self.up, tan))
    self.laid = self.fall = 0.0
    self.rang = False


class Flight:

  def __init__(self, start, box, boxes, yaw=0.0, seed=None, instruments=()):
    rng = random.Random(seed)
    self.rng = rng
    self.box = box
    self.style = _pick(rng, "style", list(STYLES))
    self.label, self.flap_rate = STYLES[self.style]
    self.palette = _pick(rng, "palette", list(PALETTES))
    ready = [i for i in instruments if i != _LAST.get("inst")]
    self.inst = rng.choice(ready) if ready else (rng.choice(list(instruments)) if instruments else None)
    _LAST["inst"] = self.inst
    self.scale = dict(magic.SCALES)[_pick(rng, "scale", [s[0] for s in magic.SCALES])]
    self.contour = _pick(rng, "contour", magic.CONTOURS)
    self.root = rng.choice([60, 62, 63, 65, 67])
    self.ph = rng.uniform(0, math.tau)
    self.t = 0.0
    self.flap = 0.0
    self.finished = False          # the last domino has fallen
    self.fade = 0.0
    self.next_note = 0.0
    self.pts, self.ts = [], []
    self._build(start, box, boxes, yaw)
    self._lay_dominoes()
    self.pos = self.pts[0]
    self.yaw = yaw

  # ------------------------------------------------------------------ the path
  def _offsets(self, u, d, q):
    """(forward, side, up) metres away from the straight line at share u of the cruise,
    and the speed there (1 = the flight's usual speed)."""
    s = self.style
    tau = math.tau
    if s == "stone":                       # one high arc, even speed across the ground
      return 0.0, 0.0, 4 * q["h"] * u * (1 - u), 1.0
    if s == "penguin":                     # hop, hop, hop
      hop = abs(math.sin(math.pi * q["n"] * u))
      return 0.0, 0.8 * math.sin(tau * q["n"] * u), q["hh"] * hop, 0.65 + 0.6 * hop
    if s == "butterfly":                   # flutter up and down, drift side to side
      up = 3.0 * math.sin(tau * q["n"] * u + q["p"]) + 1.4 * math.sin(tau * 2.7 * q["n"] * u)
      side = q["a"] * math.sin(tau * q["m"] * u + q["p2"]) + 1.3 * math.sin(tau * 6.3 * u)
      return 0.0, side, 3.0 + up, 0.6 + 0.5 * math.sin(tau * 3.0 * u + q["p"]) ** 2
    if s == "eagle":                       # circle up a warm wind, then one long glide
      c = 0.4
      if u < c:
        a = tau * q["turns"] * u / c
        fwd = d * (0.06 * u / c - u) + q["r"] * math.sin(a)
        return fwd, q["dir"] * q["r"] * (1 - math.cos(a)), q["h"] * u / c, 0.7
      g = (u - c) / (1 - c)
      return d * (0.06 + 0.94 * g - u), 0.0, q["h"] * (1 - _ease(g)), 1.35
    if s == "swallow":                     # deep dives and climbs
      wave = 0.5 + 0.5 * math.cos(tau * q["n"] * u)
      return 0.0, q["a"] * math.sin(tau * 1.2 * u), q["h"] * wave, 0.75 + 0.6 * (1 - wave)
    if s == "hummingbird":                 # dart ... stop and hover ... dart
      dart = abs(math.sin(math.pi * q["n"] * u))
      return 0.0, 2.5 * math.sin(math.pi * q["n"] * u * 0.5), 3.0 + 1.5 * math.sin(tau * 2 * q["n"] * u), \
          0.12 + 0.9 * dart ** 0.7
    if s == "paper plane":                 # a straight glide with a loop-the-loop
      lo, hi = q["c"] - 0.12, q["c"] + 0.12
      if lo <= u <= hi:
        a = tau * (u - lo) / (hi - lo)
        fwd = d * 0.24 * (a / tau) - d * (u - lo) + q["r"] * math.sin(a)
        return fwd, 0.0, 4.0 + q["r"] * (1 - math.cos(a)), 0.8
      return 0.0, 0.0, 4.0, 1.1
    if s == "bee":                         # little figure-eights
      return 0.0, 3.2 * math.sin(tau * q["n"] * u), 4.0 + 1.8 * math.sin(2 * tau * q["n"] * u), 1.0
    # dragonfly: sharp zigzags with a tiny stop at every corner
    z = _tri(q["n"] * u)
    return 0.0, 6.0 * z, 4.0 + 2.5 * _tri(q["n"] * u * 0.5 + 0.25), 0.25 + 0.95 * (1 - abs(z)) ** 0.5

  def _params(self, d):
    r = self.rng
    return {
        "h": min(38.0, max(14.0, 0.3 * d)) * r.uniform(0.85, 1.15) if self.style == "stone" else
        (r.uniform(16, 24) if self.style == "eagle" else r.uniform(6, 10)),
        "n": max(2, min(9, int(d / r.uniform(16, 24)) + 1)) if self.style in ("penguin", "hummingbird")
        else r.choice([2, 3, 4]) if self.style in ("swallow", "dragonfly") else r.choice([4, 5, 6, 7]),
        "hh": r.uniform(3.5, 5.5), "a": r.uniform(3.5, 6.0), "m": r.choice([1.5, 2.0, 2.5]),
        "p": r.uniform(0, math.tau), "p2": r.uniform(0, math.tau),
        "turns": r.choice([1.0, 1.5]), "r": r.uniform(7.0, 11.0), "dir": r.choice([-1, 1]),
        "c": r.uniform(0.4, 0.6),
    }

  def _build(self, start, box, boxes, yaw):
    ax, ay, az = start
    cx, _, cz = box.centre
    door = box.door()
    radius = max(12.0, math.hypot(box.x1 - box.x0, box.z1 - box.z0) / 2 + 7.0)
    hc = box.top + 7.0                                   # height of the round over the house
    th0 = math.atan2(az - cz, ax - cx) if math.hypot(ax - cx, az - cz) > 0.5 else -yaw
    ex, ez = cx + radius * math.cos(th0), cz + radius * math.sin(th0)
    d = math.hypot(ex - ax, ez - az)
    if d > 1.0:
      fx, fz = (ex - ax) / d, (ez - az) / d
    else:
      fx, fz = math.sin(yaw), math.cos(yaw)
    sx, sz = fz, -fx
    q = self._params(max(d, 30.0))
    pts, speeds = [], []
    n = max(160, int(d * 2.5))
    for i in range(n + 1):                               # 1. the cruise in this flight's style
      u = i / n
      fwd, side, up, sp = self._offsets(u, max(d, 30.0), q)
      env = _ease(u / 0.08) * _ease((1 - u) / 0.12)
      side *= env
      up *= _ease((1 - u) / 0.12) * (1.0 if self.style in ("stone", "penguin") else _ease(u / 0.06))
      base_y = ay + (hc - ay) * (1 - (1 - u) ** 2) + 6.0 * math.sin(math.pi * u)
      along = d * u + fwd * env
      pts.append((ax + fx * along + sx * side, base_y + up, az + fz * along + sz * side))
      speeds.append(sp)
    cruise_end = len(pts)
    turn = self.rng.choice([-1, 1])                     # 2. one round around the house
    thd = math.atan2(door[2] - cz, door[0] - cx)
    sweep = math.tau + ((thd - th0) * turn) % math.tau
    m = 140
    for i in range(1, m + 1):
      v = i / m
      a = th0 + turn * sweep * v
      pts.append((cx + radius * math.cos(a), hc + 2.0 * math.sin(math.tau * v), cz + radius * math.sin(a)))
    circle_end = len(pts)
    last = pts[-1]                                       # 3. in over the door
    for i in range(1, 21):
      v = _ease(i / 20)
      pts.append((last[0] + (door[0] - last[0]) * v, hc, last[2] + (door[2] - last[2]) * v))
    self.hover_at = len(pts) - 1
    self._clear_roofs(pts, boxes, box, cruise_end)
    # times: the cruise by its style's speed, then the round, the glide in, hover and landing
    cruise_secs = max(3.5, min(6.0, d / 18.0))
    raw = [0.0]
    for i in range(1, cruise_end):
      raw.append(raw[-1] + math.dist(pts[i], pts[i - 1]) / max(0.05, speeds[i]))
    k = cruise_secs / max(1e-6, raw[-1])
    ts = [r * k for r in raw]
    round_secs = max(3.0, min(4.0, math.tau * radius / 16.0))
    for i in range(cruise_end, circle_end):
      ts.append(ts[-1] + round_secs / (circle_end - cruise_end))
    for i in range(circle_end, len(pts)):
      ts.append(ts[-1] + 0.9 / (len(pts) - circle_end))
    hx, hy, hz = pts[-1]
    pts.append((hx, hy, hz))                             # 4. hover ...
    ts.append(ts[-1] + 0.6)
    steps = 40                                           # 5. ... and down like a helicopter
    for i in range(1, steps + 1):
      v = i / steps
      pts.append((hx, hy * (1 - _ease(v)), hz))
      ts.append(ts[-1] + 1.8 / steps)
    self.pts, self.ts = pts, ts
    self.land_at = ts[-1]
    self.hover_t = ts[self.hover_at]

  @staticmethod
  def _clear_roofs(pts, boxes, target, cruise_end):
    """Keeps the path a few metres above every roof it crosses (smoothly)."""
    need = []
    for x, y, z in pts:
      roof = 0.0
      for b in boxes:
        if b is not target and b.contains_xz(x, z, pad=2.5):
          roof = max(roof, b.top)
      need.append(roof + 3.0 if roof > 0 else -1e9)
    lift = [max(0.0, n - p[1]) for n, p in zip(need, pts)]
    for _ in range(3):                                   # spread each lift to its neighbours
      lift = [max(lift[i], 0.85 * max(lift[max(0, i - 6):i + 7])) for i in range(len(lift))]
    for i in range(len(pts)):
      x, y, z = pts[i]
      pts[i] = (x, max(y + lift[i], need[i]), z)

  def _lay_dominoes(self):
    pts, ts = self.pts[:self.hover_at + 1], self.ts
    arc = [0.0]
    for i in range(1, len(pts)):
      arc.append(arc[-1] + math.dist(pts[i], pts[i - 1]))
    total = arc[-1]
    gap = max(SPACING, total / MAX_DOMINOES)
    self.size = max(1.0, gap / SPACING)                # longer paths: bigger dominoes, further apart
    n = max(2, int(total / gap))
    out = []
    j = 0
    for k in range(n):
      s = 1.0 + k * (total - 1.0) / max(1, n - 1)
      while j < len(arc) - 2 and arc[j + 1] < s:
        j += 1
      seg = max(1e-6, arc[j + 1] - arc[j])
      f = (s - arc[j]) / seg
      a, b = pts[j], pts[j + 1]
      p = tuple(a[c] + (b[c] - a[c]) * f for c in range(3))
      dm = Domino(p, _norm(tuple(b[c] - a[c] for c in range(3))),
                  PALETTES[self.palette](k / max(1, n - 1), k))
      dm.laid = ts[j] + (ts[j + 1] - ts[j]) * f + 0.2
      out.append(dm)
    # the toppling wave chases the hero and reaches the last domino just after touch-down
    lag0, end = 1.2, self.land_at + 0.35
    extra = end - (out[-1].laid + lag0)
    for k, dm in enumerate(out):
      dm.fall = dm.laid + lag0 + extra * (k / (n - 1))
    self.dominoes = out
    self.done_at = out[-1].fall + FALL_SECS
    span = max(0.5, out[-1].fall - out[0].fall)
    self.step = max(1, round(n / (span * NOTES_PER_SECOND)))

  # ------------------------------------------------------------------ running
  @property
  def rotor(self):
    """0..1: how much the helicopter rotor shows (hover and landing)."""
    if self.t >= self.land_at + 0.6:
      return 0.0
    return max(0.0, min(1.0, (self.t - self.hover_t + 0.5) / 0.5))

  @property
  def landed(self):
    return self.t >= self.land_at

  def skip(self):
    self.t = max(self.t, self.done_at)

  def at(self, t):
    i = bisect.bisect_right(self.ts, t) - 1
    if i < 0:
      return self.pts[0], 0
    if i >= len(self.ts) - 1:
      return self.pts[-1], len(self.pts) - 1
    k = (t - self.ts[i]) / max(1e-9, self.ts[i + 1] - self.ts[i])
    a, b = self.pts[i], self.pts[i + 1]
    return tuple(a[c] + (b[c] - a[c]) * k for c in range(3)), i

  def note(self, k):
    j, m = k // self.step, max(1, (len(self.dominoes) - 1) // self.step)
    span = len(self.scale) * 2
    f = j / m
    shape = {"up": f, "down": 1 - f, "wave": 0.5 + 0.5 * math.sin(j * 0.6),
             "zigzag": (j % 4) / 3, "mountain": 1 - abs(2 * f - 1), "valley": abs(2 * f - 1),
             "ocean": 0.5 + 0.35 * math.sin(j * 0.5 + self.ph) + 0.15 * math.sin(j * 1.7)}[self.contour]
    d = int(round(max(0.0, min(1.0, shape)) * (span - 1)))
    return self.root + self.scale[d % len(self.scale)] + 12 * (d // len(self.scale))

  def update(self, dt, sfx=None):
    """Moves the flight on; returns "landed" at touch-down and "done" once the last
    domino has fallen."""
    event = None
    if self.finished:
      self.fade += dt
      return None
    was_landed = self.landed
    self.t += dt
    self.flap += dt * self.flap_rate * math.tau
    pos, i = self.at(self.t)
    if i < self.hover_at:
      a, b = self.pts[i], self.pts[min(len(self.pts) - 1, i + 1)]
      if abs(b[0] - a[0]) + abs(b[2] - a[2]) > 1e-4:
        want = math.atan2(b[0] - a[0], b[2] - a[2])
        self.yaw += ((want - self.yaw + math.pi) % math.tau - math.pi) * min(1.0, dt * 8)
    self.pos = pos
    if self.landed and not was_landed:
      event = "landed"
      if sfx:
        sfx.play("pop", 3)
    for k, dm in enumerate(self.dominoes):
      if dm.rang or self.t < dm.fall:
        continue
      dm.rang = True
      if sfx and k % self.step == 0 and self.t - dm.fall < 0.3:
        if self.inst:
          sfx.note(self.note(k), self.inst, 1.0 if (k // self.step) % 3 == 0 else 0.7)
        else:
          sfx.play("clack", k * 8 // len(self.dominoes))
    if self.t >= self.done_at:
      self.finished = True
      event = "done"
    return event

  @property
  def gone(self):
    return self.finished and self.fade >= FADE_SECS

  # ------------------------------------------------------------------ drawing
  def visible(self, cam_pos, far=170.0):
    """(distance, domino) for the dominoes laid so far and near enough to draw."""
    out = []
    for dm in self.dominoes:
      if self.t < dm.laid:
        break
      d = math.dist(dm.pos, cam_pos)
      if d < far:
        out.append((d, dm))
    return out

  def draw_domino(self, s, cam, dm, fog=None):
    grow = min(1.0, (self.t - dm.laid) / 0.25)
    if self.finished:
      grow *= max(0.0, 1.0 - self.fade / FADE_SECS)
    if grow <= 0.02:
      return
    k = 0.0 if self.t < dm.fall else min(1.0, (self.t - dm.fall) / FALL_SECS)
    a = FALL_ANGLE * k * k
    h, w = DOM_H * self.size * grow, DOM_W * self.size * grow / 2
    up = tuple(dm.up[c] * math.cos(a) + dm.tan[c] * math.sin(a) for c in range(3))
    p, sd = dm.pos, dm.side
    base = [tuple(p[c] + sd[c] * w * m for c in range(3)) for m in (-1, 1)]
    top = [tuple(b[c] + up[c] * h for c in range(3)) for b in base]
    got = cam.project_poly([base[0], base[1], top[1], top[0]])
    if not got:
      return
    poly, _depth = got
    normal = _cross(sd, up)
    lit = 0.72 + 0.28 * abs(sum(n * l for n, l in zip(normal, LIGHT)))
    col = tuple(min(255, int(c * lit)) for c in dm.col)
    if k > 0:                                          # falling: a little brighter
      col = tuple(min(255, int(c + (255 - c) * 0.18 * (1 - k))) for c in col)
    if fog:
      col = fog(col, _depth)
    rim = tuple(int(c * 0.45) for c in col)
    pygame.draw.polygon(s, col, poly)
    ys = [q[1] for q in poly]
    tall = max(ys) - min(ys)
    if tall >= 6:
      pygame.draw.polygon(s, rim, poly, 1 if tall < 30 else 2)
    if tall >= 16:                                     # the middle line and two pips
      white = (255, 255, 255) if sum(dm.col) < 690 else (40, 40, 60)

      def P(m, v):
        q = cam.project(tuple(p[c] + sd[c] * w * m + up[c] * h * v for c in range(3)))
        return q[:2] if q else None

      l1, l2 = P(-0.75, 0.5), P(0.75, 0.5)
      if l1 and l2:
        pygame.draw.line(s, white, l1, l2, max(1, int(tall / 24)))
      for v in (0.25, 0.75):
        c = P(0, v)
        if c:
          pygame.draw.circle(s, white, (int(c[0]), int(c[1])), max(1, int(tall / 13)))
