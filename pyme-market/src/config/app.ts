export const config = {
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  mode: import.meta.env.MODE,

  auth: {
    skipAuthInDev: true,
    devUser: {
      id: 'dev-user-1',
      email: 'admin@pyme-market.com',
      name: 'Loreley Pazmiño',
      role: 'admin',
      isSuperuser: true,
      isActive: true,
      isResetPassword: false,
      createdAt: new Date(),
    },
    devToken: 'dev-token-12345',
    defaultPassword: 'PYME2025!',
  },

  api: {
    auth: import.meta.env.DEV 
      ? 'http://127.0.0.1:8000' 
      : 'https://auth.pyme-market.com',
    products: import.meta.env.DEV 
      ? 'http://127.0.0.1:8001'
      : 'https://products.pyme-market.com',
    orders: import.meta.env.DEV 
      ? 'http://127.0.0.1:8002/api/v1' 
      : 'https://orders.pyme-market.com/api/v1',
    chat: import.meta.env.DEV 
      ? 'http://127.0.0.1:8003' 
      : 'https://chat.pyme-market.com',
  },

  debug: {
    enabled: import.meta.env.DEV,
    logLevel: import.meta.env.DEV ? 'debug' : 'error',
  },
};

export const shouldSkipAuth = (): boolean => {
  return config.isDevelopment && config.auth.skipAuthInDev;
};

export const getDevUser = () => {
  return shouldSkipAuth() ? config.auth.devUser : null;
};

export const devLog = (message: string, data?: unknown) => {
  if (config.debug.enabled) {
    console.log(`[DEV] ${message}`, data || '');
  }
};
