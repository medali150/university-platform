'use client'

import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BookOpen, Calendar, Clock, Users, Search, Plus, Check, X, Eye, AlertCircle } from 'lucide-react'
import { useState } from 'react'

export default function MakeupsPage() {
  const { user, loading } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedMakeup, setSelectedMakeup] = useState<number | null>(null)

  if (loading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const makeupSessions = [
    {
      id: 1,
      subject: 'Mathématiques Fondamentales',
      teacher: 'Prof. Martin',
      originalDate: '2024-09-28',
      originalTime: '08:00-10:00',
      proposedDate: '2024-10-05',
      proposedTime: '14:00-16:00',
      room: 'Salle A101',
      reason: 'Absence enseignant - Formation obligatoire',
      students: ['Jean Dupont', 'Marie Laurent', 'Pierre Bernard'],
      status: 'pending',
      createdBy: 'Prof. Martin',
      createdAt: '2024-09-29 10:00',
      group: 'Groupe A'
    },
    {
      id: 2,
      subject: 'Physique Générale',
      teacher: 'Prof. Dubois',
      originalDate: '2024-09-27',
      originalTime: '14:00-16:00',
      proposedDate: '2024-10-03',
      proposedTime: '10:30-12:30',
      room: 'Labo Physique 1',
      reason: 'Panne équipement - Expérience reportée',
      students: ['Sophie Martin', 'Antoine Petit', 'Julie Moreau'],
      status: 'approved',
      createdBy: 'Prof. Dubois',
      createdAt: '2024-09-27 16:30',
      group: 'Groupe B'
    },
    {
      id: 3,
      subject: 'Chimie Organique',
      teacher: 'Prof. Laurent',
      originalDate: '2024-09-26',
      originalTime: '10:30-12:30',
      proposedDate: '2024-10-02',
      proposedTime: '08:00-10:00',
      room: 'Labo Chimie 2',
      reason: 'Évacuation bâtiment - Alarme incendie',
      students: ['Lucas Dubois', 'Emma Martin'],
      status: 'rejected',
      createdBy: 'Dept. Head',
      createdAt: '2024-09-26 15:45',
      group: 'Groupe C',
      rejectionReason: 'Conflit avec autre cours du groupe'
    },
    {
      id: 4,
      subject: 'Informatique Théorique',
      teacher: 'Prof. Rousseau',
      originalDate: '2024-09-25',
      originalTime: '09:30-11:30',
      proposedDate: '2024-10-01',
      proposedTime: '15:30-17:30',
      room: 'Salle Info B12',
      reason: 'Maintenance serveurs - Cours pratique impossible',
      students: ['Alice Bernard', 'Thomas Laurent', 'Clara Petit', 'Nicolas Moreau'],
      status: 'scheduled',
      createdBy: 'Prof. Rousseau',
      createdAt: '2024-09-25 12:00',
      group: 'Groupe A'
    },
    {
      id: 5,
      subject: 'Statistiques Appliquées',
      teacher: 'Prof. Moreau',
      originalDate: '2024-09-24',
      originalTime: '15:30-17:30',
      proposedDate: '2024-09-30',
      proposedTime: '13:00-15:00',
      room: 'Salle C205',
      reason: 'Grève transports - Trop d\'absents',
      students: ['Paul Dupont', 'Léa Martin'],
      status: 'completed',
      createdBy: 'Prof. Moreau',
      createdAt: '2024-09-24 18:00',
      group: 'Groupe B'
    }
  ]

  const filteredMakeups = makeupSessions.filter(makeup =>
    makeup.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    makeup.teacher.toLowerCase().includes(searchTerm.toLowerCase()) ||
    makeup.reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
    makeup.students.some(student => student.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">En Attente</Badge>
      case 'approved':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Approuvée</Badge>
      case 'rejected':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Rejetée</Badge>
      case 'scheduled':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Programmée</Badge>
      case 'completed':
        return <Badge variant="secondary" className="bg-gray-100 text-gray-800">Terminée</Badge>
      default:
        return <Badge variant="secondary">Inconnu</Badge>
    }
  }

  const selectedMakeupData = selectedMakeup ? makeupSessions.find(makeup => makeup.id === selectedMakeup) : null

  const handleStatusChange = (makeupId: number, newStatus: string) => {
    // This would typically update the backend
    console.log(`Update makeup ${makeupId} to ${newStatus}`)
  }

  const canManageMakeups = user?.role === 'DEPARTMENT_HEAD' || user?.role === 'TEACHER' || user?.role === 'ADMIN'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sessions de Rattrapage</h1>
          <p className="text-muted-foreground">
            {user?.role === 'STUDENT' 
              ? 'Consultez vos sessions de rattrapage' 
              : 'Gérez et organisez les sessions de rattrapage'
            }
          </p>
        </div>
        {canManageMakeups && (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Nouvelle Session
          </Button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{makeupSessions.length}</div>
            <p className="text-xs text-muted-foreground">Ce mois-ci</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Attente</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {makeupSessions.filter(session => session.status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">À valider</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Programmées</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {makeupSessions.filter(session => session.status === 'scheduled').length}
            </div>
            <p className="text-xs text-muted-foreground">À venir</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Terminées</CardTitle>
            <Check className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">
              {makeupSessions.filter(session => session.status === 'completed').length}
            </div>
            <p className="text-xs text-muted-foreground">Réalisées</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Étudiants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(makeupSessions.flatMap(session => session.students)).size}
            </div>
            <p className="text-xs text-muted-foreground">Concernés</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Makeup Sessions List */}
        <Card>
          <CardHeader>
            <CardTitle>Sessions de Rattrapage</CardTitle>
            <CardDescription>
              {user?.role === 'STUDENT' ? 'Vos sessions programmées' : 'Toutes les sessions'}
            </CardDescription>
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher dans les sessions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredMakeups.map((makeup) => (
                <div
                  key={makeup.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                    selectedMakeup === makeup.id ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => setSelectedMakeup(makeup.id)}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-sm font-medium truncate">{makeup.subject}</h4>
                        {getStatusBadge(makeup.status)}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {makeup.teacher} • {makeup.group}
                      </p>
                      <div className="text-xs text-muted-foreground mt-1">
                        <p>Original: {new Date(makeup.originalDate).toLocaleDateString('fr-FR')} • {makeup.originalTime}</p>
                        <p className="font-medium">Rattrapage: {new Date(makeup.proposedDate).toLocaleDateString('fr-FR')} • {makeup.proposedTime}</p>
                      </div>
                      <p className="text-xs mt-1 truncate">
                        <span className="font-medium">Motif:</span> {makeup.reason}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <Badge variant="outline">{makeup.room}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {makeup.students.length} étudiant{makeup.students.length > 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Makeup Session Detail */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedMakeupData ? 'Détail de la Session' : 'Sélectionnez une Session'}
            </CardTitle>
            {selectedMakeupData && (
              <CardDescription>
                {selectedMakeupData.subject} • {selectedMakeupData.teacher}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedMakeupData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Matière</label>
                    <p className="font-medium">{selectedMakeupData.subject}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Enseignant</label>
                    <p className="font-medium">{selectedMakeupData.teacher}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Groupe</label>
                    <p className="font-medium">{selectedMakeupData.group}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Salle</label>
                    <p className="font-medium">{selectedMakeupData.room}</p>
                  </div>
                </div>

                <div className="border rounded-lg p-4 bg-red-50">
                  <h4 className="font-medium mb-2 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-2 text-red-600" />
                    Session Originale (Annulée)
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Date:</span>
                      <span className="ml-2">{new Date(selectedMakeupData.originalDate).toLocaleDateString('fr-FR')}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Horaire:</span>
                      <span className="ml-2">{selectedMakeupData.originalTime}</span>
                    </div>
                  </div>
                </div>

                <div className="border rounded-lg p-4 bg-green-50">
                  <h4 className="font-medium mb-2 flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-green-600" />
                    Session de Rattrapage
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Date:</span>
                      <span className="ml-2 font-medium">{new Date(selectedMakeupData.proposedDate).toLocaleDateString('fr-FR')}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Horaire:</span>
                      <span className="ml-2 font-medium">{selectedMakeupData.proposedTime}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Motif du Report</label>
                  <p className="text-sm mt-1 p-3 bg-gray-50 rounded-lg">
                    {selectedMakeupData.reason}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Étudiants Concernés ({selectedMakeupData.students.length})</label>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {selectedMakeupData.students.map((student, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {student}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-muted-foreground">Statut:</label>
                  {getStatusBadge(selectedMakeupData.status)}
                </div>

                {selectedMakeupData.status === 'rejected' && selectedMakeupData.rejectionReason && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Motif du Rejet</label>
                    <p className="text-sm mt-1 p-3 bg-red-50 rounded-lg text-red-700">
                      {selectedMakeupData.rejectionReason}
                    </p>
                  </div>
                )}

                {canManageMakeups && selectedMakeupData.status === 'pending' && (
                  <div className="border-t pt-4 space-y-3">
                    <h4 className="font-medium">Actions</h4>
                    <div className="flex space-x-2">
                      <Button 
                        variant="default" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedMakeupData.id, 'approved')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Check className="h-4 w-4 mr-1" />
                        Approuver
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedMakeupData.id, 'rejected')}
                      >
                        <X className="h-4 w-4 mr-1" />
                        Rejeter
                      </Button>
                    </div>
                  </div>
                )}

                <div className="text-xs text-muted-foreground border-t pt-3">
                  Créée par {selectedMakeupData.createdBy} le {new Date(selectedMakeupData.createdAt).toLocaleString('fr-FR')}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="mx-auto h-12 w-12 mb-4" />
                <p>Sélectionnez une session pour voir les détails</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions for Teachers */}
      {(user?.role === 'TEACHER' || user?.role === 'DEPARTMENT_HEAD') && (
        <Card>
          <CardHeader>
            <CardTitle>Proposer une Session de Rattrapage</CardTitle>
            <CardDescription>Créez une nouvelle session pour compenser un cours annulé</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Matière</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez une matière" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="math">Mathématiques Fondamentales</SelectItem>
                    <SelectItem value="physics">Physique Générale</SelectItem>
                    <SelectItem value="chemistry">Chimie Organique</SelectItem>
                    <SelectItem value="info">Informatique Théorique</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Groupe Concerné</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un groupe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="a">Groupe A</SelectItem>
                    <SelectItem value="b">Groupe B</SelectItem>
                    <SelectItem value="c">Groupe C</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Date du Rattrapage</label>
                <Input type="date" />
              </div>
              <div>
                <label className="text-sm font-medium">Horaire</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un créneau" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0800">08:00 - 10:00</SelectItem>
                    <SelectItem value="1030">10:30 - 12:30</SelectItem>
                    <SelectItem value="1400">14:00 - 16:00</SelectItem>
                    <SelectItem value="1630">16:30 - 18:30</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">Motif du Report</label>
              <Textarea
                placeholder="Expliquez pourquoi la session originale a été annulée..."
                rows={2}
              />
            </div>
            <Button className="w-full">
              <Calendar className="mr-2 h-4 w-4" />
              Proposer la Session
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}