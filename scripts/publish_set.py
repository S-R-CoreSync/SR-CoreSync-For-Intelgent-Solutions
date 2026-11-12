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
S&R CoreSync For Intelligent Solutions - Publish Set Rules
===============================================================================
Single source of truth for "what gets published to GitHub Pages".

Both the local builder (`scripts/prepare_publish_set.py`) and the CI guard
(`scripts/validate_publish_set.py`) import this module, so the artifact that
CI verifies is byte-for-byte the artifact that CI publishes.

The site is a static GitHub Pages deployment. Everything in EXCLUDED_DIRS or
EXCLUDED_ROOT_FILES is server-side material that must never be reachable from
the public domain.

Browser "Save page as -> Webpage, Complete" snapshots are likewise never
published: neither the saved page (nor any renamed copy of it) nor its
*_files/ asset folder belongs to site content.
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Directories that are never published (at any depth).
# ---------------------------------------------------------------------------
EXCLUDED_DIRS = {
    '.git', '_site', '.github', '.githooks', '.secrets', '.agents', '.vscode',
    '.zwork', 'api', 'config', 'workers', 'scripts', 'dist', 'deploy',
    'scratch', 'node_modules', '__pycache__', 'docs',
    # stray Chrome print scratch dirs from an old local run: 329 junk files that
    # no page references and that only bloat the Pages artefact.
    'temp_chrome_print_dir', 'temp_chrome_print_dir2'
}

# Any other dot-directory is tooling state (editor caches, agent artefacts), not
# site content. Excluding the whole class stops the next tool from leaking a
# screenshot into the published artefact the way .zwork nearly did.
ALLOWED_DOT_DIRS = {'.nojekyll', '.well-known'}

# Underscore-prefixed directories are local archives and staging folders
# (_site, _trash_*, _css_archive_*). They are never site content: publishing
# _trash_160 exposed 474 duplicate pages (406 MB) to search engines. The only
# underscore-named entries that do ship are root files such as _headers, so
# the rule is scoped to directories on purpose.
EXCLUDED_DIR_PREFIXES = ('_',)

# ---------------------------------------------------------------------------
# Root level files that are never published.
# ---------------------------------------------------------------------------
EXCLUDED_ROOT_FILES = {
    '.env', '.env.example', '.env.local', '.env.vault', '.gitignore',
    '.dockerignore', '.htaccess', 'LICENSE', 'serve.py'
}

# Root level file suffixes that are never published.
# Root PDFs are internal working documents (the Arabic deployment guide and a
# draft proposal). None is linked from a page; the non-ASCII file name also
# trips the GitHub Pages file sync.
EXCLUDED_ROOT_SUFFIXES = ('.md', '.bat', '.url', '.ps1', '.pdf')

# ---------------------------------------------------------------------------
# Root level development artifacts that must never be published.
# They are internal component / e-mail / modal mock-ups and debug harnesses:
# no published page links to them, they carry no `noindex`, and publishing
# them exposed 13 stale duplicates of the real portals to search engines.
# ---------------------------------------------------------------------------
EXCLUDED_DEV_PAGES = {
    'preview-hero-v2.html',
    'debug_header.html',
    'preview_emblem_tuning.html',
    'preview_new_official_embel.html',
    'preview_roi_modal.html',
    'preview-booking-modal.html',
    'preview-checkout.html',
    'preview-client-portal.html',
    'preview-comparison.html',
    'preview-header.html',
    'preview-invoice-quote.html',
    'preview-license-manager.html',
    'preview-software-modal.html',
    'preview-welcome-email.html',
    'preview-welcome-email.html',
}

# ---------------------------------------------------------------------------
# Global file suffixes that are never published.
# ---------------------------------------------------------------------------
EXCLUDED_SUFFIXES = ('.pyc',)

# ---------------------------------------------------------------------------
# Browser "Save page as -> Webpage, Complete" artefacts. Chrome/Edge save a
# page as X.html next to an X_files/ asset folder, and every renamed copy of
# that HTML still references the same *_files/ folder. These are third-party
# snapshots (e.g. saved Z.ai chats) with their trackers, never site content:
# neither the page nor its asset folder is ever published.
# The project's own pages never reference a local *_files/ folder, so the
# content marker below cannot misclassify them.
# ---------------------------------------------------------------------------
SAVED_PAGE_DIR_SUFFIX = '_files'
SAVED_PAGE_REF_RE = re.compile(
    r'(?:src|href)\s*=\s*["\']'
    r'(?!https?:|//|data:|mailto:|tel:|javascript:|blob:|#)'
    r'[^"\']*' + re.escape(SAVED_PAGE_DIR_SUFFIX) + r'/',
    re.IGNORECASE,
)


def _is_saved_page(path):
    """True when an HTML file is a browser "Webpage, Complete" snapshot or a
    renamed copy of one: it references a local *_files/ asset folder, which
    Chrome always rewrites saved-page resources into. Reading is bounded to
    the first megabyte (the marker sits in <head>); real pages never match."""
    try:
        with io.open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            return SAVED_PAGE_REF_RE.search(fh.read(1024 * 1024)) is not None
    except OSError:
        return False

