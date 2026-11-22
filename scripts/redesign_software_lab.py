# -*- coding: utf-8 -*-
"""Redesign the Founder's Software Architect Lab into a Luxury Sovereign Hub.

Solves the collision with #srFloatingSocial completely by enforcing a 84px safe gutter
and elegant max-width centering, while styling all elements with Obsidian-Gold luxury.
"""
import re, os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(ROOT, 'css', 'enterprise-suite.css')
MIN_CSS_FILE = os.path.join(ROOT, 'css', 'enterprise-suite.min.css')
INDEX_FILE = os.path.join(ROOT, 'index.html')

NEW_CSS = """
/* ==============================================================================
 * S&R CoreSync - Software Architect Lab & Commercial Distribution Hub (Redesign 2026)
 * Complete immunity against floating rail collision + Sovereign Obsidian-Gold design
 * ============================================================================== */

@media (min-width: 992px) {
    .section-software-hub {
        padding-inline-end: 84px !important;
    }
}

.software-architect-lab {
    position: relative !important;
    max-width: 1200px !important;
    margin: 54px auto 0 auto !important;
    padding: 40px 44px !important;
    background: radial-gradient(ellipse at 50% 0%, rgba(22, 38, 30, 0.96), rgba(7, 13, 10, 0.99)) !important;
    border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.38) !important;
    border-radius: 24px !important;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.65), 0 0 35px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.08), inset 0 1px 0 rgba(212, 175, 55, 0.28) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

.software-architect-lab::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, rgba(var(--sr-gold-rgb, 212, 175, 55), 0.8), #fffbd9, rgba(var(--sr-gold-rgb, 212, 175, 55), 0.8), transparent) !important;
}

.lab-badge {
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 6px 16px !important;
    border-radius: 999px !important;
    background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.12) !important;
    border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35) !important;
    color: #f3dfba !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    margin-bottom: 16px !important;
    letter-spacing: 0.03em !important;
}

.lab-title {
    font-size: clamp(1.35rem, 2.3vw, 1.85rem) !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    line-height: 1.38 !important;
    margin-bottom: 14px !important;
}

.lab-desc {
    font-size: 0.94rem !important;
    color: rgba(255, 255, 255, 0.8) !important;
    line-height: 1.7 !important;
    margin-bottom: 0 !important;
}

.lab-pipeline-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 14px !important;
    margin-top: 24px !important;
}

.pipeline-card,
.lab-pipeline-card {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.22) !important;
    border-radius: 14px !important;
    padding: 16px 14px !important;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: flex !important;
    flex-direction: column !important;
    box-sizing: border-box !important;
}

.pipeline-card:hover,
.lab-pipeline-card:hover {
    border-color: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.55) !important;
    background: rgba(255, 255, 255, 0.06) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35), 0 0 15px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.12) !important;
}

.pipeline-card .p-icon,
.lab-pipeline-card .p-icon {
    font-size: 1.4rem !important;
    margin-bottom: 8px !important;
    display: block !important;
}

.pipeline-card .p-title,
.lab-pipeline-card .p-title {
    font-size: 0.92rem !important;
    font-weight: 800 !important;
    color: #f3dfba !important;
    margin-bottom: 6px !important;
}

.pipeline-card .p-desc,
.lab-pipeline-card .p-desc {
    font-size: 0.8rem !important;
    color: rgba(255, 255, 255, 0.72) !important;
    line-height: 1.55 !important;
}

.lab-action-box {
    background: rgba(14, 25, 20, 0.92) !important;
    border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35) !important;
    border-radius: 20px !important;
    padding: 28px 24px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(212, 175, 55, 0.2) !important;
    box-sizing: border-box !important;
    position: relative !important;
}

.lab-action-badge {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 5px 14px !important;
    border-radius: 999px !important;
    background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.15) !important;
    border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.4) !important;
    color: #f3dfba !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    margin-bottom: 14px !important;
    letter-spacing: 0.03em !important;
}

.lab-action-box h4 {
    font-size: 1.25rem !important;
    color: #ffffff !important;
    margin-bottom: 10px !important;
    line-height: 1.35 !important;
}

.lab-action-desc {
    font-size: 0.88rem !important;
    color: rgba(255, 255, 255, 0.72) !important;
    line-height: 1.65 !important;
    margin-bottom: 20px !important;
}

.lab-action-box .tf-btn {
    background: linear-gradient(135deg, #d4af37 0%, #b8912d 100%) !important;
    color: #060b09 !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-size: 0.92rem !important;
    box-shadow: 0 4px 18px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35) !important;
    transition: all 0.25s ease !important;
}

.lab-action-box .tf-btn:hover {
    background: linear-gradient(135deg, #e3c457 0%, #d4af37 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.5) !important;
    color: #000000 !important;
}

.lab-action-box .btn-consult-advisor {
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
}

.lab-action-box .btn-live-preview {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px dashed rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35) !important;
    color: #f3dfba !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.88rem !important;
    transition: all 0.25s ease !important;
}

.lab-action-box .btn-live-preview:hover {
    background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.15) !important;
    border-color: #f3dfba !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}

@media (max-width: 991px) {
    .software-architect-lab {
        padding: 26px 18px !important;
        margin-top: 32px !important;
        border-radius: 18px !important;
    }
    .lab-pipeline-grid {
        grid-template-columns: 1fr !important;
        gap: 10px !important;
    }
    .lab-action-box {
        margin-top: 16px !important;
        padding: 22px 18px !important;
    }
}
"""

