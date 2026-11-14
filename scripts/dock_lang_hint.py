"""Replace the floating language pill with a ring on the matching flag."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'css', 'sr-tokens.css')
s = open(P, encoding='utf-8', newline='').read()

# 1 · drop the old pill rules (start of the block through its close)
i = s.find('.sr-lang-hint{')
if i >= 0:
    j = s.find('\n', s.find('.sr-lang-hint__close', i))
    # walk to the end of the last related rule
    end = s.find('}', s.find('.sr-lang-hint__close', i))
    end = s.find('\n', end) if end > 0 else j
    removed = s[i:end]
    s = s[:i] + s[end:]
    print('old pill rules removed: %.1f KB' % (len(removed.encode()) / 1024))
else:
    print('old pill rules not found')

# 2 · add the ring, placed next to the dock rules
RING = """
/* Language hint inside the dock: a gold ring on the flag for the visitor's
   own language, shown once, then gone. No extra element on screen. */
.apple-dock-item.sr-lang-hint-pulse{position:relative}
.apple-dock-item.sr-lang-hint-pulse::after{
  content:'';position:absolute;inset:-4px;border-radius:12px;pointer-events:none;
  border:2px solid rgba(var(--sr-gold-rgb,212,175,55),.9);
  box-shadow:0 0 0 4px rgba(var(--sr-gold-rgb,212,175,55),.14),0 0 14px rgba(var(--sr-gold-rgb,212,175,55),.35);
  animation:srLangPulse 1.5s ease-in-out infinite}
@keyframes srLangPulse{0%,100%{opacity:.45}50%{opacity:1}}
@media (prefers-reduced-motion: reduce){
  .apple-dock-item.sr-lang-hint-pulse::after{animation:none;opacity:.95}
}
"""

if 'sr-lang-hint-pulse' not in s:
    anchor = '.apple-macos-dock-wrapper'
    k = s.find(anchor)
    if k < 0:
        s = s.rstrip() + '\n' + RING
    else:
        # insert right before the dock wrapper block
        s = s[:k] + RING.strip() + '\n\n' + s[k:]
    print('ring styles added')

open(P, 'w', encoding='utf-8', newline='').write(s)
print('sr-tokens.css now: %.1f KB' % (os.path.getsize(P) / 1024))
