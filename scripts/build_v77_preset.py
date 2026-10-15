#!/usr/bin/env python3
"""Breezy Minimal v77: crowded rows move apart.

Usage: build_v77_preset.py BASE_v76.kwgt OUT.kwgt

When the middle or bottom row switches to its small font (long values or the "maximal"
switch, see build_v75_preset.py), its left group moves SPREAD units to the left and its
right group SPREAD units to the right, so the two halves do not touch.
"""
import json
import re
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v7.7 • Manrope"
SPREAD = 8
ROWS = ["Date", "Next alarm + next sunset/sunrise",
        "Wind + rain now + feels like", "Today + tomorrow + umbrella"]
# The y formula ends with "..., <y small>, <y big>)$"; x uses the same condition.
CHOICE = re.compile(r", -?[\d.]+, -?[\d.]+\)\$$")


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))

    for title in ROWS:
        row = next(i for i in walk(preset["preset_root"]["viewgroup_items"])
                   if i.get("internal_title") == title)
        x = int(row.get("position_offset_x", 0))
        y_formula = row["internal_formulas"]["position_offset_y"]
        assert CHOICE.search(y_formula), title
        # TOPLEFT counts x from the left edge, TOPRIGHT from the right one: less = outwards.
        row["internal_toggles"]["position_offset_x"] = 10
        row["internal_formulas"]["position_offset_x"] = CHOICE.sub(
            ", %d, %d)$" % (x - SPREAD, x), y_formula)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
