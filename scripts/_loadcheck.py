# -*- coding: utf-8 -*-
"""Dev-only: load the game on a THROTTLED network and check the asset gate.
  - when does the loader go away, and is the landing scene fully decoded at that moment?
  - are all images + sounds in CARD.preload ready by then?
  - does ANY game file download after the loader is gone (= a visible delay later)?
python scripts/_loadcheck.py [mbps]     (DIST=1 for the delivery copy; default 8 Mbit/s, 40 ms latency)"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
MBPS = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True; request_queue_size = 256
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
d = webdriver.Chrome(options=o)
d.execute_cdp_cmd("Network.enable", {})
d.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": False})
d.execute_cdp_cmd("Network.emulateNetworkConditions", {"offline": False, "latency": 40,
    "downloadThroughput": MBPS * 1e6 / 8, "uploadThroughput": 2e6 / 8})
# record the moment the loader leaves + the landing scene's state at that moment
d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
  window.__t_nav = performance.now();
  const __iv = setInterval(()=>{ if(!document.body) return;
    const bl = document.getElementById('bootLoader'); if(bl) window.__t_seen = true;
    if(window.__loaderGoneAt == null && window.__t_seen && (!bl || bl.classList.contains('done'))){
      window.__loaderGoneAt = performance.now();
      const card = document.querySelector('#startGate .sg-card');
      const m = card && getComputedStyle(card).backgroundImage.match(/url\\("?(.*?)"?\\)/);
      window.__sceneUrl = m ? m[1] : null;
      window.__progressAtGone = window.__preloadProgress;
      window.__resAtGone = performance.getEntriesByType('resource').length;
    }
  if(window.__loaderGoneAt != null) clearInterval(__iv); }, 10);
"""})
t0 = time.time()
d.get("http://127.0.0.1:%d/%s" % (port, PAGE))
while time.time() - t0 < 60 and not d.execute_script("return window.__loaderGoneAt != null"): time.sleep(0.1)
js = d.execute_script
gone = js("return Math.round(window.__loaderGoneAt)")
print("network: %.0f Mbit/s, 40 ms | loader gone at %.1f s | preload done in %s ms | capped: %s"
      % (MBPS, gone / 1000, js("return window.__preloadMs"), js("return !!window.__preloadCapped")))
print("preload progress when the loader left: %s" % js("return window.__progressAtGone"))
scene = js("return window.__sceneUrl")
print("landing scene at that moment:", scene and scene.split("/")[-1],
      "| fully downloaded before the loader left:",
      js("""const e = performance.getEntriesByType('resource').find(r => r.name.indexOf(arguments[0]) >= 0);
            return e ? (e.responseEnd <= window.__loaderGoneAt) : null""", scene.split("/")[-1] if scene else "x"))
tot = js("""const r = performance.getEntriesByType('resource').filter(e => e.responseEnd <= window.__loaderGoneAt);
  const by = {}; r.forEach(e => { const k = e.name.split('?')[0]; by[k] = (by[k] || 0) + 1; });
  return [Math.round(r.reduce((a, e) => a + (e.transferSize || 0), 0) / 1e6 * 100) / 100, r.length,
          Object.entries(by).filter(([k, n]) => n > 1).map(([k, n]) => k.split('/').slice(-1)[0] + ' x' + n).slice(0, 15),
          Math.round(r.reduce((m, e) => Math.min(m, e.startTime), 1e9)), Math.round(window.__gateStartedAt || -1)]""")
print("before the loader left: %.2f MB transferred in %d requests | page script (gate) started at %.1f s" % (tot[0], tot[1], tot[4] / 1000))
print("files requested more than once:", tot[2] if tot[2] else "none")
# enter the game and walk every screen: nothing should download from now on
n_before = js("return performance.getEntriesByType('resource').length")
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').click()"); time.sleep(1)
js("window.play=function(s,cb){setTimeout(()=>cb&&cb(),50)}")
for i in range(js("return CARD.slides.length")):
    js("mountSlide(arguments[0])", i); time.sleep(0.6)
js("phaseBlurTransition(()=>{}, 'guided')"); time.sleep(2.5)
late = js("""return performance.getEntriesByType('resource').slice(arguments[0])
              .filter(r => /assets\\//.test(r.name) && r.transferSize > 0)
              .map(r => r.name.split('/').slice(-2).join('/') + ' ' + Math.round(r.transferSize/1024) + 'KB')""", n_before)
print("game files downloaded AFTER the loader (should be none):", late if late else "none")
errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
print("console errors:", errs if errs else "none")
d.quit(); srv.shutdown()
