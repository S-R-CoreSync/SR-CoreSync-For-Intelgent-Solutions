# -*- coding: utf-8 -*-
"""ku has the button but not the function. Copy the one function, not the whole block."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
de = open(os.path.join(ROOT, 'de', 'index.html'), encoding='utf-8', newline='').read()

i = de.find('function toggleNavMore')
assert i > 0
# brace-match the function body
j = de.find('{', i)
depth = 0
end = None
for m in re.finditer(r'[{}]', de[j:]):
    depth += 1 if m.group(0) == '{' else -1
    if depth == 0:
        end = j + m.end()
        break
assert end, 'unbalanced'
fn = de[i:end]
print('extracted %d chars' % len(fn))

ku_path = os.path.join(ROOT, 'ku', 'index.html')
ku = open(ku_path, encoding='utf-8', newline='').read()
if 'function toggleNavMore' in ku:
    print('already defined')
    raise SystemExit

block = '<script>\n/* nav "more" toggle - the button existed, the function did not */\n%s\n</script>\n' % fn
k = ku.rfind('</body>')
ku = ku[:k] + block + ku[k:]
open(ku_path, 'w', encoding='utf-8', newline='').write(ku)
print('definition added to ku')
