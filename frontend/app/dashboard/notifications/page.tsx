'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Bell, 
  BellOff, 
  Check, 
  CheckCheck, 
  Trash2, 
  Calendar,
  BookOpen,
  AlertCircle,
  Loader2,
  RefreshCw
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import Link from 'next/link'

interface Notification {
  id: string
  userId: string
  type: string
  title: string
  message: string
  relatedId?: string
  isRead: boolean
  createdAt: string
}

interface NotificationStats {
  total: number
  unread: number
}

export default function NotificationsPage() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [stats, setStats] = useState<NotificationStats>({ total: 0, unread: 0 })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [error, setError] = useState<string | null>(null)

  const loadNotifications = async () => {
    try {
      setLoading(true)
      setError(null)
      const [notifs, statsData] = await Promise.all([
        api.getNotifications(filter === 'unread'),
        api.getNotificationStats()
      ])
      setNotifications(notifs)
      setStats(statsData)
    } catch (err: any) {
      console.error('Error loading notifications:', err)
      setError('Erreur lors du chargement des notifications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      loadNotifications()
    }
  }, [user, filter])

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await api.markNotificationAsRead(notificationId)
      await loadNotifications()
    } catch (err) {
      console.error('Error marking notification as read:', err)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await api.markAllNotificationsAsRead()
      await loadNotifications()
    } catch (err) {
      console.error('Error marking all as read:', err)
    }
  }

  const handleDelete = async (notificationId: string) => {
    try {
      await api.deleteNotification(notificationId)
      await loadNotifications()
    } catch (err) {
      console.error('Error deleting notification:', err)
    }
  }

  const handleDeleteAll = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer toutes les notifications ?')) {
      return
    }
    try {
      await api.deleteAllNotifications()
      await loadNotifications()
    } catch (err) {
      console.error('Error deleting all notifications:', err)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'SCHEDULE_CREATED':
        return <Calendar className="h-5 w-5 text-blue-600" />
      case 'SCHEDULE_UPDATED':
        return <Calendar className="h-5 w-5 text-orange-600" />
      case 'ABSENCE_SUBMITTED':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />
      case 'ABSENCE_REVIEWED':
        return <Check className="h-5 w-5 text-green-600" />
      case 'SUBJECT_ASSIGNED':
        return <BookOpen className="h-5 w-5 text-purple-600" />
      default:
        return <Bell className="h-5 w-5 text-gray-600" />
    }
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">
            Restez informé des dernières mises à jour
          </p>
        </div>
        <Button onClick={loadNotifications} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">Toutes les notifications</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Non lues</CardTitle>
            <BellOff className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.unread}</div>
            <p className="text-xs text-muted-foreground">À traiter</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lues</CardTitle>
            <CheckCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.total - stats.unread}</div>
            <p className="text-xs text-muted-foreground">Traitées</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                Toutes ({stats.total})
              </Button>
              <Button
                variant={filter === 'unread' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('unread')}
              >
                Non lues ({stats.unread})
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              {stats.unread > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleMarkAllAsRead}
                >
                  <CheckCheck className="h-4 w-4 mr-2" />
                  Tout marquer comme lu
                </Button>
              )}
              {stats.total > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeleteAll}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Tout supprimer
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Mes notifications</CardTitle>
          <CardDescription>
            {notifications.length} notification(s) {filter === 'unread' ? 'non lue(s)' : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">
              <AlertCircle className="h-12 w-12 mx-auto mb-4" />
              <p>{error}</p>
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <BellOff className="h-12 w-12 mx-auto mb-4" />
              <p>Aucune notification</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border rounded-lg transition-colors ${
                    notification.isRead
                      ? 'bg-white'
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold text-sm">
                            {notification.title}
                          </h3>
                          {!notification.isRead && (
                            <Badge variant="default" className="text-xs">
                              Nouveau
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {notification.message}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span>
                            {formatDistanceToNow(new Date(notification.createdAt), {
                              addSuffix: true,
                              locale: fr
                            })}
                          </span>
                          {notification.relatedId && (
                            <Link 
                              href={`/dashboard/schedules/${notification.relatedId}`}
                              className="text-blue-600 hover:underline"
                              onClick={() => handleMarkAsRead(notification.id)}
                            >
                              Voir détails 
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {!notification.isRead && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleMarkAsRead(notification.id)}
                          title="Marquer comme lu"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(notification.id)}
                        className="text-red-600 hover:text-red-700"
                        title="Supprimer"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
