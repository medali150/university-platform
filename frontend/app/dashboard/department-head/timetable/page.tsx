'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import ScheduleCreator from '@/components/department-head/schedule-creator'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function DepartmentHeadTimetablePage() {
  const { isLoading } = useRequireRole('DEPARTMENT_HEAD')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <Link href="/dashboard/department-head">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour au tableau de bord
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Gestion de l'Emploi du Temps</h1>
        <p className="text-gray-600 mt-2">
          Créez et gérez les emplois du temps de manière interactive
        </p>
      </div>

      <ScheduleCreator />
    </div>
  )
}
