import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['de','nl','fr','es','it','pl','pt','ro','sv','cs','tr','el','da','no','fi',
         'hu','sk','sl','hr','lt','lv','et','mt','ga','ku','bg']

BLOCK = """
/* === v9 - bottom row: tools left, languages centre, counters right ===
   One height (46px), one baseline, one typeface for the three blocks.
   The hero carries "contain: layout", which traps fixed children, so it
   keeps style containment only; nothing inside the hero moves for that. */
#home{contain:style !important}
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
  .sr-tools-capsule{box-sizing:border-box !important; padding:5px !important}
  .sr-tools-capsule .header-col-actions{height:34px !important; margin:0 !important; gap:6px !important}
  .sr-tools-capsule .header-col-actions > .btn-pwa-header,
  .sr-tools-capsule .header-col-actions > .btn-support-tools-header{
    height:34px !important; line-height:18px !important; padding-top:0 !important;
    padding-bottom:0 !important;
  }
}
@media (min-width:1320px){
  .section-trust-metrics{
    bottom:calc(var(--privacy-h, 0px) + var(--consent-h, 0px) + 14px) !important;
  }
}
"""

targets = [os.path.join(ROOT, l, 'index.html') for l in LANGS]
targets += [os.path.join(ROOT, 'partials', 'en', '00-gap.html')]

done = skipped = 0
for p in targets:
    s = open(p, encoding='utf-8', newline='').read()
    if 'v9 - bottom row' in s:
        skipped += 1
        continue
    m = re.search(r'</style>\r?\n<style id="srf-css">', s)
    if not m:
        print('anchor missing:', p)
        continue
    s = s[:m.start()] + BLOCK + s[m.start():]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    done += 1

print('written:', done, ' already had it:', skipped)
