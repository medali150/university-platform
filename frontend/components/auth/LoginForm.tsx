'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { authApi } from '@/lib/auth-api-fixed'
import type { LoginCredentials, LoginResponse } from '@/lib/auth-api-fixed'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Mail, Lock } from 'lucide-react'

export function LoginForm() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [submitError, setSubmitError] = useState<string>('')
  const [formData, setFormData] = useState({
    loginField: '', // Can be email or login
    password: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error when user starts typing
    if (submitError) {
      setSubmitError('')
    }
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.loginField.trim() || !formData.password) {
      setSubmitError('Tous les champs sont requis')
      return
    }

    setLoading(true)
    setSubmitError('')
    
    try {
      // Determine if it's an email or login
      const isEmail = formData.loginField.includes('@')
      const credentials: LoginCredentials = {
        password: formData.password,
        ...(isEmail ? { email: formData.loginField } : { login: formData.loginField })
      }

      const result = await authApi.login(credentials)
      
      if (result.success && result.data) {
        // Store auth token
        localStorage.setItem('authToken', result.data.access_token)
        localStorage.setItem('userRole', result.data.user.role)
        localStorage.setItem('userInfo', JSON.stringify(result.data.user))
        
        // Redirect based on role
        const role = result.data.user.role
        switch (role) {
          case 'ADMIN':
            router.push('/admin')
            break
          case 'DEPARTMENT_HEAD':
            router.push('/department-head')
            break
          case 'TEACHER':
            router.push('/teacher')
            break
          case 'STUDENT':
            router.push('/student')
            break
          default:
            router.push('/dashboard')
        }
      } else {
        setSubmitError(result.error || 'Erreur lors de la connexion')
      }
    } catch (error) {
      console.error('Login error:', error)
      setSubmitError('Erreur de connexion. Veuillez vérifier vos identifiants.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemoCredentials = (role: 'admin' | 'teacher' | 'student' | 'depthead') => {
    const credentials = {
      admin: { email: 'admin@university.com', password: 'admin123' },
      teacher: { email: 'jean.dupont@university.com', password: 'teacher123' },
      student: { email: 'marie.martin@student.university.edu', password: 'student123' },
      depthead: { email: 'pierre.leclerc@university.com', password: 'depthead123' },
    }
    
    setFormData({
      loginField: credentials[role].email,
      password: credentials[role].password
    })
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="space-y-4">
        {submitError && (
          <Alert variant="destructive">
            <AlertDescription>{submitError}</AlertDescription>
          </Alert>
        )}

        <div>
          <label htmlFor="loginField" className="block text-sm font-medium mb-2">
            Email ou Nom d'utilisateur
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              id="loginField"
              name="loginField"
              value={formData.loginField}
              onChange={handleChange}
              placeholder="votre.email@university.com"
              className="pl-10"
              disabled={loading}
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-2">
            Mot de passe
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
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

      {/* Demo credentials */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Comptes de démonstration :</h3>
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('admin')}
            className="text-xs"
            disabled={loading}
          >
            Admin
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('teacher')}
            className="text-xs"
            disabled={loading}
          >
            Enseignant
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('student')}
            className="text-xs"
            disabled={loading}
          >
            Étudiant
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('depthead')}
            className="text-xs"
            disabled={loading}
          >
            Chef Dépt
          </Button>
        </div>
      </div>
    </div>
  )
}