import { 
  AuthResponse, 
  User, 
  Schedule, 
  Subject, 
  Group, 
  Room, 
  Department, 
  Specialty, 
  Level,
  Absence, 
  Makeup, 
  Message, 
  Conversation,
  PaginatedResponse,
  UserQuery,
  ScheduleQuery,
  AbsenceQuery,
  MessageQuery,
  Analytics,
  AnalyticsQuery,
  AutoGenerationResult
} from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

class ApiClient {
  private baseURL: string
  private tokenRefreshPromise: Promise<string> | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null
    // Check both keys for compatibility
    return localStorage.getItem('authToken') || localStorage.getItem('access_token')
  }

  private setToken(token: string): void {
    if (typeof window === 'undefined') return
    // Set both keys for compatibility
    localStorage.setItem('authToken', token)
    localStorage.setItem('access_token', token)
  }

  private removeToken(): void {
    if (typeof window === 'undefined') return
    // Remove all token keys
    localStorage.removeItem('authToken')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('user')
    localStorage.removeItem('userRole')
  }

  private async refreshToken(): Promise<string> {
    if (this.tokenRefreshPromise) {
      return this.tokenRefreshPromise
    }

    this.tokenRefreshPromise = this.performTokenRefresh()
    
    try {
      const newToken = await this.tokenRefreshPromise
      return newToken
    } finally {
      this.tokenRefreshPromise = null
    }
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = typeof window !== 'undefined' ? 
      localStorage.getItem('refresh_token') : null
    
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) {
      this.removeToken()
      throw new ApiError('Token refresh failed', response.status, response.statusText)
    }

    const data = await response.json()
    this.setToken(data.access_token)
    
    if (data.refresh_token && typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', data.refresh_token)
    }

    return data.access_token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getToken()

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    }

    let response = await fetch(url, config)

    // Handle token refresh on 401
    if (response.status === 401 && token) {
      try {
        const newToken = await this.refreshToken()
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${newToken}`,
        }
        response = await fetch(url, config)
      } catch (error) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        throw error
      }
    }

    if (!response.ok) {
      const errorText = await response.text()
      throw new ApiError(
        errorText || `HTTP ${response.status}`,
        response.status,
        response.statusText
      )
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return response.json()
    }

    return response.text() as T
  }

  // Authentication
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    this.setToken(response.access_token)
    if (typeof window !== 'undefined') {
      document.cookie = `refreshToken=${response.refresh_token}; path=/; httpOnly=false; secure=${location.protocol === 'https:'}; samesite=strict`
    }
    
    return response
  }

  async logout(): Promise<void> {
    try {
      await this.request('/auth/logout', { method: 'POST' })
    } catch (error) {
      // Ignore errors during logout
    } finally {
      this.removeToken()
    }
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me')
  }

  async register(userData: {
    prenom: string
    nom: string
    email: string
    login: string
    password: string
    role: string
    departmentId?: string
  }): Promise<AuthResponse> {
    // Build URL with query parameters for department heads and teachers
    let url = '/auth/register'
    if ((userData.role === 'DEPARTMENT_HEAD' || userData.role === 'TEACHER') && userData.departmentId) {
      url += `?department_id=${encodeURIComponent(userData.departmentId)}`
    }

    const { departmentId, ...requestBody } = userData
    const response = await this.request<AuthResponse>(url, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    })

    this.setToken(response.access_token)
    if (typeof window !== 'undefined') {
      document.cookie = `refreshToken=${response.refresh_token}; path=/; httpOnly=false; secure=${location.protocol === 'https:'}; samesite=strict`
    }
    
    return response
  }

  // Users
  async getUsers(query: UserQuery = {}): Promise<PaginatedResponse<User>> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    
    return this.request<PaginatedResponse<User>>(`/users?${params}`)
  }

  async createUser(user: Partial<User>): Promise<User> {
    return this.request<User>('/users', {
      method: 'POST',
      body: JSON.stringify(user),
    })
  }

  // Departments
  async getDepartments(): Promise<Department[]> {
    return this.request<Department[]>('/departments')
  }

  async createDepartment(department: Partial<Department>): Promise<Department> {
    return this.request<Department>('/departments', {
      method: 'POST',
      body: JSON.stringify(department),
    })
  }

  async updateDepartment(id: string, department: Partial<Department>): Promise<Department> {
    return this.request<Department>(`/departments/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(department),
    })
  }

  async deleteDepartment(id: string): Promise<void> {
    return this.request<void>(`/departments/${id}`, {
      method: 'DELETE',
    })
  }

  // Specialties
  async getSpecialties(): Promise<Specialty[]> {
    return this.request<Specialty[]>('/specialties')
  }

  async createSpecialty(specialty: Partial<Specialty>): Promise<Specialty> {
    return this.request<Specialty>('/specialties', {
      method: 'POST',
      body: JSON.stringify(specialty),
    })
  }

  // Levels
  async getLevels(): Promise<Level[]> {
    return this.request<Level[]>('/levels')
  }

  async createLevel(level: Partial<Level>): Promise<Level> {
    return this.request<Level>('/levels', {
      method: 'POST',
      body: JSON.stringify(level),
    })
  }

  // Groups
  async getGroups(): Promise<Group[]> {
    return this.request<Group[]>('/groups')
  }

  async createGroup(group: Partial<Group>): Promise<Group> {
    return this.request<Group>('/groups', {
      method: 'POST',
      body: JSON.stringify(group),
    })
  }

  async updateGroup(id: string, group: Partial<Group>): Promise<Group> {
    return this.request<Group>(`/groups/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(group),
    })
  }

  async deleteGroup(id: string): Promise<void> {
    return this.request<void>(`/groups/${id}`, {
      method: 'DELETE',
    })
  }

  // Rooms
  async getRooms(): Promise<Room[]> {
    return this.request<Room[]>('/rooms')
  }

  async createRoom(room: Partial<Room>): Promise<Room> {
    return this.request<Room>('/rooms', {
      method: 'POST',
      body: JSON.stringify(room),
    })
  }

  async updateRoom(id: string, room: Partial<Room>): Promise<Room> {
    return this.request<Room>(`/rooms/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(room),
    })
  }

  async deleteRoom(id: string): Promise<void> {
    return this.request<void>(`/rooms/${id}`, {
      method: 'DELETE',
    })
  }

  // Subjects
  async getSubjects(query: { page?: number; pageSize?: number; search?: string; levelId?: string; teacherId?: string } = {}): Promise<{ subjects: Subject[], total: number, page: number, pageSize: number, totalPages: number }> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    return this.request<{ subjects: Subject[], total: number, page: number, pageSize: number, totalPages: number }>(`/department-head/subjects/?${params}`)
  }

  async getSubject(id: string): Promise<Subject> {
    return this.request<Subject>(`/department-head/subjects/${id}`)
  }

  async createSubject(subject: { name: string; levelId: string; teacherId?: string }): Promise<Subject> {
    return this.request<Subject>('/department-head/subjects/', {
      method: 'POST',
      body: JSON.stringify(subject),
    })
  }

  async updateSubject(id: string, subject: { name?: string; levelId?: string; teacherId?: string }): Promise<Subject> {
    return this.request<Subject>(`/department-head/subjects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(subject),
    })
  }

  async deleteSubject(id: string): Promise<void> {
    return this.request<void>(`/department-head/subjects/${id}`, {
      method: 'DELETE',
    })
  }

  async getSubjectHelperData(): Promise<{ levels: Level[], teachers: any[] }> {
    const [levelsResponse, teachersResponse] = await Promise.all([
      this.request<{ levels: Level[] }>('/department-head/subjects/helpers/levels'),
      this.request<{ teachers: any[] }>('/department-head/subjects/helpers/teachers')
    ])
    return {
      levels: levelsResponse.levels,
      teachers: teachersResponse.teachers
    }
  }

  // Schedules
  async getSchedules(query: ScheduleQuery = {}): Promise<Schedule[]> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    
    return this.request<Schedule[]>(`/schedules?${params}`)
  }

  async createSchedule(schedule: Partial<Schedule>): Promise<Schedule> {
    return this.request<Schedule>('/schedules', {
      method: 'POST',
      body: JSON.stringify(schedule),
    })
  }

  async updateSchedule(id: string, schedule: Partial<Schedule>): Promise<Schedule> {
    return this.request<Schedule>(`/schedules/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(schedule),
    })
  }

  async deleteSchedule(id: string): Promise<void> {
    return this.request<void>(`/schedules/${id}`, {
      method: 'DELETE',
    })
  }

  async autoGenerateSchedule(groupId: string, mode: 'FILL' | 'REPLACE'): Promise<AutoGenerationResult> {
    return this.request<AutoGenerationResult>('/scheduling/auto-generate', {
      method: 'POST',
      body: JSON.stringify({ groupId, mode }),
    })
  }

  // Absences - New absence management system
  async getAbsences(query: {
    page?: number;
    pageSize?: number;
    studentId?: string;
    teacherId?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
  } = {}): Promise<{
    data: any[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  }> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    
    return this.request<{
      data: any[];
      total: number;
      page: number;
      pageSize: number;
      totalPages: number;
    }>(`/absences/?${params.toString()}`)
  }

  async createAbsence(data: {
    studentId: string;
    scheduleId: string;
    reason: string;
    status: string;
  }): Promise<{ message: string; id: string; notification_sent: boolean }> {
    return this.request<{ message: string; id: string; notification_sent: boolean }>('/absences/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getStudentAbsences(studentId: string): Promise<{
    absences: any[];
    statistics: {
      total: number;
      justified: number;
      unjustified: number;
      pending: number;
      absenceRate: number;
    };
  }> {
    return this.request<{
      absences: any[];
      statistics: {
        total: number;
        justified: number;
        unjustified: number;
        pending: number;
        absenceRate: number;
      };
    }>(`/absences/student/${studentId}`)
  }

  async justifyAbsence(absenceId: string, data: {
    justificationText: string;
    supportingDocuments: string[];
  }): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>(`/absences/${absenceId}/justify`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async reviewAbsence(absenceId: string, data: {
    reviewStatus: string;
    reviewNotes: string;
  }): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>(`/absences/${absenceId}/review`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteAbsence(absenceId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/absences/${absenceId}`, {
      method: 'DELETE',
    })
  }

  async getAbsenceStatistics(departmentId?: string, dateFrom?: string, dateTo?: string): Promise<{
    totalAbsences: number;
    justifiedAbsences: number;
    unjustifiedAbsences: number;
    pendingReview: number;
    approvedJustifications: number;
    rejectedJustifications: number;
    absenceRate: number;
    studentsWithHighAbsences: Array<{
      studentId: string;
      studentName: string;
      absenceCount: number;
    }>;
  }> {
    const params = new URLSearchParams()
    if (departmentId) params.append('departmentId', departmentId)
    if (dateFrom) params.append('dateFrom', dateFrom)
    if (dateTo) params.append('dateTo', dateTo)

    return this.request<{
      totalAbsences: number;
      justifiedAbsences: number;
      unjustifiedAbsences: number;
      pendingReview: number;
      approvedJustifications: number;
      rejectedJustifications: number;
      absenceRate: number;
      studentsWithHighAbsences: Array<{
        studentId: string;
        studentName: string;
        absenceCount: number;
      }>;
    }>(`/absences/statistics?${params.toString()}`)
  }

  // Makeups
  async getMakeups(): Promise<Makeup[]> {
    return this.request<Makeup[]>('/makeups')
  }

  async createMakeup(makeup: Partial<Makeup>): Promise<Makeup> {
    return this.request<Makeup>('/makeups', {
      method: 'POST',
      body: JSON.stringify(makeup),
    })
  }

  async approveMakeup(id: string): Promise<Makeup> {
    return this.request<Makeup>(`/makeups/${id}/approve`, {
      method: 'PATCH',
    })
  }

  async rejectMakeup(id: string, reason?: string): Promise<Makeup> {
    return this.request<Makeup>(`/makeups/${id}/reject`, {
      method: 'PATCH',
      body: JSON.stringify({ reason }),
    })
  }

  // Messages
  async getMessages(query: MessageQuery = {}): Promise<Message[]> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    
    return this.request<Message[]>(`/messages?${params}`)
  }

  async sendMessage(receiverId: string, content: string): Promise<Message> {
    return this.request<Message>('/messages', {
      method: 'POST',
      body: JSON.stringify({ receiverId, content }),
    })
  }

  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/messages/conversations')
  }

  // Export
  async exportTimetablePDF(groupId: string, weekStart: string): Promise<Blob> {
    const params = new URLSearchParams({ groupId, weekStart })
    const response = await fetch(`${this.baseURL}/export/timetable/pdf?${params}`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    })

    if (!response.ok) {
      throw new ApiError('Export failed', response.status, response.statusText)
    }

    return response.blob()
  }

  async exportTimetableICS(groupId: string, weekStart: string): Promise<Blob> {
    const params = new URLSearchParams({ groupId, weekStart })
    const response = await fetch(`${this.baseURL}/export/timetable/ics?${params}`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    })

    if (!response.ok) {
      throw new ApiError('Export failed', response.status, response.statusText)
    }

    return response.blob()
  }

  // Analytics
  async getAnalytics(query: AnalyticsQuery = {}): Promise<Analytics> {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
    
    return this.request<Analytics>(`/analytics?${params}`)
  }

  // Students Management
  async getStudents(filters?: { 
    department_id?: string; 
    specialty_id?: string; 
    academic_year?: string 
  }): Promise<User[]> {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
    }
    
    const url = `/admin/students${params.toString() ? '?' + params.toString() : ''}`
    return this.request<User[]>(url)
  }

  // Teachers Management
  async getTeachers(filters?: { 
    department_id?: string; 
    specialty_id?: string 
  }): Promise<User[]> {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
    }
    
    const url = `/admin/teachers${params.toString() ? '?' + params.toString() : ''}`
    return this.request<User[]>(url)
  }

  // Department Heads Management
  async getDepartmentHeads(filters?: { 
    department_id?: string 
  }): Promise<any[]> {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
    }
    
    const url = `/admin/department-heads${params.toString() ? '?' + params.toString() : ''}`
    return this.request<any[]>(url)
  }

  // Department Head Dashboard
  async getDepartmentHeadStatistics(): Promise<any> {
    return this.request<any>('/department-head/statistics')
  }
  
  async getDepartmentHeadStudents(): Promise<User[]> {
    return this.request<User[]>('/department-head/students')
  }
  
  async getDepartmentHeadTeachers(): Promise<User[]> {
    return this.request<User[]>('/department-head/teachers')
  }

  // Department Head Timetable Management
  async getTimetableGroups(): Promise<any[]> {
    return this.request<any[]>('/department-head/timetable/groups')
  }

  async getTimetableTeachers(): Promise<any[]> {
    return this.request<any[]>('/department-head/timetable/teachers')
  }

  async getTimetableSubjects(): Promise<any[]> {
    return this.request<any[]>('/department-head/timetable/subjects')
  }

  async getTimetableSpecialities(): Promise<any[]> {
    return this.request<any[]>('/department-head/timetable/specialities')
  }

  async getSubjectsBySpeciality(specialityId: string): Promise<any[]> {
    return this.request<any[]>(`/department-head/timetable/subjects/by-speciality/${specialityId}`)
  }

  async createTimetableSubject(subjectData: any): Promise<any> {
    return this.request<any>('/department-head/timetable/subjects', {
      method: 'POST',
      body: JSON.stringify(subjectData)
    })
  }

  async updateTimetableSubject(subjectId: string, subjectData: any): Promise<any> {
    return this.request<any>(`/department-head/timetable/subjects/${subjectId}`, {
      method: 'PUT',
      body: JSON.stringify(subjectData)
    })
  }

  async deleteTimetableSubject(subjectId: string): Promise<any> {
    return this.request<any>(`/department-head/timetable/subjects/${subjectId}`, {
      method: 'DELETE'
    })
  }

  async getTimetableRooms(): Promise<any[]> {
    return this.request<any[]>('/department-head/timetable/rooms')
  }

  async getTimetableSchedules(params?: URLSearchParams): Promise<any[]> {
    const queryString = params ? `?${params.toString()}` : ''
    return this.request<any[]>(`/department-head/timetable/schedules${queryString}`)
  }

  async getTimetableConflicts(params?: URLSearchParams): Promise<{ conflicts: any[] }> {
    const queryString = params ? `?${params.toString()}` : ''
    return this.request<{ conflicts: any[] }>(`/department-head/timetable/conflicts${queryString}`)
  }

  async createTimetableSchedule(scheduleData: any): Promise<any> {
    return this.request<any>('/department-head/timetable/schedules', {
      method: 'POST',
      body: JSON.stringify(scheduleData),
    })
  }

  async updateTimetableSchedule(id: string, scheduleData: any): Promise<any> {
    return this.request<any>(`/department-head/timetable/schedules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(scheduleData),
    })
  }

  async deleteTimetableSchedule(id: string): Promise<void> {
    return this.request<void>(`/department-head/timetable/schedules/${id}`, {
      method: 'DELETE',
    })
  }

  // Room Occupancy
  async getRoomOccupancy(params?: { week_offset?: number; room_type?: string; building?: string }): Promise<any> {
    const queryParams = new URLSearchParams()
    
    if (params?.week_offset !== undefined) {
      queryParams.append('week_offset', params.week_offset.toString())
    }
    if (params?.room_type && params.room_type !== 'all') {
      queryParams.append('room_type', params.room_type)
    }
    if (params?.building && params.building !== 'all') {
      queryParams.append('building', params.building)
    }
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : ''
    return this.request<any>(`/room-occupancy/rooms${queryString}`)
  }

  async getRoomDetails(roomId: string): Promise<any> {
    return this.request<any>(`/room-occupancy/rooms/${roomId}/details`)
  }

  async getRoomOccupancyStatistics(weekOffset: number = 0): Promise<any> {
    return this.request<any>(`/room-occupancy/statistics?week_offset=${weekOffset}`)
  }

  // Department-specific comprehensive data
  async getDepartmentComprehensiveData(departmentId: string): Promise<any> {
    try {
      const [students, teachers, subjects, groups, levels, specialties, schedules, rooms, departmentHeads] = await Promise.allSettled([
        this.getStudents({ department_id: departmentId }),
        this.getTeachers({ department_id: departmentId }),
        this.getSubjects(),
        this.getGroups(),
        this.getLevels(),
        this.getSpecialties(),
        this.getSchedules(),
        this.getRooms(),
        this.getDepartmentHeads({ department_id: departmentId })
      ])
      
      return {
        students: students.status === 'fulfilled' ? students.value : [],
        teachers: teachers.status === 'fulfilled' ? teachers.value : [],
        subjects: subjects.status === 'fulfilled' ? subjects.value : [],
        groups: groups.status === 'fulfilled' ? groups.value : [],
        levels: levels.status === 'fulfilled' ? levels.value : [],
        specialties: specialties.status === 'fulfilled' ? (Array.isArray(specialties.value) ? specialties.value.filter((s: any) => s.departmentId === departmentId) : []) : [],
        schedules: schedules.status === 'fulfilled' ? schedules.value : [],
        rooms: rooms.status === 'fulfilled' ? rooms.value : [],
        departmentHeads: departmentHeads.status === 'fulfilled' ? departmentHeads.value : []
      }
    } catch (error) {
      console.error('Error fetching comprehensive department data:', error)
      // Return empty data structure instead of throwing
      return {
        students: [],
        teachers: [],
        subjects: [],
        groups: [],
        levels: [],
        specialties: [],
        schedules: [],
        rooms: [],
        departmentHeads: []
      }
    }
  }

  // Department Head specific dashboard data using timetable endpoints
  async getDepartmentHeadDashboardData(): Promise<any> {
    try {
      const [groups, teachers, subjects, specialities, rooms, schedules] = await Promise.allSettled([
        this.getTimetableGroups(),
        this.getTimetableTeachers(),
        this.getTimetableSubjects(),
        this.getTimetableSpecialities(),
        this.getTimetableRooms(),
        this.getTimetableSchedules()
      ])
      
      console.log('📊 Dashboard data loaded:', {
        groups: groups.status === 'fulfilled' ? groups.value.length : 0,
        teachers: teachers.status === 'fulfilled' ? teachers.value.length : 0,
        subjects: subjects.status === 'fulfilled' ? subjects.value.length : 0,
        specialities: specialities.status === 'fulfilled' ? specialities.value.length : 0,
        rooms: rooms.status === 'fulfilled' ? rooms.value.length : 0,
        schedules: schedules.status === 'fulfilled' ? schedules.value.length : 0
      })
      
      return {
        groups: groups.status === 'fulfilled' ? groups.value : [],
        teachers: teachers.status === 'fulfilled' ? teachers.value : [],
        subjects: subjects.status === 'fulfilled' ? subjects.value : [],
        specialities: specialities.status === 'fulfilled' ? specialities.value : [],
        rooms: rooms.status === 'fulfilled' ? rooms.value : [],
        schedules: schedules.status === 'fulfilled' ? schedules.value : []
      }
    } catch (error) {
      console.error('❌ Error fetching department head dashboard data:', error)
      throw error
    }
  }

  // Notification endpoints
  async getNotifications(unreadOnly: boolean = false): Promise<any[]> {
    const params = unreadOnly ? '?unread_only=true' : ''
    return this.request<any[]>(`/notifications${params}`)
  }

  async getNotificationStats(): Promise<any> {
    return this.request<any>('/notifications/stats')
  }

  async markNotificationAsRead(notificationId: string): Promise<any> {
    return this.request<any>(`/notifications/${notificationId}/read`, {
      method: 'PATCH'
    })
  }

  async markAllNotificationsAsRead(): Promise<any> {
    return this.request<any>('/notifications/mark-all-read', {
      method: 'PATCH'
    })
  }

  async deleteNotification(notificationId: string): Promise<any> {
    return this.request<any>(`/notifications/${notificationId}`, {
      method: 'DELETE'
    })
  }

  async deleteAllNotifications(): Promise<any> {
    return this.request<any>('/notifications', {
      method: 'DELETE'
    })
  }
}

export const api = new ApiClient()

// Helper function to get auth headers
export function getAuthHeaders(): Record<string, string> {
  // Try both token keys for compatibility
  const token = typeof window !== 'undefined' 
    ? (localStorage.getItem('authToken') || localStorage.getItem('access_token'))
    : null;
  
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}
export { ApiError }