P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('.section-trust-metrics .trust-metric-separator{height:26px !important}')
j = s.find('</style>', i)
seg = s[i:j]
for bad, good in (('  }\n}\n}\n', '  }\n}\n'), ('  }\r\n}\r\n}\r\n', '  }\r\n}\r\n')):
    if seg.endswith(bad):
        seg = seg[: -len(bad)] + good
        print('removed the stray brace')
        break
else:
    print('tail is:', repr(seg[-30:]))
s = s[:i] + seg + s[j:]
open(P, 'w', encoding='utf-8', newline='').write(s)
