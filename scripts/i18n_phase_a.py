"""Phase A - semantic language attributes on the dock, with no visual effect.

Each dock link says nothing about the language it points to. A screen reader
falls back to the page language and mangles "Nederlands" or "Ελληνικά", and the
active language is marked only by a CSS class. This adds, on every page:

  · hreflang + lang on each link   -> the target language is declared
  · aria-current="page" on the live one
  · translate="no" on the aside    -> browsers stop offering to translate names

Nothing here changes layout, colour, or geometry.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'ga',
         'hr', 'hu', 'it', 'ku', 'lt', 'lv', 'mt', 'nl', 'no', 'pl', 'pt', 'ro',
         'sk', 'sl', 'sv', 'tr']

A_TAG = re.compile(r'<a\s+href="([^"]+)"([^>]*class="apple-dock-item[^"]*"[^>]*)>', re.I)


def code_from_href(href):
    m = re.search(r'(?:^|/)\.{0,2}/([a-z]{2})/index\.html$', href)
    if m:
        return m.group(1)
    if href in ('./index.html', '../index.html'):
        return 'ar'
    return None


def fix_page(path, page_lang, dry=False):
    s = open(path, encoding='utf-8', newline='').read()
    if 'hreflang="' in s.split('<aside class="apple-macos-dock-wrapper"')[-1][:6000] and 'aria-current="page"' in s:
        return 0, 0, 'already'

    a0 = s.find('<aside class="apple-macos-dock-wrapper"')
    if a0 < 0:
        return 0, 0, 'no dock'
    a1 = s.find('</aside>', a0)
    block = s[a0:a1]

    added_lang = 0
    added_current = 0

    # translate="no" on the aside (attribute only - no class, no style)
    head_end = block.find('>')
    head = block[:head_end]
    if 'translate=' not in head:
        head = head.replace('aria-label="Sovereign Language Quick Dock"',
                            'aria-label="Sovereign Language Quick Dock" translate="no"', 1)
        if 'translate=' not in head:
            head = head[:-1] + ' translate="no"'
        block = head + block[head_end:]

    def repl(m):
        nonlocal added_lang, added_current
        href, rest = m.group(1), m.group(2)
        code = code_from_href(href)
        if not code or 'hreflang=' in rest:
            return m.group(0)
        extra = ' hreflang="%s" lang="%s"' % (code, code)
        if re.search(r'class="apple-dock-item[^"]*\bactive\b', rest):
            extra += ' aria-current="page"'
            added_current += 1
        added_lang += 1
        return '<a href="%s"%s%s>' % (href, rest, extra)

    block = A_TAG.sub(repl, block)
    out = s[:a0] + block + s[a1:]
    if not dry and out != s:
        open(path, 'w', encoding='utf-8', newline='').write(out)
    return added_lang, added_current, 'ok' if out != s else 'nochange'


def main():
    dry = '--dry' in sys.argv
    total_l = total_c = 0
    for lang in LANGS:
        p = os.path.join(ROOT, 'index.html') if lang == 'ar' else os.path.join(ROOT, lang, 'index.html')
        if not os.path.exists(p):
            print('%-3s missing' % lang)
            continue
        l, c, note = fix_page(p, lang, dry)
        total_l += l
        total_c += c
        print('%-3s %-9s links=%d current=%d' % (lang, note, l, c))
    print('\ntotal links annotated: %d · active marked: %d' % (total_l, total_c))


if __name__ == '__main__':
    main()
