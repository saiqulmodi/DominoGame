"""Picture Data Hub for Domino Wonder Dash.

CATALOG below is the single list of every category and item in the game.
Each item says where its outline comes from:

  ("emoji", "1F408")         - OpenMoji picture; its real silhouette is traced
  ("country", "India")       - real map border (Natural Earth, India's view)
  ("state", "Karnataka")     - real Indian state border (Natural Earth)
  ("river", ["Ganges"])      - real river course, drawn over its countries
  ("landmark", [(x, y)...])  - right half of a symmetric landmark, 0..100,
                               or (right_half, [hole loops]) for gaps
  ("shape", "star")          - exact geometric shape
  ("glyph", "A")             - a letter, number or sign, traced from a font
  ("hindi", ("अ से अनार", "a")) - Hindi letter with its word (spoken in Hindi)
  ("custom", None)           - the child draws their own

To add or change items, edit CATALOG and run:  python tools/build_hub.py
That writes hub_data.json (outlines) and pics/ (pictures), which the game
reads through the functions at the bottom of this file.
"""

import json
import math
import os

from translations import TRANSLATIONS

HERE = os.path.dirname(os.path.abspath(__file__))
HUB_JSON = os.path.join(HERE, "hub_data.json")

# --------------------------------------------------------------------------
# Landmark outlines (right half, x 50..100, y 0 top .. 100 ground). The left
# half is mirrored automatically.
# --------------------------------------------------------------------------
INDIA_GATE = [
    (50, 4), (55, 6), (58, 10), (60, 15), (80, 15), (80, 24), (88, 24),
    (88, 34), (84, 34), (84, 100), (62, 100), (62, 60), (61.6, 56.9),
    (60.4, 54), (58.5, 51.5), (56, 49.6), (53.1, 48.4), (50, 48),
]
TAJ_MAHAL = [
    (50, 4), (52, 12), (57, 17), (63, 24), (65, 32), (63, 39), (60, 44),
    (64, 44), (64, 54), (67, 54), (67, 48), (70, 44), (73, 48), (73, 54),
    (78, 54), (78, 84), (88, 84), (88, 40), (87, 37), (91, 30), (95, 37),
    (94, 40), (94, 94), (100, 94), (100, 100), (50, 100),
]
GATEWAY_OF_INDIA = [
    (50, 16), (54, 17), (56, 22), (68, 22), (68, 12), (71, 8), (74, 6),
    (77, 8), (80, 12), (80, 22), (84, 22), (84, 100), (62, 100), (62, 62),
    (61, 55), (58, 50), (54, 47), (50, 46),
]
CHARMINAR = [
    (50, 30), (70, 30), (70, 10), (72, 6), (74, 0), (76, 6), (78, 10),
    (78, 28), (81, 28), (81, 32), (78, 32), (78, 55), (81, 55), (81, 59),
    (78, 59), (78, 100), (64, 100), (64, 70), (63, 63), (60, 58), (55, 56),
    (50, 55),
]
VIDHANA_SOUDHA = [
    (50, 8), (53, 10), (57, 14), (59, 20), (60, 27), (62, 27), (62, 40),
    (68, 40), (68, 48), (80, 48), (80, 43), (84, 38), (88, 43), (88, 48),
    (98, 48), (98, 100), (50, 100),
]
HOWRAH_BRIDGE = [
    (50, 42), (66, 14), (68, 10), (73, 10), (75, 14), (90, 50), (100, 60),
    (100, 70), (76, 70), (76, 92), (66, 92), (66, 70), (50, 70),
]
EIFFEL_TOWER = [
    (50, 0), (51, 8), (52, 20), (54, 34), (58, 35), (58, 39), (56, 39),
    (60, 57), (66, 58), (66, 62), (63, 62), (70, 80), (78, 100), (64, 100),
    (61, 93), (56, 88), (50, 86),
]
BIG_BEN = [
    (50, 0), (52, 8), (55, 15), (58, 20), (58, 26), (62, 26), (62, 30),
    (60, 30), (60, 52), (62, 52), (62, 56), (59, 56), (59, 100), (50, 100),
]
BURJ_KHALIFA = [
    (50, 0), (50.8, 12), (52, 28), (54, 30), (54, 48), (57, 50), (57, 66),
    (60, 68), (60, 82), (63, 84), (63, 100), (50, 100),
]

# Bridges: (right half, optional hole loops in full 0..100 coordinates)
ARCH_BRIDGE = [
    (50, 40), (100, 40), (100, 100), (92, 100), (90.6, 89.1), (86.4, 79),
    (79.7, 70.3), (71, 63.6), (60.9, 59.4), (50, 58),
]
SUSPENSION_BRIDGE = [
    (50, 58), (60, 40), (68, 10), (70, 4), (76, 4), (78, 10), (88, 40),
    (100, 62), (100, 70), (78, 70), (78, 100), (68, 100), (68, 70), (50, 70),
]
BEAM_BRIDGE = [
    (50, 40), (100, 40), (100, 50), (90, 50), (90, 100), (84, 100), (84, 50),
    (64, 50), (64, 100), (58, 100), (58, 50), (50, 50),
]
STONE_BRIDGE = (
    [(50, 40), (100, 40), (100, 100), (50, 100)],
    [
        [(50 + 18 * math.cos(a / 10 * math.pi), 100 - 18 * math.sin(a / 10 * math.pi))
         for a in range(11)],
        [(82 + 12 * math.cos(a / 10 * math.pi), 100 - 12 * math.sin(a / 10 * math.pi))
         for a in range(11)],
        [(18 + 12 * math.cos(a / 10 * math.pi), 100 - 12 * math.sin(a / 10 * math.pi))
         for a in range(11)],
    ],
)
TOWER_BRIDGE = (
    [(50, 22), (62, 22), (62, 14), (66, 14), (70, 4), (74, 14), (78, 14),
     (78, 62), (100, 66), (100, 72), (78, 72), (78, 100), (62, 100), (62, 72),
     (50, 72)],
    [[(38, 28), (62, 28), (62, 62), (38, 62)]],
)

