import hashlib, os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

def biggest_anon_style(path):
    s = open(path, encoding='utf-8', newline='').read()
    best = None
    for m in re.finditer(r'<style(?![^>]*\bid=)[^>]*>(.*?)</style>', s, re.S | re.I):
        body = m.group(1)
        if best is None or len(body) > len(best[1]):
            best = (m.group(0), body, m.start(), m.end())
    return best

for rel in ('index.html', 'en/index.html', 'de/index.html', 'ckb/index.html'):
    p = os.path.join(ROOT, rel)
    b = biggest_anon_style(p)
    if not b:
        print('%-18s none' % rel); continue
    print('%-18s %7.1f KB  sha1=%s' % (rel, len(b[1].encode()) / 1024, hashlib.sha1(b[1].encode()).hexdigest()[:16]))
