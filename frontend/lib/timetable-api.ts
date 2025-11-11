/**
 * Timetable API Client
 * 
 * This service handles all timetable-related API calls for the university system.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Types & Interfaces
// ============================================================================

export enum DayOfWeek {
  MONDAY = 'Lundi',
  TUESDAY = 'Mardi',
  WEDNESDAY = 'Mercredi',
  THURSDAY = 'Jeudi',
  FRIDAY = 'Vendredi',
  SATURDAY = 'Samedi'
}

export enum RecurrenceType {
  WEEKLY = 'WEEKLY',
  BIWEEKLY = 'BIWEEKLY'
}

export interface AvailableResources {
  subjects: Array<{
    id: string;
    nom: string;
    code: string;
  }>;
  groups: Array<{
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  }>;
  teachers: Array<{
    id: string;
    nom: string;
    prenom: string;
    email: string;
  }>;
  rooms: Array<{
    id: string;
    code: string;
    type: string;
    capacite: number;
  }>;
}

export interface TimetableResponse {
  [day: string]: Array<{
    id: string;
    subject: string;
    teacher: string;
    room: string;
    startTime: string;
    endTime: string;
    group?: string;
  }>;
}

export interface SemesterScheduleCreate {
  subject_id: string;
  group_id: string;
  teacher_id: string;
  room_id: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  recurrence: RecurrenceType;
  semester_start: string;
  semester_end: string;
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
  // Department Head Endpoints
  // ==========================================================================

  /**
   * Get available resources for schedule creation
   */
  async getAvailableResources(): Promise<AvailableResources> {
    try {
      const [subjectsRes, groupsRes, teachersRes, roomsRes] = await Promise.all([
        fetch(`${this.baseURL}/department-head/timetable/subjects`, { headers: this.getHeaders() }),
        fetch(`${this.baseURL}/department-head/timetable/groups`, { headers: this.getHeaders() }),
        fetch(`${this.baseURL}/department-head/teachers`, { headers: this.getHeaders() }),
        fetch(`${this.baseURL}/department-head/timetable/rooms`, { headers: this.getHeaders() })
      ]);

      const [subjects, groups, teachers, rooms] = await Promise.all([
        this.handleResponse<any[]>(subjectsRes),
        this.handleResponse<any[]>(groupsRes),
        this.handleResponse<any[]>(teachersRes),
        this.handleResponse<any[]>(roomsRes)
      ]);

      return { subjects, groups, teachers, rooms };
    } catch (error) {
      console.error('Error fetching resources:', error);
      throw error;
    }
  }

  /**
   * Get weekly schedule for a specific group
   */
  async getGroupWeeklySchedule(groupId: string, weekStart: string): Promise<TimetableResponse> {
    try {
      const weekEnd = this.getWeekEnd(weekStart);
      const params = new URLSearchParams({
        group_id: groupId,
        date_from: weekStart,
        date_to: weekEnd
      });

      const response = await fetch(
        `${this.baseURL}/department-head/timetable/schedules?${params.toString()}`,
        { headers: this.getHeaders() }
      );

      const data = await this.handleResponse<any[]>(response);

      // Transform backend data to timetable format
      const timetable: TimetableResponse = {
        Lundi: [],
        Mardi: [],
        Mercredi: [],
        Jeudi: [],
        Vendredi: [],
        Samedi: []
      };

      data.forEach((schedule: any) => {
        const dayName = this.getDayNameFromDate(schedule.date);
        if (dayName && timetable[dayName]) {
          // Extract time from datetime objects (heure_debut and heure_fin are DateTime in Prisma)
          const startTime = schedule.heure_debut ? new Date(schedule.heure_debut).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false }) : '';
          const endTime = schedule.heure_fin ? new Date(schedule.heure_fin).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', hour12: false }) : '';
          
          timetable[dayName].push({
            id: schedule.id,
            subject: schedule.matiere?.nom || 'Unknown',
            teacher: schedule.enseignant ? `${schedule.enseignant.nom} ${schedule.enseignant.prenom}` : 'Unknown',
            room: schedule.salle?.code || 'Unknown',
            startTime: startTime,
            endTime: endTime,
            group: schedule.groupe?.nom || ''
          });
        }
      });

      return timetable;
    } catch (error) {
      console.error('Error fetching group schedule:', error);
      throw error;
    }
  }

  /**
   * Create a semester schedule (creates recurring schedules for entire semester)
   */
  async createSemesterSchedule(data: SemesterScheduleCreate): Promise<{ success: boolean; message: string }> {
    try {
      // Calculate the specific date for this day in the current week
      const weekStart = new Date(data.semester_start);
      const dayIndex = this.getDayIndex(data.day_of_week);
      const scheduleDate = new Date(weekStart);
      scheduleDate.setDate(scheduleDate.getDate() + dayIndex);

      const scheduleData = {
        subject_id: data.subject_id,
        group_id: data.group_id,
        teacher_id: data.teacher_id,
        room_id: data.room_id,
        date: scheduleDate.toISOString().split('T')[0],
        start_time: data.start_time,
        end_time: data.end_time,
        recurrence: data.recurrence || 'WEEKLY',  // Default to WEEKLY recurrence
        semester_start: data.semester_start,
        semester_end: data.semester_end
      };

      const response = await fetch(`${this.baseURL}/department-head/timetable/schedules`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(scheduleData)
      });

      await this.handleResponse(response);
      return { success: true, message: 'Schedule created successfully' };
    } catch (error: any) {
      console.error('Error creating schedule:', error);
      throw error;
    }
  }

  /**
   * Update a single session
   */
  async updateSession(sessionId: string, updates: any): Promise<any> {
    const response = await fetch(`${this.baseURL}/department-head/timetable/schedules/${sessionId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(updates)
    });
    return this.handleResponse(response);
  }

  /**
   * Cancel a session
   */
  async cancelSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseURL}/department-head/timetable/schedules/${sessionId}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
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
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    d.setDate(diff);
    return d.toISOString().split('T')[0];
  }

  /**
   * Calculate week end date (Sunday) from week start
   */
  getWeekEnd(weekStart: string): string {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + 6);
    return d.toISOString().split('T')[0];
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
   * Get next week's Monday
   */
  getNextWeekStart(currentWeekStart: string): string {
    const date = new Date(currentWeekStart);
    date.setDate(date.getDate() + 7);
    return date.toISOString().split('T')[0];
  }

  /**
   * Convert date to French day name
   */
  private getDayNameFromDate(dateStr: string): string | null {
    const date = new Date(dateStr);
    const dayIndex = date.getDay();
    const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
    return days[dayIndex] === 'Dimanche' ? null : days[dayIndex];
  }

  /**
   * Get day index from French day name (0 = Monday)
   */
  private getDayIndex(dayName: string): number {
    const days: Record<string, number> = {
      'Lundi': 0,
      'Mardi': 1,
      'Mercredi': 2,
      'Jeudi': 3,
      'Vendredi': 4,
      'Samedi': 5
    };
    return days[dayName] || 0;
  }

  /**
   * Convert DayOfWeek enum to French day name
   */
  dayOfWeekToFrench(day: DayOfWeek): string {
    return day;
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const TimetableAPI = new TimetableAPIClient();
export default TimetableAPI;