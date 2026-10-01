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

    # sw_lg_hint_anim is the mascot of the engine hint OVERLAY, which no module in this game opens.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ui_skip import UI_SKIP
    SKIP = set(UI_SKIP)
    # UI: keep what the HTML names — minus three files that are named but never fetched here:
    # the train art belongs to the inherited train modules this card never mounts, and peeking.webp
    # is the gate bird ONLY when a card sets no CARD.gate (this one sets swifty_gate.webp). The gate
    # <img>'s initial src is pointed at the bird actually used, so nothing requests peeking at load.
    # round 2i: the gate plays gate_peek/talk/rest; the old 8.5 s swifty_gate.webp is never fetched
    html = html.replace('id="phaseGateImg" src="assets/UI/peeking.webp"', 'id="phaseGateImg" src="assets/UI/gate_peek.webp"')
    SKIP.add("swifty_gate.webp")
    # round 2j: the celebration shows the team GIF (end_swiftee.gif, shipped unchanged); the stock
    # celebrating mascot is never shown, so its <img> starts on the GIF and the old file stays out
    # round 2l: the celebration is the lip-synced sprite (cel_swiftee_sheet.webp); the hidden <img>
    # starts on that sheet, so neither the stock mascot nor the round-2j GIF ships
    html = html.replace('class="end-mascot" src="assets/UI/sw_lg_celebrating_anim.webp"', 'class="end-mascot" src="assets/UI/cel_talk.webp"')
    SKIP.update({"sw_lg_celebrating_anim.webp", "Swiftee-end page gif.gif", "end_swiftee.gif", "cel_swiftee_sheet.webp"})
    ui = os.path.join(ROOT, "assets", "UI"); kept_ui = []
    for f in sorted(os.listdir(ui)):
        if os.path.isdir(os.path.join(ui, f)): continue      # e.g. assets/UI/gif (source sheets)
        # Swiftie's head poses are chosen at runtime ("sw_head_" + expr + "_anim.webp"), so their
        # names never appear literally in the HTML - a literal-name prune dropped all of them.
        if (f in html or f.startswith("sw_head_")) and f not in SKIP:
            if f == "new_landing_swiftee_anim.webp":
                # round 2j: the 1.7 MB landing Swiftie re-encoded at q72 (no visible difference, -0.66 MB)
                # to make room for the team's celebration GIF, which ships byte-for-byte unchanged
                from PIL import ImageSequence
                an = Image.open(os.path.join(ui, f)); fr, ds = [], []
                for fx in ImageSequence.Iterator(an):
                    fr.append(fx.convert("RGBA").copy()); ds.append(fx.info.get("duration") or 40)
                fr[0].save(os.path.join(DIST, "assets", "UI", f), "WEBP", save_all=True, append_images=fr[1:],
                           duration=ds, loop=0, quality=72, method=4)
            else:
                shutil.copy2(os.path.join(ui, f), os.path.join(DIST, "assets", "UI", f))
            kept_ui.append(f)

    # images -> webp
    im_dir = os.path.join(ROOT, "assets", "Images"); n_img = 0
    for f in sorted(os.listdir(im_dir)):
        p = os.path.join(im_dir, f)
        if not os.path.isfile(p): continue
        stem, ext = os.path.splitext(f)
        if ext == ".png" and re.search(r'\b%s\b' % re.escape(stem), html):
            im = Image.open(p)
            # ship at 2x the largest size the game ever draws it: items <= 150 px, Pari <= 410 px,
            # scenes <= 620 px wide on the 1333-px stage
            cap = 1280 if stem.startswith("scn_") else (900 if stem.startswith("pari_") else 400)
            if max(im.size) > cap: im.thumbnail((cap, cap), Image.LANCZOS)
            im.save(os.path.join(DIST, "assets", "Images", stem + ".webp"), "WEBP", quality=85, method=6)
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
        br = "64k" if stem.startswith("sfx_") else "16k"      # sfx are music-like; 16k is for speech
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(au, f), "-c:a", "libopus",
                            "-b:a", br, "-ac", "1", out], capture_output=True, text=True)
        if r.returncode: sys.exit("X  ffmpeg failed on %s: %s" % (f, r.stderr[:200]))
        n_au += 1

    # round 2n: every file the loader waits for must exist in the delivery copy, or the gate would
    # wait on a 404 (it would still open at its 30 s cap, but that is a bug, not a slow network)
    import json as _json
    m = re.search(r'<script type="application/json" id="cardData">(.*?)</script>', html, re.S)
    pre = _json.loads(m.group(1)).get("preload", {})
    missing = [u for u in pre.get("images", []) + pre.get("audio", []) if not os.path.isfile(os.path.join(DIST, u))]
    if missing: sys.exit("X  preload lists files dist does not ship: %s" % missing[:10])
    print("  OK  loader preload: %d images + %d sounds, all present" % (len(pre.get("images", [])), len(pre.get("audio", []))))
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(html)
    fav = os.path.join(ROOT, "assets", "UI", "favicon.ico")      # browsers ask for /favicon.ico
    if os.path.isfile(fav): shutil.copy2(fav, os.path.join(DIST, "favicon.ico"))
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DIST) for f in fs)
    print("  OK  dist: %d images (webp), %d clips (opus 16k), %d UI files kept" % (n_img, n_au, len(kept_ui)))
    print("  DIST TOTAL %.2f MB (decimal, as verify_bundle counts)  %s" % (tot / 1e6, "UNDER 10MB" if tot < 10e6 else "OVER 10MB !!"))

if __name__ == "__main__":
    main()
