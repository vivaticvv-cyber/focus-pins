# FOCUS ops status

**Updated:** 2026-10-24 ~04:50 Kyiv (Grok insurance)

## STATUS: IN PROGRESS

### Daily run 24.10
- Auto-status fresh, Actions green
- social_batch_2.csv still in root (ids already in social.csv, merge skips)
- M images: M021–M026 stocked; ~14 new remaining
- Triggered Autopilot #35 to move batch + stock next 6 images
- Pins quota met (366), runway 33d normal

### Current numbers (auto-status 24.10 01:40 UTC)
- pins.csv: **366** (new 208, ready 66, scheduled 6, published 86)
- Info runway: 214 (~to 26.11), **33 days** → normal (>21)
- Promo runway: 60 (~to 25.11)
- Social: S ready 20, SX ready 18, M ready 26 + new 14 (images stocking)
- Pad=0, shifted=0, reject=0
- Root waiting: social_batch_2.csv

### Next batch due: 2026-10-28
Quota met for 04.11. Next weekly ~52 info + 15 promo from 28.10.
MAX_PER_DAY = **10**.

### Gumroad (verified 22.10)
- Access token working (view_sales confirmed).
- Paid sales: **0**
- Free trial (FOCUS Mini / dwshkr): **1** download
- Products: Soft Structure, seqen, Premium Pack, Mini — all present
- metrics.md can now be filled automatically by Grok

### STATUS rules (help-6 §4)
1. STATUS: DONE = last cycle 0 rejects **and** weekly quota met; else IN PROGRESS with remainder.
2. Always include `Next batch due: <date>` + stock numbers from auto-status.
3. Never use word «Idle».

### Automation
- FOCUS daily ops check (04:30 Kyiv) — weekly quota + 21-day threshold.
- FOCUS batch continue 04:45–07:00 — insurance.
- Gumroad sales pull — available to Grok on demand / daily.

### NEED OWNER
- None.
