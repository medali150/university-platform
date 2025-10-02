'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';

export default function AdminHomePage() {
  const { admin, loading } = useAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (admin) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [admin, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-900 to-red-600">
      <div className="text-white text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-white mx-auto mb-4"></div>
        <h1 className="text-2xl font-bold mb-2">🔒 Admin Panel</h1>
        <p>Initializing secure access...</p>
      </div>
    </div>
  );
}