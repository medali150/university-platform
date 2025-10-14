"""
Check login issue - verify user exists and password is correct
"""

import asyncio
from prisma import Prisma
import bcrypt

async def check_login():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("="*80)
        print("CHECKING LOGIN ISSUE")
        print("="*80)
        
        # Test emails to check
        test_emails = [
            "teacher1@university.tn",
            "chef.dept1@university.tn",
            "student1@university.tn"
        ]
        
        test_password = "Test123!"
        
        for email in test_emails:
            print(f"\n📧 Checking: {email}")
            
            # Find user
            user = await prisma.utilisateur.find_unique(
                where={"email": email}
            )
            
            if not user:
                print(f"   ❌ User NOT found in database!")
                continue
            
            print(f"   ✅ User found")
            print(f"   ID: {user.id}")
            print(f"   Role: {user.role}")
            print(f"   Name: {user.prenom} {user.nom}")
            print(f"   Password hash: {user.mdp_hash[:50]}...")
            
            # Test password
            try:
                password_match = bcrypt.checkpw(
                    test_password.encode('utf-8'),
                    user.mdp_hash.encode('utf-8')
                )
                
                if password_match:
                    print(f"   ✅ Password 'Test123!' is CORRECT")
                else:
                    print(f"   ❌ Password 'Test123!' is WRONG")
                    
                    # Try to generate correct hash
                    correct_hash = bcrypt.hashpw(
                        test_password.encode('utf-8'),
                        bcrypt.gensalt()
                    ).decode('utf-8')
                    print(f"   Correct hash would be: {correct_hash[:50]}...")
                    
            except Exception as e:
                print(f"   ❌ Error checking password: {e}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(check_login())
