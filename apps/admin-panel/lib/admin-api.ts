// Secure Admin Panel API Integration
const ADMIN_API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_URL || 'http://127.0.0.1:8000';

// Admin-only auth token storage
let adminAuthToken: string | null = null;

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface AdminLoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AdminUser;
}

export interface AdminUser {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  role: 'ADMIN';
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

// Secure HTTP Client with enhanced security
class SecureAdminApiClient {
  private baseURL: string;
  private maxRetries: number = 3;
  private timeout: number = 30000; // 30 seconds
  
  constructor(baseURL: string = ADMIN_API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-Admin-Client': 'true',
      'X-Requested-With': 'AdminPanel',
    };
    
    if (adminAuthToken) {
      headers['Authorization'] = `Bearer ${adminAuthToken}`;
    }
    
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();
      
      if (response.ok) {
        return { success: true, data };
      } else {
        // Handle unauthorized access
        if (response.status === 401 || response.status === 403) {
          this.logout();
          throw new Error('Admin access denied. Please re-authenticate.');
        }
        
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

  private async makeRequest<T>(
    method: string, 
    endpoint: string, 
    data?: any
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method,
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      return this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        return { success: false, error: 'Request timeout' };
      }
      
      return { 
        success: false, 
        error: `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.makeRequest<T>('GET', endpoint);
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.makeRequest<T>('POST', endpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.makeRequest<T>('PUT', endpoint, data);
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.makeRequest<T>('PATCH', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.makeRequest<T>('DELETE', endpoint);
  }

  // Admin logout with secure cleanup
  logout(): void {
    adminAuthToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('admin_auth_token');
      localStorage.removeItem('admin_user_data');
      // Clear any cached admin data
      sessionStorage.clear();
    }
  }
}

// Create secure admin API client instance
const secureAdminApiClient = new SecureAdminApiClient();

// Admin Authentication Functions
export const adminAuthApi = {
  // Secure admin login with enhanced validation
  async login(login: string, password: string): Promise<ApiResponse<AdminLoginResponse>> {
    // Pre-validate credentials format
    if (!login || login.length < 3) {
      return { success: false, error: 'Invalid admin login format' };
    }
    
    if (!password || password.length < 8) {
      return { success: false, error: 'Invalid password format' };
    }

    const result = await secureAdminApiClient.post<AdminLoginResponse>('/auth/login', { 
      login, 
      password 
    });
    
    if (result.success && result.data?.access_token) {
      // Verify this is actually an admin user
      if (result.data.user.role !== 'ADMIN') {
        return { success: false, error: 'Access denied. Admin privileges required.' };
      }
      
      adminAuthToken = result.data.access_token;
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('admin_auth_token', adminAuthToken);
        localStorage.setItem('admin_user_data', JSON.stringify(result.data.user));
        
        // Log admin access for security
        console.log(`Admin access granted: ${result.data.user.firstName} ${result.data.user.lastName} at ${new Date().toISOString()}`);
      }
    }
    
    return result;
  },

  // Get current admin user info
  async me(): Promise<ApiResponse<AdminUser>> {
    const result = await secureAdminApiClient.get<AdminUser>('/auth/me');
    
    // Double-check admin role
    if (result.success && result.data?.role !== 'ADMIN') {
      this.logout();
      return { success: false, error: 'Admin access revoked' };
    }
    
    return result;
  },

  // Secure logout
  logout(): void {
    secureAdminApiClient.logout();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  },

  // Initialize token from secure storage
  init(): boolean {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('admin_auth_token');
      const userData = localStorage.getItem('admin_user_data');
      
      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          if (user.role === 'ADMIN') {
            adminAuthToken = token;
            return true;
          } else {
            // Invalid role, clear storage
            this.logout();
            return false;
          }
        } catch (e) {
          this.logout();
          return false;
        }
      }
    }
    return false;
  },

  // Check if admin is authenticated
  isAuthenticated(): boolean {
    return !!adminAuthToken;
  },

  // Get stored admin user data
  getCurrentAdmin(): AdminUser | null {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('admin_user_data');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          return user.role === 'ADMIN' ? user : null;
        } catch (e) {
          return null;
        }
      }
    }
    return null;
  }
};

// Admin Management Functions
export const adminManagementApi = {
  // Dashboard Statistics
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    return secureAdminApiClient.get<DashboardStats>('/admin/dashboard/statistics');
  },

  // System Health
  async getSystemHealth(): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get('/admin/dashboard/system-health');
  },

  // Recent Activity
  async getRecentActivity(limit: number = 20): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/dashboard/recent-activity?limit=${limit}`);
  },

