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
MODULES = ["MONEY_SHOW", "MONEY_PICK", "MONEY_SCENE", "MONEY_LIST", "MONEY_BUILD", "MONEY_DONE", "SHOP_GAME", "CELEBRATION"]
COPY_AUDIO = ["vo_pt_tutorial", "vo_pt_guided", "vo_pt_practice", "sfx_celebrate", "sfx_correct", "sfx_wrong",
              "sfx_tap", "sfx_pop", "sfx_fb_correct", "sfx_fb_incorrect"]

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

# ============================================================== content (deck wording)
LANDING = vo("vo_landing", "नमस्ते दोस्त! मैं हूँ स्विफ्टी। परी के स्कूल में पिकनिक होने वाली है। उसे पिकनिक के लिए कुछ सामान खरीदना है। चलिए, उसकी मदद करते हैं!")

def s_show():
    return {"id": "T1", "phase": "tutorial", "eis": "iconic", "type": "MONEY_SHOW",
            "prompt_hi": "क्या आप ₹10 और ₹1 को पहचानते हैं?",
            "audio": {"prompt": vo("vo_t1_prompt", "बाज़ार जाने से पहले, आइए पहचानते हैं कि ₹10 और ₹1 कैसे दिखते हैं।")},
            "data": {"groups": [{"faces": ["cur_note10"]}, {"faces": ["cur_coin1", "cur_coin1_back"]}]}}

def s_pick10():
    return {"id": "T2", "phase": "tutorial", "eis": "iconic", "type": "MONEY_PICK",
            "prompt_hi": "₹10 पर टैप कीजिए।",
            "audio": {"prompt": vo("vo_t2_prompt", "इनमें से दस रुपये का नोट पहचानिए।"),
                      "correct": vo("vo_t2_correct", "शाबाश! यह दस रुपये का नोट है।"),
                      "wrong": vo("vo_t2_wrong", "यह दस रुपये का नोट है।")},
            "data": {"options": [{"id": "note10", "faces": ["cur_note10"], "correct": True},
                                 {"id": "coin1", "faces": ["cur_coin1", "cur_coin1_back"]}],
                     "reveal_faces": ["cur_note10"],
                     "correct_text": "शाबाश! यह दस रुपये का नोट है।",
                     "wrong_text": "यह दस रुपये का नोट है।",
                     "idle_pulse_ms": 5000}}

def s_pick1():
    return {"id": "T3", "phase": "tutorial", "eis": "iconic", "type": "MONEY_PICK",
            "prompt_hi": "₹1 पर टैप कीजिए।",
            "audio": {"prompt": vo("vo_t3_prompt", "इनमें से एक रुपये का सिक्का कौन सा है?"),
                      "correct": vo("vo_t3_correct", "शाबाश! यह एक रुपये का सिक्का है।"),
                      "wrong": vo("vo_t3_wrong", "यह एक रुपये का सिक्का है। एक रुपये का सिक्का ऐसा दिखता है।")},
            "data": {"options": [{"id": "coin10", "faces": ["cur_coin10", "cur_coin10_back"]},
                                 {"id": "coin1", "faces": ["cur_coin1", "cur_coin1_back"], "correct": True}],
                     "reveal_faces": ["cur_coin1", "cur_coin1_back"],
                     "correct_text": "शाबाश! यह एक रुपये का सिक्का है।",
                     "wrong_text": "यह एक रुपये का सिक्का है। एक रुपये का सिक्का ऐसा दिखता है।"}}

def s_market():
    return {"id": "T4", "phase": "tutorial", "eis": "iconic", "type": "MONEY_SCENE",
            "prompt_hi": "अब परी के साथ बाज़ार चलिए।",
            "audio": {"prompt": vo("vo_t4_prompt", "परी अपनी खरीदारी की सूची लेकर बाज़ार पहुँच गई है। आइए देखें, उसे क्या-क्या खरीदना है।")},
            "data": {"img": "scn_market", "scene": True}}

LIST = [("कॉपी", 14, "obj_copy"), ("चिप्स", 20, "obj_chips"), ("चॉकलेट", 25, "obj_chocolate"),
        ("प्लेटों का पैकेट", 35, "obj_plates"), ("टॉफ़ी", 5, "obj_toffee")]
