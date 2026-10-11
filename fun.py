"""Extra delight for Domino Wonder Dash: particles, colour themes, trace
streaks and the sticker shelf (saved progress).

Pure pygame + standard library, so it runs the same on desktop, in the
browser (pygbag) and on Android.
"""

import json
import math
import os
import random

import pygame

from audio import IS_ANDROID, IS_WEB

# --------------------------------------------------------------------------
# Colour themes (the palette button cycles them; the choice is saved)
# --------------------------------------------------------------------------
# Each theme also has a picture-book scene behind the play area (scenery.py).
# "Sunny Day" is first, so it is what a new child sees.
THEMES = [
    {"name": "Sunny Day", "bg": (34, 108, 190), "panel": (22, 84, 156),
     "banner": (24, 80, 150), "subject": (255, 130, 40), "cat": (233, 69, 96),
     "cell": (52, 128, 200), "context": (70, 100, 150), "guide": (50, 80, 130),
     "domino_sat": 85, "domino_val": 95, "scene": "day"},
    {"name": "Night", "bg": (26, 26, 46), "panel": (15, 52, 96),
     "banner": (22, 33, 62), "subject": (120, 80, 200), "cat": (233, 69, 96),
     "cell": (53, 79, 82), "context": (70, 85, 120), "guide": (90, 100, 140),
     "domino_sat": 90, "domino_val": 85, "scene": "night"},
    {"name": "Ocean", "bg": (8, 38, 58), "panel": (6, 70, 100),
     "banner": (10, 52, 78), "subject": (0, 140, 170), "cat": (255, 120, 90),
     "cell": (30, 90, 110), "context": (60, 120, 150), "guide": (80, 140, 170),
     "domino_sat": 55, "domino_val": 100, "scene": "sea"},
    {"name": "Forest", "bg": (18, 42, 28), "panel": (30, 80, 45),
     "banner": (24, 58, 36), "subject": (90, 150, 60), "cat": (230, 150, 40),
     "cell": (50, 90, 60), "context": (80, 120, 80), "guide": (100, 140, 100),
     "domino_sat": 75, "domino_val": 95, "scene": "forest"},
    {"name": "Berry", "bg": (48, 18, 50), "panel": (90, 30, 90),
     "banner": (66, 24, 70), "subject": (200, 70, 160), "cat": (90, 160, 250),
     "cell": (90, 50, 95), "context": (130, 80, 130), "guide": (150, 100, 150),
     "domino_sat": 45, "domino_val": 100, "scene": "candy"},
    {"name": "Sunset", "bg": (58, 28, 24), "panel": (120, 50, 30),
     "banner": (84, 38, 30), "subject": (230, 110, 50), "cat": (200, 60, 110),
     "cell": (110, 60, 50), "context": (150, 90, 80), "guide": (170, 110, 90),
     "domino_sat": 100, "domino_val": 100, "scene": "sunset"},
]

# --------------------------------------------------------------------------
# Particles: sparks when dots pop, confetti when the dominoes finish
# --------------------------------------------------------------------------
CONFETTI_COLORS = [(255, 204, 0), (0, 255, 204), (255, 90, 120), (120, 160, 255),
                   (170, 255, 90), (255, 150, 40), (220, 120, 255)]


class Particle:
  __slots__ = ("x", "y", "vx", "vy", "color", "life", "max_life", "size",
               "gravity", "square", "spin")

  def __init__(self, x, y, vx, vy, color, life, size, gravity=0.0, square=False):
    self.x, self.y, self.vx, self.vy = x, y, vx, vy
    self.color = color
    self.life = self.max_life = life
    self.size = size
    self.gravity = gravity
    self.square = square
    self.spin = random.uniform(0, math.pi)


class FloatText:
  __slots__ = ("x", "y", "text", "color", "life", "max_life")

  def __init__(self, x, y, text, color, life=1.2):
    self.x, self.y, self.text, self.color = x, y, text, color
    self.life = self.max_life = life


