# Weather Bridge + KWGT widget — project status

Snapshot for picking the work up in a new session. Repository: `Rezz1dent/weather-bridge`,
branch `main` (moved out of the old `Rezz1dent/Lwidget` fork in October 2026; history keeps only
this project's commits, paths rewritten to the layout below). Conversation with the owner is in
Russian.

## What it is

- **Weather Bridge** (`app/`, Android, Java, no dependencies, no launcher icon, package and
  namespace `com.rezz1dent.weatherbridge`; until 1.8 it was "Breezy Bridge",
  `com.rezz1dent.breezykwgtbridge`): reads Breezy Weather's ContentProvider
  (`org.breezyweather.provider.weather`, needs Breezy 6.1+ and the `READ_PROVIDER`
  permission) when Breezy's "Update Notifier" broadcast arrives, and sends ~40 variables to
  KWGT as `$br(breezy, name)$` (the KWGT extension name stays `breezy`, the presets use it).
  Current version **2.0** (versionCode 12). GitHub Actions workflow "Build" builds the release
  APK on pushes to `main` (artifact `weather-bridge-apk`) and publishes the GitHub release
  `v<versionName>` when that version has none yet (APK + current preset, notes from
  `docs/release-notes/v<version>.md`). Tag pushes from the cloud session are blocked by its proxy,
  hence this. To release: bump `versionName`/`versionCode`, add the notes file, push.
- **KWGT preset** "Breezy Minimal" (`widget/`, older versions in `widget/archive/`): clock +
  Breezy weather, Manrope fonts, Material Design Icons via KWGT's built-in Iconify set.

Docs: `README.md` / `README.ru.md` (setup, variables, credits), `docs/TODO.md`,
`docs/KWGT_NOTES.md` (KWGT file format, Kode formulas, lessons learned on the phone — read it
before editing presets). Preset build scripts in `scripts/` (abandoned ones in
`scripts/archive/`).

## Current widget: v7.6 (`widget/Breezy_Minimal_v76__Manrope.kwgt`)

Built by a chain of scripts from the owner's hand-tuned exports:
`v70` (exported from the phone) → `build_v71_preset.py` → `build_v72_preset.py` → owner's
hand-tuned `v73` (exported; sizes: middle row 22, bottom row 18) → `build_v73_preset.py`
(alarm icon) = `v74` → `build_v75_preset.py` (automatic row sizes) = `v75` → `build_v76_preset.py` (rain / snow / mix icons) = `v76`. Always start the next change from the newest export of the owner. Fonts come from `make_manrope_fonts.py` (needs the variable
`Manrope[wght].ttf` from google/fonts; static weights, tabular clock digits, narrow minus,
spacer glyphs in `Manrope-Light-Spaced`).

Layout (root ~497 × 190 units at scale 160, widget 1458 × 533 px, grid 8×3, KWGT sizing Auto):

```
05 28            -35° ☀              hours ExtraBold / minutes ExtraLight (95), temp 78, icon 65
───────────────────────────
Воскресенье, 28 сент.   ↖ 12,5 м/с 💧12,5 👤-42°        middle row, size 22 / 20 (auto)
⏰ 20:08 (пн) 🌇 22:58    -35/-42° 📅 -35/-42° ☂ 100% 💧12,5   bottom row, size 20 / 18 (auto)
```

- Middle: date with short month; stack: wind | rain now (`precip_now`, only while it
  rains) | feels-like (`account-outline` icon + `like`).
- Bottom left: stack: alarm (`alarm` / `alarm-off` icon + time) | next sunset by day /
  sunrise by night (KWGT `ai()`, its own location, offline).
- Bottom right: stack: today's range | `calendar-arrow-right` + tomorrow's range | umbrella
  group (`umbrella-outline` + probability + drop + `tomorrow_precip_mm`), hidden with
  `config_visible = REMOVE` below the threshold.
- Precipitation icon (rain now, tomorrow's mm): bridge 1.8 `precip_now_icon` /
  `tomorrow_precip_icon` = `water-outline` (rain), `snowflake` (snow), `snowflake-melt` (mix:
  rain and snow each from a quarter of the sum, or a quarter of ice); drop with an older bridge.
- Weather icon: bridge's `icon_mdi`, sun/moon variant re-chosen in KWGT with `ai(isday)`;
  clear day = outline `weather-sunny`.
- Shadow everywhere: `#68000000`, distance 1, small blur (blur grows the frame and shifts text).
- Root globals: `umbrella_test` (switch, always show umbrella), `umbrella_min` (number, %,
  owner uses 60), `maximal` (switch: every row shows its longest value, for overlap checks),
  `precip_test` (number: 0 data, 1 rain, 2 snow, 3 mix; shows both precipitation blocks and
  the umbrella with that icon).

Automatic sizes (v7.5): KWGT cannot measure text, so each row estimates its width from the
character and icon counts of the current values (middle 0.52 em/char + 1.1 em/icon, bottom
0.55 + 1.3, plus margins; limit 445 units for both halves of a row) and uses the big size
(middle 22, bottom 20) when it fits, else the small one (20 / 18, the owner's sizes). Formulas
sit on `text_size` / `icon_size` of every text and icon and on `position_offset_y` of the row
roots (keeps the baseline). `maximal` always shows the small size. Constants at the top of
`build_v75_preset.py`. Calibration: text widths from the font are exact, stack icons/margins
take ~14% more than nominal; the estimate is deliberately on the wide side.

## Decisions and why

- **Icons**: icon fonts bundled in a preset did not work on the home screen ("?"); only
  KWGT built-in sets work → Iconify `iconify://mdi?name=Material%20Design%20Icons`.
- **Fonts** bundled in the preset (`fonts/*.ttf`) work, but the home screen needs **one phone
  reboot** after the first import (and after a font file with the same name changes).
- **English weekday** with a half-cut word (v51–v53) was tried and dropped by the owner.
- Bridge visibility: Breezy has no `<queries>` entry for its own Update Notifier, so it only
  sees the bridge after the bridge read its provider; the bridge re-reads it on boot/update
  (`BootReceiver`). If Breezy lists "no compatible packages": tap "send to KWGT" in the
  bridge, close Breezy, reopen its settings, enable the bridge.
- Temperatures arrive with "-" (hyphen); the bundled fonts draw it as a narrow minus.

## Open / ideas

- Automatic row sizes work on the phone (v7.5). Check v7.6's precipitation icons with
  `precip_test` 1-3 (`snowflake-melt` is a newer MDI icon). If the size switch comes too early
  or too late, tune the coefficients or `FIT` in `build_v75_preset.py`.
- Possible upstream issue for Breezy: add its own `ACTION_UPDATE_NOTIFIER` to `<queries>`.
- Release signing: owner's key (PKCS12, alias `weatherbridge`, created 2026-10-15, SHA-256
  96:96:16:0B:…:44:91:07), kept by the owner; CI reads the secrets `SIGNING_KEYSTORE_BASE64` and
  `SIGNING_PASSWORD`. Without them CI signs with a throwaway key (updates need uninstalling).
- Add a screenshot of the widget to the README.
