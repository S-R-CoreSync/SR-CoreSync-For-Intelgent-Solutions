#!/usr/bin/env python3
"""Export the untranslated keys of a language as a classified CSV.

Categories keep the translator honest about effort: a label is not a sentence, and
a repeated string is paid for once.

  python scripts/i18n_export_todo.py --lang de --out docs/i18n-de-todo.csv
"""
import argparse, csv, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = ROOT / "i18n"
ARABIC = re.compile(r"[\u0600-\u06FF]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="de")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    master = json.loads((I18N / "_master.json").read_text(encoding="utf-8"))
    catalog = json.loads((I18N / f"{args.lang}.json").read_text(encoding="utf-8"))

    required = {k: v for k, v in master.items()
                if ARABIC.search(v["ar"]) or re.search(r"[A-Za-z]{3,}", v["ar"])}
    missing = {k: v for k, v in required.items() if k not in catalog}

    counts = {}
    for v in missing.values():
        counts[v["ar"]] = counts.get(v["ar"], 0) + 1

    rows = []
    for key, item in missing.items():
        text = item["ar"]
        words = len(text.split())
        if counts[text] > 1:
            category = "repeated"
        elif not re.search(r"[A-Za-z\u0600-\u06FF]", text):
            category = "number"
        elif words <= 4:
            category = "label"
        else:
            category = "sentence"
        rows.append({
            "key": key,
            "kind": item["kind"],
            "category": category,
            "words": words,
            "occurrences": counts[text],
            "arabic": text,
            "translation": "",
        })

    order = {"label": 0, "repeated": 1, "sentence": 2, "number": 3}
    rows.sort(key=lambda r: (order[r["category"]], -r["occurrences"], r["words"]))

    out = pathlib.Path(args.out or f"docs/i18n-{args.lang}-todo.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["key", "kind", "category", "words",
                                                "occurrences", "arabic", "translation"])
        writer.writeheader()
        writer.writerows(rows)

    by_cat = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    total_words = sum(r["words"] for r in rows)

    print(f"{args.lang}: {len(rows)} keys to translate, {total_words} words")
    for cat in ("label", "repeated", "sentence", "number"):
        print(f"   {cat:9} {by_cat.get(cat, 0):>5}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