class Particles:
  """Lightweight particle system; capped so it never slows a phone down."""

  def __init__(self, cap=450):
    self.items = []
    self.texts = []
    self.cap = cap

  def sparks(self, x, y, color, n=6, power=1.0):
    for _ in range(n):
      a = random.uniform(0, 2 * math.pi)
      sp = random.uniform(60, 170) * power
      self.items.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp, color,
                                 random.uniform(0.35, 0.65), random.uniform(2.5, 4.5)))
    self._trim()

  def confetti(self, rect, n=140):
    for _ in range(n):
      x = random.uniform(rect.left, rect.right)
      y = random.uniform(rect.top, rect.top + rect.h * 0.4)
      self.items.append(Particle(
          x, y, random.uniform(-90, 90), random.uniform(-260, -60),
          random.choice(CONFETTI_COLORS), random.uniform(1.4, 2.4),
          random.uniform(3, 6), gravity=320, square=True))
    self._trim()

  def burst(self, x, y, n=40):
    for _ in range(n):
      a = random.uniform(0, 2 * math.pi)
      sp = random.uniform(120, 320)
      self.items.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp,
                                 random.choice(CONFETTI_COLORS),
                                 random.uniform(0.6, 1.1), random.uniform(3, 5.5),
                                 gravity=120, square=random.random() < 0.5))
    self._trim()

  def text(self, x, y, text, color):
    self.texts.append(FloatText(x, y, text, color))
    del self.texts[:-3]          # never more than 3 messages at once

  def _trim(self):
    if len(self.items) > self.cap:
      del self.items[:len(self.items) - self.cap]

  def update(self, dt):
    alive = []
    for p in self.items:
      p.life -= dt
      if p.life <= 0:
        continue
      p.vy += p.gravity * dt
      p.vx *= 0.985
      p.x += p.vx * dt
      p.y += p.vy * dt
      p.spin += dt * 8
      alive.append(p)
    self.items = alive
    texts = []
    for t in self.texts:
      t.life -= dt
      if t.life > 0:
        t.y -= 40 * dt
        texts.append(t)
    self.texts = texts

  def draw(self, screen, font):
    for p in self.items:
      k = p.life / p.max_life           # shrinks and fades as it dies
      size = max(1, int(p.size * (0.4 + 0.6 * k)))
      if p.square:
        w = max(1, int(size * abs(math.cos(p.spin))) + 1)
        pygame.draw.rect(screen, p.color, (int(p.x) - w // 2, int(p.y) - size // 2,
                                           w, size))
      else:
        pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), size)
    for t in self.texts:
      k = t.life / t.max_life
      surf = font.render(t.text, True, t.color)
      surf.set_alpha(int(255 * min(1.0, k * 2)))
      screen.blit(surf, surf.get_rect(center=(int(t.x), int(t.y))))


# --------------------------------------------------------------------------
# Trace streaks: quick pops in a row climb a musical scale
# --------------------------------------------------------------------------
STREAK_GAP = 0.45   # seconds between pops that still count as one streak


class Streak:

  def __init__(self):
    self.count = 0
    self.last = -10.0

  def pop(self, now, newly):
    if now - self.last <= STREAK_GAP:
      self.count += newly
    else:
      self.count = newly
    self.last = now
    return self.count

  def active(self, now):
    return self.count if now - self.last <= STREAK_GAP * 2 else 0

  def note(self):
    """Pop sound index (0-11): climbs the scale, then sparkles at the top."""
    if self.count <= 12:
      return self.count - 1
    return 6 + (self.count % 6)


# --------------------------------------------------------------------------
# Sticker shelf: saved progress and milestone rewards
# --------------------------------------------------------------------------
MILESTONES = [
    (1, "First Trace!"), (3, "Super Three"), (5, "High Five"), (10, "Perfect Ten"),
    (20, "Twenty Stars"), (30, "Thirty Thrills"), (50, "Half Century"),
    (75, "Seventy-Five"), (100, "Century Star"), (150, "Super Learner"),
    (200, "Double Century"), (250, "Brain Builder"), (300, "Triple Century"),
]
STORAGE_KEY = "domino_wonder_dash_progress"


