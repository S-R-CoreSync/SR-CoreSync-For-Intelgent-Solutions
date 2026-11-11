# Roll-out kit — closing the residue, language by language

**Status (2026-11-11, v19):** the FAQ residue is gone. Every one of the 27
non-English portals answers all 15 questions in its own language
(`check_content_depth_parity.py`: `faq EN = 0` everywhere, 27/27).
The 22-language wave wrote 196 question/answer pairs through
`scripts/portal_faq_locales.json` + `scripts/apply_faq_locales.py`.

What is left is not copy, it is a component: the interactive **estimator** is
installed on `de` and `ckb` only. `de` is fully translated (55/55 labels, no
booking button, no dead control). `ckb` still carries the **Arabic** labels and
a `transferEstimatorToVipBooking` button that opens nothing, because that page
has no `executiveBookingModal`.

## `ckb` first, then the other 24

Either give `ckb` the 55 Sorani labels and drop the booking button, or remove
the Arabic block from the Kurdish page until the labels exist - an Arabic
calculator on a Kurdish page is worse than no calculator.

## The estimator, one language at a time

```bash
# 1. fill the 55 labels for that language (de is the reference, complete)
#    scripts/portal_estimator_locales.json -> {"xx": {"<arabic label>": "<translation>"}}
python scripts/install_estimator.py --lang xx --dry-run   # must print 0 labels missing
python scripts/install_estimator.py --lang xx
python scripts/check_content_depth_parity.py              # estimator > 0
python scripts/audit_language_purity.py
```

**Blocker to close before scaling to 25 languages:** `js/sr-estimator.js`
composes the WhatsApp enquiry in Arabic inside the code
(`bookEstimatorViaWhatsApp`), and falls back to `"5 - 7 أيام عمل"` for the
duration. Today the damage is confined to `ckb` and the Arabic master, but the
first new language ported will send an Arabic enquiry in its own name.
The Arabic-containment gate cannot see it: it reads page text, not JS strings,
and it exempts languages written in Arabic script.
Move the eight message segments into `portal_estimator_locales.json` under
`whatsapp`, pass them as `data-*` on the widget root, and fall back to English.

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
estimator per language. Its only remaining drift is the estimator; once that
reaches every language, drop `continue-on-error` from the CI step and add
`--strict`.
