/* ============================================================================================
   «परी की पिकनिक की खरीदारी» — MONEY MODULE SET                    [local to MTG2A04_L01_S01]
   ============================================================================================
   Built to the SME deck MTG2A04_L01_S01_review.pptx (22 pages) — see ../CHANGES.md for the row-by-
   row contract. Injected into this game's own engine copy (engine/lesson_template.html, which is the
   HI02H11_L02_S02 engine the user named as the visual baseline) by engine/inject_money.py.

   ADDITIVE ONLY: new SlideModules entries + one CSS block. The two engine behaviours this game changes
   are changed by WRAPPING, not editing, and only for this card:
     · autoAdvances() -> false. The deck asks for "Arrow appears for next screen" on every screen; the
       engine's AUTO_ADVANCE_FROM=5 would press it for the child.
     · armIdleVo() is skipped on slides with data.no_engine_idle — the build and shop screens run the
       deck's own inactivity ladder (pulse -> ghost / glow + VO) and the engine's 7s prompt replay would
       talk over it.
     · a 4th phase gate ("mastery") in front of the shop game (decision D6).

   MODULES
     MONEY_SHOW   p2   ₹10 note + ₹1 coin (both faces) pop in; autonomous
     MONEY_PICK   p3–6 tap the named currency; correct = green + glow + confetti; wrong = shake + red
                       + the right currency shown big in the centre with its line
     MONEY_SCENE  p7   Pari with her list
     MONEY_LIST   p8   zoom-in list; each row pulses as the VO names it
     MONEY_BUILD  p9–13 + toffee   drag ₹10 notes/coins and ₹1 coins into a tray.
                       teach: scripted demo steps -> child steps.  practice: free build with
                       the ₹1 TOLERANCE rule (S14), the bounce ladder (S11–S15, decision D1) and
                       the pulse -> ghost idle ladder; optional «हो गया» check (juice, D2)
     MONEY_DONE   p18  the ticked list, 5 / 5
     SHOP_GAME    S17–S21  the mastery shop: choose -> select -> make -> जाँचें -> basket, ×8
   ============================================================================================ */
