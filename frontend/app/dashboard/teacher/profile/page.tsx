"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { User, Building2, BookOpen, Users, Mail, GraduationCap, Camera } from 'lucide-react';
import { toast } from 'sonner';
import { TeacherAPI, TeacherProfile, Department } from '@/lib/teacher-api';
import { ImageUploadComponent } from '@/components/teacher/image-upload';



export default function TeacherProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [availableDepartments, setAvailableDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  // Fetch teacher profile
  const fetchProfile = async () => {
    try {
      const data = await TeacherAPI.getProfile();
      setProfile(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast.error('Erreur lors du chargement du profil');
    }
  };

  // Fetch available departments
  const fetchDepartments = async () => {
    try {
      const data = await TeacherAPI.getDepartments();
      setAvailableDepartments(data);
    } catch (error) {
      console.error('Error fetching departments:', error);
      toast.error('Erreur lors du chargement des départements');
    }
  };

  // Update teacher department
  const updateDepartment = async (newDepartmentId: string) => {
    setUpdating(true);
    try {
      await TeacherAPI.updateDepartment(newDepartmentId);
      toast.success('Département mis à jour avec succès');
      fetchProfile(); // Refresh profile
    } catch (error) {
      console.error('Error updating department:', error);
      toast.error('Erreur lors de la mise à jour');
    } finally {
      setUpdating(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchProfile(), fetchDepartments()]);
      setLoading(false);
    };
    
    if (user?.role === 'TEACHER') {
      loadData();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">Chargement du profil...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center text-red-600">Profil enseignant non trouvé</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Mon Profil Enseignant</h1>
        <Badge variant="secondary" className="text-sm">
          <GraduationCap className="w-4 h-4 mr-1" />
          Enseignant
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Image Upload */}
        <ImageUploadComponent
          currentImageUrl={profile.teacher_info.image_url}
          teacherName={`${profile.teacher_info.prenom} ${profile.teacher_info.nom}`}
          onImageUpdate={(imageUrl) => {
            setProfile(prev => prev ? {
              ...prev,
              teacher_info: {
                ...prev.teacher_info,
                image_url: imageUrl || undefined
              }
            } : null);
          }}
        />

        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Informations Personnelles
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Nom Complet</label>
              <p className="text-lg font-semibold">
                {profile.teacher_info.prenom} {profile.teacher_info.nom}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Email</label>
              <p className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                {profile.teacher_info.email}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Membre depuis</label>
              <p>{new Date(profile.teacher_info.createdAt).toLocaleDateString('fr-FR')}</p>
            </div>
          </CardContent>
        </Card>

        {/* Department Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Département
            </CardTitle>
            <CardDescription>
              Votre département actuel et ses spécialités
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Département Actuel</label>
              <p className="text-lg font-semibold">{profile.department.nom}</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-600">Changer de Département</label>
              <Select 
                onValueChange={updateDepartment}
                disabled={updating}
                defaultValue={profile.department.id}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un département" />
                </SelectTrigger>
                <SelectContent>
                  {availableDepartments.map((dept) => (
                    <SelectItem key={dept.id} value={dept.id}>
                      {dept.nom}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {profile.department_head && (
              <div>
                <label className="text-sm font-medium text-gray-600">Chef de Département</label>
                <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                  <User className="w-4 h-4" />
                  <div>
                    <p className="font-semibold">
                      {profile.department_head.prenom} {profile.department_head.nom}
                    </p>
                    <p className="text-sm text-gray-600">{profile.department_head.email}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Specialties */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Spécialités du Département
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {profile.department.specialties.map((specialty) => (
              <div key={specialty.id} className="p-4 border rounded-lg">
                <h3 className="font-semibold mb-2">{specialty.nom}</h3>
                <div className="space-y-1">
                  {specialty.levels.map((level) => (
                    <Badge key={level.id} variant="outline" className="mr-1 mb-1">
                      {level.nom}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Subjects Taught */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Matières Enseignées
          </CardTitle>
        </CardHeader>
        <CardContent>
          {profile.subjects_taught.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {profile.subjects_taught.map((subject) => (
                <div key={subject.id} className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-2">{subject.nom}</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>
                      <strong>Niveau:</strong> {subject.level.nom}
                    </p>
                    <p>
                      <strong>Spécialité:</strong> {subject.level.specialty.nom}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Aucune matière assignée pour le moment
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}