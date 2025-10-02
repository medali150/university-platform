// Student API Service
import { getAuthHeaders } from './api';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface StudentSchedule {
  id: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  status: string;
  matiere: {
    id: string;
    nom: string;
  };
  enseignant: {
    id: string;
    nom: string;
    prenom: string;
  };
  salle: {
    id: string;
    code: string;
    type: string;
  };
  groupe?: {
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  };
  absence?: {
    id: string | null;
    status: string | null;
    motif: string | null;
    is_absent: boolean;
  } | null;
}

export interface StudentProfile {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  image_url?: string;
  groupe: {
    id: string;
    nom: string;
    niveau: {
      id: string;
      nom: string;
      specialite: {
        id: string;
        nom: string;
        departement: {
          id: string;
          nom: string;
        };
      };
    };
  };
  specialite: {
    id: string;
    nom: string;
  };
}

export interface StudentScheduleResponse {
  schedules: StudentSchedule[];
  student_info: {
    id: string;
    nom: string;
    prenom: string;
    email: string;
    groupe: {
      id: string;
      nom: string;
    };
  };
  date_range: {
    start: string;
    end: string;
  };
}

export class StudentAPI {
  /**
   * Get student profile
   */
  static async getProfile(): Promise<StudentProfile> {
    const response = await fetch(`${BASE_URL}/student/profile`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get student schedule for a date range
   */
  static async getSchedule(startDate?: string, endDate?: string): Promise<StudentScheduleResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const url = `${BASE_URL}/student/schedule${params.toString() ? `?${params}` : ''}`;

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
   * Get student's schedule for today
   */
  static async getTodaySchedule(): Promise<StudentSchedule[]> {
    const response = await fetch(`${BASE_URL}/student/schedule/today`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Legacy method for backward compatibility
  static async getMySchedule(params?: { date_from?: string; date_to?: string }): Promise<StudentSchedule[]> {
    const startDate = params?.date_from;
    const endDate = params?.date_to;
    
    const response = await this.getSchedule(startDate, endDate);
    return response.schedules;
  }
}


