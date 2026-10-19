# FOCUS ops status

**Updated:** 2026-10-19 ~18:50 Kyiv (Grok)

## STATUS: DONE (orchestration)

### Done 19.10
- pins.csv = **311** (ids 262–311 merged; Autopilot #21)
- merge_batch: auto-pad short descriptions + independent per-file merge
- publish.py: **STOCK_DAYS=5**
- social_publish.py: Buffer FB/X **every free day** (SKIP_BUSY_DAYS keeps Metricool/Typefully days free)
- Root cleaned of merged pins_batch_5/6/6a–e/7
- Automations: 04:30 daily ops; 04:45–07:00 hourly continue if STATUS:TODO

### In progress (Actions, no owner)
- Daily pins #39 queued (stock_days=5) — generate images for status=new
- Image max id was ~208; need 209–311 over successive Daily runs (GEN_MAX_PER_RUN≈12)

### Counts (approx)
- pins: 311 total — published ~60, scheduled ~3, ready ~61, **new ~187**
- social: ~62 rows — ready ~58 (FB+X); denser Buffer will consume faster

## Next (Grok)
1. After Daily: verify new images appear; keep stock ≥5 days
2. social_batch — more FB/X ready posts for denser Buffer
3. Quality check ADHD tone + image/text match on new pins

## Questions / tasks for Claude
1. **Metricool:** prepare M021–M050 (Dec–mid Jan) if not already in pipeline
2. **Typefully:** keep ~10/mo X schedule aligned
3. **external_posts.csv:** refresh from live Metricool/Typefully calendars (weekly) so Buffer SKIP_BUSY_DAYS stays accurate
4. Product-pin SPECS / promo strategy only if owner requests

## Permanent rules (reminders)
- Push batches in ≤10-row chunks; validate lengths after push; never overwrite pins.csv/social.csv wholesale
- ADHD tone always: no shame, one small step, trial/product links soft
- Heavy work = GitHub Actions cloud; Grok = CSV + monitor + ops
