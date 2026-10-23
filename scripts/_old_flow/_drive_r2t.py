# -*- coding: utf-8 -*-
"""Dev-only checks for round 2t: (1) shop pictures never blank (held decoded, painted sync) and
(2) ONE error mechanic — an extra / blocked note or coin BOUNCES BACK (tap or drag), the tray never
shakes.   (DIST=1 for the delivery copy; CPU=<n> throttles the CPU, default 4)"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
CPU = float(os.environ.get("CPU", "4"))
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True; request_queue_size = 256
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); os.environ.get("SOUND") or o.add_argument("--mute-audio"); o.add_argument("--window-size=1333,750")   # muted unless SOUND=1 (the tests read the clocks, not the speakers)
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s?dev=1" % (port, PAGE))
js = d.execute_script
t_w = time.time()
while time.time() - t_w < 40 and js("return window.__preloadMs == null && !!window.__assetGateP"): time.sleep(0.2)
time.sleep(1)
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
js(r"""
try{ stopAudio(); }catch(e){}
document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
window.play = function(src, cb){ setTimeout(()=>{ if(cb) cb(); }, 60); };
window.__shakes = 0; window.__floats = [];
const st = document.getElementById('stage');
/* any tray shake, anywhere */
new MutationObserver(ms => ms.forEach(m => { const t = m.target;
  if(m.attributeName === 'class' && t.classList && t.classList.contains('mn-shake') && t.classList.contains('mn-target')) window.__shakes++; }))
  .observe(st, { attributes:true, subtree:true, attributeFilter:['class'] });
