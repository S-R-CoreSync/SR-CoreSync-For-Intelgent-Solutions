#!/usr/bin/env python3
"""Insert the missing 'Bespoke Sovereign & FinTech' plan card into a language page.

Content-parity counts 13 plan cards on the Arabic master but every locale page
ships 12: the Bespoke tier was added to the master only. This script ports the
card from docs/_extract/plan-bespoke.html and swaps the words using
scripts/portal_bespoke_locales.json - an unmatched node is an error, not a
silent Arabic leak.

  python scripts/apply_bespoke_card.py --lang bg [--dry-run]
"""
import argparse
import json
import pathlib
import re
import sys

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "docs" / "_extract" / "plan-bespoke.html"
LOCALES = ROOT / "scripts" / "portal_bespoke_locales.json"
MARKER = "Bespoke Sovereign & FinTech"      # tier name, never translated
ANCHOR = ">ERP Setup<"                      # card stays after Core MAX Synergy


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    locales = json.loads(LOCALES.read_text(encoding="utf-8"))
    loc = locales.get(args.lang)
    if not loc:
        print(f"no bespoke-card translations for {args.lang}")
        return 2

    card_html = CARD.read_text(encoding="utf-8")
    root = LH.fragment_fromstring(card_html)

    unmatched, matched = set(), 0
    for el in root.iter():
        for attr in ("text", "tail"):
            value = getattr(el, attr)
            if not value or not value.strip():
                continue
            key = norm(value)
            if key == MARKER:
                matched += 1
                continue
            if key in loc:
                lead = value[:len(value) - len(value.lstrip())]
                trail = value[len(value.rstrip()):]
                setattr(el, attr, lead + loc[key] + trail)
                matched += 1
            else:
                unmatched.add(key)
        for attr in ("alt", "title", "aria-label"):
            value = el.get(attr)
            if not value or not value.strip():
                continue
            key = norm(value)
            if key != MARKER and key in loc:
                el.set(attr, loc[key])
                matched += 1
            else:
                unmatched.add(key)

    if unmatched:
        print(f"{args.lang}: {len(unmatched)} text nodes have no translation:")
        for u in sorted(unmatched)[:12]:
            print("   -", u[:100])
        return 3

    new_card = LH.tostring(root, encoding="unicode")
    new_card = new_card.replace('src="./assets/', 'src="../assets/')
    new_card = new_card.replace('href="./assets/', 'href="../assets/')
    new_card = new_card.replace('src="./js/', 'src="../js/')

    page_path = ROOT / args.lang / "index.html"
    html = page_path.read_text(encoding="utf-8", errors="replace")
    # lxml escapes the '&' in the card title on write, so both forms count.
    if f">{MARKER}<" in html or f">Bespoke Sovereign &amp; FinTech<" in html:
        print(f"{args.lang}: bespoke plan card already present")
        return 0

    name_at = html.find(ANCHOR)
    if name_at < 0:
        print(f"{args.lang}: anchor card 'ERP Setup' not found")
        return 4
    start = html.rfind('<div class="wg-plan', 0, name_at)
    if start < 0:
        print(f"{args.lang}: anchor card markup not found")
        return 4
    html = html[:start] + new_card.strip() + "\n\n                            " + html[start:]

    print(f"{args.lang}: inserted bespoke card ({len(new_card):,} chars), {matched} text nodes translated")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page_path.write_text(html, encoding="utf-8", newline="")
    print(f"wrote {page_path} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
