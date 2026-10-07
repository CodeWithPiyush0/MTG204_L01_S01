# -*- coding: utf-8 -*-
"""Dev-only: play the celebration with the REAL audio and score the lip-sync of the three-sheet Swiftie.
python scripts/_celcheck.py [shot_prefix]   (DIST=1 to test the delivery copy)"""
import os, sys, time, threading, http.server, socketserver, functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); PAGE = "MTG2A04_L01_S01.html"
if os.environ.get("DIST"): ROOT, PAGE = os.path.join(ROOT, "dist", "MTG2A04_L01_S01"), "index.html"
OUT = sys.argv[1] if len(sys.argv) > 1 else None
class TS(socketserver.ThreadingMixIn, socketserver.TCPServer): daemon_threads = True; allow_reuse_address = True
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = TS(("127.0.0.1", 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
o = Options(); o.add_argument("--headless=new"); o.add_argument("--window-size=1333,750"); o.add_argument("--autoplay-policy=no-user-gesture-required")
d = webdriver.Chrome(options=o)
if os.environ.get("NOGATE"):
    d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source":
        "Object.defineProperty(window,'__assetGateFn',{configurable:true,set(v){},get(){return ()=>Promise.resolve();}});"})
d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(4)
t_w = time.time()    # as in real use: the celebration is never reached before the loader's preload ends
while time.time() - t_w < 40 and d.execute_script("return window.__preloadMs == null && !!window.__assetGateP"): time.sleep(0.2)
time.sleep(1)
if os.environ.get("NOKEEP"): d.execute_script("window.__preloadKeep = []")
js = d.execute_script
js("""try{stopAudio()}catch(e){}; document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
  /* the recorder's clock = when the celebration clip's audio source really started (+ output latency),
     independent of any paint: isPlaying is only seen on the next paint, which can run late */
  const _st=AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start=function(when){
    try{ const c=this.context, A=CARD.end_anim; if(this.buffer && Math.abs(this.buffer.duration*1000 - A.bits.length*A.step_ms) < 150)
      window.__srcAt = performance.now() + ((c.baseLatency||0)+(c.outputLatency||0))*1000; }catch(e){}
    return _st.apply(this, arguments); };
  window.__log=[]; window.__t0=0; window.__pre=[]; window.__m0=performance.now();
  /* the recorder is registered AFTER the mount, so in every frame it runs after the sprite's own rAF
     callback and samples exactly what that paint shows (sampling first compared the previous frame's
     mouth with the current audio — wrong by a whole stall whenever a paint was late) */
  window.__rec = function rec(){ const sp=document.getElementById('celSprite'); if(isPlaying && !window.__t0) window.__t0=(window.__srcAt || performance.now());
    if(sp && sp.dataset.f && !window.__t0) window.__pre.push([Math.round(performance.now()-window.__m0), sp.dataset.sheet, +sp.dataset.f]);
    if(sp && sp.dataset.f) window.__log.push([window.__t0?Math.round(performance.now()-window.__t0):-1, sp.dataset.sheet, +sp.dataset.f, isPlaying?1:0]);
    requestAnimationFrame(rec); };
  window.__srcs=[]; const _pl=window.play; window.play=function(s,cb){ window.__srcs.push(String(s||'').split('/').pop().split('.')[0]); return _pl.apply(this, arguments); };
  mountSlide(CARD.slides.length-1); requestAnimationFrame(window.__rec);""")
t_start = time.time()
for name, at in (("pre", 0.15), ("jump", 0.8), ("talk", 3.0), ("after", 8.5)):
    while time.time() - t_start < at: time.sleep(0.01)
    if OUT: d.save_screenshot(OUT + "_" + name + ".png")
