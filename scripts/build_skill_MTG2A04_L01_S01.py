# -*- coding: utf-8 -*-
"""Build MTG2A04_L01_S01 — «परी की पिकनिक की खरीदारी» (Grade 2 Maths · Money: ₹10 and ₹1).

Round 2 — built to the SME deck `MTG2A04_L01_S01_review.pptx` (22 pages). The row-by-row contract is
`../CHANGES.md`; decisions D1–D8 there were taken with the user before this was written.

Visual baseline: the user's HI02H11_L02_S02 lesson. Its pinned engine (with its train modules) is
copied to engine/lesson_template.html and this game's money modules are injected on top by
engine/inject_money.py. Only the CONTENT differs from that lesson.

TEXT RULES
  * Shown text is the deck's wording (with ₹ and digits). The spoken text is the SAME sentence with
    every «₹N» read out as «<N in words> रुपये» (the deck's own spoken form — «चौदह रुपये बनाइए») and
    an em-dash turned into a comma (the TTS model truncates a clip at «— short-word»; see the
    reference lesson's README).
  * Register: kept EXACTLY as the deck wrote it (decision D4) — the आप/तुम mix is flagged, not fixed.

Run (from the game folder):   PYTHONUTF8=1 python scripts/build_skill_MTG2A04_L01_S01.py
Then:   voice-over  -> PYTHONUTF8=1 python <skill>/scripts/gen_tts.py card.json --voice Leda --ext ogg
        and re-run this builder (it measures the clips for timing).
"""
import os, re, sys, json, hashlib, subprocess

CODE = "MTG2A04_L01_S01"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE = os.path.join(ROOT, "engine", "lesson_template.html")
AUD = os.path.join(ROOT, "assets", "Audio")
IMG = os.path.join(ROOT, "assets", "Images")
CARD_TAG = re.compile(r'(<script type="application/json" id="cardData">)(.*?)(</script>)', re.S)
VER_RE = re.compile(r'ENGINE_VERSION\s*=\s*["\']([^"\']+)["\']')
MODULES = ["MONEY_INTRO", "MONEY_SORT", "MONEY_BUILD", "SHOP_GAME", "CELEBRATION"]
# round 3: vo_pt_tutorial is RE-RECORDED (registered below) for the checklist's «चलिए, शुरू करते हैं।»
COPY_AUDIO = ["vo_pt_guided", "vo_pt_practice", "sfx_celebrate", "sfx_correct", "sfx_wrong",
              "sfx_tap", "sfx_pop", "sfx_fb_correct", "sfx_fb_incorrect",
              "sfx_play_button", "sfx_next_button",      # round 2k: the team's button sounds
              "sfx_drop_coin", "sfx_drop_note",          # round 2o: the team's coin / note drop sounds
              "sfx_confetti", "sfx_nudge"]               # round 3: the team's Standard SFX pack (checklist)

NUM = ("शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह सोलह सत्रह अठारह उन्नीस "
       "बीस इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस अट्ठाईस उनतीस तीस इकतीस बत्तीस तैंतीस चौंतीस "
       "पैंतीस छत्तीस सैंतीस अड़तीस उनतालीस चालीस इकतालीस बयालीस तैंतालीस चौवालीस पैंतालीस छियालीस "
       "सैंतालीस अड़तालीस उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ साठ "
       "इकसठ बासठ तिरसठ चौंसठ पैंसठ छियासठ सड़सठ अड़सठ उनहत्तर सत्तर").split()
assert len(NUM) == 71 and NUM[65] == "पैंसठ" and NUM[42] == "बयालीस"

def spoken(t):
    t = re.sub(r"₹(\d+)", lambda m: NUM[int(m.group(1))] + " रुपये", t)
    return t.replace(" — ", ", ").replace("—", ", ")

AUDIO = {}          # id -> spoken text
SHOWN = {}          # id -> shown text (for the VO list / review)
_BY_TEXT = {}       # spoken text -> id  (one clip per distinct line)
def vo(id_, shown):
    sp = spoken(shown)
    if sp in _BY_TEXT:
        return _BY_TEXT[sp]
    assert id_ not in AUDIO, id_
    AUDIO[id_] = sp; SHOWN[id_] = shown; _BY_TEXT[sp] = id_
    return id_

