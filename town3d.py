"""Wonder Town: the 3D world children explore to reach every part of Domino Wonder Dash.

Pure maths, no drawing (world.py paints it):
  * the town - one colourful building for each subject (ABC School, Zoo & Garden, Food
    Market, ...), plus the Story House, Family House, Drawing Studio, Sticker Museum and
    Games Arcade, a river with a bridge and stepping posts, trees and lamp posts;
  * a perspective camera with near-plane clipping (works the same in the browser);
  * the player: walking, jumping, landing on roofs, and the rope swing - a rope to a roof
    corner or post that swings you across with real pendulum physics;
  * a fly-there ride that carries a child straight to the building they tapped.

World axes: x = east, y = up, z = north, in metres. The main street runs north along x = 0.
(The same engine as Bridge Genius's Campus World, laid out as a children's town.)
"""

import math

GRAVITY = 26.0
WALK_SPEED = 12.0
TURN_SPEED = 2.4            # rad/s
JUMP_SPEED = 11.5
SUPER_JUMP_SPEED = 21.0     # magic boots
GLIDE_FALL = 3.0            # the cape caps the falling speed (m/s)
RADIUS = 0.6                # the player's body, for collisions
ROPE_MIN, ROPE_MAX = 6.0, 40.0
RIVER_Z = (96.0, 112.0)
BRIDGE_HALF = 6.0           # the street bridge over the river is |x| < 6
BOUNDS = (-95.0, 95.0, -35.0, 245.0)      # x0, x1, z0, z1
START = (0.0, 0.0, -18.0)


class Box:
  """A solid block: a building, a post, a gate pillar. kind/payload say what entering does."""

  def __init__(self, key, x0, z0, x1, z1, h, colour, label="", sub="", kind=None,
               payload=None, roof=None, windows=True, y0=0.0, gable=False, icon=None):
    self.key = key
    self.x0, self.z0, self.x1, self.z1 = min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)
    self.y0, self.h = y0, h
    self.colour = colour
    self.roof = roof or tuple(max(0, c - 50) for c in colour)
    self.label = label
    self.sub = sub
    self.kind = kind            # None = scenery only
    self.payload = payload
    self.windows = windows
    self.gable = gable          # a pointed house roof on top
    self.icon = icon            # (category, item) whose picture goes on the sign

  @property
  def centre(self):
    return ((self.x0 + self.x1) / 2, (self.y0 + self.h) / 2, (self.z0 + self.z1) / 2)

  @property
  def top(self):
    """Height of the highest point (the ridge of a pointed roof)."""
    return self.h + (self.roof_height() if self.gable else 0.0)

  def roof_height(self):
    return min(5.0, (self.z1 - self.z0) * 0.35)

  def contains_xz(self, x, z, pad=0.0):
    return self.x0 - pad <= x <= self.x1 + pad and self.z0 - pad <= z <= self.z1 + pad

  def distance_xz(self, x, z):
    dx = max(self.x0 - x, 0.0, x - self.x1)
    dz = max(self.z0 - z, 0.0, z - self.z1)
    return math.hypot(dx, dz)

  def door(self):
    """The ground point in front of the building, on the street side."""
    cx, _, cz = self.centre
    if self.x1 < -BRIDGE_HALF:
      return (self.x1 + 3.0, 0.0, cz)
    if self.x0 > BRIDGE_HALF:
      return (self.x0 - 3.0, 0.0, cz)
    return (cx, 0.0, self.z0 - 3.0)

  def anchors(self):
    """Rope anchor points: the roof corners (and the top of thin posts)."""
    y = self.h
    if (self.x1 - self.x0) < 5 and (self.z1 - self.z0) < 5:
      return [((self.x0 + self.x1) / 2, y, (self.z0 + self.z1) / 2)]
    return [(self.x0, y, self.z0), (self.x1, y, self.z0), (self.x0, y, self.z1), (self.x1, y, self.z1)]


