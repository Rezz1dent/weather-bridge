#!/usr/bin/env python3
"""Alarm weekday: "less than a day away" by minutes, without the a1d date.

Usage: fix_alarm_soon.py IN.kwgt OUT.kwgt TITLE

build_v108_steps.py compared dates with df("yyyyMMdd", a1d); on the owner's phone the
weekday stayed for an alarm tomorrow morning. Now: minutes until the alarm = day-of-year
difference (+365 across New Year) x 1440 + time-of-day difference; the weekday is hidden
below 1440. Replaced everywhere (alarm text and the row estimates).
"""
import json
import sys
import time
import uuid
import zipfile

OLD = ('(df("yyyyMMdd", si(alarmd)) = df("yyyyMMdd") | (df("yyyyMMdd", si(alarmd)) = '
       'df("yyyyMMdd", a1d) & df("HHmm", si(alarmd)) <= df("HHmm")))')
NEW = ('(((df(D, si(alarmd)) - df(D) + if(df(D, si(alarmd)) < df(D), 365, 0)) * 1440 + '
       'df(H, si(alarmd)) * 60 + df(m, si(alarmd)) - df(H) * 60 - df(m)) < 1440)')


def main(source_path, target, title):
    source = zipfile.ZipFile(source_path)
    text = source.read("preset.json").decode("utf-8")
    preset = json.loads(text)
    preset["preset_info"].update(title=title, id=str(uuid.uuid4()), ts=int(time.time() * 1000))
    data = json.dumps(preset, ensure_ascii=False, indent=2)
    count = data.count(json.dumps(OLD, ensure_ascii=False)[1:-1])
    assert count, "old condition not found"
    data = data.replace(json.dumps(OLD, ensure_ascii=False)[1:-1], json.dumps(NEW, ensure_ascii=False)[1:-1])
    print("replaced", count)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for entry in source.infolist():
            payload = source.read(entry.filename)
            if entry.filename == "preset.json":
                payload = data.encode("utf-8")
            out.writestr(entry, payload)


if __name__ == "__main__":
    main(*sys.argv[1:4])
