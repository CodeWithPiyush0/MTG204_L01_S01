# -*- coding: utf-8 -*-
"""Inject the MONEY module set + styles into this game's engine copy (engine/lesson_template.html).

The template is the HI02H11_L02_S02 engine (the visual baseline the user named), which already
carries that lesson's train modules — they are inert here because this card never mounts them.

Run:  PYTHONUTF8=1 python engine/inject_money.py      then RE-RUN THE BUILDER (the served HTML is
generated from this template; patching the template alone leaves the game on the old code).
Idempotent: a re-run replaces the previous block instead of stacking a second copy.
"""
import io, os, re, sys

HERE   = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "lesson_template.html")
JS_BEGIN  = "/* == MONEY MODULE SET :: BEGIN (engine_local, MTG2A04_L01_S01) == */"
JS_END    = "/* == MONEY MODULE SET :: END == */"
CSS_BEGIN = "/* == MONEY STYLES :: BEGIN (engine_local, MTG2A04_L01_S01) == */"
CSS_END   = "/* == MONEY STYLES :: END == */"

js  = io.open(os.path.join(HERE, "money_modules.js"), encoding="utf-8").read()
css = io.open(os.path.join(HERE, "money_styles.css"), encoding="utf-8").read()
src = io.open(ENGINE, encoding="utf-8").read()

# a literal closing tag anywhere in a source — even inside a comment — ends the host element there
for name, txt, bad in (("money_styles.css", css, "</" + "style>"), ("money_modules.js", js, "</" + "script>")):
    if bad in txt:
        ln = txt[:txt.find(bad)].count("\n") + 1
        sys.exit("X  %s line %d contains a literal %s — it would truncate the host element" % (name, ln, bad))

def strip(s, a, b):
    i, j = s.find(a), s.find(b)
    if i >= 0 and j > i:
        j += len(b)
        while i > 0 and s[i - 1] == "\n": i -= 1
        return s[:i] + "\n" + s[j:].lstrip("\n")
    return s
src = strip(src, JS_BEGIN, JS_END)
src = strip(src, CSS_BEGIN, CSS_END)

# JS: after the LAST SlideModules registration so SlideModules and every helper already exist
anchor = "/* == TRAIN MODULE SET :: END == */"
at = src.find(anchor)
if at < 0:
    aliases = list(re.finditer(r"SlideModules\.[A-Z_0-9]+\s*=\s*SlideModules\.[A-Z_0-9]+;", src))
    if not aliases: sys.exit("X  no injection point for the JS")
    at = aliases[-1].end()
else:
    at += len(anchor)
src = src[:at] + "\n\n" + JS_BEGIN + "\n" + js + "\n" + JS_END + "\n" + src[at:]

# CSS: before the LAST closing style tag so these rules win on equal specificity
close = "</" + "style>"
i = src.rfind(close)
if i < 0: sys.exit("X  no closing style tag")
src = src[:i] + "\n" + CSS_BEGIN + "\n" + css + "\n" + CSS_END + "\n" + src[i:]

io.open(ENGINE, "w", encoding="utf-8").write(src)
out = io.open(ENGINE, encoding="utf-8").read()
mods = ["MONEY_SHOW", "MONEY_PICK", "MONEY_SCENE", "MONEY_LIST", "MONEY_BUILD", "MONEY_DONE", "SHOP_GAME"]
print("engine:", os.path.basename(ENGINE), "%.0f KB" % (len(out.encode("utf-8")) / 1024))
for m in mods:
    print("   %-12s registered: %s" % (m, ("SlideModules." + m + " = {") in out))
print("   injected once:", out.count(JS_BEGIN) == 1 and out.count(CSS_BEGIN) == 1)
