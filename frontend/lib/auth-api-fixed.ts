// Frontend Auth API Service  
// Handles all authentication API calls for different user roles

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// API Response Type
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// User Types
export interface User {
  id: string;
  email: string;
  prenom: string;
  nom: string;
  role: 'ADMIN' | 'DEPARTMENT_HEAD' | 'TEACHER' | 'STUDENT';
  firstName?: string; // Admin panel compatibility
  lastName?: string;  // Admin panel compatibility
  login?: string;     // Admin panel compatibility
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
  role: 'ADMIN' | 'DEPARTMENT_HEAD' | 'TEACHER' | 'STUDENT';
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
      
      if (response.ok) {
        return { success: true, data };
      } else {
        return { 
          success: false, 
          error: data.detail || data.message || `HTTP ${response.status}` 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  // Authentication Methods
  async login(email: string, password: string): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ email, password }),
      });

      return this.handleResponse<LoginResponse>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Login failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async getCurrentUser(token: string): Promise<ApiResponse<User>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: this.getHeaders(token),
      });

      return this.handleResponse<User>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Failed to get user info: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  // Registration Methods
  async registerDepartmentHead(data: DepartmentHeadRegistrationData): Promise<ApiResponse<User>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register?department_id=${data.department_id}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          nom: data.nom,
          prenom: data.prenom,
          email: data.email,
          password: data.password,
          role: data.role,
        }),
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
      const response = await fetch(`${API_BASE_URL}/auth/register?department_id=${data.department_id}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          nom: data.nom,
          prenom: data.prenom,
          email: data.email,
          password: data.password,
          role: data.role,
        }),
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
      const params = new URLSearchParams();
      if (data.specialty_id) params.append('specialty_id', data.specialty_id);
      if (data.group_id) params.append('group_id', data.group_id);

      const url = `${API_BASE_URL}/auth/register${params.toString() ? '?' + params.toString() : ''}`;

      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          nom: data.nom,
          prenom: data.prenom,
          email: data.email,
          password: data.password,
          role: data.role,
        }),
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
        headers: this.getHeaders(),
      });

      const result = await this.handleResponse<{ departments: Department[] }>(response);
      
      if (result.success && result.data) {
        return { success: true, data: result.data.departments };
      }
      
      return { success: false, error: result.error };
    } catch (error) {
      return { 
        success: false, 
        error: `Failed to get departments: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async getAvailableDepartments(): Promise<ApiResponse<Department[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/available-departments`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      const result = await this.handleResponse<{ available_departments: Department[] }>(response);
      
      if (result.success && result.data) {
        return { success: true, data: result.data.available_departments };
      }
      
      return { success: false, error: result.error };
    } catch (error) {
      return { 
        success: false, 
        error: `Failed to get available departments: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async getSpecialties(department_id?: string): Promise<ApiResponse<Specialty[]>> {
    try {
      const params = department_id ? `?department_id=${department_id}` : '';
      const response = await fetch(`${API_BASE_URL}/auth/specialties${params}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      const result = await this.handleResponse<{ specialties: Specialty[] }>(response);
      
      if (result.success && result.data) {
        return { success: true, data: result.data.specialties };
      }
      
      return { success: false, error: result.error };
    } catch (error) {
      return { 
        success: false, 
        error: `Failed to get specialties: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async getGroups(specialty_id?: string): Promise<ApiResponse<Group[]>> {
    try {
      const params = specialty_id ? `?specialty_id=${specialty_id}` : '';
      const response = await fetch(`${API_BASE_URL}/auth/groups${params}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      const result = await this.handleResponse<{ groups: Group[] }>(response);
      
      if (result.success && result.data) {
        return { success: true, data: result.data.groups };
      }
      
      return { success: false, error: result.error };
    } catch (error) {
      return { 
        success: false, 
        error: `Failed to get groups: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }
}

// Export singleton instance
export const authApi = new AuthApiService();
export default authApi;