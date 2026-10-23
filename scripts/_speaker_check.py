# -*- coding: utf-8 -*-
"""Dev-only, REAL audio (round 19 QA bug): the speaker must stay greyed through a sequence of lines - no blue
flash in the gaps between them - and come back once the last line is done.   (DIST=1 for the delivery copy)"""
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
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
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
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
REC = r"""window.__s = []; window.__s0 = performance.now();
  (function rec(){
    const chip = document.querySelector('#slideHost .tut-audio') || document.getElementById('audioChip');
    const cs = chip ? getComputedStyle(chip) : null;
    window.__s.push([Math.round(performance.now() - window.__s0), isPlaying ? 1 : 0, document.body.classList.contains('vo-lock') ? 1 : 0,
                     cs ? +(+cs.opacity).toFixed(2) : -1, cs ? cs.pointerEvents : '']);
    if(performance.now() - window.__s0 < arguments_ms) requestAnimationFrame(rec); })();"""
def screen(sid, label, secs, n_lines):
    js("mountSlide(arguments[0])", idx[sid])
    js(REC.replace("arguments_ms", str(secs * 1000)))
    time.sleep(secs + 0.5)
    s = js("return window.__s")
    on = [x for x in s if x[1]]
    if not on: check("%s: lines played" % label, False); return
    t_first, t_last = on[0][0], on[-1][0]
    during = [x for x in s if t_first <= x[0] <= t_last]
    lock_drops = sum(1 for a, b in zip(during, during[1:]) if a[2] and not b[2])
    blue = [x for x in during if x[0] > t_first + 300 and (x[3] > 0.6 or x[4] != "none")]   # (its 0.18 s fade to grey at the start excluded)
    after = [x for x in s if x[0] > t_last + 1100]
    print("  %-34s lines %.1f-%.1f s · voice-lock drops between lines: %d · speaker blue during the sequence: %d frames · after: opacity %s"
          % (label, t_first / 1000, t_last / 1000, lock_drops, len(blue), after[-1][3] if after else None))
    if n_lines > 1 and lock_drops:
        print("    (this screen has %d gap(s) between its lines - the bug's trigger)" % lock_drops)
    check("%s: the speaker stays greyed + untappable through the whole sequence" % label, not blue, blue[:3])
    check("%s: the speaker comes back (blue, tappable) after the last line" % label, after and after[-1][3] > 0.9 and after[-1][4] != "none", after[-1:] if after else None)
screen("T1", "page 1 - ₹10 then ₹1 (card speaker)", 7.0, 2)
screen("G3", "page 4 - opening line then instruction", 13.0, 2)
js("window.__sgDragInShown = true")
screen("M1", "shop stall - intro then instruction", 10.0, 2)
errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
