#!/usr/bin/env python3
"""
Fix null teacher records in the database
"""

import asyncio
from prisma import Prisma

async def fix_null_teachers():
    """Fix subjects with null teachers"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Find subjects with null teachers
        subjects_with_null_teachers = await prisma.matiere.find_many(
            where={'id_enseignant': None}
        )
        
        print(f'🔍 Found {len(subjects_with_null_teachers)} subjects with null teachers')
        
        if subjects_with_null_teachers:
            # Instead of assigning random teachers, let's delete these records
            # since they might be test data or incomplete records
            
            print("🗑️  Deleting subjects with null teachers...")
            deleted = await prisma.matiere.delete_many(
                where={'id_enseignant': None}
            )
            print(f"✅ Deleted {deleted} subjects with null teachers")
        else:
            print("✅ No subjects with null teachers found")
        
        # Check remaining subjects
        remaining_subjects = await prisma.matiere.count()
        print(f"📊 Total subjects remaining: {remaining_subjects}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_null_teachers())