def _save_path():
  if os.environ.get("DOMINO_PROGRESS_FILE"):   # tests use a scratch file
    return os.environ["DOMINO_PROGRESS_FILE"]
  if IS_ANDROID:
    base = os.environ.get("ANDROID_PRIVATE") or os.getcwd()
  else:
    base = os.path.join(os.path.expanduser("~"), ".domino_wonder_dash")
  return os.path.join(base, "progress.json")


AVATARS = [("Animals", "Tiger"), ("Animals", "Elephant"), ("Animals", "Rabbit"),
           ("Birds", "Peacock"), ("Animals", "Monkey"), ("Sea", "Dolphin")]
MAX_PLAYERS = len(AVATARS)


def new_profile(n):
  return {"name": f"Player {n + 1}", "avatar": n % len(AVATARS), "done": [],
          "stickers": [], "theme": 0, "theme_v": 2, "best_streak": 0, "lang": "hi",
          "quiz": {"right": 0, "asked": 0}, "spell": {"right": 0, "words": []},
          "stories": [], "days": []}


class Progress:
  """Each child's progress: items traced, stickers, theme, language, quiz and
  spelling scores, stories and days played. Several children can share one
  device (profiles). Saved in a file on desktop/Android and in the browser's
  localStorage."""

  def __init__(self, total_items):
    self.total = total_items
    self.store = {"profiles": [new_profile(0)], "current": 0}
    self.load()

  @property
  def data(self):
    """The current child's profile."""
    return self.store["profiles"][self.store["current"]]

  # storage ------------------------------------------------------------
  def load(self):
    try:
      if IS_WEB:
        import platform
        raw = platform.window.localStorage.getItem(STORAGE_KEY)
      else:
        with open(_save_path(), encoding="utf-8") as fh:
          raw = fh.read()
      if raw:
        saved = json.loads(str(raw))
        if "profiles" not in saved:          # older single-player save
          prof = new_profile(0)
          prof.update(saved)
          saved = {"profiles": [prof], "current": 0}
        for i, prof in enumerate(saved["profiles"]):
          if prof.get("theme_v") != 2:
            # "Sunny Day" was added in front: a child who picked a theme keeps
            # it; the old default (Night) moves to the new bright default
            if prof.get("theme", 0):
              prof["theme"] = prof["theme"] + 1
            prof["theme_v"] = 2
          full = new_profile(i)
          full.update(prof)
          saved["profiles"][i] = full
        saved["current"] = min(saved.get("current", 0), len(saved["profiles"]) - 1)
        self.store = saved
    except Exception:
      pass  # first run, or storage not available: start fresh

  def save(self):
    try:
      raw = json.dumps(self.store)
      if IS_WEB:
        import platform
        platform.window.localStorage.setItem(STORAGE_KEY, raw)
      else:
        path = _save_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
          fh.write(raw)
    except Exception as exc:
      print(f"[progress] not saved: {exc}")

  # profiles -----------------------------------------------------------
  def profiles(self):
    return self.store["profiles"]

  def switch(self, index):
    self.store["current"] = index
    self.save()

  def add_profile(self):
    if len(self.profiles()) >= MAX_PLAYERS:
      return None
    used = {p["avatar"] for p in self.profiles()}
    prof = new_profile(len(self.profiles()))
    prof["avatar"] = next((i for i in range(len(AVATARS)) if i not in used), 0)
    self.profiles().append(prof)
    self.store["current"] = len(self.profiles()) - 1
    self.save()
    return prof

  def mark_day(self, day):
    if day not in self.data["days"]:
      self.data["days"].append(day)
      self.save()

  # queries ------------------------------------------------------------
  def is_done(self, key):
    return key in self._done_set()

  def _done_set(self):
    return set(self.data["done"])

  def count(self):
    return len(self.data["done"])

  def all_stickers(self, categories, story_ids=()):
    """Every sticker: milestones, all-done, one per category, one per story."""
    out = [f"m{n}" for n, _ in MILESTONES if n <= self.total]
    out.append("all")
    out += [f"c:{c}" for c in categories]
    out += [f"s:{s}" for s in story_ids]
    return out

  def has(self, sticker):
    return sticker in self.data["stickers"]

  # updates ------------------------------------------------------------
  def complete(self, key, cat_keys, cat):
    """Marks an item done; returns the list of newly earned stickers."""
    new = []
    if key not in self._done_set():
      self.data["done"].append(key)
    n = self.count()
    for need, _ in MILESTONES:
      sid = f"m{need}"
      if n >= need and need <= self.total and not self.has(sid):
        new.append(sid)
    if n >= self.total and not self.has("all"):
      new.append("all")
    done = self._done_set()
    if all(k in done for k in cat_keys) and not self.has(f"c:{cat}"):
      new.append(f"c:{cat}")
    self.data["stickers"] += new
    self.save()
    return new

  def finish_story(self, story_id):
    if story_id not in self.data["stories"]:
      self.data["stories"].append(story_id)
    sid = f"s:{story_id}"
    new = [] if self.has(sid) else [sid]
    self.data["stickers"] += new
    self.save()
    return new

  def quiz_answer(self, right):
    q = self.data["quiz"]
    q["asked"] += 1
    q["right"] += 1 if right else 0
    self.save()

  def spelled(self, word):
    s = self.data["spell"]
    s["right"] += 1
    if word not in s["words"]:
      s["words"].append(word)
    self.save()

  def note_streak(self, streak):
    if streak > self.data.get("best_streak", 0):
      self.data["best_streak"] = streak
      return True
    return False