(function(){
  "use strict";

  /* ============ PAUSE WHEN HIDDEN, round 16 (user, 2026-10-21) ============
     "the game should pause when we switch the tab or even minimise the browser, and resume when we move
     back". The whole lesson runs on ONE clock, frozen while the page is hidden:
       time    performance.now(), Date.now() and the rAF timestamp stand still while hidden (the time spent
               away is subtracted), so every "how long since" in the lesson — inactivity nudges, the VO
               fallback timers, Swiftee's lip-sync, the title typing, the ₹ highlights — carries on exactly
               where it stopped
       timers  every setTimeout / setInterval created by the lesson is held (its remaining time kept) and
               re-armed on return
       sound   the Web Audio context (voice + sound effects) is suspended — a line resumes mid-word; every
               <audio> element that was playing (the music, a fallback clip) is paused and resumed
       motion  every running CSS / Web animation (confetti, a piece in flight, glows, the hand) is paused
     The music's own loop is told by window.__lessonPaused (the inject_money.py patch 'r16p'). */
  (function pauseWhenHidden(){
    if(window.__lessonPauseInstalled) return; window.__lessonPauseInstalled = true;
    const RT = { st:window.setTimeout.bind(window), ct:window.clearTimeout.bind(window),
                 si:window.setInterval.bind(window), ci:window.clearInterval.bind(window),
                 pn:performance.now.bind(performance), dn:Date.now, raf:window.requestAnimationFrame.bind(window) };
    let paused = false, pausedReal = 0, offset = 0;              /* ms of real time spent paused, in total */
    const vnow = ()=> paused ? pausedReal - offset : RT.pn() - offset;
    try { performance.now = vnow; } catch(e){}
    Date.now = ()=> Math.round(RT.dn() - offset - (paused ? RT.pn() - pausedReal : 0));
    window.requestAnimationFrame = (cb)=> RT.raf(()=> cb(vnow()));

    const T = new Map(), I = new Map(); let seq = 1e9;            /* ids far from the browser's own */
    window.setTimeout = function(cb, ms){
      const a = Array.prototype.slice.call(arguments, 2);
      if(typeof cb !== "function") return RT.st.apply(null, arguments);
      const id = ++seq, d = Math.max(0, +ms || 0);
      const rec = { due:vnow() + d, h:null, left:d };
      rec.fire = ()=>{ T.delete(id); cb.apply(window, a); };
      if(!paused) rec.h = RT.st(rec.fire, d);
      T.set(id, rec); return id;
    };
    window.clearTimeout = function(id){ const r = T.get(id); if(r){ if(r.h != null) RT.ct(r.h); T.delete(id); } else RT.ct(id); };
    window.setInterval = function(cb, ms){
      const a = Array.prototype.slice.call(arguments, 2);
      if(typeof cb !== "function") return RT.si.apply(null, arguments);
      const id = ++seq, rec = { ms:Math.max(0, +ms || 0), h:null };
      rec.start = ()=>{ rec.h = RT.si(()=> cb.apply(window, a), rec.ms); };
      if(!paused) rec.start();
      I.set(id, rec); return id;
    };
    window.clearInterval = function(id){ const r = I.get(id); if(r){ if(r.h != null) RT.ci(r.h); I.delete(id); } else RT.ci(id); };

    /* every <audio> the lesson plays is remembered, so it can be paused and resumed */
    const media = new Set();
    const _play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function(){ media.add(this); return _play.apply(this, arguments); };
    let held = { anims:[], media:[], ctx:null };
    const ctxOf = ()=>{ try { return (typeof _juiceAC !== "undefined" && _juiceAC) || (typeof _voiceContext === "function" ? _voiceContext() : null); } catch(e){ return null; } };

    function pause(){
      if(paused) return;
      pausedReal = RT.pn(); paused = true; window.__lessonPaused = true;
      T.forEach(r => { if(r.h != null){ RT.ct(r.h); r.h = null; r.left = Math.max(0, r.due - (pausedReal - offset)); } });
      I.forEach(r => { if(r.h != null){ RT.ci(r.h); r.h = null; } });
      held.media = [...media].filter(m => !m.paused && !m.ended);
      held.media.forEach(m => { try { m.pause(); } catch(e){} });
      const c = ctxOf(); held.ctx = (c && c.state === "running") ? c : null;
      if(held.ctx) held.ctx.suspend().catch(()=>{});
      try { held.anims = document.getAnimations().filter(a => a.playState === "running"); held.anims.forEach(a => a.pause()); } catch(e){ held.anims = []; }
      try { SwiftPAL.emit("lesson_paused", { slide_id:(CARD.slides[state.idx] || {}).id }); } catch(e){}
    }
    function resume(){
      if(!paused) return;
      offset += RT.pn() - pausedReal; paused = false; window.__lessonPaused = false;
      const now = vnow();
      T.forEach(r => { if(r.h == null){ r.due = now + r.left; r.h = RT.st(r.fire, r.left); } });
      I.forEach(r => { if(r.h == null) r.start(); });
      if(held.ctx) held.ctx.resume().catch(()=>{});
      held.media.forEach(m => { try { const p = m.play(); if(p && p.catch) p.catch(()=>{}); } catch(e){} });
      held.anims.forEach(a => { try { if(a.playState === "paused") a.play(); } catch(e){} });
      held = { anims:[], media:[], ctx:null };
      try { SwiftPAL.emit("lesson_resumed", { slide_id:(CARD.slides[state.idx] || {}).id }); } catch(e){}
    }
    document.addEventListener("visibilitychange", ()=>{ if(document.hidden) pause(); else resume(); });
    window.addEventListener("pagehide", pause);
    window.addEventListener("pageshow", ()=>{ if(!document.hidden) resume(); });
    window.__lessonPause = pause; window.__lessonResume = resume;   /* (tests / the host app) */
  })();

  /* ============ SPEAKER STAYS "BUSY" THROUGH A SEQUENCE OF LINES, round 19 (QA bug, 2026-10-23) ============
     "the speaker turns blue then grey and so on, between the pauses of the VO - on every screen where
     lines are announced". The engine greys the speakers (header chip, teaching-card chip, cover speaker)
     under body.vo-lock, which is on EXACTLY while a clip sounds - so in the gap between two lines of one
     sequence (page 1's ₹10 then ₹1, page 4's opening line then the instruction, the shop's intro then
     its instruction ...) it flashed back to blue for a moment. body.vo-busy follows vo-lock ON at once,
     but goes OFF only after the voice has been quiet for SPK_HOLD_MS - the speakers' look and their
     tap-lock follow vo-busy (money_styles.css). vo-lock itself (the screen's tap / drag lock) is untouched. */
  (function speakerBusy(){
    const SPK_HOLD_MS = 700;
    let offT = null;
    const sync = ()=>{
      const b = document.body; if(!b) return;
      if(b.classList.contains("vo-lock")){
        if(offT){ clearTimeout(offT); offT = null; }
        /* only when missing: classList.add() of a class already there still rewrites the attribute, which
           re-fires this observer - an endless loop that froze the page while a clip played */
        if(!b.classList.contains("vo-busy")) b.classList.add("vo-busy");
      } else if(b.classList.contains("vo-busy") && !offT){
        offT = setTimeout(()=>{ offT = null; if(!document.body.classList.contains("vo-lock")) document.body.classList.remove("vo-busy"); }, SPK_HOLD_MS);
      }
    };
    const start = ()=>{ sync(); new MutationObserver(sync).observe(document.body, { attributes:true, attributeFilter:["class"] }); };
    if(document.body) start(); else document.addEventListener("DOMContentLoaded", start);
  })();

  /* ---------------------------------------------------------------- engine wraps (this card only) */
  try { autoAdvances = function(){ return false; }; } catch(e){}
  /* round 20 (QA BUG_07): a new page takes the solved screen's grey off the speaker */
  try {
    const _msd = mountSlide;
    mountSlide = function(){ document.body.classList.remove("spk-done"); return _msd.apply(this, arguments); };
  } catch(e){}
  try {
    const _arm = armIdleVo;
    armIdleVo = function(){
      const s = CARD && CARD.slides && CARD.slides[state.idx];
      if(s && s.data && s.data.no_engine_idle){ if(typeof stopIdleVo === "function") stopIdleVo(); return; }
      return _arm.apply(this, arguments);
    };
  } catch(e){}

  /* ============ CONFETTI, round 2s (user, 2026-10-08) ============
     "extract the same confetti effect (animation)" from MTG2A04_L02_S01: the FLN animation kit's
     recipe 7, copied verbatim (kit core: still + guard; the confetti module) — stars 40 %, rectangles,
     lines, squares, two-faced, fluttering / tumbling at terminal velocity, VIBGYOR pairs. Called as
     that lesson calls it: body-level #fxLayer (falls over the whole window), 100 pieces, fall
     [1.6, 2.6] s, every phase (phases: []), pieces 1.5x and sized with the stage (money_styles.css).
     The engine's old .conf-shot cannon is replaced at the one name every call site uses; it had no
     sound and none is added here (that lesson's sfx_confetti is a separate call). */
  (function(){ "use strict";
    var M = window.FLNMotion = window.FLNMotion || {};
    M.still = M.still || function(){
      try{ return document.documentElement.classList.contains("no-anim") ||
        (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches); }
      catch(_){ return false; }
    };
    M.guard = M.guard || function(fn){
      try{ fn(); }catch(e){ try{ console.warn("[animation-kit]", e && e.message); }catch(_){} }
    };
    function rnd(a, b){ return a + Math.random() * (b - a); }
    M.confetti = {
      defaults: {
        host:".stage-inner", count:80, stagger:0.35,
        fall:[1.1,1.8], drift:45, sway:[10,34], bob:[3,7],
        rockT:[0.6,1.2], tumbleT:[0.75,1.5], tumbleShare:0.22,
        amp:[28,52], yaw:30, depth:[0.75,1.15], tilt:25,
        shapes:["st","st","st","st","rc","rc","ln","ln","sq","sq"],
        colors:[["#8B2FC9","#5E1C8C"],["#3F51B5","#27358A"],["#1E88E5","#135FA6"],["#22B24C","#157A34"],
                ["#FFD21E","#D9A800"],["#FF8A1E","#C75F00"],["#E5322D","#A81F1B"]],
        phases:["guided","practice","mastery"]
      },
      burst: function(opts){
        var o = Object.assign({}, this.defaults, opts || {});
        M.guard(function(){
          if(M.still()) return;
          if(o.phases.length && o.phase && o.phases.indexOf(o.phase) < 0) return;
          var host = document.querySelector(o.host); if(!host) return;
          var dist = host.clientHeight + 60, maxLife = 0;
          var wrap = document.createElement("div");
          wrap.className = "fx-confetti";
          for(var i = 0; i < o.count; i++){
            var z     = rnd(o.depth[0], o.depth[1]);
            var fall  = rnd(o.fall[0], o.fall[1]) / z;
            var delay = rnd(0, o.stagger);
            if(fall + delay > maxLife) maxLife = fall + delay;
            var pair = o.colors[i % o.colors.length];
            var flutter = Math.random() > o.tumbleShare;
            var rockT   = flutter ? rnd(o.rockT[0], o.rockT[1]) : rnd(o.tumbleT[0], o.tumbleT[1]);
            var sway    = flutter ? rnd(o.sway[0], o.sway[1]) : rnd(2, 8);
            var drift   = flutter ? rnd(-o.drift/2.5, o.drift/2.5) : rnd(-o.drift, o.drift);
            var bob     = flutter ? rnd(o.bob[0], o.bob[1]) : rnd(2, 4);
            var p = document.createElement("i"); p.className = "p";
            p.style.cssText =
              "--x:"     + rnd(-2, 98).toFixed(1) + "%;" +
              "--dist:"  + dist + "px;" +
              "--fall:"  + fall.toFixed(2) + "s;" +
              "--delay:" + delay.toFixed(2) + "s;" +
              "--drift:" + drift.toFixed(0) + "px;" +
              "--sway:"  + sway.toFixed(0) + "px;" +
              "--bob:"   + bob.toFixed(1) + "px;" +
              "--rockT:" + rockT.toFixed(2) + "s;" +
              "--amp:"   + Math.round(rnd(o.amp[0], o.amp[1])) + "deg;" +
              "--yaw:"   + Math.round(rnd(-o.yaw, o.yaw)) + "deg;" +
              "--tilt:"  + Math.round(rnd(-o.tilt, o.tilt)) + "deg;" +
              "--z:"     + z.toFixed(2) + ";" +
              "--dim:"   + (0.72 + (z - o.depth[0]) / (o.depth[1] - o.depth[0]) * 0.28).toFixed(2) + ";" +
              "--c:"     + pair[0] + ";--c2:" + pair[1] + ";";
            var w = document.createElement("i"); w.className = "w";
            var f = document.createElement("i");
            f.className = "f " + o.shapes[Math.floor(Math.random() * o.shapes.length)] + (flutter ? "" : " tum");
            w.appendChild(f); p.appendChild(w); wrap.appendChild(p);
          }
          host.appendChild(wrap);
          setTimeout(function(){ wrap.remove(); }, (maxLife + 0.3) * 1000);
        });
      }
    };
    var layer = function(){
      var L = document.getElementById("fxLayer");
      if(!L){ L = document.createElement("div"); L.className = "fx-layer"; L.id = "fxLayer";
              L.setAttribute("aria-hidden", "true"); document.body.appendChild(L); }
      return L;
    };
    if(document.body) layer(); else document.addEventListener("DOMContentLoaded", layer);
    confettiCannon = function(){
      var sl = (CARD && CARD.slides && CARD.slides[state.idx]) || {};
      layer();
      M.confetti.burst({ host: "#fxLayer", phase: sl.phase, phases: [], count: 100, fall: [1.6, 2.6] });
      try { sfxVol("sfx_confetti", 0.4); } catch(e){}    /* round 3 (checklist): the standard confetti SFX */
    };
  })();
  /* CARD is parsed AFTER this script runs (the engine polls for it the same way in _warmSoon), so
     the gate is registered once CARD exists — registering it at load time silently did nothing and
     the shop opened with no transition. */
  /* ...and the PHASE_* tables are `const`s declared FURTHER DOWN the same script, so touching them
     synchronously here is a temporal-dead-zone ReferenceError. Always defer, retry until both exist. */
  setTimeout(()=> (function regGate(tries){
    let ok = false;
    try {
      const g = CARD && CARD.mastery_gate;
      if(g){ PHASE_ROUND.mastery = "mastery"; PHASE_GATE_TITLE.mastery = g.title || ""; PHASE_GATE_VO.mastery = g.audio || null; }
      /* round 3 (checklist): the transitions' on-screen titles, worded exactly as the checklist —
         «चलिए, शुरू करें!» / «चलिए, साथ में करें।» / «अब आपकी बारी।» (CARD.gate_titles; round 16) */
      const tt = CARD && CARD.gate_titles;
      if(tt) Object.keys(tt).forEach(ph => { PHASE_GATE_TITLE[ph] = tt[ph]; });
      ok = true;
    } catch(e){}
    if(!ok && tries < 400) setTimeout(()=> regGate(tries + 1), 25);
  })(0), 0);

  /* LANDING SCENE: the team's painted landing (title painted into the art) becomes the landing
     card itself — CARD.landing_scene = {img}. The engine's title stays in the DOM for screen readers
     but is hidden visually (it is already in the picture). Deferred for the same TDZ reason as above. */
  setTimeout(()=> (function applyScene(tries){
    try {
      const sc = CARD && CARD.landing_scene;
      const c = document.querySelector("#startGate .sg-card");
      if(!sc || !c){ if(tries < 200 && !c) setTimeout(()=> applyScene(tries + 1), 25); return; }
      const ext = (CARD.assets && CARD.assets.img_ext) || "png";
      c.classList.add("sg-scene");
      c.style.backgroundImage = 'url("assets/Images/' + sc.img + "." + ext + '")';
      /* round 3c (user): the title is its own picture (the cover has none), laid over the cover */
      if(sc.title_img && !c.querySelector(".sg-title-img")){
        const ti = document.createElement("img"); ti.className = "sg-title-img"; ti.alt = "";
        ti.decoding = "sync"; ti.src = "assets/Images/" + sc.title_img + "." + ext; c.appendChild(ti);
      }
    } catch(e){ if(tries < 200) setTimeout(()=> applyScene(tries + 1), 25); }
  })(0), 0);

  /* DEV NAV LABELS (?dev=1 / ?nav=1 only). The engine's navigator lists "6. G2 · MONEY_BUILD"; a card
     slide may carry `dev_label` (deck page + content) and the dropdown shows that instead, so a reviewer
     can jump straight to "p9 · कॉपी ₹14" without knowing the ids. Waits for the bar to exist. */
  (function relabelDev(tries){
    const sel = document.querySelector("#devNav .dev-nav-sel");
    if(!sel){ if(tries < 400) setTimeout(()=> relabelDev(tries + 1), 50); return; }
    try {
      [...sel.options].forEach((o, i)=>{
        const s = CARD.slides[i];
        if(s && s.dev_label) o.textContent = (i + 1) + ". " + s.id + " · " + s.dev_label;
      });
      /* round 3b (user): «दुकान का खेल» sub-entries, so a later item / the end can be tested without
         playing the whole game. Value "<slide>.<sub>": the engine's own handler parseInt()s it to the
         shop's index; this capture listener (on the bar, so it runs FIRST) leaves the sub-state for
         SHOP_GAME.mount to pick up. */
      const si = CARD.slides.findIndex(s => s.type === "SHOP_GAME");
      if(si >= 0 && !sel.querySelector('option[value^="' + si + '."]')){
        const items = CARD.slides[si].data.items || [];
        const subs = items.map((it, k)=> ({ v:si + "." + (k + 1), t:"   ↳ " + it.name + " ₹" + it.price + " (बनाना)", st:{ open:k, bought:k } }));
        subs.push({ v:si + ".s5", t:"   ↳ स्टॉल · 5 खरीदे", st:{ bought:Math.max(0, items.length - 1) } });
        subs.push({ v:si + ".done", t:"   ↳ सब खरीदे · सूची", st:{ bought:items.length, done:true } });
        let after = sel.options[si];
        subs.forEach(sb => { const o = document.createElement("option"); o.value = sb.v; o.textContent = sb.t;
          after.insertAdjacentElement("afterend", o); after = o; });
        const map = {}; subs.forEach(sb => { map[sb.v] = sb.st; });
        sel.parentElement.addEventListener("change", (ev)=>{
          if(ev.target !== sel) return;
          window.__shopDev = map[sel.value] || null;
          if(window.__shopDev) window.__sgDragInShown = true;   /* skip the first-item demo in a jump */
        }, true);
      }
    } catch(e){}
  })(0);

  /* (round 2i's own transition gate removed in round 2p: the engine's r107/r108 gate is used —
     rise animation, lip-synced talk sheet, typewriter title on the clip's clock; data on CARD.gate) */

  /* round 2j: the celebration screen shows the team's own Swiftie GIF (CARD.end_mascot), used exactly as
     supplied — background included (user instruction: do not remove or alter its background). */
  setTimeout(()=> (function endMascot(tries){
    try {
      const src = CARD && CARD.end_mascot;
      const im = document.querySelector("#endScreen .end-mascot");
      if(!src) return;
      if(!im){ if(tries < 200) setTimeout(()=> endMascot(tries + 1), 25); return; }
      im.src = src; im.classList.add("end-mascot-team");
    } catch(e){ if(tries < 200) setTimeout(()=> endMascot(tries + 1), 25); }
  })(0), 0);

  /* (round 2k's button-sound listener removed in round 2p: the engine plays CARD.ui_sfx — the play
     sound on the press, the next sound on a real click of the arrow / celebration arrow) */

  /* ============ CELEBRATION SWIFTIE, round 2l — lip-synced to the VO ============
     The team's jumping + speaking Swiftie (36 frames) is a sprite sheet the page drives itself, because
     a GIF runs on its own 4 s clock and cannot follow a 5.7 s line. The timeline comes from the VO:
       before the voice      frame 21 (arms out, ready)
       «शाबाश!» (1st word)    the jump, frames 22-32 (arms up, mouth open), stretched over that word
       the pause after it     fist pump 33-35 (mouth closed)
       the rest of the line   standing; every step the VO's loudness at THAT moment picks a mouth-open
                              frame (loud) or a mouth-closed one (quiet) — so the mouth moves with the
                              syllables and shuts on every pause
       after the voice        two fist pumps, then a standing idle with a blink, mouth shut
     The VO clock is the moment the engine's clip actually starts (isPlaying), not the mount. */
  /* round 2p (user): "once the VO finishes, the button is enabled and pulses" — on the celebration too.
     The engine shows its arrow at once; here it waits (dim, not pressable) until the celebration
     line has ended, then it pulses like the in-lesson arrow (no glow, no border change). */
  function celArrowAfterVO(){
    const eb = document.getElementById("endBtn"); if(!eb) return;
    eb.classList.remove("hint-glow"); eb.classList.add("cel-wait");
    const t0 = performance.now(); let heard = false;
    (function tick(){
      if(!eb.isConnected) return;
      if(isPlaying) heard = true;
      if((heard && !isPlaying) || performance.now() - t0 > 15000){
        eb.classList.remove("cel-wait"); eb.classList.add("cel-ready"); return; }
      requestAnimationFrame(tick);
    })();
  }
  setTimeout(()=> (function wrapCel(tries){
    const C = (typeof SlideModules !== "undefined") && SlideModules.CELEBRATION;
    if(!C || !C.mount){ if(tries < 200) setTimeout(()=> wrapCel(tries + 1), 25); return; }
    if(C.__celWrapped) return; C.__celWrapped = true;
    const _mount = C.mount;
    C.mount = function(host, slide){
      const r = _mount.apply(this, arguments);
      try { releaseShop(); } catch(e){}            /* round 2t: the shop's held pictures are no longer needed */
      try { celArrowAfterVO(); } catch(e){}
      try { runCelSprite(slide); } catch(e){}
      return r;
    };
  })(0), 0);
  let _celGen = 0;
  /* round 2m — THREE SHEETS, ONE CLOCK (timeline re-ordered in round 2r — see inside: jump first, then
     the line). While she talks the clock is the celebration VO itself, from the moment it is sounding:
     the cursor walks the talk sheet forward (so the body keeps moving naturally) but only ever lands on
     a frame whose mouth matches the VO at that instant — open on each syllable, shut in every dip.
     All three sheets share frame size and alignment (make_cel_sprite.py), so switching never jumps. */
  function runCelSprite(slide){
    const A = CARD && CARD.end_anim;
    const im = document.querySelector("#endScreen .end-mascot");
    if(!A || !im || !A.bits || !A.shabaash) return;
    const gen = ++_celGen;
    let sp = document.getElementById("celSprite");
    if(!sp){
      sp = document.createElement("div"); sp.id = "celSprite"; sp.className = "cel-sprite";
      sp.innerHTML = '<div class="cel-art"></div>';
      im.parentNode.insertBefore(sp, im);
    }
    im.style.display = "none";
    const art = sp.querySelector(".cel-art");
    /* paint the talk + idle sheets once, invisibly, while the screen opens — so the browser decodes and
       uploads them now, not at the शाबाश -> talk switch (measured: a 130-180 ms stall there) */
    [A.talk, A.idle].forEach(sh => {
      const pp = document.createElement("div"); pp.className = "cel-art cel-prepaint";
      pp.style.aspectRatio = A.fw + " / " + A.fh; pp.style.backgroundImage = 'url("' + sh.src + '")';
      sp.appendChild(pp);
      requestAnimationFrame(()=> requestAnimationFrame(()=> setTimeout(()=> pp.remove(), 120)));
    });
    art.style.aspectRatio = A.fw + " / " + A.fh;
    let curSrc = "";
    const show = (sheet, i)=>{
      if(sheet.src !== curSrc){ art.style.backgroundImage = 'url("' + sheet.src + '")'; curSrc = sheet.src; }
      const c = i % A.cols, r = Math.floor(i / A.cols);
      art.style.backgroundPosition = (c * 100 / (A.cols - 1)) + "% " + (r * 100 / (A.cols - 1)) + "%";
      sp.dataset.sheet = sheet === A.shabaash ? "shabaash" : (sheet === A.idle ? "idle" : "talk");
      sp.dataset.f = i;
    };
    const S = A.shabaash, T = A.talk, I = A.idle;
    const OPEN = new Set(T.open);
    const bits = A.bits || "";
    const step = A.step_ms || 25;
    const loud = (t)=> bits.charAt(Math.floor(t / step)) === "1";
    const lenMs = bits.length * step;
    /* round 2r (user + reference HI02H11 r106): SHE JUMPS AND CELEBRATES FIRST, THEN SPEAKS. The line
       («बहुत बढ़िया, दोस्त! तुमने कमाल कर दिया!») has no «शाबाश» to hang the jump on, so the page owns
       the audio (ownsAudio: the engine's auto-play is skipped) and runs:
         jump     «शाबाश» sheet 0-29 at 45 ms/frame (1.35 s) — silent but for the engine's celebration sfx
         landing  «शाबाश» sheet 30-35 (mouth shut, 0.27 s)
         the VO   starts here; the WHOLE line lip-syncs on the talk sheet (the clip speaks from 0 ms)
         after    idle sheet, mouth-shut frames only, looping */
    const JUMP = S.pre.concat(S.word), LAND = S.post, FMS = 45;
    const src = (typeof audioFor === "function") ? audioFor(slide, "prompt") : null;
    if(!src) return;                                   /* no clip: let the engine's own auto-play run */
    state.ownsAudio = true;
    show(S, JUMP[0]);
    let m0 = 0, lastF = 0, smooth = 0, vclock = null;
    let phase = "jump", tj = 0, t0 = 0, waitStart = 0, done = false, cursor = 0, curOpen = null, lastStep = 0;
    const idle = ()=>{
      let j = 0;
      (function tick(){
        if(gen !== _celGen || !sp.isConnected) return;
        show(I, I.loop[j % I.loop.length]); j++;
        setTimeout(tick, 110);
      })();
    };
    (function frame(){
      if(gen !== _celGen || !sp.isConnected || done) return;
      if(CARD.slides[state.idx] !== slide){ done = true; return; }
      const now = performance.now();
      /* the jump's clock starts once the screen's opening work has settled — three smooth paints in a
         row (sunburst, stars, sfx and the sheets' first decode stall the first ~0.2-0.5 s; a jump timed
         from the mount skipped half its frames). Capped at 0.7 s, so she never stands still longer. */
      if(!tj){
        if(!m0){ m0 = now; lastF = now; }
        smooth = (now - lastF < 40) ? smooth + 1 : 0; lastF = now;
        if(smooth >= 3 || now - m0 > 700) tj = now;
        else { requestAnimationFrame(frame); return; }
      }
      if(phase === "jump" || phase === "land"){
        const list = phase === "jump" ? JUMP : LAND, k = Math.floor((now - tj) / FMS);
        if(k < list.length){ show(S, list[k]); requestAnimationFrame(frame); return; }
        if(phase === "jump"){ phase = "land"; tj = now; show(S, LAND[0]); requestAnimationFrame(frame); return; }
        phase = "wait"; waitStart = now;
        play(src, ()=>{});                             /* the line starts as she lands */
        /* the clip's OWN clock (engine: when the source really started + output latency) — a paint
           that runs late after play() no longer shifts the whole track (measured: 52 ms) */
        vclock = (typeof _voiceClock === "function") ? _voiceClock() : null;
      }
      if(phase === "wait"){
        if(isPlaying){ phase = "talk"; t0 = now; }
        else if(now - waitStart > 1800){ done = true; idle(); return; }     /* the VO never started */
        else { requestAnimationFrame(frame); return; }
      }
      const vt = vclock ? vclock().t : null;
      const t = vt != null ? vt : now - t0;
      if(!isPlaying || t > lenMs + 400){ done = true; idle(); return; }
      const want = loud(t + 16);                       /* one paint ahead: the frame shows on the NEXT paint */
      /* step the talk sheet forward: at once when the mouth must change, else every 80 ms */
      if(want !== curOpen || now - lastStep > 80){
        let k = 1;
        while(k < 36 && OPEN.has((cursor + k) % 36) !== want) k++;
        cursor = (cursor + k) % 36;
        show(T, cursor); curOpen = want; lastStep = now;
      }
      sp.dataset.t = Math.round(t); sp.dataset.w = want ? 1 : 0;   /* the sprite's own clock + choice (tests) */
      requestAnimationFrame(frame);
    })();
  }
  /* warm the sheet during the lesson, so the end screen never opens on an empty box */
  setTimeout(()=>{ try { const A = CARD && CARD.end_anim; if(A && A.shabaash){
    window.__celWarm = [A.shabaash.src, A.talk.src, A.idle.src].map(u => { const i = new Image(); i.src = u; if(i.decode) i.decode().catch(()=>{}); return i; }); } } catch(e){} }, 1500);

  /* ============ ASSET GATE, round 2n (user, 2026-10-01) ============
     "The landing image should load completely before the loader disappears ... load all the assets
     before entering, so nothing loads with a delay." The stock loader left on window 'load' OR a 2.5 s
     watchdog, and nothing waited for the landing scene (a CSS background), the other screens' art or
     any sound. Now the loader's dismissal (engine boot loader, patched by inject_money.py) awaits
     this: every image in CARD.preload downloaded AND decoded, every sound fetched AND decoded into the
     engine's own voice-buffer cache (the same URLs play() asks for). Hard cap 30 s — a child is never
     stranded on the loader; the cap is logged. Defined synchronously: boot() may ask before any timer. */
  window.__assetGateFn = function(){
    if(window.__assetGateP) return window.__assetGateP;
    const t0 = performance.now(); window.__gateStartedAt = t0;
    const P = (CARD && CARD.preload) || {};
    const imgs = (P.images || []).map(u => new Promise(res => {
      const im = new Image();
      im.onload = ()=>{ (im.decode ? im.decode() : Promise.resolve()).then(res, res); };
      im.onerror = ()=>{ console.warn("[preload] image failed:", u); res(); };
      im.src = u;
      /* keep decoded copies only of what is on screen the instant the loader goes (the landing);
         holding all 58 decoded bitmaps measurably cost frame rate on the celebration. Everything
         else is in the HTTP cache, so it never touches the network again. */
      if(/scn_landing|new_landing_swiftee|play_btn|startnew_bg|start_card/.test(u))
        (window.__preloadKeep = window.__preloadKeep || []).push(im);
    }));
    const av = (u)=> (typeof _av === "function" ? _av(u) : u);
    /* voice clips are played through play() at the version-stamped URL; sound effects only through
       playSfx() at the PLAIN URL — each is warmed under exactly the key it is played with */
    const aurls = [];
    (P.audio || []).forEach(u => { aurls.push(/\/sfx_/.test(u) ? u : av(u)); });
    /* round 2q: files that are only DOWNLOADED, never decoded (the 4-minute music) — same URL as the
       engine's <audio> element asks for, so it plays from the cache */
    (P.fetch || []).forEach(u => aurls.push("__fetch__" + av(u)));
    const aud = aurls.map(u => u.indexOf("__fetch__") === 0
        ? fetch(u.slice(9), { cache:"force-cache" }).then(r => r.blob()).catch(()=>{ console.warn("[preload] fetch failed:", u); })
        : (typeof _loadVoiceBuffer === "function"
        ? _loadVoiceBuffer(u) : fetch(u, { cache:"force-cache" })).catch(()=>{ console.warn("[preload] audio failed:", u); }));
    let total = imgs.length + aud.length, done = 0;
    const tick = (p)=> p.then(()=>{ done++; window.__preloadProgress = done / Math.max(1, total); });
    const all = Promise.all(imgs.concat(aud).map(tick)).then(()=>{
      window.__preloadMs = Math.round(performance.now() - t0);
      console.log("[preload] %d images + %d sounds ready in %d ms", imgs.length, aud.length, window.__preloadMs);
    });
    const cap = new Promise(res => setTimeout(()=>{ if(window.__preloadMs == null){
      console.warn("[preload] 30 s cap reached at %d%% — entering anyway", Math.round(100 * (window.__preloadProgress || 0)));
      window.__preloadCapped = true; } res(); }, 30000));
    window.__assetGateP = Promise.race([all, cap]);
    return window.__assetGateP;
  };
  /* start downloading at once — not when the loader first asks (window 'load' / the 2.5 s watchdog,
     measured 9.8 s in on a slow link). Waits only for CARD to exist. */
  setTimeout(()=> (function startGate(tries){
    let ok = false; try { ok = !!CARD; } catch(e){}
    if(ok){ window.__assetGateFn(); return; }
    if(tries < 400) setTimeout(()=> startGate(tries + 1), 10);
  })(0), 0);

  /* ============ TRANSITIONS, round 2o (user: "some transition screens sometimes appear and sometimes
     do not") ============ Three causes, all fixed here (engine file untouched, wrapped):
       1. a double tap on the arrow called completeSlide() twice; the second call took the no-gate path
          and mounted the next screen first, so the gate's callback saw the screen had moved and quit.
          -> completeSlide runs once per screen.
       2. the engine shows each round's gate ONCE PER PAGE LOAD (_gatedPhases), so replaying the lesson
          without a reload, or going back with the dev bar, skipped every gate the second time.
          -> a gate is shown every time its round boundary is crossed.
       3. the dev bar's ▶ mounted the next screen directly, so testing with ▶ never showed a gate.
          -> ▶ now goes through the same path as the arrow when it crosses into a new round. */
  setTimeout(()=> (function patchFlow(tries){
    let ok = false;
    try {
      if(typeof completeSlide === "function" && typeof _gatedPhases !== "undefined" && typeof mountSlide === "function"){
        const _cs = completeSlide, _ms = mountSlide;
        let doneFor = -1;
        completeSlide = function(success){
          if(doneFor === state.idx) return;              /* (1) once per screen */
          doneFor = state.idx;
          const nx = CARD.slides[state.idx + 1];
          const r = nx && PHASE_ROUND[nx.phase];
          if(r) _gatedPhases.delete(r);                   /* (2) every crossing shows its gate */
          return _cs.apply(this, arguments);
        };
        mountSlide = function(i){ doneFor = -1; return _ms.apply(this, arguments); };
        window.__devAdvance = (i)=>{                      /* (3) ▶ on the dev bar */
          const cur = CARD.slides[state.idx], nx = CARD.slides[i];
          if(i === state.idx + 1 && nx && PHASE_ROUND[nx.phase] && PHASE_ROUND[nx.phase] !== PHASE_ROUND[cur.phase]){
            completeSlide(true); return true;
          }
          return false;
        };
        ok = true;
      }
    } catch(e){}
    if(!ok && tries < 400) setTimeout(()=> patchFlow(tries + 1), 25);
  })(0), 0);

  const SW = 1333;
  const IE = ()=> (typeof IMG_EXT !== "undefined" && IMG_EXT) ? IMG_EXT : "png";
  const img = (k)=> "assets/Images/" + k + "." + IE();
  const AMS = ()=> (CARD.assets && CARD.assets.audio_ms) || {};
  const A = (slide, key)=> (slide.audio && slide.audio[key]) || null;
  function clip(id){
    if(!id) return null;
    if(id.indexOf("/") >= 0) return id;
    return "assets/Audio/" + id + "." + AUDIO_EXT;
  }
  function el(tag, cls, html){
    const e = document.createElement(tag);
    if(cls) e.className = cls;
    if(html != null) e.innerHTML = html;
    return e;
  }

  /* ---------------------------------------------------------------- audio: one chain at a time */
  /* A chain carries the epoch it started in; a mount bumps the epoch so a chain left over from the
     previous screen is dropped. Every say() also takes a token, so its fallback timer can only fire
     if no later say() has started — a clip cut short by a newer one must not advance its chain. */
  let _gen = 0, _tok = 0;
  function epoch(){ _tok++; return ++_gen; }
  function say(id, next){
    const g = _gen, tok = ++_tok;
    let done = false;
    const go = ()=>{ if(done) return; done = true; if(g !== _gen) return; if(next) next(); };
    if(!id){ setTimeout(go, 0); return; }
    try { play(clip(id), go); } catch(e){ setTimeout(go, 0); return; }
    const ms = (AMS()[id] || 7000) + 1800;
    setTimeout(()=>{ if(tok === _tok) go(); }, ms);
  }
  function sfxFile(name, fb){
    /* round 2n: through the engine's playSfx — the DECODED buffer the loader already warmed, so a sound
       effect never waits on the network (an <audio> element re-requested it, measured on a slow link) */
    if(typeof playSfx === "function"){ try { playSfx(name); return; } catch(e){} }
    try {
      const p = "assets/Audio/" + name + "." + AUDIO_EXT;
      const a = new Audio(typeof _av === "function" ? _av(p) : p);
      a.volume = 0.6;
      a.play().catch(()=>{ if(fb) fb(); });
    } catch(e){ if(fb) fb(); }
  }
  const tone = (f, w, d, v)=>{ if(typeof _tone === "function") _tone(f, w, d, v); };
  const fbCorrect = ()=> sfxFile("sfx_fb_correct", ()=>{ if(typeof sfxCorrect === "function") sfxCorrect(); });
  const fbWrong   = ()=> sfxFile("sfx_fb_incorrect", ()=>{ if(typeof sfxWrongSoft === "function") sfxWrongSoft(); });
  /* round 2o: the team's drop sounds — a note lands with the note sound, a coin with the coin sound */
  const sfxDrop   = (kind)=> sfxFile(kind === "n10" ? "sfx_drop_note" : "sfx_drop_coin",
                                     ()=> tone([560, 840], "sine", 0.13, 0.07));
  const sfxPop    = ()=> tone([720], "sine", 0.10, 0.06);
  /* round 3 (checklist): the team's Standard SFX pack (from MTG2A04_L02_S01) — the confetti and the
     nudge chime are mastered hotter than the rest, so they play at their own, lower gain (that
     lesson: 0.45 against 0.8 for correct). Through the loader's decoded buffers, like playSfx. */
  function sfxVol(name, vol){
    try {
      const src = "assets/Audio/" + name + "." + AUDIO_EXT;
      _loadVoiceBuffer(src).then(buf => {
        const c = _resumeVoiceAudio(); if(!c) return;
        const s = c.createBufferSource(), g = c.createGain();
        s.buffer = buf; g.gain.value = vol; s.connect(g).connect(c.destination); s.start(0);
      }).catch(()=>{});
    } catch(e){}
  }
  const sfxNudge  = ()=> sfxVol("sfx_nudge", 0.4);      /* with every inactivity nudge */
  /* round 20 (QA BUG_06, 2026-10-23): "Swiftee stays SAD after a wrong answer" - and, from the other
     lesson's 2nd QA round, she must not turn back BEFORE the wrong-answer line is over either. The sad
     face now lasts for the whole wrong-attempt sequence (the wrong sound, the shake, any hint line) and
     goes back to her normal face 250 ms after the voice is quiet; a wrong attempt with nothing spoken
     turns back after 3 s. Any other mood (a correct answer) or a new page ends the watch. */
  let _sadT = 0;
  const mood = (m)=>{
    clearInterval(_sadT); _sadT = 0;
    if(typeof setSwMood === "function") setSwMood(m);
    if(m !== "tryagain") return;
    const g = _gen, t0 = performance.now();
    let spoke = false, quiet = 0;
    _sadT = setInterval(()=>{
      if(g !== _gen){ clearInterval(_sadT); _sadT = 0; return; }
      const now = performance.now();
      if(isPlaying || document.body.classList.contains("vo-lock")){ spoke = true; quiet = 0; return; }
      if(!spoke){ if(now - t0 < 3000) return; }
      else { if(!quiet) quiet = now; if(now - quiet < 250) return; }
      clearInterval(_sadT); _sadT = 0;
      if(typeof swMood === "undefined" || swMood === "tryagain") setSwMood("point");   /* her normal face */
    }, 50);
  };
  /* round 24 (user: "whenever VO is playing do not let the user click on any object" - first seen on the
     shop's stall): ONE rule for every note, coin, item and button of ours - nothing takes a tap or a drag
     while the voice is busy. "Busy" is the speaker's own grey state (round 19's body.vo-busy: on while a
     line plays, through the short pauses INSIDE a sequence of lines, off 0.7 s after the last), so the
     child sees it: speaker grey = wait. isPlaying / vo-lock alone left those pauses open. */
  const voBusy = ()=>{ const b = document.body;
    return isPlaying || b.classList.contains("vo-lock") || b.classList.contains("vo-busy"); };

  /* round 20 (QA BUG_07): once a screen is solved the speaker is greyed and takes no tap until the next
     page - it used to replay the instruction of a screen already done. body.spk-done (money_styles.css)
     greys it; the replay is a no-op too (the engine's idle replay calls it). The next mount clears it. */
  function speakerDone(){ state.replayAudio = ()=>{}; document.body.classList.add("spk-done"); }

  /* ---------------------------------------------------------------- stage geometry */
  function stageEl(){ return document.getElementById("stage"); }
  function k(){ const r = stageEl().getBoundingClientRect(); return (r.width / SW) || 1; }
  function box(e){
    const st = stageEl().getBoundingClientRect(), s = (st.width / SW) || 1, r = e.getBoundingClientRect();
    return { x:(r.left - st.left) / s, y:(r.top - st.top) / s, w:r.width / s, h:r.height / s };
  }
  function toStage(cx, cy){
    const st = stageEl().getBoundingClientRect(), s = (st.width / SW) || 1;
    return { x:(cx - st.left) / s, y:(cy - st.top) / s };
  }
  function inside(e, cx, cy){
    const r = e.getBoundingClientRect();
    return cx >= r.left && cx <= r.right && cy >= r.top && cy <= r.bottom;
  }
  function restart(e, cls){ if(!e) return; e.classList.remove(cls); void e.offsetWidth; e.classList.add(cls); }

  /* ---------------------------------------------------------------- currency pieces */
  const KIND = {
    n10: { v:10, img:"cur_note10", cls:"mn-note", label:"₹10", name:"note" },
    c10: { v:10, img:"cur_coin10", cls:"mn-coin mn-c10", label:"₹10", name:"coin" },
    c1:  { v:1,  img:"cur_coin1",  cls:"mn-coin mn-c1",  label:"₹1",  name:"coin" }
  };
  /* The team's currency set ships three states per piece — Default / Glow / Lock — so a source's
     look follows its state classes: .mn-off -> the _lock art, .mn-glowsrc -> the _glow art. Called
     after every class change on a source; a MutationObserver would also work but costs more than
     the handful of call sites. */
  function syncArt(e){
    if(!e || !e.dataset.kind) return;
    const k0 = KIND[e.dataset.kind].img;
    const st = e.classList.contains("mn-off") ? "_lock" : (e.classList.contains("mn-glowsrc") ? "_glow" : "");
    const im = e.querySelector("img");
    const want = img(k0 + st);
    if(im && im.getAttribute("src") !== want) im.setAttribute("src", want);
    e.classList.toggle("st-lock", st === "_lock"); e.classList.toggle("st-glow", st === "_glow");
  }
  function piece(kind, extra){
    const d = el("div", "mn-piece " + KIND[kind].cls + (extra ? " " + extra : ""));
    d.dataset.kind = kind;
    d.innerHTML = '<img src="' + img(KIND[kind].img) + '" alt="' + KIND[kind].label + '" draggable="false" decoding="sync">';   /* round 2t */
    return d;
  }
  function floatAt(kind, b, extra){
    const f = piece(kind, "mn-float" + (extra ? " " + extra : ""));
    f.style.left = b.x + "px"; f.style.top = b.y + "px"; f.style.width = b.w + "px"; f.style.height = b.h + "px";
    stageEl().appendChild(f);
    return f;
  }
  function animTo(f, b, ms, ease){
    return new Promise(res => {
      const a = { x:parseFloat(f.style.left), y:parseFloat(f.style.top), w:parseFloat(f.style.width), h:parseFloat(f.style.height) };
      if(typeof f.animate !== "function"){ res(); return; }
      const an = f.animate([
        { left:a.x + "px", top:a.y + "px", width:a.w + "px", height:a.h + "px" },
        { left:b.x + "px", top:b.y + "px", width:b.w + "px", height:b.h + "px" }],
        { duration:ms || 800, easing:ease || "cubic-bezier(.45,.05,.3,1)", fill:"forwards" });
      /* round 2v (user: "the bounce back is not visible, it disappears in the drop zone"): COMMIT the
         end position to the element's style. A move reads its start from the style, so without this a
         second move (a tapped wrong piece: into the tray, THEN back) started from where the piece had
         been BEFORE the first move — it jumped home in one frame instead of bouncing back. */
      const commit = ()=>{ f.style.left = b.x + "px"; f.style.top = b.y + "px"; f.style.width = b.w + "px"; f.style.height = b.h + "px"; };
      an.onfinish = ()=>{ commit(); res(); };
      an.oncancel = ()=> res();
    });
  }
  /* a piece travels from `fromEl` to `toEl` on its own (demo, ghost, return) */
  function fly(kind, fromEl, toEl, opts){
    opts = opts || {};
    const f = floatAt(kind, box(fromEl), opts.ghost ? "mn-ghost" : "");
    return animTo(f, box(toEl), opts.ms || 850).then(()=>{
      if(!opts.ghost){ f.remove(); return; }
      if(typeof f.animate !== "function"){ f.remove(); return; }
      return new Promise(r => { const an = f.animate([{ opacity:.6 }, { opacity:0 }], { duration:380, fill:"forwards" });
                                an.onfinish = ()=>{ f.remove(); r(); }; });
    });
  }
  function bounceBack(f, src, ms){
    if(!f) return Promise.resolve();
    return animTo(f, box(src), ms || 440, "cubic-bezier(.3,1.35,.5,1)").then(()=>{ f.remove(); restart(src, "mn-bump"); });
  }
  /* round 2t (SME): ONE error mechanic for an extra / incorrect note or coin — BOUNCE BACK, never a
     tray shake, the same for a drag and a tap. A dragged piece is already over the tray, so it
     bounces straight home; a TAPPED piece starts on its own source, so it first travels into the
     tray (as a correct tap does) and then bounces back — otherwise the child would see nothing move. */
  /* round 2v: the error bounce takes 0.62 s (the plain return keeps 0.44 s) so the child SEES the
     piece travel home — at 0.44 s with this overshoot curve it covered the distance in ~0.17 s. */
  function rejectPiece(f, src, zone, shake){
    if(!f) return Promise.resolve();
    /* round 4 (SME, ₹32 / ₹45): `shake` — the drop zone wiggles the moment the refused piece is in it */
    if(f.dataset.tap !== "1" || !zone){ if(shake && zone) restart(zone, "mn-shake"); return bounceBack(f, src, 620); }
    const z = box(zone), w = parseFloat(f.style.width), h = parseFloat(f.style.height);
    return animTo(f, { x:z.x + z.w / 2 - w / 2, y:z.y + z.h / 2 - h / 2, w, h }, 320)
      .then(()=>{ if(shake) restart(zone, "mn-shake"); return bounceBack(f, src, 620); });
  }
  function tapFloat(kind, src){ const f = floatAt(kind, box(src)); f.dataset.tap = "1"; return f; }

  /* DRAG from an endless source. A press that does not travel is a TAP (the shop allows tap-to-add).
     Drags are refused while a voice clip is sounding — the engine-wide drag VO gate. */
  function dragSource(src, kind, h){
    src.addEventListener("pointerdown", (e)=>{
      if(e.button > 0) return;
      if(!h.canStart(kind, src)) return;
      e.preventDefault();
      const p0 = { x:e.clientX, y:e.clientY }, b0 = box(src), s0 = toStage(e.clientX, e.clientY);
      let f = null, moved = false;
      const zone = h.zone();
      const mv = (ev)=>{
        if(!moved && Math.hypot(ev.clientX - p0.x, ev.clientY - p0.y) > 7){
          moved = true;
          f = floatAt(kind, b0, "mn-drag");
          if(h.onPick) h.onPick(kind);
        }
        if(f){
          const s = toStage(ev.clientX, ev.clientY);
          f.style.left = (b0.x + s.x - s0.x) + "px"; f.style.top = (b0.y + s.y - s0.y) + "px";
          if(zone) zone.classList.toggle("mn-hover", inside(zone, ev.clientX, ev.clientY));
        }
      };
      const up = (ev)=>{
        document.removeEventListener("pointermove", mv);
        document.removeEventListener("pointerup", up);
        document.removeEventListener("pointercancel", up);
        if(zone) zone.classList.remove("mn-hover");
        if(!moved){ if(h.onTap) h.onTap(kind, src); return; }
        if(ev.type !== "pointercancel" && zone && inside(zone, ev.clientX, ev.clientY)) h.onDrop(kind, f, src);
        else bounceBack(f, src);
      };
      document.addEventListener("pointermove", mv);
      document.addEventListener("pointerup", up);
      document.addEventListener("pointercancel", up);
    });
  }

  /* the tray the money goes INTO: tens on the first row, ones on the second — so the child sees the
     amount decomposed the way the equation reads it (₹10 + ₹10 + ₹1 + …) */
  function makeTray(){
    const t = el("div", "mn-tray");
    t.innerHTML = '<div class="mn-row mn-row-t"></div><div class="mn-row mn-row-o"></div>';
    return t;
  }
  function addPlaced(tray, kind, f){
    const row = tray.querySelector(KIND[kind].v === 10 ? ".mn-row-t" : ".mn-row-o");
    const p = piece(kind, "mn-placed");
    row.appendChild(p);
    if(f){
      p.style.visibility = "hidden";
      return animTo(f, box(p), 200, "ease-out").then(()=>{ p.style.visibility = ""; f.remove(); p.classList.add("mn-in"); return p; });
    }
    p.classList.add("mn-in");
    return Promise.resolve(p);
  }
  /* a slot where the NEXT piece of `kind` would land — the ghost's destination */
  function nextSlot(tray, kind){
    const row = tray.querySelector(KIND[kind].v === 10 ? ".mn-row-t" : ".mn-row-o");
    const p = piece(kind, "mn-placed mn-slot");
    p.style.visibility = "hidden";
    row.appendChild(p);
    return p;
  }

  function faces(list, cls){
    return '<div class="mn-faces ' + (cls || "") + '">' +
      list.map(kf => '<img class="mn-face ' + (kf.indexOf("note") >= 0 ? "is-note" : "is-coin") +
                     '" src="' + img(kf) + '" alt="" draggable="false">').join("") + '</div>';
  }

  /* ================================================================ MONEY_SHOW (p2) */
  SlideModules.MONEY_SHOW = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      const root = el("div", "mn-show");
      (d.groups || []).forEach((g, i)=>{
        const c = el("div", "mn-show-g mn-pop", faces(g.faces));
        c.style.animationDelay = (250 + i * 420) + "ms";
        root.appendChild(c);
      });
      host.appendChild(root);
      setTimeout(sfxPop, 250); setTimeout(sfxPop, 670);
      state.replayAudio = ()=> say(A(slide, "prompt"));
      say(A(slide, "prompt"), ()=>{ setNavActive(true); });
    }
  };

  /* ================================================================ MONEY_INTRO (round 3) */
  /* SME round 3, teaching: "Keep the screen simple … Swifty will introduce the ₹10 note and ₹1 coin.
     First, show the ₹10 note (front view only) with the text «₹10» above it. Next, show the ₹1 coin
     (front view only) with the text «₹1» above it. Both visuals and labels should appear one by one,
     synchronised with the VO. No separate title or heading." Each picture + its label arrives as its
     own line starts (with a soft pop); the arrow is enabled when the last line ends. */
  SlideModules.MONEY_INTRO = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      $("promptText").textContent = slide.prompt_hi || "";
      const root = el("div", "mn-intro");
      const cols = (d.items || []).map(it => {
        const c = el("div", "mn-intro-it mn-intro-wait " + (it.note ? "is-note" : "is-coin"),
          '<div class="mn-intro-lbl">' + it.label + '</div>' +
          '<img src="' + img(it.img) + '" alt="' + it.label + '" draggable="false" decoding="sync">');
        root.appendChild(c); return c;
      });
      host.appendChild(root);
      const show = (i)=>{ const c = cols[i]; if(!c) return; c.classList.remove("mn-intro-wait"); restart(c, "mn-pop"); sfxPop(); };
      /* round 21 (lead): on a replay (the speaker, or the idle replay) the ₹10 and then the ₹1 PULSATE one
         by one, each for as long as its own line is being said (it used to be a single small bump) */
      const run = (i, first)=>{
        cols.forEach(c => c.classList.remove("mn-say"));
        if(i >= cols.length){ if(first) setNavActive(true); return; }
        if(first) show(i); else { cols[i].classList.remove("mn-pop"); restart(cols[i], "mn-say"); }
        say(d.items[i].say, ()=>{ cols[i].classList.remove("mn-say"); setTimeout(()=> run(i + 1, first), 250); });
      };
      state.replayAudio = ()=> run(0, false);
      setTimeout(()=> run(0, true), 350);
    }
  };

  /* ================================================================ MONEY_SORT (round 3 / 3b) */
  /* SME round 3, guided practice — sorting: a random arrangement of notes and coins, a small wallet in
     a corner. The child CLICKS each piece of the asked value (d.target: ₹10 notes AND ₹10 coins, or the
     ₹1 coins): it goes INTO the wallet with a sound. Any other piece only wiggles (with the standard
     incorrect sound) — no wrong-answer flow. Done when every asked piece is in: confetti + «शाबाश!»,
     then the arrow. Pieces arrive one by one, each with a soft pop (checklist). Inactive 7 s -> a piece
     still to be collected glows, with the nudge chime.
     Round 3b (user): the screen sits in the teaching screen's grid-paper card (blue border) but KEEPS
     the instruction panel and has no Swiftee in the card; the team's wallet is drawn in TWO layers —
     the whole wallet behind, its front pocket in front — and a collected piece flies to the wallet's
     mouth and slides down BETWEEN them, so it really goes inside. No piece is ever placed over the
     wallet: the slots are a 4 x 3 grid, and any slot whose piece would touch the wallet is skipped. */
  /* round 5 (user mockup): the table is the wooden board, the pieces sit in BALANCED slots (3 rows x 3 —
     each slot made for a note or a coin, the mockup's pattern), the denominations are shuffled into the
     slots of their kind on every visit, and the layout is mirrored on some visits. The open coin purse
     sits on the right: a collected piece is lifted over its mouth and drops in BEHIND the purse's front
     rim (obj_purse_front), so it really goes inside. Fractions of the field; the purse keeps x > 0.74. */
  /* round 6 (user): the purse sits in the BOTTOM-RIGHT corner, so the top rows run the full width and
     the bottom row stays left of the purse */
  const SORT_LAYOUTS = {
    mixed: [{k:"note", x:0.160, y:0.18}, {k:"coin", x:0.385, y:0.18}, {k:"note", x:0.600, y:0.19}, {k:"coin", x:0.840, y:0.18},
            {k:"coin", x:0.175, y:0.50}, {k:"note", x:0.400, y:0.51}, {k:"coin", x:0.620, y:0.50},
            {k:"note", x:0.195, y:0.82}, {k:"coin", x:0.430, y:0.82}],
    coins: [{k:"coin", x:0.150, y:0.18}, {k:"coin", x:0.370, y:0.18}, {k:"coin", x:0.590, y:0.18}, {k:"coin", x:0.810, y:0.18},
            {k:"coin", x:0.255, y:0.50}, {k:"coin", x:0.470, y:0.50}, {k:"coin", x:0.660, y:0.50},
            {k:"coin", x:0.165, y:0.82}, {k:"coin", x:0.400, y:0.82}]
  };
  const SORT_SIZE = { note:[210, 99], coin:[112, 112] };
  SlideModules.MONEY_SORT = {
    mount(host, slide){
      const gen = epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data, T = d.target;
      /* round 3d: the instruction is shown when Swiftee starts saying it — after the pieces arrive */
      $("promptText").textContent = "";
      const root = el("div", "mn-sort-card");
      if(d.board_img) root.style.backgroundImage = 'url("' + img(d.board_img) + '")';
      root.insertAdjacentHTML("beforeend", '<span class="mn-star s1">★</span><span class="mn-star s2">★</span><span class="mn-star s3">★</span>');
      const field = el("div", "mn-sort-field");
      const wallet = el("div", "mn-wallet",
        '<img class="mn-wb" src="' + img(d.wallet_img) + '" alt="" draggable="false" decoding="sync">' +
        '<div class="mn-wfly"></div>' +
        '<img class="mn-wf" src="' + img(d.wallet_front_img) + '" alt="" draggable="false" decoding="sync">');
      field.appendChild(wallet);
      root.appendChild(field);
      host.appendChild(root);
      const FW = field.offsetWidth || 1100, FH = field.offsetHeight || 380;
      const slotsOf = (kind)=>{
        const s = (SORT_LAYOUTS[d.layout] || SORT_LAYOUTS.mixed).filter(q => q.k === kind)
          .map(q => ({ x:q.x * FW, y:q.y * FH }));
        for(let i = s.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); const x = s[i]; s[i] = s[j]; s[j] = x; }
        return s;
      };
      const free = { note:slotsOf("note"), coin:slotsOf("coin") };
      const pieces = [];
      (d.pieces || []).forEach(pc => {
        const kind = pc.note ? "note" : "coin", sz = SORT_SIZE[kind];
        const c = free[kind].shift() || free[kind === "note" ? "coin" : "note"].shift();
        if(!c) return;
        const jx = (Math.random() * 2 - 1) * 6, jy = (Math.random() * 2 - 1) * 6;
        const x = Math.max(6, Math.min(FW - sz[0] - 6, c.x - sz[0] / 2 + jx)), y = Math.max(6, Math.min(FH - sz[1] - 6, c.y - sz[1] / 2 + jy));
        const e = el("div", "mn-sp mn-sp-wait " + (pc.note ? "is-note" : "is-coin"),
                     '<img src="' + img(pc.img) + '" alt="₹' + pc.value + '" draggable="false" decoding="sync">');
        e.style.left = x + "px"; e.style.top = y + "px";
        e.style.setProperty("--tilt", ((Math.random() * 2 - 1) * (pc.note ? 7 : 11)).toFixed(1) + "deg");
        e.dataset.value = pc.value;
        field.insertBefore(e, wallet);
        pieces.push(e);
      });
      /* appear in a random order, not slot order */
      const shown = pieces.slice().sort(()=> Math.random() - 0.5);
      const want = pieces.filter(e => +e.dataset.value === T);
      let got = 0, armed = false, done = false, wrongs = 0, lastAct = Date.now(), nudges = 0;
      const touch = ()=>{ lastAct = Date.now(); nudges = 0; };
      root.addEventListener("pointerdown", touch, true);
      shown.forEach((e, k)=> setTimeout(()=>{ if(!e.isConnected) return; e.classList.remove("mn-sp-wait"); restart(e, "mn-sp-in"); sfxPop(); }, 200 + k * 170));
      /* round 8 (user): the pop-in animation must not stay on the piece — it outranked the wrong-tap wiggle */
      pieces.forEach(e => e.addEventListener("animationend", (ev)=>{ if(ev.animationName === "mnSpIn") e.classList.remove("mn-sp-in"); }));
      const ready = 200 + shown.length * 170 + 250;
      const finish = ()=>{
        done = true; state.locked = true; speakerDone();
        restart(wallet, "mn-bump");
        fbCorrect(); mood("celebrate");
        if(typeof confettiCannon === "function") confettiCannon();
        SwiftPAL.emit("money_sort_done", { slide_id:slide.id, phase:slide.phase, value:wrongs === 0, target:T, wrong:wrongs,
          latency_ms:Date.now() - state.slideStart });
        say(A(slide, "done"), ()=>{ setNavActive(true); $("navBtn").onclick = ()=> completeSlide(wrongs === 0); });
      };
      /* INTO the wallet: the piece is re-drawn inside the wallet, between its two layers — first it
         travels to just above the wallet's mouth (shrinking), then slides down behind the front pocket */
      /* INTO the purse: the piece is re-drawn inside the purse, between its two layers — it is lifted over
         the purse's open mouth (shrinking), then drops in behind the front rim, out of sight */
      /* round 6 (user: "when the coin or note goes inside the purse it should be visible inside the purse as
         it has an open mouth"): the piece is lifted over the mouth, then drops in and STAYS there — resting in
         the opening with its lower part behind the front rim, slightly tilted, beside the ones before it.
         The rim's top edge in the purse art runs from y .546 (x .17) to y .692 (x .77) of the picture. */
      const RIM = (fx)=> 0.546 + (fx - 0.169) * 0.245;
      const REST = [{x:0.42, r:-9}, {x:0.58, r:8}, {x:0.33, r:5}, {x:0.66, r:-6}, {x:0.50, r:2}];
      let rested = 0;
      const intoWallet = (e)=> new Promise(res => {
        const b = box(e), w = box(wallet), isNote = e.classList.contains("is-note");
        const f = el("div", "mn-wpiece " + (isNote ? "is-note" : "is-coin"), e.innerHTML);
        f.style.left = (b.x - w.x) + "px"; f.style.top = (b.y - w.y) + "px";
        f.style.width = b.w + "px"; f.style.height = b.h + "px";
        wallet.querySelector(".mn-wfly").appendChild(f);
        const tw = w.w * (isNote ? 0.44 : 0.26), th = tw * b.h / b.w;
        const spot = REST[rested++ % REST.length];
        const cx = w.w * spot.x, restY = w.h * RIM(spot.x) - th * 0.62;   /* ~60 % shows above the rim */
        animTo(f, { x:cx - tw / 2, y:w.h * 0.12 - th / 2, w:tw, h:th }, 560).then(()=>{
          sfxFile(isNote ? "sfx_drop_note" : "sfx_drop_coin");
          f.style.transform = "rotate(" + spot.r + "deg)";
          return animTo(f, { x:cx - tw / 2, y:restY, w:tw, h:th }, 320, "cubic-bezier(.5,0,.9,.6)");
        }).then(()=>{ restart(wallet, "mn-bump"); res(); });
      });
      /* round 5 (SME: "On the first wallet screen, show a hand nudge on the ₹10 coin to guide the child to
         tap it"): when the instruction ends, the standard hand taps a ₹10 COIN a few times; any tap ends it */
      let hand = null, handCoin = null;
      /* round 9 (SME): the coin the hand points at also glows (the brighter golden halo) while the hand is up */
      const dropHand = ()=>{ if(hand){ hand.remove(); hand = null; } if(handCoin){ handCoin.classList.remove("mn-sp-handglow"); handCoin = null; } };
      const showHand = ()=>{
        if(!d.hand_nudge || done || got) return;
        const c = pieces.find(e => +e.dataset.value === T && e.classList.contains("is-coin") && !e.classList.contains("mn-sp-gone"))
               || pieces.find(e => +e.dataset.value === T && !e.classList.contains("mn-sp-gone"));
        if(!c) return;
        hand = el("img", "mn-hand"); hand.src = "assets/UI/nudge_hand_new.svg"; hand.alt = "";
        const hw = 74, hh = 93;
        hand.style.left = (c.offsetLeft + c.offsetWidth / 2 - hw * 0.38) + "px";
        hand.style.top = (c.offsetTop + c.offsetHeight / 2 - hh * 0.06) + "px";
        field.appendChild(hand);
        handCoin = c; c.classList.add("mn-sp-handglow");
        setTimeout(()=>{ if(hand) dropHand(); }, 4200);
      };
      root.addEventListener("pointerdown", dropHand, true);
      pieces.forEach(e => {
        e.addEventListener("click", ()=>{
          if(!armed || done || voBusy() || e.classList.contains("mn-sp-gone") || e.classList.contains("mn-sp-wait")) return;   /* round 24 */
          touch(); dropHand();
          if(+e.dataset.value !== T){
            e.classList.remove("mn-sp-in"); restart(e, "mn-wiggle"); fbWrong(); mood("tryagain"); wrongs++;
            SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, value:+e.dataset.value, target:T });
            return;
          }
          const p = intoWallet(e);
          e.classList.add("mn-sp-gone");
          mood("happy");
          p.then(()=>{
            if(gen !== _gen) return;
            if(++got >= want.length && !done) setTimeout(()=>{ if(gen === _gen) finish(); }, 250);
          });
        });
      });
      /* inactivity: a piece still to be collected glows, with the nudge chime — every 7 s while idle */
      const idleT = setInterval(()=>{
        if(!root.isConnected){ clearInterval(idleT); return; }
        if(!armed || done || isPlaying){ lastAct = Math.max(lastAct, Date.now() - 1000); return; }
        if(Date.now() - lastAct < (d.idle_ms || 7000) || nudges >= 5) return;
        lastAct = Date.now(); nudges++;
        const left = want.filter(e => !e.classList.contains("mn-sp-gone"));
        const e = left[Math.floor(Math.random() * left.length)];
        if(e){ restart(e, "mn-sp-hint"); sfxNudge(); }
      }, 500);
      state.replayAudio = ()=> say(A(slide, "prompt"));
      setTimeout(()=>{ if(gen !== _gen) return;
        $("promptText").textContent = slide.prompt_hi || "";
        say(A(slide, "prompt"), ()=>{ armed = true; touch(); showHand(); }); }, ready);
    }
  };

  /* ================================================================ MONEY_PICK (p3–p6) */
  SlideModules.MONEY_PICK = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      const root = el("div", "mn-pick");
      const row = el("div", "mn-pick-row");
      const fb = el("div", "mn-pick-fb");
      const cards = d.options.map(o => {
        const c = el("div", "mn-card", faces(o.faces));
        c.dataset.ok = o.correct ? "1" : "";
        row.appendChild(c);
        return c;
      });
      const reveal = el("div", "mn-reveal", faces(d.reveal_faces || [], "big") + '<div class="mn-reveal-t"></div>');
      root.append(row, fb, reveal);
      host.appendChild(root);
      const good = cards.find(c => c.dataset.ok);
      let armed = false, done = false, idleT = 0;
      const armIdle = ()=>{
        clearTimeout(idleT);
        if(!d.idle_pulse_ms) return;
        idleT = setTimeout(()=>{ if(!done && root.isConnected) restart(good, "mn-pulse"); }, d.idle_pulse_ms);
      };
      state.replayAudio = ()=> say(A(slide, "prompt"));
      cards.forEach(c => {
        c.onclick = ()=>{
          if(!armed || done || c.classList.contains("mn-bad") || isPlaying) return;
          clearTimeout(idleT);
          if(c.dataset.ok){
            done = true; state.locked = true;
            c.classList.remove("mn-pulse");
            c.classList.add("mn-ok");
            cards.forEach(x => { if(x !== c) x.classList.add("mn-out"); });
            fbCorrect(); mood("celebrate");
            if(typeof confettiCannon === "function") confettiCannon();
            /* round 2q: no on-screen praise — the VO «शाबाश! यह … है।» alone */
            if(d.correct_text){ fb.textContent = d.correct_text; fb.classList.add("show", "ok"); }
            SwiftPAL.emit("money_pick_first_try", { slide_id:slide.id, phase:slide.phase, value:state.attempts === 0,
              attempts:state.attempts + 1, latency_ms:Date.now() - state.slideStart });
            say(A(slide, "correct"), ()=>{
              setNavActive(true);
              $("navBtn").onclick = ()=> completeSlide(state.attempts === 0);
            });
          } else {
            state.attempts++;
            SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, attempts:state.attempts });
            fbWrong(); mood("tryagain");
            restart(c, "mn-shake");
            c.classList.add("mn-bad");
            reveal.querySelector(".mn-reveal-t").textContent = d.wrong_text || "";
            armed = false;
            setTimeout(()=>{
              reveal.classList.add("show");
              say(A(slide, "wrong"), ()=>{
                setTimeout(()=>{ reveal.classList.remove("show"); armed = true; armIdle(); }, 500);
              });
            }, 380);
          }
        };
      });
      say(A(slide, "prompt"), ()=>{ armed = true; armIdle(); });
    }
  };

  /* ================================================================ MONEY_SCENE (p7) */
  SlideModules.MONEY_SCENE = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      const root = el("div", "mn-scene", '<img class="mn-scene-img mn-pop' + (d.scene ? " is-scene" : "") + '" src="' + img(d.img) + '" alt="">');
      host.appendChild(root);
      state.replayAudio = ()=> say(A(slide, "prompt"));
      say(A(slide, "prompt"), ()=> setNavActive(true));
    }
  };

  /* ================================================================ MONEY_LIST (p8) */
  SlideModules.MONEY_LIST = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      const root = el("div", "mn-list mn-zoom");
      /* each row APPEARS as the VO names it (its cue), then lights up while it is being named; on a
         replay (the audio chip or the engine's inactivity replay) the rows only light up in turn. */
      const VO_AT = 700;
      const rows = d.rows.map((r, i) => {
        const e = el("div", "mn-li mn-li-wait",
          '<span class="mn-li-ic">' + (r.img ? '<img src="' + img(r.img) + '" alt="" draggable="false">' : "") + '</span>' +
          '<span class="mn-li-n">' + r.name + '</span>' +
          '<span class="mn-li-p"><span>₹' + r.price + '</span></span>');
        const at = VO_AT + (r.cue_ms || (600 + i * 700)) - 120;
        setTimeout(()=>{ if(!e.isConnected) return; e.classList.remove("mn-li-wait"); sfxPop(); }, at);
        root.appendChild(e);
        return e;
      });
      host.appendChild(root);
      const pulses = ()=>{
        const g = _gen;
        rows.forEach((e, i)=>{
          const at = (d.rows[i].cue_ms || (600 + i * 700));
          setTimeout(()=>{ if(g !== _gen) return;
            rows.forEach(x => x.classList.remove("mn-say"));
            restart(e, "mn-say"); }, at);
        });
        setTimeout(()=>{ if(g === _gen) rows.forEach(x => x.classList.remove("mn-say")); },
                   (d.rows[d.rows.length - 1].cue_ms || 4000) + 1300);
      };
      const run = (after)=>{ pulses(); say(A(slide, "prompt"), after); };
      state.replayAudio = ()=> run();
      setTimeout(()=> run(()=> setNavActive(true)), VO_AT);   /* after the card lands */
    }
  };

  /* ================================================================ MONEY_BUILD (p9–p13 + toffee) */
  SlideModules.MONEY_BUILD = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data, T = d.target, TP = Math.floor(T / 10), OP = T % 10;
      const teach = d.mode === "teach";
      if(d.prompt_delayed) $("promptText").textContent = "";

      const root = el("div", "mn-build" + (d.total_below ? " mn-total-below" : "") + (d.tray_down ? " mn-tray-down" : ""));
      /* round 2d: picture + price tag in a card, no name text (the name is the image's alt) */
      /* round 3 (SME): no item picture — only the amount, prominently (d.no_item) */
      const item = d.no_item
        ? el("div", "mn-item mn-item-amt", '<div class="mn-tag mn-tag-big"><span>₹' + T + '</span></div>')
        : el("div", "mn-item", '<img class="mn-item-img" src="' + img(d.item_img) + '" alt="' + (d.item_name || "") + '">' +
                               '<div class="mn-tag"><span>₹' + T + '</span></div>');
      const tcol = el("div", "mn-tcol");
      const tgt = el("div", "mn-target");
      const tray = makeTray();
      const tot = el("div", "mn-total", 'कुल <b>₹0</b>');
      tgt.appendChild(tray);
      /* (round 3c: the «कुल» counter stays IN the drop zone, top-right; on the amount-only screens the
         money starts below it instead — data.tray_down — so it never hides a note) */
      if(d.total_below){ tcol.append(tgt, tot); } else { tgt.appendChild(tot); tcol.appendChild(tgt); }
      const top = el("div", "mn-top"); top.append(item, tcol);
      const bottom = el("div", "mn-bottom");
      const bank = el("div", "mn-bank");
      const srcs = {};
      (d.sources || []).forEach(kd => { const s = piece(kd, "mn-src"); srcs[kd] = s; bank.appendChild(s); });
      bottom.appendChild(bank);
      /* round 3 (checklist): the notes / coins arrive one by one, each with a soft pop */
      /* round 23 (user: "after highlighting for a fraction of a second the currency disappears and re-appears"):
         the pop-in must be TAKEN OFF once it has played. While .mn-pop stayed on, any later animation on the
         piece (the round-22 highlight, a hint pulse) replaced it - and when that one ended, mnPop started
         again from scratch: invisible for its delay (backwards fill), then a second pop-in. */
      const unPop = (s)=>{ s.classList.remove("mn-pop"); s.style.animationDelay = ""; };
      if(d.pop_sources) Object.keys(srcs).forEach((kd, i)=>{ const s = srcs[kd]; s.style.animationDelay = (150 + i * 300) + "ms";
        s.classList.add("mn-pop"); setTimeout(()=>{ if(s.isConnected) sfxPop(); }, 150 + i * 300);
        s.addEventListener("animationend", (ev)=>{ if(ev.animationName === "mnPop") unPop(s); }); });
      { const nx = CARD.slides[state.idx + 1]; if(nx && nx.type === "SHOP_GAME") warmShop(); }   /* round 3 */
      let chk = null;
      if(d.check_label){ chk = el("button", "mn-check", d.check_label); chk.disabled = true; bottom.appendChild(chk); }
      const eq = el("div", "mn-eq");
      root.append(top, bottom, eq);
      host.appendChild(root);

      const tensKind = srcs.n10 ? "n10" : (srcs.c10 ? "c10" : null);
      let tc = 0, oc = 0, done = false, armed = false, reached = false;
      const wrongN = { tens:0, ones:0 };
      const off = new Set();
      const total = ()=> tc * 10 + oc;
      const setTotal = ()=>{
        tot.querySelector("b").textContent = "₹" + total();
        restart(tot, "mn-bump");
        if(chk) chk.disabled = !(tc + oc) || done;
      };
      const setOff = (kd, on)=>{ if(!srcs[kd]) return; srcs[kd].classList.toggle("mn-off", on); if(on) off.add(kd); else off.delete(kd); syncArt(srcs[kd]); };
      /* round 2e: a currency hint is a GLOW, never a pulse — a scaling piece is hard to grab.
         hint(kd) glows three times; hintOn(kd) glows until that piece is dragged (a teach step that is
         waiting for the child). Both are filter-only, so the piece never moves under the finger. */
      const clearHints = ()=> Object.keys(srcs).forEach(kd => srcs[kd].classList.remove("mn-hintglow", "mn-hintglow-on", "mn-pulse"));
      const pulse  = (kd)=>{ if(srcs[kd]) restart(srcs[kd], "mn-hintglow"); };
      const hintOn = (kd)=>{ if(srcs[kd]){ srcs[kd].classList.remove("mn-hintglow"); srcs[kd].classList.add("mn-hintglow-on"); } };

      /* ---- idle ladder: pulse the currency that is needed, then send its ghost to the tray ---- */
      let lastAct = Date.now(), idleN = 0, idleTimer = 0;
      const touch = ()=>{ lastAct = Date.now(); };
      root.addEventListener("pointerdown", touch, true);
      const needKind = ()=> (tc < TP && tensKind && !off.has(tensKind)) ? tensKind : "c1";
      const ghost = (kd)=>{ if(!srcs[kd]) return; const slot = nextSlot(tray, kd);
        fly(kd, srcs[kd], slot, { ghost:true, ms:1000 }).then(()=> slot.remove()); };
      let teachWait = null;
      /* round 3 (SME): ₹14 / ₹32 / ₹45 — STRICT ORDER: ₹10 first (₹1 locked), then ₹1 (₹10 locked);
         no tolerance, no other order; complete the moment the amount is formed. d.mode "ghost" (₹14
         only) also shows a ghost of the next piece before EVERY move — one ₹10, then each ₹1 — and
         never moves money itself; "seq" (₹32 / ₹45) has no ghost. */
      const seqMode = d.mode === "seq" || d.mode === "ghost";
      const ghostMode = d.mode === "ghost";
      /* round 4 (SME): on ₹32 / ₹45 (d.keep_tens_open) the ₹10 is NOT locked once its notes are in — the
         ₹1 unlocks and an extra ₹10 goes through the hint ladder in wrong(); the 3rd extra locks it */
      let tensLocked = false;
      const seqLocks = ()=>{
        if(!seqMode || !tensKind) return;
        const tensPhase = tc < TP;
        setOff(tensKind, (!tensPhase && !d.keep_tens_open) || tensLocked); setOff("c1", tensPhase || oc >= OP);
      };
      const stepGhost = ()=>{
        if(!ghostMode || done || reached || !root.isConnected) return;
        const kd = needKind(); if(!srcs[kd] || off.has(kd)) return;
        hintOn(kd); ghost(kd);
      };
      const idleTick = ()=>{
        if(!root.isConnected){ clearInterval(idleTimer); return; }
        if(done || !armed || reached || isPlaying || (teach && !teachWait)){ touch(); return; }
        /* round 2o (user): the teaching reminder plays ONCE, ~10 s after the child stops — a gentle
           reminder, not a loop. Practice keeps its silent pulse -> ghost nudge, capped at 3. */
        if(Date.now() - lastAct < (teach ? 10000 : (d.idle_ms || 7000))) return;
        lastAct = Date.now();
        if(seqMode){                                   /* round 3: ₹14 / ₹32 / ₹45 — every 7 s, up to 3 */
          if(idleN >= 3) return;
          idleN++;
          /* round 3d (SME: "Only the ₹14 amount-making screen will have ghost animations"): ₹32 / ₹45
             nudge with the glow + chime alone; the ghost is ₹14's (mode "ghost") only */
          const kd = needKind(); pulse(kd); if(ghostMode) ghost(kd); sfxNudge();
          return;
        }
        if(teach){
          if(!teachWait || teachWait.reminded) return;
          teachWait.reminded = true;
          const lines = teachWait.idle || [];
          pulse(teachWait.kind);
          if(lines.length) say(lines[0]);
        } else {
          if(idleN >= 3) return;
          idleN++;
          const kd = needKind();
          if(idleN === 1) pulse(kd); else { pulse(kd); ghost(kd); }
        }
      };
      idleTimer = setInterval(idleTick, 500);

      /* ---- completion ---- */
      /* round 21 (lead): the equation is always "₹<all the tens> + ₹<all the ones> = ₹T" — ₹10 + ₹4 = ₹14,
         ₹30 + ₹2 = ₹32, ₹40 + ₹5 = ₹45 — never every ₹10 and every ₹1 written out */
      const equation = ()=>{
        const parts = [];
        if(tc) parts.push("₹" + tc * 10);
        if(oc) parts.push("₹" + oc);
        return parts.join(" + ") + " = ₹" + T;
      };
      const finish = ()=>{
        if(done) return;
        done = true; state.locked = true;
        Object.keys(srcs).forEach(kd => { srcs[kd].classList.add("mn-off"); syncArt(srcs[kd]); });
        if(chk){ chk.classList.remove("mn-pulse"); chk.disabled = true; }
        tot.classList.add("mn-green"); tgt.classList.add("mn-done");
        tray.querySelectorAll(".mn-placed").forEach((p, i)=> setTimeout(()=> p.classList.add("mn-glow"), i * 90));
        eq.textContent = equation(); root.classList.add("mn-finished");
        if(d.eq_in_band) $("promptText").innerHTML = '<span class="mn-band-eq">' + equation() + '</span>';
        fbCorrect(); mood("celebrate");
        if(typeof confettiCannon === "function") confettiCannon();
        const clean = wrongN.tens + wrongN.ones === 0;
        SwiftPAL.emit("money_build_done", { slide_id:slide.id, phase:slide.phase, value:clean, target:T,
          tens:tc, ones:oc, wrong_tens:wrongN.tens, wrong_ones:wrongN.ones, latency_ms:Date.now() - state.slideStart });
        speakerDone();                                            /* round 20 (QA BUG_07) */
        say(A(slide, "done"), ()=>{
          setNavActive(true);
          $("navBtn").onclick = ()=> completeSlide(clean);
        });
        spokenHighlight();
      };
      /* round 2p: AS THE CLOSING LINE NAMES THEM. «एक दस रुपये का नोट» lights the ₹10 row, «चार एक रुपये के
         सिक्के» the ₹1 row, «कुल मिलाकर बने …» both + the total. The windows are measured from the clip
         by the build (data.done_cues, ms in the clip) and read on the clip's own clock (engine
         _voiceClock — when it is really audible), so the light moves with the words. */
      function spokenHighlight(){
        const C = d.done_cues; if(!C) return;
        const rowT = tray.querySelector(".mn-row-t"), rowO = tray.querySelector(".mn-row-o");
        const clock = (typeof _voiceClock === "function") ? _voiceClock() : null;
        const t0 = performance.now(), g = _gen;
        const set = (el, on)=>{ if(el) el.classList.toggle("mn-say-hi", !!on); };
        (function tick(){
          if(!root.isConnected || g !== _gen) return;
          let t = null, ended = false;
          if(clock){ const c = clock(); t = c.t; ended = c.ended; }
          else t = performance.now() - t0 - 80;
          if(clock && t == null && !ended && performance.now() - t0 > 2500) ended = true;   /* never started */
          const inW = (w)=> w && t != null && t >= w[0] && t <= w[1];
          const tot_on = inW(C.total);
          set(rowT, inW(C.tens) || tot_on); set(rowO, inW(C.ones) || tot_on); set(tot, tot_on);
          if(ended){ set(rowT, 0); set(rowO, 0); set(tot, 0); return; }
          requestAnimationFrame(tick);
        })();
      }
      const onReached = ()=>{
        reached = true;
        tot.classList.add("mn-green");
        Object.keys(srcs).forEach(kd => { srcs[kd].classList.add("mn-off"); syncArt(srcs[kd]); });
        if(chk){ chk.disabled = false; restart(chk, "mn-pulse"); }
        else finish();
      };

      /* ---- the ladder (practice) ---- */
      const wrong = (type, kind, f, src)=>{
        /* round 4 (SME, ₹32 / ₹45): an extra ₹10 — it ALWAYS bounces back home with the drop zone shaking;
           1st: nothing more (no VO) · 2nd: a ghost of the ₹1 coin into the tray + «ध्यान से देखिए! अब एक
           रुपये के सिक्कों से <the ₹ still missing> बनाइए।» · 3rd: the ₹10 locks (attention to the ₹1) */
        if(seqMode && d.keep_tens_open && type === "tens"){
          rejectPiece(f, src, tgt, true);
          state.attempts++;
          SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, attempts:state.attempts, kind:type, total:total() });
          mood("tryagain"); fbWrong();
          const n = ++wrongN.tens;
          if(n === 2){ ghost("c1"); say((d.ones_hint || {})[String(T - total())]); }
          else if(n >= 3){ tensLocked = true; setOff(tensKind, true); }
          return;
        }
        rejectPiece(f, src, tgt);                                 /* round 2t: bounce back, no tray shake */
        state.attempts++;
        SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, attempts:state.attempts, kind:type, total:total() });
        mood("tryagain");
        if(teach){
          const line = (d.teach_wrong || {})[kind];
          fbWrong();
          if(line){ say(line); if(teachWait) pulse(teachWait.kind); }
          return;
        }
        const n = ++wrongN[type];
        fbWrong();
        if(n === 1) return;                                       /* A1: bounce + gentle buzz */
        const L = ((d.ladder || {})[type]) || {};
        const pair = L[String(total())] || L["*"] || [];
        const need = type === "tens" ? "c1" : tensKind;
        if(n === 2){ say(pair[0]); ghost(need); }                /* A2: line + ghost of what IS needed */
        else {                                                    /* A3: line; right one glows, wrong one fades */
          say(pair[1] || pair[0]);
          if(srcs[need]){ srcs[need].classList.add("mn-glowsrc"); syncArt(srcs[need]); }
          if(type === "tens"){ ["n10", "c10"].forEach(kd => setOff(kd, true)); }
          else setOff("c1", true);
        }
      };

      const accept = (kind, f)=>{
        if(KIND[kind].v === 10) tc++; else oc++;
        const n = tc + oc;
        sfxDrop(kind); mood("happy");
        addPlaced(tray, kind, f);
        setTotal(); touch(); idleN = 0;
        clearHints();
        if(total() === T){ onReached(); return true; }
        if(seqMode){ seqLocks(); setTimeout(stepGhost, 450); }
        return false;
      };

      Object.keys(srcs).forEach(kd => dragSource(srcs[kd], kd, {
        zone: ()=> tgt,
        canStart: (kind)=> armed && !done && !reached && !off.has(kind) && !voBusy(),          /* round 24 */
        /* round 2p: a TAP on a note / coin works like dragging it into the tray (same rules) */
        onTap: (kind, src)=> handleDrop(kind, tapFloat(kind, src), src),
        onDrop: (kind, f, src)=> handleDrop(kind, f, src)
      }));
      function handleDrop(kind, f, src){
        {
          const v = KIND[kind].v;
          /* teach: a drop only counts while a child step is open — never between two scripted beats */
          if(teach && !teachWait){ bounceBack(f, src); return; }
          if(teach && KIND[kind].v !== KIND[teachWait.kind].v){
            wrong(v === 10 ? "tens" : "ones", kind, f, src); return;
          }
          if(v === 10 ? tc >= TP : oc >= OP){ wrong(v === 10 ? "tens" : "ones", kind, f, src); return; }
          const hit = accept(kind, f);
          if(teach){
            const w = teachWait; teachWait = null;
            clearHints();
            if(!hit) setTimeout(runStep, 250);
          }
        }
      }

      if(chk) chk.onclick = ()=>{
        if(done || !(tc + oc) || voBusy()) return;                /* round 24 */
        touch();
        if(total() === T){ finish(); return; }
        state.attempts++;
        fbWrong(); mood("tryagain");                              /* round 2t: no tray shake */
        SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, attempts:state.attempts, kind:"under", total:total() });
        say((d.under || {})[String(total())]);
      };

      /* ---- teach: the scripted demonstration ---- */
      const steps = d.script || [];
      let si = 0, curLine = null;
      const autoPlace = (kind)=> new Promise(res => {
        const src = srcs[kind];
        const slot = nextSlot(tray, kind);
        fly(kind, src, slot, { ms:1000 }).then(()=>{
          slot.remove();
          if(KIND[kind].v === 10) tc++; else oc++;
          addPlaced(tray, kind, null); sfxDrop(kind); setTotal();
          res();
        });
      });
      function runStep(){
        if(done || si >= steps.length) return;
        const s = steps[si++];
        if(s.say) curLine = s.say;               /* a silent step keeps the last instruction for 🔊 */
        if(s.show_prompt) $("promptText").textContent = slide.prompt_hi || "";
        if(s.pulse_total) setTimeout(()=> restart(tot, "mn-pulse"), 400);
        let voDone = false, moveDone = !s.auto;
        const next = ()=>{
          if(!voDone || !moveDone) return;
          if(s.child){
            teachWait = { kind:s.child, idle:s.idle || [] };
            armed = true; touch(); idleN = 0;
            hintOn(s.child);                      /* glows from the moment it can be dragged */
          } else runStep();
        };
        if(s.auto) setTimeout(()=> autoPlace(s.auto).then(()=>{ moveDone = true; next(); }), s.auto_delay || 900);
        /* (4) the price tag pulses while the VO says the amount — as on the practice screens */
        if(s.tag) restart(item.querySelector(".mn-tag"), "mn-pulse");
        say(s.say, ()=>{ voDone = true; next(); });
      }

      if(teach){
        state.replayAudio = ()=>{ if(curLine) say(curLine); };
        runStep();
      } else {
        /* round 22 (lead, ₹14): while a line says «दस रुपये» the ₹10 below lights up, while it says «एक
           रुपये (के सिक्कों)» the ₹1 does - in the opening line, the instruction, and the instruction's
           replay. data.say_cues = per line, the ms windows in the clip (measured by the build, word by
           word over the clip's pauses); read on the clip's own clock, like the closing line's rows. */
        const sayCued = (key, next)=>{
          say(A(slide, key), next);
          const C = d.say_cues && d.say_cues[key]; if(!C) return;
          const clock = (typeof _voiceClock === "function") ? _voiceClock() : null;
          const t0 = performance.now(), g = _gen;
          const set = (kd, on)=>{ const s = srcs[kd]; if(!s) return;
            if(on && s.classList.contains("mn-pop")) unPop(s);          /* round 23: never return to the pop-in */
            s.classList.toggle("mn-say-src", !!on); };
          (function tick(){
            if(!root.isConnected || g !== _gen){ Object.keys(srcs).forEach(kd => set(kd, 0)); return; }
            let t = null, ended = false;
            if(clock){ const c = clock(); t = c.t; ended = c.ended; } else t = performance.now() - t0 - 80;
            if(clock && t == null && !ended && performance.now() - t0 > 2500) ended = true;
            if(t != null && t > (AMS()[A(slide, key)] || 8000) + 300) ended = true;
            Object.keys(C).forEach(kd => set(kd, !ended && t != null && t >= C[kd][0] - 60 && t <= C[kd][1] + 150));
            if(!ended) requestAnimationFrame(tick);
          })();
        };
        state.replayAudio = ()=> sayCued("prompt");
        restart(item.querySelector(".mn-tag"), d.tag_fx === "glow" ? "mn-tagglow" : "mn-pulse");
        /* round 21 (lead, ₹14): while Swiftee is still talking («…₹10 और ₹1 से…») BOTH the ₹10 and the ₹1 are
           shown as they are (not greyed; nothing can be taken until the lines end - `armed`). The ₹1 locks
           when the building starts: with the first ghost ₹10. ₹32 / ₹45 lock from the start, as before. */
        if(!ghostMode) seqLocks();
        const startPrompt = ()=>{
          if(d.intro_text) $("promptText").textContent = slide.prompt_hi || "";
          sayCued("prompt", ()=>{ armed = true; touch(); if(ghostMode) seqLocks(); stepGhost(); });
        };
        /* round 4 (SME, ₹14): Swiftee's line from the earlier version plays first —
           «चलिए, दस रुपये और एक रुपये के सिक्कों से इस राशि को बनाते हैं।» — then the existing flow */
        if(A(slide, "intro")){
          if(d.intro_text) $("promptText").textContent = d.intro_text;
          sayCued("intro", startPrompt);
        } else startPrompt();
      }
    }
  };

  /* ================================================================ MONEY_DONE (p18) */
  /* round 2d (user mockup): celebrating Pari + Pari's list again (the p8 rows), every row green with a
     tick — rows arrive one by one, each tick pops as its row lands. Entrance = transitions (see the
     p8 note on why not keyframes). */
  SlideModules.MONEY_DONE = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      warmShop();                                  /* round 2t: the shop's pictures, decoded before it opens */
      const d = slide.data;
      /* "mn-fin", NOT "mn-done": .mn-done is the build screens' solved-target state, and sharing the
         name collapsed every solved drop zone to 8 px */
      const root = el("div", "mn-fin");
      if(d.pari_img) root.appendChild(el("img", "mn-fin-pari mn-pop")).src = img(d.pari_img);
      const list = el("div", "mn-list mn-fin-list");
      const STEP = 380, T0 = 450;
      d.items.forEach((it, i)=>{
        const r = el("div", "mn-li mn-li-ok mn-li-wait",
          '<span class="mn-li-ic"><img src="' + img(it.img) + '" alt="" draggable="false"></span>' +
          '<span class="mn-li-n">' + it.name + '</span>' +
          '<span class="mn-li-p"><span>₹' + it.price + '</span></span>' +
          '<span class="mn-li-tick"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M5 12.5l4.3 4.3L19 7.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span>');
        list.appendChild(r);
        setTimeout(()=>{ if(!r.isConnected) return; r.classList.remove("mn-li-wait"); sfxPop(); }, T0 + i * STEP);
      });
      root.appendChild(list);
      host.appendChild(root);
      setTimeout(()=>{ if(typeof confettiCannon === "function" && root.isConnected) confettiCannon(); }, T0 + d.items.length * STEP);
      mood("celebrate");
      state.replayAudio = ()=> say(A(slide, "prompt"));
      say(A(slide, "prompt"), ()=> setNavActive(true));
    }
  };

  /* ================================================================ SHOP_GAME (S17–S21) */
  /* The mastery shop. One slide, a small state machine:
       choose  — the stall; all unbought items active, priced, idling; 5–6 s idle -> one glows + VO
       select  — the tapped item shines, the rest dull, it comes to the centre with its price large
       make    — ₹10 note / ₹10 coin / ₹1 coin, tap OR drag; tap placed money to return it; Undo;
                 जाँचें inactive until one piece is placed. NO running total (S11 note).
       check   — less / more: shake, soft error, everything goes back, attempt +1. After the THIRD
                 wrong the backend caps (tens ≤ tens-part, ones ≤ ones-part, note+coin counted together)
                 switch on, silently. Exact: green glow, sound, sequenced highlight; the FIRST purchase
                 gets the decomposition line built from the currency actually used, later ones a short
                 playful line.
       basket  — the item jumps, flies to Pari's basket, the counter ticks, the item goes inactive.
     After all items: Pari with a full basket, the ticked list, the total. */
  /* round 2t (SME): "the vegetable/food item icons sometimes disappear while moving into or playing
     the game". The stall is rebuilt on every return from a purchase (and the make screen / list on
     every step), so each visit creates FRESH <img>s. The loader downloaded and decoded these files
     once, but a browser may drop decoded pictures it no longer holds — then every new <img> waits
     for a re-decode (and on a busy tablet, a reload from cache) before it paints: a cell, its price
     and its tick appear with no picture. Measured in Chrome at 4-6x CPU throttle: up to ~0.4 s blank.
     Two fixes: (a) from the screen before the shop until the celebration, the shop's pictures are
     HELD decoded (Image objects kept referenced); (b) every shop <img> paints with decoding="sync",
     so a cell is never shown before its picture — the picture is drawn in the same frame. */
  let _shopKeep = null;
  function warmShop(){
    if(_shopKeep) return;
    try {
      const S = CARD && CARD.slides && CARD.slides.find(s => s.type === "SHOP_GAME"); if(!S) return;
      const d = S.data || {};
      const keys = (d.items || []).map(it => it.img).concat([d.pari_img, d.pari_full_img, d.stall_img]).filter(Boolean)
        /* the notes / coins too, in all three states (Default / Glow / Lock) */
        .concat(...Object.keys(KIND).map(kd => ["", "_glow", "_lock"].map(sfx => KIND[kd].img + sfx)));
      _shopKeep = keys.map(k0 => { const im = new Image(); im.decoding = "sync"; im.src = img(k0);
                                   if(im.decode) im.decode().catch(()=>{}); return im; });
    } catch(e){}
  }
  function releaseShop(){ _shopKeep = null; }
  const syncImgs = (node)=>{ try { node.querySelectorAll("img").forEach(i => { i.decoding = "sync"; }); } catch(e){} };

  SlideModules.SHOP_GAME = {
    /* round 2f (user, 2026-09-30):
         stall  — the team's 6-panel stall art; one item per panel, prices ascending. No basket counter:
                  a bought item turns green with a tick and is disabled, which already says it.
         make   — the page-6 build layout reused: item card (picture + price tag) left, drop zone right
                  (no running total), coin tray below with ₹10 note · ₹10 coin · ₹1 coin, and «जाँचें»
                  where the arrow button sits. No Undo button: a placed piece goes back by dragging it
                  out of the drop zone (or tapping it). */
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data, items = d.items;
      warmShop();                                  /* round 2t: no-op if P4 already warmed them */
      $("navBtn").style.display = "none";
      const bought = new Set();
      let first = true, busy = false, view = null, idleT = 0, justSold = -1;
      let tipped = false;          /* round 2g: the drag-back tip is spoken ONCE per game */
      const root = el("div", "sg-root");
      host.appendChild(root);
      const band = (t)=>{ $("promptText").textContent = t; };
      /* panel rectangles of shop_stall.png, as % of the cropped image (measured off the art) */
      const PANELS = [[9.89,31.18],[37.86,31.18],[65.55,31.18],[9.89,62.06],[37.86,62.06],[65.55,62.06]];
      const PW = 25.0, PH = 26.3;

      /* ---------- choose ---------- */
      function showChoose(speak){
        clearTimeout(idleT);
        if(view) view.remove();
        document.body.classList.remove("spk-done");               /* round 20: the stall is a new question */
        band(d.text.choose);
        const v = el("div", "sg-choose");
        v.innerHTML = '<img class="sg-pari" src="' + img(d.pari_img) + '" alt="">';
        const stall = el("div", "sg-stall2");
        stall.style.backgroundImage = 'url("' + img(d.stall_img) + '")';
        const cells = items.map((it, i)=>{
          const c = el("div", "sg-cell2" + (bought.has(i) ? " sg-sold" : "") + (i === justSold ? " sg-justsold" : ""),
            '<img src="' + img(it.img) + '" alt="' + it.name + '" draggable="false"><div class="sg-price">₹' + it.price + '</div>' +
            '<span class="sg-tick"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M5 12.5l4.3 4.3L19 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>');
          const p = PANELS[i];
          c.style.left = p[0] + "%"; c.style.top = p[1] + "%"; c.style.width = PW + "%"; c.style.height = PH + "%";
          c.style.animationDelay = (i % 3) * 0.4 + "s";
          /* round 2k let a tap on an item cut the voice off and open the item. Round 24 (user): "we should
             not be able to click on any object until the VO is finished" - an item takes no tap while the
             voice is busy (Swiftee's opening, the instruction, the idle reminder). */
          c.onclick = ()=>{ if(busy || bought.has(i) || voBusy()) return; pick(i, c, cells); };
          stall.appendChild(c);
          return c;
        });
        justSold = -1;
        v.appendChild(stall);
        syncImgs(v); root.appendChild(v); view = v;
        let nags = 0;
        const arm = ()=>{
          clearTimeout(idleT);
          if(nags >= 3) return;                      /* at most three reminders per visit to the stall */
          idleT = setTimeout(()=>{
            if(!v.isConnected || busy) return;
            if(isPlaying){ arm(); return; }
            nags++;
            const free = cells.filter((c, i)=> !bought.has(i));
            const c = free[Math.floor(Math.random() * free.length)];
            /* round 2p: NOT "sg-glow" — the engine owns .sg-glow (a full-screen landing layer with
               pointer-events:none / display:none), so a glowed item stopped taking taps for good */
            if(c){ restart(c, "sg-hilite"); setTimeout(()=> c.classList.remove("sg-hilite"), 3200); sfxNudge(); }
            say(A(slide, "idle"), arm);
          }, d.idle_ms || 5500);
        };
        v.addEventListener("pointerdown", arm, true);
        state.replayAudio = ()=> say(A(slide, "prompt"), arm);
        /* round 3 (SME): Swiftee opens the game on the stall — «परी पहुँच गई है बाज़ार। आओ, चलो खरीदारी
           शुरू करें।» — then the instruction; each line's text shows as it is spoken */
        if(speak && A(slide, "intro")){
          if(d.text.intro) band(d.text.intro);
          say(A(slide, "intro"), ()=>{ band(d.text.choose); say(A(slide, "prompt"), arm); });
        }
        else if(speak) say(A(slide, "prompt"), arm); else arm();
      }

      function pick(i, c, cells){
        busy = true; clearTimeout(idleT);
        if(typeof sfxTap === "function") sfxTap(); else sfxPop();
        cells.forEach(x => x.classList.toggle("sg-dull", x !== c));
        c.classList.add("sg-shine");
        setTimeout(()=> showMake(i), 650);
      }

      /* ---------- make ---------- */
      function showMake(i){
        const it = items[i], T = it.price, TP = Math.floor(T / 10), OP = T % 10;
        if(view) view.remove();
        band(d.text.make.replace("{T}", T));
        const v = el("div", "mn-build sg-make2");
        const card = el("div", "mn-item mn-pop", '<img class="mn-item-img" src="' + img(it.img) + '" alt="' + it.name + '">' +
                                               '<div class="mn-tag"><span>₹' + T + '</span></div>');
        const amt = el("div", "mn-target");
        const tray = makeTray(); amt.appendChild(tray);
        const top = el("div", "mn-top"); top.append(card, amt);
        const bottom = el("div", "mn-bottom");
        const bank = el("div", "mn-bank");
        const srcs = {};
        ["n10", "c10", "c1"].forEach(kd => { const s = piece(kd, "mn-src"); srcs[kd] = s; bank.appendChild(s); });
        bottom.appendChild(bank);
        v.append(top, bottom);
        syncImgs(v); root.appendChild(v); view = v;
        /* «जाँचें» takes the arrow button's place (same pill, same spot) */
        const chk = el("button", "sg-checkpill", d.text.check);
        /* sits next to the arrow button (same container, same spot); taken away with the screen */
        const nav = $("navBtn");
        (nav && nav.parentElement ? nav.parentElement : host).appendChild(chk);
        const reap = setInterval(()=>{ if(!view || !view.isConnected || !root.isConnected){ chk.remove(); clearInterval(reap); } }, 300);
        restart(card.querySelector(".mn-tag"), "mn-pulse");

        let attempts = 0, caps = false, working = false, solved = false, tipping = false;
        let wrongRun = 0;            /* round 3: wrong checks since the last reset (1, 2 keep the money; 3 resets) */
        const placed = [];   /* {kind, el} in placement order */
        const tens = ()=> placed.filter(p => KIND[p.kind].v === 10).length;
        const ones = ()=> placed.filter(p => KIND[p.kind].v === 1).length;
        const sum  = ()=> tens() * 10 + ones();
        const refresh = ()=>{
          chk.disabled = !placed.length || solved;
          const tOff = caps && tens() >= TP, oOff = caps && ones() >= OP;
          srcs.n10.classList.toggle("mn-off", tOff); srcs.c10.classList.toggle("mn-off", tOff);
          srcs.c1.classList.toggle("mn-off", oOff);
          Object.keys(srcs).forEach(kd => syncArt(srcs[kd]));
        };
        const allowed = (kind)=>{
          const v10 = KIND[kind].v === 10;
          if(caps && (v10 ? tens() >= TP : ones() >= OP)) return false;
          if(v10 ? tens() >= 9 : ones() >= 9) return false;          /* the tray's physical room */
          return true;
        };
        const giveBack = (rec, fromFloat, withSound)=>{
          const i2 = placed.indexOf(rec); if(i2 < 0 || !rec.el) return;
          placed.splice(i2, 1);
          const f = fromFloat || floatAt(rec.kind, box(rec.el));
          rec.el.remove();
          const b = bounceBack(f, srcs[rec.kind]);
          /* round 16 (checklist: "SFX for every interaction"): money the child drags back out lands home
             with its own drop sound (note / coin); the 3rd-check reset stays quiet (it has the wrong sound) */
          if(withSound) b.then(()=> sfxDrop(rec.kind));
          refresh();
        };
        /* a placed piece: drag it OUT of the drop zone to give it back (tap also gives it back) */
        const armPlaced = (rec)=>{
          const p = rec.el;
          p.style.touchAction = "none"; p.style.cursor = "grab";
          p.addEventListener("pointerdown", (e)=>{
            if(working || solved || tipping || voBusy() || e.button > 0) return;   /* round 24 */
            e.preventDefault(); e.stopPropagation();
            const p0 = { x:e.clientX, y:e.clientY }, b0 = box(p), s0 = toStage(e.clientX, e.clientY);
            let f = null, moved = false;
            const mv = (ev)=>{
              if(!moved && Math.hypot(ev.clientX - p0.x, ev.clientY - p0.y) > 7){
                moved = true; f = floatAt(rec.kind, b0, "mn-drag"); p.style.visibility = "hidden";
              }
              if(f){ const s = toStage(ev.clientX, ev.clientY);
                     f.style.left = (b0.x + s.x - s0.x) + "px"; f.style.top = (b0.y + s.y - s0.y) + "px"; }
            };
            const up = (ev)=>{
              document.removeEventListener("pointermove", mv);
              document.removeEventListener("pointerup", up);
              document.removeEventListener("pointercancel", up);
              /* round 21 (lead): a TAP gives it back too (it was drag-only since round 2g) - both ways, as
                 for putting money in; the same landing sound. The tip line is unchanged. */
              if(!moved){ if(ev.type !== "pointercancel") giveBack(rec, null, true); return; }
              if(ev.type !== "pointercancel" && inside(amt, ev.clientX, ev.clientY)){
                /* dropped back inside: snap home */
                animTo(f, box(p), 220, "ease-out").then(()=>{ f.remove(); p.style.visibility = ""; });
              } else giveBack(rec, f, true);
            };
            document.addEventListener("pointermove", mv);
            document.addEventListener("pointerup", up);
            document.addEventListener("pointercancel", up);
          });
        };
        const put = (kind, f)=>{
          const rec = { kind, el:null };
          placed.push(rec);
          sfxDrop(kind);
          addPlaced(tray, kind, f).then(p => { rec.el = p; armPlaced(rec); if(!tipped) tipDragBack(p); });
          refresh();
        };
        /* round 2g/2h — the ONE-TIME TIP. There is no Undo button, so the first piece the child ever
           places in the shop shows the way back: while Swiftie says «कोई पैसा हटाना हो, तो उसे वापस नीचे
           खींच लीजिए।», a GHOST of that piece travels from the drop zone to its place in the tray — twice,
           then stops. Waits for any clip already sounding (the item's own line) so it never cuts it off.
           No hand (practice rounds). */
        const tipDragBack = (p)=>{
          tipped = true;
          const kd = p.dataset.kind;
          const ghostBack = (n)=>{
            if(n <= 0 || !p.isConnected || solved || !srcs[kd]) return;
            fly(kd, p, srcs[kd], { ghost:true, ms:1100 }).then(()=> setTimeout(()=> ghostBack(n - 1), 250));
          };
          const go = (tries)=>{
            if(!p.isConnected || solved) return;
            if((isPlaying || working) && tries < 40){ setTimeout(()=> go(tries + 1), 250); return; }
            /* round 2k: money cannot be dragged while this line is speaking */
            tipping = true; v.classList.add("sg-tipping");
            say(A(slide, "tip"), ()=>{ tipping = false; v.classList.remove("sg-tipping"); });
            setTimeout(()=> ghostBack(2), 300);
          };
          setTimeout(()=> go(0), 350);
        };
        Object.keys(srcs).forEach(kd => dragSource(srcs[kd], kd, {
          zone: ()=> amt,
          canStart: (kind)=> !working && !solved && !tipping && !voBusy() && !srcs[kind].classList.contains("mn-off"),   /* round 24 */
          /* round 14 (user): a refused piece in the shop also shakes the drop zone, as on ₹32 / ₹45 */
          onDrop: (kind, f, src)=>{ if(!allowed(kind)){ rejectPiece(f, src, amt, true); return; } put(kind, f); },
          /* round 2p: tap works too (user: "giving the user both interactions") — same rules as a drop */
          onTap: (kind, src)=>{
            if(!allowed(kind)){ rejectPiece(tapFloat(kind, src), src, amt, true); return; }   /* round 2t / 14 */
            put(kind, floatAt(kind, box(src)));
          }
        }));
        chk.onclick = ()=>{
          if(working || solved || !placed.length || voBusy()) return;   /* round 24 */
          const s = sum();
          if(s === T){ win(); return; }
          /* round 3 (SME): "the child should be able to correct the amount already placed instead of
             having the entire tray reset immediately". 1st wrong: «ओहो! रुपये ज़्यादा हैं। कुछ कम करिए।» /
             «ओहो! रुपये कम हैं। कुछ और डालिए।» — the money STAYS; 2nd: «ओहो! अभी भी …» — it stays; 3rd:
             the same line and the tray resets (every piece bounces home) so the child starts again, and
             the existing silent caps switch on (tens <= tens-part, ones <= ones-part). The count starts
             again after a reset. Idle 7 s after a wrong check -> a ghost shows the fix (below). */
          working = true; attempts++; wrongRun++;
          state.attempts++;
          const more = s > T;
          SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, item:it.id, attempts, kind: more ? "more" : "less" });
          fbWrong(); mood("tryagain");
          restart(amt, "mn-shake");                          /* round 14 (user): a wrong «जाँचें» shakes the drop zone */
          /* round 3b (user): the 3rd wrong check empties the tray, so it does not say «कुछ और डालिए / कम करिए»
             — it says «फिर से कोशिश करें।» (the money is placed again from the start) */
          const key = wrongRun >= 3 ? "retry" : (more ? "more" : "less") + (wrongRun >= 2 ? "2" : "1");
          band(d.text[key]);
          if(wrongRun >= 3){
            wrongRun = 0; caps = true;
            setTimeout(()=>{
              placed.slice().reverse().forEach((rec, j)=> setTimeout(()=> giveBack(rec), j * 70));
            }, 520);
          }
          say(A(slide, key), ()=>{
            working = false; refresh();
            band(d.text.make.replace("{T}", T));
            idleAt = Date.now(); nudges = 0;
          });
        };
        const win = ()=>{
          working = true; solved = true; refresh();
          speakerDone();                                          /* round 20 (QA BUG_07): until the stall is back */
          Object.keys(srcs).forEach(kd => { srcs[kd].classList.add("mn-off"); syncArt(srcs[kd]); });
          amt.classList.add("mn-done");
          fbCorrect(); mood("celebrate");
          if(typeof confettiCannon === "function") confettiCannon();
          placed.forEach((rec, j)=> setTimeout(()=> rec.el && rec.el.classList.add("mn-glow", "mn-seq"), 200 + j * 160));
          const n = placed.filter(p => p.kind === "n10").length, c = placed.filter(p => p.kind === "c10").length, o = ones();
          SwiftPAL.emit("shop_item_bought", { slide_id:slide.id, phase:slide.phase, item:it.id, price:T,
            value:attempts === 0, attempts:attempts + 1, notes:n, coins10:c, ones:o });
          state.masteryAttempts = (state.masteryAttempts || 0) + 1;
          if(attempts === 0) state.masteryHits = (state.masteryHits || 0) + 1;
          let line, text;
          /* round 2o: short success only — the first purchase «बहुत बढ़िया!», the rest per item */
          if(first){ line = A(slide, "first_ok") || it.vo_praise; text = d.text.first_ok || "बहुत बढ़िया!"; }
          else { line = it.vo_praise; text = it.praise; }
          first = false;
          band(text);
          say(line, ()=> backToStall(i, card, chk));
        };
        refresh();                                   /* जाँचें starts inactive — nothing placed yet */
        /* INACTIVITY NUDGE — round 3: every 7 s of inactivity (checklist), with the nudge chime, up to
           5 in a row (any touch restarts the count). What it shows follows the amount in the tray, as in
           the Game Zone: TOO MUCH -> a ghost of the last-added piece travels from the tray back to its
           place (how to take money out); TOO LITTLE / nothing yet -> a ghost of the piece still needed
           (a ₹10 while tens are missing, else a ₹1) travels in; the RIGHT amount -> «जाँचें» pulses. */
        let idleAt = Date.now(), nudges = 0;
        v.addEventListener("pointerdown", ()=>{ idleAt = Date.now(); nudges = 0; }, true);
        const nudgeT = setInterval(()=>{
          if(!v.isConnected){ clearInterval(nudgeT); return; }
          if(working || solved || tipping || isPlaying){ idleAt = Math.max(idleAt, Date.now() - 1000); return; }
          if(nudges >= 5 || Date.now() - idleAt < (d.make_idle_ms || 7000)) return;
          nudges++; idleAt = Date.now();
          const s = sum();
          if(s > T){
            const rec = placed[placed.length - 1];
            if(!rec || !rec.el || !srcs[rec.kind]) return;
            fly(rec.kind, rec.el, srcs[rec.kind], { ghost:true, ms:1100 });
            SwiftPAL.emit("hint_shown", { slide_id:slide.id, level:"idle_ghost_back", item:it.id });
          } else if(s < T){
            const kd = tens() < TP ? (nudges % 2 ? "n10" : "c10") : "c1";
            if(srcs[kd].classList.contains("mn-off")) return;
            const slot = nextSlot(tray, kd);
            restart(srcs[kd], "mn-hintglow");
            fly(kd, srcs[kd], slot, { ghost:true, ms:1100 }).then(()=> slot.remove());
            SwiftPAL.emit("hint_shown", { slide_id:slide.id, level:"idle_ghost", item:it.id });
          } else restart(chk, "mn-pulse");
          sfxNudge();
        }, 500);
        state.replayAudio = ()=> say(it.vo_select);
        /* round 2p: the first time the game opens an item, a ghost ₹10 note glides from the tray into
           the amount area twice once the item's line has finished — the drag-in, shown (as the
           drag-back is shown by the tip). One piece only, never the answer; skipped once the child acts. */
        const showDragIn = !window.__sgDragInShown;
        let acted = false;
        v.addEventListener("pointerdown", ()=>{ acted = true; }, true);
        say(it.vo_select, ()=>{
          if(!showDragIn || acted || solved) return;
          window.__sgDragInShown = true;
          const once = (n)=>{
            if(n <= 0 || acted || solved || !v.isConnected) return;
            const slot = nextSlot(tray, "n10");
            restart(srcs.n10, "mn-hintglow");
            fly("n10", srcs.n10, slot, { ghost:true, ms:1100 }).then(()=>{ slot.remove(); setTimeout(()=> once(n - 1), 300); });
          };
          setTimeout(()=> once(2), 250);
          idleAt = Date.now();
        });
      }

      function detailText(n, c, o, T){
        const parts = [];
        if(n) parts.push("₹10 " + (n === 1 ? "का" : "के") + " " + n + " नोट");
        if(c) parts.push("₹10 " + (c === 1 ? "का" : "के") + " " + c + " " + (c === 1 ? "सिक्का" : "सिक्के"));
        if(o) parts.push("₹1 " + (o === 1 ? "का" : "के") + " " + o + " " + (o === 1 ? "सिक्का" : "सिक्के"));
        const joined = parts.length > 1 ? parts.slice(0, -1).join(", ") + " और " + parts[parts.length - 1] : parts[0];
        return d.text.detail_tpl.replace("{parts}", joined).replace("{T}", T);
      }

      /* the bought item jumps, then the stall comes back with that panel green + ticked */
      function backToStall(i, card, chk){
        restart(card, "sg-jump");
        setTimeout(()=>{
          sfxPop();
          chk.remove();
          bought.add(i); justSold = i;
          busy = false;
          if(bought.size >= items.length) showComplete();
          else showChoose(false);
        }, 700);
      }

      /* ---------- complete ---------- */
      function showComplete(){
        clearTimeout(idleT);
        if(view) view.remove();
        band(d.text.done);
        /* round 2p (user): only the list — the same card as page 12 (rows: picture · name · price · ✓,
           green, arriving one by one), beside Pari with her full basket. No total, no extra card. */
        const v = el("div", "mn-fin sg-complete");
        v.innerHTML = '<img class="mn-fin-pari mn-pop" src="' + img(d.pari_full_img) + '" alt="">';
        const list = el("div", "mn-list mn-fin-list");
        items.forEach((it, j)=>{
          const r = el("div", "mn-li mn-li-ok mn-li-wait",
            '<span class="mn-li-ic"><img src="' + img(it.img) + '" alt="" draggable="false"></span>' +
            '<span class="mn-li-n">' + it.name + '</span>' +
            '<span class="mn-li-p"><span>₹' + it.price + '</span></span>' +
            '<span class="mn-li-tick"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M5 12.5l4.3 4.3L19 7.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span>');
          list.appendChild(r);
          setTimeout(()=>{ if(!r.isConnected) return; r.classList.remove("mn-li-wait"); sfxPop(); }, 450 + j * 380);
        });
        v.append(list);
        syncImgs(v); root.appendChild(v); view = v;
        if(typeof confettiCannon === "function") confettiCannon();
        mood("celebrate");
        $("navBtn").style.display = "";
        speakerDone();                                            /* round 20 (QA BUG_07): the game is solved */
        say(A(slide, "done"), ()=>{
          setNavActive(true);
          $("navBtn").onclick = ()=> completeSlide(true);
        });
      }

      /* round 3b (user): the dev menu's «दुकान का खेल» sub-entries (dev only) — open one item's amount
         screen directly (the items before it bought), the stall with five bought, or the final list */
      const dv = window.__shopDev; window.__shopDev = null;
      if(dv){
        for(let k = 0; k < Math.min(dv.bought || 0, items.length); k++) bought.add(k);
        if(bought.size) first = false;
      }
      if(dv && dv.done) showComplete();
      else if(dv && dv.open != null){ showMake(dv.open); }
      else showChoose(!(dv && dv.bought));
    }
  };
})();
