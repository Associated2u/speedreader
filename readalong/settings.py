#!/usr/bin/env python3
"""
readalong - SETTINGS window.

Right-click the reader button and this opens. Every control writes straight
to ~/.config/readalong/config.json, which is the single source of truth that the
button, the CLI and the voice lab all read - so a change here is live for the
very next read, no restart.

Runs as its own process so that nothing in here can take the pill down.
"""
import os, sys, subprocess, importlib.util
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("reader", os.path.join(HERE, "reader.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

US = "English (America)"
VOICES = [                      # the shortlist the author actually auditioned, winners first
    f"{US}+klatt", f"{US}+Alex", f"{US}+Storm",
    f"{US}", "English (Great Britain)",
    f"{US}+klatt2", f"{US}+klatt3", f"{US}+klatt4", f"{US}+klatt5", f"{US}+klatt6",
    f"{US}+Andy", f"{US}+Michael", f"{US}+Max", f"{US}+Alicia", f"{US}+Gene2",
    f"{US}+Robosoft", f"{US}+Robosoft3", f"{US}+Denis", f"{US}+norbert",
    f"{US}+Tweaky", f"{US}+anikaRobot", f"{US}+whisper",
]
SAMPLE = ("The reader now speaks every word, and the follow-along window "
          "lights each one as it is said.")

def wpm(rate):
    """Linear fit to klatt as MEASURED on 2026-09-04: rate 20->267, 40->329,
    60->395, 80->448, 100->506. Slope 3.0 wpm per rate unit."""
    return int(207 + rate * 3.0)


class Settings(Gtk.Window):
    def __init__(self):
        super().__init__(title="Reader settings")
        self.set_default_size(520, -1)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_keep_above(True)
        self.set_border_width(14)
        self.cfg = R.load_config()
        self._test = None

        grid = Gtk.Grid(column_spacing=14, row_spacing=10)
        self.add(grid)
        row = [0]
        def add(label, widget, hint=None):
            l = Gtk.Label(label=label, xalign=1.0)
            l.get_style_context().add_class("dim-label")
            grid.attach(l, 0, row[0], 1, 1)
            grid.attach(widget, 1, row[0], 2, 1)
            if hint:
                h = Gtk.Label(xalign=0); h.set_markup(f"<small>{hint}</small>")
                h.get_style_context().add_class("dim-label")
                row[0] += 1; grid.attach(h, 1, row[0], 2, 1)
            row[0] += 1
            return widget

        # ---- voice ---------------------------------------------------------
        self.voice = Gtk.ComboBoxText.new_with_entry()
        for v in VOICES: self.voice.append_text(v)
        self.voice.get_child().set_text(self.cfg["voice"])
        vb = Gtk.Box(spacing=6); vb.pack_start(self.voice, True, True, 0)
        t = Gtk.Button(label="Test"); t.connect("clicked", self.on_test)
        vb.pack_start(t, False, False, 0)
        add("Voice", vb, "klatt / Alex / Storm were the three that stayed clear at speed")

        # ---- rate / pitch --------------------------------------------------
        self.rate = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -100, 100, 1)
        self.rate.set_value(self.cfg["rate"]); self.rate.set_hexpand(True)
        self.rate.connect("value-changed", lambda s: self.rate_hint.set_markup(
            f"<small>≈ {wpm(int(s.get_value()))} words per minute</small>"))
        add("Rate", self.rate)
        self.rate_hint = Gtk.Label(xalign=0); self.rate_hint.get_style_context().add_class("dim-label")
        self.rate_hint.set_markup(f"<small>≈ {wpm(self.cfg['rate'])} words per minute</small>")
        grid.attach(self.rate_hint, 1, row[0], 2, 1); row[0] += 1

        self.pitch = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -100, 100, 1)
        self.pitch.set_value(self.cfg["pitch"])
        add("Pitch", self.pitch)

        # ---- style ---------------------------------------------------------
        self.style = {}
        sb = Gtk.Box(spacing=10); first = None
        for name, blurb in (("verbatim", "every word"), ("skim", "2x"),
                            ("structure", "2.4x"), ("gist", "10x")):
            b = Gtk.RadioButton.new_with_label_from_widget(first, f"{name}  ({blurb})")
            first = first or b
            b.set_active(self.cfg["style"] == name)
            self.style[name] = b; sb.pack_start(b, False, False, 0)
        add("Reads", sb, "only <b>verbatim</b> can drive the follow-along window - a skimmed voice leaves the eye nothing to follow")

        # ---- left click ----------------------------------------------------
        self.left = {}
        lb = Gtk.Box(spacing=10)
        a = Gtk.RadioButton.new_with_label(None, "Read aloud")
        p = Gtk.RadioButton.new_with_label_from_widget(a, "Read aloud + follow-along window")
        (p if self.cfg.get("left_click") == "pacer" else a).set_active(True)
        self.left = {"audio": a, "pacer": p}
        lb.pack_start(a, False, False, 0); lb.pack_start(p, False, False, 0)
        add("Left click", lb, "right click always opens this window")

        # ---- toggles -------------------------------------------------------
        tb = Gtk.Box(spacing=16)
        self.redact  = Gtk.CheckButton(label="Redact secrets");  self.redact.set_active(self.cfg.get("redact", True))
        self.earcons = Gtk.CheckButton(label="Earcons");         self.earcons.set_active(self.cfg.get("earcons", True))
        self.code    = Gtk.CheckButton(label="Read code blocks out"); self.code.set_active(self.cfg.get("code") == "speak")
        for w in (self.redact, self.earcons, self.code): tb.pack_start(w, False, False, 0)
        add("", tb)

        # ---- buttons -------------------------------------------------------
        bb = Gtk.Box(spacing=8); bb.set_halign(Gtk.Align.END)
        c = Gtk.Button(label="Cancel"); c.connect("clicked", lambda *_: Gtk.main_quit())
        s = Gtk.Button(label="Save");   s.connect("clicked", self.on_save)
        s.get_style_context().add_class("suggested-action")
        bb.pack_start(c, False, False, 0); bb.pack_start(s, False, False, 0)
        grid.attach(bb, 0, row[0], 3, 1)

        self.connect("destroy", lambda *_: Gtk.main_quit())
        self.connect("key-press-event", lambda w, e: Gtk.main_quit() if e.keyval == Gdk.KEY_Escape else None)

    # ------------------------------------------------------------------ ---
    def values(self):
        return dict(
            voice=self.voice.get_child().get_text().strip() or R.DEFAULTS["voice"],
            rate=int(self.rate.get_value()), pitch=int(self.pitch.get_value()),
            style=next(k for k, b in self.style.items() if b.get_active()),
            left_click=next(k for k, b in self.left.items() if b.get_active()),
            redact=self.redact.get_active(), earcons=self.earcons.get_active(),
            code="speak" if self.code.get_active() else "describe")

    def on_test(self, _b):
        v = self.values()
        if self._test and self._test.poll() is None:
            self._test.terminate()
        self._test = subprocess.Popen(
            ["spd-say", "-o", "espeak-ng", "-y", v["voice"],
             "-r", str(v["rate"]), "-p", str(v["pitch"]), SAMPLE],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def on_save(self, _b):
        cfg = R.save_config(**self.values())
        print(f"saved: {cfg}", file=sys.stderr)
        Gtk.main_quit()


if __name__ == "__main__":
    w = Settings(); w.show_all(); Gtk.main()
