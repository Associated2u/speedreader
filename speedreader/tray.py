#!/usr/bin/env python3
"""
SpeedReader system-tray icon.

A standalone tray icon for people who don't have a custom panel/pill. Same
actions as a pill button, driven entirely by the `speedreader` CLI:

    left click        read aloud (start), or stop if already reading
    right click       read along in the follow-along window
    middle click      settings
    hold left (>0.6s) settings

On desktops whose tray only speaks the StatusNotifier protocol (per-button
events don't arrive), it falls back to: left = read aloud, right = a menu
with every action, middle = settings. Quit lives in that menu and in the
Settings window, so it is always reachable.

    speedreader-tray            run it (foreground)
    speedreader-tray --quit     stop a running tray

The glyph fills in and turns green while reading (polled from the CLI's
pidfile), so the tray shows state without any IPC.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import cairo, os, sys, math, subprocess, time, signal, atexit, warnings

# Gtk.StatusIcon is deprecated but is the only X11 API that delivers per-button
# tray clicks; the warnings would only alarm a user, so silence just those.
warnings.filterwarnings("ignore", category=DeprecationWarning)

STATE   = os.path.expanduser("~/.local/state/speedreader")
PIDFILE = os.path.join(STATE, "reading.pid")     # written by the reader
TRAYPID = os.path.join(STATE, "tray.pid")        # so Settings can offer Quit
ICON_PX = 24

# ---------------------------------------------------------------- the glyph --
def _draw(px, reading):
    """▷)) as a pixbuf. Drawn with a light fill AND a dark hairline outline so
    it stays visible on both light and dark panels - a tray pixbuf cannot
    recolour itself to the theme the way a symbolic icon would."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, px, px)
    cr = cairo.Context(s)
    k = px / 24.0
    cx, cy = 7 * k, px / 2
    fill    = (0.30, 0.80, 0.42) if reading else (0.62, 0.65, 0.72)
    outline = (0.08, 0.09, 0.11)

    def triangle():
        cr.move_to(cx - 3 * k, cy - 6 * k)
        cr.line_to(cx - 3 * k, cy + 6 * k)
        cr.line_to(cx + 4 * k, cy)
        cr.close_path()
    # outline pass, then fill/stroke
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgb(*outline); cr.set_line_width(3 * k); triangle(); cr.stroke()
    cr.set_source_rgb(*fill)
    triangle()
    cr.fill() if reading else (cr.set_line_width(1.7 * k), triangle(), cr.stroke())
    for i, r in enumerate((5.5 * k, 9 * k)):
        cr.set_source_rgb(*outline); cr.set_line_width(3 * k)
        cr.new_sub_path(); cr.arc(cx + 2 * k, cy, r, -0.8, 0.8); cr.stroke()
        cr.set_source_rgb(*fill); cr.set_line_width(1.7 * k)
        cr.new_sub_path(); cr.arc(cx + 2 * k, cy, r, -0.8, 0.8); cr.stroke()
    return Gdk.pixbuf_get_from_surface(s, 0, 0, px, px)

# ---------------------------------------------------------------- the tray ---
class Tray:
    def __init__(self):
        os.makedirs(STATE, exist_ok=True)
        with open(TRAYPID, "w") as f:
            f.write(str(os.getpid()))
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
        signal.signal(signal.SIGINT, lambda *_: Gtk.main_quit())
        self.icon = Gtk.StatusIcon()
        self.icon.set_title("SpeedReader")
        self.icon.set_tooltip_text("SpeedReader — left: read · right: read-along · middle: settings")
        self._reading = None
        self._paint(force=True)

        # Precise per-button path (works on X11 / Cinnamon).
        self.icon.connect("button-press-event", self._press)
        self.icon.connect("button-release-event", self._release)
        # StatusNotifier fallback path (GNOME-style trays).
        self.icon.connect("activate", self._activate)
        self.icon.connect("popup-menu", self._popup)

        self._hold_id = None
        self._handled_until = 0.0      # suppresses the SNI signals that echo a press
        GLib.timeout_add(700, self._paint)

    # ---- state --------------------------------------------------------------
    @staticmethod
    def _is_reading():
        try:
            os.kill(int(open(PIDFILE).read()), 0); return True
        except Exception:
            return False

    def _paint(self, force=False):
        r = self._is_reading()
        if force or r != self._reading:
            self._reading = r
            self.icon.set_from_pixbuf(_draw(ICON_PX, r))
        return True

    # ---- actions ------------------------------------------------------------
    @staticmethod
    def _run(*args):
        subprocess.Popen(["speedreader", *args], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def read_audio(self):  self._run("--toggle", "--pacer", "off")
    def read_window(self): self._run("--toggle", "--pacer", "on")
    def settings(self):    self._run("--settings")
    def stop(self):        self._run("--stop")

    def _mark(self): self._handled_until = time.monotonic() + 0.4
    def _echo(self): return time.monotonic() < self._handled_until

    # ---- precise per-button (X11) ------------------------------------------
    def _press(self, _icon, ev):
        if ev.button == 1:
            self._hold_id = GLib.timeout_add(600, self._hold_fire)
        elif ev.button == 2:
            self._mark(); self.settings()
        elif ev.button == 3:
            self._mark(); self.read_window()
        return False

    def _release(self, _icon, ev):
        if ev.button == 1:
            if self._hold_id is not None:
                GLib.source_remove(self._hold_id); self._hold_id = None
                self._mark(); self.read_audio()      # a tap, not a hold
        return False

    def _hold_fire(self):
        self._hold_id = None
        self._mark(); self.settings()                # held long enough
        return False

    # ---- StatusNotifier fallback -------------------------------------------
    def _activate(self, _icon):
        if not self._echo():
            self.read_audio()

    def _popup(self, _icon, button, when):
        if self._echo():
            return
        m = Gtk.Menu()
        for label, cb in (("Read aloud", self.read_audio),
                          ("Read along (window)", self.read_window),
                          ("Settings…", self.settings),
                          ("Stop", self.stop),
                          (None, None),
                          ("Quit SpeedReader", self._quit)):
            if label is None:
                m.append(Gtk.SeparatorMenuItem()); continue
            it = Gtk.MenuItem(label=label)
            it.connect("activate", lambda _w, f=cb: f())
            m.append(it)
        m.show_all()
        m.popup(None, None, Gtk.StatusIcon.position_menu, self.icon, button, when)

    def _cleanup(self):
        try:
            if int(open(TRAYPID).read()) == os.getpid():
                os.unlink(TRAYPID)
        except Exception:
            pass

    def _quit(self, *_):
        Gtk.main_quit()          # atexit does the pidfile cleanup


def main():
    if "--quit" in sys.argv:
        try:
            os.kill(int(open(TRAYPID).read()), 15); print("tray stopped")
        except Exception:
            print("no tray running")
        return
    # one tray at a time
    try:
        os.kill(int(open(TRAYPID).read()), 0)
        print("SpeedReader tray already running", file=sys.stderr); return
    except Exception:
        pass
    Tray()
    Gtk.main()


if __name__ == "__main__":
    main()
