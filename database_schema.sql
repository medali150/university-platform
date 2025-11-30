-- University Platform Database Schema
-- PostgreSQL Database Script
-- Generated for: universety_db

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS "password_reset_tokens" CASCADE;
DROP TABLE IF EXISTS "calendar_events" CASCADE;
DROP TABLE IF EXISTS "ai_chats" CASCADE;
DROP TABLE IF EXISTS "course_attendance" CASCADE;
DROP TABLE IF EXISTS "discussion_replies" CASCADE;
DROP TABLE IF EXISTS "discussions" CASCADE;
DROP TABLE IF EXISTS "announcement_comments" CASCADE;
DROP TABLE IF EXISTS "course_announcements" CASCADE;
DROP TABLE IF EXISTS "course_materials" CASCADE;
DROP TABLE IF EXISTS "submission_comments" CASCADE;
DROP TABLE IF EXISTS "rubrics" CASCADE;
DROP TABLE IF EXISTS "assignment_submissions" CASCADE;
DROP TABLE IF EXISTS "assignments" CASCADE;
DROP TABLE IF EXISTS "course_enrollments" CASCADE;
DROP TABLE IF EXISTS "courses" CASCADE;
DROP TABLE IF EXISTS "event_reactions" CASCADE;
DROP TABLE IF EXISTS "event_comments" CASCADE;
DROP TABLE IF EXISTS "events" CASCADE;
DROP TABLE IF EXISTS "grade_reports" CASCADE;
DROP TABLE IF EXISTS "averages" CASCADE;
DROP TABLE IF EXISTS "grades" CASCADE;
DROP TABLE IF EXISTS "notifications" CASCADE;
DROP TABLE IF EXISTS "Message" CASCADE;
DROP TABLE IF EXISTS "Admin" CASCADE;
DROP TABLE IF EXISTS "DepartmentHead" CASCADE;
DROP TABLE IF EXISTS "Absence" CASCADE;
DROP TABLE IF EXISTS "Schedule" CASCADE;
DROP TABLE IF EXISTS "Subject" CASCADE;
DROP TABLE IF EXISTS "Student" CASCADE;
DROP TABLE IF EXISTS "Teacher" CASCADE;
DROP TABLE IF EXISTS "Room" CASCADE;
DROP TABLE IF EXISTS "Group" CASCADE;
DROP TABLE IF EXISTS "Level" CASCADE;
DROP TABLE IF EXISTS "Specialty" CASCADE;
DROP TABLE IF EXISTS "Department" CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;

-- Drop types if they exist
DROP TYPE IF EXISTS "SemesterType" CASCADE;
DROP TYPE IF EXISTS "GradeType" CASCADE;
DROP TYPE IF EXISTS "ScheduleStatus" CASCADE;
DROP TYPE IF EXISTS "RoomType" CASCADE;
DROP TYPE IF EXISTS "AbsenceStatus" CASCADE;
DROP TYPE IF EXISTS "Role" CASCADE;

-- Create ENUMS
CREATE TYPE "Role" AS ENUM ('STUDENT', 'TEACHER', 'DEPARTMENT_HEAD', 'ADMIN');
CREATE TYPE "AbsenceStatus" AS ENUM ('unjustified', 'pending_review', 'justified', 'approved', 'rejected');
CREATE TYPE "RoomType" AS ENUM ('LECTURE', 'LAB', 'EXAM', 'OTHER');
CREATE TYPE "ScheduleStatus" AS ENUM ('PLANNED', 'CANCELED', 'MAKEUP');
CREATE TYPE "GradeType" AS ENUM ('EXAM', 'CONTINUOUS', 'PRACTICAL', 'PROJECT', 'ORAL');
CREATE TYPE "SemesterType" AS ENUM ('SEMESTER_1', 'SEMESTER_2');

-- Create Tables

-- User Table
CREATE TABLE "User" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT UNIQUE NOT NULL,
    "role" "Role" NOT NULL,
    "mdp_hash" TEXT NOT NULL,
    "enseignant_id" TEXT UNIQUE,
    "etudiant_id" TEXT UNIQUE,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL
);

