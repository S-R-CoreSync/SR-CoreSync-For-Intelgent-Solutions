import subprocess
import os

ART_DIR = r'C:\Users\msali\.gemini\antigravity\brain\36a38584-d480-4aa6-b502-4d07f979cd72'
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
temp_profile = os.path.join(ART_DIR, 'temp_chrome_profile_map')

test_html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>Real SRLangMap Live Test</title>
  <style>body { background: #030b08; margin: 0; padding: 0; font-family: Alexandria, sans-serif; }</style>
</head>
<body>
  <div style="padding: 40px; color: gold;">Testing Live SR Language Map Option 2...</div>
  <script src="js/sr-lang-map.js?v=20261120-hud2"></script>
  <script>
    window.addEventListener('DOMContentLoaded', function() {
      if (window.SRLangMap && window.SRLangMap.open) {
        window.SRLangMap.open();
      }
    });
  </script>
</body>
</html>"""

test_path = 'temp_real_map_test.html'
with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_html)

out_file = os.path.join(ART_DIR, 'real_lang_map_option2_live.png')
t_url = 'file:///' + os.path.abspath(test_path).replace('\\', '/')

cmd = [
    chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--incognito',
    f'--user-data-dir={temp_profile}',
    f'--screenshot={out_file}',
    '--window-size=1600,980',
    '--virtual-time-budget=2500',
    '--run-all-compositor-stages-before-draw',
    t_url
]
subprocess.run(cmd, capture_output=True, text=True, timeout=25)

if os.path.exists(test_path):
    os.remove(test_path)

size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
print(f"Captured real_lang_map_option2_live.png: exists={os.path.exists(out_file)}, size={size}")
