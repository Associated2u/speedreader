# Things that were only found by running it

Every one of these passed a read-through. Recorded so the next person edits
with them in mind.

**A fallback the real failure mode can't reach is not a fallback.** Window
capture tried ImageMagick's `import` and fell back to ffmpeg on a non-zero
exit. `import` wasn't installed, so it raised `FileNotFoundError` and crashed
straight past the fallback. To the user, the button "did nothing".

**Don't send a subprocess's stderr to `/dev/null`.** That is what hid the
crash above — a traceback and a no-op looked identical. It now writes to
`~/.local/state/speedreader/last.log`, and every run logs its *effective*
settings, not its intended ones.

**Two sources of truth, and the wrong one wins silently.** The button once
kept its own style and rate fallbacks and passed them as explicit CLI flags,
which beat the config file. Every setting the voice lab wrote was overridden,
and the only symptom was "it still skims". Config file or nothing — the
button passes only what the click itself decides.

**A D-Bus filter that is right in principle can return a plausible zero.** The
A2DP delay probe filtered transports on `State == "active"`, but the
transport is `idle` until audio flows — and the probe runs before the first
word. It returned 0 with no error, silently disabling sync compensation.

**GTK3 CSS has no `line-height`, and rejects the entire stylesheet** over one
unknown property. The follow-along window refused to build. Line spacing
belongs on the `TextView` (`pixels_above/below_lines`).

**A redactor that only catches the canonical form is the dangerous kind.** The
Telegram-token pattern demanded exactly 35 characters after the colon; a
near-miss walked through while the tool looked like it was working.

**…and a redactor that bleeps your own project names gets switched off.** The
entropy backstop then caught `MyProject-GDD-v1-1`. It now needs a 20+
character *unbroken* alphanumeric run containing a digit. Both directions
have to be tested: secrets caught, legitimate strings surviving.

**`set(c) > set("-: ")` is a strict-superset test**, not "is this only dashes
and colons". It silently dropped every real table row while reading as
correct.

**X11's PRIMARY selection is stale by default.** It holds whatever was last
highlighted, possibly hours ago in another app. An "already highlighted?
read it" shortcut fires on every click unless you remember what you last
acted on. A highlight is auto-read exactly once.

**PRIMARY doesn't update until mouse-up.** So a slow drag-to-highlight would
lose the race to the "you clicked a window" timer. The pointer button mask
(via Xlib) freezes that timer while a button is held.

**Index marks bunch at the end of an utterance.** espeak fires a mark when
the audio *buffer* containing it is submitted, not when it plays, so the
last two or three short words of a sentence light together. Sentence-sized
spans keep this tolerable.

**Compression and pacing are mutually exclusive.** Skimmed audio against full
on-screen text means the highlight jumps over paragraphs the eye is still
reading. Only verbatim can drive the follow-along window.

**Listening speed does not scale like reading speed.** Advising "just turn the
rate up" assumed it did. See WHY-KLATT.md.

**Bluetooth headsets may come up degraded on first connect.** Ray-Ban Meta
glasses paired fine, then connected HFP-only — 16 kHz mono with the mic held
open. A clean disconnect and reconnect produced A2DP at 48 kHz stereo with
the mic released. If your sink reports `1ch 16000Hz`, cycle the connection.