-- Department Table
CREATE TABLE "Department" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT UNIQUE NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL
);

-- Specialty Table
CREATE TABLE "Specialty" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_specialty_department" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE
);

-- Level Table
CREATE TABLE "Level" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_level_specialty" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE
);

-- Group Table
CREATE TABLE "Group" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_group_level" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE
);

-- Room Table
CREATE TABLE "Room" (
    "id" TEXT PRIMARY KEY,
    "code" TEXT UNIQUE NOT NULL,
    "type" "RoomType" NOT NULL,
    "capacite" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL
);

-- Teacher Table
CREATE TABLE "Teacher" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT UNIQUE NOT NULL,
    "id_departement" TEXT NOT NULL,
    "image_url" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_teacher_department" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE
);

-- Student Table
CREATE TABLE "Student" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT UNIQUE NOT NULL,
    "id_groupe" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "id_niveau" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_student_group" FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_student_specialty" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_student_level" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL
);

-- Subject Table
CREATE TABLE "Subject" (
    "id" TEXT PRIMARY KEY,
    "nom" TEXT NOT NULL,
    "coefficient" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "semester" TEXT,
    "id_departement" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "id_enseignant" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_subject_department" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_subject_level" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_subject_specialty" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_subject_teacher" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE SET NULL
);

-- Schedule Table
CREATE TABLE "Schedule" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_schedule_room" FOREIGN KEY ("id_salle") REFERENCES "Room"("id") ON DELETE RESTRICT,
    CONSTRAINT "fk_schedule_subject" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_schedule_group" FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_schedule_teacher" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE
);

-- Absence Table
CREATE TABLE "Absence" (
    "id" TEXT PRIMARY KEY,
    "id_etudiant" TEXT NOT NULL,
    "id_emploitemps" TEXT,
    "id_enseignant" TEXT,
    "date_absence" TIMESTAMP(3),
    "id_matiere" TEXT,
    "motif" TEXT,
    "statut" "AbsenceStatus" NOT NULL DEFAULT 'unjustified',
    "justification_text" TEXT,
    "supporting_documents" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "review_notes" TEXT,
    "reviewed_at" TIMESTAMP(3),
    "reviewed_by" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_absence_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_absence_schedule" FOREIGN KEY ("id_emploitemps") REFERENCES "Schedule"("id") ON DELETE CASCADE
);

-- Department Head Table
CREATE TABLE "DepartmentHead" (
    "id" TEXT PRIMARY KEY,
    "id_utilisateur" TEXT UNIQUE NOT NULL,
    "id_departement" TEXT UNIQUE NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_depthead_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_depthead_dept" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE
);

-- Admin Table
CREATE TABLE "Admin" (
    "id" TEXT PRIMARY KEY,
    "id_utilisateur" TEXT UNIQUE NOT NULL,
    "niveau" TEXT NOT NULL DEFAULT 'ADMIN',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_admin_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Message Table
CREATE TABLE "Message" (
    "id" TEXT PRIMARY KEY,
    "id_expediteur" TEXT NOT NULL,
    "id_destinataire" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "fk_message_sender" FOREIGN KEY ("id_expediteur") REFERENCES "User"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_message_receiver" FOREIGN KEY ("id_destinataire") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Notification Table
CREATE TABLE "notifications" (
    "id" TEXT PRIMARY KEY,
    "user_id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "related_id" TEXT,
    "is_read" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "fk_notification_user" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Grades Table
CREATE TABLE "grades" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_grade_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_grade_subject" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_grade_teacher" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE
);

-- Averages Table
CREATE TABLE "averages" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_average_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_average_subject" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_average" UNIQUE ("id_etudiant", "id_matiere", "semestre", "annee_scolaire")
);

-- Grade Reports Table
CREATE TABLE "grade_reports" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_report_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_report" UNIQUE ("id_etudiant", "semestre", "annee_scolaire")
);

