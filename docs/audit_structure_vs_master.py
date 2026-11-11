"""Compare the DOM order and composition of every language page with the master.

  python docs/audit_structure_vs_master.py [--json docs/structure_diff.json]

Measures what the parity gates do not: the ORDER of the sections, and how much
each section actually contains (cards, rows, headings, buttons). A page can have
all 19 ids and still read differently because a block moved, duplicated or lost
its inner content.
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
        drift = [] if first is None and len(seq) == len(order) else []
        if first is not None or len(seq) != len(order):
            drift = [order[first], seq[first]] if first is not None else []

        counts = {}
        for m, p in zip(master["sections"], fp["sections"]):
            if m["key"] != p["key"]:
                continue
            d = {k: p[k] - m[k] for k in ("cards", "li", "tr", "h2h3", "btn")
                 if abs(p[k] - m[k]) > 2}
            if d:
                counts[m["key"]] = d

        bad = bool(missing or extra or drift or fp["footers"] != master["footers"] or counts)
        if bad:
            problems_total += 1
        report["pages"][lang] = {
            "missing": missing, "extra": extra, "first_drift": drift,
            "footers": fp["footers"], "content_delta": counts,
        }
        flag = "DRIFT" if bad else "ok"
        print(f"{lang:5}{len(seq):>4} sections  {fp['footers']} footers  {flag}")
        if missing:
            print(f"      missing: {missing}")
        if extra:
            print(f"      extra  : {extra}")
        if drift:
            print(f"      order  : master has '{drift[0]}' where page has '{drift[1]}'")
        if fp["footers"] != master["footers"]:
            print(f"      footers: {fp['footers']} vs master {master['footers']}")
        for sec, d in counts.items():
            print(f"      {sec}: {d}")

    print("-" * 100)
    print(f"{problems_total} of {len(report['pages'])} pages differ from the master")
    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
        print("wrote", args.json)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
