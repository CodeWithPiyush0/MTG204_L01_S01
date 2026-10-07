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

  /* ---------------------------------------------------------------- engine wraps (this card only) */
  try { autoAdvances = function(){ return false; }; } catch(e){}
  try {
    const _arm = armIdleVo;
    armIdleVo = function(){
      const s = CARD && CARD.slides && CARD.slides[state.idx];
      if(s && s.data && s.data.no_engine_idle){ if(typeof stopIdleVo === "function") stopIdleVo(); return; }
      return _arm.apply(this, arguments);
    };
  } catch(e){}
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
  const mood = (m)=>{ if(typeof setSwMood === "function") setSwMood(m); };

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
    d.innerHTML = '<img src="' + img(KIND[kind].img) + '" alt="' + KIND[kind].label + '" draggable="false">';
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
      an.onfinish = ()=> res();
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
  function bounceBack(f, src){
    if(!f) return Promise.resolve();
    return animTo(f, box(src), 440, "cubic-bezier(.3,1.35,.5,1)").then(()=>{ f.remove(); restart(src, "mn-bump"); });
  }

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
      const item = el("div", "mn-item", '<img class="mn-item-img" src="' + img(d.item_img) + '" alt="' + (d.item_name || "") + '">' +
                                       '<div class="mn-tag"><span>₹' + T + '</span></div>');
      const tcol = el("div", "mn-tcol");
      const tgt = el("div", "mn-target");
      const tray = makeTray();
      const tot = el("div", "mn-total", 'कुल <b>₹0</b>');
      tgt.appendChild(tray);
      if(d.total_below){ tcol.append(tgt, tot); } else { tgt.appendChild(tot); tcol.appendChild(tgt); }
      const top = el("div", "mn-top"); top.append(item, tcol);
      const bottom = el("div", "mn-bottom");
      const bank = el("div", "mn-bank");
      const srcs = {};
      (d.sources || []).forEach(kd => { const s = piece(kd, "mn-src"); srcs[kd] = s; bank.appendChild(s); });
      bottom.appendChild(bank);
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
      const idleTick = ()=>{
        if(!root.isConnected){ clearInterval(idleTimer); return; }
        if(done || !armed || reached || isPlaying || (teach && !teachWait)){ touch(); return; }
        /* round 2o (user): the teaching reminder plays ONCE, ~10 s after the child stops — a gentle
           reminder, not a loop. Practice keeps its silent pulse -> ghost nudge, capped at 3. */
        if(Date.now() - lastAct < (teach ? 10000 : (d.idle_ms || 7000))) return;
        lastAct = Date.now();
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
      const equation = ()=>{
        const parts = [];
        for(let i = 0; i < tc; i++) parts.push("₹10");
        for(let i = 0; i < oc; i++) parts.push("₹1");
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
        state.replayAudio = ()=>{ say(A(slide, "done")); spokenHighlight(); };
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
        bounceBack(f, src);
        restart(tgt, "mn-shake");
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
        return false;
      };

      Object.keys(srcs).forEach(kd => dragSource(srcs[kd], kd, {
        zone: ()=> tgt,
        canStart: (kind)=> armed && !done && !reached && !off.has(kind) && !isPlaying,
        /* round 2p: a TAP on a note / coin works like dragging it into the tray (same rules) */
        onTap: (kind, src)=> handleDrop(kind, floatAt(kind, box(src)), src),
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
        if(done || !(tc + oc) || isPlaying) return;
        touch();
        if(total() === T){ finish(); return; }
        state.attempts++;
        fbWrong(); mood("tryagain"); restart(tgt, "mn-shake");
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
        state.replayAudio = ()=> say(A(slide, "prompt"));
        restart(item.querySelector(".mn-tag"), d.tag_fx === "glow" ? "mn-tagglow" : "mn-pulse");
        say(A(slide, "prompt"), ()=>{ armed = true; touch(); });
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
          /* round 2k: never ignore a tap on an unbought item. It used to return while ANY clip was
             playing (the idle reminder, the praise line tail), which read as "some sections are not
             clickable". The tap now stops that clip and goes straight to the item. */
          c.onclick = ()=>{ if(busy || bought.has(i)) return; if(isPlaying) stopAudio(); pick(i, c, cells); };
          stall.appendChild(c);
          return c;
        });
        justSold = -1;
        v.appendChild(stall);
        root.appendChild(v); view = v;
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
            if(c){ restart(c, "sg-hilite"); setTimeout(()=> c.classList.remove("sg-hilite"), 3200); }
            say(A(slide, "idle"), arm);
          }, d.idle_ms || 5500);
        };
        v.addEventListener("pointerdown", arm, true);
        state.replayAudio = ()=> say(A(slide, "prompt"), arm);
        if(speak) say(A(slide, "prompt"), arm); else arm();
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
        root.appendChild(v); view = v;
        /* «जाँचें» takes the arrow button's place (same pill, same spot) */
        const chk = el("button", "sg-checkpill", d.text.check);
        /* sits next to the arrow button (same container, same spot); taken away with the screen */
        const nav = $("navBtn");
        (nav && nav.parentElement ? nav.parentElement : host).appendChild(chk);
        const reap = setInterval(()=>{ if(!view || !view.isConnected || !root.isConnected){ chk.remove(); clearInterval(reap); } }, 300);
        restart(card.querySelector(".mn-tag"), "mn-pulse");

        let attempts = 0, caps = false, working = false, solved = false, tipping = false;
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
        const giveBack = (rec, fromFloat)=>{
          const i2 = placed.indexOf(rec); if(i2 < 0 || !rec.el) return;
          placed.splice(i2, 1);
          const f = fromFloat || floatAt(rec.kind, box(rec.el));
          rec.el.remove();
          bounceBack(f, srcs[rec.kind]);
          refresh();
        };
        /* a placed piece: drag it OUT of the drop zone to give it back (tap also gives it back) */
        const armPlaced = (rec)=>{
          const p = rec.el;
          p.style.touchAction = "none"; p.style.cursor = "grab";
          p.addEventListener("pointerdown", (e)=>{
            if(working || solved || tipping || e.button > 0) return;
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
              if(!moved) return;                           /* drag-only (round 2g): a tap does nothing */
              if(ev.type !== "pointercancel" && inside(amt, ev.clientX, ev.clientY)){
                /* dropped back inside: snap home */
                animTo(f, box(p), 220, "ease-out").then(()=>{ f.remove(); p.style.visibility = ""; });
              } else giveBack(rec, f);
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
          canStart: (kind)=> !working && !solved && !tipping && !srcs[kind].classList.contains("mn-off"),
          onDrop: (kind, f, src)=>{ if(!allowed(kind)){ bounceBack(f, src); restart(amt, "mn-shake"); return; } put(kind, f); },
          /* round 2p: tap works too (user: "giving the user both interactions") — same rules as a drop */
          onTap: (kind, src)=>{
            if(!allowed(kind)){ restart(src, "mn-bump"); restart(amt, "mn-shake"); return; }
            put(kind, floatAt(kind, box(src)));
          }
        }));
        chk.onclick = ()=>{
          if(working || solved || !placed.length || isPlaying) return;
          const s = sum();
          if(s === T){ win(); return; }
          working = true; attempts++;
          state.attempts++;
          SwiftPAL.emit("answer_wrong", { slide_id:slide.id, phase:slide.phase, item:it.id, attempts, kind: s < T ? "less" : "more" });
          fbWrong(); mood("tryagain"); restart(amt, "mn-shake");
          band(s < T ? d.text.less : d.text.more);
          setTimeout(()=>{
            placed.slice().reverse().forEach((rec, j)=> setTimeout(()=> giveBack(rec), j * 70));
          }, 520);
          if(attempts >= 3) caps = true;                     /* S20: silent backend support from now on */
          say(A(slide, s < T ? "less" : "more"), ()=>{
            working = false; refresh();
            band(d.text.make.replace("{T}", T));
          });
        };
        const win = ()=>{
          working = true; solved = true; refresh();
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
        /* round 2o (user): INACTIVITY NUDGE. If the child does nothing, one ghost currency glides from
           the tray into the amount area — a reminder of the drag, never the answer (one piece only: a
           ₹10 while tens are still missing, else a ₹1). First nudge after 10 s on the first item of the
           game (12 s later), then again every 15 s, at most 3 per item. Any touch restarts the clock. */
        let idleAt = Date.now(), nudges = 0;
        const firstWait = (bought.size === 0) ? 10000 : 12000;
        v.addEventListener("pointerdown", ()=>{ idleAt = Date.now(); }, true);
        const nudgeT = setInterval(()=>{
          if(!v.isConnected){ clearInterval(nudgeT); return; }
          if(working || solved || tipping || isPlaying){ idleAt = Math.max(idleAt, Date.now() - 1000); return; }
          if(nudges >= 3 || Date.now() - idleAt < (nudges === 0 ? firstWait : 15000)) return;
          nudges++; idleAt = Date.now();
          const kd = tens() < TP ? (nudges % 2 ? "n10" : "c10") : "c1";
          if(srcs[kd].classList.contains("mn-off")) return;
          const slot = nextSlot(tray, kd);
          restart(srcs[kd], "mn-hintglow");
          fly(kd, srcs[kd], slot, { ghost:true, ms:1100 }).then(()=> slot.remove());
          SwiftPAL.emit("hint_shown", { slide_id:slide.id, level:"idle_ghost", item:it.id });
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
        root.appendChild(v); view = v;
        if(typeof confettiCannon === "function") confettiCannon();
        mood("celebrate");
        $("navBtn").style.display = "";
        state.replayAudio = ()=> say(A(slide, "done"));
        say(A(slide, "done"), ()=>{
          setNavActive(true);
          $("navBtn").onclick = ()=> completeSlide(true);
        });
      }

      showChoose(true);
    }
  };
})();