LIST_VO_SHOWN = "परी को कॉपी, चिप्स, चॉकलेट, प्लेटें और टॉफ़ी खरीदनी हैं। चलो, ₹10 और ₹1 से हर चीज़ की राशि बनाते हैं।"
LIST_CUE_WORDS = ["कॉपी", "चिप्स", "चॉकलेट", "प्लेटें", "टॉफ़ी"]

def s_list():
    return {"id": "G1", "phase": "guided", "eis": "symbolic", "type": "MONEY_LIST",
            "prompt_hi": "परी की सूची",
            "audio": {"prompt": vo("vo_g1_prompt", LIST_VO_SHOWN)},
            "data": {"rows": [{"name": n, "price": p, "img": im} for n, p, im in LIST]}}

def s_copy():
    return {"id": "G2", "phase": "guided", "eis": "enactive", "type": "MONEY_BUILD",
            "prompt_hi": "₹14 बनाइए",
            "audio": {"prompt": "vo_g2_1", "done": vo("vo_g2_done", "शाबाश! एक ₹10 का नोट और चार ₹1 के सिक्के — कुल मिलाकर बने ₹14। अब परी कॉपी खरीद सकती है।")},
            "data": {"mode": "teach", "target": 14, "item_img": "obj_copy", "item_name": "कॉपी", "sources": ["n10", "c1"], "no_engine_idle": True,
                     "script": [
                         {"say": vo("vo_g2_1", "सबसे पहले परी को ₹14 की कॉपी लेनी है। आइए, ₹10 और ₹1 से ₹14 बनाते हैं।"), "tag": True},
                         {"say": vo("vo_g2_2", "पहले ₹10 का एक नोट रखते हैं।"), "auto": "n10"},
                         {"say": vo("vo_g2_3", "अभी कुल ₹10 हुए। ₹14 बनाने के लिए अभी ₹4 और चाहिए।"), "pulse_total": True},
                         # user 2026-09-29: only the NOTE is placed by Swiftie; the child places all four ₹1
                         {"say": vo("vo_g2_4", "अब एक-एक रुपए के सिक्के रखेंगे।")},
                         {"say": vo("vo_g2_5", "चलो, अब तुम रखो।"), "child": "c1",
                          "idle": [vo("vo_g2_idle", "सिक्के को ऊपर ट्रे में रखो।")]},
                         {"say": vo("vo_g2_6", "अब एक रुपए का और सिक्का रखो।"), "child": "c1",
                          "idle": ["vo_g2_idle"]},
                         {"say": "vo_g2_6", "child": "c1", "idle": ["vo_g2_idle"]},
                         {"say": vo("vo_g2_7", "आखिरी सिक्का।"), "child": "c1", "idle": ["vo_g2_idle"]}]}}

def s_chips():
    return {"id": "G3", "phase": "guided", "eis": "enactive", "type": "MONEY_BUILD",
            "prompt_hi": "₹20 बनाइए।",
            "audio": {"prompt": "vo_g3_1a", "done": vo("vo_g3_done", "बहुत अच्छे! दो ₹10 के सिक्के — कुल मिलाकर बने ₹20।")},
            "data": {"mode": "teach", "target": 20, "item_img": "obj_chips", "item_name": "चिप्स", "sources": ["c10", "c1"],
                     "no_engine_idle": True,
                     "teach_wrong": {"c1": vo("vo_g3_wrong", "₹20 बनाने के लिए ₹10 के सिक्के लगेंगे।")},
                     "script": [
                         {"say": vo("vo_g3_1a", "अब परी को ₹20 के चिप्स लेने हैं।"), "tag": True},
                         {"say": vo("vo_g3_1b", "आइए, ₹10 के सिक्कों से ₹20 बनाते हैं।")},
                         {"say": vo("vo_g3_2", "पहले ₹10 का सिक्का रखते हैं।"), "auto": "c10"},
                         {"say": vo("vo_g3_3", "अभी कुल ₹10 हुए। ₹20 के लिए ₹10 और चाहिए। चलिए, अब आप रखिए।"),
                          "pulse_total": True, "child": "c10",
                          "idle": [vo("vo_g3_idle1", "अब तुम एक और ₹10 का सिक्का रखो।"),
                                   vo("vo_g3_idle2", "₹10 का सिक्का ट्रे में रखिए।")]}]}}

