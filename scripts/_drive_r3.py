# -*- coding: utf-8 -*-
"""Dev-only checks for round 3 (SME restructure + checklist): the new flow, the teaching screen, the two
sorting screens, ₹14 (ghost) / ₹32 / ₹45 (strict order), the shop's intro + keep-and-correct retry +
ghost hints, the transition titles, the speaker size, the confetti / nudge sounds.   (DIST=1 for dist)"""
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

# ---- static: flow, titles, speaker
ids = js("return CARD.slides.map(s=>s.id+':'+s.type+':'+s.phase)")
check("flow = teach -> sort ₹10 -> sort ₹1 -> ₹14 -> ₹32 -> ₹45 -> shop -> end",
      ids == ["T1:MONEY_INTRO:tutorial", "G1:MONEY_SORT:guided", "G2:MONEY_SORT:guided", "G3:MONEY_BUILD:guided",
              "G4:MONEY_BUILD:guided", "G5:MONEY_BUILD:guided", "M1:SHOP_GAME:practice", "CEL:CELEBRATION:mastery"], ids)
check("no «खरीदारी का खेल!» transition", js("return !CARD.mastery_gate"))
time.sleep(0.5)
titles = js("return [PHASE_GATE_TITLE.tutorial, PHASE_GATE_TITLE.guided, PHASE_GATE_TITLE.practice]")
check("transition titles per checklist", titles == ["चलिए, शुरू करें!", "चलिए, साथ में करें।", "अब आपकी बारी।"], titles)
check("tutorial transition VO says «चलिए, शुरू करें!»", js("return CARD.assets.audio_text.vo_pt_tutorial").endswith("चलिए, शुरू करें!"))
sp = js("const v=document.getElementById('sgVo'); return v ? [Math.round(parseFloat(getComputedStyle(v).width)), Math.round(parseFloat(getComputedStyle(v).height))] : null")
check("speaker button 70 x 70 px", sp == [70, 70], sp)

js(r"""
try{ stopAudio(); }catch(e){}
document.getElementById('startGate').classList.add('hidden'); document.body.classList.remove('is-start');
window.__said = []; window.__sfx = [];
window.play = function(src, cb){ window.__said.push(String(src||'').split('/').pop().split('.')[0]); setTimeout(()=>{ if(cb) cb(); }, 300); };
const _lvb = window._loadVoiceBuffer;
window._loadVoiceBuffer = function(src){ const n = String(src).split('/').pop().split('.')[0]; if(/^sfx_/.test(n)) window.__sfx.push(n); return _lvb.apply(this, arguments); };
window.__ghosts = 0;
new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('mn-ghost')) window.__ghosts++; }))).observe(document.getElementById('stage'),{childList:true});
window.C = (el)=>{ const r = el.getBoundingClientRect(); return [r.left + r.width/2, r.top + r.height/2]; };
window.PE = (type, x, y, tgt)=> (tgt||document).dispatchEvent(new PointerEvent(type, {clientX:x, clientY:y, bubbles:true, button:0, pointerId:1, isPrimary:true}));
window.drag = (src, dst)=>{ const [x0,y0] = C(src), [x1,y1] = C(dst);
  PE('pointerdown', x0, y0, src); for(let i=1;i<=6;i++) PE('pointermove', x0+(x1-x0)*i/6, y0+(y1-y0)*i/6); PE('pointerup', x1, y1); };
window.tap = (el)=>{ const [x,y] = C(el); PE('pointerdown', x, y, el); PE('pointerup', x, y); };
window.src = (k, root)=> (root||document).querySelector('.mn-src.mn-' + ({n10:'note', c10:'c10', c1:'c1'})[k]);
""")
idx = {s: i for i, s in enumerate(js("return CARD.slides.map(s=>s.id)"))}
said = lambda: js("return window.__said")
nav_on = lambda: js("const b=document.getElementById('navBtn'); return !!b && !b.disabled && getComputedStyle(b).display!=='none'")

