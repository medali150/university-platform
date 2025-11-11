-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
CREATE TABLE "announcement_comments" (
    "id" TEXT NOT NULL,
    "id_annonce" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "announcement_comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateIndex
CREATE UNIQUE INDEX "courses_code_key" ON "courses"("code");

-- CreateIndex
CREATE UNIQUE INDEX "courses_codeInvitation_key" ON "courses"("codeInvitation");

-- CreateIndex
CREATE INDEX "courses_id_enseignant_idx" ON "courses"("id_enseignant");

-- CreateIndex
CREATE INDEX "courses_id_departement_idx" ON "courses"("id_departement");

-- CreateIndex
CREATE INDEX "courses_anneeAcademique_semestre_idx" ON "courses"("anneeAcademique", "semestre");

-- CreateIndex
CREATE INDEX "course_enrollments_id_cours_idx" ON "course_enrollments"("id_cours");

-- CreateIndex
CREATE INDEX "course_enrollments_id_etudiant_idx" ON "course_enrollments"("id_etudiant");

-- CreateIndex
CREATE UNIQUE INDEX "course_enrollments_id_cours_id_etudiant_key" ON "course_enrollments"("id_cours", "id_etudiant");

-- CreateIndex
CREATE INDEX "assignments_id_cours_idx" ON "assignments"("id_cours");

-- CreateIndex
CREATE INDEX "assignments_dateLimite_idx" ON "assignments"("dateLimite");

-- CreateIndex
CREATE INDEX "assignment_submissions_id_devoir_idx" ON "assignment_submissions"("id_devoir");

-- CreateIndex
CREATE INDEX "assignment_submissions_id_etudiant_idx" ON "assignment_submissions"("id_etudiant");

-- CreateIndex
CREATE INDEX "assignment_submissions_statut_idx" ON "assignment_submissions"("statut");

-- CreateIndex
CREATE UNIQUE INDEX "assignment_submissions_id_devoir_id_etudiant_tentativeNumer_key" ON "assignment_submissions"("id_devoir", "id_etudiant", "tentativeNumero");

-- CreateIndex
CREATE INDEX "rubrics_id_devoir_idx" ON "rubrics"("id_devoir");

-- CreateIndex
CREATE INDEX "submission_comments_id_soumission_idx" ON "submission_comments"("id_soumission");

-- CreateIndex
CREATE INDEX "submission_comments_id_utilisateur_idx" ON "submission_comments"("id_utilisateur");

-- CreateIndex
CREATE INDEX "course_materials_id_cours_idx" ON "course_materials"("id_cours");

-- CreateIndex
CREATE INDEX "course_materials_type_idx" ON "course_materials"("type");

-- CreateIndex
CREATE INDEX "course_announcements_id_cours_idx" ON "course_announcements"("id_cours");

-- CreateIndex
CREATE INDEX "course_announcements_id_auteur_idx" ON "course_announcements"("id_auteur");

-- CreateIndex
CREATE INDEX "announcement_comments_id_annonce_idx" ON "announcement_comments"("id_annonce");

-- CreateIndex
CREATE INDEX "announcement_comments_id_utilisateur_idx" ON "announcement_comments"("id_utilisateur");

-- CreateIndex
CREATE INDEX "discussions_id_cours_idx" ON "discussions"("id_cours");

-- CreateIndex
CREATE INDEX "discussions_id_auteur_idx" ON "discussions"("id_auteur");

-- CreateIndex
CREATE INDEX "discussion_replies_id_discussion_idx" ON "discussion_replies"("id_discussion");

-- CreateIndex
CREATE INDEX "discussion_replies_id_auteur_idx" ON "discussion_replies"("id_auteur");

-- CreateIndex
CREATE INDEX "course_attendance_id_cours_idx" ON "course_attendance"("id_cours");

-- CreateIndex
CREATE INDEX "course_attendance_id_etudiant_idx" ON "course_attendance"("id_etudiant");

-- CreateIndex
CREATE UNIQUE INDEX "course_attendance_id_cours_id_etudiant_dateSeance_key" ON "course_attendance"("id_cours", "id_etudiant", "dateSeance");

-- CreateIndex
CREATE INDEX "ai_chats_id_utilisateur_idx" ON "ai_chats"("id_utilisateur");

-- CreateIndex
CREATE INDEX "ai_chats_id_cours_idx" ON "ai_chats"("id_cours");

-- CreateIndex
CREATE INDEX "calendar_events_id_utilisateur_idx" ON "calendar_events"("id_utilisateur");

-- CreateIndex
CREATE INDEX "calendar_events_dateDebut_idx" ON "calendar_events"("dateDebut");

-- AddForeignKey
ALTER TABLE "courses" ADD CONSTRAINT "courses_id_enseignant_fkey" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "courses" ADD CONSTRAINT "courses_id_departement_fkey" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "courses" ADD CONSTRAINT "courses_id_specialite_fkey" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "courses" ADD CONSTRAINT "courses_id_niveau_fkey" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_enrollments" ADD CONSTRAINT "course_enrollments_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_enrollments" ADD CONSTRAINT "course_enrollments_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "assignments" ADD CONSTRAINT "assignments_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "assignment_submissions" ADD CONSTRAINT "assignment_submissions_id_devoir_fkey" FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "assignment_submissions" ADD CONSTRAINT "assignment_submissions_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "rubrics" ADD CONSTRAINT "rubrics_id_devoir_fkey" FOREIGN KEY ("id_devoir") REFERENCES "assignments"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "submission_comments" ADD CONSTRAINT "submission_comments_id_soumission_fkey" FOREIGN KEY ("id_soumission") REFERENCES "assignment_submissions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "submission_comments" ADD CONSTRAINT "submission_comments_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_materials" ADD CONSTRAINT "course_materials_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_announcements" ADD CONSTRAINT "course_announcements_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_announcements" ADD CONSTRAINT "course_announcements_id_auteur_fkey" FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "announcement_comments" ADD CONSTRAINT "announcement_comments_id_annonce_fkey" FOREIGN KEY ("id_annonce") REFERENCES "course_announcements"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "announcement_comments" ADD CONSTRAINT "announcement_comments_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "discussions" ADD CONSTRAINT "discussions_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "discussions" ADD CONSTRAINT "discussions_id_auteur_fkey" FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "discussion_replies" ADD CONSTRAINT "discussion_replies_id_discussion_fkey" FOREIGN KEY ("id_discussion") REFERENCES "discussions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "discussion_replies" ADD CONSTRAINT "discussion_replies_id_auteur_fkey" FOREIGN KEY ("id_auteur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_attendance" ADD CONSTRAINT "course_attendance_id_cours_fkey" FOREIGN KEY ("id_cours") REFERENCES "courses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "course_attendance" ADD CONSTRAINT "course_attendance_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ai_chats" ADD CONSTRAINT "ai_chats_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "calendar_events" ADD CONSTRAINT "calendar_events_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
