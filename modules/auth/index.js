/**
 * S&R CoreScience / CoreSync - Auth Feature Module
 * Enterprise Authentication, RBAC, Hardware-Lock & Session Management
 */



export class AuthService {
  static instance: AuthService;
  state= {
    isAuthenticated,
    currentUser,
    permissions: []
  };

  constructor() {}

  static getInstance() {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  getSession() {
    try {
      const saved = localStorage.getItem('sr_auth_session');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return this.state.currentUser;
  }

  authenticateWithHardwareId(machineId, licenseKey) {
    if (machineId && licenseKey.startsWith('SRLIC-')) {
      const session= {
        userId: 'dev_' + Math.floor(1000 + Math.random() * 9000),
        role,
        email: 'developer@sr-coresync.com',
        hardwareMachineId,
        licensedUntil: '2027-12-31',
        token: 'sr_tok_' + Math.random().toString(36).substring(2)
      };
      this.state.isAuthenticated = true;
      this.state.currentUser = session;
      try {
        localStorage.setItem('sr_auth_session', JSON.stringify(session));
      } catch (e) {}
      return true;
    }
    return false;
  }

  logout() {
    this.state.isAuthenticated = false;
    this.state.currentUser = null;
    try {
      localStorage.removeItem('sr_auth_session');
    } catch (e) {}
  }
}

export const authService = AuthService.getInstance();
