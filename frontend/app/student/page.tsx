'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function StudentPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to student dashboard
    router.replace('/student/dashboard');
  }, [router]);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  );
}