#!/usr/bin/env python3
"""Export every FAQ answer that is still English, per language, as one CSV.

The remaining gap in the accordion is the eleven older answers, which were never
translated. They are long legal/commercial prose, so they go to a translator as a
single worksheet instead of being rewritten page by page.

  python scripts/i18n_export_faq_remaining.py --out docs/i18n-faq-remaining.csv
"""
import argparse, csv, pathlib, re
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
ENGLISH = re.compile(r"^(how|do|does|what|which|are|is|can|why|when|where|who)\b", re.I)


def norm(v):
    return re.sub(r"\s+", " ", v or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/i18n-faq-remaining.csv")
    args = ap.parse_args()

    rows = []
    for lang in LANGS:
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        doc = LH.fromstring(page.read_text(encoding="utf-8", errors="replace"))
        for item in doc.xpath("//*[contains(@class,'accordion-faq_item')]"):
            q = item.xpath(".//*[contains(@class,'accordion-text')]")
            a = item.xpath(".//*[contains(@class,'accordion-content')]")
            o = item.xpath(".//*[contains(@class,'accordion-order')]")
            if not (q and a and o):
                continue
            question = norm(q[0].text_content())
            if not ENGLISH.match(question):
                continue
            rows.append({
                "lang": lang,
                "order": norm(o[0].text_content()),
                "question_en": question,
                "answer_en": norm(a[0].text_content()),
                "question_translated": "",
                "answer_translated": "",
            })

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["lang", "order", "question_en", "answer_en",
                                           "question_translated", "answer_translated"])
        w.writeheader()
        w.writerows(rows)

    langs = sorted({r["lang"] for r in rows})
    words = sum(len(r["answer_en"].split()) + len(r["question_en"].split()) for r in rows)
    print(f"{len(rows)} untranslated answers across {len(langs)} languages, {words:,} words")
    print("per language:", len(rows) // max(1, len(langs)))
    print("wrote", out)


if __name__ == "__main__":
    main()
