'use client';

import { useState, useEffect } from 'react';
import { eventsApi, Event } from '@/lib/events-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Calendar, 
  MapPin, 
  Plus, 
  Edit, 
  Trash2,
  Save,
  X,
  MessageSquare,
  Heart,
  TrendingUp
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const EVENT_TYPES = {
  FORMATION: { label: 'Formation', color: 'bg-blue-500' },
  NEWS: { label: 'Actualités', color: 'bg-green-500' },
  ANNOUNCEMENT: { label: 'Annonce', color: 'bg-yellow-500' },
  EXAM: { label: 'Examen', color: 'bg-red-500' },
  OTHER: { label: 'Autre', color: 'bg-gray-500' }
};

interface EventForm {
  titre: string;
  type: string;
  description: string;
  date: string;
  lieu: string;
}

const emptyForm: EventForm = {
  titre: '',
  type: 'NEWS',
  description: '',
  date: '',
  lieu: ''
};

export default function ManageEventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<EventForm>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadEvents();
    loadStats();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await eventsApi.getEvents({});
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await eventsApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      
      if (editingId) {
        await eventsApi.updateEvent(editingId, formData);
      } else {
        await eventsApi.createEvent(formData);
      }
      
      setShowForm(false);
      setEditingId(null);
      setFormData(emptyForm);
      await loadEvents();
      await loadStats();
    } catch (error) {
      console.error('Failed to save event:', error);
      alert('Erreur lors de la sauvegarde de l\'événement');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (event: Event) => {
    setFormData({
      titre: event.titre,
      type: event.type,
      description: event.description || '',
      date: event.date ? format(new Date(event.date), "yyyy-MM-dd'T'HH:mm") : '',
      lieu: event.lieu || ''
    });
    setEditingId(event.id);
    setShowForm(true);
  };

  const handleDelete = async (eventId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet événement ?')) {
      return;
    }

    try {
      await eventsApi.deleteEvent(eventId);
      await loadEvents();
      await loadStats();
    } catch (error) {
      console.error('Failed to delete event:', error);
      alert('Erreur lors de la suppression de l\'événement');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData(emptyForm);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">📅 Gestion des Événements</h1>
          <p className="text-gray-600">
            Créez et gérez les événements, formations et actualités
          </p>
        </div>
        <Button onClick={() => setShowForm(true)} disabled={showForm}>
          <Plus className="h-4 w-4 mr-2" />
          Nouvel événement
        </Button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Événements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.totalEvents}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                À venir
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {stats.upcomingEvents}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Commentaires
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {stats.totalComments}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Réactions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {stats.totalReactions}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Event Form */}
      {showForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>
              {editingId ? 'Modifier l\'événement' : 'Nouvel événement'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Titre *</label>
                <Input
                  value={formData.titre}
                  onChange={(e) => setFormData({ ...formData, titre: e.target.value })}
                  placeholder="Formation Python Avancé"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Type *</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                >
                  {Object.entries(EVENT_TYPES).map(([value, { label }]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Détails de l'événement..."
                  rows={4}
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Date et heure *</label>
                  <Input
                    type="datetime-local"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Lieu</label>
                  <Input
                    value={formData.lieu}
                    onChange={(e) => setFormData({ ...formData, lieu: e.target.value })}
                    placeholder="Salle A201"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={submitting}>
                  <Save className="h-4 w-4 mr-2" />
                  {submitting ? 'Enregistrement...' : 'Enregistrer'}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  <X className="h-4 w-4 mr-2" />
                  Annuler
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Events List */}
      <div className="space-y-4">
        {events.map((event) => (
          <Card key={event.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={EVENT_TYPES[event.type as keyof typeof EVENT_TYPES]?.color || 'bg-gray-500'}>
                      {EVENT_TYPES[event.type as keyof typeof EVENT_TYPES]?.label || event.type}
                    </Badge>
                    <div className="flex gap-3 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{event.stats.commentsCount}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        <span>{event.stats.reactionsCount}</span>
                      </div>
                    </div>
                  </div>
                  <CardTitle className="mb-2">{event.titre}</CardTitle>
                  {event.date && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{format(new Date(event.date), 'PPP à HH:mm', { locale: fr })}</span>
                    </div>
                  )}
                  {event.lieu && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                      <MapPin className="h-4 w-4" />
                      <span>{event.lieu}</span>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(event)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(event.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            {event.description && (
              <CardContent>
                <p className="text-gray-600 whitespace-pre-wrap">{event.description}</p>
              </CardContent>
            )}
          </Card>
        ))}

        {events.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-600">Aucun événement créé</p>
            <Button className="mt-4" onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Créer le premier événement
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
