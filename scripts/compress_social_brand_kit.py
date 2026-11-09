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
Compress the social brand kit without losing it
===============================================

`assets/social-8k-branding/` holds 78 files and 95.7 MB, and 24 of the assets
are stored three times - once as PNG, once as JPG and once as WebP:

    PNG   59.4 MB   28 files
    JPG   24.6 MB   24 files
    WebP  11.7 MB   24 files

A 7680x4320 *photograph* stored as PNG is lossless compression of noise: the
format cannot beat JPEG on this content, and it costs 3x the bytes. The PNG
copies are therefore the redundant ones - not the assets.

What this tool does, per asset:

  1. If a PNG has a JPG sibling with identical pixel dimensions, the PNG is
     redundant and is removed. The JPG (universally uploadable to every social
     platform) and the WebP (what the web pages would use) both stay.
  2. If a PNG has no sibling and carries no transparency, it is converted to a
     high-quality JPG (q92) and the PNG is removed.
  3. A PNG that uses transparency is kept untouched - an overlay without its
     alpha channel is a broken asset, not a smaller one.

Nothing is resized, cropped or re-compressed where a sibling already exists, so
the 8K promise of the kit survives.

Usage:
    python scripts/compress_social_brand_kit.py
    python scripts/compress_social_brand_kit.py --apply
"""
import argparse
import collections
import io
import os
import sys

from PIL import Image

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'assets', 'social-8k-branding')

PHOTO_QUALITY = 92


def has_alpha(path):
    with Image.open(path) as image:
        return image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    by_base = collections.defaultdict(dict)
    for dirpath, _, filenames in os.walk(KIT):
        for name in filenames:
            base, ext = os.path.splitext(name)
            by_base[os.path.join(dirpath, base)][ext.lower()] = os.path.join(dirpath, name)

    removed_bytes = 0
    removed_files = 0
    converted = 0
    kept_alpha = []

    for base, group in sorted(by_base.items()):
        png = group.get('.png')
        if not png:
            continue
        rel = os.path.relpath(png, ROOT).replace('\\', '/')
        size = os.path.getsize(png)

        jpg = group.get('.jpg')
        if jpg:
            with Image.open(png) as a, Image.open(jpg) as b:
                if a.size != b.size:
                    print('SKIP  %s - JPG sibling is %dx%d, PNG is %dx%d'
                          % (rel, b.size[0], b.size[1], a.size[0], a.size[1]))
                    continue
            print('DROP  %s  (-%.1f MB, JPG sibling kept)' % (rel, size / 1048576))
            removed_bytes += size
            removed_files += 1
            if args.apply:
                os.remove(png)
            continue

        if has_alpha(png):
            kept_alpha.append(rel)
            continue

        target = os.path.splitext(png)[0] + '.jpg'
        with Image.open(png) as image:
            buf = io.BytesIO()
            image.convert('RGB').save(buf, 'JPEG', quality=PHOTO_QUALITY,
                                      optimize=True, progressive=True)
            data = buf.getvalue()
        # A conversion that does not clearly win is a format change for nothing:
        # keep the PNG and leave the asset alone.
        if len(data) > size * 0.85:
            kept_alpha.append(rel + '  (conversion would not pay off)')
            continue
        print('CONV  %s  %.1f MB -> %.1f MB (q%d JPG)'
              % (rel, size / 1048576, len(data) / 1048576, PHOTO_QUALITY))
        removed_bytes += size - len(data)
        converted += 1
        if args.apply:
            with open(target, 'wb') as fh:
                fh.write(data)
            os.remove(png)

    if kept_alpha:
        print('\nkept PNG:')
        for rel in kept_alpha:
            print('  %s' % rel)

    print('-' * 74)
    print('%s: %d removed, %d converted, %.1f MB reclaimed'
          % ('APPLIED' if args.apply else 'DRY RUN', removed_files, converted,
             removed_bytes / 1048576))
    if not args.apply:
        print('Re-run with --apply to write.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
