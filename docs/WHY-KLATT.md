# Why the default voice is a 1980s robot

speedreader defaults to espeak-ng's `klatt` variant. It sounds like a
computer. That is the point, and it was chosen by ear, not by theory: across
two rounds of auditioning twenty-two voices, only three stayed intelligible
at speed — `klatt`, `Alex` and `Storm` — and `klatt` was clearly the best of
them. The pleasant-sounding ones were the ones that failed.

## The mechanism

Natural speech **coarticulates**: every sound bends toward its neighbours,
so the /t/ in "stop" is acoustically different from the /t/ in "tree". A
listener reconstructs the intended phoneme from context, continuously.
That's cheap at conversational pace and it's exactly what breaks under time
compression — the blending smears phoneme boundaries just when there is less
time to resolve them.

A formant synthesiser does not coarticulate. Every /t/ is **identical, every
time**. The listener stops inferring and starts pattern-matching against a
fixed table. Less work per word, less fatigue per hour, a higher sustainable
rate. Blind users who listen at 400+ wpm overwhelmingly choose
DECtalk-lineage voices over natural-sounding ones for precisely this reason —
the robot is not a compromise they tolerate, it is what makes the speed
possible.

`klatt` is the Klatt cascade formant model — the same family DECtalk came
from, and the voice most people know from Stephen Hawking. Its consonant
transients are sharper and its formant transitions higher-contrast than
espeak's default synthesiser.

## What this predicts

- **More natural is worse, not better.** mbrola (diphone) and Piper (neural)
  both sound nicer than espeak. Both are more natural *because* they
  coarticulate. For fast listening they are the wrong direction. Try them if
  you like, but not on the assumption they are an upgrade.
- **Breathy voices fail first.** `whisper` was unusable — breathiness means
  low consonant energy, exactly backwards.
- **Intonation helps for a different reason.** `Storm` has high pitch
  variance, which marks phrase boundaries. That is prosodic chunking, not
  crispness. Both help, independently.

## The ceiling

Phoneme discrimination needs roughly 60–80 ms per phoneme. That caps
intelligible speech somewhere around 500–700 wpm for trained listeners and
much lower for most. `klatt` at rate 100 measured 506 wpm and was still
clear; there is not a lot of headroom above that for anyone.

Reading has no such ceiling. A practised reader takes in a line or a
paragraph at once, in parallel. Audio is one phoneme after another, in
order, forever. So a text-to-speech tool cannot be a speed-reading trainer,
whatever the voice — the ear is not the vehicle. What it can be is a pacer
that keeps your place while you read at your own speed, which is what
speedreader is.
