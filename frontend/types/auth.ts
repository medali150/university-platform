// Authentication types for French database schema

export type Role = 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN'

// User types - French schema
export interface User {
  id: string
  nom: string        // lastName
  prenom: string     // firstName
  email: string
  login: string
  role: Role
  createdAt?: string
  updatedAt?: string
}

export interface CreateUserData {
  nom: string        // lastName
  prenom: string     // firstName
  email: string
  password: string
  role: Role
  // Optional role-specific assignments
  departmentId?: string
  specialtyId?: string
  levelId?: string
}

export interface LoginData {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface AuthContextType {
  user: User | null
  login: (credentials: LoginData) => Promise<void>
  register: (userData: CreateUserData) => Promise<void>
  logout: () => void
  loading: boolean
  isAuthenticated: boolean
}

// Form validation types
export interface LoginFormData {
  email: string
  password: string
}

export interface RegisterFormData {
  nom: string
  prenom: string
  email: string
  password: string
  confirmPassword: string
  role: Role
  // Optional role-specific selections (used in UI)
  departmentId?: string
  specialtyId?: string
  levelId?: string
}

// API Error types
export interface ApiError {
  detail: string
  status?: number
}