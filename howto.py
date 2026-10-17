"""How to play: picture guides that show, not tell.

Young children (Class 1 and up) may not read yet, so every step is a moving
picture - a hand traces real dots, taps, dominoes fall - with one short line
that the game also says out loud (English, Hindi or Bengali, the child's
language). Big Back / Hear again / Next buttons.

A guide opens by itself the first time a child plays each way (trace, Find
it!, Spell it, Draw my own); the "?" button and Games > How to play open it
again. While tracing, a helping hand also shows what to do when a child
stops for a few seconds.
"""

import math
import time

import pygame

import domino_data as hub

WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
CYAN = (0, 255, 204)
GREEN = (60, 180, 90)
RED = (230, 40, 50)
HINT = (170, 180, 210)
SKIN = (255, 214, 170)
SKIN_LINE = (150, 90, 50)

STAGE = pygame.Rect(16, 96, 418, 404)       # where the moving picture plays (panel coords)
BACK_BTN = pygame.Rect(16, 652, 120, 84)
HEAR_BTN = pygame.Rect(165, 652, 120, 84)
NEXT_BTN = pygame.Rect(314, 652, 120, 84)
CLOSE_BTN = pygame.Rect(392, 10, 48, 48)

IDLE_TRACE = 6.0       # s without a new dot before the helping hand shows
IDLE_TAP = 3.0         # s of standing dominoes before the hand shows a tap
IDLE_DRAW = 5.0        # s of an empty drawing page

SAMPLE = ("Animals", "Cat")                 # the picture every guide uses
CHOICES = [("Animals", "Cat"), ("Vehicles", "Car"), ("Fruits", "Apple"), ("Sea", "Fish"),
           ("Shapes", "Star"), ("Home", "Ball")]

# Each page: (moving picture, title, line shown and said, Hindi, Bengali)
PAGES = {
    "trace": [
        ("pick", "1. Pick a picture",
         "Tap the menu button, then pick a picture.",
         "मेन्यू बटन दबाओ, फिर एक चित्र चुनो।",
         "মেনু বোতাম টিপো, তারপর একটা ছবি বেছে নাও।"),
        ("trace", "2. Trace the dots",
         "Put your finger on the dots and slide along them.",
         "उंगली बिंदुओं पर रखो और उनके ऊपर चलाओ।",
         "আঙুল বিন্দুগুলোর ওপর রেখে টেনে নিয়ে যাও।"),
        ("topple", "3. Tap! They fall",
         "Dominoes stand up. Tap the screen and watch them fall!",
         "डोमिनो खड़े हो जाएंगे। स्क्रीन पर टैप करो और उन्हें गिरते देखो!",
         "ডোমিনো দাঁড়িয়ে যাবে। স্ক্রিনে টোকা দাও আর দেখো সেগুলো পড়ে যায়!"),
        ("hear", "4. See, hear, spell",
         "See the real picture. Hear its name and spell it. Win stickers!",
         "असली चित्र देखो। उसका नाम सुनो और स्पेलिंग सीखो। स्टिकर जीतो!",
         "আসল ছবি দেখো। নাম শোনো আর বানান শেখো। স্টিকার জেতো!"),
        ("buttons", "5. Your buttons",
         "Menu: all pictures. House: Wonder Town. Arrow: next picture. Speaker: hear it again.",
         "मेन्यू में सारे चित्र हैं। घर वाला बटन वंडर टाउन है। "
         "हरा तीर अगला चित्र है। स्पीकर नाम दोबारा बोलता है।",
         "মেনুতে সব ছবি আছে। বাড়ির বোতাম ওয়ান্ডার টাউন। "
         "সবুজ তীর পরের ছবি। স্পিকার আবার নাম বলে।"),
        ("more", "6. More games",
         "Open the menu, then Games: Find it, Spell it, Draw and Stories.",
         "मेन्यू खोलो, फिर गेम्स: ढूंढो, स्पेलिंग, ड्राइंग और कहानियाँ।",
         "মেনু খোলো, তারপর গেমস: খুঁজে বের করো, বানান, আঁকা আর গল্প।"),
    ],
    "quiz": [
        ("quiz", "Find it!",
         "Listen to the name, then tap the right picture.",
         "नाम सुनो, फिर सही चित्र पर टैप करो।",
         "নাম শোনো, তারপর ঠিক ছবিতে টোকা দাও।"),
    ],
    "spell": [
        ("spell", "Spell it",
         "Tap the letters in the right order to make the word.",
         "शब्द बनाने के लिए अक्षरों को सही क्रम में टैप करो।",
         "শব্দ বানাতে অক্ষরগুলো ঠিক ক্রমে টোকা দাও।"),
    ],
    "draw": [
        ("draw", "Draw my own",
         "Pick a crayon and draw with your finger. Tap Done to make dominoes.",
         "एक क्रेयॉन चुनो और उंगली से ड्रॉ करो। डोमिनो बनाने के लिए डन दबाओ।",
         "একটা রং বেছে আঙুল দিয়ে আঁকো। ডোমিনো বানাতে ডান টিপো।"),
    ],
}
NUDGE = ("Put your finger on the dots and slide!",
         "उंगली बिंदुओं पर रखो और चलाओ!",
         "আঙুল বিন্দুর ওপর রেখে টানো!")
