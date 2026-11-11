#!/usr/bin/env python3
"""Translation memory for the static site: master keys, harvest, coverage.

The master page is the single source of structure. Every translatable string is
addressed by its DOM path, so a language page can be rebuilt from the master
without ever hand-editing HTML.

  python scripts/i18n_pipeline.py extract
  python scripts/i18n_pipeline.py coverage [--json out.json]
"""
import argparse
import json
import pathlib
import re
import sys

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = ROOT / "i18n"
LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
ATTRS = ("alt", "title", "aria-label", "placeholder", "content", "data-short",
         "data-title", "data-days")
SKIP_TAGS = {"script", "style", "svg", "path", "rect", "line", "polyline", "circle"}
ARABIC = re.compile(r"[\u0600-\u06FF]")


def keyed(html_text):
    """{key: (kind, value, node, attr)} for every translatable string."""
    doc = LH.fromstring(html_text)
    out = {}

    def path_of(el):
        parts = []
        node = el
        while node is not None and node.tag not in ("html", "#document"):
            parent = node.getparent()
            if parent is None:
                break
            same = [c for c in parent if isinstance(c.tag, str) and c.tag == node.tag]
            parts.append(f"{node.tag}[{same.index(node)}]")
            node = parent
        return "/" + "/".join(reversed(parts))

    def visit(el, skip):
        if not isinstance(el.tag, str):
            return
        if el.tag in SKIP_TAGS:
            skip = True
        if not skip:
            base = path_of(el)
            if el.text and el.text.strip():
                out[base + "/text()"] = ("text", el.text, el, "text")
            for attr in ATTRS:
                value = el.get(attr)
                if value and value.strip() and (ARABIC.search(value) or attr != "content"):
                    out[base + "/@" + attr] = ("attr", value, el, attr)
        for child in el:
            visit(child, skip)

    visit(doc.getroottree().getroot(), False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["extract", "coverage"])
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    master_html = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    master = keyed(master_html)

    # keys that must stay identical everywhere: no Arabic inside, pure numbers/symbols
    translatable = {k: v for k, v in master.items()
                    if ARABIC.search(v[1]) or re.search(r"[A-Za-z]{3,}", v[1])}

    if args.action == "extract":
        I18N.mkdir(exist_ok=True)
        payload = {k: {"kind": v[0], "ar": v[1]} for k, v in master.items()}
        (I18N / "_master.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"master keys: {len(master)} (translatable {len(translatable)}) -> i18n/_master.json")
        return 0

    I18N.mkdir(exist_ok=True)
    rows, coverage = [], {}
    for lang in LANGS:
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        target = keyed(page.read_text(encoding="utf-8", errors="replace"))
        translated = same = missing = 0
        missing_keys = []
        for key, (kind, ar_value, _node, _attr) in translatable.items():
            found = target.get(key)
            if not found:
                missing += 1
                if len(missing_keys) < 200:
                    missing_keys.append(key)
            elif found[1].strip() == ar_value.strip():
                same += 1
            else:
                translated += 1
        total = len(translatable)
        done = (translated + same - 0) / total if total else 0
        coverage[lang] = {"total": total, "translated": translated,
                          "same_as_master": same, "missing": missing,
                          "translated_ratio": round(translated / total, 3),
                          "missing_keys": missing_keys}
        rows.append((lang, total, translated, same, missing, translated / total))

    (I18N / "coverage.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{'lang':6}{'keys':>7}{'translated':>12}{'same as AR':>12}{'missing':>9}{'coverage':>10}")
    print("-" * 58)
    for lang, total, tr, same, miss, ratio in rows:
        print(f"{lang:6}{total:>7}{tr:>12}{same:>12}{miss:>9}{ratio:>10.1%}")
    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(coverage, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
