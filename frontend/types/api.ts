export enum UserRole {
  STUDENT = 'STUDENT',
  TEACHER = 'TEACHER',
  DEPARTMENT_HEAD = 'DEPARTMENT_HEAD'
}

export enum ScheduleStatus {
  PLANNED = 'PLANNED',
  MAKEUP = 'MAKEUP',
  CANCELLED = 'CANCELLED'
}

export enum AbsenceStatus {
  PENDING = 'PENDING',
  JUSTIFIED = 'JUSTIFIED',
  REFUSED = 'REFUSED'
}

export enum MakeupStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED'
}

export interface User {
  id: string
  email: string
  prenom: string  // French: firstName
  nom: string     // French: lastName
  login: string
  role: UserRole
  departmentId?: string
  specialtyId?: string
  levelId?: string
  groupId?: string
  subjectIds?: string[]
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface Department {
  id: string
  name: string
  headId?: string
}

export interface Specialty {
  id: string
  name: string
  departmentId: string
}

export interface Level {
  id: string
  name: string
  specialtyId: string
}

export interface Group {
  id: string
  name: string
  levelId: string
  studentCount: number
}

export interface Room {
  id: string
  name: string
  capacity: number
  type: string
}

export interface Subject {
  id: string
  name: string
  levelId: string
  teacherId: string
  level?: {
    id: string
    name: string
    specialty?: {
      id: string
      name: string
      department?: {
        id: string
        name: string
      }
    }
  }
  teacher?: {
    id: string
    user?: {
      id: string
      prenom: string
      nom: string
      email: string
    }
    department?: {
      id: string
      name: string
    }
  }
}

export interface Schedule {
  id: string
  subjectId: string
  groupId: string
  roomId: string
  teacherId: string
  date: string
  startTime: string
  endTime: string
  status: ScheduleStatus
  subject?: Subject
  group?: Group
  room?: Room
  teacher?: User
}

export interface Absence {
  id: string
  studentId: string
  scheduleId: string
  status: AbsenceStatus
  justificationUrl?: string
  createdAt: string
  student?: User
  schedule?: Schedule
}

export interface Makeup {
  id: string
  originalScheduleId?: string
  subjectId: string
  groupId: string
  roomId: string
  teacherId: string
  date: string
  startTime: string
  endTime: string
  status: MakeupStatus
  reason: string
  createdAt: string
  subject?: Subject
  group?: Group
  room?: Room
  teacher?: User
}

export interface Message {
  id: string
  senderId: string
  receiverId: string
  content: string
  createdAt: string
  sender?: User
  receiver?: User
}

export interface Conversation {
  userId: string
  user: User
  lastMessage?: Message
  unreadCount: number
}

export interface AutoGenerationResult {
  created: number
  conflicts: ScheduleConflict[]
  unplaced: UnplacedSession[]
}

export interface ScheduleConflict {
  reason: string
  existingSchedule: Schedule
  conflictingSchedule: Partial<Schedule>
}

export interface UnplacedSession {
  subjectId: string
  groupId: string
  reason: string
  subject?: Subject
  group?: Group
}

export interface Analytics {
  absenceRate: { groupId: string; rate: number; groupName: string }[]
  roomUsage: { roomId: string; usage: number; roomName: string }[]
  subjectCoverage: { subjectId: string; coverage: number; subjectName: string }[]
}

// API Query Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface UserQuery {
  role?: UserRole
  page?: number
  size?: number
  search?: string
}

export interface ScheduleQuery {
  groupId?: string
  date?: string
  weekStart?: string
  teacherId?: string
}

export interface AbsenceQuery {
  studentId?: string
  status?: AbsenceStatus
  groupId?: string
  page?: number
  size?: number
}

export interface MessageQuery {
  withUser?: string
  page?: number
  size?: number
}

export interface AnalyticsQuery {
  groupId?: string
  roomId?: string
  range?: string
  weekStart?: string
}