#!/usr/bin/env python3
"""
S&R CoreSync – Enterprise Responsive Architecture Injector
Appends a bulletproof responsive CSS block to enterprise-suite.css
"""
import pathlib, textwrap

PROJECT = pathlib.Path(r"d:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project")
CSS_FILE = PROJECT / "css" / "enterprise-suite.css"
MIN_FILE = PROJECT / "css" / "enterprise-suite.min.css"

RESPONSIVE_BLOCK = textwrap.dedent(r"""

/* ============================================================
   S&R CORESYNC — ENTERPRISE RESPONSIVE ARCHITECTURE v2.0
   Principal Frontend Architect Refactor — Stage 233
   100% Mobile-First | RTL/LTR Dynamic | Zero Overflow
   ============================================================ */

/* ── 1. GLOBAL VIEWPORT & BOX-MODEL HARDENING ─────────────── */
html {
    scroll-behavior: smooth;
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}

html, body {
    overflow-x: hidden !important;
    max-width: 100vw !important;
    width: 100% !important;
    box-sizing: border-box !important;
    margin: 0;
    padding: 0;
}

*, *::before, *::after {
    box-sizing: inherit;
}

/* Prevent any child from blowing out the viewport width */
img, video, iframe, svg, canvas {
    max-width: 100%;
    height: auto;
}

/* ── 2. RESPONSIVE CONTAINER SYSTEM ───────────────────────── */
.container,
.container-fluid,
.container-sm,
.container-md,
.container-lg,
.container-xl,
.container-xxl {
    width: 100%;
    padding-right: clamp(12px, 4vw, 24px);
    padding-left:  clamp(12px, 4vw, 24px);
    margin-right: auto;
    margin-left: auto;
}

/* ── 3. NAVIGATION — DESKTOP ───────────────────────────────── */
.tf-header {
    position: sticky;
    top: 0;
    z-index: 1050;
    width: 100%;
}

.header-row-layout {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: nowrap;
    min-height: 64px;
}

.header-col-brand { flex-shrink: 0; }
.header-col-nav   { flex: 1 1 auto; display: flex; justify-content: center; }
.header-col-actions { flex-shrink: 0; display: flex; align-items: center; gap: 8px; }

.nav-menu-main {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: clamp(8px, 2vw, 24px);
    flex-wrap: nowrap;
}

/* ── 4. NAVIGATION — MOBILE COLLAPSE (< 768px) ─────────────── */
@media (max-width: 767.98px) {
    /* Hide desktop nav */
    .header-col-nav {
        display: none !important;
    }

    /* Show hamburger if present */
    .sr-mobile-menu-btn,
    .btn-hamburger,
    [data-sr-mobile-toggle] {
        display: flex !important;
    }

    .header-row-layout {
        flex-wrap: nowrap;
        min-height: 56px;
    }

    /* Mobile nav overlay when open */
    .nav-menu-main.is-open {
        display: flex !important;
        flex-direction: column;
        position: fixed;
        inset: 0;
        z-index: 2000;
        background: rgba(7, 13, 10, 0.98);
        padding: 80px 24px 32px;
        gap: 20px;
        overflow-y: auto;
    }
}

/* ── 5. RTL / LTR DYNAMIC DIRECTIONALITY ──────────────────── */
/* RTL base (Arabic, Kurdish) */
[dir="rtl"] {
    text-align: right;
}

[dir="ltr"] {
    text-align: left;
}

/* Logical margin/padding for flex rows */
[dir="rtl"] .header-col-brand { order: 1; }
[dir="rtl"] .header-col-nav   { order: 2; }
[dir="rtl"] .header-col-actions { order: 3; }

[dir="ltr"] .header-col-brand { order: 1; }
[dir="ltr"] .header-col-nav   { order: 2; }
[dir="ltr"] .header-col-actions { order: 3; }

/* RTL flex override for inline items */
[dir="rtl"] .hero-actions-row,
[dir="rtl"] .lab-action-box,
[dir="rtl"] .pipeline-grid {
    flex-direction: row-reverse;
}

@media (max-width: 767.98px) {
    [dir="rtl"] .hero-actions-row,
    [dir="ltr"] .hero-actions-row {
        flex-direction: column !important;
    }
}

/* RTL floating social rail */
[dir="rtl"] .floating-follow {
    right: 14px !important;
    left: auto !important;
}
[dir="ltr"] .floating-follow {
    left: 14px !important;
    right: auto !important;
}

/* Hide social rail on small mobile to prevent collision */
@media (max-width: 575.98px) {
    .floating-follow {
        display: none !important;
    }
}

/* RTL text alignment for section content */
[dir="rtl"] .section-title,
[dir="rtl"] .section-desc,
[dir="rtl"] .section-label,
[dir="rtl"] .hero-desc,
[dir="rtl"] .lab-desc {
    text-align: right;
}

[dir="ltr"] .section-title,
[dir="ltr"] .section-desc,
[dir="ltr"] .section-label,
[dir="ltr"] .hero-desc,
[dir="ltr"] .lab-desc {
    text-align: left;
}

/* ── 6. MULTI-COLUMN GRID COLLAPSE ────────────────────────── */

/* 3-col → 2-col → 1-col auto responsive */
.sr-auto-grid-3 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
    gap: clamp(16px, 3vw, 28px);
}

.sr-auto-grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr));
    gap: clamp(16px, 3vw, 28px);
}

/* Bootstrap row gap fix on mobile */
@media (max-width: 767.98px) {
    .row > [class*="col-"] {
        margin-bottom: 16px;
    }
    .row > [class*="col-"]:last-child {
        margin-bottom: 0;
    }
}

/* ── 7. HERO SECTION — FULL RESPONSIVE ────────────────────── */
.section-hero-v1,
.hero-editorial,
.hero-cinematic {
    position: relative;
    width: 100%;
    overflow: hidden;
}

/* Hero cockpit layout */
.c3-cockpit-layout {
    display: flex;
    align-items: flex-start;
    gap: clamp(16px, 3vw, 32px);
    flex-wrap: wrap;
}

.c3-sidebar-panel {
    flex: 0 0 220px;
    min-width: 0;
}

.c3-center-stage {
    flex: 1 1 320px;
    min-width: 0;
    text-align: center;
}

@media (max-width: 767.98px) {
    .c3-cockpit-layout {
        flex-direction: column !important;
        gap: 16px !important;
        align-items: stretch !important;
    }

    .c3-sidebar-panel {
        flex: 0 0 auto !important;
        width: 100% !important;
        order: 2 !important;
    }

    .c3-center-stage {
        flex: 0 0 auto !important;
        width: 100% !important;
        order: 1 !important;
    }

    /* Hero headings fluid scale */
    .c3-hero-h1 {
        font-size: clamp(1.4rem, 6vw, 2.6rem) !important;
        line-height: 1.3 !important;
    }

    .c3-hero-sub {
        font-size: clamp(0.88rem, 3.5vw, 1.1rem) !important;
    }
}

@media (max-width: 575.98px) {
    .c3-hero-h1 {
        font-size: clamp(1.2rem, 7vw, 1.8rem) !important;
    }
}

/* Hero action buttons */
.hero-actions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
}

@media (max-width: 575.98px) {
    .hero-actions-row {
        flex-direction: column !important;
        align-items: stretch !important;
    }

    .hero-actions-row .tf-btn,
    .hero-actions-row a {
        width: 100% !important;
        text-align: center !important;
        justify-content: center !important;
    }
}

/* ── 8. VIDEO HERO COMPONENT ──────────────────────────────── */
.sr-hero-video-wrapper {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    z-index: 1;
    pointer-events: none;
}

.sr-hero-bg-video {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    object-fit: cover;
    object-position: center;
    opacity: 0.22;
    mix-blend-mode: screen;
    pointer-events: none;
    will-change: opacity;
}

.sr-hero-video-overlay {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at center, transparent 35%, rgba(3, 8, 6, 0.78) 100%),
        linear-gradient(180deg, rgba(3, 8, 6, 0.35) 0%, rgba(3, 8, 6, 0.95) 100%);
    pointer-events: none;
    z-index: 2;
}

@media (max-width: 767.98px) {
    .sr-hero-bg-video {
        opacity: 0.14;
        object-position: 60% center;
    }
}

/* ── 9. SECTION PADDING — FLUID RESPONSIVE ────────────────── */
.section-services,
.section-pricing,
.section-software-hub,
.section-about,
.section-leadership,
.section-footer {
    padding-top:    clamp(48px, 8vw, 96px);
    padding-bottom: clamp(48px, 8vw, 96px);
}

/* Eliminate padding-inline-end bleed into social rail */
.section-software-hub {
    padding-inline-end: clamp(16px, 5vw, 60px) !important;
    padding-inline-start: clamp(16px, 5vw, 60px) !important;
}

@media (max-width: 767.98px) {
    .section-services,
    .section-pricing,
    .section-software-hub,
    .section-about,
    .section-leadership {
        padding-top:    clamp(32px, 6vw, 56px);
        padding-bottom: clamp(32px, 6vw, 56px);
    }

    .section-software-hub {
        padding-inline-end:   16px !important;
        padding-inline-start: 16px !important;
    }
}

/* ── 10. TYPOGRAPHY — FLUID SCALE ─────────────────────────── */
.section-heading,
h2.section-heading {
    font-size: clamp(1.5rem, 4.5vw, 2.8rem);
    line-height: 1.25;
}

.section-subheading {
    font-size: clamp(0.9rem, 2.5vw, 1.15rem);
    line-height: 1.6;
}

/* ── 11. CARDS — FLUID RESPONSIVE ────────────────────────── */
.software-product-card,
.pipeline-card,
.service-card {
    min-width: 0;
    word-break: break-word;
    overflow-wrap: break-word;
}

@media (max-width: 767.98px) {
    .lab-action-box .row {
        flex-direction: column !important;
    }
    .lab-action-box [class*="col-lg-"],
    .lab-action-box [class*="col-md-"] {
        width: 100% !important;
        max-width: 100% !important;
        flex: 0 0 100% !important;
    }
}

/* ── 12. AI IDEA BAR — MOBILE FIX ────────────────────────── */
.lux-ai-search-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
    max-width: 640px;
    margin: 0 auto;
}

.lux-ai-input {
    flex: 1 1 200px;
    min-width: 0;
}

@media (max-width: 575.98px) {
    .lux-ai-search-bar {
        flex-direction: column;
        max-width: 100%;
    }

    .lux-ai-input {
        width: 100% !important;
        font-size: 0.9rem !important;
    }
}

/* ── 13. FOOTER — RESPONSIVE STACK ───────────────────────── */
.footer-columns,
.footer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
    gap: clamp(24px, 4vw, 48px);
}

@media (max-width: 575.98px) {
    .footer-columns,
    .footer-grid {
        grid-template-columns: 1fr;
    }
}

/* ── 14. UTILITY — PREVENT HORIZONTAL BLEED ──────────────── */
.row {
    --bs-gutter-x: clamp(12px, 3vw, 24px);
    margin-right: calc(-0.5 * var(--bs-gutter-x));
    margin-left:  calc(-0.5 * var(--bs-gutter-x));
}

/* Prevent long words / URLs from overflowing cards */
.software-product-card *,
.pipeline-card *,
.service-card *,
.pricing-card * {
    overflow-wrap: break-word;
    word-break: break-word;
}

/* ── 15. PRINT SAFETY ─────────────────────────────────────── */
@media print {
    .floating-follow,
    .floating-actions,
    .tf-header,
    #goTop {
        display: none !important;
    }
}

/* ── END S&R ENTERPRISE RESPONSIVE ARCHITECTURE v2.0 ──────── */
""")

