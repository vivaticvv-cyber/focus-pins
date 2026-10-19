# FOCUS ops status

**Updated:** 2026-10-19 14:30 UTC (Grok)

## DONE: pins_batch 262–311
- Autopilot #21: all remaining 30 rows merged via auto-pad
- pins.csv = **311** строк
- batches/: 6, 6b, 6c, 6d, 6e present

## Permanent resilience (in merge_batch.py)
1. Auto-pad description 20–299 → ≥300
2. Independent per-file merge (one bad file does not block others)

## Images policy
- Keep published pin images in repo for now (needed for recycle/republish, Buffer history, quality review)
- Binary images do NOT inflate AI tokens when reading code/CSV
- Soft GitHub soft limit ~1–5 GB; current scale is fine
- Later (when >500 images or slow clones): archive old published to `images/archive/` or external storage; do not delete without recycle decision

## Automations
FOCUS daily ops check active (04:30 Kyiv)

## Next
1. social_batch (increase FB/X via Buffer)
2. Monitor first generated images for ADHD tone
3. Optional: image archive policy after ~3 months stock

## Questions to Claude
- None
