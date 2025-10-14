/*
  Warnings:

  - The values [PENDING,JUSTIFIED,REFUSED] on the enum `AbsenceStatus` will be removed. If these variants are still used in the database, this will fail.
  - You are about to drop the column `id_emploi` on the `Absence` table. All the data in the column will be lost.
  - You are about to drop the column `justificationUrl` on the `Absence` table. All the data in the column will be lost.
  - Added the required column `id_emploitemps` to the `Absence` table without a default value. This is not possible if the table is not empty.

*/
-- AlterEnum
BEGIN;
CREATE TYPE "AbsenceStatus_new" AS ENUM ('unjustified', 'pending_review', 'justified', 'approved', 'rejected');
ALTER TABLE "Absence" ALTER COLUMN "statut" DROP DEFAULT;
ALTER TABLE "Absence" ALTER COLUMN "statut" TYPE "AbsenceStatus_new" USING ("statut"::text::"AbsenceStatus_new");
ALTER TYPE "AbsenceStatus" RENAME TO "AbsenceStatus_old";
ALTER TYPE "AbsenceStatus_new" RENAME TO "AbsenceStatus";
DROP TYPE "AbsenceStatus_old";
ALTER TABLE "Absence" ALTER COLUMN "statut" SET DEFAULT 'unjustified';
COMMIT;

-- DropForeignKey
ALTER TABLE "Absence" DROP CONSTRAINT "Absence_id_emploi_fkey";

-- DropForeignKey
ALTER TABLE "Subject" DROP CONSTRAINT "Subject_id_enseignant_fkey";

-- DropIndex
DROP INDEX "Absence_id_emploi_idx";

-- AlterTable
ALTER TABLE "Absence" DROP COLUMN "id_emploi",
DROP COLUMN "justificationUrl",
ADD COLUMN     "id_emploitemps" TEXT NOT NULL,
ADD COLUMN     "justification_text" TEXT,
ADD COLUMN     "review_notes" TEXT,
ADD COLUMN     "reviewed_at" TIMESTAMP(3),
ADD COLUMN     "reviewed_by" TEXT,
ADD COLUMN     "supporting_documents" TEXT[] DEFAULT ARRAY[]::TEXT[],
ALTER COLUMN "statut" SET DEFAULT 'unjustified';

-- AlterTable
ALTER TABLE "Subject" ADD COLUMN     "coefficient" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
ALTER COLUMN "id_enseignant" DROP NOT NULL;

-- CreateIndex
CREATE INDEX "Absence_id_emploitemps_idx" ON "Absence"("id_emploitemps");

-- CreateIndex
CREATE INDEX "Absence_statut_idx" ON "Absence"("statut");

-- CreateIndex
CREATE INDEX "Absence_createdAt_idx" ON "Absence"("createdAt");

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_enseignant_fkey" FOREIGN KEY ("id_enseignant") REFERENCES "Teacher"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Absence" ADD CONSTRAINT "Absence_id_emploitemps_fkey" FOREIGN KEY ("id_emploitemps") REFERENCES "Schedule"("id") ON DELETE CASCADE ON UPDATE CASCADE;
