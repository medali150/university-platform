'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { classroomApi } from '@/lib/classroom-api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { 
  ArrowLeft, 
  Download, 
  ExternalLink, 
  FileText, 
  Calendar,
  User,
  Folder,
  Link as LinkIcon
} from 'lucide-react';

interface MaterialDetailProps {
  params: {
    id: string;
  };
}

export default function MaterialDetailPage({ params }: MaterialDetailProps) {
  const router = useRouter();
  const [material, setMaterial] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    loadMaterial();
  }, [params.id]);

  const loadMaterial = async () => {
    try {
      setLoading(true);
      console.log('🔍 Loading material with ID:', params.id);
      const data = await classroomApi.getMaterial(params.id);
      console.log('✅ Material loaded:', data);
      setMaterial(data);
    } catch (error) {
      console.error('❌ Failed to load material:', error);
      console.error('Error details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!material) return;

    try {
      setDownloading(true);
      
      if (material.type === 'link' && material.lienExterne) {
        // Open external link in new tab
        window.open(material.lienExterne, '_blank');
      } else if (material.fichierUrl) {
        // Download file
        const blob = await classroomApi.downloadMaterial(params.id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = material.titre || 'material';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to download:', error);
      alert('Échec du téléchargement');
    } finally {
      setDownloading(false);
    }
  };

  const handleOpenLink = () => {
    if (material?.lienExterne) {
      // Open external link directly
      window.open(material.lienExterne, '_blank');
    } else if (material?.fichierUrl) {
      // For files, use the download endpoint which will try to serve the file
      const downloadUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/classroom/materials/${params.id}/download`;
      window.open(downloadUrl, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!material) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">Matériel introuvable</h3>
            <p className="text-muted-foreground mb-4">
              Ce matériel n'existe pas ou a été supprimé
            </p>
            <Button onClick={() => router.back()}>
              Retour
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isLink = material.type === 'link';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex-1">
              <h1 className="text-2xl font-bold">{material.titre}</h1>
              <p className="text-sm text-muted-foreground mt-1">
                {isLink ? 'Lien externe' : 'Fichier'}
              </p>
            </div>
            <Button
              onClick={handleDownload}
              disabled={downloading}
              size="lg"
            >
              {isLink ? (
                <>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Ouvrir le lien
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  {downloading ? 'Téléchargement...' : 'Télécharger'}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Preview Card */}
            <Card>
              <CardHeader>
                <CardTitle>Aperçu</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-lg border-2 border-dashed">
                  {isLink ? (
                    <LinkIcon className="h-24 w-24 text-primary mx-auto mb-4" />
                  ) : (
                    <FileText className="h-24 w-24 text-primary mx-auto mb-4" />
                  )}
                  <div className="text-center">
                    <p className="font-medium text-lg mb-2">{material.titre}</p>
                    <p className="text-sm text-muted-foreground">
                      {isLink ? (
                        <>
                          <LinkIcon className="h-4 w-4 inline mr-1" />
                          Lien externe
                        </>
                      ) : (
                        <>
                          <FileText className="h-4 w-4 inline mr-1" />
                          Fichier disponible au téléchargement
                        </>
                      )}
                    </p>
                  </div>
                </div>

                {material.description && (
                  <div className="mt-6">
                    <h3 className="font-semibold mb-2">Description</h3>
                    <p className="text-muted-foreground whitespace-pre-wrap">
                      {material.description}
                    </p>
                  </div>
                )}

                {isLink && material.lienExterne && (
                  <div className="mt-6">
                    <h3 className="font-semibold mb-2">URL</h3>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 p-3 bg-gray-100 rounded-lg text-sm break-all">
                        {material.lienExterne}
                      </code>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => {
                          navigator.clipboard.writeText(material.lienExterne);
                          alert('Lien copié!');
                        }}
                      >
                        📋
                      </Button>
                    </div>
                  </div>
                )}

                {material.contenu && (
                  <div className="mt-6">
                    <h3 className="font-semibold mb-2">Contenu</h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm whitespace-pre-wrap">
                        {material.contenu}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full" 
                  size="lg"
                  onClick={handleDownload}
                  disabled={downloading}
                >
                  {isLink ? (
                    <>
                      <ExternalLink className="h-5 w-5 mr-2" />
                      Ouvrir dans un nouvel onglet
                    </>
                  ) : (
                    <>
                      <Download className="h-5 w-5 mr-2" />
                      {downloading ? 'Téléchargement en cours...' : 'Télécharger le fichier'}
                    </>
                  )}
                </Button>

                {(material.fichierUrl || material.lienExterne) && (
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={handleOpenLink}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Ouvrir dans un nouvel onglet
                  </Button>
                )}

                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => router.back()}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Retour au cours
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Details Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Détails</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Folder className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Type</p>
                    <p className="text-sm text-muted-foreground">
                      {isLink ? 'Lien externe' : 'Document'}
                    </p>
                  </div>
                </div>

                {material.dossier && (
                  <div className="flex items-start gap-3">
                    <Folder className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Dossier</p>
                      <p className="text-sm text-muted-foreground">
                        {material.dossier}
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Date d'ajout</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(material.createdAt).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>

                {material.enseignant && (
                  <div className="flex items-start gap-3">
                    <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Ajouté par</p>
                      <p className="text-sm text-muted-foreground">
                        {material.enseignant.prenom} {material.enseignant.nom}
                      </p>
                    </div>
                  </div>
                )}

                {material.tailleOctets && (
                  <div className="flex items-start gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Taille</p>
                      <p className="text-sm text-muted-foreground">
                        {(material.tailleOctets / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <div className="text-blue-600 text-2xl">ℹ️</div>
                  <div>
                    <h4 className="font-semibold text-blue-900 mb-1">
                      Besoin d'aide?
                    </h4>
                    <p className="text-sm text-blue-800">
                      {isLink ? (
                        "Le lien s'ouvrira dans un nouvel onglet. Assurez-vous que les pop-ups ne sont pas bloqués."
                      ) : (
                        "Le fichier sera téléchargé sur votre appareil. Vérifiez votre dossier de téléchargements."
                      )}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Assistant Promo */}
            <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-4xl mb-2">✨</div>
                  <h4 className="font-semibold mb-2">Assistant IA</h4>
                  <p className="text-sm text-muted-foreground mb-4">
                    Besoin d'aide pour comprendre ce contenu?
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push('/classroom/ai-assistant')}
                    className="w-full"
                  >
                    Demander à l'IA
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
