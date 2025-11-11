'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi } from '@/lib/classroom-api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Users, Mail, UserCheck, Search } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface CoursePeopleProps {
  params: {
    id: string;
  };
}

interface Person {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  role: string;
  enrolledAt?: string;
  imageUrl?: string;
}

export default function CoursePeoplePage({ params }: CoursePeopleProps) {
  const router = useRouter();
  const { user } = useAuth();
  const [teacher, setTeacher] = useState<Person | null>(null);
  const [students, setStudents] = useState<Person[]>([]);
  const [filteredStudents, setFilteredStudents] = useState<Person[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPeople();
  }, [params.id]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredStudents(students);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = students.filter(student => 
        student.nom.toLowerCase().includes(query) ||
        student.prenom.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query)
      );
      setFilteredStudents(filtered);
    }
  }, [searchQuery, students]);

  const loadPeople = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/classroom/courses/${params.id}/people`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load people');
      }

      const data = await response.json();
      setTeacher(data.teacher);
      setStudents(data.students);
      setFilteredStudents(data.students);
    } catch (error) {
      console.error('Failed to load course people:', error);
    } finally {
      setLoading(false);
    }
  };

  const isTeacher = user?.role === 'TEACHER';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push(`/classroom/courses/${params.id}`)}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex-1">
              <h1 className="text-2xl font-bold">Personnes</h1>
              <p className="text-muted-foreground mt-1">
                {students.length + 1} membres • {students.length} étudiants
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          {/* Teacher Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5" />
                Enseignant
              </CardTitle>
            </CardHeader>
            <CardContent>
              {teacher && (
                <div className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary font-semibold text-lg">
                      {teacher.prenom[0]}{teacher.nom[0]}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium">
                      {teacher.prenom} {teacher.nom}
                    </h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <Mail className="h-3 w-3" />
                      {teacher.email}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Students Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Étudiants ({filteredStudents.length})
                </CardTitle>
              </div>
              {/* Search */}
              <div className="mt-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Rechercher un étudiant..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredStudents.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">
                    {searchQuery ? 'Aucun résultat' : 'Aucun étudiant'}
                  </h3>
                  <p className="text-muted-foreground">
                    {searchQuery 
                      ? 'Aucun étudiant ne correspond à votre recherche'
                      : 'Aucun étudiant inscrit pour le moment'}
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredStudents.map((student) => (
                    <div
                      key={student.id}
                      className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50"
                    >
                      <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                        <span className="text-gray-600 font-medium">
                          {student.prenom[0]}{student.nom[0]}
                        </span>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">
                          {student.prenom} {student.nom}
                        </h4>
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {student.email}
                        </p>
                      </div>
                      {student.enrolledAt && (
                        <div className="text-xs text-muted-foreground">
                          Inscrit le {new Date(student.enrolledAt).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