# Letter words (A for Apple ...) and number words
LETTER_WORDS = [
    "Apple", "Ball", "Cat", "Dog", "Elephant", "Fish", "Grapes", "House",
    "Ice cream", "Jug", "Kite", "Lion", "Mango", "Nest", "Owl", "Parrot",
    "Queen", "Rabbit", "Sun", "Tiger", "Umbrella", "Van", "Watch",
    "Xylophone", "Yak", "Zebra",
]
NUMBER_WORDS = [
    "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten",
]

# Hindi varnamala: (letter, word, letter in English letters, word in English
# letters, meaning). Letters with no common word just say themselves.
HINDI_SWAR = [
    ("अ", "अनार", "a", "anaar", "pomegranate"),
    ("आ", "आम", "aa", "aam", "mango"),
    ("इ", "इमली", "i", "imlee", "tamarind"),
    ("ई", "ईख", "ee", "eekh", "sugarcane"),
    ("उ", "उल्लू", "u", "ulloo", "owl"),
    ("ऊ", "ऊन", "oo", "oon", "wool"),
    ("ऋ", "ऋषि", "ri", "rishi", "sage"),
    ("ए", "एड़ी", "e", "edee", "heel"),
    ("ऐ", "ऐनक", "ai", "ainak", "spectacles"),
    ("ओ", "ओखली", "o", "okhlee", "mortar"),
    ("औ", "औरत", "au", "aurat", "woman"),
    ("अं", "अंगूर", "an", "angoor", "grapes"),
    ("अः", "प्रातः", "ah", "praatah", "morning"),
]
HINDI_VYANJAN = [
    ("क", "कबूतर", "ka", "kabootar", "pigeon"),
    ("ख", "खरगोश", "kha", "khargosh", "rabbit"),
    ("ग", "गमला", "ga", "gamla", "flower pot"),
    ("घ", "घड़ी", "gha", "ghadee", "clock"),
    ("ङ", "", "nga", "", ""),
    ("च", "चम्मच", "cha", "chammach", "spoon"),
    ("छ", "छतरी", "chha", "chhatree", "umbrella"),
    ("ज", "जहाज़", "ja", "jahaaz", "ship"),
    ("झ", "झंडा", "jha", "jhanda", "flag"),
    ("ञ", "", "nya", "", ""),
    ("ट", "टमाटर", "ta", "tamaatar", "tomato"),
    ("ठ", "ठठेरा", "tha", "thathera", "metal worker"),
    ("ड", "डमरू", "da", "damroo", "small drum"),
    ("ढ", "ढक्कन", "dha", "dhakkan", "lid"),
    ("ण", "बाण", "na", "baan", "arrow"),
    ("त", "तरबूज़", "ta", "tarbooz", "watermelon"),
    ("थ", "थरमस", "tha", "tharmas", "flask"),
    ("द", "दवात", "da", "davaat", "ink pot"),
    ("ध", "धनुष", "dha", "dhanush", "bow"),
    ("न", "नल", "na", "nal", "water tap"),
    ("प", "पतंग", "pa", "patang", "kite"),
    ("फ", "फल", "pha", "phal", "fruit"),
    ("ब", "बतख़", "ba", "batakh", "duck"),
    ("भ", "भालू", "bha", "bhaaloo", "bear"),
    ("म", "मछली", "ma", "machhlee", "fish"),
    ("य", "यज्ञ", "ya", "yagya", "sacred fire"),
    ("र", "रथ", "ra", "rath", "chariot"),
    ("ल", "लट्टू", "la", "lattoo", "spinning top"),
    ("व", "वन", "va", "van", "forest"),
    ("श", "शलगम", "sha", "shalgam", "turnip"),
    ("ष", "षट्कोण", "sha", "shatkon", "hexagon"),
    ("स", "सपेरा", "sa", "sapera", "snake charmer"),
    ("ह", "हाथी", "ha", "haathee", "elephant"),
    ("क्ष", "क्षत्रिय", "ksha", "kshatriya", "warrior"),
    ("त्र", "त्रिशूल", "tra", "trishool", "trident"),
    ("ज्ञ", "ज्ञानी", "gya", "gyaanee", "wise person"),
]


def _hindi_items(rows):
  items = []
  for letter, word, roman, word_roman, meaning in rows:
    if word:
      phrase = f"{letter} से {word}"
      desc = f"{roman} se {word_roman} - {meaning}"
    else:
      phrase, desc = letter, f"{roman} - a nasal sound"
    items.append((letter, desc, ("hindi", (phrase, roman))))
  return items


