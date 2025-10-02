import { UserRole } from '@/types/api'

export const ROLE_ROUTES = {
  [UserRole.STUDENT]: '/dashboard/student',
  [UserRole.TEACHER]: '/dashboard/teacher',
  [UserRole.DEPARTMENT_HEAD]: '/dashboard/department-head',
} as const

export const ROLE_PERMISSIONS = {
  [UserRole.STUDENT]: {
    canViewTimetable: true,
    canEditTimetable: false,
    canManageAbsences: true,
    canManageUsers: false,
    canManageSubjects: false,
    canViewAnalytics: false,
    canExportData: false,
  },
  [UserRole.TEACHER]: {
    canViewTimetable: true,
    canEditTimetable: true,
    canManageAbsences: true,
    canManageUsers: false,
    canManageSubjects: false,
    canViewAnalytics: false,
    canExportData: false,
  },
  [UserRole.DEPARTMENT_HEAD]: {
    canViewTimetable: true,
    canEditTimetable: true,
    canManageAbsences: true,
    canManageUsers: true,
    canManageSubjects: true,
    canViewAnalytics: true,
    canExportData: true,
  },
} as const

export function getRoleRoute(role: UserRole): string {
  return ROLE_ROUTES[role] || '/dashboard'
}

export function hasPermission(role: UserRole, permission: keyof typeof ROLE_PERMISSIONS[UserRole]): boolean {
  return ROLE_PERMISSIONS[role]?.[permission] || false
}