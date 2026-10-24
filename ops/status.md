# FOCUS ops status

**Updated:** 2026-10-24 ~04:40 Kyiv (Grok)

## STATUS: IN PROGRESS

### Daily run 24.10
- Auto-status fresh (00:40 UTC), Actions green (Daily #48, Autopilot #33, Ops report)
- Fixed social_batch_2.csv: M021–M040 status ready→new so Autopilot stocks images
- Triggered Autopilot to merge batch + start image generation
- Pins quota met, no new pins needed

### Current numbers (auto-status 24.10 00:40 UTC)
- pins.csv: **366** (new 208, ready 66, scheduled 6, published 86)
- Info runway: 214 (~to 26.11), **33 days** → normal (>21)
- Promo runway: 60 (~to 25.11)
- Social: S ready 20, SX ready 18, M ready 40 (M021–M040 waiting images)
- Pad=0, shifted=0, reject=0
- Root waiting: social_batch_2.csv (now status=new)

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