def ladder(tag, T, tens_note, tens_totals, ones_totals, ten_word, zero_line=None):
    """per-total A2/A3 lines. tens = a ₹10 dropped when fewer than ₹10 remain (S11–S13 wording);
    ones = a ₹1 dropped past the ones-part tolerance (S15 wording)."""
    L = {"tens": {}, "ones": {}}
    for X in tens_totals:
        R = T - X
        if X == 0 and zero_line:
            a2 = vo("vo_%s_t0" % tag, zero_line)
        else:
            a2 = vo("vo_%s_t%d" % (tag, X), ("कुल ₹%d हुए। ₹%d बनाने के लिए ₹%d और चाहिए।" if tens_note else
                                                "कुल ₹%d हुए। ₹%d के लिए ₹%d और चाहिए।") % (X, T, R))
        a3 = vo("vo_ones_use_%d" % R, "₹%d बनाने के लिए ₹1 के सिक्कों का इस्तेमाल कीजिए।" % R)
        L["tens"][str(X)] = [a2, a3]
    for X in ones_totals:
        R = T - X
        a2 = vo("vo_%s_o%d" % (tag, X), "कुल ₹%d हैं। ₹%d के लिए ₹%d और बनाओ।" % (X, T, R))
        a3 = vo("vo_tens_use_%s_%d" % (ten_word[0], R), "₹%d बनाने के लिए ₹10 का %s इस्तेमाल कीजिए।" % (R, ten_word[1]))
        L["ones"][str(X)] = [a2, a3]
    return L

NAMES = {"obj_chocolate": "चॉकलेट", "obj_plates": "प्लेटों का पैकेट", "obj_toffee": "टॉफ़ी", "obj_juice": "जूस"}

def s_practice(id_, phase, T, img, sources, vo_prompt, done_line, lad, **extra):
    d = {"mode": "practice", "target": T, "item_img": img, "item_name": NAMES[img], "sources": sources, "ladder": lad,
         "eq_in_band": False, "no_engine_idle": True}
    d.update(extra)
    return {"id": id_, "phase": phase, "eis": "enactive", "type": "MONEY_BUILD",
            "prompt_hi": "₹%d बनाइए।" % T,
            "audio": {"prompt": vo_prompt, "done": done_line}, "data": d}

def s_choc():
    T = 25
    return s_practice("G4", "guided", T, "obj_chocolate", ["c10", "c1"],
        vo("vo_g4_prompt", "परी को ₹25 की चॉकलेट लेनी है। ₹10 और ₹1 के सिक्कों से ₹25 बनाइए।"),
        vo("vo_g4_done", "शाबाश! दो ₹10 के सिक्के और पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹25।"),
        ladder("g4", T, True, range(20, 25), [5, 15], ("coin", "सिक्का")), tag_fx="pulse")

def s_plates():
    T = 35
    return s_practice("P1", "practice", T, "obj_plates", ["n10", "c1"],
        vo("vo_p1_prompt", "परी को ₹35 का प्लेटों का पैकेट लेना है। ₹10 के नोट और ₹1 के सिक्कों से ₹35 बनाइए।"),
        vo("vo_p1_done", "शाबाश! तीन ₹10 के नोट और पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹35। अब परी प्लेटों का पैकेट खरीद सकती है।"),
        ladder("p1", T, False, range(30, 35), [5, 15, 25], ("note", "नोट")))

def s_toffee():   # D5 — added; the deck lists toffee but gives it no screen
    T = 5
    return s_practice("P2", "practice", T, "obj_toffee", ["n10", "c1"],
        vo("vo_p2_prompt", "परी को ₹5 की टॉफ़ी लेनी है। ₹10 के नोट और ₹1 के सिक्कों से ₹5 बनाइए।"),
        vo("vo_p2_done", "शाबाश! पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹5। अब परी टॉफ़ी खरीद सकती है।"),
        ladder("p2", T, False, range(0, 5), [], ("note", "नोट"), zero_line="₹10 का नोट ₹5 से ज़्यादा है।"))

