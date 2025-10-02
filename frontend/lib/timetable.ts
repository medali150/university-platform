import { Schedule } from '@/types/api'

export const TIME_SLOTS = [
  '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
  '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
  '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
  '17:00', '17:30', '18:00'
] as const

export const WEEKDAYS = [
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
] as const

export interface TimeSlot {
  time: string
  sessions: Schedule[][]
}

export interface TimetableDay {
  date: string
  weekday: string
  sessions: Schedule[]
}

export function generateColorFromId(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const hue = hash % 360
  return `hsl(${hue}, 70%, 80%)`
}

export function mergeConsecutiveSessions(sessions: Schedule[]): Schedule[][] {
  if (sessions.length === 0) return []

  // Sort sessions by start time
  const sortedSessions = [...sessions].sort((a, b) => 
    a.startTime.localeCompare(b.startTime)
  )

  const merged: Schedule[][] = []
  let currentGroup: Schedule[] = [sortedSessions[0]]

  for (let i = 1; i < sortedSessions.length; i++) {
    const current = sortedSessions[i]
    const last = currentGroup[currentGroup.length - 1]

    // Check if sessions can be merged (same subject, teacher, group, room and consecutive times)
    if (
      current.subjectId === last.subjectId &&
      current.teacherId === last.teacherId &&
      current.groupId === last.groupId &&
      current.roomId === last.roomId &&
      current.startTime === last.endTime
    ) {
      currentGroup.push(current)
    } else {
      merged.push(currentGroup)
      currentGroup = [current]
    }
  }

  merged.push(currentGroup)
  return merged
}

export function getSessionDuration(sessions: Schedule[]): number {
  if (sessions.length === 0) return 0
  
  const startTime = sessions[0].startTime
  const endTime = sessions[sessions.length - 1].endTime
  
  const start = new Date(`1970-01-01T${startTime}:00`)
  const end = new Date(`1970-01-01T${endTime}:00`)
  
  return (end.getTime() - start.getTime()) / (1000 * 60) // Duration in minutes
}

export function formatTimeRange(sessions: Schedule[]): string {
  if (sessions.length === 0) return ''
  
  const startTime = sessions[0].startTime
  const endTime = sessions[sessions.length - 1].endTime
  
  return `${startTime} - ${endTime}`
}

export function createTimeSlots(sessions: Schedule[]): TimeSlot[] {
  const timeSlots: TimeSlot[] = TIME_SLOTS.map(time => ({
    time,
    sessions: []
  }))

  // Group sessions by time slot
  sessions.forEach(session => {
    const timeIndex = TIME_SLOTS.indexOf(session.startTime as any)
    if (timeIndex !== -1) {
      timeSlots[timeIndex].sessions.push([session])
    }
  })

  // Merge consecutive sessions for each time slot
  timeSlots.forEach(slot => {
    const allSessions = slot.sessions.flat()
    slot.sessions = mergeConsecutiveSessions(allSessions)
  })

  return timeSlots
}

export function getWeekDates(weekStart: Date): Date[] {
  const dates: Date[] = []
  const startOfWeek = new Date(weekStart)
  
  // Ensure we start from Monday
  const dayOfWeek = startOfWeek.getDay()
  const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1
  startOfWeek.setDate(startOfWeek.getDate() - daysToSubtract)
  
  for (let i = 0; i < 6; i++) {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + i)
    dates.push(date)
  }
  
  return dates
}

export function formatDateForAPI(date: Date): string {
  return date.toISOString().split('T')[0]
}

export function isTimeSlotAvailable(
  timeSlot: string,
  date: string,
  existingSessions: Schedule[],
  roomId?: string,
  teacherId?: string,
  groupId?: string
): boolean {
  return !existingSessions.some(session => {
    if (session.date !== date || session.startTime !== timeSlot) {
      return false
    }
    
    // Check for conflicts
    if (roomId && session.roomId === roomId) return true
    if (teacherId && session.teacherId === teacherId) return true
    if (groupId && session.groupId === groupId) return true
    
    return false
  })
}

export function findNextAvailableSlot(
  startTime: string,
  date: string,
  existingSessions: Schedule[],
  roomId?: string,
  teacherId?: string,
  groupId?: string
): string | null {
  const startIndex = TIME_SLOTS.indexOf(startTime as any)
  if (startIndex === -1) return null
  
  for (let i = startIndex; i < TIME_SLOTS.length; i++) {
    const timeSlot = TIME_SLOTS[i]
    if (isTimeSlotAvailable(timeSlot, date, existingSessions, roomId, teacherId, groupId)) {
      return timeSlot
    }
  }
  
  return null
}