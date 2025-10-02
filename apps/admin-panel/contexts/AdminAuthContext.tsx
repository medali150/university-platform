'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { adminAuthApi, AdminUser } from '@/lib/admin-api';

interface AdminAuthContextType {
  admin: AdminUser | null;
  loading: boolean;
  login: (login: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

export function AdminAuthProvider({ children }: { children: React.ReactNode }) {
  const [admin, setAdmin] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize admin session
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (adminAuthApi.isAuthenticated()) {
          const result = await adminAuthApi.me();
          if (result.success && result.data) {
            setAdmin(result.data);
          } else {
            adminAuthApi.logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        adminAuthApi.logout();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (login: string, password: string) => {
    try {
      const result = await adminAuthApi.login(login, password);
      
      if (result.success && result.data) {
        setAdmin(result.data.user);
      } else {
        throw new Error(result.error || 'Admin login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      adminAuthApi.logout();
      setAdmin(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value: AdminAuthContextType = {
    admin,
    loading,
    login,
    logout,
    isAuthenticated: !!admin
  };

  return (
    <AdminAuthContext.Provider value={value}>
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const context = useContext(AdminAuthContext);
  if (context === undefined) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
}