def s_juice():
    # round 2d (user): no «हो गया» — juice completes at ₹17 like every other build screen
    T = 17
    return s_practice("P3", "practice", T, "obj_juice", ["n10", "c1"],
        vo("vo_p3_prompt", "परी को ₹17 का जूस पैकेट लेना है। ₹10 के नोट और ₹1 के सिक्कों से ₹17 बनाइए।"),
        vo("vo_p3_done", "शाबाश! एक ₹10 का नोट और सात ₹1 के सिक्के — कुल मिलाकर बने ₹17। अब परी जूस पैकेट खरीद सकती है।"),
        ladder("p3", T, False, range(10, 17), [7], ("note", "नोट")),
        tag_fx="glow")

def s_done():
    return {"id": "P4", "phase": "practice", "eis": "iconic", "type": "MONEY_DONE",
            "prompt_hi": "परी की पिकनिक की खरीदारी पूरी हुई!",
            "audio": {"prompt": vo("vo_p4_prompt", "शाबाश! आपने ₹10 और ₹1 का उपयोग करके सभी धनराशियाँ बनाईं। परी की पिकनिक की खरीदारी पूरी हुई!")},
            "data": {"items": [{"name": n, "price": p, "img": im} for n, p, im in LIST],
                     "pari_img": "pari_celebrate"}}

# mastery shop (D3: all 8 from the mockup). The SME wrote the praise line for सेब/केले/अंगूर/आम;
# the other four are written in the same pattern (flagged in CHANGES.md).
SHOP = [   # round 2f (user): 6 items, one per stall panel, prices 14 / 25 / 35 / 42 / 60 / 65 ascending
        ("apple", "सेब", "obj_apple", 14, "शाबाश! सेब आपकी टोकरी में आ गया।"),
        ("oranges", "संतरे", "obj_oranges", 25, "कमाल! संतरे अब आपके हैं।"),
        ("tomatoes", "टमाटर", "obj_tomatoes", 35, "बहुत बढ़िया! टमाटर आपने खरीद लिए।"),
        ("grapes", "अंगूर", "obj_grapes", 42, "कमाल! अंगूर अब आपके हैं।"),
        ("cucumbers", "खीरे", "obj_cucumbers", 60, "वाह! खीरे आपकी टोकरी में आ गए।"),
        ("mangoes", "आम", "obj_mangoes", 65, "वाह! आम आपकी टोकरी में आ गए।")]

def detail_spoken(n, c, o, T):
    parts = []
    if n: parts.append("दस रुपये " + ("का एक नोट" if n == 1 else "के %s नोट" % NUM[n]))
    if c: parts.append("दस रुपये " + ("का एक सिक्का" if c == 1 else "के %s सिक्के" % NUM[c]))
    if o: parts.append("एक रुपये " + ("का एक सिक्का" if o == 1 else "के %s सिक्के" % NUM[o]))
    j = (", ".join(parts[:-1]) + " और " + parts[-1]) if len(parts) > 1 else parts[0]
    return "बहुत बढ़िया! %s मिलाकर %s रुपये बने।" % (j, NUM[T])

