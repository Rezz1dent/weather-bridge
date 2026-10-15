#!/usr/bin/env python3
"""Breezy Minimal v79: no alarm set = only the crossed-out alarm icon, without "—".

Usage: build_v79_preset.py BASE_v78.kwgt OUT.kwgt
"""
import json
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v7.9 • Manrope"
DASH = ', "—"))$'


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = list(walk(preset["preset_root"]["viewgroup_items"]))

    alarm = next(i for i in items if i.get("internal_title") == "Alarm time")
    assert alarm["text_expression"].endswith(DASH)
    alarm["text_expression"] = alarm["text_expression"][:-len(DASH)] + ', ""))$'
    # Row width estimate (build_v75_preset.py) counted the dash as one character.
    changed = 0
    for item in items:
        for key, value in item.get("internal_formulas", {}).items():
            if "if(si(alarmon) = 1, 10, 1)" in value:
                item["internal_formulas"][key] = value.replace(
                    "if(si(alarmon) = 1, 10, 1)", "if(si(alarmon) = 1, 10, 0)")
                changed += 1
    assert changed

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
