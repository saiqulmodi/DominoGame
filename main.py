"""Domino Wonder Dash - children learn by tracing, toppling and listening.

1. Pick a subject, a category and an item (all from the Picture Data Hub).
2. Trace the dotted outline with a finger or the mouse; each dot pops.
3. Dominoes stand up on the outline - tap and watch them fall.
4. The real picture appears and the name is said, spelled and shown.
5. Sparks, streaks, colour themes and a sticker shelf keep it exciting.

Runs on desktop (python main.py), in mobile/desktop browsers (pygbag) and on
Android (buildozer). See BUILD_MOBILE.md.
"""

import asyncio
import math
import os
import time

import pygame

import domino_data as hub
import fun
from audio import IS_ANDROID, IS_WEB, SoundBank, Speaker

# Virtual 9:16 portrait canvas. Everything is drawn here, then scaled to fit
# the real window / phone screen with letterboxing.
WIDTH, HEIGHT = 450, 800

SUBJ_RECT = pygame.Rect(0, 0, WIDTH, 40)
CAT_RECT = pygame.Rect(0, 40, WIDTH, 38)
BANNER_RECT = pygame.Rect(8, 82, WIDTH - 16, 66)
SPEAKER_CENTER = (BANNER_RECT.right - 28, BANNER_RECT.centery)
SPEAKER_R = 21
DESC_Y = 151
PLAY_RECT = pygame.Rect(0, 188, WIDTH, 408)
BANK_RECT = pygame.Rect(0, 598, WIDTH, 150)
RESET_RECT = pygame.Rect(8, HEIGHT - 48, 124, 42)
STICKER_RECT = pygame.Rect(138, HEIGHT - 48, 110, 42)
THEME_RECT = pygame.Rect(254, HEIGHT - 48, 56, 42)
NEXT_RECT = pygame.Rect(316, HEIGHT - 48, 126, 42)
BANK_COLS, BANK_ROWS = 4, 2

# Colors (backgrounds and panels come from the chosen theme in fun.THEMES)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
CYAN = (0, 255, 204)
PINK = (233, 69, 96)
PURPLE = (120, 80, 200)
GOLD = (255, 215, 0)
HINT = (170, 180, 210)

CUSTOM = "Custom Draw"
TRACE_RADIUS = 24      # how close the finger must pass to cover a dot
TRACE_DONE = 0.95      # share of dots that completes the outline

# Spelling animation timing, measured from the Windows voice at rate -2:
# name at ~0.1 s, then one letter every ~0.82 s starting at ~1.7 s.
SPELL_START = 1.7
SPELL_STEP = 0.82

RATE_HINT = 44100  # mixer output rate; effects are resampled to it


class Domino:

  def __init__(self, x, y, angle, color):
    self.x = x
    self.y = y
    self.angle = angle
    self.current_angle = 0.0
    self.state = "standing"
    self.color = color


def dominoes_from_loops(loops, closed, sat=90, val=85):
  domino_list = []
  total = sum(len(lp) for lp in loops)
  i = 0
  for lp in loops:
    for j, p in enumerate(lp):
      if j + 1 < len(lp):
        nxt = lp[j + 1]
      elif closed and len(lp) > 2:
        nxt = lp[0]
      else:
        nxt = None
      if nxt is not None:
        angle = math.atan2(nxt[1] - p[1], nxt[0] - p[0]) + math.pi / 2
      else:
        angle = domino_list[-1].angle if domino_list else 0
      color = pygame.Color(0)
      color.hsva = (int(i * 360 / max(1, total)) % 360, sat, val, 100)
      domino_list.append(Domino(p[0], p[1], angle, color))
      i += 1
  return domino_list


def wrap_text(font, text, max_w):
  lines, line = [], ""
  for word in text.split():
    trial = f"{line} {word}".strip()
    if font.size(trial)[0] <= max_w or not line:
      line = trial
    else:
      lines.append(line)
      line = word
  if line:
    lines.append(line)
  return lines


def fit_label(font, text, color, max_w):
  lbl = font.render(text, True, color)
  if lbl.get_width() > max_w:
    lbl = pygame.transform.smoothscale(
        lbl, (int(max_w), max(1, int(lbl.get_height() * max_w / lbl.get_width()))))
  return lbl


