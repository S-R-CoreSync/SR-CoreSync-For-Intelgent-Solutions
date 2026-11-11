#!/usr/bin/env python3
"""Render a language page from the Arabic master plus its text catalog.

The master owns structure. The catalog owns words. Nothing else is allowed to
differ, so a new card or section reaches every language by editing the master and
re-running this command.

  python scripts/build_pages.py --lang de --check
  python scripts/build_pages.py --lang de --preview scratch/preview

--check  reports the keys that block the render and writes nothing.
Without it the page is written only when every key resolves: fail closed, so the
Arabic master can never leak into a localized page.
"""
import argparse
import json
import pathlib
import re
import sys

from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = ROOT / "i18n"
ATTRS = ("alt", "title", "aria-label", "placeholder", "data-short", "data-title", "data-days")
SKIP = {"script", "style", "svg", "path", "rect", "line", "polyline", "circle"}
RTL = {"ar", "ku", "ckb"}


def norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def walk(doc):
    """Yield (key, kind, node, attr) for every translatable slot."""
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

    out = []

    def visit(el, skip):
        if not isinstance(el.tag, str):
            return
        if el.tag in SKIP:
            skip = True
        if not skip:
            base = path_of(el)
            if el.text and el.text.strip():
                out.append((base + "/text()", "text", el, "text"))
            for attr in ATTRS:
                if el.get(attr) and el.get(attr).strip():
                    out.append((base + "/@" + attr, "attr", el, attr))
        for child in el:
            visit(child, skip)

    visit(doc.getroottree().getroot(), False)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview", default="")
    ap.add_argument("--allow-master-fallback", action="store_true")
    args = ap.parse_args()

    catalog_path = I18N / f"{args.lang}.json"
    if not catalog_path.exists():
        print(f"no catalog for {args.lang}: {catalog_path}")
        return 2
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    master_html = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    doc = LH.fromstring(master_html)
    slots = walk(doc)

    # only strings the master actually needs translated block the render;
    # numbers, brand names and code-like values stay as they are.
    master_map = json.loads((I18N / "_master.json").read_text(encoding="utf-8"))
    ARABIC = re.compile(r"[\u0600-\u06FF]")
    required = {k for k, v in master_map.items()
                if ARABIC.search(v["ar"]) or re.search(r"[A-Za-z]{3,}", v["ar"])}

    missing, filled = [], 0
    for key, kind, node, attr in slots:
        if key not in required:
            continue
        value = catalog.get(key)
        if value is None:
            missing.append(key)
            continue
        if kind == "text":
            lead = node.text[:len(node.text) - len(node.text.lstrip())]
            node.text = lead + value
        else:
            node.set(attr, value)
        filled += 1

    print(f"{args.lang}: {len(slots)} slots, {filled} from catalog, {len(missing)} missing")
    if missing:
        for key in missing[:8]:
            print("   missing", key)

    if args.check:
        return 1 if missing else 0

    if missing and not args.allow_master_fallback:
        print("refusing to write: the catalog is incomplete (fail closed)")
        return 1

    # language chrome
    doc.set("lang", args.lang)
    html_el = doc.find("html")
    if html_el is not None:
        html_el.set("lang", args.lang)
        html_el.set("dir", "rtl" if args.lang in RTL else "ltr")

    rendered = LH.tostring(doc, encoding="unicode", method="html")
    target = (pathlib.Path(args.preview) if args.preview else ROOT / args.lang) / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8", newline="")
    print(f"wrote {target} ({len(rendered):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
