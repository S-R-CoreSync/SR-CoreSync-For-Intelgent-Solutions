P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
orig = s

# ---- 1 · pull the section out of wherever it is now ----
start = s.find('<section id="trust-metrics"')
assert start > 0
end = s.find('</section>', start) + len('</section>')
block = s[start:end]
s = s[:start] + s[end:]
# tidy the blank line left behind
s = s.replace('\r\n\r\n\r\n', '\r\n\r\n')

# ---- 2 · put it right after the hero, before the first section anchor ----
anchor = '<div id="service" data-section class="section-scroll-anchor"'
assert anchor in s, 'hero end anchor missing'
i = s.find(anchor)
s = s[:i] + block + '\r\n\r\n' + s[i:]

# ---- 3 · replace the v7 style block with v8 ----
v7_start = s.find('/* === v7 - one bottom row')
assert v7_start > 0, 'v7 block not found'
v7_end = s.find('}', s.find('.trust-metric-separator{height:26px !important}')) + 1
old_block = s[v7_start:v7_end]

NEW = """/* === v8 - bottom row: tools left, languages centre, counters right ===
   All three share one height (46px), one baseline and one typeface.
   The counters live just outside the hero because #home carries
   "contain: layout", which would trap a fixed child inside it.
   Below 1320px the row does not fit, so the counters sit one step above. */
@media (min-width:601px){
  .section-trust-metrics{
    position:fixed !important; right:22px !important; left:auto !important;
    bottom:calc(var(--privacy-h, 0px) + var(--consent-h, 0px) + 78px) !important;
    width:auto !important; margin:0 !important; padding:0 !important;
    z-index:9997;
  }
  .section-trust-metrics .hero-trust-metrics-strip{
    height:46px !important; box-sizing:border-box !important;
    display:flex !important; flex-wrap:nowrap !important;
    align-items:center !important; justify-content:flex-end !important;
    gap:16px !important; margin:0 !important; padding:0 16px !important;
    border-radius:14px !important;
    font-family:'Alexandria',system-ui,-apple-system,sans-serif !important;
  }
  .section-trust-metrics .trust-metric-item{
    height:auto !important; display:flex !important; flex-direction:column !important;
    align-items:center !important; justify-content:center !important;
    gap:1px !important; text-align:center !important; white-space:nowrap !important;
  }
  .section-trust-metrics .metric-val{
    font-family:'Alexandria',system-ui,-apple-system,sans-serif !important;
    font-size:12.5px !important; line-height:1.3 !important; letter-spacing:0 !important;
  }
  .section-trust-metrics .metric-lbl{
    font-family:'Alexandria',system-ui,-apple-system,sans-serif !important;
    font-size:10px !important; line-height:1.2 !important;
  }
  .section-trust-metrics .trust-metric-separator{height:26px !important}
}
@media (min-width:1320px){
  .section-trust-metrics{
    bottom:calc(var(--privacy-h, 0px) + var(--consent-h, 0px) + 14px) !important;
  }
}"""

s = s.replace(old_block, NEW, 1)

if s != orig:
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('v8 applied; section sits after the hero')
else:
    print('no change')
