// Authentication API service for French database schema
import { CreateUserData, LoginData, AuthResponse, User, ApiError } from '@/types/auth'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class AuthApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'AuthApiError'
  }
}

class AuthApi {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // Add auth token if available
    const token = this.getStoredToken()
    if (token) {
      defaultHeaders.Authorization = `Bearer ${token}`
    }

    // Merge with provided headers
    const headers = { ...defaultHeaders, ...options.headers }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      let errorMessage = 'An error occurred'
      try {
        const errorData = await response.json() as ApiError
        errorMessage = errorData.detail || errorMessage
      } catch (e) {
        errorMessage = response.statusText || errorMessage
      }
      throw new AuthApiError(response.status, errorMessage)
    }

    return response.json()
  }

  private getStoredToken(): string | null {
    if (typeof window === 'undefined') return null
    
    // Try localStorage first
    const token = localStorage.getItem('access_token')
    if (token) return token
    
    // Fallback to cookies
    const cookies = document.cookie.split(';')
    const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('accessToken='))
    if (tokenCookie) {
      return tokenCookie.split('=')[1]
    }
    
    return null
  }

  private setStoredTokens(accessToken: string, refreshToken: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
    
    // Also set cookies for middleware
    document.cookie = `accessToken=${accessToken}; path=/; max-age=${7 * 24 * 60 * 60}` // 7 days
    document.cookie = `refreshToken=${refreshToken}; path=/; max-age=${7 * 24 * 60 * 60}` // 7 days
  }

  private clearStoredTokens(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    // Also clear cookies
    document.cookie = 'accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    document.cookie = 'refreshToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  }

  private setStoredUser(user: User): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('user', JSON.stringify(user))
  }

  private getStoredUser(): User | null {
    if (typeof window === 'undefined') return null
    try {
      const userData = localStorage.getItem('user')
      return userData ? JSON.parse(userData) : null
    } catch (e) {
      return null
    }
  }

  async login(credentials: LoginData): Promise<AuthResponse> {
    try {
      const response = await this.makeRequest<AuthResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      })

      // Store tokens and user data
      this.setStoredTokens(response.access_token, response.refresh_token)
      this.setStoredUser(response.user)

      return response
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  async register(userData: CreateUserData): Promise<User> {
    try {
      // Extract departmentId and other data
      const { departmentId, ...userDataWithoutDepartmentId } = userData as any
      
      // Build the URL with query parameter if departmentId is provided
      let url = '/auth/register'
      if (departmentId) {
        url += `?department_id=${departmentId}`
      }
      
      const response = await this.makeRequest<User>(url, {
        method: 'POST',
        body: JSON.stringify(userDataWithoutDepartmentId),
      })

      return response
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.makeRequest<User>('/auth/me', {
        method: 'GET',
      })

      // Update stored user data
      this.setStoredUser(response)
      return response
    } catch (error) {
      console.error('Get current user error:', error)
      // If token is invalid, clear stored data
      if (error instanceof AuthApiError && error.status === 401) {
        this.clearStoredTokens()
      }
      throw error
    }
  }

  async getAllUsers(): Promise<User[]> {
    try {
      const response = await this.makeRequest<User[]>('/auth/users', {
        method: 'GET',
      })

      return response
    } catch (error) {
      console.error('Get all users error:', error)
      throw error
    }
  }

  logout(): void {
    this.clearStoredTokens()
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken()
  }

  getUser(): User | null {
    return this.getStoredUser()
  }

  // Helper method to format user display name
  getUserDisplayName(user: User): string {
    return `${user.prenom} ${user.nom}`
  }

  // Helper method to get role display name
  getRoleDisplayName(role: string): string {
    const roleNames = {
      STUDENT: 'Étudiant',
      TEACHER: 'Enseignant',
      DEPARTMENT_HEAD: 'Chef de Département',
      ADMIN: 'Administrateur'
    }
    return roleNames[role as keyof typeof roleNames] || role
  }

  // Fetch all departments
  async getDepartments(): Promise<any[]> {
    try {
      const response = await this.makeRequest<any[]>('/departments/', {
        method: 'GET',
      })
      return response
    } catch (error) {
      console.error('Get departments error:', error)
      throw error
    }
  }

  // Fetch all students
  async getStudents(filters?: { department_id?: string; specialty_id?: string; academic_year?: string }): Promise<User[]> {
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value)
        })
      }
      
      const url = `/admin/students/${params.toString() ? '?' + params.toString() : ''}`
      const response = await this.makeRequest<User[]>(url, {
        method: 'GET',
      })
      return response
    } catch (error) {
      console.error('Get students error:', error)
      throw error
    }
  }

  // Fetch all teachers
  async getTeachers(filters?: { department_id?: string; specialty_id?: string }): Promise<User[]> {
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value)
        })
      }
      
      const url = `/admin/teachers/${params.toString() ? '?' + params.toString() : ''}`
      const response = await this.makeRequest<User[]>(url, {
        method: 'GET',
      })
      return response
    } catch (error) {
      console.error('Get teachers error:', error)
      throw error
    }
  }

  // Fetch all department heads
  async getDepartmentHeads(filters?: { department_id?: string }): Promise<any[]> {
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value)
        })
      }
      
      const url = `/admin/department-heads/${params.toString() ? '?' + params.toString() : ''}`
      const response = await this.makeRequest<any[]>(url, {
        method: 'GET',
      })
      return response
    } catch (error) {
      console.error('Get department heads error:', error)
      throw error
    }
  }
}

export const authApi = new AuthApi()
export { AuthApiError }