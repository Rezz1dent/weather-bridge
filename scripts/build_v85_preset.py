#!/usr/bin/env python3
"""Breezy Minimal v85: clock in Manrope Bold (hours) + Light (minutes), was ExtraBold + ExtraLight.

Usage: build_v85_preset.py BASE_v84.kwgt FONT_DIR OUT.kwgt
       FONT_DIR = output of make_manrope_fonts.py (Manrope-Bold-Tnum.ttf, Manrope-Light-Tnum.ttf)

Tabular digits have the same advance in every weight, so the minutes keep their position.
The old clock fonts are dropped from the archive; the new files have names KWGT has never
seen, so no stale font cache can stand in for them.
"""
import json
import os
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.5 • Manrope"
CLOCK = {"Clock • hours": ("Manrope-ExtraBold-Tnum.ttf", "Manrope-Bold-Tnum.ttf"),
         "Clock • minutes": ("Manrope-ExtraLight-Tnum.ttf", "Manrope-Light-Tnum.ttf")}
PREFIX = "kfile://org.kustom.provider/fonts/"


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, font_dir, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    items = {i.get("internal_title"): i for i in walk(preset["preset_root"]["viewgroup_items"])}
    for title, (old, new) in CLOCK.items():
        assert items[title]["text_family"] == PREFIX + old, items[title]["text_family"]
        items[title]["text_family"] = PREFIX + new
    used = json.dumps(preset)
    dropped = {"fonts/" + old for old, _ in CLOCK.values()}
    assert not any(name.split("/")[1] in used for name in dropped)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            if entry.filename in dropped:
                continue
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)
        for _, new in CLOCK.values():
            out.write(os.path.join(font_dir, new), "fonts/" + new)


if __name__ == "__main__":
    main(*sys.argv[1:4])
