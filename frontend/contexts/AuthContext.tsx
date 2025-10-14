'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { User, CreateUserData, LoginData, AuthContextType } from '@/types/auth'
import { authApi, LoginCredentials, LoginResponse, User as ApiUser } from '@/lib/auth-api'
import { toast } from 'sonner'

// Helper function to convert API User to App User
function convertApiUserToAppUser(apiUser: ApiUser): User {
  return {
    id: apiUser.id,
    nom: apiUser.nom,
    prenom: apiUser.prenom,
    email: apiUser.email,
    login: apiUser.login || apiUser.email, // Fallback to email if login is missing
    role: apiUser.role,
    createdAt: apiUser.createdAt,
    updatedAt: apiUser.updatedAt
  }
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Flag to prevent multiple initializations (outside component to persist across renders)
let authInitialized = false

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  // Initialize auth state from stored data
  useEffect(() => {
    setMounted(true)
    
    const initAuth = async () => {
      // Prevent multiple initializations
      if (authInitialized) {
        console.log('AuthContext: Already initialized, skipping')
        setLoading(false)
        return
      }
      authInitialized = true
      
      try {
        // Only run on client side
        if (typeof window === 'undefined') {
          console.log('AuthContext: SSR detected, skipping init')
          setLoading(false)
          return
        }

        console.log('AuthContext: Initializing auth from storage...')
        
        // First, try to get stored user data (fast, synchronous)
        const storedUser = authApi.getStoredUser()
        const storedToken = authApi.getStoredToken()
        
        console.log('AuthContext: Stored data check', { 
          hasUser: !!storedUser, 
          hasToken: !!storedToken 
        })

        if (storedUser && storedToken) {
          // Set user immediately from storage
          setUser(convertApiUserToAppUser(storedUser))
          console.log('AuthContext: User restored from storage', storedUser.role)
          
          // Then try to refresh user data from API to validate token
          try {
            const result = await authApi.getCurrentUser(storedToken)
            if (result.success && result.data) {
              setUser(convertApiUserToAppUser(result.data))
              console.log('AuthContext: ✅ Token valid, user refreshed from API')
            } else if (result.error?.includes('401') || result.error?.includes('Unauthorized')) {
              // Token is invalid/expired - clear everything
              console.log('AuthContext: ❌ Token expired/invalid (401), clearing auth data')
              authApi.clearAuthData()
              setUser(null)
            }
          } catch (error: any) {
            console.log('AuthContext: API refresh failed', error)
            // Check if it's a 401 error
            if (error?.message?.includes('401') || error?.status === 401) {
              console.log('AuthContext: ❌ Token invalid, clearing auth data')
              authApi.clearAuthData()
              setUser(null)
            } else {
              // Keep using stored user data for other errors (network, etc.)
              console.log('AuthContext: Using stored data (API temporarily unavailable)')
            }
          }
        } else {
          console.log('AuthContext: No stored auth data found')
          setUser(null)
        }
      } catch (error) {
        console.error('AuthContext: Failed to initialize auth:', error)
        // Clear invalid auth data
        authApi.clearAuthData()
        setUser(null)
      } finally {
        setLoading(false)
        console.log('AuthContext: Initialization complete')
      }
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginData) => {
    try {
      setLoading(true)
      
      // Convert LoginData to LoginCredentials
      const loginCredentials: LoginCredentials = {
        email: credentials.email,
        password: credentials.password
      }
      
      const result = await authApi.login(loginCredentials)
      
      if (result.success && result.data) {
        // Store auth data
        authApi.storeAuthData(result.data)
        setUser(convertApiUserToAppUser(result.data.user))
        
        toast.success(`Bienvenue ${result.data.user.prenom} ${result.data.user.nom} !`)
      } else {
        throw new Error(result.error || 'Login failed')
      }
    } catch (error) {
      console.error('Login failed:', error)
      let errorMessage = 'Erreur de connexion'
      
      if (error instanceof Error) {
        errorMessage = error.message
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
      
      // Convert CreateUserData based on role
      let result
      if (userData.role === 'DEPARTMENT_HEAD' && userData.departmentId) {
        result = await authApi.registerDepartmentHead({
          nom: userData.nom,
          prenom: userData.prenom,
          email: userData.email,
          password: userData.password,
          role: 'DEPARTMENT_HEAD',
          department_id: userData.departmentId
        })
      } else if (userData.role === 'TEACHER' && userData.departmentId) {
        result = await authApi.registerTeacher({
          nom: userData.nom,
          prenom: userData.prenom,
          email: userData.email,
          password: userData.password,
          role: 'TEACHER',
          department_id: userData.departmentId
        })
      } else if (userData.role === 'STUDENT') {
        result = await authApi.registerStudent({
          nom: userData.nom,
          prenom: userData.prenom,
          email: userData.email,
          password: userData.password,
          role: 'STUDENT',
          ...(userData.specialtyId && { specialty_id: userData.specialtyId })
        })
      } else {
        throw new Error('Invalid registration data or missing required fields')
      }
      
      if (result.success) {
        toast.success('Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
      } else {
        throw new Error(result.error || 'Registration failed')
      }
    } catch (error) {
      console.error('Registration failed:', error)
      let errorMessage = 'Erreur lors de l\'inscription'
      
      if (error instanceof Error) {
        if (error.message.includes('already has a department head')) {
          errorMessage = 'Ce département a déjà un chef assigné'
        } else if (error.message.includes('already exists')) {
          errorMessage = 'Un utilisateur avec cet email existe déjà'
        } else if (error.message.includes('Configuration système')) {
          errorMessage = 'Configuration système incomplète. Contactez l\'administrateur.'
        } else {
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
    authApi.clearAuthData()
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