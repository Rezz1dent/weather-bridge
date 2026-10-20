#!/usr/bin/env python3
"""Stack gaps that do not depend on hidden items.

Usage: fix_removed_gaps.py IN.kwgt OUT.kwgt TITLE

KWGT keeps a horizontal stack's gap (config_margin) next to an item hidden with
config_visible = REMOVE. The umbrella is the last item of "Today + tomorrow + umbrella",
so without it the row ended 8 units short of the right edge (the middle row, whose hidden
item "rain now" sits in the middle, only got a wider gap). In every horizontal stack with
a hideable item the gap becomes the left padding of each item after the first, which
disappears together with a hidden item.
"""
import json
import sys
import time
import uuid
import zipfile


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    for stack in walk(preset["preset_root"]["viewgroup_items"]):
        children = stack.get("viewgroup_items", [])
        if (stack["internal_type"] != "StackLayerModule"
                or not stack.get("config_stacking", "").startswith("HORIZONTAL")
                or not any(c.get("internal_toggles", {}).get("config_visible") for c in children)):
            continue
        gap = float(stack.get("config_margin", 0))
        assert not stack.get("internal_toggles", {}).get("config_margin"), stack["internal_title"]
        for child in children[1:]:
            assert not child.get("internal_toggles", {}).get("position_padding_left"), child["internal_title"]
            child["position_padding_left"] = child.get("position_padding_left", 0) + gap
        stack["config_margin"] = 0.0
        print("%s: gap %g -> padding of %s" % (stack["internal_title"], gap,
                                               ", ".join(c["internal_title"] for c in children[1:])))

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
