import asyncio
import requests
from prisma import Prisma

async def test_authentication():
    """Test subjects endpoint authentication"""
    try:
        # First check what users exist
        prisma = Prisma()
        await prisma.connect()
        
        # Get users with different roles
        print("Looking for users...")
        
        # Get all users to see the structure
        all_users = await prisma.utilisateur.find_many()
        print(f"Total users: {len(all_users)}")
        
        # Show first few users with their roles
        for user in all_users[:5]:  # Show first 5
            print(f"  - {user.email} ({user.nom} {user.prenom}) - Role: {getattr(user, 'role', 'No role field')}")
        
        # Find admin and department head users manually
        admin_users = [u for u in all_users if hasattr(u, 'role') and u.role == 'ADMIN']
        dept_users = [u for u in all_users if hasattr(u, 'role') and u.role == 'DEPARTMENT_HEAD']
        
        print(f"ADMIN users: {len(admin_users)}")
        print(f"DEPARTMENT_HEAD users: {len(dept_users)}")
        
        await prisma.disconnect()
        
        # Test login with a department head user first, fallback to admin
        if dept_users:
            test_user = dept_users[0]
            print(f"Testing with DEPARTMENT_HEAD user: {test_user.email}")
        elif admin_users:
            test_user = admin_users[0]
            print(f"Testing with ADMIN user: {test_user.email}")
        else:
            print("No suitable users found")
            return
        # Try to login (we'll need to guess password or create one)
        login_data = {
            'email': test_user.email,
            'password': 'password123'  # Common test password
        }
        
        response = requests.post('http://localhost:8000/auth/login', json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print("✅ Login successful")
            
            # Test subjects endpoint with new department-head endpoint
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('http://localhost:8000/department-head/subjects/', headers=headers)
            print(f"Department Head Subjects endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('subjects', []))} subjects")
            else:
                print(f"❌ Error: {response.text[:200]}")
        else:
            print(f"❌ Login failed: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_authentication())