'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Schedule, Subject, Room, Group } from '@/types/api'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { Loader2, Trash2 } from 'lucide-react'

const sessionSchema = z.object({
  subjectId: z.string().min(1, 'Subject is required'),
  groupId: z.string().min(1, 'Group is required'),
  roomId: z.string().min(1, 'Room is required'),
  date: z.string().min(1, 'Date is required'),
  startTime: z.string().min(1, 'Start time is required'),
  endTime: z.string().min(1, 'End time is required'),
  status: z.enum(['PLANNED', 'MAKEUP', 'CANCELLED']).default('PLANNED'),
})

type SessionFormData = z.infer<typeof sessionSchema>

interface SessionFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  session?: Schedule | null
  defaultDate?: string
  defaultTime?: string
  groupId?: string
  onSave: (data: Partial<Schedule>) => Promise<void>
  onDelete?: () => Promise<void>
}

export function SessionFormDialog({
  open,
  onOpenChange,
  session,
  defaultDate,
  defaultTime,
  groupId,
  onSave,
  onDelete,
}: SessionFormDialogProps) {
  const [isLoading, setIsLoading] = useState(false)

  const { data: subjects = [] } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.getSubjects(),
  })

  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => api.getRooms(),
  })

  const { data: groups = [] } = useQuery({
    queryKey: ['groups'],
    queryFn: () => api.getGroups(),
  })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<SessionFormData>({
    resolver: zodResolver(sessionSchema),
    defaultValues: {
      status: 'PLANNED',
    },
  })

  const selectedSubjectId = watch('subjectId')

  // Auto-fill teacher when subject is selected
  useEffect(() => {
    if (selectedSubjectId) {
      const subject = subjects.find(s => s.id === selectedSubjectId)
      if (subject) {
        // The teacherId will be set automatically from the subject
      }
    }
  }, [selectedSubjectId, subjects])

  // Reset form when dialog opens/closes or session changes
  useEffect(() => {
    if (open) {
      if (session) {
        // Edit mode
        reset({
          subjectId: session.subjectId,
          groupId: session.groupId,
          roomId: session.roomId,
          date: session.date,
          startTime: session.startTime,
          endTime: session.endTime,
          status: session.status,
        })
      } else {
        // Create mode
        reset({
          subjectId: '',
          groupId: groupId || '',
          roomId: '',
          date: defaultDate || '',
          startTime: defaultTime || '',
          endTime: defaultTime || '',
          status: 'PLANNED',
        })
      }
    }
  }, [open, session, groupId, defaultDate, defaultTime, reset])

  const onSubmit = async (data: SessionFormData) => {
    setIsLoading(true)
    
    try {
      const subject = subjects.find(s => s.id === data.subjectId)
      const sessionData = {
        ...data,
        teacherId: subject?.teacherId || '',
      }
      
      await onSave(sessionData)
      toast.success(session ? 'Session updated successfully' : 'Session created successfully')
      onOpenChange(false)
    } catch (error: any) {
      console.error('Failed to save session:', error)
      toast.error('Failed to save session. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    
    setIsLoading(true)
    
    try {
      await onDelete()
      toast.success('Session deleted successfully')
      onOpenChange(false)
    } catch (error: any) {
      console.error('Failed to delete session:', error)
      toast.error('Failed to delete session. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const generateEndTime = (startTime: string): string => {
    if (!startTime) return ''
    
    const [hours, minutes] = startTime.split(':').map(Number)
    const startDate = new Date()
    startDate.setHours(hours, minutes)
    
    // Add 2 hours by default
    const endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000)
    
    return `${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`
  }

  const handleStartTimeChange = (value: string) => {
    setValue('startTime', value)
    if (!watch('endTime')) {
      setValue('endTime', generateEndTime(value))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>
            {session ? 'Edit Session' : 'Create Session'}
          </DialogTitle>
          <DialogDescription>
            {session 
              ? 'Update the session details below.'
              : 'Fill in the details to create a new session.'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="subjectId">Subject</Label>
              <Select 
                value={watch('subjectId')} 
                onValueChange={(value) => setValue('subjectId', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select subject" />
                </SelectTrigger>
                <SelectContent>
                  {subjects.map((subject) => (
                    <SelectItem key={subject.id} value={subject.id}>
                      {subject.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.subjectId && (
                <p className="text-sm text-destructive">{errors.subjectId.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="groupId">Group</Label>
              <Select 
                value={watch('groupId')} 
                onValueChange={(value) => setValue('groupId', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select group" />
                </SelectTrigger>
                <SelectContent>
                  {groups.map((group) => (
                    <SelectItem key={group.id} value={group.id}>
                      {group.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.groupId && (
                <p className="text-sm text-destructive">{errors.groupId.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="roomId">Room</Label>
              <Select 
                value={watch('roomId')} 
                onValueChange={(value) => setValue('roomId', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select room" />
                </SelectTrigger>
                <SelectContent>
                  {rooms.map((room) => (
                    <SelectItem key={room.id} value={room.id}>
                      {room.name} (Capacity: {room.capacity})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.roomId && (
                <p className="text-sm text-destructive">{errors.roomId.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                {...register('date')}
                disabled={isLoading}
              />
              {errors.date && (
                <p className="text-sm text-destructive">{errors.date.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startTime">Start Time</Label>
              <Input
                id="startTime"
                type="time"
                {...register('startTime')}
                onChange={(e) => handleStartTimeChange(e.target.value)}
                disabled={isLoading}
              />
              {errors.startTime && (
                <p className="text-sm text-destructive">{errors.startTime.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime">End Time</Label>
              <Input
                id="endTime"
                type="time"
                {...register('endTime')}
                disabled={isLoading}
              />
              {errors.endTime && (
                <p className="text-sm text-destructive">{errors.endTime.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select 
                value={watch('status')} 
                onValueChange={(value) => setValue('status', value as any)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PLANNED">Planned</SelectItem>
                  <SelectItem value="MAKEUP">Make-up</SelectItem>
                  <SelectItem value="CANCELLED">Cancelled</SelectItem>
                </SelectContent>
              </Select>
              {errors.status && (
                <p className="text-sm text-destructive">{errors.status.message}</p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2">
            {session && onDelete && (
              <Button
                type="button"
                variant="destructive"
                onClick={handleDelete}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="mr-2 h-4 w-4" />
                )}
                Delete
              </Button>
            )}
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {session ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}