# ---- T1 teaching
js("mountSlide(arguments[0]); window.__said=[]", idx["T1"]); time.sleep(0.15)
s0 = js("return [document.getElementById('promptText').textContent, [...document.querySelectorAll('.mn-intro-it')].map(e=>e.classList.contains('mn-intro-wait'))]")
check("T1 no heading; nothing shown before the VO", s0[0] == "" and s0[1] == [True, True], s0)
time.sleep(0.35)
s1 = js("return [...document.querySelectorAll('.mn-intro-it')].map(e=>[e.classList.contains('mn-intro-wait'), e.querySelector('.mn-intro-lbl').textContent])")
check("T1 the ₹10 note + «₹10» appear with the first line, the coin still hidden", s1[0] == [False, "₹10"] and s1[1][0] is True and said()[:1] == ["vo_t1_note"], (s1, said()))
time.sleep(1.0)
s2 = js("return [...document.querySelectorAll('.mn-intro-it')].map(e=>e.classList.contains('mn-intro-wait'))")
check("T1 then the ₹1 coin + «₹1» with the second line", s2 == [False, False] and "vo_t1_coin" in said(), (s2, said()))
check("T1 only the note + coin (no list / extra images)", js("return document.querySelectorAll('#slideHost .mn-intro img').length") == 2
      and js("return document.querySelectorAll('#slideHost img:not(.mn-intro img)').length") == js("return [...document.querySelectorAll('#slideHost img')].filter(i=>!i.closest('.mn-intro')).length"))
time.sleep(0.6)
check("T1 arrow enabled after the VO", nav_on())
lab = js("""const s=document.getElementById('stage').getBoundingClientRect().width/1333;
  return [...document.querySelectorAll('.mn-intro-it')].map(it=>{const l=it.querySelector('.mn-intro-lbl').getBoundingClientRect(), i=it.querySelector('img').getBoundingClientRect();
    const tm = it.classList.contains('is-note') ? 21/326 : 7/210; return [Math.round(l.width/s), Math.round(l.height/s), Math.round(l.top/s), Math.round((i.top + i.height*tm - l.bottom)/s)]})""")
check("T1 «₹10» / «₹1» labels: same box, same line, same gap to their art (round 9)",
      lab[0][:3] == lab[1][:3] and abs(lab[0][3] - lab[1][3]) <= 2 and 8 <= lab[0][3] <= 16, lab)

