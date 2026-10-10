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

## 2. Play in a phone or desktop browser (pygbag)

```
python -m pip install pygbag
cd C:\Users\saiqu
python -m pygbag DominoGame
```

Open http://localhost:8000. The first load downloads the Python runtime, so it takes about 30 seconds.
Then **tap the page** when it says "Ready to start". Browsers allow sound only after a real tap.
If port 8000 is busy, add `--port 8765`.

To get files you can put online (itch.io, GitHub Pages and so on):

```
python -m pygbag --build DominoGame
```

The upload folder is `DominoGame\build\web` (index.html + dominogame.apk). Phones then open it
by URL. Names are spoken by the browser's own voice (speechSynthesis).

## 3. Android app (.apk) with Buildozer

Buildozer runs only on Linux. On Windows, use WSL (Ubuntu):

```
wsl --install -d Ubuntu          # once, then restart Windows
```

Inside Ubuntu:

```
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
pip3 install --user buildozer cython
cp -r /mnt/c/Users/saiqu/DominoGame ~/DominoGame
cd ~/DominoGame
~/.local/bin/buildozer android debug
```

The first build downloads the Android SDK/NDK and takes 20-40 minutes. The app appears in `bin/`
as `dominowonderdash-1.0-arm64-v8a_armeabi-v7a-debug.apk`. Copy it to the phone and install it
(allow "install unknown apps").

`buildozer.spec` already sets portrait, fullscreen, pygame on the SDL2 bootstrap, and
`pyjnius` for the phone's built-in text-to-speech voice. `android_queries.xml` declares the TTS
service, which Android 11+ requires. The phone's Back button closes the game.

iOS: pygame cannot be packaged as a native iOS app with these tools. On iPhone/iPad, use the
pygbag web version (section 2) in Safari, then use "Add to Home Screen" for an app-like icon.
