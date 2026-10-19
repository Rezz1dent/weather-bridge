# Unreleased (dev)

Collected on `dev`; becomes the notes of the next published release.

## Breezy Minimal 8.4

- RU: Нажатие на время восхода/заката переключает показ по кругу: ближайшее событие (как раньше) → второе событие (днём восход, ночью закат) → продолжительность светового дня → снова ближайшее. Через 10 секунд показ сам возвращается к обычному (поток KWGT внутри виджета).
- EN: Tapping the sunrise/sunset time cycles what it shows: the next event (as before) → the other event (sunrise by day, sunset by night) → day length → back. It returns to the usual view by itself after 10 seconds (a KWGT flow inside the widget).
- RU/EN: Owner's tweaks from the editor kept: temperature 5 units further left, own SemiBold font file. / Owner's editor tweaks kept.
- RU: Нажатие на левую часть нижней строки больше не открывает календарь. / EN: Tapping the left part of the bottom row no longer opens the calendar.

## Breezy Minimal 8.5

- RU: Часы: часы шрифтом Manrope Bold, минуты — Light (было ExtraBold и ExtraLight). / EN: Clock: hours in Manrope Bold, minutes in Light (were ExtraBold and ExtraLight).

## Breezy Minimal 8.6–8.7

- RU: Часы обычными (не моноширинными) цифрами: минуты стоят сразу за часами, расстояние между цифрами везде одинаковое. Зазор между часами и минутами — глобальная переменная `clock_gap`. / EN: Clock with normal (proportional) digits: the minutes follow the hours, even spacing between digits. The gap between hours and minutes is the global `clock_gap`.
- RU: Часы крупнее (×1,15), минуты шрифтом Manrope ExtraLight, разделительная линия чуть ниже (правки автора в редакторе). / EN: Larger clock (×1.15), minutes in Manrope ExtraLight, divider line a bit lower (owner's tweaks in the editor).

## Breezy Minimal 8.8–8.9

- RU: Зазор между часами и минутами 5 (правка автора). / EN: Gap between hours and minutes 5 (owner's tweak).
- RU: Блоки: температура с иконкой — одна группа, строки 2–3 — два столбца (дата над будильником слева, ветер над прогнозом справа); каждый блок двигается целиком одним смещением. / EN: Blocks: temperature and icon are one group, rows 2–3 are two columns (date over alarm on the left, wind over the forecast on the right); each block moves as a whole with one offset.
