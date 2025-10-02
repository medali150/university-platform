"""
Check Available Absence Management Endpoints
This script checks what endpoints are available for absence management
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def check_swagger_endpoints():
    """Check what absence-related endpoints are available in the API"""
    async with httpx.AsyncClient() as client:
        try:
            # Get the OpenAPI spec
            response = await client.get(f"{BASE_URL}/openapi.json")
            if response.status_code != 200:
                print("❌ Could not fetch API specification")
                return
            
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print("🔍 Checking for absence-related endpoints:")
            print("=" * 50)
            
            absence_endpoints = []
            for path, methods in paths.items():
                if "absence" in path.lower():
                    absence_endpoints.append((path, list(methods.keys())))
            
            if absence_endpoints:
                print(f"✅ Found {len(absence_endpoints)} absence-related endpoints:")
                for path, methods in absence_endpoints:
                    print(f"  {path}")
                    for method in methods:
                        operation = methods[method] if isinstance(methods, dict) else {}
                        summary = operation.get("summary", "No description") if isinstance(operation, dict) else "No description"
                        print(f"    {method.upper()}: {summary}")
                    print()
            else:
                print("❌ No absence-related endpoints found in API spec")
                
                # Let's check for teacher-related endpoints
                print("\n🔍 Checking for teacher-related endpoints:")
                teacher_endpoints = []
                for path, methods in paths.items():
                    if "teacher" in path.lower():
                        teacher_endpoints.append((path, list(methods.keys())))
                
                if teacher_endpoints:
                    print(f"Found {len(teacher_endpoints)} teacher-related endpoints:")
                    for path, methods in teacher_endpoints:
                        print(f"  {path}")
                        for method in methods:
                            print(f"    {method.upper()}")
                
        except Exception as e:
            print(f"❌ Error checking endpoints: {str(e)}")

async def test_server_health():
    """Test if the server is running"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Server is running and healthy")
                data = response.json()
                print(f"Database status: {data.get('database', 'unknown')}")
                return True
            else:
                print(f"⚠️ Server responding but not healthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server is not running: {str(e)}")
            return False

async def main():
    print("🔍 Checking Absence Management API Availability")
    print("=" * 50)
    
    # Check if server is running
    if await test_server_health():
        await check_swagger_endpoints()
    else:
        print("⚠️ Please start the server first with: python run_server.py")

if __name__ == "__main__":
    asyncio.run(main())