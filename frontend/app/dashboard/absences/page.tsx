'use client'

import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { UserX, Calendar, Clock, FileText, Search, Plus, Check, X, Eye } from 'lucide-react'
import { useState } from 'react'

export default function AbsencesPage() {
  const { user, loading } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedAbsence, setSelectedAbsence] = useState<number | null>(null)

  if (loading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const absences = [
    {
      id: 1,
      student: 'Jean Dupont',
      subject: 'Mathématiques Fondamentales',
      teacher: 'Prof. Martin',
      date: '2024-09-28',
      time: '08:00-10:00',
      reason: 'Maladie',
      status: 'pending',
      justification: 'Certificat médical fourni - Grippe saisonnière',
      group: 'Groupe A',
      submittedAt: '2024-09-28 10:30'
    },
    {
      id: 2,
      student: 'Marie Laurent',
      subject: 'Physique Générale',
      teacher: 'Prof. Dubois',
      date: '2024-09-27',
      time: '14:00-16:00',
      reason: 'Rendez-vous médical',
      status: 'approved',
      justification: 'Rendez-vous spécialisé programmé à l\'avance',
      group: 'Groupe B',
      submittedAt: '2024-09-27 16:15'
    },
    {
      id: 3,
      student: 'Pierre Bernard',
      subject: 'Chimie Organique',
      teacher: 'Prof. Laurent',
      date: '2024-09-26',
      time: '10:30-12:30',
      reason: 'Problème de transport',
      status: 'rejected',
      justification: 'Retard important dû à une panne de transport en commun',
      group: 'Groupe C',
      submittedAt: '2024-09-26 13:00'
    },
    {
      id: 4,
      student: 'Sophie Martin',
      subject: 'Informatique Théorique',
      teacher: 'Prof. Rousseau',
      date: '2024-09-25',
      time: '09:30-11:30',
      reason: 'Urgence familiale',
      status: 'pending',
      justification: 'Hospitalisation d\'un proche nécessitant ma présence',
      group: 'Groupe A',
      submittedAt: '2024-09-25 11:45'
    },
    {
      id: 5,
      student: 'Antoine Petit',
      subject: 'Statistiques Appliquées',
      teacher: 'Prof. Moreau',
      date: '2024-09-24',
      time: '15:30-17:30',
      reason: 'Entretien d\'embauche',
      status: 'approved',
      justification: 'Entretien pour stage obligatoire du cursus',
      group: 'Groupe B',
      submittedAt: '2024-09-24 09:00'
    }
  ]

  const filteredAbsences = absences.filter(absence =>
    absence.student.toLowerCase().includes(searchTerm.toLowerCase()) ||
    absence.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    absence.teacher.toLowerCase().includes(searchTerm.toLowerCase()) ||
    absence.reason.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">En Attente</Badge>
      case 'approved':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Approuvée</Badge>
      case 'rejected':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Rejetée</Badge>
      default:
        return <Badge variant="secondary">Inconnu</Badge>
    }
  }

  const selectedAbsenceData = selectedAbsence ? absences.find(abs => abs.id === selectedAbsence) : null

  const handleStatusChange = (absenceId: number, newStatus: string) => {
    // This would typically update the backend
    console.log(`Update absence ${absenceId} to ${newStatus}`)
  }

  const canManageAbsences = user?.role === 'DEPARTMENT_HEAD' || user?.role === 'TEACHER' || user?.role === 'ADMIN'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion des Absences</h1>
          <p className="text-muted-foreground">
            {user?.role === 'STUDENT' 
              ? 'Gérez vos justifications d\'absence' 
              : 'Validez et gérez les absences des étudiants'
            }
          </p>
        </div>
        {user?.role === 'STUDENT' && (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Déclarer une Absence
          </Button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Absences</CardTitle>
            <UserX className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{absences.length}</div>
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
              {absences.filter(abs => abs.status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">À traiter</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approuvées</CardTitle>
            <Check className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {absences.filter(abs => abs.status === 'approved').length}
            </div>
            <p className="text-xs text-muted-foreground">Justifiées</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejetées</CardTitle>
            <X className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {absences.filter(abs => abs.status === 'rejected').length}
            </div>
            <p className="text-xs text-muted-foreground">Non justifiées</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Absences List */}
        <Card>
          <CardHeader>
            <CardTitle>Liste des Absences</CardTitle>
            <CardDescription>
              {user?.role === 'STUDENT' ? 'Vos absences déclarées' : 'Absences à traiter'}
            </CardDescription>
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher dans les absences..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredAbsences.map((absence) => (
                <div
                  key={absence.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                    selectedAbsence === absence.id ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => setSelectedAbsence(absence.id)}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-sm font-medium truncate">{absence.student}</h4>
                        {getStatusBadge(absence.status)}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {absence.subject} • {absence.teacher}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(absence.date).toLocaleDateString('fr-FR')} • {absence.time}
                      </p>
                      <p className="text-xs font-medium mt-1 truncate">
                        Motif: {absence.reason}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <Badge variant="outline">{absence.group}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(absence.submittedAt).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Absence Detail */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedAbsenceData ? 'Détail de l\'Absence' : 'Sélectionnez une Absence'}
            </CardTitle>
            {selectedAbsenceData && (
              <CardDescription>
                {selectedAbsenceData.student} • {new Date(selectedAbsenceData.date).toLocaleDateString('fr-FR')}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedAbsenceData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Étudiant</label>
                    <p className="font-medium">{selectedAbsenceData.student}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Groupe</label>
                    <p className="font-medium">{selectedAbsenceData.group}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Matière</label>
                    <p className="font-medium">{selectedAbsenceData.subject}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Enseignant</label>
                    <p className="font-medium">{selectedAbsenceData.teacher}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Date</label>
                    <p className="font-medium">{new Date(selectedAbsenceData.date).toLocaleDateString('fr-FR')}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Horaire</label>
                    <p className="font-medium">{selectedAbsenceData.time}</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Motif</label>
                  <p className="font-medium">{selectedAbsenceData.reason}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Justification</label>
                  <p className="text-sm mt-1 p-3 bg-gray-50 rounded-lg">
                    {selectedAbsenceData.justification}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-muted-foreground">Statut actuel:</label>
                  {getStatusBadge(selectedAbsenceData.status)}
                </div>

                {canManageAbsences && selectedAbsenceData.status === 'pending' && (
                  <div className="border-t pt-4 space-y-3">
                    <h4 className="font-medium">Actions</h4>
                    <div className="flex space-x-2">
                      <Button 
                        variant="default" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedAbsenceData.id, 'approved')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <Check className="h-4 w-4 mr-1" />
                        Approuver
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedAbsenceData.id, 'rejected')}
                      >
                        <X className="h-4 w-4 mr-1" />
                        Rejeter
                      </Button>
                    </div>
                  </div>
                )}

                <div className="text-xs text-muted-foreground border-t pt-3">
                  Soumise le {new Date(selectedAbsenceData.submittedAt).toLocaleString('fr-FR')}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <UserX className="mx-auto h-12 w-12 mb-4" />
                <p>Sélectionnez une absence pour voir les détails</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions for Students */}
      {user?.role === 'STUDENT' && (
        <Card>
          <CardHeader>
            <CardTitle>Déclarer une Nouvelle Absence</CardTitle>
            <CardDescription>Remplissez ce formulaire pour justifier une absence</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Date de l'absence</label>
                <Input type="date" />
              </div>
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
            </div>
            <div>
              <label className="text-sm font-medium">Motif de l'absence</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionnez un motif" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="illness">Maladie</SelectItem>
                  <SelectItem value="medical">Rendez-vous médical</SelectItem>
                  <SelectItem value="family">Urgence familiale</SelectItem>
                  <SelectItem value="transport">Problème de transport</SelectItem>
                  <SelectItem value="other">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Justification détaillée</label>
              <Textarea
                placeholder="Expliquez les circonstances de votre absence..."
                rows={3}
              />
            </div>
            <Button className="w-full">
              <FileText className="mr-2 h-4 w-4" />
              Soumettre la Justification
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}