'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdmin } from '@/hooks/useAdmin';

export default function AdminPage() {
  const { isAdmin, loading } = useAdmin();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (isAdmin) {
        router.push('/admin/dashboard');
      } else {
        router.push('/admin/login');
      }
    }
  }, [isAdmin, loading, router]);

  return (
    <div className="container">
      <div className="welcome">
        <h1>Redirection...</h1>
      </div>
    </div>
  );
}