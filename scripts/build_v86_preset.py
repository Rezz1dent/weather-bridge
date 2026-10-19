#!/usr/bin/env python3
"""Breezy Minimal v86: clock with proportional digits, minutes right after the hours.

Usage: build_v86_preset.py BASE_v85.kwgt FONT_DIR OUT.kwgt
       FONT_DIR = output of make_manrope_fonts.py (Manrope-Bold.ttf, Manrope-Light.ttf)

Until v85 the clock used tabular digits (every digit as wide as "0") and the minutes stood
at a fixed x, so "11" had more air than "88". Now hours and minutes use Manrope's normal
(proportional) digits and sit in a horizontal stack at the old place: the clock gets
narrower or wider with the time, nothing else is tied to its right edge (the weather is
anchored to the widget's right side). The gap between hours and minutes is the global
clock_gap (number, may be negative: the text frames include some room for the shadow).
"""
import json
import os
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.6 • Manrope"
PREFIX = "kfile://org.kustom.provider/fonts/"
FONTS = {"Clock • hours": ("Manrope-Bold-Tnum.ttf", "Manrope-Bold.ttf"),
         "Clock • minutes": ("Manrope-Light-Tnum.ttf", "Manrope-Light.ttf")}
GAP = -4.0
POSITION = ("position_anchor", "position_offset_x", "position_offset_y")


def main(base, font_dir, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    root = preset["preset_root"]
    items = root["viewgroup_items"]
    hours = next(i for i in items if i.get("internal_title") == "Clock • hours")
    minutes = next(i for i in items if i.get("internal_title") == "Clock • minutes")
    assert hours["position_offset_y"] == minutes["position_offset_y"]

    stack = {"internal_type": "StackLayerModule", "internal_title": "Clock",
             "config_stacking": "HORIZONTAL_CENTER", "config_margin": GAP,
             "position_anchor": hours["position_anchor"],
             "position_offset_x": hours["position_offset_x"],
             "position_offset_y": hours["position_offset_y"],
             "internal_toggles": {"config_margin": 10},
             "internal_formulas": {"config_margin": "$gv(clock_gap)$"},
             "viewgroup_items": [hours, minutes]}
    for text in (hours, minutes):
        old, new = FONTS[text["internal_title"]]
        assert text["text_family"] == PREFIX + old
        text["text_family"] = PREFIX + new
        for key in POSITION:
            text.pop(key, None)
    items[items.index(hours)] = stack
    items.remove(minutes)

    globals_list = root["globals_list"]
    globals_list["clock_gap"] = {"index": len(globals_list) + 1, "type": "NUMBER",
                                 "title": "Clock: gap between hours and minutes", "value": GAP}

    dropped = {"fonts/" + old for old, _ in FONTS.values()}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            if entry.filename in dropped:
                continue
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)
        for _, new in FONTS.values():
            out.write(os.path.join(font_dir, new), "fonts/" + new)


if __name__ == "__main__":
    main(*sys.argv[1:4])