# ---- sorting
def sort_screen(sid, target, ncorrect):
    js("window.__said=[]; window.__sfx=[]; mountSlide(arguments[0])", idx[sid]); time.sleep(0.25)
    hidden0 = js("return document.querySelectorAll('.mn-sp.mn-sp-wait').length")
    txt0 = js("return document.getElementById('promptText').textContent")
    t_w = time.time()
    while time.time() - t_w < 6 and "vo_%s_prompt" % sid.lower() not in said(): time.sleep(0.03)
    txt1 = js("return document.getElementById('promptText').textContent")
    check("%s instruction appears with Swiftee's line, not before" % sid, txt0 == "" and txt1 == js("return CARD.slides[arguments[0]].prompt_hi", idx[sid]), (txt0, txt1))
    time.sleep(2.4)
    info = js("return [document.querySelectorAll('.mn-sp').length, [...document.querySelectorAll('.mn-sp')].filter(e=>+e.dataset.value===arguments[0]).length, !!document.querySelector('.mn-wallet img'), document.getElementById('promptText').textContent]", target)
    check("%s pieces arrive one by one (hidden at first)" % sid, hidden0 >= 7, hidden0)
    check("%s %d pieces, %d to collect, wallet shown" % (sid, info[0], info[1]), 8 <= info[0] <= 9 and info[1] == ncorrect and info[2], info)
    lay = js("""const w=document.querySelector('.mn-wallet').getBoundingClientRect(), ps=[...document.querySelectorAll('.mn-sp')].map(e=>e.getBoundingClientRect());
      const ov=(a,b)=>a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top; let pp=0; for(let i=0;i<ps.length;i++)for(let j=i+1;j<ps.length;j++) if(ov(ps[i],ps[j])) pp++;
      return [ps.filter(r=>ov(r,w)).length, pp, !!document.querySelector('.mn-sort-card'), !!document.querySelector('.mn-sort-card .tut-mascot'), getComputedStyle(document.querySelector('.header-row')||document.body).display]""")
    check("%s in the grid card, panel kept, no Swiftee in the card, nothing on the wallet / overlapping" % sid,
          lay[0] == 0 and lay[1] == 0 and lay[2] and not lay[3] and lay[4] != "none", lay)
    check("%s purse has two layers (back + front rim)" % sid, js("return !!document.querySelector('.mn-wallet .mn-wb') && !!document.querySelector('.mn-wallet .mn-wf')"))
    check("%s wooden table (board image) behind the pieces" % sid, "bg_wood" in js("return getComputedStyle(document.querySelector('.mn-sort-card')).backgroundImage"))
    while js("return isPlaying"): time.sleep(0.1)
    time.sleep(0.5)
    time.sleep(0.3)
    hand = js("return !!document.querySelector('.mn-hand')")
    check("%s hand nudge %s" % (sid, "on a ₹10 coin after the instruction" if sid == "G1" else "absent (first wallet screen only)"), hand == (sid == "G1"), hand)
    if sid == "G1":
        check("G1 the hand's ₹10 coin glows golden, no ring (round 12)",
              js("const c=document.querySelector('.mn-sp.mn-sp-handglow'); return !!c && +c.dataset.value===10 && getComputedStyle(c.querySelector('img')).animationName==='mnSortGlow' && getComputedStyle(c,'::before').content==='none'"))
    js("const w=[...document.querySelectorAll('.mn-sp')].find(e=>+e.dataset.value!==arguments[0]); w.click(); window.__w=w;", target); time.sleep(0.2)
    if sid == "G1": check("G1 the hand goes at the first tap", not js("return !!document.querySelector('.mn-hand')"))
    check("%s wrong piece: wiggles + incorrect sound, stays" % sid,
          js("return window.__w.classList.contains('mn-wiggle') && getComputedStyle(window.__w).animationName === 'mnSpWiggle' && !window.__w.classList.contains('mn-sp-gone')") and "sfx_fb_incorrect" in js("return window.__sfx"),
          js("return window.__sfx"))
    js("window.__sfx=[]; [...document.querySelectorAll('.mn-sp')].find(e=>+e.dataset.value===arguments[0]).click()", target); time.sleep(0.2)
    fl = js("return !!document.querySelector('.mn-wallet .mn-wfly .mn-wpiece')")   # round 3b: drawn BETWEEN the wallet's layers
    time.sleep(0.8)
    check("%s right piece: flies into the wallet with a sound" % sid, fl and js("return document.querySelectorAll('.mn-sp.mn-sp-gone').length") == 1
          and any(x in js("return window.__sfx") for x in ("sfx_drop_coin", "sfx_drop_note")), js("return window.__sfx"))
    for _ in range(ncorrect - 1):
        js("const e=[...document.querySelectorAll('.mn-sp:not(.mn-sp-gone)')].find(e=>+e.dataset.value===arguments[0]); e && e.click()", target); time.sleep(0.9)
    time.sleep(1.4)
    check("%s all collected: confetti (+ its sound) + «शाबाश!» + arrow" % sid,
          "sfx_confetti" in js("return window.__sfx") and "vo_sort_done" in said() and nav_on(), (js("return window.__sfx"), said()))
