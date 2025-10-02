import { ReactNode } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Calendar, User, BookOpen } from 'lucide-react';

interface TeacherLayoutProps {
  children: ReactNode;
}

export default function TeacherLayout({ children }: TeacherLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/teacher" className="text-xl font-bold text-primary">
                Espace Enseignant
              </Link>
              
              <div className="flex items-center gap-4">
                <Link href="/teacher/absence">
                  <Button variant="ghost" className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Absences
                  </Button>
                </Link>
                
                <Link href="/teacher/profile">
                  <Button variant="ghost" className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Profil
                  </Button>
                </Link>
                
                <Link href="/teacher/schedule">
                  <Button variant="ghost" className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Planning
                  </Button>
                </Link>
                
                <Link href="/teacher/subjects">
                  <Button variant="ghost" className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Matières
                  </Button>
                </Link>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="outline">
                  Tableau de bord
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-6">
        {children}
      </main>
    </div>
  );
}