class Game:

  def __init__(self, sfx, speaker):
    self.sfx = sfx
    self.speaker = speaker
    self.subjects = hub.subjects()
    self.subject = next(iter(self.subjects))
    self.cat = self.subjects[self.subject][0]
    self.page = 0
    self.puzzle = list(hub.CATEGORIES_HUB[self.cat].keys())[0]

    self.font = pygame.font.SysFont("Comic Sans MS", 15)
    self.small_font = pygame.font.SysFont("Comic Sans MS", 12, bold=True)
    self.cat_font = pygame.font.SysFont("Comic Sans MS", 13, bold=True)
    self.hint_font = pygame.font.SysFont("Comic Sans MS", 17, bold=True)
    self.big_font = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
    self.tile_fonts = {}
    self.images = {}

    # Delight: saved progress + stickers, theme, particles, trace streaks
    total = sum(len(v) for v in hub.CATEGORIES_HUB.values())
    self.progress = fun.Progress(total)
    self.theme = fun.THEMES[self.progress.data.get("theme", 0) % len(fun.THEMES)]
    self.particles = fun.Particles()
    self.streak = fun.Streak()
    self.shelf_open = False
    self.celebration = None      # (sticker id, start time)
    self.last_tick = time.time()

    self.load_item(announce=True)

  # ------------------------------------------------------------ item state
  @property
  def is_custom(self):
    return self.puzzle == CUSTOM

  def load_item(self, announce=True):
    """(Re)start the current item at the tracing stage."""
    self.stage = "draw" if self.is_custom else "trace"
    self.user_points = []
    self.strokes = []
    self.last_pointer = None
    self.dominoes = []
    self.finished_at = 0.0
    self.praised_at = -10.0
    self.celebration = None
    if hasattr(self, "particles"):
      self.particles.texts = []
    box =PLAY_RECT.inflate(-16, -40)
    self.box = (box.x, box.y, box.w, box.h)
    if self.is_custom:
      self.closed = False
      self.dots, self.covered = [], []
      self.context = []
      self.pic_path = self.pic_rect = None
    else:
      self.closed = hub.CATEGORIES_HUB[self.cat][self.puzzle].get("closed", True)
      self.loops = hub.fetch_path_from_hub(self.puzzle, self.box, cat=self.cat)
      self.dots = [p for lp in self.loops for p in lp]
      self.covered = [False] * len(self.dots)
      self.context = hub.fetch_context_from_hub(self.puzzle, self.box, cat=self.cat)
      self.pic_path, self.pic_rect = hub.fetch_picture_from_hub(
          self.puzzle, self.box, cat=self.cat)
    if announce:
      self.announce()

  def announce(self):
    self.announced_at = time.time()
    self.speaker.say(hub.spoken_text(self.puzzle, self.cat),
                     hindi=hub.hindi_speech(self.puzzle, self.cat))

  def key(self, name=None, cat=None):
    return hub.item_key(cat or self.cat, name or self.puzzle)

  def stand_dominoes(self, loops):
    self.dominoes = dominoes_from_loops(loops, self.closed, self.theme["domino_sat"],
                                        self.theme["domino_val"])
    self.stage = "ready"
    self.strokes = []
    self.sfx.play("switch")

  def start_cascade(self):
    if not self.dominoes:
      return
    for d in self.dominoes:
      d.state = "standing"
      d.current_angle = 0.0
    self.stage = "running"
    self.dominoes[0].state = "falling"
    self.sfx.play("tip")

  # ------------------------------------------------------------ navigation
  def items(self):
    return list(hub.CATEGORIES_HUB[self.cat].keys())

  def select_subject(self, subj):
    self.sfx.play("switch")
    self.subject = subj
    self.select_category(self.subjects[subj][0], sound=False)

  def select_category(self, cat, sound=True):
    if sound:
      self.sfx.play("switch")
    self.cat = cat
    self.page = 0
    self.puzzle = self.items()[0]
    self.load_item()

  def select_puzzle(self, name):
    self.sfx.play("click")
    self.puzzle = name
    self.load_item()

  def next_item(self):
    """Next item; moves on to the next category and subject at the end."""
    order = [(s, c, n) for s, cats in self.subjects.items() for c in cats
             for n in hub.CATEGORIES_HUB[c]]
    idx = order.index((self.subject, self.cat, self.puzzle))
    self.subject, self.cat, self.puzzle = order[(idx + 1) % len(order)]
    per = self.per_page()
    self.page = self.items().index(self.puzzle) // per if per else 0
    self.sfx.play("click")
    self.load_item()

  def per_page(self):
    cells = BANK_COLS * BANK_ROWS
    return cells if len(self.items()) <= cells else cells - 1

  # ------------------------------------------------------------ layout
  def subject_rects(self):
    subs = list(self.subjects)
    w = WIDTH / len(subs)
    return [(pygame.Rect(int(i * w) + 2, 4, int(w) - 4, 32), s)
            for i, s in enumerate(subs)]

  def category_rects(self):
    cats = self.subjects[self.subject]
    w = WIDTH / len(cats)
    return [(pygame.Rect(int(i * w) + 3, 44, int(w) - 6, 30), c)
            for i, c in enumerate(cats)]

  def bank_cells(self):
    """[(rect, item name or '>more')] for the current page of items."""
    items = self.items()
    per = self.per_page()
    pages = max(1, math.ceil(len(items) / per))
    self.page %= pages
    shown = items[self.page * per:(self.page + 1) * per]
    cells = [(name) for name in shown]
    if pages > 1:
      cells.append(">more")
    cw = WIDTH / BANK_COLS
    ch = (BANK_RECT.h - 8) / BANK_ROWS
    out = []
    for i, name in enumerate(cells):
      r, c = divmod(i, BANK_COLS)
      rect = pygame.Rect(int(c * cw) + 4, int(BANK_RECT.y + 4 + r * ch) + 2,
                         int(cw) - 8, int(ch) - 4)
      out.append((rect, name))
    return out, pages

  # ------------------------------------------------------------ input
  def press(self, pos):
    mx, my = pos
    if self.shelf_open:          # any tap closes the sticker shelf
      self.shelf_open = False
      self.sfx.play("click")
      return
    if SUBJ_RECT.collidepoint(mx, my):
      for rect, s in self.subject_rects():
        if rect.collidepoint(mx, my) and s != self.subject:
          self.select_subject(s)
    elif CAT_RECT.collidepoint(mx, my):
      for rect, c in self.category_rects():
        if rect.collidepoint(mx, my) and c != self.cat:
          self.select_category(c)
    elif BANNER_RECT.collidepoint(mx, my):
      # Tap the name (or speaker) to hear it again
      self.sfx.play("click")
      self.announce()
    elif BANK_RECT.collidepoint(mx, my):
      cells, _ = self.bank_cells()
      for rect, name in cells:
        if rect.collidepoint(mx, my):
          if name == ">more":
            self.sfx.play("switch")
            self.page += 1
          else:
            self.select_puzzle(name)
          break
    elif RESET_RECT.collidepoint(mx, my):
      self.sfx.play("click")
      self.load_item()
    elif NEXT_RECT.collidepoint(mx, my):
      self.next_item()
    elif STICKER_RECT.collidepoint(mx, my):
      self.sfx.play("switch")
      self.shelf_open = True
    elif THEME_RECT.collidepoint(mx, my):
      self.next_theme()
    elif PLAY_RECT.collidepoint(mx, my):
      if (self.stage == "finished" and self.celebration
          and time.time() - self.celebration[1] < 0.8):
        return                   # don't skip the new sticker by accident
      if self.stage == "draw":
        self.user_points = [(mx, my)]
        self.drawing = True
        self.stroke_since_sound = 0.0
        self.sfx.play("pencil")
      elif self.stage == "trace":
        self.last_pointer = (mx, my)
        self.strokes.append([(mx, my)])
        self.cover_along((mx, my), (mx, my))
      elif self.stage == "ready":
        self.start_cascade()
      elif self.stage == "finished":
        self.sfx.play("click")
        self.load_item(announce=False)  # play again, endlessly

  def drag(self, pos):
    mx, my = pos
    if self.stage == "draw" and self.user_points:
      if PLAY_RECT.collidepoint(mx, my):
        last = self.user_points[-1]
        self.stroke_since_sound += math.hypot(mx - last[0], my - last[1])
        self.user_points.append((mx, my))
        if self.stroke_since_sound >= 22:
          self.stroke_since_sound = 0.0
          self.sfx.play("pencil")
    elif self.stage == "trace" and self.last_pointer is not None:
      self.cover_along(self.last_pointer, (mx, my))
      self.last_pointer = (mx, my)
      if self.strokes:
        self.strokes[-1].append((mx, my))

  def release(self, pos):
    if self.stage == "draw" and self.user_points:
      if len(self.user_points) > 2:
        loops = hub.fetch_path_from_hub(CUSTOM, self.box, self.user_points)
        if loops:
          self.dots = [p for lp in loops for p in lp]
          self.covered = [True] * len(self.dots)
          self.stand_dominoes(loops)
      self.user_points = [] if self.stage == "draw" else self.user_points
    self.last_pointer = None

  def next_theme(self):
    idx = (fun.THEMES.index(self.theme) + 1) % len(fun.THEMES)
    self.theme = fun.THEMES[idx]
    self.progress.data["theme"] = idx
    self.progress.save()
    if self.dominoes:            # recolour dominoes already standing
      for d, nd in zip(self.dominoes, dominoes_from_loops(
          [[(d.x, d.y) for d in self.dominoes]], False,
          self.theme["domino_sat"], self.theme["domino_val"])):
        d.color = nd.color
    self.sfx.play("switch")
    self.particles.text(THEME_RECT.centerx, THEME_RECT.top - 14,
                        self.theme["name"], YELLOW)

  def dot_color(self, i):
    color = pygame.Color(0)
    color.hsva = (int(i * 360 / max(1, len(self.dots))) % 360, 85, 100, 100)
    return color

  def cover_along(self, a, b):
    """Covers every dot near the finger's path from a to b."""
    steps = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) // 6))
    r2 = TRACE_RADIUS * TRACE_RADIUS
    newly = []
    for s in range(steps + 1):
      t = s / steps
      px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
      for i, (dx, dy) in enumerate(self.dots):
        if not self.covered[i] and (dx - px) ** 2 + (dy - py) ** 2 <= r2:
          self.covered[i] = True
          newly.append(i)
    if newly:
      done = sum(self.covered)
      # Streak: quick pops in a row climb a musical scale and grow the trail
      now = time.time()
      before = self.streak.count if now - self.streak.last <= fun.STREAK_GAP else 0
      count = self.streak.pop(now, len(newly))
      self.sfx.play("pop", self.streak.note())
      power = 1.0 + min(1.5, count / 20)
      for i in newly[:4]:
        dx, dy = self.dots[i]
        self.particles.sparks(dx, dy, self.dot_color(i), n=5, power=power)
      if count // 10 > before // 10:          # every 10 in a row
        x, y = self.dots[newly[-1]]
        self.particles.text(x, y - 24, f"Streak x{count // 10 * 10}!", YELLOW)
        self.particles.burst(x, y, n=24)
      self.progress.note_streak(count)
      if done >= len(self.dots) * TRACE_DONE:
        self.covered = [True] * len(self.dots)
        self.stand_dominoes(self.loops)

  # ------------------------------------------------------------ physics
  def update(self):
    now = time.time()
    dt = min(0.05, now - self.last_tick)
    self.last_tick = now
    self.particles.update(dt)
    if self.celebration and now - self.celebration[1] > 3.5:
      self.celebration = None
    if self.stage != "running":
      return
    for i, d in enumerate(self.dominoes):
      if d.state == "falling":
        d.current_angle += 0.12
        if (
            d.current_angle > 0.3
            and i + 1 < len(self.dominoes)
            and self.dominoes[i + 1].state == "standing"
        ):
          self.dominoes[i + 1].state = "falling"
        if d.current_angle >= math.pi / 2:
          d.current_angle = math.pi / 2
          d.state = "fallen"
          self.sfx.play("clack", i)
    if all(d.state == "fallen" for d in self.dominoes):
      self.stage = "finished"
      self.finished_at = time.time()
      self.sfx.play("chime")
      self.praised_at = time.time()
      self.particles.confetti(PLAY_RECT)
      cat_keys = [self.key(n) for n in hub.CATEGORIES_HUB[self.cat]]
      new = self.progress.complete(self.key(), cat_keys, self.cat)
      praise = hub.praise_text(self.puzzle, self.cat)
      if new:
        self.celebration = (new[-1], time.time())
        self.particles.burst(PLAY_RECT.centerx, PLAY_RECT.centery, n=60)
        praise += " You got a new sticker!"
      self.speaker.say(praise,
                       hindi=hub.hindi_speech(self.puzzle, self.cat, praise=True))

  # ------------------------------------------------------------ drawing
  def image(self, path, size=None):
    """Loads (and caches) a picture, optionally scaled to size."""
    if not path:
      return None
    key = (path, size)
    if key not in self.images:
      try:
        base = self.images.get((path, None))
        if base is None:
          base = pygame.image.load(path).convert_alpha()
          self.images[(path, None)] = base
        if size:
          base = pygame.transform.smoothscale(base, size)
        self.images[key] = base
      except Exception:
        self.images[key] = None
    return self.images[key]

  def thumb(self, name, cat, max_size):
    path = hub.fetch_thumb_from_hub(name, cat)
    img = self.image(path)
    if img is None:
      return None
    w, h = img.get_size()
    s = min(max_size / w, max_size / h)
    return self.image(path, (max(1, int(w * s)), max(1, int(h * s))))

  def tile_font(self, size):
    if size not in self.tile_fonts:
      self.tile_fonts[size] = (
          pygame.font.SysFont("Comic Sans MS", size, bold=True),
          pygame.font.SysFont("Arial", size, bold=True),  # for - x / and Rupee
      )
    return self.tile_fonts[size]

  def render_char(self, ch, size, color):
    main, fallback = self.tile_font(size)
    metrics = main.metrics(ch)
    font = main if metrics and metrics[0] is not None else fallback
    return font.render(ch, True, color)

  def draw_title_banner(self, screen, now):
    pygame.draw.rect(screen, self.theme["banner"], BANNER_RECT, border_radius=14)
    pygame.draw.rect(screen, YELLOW, BANNER_RECT, 2, border_radius=14)

    # Real picture at the left of the name
    x_start = BANNER_RECT.x + 10
    th = self.thumb(self.puzzle, self.cat, 52)
    if th is not None:
      screen.blit(th, th.get_rect(center=(BANNER_RECT.x + 34, BANNER_RECT.centery)))
      x_start = BANNER_RECT.x + 64

    # Hindi letters: the word ("अ से अनार") is a ready-made picture, so it
    # shows correctly even on phones and browsers without Hindi fonts.
    item = hub.CATEGORIES_HUB[self.cat][self.puzzle]
    if item.get("word_img"):
      word = self.image(os.path.join(hub.HERE, item["word_img"]))
      if word is not None:
        avail_w = SPEAKER_CENTER[0] - SPEAKER_R - 10 - x_start
        avail_h = BANNER_RECT.h - 12
        if now - self.praised_at < 2.5:  # glow on "Well done"
          pygame.draw.rect(screen, YELLOW, BANNER_RECT, 5, border_radius=14)
        s =min(avail_w / word.get_width(), avail_h / word.get_height())
        size = (max(1, int(word.get_width() * s)), max(1, int(word.get_height() * s)))
        word = self.image(os.path.join(hub.HERE, item["word_img"]), size)
        screen.blit(word, word.get_rect(center=(x_start + avail_w / 2,
                                                BANNER_RECT.centery)))
      self.draw_speaker(screen)
      return

    name = self.puzzle
    gap = 3
    avail = SPEAKER_CENTER[0] - SPEAKER_R - 8 - x_start
    units = sum(0.5 if ch == " " else 1 for ch in name)
    tile_w = int(min(44, (avail - gap * (len(name) - 1)) / units))
    tile_h = min(54, int(tile_w * 1.3))
    total_w = sum(tile_w // 2 if ch == " " else tile_w for ch in name)
    total_w += gap * (len(name) - 1)
    x = x_start + (avail - total_w) / 2
    base_y = BANNER_RECT.centery - tile_h / 2

    elapsed = now - self.announced_at
    spelling = not self.is_custom
    active = int((elapsed - SPELL_START) // SPELL_STEP) if spelling else -1
    n_letters = sum(1 for ch in name if ch != " ")
    letter_idx = 0
    praising = now - self.praised_at < 2.5
    screen.set_clip(BANNER_RECT.inflate(-4, -4))
    for i, ch in enumerate(name):
      if ch == " ":
        x += tile_w // 2 + gap
        continue
      # Tiles drop in one after another, then light up as each letter is said
      drop = max(0.0, 1.0 - (elapsed - i * 0.05) / 0.25)
      y = base_y - drop * 30
      lit = praising or (elapsed >= SPELL_START and (
          letter_idx == active or n_letters <= active < n_letters + 2))
      color = pygame.Color(0)
      color.hsva = ((i * 360 // max(1, len(name))) % 360, 70, 95, 100)
      rect = pygame.Rect(int(x), int(y - (7 if lit else 0)), tile_w, tile_h)
      pygame.draw.rect(screen, YELLOW if lit else color, rect, border_radius=7)
      pygame.draw.rect(screen, WHITE, rect, 2, border_radius=7)
      lbl = self.render_char(ch, max(12, int(tile_h * 0.62)), self.theme["bg"])
      screen.blit(lbl, lbl.get_rect(center=rect.center))
      x += tile_w + gap
      letter_idx += 1
    screen.set_clip(None)
    self.draw_speaker(screen)

  def draw_speaker(self, screen):
    """Speaker icon (tap to hear the name again)."""
    cx, cy = SPEAKER_CENTER
    bg = self.theme["bg"]
    pygame.draw.circle(screen, CYAN, SPEAKER_CENTER, SPEAKER_R)
    pygame.draw.rect(screen, bg, (cx - 11, cy - 5, 6, 10))
    pygame.draw.polygon(
        screen, bg,
        [(cx - 6, cy - 5), (cx + 2, cy - 12), (cx + 2, cy + 12), (cx - 6, cy + 5)],
    )
    for r in (7, 12):
      pygame.draw.arc(
          screen, bg, (cx + 2 - r, cy - r, 2 * r, 2 * r),
          -math.pi / 4, math.pi / 4, 2,
      )

  def hint_text(self):
    if self.stage == "draw":
      return "Draw anything with your finger!"
    if self.stage == "trace":
      return f"Trace the dots!  {sum(self.covered)} / {len(self.dots)}"
    if self.stage == "ready":
      return "Tap to push the dominoes!"
    if self.stage == "finished":
      return "Yay! Tap to play again, or Next"
    return ""

  def draw_play_area(self, screen, now):
    screen.set_clip(PLAY_RECT)

    for line in self.context:
      if len(line) > 1:
        pygame.draw.lines(screen, self.theme["context"], False, line, 1)

    # The real picture: a faint guide while tracing, full colour at the end
    if self.pic_path and self.pic_rect:
      x, y, w, h = self.pic_rect
      img = self.image(self.pic_path, (max(1, int(w)), max(1, int(h))))
      if img is not None:
        if self.stage == "finished":
          alpha = int(70 + 185 * min(1.0, (now - self.finished_at) / 1.0))
        elif self.stage == "trace":
          alpha = 70
        else:
          alpha = 45
        img.set_alpha(alpha)
        screen.blit(img, (x, y))

    if self.stage == "trace":
      # Dotted outline: faint guide line, hollow dots, filled when covered
      for lp_start in self._loop_slices():
        pts = self.dots[lp_start[0]:lp_start[1]]
        if len(pts) > 1:
          pygame.draw.lines(screen, self.theme["guide"], self.closed, pts, 1)
      # Trail grows thicker and glows while a streak is going
      streak = self.streak.active(now)
      width = 4 + min(8, streak // 3)
      glow = pygame.Color(0)
      glow.hsva = ((now * 240) % 360, 80, 100, 100)
      for k, stroke in enumerate(self.strokes):
        if len(stroke) > 1:
          live = k == len(self.strokes) - 1 and streak >= 6
          if live:
            pulse = width + 6 + int(3 * math.sin(now * 14))
            pygame.draw.lines(screen, glow, False, stroke[-40:], pulse)
          pygame.draw.lines(screen, YELLOW, False, stroke, width if live else 4)
      first_open = next((i for i, c in enumerate(self.covered) if not c), None)
      for i, (dx, dy) in enumerate(self.dots):
        if self.covered[i]:
          pygame.draw.circle(screen, self.dot_color(i), (int(dx), int(dy)), 6)
        else:
          pygame.draw.circle(screen, WHITE, (int(dx), int(dy)), 5, 2)
      if first_open is not None and not any(self.covered):
        fx, fy = self.dots[first_open]
        r = 13 + 4 * math.sin(now * 6)
        pygame.draw.circle(screen, YELLOW, (int(fx), int(fy)), int(r), 2)

    if self.stage == "draw" and len(self.user_points) > 1:
      pygame.draw.lines(screen, YELLOW, False, self.user_points, 3)

    if self.stage in ("ready", "running", "finished"):
      if self.stage == "ready" and self.dominoes:
        r = 15 + 4 * math.sin(now * 6)
        pygame.draw.circle(screen, YELLOW, (int(self.dominoes[0].x),
                                            int(self.dominoes[0].y)), int(r), 2)
      for d in self.dominoes:
        surf = pygame.Surface((10, 26), pygame.SRCALPHA)
        surf.fill(d.color)
        pygame.draw.rect(surf, WHITE, (0, 0, 10, 26), 1)
        rotated = pygame.transform.rotate(
            surf, math.degrees(-(d.angle + d.current_angle)))
        if self.stage == "finished":
          rotated.set_alpha(110)
        screen.blit(rotated, rotated.get_rect(center=(d.x, d.y)))

    hint = self.hint_text()
    streak = self.streak.active(now) if self.stage == "trace" else 0
    if streak >= 5:
      hint = f"Streak {streak}!  " + hint
    if hint:
      surf = self.hint_font.render(hint, True, YELLOW if streak >= 5 else HINT)
      screen.blit(surf, surf.get_rect(center=(WIDTH / 2, PLAY_RECT.bottom - 14)))
    if self.celebration:
      self.draw_celebration(screen, now)
    screen.set_clip(None)

  def sticker_picture(self, sid, size):
    """Category stickers show the category's first picture."""
    if sid.startswith("c:"):
      cat = sid[2:]
      if cat in hub.CATEGORIES_HUB:
        first = next(iter(hub.CATEGORIES_HUB[cat]))
        return self.thumb(first, cat, size)
    return None

  def draw_celebration(self, screen, now):
    sid, start = self.celebration
    t = now - start
    grow = min(1.0, t / 0.35)
    radius = int(70 * (0.3 + 0.7 * grow) * (1 + 0.05 * math.sin(now * 8)))
    cx, cy = PLAY_RECT.centerx, PLAY_RECT.centery - 30
    shade = pygame.Surface(PLAY_RECT.size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, 110))
    screen.blit(shade, PLAY_RECT.topleft)
    fun.draw_sticker(screen, (cx, cy), radius, sid, True, self.big_font,
                     self.sticker_picture(sid, int(radius * 1.0)), t=now * 0.6)
    for text, y, font in (("New sticker!", cy - radius - 26, self.big_font),
                          (fun.sticker_title(sid), cy + radius + 22, self.hint_font)):
      surf = font.render(text, True, YELLOW)
      screen.blit(surf, surf.get_rect(center=(cx, y)))

  def draw_shelf(self, screen, now):
    """Sticker shelf: every sticker, earned ones in colour."""
    area = pygame.Rect(0, 0, WIDTH, STICKER_RECT.top - 6)
    shade = pygame.Surface(area.size, pygame.SRCALPHA)
    shade.fill((*self.theme["bg"], 240))
    screen.blit(shade, area.topleft)
    title = self.big_font.render("My Sticker Shelf", True, YELLOW)
    screen.blit(title, title.get_rect(center=(WIDTH / 2, 26)))
    info = (f"Traced {self.progress.count()} of {self.progress.total}   "
            f"Best streak {self.progress.data.get('best_streak', 0)}")
    surf = self.font.render(info, True, CYAN)
    screen.blit(surf, surf.get_rect(center=(WIDTH / 2, 56)))
    cats = [c for cs in self.subjects.values() for c in cs]
    stickers = self.progress.all_stickers(cats)
    cols = 6
    cw = WIDTH / cols
    ch = (area.h - 110) / math.ceil(len(stickers) / cols)
    r = int(min(cw, ch) * 0.34)
    for i, sid in enumerate(stickers):
      row, col = divmod(i, cols)
      cx = int(col * cw + cw / 2)
      cy = int(84 + row * ch + r)
      earned = self.progress.has(sid)
      fun.draw_sticker(screen, (cx, cy), r, sid, earned, self.small_font,
                       self.sticker_picture(sid, int(r * 1.0)) if earned else None)
      if sid.startswith("c:"):
        size = len(hub.CATEGORIES_HUB.get(sid[2:], {}))
        label = sid[2:] if earned else fun.sticker_need(sid, self.progress.total, size)
      else:
        label = (fun.sticker_title(sid) if earned
                 else fun.sticker_need(sid, self.progress.total))
      lbl = fit_label(self.small_font, label, WHITE if earned else HINT, cw - 4)
      screen.blit(lbl, lbl.get_rect(center=(cx, cy + r + 8)))
    tip = self.small_font.render("Tap anywhere to go back", True, HINT)
    screen.blit(tip, tip.get_rect(center=(WIDTH / 2, area.bottom - 10)))

  def _loop_slices(self):
    out, start = [], 0
    for lp in getattr(self, "loops", []):
      out.append((start, start + len(lp)))
      start += len(lp)
    return out

  def draw(self, screen):
    now = time.time()
    tm = self.theme
    bg = tm["bg"]
    screen.fill(bg)
    self.draw_play_area(screen, now)

    # Subjects (top row) and their categories (second row)
    pygame.draw.rect(screen, tm["panel"], SUBJ_RECT.union(CAT_RECT))
    for rect, s in self.subject_rects():
      active = s == self.subject
      pygame.draw.rect(screen, YELLOW if active else tm["subject"], rect, border_radius=8)
      lbl = fit_label(self.cat_font, s, bg if active else WHITE, rect.w - 4)
      screen.blit(lbl, lbl.get_rect(center=rect.center))
    for rect, c in self.category_rects():
      active = c == self.cat
      pygame.draw.rect(screen, CYAN if active else tm["cat"], rect, border_radius=8)
      lbl = fit_label(self.cat_font, c, bg if active else WHITE, rect.w - 4)
      screen.blit(lbl, lbl.get_rect(center=rect.center))
      if self.progress.has(f"c:{c}"):          # whole category finished
        pygame.draw.circle(screen, GOLD, (rect.right - 5, rect.top + 5), 5)

    self.draw_title_banner(screen, now)

    # Description (from the Data Hub)
    desc = hub.CATEGORIES_HUB[self.cat][self.puzzle]["desc"]
    for n, line in enumerate(wrap_text(self.font, desc, WIDTH - 24)[:2]):
      surf = self.font.render(line, True, CYAN)
      screen.blit(surf, surf.get_rect(midtop=(WIDTH / 2, DESC_Y + n * 17)))

    # Item bank: picture + name, with "More" when a category has many items
    pygame.draw.rect(screen, tm["panel"], BANK_RECT)
    cells, pages = self.bank_cells()
    for rect, name in cells:
      if name == ">more":
        pygame.draw.rect(screen, PURPLE, rect, border_radius=8)
        lbl = self.hint_font.render("More >", True, WHITE)
        screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.centery - 8)))
        pg = self.small_font.render(f"{self.page + 1} / {pages}", True, WHITE)
        screen.blit(pg, pg.get_rect(center=(rect.centerx, rect.centery + 14)))
        continue
      active = self.puzzle == name
      pygame.draw.rect(screen, CYAN if active else tm["cell"], rect, border_radius=8)
      th = self.thumb(name, self.cat, rect.h - 24)
      if th is not None:
        screen.blit(th, th.get_rect(center=(rect.centerx, rect.y + (rect.h - 18) / 2 + 2)))
      elif name == CUSTOM:
        pygame.draw.circle(screen, YELLOW, (rect.centerx, rect.y + 26), 14, 3)
      label = hub.CATEGORIES_HUB[self.cat][name].get("label", name)  # Hindi: "ka"
      lbl = fit_label(self.small_font, label, bg if active else WHITE, rect.w - 6)
      screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.bottom - 10)))
      if self.progress.is_done(self.key(name)):  # gold star = already traced
        self.draw_star(screen, (rect.right - 10, rect.top + 10), 8)

    # Reset, Stickers, Theme and Next
    pygame.draw.rect(screen, (255, 100, 100), RESET_RECT, border_radius=10)
    lbl = self.hint_font.render("Reset", True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=RESET_RECT.center))
    pygame.draw.rect(screen, (230, 160, 20), STICKER_RECT, border_radius=10)
    self.draw_star(screen, (STICKER_RECT.x + 20, STICKER_RECT.centery), 11)
    lbl = self.hint_font.render(str(len(self.progress.data["stickers"])), True, WHITE)
    screen.blit(lbl, lbl.get_rect(midleft=(STICKER_RECT.x + 36, STICKER_RECT.centery)))
    pygame.draw.rect(screen, tm["subject"], THEME_RECT, border_radius=10)
    for k, col in enumerate(((255, 90, 120), (255, 204, 0), (0, 220, 180), (120, 160, 255))):
      a = k * math.pi / 2 + now * 0.5
      pygame.draw.circle(screen, col, (int(THEME_RECT.centerx + 9 * math.cos(a)),
                                       int(THEME_RECT.centery + 9 * math.sin(a))), 6)
    pygame.draw.rect(screen, (60, 180, 90), NEXT_RECT, border_radius=10)
    lbl = self.hint_font.render("Next >", True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=NEXT_RECT.center))

    self.particles.draw(screen, self.hint_font)
    if self.shelf_open:
      self.draw_shelf(screen, now)

  def draw_star(self, screen, center, r):
    cx, cy = center
    pts = []
    for i in range(10):
      rad = r if i % 2 == 0 else r * 0.45
      a = -math.pi / 2 + i * math.pi / 5
      pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(screen, GOLD, pts)
    pygame.draw.polygon(screen, (150, 100, 0), pts, 1)


