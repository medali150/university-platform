'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { getRoleRoute } from '@/lib/roles'
import { Loader2 } from 'lucide-react'

export default function HomePage() {
  const { user, loading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return

    if (isAuthenticated && user) {
      const route = getRoleRoute(user.role as any)
      router.push(route)
    } else {
      router.push('/login')
    }
  }, [user, loading, isAuthenticated, router])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-16 h-16">
            <Loader2 className="w-full h-full animate-spin text-blue-500" />
          </div>
          <div className="text-center">
            <p className="text-white font-medium">Chargement...</p>
            <p className="text-slate-400 text-sm">Redirection en cours</p>
          </div>
        </div>
      </div>
    )
  }

  return null
}