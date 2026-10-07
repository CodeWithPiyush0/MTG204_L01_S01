# -*- coding: utf-8 -*-
"""Dev-only checks for round 2p (DIST=1 for the delivery copy):
border-only feedback, arrow pulse after the VO, landing play button after the greeting, celebration
arrow after its line, spoken-sync highlight, tap-to-place, shop drag-in demo, stall cells stay
tappable after the idle glow, shop complete = list only. Transitions with REAL audio are in _gate_r2p.py."""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
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
d.get("http://127.0.0.1:%d/%s" % (port, PAGE))
js = d.execute_script
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
def shot(n):
    if OUT: d.save_screenshot(os.path.join(OUT, n + ".png"))
if OUT: os.makedirs(OUT, exist_ok=True)

# ---- landing: the play button is invisible while the greeting plays, then appears + pulses
seen_during, t0 = [], time.time()
while time.time() - t0 < 25:
    st = js("""const b=document.getElementById('sgBtn'), cs=getComputedStyle(b);
      return [typeof isPlaying!=='undefined' && isPlaying, cs.visibility, cs.animationName, b.classList.contains('lt-play-shown'), b.disabled, cs.boxShadow, cs.outlineStyle]""")
    if st[0]: seen_during.append(st[1])
    if st[3] and not st[4] and not st[0]: break
    time.sleep(0.1)
check("cover: play button hidden while the greeting plays", seen_during and all(v == "hidden" for v in seen_during), seen_during[:5])
check("cover: then visible and pulsing (scale only)", st[1] == "visible" and "ltPlayPulse" in st[2], st)
shot("p_cover_ready")

js(r"""
window.__said = []; window.__ghosts = 0;
try{ stopAudio(); }catch(e){}
window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setTimeout(()=>{ if(cb) cb(); }, 60); };
new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('mn-ghost')) window.__ghosts++; }))).observe(document.getElementById('stage'),{childList:true});
document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
window.C = (el)=>{ const r = el.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
window.PE = (type, x, y, tgt)=> (tgt||document).dispatchEvent(new PointerEvent(type, {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true}));
window.drag = (src, dst)=>{ const [x0,y0] = C(src), [x1,y1] = C(dst);
  PE('pointerdown', x0, y0, src); for(let i=1;i<=6;i++) PE('pointermove', x0+(x1-x0)*i/6, y0+(y1-y0)*i/6); PE('pointerup', x1, y1); };
window.tap = (el)=>{ const [x,y] = C(el); PE('pointerdown', x, y, el); PE('pointerup', x, y); };
window.src = (k)=> document.querySelector('.mn-src.mn-' + ({n10:'note', c10:'c10', c1:'c1'})[k]);
""")
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
def mount(sid, w=0.8): js("mountSlide(arguments[0]); window.__said=[];", idx[sid]); time.sleep(w)
T = "document.querySelector('.mn-target')"
placed = lambda sel=".mn-target": js("return document.querySelectorAll('%s .mn-placed:not(.mn-slot)').length" % sel)

# ---- (1) border-only feedback on the tap cards
mount("T2")
js("document.querySelectorAll('.mn-card')[1].click()"); time.sleep(0.5)
bad = js("const c=document.querySelectorAll('.mn-card')[1], s=getComputedStyle(c); return [s.backgroundColor, s.borderTopColor]")
time.sleep(1.4)
js("document.querySelectorAll('.mn-card')[0].click()"); time.sleep(0.4)
ok = js("const c=document.querySelectorAll('.mn-card')[0], s=getComputedStyle(c); return [s.backgroundColor, s.borderTopColor]")
check("wrong card: red border, white card", bad[0] == "rgb(255, 255, 255)" and bad[1].startswith("rgb(249, 53, 68"), bad)
check("right card: green border, white card", ok[0] == "rgb(255, 255, 255)" and ok[1].startswith("rgb(0, 177, 50"), ok)
# ---- (2) the arrow pulses once enabled (scale only, no glow)
time.sleep(0.6)
nav = js("const b=document.getElementById('navBtn'), s=getComputedStyle(b); return [b.disabled, s.animationName, b.classList.contains('hint-glow')]")
check("arrow enabled after the VO, pulsing, no glow class", nav[0] is False and nav[1] not in ("none", "") and not nav[2], nav)
shot("p_T2_right")

