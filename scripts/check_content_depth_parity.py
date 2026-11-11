#!/usr/bin/env python3
"""Content parity between the Arabic master and every localized index page.

`check_multilingual_page_parity.py` proves the 19 section ids exist. This script
proves the *content inside them* still exists, using measures that survive a
markup redesign:

  plan cards      every page must offer the same packages
  faq items       every page must answer the same number of questions
  faq language    a non-English page must not show English questions
  estimator       the interactive estimator must be present
  service cards   the same number of service blocks

Default mode is a report (exit 0) so it can run during remediation; --strict
makes drift fail the build.

  python scripts/check_content_depth_parity.py [--strict] [--json out.json]
"""
import argparse
import json
import pathlib
import re
import sys

from lxml import html as LH

LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
ENGLISH = re.compile(r"^(how|do|does|what|which|are|is|can|why|when|where|who)\b", re.I)


def normalise(value):
    return re.sub(r"\s+", " ", value).strip()


def measure(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    doc = LH.fromstring(raw)
    faq = [normalise(q.text_content()) for q in doc.xpath("//*[contains(@class,'accordion-text')]")]
    return {
        "plans": len(doc.xpath("//*[contains(@class,'plan-name')]")),
        "faq": len(faq),
        "faq_english": sum(1 for q in faq if ENGLISH.match(q)),
        "estimator": raw.count("updateEstimatorOption"),
        "services": len(doc.xpath("//*[contains(@class,'tech-name')]")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    master = measure(root / "index.html")
    print("=" * 86)
    print("S&R CoreSync - content parity inside the sections")
    print("=" * 86)
    print(f"{'lang':6}{'plans':>7}{'faq':>6}{'faq EN':>8}{'estimator':>11}{'services':>10}")
    print(f"{'AR':6}{master['plans']:>7}{master['faq']:>6}{master['faq_english']:>8}"
          f"{master['estimator']:>11}{master['services']:>10}")
    print("-" * 86)

    rows, drifting = {}, []
    for lang in LANGS:
        page = root / lang / "index.html"
        if not page.exists():
            continue
        row = measure(page)
        rows[lang] = row
        bad = []
        if row["plans"] != master["plans"]:
            bad.append(f"plans {row['plans']}/{master['plans']}")
        if row["faq"] != master["faq"]:
            bad.append(f"faq {row['faq']}/{master['faq']}")
        if lang != "en" and row["faq_english"]:
            bad.append(f"{row['faq_english']} EN faq")
        if master["estimator"] and not row["estimator"]:
            bad.append("no estimator")
        if row["services"] != master["services"]:
            bad.append(f"services {row['services']}/{master['services']}")
        if bad:
            drifting.append((lang, bad))
        print(f"{lang:6}{row['plans']:>7}{row['faq']:>6}{row['faq_english']:>8}"
              f"{row['estimator']:>11}{row['services']:>10}"
              + ("   <- " + "; ".join(bad) if bad else ""))

    print("-" * 86)
    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"master": master, "pages": rows}, indent=1, ensure_ascii=False),
            encoding="utf-8")
    if not drifting:
        print(f"PASSED - {len(rows)} languages match the master.")
        return 0
    print(f"DRIFT - {len(drifting)} of {len(rows)} languages:")
    for lang, bad in drifting:
        print(f"  {lang:5} " + "; ".join(bad))
    print()
    print("Repair with scripts/apply_faq_locales.py / apply_plan_card.py once the locale")
    print("JSON for that language is filled; the estimator needs its own module.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
