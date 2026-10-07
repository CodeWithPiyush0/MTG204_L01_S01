# -*- coding: utf-8 -*-
"""Dev-only: the four transitions + the ₹14 closing-line highlight, with REAL audio.  (DIST=1 for dist)"""
import os, sys, time, threading, http.server, socketserver, functools, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
OUT = sys.argv[1] if len(sys.argv) > 1 else None
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True; request_queue_size = 256
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(3)
t_w = time.time()
while time.time() - t_w < 40 and d.execute_script("return window.__preloadMs == null"): time.sleep(0.2)   # as in real use: loader holds until preloaded
time.sleep(1)
js = d.execute_script
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
G = js("return CARD.gate"); OPEN = set(f for f, _ in G["talk"]["open"])
REC = r"""
  window.__g = []; window.__g0 = performance.now();
  const g = document.getElementById('phaseGate'), ttl = document.getElementById('phaseGateTitle');
  (function rec(){ const cv = document.getElementById('phaseGateCv');
    window.__g.push([Math.round(performance.now() - window.__g0), g.classList.contains('show') ? 1 : 0,
      g.classList.contains('pg-talking') ? 1 : 0, cv ? +cv.dataset.f : -1, isPlaying ? 1 : 0,
      ttl.querySelectorAll('.pg-tw.on').length, ttl.querySelectorAll('.pg-tw').length]);
    if(window.__g.length < 4000) requestAnimationFrame(rec); })();"""
def run_gate(phase, action, wait):
    js(REC); js(action); time.sleep(wait)
    log = js("return window.__g")
    shown = [x for x in log if x[1]]
    if not shown: check("%s: transition shown" % phase, False); return
    t_open = shown[0][0]
    vo = [x for x in shown if x[4]]
    vo_start = vo[0][0] - t_open if vo else None
    talk = [x for x in shown if x[2]]
    talk_start = talk[0][0] - t_open if talk else None
    beak_open_silent = [x for x in shown if x[2] and x[3] in OPEN and not x[4]]
    beak_opens = sum(1 for a, b in zip(talk, talk[1:]) if b[3] in OPEN and a[3] not in OPEN)
    full = [x for x in shown if x[6] and x[5] == x[6]]
    first_letter = next((x[0] - t_open for x in shown if x[5] > 0 and x[6]), None)
    vo_end = vo[-1][0] - t_open if vo else None
    print("  %-8s open→VO %s ms · talk sheet from %s ms · beak openings %d · first letter %s ms · title complete %s ms · VO end %s ms"
          % (phase, vo_start, talk_start, beak_opens, first_letter, full[0][0] - t_open if full else None, vo_end))
    check("%s: Swiftie rises first, VO starts on her first speaking frame (~1.96 s)" % phase,
          vo_start is not None and 1800 <= vo_start <= 2400, vo_start)
    check("%s: beak lip-synced (opens with the voice, never open in silence)" % phase,
          beak_opens >= 2 and len(beak_open_silent) <= 2, (beak_opens, len(beak_open_silent)))
    check("%s: the title types in and is complete by the end of the line" % phase,
          first_letter is not None and full and full[0][0] - t_open <= vo_end + 60, (first_letter, vo_end))
js("try{stopAudio()}catch(e){}")
# tutorial gate: the real play button
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').classList.add('lt-play-shown')")
run_gate("tutorial", "document.getElementById('sgBtn').click()", 9.5)
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
for phase, frm in (("guided", "T4"), ("practice", "G4"), ("mastery", "P4")):
    js("mountSlide(arguments[0])", idx[frm]); time.sleep(0.4)
    js("try{stopAudio()}catch(e){}")
    run_gate(phase, "completeSlide(true)", 9.5 if phase != "mastery" else 6.5)
    if OUT and phase == "mastery": d.save_screenshot(OUT + "_mastery_gate.png")

# ₹14 closing line with real audio: tens → ones → total, in that order, then off
js("mountSlide(arguments[0])", idx["G2"]); time.sleep(16)
js(r"""window.__h=[]; window.__h0=performance.now();
  (function rec(){ const t=document.querySelector('.mn-row-t'), o=document.querySelector('.mn-row-o'), tt=document.querySelector('.mn-total');
    window.__h.push([Math.round(performance.now()-window.__h0), t.classList.contains('mn-say-hi')?1:0, o.classList.contains('mn-say-hi')?1:0, tt.classList.contains('mn-say-hi')?1:0, isPlaying?1:0]);
    if(window.__h.length < 3000) requestAnimationFrame(rec); })();
  const C=(el)=>{ const r=el.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2]; };
  const PE=(type,x,y,tgt)=>(tgt||document).dispatchEvent(new PointerEvent(type,{clientX:x,clientY:y,bubbles:true,button:0,pointerId:1,isPrimary:true}));
  window.__tap=(el)=>{ const [x,y]=C(el); PE('pointerdown',x,y,el); PE('pointerup',x,y); };""")
for i in range(4):
    t_w = time.time()      # a tap only counts when no line is playing (as for a child)
    while time.time() - t_w < 15 and js("return isPlaying"): time.sleep(0.1)
    time.sleep(0.3); js("__tap(document.querySelector('.mn-src.mn-c1'))"); time.sleep(1.0)
time.sleep(10)
print("  ₹14 screen finished:", js("return !!document.querySelector('.mn-finished')"), "| placed:", js("return document.querySelectorAll('.mn-target .mn-placed').length"))
h = js("return window.__h")
order = []
for x in h:
    st = "total" if x[3] else ("tens" if x[1] and not x[2] else ("ones" if x[2] and not x[1] else None))
    if st and (not order or order[-1] != st): order.append(st)
print("  ₹14 closing line, highlight order:", order)
check("₹14 closing line (real audio): ₹10 → ₹1 → total, in order", order[:3] == ["tens", "ones", "total"], order)
check("₹14 closing line: lights only while the line is sounding", not [x for x in h if (x[1] or x[2] or x[3]) and not x[4]][3:])
errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors / 404s", not errs, errs[:5])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
