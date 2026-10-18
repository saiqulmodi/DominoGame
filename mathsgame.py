"""Maths Play: numbers learned with the dominoes' own dots (NCERT Class 1-7).

Every operation is shown as adding, the way the whole of arithmetic is built:
  take away  = adding a negative       9 - 3 = 9 + (-3) = 6
  times      = adding again and again  4 x 3 = 4 + 4 + 4 = 12
  sharing    = taking away again and again (12 - 3 - 3 - 3 - 3 = 0, so 4)
The answers are worked out that way too (add_all / times_by_adding /
share_by_taking_away), and after a right answer the dominoes fall one by one
in a cascade with the running total floating over each one.

Seven levels, one per class:
  1 Class 1    count the dots, which domino has more, what comes after
  2 Class 1-2  add two halves, dominoes topple = take away, before / after
  3 Class 2    number bonds (5 = 3 + ?), tens and ones, which has fewer
  4 Class 3    groups of dominoes (times as adding), sharing laddoos (division)
  5 Class 4-5  tables to 10, common multiples ("factor gates"), the Fibonacci trail
  6 Class 6    integers with blue anti-dominoes on a number line, prime shields
  7 Class 7    ratio gates (a domino grows or shrinks), balance puzzles (x + 5 = 12)

The voice asks in the child's language (English, Hindi or Bengali); the child
taps one of four big number buttons (or one of two dominoes). Wrong: a shake and
a hint; after two tries the answer and its reason. Five right first time in a
row moves up a level; three misses in a row moves one down; the chips at the
bottom let a child or parent pick any level. A wrong tap is just a lesson.
"""

import math
import random
import time

import pygame

WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
GREEN = (60, 210, 110)
RED = (240, 70, 80)
INK = (40, 40, 70)
ANTI = (70, 140, 255)         # anti-dominoes (negative numbers)
SHIELD = (120, 230, 255)
LADDOO = (255, 165, 40)
LEVELS = 7
LEVEL_UP_RUN = 5         # right first time in a row to move up
NEXT_AFTER = 3.4         # s after a right answer before the next question
CASCADE_STEP = 0.32      # s between falling dominoes in the cascade
TILE_COLOURS = [(255, 120, 90), (90, 170, 255), (120, 210, 120), (255, 190, 60),
                (190, 130, 255), (255, 120, 190), (60, 200, 200), (240, 150, 60)]
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

KINDS = {
    1: ["count", "more", "after"],
    2: ["count", "add", "topple", "after", "before"],
    3: ["add", "topple", "bonds", "tens", "fewer"],
    4: ["times", "share", "bonds", "tens"],
    5: ["times", "share", "multiple", "fib", "tens"],
    6: ["integer", "prime", "topple", "times", "integer"],
    7: ["ratio", "balance", "integer", "fib", "prime"],
}
LEVEL_NAMES = {1: "Counting (Class 1)", 2: "Add & take away (Class 1-2)",
               3: "Bonds, tens & ones (Class 2)", 4: "Groups & sharing (Class 3)",
               5: "Tables & patterns (Class 4-5)", 6: "Integers & primes (Class 6)",
               7: "Ratios & balance (Class 7)"}

# Lines: (English shown + said, Hindi, Bengali). {a} {b} {c} are numbers.
ASK = {
    "count": ("How many dots on this domino?", "इस डोमिनो पर कितने बिंदु हैं?",
              "এই ডোমিনোতে কতগুলো বিন্দু আছে?"),
    "more": ("Which domino has more dots?", "किस डोमिनो पर ज़्यादा बिंदु हैं?",
             "কোন ডোমিনোতে বেশি বিন্দু আছে?"),
    "fewer": ("Which domino has fewer dots?", "किस डोमिनो पर कम बिंदु हैं?",
              "কোন ডোমিনোতে কম বিন্দু আছে?"),
    "after": ("What number comes after {a}?", "{a} के बाद कौन-सी संख्या आती है?",
              "{a}-এর পরে কোন সংখ্যা আসে?"),
    "before": ("What number comes before {a}?", "{a} से पहले कौन-सी संख्या आती है?",
               "{a}-এর আগে কোন সংখ্যা আসে?"),
    "add": ("Count the dots: {a} and {b}. How many in all?", "बिंदु गिनो: {a} और {b}। कुल कितने बिंदु?",
            "বিন্দু গোনো: {a} আর {b}। মোট কতগুলো বিন্দু?"),
    "topple": ("{a} dominoes stand in a row. {b} fall down. How many are still standing?",
               "{a} डोमिनो खड़े हैं। {b} गिर गए। कितने अब भी खड़े हैं?",
               "{a}টা ডোমিনো দাঁড়িয়ে আছে। {b}টা পড়ে গেল। কতগুলো এখনও দাঁড়িয়ে আছে?"),
    "bonds": ("{a} and how many more make {c}?", "{a} और कितने मिलकर {c} बनते हैं?",
              "{a} আর কত মিলে {c} হয়?"),
    "tens": ("{a} rows of ten and {b} more. How many dominoes?",
             "दस-दस की {a} पंक्तियाँ और {b} और। कुल कितने डोमिनो?",
             "দশটা করে {a} সারি আর আরও {b}টা। মোট কতগুলো ডোমিনো?"),
    "times": ("{a} dominoes with {b} dots each. How many dots in all?",
              "{a} डोमिनो, हर एक पर {b} बिंदु। कुल कितने बिंदु?",
              "{a}টা ডোমিনো, প্রতিটিতে {b}টা বিন্দু। মোট কতগুলো বিন্দু?"),
    "share": ("{a} laddoos shared equally by {b} friends. How many does each friend get?",
              "{a} लड्डू {b} दोस्तों में बराबर बाँटे। हर दोस्त को कितने मिलेंगे?",
              "{a}টা লাড্ডু {b} বন্ধুর মধ্যে সমান ভাগ করা হল। প্রত্যেকে কতগুলো পাবে?"),
    "multiple": ("Factor gate! Which number is in both the {a} table and the {b} table?",
                 "फ़ैक्टर गेट! कौन-सी संख्या {a} और {b} दोनों के पहाड़े में है?",
                 "ফ্যাক্টর গেট! কোন সংখ্যা {a} আর {b} দুটো নামতাতেই আছে?"),
    "fib": ("Spiral trail! Each domino is the two before it added. What comes next?",
            "घुमावदार रास्ता! हर डोमिनो पिछले दो का जोड़ है। आगे क्या आएगा?",
            "প্যাঁচানো পথ! প্রতিটি ডোমিনো আগের দুটোর যোগফল। এরপর কী আসবে?"),
    "prime": ("Prime shield! Which number is a prime number?",
              "प्राइम शील्ड! इनमें अभाज्य संख्या कौन-सी है?",
              "প্রাইম শিল্ড! এর মধ্যে মৌলিক সংখ্যা কোনটা?"),
    "int_plus": ("{a} plus negative {b}. Where do we land?",
                 "{a} में ऋण {b} जोड़ो। हम कहाँ पहुँचेंगे?",
                 "{a}-এর সাথে ঋণাত্মক {b} যোগ করো। আমরা কোথায় পৌঁছাব?"),
    "int_minus": ("{a} minus {b}. Where do we land?", "{a} में से {b} घटाओ। हम कहाँ पहुँचेंगे?",
                  "{a} থেকে {b} বিয়োগ করো। আমরা কোথায় পৌঁছাব?"),
    "int_minus_neg": ("{a} minus negative {b}. Where do we land?",
                      "{a} में से ऋण {b} घटाओ। हम कहाँ पहुँचेंगे?",
                      "{a} থেকে ঋণাত্মক {b} বিয়োগ করো। আমরা কোথায় পৌঁছাব?"),
    "ratio_up": ("A {a}-dot domino goes through a 1 to {b} ratio gate. How many dots now?",
                 "{a} बिंदु वाला डोमिनो 1 अनुपात {b} गेट से गुज़रा। अब कितने बिंदु?",
                 "{a} বিন্দুর ডোমিনো 1 অনুপাত {b} গেট পেরোল। এখন কতগুলো বিন্দু?"),
    "ratio_down": ("A {a}-dot domino goes through a {b} to 1 ratio gate. How many dots now?",
                   "{a} बिंदु वाला डोमिनो {b} अनुपात 1 गेट से गुज़रा। अब कितने बिंदु?",
                   "{a} বিন্দুর ডোমিনো {b} অনুপাত 1 গেট পেরোল। এখন কতগুলো বিন্দু?"),
    "balance": ("Balance it! x plus {a} equals {c}. What is x?",
                "तराज़ू बराबर करो! x और {a} मिलकर {c}। x क्या है?",
                "দাঁড়িপাল্লা সমান করো! x যোগ {a} সমান {c}। x কত?"),
    "balance2": ("Balance it! x plus x equals {c}. What is x?",
                 "तराज़ू बराबर करो! x और x मिलकर {c}। x क्या है?",
                 "দাঁড়িপাল্লা সমান করো! x যোগ x সমান {c}। x কত?"),
}
# The reason, said after a right answer (or after two tries)
EXPLAIN = {
    "count": ("{c} dots!", "{c} बिंदु!", "{c}টা বিন্দু!"),
    "more": ("{a} is more than {b}.", "{a}, {b} से ज़्यादा है।", "{a}, {b}-এর চেয়ে বেশি।"),
    "fewer": ("{a} is less than {b}.", "{a}, {b} से कम है।", "{a}, {b}-এর চেয়ে কম।"),
    "after": ("{c} comes after {a}.", "{a} के बाद {c} आता है।", "{a}-এর পরে আসে {c}।"),
    "before": ("{c} comes before {a}.", "{a} से पहले {c} आता है।", "{a}-এর আগে আসে {c}।"),
    "add": ("{a} plus {b} is {c}.", "{a} और {b} मिलकर {c}।", "{a} যোগ {b} সমান {c}।"),
    "topple": ("{a} take away {b} is {c}.", "{a} में से {b} गए, बचे {c}।",
               "{a} থেকে {b} গেলে থাকে {c}।"),
    "bonds": ("{a} and {b} make {c}.", "{a} और {b} मिलकर {c}।", "{a} আর {b} মিলে {c}।"),
    "tens": ("{a} tens and {b} ones make {c}.", "{a} दहाई और {b} इकाई मिलकर {c}।",
             "{a} দশক আর {b} একক মিলে {c}।"),
    "times": ("{b} added {a} times is {c}.", "{b} को {a} बार जोड़ो तो {c}।",
              "{b} কে {a} বার যোগ করলে {c}।"),
    "share": ("{a} shared by {b} is {c} each.", "{a} को {b} में बाँटो तो हर एक को {c}।",
              "{a} কে {b} জনে ভাগ করলে প্রত্যেকে {c}টা।"),
    "multiple": ("{c} is in the {a} table and in the {b} table.",
                 "{c}, {a} और {b} दोनों के पहाड़े में है।", "{c}, {a} আর {b} দুটো নামতাতেই আছে।"),
    "fib": ("{a} plus {b} is {c}.", "{a} और {b} मिलकर {c}।", "{a} যোগ {b} সমান {c}।"),
    "prime": ("{c} is prime. Only 1 times {c} makes it.", "{c} अभाज्य है। सिर्फ़ 1 गुणा {c} से बनता है।",
              "{c} মৌলিক। শুধু 1 গুণ {c} দিয়েই হয়।"),
    "integer": ("We land on {c}.", "हम {c} पर पहुँचे।", "আমরা {c}-এ পৌঁছালাম।"),
    "ratio": ("The domino now has {c} dots.", "अब डोमिनो पर {c} बिंदु हैं।",
              "এখন ডোমিনোতে {c}টা বিন্দু।"),
    "balance": ("x is {c}. Now both sides are equal.", "x बराबर {c}। अब दोनों तरफ़ बराबर।",
                "x সমান {c}। এখন দুই দিক সমান।"),
}
PRAISE = [("Yes!", "शाबाश!", "দারুণ!"), ("Well done!", "बहुत अच्छे!", "খুব ভালো!"),
          ("Super!", "बढ़िया!", "চমৎকার!"), ("You got it!", "सही जवाब!", "ঠিক উত্তর!")]
