import { useAuth } from '@/contexts/AuthContext';

export interface AdminUser {
  id: string;
  email: string;
  role: 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN';
  firstName: string;
  lastName: string;
  isAdmin: boolean;
  isDepartmentHead: boolean;
  hasManagementRights: boolean;
}

export const useAdmin = () => {
  const { user, loading, isAdmin, isDepartmentHead, isTeacherOrAbove } = useAuth();

  const adminUser: AdminUser | null = user ? {
    id: user.id,
    email: user.email,
    role: user.role,
    firstName: user.firstName,
    lastName: user.lastName,
    isAdmin,
    isDepartmentHead,
    hasManagementRights: isAdmin || isDepartmentHead
  } : null;

  return {
    adminUser,
    loading,
    error: null,
    isAdmin,
    isDepartmentHead,
    hasManagementRights: isAdmin || isDepartmentHead,
    role: user?.role || 'STUDENT'
  };
};