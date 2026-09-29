# -*- coding: utf-8 -*-
"""Make the child-facing delivery copy: dist/MTG2A04_L01_S01/  (index.html + assets/).

The working folder is NOT shippable (raw-WAV clips in .ogg containers, full-size PNGs, the whole
inherited UI kit). This is the "mini-dist" recipe from the revise skill, done on a COPY:
  1. only the files the built HTML actually references are copied (UI kit pruned);
  2. images PNG -> WebP q85 (alpha kept); the card's img_ext and every path are rewritten;
  3. voice clips re-encoded to Opus 16 kbit/s mono (speech) (same .ogg names);
  4. dev-only files never enter the copy (card.json, CHANGES.md, scripts/, engine/, _draft_original/).
Smoke-test the copy afterwards:  DIST=1 python scripts/_shots.py <out>   (serves the dist folder).
"""
import os, re, sys, shutil, subprocess
from PIL import Image

CODE = "MTG2A04_L01_S01"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST = os.path.join(ROOT, "dist", CODE)

def main():
    html = open(os.path.join(ROOT, CODE + ".html"), encoding="utf-8").read()
    if os.path.isdir(DIST):              # empty it rather than rmtree the folder: a shell or an
        for e in os.listdir(DIST):          # explorer window sitting IN it would lock the directory
            q = os.path.join(DIST, e)
            shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    for sub in ("assets/Audio", "assets/Images", "assets/UI"):
        os.makedirs(os.path.join(DIST, sub), exist_ok=True)

    # UI: keep what the HTML names — minus three files that are named but never fetched here:
    # the train art belongs to the inherited train modules this card never mounts, and peeking.webp
    # is the gate bird ONLY when a card sets no CARD.gate (this one sets swifty_gate.webp). The gate
    # <img>'s initial src is pointed at the bird actually used, so nothing requests peeking at load.
    # sw_lg_hint_anim is the mascot of the engine hint OVERLAY, which no module in this game opens.
    SKIP = {"train_spritesheet.webp", "train_still.webp", "peeking.webp", "sw_lg_hint_anim.webp"}
    html = html.replace('id="phaseGateImg" src="assets/UI/peeking.webp"', 'id="phaseGateImg" src="assets/UI/swifty_gate.webp"')
    ui = os.path.join(ROOT, "assets", "UI"); kept_ui = []
    for f in sorted(os.listdir(ui)):
        # Swiftie's head poses are chosen at runtime ("sw_head_" + expr + "_anim.webp"), so their
        # names never appear literally in the HTML - a literal-name prune dropped all of them.
        if (f in html or f.startswith("sw_head_")) and f not in SKIP:
            shutil.copy2(os.path.join(ui, f), os.path.join(DIST, "assets", "UI", f)); kept_ui.append(f)

    # images -> webp
    im_dir = os.path.join(ROOT, "assets", "Images"); n_img = 0
    for f in sorted(os.listdir(im_dir)):
        p = os.path.join(im_dir, f)
        if not os.path.isfile(p): continue
        stem, ext = os.path.splitext(f)
        if ext == ".png" and re.search(r'\b%s\b' % re.escape(stem), html):
            Image.open(p).save(os.path.join(DIST, "assets", "Images", stem + ".webp"), "WEBP", quality=85, method=6)
            n_img += 1
        elif ext == ".svg" and f in html:
            shutil.copy2(p, os.path.join(DIST, "assets", "Images", f))
    html = re.sub(r'(assets/Images/[A-Za-z0-9_]+)\.png', r'\1.webp', html)
    html = html.replace('"img_ext": "png"', '"img_ext": "webp"')

    # audio -> opus 16k mono
    au = os.path.join(ROOT, "assets", "Audio"); n_au = 0
    for f in sorted(os.listdir(au)):
        stem, ext = os.path.splitext(f)
        if ext != ".ogg" or stem not in html: continue
        out = os.path.join(DIST, "assets", "Audio", f)
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(au, f), "-c:a", "libopus",
                            "-b:a", "16k", "-ac", "1", out], capture_output=True, text=True)
        if r.returncode: sys.exit("X  ffmpeg failed on %s: %s" % (f, r.stderr[:200]))
        n_au += 1

    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(html)
    fav = os.path.join(ROOT, "assets", "UI", "favicon.ico")      # browsers ask for /favicon.ico
    if os.path.isfile(fav): shutil.copy2(fav, os.path.join(DIST, "favicon.ico"))
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DIST) for f in fs)
    print("  OK  dist: %d images (webp), %d clips (opus 16k), %d UI files kept" % (n_img, n_au, len(kept_ui)))
    print("  DIST TOTAL %.2f MB (decimal, as verify_bundle counts)  %s" % (tot / 1e6, "UNDER 10MB" if tot < 10e6 else "OVER 10MB !!"))

if __name__ == "__main__":
    main()
