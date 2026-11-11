"""Install the cost estimator (calculator + WhatsApp button, no booking modal)
into one language page.

  python scripts/install_estimator.py --lang de [--dry-run]

The block comes from the master; labels come from scripts/portal_estimator_locales.json.
The booking button is removed because these pages have no booking modal, and a
dead button is worse than an absent one.
"""
import argparse, json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK = ROOT / "docs" / "_extract" / "estimator.html"
LOCALES = ROOT / "scripts" / "portal_estimator_locales.json"


def norm(v):
    return re.sub(r"\s+", " ", v or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    labels = json.loads(LOCALES.read_text(encoding="utf-8")).get(args.lang, {})
    if not labels:
        print(f"no labels for {args.lang}")
        return 2

    node = LH.fragment_fromstring(BLOCK.read_text(encoding="utf-8"))
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
            else:
                missing.append(key)
        for attr in ("alt", "title", "placeholder", "aria-label", "data-title", "data-days"):
            value = el.get(attr)
            if value and value.strip():
                key = norm(value)
                if key in labels and labels[key]:
                    el.set(attr, labels[key])
                else:
                    missing.append(key)

    if missing:
        print(f"{args.lang}: {len(set(missing))} labels missing, first: {sorted(set(missing))[:4]}")
        return 3

    for btn in node.xpath(".//*[@data-sr-call='transferEstimatorToVipBooking']"):
        btn.getparent().remove(btn)

    block = LH.tostring(node, encoding="unicode")
    page = ROOT / args.lang / "index.html"
    html = page.read_text(encoding="utf-8", errors="replace")
    if "cost-estimator-controls" in html:
        print(f"{args.lang}: estimator already present")
        return 0

    m = re.search(r'<section[^>]*id="pricing"', html)
    if not m:
        print(f"{args.lang}: pricing section not found")
        return 4

    html = html[:m.start()] + block.strip() + "\n\n            " + html[m.start():]
    if "sr-estimator.css" not in html:
        html = html.replace("</head>", '<link rel="stylesheet" href="../css/sr-estimator.css?v=20261111">\n</head>', 1)
    if "sr-estimator.js" not in html:
        html = html.replace("</body>", '<script src="../js/sr-estimator.js?v=20261111" defer></script>\n</body>', 1)

    print(f"{args.lang}: estimator inserted ({len(block):,} chars)")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page.write_text(html, encoding="utf-8", newline="")
    print(f"wrote {page}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