def s_shop():
    items, detail = [], {}
    for key, name, im, price, praise in SHOP:
        items.append({"id": key, "name": name, "img": im, "price": price, "praise": praise,
                      "vo_select": vo("vo_m_sel_%s" % key, "%s की कीमत %s रुपये है। %s रुपये बनाइए।" % (name, NUM[price], NUM[price])),
                      "vo_praise": vo("vo_m_ok_%s" % key, praise)})
        t, o = divmod(price, 10)
        dd = {}
        for n in range(t + 1):
            c = t - n
            txt = detail_spoken(n, c, o, price)
            # spoken text is already in words; register it verbatim (no ₹ to convert)
            id_ = "vo_m_det_%d_%d_%d" % (price, n, c)
            AUDIO[id_] = txt; SHOWN[id_] = txt; _BY_TEXT[txt] = id_
            dd["%d,%d" % (n, c)] = id_
        detail[str(price)] = dd
    return {"id": "M1", "phase": "mastery", "eis": "enactive", "type": "SHOP_GAME",
            "prompt_hi": "कोई वस्तु चुनिए।",
            "audio": {"prompt": vo("vo_m_prompt", "कोई वस्तु चुनिए और उसकी राशि बनाइए।"),
                      "idle": vo("vo_m_idle", "कोई वस्तु चुनिए।"),
                      "less": vo("vo_m_less", "ओह! रुपये कम हैं। फिर से बनाइए।"),
                      "more": vo("vo_m_more", "ओह! रुपये ज़्यादा हैं। फिर से बनाइए।"),
                      # round 2g: one-time drag-back tip (no Undo button)
                      "tip": vo("vo_m_tip", "कोई पैसा हटाना हो, तो उसे वापस नीचे खींच लीजिए।"),
                      "done": vo("vo_m_done", "शाबाश! परी की सारी खरीदारी हो गई।")},
            "data": {"items": items, "detail": detail, "no_engine_idle": True, "idle_ms": 5500,
                     "pari_img": "pari_basket", "pari_full_img": "pari_basket_full", "stall_img": "shop_stall",
                     "text": {"choose": "कोई वस्तु चुनिए।", "make": "₹{T} बनाइए।",
                              "less": "ओह! रुपये कम हैं। फिर से बनाइए।", "more": "ओह! रुपये ज़्यादा हैं। फिर से बनाइए।",
                              "check": "जाँचें", "detail_tpl": "बहुत बढ़िया! {parts} मिलाकर ₹{T} बने।",
                              "done": "शाबाश! परी की सारी खरीदारी हो गई।", "list_title": "खरीदारी की सूची",
                              "total": "कुल", "great": "बहुत बढ़िया खरीदारी!"}}}

def s_cel():
    return {"id": "CEL", "phase": "mastery", "eis": "iconic", "type": "CELEBRATION",
            "prompt_hi": "शाबाश! आज आपने ₹10 और ₹1 से राशि बनाना सीखा।",
            "audio": {"prompt": vo("vo_cel_prompt", "शाबाश! आज आपने ₹10 और ₹1 से राशि बनाना सीखा।")}, "data": {}}

MASTERY_GATE = {"title": "खरीदारी का खेल!", "audio": vo("vo_pt_mastery", "चलिए, अब खरीदारी का खेल खेलते हैं!")}

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
        if s["type"] != "CELEBRATION" and not s.get("prompt_hi"):
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
                if k in ("img", "item_img", "pari_img", "pari_full_img", "stall_img") and isinstance(v, str): need.add(v)
                elif k in ("faces", "reveal_faces"): need.update(v)
                else: walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(slides)
    need.add("scn_landing")
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

def gate_spec():
    """round 2i: peek once -> talk loop while the VO sounds -> rest (scripts/make_gate_bird.py).
    peek_ms is measured off the file so the talk starts on her last rising frame."""
    ui = os.path.join(ROOT, "assets", "UI")
    peek = os.path.join(ui, "gate_peek.webp")
    if not os.path.isfile(peek):
        return {"img": "assets/UI/swifty_gate.webp", "talk_at_ms": 3820}      # stock gate
    from PIL import Image, ImageSequence
    ms = sum((f.info.get("duration") or 40) for f in ImageSequence.Iterator(Image.open(peek)))
    return {"img": "assets/UI/gate_peek.webp", "peek": "assets/UI/gate_peek.webp",
            "talk": "assets/UI/gate_talk.webp", "rest": "assets/UI/gate_rest.webp",
            "peek_ms": ms, "hold_ms": 450}

