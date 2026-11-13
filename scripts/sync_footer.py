# -*- coding: utf-8 -*-
"""
Footer renderer - phase 2.

Renders the calibrated footer (i18n/footer.calibrated.json) as a standalone,
self-styled block. Two modes:

    python scripts/sync_footer.py --preview ar out.html
    python scripts/sync_footer.py --preview en out.html

Applying it to the 28 pages is deliberately NOT wired yet: the preview is the
review step that proves the shape before any page is touched.
"""
import os, sys, json, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

CSS = """
.srf{direction:rtl;background:#05080e;border-top:1px solid rgba(212,175,55,.22);
  padding:34px 24px 20px;font-family:'Alexandria',system-ui,sans-serif;color:#b9c6d6}
html[dir="ltr"] .srf{direction:ltr}
.srf__inner{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:1.1fr 2fr;gap:34px}
.srf__brand{display:flex;flex-direction:column;gap:8px}
.srf__mark{display:flex;align-items:center;gap:10px}
.srf__mark b{color:#fff;font-size:15px;font-weight:800;letter-spacing:.2px}
.srf__mark span{color:#f3dfba;font-size:11px;letter-spacing:1.4px}
.srf__tag{font-size:11.5px;color:#7f8fa3;line-height:1.7;max-width:34ch}
.srf__cols{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
.srf__col h3{margin:0 0 10px;font-size:11px;font-weight:800;color:#f3dfba;
  letter-spacing:.06em;text-transform:uppercase}
.srf__col ul{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.srf__col a{color:#b9c6d6;text-decoration:none;font-size:12.5px;line-height:1.5}
.srf__col a:hover{color:#f3dfba;text-decoration:underline;text-underline-offset:3px}
.srf__legal{max-width:1180px;margin:26px auto 0;padding-top:14px;
  border-top:1px solid rgba(255,255,255,.08);display:flex;justify-content:space-between;
  gap:12px;font-size:10.5px;color:#7f8fa3}
@media (max-width:900px){
  .srf__inner{grid-template-columns:1fr;gap:22px}
  .srf__cols{grid-template-columns:repeat(2,1fr)}
  .srf__legal{flex-direction:column}
}
"""


def label(link, lang):
    v = link.get(lang)
    return v if v else link.get('en') or link.get('ar') or link['href']


def render(model, lang, base=''):
    rtl = lang == 'ar'
    tag = model['tagline'].get(lang) or model['tagline']['en']
    legal = model['legal_line'].get(lang) or model['legal_line']['en']
    cols = []
    for b in model['blocks']:
        items = ''.join(
            ('<li><a href="#" data-sr-call="%s">%s</a></li>' % (l['srCall'], label(l, lang)))
            if l.get('srCall') else
            ('<li><a href="%s">%s</a></li>' % ((base + l['href'][2:]) if base and l['href'].startswith('./') else l['href'], label(l, lang)))
            for l in b['links']
        )
        cols.append('<div class="srf__col"><h3>%s</h3><ul>%s</ul></div>' % (
            b['title'] if rtl else b['title_en'] if 'title_en' in b else b['title'], items))
    return ('<footer class="srf" id="srf-footer" role="contentinfo" dir="%s">'
            '<div class="srf__inner">'
            '<div class="srf__brand"><div class="srf__mark">'
            '<b>S&amp;R CoreSync</b><span>INTELLIGENT SOLUTIONS</span></div>'
            '<div class="srf__tag">%s</div></div>'
            '<nav class="srf__cols" aria-label="Footer">%s</nav>'
            '</div>'
            '<div class="srf__legal"><span>%s</span><span>GDPR · NIS2 · eIDAS · ISO 27001</span></div>'
            '</footer>' % ('rtl' if rtl else 'ltr', tag, ''.join(cols), legal))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', nargs=2, metavar=('LANG', 'OUT'))
    a = ap.parse_args()
    model = json.load(open(MODEL, encoding='utf-8'))
    if a.preview:
        lang, out = a.preview
        html = ('<!DOCTYPE html><html lang="%s" dir="%s"><head><meta charset="utf-8">'
                '<title>footer preview</title><style>body{margin:0;background:#05080e}%s</style></head>'
                '<body>%s</body></html>' % (lang, 'rtl' if lang == 'ar' else 'ltr', CSS, render(model, lang)))
        open(out, 'w', encoding='utf-8').write(html)
        print('preview ->', out)
    else:
        print('use --preview LANG OUT')


if __name__ == '__main__':
    main()
