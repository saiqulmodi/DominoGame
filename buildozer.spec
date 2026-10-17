[app]

# Name shown under the app icon
title = Domino Wonder Dash
package.name = dominowonderdash
package.domain = org.saiqul

source.dir = .
source.include_exts = py,png,json,ogg,ttf
# venv/ and docs/ (the web build and its videos) must never go into the app
source.exclude_dirs = build, bin, .buildozer, __pycache__, tools, venv, docs, icons, .git
source.exclude_patterns = buildozer.spec*, source.include_exts

version = 1.1

# pygame runs on the SDL2 bootstrap; pyjnius gives access to Android's
# built-in text-to-speech voice (used to say the names out loud).
requirements = python3,pygame,pyjnius
p4a.bootstrap = sdl2

# Portrait 9:16 phone layout, full screen
orientation = portrait
fullscreen = 1

# App icon and the picture shown while the game starts (python tools/make_icons.py)
icon.filename = %(source.dir)s/icons/icon-512.png
presplash.filename = %(source.dir)s/icons/presplash.png
android.presplash_color = #4A90E2

android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
# keeps the screen on while a child is tracing
android.wakelock = True
# no permissions: real-life videos open in the phone's own browser
android.permissions =
android.extra_manifest_xml = ./android_queries.xml

[buildozer]
log_level = 2
warn_on_root = 1
