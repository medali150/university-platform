"""
Debug script for auth registration issues
"""
import asyncio
from prisma import Prisma
import traceback

async def debug_auth_registration():
    """Debug the auth registration process"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Debugging Auth Registration Issues\n")
        
        # Check if basic tables exist and have data
        print("1. Checking database structure...")
        
        # Check users table
        try:
            users_count = await prisma.utilisateur.count()
            print(f"   ✅ Users table exists: {users_count} users")
        except Exception as e:
            print(f"   ❌ Users table issue: {str(e)}")
        
        # Check departments table
        try:
            departments = await prisma.departement.find_many()
            print(f"   ✅ Departments table exists: {len(departments)} departments")
            for dept in departments:
                print(f"      - {dept.nom} (ID: {dept.id})")
        except Exception as e:
            print(f"   ❌ Departments table issue: {str(e)}")
        
        # Check specialites table
        try:
            specialites = await prisma.specialite.find_many()
            print(f"   ✅ Specialites table exists: {len(specialites)} specialites")
        except Exception as e:
            print(f"   ❌ Specialites table issue: {str(e)}")
        
        # Check groupes table
        try:
            groupes = await prisma.groupe.find_many()
            print(f"   ✅ Groups table exists: {len(groupes)} groups")
        except Exception as e:
            print(f"   ❌ Groups table issue: {str(e)}")
        
        # Check chef departement table
        try:
            chef_depts = await prisma.chefdepartement.find_many()
            print(f"   ✅ ChefDepartement table exists: {len(chef_depts)} department heads")
        except Exception as e:
            print(f"   ❌ ChefDepartement table issue: {str(e)}")
        
        print("\n2. Testing department head creation...")
        
        # Get the department ID from the error
        test_dept_id = "cmgf7np350000bmb0jj5odswj"
        
        # Check if this department exists
        try:
            test_dept = await prisma.departement.find_unique(
                where={"id": test_dept_id}
            )
            
            if test_dept:
                print(f"   ✅ Test department exists: {test_dept.nom}")
            else:
                print(f"   ❌ Test department ID {test_dept_id} does not exist")
                
                # Show available departments
                all_depts = await prisma.departement.find_many()
                print(f"   Available departments:")
                for dept in all_depts:
                    print(f"      - {dept.nom}: {dept.id}")
                    
        except Exception as e:
            print(f"   ❌ Error checking test department: {str(e)}")
        
        print("\n3. Testing user creation process...")
        
        # Test creating a test user and department head
        try:
            # Check if we can create a basic user
            test_email = "test_debug@university.tn"
            
            # Clean up any existing test user
            existing_user = await prisma.utilisateur.find_unique(
                where={"email": test_email}
            )
            if existing_user:
                print(f"   🗑️ Cleaning up existing test user")
                await prisma.utilisateur.delete(where={"id": existing_user.id})
            
            # Create test user
            test_user = await prisma.utilisateur.create(
                data={
                    "prenom": "Test",
                    "nom": "Debug",
                    "email": test_email,
                    "mdp_hash": "test_hash",
                    "role": "DEPARTMENT_HEAD"
                }
            )
            print(f"   ✅ Test user created: {test_user.id}")
            
            # Try to create department head record
            if departments:
                test_dept_head = await prisma.chefdepartement.create(
                    data={
                        "id_utilisateur": test_user.id,
                        "id_departement": departments[0].id
                    }
                )
                print(f"   ✅ Test department head created: {test_dept_head.id}")
                
                # Clean up
                await prisma.chefdepartement.delete(where={"id": test_dept_head.id})
                print(f"   🗑️ Test department head deleted")
            
            # Clean up test user
            await prisma.utilisateur.delete(where={"id": test_user.id})
            print(f"   🗑️ Test user deleted")
            
        except Exception as e:
            print(f"   ❌ Error in user creation test: {str(e)}")
            traceback.print_exc()
        
        print("\n4. Checking foreign key constraints...")
        
        # Check if there are any constraint issues
        try:
            # Try to find any orphaned records
            users_with_invalid_enseignant = await prisma.utilisateur.find_many(
                where={
                    "enseignant_id": {"not": None}
                },
                include={"enseignant": True}
            )
            
            invalid_count = 0
            for user in users_with_invalid_enseignant:
                if not user.enseignant:
                    invalid_count += 1
            
            if invalid_count > 0:
                print(f"   ⚠️ Found {invalid_count} users with invalid enseignant references")
            else:
                print(f"   ✅ All user-enseignant relations are valid")
                
        except Exception as e:
            print(f"   ❌ Error checking constraints: {str(e)}")
            
    except Exception as e:
        print(f"❌ Overall error: {str(e)}")
        traceback.print_exc()
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_auth_registration())