  // Search Users
  async searchUsers(query: string, role?: string, limit: number = 50): Promise<ApiResponse<any>> {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    if (role) params.append('role', role);
    return secureAdminApiClient.get(`/admin/dashboard/search?${params}`);
  }
};

// Student Management Functions
export const adminStudentApi = {
  async getAll(filters?: {
    department_id?: string;
    specialty_id?: string;
    academic_year?: string;
  }): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return secureAdminApiClient.get<any[]>(`/admin/students/?${params}`);
  },

  async getById(id: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/students/${id}`);
  },

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
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return secureAdminApiClient.post(`/admin/students/?${params}`, studentData);
  },

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
    return secureAdminApiClient.put(`/admin/students/${id}?${params}`);
  },

  async delete(id: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.delete(`/admin/students/${id}`);
  }
};

// Teacher Management Functions
export const adminTeacherApi = {
  async getAll(filters?: {
    department_id?: string;
    specialty_id?: string;
    academic_title?: string;
  }): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    return secureAdminApiClient.get<any[]>(`/admin/teachers/?${params}`);
  },

  async getById(id: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/teachers/${id}`);
  },

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
    return secureAdminApiClient.post(`/admin/teachers/?${params}`, teacherData);
  },

  async update(
    teacherId: string,
    teacherData: {
      firstName?: string;
      lastName?: string;
      email?: string;
      login?: string;
      password?: string;
    },
    options?: {
      department_id?: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    return secureAdminApiClient.put(`/admin/teachers/${teacherId}?${params}`, teacherData);
  },

  async delete(teacherId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.delete(`/admin/teachers/${teacherId}`);
  }
};

// Department Head Management
export const adminDeptHeadApi = {
  async getAll(): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get<any[]>('/admin/department-heads/');
  },

  async getById(id: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/department-heads/${id}`);
  },

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
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    Object.entries(options).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    return secureAdminApiClient.post(`/admin/department-heads/?${params}`, deptHeadData);
  },

  async updateUserInfo(
    deptHeadId: string, 
    userData: {
      firstName?: string;
      lastName?: string;
      email?: string;
      login?: string;
    }
  ): Promise<ApiResponse<any>> {
    return secureAdminApiClient.patch(`/admin/department-heads/${deptHeadId}/user`, userData);
  },

  async updateDepartment(
    deptHeadId: string,
    options: {
      department_id?: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (options.department_id) {
      params.append('department_id', options.department_id);
    }
    return secureAdminApiClient.put(`/admin/department-heads/${deptHeadId}?${params}`);
  },

  async delete(deptHeadId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.delete(`/admin/department-heads/${deptHeadId}`);
  },

  async assignFromTeacher(
    teacherId: string,
    options: {
      department_id: string;
    }
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    params.append('department_id', options.department_id);
    return secureAdminApiClient.post(`/admin/department-heads/assign-from-teacher/${teacherId}?${params}`);
  },

  async demoteToTeacher(deptHeadId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.post(`/admin/department-heads/${deptHeadId}/demote-to-teacher`);
  }
};

// University Structure Functions
export const adminUniversityApi = {
  async getDepartments(): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get('/departments/');
  },

  async getSpecialties(): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get('/specialties/');
  },

  async getLevelsBySpecialty(specialtyId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/levels/?specialty_id=${specialtyId}&page_size=100`);
  },

  async getGroupsByLevel(levelId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.get(`/admin/levels/${levelId}/groups`);
  }
};

