#!/usr/bin/env python3
"""Breezy Minimal v81: the middle row in Manrope SemiBold (owner's choice; v80's colour dropped).

Usage: build_v81_preset.py BASE_v79.kwgt Manrope-SemiBold.ttf OUT.kwgt

Built on v79 (v80's light blue was rolled back). The texts of the middle row (date | wind,
rain now, feels like) use Manrope SemiBold from make_manrope_fonts.py (narrow minus like the
other weights), bundled as fonts/Manrope-SemiBold.ttf. SemiBold is ~3.5 % wider than
Regular, so the row's width estimate (build_v75_preset.py) uses 0.54 em per character.
"""
import json
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.1 • Manrope"
FONT = "fonts/Manrope-SemiBold.ttf"
FAMILY = "kfile://org.kustom.provider/" + FONT
MIDDLE = ["Date", "Wind + rain now + feels like"]
ESTIMATE = ("22 * (0.52 * (", "22 * (0.54 * (")


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, font, target):
    source = zipfile.ZipFile(base)
    assert FONT not in source.namelist()
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = preset["preset_root"]["viewgroup_items"]

    texts = 0
    for title in MIDDLE:
        row = next(i for i in walk(items) if i.get("internal_title") == title)
        for item in walk([row]):
            if item["internal_type"] == "TextModule":
                item["text_family"] = FAMILY
                texts += 1
    assert texts == 4, texts   # date, wind, rain mm, feels like

    estimates = 0
    for item in walk(items):
        for key, value in item.get("internal_formulas", {}).items():
            if ESTIMATE[0] in value:
                item["internal_formulas"][key] = value.replace(*ESTIMATE)
                estimates += 1
    assert estimates, "middle row width estimate not found"

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)
        out.write(font, FONT)


if __name__ == "__main__":
    main(*sys.argv[1:4])
