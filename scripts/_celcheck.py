# -*- coding: utf-8 -*-
"""Dev-only, REAL audio (muted unless SOUND=1): the end screen, round 25 = HI02H11_L02_S02's end screen
(celebration_kit Swiftie + its CELEBRATION.mount wrapper, the engine's own button).
  - the jump (the kit's शाबाश sheet) plays first, silent but for the celebration sound; then the line
  - from the line's first voiced instant she is the kit's player; mouth = the kit track on its own clock
  - after the line: the idle sheet, mouth shut
  - the button: the reference's exactly - shown + glowing from the start, pressable during the line
python scripts/_celcheck.py [shot_prefix]   (DIST=1 to test the delivery copy)"""
import os, sys, time, threading, http.server, socketserver, functools
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
# 1382 x 850: the window the reference measured its button in (r82: 124 x 82 at 620, 485 once settled)
o = Options(); o.add_argument("--headless=new"); os.environ.get("SOUND") or o.add_argument("--mute-audio"); o.add_argument("--window-size=1382,850"); o.add_argument("--autoplay-policy=no-user-gesture-required")   # muted unless SOUND=1 (the tests read the clocks, not the speakers)
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
d = webdriver.Chrome(options=o)
fails = []
def check(label, cond, info=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else "   " + str(info)))
    if not cond: fails.append(label)
