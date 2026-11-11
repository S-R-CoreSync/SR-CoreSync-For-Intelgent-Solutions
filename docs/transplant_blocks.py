"""Transplant missing CTA markup from the master into a language page.

  python docs/transplant_blocks.py --lang de [--map scratch/wave1-map.json] [--dry-run]

Two shapes of gap, both handled as text (never re-serializing the page):

  container  the whole row is absent        -> clone it into the card
             pricing-card-actions inside .wg-plan

  child      the row exists but lost its    -> clone the missing button into
             buttons                          the row
             software-btn-wa / -sim inside .software-card-actions
             tech-btn-consult inside .tech-card-footer-actions

Every insertion is collected first and applied from the end of the file
backwards. Arabic is never injected: a clone whose strings the map cannot cover
is skipped and reported.
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARABIC = re.compile(r"[\u0600-\u06FF]")

CONTAINERS = [("pricing-card-actions", 'class="wg-plan')]
CHILDREN = [
    ("software-btn-wa", 'class="founder-editorial-card', "software-card-actions"),
    ("software-btn-sim", 'class="founder-editorial-card', "software-card-actions"),
    ("tech-btn-consult", 'class="wg-tech-v2', "tech-card-footer-actions"),
]


def div_end(raw, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", raw[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    return -1


def blocks(raw, marker):
    rx = re.compile(re.escape(marker) + r'(?=[" ])')
    out, last = [], -1
    for m in rx.finditer(raw):
        s = raw.rfind("<div", 0, m.start())
        if s < 0 or s < last:
            continue
        e = div_end(raw, s)
        if e > 0:
            out.append((s, e))
            last = e
    return out


def element(raw, cls):
    """Span of the first element whose class contains cls."""
    rx = re.compile(r'class="[^"]*\b' + re.escape(cls) + r'\b')
    m = rx.search(raw)
    if not m:
        return None
    start = raw.rfind("<", 0, m.start())
    name = re.match(r"<([a-zA-Z0-9]+)", raw[start:]).group(1)
    if name == "div":
        end = div_end(raw, start)
    else:
        end = raw.find("</%s>" % name, start)
        end = end + len(name) + 3 if end > 0 else -1
    return (start, end) if end > 0 else None


def localise(block, mapping):
    block = re.sub(r'href="(https://wa\.me/\d+)\?text=[^"]*"', r'href="\1"', block)
    for ar, tr in mapping.items():
        block = block.replace(ar, html.escape(tr, quote=False))
    # a tooltip we cannot translate is worse than no tooltip
    block = re.sub(r'\s(?:title|aria-label)="[^"]*[\u0600-\u06FF][^"]*"', '', block)
    return block


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
    path = ROOT / args.lang / "index.html"
    page = path.read_text(encoding="utf-8", errors="replace")
    has_modal = 'id="executiveBookingModal"' in page
    insertions, skipped = [], []

    for cls, marker in CONTAINERS:
        m_cards, t_cards = blocks(master, marker), blocks(page, marker)
        if len(m_cards) != len(t_cards):
            skipped.append(f"{cls}: {len(m_cards)} vs {len(t_cards)} cards")
            continue
        for (ms, me), (ts, te) in zip(m_cards, t_cards):
            if cls in page[ts:te]:
                continue
            span = element(master[ms:me], cls)
            if not span:
                continue
            block = localise(master[ms + span[0]:ms + span[1]], mapping)
            if ARABIC.search(block):
                skipped.append(f"{cls}: untranslated text")
                continue
            if not has_modal:
                block = re.sub(r"<button[^>]*openExecutiveBookingModal.*?</button>", "", block, flags=re.S)
            at = page.rfind("</div>", ts, te)
            insertions.append((at, block))

    for child_cls, marker, container_cls in CHILDREN:
        m_cards, t_cards = blocks(master, marker), blocks(page, marker)
        if len(m_cards) != len(t_cards):
            skipped.append(f"{child_cls}: {len(m_cards)} vs {len(t_cards)} cards")
            continue
        for (ms, me), (ts, te) in zip(m_cards, t_cards):
            m_box, t_box = element(master[ms:me], container_cls), element(page[ts:te], container_cls)
            if not m_box or not t_box:
                continue
            if child_cls in page[ts + t_box[0]:ts + t_box[1]]:
                continue
            span = element(master[ms + m_box[0]:ms + m_box[1]], child_cls)
            if not span:
                continue
            block = localise(master[ms + m_box[0] + span[0]:ms + m_box[0] + span[1]], mapping)
            if ARABIC.search(block):
                skipped.append(f"{child_cls}: untranslated text")
                continue
            at = page.rfind("</div>", ts + t_box[0], ts + t_box[1])
            if at > 0:
                insertions.append((at, block))

    for at, block in sorted(insertions, reverse=True):
        page = page[:at] + block + page[at:]

    print(f"{args.lang}: {len(insertions)} insertions")
    for s in sorted(set(skipped)):
        print("   skipped:", s)
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    path.write_text(page, encoding="utf-8", newline="")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
