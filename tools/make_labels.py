"""Hindi and Bangla labels for the Magic Box and the Subject Magic Console (world.py).

The game's font has no Devanagari or Bengali letters, so these few labels are drawn
here with Noto Sans (the same fonts build_hub.py uses) into labels/<lang>_<key>.png:
white letters with a dark rim, readable on any crystal colour.

Run:  python tools/make_labels.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hub as bh  # noqa: E402

import pygame  # noqa: E402

OUT = os.path.join(bh.ROOT, "labels")
HI_DIGITS = "०१२३४५६७८९"
BN_DIGITS = "০১২৩৪৫৬৭৮৯"
LABELS = {
    "maths": ("गणित", "গণিত"),
    "evs": ("पर्यावरण अध्ययन", "পরিবেশ পরিচিতি"),
    "science": ("विज्ञान", "বিজ্ঞান"),
    "social": ("सामाजिक विज्ञान", "সমাজবিজ্ঞান"),
    "english": ("अंग्रेज़ी", "ইংরেজি"),
    "hindi": ("हिंदी वर्णमाला", "হিন্দি বর্ণমালা"),
    "bangla": ("बांग्ला वर्णमाला", "বাংলা বর্ণমালা"),
    "india": ("भारत का नक्शा", "ভারতের মানচিত্র"),
}
for n in range(1, 8):
  LABELS[f"class{n}"] = (f"कक्षा {HI_DIGITS[n]}", f"শ্রেণি {BN_DIGITS[n]}")


def render(font, text):
  ink = font.render(text, True, (255, 255, 255))
  rim = font.render(text, True, (30, 30, 60))
  pad = 4
  out = pygame.Surface((ink.get_width() + 2 * pad, ink.get_height() + 2 * pad), pygame.SRCALPHA)
  for dx in range(-3, 4):
    for dy in range(-3, 4):
      if dx * dx + dy * dy <= 10:
        out.blit(rim, (pad + dx, pad + dy))
  out.blit(ink, (pad, pad))
  box = out.get_bounding_rect()
  return out.subsurface(box.inflate(4, 4).clip(out.get_rect())).copy()


def main():
  pygame.init()
  os.makedirs(OUT, exist_ok=True)
  for key, (hi, bn) in LABELS.items():
    for lang, text, font in (("hi", hi, bh.deva_font(56)), ("bn", bn, bh.beng_font(56))):
      path = os.path.join(OUT, f"{lang}_{key}.png")
      pygame.image.save(render(font, text), path)
  print(len(LABELS) * 2, "labels in", OUT)


if __name__ == "__main__":
  main()
