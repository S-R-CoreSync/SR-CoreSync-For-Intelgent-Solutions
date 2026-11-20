import http.server
import socketserver
import threading
import subprocess
import os
import time

PORT = 8933
ART_DIR = r'C:\Users\msali\.gemini\antigravity\brain\36a38584-d480-4aa6-b502-4d07f979cd72'
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
temp_profile = os.path.join(ART_DIR, 'temp_chrome_profile_map')

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

httpd = socketserver.TCPServer(('127.0.0.1', PORT), Handler)
server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()

test_html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>Real SRLangMap Live Test</title>
  <style>
    body { background: #030b08; margin: 0; padding: 0; font-family: Alexandria, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }
  </style>
</head>
<body>
  <script src="js/sr-lang-map.js?v=20261120-hud2"></script>
  <script>
    window.addEventListener('DOMContentLoaded', function() {
      if (window.SRLangMap && window.SRLangMap.open) {
        window.SRLangMap.open();
        setTimeout(function() {
          var host = document.getElementById('srLangMapHost');
          if (host && host.shadowRoot) {
            var pin = host.shadowRoot.querySelector('.sr-lm__pin[data-id="iq"]');
            if (pin) {
              pin.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, cancelable: true }));
              console.log('Hover dispatched on iq!');
            } else {
              console.log('Pin iq not found');
            }
          } else {
            console.log('Host/ShadowRoot not found');
          }
        }, 500);
      }
    });
  </script>
</body>
</html>"""

test_file = 'temp_map_test2.html'
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_html)

out_file = os.path.join(ART_DIR, 'real_lang_map_option2_live.png')
url = f'http://127.0.0.1:{PORT}/{test_file}'

cmd = [
    chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--incognito',
    f'--user-data-dir={temp_profile}',
    f'--screenshot={out_file}',
    '--window-size=1600,980',
    '--virtual-time-budget=3000',
    '--run-all-compositor-stages-before-draw',
    url
]
res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
httpd.shutdown()

if os.path.exists(test_file):
    os.remove(test_file)

size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
print(f"Captured real_lang_map_option2_live.png: exists={os.path.exists(out_file)}, size={size}")
