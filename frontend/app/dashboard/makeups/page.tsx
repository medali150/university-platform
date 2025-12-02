'use client'

import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { BookOpen, Calendar, Clock, Users, Search, Plus, Check, X, Eye, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import {
  getMakeupSessions,
  getMakeupStats,
  createMakeupSession,
  reviewMakeupSession,
  scheduleMakeupSession,
  completeMakeupSession,
  deleteMakeupSession,
  formatMakeupDate,
  getStatusColor,
  getStatusLabel,
  type MakeupSession,
  type MakeupStats,
  type MakeupStatus,
  type CreateMakeupSession,
} from '@/lib/makeup-api'
import { useToast } from '@/hooks/use-toast'

export default function MakeupsPage() {
  const { user, loading } = useAuth()
  const { toast } = useToast()
  
  // State
  const [sessions, setSessions] = useState<MakeupSession[]>([])
  const [stats, setStats] = useState<MakeupStats | null>(null)
  const [loadingData, setLoadingData] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<MakeupStatus | 'ALL'>('ALL')
  const [selectedSession, setSelectedSession] = useState<MakeupSession | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [createFormData, setCreateFormData] = useState<Partial<CreateMakeupSession>>({
    motif: '',
  })
  
  // Teacher data
  const [teacherInfo, setTeacherInfo] = useState<any>(null)
  const [teacherSubjects, setTeacherSubjects] = useState<any[]>([])
  const [teacherGroups, setTeacherGroups] = useState<any[]>([])
  const [loadingTeacherData, setLoadingTeacherData] = useState(false)

  // Load data
  useEffect(() => {
    if (user) {
      loadData()
      if (user.role === 'TEACHER') {
        loadTeacherData()
      }
    }
  }, [user, statusFilter])

  const loadData = async () => {
    try {
      setLoadingData(true)
      const [sessionsData, statsData] = await Promise.all([
        getMakeupSessions(statusFilter !== 'ALL' ? { status: statusFilter } : undefined),
        getMakeupStats(),
      ])
      setSessions(sessionsData)
      setStats(statsData)
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors du chargement des données',
        variant: 'destructive',
      })
    } finally {
      setLoadingData(false)
    }
  }

  const loadTeacherData = async () => {
    try {
      setLoadingTeacherData(true)
      const token = localStorage.getItem('token')
      if (!token) return

      // Fetch teacher profile, subjects, and groups
      const [profileRes, subjectsRes, groupsRes] = await Promise.all([
        fetch('http://localhost:8000/teacher/profile', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/teacher/subjects', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/teacher/groups', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])

      if (profileRes.ok && subjectsRes.ok && groupsRes.ok) {
        const profile = await profileRes.json()
        const subjects = await subjectsRes.json()
        const groups = await groupsRes.json()
        
        setTeacherInfo(profile.teacher_info)
        setTeacherSubjects(subjects)
        setTeacherGroups(groups)
        
        // Auto-fill teacher ID
        setCreateFormData(prev => ({
          ...prev,
          id_enseignant: profile.teacher_info.id
        }))
      }
    } catch (error) {
      console.error('Error loading teacher data:', error)
    } finally {
      setLoadingTeacherData(false)
    }
  }

  // Handle actions
  const handleApprove = async (sessionId: string) => {
    try {
      setActionLoading(true)
      await reviewMakeupSession(sessionId, { statut: 'APPROVED' })
      toast({
        title: 'Succès',
        description: 'Séance de rattrapage approuvée',
      })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors de l\'approbation',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async (sessionId: string, notes?: string) => {
    try {
      setActionLoading(true)
      await reviewMakeupSession(sessionId, { statut: 'REJECTED', notes_validation: notes })
      toast({
        title: 'Succès',
        description: 'Séance de rattrapage rejetée',
      })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors du rejet',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleSchedule = async (sessionId: string) => {
    try {
      setActionLoading(true)
      await scheduleMakeupSession(sessionId)
      toast({
        title: 'Succès',
        description: 'Séance programmée',
      })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors de la programmation',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleComplete = async (sessionId: string) => {
    try {
      setActionLoading(true)
      await completeMakeupSession(sessionId)
      toast({
        title: 'Succès',
        description: 'Séance marquée comme terminée',
      })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors de la completion',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (sessionId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette séance ?')) return
    
    try {
      setActionLoading(true)
      await deleteMakeupSession(sessionId)
      toast({
        title: 'Succès',
        description: 'Séance supprimée',
      })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors de la suppression',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      // Validate form data
      if (!createFormData.id_matiere || 
          !createFormData.id_enseignant || !createFormData.id_groupe ||
          !createFormData.date_originale || !createFormData.heure_debut_origin ||
          !createFormData.heure_fin_origin || !createFormData.date_proposee ||
          !createFormData.heure_debut_proposee || !createFormData.heure_fin_proposee ||
          !createFormData.motif) {
        toast({
          title: 'Erreur',
          description: 'Veuillez remplir tous les champs obligatoires',
          variant: 'destructive',
        })
        return
      }

      // Generate emploi du temps ID from components
      const emploiTempsId = `et_${createFormData.id_matiere}_${createFormData.id_groupe}_${Date.now()}`
      
      const sessionData: CreateMakeupSession = {
        ...createFormData as CreateMakeupSession,
        id_emploitemps_origin: emploiTempsId
      }

      setActionLoading(true)
      await createMakeupSession(sessionData)
      
      toast({
        title: 'Succès',
        description: 'Demande de rattrapage créée avec succès',
      })
      
      setShowCreateDialog(false)
      setCreateFormData({ motif: '' })
      await loadData()
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error instanceof Error ? error.message : 'Erreur lors de la création',
        variant: 'destructive',
      })
    } finally {
      setActionLoading(false)
    }
  }

  if (loading || loadingData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) return null

  // Filter sessions
  const filteredSessions = sessions.filter((session) =>
    session.subject.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.teacher.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.group.nom.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Get role message
  const getRoleMessage = () => {
    switch (user.role) {
      case 'TEACHER':
        return 'Gérez vos séances de rattrapage et consultez leur statut'
      case 'DEPARTMENT_HEAD':
        return 'Approuvez ou rejetez les demandes de rattrapage'
      case 'ADMIN':
        return 'Vue d\'ensemble de tous les rattrapages'
      default:
        return 'Consultez les séances de rattrapage de votre groupe'
    }
  }

  const canReview = user.role === 'DEPARTMENT_HEAD' || user.role === 'ADMIN'
  const canSchedule = user.role === 'DEPARTMENT_HEAD' || user.role === 'ADMIN'
  const canComplete = user.role === 'TEACHER' || user.role === 'DEPARTMENT_HEAD' || user.role === 'ADMIN'

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 min-h-screen">
      {/* Header with gradient */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-2xl shadow-2xl p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Séances de Rattrapage</h1>
            <p className="text-blue-100 text-lg">{getRoleMessage()}</p>
          </div>
          {(user.role === 'TEACHER' || user.role === 'DEPARTMENT_HEAD' || user.role === 'ADMIN') && (
            <Button
              size="lg"
              className="bg-white text-blue-600 hover:bg-blue-50 shadow-lg"
              onClick={() => {
                setShowCreateDialog(true)
                if (user.role === 'TEACHER' && !teacherInfo) {
                  loadTeacherData()
                }
              }}
            >
              <Plus className="mr-2 h-5 w-5" />
              Nouvelle demande
            </Button>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.total}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                  <BookOpen className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-950 dark:to-yellow-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-yellow-700 dark:text-yellow-300">En attente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Approuvées</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.approved}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
                  <CheckCircle className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-blue-50 to-cyan-100 dark:from-blue-950 dark:to-cyan-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Programmées</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.scheduled}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-cyan-600 flex items-center justify-center">
                  <Calendar className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Terminées</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">{stats.completed}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
                  <Check className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950 dark:to-red-900">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-red-700 dark:text-red-300">Rejetées</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600 dark:text-red-400">{stats.rejected}</div>
              <div className="flex items-center gap-2 mt-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-400 to-red-600 flex items-center justify-center">
                  <XCircle className="h-5 w-5 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            Filtrer les séances
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Rechercher par matière, enseignant ou groupe..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as MakeupStatus | 'ALL')}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Tous les statuts" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Tous les statuts</SelectItem>
                <SelectItem value="PENDING">En attente</SelectItem>
                <SelectItem value="APPROVED">Approuvées</SelectItem>
                <SelectItem value="REJECTED">Rejetées</SelectItem>
                <SelectItem value="SCHEDULED">Programmées</SelectItem>
                <SelectItem value="COMPLETED">Terminées</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Sessions List */}
      <div className="space-y-4">
        {filteredSessions.length === 0 ? (
          <Card className="border-0 shadow-lg">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500 text-lg">Aucune séance de rattrapage trouvée</p>
            </CardContent>
          </Card>
        ) : (
          filteredSessions.map((session) => (
            <Card key={session.id} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-xl">{session.subject.nom}</CardTitle>
                      <Badge className={`${getStatusColor(session.status)} text-white`}>
                        {getStatusLabel(session.status)}
                      </Badge>
                    </div>
                    <CardDescription className="text-base">
                      {session.teacher.fullName} • {session.group.nom} • {session.studentCount} étudiants
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Original Session Info */}
                <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-red-700 dark:text-red-300 mb-2">Séance originale (annulée)</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-red-600" />
                      <span>{formatMakeupDate(session.originalDate)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-red-600" />
                      <span>{session.originalStartTime} - {session.originalEndTime}</span>
                    </div>
                  </div>
                </div>

                {/* Proposed Session Info */}
                <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">Séance proposée</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-green-600" />
                      <span>{formatMakeupDate(session.proposedDate)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-green-600" />
                      <span>{session.proposedStartTime} - {session.proposedEndTime}</span>
                    </div>
                    {session.room && (
                      <div className="flex items-center gap-2 col-span-2">
                        <BookOpen className="h-4 w-4 text-green-600" />
                        <span>{session.room.code} (Capacité: {session.room.capacite})</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Reason */}
                <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">Motif</h4>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{session.reason}</p>
                </div>

                {/* Validation Notes */}
                {session.validationNotes && (
                  <div className="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">Notes de validation</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{session.validationNotes}</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  {canReview && session.status === 'PENDING' && (
                    <>
                      <Button
                        size="sm"
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => handleApprove(session.id)}
                        disabled={actionLoading}
                      >
                        <Check className="mr-2 h-4 w-4" />
                        Approuver
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleReject(session.id)}
                        disabled={actionLoading}
                      >
                        <X className="mr-2 h-4 w-4" />
                        Rejeter
                      </Button>
                    </>
                  )}
                  
                  {canSchedule && session.status === 'APPROVED' && (
                    <Button
                      size="sm"
                      className="bg-blue-600 hover:bg-blue-700"
                      onClick={() => handleSchedule(session.id)}
                      disabled={actionLoading}
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      Programmer
                    </Button>
                  )}
                  
                  {canComplete && session.status === 'SCHEDULED' && (
                    <Button
                      size="sm"
                      className="bg-purple-600 hover:bg-purple-700"
                      onClick={() => handleComplete(session.id)}
                      disabled={actionLoading}
                    >
                      <Check className="mr-2 h-4 w-4" />
                      Marquer comme terminée
                    </Button>
                  )}

                  {(session.status === 'PENDING' || session.status === 'REJECTED') && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="ml-auto"
                      onClick={() => handleDelete(session.id)}
                      disabled={actionLoading}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Supprimer
                    </Button>
                  )}

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedSession(session)}
                  >
                    <Eye className="mr-2 h-4 w-4" />
                    Détails
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Create Makeup Session Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Nouvelle demande de rattrapage
            </DialogTitle>
            <DialogDescription>
              Remplissez les informations pour créer une demande de séance de rattrapage
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Teacher Info */}
            {teacherInfo && (
              <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">Enseignant</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {teacherInfo.prenom} {teacherInfo.nom}
                </p>
                <p className="text-xs text-gray-500">{teacherInfo.email}</p>
              </div>
            )}

            {/* Original Session Info */}
            <div className="space-y-3">
              <h3 className="font-semibold text-lg">Séance originale (annulée)</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="id_matiere">Matière *</Label>
                  <Select 
                    value={createFormData.id_matiere || ''} 
                    onValueChange={(value) => setCreateFormData({ ...createFormData, id_matiere: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionnez une matière" />
                    </SelectTrigger>
                    <SelectContent>
                      {teacherSubjects.map((subject) => (
                        <SelectItem key={subject.id} value={subject.id}>
                          {subject.nom}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="id_groupe">Groupe *</Label>
                  <Select 
                    value={createFormData.id_groupe || ''} 
                    onValueChange={(value) => setCreateFormData({ ...createFormData, id_groupe: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionnez un groupe" />
                    </SelectTrigger>
                    <SelectContent>
                      {teacherGroups.map((group) => (
                        <SelectItem key={group.id} value={group.id}>
                          {group.nom}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="date_originale">Date originale *</Label>
                  <Input
                    id="date_originale"
                    type="date"
                    value={createFormData.date_originale || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, date_originale: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="id_salle">ID Salle (optionnel)</Label>
                  <Input
                    id="id_salle"
                    placeholder="Ex: sal_123456"
                    value={createFormData.id_salle || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, id_salle: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="heure_debut_origin">Heure début *</Label>
                  <Input
                    id="heure_debut_origin"
                    type="time"
                    value={createFormData.heure_debut_origin || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, heure_debut_origin: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="heure_fin_origin">Heure fin *</Label>
                  <Input
                    id="heure_fin_origin"
                    type="time"
                    value={createFormData.heure_fin_origin || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, heure_fin_origin: e.target.value })}
                  />
                </div>
              </div>
            </div>

            <div className="border-t pt-4 space-y-3">
              <h3 className="font-semibold text-lg">Séance proposée</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date_proposee">Date proposée *</Label>
                  <Input
                    id="date_proposee"
                    type="date"
                    value={createFormData.date_proposee || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, date_proposee: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="heure_debut_proposee">Heure début *</Label>
                  <Input
                    id="heure_debut_proposee"
                    type="time"
                    value={createFormData.heure_debut_proposee || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, heure_debut_proposee: e.target.value })}
                  />
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="heure_fin_proposee">Heure fin *</Label>
                  <Input
                    id="heure_fin_proposee"
                    type="time"
                    value={createFormData.heure_fin_proposee || ''}
                    onChange={(e) => setCreateFormData({ ...createFormData, heure_fin_proposee: e.target.value })}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="motif">Motif de l'annulation *</Label>
              <Textarea
                id="motif"
                placeholder="Expliquez la raison de l'annulation de la séance originale..."
                value={createFormData.motif || ''}
                onChange={(e) => setCreateFormData({ ...createFormData, motif: e.target.value })}
                rows={4}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateDialog(false)
                setCreateFormData({ motif: '' })
              }}
              disabled={actionLoading}
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreateSession}
              disabled={actionLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              {actionLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Création...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Créer la demande
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
