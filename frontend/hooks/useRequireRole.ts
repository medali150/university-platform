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
    // CRITICAL: Only check auth after loading is complete
    // This prevents redirect loops during initialization
    if (loading) {
      console.log('[useRequireRole] Still loading auth state...')
      return
    }

    console.log('[useRequireRole] Auth check:', { 
      isAuthenticated, 
      hasUser: !!user,
      userRole: user?.role,
      requiredRoles: roles,
      pathname 
    })

    if (!isAuthenticated || !user) {
      console.log('[useRequireRole] NOT AUTHENTICATED - redirecting to login')
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`)
      return
    }

    if (!roles.includes(user.role)) {
      const userRoute = user.role === 'STUDENT' 
        ? '/dashboard/student'
        : user.role === 'TEACHER'
        ? '/dashboard/teacher'
        : '/dashboard/department-head'
      
      console.log(`[useRequireRole] WRONG ROLE (${user.role}) - redirecting to ${userRoute}`)
      router.push(userRoute)
      return
    }

    console.log('[useRequireRole] ✅ Access granted')
  }, [user, loading, isAuthenticated, roles, router, pathname])

  return {
    user,
    isLoading: loading,
    isAuthenticated,
    hasRequiredRole: user ? roles.includes(user.role) : false,
  }
}