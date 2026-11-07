/**
 * S&R CoreSync Sovereign Social Share Card Engine
 * Generates 1200x630 OpenGraph / Twitter Cards with luxury gold branding & instant social sharing
 * (c) 2026 S&R CoreSync For Intelligent Solutions — The Netherlands
 */

(function (global) {
  'use strict';

  let activeConfig = null;
  let cachedDataUrl = null;

  function createModalDOM() {
    if (document.getElementById('srSocialCardModal')) return;

    const modal = document.createElement('div');
    modal.id = 'srSocialCardModal';
    modal.className = 'sr-social-modal-overlay';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'توليد بطاقة المشاركة الاجتماعية');

    modal.innerHTML = `
      <div class="sr-social-modal-card">
        <div class="sr-social-modal-header">
          <div style="display:flex; align-items:center; gap:10px;">
            <img src="./assets/sr-core-emblem.svg" alt="S&R Emblem" width="28" height="28">
            <h3 style="font-size:1.1rem; color:var(--sr-gold-light, #f3dfba); font-weight:800; margin:0;">
              محرك توليد بطاقات المشاركة الاجتماعية الفاخرة (1200×630)
            </h3>
          </div>
          <button type="button" class="sr-social-close-btn" onclick="SRSocialCard.close()">✕</button>
        </div>

        <div class="sr-social-modal-body">
          <div class="sr-social-canvas-wrap">
            <canvas id="srSocialCanvas" width="1200" height="630"></canvas>
          </div>
          <div class="sr-social-actions">
            <button type="button" class="sr-social-btn sr-social-btn--gold" onclick="SRSocialCard.download()">
              📥 تحميل البطاقة عالية الدقة (PNG 1200×630)
            </button>
            <button type="button" class="sr-social-btn sr-social-btn--linkedin" onclick="SRSocialCard.shareLinkedIn()">
              💼 مشاركة مباشرة على LinkedIn
            </button>
            <button type="button" class="sr-social-btn sr-social-btn--x" onclick="SRSocialCard.shareX()">
              🐦 مشاركة مباشرة على X (تويتر)
            </button>
            <button type="button" class="sr-social-btn sr-social-btn--outline" onclick="SRSocialCard.copyLink()">
              📋 نسخ الرابط الذكي
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Inject styles
    if (!document.getElementById('srSocialCardStyles')) {
      const style = document.createElement('style');
      style.id = 'srSocialCardStyles';
      style.textContent = `
        .sr-social-modal-overlay {
          position: fixed;
          top: 0; left: 0; width: 100%; height: 100%;
          background: rgba(3, 8, 6, 0.85);
          backdrop-filter: blur(12px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10050;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.25s ease;
          padding: 20px;
          direction: rtl;
        }
        .sr-social-modal-overlay.active {
          opacity: 1;
          pointer-events: auto;
        }
        .sr-social-modal-card {
          background: linear-gradient(135deg, rgba(8, 22, 16, 0.98), rgba(4, 10, 8, 0.98));
          border: 1px solid rgba(197, 168, 128, 0.35);
          border-radius: 18px;
          width: 100%;
          max-width: 920px;
          box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(197, 168, 128, 0.15);
          overflow: hidden;
          transform: translateY(20px);
          transition: transform 0.25s ease;
        }
        .sr-social-modal-overlay.active .sr-social-modal-card {
          transform: translateY(0);
        }
        .sr-social-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 24px;
          border-bottom: 1px solid rgba(197, 168, 128, 0.2);
          background: rgba(13, 34, 26, 0.6);
        }
        .sr-social-close-btn {
          background: none; border: none; color: #94a3b8;
          font-size: 1.3rem; cursor: pointer; padding: 4px 8px;
          border-radius: 6px; transition: all 0.2s;
        }
        .sr-social-close-btn:hover {
          color: #f8fafc; background: rgba(239, 68, 68, 0.2);
        }
        .sr-social-modal-body {
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .sr-social-canvas-wrap {
          width: 100%;
          background: #020504;
          border: 1px solid rgba(197, 168, 128, 0.25);
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .sr-social-canvas-wrap canvas {
          width: 100%;
          height: auto;
          display: block;
        }
        .sr-social-actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 12px;
        }
        .sr-social-btn {
          padding: 12px 18px;
          border-radius: 8px;
          font-family: inherit;
          font-size: 0.88rem;
          font-weight: 700;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: all 0.2s;
          border: none;
        }
        .sr-social-btn--gold {
          background: linear-gradient(135deg, #c5a880, #8c734b);
          color: #030806;
          box-shadow: 0 4px 15px rgba(197, 168, 128, 0.3);
        }
        .sr-social-btn--gold:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 22px rgba(197, 168, 128, 0.45);
        }
        .sr-social-btn--linkedin {
          background: #0a66c2; color: #fff;
        }
        .sr-social-btn--linkedin:hover {
          background: #004182; transform: translateY(-2px);
        }
        .sr-social-btn--x {
          background: #000; color: #fff; border: 1px solid #334155;
        }
        .sr-social-btn--x:hover {
          background: #1e293b; transform: translateY(-2px);
        }
        .sr-social-btn--outline {
          background: rgba(197, 168, 128, 0.1);
          color: #f3dfba;
          border: 1px solid rgba(197, 168, 128, 0.3);
        }
        .sr-social-btn--outline:hover {
          background: rgba(197, 168, 128, 0.2);
        }
      `;
      document.head.appendChild(style);
    }
  }

  function renderCard(config) {
    const canvas = document.getElementById('srSocialCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = 1200;
    const h = 630;

    // 1. Background Luxury Gradient
    const bgGrad = ctx.createRadialGradient(w / 2, 80, 50, w / 2, h / 2, 700);
    bgGrad.addColorStop(0, '#0d281e');
    bgGrad.addColorStop(0.5, '#05120c');
    bgGrad.addColorStop(1, '#020604');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // 2. Ornate Golden Borders & Corner Accents
    ctx.strokeStyle = 'rgba(197, 168, 128, 0.35)';
    ctx.lineWidth = 3;
    ctx.strokeRect(30, 30, w - 60, h - 60);

    ctx.strokeStyle = '#c5a880';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(38, 38, w - 76, h - 76);

    // Corner decorative brackets
    const cSize = 25;
    ctx.fillStyle = '#c5a880';
    // Top-left
    ctx.fillRect(26, 26, cSize, 5); ctx.fillRect(26, 26, 5, cSize);
    // Top-right
    ctx.fillRect(w - 26 - cSize, 26, cSize, 5); ctx.fillRect(w - 31, 26, 5, cSize);
    // Bottom-left
    ctx.fillRect(26, h - 31, cSize, 5); ctx.fillRect(26, h - 26 - cSize, 5, cSize);
    // Bottom-right
    ctx.fillRect(w - 26 - cSize, h - 31, cSize, 5); ctx.fillRect(w - 31, h - 26 - cSize, 5, cSize);

    // 3. Top Header Branding
    ctx.fillStyle = '#c5a880';
    ctx.font = 'bold 24px "Alexandria", sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('S&R CoreSync For Intelligent Solutions', w - 80, 85);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 16px "Alexandria", sans-serif';
    ctx.fillText('Den Haag / Rijswijk • The Netherlands • Sovereign Architecture', w - 80, 115);

    // Category / Badge
    const category = config.badge || 'استوديو الابتكار الرقمي';
    ctx.fillStyle = 'rgba(197, 168, 128, 0.15)';
    ctx.beginPath();
    ctx.roundRect(80, 65, 260, 42, 8);
    ctx.fill();
    ctx.strokeStyle = 'rgba(197, 168, 128, 0.4)';
    ctx.stroke();

    ctx.fillStyle = '#f3dfba';
    ctx.font = '700 16px "Alexandria", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(category, 80 + 130, 92);

    // 4. Main Title
    ctx.fillStyle = '#ffffff';
    ctx.font = '900 48px "Alexandria", sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(config.title || 'منظومة الحلول الذكية والأنظمة السحابية', w - 80, 210);

    // Subtitle / Description
    ctx.fillStyle = '#cbd5e1';
    ctx.font = '500 22px "Alexandria", sans-serif';
    ctx.fillText(config.subtitle || 'تقنيات سحابية فائقة الأداء مدعومة بالذكاء الاصطناعي وبنية Edge CDN', w - 80, 260);

    // 5. Featured Metric Cards (3 Cards)
    const cardY = 320;
    const cardW = 320;
    const cardH = 170;
    const cardGap = 40;
    const startX = w - 80 - cardW;

    const metrics = config.metrics || [
      { label: 'تقييم الأداء العام', val: '98 / 100', sub: 'امتياز هندسي معتمد ✓', color: '#10b981' },
      { label: 'زمن أول بايت TTFB', val: '0.15s', sub: 'Edge CDN فائق السرعة', color: '#38bdf8' },
      { label: 'التوفير السنوي التقديري', val: '€ 14,800', sub: 'عائد استثماري ROI فوري', color: '#c5a880' }
    ];

    metrics.forEach((m, i) => {
      const curX = startX - (i * (cardW + cardGap));

      // Card BG
      ctx.fillStyle = 'rgba(8, 24, 18, 0.75)';
      ctx.beginPath();
      ctx.roundRect(curX, cardY, cardW, cardH, 12);
      ctx.fill();
      ctx.strokeStyle = 'rgba(197, 168, 128, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '600 15px "Alexandria", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(m.label, curX + cardW - 20, cardY + 40);

      // Value
      ctx.fillStyle = m.color || '#f3dfba';
      ctx.font = '900 38px "Space Grotesk", "Alexandria", sans-serif';
      ctx.fillText(m.val, curX + cardW - 20, cardY + 95);

      // Sub
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '500 14px "Alexandria", sans-serif';
      ctx.fillText(m.sub, curX + cardW - 20, cardY + 135);
    });

    // 6. Bottom Verification Ribbon
    ctx.fillStyle = '#c5a880';
    ctx.font = '700 16px "Alexandria", sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('✓ موثق ومعتمد رسمياً وفق المعايير الأوروبية GDPR • S&R CoreSync Platform', w - 80, 565);

    ctx.fillStyle = '#38bdf8';
    ctx.font = '700 16px "Space Grotesk", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('https://sr-coresync.com', 80, 565);

    cachedDataUrl = canvas.toDataURL('image/png');
  }

  const SRSocialCard = {
    open(config = {}) {
      createModalDOM();
      activeConfig = Object.assign({
        title: 'استوديو الابتكار والحلول الذكية',
        subtitle: 'منظومة سحابية متقدمة من S&R CoreSync For Intelligent Solutions',
        badge: 'مشاركة الإنجاز 🏆',
        url: window.location.href,
        metrics: null
      }, config);

      renderCard(activeConfig);
      const modal = document.getElementById('srSocialCardModal');
      if (modal) modal.classList.add('active');
    },

    close() {
      const modal = document.getElementById('srSocialCardModal');
      if (modal) modal.classList.remove('active');
    },

    download() {
      if (!cachedDataUrl) return;
      const a = document.createElement('a');
      a.download = `SR-CoreSync-Social-Card-${Date.now()}.png`;
      a.href = cachedDataUrl;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      if (typeof showStudioToast === 'function') {
        showStudioToast('✓ تم تحميل بطاقة المشاركة الاجتماعية (1200×630) بنجاح!');
      }
    },

    shareLinkedIn() {
      const url = encodeURIComponent((activeConfig && activeConfig.url) || window.location.href);
      const text = encodeURIComponent(`${(activeConfig && activeConfig.title) || 'حلول رقمية مبتكرة'} من S&R CoreSync For Intelligent Solutions في هولندا.`);
      window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
    },

    shareX() {
      const url = encodeURIComponent((activeConfig && activeConfig.url) || window.location.href);
      const text = encodeURIComponent(`🚀 ${(activeConfig && activeConfig.title) || 'استوديو رقمي فاخر'} من @SR_CoreSync:\n${url}`);
      window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
    },

    copyLink() {
      const url = (activeConfig && activeConfig.url) || window.location.href;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
          if (typeof showStudioToast === 'function') {
            showStudioToast('✓ تم نسخ الرابط الذكي للحافظة!');
          } else {
            alert('✓ تم نسخ الرابط الذكي بنجاح!');
          }
        });
      }
    }
  };

  global.SRSocialCard = SRSocialCard;
})(typeof window !== 'undefined' ? window : this);
