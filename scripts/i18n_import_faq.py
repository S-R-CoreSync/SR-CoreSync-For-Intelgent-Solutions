#!/usr/bin/env python3
"""Import the translated FAQ worksheet back into the locale files.

Round trip: export (i18n_export_faq_remaining.py) -> translator fills the two
columns -> this script merges them into scripts/portal_faq_locales.json -> the
existing appliers write the pages.

Rows with an empty translation are skipped and reported, never half-applied.

  python scripts/i18n_import_faq.py docs/i18n-faq-remaining.csv [--apply]
"""
import argparse
import csv
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCALES = ROOT / "scripts" / "portal_faq_locales.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--apply", action="store_true", help="run the page appliers afterwards")
    args = ap.parse_args()

    path = pathlib.Path(args.csv_path)
    if not path.exists():
        print(f"csv not found: {path}")
        return 2

    locales = json.loads(LOCALES.read_text(encoding="utf-8"))
    merged, skipped, touched = 0, 0, set()

    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            q = (row.get("question_translated") or "").strip()
            a = (row.get("answer_translated") or "").strip()
            if not q or not a:
                skipped += 1
                continue
            lang = row["lang"].strip()
            order = row["order"].strip().zfill(2)
            entry = locales.setdefault(lang, {"heading": "", "faq": {}})
            entry.setdefault("faq", {})[order] = {"q": q, "a": a}
            merged += 1
            touched.add(lang)

    if not merged:
        print(f"nothing to import: {skipped} rows still empty")
        return 1

    LOCALES.write_text(json.dumps(locales, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"merged {merged} answers into {len(touched)} languages (skipped {skipped} empty)")

    if args.apply:
        for lang in sorted(touched):
            subprocess.run([sys.executable, str(ROOT / "scripts" / "apply_faq_locales.py"),
                            "--lang", lang], check=False)
    else:
        print("run with --apply (or apply_faq_locales.py --lang XX) to write the pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
