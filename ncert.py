"""Which picture categories belong to which class, for the Class Pavilions' Subject Magic
Console (world.py): CLASS_TOPICS[class][button] = [category, ...], this class's own NCERT
topics first. Buttons: "evs" (Classes 1-5), "science" and "social" (Classes 6-7).
"""

CLASS_TOPICS = {
    1: {"evs": ["Living & Non-living", "My Family", "Clean & Healthy"]},
    2: {"evs": ["Seasons & Weather", "Helpers Around Us", "Clean & Healthy"]},
    3: {"evs": ["Animal Homes", "Water O' Water", "Flying High", "Houses We Live In"]},
    4: {"evs": ["Going to School", "Save the Trees", "Basva's Farm", "Animal Homes"]},
    5: {"evs": ["Super Senses", "Tasting to Digesting", "Float or Sink", "Up You Go"]},
    6: {"science": ["Food & Nutrients", "Deficiency Diseases", "Plant Parts", "Body Movements",
                    "Light & Shadows", "Energy"],
        "social": ["Early Humans", "Kings & Empires", "Moon Phases", "Globe & Time", "Government & Us"]},
    7: {"science": ["How Living Things Eat", "Heat", "Acids & Bases", "Changes Around Us",
                    "Breathing & Blood", "Motion & Time"],
        "social": ["Kings & Empires", "Government & Us", "Globe & Time"]},
}
