'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Clock, User, MapPin, BookOpen, Calendar } from 'lucide-react'

interface TimeSlot {
  id: string
  start_time: string
  end_time: string
  label: string
}

interface TimetableEntry {
  id: string
  day_of_week: number // 1 = Monday, 2 = Tuesday, etc.
  time_slot: TimeSlot
  subject: {
    nom: string
    code?: string
  }
  teacher: {
    nom: string
    prenom: string
  }
  room: {
    nom: string
    type: string
  }
  group: {
    nom: string
  }
}

const DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
const DAY_NUMBERS = [1, 2, 3, 4, 5, 6]

const TIME_SLOTS = [
  { id: '1', start_time: '08:30', end_time: '10:00', label: '8h30 à 10h00' },
  { id: '2', start_time: '10:10', end_time: '11:40', label: '10h10 à 11h40' },
  { id: '3', start_time: '11:50', end_time: '13:20', label: '11h50 à 13h20' },
  { id: '4', start_time: '14:30', end_time: '16:00', label: '14h30 à 16h00' },
  { id: '5', start_time: '16:10', end_time: '17:40', label: '16h10 à 17h40' }
]

export default function TimetablePage() {
  const { user, loading } = useAuth()
  const [timetable, setTimetable] = useState<TimetableEntry[]>([])
  const [loadingTimetable, setLoadingTimetable] = useState(true)
  const [selectedWeek, setSelectedWeek] = useState(getCurrentWeek())
  const [viewMode, setViewMode] = useState<'student' | 'teacher'>('student')

  // Get current week (you can modify this to handle different weeks)
  function getCurrentWeek() {
    const now = new Date()
    const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay() + 1))
    return startOfWeek.toISOString().split('T')[0]
  }

  // Fetch timetable data
  useEffect(() => {
    const fetchTimetable = async () => {
      if (!user) return

      try {
        setLoadingTimetable(true)
        const token = localStorage.getItem('authToken')
        if (!token) return

        // Determine endpoint based on user role
        let endpoint = ''
        if (user.role === 'STUDENT') {
          endpoint = '/timetable/student'
          setViewMode('student')
        } else if (user.role === 'TEACHER') {
          endpoint = '/timetable/teacher'
          setViewMode('teacher')
        } else {
          // For admin/department head, default to teacher view
          endpoint = '/timetable/teacher'
          setViewMode('teacher')
        }

        const response = await fetch(`http://localhost:8000${endpoint}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          setTimetable(data)
        } else {
          console.error('Failed to fetch timetable:', response.status)
          // Mock data for development
          setTimetable(getMockTimetable())
        }
      } catch (error) {
        console.error('Error fetching timetable:', error)
        setTimetable(getMockTimetable())
      } finally {
        setLoadingTimetable(false)
      }
    }

    fetchTimetable()
  }, [user])

  // Mock data for development
  function getMockTimetable(): TimetableEntry[] {
    return [
      {
        id: '1',
        day_of_week: 1, // Monday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Algorithmique et programmation 1', code: 'ALGO1' },
        teacher: { nom: 'CHETOUI', prenom: 'Iftikhar' },
        room: { nom: 'TI 12', type: 'LAB' },
        group: { nom: 'TI 12' }
      },
      {
        id: '2',
        day_of_week: 1, // Monday
        time_slot: TIME_SLOTS[1],
        subject: { nom: 'High tech english', code: 'ENG1' },
        teacher: { nom: 'ARFAOUI', prenom: 'Dziriya' },
        room: { nom: 'DSI 23', type: 'LECTURE' },
        group: { nom: 'DSI 23' }
      },
      {
        id: '3',
        day_of_week: 2, // Tuesday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Algorithmique et programmation 1', code: 'ALGO1' },
        teacher: { nom: 'CHETOUI', prenom: 'Iftikhar' },
        room: { nom: 'TI 11', type: 'LAB' },
        group: { nom: 'TI 11' }
      },
      {
        id: '4',
        day_of_week: 2, // Tuesday
        time_slot: TIME_SLOTS[1],
        subject: { nom: 'Mathématique Appliquée', code: 'MATH1' },
        teacher: { nom: 'BEN YOUSSEF', prenom: 'Taher' },
        room: { nom: 'TI 11', type: 'LECTURE' },
        group: { nom: 'TI 11' }
      },
      {
        id: '5',
        day_of_week: 3, // Wednesday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Architecture des Ordinateurs', code: 'ARCH1' },
        teacher: { nom: 'RHILI', prenom: 'Rana' },
        room: { nom: 'TI 11', type: 'LECTURE' },
        group: { nom: 'TI 11' }
      }
    ]
  }

  // Get timetable entry for specific day and time slot
  function getTimetableEntry(dayNumber: number, timeSlot: TimeSlot): TimetableEntry | null {
    return timetable.find(entry => {
      // Match day and time slot by comparing start/end times
      return entry.day_of_week === dayNumber && 
             entry.time_slot.start_time === timeSlot.start_time &&
             entry.time_slot.end_time === timeSlot.end_time
    }) || null
  }

  // Render a timetable cell
  function renderTimetableCell(dayNumber: number, timeSlot: TimeSlot) {
    const entry = getTimetableEntry(dayNumber, timeSlot)
    
    if (!entry) {
      return (
        <td key={`${dayNumber}-${timeSlot.id}`} className="border p-2 h-24 bg-gray-50">
          <div className="text-center text-gray-400 text-sm">
            Libre
          </div>
        </td>
      )
    }

    return (
      <td key={`${dayNumber}-${timeSlot.id}`} className="border p-2 h-24 bg-white hover:bg-blue-50 transition-colors">
        <div className="h-full flex flex-col justify-between">
          <div>
            <div className="font-semibold text-sm text-blue-900 mb-1 leading-tight">
              {entry.subject.nom}
            </div>
            <div className="text-xs text-gray-600 flex items-center gap-1 mb-1">
              <User size={10} />
              {entry.teacher.prenom} {entry.teacher.nom}
            </div>
          </div>
          <div className="flex justify-between items-end">
            <div className="text-xs text-gray-500 flex items-center gap-1">
              <MapPin size={10} />
              {entry.room.nom}
            </div>
            <Badge variant="outline" className="text-xs px-1 py-0">
              {entry.group.nom}
            </Badge>
          </div>
        </div>
      </td>
    )
  }

  if (loading || loadingTimetable) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Emploi du Temps</h1>
          <p className="text-gray-600">
            {viewMode === 'student' ? 'Votre emploi du temps hebdomadaire' : 'Planning des cours'}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant="outline" className="flex items-center gap-2">
            <Calendar size={16} />
            Semaine du {selectedWeek}
          </Badge>
          <Button variant="outline" size="sm">
            <Clock size={16} className="mr-2" />
            Aujourd'hui
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Cours</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{timetable.length}</div>
            <p className="text-xs text-gray-600">Cette semaine</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Heures/Semaine</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {timetable.length * 1.5}h
            </div>
            <p className="text-xs text-gray-600">Temps total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Matières</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {new Set(timetable.map(t => t.subject.nom)).size}
            </div>
            <p className="text-xs text-gray-600">Différentes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {new Set(timetable.map(t => `${t.teacher.prenom} ${t.teacher.nom}`)).size}
            </div>
            <p className="text-xs text-gray-600">Différents</p>
          </CardContent>
        </Card>
      </div>

      {/* Timetable */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen size={20} />
            Emploi du Temps Hebdomadaire
          </CardTitle>
          <CardDescription>
            Planning fixe pour toute l'année académique
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-3 text-left font-semibold min-w-32">
                    Horaires
                  </th>
                  {DAYS.map(day => (
                    <th key={day} className="border border-gray-300 p-3 text-center font-semibold min-w-48">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map(timeSlot => (
                  <tr key={timeSlot.id}>
                    <td className="border border-gray-300 p-3 bg-gray-50 font-medium text-center">
                      <div className="text-sm font-semibold text-gray-700">
                        {timeSlot.start_time}
                      </div>
                      <div className="text-sm text-gray-500">à</div>
                      <div className="text-sm font-semibold text-gray-700">
                        {timeSlot.end_time}
                      </div>
                    </td>
                    {DAY_NUMBERS.map(dayNumber => 
                      renderTimetableCell(dayNumber, timeSlot)
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Légende</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <BookOpen size={16} className="text-blue-600" />
              <span>Nom de la matière</span>
            </div>
            <div className="flex items-center gap-2">
              <User size={16} className="text-gray-600" />
              <span>Enseignant</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin size={16} className="text-gray-500" />
              <span>Salle</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}