import re, gzip, urllib.request, os

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Chrome/120'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read()
            if 'gzip' in r.headers.get('Content-Encoding', ''):
                raw = gzip.decompress(raw)
            return raw.decode('utf-8', 'replace'), r.status
    except Exception as e:
        return '', str(e)

def probe(url, label):
    h, st = get(url)
    if not h:
        print('%-22s FAILED %s' % (label, st)); return
    out = {}
    out['bytes'] = len(h)
    m = re.search(r'<html[^>]*>', h, re.I)
    out['html'] = (m.group(0)[:90] if m else '')
    out['hreflang_tags'] = len(re.findall(r'<link[^>]+hreflang=["\']([a-zA-Z\-]+)["\']', h))
    langs = re.findall(r'<link[^>]+hreflang=["\']([a-zA-Z\-]+)["\'][^>]*href=["\']([^"\']+)', h)
    out['x_default'] = any(l == 'x-default' for l, _ in langs)
    out['og_locale'] = re.findall(r'property=["\']og:locale["\'][^>]*content=["\']([^"\']+)', h)
    out['og_alt'] = len(re.findall(r'og:locale:alternate', h))
    out['og_image'] = re.findall(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)', h)[:1]
    # language switcher markup
    m2 = re.search(r'<(?:div|nav|details)[^>]+(?:lang|language)[^>]*>', h, re.I)
    out['switcher_tag'] = (m2.group(0)[:110] if m2 else 'none')
    out['switcher_links'] = len(re.findall(r'<a[^>]+href=["\'][^"\']*/(?:de|en|nl|fr|es|it|ar)/[^"\']*["\']', h))
    out['aria_current'] = len(re.findall(r'aria-current', h))
    out['notranslate'] = len(re.findall(r'notranslate|translate=["\']no["\']', h, re.I))
    out['details_el'] = len(re.findall(r'<details', h, re.I))
    print('%-22s %6d B  hreflang=%-3d xdef=%-5s og=%-6s alt=%-2d links=%-3d aria-cur=%-2d notranslate=%-2d'
          % (label, out['bytes'], out['hreflang_tags'], out['x_default'],
             ','.join(out['og_locale']) or '-', out['og_alt'], out['switcher_links'],
             out['aria_current'], out['notranslate']))
    print('   html:', out['html'])
    print('   og:image:', out['og_image'][0][:90] if out['og_image'] else '-')
    return h

probe('https://sr-coresync.com/', 'coresync ar')
probe('https://sr-coresync.com/en/', 'coresync en')
probe('https://sr-coresync.com/de/', 'coresync de')

print('\n--- sitemap ---')
s, st = get('https://sr-coresync.com/sitemap.xml')
print('status', st, 'bytes', len(s))
print('urls:', len(re.findall(r'<url>', s)), '| xhtml:link:', len(re.findall(r'xhtml:link', s)))
print(s[:300].replace('\n', ' '))
