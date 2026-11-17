#!/usr/bin/env python3
"""Guard 12: full-site HTML tag balance (approved suggestion #17).

The 2026-11-18 cleanup proved 29/29 index pages carried damage from the old
buggy sync tool: 132 orphan </div> closes (browser-ignored junk that still
broke DOM audits) and 6 missing closes on en (real nesting damage). The
cleanup fixed the 29 index pages; this guard locks the ENTIRE site (232+
pages) so no future tool can reintroduce the same class of damage anywhere.

Browser-semantics balance, comment/script/style aware:
- orphan close  </X> with no open match          => error (the old tool's signature)
- unclosed <div> at end of file (div-level only) => error (en's accordion signature)
- implied end tags (</p>, </li>, </td>... in HTML) are tolerated, so ordinary
  HTML shorthand never false-positives;
- inside <svg>/<math> foreign content, tags are XML-style: /> self-closes and
  every close must match exactly.

Usage: python3 scripts/check_tag_balance_all.py   (exit 1 on any fault)
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SKIP_DIRS = {'.git', 'node_modules', 'partials'}  # partials = unpublished build fragments
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}

TOKEN = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>',
                   re.DOTALL)
MASK = re.compile(r'<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>',
                  re.DOTALL | re.IGNORECASE)
SELF_CLOSE = re.compile(r'/\s*$')


def balance_errors(raw):
    """Return (orphans, unclosed_divs) for one HTML source string.

    Matching follows the browser tree builder closely enough for damage
    detection: a close tag matches if the tag is open anywhere below it (the
    "any other end tag" step pops everything above it), implied end tags are
    never a mismatch, and <svg>/<math> content is XML-strict."""
    mask = list(raw)
    for m in MASK.finditer(raw):
        for i in range(m.start(), m.end()):
            mask[i] = '\x00'
    masked = ''.join(mask)

    stack = []          # (tag, is_foreign)
    foreign_depth = 0   # >0 while inside <svg>/<math> content
    orphans = []
    for m in TOKEN.finditer(masked):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        in_foreign = foreign_depth > 0
        if closing:
            if in_foreign:
                if tag == 'svg' or tag == 'math':
                    pos = next((i for i in range(len(stack) - 1, -1, -1)
                                if stack[i] == (tag, True)), None)
                    if pos is None:
                        orphans.append(tag)
                    else:
                        del stack[pos:]
                        foreign_depth -= 1
                elif stack and stack[-1] == (tag, True):
                    stack.pop()
                else:
                    orphans.append(tag)
                continue
            pos = next((i for i in range(len(stack) - 1, -1, -1)
                        if stack[i] == (tag, False)), None)
            if pos is None:
                orphans.append(tag)
            else:
                del stack[pos:]   # any-other-end-tag: pop through everything above
            continue
        # open tag
        if tag == 'svg' or tag == 'math':
            if not SELF_CLOSE.search(attrs):
                stack.append((tag, True))
                foreign_depth += 1
            continue
        if tag in VOID and not in_foreign:
            continue
        if in_foreign and SELF_CLOSE.search(attrs):
            continue          # XML-style self-close inside foreign content
        stack.append((tag, in_foreign))

    unclosed = [t for t, f in stack if not f and t == 'div']
    return orphans, unclosed


def html_files(root='.'):
    """The guard's scope is exactly the PUBLISH SET (what GitHub Pages serves).

    publish_set.iter_publish_files() is the single authority: it excludes the
    underscore-prefixed dirs, partials/ fragments, the EXCLUDED_DEV_PAGES
    previews (e.g. preview-hero-v2.html - intentionally damaged dev replicas
    that are never reachable live) and the other server-side material. The
    directory walk below is only a fallback if that import ever breaks."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from publish_set import iter_publish_files
        return sorted(p for p in iter_publish_files(root)
                      if p.lower().endswith('.html'))
    except Exception as e:                                   # pragma: no cover
        print(f'(publish_set unavailable: {e} - falling back to a raw walk)')
        out = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if not d.startswith('_') and d not in SKIP_DIRS]
            for fn in filenames:
                if fn.lower().endswith('.html'):
                    out.append(os.path.join(dirpath, fn))
        return sorted(out)


def main():
    faults = []
    checked = 0
    for path in html_files():
        with open(path, encoding='utf-8', errors='replace') as f:
            raw = f.read()
        orphans, unclosed = balance_errors(raw)
        checked += 1
        for tag in sorted(set(orphans)):
            faults.append(f'{path}: orphan </{tag}> x{orphans.count(tag)}')
        if unclosed:
            faults.append(f'{path}: unclosed <div> x{len(unclosed)} at EOF')

    if faults:
        print(f'FAIL tag balance (full site) - {checked} pages, '
              f'{len(faults)} fault(s):')
        for f in faults:
            print('  -', f)
        sys.exit(1)
    print(f'PASS tag balance (full site) - {checked} pages, '
          f'0 orphans, 0 unclosed divs')


if __name__ == '__main__':
    main()
