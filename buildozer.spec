[app]

# Name shown under the app icon
title = Domino Wonder Dash
package.name = dominowonderdash
package.domain = org.saiqul

source.dir = .
source.include_exts = py,png,json,ogg,ttf
source.exclude_dirs = build, bin, .buildozer, __pycache__, tools

version = 1.0

# pygame runs on the SDL2 bootstrap; pyjnius gives access to Android's
# built-in text-to-speech voice (used to say the names out loud).
requirements = python3,pygame,pyjnius
p4a.bootstrap = sdl2

# Portrait 9:16 phone layout, full screen
orientation = portrait
fullscreen = 1

# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.permissions =
android.extra_manifest_xml = ./android_queries.xml

[buildozer]
log_level = 2
warn_on_root = 1