STORY_TITLES = {}   # filled by main.py from stories.py


def sticker_title(sid):
  if sid == "all":
    return "Grand Champion"
  if sid.startswith("s:"):
    return STORY_TITLES.get(sid[2:], "Story Star")
  if sid.startswith("m"):
    need = int(sid[1:])
    return dict(MILESTONES)[need]
  return f"{sid[2:]} Master"


def sticker_need(sid, total, cat_size=0):
  if sid == "all":
    return f"Trace all {total}"
  if sid.startswith("s:"):
    return "Finish the story"
  if sid.startswith("m"):
    return f"Trace {sid[1:]}"
  return f"Finish all {cat_size}"


def draw_sticker(screen, center, radius, sid, earned, font, picture=None, t=0.0):
  """A round star-burst badge. Locked stickers are grey with a '?'."""
  cx, cy = center
  seed = sum(ord(c) for c in sid)
  hue = (seed * 47) % 360
  base = pygame.Color(0)
  base.hsva = (hue, 70 if earned else 0, 95 if earned else 45, 100)
  rim = pygame.Color(0)
  rim.hsva = (hue, 90 if earned else 0, 70 if earned else 35, 100)
  pts = []
  spikes = 12
  for i in range(spikes * 2):
    a = math.pi * i / spikes + t
    r = radius if i % 2 == 0 else radius * 0.82
    pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
  pygame.draw.polygon(screen, rim, pts)
  pygame.draw.circle(screen, base, center, int(radius * 0.74))
  pygame.draw.circle(screen, (255, 255, 255) if earned else (120, 120, 120),
                     center, int(radius * 0.74), 2)
  if not earned:
    q = font.render("?", True, (200, 200, 200))
    screen.blit(q, q.get_rect(center=center))
    return
  if picture is not None:
    screen.blit(picture, picture.get_rect(center=center))
  elif sid == "all" or sid.startswith("c:"):
    star = []
    for i in range(10):
      r = radius * (0.55 if i % 2 == 0 else 0.24)
      a = -math.pi / 2 + i * math.pi / 5
      star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(screen, (255, 215, 0), star)
  else:
    label = sid[1:] if sid.startswith("m") else "?"
    num = font.render(label, True, (40, 30, 60))
    screen.blit(num, num.get_rect(center=center))
