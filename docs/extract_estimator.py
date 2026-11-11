#!/usr/bin/env python3
"""Extract the estimator into a standalone module (no page is wired yet).

The interactive estimator exists only in the Arabic and Sorani pages: its CSS
lives in inline-core.css / inline-ckb.css and its logic in the master's inline
bundle. Extracting both into js/sr-estimator.js and css/sr-estimator.css is the
first half of making it available to the other 27 languages; the second half is
the per-language markup and the 21 labels.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------- CSS: every rule whose selector mentions cost-estimator ----------
css_out = []
for src in ("css/inline-core.css", "css/inline-ckb.css"):
    text = (ROOT / src).read_text(encoding="utf-8", errors="replace")
    seen = set()
    for m in re.finditer(r'([^{}]*cost-estimator[^{}]*)\{([^{}]*)\}', text):
        selector = re.sub(r"\s+", " ", m.group(1)).strip()
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        key = (selector, body)
        if key in seen:
            continue
        seen.add(key)
        css_out.append(f"{selector}{{{body}}}")

header = ("/* S&R CoreSync - estimator module.\n"
          "   Extracted from the Arabic/Sorani sheets so every language can load the\n"
          "   same widget instead of inheriting a different one. */\n")
(ROOT / "css" / "sr-estimator.css").write_text(header + "\n".join(css_out) + "\n", encoding="utf-8")
print(f"css/sr-estimator.css: {len(css_out)} rules")

# ---------- JS: the four estimator functions from the master bundle ----------
bundle = (ROOT / "js" / "sr-inline-fa62ed13.js").read_text(encoding="utf-8", errors="replace")
wanted = ["updateEstimatorOption", "_recalcEstimator",
          "bookEstimatorViaWhatsApp", "transferEstimatorToVipBooking"]
chunks = []
for name in wanted:
    m = re.search(rf'function\s+{name}\s*\(', bundle)
    if not m:
        print("missing", name)
        continue
    start = m.start()
    depth = 0
    i = bundle.index("{", m.end())
    end = None
    while i < len(bundle):
        if bundle[i] == "{":
            depth += 1
        elif bundle[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    if end:
        chunks.append(bundle[start:end])
        print(f"js: extracted {name} ({end-start:,} chars)")

body = ("/* S&R CoreSync - estimator module (extracted from the master inline bundle).\n"
        "   Exposes the four handlers the markup calls. Strings come from the markup,\n"
        "   not from this file, so a language only supplies its own labels. */\n"
        "(function () {\n  'use strict';\n\n"
        + "\n\n".join(chunks)
        + "\n\n  window.updateEstimatorOption = updateEstimatorOption;\n"
          "  window.bookEstimatorViaWhatsApp = bookEstimatorViaWhatsApp;\n"
          "  window.transferEstimatorToVipBooking = transferEstimatorToVipBooking;\n})();\n")
(ROOT / "js" / "sr-estimator.js").write_text(body, encoding="utf-8")
print(f"js/sr-estimator.js: {len(body):,} bytes")
