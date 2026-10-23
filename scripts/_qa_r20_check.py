# -*- coding: utf-8 -*-
"""Dev-only (round 20, QA sheet BUG_01 / 06 / 07):
  BUG_01  the page cannot be translated (html translate=no + notranslate, meta google notranslate)
  BUG_06  Swiftee's sad face lasts the whole wrong attempt and comes back to normal after it
  BUG_07  once a screen is solved the speaker is grey and takes no tap until the next page
(DIST=1 for the delivery copy; muted unless SOUND=1)"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True; request_queue_size = 256
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); os.environ.get("SOUND") or o.add_argument("--mute-audio"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")   # muted unless SOUND=1 (the tests read the clocks, not the speakers)
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); js = d.execute_script
t_w = time.time()
while time.time() - t_w < 40 and js("return window.__preloadMs == null && !!window.__assetGateP"): time.sleep(0.2)
time.sleep(1)
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)

# ---- BUG_01
h = js("const h = document.documentElement; const m = document.querySelector('meta[name=google]'); return [h.getAttribute('translate'), h.classList.contains('notranslate'), m && m.content]")
check("BUG_01: <html translate=no class=notranslate> + <meta name=google content=notranslate>", h == ["no", True, "notranslate"], h)

js("try{stopAudio()}catch(e){}; document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');")
js(r"""window.__plays = []; const _p = window.play;
  window.play = function(src, cb){ window.__plays.push(String(src).split('/').pop()); return _p.apply(this, arguments); };""")
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
CHIP = "(document.querySelector('#slideHost .tut-audio') || document.getElementById('audioChip'))"
def chip():
    return js("const c = %s; const s = getComputedStyle(c); return [+(+s.opacity).toFixed(2), s.pointerEvents]" % CHIP)
def tap_chip():
    """a real tap lands only where the speaker can be hit (pointer-events) - returns the clips it started"""
    js("window.__plays = []")
    r = js("""const c = %s; const b = c.getBoundingClientRect(); const e = document.elementFromPoint(b.left + b.width/2, b.top + b.height/2);
              const ok = e && (e === c || c.contains(e)); if(ok) e.dispatchEvent(new MouseEvent('click', {bubbles:true})); return ok;""" % CHIP)
    time.sleep(0.6)
    return r, js("return window.__plays")
def face(): return js("const b = document.getElementById('swBuddy'); return b && b.dataset.expr")
def quiet(limit=20):
    t = time.time()
    while time.time() - t < limit and js("return isPlaying || document.body.classList.contains('vo-lock')"): time.sleep(0.1)
def mount(sid, pre=""):
    js(pre + "; mountSlide(arguments[0])", idx[sid]); time.sleep(0.4)

# ---- BUG_06, nothing spoken: G1, a wrong piece
mount("G1"); time.sleep(2.4); quiet(); time.sleep(0.3)
js("const T = CARD.slides[arguments[0]].data.target; [...document.querySelectorAll('.mn-sp')].find(x => +x.dataset.value !== T).click()", idx["G1"])
f = []
for w in (0.3, 1.5, 2.6):
    time.sleep(w - (f[-1][0] if f else 0)); f.append((w, face()))
time.sleep(3.6 - 2.6); f.append((3.6, face()))
print("  G1 wrong piece (no line):", f)
check("BUG_06: G1 - sad right after the wrong tap, still sad at 2.6 s", f[0][1] == "tryagain" and f[2][1] == "tryagain", f)
check("BUG_06: G1 - back to the normal face by 3.6 s", f[3][1] != "tryagain", f)

# ---- BUG_07: G1 solved
js("const T = CARD.slides[arguments[0]].data.target; window.__want = [...document.querySelectorAll('.mn-sp')].filter(x => +x.dataset.value === T && !x.classList.contains('mn-sp-gone'));", idx["G1"])
for i in range(js("return window.__want.length")):
    quiet(); js("window.__want[arguments[0]].click()", i); time.sleep(1.1)
time.sleep(0.8)
during = chip()
quiet(); time.sleep(1.5)
after = chip(); ok, clips = tap_chip()
print("  G1 solved: speaker during the done line %s, after it %s, tap -> %s %s" % (during, after, ok, clips))
check("BUG_07: G1 solved - the speaker is grey and untappable after the done line", after[0] < 0.6 and after[1] == "none" and not ok and not clips, (after, ok, clips))
check("BUG_07: G1 solved - the arrow is live", js("return !document.getElementById('navBtn').disabled"))
mount("G2"); time.sleep(2.4); quiet(); time.sleep(1.2)
nxt = chip(); ok, clips = tap_chip()
check("BUG_07: the next page (G2) - the speaker is blue again and replays its line", nxt[0] > 0.9 and ok and clips == ["vo_g2_prompt.ogg"], (nxt, ok, clips))
js("try{stopAudio()}catch(e){}")

# ---- BUG_07: G3 (₹14) solved, real taps on the notes / coins
mount("G3"); quiet(25); time.sleep(0.6)
T = js("return CARD.slides[arguments[0]].data.target", idx["G3"])
seq = ["n10"] * (T // 10) + ["c1"] * (T % 10)
srcs = {k: js("return [...document.querySelectorAll('.mn-src')].find(e => e.dataset.kind === arguments[0]) ? true : false", k) for k in set(seq)}
for kd in seq:
    quiet(); time.sleep(0.5)
    el = d.execute_script("return [...document.querySelectorAll('.mn-bank .mn-src')].find(e => e.dataset.kind === arguments[0])", kd)
    ActionChains(d).move_to_element(el).click().perform(); time.sleep(1.3)
time.sleep(0.5); quiet(); time.sleep(1.5)
fin = js("return document.querySelector('.mn-build').classList.contains('mn-finished')")
after = chip(); ok, clips = tap_chip()
print("  G3 finished %s · speaker after the done line %s, tap -> %s %s" % (fin, after, ok, clips))
check("BUG_07: G3 solved - grey, no replay", fin and after[1] == "none" and not ok and not clips, (fin, after, ok, clips))
js("try{stopAudio()}catch(e){}")

# ---- BUG_06 with a line + BUG_07 in the shop: open item 0's amount screen
mount("M1", "window.__sgDragInShown = true; window.__shopDev = {open:0}")
quiet(); time.sleep(0.6)
price = js("return CARD.slides[arguments[0]].data.items[0].price", idx["M1"])
def put(kd):
    quiet(); el = js("return [...document.querySelectorAll('.sg-make2 .mn-bank .mn-src')].find(e => e.dataset.kind === arguments[0])", kd)
    ActionChains(d).move_to_element(el).click().perform(); time.sleep(0.9)
put("c1"); quiet(); time.sleep(0.4)                    # (the one-time drag-back tip plays after the first piece)
chk = js("return document.querySelector('.sg-checkpill')")
if price != 1:
    ActionChains(d).move_to_element(chk).click().perform()
    s = []; t0 = time.time()
    while time.time() - t0 < 12:
        s.append((round(time.time() - t0, 2), face(), js("return isPlaying")))
        time.sleep(0.1)
    spoken = [x for x in s if x[2]]
    end = spoken[-1][0] if spoken else None
    sad_through = all(x[1] == "tryagain" for x in s if spoken and x[0] <= end)
    back = next((x[0] for x in s if end is not None and x[0] > end and x[1] != "tryagain"), None)
    print("  shop wrong check: line %.1f-%.1f s · sad through it %s · normal again at %s s" % (spoken[0][0] if spoken else -1, end or -1, sad_through, back))
    check("BUG_06: shop - sad for the whole wrong-check line", spoken and sad_through, s[:5])
    check("BUG_06: shop - normal face within 0.7 s after the line", back is not None and back - end <= 0.7, (end, back))
# take the coin back out is not needed: make the exact price on top (wrong check keeps the money)
need = price - 1
for _ in range(need // 10): put("n10")
for _ in range(need % 10): put("c1")
quiet(); ActionChains(d).move_to_element(chk).click().perform(); time.sleep(0.6)
during = chip(); ok, clips = tap_chip()
check("BUG_07: shop - item solved: the speaker is grey, a tap does nothing", during[1] == "none" and not ok and not clips, (during, ok, clips))
t = time.time()
while time.time() - t < 15 and not js("return !!document.querySelector('.sg-choose')"): time.sleep(0.2)
quiet(); time.sleep(1.2)
st = chip(); ok, clips = tap_chip()
check("BUG_07: shop - back on the stall the speaker is live and replays the stall line", st[0] > 0.9 and ok and clips == ["vo_m_prompt.ogg"], (st, ok, clips))
js("try{stopAudio()}catch(e){}")

# ---- round 21 (lead): page 1, the speaker replay - the ₹10 then the ₹1 pulsate, each during its own line
js("window.__plays = []"); mount("T1")
t = time.time()
while time.time() - t < 15 and "vo_t1_coin.ogg" not in js("return window.__plays"): time.sleep(0.1)
time.sleep(0.5); quiet(); time.sleep(1.2)          # both lines over (there is a 0.25 s gap between them)
js(r"""window.__p = []; const t0 = performance.now(); (function rec(){
  const it = [...document.querySelectorAll('.mn-intro-it')];
  window.__p.push([Math.round(performance.now() - t0), isPlaying ? 1 : 0, it.map(e => e.classList.contains('mn-say') && getComputedStyle(e).animationName === 'mnIntroSay' ? 1 : 0).join(''),
                   (window.__plays || []).length]);
  if(performance.now() - t0 < 7000) requestAnimationFrame(rec); })();""")
ok, clips = tap_chip(); time.sleep(6.6)
p = js("return window.__p")
phases = []
for x in p:
    if not phases or phases[-1][0] != x[2]: phases.append([x[2], x[0]])
print("  T1 replay: clips %s · pulse phases (which picture pulses, from ms) %s" % (clips, phases))
seen = [ph[0] for ph in phases]
check("round 21: T1 replay - ₹10 pulses, then ₹1 pulses, one at a time, then both still",
      ok and clips[:1] == ["vo_t1_note.ogg"] and "10" in seen and "01" in seen and seen.index("10") < seen.index("01") and "11" not in seen and seen[-1] == "00", (ok, clips, phases))
on10 = [x for x in p if x[2] == "10"]; on01 = [x for x in p if x[2] == "01"]
check("round 21: T1 replay - each pulse lasts about as long as its line (> 1 s)", on10 and on01 and on10[-1][0] - on10[0][0] > 1000 and on01[-1][0] - on01[0][0] > 1000,
      (on10[:1], on10[-1:], on01[:1], on01[-1:]))
js("try{stopAudio()}catch(e){}")

# ---- round 22 (lead): ₹14 - the ₹10 / ₹1 light up while the line names them (opening line, instruction, replay)
REC22 = r"""window.__h = []; const t0 = performance.now(); (function rec(){
  const on = k => { const e = [...document.querySelectorAll('.mn-bank .mn-src')].find(x => x.dataset.kind === k); return e && e.classList.contains('mn-say-src') ? 1 : 0; };
  window.__h.push([Math.round(performance.now() - t0), (window.__plays || []).slice(-1)[0] || '', isPlaying ? 1 : 0, on('n10'), on('c1')]);
  if(performance.now() - t0 < %d) requestAnimationFrame(rec); })();"""
def lit(h, clipname):
    """the highlight windows (ms from the clip becoming audible) on one clip: {'n10': [a, b], 'c1': [a, b]}"""
    rows = [x for x in h if x[1] == clipname]
    st = next((x[0] for x in rows if x[2]), None)
    if st is None: return None, None
    out = {}
    for k, i in (("n10", 3), ("c1", 4)):
        on = [x[0] - st for x in rows if x[i]]
        if on: out[k] = [on[0], on[-1]]
    both = sum(1 for x in rows if x[3] and x[4])
    return out, both
cues = js("return CARD.slides[arguments[0]].data.say_cues", idx["G3"])
js("window.__plays = []; mountSlide(arguments[0])", idx["G3"]); js(REC22 % 11000)
js(r"""window.__vis = []; const v0 = performance.now(); (function rv(){
  const op = k => { const e = [...document.querySelectorAll('.mn-bank .mn-src')].find(x => x.dataset.kind === k); return e ? +getComputedStyle(e).opacity : -1; };
  window.__vis.push([Math.round(performance.now() - v0), op('n10'), op('c1')]); if(performance.now() - v0 < 11000) requestAnimationFrame(rv); })();""")
time.sleep(11.3)
h = js("return window.__h")
for clipname, key in (("vo_b14_intro.ogg", "intro"), ("vo_b14_prompt.ogg", "prompt")):
    w, both = lit(h, clipname)
    print("  G3 %-6s measured cues %s · lit %s · both at once: %s frames" % (key, cues.get(key), w, both))
    good = w and all(k in w and abs(w[k][0] - cues[key][k][0]) <= 250 and abs(w[k][1] - cues[key][k][1]) <= 400 for k in ("n10", "c1"))
    check("round 22: G3 %s - ₹10 then ₹1 light up with «दस रुपये» / «एक रुपये…» (±0.25 s), never together" % key,
          good and not both and w["n10"][0] < w["c1"][0], (w, cues.get(key), both))
vis = js("return window.__vis")
dips = [x for x in vis if x[0] > 1200 and min(x[1], x[2]) < 0.95]
print("  G3 visibility after the pop-in: lowest ₹10 %.2f, ₹1 %.2f, frames below 0.95: %d" % (min(x[1] for x in vis if x[0] > 1200), min(x[2] for x in vis if x[0] > 1200), len(dips)))
check("round 23: G3 - the ₹10 / ₹1 never vanish (or pop in again) when a highlight ends", not dips, dips[:5])
quiet(); time.sleep(1.2)
off_now = js("return [...document.querySelectorAll('.mn-bank .mn-src.mn-say-src')].length")
check("round 22: G3 - no highlight left after the lines", off_now == 0, off_now)
js(REC22 % 5000); ok, clips = tap_chip(); time.sleep(4.6)
w, both = lit(js("return window.__h"), "vo_b14_prompt.ogg")
print("  G3 replay  lit %s" % w)
check("round 22: G3 speaker replay - the instruction lights them again", ok and w and "n10" in w and "c1" in w and not both, (ok, clips, w))
js("try{stopAudio()}catch(e){}")

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
