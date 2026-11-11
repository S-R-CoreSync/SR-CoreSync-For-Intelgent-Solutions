"""Install the cost estimator into one language page.

  python scripts/install_estimator.py --lang de --full [--dry-run]

  --full   install the whole widget (options + total + timeline + CTA) from
           docs/_extract/estimator-grid.html. Without it only the option block
           is installed - which is what shipped on de by mistake: buttons, no
           total and no call to action.

Labels come from scripts/portal_estimator_locales.json, keyed by the Arabic
source string. A previous install - partial or in the wrong language - is
removed before the new one goes in, so the command is idempotent.

The WhatsApp message segments are written onto the widget root as data-wa-*,
read from the "_whatsapp" block of the same file. Without them the shared module
falls back to Arabic, which is only right on the master page.

The booking button is dropped unless the page defines #executiveBookingModal:
a dead button is worse than an absent one.
"""
import argparse
import json
import pathlib
import re
import sys

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCALES = ROOT / "scripts" / "portal_estimator_locales.json"
SKIP = {"590", "\u20ac", "\u2713"}          # numbers and glyphs, not prose
BLOCKS = {
    "controls": ROOT / "docs" / "_extract" / "estimator.html",
    "full": ROOT / "docs" / "_extract" / "estimator-grid.html",
}
ATTRS = ("alt", "title", "placeholder", "aria-label", "data-title", "data-days")
WA = ("title", "type", "scope", "lang", "pay", "speed", "total", "duration", "days")


def norm(v):
    return re.sub(r"\s+", " ", v or "").strip()


def span_of(raw, marker):
    """Balanced <div> span of the element containing marker."""
    i = raw.find(marker)
    if i < 0:
        return None
    start = raw.rfind("<div", 0, i)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", raw[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return start, start + m.end()
    return None


def localise(node, labels):
    missing = []
    for el in node.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in ("text", "tail"):
            value = getattr(el, attr)
            if not value or not value.strip():
                continue
            key = norm(value)
            if key in labels and labels[key]:
                lead = value[:len(value) - len(value.lstrip())]
                setattr(el, attr, lead + labels[key])
            elif key not in SKIP:
                missing.append(key)
        for attr in ATTRS:
            value = el.get(attr)
            if value and value.strip():
                key = norm(value)
                if key in labels and labels[key]:
                    el.set(attr, labels[key])
                elif key not in SKIP:
                    missing.append(key)
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db = json.loads(LOCALES.read_text(encoding="utf-8"))
    labels = db.get(args.lang, {})
    if not labels:
        print(f"no labels for {args.lang}")
        return 2

    source = BLOCKS["full" if args.full else "controls"]
    node = LH.fragment_fromstring(source.read_text(encoding="utf-8"))
    missing = localise(node, labels)
    if missing:
        print(f"{args.lang}: {len(set(missing))} labels missing")
        for m in sorted(set(missing))[:8]:
            print("   -", m[:100])
        return 3

    wa = db.get("_whatsapp", {}).get(args.lang, {})
    for key in WA:
        if wa.get(key):
            node.set("data-wa-" + key, wa[key])
    if not wa:
        print(f"{args.lang}: no _whatsapp segments - the WhatsApp text stays Arabic")

    page = ROOT / args.lang / "index.html"
    html = page.read_text(encoding="utf-8", errors="replace")

    if 'id="executiveBookingModal"' not in html:
        for btn in node.xpath(".//*[@data-sr-call='transferEstimatorToVipBooking']"):
            btn.getparent().remove(btn)

    markup = LH.tostring(node, encoding="unicode").strip()

    removed = 0
    for marker in ("cost-estimator-grid", "cost-estimator-controls"):
        span = span_of(html, marker)
        if span:
            html = html[:span[0]] + html[span[1]:]
            removed += 1
            break

    m = re.search(r'<section[^>]*id="pricing"', html)
    if not m:
        print(f"{args.lang}: pricing section not found")
        return 4
    html = html[:m.start()] + markup + "\n\n            " + html[m.start():]

    if "sr-estimator.css" not in html:
        html = html.replace("</head>", '<link rel="stylesheet" href="../css/sr-estimator.css?v=20261112">\n</head>', 1)
    if "sr-estimator.js" not in html:
        html = html.replace("</body>", '<script src="../js/sr-estimator.js?v=20261112" defer></script>\n</body>', 1)

    print(f"{args.lang}: {'full' if args.full else 'controls'} installed "
          f"({len(markup):,} chars, removed {removed} old block, wa={'yes' if wa else 'arabic default'})")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page.write_text(html, encoding="utf-8", newline="")
    print("wrote", page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