# ---------------------------------------------------------------------------
# Paths that must never appear in the published artifact.
# ---------------------------------------------------------------------------
FORBIDDEN_PUBLISHED = [
    'api', 'config', 'workers', 'scripts', 'dist', 'deploy',
    '.htaccess', '.env', '.env.example', '.env.vault', '.github', '.githooks', '.secrets'
]

# ---------------------------------------------------------------------------
# Files that must always be present in the published artifact.
# ---------------------------------------------------------------------------
REQUIRED_PUBLISHED = [
    '_headers',
    '.nojekyll',
    # Mail clients fetch this to configure themselves. If it stops being
    # published, the only remaining discovery path is the CNAME that fails its
    # certificate check, so failing the build is the correct response.
    '.well-known/autoconfig/mail/config-v1.1.xml',
    # RFC 9116 security policy. If it silently disappears, security scanners
    # and researchers lose the documented contact path, so fail the build.
    '.well-known/security.txt',
    # IndexNow ownership key (Bing/Yandex/Seznam/Naver). The filename IS the
    # key; if content or name drift, search-engine submission breaks, so fail
    # the build rather than publish a silent 404.
    '28e2de90a2704782b40cbd444d5e764d.txt',
    # RFC 6350 contact card, discovered via <link rel="alternate"> on the ar
    # and en landing pages; losing it breaks those discovery links.
    'SR-CoreSync.vcf',
]


def is_excluded(rel_path):
    """Return True when the repository-relative path must not be published."""
    rel = rel_path.replace('\\', '/')
    parts = rel.split('/')
    name = parts[-1]

    if name in EXCLUDED_DIRS:
        return True
    # Any underscore-prefixed directory is a local archive / staging folder.
    if any(part.startswith(EXCLUDED_DIR_PREFIXES) for part in parts[:-1]):
        return True
    # Any dot-directory (including at the repository root) is tooling state
    # unless explicitly allow-listed. Stops .venv / .agents / etc. leaking.
    if name.startswith('.') and name not in ALLOWED_DOT_DIRS:
        return True
    if name.endswith(EXCLUDED_SUFFIXES):
        return True
    if name.endswith(SAVED_PAGE_DIR_SUFFIX):
        return True  # browser saved-page asset folder (or a stray file named so)
    if len(parts) == 1:
        if name in EXCLUDED_ROOT_FILES:
            return True
        if name in EXCLUDED_DEV_PAGES:
            return True
        if name.lower().endswith(EXCLUDED_ROOT_SUFFIXES):
            return True
    return False


# ---------------------------------------------------------------------------
# Assets no published page can reach.
#
# 55.6 MB of the artefact was brand exports whose file name appears in no
# HTML/CSS/JS/JSON of the repository (mostly JPG twins of the WebP files the
# pages actually load). They stay in git - only the deploy artefact skips them,
# which keeps the Pages sync inside its 10-minute budget. The list is data, not
# code, so it can be reviewed and regenerated without touching this module.
# ---------------------------------------------------------------------------
DEAD_ASSET_LIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'publish_dead_assets.txt')


def _load_dead_assets():
    try:
        with open(DEAD_ASSET_LIST, encoding='utf-8') as handle:
            return {
                line.strip() for line in handle
                if line.strip() and not line.lstrip().startswith('#')
            }
    except OSError:
        return set()


DEAD_ASSETS = _load_dead_assets()


# ---------------------------------------------------------------------------
# Assets served from the repository instead of the artefact (see
# scripts/publish_remote_assets.txt). Downloads and lightbox sources only; the
# pages point at raw.githubusercontent.com for exactly these paths.
# ---------------------------------------------------------------------------
REMOTE_ASSET_LIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'publish_remote_assets.txt')


def _load_list(path):
    try:
        with open(path, encoding='utf-8') as handle:
            return {line.strip() for line in handle
                    if line.strip() and not line.lstrip().startswith('#')}
    except OSError:
        return set()


REMOTE_ASSETS = _load_list(REMOTE_ASSET_LIST)


def iter_publish_files(root=None):
    """Yield every repository-relative path that belongs to the publish set."""
    base = root or ROOT
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in EXCLUDED_DIRS
            and not d.startswith(EXCLUDED_DIR_PREFIXES)
            and not (d.startswith('.') and d not in ALLOWED_DOT_DIRS)
            and not d.endswith(SAVED_PAGE_DIR_SUFFIX)
        )
        rel_dir = os.path.relpath(dirpath, base).replace('\\', '/')
        if rel_dir == '.':
            rel_dir = ''
        for name in sorted(filenames):
            rel = (rel_dir + '/' + name) if rel_dir else name
            if is_excluded(rel):
                continue
            if rel in DEAD_ASSETS or rel in REMOTE_ASSETS:
                continue
            if name.lower().endswith('.html') and _is_saved_page(
                    os.path.join(dirpath, name)):
                continue
            yield rel


def publish_set(root=None):
    return list(iter_publish_files(root))
