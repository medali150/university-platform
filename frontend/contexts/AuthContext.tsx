'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { User, CreateUserData, LoginData, AuthContextType } from '@/types/auth'
import { authApi, AuthApiError } from '@/lib/auth-api'
import { toast } from 'sonner'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  // Initialize auth state from stored data
  useEffect(() => {
    setMounted(true)
    
    const initAuth = async () => {
      try {
        // Only run on client side
        if (typeof window === 'undefined') {
          setLoading(false)
          return
        }

        if (authApi.isAuthenticated()) {
          // Try to get fresh user data
          try {
            const userData = await authApi.getCurrentUser()
            setUser(userData)
          } catch (error) {
            // If API call fails, try stored user data
            const storedUser = authApi.getUser()
            if (storedUser) {
              setUser(storedUser)
            } else {
              // Clear invalid auth data
              authApi.logout()
              setUser(null)
            }
          }
        } else {
          // Check if we have stored user data
          const storedUser = authApi.getUser()
          if (storedUser) {
            setUser(storedUser)
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        // Clear invalid auth data
        authApi.logout()
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginData) => {
    try {
      setLoading(true)
      const response = await authApi.login(credentials)
      setUser(response.user)
      
      toast.success(`Bienvenue ${authApi.getUserDisplayName(response.user)} !`)
    } catch (error) {
      console.error('Login failed:', error)
      let errorMessage = 'Erreur de connexion'
      
      if (error instanceof AuthApiError) {
        switch (error.status) {
          case 401:
            errorMessage = 'Email ou mot de passe incorrect'
            break
          case 422:
            errorMessage = 'Données de connexion invalides'
            break
          case 500:
            errorMessage = 'Erreur serveur, veuillez réessayer'
            break
          default:
            errorMessage = error.message
        }
      }
      
      toast.error(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData: CreateUserData) => {
    try {
      setLoading(true)
      await authApi.register(userData)
      
      toast.success('Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
    } catch (error) {
      console.error('Registration failed:', error)
      let errorMessage = 'Erreur lors de l\'inscription'
      
      if (error instanceof AuthApiError) {
        switch (error.status) {
          case 400:
            errorMessage = 'Un utilisateur avec cet email ou login existe déjà'
            break
          case 422:
            errorMessage = 'Données d\'inscription invalides'
            break
          case 500:
            errorMessage = 'Erreur serveur, veuillez réessayer'
            break
          default:
            errorMessage = error.message
        }
      }
      
      toast.error(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
    
    toast.success('Vous avez été déconnecté avec succès')
    
    // Navigate to login page after logout with a small delay for toast
    setTimeout(() => {
      router.push('/login')
    }, 500)
  }

  const value: AuthContextType = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Helper hooks for role-based access
export function useRequireAuth() {
  const { user, loading } = useAuth()
  
  useEffect(() => {
    if (!loading && !user) {
      // Redirect to login page
      window.location.href = '/login'
    }
  }, [user, loading])
  
  return { user, loading }
}

export function useRequireRole(allowedRoles: string[]) {
  const { user, loading } = useAuth()
  
  useEffect(() => {
    if (!loading) {
      if (!user) {
        window.location.href = '/login'
      } else if (!allowedRoles.includes(user.role)) {
        window.location.href = '/unauthorized'
      }
    }
  }, [user, loading, allowedRoles])
  
  return { user, loading, hasAccess: user ? allowedRoles.includes(user.role) : false }
}