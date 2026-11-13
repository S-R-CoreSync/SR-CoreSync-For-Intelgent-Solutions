P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
nl = '\r\n'

# 1 · the tools capsule must be exactly 46px tall, border included
old = "    z-index:9997; display:flex; align-items:center; gap:6px;"
new = "    z-index:9997; display:flex; align-items:center; gap:6px; box-sizing:border-box;"
assert old in s, 'tools rule missing'
s = s.replace(old, new, 1)

# 2 · one row: counters join the same baseline as the capsule and the dock
BLOCK = """
/* === v9 - bottom row: tools left, languages centre, counters right ===
   Three blocks, one height (46px), one baseline, one typeface. The counters
   stay inside the hero, so their fixed offset is measured against the hero
   box; that box ends where the viewport ends, which keeps the three on one
   line. Under 1320px the row cannot hold three blocks, so the counters step
   one level up instead of crowding the dock. */
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
}
"""
anchor = '</style>' + nl + '<style id="srf-css">'
assert anchor in s, 'srf-css anchor missing'
if 'v9 - bottom row' not in s:
    s = s.replace(anchor, BLOCK + anchor, 1)
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('v9 applied in place')
else:
    print('already applied')
