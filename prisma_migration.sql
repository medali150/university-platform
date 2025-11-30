-- ========================================
-- UNIVERSITY PLATFORM - PRISMA MIGRATION
-- Complete Database Schema Script
-- Generated from Prisma Schema
-- ========================================

-- Drop existing database objects (CAUTION: This will delete all data)
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- ========================================
-- CREATE ENUMS
-- ========================================

CREATE TYPE "Role" AS ENUM ('STUDENT', 'TEACHER', 'DEPARTMENT_HEAD', 'ADMIN');

CREATE TYPE "AbsenceStatus" AS ENUM (
    'unjustified',
    'pending_review',
    'justified',
    'approved',
    'rejected'
);

CREATE TYPE "RoomType" AS ENUM ('LECTURE', 'LAB', 'EXAM', 'OTHER');

CREATE TYPE "ScheduleStatus" AS ENUM ('PLANNED', 'CANCELED', 'MAKEUP');

CREATE TYPE "GradeType" AS ENUM ('EXAM', 'CONTINUOUS', 'PRACTICAL', 'PROJECT', 'ORAL');

CREATE TYPE "SemesterType" AS ENUM ('SEMESTER_1', 'SEMESTER_2');

-- ========================================
-- CREATE TABLES
-- ========================================

-- User Table
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "role" "Role" NOT NULL,
    "mdp_hash" TEXT NOT NULL,
    "enseignant_id" TEXT,
    "etudiant_id" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- Department Table
CREATE TABLE "Department" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Department_pkey" PRIMARY KEY ("id")
);

-- Specialty Table
CREATE TABLE "Specialty" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Specialty_pkey" PRIMARY KEY ("id")
);

-- Level Table
CREATE TABLE "Level" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Level_pkey" PRIMARY KEY ("id")
);

-- Group Table
CREATE TABLE "Group" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Group_pkey" PRIMARY KEY ("id")
);

-- Room Table
CREATE TABLE "Room" (
    "id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "type" "RoomType" NOT NULL,
    "capacite" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Room_pkey" PRIMARY KEY ("id")
);

-- Teacher Table
CREATE TABLE "Teacher" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "image_url" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Teacher_pkey" PRIMARY KEY ("id")
);

-- Student Table
CREATE TABLE "Student" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "id_groupe" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "id_niveau" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Student_pkey" PRIMARY KEY ("id")
);

-- Subject Table
CREATE TABLE "Subject" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "coefficient" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "semester" TEXT,
    "id_departement" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "id_enseignant" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Subject_pkey" PRIMARY KEY ("id")
);

-- Schedule Table
CREATE TABLE "Schedule" (
    "id" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "heure_debut" TIMESTAMP(3) NOT NULL,
    "heure_fin" TIMESTAMP(3) NOT NULL,
    "id_salle" TEXT NOT NULL,
    "id_matiere" TEXT NOT NULL,
    "id_groupe" TEXT NOT NULL,
    "id_enseignant" TEXT NOT NULL,
    "status" "ScheduleStatus" NOT NULL DEFAULT 'PLANNED',
    "semester" TEXT,
    "week_day" INTEGER,
    "is_recurring" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Schedule_pkey" PRIMARY KEY ("id")
);

-- Absence Table
CREATE TABLE "Absence" (
    "id" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "id_emploitemps" TEXT,
    "id_enseignant" TEXT,
    "date_absence" TIMESTAMP(3),
    "id_matiere" TEXT,
    "motif" TEXT,
    "statut" "AbsenceStatus" NOT NULL DEFAULT 'unjustified',
    "justification_text" TEXT,
    "supporting_documents" TEXT[],
    "review_notes" TEXT,
    "reviewed_at" TIMESTAMP(3),
    "reviewed_by" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Absence_pkey" PRIMARY KEY ("id")
);

-- DepartmentHead Table
CREATE TABLE "DepartmentHead" (
    "id" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "DepartmentHead_pkey" PRIMARY KEY ("id")
);

-- Admin Table
CREATE TABLE "Admin" (
    "id" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "niveau" TEXT NOT NULL DEFAULT 'ADMIN',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "Admin_pkey" PRIMARY KEY ("id")
);

-- Message Table
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "id_expediteur" TEXT NOT NULL,
    "id_destinataire" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- Notification Table
CREATE TABLE "notifications" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "related_id" TEXT,
    "is_read" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT "notifications_pkey" PRIMARY KEY ("id")
);

