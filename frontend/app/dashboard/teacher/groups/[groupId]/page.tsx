'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ArrowLeft, Users, Mail, User, Search, UserX, Calendar, Clock } from 'lucide-react'
import { TeacherAPI } from '@/lib/teacher-api'

interface GroupStudent {
  id: string
  nom: string
  prenom: string
  email: string
  is_absent: boolean
  absence_id: string | null
}

interface GroupDetails {
  id: string
  nom: string
  niveau: {
    id: string
    nom: string
    specialite: {
      id: string
      nom: string
    }
  }
  students: GroupStudent[]
}

export default function GroupStudentsPage() {
  const params = useParams()
  const router = useRouter()
  const groupId = params.groupId as string
  
  const [groupDetails, setGroupDetails] = useState<GroupDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const fetchGroupDetails = async () => {
      try {
        const data = await TeacherAPI.getGroupStudents(groupId)
        setGroupDetails(data)
      } catch (error) {
        console.error('Error fetching group details:', error)
      } finally {
        setLoading(false)
      }
    }

    if (groupId) {
      fetchGroupDetails()
    }
  }, [groupId])

  const filteredStudents = groupDetails?.students.filter(student =>
    student.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!groupDetails) {
    return (
      <div className="text-center p-8">
        <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p className="text-muted-foreground">Groupe introuvable</p>
        <Button onClick={() => router.back()} className="mt-4">
          Retourner
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour aux groupes
        </Button>
        
        <h1 className="text-3xl font-bold tracking-tight">
          {groupDetails.nom}
        </h1>
        <p className="text-muted-foreground">
          {groupDetails.niveau.nom} - {groupDetails.niveau.specialite.nom}
        </p>
      </div>

      {/* Group Statistics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Étudiants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{groupDetails.students.length}</div>
            <p className="text-xs text-muted-foreground">Étudiants inscrits</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Matières</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">Matières enseignées</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-center p-6">
            <Button
              onClick={() => router.push(`/dashboard/teacher/absences?group=${groupId}`)}
              className="w-full"
            >
              <UserX className="mr-2 h-4 w-4" />
              Marquer Absences
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Subjects List - Not available from API */}

      {/* Students List */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des Étudiants</CardTitle>
          <CardDescription>
            Tous les étudiants de ce groupe
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher un étudiant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>

            <div className="grid gap-3">
              {filteredStudents.length === 0 ? (
                <div className="text-center p-8 text-muted-foreground">
                  <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Aucun étudiant trouvé</p>
                </div>
              ) : (
                filteredStudents.map((student) => (
                  <div key={student.id} className="flex items-center space-x-4 rounded-lg border p-4">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={`/placeholder-avatar.png`} alt={student.nom} />
                      <AvatarFallback>
                        {student.prenom.charAt(0)}{student.nom.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <p className="text-base font-medium">
                        {student.prenom} {student.nom}
                      </p>
                      <p className="text-sm text-muted-foreground flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        {student.email}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // Add functionality to view student details or mark individual absence
                        console.log('View student:', student.id)
                      }}
                    >
                      Détails
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}