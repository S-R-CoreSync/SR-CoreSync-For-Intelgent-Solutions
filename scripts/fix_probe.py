P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\scripts\layout_probe.mjs'
s = open(P, encoding='utf-8').read()
old = "t.url.includes('8150')"
new = "t.url.includes(process.argv[2] || '8150')"
if old in s:
    open(P, 'w', encoding='utf-8').write(s.replace(old, new, 1))
    print('probe accepts a target now')
else:
    print('already parameterised')