# One building per subject. key, side (-1 west / +1 east), z, width, depth, height, colour,
# label, little sign text, subject name in domino_data, sign picture (category, item)
SUBJECT_HOUSES = [
    ("english", -1, 40, 18, 14, 11, (250, 196, 70), "ABC School", "English letters", "English", ("ABC", "A")),
    ("hindi", 1, 40, 18, 14, 11, (246, 140, 72), "Hindi Pathshala", "Swar and Vyanjan", "Hindi", None),
    ("maths", -1, 70, 18, 14, 13, (90, 150, 240), "Number House", "Numbers, shapes, signs", "Maths", None),
    ("home", 1, 70, 18, 14, 10, (240, 170, 150), "My Home", "Body, home, helpers", "Me & Home", None),
    ("nature", -1, 136, 24, 18, 9, (90, 190, 110), "Zoo & Garden", "Animals, birds, plants", "Nature", ("Animals", "Tiger")),
    ("food", 1, 136, 20, 16, 9, (236, 90, 90), "Food Market", "Fruits and vegetables", "Food", ("Fruits", "Apple")),
    ("travel", -1, 168, 22, 16, 12, (160, 110, 220), "Station", "Vehicles, travel, bridges", "Travel", None),
    ("world", 1, 168, 16, 16, 24, (60, 190, 200), "Globe Tower", "Sky, countries, cities", "World", None),
    ("india", -1, 200, 22, 16, 12, (255, 153, 51), "India Park", "Map, states, monuments", "India", None),
    ("fun", 1, 200, 20, 16, 12, (220, 90, 190), "Fun Park", "Cartoons, music, sports", "Fun", None),
]

# Houses for everything else. key, side, z, w, d, h, colour, label, sign text, what entering does
EXTRA_HOUSES = [
    ("story", -1, 12, 14, 12, 9, (255, 150, 190), "Story House", "Story of the day", "story"),
    ("family", 1, 12, 14, 12, 9, (150, 200, 120), "Family House", "Players", "players"),
    ("studio", -1, 228, 16, 12, 10, (120, 200, 255), "Drawing Studio", "Draw my own", "draw"),
    ("museum", 1, 228, 16, 12, 10, (255, 215, 80), "Sticker Museum", "Your stickers", "stickers"),
]


def build_world():
  """Every solid thing in the town."""
  boxes = []
  for key, side, z, w, d, h, col, label, sub, subject, icon in SUBJECT_HOUSES:
    x0 = side * 9.0
    boxes.append(Box(key, x0, z - d / 2, x0 + side * w, z + d / 2, h, col, label, sub,
                     kind="subject", payload=subject, gable=h <= 13, icon=icon))
  for key, side, z, w, d, h, col, label, sub, kind in EXTRA_HOUSES:
    x0 = side * 9.0
    boxes.append(Box(key, x0, z - d / 2, x0 + side * w, z + d / 2, h, col, label, sub,
                     kind=kind, gable=True))
  # the Games Arcade closes the end of the street
  boxes.append(Box("arcade", -7, 236, 7, 244, 20, (255, 120, 60), "Games Arcade", "Find it, Spell it, more",
                   kind="games", roof=(250, 220, 60)))
  # stepping posts standing in the river, so you can swing across
  for x in (-45, -24, 24, 45):
    boxes.append(Box(f"post{x}", x - 1.1, 102.9, x + 1.1, 105.1, 18, (250, 200, 80),
                     windows=False, roof=(240, 110, 60)))
  # the town gate
  boxes.append(Box("gate_w", -8.5, -6, -6.5, -4, 10, (230, 90, 120), windows=False))
  boxes.append(Box("gate_e", 6.5, -6, 8.5, -4, 10, (230, 90, 120), windows=False))
  boxes.append(Box("gate_top", -8.5, -6, 8.5, -4, 12.5, (90, 170, 240), windows=False, y0=10))
  # bridge railings
  for side in (-1, 1):
    boxes.append(Box(f"rail{side}", side * 5.6, RIVER_Z[0] - 2, side * 6.2, RIVER_Z[1] + 2, 1.1,
                     (255, 255, 255), windows=False))
  return boxes


def trees_and_lamps():
  trees, lamps = [], []
  for z in range(-30, 236, 16):
    if RIVER_Z[0] - 6 < z < RIVER_Z[1] + 6:
      continue
    lamps.append((-7.5, z))
    lamps.append((7.5, z + 8))
  for i in range(60):            # a fixed pseudo-random scatter (same every run)
    x = ((i * 73) % 180) - 90
    z = ((i * 131) % 270) - 30
    if abs(x) < 36 and z > -10:
      continue                    # keep the street and building rows clear
    if RIVER_Z[0] - 4 < z < RIVER_Z[1] + 4:
      continue
    trees.append((x + 0.5, z + 0.5, 5.0 + (i % 4) * 1.5))
  return trees, lamps


def in_river(x, z):
  return RIVER_Z[0] < z < RIVER_Z[1] and abs(x) > BRIDGE_HALF


