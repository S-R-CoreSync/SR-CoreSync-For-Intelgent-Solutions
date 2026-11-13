# -*- coding: utf-8 -*-
"""Apply the calibrated footer to a page (master first)."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF


def footer_span(src):
    best = None
    for m in re.finditer(r'<footer\b[^>]*>', src):
        i = m.start()
        depth, end = 0, None
        for t in re.finditer(r'<footer\b|</footer>', src[i:]):
            if t.group(0).startswith('</'):
                depth -= 1
                if depth == 0:
                    end = i + t.end()
                    break
            else:
                depth += 1
        if end and (best is None or (end - i) > (best[1] - best[0])):
            best = (i, end)
    return best


def apply(path, lang):
    s = open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    base = '' if os.path.basename(os.path.dirname(path)) == os.path.basename(ROOT) else '../'
    if 'id="srf-footer"' in s:
        m2 = re.search(r'<footer class="srf".*?</footer>', s, re.S)
        if m2:
            s = s[:m2.start()] + SF.render(model, lang, base) + s[m2.end():]
            open(path, 'w', encoding='utf-8', newline='').write(s)
            print(path, 'refreshed')
        return
    span = footer_span(s)
    if not span:
        print(path, 'no footer')
        return
    model = json.load(open(SF.MODEL, encoding='utf-8'))
    block = SF.render(model, lang, base)

    s = s[:span[0]] + block + s[span[1]:]

    if 'id="srf-css"' not in s:
        k = s.lower().rindex('</head>')
        s = s[:k] + '<style id="srf-css">' + nl + SF.CSS + nl + '</style>' + nl + s[k:]

    open(path, 'w', encoding='utf-8', newline='').write(s)
    print(path, 'calibrated', len(block), 'bytes')


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    lang = sys.argv[2] if len(sys.argv) > 2 else 'ar'
    apply(os.path.join(ROOT, target), lang)
