#!/usr/bin/env python3
"""
Test script to verify backend API endpoints for timetable data
"""
import asyncio
import requests
import json
from prisma import Prisma

async def test_backend_data():
    """Test if backend endpoints are working"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Check if we have a department head user
        print("🔍 Checking department head users...")
        dept_heads = await prisma.chefdepartement.find_many(
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        
        if not dept_heads:
            print("❌ No department head users found!")
            
            # Check if we have users with DEPARTMENT_HEAD role
            dept_head_users = await prisma.utilisateur.find_many(
                where={"role": "DEPARTMENT_HEAD"}
            )
            
            if dept_head_users:
                print(f"📋 Found {len(dept_head_users)} users with DEPARTMENT_HEAD role:")
                for user in dept_head_users:
                    print(f"   • {user.prenom} {user.nom} ({user.email})")
                    
                # Create ChefDepartement record for the first department head user
                departments = await prisma.departement.find_many()
                if departments and dept_head_users:
                    print(f"🔧 Creating ChefDepartement record...")
                    chef = await prisma.chefdepartement.create(
                        data={
                            "id_utilisateur": dept_head_users[0].id,
                            "id_departement": departments[0].id
                        }
                    )
                    print(f"✅ Created department head: {dept_head_users[0].email} for {departments[0].nom}")
            else:
                print("❌ No users with DEPARTMENT_HEAD role found!")
                return
        else:
            print(f"✅ Found {len(dept_heads)} department head users:")
            for chef in dept_heads:
                print(f"   • {chef.utilisateur.prenom} {chef.utilisateur.nom} - {chef.departement.nom}")
        
        # Check data counts
        print("\n📊 Database content:")
        
        groups_count = await prisma.groupe.count()
        print(f"   👥 Groups: {groups_count}")
        
        specialities_count = await prisma.specialite.count()
        print(f"   🎓 Specialities: {specialities_count}")
        
        subjects_count = await prisma.matiere.count()
        print(f"   📚 Subjects: {subjects_count}")
        
        teachers_count = await prisma.enseignant.count()
        print(f"   👨‍🏫 Teachers: {teachers_count}")
        
        rooms_count = await prisma.salle.count()
        print(f"   🏛️ Rooms: {rooms_count}")
        
        # Test specific data for Informatique department
        print("\n🖥️ Informatique Department Data:")
        
        informatique_dept = await prisma.departement.find_first(
            where={"nom": "Informatique"}
        )
        
        if informatique_dept:
            # Get groups in Informatique department
            groups = await prisma.groupe.find_many(
                where={
                    "niveau": {
                        "specialite": {
                            "id_departement": informatique_dept.id
                        }
                    }
                },
                include={
                    "niveau": {
                        "include": {
                            "specialite": True
                        }
                    }
                }
            )
            print(f"   👥 Groups: {len(groups)}")
            for group in groups:
                print(f"      • {group.nom} ({group.niveau.specialite.nom})")
            
            # Get specialities in Informatique department
            specialities = await prisma.specialite.find_many(
                where={"id_departement": informatique_dept.id}
            )
            print(f"   🎓 Specialities: {len(specialities)}")
            for spec in specialities:
                print(f"      • {spec.nom}")
            
            # Get subjects in Informatique department
            subjects = await prisma.matiere.find_many(
                where={
                    "specialite": {
                        "id_departement": informatique_dept.id
                    }
                },
                include={
                    "specialite": True,
                    "enseignant": True
                }
            )
            print(f"   📚 Subjects: {len(subjects)}")
            for subject in subjects:
                print(f"      • {subject.nom} ({subject.specialite.nom}) - {subject.enseignant.nom}")
        
        # Check if we have test login credentials
        print("\n🔐 Test Login Info:")
        test_user = await prisma.utilisateur.find_first(
            where={
                "role": "DEPARTMENT_HEAD",
                "email": {"contains": "@"}
            }
        )
        
        if test_user:
            print(f"   📧 Test Email: {test_user.email}")
            print(f"   👤 Name: {test_user.prenom} {test_user.nom}")
            print("   🔑 Try logging in with this email and password")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_backend_data())