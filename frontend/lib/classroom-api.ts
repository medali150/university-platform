/**
 * Smart Classroom API Client
 * Handles all API calls for Google Classroom-like features
 * - Courses
 * - Assignments
 * - Materials
 * - Announcements
 * - Discussions
 * - AI Features
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ========================================
// TYPE DEFINITIONS
// ========================================

export interface Course {
  id: string;
  code: string;              // Course code like "BIGDA257-20252026-S1"
  nom: string;               // Course name
  description?: string;
  id_enseignant: string;     // Teacher ID
  anneeAcademique: string;   // "2024-2025"
  semestre: string;          // "S1" or "S2"
  couleur: string;           // Color theme
  codeInvitation?: string;   // Invite code for students
  estActif: boolean;
  estPublic: boolean;
  imageUrl?: string;
  capaciteMax?: number;
  dateDebut?: string;
  dateFin?: string;
  createdAt: string;
  updatedAt: string;
  enseignant?: any;          // Teacher with utilisateur nested
  nbEtudiants?: number;
  nbDevoirs?: number;
  nbMateriaux?: number;
}

export interface CourseCreate {
  nom: string;
  description?: string;
  anneeAcademique: string;  // "2024-2025"
  semestre: string;          // "S1" or "S2"
  couleur?: string;
  estPublic?: boolean;
  id_departement?: string;
  id_specialite?: string;
  id_niveau?: string;
  imageUrl?: string;
  capaciteMax?: number;
  dateDebut?: string;
  dateFin?: string;
}

export interface Assignment {
  id: string;
  courseId: string;
  title: string;
  description?: string;
  dueDate?: string;
  points?: number;
  status: 'DRAFT' | 'PUBLISHED' | 'CLOSED';
  allowLateSubmission: boolean;
  attachments?: string[];
  createdAt: string;
  updatedAt: string;
  course?: Course;
  submissionsCount?: number;
  gradedCount?: number;
}

export interface AssignmentCreate {
  title: string;
  description?: string;
  dueDate?: string;
  points?: number;
  status?: 'DRAFT' | 'PUBLISHED' | 'CLOSED';
  allowLateSubmission?: boolean;
  attachments?: string[];
}

export interface Submission {
  id: string;
  assignmentId: string;
  studentId: string;
  content?: string;
  attachments?: string[];
  status: 'DRAFT' | 'SUBMITTED' | 'GRADED' | 'RETURNED';
  grade?: number;
  feedback?: string;
  submittedAt?: string;
  gradedAt?: string;
  createdAt: string;
  updatedAt: string;
  student?: User;
  assignment?: Assignment;
}

export interface PlagiarismResult {
  is_plagiarized: boolean;
  similarity_score: number;
  matched_submissions?: Array<{
    id: string;
    student_name: string;
    similarity: number;
  }>;
  details?: string;
}

export interface AIFeedback {
  feedback: string;
  strengths?: string[];
  improvements?: string[];
  grade_suggestion?: number;
}

export interface SubmissionCreate {
  content?: string;
  attachments?: string[];
  status?: 'DRAFT' | 'SUBMITTED';
}

export interface Announcement {
  id: string;
  courseId: string;
  teacherId: string;
  content: string;
  attachments?: string[];
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
  teacher?: User;
  course?: Course;
  commentsCount?: number;
}

export interface AnnouncementCreate {
  content: string;
  attachments?: string[];
  isPinned?: boolean;
}

export interface Discussion {
  id: string;
  courseId: string;
  authorId: string;
  title: string;
  content: string;
  isPinned: boolean;
  isResolved: boolean;
  createdAt: string;
  updatedAt: string;
  author?: User;
  course?: Course;
  repliesCount?: number;
}

export interface DiscussionCreate {
  title: string;
  content: string;
  isPinned?: boolean;
}

export interface Material {
  id: string;
  courseId: string;
  title: string;
  description?: string;
  fileUrl?: string;
  fileType?: string;
  fileSize?: number;
  folderId?: string;
  createdAt: string;
  updatedAt: string;
  course?: Course;
  folder?: MaterialFolder;
}

export interface MaterialCreate {
  title: string;
  description?: string;
  fileUrl?: string;
  fileType?: string;
  fileSize?: number;
  folderId?: string;
}

export interface MaterialFolder {
  id: string;
  courseId: string;
  name: string;
  parentId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: string;
  email: string;
  prenom: string;
  nom: string;
  role: string;
}

export interface CourseEnrollment {
  id: string;
  courseId: string;
  studentId: string;
  enrolledAt: string;
  student?: User;
}

export interface CourseAnalytics {
  enrollmentCount: number;
  assignmentCount: number;
  submissionRate: number;
  averageGrade: number;
  activeStudents: number;
}

// PlagiarismResult and AIFeedback interfaces moved up near Submission

// ========================================
// API CLIENT CLASS
// ========================================

class SmartClassroomAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeaders(): Record<string, string> {
    // Use 'authToken' key to match the auth system
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    console.log(`🌐 API Request: ${options?.method || 'GET'} ${url}`);
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options?.headers,
      },
    });

    console.log(`📡 API Response: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.error(`❌ API Error:`, error);
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log(`✅ API Data:`, data);
    return data;
  }

  // ========================================
  // COURSE ENDPOINTS
  // ========================================

  async getCourses(includeArchived = false): Promise<Course[]> {
    return this.request<Course[]>(
      `/api/classroom/courses?include_archived=${includeArchived}`
    );
  }

  async getCourse(courseId: string): Promise<Course> {
    return this.request<Course>(`/api/classroom/courses/${courseId}`);
  }

  async createCourse(data: CourseCreate): Promise<Course> {
    return this.request<Course>('/api/classroom/courses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCourse(courseId: string, data: Partial<CourseCreate>): Promise<Course> {
    return this.request<Course>(`/api/classroom/courses/${courseId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCourse(courseId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/courses/${courseId}`, {
      method: 'DELETE',
    });
  }

  async findCourseByInviteCode(inviteCode: string): Promise<Course> {
    return this.request<Course>(`/api/classroom/courses/search/by-code/${inviteCode.toUpperCase()}`);
  }

  async enrollInCourse(courseId: string, inviteCode?: string): Promise<any> {
    const url = inviteCode 
      ? `/api/classroom/courses/${courseId}/join?code=${encodeURIComponent(inviteCode)}`
      : `/api/classroom/courses/${courseId}/join`;
    
    return this.request<any>(url, {
      method: 'POST',
    });
  }

  async unenrollStudent(courseId: string, studentId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/courses/${courseId}/enroll/${studentId}`, {
      method: 'DELETE',
    });
  }

  async getCourseStudents(courseId: string): Promise<CourseEnrollment[]> {
    return this.request<CourseEnrollment[]>(`/api/classroom/courses/${courseId}/students`);
  }

  async getCourseAnalytics(courseId: string): Promise<CourseAnalytics> {
    return this.request<CourseAnalytics>(`/api/classroom/courses/${courseId}/analytics`);
  }

  async copyCourse(courseId: string, newName?: string): Promise<Course> {
    return this.request<Course>(`/api/classroom/courses/${courseId}/copy`, {
      method: 'POST',
      body: JSON.stringify({ newName }),
    });
  }

  async archiveCourse(courseId: string, archive = true): Promise<Course> {
    return this.request<Course>(`/api/classroom/courses/${courseId}/archive`, {
      method: 'PUT',
      body: JSON.stringify({ archive }),
    });
  }

  // ========================================
  // ASSIGNMENT ENDPOINTS
  // ========================================

  async getAssignments(courseId: string, status?: string): Promise<Assignment[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<Assignment[]>(`/api/classroom/courses/${courseId}/assignments${query}`);
  }

  async getAssignment(assignmentId: string): Promise<Assignment> {
    return this.request<Assignment>(`/api/classroom/assignments/${assignmentId}`);
  }

  async createAssignment(courseId: string, data: AssignmentCreate): Promise<Assignment> {
    return this.request<Assignment>(`/api/classroom/courses/${courseId}/assignments`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAssignment(assignmentId: string, data: Partial<AssignmentCreate>): Promise<Assignment> {
    return this.request<Assignment>(`/api/classroom/assignments/${assignmentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAssignment(assignmentId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/assignments/${assignmentId}`, {
      method: 'DELETE',
    });
  }

  async submitAssignment(assignmentId: string, data: SubmissionCreate): Promise<Submission> {
    return this.request<Submission>(`/api/classroom/assignments/${assignmentId}/submit`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSubmissions(assignmentId: string): Promise<Submission[]> {
    return this.request<Submission[]>(`/api/classroom/assignments/${assignmentId}/submissions`);
  }

  async gradeSubmission(
    submissionId: string,
    grade: number,
    feedback?: string
  ): Promise<Submission> {
    return this.request<Submission>(`/api/classroom/submissions/${submissionId}/grade`, {
      method: 'PUT',
      body: JSON.stringify({ grade, feedback }),
    });
  }

  // ========================================
  // ANNOUNCEMENT ENDPOINTS
  // ========================================

  async getAnnouncements(courseId: string): Promise<Announcement[]> {
    return this.request<Announcement[]>(`/api/classroom/courses/${courseId}/announcements`);
  }

  async createAnnouncement(courseId: string, data: AnnouncementCreate): Promise<Announcement> {
    return this.request<Announcement>(`/api/classroom/courses/${courseId}/announcements`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAnnouncement(announcementId: string, data: Partial<AnnouncementCreate>): Promise<Announcement> {
    return this.request<Announcement>(`/api/classroom/announcements/${announcementId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAnnouncement(announcementId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/announcements/${announcementId}`, {
      method: 'DELETE',
    });
  }

  // ========================================
  // DISCUSSION ENDPOINTS
  // ========================================

  async getDiscussions(courseId: string): Promise<Discussion[]> {
    return this.request<Discussion[]>(`/api/classroom/courses/${courseId}/discussions`);
  }

  async getDiscussion(discussionId: string): Promise<Discussion> {
    return this.request<Discussion>(`/api/classroom/discussions/${discussionId}`);
  }

  async createDiscussion(courseId: string, data: DiscussionCreate): Promise<Discussion> {
    return this.request<Discussion>(`/api/classroom/courses/${courseId}/discussions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateDiscussion(discussionId: string, data: Partial<DiscussionCreate>): Promise<Discussion> {
    return this.request<Discussion>(`/api/classroom/discussions/${discussionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteDiscussion(discussionId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/discussions/${discussionId}`, {
      method: 'DELETE',
    });
  }

  // ========================================
  // MATERIAL ENDPOINTS
  // ========================================

  async getMaterials(courseId: string): Promise<Material[]> {
    return this.request<Material[]>(`/api/classroom/courses/${courseId}/materials`);
  }

  async getMaterial(materialId: string): Promise<Material> {
    return this.request<Material>(`/api/classroom/materials/${materialId}`);
  }

  async createMaterial(courseId: string, data: MaterialCreate): Promise<Material> {
    return this.request<Material>(`/api/classroom/courses/${courseId}/materials`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async uploadMaterialFile(
    courseId: string,
    file: File,
    titre?: string,
    description?: string
  ): Promise<Material> {
    const token = localStorage.getItem('authToken');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', courseId);
    if (titre) formData.append('titre', titre);
    if (description) formData.append('description', description);

    const response = await fetch(`${this.baseUrl}/api/classroom/materials/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async updateMaterial(materialId: string, data: Partial<MaterialCreate>): Promise<Material> {
    return this.request<Material>(`/api/classroom/materials/${materialId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteMaterial(materialId: string): Promise<{ message: string }> {
    return this.request(`/api/classroom/materials/${materialId}`, {
      method: 'DELETE',
    });
  }

  async downloadMaterial(materialId: string): Promise<Blob> {
    // Use 'authToken' key to match the auth system
    const token = localStorage.getItem('authToken');
    const response = await fetch(`${this.baseUrl}/api/classroom/materials/${materialId}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!response.ok) {
      throw new Error('Failed to download material');
    }

    return response.blob();
  }

  // ========================================
  // AI ENDPOINTS
  // ========================================

  async chatWithAI(message: string, context?: string, courseId?: string): Promise<{ response: string }> {
    return this.request<{ response: string }>('/api/classroom/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context, courseId }),
    });
  }

  async checkPlagiarism(
    assignmentId: string,
    content: string
  ): Promise<PlagiarismResult> {
    return this.request<PlagiarismResult>('/api/classroom/ai/plagiarism/check', {
      method: 'POST',
      body: JSON.stringify({ assignmentId, content }),
    });
  }

  async generateFeedback(
    assignmentTitle: string,
    submissionContent: string,
    rubric?: string
  ): Promise<AIFeedback> {
    return this.request<AIFeedback>('/api/classroom/ai/feedback/generate', {
      method: 'POST',
      body: JSON.stringify({ assignmentTitle, submissionContent, rubric }),
    });
  }

  async summarizeContent(content: string, maxLength?: number, style?: string): Promise<{ summary: string }> {
    return this.request<{ summary: string }>('/api/classroom/ai/summarize', {
      method: 'POST',
      body: JSON.stringify({ content, maxLength, style }),
    });
  }

  async generateStudyGuide(content: string, topic?: string): Promise<{ studyGuide: string }> {
    return this.request<{ studyGuide: string }>('/api/classroom/ai/study-guide', {
      method: 'POST',
      body: JSON.stringify({ content, topic }),
    });
  }

  async extractKeyPoints(content: string, numPoints?: number): Promise<{ keyPoints: string[] }> {
    return this.request<{ keyPoints: string[] }>('/api/classroom/ai/key-points', {
      method: 'POST',
      body: JSON.stringify({ content, numPoints }),
    });
  }

  async simplifyText(content: string, targetLevel?: string): Promise<{ simplified: string }> {
    return this.request<{ simplified: string }>('/api/classroom/ai/simplify', {
      method: 'POST',
      body: JSON.stringify({ content, targetLevel }),
    });
  }
}

// Export singleton instance
export const classroomApi = new SmartClassroomAPI();
export default classroomApi;
