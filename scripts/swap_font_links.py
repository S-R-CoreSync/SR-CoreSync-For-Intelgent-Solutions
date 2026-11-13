"""Point every page at the local copy of the two families, drop the preconnects."""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'ga',
         'hr', 'hu', 'it', 'ku', 'lt', 'lv', 'mt', 'nl', 'no', 'pl', 'pt', 'ro',
         'sk', 'sl', 'sv', 'tr']

LINK = re.compile(
    r'<link\s*\r?\n?\s*href="https://fonts\.googleapis\.com/css2\?[^"]+"\s*\r?\n?\s*rel="stylesheet"\s*>',
    re.I)
PRE = re.compile(r'[ \t]*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\r?\n', re.I)


def process(path, depth, dry):
    s = open(path, encoding='utf-8', newline='').read()
    orig = s
    prefix = './' if depth == 0 else '../'
    local = '<link rel="stylesheet" href="%sassets/fonts/gf/fonts.css?v=%s">' % (prefix, '20261114')

    s, n_pre = PRE.subn('', s)
    s, n_link = LINK.subn(local, s)

    # some pages may carry the link on a single line
    if n_link == 0:
        single = re.compile(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet">', re.I)
        s, n_link = single.subn(local, s)

    if not dry and s != orig:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    return n_pre, n_link, ('ok' if s != orig else 'nochange')


def main():
    dry = '--dry' in sys.argv
    tp = tl = 0
    for lang in LANGS:
        p = os.path.join(ROOT, 'index.html') if lang == 'ar' else os.path.join(ROOT, lang, 'index.html')
        if not os.path.exists(p):
            print('%-3s missing' % lang); continue
        n_pre, n_link, note = process(p, 0 if lang == 'ar' else 1, dry)
        tp += n_pre; tl += n_link
        print('%-3s %-9s preconnect_removed=%d link_replaced=%d' % (lang, note, n_pre, n_link))
    print('\npreconnects removed: %d · links replaced: %d' % (tp, tl))


if __name__ == '__main__':
    main()