-- Grades Table
CREATE TABLE "grades" (
    "id" TEXT NOT NULL,
    "valeur" DOUBLE PRECISION NOT NULL,
    "type" "GradeType" NOT NULL,
    "coefficient" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "id_etudiant" TEXT NOT NULL,
    "id_matiere" TEXT NOT NULL,
    "id_enseignant" TEXT NOT NULL,
    "semestre" "SemesterType" NOT NULL,
    "annee_scolaire" TEXT NOT NULL,
    "date_examen" TIMESTAMP(3),
    "validee" BOOLEAN NOT NULL DEFAULT false,
    "observation" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "grades_pkey" PRIMARY KEY ("id")
);

-- Averages Table
CREATE TABLE "averages" (
    "id" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "id_matiere" TEXT,
    "semestre" "SemesterType" NOT NULL,
    "annee_scolaire" TEXT NOT NULL,
    "moyenne_matiere" DOUBLE PRECISION,
    "moyenne_generale" DOUBLE PRECISION,
    "rang" INTEGER,
    "validee" BOOLEAN NOT NULL DEFAULT false,
    "validee_par" TEXT,
    "date_validation" TIMESTAMP(3),
    "observation" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "averages_pkey" PRIMARY KEY ("id")
);

-- Grade Reports Table
CREATE TABLE "grade_reports" (
    "id" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "semestre" "SemesterType" NOT NULL,
    "annee_scolaire" TEXT NOT NULL,
    "moyenne_generale" DOUBLE PRECISION NOT NULL,
    "rang" INTEGER,
    "total_etudiants" INTEGER,
    "appreciation" TEXT,
    "pdf_url" TEXT,
    "genere_par" TEXT,
    "date_generation" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "envoye" BOOLEAN NOT NULL DEFAULT false,
    "date_envoi" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "grade_reports_pkey" PRIMARY KEY ("id")
);

-- Events Table
CREATE TABLE "events" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "description" TEXT,
    "date" TIMESTAMP(3),
    "lieu" TEXT,
    "id_createur" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "events_pkey" PRIMARY KEY ("id")
);

-- Event Comments Table
CREATE TABLE "event_comments" (
    "id" TEXT NOT NULL,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "event_comments_pkey" PRIMARY KEY ("id")
);

-- Event Reactions Table
CREATE TABLE "event_reactions" (
    "id" TEXT NOT NULL,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "event_reactions_pkey" PRIMARY KEY ("id")
);

-- Courses Table (Smart Classroom)
CREATE TABLE "courses" (
    "id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "description" TEXT,
    "imageUrl" TEXT,
    "couleur" TEXT NOT NULL DEFAULT '#3B82F6',
    "id_enseignant" TEXT NOT NULL,
    "id_departement" TEXT,
    "id_specialite" TEXT,
    "id_niveau" TEXT,
    "anneeAcademique" TEXT NOT NULL,
    "semestre" TEXT NOT NULL,
    "capaciteMax" INTEGER,
    "estActif" BOOLEAN NOT NULL DEFAULT true,
    "estPublic" BOOLEAN NOT NULL DEFAULT false,
    "codeInvitation" TEXT,
    "dateDebut" TIMESTAMP(3),
    "dateFin" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "courses_pkey" PRIMARY KEY ("id")
);

-- Course Enrollments Table
CREATE TABLE "course_enrollments" (
    "id" TEXT NOT NULL,
    "id_cours" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "statut" TEXT NOT NULL DEFAULT 'active',
    "role" TEXT NOT NULL DEFAULT 'student',
    "dateInscription" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "dateRetrait" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "course_enrollments_pkey" PRIMARY KEY ("id")
);

-- Assignments Table
CREATE TABLE "assignments" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "instructions" TEXT,
    "id_cours" TEXT NOT NULL,
    "type" TEXT NOT NULL DEFAULT 'assignment',
    "points" INTEGER NOT NULL DEFAULT 100,
    "dateCreation" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "dateLimite" TIMESTAMP(3) NOT NULL,
    "dateDisponible" TIMESTAMP(3),
    "autoriserSoumissionTardive" BOOLEAN NOT NULL DEFAULT false,
    "penaliteRetard" INTEGER,
    "attemptsMax" INTEGER NOT NULL DEFAULT 1,
    "afficherCorrection" BOOLEAN NOT NULL DEFAULT true,
    "detectionPlagiat" BOOLEAN NOT NULL DEFAULT true,
    "feedbackAI" BOOLEAN NOT NULL DEFAULT true,
    "fichiers" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "assignments_pkey" PRIMARY KEY ("id")
);