-- Events Table
CREATE TABLE "events" (
    "id" TEXT PRIMARY KEY,
    "titre" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "description" TEXT,
    "date" TIMESTAMP(3),
    "lieu" TEXT,
    "id_createur" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_event_creator" FOREIGN KEY ("id_createur") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Event Comments Table
CREATE TABLE "event_comments" (
    "id" TEXT PRIMARY KEY,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_comment_event" FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_comment_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Event Reactions Table
CREATE TABLE "event_reactions" (
    "id" TEXT PRIMARY KEY,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_reaction_event" FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_reaction_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_reaction" UNIQUE ("id_evenement", "id_utilisateur")
);

-- Courses Table
CREATE TABLE "courses" (
    "id" TEXT PRIMARY KEY,
    "code" TEXT UNIQUE NOT NULL,
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
    "codeInvitation" TEXT UNIQUE,
    "dateDebut" TIMESTAMP(3),
    "dateFin" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_course_teacher" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_course_department" FOREIGN KEY ("id_departement") REFERENCES "Department"("id"),
    CONSTRAINT "fk_course_specialty" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id"),
    CONSTRAINT "fk_course_level" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id")
);

-- Course Enrollments Table
CREATE TABLE "course_enrollments" (
    "id" TEXT PRIMARY KEY,
    "id_cours" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "statut" TEXT NOT NULL DEFAULT 'active',
    "role" TEXT NOT NULL DEFAULT 'student',
    "dateInscription" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "dateRetrait" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_enrollment_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_enrollment_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_enrollment" UNIQUE ("id_cours", "id_etudiant")
);

-- Assignments Table
CREATE TABLE "assignments" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_assignment_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE
);

-- Assignment Submissions Table
CREATE TABLE "assignment_submissions" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_submission_assignment" FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_submission_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_submission" UNIQUE ("id_devoir", "id_etudiant", "tentativeNumero")
);

-- Rubrics Table
CREATE TABLE "rubrics" (
    "id" TEXT PRIMARY KEY,
    "id_devoir" TEXT NOT NULL,
    "critere" TEXT NOT NULL,
    "description" TEXT,
    "points" INTEGER NOT NULL,
    "ordre" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_rubric_assignment" FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE
);

-- Submission Comments Table
CREATE TABLE "submission_comments" (
    "id" TEXT PRIMARY KEY,
    "id_soumission" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "estPrive" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_subcomment_submission" FOREIGN KEY ("id_soumission") REFERENCES "assignment_submissions"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_subcomment_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id")
);

-- Course Materials Table
CREATE TABLE "course_materials" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_material_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE
);

-- Course Announcements Table
CREATE TABLE "course_announcements" (
    "id" TEXT PRIMARY KEY,
    "titre" TEXT,
    "contenu" TEXT NOT NULL,
    "id_cours" TEXT NOT NULL,
    "id_auteur" TEXT NOT NULL,
    "estEpingle" BOOLEAN NOT NULL DEFAULT false,
    "autoriserCommentaires" BOOLEAN NOT NULL DEFAULT true,
    "fichiers" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_announcement_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_announcement_author" FOREIGN KEY ("id_auteur") REFERENCES "User"("id")
);

-- Announcement Comments Table
CREATE TABLE "announcement_comments" (
    "id" TEXT PRIMARY KEY,
    "id_annonce" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_anncomment_announcement" FOREIGN KEY ("id_annonce") REFERENCES "course_announcements"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_anncomment_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id")
);

-- Discussions Table
CREATE TABLE "discussions" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_discussion_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_discussion_author" FOREIGN KEY ("id_auteur") REFERENCES "User"("id")
);

-- Discussion Replies Table
CREATE TABLE "discussion_replies" (
    "id" TEXT PRIMARY KEY,
    "id_discussion" TEXT NOT NULL,
    "id_auteur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "estMeilleure" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_reply_discussion" FOREIGN KEY ("id_discussion") REFERENCES "discussions"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_reply_author" FOREIGN KEY ("id_auteur") REFERENCES "User"("id")
);

-- Course Attendance Table
CREATE TABLE "course_attendance" (
    "id" TEXT PRIMARY KEY,
    "id_cours" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "dateSeance" TIMESTAMP(3) NOT NULL,
    "statut" TEXT NOT NULL,
    "remarque" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "fk_attendance_course" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE,
    CONSTRAINT "fk_attendance_student" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE,
    CONSTRAINT "unique_attendance" UNIQUE ("id_cours", "id_etudiant", "dateSeance")
);

