/**
 * Makeup Sessions API Client
 * Handles all API calls for makeup sessions (rattrapage) management
 */

import { API_BASE_URL } from "./api";

// ============================================================================
// TYPES
// ============================================================================

export type MakeupStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "SCHEDULED"
  | "COMPLETED"
  | "CANCELLED";

export interface MakeupSession {
  id: string;
  subject: {
    id: string;
    nom: string;
  };
  teacher: {
    id: string;
    nom: string;
    prenom: string;
    fullName: string;
  };
  group: {
    id: string;
    nom: string;
  };
  room: {
    id: string;
    code: string;
    capacite: number;
  } | null;
  originalDate: string; // ISO date
  originalStartTime: string; // HH:MM
  originalEndTime: string; // HH:MM
  proposedDate: string; // ISO date
  proposedStartTime: string; // HH:MM
  proposedEndTime: string; // HH:MM
  reason: string;
  status: MakeupStatus;
  validationNotes: string | null;
  createdBy: string;
  validatedBy: string | null;
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
  studentCount: number;
}

export interface CreateMakeupSession {
  id_emploitemps_origin: string;
  id_matiere: string;
  id_enseignant: string;
  id_groupe: string;
  id_salle?: string;
  date_originale: string; // ISO date
  heure_debut_origin: string; // HH:MM
  heure_fin_origin: string; // HH:MM
  date_proposee: string; // ISO date
  heure_debut_proposee: string; // HH:MM
  heure_fin_proposee: string; // HH:MM
  motif: string;
}

export interface UpdateMakeupSession {
  date_proposee?: string;
  heure_debut_proposee?: string;
  heure_fin_proposee?: string;
  id_salle?: string;
  motif?: string;
}

export interface ReviewMakeupSession {
  statut: "APPROVED" | "REJECTED";
  notes_validation?: string;
}

export interface MakeupStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  scheduled: number;
  completed: number;
  uniqueStudents: number;
}

export interface MakeupFilters {
  status?: MakeupStatus;
  teacher_id?: string;
  group_id?: string;
  from_date?: string; // ISO date
  to_date?: string; // ISO date
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

/**
 * Get all makeup sessions with optional filters
 */
export async function getMakeupSessions(
  filters?: MakeupFilters
): Promise<MakeupSession[]> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const params = new URLSearchParams();
  if (filters?.status) params.append("status", filters.status);
  if (filters?.teacher_id) params.append("teacher_id", filters.teacher_id);
  if (filters?.group_id) params.append("group_id", filters.group_id);
  if (filters?.from_date) params.append("from_date", filters.from_date);
  if (filters?.to_date) params.append("to_date", filters.to_date);

  const queryString = params.toString();
  const url = `${API_BASE_URL}/makeup-sessions/${
    queryString ? `?${queryString}` : ""
  }`;

  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch makeup sessions");
  }

  return response.json();
}

/**
 * Get a specific makeup session by ID
 */
export async function getMakeupSession(
  sessionId: string
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch makeup session");
  }

  return response.json();
}

/**
 * Create a new makeup session
 */
export async function createMakeupSession(
  sessionData: CreateMakeupSession
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(`${API_BASE_URL}/makeup-sessions/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(sessionData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create makeup session");
  }

  return response.json();
}

/**
 * Update a makeup session
 */
export async function updateMakeupSession(
  sessionId: string,
  sessionData: UpdateMakeupSession
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sessionData),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update makeup session");
  }

  return response.json();
}

/**
 * Review a makeup session (approve or reject)
 */
export async function reviewMakeupSession(
  sessionId: string,
  reviewData: ReviewMakeupSession
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}/review`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(reviewData),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to review makeup session");
  }

  return response.json();
}

/**
 * Schedule an approved makeup session
 */
export async function scheduleMakeupSession(
  sessionId: string
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}/schedule`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to schedule makeup session");
  }

  return response.json();
}

/**
 * Mark a scheduled session as completed
 */
export async function completeMakeupSession(
  sessionId: string
): Promise<MakeupSession> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}/complete`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to complete makeup session");
  }

  return response.json();
}

/**
 * Delete a makeup session
 */
export async function deleteMakeupSession(sessionId: string): Promise<void> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/${sessionId}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete makeup session");
  }
}

/**
 * Get makeup session statistics
 */
export async function getMakeupStats(): Promise<MakeupStats> {
  const token = getAuthToken();
  if (!token) throw new Error("No authentication token found");

  const response = await fetch(
    `${API_BASE_URL}/makeup-sessions/stats/summary`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch makeup statistics");
  }

  return response.json();
}

/**
 * Format date for display
 */
export function formatMakeupDate(dateStr: string): string {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("fr-FR", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

/**
 * Format time for display
 */
export function formatMakeupTime(timeStr: string): string {
  return timeStr;
}

/**
 * Get status badge color
 */
export function getStatusColor(status: MakeupStatus): string {
  switch (status) {
    case "PENDING":
      return "bg-yellow-500";
    case "APPROVED":
      return "bg-green-500";
    case "REJECTED":
      return "bg-red-500";
    case "SCHEDULED":
      return "bg-blue-500";
    case "COMPLETED":
      return "bg-purple-500";
    case "CANCELLED":
      return "bg-gray-500";
    default:
      return "bg-gray-500";
  }
}

/**
 * Get status label in French
 */
export function getStatusLabel(status: MakeupStatus): string {
  switch (status) {
    case "PENDING":
      return "En attente";
    case "APPROVED":
      return "Approuvée";
    case "REJECTED":
      return "Rejetée";
    case "SCHEDULED":
      return "Programmée";
    case "COMPLETED":
      return "Terminée";
    case "CANCELLED":
      return "Annulée";
    default:
      return status;
  }
}
