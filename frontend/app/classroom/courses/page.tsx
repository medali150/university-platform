'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi, Course } from '@/lib/classroom-api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { PlusCircle, BookOpen, Users, Archive, Grid3x3, List, LogIn, ArrowLeft } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/20 to-blue-50/30">
      {/* Modern Header with Glassmorphism */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl shadow-lg">
                <BookOpen className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-purple-900 to-blue-900 bg-clip-text text-transparent">
                  Mes Cours
                </h1>
                <p className="text-sm text-gray-600 mt-1 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  {isTeacher
                    ? 'Gérez vos cours et devoirs'
                    : 'Afficher vos cours inscrits'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* AI Assistant Button */}
              <Button
                variant="outline"
                className="bg-gradient-to-r from-purple-500 to-blue-600 text-white border-0 hover:from-purple-600 hover:to-blue-700 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                onClick={() => router.push('/classroom/ai-assistant')}
              >
                <span className="mr-2">✨</span>
                Assistant IA
              </Button>
              
              {/* View Mode Toggle */}
              <div className="flex gap-1 bg-gray-100 rounded-xl p-1 shadow-inner">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className={viewMode === 'grid' ? 'bg-white shadow-md' : 'hover:bg-white/50'}
                >
                  <Grid3x3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className={viewMode === 'list' ? 'bg-white shadow-md' : 'hover:bg-white/50'}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>

              {/* Archive Toggle */}
              <Button
                variant="outline"
                onClick={() => setShowArchived(!showArchived)}
                className="border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all"
              >
                <Archive className="h-4 w-4 mr-2" />
                {showArchived ? 'Actif' : 'Archivé'}
              </Button>

              {/* Create Course Button (Teachers Only) */}
              {isTeacher && (
                <Button 
                  onClick={handleCreateCourse}
                  className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  <PlusCircle className="h-4 w-4 mr-2" />
                  Créer un cours
                </Button>
              )}

              {/* Join Course Button (Students Only) */}
              {isStudent && (
                <Button 
                  onClick={() => setShowEnrollDialog(true)}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Rejoindre un cours
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">

        {/* Courses Grid/List */}
        {courses.length === 0 ? (
          <Card className="p-16 text-center bg-white/80 backdrop-blur-sm border-2 border-dashed border-gray-300 hover:border-purple-300 transition-all">
            <div className="max-w-md mx-auto">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <BookOpen className="h-12 w-12 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Pas encore de cours
              </h3>
              <p className="text-gray-600 mb-6">
                {isTeacher
                  ? 'Créez votre premier cours pour commencer à enseigner'
                  : 'Inscrivez-vous à un cours à l\'aide d\'un code d\'invitation'}
              </p>
              <div className="flex gap-4 justify-center">
                {isTeacher && (
                  <Button 
                    onClick={handleCreateCourse}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-xl transition-all px-8"
                    size="lg"
                  >
                    <PlusCircle className="h-5 w-5 mr-2" />
                    Créer un cours
                  </Button>
                )}
                {isStudent && (
                  <Button 
                    onClick={() => setShowEnrollDialog(true)} 
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all px-8"
                    size="lg"
                  >
                    <LogIn className="h-5 w-5 mr-2" />
                    Rejoindre un cours
                  </Button>
                )}
              </div>
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
            {courses.map((course, index) => (
              <Card
                key={course.id}
                className="group cursor-pointer hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-white/90 backdrop-blur-sm border-0 overflow-hidden"
                onClick={() => handleCourseClick(course.id)}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {/* Gradient Header with Pattern */}
                <CardHeader
                  className="relative pb-16 pt-8 overflow-hidden"
                  style={{
                    background: `linear-gradient(135deg, ${getRandomColor(course.id)} 0%, ${getRandomColor(course.id)}DD 100%)`,
                  }}
                >
                  {/* Decorative circles */}
                  <div className="absolute -top-8 -right-8 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
                  <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
                  
                  <div className="relative z-10">
                    <CardTitle className="text-white text-xl mb-2 group-hover:scale-105 transition-transform">
                      {course.nom}
                    </CardTitle>
                    <CardDescription className="text-white/90 font-medium">
                      {course.anneeAcademique} • {course.semestre}
                      {course.code && ` • ${course.code}`}
                    </CardDescription>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-6 pb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700">
                        <Users className="h-4 w-4" />
                        <span className="text-sm font-semibold">{course.nbEtudiants || 0}</span>
                      </div>
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700">
                        <BookOpen className="h-4 w-4" />
                        <span className="text-sm font-semibold">{course.nbDevoirs || 0}</span>
                      </div>
                    </div>
                    {!course.estActif && (
                      <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                        Archivé
                      </span>
                    )}
                  </div>
                  {course.description && (
                    <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                      {course.description}
                    </p>
                  )}
                  
                  {/* Hover indicator */}
                  <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs text-purple-600 font-medium flex items-center gap-1">
                      Voir le cours
                      <ArrowLeft className="h-3 w-3 rotate-180" />
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Enroll Dialog - Modern Design */}
      <Dialog open={showEnrollDialog} onOpenChange={setShowEnrollDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Rejoindre un cours
            </DialogTitle>
            <DialogDescription className="text-base">
              Entrez le code d'invitation fourni par votre enseignant
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-6">
            <div className="relative">
              <Input
                placeholder="ABC123"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                maxLength={6}
                className="text-center text-2xl font-mono tracking-[0.5em] h-16 border-2 focus:border-blue-500 focus:ring-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50"
              />
            </div>
            <p className="text-sm text-gray-500 text-center flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              Le code est sensible à la casse et contient 6 caractères
            </p>
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={() => {
                setShowEnrollDialog(false);
                setInviteCode('');
              }}
              disabled={enrollLoading}
              className="border-gray-300 hover:bg-gray-50"
            >
              Annuler
            </Button>
            <Button 
              onClick={handleEnrollWithCode} 
              disabled={enrollLoading || !inviteCode || inviteCode.length < 6}
              className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all"
            >
              {enrollLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Inscription...
                </>
              ) : (
                <>
                  <LogIn className="h-4 w-4 mr-2" />
                  Rejoindre
                </>
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
