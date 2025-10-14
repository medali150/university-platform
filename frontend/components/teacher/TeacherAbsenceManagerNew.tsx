'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Users, 
  BookOpen, 
  GraduationCap, 
  Building2, 
  Search,
  Mail,
  User,
  ChevronDown,
  ChevronUp,
  UserX,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Save
} from 'lucide-react'
import { TeacherAPI, TeacherGroup, TeacherGroupsResponse, TeacherSchedule } from '@/lib/teacher-api'

interface GroupStudent {
  id: string
  nom: string
  prenom: string
  email: string
  isAbsent?: boolean
  absenceMotif?: string
}

interface GroupSchedule {
  id: string
  date: string
  heure_debut: string
  heure_fin: string
  matiere: {
    id: string
    nom: string
  }
  groupe: {
    id: string
    nom: string
  }
  salle: {
    id: string
    code: string
  }
}

export default function TeacherAbsenceManagerNew() {
  const searchParams = useSearchParams()
  const preSelectedGroupId = searchParams.get('group')
  
  const [activeTab, setActiveTab] = useState(preSelectedGroupId ? 'students' : 'groups')
  const [groupsData, setGroupsData] = useState<TeacherGroupsResponse | null>(null)
  const [todaySchedule, setTodaySchedule] = useState<TeacherSchedule[]>([])
  const [selectedGroup, setSelectedGroup] = useState<TeacherGroup | null>(null)
  const [selectedSchedule, setSelectedSchedule] = useState<GroupSchedule | null>(null)
  const [groupStudents, setGroupStudents] = useState<GroupStudent[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(new Set())
  const [absenceMotif, setAbsenceMotif] = useState('')
  const [isMarkingAbsence, setIsMarkingAbsence] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupsResponse, scheduleResponse] = await Promise.all([
          TeacherAPI.getGroupsDetailed(),
          TeacherAPI.getTodaySchedule()
        ])
        
        setGroupsData(groupsResponse)
        setTodaySchedule(scheduleResponse)
        
        // If there's a pre-selected group, load it
        if (preSelectedGroupId && groupsResponse.groups) {
          const preSelectedGroup = groupsResponse.groups.find(g => g.id === preSelectedGroupId)
          if (preSelectedGroup) {
            handleGroupSelect(preSelectedGroup)
          }
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [preSelectedGroupId])

  const handleGroupSelect = async (group: TeacherGroup, schedule?: GroupSchedule) => {
    try {
      setSelectedGroup(group)
      setSelectedSchedule(schedule || null)
      setLoading(true)
      
      const students = await TeacherAPI.getGroupStudents(group.id, schedule?.id)
      setGroupStudents(students.students || [])
      setActiveTab('students')
    } catch (error) {
      console.error('Error fetching group students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStudentSelect = (studentId: string, isSelected: boolean) => {
    const newSelected = new Set(selectedStudents)
    if (isSelected) {
      newSelected.add(studentId)
    } else {
      newSelected.delete(studentId)
    }
    setSelectedStudents(newSelected)
  }

  const handleMarkAbsences = async () => {
    if (!selectedSchedule || selectedStudents.size === 0) return

    setIsMarkingAbsence(true)
    try {
      // Mark absences for each selected student
      const promises = Array.from(selectedStudents).map(studentId =>
        TeacherAPI.markAbsence({
          student_id: studentId,
          schedule_id: selectedSchedule.id,
          is_absent: true,
          motif: absenceMotif
        })
      )

      await Promise.all(promises)
      
      // Show success message
      alert(`Absences marquées pour ${selectedStudents.size} étudiant(s)`)
      
      setSelectedStudents(new Set())
      setAbsenceMotif('')
      
      // Refresh student data
      if (selectedGroup) {
        const students = await TeacherAPI.getGroupStudents(selectedGroup.id, selectedSchedule.id)
        setGroupStudents(students.students || [])
      }
    } catch (error) {
      console.error('Error marking absences:', error)
      alert('Erreur lors de la création des absences')
    } finally {
      setIsMarkingAbsence(false)
    }
  }

  const filteredGroups = groupsData?.groups.filter(group =>
    group.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    group.specialty.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const filteredStudents = groupStudents.filter(student =>
    student.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading && !groupsData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Gestion des Absences</h1>
        <p className="text-muted-foreground">
          Marquez les absences des étudiants pour vos cours
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="groups">Mes Groupes</TabsTrigger>
          <TabsTrigger value="students">Étudiants</TabsTrigger>
          <TabsTrigger value="schedule">Emploi du Temps</TabsTrigger>
        </TabsList>

        {/* Groups Tab */}
        <TabsContent value="groups" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sélectionner un Groupe</CardTitle>
              <CardDescription>
                Choisissez un groupe pour marquer les absences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Rechercher un groupe..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>

                <div className="grid gap-4">
                  {filteredGroups.length === 0 ? (
                    <div className="text-center p-8 text-muted-foreground">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Aucun groupe trouvé</p>
                    </div>
                  ) : (
                    filteredGroups.map((group) => (
                      <Card key={group.id} className="cursor-pointer hover:bg-accent transition-colors">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <Users className="h-5 w-5" />
                                <h3 className="font-semibold">{group.nom}</h3>
                                <Badge variant="outline">{group.student_count} étudiants</Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {group.level} - {group.specialty} • Département: {group.department}
                              </p>
                            </div>
                            <Button
                              onClick={() => handleGroupSelect(group)}
                              size="sm"
                            >
                              Sélectionner
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Students Tab */}
        <TabsContent value="students" className="space-y-4">
          {selectedGroup ? (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Étudiants - {selectedGroup.nom}</CardTitle>
                      <CardDescription>
                        {selectedGroup.level} - {selectedGroup.specialty}
                      </CardDescription>
                    </div>
                    <Badge variant="outline">
                      {groupStudents.length} étudiants
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="relative flex-1 max-w-sm">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Rechercher un étudiant..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-8"
                        />
                      </div>
                      
                      {selectedStudents.size > 0 && (
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button>
                              <UserX className="mr-2 h-4 w-4" />
                              Marquer Absences ({selectedStudents.size})
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Marquer les Absences</DialogTitle>
                              <DialogDescription>
                                Marquer {selectedStudents.size} étudiant(s) comme absent(s)
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <Label htmlFor="motif">Motif (optionnel)</Label>
                                <Textarea
                                  id="motif"
                                  value={absenceMotif}
                                  onChange={(e) => setAbsenceMotif(e.target.value)}
                                  placeholder="Raison de l'absence..."
                                  className="resize-none"
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button
                                onClick={handleMarkAbsences}
                                disabled={isMarkingAbsence || !selectedSchedule}
                              >
                                {isMarkingAbsence ? 'Enregistrement...' : 'Confirmer'}
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      )}
                    </div>

                    {!selectedSchedule && (
                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-amber-600" />
                          <p className="text-sm text-amber-800">
                            Sélectionnez un cours dans l'onglet "Emploi du Temps" pour marquer les absences
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="grid gap-3">
                      {loading ? (
                        <div className="flex items-center justify-center p-8">
                          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                        </div>
                      ) : filteredStudents.length === 0 ? (
                        <div className="text-center p-8 text-muted-foreground">
                          <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p>Aucun étudiant trouvé</p>
                        </div>
                      ) : (
                        filteredStudents.map((student) => (
                          <div key={student.id} className="flex items-center space-x-4 rounded-lg border p-3">
                            <Checkbox
                              checked={selectedStudents.has(student.id)}
                              onCheckedChange={(checked) => 
                                handleStudentSelect(student.id, checked as boolean)
                              }
                              disabled={!selectedSchedule}
                            />
                            <Avatar className="h-10 w-10">
                              <AvatarImage src={`/placeholder-avatar.png`} alt={student.nom} />
                              <AvatarFallback>
                                {student.prenom.charAt(0)}{student.nom.charAt(0)}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium">
                                {student.prenom} {student.nom}
                              </p>
                              <p className="text-sm text-muted-foreground flex items-center gap-1">
                                <Mail className="h-3 w-3" />
                                {student.email}
                              </p>
                            </div>
                            {student.isAbsent && (
                              <Badge variant="destructive">Absent</Badge>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center p-8">
                <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-muted-foreground">
                  Sélectionnez d'abord un groupe dans l'onglet "Mes Groupes"
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Schedule Tab */}
        <TabsContent value="schedule" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Emploi du Temps d'Aujourd'hui</CardTitle>
              <CardDescription>
                Sélectionnez un cours pour marquer les absences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {todaySchedule.length === 0 ? (
                  <div className="text-center p-8 text-muted-foreground">
                    <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun cours prévu aujourd'hui</p>
                  </div>
                ) : (
                  todaySchedule.map((schedule) => (
                    <Card 
                      key={schedule.id} 
                      className={`cursor-pointer transition-colors ${
                        selectedSchedule?.id === schedule.id 
                          ? 'bg-primary/10 border-primary' 
                          : 'hover:bg-accent'
                      }`}
                      onClick={() => setSelectedSchedule(schedule as GroupSchedule)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <BookOpen className="h-5 w-5" />
                              <h3 className="font-semibold">{schedule.matiere.nom}</h3>
                              <Badge variant="outline">{schedule.groupe.nom}</Badge>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Clock className="h-4 w-4" />
                                {schedule.heure_debut} - {schedule.heure_fin}
                              </span>
                              <span className="flex items-center gap-1">
                                <Building2 className="h-4 w-4" />
                                {schedule.salle.code}
                              </span>
                            </div>
                          </div>
                          {selectedSchedule?.id === schedule.id && (
                            <CheckCircle className="h-5 w-5 text-primary" />
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {selectedSchedule && (
            <Card>
              <CardHeader>
                <CardTitle>Cours Sélectionné</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p><strong>Matière:</strong> {selectedSchedule.matiere.nom}</p>
                  <p><strong>Groupe:</strong> {selectedSchedule.groupe.nom}</p>
                  <p><strong>Horaire:</strong> {selectedSchedule.heure_debut} - {selectedSchedule.heure_fin}</p>
                  <p><strong>Salle:</strong> {selectedSchedule.salle.code}</p>
                </div>
                <div className="mt-4">
                  <Button
                    onClick={() => {
                      const group = groupsData?.groups.find(g => g.id === selectedSchedule.groupe.id)
                      if (group) {
                        handleGroupSelect(group, selectedSchedule)
                      }
                    }}
                  >
                    Voir les Étudiants
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}