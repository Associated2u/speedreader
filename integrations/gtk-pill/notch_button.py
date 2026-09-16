#!/usr/bin/env python3
"""
readalong button for a custom GTK/cairo pill.

This is the reference integration: a line-drawn glyph with three states,
driven entirely by the readalong CLI and its pidfile. Nothing here knows how
text is read - it only knows how to draw, and which command to spawn.

    left click   -> `readalong --toggle`
    right click  -> `readalong --settings`

Drop into any pill that gives you a cairo context and a click event:

    self.reader = ReaderButton()
    ...in draw():   self.reader.draw(cr, x, pill_h, dim_rgb, green_rgb)
    ...in click():  self.reader.click(secondary=(ev.button == 3))
"""
import os, subprocess, time, math

READER_W = 20                              # pixels the glyph occupies
PIDFILE  = os.path.expanduser("~/.local/state/readalong/reading.pid")
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
            return "reading"
        return "armed" if time.monotonic() < self._armed_until else "idle"

    # ---------------------------------------------------------- actions ---
    def click(self, secondary: bool = False):
        if secondary:
            subprocess.Popen(["readalong", "--settings"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        was_reading = self.reading()
        subprocess.Popen(["readalong", "--toggle"], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # --toggle arms for up to 25 s; show amber for that window unless it
        # was a stop.
        self._armed_until = 0.0 if was_reading else time.monotonic() + 25.0

    # ------------------------------------------------------------- draw ---
    def draw(self, cr, bx, pill_h, dim, green):
        """Play triangle with two sound arcs. Call from your draw handler."""
        st  = self.state()
        col = {"idle": dim, "armed": AMBER, "reading": green}[st]
        cy  = pill_h / 2
        cr.set_source_rgb(*col)
        cr.set_line_width(1.4)

        cr.new_path()
        cr.move_to(bx, cy - 5.5)
        cr.line_to(bx, cy + 5.5)
        cr.line_to(bx + 6.5, cy)
        cr.close_path()
        cr.fill() if st == "reading" else cr.stroke()

        t = time.monotonic()
        for i, r in enumerate((5.0, 8.5)):
            if st == "reading":
                a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 4 - i * 1.1))
            elif st == "armed":
                a = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 3))
            else:
                a = 0.75
            cr.set_source_rgba(*col, a)
            cr.new_sub_path()              # never let a prior text point trail in
            cr.arc(bx + 8.0, cy, r, -0.85, 0.85)
            cr.stroke()
