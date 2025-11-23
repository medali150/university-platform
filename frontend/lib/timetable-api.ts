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
    const token = typeof window !== 'undefined' ? (localStorage.getItem('authToken') || localStorage.getItem('auth_token')) : null;
    
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

      console.log('🔍 Fetching schedule with params:', {
        group_id: groupId,
        date_from: weekStart,
        date_to: weekEnd,
        url: `${this.baseURL}/department-head/timetable/schedules?${params.toString()}`
      });

      const response = await fetch(
        `${this.baseURL}/department-head/timetable/schedules?${params.toString()}`,
        { headers: this.getHeaders() }
      );

      const data = await this.handleResponse<any[]>(response);
      
      console.log(`📥 Received ${data.length} schedules from API:`, data);

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
        console.log('Processing schedule:', {
          id: schedule.id,
          date: schedule.date,
          dayName,
          heure_debut: schedule.heure_debut,
          heure_debut_type: typeof schedule.heure_debut,
          heure_fin: schedule.heure_fin,
          heure_fin_type: typeof schedule.heure_fin,
          matiere: schedule.matiere?.nom,
          enseignant: schedule.enseignant?.utilisateur
        });
        
        if (dayName && timetable[dayName]) {
          // Extract time from datetime objects (heure_debut and heure_fin are DateTime in Prisma)
          // The backend sends these as ISO strings like "2024-01-15T14:30:00.000Z"
          let startTime = '';
          let endTime = '';
          
          if (schedule.heure_debut) {
            console.log('🕐 Raw heure_debut:', schedule.heure_debut);
            // Try parsing as Date first, fallback to direct string
            try {
              const date = new Date(schedule.heure_debut);
              if (!isNaN(date.getTime())) {
                // Format as HH:MM (24-hour format)
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                startTime = `${hours}:${minutes}`;
                console.log('  ✓ Parsed as Date:', startTime);
              } else {
                // It's already a time string (HH:MM:SS or HH:MM)
                startTime = schedule.heure_debut.substring(0, 5);
                console.log('  ✓ Used as string:', startTime);
              }
            } catch (e) {
              console.log('  ⚠️ Parse error, using substring:', e);
              startTime = schedule.heure_debut.substring(0, 5);
            }
          }
          
          if (schedule.heure_fin) {
            console.log('🕑 Raw heure_fin:', schedule.heure_fin);
            try {
              const date = new Date(schedule.heure_fin);
              if (!isNaN(date.getTime())) {
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                endTime = `${hours}:${minutes}`;
                console.log('  ✓ Parsed as Date:', endTime);
              } else {
                endTime = schedule.heure_fin.substring(0, 5);
                console.log('  ✓ Used as string:', endTime);
              }
            } catch (e) {
              console.log('  ⚠️ Parse error, using substring:', e);
              endTime = schedule.heure_fin.substring(0, 5);
            }
          }
          
          console.log('⏰ Final parsed times:', { startTime, endTime });
          
          // Handle teacher name - check if utilisateur exists
          let teacherName = 'Unknown';
          if (schedule.enseignant) {
            if (schedule.enseignant.utilisateur) {
              teacherName = `${schedule.enseignant.utilisateur.nom} ${schedule.enseignant.utilisateur.prenom}`;
            } else if (schedule.enseignant.nom && schedule.enseignant.prenom) {
              teacherName = `${schedule.enseignant.nom} ${schedule.enseignant.prenom}`;
            }
          }
          
          const sessionData = {
            id: schedule.id,
            subject: schedule.matiere?.nom || 'Unknown',
            teacher: teacherName,
            room: schedule.salle?.nom || schedule.salle?.code || 'Unknown',
            startTime: startTime,
            endTime: endTime,
            group: schedule.groupe?.nom || ''
          };
          
          console.log('Adding session to timetable:', dayName, sessionData);
          timetable[dayName].push(sessionData);
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
    // Parse date in UTC to avoid timezone issues
    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    const dayIndex = date.getDay();
    const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
    const dayName = days[dayIndex];
    
    console.log(`📅 Date conversion: ${dateStr} (${year}-${month}-${day}) -> day ${dayIndex} -> ${dayName}`);
    
    return dayName === 'Dimanche' ? null : dayName;
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