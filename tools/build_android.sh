#!/usr/bin/env bash
# Builds the Android app inside WSL Ubuntu and copies it to bin\ on Windows.
#   wsl -e bash -l tools/build_android.sh           test app (.apk) to install on a phone
#   wsl -e bash -l tools/build_android.sh release   signed Play Store bundle (.aab)
# (build_mobile.ps1 -Android / -Release do this for you.)
#
# Buildozer is slow and fragile on the Windows drive (/mnt/c), so the game
# files are copied to ~/DominoGame (Linux disk) first and built there.
#
# The Play Store upload key lives OUTSIDE the project, on the Windows side:
#   C:\Users\saiqu\DominoWonderDash-signing\upload-keystore.jks + passwords.txt
# It is made once, with a random password, by the first release build.
# Back it up: every Play Store update must be signed with the same key.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$HOME/DominoGame"
ENV="$HOME/dwd-buildenv"
KEYDIR="/mnt/c/Users/saiqu/DominoWonderDash-signing"
MODE="${1:-debug}"
export PATH="$HOME/.local/bin:$PATH"
# Java on WSL can hang trying IPv6 first (Gradle download timed out); use IPv4
export JAVA_TOOL_OPTIONS="-Djava.net.preferIPv4Stack=true"

# Buildozer runs in its own Python 3.11 (Ubuntu's Python is too new for the
# Android tools and blocks pip installs outside a virtual environment)
if [ ! -x "$ENV/bin/buildozer" ]; then
  echo "=== setting up the build tools (once)"
  command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
  uv python install 3.11
  uv venv -p 3.11 --seed "$ENV"
  "$ENV/bin/pip" install -q "cython==0.29.37" buildozer setuptools wheel
fi
# a modern Cython for pygame's C code (p4a-recipes/pygame), kept apart from
# the old Cython 0.29 that buildozer needs
if [ ! -x "$HOME/dwd-cython/bin/cython" ]; then
  uv venv -p 3.11 --seed "$HOME/dwd-cython"
  "$HOME/dwd-cython/bin/pip" install -q "cython>=3.1,<3.2" setuptools
fi
. "$ENV/bin/activate"

echo "=== copying game files to $WORK"
mkdir -p "$WORK"
rsync -a --delete \
  --exclude .git --exclude venv --exclude docs --exclude build --exclude bin \
  --exclude .buildozer --exclude __pycache__ --exclude 'buildozer.spec.save*' \
  "$SRC/" "$WORK/"

cd "$WORK"
# "< <(yes)" answers yes to licence questions and keeps buildozer's own exit
# code ("yes | buildozer" ends in a harmless SIGPIPE that pipefail calls a failure)
if [ "$MODE" = "release" ]; then
  KEY="$KEYDIR/upload-keystore.jks"
  if [ ! -f "$KEY" ]; then
    echo "=== making the Play Store upload key (once): $KEY"
    mkdir -p "$KEYDIR"
    PASS="$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | cut -c1-24)"
    keytool -genkeypair -keystore "$KEY" -storetype PKCS12 -alias upload -keyalg RSA \
      -keysize 4096 -validity 10000 -storepass "$PASS" -keypass "$PASS" \
      -dname "CN=Saiqul Modi, O=Domino Wonder Dash, C=IN"
    {
      echo "Domino Wonder Dash - Google Play upload key"
      echo "keystore file: upload-keystore.jks"
      echo "key alias: upload"
      echo "password: $PASS"
      echo
      echo "KEEP THIS FOLDER SAFE AND BACKED UP (USB stick + Google Drive)."
      echo "Every Play Store update must be signed with this same key."
      echo "Never put it in git or share it."
    } > "$KEYDIR/passwords.txt"
  fi
  PASS="$(grep '^password: ' "$KEYDIR/passwords.txt" | cut -d' ' -f2)"
  export P4A_RELEASE_KEYSTORE="$KEY" P4A_RELEASE_KEYALIAS=upload
  export P4A_RELEASE_KEYSTORE_PASSWD="$PASS" P4A_RELEASE_KEYALIAS_PASSWD="$PASS"
  echo "=== buildozer android release (signed .aab for the Play Store)"
  buildozer android release < <(yes)
  OUT="$(ls -t bin/*.aab | head -1)"
else
  echo "=== buildozer android debug (the first build takes 20-40 minutes)"
  buildozer android debug < <(yes)
  OUT="$(ls -t bin/*.apk | head -1)"
fi

mkdir -p "$SRC/bin"
cp "$OUT" "$SRC/bin/"
echo "=== ready: $SRC/bin/$(basename "$OUT")"
