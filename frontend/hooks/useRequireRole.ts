'use client'

import { useAuth } from './useAuth'
import { Role } from '@/types/auth'
import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export function useRequireRole(requiredRoles: Role | Role[]) {
  const { user, loading, isAuthenticated } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]

  useEffect(() => {
    if (loading) return

    if (!isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`)
      return
    }

    if (user && !roles.includes(user.role)) {
      // Redirect to appropriate dashboard
      const userRoute = user.role === 'STUDENT' 
        ? '/dashboard/student'
        : user.role === 'TEACHER'
        ? '/dashboard/teacher'
        : '/dashboard/department-head'
      
      router.push(userRoute)
      return
    }
  }, [user, loading, isAuthenticated, roles, router, pathname])

  return {
    user,
    isLoading: loading,
    isAuthenticated,
    hasRequiredRole: user ? roles.includes(user.role) : false,
  }
}