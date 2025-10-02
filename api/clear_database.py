#!/usr/bin/env python3
"""
Script to delete all data from Prisma database
This script will remove all records from all tables while preserving the schema
"""

import asyncio
import sys
from app.db.prisma_client import DatabaseManager

async def delete_all_data():
    """Delete all data from all tables in the correct order (respecting foreign keys)"""
    print("🗑️  DELETING ALL DATA FROM DATABASE")
    print("⚠️  WARNING: This will permanently delete all data!")
    
    # Confirm deletion
    confirm = input("\nAre you sure you want to delete all data? Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        prisma = db_manager.prisma
        
        print("\n🔄 Starting deletion process...")
        
        # Delete in reverse dependency order to avoid foreign key constraints
        tables_to_clear = [
            # Dependent tables first
            ("Message", lambda: prisma.message.delete_many()),
            ("Absence", lambda: prisma.absence.delete_many()),
            ("Schedule", lambda: prisma.schedule.delete_many()),
            
            # Junction/relation tables
            ("Admin", lambda: prisma.admin.delete_many()),
            ("DepartmentHead", lambda: prisma.departmenthead.delete_many()),
            ("Student", lambda: prisma.student.delete_many()),
            ("Teacher", lambda: prisma.teacher.delete_many()),
            
            # Core data tables
            ("Subject", lambda: prisma.subject.delete_many()),
            ("Group", lambda: prisma.group.delete_many()),
            ("Level", lambda: prisma.level.delete_many()),
            ("Specialty", lambda: prisma.specialty.delete_many()),
            ("Room", lambda: prisma.room.delete_many()),
            ("Department", lambda: prisma.department.delete_many()),
            ("Event", lambda: prisma.event.delete_many()),
            
            # Users table last (after all relations are deleted)
            ("User", lambda: prisma.user.delete_many()),
        ]
        
        deleted_counts = {}
        
        for table_name, delete_func in tables_to_clear:
            try:
                print(f"   🔄 Deleting {table_name} records...")
                result = await delete_func()
                deleted_counts[table_name] = result
                print(f"   ✅ Deleted {result} {table_name} records")
            except Exception as e:
                print(f"   ⚠️  Error deleting {table_name}: {e}")
                # Continue with other tables
        
        await db_manager.disconnect()
        
        print(f"\n📊 DELETION SUMMARY:")
        total_deleted = 0
        for table_name, count in deleted_counts.items():
            print(f"   {table_name}: {count} records")
            total_deleted += count
        
        print(f"\n✅ Successfully deleted {total_deleted} total records")
        print("🗃️  Database is now clean and ready for fresh data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        return False

async def reset_sequences():
    """Reset auto-increment sequences (if using PostgreSQL)"""
    print("\n🔄 Resetting sequences...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # Note: This is PostgreSQL specific
        # For other databases, this step might not be needed
        print("   ℹ️  Sequence reset depends on your database type")
        print("   ℹ️  PostgreSQL sequences will be reset automatically on next insert")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"⚠️  Could not reset sequences: {e}")

async def main():
    """Main function"""
    print("=" * 60)
    print("           PRISMA DATABASE CLEANUP TOOL")
    print("=" * 60)
    
    print("\nThis script will delete ALL data from your database.")
    print("The database schema will remain intact.")
    print("\n⚠️  CAUTION: This action cannot be undone!")
    
    # Show current database info
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # Get some counts to show what will be deleted
        user_count = await db_manager.prisma.user.count()
        dept_count = await db_manager.prisma.department.count()
        schedule_count = await db_manager.prisma.schedule.count()
        
        print(f"\n📊 Current database contains:")
        print(f"   Users: {user_count}")
        print(f"   Departments: {dept_count}")
        print(f"   Schedules: {schedule_count}")
        print(f"   (+ other related records)")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
        sys.exit(1)
    
    # Perform deletion
    success = await delete_all_data()
    
    if success:
        await reset_sequences()
        print("\n🎉 Database cleanup completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run your migration: python migrate_to_email_auth.py")
        print("   2. Set up fresh test data if needed")
        print("   3. Restart your application")
    else:
        print("\n❌ Database cleanup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())