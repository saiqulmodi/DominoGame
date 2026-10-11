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

# Monuments of India (right half, mirrored like the landmarks above)
WAR_MEMORIAL = [                     # National War Memorial: the eternal-flame pillar
    (50, 0), (51.6, 5), (52.6, 12), (54, 70), (60, 70), (60, 78), (72, 78),
    (72, 86), (86, 86), (86, 93), (100, 93), (100, 100), (50, 100),
]
QUTUB_MINAR = [
    (50, 0), (53, 3), (53, 8), (56, 8), (56, 11), (54.5, 11), (55.5, 24), (58.5, 24),
    (58.5, 27), (56.5, 27), (58, 42), (61, 42), (61, 45), (59, 45), (60.5, 60),
    (63.5, 60), (63.5, 63), (61.5, 63), (63, 78), (66, 78), (66, 81), (64, 81),
    (65.5, 94), (72, 94), (72, 100), (50, 100),
]
RED_FORT = [                         # Lahori Gate: gateway between two towers
    (50, 22), (52, 24), (53, 28), (56, 28), (56, 34), (64, 34), (64, 26), (66, 22),
    (66, 18), (68, 13), (70, 10), (72, 13), (74, 18), (74, 22), (76, 26), (76, 50),
    (84, 50), (84, 46), (87, 46), (87, 50), (92, 50), (92, 46), (95, 46), (95, 50),
    (100, 50), (100, 100), (60, 100), (60, 72), (58.7, 65), (55, 60.5), (50, 59),
]
LOTUS_TEMPLE = [
    (50, 6), (53, 12), (56, 22), (59, 31), (63, 21), (66, 12), (68, 22), (70, 35),
    (76, 30), (83, 26), (84, 38), (84.5, 50), (91, 48), (99, 52), (95, 60), (91, 66),
    (96, 66), (96, 74), (100, 74), (100, 86), (50, 86),
]
GOLDEN_TEMPLE = [
    (50, 4), (51, 8), (53, 10), (57, 14), (60, 20), (61, 26), (59, 30), (60, 32),
    (63, 32), (63, 35), (72, 35), (72, 28), (74, 24), (75, 20), (76, 24), (78, 28),
    (78, 35), (84, 35), (84, 39), (80, 39), (80, 58), (86, 58), (86, 62), (82, 62),
    (82, 90), (100, 90), (100, 100), (50, 100),
]
HAWA_MAHAL = [                       # Jaipur's palace of winds: stepped front
    (50, 2), (52, 0), (54, 2), (54, 10), (57, 10), (58, 8), (60, 10), (60, 22),
    (63, 22), (64, 20), (66, 22), (66, 36), (70, 36), (71, 34), (73, 36), (73, 52),
    (78, 52), (79, 50), (81, 52), (81, 66), (86, 66), (87, 64), (89, 66), (89, 100),
    (50, 100),
]
MYSURU_PALACE = [
    (50, 0), (51, 4), (54, 8), (57, 14), (58, 20), (56, 24), (58, 26), (58, 40),
    (62, 40), (62, 46), (68, 46), (68, 36), (69, 32), (71, 28), (73, 32), (74, 36),
    (74, 46), (84, 46), (84, 40), (86, 36), (88, 40), (88, 46), (96, 46), (96, 54),
    (100, 54), (100, 100), (50, 100),
]
MEENAKSHI_GOPURAM = [                # tall temple gateway tower of Madurai
    (50, 2), (52, 2), (52, 6), (58, 6), (60, 2), (62, 6), (62, 12), (60.5, 12),
    (62, 24), (64, 24), (65, 36), (67, 36), (68, 48), (70, 48), (71, 60), (73, 60),
    (74, 72), (76, 72), (77, 84), (80, 84), (80, 100), (50, 100),
]
SANCHI_STUPA = (
    [(50, 0), (57, 0), (57, 3), (51.5, 3), (51.5, 8), (56, 8), (56, 18)]
    + [(50 + 38 * math.cos(math.radians(a)), 58 - 38 * math.sin(math.radians(a)))
       for a in range(80, -1, -10)]
    + [(92, 58), (92, 74), (96, 74), (96, 100), (50, 100)],
    [],
)
GOL_GUMBAZ = (
    [(50, 8), (51, 14)]
    + [(50 + 30 * math.cos(math.radians(a)), 46 - 30 * math.sin(math.radians(a)))
       for a in range(86, -1, -8)]
    + [(84, 46), (84, 30), (86, 26), (88, 22), (90, 26), (92, 30), (92, 100), (50, 100)],
    [],
)
KONARK_WHEEL = (                     # wheel of the Sun Temple chariot, 8 spokes
    [(50 + 48 * math.sin(math.radians(a)), 50 - 48 * math.cos(math.radians(a)))
     for a in range(0, 181, 10)],
    [
        [(50 + r * math.sin(math.radians(a0 + t * (a1 - a0) / 6)),
          50 - r * math.cos(math.radians(a0 + t * (a1 - a0) / 6)))
         for r, ts in ((38, range(7)), (12, range(6, -1, -1))) for t in ts]
        for a0, a1 in [(k * 45 + 7, k * 45 + 38) for k in range(8)]
    ],
)

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

