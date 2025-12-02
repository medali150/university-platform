'use client'

import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { UserX, Calendar, Clock, FileText, Search, Plus, Check, X, Eye } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Absence {
  id: string
  student: {
    nom: string
    prenom: string
    email: string
  }
  subject: {
    nom: string
  }
  teacher: {
    nom: string
    prenom: string
  }
  emploitemps: {
    date: string
    heure_debut: string
    heure_fin: string
    groupe: {
      nom: string
    }
  }
  motif: string
  statut: 'unjustified' | 'pending_review' | 'justified' | 'approved' | 'rejected'
  justification_text?: string
  createdAt: string
  updatedAt: string
}

export default function AbsencesPage() {
  const { user, loading } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedAbsence, setSelectedAbsence] = useState<string | null>(null)
  const [absences, setAbsences] = useState<Absence[]>([])
  const [loadingAbsences, setLoadingAbsences] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch absences from API
  useEffect(() => {
    const fetchAbsences = async () => {
      const token = localStorage.getItem('authToken')
      console.log('Token found:', !!token)
      if (!token) {
        console.log('No token found, skipping fetch')
        setError('Token d\'authentification non trouvé')
        setLoadingAbsences(false)
        return
      }

      try {
        setLoadingAbsences(true)
        setError(null)
        
        // Try the main absence management API first (role-based)
        let response = await fetch('http://localhost:8000/absences/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const result = await response.json()
          console.log('Fetched absences from main API:', result)
          
          // Transform the data to match the expected format
          const transformedAbsences = result.data.map((absence: any) => ({
            id: absence.id,
            student: {
              nom: absence.studentName.split(' ').slice(-1)[0] || 'Unknown',
              prenom: absence.studentName.split(' ').slice(0, -1).join(' ') || 'Unknown',
              email: 'student@example.com' // Not available in this format
            },
            subject: {
              nom: absence.className
            },
            teacher: {
              nom: absence.teacherName.split(' ').slice(-1)[0] || 'Unknown',
              prenom: absence.teacherName.split(' ').slice(0, -1).join(' ') || 'Unknown'
            },
            emploitemps: {
              date: absence.date,
              heure_debut: absence.startTime,
              heure_fin: absence.endTime,
              groupe: { nom: 'N/A' }
            },
            motif: absence.reason || 'Non spécifié',
            statut: absence.status,
            justification_text: absence.justificationText,
            createdAt: absence.createdAt,
            updatedAt: absence.updatedAt
          }))
          
          setAbsences(transformedAbsences)
        } else {
          console.warn('Main API failed, trying debug-absences fallback:', response.status)
          
          // Fallback to debug-absences API
          response = await fetch('http://localhost:8000/debug-absences/all', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            console.log('Fetched absences from debug API:', data)
            setAbsences(data)
          } else {
            console.warn('Debug API also failed, trying simple-absences:', response.status)
            
            // Final fallback to simple-absences API
            response = await fetch('http://localhost:8000/simple-absences/all', {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            })
            
            if (response.ok) {
              const data = await response.json()
              console.log('Fetched absences from simple-absences API:', data)
              setAbsences(data)
            } else {
              throw new Error(`All APIs failed: ${response.status}`)
            }
          }
        }
      } catch (err) {
        console.error('Error fetching absences:', err)
        setError('Erreur lors du chargement des absences. Utilisation des données de démonstration.')
        
        // Fallback to demo data with more realistic examples
        setAbsences([
          {
            id: '1',
            student: { nom: 'Ben Ali', prenom: 'Ahmed', email: 'ahmed.benali@student.edu' },
            subject: { nom: 'Base de Données' },
            teacher: { nom: 'ISET', prenom: 'Wahid' },
            emploitemps: {
              date: '2025-10-04',
              heure_debut: '08:00:00',
              heure_fin: '10:00:00',
              groupe: { nom: 'L3-INFO-G1' }
            },
            motif: 'retard',
            statut: 'unjustified',
            justification_text: undefined,
            createdAt: '2025-10-04T10:30:00',
            updatedAt: '2025-10-04T10:30:00'
          },
          {
            id: '2',
            student: { nom: 'Zouari', prenom: 'Hedi', email: 'hedi.zouari@student.edu' },
            subject: { nom: 'Programmation Web' },
            teacher: { nom: 'ISET', prenom: 'Wahid' },
            emploitemps: {
              date: '2025-10-03',
              heure_debut: '10:00:00',
              heure_fin: '12:00:00',
              groupe: { nom: 'L3-INFO-G2' }
            },
            motif: 'sickness',
            statut: 'approved',
            justification_text: 'Rendez-vous spécialisé programmé à l\'avance',
            createdAt: '2025-10-03T16:15:00',
            updatedAt: '2025-10-03T16:15:00'
          },
          {
            id: '3',
            student: { nom: 'Ben Ali', prenom: 'Ahmed', email: 'ahmed.benali2@student.edu' },
            subject: { nom: 'Base de Données' },
            teacher: { nom: 'ISET', prenom: 'Wahid' },
            emploitemps: {
              date: '2025-10-03',
              heure_debut: '08:00:00',
              heure_fin: '10:00:00',
              groupe: { nom: 'L3-INFO-G1' }
            },
            motif: 'retard',
            statut: 'pending_review',
            justification_text: 'Problème de transport en commun',
            createdAt: '2025-10-03T10:30:00',
            updatedAt: '2025-10-03T10:30:00'
          }
        ])
      } finally {
        setLoadingAbsences(false)
      }
    }

    if (user) {
      fetchAbsences()
    }
  }, [user])

  if (loading || loadingAbsences) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const filteredAbsences = absences.filter(absence =>
    `${absence.student.prenom} ${absence.student.nom}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    absence.subject.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    `${absence.teacher.prenom} ${absence.teacher.nom}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    absence.motif.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending_review':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">En Attente</Badge>
      case 'approved':
      case 'justified':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Approuvée</Badge>
      case 'rejected':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Rejetée</Badge>
      case 'unjustified':
        return <Badge variant="secondary" className="bg-gray-100 text-gray-800">Non Justifiée</Badge>
      default:
        return <Badge variant="secondary">Inconnu</Badge>
    }
  }

  const selectedAbsenceData = selectedAbsence ? absences.find(abs => abs.id === selectedAbsence) : null

  const handleStatusChange = async (absenceId: string, newStatus: string, reviewNotes?: string) => {
    const token = localStorage.getItem('authToken')
    if (!token) {
      alert('Token d\'authentification manquant')
      return
    }

    try {
      setLoadingAbsences(true)
      
      // Try the main absence management API first (for department heads)
      let response = await fetch(`http://localhost:8000/absences/${absenceId}/review`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reviewStatus: newStatus,
          reviewNotes: reviewNotes || `Statut changé vers ${newStatus} par le chef de département`
        })
      })

      if (!response.ok) {
        console.warn('Main API failed, trying debug-absences fallback')
        // Fallback to debug-absences API
        response = await fetch(`http://localhost:8000/debug-absences/${absenceId}/status`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: newStatus
          })
        })
        
        if (!response.ok) {
          console.warn('Debug API also failed, trying simple-absences')
          // Final fallback to simple-absences API
          response = await fetch(`http://localhost:8000/simple-absences/${absenceId}/status`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              status: newStatus
            })
          })
        }
      }

      if (response.ok) {
        const result = await response.json()
        
        // Update the local state
        setAbsences(prev => prev.map(absence => 
          absence.id === absenceId 
            ? { ...absence, statut: newStatus as any, updatedAt: new Date().toISOString() }
            : absence
        ))
        
        setSelectedAbsence(null)
        
        // Show success message based on action
        const successMessage = newStatus === 'approved' || newStatus === 'justified' 
          ? '✅ Absence approuvée avec succès'
          : newStatus === 'rejected' || newStatus === 'unjustified'
          ? '❌ Absence rejetée'
          : `📝 Statut mis à jour vers ${newStatus}`
        
        alert(successMessage)
        console.log(`Statut de l'absence ${absenceId} mis à jour vers ${newStatus}`, result)
      } else {
        const errorText = await response.text()
        console.error('Failed to update absence status:', response.status, errorText)
        alert(`Erreur lors de la mise à jour du statut: ${response.status}\n${errorText}`)
      }
    } catch (error) {
      console.error('Error updating absence status:', error)
      alert(`Erreur lors de la mise à jour du statut: ${error instanceof Error ? error.message : 'Erreur inconnue'}`)
    } finally {
      setLoadingAbsences(false)
    }
  }

  const canManageAbsences = user?.role === 'DEPARTMENT_HEAD' || user?.role === 'TEACHER' || user?.role === 'ADMIN'

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Modern Gradient Header - Matching Dashboard Theme */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 sm:p-8 md:p-10 text-white shadow-lg">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <UserX className="h-8 w-8" />
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight">
                  Gestion des Absences 📋
                </h1>
              </div>
              <p className="text-blue-100 text-base sm:text-lg">
                {user?.role === 'STUDENT' 
                  ? 'Gérez vos justifications d\'absence' 
                  : user?.role === 'DEPARTMENT_HEAD'
                  ? 'Interface Chef de Département - Validez et gérez les absences'
                  : user?.role === 'TEACHER'
                  ? 'Interface Enseignant - Gérez les absences de vos cours'
                  : 'Validez et gérez les absences des étudiants'
                }
              </p>
              {error && (
                <div className="mt-3 text-sm text-white bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/30">
                  ⚠️ {error}
                </div>
              )}
            </div>
            <div className="flex gap-2">
              {user?.role === 'STUDENT' && (
                <Button className="bg-white text-blue-600 hover:bg-blue-50 shadow-lg">
                  <Plus className="mr-2 h-4 w-4" />
                  Déclarer une Absence
                </Button>
              )}
              {user?.role === 'DEPARTMENT_HEAD' && (
                <div className="text-right bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/30">
                  <div className="text-sm font-bold text-white">Chef de Département</div>
                  <div className="text-xs text-blue-100">Pouvoir d'approbation</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards - Modern Design */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          {
            title: 'Total Absences',
            value: absences.length,
            icon: UserX,
            color: 'from-blue-500 to-blue-600',
            bgColor: 'bg-blue-100',
            textColor: 'text-blue-600',
            trend: 'Ce mois-ci'
          },
          {
            title: 'En Attente',
            value: absences.filter(abs => abs.statut === 'pending_review').length,
            icon: Clock,
            color: 'from-orange-500 to-orange-600',
            bgColor: 'bg-orange-100',
            textColor: 'text-orange-600',
            trend: 'À traiter'
          },
          {
            title: 'Approuvées',
            value: absences.filter(abs => abs.statut === 'approved' || abs.statut === 'justified').length,
            icon: Check,
            color: 'from-green-500 to-green-600',
            bgColor: 'bg-green-100',
            textColor: 'text-green-600',
            trend: 'Justifiées'
          },
          {
            title: 'Rejetées',
            value: absences.filter(abs => abs.statut === 'rejected').length,
            icon: X,
            color: 'from-red-500 to-red-600',
            bgColor: 'bg-red-100',
            textColor: 'text-red-600',
            trend: 'Non justifiées'
          }
        ].map((stat, idx) => {
          const Icon = stat.icon
          return (
            <div 
              key={idx}
              className="group relative overflow-hidden rounded-lg bg-white p-6 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity`}></div>
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.color} text-white shadow-md`}>
                    <Icon className="h-6 w-6" />
                  </div>
                </div>
                <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-xs text-gray-500 mt-1">{stat.trend}</p>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Absences List */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-cyan-50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/20 text-blue-600">
                <UserX className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Liste des Absences</CardTitle>
                <CardDescription>
                  {user?.role === 'STUDENT' ? 'Vos absences déclarées' : 'Absences à traiter'}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2 mt-4">
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
                        <h4 className="text-sm font-medium truncate">{absence.student.prenom} {absence.student.nom}</h4>
                        {getStatusBadge(absence.statut)}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {absence.subject.nom} • {absence.teacher.prenom} {absence.teacher.nom}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(absence.emploitemps.date).toLocaleDateString('fr-FR')} • {absence.emploitemps.heure_debut}-{absence.emploitemps.heure_fin}
                      </p>
                      <p className="text-xs font-medium mt-1 truncate">
                        Motif: {absence.motif}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <Badge variant="outline">{absence.emploitemps.groupe.nom}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(absence.createdAt).toLocaleDateString('fr-FR')}
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
                {selectedAbsenceData.student.prenom} {selectedAbsenceData.student.nom} • {new Date(selectedAbsenceData.emploitemps.date).toLocaleDateString('fr-FR')}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedAbsenceData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Étudiant</label>
                    <p className="font-medium">{selectedAbsenceData.student.prenom} {selectedAbsenceData.student.nom}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Groupe</label>
                    <p className="font-medium">{selectedAbsenceData.emploitemps.groupe.nom}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Matière</label>
                    <p className="font-medium">{selectedAbsenceData.subject.nom}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Enseignant</label>
                    <p className="font-medium">{selectedAbsenceData.teacher.prenom} {selectedAbsenceData.teacher.nom}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Date</label>
                                        <p className="font-medium">{new Date(selectedAbsenceData.emploitemps.date).toLocaleDateString('fr-FR')}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Horaire</label>
                    <p className="font-medium">{selectedAbsenceData.emploitemps.heure_debut} - {selectedAbsenceData.emploitemps.heure_fin}</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Motif</label>
                  <p className="font-medium">{selectedAbsenceData.motif}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Justification</label>
                  <p className="text-sm mt-1 p-3 bg-gray-50 rounded-lg">
                    {selectedAbsenceData.justification_text || 'Aucune justification fournie'}
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-muted-foreground">Statut actuel:</label>
                  {getStatusBadge(selectedAbsenceData.statut)}
                </div>

                {canManageAbsences && (selectedAbsenceData.statut === 'pending_review' || selectedAbsenceData.statut === 'unjustified') && (
                  <div className="border-t pt-4 space-y-3">
                    <h4 className="font-medium flex items-center gap-2">
                      🎯 Actions Chef de Département
                    </h4>
                    <div className="grid grid-cols-2 gap-2">
                      <Button 
                        variant="default" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedAbsenceData.id, 'approved', 'Absence justifiée et approuvée par le chef de département')}
                        className="bg-green-600 hover:bg-green-700 text-white"
                        disabled={loadingAbsences}
                      >
                        <Check className="h-4 w-4 mr-1" />
                        {loadingAbsences ? 'En cours...' : 'Approuver'}
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => handleStatusChange(selectedAbsenceData.id, 'rejected', 'Justification insuffisante ou absence non justifiée')}
                        disabled={loadingAbsences}
                      >
                        <X className="h-4 w-4 mr-1" />
                        {loadingAbsences ? 'En cours...' : 'Rejeter'}
                      </Button>
                    </div>
                    
                    {/* Additional quick actions for department heads */}
                    <div className="mt-3 pt-2 border-t border-gray-100">
                      <p className="text-xs text-gray-500 mb-2">Actions rapides:</p>
                      <div className="flex flex-wrap gap-1">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleStatusChange(selectedAbsenceData.id, 'justified', 'Absence justifiée après examen')}
                          className="text-xs h-7"
                          disabled={loadingAbsences}
                        >
                          ✅ Justifier
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleStatusChange(selectedAbsenceData.id, 'unjustified', 'Absence marquée comme non justifiée')}
                          className="text-xs h-7"
                          disabled={loadingAbsences}
                        >
                          ❌ Non justifiée
                        </Button>
                      </div>
                    </div>
                    
                    <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                      💡 En tant que chef de département, vous pouvez approuver ou rejeter les justifications d'absence des étudiants de votre département.
                    </div>
                  </div>
                )}

                <div className="text-xs text-muted-foreground border-t pt-3">
                  Soumise le {new Date(selectedAbsenceData.createdAt).toLocaleString('fr-FR')}
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