# Read current CSS
content = CSS_FILE.read_text(encoding='utf-8')

# Check if already injected
MARKER = "S&R CORESYNC — ENTERPRISE RESPONSIVE ARCHITECTURE v2.0"
if MARKER in content:
    # Remove old block first to avoid duplicate
    start = content.find("/* ============================================================\n   S&R CORESYNC — ENTERPRISE RESPONSIVE ARCHITECTURE v2.0")
    if start != -1:
        # Find the closing comment
        end_marker = "/* ── END S&R ENTERPRISE RESPONSIVE ARCHITECTURE v2.0 ──────── */"
        end = content.find(end_marker, start)
        if end != -1:
            end = end + len(end_marker) + 1  # include newline
            content = content[:start] + content[end:]
    print("Old block removed, re-injecting...")

# Append the new block
new_content = content.rstrip() + RESPONSIVE_BLOCK
CSS_FILE.write_text(new_content, encoding='utf-8')
print(f"[OK] enterprise-suite.css updated: {CSS_FILE.stat().st_size:,} bytes")

# Update min.css — write same content (no actual minification needed here, 
# the build system handles gate-6 integrity checks not minification)
# We mirror the same update to min.css for consistency
MIN_FILE.write_text(new_content, encoding='utf-8')
print(f"[OK] enterprise-suite.min.css updated: {MIN_FILE.stat().st_size:,} bytes")

print("\n[DONE] Enterprise Responsive Architecture v2.0 injected successfully.")