# ---- (5) TAP places money on a build screen (same rules)
mount("P1")
js("tap(src('n10'))"); time.sleep(0.6)
check("tap on a ₹10 note puts it in the drop zone", placed() == 1 and js("return document.querySelector('.mn-total b').textContent") == "₹10", placed())
for i in range(2): js("tap(src('n10'))"); time.sleep(0.4)
js("tap(src('n10'))"); time.sleep(0.6)
check("a 4th ₹10 by tap is refused (₹5 still needed) and bounces", placed() == 3, placed())
for i in range(5): js("tap(src('c1'))"); time.sleep(0.4)
time.sleep(0.4)
check("tap-only build completes ₹35", js("return !!document.querySelector('.mn-finished')"))

# ---- (4) spoken-sync highlight: rows light inside their measured windows
cues = js("return CARD.slides[arguments[0]].data.done_cues", idx["G2"])
mount("G2", 4.0)
for i in range(4): js("drag(src('c1'), %s)" % T); time.sleep(1.1)
js(r"""window.__hi=[]; window.__hiT0=null;
  window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]);
     window.__hiT0 = performance.now(); setTimeout(()=>{ if(cb) cb(); }, 7600); };
  window._voiceClock = function(){ return ()=>({ t: window.__hiT0 == null ? null : performance.now() - window.__hiT0, ended: window.__hiT0 != null && performance.now() - window.__hiT0 > 7500 }); };
  (function rec(){ const t=document.querySelector('.mn-row-t'), o=document.querySelector('.mn-row-o'), tt=document.querySelector('.mn-total');
     if(window.__hiT0!=null) window.__hi.push([Math.round(performance.now()-window.__hiT0), t&&t.classList.contains('mn-say-hi')?1:0, o&&o.classList.contains('mn-say-hi')?1:0, tt&&tt.classList.contains('mn-say-hi')?1:0]);
     requestAnimationFrame(rec); })();
  state.replayAudio();""")
time.sleep(3.2); shot("p_G2_ones_lit"); time.sleep(5.0)
hi = js("return window.__hi")
def ok_at(t, tt, oo, to):
    s = [x for x in hi if abs(x[0] - t) < 40]
    return s and all(x[1] == tt and x[2] == oo and x[3] == to for x in s)
mid = lambda w: (w[0] + w[1]) // 2
check("closing line: ₹10 row lit while «एक दस रुपये का नोट» is said", ok_at(mid(cues["tens"]), 1, 0, 0), cues)
check("closing line: ₹1 row lit while «चार एक रुपये के सिक्के» is said", ok_at(mid(cues["ones"]), 0, 1, 0))
check("closing line: everything lit on «कुल मिलाकर बने …»", ok_at(mid(cues["total"]), 1, 1, 1))
check("closing line: all off after the line", all(x[1] == 0 and x[2] == 0 and x[3] == 0 for x in hi if x[0] > 7600))
js("window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setTimeout(()=>{ if(cb) cb(); }, 60); }")

# ---- (7) stall: every unbought cell still takes a REAL click after the idle glow
mount("M1", 1.0)
time.sleep(14)
dead = js("""return [...document.querySelectorAll('.sg-cell2')].map((c,i)=>{ const r=c.getBoundingClientRect();
   const top=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return c.contains(top) ? null : i; }).filter(x=>x!=null)""")
