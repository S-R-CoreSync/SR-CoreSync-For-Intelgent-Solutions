# -*- coding: utf-8 -*-
"""Restore the Hero AI Idea Prompt Bar to the Arabic root index.html.

Safety design (order matters):
1. Idempotent: exits cleanly if the bar is already present.
2. Verifies ALL required infrastructure (CSS classes reachable via the page's
   own <link> set, JS handlers reachable via the page's own <script> set,
   dispatcher sr-events.js, target modal) BEFORE writing anything.
3. EOL-safe: preserves the file's original line endings exactly.
4. Single atomic write; re-reads and re-verifies afterwards.
Run from the repository root:  python scripts/restore_root_ai_bar.py [repo_root]
"""
import hashlib
import io
import os
import re
import sys

BAR_COMMENT_AR = 'شريط كتابة الفكرة وهندسة المشروع الفوري بالذكاء الاصطناعي (Hero AI Idea Prompt Bar)'

PLACEHOLDER = 'اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)'
SUBMIT_TEXT = 'حلل فكرتي بالـ AI ⚡'
MIC_TITLE = 'تحدث بفكرة مشروعك بالصوت التفاعلي'
ARROW = '←'  # RTL page: arrow points left

REQUIRED_CSS_CLASSES = [
    'hero-ai-idea-bar', 'hero-ai-idea-form', 'hero-ai-idea-icon-wrap',
    'hero-ai-idea-input-wrap', 'hero-ai-idea-input', 'hero-ai-idea-btns',
    'hero-ai-idea-mic-btn', 'hero-ai-idea-submit-btn', 'hero-ai-submit-arrow',
]
REQUIRED_JS_HANDLERS = [
    'submitHeroAiIdea', 'openVoicePlannerFromHero',
    'openAiVoicePlannerModal', 'generateAiProjectBlueprint',
]

ANCHOR = '<div class="hero-trust-metrics-strip'


def build_bar_html(indent, eol):
    L = []
    L.append(indent + '<!-- ' + BAR_COMMENT_AR + ' -->')
    L.append(indent + '<div class="hero-ai-idea-bar" id="heroAiIdeaBar">')
    L.append(indent + '    <form class="hero-ai-idea-form" data-sr-call="submitHeroAiIdea" data-sr-on="submit" data-sr-prevent="1">')
    L.append(indent + '        <div class="hero-ai-idea-icon-wrap" aria-hidden="true">')
    L.append(indent + '            <span class="hero-ai-idea-sparkle">✨</span>')
    L.append(indent + '        </div>')
    L.append(indent + '        <div class="hero-ai-idea-input-wrap">')
    L.append(indent + '            <input type="text" id="heroAiIdeaInput" class="hero-ai-idea-input" placeholder="' + PLACEHOLDER + '" autocomplete="off" aria-label="Project Idea AI Input">')
    L.append(indent + '        </div>')
    L.append(indent + '        <div class="hero-ai-idea-btns">')
    L.append(indent + '            <button type="button" class="hero-ai-idea-mic-btn" data-sr-call="openVoicePlannerFromHero" title="' + MIC_TITLE + '" aria-label="' + MIC_TITLE + '">')
    L.append(indent + '                <span class="hero-ai-mic-icon">🎙️</span>')
    L.append(indent + '            </button>')
    L.append(indent + '            <button type="submit" class="hero-ai-idea-submit-btn" title="' + SUBMIT_TEXT + '" aria-label="' + SUBMIT_TEXT + '">')
    L.append(indent + '                <span class="hero-ai-submit-text">' + SUBMIT_TEXT + '</span>')
    L.append(indent + '                <span class="hero-ai-submit-arrow">' + ARROW + '</span>')
    L.append(indent + '            </button>')
    L.append(indent + '        </div>')
    L.append(indent + '    </form>')
    L.append(indent + '</div>')
    return eol.join(L) + eol


def read(path):
    # newline='' keeps the file's original line endings untouched
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def fail(msg):
    print('FAIL: ' + msg)
    sys.exit(1)


