# MTG2A04_L01_S01 -- परी की पिकनिक की खरीदारी (Representing amount with Rs.10 and Rs.1)

**Grade:** G2 · **LO:** MTG2A04_L01 · **Attribute:** A04 (Measurement / Money) · **Type:** CORE

**Mastery bar:** Can represent amount up to 99 using Rs.10 and Rs.1.

**Slides:** 32 · Tutorial 6 / Guided 7 / Practice 19

## Story flow (revision 2, per SME brief 2026-09-22)
Landing (परी की पिकनिक की खरीदारी) -> quick recall (teach then test: name and identify the Rs.10 note / Rs.10 coin / Rs.1 coin) -> Pari reaches the market -> shopping list overview -> one full autonomous worked example (कॉपी, Rs.14) -> guided practice (चिप्स Rs.20 notes-only, चॉकलेट Rs.25 coins+coins) -> independent practice (प्लेटें Rs.22, टॉफ़ी Rs.5 coins-only edge case) -> mastery shopping game (5 new items: जूस, बिस्कुट, केक, नैपकिन, पानी की बोतलें).

## Three adaptations made against the original brief (all disclosed, all reversible)
1. **No flexible mixed-denomination builder in this engine.** Every item is decomposed into up to two MAKE_SET steps (tens, then ones -- a step is skipped when that denomination's count is 0). The brief's free-mix-then-submit ('हो गया') flow is written up as a mechanic SPEC below for the dev team; nothing here blocks adopting it once it exists -- the amounts, items and story stay identical.
2. **Recognition feedback uses the engine's standard buzz+X+lock** (not a plain bounce-back) -- SME's explicit choice when this was raised.
3. **Recall is taught once (autonomous, T1-T3), then tested once (guided, G1-G2)**, instead of taught-and-tested in the same interactive screens as originally sketched. This was needed because the kit's locked 3-phase contract requires tutorial-phase content to be fully autonomous and never a test, and phase order is fixed (tutorial -> guided -> practice). Same visuals, same instruction language, same feedback style -- just a teach pass before the test pass, which also happens to match this kit's own 'name a label before testing it' rule. **Flag this to the SME explicitly** -- it is the one content-shape change made without a separate confirmation round, easy to revert to a single combined screen if she prefers, though that would need the recall check reclassified as guided-phase content positioned before the market-arrival beat, which changes the pacing more than this option does.

## Mechanic-Diversity Gate
With the free-mix mechanic unavailable, money-construction itself is 100% MAKE_SET (produce). A 'which item costs Rs.X?' PICK check (item-icon options) was added once per shopping item across guided/practice/mastery -- it reuses the SME's own price list as quiz content, doubles as a read-the-price-before-you-build-it check, and supplies the PICK family the gate needs. Run `verify_bundle.py` for the authoritative family count.

## Mechanic SPECs for the dev team (both KIT MODE -- proposed, not built)
1. **Flexible mixed-denomination amount builder.** A produce mechanic where the tray accepts ANY mix of two (or more) differently-valued piece types, sums by VALUE not piece count, and checks against a target on an explicit submit ('हो गया') rather than auto-gating at an exact piece count. Needed for money/currency skills generally, not just this one.
2. **Persistent cross-slide progress list.** The mastery game wants a shopping list with per-item ticks and a 'moves to a bag' animation, visible across all 5 mastery items. No current module persists state across slide boundaries this way (BUILD_TO_NUMBER's skyline strip is the closest analogue, but it's wired into that module's own stage). Not attempted in this build -- each mastery item is a self-contained slide sequence instead.

## Art & VO status -- unchanged from revision 1, still ACTION NEEDED
No GEMINI_KEY in this environment. 13 objects (3 currency pieces + 10 shopping items) ship on `_emoji_fallback`; every VO line is registered in `assets.audio_text` with Hindi text ready for TTS but no `.mp3` exists yet (silent-beat fallback). Also still missing, and not attempted here since no mechanic renders them: a Pari (परी) character sprite -- only Swiftie has a dedicated on-screen mascot slot in this engine, so Pari exists in VO/prompt text only, not as a visible character -- and a market/village background scene.

## Status: 🧪 structurally built & engine-guard-verified, ART + VO PENDING, 2 mechanic SPECs open.