# --------------------------------------------------------------------------
# The catalog: category -> list of (name, description, source)
# --------------------------------------------------------------------------
CATALOG = {
    "ABC": [
        (chr(65 + i), f"{chr(65 + i)} for {w}", ("glyph", chr(65 + i)))
        for i, w in enumerate(LETTER_WORDS)
    ],
    "abc": [
        (chr(97 + i), f"small {chr(97 + i)} for {w.lower()}", ("glyph", chr(97 + i)))
        for i, w in enumerate(LETTER_WORDS)
    ],
    "Swar": _hindi_items(HINDI_SWAR),
    "Vyanjan": _hindi_items(HINDI_VYANJAN),
    "123": [
        (str(n), f"{w} - {n}", ("glyph", str(n)))
        for n, w in enumerate(NUMBER_WORDS)
    ],
    "Signs": [
        ("+", "Plus - add", ("glyph", "+")),
        ("−", "Minus - take away", ("glyph", "−")),
        ("×", "Times - multiply", ("glyph", "×")),
        ("÷", "Divide - share equally", ("glyph", "÷")),
        ("=", "Equals - the same as", ("glyph", "=")),
        ("₹", "Rupee - our money", ("glyph", "₹")),
        ("Coin", "Coins are money we can spend.", ("emoji", "1FA99")),
        ("Ruler", "A ruler measures length.", ("emoji", "1F4CF")),
        ("Scale", "A balance weighs things.", ("emoji", "2696")),
    ],
    "Shapes": [
        ("Circle", "A circle is round with no corners.", ("shape", "circle")),
        ("Square", "A square has 4 equal sides.", ("shape", "square")),
        ("Triangle", "A triangle has 3 sides.", ("shape", "triangle")),
        ("Rectangle", "A rectangle has 2 long and 2 short sides.", ("shape", "rectangle")),
        ("Star", "A star has 5 points.", ("shape", "star")),
        ("Heart", "A heart means love.", ("shape", "heart")),
        ("Diamond", "A diamond stands on its corner.", ("shape", "diamond")),
        ("Pentagon", "A pentagon has 5 sides.", ("shape", "pentagon")),
        ("Hexagon", "A hexagon has 6 sides, like honeycomb.", ("shape", "hexagon")),
        ("Oval", "An oval is shaped like an egg.", ("shape", "oval")),
        ("Moon", "A crescent moon shines at night.", ("shape", "moon")),
        ("Arrow", "An arrow shows the way.", ("shape", "arrow")),
    ],
    "Animals": [
        ("Cat", "A cat says meow and loves to nap.", ("emoji", "1F408")),
        ("Dog", "A dog wags its tail and says woof!", ("emoji", "1F415")),
        ("Elephant", "The elephant has a long trunk and big ears.", ("emoji", "1F418")),
        ("Cow", "A cow gives us milk. Moo!", ("emoji", "1F404")),
        ("Horse", "A horse can run very fast.", ("emoji", "1F40E")),
        ("Tiger", "The tiger is India's national animal.", ("emoji", "1F405")),
        ("Monkey", "A monkey loves to climb trees.", ("emoji", "1F412")),
        ("Rabbit", "A rabbit has long ears and hops.", ("emoji", "1F407")),
        ("Giraffe", "The giraffe has the longest neck.", ("emoji", "1F992")),
        ("Camel", "A camel lives in the desert.", ("emoji", "1F42A")),
        ("Goat", "A goat says maa and eats grass.", ("emoji", "1F410")),
        ("Pig", "A pig has a curly tail.", ("emoji", "1F416")),
    ],
    "Birds": [
        ("Eagle", "The eagle soars high in the sky.", ("emoji", "1F985")),
        ("Swan", "A swan glides on the lake.", ("emoji", "1F9A2")),
        ("Peacock", "The peacock is India's national bird.", ("emoji", "1F99A")),
        ("Parrot", "A parrot can copy words.", ("emoji", "1F99C")),
        ("Duck", "A duck swims and says quack.", ("emoji", "1F986")),
        ("Owl", "The owl stays awake at night.", ("emoji", "1F989")),
        ("Rooster", "The rooster crows cock-a-doodle-doo in the morning.", ("emoji", "1F413")),
        ("Penguin", "A penguin lives in the cold ice.", ("emoji", "1F427")),
        ("Flamingo", "A pink flamingo stands on one leg.", ("emoji", "1F9A9")),
        ("Dove", "The white dove means peace.", ("emoji", "1F54A")),
    ],
    "Sea": [
        ("Fish", "A fish swims with its fins.", ("emoji", "1F41F")),
        ("Clownfish", "A bright fish of the coral reef.", ("emoji", "1F420")),
        ("Pufferfish", "It puffs up like a ball!", ("emoji", "1F421")),
        ("Shark", "The shark has many sharp teeth.", ("emoji", "1F988")),
        ("Dolphin", "A dolphin is clever and playful.", ("emoji", "1F42C")),
        ("Whale", "The whale is the biggest animal.", ("emoji", "1F40B")),
        ("Octopus", "An octopus has eight arms.", ("emoji", "1F419")),
        ("Crab", "A crab walks sideways.", ("emoji", "1F980")),
    ],
    "Reptiles": [
        ("Crocodile", "A crocodile has strong jaws.", ("emoji", "1F40A")),
        ("Turtle", "A turtle carries its shell home.", ("emoji", "1F422")),
        ("Lizard", "A lizard climbs up the wall.", ("emoji", "1F98E")),
        ("Snake", "A snake has no legs. Hiss!", ("emoji", "1F40D")),
        ("Dinosaur", "T-rex lived long, long ago.", ("emoji", "1F996")),
        ("Frog", "A frog jumps and says ribbit.", ("emoji", "1F438")),
    ],
    "Insects": [
        ("Butterfly", "A butterfly has colourful wings.", ("emoji", "1F98B")),
        ("Bee", "A bee makes sweet honey.", ("emoji", "1F41D")),
        ("Ant", "Ants work hard together.", ("emoji", "1F41C")),
        ("Ladybug", "A red ladybug with black spots.", ("emoji", "1F41E")),
        ("Snail", "A snail moves very slowly.", ("emoji", "1F40C")),
        ("Spider", "A spider spins a web.", ("emoji", "1F577")),
    ],
    "Plants": [
        ("Tree", "A tree gives us shade and fruit.", ("emoji", "1F333")),
        ("Palm Tree", "Coconuts grow on a palm tree.", ("emoji", "1F334")),
        ("Cactus", "A cactus lives in the desert.", ("emoji", "1F335")),
        ("Sunflower", "A sunflower turns to the sun.", ("emoji", "1F33B")),
        ("Rose", "A rose smells lovely.", ("emoji", "1F339")),
        ("Tulip", "A tulip is a spring flower.", ("emoji", "1F337")),
        ("Lotus", "The lotus is India's national flower.", ("emoji", "1FAB7")),
        ("Mushroom", "A mushroom grows in damp places.", ("emoji", "1F344")),
        ("Leaf", "A maple leaf falls in autumn.", ("emoji", "1F341")),
        ("Pine Tree", "A pine tree stays green all year.", ("emoji", "1F332")),
        ("Seedling", "A tiny new plant growing from a seed.", ("emoji", "1F331")),
        ("Hibiscus", "The hibiscus is a big red flower.", ("emoji", "1F33A")),
        ("Daisy", "A daisy has white petals.", ("emoji", "1F33C")),
        ("Clover", "A lucky four-leaf clover.", ("emoji", "1F340")),
        ("Potted Plant", "A plant growing in a pot.", ("emoji", "1FAB4")),
        ("Corn", "Corn (maize) grows tall in the fields.", ("emoji", "1F33D")),
        ("Herb", "Tulsi and mint are herbs.", ("emoji", "1F33F")),
        ("Cherry Blossom", "Pink flowers on a cherry tree.", ("emoji", "1F338")),
    ],
    "Fruits": [
        ("Apple", "An apple a day is good for you.", ("emoji", "1F34E")),
        ("Banana", "A banana is long and yellow.", ("emoji", "1F34C")),
        ("Mango", "The mango is the king of fruits.", ("emoji", "1F96D")),
        ("Grapes", "Grapes grow in bunches.", ("emoji", "1F347")),
        ("Watermelon", "Watermelon is juicy and red inside.", ("emoji", "1F349")),
        ("Strawberry", "A strawberry has tiny seeds outside.", ("emoji", "1F353")),
        ("Pineapple", "A pineapple has a spiky crown.", ("emoji", "1F34D")),
        ("Carrot", "A carrot grows under the ground.", ("emoji", "1F955")),
    ],
    "Vegetables": [
        ("Potato", "A potato grows under the ground.", ("emoji", "1F954")),
        ("Onion", "Cutting an onion makes us cry!", ("emoji", "1F9C5")),
        ("Tomato", "A tomato is red and juicy.", ("emoji", "1F345")),
        ("Brinjal", "Brinjal is also called eggplant.", ("emoji", "1F346")),
        ("Chilli", "A chilli is very hot!", ("emoji", "1F336")),
        ("Cucumber", "A cucumber is cool and crunchy.", ("emoji", "1F952")),
        ("Garlic", "Garlic makes food tasty.", ("emoji", "1F9C4")),
        ("Peas", "Green peas grow in a pod.", ("emoji", "1FADB")),
        ("Broccoli", "Broccoli looks like a little tree.", ("emoji", "1F966")),
        ("Coconut", "A coconut has sweet water inside.", ("emoji", "1F965")),
    ],
    "Food": [
        ("Milk", "Milk makes our bones strong.", ("emoji", "1F95B")),
        ("Egg", "A hen lays an egg.", ("emoji", "1F95A")),
        ("Bread", "Bread is made from wheat.", ("emoji", "1F35E")),
        ("Roti", "We eat roti with dal and sabzi.", ("emoji", "1FAD3")),
        ("Rice", "Rice is a grain we eat every day.", ("emoji", "1F35A")),
        ("Honey", "Bees make honey.", ("emoji", "1F36F")),
        ("Ice Cream", "Ice cream is cold and sweet.", ("emoji", "1F366")),
        ("Cake", "We cut a cake on birthdays.", ("emoji", "1F370")),
        ("Water", "Drink clean water every day.", ("emoji", "1F4A7")),
    ],
    "Body": [
        ("Eye", "We see with our eyes.", ("emoji", "1F441")),
        ("Ear", "We hear with our ears.", ("emoji", "1F442")),
        ("Nose", "We smell with our nose.", ("emoji", "1F443")),
        ("Mouth", "We eat and talk with our mouth.", ("emoji", "1F444")),
        ("Tooth", "Brush your teeth twice a day.", ("emoji", "1F9B7")),
        ("Hand", "We hold things with our hands.", ("emoji", "270B")),
        ("Leg", "We walk and run with our legs.", ("emoji", "1F9B5")),
        ("Foot", "We stand on our feet.", ("emoji", "1F9B6")),
        ("Brain", "We think with our brain.", ("emoji", "1F9E0")),
        ("Bone", "Bones keep our body strong.", ("emoji", "1F9B4")),
    ],
    "Helpers": [
        ("Doctor", "A doctor helps us get well.", ("emoji", "1F9D1-200D-2695-FE0F")),
        ("Teacher", "A teacher helps us learn.", ("emoji", "1F9D1-200D-1F3EB")),
        ("Farmer", "A farmer grows our food.", ("emoji", "1F9D1-200D-1F33E")),
        ("Police", "The police keep us safe.", ("emoji", "1F46E")),
        ("Firefighter", "A firefighter puts out fires.", ("emoji", "1F9D1-200D-1F692")),
        ("Cook", "A cook makes tasty food.", ("emoji", "1F9D1-200D-1F373")),
        ("Pilot", "A pilot flies the aeroplane.", ("emoji", "1F9D1-200D-2708-FE0F")),
        ("Mechanic", "A mechanic repairs machines.", ("emoji", "1F9D1-200D-1F527")),
        ("Scientist", "A scientist finds out how things work.", ("emoji", "1F9D1-200D-1F52C")),
        ("Astronaut", "An astronaut goes to space.", ("emoji", "1F9D1-200D-1F680")),
    ],
    "Home": [
        ("House", "A house is where we live.", ("emoji", "1F3E0")),
        ("Chair", "We sit on a chair.", ("emoji", "1FA91")),
        ("Clock", "A clock tells the time.", ("emoji", "23F0")),
        ("Umbrella", "An umbrella keeps us dry in rain.", ("emoji", "2602")),
        ("School Bag", "We carry books in a school bag.", ("emoji", "1F392")),
        ("Pencil", "We write and draw with a pencil.", ("emoji", "270F")),
        ("Cup", "We drink from a cup.", ("emoji", "2615")),
        ("Shirt", "A shirt is something we wear.", ("emoji", "1F455")),
        ("Shoe", "We wear shoes on our feet.", ("emoji", "1F45F")),
        ("Key", "A key opens a lock.", ("emoji", "1F511")),
        ("Bulb", "A bulb gives us light.", ("emoji", "1F4A1")),
        ("Ball", "Let's kick the football!", ("emoji", "26BD")),
    ],
    "Buildings": [
        ("House", "A house is where a family lives.", ("emoji", "1F3E0")),
        ("Hut", "A small hut made of mud and straw.", ("emoji", "1F6D6")),
        ("School", "We learn and play at school.", ("emoji", "1F3EB")),
        ("Hospital", "Doctors help sick people in a hospital.", ("emoji", "1F3E5")),
        ("Temple", "People pray in a temple.", ("emoji", "1F6D5")),
        ("Mosque", "People pray in a mosque.", ("emoji", "1F54C")),
        ("Church", "People pray in a church.", ("emoji", "26EA")),
        ("Igloo", "An igloo is a house made of snow blocks.", ("shape", "igloo")),
        ("Factory", "Things are made in a factory.", ("emoji", "1F3ED")),
        ("Castle", "Kings and queens lived in a castle.", ("emoji", "1F3F0")),
        ("Tent", "We sleep in a tent when camping.", ("emoji", "26FA")),
    ],
    "Bridges": [
        ("Arch Bridge", "An arch bridge stands on one strong curve.", ("landmark", ARCH_BRIDGE)),
        ("Suspension Bridge", "Hanging from big cables, like the Golden Gate Bridge.", ("landmark", SUSPENSION_BRIDGE)),
        ("Beam Bridge", "A flat road resting on pillars.", ("landmark", BEAM_BRIDGE)),
        ("Stone Bridge", "An old stone bridge with three arches.", ("landmark", STONE_BRIDGE)),
        ("Tower Bridge", "Tower Bridge in London opens for ships.", ("landmark", TOWER_BRIDGE)),
        ("Howrah Bridge", "Howrah Bridge crosses the Hooghly in Kolkata.", ("landmark", HOWRAH_BRIDGE)),
    ],
    "Vehicles": [
        ("Car", "A car drives on the road.", ("emoji", "1F697")),
        ("Taxi", "A taxi takes us where we want to go.", ("emoji", "1F695")),
        ("Jeep", "A big car for rough roads.", ("emoji", "1F699")),
        ("Racing Car", "A racing car zooms very fast!", ("emoji", "1F3CE")),
        ("Police Car", "The police car helps keep us safe.", ("emoji", "1F693")),
        ("Ambulance", "An ambulance takes sick people to hospital.", ("emoji", "1F691")),
        ("Fire Engine", "The fire engine puts out fires.", ("emoji", "1F692")),
        ("Bus", "A bus carries many people.", ("emoji", "1F68C")),
        ("Truck", "A truck carries heavy loads.", ("emoji", "1F69A")),
        ("Pickup Truck", "A small truck with an open back.", ("emoji", "1F6FB")),
        ("Tractor", "A tractor works on the farm.", ("emoji", "1F69C")),
        ("Auto Rickshaw", "An auto has three wheels.", ("emoji", "1F6FA")),
        ("Motorbike", "A motorbike has a motor and two wheels.", ("emoji", "1F3CD")),
        ("Scooter", "A scooter is a small motorbike.", ("emoji", "1F6F5")),
        ("Bicycle", "A bicycle has two wheels and pedals.", ("emoji", "1F6B2")),
        ("Kick Scooter", "Push with your foot and glide!", ("emoji", "1F6F4")),
    ],
    "Travel": [
        ("Train", "A train engine pulls the coaches. Choo choo!", ("emoji", "1F682")),
        ("Coach", "A railway coach carries passengers.", ("emoji", "1F683")),
        ("Aeroplane", "An aeroplane flies in the sky.", ("emoji", "2708")),
        ("Helicopter", "A helicopter has spinning blades.", ("emoji", "1F681")),
        ("Ship", "A ship sails on the sea.", ("emoji", "1F6F3")),
        ("Sailboat", "The wind pushes a sailboat.", ("emoji", "26F5")),
        ("Road", "A winding road for cars and buses.", ("shape", "road")),
        ("Railway", "Railway tracks for trains.", ("shape", "railway")),
        ("Rocket", "A rocket goes to space!", ("emoji", "1F680")),
    ],
    "Sky": [
        ("Sun", "The sun gives us light and heat.", ("emoji", "2600")),
        ("Cloud", "Clouds float in the sky.", ("emoji", "2601")),
        ("Rain", "Rain falls from the clouds.", ("emoji", "1F327")),
        ("Lightning", "Lightning flashes in a storm.", ("emoji", "26A1")),
        ("Rainbow", "A rainbow has seven colours.", ("emoji", "1F308")),
        ("Snowflake", "Snow is frozen water.", ("emoji", "2744")),
        ("Earth", "The Earth is our home planet.", ("emoji", "1F30D")),
        ("Saturn", "Saturn is the planet with rings.", ("emoji", "1FA90")),
        ("Comet", "A comet has a long shining tail.", ("emoji", "2604")),
        ("Mountain", "Mountains are very high land.", ("emoji", "26F0")),
        ("Volcano", "A volcano throws out hot lava.", ("emoji", "1F30B")),
    ],
    "Countries": [
        ("India", "India - our country. Capital: New Delhi.", ("country", "India")),
        ("USA", "United States of America. Capital: Washington.", ("country", "United States")),
        ("Sri Lanka", "An island country south of India.", ("country", "Sri Lanka")),
        ("Bangladesh", "Our neighbour in the east. Capital: Dhaka.", ("country", "Bangladesh")),
        ("Nepal", "Home of Mount Everest. Capital: Kathmandu.", ("country", "Nepal")),
        ("Italy", "Italy looks like a boot! Capital: Rome.", ("country", "Italy")),
        ("UK", "United Kingdom. Capital: London.", ("country", "United Kingdom")),
        ("Japan", "Land of the rising sun. Capital: Tokyo.", ("country", "Japan")),
        ("Australia", "A country and a continent. Capital: Canberra.", ("country", "Australia")),
        ("Brazil", "Home of the Amazon forest. Capital: Brasilia.", ("country", "Brazil")),
        ("Egypt", "Land of the pyramids. Capital: Cairo.", ("country", "Egypt")),
    ],
    "States": [
        ("Karnataka", "Karnataka - capital Bengaluru.", ("state", "Karnataka")),
        ("Kerala", "Kerala - capital Thiruvananthapuram.", ("state", "Kerala")),
        ("Tamil Nadu", "Tamil Nadu - capital Chennai.", ("state", "Tamil Nadu")),
        ("Maharashtra", "Maharashtra - capital Mumbai.", ("state", "Maharashtra")),
        ("Gujarat", "Gujarat - capital Gandhinagar.", ("state", "Gujarat")),
        ("Rajasthan", "Rajasthan - the biggest state. Capital Jaipur.", ("state", "Rajasthan")),
        ("Uttar Pradesh", "Uttar Pradesh - capital Lucknow.", ("state", "Uttar Pradesh")),
        ("West Bengal", "West Bengal - capital Kolkata.", ("state", "West Bengal")),
        ("Telangana", "Telangana - capital Hyderabad.", ("state", "Telangana")),
        ("Punjab", "Punjab - land of five rivers.", ("state", "Punjab")),
    ],
    "Cities": [
        ("Delhi", "Delhi is India's capital. This is India Gate.", ("landmark", INDIA_GATE)),
        ("Agra", "Agra has the Taj Mahal.", ("landmark", TAJ_MAHAL)),
        ("Mumbai", "Mumbai has the Gateway of India.", ("landmark", GATEWAY_OF_INDIA)),
        ("Hyderabad", "Hyderabad has the Charminar.", ("landmark", CHARMINAR)),
        ("Bengaluru", "Bengaluru, the garden city, has Vidhana Soudha.", ("landmark", VIDHANA_SOUDHA)),
        ("Kolkata", "Kolkata has the Howrah Bridge.", ("landmark", HOWRAH_BRIDGE)),
        ("Paris", "Paris has the Eiffel Tower.", ("landmark", EIFFEL_TOWER)),
        ("London", "London has Big Ben.", ("landmark", BIG_BEN)),
        ("New York", "New York has the Statue of Liberty.", ("emoji", "1F5FD")),
        ("Tokyo", "Tokyo has the Tokyo Tower.", ("emoji", "1F5FC")),
        ("Dubai", "Dubai has the Burj Khalifa, the tallest building.", ("landmark", BURJ_KHALIFA)),
    ],
    "Rivers": [
        ("Ganga", "The Ganga is India's holiest river.", ("river", ["Ganges"])),
        ("Yamuna", "The Yamuna flows past Delhi and Agra.", ("river", ["Yamuna"])),
        ("Brahmaputra", "The Brahmaputra flows through Assam.", ("river", ["Brahmaputra"])),
        ("Godavari", "The Godavari is South India's longest river.", ("river", ["Godavari"])),
        ("Kaveri", "The Kaveri flows through Karnataka and Tamil Nadu.", ("river", ["Cauvery", "Kaveri"])),
        ("Narmada", "The Narmada flows west to the sea.", ("river", ["Narmada"])),
        ("Indus", "India got its name from the Indus river.", ("river", ["Indus"])),
        ("Nile", "The Nile is the longest river in the world.", ("river", ["Nile"])),
        ("Amazon", "The Amazon flows through the rainforest.", ("river", ["Amazonas", "Amazon"])),
        ("Thames", "The Thames flows through London.", ("river", ["Thames"])),
        ("Mississippi", "The Mississippi is America's big river.", ("river", ["Mississippi"])),
    ],
    "Music": [
        ("Drum", "Bang the drum - dhum dhum!", ("emoji", "1F941")),
        ("Guitar", "A guitar has strings to strum.", ("emoji", "1F3B8")),
        ("Flute", "Blow into the flute to play.", ("emoji", "1FA88")),
        ("Trumpet", "A trumpet is loud and bright.", ("emoji", "1F3BA")),
        ("Violin", "Play the violin with a bow.", ("emoji", "1F3BB")),
        ("Bell", "Ring the bell - ding dong!", ("emoji", "1F514")),
        ("Banjo", "A banjo is a round guitar.", ("emoji", "1FA95")),
        ("Maracas", "Shake the maracas!", ("emoji", "1FA87")),
    ],
    "Sports": [
        ("Cricket", "Bat, ball and wickets!", ("emoji", "1F3CF")),
        ("Badminton", "Hit the shuttlecock over the net.", ("emoji", "1F3F8")),
        ("Football", "Kick the ball into the goal.", ("emoji", "26BD")),
        ("Hockey", "Hockey is played with a stick.", ("emoji", "1F3D1")),
        ("Tennis", "Hit the tennis ball with a racket.", ("emoji", "1F3BE")),
        ("Chess", "Chess is a game of thinking.", ("emoji", "265F")),
        ("Kite", "Fly a kite high in the sky.", ("emoji", "1FA81")),
        ("Trophy", "Winners get a trophy.", ("emoji", "1F3C6")),
        ("Medal", "A medal for doing your best.", ("emoji", "1F3C5")),
    ],
    "Draw": [
        ("Custom Draw", "Draw anything you imagine, in any colour!", ("custom", None)),
    ],
    # Cartoon friends from stories (OpenMoji characters, free to use)
    "Cartoons": [
        ("Superhero", "A superhero is brave and helps people.", ("emoji", "1F9B8")),
        ("Robot", "A robot is a machine that can move and help.", ("emoji", "1F916")),
        ("Unicorn", "A magic horse with one horn.", ("emoji", "1F984")),
        ("Dragon", "A dragon is a big flying creature from stories.", ("emoji", "1F409")),
        ("Fairy", "A tiny fairy with shiny wings.", ("emoji", "1F9DA")),
        ("Mermaid", "Half girl, half fish, she lives in the sea.", ("emoji", "1F9DC-200D-2640-FE0F")),
        ("Genie", "A genie comes out of a lamp to grant wishes.", ("emoji", "1F9DE")),
        ("Wizard", "A wizard does magic with a wand.", ("emoji", "1F9D9")),
        ("Prince", "A prince is the son of a king.", ("emoji", "1F934")),
        ("Princess", "A princess is the daughter of a king.", ("emoji", "1F478")),
        ("Ninja", "A ninja moves quietly and quickly.", ("emoji", "1F977")),
        ("Alien", "A friendly visitor from another planet.", ("emoji", "1F47D")),
        ("Ghost", "A friendly little ghost says Boo!", ("emoji", "1F47B")),
        ("Teddy Bear", "A soft teddy bear to hug.", ("emoji", "1F9F8")),
        ("Snowman", "We build a snowman with snow in winter.", ("emoji", "26C4")),
        ("Santa", "Santa Claus brings gifts at Christmas.", ("emoji", "1F385")),
        ("Panda", "A cute panda loves to eat bamboo.", ("emoji", "1F43C")),
        ("Elf", "An elf is a little helper from stories.", ("emoji", "1F9DD")),
    ],
}