-- Assignment Submissions Table
CREATE TABLE "assignment_submissions" (
    "id" TEXT NOT NULL,
    "id_devoir" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "contenu" TEXT,
    "fichiers" JSONB,
    "statut" TEXT NOT NULL DEFAULT 'submitted',
    "tentativeNumero" INTEGER NOT NULL DEFAULT 1,
    "estEnRetard" BOOLEAN NOT NULL DEFAULT false,
    "note" DOUBLE PRECISION,
    "noteMax" DOUBLE PRECISION,
    "feedback" TEXT,
    "feedbackAI" TEXT,
    "scorePlagiat" DOUBLE PRECISION,
    "rapportPlagiat" JSONB,
    "dateSoumission" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "dateNotation" TIMESTAMP(3),
    "dateRetour" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "assignment_submissions_pkey" PRIMARY KEY ("id")
);

-- Rubrics Table
CREATE TABLE "rubrics" (
    "id" TEXT NOT NULL,
    "id_devoir" TEXT NOT NULL,
    "critere" TEXT NOT NULL,
    "description" TEXT,
    "points" INTEGER NOT NULL,
    "ordre" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "rubrics_pkey" PRIMARY KEY ("id")
);

-- Submission Comments Table
CREATE TABLE "submission_comments" (
    "id" TEXT NOT NULL,
    "id_soumission" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "estPrive" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "submission_comments_pkey" PRIMARY KEY ("id")
);

-- Course Materials Table
CREATE TABLE "course_materials" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "description" TEXT,
    "id_cours" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "fichierUrl" TEXT,
    "fichierNom" TEXT,
    "fichierTaille" INTEGER,
    "fichierType" TEXT,
    "lienExterne" TEXT,
    "resumeAI" TEXT,
    "transcription" TEXT,
    "dossierParentId" TEXT,
    "ordre" INTEGER NOT NULL DEFAULT 0,
    "estPublie" BOOLEAN NOT NULL DEFAULT true,
    "estTelechargeable" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "course_materials_pkey" PRIMARY KEY ("id")
);

-- Course Announcements Table
CREATE TABLE "course_announcements" (
    "id" TEXT NOT NULL,
    "titre" TEXT,
    "contenu" TEXT NOT NULL,
    "id_cours" TEXT NOT NULL,
    "id_auteur" TEXT NOT NULL,
    "estEpingle" BOOLEAN NOT NULL DEFAULT false,
    "autoriserCommentaires" BOOLEAN NOT NULL DEFAULT true,
    "fichiers" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "course_announcements_pkey" PRIMARY KEY ("id")
);

-- Announcement Comments Table
CREATE TABLE "announcement_comments" (
    "id" TEXT NOT NULL,
    "id_annonce" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "announcement_comments_pkey" PRIMARY KEY ("id")
);

-- Discussions Table
CREATE TABLE "discussions" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "id_cours" TEXT NOT NULL,
    "id_auteur" TEXT NOT NULL,
    "estEpingle" BOOLEAN NOT NULL DEFAULT false,
    "estResolu" BOOLEAN NOT NULL DEFAULT false,
    "estVerrouille" BOOLEAN NOT NULL DEFAULT false,
    "nbVues" INTEGER NOT NULL DEFAULT 0,
    "nbReponses" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "discussions_pkey" PRIMARY KEY ("id")
);

-- Discussion Replies Table
CREATE TABLE "discussion_replies" (
    "id" TEXT NOT NULL,
    "id_discussion" TEXT NOT NULL,
    "id_auteur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "estMeilleure" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "discussion_replies_pkey" PRIMARY KEY ("id")
);

-- Course Attendance Table
CREATE TABLE "course_attendance" (
    "id" TEXT NOT NULL,
    "id_cours" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "dateSeance" TIMESTAMP(3) NOT NULL,
    "statut" TEXT NOT NULL,
    "remarque" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "course_attendance_pkey" PRIMARY KEY ("id")
);

