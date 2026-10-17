# Domino Wonder Dash: testing and mobile builds

## 1. Play and test on Windows

```
cd C:\Users\saiqu\DominoGame
python main.py
```

- The window opens in portrait 9:16. Drag the edge to resize it; the game scales to fit.
- **How a child plays:** pick a subject (top row), a category (second row) and an item
  (picture buttons; "More >" shows the next page). Trace the dotted outline over the faint
  picture. Each dot pops, and the notes rise as you go. When the outline is covered,
  dominoes stand up on it. Tap and they topple, then the real picture appears in full colour.
  Tap to play again, or press **Next >** to go to the next item.
- **Voice:** the name is spoken and spelled when you pick an item ("Cat. C, A, T. Cat!").
  The letter tiles light up one by one as each letter is said. Letters say "A for Apple",
  numbers say "Three". Tap the name banner or the speaker button to hear it again.
- **Sounds:** click (item), two-note blip (category), pops while tracing, pencil ticks in
  free drawing, a wooden knock when you tap, a rising clack-clack as the dominoes fall,
  and a chime at the end.
- **Hindi (वर्णमाला):** choose **Hindi**, then **Swar** (13 vowels) or **Vyanjan** (36 consonants).
  Each letter is said with its word ("क से कबूतर"). To hear real Hindi on Windows, add the Hindi
  voice once: **Settings > Time & language > Speech > Manage voices > Add voices > Hindi (India)**,
  then restart the game. Until then it says the English letters ("ka se kabootar, pigeon").
  Chrome and Android phones usually have a Hindi voice already.
- Esc closes the game. If a computer has no sound device, the game still runs silently.

## Adding or changing items (the Picture Data Hub)

Every subject, category and item is listed in `domino_data.py` (`SUBJECTS` and `CATALOG`).
To add one, add a line such as `("Zebra", "A zebra has black and white stripes.",
("emoji", "1F993"))`. The code is the OpenMoji hexcode from https://openmoji.org. Then run:

```
python tools\build_hub.py
```

This writes the outlines to `hub_data.json` and the pictures to `pics\`. It needs internet
the first time (downloads are cached in `%LOCALAPPDATA%\DominoWonderDash\downloads`).
It needs `pip install pillow numpy opencv-python-headless`, and those are needed only for building, not for playing.

## One click: `build_mobile.ps1`

```
cd C:\Users\saiqu\DominoGame
.\build_mobile.ps1            # web game + installable app into docs\, then a local test server
.\build_mobile.ps1 -Android   # also the Android .apk into bin\ (WSL Ubuntu)
.\build_mobile.ps1 -NoServe   # build only
```

If Windows refuses to run scripts: `powershell -ExecutionPolicy Bypass -File .\build_mobile.ps1`.
It picks a free port (8000, 8001, ...) and prints the address to open on a phone on the same Wi-Fi.

## 2. Play in a phone or desktop browser, and install it like an app (PWA)

`python tools\build_web.py` builds the browser version into `docs\` (GitHub Pages):
only the game files go in (never `venv\`, `tools\` or `docs\` itself). It also adds:

- `manifest.json` + app icons (`icons\`, painted by `tools\make_icons.py`): phones offer
  **Install app** / **Add to Home Screen**; it opens full screen, upright, with its own icon.
- `sw.js`: keeps the game and the Python engine on the phone, so it opens again without
  internet (videos still need internet).

Open https://saiqulmodi.github.io/DominoGame/ on the phone, tap the page when it says
"Ready to start", then use the browser menu > **Install app** (Android Chrome) or
Share > **Add to Home Screen** (iPhone Safari). Installing and offline play need https, so a
local `http://192.168.x.x:8000` test plays fine but does not install.

## 3. Android app (.apk) with Buildozer

