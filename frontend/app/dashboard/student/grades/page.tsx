'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { BookOpen, TrendingUp, Award, FileText, Calendar, User } from 'lucide-react'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { api } from '@/lib/api'

interface Grade {
  id: string
  valeur: number
  coefficient: number
  type: string
  date_examen: string | null
  observation: string | null
  enseignant: string
}

interface SubjectGrades {
  matiere_id: string
  matiere_nom: string
  coefficient: number
  moyenne: number | null
  validee: boolean
  grades: Grade[]
}

interface StudentGradesData {
  student: {
    id: string
    nom: string
    prenom: string
    email: string
    groupe: string
    niveau: string
    specialite: string
  }
  moyenne_generale: number | null
  rang: number | null
  validee: boolean
  subjects: SubjectGrades[]
  semestre: string
  annee_scolaire: string
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

export default function StudentGradesPage() {
  const { user, isLoading: authLoading } = useRequireRole('STUDENT' as Role)
  
  const [loading, setLoading] = useState(false)
  const [gradesData, setGradesData] = useState<StudentGradesData | null>(null)
  const [semestre, setSemestre] = useState<SemesterType>('SEMESTER_1')
  const [anneeScolaire, setAnneeScolaire] = useState('2024-2025')

  useEffect(() => {
    if (user && !authLoading) {
      fetchGrades()
    }
  }, [user, authLoading, semestre, anneeScolaire])

  const fetchGrades = async () => {
    try {
      setLoading(true)
      const data = await api.getStudentGrades({
        semestre,
        annee_scolaire: anneeScolaire
      })
      setGradesData(data)
    } catch (error: any) {
      console.error('Error fetching grades:', error)
      toast.error(error.message || 'Impossible de charger les notes')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (moyenne: number | null) => {
    if (moyenne === null) return <Badge variant="outline">Pas de notes</Badge>
    if (moyenne >= 16) return <Badge className="bg-green-500">Excellent</Badge>
    if (moyenne >= 14) return <Badge className="bg-blue-500">Bien</Badge>
    if (moyenne >= 10) return <Badge className="bg-yellow-500">Passable</Badge>
    return <Badge className="bg-red-500">Insuffisant</Badge>
  }

  const getGradeColor = (valeur: number) => {
    if (valeur >= 16) return 'text-green-600'
    if (valeur >= 14) return 'text-blue-600'
    if (valeur >= 10) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (authLoading || loading) {
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
        <h1 className="text-3xl font-bold tracking-tight">Mes Notes</h1>
        <p className="text-muted-foreground">
          Consultez vos notes et moyennes
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Période</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Semestre</Label>
              <Select value={semestre} onValueChange={(val) => setSemestre(val as SemesterType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SEMESTER_1">Semestre 1</SelectItem>
                  <SelectItem value="SEMESTER_2">Semestre 2</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Année Scolaire</Label>
              <Select value={anneeScolaire} onValueChange={setAnneeScolaire}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2024-2025">2024-2025</SelectItem>
                  <SelectItem value="2023-2024">2023-2024</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Student Info & Overall Average */}
      {gradesData && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Moyenne Générale
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {gradesData.moyenne_generale !== null
                    ? `${gradesData.moyenne_generale.toFixed(2)}/20`
                    : '—'}
                </div>
                <div className="mt-2">
                  {getStatusBadge(gradesData.moyenne_generale)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Classement
                </CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {gradesData.rang ? `#${gradesData.rang}` : '—'}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {gradesData.student.groupe}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Matières
                </CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {gradesData.subjects.length}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {gradesData.subjects.filter(s => s.validee).length} validées
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Subject Grades */}
          <div className="space-y-4">
            {gradesData.subjects.length > 0 ? (
              gradesData.subjects.map((subject) => (
                <Card key={subject.matiere_id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{subject.matiere_nom}</CardTitle>
                        <CardDescription>
                          Coefficient: {subject.coefficient}
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-3">
                        {subject.moyenne !== null ? (
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${getGradeColor(subject.moyenne)}`}>
                              {subject.moyenne.toFixed(2)}/20
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Moyenne
                            </div>
                          </div>
                        ) : (
                          <div className="text-muted-foreground">
                            Pas de notes
                          </div>
                        )}
                        {subject.validee && (
                          <Badge className="bg-green-500">✓ Validée</Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {subject.grades.length > 0 ? (
                      <div className="space-y-3">
                        {subject.grades.map((grade) => (
                          <div
                            key={grade.id}
                            className="flex items-center justify-between p-3 border rounded-lg"
                          >
                            <div className="flex items-center gap-4">
                              <div className={`text-2xl font-bold ${getGradeColor(grade.valeur)}`}>
                                {grade.valeur}/20
                              </div>
                              <div>
                                <div className="font-medium">
                                  {gradeTypeLabels[grade.type as GradeType]}
                                </div>
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                  <span>Coef: {grade.coefficient}</span>
                                  {grade.date_examen && (
                                    <>
                                      <span>•</span>
                                      <Calendar className="h-3 w-3" />
                                      <span>{new Date(grade.date_examen).toLocaleDateString('fr-FR')}</span>
                                    </>
                                  )}
                                </div>
                                <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                                  <User className="h-3 w-3" />
                                  <span>{grade.enseignant}</span>
                                </div>
                                {grade.observation && (
                                  <div className="text-xs text-muted-foreground mt-1 italic">
                                    {grade.observation}
                                  </div>
                                )}
                              </div>
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
              ))
            ) : (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Aucune matière trouvée pour cette période</p>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  )
}