// Schedule Management Functions
export const adminScheduleApi = {
  async getDepartmentSchedules(): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get('/schedules/department');
  },

  async getSchedulesByGroup(groupId: string, startDate?: string, endDate?: string): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return secureAdminApiClient.get(`/schedules/group/${groupId}?${params}`);
  },

  async createSchedule(scheduleData: {
    date: string;
    startTime: string;
    endTime: string;
    roomId: string;
    subjectId: string;
    groupId: string;
  }): Promise<ApiResponse<any>> {
    return secureAdminApiClient.post('/schedules/', scheduleData);
  },

  async updateSchedule(scheduleId: string, scheduleData: {
    date?: string;
    startTime?: string;
    endTime?: string;
    roomId?: string;
    subjectId?: string;
    status?: string;
  }): Promise<ApiResponse<any>> {
    return secureAdminApiClient.put(`/schedules/${scheduleId}`, scheduleData);
  },

  async deleteSchedule(scheduleId: string): Promise<ApiResponse<any>> {
    return secureAdminApiClient.delete(`/schedules/${scheduleId}`);
  },

  async checkConflicts(scheduleData: {
    date: string;
    startTime: string;
    endTime: string;
    roomId: string;
    subjectId: string;
    groupId: string;
    excludeScheduleId?: string;
  }): Promise<ApiResponse<any>> {
    return secureAdminApiClient.post('/schedules/check-conflicts', scheduleData);
  },

  async getRooms(): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get('/admin/rooms/');
  },

  async getSubjectsByLevel(levelId: string): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get(`/admin/subjects/?level_id=${levelId}`);
  },

  async getGroupsByDepartment(departmentId: string): Promise<ApiResponse<any[]>> {
    return secureAdminApiClient.get(`/admin/groups/?department_id=${departmentId}`);
  }
};

// Bulk Import Functions
export const adminBulkImportApi = {
  async importStudents(file: File): Promise<ApiResponse<{
    total: number;
    created: number;
    skipped: number;
    errors: string[];
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for file upload

    try {
      const headers: HeadersInit = {
        'X-Admin-Client': 'true',
        'X-Requested-With': 'AdminPanel',
      };
      
      if (adminAuthToken) {
        headers['Authorization'] = `Bearer ${adminAuthToken}`;
      }

      const response = await fetch(`${ADMIN_API_BASE_URL}/admin/bulk-import/students`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, data: data.details };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || 'Failed to import students' };
      }
    } catch (error) {
      clearTimeout(timeoutId);
      return { 
        success: false, 
        error: `Import failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  },

  async importTeachers(file: File): Promise<ApiResponse<{
    total: number;
    created: number;
    skipped: number;
    errors: string[];
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for file upload

    try {
      const headers: HeadersInit = {
        'X-Admin-Client': 'true',
        'X-Requested-With': 'AdminPanel',
      };
      
      if (adminAuthToken) {
        headers['Authorization'] = `Bearer ${adminAuthToken}`;
      }

      const response = await fetch(`${ADMIN_API_BASE_URL}/admin/bulk-import/teachers`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, data: data.details };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || 'Failed to import teachers' };
      }
    } catch (error) {
      clearTimeout(timeoutId);
      return { 
        success: false, 
        error: `Import failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
    }
  },

  async downloadStudentsTemplate(): Promise<void> {
    try {
      const headers: HeadersInit = {};
      
      if (adminAuthToken) {
        headers['Authorization'] = `Bearer ${adminAuthToken}`;
      }

      const response = await fetch(`${ADMIN_API_BASE_URL}/admin/bulk-import/template/students`, {
        headers
      });

      if (!response.ok) throw new Error('Failed to download template');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'students_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      throw new Error(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  async downloadTeachersTemplate(): Promise<void> {
    try {
      const headers: HeadersInit = {};
      
      if (adminAuthToken) {
        headers['Authorization'] = `Bearer ${adminAuthToken}`;
      }

      const response = await fetch(`${ADMIN_API_BASE_URL}/admin/bulk-import/template/teachers`, {
        headers
      });

      if (!response.ok) throw new Error('Failed to download template');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'teachers_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      throw new Error(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
};

// Initialize admin auth on import
if (typeof window !== 'undefined') {
  adminAuthApi.init();
}

export default secureAdminApiClient;