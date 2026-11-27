# -*- coding: utf-8 -*-
"""Swap the emblem artwork for the owner's circular official badge.

Targets, by role rather than by file name:
  * header emblem      .brand-emblem-img / -sm / .portal-brand-emblem
  * hero orb           .c3-orb-img
  * showcase slide     .showcase-img inside the emblem view (banner 16:9)
  * full-screen logo   .sr-logo-full-render

Idempotent: a second run reports 0 changes.
"""
import argparse
import io
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = re.compile(r'<img\b[^>]*>', re.S)
SRC = re.compile(r'src="[^"]*"')
SRCSET = re.compile(r'srcset="[^"]*"')
SOURCE = re.compile(r'<source\b[^>]*>', re.S)


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, encoding='utf-8')
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def prefix_for(rel):
    parts = rel.split('/')
    if parts[0] == 'partials':
        return '../' if len(parts) > 2 else './'
    depth = len(parts) - 1
    return './' if depth == 0 else '../' * depth


def badge_set(p, role):
    if role == 'header':
        return ('%sassets/sr-badge-official-192w.webp' % p,
                '%sassets/sr-badge-official-64w.webp 64w, %sassets/sr-badge-official-96w.webp 96w, '
                '%sassets/sr-badge-official-192w.webp 192w' % (p, p, p))
    if role == 'orb':
        return ('%sassets/sr-badge-official-192w.webp' % p,
                '%sassets/sr-badge-official-96w.webp 96w, %sassets/sr-badge-official-192w.webp 192w'
                % (p, p))
    if role == 'full':
        return ('%sassets/sr-badge-official.png' % p,
                '%sassets/sr-badge-official-384w.webp 384w, %sassets/sr-badge-official-1024w.webp 1024w'
                % (p, p))
    if role == 'banner':
        return ('%sassets/sr-badge-banner.jpg' % p, None)
    return (None, None)


def role_of(tag):
    m = re.search(r'class="([^"]*)"', tag)
    classes = set(m.group(1).split()) if m else set()
    if classes & {'brand-emblem-img', 'brand-emblem-img-sm', 'portal-brand-emblem'}:
        return 'header'
    if 'c3-orb-img' in classes:
        return 'orb'
    if 'sr-logo-full-render' in classes:
        return 'full'
    if 'cinematic-emblem-img' in classes:
        return 'banner'
    if 'showcase-img' in classes:
        # only the emblem slide; founder photos share the class and must not move
        return 'banner' if 'logo-official' in tag else None
    # any remaining <img> that still points at the old lockup is a logo slot
    if re.search(r'src="[^"]*logo-official', tag):
        return 'header'
    return None


def rewrite_tag(tag, role, p):
    src, srcset = badge_set(p, role)
    if not src:
        return tag
    if SRC.search(tag):
        tag = SRC.sub('src="%s"' % src, tag, count=1)
    if srcset:
        if SRCSET.search(tag):
            tag = SRCSET.sub('srcset="%s"' % srcset, tag, count=1)
    elif SRCSET.search(tag):
        tag = SRCSET.sub('', tag).replace('  ', ' ')
    return tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not (a.apply or a.check):
        ap.error('pass --apply or --check')

    changed, checked, touched = [], 0, 0
    for rel in tracked_html():
        if rel.startswith('docs/'):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path):
            continue
        checked += 1
        t = io.open(path, encoding='utf-8', newline='').read()
        p = prefix_for(rel)

        def repl(m):
            nonlocal touched
            tag = m.group(0)
            role = role_of(tag)
            if not role:
                return tag
            new = rewrite_tag(tag, role, p)
            if new != tag:
                touched += 1
            return new

        out = IMG.sub(repl, t)

        # <source> inside the emblem picture → banner webp set
        def repl_source(m):
            tag = m.group(0)
            if 'logo-official' not in tag:
                return tag
            nonlocal touched
            touched += 1
            set_ = ('%sassets/sr-badge-banner-512w.webp 512w, '
                    '%sassets/sr-badge-banner-768w.webp 768w, '
                    '%sassets/sr-badge-banner-1024w.webp 1024w' % (p, p, p))
            if SRCSET.search(tag):
                return SRCSET.sub('srcset="%s"' % set_, tag, count=1)
            return tag

        out = SOURCE.sub(repl_source, out)

        # lightbox payload on the emblem slide
        out = out.replace('data-sr-args=\'["./assets/logo-official.jpg"',
                          'data-sr-args=\'["%sassets/sr-badge-official.png"' % p)
        out = out.replace('data-sr-args=\'["../assets/logo-official.jpg"',
                          'data-sr-args=\'["%sassets/sr-badge-official.png"' % p)

        if out != t:
            changed.append(rel)
            if a.apply:
                io.open(path, 'w', encoding='utf-8', newline='').write(out)

    print('badge swap: %d pages, %d tags, %d file(s) %s'
          % (checked, touched, len(changed), 'APPLIED' if a.apply else 'DRIFT'))
    for rel in changed[:8]:
        print('  %s %s' % ('~' if a.apply else 'X', rel))
    return 0 if a.apply or not changed else 1


if __name__ == '__main__':
    sys.exit(main())
