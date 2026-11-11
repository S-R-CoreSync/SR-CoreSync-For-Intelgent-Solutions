#!/usr/bin/env python3
"""Find every visible text node that is still English on a localized page.

Manual patching misses blocks because nobody knows how many there are. This
scans the DOM and reports them by section, so the work becomes a list instead of
a hunt.

  python scripts/i18n_scan_english.py --lang de [--csv out.csv]
"""
import argparse, csv, json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"script", "style", "svg", "path", "rect", "line", "polyline", "circle"}

BRANDS = ["S&R CoreSync For Intelligent Solutions", "S&R CORESYNC FOR INTELLIGENT SOLUTIONS",
          "S&R CORESYNC", "For Intelligent Solutions", "Official Corporate Emblem",
          "Brand Emblem", "S&R TaxSync Desktop", "S&R CloudPOS Connector",
          "S&R FlowScan AI Mobile", "S&R Financial AI SDK", "S&R SecureVault B2B",
          "S&R Cloud Terminal Agent", "S&R CivicSync", "S&R HealthBridge",
          "S&R OmniBakery"]


def is_brand_only(text):
    """A line that carries nothing but the brand, a product name or an emblem label."""
    rest = text
    for brand in BRANDS:
        rest = re.sub(re.escape(brand), " ", rest, flags=re.I)
    rest = re.sub(r"[^A-Za-z\u00C0-\u024F]+", " ", rest)
    words = [w for w in rest.split() if len(w) > 2]
    return len(words) < 4

EN = re.compile(r"\b(the|and|your|with|from|this|that|our|we|are|is|will|can|you|for|of|to|"
                r"all|new|more|best|ready|solutions|systems|software|services)\b", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--csv", default="")
    args = ap.parse_args()

    page = ROOT / args.lang / "index.html"
    if not page.exists():
        print("no page", page)
        return 2
    doc = LH.fromstring(page.read_text(encoding="utf-8", errors="replace"))

    rows = []
    for el in doc.iter():
        if not isinstance(el.tag, str) or el.tag in SKIP:
            continue
        text = re.sub(r"\s+", " ", el.text or "").strip()
        if len(text) < 18:
            continue
        hits = len(EN.findall(text))
        words = len(text.split())
        if hits < 2 or words < 3:
            continue
        if is_brand_only(text):
            continue
        # section = nearest ancestor with an id
        node, section = el, ""
        while node is not None:
            if node.get("id"):
                section = node.get("id")
                break
            node = node.getparent()
        rows.append({"section": section or "-", "words": words, "text": text})

    rows.sort(key=lambda r: (-r["words"], r["section"]))
    print(f"{args.lang}: {len(rows)} English blocks, {sum(r['words'] for r in rows):,} words")
    by_section = {}
    for r in rows:
        by_section[r["section"]] = by_section.get(r["section"], 0) + 1
    for name, count in sorted(by_section.items(), key=lambda x: -x[1])[:10]:
        print(f"   {name:28} {count}")
    for r in rows[:5]:
        print(f"   - [{r['section']}] {r['text'][:80]}")

    if args.csv:
        out = pathlib.Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["section", "words", "text", "translation"])
            w.writeheader()
            for r in rows:
                w.writerow({**r, "translation": ""})
        print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
