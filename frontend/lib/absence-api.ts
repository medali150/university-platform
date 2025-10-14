import { getAuthHeaders } from './api'

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// Types for Absence Management
export interface Absence {
  id: string
  studentId: string
  studentName: string
  className: string
  teacherName: string
  date: string
  startTime: string
  endTime: string
  reason: string
  status: string
  justificationText?: string
  reviewNotes?: string
  createdAt: string
}

export interface AbsenceStatistics {
  total: number
  justified: number
  unjustified: number
  pending: number
  absenceRate: number
}

// Simple Absence API using the actual backend endpoints
export const AbsenceAPI = {
  // Get student's absences
  async getStudentAbsences(): Promise<{ absences: Absence[]; statistics: AbsenceStatistics }> {
    try {
      // First get the current user to get student ID
      const userResponse = await fetch(`${BASE_URL}/auth/me`, {
        method: 'GET',
        headers: getAuthHeaders(),
      })

      if (!userResponse.ok) {
        throw new Error('Failed to get user info')
      }

      const userData = await userResponse.json()
      
      // Get student ID from the user data
      // The backend uses user.etudiant_id to link to the student
      if (!userData.etudiant_id) {
        throw new Error('Student ID not found')
      }

      // Now fetch absences using the student ID
      const response = await fetch(`${BASE_URL}/absences/student/${userData.etudiant_id}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error fetching student absences:', error)
      return {
        absences: [],
        statistics: {
          total: 0,
          justified: 0,
          unjustified: 0,
          pending: 0,
          absenceRate: 0
        }
      }
    }
  },

  // Justify an absence
  async justifyAbsence(absenceId: string, justificationText: string, files?: File[]): Promise<any> {
    try {
      const formData = new FormData()
      formData.append('justification_text', justificationText)
      
      if (files && files.length > 0) {
        files.forEach((file, index) => {
          formData.append(`files`, file)
        })
      }

      const headers = getAuthHeaders()
      delete headers['Content-Type'] // Let browser set it for FormData

      const response = await fetch(`${BASE_URL}/absences/${absenceId}/justify`, {
        method: 'PUT',
        headers,
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error justifying absence:', error)
      throw error
    }
  },

  // Get all absences for teachers/admins
  async getAllAbsences(filters: any = {}): Promise<{ absences: Absence[]; total: number }> {
    try {
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.page) params.append('page', filters.page.toString())
      if (filters.limit) params.append('limit', filters.limit.toString())

      const response = await fetch(`${BASE_URL}/absences/all?${params}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error fetching all absences:', error)
      return { absences: [], total: 0 }
    }
  },

  // Review an absence (approve/reject)
  async reviewAbsence(absenceId: string, action: 'approve' | 'reject', reviewNotes?: string): Promise<any> {
    try {
      const response = await fetch(`${BASE_URL}/absences/${absenceId}/review`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          action,
          review_notes: reviewNotes
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error reviewing absence:', error)
      throw error
    }
  },

  // Delete an absence
  async deleteAbsence(absenceId: string): Promise<any> {
    try {
      const response = await fetch(`${BASE_URL}/absences/${absenceId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error deleting absence:', error)
      throw error
    }
  },

  // Get absence statistics
  async getAbsenceStatistics(): Promise<any> {
    try {
      const response = await fetch(`${BASE_URL}/absences/statistics`, {
        method: 'GET',
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.error('Error fetching absence statistics:', error)
      return {}
    }
  }
}

// Utility functions
export const AbsenceUtils = {
  getStatusColor: (status: string): string => {
    switch (status.toLowerCase()) {
      case 'justified':
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'unjustified':
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'pending_review':
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  },

  getStatusIcon: (status: string): string => {
    switch (status.toLowerCase()) {
      case 'justified':
      case 'approved':
        return '✓'
      case 'unjustified':
      case 'rejected':
        return '✗'
      case 'pending_review':
      case 'pending':
        return '⏳'
      default:
        return '?'
    }
  },

  formatDate: (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('fr-FR')
    } catch {
      return dateString
    }
  },

  formatTime: (timeString: string): string => {
    if (timeString && timeString.length >= 5) {
      return timeString.substring(0, 5)
    }
    return timeString
  },

  getStatusText: (status: string): string => {
    switch (status.toLowerCase()) {
      case 'justified':
        return 'Justifiée'
      case 'unjustified':
        return 'Non justifiée'
      case 'pending_review':
      case 'pending':
        return 'En attente'
      case 'approved':
        return 'Approuvée'
      case 'rejected':
        return 'Rejetée'
      default:
        return status
    }
  },

  getStatusLabel: (status: string): string => {
    switch (status.toLowerCase()) {
      case 'justified':
        return 'Justifiée'
      case 'unjustified':
        return 'Non Justifiée'
      case 'pending_review':
        return 'En Attente'
      case 'pending':
        return 'En Attente'
      case 'approved':
        return 'Approuvée'
      case 'rejected':
        return 'Rejetée'
      default:
        return status
    }
  },

  canJustifyAbsence: (absence: Absence): boolean => {
    // Student can justify if absence is unjustified or rejected
    return absence.status === 'unjustified' || absence.status === 'rejected'
  }
}