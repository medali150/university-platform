'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi } from '@/lib/classroom-api';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Save, AlertCircle } from 'lucide-react';

// Get current academic year
const getCurrentAcademicYear = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  // If before September, use previous year
  if (month < 9) {
    return `${year - 1}-${year}`;
  }
  return `${year}-${year + 1}`;
};

export default function NewCoursePage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<{
    nom: string;
    description: string;
    anneeAcademique: string;
    semestre: string;
    couleur: string;
    estPublic: boolean;
    capaciteMax?: number;
  }>({
    nom: '',
    description: '',
    anneeAcademique: getCurrentAcademicYear(),
    semestre: 'S1',
    couleur: '#3B82F6',
    estPublic: false,
  });

  // Protect this page - only teachers can create courses
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || user?.role !== 'TEACHER')) {
      alert('❌ Seuls les enseignants peuvent créer des cours');
      router.push('/classroom/courses');
    }
  }, [authLoading, isAuthenticated, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const course = await classroomApi.createCourse(formData);
      router.push(`/classroom/courses/${course.id}`);
    } catch (error: any) {
      alert(`Failed to create course: ${error.message}`);
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // If not teacher, don't render (will redirect)
  if (!user || user.role !== 'TEACHER') {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.back()}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Créer un nouveau cours</h1>
          <p className="text-muted-foreground mt-1">
            Configurez un nouveau cours pour vos étudiants
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Détails du cours</CardTitle>
            <CardDescription>
              Entrez les informations de base sur votre cours
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Course Name */}
            <div className="space-y-2">
              <Label htmlFor="nom">
                Nom du cours <span className="text-red-500">*</span>
              </Label>
              <Input
                id="nom"
                name="nom"
                placeholder="Ex: Introduction à l'informatique, Big Data, etc."
                value={formData.nom}
                onChange={handleChange}
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                name="description"
                placeholder="Décrivez ce que les étudiants apprendront dans ce cours..."
                value={formData.description}
                onChange={handleChange}
                rows={4}
              />
            </div>

            {/* Row 1: Academic Year & Semester */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anneeAcademique">
                  Année académique <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="anneeAcademique"
                  name="anneeAcademique"
                  placeholder="2024-2025"
                  value={formData.anneeAcademique}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="semestre">
                  Semestre <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={formData.semestre}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, semestre: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="S1">Semestre 1 (S1)</SelectItem>
                    <SelectItem value="S2">Semestre 2 (S2)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Row 2: Color & Capacity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="couleur">Couleur du thème</Label>
                <div className="flex gap-2">
                  <Input
                    id="couleur"
                    name="couleur"
                    type="color"
                    value={formData.couleur}
                    onChange={handleChange}
                    className="w-20 h-10"
                  />
                  <Input
                    value={formData.couleur}
                    onChange={(e) => setFormData(prev => ({ ...prev, couleur: e.target.value }))}
                    placeholder="#3B82F6"
                    className="flex-1"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="capaciteMax">Capacité maximale (optionnel)</Label>
                <Input
                  id="capaciteMax"
                  name="capaciteMax"
                  type="number"
                  placeholder="Ex: 30, 50, 100"
                  value={formData.capaciteMax || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, capaciteMax: e.target.value ? parseInt(e.target.value) : undefined }))}
                />
              </div>
            </div>

            {/* Public/Private */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="estPublic"
                checked={formData.estPublic}
                onChange={(e) => setFormData(prev => ({ ...prev, estPublic: e.target.checked }))}
                className="w-4 h-4 rounded border-gray-300"
              />
              <Label htmlFor="estPublic" className="font-normal cursor-pointer">
                Cours public (tout le monde peut rejoindre)
              </Label>
            </div>

            {/* Buttons */}
            <div className="flex justify-end gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={loading}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Création...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Créer le cours
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