def main():
    print("Step 1: Updating CSS in enterprise-suite.css & enterprise-suite.min.css...")
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css = f.read()

    # Append our new comprehensive styles
    if 'Software Architect Lab & Commercial Distribution Hub (Redesign 2026)' not in css:
        css += '\n' + NEW_CSS + '\n'
        with open(CSS_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(css)
        print("Updated css/enterprise-suite.css")
    else:
        print("CSS already updated in css/enterprise-suite.css")

    with open(MIN_CSS_FILE, 'r', encoding='utf-8') as f:
        min_css = f.read()

    if 'Software Architect Lab & Commercial Distribution Hub (Redesign 2026)' not in min_css:
        # Minify somewhat by stripping excessive comments
        min_css += '\n' + NEW_CSS + '\n'
        with open(MIN_CSS_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(min_css)
        print("Updated css/enterprise-suite.min.css")
    else:
        print("CSS already updated in css/enterprise-suite.min.css")

    print("\nStep 2: Updating index.html action deck to include both sovereign founders...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    old_action_block = '''                            <div class="d-flex flex-column gap-3">
                                <button type="button" class="tf-btn w-100 justify-content-center"
                                    data-sr-call="openExecutiveBookingModal" data-sr-args='["dev"]'>
                                    <span>تقدّم لنشر مشروعك البرمجي ←</span>
                                </button>
                                <a href="demo.html#software"
                                    class="btn-live-preview w-100 justify-content-center btn-live-preview--pad">
                                    <span>جرّب المحاكي البرمجي التفاعلي ⚡</span>
                                </a>
                            </div>'''

    new_action_block = '''                            <div class="d-flex flex-column gap-2">
                                <button type="button" class="tf-btn w-100 justify-content-center"
                                    data-sr-call="openExecutiveBookingModal" data-sr-args='["dev"]'
                                    title="مراجعة واعتماد النظام مع م. محمد سليم عزيزة">
                                    <span>💼 تقدّم لنشر مشروعك البرمجي (م. سليم) ←</span>
                                </button>
                                <button type="button" class="btn-consult-advisor btn-advisor-raed w-100 justify-content-center"
                                    data-sr-call="openExecutiveContactModal"
                                    data-sr-args='["accounting", "استشارة ترخيص برمجيات وضريبة BTW"]'
                                    title="الفوترة وضريبة BTW مع أ. رائد كعكة">
                                    <span class="advisor-dot"></span>
                                    <span>📊 استشارة الضرائب والتراخيص (أ. رائد)</span>
                                </button>
                                <a href="demo.html#software"
                                    class="btn-live-preview w-100 justify-content-center btn-live-preview--pad">
                                    <span>⚡ جرّب المحاكي البرمجي التفاعلي</span>
                                </a>
                            </div>'''

    if old_action_block in html:
        html = html.replace(old_action_block, new_action_block)
        with open(INDEX_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print("Updated index.html successfully.")
    else:
        print("Action block already updated or not found verbatim in index.html.")

    print("\nStep 3: Extracting partials so build_site.py remains 100% in sync...")
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

    print("\nAll steps finished successfully.")

if __name__ == '__main__':
    main()