log = js("return window.__log"); A = js("return CARD.end_anim")
bits, step = A["bits"], A["step_ms"]
TOPEN = set(A["talk"]["open"])
vo = [x for x in log if x[0] >= 0 and x[3] == 1]
gaps = [b[0] - a[0] for a, b in zip(vo, vo[1:])]
big = sorted(((b[0] - a[0], a[0], a[1] + ":" + str(a[2]), b[1] + ":" + str(b[2])) for a, b in zip(vo, vo[1:])), reverse=True)[:3]
print("longest stalls (gap ms, at t, from -> to):", big)
print("VO ran %d ms, %d samples, frame gap median %d ms / max %d ms" % (vo[-1][0] if vo else 0, len(vo), sorted(gaps)[len(gaps)//2] if gaps else 0, max(gaps) if gaps else 0))
print("sheets in order:", [k for i, k in enumerate(x[1] for x in vo) if i == 0 or k != vo[i - 1][1]])
sh = [(t, f) for t, s, f, p in vo if s == "shabaash"]
print("shabaash frames played:", sorted({f for t, f in sh}))
tk = [(t, f) for t, s, f, p in vo if s == "talk"]
ok = sum(1 for t, f in tk if (f in TOPEN) == (bits[min(len(bits) - 1, t // step)] == "1"))
print("TALK: %d samples, mouth matches the VO in %.1f%%" % (len(tk), 100.0 * ok / max(1, len(tk))))
bad = [(t, f) for t, f in tk if (f in TOPEN) != (bits[min(len(bits) - 1, t // step)] == "1")]
def near_edge(t, w=25):
    b = lambda x: bits[max(0, min(len(bits) - 1, x // step))]
    return b(t - w) != b(t) or b(t + w) != b(t)
edge = [x for x in bad if near_edge(x[0])]
print("  mismatches: %d, of which %d sit within 25 ms (one render frame) of a syllable edge" % (len(bad), len(edge)))
print("  mismatches NOT at an edge:", [x for x in bad if not near_edge(x[0])][:12])
after = [(s, f) for t, s, f, p in log if p == 0 and t > 0]
IOPEN = set(range(5, 24))
print("AFTER VO: sheets", sorted({s for s, f in after}), "| any open-mouth idle frame:", any(s == "idle" and f in IOPEN for s, f in after))
jumps = []
for (a, b) in zip(vo, vo[1:]):
    if a[1] != b[1]: jumps.append((b[0], a[1] + ":" + str(a[2]), "->", b[1] + ":" + str(b[2])))
print("sheet switches:", jumps)
# round 2r: she jumps and lands FIRST (silent but for the sfx), THEN the line starts, lip-synced from its first syllable
pre = js("return window.__pre"); vo_at = js("return window.__t0 - window.__m0")
pre_frames = sorted({f for t, s, f in pre if s == "shabaash"})
seq = [(t, f) for i, (t, s, f) in enumerate(pre) if i == 0 or f != pre[i - 1][2]]
pg = [b[0] - a[0] for a, b in zip(pre, pre[1:])]
print("JUMP timeline (ms, frame):", seq[:40], "| paint gaps >60 ms:", [(pre[i][0], g) for i, g in enumerate(pg) if g > 60])
print("BEFORE VO: %d ms of jump+landing, shabaash frames %s..%s (%d distinct), sheets %s" % (vo_at, pre_frames[:1], pre_frames[-1:], len(pre_frames), sorted({s for t, s, f in pre})))
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
check("only the celebration line is spoken on this screen", js("return window.__srcs") == ["vo_cel_prompt"], js("return window.__srcs"))
check("r2r: the line starts only after the jump + landing (1.6 s + up to 0.7 s settle)", 1500 <= vo_at <= 2450, vo_at)
check("r2r: the jump AND the landing play before the voice (time-based: a stalled paint may skip a frame)",
      len(pre_frames) >= 26 and min(pre_frames) <= 1 and {30, 35} <= set(pre_frames), pre_frames)
check("r2r: from the first voiced instant she is on the talk sheet", bool(vo) and vo[0][1] == "talk", vo[:2])
check("r2r: the line is «बहुत बढ़िया, दोस्त! तुमने कमाल कर दिया!»", js("return CARD.assets.audio_text.vo_cel_prompt") == "बहुत बढ़िया, दोस्त! तुमने कमाल कर दिया!")
check("lip-sync: mismatches sit on syllable edges (<=2 strays: headless paint stalls of 150-190 ms)", len([x for x in bad if not near_edge(x[0])]) <= 2 and 100.0 * ok / max(1, len(tk)) >= 85)
check("arrow pulses after the line", js("return document.getElementById('endBtn').classList.contains('cel-ready')"))
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
