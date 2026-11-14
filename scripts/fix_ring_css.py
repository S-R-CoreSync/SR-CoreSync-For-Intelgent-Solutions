"""Put the ring CSS where CSS belongs: appended, not spliced into a selector list."""
import os, re, subprocess

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'css', 'sr-tokens.css')

subprocess.run(['git', 'checkout', '--', 'css/sr-tokens.css'], cwd=ROOT, check=True)
s = open(P, encoding='utf-8', newline='').read()

RING = """

/* ── Language hint, inside the dock ────────────────────────────────────────
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

if 'sr-lang-hint-pulse' not in s:
    s = s.rstrip() + RING
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('ring appended at the end')

# sanity: braces balanced
print('braces: %d open / %d close' % (s.count('{'), s.count('}')))
