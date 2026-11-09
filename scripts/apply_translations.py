# -*- coding: utf-8 -*-
"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY

Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
Unauthorized copying, decompilation, redistribution, or external model training
of this file, via any medium, is strictly prohibited.
==============================================================================
"""

"""
Apply a translation catalog to a portal
=======================================

`scripts/extract_translation_gaps.py` produces the list of English strings a
language still shows. This tool consumes the filled-in counterpart:

    i18n/translations/<lang>.json     {"English source": "localized text"}

and rewrites the portal's **text nodes only**. Attributes and markup are never
touched by the node pass, so a translation containing `<`, `&` or a quote cannot
break the document. A separate, explicit pass covers the handful of user-facing
attributes (alt, title, aria-label, placeholder) where English also leaks.

Why text nodes and not a global string replace: the English sentence
"Enterprise AI & LLM Automation" also appears inside JSON-LD and URL slugs on
some pages. Replacing globally would corrupt structured data that search engines
read. Restricting the pass to text between `>` and `<`, outside script/style,
keeps the machine-readable layer intact.

Idempotent: a string that is already translated is no longer present, so a second
run changes nothing.

Usage:
    python scripts/apply_translations.py --lang no --dry-run
    python scripts/apply_translations.py --lang no
    python scripts/apply_translations.py --all
"""
import argparse
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS_DIR = os.path.join(ROOT, 'scripts', 'i18n', 'translations')

SKIP_BLOCK = re.compile(r'(?is)<(script|style|noscript|template)\b.*?</\1>')
TEXT_NODE = re.compile(r'>([^<>]{2,})<')
ATTR = re.compile(r'(?is)\b(alt|title|aria-label|placeholder)\s*=\s*"([^"]{4,})"')


def load_catalog(lang):
    path = os.path.join(TRANS_DIR, lang + '.json')
    if not os.path.exists(path):
        return None, path
    with io.open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    if isinstance(data, dict) and 'strings' in data and isinstance(data['strings'], dict):
        data = data['strings']
    return {k: v for k, v in data.items() if isinstance(v, str) and v.strip()}, path


def protect(text):
    """Swap script/style blocks out so their contents are never rewritten."""
    stash = []

    def repl(match):
        stash.append(match.group(0))
        return '\x00BLOCK%d\x00' % (len(stash) - 1)

    return SKIP_BLOCK.sub(repl, text), stash


def restore(text, stash):
    for index, block in enumerate(stash):
        text = text.replace('\x00BLOCK%d\x00' % index, block)
    return text


def apply_to_html(text, catalog):
    text, stash = protect(text)
    applied = []

    def node_repl(match):
        inner = match.group(1)
        stripped = ' '.join(inner.split())
        replacement = catalog.get(stripped)
        if replacement is None:
            return match.group(0)
        applied.append(stripped)
        return '>' + inner.replace(stripped, replacement) + '<'

    text = TEXT_NODE.sub(node_repl, text)

    def attr_repl(match):
        name, value = match.group(1), match.group(2)
        replacement = catalog.get(' '.join(value.split()))
        if replacement is None:
            return match.group(0)
        applied.append('[' + name + '] ' + value)
        return '%s="%s"' % (name, replacement)

    text = ATTR.sub(attr_repl, text)
    return restore(text, stash), applied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', nargs='*', default=None)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if args.all:
        langs = sorted(os.path.splitext(os.path.basename(p))[0]
                       for p in glob.glob(os.path.join(TRANS_DIR, '*.json')))
    else:
        langs = args.lang or []

    if not langs:
        print('nothing to do: pass --lang <code> or --all')
        print('translation files live in i18n/translations/<lang>.json')
        return 0

    total = 0
    for lang in langs:
        catalog, path = load_catalog(lang)
        if catalog is None:
            print('%-4s no catalog at %s' % (lang, os.path.relpath(path, ROOT)))
            continue
        pages = [os.path.join(ROOT, lang, 'index.html')] if lang != 'ar' else [os.path.join(ROOT, 'index.html')]
        demo = os.path.join(ROOT, lang, 'demo.html')
        if os.path.exists(demo):
            pages.append(demo)

        for page in pages:
            if not os.path.exists(page):
                continue
            with io.open(page, 'r', encoding='utf-8', newline='') as fh:
                text = fh.read()
            new_text, applied = apply_to_html(text, catalog)
            rel = os.path.relpath(page, ROOT).replace('\\', '/')
            if not applied:
                print('%-4s %-24s no change' % (lang, rel))
                continue
            total += len(applied)
            print('%-4s %-24s %3d replacement(s)%s'
                  % (lang, rel, len(applied), '  [dry run]' if args.dry_run else ''))
            for item in applied[:3]:
                print('        %s' % item[:88])
            if not args.dry_run:
                with io.open(page, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(new_text)

    print('-' * 70)
    print('%s: %d replacement(s)' % ('DRY RUN' if args.dry_run else 'APPLIED', total))
    return 0


if __name__ == '__main__':
    sys.exit(main())
