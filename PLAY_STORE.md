# Domino Wonder Dash on Google Play: everything ready to paste

## What to upload

| Play Console asks for | File / link |
|---|---|
| App bundle | `bin\dominowonderdash-1.1-....aab` (signed release, Android 7.0+, targets Android 16 / API 36) |
| App icon 512 x 512 | `store\icon_512.png` |
| Feature graphic 1024 x 500 | `store\feature_graphic.png` |
| Phone screenshots (2-8) | `store\1_town.png` ... `store\7_quiz.png` (1080 x 1920) |
| Privacy policy | https://saiqulmodi.github.io/DominoGame/privacy.html |

Remake them after changes: `.\build_mobile.ps1 -Release` (bundle) and `python tools\store_shots.py` (graphics).

**Upload key:** `C:\Users\saiqu\DominoWonderDash-signing\` (`upload-keystore.jks` + `passwords.txt`).
Copy that folder to a USB stick and to Google Drive today. Every update must be signed with it.
Keep **Play App Signing** switched on (the default): Google keeps the real signing key, and if
the upload key is ever lost, Play support can reset it.

**Every update:** raise `android.numeric_version` in `buildozer.spec` by 1 (101 -> 102) and
`version` (1.1 -> 1.2), then build again.

## Step by step

1. https://play.google.com/console : create a developer account (one-time US$25, identity check).
2. **Create app**: name *Domino Wonder Dash*, default language English (India), **Game**, **Free**.
3. **Testing first**: new personal developer accounts must run a **closed test with at least 12
   testers for 14 days** before production is unlocked. Make a closed testing track, upload the
   .aab, add 12+ Gmail addresses (family, teachers, friends), and ask them to keep it installed
   and play now and then.
4. Fill in **App content** (answers below), the **store listing** (text below), then **Production
   > Create release** with the same .aab and send for review (usually 1-7 days; apps for children
   are reviewed more carefully).

## Store listing

**App name** (max 30): `Domino Wonder Dash`

**Short description** (max 80):
`Trace, topple and learn: ABC, Hindi, maths, India map and road safety for kids`

**Full description**:

```
Learn while you play! Domino Wonder Dash turns learning into a game for children from Class 1 to Class 7.

TRACE, TOPPLE, LEARN
Trace the dotted outline of a real picture with your finger. Dominoes stand up on your line, you tap, they topple, and the real picture appears. The name is spoken, spelled letter by letter and shown in English with Hindi or Bengali.

500+ PICTURES ACROSS EVERY SUBJECT
- English: ABC and abc with A for Apple
- Hindi: Swar and Vyanjan with real Hindi voice
- Maths: numbers, shapes, signs, angles and solids
- India: the India map, all 28 states and 8 union territories with capitals, monuments
- Nature, food, home, travel, the world, sky and space
- Science and Social Studies for Class 6 and 7 (NCERT aligned)

ROAD SAFETY
Cross the Road: wait for the green man, look right, look left, look right again, and walk over the zebra crossing. Learn traffic lights (red STOP, yellow WAIT, green GO), road signs, helmets and seat belts by playing.

EASY FOR LITTLE ONES
Moving picture guides show how to play, and every instruction is spoken aloud, so even children who cannot read yet can play on their own. A helping hand appears if a child gets stuck.

WONDER TOWN
Walk, swing and fly through a 3D town where every building is a subject. Earn stickers, and paint your rainbow cap with a new colour for every subject you discover.

MORE WAYS TO PLAY
Find it! quiz, Spell it, Draw my own (your drawing becomes dominoes), a story every day, up to 6 players on one device, and a report for parents.

SAFE FOR CHILDREN
No ads. No in-app purchases. No accounts. No data collected. Works offline.
```

**Hindi listing** (add translation > Hindi):
- Short: `चित्र बनाओ, डोमिनो गिराओ, सीखो: ABC, हिंदी, गणित, भारत का नक्शा, सड़क सुरक्षा`
- Full: start with `खेल-खेल में सीखो! कक्षा 1 से 7 के बच्चों के लिए।` then the English text, or translate it in the console.

**Category**: Game > Educational. **Tags**: Educational, Kids, Puzzle, Casual.
**Contact email**: your developer email (required, shown publicly). **Website**: https://saiqulmodi.github.io/DominoGame/

## App content answers

| Section | Answer |
|---|---|
| Privacy policy | https://saiqulmodi.github.io/DominoGame/privacy.html |
| Ads | **No**, the app contains no ads |
| App access | All functionality is available without special access (no login) |
| Content rating | Category **Game** (or Reference/Education); answer **No** to violence, fear, sex, language, drugs, gambling, user interaction, sharing location, buying digital goods. Expected rating: 3+ / Everyone |
| Target audience | Ages **6-8** and **9-12** (add **5 and under** if you want the youngest too). This puts the app under the **Families Policy**, which it meets: no ads, no data collection, no accounts |
| Appeal to children | Yes |
| Data safety | **Does your app collect or share any of the required user data types? No.** (Progress and the typed player name stay on the device and are never sent anywhere, so under Play's rules they are not "collected".) Encryption in transit: not applicable. Data deletion: not applicable |
| Government / financial / health / news app | No |
| Permissions | None requested |

**Teacher Approved**: once live, the app can be considered for Google Play's Teacher Approved
badge (it is automatic for eligible Families apps; nothing to apply for).

## Good to know

- The **"Watch the real one"** video button opens the phone's web browser (Wikimedia Commons or
  our GitHub Pages videos, all checked by hand). Play allows this, but some reviewers prefer a
  **grown-up gate** (for example "ask a grown-up: hold the button for 3 seconds") before a
  child leaves the app. It can be added if review asks.
- Testers get the app from a Play link; nobody needs the .apk for that. The debug .apk
  (`build_mobile.ps1 -Android`) is only for quick tests on your own phone (allow "install
  unknown apps").
- Other Android stores accept the same app: Samsung Galaxy Store, Amazon Appstore and India's
  Indus Appstore (they usually want an .apk: build one with the same key if needed).