Buildozer runs only on Linux, so it runs in WSL Ubuntu (already set up on this laptop).
`tools/build_android.sh` copies the game files to `~/DominoGame` on the Linux disk (much faster
than `/mnt/c`), builds with buildozer in its own Python 3.11 (`~/dwd-buildenv`; Ubuntu's own
Python is too new and blocks pip), and copies the .apk back to `bin\`:

```
wsl -e bash -l tools/build_android.sh       # or .\build_mobile.ps1 -Android
```

New machine: `wsl --install -d Ubuntu`, then inside Ubuntu
`sudo apt install -y git zip unzip openjdk-17-jdk autoconf automake libtool pkg-config zlib1g-dev
libncurses-dev cmake libffi-dev libssl-dev build-essential rsync`. The script installs the rest.
The first build downloads the Android SDK/NDK and takes 20-40 minutes.

Copy `bin\dominowonderdash-*.apk` to the phone and install it (allow "install unknown apps").
`buildozer.spec` sets portrait, full screen, the app icon and start-up picture (`icons\`),
keeps the screen on while a child plays, and asks for no permissions. `pyjnius` gives the
phone's text-to-speech voice; `android_queries.xml` declares that service (Android 11+).
Real-life videos open the game's own player page (`docs/play.html`, written by
`tools/build_web.py`) in Chrome; the phone's Back button returns to the game. In the game,
the phone's Back button closes the game.

Fixes the Android build needs (already in place):
- `p4a-recipes/pygame`: pygame 2.6.1 with its C code made by Cython 3.1 (`~/dwd-cython`),
  plus the SIMD blitter files added to the surface module (without them 64-bit phones
  closed at once: "cannot locate symbol alphablit_alpha_sse2_argb_surf_alpha").
- Speech: Android's `speak()` needs the text as a Java CharSequence and a Bundle (`audio.py`).
- Names are typed with the game's own big letters; the phone keyboard is not opened.

### Test on a real phone over USB (adb)

1. On the phone: Settings > About phone > Software information > tap **Build number** 7
   times; Settings > **Developer options** > **USB debugging** on; plug in the cable and
   tap **Allow**.
2. Install and start: `adb install -r bin\dominowonderdash-1.1-...-debug.apk` and
   `adb shell am start -n org.saiqul.dominowonderdash/org.kivy.android.PythonActivity`.
3. The game's messages and any error: `adb logcat -d | findstr python`.
   (adb comes with Google's platform-tools. If `adb devices` is empty, run
   `adb kill-server`, unplug and replug, and allow the phone again.)

iOS: pygame cannot be packaged as a native iOS app with these tools. On iPhone/iPad, use the
web version (section 2) and **Add to Home Screen**.

## How children learn to play (no reading needed)

- **Picture guides** (`howto.py`): the first time a child traces, plays Find it!, Spell it or
  Draw my own, a short guide opens: a moving hand shows each step on a real picture, and one
  short line is said aloud in the child's language (English, Hindi, Bengali). Big Back /
  Hear / Next buttons. The purple **?** button (under Next) and Games > **How to play** open it again.
- **Helping hand**: if a child stops tracing for 6 seconds, a hand slides over the next dots
  (and new players hear "Put your finger on the dots and slide!"); standing dominoes get a
  tapping hand; an empty drawing page gets a drawing hand.
- **Wonder Town** says its welcome tips aloud, and **Guide me** says each building's name.
- **Rainbow cap**: each subject a child discovers (first picture finished in it) paints the next
  stripe of the hero's cap: violet, indigo, blue, green, yellow, orange, red. The cap shows on the
  hero, in the town's top bar (tap it to hear how many colours), on each player card and in
  the parents' report.
- **Road safety** (`roadsafety.py`, Safety subject, Road Safety Park in Wonder Town, Games >
  Cross the Road): a street in the child's theme with cars, buses and autos, a zebra crossing,
  the cars' traffic light (red STOP, yellow WAIT, green GO) and the walk signal (red man,
  green man, blinking = don't start). The child taps Walk; on the green man the child looks
  right, left and right again (India keeps left) and crosses; on red a car goes beep-beep and
  the voice explains why we wait. Every safe crossing gives a star and a spoken tip (helmet,
  seat belt, footpath, bus stop ...). 13 road signs to trace: `python toolsdd_items.py "Road Safety"`
  builds just that category into the hub.

## Where the game is published

The game is shared on GitHub and Stratos (the Play Store kit in `PLAY_STORE.md` is kept
for later but not used). After every change:

1. `python tools\build_web.py`, then commit and push to both GitHub remotes
   (`dominogame` = github.com/saiqulmodi/DominoGame, `origin` = DominoWonderDash).
   GitHub Pages updates https://saiqulmodi.github.io/DominoGame/ by itself.
2. `python tools\make_stratos_box.py`, then in the stratos-games-site folder commit
   **only** `games/saiqulmodi-domino-wonder-dash`, pull with rebase and push.
   Stratos asks for the box to stay **under 20 MB (20,000,000 bytes)**; the script prints
   MiB, so check the real byte count. The web build keeps it small: only pictures the game
   uses, pictures sized to the 450-wide canvas, 88 px thumbnails, outline points rounded.
3. Build the Android app (`.\build_mobile.ps1 -Android`), attach it to the GitHub release
   **v1.1-test** (the download link stays the same), and install it on a test phone.

**Sharing:** https://saiqulmodi.github.io/DominoGame/share.html has a *Share on WhatsApp*
button with a ready message asking friends what their child liked, what was hard, what did
not work and what to add.