-- AI Chats Table
CREATE TABLE "ai_chats" (
    "id" TEXT NOT NULL,
    "id_cours" TEXT,
    "id_utilisateur" TEXT NOT NULL,
    "question" TEXT NOT NULL,
    "reponse" TEXT NOT NULL,
    "contexte" JSONB,
    "modeleAI" TEXT NOT NULL DEFAULT 'gpt-4',
    "tokensUtilises" INTEGER,
    "tempReponse" DOUBLE PRECISION,
    "estUtile" BOOLEAN,
    "feedback" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT "ai_chats_pkey" PRIMARY KEY ("id")
);

-- Calendar Events Table
CREATE TABLE "calendar_events" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "description" TEXT,
    "id_cours" TEXT,
    "id_utilisateur" TEXT NOT NULL,
    "dateDebut" TIMESTAMP(3) NOT NULL,
    "dateFin" TIMESTAMP(3) NOT NULL,
    "estJourneeComplete" BOOLEAN NOT NULL DEFAULT false,
    "type" TEXT NOT NULL,
    "couleur" TEXT NOT NULL DEFAULT '#3B82F6',
    "rappel" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    
    CONSTRAINT "calendar_events_pkey" PRIMARY KEY ("id")
);

-- Password Reset Tokens Table
CREATE TABLE "password_reset_tokens" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "used" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT "password_reset_tokens_pkey" PRIMARY KEY ("id")
);

-- ========================================
-- CREATE UNIQUE CONSTRAINTS
-- ========================================

CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
CREATE UNIQUE INDEX "User_enseignant_id_key" ON "User"("enseignant_id");
CREATE UNIQUE INDEX "User_etudiant_id_key" ON "User"("etudiant_id");

CREATE UNIQUE INDEX "Department_nom_key" ON "Department"("nom");

CREATE UNIQUE INDEX "Room_code_key" ON "Room"("code");

CREATE UNIQUE INDEX "Teacher_email_key" ON "Teacher"("email");

CREATE UNIQUE INDEX "Student_email_key" ON "Student"("email");

CREATE UNIQUE INDEX "DepartmentHead_id_utilisateur_key" ON "DepartmentHead"("id_utilisateur");
CREATE UNIQUE INDEX "DepartmentHead_id_departement_key" ON "DepartmentHead"("id_departement");

CREATE UNIQUE INDEX "Admin_id_utilisateur_key" ON "Admin"("id_utilisateur");

CREATE UNIQUE INDEX "averages_id_etudiant_id_matiere_semestre_annee_scolaire_key" 
    ON "averages"("id_etudiant", "id_matiere", "semestre", "annee_scolaire");

CREATE UNIQUE INDEX "grade_reports_id_etudiant_semestre_annee_scolaire_key" 
    ON "grade_reports"("id_etudiant", "semestre", "annee_scolaire");

CREATE UNIQUE INDEX "event_reactions_id_evenement_id_utilisateur_key" 
    ON "event_reactions"("id_evenement", "id_utilisateur");

CREATE UNIQUE INDEX "courses_code_key" ON "courses"("code");
CREATE UNIQUE INDEX "courses_codeInvitation_key" ON "courses"("codeInvitation");

CREATE UNIQUE INDEX "course_enrollments_id_cours_id_etudiant_key" 
    ON "course_enrollments"("id_cours", "id_etudiant");

CREATE UNIQUE INDEX "assignment_submissions_id_devoir_id_etudiant_tentativeNumero_key" 
    ON "assignment_submissions"("id_devoir", "id_etudiant", "tentativeNumero");

CREATE UNIQUE INDEX "course_attendance_id_cours_id_etudiant_dateSeance_key" 
    ON "course_attendance"("id_cours", "id_etudiant", "dateSeance");

CREATE UNIQUE INDEX "password_reset_tokens_token_key" ON "password_reset_tokens"("token");

-- ========================================
-- CREATE INDEXES
-- ========================================

CREATE INDEX "User_role_idx" ON "User"("role");
CREATE INDEX "User_email_idx" ON "User"("email");
CREATE INDEX "User_enseignant_id_idx" ON "User"("enseignant_id");
CREATE INDEX "User_etudiant_id_idx" ON "User"("etudiant_id");

CREATE INDEX "Specialty_id_departement_idx" ON "Specialty"("id_departement");
CREATE INDEX "Level_id_specialite_idx" ON "Level"("id_specialite");
CREATE INDEX "Group_id_niveau_idx" ON "Group"("id_niveau");

CREATE INDEX "Teacher_id_departement_idx" ON "Teacher"("id_departement");
CREATE INDEX "Teacher_email_idx" ON "Teacher"("email");