# Subject tabs (top row of the game) -> categories (second row)
SUBJECTS = {
    "English": ["ABC", "abc"],
    "Hindi": ["Swar", "Vyanjan"],
    "Maths": ["123", "Shapes", "Signs"],
    "Nature": ["Animals", "Birds", "Sea", "Reptiles", "Insects", "Plants"],
    "Food": ["Fruits", "Vegetables", "Food"],
    "Me & Home": ["Body", "Home", "Buildings", "Helpers"],
    "Travel": ["Vehicles", "Travel", "Bridges"],
    "World": ["Sky", "Countries", "States", "Cities", "Rivers"],
    "Fun": ["Cartoons", "Music", "Sports", "Draw"],
}


def spoken_text(name, cat=None):
  """What the voice says when an item is picked."""
  item = _find(name, cat)
  src = item["source"] if item else ""
  if src == "custom":
    return "Draw anything you imagine! Pick a colour, draw, then tap Done."
  if src in ("glyph", "hindi"):
    return item["desc"].replace(" - ", ". ") + "!"
  letters = ", ".join(ch for ch in name.upper() if ch.isalpha())
  return f"{name}. {letters}. {name}!"


def hindi_speech(name, cat=None, praise=False):
  """Hindi words to say for Hindi letters (None for other items)."""
  item = _find(name, cat)
  if not item or "hindi" not in item:
    return None
  return f"शाबाश! {item['hindi']}" if praise else item["hindi"]


