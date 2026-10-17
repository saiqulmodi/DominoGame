"""Rhymes and School Hub for Domino Wonder Dash.

Sing-along rhymes: the child traces the rhyme's picture (a star for Twinkle
Twinkle, a sheep for Baa Baa Black Sheep ...), the dominoes topple, and then
the words appear line by line and are sung (spoken) together, each word
lighting up with a little xylophone note (singalong.py).

Only traditional rhymes that are free for everyone (public domain) are here.
Songs that still belong to someone (Baby Shark, Wheels on the Bus, I'm a
Little Teapot, film songs such as Chanda Mama Door Ke or Lakdi Ki Kathi) are
left out, and so are YouTube videos of other people's cartoons: a children's
app may not use them without the owner's permission.

Each rhyme: name -> desc (shown under the name), emoji (OpenMoji picture to
trace), lines (the words, in English letters), optional native lines (Hindi
or Bengali script) with their lang, and optional hi / bn names.
NCERT Class 1-5 below is kept for later (no pictures built yet, so hidden).
"""


def _rhyme(emoji, lines, hi=None, bn=None, native=None, lang="en", closed=True):
  return {"desc": lines[0].rstrip(",;:"), "emoji": emoji, "lines": lines, "native": native,
          "lang": lang, "hi": hi, "bn": bn, "closed": closed}


