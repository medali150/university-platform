'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Upload, X, User, Camera } from 'lucide-react';
import { TeacherAPI } from '@/lib/teacher-api';

interface ImageUploadProps {
  currentImageUrl?: string;
  teacherName: string;
  onImageUpdate: (imageUrl: string | null) => void;
}

export function ImageUploadComponent({ currentImageUrl, teacherName, onImageUpdate }: ImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentImageUrl || null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Veuillez sélectionner un fichier image');
      return;
    }

    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      toast.error('La taille du fichier ne doit pas dépasser 5MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload file
    handleUpload(file);
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const result = await TeacherAPI.uploadImage(file);
      
      if (result.success && result.image_url) {
        setPreviewUrl(result.image_url);
        onImageUpdate(result.image_url);
        toast.success('Photo de profil mise à jour avec succès');
      } else {
        toast.error(result.message || 'Erreur lors du téléchargement');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Erreur lors du téléchargement de l\'image');
      // Reset preview on error
      setPreviewUrl(currentImageUrl || null);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await TeacherAPI.deleteImage();
      setPreviewUrl(null);
      onImageUpdate(null);
      toast.success('Photo de profil supprimée');
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Erreur lors de la suppression de l\'image');
    } finally {
      setIsDeleting(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="h-5 w-5" />
          Photo de Profil
        </CardTitle>
        <CardDescription>
          Téléchargez votre photo de profil (JPG, PNG - max 5MB)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col items-center space-y-4">
          {/* Avatar Preview */}
          <div className="relative">
            <Avatar className="h-32 w-32">
              <AvatarImage 
                src={previewUrl || undefined} 
                alt={teacherName}
                className="object-cover"
              />
              <AvatarFallback className="text-2xl">
                {getInitials(teacherName)}
              </AvatarFallback>
            </Avatar>
            
            {/* Upload Status Overlay */}
            {isUploading && (
              <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              </div>
            )}
          </div>

          {/* Upload Status */}
          {isUploading && (
            <Badge variant="secondary" className="animate-pulse">
              Téléchargement en cours...
            </Badge>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button
              onClick={triggerFileInput}
              disabled={isUploading || isDeleting}
              className="flex items-center gap-2"
              variant="outline"
            >
              <Upload className="h-4 w-4" />
              {previewUrl ? 'Changer' : 'Télécharger'}
            </Button>

            {previewUrl && (
              <Button
                onClick={handleDelete}
                disabled={isUploading || isDeleting}
                variant="destructive"
                size="sm"
                className="flex items-center gap-2"
              >
                <X className="h-4 w-4" />
                {isDeleting ? 'Suppression...' : 'Supprimer'}
              </Button>
            )}
          </div>

          {/* Hidden File Input */}
          <Input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            disabled={isUploading || isDeleting}
          />

          {/* Help Text */}
          <p className="text-sm text-muted-foreground text-center">
            Formats acceptés: JPG, PNG, GIF<br />
            Taille maximale: 5MB<br />
            Recommandé: 400x400 pixels
          </p>
        </div>
      </CardContent>
    </Card>
  );
}