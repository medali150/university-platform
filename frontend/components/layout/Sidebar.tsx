'use client'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useAuth } from '@/hooks/useAuth'
import { Role } from '@/types/auth'
import { 
  Home, 
  Calendar, 
  MessageSquare, 
  UserX, 
  BookOpen, 
  Users, 
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Building,
  Newspaper,
  GraduationCap
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

interface SidebarProps {
  className?: string
}

const studentNavItems = [
  { href: '/dashboard/student', label: 'Dashboard', icon: Home },
  { href: '/classroom/courses', label: 'Smart Classroom', icon: GraduationCap },
  { href: '/dashboard/student/timetable', label: 'Timetable', icon: Calendar },
  { href: '/dashboard/events', label: 'Événements', icon: Newspaper },
  { href: '/dashboard/student/profile', label: 'Mon Profil', icon: Users },
  { href: '/dashboard/messages', label: 'Messages', icon: MessageSquare },
  { href: '/dashboard/absences', label: 'Absences', icon: UserX },
]

const teacherNavItems = [
  { href: '/dashboard/teacher', label: 'Dashboard', icon: Home },
  { href: '/classroom/courses', label: 'Smart Classroom', icon: GraduationCap },
  { href: '/dashboard/teacher/profile', label: 'Mon Profil', icon: Users },
  { href: '/dashboard/teacher/timetable', label: 'Timetable', icon: Calendar },
  { href: '/dashboard/messages', label: 'Messages', icon: MessageSquare },
  { href: '/dashboard/absences', label: 'Absences', icon: UserX },
  { href: '/dashboard/makeups', label: 'Make-up Sessions', icon: BookOpen },
]

const departmentHeadNavItems = [
  { href: '/dashboard/department-head', label: 'Dashboard', icon: Home },
  { href: '/classroom/courses', label: 'Smart Classroom', icon: GraduationCap },
  { href: '/dashboard/department-head/department-schedule', label: 'Emplois du Temps Département', icon: Calendar },
  { href: '/dashboard/department-head/timetable', label: 'Mon Emploi du Temps', icon: Calendar },
  { href: '/dashboard/department-head/classes', label: 'Classes', icon: Users },
  { href: '/dashboard/department-head/analytics', label: 'Statistiques', icon: BarChart3 },
  { href: '/dashboard/department-head/rooms', label: 'Gestion des Salles', icon: Building },
  { href: '/dashboard/department-head/room-occupancy', label: 'Occupation des Salles', icon: Building },
  { href: '/dashboard/messages', label: 'Messages', icon: MessageSquare },
  { href: '/dashboard/absences', label: 'Absences', icon: UserX },
]

export function Sidebar({ className }: SidebarProps) {
  const { user } = useAuth()
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  const getNavItems = () => {
    if (!user) return []
    
    switch (user.role) {
      case 'STUDENT':
        return studentNavItems
      case 'TEACHER':
        return teacherNavItems
      case 'DEPARTMENT_HEAD':
        return departmentHeadNavItems
      default:
        return []
    }
  }

  const navItems = getNavItems()

  return (
    <div
      className={cn(
        'relative flex flex-col border-r bg-background transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">U</span>
            </div>
            <span className="font-semibold">University</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </Button>
      </div>
      
      <ScrollArea className="flex-1">
        <nav className="p-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn(
                    'w-full justify-start h-10',
                    collapsed && 'px-2 justify-center'
                  )}
                >
                  <Icon size={18} />
                  {!collapsed && <span className="ml-3">{item.label}</span>}
                </Button>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>
    </div>
  )
}