 'use client'

import { useState } from 'react'
import { Schedule } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  TIME_SLOTS, 
  WEEKDAYS, 
  generateColorFromId, 
  mergeConsecutiveSessions,
  formatTimeRange,
  getWeekDates,
  formatDateForAPI 
} from '@/lib/timetable'
import { SessionFormDialog } from './SessionFormDialog'
import { format } from 'date-fns'
import { Plus, Edit, Trash2, Loader2 } from 'lucide-react'

interface TimetableGridProps {
  schedules: Schedule[]
  mode: 'read' | 'edit'
  weekStart: Date
  onSessionCreate?: (session: Partial<Schedule>) => Promise<void>
  onSessionUpdate?: (id: string, session: Partial<Schedule>) => Promise<void>
  onSessionDelete?: (id: string) => Promise<void>
  groupId?: string
  isLoading?: boolean
}

export function TimetableGrid({
  schedules,
  mode,
  weekStart,
  onSessionCreate,
  onSessionUpdate,
  onSessionDelete,
  groupId,
  isLoading = false
}: TimetableGridProps) {
  const [selectedSession, setSelectedSession] = useState<Schedule | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<{
    date: string
    time: string
  } | null>(null)

  const weekDates = getWeekDates(weekStart)

  const getSessionsForDateAndTime = (date: string, time: string): Schedule[] => {
    return schedules.filter(
      schedule => schedule.date === date && schedule.startTime === time
    )
  }

  const handleCellClick = (date: string, time: string) => {
    if (mode !== 'edit') return

    const existingSessions = getSessionsForDateAndTime(date, time)
    
    if (existingSessions.length > 0) {
      // Edit existing session
      setSelectedSession(existingSessions[0])
    } else {
      // Create new session
      setSelectedSession(null)
      setSelectedTimeSlot({ date, time })
    }
    
    setIsDialogOpen(true)
  }

  const handleSessionSave = async (sessionData: Partial<Schedule>) => {
    try {
      if (selectedSession) {
        // Update existing session
        await onSessionUpdate?.(selectedSession.id, sessionData)
      } else {
        // Create new session
        await onSessionCreate?.(sessionData)
      }
      setIsDialogOpen(false)
      setSelectedSession(null)
      setSelectedTimeSlot(null)
    } catch (error) {
      console.error('Failed to save session:', error)
    }
  }

  const handleSessionDelete = async (sessionId: string) => {
    try {
      await onSessionDelete?.(sessionId)
      setIsDialogOpen(false)
      setSelectedSession(null)
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  const renderSessionCell = (sessions: Schedule[]) => {
    if (sessions.length === 0) return null

    const mergedSessions = mergeConsecutiveSessions(sessions)
    
    // Color mapping for subjects
    const subjectColorMap: Record<string, { gradient: string; bg: string }> = {
      'ALGO': { gradient: 'from-blue-500 to-blue-600', bg: 'bg-blue-500' },
      'MATH': { gradient: 'from-green-500 to-green-600', bg: 'bg-green-500' },
      'ARCH': { gradient: 'from-purple-500 to-purple-600', bg: 'bg-purple-500' },
      'ENG': { gradient: 'from-orange-500 to-orange-600', bg: 'bg-orange-500' },
      'default': { gradient: 'from-indigo-500 to-indigo-600', bg: 'bg-indigo-500' }
    }
    
    return (
      <div className="space-y-1.5">
        {mergedSessions.map((sessionGroup, index) => {
          const session = sessionGroup[0]
          const subjectCode = session.subject?.name?.split(' ')[0] || 'default'
          const colorConfig = subjectColorMap[subjectCode] || subjectColorMap['default']
          const backgroundColor = generateColorFromId(session.subjectId)
          
          // Handle property naming - use prenom/nom (French naming convention)
          const teacherName = session.teacher 
            ? `${session.teacher.prenom || ''} ${session.teacher.nom || ''}`.trim() || 'Enseignant'
            : 'Enseignant'
          
          return (
            <div
              key={`${session.id}-${index}`}
              className={`bg-gradient-to-br ${colorConfig.gradient} rounded-lg p-2.5 text-white shadow-md hover:shadow-lg transition-all cursor-pointer group hover:scale-105 transform text-xs`}
              onClick={(e) => {
                e.stopPropagation()
                if (mode === 'edit') {
                  setSelectedSession(session)
                  setIsDialogOpen(true)
                }
              }}
            >
              <div className="font-bold truncate">
                {session.subject?.name || 'Cours'}
              </div>
              <div className="text-white/90 truncate text-xs">
                {teacherName}
              </div>
              <div className="flex items-center gap-1 text-white/80 mt-1 text-xs">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                </svg>
                <span className="truncate">{session.room?.name || 'Salle'}</span>
              </div>
              <div className="text-white/70 text-xs mt-1">
                {formatTimeRange(sessionGroup)}
              </div>
              {session.status === 'MAKEUP' && (
                <Badge className="absolute top-1 right-1 text-xs bg-yellow-500 text-white hover:bg-yellow-600">
                  Rattrapage
                </Badge>
              )}
              {mode === 'edit' && (
                <div className="flex gap-1 mt-2 pt-1.5 border-t border-white/20">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedSession(session)
                      setIsDialogOpen(true)
                    }}
                    className="text-white/90 hover:text-white hover:bg-white/20 p-1 rounded flex-1 flex items-center justify-center transition-all"
                    title="Modifier"
                  >
                    <Edit size={12} />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSessionDelete(session.id)
                    }}
                    className="text-white/90 hover:text-white hover:bg-red-500/40 p-1 rounded flex-1 flex items-center justify-center transition-all"
                    title="Supprimer"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  if (isLoading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="p-6">
          <div className="flex flex-col items-center justify-center h-96 gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            <p className="text-gray-500">Chargement de l'emploi du temps...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className="border-0 shadow-lg overflow-hidden">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-indigo-50 to-purple-50 border-b-2 border-indigo-200">
                  <th className="w-24 p-4 text-left font-bold text-gray-900 border-r border-indigo-200">
                    Heure
                  </th>
                  {weekDates.map((date, index) => (
                    <th
                      key={date.toISOString()}
                      className="p-4 text-center font-bold text-gray-900 border-r border-indigo-200 min-w-[200px] bg-gradient-to-b from-indigo-50 to-transparent"
                    >
                      <div className="text-sm font-bold text-indigo-900">{WEEKDAYS[index]}</div>
                      <div className="text-xs text-indigo-600 font-semibold">
                        {format(date, 'dd MMM')}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((time, timeIdx) => (
                  <tr key={time} className={`border-b border-gray-200 ${timeIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'}`}>
                    <td className="p-4 font-semibold text-gray-900 border-r border-gray-200 bg-gradient-to-r from-indigo-50 to-transparent text-sm">
                      {time}
                    </td>
                    {weekDates.map((date) => {
                      const dateStr = formatDateForAPI(date)
                      const sessions = getSessionsForDateAndTime(dateStr, time)
                      
                      return (
                        <td
                          key={`${dateStr}-${time}`}
                          className="p-2 border-r border-gray-200 min-h-[100px] align-top cursor-pointer hover:bg-indigo-50/50 transition-all"
                          onClick={() => handleCellClick(dateStr, time)}
                        >
                          {sessions.length > 0 ? (
                            renderSessionCell(sessions)
                          ) : (
                            mode === 'edit' && (
                              <div className="flex items-center justify-center h-20 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-all">
                                <Plus size={20} />
                              </div>
                            )
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <SessionFormDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        session={selectedSession}
        defaultDate={selectedTimeSlot?.date}
        defaultTime={selectedTimeSlot?.time}
        groupId={groupId}
        onSave={handleSessionSave}
        onDelete={selectedSession ? () => handleSessionDelete(selectedSession.id) : undefined}
      />
    </>
  )
}