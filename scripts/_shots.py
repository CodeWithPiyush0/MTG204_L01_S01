# -*- coding: utf-8 -*-
"""Dev-only: serve the game, mount every slide, screenshot it, dump console errors.
Usage: python scripts/_shots.py <outdir> [slide_indices comma list] [--js "<js to run after mount>"] [--wait ms]"""
import os, sys, time, json, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
OUT = sys.argv[1]
SEL = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
JS = None; WAIT = 2500; LAND = False
a = sys.argv[2:]
for i, x in enumerate(a):
    if x == "--js": JS = a[i + 1]
    if x == "--wait": WAIT = int(a[i + 1])
    if x == "--landing": LAND = True
os.makedirs(OUT, exist_ok=True)

class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
H.log_message = lambda *a, **k: None
srv = TS(("127.0.0.1", 0), H); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s" % (port, PAGE))
time.sleep(3.2)
if LAND:
    d.save_screenshot(os.path.join(OUT, "00_landing.png"))
n = d.execute_script("return CARD.slides.length")
idx = [int(x) for x in SEL.split(",")] if SEL else list(range(n))
d.execute_script("""
  const sg=document.getElementById('startGate'); if(sg) sg.classList.add('hidden');
  document.body.classList.remove('is-start');
""")
for i in idx:
    d.execute_script("mountSlide(arguments[0])", i)
    if JS: d.execute_script(JS)
    time.sleep(WAIT / 1000)
    t = d.execute_script("return CARD.slides[arguments[0]].id + '_' + CARD.slides[arguments[0]].type", i)
    d.save_screenshot(os.path.join(OUT, "%02d_%s.png" % (i + 1, t)))
logs = [l for l in d.get_log("browser") if l["level"] in ("SEVERE", "WARNING")]
for l in logs:
    m = l["message"]
    if "Audio/" in m and "404" in m: continue
    print(l["level"], m[:300])
print("done", len(idx))
d.quit(); srv.shutdown()
