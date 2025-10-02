'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Settings, Zap, Clock, Users, Calendar, CheckCircle, AlertTriangle } from 'lucide-react'
import { useState } from 'react'

export default function AutoSchedulingPage() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [isGenerating, setIsGenerating] = useState(false)

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const handleAutoGenerate = async () => {
    setIsGenerating(true)
    // Simulate auto-generation process
    setTimeout(() => {
      setIsGenerating(false)
    }, 3000)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Génération Automatique d'Emploi du Temps</h1>
          <p className="text-muted-foreground">
            Créez automatiquement des emplois du temps optimisés pour votre département
          </p>
        </div>
        <Button onClick={handleAutoGenerate} disabled={isGenerating}>
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Génération...
            </>
          ) : (
            <>
              <Zap className="mr-2 h-4 w-4" />
              Générer Automatiquement
            </>
          )}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Matières</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15</div>
            <p className="text-xs text-muted-foreground">À programmer</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">Disponibles</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Salles</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">20</div>
            <p className="text-xs text-muted-foreground">Disponibles</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Créneaux</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45</div>
            <p className="text-xs text-muted-foreground">Par semaine</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Paramètres de Génération</CardTitle>
            <CardDescription>Configurez les contraintes pour la génération automatique</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Heures de début</label>
              <div className="flex gap-2">
                <Badge variant="secondary">08:00</Badge>
                <Badge variant="secondary">09:30</Badge>
                <Badge variant="secondary">11:00</Badge>
                <Badge variant="secondary">14:00</Badge>
                <Badge variant="secondary">15:30</Badge>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Durée des sessions</label>
              <div className="flex gap-2">
                <Badge variant="outline">1h30</Badge>
                <Badge variant="secondary">2h00</Badge>
                <Badge variant="outline">3h00</Badge>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Jours de la semaine</label>
              <div className="flex gap-2">
                <Badge variant="secondary">Lundi</Badge>
                <Badge variant="secondary">Mardi</Badge>
                <Badge variant="secondary">Mercredi</Badge>
                <Badge variant="secondary">Jeudi</Badge>
                <Badge variant="secondary">Vendredi</Badge>
                <Badge variant="outline">Samedi</Badge>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Contraintes spéciales</label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="no-conflicts" className="rounded" defaultChecked />
                  <label htmlFor="no-conflicts" className="text-sm">Éviter les conflits de salle</label>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="teacher-availability" className="rounded" defaultChecked />
                  <label htmlFor="teacher-availability" className="text-sm">Respecter la disponibilité des enseignants</label>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="room-capacity" className="rounded" defaultChecked />
                  <label htmlFor="room-capacity" className="text-sm">Vérifier la capacité des salles</label>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" id="lunch-break" className="rounded" defaultChecked />
                  <label htmlFor="lunch-break" className="text-sm">Pause déjeuner obligatoire (12:00-14:00)</label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Résultats de la Dernière Génération</CardTitle>
            <CardDescription>Analyse de performance de l'algorithme</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-green-50 border border-green-200">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-green-800">Génération Réussie</p>
                  <p className="text-xs text-green-600">Il y a 2 heures</p>
                </div>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                98% Optimisé
              </Badge>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium">Statistiques:</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Sessions créées:</span>
                  <span className="font-medium">245</span>
                </div>
                <div className="flex justify-between">
                  <span>Conflits résolus:</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex justify-between">
                  <span>Taux d'utilisation des salles:</span>
                  <span className="font-medium">89%</span>
                </div>
                <div className="flex justify-between">
                  <span>Temps de génération:</span>
                  <span className="font-medium">2.3s</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">Problèmes détectés:</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span>3 conflits mineurs de préférence d'horaire</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span>1 salle temporairement sur-capacité</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historique des Générations</CardTitle>
          <CardDescription>Vos dernières générations automatiques</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <Calendar className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-medium">Génération Semestre Automne 2024</p>
                  <p className="text-sm text-muted-foreground">15 septembre 2024 • 245 sessions créées</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="bg-green-100 text-green-800">Succès</Badge>
                <Button variant="outline" size="sm">Voir Détails</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <Calendar className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="font-medium">Test Génération Rapide</p>
                  <p className="text-sm text-muted-foreground">12 septembre 2024 • 180 sessions créées</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">Test</Badge>
                <Button variant="outline" size="sm">Voir Détails</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <Calendar className="h-8 w-8 text-yellow-600" />
                <div>
                  <p className="font-medium">Génération Manuelle Corrigée</p>
                  <p className="text-sm text-muted-foreground">8 septembre 2024 • 220 sessions créées</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Partiel</Badge>
                <Button variant="outline" size="sm">Voir Détails</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}