def praise_text(name, cat=None):
  item = _find(name, cat)
  if item and item["source"] == "custom":
    return "Wonderful drawing!"
  if item and item["source"] in ("glyph", "hindi"):
    return f"Well done! {item['desc'].split(' - ')[0]}!"
  return f"Well done! {name}!"


# --------------------------------------------------------------------------
# Runtime access (used by main.py)
# --------------------------------------------------------------------------
_OUTLINES = {}
if os.path.exists(HUB_JSON):
  with open(HUB_JSON, encoding="utf-8") as fh:
    _OUTLINES = json.load(fh)


def item_key(cat, name):
  """Hub key; letters like 'a' and 'A' need the category to stay distinct."""
  return f"{cat}/{name}"


# category -> {item name -> {"desc", "source", ...outline data}}; only items
# whose outline was built are listed, so the game never shows a blank item.
CATEGORIES_HUB = {}
_BY_NAME = {}
for _cat, _items in CATALOG.items():
  _bucket = {}
  for _name, _desc, _src in _items:
    _data = _OUTLINES.get(item_key(_cat, _name))
    if _src[0] == "custom" or _data:
      _bucket[_name] = dict(desc=_desc, source=_src[0], **(_data or {}))
      if _src[0] == "hindi":
        _bucket[_name]["hindi"], _bucket[_name]["label"] = _src[1]
      if item_key(_cat, _name) in TRANSLATIONS:
        _bucket[_name]["hi"], _bucket[_name]["bn"] = TRANSLATIONS[item_key(_cat, _name)]
      if _src[0] == "glyph" and not _name.isalnum():
        # maths signs: the title spells the word ("Plus", "Rupee")
        _bucket[_name]["tile_text"] = _desc.split(" - ")[0]
      _BY_NAME.setdefault(_name, _bucket[_name])
  if _bucket:
    CATEGORIES_HUB[_cat] = _bucket


