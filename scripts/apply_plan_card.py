#!/usr/bin/env python3
"""Insert the missing social-media plan card into a language page.

The card markup comes from the Arabic master; this script only swaps the words.
Every text node must be covered by the locale map - an unmatched node is an
error, not a silent Arabic leak.

  python scripts/apply_plan_card.py --lang de [--dry-run]
"""
import argparse, json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "docs" / "_extract" / "plan-social.html"
LOCALES = ROOT / "scripts" / "portal_plan_locales.json"


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
        print(f"no plan-card translations for {args.lang}")
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
            if key in loc:
                lead = value[:len(value) - len(value.lstrip())]
                trail = value[len(value.rstrip()):]
                setattr(el, attr, lead + loc[key] + trail)
                matched += 1
            else:
                unmatched.add(key)

    if unmatched:
        print(f"{args.lang}: {len(unmatched)} text nodes have no translation:")
        for u in sorted(unmatched)[:12]:
            print("   -", u[:100])
        return 3

    new_card = LH.tostring(root, encoding="unicode")

    page_path = ROOT / args.lang / "index.html"
    html = page_path.read_text(encoding="utf-8", errors="replace")
    if "plan-social-8k" in html or norm(loc["حزمة 8K السيادية 2026"]) in html:
        print(f"{args.lang}: social plan card already present")
        return 0

    # insert before the first card whose plan name is the visual-identity package
    anchor_name = loc.get("__anchor_plan_name__")
    name_at = html.find(">" + anchor_name + "<")
    if name_at < 0:
        print(f"{args.lang}: anchor card {anchor_name!r} not found")
        return 4
    start = html.rfind('<div class="wg-plan', 0, name_at)
    if start < 0:
        print(f"{args.lang}: anchor card markup not found")
        return 4
    # back up to the beginning of the tag
    html = html[:start] + new_card.strip() + "\n\n                            " + html[start:]

    print(f"{args.lang}: inserted card ({len(new_card):,} chars), {matched} text nodes translated")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page_path.write_text(html, encoding="utf-8", newline="")
    print(f"wrote {page_path} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
