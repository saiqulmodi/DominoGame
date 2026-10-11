"""Wonder Town - the 3D front door of Domino Wonder Dash (like Bridge Genius's Campus World).

Children walk, jump and use magic tools to move around a sunny town. Every building opens a
part of the game:
  * ABC School, Hindi Pathshala, Number House, My Home, Zoo & Garden, Food Market, Station,
    Globe Tower, India Park and Fun Park open their subject - pick a category, then a picture;
  * Story House plays the story of the day, Family House the players, Drawing Studio
    "Draw my own", Sticker Museum the sticker shelf, and the Games Arcade the Games menu.
Tapping a building (or its square on the map) flies you there and opens it.

Magic tools: Web swing (hold), Web zip (onto a roof), Super-jump boots, and a Glide cape (hold).
The town's maths lives in town3d.py; this file paints it and handles taps and keys.
"""

import math

import pygame

import domino_data as hub
import town3d as town

SKY_TOP = (90, 160, 240)
SKY_LOW = (255, 222, 180)
FOG = (210, 228, 242)
GRASS_NEAR = (98, 180, 86)
GRASS_FAR = (160, 206, 128)
STREET = (190, 182, 168)
RIVER = (60, 150, 220)
DECK = (150, 120, 96)
SUIT = (220, 40, 50)          # the little hero's red suit
SUIT_DARK = (40, 70, 170)
WEB = (250, 250, 255)
LIGHT = (0.45, 0.80, -0.40)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)

TIPS = [
    ((90, 210, 240), "Walk with the arrows (or arrow keys / W A S D)."),
    ((255, 220, 60), "Tap any building to fly there and go in."),
    ((255, 120, 120), "Magic tools: WEB to swing, ZIP onto a roof, BOOTS to jump high, CAPE to float."),
    ((140, 230, 140), "Press E (or GO IN) at a door. The house button in a game brings you back here."),
]
TOUR = ["english", "nature", "maths", "food", "story", "hindi", "home", "travel", "world", "india",
        "fun", "studio", "museum", "family", "arcade"]


def _mix(a, b, k):
  return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _shade(c, k):
  return tuple(max(0, min(255, int(v * k))) for v in c)


def _inside(pt, poly):
  x, y = pt
  inside = False
  n = len(poly)
  for i in range(n):
    x1, y1 = poly[i]
    x2, y2 = poly[(i + 1) % n]
    if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1:
      inside = not inside
  return inside


class Pad:
  """A big on-screen button. Hold pads count while a finger stays on them."""

  def __init__(self, key, label, colour, icon=None):
    self.key, self.label, self.colour, self.icon = key, label, colour, icon
    self.rect = pygame.Rect(0, 0, 10, 10)
    self.held = False
    self.visible = True


