#!/usr/bin/env python
"""Fail when the publish artefact contains anything git does not track at HEAD.

The publish set is assembled from the working tree, not from git, so any file the
application wrote into the tree - a session database, a log, a chat transcript,
the API-key hash store, a user upload - is copied into the artefact that GitHub
Pages serves publicly. `.gitignore` already declares those files non-content, and
the hardcoded forbidden list in `publish_set.py` only names a handful of them, so
neither stops a new runtime file from shipping.

This check inverts the question: instead of asking "is this path forbidden?", it
asks "is this path tracked at HEAD at all?". A file the repository does not
contain cannot be site content, whatever it is called.

Exit codes: 0 = the artefact is a subset of HEAD, 1 = untracked files found,
2 = the artefact is missing (the build step did not run).
"""
import os
import subprocess
import sys

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
    leaked = []
    total = 0
    for rel in staged_files(STAGE):
        total += 1
        if rel not in tracked:
            leaked.append(rel)

    if leaked:
        sys.stderr.write('FAILED: %d file(s) in the publish artefact are not tracked at HEAD.\n'
                         % len(leaked))
        sys.stderr.write('Git does not consider them content, so they must never be published:\n')
        for rel in sorted(leaked)[:40]:
            sys.stderr.write('  - %s (%s)\n' % (rel, describe(os.path.join(STAGE, rel))))
        if len(leaked) > 40:
            sys.stderr.write('  ... and %d more\n' % (len(leaked) - 40))
        sys.stderr.write('Add a rule to scripts/publish_set.py, or delete the file from the tree.\n')
        return 1

    print('PASSED: %d artefact file(s), every one tracked at HEAD.' % total)
    print('        (HEAD carries %d tracked path(s); the publish set ships a subset by design.)'
          % len(tracked))
    return 0


if __name__ == '__main__':
    sys.exit(main())
