# Domino Wonder Dash

A learning game for children (NCERT Class 1-5 level). Pick something, trace its dotted
outline with a finger or the mouse, watch the dominoes topple, and see the real picture
while the name is said, spelled and shown.

**Play in the browser:** https://saiqulmodi.github.io/DominoWonderDash/

## What children learn

366 items in 8 subjects, all from the Picture Data Hub (`domino_data.py`):

- **English** - A-Z ("A for Apple") and a-z
- **Hindi** - वर्णमाला: 13 स्वर and 36 व्यंजन ("क से कबूतर")
- **Maths** - 0-10, shapes, signs (+ − × ÷ = ₹), coin, ruler, balance
- **Nature** - animals, birds, sea life, reptiles, insects, plants
- **Food** - fruits, vegetables, everyday food
- **Me & Home** - body parts, home, buildings, community helpers
- **Travel** - vehicles, trains, planes, ships, bridges
- **World** - sky and weather, countries (India's official map), Indian states,
  cities (famous landmarks), rivers
- **Fun** - music, sports, and free drawing

## More ways to learn (Games button)

- **Find it!** - the voice says a name, the child taps the right picture of four
- **Spell it** - put jumbled letter tiles in the right order
- **Story of the day** - 14 short adventures (farm, jungle, sea, school, kitchen,
  a trip across India, rainy day, space ...) that link 5 pictures with a sentence each
- **Players** - one profile per child (up to 6), with an on-screen keyboard for names
- **Language** - every picture's name in English + Hindi or English + Bangla,
  shown and spoken (where the device has that voice)
- **For parents** - progress per subject, quiz accuracy, words spelled, stories, days played

## Fun that keeps them playing

- Real sounds after each picture: moo, roar, quack, choo-choo, sirens, drums, rain ...
- Sparks fly from every dot, confetti when the dominoes finish
- Trace quickly for a streak: the pops climb a musical scale and the trail glows
- A gold star on every item already traced, and stickers for milestones and for
  finishing a whole category (the star button opens the sticker shelf)
- 5 colour themes (palette button)

## Run it

```
pip install pygame-ce
python main.py
```

Phone, browser and Android builds: see [BUILD_MOBILE.md](BUILD_MOBILE.md).
Rebuild the browser version: `python tools/build_web.py` (writes `docs/`).
Add or change items: edit `domino_data.py` (Hindi/Bengali names in `translations.py`),
then `python tools/build_hub.py`. Sounds: `python tools/build_sounds.py`.

## Credits

Pictures from [OpenMoji](https://openmoji.org) (CC BY-SA 4.0), maps from
[Natural Earth](https://www.naturalearthdata.com) (public domain). See [CREDITS.md](CREDITS.md).

Made by Md. Saiqul Haque Modi.