# India, state by state: (name in the game, Natural Earth name, capital,
# capital (lat, lon), famous places shown on the map [(name, lat, lon)],
# what it is famous for). The maps follow India's official boundaries.
INDIA_STATES = [
    ("Andhra Pradesh", "Andhra Pradesh", "Amaravati", (16.51, 80.52),
     [("Tirupati", 13.63, 79.42), ("Visakhapatnam", 17.69, 83.22)],
     "Tirupati temple and the Araku valley."),
    ("Arunachal Pradesh", "Arunachal Pradesh", "Itanagar", (27.08, 93.61),
     [("Tawang Monastery", 27.59, 91.86)], "India's first sunrise and Tawang Monastery."),
    ("Assam", "Assam", "Dispur", (26.14, 91.79),
     [("Kaziranga", 26.58, 93.17), ("Majuli Island", 26.95, 94.17)],
     "Kaziranga's one-horned rhinos and tea gardens."),
    ("Bihar", "Bihar", "Patna", (25.59, 85.14),
     [("Bodh Gaya", 24.70, 84.99), ("Nalanda", 25.14, 85.44)],
     "Bodh Gaya and the old Nalanda University."),
    ("Chhattisgarh", "Chhattisgarh", "Raipur", (21.25, 81.63),
     [("Chitrakote Falls", 19.21, 81.70)], "Chitrakote Falls and green forests."),
    ("Goa", "Goa", "Panaji", (15.49, 73.83),
     [("Old Goa churches", 15.50, 73.95), ("Palolem Beach", 15.01, 74.02)],
     "Sunny beaches and old churches."),
    ("Gujarat", "Gujarat", "Gandhinagar", (23.22, 72.65),
     [("Statue of Unity", 21.84, 73.72), ("Gir lions", 21.12, 70.82),
      ("Rann of Kutch", 23.85, 69.80)],
     "Statue of Unity, Gir lions and the white Rann."),
    ("Haryana", "Haryana", "Chandigarh", (30.73, 76.78),
     [("Kurukshetra", 29.97, 76.85), ("Gurugram", 28.46, 77.03)],
     "Kurukshetra and fields of wheat."),
    ("Himachal Pradesh", "Himachal Pradesh", "Shimla", (31.10, 77.17),
     [("Manali", 32.24, 77.19), ("Dharamshala", 32.22, 76.32)],
     "Snowy mountains and apple orchards."),
    ("Jharkhand", "Jharkhand", "Ranchi", (23.34, 85.31),
     [("Hundru Falls", 23.45, 85.65), ("Jamshedpur", 22.80, 86.20)],
     "Waterfalls, forests and the steel city Jamshedpur."),
    ("Karnataka", "Karnataka", "Bengaluru", (12.97, 77.59),
     [("Mysuru Palace", 12.31, 76.65), ("Hampi", 15.34, 76.46), ("Gol Gumbaz", 16.83, 75.74)],
     "Mysuru Palace, Hampi, coffee and silk."),
    ("Kerala", "Kerala", "Thiruvananthapuram", (8.52, 76.94),
     [("Backwaters", 9.50, 76.34), ("Munnar tea hills", 10.09, 77.06)],
     "Backwaters, houseboats and coconut trees."),
    ("Madhya Pradesh", "Madhya Pradesh", "Bhopal", (23.26, 77.41),
     [("Sanchi Stupa", 23.48, 77.74), ("Khajuraho", 24.85, 79.92), ("Kanha tigers", 22.33, 80.61)],
     "The heart of India: Sanchi, Khajuraho and tigers."),
    ("Maharashtra", "Maharashtra", "Mumbai", (19.08, 72.88),
     [("Ajanta Caves", 20.55, 75.70), ("Ellora Caves", 20.03, 75.18), ("Pune", 18.52, 73.86)],
     "Gateway of India, Ajanta and Ellora caves."),
    ("Manipur", "Manipur", "Imphal", (24.82, 93.94),
     [("Loktak Lake", 24.55, 93.80)], "Loktak Lake with floating islands."),
    ("Meghalaya", "Meghalaya", "Shillong", (25.58, 91.89),
     [("Cherrapunji", 25.27, 91.73)], "Home of clouds and living root bridges."),
    ("Mizoram", "Mizoram", "Aizawl", (23.73, 92.72),
     [("Vantawng Falls", 23.12, 92.75)], "Green hills and bamboo forests."),
    ("Nagaland", "Nagaland", "Kohima", (25.67, 94.11),
     [("Mokokchung", 26.32, 94.52)], "The colourful Hornbill Festival."),
    ("Odisha", "Odisha", "Bhubaneswar", (20.30, 85.82),
     [("Konark Sun Temple", 19.89, 86.09), ("Chilika Lake", 19.72, 85.32)],
     "Konark Sun Temple and Puri Jagannath."),
    ("Punjab", "Punjab", "Chandigarh", (30.73, 76.78),
     [("Golden Temple", 31.62, 74.88), ("Ludhiana", 30.90, 75.85)],
     "Golden Temple, land of five rivers."),
    ("Rajasthan", "Rajasthan", "Jaipur", (26.91, 75.79),
     [("Jaisalmer Fort", 26.91, 70.91), ("Udaipur lakes", 24.58, 73.71),
      ("Ranthambore", 26.02, 76.50)],
     "Hawa Mahal, forts, camels and the Thar desert."),
    ("Sikkim", "Sikkim", "Gangtok", (27.33, 88.61),
     [("Kanchenjunga", 27.70, 88.15)], "Kanchenjunga, India's highest mountain."),
    ("Tamil Nadu", "Tamil Nadu", "Chennai", (13.08, 80.27),
     [("Meenakshi Temple", 9.92, 78.12), ("Big Temple", 10.78, 79.13),
      ("Kanyakumari", 8.08, 77.54)],
     "Meenakshi Temple, Big Temple and Kanyakumari."),
    ("Telangana", "Telangana", "Hyderabad", (17.39, 78.49),
     [("Ramappa Temple", 18.26, 79.94)], "Charminar and the Ramappa Temple."),
    ("Tripura", "Tripura", "Agartala", (23.83, 91.29),
     [("Neermahal", 23.50, 91.31)], "Ujjayanta Palace and the Neermahal water palace."),
    ("Uttar Pradesh", "Uttar Pradesh", "Lucknow", (26.85, 80.95),
     [("Taj Mahal", 27.17, 78.04), ("Varanasi ghats", 25.31, 83.01), ("Prayagraj", 25.43, 81.88)],
     "Taj Mahal, Varanasi ghats and the Ganga."),
    ("Uttarakhand", "Uttarakhand", "Dehradun", (30.32, 78.03),
     [("Kedarnath", 30.73, 79.07), ("Jim Corbett", 29.53, 78.77), ("Haridwar", 29.95, 78.16)],
     "Himalayas, the Ganga's source and Corbett tigers."),
    ("West Bengal", "West Bengal", "Kolkata", (22.57, 88.36),
     [("Darjeeling", 27.04, 88.26), ("Sundarbans", 21.95, 88.90)],
     "Howrah Bridge, Darjeeling tea and Sundarbans tigers."),
]
INDIA_UTS = [
    ("Andaman & Nicobar", "Andaman and Nicobar", "Sri Vijaya Puram", (11.62, 92.73),
     [("Radhanagar Beach", 11.98, 92.95)], "Islands with coral reefs and the Cellular Jail."),
    ("Chandigarh", "Chandigarh", "Chandigarh", (30.73, 76.78),
     [("Rock Garden", 30.755, 76.805), ("Sukhna Lake", 30.742, 76.818)],
     "A planned city with the Rock Garden."),
    ("Daman & Diu", "Dadra and Nagar Haveli and Daman and Diu", "Daman", (20.40, 72.83),
     [("Silvassa", 20.27, 73.01), ("Diu", 20.71, 70.99)],
     "Dadra and Nagar Haveli and Daman and Diu: beaches and forts."),
    ("Delhi", "Delhi", "New Delhi", (28.6143, 77.1994),
     [("War Memorial & India Gate", 28.6128, 77.2312), ("Red Fort", 28.6562, 77.2410),
      ("Qutub Minar", 28.5245, 77.1855), ("Lotus Temple", 28.5535, 77.2588),
      ("Akshardham", 28.6127, 77.2773)],
     "Capital of India: War Memorial, India Gate, Red Fort, Qutub Minar."),
    ("Jammu & Kashmir", "Jammu and Kashmir", "Srinagar", (34.08, 74.80),
     [("Jammu", 32.73, 74.86), ("Gulmarg", 34.05, 74.38), ("Vaishno Devi", 33.03, 74.95)],
     "Capitals: Srinagar (summer) and Jammu (winter). Dal Lake, saffron."),
    ("Ladakh", "Ladakh", "Leh", (34.15, 77.58),
     [("Kargil", 34.56, 76.13), ("Pangong Lake", 33.75, 78.66)],
     "A cold desert with high passes and Pangong Lake."),
    ("Lakshadweep", "Lakshadweep", "Kavaratti", (10.57, 72.64),
     [("Agatti", 10.85, 72.19)], "36 coral islands in the Arabian Sea."),
    ("Puducherry", "Puducherry", "Puducherry", (11.94, 79.81),
     [("Auroville", 12.01, 79.81), ("Karaikal", 10.92, 79.84)],
     "French-style streets, beaches and Auroville."),
]
# Short names for the India map when a full name does not fit inside a state
INDIA_SHORT = {
    "Uttar Pradesh": "UP", "Madhya Pradesh": "MP", "Andhra Pradesh": "AP", "Tamil Nadu": "TN",
    "West Bengal": "WB", "Himachal Pradesh": "HP", "Arunachal Pradesh": "Arunachal",
    "Jammu & Kashmir": "J&K", "Andaman & Nicobar": "A&N", "Chhattisgarh": "CG",
    "Uttarakhand": "UK", "Maharashtra": "MH", "Karnataka": "KA", "Telangana": "TG",
    "Jharkhand": "JH", "Rajasthan": "RJ", "Gujarat": "GJ", "Haryana": "HR", "Odisha": "OD",
    "Meghalaya": "ML", "Nagaland": "NL", "Manipur": "MN", "Mizoram": "MZ", "Tripura": "TR",
    "Kerala": "KL", "Punjab": "PB", "Bihar": "BR", "Assam": "AS", "Sikkim": "SK",
    "Ladakh": "LA", "Delhi": "DL", "Goa": "Goa", "Puducherry": "PY", "Lakshadweep": "LD",
    "Chandigarh": "CH", "Daman & Diu": "DD",
}
# game name -> capital, used for speech
INDIA_CAPITALS = {n: cap for n, _ne, cap, *_rest in INDIA_STATES + INDIA_UTS}
# Natural Earth name -> (capital, (lat, lon), places) for the map builder
INDIA_PLACES = {ne: (cap, at, places) for _n, ne, cap, at, places, _f in INDIA_STATES + INDIA_UTS}

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
    # India: the whole map, all 28 states, 8 union territories, monuments
    "India Map": [
        ("India Map", "India: 28 states and 8 union territories. Capital: New Delhi.",
         ("india_map", None)),
    ],
    "States": [(name, f"Capital: {cap}. {famous}", ("state", ne))
               for name, ne, cap, _at, _places, famous in INDIA_STATES],
    "UTs": [(name, f"Capital: {cap}. {famous}" if not famous.startswith("Capital")
             else famous, ("state", ne))
            for name, ne, cap, _at, _places, famous in INDIA_UTS],
    "Monuments": [
        ("War Memorial", "National War Memorial, New Delhi: we honour our brave soldiers.",
         ("landmark", WAR_MEMORIAL)),
        ("Qutub Minar", "Qutub Minar, Delhi: a tall tower of red stone.", ("landmark", QUTUB_MINAR)),
        ("Red Fort", "Red Fort, Delhi: our flag is raised here on 15 August.", ("landmark", RED_FORT)),
        ("Lotus Temple", "Lotus Temple, Delhi: shaped like a lotus flower.", ("landmark", LOTUS_TEMPLE)),
        ("Golden Temple", "Golden Temple, Amritsar in Punjab, shines with gold.",
         ("landmark", GOLDEN_TEMPLE)),
        ("Hawa Mahal", "Hawa Mahal, Jaipur: a palace with 953 small windows.", ("landmark", HAWA_MAHAL)),
        ("Mysuru Palace", "Mysuru Palace, Karnataka, lights up for Dasara.", ("landmark", MYSURU_PALACE)),
        ("Meenakshi Temple", "Meenakshi Temple, Madurai: tall colourful towers.",
         ("landmark", MEENAKSHI_GOPURAM)),
        ("Sanchi Stupa", "Sanchi Stupa, Madhya Pradesh: a great Buddhist dome.", ("landmark", SANCHI_STUPA)),
        ("Gol Gumbaz", "Gol Gumbaz, Vijayapura: a giant dome that echoes.", ("landmark", GOL_GUMBAZ)),
        ("Konark Wheel", "Konark Sun Temple wheel, Odisha: it can tell the time!",
         ("landmark", KONARK_WHEEL)),
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
    "India": ["India Map", "States", "UTs", "Monuments"],
    "Nature": ["Animals", "Birds", "Sea", "Reptiles", "Insects", "Plants"],
    "Food": ["Fruits", "Vegetables", "Food"],
    "Me & Home": ["Body", "Home", "Buildings", "Helpers"],
    "Travel": ["Vehicles", "Travel", "Bridges"],
    "World": ["Sky", "Countries", "Cities", "Rivers"],
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
  return f"{name}. {letters}. {name}!" + _capital_line(name, src)


def _capital_line(name, src):
  """States and union territories also say their capital."""
  if src == "india_map":
    return " India has 28 states and 8 union territories. Our capital is New Delhi."
  if src != "state" or name not in INDIA_CAPITALS:
    return ""
  if name == "Jammu & Kashmir":
    return " Its capitals are Srinagar and Jammu."
  return f" Its capital is {INDIA_CAPITALS[name]}."


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
  return f"Well done! {name}!" + (_capital_line(name, item["source"]) if item else "")


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


def fetch_places_from_hub(shape_name, box, cat=None):
  """Capital, famous places (and state names on the India map) as
  [(label, x, y, kind, room)] in screen coordinates; kind is "capital",
  "place" or "state"; room is how far a state's middle is from its edge."""
  item = _find(shape_name, cat)
  if not item or not item.get("places"):
    return []
  s, ox, oy = _fit(item, box)
  return [(p[0], ox + p[1] * s, oy + p[2] * s, p[3], (p[4] if len(p) > 4 else 0) * s)
          for p in item["places"]]


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
