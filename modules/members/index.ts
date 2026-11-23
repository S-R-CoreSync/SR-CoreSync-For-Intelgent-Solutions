/**
 * S&R CoreScience / CoreSync - Members Feature Module
 * Member Registry, Digital QR Cards & Community Governance
 */

export interface MemberProfile {
  id: string;
  name: string;
  companyName?: string;
  tier: 'Elite' | 'Sovereign' | 'Enterprise' | 'Founder';
  joinedDate: string;
  qrCodeToken: string;
  status: 'active' | 'pending' | 'suspended';
}

export class MemberService {
  private static instance: MemberService;

  private constructor() {}

  public static getInstance(): MemberService {
    if (!MemberService.instance) {
      MemberService.instance = new MemberService();
    }
    return MemberService.instance;
  }

  public getMemberBadge(tier: MemberProfile['tier']): string {
    switch (tier) {
      case 'Founder': return '👑 المؤسس الشريك';
      case 'Sovereign': return '⚜️ الشريك السيادي';
      case 'Enterprise': return '🏢 عضوية المؤسسات';
      default: return '⭐ عضوية النخبة';
    }
  }

  public verifyQrToken(token: string): boolean {
    return token.startsWith('SR-MEM-') || token.startsWith('SR-QR-');
  }
}

export const memberService = MemberService.getInstance();
