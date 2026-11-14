"""Remove the pill block as one contiguous span, then append the ring."""
import os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'css', 'sr-tokens.css')
s = open(P, encoding='utf-8', newline='').read()

start = s.find('/* Language hint:')
assert start > 0, 'pill comment not found'
close_idx = s.find('.sr-lang-hint__close', start)
assert close_idx > start
end = s.find('}', close_idx) + 1

removed = s[start:end]
s = s[:start] + s[end:].lstrip('\n')

RING = """/* ── Language hint, inside the dock ────────────────────────────────────────
   The visitor's own language gets a gold ring for six seconds, on the flag
   that already exists. No second language control on screen. */
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

s = s.rstrip() + '\n\n' + RING
open(P, 'w', encoding='utf-8', newline='').write(s)

print('pill block removed: %.1f KB' % (len(removed.encode()) / 1024))
print('ring appended:', 'sr-lang-hint-pulse' in s)
print('braces: %d/%d' % (s.count('{'), s.count('}')))
