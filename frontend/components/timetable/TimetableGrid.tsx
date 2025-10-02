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
import { Plus, Edit, Trash2 } from 'lucide-react'

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
    
    return (
      <div className="space-y-1">
        {mergedSessions.map((sessionGroup, index) => {
          const session = sessionGroup[0]
          const backgroundColor = generateColorFromId(session.subjectId)
          
          return (
            <div
              key={`${session.id}-${index}`}
              className="relative p-2 rounded-md text-xs cursor-pointer hover:opacity-80 transition-opacity"
              style={{ backgroundColor }}
              onClick={(e) => {
                e.stopPropagation()
                if (mode === 'edit') {
                  setSelectedSession(session)
                  setIsDialogOpen(true)
                }
              }}
            >
              <div className="font-medium text-gray-900">
                {session.subject?.name || 'Unknown Subject'}
              </div>
              <div className="text-gray-700">
                {session.teacher?.firstName} {session.teacher?.lastName}
              </div>
              <div className="text-gray-600">
                {session.room?.name || 'No Room'}
              </div>
              <div className="text-gray-600">
                {formatTimeRange(sessionGroup)}
              </div>
              {session.status === 'MAKEUP' && (
                <Badge variant="secondary" className="absolute top-1 right-1 text-xs">
                  Makeup
                </Badge>
              )}
              {mode === 'edit' && (
                <div className="absolute bottom-1 right-1 flex space-x-1">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-4 w-4 p-0 text-gray-600 hover:text-gray-900"
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedSession(session)
                      setIsDialogOpen(true)
                    }}
                  >
                    <Edit size={12} />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-4 w-4 p-0 text-red-600 hover:text-red-900"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSessionDelete(session.id)
                    }}
                  >
                    <Trash2 size={12} />
                  </Button>
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
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="w-24 p-4 text-left font-medium border-b border-r bg-muted">
                    Time
                  </th>
                  {weekDates.map((date, index) => (
                    <th
                      key={date.toISOString()}
                      className="p-4 text-center font-medium border-b bg-muted min-w-[200px]"
                    >
                      <div>{WEEKDAYS[index]}</div>
                      <div className="text-sm text-muted-foreground">
                        {format(date, 'MMM dd')}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((time) => (
                  <tr key={time} className="border-b">
                    <td className="p-4 font-medium border-r bg-muted/50">
                      {time}
                    </td>
                    {weekDates.map((date) => {
                      const dateStr = formatDateForAPI(date)
                      const sessions = getSessionsForDateAndTime(dateStr, time)
                      
                      return (
                        <td
                          key={`${dateStr}-${time}`}
                          className="p-2 border-r min-h-[80px] align-top cursor-pointer hover:bg-muted/20 transition-colors"
                          onClick={() => handleCellClick(dateStr, time)}
                        >
                          {sessions.length > 0 ? (
                            renderSessionCell(sessions)
                          ) : (
                            mode === 'edit' && (
                              <div className="flex items-center justify-center h-16 text-muted-foreground hover:text-foreground">
                                <Plus size={16} />
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