class Viewport:
  """Scales the virtual canvas onto the real screen and maps input back."""

  def __init__(self):
    self.scale = 1.0
    self.ox = self.oy = 0

  def fit(self, window_size):
    ww, wh = window_size
    self.scale = min(ww / WIDTH, wh / HEIGHT)
    self.ox = int((ww - WIDTH * self.scale) / 2)
    self.oy = int((wh - HEIGHT * self.scale) / 2)

  def to_virtual(self, wx, wy):
    return ((wx - self.ox) / self.scale, (wy - self.oy) / self.scale)

  def present(self, window, canvas):
    if self.scale == 1.0 and self.ox == 0 and self.oy == 0:
      window.blit(canvas, (0, 0))
      return
    window.fill((0, 0, 0))
    size = (int(WIDTH * self.scale), int(HEIGHT * self.scale))
    window.blit(pygame.transform.smoothscale(canvas, size), (self.ox, self.oy))


def open_display():
  if IS_WEB:
    return pygame.display.set_mode((WIDTH, HEIGHT))
  if IS_ANDROID:
    return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
  try:
    desk_h = pygame.display.get_desktop_sizes()[0][1]
  except Exception:
    desk_h = 900
  h = max(480, int(desk_h * 0.85))
  return pygame.display.set_mode((int(h * WIDTH / HEIGHT), h), pygame.RESIZABLE)


