'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import StudentAbsenceManagement from '@/components/student/StudentAbsenceManagement'

export default function StudentAbsencePage() {
  const { user, isLoading } = useRequireRole('STUDENT' as Role)

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  return <StudentAbsenceManagement />
}