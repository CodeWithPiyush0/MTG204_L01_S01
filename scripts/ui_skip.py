# -*- coding: utf-8 -*-
"""UI files named somewhere in the inherited engine but never used by this game. Shared by the
builder (the loader's preload list) and make_dist.py (what ships), so the two can never disagree."""
UI_SKIP = {"train_spritesheet.webp", "train_still.webp", "peeking.webp", "sw_lg_hint_anim.webp",
           "swifty_gate.webp", "sw_lg_celebrating_anim.webp", "Swiftee-end page gif.gif",
           "end_swiftee.gif", "cel_swiftee_sheet.webp", "favicon.ico"}

def ui_files(ui_dir, html):
    """the assets/UI files the game really uses: named in the page (or a runtime Swiftie pose)"""
    import os
    out = []
    for f in sorted(os.listdir(ui_dir)):
        if os.path.isdir(os.path.join(ui_dir, f)) or f in UI_SKIP: continue
        if f in html or f.startswith("sw_head_"): out.append(f)
    return out