# --------------------------------------------------------------------------------------
# Camera
# --------------------------------------------------------------------------------------
class Camera:
  """A chase camera behind the player. Fixed pitch keeps the horizon steady."""

  FOV = math.radians(60)
  NEAR = 0.6

  def __init__(self, width, height):
    self.pitch = -0.17
    self.dist = 14.0
    self.yaw = 0.0
    self.pos = (0.0, 6.0, -15.0)
    self.resize(width, height)

  def resize(self, width, height):
    self.w, self.h = width, height
    self.cx, self.cy = width / 2, height * 0.5
    # tall phone screens: keep the same sideways view, so the town is not squeezed
    self.focal = (min(width * 0.75, height) / 2) / math.tan(self.FOV / 2)
    self._axes()

  def _axes(self):
    cp, sp = math.cos(self.pitch), math.sin(self.pitch)
    sy, cy = math.sin(self.yaw), math.cos(self.yaw)
    self.f = (sy * cp, sp, cy * cp)
    self.r = (cy, 0.0, -sy)
    self.u = (-sy * sp, cp, -cy * sp)

  def follow(self, target, yaw, dt=None):
    """Sit behind and above the target, looking the way it faces (eased with dt)."""
    if dt is None:
      self.yaw = yaw
    else:
      d = (yaw - self.yaw + math.pi) % (2 * math.pi) - math.pi
      self.yaw += d * min(1.0, dt * 5.0)
    self._axes()
    tx, ty, tz = target[0], target[1] + 2.0, target[2]
    want = (tx - self.f[0] * self.dist, max(1.5, ty - self.f[1] * self.dist + 2.0),
            tz - self.f[2] * self.dist)
    if dt is None:
      self.pos = want
    else:
      k = min(1.0, dt * 8.0)
      self.pos = tuple(self.pos[i] + (want[i] - self.pos[i]) * k for i in range(3))

  def to_cam(self, p):
    d = (p[0] - self.pos[0], p[1] - self.pos[1], p[2] - self.pos[2])
    return (d[0] * self.r[0] + d[2] * self.r[2],
            d[0] * self.u[0] + d[1] * self.u[1] + d[2] * self.u[2],
            d[0] * self.f[0] + d[1] * self.f[1] + d[2] * self.f[2])

  def screen(self, c):
    return (self.cx + self.focal * c[0] / c[2], self.cy - self.focal * c[1] / c[2])

  def project(self, p):
    """(x, y, depth) on screen, or None when behind the camera."""
    c = self.to_cam(p)
    if c[2] < self.NEAR:
      return None
    x, y = self.screen(c)
    return (x, y, c[2])

  def project_poly(self, pts):
    """Project a flat polygon, clipping it at the near plane so walls right next to the
    camera do not vanish. Returns (screen points, mean depth) or None."""
    cam = [self.to_cam(p) for p in pts]
    if all(c[2] >= self.NEAR for c in cam):
      clipped = cam
    else:
      clipped = []
      n = len(cam)
      for i in range(n):
        a, b = cam[i], cam[(i + 1) % n]
        ain, bin_ = a[2] >= self.NEAR, b[2] >= self.NEAR
        if ain:
          clipped.append(a)
        if ain != bin_:
          t = (self.NEAR - a[2]) / (b[2] - a[2])
          clipped.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
      if len(clipped) < 3:
        return None
    depth = sum(c[2] for c in clipped) / len(clipped)
    return [self.screen(c) for c in clipped], depth

  def horizon_y(self):
    """Screen y of the horizon (looking down puts it above the middle)."""
    return self.cy + self.focal * math.tan(self.pitch)


