"""Measure the real structure of every index page and write the two data files
the structure dashboard is built from.

  python docs/measure_structure.py

Writes docs/component_counts.json (what a visitor can count: cards, rows, items)
and docs/structure_census.json (per-section bytes, words, list items, cards).
Read-only for the site; safe to run any time after editing a page.
"""
import json, pathlib, re
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = ["hero","about","trust-band","founders-showcase","services","services-compare",
            "tech-pillars","compliance","process","software-hub","testimonials",
            "roi-calculator","pricing","guarantees","faq","executive-solutions-stage",
            "contact","newsletter","insights"]
LANGS = ["bg","ckb","cs","da","de","el","en","es","et","fi","fr","ga","hr","hu","it",
         "ku","lt","lv","mt","nl","no","pl","pt","ro","sk","sl","sv","tr"]
MARKERS = {
    "service_cards": r"tech-card-top-bar",
    "pricing_rows": r"sr-tier-row",
    "pricing_cells": r"sr-tier-val-col",
    "plan_cards": r'class="[^"]*wg-plan[^"]*"',
    "estimator_options": r'class="[^"]*estimator-option[^"]*"',
    "faq_items": r'class="accordion-action',
    "process_steps": r'class="[^"]*process-step',
    "finder_tabs": r"founder-tab",
    "trust_marks": r"trust-logo",
}


def counts(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return {k: len(re.findall(v, text)) for k, v in MARKERS.items()}


def census(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    doc = LH.fromstring(raw)
    out = {}
    for name in SECTIONS:
        el = doc.get_element_by_id(name, None)
        if el is None:
            out[name] = None
            continue
        node = el
        while node is not None and node.tag not in ("section", "main", "div"):
            node = node.getparent()
        block = node if node is not None else el
        marker = LH.tostring(block, encoding="unicode")
        out[name] = {
            "tag": block.tag,
            "bytes": len(marker),
            "li": len(block.xpath(".//li")),
            "article": len(block.xpath(".//article")),
            "h2h3": len(block.xpath(".//h2|.//h3")),
            "tr": len(block.xpath(".//tr")),
            "img": len(block.xpath(".//img")),
            "button": len(block.xpath(".//button")),
            "cards": len(block.xpath(".//*[@class and contains(@class,'card')]")),
            "text": len(re.sub(r"<[^>]+>", " ", marker).split()),
        }
    return {"bytes": len(raw), "sections": out}


def main():
    out_dir = ROOT / "docs"
    comp = {"master": counts(ROOT / "index.html"), "pages": {}}
    cens = {"master": census(ROOT / "index.html"), "pages": {}}
    for lang in LANGS:
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        comp["pages"][lang] = counts(page)
        cens["pages"][lang] = census(page)
    (out_dir / "component_counts.json").write_text(
        json.dumps(comp, indent=1, ensure_ascii=False), encoding="utf-8")
    (out_dir / "structure_census.json").write_text(
        json.dumps(cens, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"measured 1 master + {len(comp['pages'])} languages")
    print("master components:", comp["master"])


if __name__ == "__main__":
    main()