TRY_AGAIN = ("Not {x}. Try again!", "{x} नहीं। फिर से कोशिश करो!", "{x} নয়। আবার চেষ্টা করো!")
TRY_OTHER = ("Look again. Try the other one!", "ध्यान से देखो। दूसरा वाला चुनो!",
             "আবার দেখো। অন্যটা বেছে নাও!")
SHOW = ("The answer is {c}.", "सही जवाब है {c}।", "ঠিক উত্তর {c}।")
LEVEL_UP = ("Level {a}! You are a Maths Star!", "लेवल {a}! तुम मैथ्स स्टार हो!",
            "লেভেল {a}! তুমি অঙ্কের তারকা!")
START = ("Let's play with numbers! Listen, then tap the answer.",
         "चलो संख्याओं से खेलें! सुनो, फिर सही जवाब पर टैप करो।",
         "চলো সংখ্যা নিয়ে খেলি! শোনো, তারপর ঠিক উত্তরে টোকা দাও।")


def fmt(line, **kw):
  return tuple(s.format(**kw) for s in line)


def neg(n):
  """-3 written with a real minus sign, in brackets: (−3)."""
  return f"(−{abs(n)})" if n < 0 else str(n)


def num(n):
  return f"−{abs(n)}" if n < 0 else str(n)


# ---------------------------------------------------------------- the addition engine
def add_all(terms):
  """Every answer in this game is worked out by adding (the unified view)."""
  total = 0
  for t in terms:
    total += t
  return total


def take_away_by_adding(a, b):
  """a - b = a + (-b): the additive inverse."""
  return add_all([a, -b])


def times_by_adding(group, size):
  """group x size = size + size + ... (group times)."""
  return add_all([size] * group)


def share_by_taking_away(n, parts):
  """n / parts: take one round away from every friend until nothing is left;
  the number of rounds is each friend's share."""
  rounds, left = 0, n
  while left >= parts:
    left = add_all([left, -parts])
    rounds = add_all([rounds, 1])
  return rounds


def lcm(a, b):
  m = a
  while m % b:
    m = add_all([m, a])
  return m


def is_prime(n):
  return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def factor_pair(n):
  for d in range(int(n ** 0.5), 1, -1):
    if n % d == 0:
      return d, n // d
  return 1, n


def split_dots(n, max_half=6):
  """Two halves of a domino that add up to n (each half 0..9)."""
  if n <= max_half:
    a = random.randint(0, n) if n > 1 else n
    return a, n - a
  lo, hi = max(0, n - 9), min(9, n)
  a = random.randint(lo, hi)
  return a, n - a


# Pip spots in a half (unit square), standard dice layouts, 3x3 for 7-9
_SPOTS = {
    0: [], 1: [(0.5, 0.5)], 2: [(0.27, 0.27), (0.73, 0.73)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.27, 0.22), (0.73, 0.22), (0.27, 0.5), (0.73, 0.5), (0.27, 0.78), (0.73, 0.78)],
    7: [(0.22, 0.22), (0.5, 0.22), (0.78, 0.22), (0.5, 0.5), (0.22, 0.78), (0.5, 0.78),
        (0.78, 0.78)],
    8: [(0.22, 0.22), (0.5, 0.22), (0.78, 0.22), (0.22, 0.5), (0.78, 0.5), (0.22, 0.78),
        (0.5, 0.78), (0.78, 0.78)],
    9: [(x, y) for y in (0.22, 0.5, 0.78) for x in (0.22, 0.5, 0.78)],
}


