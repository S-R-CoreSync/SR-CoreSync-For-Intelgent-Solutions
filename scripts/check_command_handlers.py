#!/usr/bin/env python3
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
Inline command handler audit (engine-agnostic).
==============================================
History: the 28 localized homepages shipped twelve hero chips each calling
showStudioPeek(...) while neither the function nor its overlay travelled with
the translation batch. Nothing failed at load time - the buttons were simply
dead - and only the headless browser audit caught it, one published release
later. check_dock_handler.py guards that exact handler; this gate generalises
the invariant to every handler a page calls from markup:

    a function called from an inline event attribute must be defined either
    in that page's inline scripts or in a local script file the page loads.

External (http/https) scripts are skipped: their definitions cannot be read
here, so a name that a page only defines through a CDN is never flagged.

Usage:
  python scripts/check_command_handlers.py            # report + gate
  python scripts/check_command_handlers.py --verbose  # list every handler
Exit 0 = invariant holds, 1 = undefined handler found.
"""
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HANDLER_ATTR_RE = re.compile(
    r'''\son[a-z]+\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.I)
CALL_RE = re.compile(r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(')
SCRIPT_SRC_RE = re.compile(
    r'''<script\b[^>]*\bsrc\s*=\s*(?:"([^"]+)"|'([^']+)')''', re.I)
INLINE_SCRIPT_RE = re.compile(
    r'(?is)<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>')

# Tokens that look like calls but are language constructs or browser built-ins.
BUILTINS = {
    'if', 'for', 'while', 'switch', 'catch', 'return', 'typeof', 'function',
    'new', 'this', 'event', 'document', 'window', 'console', 'alert', 'confirm',
    'prompt', 'parseInt', 'parseFloat', 'number', 'string', 'boolean', 'array',
    'object', 'json', 'math', 'date', 'regexp', 'encodeURIComponent',
    'decodeURIComponent', 'encodeURI', 'decodeURI', 'setTimeout', 'setInterval',
    'clearTimeout', 'clearInterval', 'isNaN', 'isFinite', 'history', 'location',
    'navigator', 'localStorage', 'sessionStorage', 'url', 'blob', 'FileReader',
    'URLSearchParams', 'requestAnimationFrame', 'structuredClone', 'fetch',
    'String', 'Number', 'Boolean', 'Array', 'Object', 'JSON', 'Math', 'Date',
    'RegExp', 'Error', 'Promise', 'Map', 'Set', 'Intl', 'AbortController',
    'Image', 'Audio', 'Event', 'CustomEvent', 'FormData', 'Headers', 'Request',
    'Response', 'XMLHttpRequest', 'WebSocket', 'IntersectionObserver',
    'MutationObserver', 'ResizeObserver', 'Notification', 'BarcodeDetector',
    'matchMedia', 'getComputedStyle', 'scrollTo', 'open', 'close', 'print',
    'focus', 'blur', 'postMessage', 'eval', 'atob', 'btoa', 'void', 'delete',
}


def tracked_pages():
    out = subprocess.run(
        ['git', 'ls-files', '*.html'], cwd=ROOT, capture_output=True,
        text=True, check=True).stdout.splitlines()
    keep = []
    for rel in out:
        parts = rel.split('/')
        if parts[0] in ('_site', 'dist', 'downloads', 'templates', 'workers',
                        'scripts', 'deploy', 'sdk', 'docs', 'node_modules'):
            continue
        if len(parts) <= 2 and (parts[-1] in ('index.html', 'demo.html')):
            keep.append(rel)
    return sorted(keep)


def read_text(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read()
    except OSError:
        return ''


def local_scripts(html, page_rel):
    """Script files the page loads from this repository, resolved on disk."""
    paths = []
    for match in SCRIPT_SRC_RE.finditer(html):
        src = (match.group(1) or match.group(2) or '').strip()
        if not src or src.startswith(('http://', 'https://', '//', 'data:')):
            continue
        src = src.split('?')[0].split('#')[0]
        base = os.path.dirname(os.path.join(ROOT, page_rel))
        target = os.path.normpath(os.path.join(base, src))
        if os.path.isfile(target):
            paths.append(target)
    return paths


DEFINITION_CACHE = {}


def definitions_in(text):
    names = set()
    for match in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\(', text):
        names.add(match.group(1))
    for match in re.finditer(
            r'(?:window|global|globalThis)\.([A-Za-z_$][\w$]*)\s*=', text):
        names.add(match.group(1))
    for match in re.finditer(
            r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*=\s*(?:function|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)',
            text):
        names.add(match.group(1))
    for match in re.finditer(r'^\s*([A-Za-z_$][\w$]*)\s*:\s*function', text, re.M):
        names.add(match.group(1))
    return names


def file_definitions(path):
    if path not in DEFINITION_CACHE:
        DEFINITION_CACHE[path] = definitions_in(read_text(path))
    return DEFINITION_CACHE[path]


def page_calls(html):
    calls = {}
    for match in HANDLER_ATTR_RE.finditer(html):
        code = match.group(1) if match.group(1) is not None else match.group(2)
        for name in CALL_RE.findall(code or ''):
            if name.lower() in BUILTINS:
                continue
            calls[name] = calls.get(name, 0) + 1
    return calls


def main():
    verbose = '--verbose' in sys.argv
    pages = tracked_pages()
    failures = []
    total_handlers = 0

    for rel in pages:
        html = read_text(os.path.join(ROOT, rel))
        calls = page_calls(html)
        if not calls:
            continue
        total_handlers += len(calls)

        defined = definitions_in(html)
        for script in local_scripts(html, rel):
            defined |= file_definitions(script)

        missing = sorted(name for name in calls if name not in defined)
        if verbose:
            print('  %-46s handlers=%d missing=%s'
                  % (rel, len(calls), ','.join(missing) if missing else '-'))
        if missing:
            failures.append((rel, missing))

    print('=' * 74)
    print('Inline handler invariant: a markup call requires a definition')
    print('=' * 74)
    print('  pages audited          : %d' % len(pages))
    print('  handler names resolved : %d' % total_handlers)

    if failures:
        for rel, missing in failures:
            print('  X %-44s undefined: %s' % (rel, ', '.join(missing)))
        print('-' * 74)
        print('FAILED - %d page(s) call a handler no loaded script defines.'
              % len(failures))
        return 1

    print('  every inline handler call site has a local definition')
    print('=' * 74)
    print('PASSED - inline handler invariant holds.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
