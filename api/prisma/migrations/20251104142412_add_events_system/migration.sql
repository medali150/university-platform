/*
  Warnings:

  - You are about to drop the `Event` table. If the table is not empty, all the data it contains will be lost.

*/
-- CreateEnum
CREATE TYPE "GradeType" AS ENUM ('EXAM', 'CONTINUOUS', 'PRACTICAL', 'PROJECT', 'ORAL');

-- CreateEnum
CREATE TYPE "SemesterType" AS ENUM ('SEMESTER_1', 'SEMESTER_2');

-- AlterTable
ALTER TABLE "Student" ADD COLUMN     "id_niveau" TEXT;

-- DropTable
DROP TABLE "Event";

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
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

-- CreateTable
CREATE TABLE "event_comments" (
    "id" TEXT NOT NULL,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "event_comments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "event_reactions" (
    "id" TEXT NOT NULL,
    "id_evenement" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "event_reactions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "grades_id_etudiant_idx" ON "grades"("id_etudiant");

-- CreateIndex
CREATE INDEX "grades_id_matiere_idx" ON "grades"("id_matiere");

-- CreateIndex
CREATE INDEX "grades_id_enseignant_idx" ON "grades"("id_enseignant");

-- CreateIndex
CREATE INDEX "grades_semestre_annee_scolaire_idx" ON "grades"("semestre", "annee_scolaire");

-- CreateIndex
CREATE INDEX "averages_id_etudiant_idx" ON "averages"("id_etudiant");

-- CreateIndex
CREATE INDEX "averages_id_matiere_idx" ON "averages"("id_matiere");

-- CreateIndex
CREATE INDEX "averages_semestre_annee_scolaire_idx" ON "averages"("semestre", "annee_scolaire");

-- CreateIndex
CREATE INDEX "averages_validee_idx" ON "averages"("validee");

-- CreateIndex
CREATE UNIQUE INDEX "averages_id_etudiant_id_matiere_semestre_annee_scolaire_key" ON "averages"("id_etudiant", "id_matiere", "semestre", "annee_scolaire");

-- CreateIndex
CREATE INDEX "grade_reports_id_etudiant_idx" ON "grade_reports"("id_etudiant");

-- CreateIndex
CREATE INDEX "grade_reports_semestre_annee_scolaire_idx" ON "grade_reports"("semestre", "annee_scolaire");

-- CreateIndex
CREATE INDEX "grade_reports_envoye_idx" ON "grade_reports"("envoye");

-- CreateIndex
CREATE UNIQUE INDEX "grade_reports_id_etudiant_semestre_annee_scolaire_key" ON "grade_reports"("id_etudiant", "semestre", "annee_scolaire");

-- CreateIndex
CREATE INDEX "events_id_createur_idx" ON "events"("id_createur");

-- CreateIndex
CREATE INDEX "events_type_idx" ON "events"("type");

-- CreateIndex
CREATE INDEX "events_date_idx" ON "events"("date");

-- CreateIndex
CREATE INDEX "event_comments_id_evenement_idx" ON "event_comments"("id_evenement");

-- CreateIndex
CREATE INDEX "event_comments_id_utilisateur_idx" ON "event_comments"("id_utilisateur");

-- CreateIndex
CREATE INDEX "event_reactions_id_evenement_idx" ON "event_reactions"("id_evenement");

-- CreateIndex
CREATE INDEX "event_reactions_id_utilisateur_idx" ON "event_reactions"("id_utilisateur");

-- CreateIndex
CREATE UNIQUE INDEX "event_reactions_id_evenement_id_utilisateur_key" ON "event_reactions"("id_evenement", "id_utilisateur");

-- CreateIndex
CREATE INDEX "Student_id_niveau_idx" ON "Student"("id_niveau");

-- AddForeignKey
ALTER TABLE "Student" ADD CONSTRAINT "Student_id_niveau_fkey" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "grades" ADD CONSTRAINT "grades_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "grades" ADD CONSTRAINT "grades_id_matiere_fkey" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "grades" ADD CONSTRAINT "grades_id_enseignant_fkey" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "averages" ADD CONSTRAINT "averages_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "averages" ADD CONSTRAINT "averages_id_matiere_fkey" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "grade_reports" ADD CONSTRAINT "grade_reports_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "events" ADD CONSTRAINT "events_id_createur_fkey" FOREIGN KEY ("id_createur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_comments" ADD CONSTRAINT "event_comments_id_evenement_fkey" FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_comments" ADD CONSTRAINT "event_comments_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_reactions" ADD CONSTRAINT "event_reactions_id_evenement_fkey" FOREIGN KEY ("id_evenement") REFERENCES "events"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "event_reactions" ADD CONSTRAINT "event_reactions_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
