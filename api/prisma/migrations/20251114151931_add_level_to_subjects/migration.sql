-- AlterTable
ALTER TABLE "Subject" ADD COLUMN     "id_niveau" TEXT;

-- CreateIndex
CREATE INDEX "Subject_id_niveau_idx" ON "Subject"("id_niveau");

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_id_niveau_fkey" FOREIGN KEY ("id_niveau") REFERENCES "Level"("id") ON DELETE SET NULL ON UPDATE CASCADE;
