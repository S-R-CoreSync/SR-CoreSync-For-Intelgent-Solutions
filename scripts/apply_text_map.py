"""Apply English→translation replacements tolerantly.

Plain string replacement failed on 6 of 13 strings because the markup splits a
sentence or encodes "&" as "&amp;". This matches the same sentence across
whitespace runs, HTML entities and simple inline tags, then replaces it with the
translated text.

  python scripts/apply_text_map.py --lang de --map map.json [--dry-run]
"""
import argparse, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INLINE = r"(?:br|span|strong|em|b|i|small|sup)"


def pattern_for(text):
    parts = [re.escape(w) for w in text.split()]
    gap = rf"(?:\s|&nbsp;|<{INLINE}\b[^>]*>|</{INLINE}>)+"
    body = gap.join(parts)
    body = body.replace(re.escape("&"), "(?:&amp;|&)")
    return re.compile(body, re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pairs = json.loads(pathlib.Path(args.map).read_text(encoding="utf-8"))
    page = ROOT / args.lang / "index.html"
    text = page.read_text(encoding="utf-8", errors="replace")

    done, missed = 0, []
    for source, target in pairs.items():
        rx = pattern_for(source)
        text, n = rx.subn(html.escape(target, quote=False), text, count=1)
        if n:
            done += 1
        else:
            missed.append(source[:60])

    print(f"{args.lang}: applied {done}/{len(pairs)}")
    for m in missed:
        print("   missed:", m)

    if args.dry_run:
        print("dry run")
        return 0
    page.write_text(text, encoding="utf-8", newline="")
    print("wrote", page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
