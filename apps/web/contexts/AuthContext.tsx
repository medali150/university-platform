'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { authApi, User } from '@/lib/api-utils';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (login: string, password: string, expectedRole?: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    role?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  isAdmin: boolean;
  isDepartmentHead: boolean;
  isTeacherOrAbove: boolean;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  // Load user from localStorage on startup
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setToken(savedToken);
      verifyAndLoadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const verifyAndLoadUser = async () => {
    try {
      const result = await authApi.me();
      if (result.success && result.data) {
        setUser(result.data);
      } else {
        // Invalid token
        authApi.logout();
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Error verifying user:', error);
      authApi.logout();
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (login: string, password: string, expectedRole?: string) => {
    try {
      const result = await authApi.login(login, password);
      
      if (result.success && result.data) {
        // Cast the user data to include all required fields
        const userData: User = {
          ...result.data.user,
          role: result.data.user.role as 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN',
          createdAt: (result.data.user as any).createdAt || new Date().toISOString(),
          updatedAt: (result.data.user as any).updatedAt || new Date().toISOString()
        };

        // Validate role if expectedRole is provided
        if (expectedRole && userData.role !== expectedRole) {
          throw new Error(`Rôle incorrect. Connecté en tant que ${getRoleLabel(userData.role)}, mais ${getRoleLabel(expectedRole)} attendu.`);
        }

        setUser(userData);
        setToken(result.data.access_token);
      } else {
        throw new Error(result.error || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  // Helper function to get role labels in French
  const getRoleLabel = (role: string): string => {
    const roleLabels = {
      'STUDENT': 'Étudiant',
      'TEACHER': 'Professeur',
      'DEPARTMENT_HEAD': 'Chef de département',
      'ADMIN': 'Administrateur'
    };
    return roleLabels[role as keyof typeof roleLabels] || role;
  };

  const register = async (userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    role?: string;
  }) => {
    try {
      // Convert to the format expected by FastAPI
      const registerData = {
        ...userData,
        login: userData.email, // Use email as login
        role: userData.role || 'STUDENT'
      };

      const result = await authApi.register(registerData);
      
      if (result.success && result.data) {
        // After registration, login the user
        await login(registerData.login, userData.password);
      } else {
        throw new Error(result.error || 'Registration failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      authApi.logout();
      setUser(null);
      setToken(null);
    } catch (error) {
      console.error('Error during logout:', error);
      // Force logout even if there's an error
      authApi.logout();
      setUser(null);
      setToken(null);
    }
  };

  const isAdmin = user?.role === 'ADMIN';
  const isDepartmentHead = user?.role === 'DEPARTMENT_HEAD';
  const isTeacherOrAbove = ['TEACHER', 'DEPARTMENT_HEAD', 'ADMIN'].includes(user?.role || '');

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin,
    isDepartmentHead,
    isTeacherOrAbove,
    token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}