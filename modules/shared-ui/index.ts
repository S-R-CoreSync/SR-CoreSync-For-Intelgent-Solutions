/**
 * S&R CoreScience / CoreSync - Shared UI Architecture Module
 * Responsive Breakpoints, RTL/LTR Directionality & Video Hero Component
 */

export type ScreenBreakpoint = 'mobile' | 'tablet' | 'desktop' | 'ultrawide';

export interface LayoutOptions {
  direction: 'rtl' | 'ltr';
  locale: string;
  breakpoint: ScreenBreakpoint;
  enableVideoHero: boolean;
}

export class SharedUiService {
  private static instance: SharedUiService;

  private constructor() {}

  public static getInstance(): SharedUiService {
    if (!SharedUiService.instance) {
      SharedUiService.instance = new SharedUiService();
    }
    return SharedUiService.instance;
  }

  public detectBreakpoint(width: number): ScreenBreakpoint {
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    if (width < 1920) return 'desktop';
    return 'ultrawide';
  }

  public getDirectionForLocale(locale: string): 'rtl' | 'ltr' {
    const rtlLocales = ['ar', 'ku', 'ckb', 'fa', 'he', 'ur'];
    return rtlLocales.includes(locale.toLowerCase()) ? 'rtl' : 'ltr';
  }

  public createVideoHeroMarkup(poster: string = './assets/about-founder-poster-640.webp', videoSrc: string = './assets/hero-bg-abstract.mp4'): string {
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
