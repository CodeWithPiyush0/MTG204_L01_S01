# MTG2A04_L01_S01 — «परी की पिकनिक की खरीदारी» (round 2)

Grade 2 Maths · Money · **represent an amount up to 99 with ₹10 and ₹1**.
Built to the SME deck `MTG2A04_L01_S01_review.pptx` on the look of HI02H11_L02_S02 (same engine,
buttons, frames, colours, type, Swiftie, gates, celebration). **Read `CHANGES.md` first**: it holds
every ask in the deck as a numbered row with its status and evidence, the decisions taken (D1–D9),
what was added beyond the deck, and the open observations.

## Flow (14 screens)
Landing → *gate* → recall ₹10 & ₹1 → identify ₹10 → identify ₹1 → market → *gate* → Pari's list →
copy ₹14 (teach) → chips ₹20 (teach) → chocolate ₹25 (guided) → *gate* → plates ₹35 → toffee ₹5 →
juice ₹17 (हो गया) → list complete 5/5 → *gate* → mastery shop (8 items, जाँचें) → celebration.

## What is where
| path | what |
|---|---|
| `MTG2A04_L01_S01.html` | the working build (serve over HTTP) |
| `dist/MTG2A04_L01_S01/` | **the delivery copy**: `index.html` + optimised assets, 9.7 MB |
| `card.json` | generated — never hand-edit |
| `scripts/build_skill_MTG2A04_L01_S01.py` | **all content lives here** (every Hindi line, prices, ladders) |
| `engine/lesson_template.html` | this game's engine copy (the HI02H11 engine + injected money modules) |
| `engine/money_modules.js`, `money_styles.css`, `inject_money.py` | the money module set and its injector |
| `assets/Currency/` | the team's currency set (source; copied into `assets/Images/` unchanged) |
| `scripts/make_currency.py`, `gen_money_art.py` | currency copy + coin backs; Pari / item art (Gemini) |
| `scripts/make_dist.py` | builds `dist/` |
| `scripts/_drive.py`, `_shots.py`, `_gates.py` | dev checks: mechanics driver, screenshots, gate test |
| `_review_shots/`, `MTG2A04_L01_S01_round2_build_review.pptx` | page-by-page review deck for the SME |
| `_draft_original/` | the SME's first draft, untouched |

## Rebuild
```bash
PYTHONUTF8=1 python engine/inject_money.py              # only after editing engine/money_*
PYTHONUTF8=1 python scripts/build_skill_MTG2A04_L01_S01.py
# changed a line? the builder deletes exactly the clips whose text changed; re-record just those:
export GEMINI_KEY=...   # from .env (GKEY)
PYTHONUTF8=1 python <revise-skill>/scripts/gen_tts.py card.json --voice Leda --ext ogg
PYTHONUTF8=1 python scripts/build_skill_MTG2A04_L01_S01.py   # again, to measure the new clips
PYTHONUTF8=1 python scripts/make_dist.py
DIST=1 PYTHONUTF8=1 python scripts/_drive.py <outdir>          # smoke-test the delivery copy
```
Serve with `python -m http.server` from this folder (or from `dist/MTG2A04_L01_S01/`).