sort_screen("G1", 10, 4)
check("G1 asks for ₹10 notes AND coins", js("return [...new Set(CARD.slides[1].data.pieces.filter(p=>p.value===10).map(p=>p.img))].sort().join()") == "cur_coin10,cur_note10")
sort_screen("G2", 1, 4)
# idle nudge on a sorting screen: 7 s -> a piece glows + the chime
js("window.__said=[]; window.__sfx=[]; mountSlide(arguments[0])", idx["G1"])
t_w = time.time()
while time.time() - t_w < 10 and "vo_g1_prompt" not in said(): time.sleep(0.05)
time.sleep(0.4)                                   # the (mocked) instruction ends -> the screen is armed
time.sleep(5.5); n0 = js("return document.querySelectorAll('.mn-sp.mn-sp-hint').length")
time.sleep(1.8); n1 = js("return document.querySelectorAll('.mn-sp.mn-sp-hint').length")
check("G1 idle ~7 s: a ₹10 piece glows + nudge chime", n0 == 0 and n1 == 1 and "sfx_nudge" in js("return window.__sfx"), (n0, n1, js("return window.__sfx")))

# ---- make screens
T = "document.querySelector('.mn-target')"
placed = lambda: js("return document.querySelectorAll('.mn-target .mn-placed:not(.mn-slot)').length")
off = lambda k: js("return src(arguments[0]).classList.contains('mn-off')", k)
def make(sid, Tv, ghost):
    js("window.__said=[]; window.__ghosts=0; window.__shk=0; mountSlide(arguments[0])", idx[sid]); time.sleep(0.2)
    js("""new MutationObserver(ms=>ms.forEach(m=>{ const t=m.target; if(t.classList && t.classList.contains('mn-target') && t.classList.contains('mn-shake')) window.__shk++; }))
          .observe(document.querySelector('.mn-target'),{attributes:true, attributeFilter:['class']});""")
    if sid == "G3":   # round 4: the retained line first, then the instruction; the panel follows the voice
        band0 = js("return document.getElementById('promptText').textContent")
        check("G3 opens with «चलिए, दस रुपये और एक रुपये के सिक्कों से इस राशि को बनाते हैं।» (panel shows it)",
              said()[:1] == ["vo_b14_intro"] and "इस राशि को बनाते हैं" in band0, (said(), band0))
    check("%s no container round the amount; «कुल» in the drop zone" % sid,
          js("const i=document.querySelector('.mn-item-amt'), s=getComputedStyle(i); return s.borderTopStyle==='none' && s.backgroundColor==='rgba(0, 0, 0, 0)' && !!document.querySelector('.mn-target .mn-total')"))
    check("%s only the amount (no item picture), ₹10 note + ₹1 coin below" % sid,
          js("return !document.querySelector('.mn-item-img') && document.querySelector('.mn-tag-big').textContent") == "₹%d" % Tv
          and js("return document.querySelectorAll('.mn-src').length") == 2 and js("return !!src('n10') && !!src('c1')"))
    if sid == "G3":   # round 21 (lead): while Swiftee talks both are shown as they are; the ₹1 locks with the first ghost
        check("G3 while the lines play: ₹10 AND ₹1 shown, not greyed", (not off("n10")) and not off("c1"))
    else:
        check("%s starts: ₹10 unlocked, ₹1 locked" % sid, (not off("n10")) and off("c1"))
    time.sleep(1.4 if sid != "G3" else 1.8)
    if sid == "G3":
        check("G3 then the instruction «₹14 बनाइए।»", said()[:2] == ["vo_b14_intro", "vo_b14_prompt"] and js("return document.getElementById('promptText').textContent") == "₹14 बनाइए।", said())
    if sid == "G3":
        t_w = time.time()
        while time.time() - t_w < 12 and not js("return window.__ghosts"): time.sleep(0.05)
        check("G3 the instruction ends: the ₹1 locks together with the ghost ₹10", js("return window.__ghosts") >= 1 and off("c1") and not off("n10"))
    g0 = js("return window.__ghosts")
    check("%s %s" % (sid, "ghost ₹10 after the instruction" if ghost else "no ghost"), (g0 >= 1) if ghost else (g0 == 0), g0)
    TP, OP = Tv // 10, Tv % 10
    for i in range(TP):
        js("drag(src('n10'), %s)" % T); time.sleep(0.8)
    if ghost:      # ₹14 (page 4): unchanged — the ₹10 locks after its one note
        check("%s after %d tens: ₹10 locked, ₹1 unlocked" % (sid, TP), off("n10") and not off("c1"))
        time.sleep(0.6)
        check("%s ghost ₹1 before the first coin" % sid, js("return window.__ghosts") > g0)
        js("drag(src('n10'), %s)" % T); time.sleep(0.6)
        check("%s a locked ₹10 cannot be added" % sid, placed() == TP)
    else:          # round 4: ₹32 / ₹45 — ₹10 stays open; extra ₹10 -> bounce + shake; 2nd + ghost ₹1 + hint; 3rd locks
        check("%s after %d tens: ₹1 unlocks, ₹10 stays OPEN" % (sid, TP), (not off("n10")) and not off("c1"))
        js("window.__said=[]; window.__ghosts=0; window.__shk=0"); js("drag(src('n10'), %s)" % T); time.sleep(1.2)
        check("%s 1st extra ₹10: bounces back + drop zone shakes, no VO, no ghost" % sid,
              placed() == TP and js("return window.__shk") >= 1 and not said() and js("return window.__ghosts") == 0, (placed(), js("return window.__shk"), said()))
        js("window.__said=[]; window.__ghosts=0; window.__shk=0"); js("drag(src('n10'), %s)" % T); time.sleep(1.2)
        check("%s 2nd extra ₹10: bounces + shake + ghost ₹1 + «ध्यान से देखिए! … %s रुपये बनाइए।»" % (sid, ["", "", "दो", "", "", "पाँच"][OP]),
              placed() == TP and js("return window.__shk") >= 1 and js("return window.__ghosts") >= 1 and said()[:1] == ["vo_hint_ones_%d" % OP], (said(), js("return window.__ghosts")))
        time.sleep(0.4); js("window.__shk=0"); js("drag(src('n10'), %s)" % T); time.sleep(1.2)
        check("%s 3rd extra ₹10: bounces back and the ₹10 LOCKS" % sid, placed() == TP and off("n10") and not off("c1"), (placed(), off("n10")))
        js("drag(src('n10'), %s)" % T); time.sleep(0.6)
        check("%s a locked ₹10 cannot be dragged any more" % sid, placed() == TP)
    for i in range(OP):
        g1 = js("return window.__ghosts")
        js("drag(src('c1'), %s)" % T); time.sleep(0.9)
        if ghost and i < OP - 1:
            if not js("return window.__ghosts") > g1: check("%s ghost before coin %d" % (sid, i + 2), False)
    time.sleep(0.6)
    cov = js("""const t=document.querySelector('.mn-target .mn-total').getBoundingClientRect();
      return [...document.querySelectorAll('.mn-target .mn-placed:not(.mn-slot)')].filter(e=>{const r=e.getBoundingClientRect(); return r.left<t.right&&r.right>t.left&&r.top<t.bottom&&r.bottom>t.top}).length""")
    check("%s no note / coin under the «कुल» counter" % sid, cov == 0, cov)
    check("%s completes itself at ₹%d (child-placed only) + closing line" % (sid, Tv),
          placed() == Tv // 10 + Tv % 10 and js("return !!document.querySelector('.mn-finished')") and any(x.endswith("_done") for x in said()), said())
    eq = js("return document.querySelector('.mn-eq').textContent")
    check("%s equation «₹%d + ₹%d = ₹%d» (round 21: one total per kind)" % (sid, Tv // 10 * 10, Tv % 10, Tv), eq == "₹%d + ₹%d = ₹%d" % (Tv // 10 * 10, Tv % 10, Tv), eq)
make("G3", 14, True)
make("G4", 32, False)
make("G5", 45, False)
# idle on ₹32 / ₹45: the nudge glows + chimes, no ghost (only ₹14 has ghosts); ₹14's idle nudge does ghost
for sid, want_ghost in (("G4", False), ("G5", False), ("G3", True)):
    js("window.__said=[]; window.__sfx=[]; window.__ghosts=0; mountSlide(arguments[0])", idx[sid]); time.sleep(1.0)
    js("window.__ghosts=0")
    time.sleep(8.3)
    g, sfx = js("return window.__ghosts"), js("return window.__sfx")
    glow = js("return !!document.querySelector('.mn-src.mn-hintglow, .mn-src.mn-hintglow-on')")
    if want_ghost: check("%s idle 7 s: ghost + chime" % sid, g >= 1 and "sfx_nudge" in sfx, (g, sfx))
    else: check("%s idle 7 s: glow + chime, NO ghost" % sid, g == 0 and glow and "sfx_nudge" in sfx, (g, glow, sfx))

# ---- shop
js("window.__sgDragInShown = true; window.__said=[]; mountSlide(arguments[0])", idx["M1"]); time.sleep(2.5)
s = said()
check("shop opens with Swiftee's line, then the instruction", s[:2] == ["vo_m_intro", "vo_m_prompt"], s)
mk = "document.querySelector('.sg-make2')"
js("document.querySelectorAll('.sg-cell2')[0].click()"); time.sleep(2.0)          # ₹14
js("""window.__sshk=0; new MutationObserver(ms=>ms.forEach(m=>{ const t=m.target; if(t.classList && t.classList.contains('mn-target') && t.classList.contains('mn-shake')) window.__sshk++; }))
      .observe(document.getElementById('stage'),{attributes:true, subtree:true, attributeFilter:['class']});""")
def chk():
    js("window.__said=[]; window.__sshk=0; document.querySelector('.sg-checkpill').click()"); time.sleep(1.4)
js("drag(src('c1', %s), %s)" % (mk, T)); time.sleep(4.0)                           # + the one-time tip
chk()
check("shop 1st wrong (less): «ओहो! रुपये कम हैं…», money stays", said()[:1] == ["vo_m_less1"] and placed() == 1, (said(), placed()))
check("shop wrong «जाँचें»: the drop zone shakes (round 14)", js("return window.__sshk") >= 1, js("return window.__sshk"))
chk()
check("shop 2nd wrong (less): «ओहो! अभी भी … कम …», money stays", said()[:1] == ["vo_m_less2"] and placed() == 1, (said(), placed()))
chk(); time.sleep(0.8)
check("shop 3rd wrong: «फिर से कोशिश करें।» and the tray resets", said()[:1] == ["vo_m_retry"] and placed() == 0
      and js("return document.getElementById('promptText').textContent") in ("फिर से कोशिश करें।", "₹14 बनाइए।"), (said(), placed()))
js("window.__sshk=0")
for _ in range(2): js("drag(src('n10', %s), %s)" % (mk, T)); time.sleep(0.6)
check("after the reset the silent caps hold: a 2nd ₹10 for ₹14 is refused", placed() == 1, placed())
check("shop refused piece: bounces back and the drop zone shakes (round 14)", js("return window.__sshk") >= 1, js("return window.__sshk"))
chk()
check("after the reset the count starts again: 1st wrong «ओहो! रुपये कम हैं…»", said()[:1] == ["vo_m_less1"], said())
# "too much" on a fresh item (no caps yet): ₹25 with three ₹10
js("window.__sgDragInShown = true; window.__said=[]; mountSlide(arguments[0])", idx["M1"]); time.sleep(2.5)
js("document.querySelectorAll('.sg-cell2')[1].click()"); time.sleep(2.0)
js("drag(src('n10', %s), %s)" % (mk, T)); time.sleep(4.5)            # the one-time drag-back tip speaks first
for _ in range(2): js("drag(src('n10', %s), %s)" % (mk, T)); time.sleep(0.6)
chk()
check("shop 1st wrong (more): «ओहो! रुपये ज़्यादा हैं…», money stays", said()[:1] == ["vo_m_more1"] and placed() == 3, (said(), placed()))
# idle after "more": the last-added piece is ghosted from the tray back to its place
js("""window.__gb=[]; new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList && n.classList.contains('mn-ghost')){
   const z=document.querySelector('.sg-make2 .mn-target').getBoundingClientRect(), r=n.getBoundingClientRect();
   window.__gb.push(r.left+r.width/2>z.left && r.left+r.width/2<z.right && r.top+r.height/2>z.top && r.top+r.height/2<z.bottom); }}))).observe(document.getElementById('stage'),{childList:true});
   window.__sfx=[];""")
time.sleep(8.0)
gb = js("return window.__gb")
check("idle 7 s after «ज़्यादा»: a ghost starts IN the tray (drag-back hint) + chime", gb[:1] == [True] and "sfx_nudge" in js("return window.__sfx"), (gb, js("return window.__sfx")))
js("window.__sfx=[]; tap(document.querySelector('.sg-make2 .mn-target .mn-placed:not(.mn-slot)'))"); time.sleep(1.0)
check("shop: a TAP on placed money sends it back to the tray, with its sound (round 21)", placed() == 2 and "sfx_drop_note" in js("return window.__sfx"), (placed(), js("return window.__sfx")))
js("window.__gb=[]"); time.sleep(8.0)
gb = js("return window.__gb")
check("idle 7 s with too little: a ghost starts OUTSIDE the tray (drag-in hint)", gb[:1] == [False], gb)

# ---- dev menu: «दुकान का खेल» sub-entries
d.get("http://127.0.0.1:%d/%s?dev=1" % (port, PAGE)); time.sleep(2)
t_w = time.time()
while time.time() - t_w < 40 and js("return window.__preloadMs == null && !!window.__assetGateP"): time.sleep(0.2)
time.sleep(1.5)
opts = js("return [...document.querySelectorAll('#devNav .dev-nav-sel option')].map(o=>o.value+'|'+o.textContent)")
subs = [o for o in opts if o.startswith("6.")]
check("dev menu: 8 sub-entries under the shop (6 items + 5 bought + the list)", len(subs) == 8, subs)
def pick(v):
    js("const s=document.querySelector('#devNav .dev-nav-sel'); s.value=arguments[0]; s.dispatchEvent(new Event('change',{bubbles:true}))", v); time.sleep(1.5)
pick("6.4")
check("dev ↳ अंगूर ₹42: opens its amount screen, 3 bought", js("return [!!document.querySelector('.sg-make2'), document.querySelector('.sg-make2 .mn-tag span').textContent]") == [True, "₹42"])
pick("6.s5")
check("dev ↳ 5 bought: the stall with one left", js("return [document.querySelectorAll('.sg-cell2').length, document.querySelectorAll('.sg-cell2.sg-sold').length]") == [6, 5])
pick("6.done")
check("dev ↳ all bought: the final list", js("return !!document.querySelector('.sg-complete')"))
pick("6")
check("dev plain «दुकान का खेल»: the stall from the start", js("return document.querySelectorAll('.sg-cell2.sg-sold').length") == 0 and js("return !!document.querySelector('.sg-cell2')"))

errs = [l["message"][:160] for l in d.get_log("browser") if l["level"] == "SEVERE" and "favicon" not in l["message"]]
check("no console errors", not errs, errs[:4])
print("\n%d FAIL" % len(fails), fails)
d.quit(); srv.shutdown()
