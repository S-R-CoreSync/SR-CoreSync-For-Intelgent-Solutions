P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

# 1 · drop the hard-coded order that pinned the brand to the left
n = 0
for old, new in (
    ('<div class="header-col-brand" style="order: 3 !important;">', '<div class="header-col-brand">'),
    ('<div class="header-col-nav" style="order: 1 !important;">', '<div class="header-col-nav">'),
):
    if old in s:
        s = s.replace(old, new, 1)
        n += 1

# 2 · let the Arabic menu sit beside the brand, not float in the middle
rule = ('\r\n/* Arabic header: the menu starts beside the brand, at the right,\r\n'
        '   and the brand takes its natural first position (logo right). */\r\n'
        'html[lang="ar"] .header-col-nav .box-navigation{justify-content:flex-start !important}\r\n')
if 'box-navigation{justify-content:flex-start' not in s:
    anchor = '</style>\r\n<style id="srf-css">'
    assert anchor in s
    s = s.replace(anchor, rule + anchor, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print('inline orders removed:', n, '· rule added')
