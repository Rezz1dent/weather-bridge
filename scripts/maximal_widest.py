#!/usr/bin/env python3
"""The "maximal" switch shows the widest values that can really occur.

Usage: maximal_widest.py IN.kwgt OUT.kwgt TITLE

For every field the candidates are the values it can show (times 00:00-23:59, day 1-31
of a real month, temperatures -40..40, wind up to 29.9 m/s, rain now up to 39.9 mm,
tomorrow up to 99.9 mm), measured with the font the field uses inside the preset; the
widest one becomes the field's "maximal" text. Russian names as Android writes them
for df("EEEE, d MMM") and df("EEE").

The clock is wrapped in tc(lpad, ..., 2, 0): KWGT reads a literal "00" as the number 0,
so if(gv(maximal) = 1, "00", ...) showed a single 0.
"""
import io
import json
import re
import sys
import time
import uuid
import zipfile

from fontTools.ttLib import TTFont

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
SHORT_DAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
MONTHS = [("янв.", 31), ("февр.", 29), ("мар.", 31), ("апр.", 30), ("мая", 31), ("июн.", 30),
          ("июл.", 31), ("авг.", 31), ("сент.", 30), ("окт.", 31), ("нояб.", 30), ("дек.", 31)]
TIMES = ["%02d:%02d" % (h, m) for h in range(24) for m in range(60)]
TEMPS = list(range(-40, 41))


def tenths(top):
    return [("%.1f" % (n / 10)).replace(".", ",") for n in range(1, int(top * 10) + 1)]


CANDIDATES = {
    "Row 1 • Breezy temperature": ["%d°" % t for t in TEMPS],
    "Feels like value": ["%d°" % t for t in TEMPS],
    "Today range": ["%d/%d°" % (hi, lo) for hi in TEMPS for lo in TEMPS if lo <= hi],
    "Tomorrow range": ["%d/%d°" % (hi, lo) for hi in TEMPS for lo in TEMPS if lo <= hi],
    "Date": ["%s, %d %s" % (d, n, m) for d in DAYS for m, last in MONTHS for n in range(1, last + 1)],
    "Wind": ["↖ %s м/с" % v for v in tenths(29.9)],
    "Rain mm (precip_now)": tenths(39.9),
    "Tomorrow mm": tenths(99.9),
    "Alarm time": ["%s (%s)" % (t, d) for t in TIMES for d in SHORT_DAYS],
    "Sun time": TIMES,
}
CLOCK = {"Clock • hours": ("H", range(24)), "Clock • minutes": ("m", range(60))}


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    fonts = {}

    def width(item, text):
        name = item["text_family"].rsplit("/", 1)[1]
        if name not in fonts:
            font = TTFont(io.BytesIO(source.read("fonts/" + name)))
            fonts[name] = (font.getBestCmap(), font["hmtx"])
        cmap, hmtx = fonts[name]
        return sum(hmtx[cmap[ord(c)]][0] for c in text)

    for item in walk(preset["preset_root"]["viewgroup_items"]):
        name = item.get("internal_title")
        if name in CLOCK:
            unit, values = CLOCK[name]
            best = max(values, key=lambda v: width(item, "%02d" % v))
            item["text_expression"] = '$tc(lpad, if(gv(maximal) = 1, %d, df(%s)), 2, 0)$' % (best, unit)
            print("%s: %02d" % (name, best))
        elif name in CANDIDATES:
            best = max(CANDIDATES[name], key=lambda v: width(item, v))
            expression, n = re.subn(r'gv\(maximal\) = 1, "[^"]*"', 'gv(maximal) = 1, "%s"' % best,
                                    item["text_expression"])
            assert n == 1, name
            item["text_expression"] = expression
            print("%s: %s" % (name, best))

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
