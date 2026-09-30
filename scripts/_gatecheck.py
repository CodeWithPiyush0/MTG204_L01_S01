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
d = webdriver.Chrome(options=o); d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(3.5)
js = d.execute_script
js("try{stopAudio()}catch(e){};document.getElementById('startGate').classList.add('hidden');document.body.classList.remove('is-start');")
for sid in ("T4", "P4"):
    i = js("return CARD.slides.findIndex(s=>s.id===arguments[0])", sid)
    js("mountSlide(arguments[0])", i)
    t_w = time.time() + 20
    while time.time() < t_w and not js("return !document.getElementById('navBtn').disabled && !isPlaying"): time.sleep(0.2)
    time.sleep(0.3)
    js("window.__t0=performance.now(); document.getElementById('navBtn').click()")
    log, last = [], None
    t_end = time.time() + 12
    while time.time() < t_end:
        st = js("""const im=document.getElementById('phaseGateImg'), t=document.getElementById('phaseGateTitle');
          return [Math.round(performance.now()-window.__t0), (im.getAttribute('src')||'').split('/').pop(), t.className, isPlaying,
                  document.getElementById('phaseGate').classList.contains('show'), CARD.slides[state.idx].id]""")
        key = tuple(st[1:])
        if key != last: log.append(st); last = key
        if len(sys.argv) > 1 and sid == "T4" and 2600 < st[0] < 2800 and not getattr(d, "_shot", 0): d.save_screenshot(sys.argv[1]); d._shot = 1
        if not st[4] and st[5] != sid: break
        time.sleep(0.05)
    print("==", sid, "->", st[5]); [print("  %5d ms  img=%-16s title=%-22s playing=%s gate=%s slide=%s" % tuple(x)) for x in log]
d.quit(); srv.shutdown()
