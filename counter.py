"""Counts how often the game is opened, on GoatCounter (dominogame.goatcounter.com).

The Android app sends one "opened" hit when it starts: the app's version and
the Android version only. No name, profile, progress or device id is sent.
The web pages count themselves with GoatCounter's own script, which
tools/build_web.py adds to the game page (download.html has it by hand).
Offline, or on any error, nothing happens: the game never waits for it.
"""
import random
import threading

from audio import IS_ANDROID

COUNT_URL = "https://dominogame.goatcounter.com/count"
APP_PATH = "/android-app"
APP_VERSION = "1.1"          # same as version in buildozer.spec


def count_open():
  """One anonymous hit for this opening of the Android app (in the background)."""
  if IS_ANDROID:
    threading.Thread(target=_send, daemon=True).start()


def hit_url():
  return (f"{COUNT_URL}?p={APP_PATH}&t=Domino%20Game%20Android%20app"
          f"&rnd={random.randint(1, 10 ** 9)}")


def user_agent(android_release):
  # GoatCounter shows the system from this; a browser-like form keeps it from
  # being taken for a bot (its own script runs in a browser)
  return f"Mozilla/5.0 (Linux; Android {android_release}) DominoGame/{APP_VERSION}"


def _send():
  try:
    from jnius import autoclass     # Android's own web client (system certificates)
    release = autoclass("android.os.Build$VERSION").RELEASE
    conn = autoclass("java.net.URL")(hit_url()).openConnection()
    conn.setConnectTimeout(8000)
    conn.setReadTimeout(8000)
    conn.setRequestProperty("User-Agent", user_agent(release))
    conn.getResponseCode()
    conn.disconnect()
  except Exception:
    pass
  finally:
    try:
      from jnius import detach      # a Java-attached thread must detach before it ends
      detach()
    except Exception:
      pass