try:
    d.get("http://127.0.0.1:%d/%s" % (port, PAGE)); time.sleep(3)
    t_w = time.time()    # as in real use: the end screen is never reached before the loader's preload ends
    while time.time() - t_w < 40 and d.execute_script("return window.__preloadMs == null && !!window.__assetGateP"): time.sleep(0.2)
    time.sleep(1)
    js = d.execute_script
    js("""try{stopAudio()}catch(e){}; document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
      window.__srcs = []; const _pl = window.play; window.play = function(s, cb){ window.__srcs.push(String(s||'').split('/').pop().split('.')[0]); window.__playAt = performance.now(); return _pl.apply(this, arguments); };
      window.__sig = []; const _em = SwiftPAL.emit; SwiftPAL.emit = function(n, p){ window.__sig.push(n); return _em.apply(this, arguments); };
      window.__log = []; window.__m0 = performance.now();
      /* registered AFTER the mount: in every frame it runs after the players' own rAF callbacks, so it samples
         exactly what that paint shows. The VISIBLE .swc-sprite is the one on screen (the wrapper's jump
         sprite, then the kit's player). */
      window.__rec = function rec(){
        const box = document.getElementById('celBox');
        const sp = box ? [...box.querySelectorAll('.swc-sprite')].find(e => e.style.visibility !== 'hidden') : null;
        const eb = document.getElementById('endBtn'), cs = getComputedStyle(eb);
        if(sp) window.__log.push([Math.round(performance.now() - window.__m0), sp.dataset.sheet || '', +(sp.dataset.f || -1),
                                  sp.dataset.t === undefined ? null : +sp.dataset.t, isPlaying ? 1 : 0,
                                  eb.classList.contains('show') && cs.display !== 'none' && cs.pointerEvents !== 'none' && !/grayscale/.test(cs.filter) ? 1 : 0]);   /* shown + pressable (it fades in over ~0.3 s) */
        requestAnimationFrame(rec); };
      mountSlide(CARD.slides.length - 1); requestAnimationFrame(window.__rec);""")
    t_start = time.time()
    for name, at in (("jump", 0.8), ("talk", 2.6), ("after", 7.5)):
        while time.time() - t_start < at: time.sleep(0.01)
        if OUT: d.save_screenshot(OUT + "_" + name + ".png")
        if name == "talk":      # the reference's logic (user's choice): the arrow is pressable while she speaks
            tap = js("""const b = document.getElementById('endBtn'), r = b.getBoundingClientRect();
              const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
              const ok = e === b || b.contains(e); if(ok) e.dispatchEvent(new MouseEvent('click', {bubbles:true}));
              return [ok, isPlaying];""")
    while time.time() - t_start < 9.5: time.sleep(0.05)
    log = js("return window.__log"); A = js("return CARD.end_anim")
    M, track = A["meta"], A["track"]
    bits, step = track["bits"], track.get("step_ms", 25)
    lead = max(0, bits.index("1")); bits2 = "1" + "0" * 8 + bits[lead:]          # the wrapper's arrangement
    TOPEN = set(M["talk"]["open"]); IOPEN = set(range(5, 24))
    vo_at = js("return window.__playAt - window.__m0")
    pre = [x for x in log if x[0] < vo_at]
    kit = [x for x in log if x[3] is not None]                                   # the kit's player, on its clock
    tk = [x for x in kit if x[1] == "talk" and x[4]]
    ok = sum(1 for x in tk if (x[2] in TOPEN) == (bits2[min(len(bits2) - 1, (x[3] + 16) // step)] == "1"))
    def near_edge(t, w=25):
        b = lambda q: bits2[max(0, min(len(bits2) - 1, (q + 16) // step))]
        return b(t - w) != b(t) or b(t + w) != b(t)
    bad = [x for x in tk if (x[2] in TOPEN) != (bits2[min(len(bits2) - 1, (x[3] + 16) // step)] == "1")]
    after = [x for x in log if x[0] > vo_at + 500 and not x[4]]
    sheets = [k for i, k in enumerate(x[1] for x in log) if i == 0 or k != log[i - 1][1]]
    first_voiced = next((x for x in kit if x[4]), None)
    print("  line started %d ms after the screen opened; the kit track %d ms (%d steps)" % (vo_at, track["ms"], len(bits)))
    print("  sheets in order:", sheets, "| jump frames before the line:", sorted({x[2] for x in pre if x[1] == "shabaash"})[:3], "...", len({x[2] for x in pre if x[1] == "shabaash"}))
    print("TALK: %d samples, mouth matches the VO in %.1f%% (mismatches %d, %d at a syllable edge)" %
          (len(tk), 100.0 * ok / max(1, len(tk)), len(bad), len([x for x in bad if near_edge(x[3])])))
    eb = js("const b = document.getElementById('endBtn'), r = b.getBoundingClientRect(); return [b.className, Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height), b.getAttribute('aria-label'), getComputedStyle(b, '::after').content]")
    print("  end button:", eb, "| live from:", next((x[0] for x in log if x[5]), None), "ms | tap during the line:", tap, "-> signals", js("return window.__sig"))
    check("only the celebration line is spoken on this screen", js("return window.__srcs") == ["vo_cel_prompt"], js("return window.__srcs"))
    check("r106: she jumps first (the kit's शाबाश sheet, 30 frames at 45 ms), then the line starts (1.35 s + the opening work)", 1300 <= vo_at <= 2300 and len({x[2] for x in pre if x[1] == "shabaash"}) >= 24, (vo_at, sorted({x[2] for x in pre if x[1] == "shabaash"})))
    check("r85: the kit's player takes over as the line sounds, then talk, then idle", sheets[:1] == ["shabaash"] and "talk" in sheets and sheets[-1] == "idle", sheets)
    check("lip-sync: mouth = the kit track on its clock (>= 95 %, misses only at syllable edges)", tk and 100.0 * ok / len(tk) >= 95 and len([x for x in bad if not near_edge(x[3])]) <= 2, (len(tk), ok, bad[:6]))
    check("after the line: idle sheet, mouth shut", after and all(x[1] == "idle" for x in after[-20:]) and not any(x[1] == "idle" and x[2] in IOPEN for x in after), after[-3:])
    check("the button = the reference's: arrow only, «आगे बढ़ें» as its label, 124 x 82 at (620, 485), glowing", eb[0].split() == ["end-btn", "show", "hint-glow"] and eb[1:5] == [620, 485, 124, 82] and eb[5] == "आगे बढ़ें" and "→" in eb[6], eb)
    check("the button is live from the moment the screen opens (the reference's [30i])", log and log[0][5] == 1 and all(x[5] for x in log), [x for x in log if not x[5]][:3])
    check("a tap during the line goes on (proceed_next) - the reference's logic, by the user's choice", tap == [True, True] and "proceed_next" in js("return window.__sig"), (tap, js("return window.__sig")))
    check("the stock mascot art is never downloaded (data-src, as in the reference)", not js("return performance.getEntriesByType('resource').some(e => /sw_lg_celebrating_anim/.test(e.name))"))
    errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
    check("no console errors", not errs, errs[:4])
finally:
    print("\n%d FAIL" % len(fails), fails)
    d.quit(); srv.shutdown()
