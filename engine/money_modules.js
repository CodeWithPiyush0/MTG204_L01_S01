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
  const sfxDrop   = (n)=> tone([560 + (n || 0) * 26, 840 + (n || 0) * 26], "sine", 0.13, 0.07);
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
            fb.textContent = d.correct_text || ""; fb.classList.add("show", "ok");
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

      const root = el("div", "mn-build" + (d.total_below ? " mn-total-below" : ""));
      const item = el("div", "mn-item", (d.item_name ? '<div class="mn-item-name">' + d.item_name + '</div>' : "") +
                                       '<img class="mn-item-img" src="' + img(d.item_img) + '" alt="">' +
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
      const pulse = (kd)=>{ if(srcs[kd]) restart(srcs[kd], "mn-pulse"); };

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
        if(Date.now() - lastAct < (d.idle_ms || 7000)) return;
        lastAct = Date.now(); idleN++;
        if(teach){
          if(!teachWait) return;
          const lines = teachWait.idle || [];
          pulse(teachWait.kind);
          if(lines.length) say(lines[Math.min(idleN - 1, lines.length - 1)]);
        } else {
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
        item.classList.add("mn-bought");
        fbCorrect(); mood("celebrate");
        if(typeof confettiCannon === "function") confettiCannon();
        const clean = wrongN.tens + wrongN.ones === 0;
        SwiftPAL.emit("money_build_done", { slide_id:slide.id, phase:slide.phase, value:clean, target:T,
          tens:tc, ones:oc, wrong_tens:wrongN.tens, wrong_ones:wrongN.ones, latency_ms:Date.now() - state.slideStart });
        state.replayAudio = ()=> say(A(slide, "done"));
        say(A(slide, "done"), ()=>{
          setNavActive(true);
          $("navBtn").onclick = ()=> completeSlide(clean);
        });
      };
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
        sfxDrop(n); mood("happy");
        addPlaced(tray, kind, f);
        setTotal(); touch(); idleN = 0;
        Object.keys(srcs).forEach(kd => srcs[kd].classList.remove("mn-pulse"));
        if(total() === T){ onReached(); return true; }
        return false;
      };

      Object.keys(srcs).forEach(kd => dragSource(srcs[kd], kd, {
        zone: ()=> tgt,
        canStart: (kind)=> armed && !done && !reached && !off.has(kind) && !isPlaying,
        onDrop: (kind, f, src)=>{
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
            srcs[w.kind] && srcs[w.kind].classList.remove("mn-pulse");
            if(!hit) setTimeout(runStep, 250);
          }
        }
      }));

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
          addPlaced(tray, kind, null); sfxDrop(tc + oc); setTotal();
          res();
        });
      });
      function runStep(){
        if(done || si >= steps.length) return;
        const s = steps[si++];
        curLine = s.say;
        if(s.show_prompt) $("promptText").textContent = slide.prompt_hi || "";
        if(s.pulse_total) setTimeout(()=> restart(tot, "mn-pulse"), 400);
        let voDone = false, moveDone = !s.auto;
        const next = ()=>{
          if(!voDone || !moveDone) return;
          if(s.child){
            teachWait = { kind:s.child, idle:s.idle || [] };
            armed = true; touch(); idleN = 0;
            pulse(s.child);
          } else runStep();
        };
        if(s.auto) setTimeout(()=> autoPlace(s.auto).then(()=>{ moveDone = true; next(); }), s.auto_delay || 900);
        if(s.child) pulse(s.child);
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
  SlideModules.MONEY_DONE = {
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data;
      const root = el("div", "mn-done-card");
      const grid = el("div", "mn-done-grid");
      d.items.forEach((nm, i)=>{
        const r = el("div", "mn-done-i", '<span class="mn-tick">✓</span><span>' + nm + '</span>');
        r.querySelector(".mn-tick").style.animationDelay = (500 + i * 380) + "ms";
        grid.appendChild(r);
        setTimeout(sfxPop, 500 + i * 380);
      });
      root.append(grid, el("div", "mn-done-count", d.items.length + " / " + d.items.length));
      host.appendChild(root);
      setTimeout(()=>{ if(typeof confettiCannon === "function" && root.isConnected) confettiCannon(); }, 500 + d.items.length * 380);
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
    mount(host, slide){
      epoch(); state.ownsAudio = true; setNavActive(false);
      const d = slide.data, items = d.items;
      $("navBtn").style.display = "none";
      const bought = new Set();
      let first = true, busy = false, view = null, idleT = 0;
      const root = el("div", "sg-root");
      const counter = el("div", "sg-counter", '<span class="sg-basket-ic"></span><b>0/' + items.length + '</b>');
      root.appendChild(counter);
      host.appendChild(root);
      const band = (t)=>{ $("promptText").textContent = t; };
      const setCount = ()=>{ counter.querySelector("b").textContent = bought.size + "/" + items.length; restart(counter, "mn-bump"); };

      /* ---------- choose ---------- */
      function showChoose(speak){
        clearTimeout(idleT);
        if(view) view.remove();
        band(d.text.choose);
        const v = el("div", "sg-choose");
        v.innerHTML = '<img class="sg-pari" src="' + img(d.pari_img) + '" alt="">';
        const stall = el("div", "sg-stall", '<div class="sg-awning"></div>');
        const shelves = el("div", "sg-shelves");
        const cells = items.map((it, i)=>{
          const c = el("div", "sg-cell" + (bought.has(i) ? " sg-sold" : ""),
            '<img src="' + img(it.img) + '" alt="' + it.name + '" draggable="false"><div class="sg-price">₹' + it.price + '</div>');
          c.style.animationDelay = (i % 4) * 0.35 + "s";
          c.onclick = ()=>{ if(busy || bought.has(i) || isPlaying) return; pick(i, c, cells); };
          shelves.appendChild(c);
          return c;
        });
        stall.appendChild(shelves); v.appendChild(stall);
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
            if(c) restart(c, "sg-glow");
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
        const v = el("div", "sg-make");
        const pari = el("img", "sg-pari-sm"); pari.src = img(d.pari_img); pari.alt = "";
        const card = el("div", "sg-item-big mn-pop", '<img src="' + img(it.img) + '" alt=""><div class="sg-price-big">₹' + T + '</div>');
        const amt = el("div", "sg-amount mn-target");
        const tray = makeTray(); amt.appendChild(tray);
        const bank = el("div", "sg-bank");
        const srcs = {};
        ["n10", "c10", "c1"].forEach(kd => {
          const w = el("div", "sg-src-w");
          const s = piece(kd, "mn-src"); srcs[kd] = s;
          w.append(s, el("div", "sg-src-l", KIND[kd].label));
          bank.appendChild(w);
        });
        const undo = el("button", "sg-undo", '<svg viewBox="0 0 48 48" width="34" height="34"><path d="M18 12 8 22l10 10" fill="none" stroke="#0B3D8C" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 22h19a11 11 0 0 1 0 22h-6" fill="none" stroke="#0B3D8C" stroke-width="5" stroke-linecap="round"/></svg>');
        undo.setAttribute("aria-label", "Undo");
        const chk = el("button", "sg-check", d.text.check);
        const btns = el("div", "sg-btns"); btns.append(undo, chk);
        const low = el("div", "sg-low"); low.append(bank, btns);
        v.append(pari, card, amt, low);
        root.appendChild(v); view = v;

        let attempts = 0, caps = false, working = false, solved = false;
        const placed = [];   /* {kind, el} in placement order */
        const tens = ()=> placed.filter(p => KIND[p.kind].v === 10).length;
        const ones = ()=> placed.filter(p => KIND[p.kind].v === 1).length;
        const sum  = ()=> tens() * 10 + ones();
        const refresh = ()=>{
          chk.disabled = !placed.length || solved;
          undo.disabled = !placed.length || solved;
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
        const put = (kind, f)=>{
          const rec = { kind, el:null };
          placed.push(rec);
          sfxDrop(placed.length);
          addPlaced(tray, kind, f).then(p => {
            rec.el = p;
            p.onclick = ()=>{ if(working || solved) return; giveBack(rec); };
          });
          refresh();
        };
        const giveBack = (rec)=>{
          const i2 = placed.indexOf(rec); if(i2 < 0 || !rec.el) return;
          placed.splice(i2, 1);
          const b = box(rec.el); rec.el.remove();
          const f = floatAt(rec.kind, b);
          bounceBack(f, srcs[rec.kind]);
          refresh();
        };
        Object.keys(srcs).forEach(kd => dragSource(srcs[kd], kd, {
          zone: ()=> amt,
          canStart: (kind)=> !working && !solved && !srcs[kind].classList.contains("mn-off"),
          onDrop: (kind, f, src)=>{ if(!allowed(kind)){ bounceBack(f, src); return; } put(kind, f); },
          onTap: (kind, src)=>{
            if(working || solved || src.classList.contains("mn-off")) return;
            if(!allowed(kind)){ restart(src, "mn-bump"); return; }
            const f = floatAt(kind, box(src));
            put(kind, f);
          }
        }));
        undo.onclick = ()=>{ if(working || solved || !placed.length) return; giveBack(placed[placed.length - 1]); };
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
          if(first){ line = ((d.detail || {})[String(T)] || {})[n + "," + c]; text = detailText(n, c, o, T); }
          else { line = it.vo_praise; text = it.praise; }
          first = false;
          band(text);
          say(line, ()=> toBasket(i, card, pari));
        };
        refresh();                                   /* जाँचें / undo start inactive — nothing placed yet */
        state.replayAudio = ()=> say(it.vo_select);
        say(it.vo_select);
      }

      function detailText(n, c, o, T){
        const parts = [];
        if(n) parts.push("₹10 " + (n === 1 ? "का" : "के") + " " + n + " नोट");
        if(c) parts.push("₹10 " + (c === 1 ? "का" : "के") + " " + c + " " + (c === 1 ? "सिक्का" : "सिक्के"));
        if(o) parts.push("₹1 " + (o === 1 ? "का" : "के") + " " + o + " " + (o === 1 ? "सिक्का" : "सिक्के"));
        const joined = parts.length > 1 ? parts.slice(0, -1).join(", ") + " और " + parts[parts.length - 1] : parts[0];
        return d.text.detail_tpl.replace("{parts}", joined).replace("{T}", T);
      }

      function toBasket(i, card, pari){
        restart(card, "sg-jump");
        setTimeout(()=>{
          const img0 = card.querySelector("img");
          const b0 = box(img0), bp = box(pari);
          const f = el("img", "mn-float sg-flyitem"); f.src = img0.src;
          f.style.left = b0.x + "px"; f.style.top = b0.y + "px"; f.style.width = b0.w + "px"; f.style.height = b0.h + "px";
          stageEl().appendChild(f);
          img0.style.visibility = "hidden";
          animTo(f, { x:bp.x + bp.w * 0.28, y:bp.y + bp.h * 0.52, w:bp.w * 0.34, h:bp.w * 0.34 }, 700).then(()=>{
            f.remove(); sfxPop();
            bought.add(i); setCount();
            busy = false;
            if(bought.size >= items.length) showComplete();
            else setTimeout(()=> showChoose(false), 350);
          });
        }, 520);
      }

      /* ---------- complete ---------- */
      function showComplete(){
        clearTimeout(idleT);
        if(view) view.remove();
        band(d.text.done);
        const v = el("div", "sg-complete");
        v.innerHTML = '<img class="sg-pari-full mn-pop" src="' + img(d.pari_full_img) + '" alt="">';
        const list = el("div", "sg-list", '<div class="sg-list-h">' + d.text.list_title + '</div>');
        items.forEach((it, j)=>{
          const r = el("div", "sg-list-r", '<img src="' + img(it.img) + '" alt=""><span class="sg-ln">' + it.name +
            '</span><span class="sg-lp">₹' + it.price + '</span><span class="mn-tick">✓</span>');
          r.querySelector(".mn-tick").style.animationDelay = (300 + j * 180) + "ms";
          list.appendChild(r);
        });
        const sumAll = items.reduce((a, it)=> a + it.price, 0);
        const side = el("div", "sg-side",
          '<div class="sg-till"><div class="sg-till-l">' + d.text.total + '</div><div class="sg-till-v">₹' + sumAll + '</div></div>' +
          '<div class="sg-great"><span class="mn-tick">✓</span><span>' + d.text.great + '</span></div>');
        v.append(list, side);
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
