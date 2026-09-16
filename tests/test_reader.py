#!/usr/bin/env python3
"""
speedreader tests. Plain asserts, no pytest needed:  python3 tests/test_reader.py
(pytest picks them up too.)

These are the checks that found real bugs during development. Each one is
here because the code once passed a read-through and failed this.
"""
import os, sys, json, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "reader", os.path.join(HERE, "..", "speedreader", "reader.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

DOC = """## A heading here

A paragraph with **bold inside** that runs on for a second sentence too.

- A bullet with **a bold bit** and a long tail that must not be cut off
- Second bullet, also complete

| level | speed |
|---|---|
| gist | ten times |

```bash
echo hello
```
"""

def test_verbatim_keeps_every_word():
    spans = list(R.extract(DOC, "verbatim"))
    spoken = " ".join(t for _, t, _, _ in spans)
    assert "long tail that must not be cut off" in spoken, "bullet was truncated"
    assert "Second bullet, also complete" in spoken
    assert "gist, ten times" in spoken, "table row dropped"
    assert not any("---" in t for _, t, _, _ in spans), "separator row spoken"
    assert any(k == "code" for k, *_ in spans)

def test_offsets_point_at_source():
    for kind, text, a, b in R.extract(DOC, "verbatim"):
        src = DOC[a:b]
        assert a < b and src.strip(), f"empty source for {text!r}"
        first = text.split()[0].strip(",.")
        assert first.lower() in R._clean(src).lower(), f"{text!r} not in source[{a}:{b}]"

def test_levels_are_ordered():
    words = lambda lv: sum(len(t.split()) for _, t, _, _ in R.extract(DOC, lv))
    v, s, st, g = (words(l) for l in ("verbatim", "skim", "structure", "gist"))
    assert v >= s >= st >= g, (v, s, st, g)
    assert g < v

def test_tokens_strip_markup_keep_offsets():
    src = "Run `pactl list` and see **the a2dp-sink** profile [here](http://x) now."
    toks = R.Speaker._tokens(src, 0, len(src))
    spoken = [t for t, _, _ in toks]
    assert spoken == ["Run", "pactl", "list", "and", "see", "the", "a2dp-sink",
                      "profile", "here", "now."], spoken
    for t, a, b in toks:
        assert R._clean(src[a:b]) == t, (t, src[a:b])
    assert "<mark name=\"0\"/>Run" in R.Speaker._ssml(toks)
    assert "&" not in R.Speaker._ssml([("a&b", 0, 3)]).replace("&amp;", "")

def test_redaction_catches_secrets():
    for t in ["8412345678:AAHfakefakefakefakefakefakefakefake1",
              "token AKIAIOSFODNN7EXAMPLE here",
              "sk-ant-api03-abcdefghijklmnopqrstuvwxyz012345",
              "ftp://user:hunter2@host.example/path",
              "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----"]:
        out, n = R.redact(t)
        assert n >= 1, f"LEAKED: {t!r}"
        assert "redacted" in out

def test_redaction_spares_prose():
    for t in ["MyProject-GDD-v1-1", "bluez_output.98_59_49_F2_0D_ED.1",
              "/home/user/speedreader/speedreader/pacer.py", "kernel 7.0.0-31-generic",
              "Qwen3-Next-80B-A3B-Instruct", "wireplumber 0.4.17-1ubuntu4.1",
              "commit e836acb on origin/main"]:
        out, n = R.redact(t)
        assert n == 0, f"FALSE POSITIVE: {t!r} -> {out!r}"

def test_config_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        R.CONFIG = os.path.join(d, "config.json")
        cfg = R.save_config(voice="English (America)+Alex", rate=55, bogus="ignored")
        assert cfg["voice"] == "English (America)+Alex" and cfg["rate"] == 55
        assert "bogus" not in cfg
        assert R.load_config()["rate"] == 55
        assert R.load_config()["style"] == R.DEFAULTS["style"]

def test_config_schema():
    # the click model is fixed (left=audio, right=window, middle/hold=settings),
    # so there is no left_click key; guard against it creeping back.
    assert "left_click" not in R.DEFAULTS
    assert set(R.DEFAULTS) == {"voice", "rate", "pitch", "style", "pacer",
                               "redact", "earcons", "code", "numbers",
                               "win_bg", "win_text", "win_live",
                               "win_sentence", "win_word"}
    assert set(R.PRESETS) == {"easy", "medium", "fast", "superfast"}
    assert R.DEFAULTS["voice"].endswith("+klatt")
    assert R.DEFAULTS["style"] == "verbatim"

def test_numbers():
    R.NUM_MODE = "skip"
    keep = {"$5,000,000", "2026", "42", "98%", "GPT-4", "COVID-19", "mp3"}
    drop = {"10240", "1.0.5", "98:59:49", "e3b0c44298fc", "5,000,000"}
    for w in keep:
        assert R._speak_number_token(w) == w, f"should keep {w}"
    for w in drop:
        assert R._speak_number_token(w) is None, f"should drop {w}"
    R.NUM_MODE = "normal"
    assert R._speak_number_token("10240") == "10240"
    R.NUM_MODE = "digits"
    assert R._speak_number_token("10240") == "1 0 2 4 0 "
    R.NUM_MODE = "skip"
    # a whole span
    assert R._filter_numbers("build 10240 cost $5 in 2026") == "build cost $5 in 2026"

def test_code_mode():
    R.CODE_MODE = "describe"
    d = [t for k, t, *_ in R.extract(DOC, "verbatim") if k == "code"][0]
    assert d.startswith("bash block, 1 line")
    R.CODE_MODE = "speak"
    s = [t for k, t, *_ in R.extract(DOC, "verbatim") if k == "code"][0]
    assert s == "echo hello", s
    R.CODE_MODE = "describe"

if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn(); print(f"  ok    {name}")
        except AssertionError as e:
            failed += 1; print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1; print(f"  ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
