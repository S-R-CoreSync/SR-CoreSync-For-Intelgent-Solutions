import os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def text_of(html):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

# tier matrix block
i = home.find('id="tier-matrix"')
i = home.rfind('<div', 0, i)
depth = 0
for t in re.finditer(r'<div\b|</div>', home[i:], re.I):
    if t.group(0).startswith('</'):
        depth -= 1
        if depth == 0:
            end = i + t.end(); break
    else:
        depth += 1
matrix = home[i:end]
mt = text_of(matrix)

tech = open(os.path.join(ROOT, 'tech-matrix.html'), encoding='utf-8', newline='').read()
tt = text_of(tech)

def grams(t, n=6):
    words = t.split()
    return {' '.join(words[k:k + n]) for k in range(0, max(0, len(words) - n), 3)}

g1, g2 = grams(mt), grams(tt)
inter = g1 & g2
print('tier matrix text: %d chars, %d 6-grams' % (len(mt), len(g1)))
print('tech-matrix page: %d chars, %d 6-grams' % (len(tt), len(g2)))
print('overlap: %d 6-grams = %.0f%% of the matrix text' % (len(inter), 100 * len(inter) / max(1, len(g1))))

print('\nmatrix sample:', mt[:220])
print('\ntech-matrix sample:', tt[:220])
