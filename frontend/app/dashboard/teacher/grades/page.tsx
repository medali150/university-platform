'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { BookOpen, Users, Save, Edit, Trash2, Plus, AlertCircle, CheckCircle, FileText } from 'lucide-react'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { api } from '@/lib/api'

// Types
interface Subject {
  id: string
  nom: string
  coefficient: number
  specialite: string
  departement: string
}

interface Group {
  id: string
  nom: string
  student_count: number
}

interface Grade {
  id: string
  valeur: number
  coefficient: number
  type: string
  date_examen: string | null
  observation: string | null
  createdAt: string
}

interface Student {
  id: string
  nom: string
  prenom: string
  email: string
  grades: Grade[]
}

type GradeType = 'EXAM' | 'CONTINUOUS' | 'PRACTICAL' | 'PROJECT' | 'ORAL'
type SemesterType = 'SEMESTER_1' | 'SEMESTER_2'

const gradeTypeLabels: Record<GradeType, string> = {
  EXAM: 'Examen',
  CONTINUOUS: 'Contrôle Continu',
  PRACTICAL: 'TP',
  PROJECT: 'Projet',
  ORAL: 'Oral'
}

export default function TeacherGradesPage() {
  const { user, isLoading: authLoading } = useRequireRole('TEACHER' as Role)
  
  // State
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [selectedSubject, setSelectedSubject] = useState<string>('')
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<string>('')
  const [students, setStudents] = useState<Student[]>([])
  const [semester, setSemester] = useState<SemesterType>('SEMESTER_1')
  const [academicYear, setAcademicYear] = useState('2024-2025')
  const [loading, setLoading] = useState(false)
  
  // Grade entry state
  const [showGradeDialog, setShowGradeDialog] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [gradeForm, setGradeForm] = useState({
    valeur: '',
    type: 'EXAM' as GradeType,
    date_examen: '',
    observation: ''
  })
  
  // Edit state
  const [editingGrade, setEditingGrade] = useState<Grade | null>(null)

  // Load subjects on mount
  useEffect(() => {
    if (user && !authLoading) {
      fetchSubjects()
    }
  }, [user, authLoading])

  // Load groups when subject is selected
  useEffect(() => {
    if (selectedSubject) {
      fetchGroups()
      setSelectedGroup('')
      setStudents([])
    }
  }, [selectedSubject])

  // Load students when group is selected
  useEffect(() => {
    if (selectedGroup && selectedSubject) {
      fetchStudents()
    }
  }, [selectedGroup, semester, academicYear])

  const fetchSubjects = async () => {
    try {
      setLoading(true)
      console.log('🔍 Fetching teacher subjects...')
      const data = await api.getTeacherSubjects()
      console.log('✅ Subjects loaded:', data)
      if (data.subjects && data.subjects.length > 0) {
        setSubjects(data.subjects)
        toast.success(`${data.subjects.length} matière(s) chargée(s)`)
      } else {
        setSubjects([])
        toast.error('Aucune matière assignée à cet enseignant', {
          description: 'Veuillez contacter l\'administrateur pour vous assigner des matières.'
        })
      }
    } catch (error: any) {
      console.error('❌ Error loading subjects:', error)
      toast.error('Erreur lors du chargement des matières', {
        description: error.message || 'Impossible de charger les matières'
      })
      setSubjects([])
    } finally {
      setLoading(false)
    }
  }

  const fetchGroups = async () => {
    if (!selectedSubject) return
    
    try {
      setLoading(true)
      console.log('🔍 Fetching groups for subject:', selectedSubject)
      const data = await api.getSubjectGroups(selectedSubject)
      console.log('✅ Groups loaded:', data)
      if (data.groups && data.groups.length > 0) {
        setGroups(data.groups)
        toast.success(`${data.groups.length} groupe(s) trouvé(s)`)
      } else {
        setGroups([])
        toast.error('Aucun groupe trouvé pour cette matière', {
          description: 'Cette matière n\'a pas encore de groupes assignés.'
        })
      }
    } catch (error: any) {
      console.error('❌ Error loading groups:', error)
      toast.error('Erreur lors du chargement des groupes', {
        description: error.message
      })
      setGroups([])
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async () => {
    if (!selectedSubject || !selectedGroup) return
    
    try {
      setLoading(true)
      console.log('🔍 Fetching students for group:', selectedGroup)
      const data = await api.getGroupStudentsForGrading(
        selectedSubject,
        selectedGroup,
        {
          semestre: semester,
          annee_scolaire: academicYear
        }
      )
      console.log('✅ Students loaded:', data)
      setStudents(data.students || [])
      if (data.students && data.students.length > 0) {
        toast.success(`${data.students.length} étudiant(s) chargé(s)`)
      } else {
        toast.info('Aucun étudiant dans ce groupe')
      }
    } catch (error: any) {
      console.error('❌ Error loading students:', error)
      toast.error('Erreur lors du chargement des étudiants', {
        description: error.message
      })
      setStudents([])
    } finally {
      setLoading(false)
    }
  }

  const openGradeDialog = (student: Student, grade?: Grade) => {
    setSelectedStudent(student)
    if (grade) {
      setEditingGrade(grade)
      setGradeForm({
        valeur: grade.valeur.toString(),
        type: grade.type as GradeType,
        date_examen: grade.date_examen || '',
        observation: grade.observation || ''
      })
    } else {
      setEditingGrade(null)
      setGradeForm({
        valeur: '',
        type: 'EXAM',
        date_examen: '',
        observation: ''
      })
    }
    setShowGradeDialog(true)
  }

  const closeGradeDialog = () => {
    setShowGradeDialog(false)
    setSelectedStudent(null)
    setEditingGrade(null)
    setGradeForm({
      valeur: '',
      type: 'EXAM',
      date_examen: '',
      observation: ''
    })
  }

  const handleSubmitGrade = async () => {
    if (!selectedStudent || !gradeForm.valeur) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }

    const valeur = parseFloat(gradeForm.valeur)
    if (isNaN(valeur) || valeur < 0 || valeur > 20) {
      toast.error('La note doit être entre 0 et 20')
      return
    }

    try {
      setLoading(true)
      
      if (editingGrade) {
        // Update existing grade
        await api.updateGrade(editingGrade.id, {
          valeur,
          type: gradeForm.type,
          date_examen: gradeForm.date_examen || null,
          observation: gradeForm.observation || null
        })
        toast.success('Note modifiée avec succès')
      } else {
        // Create new grade (coefficient is automatically taken from subject)
        await api.submitSingleGrade({
          id_etudiant: selectedStudent.id,
          id_matiere: selectedSubject,
          valeur,
          type: gradeForm.type,
          semestre: semester,
          annee_scolaire: academicYear,
          date_examen: gradeForm.date_examen || null,
          observation: gradeForm.observation || null
        })
        toast.success('Note ajoutée avec succès')
      }
      
      closeGradeDialog()
      fetchStudents() // Reload students with updated grades
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'enregistrement de la note')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteGrade = async (gradeId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
      return
    }

    try {
      setLoading(true)
      await api.deleteGrade(gradeId)
      toast.success('Note supprimée avec succès')
      fetchStudents() // Reload students
    } catch (error: any) {
      toast.error('Erreur lors de la suppression')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const calculateStudentAverage = (grades: Grade[]): number | null => {
    if (grades.length === 0) return null
    
    const totalWeighted = grades.reduce((sum, g) => sum + (g.valeur * g.coefficient), 0)
    const totalCoef = grades.reduce((sum, g) => sum + g.coefficient, 0)
    
    return totalCoef > 0 ? totalWeighted / totalCoef : null
  }

  const getGradeStats = () => {
    const allGrades = students.flatMap(s => s.grades)
    const totalGrades = allGrades.length
    const studentsWithGrades = students.filter(s => s.grades.length > 0).length
    const averageGrade = allGrades.length > 0 
      ? allGrades.reduce((sum, g) => sum + g.valeur, 0) / allGrades.length 
      : 0
    
    return { totalGrades, studentsWithGrades, averageGrade }
  }

  const getSubjectName = () => {
    const subject = subjects.find(s => s.id === selectedSubject)
    return subject?.nom || ''
  }

  const getGroupName = () => {
    const group = groups.find(g => g.id === selectedGroup)
    return group?.nom || ''
  }

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Gestion des Notes</h1>
        <p className="text-muted-foreground">
          Entrez et gérez les notes de vos étudiants
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Sélection</CardTitle>
          <CardDescription>
            Choisissez la matière, le groupe et le semestre
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading && (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-2"></div>
              <span className="text-muted-foreground">Chargement...</span>
            </div>
          )}
          
          {!loading && subjects.length === 0 && (
            <div className="text-center py-8 px-4 bg-muted/50 rounded-lg">
              <AlertCircle className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
              <h3 className="font-semibold mb-2">Aucune matière assignée</h3>
              <p className="text-sm text-muted-foreground">
                Vous n'avez pas encore de matières assignées. Contactez l'administrateur pour vous assigner des matières.
              </p>
            </div>
          )}
          
          {subjects.length > 0 && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {/* Subject Selection */}
              <div className="space-y-2">
                <Label>Matière</Label>
                <Select value={selectedSubject} onValueChange={setSelectedSubject} disabled={loading}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choisir une matière" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects.map(subject => (
                      <SelectItem key={subject.id} value={subject.id}>
                        {subject.nom}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  {subjects.length} matière(s) disponible(s)
                </p>
              </div>

              {/* Group Selection */}
              <div className="space-y-2">
                <Label>Groupe</Label>
                <Select 
                  value={selectedGroup} 
                  onValueChange={setSelectedGroup}
                  disabled={!selectedSubject || groups.length === 0 || loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choisir un groupe" />
                  </SelectTrigger>
                  <SelectContent>
                    {groups.map(group => (
                      <SelectItem key={group.id} value={group.id}>
                        {group.nom} ({group.student_count} étudiants)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedSubject && groups.length === 0 && !loading && (
                  <p className="text-xs text-amber-600">
                    Aucun groupe pour cette matière
                  </p>
                )}
              </div>

              {/* Semester Selection */}
              <div className="space-y-2">
                <Label>Semestre</Label>
                <Select value={semester} onValueChange={(val) => setSemester(val as SemesterType)} disabled={loading}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SEMESTER_1">Semestre 1</SelectItem>
                    <SelectItem value="SEMESTER_2">Semestre 2</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Academic Year */}
              <div className="space-y-2">
                <Label>Année Scolaire</Label>
                <Input 
                  type="text"
                  value={academicYear}
                  onChange={(e) => setAcademicYear(e.target.value)}
                  placeholder="2024-2025"
                  disabled={loading}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistics Card */}
      {selectedGroup && students.length > 0 && (() => {
        const stats = getGradeStats()
        return (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalGrades}</div>
                <p className="text-xs text-muted-foreground mt-1">notes enregistrées</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Étudiants Notés</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.studentsWithGrades}/{students.length}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round((stats.studentsWithGrades / students.length) * 100)}% complété
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Moyenne Classe</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats.averageGrade > 0 ? stats.averageGrade.toFixed(2) : '-'}/20
                </div>
                <p className="text-xs text-muted-foreground mt-1">moyenne générale</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Statut</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge variant={stats.studentsWithGrades === students.length ? "default" : "secondary"} className="text-sm">
                  {stats.studentsWithGrades === students.length ? (
                    <><CheckCircle className="h-3 w-3 mr-1" />Complet</>
                  ) : (
                    <><AlertCircle className="h-3 w-3 mr-1" />En cours</>
                  )}
                </Badge>
                <p className="text-xs text-muted-foreground mt-2">
                  {students.length - stats.studentsWithGrades} restant(s)
                </p>
              </CardContent>
            </Card>
          </div>
        )
      })()}

      {/* Students List */}
      {selectedGroup && students.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Étudiants - {getGroupName()}</CardTitle>
                <CardDescription>
                  {getSubjectName()} • {semester === 'SEMESTER_1' ? 'Semestre 1' : 'Semestre 2'} • {academicYear}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">
                  <Users className="h-4 w-4 mr-1" />
                  {students.length} étudiants
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {students.map((student) => {
                const average = calculateStudentAverage(student.grades)
                
                return (
                  <Card key={student.id} className="overflow-hidden">
                    <CardHeader className="bg-muted/50">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">
                            {student.prenom} {student.nom}
                          </CardTitle>
                          <CardDescription>{student.email}</CardDescription>
                        </div>
                        <div className="flex items-center gap-3">
                          {average !== null && (
                            <div className="text-right">
                              <div className="text-2xl font-bold">
                                {average.toFixed(2)}/20
                              </div>
                              <div className="text-xs text-muted-foreground">
                                Moyenne
                              </div>
                            </div>
                          )}
                          <Button 
                            size="sm"
                            onClick={() => openGradeDialog(student)}
                          >
                            <Plus className="h-4 w-4 mr-1" />
                            Ajouter Note
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="p-4">
                      {student.grades.length > 0 ? (
                        <div className="space-y-2">
                          {student.grades.map((grade) => (
                            <div 
                              key={grade.id}
                              className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                            >
                              <div className="flex items-center gap-4">
                                <div className="flex flex-col items-center">
                                  <div className={`text-2xl font-bold ${
                                    grade.valeur >= 10 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {grade.valeur}/20
                                  </div>
                                  <Badge 
                                    variant={grade.valeur >= 10 ? "default" : "destructive"}
                                    className="text-xs"
                                  >
                                    {grade.valeur >= 10 ? 'Admis' : 'Non admis'}
                                  </Badge>
                                </div>
                                <div className="flex-1">
                                  <div className="font-medium">
                                    {gradeTypeLabels[grade.type as GradeType]}
                                  </div>
                                  <div className="text-sm text-muted-foreground">
                                    Coef: {grade.coefficient}
                                    {grade.date_examen && ` • ${new Date(grade.date_examen).toLocaleDateString('fr-FR')}`}
                                  </div>
                                  {grade.observation && (
                                    <div className="text-xs text-muted-foreground mt-1 italic">
                                      📝 {grade.observation}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => openGradeDialog(student, grade)}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleDeleteGrade(grade.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                          <p>Aucune note enregistrée</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedGroup && students.length === 0 && !loading && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <Users className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p>Aucun étudiant trouvé dans ce groupe</p>
          </CardContent>
        </Card>
      )}

      {/* Grade Entry Dialog */}
      <Dialog open={showGradeDialog} onOpenChange={setShowGradeDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingGrade ? 'Modifier la Note' : 'Ajouter une Note'}
            </DialogTitle>
            <DialogDescription>
              {selectedStudent && `${selectedStudent.prenom} ${selectedStudent.nom}`}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="valeur">Note <span className="text-red-500">*</span></Label>
              <div className="flex gap-2">
                <Input
                  id="valeur"
                  type="number"
                  step="0.5"
                  min="0"
                  max="20"
                  value={gradeForm.valeur}
                  onChange={(e) => setGradeForm({...gradeForm, valeur: e.target.value})}
                  placeholder="0-20"
                  className="flex-1"
                />
                <span className="flex items-center text-2xl font-bold text-muted-foreground">/20</span>
              </div>
              <div className="flex gap-2">
                <p className="text-xs text-muted-foreground flex-1">
                  Le coefficient sera automatiquement pris de la matière
                </p>
                {gradeForm.valeur && parseFloat(gradeForm.valeur) >= 0 && parseFloat(gradeForm.valeur) <= 20 && (
                  <Badge variant={parseFloat(gradeForm.valeur) >= 10 ? "default" : "destructive"}>
                    {parseFloat(gradeForm.valeur) >= 10 ? 'Admis' : 'Non admis'}
                  </Badge>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Type <span className="text-red-500">*</span></Label>
              <Select 
                value={gradeForm.type} 
                onValueChange={(val) => setGradeForm({...gradeForm, type: val as GradeType})}
              >
                <SelectTrigger id="type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(gradeTypeLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Date d'examen</Label>
              <Input
                id="date"
                type="date"
                value={gradeForm.date_examen}
                onChange={(e) => setGradeForm({...gradeForm, date_examen: e.target.value})}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="observation">Observation</Label>
              <Input
                id="observation"
                type="text"
                value={gradeForm.observation}
                onChange={(e) => setGradeForm({...gradeForm, observation: e.target.value})}
                placeholder="Remarques optionnelles"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                onClick={closeGradeDialog}
                className="flex-1"
                disabled={loading}
              >
                Annuler
              </Button>
              <Button
                onClick={handleSubmitGrade}
                className="flex-1"
                disabled={loading}
              >
                <Save className="h-4 w-4 mr-2" />
                {editingGrade ? 'Modifier' : 'Enregistrer'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
