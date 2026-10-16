#!/usr/bin/env python3
"""Breezy Minimal v80: the two small rows in the owner's colour #FFD7EDFF (light blue).

Usage: build_v80_preset.py BASE_v79.kwgt OUT.kwgt

Every text and icon of the middle row (date | wind, rain now, feels like) and of the bottom
row (alarm, sun | today, tomorrow, umbrella) gets COLOR (KWGT #AARRGGBB); they were
#B8FFFFFF (white, 72 %). Clock, temperature and weather icon stay as they are.
"""
import json
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.0 • Manrope"
COLOR = "#FFD7EDFF"
ROWS = ["Date", "Wind + rain now + feels like",
        "Next alarm + next sunset/sunrise", "Today + tomorrow + umbrella"]


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = preset["preset_root"]["viewgroup_items"]

    changed = 0
    for title in ROWS:
        row = next(i for i in walk(items) if i.get("internal_title") == title)
        for item in walk([row]):
            if item["internal_type"] in ("TextModule", "FontIconModule"):
                assert "paint_color" not in item.get("internal_formulas", {}), item["internal_title"]
                item["paint_color"] = COLOR
                changed += 1
    assert changed == 17, changed  # 1 + 5 + 4 + 7 texts and icons

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