# ============================================================== content
LANDING = vo("vo_landing", "नमस्ते दोस्त! मैं हूँ स्विफ्टी। परी के स्कूल में पिकनिक होने वाली है। उसे पिकनिक के लिए कुछ सामान खरीदना है। चलिए, उसकी मदद करते हैं!")

# round 3 (checklist): the transitions' on-screen titles, exactly as the checklist words them. The
# tutorial line is re-recorded so Swiftee SAYS that title; the guided / practice clips already end in
# «चलिए, साथ में करें» / «अब आपकी बारी».
GATE_TITLES = {"tutorial": "चलिए, शुरू करते हैं।", "guided": "चलिए, साथ में करें।",
               "practice": "अब आपकी बारी।", "independent": "अब आपकी बारी।"}
PT_TUTORIAL = vo("vo_pt_tutorial", "ध्यान से देखिए और मेरे साथ जानिए। चलिए, शुरू करते हैं।")

def s_intro():
    """round 3 (SME): the teaching screen — the ₹10 note, then the ₹1 coin, each with its label above
    it, appearing as its line is spoken. No heading. VO drafted here; the SME will revise it."""
    return {"id": "T1", "phase": "tutorial", "eis": "iconic", "type": "MONEY_INTRO",
            "prompt_hi": "",
            "audio": {"prompt": vo("vo_t1_note", "यह ₹10 का नोट है।")},
            "data": {"no_heading": True,
                     "items": [{"img": "cur_note10", "label": "₹10", "note": True, "say": "vo_t1_note"},
                               {"img": "cur_coin1", "label": "₹1", "say": vo("vo_t1_coin", "और यह ₹1 का सिक्का है।")}]}}

# sorting pieces — the Game-Zone currency set (front views); value decides right / wrong
P = {"n10": {"img": "cur_note10", "value": 10, "note": True}, "c10": {"img": "cur_coin10", "value": 10},
     "n20": {"img": "cur_note20", "value": 20, "note": True}, "n50": {"img": "cur_note50", "value": 50, "note": True},
     "c1": {"img": "cur_coin1", "value": 1}, "c2": {"img": "cur_coin2", "value": 2},
     "c5": {"img": "cur_coin5", "value": 5}, "c20": {"img": "cur_coin20", "value": 20}}
SORT_DONE = vo("vo_sort_done", "शाबाश!")

def s_sort(id_, target, kinds, shown):
    return {"id": id_, "phase": "guided", "eis": "iconic", "type": "MONEY_SORT",
            "prompt_hi": shown,
            "audio": {"prompt": vo("vo_%s_prompt" % id_.lower(), shown), "done": SORT_DONE},
            # round 5 (user mockup): wooden table, open coin purse in two layers, balanced slots
            "data": {"target": target, "wallet_img": "obj_purse", "wallet_front_img": "obj_purse_front", "board_img": "bg_wood",
                     "layout": "coins" if all(not P[k].get("note") for k in kinds) else "mixed",
                     "hand_nudge": id_ == "G1",          # SME: the hand on the ₹10 coin, first wallet screen only
                     "no_engine_idle": True, "idle_ms": 7000,
                     "pieces": [dict(P[k]) for k in kinds]}}

def s_sort10():   # «चलिए, दस रुपये छाँटते हैं।» — ₹10 notes AND ₹10 coins (the user: recognise both)
    return s_sort("G1", 10, ["n10", "n10", "c10", "c10", "n20", "n50", "c20", "c5", "c2"], "चलिए, ₹10 छाँटते हैं।")

def s_sort1():    # «चलिए, एक रुपये के सिक्के छांटिए।» — ₹1 among ₹2 / ₹5 / ₹10
    return s_sort("G2", 1, ["c1", "c1", "c1", "c1", "c2", "c2", "c5", "c5", "c10"], "चलिए, ₹1 के सिक्के छांटिए।")

