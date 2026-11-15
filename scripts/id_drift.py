import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
for rel in ('index.html', 'de/index.html', 'tr/index.html'):
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    ids = re.findall(r'id="([a-zA-Z][\w-]{2,30})"', s)
    lab = [x for x in ids if 'lab' in x.lower() or 'architect' in x.lower()]
    comp = [x for x in ids if 'compl' in x.lower() or 'trust' in x.lower() or 'cert' in x.lower()]
    print('%-16s lab ids=%s · compliance ids=%s' % (rel, lab[:4], comp[:4]))
