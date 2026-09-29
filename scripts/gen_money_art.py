# -*- coding: utf-8 -*-
"""Generate the art for MTG2A04_L01_S01 (currency, Pari, shopping items) with Gemini image.

Why a local generator and not gen_objects.py: the currency and Pari are REDRAWN FROM THE SME'S OWN
REFERENCE PICTURES (the deck's ₹10 note / coin photos and the landing mockup's Pari), so the model
needs image inputs; gen_objects.py is text-only. The keying pipeline (flat chroma bg -> flood key
-> keep largest blob -> autocrop) is the same one gen_objects uses, imported from it.

Chroma choice per asset: Pari wears a PINK dupatta, which fights a magenta key, so she is painted
on flat GREEN. Everything else is on magenta (cucumbers are green — magenta is right for them).

Key: GEMINI_KEY / GKEY from the environment, else read from ../.env (never printed).
Usage:  PYTHONUTF8=1 python scripts/gen_money_art.py [--only key1,key2] [--force]
"""
import os, sys, io, json, time, base64, argparse, urllib.request, urllib.error
from collections import deque
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT  = os.path.join(ROOT, "assets", "Images")
REFS = os.path.join(ROOT, "scripts", "art_refs")
MODEL = "gemini-2.5-flash-image"

sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "skills", "swiftpal-game-revise", "scripts"))
from gen_objects import keyout_magenta, keep_largest, autocrop   # noqa: E402

FLAT = (" Flat vector illustration for a children's learning app. Bold rounded dark outline, bright "
        "cheerful flat colours, simple friendly rounded shapes, soft highlights. ONE single subject, "
        "centred, filling most of the frame. NO shadow, NO ground line, NO extra objects.")
BG = {"magenta": " The background must be a PERFECTLY FLAT, UNIFORM, SINGLE solid pure magenta #FF00FF "
                 "fill — no texture, no gradient, no lighting variation, edge to edge.",
      "blue":    " The background must be a PERFECTLY FLAT, UNIFORM, SINGLE solid pure blue #0000FF "
                 "fill — no texture, no gradient, no lighting variation, edge to edge.",
      "green":   " The background must be a PERFECTLY FLAT, UNIFORM, SINGLE solid pure green #00FF00 "
                 "fill — no texture, no gradient, no lighting variation, edge to edge."}
# CHROMA PER ITEM: Gemini's "magenta" arrives as raspberry (222,46,113) — measured on the first apple —
# which is within keying distance of every red object. Green is the default; carrots and cucumbers
# (orange / green) go on blue.

CUR = (" Clean, crisp, high-resolution flat illustration of Indian currency for a Grade-2 maths app — "
       "recognisable as the real design (same colours, layout and main motifs) but simplified. ")
SPEC_NOTE = (" Both serial numbers must read exactly 000000. The word SPECIMEN must be printed clearly in "
             "bold capital letters across the middle of the note.")
SPEC_COIN = (" Where the year is normally printed, print 000 instead. The word SPECIMEN must be printed "
             "clearly in small bold capital letters on the coin face.")

PARI = ("The girl character in the reference picture: an Indian schoolgirl with two dark braids, a small "
        "bindi, big brown eyes, a yellow kurta with small orange flowers, pink salwar, a bright pink dupatta "
        "and a teal cross-body bag. Draw EXACTLY this same character (same face, hair, outfit, colours and "
        "art style), full body, standing, facing the viewer. ")

# key -> (prompt, [reference files], chroma)
ART = {
  # ---------------- currency: NOT generated here ----------------
  # Gemini refuses banknotes (finishReason IMAGE_OTHER). The six cur_* faces are built from the SME's
  # own photos by scripts/make_currency.py instead.
  # ---------------- Pari ----------------
  "pari_list":         (PARI + "She smiles and holds up a tall paper shopping list showing small pictures of "
                        "chips, a juice box, a toffee, a cake and plates, exactly as in the reference.",
                        ["pari_ref.png"], "green"),
  "pari_basket":       (PARI + "She smiles and holds an EMPTY red plastic shopping basket in front of her with "
                        "both hands.", ["pari_ref.png"], "green"),
  "pari_basket_full":  (PARI + "She is very happy, one arm raised in joy, holding a red shopping basket full of "
                        "fruits and vegetables (apple, bananas, carrots, grapes, mangoes).",
                        ["pari_ref.png"], "blue"),
  # ---------------- shopping items (practice screens) ----------------
  "obj_copy":      ("A school exercise notebook (कॉपी) with a plain orange cover and a white label, slightly angled", [], "green"),
  "obj_chips":     ("A puffy packet of potato chips, yellow and red packet with a picture of chips, no brand name or letters", [], "green"),
  "obj_chocolate": ("A chocolate bar, half unwrapped, brown chocolate squares showing from a purple wrapper, no letters", [], "green"),
  "obj_plates":    ("A packet of round white paper party plates stacked inside a clear plastic wrapper", [], "green"),
  "obj_toffee":    ("Three wrapped toffees with twisted ends, in orange, green and blue wrappers, grouped together", [], "green"),
  "obj_juice":     ("A small orange juice box with a straw, a picture of an orange on it, no letters", [], "green"),
  # ---------------- shop game items (mastery) ----------------
  "obj_apple":     ("One shiny red apple with a green leaf", [], "green"),
  "obj_bananas":   ("A bunch of four ripe yellow bananas", [], "green"),
  "obj_carrots":   ("A bunch of three orange carrots with green leafy tops", [], "blue"),
  "obj_tomatoes":  ("Three round red tomatoes with green stems, grouped together", [], "green"),
  "obj_grapes":    ("A bunch of purple grapes with a green leaf", [], "green"),
  "obj_oranges":   ("Three round orange fruits (oranges) with a green leaf, grouped together", [], "green"),
  "obj_cucumbers": ("Two green cucumbers lying side by side", [], "blue"),
  "obj_mangoes":   ("Two ripe yellow-orange mangoes with a green leaf", [], "green"),
}

