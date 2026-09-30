# MTG2A04_L01_S01 — «परी की पिकनिक की खरीदारी» · CHANGE CHECKLIST (round 2, SME deck `MTG2A04_L01_S01_review.pptx`)

This file is the contract for the revise run AND its scorecard. Every ask in the deck is one row.
Status vocabulary: ✅ DONE · ⚑ FLAGGED-BACK · ⏳ PENDING · N/C (no change requested).

**Visual baseline (user instruction, 2026-09-29):** layout, buttons, animation, colours and typography
follow `F:\CG Game\FLN\File3\HI02H11_L02_S02_DEV_HANDOFF` (its pinned engine `4_ENGINE/lesson_template.html`,
2026.08.04b-r4-unified + its UI kit). Only the content changes. The first-draft HTML (engine 2026.07.16i,
32 generic MAKE_SET / PICK slides, no art, no VO, no build script) is replaced wholesale — the deck
describes a different game from the draft.

Deck page refs = the deck's slide number (S#) and the page label printed on it ("Page N").

| # | Deck | Target | Change (verbatim from the deck where it gives wording) | Where | Status | Proof |
|---|---|---|---|---|---|---|
| 1 | S1 · Page 1 | Landing | Title «परी की पिकनिक की खरीदारी»; Pari (girl, yellow kurta, pink dupatta, bag) holding a shopping list, centre; Swiftie bottom-left with audio button; arrow/start button bottom-centre (mockup image) | card + art | ✅ | shot 01; `landing_hero` = pari_list |
| 2 | S1 | Landing VO | «नमस्ते दोस्त! मैं हूँ स्विफ्टी। परी के स्कूल में पिकनिक होने वाली है। उसे पिकनिक के लिए कुछ सामान खरीदना है। चलिए, उसकी मदद करते हैं!» | card + VO | ✅ | `vo_landing` (9.7 s) |
| 3 | S1 | Landing motion | "No animation embedded." (no extra animation on the landing art) | card | ✅ | stock landing, no added motion |
| 4 | S2 · Page 2 | Recall transition | OST «क्या आप ₹10 और ₹1 को पहचानते हैं?» | card | ✅ | shot 02 |
| 5 | S2 | Recall VO | «बाज़ार जाने से पहले, आइए पहचानते हैं कि ₹10 और ₹1 कैसे दिखते हैं।» | VO | ✅ | `vo_t1_prompt` |
| 6 | S2 | Motion | ₹10 note और ₹1 coin हल्के pop के साथ दिखाई दें | engine module | ✅ | MONEY_SHOW `.mn-pop` stagger + pop sfx |
| 7 | S2 | Visuals | ₹10 note and ₹1 coin, BACK and FRONT both; note serial 000000 and «SPECIMEN» written on the note | art | ✅ | shot 02 — note front + ₹1 coin front & back (the mockup shows both coin faces, the note one side). Currency = team set (D9) |
| 8 | S2 | Layout | Swiftie bottom-left; buttons centre | engine module | ✅ | tutorial frame: Swiftie bottom-left, arrow centre |
| 9 | S3 · Page 3 | Identify ₹10 | OST «₹10 पर टैप कीजिए।»; two tappable cards: ₹10 note · ₹1 coin (both faces); correct = ₹10 note | card + module | ✅ | shot 03 |
| 10 | S3 | Entry VO | «इनमें से दस रुपये का नोट पहचानिए।» | VO | ✅ | `vo_t2_prompt` |
| 11 | S3 | No response | 5 sec बाद ₹10 note card pulse करे | module | ✅ | `idle_pulse_ms: 5000` (code; timing not driven) |
| 12 | S3 | Correct | ₹10 note glows; text + VO «शाबाश! यह दस रुपये का नोट है।» | module + VO | ✅ | drive: `T2 right -> green + nav on`, `T2 correct text` |
| 13 | S3 | Incorrect (₹1 coin) | ₹1 coin vibrates + red error; ₹10 note appears centre screen; text + VO «यह दस रुपये का नोट है।» | module + VO | ✅ | drive: `T2 wrong -> reveal shown + card red`, `T2 wrong VO`; shot 04 |
| 14 | S4 · Page 4 | ₹10 correct state | Note card turns green; OST «शाबाश! यही दस रुपये का नोट है।»; chime + confetti (deck S3 says «यह», S4 says «यही» — see Q) | module | ✅ | shot 05 (green + ✓ + glow, sfx_fb_correct, confetti); text per D8 |
| 15 | S4 | Visuals | "Character: Swifty upar hogi" | module | ✅ (per D7) | tutorial-phase screens keep Swiftie bottom-left |
| 16 | S4 | Visuals | ALL currency (notes + coins): "000" printed + «SPECIMEN» written clearly — consistent on every screen | art | ⚑ FLAGGED-BACK | team currency used as supplied (D9): the note carries 000000 + SPECIMEN; the team's coin FRONTS show 2013 and no SPECIMEN; the generated coin BACKS carry 000 + SPECIMEN |
| 17 | S5 · Page 5 | Identify ₹1 | OST «₹1 पर टैप कीजिए।»; mockup cards: ₹10 coin (both faces) · ₹1 coin (both faces) | card + module | ✅ | shot 06 — ₹10 coin vs ₹1 coin (D8) |
| 18 | S5 | Entry VO | «इनमें से एक रुपये का सिक्का कौन सा है?» | VO | ✅ | `vo_t3_prompt` |
| 19 | S5 | Correct | ₹1 coin box turns green; text + VO «शाबाश! यह एक रुपये का सिक्का है।»; chime + confetti | module + VO | ✅ | same code path as row 12 |
| 20 | S5 | Incorrect | "₹10 note tapped" (mockup shows the ₹10 COIN) → turns red + error sound; ₹1 coins appear centre; text + VO «यह एक रुपये का सिक्का है। एक ka sikka ऐसा दिखता है।» | module + VO | ✅ | `vo_t3_wrong` (D8 wording) |
| 21 | S5 | Visuals | Swiftie visible bottom-left | module | ✅ | tutorial frame |
| 22 | S6 · Page 6 | ₹1 correct state | Coin box green; text + VO «शाबाश! यह एक रुपये का सिक्का है।»; chime + confetti (mockup OST reads «सही! यही ₹1 का सिक्का है।») | module | ✅ | text + VO = `vo_t3_correct` (D8) |
| 23 | S7 · Page 7 | Market transition | OST «अब परी के साथ बाज़ार चलिए।»; Pari centre holding the list; list NOT fully readable on this slide | card + art | ✅ | shot 07 |
| 24 | S7 | VO | «परी अपनी खरीदारी की सूची लेकर बाज़ार पहुँच गई है। आइए देखें, उसे क्या-क्या खरीदना है।» | VO | ✅ | `vo_t4_prompt` |
| 25 | S7 | Flow | "[swifty second transition after this slide]" → Swiftie phase-gate transition after page 7 | card | ✅ | gate test: T4 → «चलिए, साथ में करें!» → G1 |
| 26 | S7 | Flow | अगली slide में सूची पर zoom | module | ✅ | MONEY_LIST `.mn-zoom` entry |
| 27 | S8 · Page 8 | Shopping list | Title «परी की सूची»; rows कॉपी ₹14 · चिप्स ₹20 · चॉकलेट ₹25 · प्लेटों का पैकेट ₹35 · टॉफ़ी ₹5 | card + module | ✅ | shot 08 |
| 28 | S8 | VO | «परी को कॉपी, चिप्स, चॉकलेट, प्लेटें और टॉफ़ी खरीदनी हैं। चलो, ₹10 और ₹1 से हर चीज़ की राशि बनाते हैं।» | VO | ✅ | `vo_g1_prompt` |
| 29 | S8 | Motion | As the VO names each item, that row pulses slightly, then moves on to the next | module | ✅ | rows pulse at cues measured off the clip: 550 / 1022 / 1573 / 2202 / 3067 ms |
| 30 | S8 | Transition | Arrow tap पर Guided teaching | card | ✅ | manual arrow (engine auto-advance disabled for this card) |
| 31 | S9 · Page 9 | Copy ₹14 teach — screen | OST «₹14 बनाइए»; कॉपी picture + price tag «₹14» (price tag shows amount ONLY, no item name); bottom tray ₹10 note + ₹1 coins; empty target tray centre with «कुल ₹0» | module + art | ✅ | shot 09 |
| 32 | S9 | Step 1 | VO1 «सबसे पहले परी को ₹14 की कॉपी लेनी है। आइए, ₹10 और ₹1 से ₹14 बनाते हैं।» VO2 «पहले ₹10 का एक नोट rakhte hain।» — note moves into tray on its own; total → कुल ₹10 (demo) | module + VO | ✅ | drive: `G2 demo placed ₹10 + ₹1 (कुल ₹11)` |
| 33 | S9 | Step 2 | VO3 «अभी कुल ₹10 हुए। ₹14 बनाने के लिए अभी ₹4 और चाहिए।» + counter pulses | module + VO | ✅ | `pulse_total` step (code) |
| 34 | S9 | Step 3 | VO4 «अब एक-एक रुपए के सिक्के रखेंगे।» — one ₹1 coin moves in on its own; कुल ₹11 (demo) | module + VO | ✅ | drive (₹11 after demo) |
| 35 | S9 | Step 4 | VO5 «चलो, अब तुम रखो।» — ₹1 coin pulses; child drags it in (कुल ₹12). No action → coin pulses again + «सिक्के को ऊपर ट्रे में रखो।» | module + VO | ✅ | drive (child drags); idle line `vo_g2_idle` (code, not timed) |
| 36 | S9 | Step 5 | VO6 «अब एक रुपए का और सिक्का रखो» — child drags (कुल ₹13) | module + VO | ✅ | drive |
| 37 | S9 | Step 6 | VO7 «आखिरी सिक्का।» — child drags (कुल ₹14); positive audio | module + VO | ✅ | drive |
| 38 | S9 | Step 7 | VO8 «शाबाश! एक ₹10 का नोट और चार ₹1 के सिक्के — कुल मिलाकर बने ₹14। अब परी कॉपी खरीद सकती है।»; OST in green, centre «₹10 + ₹1 + ₹1 + ₹1 + ₹1 = ₹14»; total green; tray highlights; green confetti; कॉपी highlights; arrow appears | module + VO | ✅ | drive: `G2 … ₹14 finished`, `G2 equation`; shot 10 |
| 39 | S10 · Page 11 | Chips ₹20 teach — screen | OST «₹20 बनाइए।» (appears with the second line of VO1); चिप्स + price tag ₹20; tray ₹10 coins (multiple) + ₹1 coins (visible, not needed); कुल ₹0 | module | ✅ | drive: `G3 prompt appears with 2nd line`; shot 11 |
| 40 | S10 | Step 1 | VO1 «अब परी को ₹20 के चिप्स लेने हैं। आइए, ₹10 के सिक्कों से ₹20 बनाते हैं।» | VO | ✅ | `vo_g3_1a` + `vo_g3_1b` |
| 41 | S10 | Step 2 | VO2 «पहले ₹10 का सिक्का रखते हैं।» — coin moves in on its own; कुल ₹10 | module + VO | ✅ | drive (कुल ₹10 after demo) |
| 42 | S10 | Step 3 | VO3 «अभी कुल ₹10 हुए। ₹20 के लिए ₹10 और चाहिए। चलिए, अब आप रखिए।» + counter pulses; child drags ₹10 coin → कुल ₹20; positive audio | module + VO | ✅ | drive: `G3 ₹10 coin -> ₹20 finished` |
| 43 | S10 | Inactivity | VO4 «अब तुम एक और ₹10 का सिक्का रखो।» + ₹10 coin pulses; again → VO5 «₹10 का सिक्का ट्रे में रखिए।» (OST stays) | module + VO | ✅ | idle ladder `vo_g3_idle1` → `vo_g3_idle2` (code, not timed) |
| 44 | S10 | Wrong (₹1 coin) | ₹1 coin returns; VO6 «₹20 बनाने के लिए ₹10 के सिक्के लगेंगे।»; ₹10 coin pulses | module + VO | ✅ | drive: `G3 ₹1 rejected + VO6` |
| 45 | S10 | Completion | VO7 «बहुत अच्छे! दो ₹10 के सिक्के — कुल मिलाकर बने ₹20।»; OST green «₹10 + ₹10 = ₹20»; total green; tray highlights; confetti; चिप्स highlights; arrow | module + VO | ✅ | drive |
| 46 | S11 · Page 12 | Chocolate ₹25 guided practice | VO «परी को ₹25 की चॉकलेट लेनी है। ₹10 और ₹1 के सिक्कों से ₹25 बनाइए।» + price tag pulses; tray ₹10 coins + ₹1 coins; drag one by one; total updates; positive VO/audio per drop | module + VO | ✅ | shot 12; price tag pulses with the VO |
| 47 | S11 | Inactivity | Coins pulse; on second pause a ghost image of the next currency travels to the tray | module | ✅ | idle ladder pulse → ghost (code, not timed) |
| 48 | S11 | Wrong ₹10 after कुल ₹20 | A1 bounce + gentle buzz · A2 bounce + VO «कुल ₹20 हुए। ₹25 बनाने के लिए ₹5 और चाहिए।» + ₹1 ghost nudge · A3 bounce + VO «₹5 बनाने के लिए ₹1 के सिक्कों का इस्तेमाल कीजिए।», ₹1 glows, ₹10 fades | module + VO | ✅ | drive: `G4 tens A2 VO said`, `G4 tens ladder A3: ₹10 off, ₹1 glows, VO` |
| 49 | S11 | Completion | At कुल ₹25: total green at once; tray inactive; further drags bounce; OST → «₹10 + ₹10 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 = ₹25»; VO «शाबाश! दो ₹10 के सिक्के और पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹25।»; green confetti; चॉकलेट highlights; arrow | module + VO | ✅ | drive: `G4 -> ₹25 finished, equation in band`; shot 15 |
| 50 | S11 | Note | "Counter will not exist in master game level." | module | ✅ | SHOP_GAME has no running total |
| 51 | S12 · Page 13 | Plates ₹35 practice | VO «परी को ₹35 का प्लेटों का पैकेट लेना है। ₹10 के नोट और ₹1 के सिक्कों से ₹35 बनाइए।»; tray ₹10 notes + ₹1 coins; कुल ₹0; drag one by one; total updates; positive audio | module + VO | ✅ | shot 16 (same module + ladder as row 48; not separately driven) |
| 52 | S12 | Inactivity | Pulse, then ghost of next currency on the second pause | module | ✅ | as row 47 |
| 53 | S12 | Wrong ₹10 after कुल ₹30 | A1 bounce + buzz · A2 bounce + VO «कुल ₹30 हुए। ₹35 के लिए ₹5 और चाहिए।» + ghost auto-shown · A3 bounce + VO «₹5 बनाने के लिए ₹1 के सिक्कों का इस्तेमाल कीजिए।», ₹1 glows, ₹10 fades | module + VO | ✅ | ladder lines `vo_p1_t30…t34` registered |
| 54 | S12 | ₹1 first | Not incorrect — any valid path to ₹35 accepted (subject to the ₹1 tolerance, row 60) | module | ✅ | any order accepted within the tolerance |
| 55 | S12 | Completion | At ₹35: total green; tray inactive; drags bounce; OST «₹10 + ₹10 + ₹10 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 = ₹35»; VO «शाबाश! तीन ₹10 के नोट और पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹35। अब परी पेंसिल बॉक्स खरीद सकती है।» (deck says पेंसिल बॉक्स — see Q); confetti; item highlights; arrow | module + VO | ✅ | `vo_p1_done` — «…प्लेटों का पैकेट…» (D8) |
| 56 | S13 · Page 16 | Juice ₹17 | VO «परी को ₹17 का जूस पैकेट लेना है। ₹10 के नोट और ₹1 के सिक्कों से ₹17 बनाइए।» + price tag glows; tray ₹10 notes + ₹1 coins; कुल ₹0 shown under the tray; «हो गया» button (mockup) | module + VO | ✅ | shot 18; «हो गया» + total below the tray (D2) |
| 57 | S13 | Inactivity | Pulse, then ghost on the second pause | module | ✅ | as row 47 |
| 58 | S13 | Wrong ₹10 after कुल ₹10 | A1 bounce + buzz · A2 VO «कुल ₹10 हुए। ₹17 के लिए ₹7 और चाहिए।» + ghost · A3 VO «₹7 बनाने के लिए ₹1 के सिक्कों का इस्तेमाल कीजिए।», ₹1 glows, ₹10 fades; anything after ₹17 bounces | module + VO | ✅ | ladder `vo_p3_t10…t16`; drops after ₹17 bounce |
| 59 | S13 | Completion | At ₹17: total green; inactive; OST «₹10 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 + ₹1 = ₹17»; VO «शाबाश! एक ₹10 का नोट और सात ₹1 के सिक्के — कुल मिलाकर बने ₹17। अब परी जूस पैकेट खरीद सकती है।»; confetti; highlight; arrow | module + VO | ✅ | drive: `P3 हो गया -> finished`; shot 19 |
| 60 | S14 | ₹1 tolerance rule | ₹1 coins placed before tens: accept only up to the ones-part (₹14→4, ₹25→5, ₹35→5, ₹17→7); beyond that the ₹1 coin bounces back — applies across all amounts in the file | module | ✅ | drive: `G4 5 coins -> ₹5`, `G4 6th ₹1 A1 bounce, no VO` |
| 61 | S15 | Tolerance feedback | A1 ₹1 bounces + buzz · A2 VO + ghost of next required coin · A3 VO (+ ₹1 disabled): ₹25 «कुल ₹5 हैं। ₹25 के लिए ₹20 और बनाओ।» / «₹20 बनाने के लिए ₹10 का सिक्का इस्तेमाल कीजिए।»; ₹35 «कुल ₹5 हैं। ₹35 के लिए ₹30 और बनाओ।» / «₹30 बनाने के लिए ₹10 का नोट इस्तेमाल कीजिए।»; ₹17 «कुल ₹7 हैं। ₹17 के लिए ₹10 और बनाओ।» / «₹10 बनाने के लिए ₹10 का नोट इस्तेमाल कीजिए।» | module + VO | ✅ | drive: `G4 A2 VO 'कुल ₹5 हैं…'`, `G4 A3 VO + ₹1 disabled + ₹10 glows`; shots 13–14 |
| 62 | S15 | Check-button note | "For Grade 2 … a check button is worth adding" (जमा करें / देखिए / ✓), under-check VO «अभी कुल ₹12 हुए हैं। ₹17 के लिए ₹5 और चाहिए। और सिक्के या नोट रखिए।»; over rule = red immediately | module + VO | ✅ (per D2) | drive: `P3 check under -> VO u3` |
| 63 | S16 · Page 18 | Completion | Title «परी की पिकनिक की खरीदारी पूरी हुई!»; list ✓ कॉपी ✓ चिप्स ✓ चॉकलेट ✓ प्लेटें ✓ टॉफ़ी; «5 / 5» | module | ✅ | shot 20 |
| 64 | S16 | VO | «शाबाश! आपने ₹10 और ₹1 का उपयोग करके सभी धनराशियाँ बनाईं। परी की पिकनिक की खरीदारी पूरी हुई!» | VO | ✅ | `vo_p4_prompt` |
| 65 | S16 | Motion / CTA | हल्की confetti; every list item ticks; arrow → lesson complete / replay routing | module | ✅ | ticks + confetti; arrow → shop game (D6) |
| 66 | S17 | Mastery game mockup | 6-state shop game: CHOOSE → SELECT → MAKE ₹X → CHECK → IN BASKET → SHOPPING COMPLETE; basket counter «n/8»; Pari with basket; shop stall with 8 priced items (mockup: apple 14, bananas 20, carrots 23, tomatoes 35, grapes 42, oranges 25, cucumber 60, mangoes 65); final shopping list with ticks + total | new module + art | ✅ | shots 21–24 |
| 67 | S18 | Game screen 1 | Pari with empty basket; all items active with price; light idle movement; OST «कोई वस्तु चुनिए।»; VO «कोई वस्तु चुनिए और उसकी राशि बनाइए।»; 5–6 s no action → one item glows + VO «कोई वस्तु चुनिए।» | module + VO | ✅ | idle glow + `vo_m_idle` (code; at most 3 per visit; not timed) |
| 68 | S18 | Game screen 2 | Tapped item shines, others dull, item moves to centre, price shown large; OST «₹14 बनाइए।»; VO e.g. «सेब की कीमत चौदह रुपये है। चौदह रुपये बनाइए।» | module + VO | ✅ | drive: `M1 make view for ₹14`; shot 22 |
| 69 | S18 | Game screen 3 | Currency tray ₹10 note · ₹10 coin · ₹1 coin; any start; tap OR drag; placed money shows in amount area; tap placed money to return it; Undo button; «जाँचें» inactive until ≥1 currency placed; no running total ("Counter will not exist in master game level") | module | ✅ | drive: `M1 जाँचें disabled with nothing placed`, `M1 undo re-activates ₹1`; tap and drag both wired |
| 70 | S19 | Check — less | Amount area shakes; soft error; all money returns; area empties; attempt +1; OST/VO «ओह! रुपये कम हैं। फिर से बनाइए।» | module + VO | ✅ | drive: `M1 less -> VO less + tray emptied` |
| 71 | S19 | Check — more | Same actions; OST/VO «ओह! रुपये ज़्यादा हैं। फिर से बनाइए।» | module + VO | ✅ | drive: `M1 more VO` |
| 72 | S20 | Attempts 1–3 | All currency active; correct combination NOT told; short कम/ज़्यादा feedback; reset each time (attempt table image) | module | ✅ | no hint on attempts 1–3 (code) |
| 73 | S20 | After 3rd wrong | Next attempt supported — layout unchanged, backend cap: tens (₹10 note + ₹10 coin counted together) ≤ tens-part, ₹1 ≤ ones-part | module | ✅ | drive: `M1 after 3 wrong: caps hold at 1 ten + 4 ones` |
| 74 | S21 | Valid combos | Any note/coin mix of the tens is correct (₹25: 2 notes / 2 coins / 1+1, + 5×₹1) | module | ✅ | drive (₹10 coin + ₹10 note counted together) |
| 75 | S21 | Deactivation | ones cap reached → ₹1 inactive; tens cap reached → ₹10 note + coin inactive; extra currency bounces back to tray, no verbal hint; undo re-activates | module | ✅ | drive: `M1 capped currencies inactive`, `M1 undo re-activates ₹1` |
| 76 | S21 | First correct | Placed money green-glows; correct sound; used currency highlights in sequence; OST «बहुत बढ़िया! ₹10 के 2 नोट और ₹1 के 5 सिक्के मिलाकर ₹25 बने।» VO «बहुत बढ़िया! दस रुपये के दो नोट और एक रुपये के पाँच सिक्के मिलाकर पच्चीस रुपये बने।» — worded from the ACTUAL currency used; first item only | module + VO | ✅ | drive: `M1 first purchase = detailed OST`, `M1 detailed VO chosen by actual currency`; shot 23 |
| 77 | S21 | Later correct | Short playful line: सेब «शाबाश! सेब आपकी टोकरी में आ गया।» · केले «बहुत बढ़िया! केले आपने खरीद लिए।» · अंगूर «कमाल! अंगूर अब आपके हैं।» · आम «वाह! आम आपकी टोकरी में आ गए।» | VO | ✅ | drive: `M1 2nd purchase = playful line` (4 lines authored — see Beyond) |
| 78 | S21 | After correct | Item jumps, goes into basket, basket counter updates, bought item inactive, others active again | module | ✅ | drive: `M1 back to stall, counter 1/8`, `M1 apple marked sold` |
| 79 | S22 | Dev note — per-drop rule | Any order; check after every drop; exact → all green, inactive; less → continue; idle → VO «अभी कुल ₹[current] हुए हैं। ₹[remaining] और रखिए।» OST «₹[remaining] और रखिए।» | module + VO | ⚑ FLAGGED-BACK | superseded by D1: the per-screen idle ladder (pulse → ghost) runs instead of this idle VO |
| 80 | S22 | Dev note — over | The item that crosses the target sits red + pulsing; child taps it to return; VO «ये ज़्यादा हो गया। ₹[target] बनाने हैं, लेकिन अभी ₹[current] हो गए। लाल नोट/सिक्के पर टैप करके वापस रखिए।»; after tap-back no extra VO | module + VO | ⚑ FLAGGED-BACK | superseded by D1: the total can never go over (bounce ladder) |