def _find(name, cat=None):
  if cat is not None:
    return CATEGORIES_HUB.get(cat, {}).get(name)
  return _BY_NAME.get(name)


def _fit(item, box, margin=0.9):
  """Scale factor + offset that fit an item's 0..w x 0..h space into box."""
  bx, by, bw, bh = box
  w, h = item["w"], item["h"]
  s = min(bw * margin / w, bh * margin / h)
  ox = bx + (bw - w * s) / 2
  oy = by + (bh - h * s) / 2
  return s, ox, oy


def _resample(pts, closed, spacing):
  if closed:
    pts = pts + [pts[0]]
  out = [pts[0]]
  carry = 0.0
  for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    seg = math.hypot(x1 - x0, y1 - y0)
    if seg == 0:
      continue
    d = spacing - carry
    while d <= seg:
      t = d / seg
      out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
      d += spacing
    carry = seg - (d - spacing)
  if closed and len(out) > 1 and math.hypot(
      out[-1][0] - out[0][0], out[-1][1] - out[0][1]) < spacing * 0.5:
    out.pop()
  return out


def _length(pts, closed):
  total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
  if closed and len(pts) > 2:
    total += math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
  return total


def fetch_path_from_hub(shape_name, box, custom_points=None, cat=None,
                        max_dots=110, min_spacing=14):
  """Outline of an item as evenly spaced dots in screen coordinates.

  Returns a list of loops (each a list of (x, y)). Dominoes follow the loops
  one after another.
  """
  item = _find(shape_name, cat)
  if item is None:
    return []
  if item["source"] == "custom":
    if not custom_points or len(custom_points) < 2:
      return []
    # evenly spaced along the child's line, however fast it was drawn
    dots = _resample(list(custom_points), False, min_spacing)
    return [dots] if len(dots) >= 2 else []

  s, ox, oy = _fit(item, box)
  closed = item.get("closed", True)
  loops = [[(ox + x * s, oy + y * s) for x, y in loop] for loop in item["loops"]]
  total = sum(_length(lp, closed) for lp in loops)
  spacing = max(min_spacing, total / max_dots)
  out = []
  for lp in loops:
    dots = _resample(lp, closed, spacing)
    if len(dots) >= (3 if closed else 2):
      out.append(dots)
  return out


