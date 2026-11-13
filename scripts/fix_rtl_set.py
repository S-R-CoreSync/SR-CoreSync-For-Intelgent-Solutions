P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\scripts\check_hreflang.py'
s = open(P, encoding='utf-8').read()
old = "RTL = {'ar', 'ckb', 'ku'}"
new = ("# Kurmanji (ku) is written in Latin letters, so it is LTR; Sorani (ckb) is not.\r\n"
       "RTL = {'ar', 'ckb'}")
if old in s:
    s = s.replace(old, new, 1)
    open(P, 'w', encoding='utf-8').write(s)
    print('ku corrected to LTR')
else:
    print('already corrected')