def s_make(id_, T, mode, done_id, done_line, intro=None, keep_tens_open=False):
    """round 3 (SME): make ₹T on the existing build layout — no item picture, only the amount; the ₹10
    note + the ₹1 coin below; ₹10 first, then ₹1 (strict). mode "ghost" = ₹14 (a ghost before every
    move), "seq" = ₹32 / ₹45 (no ghost)."""
    audio = {"prompt": vo("vo_b%d_prompt" % T, "₹10 और ₹1 से ₹%d बनाइए।" % T), "done": vo(done_id, done_line)}
    extra = {}
    if intro:                       # round 4 (SME, ₹14): the earlier version's line, spoken first
        audio["intro"] = vo("vo_b%d_intro" % T, intro); extra["intro_text"] = intro
    if keep_tens_open:              # round 4 (SME, ₹32 / ₹45): ₹10 stays open; extra ₹10 -> the hint ladder
        extra["keep_tens_open"] = True
        # the 2nd extra ₹10's line names the ₹ still missing (₹45: पाँच … एक; ₹32: दो, एक)
        extra["ones_hint"] = {str(n): vo("vo_hint_ones_%d" % n, ("ध्यान से देखिए! अब ₹1 के सिक्कों से ₹%d बनाइए।" % n) if n > 1
                                         else "ध्यान से देखिए! अब ₹1 का एक सिक्का रखिए।") for n in range(1, T % 10 + 1)}
    return {"id": id_, "phase": "guided", "eis": "enactive", "type": "MONEY_BUILD",
            "prompt_hi": "₹%d बनाइए।" % T,
            "audio": audio,
            # round 3c: the «कुल» counter stays in the drop zone; the money starts below it (tray_down)
            "data": dict({"mode": mode, "target": T, "no_item": True, "tray_down": True, "sources": ["n10", "c1"], "pop_sources": True,
                          "no_engine_idle": True, "idle_ms": 7000, "eq_in_band": False}, **extra)}

def s_b14():
    return s_make("G3", 14, "ghost", "vo_g2_done", "शाबाश! एक ₹10 का नोट और चार ₹1 के सिक्के — कुल मिलाकर बने ₹14।",
                  intro="चलिए, ₹10 और ₹1 के सिक्कों से इस राशि को बनाते हैं।")
def s_b32():
    return s_make("G4", 32, "seq", "vo_b32_done", "शाबाश! तीन ₹10 के नोट और दो ₹1 के सिक्के — कुल मिलाकर बने ₹32।", keep_tens_open=True)
def s_b45():
    return s_make("G5", 45, "seq", "vo_b45_done", "शाबाश! चार ₹10 के नोट और पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹45।", keep_tens_open=True)

# the shop (unchanged items / sequence / mechanics). Round 3: preceded by «अब आपकी बारी।» (phase
# practice), opened by Swiftee's line, wooden basket, keep-and-correct retry with ghost hints.
SHOP = [   # round 2f (user): 6 items, one per stall panel, prices 14 / 25 / 35 / 42 / 60 / 65 ascending
        # round 2o (updated deck + user): success is short only — «शाबाश!» / «बहुत बढ़िया!»
        ("apple", "सेब", "obj_apple", 14, "शाबाश!"),
        ("oranges", "संतरे", "obj_oranges", 25, "बहुत बढ़िया!"),
        ("tomatoes", "टमाटर", "obj_tomatoes", 35, "शाबाश!"),
        ("grapes", "अंगूर", "obj_grapes", 42, "शाबाश!"),
        ("bananas", "केले", "obj_bananas", 60, "बहुत बढ़िया!"),     # round 2k: replaces खीरे
        ("carrots", "गाजर", "obj_carrots", 65, "बहुत बढ़िया!")]      # round 2k: replaces आम

SHOP_TEXT = {"intro": "परी पहुँच गई है बाज़ार। आओ, चलो खरीदारी शुरू करें।",
             "more1": "ओहो! रुपये ज़्यादा हैं। कुछ कम करिए।", "less1": "ओहो! रुपये कम हैं। कुछ और डालिए।",
             "more2": "ओहो! अभी भी रुपये ज़्यादा हैं। कुछ कम करिए।", "less2": "ओहो! अभी भी रुपये कम हैं। कुछ और डालिए।",
             # round 3b (user): the 3rd wrong check empties the tray -> «फिर से कोशिश करें।»
             "retry": "फिर से कोशिश करें।"}

