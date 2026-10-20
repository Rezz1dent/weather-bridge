#!/usr/bin/env python3
"""Breezy Minimal: more size steps, a shorter alarm, and "maximal" with modes.

Usage: build_v108_steps.py IN.kwgt OUT.kwgt TITLE

- Bottom row: a second step, 16 (icons too), when even 18 does not fit (estimate > 580;
  the first step stays at > 445). With every longest value the row needs ~484 units at 18
  and ~435 at 16 (OPPO Sans, row ~486 wide).
- Temperature 78 -> 66 in deep frost (<= -20, three characters with the minus) while the
  clock has no "1" (the only narrow digit): only then can the clock and the temperature
  touch (measured for every time and temperature). The top padding grows 10 -> 21 so the
  baseline stays with the clock's.
- Alarm: the weekday only when the alarm is more than a day away (today, or tomorrow at
  an earlier time of day, is clear from the time alone); the row estimate counts 5 or 10.
- Global "maximal" becomes a list: 0 off, 1 longest values at full size, 2 the same with
  the first step everywhere (rows, temperature), 3 with the smallest sizes.
"""
import json
import re
import sys
import time
import uuid
import zipfile

STEP2 = 580
SIZE = re.compile(r"^\$if\(gv\(maximal\) > 0 \| (.*) > 445, (-?[\d.]+), (-?[\d.]+)\)\$$", re.S)
ALARM_EST = "if(si(alarmon) = 1, 10, 0)"
SOON = ('(df("yyyyMMdd", si(alarmd)) = df("yyyyMMdd") | (df("yyyyMMdd", si(alarmd)) = '
        'df("yyyyMMdd", a1d) & df("HHmm", si(alarmd)) <= df("HHmm")))')
WEEKDAY = '" (" + df("EEE", si(alarmd)) + ")"'
TEMP_NUM = 'tc(reg, br(breezy, temp), "[^0-9-]", "")'
FROST = ('(gv(maximal) > 1 | (gv(maximal) = 0 & %s != "" & %s <= -20 & '
         'tc(len, tc(reg, df("HHmm"), "1", "")) = 4))' % (TEMP_NUM, TEMP_NUM))


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def formula(item, key, value):
    item.setdefault("internal_toggles", {})[key] = 10
    item.setdefault("internal_formulas", {})[key] = value


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    root = preset["preset_root"]
    old = root["globals_list"]["maximal"]
    root["globals_list"]["maximal"] = {
        "index": old["index"], "type": "LIST",
        "title": "Maximal: 0 off, 1 longest values, 2 + first size step, 3 + smallest sizes",
        "entries": "0, 1, 2, 3", "value": "0"}

    counts = {"step2": 0, "step1": 0, "alarm est": 0}
    for item in walk(root["viewgroup_items"]):
        if "text_expression" in item:
            item["text_expression"] = item["text_expression"].replace("gv(maximal) = 1", "gv(maximal) > 0")
        for key, value in list(item.get("internal_formulas", {}).items()):
            value = value.replace("gv(maximal) = 1", "gv(maximal) > 0")
            n = value.count(ALARM_EST)
            value = value.replace(ALARM_EST, "if(si(alarmon) = 1, if(%s, 5, 10), 0)" % SOON)
            counts["alarm est"] += n
            m = SIZE.match(value)
            if m:
                est, small, big = m.groups()
                step1 = "(gv(maximal) > 1 | (gv(maximal) = 0 & %s > 445))" % est
                if (small, big) == ("18", "20"):
                    step2 = "(gv(maximal) = 3 | (gv(maximal) = 0 & %s > %d))" % (est, STEP2)
                    value = "$if(%s, 16, %s, 18, 20)$" % (step2, step1)
                    counts["step2"] += 1
                else:
                    value = "$if(%s, %s, %s)$" % (step1, small, big)
                    counts["step1"] += 1
            item["internal_formulas"][key] = value

    items = {i.get("internal_title"): i for i in walk(root["viewgroup_items"])}
    alarm = items["Alarm time"]
    plain = 'df("HH:mm", si(alarmd)) + " (" + df("EEE", si(alarmd)) + ")"'
    assert alarm["text_expression"].count(plain) == 1
    alarm["text_expression"] = alarm["text_expression"].replace(
        plain, 'df("HH:mm", si(alarmd)) + if(%s, "", %s)' % (SOON, WEEKDAY))

    temp = items["Row 1 • Breezy temperature"]
    size, pad = temp["text_size"], temp.get("position_padding_top", 0)
    small = 66.0
    formula(temp, "text_size", "$if(%s, %g, %g)$" % (FROST, small, size))
    # Keep the baseline: hhea ascent of OPPO Sans 0.928 em.
    formula(temp, "position_padding_top", "$if(%s, %g, %g)$" % (FROST, round(pad + 0.928 * (size - small)), pad))
    print(counts)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:4])
