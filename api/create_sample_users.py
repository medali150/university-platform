#!/usr/bin/env python3
"""
Create sample users for testing
"""
import asyncio
from prisma import Prisma
from app.core.security import hash_password

async def create_sample_users():
    """Create sample users for testing"""
    print("📝 Creating sample users...")
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Create admin user
        admin_user = await prisma.utilisateur.create({
            "nom": "Admin",
            "prenom": "System",
            "email": "admin@university.com",
            "login": "admin",
            "role": "ADMIN",
            "mdp_hash": hash_password("admin123")
        })
        print(f"✅ Created admin user: {admin_user.email}")
        
        # Create teacher user
        teacher_user = await prisma.utilisateur.create({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@university.com",
            "login": "jdupont",
            "role": "TEACHER",
            "mdp_hash": hash_password("teacher123")
        })
        print(f"✅ Created teacher user: {teacher_user.email}")
        
        # Create student user
        student_user = await prisma.utilisateur.create({
            "nom": "Martin",
            "prenom": "Marie",
            "email": "marie.martin@student.university.edu",
            "login": "mmartin",
            "role": "STUDENT",
            "mdp_hash": hash_password("student123")
        })
        print(f"✅ Created student user: {student_user.email}")
        
        # Create department head user
        dept_head_user = await prisma.utilisateur.create({
            "nom": "Leclerc",
            "prenom": "Pierre",
            "email": "pierre.leclerc@university.com",
            "login": "pleclerc",
            "role": "DEPARTMENT_HEAD",
            "mdp_hash": hash_password("depthead123")
        })
        print(f"✅ Created department head user: {dept_head_user.email}")
        
        print("\n🎉 Sample users created successfully!")
        print("\n📧 Test credentials:")
        print("   👨‍💼 Admin: admin@university.com / admin123")
        print("   👨‍🏫 Teacher: jean.dupont@university.com / teacher123")
        print("   🎓 Student: marie.martin@student.university.edu / student123")
        print("   🏢 Dept Head: pierre.leclerc@university.com / depthead123")
        
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_sample_users())