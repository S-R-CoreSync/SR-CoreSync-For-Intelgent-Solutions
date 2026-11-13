P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\docs\header-direction-preview.html'
s = open(P, encoding='utf-8', newline='').read()
old = '<div class="hdr">'
if '<div class="hdr" dir="ltr">' not in s:
    assert old in s
    s = s.replace(old, '<div class="hdr" dir="ltr">', 1)
    s = s.replace('.hdr{display:flex;', '.hdr[dir="ltr"] .brand{order:0}\r\n  .hdr{display:flex;', 1)
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('current panel forced to LTR')
else:
    print('already LTR')
