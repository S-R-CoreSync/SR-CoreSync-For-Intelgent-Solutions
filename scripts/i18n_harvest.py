#!/usr/bin/env python3
"""Fuzzy translation harvest: pair master strings with existing translations by
element signature (tag + class list + attribute), not by DOM path.

Path alignment failed because the localized pages moved blocks around; a caption
still lives inside h5.tech-name, only at a different offset. Grouping elements by
signature and pairing them in order recovers those translations without asking a
translator to redo them.

  python scripts/i18n_harvest.py [--min-group 1]
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
ATTRS = ("alt", "title", "aria-label", "placeholder", "data-short", "data-title", "data-days")
SKIP = {"script", "style", "svg", "path", "rect", "line", "polyline", "circle"}
ARABIC = re.compile(r"[\u0600-\u06FF]")


def norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def signature(el, attr):
    classes = " ".join(sorted((el.get("class") or "").split()))
    return f"{el.tag}|{classes}|{attr}"


def collect(html_text):
    """{key: {sig, value}} for every translatable string, keyed by DOM path."""
    doc = LH.fromstring(html_text)
    out = {}

    def path_of(el):
        parts, node = [], el
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
        if el.tag in SKIP:
            skip = True
        if not skip:
            base = path_of(el)
            if el.text and el.text.strip():
                out[base + "/text()"] = {"sig": signature(el, "text"), "value": norm(el.text),
                                         "key": base + "/text()", "attr": "text", "el": el}
            for attr in ATTRS:
                value = el.get(attr)
                if value and value.strip():
                    out[base + "/@" + attr] = {"sig": signature(el, "@" + attr), "value": norm(value),
                                               "key": base + "/@" + attr, "attr": attr, "el": el}
        for child in el:
            visit(child, skip)

    visit(doc.getroottree().getroot(), False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-group", type=int, default=1)
    args = ap.parse_args()

    master = collect((ROOT / "index.html").read_text(encoding="utf-8", errors="replace"))
    translatable = {k: v for k, v in master.items()
                    if ARABIC.search(v["value"]) or re.search(r"[A-Za-z]{3,}", v["value"])}

    by_sig = {}
    for key, item in translatable.items():
        by_sig.setdefault(item["sig"], []).append(key)

    I18N.mkdir(exist_ok=True)
    rows = []
    for lang in LANGS:
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        target = collect(page.read_text(encoding="utf-8", errors="replace"))
        t_by_sig = {}
        for key, item in target.items():
            t_by_sig.setdefault(item["sig"], []).append(item)

        catalog, harvested, same = {}, 0, 0
        for sig, keys in by_sig.items():
            candidates = t_by_sig.get(sig, [])
            if len(candidates) != len(keys):
                continue          # ambiguous pairing: leave for the translator
            for key, cand in zip(keys, candidates):
                value = cand["value"]
                if not value:
                    continue
                if value == translatable[key]["value"]:
                    same += 1
                    continue
                catalog[key] = value
                harvested += 1
        (I18N / f"{lang}.json").write_text(
            json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")
        total = len(translatable)
        rows.append((lang, total, harvested, same, total - harvested - same))

    print(f"{'lang':6}{'keys':>7}{'harvested':>11}{'still AR':>10}{'unpaired':>10}{'coverage':>10}")
    print("-" * 56)
    for lang, total, harv, same, unpaired in rows:
        print(f"{lang:6}{total:>7}{harv:>11}{same:>10}{unpaired:>10}{harv/total:>10.1%}")
    print()
    print("written:", sorted(p.name for p in I18N.glob('*.json'))[:6], "...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