# --------------------------------------------------------------------------------------
# Player
# --------------------------------------------------------------------------------------
class Player:

  def __init__(self, pos=START, yaw=0.0):
    self.pos = list(pos)
    self.vel = [0.0, 0.0, 0.0]
    self.yaw = yaw              # 0 = facing north (+z)
    self.grounded = True
    self.rope = None            # [anchor (x,y,z), length, longest safe length]
    self.zip = None             # [start, end, t, duration]
    self.splash = 0.0           # >0 just after falling in the river
    self.gliding = False        # the magic cape is open
    self.walk_phase = 0.0

  @property
  def heading(self):
    return (math.sin(self.yaw), 0.0, math.cos(self.yaw))

  # --- swinging -------------------------------------------------------------------
  def best_anchor(self, boxes):
    """The best rope anchor: ahead of you, above you, within reach."""
    hx, _, hz = self.heading
    px, py, pz = self.pos
    best, best_score = None, -1e9
    for b in boxes:
      for a in b.anchors():
        dx, dy, dz = a[0] - px, a[1] - py, a[2] - pz
        if dy < 3.0:
          continue
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if not ROPE_MIN <= dist <= ROPE_MAX:
          continue
        flat = math.hypot(dx, dz) or 1.0
        ahead = (dx * hx + dz * hz) / flat
        if ahead < 0.25:
          continue
        score = ahead * 30 - abs(dist - 20) + min(dy, 20) * 0.4
        if score > best_score:
          best, best_score = a, score
    return best

  def attach(self, boxes):
    a = self.best_anchor(boxes)
    if a is None:
      return False
    d = math.dist(a, self.pos)
    self.rope = [a, max(ROPE_MIN, d * 0.96), a[1] - 2.5]
    self.grounded = False
    if self.vel[1] < 0:
      self.vel[1] *= 0.5
    return True

  def release(self):
    if self.rope is None:
      return
    self.rope = None
    self.vel[0] *= 1.12
    self.vel[2] *= 1.12
    self.vel[1] = max(self.vel[1], 0.0) + 5.0       # a little hop as you let go

  def zip_to(self, point, duration=None):
    start = tuple(self.pos)
    d = math.dist(start, point)
    self.rope = None
    self.zip = [start, tuple(point), 0.0, duration or max(0.8, min(2.4, d / 40.0))]
    dx, dz = point[0] - start[0], point[2] - start[2]
    if abs(dx) + abs(dz) > 0.1:
      self.yaw = math.atan2(dx, dz)

  def jump(self):
    if self.grounded:
      self.vel[1] = JUMP_SPEED
      self.grounded = False
      return True
    return False

  # --- magic tools (like a web-slinging superhero) ----------------------------------
  def super_jump(self):
    """Magic boots: a jump about three times as high."""
    if self.grounded or self.rope is not None:
      self.rope = None
      self.vel[1] = SUPER_JUMP_SPEED
      hx, _, hz = self.heading
      self.vel[0] += hx * 4.0
      self.vel[2] += hz * 4.0
      self.grounded = False
      return True
    return False

  def web_pull_target(self, boxes):
    """Where the web-zip lands you: just inside the roof edge of the best building ahead."""
    a = self.best_anchor(boxes)
    if a is None:
      return None
    for b in boxes:
      if a in b.anchors():
        cx, _, cz = b.centre
        x = a[0] + max(-1.2, min(1.2, cx - a[0]))
        z = a[2] + max(-1.2, min(1.2, cz - a[2]))
        return (a, (x, b.h, z))
    return None

  def web_pull(self, boxes):
    """Magic web-zip: shoot a web at a roof and get pulled up onto it."""
    hit = self.web_pull_target(boxes)
    if hit is None:
      return None
    anchor, landing = hit
    self.zip_to(landing, duration=max(0.5, min(1.4, math.dist(self.pos, landing) / 30.0)))
    self.zip.append(anchor)            # remembered so the web line can be drawn
    return anchor

  def glide(self, on):
    """Magic cape: falling slowly and drifting forward while it is open."""
    self.gliding = bool(on) and not self.grounded and self.rope is None and self.zip is None

  # --- stepping -------------------------------------------------------------------
  def update(self, dt, boxes, forward=0.0, turn=0.0):
    """forward/turn in -1..1. Returns an event string or None."""
    self.splash = max(0.0, self.splash - dt)
    if self.zip is not None:
      start, end, t, dur = self.zip[:4]
      t = min(1.0, t + dt / dur)
      self.zip[2] = t
      k = t * t * (3 - 2 * t)
      arc = 0.0 if len(self.zip) > 4 else 9.0 * 4 * t * (1 - t)   # a web pulls straight
      self.pos = [start[i] + (end[i] - start[i]) * k for i in range(3)]
      self.pos[1] += arc
      if t >= 1.0:
        self.zip = None
        self.vel = [0.0, 0.0, 0.0]
        self.grounded = True
        return "arrived"
      return None
    self.yaw = (self.yaw + turn * TURN_SPEED * dt + math.pi) % (2 * math.pi) - math.pi
    hx, _, hz = self.heading
    event = None
    steps = max(1, int(dt / (1 / 120)) + 1)
    h = dt / steps
    for _ in range(steps):
      if self.rope is not None:
        self.vel[0] += hx * forward * 9.0 * h          # pump the swing
        self.vel[2] += hz * forward * 9.0 * h
        self.rope[1] = max(ROPE_MIN, self.rope[1] - 2.5 * h * max(forward, 0))
        if self.rope[1] > self.rope[2]:
          # reel in, so the bottom of the swing clears the ground
          self.rope[1] = max(self.rope[2], self.rope[1] - 22.0 * h)
      elif self.grounded:
        want = (hx * forward * WALK_SPEED, hz * forward * WALK_SPEED)
        k = min(1.0, h * 12.0)
        self.vel[0] += (want[0] - self.vel[0]) * k
        self.vel[2] += (want[1] - self.vel[2]) * k
      else:
        self.vel[0] += hx * forward * 6.0 * h          # a little air control
        self.vel[2] += hz * forward * 6.0 * h
      self.vel[1] -= GRAVITY * h
      if self.gliding:
        if self.vel[1] < -GLIDE_FALL:
          self.vel[1] = -GLIDE_FALL
        self.vel[0] += hx * 5.0 * h                   # the cape carries you forward
        self.vel[2] += hz * 5.0 * h
      old_y = self.pos[1]
      for i in range(3):
        self.pos[i] += self.vel[i] * h
      if self.rope is not None:
        a, L = self.rope[0], self.rope[1]
        d = [self.pos[i] - a[i] for i in range(3)]
        n = math.sqrt(sum(c * c for c in d)) or 1.0
        if n > L:
          u = [c / n for c in d]
          self.pos = [a[i] + u[i] * L for i in range(3)]
          radial = sum(self.vel[i] * u[i] for i in range(3))
          if radial > 0:
            self.vel = [self.vel[i] - radial * u[i] for i in range(3)]
      event = self._collide(boxes, old_y) or event
    speed = math.hypot(self.vel[0], self.vel[2])
    self.walk_phase += speed * dt * 0.9
    return event

  def _collide(self, boxes, old_y):
    event = None
    floor = 0.0
    px, pz = self.pos[0], self.pos[2]
    for b in boxes:
      if not b.contains_xz(px, pz, RADIUS):
        continue
      if b.y0 > 0.5 and self.pos[1] + 1.7 < b.y0:
        continue                    # walking under the gate's top beam
      if old_y >= b.h - 0.05 and self.pos[1] <= b.h + 0.01:
        floor = max(floor, b.h)     # landing on the roof
        continue
      if self.pos[1] >= b.h:
        continue
      # inside a wall: push out the shortest way
      pushes = [(px - (b.x0 - RADIUS), 0, -1), ((b.x1 + RADIUS) - px, 0, 1),
                (pz - (b.z0 - RADIUS), 2, -1), ((b.z1 + RADIUS) - pz, 2, 1)]
      depth, axis, sign = min(pushes)
      self.pos[axis] += sign * depth
      if self.vel[axis] * sign < 0:
        self.vel[axis] = 0.0
      px, pz = self.pos[0], self.pos[2]
    if self.pos[1] <= floor:
      if not self.grounded and self.vel[1] < -4:
        event = "landed"
      self.pos[1] = floor
      if self.vel[1] < 0:
        self.vel[1] = 0.0
      self.gliding = False
      # on a rope you are only touching down: the reel lifts you off again
      self.grounded = self.rope is None
    else:
      self.grounded = False
    x0, x1, z0, z1 = BOUNDS
    self.pos[0] = max(x0, min(x1, self.pos[0]))
    self.pos[2] = max(z0, min(z1, self.pos[2]))
    if self.grounded and self.pos[1] < 0.5 and in_river(self.pos[0], self.pos[2]):
      # splash! back to the nearest bank
      bank = RIVER_Z[0] - 2.0 if self.pos[2] < sum(RIVER_Z) / 2 else RIVER_Z[1] + 2.0
      self.pos = [self.pos[0], 0.0, bank]
      self.vel = [0.0, 0.0, 0.0]
      self.rope = None
      self.splash = 2.5
      event = "splash"
    return event


def nearest_entrance(boxes, pos, reach=4.5):
  """The building you are standing at (on the ground beside it or on its roof), or None."""
  best, best_d = None, reach
  for b in boxes:
    if b.kind is None:
      continue
    on_roof = b.contains_xz(pos[0], pos[2], 0.5) and abs(pos[1] - b.h) < 0.6
    d = 0.0 if on_roof else b.distance_xz(pos[0], pos[2])
    if pos[1] > 1.0 and not on_roof:
      continue
    if d < best_d:
      best, best_d = b, d
  return best
