# -*- coding: utf-8 -*-
"""Import the team's art (2026-09-29) into assets/Images under the engine's keys.

Sources live in assets/Team_art_source/ (the ChatGPT sheets the user added). The object sheets hold
2–4 items each on transparency; they are split on the transparent COLUMNS between items (alpha
projection), each item cropped to its own bbox + a small pad, and saved under the key the card uses.
The two scenes are opaque 16:9 paintings, saved as-is (downscaled to 1600 px wide).

Replaces the Gemini versions of: obj_copy/chips/chocolate/plates/toffee/juice, obj_apple/bananas/
carrots/tomatoes/grapes/oranges. obj_cucumbers + obj_mangoes are NOT in the team set -> unchanged.
Run: python scripts/import_team_art.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "Team_art_source")
OUT = os.path.join(HERE, "..", "assets", "Images")

SHEETS = {
    "ChatGPT Image Sep 29, 2026, 04_51_25 PM.png": ["obj_copy", "obj_chips", "obj_chocolate"],
    "ChatGPT Image Sep 29, 2026, 04_55_07 PM.png": ["obj_plates", "obj_toffee", "obj_juice"],
    "ChatGPT Image Sep 29, 2026, 05_01_45 PM.png": ["obj_apple", "obj_bananas", "obj_carrots", "obj_tomatoes"],
    "ChatGPT Image Sep 29, 2026, 05_01_53 PM.png": ["obj_grapes", "obj_oranges"],
}
SCENES = {   # round 2d (2026-09-29 evening): the new cover + market replace the morning versions
    "ChatGPT Image Sep 29, 2026, 11_37_55 PM.png": "scn_landing",   # 11:37 PM cover: Pari on the RIGHT
    "ChatGPT Image Sep 29, 2026, 10_34_28 PM.png": "scn_market",
}
A_MIN = 40        # alpha counted as "ink"
GAP = 12          # empty columns that separate two items
MAX_SIDE = 640

def segments(im):
    w, h = im.size
    a = im.getchannel("A").point(lambda v: 255 if v >= A_MIN else 0)
    cols = [a.crop((x, 0, x + 1, h)).getbbox() is not None for x in range(w)]
    segs, start, empty = [], None, 0
    for x, ink in enumerate(cols + [False] * (GAP + 1)):
        if ink:
            if start is None: start = x
            empty = 0
        elif start is not None:
            empty += 1
            if empty > GAP:
                segs.append((start, x - empty + 1)); start, empty = None, 0
    return segs, a

def main():
    for f, keys in SHEETS.items():
        im = Image.open(os.path.join(SRC, f)).convert("RGBA")
        segs, a = segments(im)
        # tiny specks (stray halo pixels) are not items
        segs = [s for s in segs if s[1] - s[0] > 60]
        if len(segs) != len(keys):
            raise SystemExit("X  %s: found %d items, expected %d (%s)" % (f, len(segs), len(keys), segs))
        for (x0, x1), key in zip(segs, keys):
            bb = a.crop((x0, 0, x1, im.height)).getbbox()
            box = (x0 + bb[0], bb[1], x0 + bb[2], bb[3])
            it = im.crop(box)
            pad = int(0.04 * max(it.size))
            canvas = Image.new("RGBA", (it.width + 2 * pad, it.height + 2 * pad), (0, 0, 0, 0))
            canvas.alpha_composite(it, (pad, pad))
            canvas.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            canvas.save(os.path.join(OUT, key + ".png"))
            print("ok %-14s %s  <- %s" % (key, canvas.size, f[-15:]))
    for f, key in SCENES.items():
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(os.path.join(OUT, key + ".png"))
        print("ok %-14s %s  <- %s" % (key, im.size, f[-15:]))

if __name__ == "__main__":
    main()
