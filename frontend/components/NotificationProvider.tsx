'use client';

import dynamic from 'next/dynamic';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect, useState } from 'react';

// Dynamically import NotificationAPI components to prevent SSR issues
const NotificationAPIProvider = dynamic(
  () => import('@notificationapi/react').then((mod) => mod.NotificationAPIProvider),
  {
    ssr: false,
    loading: () => null
  }
);

const NotificationPopup = dynamic(
  () => import('@notificationapi/react').then((mod) => mod.NotificationPopup),
  {
    ssr: false,
    loading: () => null
  }
);

interface NotificationProviderProps {
  children: React.ReactNode;
}

export default function NotificationProvider({ children }: NotificationProviderProps) {
  const [isClient, setIsClient] = useState(false);
  
  // Use try-catch to handle auth context issues during initial render
  let user = null;
  let loading = true;
  
  try {
    const authContext = useAuth();
    user = authContext.user;
    loading = authContext.loading;
  } catch (error) {
    // Auth context not available yet, will retry after mount
    console.log('NotificationProvider: Auth context not available yet');
  }

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Don't render NotificationAPI provider on server or when user is not loaded
  if (!isClient || loading || !user) {
    return <>{children}</>;
  }

  // Use the user's email as the userId for NotificationAPI
  const userId = user.email || 'anonymous';

  return (
    <NotificationAPIProvider
      userId={userId}
      clientId="m9dp6o7vnr5t3uf2daxase81zj"
    >
      {children}
      <NotificationPopup
        buttonStyles={{
          width: 40,
          height: 40,
          backgroundColor: '#1890ff'
        }}
        popoverPosition={{
          anchorOrigin: {
            vertical: 'bottom',
            horizontal: 'center'
          }
        }}
        iconColor="#ffffff"
        buttonIconSize={20}
        popupWidth={400}
        popupHeight={500}
      />
    </NotificationAPIProvider>
  );
}