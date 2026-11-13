# -*- coding: utf-8 -*-
"""Port the v3/v4 hero from the Arabic master into a localized page.

Localized pages get: the three style layers, the hero markup (translated),
a measure-only script (belt + hero budget) and the dock-merge script.
The header is left exactly as the localized page designed it — the master's
header choreography (RTL brand move) must not run on an LTR page.
"""
import re, sys, os

MASTER = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
AR = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

EN = {
  "أنظمة برمجية متقدمة": "Advanced software systems",
  "تطبيقات ومنصات رقمية": "Digital apps and platforms",
  "هويات بصرية تُبنى لتدوم": "Brand identities built to last",
  "اكتب فكرة مشروعك هنا…": "Type your project idea here…",
  "حلّل فكرتي ✦": "Analyse my idea ✦",
  "تجربة النظام السحابي الحي": "Try the live cloud system",
  "نسخة تجريبية حيّة": "Live demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Or start from what fits your project:",
  "متجر إلكتروني فاخر": "Luxury online store",
  "نظام ERP متكامل": "Full ERP system",
  "هوية بصرية كاملة": "Complete brand identity",
  "موقع تعريفي عالي التحويل": "High-converting website",
  "أتمتة وربط الأنظمة": "Automation & integrations",
  "استشارة تقنية": "Tech consultation",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Type your project idea here…",
  "حلل فكرتي بالـ AI ⚡": "Analyse my idea ⚡",
  "حلّل فكرتي": "Analyse my idea",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Describe your idea by voice",
  "فكرة المشروع": "Project idea",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Install S&amp;R CoreSync on your device",
  "تثبيت التطبيق": "Install app",
  "أدوات الدعم": "Support tools",
  "خريطة 34 سوقاً": "34 markets map",
}

LTR = """
/* LTR corrections for localized pages */
html[dir="ltr"] .hv2__copy{align-items:flex-start !important; text-align:left !important}
html[dir="ltr"] .hv2__chips .hv2__chiprow{direction:ltr !important; justify-content:flex-start !important}
html[dir="ltr"] .hv2__badge, html[dir="ltr"] .hv2__h1{text-align:left !important}
html[dir="ltr"] .hv2__rot span{inset-inline-start:0}
"""

BELT = """<script id="hv2-belt">
(function(){
  'use strict';
  function q(id){ return document.getElementById(id); }
  function h(el){ if(!el) return 0; var s=getComputedStyle(el);
    if(s.display==='none'||s.visibility==='hidden') return 0;
    var r=el.getBoundingClientRect(); return r.height>4?r.height:0; }
  function measure(){
    var pb=q('srPrivacyBannerWrap'), ph=0;
    if(pb){ var r=pb.getBoundingClientRect(); if(r.height>4){ ph=Math.max(r.height, window.innerHeight-r.top); } }
    var c=document.querySelector('.sr-consent'), ch=0;
    if(c){ var cs=getComputedStyle(c); if(cs.display!=='none'&&cs.visibility!=='hidden'){ ch=c.getBoundingClientRect().height||0; } }
    document.documentElement.style.setProperty('--privacy-h', Math.round(ph)+'px');
    document.documentElement.style.setProperty('--consent-h', Math.round(ch)+'px');
    document.documentElement.style.setProperty('--chrome-h', Math.round(Math.max(h(q('srPrivacyBannerWrap')), h(q('srQuickDockContainer')), 0))+16+'px');
    var hero=q('hero');
    if(hero){ hero.style.setProperty('min-height', Math.max(460, Math.round(window.innerHeight-142-ch-ph))+'px', 'important'); }
  }
  if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded', measure, {once:true}); } else { measure(); }
  window.addEventListener('load', measure, {once:true});
  setTimeout(measure, 900); setTimeout(measure, 2200);
  window.addEventListener('resize', measure, {passive:true});
  if(window.MutationObserver){ new MutationObserver(measure).observe(document.body, {childList:true, attributes:true, attributeFilter:['class','style']}); }
})();
</script>"""


def block(src, marker, tag='div'):
    i = src.index(marker)
    depth = 0
    for m in re.finditer(r'<%s\b|</%s>' % (tag, tag), src[i:]):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + m.end()
        else:
            depth += 1
    raise SystemExit('unbalanced ' + marker)


master = open(MASTER, encoding='utf-8', newline='').read()

styles = []
for sid in ('hv2-css', 'hv2-fixes', 'hv2-order'):
    m = re.search(r'<style id="%s">(.*?)</style>' % sid, master, re.S)
    assert m, sid
    styles.append(re.sub(r'/\*.*?\*/', '', m.group(1), flags=re.S).strip())

a, b = block(master, '<div class="hv2" id="hv2-hero">')
hero = master[a:b]


def translate(text, table):
    for k, v in sorted(table.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(k, v)
    return text


def port(lang, table, dry=False):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in s else '\n'
    if 'id="hv2-hero"' in s:
        print(lang, 'already ported')
        return
    head = translate(hero, table).replace('./assets/', '../assets/')
    css_all = translate('\n'.join(styles), table) + LTR

    for name, chunk in (('hero', head), ('css', css_all), ('belt', BELT)):
        left = AR.findall(chunk)
        if left:
            raise SystemExit('%s: %d Arabic chars left in %s -> %r' % (lang, len(left), name, ''.join(left[:20])))

    i = s.lower().rindex('</head>')
    s = s[:i] + '<style id="hv2-port">' + NL + css_all + NL + '</style>' + NL + s[i:]

    m = re.search(r'<section[^>]*id="hero"[^>]*>', s)
    assert m, 'hero section not found'
    s = s[:m.end()] + NL + head + NL + s[m.end():]

    j = s.lower().rindex('</body>')
    s = s[:j] + BELT + NL + '<script src="../js/sr-dock-merge.js?v=20261113b" defer></script>' + NL + s[j:]

    if dry:
        print(lang, 'dry ok', len(s))
        return
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print(lang, 'ported', len(s))


if __name__ == '__main__':
    langs = sys.argv[1:] or ['en']
    tables = {'en': EN}
    dry = bool(os.environ.get('DRY'))
    for l in langs:
        port(l, tables[l], dry=dry)
