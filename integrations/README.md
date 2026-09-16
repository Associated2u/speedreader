# Wiring SpeedReader to a bar, key, or button

The easiest route is the tray icon (`speedreader-tray`) — see the main
README. This directory is for driving SpeedReader from something you already
run: a hotkey daemon, a status bar, or a custom panel widget.

Everything goes through two commands, so the click model is yours to map:

| your action | command |
|---|---|
| left | `speedreader --toggle` |
| right | `speedreader --toggle --pacer on` |
| middle / hold | `speedreader --settings` |

`--toggle` arms if idle (highlight text or click a window and it starts) and
stops if already reading — one binding covers start and stop. Highlight-first
works too: select text, then trigger, and it reads immediately.

## Keyboard shortcut (any desktop)

Bind a key to `speedreader --toggle`, and another to `speedreader --settings`.
GNOME / Cinnamon: Settings → Keyboard → Shortcuts → Custom.

## sxhkd

```
super + r
    speedreader --toggle
super + shift + r
    speedreader --toggle --pacer on
super + ctrl + r
    speedreader --settings
```

## xbindkeys

```
"speedreader --toggle"
    Mod4 + r
"speedreader --toggle --pacer on"
    Mod4 + shift + r
"speedreader --settings"
    Mod4 + control + r
```

## Waybar

```json
"custom/speedreader": {
    "format": "▷))",
    "on-click": "speedreader --toggle",
    "on-click-right": "speedreader --toggle --pacer on",
    "on-click-middle": "speedreader --settings",
    "tooltip": false
}
```

## Polybar

```ini
[module/speedreader]
type = custom/text
content = ▷))
click-left = speedreader --toggle
click-right = speedreader --toggle --pacer on
click-middle = speedreader --settings
```

## Showing state

While a read is running, `~/.local/state/speedreader/reading.pid` exists and
names the process:

```bash
[ -f ~/.local/state/speedreader/reading.pid ] && echo reading || echo idle
```

## A full example: a button on a custom GTK/cairo panel

`gtk-pill/notch_button.py` is the reference — a line-drawn button with three
states (idle / armed / reading) that animates while speaking and routes all
three mouse buttons through the CLI. It's the shape used by the pill this tool
grew out of. Nothing in it knows how text is read; it only draws and spawns.
The same pattern — spawn the CLI, poll the pidfile for state — fits any custom
bar.
