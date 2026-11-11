"""Point localized pages at the root copy of a shared page.

  python scripts/fix_localized_root_links.py [--apply]

A page in de/ that links "./whitelabel-calculator.html" asks for
de/whitelabel-calculator.html, which does not exist: the file lives at the root.
validate_publish_set.py fails the build on it. The same class of error hides in
every language, so this checks all of them against the real file system.
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r'href="(\.?/?[A-Za-z0-9_\-./]+\.html)(\?[^"]*)?"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    changed = 0
    for page in sorted(ROOT.glob("*/index.html")):
        lang = page.parent.name
        raw = page.read_text(encoding="utf-8", errors="replace")
        hits = []

        def fix(m):
            target, query = m.group(1), m.group(2) or ""
            if target.startswith(("../", "/", "http")):
                return m.group(0)
            name = target[2:] if target.startswith("./") else target
            if (page.parent / name).exists():
                return m.group(0)
            if (ROOT / name).exists():
                hits.append(name)
                return 'href="../%s%s"' % (name, query)
            return m.group(0)

        new = LINK.sub(fix, raw)
        if hits:
            changed += 1
            print(f"{lang:5} {len(hits):>3} link(s) -> ../  {sorted(set(hits))[:4]}")
            if args.apply:
                page.write_text(new, encoding="utf-8", newline="")
    print(f"{changed} page(s) with references fixed to the root copy")
    if not args.apply:
        print("dry run - pass --apply to write")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
