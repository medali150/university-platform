'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { api } from '@/lib/api'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Calendar, 
  Plus, 
  Users, 
  BookOpen, 
  MapPin, 
  User,
  Edit,
  Trash2,
  Clock,
  AlertTriangle,
  Filter,
  Download,
  Upload,
  RefreshCw,
  CheckCircle,
  XCircle,
  Search
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'

// Interfaces
interface Group {
  id: string
  nom: string
  niveau: {
    nom: string
    specialite: {
      nom: string
      departement: {
        nom: string
      }
    }
  }
}

interface Teacher {
  id: string
  nom: string
  prenom: string
  email: string
  utilisateur: {
    prenom: string
    nom: string
    email: string
  }
}

interface Subject {
  id: string
  nom: string
  specialite: {
    id: string
    nom: string
    departement: {
      nom: string
    }
  }
  enseignant: {
    nom: string
    prenom: string
  }
}

interface Speciality {
  id: string
  nom: string
  departement: {
    nom: string
  }
  _count?: {
    matieres: number
    niveaux: number
    etudiants: number
  }
}

interface Room {
  id: string
  code: string
  type: string
  capacite: number
}

interface Schedule {
  id: string
  date: string
  heure_debut: string
  heure_fin: string
  salle: Room
  matiere: Subject
  groupe: Group
  enseignant: Teacher
  status?: string
  created_at?: string
}

interface ScheduleFormData {
  date: string
  start_time: string
  end_time: string
  speciality_id: string
  subject_id: string
  group_id: string
  teacher_id: string
  room_id: string
}

interface Conflict {
  type: string
  message: string
  room?: string
  teacher?: string
  date: string
  time: string
  schedules: Array<{
    id: string
    time: string
    group: string
    subject: string
  }>
}

