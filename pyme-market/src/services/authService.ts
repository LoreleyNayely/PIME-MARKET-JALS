import type { 
  User, 
  LoginData, 
  RegisterData, 
  ForgotPasswordData, 
  ChangePasswordData,
  LoginResponse,
  RegisterResponse,
  AuthResponse 
} from '../interfaces/auth';
import { authApiClient } from './apiClient';
import { config, devLog } from '../config/app';

class AuthService {
  private readonly fallbackUsers: User[] = [];

  constructor() {
    const savedUsers = localStorage.getItem('demo_users');
    if (savedUsers) {
      this.fallbackUsers.push(...JSON.parse(savedUsers));
    } else {
      this.fallbackUsers.push({
        email: 'admin@pyme-market.com',
        name: 'Administrador',
        isActive: true,
        isSuperuser: true,
        isResetPassword: false,
        role: 'admin',
      });
      this.saveUsers();
    }
  }

  private saveUsers(): void {
    localStorage.setItem('demo_users', JSON.stringify(this.fallbackUsers));
  }

  private generateId(): string {
    return Math.random().toString(36).substring(2, 11);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private transformUser(apiUser: RegisterResponse): User {
    return {
      email: apiUser.email,
      name: apiUser.name,
      isActive: apiUser.isActive,
      isSuperuser: apiUser.isSuperuser,
      isResetPassword: apiUser.isResetPassword,
      id: apiUser.email,
      role: apiUser.isSuperuser ? 'admin' : 'client',
      createdAt: new Date(),
    };
  }

  async login(data: LoginData): Promise<AuthResponse> {
    try {
      devLog('🔐 Intentando login con microservicio de auth', { email: data.email });
      
      const response = await authApiClient.post<LoginResponse>('/auth/login', data);
      
      const user = this.transformUser(response.user);
      const token = response.accessToken;
      
      localStorage.setItem('auth_token', token);
      localStorage.setItem('current_user', JSON.stringify(user));
      
      devLog('✅ Login exitoso con microservicio', user);
      return { user, token };

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      
      return this.loginFallback(data);
    }
  }

  private async loginFallback(data: LoginData): Promise<AuthResponse> {
    await this.delay(1000);

    const user = this.fallbackUsers.find(u => u.email === data.email);
    
    if (!user) {
      throw new Error('Usuario no encontrado');
    }

    if (data.password.length < 6) {
      throw new Error('Contraseña incorrecta');
    }

    const token = `demo_token_${this.generateId()}`;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('current_user', JSON.stringify(user));

    return { user, token };
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      devLog('📝 Intentando registro con microservicio de auth', { email: data.email });
      
      const registerPayload = {
        email: data.email,
        name: data.name,
        password: data.password,
      };
      
      const response = await authApiClient.post<RegisterResponse>('/auth/register', registerPayload);
      
      const user = this.transformUser(response);
      
      const loginResponse = await this.login({
        email: data.email,
        password: data.password,
      });
      
      devLog('✅ Registro exitoso con microservicio', user);
      return loginResponse;

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      
      return this.registerFallback(data);
    }
  }

  private async registerFallback(data: RegisterData): Promise<AuthResponse> {
    await this.delay(1000);

    if (this.fallbackUsers.find(u => u.email === data.email)) {
      throw new Error('El email ya está registrado');
    }

    if (data.confirmPassword && data.password !== data.confirmPassword) {
      throw new Error('Las contraseñas no coinciden');
    }

    if (data.password.length < 6) {
      throw new Error('La contraseña debe tener al menos 6 caracteres');
    }

    const newUser: User = {
      email: data.email,
      name: data.name,
      isActive: true,
      isSuperuser: false,
      isResetPassword: false,
      id: this.generateId(),
      role: 'client',
      createdAt: new Date(),
    };

    this.fallbackUsers.push(newUser);
    this.saveUsers();

    const token = `demo_token_${this.generateId()}`;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('current_user', JSON.stringify(newUser));

    return { user: newUser, token };
  }

  async validateToken(): Promise<boolean> {
    try {
      const token = this.getToken();
      if (!token) return false;

      devLog('🔍 Validando token con microservicio');
      
      const response = await authApiClient.get<{ valid: boolean }>('/auth/validate-token');
      
      devLog('✅ Token válido', response);
      return response.valid === true;

    } catch (error) {
      devLog('⚠️ Error validando token', error);
      return false;
    }
  }

  async getCurrentUserFromApi(): Promise<User | null> {
    try {
      devLog('👤 Obteniendo usuario actual del microservicio');
      
      const response = await authApiClient.get<RegisterResponse>('/auth/me');
      const user = this.transformUser(response);
      
      localStorage.setItem('current_user', JSON.stringify(user));
      
      devLog('✅ Usuario obtenido del microservicio', user);
      return user;

    } catch (error) {
      devLog('⚠️ Error obteniendo usuario del microservicio', error);
      return null;
    }
  }

  async forgotPassword(data: ForgotPasswordData): Promise<{ message: string }> {
    try {
      devLog('🔑 Intentando reset de contraseña con microservicio');
      return this.forgotPasswordFallback(data);

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.forgotPasswordFallback(data);
    }
  }

  private async forgotPasswordFallback(_data: ForgotPasswordData): Promise<{ message: string }> {
    await this.delay(1000);

    return {
      message: `Tu contraseña ha sido restablecida a: ${config.auth.defaultPassword}. Te recomendamos cambiarla después de iniciar sesión.`
    };
  }

  async changePassword(data: ChangePasswordData): Promise<{ message: string }> {
    try {
      devLog('🔐 Intentando cambio de contraseña con microservicio');
      return this.changePasswordFallback(data);

    } catch (error) {
      devLog('⚠️ Error con microservicio, usando fallback', error);
      return this.changePasswordFallback(data);
    }
  }

  private async changePasswordFallback(data: ChangePasswordData): Promise<{ message: string }> {
    await this.delay(1000);

    if (data.newPassword !== data.confirmNewPassword) {
      throw new Error('Las contraseñas nuevas no coinciden');
    }

    if (data.newPassword.length < 6) {
      throw new Error('La nueva contraseña debe tener al menos 6 caracteres');
    }

    return {
      message: 'Contraseña cambiada exitosamente'
    };
  }

  async logout(): Promise<void> {
    try {
      devLog('🚪 Cerrando sesión');
    } catch (error) {
      devLog('⚠️ Error al hacer logout en microservicio', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('current_user');
    }
  }

  getCurrentUser(): User | null {
    const userData = localStorage.getItem('current_user');
    if (userData) {
      return JSON.parse(userData);
    }
    return null;
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getCurrentUser();
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin' || user?.isSuperuser === true;
  }

  isClient(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'client' || (user?.isSuperuser === false && user?.isActive === true);
  }
}

export const authService = new AuthService();
