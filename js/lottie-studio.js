/**
 * S&R CoreSync Sovereign Lottie & Micro-Interactions Studio
 * (c) 2026 S&R CoreSync For Intelligent Solutions — The Netherlands
 */

let lottieInstance = null;
let currentAnimationData = null;

function downloadFile(filename, content, mime = 'application/json') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function showStudioToast(msg) {
  let toast = document.getElementById('studioToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'studioToast';
    toast.className = 'studio-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2600);
}

function loadLottieAnimation(animData) {
  const previewDiv = document.getElementById('lottiePreview');
  if (!previewDiv || typeof window.lottie === 'undefined') return;

  if (lottieInstance) lottieInstance.destroy();

  currentAnimationData = animData || (window.lottie.presets && window.lottie.presets.checkmark);

  lottieInstance = window.lottie.loadAnimation({
    container: previewDiv,
    renderer: 'svg',
    loop: true,
    autoplay: true,
    animationData: currentAnimationData,
  });

  const speedRange = document.getElementById('speedRange');
  if (speedRange && lottieInstance) {
    lottieInstance.setSpeed(parseFloat(speedRange.value) || 1);
  }
}

function openLottieSocialCard() {
  if (typeof SRSocialCard === 'undefined') return;
  const speedRange = document.getElementById('speedRange');
  const speed = (speedRange && speedRange.value) || '1';
  const presetSelect = document.getElementById('presetSelect');
  const presetName = (presetSelect && presetSelect.options[presetSelect.selectedIndex].text) || 'علامة الإنجاز السيادية';

  SRSocialCard.open({
    title: 'استوديو الرسوم المتحركة والتفاعلات الدقيقة Lottie',
    subtitle: `تصميم وتوليد عناصر بصرية تفاعلية بنقرة واحدة (${presetName})`,
    badge: 'أنيميشن Lottie ✨',
    url: window.location.href,
    metrics: [
      { label: 'معدل السرعة وسلاسة الحركة', val: `${speed}x`, sub: '60 FPS Full Vector Animation', color: '#10b981' },
      { label: 'توليد كود CSS Keyframes', val: '100% Pure', sub: 'بدون مكتبات خارجية', color: '#38bdf8' },
      { label: 'دقة الرسم والإخراج', val: '8K Vector', sub: 'متطابق مع كافة الشاشات', color: '#c5a880' }
    ]
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('lottieFile');
  const speedRange = document.getElementById('speedRange');
  const speedVal = document.getElementById('speedVal');
  const colorPicker = document.getElementById('colorPicker');
  const previewDiv = document.getElementById('lottiePreview');
  const exportJsonBtn = document.getElementById('exportJsonBtn');
  const exportCssBtn = document.getElementById('exportCssBtn');
  const presetSelect = document.getElementById('presetSelect');
  const btnPlay = document.getElementById('btnPlay');
  const btnPause = document.getElementById('btnPause');
  const btnStop = document.getElementById('btnStop');

  // Load default preset
  if (window.lottie && window.lottie.presets) {
    loadLottieAnimation(window.lottie.presets.checkmark);
  }

  // Preset selector
  if (presetSelect) {
    presetSelect.addEventListener('change', () => {
      const key = presetSelect.value;
      if (window.lottie && window.lottie.presets && window.lottie.presets[key]) {
        loadLottieAnimation(window.lottie.presets[key]);
        showStudioToast(`✓ تم تحميل نموذج: ${window.lottie.presets[key].name || key}`);
      }
    });
  }

  // Load animation from local file (JSON)
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          const parsed = JSON.parse(ev.target.result);
          loadLottieAnimation(parsed);
          showStudioToast(`✓ تم استيراد ملف Lottie: ${file.name}`);
        } catch (err) {
          alert('ملف Lottie غير صالح، يرجى التأكد من هيكل الـ JSON');
          console.error(err);
        }
      };
      reader.readAsText(file);
    });
  }

  // Speed control
  if (speedRange) {
    speedRange.addEventListener('input', () => {
      const speed = parseFloat(speedRange.value);
      if (speedVal) speedVal.textContent = `${speed}x`;
      if (lottieInstance) lottieInstance.setSpeed(speed);
    });
  }

  // Color control
  if (colorPicker && previewDiv) {
    colorPicker.addEventListener('input', () => {
      const color = colorPicker.value;
      previewDiv.style.setProperty('--lottie-color', color);
    });
  }

  // Playback buttons
  if (btnPlay) {
    btnPlay.addEventListener('click', () => {
      if (lottieInstance) lottieInstance.play();
    });
  }
  if (btnPause) {
    btnPause.addEventListener('click', () => {
      if (lottieInstance) lottieInstance.pause();
    });
  }
  if (btnStop) {
    btnStop.addEventListener('click', () => {
      if (lottieInstance) lottieInstance.stop();
    });
  }

  // Export JSON
  if (exportJsonBtn) {
    exportJsonBtn.addEventListener('click', () => {
      const dataToExport = currentAnimationData || (window.lottie && window.lottie.presets && window.lottie.presets.checkmark);
      const jsonStr = JSON.stringify(dataToExport, null, 2);
      downloadFile('sr-micro-interaction.json', jsonStr, 'application/json');
      showStudioToast('✓ تم تصدير ملف Lottie JSON بنجاح!');
      if (window.SRStudioTelemetry) {
        window.SRStudioTelemetry.track('lottie-studio', 'export_json', { preset: animSelect ? animSelect.value : 'custom' });
      }
    });
  }

  // Export CSS Keyframes
  if (exportCssBtn) {
    exportCssBtn.addEventListener('click', () => {
      const speed = parseFloat((speedRange && speedRange.value) || 1);
      const duration = (2 / speed).toFixed(2);
      const color = (colorPicker && colorPicker.value) || '#c5a880';
      const css = `/* S&R CoreSync - Micro-Interactions Keyframes */
@keyframes srLottiePulse {
  0% { transform: scale(1) rotate(0deg); opacity: 1; filter: drop-shadow(0 0 10px rgba(197, 168, 128, 0.3)); }
  50% { transform: scale(1.08) rotate(180deg); opacity: 0.92; filter: drop-shadow(0 0 25px ${color}); }
  100% { transform: scale(1) rotate(360deg); opacity: 1; filter: drop-shadow(0 0 10px rgba(197, 168, 128, 0.3)); }
}

.sr-lottie-animated {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  animation: srLottiePulse ${duration}s ease-in-out infinite;
  --lottie-color: ${color};
}
`;
      downloadFile('sr-micro-interactions.css', css, 'text/css');
      showStudioToast('✓ تم تصدير كود CSS Keyframes الجاهز للتضمين!');
      if (window.SRStudioTelemetry) {
        window.SRStudioTelemetry.track('lottie-studio', 'export_css', { speed: speed, color: color });
        window.SRStudioTelemetry.recordLead({
          studio: 'lottie-studio',
          studioName: 'استوديو الرسوم والتفاعلات',
          type: 'design_export',
          title: `تصدير هوية وتفاعلات CSS Keyframes (${color})`,
          matchScore: 90,
          estimatedValue: '€ 9,500',
          clientHint: 'عميل تفاعلات وهوية رقمية للمواقع',
          status: 'engaged',
          statusLabel: 'تفاعل تصميم 🎨'
        });
      }
    });
  }
});
