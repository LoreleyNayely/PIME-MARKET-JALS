import { createContext, useContext, useReducer, useEffect, useMemo } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthState, LoginData, RegisterData, ForgotPasswordData, ChangePasswordData } from '../interfaces/auth';
import { authService } from '../services/authService';
import { shouldSkipAuth, getDevUser, devLog } from '../config/app';

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_RESET_ERROR' };

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: { message: action.payload },
      };
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'AUTH_RESET_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

interface AuthContextType extends AuthState {
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  forgotPassword: (data: ForgotPasswordData) => Promise<string>;
  changePassword: (data: ChangePasswordData) => Promise<string>;
  logout: () => void;
  resetError: () => void;
  isAdmin: () => boolean;
  isClient: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };

interface AuthProviderProps {
  readonly children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const checkAuth = () => {
      if (shouldSkipAuth()) {
        const devUser = getDevUser();
        if (devUser) {
          devLog('👨‍💻 Usando usuario de desarrollo', devUser);
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: { user: devUser, token: 'dev-token' }
          });
          return;
        }
      }

      const user = authService.getCurrentUser();
      const token = authService.getToken();

      if (user && token) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: { user, token }
        });
      }
    };

    checkAuth();
  }, []);

  const login = async (data: LoginData) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authService.login(data);
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: response
      });
    } catch (error) {
      dispatch({
        type: 'AUTH_ERROR',
        payload: error instanceof Error ? error.message : 'Error al iniciar sesión'
      });
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authService.register(data);
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: response
      });
    } catch (error) {
      dispatch({
        type: 'AUTH_ERROR',
        payload: error instanceof Error ? error.message : 'Error al registrarse'
      });
      throw error;
    }
  };

  const forgotPassword = async (data: ForgotPasswordData): Promise<string> => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authService.forgotPassword(data);
      dispatch({ type: 'AUTH_RESET_ERROR' });
      return response.message;
    } catch (error) {
      dispatch({
        type: 'AUTH_ERROR',
        payload: error instanceof Error ? error.message : 'Error al recuperar contraseña'
      });
      throw error;
    }
  };

  const changePassword = async (data: ChangePasswordData): Promise<string> => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authService.changePassword(data);
      dispatch({ type: 'AUTH_RESET_ERROR' });
      return response.message;
    } catch (error) {
      dispatch({
        type: 'AUTH_ERROR',
        payload: error instanceof Error ? error.message : 'Error al cambiar contraseña'
      });
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    dispatch({ type: 'AUTH_LOGOUT' });
  };

  const resetError = () => {
    dispatch({ type: 'AUTH_RESET_ERROR' });
  };

  const isAdmin = () => {
    return authService.isAdmin();
  };

  const isClient = () => {
    return authService.isClient();
  };

  const value: AuthContextType = useMemo(() => ({
    ...state,
    login,
    register,
    forgotPassword,
    changePassword,
    logout,
    resetError,
    isAdmin,
    isClient,
  }), [state]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
