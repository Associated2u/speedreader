#!/usr/bin/env python3
"""
speedreader button for a custom GTK/cairo pill.

This is the reference integration: a line-drawn glyph with three states,
driven entirely by the speedreader CLI and its pidfile. Nothing here knows how
text is read - it only knows how to draw, and which command to spawn.

    left click    -> `speedreader --primary`   (read aloud; pause/resume if reading)
    right click   -> `speedreader --secondary` (read-along window; stop if reading)
    middle click  -> `speedreader --settings`

Drop into any pill that gives you a cairo context and a click event:

    self.reader = ReaderButton()
    ...in draw():   self.reader.draw(cr, x, pill_h, dim_rgb, green_rgb)
    ...in click():  self.reader.click(button=ev.button)
"""
import os, subprocess, time, math

READER_W = 20                              # pixels the glyph occupies
PIDFILE  = os.path.expanduser("~/.local/state/speedreader/reading.pid")
PAUSEFILE = os.path.expanduser("~/.local/state/speedreader/paused")
AMBER    = (0.95, 0.72, 0.25)


class ReaderButton:
    def __init__(self):
        self._armed_until = 0.0

    # ------------------------------------------------------------ state ---
    @staticmethod
    def reading() -> bool:
        try:
            os.kill(int(open(PIDFILE).read()), 0)
            return True
        except Exception:
            return False

    def state(self) -> str:
        if self.reading():
            self._armed_until = 0.0
            return "paused" if os.path.exists(PAUSEFILE) else "reading"
        return "armed" if time.monotonic() < self._armed_until else "idle"

    # ---------------------------------------------------------- actions ---
    def click(self, button: int = 1):
        cmd = {2: "--settings", 3: "--secondary"}.get(button, "--primary")
        was_active = self.state() != "idle"
        subprocess.Popen(["speedreader", cmd], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._armed_until = (time.monotonic() + 25.0
                             if button == 1 and not was_active else 0.0)

    def draw(self, cr, bx, pill_h, dim, green):
        """Play triangle with two sound arcs. Call from your draw handler."""
        st  = self.state()
        col = {"idle": dim, "armed": AMBER, "reading": green, "paused": AMBER}[st]
        cy  = pill_h / 2
        cr.set_source_rgb(*col); cr.set_line_width(1.4); cr.new_path()
        if st == "reading":                       # pause bars
            cr.rectangle(bx, cy - 5.5, 2.4, 11); cr.fill()
            cr.rectangle(bx + 4.1, cy - 5.5, 2.4, 11); cr.fill()
            return
        if st == "paused":                        # play triangle = resume
            cr.move_to(bx, cy - 5.5); cr.line_to(bx, cy + 5.5)
            cr.line_to(bx + 6.5, cy); cr.close_path(); cr.fill()
            return
        cr.move_to(bx, cy - 5.5); cr.line_to(bx, cy + 5.5)
        cr.line_to(bx + 6.5, cy); cr.close_path(); cr.stroke()
        t = time.monotonic()
        for i, r in enumerate((5.0, 8.5)):
            a = (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 3))) if st == "armed" else 0.75
            cr.set_source_rgba(*col, a)
            cr.new_sub_path()              # never let a prior text point trail in
            cr.arc(bx + 8.0, cy, r, -0.85, 0.85)
            cr.stroke()
