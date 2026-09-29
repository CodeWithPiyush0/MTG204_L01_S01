import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750")
d = webdriver.Chrome(options=o); d.get("http://127.0.0.1:%d/MTG2A04_L01_S01.html" % port); time.sleep(3)
d.execute_script("window.__said=[];window.play=function(s,cb){window.__said.push(String(s||'').split('/').pop().split('.')[0]);setTimeout(()=>cb&&cb(),300)};")
# real start button -> tutorial gate -> T1
d.execute_script("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').click()"); time.sleep(0.8)
d.save_screenshot(os.path.join(OUT, "gate_tutorial.png"))
print("gate1 title:", d.execute_script("return document.getElementById('phaseGateTitle').textContent"))
time.sleep(3.5); print("after gate1 slide:", d.execute_script("return CARD.slides[state.idx].id"))
for sid in ("T4", "P4"):
    i = d.execute_script("return CARD.slides.findIndex(s=>s.id===arguments[0])", sid)
    d.execute_script("mountSlide(arguments[0])", i); time.sleep(2.5)
    print(sid, "nav enabled after VO:", d.execute_script("return !document.getElementById('navBtn').disabled"))
    d.execute_script("document.getElementById('navBtn').click()"); time.sleep(0.9)
    d.save_screenshot(os.path.join(OUT, "gate_after_%s.png" % sid))
    print("  gate title:", d.execute_script("return document.getElementById('phaseGateTitle').textContent"),
          "| said:", d.execute_script("return window.__said.slice(-1)"))
    time.sleep(1.6); print("  mid-gate title:", d.execute_script("return document.getElementById('phaseGateTitle').textContent"), "visible:", d.execute_script("return document.getElementById('phaseGate').classList.contains('show')")); time.sleep(6); print("  said:", d.execute_script("return window.__said.slice(-2)")); print("  now on:", d.execute_script("return CARD.slides[state.idx].id"),
                           "auto-next class:", d.execute_script("return document.body.classList.contains('auto-next')"))
d.quit(); srv.shutdown()
