// FastAPI Backend API Integration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Auth token storage
let authToken: string | null = null;

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    role: string;
  };
}

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  role: 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN';
  createdAt: string;
  updatedAt: string;
}

export interface DashboardStats {
  overview: {
    totalUsers: number;
    totalStudents: number;
    totalTeachers: number;
    totalDepartmentHeads: number;
    recentRegistrations: number;
  };
  universityStructure: {
    faculties: number;
    departments: number;
    specialties: number;
    levels: number;
    groups: number;
  };
  roleDistribution: Record<string, number>;
  departmentStats: {
    studentsByDepartment: Record<string, number>;
    teachersByDepartment: Record<string, number>;
  };
}

// HTTP Client with error handling
class ApiClient {
  private baseURL: string;
  
  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
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

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { 
        success: false, 
        error: `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }
}

// Create API client instance
const apiClient = new ApiClient();

// Authentication Functions
export const authApi = {
  // Login user
  async login(login: string, password: string): Promise<ApiResponse<LoginResponse>> {
    const result = await apiClient.post<LoginResponse>('/auth/login', { login, password });
    
    if (result.success && result.data?.access_token) {
      authToken = result.data.access_token;
      localStorage.setItem('auth_token', authToken);
      localStorage.setItem('user_data', JSON.stringify(result.data.user));
    }
    
    return result;
  },

  // Register user
  async register(userData: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password: string;
    role: string;
  }): Promise<ApiResponse<User>> {
    return apiClient.post<User>('/auth/register', userData);
  },

  // Get current user
  async me(): Promise<ApiResponse<User>> {
    return apiClient.get<User>('/auth/me');
  },

  // Logout
  logout(): void {
    authToken = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  },

  // Initialize token from localStorage
  init(): void {
    if (typeof window !== 'undefined') {
      authToken = localStorage.getItem('auth_token');
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!authToken;
  },

  // Get stored user data
  getCurrentUser(): User | null {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    }
    return null;
  }
};

// Admin CRUD Functions
export const adminApi = {
  // Dashboard Statistics
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    return apiClient.get<DashboardStats>('/admin/dashboard/statistics');
  },

  // System Health
  async getSystemHealth(): Promise<ApiResponse<any>> {
    return apiClient.get('/admin/dashboard/system-health');
  },

  // Recent Activity
  async getRecentActivity(limit: number = 20): Promise<ApiResponse<any>> {
    return apiClient.get(`/admin/dashboard/recent-activity?limit=${limit}`);
  },

  // Search Users
  async searchUsers(query: string, role?: string, limit: number = 50): Promise<ApiResponse<any>> {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    if (role) params.append('role', role);
    return apiClient.get(`/admin/dashboard/search?${params}`);
  }
};

// Student Management Functions
export const studentApi = {
  // Get all students
  async getAll(filters?: {
    department_id?: string;
    specialty_id?: string;
    academic_year?: string;
  }): Promise<ApiResponse<User[]>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.get<User[]>(`/admin/students/?${params}`);
  },

  // Get student by ID
  async getById(id: string): Promise<ApiResponse<User>> {
    return apiClient.get<User>(`/admin/students/${id}`);
  },

  // Create student
  async create(
    studentData: {
      firstName: string;
      lastName: string;
      email: string;
      login: string;
      password: string;
      role: 'STUDENT';
    },
    options?: {
      specialty_id?: string;
      level_id?: string;
      group_id?: string;
    }
  ): Promise<ApiResponse<User>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.post<User>(`/admin/students/?${params}`, studentData);
  },

  // Update student
  async update(
    id: string,
    options?: {
      specialty_id?: string;
      level_id?: string;
      group_id?: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.put(`/admin/students/${id}?${params}`);
  },

  // Delete student
  async delete(id: string): Promise<ApiResponse<any>> {
    return apiClient.delete(`/admin/students/${id}`);
  }
};

// Teacher Management Functions
export const teacherApi = {
  // Get all teachers
  async getAll(filters?: {
    department_id?: string;
    specialty_id?: string;
    academic_title?: string;
  }): Promise<ApiResponse<User[]>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.get<User[]>(`/admin/teachers/?${params}`);
  },

  // Get teacher by ID
  async getById(id: string): Promise<ApiResponse<User>> {
    return apiClient.get<User>(`/admin/teachers/${id}`);
  },

  // Create teacher
  async create(
    teacherData: {
      firstName: string;
      lastName: string;
      email: string;
      login: string;
      password: string;
      role: 'TEACHER';
    },
    options?: {
      department_id?: string;
      academic_title?: string;
      years_of_experience?: number;
      specialty_ids?: string[];
    }
  ): Promise<ApiResponse<User>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }
    return apiClient.post<User>(`/admin/teachers/?${params}`, teacherData);
  },

  // Update teacher
  async update(
    id: string,
    options?: {
      department_id?: string;
      academic_title?: string;
      years_of_experience?: number;
      specialty_ids?: string[];
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }
    return apiClient.put(`/admin/teachers/${id}?${params}`);
  },

  // Delete teacher
  async delete(id: string): Promise<ApiResponse<any>> {
    return apiClient.delete(`/admin/teachers/${id}`);
  },

  // Add specialty to teacher
  async addSpecialty(teacherId: string, specialtyId: string): Promise<ApiResponse<any>> {
    return apiClient.post(`/admin/teachers/${teacherId}/specialties/${specialtyId}`);
  },

  // Remove specialty from teacher
  async removeSpecialty(teacherId: string, specialtyId: string): Promise<ApiResponse<any>> {
    return apiClient.delete(`/admin/teachers/${teacherId}/specialties/${specialtyId}`);
  }
};

// Department Head Management Functions
export const departmentHeadApi = {
  // Get all department heads
  async getAll(filters?: {
    department_id?: string;
  }): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.get<any[]>(`/admin/department-heads/?${params}`);
  },

  // Get department head by ID
  async getById(id: string): Promise<ApiResponse<any>> {
    return apiClient.get(`/admin/department-heads/${id}`);
  },

  // Create department head
  async create(
    deptHeadData: {
      firstName: string;
      lastName: string;
      email: string;
      login: string;
      password: string;
      role: 'DEPARTMENT_HEAD';
    },
    options: {
      department_id: string;
      appointment_date?: string;
    }
  ): Promise<ApiResponse<User>> {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    return apiClient.post<User>(`/admin/department-heads/?${params}`, deptHeadData);
  },

  // Update department head
  async update(
    id: string,
    options?: {
      department_id?: string;
      appointment_date?: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return apiClient.put(`/admin/department-heads/${id}?${params}`);
  },

  // Delete department head
  async delete(id: string): Promise<ApiResponse<any>> {
    return apiClient.delete(`/admin/department-heads/${id}`);
  },

  // Assign teacher as department head
  async assignFromTeacher(
    teacherId: string,
    options: {
      department_id: string;
      appointment_date?: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    return apiClient.post(`/admin/department-heads/assign-from-teacher/${teacherId}?${params}`);
  },

  // Demote department head to teacher
  async demoteToTeacher(id: string): Promise<ApiResponse<any>> {
    return apiClient.post(`/admin/department-heads/${id}/demote-to-teacher`);
  }
};

// University Structure Functions
export const universityApi = {
  // Get all departments
  async getDepartments(): Promise<ApiResponse<any[]>> {
    return apiClient.get('/departments/');
  },

  // Get all specialties
  async getSpecialties(): Promise<ApiResponse<any[]>> {
    return apiClient.get('/specialties/');
  },

  // Get levels by specialty
  async getLevelsBySpecialty(specialtyId: string): Promise<ApiResponse<any[]>> {
    return apiClient.get(`/specialties/${specialtyId}/levels`);
  },

  // Get groups by level
  async getGroupsByLevel(levelId: string): Promise<ApiResponse<any[]>> {
    return apiClient.get(`/levels/${levelId}/groups`);
  }
};

// Legacy compatibility functions (keeping for backward compatibility)
export async function getAuthToken(): Promise<string | null> {
  return authToken || localStorage.getItem('auth_token');
}

export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Unable to retrieve authentication token');
  }

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

export async function testApiMe(): Promise<any> {
  const result = await authApi.me();
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.error || 'Unknown error');
  }
}

// Initialize auth token on import
if (typeof window !== 'undefined') {
  authApi.init();
}

export default apiClient;