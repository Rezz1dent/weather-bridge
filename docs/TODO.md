# Weather Bridge — TODO

## Settings screen

- [x] **Language switch in the top-right corner.** (done in 1.5) Replace the "Language" dropdown at the bottom
  with a small rectangle on the same row as the "Weather Bridge" title, aligned right, showing the
  current language ("EN"). Tapping it opens a short dropdown with "EN / RU". English stays the
  default.

- [x] **Quieter language switch.** (done in 1.6) The "EN ▾" box should not stand out: grey text and grey
  border (like the secondary text), not the blue accent color.

- [x] **Complete setup instructions on the settings screen** (done in 1.6) (both English and Russian strings).
  Replace the short intro ("grant access, then refresh the forecast") with numbered steps:
  1. Allow access to Breezy Weather (button below).
  2. In Breezy Weather: Settings → Widgets & live wallpapers → "Send weather data to Breezy
     Weather Update Notifier" → enable Weather Bridge.
  3. Turn off battery restrictions for Weather Bridge (and Breezy Weather) in the system settings,
     so updates are not blocked in the background; ideally a button that opens that screen.
  4. Refresh the weather in Breezy Weather (or tap "Read Breezy data and send to KWGT").
  If Breezy does not list the bridge in step 2: tap "Read Breezy data and send to KWGT", close
  Breezy completely and reopen its settings.

- [x] **Day/night switch can be late.** (done in 1.6) The re-send at sunrise/sunset uses an inexact
  `AlarmManager.set(RTC)`, which Doze / app standby can delay for hours (seen: moon icon at
  13:00). Consider `setAndAllowWhileIdle(RTC_WAKEUP)` or `setWindow`, and check the status line
  time ("Data received HH:MM") when it happens. Preset v58+ picks sun/moon with KWGT's own
  `ai(isday)`, so the widget no longer depends on it.

- [x] **Outline sun.** (done in 1.6) Send `weather-sunny` (outline, as in Breezy's widget) instead of
  `white-balance-sunny` for a clear day in `icon_mdi`. Preset v60 already swaps it.

## Precipitation

- [x] **Rain / snow / mix.** (done in 1.8) Send the kind of precipitation now and tomorrow
  (`precip_now_type`, `tomorrow_precip_type`: rain / snow / mix) and a matching MDI icon
  (`water-outline`, `snowflake`, `snowflake-melt`), so the widget can swap the drop.

## Launcher icon

- [x] **Install with a launcher icon, hide it from the app.** (done in 2.1: alias
  `com.rezz1dent.weatherbridge.Launcher`, button on the bridge's screen) The bridge should install with a
  normal launcher icon (easy to find right after installing), and its screen gets a button
  "Hide icon from launcher" / «Скрыть иконку из лаунчера» that turns it into what it is now: no
  launcher icon, opened from Android Settings → Apps → Weather Bridge → App settings. Probably
  an `<activity-alias>` with the LAUNCHER category, switched by
  `PackageManager.setComponentEnabledSetting`; the button should become "Show icon" when the
  icon is hidden. Update the README ("no launcher icon" note), the setup text in the app and the
  CI check that currently fails when the APK has a launchable activity.

- [x] **New app icon.** Drafts A/B/C were offered on 2026-10-15; the owner decided to keep the
  current icon. Do not change it.

## Widget visuals (after the features)

The owner finds the visuals the weakest part of Breezy Minimal. Plan: first 2–3 mockups next to the
current widget on his wallpaper, he picks a direction, only then change the preset.

- [ ] **Rhythm and spacing:** one vertical step for clock → line → middle row → bottom row.
- [ ] **Hierarchy by opacity, not colour** (colours were rejected): middle row a bit brighter, bottom row quieter.
- [ ] **Icons vs text:** MDI outline icons matched to Manrope in weight and optical size, aligned to the cap height.
- [ ] **Divider line:** soft fade towards both ends (it is already 1 px, cannot be thinner). Tried a radial
  gradient by hand (2026-10-16): the owner did not like it and turned it off. Reason: it lights up the
  centre, which is empty; the content sits in a left and a right block. Ideas for a mockup: two halves fading
  towards the centre (bright under the blocks), or a gap in the middle.
- [ ] **Temperature block:** proportions of digits, degree sign and weather icon; alignment with the clock.
- [ ] **Optical alignment of the edges:** date vs the clock's first digit, weather icon vs the right column.
- [ ] **Optional backing:** a barely visible translucent rounded shape for busy wallpapers.
