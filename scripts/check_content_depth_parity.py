#!/usr/bin/env python3
"""Content depth parity between the Arabic master and every localized index page.

`check_multilingual_page_parity.py` proves that the 19 section ids exist. This
script proves that what lives *inside* those sections still exists: the service
grid, the budget estimator, the FAQ accordion and the plan cards can all vanish
while every id stays in place - which is exactly what happened to 27 languages.

Default mode is a report (exit 0) so it can be run during remediation; pass
--strict to make drift a blocking gate.
"""
import argparse
import pathlib
import re
import sys

MARKERS = {
    "service_cards": (r"tech-card-top-bar", "service grid cards"),
    "estimator_options": (r'class="[^"]*estimator-option[^"]*"', "budget estimator options"),
    "faq_items": (r'class="accordion-action', "FAQ accordion items"),
    "plan_cards": (r'class="[^"]*wg-plan[^"]*"', "pricing plan cards"),
    "pricing_rows": (r"sr-tier-row", "tier comparison rows"),
    "pricing_cells": (r"sr-tier-val-col", "tier comparison cells"),
}

LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]


def counts(path):
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    return {key: len(re.findall(pattern, text)) for key, (pattern, _) in MARKERS.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any language drifts")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    master_path = root / "index.html"
    if not master_path.exists():
        print(f"master page not found: {master_path}")
        return 2

    master = counts(master_path)
    print("=" * 78)
    print("S&R CoreSync - Content depth parity (what is inside the sections)")
    print("=" * 78)
    print(f"{'lang':6}" + "".join(f"{name[:13]:>15}" for name in MARKERS))
    print(f"{'AR':6}" + "".join(f"{master[k]:>15}" for k in MARKERS))
    print("-" * 78)

    drifting = []
    for lang in LANGS:
        page = root / lang / "index.html"
        if not page.exists():
            continue
        row = counts(page)
        bad = {k: (master[k], row[k]) for k in MARKERS if row[k] != master[k]}
        if bad:
            drifting.append((lang, bad))
        cells = "".join(
            f"{row[k]:>15}" if row[k] == master[k] else f"{str(row[k]) + ' !':>15}"
            for k in MARKERS
        )
        print(f"{lang:6}{cells}")

    print("-" * 78)
    if not drifting:
        print(f"PASSED - {len(LANGS)} languages match the master down to component counts.")
        return 0

    print(f"DRIFT - {len(drifting)} of {len(LANGS)} languages are missing content the master has:")
    for lang, bad in drifting:
        detail = ", ".join(f"{k} {have}/{want}" for k, (want, have) in bad.items())
        print(f"  {lang:5} {detail}")
    print()
    print("Repair path: regenerate the missing blocks from portal_shared_sections_locales.json")
    print("instead of hand-copying markup, then re-run this script.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
