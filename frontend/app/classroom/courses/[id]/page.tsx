'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi, Course, Announcement, Assignment } from '@/lib/classroom-api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Users, 
  Settings, 
  Megaphone, 
  BookOpen, 
  FolderOpen,
  MessageSquare,
  Plus,
  Calendar,
  Clock
} from 'lucide-react';

interface CourseHomeProps {
  params: {
    id: string;
  };
}

export default function CourseHomePage({ params }: CourseHomeProps) {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      loadCourseData();
    }
  }, [params.id, authLoading]);

  const loadCourseData = async () => {
    try {
      setLoading(true);
      const [courseData, announcementsData, assignmentsData] = await Promise.all([
        classroomApi.getCourse(params.id),
        classroomApi.getAnnouncements(params.id),
        classroomApi.getAssignments(params.id),
      ]);

      setCourse(courseData);
      setAnnouncements(announcementsData);
      setAssignments(assignmentsData);
    } catch (error) {
      console.error('Failed to load course data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Check if user is teacher
  const isTeacher = user?.role === 'TEACHER';
  
  // Debug logging
  useEffect(() => {
    if (user && course) {
      console.log('🔍 Teacher Check:', {
        userRole: user.role,
        userEnseignantId: user.enseignant_id,
        courseTeacherId: course.id_enseignant,
        isTeacherRole: user.role === 'TEACHER',
        SHOW_BUTTONS: user.role === 'TEACHER' ? 'YES ✅' : 'NO ❌'
      });
    }
  }, [user, course]);

  // Show loading while auth is loading
  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!isAuthenticated || !user) {
    router.push('/login');
    return null;
  }

  if (!course) {
    return <div>Course not found</div>;
  }

  const upcomingAssignments = assignments
    .filter((a) => a.dueDate && new Date(a.dueDate) > new Date())
    .sort((a, b) => new Date(a.dueDate!).getTime() - new Date(b.dueDate!).getTime())
    .slice(0, 3);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Header */}
      <div 
        className="bg-gradient-to-r from-primary to-primary/80 text-white"
        style={{
          background: `linear-gradient(135deg, ${getRandomColor(course.id)} 0%, ${getRandomColor(course.id)}CC 100%)`,
        }}
      >
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-white/20"
                onClick={() => router.push('/classroom/courses')}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold">{course.nom}</h1>
                <p className="text-white/90 mt-2">
                  {course.anneeAcademique} • {course.semestre}
                  {course.code && ` • ${course.code}`}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="ghost"
                className="text-white hover:bg-white/20 bg-white/10"
                onClick={() => router.push('/classroom/ai-assistant')}
              >
                <span className="mr-2">✨</span>
                Assistant IA
              </Button>
              <Button
                variant="ghost"
                className="text-white hover:bg-white/20"
                onClick={() => router.push(`/classroom/courses/${params.id}/people`)}
              >
                <Users className="h-4 w-4 mr-2" />
                Personnes
              </Button>
              {isTeacher && (
                <Button
                  variant="ghost"
                  className="text-white hover:bg-white/20"
                  onClick={() => router.push(`/classroom/courses/${params.id}/settings`)}
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Paramètres
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4">
          <Tabs defaultValue="stream" className="w-full">
            <TabsList className="w-full justify-start border-0 bg-transparent">
              <TabsTrigger value="stream">Stream</TabsTrigger>
              <TabsTrigger value="assignments">Assignments</TabsTrigger>
              <TabsTrigger value="materials">Materials</TabsTrigger>
              <TabsTrigger value="discussions">Discussions</TabsTrigger>
            </TabsList>

            <TabsContent value="stream">
              <StreamView
                course={course}
                announcements={announcements}
                upcomingAssignments={upcomingAssignments}
                isTeacher={isTeacher}
                currentUser={user}
                onRefresh={loadCourseData}
              />
            </TabsContent>

            <TabsContent value="assignments">
              <AssignmentsView courseId={params.id} isTeacher={isTeacher} />
            </TabsContent>

            <TabsContent value="materials">
              <MaterialsView courseId={params.id} isTeacher={isTeacher} />
            </TabsContent>

            <TabsContent value="discussions">
              <DiscussionsView courseId={params.id} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

// Stream View Component  
function StreamView({ course, announcements, upcomingAssignments, isTeacher, onRefresh, currentUser }: any) {
  const [showAnnounceDialog, setShowAnnounceDialog] = useState(false);
  const [announcementContent, setAnnouncementContent] = useState('');
  const [isPinned, setIsPinned] = useState(false);
  const [allowComments, setAllowComments] = useState(true);
  const [creating, setCreating] = useState(false);

  const handleCreateAnnouncement = async () => {
    if (!announcementContent.trim()) return;
    
    try {
      setCreating(true);
      await classroomApi.createAnnouncement(course.id, {
        content: announcementContent,
        isPinned,
        allowComments
      });
      setAnnouncementContent('');
      setIsPinned(false);
      setAllowComments(true);
      setShowAnnounceDialog(false);
      onRefresh();
    } catch (error) {
      console.error('Failed to create announcement:', error);
      alert('Échec de la création de l\'annonce');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Content */}
      <div className="lg:col-span-2 space-y-6">
        {/* DEBUG INFO - TOUJOURS VISIBLE */}
        <Card className="bg-yellow-50 border-yellow-300">
          <CardContent className="pt-4">
            <p className="text-sm font-bold">🔍 DEBUG INFO:</p>
            <p className="text-xs">Rôle utilisateur: <strong>{user?.role || 'NON DÉFINI'}</strong></p>
            <p className="text-xs">isTeacher: <strong>{isTeacher ? 'OUI ✅' : 'NON ❌'}</strong></p>
            <p className="text-xs">Boutons visibles: <strong>{isTeacher ? 'OUI ✅' : 'NON ❌'}</strong></p>
          </CardContent>
        </Card>

        {/* Quick Actions (Teacher) */}
        {isTeacher && (
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-3 gap-4">
                <Button 
                  variant="outline" 
                  className="h-auto flex-col py-4"
                  onClick={() => setShowAnnounceDialog(true)}
                >
                  <Megaphone className="h-6 w-6 mb-2" />
                  <span>Annoncer</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-auto flex-col py-4"
                  onClick={() => {
                    // Switch to Assignments tab
                    const assignmentsTab = document.querySelector('[value="assignments"]');
                    if (assignmentsTab) (assignmentsTab as HTMLElement).click();
                  }}
                >
                  <BookOpen className="h-6 w-6 mb-2" />
                  <span>Devoir</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-auto flex-col py-4"
                  onClick={() => {
                    // Switch to Materials tab
                    const materialsTab = document.querySelector('[value="materials"]');
                    if (materialsTab) (materialsTab as HTMLElement).click();
                  }}
                >
                  <FolderOpen className="h-6 w-6 mb-2" />
                  <span>Matériel</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Create Announcement Dialog */}
        {showAnnounceDialog && (
          <Card className="border-2 border-primary">
            <CardHeader>
              <CardTitle>Créer une annonce</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                className="w-full min-h-[150px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Partagez quelque chose avec votre classe..."
                value={announcementContent}
                onChange={(e) => setAnnouncementContent(e.target.value)}
              />
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isPinned}
                    onChange={(e) => setIsPinned(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Épingler en haut</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allowComments}
                    onChange={(e) => setAllowComments(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Autoriser les commentaires</span>
                </label>
              </div>
              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline"
                  onClick={() => {
                    setShowAnnounceDialog(false);
                    setAnnouncementContent('');
                    setIsPinned(false);
                    setAllowComments(true);
                  }}
                >
                  Annuler
                </Button>
                <Button 
                  onClick={handleCreateAnnouncement}
                  disabled={!announcementContent.trim() || creating}
                >
                  {creating ? 'Publication...' : 'Publier'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Announcements */}
        <div className="space-y-4">
          {announcements.length === 0 ? (
            <Card className="p-12 text-center">
              <Megaphone className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No announcements yet</h3>
              <p className="text-muted-foreground">
                {isTeacher
                  ? 'Create your first announcement to communicate with students'
                  : 'Your teacher will post announcements here'}
              </p>
            </Card>
          ) : (
            announcements.map((announcement: Announcement) => (
              <Card key={announcement.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">
                        {announcement.teacher?.prenom} {announcement.teacher?.nom}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {new Date(announcement.createdAt).toLocaleDateString()} at{' '}
                        {new Date(announcement.createdAt).toLocaleTimeString()}
                      </p>
                    </div>
                    {announcement.isPinned && (
                      <span className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs">
                        Pinned
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap">{announcement.content}</p>
                  {announcement.commentsCount && announcement.commentsCount > 0 && (
                    <div className="mt-4 pt-4 border-t flex items-center gap-2 text-sm text-muted-foreground">
                      <MessageSquare className="h-4 w-4" />
                      <span>{announcement.commentsCount} comments</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Upcoming Assignments */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Upcoming</CardTitle>
          </CardHeader>
          <CardContent>
            {upcomingAssignments.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No upcoming assignments
              </p>
            ) : (
              <div className="space-y-3">
                {upcomingAssignments.map((assignment: Assignment) => (
                  <div
                    key={assignment.id}
                    className="p-3 rounded-lg border hover:bg-gray-50 cursor-pointer"
                  >
                    <h4 className="font-medium text-sm">{assignment.title}</h4>
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>
                        Due {new Date(assignment.dueDate!).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Course Code */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Code de classe</CardTitle>
          </CardHeader>
          <CardContent>
            {course.codeInvitation ? (
              <div className="space-y-3">
                <div className="p-4 rounded-lg bg-primary/5 border-2 border-primary/20 text-center">
                  <p className="text-3xl font-mono font-bold tracking-wider text-primary">
                    {course.codeInvitation}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground text-center">
                  Partagez ce code avec les élèves pour qu'ils s'inscrivent
                </p>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    navigator.clipboard.writeText(course.codeInvitation!);
                    alert('Code copié!');
                  }}
                >
                  Copier le code
                </Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center">
                Aucun code d'invitation
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Assignments View Component
function AssignmentsView({ courseId, isTeacher }: any) {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructions: '',
    points: 100,
    dueDate: '',
    availableFrom: '',
    allowLateSubmissions: true,
    enablePlagiarismCheck: true,
    enableAIFeedback: true
  });

  useEffect(() => {
    loadAssignments();
  }, [courseId]);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const data = await classroomApi.getAssignments(courseId);
      setAssignments(data);
    } catch (error) {
      console.error('Failed to load assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAssignment = async () => {
    if (!formData.title.trim()) {
      alert('Le titre est requis');
      return;
    }

    try {
      setCreating(true);
      await classroomApi.createAssignment(courseId, {
        ...formData,
        dueDate: formData.dueDate ? new Date(formData.dueDate).toISOString() : undefined,
        availableFrom: formData.availableFrom ? new Date(formData.availableFrom).toISOString() : undefined
      });
      setShowCreateDialog(false);
      setFormData({
        title: '',
        description: '',
        instructions: '',
        points: 100,
        dueDate: '',
        availableFrom: '',
        allowLateSubmissions: true,
        enablePlagiarismCheck: true,
        enableAIFeedback: true
      });
      loadAssignments();
    } catch (error) {
      console.error('Failed to create assignment:', error);
      alert('Échec de la création du devoir');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="py-6 space-y-6">
      {/* Header with Create Button */}
      {isTeacher && (
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Devoirs</h2>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Créer un devoir
          </Button>
        </div>
      )}

      {/* Create Assignment Dialog */}
      {showCreateDialog && (
        <Card className="border-2 border-primary">
          <CardHeader>
            <CardTitle>Créer un devoir</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Titre *</label>
              <input
                type="text"
                className="w-full p-2 border rounded-lg"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Titre du devoir"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                className="w-full p-2 border rounded-lg resize-none"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Description courte..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Instructions</label>
              <textarea
                className="w-full p-2 border rounded-lg resize-none"
                rows={4}
                value={formData.instructions}
                onChange={(e) => setFormData({...formData, instructions: e.target.value})}
                placeholder="Instructions détaillées..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Points</label>
                <input
                  type="number"
                  className="w-full p-2 border rounded-lg"
                  value={formData.points}
                  onChange={(e) => setFormData({...formData, points: parseInt(e.target.value)})}
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Date limite</label>
                <input
                  type="datetime-local"
                  className="w-full p-2 border rounded-lg"
                  value={formData.dueDate}
                  onChange={(e) => setFormData({...formData, dueDate: e.target.value})}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Disponible à partir de</label>
              <input
                type="datetime-local"
                className="w-full p-2 border rounded-lg"
                value={formData.availableFrom}
                onChange={(e) => setFormData({...formData, availableFrom: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.allowLateSubmissions}
                  onChange={(e) => setFormData({...formData, allowLateSubmissions: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm">Autoriser les soumissions tardives</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.enablePlagiarismCheck}
                  onChange={(e) => setFormData({...formData, enablePlagiarismCheck: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm">Activer la détection de plagiat (IA)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.enableAIFeedback}
                  onChange={(e) => setFormData({...formData, enableAIFeedback: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm">Activer les commentaires IA</span>
              </label>
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button 
                variant="outline"
                onClick={() => {
                  setShowCreateDialog(false);
                  setFormData({
                    title: '',
                    description: '',
                    instructions: '',
                    points: 100,
                    dueDate: '',
                    availableFrom: '',
                    allowLateSubmissions: true,
                    enablePlagiarismCheck: true,
                    enableAIFeedback: true
                  });
                }}
              >
                Annuler
              </Button>
              <Button 
                onClick={handleCreateAssignment}
                disabled={!formData.title.trim() || creating}
              >
                {creating ? 'Création...' : 'Créer'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Assignments List */}
      {assignments.length === 0 ? (
        <Card className="p-12 text-center">
          <BookOpen className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold mb-2">Aucun devoir</h3>
          <p className="text-muted-foreground">
            {isTeacher
              ? 'Créez votre premier devoir pour vos étudiants'
              : 'Aucun devoir pour le moment'}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {assignments.map((assignment) => (
            <Card key={assignment.id} className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{assignment.title}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      {assignment.points} points • 
                      {assignment.dueDate && ` Date limite: ${new Date(assignment.dueDate).toLocaleDateString()}`}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    assignment.status === 'PUBLISHED' 
                      ? 'bg-green-100 text-green-700'
                      : assignment.status === 'DRAFT'
                      ? 'bg-gray-100 text-gray-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {assignment.status === 'PUBLISHED' ? 'Publié' : 
                     assignment.status === 'DRAFT' ? 'Brouillon' : 'Fermé'}
                  </span>
                </div>
              </CardHeader>
              {assignment.description && (
                <CardContent>
                  <p className="text-sm line-clamp-2">{assignment.description}</p>
                  <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
                    <span>{assignment.submissionsCount || 0} soumissions</span>
                    {isTeacher && <span>{assignment.gradedCount || 0} notées</span>}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// Materials View Component
function MaterialsView({ courseId, isTeacher }: any) {
  const router = useRouter();
  const [materials, setMaterials] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    url: '',
    folder: 'General'
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    loadMaterials();
  }, [courseId]);

  const loadMaterials = async () => {
    try {
      setLoading(true);
      const data = await classroomApi.getMaterials(courseId);
      setMaterials(data);
    } catch (error) {
      console.error('Failed to load materials:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadMaterial = async () => {
    if (!formData.title.trim() || (!selectedFile && !formData.url.trim())) {
      alert('Le titre et un fichier ou URL sont requis');
      return;
    }

    try {
      setUploading(true);
      const materialData: any = {
        ...formData,
        fileUrl: formData.url || undefined
      };

      if (selectedFile) {
        // In a real implementation, you would upload the file first and get the URL
        // For now, we'll just use the file name
        materialData.fileUrl = `/uploads/${selectedFile.name}`;
        materialData.fileName = selectedFile.name;
        materialData.fileType = selectedFile.type;
        materialData.fileSize = selectedFile.size;
      }

      await classroomApi.createMaterial(courseId, materialData);
      setShowUploadDialog(false);
      setFormData({ title: '', description: '', url: '', folder: 'General' });
      setSelectedFile(null);
      loadMaterials();
    } catch (error) {
      console.error('Failed to upload material:', error);
      alert('Échec du téléchargement du matériel');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="py-6 space-y-6">
      {/* Header with Upload Button */}
      {isTeacher && (
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Matériaux</h2>
          <Button onClick={() => setShowUploadDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Ajouter du matériel
          </Button>
        </div>
      )}

      {/* Upload Material Dialog */}
      {showUploadDialog && (
        <Card className="border-2 border-primary">
          <CardHeader>
            <CardTitle>Ajouter du matériel</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Titre *</label>
              <input
                type="text"
                className="w-full p-2 border rounded-lg"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Nom du matériel"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                className="w-full p-2 border rounded-lg resize-none"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Description facultative..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Dossier</label>
              <select
                className="w-full p-2 border rounded-lg"
                value={formData.folder}
                onChange={(e) => setFormData({...formData, folder: e.target.value})}
              >
                <option value="General">Général</option>
                <option value="Lectures">Cours</option>
                <option value="Resources">Ressources</option>
                <option value="Assignments">Devoirs</option>
              </select>
            </div>
            <div className="border-t pt-4">
              <label className="block text-sm font-medium mb-2">Fichier</label>
              <input
                type="file"
                className="w-full p-2 border rounded-lg"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              {selectedFile && (
                <p className="text-sm text-muted-foreground mt-2">
                  {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>
            <div className="text-center text-sm text-muted-foreground">OU</div>
            <div>
              <label className="block text-sm font-medium mb-2">URL</label>
              <input
                type="url"
                className="w-full p-2 border rounded-lg"
                value={formData.url}
                onChange={(e) => setFormData({...formData, url: e.target.value})}
                placeholder="https://..."
              />
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button 
                variant="outline"
                onClick={() => {
                  setShowUploadDialog(false);
                  setFormData({ title: '', description: '', url: '', folder: 'General' });
                  setSelectedFile(null);
                }}
              >
                Annuler
              </Button>
              <Button 
                onClick={handleUploadMaterial}
                disabled={!formData.title.trim() || (!selectedFile && !formData.url.trim()) || uploading}
              >
                {uploading ? 'Téléchargement...' : 'Ajouter'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Materials List */}
      {materials.length === 0 ? (
        <Card className="p-12 text-center">
          <FolderOpen className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold mb-2">Aucun matériel</h3>
          <p className="text-muted-foreground">
            {isTeacher
              ? 'Ajoutez des fichiers, liens et ressources pour vos étudiants'
              : 'Aucun matériel disponible pour le moment'}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {materials.map((material) => (
            <Card 
              key={material.id} 
              className="hover:shadow-md transition-shadow cursor-pointer hover:border-primary"
              onClick={() => router.push(`/classroom/materials/${material.id}`)}
            >
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <FolderOpen className="h-8 w-8 text-primary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate">{material.title || material.titre}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {material.type === 'link' ? '🔗 Lien' : '📄 Document'} • {material.fileSize ? `${(material.fileSize / 1024).toFixed(1)} KB` : 'Lien'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(material.createdAt).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// Discussions View Component
function DiscussionsView({ courseId }: any) {
  const [discussions, setDiscussions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    isPinned: false
  });

  useEffect(() => {
    loadDiscussions();
  }, [courseId]);

  const loadDiscussions = async () => {
    try {
      setLoading(true);
      const data = await classroomApi.getDiscussions(courseId);
      setDiscussions(data);
    } catch (error) {
      console.error('Failed to load discussions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDiscussion = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      alert('Le titre et le contenu sont requis');
      return;
    }

    try {
      setCreating(true);
      await classroomApi.createDiscussion(courseId, formData);
      setShowCreateDialog(false);
      setFormData({ title: '', content: '', isPinned: false });
      loadDiscussions();
    } catch (error) {
      console.error('Failed to create discussion:', error);
      alert('Échec de la création de la discussion');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="py-6 space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Discussions</h2>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nouvelle discussion
        </Button>
      </div>

      {/* Create Discussion Dialog */}
      {showCreateDialog && (
        <Card className="border-2 border-primary">
          <CardHeader>
            <CardTitle>Nouvelle discussion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Titre *</label>
              <input
                type="text"
                className="w-full p-2 border rounded-lg"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Titre de la discussion"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Contenu *</label>
              <textarea
                className="w-full p-2 border rounded-lg resize-none"
                rows={6}
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                placeholder="Décrivez votre question ou démarrez une conversation..."
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.isPinned}
                onChange={(e) => setFormData({...formData, isPinned: e.target.checked})}
                className="rounded"
              />
              <span className="text-sm">Épingler cette discussion en haut</span>
            </label>
            <div className="flex justify-end gap-2 pt-4">
              <Button 
                variant="outline"
                onClick={() => {
                  setShowCreateDialog(false);
                  setFormData({ title: '', content: '', isPinned: false });
                }}
              >
                Annuler
              </Button>
              <Button 
                onClick={handleCreateDiscussion}
                disabled={!formData.title.trim() || !formData.content.trim() || creating}
              >
                {creating ? 'Création...' : 'Publier'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Discussions List */}
      {discussions.length === 0 ? (
        <Card className="p-12 text-center">
          <MessageSquare className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold mb-2">Aucune discussion</h3>
          <p className="text-muted-foreground">
            Commencez une discussion pour poser des questions ou partager des idées
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {discussions.map((discussion) => (
            <Card key={discussion.id} className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      {discussion.isPinned && (
                        <span className="px-2 py-0.5 rounded text-xs bg-primary/10 text-primary">
                          Épinglé
                        </span>
                      )}
                      {discussion.isResolved && (
                        <span className="px-2 py-0.5 rounded text-xs bg-green-100 text-green-700">
                          Résolu
                        </span>
                      )}
                    </div>
                    <h4 className="font-medium mt-2">{discussion.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {discussion.content}
                    </p>
                    <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                      <span>{discussion.author?.prenom} {discussion.author?.nom}</span>
                      <span>{new Date(discussion.createdAt).toLocaleDateString()}</span>
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {discussion.repliesCount || 0} réponses
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function getRandomColor(seed: string): string {
  const colors = [
    '#6366f1',
    '#8b5cf6',
    '#ec4899',
    '#f43f5e',
    '#f97316',
    '#eab308',
    '#22c55e',
    '#14b8a6',
    '#06b6d4',
    '#0ea5e9',
  ];
  
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}