CREATE INDEX "Student_id_groupe_idx" ON "Student"("id_groupe");
CREATE INDEX "Student_id_specialite_idx" ON "Student"("id_specialite");
CREATE INDEX "Student_id_niveau_idx" ON "Student"("id_niveau");
CREATE INDEX "Student_email_idx" ON "Student"("email");

CREATE INDEX "Subject_id_departement_idx" ON "Subject"("id_departement");
CREATE INDEX "Subject_id_niveau_idx" ON "Subject"("id_niveau");
CREATE INDEX "Subject_id_specialite_idx" ON "Subject"("id_specialite");
CREATE INDEX "Subject_id_enseignant_idx" ON "Subject"("id_enseignant");

CREATE INDEX "Schedule_date_idx" ON "Schedule"("date");
CREATE INDEX "Schedule_id_salle_idx" ON "Schedule"("id_salle");
CREATE INDEX "Schedule_id_matiere_idx" ON "Schedule"("id_matiere");
CREATE INDEX "Schedule_id_groupe_idx" ON "Schedule"("id_groupe");
CREATE INDEX "Schedule_id_enseignant_idx" ON "Schedule"("id_enseignant");
CREATE INDEX "Schedule_semester_idx" ON "Schedule"("semester");
CREATE INDEX "Schedule_is_recurring_idx" ON "Schedule"("is_recurring");

CREATE INDEX "Absence_id_etudiant_idx" ON "Absence"("id_etudiant");
CREATE INDEX "Absence_id_emploitemps_idx" ON "Absence"("id_emploitemps");
CREATE INDEX "Absence_id_enseignant_idx" ON "Absence"("id_enseignant");
CREATE INDEX "Absence_date_absence_idx" ON "Absence"("date_absence");
CREATE INDEX "Absence_statut_idx" ON "Absence"("statut");
CREATE INDEX "Absence_createdAt_idx" ON "Absence"("createdAt");

CREATE INDEX "DepartmentHead_id_departement_idx" ON "DepartmentHead"("id_departement");
CREATE INDEX "Admin_niveau_idx" ON "Admin"("niveau");

CREATE INDEX "Message_id_expediteur_createdAt_idx" ON "Message"("id_expediteur", "createdAt");
CREATE INDEX "Message_id_destinataire_createdAt_idx" ON "Message"("id_destinataire", "createdAt");

CREATE INDEX "notifications_user_id_idx" ON "notifications"("user_id");
CREATE INDEX "notifications_is_read_idx" ON "notifications"("is_read");
CREATE INDEX "notifications_created_at_idx" ON "notifications"("created_at");

CREATE INDEX "grades_id_etudiant_idx" ON "grades"("id_etudiant");
CREATE INDEX "grades_id_matiere_idx" ON "grades"("id_matiere");
CREATE INDEX "grades_id_enseignant_idx" ON "grades"("id_enseignant");
CREATE INDEX "grades_semestre_annee_scolaire_idx" ON "grades"("semestre", "annee_scolaire");

CREATE INDEX "averages_id_etudiant_idx" ON "averages"("id_etudiant");
CREATE INDEX "averages_id_matiere_idx" ON "averages"("id_matiere");
CREATE INDEX "averages_semestre_annee_scolaire_idx" ON "averages"("semestre", "annee_scolaire");
CREATE INDEX "averages_validee_idx" ON "averages"("validee");

CREATE INDEX "grade_reports_id_etudiant_idx" ON "grade_reports"("id_etudiant");
CREATE INDEX "grade_reports_semestre_annee_scolaire_idx" ON "grade_reports"("semestre", "annee_scolaire");
CREATE INDEX "grade_reports_envoye_idx" ON "grade_reports"("envoye");

CREATE INDEX "events_id_createur_idx" ON "events"("id_createur");
CREATE INDEX "events_type_idx" ON "events"("type");
CREATE INDEX "events_date_idx" ON "events"("date");

CREATE INDEX "event_comments_id_evenement_idx" ON "event_comments"("id_evenement");
CREATE INDEX "event_comments_id_utilisateur_idx" ON "event_comments"("id_utilisateur");

CREATE INDEX "event_reactions_id_evenement_idx" ON "event_reactions"("id_evenement");
CREATE INDEX "event_reactions_id_utilisateur_idx" ON "event_reactions"("id_utilisateur");

