import { api } from '@/lib/api'
import { Subject, Level } from '@/types/api'

export interface SubjectsListResponse {
  subjects: Subject[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface Teacher {
  id: string
  user: {
    id: string
    prenom: string
    nom: string
    email: string
  }
  department: {
    id: string
    name: string
  }
}

export interface LevelWithRelations {
  id: string
  name: string
  specialty: {
    id: string
    name: string
    department: {
      id: string
      name: string
    }
  }
}

export class SubjectsAPI {
  // Get subjects with pagination and filters
  static async getSubjects(params: {
    page?: number
    pageSize?: number
    search?: string
    levelId?: string
    teacherId?: string
  } = {}): Promise<SubjectsListResponse> {
    try {
      const response = await api.getSubjects({
        page: params.page || 1,
        pageSize: params.pageSize || 10,
        search: params.search,
        levelId: params.levelId,
        teacherId: params.teacherId
      })
      return response as unknown as SubjectsListResponse
    } catch (error) {
      console.error('Error fetching subjects:', error)
      throw error
    }
  }

  // Get single subject by ID
  static async getSubject(id: string): Promise<Subject> {
    try {
      return await api.getSubject(id) as unknown as Subject
    } catch (error) {
      console.error('Error fetching subject:', error)
      throw error
    }
  }

  // Create new subject
  static async createSubject(subjectData: {
    name: string
    levelId: string
    teacherId: string
  }): Promise<Subject> {
    try {
      return await api.createSubject(subjectData) as unknown as Subject
    } catch (error) {
      console.error('Error creating subject:', error)
      throw error
    }
  }

  // Update subject
  static async updateSubject(
    id: string, 
    subjectData: {
      name?: string
      levelId?: string
      teacherId?: string
    }
  ): Promise<Subject> {
    try {
      return await api.updateSubject(id, subjectData) as unknown as Subject
    } catch (error) {
      console.error('Error updating subject:', error)
      throw error
    }
  }

  // Delete subject
  static async deleteSubject(id: string): Promise<void> {
    try {
      await api.deleteSubject(id)
    } catch (error) {
      console.error('Error deleting subject:', error)
      throw error
    }
  }

  // Get helper data for subject creation/editing
  static async getHelperData(): Promise<{
    levels: LevelWithRelations[]
    teachers: Teacher[]
  }> {
    try {
      return await api.getSubjectHelperData() as unknown as {
        levels: LevelWithRelations[]
        teachers: Teacher[]
      }
    } catch (error) {
      console.error('Error fetching helper data:', error)
      throw error
    }
  }

  // Get subject statistics
  static async getSubjectStats(): Promise<{
    totalSubjects: number
    byLevel: { levelName: string; count: number }[]
    byDepartment: { departmentName: string; count: number }[]
    byTeacher: { teacherName: string; count: number }[]
  }> {
    try {
      const response = await this.getSubjects({ pageSize: 1000 }) // Get all for stats
      const subjects = response.subjects

      const totalSubjects = subjects.length
      
      // Group by level
      const levelCounts = subjects.reduce((acc, subject) => {
        const levelName = subject.level?.name || 'Non spécifié'
        acc[levelName] = (acc[levelName] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Group by department
      const departmentCounts = subjects.reduce((acc, subject) => {
        const departmentName = subject.level?.specialty?.department?.name || 'Non spécifié'
        acc[departmentName] = (acc[departmentName] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      // Group by teacher
      const teacherCounts = subjects.reduce((acc, subject) => {
        const teacherName = subject.teacher?.user ? 
          `${subject.teacher.user.prenom} ${subject.teacher.user.nom}` : 
          'Non assigné'
        acc[teacherName] = (acc[teacherName] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      return {
        totalSubjects,
        byLevel: Object.entries(levelCounts).map(([levelName, count]) => ({ levelName, count })),
        byDepartment: Object.entries(departmentCounts).map(([departmentName, count]) => ({ departmentName, count })),
        byTeacher: Object.entries(teacherCounts).map(([teacherName, count]) => ({ teacherName, count }))
      }
    } catch (error) {
      console.error('Error fetching subject stats:', error)
      // Return mock data if API fails
      return {
        totalSubjects: 0,
        byLevel: [],
        byDepartment: [],
        byTeacher: []
      }
    }
  }
}