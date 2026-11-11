#!/usr/bin/env python3
"""Apply localized FAQ content to a language page.

The master page owns the markup; the JSON file owns only the words. Questions a
target page is missing are cloned from the master block and filled with the
translation, so structure and copy cannot drift apart.

  python scripts/apply_faq_locales.py --lang de [--dry-run]

Works item by item instead of on the whole accordion container: several pages
carry a few unclosed <div> tags that browsers tolerate, so counting container
depth is not a reliable boundary. Idempotent.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCALES = ROOT / "scripts" / "portal_faq_locales.json"
ITEM_SPLIT = re.compile(r'(?=<div class="accordion-faq_item")')
ORDER = re.compile(r'accordion-order">\s*(\d+)\s*<')


def split_items(html):
    parts = ITEM_SPLIT.split(html)
    if len(parts) < 2:
        raise SystemExit("no FAQ items found")
    head, items = parts[0], parts[1:]
    mapped = {}
    for idx, part in enumerate(items):
        m = ORDER.search(part)
        if m:
            mapped[m.group(1)] = idx
    return head, items, mapped


def set_texts(block, question, answer):
    block = re.sub(r'(<p class="accordion-text">).*?(</p>)',
                   lambda m: m.group(1) + question + m.group(2), block, count=1, flags=re.S)
    block = re.sub(r'(<p class="accordion-content[^"]*">).*?(</p>)',
                   lambda m: m.group(1) + answer + m.group(2), block, count=1, flags=re.S)
    return block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    locale = json.loads(LOCALES.read_text(encoding="utf-8")).get(args.lang)
    if not locale:
        print(f"no translations for {args.lang}")
        return 2

    _, master_items, master_map = split_items(
        (ROOT / "index.html").read_text(encoding="utf-8", errors="replace"))
    target = ROOT / args.lang / "index.html"
    html = target.read_text(encoding="utf-8", errors="replace")
    head, items, target_map = split_items(html)

    updated, added = [], []
    for order in sorted(master_map):
        tr = locale["faq"].get(order)
        if not tr:
            continue
        if order in target_map:
            idx = target_map[order]
            items[idx] = set_texts(items[idx], tr["q"], tr["a"])
            updated.append(order)
        else:
            lower = [o for o in target_map if o < order]
            if not lower:
                print(f"cannot place question {order}: nothing precedes it")
                return 3
            anchor = target_map[max(lower)]
            block = set_texts(master_items[master_map[order]], tr["q"], tr["a"])
            items[anchor] = items[anchor].rstrip() + "\n" + block.strip() + "\n                            "
            added.append(order)

    html = head + "".join(items)

    heading = locale.get("heading")
    if heading:
        html = re.sub(r'(<h2 class="text-display-2[^"]*">)\s*.*?\s*(</h2>)',
                      lambda m: m.group(1) + "\n                        " + heading + "\n                    " + m.group(2),
                      html, count=1, flags=re.S)

    print(f"{args.lang}: updated {len(updated)} {updated} | added {len(added)} {added}")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    target.write_text(html, encoding="utf-8", newline="")
    print(f"wrote {target} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
