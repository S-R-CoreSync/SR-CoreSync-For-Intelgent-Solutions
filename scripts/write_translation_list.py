# -*- coding: utf-8 -*-
"""The 33 English lines that leak into all 28 translated pages, with the Arabic
they should have carried. Written by hand: the automatic pairing by XPath fails
because the two pages do not share a node tree."""
import csv, os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

ROWS = [
    ('hero', 'Plan your project with interactive voice • AI Engineer ready',
     'خطّط مشروعك بالصوت التفاعلي • مهندس ذكاء اصطناعي جاهز'),
    ('services', 'Distinct visual identities built with strategy, clarity, and consistency.',
     'هويات بصرية مميّزة تُبنى باستراتيجية ووضوح واتساق.'),
    ('services', 'Modern, high-performance websites designed for clarity, trust, and growth.',
     'مواقع عصرية عالية الأداء مصمّمة للوضوح والثقة والنمو.'),
    ('tech', 'Hardened multi-region infrastructure on AWS and Azure with automated failover, zero-trust security, and 99.9% uptime SLA.',
     'بنية تحتية موزّعة على مناطق متعددة في AWS وAzure، مع تحويل تلقائي عند التعطّل، وأمان بلا ثقة مفترضة، واتفاقية توفّر 99.9%.'),
    ('pricing', 'Complete digital and financial enterprise architecture fully customized for established corporations.',
     'منظومة رقمية ومالية متكاملة مخصّصة بالكامل للمؤسسات القائمة.'),
    ('pricing', 'Custom-built enterprise ERP from scratch matching your exact workflows',
     'نظام ERP مؤسسي مبني من الصفر ليطابق سير عملك بدقة'),
    ('pricing', 'Distinct visual identities built with strategy, clarity, and consistency to anchor institutional trust.',
     'هويات بصرية مميّزة تُبنى باستراتيجية ووضوح واتساق لتثبيت الثقة المؤسسية.'),
    ('pricing', 'Modern, high-performance websites engineered for clarity, trust, and growth with instant loading.',
     'مواقع عصرية عالية الأداء مهندسة للوضوح والثقة والنمو مع تحميل فوري.'),
    ('pricing', 'Intuitive online store architecture that turns casual visitors into repeat buyers with frictionless checkout.',
     'بنية متجر إلكتروني بديهية تحوّل الزائر العابر إلى مشترٍ متكرّر عبر دفع بلا تعقيد.'),
    ('software', 'High-performance software library enabling developers and enterprises to integrate European tax compliance and cashflow forecasting into their applications.',
     'مكتبة برمجية عالية الأداء تتيح للمطوّرين والمؤسسات دمج الامتثال الضريبي الأوروبي وتوقّع التدفق النقدي في تطبيقاتهم.'),
    ('software', 'Military-grade AES-256 encryption engine protecting database backups and sensitive contracts, with automated zero-knowledge European cloud sync.',
     'محرّك تشفير AES-256 بمعيار عسكري يحمي نسخ قواعد البيانات والعقود الحساسة، مع مزامنة سحابية أوروبية آلية بلا معرفة بالمحتوى.'),
    ('software', 'Cloud ecosystem for any clinic, medical network, or telehealth center: video consultations, appointments, e-pharmacy, and patient/doctor portals with full GDPR compliance.',
     'منظومة سحابية لأي عيادة أو شبكة طبية أو مركز رعاية عن بُعد: استشارات فيديو ومواعيد وصيدلية إلكترونية وبوابات للمريض والطبيب بامتثال كامل لـGDPR.'),
    ('lab', 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?',
     'لديك برمجيات أو أنظمة خاصة تريد ترخيصها وتوزيعها تجارياً؟'),
    ('lab', 'Publish & Monetize Your Software',
     'انشر برمجياتك وحقّق منها دخلاً'),
    ('lab', 'Connect directly with Lead Systems Architect Eng. Salim Aziza to review your system, define commercial licensing tiers, and publish it on our marketplace.',
     'تواصل مباشرة مع مهندس النظم الأول م. سليم عزيزة لمراجعة نظامك وتحديد فئات الترخيص التجاري ونشره في سوقنا.'),
    ('compliance', 'Legally binding European regulatory certifications, enterprise SLA guarantees, and sovereign cloud infrastructure anchored in Amsterdam, the Netherlands.',
     'شهادات تنظيمية أوروبية مُلزمة قانوناً، وضمانات اتفاقيات خدمة مؤسسية، وبنية سحابية سيادية مقرّها أمستردام في هولندا.'),
    ('compliance', 'Rigorous alignment with ISO/IEC 27001 standards and SOC 2 Type II controls for enterprise risk governance.',
     'مواءمة صارمة مع معيار ISO/IEC 27001 وضوابط SOC 2 Type II لحوكمة المخاطر المؤسسية.'),
    ('compliance', 'S&R CoreSync For Intelligent Solutions operates strictly under Dutch and European Union jurisdictions.',
     'تعمل S&R CoreSync For Intelligent Solutions حصراً ضمن الاختصاص القضائي الهولندي والاتحاد الأوروبي.'),
    ('testimonials', 'A genuine quantum leap in our multi-warehouse management and accounting workflows after deploying S&R CoreSync custom ERP. Exceptional precision and accountability.',
     'قفزة حقيقية في إدارة مستودعاتنا المتعددة وسير العمل المحاسبي بعد تطبيق نظام ERP المخصّص من S&R CoreSync. دقة ومساءلة استثنائيتان.'),
    ('testimonials', 'Their dual mastery of cutting-edge software engineering and financial regulations saved us hundreds of manual hours every monthly close and revenue recognition cycle.',
     'إتقانهم المزدوج لهندسة البرمجيات المتقدمة واللوائح المالية وفّر علينا مئات الساعات اليدوية في كل إقفال شهري ودورة اعتراف بالإيراد.'),
    ('testimonials', 'The mobile platforms and executive cloud dashboards engineered by S&R CoreSync operate with blazing speed and bank-grade security. Our trusted technology partner.',
     'منصات الجوال ولوحات القيادة السحابية التي هندسها فريق S&R CoreSync تعمل بسرعة فائقة وأمان بمستوى البنوك. شريك تقني موثوق.'),
    ('roi', 'Discover How Much Your Organization Saves Annually with',
     'اكتشف كم توفّر مؤسستك سنوياً مع'),
    ('roi', 'Calculate the exact financial savings and reclaimed administrative hours unlocked when automating your workflows and integrating your ERP with our architecture.',
     'احسب التوفير المالي الدقيق والساعات الإدارية المستعادة عند أتمتة سير عملك وربط نظام ERP بمعماريتنا.'),
    ('exec', 'We engineer resilient cloud systems, high-performance web platforms, and automated ERP architectures driving enterprise growth across Europe and the Middle East.',
     'نهندس أنظمة سحابية مرنة ومنصات ويب عالية الأداء ومعماريات ERP مؤتمتة تقود نمو المؤسسات في أوروبا والشرق الأوسط.'),
    ('newsletter', 'Receive monthly corporate ROI benchmarks, European cloud tax (BTW/VAT) automation updates, and exclusive enterprise sandbox access directly to your inbox.',
     'استلم شهرياً مؤشرات العائد المؤسسي وتحديثات أتمتة الضريبة الأوروبية (BTW/VAT) ووصولاً حصرياً إلى بيئة التجربة المؤسسية في بريدك.'),
    ('modal', 'Designed the full brand identity for Sarlor, an artisanal Syrian eatery in the Netherlands specializing in authentic Levantine pastries, manakish, and specialties.',
     'تصميم الهوية البصرية الكاملة لـSarlor، مطعم سوري حرفي في هولندا متخصّص في المعجنات الشامية الأصيلة والمناقيش والأطباق المميّزة.'),
    ('modal', '"A disciplined visual system with sharp rhythm, memorable presence, and enduring resonance."',
     '«نظام بصري منضبط بإيقاع حادّ وحضور لا يُنسى وأثر باقٍ.»'),
    ('modal', 'Instant direct communication with the founding partners to discuss your requirements.',
     'تواصل مباشر فوري مع الشريكين المؤسسين لمناقشة متطلباتك.'),
    ('modal', 'Cloud infrastructure with automated workflows, ledger sync, and inventory',
     'بنية سحابية مع سير عمل مؤتمت ومزامنة للدفاتر وإدارة للمخزون'),
    ('modal', 'A concise walkthrough of our key enterprise modules before entering the complete sandbox.',
     'جولة موجزة على وحداتنا المؤسسية الأساسية قبل الدخول إلى بيئة التجربة الكاملة.'),
    ('modal', 'Access your central cloud management dashboard, deployments, and SLA tickets.',
     'ادخل إلى لوحة إدارة السحابة المركزية والنشر وتذاكر اتفاقية الخدمة.'),
    ('modal', '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions',
     '🛡️ بوابة إدارة تراخيص البرمجيات • حصرية لم. سليم عزيزة، المؤسس والمهندس الأول • S&R CoreSync For Intelligent Solutions'),
    ('modal', 'Thank you for choosing S&R CoreSync For Intelligent Solutions. Your transaction is verified and registered under the Dutch fiscal framework.',
     'شكراً لاختيارك S&R CoreSync For Intelligent Solutions. تم التحقق من معاملتك وتسجيلها وفق الإطار الضريبي الهولندي.'),
]

out = os.path.join(ROOT, 'docs', 'ترجمات-ناقصة.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['#', 'section', 'english', 'arabic_reference', 'chars'])
    for i, (sec, en, ar) in enumerate(ROWS, 1):
        w.writerow([i, sec, en, ar, len(en)])

print('rows:', len(ROWS))
print('total english characters:', sum(len(r[1]) for r in ROWS))
by = {}
for sec, _, _ in ROWS:
    by[sec] = by.get(sec, 0) + 1
print('by area:', by)
