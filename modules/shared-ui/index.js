/**
 * S&R CoreScience / CoreSync - Shared UI Architecture Module
 * Responsive Breakpoints, RTL/LTR Directionality & Video Hero Component
 */



export class SharedUiService {
  static instance: SharedUiService;

  constructor() {}

  static getInstance() {
    if (!SharedUiService.instance) {
      SharedUiService.instance = new SharedUiService();
    }
    return SharedUiService.instance;
  }

  detectBreakpoint(width) {
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    if (width < 1920) return 'desktop';
    return 'ultrawide';
  }

  getDirectionForLocale(locale) {
    const rtlLocales = ['ar', 'ku', 'ckb', 'fa', 'he', 'ur'];
    return rtlLocales.includes(locale.toLowerCase()) ? 'rtl' : 'ltr';
  }

  createVideoHeroMarkup(poster= './assets/about-founder-poster-640.webp', videoSrc= './assets/hero-bg-abstract.mp4') {
    return `
      <div class="sr-hero-video-wrapper" aria-hidden="true">
        <video class="sr-hero-bg-video" autoplay muted playsinline loop preload="metadata" poster="${poster}">
          <source src="${videoSrc}" type="video/mp4">
        </video>
        <div class="sr-hero-video-overlay"></div>
      </div>
    `.trim();
  }
}

export const sharedUiService = SharedUiService.getInstance();
