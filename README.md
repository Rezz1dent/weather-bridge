# Weather Bridge for KWGT

**Weather Bridge** is a tiny Android app that passes the forecast from
[Breezy Weather](https://github.com/breezy-weather/breezy-weather) to
[KWGT](https://kustom.rocks/) as ready-to-use variables. It makes no network requests and does
not use your location: Breezy fetches the weather, the bridge only forwards it.

The repository also contains **Breezy Minimal**, a KWGT widget built on these variables:
a large clock, temperature and weather icon, then date, wind, precipitation, feels-like, next
alarm, sunrise/sunset and the forecast for today and tomorrow.

![Breezy Minimal on the home screen](docs/images/widget.jpg)

> Independent, unofficial project. Not affiliated with Breezy Weather or Kustom Industries.

[Русская версия](README.ru.md)

## How it works

```
Breezy Weather ──(Update Notifier broadcast)──▶ Weather Bridge ──(reads Breezy's provider)
                                                      │
                                                      └──(KWGT broadcast)──▶ $br(breezy, temp)$
```

Every time Breezy refreshes the weather it notifies the bridge; the bridge reads Breezy's
weather ContentProvider and sends about 40 variables to KWGT. Day/night icons switch at
sunrise and sunset even without a refresh.

## Requirements

- Android 8.0+
- Breezy Weather **6.1.0+** (with its weather ContentProvider)
- KWGT 3.80+ (built-in Material Design Icons)

## Install

1. Download `weather-bridge-*.apk` from [Releases](../../releases) and install it.
   The app has **no launcher icon** on purpose: open it from
   **Settings → Apps → Weather Bridge → Open app settings**, or from Breezy's settings.
2. Tap **Allow access to Breezy Weather**.
3. In Breezy Weather: **Settings → Widgets & live wallpapers → Send weather data to Breezy
   Weather Update Notifier** → enable **Weather Bridge**.
4. Turn off battery restrictions for Weather Bridge and Breezy Weather (button in the app), so
   background updates are not blocked.
5. Refresh the weather in Breezy, or tap **Read Breezy data and send to KWGT**.

The settings screen lists every variable; tap one to copy its formula. Interface: English or
Russian (switch in the top-right corner).

## Breezy Minimal widget

### Install

1. Download `Breezy_Minimal_*.kwgt` (or the `.zip` with it) from [Releases](../../releases) or
   [`widget/`](widget) and open it in KWGT.
2. If the text appears in a standard font instead of Manrope: KWGT has not picked up the fonts
   bundled with the preset yet. Usually it helps to **force stop KWGT** (Settings → Apps → KWGT
   → Force stop) and open it again; if that does not help, restart the phone. Usually this is
   needed only once, after the first import.

### What it shows

**Top row:** clock (hours bold, minutes light), current temperature and weather icon. The icon
is the same one Breezy shows; sun and moon follow the actual sunrise and sunset.

**Middle row, left:** the date. **Right:**
- wind: the arrow points where the wind blows, speed in m/s;
- precipitation now, mm: appears **only while it rains or snows** (current hour of Breezy's
  forecast) and disappears when it is dry; the icon changes by itself: drop for rain,
  snowflake for snow, snowflake with a drop for sleet;
- feels-like temperature (person icon).

**Bottom row, left:**
- next alarm with its weekday (crossed-out icon and "—" when no alarm is set);
- next sunset by day or next sunrise by night (calculated by KWGT for your location).

**Bottom row, right:**
- today's high/low;
- tomorrow's high/low (calendar icon);
- umbrella: appears **only when tomorrow's chance of precipitation reaches the threshold**
  (`umbrella_min`, 60% in the preset), with the chance in % and the expected amount in mm; the
  mm icon also changes for rain, snow and sleet.

The middle and bottom rows pick a larger font when everything fits and a slightly smaller one
when the values get long, so nothing overlaps.

Taps: the weather area opens Breezy Weather; the clock opens the clock app of ColorOS / OnePlus
(on other phones, change the "Ярлык Часов" element's action in KWGT).

### Settings (KWGT → Globals)

| Global | Meaning |
|---|---|
| `umbrella_min` | Umbrella threshold: chance of precipitation tomorrow, %. Preset: 60; 0 means 70 |
| `umbrella_test` | Always show the umbrella (to check how it looks) |
| `maximal` | Fill every row with its longest value, to check for overlaps |
| `precip_test` | Show the precipitation blocks with a given icon: 0 real data, 1 rain, 2 snow, 3 sleet |

With `maximal` on (every row at its longest, smaller font):

![maximal](docs/images/widget-maximal.jpg)

Older versions of the widget are in [`widget/archive`](widget/archive).

## Variables

Use them in KWGT as `$br(breezy, name)$`.

| Group | Variable | Value |
|---|---|---|
| Now | `temp` | Current temperature, ° (for example, 8°) |
| Now | `feels` | Feels-like temperature with a Feels like label |
| Now | `like` | Feels-like temperature in degrees only |
| Now | `condition` | Current weather description from Breezy |
| Now | `code` | Numeric weather condition code (OpenWeather-like) |
| Now | `icon` | Weather emoji |
| Now | `icon_flat` | Glyph name in the Meteo icon font |
| Now | `icon_mdi` | Material Design Icons name, as in Breezy widgets (KWGT icon set: Iconify → mdi) |
| Now | `is_day` | 1 by day, 0 at night (from Breezy hourly data) |
| Now | `humidity` | Relative humidity, % |
| Now | `precip` | Current precipitation probability, % (if available) |
| Now | `precip_now` | Precipitation now, mm (current hour), empty when dry |
| Now | `precip_now_type` | Kind of precipitation now: rain, snow or mix (sleet), empty when dry |
| Now | `precip_now_icon` | Icon for the precipitation now (MDI): water-outline, snowflake, snowflake-melt |
| Now | `details` | Combined text: feels-like, wind arrow, m/s, humidity |
| Wind | `wind` | Wind speed in km/h (English label) |
| Wind | `wind_kmh` | Wind speed in km/h |
| Wind | `wind_ms` | Wind speed in m/s |
| Wind | `wind_direction` | Wind direction (from), compass abbreviation |
| Wind | `wind_degrees` | Wind direction (from), bearing 0–359° |
| Wind | `wind_arrow` | Arrow pointing in the direction the wind blows |
| Wind | `wind_text` | Wind direction (from) + speed in m/s |
| Today | `today_max` | Today's highest temperature, ° |
| Today | `today_min` | Today's lowest temperature, ° |
| Today | `today_range` | Today's high/low, for example 10/7° |
| Today | `today_compact` | Ready-to-use text: Today 10/7° |
| Tomorrow | `tomorrow_max` | Tomorrow's highest temperature, ° |
| Tomorrow | `tomorrow_min` | Tomorrow's lowest temperature, ° |
| Tomorrow | `tomorrow_range` | Tomorrow's high ↑ and low ↓, ° |
| Tomorrow | `tomorrow` | Ready-to-use tomorrow forecast text |
| Tomorrow | `tomorrow_compact` | Ready-to-use text: Tomorrow 8/4° |
| Tomorrow | `tomorrow_precip` | Tomorrow's precipitation probability, % |
| Tomorrow | `tomorrow_precip_mm` | Tomorrow's precipitation, mm (day + night), empty when dry |
| Tomorrow | `tomorrow_precip_type` | Kind of tomorrow's precipitation: rain, snow or mix, empty when dry |
| Tomorrow | `tomorrow_precip_icon` | Icon for tomorrow's precipitation (MDI): water-outline, snowflake, snowflake-melt |
| Tomorrow | `tomorrow_icon` | Tomorrow's weather emoji |
| Tomorrow | `tomorrow_icon_flat` | Tomorrow's Meteo icon glyph name |
| Tomorrow | `tomorrow_icon_mdi` | Tomorrow's Material Design Icons name (Iconify → mdi) |
| Other | `location` | Location name from Breezy |

Notes:
- `precip_now_type` / `tomorrow_precip_type`: Breezy reports rain, snow and ice separately (snow
  in mm of water); the smaller of rain and snow counts from a quarter of the sum, a quarter of
  ice makes it `mix`; a source without the split gives `rain`.
- `icon_mdi`, `tomorrow_icon_mdi`, `precip_now_icon`, `tomorrow_precip_icon`: names from
  [Material Design Icons](https://pictogrammers.com/library/mdi/). In KWGT choose the icon set
  **Iconify → Material Design Icons (mdi)** and use e.g. `$br(breezy, icon_mdi)$`.
  Icon fonts bundled inside a preset do not work on the home screen, so the bridge relies on
  icon sets built into KWGT.

## Troubleshooting

**Breezy says "no compatible packages" / does not list the bridge.** Breezy does not declare its
own Update Notifier in its manifest `<queries>`, so on Android 11+ it sees the bridge only after
the bridge has read its data. The bridge does that on boot and after an update. If Breezy still
does not list it: open the bridge, tap **Read Breezy data and send to KWGT**, close Breezy
completely, reopen its settings and enable the bridge again.

**The widget shows old data.** Check battery restrictions (step 4) and the "Data received"
time on the bridge's screen.

## Build

```
./gradlew :app:assembleRelease
```

GitHub Actions builds the APK on every push (artifact `weather-bridge-apk`). When `main` gets a
new `versionName`, it publishes the release `v<version>` with the APK and the current widget
(notes from `docs/release-notes/v<version>.md`). Releases are signed with the owner's key from the repository secrets
`SIGNING_KEYSTORE_BASE64` (the keystore, base64) and `SIGNING_PASSWORD` (key alias
`weatherbridge`). Without them, e.g. in a fork, the APK is signed with a throwaway debug key and
Android will not update it in place.

## Repository

| Path | Contents |
|---|---|
| [`app/`](app) | Weather Bridge, Android app (Java, no dependencies) |
| [`widget/`](widget) | Breezy Minimal KWGT preset, older versions in `archive/` |
| [`scripts/`](scripts) | Python scripts that build the presets and the Manrope fonts |
| [`docs/`](docs) | Project status, KWGT file format notes, TODO, release notes |

## Credits and license

- Weather data: [Breezy Weather](https://github.com/breezy-weather/breezy-weather) (LGPL-3.0)
  and the forecast source chosen in it.
- Icons: [Material Design Icons](https://pictogrammers.com/library/mdi/) by Pictogrammers,
  Apache License 2.0, provided by KWGT; the bridge only sends icon names.
- Font: [Manrope](https://github.com/sharanda/manrope) by Mikhail Sharanda, SIL Open Font
  License 1.1 ([`widget/OFL-Manrope.txt`](widget/OFL-Manrope.txt)); the preset bundles
  versions modified by `scripts/make_manrope_fonts.py`.
- The project started in a fork of [LeanBitLab/Lwidget](https://github.com/LeanBitLab/Lwidget).

Weather Bridge is licensed under the [GNU General Public License v3.0](LICENSE).
