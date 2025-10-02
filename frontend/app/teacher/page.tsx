import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Calendar, User, BookOpen, GraduationCap } from 'lucide-react';

export default function TeacherPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Espace Enseignant</h1>
        <p className="text-muted-foreground">
          Gérez vos cours, étudiants et absences
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Absence Management */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              Gestion des Absences
            </CardTitle>
            <CardDescription>
              Marquez les absences de vos étudiants pour chaque cours
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/teacher/absence">
              <Button className="w-full">
                Gérer les Absences
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Profile Management */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              Mon Profil
            </CardTitle>
            <CardDescription>
              Gérez vos informations personnelles et votre département
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/teacher/profile">
              <Button className="w-full" variant="outline">
                Voir le Profil
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Schedule */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              Mon Planning
            </CardTitle>
            <CardDescription>
              Consultez votre emploi du temps et vos cours
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/teacher/schedule">
              <Button className="w-full" variant="outline">
                Voir le Planning
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Subjects */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              Mes Matières
            </CardTitle>
            <CardDescription>
              Consultez les matières que vous enseignez
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/teacher/subjects">
              <Button className="w-full" variant="outline">
                Voir les Matières
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Groups */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary" />
              Mes Groupes
            </CardTitle>
            <CardDescription>
              Consultez tous les groupes que vous enseignez
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/teacher/groups">
              <Button className="w-full" variant="outline">
                Voir les Groupes
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}