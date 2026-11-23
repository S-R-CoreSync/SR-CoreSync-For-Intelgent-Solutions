/**
 * S&R CoreScience / CoreSync - Members Feature Module
 * Member Registry, Digital QR Cards & Community Governance
 */


export class MemberService {
  static instance;

  constructor() {}

  static getInstance() {
    if (!MemberService.instance) {
      MemberService.instance = new MemberService();
    }
    return MemberService.instance;
  }

  getMemberBadge(tier) {
    switch (tier) {
      case 'Founder': return '👑 المؤسس الشريك';
      case 'Sovereign': return '⚜️ الشريك السيادي';
      case 'Enterprise': return '🏢 عضوية المؤسسات';
      default: return '⭐ عضوية النخبة';
    }
  }

  verifyQrToken(token) {
    return token.startsWith('SR-MEM-') || token.startsWith('SR-QR-');
  }
}

export const memberService = MemberService.getInstance();
