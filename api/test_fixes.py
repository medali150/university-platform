#!/usr/bin/env python3
"""
Direct test of individual endpoints to verify fixes
"""
import subprocess
import time
import sys
import requests

def start_server():
    """Start the server in background"""
    print("🚀 Starting server...")
    try:
        # Kill existing processes first
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, shell=True)
        time.sleep(2)
        
        # Start new server process
        cmd = [
            sys.executable, "-c", 
            "import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8002, reload=False, log_level='error')"
        ]
        
        process = subprocess.Popen(cmd, cwd=".", shell=True)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://127.0.0.1:8002/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return process
            except:
                pass
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Server failed to start")
        return None
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def test_endpoints():
    """Test the endpoints"""
    base_url = "http://127.0.0.1:8002"
    
    print("\\n🧪 Testing endpoints...")
    
    # Basic tests
    endpoints = [
        ("/health", "Health check"),
        ("/", "Root endpoint"),
        ("/departments", "Departments"),
        ("/specialties", "Specialties"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            print(f"   Testing {endpoint} ({description})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - OK")
                results.append(True)
            else:
                print(f"   ❌ {endpoint} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   💥 {endpoint} - Error: {e}")
            results.append(False)
    
    # Auth test
    print("\\n🔐 Testing authentication...")
    try:
        login_data = {"login": "admin.user", "password": "admin123"}
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("   ✅ Login - OK")
            token = response.json().get("access_token")
            results.append(True)
            
            # Test authenticated endpoints
            headers = {"Authorization": f"Bearer {token}"}
            auth_endpoints = [
                "/auth/me",
                "/auth/users",
                "/admin/students",
                "/admin/teachers", 
                "/admin/levels",
                "/admin/subjects",
                "/admin/dashboard/stats"
            ]
            
            print("\\n🔒 Testing authenticated endpoints...")
            for endpoint in auth_endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ {endpoint} - OK")
                        results.append(True)
                    else:
                        print(f"   ❌ {endpoint} - {response.status_code}")
                        results.append(False)
                except Exception as e:
                    print(f"   💥 {endpoint} - Error: {e}")
                    results.append(False)
        else:
            print(f"   ❌ Login failed - {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   💥 Auth error: {e}")
        results.append(False)
    
    return results

def main():
    print("🎯 Comprehensive API Fix Verification")
    print("=" * 50)
    
    # This script will test the fixes we made
    server_process = start_server()
    if not server_process:
        print("❌ Cannot start server. Exiting.")
        return
    
    try:
        # Run tests
        results = test_endpoints()
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\\n" + "=" * 50)
        print("🎯 RESULTS SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📊 Total: {total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\\n🎉 ALL TESTS PASSED! All fixes are working!")
        else:
            print(f"\\n⚠️  {total - passed} issues remain.")
            
    finally:
        # Clean up
        print("\\n🧹 Cleaning up...")
        try:
            server_process.terminate()
        except:
            pass
        
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, shell=True)

if __name__ == "__main__":
    main()