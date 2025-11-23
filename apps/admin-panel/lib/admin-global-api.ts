// Admin Global CRUD API Client
const ADMIN_API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_URL || 'http://127.0.0.1:8000';

let adminAuthToken: string | null = null;

// Initialize token from storage
if (typeof window !== 'undefined') {
  adminAuthToken = localStorage.getItem('admin_auth_token');
}

// Base fetch with auth
async function adminFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (adminAuthToken) {
    headers['Authorization'] = `Bearer ${adminAuthToken}`;
  }

  const response = await fetch(`${ADMIN_API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// GLOBAL CRUD API
// ============================================================================

export const globalCrudApi = {
  // Global Lookup
  lookup: {
    async search(q: string, entity?: 'teachers' | 'students' | 'all', limit = 10) {
      const query = new URLSearchParams({ q, limit: limit.toString() });
      if (entity) query.append('entity', entity);
      return adminFetch<any>(`/admin/global/lookup?${query}`);
    },
  },

  // Departments
  departments: {
    async list(params?: { skip?: number; limit?: number; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/departments?${query}`);
    },
    async get(id: string) {
      return adminFetch<any>(`/admin/global/departments/${id}`);
    },
    async create(data: { nom: string }) {
      return adminFetch<any>('/admin/global/departments', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: { nom?: string }) {
      return adminFetch<any>(`/admin/global/departments/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/departments/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Specialties
  specialties: {
    async list(params?: { skip?: number; limit?: number; department_id?: string; level_id?: string; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.department_id) query.append('department_id', params.department_id);
      if (params?.level_id) query.append('level_id', params.level_id);
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/specialties?${query}`);
    },
    async create(data: { nom: string; id_departement: string }) {
      return adminFetch<any>('/admin/global/specialties', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: { nom?: string; id_departement?: string }) {
      return adminFetch<any>(`/admin/global/specialties/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/specialties/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Levels
  levels: {
    async list(params?: { department_id?: string; specialty_id?: string; skip?: number; limit?: number }) {
      const query = new URLSearchParams();
      if (params?.department_id) query.append('department_id', params.department_id);
      if (params?.specialty_id) query.append('specialty_id', params.specialty_id);
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      return adminFetch<any>(`/admin/global/levels?${query}`);
    },
    async create(data: { nom: string; id_specialite: string }) {
      return adminFetch<any>('/admin/global/levels', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: { nom?: string; id_specialite?: string }) {
      return adminFetch<any>(`/admin/global/levels/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/levels/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Groups
  groups: {
    async list(params?: { level_id?: string; skip?: number; limit?: number }) {
      const query = new URLSearchParams();
      if (params?.level_id) query.append('level_id', params.level_id);
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      return adminFetch<any>(`/admin/global/groups?${query}`);
    },
    async create(data: { nom: string; id_niveau: string }) {
      return adminFetch<any>('/admin/global/groups', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  // Rooms
  rooms: {
    async list(params?: { skip?: number; limit?: number; type?: string; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.type) query.append('type', params.type);
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/rooms?${query}`);
    },
    async create(data: { code: string; type: string; capacite: number }) {
      return adminFetch<any>('/admin/global/rooms', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: { code?: string; type?: string; capacite?: number }) {
      return adminFetch<any>(`/admin/global/rooms/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/rooms/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Teachers
  teachers: {
    async list(params?: { skip?: number; limit?: number; department_id?: string; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.department_id) query.append('department_id', params.department_id);
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/teachers?${query}`);
    },
    async get(id: string) {
      return adminFetch<any>(`/admin/global/teachers/${id}`);
    },
    async search(q: string, limit = 20) {
      const query = new URLSearchParams({ q, limit: limit.toString() });
      return adminFetch<any>(`/admin/global/teachers/search?${query}`);
    },
    async create(data: {
      nom: string;
      prenom: string;
      email: string;
      id_departement: string;
      password: string;
      image_url?: string;
    }) {
      return adminFetch<any>('/admin/global/teachers', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: {
      nom?: string;
      prenom?: string;
      email?: string;
      id_departement?: string;
      image_url?: string;
    }) {
      return adminFetch<any>(`/admin/global/teachers/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/teachers/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Students
  students: {
    async list(params?: { skip?: number; limit?: number; department_id?: string; specialty_id?: string; level_id?: string; group_id?: string; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.department_id) query.append('department_id', params.department_id);
      if (params?.specialty_id) query.append('specialty_id', params.specialty_id);
      if (params?.level_id) query.append('level_id', params.level_id);
      if (params?.group_id) query.append('group_id', params.group_id);
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/students?${query}`);
    },
    async get(id: string) {
      return adminFetch<any>(`/admin/global/students/${id}`);
    },
    async search(q: string, limit = 20) {
      const query = new URLSearchParams({ q, limit: limit.toString() });
      return adminFetch<any>(`/admin/global/students/search?${query}`);
    },
    async create(data: {
      nom: string;
      prenom: string;
      email: string;
      id_groupe: string;
      id_specialite: string;
      id_niveau?: string;
      password: string;
    }) {
      return adminFetch<any>('/admin/global/students', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: {
      nom?: string;
      prenom?: string;
      email?: string;
      id_groupe?: string;
      id_specialite?: string;
      id_niveau?: string;
    }) {
      return adminFetch<any>(`/admin/global/students/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/students/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },

  // Subjects
  subjects: {
    async list(params?: { skip?: number; limit?: number; specialty_id?: string; teacher_id?: string; search?: string }) {
      const query = new URLSearchParams();
      if (params?.skip) query.append('skip', params.skip.toString());
      if (params?.limit) query.append('limit', params.limit.toString());
      if (params?.specialty_id) query.append('specialty_id', params.specialty_id);
      if (params?.teacher_id) query.append('teacher_id', params.teacher_id);
      if (params?.search) query.append('search', params.search);
      return adminFetch<any>(`/admin/global/subjects?${query}`);
    },
    async create(data: {
      nom: string;
      coefficient: number;
      semester?: string;
      id_departement: string;
      id_niveau: string;
      id_specialite: string;
      id_enseignant?: string;
    }) {
      return adminFetch<any>('/admin/global/subjects', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async update(id: string, data: {
      nom?: string;
      coefficient?: number;
      semester?: string;
      id_departement?: string;
      id_niveau?: string;
      id_specialite?: string;
      id_enseignant?: string;
    }) {
      return adminFetch<any>(`/admin/global/subjects/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    async delete(id: string, force = false) {
      return adminFetch<any>(`/admin/global/subjects/${id}?force=${force}`, {
        method: 'DELETE',
      });
    },
  },
};

// ============================================================================
// TIMETABLE SUPERVISION API
// ============================================================================

export const timetableApi = {
  // Sessions
  sessions: {
    async list(params?: {
      start_date?: string;
      end_date?: string;
      department_id?: string;
      teacher_id?: string;
      room_id?: string;
      group_id?: string;
      specialty_id?: string;
      status?: string;
      skip?: number;
      limit?: number;
    }) {
      const query = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined) query.append(key, value.toString());
        });
      }
      return adminFetch<any>(`/admin/timetable/sessions?${query}`);
    },

    async get(id: string) {
      return adminFetch<any>(`/admin/timetable/sessions/${id}`);
    },

    async create(data: {
      date: string;
      start_time: string;
      end_time: string;
      subject_id: string;
      group_id: string;
      teacher_id: string;
      room_id: string;
      semester?: string;
      is_recurring?: boolean;
      recurrence_weeks?: number;
    }) {
      return adminFetch<any>('/admin/timetable/sessions', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    async bulkCreate(data: {
      sessions: Array<{
        date: string;
        start_time: string;
        end_time: string;
        subject_id: string;
        group_id: string;
        teacher_id: string;
        room_id: string;
      }>;
      check_conflicts?: boolean;
    }) {
      return adminFetch<any>('/admin/timetable/sessions/bulk', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    async update(id: string, data: {
      date?: string;
      start_time?: string;
      end_time?: string;
      subject_id?: string;
      group_id?: string;
      teacher_id?: string;
      room_id?: string;
      status?: string;
    }, params?: { check_conflicts?: boolean; force?: boolean }) {
      const query = new URLSearchParams();
      if (params?.check_conflicts !== undefined) query.append('check_conflicts', params.check_conflicts.toString());
      if (params?.force !== undefined) query.append('force', params.force.toString());
      return adminFetch<any>(`/admin/timetable/sessions/${id}?${query}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    async delete(id: string, cascade = false) {
      return adminFetch<any>(`/admin/timetable/sessions/${id}?cascade=${cascade}`, {
        method: 'DELETE',
      });
    },

    async checkConflicts(data: {
      date: string;
      start_time: string;
      end_time: string;
      subject_id: string;
      group_id: string;
      teacher_id: string;
      room_id: string;
    }) {
      return adminFetch<any>('/admin/timetable/sessions/check-conflicts', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  // Analytics
  analytics: {
    async overview(params?: { start_date?: string; end_date?: string }) {
      const query = new URLSearchParams();
      if (params?.start_date) query.append('start_date', params.start_date);
      if (params?.end_date) query.append('end_date', params.end_date);
      return adminFetch<any>(`/admin/timetable/analytics/overview?${query}`);
    },
  },
};

// ============================================================================
// AUTH HELPERS
// ============================================================================

export const setAuthToken = (token: string) => {
  adminAuthToken = token;
  if (typeof window !== 'undefined') {
    localStorage.setItem('admin_auth_token', token);
  }
};

export const clearAuthToken = () => {
  adminAuthToken = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('admin_auth_token');
    localStorage.removeItem('admin_user_data');
  }
};

export const getAuthToken = () => adminAuthToken;
