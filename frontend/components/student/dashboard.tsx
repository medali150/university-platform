'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Clock, 
  MapPin, 
  User, 
  BookOpen,
  AlertCircle,
  CheckCircle,
  XCircle,
  CalendarDays,
  GraduationCap,
  TrendingUp,
  Award,
  Target,
  ActivityIcon
} from 'lucide-react';
import { StudentAPI, StudentSchedule, StudentProfile } from '@/lib/student-api';

interface TodayScheduleCardProps {
  schedule: StudentSchedule;
  isNext?: boolean;
}

const TodayScheduleCard: React.FC<TodayScheduleCardProps> = ({ schedule, isNext = false }) => {
  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PLANNED':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700">Programmé</Badge>;
      case 'CANCELED':
        return <Badge variant="destructive">Annulé</Badge>;
      case 'MAKEUP':
        return <Badge variant="secondary">Rattrapage</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getAbsenceBadge = (absence: StudentSchedule['absence']) => {
    if (!absence || !absence.is_absent) return null;
    
    switch (absence.status) {
      case 'PENDING':
        return <Badge variant="outline" className="bg-orange-50 text-orange-700">Absence en attente</Badge>;
      case 'JUSTIFIED':
        return <Badge variant="outline" className="bg-green-50 text-green-700">Absence justifiée</Badge>;
      case 'REFUSED':
        return <Badge variant="destructive">Absence refusée</Badge>;
      default:
        return <Badge variant="destructive">Absent</Badge>;
    }
  };

  const isCurrentlyInClass = () => {
    const now = new Date();
    const startTime = new Date(schedule.heure_debut);
    const endTime = new Date(schedule.heure_fin);
    return now >= startTime && now <= endTime;
  };

  const getTimeUntilClass = () => {
    const now = new Date();
    const startTime = new Date(schedule.heure_debut);
    const diffMs = startTime.getTime() - now.getTime();
    
    if (diffMs <= 0) return null;
    
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `Dans ${hours}h ${minutes}min`;
    } else {
      return `Dans ${minutes}min`;
    }
  };

  const timeUntil = getTimeUntilClass();
  const inClass = isCurrentlyInClass();

  return (
    <Card className={`${isNext ? 'border-l-4 border-l-primary shadow-md' : ''} ${inClass ? 'bg-green-50 border-green-200' : ''}`}>
      <CardContent className="p-4">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="h-4 w-4 text-primary" />
              <h3 className="font-semibold text-lg">
                {schedule.matiere.nom}
              </h3>
              {isNext && <Badge variant="outline" className="bg-blue-50 text-blue-700">Prochain cours</Badge>}
              {inClass && <Badge className="bg-green-600">En cours</Badge>}
              {getStatusBadge(schedule.status)}
              {getAbsenceBadge(schedule.absence)}
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>
                  {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                <User className="h-3 w-3" />
                <span>
                  Prof. {schedule.enseignant.prenom} {schedule.enseignant.nom}
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                <span>
                  Salle {schedule.salle.code}
                </span>
              </div>
            </div>

            {timeUntil && (
              <div className="mt-2 text-sm font-medium text-blue-600">
                {timeUntil}
              </div>
            )}

            {schedule.absence?.motif && (
              <div className="mt-2 p-2 bg-orange-50 rounded text-sm">
                <strong>Motif d'absence:</strong> {schedule.absence.motif}
              </div>
            )}
          </div>
          
          <div className="flex flex-col items-end gap-1">
            {schedule.absence?.is_absent ? (
              <XCircle className="h-5 w-5 text-red-500" />
            ) : (
              <CheckCircle className="h-5 w-5 text-green-500" />
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default function StudentDashboard() {
  const [todaySchedule, setTodaySchedule] = useState<StudentSchedule[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [scheduleData, profileData] = await Promise.all([
          StudentAPI.getTodaySchedule(),
          StudentAPI.getProfile()
        ]);

        setTodaySchedule(scheduleData);
        setProfile(profileData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getNextClass = () => {
    const now = new Date();
    return todaySchedule
      .filter(schedule => new Date(schedule.heure_debut) > now)
      .sort((a, b) => new Date(a.heure_debut).getTime() - new Date(b.heure_debut).getTime())[0];
  };

  const getCurrentClass = () => {
    const now = new Date();
    return todaySchedule.find(schedule => {
      const startTime = new Date(schedule.heure_debut);
      const endTime = new Date(schedule.heure_fin);
      return now >= startTime && now <= endTime;
    });
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bonjour';
    if (hour < 18) return 'Bon après-midi';
    return 'Bonsoir';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-white/60">Chargement de votre tableau de bord...</p>
        </div>
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

  const nextClass = getNextClass();
  const currentClass = getCurrentClass();
  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Modern Gradient Header */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-6 sm:p-8 md:p-10 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-2">
            Bienvenue, {profile?.prenom}! 👋
          </h1>
          <p className="text-indigo-100 text-base sm:text-lg">
            {today}
          </p>
        </div>
      </div>

      {/* Quick Profile Summary */}
      {profile && (
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center text-white shadow-lg">
                  <GraduationCap className="h-7 w-7" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-900">{profile.prenom} {profile.nom}</h3>
                  <p className="text-sm text-gray-600">📚 {profile.groupe.nom}</p>
                </div>
              </div>
              <Link href="/dashboard/student/profile">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  Voir le profil
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-blue-100 text-blue-600">
              <CalendarDays className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">Aujourd'hui</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Cours aujourd'hui</p>
          <p className="text-3xl font-bold text-gray-900">{todaySchedule.length}</p>
        </div>

        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-orange-100 text-orange-600">
              <AlertCircle className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">Attention</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Absences</p>
          <p className="text-3xl font-bold text-gray-900">
            {todaySchedule.filter(s => s.absence?.is_absent).length}
          </p>
        </div>

        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-green-100 text-green-600">
              <CheckCircle className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">Bon</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Présences</p>
          <p className="text-3xl font-bold text-gray-900">
            {todaySchedule.filter(s => !s.absence?.is_absent).length}
          </p>
        </div>

        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-purple-100 text-purple-600">
              <Award className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-purple-600 bg-purple-50 px-2 py-1 rounded-full">Moyenne</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Taux de présence</p>
          <p className="text-3xl font-bold text-gray-900">
            {todaySchedule.length > 0 
              ? Math.round((todaySchedule.filter(s => !s.absence?.is_absent).length / todaySchedule.length) * 100)
              : 0}%
          </p>
        </div>
      </div>

      {/* Current Class */}
      {currentClass && (
        <div className="space-y-2">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Clock className="h-5 w-5 text-green-600" />
            Cours en cours
          </h2>
          <TodayScheduleCard schedule={currentClass} />
        </div>
      )}

      {/* Next Class */}
      {nextClass && (
        <div className="space-y-2">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <CalendarDays className="h-5 w-5 text-blue-600" />
            Prochain cours
          </h2>
          <TodayScheduleCard schedule={nextClass} isNext={true} />
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link href="/dashboard/student/timetable">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <CalendarDays className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <h3 className="font-semibold text-gray-900">Emploi du temps</h3>
              <p className="text-sm text-gray-600">Consulter votre planning</p>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/dashboard/student/grades">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <BookOpen className="h-8 w-8 mx-auto mb-2 text-orange-600" />
              <h3 className="font-semibold text-gray-900">Mes Notes</h3>
              <p className="text-sm text-gray-600">Consulter mes résultats</p>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/dashboard/student/profile">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <User className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <h3 className="font-semibold text-gray-900">Mon Profil</h3>
              <p className="text-sm text-gray-600">Voir mes informations</p>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/dashboard/student/absences">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="p-4 text-center">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <h3 className="font-semibold text-gray-900">Mes Absences</h3>
              <p className="text-sm text-gray-600">Gérer mes absences</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Today's Complete Schedule */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          Emploi du temps d'aujourd'hui
          <Badge variant="outline">{todaySchedule.length} cours</Badge>
        </h2>
        
        {todaySchedule.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <CalendarDays className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">Aucun cours programmé aujourd'hui</p>
              <p className="text-sm text-muted-foreground mt-2">Profitez de votre journée libre !</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {/* Show only next 3 classes or all if less than 3 */}
            {todaySchedule
              .sort((a, b) => new Date(a.heure_debut).getTime() - new Date(b.heure_debut).getTime())
              .slice(0, 3)
              .map(schedule => (
                <TodayScheduleCard 
                  key={schedule.id} 
                  schedule={schedule}
                  isNext={schedule.id === nextClass?.id && !currentClass}
                />
              ))}
            
            {todaySchedule.length > 3 && (
              <Card className="border-dashed">
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-muted-foreground mb-2">
                    +{todaySchedule.length - 3} autres cours aujourd'hui
                  </p>
                  <Link href="/dashboard/student/timetable">
                    <Button variant="outline" size="sm">
                      Voir tout l'emploi du temps
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
}