def s_shop():
    items = []
    for key, name, im, price, praise in SHOP:
        items.append({"id": key, "name": name, "img": im, "price": price, "praise": praise,
                      "vo_select": vo("vo_m_sel_%s" % key, "%s की कीमत %s रुपये है। %s रुपये बनाइए।" % (name, NUM[price], NUM[price])),
                      "vo_praise": vo("vo_m_ok_%s" % key, praise)})     # identical lines share one clip
    return {"id": "M1", "phase": "practice", "eis": "enactive", "type": "SHOP_GAME",
            "prompt_hi": "कोई वस्तु चुनिए।",
            "audio": {"intro": vo("vo_m_intro", SHOP_TEXT["intro"]),
                      "prompt": vo("vo_m_prompt", "कोई वस्तु चुनिए और उसकी राशि बनाइए।"),
                      "idle": vo("vo_m_idle", "कोई वस्तु चुनिए।"),
                      "more1": vo("vo_m_more1", SHOP_TEXT["more1"]), "less1": vo("vo_m_less1", SHOP_TEXT["less1"]),
                      "more2": vo("vo_m_more2", SHOP_TEXT["more2"]), "less2": vo("vo_m_less2", SHOP_TEXT["less2"]),
                      "retry": vo("vo_m_retry", SHOP_TEXT["retry"]),
                      "first_ok": vo("vo_m_ok_first", "बहुत बढ़िया!"),
                      # round 2g: one-time drag-back tip (no Undo button)
                      "tip": vo("vo_m_tip", "कोई पैसा हटाना हो, तो उसे वापस नीचे खींच लीजिए।"),
                      "done": vo("vo_m_done", "शाबाश! परी की सारी खरीदारी हो गई।")},
            "data": {"items": items, "detail": {}, "no_engine_idle": True, "idle_ms": 7000, "make_idle_ms": 7000,
                     "pari_img": "pari_basket", "pari_full_img": "pari_basket_full", "stall_img": "shop_stall",
                     "text": dict(SHOP_TEXT, **{"choose": "कोई वस्तु चुनिए।", "make": "₹{T} बनाइए।",
                              "check": "जाँचें", "detail_tpl": "बहुत बढ़िया! {parts} मिलाकर ₹{T} बने।",
                              "done": "शाबाश! परी की सारी खरीदारी हो गई।", "list_title": "खरीदारी की सूची",
                              "total": "कुल", "great": "बहुत बढ़िया खरीदारी!"})}}

def s_cel():
    return {"id": "CEL", "phase": "mastery", "eis": "iconic", "type": "CELEBRATION",
            # round 2r (user): the closing line is the reference lesson's (HI02H11 r105) — same words, same
            # Leda recording (copied from its build). «तुम» here by request, as there.
            "prompt_hi": "बहुत बढ़िया, दोस्त! तुमने कमाल कर दिया!",
            "audio": {"prompt": vo("vo_cel_prompt", "बहुत बढ़िया, दोस्त! तुमने कमाल कर दिया!")}, "data": {}}

# ============================================================== helpers
def clip_ms(id_):
    p = os.path.join(AUD, id_ + ".ogg")
    if not os.path.isfile(p): return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return int(float(out) * 1000)
    except Exception:
        return None

