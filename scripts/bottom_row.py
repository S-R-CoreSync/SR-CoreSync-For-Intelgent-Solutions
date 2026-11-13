P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

# exact 46px box for the tools capsule
old_tools = "    z-index:9997; display:flex; align-items:center; gap:6px; height:46px;"
new_tools = "    z-index:9997; display:flex; align-items:center; gap:6px; height:46px; box-sizing:border-box;"
if old_tools in s:
    s = s.replace(old_tools, new_tools, 1)

BLOCK = """
/* === v7 - one bottom row: tools left, languages centre, counters right ===
   All three share one height (46px), one baseline and one typeface, so none
   sits higher or shorter than its neighbour. The strip stays in flow below
   1320px because a single row does not fit there. */
@media (min-width:1320px){
  .section-trust-metrics{
    position:fixed !important; right:22px !important; left:auto !important;
    bottom:calc(var(--privacy-h, 0px) + var(--consent-h, 0px) + 14px) !important;
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
"""

anchor = "</style>\r\n<style id=\"srf-css\">"
if 'v7 - one bottom row' not in s:
    assert anchor in s, 'srf-css anchor missing'
    s = s.replace(anchor, BLOCK + anchor, 1)
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('bottom row unified')
else:
    print('already unified')
