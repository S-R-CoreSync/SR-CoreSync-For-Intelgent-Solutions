import re, sys, os

p = os.path.join(os.environ['TEMP'], 'danana.html')
h = open(p, encoding='utf-8', errors='replace').read()
print('bytes', len(h))

m = re.search(r'<html[^>]*>', h, re.I)
print('HTML TAG:', (m.group(0)[:300] if m else 'none'))

for pat in (r'<title[^>]*>(.*?)</title>', r'<meta[^>]+generator[^>]*>', r'<meta[^>]+description[^>]*>'):
    for mm in re.finditer(pat, h, re.I | re.S):
        print('META:', mm.group(0)[:200])

print('\n--- css ---')
for mm in list(re.finditer(r'<link[^>]+stylesheet[^>]*>', h, re.I))[:16]:
    print(mm.group(0)[:170])

print('\n--- js ---')
for mm in list(re.finditer(r'<script[^>]+src=["\']([^"\']+)', h, re.I))[:24]:
    print(mm.group(1)[:150])

print('\n--- hreflang ---')
for mm in list(re.finditer(r'<link[^>]+hreflang=[^>]*>', h, re.I))[:16]:
    print(mm.group(0)[:200])

print('\n--- signals ---')
for sig in ['wp-content', 'wp-json', 'elementor', 'swiper', 'aos', 'gsap', 'lottie', 'fontawesome',
            'font-awesome', 'fonts.googleapis', 'cdn.jsdelivr', 'unpkg', 'sweetalert', 'animate.css',
            'wpml', 'polylang', 'translatepress', 'trp-', 'gtranslate', 'weglot', 'og:locale',
            'alternate', 'dir="rtl"', 'data-elementor']:
    c = len(re.findall(re.escape(sig), h, re.I))
    if c:
        print('%-20s %d' % (sig, c))
