# SpeedReader

Reads text aloud and lights up each word as it's spoken — so your ear sets
the pace and your eye never loses its place.

Point it at anything: a highlighted paragraph, a window, or the newest reply
from Claude Code. It starts talking in about 5 ms and can open a follow-along
window that dims everything except the sentence being read, with a bright
cursor on the exact word.

> **Demo:** _video coming — left-click reads aloud, right-click reads along in
> the window, glasses as the speaker._

## Clicks

However you trigger it — the tray icon, a panel button, a hotkey — the model
is the same:

| action | does |
|---|---|
| **left** | read aloud |
| **right** | read along in the follow-along window |
| **middle**, or **hold** | settings |

Left or right again while it's talking stops it.

## What it does

- **Reads what you point at.** Highlight text and click. Or click first, then
  highlight, or click a window. Highlight always wins.
- **Follow-along window.** Full text, everything dimmed except the live
  sentence, a bright cursor on the current word. Lose your place, look for the
  bright one. Synced to your Bluetooth audio delay (read live from BlueZ) so
  the light lands *with* the sound.
- **Reads Claude Code replies straight from the transcript** — the JSONL on
  disk, not the screen. Clean markdown, exact; `--delta` speaks only what's new.
- **A voice that survives speed.** Defaults to espeak's `klatt`, a formant
  synthesiser from the DECtalk lineage that stays intelligible at 400+ wpm
  where natural-sounding voices smear. Two megabytes, offline, no model.
  [Why](docs/WHY-KLATT.md).
- **Earcons instead of spoken scaffolding** — a tick for a bullet, a thud for
  a code block, a buzz for a warning.
- **Redacts secrets before speaking** — API keys, tokens, credentialed URLs,
  private-key blocks. You hear "anthropic key redacted"; the secret isn't said
  into the room. It's best-effort, not a guarantee — read
  [docs/SECURITY.md](docs/SECURITY.md) before you trust it with anything.
- **Settings in a window** — voice, speed with a live wpm readout, pitch,
  level. Middle-click or hold.

## Install

Linux with X11. Debian, Ubuntu and Mint are tested; anything with
speech-dispatcher and GTK 3 should work.

```bash
sudo apt install speech-dispatcher speech-dispatcher-espeak-ng python3-speechd \
     xclip xdotool x11-utils pulseaudio-utils python3-gi gir1.2-gtk-3.0 python3-xlib
```

Optional, for reading windows that expose no accessibility tree:

```bash
sudo apt install tesseract-ocr ffmpeg
```

Then:

```bash
git clone https://github.com/YOUR-USER/speedreader && cd speedreader && bash install.sh
```

No root. Everything lands in `~/.local`. `bash uninstall.sh` removes it.

## The tray icon

The simplest way to use it — no panel of your own required:

```bash
speedreader-tray
```

An icon appears in your system tray (it fills in and turns green while
reading). Left-click reads, right-click reads along, middle-click or hold
opens settings. Start it every login:

```bash
cp ~/.local/share/applications/speedreader-tray.desktop ~/.config/autostart/
```

On desktops whose tray only speaks the StatusNotifier protocol (some GNOME
setups), per-button clicks may not all arrive; there the tray falls back to
left = read, right = a menu with every action, middle = settings. Quit is in
that menu and in the settings window, so it's always reachable.

## Add it to your panel

The tray works on any desktop with a notification area. To put it on a
specific panel instead:

**Cinnamon / MATE / Xfce** — add a "Notification Area" (or "System Tray")
applet to the panel if you don't have one, then run `speedreader-tray`; the
icon lands in it.

**A launcher button** (runs the reader directly, no tray): most panels let
you add a custom launcher pointing at a command. Use `speedreader --toggle`
for left-click behaviour. Cinnamon: panel → add applets → "Custom Launcher".

**KDE / GNOME** — the tray icon shows in the status area (GNOME needs an
AppIndicator/Tray extension). Or bind the CLI to keys (below).

## Use from the CLI or your own bar

Two commands cover a button of your own:

```bash
speedreader --toggle              # left click: read (audio), or stop if reading
speedreader --toggle --pacer on   # right click: read along in the window
speedreader --settings            # middle / hold: settings
```

Ready-made snippets for sxhkd, xbindkeys, Waybar, Polybar and a custom
GTK/cairo panel button are in [integrations/](integrations/).

More:

```bash
speedreader                  # highlighted text, else newest Claude reply, else window
speedreader claude --delta   # only what Claude has said since you last listened
speedreader --style gist     # headings and warnings only, ~10x — audio-only triage
speedreader --code speak     # read code blocks out instead of summarising them
speedreader ... --dry        # print what it WOULD say, say nothing
speedreader-voices           # audition voices, sweep speeds
```

## The follow-along window

Opens on a right-click, or automatically for anything over 60 words on a
left-click. Everything is dimmed except the sentence being spoken; the current
word gets a bright underlined cursor. Markdown renders — bold is bold, code is
monospace, the markers are hidden — and it scrolls to keep the live line about
a third of the way down. Escape stops it.

The highlight is delayed by the real Bluetooth transport delay, read from
BlueZ at start (about 320 ms on Ray-Ban Meta glasses). Without that the light
runs ahead of the sound.

Only **verbatim** drives the window. A skimmed voice against full on-screen
text leaves the eye nothing to follow; the other levels are for audio-only use.

## Where the text comes from

| source | how | time to first word |
|---|---|---|
| highlighted text | X11 PRIMARY selection | **5 ms** |
| Claude Code reply | `~/.claude/projects/*/*.jsonl` | **5 ms**, exact |
| a window | accessibility tree (AT-SPI) | ~160 ms |
| a window | screenshot + OCR (fallback) | ~800 ms, lossy |

AT-SPI needs accessibility enabled (`gsettings set
org.gnome.desktop.interface toolkit-accessibility true`) **and** the app must
have started since — the bridge loads at launch. Electron apps also need
`--force-renderer-accessibility`. Pointing at the Claude desktop app skips all
that: it reads the transcript instead.

## Config

`~/.config/speedreader/config.json`, written by the settings window and
`speedreader-voices --set`, read by everything:

```json
{"voice": "English (America)+klatt", "rate": 30, "pitch": 0,
 "style": "verbatim", "pacer": "auto",
 "redact": true, "earcons": true, "code": "describe"}
```

Every run logs the settings it actually used to
`~/.local/state/speedreader/last.log`. If it ever behaves oddly, read that
line first.

## Speeds

Measured with `klatt`:

| rate | words / min |
|---|---|
| 20 | 267 |
| 40 | 329 |
| 60 | 395 |
| 80 | 448 |
| 100 | 506 |

## What it will not do

**It will not get you to 8–10x.** Speech is serial: phonemes need roughly
60–80 ms to be told apart, capping intelligible listening around 500–700 wpm
even for trained ears. Fast readers take in whole lines at once; audio can't.
What this gives you is a comfortable hands-free pace with a cursor that keeps
your place — not a speed-reading trainer.

It's X11 and Linux. Wayland has no global selection or window targeting to
build on.

## License

MIT.
