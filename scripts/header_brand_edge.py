P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

old = """    if (row && brand && row.lastElementChild !== brand) {\r
      row.appendChild(brand);\r
      /* الصفحة تفرض order في ورقتها، فنفرض ترتيبنا مضمّناً بـ!important */\r
      var navCol = row.querySelector('.header-col-nav');\r
      var actCol = row.querySelector('.header-col-actions');\r
      brand.style.setProperty('order', '3', 'important');\r
      if (navCol) { navCol.style.setProperty('order', '1', 'important'); }\r
      if (actCol) { actCol.style.setProperty('order', '2', 'important'); }\r
      var heroEl = document.getElementById('hero');\r
      if (heroEl) { heroEl.style.removeProperty('padding-bottom'); }\r
    }""".replace('\r\n', '\r\n')

# locate the block by its distinctive first and last lines instead of exact whitespace
start_marker = "    if (row && brand && row.lastElementChild !== brand) {"
end_marker = "      if (heroEl) { heroEl.style.removeProperty('padding-bottom'); }\r\n    }"
i = s.find(start_marker)
assert i > 0, 'header script block not found'
j = s.find(end_marker, i)
assert j > i, 'header script end not found'
j += len(end_marker)

new = """    /* الشعار يقف عند بداية السطر: يميناً في العربية، يساراً في غيرها.
       في صفّ RTL أول عنصر في الوسم هو أقصى اليمين، وفي LTR هو أقصى اليسار. */
    if (row && brand) {
      var isAr = (document.documentElement.lang || '').toLowerCase().indexOf('ar') === 0;
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
      }
      var heroEl = document.getElementById('hero');
      if (heroEl) { heroEl.style.removeProperty('padding-bottom'); }
    }"""

s = s[:i] + new + s[j:]
open(P, 'w', encoding='utf-8', newline='').write(s)
print('the brand keeps the start edge of its own language')
