'use client';

import { useState, useEffect } from 'react';
import { Bell, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';

interface AbsenceNotification {
  id: string;
  type: 'absence_marked' | 'justification_reviewed' | 'teacher_justification' | 'high_absences' | 'parent_alert' | 'daily_summary';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  data?: {
    absence_id?: string;
    student_name?: string;
    teacher_name?: string;
    subject_name?: string;
    absence_date?: string;
    decision?: 'approved' | 'rejected';
    absence_count?: number;
  };
}

export default function AbsenceNotifications() {
  const [notifications, setNotifications] = useState<AbsenceNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showAll, setShowAll] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      if (typeof window === 'undefined') return;
      
      const token = localStorage.getItem('authToken');
      if (!token) return;
      
      const response = await fetch('/api/notifications/absence', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.notifications?.filter((n: AbsenceNotification) => !n.read).length || 0);
      }
    } catch (error) {
      console.error('Error fetching absence notifications:', error);
      // Set mock data for demonstration
      setNotifications([
        {
          id: '1',
          type: 'absence_marked',
          title: 'Absence Marked',
          message: 'You have been marked absent for Mathematics on 2024-01-15',
          timestamp: '2024-01-15T10:30:00Z',
          read: false,
          data: {
            absence_id: 'abs_1',
            teacher_name: 'Prof. Smith',
            subject_name: 'Mathematics',
            absence_date: '2024-01-15'
          }
        },
        {
          id: '2',
          type: 'justification_reviewed',
          title: 'Justification Approved',
          message: 'Your absence justification for Physics has been approved',
          timestamp: '2024-01-14T15:45:00Z',
          read: false,
          data: {
            absence_id: 'abs_2',
            subject_name: 'Physics',
            absence_date: '2024-01-14',
            decision: 'approved'
          }
        }
      ]);
      setUnreadCount(2);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      if (typeof window === 'undefined') return;
      
      const token = localStorage.getItem('authToken');
      if (!token) return;
      
      await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'absence_marked':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'justification_reviewed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'teacher_justification':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'high_absences':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'parent_alert':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'daily_summary':
        return <Bell className="h-4 w-4 text-gray-500" />;
      default:
        return <Bell className="h-4 w-4 text-gray-500" />;
    }
  };

  const getNotificationBadgeColor = (type: string) => {
    switch (type) {
      case 'absence_marked':
        return 'destructive';
      case 'justification_reviewed':
        return 'default';
      case 'teacher_justification':
        return 'secondary';
      case 'high_absences':
        return 'destructive';
      case 'parent_alert':
        return 'destructive';
      case 'daily_summary':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const displayNotifications = showAll ? notifications : notifications.slice(0, 5);

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Absence Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">Loading notifications...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Absence Notifications
            {unreadCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {unreadCount}
              </Badge>
            )}
          </div>
          {notifications.length > 5 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? 'Show Less' : `Show All (${notifications.length})`}
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No absence notifications</p>
          </div>
        ) : (
          <div className="space-y-4">
            {displayNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 rounded-lg border transition-colors ${
                  notification.read 
                    ? 'bg-gray-50 border-gray-200' 
                    : 'bg-white border-blue-200 shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className={`font-medium ${
                          notification.read ? 'text-gray-700' : 'text-gray-900'
                        }`}>
                          {notification.title}
                        </h4>
                        <Badge 
                          variant={getNotificationBadgeColor(notification.type)}
                          className="text-xs"
                        >
                          {notification.type.replace('_', ' ')}
                        </Badge>
                      </div>
                      <p className={`text-sm ${
                        notification.read ? 'text-gray-500' : 'text-gray-700'
                      }`}>
                        {notification.message}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span>{formatTimestamp(notification.timestamp)}</span>
                        {notification.data?.subject_name && (
                          <span>• {notification.data.subject_name}</span>
                        )}
                        {notification.data?.absence_date && (
                          <span>• {notification.data.absence_date}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {!notification.read && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => markAsRead(notification.id)}
                      className="text-xs"
                    >
                      Mark Read
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}