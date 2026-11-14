import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.cleanse_headers import get_trans

for lang in ['de', 'fr']:
    p = os.path.join(lang, 'index.html')
    s = open(p, encoding='utf-8').read()
    t = get_trans(lang)
    s = re.sub(r'title="Support-Tools والتقييم المؤسسي"', f'title="{t["support_tools_title"]}"', s)
    s = re.sub(r'aria-label="Support-Tools والمحاكاة"', f'aria-label="{t["support_tools_aria"]}"', s)
    s = re.sub(r'<!-- Support-Tools المؤسسي والتقييم \(Header Support Tools Dropdown\) -->', '<!-- Enterprise Support Tools Dropdown -->', s)
    open(p, 'w', encoding='utf-8').write(s)
    print(f'Fixed {lang} header hyphens')
