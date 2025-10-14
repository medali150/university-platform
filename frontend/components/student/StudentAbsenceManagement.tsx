'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { UserX, Calendar, Clock, FileText, Search, Upload, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { AbsenceAPI, AbsenceUtils } from '@/lib/absence-api'

interface Absence {
  id: string
  studentId: string
  studentName: string
  scheduleId: string
  className: string
  teacherName: string
  date: string
  startTime: string
  endTime: string
  reason: string
  status: string
  justificationText?: string
  supportingDocuments?: string[]
  reviewNotes?: string
  createdAt: string
}

interface AbsenceStatistics {
  total: number
  justified: number
  unjustified: number
  pending: number
  absenceRate: number
}

export default function StudentAbsenceManagement() {
  const { user, loading } = useAuth()
  const [absences, setAbsences] = useState<Absence[]>([])
  const [statistics, setStatistics] = useState<AbsenceStatistics | null>(null)
  const [selectedAbsence, setSelectedAbsence] = useState<Absence | null>(null)
  const [isJustifyModalOpen, setIsJustifyModalOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [loadingData, setLoadingData] = useState(true)

  // Justification form state
  const [justificationForm, setJustificationForm] = useState({
    justificationText: '',
    supportingDocuments: [] as string[]
  })

  useEffect(() => {
    if (user?.role === 'STUDENT') {
      fetchStudentAbsences()
    }
  }, [user])

  const fetchStudentAbsences = async () => {
    try {
      setLoadingData(true)
      
      const { absences: studentAbsences, statistics: stats } = await AbsenceAPI.getStudentAbsences()
      setAbsences(studentAbsences || [])
      setStatistics(stats || null)
    } catch (error) {
      console.error('Error fetching student absences:', error)
      alert('Erreur lors du chargement de vos absences')
    } finally {
      setLoadingData(false)
    }
  }

  const handleJustifyAbsence = async () => {
    if (!selectedAbsence) return

    try {
      if (!justificationForm.justificationText.trim()) {
        alert('Veuillez saisir une justification')
        return
      }

      await AbsenceAPI.justifyAbsence(selectedAbsence.id, justificationForm.justificationText)

      alert('Justification soumise avec succès')
      setIsJustifyModalOpen(false)
      setJustificationForm({
        justificationText: '',
        supportingDocuments: []
      })
      setSelectedAbsence(null)
      fetchStudentAbsences()
    } catch (error) {
      console.error('Error submitting justification:', error)
      alert('Erreur lors de la soumission de la justification')
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      // In a real implementation, you would upload these files to a server
      // and get back URLs. For now, we'll just store the file names
      const fileNames = Array.from(files).map(file => file.name)
      setJustificationForm(prev => ({
        ...prev,
        supportingDocuments: [...prev.supportingDocuments, ...fileNames]
      }))
      alert(`${files.length} fichier(s) ajouté(s)`)
    }
  }

  const removeDocument = (index: number) => {
    setJustificationForm(prev => ({
      ...prev,
      supportingDocuments: prev.supportingDocuments.filter((_, i) => i !== index)
    }))
  }

  // Filter absences
  const filteredAbsences = absences.filter(absence => {
    const matchesSearch = absence.className.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         absence.teacherName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         absence.reason.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || absence.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'rejected':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'pending_review':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />
      default:
        return <UserX className="h-4 w-4 text-gray-600" />
    }
  }

  if (loading || loadingData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (user?.role !== 'STUDENT') {
    return (
      <div className="text-center py-8">
        <p>Accès non autorisé</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mes Absences</h1>
          <p className="text-muted-foreground">
            Consultez et justifiez vos absences
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Absences</CardTitle>
              <UserX className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total}</div>
              <p className="text-xs text-muted-foreground">Ce semestre</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">En Attente</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {statistics.pending}
              </div>
              <p className="text-xs text-muted-foreground">À justifier</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Justifiées</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {statistics.justified}
              </div>
              <p className="text-xs text-muted-foreground">Acceptées</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Taux d'Absence</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.absenceRate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">Du total des cours</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Absences List */}
        <Card>
          <CardHeader>
            <CardTitle>Liste de vos Absences</CardTitle>
            <CardDescription>Toutes vos absences déclarées</CardDescription>
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher dans vos absences..."
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
                    selectedAbsence?.id === absence.id ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => setSelectedAbsence(absence)}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-sm font-medium truncate">{absence.className}</h4>
                        <Badge className={AbsenceUtils.getStatusColor(absence.status as any)}>
                          {AbsenceUtils.getStatusLabel(absence.status as any)}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        Prof. {absence.teacherName}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {AbsenceUtils.formatDate(absence.date)} • {AbsenceUtils.formatTime(absence.startTime)} - {AbsenceUtils.formatTime(absence.endTime)}
                      </p>
                      <p className="text-xs font-medium mt-1 truncate">
                        Motif: {absence.reason}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {getStatusIcon(absence.status)}
                      {AbsenceUtils.canJustifyAbsence(absence as any) && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedAbsence(absence)
                            setIsJustifyModalOpen(true)
                          }}
                        >
                          Justifier
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {filteredAbsences.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <UserX className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>Aucune absence trouvée</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Absence Detail */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedAbsence ? 'Détail de l\'Absence' : 'Sélectionnez une Absence'}
            </CardTitle>
            {selectedAbsence && (
              <CardDescription>
                {selectedAbsence.className} • {AbsenceUtils.formatDate(selectedAbsence.date)}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedAbsence ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Matière</label>
                    <p className="font-medium">{selectedAbsence.className}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Enseignant</label>
                    <p className="font-medium">Prof. {selectedAbsence.teacherName}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Date</label>
                    <p className="font-medium">{AbsenceUtils.formatDate(selectedAbsence.date)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Horaire</label>
                    <p className="font-medium">
                      {AbsenceUtils.formatTime(selectedAbsence.startTime)} - {AbsenceUtils.formatTime(selectedAbsence.endTime)}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Motif déclaré</label>
                  <p className="font-medium">{selectedAbsence.reason}</p>
                </div>

                {selectedAbsence.justificationText && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Votre justification</label>
                    <p className="text-sm mt-1 p-3 bg-blue-50 rounded-lg">
                      {selectedAbsence.justificationText}
                    </p>
                  </div>
                )}

                {selectedAbsence.supportingDocuments && selectedAbsence.supportingDocuments.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Documents joints</label>
                    <ul className="text-sm mt-1 space-y-1">
                      {selectedAbsence.supportingDocuments.map((doc, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <FileText className="h-4 w-4" />
                          <span>{doc}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedAbsence.reviewNotes && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Avis du chef de département</label>
                    <p className="text-sm mt-1 p-3 bg-gray-50 rounded-lg">
                      {selectedAbsence.reviewNotes}
                    </p>
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-muted-foreground">Statut:</label>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(selectedAbsence.status)}
                    <Badge className={AbsenceUtils.getStatusColor(selectedAbsence.status as any)}>
                      {AbsenceUtils.getStatusLabel(selectedAbsence.status as any)}
                    </Badge>
                  </div>
                </div>

                {AbsenceUtils.canJustifyAbsence(selectedAbsence as any) && (
                  <div className="border-t pt-4">
                    <Button 
                      onClick={() => setIsJustifyModalOpen(true)}
                      className="w-full"
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Justifier cette Absence
                    </Button>
                  </div>
                )}

                <div className="text-xs text-muted-foreground border-t pt-3">
                  Créée le {AbsenceUtils.formatDate(selectedAbsence.createdAt)}
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

      {/* Justification Modal */}
      <Dialog open={isJustifyModalOpen} onOpenChange={setIsJustifyModalOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Justifier l'Absence</DialogTitle>
            <DialogDescription>
              {selectedAbsence && (
                <>
                  {selectedAbsence.className} • {AbsenceUtils.formatDate(selectedAbsence.date)}
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Justification détaillée</label>
              <Textarea
                placeholder="Expliquez les circonstances de votre absence..."
                value={justificationForm.justificationText}
                onChange={(e) => setJustificationForm(prev => ({ 
                  ...prev, 
                  justificationText: e.target.value 
                }))}
                rows={4}
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Documents justificatifs (optionnel)</label>
              <div className="mt-1 space-y-2">
                <div className="flex items-center space-x-2">
                  <Input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Ajouter des fichiers
                  </Button>
                </div>
                
                {justificationForm.supportingDocuments.length > 0 && (
                  <div className="space-y-1">
                    {justificationForm.supportingDocuments.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center space-x-2">
                          <FileText className="h-4 w-4" />
                          <span className="text-sm">{doc}</span>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeDocument(index)}
                        >
                          ×
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsJustifyModalOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleJustifyAbsence}>
                Soumettre la Justification
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}