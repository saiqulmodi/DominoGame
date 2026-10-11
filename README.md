# Domino Wonder Dash

A learning game for children (NCERT Class 1-5 level). Pick something, trace its dotted
outline with a finger or the mouse, watch the dominoes topple, and see the real picture
while the name is said, spelled and shown.

**Play in the browser:** https://saiqulmodi.github.io/DominoGame/
(also on [Stratos Games](https://stratos-technologies-fzco.github.io/stratos-games-site/play/saiqulmodi-domino-wonder-dash/))

## What children learn

422 items in 10 subjects, all from the Picture Data Hub (`domino_data.py`):

- **English** - A-Z ("A for Apple") and a-z
- **Hindi** - वर्णमाला: 13 स्वर and 36 व्यंजन ("क से कबूतर")
- **Maths** - 0-10, shapes, signs (+ − × ÷ = ₹), coin, ruler, balance
- **India** - the whole India map (trace it, then every state appears in colour
  with its name), all 28 states and 8 union territories on India's official map,
  each with its capital (star) and famous places (for example Delhi: National War
  Memorial and India Gate, Red Fort, Qutub Minar, Lotus Temple, Akshardham), and
  11 monuments (War Memorial, Qutub Minar, Red Fort, Lotus Temple, Golden Temple,
  Hawa Mahal, Mysuru Palace, Meenakshi Temple, Sanchi Stupa, Gol Gumbaz, Konark wheel)
- **Nature** - animals, birds, sea life, reptiles, insects, plants
- **Food** - fruits, vegetables, everyday food
- **Me & Home** - body parts, home, buildings, community helpers
- **Travel** - vehicles, trains, planes, ships, bridges
- **World** - sky and weather, countries (India's official map), cities (famous
  landmarks), rivers
- **Fun** - cartoon friends (superhero, robot, unicorn, dragon, fairy, mermaid,
  genie, wizard, prince, princess, ninja, alien, friendly ghost, teddy bear,
  snowman, Santa, panda, elf), music, sports, and free drawing

## More ways to learn (Games button)

- **Find it!** - the voice says a name, the child taps the right picture of four
- **Spell it** - put jumbled letter tiles in the right order
- **Draw my own** - free drawing from the child's own imagination: pick crayon
  colours, draw as many lines as they like (Undo fixes a mistake), tap Done and
  their picture turns into dominoes that topple
- **Story of the day** - 14 short adventures (farm, jungle, sea, school, kitchen,
  a trip across India, rainy day, space ...) that link 5 pictures with a sentence each
- **Players** - one profile per child (up to 6), with an on-screen keyboard for names
- **Language** - every picture's name in English + Hindi or English + Bangla,
  shown and spoken (where the device has that voice)
- **For parents** - progress per subject, quiz accuracy, words spelled, stories, days played
- **Full screen** - the game fills the whole screen: in the browser the first tap
  goes full screen (phones stay upright), on a computer it opens full screen
  (F11 or this button switches, Esc leaves full screen). The game takes the shape
  of any screen (phone, tablet, computer), so nothing is cut off and there are no
  empty bars; turning the screen keeps what was already traced

## Playing

The picture to trace fills the screen. A slim top row has the **☰ menu** button
(left), the picture's name with the speaker and real-video buttons, and **Next**
(right). The menu shows every subject, category and picture plus Reset, Games,
Stickers and Theme; picking a picture (or Play) goes straight back to the game.
- **Watch the real one** - pictures with a red ▶ badge have a short real-life
  video (190 pictures: animals, birds, sea life, plants, food, vehicles, bridges,
  sky, states, cities, rivers, monuments, instruments, sports). Tap the red play
  button next to the speaker, or the big "Watch the real ..." button after
  finishing; "Back to play" returns to the game to trace it again. Every video is a free Wikimedia
  Commons clip checked by a person (`tools/find_videos.py`): no adverts and no
  "watch next" list
- **Famous places of India** - 31 states and union territories have a playlist of
  their famous places (99 clips, `tools/place_videos.py`), for example Delhi: India
  Gate, Red Fort, Humayun's Tomb, Rashtrapati Bhavan; Kerala: backwaters,
  houseboats, Munnar tea hills, Kathakali, snake boat race; Ladakh: Pangong Lake,
  Hemis Monastery, a snow leopard. One button per place; each place's name is said
  as it starts and the next place follows by itself

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