def local_assets(page_html, root):
    """Collect local css/js files referenced by the page (resolves ./ and ../)."""
    css_files, js_files = [], []
    for m in re.finditer(r'<link[^>]+?href="([^"]+)"', page_html):
        href = m.group(1).split('?')[0]
        if href.lower().endswith('.css') and not href.startswith(('http://', 'https://', '//', 'data:')):
            p = os.path.normpath(os.path.join(root, href))
            if os.path.isfile(p):
                css_files.append(p)
    for m in re.finditer(r'<script[^>]+?src="([^"]+)"', page_html):
        src = m.group(1).split('?')[0]
        if src.lower().endswith('.js') and not src.startswith(('http://', 'https://', '//', 'data:')):
            p = os.path.normpath(os.path.join(root, src))
            if os.path.isfile(p):
                js_files.append(p)
    return css_files, js_files


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    page = os.path.join(root, 'index.html')
    if not os.path.isfile(page):
        fail('index.html not found under ' + root)
    content = read(page)
    original_len = len(content.encode('utf-8'))

    # ---- 1. Idempotency ----------------------------------------------------------
    if 'hero-ai-idea-bar' in content:
        print('PASS: hero-ai-idea-bar already present in index.html (nothing to do).')
        return

    # ---- 2. Infrastructure verification BEFORE any write ----------------------
    css_files, js_files = local_assets(content, root)
    if not css_files:
        fail('no local CSS files resolved from index.html')
    css_blob = '\n'.join(read(p) for p in css_files)
    missing_css = [cl for cl in REQUIRED_CSS_CLASSES if ('.' + cl) not in css_blob]
    if missing_css:
        fail('missing CSS classes in loaded stylesheets: ' + ', '.join(missing_css))

    if not any(os.path.basename(p) == 'sr-events.js' for p in js_files):
        fail('dispatcher sr-events.js is not referenced by index.html')
    js_blob = '\n'.join(read(p) for p in js_files)
    missing_js = [h for h in REQUIRED_JS_HANDLERS if ('function ' + h) not in js_blob
                  and (h + '=') not in js_blob and ('window.' + h) not in js_blob]
    if missing_js:
        fail('missing JS handlers in loaded scripts: ' + ', '.join(missing_js))

    if 'aiVoicePlannerModal' not in content:
        fail('target modal aiVoicePlannerModal not found in index.html')
    if content.count(ANCHOR) != 1:
        fail('expected exactly one hero-trust-metrics-strip div anchor, found '
             + str(content.count(ANCHOR)))

    # ---- 3. Insertion -------------------------------------------------------------
    eol = '\r\n' if '\r\n' in content else '\n'
    pos = content.find(ANCHOR)
    line_start = content.rfind(eol, 0, pos) + 1
    line_prefix = content[line_start:pos]
    indent = line_prefix[:len(line_prefix) - len(line_prefix.lstrip())]
    if indent.strip():
        fail('unexpected non-whitespace before anchor div: ' + repr(line_prefix[:80]))
    bar = build_bar_html(indent, eol)
    new_content = content[:line_start] + bar + content[line_start:]

    # ---- 4. Atomic write + re-verify -------------------------------------------
    with io.open(page, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    check = read(page)
    n_bar = check.count('hero-ai-idea-bar')
    n_anchor = check.count(ANCHOR)
    if n_bar < 1 or n_anchor != 1 or 'id="heroAiIdeaInput"' not in check:
        fail('post-write verification failed (bar=%d anchor=%d)' % (n_bar, n_anchor))
    if len(check) != len(new_content):
        fail('post-write length mismatch')

    new_len = len(check.encode('utf-8'))
    sha = hashlib.sha256(check.encode('utf-8')).hexdigest().upper()
    print('PASS: Hero AI Idea Prompt Bar inserted into index.html (Arabic root).')
    print('  inserted at byte offset : %d' % line_start)
    print('  size: %d -> %d bytes (+%d)' % (original_len, new_len, new_len - original_len))
    print('  css verified : %d local stylesheets, all %d classes present' % (len(css_files), len(REQUIRED_CSS_CLASSES)))
    print('  js verified  : %d local scripts, all %d handlers present' % (len(js_files), len(REQUIRED_JS_HANDLERS)))
    print('  SHA-256(index.html) = ' + sha)


if __name__ == '__main__':
    main()