CLASSIC_RHYMES = {
    "Twinkle Twinkle": _rhyme("2B50", [
        "Twinkle, twinkle, little star,",
        "How I wonder what you are!",
        "Up above the world so high,",
        "Like a diamond in the sky.",
        "Twinkle, twinkle, little star,",
        "How I wonder what you are!",
    ], hi="ट्विंकल ट्विंकल लिटिल स्टार", bn="টুইঙ্কল টুইঙ্কল"),
    "ABC Song": _rhyme("1F524", [
        "A, B, C, D, E, F, G,",
        "H, I, J, K, L, M, N, O, P,",
        "Q, R, S, T, U, V,",
        "W, X, Y and Z.",
        "Now I know my A B C,",
        "Next time won't you sing with me?",
    ]),
    "Baa Baa Black Sheep": _rhyme("1F411", [
        "Baa, baa, black sheep, have you any wool?",
        "Yes sir, yes sir, three bags full!",
        "One for the master, and one for the dame,",
        "And one for the little boy who lives down the lane.",
    ], hi="बा बा ब्लैक शीप", bn="বা বা ব্ল্যাক শিপ"),
    "Johny Johny": _rhyme("1F36C", [
        "Johny, Johny! Yes, Papa?",
        "Eating sugar? No, Papa!",
        "Telling lies? No, Papa!",
        "Open your mouth! Ha, ha, ha!",
    ]),
    "Humpty Dumpty": _rhyme("1F95A", [
        "Humpty Dumpty sat on a wall,",
        "Humpty Dumpty had a great fall.",
        "All the king's horses and all the king's men",
        "Couldn't put Humpty together again.",
    ], hi="हम्प्टी डम्प्टी", bn="হাম্পটি ডাম্পটি"),
    "Jack and Jill": _rhyme("1FAA3", [
        "Jack and Jill went up the hill",
        "To fetch a pail of water.",
        "Jack fell down and broke his crown,",
        "And Jill came tumbling after.",
    ]),
    "Chubby Cheeks": _rhyme("1F467", [
        "Chubby cheeks, dimple chin,",
        "Rosy lips, teeth within,",
        "Curly hair, very fair,",
        "Eyes are blue, lovely too.",
        "Teacher's pet, is that you?",
        "Yes, yes, yes!",
    ]),
    "Rain Rain Go Away": _rhyme("1F327", [
        "Rain, rain, go away,",
        "Come again another day.",
        "Little children want to play,",
        "Rain, rain, go away.",
    ]),
    "Hickory Dickory Dock": _rhyme("1F570", [
        "Hickory, dickory, dock,",
        "The mouse ran up the clock.",
        "The clock struck one,",
        "The mouse ran down,",
        "Hickory, dickory, dock.",
    ]),
    "Two Little Dicky Birds": _rhyme("1F426", [
        "Two little dicky birds sitting on a wall,",
        "One named Peter, one named Paul.",
        "Fly away, Peter! Fly away, Paul!",
        "Come back, Peter! Come back, Paul!",
    ]),
    "Pussy Cat": _rhyme("1F408", [
        "Pussy cat, pussy cat, where have you been?",
        "I've been to London to visit the Queen.",
        "Pussy cat, pussy cat, what did you there?",
        "I frightened a little mouse under her chair.",
    ]),
    "Row Your Boat": _rhyme("1F6F6", [
        "Row, row, row your boat,",
        "Gently down the stream.",
        "Merrily, merrily, merrily, merrily,",
        "Life is but a dream.",
    ]),
    "Itsy Bitsy Spider": _rhyme("1F577", [
        "The itsy bitsy spider climbed up the water spout.",
        "Down came the rain and washed the spider out.",
        "Out came the sun and dried up all the rain,",
        "And the itsy bitsy spider climbed up the spout again.",
    ]),
    "Hot Cross Buns": _rhyme("1F35E", [
        "Hot cross buns! Hot cross buns!",
        "One a penny, two a penny, hot cross buns!",
        "If you have no daughters, give them to your sons.",
        "One a penny, two a penny, hot cross buns!",
    ]),
    "Buckle My Shoe": _rhyme("1F45F", [
        "One, two, buckle my shoe;",
        "Three, four, knock at the door;",
        "Five, six, pick up sticks;",
        "Seven, eight, lay them straight;",
        "Nine, ten, a big fat hen!",
    ]),
    "Hey Diddle Diddle": _rhyme("1F404", [
        "Hey diddle diddle, the cat and the fiddle,",
        "The cow jumped over the moon.",
        "The little dog laughed to see such fun,",
        "And the dish ran away with the spoon.",
    ]),
    "Mary's Little Lamb": _rhyme("1F411", [
        "Mary had a little lamb, its fleece was white as snow,",
        "And everywhere that Mary went, the lamb was sure to go.",
        "It followed her to school one day, which was against the rule;",
        "It made the children laugh and play to see a lamb at school.",
    ]),
    "Little Miss Muffet": _rhyme("1F963", [
        "Little Miss Muffet sat on a tuffet,",
        "Eating her curds and whey.",
        "Along came a spider, who sat down beside her,",
        "And frightened Miss Muffet away.",
    ]),
    "Lazy Mary": _rhyme("1F6CF", [
        "Lazy Mary, will you get up,",
        "Will you get up, will you get up?",
        "Lazy Mary, will you get up,",
        "Will you get up today?",
    ]),
    "Pat-a-Cake": _rhyme("1F382", [
        "Pat-a-cake, pat-a-cake, baker's man,",
        "Bake me a cake as fast as you can.",
        "Roll it, and pat it, and mark it with B,",
        "And put it in the oven for baby and me!",
    ]),
    "Polly Put the Kettle On": _rhyme("1FAD6", [
        "Polly, put the kettle on,",
        "Polly, put the kettle on,",
        "Polly, put the kettle on,",
        "We'll all have tea.",
        "Sukey, take it off again,",
        "Sukey, take it off again,",
        "Sukey, take it off again,",
        "They've all gone away.",
    ]),
    "Five Little Monkeys": _rhyme("1F412", [
        "Five little monkeys jumping on the bed,",
        "One fell off and bumped his head.",
        "Mama called the doctor, and the doctor said,",
        "No more monkeys jumping on the bed!",
    ]),
    "Old MacDonald": _rhyme("1F416", [
        "Old MacDonald had a farm, E-I-E-I-O!",
        "And on that farm he had a pig, E-I-E-I-O!",
        "With an oink-oink here, and an oink-oink there,",
        "Here an oink, there an oink, everywhere an oink-oink!",
        "Old MacDonald had a farm, E-I-E-I-O!",
    ]),
    "Little Jack Horner": _rhyme("1F967", [
        "Little Jack Horner sat in the corner,",
        "Eating his Christmas pie;",
        "He put in his thumb, and pulled out a plum,",
        "And said, What a good boy am I!",
    ]),
    "Once I Caught a Fish": _rhyme("1F420", [
        "One, two, three, four, five,",
        "Once I caught a fish alive.",
        "Six, seven, eight, nine, ten,",
        "Then I let it go again.",
        "Why did you let it go?",
        "Because it bit my finger so.",
        "Which finger did it bite?",
        "This little finger on my right.",
    ]),
    "Grand Old Duke of York": _rhyme("1F482", [
        "Oh, the grand old Duke of York,",
        "He had ten thousand men;",
        "He marched them up to the top of the hill,",
        "And he marched them down again.",
        "And when they were up, they were up,",
        "And when they were down, they were down,",
        "And when they were only halfway up,",
        "They were neither up nor down.",
    ]),
    "Pease Porridge Hot": _rhyme("1F372", [
        "Pease porridge hot, pease porridge cold,",
        "Pease porridge in the pot, nine days old.",
        "Some like it hot, some like it cold,",
        "Some like it in the pot, nine days old.",
    ]),
    "Wee Willie Winkie": _rhyme("1F319", [
        "Wee Willie Winkie runs through the town,",
        "Upstairs and downstairs in his nightgown,",
        "Tapping at the window, crying through the lock,",
        "Are the children in their beds? It's past eight o'clock!",
    ]),
    "Jack Be Nimble": _rhyme("1F56F", [
        "Jack be nimble,",
        "Jack be quick,",
        "Jack jump over",
        "The candlestick.",
    ]),
    "Hickety Pickety": _rhyme("1F414", [
        "Hickety, pickety, my black hen,",
        "She lays eggs for gentlemen;",
        "Sometimes nine, and sometimes ten,",
        "Hickety, pickety, my black hen!",
    ]),
    "Little Boy Blue": _rhyme("1F4EF", [
        "Little Boy Blue, come blow your horn,",
        "The sheep's in the meadow, the cow's in the corn.",
        "But where is the boy who looks after the sheep?",
        "He's under a haystack, fast asleep.",
    ]),
    "Mary Mary": _rhyme("1F337", [
        "Mary, Mary, quite contrary,",
        "How does your garden grow?",
        "With silver bells and cockle shells,",
        "And pretty maids all in a row.",
    ]),
    "Head Shoulders Knees": _rhyme("1F9CD", [
        "Head, shoulders, knees and toes, knees and toes,",
        "Head, shoulders, knees and toes, knees and toes,",
        "And eyes and ears and mouth and nose,",
        "Head, shoulders, knees and toes, knees and toes!",
    ]),
    "Teddy Bear": _rhyme("1F9F8", [
        "Teddy bear, teddy bear, turn around,",
        "Teddy bear, teddy bear, touch the ground,",
        "Teddy bear, teddy bear, show your shoe,",
        "Teddy bear, teddy bear, that will do!",
        "Teddy bear, teddy bear, go upstairs,",
        "Teddy bear, teddy bear, say your prayers,",
        "Teddy bear, teddy bear, turn out the light,",
        "Teddy bear, teddy bear, say good night!",
    ]),
    "Five Little Ducks": _rhyme("1F986", [
        "Five little ducks went out one day,",
        "Over the hill and far away.",
        "Mother duck said, Quack, quack, quack, quack!",
        "And all the five little ducks came back.",
    ]),
    "Bingo": _rhyme("1F415", [
        "There was a farmer had a dog,",
        "And Bingo was his name-o.",
        "B, I, N, G, O! B, I, N, G, O! B, I, N, G, O!",
        "And Bingo was his name-o!",
    ]),
    "London Bridge": _rhyme("1F309", [
        "London Bridge is falling down,",
        "Falling down, falling down.",
        "London Bridge is falling down,",
        "My fair lady.",
        "Build it up with iron bars,",
        "Iron bars, iron bars.",
        "Build it up with iron bars,",
        "My fair lady.",
    ]),
    "Ring a Ring o' Roses": _rhyme("1F339", [
        "Ring-a-ring o' roses,",
        "A pocket full of posies,",
        "A-tishoo! A-tishoo!",
        "We all fall down.",
    ]),
    "Mulberry Bush": _rhyme("1F333", [
        "Here we go round the mulberry bush,",
        "The mulberry bush, the mulberry bush.",
        "Here we go round the mulberry bush,",
        "On a cold and frosty morning.",
        "This is the way we wash our hands,",
        "Wash our hands, wash our hands.",
        "This is the way we wash our hands,",
        "On a cold and frosty morning.",
    ]),
    "Old Mother Hubbard": _rhyme("1F9B4", [
        "Old Mother Hubbard went to the cupboard",
        "To give her poor dog a bone;",
        "But when she got there, the cupboard was bare,",
        "And so the poor dog had none.",
    ]),
    "Star Light Star Bright": _rhyme("1F320", [
        "Star light, star bright,",
        "First star I see tonight,",
        "I wish I may, I wish I might,",
        "Have the wish I wish tonight.",
    ]),
    "The Muffin Man": _rhyme("1F9C1", [
        "Oh, do you know the muffin man,",
        "The muffin man, the muffin man?",
        "Oh, do you know the muffin man,",
        "Who lives on Drury Lane?",
        "Oh, yes, I know the muffin man,",
        "The muffin man, the muffin man.",
        "Oh, yes, I know the muffin man,",
        "Who lives on Drury Lane.",
    ]),
    "Roses Are Red": _rhyme("1F490", [
        "Roses are red,",
        "Violets are blue,",
        "Sugar is sweet,",
        "And so are you!",
    ]),
    "Farmer in the Dell": _rhyme("1F9D1-200D-1F33E", [
        "The farmer in the dell,",
        "The farmer in the dell,",
        "Hi-ho, the derry-o,",
        "The farmer in the dell.",
        "The farmer takes a cow,",
        "The farmer takes a cow,",
        "Hi-ho, the derry-o,",
        "The farmer takes a cow.",
    ]),
    "A Was an Apple Pie": _rhyme("1F967", [
        "A was an apple pie,",
        "B bit it, C cut it,",
        "D dealt it, E ate it,",
        "F fought for it, G got it,",
        "H had it, I inspected it,",
        "J jumped for it, K kept it,",
        "L longed for it, M mourned for it,",
        "N nodded at it, O opened it,",
        "P peeped in it, Q quartered it,",
        "R ran for it, S sang for it,",
        "T took it, U upset it,",
        "V viewed it, W wanted it,",
        "X, Y, Z and ampersand",
        "All wished for a piece in hand!",
    ]),
}