-- AI Chats Table
CREATE TABLE "ai_chats" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_chat_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id")
);

-- Calendar Events Table
CREATE TABLE "calendar_events" (
    "id" TEXT PRIMARY KEY,
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
    CONSTRAINT "fk_calendar_user" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id")
);

-- Password Reset Tokens Table
CREATE TABLE "password_reset_tokens" (
    "id" TEXT PRIMARY KEY,
    "token" TEXT UNIQUE NOT NULL,
    "userId" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "used" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "fk_reset_user" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Add Foreign Key Constraints to User table (circular references)
ALTER TABLE "User" ADD CONSTRAINT "fk_user_teacher" 
    FOREIGN KEY ("enseignant_id") REFERENCES "Teacher"("id");
    
ALTER TABLE "User" ADD CONSTRAINT "fk_user_student" 
    FOREIGN KEY ("etudiant_id") REFERENCES "Student"("id");

-- Create Indexes for better performance
CREATE INDEX "idx_user_role" ON "User"("role");
CREATE INDEX "idx_user_email" ON "User"("email");
CREATE INDEX "idx_user_enseignant" ON "User"("enseignant_id");
CREATE INDEX "idx_user_etudiant" ON "User"("etudiant_id");

CREATE INDEX "idx_specialty_dept" ON "Specialty"("id_departement");
CREATE INDEX "idx_level_specialty" ON "Level"("id_specialite");
CREATE INDEX "idx_group_level" ON "Group"("id_niveau");

CREATE INDEX "idx_teacher_dept" ON "Teacher"("id_departement");
CREATE INDEX "idx_teacher_email" ON "Teacher"("email");

CREATE INDEX "idx_student_group" ON "Student"("id_groupe");
CREATE INDEX "idx_student_specialty" ON "Student"("id_specialite");
CREATE INDEX "idx_student_level" ON "Student"("id_niveau");
CREATE INDEX "idx_student_email" ON "Student"("email");

CREATE INDEX "idx_subject_dept" ON "Subject"("id_departement");
CREATE INDEX "idx_subject_level" ON "Subject"("id_niveau");
CREATE INDEX "idx_subject_specialty" ON "Subject"("id_specialite");
CREATE INDEX "idx_subject_teacher" ON "Subject"("id_enseignant");

CREATE INDEX "idx_schedule_date" ON "Schedule"("date");
CREATE INDEX "idx_schedule_room" ON "Schedule"("id_salle");
CREATE INDEX "idx_schedule_teacher" ON "Schedule"("id_enseignant");
CREATE INDEX "idx_schedule_group" ON "Schedule"("id_groupe");
CREATE INDEX "idx_schedule_semester" ON "Schedule"("semester");
CREATE INDEX "idx_schedule_recurring" ON "Schedule"("is_recurring");

CREATE INDEX "idx_absence_student" ON "Absence"("id_etudiant");
CREATE INDEX "idx_absence_schedule" ON "Absence"("id_emploitemps");
CREATE INDEX "idx_absence_teacher" ON "Absence"("id_enseignant");
CREATE INDEX "idx_absence_date" ON "Absence"("date_absence");
CREATE INDEX "idx_absence_status" ON "Absence"("statut");
CREATE INDEX "idx_absence_created" ON "Absence"("createdAt");

CREATE INDEX "idx_depthead_dept" ON "DepartmentHead"("id_departement");
CREATE INDEX "idx_admin_level" ON "Admin"("niveau");

CREATE INDEX "idx_message_sender" ON "Message"("id_expediteur", "createdAt");
CREATE INDEX "idx_message_receiver" ON "Message"("id_destinataire", "createdAt");

CREATE INDEX "idx_notification_user" ON "notifications"("user_id");
CREATE INDEX "idx_notification_read" ON "notifications"("is_read");
CREATE INDEX "idx_notification_created" ON "notifications"("created_at");

CREATE INDEX "idx_grade_student" ON "grades"("id_etudiant");
CREATE INDEX "idx_grade_subject" ON "grades"("id_matiere");
CREATE INDEX "idx_grade_teacher" ON "grades"("id_enseignant");
CREATE INDEX "idx_grade_semester" ON "grades"("semestre", "annee_scolaire");

CREATE INDEX "idx_average_student" ON "averages"("id_etudiant");
CREATE INDEX "idx_average_subject" ON "averages"("id_matiere");
CREATE INDEX "idx_average_semester" ON "averages"("semestre", "annee_scolaire");
CREATE INDEX "idx_average_validated" ON "averages"("validee");

CREATE INDEX "idx_report_student" ON "grade_reports"("id_etudiant");
CREATE INDEX "idx_report_semester" ON "grade_reports"("semestre", "annee_scolaire");
CREATE INDEX "idx_report_sent" ON "grade_reports"("envoye");

CREATE INDEX "idx_event_creator" ON "events"("id_createur");
CREATE INDEX "idx_event_type" ON "events"("type");
CREATE INDEX "idx_event_date" ON "events"("date");

CREATE INDEX "idx_event_comment_event" ON "event_comments"("id_evenement");
CREATE INDEX "idx_event_comment_user" ON "event_comments"("id_utilisateur");

CREATE INDEX "idx_event_reaction_event" ON "event_reactions"("id_evenement");
CREATE INDEX "idx_event_reaction_user" ON "event_reactions"("id_utilisateur");

CREATE INDEX "idx_course_teacher" ON "courses"("id_enseignant");
CREATE INDEX "idx_course_dept" ON "courses"("id_departement");
CREATE INDEX "idx_course_academic" ON "courses"("anneeAcademique", "semestre");

CREATE INDEX "idx_enrollment_course" ON "course_enrollments"("id_cours");
CREATE INDEX "idx_enrollment_student" ON "course_enrollments"("id_etudiant");

CREATE INDEX "idx_assignment_course" ON "assignments"("id_cours");
CREATE INDEX "idx_assignment_deadline" ON "assignments"("dateLimite");

CREATE INDEX "idx_submission_assignment" ON "assignment_submissions"("id_devoir");
CREATE INDEX "idx_submission_student" ON "assignment_submissions"("id_etudiant");
CREATE INDEX "idx_submission_status" ON "assignment_submissions"("statut");

CREATE INDEX "idx_rubric_assignment" ON "rubrics"("id_devoir");

CREATE INDEX "idx_subcomment_submission" ON "submission_comments"("id_soumission");
CREATE INDEX "idx_subcomment_user" ON "submission_comments"("id_utilisateur");

CREATE INDEX "idx_material_course" ON "course_materials"("id_cours");
CREATE INDEX "idx_material_type" ON "course_materials"("type");

CREATE INDEX "idx_announcement_course" ON "course_announcements"("id_cours");
CREATE INDEX "idx_announcement_author" ON "course_announcements"("id_auteur");

CREATE INDEX "idx_anncomment_announcement" ON "announcement_comments"("id_annonce");
CREATE INDEX "idx_anncomment_user" ON "announcement_comments"("id_utilisateur");

CREATE INDEX "idx_discussion_course" ON "discussions"("id_cours");
CREATE INDEX "idx_discussion_author" ON "discussions"("id_auteur");

CREATE INDEX "idx_reply_discussion" ON "discussion_replies"("id_discussion");
CREATE INDEX "idx_reply_author" ON "discussion_replies"("id_auteur");

CREATE INDEX "idx_attendance_course" ON "course_attendance"("id_cours");
CREATE INDEX "idx_attendance_student" ON "course_attendance"("id_etudiant");

CREATE INDEX "idx_chat_user" ON "ai_chats"("id_utilisateur");
CREATE INDEX "idx_chat_course" ON "ai_chats"("id_cours");

CREATE INDEX "idx_calendar_user" ON "calendar_events"("id_utilisateur");
CREATE INDEX "idx_calendar_start" ON "calendar_events"("dateDebut");

CREATE INDEX "idx_reset_token" ON "password_reset_tokens"("token");
CREATE INDEX "idx_reset_user" ON "password_reset_tokens"("userId");
CREATE INDEX "idx_reset_email" ON "password_reset_tokens"("email");
