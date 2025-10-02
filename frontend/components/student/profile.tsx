'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  User, 
  Mail, 
  Users, 
  BookOpen,
  Building,
  GraduationCap,
  AlertCircle,
  Camera,
  Edit,
  Calendar
} from 'lucide-react';
import { StudentAPI, StudentProfile } from '@/lib/student-api';

export default function StudentProfilePage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        const profileData = await StudentAPI.getProfile();
        setProfile(profileData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Chargement du profil...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!profile) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Aucune donnée de profil trouvée</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mon Profil Étudiant</h1>
          <p className="text-muted-foreground">
            Toutes vos informations académiques et personnelles
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled>
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Picture and Basic Info */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col items-center space-y-4">
                <div className="relative">
                  <Avatar className="h-32 w-32">
                    <AvatarImage src={profile.image_url || undefined} />
                    <AvatarFallback className="text-2xl">
                      {getInitials(profile.prenom, profile.nom)}
                    </AvatarFallback>
                  </Avatar>
                  <Button
                    variant="outline"
                    size="sm"
                    className="absolute bottom-0 right-0 rounded-full h-8 w-8 p-0"
                  >
                    <Camera className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="text-center">
                  <h2 className="text-2xl font-bold">
                    {profile.prenom} {profile.nom}
                  </h2>
                  <p className="text-muted-foreground">
                    Étudiant
                  </p>
                  <Badge variant="outline" className="mt-2">
                    {profile.groupe.nom}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Informations Personnelles
              </CardTitle>
              <CardDescription>
                Vos informations de base
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Prénom
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-md">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{profile.prenom}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Nom de famille
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-md">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{profile.nom}</span>
                  </div>
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Adresse email
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-md">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{profile.email}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Academic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Informations Académiques
              </CardTitle>
              <CardDescription>
                Votre parcours académique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Group Information */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Groupe
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-md">
                    <Users className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-blue-900">{profile.groupe.nom}</span>
                  </div>
                </div>

                {/* Level Information */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Niveau
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-green-50 rounded-md">
                    <BookOpen className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-green-900">
                      {profile.groupe.niveau.nom}
                    </span>
                  </div>
                </div>

                {/* Speciality Information */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Spécialité
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-md">
                    <BookOpen className="h-4 w-4 text-purple-600" />
                    <span className="font-medium text-purple-900">
                      {profile.groupe.niveau.specialite.nom}
                    </span>
                  </div>
                </div>

                {/* Department Information */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Département
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-md">
                    <Building className="h-4 w-4 text-orange-600" />
                    <span className="font-medium text-orange-900">
                      {profile.groupe.niveau.specialite.departement.nom}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Academic Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Résumé Académique
              </CardTitle>
              <CardDescription>
                Vue d'ensemble de votre parcours académique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {profile.groupe.nom}
                  </div>
                  <p className="text-sm text-blue-800">Mon Groupe</p>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {profile.groupe.niveau.nom}
                  </div>
                  <p className="text-sm text-green-800">Niveau d'études</p>
                </div>

                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-lg font-bold text-purple-600">
                    {profile.specialite.nom}
                  </div>
                  <p className="text-sm text-purple-800">Spécialité</p>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-lg font-bold text-orange-600">
                    ID: {profile.id}
                  </div>
                  <p className="text-sm text-orange-800">Numéro Étudiant</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Navigation Links */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Actions Rapides
              </CardTitle>
              <CardDescription>
                Accès direct aux fonctionnalités principales
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link href="/dashboard/student/timetable">
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4 flex items-center gap-3">
                      <Calendar className="h-8 w-8 text-blue-600" />
                      <div>
                        <h3 className="font-semibold">Emploi du temps</h3>
                        <p className="text-sm text-muted-foreground">
                          Consulter votre planning complet
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>

                <Link href="/dashboard/student">
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4 flex items-center gap-3">
                      <BookOpen className="h-8 w-8 text-green-600" />
                      <div>
                        <h3 className="font-semibold">Tableau de bord</h3>
                        <p className="text-sm text-muted-foreground">
                          Retour au tableau de bord
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}