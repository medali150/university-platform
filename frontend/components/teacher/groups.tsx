'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
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
  Eye,
  UserX
} from 'lucide-react'
import { TeacherAPI, TeacherGroup, TeacherGroupsResponse } from '@/lib/teacher-api'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function TeacherGroupsPage() {
  const router = useRouter()
  const [groupsData, setGroupsData] = useState<TeacherGroupsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const data = await TeacherAPI.getGroupsDetailed()
        setGroupsData(data)
      } catch (error) {
        console.error('Error fetching groups:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchGroups()
  }, [])

  const toggleGroupExpansion = (groupId: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId)
    } else {
      newExpanded.add(groupId)
    }
    setExpandedGroups(newExpanded)
  }

  const filteredGroups = groupsData?.groups.filter(group => {
    const matchesSearch = group.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         group.specialty.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         group.department.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesLevel = selectedLevel === 'all' || group.level === selectedLevel
    
    return matchesSearch && matchesLevel
  }) || []

  const uniqueLevels = [...new Set(groupsData?.groups.map(group => group.level) || [])]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!groupsData) {
    return (
      <div className="text-center p-8">
        <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p className="text-muted-foreground">Unable to load groups</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Groups</h1>
        <p className="text-muted-foreground">
          Manage and view all the groups you teach
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Groups</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{groupsData.total_groups}</div>
            <p className="text-xs text-muted-foreground">Groups you teach</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{groupsData.total_students}</div>
            <p className="text-xs text-muted-foreground">Students across all groups</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Subjects Taught</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {[...new Set(groupsData.groups.flatMap(g => g.subjects.map(s => s.id)))].length}
            </div>
            <p className="text-xs text-muted-foreground">Different subjects</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="search">Search Groups</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search by group name, specialty, or department..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="level">Filter by Level</Label>
              <select
                id="level"
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <option value="all">All Levels</option>
                {uniqueLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Groups List */}
      <div className="space-y-4">
        {filteredGroups.length === 0 ? (
          <Card>
            <CardContent className="text-center p-8">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">No groups found matching your criteria</p>
            </CardContent>
          </Card>
        ) : (
          filteredGroups.map((group) => (
            <Card key={group.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      {group.nom}
                      <Badge variant="outline">{group.student_count} students</Badge>
                    </CardTitle>
                    <CardDescription className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <GraduationCap className="h-4 w-4" />
                        {group.level} - {group.specialty}
                      </span>
                      <span className="flex items-center gap-1">
                        <Building2 className="h-4 w-4" />
                        {group.department}
                      </span>
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/dashboard/teacher/groups/${group.id}`)}
                    >
                      <Eye className="mr-2 h-4 w-4" />
                      Voir Étudiants
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/dashboard/teacher/absences?group=${group.id}`)}
                    >
                      <UserX className="mr-2 h-4 w-4" />
                      Absences
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleGroupExpansion(group.id)}
                    >
                      {expandedGroups.has(group.id) ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardHeader>

              {expandedGroups.has(group.id) && (
                <CardContent className="pt-0">
                  <div className="space-y-6">
                    {/* Students Section */}
                    <div>
                      <h4 className="font-medium mb-3">Students ({group.students.length})</h4>
                      <div className="grid gap-3">
                        {group.students.length === 0 ? (
                          <p className="text-center text-muted-foreground py-4">
                            No students enrolled in this group
                          </p>
                        ) : (
                          group.students.map((student) => (
                            <div key={student.id} className="flex items-center space-x-4 rounded-lg border p-3">
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
                            </div>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Subjects Section */}
                    <div>
                      <h4 className="font-medium mb-3">Subjects ({group.subjects.length})</h4>
                      <div className="grid gap-3">
                        {group.subjects.length === 0 ? (
                          <p className="text-center text-muted-foreground py-4">
                            No subjects assigned to this group
                          </p>
                        ) : (
                          group.subjects.map((subject) => (
                            <div key={subject.id} className="flex items-center space-x-4 rounded-lg border p-3">
                              <div className="flex-shrink-0">
                                <BookOpen className="h-10 w-10 p-2 bg-primary/10 text-primary rounded-lg" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium">{subject.nom}</p>
                                <p className="text-sm text-muted-foreground">Subject</p>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
