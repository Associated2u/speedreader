# Working on SpeedReader (for AI coding agents and contributors)

SpeedReader reads text aloud with a word-synced follow-along window. Linux/X11,
Python 3, GTK 3, espeak-ng via speech-dispatcher. **CPU-only, no model, no GPU.**

## Layout

| file | what |
|---|---|
| `speedreader/reader.py` | engine: sources, extraction, redaction, number handling, earcons, the `Speaker`, and the CLI. The single source of truth for config. |
| `speedreader/pacer.py` | the follow-along window (GTK TextView); palette from config. |
| `speedreader/settings.py` | the settings window; writes the config. |
| `speedreader/voice-lab.py` | audition/sweep voices from the terminal. |
| `speedreader/tray.py` | the system-tray icon; drives the CLI. |
| `integrations/gtk-pill/notch_button.py` | reference custom-panel button; drives the CLI. |
| `tests/test_reader.py` | plain-assert tests, no pytest. **Run after every change.** |

## Rules that matter

- **Config is the one source of truth** (`~/.config/speedreader/config.json`,
  keys = `DEFAULTS` in `reader.py`). The tray, pill and CLI must pass only the
  action; never bake a second default into a button, or it silently overrides
  the config (this bug shipped once).
- **The click model is uniform**: left = read / pause-resume, right =
  read-along / stop, middle or hold = settings. `--primary` / `--secondary` /
  `--settings` / `--playpause` / `--stop` are the button-facing commands; they
  branch on whether a read is running (pidfile `~/.local/state/speedreader/
  reading.pid`, plus a `paused` marker).
- **Redaction is best-effort, not a guarantee** — see `docs/SECURITY.md`.
  Adding a pattern to `REDACT` is fine; do not claim it makes redaction
  complete.
- **Every spoken read inserts SSML index marks per word.** That is what makes
  both the pacer highlight and pause work; do not remove them.
- **Verify by running it.** Most bugs here (a fallback the failure mode can't
  reach, a stderr sent to /dev/null, a set-superset used as set-membership)
  passed a read-through and only showed up on a real run. `docs/TRAPS.md` lists
  them.

## Quick check

```bash
python3 tests/test_reader.py        # 10/10
python3 -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('speedreader/*.py')]"
```
