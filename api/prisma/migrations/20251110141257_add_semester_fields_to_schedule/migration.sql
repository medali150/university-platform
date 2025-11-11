-- AlterTable
ALTER TABLE "Schedule" ADD COLUMN     "is_recurring" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "semester" TEXT,
ADD COLUMN     "week_day" INTEGER;

-- CreateIndex
CREATE INDEX "Schedule_semester_idx" ON "Schedule"("semester");

-- CreateIndex
CREATE INDEX "Schedule_is_recurring_idx" ON "Schedule"("is_recurring");
