# -*- coding: utf-8 -*-
"""Split the transition bird (assets/UI/swifty_gate.webp, 84 frames / 8.5 s) into three pieces so the
gate can be short and the mouth can follow the VO exactly (user, 2026-09-30):

  gate_peek.webp  — ONE continuous rise, played once (frames 0-19 + 36-53: the half-way pause and the
                    second rise are cut). Ends on her full, eyes-open, mouth-closed frame.
  gate_talk.webp  — a mouth open/close loop (frames 66-71: closed/open alternating, eyes open), looped
                    for as long as the gate VO plays — so the mouth moves exactly while the voice does.
  gate_rest.webp  — her mouth-closed still, shown when the VO ends.

Frame analysis (mouth-open frames = fewer beak-orange pixels): open 58, 60, 67, 69, 71, 74, 76.
Run: python scripts/make_gate_bird.py
"""
import os
from PIL import Image, ImageSequence

UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "UI")
src = Image.open(os.path.join(UI, "swifty_gate.webp"))
frames, durs = [], []
for f in ImageSequence.Iterator(src):
    durs.append(f.info.get("duration") or 40)
    frames.append(f.convert("RGBA").copy())
assert len(frames) == 84, len(frames)

def save(name, idx, dur=None, loop=0):
    fs = [frames[i] for i in idx]
    ds = [dur or max(20, durs[i]) for i in idx]
    fs[0].save(os.path.join(UI, name), "WEBP", save_all=len(fs) > 1, append_images=fs[1:], duration=ds,
               loop=loop, quality=72, method=4)
    return sum(ds)

PEEK = list(range(0, 20)) + list(range(36, 54))
peek_ms = save("gate_peek.webp", PEEK, loop=1)            # loop=1 -> plays once, holds the last frame
talk_ms = save("gate_talk.webp", [66, 67, 68, 69, 70, 71], dur=115, loop=0)
save("gate_rest.webp", [66])
print("gate_peek.webp  %d frames, %d ms (was 84 frames / %d ms)" % (len(PEEK), peek_ms, sum(durs)))
print("gate_talk.webp  6 frames, %d ms per loop" % talk_ms)
for n in ("gate_peek.webp", "gate_talk.webp", "gate_rest.webp"):
    print("  %-16s %6.0f KB" % (n, os.path.getsize(os.path.join(UI, n)) / 1024))
