import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing University Management API")
    print("=" * 50)
    
    # Test 1: Check API status
    print("\n1. Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API Status: OK")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ API Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check: OK")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Create a department
    print("\n3. Testing department creation...")
    dept_data = {
        "name": "Computer Science"
    }
    try:
        response = requests.post(f"{BASE_URL}/departments", json=dept_data)
        if response.status_code == 200:
            print("✅ Department created successfully")
            dept_response = response.json()
            print(f"   Department ID: {dept_response['department']['id']}")
            department_id = dept_response['department']['id']
        else:
            print(f"❌ Department creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Department creation error: {e}")
        return
    
    # Test 4: Get all departments
    print("\n4. Testing get all departments...")
    try:
        response = requests.get(f"{BASE_URL}/departments")
        if response.status_code == 200:
            print("✅ Get departments: OK")
            departments = response.json()['departments']
            print(f"   Found {len(departments)} departments")
            for dept in departments:
                print(f"   - {dept['name']} (ID: {dept['id']})")
        else:
            print(f"❌ Get departments failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get departments error: {e}")
    
    # Test 5: Create a specialty
    print("\n5. Testing specialty creation...")
    specialty_data = {
        "name": "Software Engineering",
        "departmentId": department_id
    }
    try:
        response = requests.post(f"{BASE_URL}/specialties", json=specialty_data)
        if response.status_code == 200:
            print("✅ Specialty created successfully")
            specialty_response = response.json()
            print(f"   Specialty: {specialty_response['specialty']['name']}")
            print(f"   Department: {specialty_response['specialty']['department']['name']}")
        else:
            print(f"❌ Specialty creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Specialty creation error: {e}")
    
    # Test 6: Get all specialties
    print("\n6. Testing get all specialties...")
    try:
        response = requests.get(f"{BASE_URL}/specialties")
        if response.status_code == 200:
            print("✅ Get specialties: OK")
            specialties = response.json()['specialties']
            print(f"   Found {len(specialties)} specialties")
            for spec in specialties:
                print(f"   - {spec['name']} (Department: {spec['department']['name']})")
        else:
            print(f"❌ Get specialties failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get specialties error: {e}")
    
    # Test 7: Create users for different roles
    print("\n7. Testing user creation for different roles...")
    users_to_create = [
        {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@university.edu",
            "login": "johndoe",
            "password": "securepassword123",
            "role": "STUDENT"
        },
        {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@university.edu",
            "login": "janesmith",
            "password": "securepassword456",
            "role": "TEACHER"
        },
        {
            "firstName": "Dr. Robert",
            "lastName": "Johnson",
            "email": "robert.johnson@university.edu",
            "login": "robertjohnson",
            "password": "securepassword789",
            "role": "DEPARTMENT_HEAD"
        },
        {
            "firstName": "Alice",
            "lastName": "Brown",
            "email": "alice.brown@university.edu",
            "login": "alicebrown",
            "password": "securepassword000",
            "role": "ADMIN"
        }
    ]
    
    created_users = {}
    for user_data in users_to_create:
        try:
            response = requests.post(f"{BASE_URL}/users", json=user_data)
            if response.status_code == 200:
                print(f"✅ {user_data['role']} user created: {user_data['firstName']} {user_data['lastName']}")
                user_response = response.json()
                created_users[user_data['role']] = user_response['user']['id']
            else:
                print(f"❌ {user_data['role']} user creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ {user_data['role']} user creation error: {e}")
    
    # Test 8: Get all users
    print("\n8. Testing get all users...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            print("✅ Get users: OK")
            users = response.json()['users']
            print(f"   Found {len(users)} users")
            for user in users:
                print(f"   - {user['firstName']} {user['lastName']} ({user['role']})")
        else:
            print(f"❌ Get users failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get users error: {e}")
    
    # Test 9: Create a department head
    print("\n9. Testing department head creation...")
    if 'DEPARTMENT_HEAD' in created_users:
        dept_head_data = {
            "userId": created_users['DEPARTMENT_HEAD'],
            "departmentId": department_id
        }
        try:
            response = requests.post(f"{BASE_URL}/department-heads", json=dept_head_data)
            if response.status_code == 200:
                print("✅ Department head created successfully")
                dept_head_response = response.json()
                print(f"   Head: {dept_head_response['department_head']['user']['firstName']} {dept_head_response['department_head']['user']['lastName']}")
                print(f"   Department: {dept_head_response['department_head']['department']['name']}")
            else:
                print(f"❌ Department head creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Department head creation error: {e}")
    else:
        print("⚠️ Skipping department head creation - no DEPARTMENT_HEAD user created")
    
    # Test 10: Get all department heads
    print("\n10. Testing get all department heads...")
    try:
        response = requests.get(f"{BASE_URL}/department-heads")
        if response.status_code == 200:
            print("✅ Get department heads: OK")
            dept_heads = response.json()['department_heads']
            print(f"   Found {len(dept_heads)} department heads")
            for head in dept_heads:
                print(f"   - {head['user']['firstName']} {head['user']['lastName']} (Dept: {head['department']['name']})")
        else:
            print(f"❌ Get department heads failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get department heads error: {e}")
    
    # Test 11: Create an admin
    print("\n11. Testing admin creation...")
    if 'ADMIN' in created_users:
        admin_data = {
            "userId": created_users['ADMIN'],
            "level": "ADMIN"
        }
        try:
            response = requests.post(f"{BASE_URL}/admins", json=admin_data)
            if response.status_code == 200:
                print("✅ Admin created successfully")
                admin_response = response.json()
                print(f"   Admin: {admin_response['admin']['user']['firstName']} {admin_response['admin']['user']['lastName']}")
                print(f"   Level: {admin_response['admin']['level']}")
            else:
                print(f"❌ Admin creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Admin creation error: {e}")
    else:
        print("⚠️ Skipping admin creation - no ADMIN user created")
    
    # Test 12: Get all admins
    print("\n12. Testing get all admins...")
    try:
        response = requests.get(f"{BASE_URL}/admins")
        if response.status_code == 200:
            print("✅ Get admins: OK")
            admins = response.json()['admins']
            print(f"   Found {len(admins)} admins")
            for admin in admins:
                print(f"   - {admin['user']['firstName']} {admin['user']['lastName']} (Level: {admin['level']})")
        else:
            print(f"❌ Get admins failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get admins error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\n💡 You can also test these endpoints manually:")
    print(f"   • API Docs: {BASE_URL}/docs")
    print(f"   • Health: {BASE_URL}/health")
    print(f"   • Users: {BASE_URL}/users")
    print(f"   • Departments: {BASE_URL}/departments")
    print(f"   • Specialties: {BASE_URL}/specialties")
    print(f"   • Department Heads: {BASE_URL}/department-heads")
    print(f"   • Admins: {BASE_URL}/admins")

if __name__ == "__main__":
    test_api()