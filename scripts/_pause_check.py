# -*- coding: utf-8 -*-
"""Dev-only checks for round 16, REAL audio: the lesson pauses when hidden (tab switched / minimised) and
resumes where it left off; the music at 30 %; the shop's drag-back sound.   (DIST=1 for the delivery copy)
Hiding is simulated the way the browser reports it: document.hidden / visibilityState + 'visibilitychange'."""
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
js(r"""window.__hid = false;
  Object.defineProperty(document, 'hidden', { configurable:true, get(){ return window.__hid; } });
  Object.defineProperty(document, 'visibilityState', { configurable:true, get(){ return window.__hid ? 'hidden' : 'visible'; } });
  window.hideTab = (h)=>{ window.__hid = h; document.dispatchEvent(new Event('visibilitychange')); };
  window.__sfx = []; const _l = window._loadVoiceBuffer;
  window._loadVoiceBuffer = function(s){ const n = String(s).split('/').pop().split('.')[0]; if(/^sfx_/.test(n)) window.__sfx.push(n); return _l.apply(this, arguments); };""")
hide = lambda h: js("hideTab(arguments[0])", h)

# ---- music: 30 %, paused while hidden, back after
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').classList.add('lt-play-shown'); document.getElementById('sgBtn').click()")
time.sleep(0.8)
quiet, t_q = 0, time.time()                           # wait for 2.5 s with no voice (the transition + page 1's lines)
while time.time() - t_q < 25 and quiet < 2.5:
    quiet = 0 if js("return isPlaying") else quiet + 0.1
    time.sleep(0.1)
v = js("const B=window.__lessonBgm; return [B.element && !B.element.paused, +B.volume.toFixed(2)]")
check("music plays at 30 % when nothing is speaking", v[0] and 0.27 <= v[1] <= 0.31, v)
hide(True); time.sleep(3)
check("tab hidden: the music is paused (and stays paused)", js("return window.__lessonBgm.element.paused && window.__lessonPaused === true"))
hide(False); time.sleep(1.5)
check("tab back: the music plays again", js("return !window.__lessonBgm.element.paused && !window.__lessonPaused"))

idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
# ---- a voice line pauses mid-word and finishes after
js("mountSlide(arguments[0])", idx["G5"])
t0 = time.time()
while time.time() - t0 < 6 and not js("return isPlaying"): time.sleep(0.05)
t_start = time.time(); time.sleep(1.0)
hide(True); time.sleep(5.0)
mid = js("""const c = (typeof _voiceContext==='function') ? _voiceContext() : null; return [isPlaying, c ? c.state : null]""")
check("hidden mid-line: the voice is frozen (still 'playing', audio suspended)", mid == [True, "suspended"], mid)
hide(False)
while time.time() - t_start < 20 and js("return isPlaying"): time.sleep(0.05)
took = time.time() - t_start; L = js("return CARD.assets.audio_ms.vo_b45_prompt") / 1000.0
check("tab back: the line carries on and ends ~5 s later than it would have (%.1f s for a %.1f s line)" % (took, L), L + 4.3 <= took <= L + 6.5, took)

# ---- inactivity nudge: time away does not count
js("mountSlide(arguments[0])", idx["G1"])
t0 = time.time()
while time.time() - t0 < 8 and "vo_g1_prompt" not in str(js("return (window.__playedSrc||'')")) and not js("return isPlaying"): time.sleep(0.05)
while js("return isPlaying"): time.sleep(0.05)
time.sleep(0.6)                                          # armed
js("window.__hintAt = []; new MutationObserver(ms=>ms.forEach(m=>{ if(m.target.classList && m.target.classList.contains('mn-sp-hint')) window.__hintAt.push(performance.now()); })).observe(document.querySelector('.mn-sort-field'),{attributes:true,subtree:true,attributeFilter:['class']});")
time.sleep(3.0); hide(True); time.sleep(8.0)
n_hidden = js("return window.__hintAt.length")
hide(False); time.sleep(2.0)
n_soon = js("return window.__hintAt.length")
time.sleep(3.0)
n_later = js("return window.__hintAt.length")
check("idle nudge: none while hidden, none right after coming back, then at ~7 s of VISIBLE idle", n_hidden == 0 and n_soon == 0 and n_later >= 1, (n_hidden, n_soon, n_later))

# ---- animations freeze: confetti stops mid-fall
js("confettiCannon()"); time.sleep(0.8)
hide(True); time.sleep(0.3)
run = js("return document.getAnimations().filter(a=>a.playState==='running').length")
time.sleep(2.0)
still = js("return document.querySelectorAll('.fx-confetti').length")
hide(False); time.sleep(0.3)
run2 = js("return document.getAnimations().filter(a=>a.playState==='running').length")
check("hidden: every animation paused (confetti frozen, not finished)", run == 0 and still >= 1 and run2 > 0, (run, still, run2))
time.sleep(5)

# ---- shop: dragging money back out makes its sound
js("window.__sgDragInShown = true; mountSlide(arguments[0])", idx["M1"]); time.sleep(1.0)
while js("return isPlaying"): time.sleep(0.1)
js("document.querySelectorAll('.sg-cell2')[1].click()"); time.sleep(1.5)
while js("return isPlaying"): time.sleep(0.1)
js(r"""window.C=(el)=>{const r=el.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]};
  window.PE=(t,x,y,g)=>(g||document).dispatchEvent(new PointerEvent(t,{clientX:x,clientY:y,bubbles:true,button:0,pointerId:1,isPrimary:true}));
  window.drag=(s,dd)=>{const [x0,y0]=C(s),[x1,y1]=C(dd);PE('pointerdown',x0,y0,s);for(let i=1;i<=6;i++)PE('pointermove',x0+(x1-x0)*i/6,y0+(y1-y0)*i/6);PE('pointerup',x1,y1);};""")
js("drag(document.querySelector('.sg-make2 .mn-src.mn-note'), document.querySelector('.sg-make2 .mn-target'))"); time.sleep(5.0)   # + the one-time tip
js("window.__sfx = []; drag(document.querySelector('.sg-make2 .mn-target .mn-placed:not(.mn-slot)'), document.querySelector('.sg-make2 .mn-src.mn-c1'))"); time.sleep(1.2)
check("shop: dragging money back out plays its drop sound", "sfx_drop_note" in js("return window.__sfx"), js("return window.__sfx"))

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
