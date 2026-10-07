# -*- coding: utf-8 -*-
"""Dev-only: background music + the round-2q praise text, with REAL audio.   (DIST=1 for dist)"""
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
d.get("http://127.0.0.1:%d/%s" % (port, PAGE))
js = d.execute_script
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
t0 = time.time()
while time.time() - t0 < 40 and js("return window.__preloadMs == null"): time.sleep(0.2)
bgm_res = js("return performance.getEntriesByType('resource').filter(r => /bgm_lesson/.test(r.name)).map(r => [Math.round(r.responseEnd), Math.round(r.transferSize/1024)])")
check("music downloaded before the loader leaves (fetch only)", bool(bgm_res), bgm_res)
time.sleep(10)
pre = js("const B=window.__lessonBgm; return [!!B, B && B.element ? !B.element.paused : false]")
check("no music on the cover, before the play tap", pre[0] and not pre[1], pre)
# the play tap -> music + the first transition (VO)
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').classList.add('lt-play-shown'); document.getElementById('sgBtn').click()")
samples = []
t1 = time.time()
while time.time() - t1 < 16:
    samples.append(js("const B=window.__lessonBgm, e=B && B.element; return [e ? !e.paused : false, B ? +B.volume.toFixed(3) : 0, isPlaying ? 1 : 0, e ? +e.currentTime.toFixed(1) : 0]"))
    time.sleep(0.1)
playing = [s for s in samples if s[0]]
check("music starts on the play tap", len(playing) > 10, samples[:3])
under_vo = [s[1] for s in samples if s[0] and s[2]]
free = [s[1] for s in samples if s[0] and not s[2]]
print("  volume while a VO plays: min %.2f max %.2f | with no VO: max %.2f" % (min(under_vo or [0]), max(under_vo or [0]), max(free or [0])))
check("music ducks to ~0.16 under the voice-over", under_vo and min(under_vo) <= 0.18 and sorted(under_vo)[len(under_vo)//2] <= 0.2, under_vo[:10])
check("music at ~0.68 when nothing else is speaking", free and max(free) >= 0.6, free[-10:])
check("music is advancing (really playing)", playing and playing[-1][3] > 2, playing[-1] if playing else None)
# the praise text on the tap screen
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
js("mountSlide(arguments[0])", idx["T2"]); time.sleep(4.5)
js("document.querySelectorAll('.mn-card')[0].click()"); time.sleep(0.8)
fb = js("const f=document.querySelector('.mn-pick-fb'); return [f.textContent, getComputedStyle(f).opacity]")
said = js("return isPlaying")
check("₹10 correct: no on-screen praise text", fb[0] == "", fb)
check("₹10 correct: the praise VO plays", said is True)
js("mountSlide(arguments[0])", idx["T3"]); time.sleep(4.5)
js("[...document.querySelectorAll('.mn-card')].find(c=>c.dataset.ok).click()"); time.sleep(0.6)
check("₹1 correct: no on-screen praise text", js("return document.querySelector('.mn-pick-fb').textContent") == "")
errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors / 404s", not errs, errs[:5])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
