# -*- coding: utf-8 -*-
"""Dev-only mechanics driver: plays each interactive screen wrong -> wrong -> right with synthetic
pointer events (real drags from the tray into the target), audio stubbed to a short beat, and asserts
the state the deck asks for. Screenshots land in <outdir>.   python scripts/_drive.py <outdir>"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True
MISSING = []
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):
        if len(a) > 1 and str(a[1]) == "404": MISSING.append(str(a[0]))
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750")
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(3)

HELP = r"""
window.__said = [];
try{ stopAudio(); }catch(e){}   /* the real start button silences the landing greeting; do the same */
window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setTimeout(()=>{ if(cb) cb(); }, 60); };
document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
window.C = (el)=>{ const r = el.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
window.PE = (type, x, y, tgt)=> (tgt||document).dispatchEvent(new PointerEvent(type, {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true}));
window.drag = (src, dst)=>{ const [x0,y0] = C(src), [x1,y1] = C(dst);
  PE('pointerdown', x0, y0, src); for(let i=1;i<=6;i++) PE('pointermove', x0+(x1-x0)*i/6, y0+(y1-y0)*i/6); PE('pointerup', x1, y1); };
window.tap = (el)=>{ const [x,y] = C(el); PE('pointerdown', x, y, el); PE('pointerup', x, y); el.click(); };
window.src = (k)=> document.querySelector('.mn-src.mn-' + ({n10:'note', c10:'c10', c1:'c1'})[k]);
window.S = ()=> ({ total: (document.querySelector('.mn-total b')||{}).textContent, nav: !document.getElementById('navBtn').disabled,
   said: window.__said.slice(-3), prompt: document.getElementById('promptText').textContent,
   off: [...document.querySelectorAll('.mn-src.mn-off')].map(e=>e.dataset.kind),
   glow: [...document.querySelectorAll('.mn-src.mn-glowsrc')].map(e=>e.dataset.kind),
   placed: document.querySelectorAll('.mn-tray .mn-placed:not(.mn-slot)').length,
   finished: !!document.querySelector('.mn-finished') });
"""
d.execute_script(HELP)
def js(s, *a): return d.execute_script(s, *a)
def mount(i): js("mountSlide(arguments[0]); window.__said=[];", i); time.sleep(0.9)
def w(t=0.7): time.sleep(t)
def shot(n): d.save_screenshot(os.path.join(OUT, n + ".png"))
def st(): return js("return S()")
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}

# ---------------- T2 identify ₹10: wrong then right
mount(idx["T2"])
cards = "document.querySelectorAll('.mn-card')"
# the reveal is up only while its (stubbed, 60 ms) VO plays + 0.5 s, so record whether it EVER showed
js("window.__rev=false; const r=document.querySelector('.mn-reveal'); new MutationObserver(()=>{ if(r.classList.contains('show')) window.__rev=true; }).observe(r,{attributes:true});")
js(cards + "[1].click()"); w(0.6); shot("T2_wrong"); w(0.8)
check("T2 wrong -> reveal shown + card red", js("return window.__rev && " + cards + "[1].classList.contains('mn-bad')"))
check("T2 wrong VO", "vo_t2_wrong" in st()["said"], st())
w(1.2)
js(cards + "[0].click()"); w(0.6); shot("T2_right")
check("T2 right -> green + nav on", js("return " + cards + "[0].classList.contains('mn-ok')") and st()["nav"], st())
check("T2 correct text", js("return document.querySelector('.mn-pick-fb').textContent") == "शाबाश! यह दस रुपये का नोट है।")

# ---------------- G2 copy teach
mount(idx["G2"])
w(0.2); check("G2 price tag pulses with VO1", js("return document.querySelector('.mn-tag').classList.contains('mn-pulse')"))
w(5.8)
s = st(); check("G2 demo placed ONLY the ₹10 note (कुल ₹10)", s["total"] == "₹10" and s["placed"] == 1, s)
check("G2 waiting ₹1 coin GLOWS (no pulse) and is draggable", js("return src('c1').classList.contains('mn-hintglow-on') && !src('c1').classList.contains('mn-pulse')"))
for n in range(4):
    js("drag(src('c1'), document.querySelector('.mn-target'))"); w(1.2)
s = st(); shot("G2_done")
check("G2 child places 4 coins -> ₹14 finished", s["total"] == "₹14" and s["finished"] and s["nav"], s)
check("G2 equation", js("return document.querySelector('.mn-eq').textContent") == "₹10 + ₹1 + ₹1 + ₹1 + ₹1 = ₹14")
check("G2 item card NOT turned green", js("return !document.querySelector('.mn-item').classList.contains('mn-bought')"))
check("G2 equation strip in tray colours (not green)", js("return getComputedStyle(document.querySelector('.mn-eq')).backgroundColor") == "rgb(255, 248, 231)")

# ---------------- G3 chips teach: ₹1 is wrong
mount(idx["G3"]); w(0.15)
check("G3 heading shows at once", st()["prompt"] == "₹20 बनाइए।", st())
w(4.3)
js("drag(src('c1'), document.querySelector('.mn-target'))"); w(0.1)
check("G3 wrong drop shakes the drop zone", js("return document.querySelector('.mn-target').classList.contains('mn-shake')")); w(0.7)
s = st(); check("G3 ₹1 rejected + VO6", s["total"] == "₹10" and "vo_g3_wrong" in s["said"], s)
js("drag(src('c10'), document.querySelector('.mn-target'))"); w(1)
s = st(); check("G3 ₹10 coin -> ₹20 finished", s["total"] == "₹20" and s["finished"], s)

# ---------------- G4 chocolate: tolerance ladder then tens ladder
mount(idx["G4"]); w(0.6)
T = "document.querySelector('.mn-target')"
for n in range(5): js("drag(src('c1'), %s)" % T); w(0.35)
check("G4 5 coins -> ₹5", st()["total"] == "₹5", st())
js("drag(src('c1'), %s)" % T); w(0.6); s1 = st()
js("drag(src('c1'), %s)" % T); w(0.6); s2 = st(); shot("G4_tol_a2")
js("drag(src('c1'), %s)" % T); w(0.6); s3 = st(); shot("G4_tol_a3")
check("G4 6th ₹1 A1 bounce, no VO", s1["total"] == "₹5" and not any(x.startswith("vo_g4_o") for x in s1["said"]), s1)
check("G4 A2 VO 'कुल ₹5 हैं…'", "vo_g4_o5" in s2["said"], s2)
check("G4 A3 VO + ₹1 disabled + ₹10 glows", "vo_tens_use_coin_20" in s3["said"] and "c1" in s3["off"] and "c10" in s3["glow"], s3)
js("drag(src('c10'), %s)" % T); w(0.4); js("drag(src('c10'), %s)" % T); w(0.8)
s = st(); shot("G4_done")
check("G4 -> ₹25 finished, heading stays «₹25 बनाइए।»", s["finished"] and s["prompt"] == "₹25 बनाइए।", s)
# tens ladder on a fresh mount
mount(idx["G4"]); w(0.6)
js("drag(src('c10'), %s)" % T); w(0.3); js("drag(src('c10'), %s)" % T); w(0.3)
for n in range(3): js("drag(src('c10'), %s)" % T); w(0.6)
s = st()
check("G4 tens ladder A3: ₹10 off, ₹1 glows, VO", "c10" in s["off"] and "c1" in s["glow"] and "vo_ones_use_5" in s["said"], s)
check("G4 tens A2 VO said", "vo_g4_t20" in js("return window.__said"), js("return window.__said"))

# ---------------- P2 toffee: five ₹1 coins centred in the drop zone
mount(idx["P2"]); w(0.6)
for n in range(5): js("drag(src('c1'), %s)" % T); w(0.3)
w(0.5)
off = js("""const z=document.querySelector('.mn-target').getBoundingClientRect(), r=document.querySelector('.mn-row-o').getBoundingClientRect();
  return [Math.round((r.left+r.width/2)-(z.left+z.width/2)), Math.round((r.top+r.height/2)-(z.top+z.height/2))];""")
check("P2 coins centred in the drop zone (x, y offset ≤ 3 px)", abs(off[0]) <= 3 and abs(off[1]) <= 3, off); shot("P2_done")

# ---------------- P3 juice: completes on its own at ₹17 (no «हो गया», round 2d)
mount(idx["P3"]); w(0.6)
check("P3 has no check button", js("return !document.querySelector('.mn-check')"))
js("drag(src('n10'), %s)" % T); w(0.3)
for n in range(7): js("drag(src('c1'), %s)" % T); w(0.3)
w(0.5); s = st(); shot("P3_done")
check("P3 -> ₹17 finished by itself", s["total"] == "₹17" and s["finished"], s)

# ---------------- P4 completion list
mount(idx["P4"]); w(3.2); shot("P4_done")
check("P4 5 green rows with ticks, all shown", js("return document.querySelectorAll('.mn-li-ok:not(.mn-li-wait) .mn-li-tick').length") == 5)
check("P4 celebrating Pari", js("return !!document.querySelector('.mn-fin-pari')"))

# ---------------- M1 shop (round 2f layout)
mount(idx["M1"]); w(1); shot("M1_choose")
check("M1 6 items on the stall, prices ascending", js("return [...document.querySelectorAll('.sg-cell2 .sg-price')].map(e=>e.textContent).join(',')") == "₹14,₹25,₹35,₹42,₹60,₹65")
check("M1 no basket counter", js("return !document.querySelector('.sg-counter')"))
js("document.querySelectorAll('.sg-cell2')[0].click()"); w(1.4); shot("M1_make")
check("M1 make view for ₹14", st()["prompt"] == "₹14 बनाइए।", st())
check("M1 make view: no Pari, no undo, no running total", js("return !document.querySelector('.sg-make2 .sg-pari-sm') && !document.querySelector('.sg-undo') && !document.querySelector('.sg-make2 .mn-total')"))
check("M1 tray has ₹10 note, ₹10 coin, ₹1 coin", js("return [...document.querySelectorAll('.sg-make2 .mn-bank .mn-src')].map(e=>e.dataset.kind).join(',')") == "n10,c10,c1")
chk = "document.querySelector('.sg-checkpill')"
check("M1 जाँचें in the arrow's place, disabled with nothing placed", js("return " + chk + ".disabled && document.getElementById('navBtn').style.display === 'none'"))
TT = "document.querySelector('.sg-make2 .mn-target')"
def dragk(k): js("drag(src('%s'), %s)" % (k, TT)); w(0.35)
js("tap(src('c1'))"); w(0.5)
check("M1 a TAP on currency does not add it", js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length") == 0)
js("""window.__said=[]; window.__ghosts=0; new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('mn-ghost')) window.__ghosts++; }))).observe(document.getElementById('stage'),{childList:true});""")
dragk("c1"); w(0.9); shot("M1_tip_ghost"); w(3.2)
check("M1 first placed piece: drag-back tip spoken", "vo_m_tip" in js("return window.__said"), js("return window.__said"))
check("M1 tip ghost travels back to the tray exactly 2 times", js("return window.__ghosts") == 2, js("return window.__ghosts"))
js("(function(el){const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;PE('pointerdown',x,y,el);PE('pointerup',x,y);})(document.querySelector('.sg-make2 .mn-target .mn-placed'))"); w(0.6)
check("M1 a TAP on a placed coin does nothing", js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length") == 1)
js("drag(document.querySelector('.sg-make2 .mn-target .mn-placed'), src('c1'))"); w(0.8)
check("M1 drag it back out -> tray empty", js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length") == 0)
js("window.__said=[]"); dragk("c1"); w(1.0)
check("M1 tip is NOT repeated", "vo_m_tip" not in js("return window.__said"), js("return window.__said"))
js("drag(document.querySelector('.sg-make2 .mn-target .mn-placed'), src('c1'))"); w(0.8)
dragk("n10"); dragk("c1"); dragk("c1"); js(chk + ".click()"); w(1.2)
check("M1 less -> VO less + tray emptied", "vo_m_less" in js("return window.__said") and js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length") == 0)
dragk("n10"); dragk("n10"); js(chk + ".click()"); w(1.2)
dragk("n10"); dragk("c10"); js(chk + ".click()"); w(1.2)
check("M1 more VO", "vo_m_more" in js("return window.__said"))
for k in ["c10", "n10", "c1", "c1", "c1", "c1", "c1"]: dragk(k)
n = js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length")
check("M1 after 3 wrong: caps hold at 1 ten + 4 ones", n == 5, n)
offk = js("return [...document.querySelectorAll('.sg-make2 .mn-bank .mn-src.mn-off')].map(e=>e.dataset.kind)")
check("M1 capped currencies inactive", set(offk) == {"n10", "c10", "c1"}, offk)
# drag a placed ₹1 back OUT of the drop zone = undo
js("drag(document.querySelectorAll('.sg-make2 .mn-row-o .mn-placed')[3], src('c1'))"); w(0.8)
check("M1 drag-back returns the coin + re-activates ₹1", js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed').length") == 4
      and "c1" not in js("return [...document.querySelectorAll('.sg-make2 .mn-bank .mn-src.mn-off')].map(e=>e.dataset.kind)"))
dragk("c1"); js(chk + ".click()"); w(0.4); shot("M1_win")
check("M1 first purchase = detailed OST", st()["prompt"] == "बहुत बढ़िया! ₹10 का 1 सिक्का और ₹1 के 4 सिक्के मिलाकर ₹14 बने।", st()["prompt"])
check("M1 detailed VO chosen by actual currency", "vo_m_det_14_0_1" in js("return window.__said"), js("return window.__said"))
w(1.6)
check("M1 back to stall, apple green + ticked + disabled", js("return !!document.querySelector('.sg-choose') && document.querySelectorAll('.sg-cell2')[0].classList.contains('sg-sold')"))
check("M1 जाँचें removed on the stall", js("return !document.querySelector('.sg-checkpill')"))
for i in range(1, 6):
    price = js("return CARD.slides[arguments[0]].data.items[arguments[1]].price", idx["M1"], i)
    js("document.querySelectorAll('.sg-cell2')[arguments[0]].click()", i); w(1.2)
    for _ in range(price // 10): dragk("n10")
    for _ in range(price % 10): dragk("c1")
    js(chk + ".click()"); w(2.6)
    if i == 1: check("M1 2nd purchase = playful line", "vo_m_ok_oranges" in js("return window.__said"))
    if i == 5: check("M1 tip never spoken again on later items", js("return window.__said.filter(x=>x==='vo_m_tip').length") == 0)
    if i == 4: shot("M1_stall_5sold")
shot("M1_complete")
check("M1 complete view + nav", js("return !!document.querySelector('.sg-complete')") and st()["nav"], st())
check("M1 total ₹241", js("return document.querySelector('.sg-till-v').textContent") == "₹241")

errs = [l["message"] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:5])
check("no 404s", not MISSING, MISSING[:8])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
