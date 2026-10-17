#!/usr/bin/env bash
# Builds the Android app (.apk) inside WSL Ubuntu and copies it to bin\ on Windows.
#
# Buildozer is slow and fragile on the Windows drive (/mnt/c), so the game
# files are copied to ~/DominoGame (Linux disk) first and built there.
# Run from Windows:  wsl -e bash -l tools/build_android.sh
# (build_mobile.ps1 -Android does this for you.)
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$HOME/DominoGame"
ENV="$HOME/dwd-buildenv"
export PATH="$HOME/.local/bin:$PATH"

# Buildozer runs in its own Python 3.11 (Ubuntu's Python is too new for the
# Android tools and blocks pip installs outside a virtual environment)
if [ ! -x "$ENV/bin/buildozer" ]; then
  echo "=== setting up the build tools (once)"
  command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
  uv python install 3.11
  uv venv -p 3.11 --seed "$ENV"
  "$ENV/bin/pip" install -q "cython==0.29.37" buildozer setuptools wheel
fi
. "$ENV/bin/activate"

echo "=== copying game files to $WORK"
mkdir -p "$WORK"
rsync -a --delete \
  --exclude .git --exclude venv --exclude docs --exclude build --exclude bin \
  --exclude .buildozer --exclude __pycache__ --exclude 'buildozer.spec.save*' \
  "$SRC/" "$WORK/"

cd "$WORK"
echo "=== buildozer android debug (the first build takes 20-40 minutes)"
yes | buildozer android debug

APK="$(ls -t bin/*.apk | head -1)"
mkdir -p "$SRC/bin"
cp "$APK" "$SRC/bin/"
echo "=== APK ready: $SRC/bin/$(basename "$APK")"
