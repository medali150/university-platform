'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Group } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Users, Search, X, Loader2, GraduationCap, Mail, Phone, Calendar, TrendingUp } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'sonner'

export default function ClassesManagementPage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  
  const [groupes, setGroupes] = useState<any[]>([])
  const [selectedGroupe, setSelectedGroupe] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (user && !authLoading) {
      loadGroupes()
    }
  }, [user, authLoading])

  const loadGroupes = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load all groupes with students  
      const groupesData = await api.getGroups()
      
      setGroupes(groupesData)
    } catch (err) {
      console.error('Error loading groupes:', err)
      setError('Erreur lors du chargement des classes')
      toast.error('Erreur lors du chargement des classes')
    } finally {
      setLoading(false)
    }
  }

  const loadGroupeDetails = async (groupeId: string) => {
    try {
      // Load groupe details - for now just use the existing data
      const groupe = groupes.find(g => g.id === groupeId)
      if (groupe) {
        setSelectedGroupe(groupe)
      }
    } catch (err) {
      console.error('Error loading groupe details:', err)
      toast.error('Erreur lors du chargement des détails')
    }
  }

  const filteredGroupes = groupes.filter(groupe =>
    groupe.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    groupe.niveau?.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    groupe.niveau?.specialite?.nom.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const calculateOccupancy = (groupe: any) => {
    const count = groupe._count?.etudiants || groupe.etudiants?.length || 0
    const percentage = groupe.capacite > 0 ? (count / groupe.capacite) * 100 : 0
    return { count, percentage: Math.round(percentage) }
  }

  const getOccupancyColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600 bg-red-100'
    if (percentage >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-green-600 bg-green-100'
  }

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <GraduationCap className="h-8 w-8" />
            Gestion des Classes
          </h1>
          <p className="text-muted-foreground">
            Vue d'ensemble des classes et étudiants du département
          </p>
        </div>
        <Button onClick={loadGroupes} variant="outline">
          <Loader2 className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher par classe, niveau ou spécialité..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-10"
            />
            {searchTerm && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1 h-8 w-8 p-0"
                onClick={() => setSearchTerm('')}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Statistics Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Classes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{groupes.length}</div>
            <p className="text-xs text-muted-foreground">Classes actives</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Étudiants</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {groupes.reduce((sum, g) => sum + (g._count?.etudiants || g.etudiants?.length || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">Inscrits au département</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Capacité Moyenne</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {groupes.length > 0 
                ? Math.round(groupes.reduce((sum, g) => {
                    const { percentage } = calculateOccupancy(g)
                    return sum + percentage
                  }, 0) / groupes.length) 
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">Taux d'occupation</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Classes Pleines</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {groupes.filter(g => calculateOccupancy(g).percentage >= 90).length}
            </div>
            <p className="text-xs text-muted-foreground">≥ 90% de capacité</p>
          </CardContent>
        </Card>
      </div>

      {/* Classes List */}
      {error ? (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadGroupes} className="mt-4" variant="outline">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      ) : filteredGroupes.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                {searchTerm ? 'Aucune classe trouvée' : 'Aucune classe'}
              </h3>
              <p className="text-muted-foreground">
                {searchTerm 
                  ? 'Aucune classe ne correspond à votre recherche'
                  : 'Aucune classe disponible'
                }
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredGroupes.map((groupe) => {
            const { count, percentage } = calculateOccupancy(groupe)
            return (
              <Card key={groupe.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl">{groupe.nom}</CardTitle>
                      <CardDescription>
                        {groupe.niveau?.specialite?.nom} - {groupe.niveau?.nom}
                      </CardDescription>
                    </div>
                    <Badge className={getOccupancyColor(percentage)}>
                      {percentage}%
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Effectif:</span>
                      <span className="font-medium">{count} / {groupe.capacite} étudiants</span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          percentage >= 90 ? 'bg-red-600' : 
                          percentage >= 70 ? 'bg-yellow-600' : 
                          'bg-green-600'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      ></div>
                    </div>

                    <Button 
                      onClick={() => loadGroupeDetails(groupe.id)} 
                      className="w-full"
                      variant="outline"
                    >
                      <Users className="h-4 w-4 mr-2" />
                      Voir les étudiants ({count})
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Student Details Dialog */}
      {selectedGroupe && (
        <Card className="mt-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Étudiants de {selectedGroupe.nom}</CardTitle>
                <CardDescription>
                  {selectedGroupe.niveau?.specialite?.nom} - {selectedGroupe.niveau?.nom}
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => setSelectedGroupe(null)}>
                <X className="h-4 w-4 mr-2" />
                Fermer
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {selectedGroupe.etudiants && selectedGroupe.etudiants.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Prénom</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Téléphone</TableHead>
                    <TableHead>Date de Naissance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedGroupe.etudiants.map((student) => (
                    <TableRow key={student.id}>
                      <TableCell className="font-medium">{student.utilisateur.nom}</TableCell>
                      <TableCell>{student.utilisateur.prenom}</TableCell>
                      <TableCell>
                        <a href={`mailto:${student.utilisateur.email}`} className="text-blue-600 hover:underline flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {student.utilisateur.email}
                        </a>
                      </TableCell>
                      <TableCell>
                        {student.utilisateur.telephone ? (
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {student.utilisateur.telephone}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {student.date_naissance ? (
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {new Date(student.date_naissance).toLocaleDateString('fr-FR')}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucun étudiant inscrit dans cette classe</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
