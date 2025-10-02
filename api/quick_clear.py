#!/usr/bin/env python3
"""
Quick script to delete all data from Prisma database (no confirmation)
Use this for rapid development/testing cycles
"""

import asyncio
from app.db.prisma_client import DatabaseManager

async def quick_clear():
    """Quickly delete all data without confirmation"""
    print("🗑️  Quick database clear...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        prisma = db_manager.prisma
        
        # Delete in dependency order
        tables_to_clear = [
            ("messages", prisma.message.delete_many()),
            ("absences", prisma.absence.delete_many()),
            ("schedules", prisma.schedule.delete_many()),
            ("admins", prisma.admin.delete_many()),
            ("department_heads", prisma.departmenthead.delete_many()),
            ("students", prisma.student.delete_many()),
            ("teachers", prisma.teacher.delete_many()),
            ("subjects", prisma.subject.delete_many()),
            ("groups", prisma.group.delete_many()),
            ("levels", prisma.level.delete_many()),
            ("specialties", prisma.specialty.delete_many()),
            ("rooms", prisma.room.delete_many()),
            ("departments", prisma.department.delete_many()),
            ("events", prisma.event.delete_many()),
            ("users", prisma.user.delete_many()),
        ]
        
        total = 0
        for name, delete_operation in tables_to_clear:
            try:
                count = await delete_operation
                total += count
                print(f"   ✅ {name}: {count}")
            except Exception as e:
                print(f"   ⚠️  {name}: {e}")
        
        await db_manager.disconnect()
        print(f"✅ Deleted {total} records total")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_clear())