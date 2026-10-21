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
BOUNDS = (-140.0, 140.0, -45.0, 310.0)      # x0, x1, z0, z1
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
    self.kind = kind
    self.payload = payload
    self.windows = windows
    self.gable = gable
    self.icon = icon

  @property
  def centre(self):
    return ((self.x0 + self.x1) / 2, (self.y0 + self.h) / 2, (self.z0 + self.z1) / 2)

  @property
  def top(self):
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
    cx, _, cz = self.centre
    if self.x1 < -BRIDGE_HALF:
      return (self.x1 + 3.0, 0.0, cz)
    if self.x0 > BRIDGE_HALF:
      return (self.x0 - 3.0, 0.0, cz)
    return (cx, 0.0, self.z0 - 3.0)

  def anchors(self):
    y = self.h
    if (self.x1 - self.x0) < 5 and (self.z1 - self.z0) < 5:
      return [((self.x0 + self.x1) / 2, y, (self.z0 + self.z1) / 2)]
    return [(self.x0, y, self.z0), (self.x1, y, self.z0), (self.x0, y, self.z1), (self.x1, y, self.z1)]


# --- Palm Jumeirah Archipelago Layout ---
# side: -1 (West Fronds), 1 (East Fronds)
# x_reach: how far along the curved frond the pavilion is located
SUBJECT_HOUSES = [
    # --- Frond 1: CLASS 1 (Foundation Frond) ---
    ("english", -1, 38, 38.0, 22, 16, 13, (250, 196, 70), "Class 1: ABC School", "Class 1 - English & Phonics", "English", ("ABC", "A")),
    ("hindi",    1, 38, 38.0, 22, 16, 13, (246, 140, 72), "Class 1: Hindi Pathshala", "Class 1 - Swar & Vyanjan", "Hindi", None),

    # --- Frond 2: CLASS 2 (Numbers & EVS) ---
    ("maths",   -1, 78, 48.0, 22, 16, 15, (90, 150, 240), "Class 2: Number House", "Class 2 - Count, Add & Shapes", "Maths", None),
    ("home",     1, 78, 48.0, 22, 16, 12, (240, 170, 150), "Class 2: My Home & EVS", "Class 2 - Body, Family & Helpers", "Me & Home", None),
    ("rhymes",   1, 108, 36.0, 20, 14, 12, (255, 150, 60), "Class 2: Rhyme Stage", "Class 2 - Action Poems", "Rhymes", ("Classic Rhymes", "Twinkle Twinkle")),

    # --- Frond 3: CLASS 3 (Science & Social Studies) ---
    ("science", -1, 145, 56.0, 24, 16, 14, (110, 200, 230), "Class 3: Science Lab", "Class 3 - Living World & Matter", "Science", ("Lab Tools", "Microscope")),
    ("social",   1, 145, 56.0, 24, 16, 14, (200, 150, 100), "Class 3: Heritage Hall", "Class 3 - History, Land & Maps", "Social", ("Long Ago", "Clay Pot")),

    # --- Frond 4: CLASS 4 (Nature & Food Exploration) ---
    ("nature",  -1, 185, 58.0, 26, 18, 12, (90, 190, 110), "Class 4: Zoo & Nature", "Class 4 - Habitats, Birds & Plants", "Nature", ("Animals", "Tiger")),
    ("food",     1, 185, 58.0, 24, 18, 12, (236, 90, 90), "Class 4: Food Souq", "Class 4 - Crops, Diet & Health", "Food", ("Fruits", "Apple")),

    # --- Frond 5: CLASS 5 (World Travel & Languages) ---
    ("travel",  -1, 225, 52.0, 24, 18, 14, (160, 110, 220), "Class 5: Station Hub", "Class 5 - Transport, Engines & Trade", "Travel", None),
    ("bangla",   1, 225, 52.0, 22, 16, 12, (60, 170, 120), "Class 5: Bangla Pathshala", "Class 5 - Language & Grammar", "Bangla", None),

    # --- Frond 6: CLASS 6 (Safety & Global Sciences) ---
    ("safety",  -1, 265, 44.0, 22, 16, 12, (240, 70, 70), "Class 6: Safety Park", "Class 6 - Civics, Signs & Rules", "Safety", ("Road Safety", "Traffic Light")),
    ("world",    1, 265, 44.0, 20, 20, 28, (60, 190, 200), "Class 6: Globe Tower", "Class 6 - Geography & World Nations", "World", None),

    # --- Outer Crescent: CLASS 7 (Master Subject Arenas) ---
    ("india",   -1, 305, 34.0, 26, 20, 16, (255, 153, 51), "Class 7: India Pavilion", "Class 7 - States, Constitution & Heritage", "India", None),
    ("fun",      1, 305, 34.0, 24, 18, 15, (220, 90, 190), "Class 7: Carnival Park", "Class 7 - Logic, Puzzles & Sports", "Fun", None),
]

