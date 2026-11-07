// lottie-studio.js – Handles loading, preview, speed, color and export
// Uses the minimal stub `window.lottie` defined in lottie.min.js.

let lottieInstance = null;
let loadedAnimationData = null; // Store JSON for export if user loads a file

// Helper to download data as a file
def downloadFile(filename, content, mime = 'application/json') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// Initialize UI events after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('lottieFile');
  const speedRange = document.getElementById('speedRange');
  const colorPicker = document.getElementById('colorPicker');
  const previewDiv = document.getElementById('lottiePreview');
  const exportJsonBtn = document.getElementById('exportJsonBtn');
  const exportCssBtn = document.getElementById('exportCssBtn');

  // Load animation from local file (JSON)
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        loadedAnimationData = JSON.parse(ev.target.result);
        // For demo we reuse the stub animation – ignore actual data
        if (lottieInstance) lottieInstance.destroy();
        lottieInstance = lottie.loadAnimation({
          container: previewDiv,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          animationData: loadedAnimationData,
        });
      } catch (err) {
        alert('ملف Lottie غير صالح');
        console.error(err);
      }
    };
    reader.readAsText(file);
  });

  // Speed control – updates animation speed
  speedRange.addEventListener('input', () => {
    const speed = parseFloat(speedRange.value);
    if (lottieInstance) lottieInstance.setSpeed(speed);
  });

  // Color control – CSS variable applied to preview container
  colorPicker.addEventListener('input', () => {
    const color = colorPicker.value;
    previewDiv.style.setProperty('--lottie-color', color);
  });

  // Export JSON – if a file was loaded, download it again
  exportJsonBtn.addEventListener('click', () => {
    if (!loadedAnimationData) {
      alert('لم يتم تحميل ملف Lottie لتصديره');
      return;
    }
    const jsonStr = JSON.stringify(loadedAnimationData, null, 2);
    downloadFile('animation-export.json', jsonStr, 'application/json');
  });

  // Export CSS – generate simple keyframes based on current speed
  exportCssBtn.addEventListener('click', () => {
    const speed = parseFloat(speedRange.value) || 1;
    const duration = (2 / speed).toFixed(2);
    const css = `@keyframes lottieSpin {\n  from { transform: rotate(0deg); }\n  to { transform: rotate(360deg); }\n}\n\n.lottie-preview {\n  animation: lottieSpin ${duration}s linear infinite;\n  --lottie-color: ${colorPicker.value};\n}`;
    downloadFile('lottie-animation.css', css, 'text/css');
  });
});
