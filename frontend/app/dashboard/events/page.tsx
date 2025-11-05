'use client';

import { useState, useEffect } from 'react';
import { eventsApi, Event, EventComment } from '@/lib/events-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { 
  Calendar, 
  MapPin, 
  MessageSquare, 
  ThumbsUp, 
  Heart, 
  Eye, 
  CheckCircle, 
  XCircle,
  Plus,
  Search,
  AlertCircle
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

const REACTION_ICONS = {
  LIKE: { icon: ThumbsUp, label: 'J\'aime', color: 'text-blue-500' },
  LOVE: { icon: Heart, label: 'J\'adore', color: 'text-red-500' },
  INTERESTED: { icon: Eye, label: 'Intéressé', color: 'text-purple-500' },
  GOING: { icon: CheckCircle, label: 'Je participe', color: 'text-green-500' },
  NOT_GOING: { icon: XCircle, label: 'Absent', color: 'text-gray-500' }
};

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    loadEvents();
  }, [filter, user, router]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = {};
      
      if (filter !== 'all') {
        if (filter === 'upcoming') {
          params.upcoming = true;
        } else {
          params.type = filter;
        }
      }
      
      const data = await eventsApi.getEvents(params);
      setEvents(data);
    } catch (error: any) {
      console.error('Failed to load events:', error);
      setError(error.message || 'Erreur lors du chargement des événements');
    } finally {
      setLoading(false);
    }
  };

  const handleReaction = async (eventId: string, reactionType: 'LIKE' | 'LOVE' | 'INTERESTED' | 'GOING' | 'NOT_GOING') => {
    try {
      const event = events.find(e => e.id === eventId);
      if (!event) return;

      // If same reaction, remove it
      if (event.reactions.userReaction === reactionType) {
        await eventsApi.removeReaction(eventId);
      } else {
        await eventsApi.addReaction(eventId, reactionType);
      }

      // Reload event
      await loadEvents();
      if (selectedEvent?.id === eventId) {
        const updated = await eventsApi.getEvent(eventId);
        setSelectedEvent(updated);
      }
    } catch (error: any) {
      console.error('Failed to add reaction:', error);
      setError(error.message || 'Erreur lors de l\'ajout de la réaction');
    }
  };

  const handleAddComment = async (eventId: string) => {
    if (!commentText.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      await eventsApi.addComment(eventId, commentText);
      setCommentText('');

      // Reload event
      await loadEvents();
      if (selectedEvent?.id === eventId) {
        const updated = await eventsApi.getEvent(eventId);
        setSelectedEvent(updated);
      }
    } catch (error: any) {
      console.error('Failed to add comment:', error);
      setError(error.message || 'Erreur lors de l\'ajout du commentaire');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredEvents = events.filter(event =>
    event.titre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    event.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des événements...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6 max-w-7xl">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 p-6">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <div>
              <h3 className="font-semibold text-red-900">Erreur</h3>
              <p className="text-red-700">{error}</p>
            </div>
            <Button onClick={loadEvents} variant="outline" className="ml-auto">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">📅 Événements & Actualités</h1>
        <p className="text-gray-600">
          Découvrez les formations, actualités et annonces de votre département
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[300px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Rechercher un événement..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="all">Tous les événements</option>
          <option value="upcoming">À venir</option>
          <option value="FORMATION">Formations</option>
          <option value="NEWS">Actualités</option>
          <option value="ANNOUNCEMENT">Annonces</option>
          <option value="EXAM">Examens</option>
          <option value="OTHER">Autres</option>
        </select>
      </div>

      {/* Events Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredEvents.map((event) => (
          <Card
            key={event.id}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => setSelectedEvent(event)}
          >
            <CardHeader>
              <div className="flex items-start justify-between mb-2">
                <Badge className={EVENT_TYPES[event.type as keyof typeof EVENT_TYPES]?.color || 'bg-gray-500'}>
                  {EVENT_TYPES[event.type as keyof typeof EVENT_TYPES]?.label || event.type}
                </Badge>
                <div className="flex gap-2">
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <MessageSquare className="h-4 w-4" />
                    <span>{event.stats.commentsCount}</span>
                  </div>
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Heart className="h-4 w-4" />
                    <span>{event.stats.reactionsCount}</span>
                  </div>
                </div>
              </div>
              <CardTitle className="line-clamp-2">{event.titre}</CardTitle>
              {event.date && (
                <div className="flex items-center gap-2 text-sm text-gray-600 mt-2">
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
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 line-clamp-3">{event.description}</p>
              {event.creator && (
                <p className="text-sm text-gray-500 mt-3">
                  Par {event.creator.prenom} {event.creator.nom}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEvents.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-600">Aucun événement trouvé</p>
        </div>
      )}

      {/* Event Details Modal */}
      {selectedEvent && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedEvent(null)}
        >
          <Card
            className="max-w-3xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <ScrollArea className="h-full">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <Badge className={EVENT_TYPES[selectedEvent.type as keyof typeof EVENT_TYPES]?.color || 'bg-gray-500'}>
                    {EVENT_TYPES[selectedEvent.type as keyof typeof EVENT_TYPES]?.label || selectedEvent.type}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedEvent(null)}
                  >
                    ✕
                  </Button>
                </div>
                <CardTitle className="text-2xl">{selectedEvent.titre}</CardTitle>
                {selectedEvent.date && (
                  <div className="flex items-center gap-2 text-gray-600 mt-2">
                    <Calendar className="h-4 w-4" />
                    <span>{format(new Date(selectedEvent.date), 'PPP à HH:mm', { locale: fr })}</span>
                  </div>
                )}
                {selectedEvent.lieu && (
                  <div className="flex items-center gap-2 text-gray-600 mt-1">
                    <MapPin className="h-4 w-4" />
                    <span>{selectedEvent.lieu}</span>
                  </div>
                )}
              </CardHeader>

              <CardContent>
                <p className="text-gray-700 mb-6 whitespace-pre-wrap">{selectedEvent.description}</p>

                {/* Reactions */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Votre réaction</h3>
                  <div className="flex gap-2 flex-wrap">
                    {Object.entries(REACTION_ICONS).map(([type, { icon: Icon, label, color }]) => {
                      const isActive = selectedEvent.reactions.userReaction === type;
                      const count = selectedEvent.reactions.counts[type] || 0;
                      const reactionType = type as 'LIKE' | 'LOVE' | 'INTERESTED' | 'GOING' | 'NOT_GOING';
                      
                      return (
                        <Button
                          key={type}
                          variant={isActive ? "default" : "outline"}
                          size="sm"
                          onClick={() => handleReaction(selectedEvent.id, reactionType)}
                          className={isActive ? color : ''}
                        >
                          <Icon className="h-4 w-4 mr-1" />
                          {label}
                          {count > 0 && <span className="ml-2 text-xs">({count})</span>}
                        </Button>
                      );
                    })}
                  </div>
                </div>

                {/* Comments */}
                <div>
                  <h3 className="font-semibold mb-3">
                    Commentaires ({selectedEvent.comments.length})
                  </h3>

                  {/* Add comment */}
                  <div className="mb-4">
                    <Textarea
                      placeholder="Ajouter un commentaire..."
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      className="mb-2"
                      rows={3}
                    />
                    <Button
                      onClick={() => handleAddComment(selectedEvent.id)}
                      disabled={!commentText.trim() || submitting}
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      {submitting ? 'Envoi...' : 'Commenter'}
                    </Button>
                  </div>

                  {/* Comments list */}
                  <div className="space-y-4">
                    {selectedEvent.comments.map((comment) => (
                      <div key={comment.id} className="border-l-2 border-gray-200 pl-4">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm">
                            {comment.user.prenom} {comment.user.nom}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {comment.user.role}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {format(new Date(comment.createdAt), 'PPP à HH:mm', { locale: fr })}
                          </span>
                        </div>
                        <p className="text-gray-700">{comment.contenu}</p>
                      </div>
                    ))}

                    {selectedEvent.comments.length === 0 && (
                      <p className="text-gray-500 text-center py-4">
                        Aucun commentaire pour le moment
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </ScrollArea>
          </Card>
        </div>
      )}
    </div>
  );
}