EXTRA_HOUSES = [
    # Trunk Entry Houses
    ("story",  -1, 12, 18.0, 14, 12, 9, (255, 150, 190), "Story House", "Story of the day", "story"),
    ("family",  1, 12, 18.0, 14, 12, 9, (150, 200, 120), "Family House", "Players", "players"),
    # Upper Trunk Studios
    ("studio", -1, 240, 20.0, 16, 12, 10, (120, 200, 255), "Drawing Studio", "Draw my own", "draw"),
    ("museum",  1, 240, 20.0, 16, 12, 10, (255, 215, 80), "Sticker Museum", "Your stickers", "stickers"),
]


def build_world():
  boxes = []
  for key, side, z, reach_x, w, d, h, col, label, sub, subject, icon in SUBJECT_HOUSES:
    x0 = side * reach_x
    boxes.append(Box(key, x0, z - d / 2, x0 + side * w, z + d / 2, h, col, label, sub,
                     kind="subject", payload=subject, gable=h <= 13, icon=icon))
  for key, side, z, reach_x, w, d, h, col, label, sub, kind in EXTRA_HOUSES:
    x0 = side * reach_x
    boxes.append(Box(key, x0, z - d / 2, x0 + side * w, z + d / 2, h, col, label, sub,
                     kind=kind, gable=True))
  # Grand Arcade at the apex of the Crescent
  boxes.append(Box("arcade", -14, 325, 14, 342, 24, (255, 120, 60), "Games Arcade", "Find it, Spell it, more",
                   kind="games", roof=(250, 220, 60)))

  for x in (-45, -24, 24, 45):
    boxes.append(Box(f"post{x}", x - 1.1, 102.9, x + 1.1, 105.1, 18, (250, 200, 80),
                     windows=False, roof=(240, 110, 60)))
  boxes.append(Box("gate_w", -8.5, -6, -6.5, -4, 10, (230, 90, 120), windows=False))
  boxes.append(Box("gate_e", 6.5, -6, 8.5, -4, 10, (230, 90, 120), windows=False))
  boxes.append(Box("gate_top", -8.5, -6, 8.5, -4, 12.5, (90, 170, 240), windows=False, y0=10))
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
  for i in range(60):
    x = ((i * 73) % 180) - 90
    z = ((i * 131) % 270) - 30
    if abs(x) < 36 and z > -10:
      continue
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
  """A chase camera behind the player with panoramic elevation."""

  FOV = math.radians(68)
  NEAR = 0.6

  def __init__(self, width, height):
    self.pitch = -0.32
    self.dist = 28.0
    self.height_offset = 12.0
    self.yaw = 0.0
    self.pos = (0.0, 12.0, -28.0)
    self.resize(width, height)

  def resize(self, width, height):
    self.w, self.h = width, height
    self.cx, self.cy = width / 2, height * 0.46
    self.focal = (min(width * 0.85, height) / 2) / math.tan(self.FOV / 2)
    self._axes()

  def _axes(self):
    cp, sp = math.cos(self.pitch), math.sin(self.pitch)
    sy, cy = math.sin(self.yaw), math.cos(self.yaw)
    self.f = (sy * cp, sp, cy * cp)
    self.r = (cy, 0.0, -sy)
    self.u = (-sy * sp, cp, -cy * sp)

  def follow(self, target, yaw, dt=None):
    if dt is None:
      self.yaw = yaw
    else:
      d = (yaw - self.yaw + math.pi) % (2 * math.pi) - math.pi
      self.yaw += d * min(1.0, dt * 5.0)
    self._axes()
    tx, ty, tz = target[0], target[1] + 1.5, target[2]
    want = (
        tx - self.f[0] * self.dist,
        max(3.5, ty + self.height_offset - self.f[1] * self.dist * 0.5),
        tz - self.f[2] * self.dist,
    )
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
    c = self.to_cam(p)
    if c[2] < self.NEAR:
      return None
    x, y = self.screen(c)
    return (x, y, c[2])

  def project_poly(self, pts):
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
    return self.cy + self.focal * math.tan(self.pitch)


