#!/usr/bin/env python3
"""Breezy Minimal v89: blocks, as in the owner's personal v9.4.

Usage: build_v89_preset.py BASE_v88.kwgt OUT.kwgt

- Temperature and weather icon go into one horizontal stack (tops aligned), so the pair
  moves with one offset; their old relative position is kept with a top padding on the
  lower one and the stack gap.
- Rows 2 and 3 become two vertical stacks: date over alarm/sun (left edge) and wind over
  today/tomorrow (right edge). Offsets inside a stack do not count, so the per-row shifts
  become paddings: x 20 / 12 (crowded row) -> column at 12 + padding 8 / 0, y +2 / -2 for
  the small font -> padding_top. Gap between the rows: 42 (old y difference) - Manrope
  line height at 22 (30) - padding 2 = 10.
- Order as in v9.4: clock tap zone, the two columns, weather tap zone on top.
"""
import json
import re
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.9 • Manrope"
TEMP = "Row 1 • Breezy temperature"
ICON = "Row 1 • Current weather icon (Breezy, Iconify mdi)"
LEFT = ["Date", "Next alarm + next sunset/sunrise"]
RIGHT = ["Wind + rain now + feels like", "Today + tomorrow + umbrella"]
EDGE, INDENT, ROWS_Y, ROWS_GAP = 12, 8, 110.0, 10.0
CHOICE = re.compile(r"^\$if\((.*), -?[\d.]+, -?[\d.]+\)\$$", re.S)
POSITION = ("position_anchor", "position_offset_x", "position_offset_y")


def unplace(item):
    for key in POSITION:
        item.pop(key, None)
        item.get("internal_toggles", {}).pop(key, None)
        item.get("internal_formulas", {}).pop(key, None)


def formula(item, key, value):
    item.setdefault("internal_toggles", {})[key] = 10
    item.setdefault("internal_formulas", {})[key] = value


def weather(temp, icon):
    assert temp["position_anchor"] == icon["position_anchor"] == "TOPRIGHT"
    tx, ty = temp.get("position_offset_x", 0), temp.get("position_offset_y", 0)
    ix, iy = icon.get("position_offset_x", 0), icon.get("position_offset_y", 0)
    if ty > iy:
        temp["position_padding_top"] = ty - iy
    elif iy > ty:
        icon["position_padding_top"] = iy - ty
    unplace(temp)
    unplace(icon)
    return {
        "internal_type": "StackLayerModule",
        "internal_title": "Row 1 • Weather (temperature + icon)",
        "config_stacking": "HORIZONTAL_TOP",
        "config_margin": float(tx - (ix + icon["icon_size"])),
        "position_anchor": "TOPRIGHT",
        "position_offset_x": float(ix),
        "position_offset_y": float(min(ty, iy)),
        "viewgroup_items": [temp, icon],
    }


def column(title, stacking, anchor, items, side):
    middle, bottom = items
    for item in items:
        m = CHOICE.match(item["internal_formulas"]["position_offset_y"])
        assert m, item.get("internal_title")
        crowded = m.group(1)
        unplace(item)
        if item is middle:
            item["position_padding_" + side] = float(INDENT)
            formula(item, "position_padding_top", "$if(%s, 2, 0)$" % crowded)
        else:
            formula(item, "position_padding_" + side, "$if(%s, 0, %d)$" % (crowded, INDENT))
            formula(item, "position_padding_top", "$if(%s, 0, 2)$" % crowded)
    return {
        "internal_type": "StackLayerModule",
        "internal_title": title,
        "config_stacking": stacking,
        "config_margin": ROWS_GAP,
        "position_anchor": anchor,
        "position_offset_x": float(EDGE),
        "position_offset_y": ROWS_Y,
        "viewgroup_items": items,
    }


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = preset["preset_root"]["viewgroup_items"]
    by_title = {i.get("internal_title"): i for i in items}

    block = weather(by_title[TEMP], by_title[ICON])
    left = column("Rows 2-3 • left column", "VERTICAL_LEFT", "TOPLEFT",
                  [by_title[t] for t in LEFT], "left")
    right = column("Rows 2-3 • right column", "VERTICAL_RIGHT", "TOPRIGHT",
                   [by_title[t] for t in RIGHT], "right")
    taps = [by_title["Ярлык Часов"], by_title["Ярлык Погоды"]]

    moved = {TEMP, ICON, "Ярлык Часов", "Ярлык Погоды", *LEFT, *RIGHT}
    rest = []
    for item in items:
        if item is by_title[TEMP]:
            rest.append(block)
        elif item.get("internal_title") not in moved:
            rest.append(item)
    preset["preset_root"]["viewgroup_items"] = rest + [taps[0], left, right, taps[1]]

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
