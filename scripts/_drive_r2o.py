# -*- coding: utf-8 -*-
"""Dev-only checks for round 2o: one-time teaching reminder, struck VOs gone, drop sounds, shop
inactivity ghost, transitions every crossing / no double-fire / dev ▶.   (DIST=1 for the delivery copy)"""
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
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750")
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
d.get("http://127.0.0.1:%d/%s?dev=1" % (port, PAGE)); time.sleep(4)
js = d.execute_script
js(r"""
window.__said = []; window.__sfx = []; window.__ghosts = 0;
try{ stopAudio(); }catch(e){}
window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setTimeout(()=>{ if(cb) cb(); }, 60); };
const _P = window.playSfx; window.playSfx = function(id){ window.__sfx.push(id); };
new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('mn-ghost')) window.__ghosts++; }))).observe(document.getElementById('stage'),{childList:true});
document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
window.C = (el)=>{ const r = el.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
window.PE = (type, x, y, tgt)=> (tgt||document).dispatchEvent(new PointerEvent(type, {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true}));
window.drag = (src, dst)=>{ const [x0,y0] = C(src), [x1,y1] = C(dst);
  PE('pointerdown', x0, y0, src); for(let i=1;i<=6;i++) PE('pointermove', x0+(x1-x0)*i/6, y0+(y1-y0)*i/6); PE('pointerup', x1, y1); };
window.src = (k)=> document.querySelector('.mn-src.mn-' + ({n10:'note', c10:'c10', c1:'c1'})[k]);
""")
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
said = lambda: js("return window.__said")
T = "document.querySelector('.mn-target')"

# ---- copy ₹14: struck lines gone, reminder ONCE after ~10 s, drop sounds
js("mountSlide(arguments[0]); window.__said=[]; window.__sfx=[];", idx["G2"]); time.sleep(4)
check("G2 struck VO4/VO6 never spoken", not any(x in ("vo_g2_4", "vo_g2_6") for x in said()), said())
check("G2 note demo plays the NOTE drop sound", "sfx_drop_note" in js("return window.__sfx"), js("return window.__sfx"))
time.sleep(9.0); n1 = said().count("vo_g2_idle")
time.sleep(13.0); n2 = said().count("vo_g2_idle")
check("G2 reminder «सिक्के को ऊपर वाली ट्रे में रखिए।» once after ~10 s, not repeated", n1 == 1 and n2 == 1, (n1, n2))
js("window.__sfx=[]"); js("drag(src('c1'), %s)" % T); time.sleep(0.6)
check("G2 a dropped ₹1 plays the COIN drop sound", "sfx_drop_coin" in js("return window.__sfx"), js("return window.__sfx"))
for i in range(3): js("drag(src('c1'), %s)" % T); time.sleep(1.0)
check("G2 'आखिरी सिक्का।' before the last coin", "vo_g2_7" in said(), said())
time.sleep(0.8)
anim = js("const i=document.querySelector('.mn-target.mn-done .mn-placed.mn-glow img'); return i ? getComputedStyle(i).animationName : null")
check("G2 solved currency has the strong breathing glow", anim == "mnSolvedGlow", anim)
check("G2 closing line ends at «₹14।» (struck tail gone)", js("return CARD.assets.audio_text.vo_g2_done").endswith("चौदह रुपये।"), js("return CARD.assets.audio_text.vo_g2_done"))
check("G2 heading stays «₹14 बनाइए» (no equation in the panel)", js("return document.getElementById('promptText').textContent") == "₹14 बनाइए")

# ---- chips ₹20: new VO3, single reminder line
check("G3 VO3 = «कुल ₹10 हुए। ₹20 के लिए ₹10 और रखिए।»", js("return CARD.assets.audio_text.vo_g3_3") == "कुल दस रुपये हुए। बीस रुपये के लिए दस रुपये और रखिए।")
check("G3 struck reminder «अब तुम एक और…» removed", js("return !CARD.assets.audio_text.vo_g3_idle1"))

# ---- guided practice prompts (first full, the rest short), heading never the equation
P = js("return ['G4','P1','P2','P3'].map(id=>CARD.assets.audio_text[CARD.slides.find(s=>s.id===id).audio.prompt])")
check("G4 keeps the full instruction", P[0].count("।") == 2, P[0])
check("P1/P2/P3 short (one sentence)", all(x.count("।") == 1 for x in P[1:]), P[1:])
js("mountSlide(arguments[0]); window.__said=[];", idx["P1"]); time.sleep(0.8)
for k in ["n10", "n10", "n10", "c1", "c1", "c1", "c1", "c1"]: js("drag(src('%s'), %s)" % (k, T)); time.sleep(0.3)
time.sleep(0.8)
check("P1 heading stays «₹35 बनाइए।» after solving", js("return document.getElementById('promptText').textContent") == "₹35 बनाइए।")

# ---- shop: inactivity ghost on the make screen, not the answer, capped
js("mountSlide(arguments[0]); window.__said=[];", idx["M1"]); time.sleep(1.0)
js("document.querySelectorAll('.sg-cell2')[0].click()"); time.sleep(1.2)
js("window.__ghosts=0")
time.sleep(9.0); g0 = js("return window.__ghosts")
time.sleep(2.5); g1 = js("return window.__ghosts")
check("M1 no ghost before ~10 s idle, one ghost at ~10 s (first item)", g0 == 0 and g1 == 1, (g0, g1))
time.sleep(16.0); g2 = js("return window.__ghosts")
check("M1 second ghost ~15 s later", g2 == 2, g2)
check("M1 ghost does not place money (answer not shown)", js("return document.querySelectorAll('.sg-make2 .mn-target .mn-placed:not(.mn-slot)').length") == 0)

# ---- transitions
def gate_seen(action, wait=1.2):
    js("window.__gate=0; const g=document.getElementById('phaseGate'); window.__go=new MutationObserver(()=>{ if(g.classList.contains('show')) window.__gate=1; }); window.__go.observe(g,{attributes:true});")
    js(action); time.sleep(wait)
    return js("return window.__gate")
for rnd in (1, 2):
    js("mountSlide(arguments[0])", idx["T4"]); time.sleep(0.5)
    seen = gate_seen("document.getElementById('navBtn').disabled=false; document.getElementById('navBtn').click(); document.getElementById('navBtn').click();")
    check("transition T4->G1 shows on pass %d (double tap on the arrow)" % rnd, seen == 1)
    time.sleep(7.5)
    check("  ...and lands on G1 after it (pass %d)" % rnd, js("return CARD.slides[state.idx].id") == "G1", js("return CARD.slides[state.idx].id"))
js("mountSlide(arguments[0])", idx["G4"]); time.sleep(0.5)
seen = gate_seen("document.querySelectorAll('#devNav .dev-nav-btn')[3].click()")
check("dev ▶ across a round (G4->P1) shows the transition", seen == 1)
time.sleep(5.5)
js("mountSlide(arguments[0])", idx["P2"]); time.sleep(0.5)
seen = gate_seen("document.querySelectorAll('#devNav .dev-nav-btn')[3].click()", 0.8)
check("dev ▶ inside a round (P2->P3) shows NO transition", seen == 0 and js("return CARD.slides[state.idx].id") == "P3")

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
