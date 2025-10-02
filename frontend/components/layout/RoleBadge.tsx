import { Role } from '@/types/auth'
import { Badge } from '@/components/ui/badge'

interface RoleBadgeProps {
  role: Role
}

const roleConfig = {
  'STUDENT': {
    label: 'Étudiant',
    variant: 'secondary' as const,
  },
  'TEACHER': {
    label: 'Enseignant',
    variant: 'default' as const,
  },
  'DEPARTMENT_HEAD': {
    label: 'Chef de Département',
    variant: 'destructive' as const,
  },
  'ADMIN': {
    label: 'Administrateur',
    variant: 'outline' as const,
  },
} as const

export function RoleBadge({ role }: RoleBadgeProps) {
  const config = roleConfig[role]
  
  if (!config) return null

  return (
    <Badge variant={config.variant}>
      {config.label}
    </Badge>
  )
}