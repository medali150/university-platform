'use client';

interface NotificationProviderProps {
  children: React.ReactNode;
}

// Temporarily disabled NotificationAPI to fix chunk loading error
// TODO: Re-enable after fixing the chunk loading issue
export default function NotificationProvider({ children }: NotificationProviderProps) {
  return <>{children}</>;
}