export default function DepartmentHeadTimetablePage() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  
  // Data states
  const [groups, setGroups] = useState<Group[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [specialities, setSpecialities] = useState<Speciality[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [conflicts, setConflicts] = useState<Conflict[]>([])
  
  // UI states
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('schedules')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null)
  
  // Form states
  const [formData, setFormData] = useState<ScheduleFormData>({
    date: '',
    start_time: '',
    end_time: '',
    speciality_id: '',
    subject_id: '',
    group_id: '',
    teacher_id: '',
    room_id: ''
  })
  
  // Filter states
  const [filters, setFilters] = useState({
    group_id: 'all',
    teacher_id: 'all',
    subject_id: 'all',
    speciality_id: 'all',
    room_id: 'all',
    date_from: '',
    date_to: '',
    search: ''
  })

  // Load data on mount
  useEffect(() => {
    loadInitialData()
  }, [])

  // Load schedules when filters change
  useEffect(() => {
    if (activeTab === 'schedules') {
      loadSchedules()
    } else if (activeTab === 'conflicts') {
      loadConflicts()
    }
  }, [activeTab, filters])

  // Auto-clear success messages
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        setSuccess(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [success])

  // Auto-clear error messages
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null)
      }, 8000)
      return () => clearTimeout(timer)
    }
  }, [error])

  const loadInitialData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [groupsRes, teachersRes, subjectsRes, specialitiesRes, roomsRes] = await Promise.allSettled([
        api.getTimetableGroups(),
        api.getTimetableTeachers(),
        api.getTimetableSubjects(),
        api.getTimetableSpecialities(),
        api.getTimetableRooms()
      ])
      
      if (groupsRes.status === 'fulfilled') {
        setGroups(groupsRes.value as Group[])
      }
      if (teachersRes.status === 'fulfilled') {
        setTeachers(teachersRes.value as Teacher[])
      }
      if (subjectsRes.status === 'fulfilled') {
        setSubjects(subjectsRes.value as Subject[])
      }
      if (specialitiesRes.status === 'fulfilled') {
        setSpecialities(specialitiesRes.value as Speciality[])
      }
      if (roomsRes.status === 'fulfilled') {
        setRooms(roomsRes.value as Room[])
      }
    } catch (err: any) {
      setError('Erreur lors du chargement des données: ' + (err.message || 'Erreur inconnue'))
    } finally {
      setLoading(false)
    }
  }

  const loadSchedules = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== 'all') params.append(key, value)
      })
      
      const response = await api.getTimetableSchedules(params)
      setSchedules(Array.isArray(response) ? response as Schedule[] : [])
    } catch (err: any) {
      setError('Erreur lors du chargement des emplois du temps: ' + (err.message || 'Erreur inconnue'))
      setSchedules([])
    } finally {
      setLoading(false)
    }
  }

  const loadConflicts = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.date_from) params.append('date_from', filters.date_from)
      if (filters.date_to) params.append('date_to', filters.date_to)
      
      const response = await api.getTimetableConflicts(params)
      setConflicts(response.conflicts || [])
    } catch (err: any) {
      setError('Erreur lors de la vérification des conflits: ' + (err.message || 'Erreur inconnue'))
      setConflicts([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSchedule = async () => {
    if (!formData.date || !formData.start_time || !formData.end_time || !formData.speciality_id ||
        !formData.subject_id || !formData.group_id || !formData.teacher_id || !formData.room_id) {
      setError('Tous les champs sont requis')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await api.createTimetableSchedule({
        date: formData.date,
        heure_debut: formData.start_time,
        heure_fin: formData.end_time,
        matiere_id: formData.subject_id,
        groupe_id: formData.group_id,
        enseignant_id: formData.teacher_id,
        salle_id: formData.room_id
      })
      
      setShowCreateDialog(false)
      setFormData({
        date: '',
        start_time: '',
        end_time: '',
        speciality_id: '',
        subject_id: '',
        group_id: '',
        teacher_id: '',
        room_id: ''
      })
      setSuccess('Emploi du temps créé avec succès!')
      await loadSchedules()
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la création')
    } finally {
      setLoading(false)
    }
  }

  const handleEditSchedule = (schedule: Schedule) => {
    setEditingSchedule(schedule)
    setFormData({
      date: schedule.date,
      start_time: schedule.heure_debut,
      end_time: schedule.heure_fin,
      speciality_id: schedule.matiere.specialite.id,
      subject_id: schedule.matiere.id,
      group_id: schedule.groupe.id,
      teacher_id: schedule.enseignant.id,
      room_id: schedule.salle.id
    })
    setShowEditDialog(true)
  }

  const handleUpdateSchedule = async () => {
    if (!editingSchedule) return

    try {
      setLoading(true)
      setError(null)
      
      await api.updateTimetableSchedule(editingSchedule.id, {
        date: formData.date,
        heure_debut: formData.start_time,
        heure_fin: formData.end_time,
        matiere_id: formData.subject_id,
        groupe_id: formData.group_id,
        enseignant_id: formData.teacher_id,
        salle_id: formData.room_id
      })
      
      setShowEditDialog(false)
      setEditingSchedule(null)
      setFormData({
        date: '',
        start_time: '',
        end_time: '',
        speciality_id: '',
        subject_id: '',
        group_id: '',
        teacher_id: '',
        room_id: ''
      })
      setSuccess('Emploi du temps modifié avec succès!')
      await loadSchedules()
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la modification')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSchedule = async (scheduleId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet emploi du temps ?')) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await api.deleteTimetableSchedule(scheduleId)
      
      setSuccess('Emploi du temps supprimé avec succès!')
      await loadSchedules()
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la suppression')
    } finally {
      setLoading(false)
    }
  }

  const resetFilters = () => {
    setFilters({
      group_id: 'all',
      teacher_id: 'all',
      subject_id: 'all',
      speciality_id: 'all',
      room_id: 'all',
      date_from: '',
      date_to: '',
      search: ''
    })
  }

  const formatTime = (time: string) => {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (isLoading && schedules.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <Link 
                href="/dashboard/department-head" 
                className="p-2 rounded-lg bg-white shadow-sm hover:shadow-md transition-all duration-200 text-blue-600 hover:text-blue-800"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Gestion des Emplois du Temps
                </h1>
                <p className="text-gray-600">
                  Planifiez et organisez les cours de votre département
                </p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Exporter
              </Button>
              <Button variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-2" />
                Importer
              </Button>
            </div>
          </div>

          {/* Alert Messages */}
          {error && (
            <div className="mb-4 border border-red-200 bg-red-50 p-4 rounded-lg flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0" />
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 border border-green-200 bg-green-50 p-4 rounded-lg flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              <p className="text-green-800">{success}</p>
            </div>
          )}

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">Groupes</p>
                    <p className="text-3xl font-bold">{groups.length}</p>
                  </div>
                  <Users className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">Enseignants</p>
                    <p className="text-3xl font-bold">{teachers.length}</p>
                  </div>
                  <User className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">Matières</p>
                    <p className="text-3xl font-bold">{subjects.length}</p>
                  </div>
                  <BookOpen className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm font-medium">Salles</p>
                    <p className="text-3xl font-bold">{rooms.length}</p>
                  </div>
                  <MapPin className="h-8 w-8 text-orange-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('schedules')}
                className={`px-4 py-2 rounded-md transition-all ${
                  activeTab === 'schedules' 
                    ? 'bg-white shadow-sm text-blue-600 font-medium' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Emplois du Temps
              </button>
              <button
                onClick={() => setActiveTab('conflicts')}
                className={`px-4 py-2 rounded-md transition-all ${
                  activeTab === 'conflicts' 
                    ? 'bg-white shadow-sm text-blue-600 font-medium' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Conflits
              </button>
              <button
                onClick={() => setActiveTab('calendar')}
                className={`px-4 py-2 rounded-md transition-all ${
                  activeTab === 'calendar' 
                    ? 'bg-white shadow-sm text-blue-600 font-medium' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Calendrier
              </button>
            </div>

            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Nouveau Planning
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Créer un nouvel emploi du temps</DialogTitle>
                  <DialogDescription>
                    Planifiez une nouvelle session de cours pour votre département
                  </DialogDescription>
                </DialogHeader>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="group">Groupe</Label>
                    <Select 
                      value={formData.group_id} 
                      onValueChange={(value) => setFormData(prev => ({ ...prev, group_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un groupe" />
                      </SelectTrigger>
                      <SelectContent>
                        {groups.map(group => (
                          <SelectItem key={group.id} value={group.id}>
                            {group.nom} - {group.niveau?.specialite?.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="start-time">Heure de début</Label>
                    <Input
                      id="start-time"
                      type="time"
                      value={formData.start_time}
                      onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="end-time">Heure de fin</Label>
                    <Input
                      id="end-time"
                      type="time"
                      value={formData.end_time}
                      onChange={(e) => setFormData(prev => ({ ...prev, end_time: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="speciality">Spécialité</Label>
                    <Select 
                      value={formData.speciality_id} 
                      onValueChange={(value) => {
                        setFormData(prev => ({ ...prev, speciality_id: value, subject_id: '' }))
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner une spécialité" />
                      </SelectTrigger>
                      <SelectContent>
                        {specialities.map(speciality => (
                          <SelectItem key={speciality.id} value={speciality.id}>
                            {speciality.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject">Matière</Label>
                    <Select 
                      value={formData.subject_id} 
                      onValueChange={(value) => setFormData(prev => ({ ...prev, subject_id: value }))}
                      disabled={!formData.speciality_id}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={
                          !formData.speciality_id 
                            ? "Sélectionner d'abord une spécialité" 
                            : "Sélectionner une matière"
                        } />
                      </SelectTrigger>
                      <SelectContent>
                        {subjects
                          .filter(subject => subject.specialite.id === formData.speciality_id)
                          .map(subject => (
                          <SelectItem key={subject.id} value={subject.id}>
                            {subject.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="teacher">Enseignant</Label>
                    <Select 
                      value={formData.teacher_id} 
                      onValueChange={(value) => setFormData(prev => ({ ...prev, teacher_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un enseignant" />
                      </SelectTrigger>
                      <SelectContent>
                        {teachers.map(teacher => (
                          <SelectItem key={teacher.id} value={teacher.id}>
                            {teacher.utilisateur?.prenom || teacher.prenom} {teacher.utilisateur?.nom || teacher.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="room">Salle</Label>
                    <Select 
                      value={formData.room_id} 
                      onValueChange={(value) => setFormData(prev => ({ ...prev, room_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner une salle" />
                      </SelectTrigger>
                      <SelectContent>
                        {rooms.map(room => (
                          <SelectItem key={room.id} value={room.id}>
                            {room.code} - {room.type} ({room.capacite} places)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <DialogFooter>
                  <Button 
                    variant="outline" 
                    onClick={() => setShowCreateDialog(false)}
                    disabled={loading}
                  >
                    Annuler
                  </Button>
                  <Button 
                    onClick={handleCreateSchedule}
                    disabled={loading}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Création...
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-2" />
                        Créer
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {activeTab === 'schedules' && (
            <div className="space-y-6">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filtres
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="space-y-2">
                    <Label>Recherche</Label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Rechercher..."
                        className="pl-10"
                        value={filters.search}
                        onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Groupe</Label>
                    <Select 
                      value={filters.group_id} 
                      onValueChange={(value) => setFilters(prev => ({ ...prev, group_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Tous" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Tous les groupes</SelectItem>
                        {groups.map(group => (
                          <SelectItem key={group.id} value={group.id}>
                            {group.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Enseignant</Label>
                    <Select 
                      value={filters.teacher_id} 
                      onValueChange={(value) => setFilters(prev => ({ ...prev, teacher_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Tous" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Tous les enseignants</SelectItem>
                        {teachers.map(teacher => (
                          <SelectItem key={teacher.id} value={teacher.id}>
                            {teacher.utilisateur?.prenom || teacher.prenom} {teacher.utilisateur?.nom || teacher.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Spécialité</Label>
                    <Select 
                      value={filters.speciality_id} 
                      onValueChange={(value) => setFilters(prev => ({ ...prev, speciality_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Toutes" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Toutes les spécialités</SelectItem>
                        {specialities.map(speciality => (
                          <SelectItem key={speciality.id} value={speciality.id}>
                            {speciality.nom}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Matière</Label>
                    <Select 
                      value={filters.subject_id} 
                      onValueChange={(value) => setFilters(prev => ({ ...prev, subject_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Toutes" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Toutes les matières</SelectItem>
                        {subjects
                          .filter(subject => 
                            filters.speciality_id === 'all' || 
                            subject.specialite.id === filters.speciality_id
                          )
                          .map(subject => (
                          <SelectItem key={subject.id} value={subject.id}>
                            {subject.nom} ({subject.specialite.nom})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Date début</Label>
                    <Input
                      type="date"
                      value={filters.date_from}
                      onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Date fin</Label>
                    <Input
                      type="date"
                      value={filters.date_to}
                      onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>&nbsp;</Label>
                    <Button variant="outline" onClick={resetFilters} className="w-full">
                      Réinitialiser
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Schedules Table */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Emplois du Temps</CardTitle>
                    <CardDescription>
                      {schedules.length} emploi(s) du temps trouvé(s)
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={loadSchedules}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Actualiser
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {schedules.length > 0 ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Heure</TableHead>
                          <TableHead>Matière</TableHead>
                          <TableHead>Groupe</TableHead>
                          <TableHead>Enseignant</TableHead>
                          <TableHead>Salle</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {schedules.map((schedule) => (
                          <TableRow key={schedule.id} className="hover:bg-gray-50/50 transition-colors">
                            <TableCell className="font-medium">
                              {formatDate(schedule.date)}
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline" className="font-mono">
                                {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">{schedule.matiere?.nom}</p>
                                <p className="text-sm text-gray-500">{schedule.matiere?.specialite?.nom}</p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">{schedule.groupe?.nom}</p>
                                <p className="text-sm text-gray-500">{schedule.groupe?.niveau?.specialite?.nom}</p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div>
                                <p className="font-medium">
                                  {schedule.enseignant?.utilisateur?.prenom || schedule.enseignant?.prenom} {' '}
                                  {schedule.enseignant?.utilisateur?.nom || schedule.enseignant?.nom}
                                </p>
                                <p className="text-sm text-gray-500">{schedule.enseignant?.email}</p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant="secondary">
                                {schedule.salle?.code} ({schedule.salle?.capacite} places)
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => handleEditSchedule(schedule)}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => handleDeleteSchedule(schedule.id)}
                                  className="text-red-600 hover:text-red-700 hover:border-red-300"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Aucun emploi du temps trouvé
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Commencez par créer votre premier emploi du temps
                    </p>
                    <Button onClick={() => setShowCreateDialog(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Créer un emploi du temps
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
            </div>
          )}

          {activeTab === 'conflicts' && (
            <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-orange-500" />
                      Conflits Détectés
                    </CardTitle>
                    <CardDescription>
                      {conflicts.length} conflit(s) détecté(s)
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={loadConflicts}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Vérifier les conflits
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {conflicts.length > 0 ? (
                  <div className="space-y-4">
                    {conflicts.map((conflict, index) => (
                      <div key={index} className="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-red-800">
                              {conflict.type} - {conflict.message}
                            </h4>
                            <p className="text-red-600 text-sm mt-1">
                              {formatDate(conflict.date)} à {conflict.time}
                            </p>
                            {conflict.room && (
                              <p className="text-red-600 text-sm">Salle: {conflict.room}</p>
                            )}
                            {conflict.teacher && (
                              <p className="text-red-600 text-sm">Enseignant: {conflict.teacher}</p>
                            )}
                            {conflict.schedules.length > 0 && (
                              <div className="mt-2">
                                <p className="text-red-700 text-sm font-medium">Sessions en conflit:</p>
                                <ul className="text-red-600 text-sm mt-1">
                                  {conflict.schedules.map((schedule, idx) => (
                                    <li key={idx} className="ml-4">
                                      • {schedule.subject} - {schedule.group} ({schedule.time})
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                          <Button size="sm" variant="destructive" className="ml-4">
                            Résoudre
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-500" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Aucun conflit détecté
                    </h3>
                    <p className="text-gray-600">
                      Tous les emplois du temps sont compatibles
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
            </div>
          )}

          {activeTab === 'calendar' && (
            <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Vue Calendrier
                </CardTitle>
                <CardDescription>
                  Visualisation calendaire des emplois du temps
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Calendar className="h-16 w-16 mx-auto mb-4 text-blue-500" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Vue Calendrier
                  </h3>
                  <p className="text-gray-600 mb-4">
                    La vue calendrier sera disponible prochainement
                  </p>
                  <p className="text-sm text-gray-500">
                    Vous pourrez visualiser vos emplois du temps sous forme de calendrier interactif
                  </p>
                </div>
              </CardContent>
            </Card>
            </div>
          )}
        </div>

        {/* Edit Dialog */}
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Modifier l'emploi du temps</DialogTitle>
              <DialogDescription>
                Modifiez les détails de cette session de cours
              </DialogDescription>
            </DialogHeader>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-date">Date</Label>
                <Input
                  id="edit-date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="edit-group">Groupe</Label>
                <Select 
                  value={formData.group_id} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, group_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner un groupe" />
                  </SelectTrigger>
                  <SelectContent>
                    {groups.map(group => (
                      <SelectItem key={group.id} value={group.id}>
                        {group.nom} - {group.niveau?.specialite?.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-start-time">Heure de début</Label>
                <Input
                  id="edit-start-time"
                  type="time"
                  value={formData.start_time}
                  onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-end-time">Heure de fin</Label>
                <Input
                  id="edit-end-time"
                  type="time"
                  value={formData.end_time}
                  onChange={(e) => setFormData(prev => ({ ...prev, end_time: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-speciality">Spécialité</Label>
                <Select 
                  value={formData.speciality_id} 
                  onValueChange={(value) => {
                    setFormData(prev => ({ ...prev, speciality_id: value, subject_id: '' }))
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner une spécialité" />
                  </SelectTrigger>
                  <SelectContent>
                    {specialities.map(speciality => (
                      <SelectItem key={speciality.id} value={speciality.id}>
                        {speciality.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-subject">Matière</Label>
                <Select 
                  value={formData.subject_id} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, subject_id: value }))}
                  disabled={!formData.speciality_id}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={
                      !formData.speciality_id 
                        ? "Sélectionner d'abord une spécialité" 
                        : "Sélectionner une matière"
                    } />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects
                      .filter(subject => subject.specialite.id === formData.speciality_id)
                      .map(subject => (
                      <SelectItem key={subject.id} value={subject.id}>
                        {subject.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-teacher">Enseignant</Label>
                <Select 
                  value={formData.teacher_id} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, teacher_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner un enseignant" />
                  </SelectTrigger>
                  <SelectContent>
                    {teachers.map(teacher => (
                      <SelectItem key={teacher.id} value={teacher.id}>
                        {teacher.utilisateur?.prenom || teacher.prenom} {teacher.utilisateur?.nom || teacher.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-room">Salle</Label>
                <Select 
                  value={formData.room_id} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, room_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner une salle" />
                  </SelectTrigger>
                  <SelectContent>
                    {rooms.map(room => (
                      <SelectItem key={room.id} value={room.id}>
                        {room.code} - {room.type} ({room.capacite} places)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <DialogFooter>
              <Button 
                variant="outline" 
                onClick={() => setShowEditDialog(false)}
                disabled={loading}
              >
                Annuler
              </Button>
              <Button 
                onClick={handleUpdateSchedule}
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Modification...
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Modifier
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