check("stall: after the idle reminder every cell is still on top (tappable)", dead == [], dead)
check("stall: engine class .sg-glow never used on a cell", js("return !document.querySelector('.sg-cell2.sg-glow')"))
el = d.find_elements(By.CSS_SELECTOR, ".sg-cell2")[3]
ActionChains(d).move_to_element(el).click().perform(); time.sleep(1.2)
check("stall: real click on a reminded cell opens it", js("return !!document.querySelector('.sg-make2')"))

# ---- (6) shop: the first item shows the drag-in ghost twice after its line
js("window.__ghosts=0; window.__sgDragInShown=false; mountSlide(arguments[0]); window.__said=[];", idx["M1"]); time.sleep(1.0)
js("document.querySelectorAll('.sg-cell2')[0].click()"); time.sleep(0.9)
g_mid = js("return window.__ghosts"); shot("p_M1_dragin_ghost")
time.sleep(3.2)
check("shop: drag-in ghost shown twice on the first item", js("return window.__ghosts") == 2, (g_mid, js("return window.__ghosts")))
check("shop: the demo places nothing", placed(".sg-make2") == 0)
js("tap(src('n10'))"); time.sleep(0.6)
check("shop: tap puts money in the amount area", placed(".sg-make2") == 1, placed(".sg-make2"))
js("window.__ghosts=0; mountSlide(arguments[0]);", idx["M1"]); time.sleep(1.0)
js("document.querySelectorAll('.sg-cell2')[1].click()"); time.sleep(3.0)
check("shop: no drag-in demo on later items", js("return window.__ghosts") == 0, js("return window.__ghosts"))

# ---- (8) shop complete = Pari + the page-12 list, no total, no extra card
mount("M1", 1.0)
js("""const it = CARD.slides[state.idx].data.items;""")
for i in range(6):
    price = js("return CARD.slides[arguments[0]].data.items[arguments[1]].price", idx["M1"], i)
    js("document.querySelectorAll('.sg-cell2')[arguments[0]].click()", i); time.sleep(1.2)
    for _ in range(price // 10): js("tap(src('n10'))"); time.sleep(0.25)
    for _ in range(price % 10): js("tap(src('c1'))"); time.sleep(0.25)
    js("document.querySelector('.sg-checkpill').click()"); time.sleep(2.6)
time.sleep(3.0); shot("p_M1_complete")
check("shop complete: 6 green list rows with ticks (page-12 card)", js("return document.querySelectorAll('.sg-complete .mn-li.mn-li-ok:not(.mn-li-wait) .mn-li-tick').length") == 6)
check("shop complete: no total, no 'बहुत बढ़िया खरीदारी' card", js("return !document.querySelector('.sg-till, .sg-great, .sg-side')"))
w1 = js("return Math.round(document.querySelector('.sg-complete .mn-fin-list').getBoundingClientRect().width)")
mount("P4", 3.0)
w2 = js("return Math.round(document.querySelector('.mn-fin-list').getBoundingClientRect().width)")
check("shop complete list = page 12 list size", abs(w1 - w2) <= 2, (w1, w2))

# ---- (2) celebration arrow: dim until the line ends, then pulses
js("window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setPlaying(true); setTimeout(()=>{ setPlaying(false); if(cb) cb(); }, 1500); }")
mount("CEL", 0.5)
e1 = js("const b=document.getElementById('endBtn'); return [b.classList.contains('cel-wait'), getComputedStyle(b).pointerEvents]")
time.sleep(3.6)        # round 2r: the line starts after the 1.62 s jump + landing, then runs 1.5 s here
e2 = js("const b=document.getElementById('endBtn'), s=getComputedStyle(b); return [b.classList.contains('cel-ready'), s.animationName, b.classList.contains('hint-glow')]")
check("celebration arrow not pressable while the line plays", e1[0] and e1[1] == "none", e1)
check("celebration arrow pulses after the line (no glow)", e2[0] and e2[1] == "celArrowPulse" and not e2[2], e2)

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors / 404s", not errs, errs[:5])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
