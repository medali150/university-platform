-- CreateEnum
CREATE TYPE "Role" AS ENUM ('STUDENT', 'TEACHER', 'DEPARTMENT_HEAD', 'ADMIN');

-- CreateEnum
CREATE TYPE "AbsenceStatus" AS ENUM ('PENDING', 'JUSTIFIED', 'REFUSED');

-- CreateEnum
CREATE TYPE "RoomType" AS ENUM ('LECTURE', 'LAB', 'EXAM', 'OTHER');

-- CreateEnum
CREATE TYPE "ScheduleStatus" AS ENUM ('PLANNED', 'CANCELED', 'MAKEUP');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "role" "Role" NOT NULL,
    "mdp_hash" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "enseignant_id" TEXT,
    "etudiant_id" TEXT,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Department" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Department_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Specialty" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Specialty_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Level" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Level_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Group" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Room" (
    "id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "type" "RoomType" NOT NULL,
    "capacite" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Room_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Teacher" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Teacher_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Student" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "prenom" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "id_groupe" TEXT NOT NULL,
    "id_specialite" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Student_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Subject" (
    "id" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "id_niveau" TEXT NOT NULL,
    "id_enseignant" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Subject_pkey" PRIMARY KEY ("id")
);

-- CreateTable
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
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Schedule_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Absence" (
    "id" TEXT NOT NULL,
    "id_etudiant" TEXT NOT NULL,
    "id_emploi" TEXT NOT NULL,
    "motif" TEXT,
    "statut" "AbsenceStatus" NOT NULL DEFAULT 'PENDING',
    "justificationUrl" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Absence_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Event" (
    "id" TEXT NOT NULL,
    "titre" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Event_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DepartmentHead" (
    "id" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "id_departement" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "DepartmentHead_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Admin" (
    "id" TEXT NOT NULL,
    "id_utilisateur" TEXT NOT NULL,
    "niveau" TEXT NOT NULL DEFAULT 'ADMIN',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Admin_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "id_expediteur" TEXT NOT NULL,
    "id_destinataire" TEXT NOT NULL,
    "contenu" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "User_enseignant_id_key" ON "User"("enseignant_id");

-- CreateIndex
CREATE UNIQUE INDEX "User_etudiant_id_key" ON "User"("etudiant_id");

-- CreateIndex
CREATE INDEX "User_role_idx" ON "User"("role");

-- CreateIndex
CREATE INDEX "User_email_idx" ON "User"("email");

-- CreateIndex
CREATE INDEX "User_enseignant_id_idx" ON "User"("enseignant_id");

-- CreateIndex
CREATE INDEX "User_etudiant_id_idx" ON "User"("etudiant_id");

-- CreateIndex
CREATE UNIQUE INDEX "Department_nom_key" ON "Department"("nom");

-- CreateIndex
CREATE INDEX "Specialty_id_departement_idx" ON "Specialty"("id_departement");

-- CreateIndex
CREATE INDEX "Level_id_specialite_idx" ON "Level"("id_specialite");

-- CreateIndex
CREATE INDEX "Group_id_niveau_idx" ON "Group"("id_niveau");

-- CreateIndex
CREATE UNIQUE INDEX "Room_code_key" ON "Room"("code");

-- CreateIndex
CREATE UNIQUE INDEX "Teacher_email_key" ON "Teacher"("email");

-- CreateIndex
CREATE INDEX "Teacher_id_departement_idx" ON "Teacher"("id_departement");

-- CreateIndex
CREATE INDEX "Teacher_email_idx" ON "Teacher"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Student_email_key" ON "Student"("email");

-- CreateIndex
CREATE INDEX "Student_id_groupe_idx" ON "Student"("id_groupe");

-- CreateIndex
CREATE INDEX "Student_id_specialite_idx" ON "Student"("id_specialite");

-- CreateIndex
CREATE INDEX "Student_email_idx" ON "Student"("email");

-- CreateIndex
CREATE INDEX "Subject_id_niveau_idx" ON "Subject"("id_niveau");

-- CreateIndex
CREATE INDEX "Subject_id_enseignant_idx" ON "Subject"("id_enseignant");

-- CreateIndex
CREATE INDEX "Schedule_date_idx" ON "Schedule"("date");

-- CreateIndex
CREATE INDEX "Schedule_id_salle_idx" ON "Schedule"("id_salle");

-- CreateIndex
CREATE INDEX "Schedule_id_enseignant_idx" ON "Schedule"("id_enseignant");

-- CreateIndex
CREATE INDEX "Schedule_id_groupe_idx" ON "Schedule"("id_groupe");

-- CreateIndex
CREATE INDEX "Absence_id_etudiant_idx" ON "Absence"("id_etudiant");

-- CreateIndex
CREATE INDEX "Absence_id_emploi_idx" ON "Absence"("id_emploi");

-- CreateIndex
CREATE UNIQUE INDEX "DepartmentHead_id_utilisateur_key" ON "DepartmentHead"("id_utilisateur");

-- CreateIndex
CREATE UNIQUE INDEX "DepartmentHead_id_departement_key" ON "DepartmentHead"("id_departement");

-- CreateIndex
CREATE INDEX "DepartmentHead_id_departement_idx" ON "DepartmentHead"("id_departement");

-- CreateIndex
CREATE UNIQUE INDEX "Admin_id_utilisateur_key" ON "Admin"("id_utilisateur");

-- CreateIndex
CREATE INDEX "Admin_niveau_idx" ON "Admin"("niveau");

-- CreateIndex
CREATE INDEX "Message_id_expediteur_createdAt_idx" ON "Message"("id_expediteur", "createdAt");

-- CreateIndex
CREATE INDEX "Message_id_destinataire_createdAt_idx" ON "Message"("id_destinataire", "createdAt");

-- AddForeignKey
ALTER TABLE "User" ADD CONSTRAINT "User_enseignant_id_fkey" FOREIGN KEY ("enseignant_id") REFERENCES "Teacher"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "User" ADD CONSTRAINT "User_etudiant_id_fkey" FOREIGN KEY ("etudiant_id") REFERENCES "Student"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Specialty" ADD CONSTRAINT "Specialty_id_departement_fkey" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Level" ADD CONSTRAINT "Level_id_specialite_fkey" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Group" ADD CONSTRAINT "Group_id_niveau_fkey" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Teacher" ADD CONSTRAINT "Teacher_id_departement_fkey" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Student" ADD CONSTRAINT "Student_id_groupe_fkey" FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Student" ADD CONSTRAINT "Student_id_specialite_fkey" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_niveau_fkey" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_enseignant_fkey" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_salle_fkey" FOREIGN KEY ("id_salle") REFERENCES "Room"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_matiere_fkey" FOREIGN KEY ("id_matiere") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_groupe_fkey" FOREIGN KEY ("id_groupe") REFERENCES "Group"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Schedule" ADD CONSTRAINT "Schedule_id_enseignant_fkey" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Absence" ADD CONSTRAINT "Absence_id_etudiant_fkey" FOREIGN KEY ("id_etudiant") REFERENCES "Student"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Absence" ADD CONSTRAINT "Absence_id_emploi_fkey" FOREIGN KEY ("id_emploi") REFERENCES "Schedule"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DepartmentHead" ADD CONSTRAINT "DepartmentHead_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DepartmentHead" ADD CONSTRAINT "DepartmentHead_id_departement_fkey" FOREIGN KEY ("id_departement") REFERENCES "Department"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Admin" ADD CONSTRAINT "Admin_id_utilisateur_fkey" FOREIGN KEY ("id_utilisateur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_id_expediteur_fkey" FOREIGN KEY ("id_expediteur") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_id_destinataire_fkey" FOREIGN KEY ("id_destinataire") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
