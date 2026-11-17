#!/usr/bin/env python3
"""Remove unmatched (orphan) </div> closes - the pre-existing damage the old
buggy sync tool left on every re-run (container_old = group(1)+group(2)+'</div>'
swallowed one parent close too many).

An unmatched </div> is IGNORED by every browser, so deleting it is a rendering
no-op; the fix restores a clean, auditable DOM without changing any layout.
Proof: the lxml DOM serialized before and after must be byte-identical.

Comment- and <script>-aware: div tokens inside HTML comments or script blocks
are not real DOM tags and are skipped. Pages whose imbalance is negative
(missing closes, e.g. en) are NOT touched by this tool.
"""
import re
import sys
from lxml import html as LH

sys.stdout.reconfigure(encoding='utf-8')


def orphan_spans(raw):
    """Absolute (start, end) spans of real orphan </div> tokens."""
    spans = []
    depth = 0
    # mask out comments and script blocks, but remember the raw offsets
    mask = list(raw)
    for m in re.finditer(r'<!--.*?-->|<script\b.*?</script\s*>', raw, re.DOTALL | re.IGNORECASE):
        for i in range(m.start(), m.end()):
            mask[i] = '\x00'
    masked = ''.join(mask)
    for m in re.finditer(r'<div\b|</div\s*>', masked):
        if m.group(0).startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                depth = 0
                spans.append((m.start(), m.end()))
    return spans


def dom_fingerprint(raw):
    doc = LH.fromstring(raw)
    return LH.tostring(doc, encoding='unicode')


def fix_page(path, write=True):
    raw = open(path, encoding='utf-8').read()
    o = len(re.findall(r'<div\b', raw))
    c = raw.count('</div>')
    if c <= o:
        return None  # nothing to delete (or negative damage - separate repair)
    before = dom_fingerprint(raw)
    spans = orphan_spans(raw)
    if not spans:
        return None
    out, last = [], 0
    for s, e in spans:
        out.append(raw[last:s])
        last = e
    out.append(raw[last:])
    fixed = ''.join(out)
    after = dom_fingerprint(fixed)
    if before != after:
        return 'DOM-MISMATCH-REFUSED'
    if write:
        open(path, 'w', encoding='utf-8').write(fixed)
    return len(spans)


def main():
    import glob
    import os
    os.chdir('/home/z/my-project/SR-CoreSync-For-Intelgent-Solutions')
    pages = ['index.html'] + sorted(glob.glob('*/index.html'))
    total = 0
    for p in pages:
        r = fix_page(p)
        if r is None:
            print(f'{p:<22} skip (no positive orphan damage)')
        elif r == 'DOM-MISMATCH-REFUSED':
            print(f'{p:<22} REFUSED - DOM would change, manual review needed')
        else:
            print(f'{p:<22} removed {r} orphan </div>')
            total += r
    print(f'\ntotal orphans removed: {total}')


if __name__ == '__main__':
    main()
