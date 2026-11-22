# -*- coding: utf-8 -*-
"""Enhance Interactive Software Showcase across all 9 products.

1. Fixes card #6 in index.html to pass 'terminal' instead of 'sdk'.
2. Expands the simulator subnav in js/sr-software-apps.js to include all 9 platforms.
3. Implements the full interactive Terminal Agent DevOps simulator view in js/sr-software-apps.js.
4. Adds terminal helper functions (runTerminalCmd, clearTerminalOutput, copyTerminalAgentKey, exportTerminalTelemetryReport).
5. Synchronizes partials and validates all CI test gates.
"""
import os, sys, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(ROOT, 'index.html')
JS_FILE = os.path.join(ROOT, 'js', 'sr-software-apps.js')

def update_index_card6():
    print("Step 1: Checking card #6 in index.html...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    target = '''                                    <div class="software-card-actions">
                                        <button type="button" class="software-btn-download"
                                            data-sr-call="openSoftwareLiveApp" data-sr-args='["sdk"]'
                                            title="تشغيل مراقبة السيرفرات في المتصفح">'''
    replacement = '''                                    <div class="software-card-actions">
                                        <button type="button" class="software-btn-download"
                                            data-sr-call="openSoftwareLiveApp" data-sr-args='["terminal"]'
                                            title="تشغيل مراقبة السيرفرات في المتصفح">'''

    if target in html:
        html = html.replace(target, replacement)
        with open(INDEX_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print("Updated card #6 in index.html to use ['terminal'].")
    else:
        print("Card #6 already updated or pattern not matched.")

def update_js_simulator():
    print("Step 2: Updating js/sr-software-apps.js with 9-app subnav and terminal simulator...")
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Update subnav buttons in function i()
    old_subnav = '''                    <button type="button" class="sr-app-subnav-btn ${"taxsync"===n?"active":""}" onclick="openSoftwareLiveApp('taxsync', currentDeviceMode)">💻 TaxSync</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"flowscan"===n?"active":""}" onclick="openSoftwareLiveApp('flowscan', currentDeviceMode)">📱 FlowScan AI</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"cloudpos"===n?"active":""}" onclick="openSoftwareLiveApp('cloudpos', currentDeviceMode)">⚡ CloudPOS</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"vault"===n?"active":""}" onclick="openSoftwareLiveApp('vault', currentDeviceMode)">🛡️ SecureVault</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"sdk"===n?"active":""}" onclick="openSoftwareLiveApp('sdk', currentDeviceMode)">🧩 Dev SDK</button>\\n'''

    new_subnav = '''                    <button type="button" class="sr-app-subnav-btn ${"taxsync"===n?"active":""}" onclick="openSoftwareLiveApp('taxsync', currentDeviceMode)">💻 TaxSync</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"flowscan"===n?"active":""}" onclick="openSoftwareLiveApp('flowscan', currentDeviceMode)">📱 FlowScan AI</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"cloudpos"===n?"active":""}" onclick="openSoftwareLiveApp('cloudpos', currentDeviceMode)">⚡ CloudPOS</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"vault"===n?"active":""}" onclick="openSoftwareLiveApp('vault', currentDeviceMode)">🛡️ SecureVault</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"sdk"===n?"active":""}" onclick="openSoftwareLiveApp('sdk', currentDeviceMode)">🧩 Dev SDK</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"civicsync"===n?"active":""}" onclick="openSoftwareLiveApp('civicsync', currentDeviceMode)">🌐 CivicSync</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"healthbridge"===n?"active":""}" onclick="openSoftwareLiveApp('healthbridge', currentDeviceMode)">🏥 HealthBridge</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"omnibakery"===n?"active":""}" onclick="openSoftwareLiveApp('omnibakery', currentDeviceMode)">🥖 OmniBakery</button>\\n                    <button type="button" class="sr-app-subnav-btn ${"terminal"===n?"active":""}" onclick="openSoftwareLiveApp('terminal', currentDeviceMode)">⚙️ Terminal Agent</button>\\n'''

    if old_subnav in js:
        js = js.replace(old_subnav, new_subnav)
        print("Updated subnav buttons to all 9 platforms.")
    else:
        print("Subnav buttons already updated or pattern not found.")

    # 2. Add terminal rendering branch before sdk or after omnibakery
    # Look for "sdk"===n?
    terminal_block = '''"terminal"===n?t.innerHTML=c+`\\n            <div class="sr-app-grid-2">\\n                <div class="sr-app-card">\\n                    <h4 class="sr-app-card-title">\\n                        <span>⚙️ وكيل مراقبة السيرفرات السحابية (Cloud Terminal Agent)</span>\\n                        <span class="sr-app-header-ver" style="color:#10b981;">● متصل: ams-node-01</span>\\n                    </h4>\\n                    <p style="font-size:0.8rem;color:#94a3b8;margin-bottom:12px;">\\n                        مراقبة حية بنبضات الـ Heartbeat لميكروسيرفس المنظومة في عنقود أمستردام (AMS-IX) مع إمكانية إرسال أوامر تشخيصية سحابية.\\n                    </p>\\n                    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">\\n                        <button type="button" class="sr-app-btn secondary" style="font-size:0.75rem;padding:4px 10px;" onclick="runTerminalCmd('health')">⚡ curl /health</button>\\n                        <button type="button" class="sr-app-btn secondary" style="font-size:0.75rem;padding:4px 10px;" onclick="runTerminalCmd('docker')">🐳 docker ps</button>\\n                        <button type="button" class="sr-app-btn secondary" style="font-size:0.75rem;padding:4px 10px;" onclick="runTerminalCmd('metrics')">📊 vmstat -s</button>\\n                        <button type="button" class="sr-app-btn secondary" style="font-size:0.75rem;padding:4px 10px;" onclick="runTerminalCmd('restart')">🔄 restart gateway</button>\\n                        <button type="button" class="sr-app-btn secondary" style="font-size:0.75rem;padding:4px 10px;" onclick="clearTerminalOutput()">🧹 مسح الشاشة</button>\\n                    </div>\\n                    <div id="srTerminalScreen" style="background:#020604;border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:14px;font-family:monospace;font-size:0.78rem;color:#34d399;min-height:240px;max-height:280px;overflow-y:auto;line-height:1.6;direction:ltr;text-align:left;">\\n                        <div style="color:#64748b;">[S&R CoreSync Sovereign Cloud OS - Linux 6.6.12-sr-enterprise x86_64]</div>\\n                        <div style="color:#64748b;">Connected to amsterdam-ams01.sr-coresync.internal (Equinix AM3)</div>\\n                        <div style="color:#10b981;">Telemetry Heartbeat: ACTIVE (1,000ms sync interval)</div>\\n                        <div style="color:#d4af37;">Type or click a command above to inspect microservices...</div>\\n                        <div id="srTerminalDynamicOutput"></div>\\n                    </div>\\n                    <div style="display:flex;gap:8px;margin-top:10px;direction:ltr;">\\n                        <span style="color:#34d399;font-family:monospace;padding-top:8px;">sr-ops@ams:~$</span>\\n                        <input type="text" id="srTerminalInput" placeholder="e.g. status, ping, docker, help" style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);border-radius:8px;padding:8px 12px;color:#ffffff;font-family:monospace;font-size:0.82rem;" onkeydown="if(event.key==='Enter')runTerminalCmd(this.value)">\\n                        <button type="button" class="sr-app-btn primary" onclick="runTerminalCmd(document.getElementById('srTerminalInput').value)" style="padding:6px 14px;font-size:0.8rem;">Run ↵</button>\\n                    </div>\\n                </div>\\n                <div class="sr-app-card">\\n                    <h4 class="sr-app-card-title">\\n                        <span>لوحة المؤشرات والقياس اللحظي (Node Telemetry)</span>\\n                        <span class="sr-app-sync-status">AMS-IX Node</span>\\n                    </h4>\\n                    <div class="sr-app-calc-box">\\n                        <div class="sr-app-calc-row">\\n                            <span>حالة العنقود (Cluster Health):</span>\\n                            <strong style="color:#34d399;">100% سليم (Healthy)</strong>\\n                        </div>\\n                        <div class="sr-app-calc-row">\\n                            <span>زمن الاستجابة (Edge Latency):</span>\\n                            <strong style="color:#38bdf8;">1.8 ms (Amsterdam AMS-IX)</strong>\\n                        </div>\\n                        <div class="sr-app-calc-row">\\n                            <span>استهلاك المعالج (CPU Load):</span>\\n                            <strong id="termCpuDisp">18.4% (8 Cores Zen4)</strong>\\n                        </div>\\n                        <div class="sr-app-calc-row">\\n                            <span>استهلاك الذاكرة (RAM Usage):</span>\\n                            <strong id="termRamDisp">3.24 GB / 16.00 GB (20.2%)</strong>\\n                        </div>\\n                        <div class="sr-app-calc-row">\\n                            <span>الخدمات المصغرة النشطة:</span>\\n                            <strong style="color:#10b981;">14 / 14 Running</strong>\\n                        </div>\\n                        <div class="sr-app-calc-row total">\\n                            <span>ضمان الجاهزية (SLA Availability):</span>\\n                            <strong style="color:var(--sr-app-gold-bright);">99.98%</strong>\\n                        </div>\\n                    </div>\\n                    <div class="d-flex flex-col gap-2 mt-3">\\n                        <button type="button" class="sr-app-btn emerald full" onclick="exportTerminalTelemetryReport()">\\n                            <span>تصدير تقرير جاهزية الخوادم والـ SLA (PDF) 📄</span>\\n                        </button>\\n                        <button type="button" class="sr-app-btn secondary full" onclick="copyTerminalAgentKey()">\\n                            <span>نسخ مفتاح الـ Agent للربط السحابي (Copy API Key) 🔑</span>\\n                        </button>\\n                        <button type="button" class="sr-app-btn primary full" onclick="window.openExecutiveContactModal('systems', 'S&R Cloud Terminal - استشارة بنية تحتية')">\\n                            <span>طلب استشارة بنية تحتية مع م. سليم عزيزة 💬</span>\\n                        </button>\\n                    </div>\\n                </div>\\n            </div>`:'''

    if '"terminal"===n' not in js:
        target_sdk = '"sdk"===n?'
        if target_sdk in js:
            js = js.replace(target_sdk, terminal_block + target_sdk)
            print("Added terminal rendering branch to js/sr-software-apps.js.")
        else:
            print("Target sdk branch not found in js.")
    else:
        print("Terminal branch already present in js.")

    # 3. Add terminal helper functions to the IIFE
    terminal_helpers = '''
    window.runTerminalCmd = function(cmd) {
        cmd = (cmd || "").trim().toLowerCase();
        const out = document.getElementById("srTerminalDynamicOutput");
        const inp = document.getElementById("srTerminalInput");
        if (inp) inp.value = "";
        if (!out) return;

        let res = "";
        const now = new Date().toISOString().replace('T', ' ').substring(0, 19);

        if (cmd === "health" || cmd === "curl /health") {
            res = `<div style="color:#38bdf8;margin-top:6px;">$ curl -s http://127.0.0.1:8080/health | jq .</div>
<div style="color:#34d399;">{
  "status": "UP",
  "node": "ams-node-01.sr-coresync.internal",
  "datacenter": "Equinix AM3 Amsterdam",
  "timestamp": "${now}",
  "services": {
    "auth-gateway": "UP",
    "taxsync-engine": "UP",
    "cloudpos-relay": "UP",
    "vault-kms": "UP",
    "escrow-ledger": "UP"
  },
  "latency_ms": 1.82
}</div>`;
        } else if (cmd === "docker" || cmd === "docker ps") {
            res = `<div style="color:#38bdf8;margin-top:6px;">$ docker ps --format "table {{.Names}}\\\\t{{.Status}}\\\\t{{.Ports}}"</div>
<div style="color:#e2e8f0;">NAMES                    STATUS              PORTS
sr-auth-gateway-v2       Up 48 days (healthy)0.0.0.0:443->443/tcp
sr-taxsync-aangifte      Up 48 days (healthy)0.0.0.0:8081->8080/tcp
sr-cloudpos-broker       Up 48 days (healthy)0.0.0.0:8883->8883/tcp
sr-vault-aes256-kms      Up 48 days (healthy)0.0.0.0:9000->9000/tcp
sr-omnibakery-edge       Up 24 days (healthy)0.0.0.0:8088->8080/tcp</div>`;
        } else if (cmd === "metrics" || cmd === "vmstat" || cmd === "vmstat -s") {
            res = `<div style="color:#38bdf8;margin-top:6px;">$ vmstat -s && uptime</div>
<div style="color:#f3dfba;">      16384000 K total memory
       3398412 K used memory
      11298540 K free memory
       1687048 K buffer memory
 17:52:00 up 48 days, load average: 0.18, 0.22, 0.19</div>`;
        } else if (cmd === "restart" || cmd === "restart gateway") {
            res = `<div style="color:#fbbf24;margin-top:6px;">$ systemctl restart sr-auth-gateway</div>
<div style="color:#34d399;">[OK] Stopped S&R Sovereign Auth Gateway v2.4.
[OK] Starting S&R Sovereign Auth Gateway v2.4...
[OK] Re-bound to 0.0.0.0:443 (HTTP/3 QUIC enabled).
[OK] Health check passed in 42ms. Zero downtime rollover complete.</div>`;
        } else if (cmd === "status") {
            res = `<div style="color:#38bdf8;margin-top:6px;">$ sr-agent status</div>
<div style="color:#34d399;">S&R Cloud Terminal Agent v1.0.4 - RUNNING
Region: EU-West (Amsterdam AMS-IX)
Active Peer: Frankfurt FRA-IX (Hot Standby)
Agent ID: AGENT-SR-AMS01-2026-SOVEREIGN</div>`;
        } else if (cmd === "help") {
            res = `<div style="color:#f3dfba;margin-top:6px;">Available commands:</div>
<div style="color:#e2e8f0;">  health   - Run full cluster microservices health check
  docker   - List active Docker containers and ports
  metrics  - Display kernel memory and CPU load telemetry
  restart  - Test zero-downtime microservice rollover
  status   - Display agent licensing and peering status
  clear    - Clear terminal screen</div>`;
        } else {
            res = `<div style="color:#f87171;margin-top:6px;">bash: ${cmd}: command not found. Type 'help' for available commands.</div>`;
        }

        out.innerHTML += res;
        const screen = document.getElementById("srTerminalScreen");
        if (screen) screen.scrollTop = screen.scrollHeight;
        a(640, "sine", 0.08);
    };

    window.clearTerminalOutput = function() {
        const out = document.getElementById("srTerminalDynamicOutput");
        if (out) out.innerHTML = "";
        a(420, "triangle", 0.08);
    };

    window.copyTerminalAgentKey = function() {
        const key = "SRTRM-OPS-2026-T100-CLOUD-AMSTERDAM-LIVE";
        navigator.clipboard.writeText(key).then(() => {
            if (typeof showPortalToast === "function") {
                showPortalToast(`🔑 تم نسخ مفتاح الربط السحابي: ${key}`);
            } else {
                alert(`تم نسخ مفتاح الربط: ${key}`);
            }
        });
        a(780, "sine", 0.12);
    };

    window.exportTerminalTelemetryReport = function() {
        a(880, "sine", 0.15);
        if (typeof showPortalToast === "function") {
            showPortalToast("📊 جاري تصدير وثيقة القياس اللحظي وسجل جاهزية الـ SLA (99.98%)...");
        } else {
            alert("📊 تم تصدير تقرير جاهزية الخوادم والـ SLA بنجاح!");
        }
    };
'''

    if 'window.runTerminalCmd' not in js:
        # Insert before the closing `}()` of the IIFE
        idx = js.rfind('}()')
        if idx != -1:
            js = js[:idx] + terminal_helpers + '\n' + js[idx:]
            print("Added terminal helper functions into js/sr-software-apps.js.")
        else:
            print("Could not find closing IIFE tag in js.")
    else:
        print("Terminal helper functions already present in js.")

    with open(JS_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print("Saved js/sr-software-apps.js successfully.")

def sync_and_verify():
    print("\nStep 3: Extracting partials via build_site.py...")
    res = subprocess.run([sys.executable, 'scripts/build_site.py', '--extract'], cwd=ROOT, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("Error during build_site.py --extract:", res.stderr)
        sys.exit(1)

    chk = subprocess.run([sys.executable, 'scripts/build_site.py', '--check'], cwd=ROOT, capture_output=True, text=True)
    print(chk.stdout)
    if chk.returncode != 0:
        print("Error during build_site.py --check:", chk.stderr)
        sys.exit(1)

if __name__ == '__main__':
    update_index_card6()
    update_js_simulator()
    sync_and_verify()
    print("\nEnhancement complete!")
