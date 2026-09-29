# -*- coding: utf-8 -*-
"""Currency art for the game.

FRONT faces + every draggable piece = the team's own currency set in assets/Currency/ (Default /
Glow / Lock states), copied to assets/Images/ UNCHANGED under the engine's image keys — the user's
instruction (2026-09-29): "I've added images of the currency so use those".
BACK faces (the deck's recall/identify screens show both sides of the coins, and the set has no
backs) are built below from the SME's own reference photos (deck media).

Gemini will not draw banknotes (finishReason IMAGE_OTHER — counterfeit policy), and the SME supplied
real photos anyway, so the currency is made HERE, deterministically, from those photos:
  * upscale (LANCZOS) + a light unsharp mask,
  * every serial number painted over and re-printed as 000000 (note), every year as 000 (coins),
  * «SPECIMEN» stamped clearly on every face  (deck S2 + S4: "000" printed + SPECIMEN written clearly,
    consistent on every screen),
  * coins cut out on a circular alpha mask; the note keeps its rectangle with rounded corners.
Outputs assets/Images/cur_*.png.   Run: python scripts/make_currency.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "art_refs")
OUT = os.path.join(HERE, "..", "assets", "Images")
FB = r"C:\Windows\Fonts\arialbd.ttf"
FM = r"C:\Windows\Fonts\consolab.ttf" if os.path.exists(r"C:\Windows\Fonts\consolab.ttf") else FB

def font(p, s): return ImageFont.truetype(p, s)

def up(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))

def avg(im, box):
    return tuple(int(v) for v in ImageStat.Stat(im.crop(box).convert("RGB")).median)

def patch(im, box, pad_src=6):
    """cover `box` with the median colour of a frame just outside it (soft-edged)"""
    x0, y0, x1, y1 = box
    ring = [avg(im, (x0 - pad_src, y0, x0, y1)), avg(im, (x1, y0, x1 + pad_src, y1)),
            avg(im, (x0, y0 - pad_src, x1, y0)), avg(im, (x0, y1, x1, y1 + pad_src))]
    col = tuple(sum(c[i] for c in ring) // 4 for i in range(3))
    lay = Image.new("L", im.size, 0)
    ImageDraw.Draw(lay).rounded_rectangle(box, radius=6, fill=255)
    lay = lay.filter(ImageFilter.GaussianBlur(2))
    im.paste(Image.new("RGB", im.size, col), (0, 0), lay)
    return col

def text_c(dr, cx, cy, s, f, fill, stroke=0, sfill=None):
    b = dr.textbbox((0, 0), s, font=f, stroke_width=stroke)
    dr.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), s, font=f, fill=fill,
            stroke_width=stroke, stroke_fill=sfill)

def specimen(im, cx, cy, size, angle, alpha=235):
    """«SPECIMEN» as a stamped overlay: deep red, white keyline, slightly rotated"""
    f = font(FB, size)
    tmp = Image.new("RGBA", (int(size * 7), int(size * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    text_c(d, tmp.width / 2, tmp.height / 2, "SPECIMEN", f, (196, 30, 42, alpha),
           stroke=max(2, size // 9), sfill=(255, 255, 255, alpha))
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))

def coin_mask(im):
    """circle through the non-white bbox of a coin photo on white"""
    g = im.convert("L").point(lambda v: 255 if v < 236 else 0)
    bb = g.getbbox()
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse(bb, fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2)), bb

def finish_coin(im, name):
    im = im.convert("RGBA")
    m, bb = coin_mask(im)
    im.putalpha(m)
    im = im.crop(bb)
    im.save(os.path.join(OUT, name + ".png"))
    print("ok", name, im.size)

USER_SET = {"cur_coin1": "One_Rupee", "cur_coin10": "Ten_Rupee", "cur_note10": "Ten_Rupee_Note"}

def copy_user_set():
    src = os.path.join(HERE, "..", "assets", "Currency")
    for key, stem in USER_SET.items():
        for st, suf in (("Default", ""), ("Glow", "_glow"), ("Lock", "_lock")):
            p = os.path.join(src, "%s_%s.png" % (stem, st))
            if not os.path.isfile(p): raise SystemExit("X  missing team currency file: " + p)
            Image.open(p).save(os.path.join(OUT, key + suf + ".png"))
            print("ok", key + suf, "<-", os.path.basename(p))

def main():
    os.makedirs(OUT, exist_ok=True)
    copy_user_set()
    # ---------------- ₹10 coin, BACK face (from the deck photo) ----------------
    K = 2
    c = up(Image.open(os.path.join(REF, "coin10_both.png")).convert("RGB"), K)
    R = c.crop((228 * K, 12 * K, 430 * K, 216 * K))
    d = ImageDraw.Draw(R)
    yb = ((302 - 228) * K, (179 - 12) * K, (349 - 228) * K, (199 - 12) * K)
    col = patch(R, yb)
    text_c(d, (yb[0] + yb[2]) / 2, (yb[1] + yb[3]) / 2, "000", font(FB, 17 * K),
           tuple(max(0, v - 70) for v in col))
    R = R.convert("RGBA")                      # no SPECIMEN on coins (user, 2026-09-29)
    finish_coin(R, "cur_coin10_back")
    # ---------------- ₹1 coin, BACK face ----------------
    K = 3
    c = up(Image.open(os.path.join(REF, "coin1_both.png")).convert("RGB"), K)
    R = c.crop((168 * K, 4 * K, 310 * K, 141 * K)).convert("RGBA")   # no SPECIMEN on coins
    finish_coin(R, "cur_coin1_back")

if __name__ == "__main__":
    main()
