P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\scripts\row_x.mjs'
s = open(P, encoding='utf-8').read()
if 'process.argv[2]' not in s:
    s = s.replace('width: 1600, height: 900', 'width: Number(process.argv[2] || 1600), height: Number(process.argv[3] || 900)')
    open(P, 'w', encoding='utf-8').write(s)
    print('width is a parameter now')
else:
    print('already parameterised')
