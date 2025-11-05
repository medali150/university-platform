/**
 * Events & News API Client
 * Handles all API calls for events, comments, and reactions
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ===========================
// TYPES
// ===========================

export interface UserInfo {
  id: string;
  nom: string;
  prenom: string;
  role: string;
}

export interface EventComment {
  id: string;
  contenu: string;
  createdAt: string;
  user: UserInfo;
}

export interface EventReactionCounts {
  [key: string]: number;
}

export interface EventReactions {
  counts: EventReactionCounts;
  total: number;
  userReaction: string | null;
}

export interface Event {
  id: string;
  titre: string;
  type: string;
  description: string | null;
  date: string | null;
  lieu: string | null;
  createdAt: string;
  updatedAt: string;
  creator: UserInfo | null;
  comments: EventComment[];
  reactions: EventReactions;
  stats: {
    commentsCount: number;
    reactionsCount: number;
  };
}

export interface EventCreateData {
  titre: string;
  type: string;
  description?: string;
  date: string;
  lieu?: string;
}

export interface EventUpdateData {
  titre?: string;
  type?: string;
  description?: string;
  date?: string;
  lieu?: string;
}

export interface EventStats {
  totalEvents: number;
  upcomingEvents: number;
  totalComments: number;
  totalReactions: number;
  eventsByType: { [key: string]: number };
}

// ===========================
// API CLIENT
// ===========================

class EventsAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE) {
    this.baseURL = baseURL;
  }

  /**
   * Get authorization token from localStorage
   */
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('authToken') || localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  /**
   * Handle API response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  }

  // ===========================
  // EVENTS ENDPOINTS
  // ===========================

  /**
   * Get all events with optional filters
   */
  async getEvents(params?: {
    type?: string;
    upcoming?: boolean;
    limit?: number;
  }): Promise<Event[]> {
    const queryParams = new URLSearchParams();
    if (params?.type) queryParams.append('type', params.type);
    if (params?.upcoming !== undefined) queryParams.append('upcoming', String(params.upcoming));
    if (params?.limit) queryParams.append('limit', String(params.limit));

    const url = `${this.baseURL}/events/?${queryParams.toString()}`;
    const response = await fetch(url, {
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<Event[]>(response);
  }

  /**
   * Get a single event by ID
   */
  async getEvent(eventId: string): Promise<Event> {
    const response = await fetch(`${this.baseURL}/events/${eventId}`, {
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<Event>(response);
  }

  /**
   * Create a new event (Department heads only)
   */
  async createEvent(data: EventCreateData): Promise<Event> {
    const response = await fetch(`${this.baseURL}/events/`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<Event>(response);
  }

  /**
   * Update an event (Creator only)
   */
  async updateEvent(eventId: string, data: EventUpdateData): Promise<Event> {
    const response = await fetch(`${this.baseURL}/events/${eventId}`, {
      method: 'PUT',
      headers: this.getAuthHeader(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<Event>(response);
  }

  /**
   * Delete an event (Creator only)
   */
  async deleteEvent(eventId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/events/${eventId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<{ message: string }>(response);
  }

  // ===========================
  // COMMENTS ENDPOINTS
  // ===========================

  /**
   * Add a comment to an event
   */
  async addComment(eventId: string, contenu: string): Promise<EventComment> {
    const response = await fetch(`${this.baseURL}/events/${eventId}/comments`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify({ contenu }),
    });

    return this.handleResponse<EventComment>(response);
  }

  /**
   * Delete a comment (Author or department head only)
   */
  async deleteComment(eventId: string, commentId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/events/${eventId}/comments/${commentId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<{ message: string }>(response);
  }

  // ===========================
  // REACTIONS ENDPOINTS
  // ===========================

  /**
   * Add or update a reaction to an event
   */
  async addReaction(
    eventId: string,
    type: 'LIKE' | 'LOVE' | 'INTERESTED' | 'GOING' | 'NOT_GOING'
  ): Promise<{
    message: string;
    userReaction: string;
    counts: EventReactionCounts;
    total: number;
  }> {
    const response = await fetch(`${this.baseURL}/events/${eventId}/reactions`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify({ type }),
    });

    return this.handleResponse(response);
  }

  /**
   * Remove user's reaction from an event
   */
  async removeReaction(eventId: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/events/${eventId}/reactions`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<{ message: string }>(response);
  }

  // ===========================
  // STATISTICS ENDPOINTS
  // ===========================

  /**
   * Get events statistics (Department heads only)
   */
  async getStats(): Promise<EventStats> {
    const response = await fetch(`${this.baseURL}/events/stats/summary`, {
      headers: this.getAuthHeader(),
    });

    return this.handleResponse<EventStats>(response);
  }
}

// Export singleton instance
export const eventsApi = new EventsAPI();
