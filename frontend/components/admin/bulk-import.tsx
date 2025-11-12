'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, Download, Users, UserCheck, AlertCircle, CheckCircle, FileSpreadsheet } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export default function BulkImportPage() {
  const [studentsFile, setStudentsFile] = useState<File | null>(null);
  const [teachersFile, setTeachersFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleStudentsUpload = async () => {
    if (!studentsFile) {
      toast.error('Veuillez sélectionner un fichier Excel');
      return;
    }

    try {
      setLoading(true);
      setResults(null);

      const formData = new FormData();
      formData.append('file', studentsFile);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/admin/bulk-import/students`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de l\'importation');
      }

      const data = await response.json();
      setResults(data);
      toast.success(data.message);
      setStudentsFile(null);
      
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'importation');
      console.error('Import error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTeachersUpload = async () => {
    if (!teachersFile) {
      toast.error('Veuillez sélectionner un fichier Excel');
      return;
    }

    try {
      setLoading(true);
      setResults(null);

      const formData = new FormData();
      formData.append('file', teachersFile);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/admin/bulk-import/teachers`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors de l\'importation');
      }

      const data = await response.json();
      setResults(data);
      toast.success(data.message);
      setTeachersFile(null);
      
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'importation');
      console.error('Import error:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadStudentsTemplate = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/admin/bulk-import/template/students`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) throw new Error('Erreur lors du téléchargement');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'students_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Modèle téléchargé avec succès');
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors du téléchargement');
    }
  };

  const downloadTeachersTemplate = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/admin/bulk-import/template/teachers`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) throw new Error('Erreur lors du téléchargement');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'teachers_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Modèle téléchargé avec succès');
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors du téléchargement');
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Importation en Masse</h1>
        <p className="text-muted-foreground">
          Importez des étudiants et enseignants à partir de fichiers Excel
        </p>
      </div>

      {/* Instructions */}
      <Alert>
        <FileSpreadsheet className="h-4 w-4" />
        <AlertDescription>
          <strong>Instructions:</strong>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>Téléchargez le modèle Excel approprié (Étudiants ou Enseignants)</li>
            <li>Remplissez le fichier avec les données requises</li>
            <li>Téléchargez le fichier rempli</li>
            <li>Les comptes seront créés automatiquement</li>
          </ol>
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Students Import */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Users className="h-6 w-6 text-blue-600" />
              <div>
                <CardTitle>Importation Étudiants</CardTitle>
                <CardDescription>
                  Créer plusieurs comptes étudiants à la fois
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Download Template */}
            <div>
              <Button
                variant="outline"
                onClick={downloadStudentsTemplate}
                className="w-full"
              >
                <Download className="mr-2 h-4 w-4" />
                Télécharger le Modèle Excel
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                Colonnes requises: nom, prenom, email, numero_etudiant, groupe_nom
              </p>
            </div>

            {/* Upload File */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Fichier Excel</label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => setStudentsFile(e.target.files?.[0] || null)}
                className="w-full text-sm border rounded-md p-2"
              />
              {studentsFile && (
                <p className="text-sm text-green-600">
                  <CheckCircle className="inline h-4 w-4 mr-1" />
                  {studentsFile.name}
                </p>
              )}
            </div>

            {/* Upload Button */}
            <Button
              onClick={handleStudentsUpload}
              disabled={!studentsFile || loading}
              className="w-full"
            >
              <Upload className="mr-2 h-4 w-4" />
              {loading ? 'Importation...' : 'Importer les Étudiants'}
            </Button>
          </CardContent>
        </Card>

        {/* Teachers Import */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <UserCheck className="h-6 w-6 text-green-600" />
              <div>
                <CardTitle>Importation Enseignants</CardTitle>
                <CardDescription>
                  Créer plusieurs comptes enseignants à la fois
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Download Template */}
            <div>
              <Button
                variant="outline"
                onClick={downloadTeachersTemplate}
                className="w-full"
              >
                <Download className="mr-2 h-4 w-4" />
                Télécharger le Modèle Excel
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                Colonnes requises: nom, prenom, email, departement_nom
              </p>
            </div>

            {/* Upload File */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Fichier Excel</label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => setTeachersFile(e.target.files?.[0] || null)}
                className="w-full text-sm border rounded-md p-2"
              />
              {teachersFile && (
                <p className="text-sm text-green-600">
                  <CheckCircle className="inline h-4 w-4 mr-1" />
                  {teachersFile.name}
                </p>
              )}
            </div>

            {/* Upload Button */}
            <Button
              onClick={handleTeachersUpload}
              disabled={!teachersFile || loading}
              className="w-full"
            >
              <Upload className="mr-2 h-4 w-4" />
              {loading ? 'Importation...' : 'Importer les Enseignants'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Results */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Résultats de l'Importation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{results.details.total}</div>
                <div className="text-sm text-muted-foreground">Total</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{results.details.created}</div>
                <div className="text-sm text-muted-foreground">Créés</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{results.details.skipped}</div>
                <div className="text-sm text-muted-foreground">Ignorés</div>
              </div>
            </div>

            {results.details.errors.length > 0 && (
              <div className="space-y-2">
                <h3 className="font-semibold flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-orange-600" />
                  Erreurs/Avertissements
                </h3>
                <div className="bg-orange-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                  {results.details.errors.map((error: string, index: number) => (
                    <p key={index} className="text-sm text-orange-800">
                      • {error}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
