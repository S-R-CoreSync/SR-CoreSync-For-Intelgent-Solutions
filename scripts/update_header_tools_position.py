# -*- coding: utf-8 -*-
import os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, 'index.html')

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update hv2-order CSS
old_css = """.header-col-brand  { direction: rtl; grid-column: 1; justify-self: start; }
.header-col-actions{ direction: rtl; grid-column: 2; justify-self: end; margin-inline-end:10px; }
.header-col-nav    { direction: rtl; grid-column: 3; justify-self: end; }"""

new_css = """/* Sovereign Top Navigation Alignment */
html[dir="rtl"] .tf-header .header-inner .header-row-layout{
  direction: rtl !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 16px !important;
}
html[dir="rtl"] .header-col-brand  { order: 1 !important; margin-inline-end: auto !important; }
html[dir="rtl"] .header-col-nav    { order: 2 !important; margin-inline: auto !important; }
html[dir="rtl"] .header-col-actions{ order: 3 !important; margin-inline-start: auto !important; margin-inline-end: 0 !important; }

html[dir="ltr"] .tf-header .header-inner .header-row-layout{
  direction: ltr !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 16px !important;
}
html[dir="ltr"] .header-col-brand  { order: 1 !important; margin-inline-end: auto !important; }
html[dir="ltr"] .header-col-nav    { order: 2 !important; margin-inline: auto !important; }
html[dir="ltr"] .header-col-actions{ order: 3 !important; margin-inline-start: auto !important; margin-inline-end: 0 !important; }

.header-col-brand  { justify-self: start; }
.header-col-actions{ justify-self: end; }
.header-col-nav    { justify-self: center; }"""

if old_css in c:
    c = c.replace(old_css, new_css)
    print("Replaced CSS in index.html")
else:
    print("Warning: old_css not found in index.html")

# 2. Update hv2-dom-order JS
old_dom = """      var isAr = (document.documentElement.lang || '').toLowerCase().indexOf('ar') === 0;
      if (isAr) {
        if (row.firstElementChild !== brand) { row.insertBefore(brand, row.firstElementChild); }
        var navAr = row.querySelector('.header-col-nav');
        var actAr = row.querySelector('.header-col-actions');
        brand.style.setProperty('order', '1', 'important');
        if (navAr) { navAr.style.setProperty('order', '2', 'important'); }
        if (actAr) { actAr.style.setProperty('order', '3', 'important'); }
      } else if (row.lastElementChild !== brand) {
        row.appendChild(brand);
        var navCol = row.querySelector('.header-col-nav');
        var actCol = row.querySelector('.header-col-actions');
        brand.style.setProperty('order', '3', 'important');
        if (navCol) { navCol.style.setProperty('order', '1', 'important'); }
        if (actCol) { actCol.style.setProperty('order', '2', 'important'); }
      }"""

new_dom = """      var navCol = row.querySelector('.header-col-nav');
      var actCol = row.querySelector('.header-col-actions');
      brand.style.setProperty('order', '1', 'important');
      if (navCol) { navCol.style.setProperty('order', '2', 'important'); }
      if (actCol) { actCol.style.setProperty('order', '3', 'important'); }"""

if old_dom in c:
    c = c.replace(old_dom, new_dom)
    print("Replaced JS in index.html")
else:
    print("Warning: old_dom not found in index.html")

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(c)

print("index.html written successfully.")

# Now update across all other language index files (e.g. */index.html)
lang_files = glob.glob(os.path.join(ROOT, '*/index.html'))
for lf in lang_files:
    if '_site' in lf or '.venv' in lf or 'build' in lf:
        continue
    with open(lf, 'r', encoding='utf-8') as f:
        lc = f.read()
    changed = False
    if old_css in lc:
        lc = lc.replace(old_css, new_css)
        changed = True
    if old_dom in lc:
        lc = lc.replace(old_dom, new_dom)
        changed = True
    if changed:
        with open(lf, 'w', encoding='utf-8') as f:
            f.write(lc)
        print(f"Updated {os.path.relpath(lf, ROOT)}")

print("All files updated successfully.")
