# Wiring readalong to your own bar, key or button

readalong has no UI of its own beyond the follow-along window and the
settings dialog. It is driven by two commands, so it fits whatever you
already run:

| action | command |
|---|---|
| left click / hotkey | `readalong --toggle` |
| right click | `readalong --settings` |

`--toggle` does the right thing whichever state you are in: if nothing is
reading it **arms** — highlight some text, or click a window, and it starts;
if something is reading it **stops**. One button covers start and stop.

Highlight-first also works: select text, then press the button, and it reads
immediately with no arming step.

## Keyboard shortcut (any desktop)

Bind a key to `readalong --toggle`. On GNOME / Cinnamon that is Settings →
Keyboard → Shortcuts → Custom. For a second key, `readalong --settings`.

## sxhkd

```
super + r
    readalong --toggle
super + shift + r
    readalong --settings
```

## xbindkeys

```
"readalong --toggle"
    Mod4 + r
"readalong --settings"
    Mod4 + shift + r
```

## Waybar

```json
"custom/readalong": {
    "format": "▷))",
    "on-click": "readalong --toggle",
    "on-click-right": "readalong --settings",
    "tooltip": false
}
```

## Polybar

```ini
[module/readalong]
type = custom/text
content = ▷))
click-left = readalong --toggle
click-right = readalong --settings
```

## Showing state

While a read is running, `~/.local/state/readalong/reading.pid` exists and
names the process. A bar that wants a "reading" indicator can test that file:

```bash
[ -f ~/.local/state/readalong/reading.pid ] && echo reading || echo idle
```

## A full example: a button on a custom GTK pill

`gtk-pill/` is the original integration — a drawn button on a
top-of-screen pill written in Python and GTK3. It shows a three-state glyph
(idle / armed / reading), animates while speaking, and routes both mouse
buttons. It is specific to that pill's drawing code, but the shape of it —
spawn the CLI, poll the pidfile for state — transfers to any custom bar.
