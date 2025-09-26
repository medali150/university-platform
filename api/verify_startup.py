#!/usr/bin/env python3
"""
Server Startup Verification Script
Checks for syntax errors and import issues before starting the server
"""

import sys
import importlib

def test_imports():
    """Test all module imports"""
    modules_to_test = [
        "app.routers.auth",
        "app.routers.departments", 
        "app.routers.specialties",
        "app.routers.admin",
        "app.routers.students_crud",
        "app.routers.teachers_crud", 
        "app.routers.department_heads_crud",
        "app.routers.admin_dashboard"
    ]
    
    print("🔍 Testing module imports...")
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} - OK")
        except Exception as e:
            print(f"❌ {module_name} - ERROR: {e}")
            return False
    
    return True

def test_main_app():
    """Test main application import"""
    try:
        from main import app
        print("✅ Main application - OK")
        return True
    except Exception as e:
        print(f"❌ Main application - ERROR: {e}")
        return False

def main():
    """Main verification function"""
    print("🎓 University API - Startup Verification")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please fix the errors above.")
        sys.exit(1)
    
    # Test main app
    if not test_main_app():
        print("\n❌ Main app test failed. Please fix the errors above.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Server is ready to start.")
    print("\n🚀 To start the server, run:")
    print("   uvicorn main:app --reload")
    print("\n📚 API Documentation will be available at:")
    print("   http://127.0.0.1:8000/docs")
    
    print("\n🔧 Admin CRUD Endpoints:")
    print("   • Student Management: /admin/students/")
    print("   • Teacher Management: /admin/teachers/")
    print("   • Department Head Management: /admin/department-heads/")
    print("   • Admin Dashboard: /admin/dashboard/")

if __name__ == "__main__":
    main()