/**
 * S&R CoreScience / CoreSync - Media Hub Feature Module
 * Video Streaming, Live Cinema, WebRTC Virtual Clinic & Podcasts
 */

export interface VideoStreamConfig {
  videoUrl: string;
  posterUrl: string;
  autoplay: boolean;
  muted: boolean;
  playsinline: boolean;
  loop: boolean;
  objectFit: 'cover' | 'contain';
}

export class MediaHubService {
  private static instance: MediaHubService;

  private constructor() {}

  public static getInstance(): MediaHubService {
    if (!MediaHubService.instance) {
      MediaHubService.instance = new MediaHubService();
    }
    return MediaHubService.instance;
  }

  public getHeroVideoConfig(): VideoStreamConfig {
    return {
      videoUrl: './assets/hero-bg-abstract.mp4',
      posterUrl: './assets/about-founder-poster-640.webp',
      autoplay: true,
      muted: true,
      playsinline: true,
      loop: true,
      objectFit: 'cover'
    };
  }
}

export const mediaHubService = MediaHubService.getInstance();
