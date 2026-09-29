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
js(cards + "[1].click()"); w(0.5); shot("T2_wrong")
check("T2 wrong -> reveal shown + card red", js("return document.querySelector('.mn-reveal').classList.contains('show') && " + cards + "[1].classList.contains('mn-bad')"))
check("T2 wrong VO", "vo_t2_wrong" in st()["said"], st())
w(1.2)
js(cards + "[0].click()"); w(0.6); shot("T2_right")
check("T2 right -> green + nav on", js("return " + cards + "[0].classList.contains('mn-ok')") and st()["nav"], st())
check("T2 correct text", js("return document.querySelector('.mn-pick-fb').textContent") == "शाबाश! यह दस रुपये का नोट है।")

# ---------------- G2 copy teach
mount(idx["G2"]); w(6)
s = st(); check("G2 demo placed ₹10 + ₹1 (कुल ₹11)", s["total"] == "₹11", s)
for n in range(3):
    js("drag(src('c1'), document.querySelector('.mn-target'))"); w(1.2)
s = st(); shot("G2_done")
check("G2 child places 3 coins -> ₹14 finished", s["total"] == "₹14" and s["finished"] and s["nav"], s)
check("G2 equation", js("return document.querySelector('.mn-eq').textContent") == "₹10 + ₹1 + ₹1 + ₹1 + ₹1 = ₹14")

# ---------------- G3 chips teach: ₹1 is wrong
mount(idx["G3"]); w(4.5)
check("G3 prompt appears with 2nd line", st()["prompt"] == "₹20 बनाइए।", st())
js("drag(src('c1'), document.querySelector('.mn-target'))"); w(0.8)
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
check("G4 -> ₹25 finished, equation in band", s["finished"] and s["prompt"] == "₹10 + ₹10 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 = ₹25", s)
# tens ladder on a fresh mount
mount(idx["G4"]); w(0.6)
js("drag(src('c10'), %s)" % T); w(0.3); js("drag(src('c10'), %s)" % T); w(0.3)
for n in range(3): js("drag(src('c10'), %s)" % T); w(0.6)
s = st()
check("G4 tens ladder A3: ₹10 off, ₹1 glows, VO", "c10" in s["off"] and "c1" in s["glow"] and "vo_ones_use_5" in s["said"], s)
check("G4 tens A2 VO said", "vo_g4_t20" in js("return window.__said"), js("return window.__said"))

# ---------------- P3 juice: check button
mount(idx["P3"]); w(0.6)
for n in range(3): js("drag(src('c1'), %s)" % T); w(0.3)
js("document.querySelector('.mn-check').click()"); w(0.5)
s = st(); check("P3 check under -> VO u3", "vo_p3_u3" in s["said"] and not s["finished"], s)
js("drag(src('n10'), %s)" % T); w(0.3)
for n in range(4): js("drag(src('c1'), %s)" % T); w(0.3)
s = st(); check("P3 reached ₹17 but waits for हो गया", s["total"] == "₹17" and not s["finished"], s)
js("document.querySelector('.mn-check').click()"); w(0.8); shot("P3_done")
check("P3 हो गया -> finished", st()["finished"], st())

# ---------------- M1 shop
mount(idx["M1"]); w(1); shot("M1_choose")
js("document.querySelectorAll('.sg-cell')[0].click()"); w(1.4); shot("M1_make")
check("M1 make view for ₹14", st()["prompt"] == "₹14 बनाइए।", st())
chk = "document.querySelector('.sg-check')"
check("M1 जाँचें disabled with nothing placed", js("return " + chk + ".disabled"))
def tapk(k): js("tap(src('%s'))" % k); w(0.3)
tapk("n10"); tapk("c1"); tapk("c1"); js(chk + ".click()"); w(1.2)
check("M1 less -> VO less + tray emptied", "vo_m_less" in js("return window.__said") and js("return document.querySelectorAll('.sg-amount .mn-placed').length") == 0)
tapk("n10"); tapk("n10"); js(chk + ".click()"); w(1.2)
tapk("n10"); tapk("c10"); js(chk + ".click()"); w(1.2)
check("M1 more VO", "vo_m_more" in js("return window.__said"))
# caps now on: 2nd ten and 5th one must bounce
tapk("c10"); tapk("n10"); tapk("c1"); tapk("c1"); tapk("c1"); tapk("c1"); tapk("c1")
n = js("return document.querySelectorAll('.sg-amount .mn-placed').length")
check("M1 after 3 wrong: caps hold at 1 ten + 4 ones", n == 5, n)
offk = js("return [...document.querySelectorAll('.sg-bank .mn-src.mn-off')].map(e=>e.dataset.kind)")
check("M1 capped currencies inactive", set(offk) == {"n10", "c10", "c1"}, offk)
# undo re-activates
js("document.querySelector('.sg-undo').click()"); w(0.6)
check("M1 undo re-activates ₹1", "c1" not in js("return [...document.querySelectorAll('.sg-bank .mn-src.mn-off')].map(e=>e.dataset.kind)"))
tapk("c1"); js(chk + ".click()"); w(0.4); shot("M1_win")
check("M1 first purchase = detailed OST", st()["prompt"] == "बहुत बढ़िया! ₹10 का 1 सिक्का और ₹1 के 4 सिक्के मिलाकर ₹14 बने।", st()["prompt"])
check("M1 detailed VO chosen by actual currency", "vo_m_det_14_0_1" in js("return window.__said"), js("return window.__said"))
w(2.6)
check("M1 back to stall, counter 1/8", js("return document.querySelector('.sg-counter b').textContent") == "1/8" and js("return !!document.querySelector('.sg-choose')"))
check("M1 apple marked sold", js("return document.querySelectorAll('.sg-cell')[0].classList.contains('sg-sold')"))
# buy the rest quickly (exact amounts)
for i in range(1, 8):
    price = js("return CARD.slides[arguments[0]].data.items[arguments[1]].price", idx["M1"], i)
    js("document.querySelectorAll('.sg-cell')[arguments[0]].click()", i); w(1.2)
    for _ in range(price // 10): tapk("n10")
    for _ in range(price % 10): tapk("c1")
    js(chk + ".click()"); w(3.4)
    if i == 1: check("M1 2nd purchase = playful line", "vo_m_ok_bananas" in js("return window.__said"))
shot("M1_complete")
check("M1 complete view + nav", js("return !!document.querySelector('.sg-complete')") and st()["nav"], st())
check("M1 total ₹284", js("return document.querySelector('.sg-till-v').textContent") == "₹284")

errs = [l["message"] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:5])
check("no 404s", not MISSING, MISSING[:8])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
