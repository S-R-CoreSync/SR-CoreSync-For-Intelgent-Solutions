#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""البند 24أ — الخيار ج (الموجة الأولى): purge المخفي + بناء المفقود ذي المعالجات الحية.

لكل صفحة لغة (28):
  (1) purge: حذف الأبناء المباشرين المخفيين لـ#hero وفق قاعدة الطبقة في الصفحة نفسها
      (#hero > *:not(...){display:none!important}) — إثبات: كل محذوف مطابق للقاعدة،
      والباقون لم يمسوا؛ صفر تغيير مرئي بالتعريف.
  (2) services: 9 أزرار «🔍 تفاصيل» (openServiceDetail) في 6 tech-card-footer-actions
      + 3 dana-card-actions-row بأستدعاءات المرجع الحرفية، وزر RFQ المستقل (openRfqModal)
      بعد بانر الباقة — يعملان عبر js/services-enhancements-locale.js (المشتق الآمن).
      بانر المرجع نفسه يُترك (ازدواج مرئي لو بُني — قرار موثق).
  (3) founders: تبويب الاستوديو (social-8k-studio) آخر تبويب + 4 روابط واتساب المؤسسين
      (حاويات 1,2,4,5 — hrefs المرجع حرفياً).
  (4) pricing: زر VIP في summary-actions (المعالج في sr-estimator.js المحمّل أصلاً).
  (5) وسم سكربت المشتق بعد وسم sr-estimator.js.

القوالب تُستخرج من index.html المرجع وقت التشغيل (بايت-دقيقة) ويُستبدل النص العربي
بترجمة اللغة. idempotent + --check. الاستخدام: apply [--lang X] | --check
"""
import pathlib, re, sys, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ["bg", "ckb", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "ga", "hr",
         "hu", "it", "ku", "lt", "lv", "mt", "nl", "no", "pl", "pt", "ro", "sk", "sl",
         "sv", "tr"]
with open(ROOT / 'index.html', encoding='utf-8', newline='') as fh:
    MASTER = fh.read()
JS_TAG = '<script src="../js/services-enhancements-locale.js?v=20261118-j" defer></script>'

# ---------------- جدول الترجمات (6 نصوص × 28 لغة) — مؤلف ----------------
T = {
 'en': dict(det='Details', rfq='📋 Request a Quote (RFQ)', vip='Pin this estimate to a VIP booking', vip_t='Open VIP booking window with this estimate details', studio='Certified Brand Identity Studio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'de': dict(det='Details', rfq='📋 Angebot anfordern (RFQ)', vip='Diese Schätzung als VIP-Buchung fixieren', vip_t='VIP-Buchungsfenster mit Details dieser Schätzung öffnen', studio='Zertifiziertes Markenidentitäts-Studio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'fr': dict(det='Détails', rfq='📋 Demander un devis (RFQ)', vip='Figer cette estimation en réservation VIP', vip_t='Ouvrir la réservation VIP avec les détails de cette estimation', studio="Studio d'identité de marque certifié 🎬", wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'es': dict(det='Detalles', rfq='📋 Solicitar presupuesto (RFQ)', vip='Fijar esta estimación en una reserva VIP', vip_t='Abrir la ventana de reserva VIP con los detalles de esta estimación', studio='Estudio de identidad de marca certificado 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'it': dict(det='Dettagli', rfq='📋 Richiedi un preventivo (RFQ)', vip='Fissa questa stima in una prenotazione VIP', vip_t='Apri la prenotazione VIP con i dettagli di questa stima', studio='Studio di identità di marca certificato 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'nl': dict(det='Details', rfq='📋 Offerte aanvragen (RFQ)', vip='Deze schatting vastzetten als VIP-boeking', vip_t='VIP-boekingsvenster openen met details van deze schatting', studio='Gecertificeerde merkidentiteitsstudio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'pt': dict(det='Detalhes', rfq='📋 Solicitar orçamento (RFQ)', vip='Fixar esta estimação numa reserva VIP', vip_t='Abrir a janela de reserva VIP com os detalhes desta estimação', studio='Estúdio de identidade de marca certificado 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'pl': dict(det='Szczegóły', rfq='📋 Zapytanie ofertowe (RFQ)', vip='Zapisz tę wycenę jako rezerwację VIP', vip_t='Otwórz okno rezerwacji VIP ze szczegółami tej wyceny', studio='Certyfikowane studio identyfikacji marki 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'sv': dict(det='Detaljer', rfq='📋 Begär offert (RFQ)', vip='Lås denna uppskattning som VIP-bokning', vip_t='Öppna VIP-bokningsfönstret med denna uppskattning', studio='Certifierad varumärkesidentitetsstudio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'da': dict(det='Detaljer', rfq='📋 Anmod om tilbud (RFQ)', vip='Lås dette estimat som VIP-bookning', vip_t='Åbn VIP-bookingsvinduet med dette estimats detaljer', studio='Certificeret brandidentitets-studie 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'no': dict(det='Detaljer', rfq='📋 Be om tilbud (RFQ)', vip='Lås dette estimatet som VIP-bestilling', vip_t='Åpne VIP-bestillingsvinduet med dette estimatets detaljer', studio='Sertifisert merkevareidentitetsstudio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'fi': dict(det='Yksityiskohdat', rfq='📋 Pyydä tarjous (RFQ)', vip='Lukitse tämä arvio VIP-varaukseksi', vip_t='Avaa VIP-varausikkuna tämän arvion yksityiskohdineen', studio='Sertifioitu brändiidentiteettistudio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'cs': dict(det='Detaily', rfq='📋 Vyžádat nabídku (RFQ)', vip='Upevnit tento odhad jako VIP rezervaci', vip_t='Otevřít okno VIP rezervace s detaily tohoto odhadu', studio='Certifikované studio značkové identity 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'sk': dict(det='Detaily', rfq='📋 Vyžiadať ponuku (RFQ)', vip='Upevniť tento odhad ako VIP rezerváciu', vip_t='Otvoriť okno VIP rezervácie s detailmi tohto odhadu', studio='Certifikované štúdio značkovej identity 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'sl': dict(det='Podrobnosti', rfq='📋 Zahtevaj ponudbo (RFQ)', vip='Pritrdi to oceno kot VIP rezervacijo', vip_t='Odpri okno VIP rezervacije s podrobnostmi te ocene', studio='Certificirani studio identitete blagovne znamke 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'hr': dict(det='Detalji', rfq='📋 Zatraži ponudu (RFQ)', vip='Prikači ovu procjenu uz VIP rezervaciju', vip_t='Otvori prozor VIP rezervacije s detaljima ove procjene', studio='Certificirani studio identiteta branda 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'ro': dict(det='Detalii', rfq='📋 Solicită ofertă (RFQ)', vip='Fixează această estimare ca rezervare VIP', vip_t='Deschide fereastra de rezervare VIP cu detaliile acestei estimări', studio='Studio certificat de identitate de brand 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'bg': dict(det='Детайли', rfq='📋 Заяви оферта (RFQ)', vip='Фиксирай тази оценка като VIP резервация', vip_t='Отвори прозореца за VIP резервация с детайлите на тази оценка', studio='Сертифицирано студио за бранд идентичност 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'el': dict(det='Λεπτομέρειες', rfq='📋 Αίτηση προσφοράς (RFQ)', vip='Καθήλωσε αυτή την εκτίμηση σε κράτηση VIP', vip_t='Άνοιξε το παράθυρο κράτησης VIP με τις λεπτομέρειες αυτής της εκτίμησης', studio='Πιστοποιημένο στούντιο ταυτότητας μάρκας 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'hu': dict(det='Részletek', rfq='📋 Ajánlatkérés (RFQ)', vip='Rögzítsd ezt a becslést VIP foglalásként', vip_t='Nyisd meg a VIP foglalási ablakot e becslés részleteivel', studio='Tanúsított márkaidentitás stúdió 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'et': dict(det='Üksikasjad', rfq='📋 Küsi pakkumist (RFQ)', vip='Kinnita see hinnang VIP-broneeringuna', vip_t='Ava VIP-broneeringu aken selle hinnangu üksikasjadega', studio='Sertifitseeritud brändiidentiteedi stuudio 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'lv': dict(det='Detaļas', rfq='📋 Pieprasīt piedāvājumu (RFQ)', vip='Pieturē šo novērtējumu kā VIP rezervāciju', vip_t='Atvert VIP rezervācijas logu ar šī novērtējuma detaļām', studio='Sertificēta zīmola identitātes studija 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'lt': dict(det='Išsamiau', rfq='📋 Užklausti pasiūlymo (RFQ)', vip='Fiksuoti šį įvertinimą kaip VIP rezervaciją', vip_t='Atverti VIP rezervacijos langą su šio įvertinimo detalėmis', studio='Sertifikuota prekės ženklso identiteto studija 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'ga': dict(det='Sonraí', rfq='📋 Iarr pragháis (RFQ)', vip='Greamaigh an measúnú seo le háirithiú VIP', vip_t='Oscail fuinneog háirithiúcháin VIP le mionsonraithe an mheasúnaithe seo', studio='Stiúideo deimhnithe aitheantais branda 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'mt': dict(det='Detalji', rfq='📋 Itlob kwotazzjoni (RFQ)', vip='Fissa l-istima f\'reżervazzjoni VIP', vip_t="Iftaħ it-tieqa ta' reżervazzjoni VIP bid-detalji ta' din l-istima", studio="Studio ċertifikat ta' l-identità tal-marka 🎬", wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'tr': dict(det='Detaylar', rfq='📋 Teklif İste (RFQ)', vip='Bu tahmini VIP rezervasyona sabitle', vip_t='Bu tahminin detaylarıyla VIP rezervasyon penceresini aç', studio='Sertifikalı marka kimliği stüdyosu 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'ku': dict(det='Hûrgulî', rfq='📋 Xwastina teklîfê (RFQ)', vip='Vê texmînê bicîh bike wekî rêzberiya VIP', vip_t='Pêncereya rêzberiya VIP veke bi hûrguliyên vê texmînê', studio='Stûdyoya nasnameya marka ya pejirandî 🎬', wa_s='WhatsApp M. Salim 💬', wa_r='WhatsApp A. Raed 💬'),
 'ckb': dict(det='وردەکاری', rfq='📋 داواکردنی نرخاندن (RFQ)', vip='ئەم خەملکە ببە بە شوێنگرتنی VIP', vip_t='پەنجەرەی شوێنگرتنی VIP بکەرەوە بە وردەکاری ئەم خەملکە', studio='ستۆدیۆی ناسنامەی براندی پەسەندکراو 🎬', wa_s='واتساپ م. سليم 💬', wa_r='واتساپ أ. رائد 💬'),
}

# ---------------- استخراج القوالب من المرجع ----------------
def extract_templates():
    m_sv = re.search(r'<section[^>]*id="services".*?(?=<section[^>]*id="[a-z-]+")', MASTER, re.S).group(0)
    m_pr = re.search(r'<section[^>]*id="pricing".*?(?=<section[^>]*id="[a-z-]+"|<footer class="srf")', MASTER, re.S).group(0)
    det = re.search(r'<button[^>]*class="tech-btn-consult"[^>]*data-sr-call="openServiceDetail"[^>]*data-sr-args=\'\["[a-z-]+"\]\'[^>]*>[^<]*</button>', m_sv)
    rfq_div = re.search(r'<div style="margin-top:0\.9rem;text-align:center;">\s*<button type="button" class="dana-btn-booking" data-sr-call="openRfqModal" data-sr-args=\'\[null\]\'[^>]*>[^<]*</button>\s*</div>', MASTER)
    vip = re.search(r'<button[^>]*data-sr-call="transferEstimatorToVipBooking"[^>]*class="estimator-btn-vip"[^>]*>\s*<span>[^<]*</span>\s*</button>', m_pr)
    tab = re.search(r'<a\s+href="social-8k-studio\.html"[^>]*class="showcase-tab-btn showcase-tab-btn-social8k"[^>]*>\s*<span class="showcase-tab-dot"></span>\s*<span>[^<]*</span>\s*</a>', MASTER)
    wa = re.findall(r'<a href="https://wa\.me/31618111116\?text=[^"]+"[^>]*class="showcase-action-btn showcase-action-wa"[^>]*>\s*<span>[^<]*</span>\s*</a>', MASTER)
    assert det and rfq_div and vip and tab and len(wa) == 4, (bool(det), bool(rfq_div), bool(vip), bool(tab), len(wa))
    return dict(det=det.group(0), rfq_div=rfq_div.group(0), vip=vip.group(0), tab=tab.group(0), wa=wa)

TPL = extract_templates()
AR_DET = re.search(r'>([^<]*)</button>', TPL['det']).group(1)
AR_RFQ = re.search(r'>([^<]*)</button>', TPL['rfq_div']).group(1)
AR_VIP = re.search(r'<span>([^<]*)</span>', TPL['vip']).group(1)
AR_TAB = re.findall(r'<span>([^<]*)</span>', TPL['tab'])[-1]
AR_WA = [re.search(r'<span>([^<]*)</span>', w).group(1) for w in TPL['wa']]
WA_HREF = [re.search(r'href="([^"]+)"', w).group(1) for w in TPL['wa']]  # [s,r,s,r]
print('قوالب المرجع مستخرجة: تفاصيل/RFQ/VIP/تبويب/واتساب×4 — نصوص عربية: %s' % ([AR_DET, AR_RFQ, AR_VIP, AR_TAB, AR_WA],))

# ---------------- مساعدات جراحة النص (بايت-دقيقة) ----------------
VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'area', 'col', 'embed', 'track', 'wbr'}

def span_of_element(s, open_start):
    """نهاية العنصر المفتوح عند open_start (بعد الوسم المطابق) — عدّ عمق بايتي."""
    m = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', s[open_start:])
    if not m:
        return None
    tag = m.group(1)
    open_end = s.find('>', open_start)
    if open_end < 0:
        return None
    open_end += 1
    frag = s[open_start:open_end]
    if frag.rstrip('>').endswith('/') or tag.lower() in VOID:
        return open_end
    depth = 1
    for mm in re.finditer(r'<(/?)' + tag + r'\b[^>]*>', s[open_end:]):
        if mm.group(1) == '/':
            depth -= 1
        elif not mm.group(0).endswith('/>'):
            depth += 1
        if depth == 0:
            return open_end + mm.end()
    return None

def child_spans(container_inner_start, s):
    """امتدادات الأبناء المباشرين (عناصر وتعليقات) داخل حاوية تبدأ داخلياً عند الموضع المعطى."""
    out = []
    i = container_inner_start
    while i < len(s):
        j = s.find('<', i)
        if j < 0:
            break
        if s.startswith('<!--', j):
            e = s.find('-->', j)
            e = len(s) if e < 0 else e + 3
        else:
            e = span_of_element(s, j)
            if e is None:
                break
        out.append((j, e, s[j:e]))
        i = e
    return out

def cls_tokens(open_frag):
    m = re.search(r'class="([^"]*)"', open_frag)
    return set((m.group(1) if m else '').split())

def insert_at(s, pos, chunk, what):
    s2 = s[:pos] + chunk + s[pos:]
    # إثبات الإدراج الصرف موضعياً (يساوي الأصل حرفياً بعد نزع المقطع من موضع إدخاله)
    assert s2[pos:pos + len(chunk)] == chunk, 'الشريحة المدرجة لا تطابق: ' + what
    assert s2[:pos] == s[:pos] and s2[pos + len(chunk):] == s[pos:], 'الخارج تغيّر: ' + what
    return s2

DET_ARGS = ['cloud-software', 'mobile-web', 'enterprise', 'automation-ai', 'finance-gov', 'cloud-security']
DANA_ARGS = ['identity', 'web', 'ecommerce']
WA_MAP = [(1, 0), (2, 1), (4, 0), (5, 1)]  # (فهرس الحاوية، فهرس قالب الواتساب: 0=سليم 1=رائد)

def btn_sig(open_frag):
    # التوقيع call-only: مناعة ضد انحراف args بين اللقاطات (نصوص وأستدعاءات)
    call = re.search(r'data-sr-call="([^"]*)"', open_frag)
    return (call.group(1) if call else '',)

def hero_sig_map():
    """خريطة first-class → Counter((call,args)) لأبناء hero المرجع."""
    from collections import Counter
    mm = re.search(r'<(section|div)\b[^>]*id="hero"', MASTER)
    kids = child_spans(MASTER.find('>', mm.start()) + 1, MASTER)
    m_map = {}
    for st, en, frag in kids:
        if frag.lstrip().startswith('<!--'):
            continue
        of = frag[:frag.find('>') + 1]
        ct = cls_tokens(of)
        if not ct:
            continue
        cnt = Counter()
        for bm in re.finditer(r'<(button|a)\b', frag):
            e = span_of_element(frag, bm.start())
            if e is None:
                continue
            el = frag[bm.start():e]
            ofb = el[:el.find('>') + 1]
            if ofb.startswith('<a') and 'btn' not in cls_tokens(ofb):
                continue  # البصمة الرسمية: button + a.btn حصراً
            cnt[btn_sig(ofb)] += 1
        m_map.setdefault(sorted(ct)[0], Counter()).update(cnt)
    return m_map

MASTER_HERO_MAP = None

def reconcile_shared_hero(s, report):
    """حذف الأزرار الزائدة داخل كتل hero المشتركة مع المرجع (المخفية بالطبقة)."""
    global MASTER_HERO_MAP
    if MASTER_HERO_MAP is None:
        MASTER_HERO_MAP = hero_sig_map()
    from collections import Counter
    m_rule = re.search(r'#hero\s*>\s*\*((?::not\(\.[A-Za-z0-9_-]+\))*)\s*\{[^}]*?display:\s*none', s)
    keep = set(re.findall(r':not\(\.([A-Za-z0-9_-]+)\)', m_rule.group(1))) if m_rule else set()
    mh = re.search(r'<(section|div)\b[^>]*id="hero"', s)
    if not mh:
        return s, 0
    inner = s.find('>', mh.start()) + 1
    kids = child_spans(inner, s)
    dels = []
    for st, en, frag in kids:
        if frag.lstrip().startswith('<!--'):
            continue
        of = frag[:frag.find('>') + 1]
        ct = cls_tokens(of)
        if not ct or (ct & keep):
            continue  # بلا صنف أو مرئي (ضمن keep) — لا يُمس
        m_cnt = MASTER_HERO_MAP.get(sorted(ct)[0])
        if not m_cnt:
            continue  # غائب عن المرجع — purge_hero يفعلته
        # أزرار هذا الابن: أبقِ أول n من كل توقيع، واحذف الفائض
        budget = Counter(m_cnt)
        pos = s.find('>', st) + 1  # من داخل الابن — لا من وسمه (والتقدم سطراً عند غير الأزرار)
        while True:
            j = s.find('<', pos)
            if j < 0 or j >= en:
                break
            if s.startswith('<!--', j):
                c2 = s.find('-->', j)
                pos = (c2 + 3) if c2 >= 0 else en
                continue
            if s[j:j + 2] == '</':
                pos = s.find('>', j) + 1
                continue
            mtag = re.match(r'<(button|a)\b', s[j:])
            if mtag:
                e = span_of_element(s, j)
                if e is None or e > en:
                    pos = j + 1
                    continue
                ofb = s[j:s.find('>', j) + 1]
                if ofb.startswith('<a') and 'btn' not in cls_tokens(ofb):
                    pos = e
                    continue  # البصمة الرسمية: button + a.btn حصراً
                sig = btn_sig(ofb)
                if budget[sig] > 0:
                    budget[sig] -= 1
                else:
                    dels.append((j, e))
                pos = e
            else:
                pos = j + 1  # وسم غير زر — تقدم سطراً لفحص أبنائه
    if not dels:
        return s, 0
    for j, e in reversed(dels):
        s = s[:j] + s[e:]
    return s, len(dels)

def purge_hero(s, report):
    m_rule = re.search(r'#hero\s*>\s*\*((?::not\(\.[A-Za-z0-9_-]+\))*)\s*\{[^}]*?display:\s*none', s)
    if not m_rule:
        report.append('hero: لا قاعدة طبقة — تخطي')
        return s, 0
    keep = set(re.findall(r':not\(\.([A-Za-z0-9_-]+)\)', m_rule.group(1)))
    m_hero = re.search(r'<(section|div)\b[^>]*id="hero"', s)
    if not m_hero:
        report.append('hero: لا قسم #hero')
        return s, 0
    # أصناف أبناء hero في المرجع = المسموح بوجودها؛ الزائد = الغائب عن المرجع
    mm = re.search(r'<(section|div)\b[^>]*id="hero"', MASTER)
    m_kids = child_spans(s.find('>', mm.start()) + 1, MASTER)
    master_classes = set()
    for st, en, frag in m_kids:
        if frag.lstrip().startswith('<') and not frag.lstrip().startswith('<!--'):
            ct = cls_tokens(frag[:frag.find('>') + 1])
            if ct:
                master_classes.add(sorted(ct)[0])
    inner_start = s.find('>', m_hero.start()) + 1
    kids = child_spans(inner_start, s)
    hidden = []
    for c in kids:
        frag = c[2].lstrip()
        if not frag.startswith('<') or frag.startswith('<!--'):
            continue
        ct = cls_tokens(frag[:frag.find('>') + 1])
        if not ct:
            continue
        first = sorted(ct)[0]
        if first in master_classes:
            continue  # المرجع يحمله — لا يُمس حتى لو كانت له قاعدة
        # حارس الغلاف: الابن قد يلفّ بنية المرجع (hv2/content-wrap/...) — لا يُحذف إن حملها
        MASTER_KEEP = ('hv2', 'hero-motion-canvas', 'overlay', 'content-wrap')
        if any(re.search(r'class="[^"]*\b%s\b' % k, c[2]) for k in MASTER_KEEP):
            continue
        # إثبات الإخفاء: الصنف ضمن قاعدة الطبقة أو hero-declutter أو أبوه مخفي بالقاعدة
        in_rule = (ct & keep) == set() or any(('.%s' % t) in m_rule.group(0) for t in ct)
        if in_rule:
            hidden.append(c)
    if not hidden:
        report.append('hero: صفر مخفي (نظيف أصلاً)')
        return s, 0
    removed = 0
    for st, en, frag in reversed(hidden):
        s = s[:st] + s[en:]
        removed += 1
    report.append('hero: حُذف %d ابن مخفي غائب عن المرجع' % removed)
    return s, removed

def apply_lang(lang):
    p = ROOT / lang / 'index.html'
    with open(p, encoding='utf-8', newline='') as fh:
        orig = fh.read()
    s = orig
    report = []
    tr = T[lang]

    # (1) purge
    s, n_purged = purge_hero(s, report)

    # (2) services — تفاصيل ×9 (المعالجة من الأخير للأول إبقاء المواضع صحيحة)
    det_btn_tpl = TPL['det']
    n_det = 0
    for kind, arg_list in (('tech-card-footer-actions', DET_ARGS), ('dana-card-actions-row', DANA_ARGS)):
        ops = []
        for m in re.finditer(r'<div class="[^"]*\b%s\b[^"]*"[^>]*>' % kind, s):
            idx = len(re.findall(r'<div class="[^"]*\b%s\b' % kind, s[:m.start()]))
            if idx < len(arg_list):
                ops.append((m, idx, arg_list[idx]))
        for m, idx, arg in reversed(ops):
            seg = s[m.end():m.end() + 400]
            if 'openServiceDetail' in seg:
                continue
            btn = det_btn_tpl.replace("data-sr-args='[\"%s\"]" % DET_ARGS[0], "data-sr-args='[\"%s\"]" % arg)
            btn = btn.replace(AR_DET, tr['det'])
            s = insert_at(s, m.end(), btn, 'det-%s-%d' % (kind, idx))
            n_det += 1
    report.append('services: تفاصيل +%d' % n_det)

    # (2ب) hero — تسوية أزرار الكتل المشتركة مع المرجع (مخفية بالطبقة — صفر مرئي)
    s, n_rec = reconcile_shared_hero(s, report)
    report.append('hero: تسوية داخلية −%d زر زائد' % n_rec)

    # RFQ المستقل وبانر المرجع: متروكان (قرار موثق) — بانر الأسطول في pricing
    # والمرجع في services؛ بناؤهما = ازدواج مرئي أو زر يتيم. قرار المالك لاحقاً.

    # (3) founders — تبويب الاستوديو
    n_tab = 0
    m_ctl = re.search(r'<div class="showcase-controls"[^>]*>', s)
    if m_ctl and 'social8k' not in s[m_ctl.start():m_ctl.start() + 3000]:
        tab = TPL['tab'].replace('href="social-8k-studio.html"', 'href="../social-8k-studio.html"')
        tab = tab.replace(AR_TAB, tr['studio'])
        e = span_of_element(s, m_ctl.start())
        close_pos = s.rfind('</div>', m_ctl.end(), e)
        s = insert_at(s, close_pos, tab, 'studio-tab')
        n_tab = 1
    report.append('founders: تبويب +%d' % n_tab)

    # واتساب المؤسسين ×4 (حاويات 1,2,4,5)
    n_wa = 0
    for idx, wi in WA_MAP:
        ms = list(re.finditer(r'<div class="showcase-footer-actions"[^>]*>', s))
        if idx >= len(ms):
            continue
        m = ms[idx]
        e = span_of_element(s, m.start())
        seg = s[m.end():e]
        if 'showcase-action-wa' in seg:
            continue
        wa = TPL['wa'][wi].replace(AR_WA[wi], tr['wa_s'] if wi == 0 else tr['wa_r'])
        close_pos = s.rfind('</div>', m.end(), e)
        s = insert_at(s, close_pos, wa, 'wa-%d' % idx)
        n_wa += 1
    report.append('founders: واتساب +%d' % n_wa)

    # (4) pricing — زر VIP
    n_vip = 0
    m_sum = re.search(r'<div class="summary-actions"[^>]*>', s)
    if m_sum and 'estimator-btn-vip' not in s[m_sum.end():m_sum.end() + 600]:
        vip = TPL['vip'].replace(AR_VIP, tr['vip'])
        ar_title = re.search(r'title="([^"]+)"', TPL['vip']).group(1)
        vip = vip.replace(ar_title, tr['vip_t'])
        e = span_of_element(s, m_sum.start())
        close_pos = s.rfind('</div>', m_sum.end(), e)
        s = insert_at(s, close_pos, vip, 'vip')
        n_vip = 1
    report.append('pricing: VIP +%d' % n_vip)

    # (4ب) تطبيع title واتساب (كان منسوخاً عربياً من المرجع — تلويث على غير العربية)
    n_tit = 0
    ar_t_s = 'محادثة واتساب مباشرة مع م. محمد سليم عزيزة'
    ar_t_r = 'محادثة واتساب مباشرة مع أ. رائد كعكة'
    if ar_t_s in s:
        s = s.replace('title="%s"' % ar_t_s, 'title="%s"' % tr['wa_s'])
        n_tit += s.count('title="%s"' % tr['wa_s'])
    if ar_t_r in s:
        s = s.replace('title="%s"' % ar_t_r, 'title="%s"' % tr['wa_r'])
    report.append('wa-title: %d' % (1 if n_tit else 0))

    # (5) وسم السكربت المشتق
    n_js = 0
    if JS_TAG not in s:
        m_js = re.search(r'<script src="\.\./js/sr-estimator\.js[^"]*"[^>]*></script>', s)
        if not m_js:
            m_js = re.search(r'<script src="\.\./js/sr-command\.js[^"]*"[^>]*></script>', s)
        if m_js:
            s = insert_at(s, m_js.end(), JS_TAG, 'script-tag')
            n_js = 1
    report.append('script: +%d' % n_js)

    if s != orig:
        p.write_text(s, encoding='utf-8', newline='')
    report.append('إجمالي: حذف %d، إدراج %d' % (n_purged, n_det + n_tab + n_wa + n_vip + n_js))
    return s != orig, ' · '.join(report)

def check_lang(lang):
    with open(ROOT / lang / 'index.html', encoding='utf-8', newline='') as fh:
        s = fh.read()
    pend = []
    sv = re.search(r'<section[^>]*id="services".*?(?=<section[^>]*id="[a-z-]+")', s, re.S)
    n_det = sv.group(0).count('openServiceDetail') if sv else 0
    if n_det != 9:
        pend.append('تفاصيل=%d/9' % n_det)
    if 'social8k' not in s:
        pend.append('studio=0/1')
    n_wa = s.count('showcase-action-wa')
    if n_wa < 4:
        pend.append('wa=%d/4' % n_wa)
    if 'estimator-btn-vip' not in s:
        pend.append('vip=0/1')
    if JS_TAG not in s:
        pend.append('js=0/1')
    return pend

def main():
    check_only = '--check' in sys.argv
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--lang'):
            only = a.split('=')[1] if '=' in a else None
    langs = [only] if only else LANGS
    if check_only:
        bad = 0
        for L in langs:
            pend = check_lang(L)
            if pend:
                bad += 1
                print('⚠ %-4s %s' % (L, ' · '.join(pend)))
        print('CHECK: %d/%d مكتملة' % (len(langs) - bad, len(langs)))
        sys.exit(1 if bad else 0)
    changed = 0
    for L in langs:
        ch, rep = apply_lang(L)
        changed += 1 if ch else 0
        print('◆ %-4s %s' % (L, rep))
    print('\nالملخص: تغيرت %d/%d صفحة' % (changed, len(langs)))

if __name__ == '__main__':
    main()
