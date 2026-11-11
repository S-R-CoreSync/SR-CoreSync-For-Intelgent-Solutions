# Roll-out kit — closing the English residue in 21 languages

**Status (2026-11-11 19:04):** German is at its baseline: 70 → 17 blocks, 1,092 → 187
words, and the 17 that remain are brand names, product names and the emblem
caption — nothing translatable.

Dutch sits at 21 blocks, Sorani Kurdish at 15. The other 21 languages share one
identical set of **82 blocks / 1,325 words**, inherited from a single template.

## Why one language at a time

The 82 blocks are *visually* identical but *textually* must be written in each
language. There is no translation that serves German, Greek and Maltese at once.
What is shared is the workflow, not the words.

## Per-language loop (about 20 minutes each)

```bash
# 1. see what is still English on that page, longest first
python scripts/i18n_scan_english.py --lang it --csv docs/i18n-en/it.csv

# 2. write the map: english -> italian  (JSON, keys exactly as in the CSV)
#    docs/i18n-en/it.map.json

# 3. apply it tolerantly (survives &amp; , line breaks and inline tags)
python scripts/apply_text_map.py --lang it --map docs/i18n-en/it.map.json

# 4. re-measure: the number must drop
python scripts/i18n_scan_english.py --lang it

# 5. gates
node scripts/validate.js
python scripts/audit_language_purity.py
python scripts/check_site_links.py .
```

Commit per language: `i18n(it): batch one — N blocks`.

## Order that costs least

1. `nl` (21 blocks) and `ckb` (15) — nearly done, cheapest to close.
2. `es`, `fr` (72 each) — the big European markets.
3. The remaining 19, two per session, in the order sales cares about.

## What must never be translated

- `S&R CoreSync For Intelligent Solutions`
- `S&R CORESYNC`
- Product names: `S&R TaxSync Desktop`, `S&R CloudPOS Connector`,
  `S&R FlowScan AI Mobile`, `S&R Financial AI SDK`, `S&R SecureVault B2B`,
  `S&R Cloud Terminal Agent`, `S&R CivicSync™`, `S&R HealthBridge™`,
  `S&R OmniBakery™`
- `Official Corporate Emblem` only stays English inside the emblem caption;
  elsewhere it is prose and should be translated.

## Guard rail

`scripts/check_content_depth_parity.py` reports English FAQ leakage per language.
After a language reaches zero, add it to the `--strict` allow-list, and when the
whole set is clean, flip the CI step from report to blocking.
