// Frontend Auth API Service  
// Handles all authentication API calls for different user roles

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Response Type
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// User Types (matching types/auth.ts)
export type Role = 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN';

export interface User {
  id: string;
  nom: string;        // lastName
  prenom: string;     // firstName
  email: string;
  login: string;      // Required field from types/auth.ts
  role: Role;
  createdAt?: string;
  updatedAt?: string;
  // Admin panel compatibility fields
  firstName?: string;
  lastName?: string;
}

export interface LoginCredentials {
  email?: string;
  login?: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// Registration Data Types
export interface BaseRegistrationData {
  nom: string;
  prenom: string;
  email: string;
  password: string;
  role: Role;
}

export interface DepartmentHeadRegistrationData extends BaseRegistrationData {
  role: 'DEPARTMENT_HEAD';
  department_id: string;
}

export interface TeacherRegistrationData extends BaseRegistrationData {
  role: 'TEACHER';
  department_id: string;
}

export interface StudentRegistrationData extends BaseRegistrationData {
  role: 'STUDENT';
  specialty_id?: string;
  group_id?: string;
}

// Academic Structure Types
export interface Department {
  id: string;
  nom: string;
}

export interface Specialty {
  id: string;
  nom: string;
  id_departement: string;
  departement?: { nom: string };
}

export interface Group {
  id: string;
  nom: string;
  niveau?: {
    nom: string;
    specialite: { nom: string };
  };
}

class AuthApiService {
  private getHeaders(token?: string): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();
      
      if (!response.ok) {
        return {
          success: false,
          error: data.detail || data.message || `HTTP ${response.status}: ${response.statusText}`
        };
      }
      
      // Ensure user objects have required login field
      if (data && typeof data === 'object') {
        if ('user' in data && data.user && !data.user.login) {
          data.user.login = data.user.email; // Fallback to email
        }
        if ('login' in data && !data.login && data.email) {
          data.login = data.email; // For single user responses
        }
      }
      
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  // Authentication Methods
  async login(credentials: LoginCredentials): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(credentials)
      });

      return this.handleResponse<LoginResponse>(response);
    } catch (error) {
      return {
        success: false,
        error: `Login failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  // Registration Methods
  async registerDepartmentHead(data: DepartmentHeadRegistrationData): Promise<ApiResponse<User>> {
    try {
      // Extract department_id and remove it from the body
      const { department_id, ...bodyData } = data;
      
      // Build URL with query parameter
      const url = `${API_BASE_URL}/auth/register?department_id=${encodeURIComponent(department_id)}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(bodyData)
      });

      return this.handleResponse<User>(response);
    } catch (error) {
      return {
        success: false,
        error: `Department head registration failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async registerTeacher(data: TeacherRegistrationData): Promise<ApiResponse<User>> {
    try {
      // Extract department_id and remove it from the body
      const { department_id, ...bodyData } = data;
      
      // Build URL with query parameter
      const url = `${API_BASE_URL}/auth/register?department_id=${encodeURIComponent(department_id)}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(bodyData)
      });

      return this.handleResponse<User>(response);
    } catch (error) {
      return {
        success: false,
        error: `Teacher registration failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async registerStudent(data: StudentRegistrationData): Promise<ApiResponse<User>> {
    try {
      // Extract specialty_id and group_id and remove them from the body
      const { specialty_id, group_id, ...bodyData } = data;
      
      // Build URL with query parameters
      const params = new URLSearchParams();
      if (specialty_id) params.append('specialty_id', specialty_id);
      if (group_id) params.append('group_id', group_id);
      
      const url = `${API_BASE_URL}/auth/register${params.toString() ? '?' + params.toString() : ''}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(bodyData)
      });

      return this.handleResponse<User>(response);
    } catch (error) {
      return {
        success: false,
        error: `Student registration failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  // Academic Structure Methods
  async getDepartments(): Promise<ApiResponse<Department[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/departments`, {
        method: 'GET',
        headers: this.getHeaders()
      });

      return this.handleResponse<Department[]>(response);
    } catch (error) {
      return {
        success: false,
        error: `Failed to fetch departments: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async getAvailableDepartments(): Promise<ApiResponse<Department[]>> {
    // For department heads, get departments without existing heads
    return this.getDepartments();
  }

  async getSpecialties(): Promise<ApiResponse<Specialty[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/specialties`, {
        method: 'GET',
        headers: this.getHeaders()
      });

      return this.handleResponse<Specialty[]>(response);
    } catch (error) {
      return {
        success: false,
        error: `Failed to fetch specialties: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  async getGroups(specialty_id?: string): Promise<ApiResponse<Group[]>> {
    try {
      const url = specialty_id 
        ? `${API_BASE_URL}/auth/groups?specialty_id=${specialty_id}`
        : `${API_BASE_URL}/auth/groups`;
        
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders()
      });

      return this.handleResponse<Group[]>(response);
    } catch (error) {
      return {
        success: false,
        error: `Failed to fetch groups: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  // User Management Methods
  async getCurrentUser(token: string): Promise<ApiResponse<User>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: this.getHeaders(token)
      });

      return this.handleResponse<User>(response);
    } catch (error) {
      return {
        success: false,
        error: `Failed to get current user: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  // Helper Methods
  storeAuthData(loginResponse: LoginResponse): void {
    if (typeof window !== 'undefined') {
      // Ensure user has login field
      const user = {
        ...loginResponse.user,
        login: loginResponse.user.login || loginResponse.user.email
      };
      
      localStorage.setItem('authToken', loginResponse.access_token);
      localStorage.setItem('refreshToken', loginResponse.refresh_token);
      localStorage.setItem('userRole', user.role);
      localStorage.setItem('userInfo', JSON.stringify(user));
      
      // Also set as cookies for SSR/middleware support (7 days)
      const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString();
      document.cookie = `authToken=${loginResponse.access_token}; path=/; expires=${expires}; SameSite=Lax`;
      document.cookie = `userRole=${user.role}; path=/; expires=${expires}; SameSite=Lax`;
    }
  }

  getStoredToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken');
    }
    return null;
  }

  getStoredUser(): User | null {
    if (typeof window !== 'undefined') {
      const userInfo = localStorage.getItem('userInfo');
      return userInfo ? JSON.parse(userInfo) : null;
    }
    return null;
  }

  clearAuthData(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userRole');
      localStorage.removeItem('userInfo');
      
      // Also clear cookies
      document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'userRole=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  }

  isAuthenticated(): boolean {
    return !!this.getStoredToken();
  }
}

// Export singleton instance
export const authApi = new AuthApiService();

// Export the class for advanced usage
export { AuthApiService };