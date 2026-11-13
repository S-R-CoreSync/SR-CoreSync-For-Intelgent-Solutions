P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

start = s.find('<section id="trust-metrics"')
assert start > 0, 'section not found'
end = s.find('</section>', start) + len('</section>')
block = s[start:end]

# the aside that really sits in the body, not the CSS mention
dock = s.find('<aside class="apple-macos-dock-wrapper"')
assert dock > 0, 'dock anchor missing'

if start > dock:
    print('the section already sits after the dock; nothing to move')
else:
    cut = end
    if s[end:end + 4] == '\r\n\r\n':
        cut = end + 4
    elif s[end:end + 2] == '\r\n':
        cut = end + 2
    out = s[:start] + s[cut:]
    dock = out.find('<aside class="apple-macos-dock-wrapper"')
    out = out[:dock] + block + '\r\n\r\n' + out[dock:]
    open(P, 'w', encoding='utf-8', newline='').write(out)
    print('moved: hero -> beside the dock (%d chars)' % len(block))
