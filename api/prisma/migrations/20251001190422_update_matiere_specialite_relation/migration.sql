/*
  Warnings:

  - You are about to drop the column `id_niveau` on the `Subject` table. All the data in the column will be lost.
  - Added the required column `id_specialite` to the `Subject` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "public"."Subject" DROP CONSTRAINT "Subject_id_niveau_fkey";

-- DropIndex
DROP INDEX "public"."Subject_id_niveau_idx";

-- AlterTable
ALTER TABLE "Subject" DROP COLUMN "id_niveau",
ADD COLUMN     "id_specialite" TEXT NOT NULL;

-- CreateIndex
CREATE INDEX "Subject_id_specialite_idx" ON "Subject"("id_specialite");

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_specialite_fkey" FOREIGN KEY ("id_specialite") REFERENCES "Specialty"("id") ON DELETE CASCADE ON UPDATE CASCADE;
