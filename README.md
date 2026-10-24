# Domino Wonder Dash

A free learning game for children from **Nursery to Class 7**. Children trace a dotted
outline with a finger or the mouse, watch magic dominoes topple, and see the real picture
while its name is said, spelled and sung, in English with Hindi or Bangla.

- **Play in the browser** (phone or computer): https://saiqulmodi.github.io/DominoGame/
  (Android: *Install app*; iPhone: Share > *Add to Home Screen*; works offline once loaded)
- **Download page (Android / iPhone & iPad / computer)**: https://saiqulmodi.github.io/DominoGame/download.html
- **Android app**: [DominoWonderDash-1.1-test.apk](https://github.com/saiqulmodi/DominoGame/releases/download/v1.1-test/DominoWonderDash-1.1-test.apk)
  (open in Chrome, allow "install unknown apps", Install)
- **On Stratos Games**: https://stratos-technologies-fzco.github.io/stratos-games-site/play/saiqulmodi-domino-wonder-dash/
- **Share with friends for feedback** (WhatsApp button): https://saiqulmodi.github.io/DominoGame/share.html

## What children learn

838 pictures in 15 subjects, all from the Picture Data Hub (`domino_data.py`,
`catalog_more.py`, `bangla.py`, `rhymes_hub.py`):

- **English** - A-Z and a-z. Every letter shows its word as a picture (A - apple,
  C - cat, X - xylophone) and has its own sing-along ("C for Cat, C for Cat ...")
- **Rhymes** - 65 sing-along rhymes: 45 English nursery rhymes (Twinkle Twinkle, Baa
  Baa Black Sheep, Johny Johny, Old MacDonald, A Was an Apple Pie ...) and 20 Hindi and
  Bengali ones (Machli Jal Ki Rani, Akkad Bakkad, Hattimatim Tim, Tagore's Amader Chhoto
  Nodi ...). Trace the rhyme's picture, then the words light up one by one as they are sung
- **Hindi** - वर्णमाला: 13 स्वर and 36 व्यंजन ("क से कबूतर"), spoken and sung in Hindi,
  each with its word's picture
- **Bangla** - বর্ণমালা: 11 স্বরবর্ণ and 39 ব্যঞ্জনবর্ণ ("ক-এ কলা"), traced, spoken and
  sung in Bengali, each with its word's picture
- **Maths** - 0-10, shapes, signs, angles and solids, abacus, set square, calendar
- **India** - the India map (every state appears in colour), all 28 states and 8 union
  territories on India's official map with capitals, famous places and real videos,
  11 monuments, the Tiranga
- **Nature** - animals, birds, sea life, reptiles, insects, plants
- **Food** - fruits, vegetables, everyday and Indian food
- **Me & Home** - body, home, buildings, helpers, **Feelings** (Nursery) and
  **Good Habits** (Class 1-2)
- **Travel** - vehicles, trains, planes, ships, bridges
- **World** - sky and weather, countries, cities, rivers
- **Fun** - cartoon friends, music, sports, free drawing
- **Science** (Class 6-7) - lab tools, inside the body, materials, space, **Energy**
- **Social** (Class 6-7) - long ago, earth and maps, our country
- **Safety** - road signs to trace and the **Cross the Road** game

## The domino show

Every cascade is a new little show (`magic.py`): its own melody on bell notes (Indian
ragas Bhupali, Yaman, Kafi, Bilawal, or major, pentatonic, whole-tone, rising, falling or
in waves), a slow start, twists where the line almost stops ("...?") and then bursts
forward, a glowing wave of light with butterflies, fireflies, stars, bubbles or a rainbow,
a butterfly-effect finale, and a **What's next?** mystery card that leads to the next
picture.

## More ways to learn (Games)

- **Find it!** - hear a name, tap the right picture
- **Spell it** - put the letter tiles in order
- **Cross the Road** - wait for the green man, look right, left, right, and cross the
  zebra crossing; every safe crossing gives a road safety tip
- **Maths Play** (the whole NCERT Class 1-7 maths syllabus; `maths_bank.py` questions,
  `mathsgame.py` screen) - pick a class, then a chapter (79 chapters, plus mixed practice
  per class). 60 kinds of question, each with its own picture: counting dots, number names,
  place value (Indian commas), rounding, Roman numerals, column sums with carrying and
  borrowing, times tables as groups of dominoes, long division with remainders, factors,
  HCF, primes and factor trees, fractions (pies, bars, equivalent, compare, add, of a
  number), decimals, percent, clocks and durations, calendars, coins, notes and bills,
  rulers and unit conversion, 2D and 3D shapes, angles with a protractor, lines,
  triangles, circles, symmetry, perimeter, area and volume, tally marks, picture graphs,
  bar graphs, mean, median and mode, number and shape patterns (Fibonacci spiral),
  integers with blue anti-dominoes on a number line, order of operations, exponents,
  algebra (evaluate, like terms, balance puzzles), ratio gates, unitary method, profit and
  loss, simple interest. Every answer is shown as adding: 4 × 3 = 4 + 4 + 4, 9 − 3 =
  9 + (−3), 12 ÷ 3 = 12 − 3 − 3 − 3 − 3; dominoes fall in a chain with running totals.
  Spoken in English, Hindi or Bangla. Three difficulty steps per chapter (five right in a
  row = harder, three misses = easier) and a gold star per chapter after ten right answers.
  Also in the Number House in Wonder Town.
- **Draw my own** - draw anything; the drawing becomes dominoes
- **Story of the day** and 14 stories, **How to play** picture guides, up to 6 players,
  Hindi or Bangla names, a **parents' report** and **Credits**

## Easy for young children

- Moving picture guides show how to play, and every instruction is spoken
- A helping hand appears when a child stops tracing
- **Wonder Town**: a 3D town where every building is a subject, with names painted on the
  walls and yellow arrows to each door
- A **rainbow cap** gains a colour for every subject discovered; stickers for milestones

## Run it

```
pip install pygame-ce
python main.py
```

Browser and phone builds, the Android app and testing on a phone: see
[BUILD_MOBILE.md](BUILD_MOBILE.md). Rebuild the browser version: `python tools/build_web.py`.
Add pictures to a category: add rows to `catalog_more.py`, then
`python tools/add_items.py "<Category>"` (only new pictures are built).

## Credits

Pictures from [OpenMoji](https://openmoji.org) (CC BY-SA 4.0) and drawn for the game,
maps from [Natural Earth](https://www.naturalearthdata.com), real-life videos from
Wikimedia Commons, Pexels and Pixabay, rhymes traditional or by public-domain poets.
See [CREDITS.md](CREDITS.md).

Made by Md. Saiqul Haque Modi.
