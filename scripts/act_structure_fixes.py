"""Structural chapters (Acts 9-11) for the master page and the ckb mirror.

Each act is idempotent: running it twice changes nothing.

  Act 9  single <h1> per document      -> the <noscript> brand headline becomes <p>
  Act 10 unique element ids            -> 2nd id="..." occurrences get a distinct name
  Act 11 live internal anchors         -> dead footer anchors point at real targets

Usage:  python scripts/act_structure_fixes.py --act 9|10|11 [--dry-run] [--all]
"""
import argparse
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MASTER = 'index.html'
CKB = 'ckb/index.html'

NOSCRIPT_H1 = '<h1 style="color:#f3dfba;">S&R CoreSync For Intelligent Solutions</h1>'
NOSCRIPT_P = ('<p style="color:#f3dfba;font-size:1.6rem;font-weight:700;line-height:1.3;margin:0 0 .75rem;">'
              'S&amp;R CoreSync For Intelligent Solutions</p>')

RENAMES = {
    'index.html': [
        ('checkoutItemTitle', 'socialCheckoutItemTitle'),
        ('newsletterForm', 'newsletterFormFooter'),
        ('softwareGridContainer', 'softwareGridContainerWl'),
    ],
    'ckb/index.html': [
        ('checkoutItemTitle', 'socialCheckoutItemTitle'),
    ],
}

DEAD_ANCHORS = [
    ('href="#privacy-preferences"', 'href="privacy.html#cookies"'),
]


def read(path):
    with open(path, 'r', encoding='utf-8', newline='') as fh:
        return fh.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def act9(text, path):
    if path != MASTER or NOSCRIPT_H1 not in text:
        return text, 0
    return text.replace(NOSCRIPT_H1, NOSCRIPT_P, 1), 1


def act10(text, path):
    changed = 0
    for old, new in RENAMES.get(path, []):
        hits = [m.start() for m in re.finditer(r'id="' + old + r'"', text)]
        if len(hits) < 2:
            continue
        pos = hits[1]
        literal = 'id="' + old + '"'
        text = text[:pos] + 'id="' + new + '"' + text[pos + len(literal):]
        changed += 1
    return text, changed


def act11(text, path):
    changed = 0
    for old, new in DEAD_ANCHORS:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


ACTS = {9: act9, 10: act10, 11: act11}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--act', type=int, choices=sorted(ACTS), required=True)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--all', action='store_true', help='also patch ckb/index.html where applicable')
    args = ap.parse_args()

    targets = [MASTER] + ([CKB] if args.all or args.act == 10 else [])
    total = 0
    for path in dict.fromkeys(targets):
        text = read(path)
        new_text, changed = ACTS[args.act](text, path)
        state = 'would change' if args.dry_run else 'changed'
        print(f'Act {args.act} | {path:<18} | {state}: {changed}')
        total += changed
        if changed and not args.dry_run:
            write(path, new_text)
    print(f'Act {args.act} total -> {total} edit(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
