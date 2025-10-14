// Teacher Profile API Service
import { getAuthHeaders } from './api';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface TeacherSchedule {
  id: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  status: string;
  matiere: {
    id: string;
    nom: string;
  };
  groupe: {
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  };
  salle: {
    id: string;
    code: string;
    type: string;
  };
}

export interface TeacherScheduleResponse {
  schedules: TeacherSchedule[];
  teacher_info: {
    id: string;
    nom: string;
    prenom: string;
    email: string;
  };
  date_range: {
    start: string;
    end: string;
  };
}

export interface TeacherProfile {
  teacher_info: {
    id: string;
    nom: string;
    prenom: string;
    email: string;
    image_url?: string;
    createdAt: string;
  };
  department: {
    id: string;
    nom: string;
    specialties: {
      id: string;
      nom: string;
      levels: {
        id: string;
        nom: string;
      }[];
    }[];
  };
  department_head: {
    nom: string;
    prenom: string;
    email: string;
  } | null;
  subjects_taught: {
    id: string;
    nom: string;
    specialty: {
      id: string;
      nom: string;
    };
  }[];
}

export interface Department {
  id: string;
  nom: string;
  specialties: {
    id: string;
    nom: string;
    levels_count: number;
  }[];
  department_head: {
    nom: string;
    prenom: string;
    email: string;
  } | null;
}

export class TeacherAPI {
  /**
   * Get teacher profile
   */
  static async getProfile(): Promise<TeacherProfile> {
    const response = await fetch(`${BASE_URL}/teacher/profile`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get available departments
   */
  static async getDepartments(): Promise<Department[]> {
    const response = await fetch(`${BASE_URL}/teacher/departments`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Update teacher department
   */
  static async updateDepartment(departmentId: string): Promise<void> {
    const response = await fetch(`${BASE_URL}/teacher/profile/department`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ new_department_id: departmentId }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get teacher subjects
   */
  static async getSubjects(): Promise<any[]> {
    const response = await fetch(`${BASE_URL}/teacher/subjects`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Upload teacher profile image
   */
  static async uploadImage(file: File): Promise<{ success: boolean; message: string; image_url?: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const headers = getAuthHeaders();
    // Remove Content-Type header to let browser set it with boundary for multipart
    delete headers['Content-Type'];

    const response = await fetch(`${BASE_URL}/teacher/profile/upload-image`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Delete teacher profile image
   */
  static async deleteImage(): Promise<{ message: string }> {
    const response = await fetch(`${BASE_URL}/teacher/profile/image`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Update teacher profile information
   */
  static async updateProfile(data: {
    nom?: string;
    prenom?: string;
    email?: string;
    image_url?: string;
  }): Promise<any> {
    const response = await fetch(`${BASE_URL}/teacher/profile/info`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // ============================================================================
  // ABSENCE MANAGEMENT METHODS
  // ============================================================================

  /**
   * Get all groups that the teacher teaches
   */
  static async getGroups(): Promise<any[]> {
    const response = await fetch(`${BASE_URL}/teacher/groups`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get students in a specific group
   */
  static async getGroupStudents(groupId: string, scheduleId?: string): Promise<any> {
    const url = scheduleId 
      ? `${BASE_URL}/teacher/groups/${groupId}/students?schedule_id=${scheduleId}`
      : `${BASE_URL}/teacher/groups/${groupId}/students`;

    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Mark student absence
   */
  static async markAbsence(data: {
    student_id: string;
    schedule_id: string;
    is_absent: boolean;
    motif?: string;
  }): Promise<any> {
    const response = await fetch(`${BASE_URL}/teacher/absence/mark`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get teacher schedule for a date range
   */
  static async getSchedule(startDate?: string, endDate?: string): Promise<TeacherScheduleResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const url = `${BASE_URL}/teacher/schedule${params.toString() ? `?${params}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Ensure proper date formatting for all schedules
    if (data.schedules) {
      data.schedules = data.schedules.map((schedule: any) => ({
        ...schedule,
        date: new Date(schedule.date).toISOString().split('T')[0],
        heure_debut: schedule.heure_debut.substring(0, 5),
        heure_fin: schedule.heure_fin.substring(0, 5)
      }));
    }
    
    return data;
  }

  /**
   * Get today's schedule for the teacher
   */
  static async getTodaySchedule(): Promise<TeacherSchedule[]> {
    const response = await fetch(`${BASE_URL}/teacher/schedule/today`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Ensure proper date formatting
    return data.map((schedule: any) => ({
      ...schedule,
      date: new Date(schedule.date).toISOString().split('T')[0],
      heure_debut: schedule.heure_debut.substring(0, 5),
      heure_fin: schedule.heure_fin.substring(0, 5)
    }));
  }

  /**
   * Get teacher dashboard statistics
   */
  static async getStats(): Promise<TeacherStats> {
    const response = await fetch(`${BASE_URL}/teacher/stats`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get detailed information about all groups the teacher teaches
   */
  static async getGroupsDetailed(): Promise<TeacherGroupsResponse> {
    const response = await fetch(`${BASE_URL}/teacher/groups/detailed`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// Teacher statistics interfaces
export interface TeacherStats {
  today_classes: number
  pending_absences: number
  makeup_requests: number
  messages: number
}

// Teacher groups interfaces
export interface TeacherGroupStudent {
  id: string
  nom: string
  prenom: string
  email: string
}

export interface TeacherGroupSubject {
  id: string
  nom: string
}

export interface TeacherGroup {
  id: string
  nom: string
  level: string
  specialty: string
  department: string
  student_count: number
  students: TeacherGroupStudent[]
  subjects: TeacherGroupSubject[]
}

export interface TeacherGroupsResponse {
  groups: TeacherGroup[]
  total_groups: number
  total_students: number
}