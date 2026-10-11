#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Kilo Code: copy the plugin and skill into a Kilo config folder
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Copy .kilo/plugin/spindoctor-qwerty.js and .kilo/skills/spindoctor-qwerty/ into a Kilo config folder.

  python3 tools/install_kilo.py PROJECT_DIR      # PROJECT_DIR/.kilo/  (this project only)
  python3 tools/install_kilo.py --global         # ~/.config/kilo/    (every project; $XDG_CONFIG_HOME/kilo if set)
  python3 tools/install_kilo.py --uninstall PROJECT_DIR | --global

Only these two entries are written or removed; anything else in the config folder (other plugins, skills, kilo.json) is left
alone. Kilo installs @kilocode/plugin into that folder on its next start. Start a new Kilo session afterwards.
Standard library only (use `py -3` or `python` on Windows).
"""
import os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PLUGIN = os.path.join(ROOT, ".kilo", "plugin", "spindoctor-qwerty.js")
SRC_SKILL = os.path.join(ROOT, ".kilo", "skills", "spindoctor-qwerty")


def target(args):
    if "--global" in args:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
        return os.path.join(base, "kilo")
    rest = [a for a in args if not a.startswith("--")]
    if len(rest) != 1:
        return None
    return os.path.join(os.path.abspath(rest[0]), ".kilo")


def main():
    a = sys.argv[1:]
    dest = target(a)
    if dest is None or "-h" in a or "--help" in a:
        print(__doc__); return 2
    plugin = os.path.join(dest, "plugin", "spindoctor-qwerty.js"); skill = os.path.join(dest, "skills", "spindoctor-qwerty")
    if "--uninstall" in a:
        if os.path.isfile(plugin): os.remove(plugin)
        shutil.rmtree(skill, ignore_errors=True)
        print("removed SpinDoctor Qwerty from", dest); return 0
    if os.path.abspath(dest) == os.path.join(ROOT, ".kilo"):
        print("this repo already is that folder:", dest); return 0
    os.makedirs(os.path.dirname(plugin), exist_ok=True)
    shutil.copyfile(SRC_PLUGIN, plugin)
    shutil.rmtree(skill, ignore_errors=True)
    shutil.copytree(SRC_SKILL, skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("installed SpinDoctor Qwerty 1.1.0 into", dest)
    print("  plugin:", plugin); print("  skill: ", skill)
    print("Start a new Kilo session; the tools are spindoctor_functions, spindoctor_run_script, spindoctor_run_preset, "
          "spindoctor_list_presets, spindoctor_report and spindoctor_test_theory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