def get_key():
    k = os.environ.get("GEMINI_KEY") or os.environ.get("GKEY") or os.environ.get("GEMINI_API_KEY")
    if k: return k.strip()
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                n, v = line.split("=", 1)
                if n.strip() in ("GEMINI_KEY", "GKEY", "GEMINI_API_KEY") and v.strip():
                    return v.strip().strip('"').strip("'")
    sys.exit("no Gemini key in env or .env")

def is_green(px):
    r, g, b, a = px
    if a == 0: return True
    return g >= 105 and r <= g - 45 and b <= g - 45

def keyout(im, test):
    im = im.convert("RGBA"); w, h = im.size; data = list(im.getdata()); vis = bytearray(w * h); dq = deque()
    for x in range(w):
        for i in (x, (h - 1) * w + x):
            if not vis[i] and test(data[i]): vis[i] = 1; dq.append(i)
    for y in range(h):
        for i in (y * w, y * w + w - 1):
            if not vis[i] and test(data[i]): vis[i] = 1; dq.append(i)
    while dq:
        i = dq.popleft(); data[i] = (0, 0, 0, 0); x = i % w; y = i // w
        for j in ((i-1) if x > 0 else -1, (i+1) if x < w-1 else -1, (i-w) if y > 0 else -1, (i+w) if y < h-1 else -1):
            if j >= 0 and not vis[j]:
                vis[j] = 1
                if test(data[j]): dq.append(j)
    im.putdata(data)
    # de-fringe: soften the green spill on the one-pixel rim
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and g > max(r, b) + 60:
                px[x, y] = (r, max(r, b), b, a)
    return im

def keyout_dist(im, tol_flood=120, tol_global=62):
    """Key by DISTANCE from the sampled background colour, not by a hue rule: Gemini's 'flat'
    chroma drifts (the first apple got a raspberry cloud a hue rule could not see). Flood from the
    edges at a loose tolerance, then clear enclosed pockets that are very close to the bg colour."""
    im = im.convert("RGBA"); w, h = im.size; px = im.load()
    cs = [px[x, y] for x in (2, w - 3) for y in (2, h - 3)] + [px[w // 2, 2], px[w // 2, h - 3], px[2, h // 2], px[w - 3, h // 2]]
    bg = tuple(sorted(c[i] for c in cs)[len(cs) // 2] for i in range(3))
    d2 = lambda c: (c[0]-bg[0])**2 + (c[1]-bg[1])**2 + (c[2]-bg[2])**2
    tf, tg = tol_flood ** 2, tol_global ** 2
    vis = bytearray(w * h); dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if d2(px[x, y]) < tf: vis[y*w+x] = 1; dq.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not vis[y*w+x] and d2(px[x, y]) < tf: vis[y*w+x] = 1; dq.append((x, y))
    while dq:
        x, y = dq.popleft(); px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < w and 0 <= ny < h and not vis[ny*w+nx]:
                vis[ny*w+nx] = 1
                if d2(px[nx, ny]) < tf: dq.append((nx, ny))
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[3] and d2(c) < tg: px[x, y] = (0, 0, 0, 0)
    # rim de-spill: pull a bg-tinted edge pixel toward neutral
    return im

def call(key, prompt, refs):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    parts = []
    for rf in refs:
        with open(os.path.join(REFS, rf), "rb") as f:
            parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(f.read()).decode()}})
    parts.append({"text": prompt})
    body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.load(r)
    for p in resp["candidates"][0]["content"]["parts"]:
        d = p.get("inlineData") or p.get("inline_data")
        if d: return base64.b64decode(d["data"])
    raise RuntimeError("no image in response: " + json.dumps(resp)[:300])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    key = get_key(); os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.join(OUT, "_raw"), exist_ok=True)
    keys = a.only.split(",") if a.only else list(ART)
    fails = []
    for k in keys:
        prompt, refs, chroma = ART[k]
        dst = os.path.join(OUT, k + ".png")
        if os.path.exists(dst) and not a.force:
            print("skip", k); continue
        full = prompt + ("" if k.startswith("cur_") else FLAT) + BG[chroma] + " No text other than what is asked for."
        ok = False
        for t in range(1, 4):
            try:
                raw = call(key, full, refs)
                open(os.path.join(OUT, "_raw", k + ".png"), "wb").write(raw)
                im = Image.open(io.BytesIO(raw)).convert("RGBA"); im.thumbnail((900, 900))
                im = keyout_dist(im)
                im = autocrop(keep_largest(im))
                im.save(dst, "PNG"); print(f"ok {k}  {im.width}x{im.height}"); ok = True; break
            except urllib.error.HTTPError as e:
                print("HTTP", e.code, e.read().decode()[:200], k, t); time.sleep(4)
            except Exception as e:
                print("ERR", type(e).__name__, str(e)[:200], k, t); time.sleep(4)
        if not ok: fails.append(k)
    print("FAILED:", fails if fails else "none")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
