# -*- coding: utf-8 -*-
"""Bring the founder-lab block into the Arabic master, translated.

The block exists in all 28 translations and in no master part, so regenerating
pages from the master would have deleted it. It is inserted into the root part
that already owns the software hub, just before that section closes.
"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
SRC = os.path.join(ROOT, 'partials', 'en', '23-store.html')
DST = os.path.join(ROOT, 'partials', '23-store.html')

en = open(SRC, encoding='utf-8', newline='').read()
i = en.find('id="softwareArchitectLab"')
start = en.rfind('<div', 0, i)
depth = 0
end = None
for m in re.finditer(r'<div\b|</div>', en[start:], re.I):
    depth += -1 if m.group(0).startswith('</') else 1
    if depth == 0:
        end = start + m.end()
        break
block = en[start:end]
print('block from en: %.1f KB' % (len(block.encode()) / 1024))

AR = {
 '🚀 FOUNDER&#x27;S LAB &amp; COMMERCIAL DISTRIBUTION PORTAL': '🚀 مختبر المؤسس وبوابة التوزيع التجاري',
 "🚀 FOUNDER'S LAB & COMMERCIAL DISTRIBUTION PORTAL": '🚀 مختبر المؤسس وبوابة التوزيع التجاري',
 'Have Proprietary Software or Systems You Want to License &amp; Distribute Commercially?':
   'هل لديك برمجيات أو أنظمة خاصة تريد ترخيصها وتوزيعها تجارياً؟',
 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?':
   'هل لديك برمجيات أو أنظمة خاصة تريد ترخيصها وتوزيعها تجارياً؟',
 'Hardware-Bound Licensing': 'ترخيص مرتبط بالعتاد',
 'Automated offline node-locking &amp; subscription token validation.':
   'قفل آلي دون اتصال وربط للترخيص بالجهاز، وتحقق من رموز الاشتراك.',
 'Automated offline node-locking & subscription token validation.':
   'قفل آلي دون اتصال وربط للترخيص بالجهاز، وتحقق من رموز الاشتراك.',
 'Automated Billing &amp; VAT': 'فوترة وضريبة آلية',
 'Automated Billing & VAT': 'فوترة وضريبة آلية',
 'Global payment settlement via SEPA, iDEAL, and credit cards with 21% BTW handling.':
   'تحصيل مدفوعات عالمي عبر SEPA وiDEAL وبطاقات الائتمان، مع معالجة ضريبة BTW بنسبة 21%.',
 'High-Availability Hosting': 'استضافة عالية التوافر',
 'Fast redundant download mirrors across Amsterdam and Frankfurt clusters.':
   'مرايا تنزيل سريعة ومتكرّرة في عنقودَي أمستردام وفرانكفورت.',
 'Exclusive Partner Program': 'برنامج شركاء حصري',
 'Publish &amp; Monetize Your Software': 'انشر برمجياتك وحقّق منها دخلاً',
 'Publish & Monetize Your Software': 'انشر برمجياتك وحقّق منها دخلاً',
 'Connect directly with Lead Systems Architect Eng. Salim Aziza to review your system, define commercial licensing tiers, and publish it on our marketplace.':
   'تواصل مباشرة مع مهندس النظم الأول م. سليم عزيزة لمراجعة نظامك، وتحديد فئات الترخيص التجاري، ونشره في سوقنا.',
 'Apply to Publish Your Software Project ←': 'تقدّم لنشر مشروعك البرمجي ←',
 'Test Interactive Software Simulator ⚡': 'جرّب المحاكي البرمجي التفاعلي ⚡',
 'Strict NDAs, full IP ownership protection &amp; transparent revenue share.':
   'اتفاقيات سرية صارمة، وحماية كاملة للملكية الفكرية، وتقاسم إيرادات شفّاف.',
 'Strict NDAs, full IP ownership protection & transparent revenue share.':
   'اتفاقيات سرية صارمة، وحماية كاملة للملكية الفكرية، وتقاسم إيرادات شفّاف.',
}

for k, v in AR.items():
    block = block.replace(k, v)

left = re.findall(r'>([A-Z][A-Za-z0-9 ,.&%\'’\-—]{25,})<', block)
print('english sentences still inside the block:', len(left))
for s in left[:4]:
    print('   ·', s[:70])

dst = open(DST, encoding='utf-8', newline='').read()
if 'softwareArchitectLab' in dst:
    print('already in the master part')
    raise SystemExit

# insert before the closing </section> of the software hub
hub = dst.find('id="software-hub"')
close = dst.find('</section>', hub)
block = block.replace('id="softwareArchitectLab"', 'id="softwareArchitectLab"').strip()
out = dst[:close] + block + '\r\n' + dst[close:]
open(DST, 'w', encoding='utf-8', newline='').write(out)
print('inserted into partials/23-store.html')
