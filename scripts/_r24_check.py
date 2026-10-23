# -*- coding: utf-8 -*-
"""Dev-only, real clips (muted unless SOUND=1) - round 24 (user): "whenever VO is playing do not let the user
click on any object". Taps every few hundred ms on the shop's items, notes / coins, placed money, and a
sorting screen's pieces WHILE Swiftee talks (lines and the pauses between them) - none may act; once she
is done (the speaker is blue again) the same tap works.   (DIST=1 for the delivery copy)"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
js("try{stopAudio()}catch(e){}; document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');")
js(r"""window.__plays = []; const _p = window.play;
  window.play = function(src, cb){ window.__plays.push(String(src).split('/').pop()); return _p.apply(this, arguments); };
  /* a real finger: the element under the point gets pointerdown + pointerup + click */
  window.TAP = (el)=>{ if(!el) return 'none'; const r = el.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    const t = document.elementFromPoint(x, y); if(!t) return 'none';
    const o = {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true};
    t.dispatchEvent(new PointerEvent('pointerdown', o)); t.dispatchEvent(new PointerEvent('pointerup', o)); t.dispatchEvent(new MouseEvent('click', o));
    return 'ok'; };
  window.VOBUSY = ()=> isPlaying || document.body.classList.contains('vo-lock') || document.body.classList.contains('vo-busy');""")
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
def quiet(limit=25):
    t = time.time()
    while time.time() - t < limit and js("return VOBUSY()"): time.sleep(0.1)
def hammer(tap_js, acted_js, secs, label):
    """tap every 0.25 s for `secs` while the voice is busy; returns (taps made while busy, taps that acted)"""
    n = acted = 0; t = time.time()
    while time.time() - t < secs:
        if js("return VOBUSY()"):
            js(tap_js); n += 1; time.sleep(0.12)
            if js(acted_js): acted += 1; break
        time.sleep(0.13)
    print("  %-44s %d taps while Swiftee talked, %d acted" % (label, n, acted))
    return n, acted

# ---- 1. the shop's stall: Swiftee's opening, then the instruction (a sequence)
js("window.__sgDragInShown = true; window.__plays = []; mountSlide(arguments[0])", idx["M1"]); time.sleep(0.3)
n, a = hammer("TAP(document.querySelectorAll('.sg-cell2')[0])", "return !!document.querySelector('.sg-make2') || document.querySelectorAll('.sg-cell2.sg-shine').length > 0", 9, "shop stall: tap an item")
said = js("return window.__plays")
check("shop stall: no item opens while the opening + the instruction play (lines and the pause between)", n >= 10 and a == 0 and said[:2] == ["vo_m_intro.ogg", "vo_m_prompt.ogg"], (n, a, said))
quiet(); time.sleep(0.2)
js("TAP(document.querySelectorAll('.sg-cell2')[0])"); time.sleep(1.2)
check("shop stall: once she is done the same tap opens the item", js("return !!document.querySelector('.sg-make2')"))

# ---- 2. the amount screen: the item's own line
placed = "return document.querySelectorAll('.sg-make2 .mn-target .mn-placed:not(.mn-slot)').length"
SRC = "[...document.querySelectorAll('.sg-make2 .mn-bank .mn-src')].find(e => e.dataset.kind === 'c1')"
n, a = hammer("TAP(%s)" % SRC, placed + " > 0", 6, "shop amount: tap the ₹1 coin")
check("shop amount: no money goes in while the item's line plays", n >= 3 and a == 0 and js(placed) == 0, (n, a, js(placed)))
quiet(); time.sleep(0.2)
js("TAP(%s)" % SRC); time.sleep(1.0)
check("shop amount: once she is done a tap puts the ₹1 in", js(placed) == 1, js(placed))
# the one-time drag-back tip speaks now: placed money cannot be taken back during it
time.sleep(0.4)
PL = "document.querySelector('.sg-make2 .mn-target .mn-placed:not(.mn-slot)')"
n, a = hammer("TAP(%s)" % PL, placed + " === 0", 6, "shop amount: tap the placed ₹1 (tip line)")
check("shop amount: placed money stays while the tip line plays", n >= 2 and a == 0 and js(placed) == 1, (n, a, js(placed)))
quiet(); time.sleep(0.2)
js("TAP(%s)" % PL); time.sleep(1.0)
check("shop amount: once she is done a tap gives it back", js(placed) == 0, js(placed))
# a wrong «जाँचें»: during its line nothing can be added
js("TAP(%s)" % SRC); time.sleep(1.0); quiet(); time.sleep(0.2)
js("TAP(document.querySelector('.sg-checkpill'))"); time.sleep(0.3)
n, a = hammer("TAP(%s)" % SRC, placed + " > 1", 5, "shop amount: tap ₹1 during «ओहो!…»")
check("shop amount: nothing goes in during the wrong-check line", n >= 2 and a == 0, (n, a))
js("try{stopAudio()}catch(e){}")

# ---- 3. a sorting screen: during the instruction (and its replay) no piece is collected
js("window.__plays = []; mountSlide(arguments[0])", idx["G1"]); time.sleep(2.2)
WANT = "[...document.querySelectorAll('.mn-sp')].find(x => +x.dataset.value === 10 && !x.classList.contains('mn-sp-gone'))"
gone = "return document.querySelectorAll('.mn-sp.mn-sp-gone').length"
n, a = hammer("TAP(%s)" % WANT, gone + " > 0", 5, "G1: tap a ₹10 during the instruction")
check("G1: no piece is collected while the instruction plays", n >= 3 and a == 0, (n, a))
quiet(); time.sleep(0.2)
js("TAP(%s)" % WANT); time.sleep(1.2)
check("G1: once she is done the tap collects it", js(gone) == 1, js(gone))
js("try{stopAudio()}catch(e){}")

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
