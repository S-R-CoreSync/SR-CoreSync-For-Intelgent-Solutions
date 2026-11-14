P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\scripts\check_hreflang.py'
s = open(P, encoding='utf-8').read()
old = "ROOT = r'D:\\I-Ai\\App\\S&R CoreSync For Intelligent Solutions\\Project'"
new = ("# resolved from this file, so the same guard runs on the runner and on Windows\r\n"
       "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))")
if old in s:
    s = s.replace(old, new, 1)
    open(P, 'w', encoding='utf-8').write(s)
    print('ROOT is now relative to the script')
else:
    print('pattern not found')
