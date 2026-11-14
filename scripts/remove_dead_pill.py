"""Remove the dead pill rules that the checkout restored, keeping the ring."""
import os, re, subprocess

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'css', 'sr-tokens.css')
s = open(P, encoding='utf-8', newline='').read()

def block_end(text, start):
    """index just after the closing brace of the rule that starts at start"""
    i = text.find('{', start)
    if i < 0:
        return start
    depth = 0
    for m in re.finditer(r'[{}]', text[i:]):
        depth += 1 if m.group(0) == '{' else -1
        if depth == 0:
            return i + m.end()
    return start

removed = 0
freed = 0
while True:
    m = re.search(r'\.sr-lang-hint(?![-\w])', s)
    if not m:
        break
    # step back to the selector start
    sel_start = s.rfind('\n', 0, m.start()) + 1
    end = block_end(s, m.start())
    chunk = s[sel_start:end]
    if 'pulse' in chunk:
        # never touch the ring: skip past it
        nxt = s.find('.sr-lang-hint', end)
        if nxt < 0:
            break
        s = s[:sel_start] + s[sel_start:]  # no-op, move cursor
        # remove only the pill blocks by name instead
        break
    s = s[:sel_start] + s[end:]
    freed += len(chunk)
    removed += 1

# the loop above stops at the first non-pill block; finish the job by name
for cls in ('.sr-lang-hint__link', '.sr-lang-hint__close', '.sr-lang-hint__flag'):
    while True:
        m = re.search(re.escape(cls) + r'[^{]*\{', s)
        if not m:
            break
        sel_start = s.rfind('\n', 0, m.start()) + 1
        end = block_end(s, m.start())
        freed += len(s[sel_start:end])
        s = s[:sel_start] + s[end:]
        removed += 1

# and the bare container rule if it survived
m = re.search(r'\n\.sr-lang-hint\{', s)
if m:
    end = block_end(s, m.start() + 1)
    freed += len(s[m.start():end])
    s = s[:m.start()] + s[end:]
    removed += 1

open(P, 'w', encoding='utf-8', newline='').write(s)
print('rules removed: %d · freed %.1f KB' % (removed, freed / 1024))
print('ring still present:', 'sr-lang-hint-pulse' in s)
print('braces: %d/%d' % (s.count('{'), s.count('}')))