# Hindi and Bengali traditional rhymes: shown in their own script (drawn as
# pictures by tools/add_items.py), sung with a Hindi or Bengali voice when the
# device has one, else read from the English-letter lines.
DESI_RHYMES = {
    "Machli Jal Ki Rani": _rhyme("1F41F", [
        "Machli jal ki rani hai,",
        "Jeevan uska paani hai.",
        "Haath lagao, dar jaayegi,",
        "Bahar nikalo, mar jaayegi.",
    ], hi="मछली जल की रानी", bn="মাছ জলের রানি", lang="hi", native=[
        "मछली जल की रानी है,",
        "जीवन उसका पानी है।",
        "हाथ लगाओ, डर जाएगी,",
        "बाहर निकालो, मर जाएगी।",
    ]),
    "Aloo Kachaloo": _rhyme("1F954", [
        "Aloo kachaloo beta kahan gaye the?",
        "Baingan ki tokri mein so rahe the.",
        "Baingan ne laat maari, ro rahe the,",
        "Mummy ne pyaar kiya, hans rahe the.",
    ], hi="आलू-कचालू", bn="আলু-কচালু", lang="hi", native=[
        "आलू-कचालू बेटा कहाँ गए थे?",
        "बैंगन की टोकरी में सो रहे थे।",
        "बैंगन ने लात मारी, रो रहे थे,",
        "मम्मी ने प्यार किया, हँस रहे थे।",
    ]),
    "Ay Ay Chand Mama": _rhyme("1F315", [
        "Ay ay chand mama, tip diye ja,",
        "Chander kopale chand, tip diye ja.",
        "Dhan bhanle kuro debo,",
        "Maach katle muro debo,",
        "Kalo gaiyer dudh debo,",
        "Dudh khabar bati debo,",
        "Chander kopale chand, tip diye ja.",
    ], hi="आ आ चाँद मामा", bn="আয় আয় চাঁদ মামা", lang="bn", native=[
        "আয় আয় চাঁদ মামা, টিপ দিয়ে যা,",
        "চাঁদের কপালে চাঁদ, টিপ দিয়ে যা।",
        "ধান ভানলে কুঁড়ো দেব,",
        "মাছ কাটলে মুড়ো দেব,",
        "কালো গাইয়ের দুধ দেব,",
        "দুধ খাবার বাটি দেব,",
        "চাঁদের কপালে চাঁদ, টিপ দিয়ে যা।",
    ]),
}

RHYMES_AND_SCHOOL_HUB = {
    "Classic Rhymes": CLASSIC_RHYMES,
    "Desi Rhymes": DESI_RHYMES,
    "NCERT Class 1-5": {
        "Solar System": {
            "desc": "Learn the planets around our Sun in order!",
            "hi": "सौर मंडल",
            "bn": "सौर জগৎ",
            "closed": False,
            "video": {
                "url": "https://www.youtube.com/watch?v=libKVRa01L8",
                "title": "Solar System for Kids",
                "places": False
            }
        },
        "Parts of Plants": {
            "desc": "Roots, stem, leaves, flowers, and fruits.",
            "hi": "पौधों के भाग",
            "bn": "উদ্ভিদের অংশ",
            "closed": True,
            "video": {
                "url": "https://www.youtube.com/watch?v=X6Tshk_ECv4",
                "title": "Parts of a Plant",
                "places": False
            }
        }
    }
}


def rhyme(cat, name):
  """The rhyme's data (lines, native lines, lang) or None."""
  if cat in ("Classic Rhymes", "Desi Rhymes"):
    return RHYMES_AND_SCHOOL_HUB[cat].get(name)
  return None
