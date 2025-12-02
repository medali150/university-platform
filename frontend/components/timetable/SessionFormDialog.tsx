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

  const { data: subjectsData } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.getSubjects(),
  })
  const subjects = subjectsData?.subjects ?? []

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
      const sessionData: Partial<Schedule> = {
        ...data,
        teacherId: subject?.teacherId || '',
        status: data.status as any,
      }
      
      await onSave(sessionData)
      toast.success(session ? 'Séance mise à jour avec succès' : 'Séance créée avec succès')
      onOpenChange(false)
    } catch (error: any) {
      console.error('Failed to save session:', error)
      toast.error('Erreur lors de l\'enregistrement de la séance. Veuillez réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    
    setIsLoading(true)
    
    try {
      await onDelete()
      toast.success('Séance supprimée avec succès')
      onOpenChange(false)
    } catch (error: any) {
      console.error('Failed to delete session:', error)
      toast.error('Erreur lors de la suppression de la séance. Veuillez réessayer.')
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
      <DialogContent className="sm:max-w-[600px] border-0 shadow-xl">
        <DialogHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white -m-6 mb-0 p-6 rounded-t-lg">
          <DialogTitle className="text-white text-lg">
            {session ? '✏️ Modifier une séance' : '➕ Créer une nouvelle séance'}
          </DialogTitle>
          <DialogDescription className="text-indigo-100">
            {session 
              ? 'Mettez à jour les informations de la séance ci-dessous.'
              : 'Remplissez les détails pour créer une nouvelle séance.'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="subjectId" className="font-semibold text-gray-700">
                Matière <span className="text-red-500">*</span>
              </Label>
              <Select 
                value={watch('subjectId')} 
                onValueChange={(value) => setValue('subjectId', value)}
              >
                <SelectTrigger className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors">
                  <SelectValue placeholder="Sélectionner une matière" />
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
                <p className="text-sm text-red-500 font-medium">{errors.subjectId.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="groupId" className="font-semibold text-gray-700">
                Groupe <span className="text-red-500">*</span>
              </Label>
              <Select 
                value={watch('groupId')} 
                onValueChange={(value) => setValue('groupId', value)}
              >
                <SelectTrigger className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors">
                  <SelectValue placeholder="Sélectionner un groupe" />
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
                <p className="text-sm text-red-500 font-medium">{errors.groupId.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="roomId" className="font-semibold text-gray-700">
                Salle <span className="text-red-500">*</span>
              </Label>
              <Select 
                value={watch('roomId')} 
                onValueChange={(value) => setValue('roomId', value)}
              >
                <SelectTrigger className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors">
                  <SelectValue placeholder="Sélectionner une salle" />
                </SelectTrigger>
                <SelectContent>
                  {rooms.map((room) => (
                    <SelectItem key={room.id} value={room.id}>
                      {room.name} (Cap: {room.capacity})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.roomId && (
                <p className="text-sm text-red-500 font-medium">{errors.roomId.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="date" className="font-semibold text-gray-700">
                Date <span className="text-red-500">*</span>
              </Label>
              <Input
                id="date"
                type="date"
                {...register('date')}
                disabled={isLoading}
                className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors"
              />
              {errors.date && (
                <p className="text-sm text-red-500 font-medium">{errors.date.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startTime" className="font-semibold text-gray-700">
                Début <span className="text-red-500">*</span>
              </Label>
              <Input
                id="startTime"
                type="time"
                {...register('startTime')}
                onChange={(e) => handleStartTimeChange(e.target.value)}
                disabled={isLoading}
                className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors"
              />
              {errors.startTime && (
                <p className="text-sm text-red-500 font-medium">{errors.startTime.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime" className="font-semibold text-gray-700">
                Fin <span className="text-red-500">*</span>
              </Label>
              <Input
                id="endTime"
                type="time"
                {...register('endTime')}
                disabled={isLoading}
                className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors"
              />
              {errors.endTime && (
                <p className="text-sm text-red-500 font-medium">{errors.endTime.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="status" className="font-semibold text-gray-700">
                Statut <span className="text-red-500">*</span>
              </Label>
              <Select 
                value={watch('status')} 
                onValueChange={(value) => setValue('status', value as any)}
              >
                <SelectTrigger className="border-gray-300 hover:border-indigo-400 focus:border-indigo-600 transition-colors">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PLANNED">Programmée</SelectItem>
                  <SelectItem value="MAKEUP">Rattrapage</SelectItem>
                  <SelectItem value="CANCELLED">Annulée</SelectItem>
                </SelectContent>
              </Select>
              {errors.status && (
                <p className="text-sm text-red-500 font-medium">{errors.status.message}</p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2 pt-4 border-t">
            {session && onDelete && (
              <Button
                type="button"
                onClick={handleDelete}
                disabled={isLoading}
                className="bg-red-600 hover:bg-red-700 text-white transition-all duration-200"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="mr-2 h-4 w-4" />
                )}
                Supprimer
              </Button>
            )}
            <Button
              type="button"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
              className="bg-gray-200 text-gray-900 hover:bg-gray-300 transition-all duration-200"
            >
              Annuler
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg transition-all duration-200"
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {session ? 'Mettre à jour' : 'Créer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}