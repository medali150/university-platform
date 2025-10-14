'use client';

import { Button } from './ui/button';
import { Bell } from 'lucide-react';
import { toast } from 'sonner';

interface NotificationTesterProps {
  userId?: string;
  title?: string;
  message?: string;
}

export default function NotificationTester({ 
  userId, 
  title = "Test Notification", 
  message = "This is a test notification from your university system" 
}: NotificationTesterProps) {

  const sendTestNotification = async () => {
    try {
      // For now, just show a toast since the NotificationAPI integration
      // will be handled by the backend service
      toast.success(`Notification de test: ${title}`);
      toast.info(message);
    } catch (error) {
      console.error('Error sending test notification:', error);
      toast.error('Erreur lors de l\'envoi de la notification');
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <Button
        variant="outline"
        size="sm"
        onClick={sendTestNotification}
        className="flex items-center space-x-2"
      >
        <Bell className="h-4 w-4" />
        <span>Test Notification</span>
      </Button>
    </div>
  );
}