def fetch_context_from_hub(shape_name, box, cat=None):
  """Faint background lines (e.g. country borders around a river)."""
  item = _find(shape_name, cat)
  if not item or not item.get("context"):
    return []
  s, ox, oy = _fit(item, box)
  return [[(ox + x * s, oy + y * s) for x, y in line] for line in item["context"]]


def fetch_thumb_from_hub(shape_name, cat=None):
  """Small picture for item buttons and the title banner."""
  item = _find(shape_name, cat)
  if not item or not item.get("thumb"):
    return None
  return os.path.join(HERE, item["thumb"])


_VIDEOS = None


def fetch_video_from_hub(shape_name, cat=None):
  """Checked real-life video of the item (videos.json), or None."""
  global _VIDEOS
  if _VIDEOS is None:
    try:
      with open(os.path.join(HERE, "videos.json"), encoding="utf-8") as fh:
        _VIDEOS = json.load(fh)
    except (OSError, ValueError):
      _VIDEOS = {}
  if cat is None:
    cat = next((c for c, items in CATEGORIES_HUB.items() if shape_name in items), None)
  return _VIDEOS.get(item_key(cat, shape_name))


def subjects():
  """Subject -> categories that actually have items (top two button rows)."""
  out = {}
  for subj, cats in SUBJECTS.items():
    present = [c for c in cats if c in CATEGORIES_HUB]
    if present:
      out[subj] = present
  return out


def fetch_picture_from_hub(shape_name, box=None, cat=None):
  """(path, screen_rect) of the item's real picture. The rect lines the
  picture up exactly over the traced outline (None if box not given)."""
  item = _find(shape_name, cat)
  if not item or not item.get("pic"):
    return None, None
  path = os.path.join(HERE, item["pic"])
  if box is None:
    return path, None
  s, ox, oy = _fit(item, box)
  x0, y0, x1, y1 = item["pic_frame"]
  return path, (ox + x0 * s, oy + y0 * s, (x1 - x0) * s, (y1 - y0) * s)
