#!/usr/bin/env python3
"""Breezy Minimal: the whole layout as one vertical Stack (owner's scheme, OPPO v10.0+).

Usage: build_v100_layout.py BASE.kwgt OUT.kwgt TITLE

    Layout (vertical stack, centred, at the old clock top)
    ├─ Top row     [clock | temperature + icon]
    ├─ Divider
    └─ Rows 2-3    (vertical stack, the old columns' scale)
       ├─ Row 2    [date | wind, rain now, feels like]
       └─ Row 3    [alarm, sun | today, tomorrow, umbrella]

A Stack lays items one after another and cannot pin one item left and another right.
Each row is therefore an Overlap group: an invisible line as wide as the widget (global
layout_width, the root width in units, ~497; if the edges look uneven, change it) gives
the group its width, the left part is anchored TOPLEFT and the right part TOPRIGHT.
Long values (the "maximal" switch) meet in the middle instead of pushing the edges out
(v10.1 used two fixed-width half stacks, and long values pushed the row past the edges).
KWGT ignores offsets inside an Overlap group, so the distance from the edge is the
padding of a one-item stack around each part.

Vertical positions come from the old absolute ones, with KWGT's text box height =
hhea ascent - descent (OPPO Sans 1.172 em): clock box 95 x 1.172 x 1.15 = 128 from y -15,
divider at 105, rows at 115. One stack has one gap, so the outer gap is -8 (top row ->
divider) and the divider gets padding_bottom 17 (divider -> rows: 9).

The layout sits above the clock tap zone (as the old rows did, so the date and sun taps
work); the clock digits therefore get the clock tap zone's own action.
"""
import json
import sys
import time
import uuid
import zipfile

LINE = "#00000000"
WIDTH = 497.0
TOP_Y = -15.0          # old clock y
EDGE = 10.0            # old x of the clock, the weather group and the columns
CLOCK_BOX = 128.0      # see the docstring
DIVIDER_Y = 105.0      # root height ~190: centre 95 + offset 10
ROWS_Y = 115.0         # old y of the columns


def side(item, anchor, pad_key, edge):
    """One-item stack: the anchor works inside an Overlap group, the padding is the edge."""
    return {
        "internal_type": "StackLayerModule",
        "internal_title": "Left part" if anchor == "TOPLEFT" else "Right part",
        "config_stacking": "HORIZONTAL_TOP",
        "position_anchor": anchor,
        pad_key: edge,
        "viewgroup_items": [item],
    }


def row(title, left, right, scale=1.0):
    edge = round(EDGE / scale, 2)
    line = {
        "internal_type": "ShapeModule",
        "internal_title": "Row width (invisible)",
        "shape_type": "RECT",
        "shape_width": round(WIDTH / scale, 2),
        "shape_height": 1.0,
        "paint_color": LINE,
        "position_anchor": "TOPLEFT",
        "internal_toggles": {"shape_width": 10},
        "internal_formulas": {"shape_width": "$gv(layout_width)%s$" % (" / %g" % scale if scale != 1 else "")},
    }
    return {
        "internal_type": "OverlapLayerModule",
        "internal_title": title,
        "viewgroup_items": [line, side(left, "TOPLEFT", "position_padding_left", edge),
                            side(right, "TOPRIGHT", "position_padding_right", edge)],
    }


def unplace(item):
    for key in ("position_anchor", "position_offset_x", "position_offset_y"):
        item.pop(key, None)
        item.get("internal_toggles", {}).pop(key, None)
        item.get("internal_formulas", {}).pop(key, None)


def main(base, target, title):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    root = preset["preset_root"]
    items = root["viewgroup_items"]
    by_title = {i.get("internal_title"): i for i in items}

    clock = by_title["Clock"]
    weather = by_title["Row 1 • Weather (temperature + icon)"]
    divider = next(i for i in items if i["internal_type"] == "ShapeModule"
                   and i.get("shape_height") == 1.0 and not i.get("internal_title"))
    left_col = by_title["Rows 2-3 • left column"]
    right_col = by_title["Rows 2-3 • right column"]
    clock_tap = by_title["Ярлык Часов"]
    weather_tap = by_title["Ярлык Погоды"]
    assert clock["position_offset_y"] == TOP_Y and clock["position_offset_x"] == EDGE

    weather["position_padding_top"] = weather["position_offset_y"] - TOP_Y
    for item in (clock, weather, divider):
        unplace(item)
    divider["internal_title"] = "Divider"
    divider["position_padding_bottom"] = ROWS_Y - (DIVIDER_Y + 1) - (DIVIDER_Y - (TOP_Y + CLOCK_BOX))
    for text in clock["viewgroup_items"]:
        text["internal_events"] = json.loads(json.dumps(clock_tap["internal_events"]))

    scale = left_col.get("config_scale_value", 100.0) / 100
    date, alarm = left_col["viewgroup_items"]
    wind, today = right_col["viewgroup_items"]
    rows = {
        "internal_type": "StackLayerModule",
        "internal_title": "Rows 2-3",
        "config_stacking": "VERTICAL_CENTER",
        "config_margin": left_col.get("config_margin", 10.0),
        "config_scale_value": left_col.get("config_scale_value", 100.0),
        "viewgroup_items": [row("Row 2 • date | weather now", date, wind, scale),
                            row("Row 3 • alarm, sun | today, tomorrow", alarm, today, scale)],
    }
    layout = {
        "internal_type": "StackLayerModule",
        "internal_title": "Layout (move everything here)",
        "config_stacking": "VERTICAL_CENTER",
        "config_margin": DIVIDER_Y - (TOP_Y + CLOCK_BOX),
        "position_anchor": "TOP",
        "position_offset_y": TOP_Y,
        "viewgroup_items": [row("Row 1 • clock | weather", clock, weather), divider, rows],
    }

    background = items[0]
    assert background.get("internal_title") == "Transparent background"
    root["viewgroup_items"] = [background, clock_tap, layout, weather_tap]

    globals_list = root["globals_list"]
    for name in ("rows_y", "rows_gap"):        # unused since the owner's v9.3
        globals_list.pop(name, None)
    globals_list["layout_width"] = {
        "index": max(g["index"] for g in globals_list.values()) + 1, "type": "NUMBER",
        "title": "Layout: widget width (edges even? change it)", "value": WIDTH}
    for n, g in enumerate(sorted(globals_list.values(), key=lambda g: g["index"]), 1):
        g["index"] = n

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
