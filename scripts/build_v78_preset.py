#!/usr/bin/env python3
"""Breezy Minimal v78: only the bottom row moves apart (v77 moved the middle one too).

Usage: build_v78_preset.py BASE_v77.kwgt OUT.kwgt

The middle row has enough room with its small font, so its groups stay at the edges.
"""
import json
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v7.8 • Manrope"
MIDDLE = ["Date", "Wind + rain now + feels like"]


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))

    for title in MIDDLE:
        row = next(i for i in walk(preset["preset_root"]["viewgroup_items"])
                   if i.get("internal_title") == title)
        del row["internal_toggles"]["position_offset_x"]
        del row["internal_formulas"]["position_offset_x"]

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
