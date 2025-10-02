import asyncio
import subprocess
import sys
import os

async def force_clear_database():
    """Force clear all database data and reset schema"""
    print("🗑️  Force clearing database...")
    
    try:
        # Force reset database with Prisma
        print("📝 Running Prisma DB push with force reset...")
        result = subprocess.run([
            "npx", "prisma", "db", "push", "--force-reset", "--accept-data-loss"
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ Database cleared and schema applied!")
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
            
        # Generate Prisma client
        print("🔧 Generating Prisma client...")
        result2 = subprocess.run([
            "npx", "prisma", "generate"
        ], capture_output=True, text=True, shell=True)
        
        if result2.returncode == 0:
            print("✅ Prisma client generated!")
        else:
            print(f"❌ Client generation error: {result2.stderr}")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    asyncio.run(force_clear_database())