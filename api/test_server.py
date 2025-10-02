#!/usr/bin/env python3
"""
Simple test server to debug the department head registration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

app = FastAPI(title="Test Registration Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock departments data
MOCK_DEPARTMENTS = [
    {"id": "dept1", "name": "Informatique"},
    {"id": "dept2", "name": "Mathématiques"},
]

# Mock user data (simplified)
class UserCreate:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

@app.get("/departments")
async def get_departments():
    """Mock departments endpoint"""
    print("📋 Departments requested")
    return MOCK_DEPARTMENTS

@app.post("/auth/register")
async def register(
    user_data: dict,
    department_id: Optional[str] = Query(None, description="Department ID for DEPARTMENT_HEAD role")
):
    """Mock registration endpoint with debugging"""
    print(f"\n🔍 Registration Request:")
    print(f"  Body: {user_data}")
    print(f"  Department ID (query): {department_id}")
    
    # Basic validation
    if not user_data.get("nom") or not user_data.get("prenom"):
        raise HTTPException(status_code=400, detail="Name fields required")
    
    if not user_data.get("email"):
        raise HTTPException(status_code=400, detail="Email required")
    
    if not user_data.get("password"):
        raise HTTPException(status_code=400, detail="Password required")
    
    if not user_data.get("role"):
        raise HTTPException(status_code=400, detail="Role required")
    
    # Department head specific validation
    if user_data.get("role") == "DEPARTMENT_HEAD":
        if not department_id:
            print("❌ Department head registration without department_id")
            raise HTTPException(status_code=400, detail="Department ID required for department heads")
        
        # Check if department exists
        dept_exists = any(d["id"] == department_id for d in MOCK_DEPARTMENTS)
        if not dept_exists:
            print(f"❌ Department not found: {department_id}")
            raise HTTPException(status_code=400, detail="Department not found")
        
        print(f"✅ Department head registration valid for dept: {department_id}")
    
    # Mock successful response
    result = {
        "id": "test-user-id",
        "nom": user_data["nom"],
        "prenom": user_data["prenom"],
        "email": user_data["email"],
        "role": user_data["role"],
        "createdAt": "2025-10-01T12:00:00Z"
    }
    
    print(f"✅ Registration successful: {result['prenom']} {result['nom']}")
    return result

@app.get("/")
async def root():
    return {"message": "Test Registration Server", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting test server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)