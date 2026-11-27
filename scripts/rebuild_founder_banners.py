# -*- coding: utf-8 -*-
"""Rebuild the founder banners from the clean 2560x1440 artwork.

The current banners carry a second emblem pasted over the headline (a wave
that swapped the legacy star logo left the paste in the wrong place). The
clean design exists in history at 6c3e12ab; this script takes those two
masters and regenerates every size the site references, so the duplicated
emblem disappears without touching the typography or the photography.
"""
import os
import subprocess

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets')
TMP = os.path.join(ROOT, 'scratch')


def clean_master(name):
    ref = '6c3e12ab:assets/founder-banner-%s.jpg' % name
    dst = os.path.join(TMP, 'clean-%s.jpg' % name)
    with open(dst, 'wb') as fh:
        subprocess.run(['git', 'show', ref], cwd=ROOT, stdout=fh, check=True)
    im = Image.open(dst).convert('RGB')
    assert im.size == (2560, 1440), (name, im.size)
    return im


def sharp(im):
    return im.filter(ImageFilter.UnsharpMask(radius=1.1, percent=90, threshold=3))


def save_both(im, base):
    im.save(os.path.join(OUT, base + '.jpg'), 'JPEG', quality=92, optimize=True)
    im.save(os.path.join(OUT, base + '.webp'), 'WEBP', quality=92, method=6)


for name in ('raed', 'salim'):
    master = clean_master(name)
    print('master', name, master.size)

    full = sharp(master)
    save_both(full, 'founder-banner-%s' % name)
    full.save(os.path.join(OUT, 'founder-banner-%s-2560.webp' % name), 'WEBP', quality=92, method=6)

    half = sharp(master.resize((1280, 720), Image.LANCZOS))
    save_both(half, 'founder-banner-%s-1280' % name)

    small = sharp(master.resize((640, 360), Image.LANCZOS))
    save_both(small, 'founder-banner-%s-640' % name)

    uhd = sharp(master.resize((3840, 2160), Image.LANCZOS))
    uhd.save(os.path.join(OUT, 'founder-banner-%s-4k.jpg' % name), 'JPEG', quality=90, optimize=True)
    uhd.save(os.path.join(OUT, 'founder-banner-%s-4k.webp' % name), 'WEBP', quality=90, method=6)

    for suffix in ('', '-1280', '-640', '-4k'):
        for ext in ('jpg', 'webp'):
            p = os.path.join(OUT, 'founder-banner-%s%s.%s' % (name, suffix, ext))
            print('  ', os.path.basename(p), round(os.path.getsize(p) / 1024), 'KB')
