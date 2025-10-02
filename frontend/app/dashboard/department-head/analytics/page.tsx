'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendingUp, Users, Calendar, Clock, Target, Download, RefreshCw } from 'lucide-react'

export default function AnalyticsPage() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analyses et Statistiques</h1>
          <p className="text-muted-foreground">
            Vue d'ensemble des performances du département
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser
          </Button>
          <Button>
            <Download className="mr-2 h-4 w-4" />
            Exporter Rapport
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taux de Présence</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">94.2%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+2.1%</span> vs mois dernier
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utilisation Salles</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">87.5%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-600">-1.2%</span> vs mois dernier
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions Planifiées</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-muted-foreground">Ce semestre</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Heures Enseignées</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2,494h</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+156h</span> vs prévu
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Évolution de la Présence</CardTitle>
            <CardDescription>Taux de présence par semaine (derniers 3 mois)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
              <div className="text-center text-gray-500">
                <BarChart3 className="mx-auto h-12 w-12 mb-2" />
                <p>Graphique de présence</p>
                <p className="text-sm">Données en temps réel</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Répartition par Matière</CardTitle>
            <CardDescription>Heures d'enseignement par discipline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Mathématiques</span>
                  <span className="font-medium">420h (24%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '24%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Physique</span>
                  <span className="font-medium">350h (20%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '20%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Chimie</span>
                  <span className="font-medium">280h (16%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '16%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Informatique</span>
                  <span className="font-medium">245h (14%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '14%' }}></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Autres</span>
                  <span className="font-medium">455h (26%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-600 h-2 rounded-full" style={{ width: '26%' }}></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Analytics */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Performance des Enseignants</CardTitle>
            <CardDescription>Top 5 enseignants par taux de présence</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 font-semibold text-sm">1</span>
                  </div>
                  <div>
                    <p className="font-medium">Prof. Martin</p>
                    <p className="text-xs text-muted-foreground">Mathématiques</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800">98.5%</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold text-sm">2</span>
                  </div>
                  <div>
                    <p className="font-medium">Prof. Dubois</p>
                    <p className="text-xs text-muted-foreground">Physique</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">97.2%</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 font-semibold text-sm">3</span>
                  </div>
                  <div>
                    <p className="font-medium">Prof. Laurent</p>
                    <p className="text-xs text-muted-foreground">Chimie</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-purple-100 text-purple-800">96.8%</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <span className="text-yellow-600 font-semibold text-sm">4</span>
                  </div>
                  <div>
                    <p className="font-medium">Prof. Bernard</p>
                    <p className="text-xs text-muted-foreground">Informatique</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">95.9%</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-gray-600 font-semibold text-sm">5</span>
                  </div>
                  <div>
                    <p className="font-medium">Prof. Rousseau</p>
                    <p className="text-xs text-muted-foreground">Biologie</p>
                  </div>
                </div>
                <Badge variant="secondary" className="bg-gray-100 text-gray-800">94.3%</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Utilisation des Salles</CardTitle>
            <CardDescription>Efficacité d'occupation par salle</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Salle A101</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '95%' }}></div>
                  </div>
                  <span className="text-xs font-medium">95%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Salle B205</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '89%' }}></div>
                  </div>
                  <span className="text-xs font-medium">89%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Salle C102</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '82%' }}></div>
                  </div>
                  <span className="text-xs font-medium">82%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Labo 1</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: '78%' }}></div>
                  </div>
                  <span className="text-xs font-medium">78%</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Amphi A</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-red-600 h-2 rounded-full" style={{ width: '65%' }}></div>
                  </div>
                  <span className="text-xs font-medium">65%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Objectifs du Semestre</CardTitle>
            <CardDescription>Progression vers les objectifs fixés</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Taux de Présence</span>
                  <span className="text-sm text-muted-foreground">94.2% / 95%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '99%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Quasi atteint</span>
                  <span>99% de l'objectif</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Sessions Planifiées</span>
                  <span className="text-sm text-muted-foreground">1,247 / 1,200</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Dépassé</span>
                  <span>104% de l'objectif</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Utilisation Salles</span>
                  <span className="text-sm text-muted-foreground">87.5% / 90%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '97%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>En progression</span>
                  <span>97% de l'objectif</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Activité Récente</CardTitle>
          <CardDescription>Dernières actions et événements importants</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 border-l-4 border-l-green-500 bg-green-50">
              <Target className="h-5 w-5 text-green-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-800">Objectif de présence atteint</p>
                <p className="text-sm text-green-600">Le taux de présence a dépassé 94% cette semaine</p>
              </div>
              <span className="text-xs text-green-500">Il y a 2h</span>
            </div>
            
            <div className="flex items-center space-x-4 p-4 border-l-4 border-l-blue-500 bg-blue-50">
              <Calendar className="h-5 w-5 text-blue-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800">Nouvelle session programmée</p>
                <p className="text-sm text-blue-600">Cours de rattrapage - Mathématiques avancées</p>
              </div>
              <span className="text-xs text-blue-500">Il y a 4h</span>
            </div>
            
            <div className="flex items-center space-x-4 p-4 border-l-4 border-l-yellow-500 bg-yellow-50">
              <Users className="h-5 w-5 text-yellow-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-800">Alerte capacité salle</p>
                <p className="text-sm text-yellow-600">Amphi A approche de la limite de capacité</p>
              </div>
              <span className="text-xs text-yellow-500">Il y a 6h</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}