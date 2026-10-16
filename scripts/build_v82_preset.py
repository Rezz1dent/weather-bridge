#!/usr/bin/env python3
"""Breezy Minimal v82: tapping the sunrise/sunset time cycles what it shows.

Usage: build_v82_preset.py BASE_test21.kwgt OUT.kwgt   (test21 = owner's export with the
       LIST global "sun" = "0, 1, 2" and the tap action SWITCH_GLOBAL sun on "Sun")

sun = 0  the usual: next sunset by day, next sunrise by night
sun = 1  the other one: today's sunrise by day, today's sunset by night
sun = 2  day length (sunset - sunrise) as h:mm with the sun-clock icon; at night before
         midnight it is tomorrow's day
A tap goes to the next value (KWGT cycles a LIST global). Resetting to 0 after a minute is
a KWGT flow, made by hand in the editor (trigger: gv(sun) changes; delay; set sun = 0).
"""
import json
import sys
import time
import uuid
import zipfile

TITLE = "Breezy Minimal v8.2 • Manrope"
SUN_TITLE = "Sun: tap mode (0 next event, 1 other event, 2 day length)"


def minutes(date):
    return "(df(H, {d}) * 60 + df(m, {d}))".format(d=date)


def length(day):
    shift = ", a1d" if day else ""
    return "({} - {})".format(minutes("ai(sunset%s)" % shift), minutes("ai(sunrise%s)" % shift))


DAY_LENGTH = ('if(ai(isday) = 0 & df(H) >= 12, {tomorrow}, {today})'
              .format(tomorrow=length(True), today=length(False)))
HOURS = "mu(floor, #dlen / 60)"
REST = "(#dlen - {} * 60)".format(HOURS)
TIME = ('$lv(dlen, {length}) + if(gv(maximal) = 1, "22:58", '
        'gv(sun) = 2, {hours} + ":" + if({rest} < 10, "0", "") + {rest}, '
        'gv(sun) = 1, df(HH:mm, if(ai(isday) = 1, ai(sunrise), ai(sunset))), '
        'df(HH:mm, if(ai(isday) = 1, ai(sunset), df(H) >= 12, ai(sunrise, a1d), ai(sunrise))))$'
        ).format(length=DAY_LENGTH, hours=HOURS, rest=REST)
ICON = ('$if(gv(maximal) = 1, "weather-sunset-down", gv(sun) = 2, "sun-clock-outline", '
        'ai(isday) = 1, if(gv(sun) = 1, "weather-sunset-up", "weather-sunset-down"), '
        'if(gv(sun) = 1, "weather-sunset-down", "weather-sunset-up"))$')


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("viewgroup_items", []))


def main(base, target):
    source = zipfile.ZipFile(base)
    preset = json.loads(source.read("preset.json").decode("utf-8"))
    preset["preset_info"].update(title=TITLE, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    root = preset["preset_root"]
    sun = root["globals_list"]["sun"]
    assert sun["type"] == "LIST" and sun["entries"] == "0, 1, 2", sun
    sun.update(title=SUN_TITLE, value="0")

    items = {i.get("internal_title"): i for i in walk(root["viewgroup_items"])}
    assert items["Sun"]["internal_events"] == [
        {"type": "SINGLE_TAP", "action": "SWITCH_GLOBAL", "switch": "sun"}]
    assert "Sun time" in items and "Sun icon" in items
    items["Sun time"]["text_expression"] = TIME
    items["Sun icon"]["internal_formulas"]["icon_icon"] = ICON

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == "preset.json":
                data = json.dumps(preset, ensure_ascii=False, indent=2).encode("utf-8")
            out.writestr(entry, data)


if __name__ == "__main__":
    main(*sys.argv[1:3])
