/**
 * S&R CoreScience / CoreSync - Media Hub Feature Module
 * Video Streaming, Live Cinema, WebRTC Virtual Clinic & Podcasts
 */


export class MediaHubService {
  static instance: MediaHubService;

  constructor() {}

  static getInstance() {
    if (!MediaHubService.instance) {
      MediaHubService.instance = new MediaHubService();
    }
    return MediaHubService.instance;
  }

  getHeroVideoConfig() {
    return {
      videoUrl: './assets/hero-bg-abstract.mp4',
      posterUrl: './assets/about-founder-poster-640.webp',
      autoplay,
      muted,
      playsinline,
      loop,
      objectFit: 'cover'
    };
  }
}

export const mediaHubService = MediaHubService.getInstance();