async def main():
  pygame.mixer.pre_init(RATE_HINT, -16, 2, 1024 if IS_ANDROID else 512)
  pygame.init()
  open_display()
  pygame.display.set_caption("Domino Wonder Dash - Learn while you play")
  clock = pygame.time.Clock()
  canvas = pygame.Surface((WIDTH, HEIGHT))
  view = Viewport()
  sfx = SoundBank()
  speaker = Speaker()
  game = Game(sfx, speaker)

  # Touch and mouse share one code path. Phones also send "fake" mouse events
  # for each touch, so those are ignored to avoid double taps.
  finger_id = None
  ignore_mouse_until = 0.0

  running = True
  while running:
    window = pygame.display.get_surface()
    view.fit(window.get_size())
    now = time.time()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYDOWN and event.key in (
          pygame.K_ESCAPE, pygame.K_AC_BACK):
        running = False

      elif event.type == pygame.FINGERDOWN:
        ignore_mouse_until = now + 0.6
        if finger_id is None:
          finger_id = event.finger_id
          ww, wh = window.get_size()
          game.press(view.to_virtual(event.x * ww, event.y * wh))
      elif event.type == pygame.FINGERMOTION:
        ignore_mouse_until = now + 0.6
        if event.finger_id == finger_id:
          ww, wh = window.get_size()
          game.drag(view.to_virtual(event.x * ww, event.y * wh))
      elif event.type == pygame.FINGERUP:
        ignore_mouse_until = now + 0.6
        if event.finger_id == finger_id:
          finger_id = None
          ww, wh = window.get_size()
          game.release(view.to_virtual(event.x * ww, event.y * wh))

      elif event.type in (
          pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
        if (getattr(event, "touch", False) or finger_id is not None
            or now < ignore_mouse_until):
          continue
        pos = view.to_virtual(*event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
          game.press(pos)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
          game.drag(pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
          game.release(pos)

    game.update()
    game.draw(canvas)
    view.present(window, canvas)
    pygame.display.flip()
    clock.tick(60)
    await asyncio.sleep(0)  # lets the browser breathe under pygbag

  speaker.close()
  pygame.quit()


if __name__ == "__main__":
  asyncio.run(main())
