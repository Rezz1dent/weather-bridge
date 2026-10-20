#!/usr/bin/env python3
"""Breezy Minimal: smaller top row in one proportion, no automatic shrinking there.

Usage: build_v109_top.py IN.kwgt OUT.kwgt TITLE

Clock C = 96 (was 95 x 1.15 = 109), temperature C / sqrt(2) = 68 (was 78, ratio 0.714),
icon 0.6 C = 58 (was 65, ratio 0.595): the old proportions, rounded to simple ones. With
the longest values (00 44 and -40°) the gap between the clock and the weather is ~69 units
(it was 8). The clock stack's scale becomes 100 and the text sizes carry the size.

Vertical: the clock's baseline, the temperature's baseline (1 unit lower, as before), the
icon's top relative to the baseline (0.745 C) and the distance from the baseline to the
divider stay as they were; the whole layout moves down by half of what the row lost, so
it stays centred. The frost rule of build_v108_steps.py is removed from the temperature.
"""
import json
import math
import sys
import time
import uuid
import zipfile

ASCENT, DESCENT = 0.928, 0.244     # OPPO Sans hhea, em
CLOCK, TEMP, ICON = 96.0, round(96 / math.sqrt(2)), round(96 * 0.6)


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = {i.get("internal_title"): i for i in walk(preset["preset_root"]["viewgroup_items"])}
    layout = items["Layout (move everything here)"]
    clock = items["Clock"]
    hours, minutes = items["Clock • hours"], items["Clock • minutes"]
    weather = items["Row 1 • Weather (temperature + icon)"]
    temp = items["Row 1 • Breezy temperature"]
    icon = items["Row 1 • Current weather icon (Breezy, Iconify mdi)"]

    old_c = hours["text_size"] * clock.get("config_scale_value", 100) / 100
    old_t, old_i = 78.0, icon["icon_size"]
    old_wpad, old_tpad = weather.get("position_padding_top", 0), 10.0
    base = ASCENT * old_c                                   # clock baseline from the row top
    temp_drop = old_wpad + old_tpad + ASCENT * old_t - base  # temperature baseline vs clock's
    icon_above = base - old_wpad                            # icon top above the baseline
    divider_gap = layout["config_margin"] + DESCENT * old_c  # baseline -> divider

    clock["config_scale_value"] = 100.0
    hours["text_size"] = minutes["text_size"] = CLOCK
    new_base = ASCENT * CLOCK
    wpad = round(new_base - icon_above * CLOCK / old_c, 1)
    weather["position_padding_top"] = wpad
    for key in ("text_size", "position_padding_top"):
        temp.get("internal_toggles", {}).pop(key, None)
        temp.get("internal_formulas", {}).pop(key, None)
    temp["text_size"] = float(TEMP)
    temp["position_padding_top"] = round(new_base + temp_drop - wpad - ASCENT * TEMP, 1)
    icon["icon_size"] = float(ICON)
    weather["config_margin"] = round(weather.get("config_margin", 0) * TEMP / old_t, 1)
    layout["config_margin"] = round(divider_gap - DESCENT * CLOCK, 1)
    layout["position_offset_y"] = round(layout["position_offset_y"] + ASCENT * (old_c - CLOCK) / 2, 1)
    print("clock %g, temp %g (pad %g), icon %g, weather pad %g, gap %g, layout y %g" % (
        CLOCK, TEMP, temp["position_padding_top"], ICON, wpad, layout["config_margin"],
        layout["position_offset_y"]))

    g = preset["preset_root"]["globals_list"]["maximal"]
    g["title"] = "Maximal: 0 off, 1 longest values, 2 + first size step, 3 + smallest sizes (rows)"

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
