"""Transplant the missing CTA containers from the master into a language page.

  python docs/transplant_blocks.py --lang de [--map scratch/wave1-map.json] [--dry-run]

Wave 1 = the three CTA rows that every localized page lost:
  pricing-card-actions      inside each .wg-plan card
  software-card-actions     inside each product card
  tech-card-footer-actions  inside each .tech-card

The page is edited as text: the master's container is copied byte for byte, its
Arabic strings are replaced from the map, and the result is inserted before the
card's closing tag. Nothing else is re-serialized, so the diff stays readable and
the CSP hashes cannot move. Every insertion is collected first and applied from
the end of the file backwards, so offsets never go stale.
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARABIC = re.compile(r"[\u0600-\u06FF]")
WAVE1 = [
    ("pricing-card-actions", ['class="wg-plan']),
    ("software-card-actions", ['class="founder-editorial-card']),
]


def div_end(raw, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", raw[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    return -1


def cards(raw, marker):
    """Top-level div blocks whose class attribute starts with marker."""
    rx = re.compile(re.escape(marker) + r'(?=[" ])')
    out, last_end = [], -1
    for m in rx.finditer(raw):
        start = raw.rfind("<div", 0, m.start())
        if start < 0 or start < last_end:
            continue
        end = div_end(raw, start)
        if end > 0:
            out.append((start, end))
            last_end = end
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--map", default="scratch/wave1-map.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mapping = json.loads((ROOT / args.map).read_text(encoding="utf-8")).get(args.lang, {})
    if not mapping:
        print(f"no map for {args.lang}")
        return 2

    master = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    page_path = ROOT / args.lang / "index.html"
    page = page_path.read_text(encoding="utf-8", errors="replace")

    insertions, skipped = [], []
    for cls, markers in WAVE1:
        m_cards, t_cards = [], []
        for mk in markers:
            m_cards.extend(cards(master, mk))
            t_cards.extend(cards(page, mk))
        m_cards.sort()
        t_cards.sort()
        if len(m_cards) != len(t_cards):
            skipped.append(f"{cls}: {len(m_cards)} master cards vs {len(t_cards)} here")
            continue
        for (ms, me), (ts, te) in zip(m_cards, t_cards):
            if cls in page[ts:te]:
                continue
            container = None
            for cs, ce in cards(master[ms:me], 'class="%s' % cls)[:1]:
                container = master[ms + cs:ms + ce]
            if not container:
                skipped.append(f"{cls}: container not found in the master card")
                continue
            localised = container
            # A prefilled Arabic WhatsApp message would ride along; the other
            # buttons on the page open the same number without a text parameter.
            localised = re.sub(r'href="(https://wa\.me/\d+)\?text=[^"]*"',
                               r'href="\1"', localised)
            for ar, tr in mapping.items():
                localised = localised.replace(ar, html.escape(tr, quote=False))
            if 'id="executiveBookingModal"' not in page:
                localised = re.sub(r'<button[^>]*openExecutiveBookingModal.*?</button>', '',
                                   localised, flags=re.S)
            if ARABIC.search(localised):
                skipped.append(f"{cls}: untranslated Arabic left")
                continue
            at = page.rfind("</div>", ts, te)
            if at < 0:
                skipped.append(f"{cls}: no closing tag")
                continue
            insertions.append((at, localised))

    for at, block in sorted(insertions, reverse=True):
        page = page[:at] + block + page[at:]

    print(f"{args.lang}: {len(insertions)} containers inserted")
    for s in sorted(set(skipped)):
        print("   skipped:", s)
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page_path.write_text(page, encoding="utf-8", newline="")
    print("wrote", page_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