TAP_NUDGE = ("Tap the screen to push the dominoes!",
             "डोमिनो गिराने के लिए स्क्रीन पर टैप करो!",
             "ডোমিনো ফেলতে স্ক্রিনে টোকা দাও!")


def guide_key(g):
  """Which guide fits what the child is doing now."""
  if g.mode in ("quiz", "spell"):
    return g.mode
  return "draw" if g.is_custom else "trace"


def say_line(g, en, hi, bn):
  native = {"hi": hi, "bn": bn}.get(g.lang)
  g.say(en, native)


# ---------------------------------------------------------------- the hand
_HAND = {}


def hand_surface(scale=1.0):
  """A cartoon pointing hand; its fingertip is at (29, 2) * scale."""
  key = round(scale, 2)
  if key in _HAND:
    return _HAND[key]
  s = pygame.Surface((64, 84), pygame.SRCALPHA)
  parts = [("rect", (21, 0, 16, 48), 8), ("rect", (11, 34, 46, 40), 15),
           ("ell", (2, 42, 22, 16), 0), ("rect", (16, 70, 36, 13), 4)]
  for kind, r, rad in parts:                      # dark outline first
    big = pygame.Rect(r).inflate(5, 5)
    if kind == "rect":
      pygame.draw.rect(s, SKIN_LINE, big, border_radius=rad + 2)
    else:
      pygame.draw.ellipse(s, SKIN_LINE, big)
  for kind, r, rad in parts[:3]:
    if kind == "rect":
      pygame.draw.rect(s, SKIN, r, border_radius=rad)
    else:
      pygame.draw.ellipse(s, SKIN, r)
  pygame.draw.rect(s, (70, 130, 230), parts[3][1], border_radius=4)     # sleeve
  for x in (38, 46):                                                    # curled fingers
    pygame.draw.line(s, SKIN_LINE, (x, 40), (x, 52), 2)
  pygame.draw.ellipse(s, (255, 235, 215), (24, 3, 8, 8))                # nail shine
  if scale != 1.0:
    s = pygame.transform.smoothscale(s, (int(64 * scale), int(84 * scale)))
  _HAND[key] = s
  return s


def draw_hand(screen, tip, pressed=False, scale=1.0):
  """Hand with its fingertip at tip; pressed shows a little tap ring."""
  k = scale * (0.9 if pressed else 1.0)
  h = hand_surface(k)
  screen.blit(h, (tip[0] - 29 * k, tip[1] - 2 * k + (3 if pressed else 0)))
  if pressed:
    pygame.draw.circle(screen, WHITE, (int(tip[0]), int(tip[1])), int(18 * scale), 3)


def tap_rings(screen, pos, t):
  """Circles that grow out of a tap."""
  for k in range(2):
    p = (t * 1.5 + k * 0.5) % 1.0
    r = int(10 + 34 * p)
    ring = pygame.Surface((2 * r + 4, 2 * r + 4), pygame.SRCALPHA)
    pygame.draw.circle(ring, (255, 255, 255, int(220 * (1 - p))), (r + 2, r + 2), r, 3)
    screen.blit(ring, (pos[0] - r - 2, pos[1] - r - 2))


