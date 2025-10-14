/**
 * Optimized Timetable API Client
 * 
 * This service integrates with the new optimized timetable system backend.
 * The system uses semester-based scheduling where:
 * - Chef de département creates student schedules (source of truth)
 * - Teacher schedules are auto-generated from student schedules
 * - Students and teachers have read-only access
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Types & Interfaces
// ============================================================================

export enum DayOfWeek {
  MONDAY = 'MONDAY',
  TUESDAY = 'TUESDAY',
  WEDNESDAY = 'WEDNESDAY',
  THURSDAY = 'THURSDAY',
  FRIDAY = 'FRIDAY',
  SATURDAY = 'SATURDAY'
}

export enum RecurrenceType {
  WEEKLY = 'WEEKLY',
  BIWEEKLY = 'BIWEEKLY'
}

export enum SessionStatus {
  PLANNED = 'PLANNED',
  CANCELED = 'CANCELED',
  MAKEUP = 'MAKEUP',
  COMPLETED = 'COMPLETED'
}

export interface SemesterScheduleCreate {
  matiere_id: string;
  groupe_id: string;
  enseignant_id: string;
  salle_id: string;
  day_of_week: DayOfWeek;
  start_time: string; // Format: "08:30"
  end_time: string;   // Format: "10:00"
  recurrence_type: RecurrenceType;
  semester_start: string; // Format: "2025-09-01"
  semester_end: string;   // Format: "2025-12-31"
}

export interface SemesterScheduleResponse {
  success: boolean;
  created_count: number;
  schedule_ids: string[];
  conflicts_count: number;
  conflicts?: ConflictInfo[];
}

export interface ConflictInfo {
  type: 'room' | 'teacher' | 'group';
  message: string;
  date: string;
  start_time: string;
  end_time: string;
}

export interface TimetableSession {
  id: string;
  date: string;
  start_time: string;
  end_time: string;
  status: SessionStatus;
  matiere: {
    id: string;
    nom: string;
    code?: string;
  };
  groupe: {
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  };
  enseignant: {
    id: string;
    nom: string;
    prenom: string;
    email: string;
  };
  salle: {
    id: string;
    code: string;
    type: string;
    capacite: number;
  };
}

export interface DaySchedule {
  [day: string]: TimetableSession[];
}

export interface TimetableResponse {
  week_start: string;
  week_end: string;
  timetable: DaySchedule;
  total_hours: string;
  note?: string;
}

export interface TodayScheduleResponse {
  date: string;
  day_name: string;
  sessions: TimetableSession[];
  total_sessions: number;
}

export interface AvailableResources {
  matieres: Array<{
    id: string;
    nom: string;
    code: string;
  }>;
  groupes: Array<{
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  }>;
  enseignants: Array<{
    id: string;
    nom: string;
    prenom: string;
    email: string;
  }>;
  salles: Array<{
    id: string;
    code: string;
    type: string;
    capacite: number;
  }>;
}

export interface SessionUpdate {
  date?: string;
  start_time?: string;
  end_time?: string;
  salle_id?: string;
  status?: SessionStatus;
}

// ============================================================================
// API Client Class
// ============================================================================

class TimetableAPIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Get authorization headers with token
   */
  private getHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
    
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Handle API responses and errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  // ==========================================================================
  // Department Head Endpoints (Create & Manage)
  // ==========================================================================

  /**
   * Create entire semester schedule from template
   * One API call creates 15+ sessions for the whole semester
   */
  async createSemesterSchedule(data: SemesterScheduleCreate): Promise<SemesterScheduleResponse> {
    const response = await fetch(`${this.baseURL}/timetables/semester`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse<SemesterScheduleResponse>(response);
  }

  /**
   * Get available resources for schedule creation
   * Returns all matieres, groupes, enseignants, and salles for the department
   */
  async getAvailableResources(): Promise<AvailableResources> {
    const response = await fetch(`${this.baseURL}/timetables/resources/available`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<AvailableResources>(response);
  }

  /**
   * Get department's full semester schedule
   * Groups all sessions by week and day
   */
  async getDepartmentSemesterSchedule(
    semester_start: string,
    semester_end: string
  ): Promise<{ weeks: Array<{ week_start: string; week_end: string; sessions: TimetableSession[] }> }> {
    const response = await fetch(
      `${this.baseURL}/timetables/department/semester?semester_start=${semester_start}&semester_end=${semester_end}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse(response);
  }

  /**
   * Update a single session (change time, room, or cancel)
   */
  async updateSession(sessionId: string, updates: SessionUpdate): Promise<TimetableSession> {
    const response = await fetch(`${this.baseURL}/timetables/${sessionId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(updates)
    });
    return this.handleResponse<TimetableSession>(response);
  }

  /**
   * Cancel a session (marks as CANCELED)
   */
  async cancelSession(sessionId: string, reason?: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseURL}/timetables/${sessionId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
      body: JSON.stringify({ reason })
    });
    return this.handleResponse(response);
  }

  // ==========================================================================
  // Student Endpoints (Read-Only)
  // ==========================================================================

  /**
   * Get student's weekly schedule (organized by day)
   */
  async getStudentWeeklySchedule(week_start: string): Promise<TimetableResponse> {
    const response = await fetch(
      `${this.baseURL}/timetables/student/weekly?week_start=${week_start}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse<TimetableResponse>(response);
  }

  /**
   * Get student's classes for today
   */
  async getStudentTodaySchedule(): Promise<TodayScheduleResponse> {
    const response = await fetch(`${this.baseURL}/timetables/student/today`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<TodayScheduleResponse>(response);
  }

  // ==========================================================================
  // Teacher Endpoints (Read-Only, Auto-Generated)
  // ==========================================================================

  /**
   * Get teacher's weekly schedule (auto-generated from student schedules)
   */
  async getTeacherWeeklySchedule(week_start: string): Promise<TimetableResponse> {
    const response = await fetch(
      `${this.baseURL}/timetables/teacher/weekly?week_start=${week_start}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse<TimetableResponse>(response);
  }

  /**
   * Get teacher's classes for today (auto-generated)
   */
  async getTeacherTodaySchedule(): Promise<TodayScheduleResponse> {
    const response = await fetch(`${this.baseURL}/timetables/teacher/today`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<TodayScheduleResponse>(response);
  }

  /**
   * Get weekly schedule for a specific group (for department heads)
   */
  async getGroupWeeklySchedule(groupId: string, week_start: string): Promise<TimetableResponse> {
    const response = await fetch(
      `${this.baseURL}/timetables/group/${groupId}/weekly?week_start=${week_start}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse<TimetableResponse>(response);
  }

  async getGroupSemesterSchedule(groupId: string, semester_start?: string, semester_end?: string) {
    const params = new URLSearchParams();
    if (semester_start) params.append('semester_start', semester_start);
    if (semester_end) params.append('semester_end', semester_end);
    
    const response = await fetch(
      `${this.baseURL}/timetables/group/${groupId}/semester?${params.toString()}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse(response);
  }

  // ==========================================================================
  // Utility Functions
  // ==========================================================================

  /**
   * Calculate week start date (Monday) from any date
   */
  getWeekStart(date: Date = new Date()): string {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust for Sunday
    d.setDate(diff);
    return d.toISOString().split('T')[0];
  }

  /**
   * Get next week's Monday
   */
  getNextWeekStart(): string {
    const today = new Date();
    today.setDate(today.getDate() + 7);
    return this.getWeekStart(today);
  }

  /**
   * Get previous week's Monday
   */
  getPreviousWeekStart(currentWeekStart: string): string {
    const date = new Date(currentWeekStart);
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  }

  /**
   * Format time for API (HH:MM format)
   */
  formatTime(time: string): string {
    // Ensure format is HH:MM
    const parts = time.split(':');
    if (parts.length >= 2) {
      return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`;
    }
    return time;
  }

  /**
   * Convert French day names to DayOfWeek enum
   */
  frenchDayToDayOfWeek(frenchDay: string): DayOfWeek {
    const mapping: Record<string, DayOfWeek> = {
      'lundi': DayOfWeek.MONDAY,
      'mardi': DayOfWeek.TUESDAY,
      'mercredi': DayOfWeek.WEDNESDAY,
      'jeudi': DayOfWeek.THURSDAY,
      'vendredi': DayOfWeek.FRIDAY,
      'samedi': DayOfWeek.SATURDAY
    };
    return mapping[frenchDay.toLowerCase()] || DayOfWeek.MONDAY;
  }

  /**
   * Convert DayOfWeek enum to French day name
   */
  dayOfWeekToFrench(day: DayOfWeek): string {
    const mapping: Record<DayOfWeek, string> = {
      [DayOfWeek.MONDAY]: 'Lundi',
      [DayOfWeek.TUESDAY]: 'Mardi',
      [DayOfWeek.WEDNESDAY]: 'Mercredi',
      [DayOfWeek.THURSDAY]: 'Jeudi',
      [DayOfWeek.FRIDAY]: 'Vendredi',
      [DayOfWeek.SATURDAY]: 'Samedi'
    };
    return mapping[day] || 'Lundi';
  }

  /**
   * Get status label in French
   */
  getStatusLabel(status: SessionStatus): string {
    const labels: Record<SessionStatus, string> = {
      [SessionStatus.PLANNED]: 'Programmé',
      [SessionStatus.CANCELED]: 'Annulé',
      [SessionStatus.MAKEUP]: 'Rattrapage',
      [SessionStatus.COMPLETED]: 'Terminé'
    };
    return labels[status] || status;
  }

  /**
   * Get status badge color variant
   */
  getStatusVariant(status: SessionStatus): 'default' | 'destructive' | 'secondary' | 'outline' {
    const variants: Record<SessionStatus, 'default' | 'destructive' | 'secondary' | 'outline'> = {
      [SessionStatus.PLANNED]: 'outline',
      [SessionStatus.CANCELED]: 'destructive',
      [SessionStatus.MAKEUP]: 'secondary',
      [SessionStatus.COMPLETED]: 'default'
    };
    return variants[status] || 'outline';
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const TimetableAPI = new TimetableAPIClient();
export default TimetableAPI;