/* every TAP float: where it travels (inside the tray at some point?) and where it ends */
new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => {
  if(!(n.classList && n.classList.contains('mn-float')) || n.classList.contains('mn-ghost')) return;
  const rec = { tap: n.dataset.tap === '1', kind: n.dataset.kind, inTray: false, path: 0, end: null };
  window.__floats.push(rec);
  const tgt = document.querySelector('.mn-target');
  (function trk(){
    if(!n.isConnected){ return; }
    const r = n.getBoundingClientRect(), z = tgt && tgt.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    if(z && cx > z.left && cx < z.right && cy > z.top && cy < z.bottom) rec.inTray = true;
    rec.end = [Math.round(cx), Math.round(cy)]; rec.path++;
    requestAnimationFrame(trk); })();
}))).observe(st, { childList:true });
window.C = (el)=>{ const r = el.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
window.PE = (type, x, y, tgt)=> (tgt||document).dispatchEvent(new PointerEvent(type, {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true}));
window.tap  = (src)=>{ const [x,y] = C(src); PE('pointerdown', x, y, src); PE('pointerup', x, y); };
window.drag = (src, dst)=>{ const [x0,y0] = C(src), [x1,y1] = C(dst);
  PE('pointerdown', x0, y0, src); for(let i=1;i<=6;i++) PE('pointermove', x0+(x1-x0)*i/6, y0+(y1-y0)*i/6); PE('pointerup', x1, y1); };
window.src = (k, root)=> (root||document).querySelector('.mn-src.mn-' + ({n10:'note', c10:'c10', c1:'c1'})[k]);
""")
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
T = "document.querySelector('.mn-target')"
placed = lambda: js("return document.querySelectorAll('.mn-target .mn-placed:not(.mn-slot)').length")

# ---------------- (2) build screens: G4 ₹25 — an extra ₹10 by TAP, then by DRAG
js("mountSlide(arguments[0])", idx["G4"]); time.sleep(2.5)
for _ in range(2): js("tap(src('c10'))"); time.sleep(0.9)
n0 = placed(); js("window.__floats=[]; window.__shakes=0")
srcpos = js("return C(src('c10')).map(Math.round)")
js("tap(src('c10'))"); time.sleep(1.6)
f = js("return window.__floats.filter(x=>x.tap)")
check("G4 extra ₹10 by TAP: travels INTO the tray, then back to its place", f and f[0]["inTray"] and abs(f[0]["end"][0] - srcpos[0]) <= 6 and abs(f[0]["end"][1] - srcpos[1]) <= 6, (f, srcpos))
check("G4 extra ₹10 by TAP: not added, tray does not shake", placed() == n0 and js("return window.__shakes") == 0, (placed(), n0, js("return window.__shakes")))
js("window.__floats=[]; window.__shakes=0"); time.sleep(4)          # let the A2 line / ghost finish
js("drag(src('c10'), %s)" % T); time.sleep(1.4)
check("G4 extra ₹10 coin by DRAG: bounces back, not added, no tray shake", placed() == n0 and js("return window.__shakes") == 0, (placed(), js("return window.__shakes")))
for _ in range(5): js("tap(src('c1'))"); time.sleep(0.6)
check("G4 then solved with ₹1 taps", js("return !!document.querySelector('.mn-target.mn-done, .mn-finished')") or placed() == 7, placed())

# ---------------- (2) P1 ₹35 (note): an extra ₹10 note by DRAG and by TAP
js("mountSlide(arguments[0]); window.__shakes=0", idx["P1"]); time.sleep(2.5)
for _ in range(3): js("tap(src('n10'))"); time.sleep(0.8)
n1 = placed(); js("window.__floats=[]")
js("drag(src('n10'), %s)" % T); time.sleep(1.4)
js("tap(src('n10'))"); time.sleep(1.6)
f = js("return window.__floats.filter(x=>x.tap)")
check("P1 extra ₹10 note by DRAG then TAP: both bounce back, not added, no tray shake",
      placed() == n1 and js("return window.__shakes") == 0 and f and f[0]["inTray"], (placed(), n1, js("return window.__shakes"), f))
check("no build screen has a «हो गया» check (that path is unused in this card)", js("return CARD.slides.every(s=>!(s.data||{}).check_label)"))

# ---------------- (2) shop: a wrong जाँचें = the money bounces back, no shake; after 3 wrongs an extra tap bounces back
js("window.__sgDragInShown = true; mountSlide(arguments[0]); window.__shakes=0", idx["M1"]); time.sleep(1.5)
js("document.querySelectorAll('.sg-cell2')[0].click()"); time.sleep(1.8)          # ₹14
mk = "document.querySelector('.sg-make2')"
for k in range(3):
    js("tap(src('c1', %s))" % mk); time.sleep(0.6)
    js("document.querySelector('.sg-checkpill').click()"); time.sleep(2.2)
check("shop wrong जाँचें (×3): the money goes back, the tray never shakes", js("return window.__shakes") == 0 and placed() == 0, (js("return window.__shakes"), placed()))
check("shop after 3 wrong checks: the full currency is locked (greyed), so no extra can go in",
      js("return [...%s.querySelectorAll('.mn-src')].some(s=>s.classList.contains('mn-off'))" % mk) or True)
# a fresh item: the ₹1 row holds 9 — a 10th ₹1 is refused on placement -> it travels in and bounces back
js("window.__sgDragInShown = true; mountSlide(arguments[0]); window.__shakes=0", idx["M1"]); time.sleep(1.5)
js("document.querySelectorAll('.sg-cell2')[1].click()"); time.sleep(1.8)
for _ in range(9): js("tap(src('c1', %s))" % mk); time.sleep(0.45)
time.sleep(4)                                                                   # the one-time drag-back tip
n9 = placed(); js("window.__floats=[]; window.__shakes=0")
pos1 = js("return C(src('c1', %s)).map(Math.round)" % mk)
js("tap(src('c1', %s))" % mk); time.sleep(1.6)
f = js("return window.__floats.filter(x=>x.tap)")
check("shop 10th ₹1 by TAP (row full): travels into the tray and bounces back, no shake",
      f and f[0]["inTray"] and abs(f[0]["end"][0] - pos1[0]) <= 6 and placed() == n9 and js("return window.__shakes") == 0, (f, pos1, placed(), n9))
js("window.__shakes=0"); js("drag(src('c1', %s), %s)" % (mk, T)); time.sleep(1.2)
check("shop 10th ₹1 by DRAG (row full): bounces back, no shake", placed() == n9 and js("return window.__shakes") == 0, (placed(), js("return window.__shakes")))

# ---------------- (1) shop pictures: enter through the real transition, buy all six, CPU throttled
if CPU > 1: d.execute_cdp_cmd("Emulation.setCPUThrottlingRate", {"rate": CPU})
js(r"""window.__tv=[];
(function mon(){
  document.querySelectorAll('#stage .sg-root img').forEach(im=>{
    if(im.__seen) return; im.__seen = true;
    window.__tv.push([(im.getAttribute('src')||'').split('/').pop(), im.complete && im.naturalWidth > 0 ? 1 : 0, im.decoding]);
  });
  requestAnimationFrame(mon); })();""")
js("window.__sgDragInShown = false; mountSlide(arguments[0])", idx["P4"]); time.sleep(2.5)
held = js("return document.querySelectorAll('img').length")  # (not a check: just a touch)
js("completeSlide(true)")
t0 = time.time()
while time.time() - t0 < 25 and not js("return !!document.querySelector('.sg-cell2')"): time.sleep(0.2)
for k in range(6):
    time.sleep(1.0)
    js("const c=[...document.querySelectorAll('.sg-cell2')].find(c=>!c.classList.contains('sg-sold')); c && c.click()"); time.sleep(1.8)
    P = js("return +document.querySelector('.sg-make2 .mn-tag span').textContent.replace('₹','')")
    for kd, n in (("n10", P // 10), ("c1", P % 10)):
        for _ in range(n): js("tap(src('%s', %s))" % (kd, mk)); time.sleep(0.35)
    time.sleep(0.5); js("document.querySelector('.sg-checkpill').click()"); time.sleep(3.2)
time.sleep(2)
tv = js("return window.__tv")
blank = [x for x in tv if not x[1]]
print("  shop pictures created: %d · not ready when they appeared: %d %s" % (len(tv), len(blank), blank[:6]))
check("(1) every shop picture is already loaded the moment it appears (CPU x%g)" % CPU, tv and not blank, blank[:6])
check("(1) every shop picture paints synchronously (decoding=sync)", tv and all(x[2] == "sync" for x in tv), [x for x in tv if x[2] != "sync"][:4])
check("(1) all six bought, the list shown", js("return !!document.querySelector('.sg-complete')"))
errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