# --------------------------------------------------------------------------------------
# Player
# --------------------------------------------------------------------------------------
class Player:

  def __init__(self, pos=START, yaw=0.0):
    self.pos = list(pos)
    self.vel = [0.0, 0.0, 0.0]
    self.yaw = yaw
    self.grounded = True
    self.rope = None
    self.zip = None
    self.splash = 0.0
    self.gliding = False
    self.walk_phase = 0.0

  @property
  def heading(self):
    return (math.sin(self.yaw), 0.0, math.cos(self.yaw))

  def best_anchor(self, boxes):
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
    self.vel[1] = max(self.vel[1], 0.0) + 5.0

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

  def super_jump(self):
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
    a = self.best_anchor(boxes)
    if a is None:
      return None
    for b in boxes:
      for a_cand in b.anchors():
        if a == a_cand:
          cx, _, cz = b.centre
          x = a[0] + max(-1.2, min(1.2, cx - a[0]))
          z = a[2] + max(-1.2, min(1.2, cz - a[2]))
          return (a, (x, b.h, z))
    return None

  def web_pull(self, boxes):
    hit = self.web_pull_target(boxes)
    if hit is None:
      return None
    anchor, landing = hit
    self.zip_to(landing, duration=max(0.5, min(1.4, math.dist(self.pos, landing) / 30.0)))
    self.zip.append(anchor)
    return anchor

  def glide(self, on):
    self.gliding = bool(on) and not self.grounded and self.rope is None and self.zip is None

  def update(self, dt, boxes, forward=0.0, turn=0.0):
    self.splash = max(0.0, self.splash - dt)
    if self.zip is not None:
      start, end, t, dur = self.zip[:4]
      t = min(1.0, t + dt / dur)
      self.zip[2] = t
      k = t * t * (3 - 2 * t)
      arc = 0.0 if len(self.zip) > 4 else 9.0 * 4 * t * (1 - t)
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
        self.vel[0] += hx * forward * 9.0 * h
        self.vel[2] += hz * forward * 9.0 * h
        self.rope[1] = max(ROPE_MIN, self.rope[1] - 2.5 * h * max(forward, 0))
        if self.rope[1] > self.rope[2]:
          self.rope[1] = max(self.rope[2], self.rope[1] - 22.0 * h)
      elif self.grounded:
        want = (hx * forward * WALK_SPEED, hz * forward * WALK_SPEED)
        k = min(1.0, h * 12.0)
        self.vel[0] += (want[0] - self.vel[0]) * k
        self.vel[2] += (want[1] - self.vel[2]) * k
      else:
        self.vel[0] += hx * forward * 6.0 * h
        self.vel[2] += hz * forward * 6.0 * h
      self.vel[1] -= GRAVITY * h
      if self.gliding:
        if self.vel[1] < -GLIDE_FALL:
          self.vel[1] = -GLIDE_FALL
        self.vel[0] += hx * 5.0 * h
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
        continue
      if old_y >= b.h - 0.05 and self.pos[1] <= b.h + 0.01:
        floor = max(floor, b.h)
        continue
      if self.pos[1] >= b.h:
        continue
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
      self.grounded = self.rope is None
    else:
      self.grounded = False
    x0, x1, z0, z1 = BOUNDS
    self.pos[0] = max(x0, min(x1, self.pos[0]))
    self.pos[2] = max(z0, min(z1, self.pos[2]))
    if self.grounded and self.pos[1] < 0.5 and in_river(self.pos[0], self.pos[2]):
      bank = RIVER_Z[0] - 2.0 if self.pos[2] < sum(RIVER_Z) / 2 else RIVER_Z[1] + 2.0
      self.pos = [self.pos[0], 0.0, bank]
      self.vel = [0.0, 0.0, 0.0]
      self.rope = None
      self.splash = 2.5
      event = "splash"
    return event


def nearest_entrance(boxes, pos, reach=4.5):
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
