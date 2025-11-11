'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi, Course } from '@/lib/classroom-api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { PlusCircle, BookOpen, Users, Archive, Grid3x3, List, LogIn } from 'lucide-react';

export default function CoursesPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showArchived, setShowArchived] = useState(false);
  const [showEnrollDialog, setShowEnrollDialog] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [enrollLoading, setEnrollLoading] = useState(false);

  useEffect(() => {
    if (!authLoading) {
      loadCourses();
    }
  }, [showArchived, authLoading]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const data = await classroomApi.getCourses(showArchived);
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = () => {
    router.push('/classroom/courses/new');
  };

  const handleCourseClick = (courseId: string) => {
    router.push(`/classroom/courses/${courseId}`);
  };

  const handleEnrollWithCode = async () => {
    if (!inviteCode.trim()) {
      alert('Veuillez entrer un code d\'invitation');
      return;
    }

    try {
      setEnrollLoading(true);
      
      // Find course by invite code using the new endpoint
      const course = await classroomApi.findCourseByInviteCode(inviteCode.trim());
      
      // Enroll in the course
      await classroomApi.enrollInCourse(course.id, inviteCode.toUpperCase());
      
      alert(`✅ Vous êtes maintenant inscrit au cours "${course.nom}"!`);
      setShowEnrollDialog(false);
      setInviteCode('');
      loadCourses();
      
    } catch (error: any) {
      console.error('Enrollment error:', error);
      if (error.message.includes('404')) {
        alert('❌ Code d\'invitation invalide');
      } else if (error.message.includes('403')) {
        alert('❌ Vous n\'avez pas la permission de rejoindre ce cours');
      } else {
        alert(`❌ Erreur: ${error.message}`);
      }
    } finally {
      setEnrollLoading(false);
    }
  };

  const isTeacher = user?.role === 'TEACHER';
  const isStudent = user?.role === 'STUDENT';

  // Redirect to login if not authenticated
  if (!authLoading && !isAuthenticated) {
    router.push('/login');
    return null;
  }

  if (loading || authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Mes cours</h1>
          <p className="text-muted-foreground mt-2">
            {isTeacher
              ? 'Gérez vos cours et devoirs'
              : 'Afficher vos cours inscrits'}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* AI Assistant Button */}
          <Button
            variant="outline"
            className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 hover:from-purple-100 hover:to-blue-100"
            onClick={() => router.push('/classroom/ai-assistant')}
          >
            <span className="text-purple-600 mr-2">✨</span>
            Assistant IA
          </Button>
          {/* View Mode Toggle */}
          <div className="flex gap-2 border rounded-lg p-1">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Archive Toggle */}
          <Button
            variant="outline"
            onClick={() => setShowArchived(!showArchived)}
          >
            <Archive className="h-4 w-4 mr-2" />
            {showArchived ? 'Show Active' : 'Show Archived'}
          </Button>

          {/* Create Course Button (Teachers Only) */}
          {isTeacher && (
            <Button onClick={handleCreateCourse}>
              <PlusCircle className="h-4 w-4 mr-2" />
              Créer un cours
            </Button>
          )}

          {/* Join Course Button (Students Only) */}
          {isStudent && (
            <Button onClick={() => setShowEnrollDialog(true)}>
              <LogIn className="h-4 w-4 mr-2" />
              Rejoindre un cours
            </Button>
          )}
        </div>
      </div>

      {/* Courses Grid/List */}
      {courses.length === 0 ? (
        <Card className="p-12 text-center">
          <BookOpen className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold mb-2">Pas encore de cours</h3>
          <p className="text-muted-foreground mb-4">
            {isTeacher
              ? 'Créez votre premier cours pour commencer'
              : 'S\'inscrire à un cours à l\'aide d\'un code d\'invitation'}
          </p>
          <div className="flex gap-4 justify-center">
            {isTeacher && (
              <Button onClick={handleCreateCourse}>
                <PlusCircle className="h-4 w-4 mr-2" />
                Créer un cours
              </Button>
            )}
            {isStudent && (
              <Button onClick={() => setShowEnrollDialog(true)} variant="outline">
                <LogIn className="h-4 w-4 mr-2" />
                Rejoindre un cours
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'flex flex-col gap-4'
          }
        >
          {courses.map((course) => (
            <Card
              key={course.id}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => handleCourseClick(course.id)}
            >
              <CardHeader
                className="bg-gradient-to-r from-primary/10 to-primary/5"
                style={{
                  background: `linear-gradient(135deg, ${getRandomColor(course.id)} 0%, ${getRandomColor(course.id)}CC 100%)`,
                }}
              >
                <CardTitle className="text-white">{course.nom}</CardTitle>
                <CardDescription className="text-white/90">
                  {course.anneeAcademique} • {course.semestre}
                  {course.code && ` • ${course.code}`}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      <span>{course.nbEtudiants || 0}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <BookOpen className="h-4 w-4" />
                      <span>{course.nbDevoirs || 0}</span>
                    </div>
                  </div>
                  {!course.estActif && (
                    <span className="px-2 py-1 rounded-full bg-muted text-xs">
                      Archivé
                    </span>
                  )}
                </div>
                {course.description && (
                  <p className="mt-3 text-sm line-clamp-2">
                    {course.description}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Enroll Dialog */}
      <Dialog open={showEnrollDialog} onOpenChange={setShowEnrollDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rejoindre un cours</DialogTitle>
            <DialogDescription>
              Entrez le code d'invitation fourni par votre enseignant
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Input
              placeholder="Code d'invitation (ex: ABC123)"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              maxLength={6}
              className="text-center text-lg font-mono tracking-wider"
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowEnrollDialog(false);
                setInviteCode('');
              }}
              disabled={enrollLoading}
            >
              Annuler
            </Button>
            <Button onClick={handleEnrollWithCode} disabled={enrollLoading || !inviteCode}>
              {enrollLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Inscription...
                </>
              ) : (
                'Rejoindre'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Helper function to generate consistent colors for courses
function getRandomColor(seed: string): string {
  const colors = [
    '#6366f1', // Indigo
    '#8b5cf6', // Violet
    '#ec4899', // Pink
    '#f43f5e', // Rose
    '#f97316', // Orange
    '#eab308', // Yellow
    '#22c55e', // Green
    '#14b8a6', // Teal
    '#06b6d4', // Cyan
    '#0ea5e9', // Sky
  ];
  
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}