## Decisions (asked before building — user, 2026-09-29)
| Q | Question | Decision |
|---|---|---|
| D1 | Over-target: bounce ladder (S11–S15) vs red-in-tray tap-back (S22)? | **Bounce back + 3-try ladder.** The total can never exceed the target, so rows 79 (idle VO aside) and 80 are superseded. |
| D2 | Juice हो गया button? | **Check on juice only.** Chocolate/plates/toffee auto-complete at the target; juice completes on «हो गया». Under → «अभी कुल ₹X हुए हैं। ₹17 के लिए ₹Y और चाहिए। और सिक्के या नोट रखिए।» |
| D3 | Shop items | **All 8 from the mockup:** सेब ₹14, केले ₹20, गाजर ₹23, टमाटर ₹35, अंगूर ₹42, संतरे ₹25, खीरे ₹60, आम ₹65. Praise lines for गाजर/टमाटर/संतरे/खीरे written in the SME's style. |
| D4 | Register (आप/तुम mix) | **Keep the deck's wording exactly** (mixed register ships as written — see Observations). |
| D5 | Toffee ₹5 has no build screen | **Add a toffee ₹5 screen** (plates pattern, ₹10 notes + ₹1 coins in the tray), after plates, before juice. |
| D6 | Order of completion vs shop game | **Completion (S16) → Swiftie transition → shop game → final celebration.** |
| D7 | Swiftie position | **Follow the reference file.** As built, the reference engine decides by PHASE: tutorial screens (recall, both identify screens, market) mount in the grid card with Swiftie bottom-left — which is what S2/S5 ask; guided → mastery screens (list onward) get the header badge top-left. ⚑ This differs from the option text in two places: the identify screens show Swiftie bottom-left (not in the header), and the list + completion screens show the header badge (not bottom-left). |
| D8 | Deck slips | Fix all four: plates VO «पेंसिल बॉक्स» → «प्लेटों का पैकेट»; «एक ka sikka» → «एक रुपये का सिक्का ऐसा दिखता है।», «rakhte hain» → «रखते हैं»; identify-₹1 distractor = ₹10 COIN (mockup); correct-state OST = the notes' wording (shown = spoken). |
| D9 | Currency art (asked after the user dropped `assets/Currency/` in mid-run) | **"I've added images of the currency so use those."** The team set (Default / Glow / Lock for ₹1 coin, ₹10 coin, ₹10 note) is used UNCHANGED for every front face and every draggable piece; Glow = the 3rd-try hint glow, Lock = a disabled currency. The set has no coin BACKS, so the two back faces the recall/identify screens need are built from the SME's deck photos (`scripts/make_currency.py`). |

