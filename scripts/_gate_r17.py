# -*- coding: utf-8 -*-
"""Dev-only, REAL audio: the three transitions as the reference lesson's r142 screen (round 17) + the ₹14 closing-line
highlight.  (DIST=1 for dist)"""
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
js(r"""window.__sfx=[]; const _l=window._loadVoiceBuffer;
  window._loadVoiceBuffer=function(s){ const n=String(s).split('/').pop().split('.')[0]; if(/^sfx_/.test(n)) window.__sfx.push([Math.round(performance.now()), n]); return _l.apply(this, arguments); };""")
CUE = js("return CARD.gate.title_cue_ms")
REC = r"""
  window.__g = []; window.__g0 = performance.now(); window.__sfx = [];
  const g = document.getElementById('phaseGate'), ttl = document.getElementById('phaseGateTitle'), im = document.getElementById('phaseGateImg');
  (function rec(){
    window.__g.push([Math.round(performance.now() - window.__g0), g.classList.contains('show') ? 1 : 0, isPlaying ? 1 : 0,
      ttl.textContent, ttl.classList.contains('pg-pop') ? 1 : 0, g.classList.contains('pg-sink') ? 1 : 0, String(im.getAttribute('src') || '')]);
    if(window.__g.length < 4000) requestAnimationFrame(rec); })();
  /* exact moments (a frame sample can land late): the headline set, the screen closed */
  window.__capAt = null; window.__closeAt = null;
  new MutationObserver(()=>{ if(ttl.textContent && window.__capAt == null) window.__capAt = Math.round(performance.now() - window.__g0); })
    .observe(ttl, {childList:true, characterData:true, subtree:true});
  let _sh = g.classList.contains('show');
  new MutationObserver(()=>{ const s = g.classList.contains('show'); if(_sh && !s && window.__closeAt == null) window.__closeAt = Math.round(performance.now() - window.__g0); _sh = s; })
    .observe(g, {attributes:true, attributeFilter:['class']});"""
def run_gate(phase, action, wait):
    js(REC); js(action); time.sleep(wait)
    log = js("return window.__g"); sfx = js("return window.__sfx")
    shown = [x for x in log if x[1]]
    if not shown: check("%s: transition shown" % phase, False); return
    t_open, t_close = shown[0][0], shown[-1][0]
    vo = [x for x in shown if x[2]]
    vo_start = vo[0][0] - t_open if vo else None
    vo_end = vo[-1][0] - t_open if vo else None
    cap = next((x for x in shown if x[3]), None)
    cap_at = (js("return window.__capAt") - t_open) if js("return window.__capAt") is not None else None
    if js("return window.__closeAt") is not None: t_close = js("return window.__closeAt")
    src = shown[3][6] if len(shown) > 3 else ""
    whoosh = [t for t, n in sfx if n == "sfx_whoosh"]
    print("  %-8s whoosh %s · art %s · VO %s-%s ms · title appears %s ms (cue %s ms into the clip) · closes %s ms%s"
          % (phase, (whoosh[0] - js("return window.__g0") - t_open) if whoosh else None, "blob/peek" if ("blob:" in src or "peeking_talk_up" in src) else src[-30:],
             vo_start, vo_end, cap_at, CUE.get(phase), t_close - t_open, " · sinks" if any(x[5] for x in shown) else ""))
    check("%s: the whoosh as the screen opens" % phase, whoosh and abs(whoosh[0] - js("return window.__g0") - t_open) < 400, whoosh)
    check("%s: Swifty is the reference's peeking_talk_up animation" % phase, "blob:" in src or "peeking_talk_up" in src, src)
    check("%s: the voice starts right away (no rise wait)" % phase, vo_start is not None and vo_start < 900, vo_start)
    check("%s: the headline is blank until Swifty says it, then wipes in" % phase,
          cap_at is not None and abs(cap_at - (vo_start + CUE.get(phase, 0))) <= 350 and cap[4] == 1, (cap_at, vo_start, CUE.get(phase)))
    check("%s: the screen stays until the line ends (and the line is up 0.7 s), then lets go" % phase,
          vo_end is not None and vo_end <= t_close - t_open <= vo_end + 2200 and (t_close - t_open) - cap_at >= 1500, (vo_end, t_close - t_open))
    if phase == "tutorial": check("tutorial: Swifty sinks out at the end", any(x[5] for x in shown))
js("try{stopAudio()}catch(e){}")
js("document.getElementById('sgBtn').disabled=false; document.getElementById('sgBtn').classList.add('lt-play-shown')")
run_gate("tutorial", "document.getElementById('sgBtn').click()", 9.0)
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
check("tutorial transition lands on the teaching screen", js("return CARD.slides[state.idx].id") == "T1", js("return CARD.slides[state.idx].id"))
for phase, frm in (("guided", "T1"), ("practice", "G5")):
    js("mountSlide(arguments[0])", idx[frm]); time.sleep(1.0)
    t_w = time.time()        # the page's own lines finish first, as for a child
    while time.time() - t_w < 15 and js("return isPlaying"): time.sleep(0.2)
    time.sleep(0.5)
    js("try{stopAudio()}catch(e){}")
    run_gate(phase, "completeSlide(true)", 9.0)

# ₹14 closing line with real audio: tens → ones → total, in that order, then off  (round 3: G3, the
# ghost-guided ₹14 — the child places the ₹10, then the four ₹1)
js("mountSlide(arguments[0])", idx["G3"]); time.sleep(6)
js(r"""window.__h=[]; window.__h0=performance.now();
  (function rec(){ const t=document.querySelector('.mn-row-t'), o=document.querySelector('.mn-row-o'), tt=document.querySelector('.mn-total');
    window.__h.push([Math.round(performance.now()-window.__h0), t.classList.contains('mn-say-hi')?1:0, o.classList.contains('mn-say-hi')?1:0, tt.classList.contains('mn-say-hi')?1:0, isPlaying?1:0]);
    if(window.__h.length < 3000) requestAnimationFrame(rec); })();
  const C=(el)=>{ const r=el.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2]; };
  const PE=(type,x,y,tgt)=>(tgt||document).dispatchEvent(new PointerEvent(type,{clientX:x,clientY:y,bubbles:true,button:0,pointerId:1,isPrimary:true}));
  window.__tap=(el)=>{ const [x,y]=C(el); PE('pointerdown',x,y,el); PE('pointerup',x,y); };""")
for k in ["note", "c1", "c1", "c1", "c1"]:
    t_w = time.time()      # a tap only counts when no line is playing (as for a child)
    while time.time() - t_w < 15 and js("return isPlaying"): time.sleep(0.1)
    time.sleep(0.3); js("__tap(document.querySelector('.mn-src.mn-%s'))" % k); time.sleep(1.2)
time.sleep(10)
print("  ₹14 screen finished:", js("return !!document.querySelector('.mn-finished')"), "| placed:", js("return document.querySelectorAll('.mn-target .mn-placed:not(.mn-slot)').length"))
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