# ============================================================== main
def main():
    src = open(ENGINE, encoding="utf-8").read()
    slides = [s_show(), s_pick10(), s_pick1(), s_market(), s_list(), s_copy(), s_chips(), s_choc(),
              s_plates(), s_toffee(), s_juice(), s_done(), s_shop(), s_cel()]
    assert [x[3] for x in SHOP] == sorted(x[3] for x in SHOP), "shop prices must be ascending"
    DEV = {"T1": "p2 · ₹10 और ₹1 पहचानें", "T2": "p3–4 · ₹10 पर टैप", "T3": "p5–6 · ₹1 पर टैप", "T4": "p7 · बाज़ार",
           "G1": "p8 · परी की सूची", "G2": "p9 · कॉपी ₹14 (teach)", "G3": "p11 · चिप्स ₹20 (teach)",
           "G4": "p12 · चॉकलेट ₹25", "P1": "p13 · प्लेटें ₹35", "P2": "added · टॉफ़ी ₹5", "P3": "p16 · जूस ₹17 (हो गया)",
           "P4": "p18 · खरीदारी पूरी", "M1": "p17–21 · दुकान का खेल", "CEL": "celebration"}
    for s in slides: s["dev_label"] = DEV[s["id"]]
    ver, imgs = guards(slides, src)
    gone = prune_stale()

    ms = {i: clip_ms(i) for i in AUDIO}
    ms = {k: v for k, v in ms.items() if v}
    # list rows pulse as the VO names them: position of each item word in the spoken line x its length
    lst = next(s for s in slides if s["type"] == "MONEY_LIST")
    line = AUDIO[lst["audio"]["prompt"]]; dur = ms.get(lst["audio"]["prompt"]) or len(line) * 85
    for r, w in zip(lst["data"]["rows"], LIST_CUE_WORDS):
        r["cue_ms"] = int(dur * line.index(w) / len(line))

    dist = {}
    for s in slides: dist[s["phase"]] = dist.get(s["phase"], 0) + 1
    all_audio = {i: "assets/Audio/%s.ogg" % i for i in list(AUDIO) + COPY_AUDIO}
    card = {
        "version": "0.2", "skill_code": CODE, "lo_code": "MTG2A04_L01", "grade": "02", "attribute": "A04",
        "skill_type": "CORE", "part_label": "", "medium": "hi",
        "title": {"hi": "परी की पिकनिक की खरीदारी", "en": "Pari's picnic shopping — making amounts with ₹10 and ₹1"},
        "subtitle_hi": "", "theme": "toybox",
        "skill_description_hi": "₹10 और ₹1 से 99 तक की राशि बनाता है।",
        "landing_audio": LANDING,
        "landing_scene": {"img": "scn_landing"},
        "phase_distribution": dist,
        "mastery_gate": MASTERY_GATE,
        "gate": gate_spec(),
        "scaffold_rules": {"max_attempts": 3, "hint_levels": 3},
        "signals_expected": ["slide_entered", "slide_completed", "money_pick_first_try", "money_build_done",
                             "answer_wrong", "phase_transition", "shop_item_bought", "mastery_score", "lesson_completed"],
        "_emoji_fallback": {},
        "slides": slides,
        "assets": {"audio": all_audio, "audio_text": dict(AUDIO), "audio_ms": ms,
                   "image": {k: "assets/Images/%s.png" % k for k in imgs}, "audio_ext": "ogg", "img_ext": "png"}}

    payload = json.dumps(card, ensure_ascii=False, indent=1)
    if not CARD_TAG.search(src): sys.exit("X  cardData tag not found")
    html = CARD_TAG.sub(lambda m: m.group(1) + payload + m.group(3), src, count=1)
    first = ["scn_landing", "cur_note10", "cur_coin1"]
    links = "".join('<link rel="preload" as="image" fetchpriority="high" href="assets/Images/%s.png">' % k for k in first)
    html, n_pre = re.subn(r'(?:<link rel="preload" as="image"[^>]*>)+', links, html, count=1)
    html = re.sub(r"<title>.*?</title>", "<title>SwiftPAL · %s · परी की पिकनिक की खरीदारी</title>" % CODE, html, count=1)
    h = hashlib.sha1()
    for f in sorted(os.listdir(AUD)):
        if f.endswith(".ogg"):
            h.update(f.encode()); h.update(open(os.path.join(AUD, f), "rb").read())
    html = html.replace("__AUDIO_V_STAMP__", h.hexdigest()[:12])
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
