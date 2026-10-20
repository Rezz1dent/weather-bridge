#!/usr/bin/env python3
"""Breezy Minimal: the bottom row no longer moves apart when crowded.

Usage: build_v110_nospread.py IN.kwgt OUT.kwgt TITLE

Since v7.8 a crowded bottom row moved 8 units outwards on both sides (the left and right
halves were placed independently and could collide). In the row layout of v10.x that made
the crowded row stick out past the rows above, and with the second size step (16) there is
room in the middle anyway. The edge padding stays 8; the second step starts a little
earlier (estimate > 560 instead of 580) because the row is now 16 units narrower.
"""
import json
import sys
import time
import uuid
import zipfile

ROW = ["Next alarm + next sunset/sunrise", "Today + tomorrow + umbrella"]


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    for item in walk(preset["preset_root"]["viewgroup_items"]):
        if item.get("internal_title") in ROW:
            for key in ("position_padding_left", "position_padding_right"):
                if key in item.get("internal_formulas", {}):
                    del item["internal_formulas"][key]
                    item["internal_toggles"].pop(key, None)
                    item[key] = 8.0
                    print(item["internal_title"], key, "-> 8")
        for key, value in item.get("internal_formulas", {}).items():
            item["internal_formulas"][key] = value.replace(") > 580))", ") > 560))")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
