'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Plus, Search, Edit, Trash2, Users, Clock } from 'lucide-react'
import { useState } from 'react'

export default function SubjectsPage() {
  const { user, isLoading } = useRequireRole(['DEPARTMENT_HEAD', 'ADMIN'] as Role[])
  const [searchTerm, setSearchTerm] = useState('')

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const subjects = [
    {
      id: 1,
      name: 'Mathématiques Fondamentales',
      code: 'MATH101',
      credits: 6,
      hours: 48,
      semester: 'S1',
      groups: ['Groupe A', 'Groupe B'],
      teachers: ['Prof. Martin', 'Prof. Dubois'],
      status: 'active'
    },
    {
      id: 2,
      name: 'Physique Générale',
      code: 'PHYS201',
      credits: 5,
      hours: 40,
      semester: 'S2',
      groups: ['Groupe A', 'Groupe C'],
      teachers: ['Prof. Laurent'],
      status: 'active'
    },
    {
      id: 3,
      name: 'Chimie Organique',
      code: 'CHEM301',
      credits: 4,
      hours: 32,
      semester: 'S3',
      groups: ['Groupe B'],
      teachers: ['Prof. Bernard'],
      status: 'active'
    },
    {
      id: 4,
      name: 'Informatique Théorique',
      code: 'INFO401',
      credits: 5,
      hours: 40,
      semester: 'S4',
      groups: ['Groupe A', 'Groupe B', 'Groupe C'],
      teachers: ['Prof. Rousseau', 'Prof. Moreau'],
      status: 'draft'
    },
    {
      id: 5,
      name: 'Statistiques Appliquées',
      code: 'STAT501',
      credits: 4,
      hours: 32,
      semester: 'S5',
      groups: ['Groupe A'],
      teachers: ['Prof. Petit'],
      status: 'active'
    }
  ]

  const filteredSubjects = subjects.filter(subject =>
    subject.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    subject.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    subject.teachers.some(teacher => teacher.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Actif</Badge>
      case 'draft':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Brouillon</Badge>
      case 'inactive':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Inactif</Badge>
      default:
        return <Badge variant="secondary">Inconnu</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion des Matières</h1>
          <p className="text-muted-foreground">
            Gérez les matières, crédits et assignations du département
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Nouvelle Matière
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matières</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15</div>
            <p className="text-xs text-muted-foreground">5 actives ce semestre</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Crédits</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">72</div>
            <p className="text-xs text-muted-foreground">ECTS disponibles</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Heures d'Enseignement</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">576h</div>
            <p className="text-xs text-muted-foreground">Total planifié</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">Assignés aux matières</p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Rechercher et Filtrer</CardTitle>
          <CardDescription>Trouvez rapidement les matières que vous cherchez</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher par nom, code ou enseignant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              Filtrer par Semestre
            </Button>
            <Button variant="outline">
              Filtrer par Statut
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Subjects List */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des Matières</CardTitle>
          <CardDescription>
            {filteredSubjects.length} matière{filteredSubjects.length > 1 ? 's' : ''} trouvée{filteredSubjects.length > 1 ? 's' : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredSubjects.map((subject) => (
              <div key={subject.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-blue-600" />
                  </div>
                  
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold">{subject.name}</h3>
                      <Badge variant="outline">{subject.code}</Badge>
                      {getStatusBadge(subject.status)}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>{subject.credits} ECTS</span>
                      <span>•</span>
                      <span>{subject.hours}h de cours</span>
                      <span>•</span>
                      <span>Semestre {subject.semester}</span>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span>Groupes: {subject.groups.join(', ')}</span>
                      </div>
                      <span>•</span>
                      <div className="flex items-center space-x-1">
                        <span>Enseignants: {subject.teachers.join(', ')}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Actions Rapides</CardTitle>
            <CardDescription>Outils de gestion des matières</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Plus className="mr-2 h-4 w-4" />
              Créer une Nouvelle Matière
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Users className="mr-2 h-4 w-4" />
              Assigner des Enseignants
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <BookOpen className="mr-2 h-4 w-4" />
              Importer depuis Excel
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Search className="mr-2 h-4 w-4" />
              Générer Rapport Complet
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiques Rapides</CardTitle>
            <CardDescription>Vue d'ensemble du département</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Matières par Semestre</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>S1-S2</span>
                  <span>6 matières</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>S3-S4</span>
                  <span>5 matières</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>S5-S6</span>
                  <span>4 matières</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Répartition des Crédits</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Matières Fondamentales</span>
                  <span>40 ECTS</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Matières Spécialisées</span>
                  <span>24 ECTS</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Projets et Stages</span>
                  <span>8 ECTS</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}