'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { 
  Home, 
  Calendar, 
  BookOpen, 
  User, 
  LogOut, 
  Menu,
  X,
  GraduationCap
} from 'lucide-react';
import { StudentAPI, StudentProfile } from '@/lib/student-api';

interface NavigationItem {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  description: string;
}

const navigationItems: NavigationItem[] = [
  {
    href: '/student/dashboard',
    icon: Home,
    label: 'Tableau de bord',
    description: 'Vue d\'ensemble de votre journée'
  },
  {
    href: '/student/timetable',
    icon: Calendar,
    label: 'Emploi du temps',
    description: 'Votre planning complet'
  },
  {
    href: '/student/profile',
    icon: User,
    label: 'Mon profil',
    description: 'Vos informations personnelles'
  }
];

interface StudentLayoutProps {
  children: React.ReactNode;
}

export default function StudentLayout({ children }: StudentLayoutProps) {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profileData = await StudentAPI.getProfile();
        setProfile(profileData);
      } catch (error) {
        console.error('Failed to load profile:', error);
        // Redirect to login if authentication fails
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const isActive = (href: string) => {
    return pathname === href;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and title */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <GraduationCap className="h-8 w-8 text-primary" />
                <div className="hidden sm:block">
                  <h1 className="text-xl font-bold text-gray-900">
                    Espace Étudiant
                  </h1>
                  <p className="text-xs text-gray-500">
                    Université Management System
                  </p>
                </div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={isActive(item.href) ? "default" : "ghost"}
                      className="flex items-center gap-2"
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Button>
                  </Link>
                );
              })}
            </nav>

            {/* User menu */}
            <div className="flex items-center gap-4">
              {profile && (
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {profile.prenom} {profile.nom}
                  </p>
                  <p className="text-xs text-gray-500">
                    {profile.groupe.nom}
                  </p>
                </div>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="relative h-10 w-10 rounded-full">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={profile?.image_url || undefined} />
                      <AvatarFallback>
                        {profile ? getInitials(profile.prenom, profile.nom) : 'ST'}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">
                        {profile ? `${profile.prenom} ${profile.nom}` : 'Étudiant'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {profile?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/student/profile" className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      Mon profil
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                    <LogOut className="mr-2 h-4 w-4" />
                    Se déconnecter
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Mobile menu button */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? (
                  <X className="h-5 w-5" />
                ) : (
                  <Menu className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t bg-white">
            <div className="px-4 py-3 space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link 
                    key={item.href} 
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <div className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm ${
                      isActive(item.href) 
                        ? 'bg-primary text-primary-foreground' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}>
                      <Icon className="h-4 w-4" />
                      <div>
                        <p className="font-medium">{item.label}</p>
                        <p className="text-xs opacity-70">{item.description}</p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <GraduationCap className="h-4 w-4" />
              <span>© 2024 Université Management System</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Espace Étudiant</span>
              {profile && (
                <Badge variant="outline">
                  {profile.groupe.nom}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}