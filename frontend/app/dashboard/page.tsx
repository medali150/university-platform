'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated, loading } = useAuth()

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        router.push('/login')
      } else if (user) {
        // Redirect to role-specific dashboard
        const roleRoute = user.role === 'STUDENT' 
          ? '/dashboard/student'
          : user.role === 'TEACHER'
          ? '/dashboard/teacher'
          : user.role === 'DEPARTMENT_HEAD'
          ? '/dashboard/department-head'
          : '/dashboard/admin'
        
        router.push(roleRoute)
      }
    }
  }, [user, isAuthenticated, loading, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600">Redirection en cours...</p>
      </div>
    </div>
  )
}