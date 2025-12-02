'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi, Course } from '@/lib/classroom-api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { PlusCircle, BookOpen, Users, Archive, Grid3x3, List, LogIn, Search, Zap, Loader2 } from 'lucide-react';

export default function CoursesPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showArchived, setShowArchived] = useState(false);
  const [showEnrollDialog, setShowEnrollDialog] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [enrollLoading, setEnrollLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!authLoading) {
      loadCourses();
    }
  }, [showArchived, authLoading]);

  // Filter courses based on search query
  useEffect(() => {
    const filtered = courses.filter(course =>
      course.nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.code?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredCourses(filtered);
  }, [courses, searchQuery]);

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
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-white/60">Chargement de vos cours...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Modern Gradient Header */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 sm:p-8 md:p-10 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-2">
            Mes cours 📚
          </h1>
          <p className="text-indigo-100 text-base sm:text-lg">
            {isTeacher
              ? 'Gérez vos cours, devoirs et suivez vos étudiants'
              : 'Afficher vos cours inscrits et progressez'}
          </p>
        </div>
      </div>

      {/* Search and Controls Bar */}
      <div className="space-y-4 sm:space-y-0 sm:flex sm:items-center sm:justify-between gap-4">
        {/* Search Input */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Rechercher un cours..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-10 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>

        {/* Control Buttons */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          {/* AI Assistant Button */}
          <Button
            size="sm"
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-0"
            onClick={() => router.push('/classroom/ai-assistant')}
          >
            <Zap className="h-4 w-4 mr-1.5" />
            <span className="hidden sm:inline">IA</span>
          </Button>

          {/* View Mode Toggle */}
          <div className="flex gap-1 border border-gray-200 rounded-lg p-1 bg-white">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="h-8 px-2"
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="h-8 px-2"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Archive Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowArchived(!showArchived)}
            className="border-gray-200"
          >
            <Archive className="h-4 w-4 mr-1.5" />
            <span className="hidden sm:inline">{showArchived ? 'Actifs' : 'Archives'}</span>
          </Button>

          {/* Create/Join Course Buttons */}
          {isTeacher && (
            <Button
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
              onClick={handleCreateCourse}
            >
              <PlusCircle className="h-4 w-4 mr-1.5" />
              <span className="hidden sm:inline">Créer</span>
            </Button>
          )}

          {isStudent && (
            <Button
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white"
              onClick={() => setShowEnrollDialog(true)}
            >
              <LogIn className="h-4 w-4 mr-1.5" />
              <span className="hidden sm:inline">Rejoindre</span>
            </Button>
          )}
        </div>
      </div>

      {/* Courses Grid/List */}
      {filteredCourses.length === 0 ? (
        <Card className="p-12 text-center border-0 shadow-lg bg-gradient-to-br from-slate-50 to-slate-100">
          <div className="flex flex-col items-center gap-4">
            <div className="p-3 rounded-full bg-indigo-100">
              <BookOpen className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">Pas encore de cours</h3>
            <p className="text-gray-600 max-w-md">
              {searchQuery
                ? "Aucun cours ne correspond à votre recherche"
                : isTeacher
                ? 'Créez votre premier cours pour commencer'
                : 'Inscrivez-vous à un cours à l\'aide d\'un code d\'invitation'}
            </p>
            {!searchQuery && (
              <div className="flex flex-col sm:flex-row gap-3 mt-4">
                {isTeacher && (
                  <Button onClick={handleCreateCourse} className="bg-indigo-600 hover:bg-indigo-700">
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
            )}
          </div>
        </Card>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'flex flex-col gap-4'
          }
        >
          {filteredCourses.map((course) => (
            <Card
              key={course.id}
              className="group cursor-pointer border-0 shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden hover:-translate-y-1"
              onClick={() => handleCourseClick(course.id)}
            >
              <CardHeader
                className="pb-4 text-white relative overflow-hidden"
                style={{
                  background: `linear-gradient(135deg, ${getRandomColor(course.id)} 0%, ${getRandomColor(course.id)}CC 100%)`,
                }}
              >
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-white rounded-full blur-xl"></div>
                </div>
                <div className="relative z-10">
                  <CardTitle className="text-lg sm:text-xl group-hover:translate-x-1 transition-transform">
                    {course.nom}
                  </CardTitle>
                  <CardDescription className="text-white/80 text-xs sm:text-sm">
                    {course.anneeAcademique} • {course.semestre}
                    {course.code && ` • ${course.code}`}
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5 text-gray-600">
                        <Users className="h-4 w-4" />
                        <span className="font-medium">{course.nbEtudiants || 0} élèves</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-gray-600">
                        <BookOpen className="h-4 w-4" />
                        <span className="font-medium">{course.nbDevoirs || 0} travaux</span>
                      </div>
                    </div>
                    {!course.estActif && (
                      <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                        Archivé
                      </span>
                    )}
                  </div>
                  {course.description && (
                    <p className="text-sm text-gray-600 line-clamp-2 pt-2 border-t border-gray-100">
                      {course.description}
                    </p>
                  )}
                </div>
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
