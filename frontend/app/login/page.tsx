'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { LoginFormData } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, Mail, Lock, GraduationCap } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const { login, loading, isAuthenticated, user } = useAuth()
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  })
  const [error, setError] = useState<string>('')

  // Redirect if already authenticated
  useEffect(() => {
    // CRITICAL: Don't redirect while auth is still loading!
    if (loading) {
      console.log('[LoginPage] Auth still loading, waiting...')
      return
    }
    
    console.log('[LoginPage] Auth state:', { isAuthenticated, hasUser: !!user, userRole: user?.role })
    
    if (isAuthenticated && user) {
      const roleRoute = user.role === 'STUDENT' 
        ? '/dashboard/student'
        : user.role === 'TEACHER'
        ? '/dashboard/teacher'
        : user.role === 'DEPARTMENT_HEAD'
        ? '/dashboard/department-head'
        : '/dashboard/admin'
      
      console.log('[LoginPage] ✅ AUTHENTICATED - redirecting to:', roleRoute)
      // Use replace to avoid back button issues
      router.replace(roleRoute)
    } else {
      console.log('[LoginPage] Not authenticated, staying on login')
    }
  }, [isAuthenticated, user, router, loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs')
      return
    }

    try {
      console.log('Attempting login with:', { email: formData.email, password: '***' })
      await login(formData)
      // Redirect will happen via useEffect after a short delay
    } catch (error) {
      // Error is already handled in the AuthContext with toast
      console.error('Login error:', error)
      setError('Identifiants incorrects. Veuillez réessayer.')
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  // Show loading state while checking auth
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and title */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-blue-600 p-3 rounded-full">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Plateforme Universitaire
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Connectez-vous à votre compte
          </p>
        </div>

        {/* Login form */}
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">Connexion</CardTitle>
            <CardDescription className="text-center">
              Entrez vos identifiants pour accéder à la plateforme
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="votre.email@university.com"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Connexion en cours...
                  </>
                ) : (
                  'Se connecter'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Pas encore de compte ?{' '}
                <Link 
                  href="/register" 
                  className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  Créer un compte
                </Link>
              </p>
            </div>

            {/* Demo credentials */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Comptes de test :</h3>
              <div className="text-xs text-gray-600 space-y-1">
                <div><strong>Enseignant:</strong> teacher1@university.tn / Test123!</div>
                <div><strong>Étudiant:</strong> student1@university.tn / Test123!</div>
                <div><strong>Chef Dépt:</strong> chef.dept1@university.tn / Test123!</div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Mot de passe pour tous les comptes : <strong>Test123!</strong>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}