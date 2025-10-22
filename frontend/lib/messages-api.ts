/**
 * Messaging System API Client
 * 
 * Handles all messaging-related API calls between teachers and students
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface UserInfo {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  role: 'STUDENT' | 'TEACHER' | 'DEPARTMENT_HEAD' | 'ADMIN';
}

export interface Message {
  id: string;
  id_expediteur: string;
  id_destinataire: string;
  contenu: string;
  createdAt: string;
  expediteur: UserInfo;
  destinataire: UserInfo;
}

export interface Conversation {
  userId: string;
  user: UserInfo;
  lastMessage: {
    contenu: string;
    createdAt: string;
    isSent: boolean;
  };
  unreadCount: number;
}

export interface MessageStats {
  sent_messages: number;
  received_messages: number;
  total_conversations: number;
  unread_messages: number;
}

export interface SendMessageRequest {
  id_destinataire: string;
  contenu: string;
}

// ============================================================================
// API Client Class
// ============================================================================

class MessagesAPIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get authentication headers with token
   */
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Handle API response and errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  // ==========================================================================
  // Conversations
  // ==========================================================================

  /**
   * Get all conversations for current user
   * Returns list of users with last message and unread count
   */
  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${this.baseURL}/messages/conversations`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<Conversation[]>(response);
  }

  /**
   * Get all messages in a conversation with another user
   * Returns messages in chronological order
   */
  async getConversationMessages(otherUserId: string): Promise<Message[]> {
    const response = await fetch(
      `${this.baseURL}/messages/conversation/${otherUserId}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse<Message[]>(response);
  }

  // ==========================================================================
  // Send Messages
  // ==========================================================================

  /**
   * Send a new message to another user
   * 
   * @param receiverId - ID of the user to send message to
   * @param content - Message content
   * @returns The created message
   */
  async sendMessage(receiverId: string, content: string): Promise<Message> {
    const response = await fetch(`${this.baseURL}/messages/send`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        id_destinataire: receiverId,
        contenu: content
      })
    });
    return this.handleResponse<Message>(response);
  }

  // ==========================================================================
  // User Search
  // ==========================================================================

  /**
   * Search for users to start a conversation with
   * 
   * @param query - Search query (minimum 2 characters)
   * @param role - Optional role filter (TEACHER or STUDENT)
   * @returns List of matching users
   */
  async searchUsers(query: string, role?: 'TEACHER' | 'STUDENT'): Promise<UserInfo[]> {
    const params = new URLSearchParams({ query });
    if (role) params.append('role', role);
    
    const response = await fetch(
      `${this.baseURL}/messages/users/search?${params}`,
      { headers: this.getHeaders() }
    );
    return this.handleResponse<UserInfo[]>(response);
  }

  // ==========================================================================
  // Message Management
  // ==========================================================================

  /**
   * Delete a message (only sender can delete)
   */
  async deleteMessage(messageId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/messages/${messageId}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
    await this.handleResponse<{ message: string }>(response);
  }

  // ==========================================================================
  // Statistics
  // ==========================================================================

  /**
   * Get count of unread messages
   */
  async getUnreadCount(): Promise<number> {
    const response = await fetch(`${this.baseURL}/messages/unread-count`, {
      headers: this.getHeaders()
    });
    const data = await this.handleResponse<{ unread_count: number }>(response);
    return data.unread_count;
  }

  /**
   * Get messaging statistics for current user
   */
  async getStats(): Promise<MessageStats> {
    const response = await fetch(`${this.baseURL}/messages/stats`, {
      headers: this.getHeaders()
    });
    return this.handleResponse<MessageStats>(response);
  }

  // ==========================================================================
  // Utility Functions
  // ==========================================================================

  /**
   * Format user's full name
   */
  static formatUserName(user: UserInfo): string {
    return `${user.prenom} ${user.nom}`;
  }

  /**
   * Format message timestamp for display
   */
  static formatMessageTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60);
      return `Il y a ${minutes} min`;
    } else if (diffInHours < 24) {
      return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 48) {
      return 'Hier';
    } else {
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    }
  }

  /**
   * Get role badge color
   */
  static getRoleBadgeColor(role: string): string {
    switch (role) {
      case 'TEACHER':
        return 'bg-blue-100 text-blue-800';
      case 'STUDENT':
        return 'bg-green-100 text-green-800';
      case 'DEPARTMENT_HEAD':
        return 'bg-purple-100 text-purple-800';
      case 'ADMIN':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  /**
   * Get role display name in French
   */
  static getRoleDisplayName(role: string): string {
    switch (role) {
      case 'TEACHER':
        return 'Enseignant';
      case 'STUDENT':
        return 'Étudiant';
      case 'DEPARTMENT_HEAD':
        return 'Chef de Département';
      case 'ADMIN':
        return 'Administrateur';
      default:
        return role;
    }
  }
}

// ============================================================================
// Export singleton instance and class
// ============================================================================

export { MessagesAPIClient };
export const MessagesAPI = new MessagesAPIClient();
export default MessagesAPI;
