P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
if '#home{contain:style' in s:
    print('already dropped')
else:
    i = s.find('/* === v9 - bottom row')
    assert i > 0, 'v9 block missing'
    note = ("/* The hero carries \"contain: layout\", which makes every fixed child\r\n"
            "   measure against the hero instead of the viewport. Keeping style\r\n"
            "   containment and dropping layout lets the counters join the bottom\r\n"
            "   row without moving anything inside the hero. */\r\n"
            "#home{contain:style !important}\r\n\r\n")
    s = s[:i] + note + s[i:]
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('layout containment dropped for the hero')
