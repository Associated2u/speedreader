# readalong

Reads text aloud and lights up each word as it's spoken — so your ear sets
the pace and your eye never loses its place.

Point it at anything: a highlighted paragraph, a window, or the newest reply
from Claude Code. It starts talking in about 5 ms and opens a follow-along
window that dims everything except the sentence being read, with a bright
cursor on the exact word.

> **Demo:** _video coming — left-click reads, right-click configures, Ray-Ban
> Meta glasses as the speaker._

## What it does

- **Reads what you point at.** Highlight text and press the button. Or press
  first, then highlight, or click a window. Highlight always wins.
- **Follow-along window.** Full text, everything dimmed except the live
  sentence, a bright cursor on the current word. Lose your place, look for
  the bright one. Synced to your Bluetooth audio delay, read live from BlueZ,
  so the light lands *with* the sound.
- **Reads Claude Code replies straight from the transcript.** Not the screen —
  the JSONL on disk. Clean markdown, exact, and `--delta` speaks only what's
  new since last time.
- **A voice that survives speed.** Defaults to espeak's `klatt` — a formant
  synthesiser from the DECtalk lineage that stays intelligible at 400+ wpm
  where natural-sounding voices smear. Two megabytes, offline, no model.
  [Why](docs/WHY-KLATT.md).
- **Earcons instead of spoken scaffolding.** A 90 ms tick for a bullet, a low
  thud for a code block, a buzz for a warning. "Bullet point three, code
  block, bash, five lines" is 2.5 seconds; the tones are 0.3.
- **Redacts secrets before speaking.** API keys, tokens, credentialed URLs,
  private-key blocks. You hear "anthropic key redacted" — the sentence isn't
  lost, the secret isn't said into the room.
- **Settings in a window.** Voice, speed with a live wpm readout, pitch,
  what left-click does. Right-click the button.

## Install

Linux with X11. Debian, Ubuntu and Mint are tested; anything with
speech-dispatcher and GTK3 should work.

```bash
sudo apt install speech-dispatcher speech-dispatcher-espeak-ng python3-speechd \
     xclip xdotool x11-utils pulseaudio-utils python3-gi gir1.2-gtk-3.0 python3-xlib
```

Optional, for windows that expose no accessibility tree:

```bash
sudo apt install tesseract-ocr ffmpeg
```

Then:

```bash
git clone https://github.com/YOUR-USER/readalong && cd readalong && bash install.sh
```

No root. Everything lands in `~/.local`. `bash uninstall.sh` removes it.

## Use

```bash
readalong                  # highlighted text, else newest Claude reply, else focused window
readalong --toggle         # arm (highlight or click a window) — or stop if reading
readalong --settings       # the settings window
readalong-voices           # audition voices, sweep speeds
```

Bind `--toggle` to a key or a bar button and `--settings` to a right-click.
Ready-made snippets for sxhkd, xbindkeys, Waybar, Polybar and a custom GTK
pill are in [integrations/](integrations/).

More:

```bash
readalong claude --delta   # only what Claude has said since you last listened
readalong --style gist     # headings and warnings only, ~10x — audio-only triage
readalong --pacer on       # force the follow-along window
readalong --code speak     # read code blocks out instead of summarising them
readalong ... --dry        # print what it WOULD say, say nothing
```

## The follow-along window

Opens automatically for anything over 60 words (a window for a six-word
highlight is noise). Everything is dimmed except the sentence being spoken;
the current word gets a bright underlined cursor. Markdown renders — bold is
bold, code is monospace, the markers are hidden — and the window scrolls to
keep the live line about a third of the way down. Escape stops it.

The highlight is delayed by the real Bluetooth transport delay, read from
BlueZ at start (about 320 ms on Ray-Ban Meta glasses). Without that the light
runs ahead of the sound and the effect inverts.

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
have been started since — the bridge loads at launch. Electron apps also need
`--force-renderer-accessibility`. Pointing at the Claude desktop app skips
all that: it reads the transcript instead.

## Config

`~/.config/readalong/config.json`, written by the settings window and
`readalong-voices --set`, read by everything:

```json
{"voice": "English (America)+klatt", "rate": 30, "pitch": 0,
 "style": "verbatim", "pacer": "auto", "left_click": "audio",
 "redact": true, "earcons": true, "code": "describe"}
```

Every run logs the settings it actually used to
`~/.local/state/readalong/last.log`. If it ever behaves oddly, read that line
first.

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
60–80 ms to be told apart, which caps intelligible listening somewhere around
500–700 wpm even for trained ears. Fast readers take in whole lines at once;
audio physically can't. What this gives you is a comfortable hands-free pace
with a cursor that keeps your place — not a speed-reading trainer. Reaching
real reading speed would need the audio to become a metronome and the eye to
do the work; that isn't built.

It's X11 and Linux. Wayland has no global selection or window targeting to
build on.

## License

MIT.