def help_icon(size):
  """A round "?" for the help button and the Games menu."""
  s = pygame.Surface((size, size), pygame.SRCALPHA)
  pygame.draw.circle(s, (150, 80, 200), (size // 2, size // 2), size // 2)
  pygame.draw.circle(s, WHITE, (size // 2, size // 2), size // 2, max(2, size // 16))
  f = pygame.font.Font(None, int(size * 0.95))
  q = f.render("?", True, WHITE)
  s.blit(q, q.get_rect(center=(size // 2, size // 2 + size // 16)))
  return s


def small_tile(colour, w=18, h=34, letter=None, font=None):
  s = pygame.Surface((w, h), pygame.SRCALPHA)
  dark = tuple(int(c * 0.55) for c in colour)
  pygame.draw.rect(s, dark, (0, 0, w, h), border_radius=4)
  pygame.draw.rect(s, colour, (2, 2, w - 4, h - 4), border_radius=4)
  if letter and font:
    pygame.draw.circle(s, WHITE, (w // 2, h // 2), w // 2 - 1)
    lb = font.render(letter, True, dark)
    s.blit(lb, lb.get_rect(center=(w // 2, h // 2 + 1)))
  else:
    pygame.draw.line(s, WHITE, (3, h // 2), (w - 4, h // 2), 1)
    pygame.draw.circle(s, WHITE, (w // 2, h // 4), 2)
    pygame.draw.circle(s, WHITE, (w // 2, 3 * h // 4), 2)
  return s


def hue(i, n, s=80, v=100):
  c = pygame.Color(0)
  c.hsva = (int(i * 360 / max(1, n)) % 360, s, v, 100)
  return c


# ---------------------------------------------------------------- the panel
class Guide:
  """Overlay panel "howto": a few moving pictures, one per step."""

  def __init__(self):
    self.key, self.page, self.at = "trace", 0, 0.0
    self._dots = {}

  def open(self, g, key, page=0):
    self.key, self.page = key, page
    g.overlay = "howto"
    self.start_page(g)

  def pages(self):
    return PAGES[self.key]

  def start_page(self, g):
    self.at = time.time()
    _anim, _title, en, hi, bn = self.pages()[self.page]
    say_line(g, en, hi, bn)

  def close(self, g):
    """Back to the game, which says the picture's name again."""
    g.overlay = None
    g.sfx.play("click")
    if g.in_world:
      return
    if g.mode == "quiz" and g.quiz:
      g.quiz.ask()
    elif g.mode == "spell" and g.spell:
      g.say(f"Spell the word: {g.puzzle}.", g.native_word(g.cat, g.puzzle))
    else:
      g.announce()

  def press(self, g, pos):
    last = self.page == len(self.pages()) - 1
    if CLOSE_BTN.collidepoint(pos):
      self.close(g)
    elif NEXT_BTN.collidepoint(pos) or STAGE.collidepoint(pos):
      if last:
        self.close(g)
      else:
        g.sfx.play("switch")
        self.page += 1
        self.start_page(g)
    elif BACK_BTN.collidepoint(pos) and self.page > 0:
      g.sfx.play("switch")
      self.page -= 1
      self.start_page(g)
    elif HEAR_BTN.collidepoint(pos):
      g.sfx.play("click")
      self.start_page(g)

  # ------------------------------------------------------------ drawing
  def draw(self, screen, g, now):
    tm = g.theme
    screen.fill(tm["bg"])
    pygame.draw.rect(screen, tm["panel"], screen.get_rect(), 3)
    anim, title, en, _hi, _bn = self.pages()[self.page]
    t = now - self.at
    head = g.font_at(30).render(title, True, YELLOW)
    screen.blit(head, head.get_rect(center=(225, 52)))
    # close (X)
    pygame.draw.circle(screen, (255, 100, 100), CLOSE_BTN.center, 22)
    pygame.draw.circle(screen, WHITE, CLOSE_BTN.center, 22, 2)
    cx, cy = CLOSE_BTN.center
    pygame.draw.line(screen, WHITE, (cx - 8, cy - 8), (cx + 8, cy + 8), 4)
    pygame.draw.line(screen, WHITE, (cx + 8, cy - 8), (cx - 8, cy + 8), 4)
    # the moving picture
    pygame.draw.rect(screen, tm["panel"], STAGE, border_radius=18)
    pygame.draw.rect(screen, WHITE, STAGE, 2, border_radius=18)
    screen.set_clip(STAGE.inflate(-4, -4))
    getattr(self, "anim_" + anim)(screen, g, t)
    screen.set_clip(None)
    # the line, big and short
    font = g.font_at(21)
    for n, line in enumerate(wrap_text(font, en, 410)[:4]):
      s = font.render(line, True, WHITE)
      screen.blit(s, s.get_rect(center=(225, 530 + n * 28)))
    # page dots
    total = len(self.pages())
    if total > 1:
      for k in range(total):
        x = 225 + (k - (total - 1) / 2) * 24
        pygame.draw.circle(screen, YELLOW if k == self.page else HINT, (int(x), 630),
                           8 if k == self.page else 5)
    # Back / Hear again / Next
    if self.page > 0:
      self.big_button(screen, g, BACK_BTN, (90, 110, 170), "back")
    self.big_button(screen, g, HEAR_BTN, (0, 170, 160), "hear")
    last = self.page == total - 1
    self.big_button(screen, g, NEXT_BTN, GREEN, "play" if last else "next", now)

  def big_button(self, screen, g, rect, colour, kind, now=0.0):
    r = rect
    if kind == "play":                       # "Let's play" gently pulses
      r = rect.inflate(int(6 * math.sin(now * 5)), int(6 * math.sin(now * 5)))
    pygame.draw.rect(screen, colour, r, border_radius=18)
    pygame.draw.rect(screen, WHITE, r, 3, border_radius=18)
    cx, cy = r.centerx, r.centery - 10
    if kind == "next":
      pygame.draw.polygon(screen, WHITE, [(cx - 12, cy - 18), (cx + 16, cy), (cx - 12, cy + 18)])
    elif kind == "back":
      pygame.draw.polygon(screen, WHITE, [(cx + 12, cy - 18), (cx - 16, cy), (cx + 12, cy + 18)])
    elif kind == "hear":
      pygame.draw.rect(screen, WHITE, (cx - 16, cy - 7, 9, 14))
      pygame.draw.polygon(screen, WHITE, [(cx - 8, cy - 7), (cx + 4, cy - 17), (cx + 4, cy + 17),
                                          (cx - 8, cy + 7)])
      for rr in (9, 16):
        pygame.draw.arc(screen, WHITE, (cx + 4 - rr, cy - rr, 2 * rr, 2 * rr),
                        -math.pi / 4, math.pi / 4, 3)
    elif kind == "play":
      self_star(screen, (cx, cy), 18)
    label = {"next": "Next", "back": "Back", "hear": "Hear", "play": "Let's play!"}[kind]
    lb = g.font_at(17).render(label, True, WHITE)
    screen.blit(lb, lb.get_rect(center=(r.centerx, r.bottom - 16)))

  # ------------------------------------------------------------ sample picture
  def sample_dots(self, g, box, n=34):
    key = (box, n)
    if key not in self._dots:
      loops, _closed = hub.fetch_trace_from_hub(SAMPLE[1], box, cat=SAMPLE[0], max_dots=n,
                                                part_dots=0, min_spacing=12)
      self._dots[key] = loops[0] if loops else []
    return self._dots[key]

  def sample_picture(self, g, box, alpha=255):
    path, rect = hub.fetch_picture_from_hub(SAMPLE[1], box, cat=SAMPLE[0])
    if not path or not rect:
      return
    img = g.image(path, (max(1, int(rect[2])), max(1, int(rect[3]))))
    if img is None:
      return
    if alpha < 255:
      img = img.copy()
      img.set_alpha(alpha)
    return img, (int(rect[0]), int(rect[1]))

  def blit_sample(self, screen, g, box, alpha=255):
    got = self.sample_picture(g, box, alpha)
    if got:
      screen.blit(*got)

  # ------------------------------------------------------------ the moving pictures
  def anim_pick(self, screen, g, t):
    t %= 5.0
    s = STAGE
    menu = pygame.Rect(s.x + 20, s.y + 18, 56, 60)
    pressed_menu = 0.6 < t < 1.0
    pygame.draw.rect(screen, (70, 130, 230), menu, border_radius=12)
    pygame.draw.rect(screen, YELLOW if t < 1.0 else WHITE, menu, 3, border_radius=12)
    for k in range(3):
      y = menu.centery - 13 + k * 13
      pygame.draw.line(screen, WHITE, (menu.x + 14, y), (menu.right - 14, y), 5)
    if t < 1.2:                                       # hand goes to the menu button
      k = min(1.0, t / 0.6)
      tip = (s.centerx + (menu.centerx - s.centerx) * k, s.bottom - 40 + (menu.centery - s.bottom + 40) * k)
      if pressed_menu:
        tap_rings(screen, menu.center, t)
      draw_hand(screen, tip, pressed_menu)
      return
    # the picture menu opens: six pictures
    cells = []
    for i, (cat, name) in enumerate(CHOICES):
      r, c = divmod(i, 3)
      cells.append((pygame.Rect(s.x + 26 + c * 126, s.y + 100 + r * 146, 114, 134), cat, name))
    chosen = t > 2.9
    for rect, cat, name in cells:
      on = chosen and name == SAMPLE[1]
      pygame.draw.rect(screen, CYAN if on else g.theme["cell"], rect, border_radius=12)
      th = g.thumb(name, cat, 84)
      if th is not None:
        screen.blit(th, th.get_rect(center=(rect.centerx, rect.y + 56)))
      lb = g.font_at(17).render(name, True, g.theme["bg"] if on else WHITE)
      screen.blit(lb, lb.get_rect(center=(rect.centerx, rect.bottom - 16)))
    target = cells[0][0].center
    k = min(1.0, max(0.0, (t - 1.6) / 1.0))
    start = (s.centerx + 40, s.bottom - 30)
    tip = (start[0] + (target[0] - start[0]) * k, start[1] + (target[1] - start[1]) * k)
    pressed = 2.7 < t < 3.2
    if pressed:
      tap_rings(screen, target, t)
    draw_hand(screen, tip, pressed)

  def anim_trace(self, screen, g, t):
    box = (STAGE.x + 40, STAGE.y + 20, STAGE.w - 80, STAGE.h - 40)
    dots = self.sample_dots(g, box)
    if not dots:
      return
    self.blit_sample(screen, g, box, 55)
    period = len(dots) * 0.11 + 1.6
    t %= period
    upto = min(len(dots), int(t / 0.11))
    for i, (x, y) in enumerate(dots):
      if i < upto:
        pygame.draw.circle(screen, hue(i, len(dots)), (int(x), int(y)), 9)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 9, 2)
      else:
        pygame.draw.circle(screen, (40, 40, 60), (int(x), int(y)), 8)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 6)
    i = min(len(dots) - 1, upto)
    tip = dots[i]
    if upto < len(dots):
      a, b = dots[max(0, i - 1)], dots[i]
      f = (t / 0.11) % 1.0
      tip = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
      draw_hand(screen, tip, True)
    lb = g.font_at(20).render(f"{upto} / {len(dots)}", True, YELLOW)
    screen.blit(lb, lb.get_rect(midbottom=(STAGE.centerx, STAGE.bottom - 8)))

  def anim_topple(self, screen, g, t):
    box = (STAGE.x + 40, STAGE.y + 20, STAGE.w - 80, STAGE.h - 40)
    dots = self.sample_dots(g, box, 26)
    if not dots:
      return
    t %= 7.0
    n = len(dots)
    font = g.font_at(14)
    tap_at, fall_from = 2.4, 2.7
    reveal = t > fall_from + n * 0.06 + 0.4
    if reveal:
      self.blit_sample(screen, g, box, min(255, int((t - fall_from - n * 0.06 - 0.4) * 400)))
    for i, (x, y) in enumerate(dots):
      drop = min(1.0, max(0.0, (t - i * 0.06) / 0.3))     # dominoes drop in one by one
      if drop <= 0:
        continue
      nxt = dots[(i + 1) % n]
      ang = math.degrees(math.atan2(nxt[1] - y, nxt[0] - x))
      fall = min(1.0, max(0.0, (t - fall_from - i * 0.06) / 0.25))
      tile = small_tile(hue(i, n, 70, 90), letter="C", font=font)
      if fall > 0:
        tile = pygame.transform.smoothscale(tile, (18, max(4, int(34 * (1 - 0.75 * fall)))))
      tile = pygame.transform.rotate(tile, -ang - 90)
      if reveal:
        tile.set_alpha(110)
      screen.blit(tile, tile.get_rect(center=(x, y - (1 - drop) * 40)))
    if t < tap_at:
      draw_hand(screen, (STAGE.centerx + 60, STAGE.bottom - 40), False)
    elif t < fall_from + 0.4:
      tap_rings(screen, (STAGE.centerx, STAGE.centery), t)
      draw_hand(screen, (STAGE.centerx, STAGE.centery), True)
    if reveal:
      lb = g.font_at(30).render("Cat!", True, YELLOW)
      screen.blit(lb, lb.get_rect(midbottom=(STAGE.centerx, STAGE.bottom - 8)))

  def anim_hear(self, screen, g, t):
    box = (STAGE.x + 70, STAGE.y + 100, STAGE.w - 140, STAGE.h - 130)
    self.blit_sample(screen, g, box)
    t %= 4.5
    word = "CAT"
    lit = int((t - 0.8) // 0.7)
    for i, ch in enumerate(word):
      r = pygame.Rect(STAGE.centerx - 130 + i * 62, STAGE.y + 20 - (8 if i == lit else 0), 54, 66)
      pygame.draw.rect(screen, YELLOW if i == lit else hue(i, 3, 70, 95), r, border_radius=10)
      pygame.draw.rect(screen, WHITE, r, 3, border_radius=10)
      lb = g.font_at(40).render(ch, True, (40, 40, 70) if i == lit else WHITE)
      screen.blit(lb, lb.get_rect(center=r.center))
    sp = (STAGE.right - 46, STAGE.y + 53)
    pygame.draw.circle(screen, CYAN, sp, 24)
    pygame.draw.polygon(screen, g.theme["bg"], [(sp[0] - 10, sp[1] - 6), (sp[0] + 4, sp[1] - 15),
                                                 (sp[0] + 4, sp[1] + 15), (sp[0] - 10, sp[1] + 6)])
    for k in range(3):                              # sound waves
      p = (t * 1.2 + k / 3) % 1.0
      pygame.draw.arc(screen, WHITE, (sp[0] - 10 - 30 * p, sp[1] - 10 - 30 * p, 40 + 60 * p,
                                      20 + 60 * p), -math.pi / 4, math.pi / 4, 2)
    if t > 3.2:                                      # a sticker!
      self_star(screen, (STAGE.right - 50, STAGE.bottom - 50), 26 + 6 * math.sin(t * 8))

  def anim_buttons(self, screen, g, t):
    rows = [("menu", "Menu: every picture"), ("town", "House: Wonder Town"),
            ("next", "Next picture"), ("speaker", "Hear the name again"),
            ("video", "Watch the real one"), ("help", "Help: this guide")]
    on = int(t / 1.3) % len(rows)
    for i, (kind, text) in enumerate(rows):
      y = STAGE.y + 16 + i * 64
      r = pygame.Rect(STAGE.x + 20, y, 56, 54)
      if i == on:
        glow = pygame.Surface((STAGE.w - 16, 62), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 255, 50), glow.get_rect(), border_radius=12)
        screen.blit(glow, (STAGE.x + 8, y - 4))
      icon_button(screen, kind, r, g)
      lb = g.font_at(20).render(text, True, YELLOW if i == on else WHITE)
      screen.blit(lb, lb.get_rect(midleft=(r.right + 18, r.centery)))
      if i == on:
        draw_hand(screen, (r.centerx + 6, r.centery + 6), int(t * 2) % 2 == 0, 0.8)

  def anim_more(self, screen, g, t):
    cards = [("Find it!", ("Home", "Bulb"), "tap the picture"),
             ("Spell it", ("ABC", "A"), "letters in order"),
             ("Draw my own", None, "your own picture"),
             ("Stories", ("Sky", "Rainbow"), "a story a day")]
    on = int(t / 1.4) % len(cards)
    from screens import crayon_icon
    for i, (name, pic, sub) in enumerate(cards):
      r, c = divmod(i, 2)
      rect = pygame.Rect(STAGE.x + 16 + c * 200, STAGE.y + 18 + r * 190, 186, 176)
      pygame.draw.rect(screen, CYAN if i == on else g.theme["cell"], rect, border_radius=14)
      pygame.draw.rect(screen, WHITE, rect, 2, border_radius=14)
      img = crayon_icon(80) if pic is None else g.thumb(pic[1], pic[0], 80)
      if img is not None:
        screen.blit(img, img.get_rect(center=(rect.centerx, rect.y + 64)))
      ink = g.theme["bg"] if i == on else WHITE
      lb = g.font_at(20).render(name, True, ink)
      screen.blit(lb, lb.get_rect(center=(rect.centerx, rect.bottom - 46)))
      sb = g.font_at(14).render(sub, True, ink)
      screen.blit(sb, sb.get_rect(center=(rect.centerx, rect.bottom - 20)))
      if i == on:
        draw_hand(screen, (rect.centerx + 34, rect.y + 70), int(t * 2) % 2 == 0, 0.7)

  def anim_quiz(self, screen, g, t):
    t %= 5.0
    sp = (STAGE.centerx - 110, STAGE.y + 46)
    pygame.draw.circle(screen, CYAN, sp, 26)
    pygame.draw.polygon(screen, g.theme["bg"], [(sp[0] - 11, sp[1] - 7), (sp[0] + 5, sp[1] - 17),
                                                 (sp[0] + 5, sp[1] + 17), (sp[0] - 11, sp[1] + 7)])
    lb = g.font_at(26).render("Find the Cat!", True, YELLOW)
    screen.blit(lb, lb.get_rect(midleft=(sp[0] + 40, sp[1])))
    picks = [CHOICES[1], CHOICES[0], CHOICES[3], CHOICES[2]]
    right = t > 2.4
    target = None
    for i, (cat, name) in enumerate(picks):
      r, c = divmod(i, 2)
      rect = pygame.Rect(STAGE.x + 26 + c * 190, STAGE.y + 96 + r * 150, 176, 138)
      good = right and name == SAMPLE[1]
      pygame.draw.rect(screen, (60, 210, 110) if good else g.theme["cell"], rect, border_radius=14)
      pygame.draw.rect(screen, WHITE, rect, 3 if good else 2, border_radius=14)
      th = g.thumb(name, cat, 104)
      if th is not None:
        screen.blit(th, th.get_rect(center=rect.center))
      if name == SAMPLE[1]:
        target = rect.center
    if right:
      lb = g.font_at(30).render("Yes!", True, YELLOW)
      screen.blit(lb, lb.get_rect(center=(STAGE.centerx, STAGE.bottom - 32)))
    k = min(1.0, max(0.0, (t - 1.0) / 1.0))
    start = (STAGE.centerx, STAGE.bottom - 20)
    tip = (start[0] + (target[0] - start[0]) * k, start[1] + (target[1] - start[1]) * k)
    if 2.1 < t < 2.7:
      tap_rings(screen, target, t)
    draw_hand(screen, tip, 2.1 < t < 2.7)

  def anim_spell(self, screen, g, t):
    t %= 6.0
    th = g.thumb(SAMPLE[1], SAMPLE[0], 120)
    if th is not None:
      screen.blit(th, th.get_rect(center=(STAGE.centerx, STAGE.y + 80)))
    word, pool = "CAT", ["T", "C", "A"]
    placed = max(0, min(3, int((t - 0.8) // 1.2) + 1)) if t > 1.6 else 0
    font = g.font_at(34)
    slots = [pygame.Rect(STAGE.centerx - 95 + i * 66, STAGE.y + 160, 58, 64) for i in range(3)]
    for i, r in enumerate(slots):
      pygame.draw.rect(screen, YELLOW if i < placed else g.theme["banner"], r, border_radius=10)
      pygame.draw.rect(screen, WHITE, r, 2, border_radius=10)
      if i < placed:
        lb = font.render(word[i], True, g.theme["bg"])
        screen.blit(lb, lb.get_rect(center=r.center))
    tiles = [pygame.Rect(STAGE.centerx - 100 + i * 72, STAGE.y + 270, 62, 62) for i in range(3)]
    for i, (r, ch) in enumerate(zip(tiles, pool)):
      if word.index(ch) < placed:
        continue
      pygame.draw.rect(screen, hue(i * 2, 6, 65, 95), r, border_radius=12)
      pygame.draw.rect(screen, WHITE, r, 2, border_radius=12)
      lb = font.render(ch, True, WHITE)
      screen.blit(lb, lb.get_rect(center=r.center))
    if placed < 3:
      nxt = word[placed]
      target = tiles[pool.index(nxt)].center
      phase = (t - 0.4) % 1.2 if t > 0.4 else 0
      pressed = phase > 0.8
      if pressed:
        tap_rings(screen, target, t)
      draw_hand(screen, target, pressed)
    else:
      lb = g.font_at(30).render("CAT!", True, YELLOW)
      screen.blit(lb, lb.get_rect(center=(STAGE.centerx, STAGE.bottom - 30)))

  def anim_draw(self, screen, g, t):
    t %= 6.5
    for i, col in enumerate(CRAYONS):
      c = (STAGE.x + 34 + i * 40, STAGE.y + 30)
      pygame.draw.circle(screen, col, c, 15)
      pygame.draw.circle(screen, WHITE if i == 1 else (40, 40, 60), c, 15, 3 if i == 1 else 1)
    done = pygame.Rect(STAGE.right - 110, STAGE.bottom - 66, 92, 48)
    pygame.draw.rect(screen, GREEN, done, border_radius=12)
    pygame.draw.rect(screen, WHITE, done, 2, border_radius=12)
    lb = g.font_at(20).render("Done", True, WHITE)
    screen.blit(lb, lb.get_rect(center=done.center))
    # a little house drawn with one line
    path = [(0.25, 0.85), (0.25, 0.5), (0.5, 0.25), (0.75, 0.5), (0.75, 0.85), (0.25, 0.85)]
    area = pygame.Rect(STAGE.x + 70, STAGE.y + 70, STAGE.w - 140, STAGE.h - 150)
    pts = [(area.x + x * area.w, area.y + y * area.h) for x, y in path]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    drawn = min(1.0, t / 3.0) * total
    line, left = [pts[0]], drawn
    for (a, b), d in zip(zip(pts, pts[1:]), seg):
      if left >= d:
        line.append(b)
        left -= d
      else:
        f = left / d
        line.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        break
    as_dominoes = t > 4.2
    if not as_dominoes and len(line) > 1:
      pygame.draw.lines(screen, CRAYONS_PINK, False, line, 8)
    if as_dominoes:
      n = 0
      for (a, b), d in zip(zip(pts, pts[1:]), seg):
        steps = max(1, int(d // 24))
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        for k in range(steps):
          f = k / steps
          tile = pygame.transform.rotate(small_tile(hue(n, 30, 70, 90)), -ang - 90)
          screen.blit(tile, tile.get_rect(center=(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)))
          n += 1
    if t < 3.0:
      draw_hand(screen, line[-1], True)
    elif t < 4.4:
      k = min(1.0, (t - 3.0) / 0.8)
      tip = (line[-1][0] + (done.centerx - line[-1][0]) * k, line[-1][1] + (done.centery - line[-1][1]) * k)
      if t > 3.9:
        tap_rings(screen, done.center, t)
      draw_hand(screen, tip, t > 3.9)


CRAYONS = [(255, 204, 0), (233, 69, 96), (255, 140, 40), (80, 200, 90),
           (60, 160, 255), (170, 110, 255), (255, 255, 255)]
CRAYONS_PINK = CRAYONS[1]


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


def self_star(screen, center, r):
  cx, cy = center
  pts = []
  for i in range(10):
    rad = r if i % 2 == 0 else r * 0.45
    a = -math.pi / 2 + i * math.pi / 5
    pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
  pygame.draw.polygon(screen, (255, 215, 0), pts)
  pygame.draw.polygon(screen, (150, 100, 0), pts, 2)


def icon_button(screen, kind, r, g):
  """The game's own top-row buttons, drawn the same way, for the legend."""
  cx, cy = r.center
  if kind == "menu":
    pygame.draw.rect(screen, (70, 130, 230), r, border_radius=12)
    pygame.draw.rect(screen, WHITE, r, 2, border_radius=12)
    for k in range(3):
      y = cy - 12 + k * 12
      pygame.draw.line(screen, WHITE, (r.x + 14, y), (r.right - 14, y), 4)
  elif kind == "town":
    pygame.draw.rect(screen, (240, 140, 40), r, border_radius=12)
    pygame.draw.rect(screen, WHITE, r, 2, border_radius=12)
    pygame.draw.polygon(screen, WHITE, [(cx - 14, cy - 1), (cx, cy - 13), (cx + 14, cy - 1)])
    pygame.draw.rect(screen, WHITE, (cx - 10, cy - 1, 20, 14))
  elif kind == "next":
    pygame.draw.rect(screen, GREEN, r, border_radius=12)
    pygame.draw.rect(screen, WHITE, r, 2, border_radius=12)
    pygame.draw.polygon(screen, WHITE, [(cx - 8, cy - 13), (cx + 10, cy), (cx - 8, cy + 13)])
  elif kind == "speaker":
    pygame.draw.circle(screen, CYAN, r.center, 22)
    bg = g.theme["bg"]
    pygame.draw.rect(screen, bg, (cx - 11, cy - 5, 6, 10))
    pygame.draw.polygon(screen, bg, [(cx - 6, cy - 5), (cx + 2, cy - 12), (cx + 2, cy + 12),
                                     (cx - 6, cy + 5)])
  elif kind == "video":
    pygame.draw.circle(screen, RED, r.center, 21)
    pygame.draw.circle(screen, WHITE, r.center, 21, 2)
    pygame.draw.polygon(screen, WHITE, [(cx - 6, cy - 10), (cx - 6, cy + 10), (cx + 11, cy)])
  elif kind == "help":
    ic = help_icon(46)
    screen.blit(ic, ic.get_rect(center=r.center))


# ---------------------------------------------------------------- helping hand in the game
def draw_idle_hand(g, screen, now, play_rect):
  """While tracing: if the child stops, a hand slides over the next dots (and
  the game says how, once per picture for new players). Standing dominoes: a
  hand shows a tap. Empty drawing page: a hand draws a squiggle."""
  if g.mode != "trace" or g.overlay or g.celebration:
    return
  idle = now - getattr(g, "last_progress_at", now)
  if g.stage == "trace" and idle > IDLE_TRACE and g.dots:
    start = next((i for i, c in enumerate(g.covered) if not c), None)
    if start is None:
      return
    path = [g.dots[start]]
    for lo, hi in g._loop_slices():
      if lo <= start < hi:
        path = g.dots[start:min(hi, start + 6)]
        break
    t = (idle - IDLE_TRACE) % 2.2
    pygame.draw.circle(screen, YELLOW, (int(path[0][0]), int(path[0][1])),
                       int(16 + 5 * math.sin(now * 6)), 3)
    if t < 0.4 or len(path) < 2:
      draw_hand(screen, path[0], t > 0.2)
    else:
      f = min(1.0, (t - 0.4) / 1.4) * (len(path) - 1)
      i = min(len(path) - 2, int(f))
      a, b = path[i], path[i + 1]
      k = f - i
      draw_hand(screen, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), True)
    if not getattr(g, "nudged", False) and len(g.progress.data.get("done", [])) < 15:
      g.nudged = True
      say_line(g, *NUDGE)
  elif g.stage == "ready" and not g.dropping() and idle > 2.4 + IDLE_TAP:
    c = (play_rect.centerx, play_rect.centery)
    tap_rings(screen, c, now)
    draw_hand(screen, c, int(now * 2) % 2 == 0)
    if not getattr(g, "tap_nudged", False) and len(g.progress.data.get("done", [])) < 15:
      g.tap_nudged = True
      say_line(g, *TAP_NUDGE)
  elif g.stage == "draw" and not g.drawing and idle > IDLE_DRAW:
    t = (idle - IDLE_DRAW) % 2.5
    c = play_rect.center
    pts = [(c[0] - 80 + k * 8, c[1] + 30 * math.sin(k / 3)) for k in range(int(min(1, t / 1.8) * 20) + 1)]
    if len(pts) > 1:
      pygame.draw.lines(screen, CRAYONS_PINK, False, pts, 6)
    draw_hand(screen, pts[-1], True)


GUIDE = Guide()
