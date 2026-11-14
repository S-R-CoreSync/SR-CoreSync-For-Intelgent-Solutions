import os, re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\css\sr-tokens.css'
s = open(P, encoding='utf-8', newline='').read()

# drop the hover rule and the mobile override, whatever line ending they carry
before = len(re.findall(r'\.sr-lang-hint(?!-pulse)', s))
s = re.sub(r'\.sr-lang-hint__close:hover\{[^}]*\}\r?\n?', '', s)
s = re.sub(r'@media \(max-width:520px\)\{\.sr-lang-hint\{[^}]*\}\}\r?\n?', '', s)
after = len(re.findall(r'\.sr-lang-hint(?!-pulse)', s))

open(P, 'w', encoding='utf-8', newline='').write(s)
print('pill selectors: %d -> %d' % (before, after))
print('braces: %d/%d' % (s.count('{'), s.count('}')))
print('ring intact:', 'sr-lang-hint-pulse' in s)
