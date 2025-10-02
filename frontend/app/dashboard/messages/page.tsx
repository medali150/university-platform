'use client'

import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { MessageSquare, Send, Search, Plus, Reply, Archive, Trash2 } from 'lucide-react'
import { useState } from 'react'

export default function MessagesPage() {
  const { user, loading } = useAuth()
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  if (loading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const messages = [
    {
      id: 1,
      from: 'Prof. Martin',
      fromRole: 'TEACHER',
      subject: 'Question sur l\'emploi du temps',
      preview: 'Bonjour, j\'aimerais discuter de quelques modifications...',
      content: 'Bonjour,\n\nJ\'aimerais discuter de quelques modifications à apporter à mon emploi du temps pour la semaine prochaine. Il y a un conflit avec une réunion importante.\n\nPourriez-vous me contacter pour en discuter ?\n\nCordialement,\nProf. Martin',
      timestamp: '2024-09-30 10:30',
      read: false,
      priority: 'high'
    },
    {
      id: 2,
      from: 'Admin Système',
      fromRole: 'ADMIN',
      subject: 'Maintenance planifiée',
      preview: 'Une maintenance du système est prévue ce weekend...',
      content: 'Bonjour,\n\nUne maintenance du système est prévue ce weekend du 30 septembre au 1er octobre.\n\nLe système sera indisponible de 20h00 samedi à 06h00 dimanche.\n\nMerci de planifier vos activités en conséquence.\n\nCordialement,\nÉquipe Technique',
      timestamp: '2024-09-29 15:45',
      read: true,
      priority: 'medium'
    },
    {
      id: 3,
      from: 'Jean Dupont',
      fromRole: 'STUDENT',
      subject: 'Demande de rattrapage',
      preview: 'Suite à mon absence de vendredi dernier...',
      content: 'Bonjour,\n\nSuite à mon absence de vendredi dernier due à un problème de santé, j\'aimerais savoir s\'il est possible d\'organiser une session de rattrapage pour le cours de mathématiques.\n\nJ\'ai un certificat médical à vous fournir.\n\nMerci pour votre compréhension.\n\nJean Dupont\nGroupe A - 2ème année',
      timestamp: '2024-09-28 14:20',
      read: true,
      priority: 'medium'
    },
    {
      id: 4,
      from: 'Prof. Dubois',
      fromRole: 'TEACHER',
      subject: 'Nouvelle ressource pédagogique',
      preview: 'J\'ai créé un nouveau module interactif...',
      content: 'Bonjour,\n\nJ\'ai créé un nouveau module interactif pour le cours de physique qui pourrait intéresser d\'autres enseignants.\n\nVoulez-vous que je le présente lors de la prochaine réunion pédagogique ?\n\nCordialement,\nProf. Dubois',
      timestamp: '2024-09-27 11:15',
      read: true,
      priority: 'low'
    },
    {
      id: 5,
      from: 'Marie Laurent',
      fromRole: 'STUDENT',
      subject: 'Problème d\'accès au laboratoire',
      preview: 'Je n\'arrive pas à accéder au laboratoire de chimie...',
      content: 'Bonjour,\n\nJe n\'arrive pas à accéder au laboratoire de chimie avec ma carte étudiante. Le lecteur ne semble pas reconnaître ma carte.\n\nPourriez-vous m\'aider à résoudre ce problème ?\n\nMerci,\nMarie Laurent\nGroupe C - 3ème année',
      timestamp: '2024-09-26 09:30',
      read: false,
      priority: 'high'
    }
  ]

  const filteredMessages = messages.filter(message =>
    message.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    message.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
    message.preview.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Badge variant="destructive">Urgent</Badge>
      case 'medium':
        return <Badge variant="secondary">Normal</Badge>
      case 'low':
        return <Badge variant="outline">Faible</Badge>
      default:
        return <Badge variant="secondary">Normal</Badge>
    }
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'STUDENT':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Étudiant</Badge>
      case 'TEACHER':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Enseignant</Badge>
      case 'DEPARTMENT_HEAD':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800">Chef Dept.</Badge>
      case 'ADMIN':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Admin</Badge>
      default:
        return <Badge variant="secondary">Utilisateur</Badge>
    }
  }

  const selectedMessageData = selectedMessage ? messages.find(msg => msg.id === selectedMessage) : null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Messages</h1>
          <p className="text-muted-foreground">
            Gérez vos communications avec les étudiants et enseignants
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Nouveau Message
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages Totaux</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{messages.length}</div>
            <p className="text-xs text-muted-foreground">Dans la boîte de réception</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Non Lus</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {messages.filter(msg => !msg.read).length}
            </div>
            <p className="text-xs text-muted-foreground">Nécessitent votre attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Urgents</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {messages.filter(msg => msg.priority === 'high').length}
            </div>
            <p className="text-xs text-muted-foreground">Priorité élevée</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aujourd'hui</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {messages.filter(msg => msg.timestamp.startsWith('2024-09-30')).length}
            </div>
            <p className="text-xs text-muted-foreground">Reçus aujourd'hui</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Messages List */}
        <Card>
          <CardHeader>
            <CardTitle>Boîte de Réception</CardTitle>
            <CardDescription>Vos messages récents</CardDescription>
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher dans les messages..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredMessages.map((message) => (
                <div
                  key={message.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                    selectedMessage === message.id ? 'bg-blue-50 border-blue-200' : ''
                  } ${!message.read ? 'bg-blue-50/30 border-blue-100' : ''}`}
                  onClick={() => setSelectedMessage(message.id)}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className={`text-sm truncate ${!message.read ? 'font-semibold' : 'font-medium'}`}>
                          {message.from}
                        </h4>
                        {getRoleBadge(message.fromRole)}
                        {!message.read && (
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        )}
                      </div>
                      <p className={`text-sm truncate ${!message.read ? 'font-medium' : 'text-muted-foreground'}`}>
                        {message.subject}
                      </p>
                      <p className="text-xs text-muted-foreground truncate mt-1">
                        {message.preview}
                      </p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {getPriorityBadge(message.priority)}
                      <span className="text-xs text-muted-foreground">
                        {new Date(message.timestamp).toLocaleTimeString('fr-FR', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Message Detail */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedMessageData ? 'Détail du Message' : 'Sélectionnez un Message'}
            </CardTitle>
            {selectedMessageData && (
              <div className="flex items-center justify-between">
                <CardDescription>
                  De: {selectedMessageData.from} • {new Date(selectedMessageData.timestamp).toLocaleString('fr-FR')}
                </CardDescription>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <Reply className="h-4 w-4 mr-1" />
                    Répondre
                  </Button>
                  <Button variant="outline" size="sm">
                    <Archive className="h-4 w-4 mr-1" />
                    Archiver
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4 mr-1" />
                    Supprimer
                  </Button>
                </div>
              </div>
            )}
          </CardHeader>
          <CardContent>
            {selectedMessageData ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-semibold">{selectedMessageData.subject}</h3>
                    {getPriorityBadge(selectedMessageData.priority)}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">De:</span>
                    <span className="text-sm font-medium">{selectedMessageData.from}</span>
                    {getRoleBadge(selectedMessageData.fromRole)}
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  <div className="whitespace-pre-wrap text-sm">
                    {selectedMessageData.content}
                  </div>
                </div>

                <div className="border-t pt-4 space-y-3">
                  <h4 className="font-medium">Répondre</h4>
                  <Textarea
                    placeholder="Tapez votre réponse..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    rows={4}
                  />
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setNewMessage('')}>
                      Annuler
                    </Button>
                    <Button>
                      <Send className="h-4 w-4 mr-2" />
                      Envoyer
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="mx-auto h-12 w-12 mb-4" />
                <p>Sélectionnez un message pour voir son contenu</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}