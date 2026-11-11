"""Compare the DOM order and composition of every language page with the master.

  python docs/audit_structure_vs_master.py [--json docs/structure_diff.json] [--strict]

Measures what the parity gates do not: the ORDER of the sections, and how much
each section actually contains (cards, rows, headings, buttons). A page can have
all 19 ids and still read differently because a block moved, duplicated or lost
its inner content.

--strict exits 1 when any page differs, so a new block cannot be added to the
master without being carried to the other pages. Tolerance for per-section node
counts is 2, which absorbs translation-driven differences.
"""
import argparse
import json
import pathlib
import sys

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
TOLERANCE = 2


def fingerprint(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    doc = LH.fromstring(raw)
    body = doc.body if doc.body is not None else doc
    sections = []
    for el in body.iter("section"):
        key = el.get("id") or (el.get("class") or "").split(" ")[0] or el.tag
        sections.append({
            "key": key,
            "cards": len(el.xpath(".//*[contains(@class,'card')]")),
            "li": len(el.xpath(".//li")),
            "tr": len(el.xpath(".//tr")),
            "h2h3": len(el.xpath(".//h2|.//h3")),
            "btn": len(el.xpath(".//button|.//a[contains(@class,'btn')]")),
            "words": len(" ".join(el.itertext()).split()),
        })
    footers = len(body.xpath(".//footer"))
    return {"sections": sections, "footers": footers, "bytes": len(raw)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    master = fingerprint(ROOT / "index.html")
    order = [s["key"] for s in master["sections"]]
    print("=" * 100)
    print("STRUCTURE vs MASTER - order, composition, footers")
    print("=" * 100)
    print(f"master: {len(order)} sections, {master['footers']} footers")
    print("  " + " > ".join(order))
    print("-" * 100)

    report = {"master": {"order": order, "footers": master["footers"]}, "pages": {}}
    problems_total = 0
    for lang in LANGS:
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        fp = fingerprint(page)
        seq = [s["key"] for s in fp["sections"]]
        missing = [k for k in order if k not in seq]
        extra = [k for k in seq if k not in order]
        first = next((i for i, (a, b) in enumerate(zip(order, seq)) if a != b), None)
        drift = [order[first], seq[first]] if first is not None else []

        counts = {}
        for m, p in zip(master["sections"], fp["sections"]):
            if m["key"] != p["key"]:
                continue
            d = {k: p[k] - m[k] for k in ("cards", "li", "tr", "h2h3", "btn")
                 if abs(p[k] - m[k]) > TOLERANCE}
            if d:
                counts[m["key"]] = d

        bad = bool(missing or extra or drift or counts)
        if bad:
            problems_total += 1
        report["pages"][lang] = {
            "missing": missing, "extra": extra, "first_drift": drift,
            "footers": fp["footers"], "content_delta": counts,
        }
        print(f"{lang:5}{len(seq):>4} sections  {fp['footers']} footers  "
              f"{'DRIFT' if bad else 'ok'}")
        if missing:
            print(f"      missing: {missing}")
        if extra:
            print(f"      extra  : {extra}")
        if drift:
            print(f"      order  : master has '{drift[0]}' where page has '{drift[1]}'")
        for sec, d in counts.items():
            print(f"      {sec}: {d}")

    print("-" * 100)
    print(f"{problems_total} of {len(report['pages'])} pages differ from the master")
    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
        print("wrote", args.json)
    if args.strict and problems_total:
        print("STRICT: structure drift is blocking")
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
