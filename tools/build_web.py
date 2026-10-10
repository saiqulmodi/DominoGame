"""Builds the browser version into docs/ (GitHub Pages) with pygbag.

pygbag packs every file in the folder it is given, so the game files are
copied into a clean staging folder first (no docs/, tools/, build/ ...).

Run:  python tools/build_web.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_FILES = ["main.py", "audio.py", "domino_data.py", "fun.py", "calls.py", "modes.py",
              "screens.py", "stories.py", "translations.py", "hub_data.json"]
GAME_DIRS = ["pics", "sounds", "fonts"]
APP = "dominowonderdash"


def main():
  stage_root = tempfile.mkdtemp(prefix="dwd_web_")
  stage = os.path.join(stage_root, APP)
  os.makedirs(stage)
  for f in GAME_FILES:
    shutil.copy2(os.path.join(ROOT, f), stage)
  for d in GAME_DIRS:
    shutil.copytree(os.path.join(ROOT, d), os.path.join(stage, d))
  for f in GAME_FILES:
    if f.endswith(".py"):
      subprocess.run([sys.executable, "-m", "py_compile", os.path.join(stage, f)], check=True)
  subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", "Domino Wonder Dash",
                  stage], check=True)
  docs = os.path.join(ROOT, "docs")
  os.makedirs(docs, exist_ok=True)
  for name in os.listdir(os.path.join(stage, "build", "web")):
    shutil.copy2(os.path.join(stage, "build", "web", name), docs)
  open(os.path.join(docs, ".nojekyll"), "w").close()
  shutil.rmtree(stage_root, ignore_errors=True)
  for name in sorted(os.listdir(docs)):
    print(f"{name:28s} {os.path.getsize(os.path.join(docs, name)) / 1e6:6.2f} MB")


if __name__ == "__main__":
  main()