class WorldScene:

  def __init__(self, game):
    self.g = game
    self.boxes = town.build_world()
    self.by_key = {b.key: b for b in self.boxes}
    self.trees, self.lamps = town.trees_and_lamps()
    self.player = town.Player()
    self.cam = town.Camera(450, 800)
    self.size = None
    self.t = 0.0
    self.target = None
    self.enter_on_arrival = None
    self.tour_k = 0
    self.toast = ("", 0.0)
    self.picker = None            # (building, [(rect, category)], close rect)
    self.hit_polys = {}
    self.anchor = None
    self.drag_x = None
    self.web_hold = False         # WEB pad or SPACE held in the air
    self.cape_hold = False
    self.web_flash = None         # (anchor, until) - the zip web line
    self.show_tips = not game.progress.data.get("town_seen")
    self.pads = {k: Pad(k, *rest) for k, *rest in (
        ("up", "", (40, 90, 160), "up"), ("left", "", (40, 90, 160), "left"),
        ("down", "", (40, 90, 160), "down"), ("right", "", (40, 90, 160), "right"),
        ("jump", "JUMP", (60, 170, 90)), ("web", "WEB", (220, 50, 60), "web"),
        ("enter", "GO IN", (170, 70, 170)),
        ("zip", "ZIP", (240, 120, 40), "zip"), ("boots", "BOOTS", (60, 140, 230), "boots"),
        ("cape", "CAPE", (150, 80, 220), "cape"))}
    self.buttons = {}             # top-row buttons: name -> rect

  # --- layout ----------------------------------------------------------------------
  def fit(self, size):
    if size == self.size:
      return
    self.size = size
    w, h = size
    self.cam.resize(w, h)
    self.cam.follow(self.player.pos, self.player.yaw)
    self.sky = self._backdrop(w, h)
    pad = max(52, min(76, int(min(w, h) * 0.13)))
    gap = 8
    bx, by = 12, h - 12 - 2 * pad - gap
    P = self.pads
    P["up"].rect = pygame.Rect(bx + pad + gap, by, pad, pad)
    P["left"].rect = pygame.Rect(bx, by + pad + gap, pad, pad)
    P["down"].rect = pygame.Rect(bx + pad + gap, by + pad + gap, pad, pad)
    P["right"].rect = pygame.Rect(bx + 2 * (pad + gap), by + pad + gap, pad, pad)
    rx = w - 12 - pad
    for k, key in enumerate(("enter", "web", "jump")):
      P[key].rect = pygame.Rect(rx - k * (pad + gap), h - 12 - pad, pad, pad)
    for k, key in enumerate(("cape", "boots", "zip")):
      P[key].rect = pygame.Rect(rx - k * (pad + gap), h - 12 - 2 * pad - gap, pad, pad)
    if w < 3 * (pad + gap) * 2 + 40:       # narrow phone: tools move up a row
      for k, key in enumerate(("cape", "boots", "zip")):
        P[key].rect.y = h - 12 - 2 * pad - gap
    bw = min(150, (w - 40) // 3)
    self.buttons = {"guide": pygame.Rect(10, 8, bw, 38),
                    "pictures": pygame.Rect(18 + bw, 8, bw, 38)}
    mw = 170 if w >= 700 else 120
    self.map_rect = pygame.Rect(w - mw - 10, 56, mw, int(mw * 1.35))

  def _backdrop(self, w, h):
    hy = int(self.cam.horizon_y())
    s = pygame.Surface((w, h))
    for y in range(h):
      if y <= hy:
        col = _mix(SKY_TOP, SKY_LOW, (y / max(1, hy)) ** 1.5)
      else:
        col = _mix(GRASS_FAR, GRASS_NEAR, ((y - hy) / max(1, h - hy)) ** 0.7)
      pygame.draw.line(s, col, (0, y), (w, y))
    return s

  # --- helpers ---------------------------------------------------------------------
  def text(self, s, msg, pos, size, colour=WHITE, anchor="center"):
    img = self.g.font_at(size).render(msg, True, colour)
    r = img.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    s.blit(img, r)
    return r

  def icon_for(self, b, size):
    """The sign picture: the building's own picture, or its subject's first picture."""
    cat, item = b.icon or (None, None)
    if b.kind == "subject" and cat is None:
      cat = self.g.subjects[b.payload][0]
      item = next(iter(hub.CATEGORIES_HUB[cat]))
    if cat is None:
      return None
    return self.g.thumb(item, cat, size)

  def say(self, msg, secs=3.5):
    self.toast = (msg, secs)

  def close_tips(self):
    self.show_tips = False
    self.g.progress.data["town_seen"] = True
    self.g.progress.save()

  def next_tour(self):
    self.g.sfx.play("click")
    self.target = self.by_key[TOUR[self.tour_k % len(TOUR)]]
    self.tour_k += 1
    self.say(f"{self.target.label}: {self.target.sub}", 4.0)

  def fly_to(self, b, enter=True):
    """Fly to a building's door (and go in when we land)."""
    if self.player.zip is not None:
      return
    self.target = b
    self.enter_on_arrival = b if enter else None
    self.g.sfx.play("switch")
    self.player.zip_to(b.door())

  # --- entering buildings ----------------------------------------------------------
  def enter(self, b):
    g = self.g
    g.sfx.play("chime")
    kind = b.kind
    if kind == "subject":
      cats = g.subjects[b.payload]
      self.picker = (b, cats)
    elif kind == "story":
      g.start_story(g.story_of_today())
    elif kind == "players":
      g.overlay = "players"
    elif kind == "draw":
      g.start_drawing()
    elif kind == "stickers":
      g.overlay = "shelf"
    elif kind == "games":
      g.overlay = "menu"

  def pick_category(self, b, cat):
    g = self.g
    self.picker = None
    if g.subject != b.payload:
      g.subject = b.payload
    g.select_category(cat)
    g.overlay = "nav"              # the picture bank of that category; a pick starts it

  # --- input -----------------------------------------------------------------------
  def picker_layout(self):
    b, cats = self.picker
    w, h = self.size
    cols = 2 if w < 600 else min(3, len(cats))
    rows = -(-len(cats) // cols)
    cw, ch = min(190, (w - 60) // cols), 120
    pw, ph = cols * (cw + 12) + 28, rows * (ch + 12) + 130
    panel = pygame.Rect(0, 0, pw, ph)
    panel.center = (w // 2, h // 2)
    cells = []
    for k, cat in enumerate(cats):
      r = pygame.Rect(panel.x + 20 + (k % cols) * (cw + 12), panel.y + 70 + (k // cols) * (ch + 12), cw, ch)
      cells.append((r, cat))
    close = pygame.Rect(0, 0, 150, 40)
    close.midbottom = (panel.centerx, panel.bottom - 12)
    return panel, cells, close

  def pick_box_at(self, pos):
    if self.map_rect.collidepoint(pos):
      best, best_d = None, 14.0
      for b in self.boxes:
        if b.kind is None:
          continue
        r = self.map_box(b)
        d = 0 if r.collidepoint(pos) else math.hypot(r.centerx - pos[0], r.centery - pos[1])
        if d < best_d:
          best, best_d = b, d
      return best
    for key in reversed(list(self.hit_polys)):
      for poly in self.hit_polys[key]:
        if _inside(pos, poly):
          return self.by_key[key]
    return None

  def press(self, pos):
    if self.picker is not None:
      panel, cells, close = self.picker_layout()
      for r, cat in cells:
        if r.collidepoint(pos):
          self.g.sfx.play("click")
          self.pick_category(self.picker[0], cat)
          return
      if close.collidepoint(pos) or not panel.collidepoint(pos):
        self.g.sfx.play("click")
        self.picker = None
      return
    if self.show_tips:
      if self.tips_button.collidepoint(pos) or self.tips_rect.collidepoint(pos):
        self.g.sfx.play("click")
        self.close_tips()
        return
    if self.buttons["guide"].collidepoint(pos):
      self.next_tour()
      return
    if self.buttons["pictures"].collidepoint(pos):
      self.g.sfx.play("switch")
      self.g.overlay = "nav"
      return
    if self.target is not None and self.zip_rect.collidepoint(pos) and self.player.zip is None:
      self.fly_to(self.target)
      return
    for key, p in self.pads.items():
      if p.visible and p.rect.collidepoint(pos):
        p.held = True
        self.pad_down(key)
        return
    b = self.pick_box_at(pos)
    if b is not None and b.kind is not None:
      self.fly_to(b)
      return
    self.drag_x = pos[0]

  def drag(self, pos):
    if self.drag_x is not None:
      self.player.yaw += (pos[0] - self.drag_x) * 0.008
      self.drag_x = pos[0]

  def release(self, pos):
    for key, p in self.pads.items():
      if p.held and key == "web":
        self.web(False)
      if p.held and key == "cape":
        self.cape_hold = False
      p.held = False
    self.drag_x = None

  def pad_down(self, key):
    if key == "jump":
      if self.player.jump():
        self.g.sfx.play("pop")
    elif key == "web":
      self.web(True)
    elif key == "enter":
      self.try_enter()
    elif key == "zip":
      self.web_zip()
    elif key == "boots":
      self.boots()
    elif key == "cape":
      self.cape_hold = True
      if self.player.grounded:
        self.boots()               # take off, then float down

  def key(self, event):
    """Keyboard in the town. Returns True when the key was used."""
    k = event.key
    if self.picker is not None and k in (pygame.K_ESCAPE, pygame.K_AC_BACK):
      self.picker = None
      return True
    if k == pygame.K_SPACE:
      if self.player.grounded:
        if self.player.jump():
          self.g.sfx.play("pop")
      else:
        self.web(True)
      return True
    if k in (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER):
      self.try_enter()
      return True
    if k == pygame.K_t:
      self.next_tour()
      return True
    if k == pygame.K_z and self.target is not None:
      self.fly_to(self.target)
      return True
    if k == pygame.K_q:
      self.web_zip()
      return True
    if k == pygame.K_b:
      self.boots()
      return True
    return k in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                 pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_g)

  def web(self, down):
    p = self.player
    if down:
      self.web_hold = True
      if p.rope is None and p.zip is None:
        if p.grounded:
          p.jump()
        if p.attach(self.boxes):
          self.g.sfx.play("switch")
    else:
      self.web_hold = False
      if p.rope is not None:
        p.release()

  def web_zip(self):
    if self.player.zip is not None:
      return
    anchor = self.player.web_pull(self.boxes)
    if anchor is None:
      self.say("Face a building to zip onto its roof!")
      return
    self.g.sfx.play("switch")
    self.web_flash = (anchor, self.t + 1.6)

  def boots(self):
    if self.player.super_jump():
      self.g.sfx.play("pop")

  def try_enter(self):
    b = town.nearest_entrance(self.boxes, self.player.pos)
    if b is not None:
      self.enter(b)

  # --- update ----------------------------------------------------------------------
  def update(self, dt):
    self.t += dt
    msg, ttl = self.toast
    self.toast = (msg, max(0.0, ttl - dt))
    if self.g.overlay or self.picker is not None:
      return
    try:
      keys = pygame.key.get_pressed()
    except pygame.error:
      keys = None

    def k(*codes):
      return bool(keys) and any(keys[c] for c in codes)

    P = self.pads
    fwd = (1.0 if (k(pygame.K_UP, pygame.K_w) or P["up"].held) else 0.0) - \
          (1.0 if (k(pygame.K_DOWN, pygame.K_s) or P["down"].held) else 0.0)
    turn = (1.0 if (k(pygame.K_RIGHT, pygame.K_d) or P["right"].held) else 0.0) - \
           (1.0 if (k(pygame.K_LEFT, pygame.K_a) or P["left"].held) else 0.0)
    if (fwd or turn) and self.show_tips and self.t > 6:
      self.close_tips()
    p = self.player
    if self.web_hold and not P["web"].held and not k(pygame.K_SPACE):
      self.web(False)              # SPACE was let go
    if p.rope is None and not p.grounded and self.web_hold and p.zip is None and p.vel[1] < 2:
      if p.attach(self.boxes):     # holding through the jump
        self.g.sfx.play("switch")
    p.glide(self.cape_hold or k(pygame.K_g))
    event = p.update(dt, self.boxes, fwd, turn)
    if event == "splash":
      self.g.sfx.play("clack")
      self.say("Splash! Use WEB or ZIP on the river posts, or walk over the bridge.", 4.0)
    elif event == "arrived":
      self.g.sfx.play("chime")
      if self.enter_on_arrival is not None:
        b, self.enter_on_arrival = self.enter_on_arrival, None
        self.enter(b)
    self.anchor = None if (p.rope or p.zip) else p.best_anchor(self.boxes)
    self.cam.follow(p.pos, p.yaw, dt)

  # --- drawing ---------------------------------------------------------------------
  def fog(self, col, depth):
    return _mix(col, FOG, min(0.75, max(0.0, (depth - 45.0) / 240.0)))

  def draw(self, s):
    self.fit(s.get_size())
    cam = self.cam
    w, h = self.size
    s.blit(self.sky, (0, 0))
    hy = int(cam.horizon_y())
    d = (0.7 - cam.yaw + math.pi) % (2 * math.pi) - math.pi      # a smiling sun in the north-east
    if abs(d) < 1.2:
      sx, sy = cam.cx + cam.focal * math.tan(d), hy - 130
      for k in range(12):
        a = self.t * 0.25 + k * math.pi / 6
        pygame.draw.line(s, (255, 226, 110), (sx + 40 * math.cos(a), sy + 40 * math.sin(a)),
                         (sx + 54 * math.cos(a), sy + 54 * math.sin(a)), 4)
      pygame.draw.circle(s, (255, 214, 80), (int(sx), int(sy)), 32)
      pygame.draw.circle(s, (90, 60, 30), (int(sx - 10), int(sy - 5)), 3)
      pygame.draw.circle(s, (90, 60, 30), (int(sx + 10), int(sy - 5)), 3)
      pygame.draw.arc(s, (90, 60, 30), (sx - 12, sy - 4, 24, 18), math.pi * 1.1, math.pi * 1.9, 3)
    self.draw_hills(s, hy)
    self.draw_ground(s)
    items = []
    self.hit_polys = {}
    cp = cam.pos
    for b in self.boxes:
      dist = math.dist(b.centre, cp)
      if dist < 280:
        items.append((dist, 0, b))
    for t in self.trees:
      dist = math.dist((t[0], t[2] / 2, t[1]), cp)
      if dist < 170:
        items.append((dist, 1, t))
    for lp in self.lamps:
      dist = math.dist((lp[0], 3, lp[1]), cp)
      if dist < 120:
        items.append((dist, 2, lp))
    items.append((math.dist(self.player.pos, cp), 3, None))
    items.sort(key=lambda it: -it[0])
    labels = self.place_labels()
    for dist, kind, obj in items:
      if kind == 0:
        self.draw_box(s, obj, dist)
        if obj.key in labels:
          self.draw_label(s, obj, *labels[obj.key])
      elif kind == 1:
        self.draw_tree(s, obj, dist)
      elif kind == 2:
        self.draw_lamp(s, obj, dist)
      else:
        self.draw_player(s)
    self.draw_anchor(s)
    self.draw_hud(s)

  def draw_hills(self, s, hy):
    w = self.size[0]
    off = -self.cam.yaw * self.cam.focal
    for col, amp, base, f in (((170, 196, 214), 26, 30, 0.004), ((128, 178, 120), 14, 6, 0.008)):
      pts = [(0, hy + 2)]
      for x in range(0, w + 12, 12):
        X = x - off
        pts.append((x, hy - base - amp * (0.6 * math.sin(X * f) + 0.4 * math.sin(X * f * 2.3 + 1))))
      pts.append((w, hy + 2))
      pygame.draw.polygon(s, col, pts)

  def ground_poly(self, s, pts, col, y=0.0):
    pr = self.cam.project_poly([(x, y, z) for x, z in pts])
    if pr is not None and len(pr[0]) >= 3:
      pygame.draw.polygon(s, self.fog(col, pr[1] * 0.6), pr[0])
      return pr[0]
    return None

  def draw_ground(self, s):
    x0, x1, z0, z1 = town.BOUNDS
    rz0, rz1 = town.RIVER_Z
    for za in range(int(z0), int(z1), 30):
      self.ground_poly(s, [(-5, za), (5, za), (5, min(z1, za + 30)), (-5, min(z1, za + 30))], STREET)
    for b in self.boxes:
      if b.kind is not None and b.key != "arcade":
        dx, _, dz = b.door()
        xa, xb = sorted((dx, 0.0))
        self.ground_poly(s, [(xa, dz - 1.8), (xb, dz - 1.8), (xb, dz + 1.8), (xa, dz + 1.8)], STREET)
    plaza = [(12 * math.cos(a / 12 * math.tau), 4 + 12 * math.sin(a / 12 * math.tau)) for a in range(12)]
    self.ground_poly(s, plaza, (236, 200, 150))
    self.ground_poly(s, [(x0, rz0), (x1, rz0), (x1, rz1), (x0, rz1)], RIVER)
    for k in range(7):
      z = rz0 + 2 + ((k * 2.0 + self.t * 1.2) % (rz1 - rz0 - 4))
      a = self.cam.project((x0 + 20, 0.02, z))
      b = self.cam.project((x1 - 20, 0.02, z))
      if a and b:
        pygame.draw.line(s, (150, 205, 245), a[:2], b[:2], 1)
    self.ground_poly(s, [(-6, rz0 - 2), (6, rz0 - 2), (6, rz1 + 2), (-6, rz1 + 2)], DECK)
    for b in self.boxes:                         # little flower beds in front of houses
      if b.kind is not None and b.gable:
        dx, _, dz = b.door()
        for k in range(5):
          p = self.cam.project((dx + (1.5 if b.x0 > 0 else -1.5), 0.05, dz - 4 + k * 2))
          if p and p[2] < 70:
            pygame.draw.circle(s, ((255, 120, 160), (255, 220, 60), (200, 140, 255))[k % 3],
                               (int(p[0]), int(p[1])), max(2, int(self.cam.focal * 0.25 / p[2])))
    if self.target is not None:
      dx, _, dz = self.target.door()
      r = 2.4 + 0.4 * math.sin(self.t * 5)
      ring = [(dx + r * math.cos(a / 16 * math.tau), dz + r * math.sin(a / 16 * math.tau)) for a in range(16)]
      pr = self.cam.project_poly([(x, 0.05, z) for x, z in ring])
      if pr:
        pygame.draw.polygon(s, YELLOW, pr[0], 4)

  def draw_box(self, s, b, dist):
    cam = self.cam
    x0, x1, z0, z1, y0, y1 = b.x0, b.x1, b.z0, b.z1, b.y0, b.h
    cp = cam.pos
    faces = []
    if cp[2] < z0:
      faces.append(((0, 0, -1), [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]))
    if cp[2] > z1:
      faces.append(((0, 0, 1), [(x1, y0, z1), (x0, y0, z1), (x0, y1, z1), (x1, y1, z1)]))
    if cp[0] < x0:
      faces.append(((-1, 0, 0), [(x0, y0, z1), (x0, y0, z0), (x0, y1, z0), (x0, y1, z1)]))
    if cp[0] > x1:
      faces.append(((1, 0, 0), [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)]))
    if cp[1] > y1 and not b.gable:
      faces.append(((0, 1, 0), [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]))
    if cp[1] < y0:
      faces.append(((0, -1, 0), [(x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0)]))
    if b.gable:                                  # a pointed roof, ridge running east-west
      rh = b.roof_height()
      zm = (z0 + z1) / 2
      faces.append((("roof", -1), [(x0, y1, z0), (x1, y1, z0), (x1, y1 + rh, zm), (x0, y1 + rh, zm)]))
      faces.append((("roof", 1), [(x1, y1, z1), (x0, y1, z1), (x0, y1 + rh, zm), (x1, y1 + rh, zm)]))
      for x, sgn in ((x0, -1), (x1, 1)):
        if (cp[0] - x) * sgn > 0:
          faces.append(((sgn, 0, 0), [(x, y1, z0), (x, y1 + rh, zm), (x, y1, z1)]))
    polys = []
    for n, pts in faces:
      if n[0] == "roof":
        # a roof slope is seen when the camera is on its side or above the ridge line
        side = n[1]
        zm = (z0 + z1) / 2
        if (cp[2] - zm) * side < 0 and cp[1] < y1 + b.roof_height():
          continue
        pr = cam.project_poly(pts)
        if pr is None:
          continue
        k = 0.75 + 0.3 * (1 if side < 0 else 0.4)
        col = self.fog(_shade(b.roof, k), dist)
      else:
        pr = cam.project_poly(pts)
        if pr is None:
          continue
        k = 0.62 + 0.45 * max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2])
        base = b.roof if n[1] > 0 else b.colour
        col = self.fog(_shade(base, k), dist)
      poly = pr[0]
      pygame.draw.polygon(s, col, poly)
      pygame.draw.polygon(s, self.fog(_shade(col, 0.75), dist), poly, 1)
      polys.append(poly)
      if n[0] != "roof" and n[1] == 0 and len(pts) == 4 and b.windows and dist < 90:
        self.draw_windows(s, b, pts, dist)
    if self.target is b and polys:
      for poly in polys:
        pygame.draw.polygon(s, (255, 236, 120), poly, 3)
    if b.kind is not None and polys:
      self.hit_polys[b.key] = polys

  def draw_windows(self, s, b, pts, dist):
    cam = self.cam
    p0, p1, _, p3 = pts
    width = math.dist(p0, p1)
    height = b.h - b.y0
    cols = max(1, min(5, int(width / 4.5)))
    rows = max(1, min(4, int(height / 5.0)))
    dx, _, dz = b.door()
    mid = ((p0[0] + p1[0]) / 2, (p0[2] + p1[2]) / 2)
    door_face = math.hypot(mid[0] - dx, mid[1] - dz) < 4.0

    def at(u, v):
      return tuple(p0[i] + (p1[i] - p0[i]) * u + (p3[i] - p0[i]) * v for i in range(3))

    for r in range(rows):
      for c in range(cols):
        if door_face and r == 0 and abs((c + 0.5) / cols - 0.5) < 0.6 / cols:
          continue
        u0, u1 = (c + 0.22) / cols, (c + 0.78) / cols
        v0, v1 = (r + 0.3) / rows, (r + 0.78) / rows
        pr = cam.project_poly([at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)])
        if pr:
          pygame.draw.polygon(s, self.fog((255, 250, 235), dist), pr[0])
          pygame.draw.polygon(s, self.fog((120, 170, 230), dist), pr[0], 2)
    if door_face:
      dw = min(0.3, 3.2 / max(width, 1.0))
      top = min(0.8, 4.2 / height)
      pr = cam.project_poly([at(0.5 - dw / 2, 0), at(0.5 + dw / 2, 0), at(0.5 + dw / 2, top), at(0.5 - dw / 2, top)])
      if pr:
        pygame.draw.polygon(s, self.fog((140, 80, 50), dist), pr[0])
        pygame.draw.polygon(s, self.fog((255, 220, 120), dist), pr[0], 2)

  def draw_tree(self, s, t, dist):
    x, z, h = t
    base = self.cam.project((x, 0.0, z))
    top = self.cam.project((x, h, z))
    if not base or not top:
      return
    scale = self.cam.focal / base[2]
    pygame.draw.line(s, self.fog((120, 80, 50), dist), base[:2], top[:2], max(1, int(0.5 * scale)))
    for fy, fr, col in ((0.55, 0.45, (60, 150, 70)), (0.82, 0.33, (90, 180, 90))):
      c = self.cam.project((x, h * fy, z))
      if c:
        pygame.draw.circle(s, self.fog(col, dist), (int(c[0]), int(c[1])), max(2, int(h * fr * scale)))

  def draw_lamp(self, s, lp, dist):
    x, z = lp
    a = self.cam.project((x, 0.0, z))
    b = self.cam.project((x, 4.5, z))
    if a and b:
      pygame.draw.line(s, self.fog((70, 80, 100), dist), a[:2], b[:2], max(1, int(self.cam.focal * 0.16 / a[2])))
      pygame.draw.circle(s, self.fog((255, 236, 170), dist), (int(b[0]), int(b[1])), max(2, int(self.cam.focal * 0.38 / b[2])))

  def floor_under(self):
    px, py, pz = self.player.pos
    floor = 0.0
    for b in self.boxes:
      if b.contains_xz(px, pz) and b.h <= py + 0.1:
        floor = max(floor, b.h)
    return floor

  def draw_player(self, s):
    """The little hero: red and blue suit, with a cape when gliding."""
    p, cam = self.player, self.cam
    px, py, pz = p.pos
    sh = cam.project((px, self.floor_under() + 0.03, pz))
    if sh:
      r = max(3, int(cam.focal * 0.7 / sh[2]))
      shadow = pygame.Surface((2 * r, r), pygame.SRCALPHA)
      pygame.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
      s.blit(shadow, (sh[0] - r, sh[1] - r // 2))
    foot = cam.project((px, py, pz))
    if not foot:
      return
    sc = cam.focal / foot[2]
    hx, _, hz = p.heading

    def P(dx, dy, dz=0.0):
      q = cam.project((px + hz * dx + hx * dz, py + dy, pz - hx * dx + hz * dz))
      return (q[0], q[1]) if q else foot[:2]

    swing = math.sin(p.walk_phase * 2.2) * (0.4 if p.grounded else 0.15)
    hip, neck, head = P(0, 0.95), P(0, 1.45), P(0, 1.68)
    lw = max(2, int(0.17 * sc))
    if p.gliding:                                # the magic cape spreads out behind
      pygame.draw.polygon(s, (150, 80, 220), [P(-0.25, 1.45, -0.1), P(0.25, 1.45, -0.1),
                                              P(0.9, 0.5, -0.8), P(-0.9, 0.5, -0.8)])
    pygame.draw.line(s, SUIT_DARK, hip, P(-0.15, 0.0, swing), lw)
    pygame.draw.line(s, SUIT_DARK, hip, P(0.15, 0.0, -swing), lw)
    pygame.draw.line(s, SUIT, hip, neck, max(3, int(0.34 * sc)))
    rope = p.rope[0] if p.rope is not None else None
    if rope is None and self.web_flash and self.t < self.web_flash[1] and p.zip is not None:
      rope = self.web_flash[0]
    if rope is not None:
      hand = P(0.1, 2.0)
      a = cam.project(rope)
      if a:
        pygame.draw.line(s, WEB, hand, a[:2], 2)
        pygame.draw.line(s, (200, 210, 230), (hand[0] + 2, hand[1]), (a[0] + 2, a[1]), 1)
        for k in range(6):                       # a little web splat where it sticks
          ang = k * math.pi / 3
          pygame.draw.line(s, WEB, a[:2], (a[0] + 9 * math.cos(ang), a[1] + 9 * math.sin(ang)), 1)
        pygame.draw.circle(s, WEB, (int(a[0]), int(a[1])), 6, 1)
      pygame.draw.line(s, SUIT, neck, hand, lw)
      pygame.draw.line(s, SUIT, neck, P(-0.35, 1.0, 0.2), lw)
    elif not p.grounded:
      pygame.draw.line(s, SUIT, neck, P(-0.45, 1.75), lw)
      pygame.draw.line(s, SUIT, neck, P(0.45, 1.75), lw)
    else:
      pygame.draw.line(s, SUIT, neck, P(-0.32, 1.0, -swing), lw)
      pygame.draw.line(s, SUIT, neck, P(0.32, 1.0, swing), lw)
    hr = max(3, int(0.22 * sc))
    pygame.draw.circle(s, SUIT, (int(head[0]), int(head[1])), hr)        # the hero's mask
    for ex in (-0.35, 0.35):
      pygame.draw.ellipse(s, WHITE, (head[0] + ex * hr * 1.6 - hr * 0.3, head[1] - hr * 0.35, hr * 0.6, hr * 0.45))
    if p.splash > 0:
      for k in range(6):
        a = k / 6 * math.tau + self.t * 3
        q = P(math.cos(a) * 0.9, 0.3 + 0.8 * p.splash / 2.5, math.sin(a) * 0.9)
        pygame.draw.circle(s, (190, 225, 255), (int(q[0]), int(q[1])), max(2, int(0.1 * sc)))

  def draw_anchor(self, s):
    if self.anchor is None or self.g.overlay or self.picker is not None:
      return
    a = self.cam.project(self.anchor)
    if a:
      r = 8 + 3 * math.sin(self.t * 8)
      pygame.draw.circle(s, WHITE, (int(a[0]), int(a[1])), int(r) + 3, 2)
      pygame.draw.circle(s, YELLOW, (int(a[0]), int(a[1])), int(r))

  def place_labels(self):
    """Name signs nearest first; a sign overlapping a nearer one is left out."""
    cam = self.cam
    cands = []
    for b in self.boxes:
      if b.kind is None:
        continue
      cx, _, cz = b.centre
      p = cam.project((cx, b.top + 2.0, cz))
      if not p or p[2] > 200 or not (-40 < p[0] < self.size[0] + 40):
        continue
      size = int(max(13, min(26, 1300 / p[2])))
      icon = size + 14 if p[2] < 120 else 0
      tw = self.g.font_at(size).size(b.label)[0]
      r = pygame.Rect(0, 0, tw + 24 + icon, max(size + 14, icon + 6))
      r.midbottom = (int(p[0]), int(p[1]))
      if r.top < 52:
        base = cam.project((cx, b.y0, cz))
        if base is None or base[1] < 52 + r.h:
          continue
        r.top = 52
      cands.append((p[2], b, r, size, icon))
    cands.sort(key=lambda c: c[0])
    kept, taken = {}, []
    for depth, b, r, size, icon in cands:
      if any(r.colliderect(t) for t in taken):
        continue
      taken.append(r.inflate(8, 6))
      kept[b.key] = (r, size, icon, depth)
    return kept

  def draw_label(self, s, b, r, size, icon, depth):
    pill = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(pill, (255, 255, 255, 235), pill.get_rect(), border_radius=r.h // 2)
    pygame.draw.rect(pill, (*b.colour, 255), pill.get_rect(), 4, border_radius=r.h // 2)
    s.blit(pill, r.topleft)
    x = r.x + 12
    if icon:
      pic = self.icon_for(b, icon)
      if pic is not None:
        s.blit(pic, pic.get_rect(midleft=(x, r.centery)))
      x += icon + 4
    self.text(s, b.label, (x, r.centery), size, (40, 40, 70), anchor="midleft")

  def map_box(self, b):
    x0, x1, z0, z1 = town.BOUNDS
    m = self.map_rect
    sx, sz = m.w / (x1 - x0), m.h / (z1 - z0)
    return pygame.Rect(m.x + (b.x0 - x0) * sx, m.bottom - (b.z1 - z0) * sz,
                       max(4, (b.x1 - b.x0) * sx), max(4, (b.z1 - b.z0) * sz))

  def map_point(self, x, z):
    x0, x1, z0, z1 = town.BOUNDS
    m = self.map_rect
    return (m.x + (x - x0) * m.w / (x1 - x0), m.bottom - (z - z0) * m.h / (z1 - z0))

  def draw_map(self, s):
    m = self.map_rect
    pygame.draw.rect(s, WHITE, m.inflate(8, 8), border_radius=10)
    pygame.draw.rect(s, (110, 180, 100), m)
    a, b = self.map_point(-5, town.BOUNDS[2]), self.map_point(5, town.BOUNDS[3])
    pygame.draw.rect(s, STREET, pygame.Rect(a[0], b[1], max(2, b[0] - a[0]), a[1] - b[1]))
    r0, r1 = self.map_point(town.BOUNDS[0], town.RIVER_Z[1]), self.map_point(town.BOUNDS[1], town.RIVER_Z[0])
    pygame.draw.rect(s, RIVER, pygame.Rect(r0[0], r0[1], r1[0] - r0[0], max(2, r1[1] - r0[1])))
    for bx in self.boxes:
      if bx.kind is None:
        continue
      r = self.map_box(bx)
      pygame.draw.rect(s, bx.colour, r)
      if bx is self.target:
        pygame.draw.rect(s, WHITE, r.inflate(6, 6), 2)
    p = self.player
    c = self.map_point(p.pos[0], p.pos[2])
    hx, _, hz = p.heading
    tri = [(c[0] + hx * 9, c[1] - hz * 9), (c[0] - hz * 5 - hx * 4, c[1] - hx * 5 + hz * 4),
           (c[0] + hz * 5 - hx * 4, c[1] + hx * 5 + hz * 4)]
    pygame.draw.polygon(s, WHITE, tri)
    pygame.draw.polygon(s, SUIT, tri, 2)

  def draw_button(self, s, rect, label, colour):
    pygame.draw.rect(s, colour, rect, border_radius=12)
    pygame.draw.rect(s, WHITE, rect, 2, border_radius=12)
    size = 17
    while size > 11 and self.g.font_at(size).size(label)[0] > rect.w - 10:
      size -= 1
    self.text(s, label, rect.center, size)

  def draw_pad(self, s, p):
    r = p.rect
    surf = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (*_shade(p.colour, 1.35 if p.held else 1.0), 215), surf.get_rect(), border_radius=16)
    pygame.draw.rect(surf, (255, 255, 255, 170), surf.get_rect(), 3, border_radius=16)
    s.blit(surf, r.topleft)
    c, k = r.center, r.w * 0.22
    arrows = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    if p.icon in arrows:
      dx, dy = arrows[p.icon]
      tip = (c[0] + dx * k, c[1] + dy * k)
      side = (-dy * k * 0.9, dx * k * 0.9)
      back = (c[0] - dx * k * 0.7, c[1] - dy * k * 0.7)
      pygame.draw.polygon(s, WHITE, [tip, (back[0] + side[0], back[1] + side[1]), (back[0] - side[0], back[1] - side[1])])
      return
    iy = c[1] - r.h * 0.12
    if p.icon == "web":                          # a spider web
      for a in range(8):
        ang = a * math.pi / 4
        pygame.draw.line(s, WHITE, (c[0], iy), (c[0] + k * math.cos(ang), iy + k * math.sin(ang)), 2)
      for rr in (k * 0.45, k * 0.9):
        pygame.draw.circle(s, WHITE, (int(c[0]), int(iy)), int(rr), 1)
    elif p.icon == "zip":                        # a web line up to a roof
      pygame.draw.polygon(s, WHITE, [(c[0] + k * 0.2, iy - k * 0.9), (c[0] + k, iy - k * 0.3), (c[0] - k * 0.6, iy - k * 0.3)])
      pygame.draw.line(s, WHITE, (c[0] - k, iy + k * 0.8), (c[0] + k * 0.2, iy - k * 0.5), 3)
    elif p.icon == "boots":                      # a winged boot
      pygame.draw.rect(s, WHITE, (c[0] - k * 0.5, iy - k * 0.8, k * 0.6, k * 1.2), border_radius=3)
      pygame.draw.rect(s, WHITE, (c[0] - k * 0.5, iy + k * 0.2, k * 1.3, k * 0.5), border_radius=4)
      pygame.draw.polygon(s, YELLOW, [(c[0] - k * 0.5, iy - k * 0.4), (c[0] - k * 1.2, iy - k * 0.9), (c[0] - k * 0.9, iy - k * 0.2)])
    elif p.icon == "cape":                       # a flowing cape
      pygame.draw.polygon(s, WHITE, [(c[0] - k * 0.4, iy - k * 0.8), (c[0] + k * 0.4, iy - k * 0.8),
                                     (c[0] + k, iy + k * 0.8), (c[0] - k, iy + k * 0.8)])
    else:
      iy = c[1] + r.h * 0.12
    self.text(s, p.label, (c[0], r.bottom - r.h * 0.2 if p.icon else c[1]), 15 if len(p.label) < 6 else 13)

  def draw_hud(self, s):
    w, h = self.size
    bar = pygame.Surface((w, 54), pygame.SRCALPHA)
    bar.fill((30, 70, 140, 160))
    s.blit(bar, (0, 0))
    self.draw_button(s, self.buttons["guide"], "Guide me", (150, 80, 200))
    self.draw_button(s, self.buttons["pictures"], "Pictures", (60, 160, 90))
    if w >= 560:
      self.text(s, "Wonder Town", (w - self.map_rect.w - 30, 27), 22, YELLOW, anchor="midright")
    self.draw_map(s)
    self.zip_rect = pygame.Rect(0, 0, 0, 0)
    if self.target is not None and self.player.zip is None:
      p = self.player
      dx, _, dz = self.target.door()
      dist = math.hypot(dx - p.pos[0], dz - p.pos[2])
      if dist > 6:
        label = f"Fly to {self.target.label}  ({int(dist)} m)"
        tw = self.g.font_at(17).size(label)[0]
        self.zip_rect = pygame.Rect(0, 0, min(w - 20, tw + 40), 40)
        self.zip_rect.midtop = (w // 2 if w >= 560 else (w - self.map_rect.w - 20) // 2 + 4, 62)
        pygame.draw.rect(s, (240, 140, 40), self.zip_rect, border_radius=20)
        pygame.draw.rect(s, WHITE, self.zip_rect, 2, border_radius=20)
        self.text(s, label, self.zip_rect.center, 17 if tw + 40 <= w - 20 else 14)
    b = town.nearest_entrance(self.boxes, self.player.pos)
    self.pads["enter"].visible = b is not None
    for p in self.pads.values():
      if p.visible:
        self.draw_pad(s, p)
    if b is not None and not self.g.overlay and self.picker is None:
      label = f"Go into {b.label}!"
      tw = self.g.font_at(20).size(label)[0]
      r = pygame.Rect(0, 0, min(w - 20, tw + 44), 46)
      top_of_pads = min(p.rect.top for p in self.pads.values())
      r.midbottom = (w // 2, top_of_pads - 10)
      pulse = int(30 * (1 + math.sin(self.t * 6)))
      pygame.draw.rect(s, (170 + pulse // 2, 70, 170), r, border_radius=23)
      pygame.draw.rect(s, WHITE, r, 2, border_radius=23)
      self.text(s, label, r.center, 20)
    msg, ttl = self.toast
    if ttl > 0 and msg:
      size = 17
      while size > 11 and self.g.font_at(size).size(msg)[0] > w - 50:
        size -= 1
      tw = self.g.font_at(size).size(msg)[0]
      r = pygame.Rect(0, 0, tw + 30, 40)
      r.midtop = (w // 2, 110)
      box = pygame.Surface(r.size, pygame.SRCALPHA)
      pygame.draw.rect(box, (30, 50, 90, int(min(1.0, ttl) * 225)), box.get_rect(), border_radius=14)
      s.blit(box, r.topleft)
      self.text(s, msg, r.center, size)
    self.tips_rect = self.tips_button = pygame.Rect(0, 0, 0, 0)
    if self.show_tips and not self.g.overlay and self.picker is None:
      cw = min(440, w - 30)
      lines = []
      for col, tip in TIPS:
        words, cur, first = tip.split(), "", True
        for word in words:
          trial = (cur + " " + word).strip()
          if self.g.font_at(15).size(trial)[0] > cw - 60 and cur:
            lines.append((col if first else None, cur))
            cur, first = word, False
          else:
            cur = trial
        lines.append((col if first else None, cur))
      r = pygame.Rect(14, 62, cw, 70 + 24 * len(lines) + 60)
      box = pygame.Surface(r.size, pygame.SRCALPHA)
      pygame.draw.rect(box, (30, 60, 110, 235), box.get_rect(), border_radius=16)
      pygame.draw.rect(box, (255, 204, 0, 255), box.get_rect(), 3, border_radius=16)
      s.blit(box, r.topleft)
      self.text(s, "Welcome to Wonder Town!", (r.x + 18, r.y + 16), 22, YELLOW, anchor="topleft")
      y = r.y + 56
      for col, line in lines:
        if col:
          pygame.draw.circle(s, col, (r.x + 24, y + 10), 6)
        self.text(s, line, (r.x + 40, y), 15, anchor="topleft")
        y += 24
      self.tips_rect = r
      self.tips_button = pygame.Rect(r.x + 18, r.bottom - 52, 150, 40)
      self.draw_button(s, self.tips_button, "Let's go!", (60, 170, 90))
    if self.picker is not None:
      self.draw_picker(s)

  def draw_picker(self, s):
    b, cats = self.picker
    panel, cells, close = self.picker_layout()
    veil = pygame.Surface(self.size, pygame.SRCALPHA)
    veil.fill((10, 20, 40, 140))
    s.blit(veil, (0, 0))
    pygame.draw.rect(s, (255, 250, 240), panel, border_radius=18)
    pygame.draw.rect(s, b.colour, panel, 5, border_radius=18)
    self.text(s, b.label, (panel.centerx, panel.y + 26), 26, (40, 40, 70))
    self.text(s, "What shall we learn?", (panel.centerx, panel.y + 52), 15, (90, 90, 120))
    for r, cat in cells:
      pygame.draw.rect(s, _shade(b.colour, 1.1), r, border_radius=14)
      pygame.draw.rect(s, WHITE, r, 3, border_radius=14)
      first = next(iter(hub.CATEGORIES_HUB[cat]))
      pic = self.g.thumb(first, cat, r.h - 46)
      if pic is not None:
        s.blit(pic, pic.get_rect(center=(r.centerx, r.y + (r.h - 30) // 2 + 4)))
      self.text(s, cat, (r.centerx, r.bottom - 16), 17)
      if self.g.progress.has(f"c:{cat}"):
        self.g.draw_star(s, (r.right - 14, r.y + 14), 9)
    self.draw_button(s, close, "Back to town", (90, 110, 150))
