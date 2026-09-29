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
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750")
d = webdriver.Chrome(options=o); d.get("http://127.0.0.1:%d/%s?dev=1" % (port, PAGE)); time.sleep(3.5)
print("devNav present:", d.execute_script("return !!document.getElementById('devNav')"))
print("options:", d.execute_script("return [...document.querySelectorAll('#devNav option')].map(o=>o.textContent)"))
js = lambda s: d.execute_script(s)
js("document.querySelectorAll('#devNav .dev-nav-btn')[2].click()"); time.sleep(1)   # prev from 0 -> clamps to 0
print("after ⏮/◀:", js("return document.querySelector('.dev-nav-lbl').textContent"))
js("document.querySelectorAll('#devNav .dev-nav-btn')[3].click()"); time.sleep(1)   # next
print("after ▶:", js("return document.querySelector('.dev-nav-lbl').textContent"), "| start hidden:", js("return document.getElementById('startGate').classList.contains('hidden')"))
js("const s=document.querySelector('#devNav select'); s.value='12'; s.dispatchEvent(new Event('change'))"); time.sleep(1.5)
print("after jump:", js("return document.querySelector('.dev-nav-lbl').textContent"), "| mounted:", js("return CARD.slides[state.idx].type"))
d.save_screenshot(sys.argv[1]); d.quit(); srv.shutdown()
