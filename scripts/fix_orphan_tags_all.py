#!/usr/bin/env python3
"""Delete orphan closing tags across the whole site - the general form of
fix_orphan_divs.py (which covered </div> on the 29 index pages only).

Suggestion #17 (approved 2026-11-18) revealed the old tool's damage went
beyond div: 61x </aside>, 31x </li>, 28x </section>, 9x </div>, 2x </main>,
1x </picture> and duplicated </body></html> tails across live pages. An end
tag with no matching open element is a parse error that every browser
ignores, so deleting it must be a rendering no-op - PROVEN per page: the
lxml DOM serialized before and after must be byte-identical, otherwise the
page is reverted untouched and reported for manual review.

Skipped on purpose:
- </p> orphans: the browser INSERTS an empty <p> for a stray </p>, so
  deletion is NOT DOM-neutral there; such pages are reported for manual
  fixes (en's case was a malformed-attribute tag, fixed by hand);
- partials/ (unpublished build fragments).

Usage: python3 scripts/fix_orphan_tags_all.py [--check-only]
"""
import argparse
import os
import re
import sys

from lxml import html as LH

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_tag_balance_all import MASK, TOKEN, VOID, html_files

SKIP_TAGS = {'p'}   # browser inserts an empty <p> for a stray </p> - manual only
SELF = re.compile(r'/\s*$')


def orphan_spans(raw):
    """Absolute (start, end) spans of real orphan closing tags (skip p)."""
    mask = list(raw)
    for m in MASK.finditer(raw):
        for i in range(m.start(), m.end()):
            mask[i] = '\x00'
    masked = ''.join(mask)

    stack = []          # (tag, is_foreign, span_start_of_close if orphan... n/a)
    foreign_depth = 0
    spans = []
    for m in TOKEN.finditer(masked):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        in_foreign = foreign_depth > 0
        if closing:
            if in_foreign:
                if tag in ('svg', 'math'):
                    pos = next((i for i in range(len(stack) - 1, -1, -1)
                                if stack[i][0] == tag and stack[i][1]), None)
                    if pos is None:
                        spans.append((m.start(), m.end(), tag))
                    else:
                        del stack[pos:]
                        foreign_depth -= 1
                elif stack and stack[-1][0] == tag and stack[-1][1]:
                    stack.pop()
                else:
                    spans.append((m.start(), m.end(), tag))
                continue
            pos = next((i for i in range(len(stack) - 1, -1, -1)
                        if stack[i][0] == tag and not stack[i][1]), None)
            if pos is None:
                spans.append((m.start(), m.end(), tag))
            else:
                del stack[pos:]
            continue
        if tag in ('svg', 'math'):
            if not SELF.search(attrs):
                stack.append((tag, True, None))
                foreign_depth += 1
            continue
        if tag in VOID and not in_foreign:
            continue
        if in_foreign and SELF.search(attrs):
            continue
        stack.append((tag, in_foreign, None))
    return [(s, e, t) for s, e, t in spans if t not in SKIP_TAGS]


def dom_fingerprint(raw):
    return LH.tostring(LH.fromstring(raw), encoding='unicode')


def fix_page(path, write=True):
    raw = open(path, encoding='utf-8').read()
    spans = orphan_spans(raw)
    if not spans:
        return None
    # delete from the end so earlier spans stay valid
    fixed = raw
    for s, e, t in sorted(spans, reverse=True):
        # also swallow one leading whitespace run if the close sat alone on a line
        fixed = fixed[:s] + fixed[e:]
    if dom_fingerprint(raw) != dom_fingerprint(fixed):
        return 'DOM-CHANGED'
    if write:
        open(path, 'w', encoding='utf-8').write(fixed)
    return f'removed x{len(spans)}: ' + ','.join(sorted({t for _, _, t in spans}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    touched, changed, skipped = 0, 0, 0
    for path in html_files():
        result = fix_page(path, write=not a.check_only)
        if result is None:
            continue
        touched += 1
        if result == 'DOM-CHANGED':
            skipped += 1
            print(f'MANUAL  {path}: orphan removal would change the DOM')
        else:
            changed += 1
            print(f'FIXED   {path}: {result}')
    print(f'\n{touched} faulted page(s): {changed} fixed, {skipped} need manual work'
          + (' (check-only run - nothing written)' if a.check_only else ''))


if __name__ == '__main__':
    main()
