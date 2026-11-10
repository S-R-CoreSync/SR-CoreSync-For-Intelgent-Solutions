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
S&R CoreSync For Intelligent Solutions - Publish Set Builder
===============================================================================
Builds the `_site/` directory that is uploaded to GitHub Pages.

The exact same rules are enforced by `scripts/validate_publish_set.py` and by
the "Verify no server-side material is published" step of the deploy
workflow, so the verified artifact is always the published artifact.

Usage:  python scripts/prepare_publish_set.py
Exit code 0 = the staging directory is ready to upload.
"""
import io
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from publish_set import (  # noqa: E402
    ROOT, FORBIDDEN_PUBLISHED, REQUIRED_PUBLISHED, publish_set
)

STAGE = os.path.join(ROOT, '_site')
# The publish set is staged beside the live tree and swapped in only once every
# file is copied and the guard passes. `_site` used to be deleted in place and
# repopulated, so any interruption - Ctrl-C, a locked file, a full disk - left a
# half-built tree, and the five gates that read `_site` then reported a site full
# of dead pages: 30 failed browser pages, 48 "missing" local references, a stale
# CSP manifest. Building beside the live tree keeps the last good artefact
# intact. Both siblings start with '_', so publish_set.py never ships them.
STAGE_NEXT = os.path.join(ROOT, '_site.next')
STAGE_PREV = os.path.join(ROOT, '_site.prev')


def main():
    print('=' * 70)
    print('S&R CoreSync - Building the GitHub Pages publish set')
    print('=' * 70)

    # Never build in place: a copy that dies halfway must not be able to hide the
    # previous artefact from the gates that audit it.
    for stale in (STAGE_NEXT, STAGE_PREV):
        if os.path.isdir(stale):
            shutil.rmtree(stale)
    os.makedirs(STAGE_NEXT)

    files = publish_set()
    copied = 0
    total_bytes = 0

    try:
        for rel in files:
            src = os.path.join(ROOT, rel.replace('/', os.sep))
            dst = os.path.join(STAGE_NEXT, rel.replace('/', os.sep))
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            shutil.copy2(src, dst)
            copied += 1
            total_bytes += os.path.getsize(src)
    except OSError as exc:
        shutil.rmtree(STAGE_NEXT, ignore_errors=True)
        print('-' * 70)
        print('FAILED: staging the publish set did not finish: %s' % exc)
        print('The previous _site/ build is untouched.')
        return 1

    print('Copied %d files (%.2f MB) into _site.next/' % (copied, total_bytes / 1024.0 / 1024.0))

    # Guard: nothing forbidden may exist inside the staging directory.
    failures = []
    for bad in FORBIDDEN_PUBLISHED:
        target = os.path.join(STAGE_NEXT, bad)
        if os.path.exists(target):
            failures.append('Forbidden path present in the publish set: %s' % bad)

    for req in REQUIRED_PUBLISHED:
        if not os.path.exists(os.path.join(STAGE_NEXT, req)):
            failures.append('Required publish file missing: %s' % req)

    if failures:
        shutil.rmtree(STAGE_NEXT, ignore_errors=True)
        print('-' * 70)
        print('FAILED:')
        for f in failures:
            print('  X ' + f)
        print('The previous _site/ build is untouched.')
        return 1

    # Promote the verified build with two directory renames on one volume, so the
    # window where `_site` is absent is a filesystem call wide instead of the
    # minutes a file-by-file copy takes.
    if os.path.isdir(STAGE):
        os.rename(STAGE, STAGE_PREV)
    try:
        os.rename(STAGE_NEXT, STAGE)
    except OSError:
        if os.path.isdir(STAGE_PREV):
            os.rename(STAGE_PREV, STAGE)
        raise
    shutil.rmtree(STAGE_PREV, ignore_errors=True)

    print('Guard passed: no server-side material in the publish set.')
    print('=' * 70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
