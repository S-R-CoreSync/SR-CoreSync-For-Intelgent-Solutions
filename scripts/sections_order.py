import json, os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
ORDER = ['services', 'pricing', 'software-hub', 'about', 'founders-showcase']
d = os.path.join(ROOT, 'i18n', 'sections')
os.makedirs(d, exist_ok=True)
json.dump({'order': ORDER}, open(os.path.join(d, 'order.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
pos = {}
for sid in ORDER:
    m = re.search(r'<section\b[^>]*\bid="%s"' % sid, s)
    pos[sid] = m.start() if m else -1
seq = sorted(ORDER, key=lambda k: pos[k])
print('declared:', ORDER)
print('in page :', seq)
print('MATCH' if seq == ORDER else 'MISMATCH')
