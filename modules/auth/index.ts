/**
 * S&R CoreScience / CoreSync - Auth Feature Module
 * Enterprise Authentication, RBAC, Hardware-Lock & Session Management
 */

export interface UserSession {
  userId: string;
  role: 'superadmin' | 'advisor' | 'developer' | 'partner' | 'guest';
  email: string;
  hardwareMachineId?: string;
  licensedUntil: string;
  token: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  currentUser: UserSession | null;
  permissions: string[];
}

export class AuthService {
  private static instance: AuthService;
  private state: AuthState = {
    isAuthenticated: false,
    currentUser: null,
    permissions: []
  };

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  public getSession(): UserSession | null {
    try {
      const saved = localStorage.getItem('sr_auth_session');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return this.state.currentUser;
  }

  public authenticateWithHardwareId(machineId: string, licenseKey: string): boolean {
    if (machineId && licenseKey.startsWith('SRLIC-')) {
      const session: UserSession = {
        userId: 'dev_' + Math.floor(1000 + Math.random() * 9000),
        role: 'developer',
        email: 'developer@sr-coresync.com',
        hardwareMachineId: machineId,
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

  public logout(): void {
    this.state.isAuthenticated = false;
    this.state.currentUser = null;
    try {
      localStorage.removeItem('sr_auth_session');
    } catch (e) {}
  }
}

export const authService = AuthService.getInstance();
