import re, os, json
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['ar','bg','cs','da','de','el','en','es','et','fi','fr','ga','hr','hu','it','ku',
         'lt','lv','mt','nl','no','pl','pt','ro','sk','sl','sv','tr']

def hreflangs(html):
    out = []
    for m in re.finditer(r'<link[^>]+hreflang="([^"]+)"[^>]*>', html, re.I):
        tag = m.group(0)
        h = re.search(r'href="([^"]+)"', tag)
        out.append((m.group(1), h.group(1) if h else None))
    return out

print('%-4s %-6s %-6s %s' % ('lang', 'count', 'xdef', 'sample anomalies'))
for lang in ['ar', 'en', 'de']:
    p = os.path.join(ROOT, 'index.html') if lang == 'ar' else os.path.join(ROOT, lang, 'index.html')
    html = open(p, encoding='utf-8', newline='').read()
    hs = hreflangs(html)
    codes = [c for c, _ in hs]
    dup = [c for c in set(codes) if codes.count(c) > 1]
    canon = re.search(r'<link[^>]+rel="canonical"[^>]*href="([^"]+)"', html)
    print('%-4s %-6d %-6s dup=%s canon=%s' % (lang, len(hs), 'x-default' in codes, dup or '-', canon.group(1) if canon else '-'))
    for c, u in hs[:3]:
        print('      ', c, '->', u)
    if len(hs) > 3:
        print('       ...', hs[-1][0], '->', hs[-1][1])
