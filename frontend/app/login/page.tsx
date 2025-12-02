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
import { Loader2, Mail, Lock, GraduationCap, Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const { login, loading, isAuthenticated, user } = useAuth()
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  })
  const [error, setError] = useState<string>('')
  const [showPassword, setShowPassword] = useState(false)

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
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="text-white/60 text-sm">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="max-w-md w-full space-y-8 relative z-10">
        {/* Header Section */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl blur-lg opacity-75"></div>
              <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-2xl transform hover:scale-110 transition-transform duration-300">
                <GraduationCap className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-300 to-purple-400">
            Plateforme Universitaire
          </h1>
          <p className="text-slate-400 text-base font-medium">
            Accédez à votre espace personnel
          </p>
        </div>

        {/* Login Card */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl blur-xl"></div>
          <Card className="relative shadow-2xl border border-white/10 bg-slate-800/50 backdrop-blur-xl rounded-2xl overflow-hidden">
            <CardHeader className="space-y-2 pb-6">
              <CardTitle className="text-2xl font-bold text-center text-white">Connexion</CardTitle>
              <CardDescription className="text-center text-slate-400">
                Entrez vos identifiants pour continuer
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Error Alert */}
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg text-sm font-medium animate-in fade-in">
                    ⚠️ {error}
                  </div>
                )}

                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-white font-semibold text-sm">
                    Adresse Email
                  </Label>
                  <div className="relative group">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="votre.email@university.com"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="pl-12 h-11 bg-slate-700/50 border border-slate-600/50 text-white placeholder:text-slate-500 focus:border-blue-500/50 focus:bg-slate-700/80 transition-all rounded-lg"
                      disabled={loading}
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-white font-semibold text-sm">
                    Mot de passe
                  </Label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleInputChange}
                      className="pl-12 pr-12 h-11 bg-slate-700/50 border border-slate-600/50 text-white placeholder:text-slate-500 focus:border-blue-500/50 focus:bg-slate-700/80 transition-all rounded-lg"
                      disabled={loading}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-blue-400 transition-colors"
                      disabled={loading}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <Button 
                  type="submit" 
                  className="w-full h-11 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-300 mt-6 shadow-lg hover:shadow-xl"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Connexion en cours...
                    </>
                  ) : (
                    'Se connecter'
                  )}
                </Button>
              </form>

              {/* Footer Links */}
              <div className="mt-8 space-y-4 border-t border-slate-700/50 pt-6">
                <div className="text-center">
                  <Link 
                    href="/forgot-password" 
                    className="text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors hover:underline"
                  >
                    Mot de passe oublié?
                  </Link>
                </div>

                <div className="text-center text-xs text-slate-500 leading-relaxed">
                  <p>
                    Vous n'avez pas de compte?<br/>
                    <span className="text-slate-400">Les comptes sont créés par l'administration.</span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Bottom Info */}
        <p className="text-center text-xs text-slate-500">
          Plateforme sécurisée • Chiffrement SSL • Données protégées
        </p>
      </div>
    </div>
  )
}