def prune_stale():
    """delete exactly the clips whose TEXT changed since the last build, so gen_tts (which skips
    existing files) re-records them and nothing else"""
    side = os.path.join(ROOT, "scripts", "_vo_text.json")   # NOT in assets/: it would ship
    old = json.load(open(side, encoding="utf-8")) if os.path.isfile(side) else {}
    gone = []
    for id_, t in old.items():
        p = os.path.join(AUD, id_ + ".ogg")
        if os.path.isfile(p) and AUDIO.get(id_) != t:
            os.remove(p); gone.append(id_)
    json.dump(AUDIO, open(side, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return gone

def guards(slides, src):
    m = VER_RE.search(src)
    if not m: sys.exit("X  engine has no ENGINE_VERSION")
    for mod in MODULES:
        if ("SlideModules." + mod + " = {") not in src and ("  " + mod + ": {") not in src:
            sys.exit("X  engine lacks module %s — run engine/inject_money.py" % mod)
    ids = [s["id"] for s in slides]
    if len(ids) != len(set(ids)): sys.exit("X  duplicate slide ids")
    for s in slides:
        if s["type"] != "CELEBRATION" and not s.get("prompt_hi") and not s.get("data", {}).get("no_heading"):
            sys.exit("X  %s has no heading" % s["id"])
    order = ["tutorial", "guided", "practice", "mastery"]
    ph = [order.index(s["phase"]) for s in slides]
    if ph != sorted(ph): sys.exit("X  phases out of order")
    if slides[-1]["type"] != "CELEBRATION": sys.exit("X  last slide must be CELEBRATION")
    # every image the card names exists
    need = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("img", "item_img", "pari_img", "pari_full_img", "stall_img", "wallet_img", "wallet_front_img", "board_img") and isinstance(v, str): need.add(v)
                elif k in ("faces", "reveal_faces"): need.update(v)
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(slides)
    need.update(["scn_landing", "title_pari_chali_bazaar"])
    need.update(k + s for k in ("cur_note10", "cur_coin10", "cur_coin1") for s in ("", "_glow", "_lock"))
    miss = [k for k in sorted(need) if not os.path.isfile(os.path.join(IMG, k + ".png"))]
    if miss: sys.exit("X  missing art: %s" % miss)
    # every clip id a slide references is registered
    ref = set()
    def walk2(o):
        if isinstance(o, dict): [walk2(v) for v in o.values()]
        elif isinstance(o, list): [walk2(v) for v in o]
        elif isinstance(o, str) and re.fullmatch(r"vo_[a-z0-9_]+", o): ref.add(o)
    walk2(slides)
    unk = sorted(r for r in ref if r not in AUDIO and r not in COPY_AUDIO)
    if unk: sys.exit("X  clip ids not registered: %s" % unk)
    return m.group(1), sorted(need)

def voiced_segments(path, thresh_db=-42, bridge_ms=150, lo=None, hi=None):
    """25 ms RMS windows above `thresh_db` dBFS, gaps under `bridge_ms` bridged (the reference
    lesson's r108 measure). Optional [lo, hi] ms window. -> [[start_ms, end_ms], ...]"""
    import array
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = array.array("h"); a.frombytes(raw[: len(raw) // 2 * 2])
    segs = []
    for i in range(0, len(a) - 400, 400):
        ms = i // 16
        if lo is not None and not (lo <= ms <= hi): continue
        r = (sum(x * x for x in a[i:i + 400]) / 400) ** 0.5
        if r > 32768 * 10 ** (thresh_db / 20):
            if segs and ms - segs[-1][1] < bridge_ms: segs[-1][1] = ms + 25
            else: segs.append([ms, ms + 25])
    return [x for x in segs if x[1] - x[0] >= 50]

def phrase_window(path, spoken, c0, c1):
    """Where characters [c0, c1) of `spoken` are voiced in the clip: the characters (spaces and
    punctuation weightless) are laid over the clip's voiced time in order -> [start_ms, end_ms]."""
    segs = voiced_segments(path)
    if not segs: return None
    w = [0 if (ch.isspace() or ch in "!,।?—-") else 1 for ch in spoken]
    W = float(sum(w)) or 1.0
    V = sum(e - s0 for s0, e in segs)
    def at(ci):
        v = sum(w[:ci]) / W * V
        for s0, e in segs:
            if v <= e - s0: return s0 + v
            v -= e - s0
        return segs[-1][1]
    return [int(at(c0)), int(at(c1))]

def gate_spec():
    """round 2p: the reference lesson's finished transition (HI02H11 r103-r108): the bird rises on
    swifty_gate_seek.webp, then from her first speaking frame (1.96 s) she is drawn from
    swifty_gate_talk.webp, lip-synced to THIS transition's clip; the title types itself while its
    phrase is voiced. The three stock clips are byte-identical to the reference's, so its measured
    phrase cues are used; the shop transition's phrase is measured here. Every lip track and every
    voiced stretch is measured from the clip on each build."""
    sys.path.insert(0, os.path.join(ROOT, "celebration_kit"))
    from make_lipsync import lipsync
    g = {"img": "assets/UI/swifty_gate_seek.webp", "talk_at_ms": 1960,
         "title_cue_ms": {"tutorial": 4030, "guided": 3970, "practice": 1260},
         "title_dur_ms": {"tutorial": 1230, "guided": 1300, "practice": 850},
         "talk": {"src": "assets/UI/swifty_gate_talk.webp", "first": 37, "cols": 8, "fw": 505, "fh": 440,
                  "rest": 37, "blink": [38, 39, 40],
                  "open": [[42, 43], [44, 45], [51, 52], [53, 54], [55, 56], [58, 59], [60, 61]]}}
    clips = {"tutorial": "vo_pt_tutorial", "guided": "vo_pt_guided", "practice": "vo_pt_practice"}
    tp = os.path.join(AUD, clips["tutorial"] + ".ogg")
    if os.path.isfile(tp):                                   # round 3: «चलिए, शुरू करते हैं» inside the re-recorded line
        sp = AUDIO[clips["tutorial"]]
        c0 = sp.index("चलिए, शुरू"); c1 = sp.index("हैं", c0) + len("हैं")
        w = phrase_window(tp, sp, c0, c1)
        g["title_cue_ms"]["tutorial"] = w[0]; g["title_dur_ms"]["tutorial"] = max(400, w[1] - w[0])
    lips, voice = {}, {}
    for ph, vid in clips.items():
        p = os.path.join(AUD, vid + ".ogg")
        if not os.path.isfile(p): continue
        bits, _ = lipsync(p)
        if "1" not in bits: sys.exit("X  the %s transition VO measured silent" % ph)
        lips[ph] = {"bits": bits, "step_ms": 25}
        cue, dur = g["title_cue_ms"].get(ph), g["title_dur_ms"].get(ph)
        if cue is not None:
            v = voiced_segments(p, lo=cue - 150, hi=cue + dur + 200)
            if v: voice[ph] = v
    g["lips"] = lips; g["title_voice_ms"] = voice
    return g

def done_cues(slide):
    """round 2p: where the closing line names the tens, the ones and the total (ms in the clip), so
    the build screen lights each group as it is spoken."""
    vid = (slide.get("audio") or {}).get("done")
    p = os.path.join(AUD, (vid or "x") + ".ogg")
    if not vid or not os.path.isfile(p): return None
    sp = AUDIO[vid]
    cues = {}
    for key, pat in (("tens", r"\S+ दस रुपये (?:का|के) (?:नोट|सिक्का|सिक्के)"),
                     ("ones", r"\S+ एक रुपये (?:का|के) (?:सिक्का|सिक्के)"),
                     ("total", r"कुल मिलाकर बने \S+ रुपये")):
        m = re.search(pat, sp)
        if m: cues[key] = phrase_window(p, sp, m.start(), m.end())
    return cues or None

def cel_anim():
    """round 2l: lip-sync track for the celebration VO + the sprite facts (scripts/make_cel_sprite.py).
    talk = one char per 25 ms of vo_cel_prompt, '1' on a syllable beat (open mouth), '0' between them.
    Measured off the recorded clip, so a re-record re-syncs on the next build."""
    meta_p = os.path.join(ROOT, "scripts", "_cel_sprite.json")
    clip = os.path.join(AUD, "vo_cel_prompt.ogg")
    if not (os.path.isfile(meta_p) and os.path.isfile(clip)):
        return None
    meta = json.load(open(meta_p))
    import array, math
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = array.array("h"); a.frombytes(raw[: len(raw) // 2 * 2])
    step = 400                                                     # 25 ms at 16 kHz
    rms = [math.sqrt(sum(x * x for x in a[i:i + step]) / step) for i in range(0, len(a) - step, step)]
    mx = max(rms) or 1
    # SYLLABLE beats, not just "voice on": the mouth is open where the clip is loud AND near its local
    # peak (+-100 ms), so it opens on each syllable nucleus and closes in the dips between syllables.
    W = 4
    bits = ["1" if (r > 0.10 * mx and r >= 0.62 * max(rms[max(0, i - W):i + W + 1])) else "0"
            for i, r in enumerate(rms)]
    t = "".join(bits)
    t = t.replace("101", "111").replace("101", "111")             # a 25 ms close inside a syllable = flicker
    t = t.replace("010", "000")                                   # a lone 25 ms open = flicker
    talk = t
    sh = meta["sheets"]
    return {"cols": meta["cols"], "fw": meta["fw"], "fh": meta["fh"], "step_ms": 25, "bits": talk,
            "vo": "vo_cel_prompt",
            # round 2m: the team's three sheets (scripts/make_cel_sprite.py), same frame size + alignment
            "shabaash": {"src": sh["shabaash"]["src"], "pre": list(range(0, 6)),       # standing, mouth shut
                         "word": list(range(6, 30)),                                    # the jump — «शाबाश!»
                         "post": list(range(30, 36))},                                  # lands, mouth shut
            "talk": {"src": sh["talk"]["src"], "open": sh["talk"]["open"]},            # per-syllable pick
            "idle": {"src": sh["idle"]["src"],                                          # after the VO:
                     "loop": [0, 1, 2, 3, 4] + list(range(24, 36))}}                    # mouth-shut frames only

# ============================================================== main
def main():
    src = open(ENGINE, encoding="utf-8").read()
    # round 3 (SME): teaching -> «चलिए, साथ में करें।» -> sort ₹10 -> sort ₹1 -> make ₹14 / ₹32 / ₹45 ->
    # «अब आपकी बारी।» -> the shop -> the end
    slides = [s_intro(), s_sort10(), s_sort1(), s_b14(), s_b32(), s_b45(), s_shop(), s_cel()]
    assert [x[3] for x in SHOP] == sorted(x[3] for x in SHOP), "shop prices must be ascending"
    DEV = {"T1": "पढ़ाना · ₹10 और ₹1", "G1": "छाँटना · ₹10", "G2": "छाँटना · ₹1", "G3": "₹14 (घोस्ट)",
           "G4": "₹32 (क्रम से)", "G5": "₹45 (क्रम से)", "M1": "दुकान का खेल", "CEL": "celebration"}
    for s in slides: s["dev_label"] = DEV[s["id"]]
    ver, imgs = guards(slides, src)
    gone = prune_stale()

    ms = {i: clip_ms(i) for i in AUDIO}
    for sl in slides:                                         # round 2p: spoken-sync highlight
        if sl["type"] == "MONEY_BUILD":
            c = done_cues(sl)
            if c: sl["data"]["done_cues"] = c
    ms = {k: v for k, v in ms.items() if v}
    dist = {}
    for s in slides: dist[s["phase"]] = dist.get(s["phase"], 0) + 1
    all_audio = {i: "assets/Audio/%s.ogg" % i for i in list(AUDIO) + COPY_AUDIO}
    card = {
        "version": "0.2", "skill_code": CODE, "lo_code": "MTG2A04_L01", "grade": "02", "attribute": "A04",
        "skill_type": "CORE", "part_label": "", "medium": "hi",
        "title": {"hi": "परी चली बाज़ार", "en": "Pari goes to the market — making amounts with ₹10 and ₹1"},   # round 3c: new title
        "subtitle_hi": "", "theme": "toybox",
        "skill_description_hi": "₹10 और ₹1 से 99 तक की राशि बनाता है।",
        "landing_audio": LANDING,
        # round 3c (user): new cover with no title + the title as its own picture over it
        "landing_scene": {"img": "scn_landing", "title_img": "title_pari_chali_bazaar"},
        "phase_distribution": dist,
        "gate_titles": GATE_TITLES,
        "gate": gate_spec(),
        # round 2p: the engine's own button sounds (play on the press, next on a real click)
        "ui_sfx": {"play": "sfx_play_button", "next": "sfx_next_button"},
        # round 2q: background music (assets/Audio/bgm_lesson.ogg, the reference lesson's track) — the
        # engine starts it on the play tap and ducks it under every VO / sound effect (HI02H11 r100)
        "bgm": True,
        # round 2l: the jumping + speaking Swiftie, driven frame-by-frame from the VO (end_swiftee.gif,
        # round 2j, is kept on disk but no longer shown)
        "end_anim": cel_anim(),
        "scaffold_rules": {"max_attempts": 3, "hint_levels": 3},
        "signals_expected": ["slide_entered", "slide_completed", "money_sort_done", "money_build_done",
                             "answer_wrong", "phase_transition", "shop_item_bought", "mastery_score", "lesson_completed"],
        "_emoji_fallback": {},
        "slides": slides,
        "assets": {"audio": all_audio, "audio_text": dict(AUDIO), "audio_ms": ms,
                   "image": {k: "assets/Images/%s.png" % k for k in imgs}, "audio_ext": "ogg", "img_ext": "png"}}

    # round 2n: the loader holds until ALL of these are downloaded + decoded (engine/money_modules.js)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from ui_skip import ui_files
    ui = ["assets/UI/" + f for f in ui_files(os.path.join(ROOT, "assets", "UI"), src + json.dumps(card))
          if f.lower().endswith((".webp", ".png", ".svg", ".gif", ".jpg"))]
    imgs_all = sorted(set(card["assets"]["image"].values()) | set(ui) |
                      {"assets/Images/play_btn.svg", "assets/Images/play_btn_disabled.svg"})
    card["preload"] = {"images": imgs_all, "audio": sorted(set(card["assets"]["audio"].values())),
                       # round 2q: the music is only DOWNLOADED before entry (decoding 4 minutes = ~80 MB)
                       "fetch": ["assets/Audio/bgm_lesson.ogg"]}
    payload = json.dumps(card, ensure_ascii=False, indent=1)
    if not CARD_TAG.search(src): sys.exit("X  cardData tag not found")
    html = CARD_TAG.sub(lambda m: m.group(1) + payload + m.group(3), src, count=1)
    first = ["scn_landing", "cur_note10", "cur_coin1"]
    links = "".join('<link rel="preload" as="image" fetchpriority="high" href="assets/Images/%s.png">' % k for k in first)
    html, n_pre = re.subn(r'(?:<link rel="preload" as="image"[^>]*>)+', links, html, count=1)
    html = re.sub(r"<title>.*?</title>", "<title>SwiftPAL · %s · परी चली बाज़ार</title>" % CODE, html, count=1)
    h = hashlib.sha1()
    for f in sorted(os.listdir(AUD)):
        if f.endswith(".ogg"):
            h.update(f.encode()); h.update(open(os.path.join(AUD, f), "rb").read())
    html = html.replace("__AUDIO_V_STAMP__", h.hexdigest()[:12])
    # round 2k: the celebration button exactly as HI02H11_L02_S02 ships it — arrow only (drawn by
    # .end-btn::after), the Hindi label moved to aria-label
    if 'id="endBtn" aria-label="आगे बढ़ें"></button>' not in html:      # older engines: make it arrow-only
        html, n_eb = re.subn(r'<button class="end-btn" id="endBtn">[^<]*</button>',
                             '<button class="end-btn" id="endBtn" aria-label="आगे बढ़ें"></button>', html)
        if n_eb != 1: sys.exit("X  end button markup not found")
    open(os.path.join(ROOT, CODE + ".html"), "w", encoding="utf-8").write(html)
    open(os.path.join(ROOT, "card.json"), "w", encoding="utf-8").write(payload + "\n")

    # VO list for the team (shown vs spoken)
    with open(os.path.join(ROOT, "scripts", "VO_LIST.md"), "w", encoding="utf-8") as f:
        f.write("# %s — VO list (%d clips; spoken text is what is recorded)\n\n| id | spoken | shown |\n|---|---|---|\n" % (CODE, len(AUDIO)))
        for i in AUDIO:
            f.write("| `%s` | %s | %s |\n" % (i, AUDIO[i], SHOWN[i]))
    gap = [i for i in AUDIO if not os.path.isfile(os.path.join(AUD, i + ".ogg"))]
    print("  OK  engine %s · %d slides %s" % (ver, len(slides), dist))
    print("  OK  audio: %d clips registered, %d recorded, %d pending; %d stale pruned" % (len(AUDIO), len(AUDIO) - len(gap), len(gap), len(gone)))
    print("  OK  images: %d referenced, all on disk; preload rewritten: %d" % (len(imgs), n_pre))
    print("  OK  wrote %s.html + card.json" % CODE)

if __name__ == "__main__":
    main()
