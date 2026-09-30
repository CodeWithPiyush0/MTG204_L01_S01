import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
d = webdriver.Chrome(options=o); d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(3)
js = d.execute_script
js("""window.__sfx=[]; const _A=window.Audio; window.Audio=function(src){ if(src && /sfx_(play|next)_button/.test(src)) window.__sfx.push(src.split('/').pop().split('?')[0]); return new _A(src); };""")
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').click()"); time.sleep(0.4)
print("play button ->", js("return window.__sfx"))
time.sleep(1.9); d.save_screenshot(sys.argv[1]); print("title class:", js("return document.getElementById('phaseGateTitle').className"))
time.sleep(6)
js("setNavActive(true)"); js("window.__sfx=[]; document.getElementById('navBtn').click()"); time.sleep(0.3)
print("next button ->", js("return window.__sfx"))
js("document.getElementById('navBtn').disabled=true; window.__sfx=[]; document.getElementById('navBtn').click()"); time.sleep(0.3)
print("disabled next ->", js("return window.__sfx"))
d.quit(); srv.shutdown()
