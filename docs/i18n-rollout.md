# Roll-out kit — closing the residue, language by language

**Status (2026-11-18, v20):** the residue is closed. Every one of the 28
non-English portals carries the full localisation stack in its own language:
15 FAQ answers, the interactive estimator (16 components per page, master
parity confirmed by `check_content_depth_parity.py` — `PASSED`, 28/28), and
the wave-2 pricing regions. The checklist below stays as the kit for future
languages.

The estimator blocker described in v19 is resolved, using exactly the
mechanism this file prescribed:

1. `js/sr-estimator.js` declares `_estimatorState` itself, initialises it
   from `localStorage` and recalculates on load - no page-side globals
   needed (only the Arabic master keeps its own inline implementation);
2. every WhatsApp string comes from `data-wa-*` attributes on the widget
   root (title, type, scope, pay, duration, days, total, speed, lang) -
   the shared module holds no per-language literals; the wave scripts
   author those attributes per language;
3. the whole grid is installed per language, and the CI step
   (`check_content_depth_parity.py --strict`) is blocking - the
   `continue-on-error` era described below is over.

For the record, the v19 state (kept until 2026-11-17): the estimator lived
on `de` and `ckb` only, `de` was never functional (options without
`_estimatorState`, first click threw ReferenceError), and the WhatsApp
message was composed in Arabic inside the shared module. Phase 201
replaced all of it; do not follow the historical instructions below on the
current fleet.

## The estimator, one language at a time (historical loop - fleet complete)

```bash
# 1. fill the 55 labels for that language
#    scripts/portal_estimator_locales.json -> {"xx": {"<arabic label>": "<translation>"}}
python scripts/install_estimator.py --lang xx --dry-run   # must print 0 labels missing
python scripts/install_estimator.py --lang xx
python scripts/check_content_depth_parity.py              # estimator > 0
python scripts/audit_language_purity.py
```

**Former blocker (closed in phase 201):** the shared module used to have no
state of its own and composed the WhatsApp enquiry in Arabic inside the code.
The containment gate could not see it: it reads page text, not JS strings, and
it exempts Arabic-script languages. The fix landed exactly as prescribed here -
the module state moved into `js/sr-estimator.js` with `localStorage`
persistence, and the message segments became `data-wa-*` attributes authored
per language on the widget root (the wave scripts carry them alongside the 55
labels). The gate now covers the result: language purity is 100% across the
fleet.

## Per-language loop for ordinary English blocks

```bash
# 1. see what is still English on that page, longest first
python scripts/i18n_scan_english.py --lang it --csv docs/i18n-en/it.csv

# 2. write the map: english -> italian  (JSON, keys exactly as in the CSV)
#    docs/i18n-en/it.map.json

# 3. apply it tolerantly (survives &amp; , line breaks and inline tags)
python scripts/apply_text_map.py --lang it --map docs/i18n-en/it.map.json --all

# 4. re-measure: the number must drop
python scripts/i18n_scan_english.py --lang it

# 5. gates
node scripts/validate.js
python scripts/audit_language_purity.py
python scripts/check_site_links.py .
```

Commit per language: `i18n(it): batch one — N blocks`.

## What must never be translated

- `S&R CoreSync For Intelligent Solutions`
- `S&R CORESYNC`
- Product names: `S&R TaxSync Desktop`, `S&R CloudPOS Connector`,
  `S&R FlowScan AI Mobile`, `S&R Financial AI SDK`, `S&R SecureVault B2B`,
  `S&R Cloud Terminal Agent`, `S&R CivicSync™`, `S&R HealthBridge™`,
  `S&R OmniBakery™`
- Legal/technical tokens: `Belastingdienst`, `KvK`, `btw-nummer`, `GDPR`, `NDA`,
  `iDEAL`, `SEPA`, `Stripe`, `Mollie`, `PayPal`, `TLS 1.3`, `AES-256`
- `Official Corporate Emblem` only stays English inside the emblem caption;
  elsewhere it is prose and should be translated.

## Guard rail

`scripts/check_content_depth_parity.py` reports English FAQ leakage and the
estimator per language. Since phase 201 every language matches the master, and
the CI step runs it as `--strict` under the name "Content parity inside the
sections (blocking)" - there is no `continue-on-error` left to drop. Keep it
that way: any new component must reach all 28 portals in the same wave, or the
gate fails the build.
