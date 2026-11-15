#!/usr/bin/env python
"""Verify the staged publish artefact: nothing extra, nothing missing.

`_site/` is assembled from the working tree, not from git, so two independent
failures are possible:

  1. **Extra** - a file git does not track (session database, log, chat
     transcript, API-key store, user upload) is copied into the bundle that
     GitHub Pages serves publicly. A hardcoded forbidden list only catches the
     names someone thought of; asking git catches every name.

  2. **Missing** - a path `REQUIRED_PUBLISHED` needs (RFC 9116 security.txt, the
     IndexNow key, the vCard) never reached the artefact. The site would then
     ship without it and every downstream check would still be green.

`validate_publish_set.py` answers a different question: it recomputes the rule
engine's output list and validates that list. A copy step that silently drops a
file, or a rule that stops matching, passes there and fails here.

Exit codes: 0 ok · 1 untracked files in the artefact · 2 artefact missing ·
3 required file missing from the artefact.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from publish_set import REQUIRED_PUBLISHED  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, '_site')


def head_paths():
    """Every path tracked at HEAD, as repository-relative POSIX strings."""
    result = subprocess.run(
        ['git', '-C', ROOT, 'ls-tree', '-r', '--name-only', '-z', 'HEAD'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0:
        sys.stderr.write('git ls-tree failed: %s\n'
                         % result.stderr.decode('utf-8', 'replace').strip())
        sys.exit(2)
    return {p for p in result.stdout.decode('utf-8', 'replace').split('\0') if p}


def staged_files(root):
    """Every file in the artefact, as POSIX paths relative to the artefact root."""
    for base, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(base, name)
            yield os.path.relpath(full, root).replace('\\', '/')


def describe(full_path):
    try:
        return '%.1f KB' % (os.path.getsize(full_path) / 1024.0)
    except OSError:
        return '?'


def main():
    if not os.path.isdir(STAGE):
        sys.stderr.write('FAILED: %s does not exist - build the publish set first '
                         '(python scripts/prepare_publish_set.py).\n' % STAGE)
        return 2

    tracked = head_paths()
    staged = list(staged_files(STAGE))
    leaked = sorted(rel for rel in staged if rel not in tracked)

    if leaked:
        sys.stderr.write('FAILED: %d file(s) in the publish artefact are not tracked at HEAD.\n'
                         % len(leaked))
        sys.stderr.write('Git does not consider them content, so they must never be published:\n')
        for rel in leaked[:40]:
            sys.stderr.write('  - %s (%s)\n' % (rel, describe(os.path.join(STAGE, rel))))
        if len(leaked) > 40:
            sys.stderr.write('  ... and %d more\n' % (len(leaked) - 40))
        sys.stderr.write('Add a rule to scripts/publish_set.py, or delete the file from the tree.\n')
        return 1

    present = set(staged)
    missing = [req for req in REQUIRED_PUBLISHED if req not in present]
    if missing:
        sys.stderr.write('FAILED: %d required file(s) never reached the artefact.\n' % len(missing))
        for req in missing:
            sys.stderr.write('  - %s\n' % req)
        sys.stderr.write('The rule engine lists them but the copy step dropped them; '
                         'check scripts/publish_set.py and the build log.\n')
        return 3

    print('PASSED: %d artefact file(s) - every one tracked at HEAD, and all %d required '
          'files present.' % (len(staged), len(REQUIRED_PUBLISHED)))
    print('        (HEAD carries %d tracked path(s); the publish set ships a subset by design.)'
          % len(tracked))
    return 0


if __name__ == '__main__':
    sys.exit(main())
