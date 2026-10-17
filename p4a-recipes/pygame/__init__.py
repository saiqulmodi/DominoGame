"""pygame for the Android app (used via p4a.local_recipes in buildozer.spec).

python-for-android's own recipe is pygame 2.1.0 (2021), whose ready-made C
code does not compile against the Python it now builds for phones (3.14:
"longintrepr.h not found"). pygame 2.6.1 ships no ready-made C, so it is made
here first with a modern Cython (3.1.x: knows Python 3.14; 3.3 rejects pygame 2.6.1) from its own small
environment (~/dwd-cython, set up by tools/build_android.sh). Buildozer itself
needs the old Cython 0.29, which would otherwise be picked up and fail.
"""

import os
import subprocess
from os.path import exists, join

from pythonforandroid.recipes.pygame import Pygame2Recipe
from pythonforandroid.toolchain import current_directory

CYTHON_PY = os.environ.get("DWD_CYTHON_PY",
                           join(os.path.expanduser("~"), "dwd-cython", "bin", "python"))


class Pygame261Recipe(Pygame2Recipe):
  version = "2.6.1"
  url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"

  def prebuild_arch(self, arch):
    super().prebuild_arch(arch)
    with current_directory(self.get_build_dir(arch.arch)):
      if not exists(join("src_c", "_sdl2", "audio.c")):
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
        subprocess.run([CYTHON_PY, "setup.py", "cython_only"], check=True, env=env)


recipe = Pygame261Recipe()
