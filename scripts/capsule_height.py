P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

if '.sr-tools-capsule .header-col-actions > button' in s:
    print('already set')
else:
    anchor = '  .sr-tools-capsule .header-col-actions{margin:0 !important; gap:6px !important}'
    assert anchor in s, 'capsule child rule missing'
    add = (anchor + '\r\n'
           '  /* 46px overall: 34 for the buttons plus 5+5 padding and the border,\r\n'
           '     so the capsule is the same height as the language dock beside it. */\r\n'
           '  .sr-tools-capsule{padding:5px !important}\r\n'
           '  .sr-tools-capsule .header-col-actions{height:34px !important}\r\n'
           '  .sr-tools-capsule .header-col-actions > button{\r\n'
           '    height:34px !important; line-height:18px !important; padding-top:0 !important;\r\n'
           '    padding-bottom:0 !important; display:inline-flex !important;\r\n'
           '    align-items:center !important; justify-content:center !important;\r\n'
           '  }')
    s = s.replace(anchor, add, 1)
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('capsule brought to 46px')
