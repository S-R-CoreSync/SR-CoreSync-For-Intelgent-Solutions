with open('tr/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re
en_words = ['Solutions', 'Creative', 'Digital', 'Frequently Asked Questions', 'Select Currency', 'Resources', 'Support Tools', 'Follow', 'Official', 'Active']
matches = []
for i, line in enumerate(lines):
    # ignore scripts, styles, svg
    if '<script' in line or '<style' in line or '<path' in line or 'class=' in line and len(line) > 500:
        continue
    clean = re.sub(r'<[^>]+>', ' ', line).strip()
    if any(w in clean for w in en_words) and len(clean) > 0:
        matches.append((i+1, clean))

print('Found English phrases in TR text:', len(matches))
for line_no, c in matches[:25]:
    print(f'{line_no}: {c[:100]}')