CREATE INDEX "courses_id_enseignant_idx" ON "courses"("id_enseignant");
CREATE INDEX "courses_id_departement_idx" ON "courses"("id_departement");
CREATE INDEX "courses_anneeAcademique_semestre_idx" ON "courses"("anneeAcademique", "semestre");

CREATE INDEX "course_enrollments_id_cours_idx" ON "course_enrollments"("id_cours");
CREATE INDEX "course_enrollments_id_etudiant_idx" ON "course_enrollments"("id_etudiant");

CREATE INDEX "assignments_id_cours_idx" ON "assignments"("id_cours");
CREATE INDEX "assignments_dateLimite_idx" ON "assignments"("dateLimite");

CREATE INDEX "assignment_submissions_id_devoir_idx" ON "assignment_submissions"("id_devoir");
CREATE INDEX "assignment_submissions_id_etudiant_idx" ON "assignment_submissions"("id_etudiant");
CREATE INDEX "assignment_submissions_statut_idx" ON "assignment_submissions"("statut");

CREATE INDEX "rubrics_id_devoir_idx" ON "rubrics"("id_devoir");

CREATE INDEX "submission_comments_id_soumission_idx" ON "submission_comments"("id_soumission");
CREATE INDEX "submission_comments_id_utilisateur_idx" ON "submission_comments"("id_utilisateur");

CREATE INDEX "course_materials_id_cours_idx" ON "course_materials"("id_cours");
CREATE INDEX "course_materials_type_idx" ON "course_materials"("type");

CREATE INDEX "course_announcements_id_cours_idx" ON "course_announcements"("id_cours");
CREATE INDEX "course_announcements_id_auteur_idx" ON "course_announcements"("id_auteur");

CREATE INDEX "announcement_comments_id_annonce_idx" ON "announcement_comments"("id_annonce");
CREATE INDEX "announcement_comments_id_utilisateur_idx" ON "announcement_comments"("id_utilisateur");

CREATE INDEX "discussions_id_cours_idx" ON "discussions"("id_cours");
CREATE INDEX "discussions_id_auteur_idx" ON "discussions"("id_auteur");

CREATE INDEX "discussion_replies_id_discussion_idx" ON "discussion_replies"("id_discussion");
CREATE INDEX "discussion_replies_id_auteur_idx" ON "discussion_replies"("id_auteur");

CREATE INDEX "course_attendance_id_cours_idx" ON "course_attendance"("id_cours");
CREATE INDEX "course_attendance_id_etudiant_idx" ON "course_attendance"("id_etudiant");

CREATE INDEX "ai_chats_id_utilisateur_idx" ON "ai_chats"("id_utilisateur");
CREATE INDEX "ai_chats_id_cours_idx" ON "ai_chats"("id_cours");

CREATE INDEX "calendar_events_id_utilisateur_idx" ON "calendar_events"("id_utilisateur");
CREATE INDEX "calendar_events_dateDebut_idx" ON "calendar_events"("dateDebut");

CREATE INDEX "password_reset_tokens_token_idx" ON "password_reset_tokens"("token");
CREATE INDEX "password_reset_tokens_userId_idx" ON "password_reset_tokens"("userId");
CREATE INDEX "password_reset_tokens_email_idx" ON "password_reset_tokens"("email");

-- ========================================
-- ADD FOREIGN KEY CONSTRAINTS
-- ========================================

