"""Which markup classes the pages lack, and which strings those carry.

  python docs/plan_transplant.py [--json docs/transplant-report.json]

Text diffing is useless here: a translated page never contains the master's
Arabic sentences. What differs structurally is a set of element classes. For
each class present on the master and missing on a page, this lists the strings
that class carries, and whether the catalog already translates them.
"""
import argparse
import json
import pathlib
import re
import sys
from collections import Counter

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
SECTIONS = ["hero", "services", "software-hub", "pricing", "founders-showcase"]
ARABIC = re.compile(r"[\u0600-\u06FF]")


def class_index(path):
    """class -> (count, [normalised texts]) over the five sections."""
    doc = LH.fromstring(pathlib.Path(path).read_text(encoding="utf-8", errors="replace"))
    idx = {}
    for sid in SECTIONS:
        el = doc.get_element_by_id(sid, None)
        if el is None:
            continue
        for node in el.iter():
            if not isinstance(node.tag, str):
                continue
            for cls in (node.get("class") or "").split():
                slot = idx.setdefault(cls, {"count": 0, "texts": []})
                slot["count"] += 1
                for chunk in node.itertext():
                    t = re.sub(r"\s+", " ", chunk).strip()
                    if len(t) > 2 and ARABIC.search(t):
                        slot["texts"].append(t)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    master = class_index(ROOT / "index.html")
    de = class_index(ROOT / "de" / "index.html")
    gaps = {c: v for c, v in master.items() if v["count"] > de.get(c, {"count": 0})["count"]}
    gaps = {c: v for c, v in gaps.items() if v["count"] >= 1}

    print("=" * 96)
    print("CLASS GAPS - present on the master, fewer or absent on a localized page")
    print("=" * 96)
    rows = []
    for cls, v in sorted(gaps.items(), key=lambda kv: -(kv[1]["count"] - de.get(kv[0], {"count": 0})["count"])):
        delta = v["count"] - de.get(cls, {"count": 0})["count"]
        if delta <= 2:
            continue
        texts = sorted(set(v["texts"]))
        rows.append({"class": cls, "delta": delta, "texts": texts})
        print(f"{cls:34} +{delta:<4} strings: {len(texts)}")
        for t in texts[:4]:
            print(f"      · {t[:88]}")

    cat_dir = ROOT / "scripts" / "i18n" / "translations"
    need = []
    for row in rows:
        need.extend(row["texts"])
    need = sorted(set(need))
    covered = 0
    for lang in LANGS:
        p = cat_dir / f"{lang}.json"
        strings = json.loads(p.read_text(encoding="utf-8")).get("strings", {}) if p.exists() else {}
        covered += sum(1 for s in need if strings.get(s))
    print("-" * 96)
    print(f"distinct new strings: {len(need)}")
    print(f"catalog hits across {len(LANGS)} languages: {covered} of {len(need) * len(LANGS)}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"gaps": rows, "strings": need}, indent=1, ensure_ascii=False),
            encoding="utf-8")
        print("wrote", args.json)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