def pip_spots(rect, a, b):
  """Screen points of every pip (top half a, bottom half b; left/right when wide)."""
  out = []
  wide = rect.w > rect.h
  for k, n in enumerate((a, b)):
    if n is None:
      continue
    if wide:
      half = pygame.Rect(rect.x + k * rect.w // 2, rect.y, rect.w // 2, rect.h)
    else:
      half = pygame.Rect(rect.x, rect.y + k * rect.h // 2, rect.w, rect.h // 2)
    side = min(half.w, half.h) * 0.86
    ox, oy = half.centerx - side / 2, half.centery - side / 2
    out += [(ox + fx * side, oy + fy * side) for fx, fy in _SPOTS[n]]
  return out


def draw_domino(s, rect, a, b, colour=(250, 250, 245), lit=0, pip=INK, font=None):
  """A domino face with pips; the first `lit` pips glow (counting aloud).
  A half given as None shows a big "?"."""
  r = max(4, min(rect.w, rect.h) // 6)
  pygame.draw.rect(s, (30, 30, 50), rect.move(3, 4), border_radius=r)
  pygame.draw.rect(s, colour, rect, border_radius=r)
  pygame.draw.rect(s, INK, rect, 3, border_radius=r)
  wide = rect.w > rect.h
  if wide:
    pygame.draw.line(s, INK, (rect.centerx, rect.y + 6), (rect.centerx, rect.bottom - 6), 3)
  else:
    pygame.draw.line(s, INK, (rect.x + 6, rect.centery), (rect.right - 6, rect.centery), 3)
  pr = max(2, int(min(rect.w, rect.h) * (0.07 if max(a or 0, b or 0) <= 6 else 0.055)))
  for i, (x, y) in enumerate(pip_spots(rect, a, b)):
    if i < lit:
      pygame.draw.circle(s, YELLOW, (int(x), int(y)), pr + 3)
      pygame.draw.circle(s, (230, 90, 30), (int(x), int(y)), pr)
    else:
      pygame.draw.circle(s, pip, (int(x), int(y)), pr)
  if font is not None:
    for k, n in enumerate((a, b)):
      if n is None:
        c = ((rect.x + rect.w * (0.25 + 0.5 * k), rect.centery) if wide
             else (rect.centerx, rect.y + rect.h * (0.25 + 0.5 * k)))
        t = font.render("?", True, (230, 90, 30))
        s.blit(t, t.get_rect(center=(int(c[0]), int(c[1]))))


def fall_blit(s, surf, foot, fall):
  """Blits an upright piece standing on `foot` (its bottom centre), tipped right
  by fall 0..1 round its bottom-right corner."""
  if fall <= 0:
    s.blit(surf, surf.get_rect(midbottom=foot))
    return
  w, h = surf.get_size()
  ang = math.radians(86 * min(1.0, fall))
  rot = pygame.transform.rotate(surf, -math.degrees(ang))
  px, py = foot[0] + w / 2, foot[1]                  # pivot: bottom-right corner
  cx = px + (h / 2) * math.sin(ang) - (w / 2) * math.cos(ang)
  cy = py - (h / 2) * math.cos(ang) - (w / 2) * math.sin(ang)
  s.blit(rot, rot.get_rect(center=(int(cx), int(cy))))


_SMALL = {}


def small_domino(h, colour, label=None, font=None, anti=False):
  """A little standing domino (cached), optionally with a number on it.
  anti: a translucent blue anti-domino (a negative one)."""
  key = (h, colour, label, anti)
  surf = _SMALL.get(key)
  if surf is None:
    if len(_SMALL) > 300:
      _SMALL.clear()
    w = max(8, h // 2 if label is not None else h // 3)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if anti:
      pygame.draw.rect(surf, (*ANTI, 150), (0, 0, w, h), border_radius=4)
      pygame.draw.rect(surf, (200, 230, 255, 230), (0, 0, w, h), 2, border_radius=4)
    else:
      dark = tuple(int(c * 0.55) for c in colour)
      pygame.draw.rect(surf, dark, (0, 0, w, h), border_radius=4)
      pygame.draw.rect(surf, colour, (1, 1, w - 2, h - 2), border_radius=4)
    if label is not None and font is not None:
      t = font.render(label, True, WHITE)
      if t.get_width() > w - 2:
        t = pygame.transform.smoothscale(t, (w - 2, max(2, int(t.get_height() * (w - 2) / t.get_width()))))
      surf.blit(t, t.get_rect(center=(w // 2, h // 2)))
    else:
      pygame.draw.line(surf, WHITE, (2, h // 2), (w - 3, h // 2), 1)
      pygame.draw.circle(surf, WHITE, (w // 2, h // 4), max(1, w // 6))
      pygame.draw.circle(surf, WHITE, (w // 2, 3 * h // 4), max(1, w // 6))
    _SMALL[key] = surf
  return surf


def face_surface(w, h, a, b):
  surf = pygame.Surface((w + 4, h + 5), pygame.SRCALPHA)
  draw_domino(surf, pygame.Rect(0, 0, w, h), a, b)
  return surf


def draw_laddoo(s, centre, r):
  pygame.draw.circle(s, (200, 110, 20), centre, r)
  pygame.draw.circle(s, LADDOO, (centre[0] - 1, centre[1] - 1), r - 2)
  pygame.draw.circle(s, (255, 220, 140), (centre[0] - r // 3, centre[1] - r // 3), max(1, r // 4))


def draw_friend(s, centre, r, colour):
  x, y = centre
  pygame.draw.circle(s, (240, 190, 140), (x, y), r)
  pygame.draw.circle(s, INK, (x - r // 3, y - r // 5), max(2, r // 8))
  pygame.draw.circle(s, INK, (x + r // 3, y - r // 5), max(2, r // 8))
  pygame.draw.arc(s, INK, (x - r // 2, y - r // 4, r, r * 2 // 3), math.pi * 1.1, math.pi * 1.9, 2)
  pygame.draw.arc(s, colour, (x - r - 2, y - r - 4, 2 * r + 4, 2 * r), 0, math.pi, max(3, r // 3))


def draw_shield(s, centre, r, colour=SHIELD, glow=0.0):
  x, y = centre
  pts = [(x - r, y - r * 0.8), (x, y - r * 1.1), (x + r, y - r * 0.8), (x + r * 0.85, y + r * 0.2),
         (x, y + r * 1.15), (x - r * 0.85, y + r * 0.2)]
  if glow > 0:
    halo = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*colour, int(90 * glow)), (r * 2, r * 2), int(r * 1.9))
    s.blit(halo, (x - r * 2, y - r * 2))
  pygame.draw.polygon(s, colour, pts)
  pygame.draw.polygon(s, WHITE, pts, 3)


def wrap(font, text, max_w):
  words, lines, cur = text.split(), [], ""
  for w in words:
    t = (cur + " " + w).strip()
    if font.size(t)[0] <= max_w or not cur:
      cur = t
    else:
      lines.append(cur)
      cur = w
  if cur:
    lines.append(cur)
  return lines


class MathsGame:
  """Maths Play; draws inside the play area like Find it! and Cross the Road."""

  def __init__(self, game):
    self.g = game
    self.q = None
    self._cascade = []
    self.new_question(first=True)

  # ------------------------------------------------------------ progress
  @property
  def data(self):
    d = self.g.progress.data.setdefault("maths", {})
    for k, v in (("level", 1), ("right", 0), ("asked", 0), ("run", 0), ("miss", 0),
                 ("best", 1), ("solved", 0)):
      d.setdefault(k, v)
    d["level"] = max(1, min(LEVELS, d["level"]))
    return d

  def say(self, line, extra=None):
    en, hi, bn = line
    if extra:
      en, hi, bn = f"{extra[0]} {en}", f"{extra[1]} {hi}", f"{extra[2]} {bn}"
    native = {"hi": hi, "bn": bn}.get(self.g.lang)
    self.g.say(en, native)

  # ------------------------------------------------------------ questions
  def make(self, kind, level):
    """A question: kind, numbers, the right answer c, choices, the sum (eq)
    and its breakdown into adding (steps)."""
    q = {"kind": kind, "level": level, "steps": None, "show": None, "neg_ok": False}
    if kind == "count":
      c = random.randint(1, 6 if level == 1 else 12)
      a, b = split_dots(c, 6)
      q.update(a=a, b=b, c=add_all([a, b]), ask=ASK["count"], explain=fmt(EXPLAIN["count"], c=c),
               eq=f"{a} + {b} = {c}" if a and b else str(c))
    elif kind in ("more", "fewer"):
      top = 6 if level == 1 else 12
      x, y = random.sample(range(1, top + 1), 2)
      want = max(x, y) if kind == "more" else min(x, y)
      other = y if want == x else x
      q.update(totals=(x, y), halves=[split_dots(x, 6), split_dots(y, 6)],
               c=0 if want == x else 1, ask=ASK[kind],
               explain=fmt(EXPLAIN[kind], a=want, b=other),
               eq=f"{want} {'>' if kind == 'more' else '<'} {other}")
    elif kind in ("after", "before"):
      top = 10 if level == 1 else 20
      a = random.randint(1, top - 1) if kind == "after" else random.randint(2, top)
      c = add_all([a, 1 if kind == "after" else -1])
      q.update(a=a, c=c, ask=fmt(ASK[kind], a=a), explain=fmt(EXPLAIN[kind], a=a, c=c),
               eq=f"{a} + 1 = {c}" if kind == "after" else f"{a} − 1 = {c}")
    elif kind == "add":
      c = random.randint(2, 10 if level <= 2 else 18)
      a, b = split_dots(c, 9)
      if a == 0 or b == 0:
        a, b = c - 1, 1
      q.update(a=a, b=b, c=add_all([a, b]), ask=fmt(ASK["add"], a=a, b=b),
               explain=fmt(EXPLAIN["add"], a=a, b=b, c=c), eq=f"{a} + {b} = {c}")
    elif kind == "topple":
      n = random.randint(3, 10 if level <= 2 else 18)
      k = random.randint(1, n - 1)
      c = take_away_by_adding(n, k)
      q.update(a=n, b=k, c=c, falls=sorted(random.sample(range(n), k)),
               ask=fmt(ASK["topple"], a=n, b=k), explain=fmt(EXPLAIN["topple"], a=n, b=k, c=c),
               eq=f"{n} − {k} = {c}")
      if level >= 6:
        q["steps"] = f"{n} − {k} = {n} + (−{k}) = {c}"
    elif kind == "bonds":
      c = random.randint(5, 10)
      a = random.randint(1, c - 1)
      b = take_away_by_adding(c, a)
      q.update(a=a, b=b, c=b, total=c, ask=fmt(ASK["bonds"], a=a, c=c),
               explain=fmt(EXPLAIN["bonds"], a=a, b=b, c=c), eq=f"{a} + {b} = {c}")
    elif kind == "tens":
      t = random.randint(1, 4 if level <= 3 else 9)
      o = random.randint(1, 9)
      c = add_all([10] * t + [o])
      q.update(a=t, b=o, c=c, ask=fmt(ASK["tens"], a=t, b=o),
               explain=fmt(EXPLAIN["tens"], a=t, b=o, c=c), eq=f"{t} tens + {o} ones = {c}",
               steps=" + ".join(["10"] * t + ([str(o)] if o else [])) + f" = {c}")
    elif kind == "times":
      top = 5 if level <= 4 else 10
      g = random.randint(2, top if level <= 5 else 9)
      p = random.randint(1, top)
      c = times_by_adding(g, p)
      q.update(a=g, b=p, c=c, halves=split_dots(p, 6), ask=fmt(ASK["times"], a=g, b=p),
               explain=fmt(EXPLAIN["times"], a=g, b=p, c=c), eq=f"{g} × {p} = {c}",
               steps=" + ".join([str(p)] * g) + f" = {c}")
    elif kind == "share":
      g = random.randint(2, 4 if level <= 4 else 5)
      each = random.randint(1, 5 if level <= 4 else 6)
      n = times_by_adding(g, each)
      c = share_by_taking_away(n, g)
      q.update(a=n, b=g, c=c, ask=fmt(ASK["share"], a=n, b=g),
               explain=fmt(EXPLAIN["share"], a=n, b=g, c=c), eq=f"{n} ÷ {g} = {c}",
               steps=f"{n} " + " ".join([f"− {g}"] * c) + f" = 0, so {c} rounds")
    elif kind == "multiple":
      a, b = random.choice([(2, 3), (2, 5), (3, 4), (3, 5), (2, 7), (4, 5), (4, 6), (3, 6),
                            (2, 9), (5, 6), (3, 8)])
      c = lcm(a, b)
      pool = [n for n in range(2, c + 12) if n != c and not (n % a == 0 and n % b == 0)]
      near = sorted(pool, key=lambda n: (n % a != 0 and n % b != 0, abs(n - c)))[:6]
      choices = random.sample(near, 3) + [c]
      random.shuffle(choices)
      q.update(a=a, b=b, c=c, choices=choices, ask=fmt(ASK["multiple"], a=a, b=b),
               explain=fmt(EXPLAIN["multiple"], a=a, b=b, c=c),
               eq=f"{a} × {c // a} = {c} = {b} × {c // b}")
    elif kind == "fib":
      x, y = random.choice([(1, 1), (1, 2), (2, 3), (1, 3), (2, 2)])
      seq = [x, y]
      while len(seq) < 6:
        seq.append(add_all(seq[-2:]))
      q.update(seq=seq, a=seq[3], b=seq[4], c=seq[5], ask=ASK["fib"],
               explain=fmt(EXPLAIN["fib"], a=seq[3], b=seq[4], c=seq[5]),
               eq=f"{seq[3]} + {seq[4]} = {seq[5]}")
    elif kind == "prime":
      p = random.choice(PRIMES[1:] if level >= 7 else PRIMES[:8])
      comps = [n for n in range(4, 31) if not is_prime(n) and abs(n - p) <= 12]
      choices = random.sample(comps, 3) + [p]
      random.shuffle(choices)
      q.update(c=p, choices=choices, ask=ASK["prime"], explain=fmt(EXPLAIN["prime"], c=p),
               eq=f"{p} = 1 × {p}  (prime shield)")
    elif kind == "integer":
      form = random.choice(["int_plus", "int_minus", "int_minus_neg"])
      if form == "int_plus":
        a, b = random.randint(-3, 8), random.randint(1, 9)
        c = add_all([a, -b])
        show = f"{num(a)} + (−{b}) = ?"
        steps = f"{num(a)} + (−{b}) = {num(c)}"
      elif form == "int_minus":
        a, b = random.randint(0, 6), random.randint(1, 9)
        c = take_away_by_adding(a, b)
        show = f"{a} − {b} = ?"
        steps = f"{a} − {b} = {a} + (−{b}) = {num(c)}"
      else:
        a, b = random.randint(-6, 5), random.randint(1, 5)
        c = add_all([a, b])
        show = f"{num(a)} − (−{b}) = ?"
        steps = f"{num(a)} − (−{b}) = {num(a)} + {b} = {num(c)}"
      q.update(a=a, b=b, c=c, form=form, ask=fmt(ASK[form], a=a, b=b), neg_ok=True,
               explain=fmt(EXPLAIN["integer"], c=c), show=show, eq=steps.split(" = ")[0] + f" = {num(c)}",
               steps=steps)
    elif kind == "ratio":
      if random.random() < 0.5:
        v, k = random.randint(1, 5), random.randint(2, 4)
        c = times_by_adding(k, v)
        q.update(a=v, b=k, c=c, up=True, ask=fmt(ASK["ratio_up"], a=v, b=k),
                 show=f"1 : {k}", eq=f"{v} × {k} = {c}",
                 steps=" + ".join([str(v)] * k) + f" = {c}")
      else:
        k, m = random.randint(2, 4), random.randint(1, 5)
        v = times_by_adding(k, m)
        c = share_by_taking_away(v, k)
        q.update(a=v, b=k, c=c, up=False, ask=fmt(ASK["ratio_down"], a=v, b=k),
                 show=f"{k} : 1", eq=f"{v} ÷ {k} = {c}",
                 steps=f"{v} " + " ".join([f"− {k}"] * c) + f" = 0, so {c}")
      q["explain"] = fmt(EXPLAIN["ratio"], c=c)
    elif kind == "balance":
      if random.random() < 0.6:
        a, x = random.randint(1, 9), random.randint(1, 9)
        c = add_all([x, a])
        q.update(a=a, c=x, total=c, two=False, ask=fmt(ASK["balance"], a=a, c=c),
                 show=f"x + {a} = {c}", eq=f"x = {x}",
                 steps=f"x = {c} + (−{a}) = {x}")
      else:
        x = random.randint(2, 9)
        c = add_all([x, x])
        q.update(a=0, c=x, total=c, two=True, ask=fmt(ASK["balance2"], c=c),
                 show=f"x + x = {c}", eq=f"x = {x}", steps=f"{x} + {x} = {c}")
      q["explain"] = fmt(EXPLAIN["balance"], c=q["c"])
    if "choices" not in q and kind not in ("more", "fewer"):
      q["choices"] = self.choices(q["c"], q["neg_ok"])
    return q

  def choices(self, c, neg_ok=False):
    near = [c - 1, c + 1, c - 2, c + 2]
    random.shuffle(near)
    picks = []
    for x in near + [c + 3, c - 3, c + 10, c + 4, c + 5]:
      if (neg_ok or x >= 0) and x != c and x not in picks:
        picks.append(x)
      if len(picks) == 3:
        break
    out = picks + [c]
    random.shuffle(out)
    return out

  def new_question(self, first=False):
    g = self.g
    lvl = self.data["level"]
    last = self.q["kind"] if self.q else None
    kinds = [k for k in KINDS[lvl] if k != last] or KINDS[lvl]
    self.q = self.make(random.choice(kinds), lvl)
    self.wrong = set()
    self.shake = {}
    self.solved_at = None
    self.revealed_at = None
    self.asked_at = time.time()
    self.level_up_at = None
    self._lit = 0
    self._cascade = []
    self._fired = set()
    g.particles.texts = []          # the last question's running totals
    g.banner_override = "MATHS PLAY"
    g.announced_at = time.time()
    self.ask_after = None
    if first and "maths_start" not in g.progress.data.setdefault("guides", []):
      self.say(START)
      g.progress.data["guides"].append("maths_start")
      g.progress.save()
      self.ask_after = time.time() + 3.6
    else:
      self.ask()

  def ask(self):
    self.say(self.q["ask"])

  def set_level(self, lvl):
    lvl = max(1, min(LEVELS, lvl))
    d = self.data
    if lvl != d["level"]:
      d["level"] = lvl
      d["run"] = d["miss"] = 0
      self.g.progress.save()
    self.g.sfx.play("switch")
    self.new_question()

  @property
  def shown(self):
    """True once the answer is on screen (solved, or shown after two tries)."""
    return self.solved_at is not None or self.revealed_at is not None

  @property
  def done_at(self):
    return self.solved_at if self.solved_at is not None else self.revealed_at

  # ------------------------------------------------------------ layout
  def area(self):
    import modes
    return modes.g_area()

  def layout(self):
    a = self.area()
    lay = {"area": a}
    foot_h = 46
    lay["foot"] = pygame.Rect(a.x + 8, a.bottom - foot_h - 6, a.w - 16, foot_h)
    cw = min(48, (min(lay["foot"].w, 520) - 150) // LEVELS - 5)
    lay["chips"] = [pygame.Rect(lay["foot"].x + 4 + i * (cw + 5), lay["foot"].y + 5, cw,
                                foot_h - 10) for i in range(LEVELS)]
    bh = int(min(84, a.h * 0.12))
    bw = min(120, (a.w - 16 - 3 * 12) // 4)
    row_w = 4 * bw + 3 * 12
    top = lay["foot"].y - bh - 12
    lay["answers"] = [pygame.Rect(a.centerx - row_w // 2 + i * (bw + 12), top, bw, bh)
                      for i in range(4)]
    lay["prompt_y"] = a.y + 12
    lay["eq_y"] = top - 26
    lay["steps_y"] = top - 60
    scene_top = a.y + 92
    lay["scene"] = pygame.Rect(a.x + 10, scene_top, a.w - 20, top - 82 - scene_top)
    return lay

  def domino_rects(self, lay):
    """The two dominoes of a more/fewer question."""
    sc = lay["scene"].copy()
    sc.h += 60                      # these questions have no number buttons
    h = int(min(sc.h * 0.85, 320))
    w = h // 2
    gap = max(40, sc.w // 6)
    return [pygame.Rect(sc.centerx - gap // 2 - w, sc.centery - h // 2, w, h),
            pygame.Rect(sc.centerx + gap // 2, sc.centery - h // 2, w, h)]

  # ------------------------------------------------------------ input
  def press(self, pos):
    g = self.g
    lay = self.layout()
    for i, chip in enumerate(lay["chips"]):
      if chip.collidepoint(pos):
        self.set_level(i + 1)
        return
    if self.shown:
      if time.time() - self.done_at > 0.8:
        g.sfx.play("click")
        self.new_question()
      return
    if self.q["kind"] in ("more", "fewer"):
      targets = self.domino_rects(lay)
    else:
      targets = lay["answers"]
    for i, r in enumerate(targets):
      if r.collidepoint(pos) and i not in self.wrong:
        self.answer(i, r)
        return

  def answer(self, i, rect):
    g = self.g
    q = self.q
    d = self.data
    picked = i if q["kind"] in ("more", "fewer") else q["choices"][i]
    if picked == q["c"]:
      first = not self.wrong
      self.solved_at = time.time()
      d["asked"] += 1
      d["solved"] += 1
      if first:
        d["right"] += 1
        d["run"] += 1
        d["miss"] = 0
      g.sfx.play("chime")
      g.particles.burst(rect.centerx, rect.centery, n=40)
      g.particles.confetti(self.area(), n=90)
      extra = random.choice(PRAISE)
      if first and d["run"] >= LEVEL_UP_RUN and d["level"] < LEVELS:
        d["level"] += 1
        d["best"] = max(d["best"], d["level"])
        d["run"] = 0
        self.level_up_at = time.time()
        ex = q["explain"]
        self.say(fmt(LEVEL_UP, a=d["level"]), tuple(f"{p} {e}" for p, e in zip(extra, ex)))
      else:
        self.say(q["explain"], extra)
      g.progress.save()
      return
    self.wrong.add(i)
    self.shake[i] = time.time()
    g.sfx.play("tip")
    if len(self.wrong) == 1:
      d["run"] = 0
      d["miss"] += 1
      if d["miss"] >= 3 and d["level"] > 1:      # three misses in a row: a gentler level
        d["level"] -= 1
        d["miss"] = 0
      g.progress.save()
    if q["kind"] in ("more", "fewer"):
      self.say(TRY_OTHER)
    elif len(self.wrong) >= 2:
      d["asked"] += 1
      self.revealed_at = time.time()
      self.say(q["explain"], fmt(SHOW, c=q["c"]))
      g.progress.save()
    else:
      self.say(fmt(TRY_AGAIN, x=picked))

  # ------------------------------------------------------------ update
  def update(self, now):
    if self.ask_after and now >= self.ask_after:
      self.ask_after = None
      self.ask()
    if not self.shown:
      return
    t = now - self.done_at
    if self.solved_at is not None:
      wait = NEXT_AFTER + (1.5 if self.level_up_at else 0.0) + CASCADE_STEP * len(self._cascade)
      if t > wait:
        self.new_question()
        return
    q = self.q
    if q["kind"] in ("count", "add", "bonds"):           # count the dots aloud
      k = int(t / 0.16)
      top = q["c"] if q["kind"] != "bonds" else q["total"]
      if k > self._lit and self._lit < top:
        self._lit = min(top, k)
        self.g.sfx.play("pop", min(11, self._lit))
    for i, (x, y, label) in enumerate(self._cascade):  # floating running totals
      if i not in self._fired and t >= 0.3 + i * CASCADE_STEP:
        self._fired.add(i)
        self.g.sfx.play("clack", min(i, 11))
        if label:
          self.g.particles.text(x, y, label, YELLOW)

  def cascade_fall(self, i, now):
    """0..1: how far domino i of the cascade has fallen."""
    if not self.shown:
      return 0.0
    t = now - self.done_at - 0.3 - i * CASCADE_STEP
    return max(0.0, min(1.0, t / 0.3))

  # ------------------------------------------------------------ drawing
  def draw(self, s, now):
    g = self.g
    lay = self.layout()
    a = lay["area"]
    veil = pygame.Surface(a.size, pygame.SRCALPHA)
    veil.fill((*g.theme["bg"], 215))
    s.blit(veil, a.topleft)
    q = self.q
    font = g.font_at(21)
    for n, line in enumerate(wrap(font, q["ask"][0], a.w - 30)[:3]):
      t = font.render(line, True, YELLOW)
      s.blit(t, t.get_rect(center=(a.centerx, lay["prompt_y"] + 13 + n * 25)))
    self._cascade = []
    getattr(self, "scene_" + {"fewer": "more", "before": "after"}.get(q["kind"], q["kind"]))(
        s, lay, now)
    if self.shown:
      self.draw_sums(s, lay, now)
    if q["kind"] not in ("more", "fewer"):
      self.draw_answers(s, lay, now)
    self.draw_footer(s, lay, now)
    if self.level_up_at and now - self.level_up_at < 3.5:
      self.draw_level_badge(s, lay, now)

  def draw_sums(self, s, lay, now):
    """The sum, then its breakdown into adding, written out term by term."""
    g = self.g
    q = self.q
    a = lay["area"]
    eq_font = g.font_at(30 if len(q["eq"]) < 22 else 22)
    eq = eq_font.render(q["eq"], True, GREEN if self.solved_at is not None else WHITE)
    if eq.get_width() > a.w - 20:
      eq = pygame.transform.smoothscale(eq, (a.w - 20, int(eq.get_height() * (a.w - 20) / eq.get_width())))
    s.blit(eq, eq.get_rect(center=(a.centerx, lay["eq_y"])))
    steps = q.get("steps")
    if steps and steps != q["eq"]:
      tokens = steps.split(" ")
      k = int((now - self.done_at) / 0.12) + 1
      text = " ".join(tokens[:k])
      f = g.font_at(19)
      lines = wrap(f, text, a.w - 30)[-2:]
      box_h = 26 * len(lines) + 8
      box = pygame.Rect(0, 0, min(a.w - 16, max(f.size(l)[0] for l in lines) + 28), box_h)
      box.center = (a.centerx, lay["steps_y"] - (box_h - 34) // 2)
      pygame.draw.rect(s, (30, 40, 80), box, border_radius=12)
      pygame.draw.rect(s, YELLOW, box, 2, border_radius=12)
      for n, line in enumerate(lines):
        t = f.render(line, True, WHITE)
        s.blit(t, t.get_rect(center=(box.centerx, box.y + 17 + n * 26)))

  def draw_answers(self, s, lay, now):
    g = self.g
    q = self.q
    for i, r in enumerate(lay["answers"]):
      dx = 0
      if i in self.shake and now - self.shake[i] < 0.4:
        dx = int(8 * math.sin((now - self.shake[i]) * 50))
      rr = r.move(dx, 0)
      val = q["choices"][i]
      good = val == q["c"] and self.shown
      if good:
        col = GREEN
      elif i in self.wrong:
        col = RED
      else:
        col = TILE_COLOURS[(i * 3 + abs(q["c"])) % len(TILE_COLOURS)]
      if good and self.solved_at is not None:
        p = int(6 * math.sin(now * 8))
        rr = rr.inflate(p, p)
      pygame.draw.rect(s, (20, 20, 40), rr.move(3, 4), border_radius=18)
      pygame.draw.rect(s, col, rr, border_radius=18)
      pygame.draw.rect(s, WHITE, rr, 3, border_radius=18)
      label = num(val)
      font = g.font_at(36 if len(label) <= 2 else 28)
      o = font.render(label, True, INK)
      t = font.render(label, True, WHITE)
      s.blit(o, o.get_rect(center=(rr.centerx + 2, rr.centery + 2)))
      s.blit(t, t.get_rect(center=rr.center))
      if q["kind"] == "prime" and self.shown:     # show why the others are not prime
        if is_prime(val):
          draw_shield(s, (rr.right - 12, rr.y + 12), 9, glow=0.6)
        else:
          x, y = factor_pair(val)
          sm = g.small_font.render(f"{x} × {y}", True, WHITE)
          s.blit(sm, sm.get_rect(center=(rr.centerx, rr.bottom - 10)))

  def draw_footer(self, s, lay, now):
    g = self.g
    d = self.data
    f = g.font_at(19)
    for i, chip in enumerate(lay["chips"]):
      on = d["level"] == i + 1
      pygame.draw.rect(s, YELLOW if on else (90, 110, 160), chip, border_radius=11)
      pygame.draw.rect(s, WHITE, chip, 2, border_radius=11)
      t = f.render(str(i + 1), True, INK if on else WHITE)
      s.blit(t, t.get_rect(center=chip.center))
    right = lay["foot"].right
    score = g.font_at(19).render(str(d["right"]), True, YELLOW)
    sr = score.get_rect(midright=(right - 4, lay["foot"].centery - 9))
    s.blit(score, sr)
    g.draw_star(s, (sr.x - 12, sr.centery), 8)
    name = g.small_font.render(LEVEL_NAMES[d["level"]], True, WHITE)
    max_w = right - lay["chips"][-1].right - 8
    if name.get_width() > max_w:
      name = pygame.transform.smoothscale(name, (max_w, name.get_height()))
    s.blit(name, name.get_rect(midright=(right - 4, lay["foot"].centery + 11)))

  def draw_level_badge(self, s, lay, now):
    g = self.g
    a = lay["area"]
    k = min(1.0, (now - self.level_up_at) / 0.4)
    r = pygame.Rect(0, 0, int(280 * k), int(96 * k))
    r.center = (a.centerx, a.y + a.h // 3)
    if r.w < 20:
      return
    pygame.draw.rect(s, (255, 120, 60), r, border_radius=24)
    pygame.draw.rect(s, WHITE, r, 4, border_radius=24)
    t = g.font_at(34).render(f"Level {self.data['level']}!", True, WHITE)
    s.blit(t, t.get_rect(center=(r.centerx, r.centery - 10)))
    sub = g.small_font.render(LEVEL_NAMES[self.data["level"]], True, WHITE)
    s.blit(sub, sub.get_rect(center=(r.centerx, r.centery + 22)))

  # --- the pictures for each kind of question ---------------------------------------
  def big_domino_rect(self, sc, wide=False):
    if wide:
      w = int(min(sc.w * 0.8, sc.h * 1.6, 360))
      return pygame.Rect(sc.centerx - w // 2, sc.centery - w // 4 - 10, w, w // 2)
    h = int(min(sc.h * 0.95, 320))
    return pygame.Rect(sc.centerx - h // 4, sc.centery - h // 2, h // 2, h)

  def scene_count(self, s, lay, now):
    q = self.q
    draw_domino(s, self.big_domino_rect(lay["scene"]), q["a"], q["b"], lit=self._lit)

  def scene_add(self, s, lay, now):
    q = self.q
    g = self.g
    r = self.big_domino_rect(lay["scene"], wide=True)
    draw_domino(s, r, q["a"], q["b"], lit=self._lit)
    f = g.font_at(30)
    for k, n in enumerate((q["a"], q["b"])):
      t = f.render(str(n), True, WHITE)
      s.blit(t, t.get_rect(center=(r.x + r.w * (0.25 + 0.5 * k), r.bottom + 24)))
    plus = f.render("+", True, YELLOW)
    s.blit(plus, plus.get_rect(center=(r.centerx, r.bottom + 24)))

  def scene_bonds(self, s, lay, now):
    q = self.q
    g = self.g
    r = self.big_domino_rect(lay["scene"], wide=True)
    b = q["b"] if self.shown else None
    draw_domino(s, r, q["a"], b, lit=self._lit, font=g.font_at(int(r.h * 0.6)))
    f = g.font_at(28)
    t = f.render(f"{q['a']} + {q['b'] if self.shown else '?'} = {q['total']}", True, WHITE)
    s.blit(t, t.get_rect(center=(r.centerx, r.bottom + 26)))

  def scene_more(self, s, lay, now):
    q = self.q
    g = self.g
    for i, r in enumerate(self.domino_rects(lay)):
      a, b = q["halves"][i]
      dx = 0
      if i in self.shake and now - self.shake[i] < 0.4:
        dx = int(8 * math.sin((now - self.shake[i]) * 50))
      rr = r.move(dx, 0)
      if i == q["c"] and self.solved_at is not None:
        pygame.draw.rect(s, GREEN, rr.inflate(18, 18), border_radius=18)
      draw_domino(s, rr, a, b, colour=(255, 225, 225) if i in self.wrong else (250, 250, 245))
      if self.solved_at is not None or i in self.wrong:
        t = g.font_at(30).render(str(q["totals"][i]), True, WHITE)
        s.blit(t, t.get_rect(center=(rr.centerx, rr.bottom + 24)))

  def scene_after(self, s, lay, now):
    """A number line of domino tiles with one empty tile."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    if q["kind"] == "after":
      nums = [n for n in (q["a"] - 2, q["a"] - 1, q["a"]) if n >= 0] + [None]
    else:
      nums = [None, q["a"], q["a"] + 1, q["a"] + 2]
    w = min(84, (sc.w - 20) // len(nums) - 10)
    h = int(w * 1.5)
    x0 = sc.centerx - (len(nums) * (w + 10) - 10) // 2
    f = g.font_at(int(w * 0.5))
    for k, n in enumerate(nums):
      r = pygame.Rect(x0 + k * (w + 10), sc.centery - h // 2, w, h)
      empty = n is None
      show = q["c"] if empty and self.shown else n
      col = (255, 250, 220) if not empty else ((200, 255, 210) if show is not None else (90, 100, 140))
      pygame.draw.rect(s, (20, 20, 40), r.move(3, 4), border_radius=12)
      pygame.draw.rect(s, col, r, border_radius=12)
      pygame.draw.rect(s, YELLOW if empty else INK, r, 3, border_radius=12)
      t = f.render("?" if show is None else str(show), True, YELLOW if show is None else INK)
      s.blit(t, t.get_rect(center=r.center))
    y = sc.centery + h // 2 + 22
    end = x0 + len(nums) * (w + 10) - 10
    pygame.draw.line(s, WHITE, (x0, y), (end, y), 3)
    pygame.draw.polygon(s, WHITE, [(end + 10, y), (end - 4, y - 8), (end - 4, y + 8)])
    lbl = g.small_font.render("+1 each step", True, WHITE)
    s.blit(lbl, lbl.get_rect(midtop=(sc.centerx, y + 6)))

  def scene_topple(self, s, lay, now):
    """n dominoes in a row; the red ones fall (take away)."""
    q = self.q
    sc = lay["scene"]
    n = q["a"]
    per_row = n if n <= 10 else (n + 1) // 2
    rows = 1 if n <= 10 else 2
    gap = min(36, (sc.w - 20) // per_row)
    h = min(int(gap * 1.9), int(sc.h / rows * 0.6))
    t = now - self.asked_at - 1.0          # they fall a moment after the question
    nf = len(q["falls"])
    for i in range(n):
      row, col = divmod(i, per_row)
      x = int(sc.centerx - (per_row - 1) * gap / 2 + col * gap)
      foot_y = sc.y + int(sc.h * (0.6 if rows == 1 else (0.45 + 0.45 * row)))
      fall = 0.0
      if i in q["falls"]:
        k = q["falls"].index(i)
        fall = max(0.0, min(1.0, (t - k * 1.4 / max(1, nf)) / 0.35))
      colour = (230, 80, 80) if i in q["falls"] else TILE_COLOURS[i % len(TILE_COLOURS)]
      fall_blit(s, small_domino(h, colour), (x, foot_y), fall)
      if self.shown and i not in q["falls"]:
        self.g.draw_star(s, (x, foot_y - h - 12), 7)

  def scene_tens(self, s, lay, now):
    """t rows of ten small dominoes and o more."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    rows = q["a"] + (1 if q["b"] else 0)
    gap = min(30, (sc.w - 70) // 10)
    rh = min(int(gap * 1.6), (sc.h - 10) // max(1, rows))
    h = int(rh * 0.8)
    y0 = sc.centery - rows * rh // 2 + h
    f = g.font_at(max(12, min(20, rh - 4)))
    total = 0
    for r in range(rows):
      count = 10 if r < q["a"] else q["b"]
      y = y0 + r * rh
      total = add_all([total, count])
      fall_row = self.cascade_fall(r, now)
      for c in range(count):
        x = sc.x + 30 + c * gap + gap // 2
        colour = (90, 170, 255) if r < q["a"] else (255, 160, 60)
        fall_blit(s, small_domino(h, colour), (int(x), y), fall_row * min(1, (c + 1) / 10 + 0.2))
      lbl = f.render("10" if r < q["a"] else str(q["b"]), True, WHITE)
      lx = sc.x + 30 + 10 * gap + 8
      s.blit(lbl, lbl.get_rect(midleft=(lx, y - h // 2)))
      self._cascade.append((lx + 30, y - h, f"= {total}"))

  def scene_times(self, s, lay, now):
    """g dominoes with the same dots: a times table is adding them up."""
    q = self.q
    sc = lay["scene"]
    gnum = q["a"]
    a, b = q["halves"]
    per_row = gnum if gnum <= 5 else (gnum + 1) // 2
    rows = 1 if gnum <= 5 else 2
    h = int(min(sc.h / rows * 0.82, (sc.w - 20) / per_row * 1.6, 150))
    w = h // 2
    gap = max(10, w // 3)
    surf = face_surface(w, h, a, b)
    total = 0
    for i in range(gnum):
      row, col = divmod(i, per_row)
      n_in_row = min(per_row, gnum - row * per_row)
      x0 = sc.centerx - (n_in_row * (w + gap) - gap) // 2
      foot_y = sc.centery + h // 2 + (0 if rows == 1 else int((row - 0.5) * (h + 14)))
      x = x0 + col * (w + gap) + w // 2
      lean = 0.42 if i < gnum - 1 else 0.3          # each one leans on the next
      fall_blit(s, surf, (x, foot_y), self.cascade_fall(i, now) * lean)
      total = add_all([total, q["b"]])
      self._cascade.append((x, foot_y - h - 8, f"+{q['b']} = {total}"))

  def scene_share(self, s, lay, now):
    """A pile of laddoos; round by round, each friend gets one."""
    q = self.q
    sc = lay["scene"]
    n, gnum, each = q["a"], q["b"], q["c"]
    cell = min(110, (sc.w - 20) // gnum)
    lr = max(6, min(12, cell // 9))
    t = (now - self.done_at) if self.shown else -1
    rounds = 0 if t < 0 else min(each, int(t / 0.45) + 1)
    for k in range(gnum):
      fx = sc.centerx - (gnum * cell) // 2 + k * cell + cell // 2
      draw_friend(s, (fx, sc.y + 30), 22, TILE_COLOURS[k % len(TILE_COLOURS)])
      plate = pygame.Rect(0, 0, cell - 14, 22)
      plate.center = (fx, sc.bottom - 26)
      pygame.draw.ellipse(s, (235, 235, 245), plate)
      pygame.draw.ellipse(s, INK, plate, 2)
      for j in range(rounds):
        rr, cc = divmod(j, 3)
        draw_laddoo(s, (fx - lr * 2 + cc * lr * 2, plate.centery - 6 - rr * lr * 2), lr)
    left = n - rounds * gnum
    for j in range(left):                       # what is still in the pile
      ring, pos = divmod(j, 8)
      ang = pos * math.pi / 4 + ring * 0.4
      rad = 0 if j == 0 else lr * 2.1 * (ring + 1)
      draw_laddoo(s, (int(sc.centerx + rad * math.cos(ang)), int(sc.centery + rad * math.sin(ang))), lr)
    if self.shown:
      for r in range(each):
        self._cascade.append((sc.centerx, sc.centery - 30, f"{n - (r + 1) * gnum} left"))

  def scene_multiple(self, s, lay, now):
    """Two factor gates listing each table; the common number opens both."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    f = g.font_at(19)
    for k, base in enumerate((q["a"], q["b"])):
      y = sc.y + int(sc.h * (0.28 + 0.44 * k))
      gate = pygame.Rect(sc.x + 4, y - 24, 64, 48)
      pygame.draw.rect(s, (150, 100, 60), gate, border_radius=8)
      pygame.draw.rect(s, WHITE, gate, 2, border_radius=8)
      t = g.font_at(24).render(f"{base}×", True, WHITE)
      s.blit(t, t.get_rect(center=gate.center))
      x = gate.right + 8
      m = base
      while x < sc.right - 30 and m <= q["c"] + base * 2:
        hit = m == q["c"] and self.shown
        label = str(m) if (m != q["c"] or self.shown) else "?"
        tw = max(34, f.size(label)[0] + 12)
        tile = pygame.Rect(x, y - 18, tw, 36)
        pygame.draw.rect(s, GREEN if hit else (255, 250, 220), tile, border_radius=8)
        pygame.draw.rect(s, YELLOW if hit else INK, tile, 2, border_radius=8)
        tt = f.render(label, True, INK)
        s.blit(tt, tt.get_rect(center=tile.center))
        x += tw + 6
        m = add_all([m, base])

  def scene_fib(self, s, lay, now):
    """A row of numbered dominoes; when solved they fall along a spiral."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    seq = q["seq"]
    f = g.font_at(20)
    if not self.shown:
      w = min(60, (sc.w - 20) // 6 - 8)
      h = int(w * 1.5)
      x0 = sc.centerx - (6 * (w + 8) - 8) // 2
      for k, n in enumerate(seq):
        r = pygame.Rect(x0 + k * (w + 8), sc.centery - h // 2, w, h)
        last = k == 5
        pygame.draw.rect(s, (90, 100, 140) if last else TILE_COLOURS[k], r, border_radius=10)
        pygame.draw.rect(s, YELLOW if last else WHITE, r, 3, border_radius=10)
        t = f.render("?" if last else str(n), True, YELLOW if last else WHITE)
        s.blit(t, t.get_rect(center=r.center))
        if 2 <= k <= 4:
          plus = g.small_font.render(f"{seq[k - 2]}+{seq[k - 1]}", True, WHITE)
          s.blit(plus, plus.get_rect(midtop=(r.centerx, r.bottom + 6)))
      return
    # the spiral (golden ratio): dominoes grow and fall one after another
    cx, cy = sc.centerx - sc.w * 0.05, sc.centery + sc.h * 0.05
    r_max = min(sc.w / 2, sc.h / 2) - 45
    pts = []
    for k in range(6):                    # the spiral opens outwards, like a snail shell
      ang = 0.4 + k * 1.25
      rad = 34 + (r_max - 34) * (k / 5) ** 1.15
      pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    for k in range(1, 6):
      pygame.draw.line(s, (255, 230, 150), pts[k - 1], pts[k], 2)
    for k, n in enumerate(seq):
      h = 34 + k * 9
      surf = small_domino(h, TILE_COLOURS[k], str(n), g.font_at(max(14, h // 3)))
      fall_blit(s, surf, (int(pts[k][0]), int(pts[k][1] + h / 2)), self.cascade_fall(k, now) * 0.5)
      self._cascade.append((int(pts[k][0]), int(pts[k][1] - h / 2 - 8),
                            str(n) if k < 2 else f"{seq[k - 2]}+{seq[k - 1]}={n}"))

  def scene_prime(self, s, lay, now):
    """Dots in equal rows: a prime number can only make one long row."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    p = q["c"]
    comp = next((c for c in q["choices"] if not is_prime(c)), 12)
    r1, c1 = factor_pair(comp)
    f = g.small_font
    # left: a composite number as a rectangle of dots
    box = pygame.Rect(sc.x + 6, sc.y + 6, sc.w // 2 - 12, sc.h - 12)
    dot = max(4, min(10, min(box.w // (c1 + 1), (box.h - 40) // (r1 + 1)) // 2))
    for rr in range(r1):
      for cc in range(c1):
        x = box.centerx - (c1 - 1) * dot * 1.3 + cc * dot * 2.6
        y = box.y + 20 + rr * dot * 2.6 + dot
        pygame.draw.circle(s, (255, 200, 90), (int(x), int(y)), dot)
    t = f.render(f"{comp} = {r1} rows of {c1}: can split", True, WHITE)
    s.blit(t, t.get_rect(midbottom=(box.centerx, box.bottom)))
    # right: a shield with "?" until solved, then the prime as one row
    right = pygame.Rect(sc.centerx + 6, sc.y + 6, sc.w // 2 - 12, sc.h - 12)
    glow = 0.5 + 0.5 * math.sin(now * 4) if self.shown else 0.0
    draw_shield(s, (right.centerx, right.centery - 10), 34, glow=glow)
    big = g.font_at(30).render(str(p) if self.shown else "?", True, INK)
    s.blit(big, big.get_rect(center=(right.centerx, right.centery - 10)))
    msg = f"{p}: only 1 row of {p}" if self.shown else "Prime: no equal rows"
    t = f.render(msg, True, WHITE)
    s.blit(t, t.get_rect(midbottom=(right.centerx, right.bottom)))

  def scene_integer(self, s, lay, now):
    """A number line from -10 to 10; blue anti-dominoes pull to the left."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    big = g.font_at(30).render(q["show"], True, WHITE)
    s.blit(big, big.get_rect(center=(sc.centerx, sc.y + 18)))
    y = sc.y + int(sc.h * 0.72)
    left, right = sc.x + 14, sc.right - 14
    step = (right - left) / 20

    def xat(v):
      return int(left + (v + 10) * step)
    pygame.draw.line(s, WHITE, (left, y), (right, y), 3)
    f = g.small_font
    for v in range(-10, 11):
      tick = 8 if v % 5 else 12
      pygame.draw.line(s, WHITE, (xat(v), y - tick), (xat(v), y + tick), 2)
      if v % 2 == 0 or step > 22:
        t = f.render(num(v), True, (140, 190, 255) if v < 0 else WHITE)
        s.blit(t, t.get_rect(midtop=(xat(v), y + 14)))
    a, b, c = q["a"], q["b"], q["c"]
    # the tiles that make the move: anti-dominoes (negative) or normal ones
    anti = q["form"] in ("int_plus", "int_minus")
    th = int(min(46, sc.h * 0.28))
    tf = g.font_at(max(12, th // 3))
    for k in range(b):
      tile = small_domino(th, (90, 200, 120), "−1" if anti else "+1", tf, anti=anti)
      x = sc.centerx - (b - 1) * (tile.get_width() + 4) / 2 + k * (tile.get_width() + 4)
      s.blit(tile, tile.get_rect(midbottom=(int(x), y - 46)))
    hint = ("Blue anti-dominoes: each one takes you 1 to the left" if anti
            else "Taking away anti-dominoes moves you right")
    t = f.render(hint, True, (170, 210, 255))
    s.blit(t, t.get_rect(midbottom=(sc.centerx, y - 46 - th - 4)))
    # the walker: starts at a, hops to c once the answer is shown
    pos = a
    if self.shown:
      hops = int((now - self.done_at) / 0.35)
      d = 1 if c > a else -1
      pos = a + d * min(abs(c - a), hops)
    pygame.draw.circle(s, YELLOW, (xat(a), y), 7)
    pygame.draw.circle(s, (255, 120, 60), (xat(pos), y - 24), 13)
    pygame.draw.circle(s, WHITE, (xat(pos), y - 24), 13, 2)
    pygame.draw.polygon(s, (255, 120, 60), [(xat(pos) - 6, y - 13), (xat(pos) + 6, y - 13), (xat(pos), y - 3)])

  def scene_ratio(self, s, lay, now):
    """A ratio gate: the domino goes in small and comes out bigger (or smaller)."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    v, c = q["a"], q["c"]
    gate = pygame.Rect(0, 0, 90, int(sc.h * 0.8))
    gate.center = sc.center
    pygame.draw.rect(s, (160, 90, 220), gate, border_radius=40)
    inner = gate.inflate(-26, -26)
    pygame.draw.rect(s, (40, 20, 70), inner, border_radius=30)
    t = g.font_at(24).render(q["show"], True, YELLOW)
    s.blit(t, t.get_rect(center=(gate.centerx, gate.y - 14 if gate.y - 14 > sc.y else gate.centery)))
    h_in = int(sc.h * 0.42)
    k = 0.0
    if self.shown:
      k = min(1.0, (now - self.done_at) / 1.2)
    ha, hb = split_dots(v, 6) if v <= 12 else (None, None)
    small = pygame.Rect(0, 0, h_in // 2, h_in)
    small.center = (int(sc.x + sc.w * 0.18 + k * sc.w * 0.32), sc.centery)
    if k < 0.5:
      if ha is not None:
        draw_domino(s, small, ha, hb)
      lbl = g.font_at(24).render(str(v), True, WHITE)
      s.blit(lbl, lbl.get_rect(midtop=(small.centerx, small.bottom + 6)))
    out_h = int(min(sc.h * 0.95, h_in * (1.5 if q["up"] else 0.6)))
    if k >= 0.5:
      big = pygame.Rect(0, 0, out_h // 2, out_h)
      big.center = (int(sc.right - sc.w * 0.18), sc.centery)
      oa, ob = split_dots(c, 9) if c <= 18 else (None, None)
      if oa is not None:
        draw_domino(s, big, oa, ob, colour=(255, 245, 210))
      lbl = g.font_at(28).render(str(c), True, GREEN)
      s.blit(lbl, lbl.get_rect(midtop=(big.centerx, min(sc.bottom - 30, big.bottom + 6))))

  def scene_balance(self, s, lay, now):
    """A balance: x and some dots on one pan, the total on the other."""
    q = self.q
    g = self.g
    sc = lay["scene"]
    show = g.font_at(30).render(q["show"], True, WHITE)
    s.blit(show, show.get_rect(center=(sc.centerx, sc.y + 18)))
    base_y = sc.bottom - 8
    top_y = sc.y + int(sc.h * 0.42)
    pygame.draw.polygon(s, (180, 140, 90), [(sc.centerx - 40, base_y), (sc.centerx + 40, base_y),
                                            (sc.centerx, top_y)])
    tilt = 0.0 if self.shown else 0.08 * math.sin(now * 2.5)   # wobbles until solved
    half = min(170, sc.w // 2 - 70)
    lx, ly = sc.centerx - half, top_y + half * tilt
    rx, ry = sc.centerx + half, top_y - half * tilt
    pygame.draw.line(s, (220, 190, 140), (lx, ly), (rx, ry), 6)
    pygame.draw.circle(s, WHITE, (sc.centerx, top_y), 7)
    f = g.font_at(26)
    for (px, py), label, colour in (((lx, ly), q["show"].split(" = ")[0], (90, 170, 255)),
                                    ((rx, ry), str(q["total"]), (255, 160, 60))):
      pygame.draw.line(s, WHITE, (px, py), (px, py + 40), 2)
      pan = pygame.Rect(0, 0, 120, 26)
      pan.center = (px, py + 52)
      pygame.draw.ellipse(s, colour, pan)
      pygame.draw.ellipse(s, WHITE, pan, 2)
      if self.shown and "x" in label:
        label = label.replace("x", str(q["c"]))
      t = f.render(label, True, WHITE)
      s.blit(t, t.get_rect(midbottom=(px, pan.y - 2)))