ALTER TABLE "User" ADD CONSTRAINT "User_enseignant_id_fkey" 
    FOREIGN KEY ("enseignant_id") REFERENCES "Teacher"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "User" ADD CONSTRAINT "User_etudiant_id_fkey" 
    FOREIGN KEY ("etudiant_id") REFERENCES "Student"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "Specialty" ADD CONSTRAINT "Specialty_id_departement_fkey" 
    FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Level" ADD CONSTRAINT "Level_id_specialite_fkey" 
    FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Group" ADD CONSTRAINT "Group_id_niveau_fkey" 
    FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Teacher" ADD CONSTRAINT "Teacher_id_departement_fkey" 
    FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Student" ADD CONSTRAINT "Student_id_groupe_fkey" 
    FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Student" ADD CONSTRAINT "Student_id_specialite_fkey" 
    FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Student" ADD CONSTRAINT "Student_id_niveau_fkey" 
    FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_departement_fkey" 
    FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_niveau_fkey" 
    FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_specialite_fkey" 
    FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_enseignant_fkey" 
    FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_salle_fkey" 
    FOREIGN KEY ("id_salle") REFERENCES "Room"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_matiere_fkey" 
    FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_groupe_fkey" 
    FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_enseignant_fkey" 
    FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Absence" ADD CONSTRAINT "Absence_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Absence" ADD CONSTRAINT "Absence_id_emploitemps_fkey" 
    FOREIGN KEY ("id_emploitemps") REFERENCES "Schedule"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "DepartmentHead" ADD CONSTRAINT "DepartmentHead_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "DepartmentHead" ADD CONSTRAINT "DepartmentHead_id_departement_fkey" 
    FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Admin" ADD CONSTRAINT "Admin_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Message" ADD CONSTRAINT "Message_id_expediteur_fkey" 
    FOREIGN KEY ("id_expediteur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "Message" ADD CONSTRAINT "Message_id_destinataire_fkey" 
    FOREIGN KEY ("id_destinataire") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "notifications" ADD CONSTRAINT "notifications_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "grades" ADD CONSTRAINT "grades_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "grades" ADD CONSTRAINT "grades_id_matiere_fkey" 
    FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "grades" ADD CONSTRAINT "grades_id_enseignant_fkey" 
    FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "averages" ADD CONSTRAINT "averages_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "averages" ADD CONSTRAINT "averages_id_matiere_fkey" 
    FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "grade_reports" ADD CONSTRAINT "grade_reports_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "events" ADD CONSTRAINT "events_id_createur_fkey" 
    FOREIGN KEY ("id_createur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "event_comments" ADD CONSTRAINT "event_comments_id_evenement_fkey" 
    FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "event_comments" ADD CONSTRAINT "event_comments_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "event_reactions" ADD CONSTRAINT "event_reactions_id_evenement_fkey" 
    FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "event_reactions" ADD CONSTRAINT "event_reactions_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "courses" ADD CONSTRAINT "courses_id_enseignant_fkey" 
    FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "courses" ADD CONSTRAINT "courses_id_departement_fkey" 
    FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "courses" ADD CONSTRAINT "courses_id_specialite_fkey" 
    FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "courses" ADD CONSTRAINT "courses_id_niveau_fkey" 
    FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "course_enrollments" ADD CONSTRAINT "course_enrollments_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "course_enrollments" ADD CONSTRAINT "course_enrollments_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "assignments" ADD CONSTRAINT "assignments_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "assignment_submissions" ADD CONSTRAINT "assignment_submissions_id_devoir_fkey" 
    FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "assignment_submissions" ADD CONSTRAINT "assignment_submissions_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "rubrics" ADD CONSTRAINT "rubrics_id_devoir_fkey" 
    FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "submission_comments" ADD CONSTRAINT "submission_comments_id_soumission_fkey" 
    FOREIGN KEY ("id_soumission") REFERENCES "assignment_submissions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "submission_comments" ADD CONSTRAINT "submission_comments_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "course_materials" ADD CONSTRAINT "course_materials_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "course_announcements" ADD CONSTRAINT "course_announcements_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "course_announcements" ADD CONSTRAINT "course_announcements_id_auteur_fkey" 
    FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "announcement_comments" ADD CONSTRAINT "announcement_comments_id_annonce_fkey" 
    FOREIGN KEY ("id_annonce") REFERENCES "course_announcements"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "announcement_comments" ADD CONSTRAINT "announcement_comments_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "discussions" ADD CONSTRAINT "discussions_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "discussions" ADD CONSTRAINT "discussions_id_auteur_fkey" 
    FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "discussion_replies" ADD CONSTRAINT "discussion_replies_id_discussion_fkey" 
    FOREIGN KEY ("id_discussion") REFERENCES "discussions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "discussion_replies" ADD CONSTRAINT "discussion_replies_id_auteur_fkey" 
    FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "course_attendance" ADD CONSTRAINT "course_attendance_id_cours_fkey" 
    FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "course_attendance" ADD CONSTRAINT "course_attendance_id_etudiant_fkey" 
    FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "ai_chats" ADD CONSTRAINT "ai_chats_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "calendar_events" ADD CONSTRAINT "calendar_events_id_utilisateur_fkey" 
    FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "password_reset_tokens" ADD CONSTRAINT "password_reset_tokens_userId_fkey" 
    FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- ========================================
-- SCRIPT COMPLETED
-- ========================================
-- Total Tables Created: 42
-- Total Enums Created: 6
-- Total Indexes Created: 100+
-- Total Foreign Keys: 60+
-- ========================================