## Changed beyond the deck (every item has a reason)
- **The whole first draft was replaced**, not edited — user instruction: the draft was a different game (32 generic MAKE_SET / PICK slides, engine 2026.07.16i, no art, no VO, no build script). It is kept untouched in `_draft_original/`. So a card-diff against the draft is a total replacement by design; the diff that matters is this checklist.
- **Engine = the HI02H11_L02_S02 engine (2026.08.04b-r4-unified)** + this game's money modules — user instruction ("layout, buttons, animation, colors, typography — same as HI02H11"). The train modules it carries are inert (never mounted).
- **Auto-advance disabled for this card** (engine AUTO_ADVANCE_FROM=5 would press आगे for the child) — the deck asks "Arrow appears for next screen" on every screen.
- **A 4th phase gate before the shop game** (D6): title «खरीदारी का खेल!», VO «चलिए, अब खरीदारी का खेल खेलते हैं!» — authored, the deck gives no wording.
- **Instruction OST on the practice screens** «₹25 बनाइए।», «₹35 बनाइए।», «₹5 बनाइए।», «₹17 बनाइए।» — the deck says "replace the instruction OST with the equation" but never writes the instruction; the pattern is its own p9/p11 «₹14 बनाइए».
- **Toffee ₹5 screen** (D5): prompt «परी को ₹5 की टॉफ़ी लेनी है। ₹10 के नोट और ₹1 के सिक्कों से ₹5 बनाइए।», done «शाबाश! पाँच ₹1 के सिक्के — कुल मिलाकर बने ₹5। अब परी टॉफ़ी खरीद सकती है।», ₹10-note line «₹10 का नोट ₹5 से ज़्यादा है।» — authored in the deck's pattern.
- **Ladder lines for every reachable total**, not just the deck's one example per screen (e.g. «कुल ₹21 हुए। ₹25 बनाने के लिए ₹4 और चाहिए।»), same template — a ₹10 can be dropped at ₹20–₹24, not only at ₹20.
- **Shop text the deck does not write:** praise lines for गाजर / टमाटर / संतरे / खीरे (D3); «<item> की कीमत <N> रुपये है। <N> रुपये बनाइए।» for all 8 (the deck gives सेब only); the 34 decomposition lines (every note/coin split of every price); the complete screen «शाबाश! परी की सारी खरीदारी हो गई।», «खरीदारी की सूची», «कुल ₹284», «बहुत बढ़िया खरीदारी!» (the mockup's English "Shopping List / Total / Great Shopping!").
- **Celebration VO** «शाबाश! आज आपने ₹10 और ₹1 से राशि बनाना सीखा।» — the engine's end screen needs one; the deck has none.
- **Spoken form of ₹:** every «₹N» is SPOKEN as «<N in words> रुपये» (the deck's own spoken form, «चौदह रुपये बनाइए») and «—» is spoken as a pause-comma (the TTS model truncates at «— short word»). Shown text keeps ₹ + digits.
- **Per-drop "Positive VO"** (S11) is a short positive chime, not a spoken line — a line on every drop would talk over the next drop.
- **Shop idle reminder capped at 3 per visit** to the stall, so it cannot nag forever.
- **Coin back faces** generated from the deck's own photos (D9).
- **Art:** Pari ×3 poses (redrawn from the SME's landing mockup), 14 item pictures — Gemini, flat-vector.

## Receipt (verify_bundle.py --delivery), verbatim counts line
`17 pass · 3 FAIL · 7 warn`
- FAIL *Built on the CURRENT unified engine — got 2026.08.04b, expected 2026.07.16i* — deliberate: the user named HI02H11's engine as the baseline; 07.16i is the maths factory's.
- FAIL *CSS token --bg:#FAF7F1* — the reference engine uses #F2F7FA (the r4 DESIGN_SYSTEM question background); kept identical to HI02H11.
- FAIL *Engine UI assets: celebrate.gif, hint.gif, talking.gif, tryagain.gif, start_mascot.png, start_btn.png* — none of the six is referenced by either this HTML or HI02H11's; the checker pattern-matches dead code (`_swApplyPose_dead`). The dist smoke test shows 0 × 404.
- WARN pick-dominates / speak-word / count-VO / hint / reveal — the checker does not recognise MONEY_BUILD / SHOP_GAME as produce mechanics and looks for roles these modules do not use; benign.
- Mechanics: `scripts/_drive.py` — **36/36 PASS** on the working build and on the dist copy (wrong → wrong → right on every interactive screen, real pointer drags, 0 console errors, 0 × 404). Synthetic pointer events in headless Chrome — a human touch test on a device is still needed.
- Dist: `dist/MTG2A04_L01_S01/` **9.74 MB** (WebP q85, Opus 16 kbit/s mono speech).

## EAR-CHECK (a human must listen before delivery)
- All **147** VO clips are Gemini TTS (voice **Leda**, same as HI02H11); 147/147 generated first pass, no fallback voices, no truncation flagged (duration vs text length). Listen at least to the longest: `vo_landing`, `vo_g2_done`, `vo_p1_done`, the `vo_m_det_*` set.
- `vo_pt_tutorial / guided / practice` are the reference lesson's recordings, copied unchanged.
- The dist re-encode is Opus 16k — clip lengths verified identical; listen to one or two on a device speaker.

## Observations — noticed, NOT changed (the game was left exactly as the deck specified on these)
- **Register mix kept (D4):** तुम forms ship next to आप — «चलो, अब तुम रखो।», «अब एक रुपए का और सिक्का रखो।», «सिक्के को ऊपर ट्रे में रखो।», «अब तुम एक और ₹10 का सिक्का रखो।», «…और बनाओ।» (4 tolerance lines), «चलो, ₹10 और ₹1 से हर चीज़ की राशि बनाते हैं।». The phase-gate clips are आप. Also «रुपए» (p9 VO4/VO6) vs «रुपये» everywhere else.
- **Team coin art vs the deck (row 16):** the team's coin fronts show the year 2013 and no SPECIMEN; S2/S4 ask for "000" + SPECIMEN on all currency. Used as supplied per D9.
- **«5 / 5»** on the completion card is a visible count; the house rule bars scores — it is a list count, shipped as the deck asks.
- **Mastery length:** 8 purchases × (select + build + check) is long for Grade 2; the deck's own mockup is 8/8.
- **The deck's S22 dev note** (red-in-tray over rule, idle VO) is superseded by D1 — noted so nobody implements both.
- **S1's mockup** shows an arrow start button; the reference lesson's play button is used (baseline instruction).
- **Production Tracker** not updated — no tracker file was provided.

## Round 2b — team art + dev navigator (user, 2026-09-29)
| # | Ask | Status | Proof |
|---|---|---|---|
| B1 | Use the new team images; crop the multi-object sheets, rename, use | ✅ | `scripts/import_team_art.py` splits the sheets on their transparent columns → obj_copy / chips / chocolate / plates / toffee / juice / apple / bananas / carrots / tomatoes / grapes / oranges (12, replacing the Gemini versions). Sources moved to `assets/Team_art_source/`. |
| B2 | Landing scene (title painted in) | ✅ | `CARD.landing_scene` → the landing card IS the painting (1040×574, not cropped), start button on its bottom edge like the SME's p1 mockup; the engine title kept for screen readers only. |
| B3 | Market scene (Pari with list at the market) | ✅ | p7 MONEY_SCENE now shows `scn_market` (framed card). `pari_list` is no longer used. |
| B4 | `?dev=1` slide navigator as in HI02H11 | ✅ | Already present (the engine is HI02H11's): ⌂ landing · ⏮ · ◀ · dropdown · ▶ · ⏭ + live "n/14 · id". Added: each dropdown entry names its deck page + content (`dev_label`), e.g. «6. G2 · p9 · कॉपी ₹14 (teach)». Verified on the working build and on dist. `?slide=N` (0-based) also opens screen N directly. |
- Not in the team set → still Gemini art: **obj_cucumbers, obj_mangoes** (flatter style than the new glossy items), Pari with basket / full basket (shop game).
- Dist re-checked: 9.89 MB (item art capped at 400 px, scenes 1280 px — 2× their largest on-screen size); `_drive.py` 36/36 on build and dist. Receipt `17 pass · 3 FAIL · 7 warn` (same 3 deliberate FAILs as above).
- `_review_shots/` + the round-2 review deck still show the round-2 art — re-capture if the SME needs the new pictures.

## Round 2c — user review (2026-09-29)
| # | Ask | Status | Proof |
|---|---|---|---|
| C1 | Remove SPECIMEN text from the coins | ✅ | `make_currency.py` no longer stamps the two generated coin BACKS (the team's coin fronts never had it). The note keeps its own printed SPECIMEN (team art). The ₹10 coin back still reads «000» where the year was. |
| C2 | Tap screens (p2 ₹10, p3 ₹1): no tick on the correct card | ✅ | `.mn-card.mn-ok::after{display:none}` — green + glow + confetti stay; shot checked. Applies to both MONEY_PICK screens. |
| C3 | Pari's list (p5): better cards, one by one, item picture + name + price on the right; highlight each card as the VO plays when it repeats on inactivity | ✅ | Rows = picture tile · name · yellow price tag; each row appears AT its VO cue and lights while named. The 🔊 replay and the engine's 7 s inactivity replay light them in turn with all rows staying visible (measured: opacities all 1.00 during replay). Entrance + highlight are transitions — a keyframe version re-hid rows on every highlight change. |
| C4 | Copy ₹14 (p6): only the NOTE auto-placed; the child drags every coin | ✅ | Demo coin removed; the child places four ₹1 (the 3rd coin reuses «अब एक रुपए का और सिक्का रखो।» — no new VO). drive: `G2 demo placed ONLY the ₹10 note`, `G2 child places 4 coins -> ₹14 finished`. |
| C5 | Build screens p6–p11: the uploaded layout; note + coin centred in the tray | ✅ | Item name above the picture (no card), yellow price tag, dashed drop zone with कुल top-right, full-width cream coin tray with the money centred; juice's «हो गया» sits at the tray's right end and its total moved to the same top-right place (layout identical on all six). Placed money enlarged. |
- Checks: `_drive.py` 36/36 on build and dist · dist 9.89 MB · receipt `17 pass · 3 FAIL · 7 warn` (the same 3 deliberate FAILs).

## Round 2d — user review (2026-09-29 evening)
| # | Ask | Status | Proof |
|---|---|---|---|
| D-1 | New cover + Pari-in-the-market images | ✅ | (cover replaced again by the 11:37 PM version — Pari on the RIGHT, Swiftie back bottom-LEFT, override removed) `import_team_art.py` maps the cover → `scn_landing`, the 10:34 PM market → `scn_market`. The new cover paints Pari bottom-LEFT, so on the landing Swiftie + her audio chip moved to the bottom-RIGHT corner (otherwise she stands on Pari's legs). |
| D-2 | Juice (page 11): remove «हो गया», same as the other build screens | ✅ | Juice completes by itself at ₹17. **Reverses decision D2** (the deck's S13 mockup + S15 note). The 14 «अभी कुल ₹X हुए हैं…» clips it used were pruned. drive: `P3 has no check button`, `P3 -> ₹17 finished by itself`. |
| D-3 | Completion (page 12): page-5 list, every card green + tick, celebrating Pari exactly like the screenshot | ✅ | Pari (`pari_celebrate`) redrawn by Gemini from a crop of the user's screenshot (same pose, fists up, eyes closed, foot kicked back); rows = picture · name · price tag · green ✓, arriving one by one with a pop, then confetti. The deck's «5 / 5» count is dropped (not in the user's mockup). drive: `P4 5 green rows with ticks, all shown`, `P4 celebrating Pari`. |
| D-4 | Build screens: picture + price tag in a card, no name text | ✅ | Light card (`#F7FBFF`, blue border) around the item picture + yellow tag; the name is kept only as the image's alt text. |
- Bug found + fixed in the same round: the completion screen's new root class `.mn-done` collided with the build screens' solved-target class and collapsed every solved drop zone to 8 px — renamed `.mn-fin`.
- Checks: `_drive.py` 37 checks, 0 FAIL on build and dist · dist 9.75 MB · receipt `17 pass · 3 FAIL · 7 warn` (the same 3 deliberate FAILs).

## Round 2e — user review (2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| E1 | Build screens: glow instead of pulse on the note/coin (can't drag while it pulses) | ✅ | Currency hints are a filter-only glow (`mn-hintglow`); on the teach screens the coin the child must place glows from the moment it becomes draggable until it is dragged. (Drags were refused during the pulse because the pulse ran while Swiftie spoke — the engine blocks drags during VO.) drive: `G2 waiting ₹1 coin GLOWS (no pulse) and is draggable`. |
| E2 | Only the drop zone + its money go green; not the coin tray / item card | ✅ | Item card no longer turns green; the equation strip keeps the tray's cream/orange. drive: `G2 item card NOT turned green`, `…tray colours (not green)`. |
| E3 | "Page 17": heading empty for 2–3 s on entry | ✅ (read as page 7, chips ₹20 — there are 14 screens) | The heading was held back until the 2nd VO line (deck S10 wording); it now shows at once. drive: `G3 heading shows at once`. |
| E4 | Pages 6–7: price tag pulse when the VO says the amount | ✅ | Tag pulses with VO1 on copy + chips. drive: `G2 price tag pulses with VO1`. |
| E5 | Pages 8–11: no equation in the heading; keep «₹X बनाइए।» | ✅ | `eq_in_band` off; the equation shows in the tray strip only. drive: `G4 … heading stays «₹25 बनाइए।»`. |
| E6 | Page 10 (toffee, ₹1 only): coins centred in the drop zone on both axes | ✅ | Empty tens row no longer reserves space; symmetric inset. Applies to every build screen. drive: `P2 coins centred (x, y offset ≤ 3 px)`. |
| E7 | Wrong currency: drop zone shakes, currency bounces back | ✅ | `mn-shake` on the target + spring-back to the tray. drive: `G3 wrong drop shakes the drop zone`. |
- Checks: `_drive.py` 0 FAIL on build and dist · dist rebuilt.

## Round 2f — mastery shop redesign (user, 2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| F1 | Use the new 6-panel shop image; 6 items, prices 14 · 25 · 35 · 42 · 60 · 65 ascending | ✅ | `shop_stall.png` (team art, cropped); items सेब ₹14 · संतरे ₹25 · टमाटर ₹35 · अंगूर ₹42 · खीरे ₹60 · आम ₹65, one per panel (positions measured off the art). केले ₹20 + गाजर ₹23 dropped; their 10 clips pruned. The builder asserts the prices are ascending. Complete-screen total now ₹241. |
| F2 | Improve or remove the 0/8 counter | ✅ removed | A bought item's panel turns green with a ✓ and is disabled. |
| F3 | Make screen = the page-6 layout: item card left, drop zone right (no total), tray with ₹10 note + ₹10 coin + ₹1 coin, no Pari, no Undo (drag back instead), «जाँचें» in place of the arrow | ✅ | drive: `no Pari, no undo, no running total`, `tray has ₹10 note, ₹10 coin, ₹1 coin`, `जाँचें in the arrow's place`, `drag-back returns the coin + re-activates ₹1`. Tap-to-add and tap-to-return still work too. After a purchase the item card jumps and the stall returns with that panel ticked. |
- Checks: `_drive.py` 0 FAIL on build and dist.

## Round 2g — shop: drag-only + one-time drag-back tip (user, 2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| G-1 | A tap must NOT put currency in the drop zone — drag and drop only | ✅ | Shop tap-to-add removed (pages 6–11 never had it). ⚑ Overrides deck S18 «Currency को tap या drag किया जा सकता है». drive: `M1 a TAP on currency does not add it`. |
| G-2 | No Undo button → teach drag-back (user chose option 3 of 4 discussed) | ✅ | (round 2h: the wiggle became a GHOST of the piece travelling drop zone → tray, exactly 2 times, during the line) The first piece the child places in the shop shows the way back while Swiftie says «कोई पैसा हटाना हो, तो उसे वापस नीचे खींच लीजिए।» (`vo_m_tip`, 3.7 s, Leda). Once per game; waits for any clip already playing; no hand (practice rounds). drive: `tip spoken + wiggle`, `tip is NOT repeated`, `never spoken again on later items`. |
| G-3 | (follows from G-2) tap-to-return removed too | ✅ | Dragging is the only way money moves, both ways — a tap on a placed coin does nothing. ⚑ Overrides deck S18 «रखे हुए पैसे पर tap करके उसे वापस कर सकता है» and «Undo button भी उपलब्ध रहेगा». A wrong जाँचें still returns everything to the tray. drive: `a TAP on a placed coin does nothing`, `drag it back out -> tray empty`. |

## Round 2i — transition screens (user, 2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| I-1 | Transition feels too long; trim the Swiftie animation — she peeks ONCE | ✅ | `scripts/make_gate_bird.py` splits the 84-frame / 8.6 s `swifty_gate.webp` into `gate_peek.webp` (one continuous rise, frames 0–19 + 36–53, ~1.5 s, plays once — the half-way pause and the second rise are cut), `gate_talk.webp` (mouth open/close loop) and `gate_rest.webp` (mouth closed). |
| I-2 | Then the text is written | ✅ | Title hidden during the peek, then written in with a left-to-right wipe (Devanagari-safe: no split clusters). |
| I-3 | VO syncs with her mouth | ✅ | The talk loop is shown only while the gate VO is actually sounding and swaps to the closed mouth on the clip's end; the next screen opens 0.45 s later. Traced live (real audio): peek 0 → 1.55 s silent · talk + VO 1.55 s → VO end · rest · next screen. All four gates (start, guided, round 3, shop) use it. The old fixed 3.8 s "talk_at" start is gone. |
- Gate length now = 1.5 s + the VO: guided gate 7.7 s (its VO is 5.6 s), shop gate 4.7 s. The tutorial/guided/practice VO clips are the reference lesson's recordings (5.6 / 5.6 / 2.5 s) — re-recording shorter lines would shorten those gates further.
- Dist 9.01 MB (the 1.5 MB old bird no longer ships). `_drive.py` 0 FAIL on build and dist.

## Round 2j — celebration GIF (user, 2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| J-1 | Use the team's Swiftie GIF on the last celebration screen, exactly as it is — background included | ✅ | `assets/UI/Swiftee-end page gif.gif` copied to `end_swiftee.gif` (URL-safe name, same bytes) and shown in place of the stock celebrating mascot, 560 px wide. Its background (a checkerboard baked into the frames) is kept; **not edited in any way — standing user instruction**. `dist/` ships it byte-identical (`cmp` checked). |
- To keep dist under 10 MB with the 2.2 MB GIF: the stock celebrating mascot (no longer shown) is not shipped; `gate_peek/talk` re-encoded at q72; the landing Swiftie animation re-encoded at q72 in dist only (checked side by side, no visible difference). Dist 9.67 MB. `_drive.py` 0 FAIL on build and dist.

## Round 2k — user review (2026-09-30)
| # | Ask | Status | Proof |
|---|---|---|---|
| K-1 | Transition title: first letter cut | ✅ | The write-in wipe clipped at the text box edge, and the title's outline stroke sits just outside it (the «च» of «चलिए»). Wipe box widened 12 % on both sides. Screenshot checked on the start gate. |
| K-2 | New sfx for the play button and the next button | ✅ | `swiftpal_sfx_3_play_button.wav` → `sfx_play_button.ogg` (landing ▶); `swiftpal_sfx_4_next_button.wav` → `sfx_next_button.ogg` (the आगे arrow + the celebration arrow). Only on a real, enabled press. Dist keeps sfx at 64 kbit/s (voice stays 16k). Verified: ▶ → play sfx, arrow → next sfx, disabled arrow → nothing. |
| K-3 | Page 9 (₹35): the कुल chip overlaps the notes | ✅ | Tray content nudged 24 px down on this screen only. drive: `P1 three notes do not overlap the कुल chip`. |
| K-4a | Shop: other items instead of खीरे and आम | ✅ | केले ₹60 and गाजर ₹65 (team art; prices still ascending). 4 new clips (select + praise), Leda. |
| K-4b | Shop: after a purchase, some sections sometimes not clickable | ✅ | Cause: a tap on the stall was ignored whenever ANY clip was playing (the idle reminder, the tail of a praise line). A tap on an unbought item now stops that clip and opens the item. drive: `an unbought item is tappable even while a line plays`. |
| K-5 | No dragging while the drag-back tip plays | ✅ | Tray pieces and placed pieces are locked for the length of «कोई पैसा हटाना हो…». drive: `no drag while the tip is speaking`. |
| K-6 | Celebration button = HI02H11's (size + placement) | ✅ | Arrow-only pill (label moved to aria-label, as the reference ships it), 134 × 88, 22 px below the mascot; the team GIF sized to the reference mascot's 358 px height so the button lands on the same spot. Measured in both builds. GIF itself unchanged (dist `cmp` identical). |
- Checks: `_drive.py` 59 checks, 0 FAIL on build and dist.
