P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\scripts\remaining_english.py'
s = open(P, encoding='utf-8').read()
s = s.replace("print('  ·', t[:120])", "print('  ·', t)")
open(P, 'w', encoding='utf-8').write(s)
print('full text enabled')
