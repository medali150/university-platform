"""
Database Reset and Migration Script
Handles Prisma database reset, migration, and setup
"""
import subprocess
import sys
import os
import asyncio
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"   Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def main():
    """Main reset and setup function"""
    print("🚀 University Platform Database Reset & Setup")
    print("=" * 50)
    
    # Change to API directory
    api_dir = Path(__file__).parent
    os.chdir(api_dir)
    print(f"📁 Working directory: {api_dir}")
    
    # Step 1: Reset database
    if not run_command("python -m prisma db push --force-reset", "Resetting database"):
        print("⚠️ Database reset failed, continuing anyway...")
    
    # Step 2: Generate Prisma client
    if not run_command("python -m prisma generate", "Generating Prisma client"):
        print("❌ Failed to generate Prisma client")
        return False
    
    # Step 3: Push schema to database
    if not run_command("python -m prisma db push", "Pushing schema to database"):
        print("❌ Failed to push schema")
        return False
    
    # Step 4: Run the complete database setup
    print("\n🎯 Starting complete database setup...")
    try:
        # Import and run the setup script
        from setup_complete_database import create_complete_database
        asyncio.run(create_complete_database())
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database reset and setup completed successfully!")
        print("🚀 You can now start the server with: uvicorn app.main:app --reload")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")
        sys.exit(1)