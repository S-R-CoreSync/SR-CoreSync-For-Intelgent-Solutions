import re
s = open(r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\de\index.html', encoding='utf-8', newline='').read()
m = re.search(r'data-i18n="pricing\.plan1\.desc">([^<]{0,90})', s)
print('local de text:', (m.group(1).strip() if m else 'not found')[:80])
print('english still in file:', 'Ideal for launching' in s)
print('german present:', 'Ideal für den Start' in s)
